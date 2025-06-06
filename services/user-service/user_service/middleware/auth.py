"""
auth - 索克生活项目模块
"""

from fastapi import Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from user_service.config import get_settings
from user_service.core.exceptions import AuthenticationError
import jwt
import logging

"""认证中间件"""



logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        # 不需要认证的路径
        self.public_paths = {
            "/health",
            "/metrics", 
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
            "/api/v1/info"
        }
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        
        # 检查是否为公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # 提取并验证JWT令牌
        try:
            user_info = await self._authenticate_request(request)
            if user_info:
                # 将用户信息添加到请求状态
                request.state.user = user_info
                request.state.user_id = user_info.get("user_id")
                request.state.authenticated = True
            else:
                request.state.user = None
                request.state.user_id = None
                request.state.authenticated = False
                
        except AuthenticationError as e:
            logger.warning(f"认证失败: {e}")
            request.state.user = None
            request.state.user_id = None
            request.state.authenticated = False
        
        response = await call_next(request)
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """检查是否为公开路径"""
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    async def _authenticate_request(self, request: Request) -> Optional[dict]:
        """认证请求"""
        
        # 从Authorization头获取令牌
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None
        
        if not authorization.startswith("Bearer "):
            raise AuthenticationError("无效的认证头格式")
        
        token = authorization[7:]  # 移除 "Bearer " 前缀
        
        try:
            # 验证JWT令牌
            payload = jwt.decode(
                token,
                self.settings.jwt.secret_key,
                algorithms=[self.settings.jwt.algorithm],
                audience=self.settings.jwt.audience,
                issuer=self.settings.jwt.issuer
            )
            
            # 提取用户信息
            user_info = {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "permissions": payload.get("permissions", []),
                "exp": payload.get("exp"),
                "iat": payload.get("iat")
            }
            
            return user_info
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("令牌已过期")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"无效的令牌: {str(e)}")
        except Exception as e:
            logger.error(f"令牌验证时发生错误: {e}")
            raise AuthenticationError("令牌验证失败") 