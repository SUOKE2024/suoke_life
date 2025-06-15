"""
安全中间件 - 提供安全防护功能
"""

import hashlib
import logging
import secrets
import time
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """安全中间件"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rate_limiter = RateLimiter(config.get("rate_limiting", {}))
        self.session_manager = SessionManager(config.get("authentication", {}))

    async def process_request(self, request):
        """处理请求"""
        # 速率限制
        if not self.rate_limiter.allow_request(request.client.host):
            raise HTTPException(status_code=429, detail="Too Many Requests")

        # 安全头检查
        self._add_security_headers(request)

        # 会话验证
        if not self.session_manager.validate_session(request):
            raise HTTPException(status_code=401, detail="Unauthorized")

        return request

    def _add_security_headers(self, request):
        """添加安全头"""
        headers = self.config.get("headers", {})
        for header, value in headers.items():
            request.headers[header] = value


class RateLimiter:
    """速率限制器"""

    def __init__(self, config: Dict[str, Any]):
        self.requests_per_minute = config.get("requests_per_minute", 60)
        self.burst_size = config.get("burst_size", 10)
        self.requests = {}

    def allow_request(self, client_ip: str) -> bool:
        """检查是否允许请求"""
        now = time.time()
        minute = int(now // 60)

        if client_ip not in self.requests:
            self.requests[client_ip] = {}

        client_requests = self.requests[client_ip]

        # 清理过期记录
        for old_minute in list(client_requests.keys()):
            if old_minute < minute - 1:
                del client_requests[old_minute]

        # 检查当前分钟的请求数
        current_requests = client_requests.get(minute, 0)

        if current_requests >= self.requests_per_minute:
            return False

        # 记录请求
        client_requests[minute] = current_requests + 1
        return True


class SessionManager:
    """会话管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.session_timeout = config.get("session_timeout", 3600)
        self.max_login_attempts = config.get("max_login_attempts", 5)
        self.lockout_duration = config.get("lockout_duration", 900)
        self.sessions = {}
        self.login_attempts = {}

    def create_session(self, user_id: str) -> str:
        """创建会话"""
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": time.time(),
            "last_accessed": time.time(),
        }
        return session_id

    def validate_session(self, request) -> bool:
        """验证会话"""
        session_id = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not session_id or session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        now = time.time()

        # 检查会话是否过期
        if now - session["last_accessed"] > self.session_timeout:
            del self.sessions[session_id]
            return False

        # 更新最后访问时间
        session["last_accessed"] = now
        return True


def secure_hash(data: str, salt: Optional[str] = None) -> str:
    """安全哈希函数"""
    if salt is None:
        salt = secrets.token_hex(16)

    # 使用PBKDF2进行密钥派生
    key = hashlib.pbkdf2_hmac("sha256", data.encode(), salt.encode(), 100000)
    return f"{salt}:{key.hex()}"


def verify_hash(data: str, hashed: str) -> bool:
    """验证哈希"""
    try:
        salt, key = hashed.split(":")
        return secure_hash(data, salt) == hashed
    except ValueError:
        return False


def require_auth(f):
    """认证装饰器"""

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # 这里应该实现具体的认证逻辑
        return await f(*args, **kwargs)

    return decorated_function


def sanitize_input(data: Any) -> Any:
    """输入清理"""
    if isinstance(data, str):
        # 移除潜在的恶意字符
        dangerous_chars = ["<", ">", '"', "'", "&", "script", "javascript"]
        for char in dangerous_chars:
            data = data.replace(char, "")

    return data
