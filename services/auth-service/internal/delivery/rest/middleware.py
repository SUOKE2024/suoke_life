#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
REST API安全中间件

实现API安全保护功能，包括：
1. 速率限制
2. 安全头设置
3. CORS配置
4. 请求ID追踪
5. IP审计
"""
import time
import uuid
from typing import Callable, Dict, List, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from secure import SecureHeaders
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

# 安全头配置
secure_headers = SecureHeaders(
    server=False,
    hsts=True,
    xfo="DENY",
    csp={
        "default-src": "'self'",
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'"],
        "connect-src": ["'self'"]
    },
    feature={"geolocation": "'none'"}
)

# 速率限制器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute", "10/second"]
)


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """请求追踪中间件
    
    为每个请求添加唯一ID，用于跟踪和日志
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算请求处理时间
        process_time = time.time() - start_time
        
        # 添加跟踪头
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """安全审计中间件
    
    记录敏感操作的IP和用户代理信息
    """
    
    def __init__(self, app: FastAPI, sensitive_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.sensitive_paths = sensitive_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/reset-password",
            "/api/v1/roles",
            "/api/v1/permissions"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        
        # 对敏感路径进行审计
        if any(path.startswith(sensitive_path) for sensitive_path in self.sensitive_paths):
            # 记录客户端信息
            client_info = {
                "ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "path": path,
                "method": request.method,
                "request_id": getattr(request.state, "request_id", "unknown")
            }
            
            # 这里应该记录到审计日志系统
            # 在实际系统中，我们会使用更高级的日志系统
            print(f"Security audit: {client_info}")
        
        response = await call_next(request)
        return response


def setup_middleware(app: FastAPI) -> None:
    """配置API中间件
    
    为FastAPI应用程序添加所有必要的中间件
    """
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制为特定域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"]
    )
    
    # 添加速率限制中间件
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    
    # 添加请求跟踪中间件
    app.add_middleware(RequestTracingMiddleware)
    
    # 添加安全审计中间件
    app.add_middleware(SecurityAuditMiddleware)
    
    # 添加安全头响应中间件
    @app.middleware("http")
    async def set_secure_headers(request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        secure_headers.framework.fastapi(response)
        return response 