"""
gRPC HTTP代理模块

提供gRPC到HTTP的协议转换功能
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import grpc
from grpc import aio
from fastapi import Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import structlog

from .client import GrpcClient, GrpcClientPool, GrpcServiceConfig
from .transcoder import GrpcTranscoder

logger = structlog.get_logger(__name__)


@dataclass
class ProxyRule:
    """代理规则配置"""
    path_pattern: str
    service_name: str
    method_name: str
    request_type: str
    response_type: str
    streaming: bool = False
    timeout: float = 30.0
    metadata_mapping: Optional[Dict[str, str]] = None


class GrpcHttpProxy:
    """gRPC HTTP代理"""
    
    def __init__(self, client_pool: GrpcClientPool):
        self.client_pool = client_pool
        self.transcoder = GrpcTranscoder()
        self.rules: Dict[str, ProxyRule] = {}
        
    def add_rule(self, rule: ProxyRule) -> None:
        """添加代理规则"""
        self.rules[rule.path_pattern] = rule
        logger.info(
            "gRPC代理规则已添加",
            pattern=rule.path_pattern,
            service=rule.service_name,
            method=rule.method_name
        )
    
    def remove_rule(self, path_pattern: str) -> None:
        """移除代理规则"""
        if path_pattern in self.rules:
            del self.rules[path_pattern]
            logger.info(
                "gRPC代理规则已移除",
                pattern=path_pattern
            )
    
    async def proxy_request(
        self,
        request: Request,
        path: str
    ) -> Union[Response, StreamingResponse]:
        """代理HTTP请求到gRPC"""
        # 查找匹配的规则
        rule = self._find_matching_rule(path)
        if not rule:
            raise HTTPException(
                status_code=404,
                detail=f"未找到匹配的gRPC服务: {path}"
            )
        
        try:
            # 获取gRPC客户端
            client = self.client_pool.get_client(rule.service_name)
            
            # 转换HTTP请求为gRPC请求
            grpc_request = await self._convert_http_to_grpc(request, rule)
            
            # 构建metadata
            metadata = self._build_metadata(request, rule)
            
            if rule.streaming:
                # 处理流式响应
                return await self._handle_streaming_response(
                    client, rule, grpc_request, metadata
                )
            else:
                # 处理一元响应
                return await self._handle_unary_response(
                    client, rule, grpc_request, metadata
                )
                
        except grpc.RpcError as e:
            logger.error(
                "gRPC调用失败",
                path=path,
                service=rule.service_name,
                method=rule.method_name,
                code=e.code(),
                details=e.details()
            )
            
            # 转换gRPC错误为HTTP错误
            http_status = self._grpc_to_http_status(e.code())
            raise HTTPException(
                status_code=http_status,
                detail=e.details()
            )
            
        except Exception as e:
            logger.error(
                "代理请求失败",
                path=path,
                error=str(e)
            )
            raise HTTPException(
                status_code=500,
                detail="内部服务器错误"
            )
    
    def _find_matching_rule(self, path: str) -> Optional[ProxyRule]:
        """查找匹配的代理规则"""
        for pattern, rule in self.rules.items():
            if self._path_matches(path, pattern):
                return rule
        return None
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """检查路径是否匹配模式"""
        # 简单的路径匹配，支持通配符
        if pattern == path:
            return True
        
        # 支持 /api/v1/* 这样的通配符
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return path.startswith(prefix)
        
        # 支持路径参数 /api/v1/{id}
        pattern_parts = pattern.split('/')
        path_parts = path.split('/')
        
        if len(pattern_parts) != len(path_parts):
            return False
        
        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith('{') and pattern_part.endswith('}'):
                # 路径参数，跳过检查
                continue
            elif pattern_part != path_part:
                return False
        
        return True
    
    async def _convert_http_to_grpc(
        self,
        request: Request,
        rule: ProxyRule
    ) -> Any:
        """转换HTTP请求为gRPC请求"""
        # 获取请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
            if body:
                try:
                    json_data = json.loads(body)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail="无效的JSON格式"
                    )
            else:
                json_data = {}
        else:
            # GET请求从查询参数获取数据
            json_data = dict(request.query_params)
        
        # 添加路径参数
        if hasattr(request, 'path_params'):
            json_data.update(request.path_params)
        
        # 使用转码器转换数据
        return self.transcoder.json_to_protobuf(
            json_data,
            rule.request_type
        )
    
    def _build_metadata(
        self,
        request: Request,
        rule: ProxyRule
    ) -> List[tuple]:
        """构建gRPC metadata"""
        metadata = []
        
        # 添加标准头部
        if 'authorization' in request.headers:
            metadata.append(('authorization', request.headers['authorization']))
        
        if 'user-agent' in request.headers:
            metadata.append(('user-agent', request.headers['user-agent']))
        
        # 添加自定义映射
        if rule.metadata_mapping:
            for http_header, grpc_key in rule.metadata_mapping.items():
                if http_header in request.headers:
                    metadata.append((grpc_key, request.headers[http_header]))
        
        # 添加请求ID用于追踪
        if 'x-request-id' in request.headers:
            metadata.append(('x-request-id', request.headers['x-request-id']))
        
        return metadata
    
    async def _handle_unary_response(
        self,
        client: GrpcClient,
        rule: ProxyRule,
        grpc_request: Any,
        metadata: List[tuple]
    ) -> Response:
        """处理一元响应"""
        # 获取服务存根和方法
        stub_class = self._get_stub_class(rule.service_name)
        stub = client.get_stub(stub_class)
        method = getattr(stub, rule.method_name)
        
        # 调用gRPC方法
        grpc_response = await client.call_unary(
            method,
            grpc_request,
            timeout=rule.timeout,
            metadata=metadata
        )
        
        # 转换gRPC响应为HTTP响应
        json_response = self.transcoder.protobuf_to_json(
            grpc_response,
            rule.response_type
        )
        
        return Response(
            content=json.dumps(json_response, ensure_ascii=False),
            media_type="application/json"
        )
    
    async def _handle_streaming_response(
        self,
        client: GrpcClient,
        rule: ProxyRule,
        grpc_request: Any,
        metadata: List[tuple]
    ) -> StreamingResponse:
        """处理流式响应"""
        async def generate_stream():
            try:
                # 获取服务存根和方法
                stub_class = self._get_stub_class(rule.service_name)
                stub = client.get_stub(stub_class)
                method = getattr(stub, rule.method_name)
                
                # 调用流式方法
                async with client.call_streaming(
                    method,
                    grpc_request,
                    timeout=rule.timeout,
                    metadata=metadata
                ) as call:
                    async for response in call:
                        # 转换每个响应
                        json_response = self.transcoder.protobuf_to_json(
                            response,
                            rule.response_type
                        )
                        
                        # 以Server-Sent Events格式发送
                        yield f"data: {json.dumps(json_response, ensure_ascii=False)}\n\n"
                        
            except Exception as e:
                logger.error(
                    "流式响应处理失败",
                    service=rule.service_name,
                    method=rule.method_name,
                    error=str(e)
                )
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    def _get_stub_class(self, service_name: str) -> type:
        """获取服务存根类"""
        # 这里需要根据实际的服务定义来实现
        # 可以通过服务注册表或配置文件来获取
        # 暂时返回一个占位符
        class DummyStub:
            def __init__(self, channel):
                self.channel = channel
        
        return DummyStub
    
    def _grpc_to_http_status(self, grpc_code: grpc.StatusCode) -> int:
        """转换gRPC状态码为HTTP状态码"""
        mapping = {
            grpc.StatusCode.OK: 200,
            grpc.StatusCode.CANCELLED: 499,
            grpc.StatusCode.UNKNOWN: 500,
            grpc.StatusCode.INVALID_ARGUMENT: 400,
            grpc.StatusCode.DEADLINE_EXCEEDED: 504,
            grpc.StatusCode.NOT_FOUND: 404,
            grpc.StatusCode.ALREADY_EXISTS: 409,
            grpc.StatusCode.PERMISSION_DENIED: 403,
            grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
            grpc.StatusCode.FAILED_PRECONDITION: 400,
            grpc.StatusCode.ABORTED: 409,
            grpc.StatusCode.OUT_OF_RANGE: 400,
            grpc.StatusCode.UNIMPLEMENTED: 501,
            grpc.StatusCode.INTERNAL: 500,
            grpc.StatusCode.UNAVAILABLE: 503,
            grpc.StatusCode.DATA_LOSS: 500,
            grpc.StatusCode.UNAUTHENTICATED: 401,
        }
        
        return mapping.get(grpc_code, 500)
    
    def get_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取所有代理规则"""
        return {
            pattern: {
                "service_name": rule.service_name,
                "method_name": rule.method_name,
                "request_type": rule.request_type,
                "response_type": rule.response_type,
                "streaming": rule.streaming,
                "timeout": rule.timeout
            }
            for pattern, rule in self.rules.items()
        } 