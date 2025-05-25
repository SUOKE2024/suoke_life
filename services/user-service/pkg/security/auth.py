"""
认证和安全工具包
提供JWT令牌管理、密码加密、权限验证等功能
"""
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Union
import jwt
from passlib.hash import pbkdf2_sha256
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)


class PasswordManager:
    """密码管理器"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=30000
        )
    
    def hash_password(self, password: str) -> str:
        """加密密码"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            return self.pwd_context.verify(password, hashed)
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def generate_password(self, length: int = 12) -> str:
        """生成随机密码"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """检查密码强度"""
        score = 0
        feedback = []
        
        # 长度检查
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("密码长度至少8位")
        
        # 包含小写字母
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("需要包含小写字母")
        
        # 包含大写字母
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("需要包含大写字母")
        
        # 包含数字
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("需要包含数字")
        
        # 包含特殊字符
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
        else:
            feedback.append("需要包含特殊字符")
        
        # 评估强度
        if score >= 4:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "score": score,
            "strength": strength,
            "feedback": feedback
        }


class JWTManager:
    """JWT令牌管理器"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(hours=1)
        self.refresh_token_expire = timedelta(days=7)
    
    def create_access_token(
        self, 
        user_id: str, 
        roles: List[str] = None,
        permissions: Set[str] = None,
        extra_claims: Dict[str, Any] = None
    ) -> str:
        """创建访问令牌"""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.access_token_expire,
            "type": "access",
            "roles": roles or [],
            "permissions": list(permissions or set())
        }
        
        if extra_claims:
            payload.update(extra_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """创建刷新令牌"""
        now = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + self.refresh_token_expire,
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效令牌: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """使用刷新令牌获取新的访问令牌"""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # 这里应该从数据库获取用户的最新角色和权限
        # 为了简化，这里使用空值
        return self.create_access_token(user_id)
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """解码令牌（不验证签名，用于调试）"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            logger.error(f"解码令牌失败: {e}")
            return None


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        # 定义角色权限映射
        self.role_permissions = {
            "admin": {
                "user:create", "user:read", "user:update", "user:delete",
                "health:read", "health:update", "health:delete",
                "device:read", "device:update", "device:delete",
                "system:admin"
            },
            "user": {
                "user:read_own", "user:update_own",
                "health:read_own", "health:update_own",
                "device:read_own", "device:update_own"
            },
            "health_provider": {
                "user:read", "health:read", "health:update",
                "device:read"
            },
            "researcher": {
                "health:read_anonymous", "user:read_anonymous"
            },
            "agent": {
                "user:read", "health:read", "health:update",
                "device:read", "agent:interact"
            }
        }
    
    def get_permissions_for_roles(self, roles: List[str]) -> Set[str]:
        """获取角色对应的权限"""
        permissions = set()
        for role in roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])
        return permissions
    
    def has_permission(self, user_permissions: Set[str], required_permission: str) -> bool:
        """检查是否有指定权限"""
        return required_permission in user_permissions
    
    def has_any_permission(self, user_permissions: Set[str], required_permissions: List[str]) -> bool:
        """检查是否有任意一个权限"""
        return any(perm in user_permissions for perm in required_permissions)
    
    def has_all_permissions(self, user_permissions: Set[str], required_permissions: List[str]) -> bool:
        """检查是否有所有权限"""
        return all(perm in user_permissions for perm in required_permissions)
    
    def can_access_user_data(self, user_permissions: Set[str], target_user_id: str, current_user_id: str) -> bool:
        """检查是否可以访问用户数据"""
        # 管理员可以访问所有用户数据
        if "user:read" in user_permissions:
            return True
        
        # 用户可以访问自己的数据
        if "user:read_own" in user_permissions and target_user_id == current_user_id:
            return True
        
        return False


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """生成安全令牌"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key() -> str:
        """生成API密钥"""
        return f"sk_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """哈希API密钥"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(api_key: str, hashed_key: str) -> bool:
        """验证API密钥"""
        return hmac.compare_digest(
            hashlib.sha256(api_key.encode()).hexdigest(),
            hashed_key
        )
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """生成一次性密码"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
        """掩码敏感数据"""
        if len(data) <= visible_chars:
            return mask_char * len(data)
        
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        import re
        # 简单的中国手机号验证
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """清理输入文本"""
        import html
        # HTML转义
        text = html.escape(text)
        # 移除潜在的SQL注入字符
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        for char in dangerous_chars:
            text = text.replace(char, "")
        return text.strip()


class RateLimiter:
    """限流器"""
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count), ...]}
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup = time.time()
    
    def is_allowed(
        self, 
        key: str, 
        limit: int, 
        window: int = 60,
        burst_limit: Optional[int] = None
    ) -> bool:
        """检查是否允许请求"""
        now = time.time()
        
        # 定期清理过期记录
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_expired_records(now)
            self.last_cleanup = now
        
        # 获取或创建请求记录
        if key not in self.requests:
            self.requests[key] = []
        
        requests = self.requests[key]
        
        # 移除过期的请求记录
        cutoff_time = now - window
        requests[:] = [req for req in requests if req[0] > cutoff_time]
        
        # 计算当前窗口内的请求数
        current_count = sum(req[1] for req in requests)
        
        # 检查是否超过限制
        if current_count >= limit:
            return False
        
        # 检查突发限制
        if burst_limit and len(requests) >= burst_limit:
            return False
        
        # 记录新请求
        requests.append((now, 1))
        return True
    
    def _cleanup_expired_records(self, now: float):
        """清理过期记录"""
        cutoff_time = now - 3600  # 1小时前的记录
        for key in list(self.requests.keys()):
            self.requests[key] = [
                req for req in self.requests[key] 
                if req[0] > cutoff_time
            ]
            if not self.requests[key]:
                del self.requests[key]
    
    def get_remaining_requests(self, key: str, limit: int, window: int = 60) -> int:
        """获取剩余请求数"""
        if key not in self.requests:
            return limit
        
        now = time.time()
        cutoff_time = now - window
        requests = [req for req in self.requests[key] if req[0] > cutoff_time]
        current_count = sum(req[1] for req in requests)
        
        return max(0, limit - current_count)
    
    def reset_limit(self, key: str):
        """重置限制"""
        if key in self.requests:
            del self.requests[key] 