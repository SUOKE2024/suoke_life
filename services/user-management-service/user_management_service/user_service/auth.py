"""
auth - 索克生活项目模块
"""

from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional

import httpx
import jwt
import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from user_service.config import get_settings

"""用户服务认证模块"""



logger = structlog.get_logger()
security = HTTPBearer()


class AuthService:
    """认证服务客户端"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.settings = get_settings()
        self.auth_service_url = self.settings.auth.auth_service_url
        self.jwt_secret = self.settings.auth.jwt_secret_key
        self.jwt_algorithm = self.settings.auth.jwt_algorithm
        self._token_cache = {}  # 简单的令牌缓存

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证JWT令牌"""
        try:
            # 首先尝试本地验证
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms = [self.jwt_algorithm]
            )

            # 检查令牌是否过期
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired", token = token[:20] + "...")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token", error = str(e), token = token[:20] + "...")
            return None
        except Exception as e:
            logger.error("Token verification failed", error = str(e))
            return None

    async def verify_token_with_auth_service(self, token: str) -> Optional[Dict[str, Any]]:
        """通过认证服务验证令牌"""
        try:
            # 检查缓存
            cache_key = f"token:{token[:20]}"
            if cache_key in self._token_cache:
                cached_data, cached_time = self._token_cache[cache_key]
                if datetime.utcnow() - cached_time < timedelta(minutes = 5):
                    return cached_data

            # 调用认证服务验证
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_service_url} / users / me",
                    headers = {"Authorization": f"Bearer {token}"},
                    timeout = 10.0
                )

                if response.status_code==200:
                    user_data = response.json()
                    # 缓存结果
                    self._token_cache[cache_key] = (user_data, datetime.utcnow())
                    return user_data
                else:
                    logger.warning(
                        "Token verification failed",
                        status_code = response.status_code,
                        response = response.text
                    )
                    return None

        except httpx.TimeoutException:
            logger.error("Auth service timeout")
            return None
        except Exception as e:
            logger.error("Failed to verify token with auth service", error = str(e))
            return None

    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        # 首先尝试本地验证
        payload = await self.verify_token(token)
        if payload:
            return {
                "id": payload.get("sub"),
                "username": payload.get("username"),
                "email": payload.get("email"),
                "is_superuser": payload.get("is_superuser", False),
                "is_verified": payload.get("is_verified", False)
            }

        # 如果本地验证失败，尝试通过认证服务验证
        return await self.verify_token_with_auth_service(token)

    def clear_token_cache(self, token: str = None):
        """清理令牌缓存"""
        if token:
            cache_key = f"token:{token[:20]}"
            self._token_cache.pop(cache_key, None)
        else:
            self._token_cache.clear()


# 全局认证服务实例
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    global _auth_service
    if not _auth_service:
        _auth_service = AuthService()
    return _auth_service


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """获取当前用户（依赖注入）"""
    auth_service = get_auth_service()
    user = await auth_service.get_current_user(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "无效的访问令牌",
            headers = {"WWW - Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取当前活跃用户"""
    if not current_user.get("is_verified"):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "用户账户未验证"
        )

    return current_user


async def get_current_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取当前超级用户"""
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "权限不足"
        )

    return current_user


def require_auth(func):
    """认证装饰器"""
    @wraps(func)
    async def wrapper( * args,**kwargs):
        # 从kwargs中获取request对象
        request = kwargs.get('request') or (args[0] if args and hasattr(args[0], 'headers') else None)

        if not request:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "无法获取请求对象"
            )

        # 获取Authorization头
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "缺少认证令牌",
                headers = {"WWW - Authenticate": "Bearer"},
            )

        token = auth_header.split(" ")[1]
        auth_service = get_auth_service()
        user = await auth_service.get_current_user(token)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "无效的访问令牌",
                headers = {"WWW - Authenticate": "Bearer"},
            )

        # 将用户信息添加到kwargs
        kwargs['current_user'] = user

        return await func( * args,**kwargs)

    return wrapper


def require_superuser(func):
    """超级用户权限装饰器"""
    @wraps(func)
    async def wrapper( * args,**kwargs):
        # 首先进行认证
        await require_auth(func)( * args,**kwargs)

        current_user = kwargs.get('current_user')
        if not current_user or not current_user.get("is_superuser"):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "权限不足"
            )

        return await func( * args,**kwargs)

    return wrapper


class AuthMiddleware:
    """认证中间件"""

    def __init__(self, app):
        """TODO: 添加文档字符串"""
        self.app = app
        self.auth_service = get_auth_service()

    async def __call__(self, scope, receive, send):
        if scope["type"]=="http":
            request = Request(scope, receive)

            # 跳过健康检查和文档路径
            path = request.url.path
            if path in [" / health", " / docs", " / redoc", " / openapi.json"]:
                await self.app(scope, receive, send)
                return

            # 检查认证
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user = await self.auth_service.get_current_user(token)
                if user:
                    # 将用户信息添加到scope
                    scope["user"] = user

        await self.app(scope, receive, send)


def get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """从请求中获取用户信息"""
    return getattr(request.scope, "user", None)