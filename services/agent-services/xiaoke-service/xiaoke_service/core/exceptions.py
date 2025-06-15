"""
异常定义模块

定义小克服务的自定义异常类，提供详细的错误信息和错误码。
"""

from typing import Any, Dict, Optional


class XiaokeServiceError(Exception):
    """小克服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str = "XIAOKE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
            status_code: HTTP状态码
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
            }
        }


class ConfigurationError(XiaokeServiceError):
    """配置错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            status_code=500,
        )


class DatabaseError(XiaokeServiceError):
    """数据库错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=500,
        )


class AIServiceError(XiaokeServiceError):
    """AI服务错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            details=details,
            status_code=500,
        )


class ValidationError(XiaokeServiceError):
    """验证错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=400,
        )


class AuthenticationError(XiaokeServiceError):
    """认证错误"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details,
            status_code=401,
        )


class AuthorizationError(XiaokeServiceError):
    """授权错误"""

    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details,
            status_code=403,
        )


class NotFoundError(XiaokeServiceError):
    """资源未找到错误"""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND_ERROR",
            details=details,
            status_code=404,
        )


class RateLimitError(XiaokeServiceError):
    """限流错误"""

    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details=details,
            status_code=429,
        )


class ExternalServiceError(XiaokeServiceError):
    """外部服务错误"""

    def __init__(self, message: str, service_name: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            status_code=502,
        )


class KnowledgeBaseError(XiaokeServiceError):
    """知识库错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="KNOWLEDGE_BASE_ERROR",
            details=details,
            status_code=500,
        )


class TCMAnalysisError(XiaokeServiceError):
    """中医分析错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="TCM_ANALYSIS_ERROR",
            details=details,
            status_code=500,
        )


class HealthDataError(XiaokeServiceError):
    """健康数据错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="HEALTH_DATA_ERROR",
            details=details,
            status_code=400,
        )


class SessionError(XiaokeServiceError):
    """会话错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            details=details,
            status_code=400,
        )


class ResourceError(XiaokeServiceError):
    """资源错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RESOURCE_ERROR",
            details=details,
            status_code=500,
        )


class AppointmentError(XiaokeServiceError):
    """预约错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="APPOINTMENT_ERROR",
            details=details,
            status_code=400,
        )


class ProductError(XiaokeServiceError):
    """产品错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="PRODUCT_ERROR",
            details=details,
            status_code=400,
        )


class RecommendationError(XiaokeServiceError):
    """推荐错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RECOMMENDATION_ERROR",
            details=details,
            status_code=500,
        )


class AccessibilityError(XiaokeServiceError):
    """无障碍服务错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ACCESSIBILITY_ERROR",
            details=details,
            status_code=500,
        )