"""
统一异常处理系统

定义认证服务的所有自定义异常类型。
"""
from typing import Optional, Dict, Any


class AuthServiceException(Exception):
    """认证服务基础异常"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AuthServiceException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败", **kwargs):
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)


class AuthorizationError(AuthServiceException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足", **kwargs):
        super().__init__(message, error_code="AUTHORIZATION_FAILED", **kwargs)


class TokenError(AuthServiceException):
    """令牌相关错误"""
    pass


class TokenExpiredError(TokenError):
    """令牌过期错误"""
    
    def __init__(self, message: str = "令牌已过期", **kwargs):
        super().__init__(message, error_code="TOKEN_EXPIRED", **kwargs)


class TokenInvalidError(TokenError):
    """令牌无效错误"""
    
    def __init__(self, message: str = "无效的令牌", **kwargs):
        super().__init__(message, error_code="TOKEN_INVALID", **kwargs)


class TokenRevokedError(TokenError):
    """令牌已撤销错误"""
    
    def __init__(self, message: str = "令牌已被撤销", **kwargs):
        super().__init__(message, error_code="TOKEN_REVOKED", **kwargs)


class UserError(AuthServiceException):
    """用户相关错误"""
    pass


class UserNotFoundError(UserError):
    """用户不存在错误"""
    
    def __init__(self, message: str = "用户不存在", **kwargs):
        super().__init__(message, error_code="USER_NOT_FOUND", **kwargs)


class UserInactiveError(UserError):
    """用户账户已禁用错误"""
    
    def __init__(self, message: str = "用户账户已禁用", **kwargs):
        super().__init__(message, error_code="USER_INACTIVE", **kwargs)


class UserAlreadyExistsError(UserError):
    """用户已存在错误"""
    
    def __init__(self, message: str = "用户已存在", **kwargs):
        super().__init__(message, error_code="USER_ALREADY_EXISTS", **kwargs)


class PasswordError(AuthServiceException):
    """密码相关错误"""
    pass


class PasswordInvalidError(PasswordError):
    """密码无效错误"""
    
    def __init__(self, message: str = "密码无效", **kwargs):
        super().__init__(message, error_code="PASSWORD_INVALID", **kwargs)


class PasswordWeakError(PasswordError):
    """密码强度不足错误"""
    
    def __init__(self, message: str = "密码强度不符合要求", **kwargs):
        super().__init__(message, error_code="PASSWORD_WEAK", **kwargs)


class MFAError(AuthServiceException):
    """多因子认证错误"""
    pass


class MFARequiredError(MFAError):
    """需要多因子认证错误"""
    
    def __init__(self, message: str = "需要多因子认证", **kwargs):
        super().__init__(message, error_code="MFA_REQUIRED", **kwargs)


class MFAInvalidError(MFAError):
    """多因子认证无效错误"""
    
    def __init__(self, message: str = "多因子认证验证失败", **kwargs):
        super().__init__(message, error_code="MFA_INVALID", **kwargs)


class MFANotSetupError(MFAError):
    """多因子认证未设置错误"""
    
    def __init__(self, message: str = "多因子认证未设置", **kwargs):
        super().__init__(message, error_code="MFA_NOT_SETUP", **kwargs)


class RateLimitError(AuthServiceException):
    """速率限制错误"""
    
    def __init__(self, message: str = "请求过于频繁", **kwargs):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", **kwargs)


class ValidationError(AuthServiceException):
    """数据验证错误"""
    
    def __init__(self, message: str = "数据验证失败", **kwargs):
        super().__init__(message, error_code="VALIDATION_FAILED", **kwargs)


class DatabaseError(AuthServiceException):
    """数据库操作错误"""
    
    def __init__(self, message: str = "数据库操作失败", **kwargs):
        super().__init__(message, error_code="DATABASE_ERROR", **kwargs)


class ExternalServiceError(AuthServiceException):
    """外部服务错误"""
    
    def __init__(self, message: str = "外部服务调用失败", **kwargs):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", **kwargs)


class EmailServiceError(ExternalServiceError):
    """邮件服务错误"""
    
    def __init__(self, message: str = "邮件发送失败", **kwargs):
        super().__init__(message, error_code="EMAIL_SERVICE_ERROR", **kwargs)


class SMSServiceError(ExternalServiceError):
    """短信服务错误"""
    
    def __init__(self, message: str = "短信发送失败", **kwargs):
        super().__init__(message, error_code="SMS_SERVICE_ERROR", **kwargs)


class ConfigurationError(AuthServiceException):
    """配置错误"""
    
    def __init__(self, message: str = "配置错误", **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs) 