#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版API网关
集成认证、限流、追踪、监控等功能
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入通用组件
from services.common.governance.circuit_breaker import CircuitBreakerOpenError
from services.common.governance.rate_limiter import RateLimitExceededError
from services.common.observability.tracing import get_tracer, SpanKind

# 导入服务
from services.agent_services.xiaoai_service.internal.service.enhanced_diagnosis_service import (
    get_diagnosis_service, DiagnosisRequest, DiagnosisResult
)

logger = logging.getLogger(__name__)

@dataclass
class APIResponse:
    """API响应格式"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class EnhancedAPIGateway:
    """增强版API网关"""
    
    def __init__(self):
        self.app = FastAPI(
            title="小艾智能诊断服务",
            description="基于AI的智能诊断服务API",
            version="2.0.0"
        )
        
        self.tracer = get_tracer("xiaoai-api-gateway")
        
        # 配置中间件
        self._setup_middleware()
        
        # 配置路由
        self._setup_routes()
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'start_time': time.time()
        }
        
        logger.info("增强版API网关初始化完成")
    
    def _setup_middleware(self):
        """配置中间件"""
        # CORS中间件
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境应该限制具体域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 可信主机中间件
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # 生产环境应该限制具体主机
        )
        
        # 自定义中间件
        @self.app.middleware("http")
        async def request_middleware(request: Request, call_next):
            """请求中间件"""
            start_time = time.time()
            
            # 开始追踪
            async with self.tracer.trace(
                f"{request.method} {request.url.path}",
                kind=SpanKind.SERVER,
                tags={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.user_agent": request.headers.get("user-agent", ""),
                    "http.remote_addr": request.client.host if request.client else ""
                }
            ) as span:
                
                try:
                    # 更新统计
                    self.stats['total_requests'] += 1
                    
                    # 调用下一个处理器
                    response = await call_next(request)
                    
                    # 记录响应信息
                    processing_time = time.time() - start_time
                    span.set_tag("http.status_code", response.status_code)
                    span.set_tag("response.time", processing_time)
                    
                    # 更新统计
                    if response.status_code < 400:
                        self.stats['successful_requests'] += 1
                    else:
                        self.stats['failed_requests'] += 1
                    
                    self._update_average_response_time(processing_time)
                    
                    # 添加追踪ID到响应头
                    response.headers["X-Trace-ID"] = span.context.trace_id
                    
                    return response
                    
                except Exception as e:
                    # 记录异常
                    span.set_tag("error", True)
                    span.log(f"请求处理异常: {e}", level="error")
                    
                    self.stats['failed_requests'] += 1
                    
                    # 返回错误响应
                    return JSONResponse(
                        status_code=500,
                        content=APIResponse(
                            success=False,
                            error=f"内部服务器错误: {str(e)}",
                            trace_id=span.context.trace_id
                        ).__dict__
                    )
    
    def _setup_routes(self):
        """配置路由"""
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            diagnosis_service = await get_diagnosis_service()
            service_health = diagnosis_service.get_health_status()
            
            return APIResponse(
                success=True,
                data={
                    'gateway': {
                        'status': 'healthy',
                        'uptime': time.time() - self.stats['start_time'],
                        'stats': self.stats
                    },
                    'diagnosis_service': service_health
                }
            ).__dict__
        
        @self.app.get("/metrics")
        async def get_metrics():
            """获取指标"""
            diagnosis_service = await get_diagnosis_service()
            
            return APIResponse(
                success=True,
                data={
                    'gateway_stats': self.stats,
                    'diagnosis_stats': diagnosis_service.stats,
                    'timestamp': time.time()
                }
            ).__dict__
        
        @self.app.post("/api/v1/diagnosis")
        async def create_diagnosis(request: Request):
            """创建诊断"""
            try:
                # 解析请求体
                body = await request.json()
                
                # 验证请求
                diagnosis_request = self._validate_diagnosis_request(body)
                
                # 获取诊断服务
                diagnosis_service = await get_diagnosis_service()
                
                # 执行诊断
                result = await diagnosis_service.diagnose(diagnosis_request)
                
                return APIResponse(
                    success=True,
                    data=result.__dict__
                ).__dict__
                
            except RateLimitExceededError as e:
                raise HTTPException(status_code=429, detail=str(e))
            except CircuitBreakerOpenError as e:
                raise HTTPException(status_code=503, detail=str(e))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"诊断请求处理失败: {e}")
                raise HTTPException(status_code=500, detail="内部服务器错误")
        
        @self.app.get("/api/v1/diagnosis/{diagnosis_id}")
        async def get_diagnosis(diagnosis_id: str):
            """获取诊断结果"""
            # 这里应该从数据库或缓存中获取诊断结果
            # 暂时返回示例数据
            return APIResponse(
                success=True,
                data={
                    'diagnosis_id': diagnosis_id,
                    'status': 'completed',
                    'message': '诊断结果查询功能待实现'
                }
            ).__dict__
        
        @self.app.get("/api/v1/user/{user_id}/diagnoses")
        async def get_user_diagnoses(user_id: str, limit: int = 10, offset: int = 0):
            """获取用户诊断历史"""
            # 这里应该从数据库中获取用户的诊断历史
            # 暂时返回示例数据
            return APIResponse(
                success=True,
                data={
                    'user_id': user_id,
                    'diagnoses': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset,
                    'message': '用户诊断历史查询功能待实现'
                }
            ).__dict__
        
        # 异常处理器
        @self.app.exception_handler(HTTPException)
        async def http_exception_handler(request: Request, exc: HTTPException):
            """HTTP异常处理器"""
            return JSONResponse(
                status_code=exc.status_code,
                content=APIResponse(
                    success=False,
                    error=exc.detail
                ).__dict__
            )
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """通用异常处理器"""
            logger.error(f"未处理的异常: {exc}")
            return JSONResponse(
                status_code=500,
                content=APIResponse(
                    success=False,
                    error="内部服务器错误"
                ).__dict__
            )
    
    def _validate_diagnosis_request(self, body: Dict[str, Any]) -> DiagnosisRequest:
        """验证诊断请求"""
        # 必需字段验证
        if 'user_id' not in body:
            raise ValueError("缺少必需字段: user_id")
        
        if 'symptoms' not in body or not body['symptoms']:
            raise ValueError("缺少必需字段: symptoms")
        
        # 创建诊断请求对象
        return DiagnosisRequest(
            user_id=body['user_id'],
            symptoms=body['symptoms'],
            medical_history=body.get('medical_history'),
            vital_signs=body.get('vital_signs'),
            images=body.get('images'),
            priority=body.get('priority', 'normal')
        )
    
    def _update_average_response_time(self, response_time: float):
        """更新平均响应时间"""
        total_requests = self.stats['total_requests']
        if total_requests == 1:
            self.stats['average_response_time'] = response_time
        else:
            current_avg = self.stats['average_response_time']
            self.stats['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """启动API网关"""
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        logger.info(f"启动API网关: http://{host}:{port}")
        await server.serve()

# 创建全局网关实例
gateway = EnhancedAPIGateway()

# 导出FastAPI应用
app = gateway.app

if __name__ == "__main__":
    # 直接运行
    asyncio.run(gateway.start()) 