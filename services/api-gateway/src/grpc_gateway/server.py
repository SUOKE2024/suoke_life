"""
gRPC服务器模块

提供gRPC服务的启动和管理功能
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor
import grpc
from grpc import aio
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
import structlog

logger = structlog.get_logger(__name__)


class GrpcGatewayServer:
    """gRPC网关服务器"""
    
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 50051,
        max_workers: int = 10,
        max_concurrent_rpcs: Optional[int] = None,
        options: Optional[List[tuple]] = None
    ):
        self.host = host
        self.port = port
        self.max_workers = max_workers
        self.max_concurrent_rpcs = max_concurrent_rpcs
        self.options = options or []
        
        self.server: Optional[aio.Server] = None
        self._services: Dict[str, Any] = {}
        self._interceptors: List[Any] = []
        self._health_servicer = health.HealthServicer()
        self._running = False
        
    def add_service(self, servicer: Any, add_servicer_func: Callable) -> None:
        """添加gRPC服务"""
        service_name = servicer.__class__.__name__
        self._services[service_name] = {
            "servicer": servicer,
            "add_func": add_servicer_func
        }
        
        logger.info(
            "gRPC服务已添加",
            service=service_name
        )
    
    def add_interceptor(self, interceptor: Any) -> None:
        """添加拦截器"""
        self._interceptors.append(interceptor)
        logger.info(
            "gRPC拦截器已添加",
            interceptor=interceptor.__class__.__name__
        )
    
    def set_service_health(self, service: str, status: health_pb2.HealthCheckResponse.ServingStatus) -> None:
        """设置服务健康状态"""
        self._health_servicer.set(service, status)
        logger.info(
            "gRPC服务健康状态已更新",
            service=service,
            status=status.name
        )
    
    async def start(self) -> None:
        """启动gRPC服务器"""
        if self._running:
            logger.warning("gRPC服务器已在运行")
            return
        
        try:
            # 创建服务器
            self.server = aio.server(
                interceptors=self._interceptors,
                options=self._get_server_options(),
                maximum_concurrent_rpcs=self.max_concurrent_rpcs
            )
            
            # 添加服务
            for service_name, service_info in self._services.items():
                service_info["add_func"](
                    service_info["servicer"],
                    self.server
                )
                
                # 设置服务为健康状态
                self.set_service_health(
                    service_name,
                    health_pb2.HealthCheckResponse.SERVING
                )
            
            # 添加健康检查服务
            health_pb2_grpc.add_HealthServicer_to_server(
                self._health_servicer,
                self.server
            )
            
            # 添加反射服务（用于调试）
            service_names = [
                desc.full_name
                for desc in self.server.get_service_descriptors()
            ]
            service_names.append(reflection.SERVICE_NAME)
            reflection.enable_server_reflection(service_names, self.server)
            
            # 绑定端口
            listen_addr = f"{self.host}:{self.port}"
            self.server.add_insecure_port(listen_addr)
            
            # 启动服务器
            await self.server.start()
            self._running = True
            
            logger.info(
                "gRPC服务器启动成功",
                host=self.host,
                port=self.port,
                services=list(self._services.keys())
            )
            
        except Exception as e:
            logger.error(
                "gRPC服务器启动失败",
                error=str(e)
            )
            raise
    
    async def stop(self, grace_period: float = 5.0) -> None:
        """停止gRPC服务器"""
        if not self._running or not self.server:
            return
        
        try:
            # 设置所有服务为不可用状态
            for service_name in self._services.keys():
                self.set_service_health(
                    service_name,
                    health_pb2.HealthCheckResponse.NOT_SERVING
                )
            
            # 优雅关闭服务器
            await self.server.stop(grace_period)
            self._running = False
            
            logger.info(
                "gRPC服务器已停止",
                grace_period=grace_period
            )
            
        except Exception as e:
            logger.error(
                "gRPC服务器停止失败",
                error=str(e)
            )
            raise
    
    async def wait_for_termination(self) -> None:
        """等待服务器终止"""
        if self.server and self._running:
            await self.server.wait_for_termination()
    
    def _get_server_options(self) -> List[tuple]:
        """获取服务器选项"""
        default_options = [
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000),
            ('grpc.max_receive_message_length', 4 * 1024 * 1024),  # 4MB
            ('grpc.max_send_message_length', 4 * 1024 * 1024),     # 4MB
        ]
        
        return default_options + self.options
    
    @property
    def is_running(self) -> bool:
        """检查服务器是否运行"""
        return self._running
    
    def get_stats(self) -> Dict[str, Any]:
        """获取服务器统计信息"""
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "services": list(self._services.keys()),
            "interceptors": [i.__class__.__name__ for i in self._interceptors],
            "max_workers": self.max_workers,
            "max_concurrent_rpcs": self.max_concurrent_rpcs
        }


class GrpcInterceptor:
    """gRPC拦截器基类"""
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """拦截一元-一元调用"""
        return await continuation(client_call_details, request)
    
    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """拦截一元-流调用"""
        return await continuation(client_call_details, request)
    
    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """拦截流-一元调用"""
        return await continuation(client_call_details, request_iterator)
    
    async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        """拦截流-流调用"""
        return await continuation(client_call_details, request_iterator)


class LoggingInterceptor(GrpcInterceptor):
    """日志拦截器"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """拦截一元-一元调用并记录日志"""
        method = client_call_details.method
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await continuation(client_call_details, request)
            duration = asyncio.get_event_loop().time() - start_time
            
            self.logger.info(
                "gRPC调用成功",
                method=method,
                duration=duration,
                request_size=len(str(request)),
                response_size=len(str(response))
            )
            
            return response
            
        except Exception as e:
            duration = asyncio.get_event_loop().time() - start_time
            
            self.logger.error(
                "gRPC调用失败",
                method=method,
                duration=duration,
                error=str(e)
            )
            raise


class AuthInterceptor(GrpcInterceptor):
    """认证拦截器"""
    
    def __init__(self, auth_func: Callable[[str], bool]):
        self.auth_func = auth_func
        self.logger = structlog.get_logger(__name__)
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """拦截一元-一元调用并进行认证"""
        # 从metadata中获取认证信息
        metadata = dict(client_call_details.metadata or [])
        auth_token = metadata.get('authorization', '')
        
        if not self.auth_func(auth_token):
            self.logger.warning(
                "gRPC认证失败",
                method=client_call_details.method,
                token=auth_token[:20] + "..." if len(auth_token) > 20 else auth_token
            )
            raise grpc.RpcError(grpc.StatusCode.UNAUTHENTICATED, "认证失败")
        
        return await continuation(client_call_details, request)


class RateLimitInterceptor(GrpcInterceptor):
    """限流拦截器"""
    
    def __init__(self, max_requests_per_minute: int = 60):
        self.max_requests = max_requests_per_minute
        self.requests = {}
        self.logger = structlog.get_logger(__name__)
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """拦截一元-一元调用并进行限流"""
        # 从metadata中获取客户端标识
        metadata = dict(client_call_details.metadata or [])
        client_id = metadata.get('client-id', 'unknown')
        
        current_time = asyncio.get_event_loop().time()
        minute_key = int(current_time // 60)
        
        # 清理过期记录
        self.requests = {
            k: v for k, v in self.requests.items()
            if k >= minute_key - 1
        }
        
        # 检查限流
        key = f"{client_id}:{minute_key}"
        current_requests = self.requests.get(key, 0)
        
        if current_requests >= self.max_requests:
            self.logger.warning(
                "gRPC请求被限流",
                client_id=client_id,
                method=client_call_details.method,
                current_requests=current_requests,
                max_requests=self.max_requests
            )
            raise grpc.RpcError(grpc.StatusCode.RESOURCE_EXHAUSTED, "请求频率过高")
        
        # 增加请求计数
        self.requests[key] = current_requests + 1
        
        return await continuation(client_call_details, request) 