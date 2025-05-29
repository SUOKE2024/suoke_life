"""
自定义异常类

定义小克服务的各种异常类型, 提供详细的错误信息和错误码。
"""

from typing import Any


class XiaokeServiceError(Exception):
    """小克服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(XiaokeServiceError):
    """配置错误"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )


class DatabaseError(XiaokeServiceError):
    """数据库错误"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
        )


class AIServiceError(XiaokeServiceError):
    """AI服务错误"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            details=details,
        )


class AuthenticationError(XiaokeServiceError):
    """认证错误"""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(XiaokeServiceError):
    """授权错误"""

    def __init__(
        self, message: str = "Access denied", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class ValidationError(XiaokeServiceError):
    """数据验证错误"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ExternalServiceError(XiaokeServiceError):
    """外部服务错误"""

    def __init__(
        self, message: str, service_name: str, details: dict[str, Any] | None = None
    ):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class RateLimitError(XiaokeServiceError):
    """限流错误"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
        )


class ResourceNotFoundError(XiaokeServiceError):
    """资源未找到错误"""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
    ):
        message = f"{resource_type} with id '{resource_id}' not found"
        details = details or {}
        details.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
        )
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details,
        )


class BusinessLogicError(XiaokeServiceError):
    """业务逻辑错误"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details,
        )
