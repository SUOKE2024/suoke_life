"""老克智能体服务异常处理模块"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """错误码枚举"""

    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # 服务错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"

    # 数据库错误
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DATABASE_QUERY_ERROR"
    DATABASE_CONSTRAINT_ERROR = "DATABASE_CONSTRAINT_ERROR"

    # 缓存错误
    CACHE_CONNECTION_ERROR = "CACHE_CONNECTION_ERROR"
    CACHE_OPERATION_ERROR = "CACHE_OPERATION_ERROR"

    # AI模型错误
    AI_MODEL_ERROR = "AI_MODEL_ERROR"
    AI_MODEL_TIMEOUT = "AI_MODEL_TIMEOUT"
    AI_MODEL_QUOTA_EXCEEDED = "AI_MODEL_QUOTA_EXCEEDED"
    AI_MODEL_INVALID_RESPONSE = "AI_MODEL_INVALID_RESPONSE"

    # 会话错误
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    SESSION_LIMIT_EXCEEDED = "SESSION_LIMIT_EXCEEDED"

    # 知识库错误
    KNOWLEDGE_SERVICE_ERROR = "KNOWLEDGE_SERVICE_ERROR"
    KNOWLEDGE_NOT_FOUND = "KNOWLEDGE_NOT_FOUND"
    KNOWLEDGE_SEARCH_ERROR = "KNOWLEDGE_SEARCH_ERROR"

    # 用户服务错误
    USER_SERVICE_ERROR = "USER_SERVICE_ERROR"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_AUTHENTICATION_ERROR = "USER_AUTHENTICATION_ERROR"

    # 无障碍服务错误
    ACCESSIBILITY_SERVICE_ERROR = "ACCESSIBILITY_SERVICE_ERROR"
    ACCESSIBILITY_CONVERSION_ERROR = "ACCESSIBILITY_CONVERSION_ERROR"

    # 内容错误
    CONTENT_TOO_LONG = "CONTENT_TOO_LONG"
    CONTENT_INVALID_FORMAT = "CONTENT_INVALID_FORMAT"
    CONTENT_MODERATION_FAILED = "CONTENT_MODERATION_FAILED"

    # 教育服务错误
    EDUCATION_SERVICE_ERROR = "EDUCATION_SERVICE_ERROR"
    COURSE_NOT_FOUND = "COURSE_NOT_FOUND"
    LEARNING_PATH_ERROR = "LEARNING_PATH_ERROR"


class LaokeServiceException(Exception):
    """老克服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details,
        }

        if self.cause:
            result["cause"] = str(self.cause)

        return result

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"


class ValidationException(LaokeServiceException):
    """参数验证异常"""

    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(
            message=message, error_code=ErrorCode.INVALID_PARAMETER, details=details
        )


class ResourceNotFoundException(LaokeServiceException):
    """资源未找到异常"""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class PermissionDeniedException(LaokeServiceException):
    """权限拒绝异常"""

    def __init__(self, action: str, resource: Optional[str] = None):
        message = f"Permission denied for action: {action}"
        if resource:
            message += f" on resource: {resource}"

        super().__init__(
            message=message,
            error_code=ErrorCode.PERMISSION_DENIED,
            details={"action": action, "resource": resource},
        )


class RateLimitExceededException(LaokeServiceException):
    """速率限制超出异常"""

    def __init__(self, limit: int, window: int, current_count: int):
        super().__init__(
            message=f"Rate limit exceeded: {current_count}/{limit} requests in {window} seconds",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details={"limit": limit, "window": window, "current_count": current_count},
        )


class DatabaseException(LaokeServiceException):
    """数据库异常"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        error_code = ErrorCode.DATABASE_QUERY_ERROR

        # 根据异常类型选择错误码
        if cause:
            cause_str = str(cause).lower()
            if "connection" in cause_str:
                error_code = ErrorCode.DATABASE_CONNECTION_ERROR
            elif "constraint" in cause_str or "unique" in cause_str:
                error_code = ErrorCode.DATABASE_CONSTRAINT_ERROR

        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class CacheException(LaokeServiceException):
    """缓存异常"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        error_code = ErrorCode.CACHE_OPERATION_ERROR

        if cause and "connection" in str(cause).lower():
            error_code = ErrorCode.CACHE_CONNECTION_ERROR

        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class AIModelException(LaokeServiceException):
    """
    AI模型异常"""

    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        error_type: str = "general",
        cause: Optional[Exception] = None,
    ):
        # 根据错误类型选择错误码
        error_code_map = {
            "timeout": ErrorCode.AI_MODEL_TIMEOUT,
            "quota": ErrorCode.AI_MODEL_QUOTA_EXCEEDED,
            "invalid_response": ErrorCode.AI_MODEL_INVALID_RESPONSE,
            "general": ErrorCode.AI_MODEL_ERROR,
        }

        error_code = error_code_map.get(error_type, ErrorCode.AI_MODEL_ERROR)

        details = {"error_type": error_type}
        if model_name:
            details["model_name"] = model_name

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class SessionException(LaokeServiceException):
    """会话异常"""

    def __init__(
        self,
        message: str,
        session_id: Optional[str] = None,
        error_type: str = "general",
    ):
        error_code_map = {
            "not_found": ErrorCode.SESSION_NOT_FOUND,
            "expired": ErrorCode.SESSION_EXPIRED,
            "limit_exceeded": ErrorCode.SESSION_LIMIT_EXCEEDED,
        }

        error_code = error_code_map.get(error_type, ErrorCode.UNKNOWN_ERROR)

        details = {"error_type": error_type}
        if session_id:
            details["session_id"] = session_id

        super().__init__(message=message, error_code=error_code, details=details)


class KnowledgeServiceException(LaokeServiceException):
    """知识服务异常"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        error_code = ErrorCode.KNOWLEDGE_SERVICE_ERROR

        if "not found" in message.lower():
            error_code = ErrorCode.KNOWLEDGE_NOT_FOUND
        elif "search" in message.lower():
            error_code = ErrorCode.KNOWLEDGE_SEARCH_ERROR

        details = {}
        if operation:
            details["operation"] = operation

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class UserServiceException(LaokeServiceException):
    """用户服务异常"""

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        error_code = ErrorCode.USER_SERVICE_ERROR

        if "not found" in message.lower():
            error_code = ErrorCode.USER_NOT_FOUND
        elif "authentication" in message.lower() or "auth" in message.lower():
            error_code = ErrorCode.USER_AUTHENTICATION_ERROR

        details = {}
        if user_id:
            details["user_id"] = user_id

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class AccessibilityServiceException(LaokeServiceException):
    """无障碍服务异常"""

    def __init__(
        self,
        message: str,
        conversion_type: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        error_code = ErrorCode.ACCESSIBILITY_SERVICE_ERROR

        if "conversion" in message.lower():
            error_code = ErrorCode.ACCESSIBILITY_CONVERSION_ERROR

        details = {}
        if conversion_type:
            details["conversion_type"] = conversion_type

        super().__init__(
            message=message, error_code=error_code, details=details, cause=cause
        )


class ContentException(LaokeServiceException):
    """内容异常"""

    def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        error_type: str = "general",
    ):
        error_code_map = {
            "too_long": ErrorCode.CONTENT_TOO_LONG,
            "invalid_format": ErrorCode.CONTENT_INVALID_FORMAT,
            "moderation_failed": ErrorCode.CONTENT_MODERATION_FAILED,
        }

        error_code = error_code_map.get(error_type, ErrorCode.INVALID_REQUEST)

        details = {"error_type": error_type}
        if content_type:
            details["content_type"] = content_type

        super().__init__(message=message, error_code=error_code, details=details)


class EducationServiceException(LaokeServiceException):
    """教育服务异常"""

    def __init__(
        self,
        message: str,
        resource_id: Optional[str] = None,
        error_type: str = "general",
    ):
        error_code_map = {
            "course_not_found": ErrorCode.COURSE_NOT_FOUND,
            "learning_path_error": ErrorCode.LEARNING_PATH_ERROR,
            "general": ErrorCode.EDUCATION_SERVICE_ERROR,
        }

        error_code = error_code_map.get(error_type, ErrorCode.EDUCATION_SERVICE_ERROR)

        details = {"error_type": error_type}
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message=message, error_code=error_code, details=details)


class ConfigurationException(LaokeServiceException):
    """配置异常"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(
            message=message, error_code=ErrorCode.CONFIGURATION_ERROR, details=details
        )


def handle_exception(exc: Exception) -> LaokeServiceException:
    """将通用异常转换为LaokeServiceException"""
    if isinstance(exc, LaokeServiceException):
        return exc

    # 根据异常类型进行转换
    exc_str = str(exc).lower()
    exc_type = type(exc).__name__.lower()

    if "database" in exc_str or "sql" in exc_str or "connection" in exc_type:
        return DatabaseException(f"Database error: {exc}", cause=exc)
    elif "redis" in exc_str or "cache" in exc_str:
        return CacheException(f"Cache error: {exc}", cause=exc)
    elif "timeout" in exc_str:
        return AIModelException(
            f"Operation timeout: {exc}", error_type="timeout", cause=exc
        )
    elif "permission" in exc_str or "access" in exc_str:
        return PermissionDeniedException("Unknown action")
    elif "not found" in exc_str:
        return ResourceNotFoundException("Unknown resource", "unknown")
    else:
        return LaokeServiceException(
            message=f"Unexpected error: {exc}",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR,
            cause=exc,
        )
