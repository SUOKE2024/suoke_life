#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全模块
提供加密、认证、授权等安全功能
"""

from .encryption import (
    EncryptionService,
    hash_password,
    verify_password,
    generate_secure_token,
    generate_api_key,
    hash_data,
    validate_password_strength,
    get_encryption_service,
    encrypt_data,
    decrypt_data
)

from .auth import (
    User,
    TokenPayload,
    JWTManager,
    OAuth2Provider,
    APIKeyManager,
    PermissionChecker,
    hash_password as auth_hash_password,
    verify_password as auth_verify_password
)

__all__ = [
    # 加密服务
    'EncryptionService',
    'hash_password',
    'verify_password',
    'generate_secure_token',
    'generate_api_key',
    'hash_data',
    'validate_password_strength',
    'get_encryption_service',
    'encrypt_data',
    'decrypt_data',
    
    # 认证授权
    'User',
    'TokenPayload',
    'JWTManager',
    'OAuth2Provider',
    'APIKeyManager',
    'PermissionChecker'
] 