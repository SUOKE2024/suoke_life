
"""
异常定义模块 - 定义所有微服务共用的标准异常类

本模块定义了统一的异常类层次结构，用于规范化错误处理方式，
确保所有微服务以一致的方式处理和报告错误。
"""


class BaseServiceError(Exception):
    """
    服务错误基类

    所有服务自定义异常的基类，包含错误码和错误消息。
    """

    def __init__(self, message: str = "", code: str = "", details: dict = None):
        """
        初始化服务错误

        Args:
            message: 错误消息
            code: 错误代码
            details: 错误详细信息，可用于日志记录或调试
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class InvalidInputError(BaseServiceError):
    """
    无效输入错误

    当客户端提供的输入数据无效或不符合要求时使用此异常
    """

    def __init__(
        self,
        message: str = "Invalid input",
        code: str = "INVALID_INPUT",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class AuthenticationError(BaseServiceError):
    """
    认证错误

    当用户认证失败时使用此异常
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_FAILED",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class AuthorizationError(BaseServiceError):
    """
    授权错误

    当用户没有足够权限执行操作时使用此异常
    """

    def __init__(
        self,
        message: str = "Not authorized",
        code: str = "NOT_AUTHORIZED",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ResourceNotFoundError(BaseServiceError):
    """
    资源未找到错误

    当请求的资源不存在时使用此异常
    """

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ResourceExistsError(BaseServiceError):
    """
    资源已存在错误

    当尝试创建已存在的资源时使用此异常
    """

    def __init__(
        self,
        message: str = "Resource already exists",
        code: str = "ALREADY_EXISTS",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ProcessingError(BaseServiceError):
    """
    处理错误

    当服务在处理请求过程中遇到错误时使用此异常
    """

    def __init__(
        self,
        message: str = "Processing error",
        code: str = "PROCESSING_ERROR",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class DatabaseError(BaseServiceError):
    """
    数据库错误

    当与数据库交互出现问题时使用此异常
    """

    def __init__(
        self,
        message: str = "Database error",
        code: str = "DB_ERROR",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ModelError(BaseServiceError):
    """
    模型错误

    当AI模型推理或加载过程中出现问题时使用此异常
    """

    def __init__(
        self,
        message: str = "Model error",
        code: str = "MODEL_ERROR",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ServiceUnavailableError(BaseServiceError):
    """
    服务不可用错误

    当服务暂时不可用时使用此异常
    """

    def __init__(
        self,
        message: str = "Service unavailable",
        code: str = "SERVICE_UNAVAILABLE",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class TimeoutError(BaseServiceError):
    """
    超时错误

    当请求处理超时时使用此异常
    """

    def __init__(
        self,
        message: str = "Request timed out",
        code: str = "TIMEOUT",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ValidationError(InvalidInputError):
    """
    验证错误

    数据验证失败时使用此异常，是InvalidInputError的具体化形式
    """

    def __init__(
        self,
        message: str = "Validation failed",
        code: str = "VALIDATION_ERROR",
        details: dict = None,
    ):
        super().__init__(message, code, details)


class ExternalServiceError(BaseServiceError):
    """
    外部服务错误

    当调用外部服务出现问题时使用此异常
    """

    def __init__(
        self,
        message: str = "External service error",
        code: str = "EXTERNAL_ERROR",
        details: dict = None,
    ):
        super().__init__(message, code, details)
