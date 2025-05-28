"""
自定义异常模块

定义服务特定的异常类，提供更好的错误处理和调试信息
"""

from typing import Any, Dict, Optional


class LaoKeServiceError(Exception):
    """老克服务基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }
    
    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"


class ConfigurationError(LaoKeServiceError):
    """配置错误"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details=details, **kwargs)


class ValidationError(LaoKeServiceError):
    """数据验证错误"""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)
        super().__init__(message, details=details, **kwargs)


class DatabaseError(LaoKeServiceError):
    """数据库操作错误"""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        super().__init__(message, details=details, **kwargs)


class ExternalServiceError(LaoKeServiceError):
    """外部服务调用错误"""
    
    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if service_name:
            details["service_name"] = service_name
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, details=details, **kwargs)


class AuthenticationError(LaoKeServiceError):
    """认证错误"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)


class AuthorizationError(LaoKeServiceError):
    """授权错误"""
    
    def __init__(
        self,
        message: str = "Access denied",
        resource: Optional[str] = None,
        action: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if resource:
            details["resource"] = resource
        if action:
            details["action"] = action
        super().__init__(message, details=details, **kwargs)


class RateLimitError(LaoKeServiceError):
    """速率限制错误"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: Optional[int] = None,
        window: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        super().__init__(message, details=details, **kwargs)


class AIServiceError(LaoKeServiceError):
    """AI 服务错误"""
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if model:
            details["model"] = model
        if provider:
            details["provider"] = provider
        super().__init__(message, details=details, **kwargs)


class KnowledgeBaseError(LaoKeServiceError):
    """知识库操作错误"""
    
    def __init__(
        self,
        message: str,
        knowledge_id: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if knowledge_id:
            details["knowledge_id"] = knowledge_id
        if operation:
            details["operation"] = operation
        super().__init__(message, details=details, **kwargs)


class CommunityError(LaoKeServiceError):
    """社区功能错误"""
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        content_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if user_id:
            details["user_id"] = user_id
        if content_id:
            details["content_id"] = content_id
        super().__init__(message, details=details, **kwargs)


class LearningPathError(LaoKeServiceError):
    """学习路径错误"""
    
    def __init__(
        self,
        message: str,
        path_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = kwargs.pop("details", {})
        if path_id:
            details["path_id"] = path_id
        if user_id:
            details["user_id"] = user_id
        super().__init__(message, details=details, **kwargs)


# 异常映射，用于快速查找
EXCEPTION_MAP = {
    "configuration": ConfigurationError,
    "validation": ValidationError,
    "database": DatabaseError,
    "external_service": ExternalServiceError,
    "authentication": AuthenticationError,
    "authorization": AuthorizationError,
    "rate_limit": RateLimitError,
    "ai_service": AIServiceError,
    "knowledge_base": KnowledgeBaseError,
    "community": CommunityError,
    "learning_path": LearningPathError,
}


def create_exception(
    exception_type: str,
    message: str,
    **kwargs: Any,
) -> LaoKeServiceError:
    """创建指定类型的异常"""
    exception_class = EXCEPTION_MAP.get(exception_type, LaoKeServiceError)
    return exception_class(message, **kwargs) 