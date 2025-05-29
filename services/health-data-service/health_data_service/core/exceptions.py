"""自定义异常类"""

from typing import Any


class HealthDataServiceError(Exception):
    """健康数据服务基础异常"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(HealthDataServiceError):
    """数据验证异常"""

    def __init__(
        self,
        message: str = "数据验证失败",
        field: str | None = None,
        value: Any | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"field": field, "value": value, **kwargs}
        super().__init__(message, "VALIDATION_ERROR", details)


class DatabaseError(HealthDataServiceError):
    """数据库操作异常"""

    def __init__(
        self,
        message: str = "数据库操作失败",
        operation: str | None = None,
        table: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"operation": operation, "table": table, **kwargs}
        super().__init__(message, "DATABASE_ERROR", details)


class CacheError(HealthDataServiceError):
    """缓存操作异常"""

    def __init__(
        self,
        message: str = "缓存操作失败",
        key: str | None = None,
        operation: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"key": key, "operation": operation, **kwargs}
        super().__init__(message, "CACHE_ERROR", details)


class AuthenticationError(HealthDataServiceError):
    """认证异常"""

    def __init__(self, message: str = "认证失败", **kwargs: Any) -> None:
        super().__init__(message, "AUTHENTICATION_ERROR", kwargs)


class AuthorizationError(HealthDataServiceError):
    """授权异常"""

    def __init__(
        self,
        message: str = "权限不足",
        required_permission: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"required_permission": required_permission, **kwargs}
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class NotFoundError(HealthDataServiceError):
    """资源未找到异常"""

    def __init__(
        self,
        message: str = "资源未找到",
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"resource_type": resource_type, "resource_id": resource_id, **kwargs}
        super().__init__(message, "NOT_FOUND_ERROR", details)


class ConflictError(HealthDataServiceError):
    """资源冲突异常"""

    def __init__(
        self,
        message: str = "资源冲突",
        resource_type: str | None = None,
        conflict_field: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"resource_type": resource_type, "conflict_field": conflict_field, **kwargs}
        super().__init__(message, "CONFLICT_ERROR", details)


class ExternalServiceError(HealthDataServiceError):
    """外部服务调用异常"""

    def __init__(
        self,
        message: str = "外部服务调用失败",
        service_name: str | None = None,
        status_code: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"service_name": service_name, "status_code": status_code, **kwargs}
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class ModelInferenceError(HealthDataServiceError):
    """模型推理异常"""

    def __init__(
        self,
        message: str = "模型推理失败",
        model_name: str | None = None,
        model_version: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"model_name": model_name, "model_version": model_version, **kwargs}
        super().__init__(message, "MODEL_INFERENCE_ERROR", details)


class RateLimitError(HealthDataServiceError):
    """请求频率限制异常"""

    def __init__(
        self,
        message: str = "请求频率过高",
        limit: int | None = None,
        window: int | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"limit": limit, "window": window, **kwargs}
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class ConfigurationError(HealthDataServiceError):
    """配置错误异常"""

    def __init__(
        self,
        message: str = "配置错误",
        config_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        details = {"config_key": config_key, **kwargs}
        super().__init__(message, "CONFIGURATION_ERROR", details)
