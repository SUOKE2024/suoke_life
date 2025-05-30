#!/usr/bin/env python3
"""
安全模块
提供加密、认证、授权等安全功能
"""

from .auth import (
    APIKeyManager,
    JWTManager,
    OAuth2Provider,
    PermissionChecker,
    TokenPayload,
    User,
)
from .auth import (
    hash_password as auth_hash_password,
)
from .auth import (
    verify_password as auth_verify_password,
)
from .encryption import (
    EncryptionService,
    decrypt_data,
    encrypt_data,
    generate_api_key,
    generate_secure_token,
    get_encryption_service,
    hash_data,
    hash_password,
    validate_password_strength,
    verify_password,
)

__all__ = [
    "APIKeyManager",
    # 加密服务
    "EncryptionService",
    "JWTManager",
    "OAuth2Provider",
    "PermissionChecker",
    "TokenPayload",
    # 认证授权
    "User",
    "decrypt_data",
    "encrypt_data",
    "generate_api_key",
    "generate_secure_token",
    "get_encryption_service",
    "hash_data",
    "hash_password",
    "validate_password_strength",
    "verify_password",
]
