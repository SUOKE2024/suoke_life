"""
exceptions - 索克生活项目模块
"""

from typing import Any

"""
异常类定义模块

定义问诊服务中使用的所有自定义异常类。
"""



class InquiryServiceError(Exception):
    """问诊服务基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    )-> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self)-> str:
        """TODO: 添加文档字符串"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(InquiryServiceError):
    """配置错误"""

    def __init__(self, message: str, config_key: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "CONFIG_ERROR",
            details = {"config_key": config_key} if config_key else {},
        )


class ValidationError(InquiryServiceError):
    """数据验证错误"""

    def __init__(self, message: str, field: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "VALIDATION_ERROR",
            details = {"field": field} if field else {},
        )


class ServiceUnavailableError(InquiryServiceError):
    """服务不可用错误"""

    def __init__(self, service_name: str, reason: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        message = f"Service '{service_name}' is unavailable"
        if reason:
            message + = f": {reason}"
        super().__init__(
            message = message,
            error_code = "SERVICE_UNAVAILABLE",
            details = {"service_name": service_name, "reason": reason},
        )


class SymptomExtractionError(InquiryServiceError):
    """症状提取错误"""

    def __init__(self, message: str, text: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "SYMPTOM_EXTRACTION_ERROR",
            details = {"text": text} if text else {},
        )


class TCMPatternMappingError(InquiryServiceError):
    """中医证型映射错误"""

    def __init__(self, message: str, symptoms: list | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "TCM_PATTERN_MAPPING_ERROR",
            details = {"symptoms": symptoms} if symptoms else {},
        )


class HealthRiskAssessmentError(InquiryServiceError):
    """健康风险评估错误"""

    def __init__(
        self, message: str, assessment_data: dict[str, Any] | None = None
    )-> None:
        super().__init__(
            message = message,
            error_code = "HEALTH_RISK_ASSESSMENT_ERROR",
            details = {"assessment_data": assessment_data} if assessment_data else {},
        )


class KnowledgeBaseError(InquiryServiceError):
    """知识库错误"""

    def __init__(self, message: str, operation: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "KNOWLEDGE_BASE_ERROR",
            details = {"operation": operation} if operation else {},
        )


class DialogueError(InquiryServiceError):
    """对话管理错误"""

    def __init__(self, message: str, session_id: str | None = None)-> None:
        """TODO: 添加文档字符串"""
        super().__init__(
            message = message,
            error_code = "DIALOGUE_ERROR",
            details = {"session_id": session_id} if session_id else {},
        )


class ExternalServiceError(InquiryServiceError):
    """外部服务调用错误"""

    def __init__(
        self,
        service_name: str,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    )-> None:
        super().__init__(
            message = f"External service '{service_name}' error: {message}",
            error_code = "EXTERNAL_SERVICE_ERROR",
            details = {
                "service_name": service_name,
                "status_code": status_code,
                "response_data": response_data,
            },
        )
