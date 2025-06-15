#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异常处理模块

定义认证服务的所有自定义异常类。
"""

class AuthServiceException(Exception):
    """认证服务基础异常"""
    pass

class AuthenticationError(AuthServiceException):
    """认证错误"""
    pass

class ValidationError(AuthServiceException):
    """验证错误"""
    pass

class ExternalServiceError(AuthServiceException):
    """外部服务错误"""
    pass

class BiometricError(AuthServiceException):
    """生物识别错误"""
    pass

class BlockchainError(AuthServiceException):
    """区块链错误"""
    pass

class TokenError(AuthServiceException):
    """令牌错误"""
    pass

class TokenExpiredError(TokenError):
    """令牌过期错误"""
    pass

class TokenInvalidError(TokenError):
    """令牌无效错误"""
    pass

class DatabaseError(AuthServiceException):
    """数据库错误"""
    pass

class ConfigurationError(AuthServiceException):
    """配置错误"""
    pass

__all__ = [
    'AuthServiceException',
    'AuthenticationError', 
    'ValidationError',
    'ExternalServiceError',
    'BiometricError',
    'BlockchainError',
    'TokenError',
    'TokenExpiredError',
    'TokenInvalidError',
    'DatabaseError',
    'ConfigurationError'
] 