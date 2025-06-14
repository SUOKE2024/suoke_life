"""
中间件模块
提供认证、限流、监控、错误处理等中间件功能
"""
import time
import json
from typing import Callable, Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.container import get_container


class MetricsMiddleware(BaseHTTPMiddleware):
    """监控指标中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 获取监控服务
        try:
            container = get_container()
            metrics_service = container.metrics_service
        except Exception:
            metrics_service = None
        
        # 处理请求
        response = await call_next(request)
        
        # 记录指标
        if metrics_service:
            duration = time.time() - start_time
            metrics_service.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(time.time() - start_time)
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 记录请求信息
        self.logger.info(
            "请求开始",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        duration = time.time() - start_time
        self.logger.info(
            "请求完成",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # HTTP异常直接返回
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "code": e.status_code,
                        "message": e.detail,
                        "type": "http_error"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            )
        except Exception as e:
            # 记录未处理的异常
            self.logger.error(
                "未处理的异常",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "method": request.method,
                    "url": str(request.url),
                    "timestamp": datetime.utcnow().isoformat()
                },
                exc_info=True
            )
            
            # 返回通用错误响应
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": 500,
                        "message": "内部服务器错误",
                        "type": "internal_error"
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": request.url.path
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.settings = get_settings()
        self.logger = get_logger()
        
        # 不需要认证的路径
        self.public_paths = {
            "/",
            "/health",
            "/metrics",
            "/api/docs",
            "/openapi.json",
            "/api/v1/health"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否为公开路径
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # 检查是否启用了安全配置
        if not self.settings.security:
            return await call_next(request)
        
        # 获取认证头
        authorization = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": 401,
                        "message": "缺少认证头",
                        "type": "authentication_error"
                    }
                }
            )
        
        # 解析认证类型
        try:
            auth_type, token = authorization.split(" ", 1)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": 401,
                        "message": "认证头格式错误",
                        "type": "authentication_error"
                    }
                }
            )
        
        # JWT认证
        if auth_type.lower() == "bearer":
            user_info = await self._verify_jwt_token(token)
            if not user_info:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": 401,
                            "message": "无效的JWT令牌",
                            "type": "authentication_error"
                        }
                    }
                )
            request.state.user = user_info
        
        # API Key认证
        elif auth_type.lower() == "apikey":
            api_key_info = await self._verify_api_key(token)
            if not api_key_info:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": 401,
                            "message": "无效的API密钥",
                            "type": "authentication_error"
                        }
                    }
                )
            request.state.api_key = api_key_info
        
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "code": 401,
                        "message": "不支持的认证类型",
                        "type": "authentication_error"
                    }
                }
            )
        
        return await call_next(request)
    
    async def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(
                token,
                self.settings.security.jwt.secret,
                algorithms=["HS256"]
            )
            
            # 检查过期时间
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return None
            
            return payload
            
        except JWTError as e:
            self.logger.warning(f"JWT验证失败: {e}")
            return None
    
    async def _verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """验证API密钥"""
        if not self.settings.security.api_keys:
            return None
        
        for key_config in self.settings.security.api_keys:
            if key_config.key == api_key:
                return {
                    "name": key_config.name,
                    "roles": key_config.roles
                }
        
        return None


# 限流器配置
limiter = Limiter(key_func=get_remote_address)


def create_rate_limit_handler():
    """创建限流异常处理器"""
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        response = JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": 429,
                    "message": f"请求过于频繁: {exc.detail}",
                    "type": "rate_limit_error"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "path": request.url.path
            }
        )
        response = request.app.state.limiter._inject_headers(response, request.state.view_rate_limit)
        return response
    
    return rate_limit_handler


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """获取当前用户信息"""
    return getattr(request.state, "user", None)


def get_current_api_key(request: Request) -> Optional[Dict[str, Any]]:
    """获取当前API密钥信息"""
    return getattr(request.state, "api_key", None)


def require_roles(required_roles: list):
    """角色权限装饰器"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            api_key = get_current_api_key(request)
            
            user_roles = []
            if user:
                user_roles = user.get("roles", [])
            elif api_key:
                user_roles = api_key.get("roles", [])
            
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator 