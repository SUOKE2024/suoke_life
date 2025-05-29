#!/usr/bin/env python

"""
统一异常处理模块
"""

from typing import Any


class InquiryServiceError(Exception):
    """问诊服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str = "INQUIRY_ERROR",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(InquiryServiceError):
    """输入验证异常"""

    def __init__(
        self, message: str, field: str | None = None, value: Any | None = None
    ):
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = str(value)

        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field
        self.value = value


class ProcessingError(InquiryServiceError):
    """处理过程异常"""

    def __init__(
        self, message: str, operation: str | None = None, cause: Exception | None = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
        if cause:
            details["cause"] = str(cause)
            details["cause_type"] = type(cause).__name__

        super().__init__(message, "PROCESSING_ERROR", details)
        self.operation = operation
        self.cause = cause


class ConfigurationError(InquiryServiceError):
    """配置异常"""

    def __init__(self, message: str, config_key: str | None = None):
        details = {}
        if config_key:
            details["config_key"] = config_key

        super().__init__(message, "CONFIGURATION_ERROR", details)
        self.config_key = config_key


class ServiceUnavailableError(InquiryServiceError):
    """服务不可用异常"""

    def __init__(self, message: str, service_name: str | None = None):
        details = {}
        if service_name:
            details["service_name"] = service_name

        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service_name = service_name


class ResourceNotFoundError(InquiryServiceError):
    """资源未找到异常"""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message, "RESOURCE_NOT_FOUND", details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class TimeoutError(InquiryServiceError):
    """超时异常"""

    def __init__(
        self,
        message: str,
        timeout_seconds: float | None = None,
        operation: str | None = None,
    ):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if operation:
            details["operation"] = operation

        super().__init__(message, "TIMEOUT_ERROR", details)
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class RateLimitError(InquiryServiceError):
    """限流异常"""

    def __init__(
        self, message: str, limit: int | None = None, window_seconds: int | None = None
    ):
        details = {}
        if limit:
            details["limit"] = limit
        if window_seconds:
            details["window_seconds"] = window_seconds

        super().__init__(message, "RATE_LIMIT_ERROR", details)
        self.limit = limit
        self.window_seconds = window_seconds


class AuthenticationError(InquiryServiceError):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(InquiryServiceError):
    """授权异常"""

    def __init__(
        self, message: str = "权限不足", required_permission: str | None = None
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(message, "AUTHORIZATION_ERROR", details)
        self.required_permission = required_permission


class DataIntegrityError(InquiryServiceError):
    """数据完整性异常"""

    def __init__(self, message: str, data_type: str | None = None):
        details = {}
        if data_type:
            details["data_type"] = data_type

        super().__init__(message, "DATA_INTEGRITY_ERROR", details)
        self.data_type = data_type


class ExternalServiceError(InquiryServiceError):
    """外部服务异常"""

    def __init__(self, message: str, service_name: str, status_code: int | None = None):
        details = {"service_name": service_name}
        if status_code:
            details["status_code"] = status_code

        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)
        self.service_name = service_name
        self.status_code = status_code


def handle_exception(func):
    """异常处理装饰器"""

    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except InquiryServiceError:
            # 重新抛出已知的业务异常
            raise
        except Exception as e:
            # 将未知异常包装为ProcessingError
            raise ProcessingError(
                f"执行 {func.__name__} 时发生未知错误: {e!s}",
                operation=func.__name__,
                cause=e,
            )

    return wrapper
