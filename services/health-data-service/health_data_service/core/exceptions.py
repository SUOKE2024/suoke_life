"""
exceptions - 索克生活项目模块
"""

from typing import Optional, Dict, Any

#!/usr/bin/env python3
"""
异常处理模块

定义健康数据服务的自定义异常类。
"""



class HealthDataServiceException(Exception):
    """健康数据服务基础异常"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ValidationError(HealthDataServiceException):
    """数据验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.field = field
        self.value = value
        details = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, "VALIDATION_ERROR", details)


class DatabaseError(HealthDataServiceException):
    """数据库操作错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        self.operation = operation
        self.table = table
        details = {}
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        super().__init__(message, "DATABASE_ERROR", details)


class NotFoundError(HealthDataServiceException):
    """资源不存在错误"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[Any] = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id is not None:
            details["resource_id"] = resource_id
        super().__init__(message, "NOT_FOUND", details)


class AuthenticationError(HealthDataServiceException):
    """认证错误"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(HealthDataServiceException):
    """授权错误"""
    
    def __init__(self, message: str = "权限不足", required_permission: Optional[str] = None):
        self.required_permission = required_permission
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ConfigurationError(HealthDataServiceException):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.config_key = config_key
        details = {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", details)


class ExternalServiceError(HealthDataServiceException):
    """外部服务错误"""
    
    def __init__(self, message: str, service_name: Optional[str] = None, status_code: Optional[int] = None):
        self.service_name = service_name
        self.status_code = status_code
        details = {}
        if service_name:
            details["service_name"] = service_name
        if status_code:
            details["status_code"] = status_code
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)


class DataProcessingError(HealthDataServiceException):
    """数据处理错误"""
    
    def __init__(self, message: str, processing_stage: Optional[str] = None, data_type: Optional[str] = None):
        self.processing_stage = processing_stage
        self.data_type = data_type
        details = {}
        if processing_stage:
            details["processing_stage"] = processing_stage
        if data_type:
            details["data_type"] = data_type
        super().__init__(message, "DATA_PROCESSING_ERROR", details)


class SecurityError(HealthDataServiceException):
    """安全错误"""
    
    def __init__(self, message: str, security_type: Optional[str] = None):
        self.security_type = security_type
        details = {}
        if security_type:
            details["security_type"] = security_type
        super().__init__(message, "SECURITY_ERROR", details)


class RateLimitError(HealthDataServiceException):
    """频率限制错误"""
    
    def __init__(self, message: str = "请求频率过高", limit: Optional[int] = None, window: Optional[int] = None):
        self.limit = limit
        self.window = window
        details = {}
        if limit:
            details["limit"] = limit
        if window:
            details["window"] = window
        super().__init__(message, "RATE_LIMIT_ERROR", details)


class BusinessLogicError(HealthDataServiceException):
    """业务逻辑错误"""
    
    def __init__(self, message: str, business_rule: Optional[str] = None):
        self.business_rule = business_rule
        details = {}
        if business_rule:
            details["business_rule"] = business_rule
        super().__init__(message, "BUSINESS_LOGIC_ERROR", details)


class DataQualityError(HealthDataServiceException):
    """数据质量错误"""
    
    def __init__(self, message: str, quality_issue: Optional[str] = None, quality_score: Optional[float] = None):
        self.quality_issue = quality_issue
        self.quality_score = quality_score
        details = {}
        if quality_issue:
            details["quality_issue"] = quality_issue
        if quality_score is not None:
            details["quality_score"] = quality_score
        super().__init__(message, "DATA_QUALITY_ERROR", details)


class ConcurrencyError(HealthDataServiceException):
    """并发错误"""
    
    def __init__(self, message: str = "并发操作冲突", resource_id: Optional[Any] = None):
        self.resource_id = resource_id
        details = {}
        if resource_id is not None:
            details["resource_id"] = resource_id
        super().__init__(message, "CONCURRENCY_ERROR", details)


class TimeoutError(HealthDataServiceException):
    """超时错误"""
    
    def __init__(self, message: str = "操作超时", timeout_seconds: Optional[float] = None):
        self.timeout_seconds = timeout_seconds
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        super().__init__(message, "TIMEOUT_ERROR", details)


# 便捷函数
def raise_validation_error(message: str, field: Optional[str] = None, value: Optional[Any] = None) -> None:
    """抛出验证错误"""
    raise ValidationError(message, field, value)


def raise_not_found_error(resource_type: str, resource_id: Any) -> None:
    """抛出资源不存在错误"""
    raise NotFoundError(f"{resource_type} 不存在: {resource_id}", resource_type, resource_id)


def raise_database_error(message: str, operation: Optional[str] = None, table: Optional[str] = None) -> None:
    """抛出数据库错误"""
    raise DatabaseError(message, operation, table)


def raise_authorization_error(message: str = "权限不足", required_permission: Optional[str] = None) -> None:
    """抛出授权错误"""
    raise AuthorizationError(message, required_permission)


def raise_data_quality_error(message: str, quality_issue: Optional[str] = None, quality_score: Optional[float] = None) -> None:
    """抛出数据质量错误"""
    raise DataQualityError(message, quality_issue, quality_score)
