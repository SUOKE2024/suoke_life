#!/usr/bin/env python3
"""
异常模块 - 定义服务相关的异常类
"""

from typing import Any


class BaseServiceError(Exception):
    """
    基础服务错误类
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        details: dict[str, Any] | None = None
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

    def __init__(self, message: str, code: str = "INVALID_INPUT", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class AuthenticationError(BaseServiceError):
    """
    认证错误

    当用户认证失败时抛出
    """

    def __init__(self, message: str, code: str = "AUTH_FAILED", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class AuthorizationError(BaseServiceError):
    """
    授权错误

    当用户权限不足时抛出
    """

    def __init__(self, message: str, code: str = "AUTH_DENIED", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ResourceNotFoundError(BaseServiceError):
    """
    资源未找到错误

    当请求的资源不存在时抛出
    """

    def __init__(self, message: str, code: str = "NOT_FOUND", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ResourceExistsError(BaseServiceError):
    """
    资源已存在错误

    当尝试创建已存在的资源时抛出
    """

    def __init__(self, message: str, code: str = "ALREADY_EXISTS", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ProcessingError(BaseServiceError):
    """
    处理错误

    当业务逻辑处理失败时抛出
    """

    def __init__(self, message: str, code: str = "PROCESSING_FAILED", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class DatabaseError(BaseServiceError):
    """
    数据库错误

    当数据库操作失败时抛出
    """

    def __init__(self, message: str, code: str = "DB_ERROR", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ModelError(BaseServiceError):
    """
    模型错误

    当AI模型操作失败时抛出
    """

    def __init__(self, message: str, code: str = "MODEL_ERROR", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ServiceUnavailableError(BaseServiceError):
    """
    服务不可用错误

    当服务暂时不可用时抛出
    """

    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class TimeoutError(BaseServiceError):
    """
    超时错误

    当操作超时时抛出
    """

    def __init__(self, message: str, code: str = "TIMEOUT", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ValidationError(InvalidInputError):
    """
    验证错误

    当数据验证失败时抛出
    """

    def __init__(self, message: str, code: str = "VALIDATION_FAILED", details: dict[str, Any] | None = None):
        super().__init__(message, code, details)


class ExternalServiceError(BaseServiceError):
    """
    外部服务错误

    当调用外部服务失败时抛出
    """

    def __init__(
        self,
        message: str,
        service_name: str,
        code: str = "EXTERNAL_SERVICE_ERROR",
        details: dict[str, Any] | None = None
    ):
        super().__init__(message, code, details)
        self.service_name = service_name
