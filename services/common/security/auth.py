#!/usr/bin/env python3
"""
认证授权模块
提供JWT、OAuth2、API密钥等认证功能
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import logging
import secrets
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@dataclass
class User:
    """用户模型"""

    user_id: str
    username: str
    email: str | None = None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    is_active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenPayload:
    """令牌载荷"""

    sub: str  # Subject (user_id)
    exp: datetime | None = None
    iat: datetime | None = None
    jti: str | None = None  # JWT ID
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class JWTManager:
    """JWT管理器"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

        # 黑名单（实际应用中应使用Redis等持久化存储）
        self.blacklist: set = set()

    def create_access_token(
        self, user: User, expires_delta: timedelta | None = None
    ) -> str:
        """创建访问令牌"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        payload = {
            "sub": user.user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(secrets.token_urlsafe(16)),
            "type": "access",
            "username": user.username,
            "roles": user.roles,
            "permissions": user.permissions,
        }

        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(
        self, user: User, expires_delta: timedelta | None = None
    ) -> str:
        """创建刷新令牌"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user.user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(secrets.token_urlsafe(16)),
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload | None:
        """解码令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # 检查是否在黑名单中
            jti = payload.get("jti")
            if jti and jti in self.blacklist:
                logger.warning(f"令牌在黑名单中: {jti}")
                return None

            return TokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                jti=payload.get("jti"),
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                metadata=payload.get("metadata", {}),
            )
        except JWTError as e:
            logger.error(f"JWT解码错误: {e}")
            return None

    def revoke_token(self, token: str):
        """撤销令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            if jti:
                self.blacklist.add(jti)
                logger.info(f"令牌已撤销: {jti}")
        except JWTError:
            pass

    def is_token_revoked(self, token: str) -> bool:
        """检查令牌是否被撤销"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            return jti in self.blacklist if jti else False
        except JWTError:
            return True


class OAuth2Provider:
    """OAuth2提供者"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_codes: dict[str, dict[str, Any]] = {}
        self.access_tokens: dict[str, dict[str, Any]] = {}

    def generate_authorization_code(
        self,
        user_id: str,
        redirect_uri: str,
        scope: list[str],
        state: str | None = None,
    ) -> str:
        """生成授权码"""
        code = secrets.token_urlsafe(32)

        self.authorization_codes[code] = {
            "user_id": user_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
        }

        return code

    def exchange_code_for_token(
        self, code: str, redirect_uri: str
    ) -> dict[str, Any] | None:
        """用授权码换取访问令牌"""
        if code not in self.authorization_codes:
            return None

        auth_code = self.authorization_codes[code]

        # 验证
        if auth_code["redirect_uri"] != redirect_uri:
            return None

        if datetime.utcnow() > auth_code["expires_at"]:
            del self.authorization_codes[code]
            return None

        # 生成令牌
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        token_data = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token,
            "scope": " ".join(auth_code["scope"]),
            "user_id": auth_code["user_id"],
        }

        # 存储访问令牌
        self.access_tokens[access_token] = {
            "user_id": auth_code["user_id"],
            "scope": auth_code["scope"],
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=1),
        }

        # 删除使用过的授权码
        del self.authorization_codes[code]

        return token_data

    def validate_access_token(self, token: str) -> dict[str, Any] | None:
        """验证访问令牌"""
        if token not in self.access_tokens:
            return None

        token_data = self.access_tokens[token]

        if datetime.utcnow() > token_data["expires_at"]:
            del self.access_tokens[token]
            return None

        return token_data


class APIKeyManager:
    """API密钥管理器"""

    def __init__(self, hash_algorithm: str = "sha256"):
        self.hash_algorithm = hash_algorithm
        self.api_keys: dict[str, dict[str, Any]] = {}

    def generate_api_key(
        self,
        user_id: str,
        name: str,
        scopes: list[str],
        expires_at: datetime | None = None,
    ) -> tuple[str, str]:
        """
        生成API密钥

        Returns:
            tuple: (key_id, api_key)
        """
        key_id = f"sk_{secrets.token_urlsafe(8)}"
        api_key = secrets.token_urlsafe(32)

        # 哈希存储
        key_hash = self._hash_key(api_key)

        self.api_keys[key_id] = {
            "user_id": user_id,
            "name": name,
            "key_hash": key_hash,
            "scopes": scopes,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "last_used": None,
            "usage_count": 0,
        }

        return key_id, api_key

    def validate_api_key(self, key_id: str, api_key: str) -> dict[str, Any] | None:
        """验证API密钥"""
        if key_id not in self.api_keys:
            return None

        key_data = self.api_keys[key_id]

        # 检查过期
        if key_data["expires_at"] and datetime.utcnow() > key_data["expires_at"]:
            return None

        # 验证密钥
        if not self._verify_key(api_key, key_data["key_hash"]):
            return None

        # 更新使用信息
        key_data["last_used"] = datetime.utcnow()
        key_data["usage_count"] += 1

        return {
            "user_id": key_data["user_id"],
            "scopes": key_data["scopes"],
            "key_id": key_id,
        }

    def revoke_api_key(self, key_id: str) -> bool:
        """撤销API密钥"""
        if key_id in self.api_keys:
            del self.api_keys[key_id]
            return True
        return False

    def _hash_key(self, api_key: str) -> str:
        """哈希API密钥"""
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(api_key.encode()).hexdigest()
        elif self.hash_algorithm == "sha512":
            return hashlib.sha512(api_key.encode()).hexdigest()
        else:
            raise ValueError(f"不支持的哈希算法: {self.hash_algorithm}")

    def _verify_key(self, api_key: str, key_hash: str) -> bool:
        """验证API密钥"""
        return self._hash_key(api_key) == key_hash


class PermissionChecker:
    """权限检查器"""

    def __init__(self):
        self.role_permissions: dict[str, list[str]] = {}

    def add_role_permissions(self, role: str, permissions: list[str]):
        """添加角色权限"""
        if role not in self.role_permissions:
            self.role_permissions[role] = []
        self.role_permissions[role].extend(permissions)

    def check_permission(
        self,
        user_roles: list[str],
        user_permissions: list[str],
        required_permission: str,
    ) -> bool:
        """检查权限"""
        # 直接权限检查
        if required_permission in user_permissions:
            return True

        # 角色权限检查
        for role in user_roles:
            if role in self.role_permissions:
                if required_permission in self.role_permissions[role]:
                    return True

        return False

    def check_any_permission(
        self,
        user_roles: list[str],
        user_permissions: list[str],
        required_permissions: list[str],
    ) -> bool:
        """检查任一权限"""
        for permission in required_permissions:
            if self.check_permission(user_roles, user_permissions, permission):
                return True
        return False

    def check_all_permissions(
        self,
        user_roles: list[str],
        user_permissions: list[str],
        required_permissions: list[str],
    ) -> bool:
        """检查所有权限"""
        for permission in required_permissions:
            if not self.check_permission(user_roles, user_permissions, permission):
                return False
        return True


# 密码工具函数
def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)
