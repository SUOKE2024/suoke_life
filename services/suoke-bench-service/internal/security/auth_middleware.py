"""
auth_middleware - 索克生活项目模块
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, List, Optional, Callable
import hashlib
import hmac
import jwt
import time

"""安全认证中间件

提供API认证、授权、限流等安全功能
"""



class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # 清理过期请求
        while client_requests and client_requests[0] < now - self.time_window:
            client_requests.popleft()
        
        # 检查是否超过限制
        if len(client_requests) >= self.max_requests:
            return False
        
        # 记录当前请求
        client_requests.append(now)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """获取剩余请求数"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # 清理过期请求
        while client_requests and client_requests[0] < now - self.time_window:
            client_requests.popleft()
        
        return max(0, self.max_requests - len(client_requests))


class APIKeyAuth:
    """API密钥认证"""
    
    def __init__(self, valid_keys: Dict[str, Dict[str, any]]):
        """
        初始化API密钥认证
        
        Args:
            valid_keys: 有效的API密钥配置
                格式: {
                    "key": {
                        "name": "客户端名称",
                        "permissions": ["read", "write"],
                        "rate_limit": {"max_requests": 1000, "time_window": 3600}
                    }
                }
        """
        self.valid_keys = valid_keys
        self.rate_limiters = {}
        
        # 为每个API密钥创建速率限制器
        for key, config in valid_keys.items():
            rate_config = config.get("rate_limit", {"max_requests": 100, "time_window": 60})
            self.rate_limiters[key] = RateLimiter(
                max_requests=rate_config["max_requests"],
                time_window=rate_config["time_window"]
            )
    
    def authenticate(self, api_key: str) -> Optional[Dict[str, any]]:
        """认证API密钥"""
        if api_key not in self.valid_keys:
            return None
        
        # 检查速率限制
        if not self.rate_limiters[api_key].is_allowed(api_key):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
        
        return self.valid_keys[api_key]


class JWTAuth:
    """JWT认证"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, payload: Dict[str, any], expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT令牌"""
        to_encode = payload.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, any]]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""
    
    def __init__(
        self,
        app,
        api_key_auth: Optional[APIKeyAuth] = None,
        jwt_auth: Optional[JWTAuth] = None,
        public_paths: List[str] = None,
        require_https: bool = False
    ):
        super().__init__(app)
        self.api_key_auth = api_key_auth
        self.jwt_auth = jwt_auth
        self.public_paths = public_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        self.require_https = require_https
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        
        # 检查HTTPS要求
        if self.require_https and request.url.scheme != "https":
            raise HTTPException(
                status_code=400,
                detail="HTTPS required"
            )
        
        # 检查是否为公开路径
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # 认证检查
        auth_result = await self._authenticate(request)
        if auth_result:
            # 将认证信息添加到请求状态
            request.state.auth = auth_result
        
        # 添加安全头
        response = await call_next(request)
        self._add_security_headers(response)
        
        return response
    
    async def _authenticate(self, request: Request) -> Optional[Dict[str, any]]:
        """认证请求"""
        
        # 尝试API密钥认证
        api_key = request.headers.get("X-API-Key")
        if api_key and self.api_key_auth:
            try:
                return self.api_key_auth.authenticate(api_key)
            except HTTPException:
                raise
        
        # 尝试JWT认证
        authorization = request.headers.get("Authorization")
        if authorization and self.jwt_auth:
            try:
                scheme, token = authorization.split()
                if scheme.lower() == "bearer":
                    return self.jwt_auth.verify_token(token)
            except ValueError:
                pass
            except HTTPException:
                raise
        
        # 如果没有认证信息，返回401
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    def _add_security_headers(self, response: Response):
        """添加安全头"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"


class PermissionChecker:
    """权限检查器"""
    
    def __init__(self):
        self.permissions = {
            "benchmark:read": "读取基准测试",
            "benchmark:write": "创建基准测试",
            "benchmark:delete": "删除基准测试",
            "model:read": "读取模型信息",
            "model:write": "注册模型",
            "model:delete": "删除模型",
            "admin": "管理员权限"
        }
    
    def check_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """检查权限"""
        if "admin" in user_permissions:
            return True
        
        return required_permission in user_permissions
    
    def require_permission(self, permission: str):
        """权限装饰器"""
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                auth = getattr(request.state, "auth", None)
                if not auth:
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required"
                    )
                
                user_permissions = auth.get("permissions", [])
                if not self.check_permission(user_permissions, permission):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Permission '{permission}' required"
                    )
                
                return await func(request, *args, **kwargs)
            return wrapper
        return decorator


def create_security_config() -> Dict[str, any]:
    """创建默认安全配置"""
    return {
        "api_keys": {
            "demo-key-123": {
                "name": "Demo Client",
                "permissions": ["benchmark:read", "model:read"],
                "rate_limit": {"max_requests": 100, "time_window": 60}
            },
            "admin-key-456": {
                "name": "Admin Client",
                "permissions": ["admin"],
                "rate_limit": {"max_requests": 1000, "time_window": 60}
            }
        },
        "jwt_secret": "your-secret-key-here",
        "require_https": False,
        "public_paths": ["/health", "/metrics", "/docs", "/openapi.json"]
    }


def setup_security(app, config: Dict[str, any]):
    """设置安全中间件"""
    
    # 创建API密钥认证
    api_key_auth = APIKeyAuth(config.get("api_keys", {}))
    
    # 创建JWT认证
    jwt_auth = JWTAuth(config.get("jwt_secret", "default-secret"))
    
    # 添加安全中间件
    app.add_middleware(
        SecurityMiddleware,
        api_key_auth=api_key_auth,
        jwt_auth=jwt_auth,
        public_paths=config.get("public_paths", []),
        require_https=config.get("require_https", False)
    )
    
    return {
        "api_key_auth": api_key_auth,
        "jwt_auth": jwt_auth,
        "permission_checker": PermissionChecker()
    } 