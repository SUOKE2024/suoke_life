#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
错误模型模块

定义认证服务使用的错误类型，实现统一的错误处理。
支持REST API和gRPC服务的错误映射。
"""
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import grpc


class ErrorCode(Enum):
    """错误码枚举"""
    # 认证相关错误 (1000-1099)
    INVALID_CREDENTIALS = (1001, "凭证无效", grpc.StatusCode.UNAUTHENTICATED, 401)
    USER_NOT_FOUND = (1002, "用户不存在", grpc.StatusCode.NOT_FOUND, 404)
    ACCOUNT_LOCKED = (1003, "账户已锁定", grpc.StatusCode.PERMISSION_DENIED, 403)
    ACCOUNT_DISABLED = (1004, "账户已禁用", grpc.StatusCode.PERMISSION_DENIED, 403)
    PASSWORD_EXPIRED = (1005, "密码已过期", grpc.StatusCode.FAILED_PRECONDITION, 403)
    INVALID_TOKEN = (1006, "令牌无效", grpc.StatusCode.UNAUTHENTICATED, 401)
    TOKEN_EXPIRED = (1007, "令牌已过期", grpc.StatusCode.UNAUTHENTICATED, 401)
    
    # 用户管理相关错误 (1100-1199)
    USER_EXISTS = (1101, "用户已存在", grpc.StatusCode.ALREADY_EXISTS, 409)
    EMAIL_EXISTS = (1102, "邮箱已被注册", grpc.StatusCode.ALREADY_EXISTS, 409)
    PHONE_EXISTS = (1103, "手机号已被注册", grpc.StatusCode.ALREADY_EXISTS, 409)
    INVALID_PASSWORD = (1104, "密码不符合要求", grpc.StatusCode.INVALID_ARGUMENT, 400)
    INVALID_EMAIL = (1105, "邮箱格式不正确", grpc.StatusCode.INVALID_ARGUMENT, 400)
    INVALID_PHONE = (1106, "手机号格式不正确", grpc.StatusCode.INVALID_ARGUMENT, 400)
    PASSWORD_POLICY_ERROR = (1107, "密码策略不符合要求", grpc.StatusCode.INVALID_ARGUMENT, 400)
    
    # 权限相关错误 (1200-1299)
    PERMISSION_DENIED = (1201, "没有操作权限", grpc.StatusCode.PERMISSION_DENIED, 403)
    ROLE_NOT_FOUND = (1202, "角色不存在", grpc.StatusCode.NOT_FOUND, 404)
    PERMISSION_NOT_FOUND = (1203, "权限不存在", grpc.StatusCode.NOT_FOUND, 404)
    
    # 多因素认证相关错误 (1300-1399)
    MFA_REQUIRED = (1301, "需要多因素认证", grpc.StatusCode.FAILED_PRECONDITION, 403)
    MFA_INVALID_CODE = (1302, "验证码无效", grpc.StatusCode.INVALID_ARGUMENT, 401)
    MFA_SETUP_REQUIRED = (1303, "需要设置多因素认证", grpc.StatusCode.FAILED_PRECONDITION, 403)
    MFA_ALREADY_ENABLED = (1304, "多因素认证已启用", grpc.StatusCode.ALREADY_EXISTS, 409)
    MFA_NOT_ENABLED = (1305, "多因素认证未启用", grpc.StatusCode.FAILED_PRECONDITION, 400)
    MFA_VERIFICATION_ERROR = (1306, "多因素认证验证失败", grpc.StatusCode.INVALID_ARGUMENT, 401)
    INVALID_VERIFICATION_CODE = (1307, "验证码无效", grpc.StatusCode.INVALID_ARGUMENT, 401)
    
    # 一般错误 (1900-1999)
    VALIDATION_ERROR = (1901, "请求参数验证失败", grpc.StatusCode.INVALID_ARGUMENT, 400)
    DATABASE_ERROR = (1902, "数据库操作错误", grpc.StatusCode.INTERNAL, 500)
    RATE_LIMIT_EXCEEDED = (1903, "请求频率超限", grpc.StatusCode.RESOURCE_EXHAUSTED, 429)
    INTERNAL_ERROR = (1904, "服务内部错误", grpc.StatusCode.INTERNAL, 500)
    CONFIGURATION_ERROR = (1905, "配置错误", grpc.StatusCode.INTERNAL, 500)
    
    def __init__(self, code: int, message: str, grpc_code: grpc.StatusCode, http_status: int):
        self.code = code
        self.message = message
        self.grpc_code = grpc_code
        self.http_status = http_status


class AuthServiceError(Exception):
    """认证服务错误基类"""
    
    def __init__(
        self, 
        error_code: ErrorCode, 
        message: Optional[str] = None, 
        details: Any = None
    ):
        self.error_code = error_code
        self.message = message or error_code.message
        self.details = details
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.error_code.code,
            "message": self.message,
            "success": False
        }
        
        if self.details:
            result["details"] = self.details
            
        return result
    
    def to_grpc_error(self) -> grpc.RpcError:
        """转换为gRPC错误"""
        return grpc.aio.ServicerError(
            self.error_code.grpc_code,
            f"{self.message} (code={self.error_code.code})"
        )
    
    @property
    def http_status(self) -> int:
        """获取HTTP状态码"""
        return self.error_code.http_status


# 认证相关错误
class CredentialsError(AuthServiceError):
    """凭证错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.INVALID_CREDENTIALS, message, details)


class UserNotFoundError(AuthServiceError):
    """用户不存在错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.USER_NOT_FOUND, message, details)


class AccountLockedError(AuthServiceError):
    """账户锁定错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.ACCOUNT_LOCKED, message, details)


class InvalidTokenError(AuthServiceError):
    """无效令牌错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.INVALID_TOKEN, message, details)


class TokenExpiredError(AuthServiceError):
    """令牌过期错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.TOKEN_EXPIRED, message, details)


# 用户管理相关错误
class UserExistsError(AuthServiceError):
    """用户已存在错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.USER_EXISTS, message, details)


class EmailExistsError(AuthServiceError):
    """邮箱已存在错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.EMAIL_EXISTS, message, details)


class PhoneExistsError(AuthServiceError):
    """手机号已存在错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.PHONE_EXISTS, message, details)


class InvalidPasswordError(AuthServiceError):
    """密码不符合要求错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.INVALID_PASSWORD, message, details)


class PasswordPolicyError(AuthServiceError):
    """密码策略错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.PASSWORD_POLICY_ERROR, message, details)


# 权限相关错误
class PermissionDeniedError(AuthServiceError):
    """权限不足错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.PERMISSION_DENIED, message, details)


class RoleNotFoundError(AuthServiceError):
    """角色不存在错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.ROLE_NOT_FOUND, message, details)


# 多因素认证相关错误
class MFARequiredError(AuthServiceError):
    """需要多因素认证错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.MFA_REQUIRED, message, details)


class MFAInvalidCodeError(AuthServiceError):
    """多因素认证码无效错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.MFA_INVALID_CODE, message, details)


class MFANotEnabledError(AuthServiceError):
    """多因素认证未启用错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.MFA_NOT_ENABLED, message, details)


class MFAVerificationError(AuthServiceError):
    """多因素认证验证失败错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.MFA_VERIFICATION_ERROR, message, details)


class InvalidVerificationCodeError(AuthServiceError):
    """验证码无效错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.INVALID_VERIFICATION_CODE, message, details)


# 一般错误
class ValidationError(AuthServiceError):
    """请求参数验证失败错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.VALIDATION_ERROR, message, details)


class DatabaseError(AuthServiceError):
    """数据库操作错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.DATABASE_ERROR, message, details)


class RateLimitExceededError(AuthServiceError):
    """请求频率超限错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.RATE_LIMIT_EXCEEDED, message, details)


class InternalError(AuthServiceError):
    """服务内部错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.INTERNAL_ERROR, message, details)


class ConfigurationError(AuthServiceError):
    """配置错误"""
    def __init__(self, message: Optional[str] = None, details: Any = None):
        super().__init__(ErrorCode.CONFIGURATION_ERROR, message, details) 