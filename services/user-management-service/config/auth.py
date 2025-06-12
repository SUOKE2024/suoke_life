"""
认证配置和工具函数
"""

import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from .settings import get_settings

logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthConfig:
    """认证配置类"""

    def __init__(self):
        self.secret_key = settings.auth.secret_key
        self.algorithm = settings.auth.algorithm
        self.access_token_expire_minutes = settings.auth.access_token_expire_minutes
        self.refresh_token_expire_days = settings.auth.refresh_token_expire_days

        # 密码策略
        self.password_min_length = settings.auth.password_min_length
        self.password_require_uppercase = settings.auth.password_require_uppercase
        self.password_require_lowercase = settings.auth.password_require_lowercase
        self.password_require_numbers = settings.auth.password_require_numbers
        self.password_require_special = settings.auth.password_require_special

        # 安全配置
        self.max_login_attempts = settings.auth.max_login_attempts
        self.lockout_duration_minutes = settings.auth.lockout_duration_minutes

        # MFA配置
        self.mfa_issuer = settings.auth.mfa_issuer
        self.mfa_enabled = settings.auth.mfa_enabled


class PasswordManager:
    """密码管理器"""

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """验证密码强度"""
        result = {"valid": True, "errors": [], "score": 0}

        # 长度检查
        if len(password) < settings.auth.password_min_length:
            result["valid"] = False
            result["errors"].append(
                f"密码长度至少{settings.auth.password_min_length}位"
            )
        else:
            result["score"] += 1

        # 大写字母检查
        if settings.auth.password_require_uppercase and not any(
            c.isupper() for c in password
        ):
            result["valid"] = False
            result["errors"].append("密码必须包含大写字母")
        else:
            result["score"] += 1

        # 小写字母检查
        if settings.auth.password_require_lowercase and not any(
            c.islower() for c in password
        ):
            result["valid"] = False
            result["errors"].append("密码必须包含小写字母")
        else:
            result["score"] += 1

        # 数字检查
        if settings.auth.password_require_numbers and not any(
            c.isdigit() for c in password
        ):
            result["valid"] = False
            result["errors"].append("密码必须包含数字")
        else:
            result["score"] += 1

        # 特殊字符检查
        if settings.auth.password_require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                result["valid"] = False
                result["errors"].append("密码必须包含特殊字符")
            else:
                result["score"] += 1

        return result

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """生成随机密码"""
        import random
        import string

        # 确保包含所有类型的字符
        chars = []
        chars.extend(random.choices(string.ascii_lowercase, k=2))
        chars.extend(random.choices(string.ascii_uppercase, k=2))
        chars.extend(random.choices(string.digits, k=2))
        chars.extend(random.choices("!@#$%^&*", k=2))

        # 填充剩余长度
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        chars.extend(random.choices(all_chars, k=length - len(chars)))

        # 打乱顺序
        random.shuffle(chars)

        return "".join(chars)


class TokenManager:
    """令牌管理器"""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建访问令牌"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.auth.access_token_expire_minutes
            )

        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.auth.refresh_token_expire_days
            )

        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(
            to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
        )
        return encoded_jwt

    @staticmethod
    def verify_token(
        token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token, settings.auth.secret_key, algorithms=[settings.auth.algorithm]
            )

            # 检查令牌类型
            if payload.get("type") != token_type:
                return None

            return payload

        except JWTError as e:
            logger.warning(f"令牌验证失败: {e}")
            return None

    @staticmethod
    def generate_session_token() -> str:
        """生成会话令牌"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_api_key() -> str:
        """生成API密钥"""
        return secrets.token_urlsafe(40)


class MFAManager:
    """多因素认证管理器"""

    @staticmethod
    def generate_secret() -> str:
        """生成MFA密钥"""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code_url(secret: str, user_email: str) -> str:
        """生成二维码URL"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email, issuer_name=settings.auth.mfa_issuer
        )

    @staticmethod
    def verify_totp(secret: str, token: str) -> bool:
        """验证TOTP令牌"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"TOTP验证失败: {e}")
            return False

    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """生成备用代码"""
        return [secrets.token_hex(4).upper() for _ in range(count)]


class SecurityUtils:
    """安全工具类"""

    @staticmethod
    def generate_csrf_token() -> str:
        """生成CSRF令牌"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_csrf_token(token: str, expected_token: str) -> bool:
        """验证CSRF令牌"""
        return hmac.compare_digest(token, expected_token)

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """哈希API密钥"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """生成验证码"""
        import random

        return "".join([str(random.randint(0, 9)) for _ in range(length)])

    @staticmethod
    def mask_email(email: str) -> str:
        """掩码邮箱地址"""
        if "@" not in email:
            return email

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """掩码手机号"""
        if len(phone) <= 4:
            return "*" * len(phone)

        return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]


# 全局实例
auth_config = AuthConfig()
password_manager = PasswordManager()
token_manager = TokenManager()
mfa_manager = MFAManager()
security_utils = SecurityUtils()

# 导出
__all__ = [
    "AuthConfig",
    "PasswordManager",
    "TokenManager",
    "MFAManager",
    "SecurityUtils",
    "auth_config",
    "password_manager",
    "token_manager",
    "mfa_manager",
    "security_utils",
]
