"""
统一异常处理系统
定义应用中使用的所有异常类型
"""
from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """错误代码枚举"""
    # 通用错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # 用户相关错误
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    USER_INACTIVE = "USER_INACTIVE"
    USER_SUSPENDED = "USER_SUSPENDED"
    
    # 设备相关错误
    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"
    DEVICE_ALREADY_BOUND = "DEVICE_ALREADY_BOUND"
    DEVICE_LIMIT_EXCEEDED = "DEVICE_LIMIT_EXCEEDED"
    
    # 健康数据相关错误
    HEALTH_DATA_NOT_FOUND = "HEALTH_DATA_NOT_FOUND"
    INVALID_HEALTH_DATA = "INVALID_HEALTH_DATA"
    
    # 数据库相关错误
    DATABASE_ERROR = "DATABASE_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TRANSACTION_ERROR = "TRANSACTION_ERROR"


class BaseException(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class ValidationError(BaseException):
    """验证错误"""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field_errors": field_errors or {}},
            status_code=400
        )


class AuthenticationError(BaseException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=401
        )


class AuthorizationError(BaseException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=403
        )


class NotFoundError(BaseException):
    """资源未找到错误"""
    
    def __init__(self, message: str, resource_type: str = "resource"):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            details={"resource_type": resource_type},
            status_code=404
        )


class ConflictError(BaseException):
    """冲突错误"""
    
    def __init__(self, message: str, conflicting_field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            details={"conflicting_field": conflicting_field},
            status_code=409
        )


class RateLimitError(BaseException):
    """限流错误"""
    
    def __init__(self, message: str = "请求过于频繁", retry_after: Optional[int] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details={"retry_after": retry_after},
            status_code=429
        )


# 用户相关异常
class UserNotFoundError(NotFoundError):
    """用户未找到错误"""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"用户 {user_id} 不存在",
            resource_type="user"
        )
        self.error_code = ErrorCode.USER_NOT_FOUND


class UserAlreadyExistsError(ConflictError):
    """用户已存在错误"""
    
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"用户 {field} '{value}' 已存在",
            conflicting_field=field
        )
        self.error_code = ErrorCode.USER_ALREADY_EXISTS


class InvalidCredentialsError(AuthenticationError):
    """无效凭据错误"""
    
    def __init__(self, message: str = "用户名或密码错误"):
        super().__init__(message)
        self.error_code = ErrorCode.INVALID_CREDENTIALS


class UserInactiveError(AuthenticationError):
    """用户未激活错误"""
    
    def __init__(self, message: str = "用户账户未激活"):
        super().__init__(message)
        self.error_code = ErrorCode.USER_INACTIVE


class UserSuspendedError(AuthenticationError):
    """用户被暂停错误"""
    
    def __init__(self, message: str = "用户账户已被暂停"):
        super().__init__(message)
        self.error_code = ErrorCode.USER_SUSPENDED


# 设备相关异常
class DeviceNotFoundError(NotFoundError):
    """设备未找到错误"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"设备 {device_id} 不存在",
            resource_type="device"
        )
        self.error_code = ErrorCode.DEVICE_NOT_FOUND


class DeviceAlreadyBoundError(ConflictError):
    """设备已绑定错误"""
    
    def __init__(self, device_id: str):
        super().__init__(
            message=f"设备 {device_id} 已被绑定",
            conflicting_field="device_id"
        )
        self.error_code = ErrorCode.DEVICE_ALREADY_BOUND


class DeviceLimitExceededError(ConflictError):
    """设备数量超限错误"""
    
    def __init__(self, limit: int):
        super().__init__(
            message=f"设备数量已达上限 {limit}",
            conflicting_field="device_count"
        )
        self.error_code = ErrorCode.DEVICE_LIMIT_EXCEEDED


# 健康数据相关异常
class HealthDataNotFoundError(NotFoundError):
    """健康数据未找到错误"""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"用户 {user_id} 的健康数据不存在",
            resource_type="health_data"
        )
        self.error_code = ErrorCode.HEALTH_DATA_NOT_FOUND


class InvalidHealthDataError(ValidationError):
    """无效健康数据错误"""
    
    def __init__(self, message: str, field_errors: Optional[Dict[str, str]] = None):
        super().__init__(message, field_errors)
        self.error_code = ErrorCode.INVALID_HEALTH_DATA


# 数据库相关异常
class DatabaseError(BaseException):
    """数据库错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            details={"operation": operation},
            status_code=500
        )


class ConnectionError(DatabaseError):
    """数据库连接错误"""
    
    def __init__(self, message: str = "数据库连接失败"):
        super().__init__(message)
        self.error_code = ErrorCode.CONNECTION_ERROR


class TransactionError(DatabaseError):
    """事务错误"""
    
    def __init__(self, message: str = "事务执行失败"):
        super().__init__(message)
        self.error_code = ErrorCode.TRANSACTION_ERROR 