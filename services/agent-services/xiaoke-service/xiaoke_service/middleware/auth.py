"""认证中间件

处理用户认证和授权，支持JWT Token和API Key两种认证方式。
"""

from collections.abc import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from xiaoke_service.core.logging import get_logger
from xiaoke_service.core.exceptions import AuthenticationError
import time
import jwt
from typing import Optional

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件
    
    支持JWT Token和API Key两种认证方式，
    为不同的路径提供灵活的认证策略。
    """

    def __init__(self, app, skip_paths: Optional[list[str]] = None):
        """初始化认证中间件
        
        Args:
            app: FastAPI应用实例
            skip_paths: 跳过认证的路径列表
        """
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/ready", 
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    def _verify_jwt_token(self, token: str) -> Optional[dict]:
        """验证JWT Token
        
        Args:
            token: JWT token字符串
            
        Returns:
            解析后的用户信息，验证失败返回None
        """
        try:
            # 这里应该使用实际的JWT密钥和算法
            # 暂时使用简单验证
            if len(token) > 10:  # 基础长度检查
                return {
                    "user_id": f"jwt_user_{token[:8]}",
                    "auth_type": "jwt"
                }
            return None
        except Exception as e:
            logger.warning("JWT验证失败", token_prefix=token[:8], error=str(e))
            return None

    def _verify_api_key(self, api_key: str) -> Optional[dict]:
        """验证API Key
        
        Args:
            api_key: API密钥字符串
            
        Returns:
            解析后的用户信息，验证失败返回None
        """
        try:
            # 这里应该查询数据库验证API Key
            # 暂时使用简单验证
            if len(api_key) >= 16:  # 基础长度检查
                return {
                    "user_id": f"api_user_{api_key[:8]}",
                    "auth_type": "api_key"
                }
            return None
        except Exception as e:
            logger.warning("API Key验证失败", key_prefix=api_key[:8], error=str(e))
            return None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求认证
        
        Args:
            request: HTTP请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            HTTP响应对象
        """
        start_time = time.time()

        # 跳过不需要认证的路径
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            response = await call_next(request)
            return response

        # 获取认证信息
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")

        # 初始化用户状态
        request.state.user_id = "anonymous"
        request.state.authenticated = False
        request.state.auth_type = None
        request.state.user_info = None

        # JWT Token认证
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            user_info = self._verify_jwt_token(token)
            if user_info:
                request.state.authenticated = True
                request.state.user_id = user_info["user_id"]
                request.state.auth_type = user_info["auth_type"]
                request.state.user_info = user_info

        # API Key认证
        elif api_key:
            user_info = self._verify_api_key(api_key)
            if user_info:
                request.state.authenticated = True
                request.state.user_id = user_info["user_id"]
                request.state.auth_type = user_info["auth_type"]
                request.state.user_info = user_info

        try:
            response = await call_next(request)

            # 记录认证信息
            duration = time.time() - start_time
            logger.info(
                "认证处理完成",
                path=request.url.path,
                method=request.method,
                user_id=request.state.user_id,
                authenticated=request.state.authenticated,
                auth_type=request.state.auth_type,
                duration_ms=round(duration * 1000, 2),
            )

            # 添加认证信息到响应头
            response.headers["X-Auth-Status"] = "authenticated" if request.state.authenticated else "anonymous"
            if request.state.auth_type:
                response.headers["X-Auth-Type"] = request.state.auth_type

            return response

        except Exception as e:
            logger.error(
                "认证处理错误",
                path=request.url.path,
                method=request.method,
                error=str(e),
            )
            raise