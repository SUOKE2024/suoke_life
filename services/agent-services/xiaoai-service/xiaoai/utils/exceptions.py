
"""
异常处理模块 - 定义服务相关的异常类
"""



class BaseServiceError(Exception):
    """
    服务基础异常类
    
    所有服务相关异常的基类，提供统一的错误处理接口
    """

    def __init__(
        self, message: str = "", code: str = "", details: dict | None = None
    ):
        """
        初始化服务错误
        
        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class InvalidInputError(BaseServiceError):
    """
    无效输入错误
    
    当用户输入不符合要求时抛出
    """

    def __init__(
        self,
        message: str = "Invalid input",
        code: str = "INVALID_INPUT",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class AuthenticationError(BaseServiceError):
    """
    认证错误
    
    当用户认证失败时抛出
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_FAILED",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class AuthorizationError(BaseServiceError):
    """
    授权错误
    
    当用户没有权限访问资源时抛出
    """

    def __init__(
        self,
        message: str = "Not authorized",
        code: str = "NOT_AUTHORIZED",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ResourceNotFoundError(BaseServiceError):
    """
    资源未找到错误
    
    当请求的资源不存在时抛出
    """

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ResourceExistsError(BaseServiceError):
    """
    资源已存在错误
    
    当尝试创建已存在的资源时抛出
    """

    def __init__(
        self,
        message: str = "Resource already exists",
        code: str = "ALREADY_EXISTS",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ProcessingError(BaseServiceError):
    """
    处理错误
    
    当业务逻辑处理失败时抛出
    """

    def __init__(
        self,
        message: str = "Processing error",
        code: str = "PROCESSING_ERROR",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class DatabaseError(BaseServiceError):
    """
    数据库错误
    
    当数据库操作失败时抛出
    """

    def __init__(
        self,
        message: str = "Database error",
        code: str = "DB_ERROR",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ModelError(BaseServiceError):
    """
    模型错误
    
    当AI模型调用失败时抛出
    """

    def __init__(
        self,
        message: str = "Model error",
        code: str = "MODEL_ERROR",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ServiceUnavailableError(BaseServiceError):
    """
    服务不可用错误
    
    当依赖的服务不可用时抛出
    """

    def __init__(
        self,
        message: str = "Service unavailable",
        code: str = "SERVICE_UNAVAILABLE",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class TimeoutError(BaseServiceError):
    """
    超时错误
    
    当请求超时时抛出
    """

    def __init__(
        self,
        message: str = "Request timed out",
        code: str = "TIMEOUT",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ValidationError(InvalidInputError):
    """
    验证错误
    
    当数据验证失败时抛出
    """

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: dict | None = None
    ):
        super().__init__(message, code, details)


class ExternalServiceError(BaseServiceError):
    """
    外部服务错误
    
    当调用外部服务失败时抛出
    """

    def __init__(
        self,
        message: str = "External service error",
        code: str = "EXTERNAL_ERROR",
        details: dict | None = None
    ):
        super().__init__(message, code, details)
