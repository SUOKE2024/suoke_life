"""用户服务异常定义"""


class UserServiceException(Exception):
    """用户服务基础异常"""

    def __init__(self, message: str, error_code: str = None):
        """TODO: 添加文档字符串"""
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UserNotFoundError(UserServiceException):
    """用户不存在异常"""

    def __init__(self, message: str = "用户不存在"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "USER_NOT_FOUND")


class UserAlreadyExistsError(UserServiceException):
    """用户已存在异常"""

    def __init__(self, message: str = "用户已存在"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "USER_ALREADY_EXISTS")


class DeviceNotFoundError(UserServiceException):
    """设备不存在异常"""

    def __init__(self, message: str = "设备不存在"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "DEVICE_NOT_FOUND")


class DeviceAlreadyBoundError(UserServiceException):
    """设备已绑定异常"""

    def __init__(self, message: str = "设备已绑定"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "DEVICE_ALREADY_BOUND")


class InvalidCredentialsError(UserServiceException):
    """无效凭证异常"""

    def __init__(self, message: str = "无效的用户凭证"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "INVALID_CREDENTIALS")


class PermissionDeniedError(UserServiceException):
    """权限拒绝异常"""

    def __init__(self, message: str = "权限不足"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "PERMISSION_DENIED")


class ValidationError(UserServiceException):
    """数据验证异常"""

    def __init__(self, message: str = "数据验证失败"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "VALIDATION_ERROR")


class DatabaseError(UserServiceException):
    """数据库操作异常"""

    def __init__(self, message: str = "数据库操作失败"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "DATABASE_ERROR")


class ExternalServiceError(UserServiceException):
    """外部服务异常"""

    def __init__(self, message: str = "外部服务调用失败"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")


class RateLimitExceededError(UserServiceException):
    """频率限制异常"""

    def __init__(self, message: str = "请求频率超限"):
        """TODO: 添加文档字符串"""
        super().__init__(message, "RATE_LIMIT_EXCEEDED")
