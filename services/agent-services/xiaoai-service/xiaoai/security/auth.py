"""
认证和授权模块

提供JWT认证、权限控制等功能
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from ..config.settings import get_settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.jwt_secret
        self.algorithm = "HS256"
        self.expire_hours = self.settings.jwt_expire_hours
    
    def create_access_token(self, user_id: str, permissions: list = None) -> str:
        """创建访问令牌"""
        try:
            expire = datetime.utcnow() + timedelta(hours=self.expire_hours)
            payload = {
                "user_id": user_id,
                "permissions": permissions or [],
                "exp": expire,
                "iat": datetime.utcnow(),
                "type": "access"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"创建访问令牌成功: user_id={user_id}")
            return token
            
        except Exception as e:
            logger.error(f"创建访问令牌失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="令牌创建失败"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # 检查令牌类型
            if payload.get("type")!="access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的令牌类型"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效令牌: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效令牌"
            )
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            salt, password_hash = hashed.split(':')
            computed_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            return computed_hash.hex()==password_hash
        except Exception:
            return False


# 全局认证管理器实例
auth_manager = AuthManager()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """获取当前用户"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    return payload


def require_permission(permission: str):
    """权限装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args,**kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证"
                )
            
            permissions = current_user.get('permissions', [])
            if permission not in permissions and 'admin' not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args,**kwargs)
        return wrapper
    return decorator


class RateLimiter:
    """限流器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # 清理过期记录
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
        else:
            self.requests[key] = []
        
        # 检查限流
        if len(self.requests[key])>=self.max_requests:
            return False
        
        # 记录请求
        self.requests[key].append(now)
        return True


# 全局限流器
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """限流装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args,**kwargs):
            client_ip = request.client.host
            
            if not rate_limiter.is_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁"
                )
            
            return await func(request, *args,**kwargs)
        return wrapper
    return decorator