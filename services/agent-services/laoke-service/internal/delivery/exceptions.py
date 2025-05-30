#!/usr/bin/env python

"""
老克智能体服务 - 异常处理模块
提供统一的异常类型和处理机制
"""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)

# 基础异常类
class LaokeServiceException(Exception):
    """老克服务基础异常类"""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None,
                status_code: int = 400):
        """
        初始化异常

        Args:
            code: 错误码
            message: 错误消息
            details: 错误详情
            status_code: HTTP状态码
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)

# 常见业务异常
class ResourceNotFoundException(LaokeServiceException):
    """资源未找到异常"""

    def __init__(self, resource_type: str, resource_id: str):
        """
        初始化资源未找到异常

        Args:
            resource_type: 资源类型
            resource_id: 资源ID
        """
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource_type}未找到: {resource_id}",
            details={"resource_type": resource_type, "resource_id": resource_id},
            status_code=404
        )

class ValidationException(LaokeServiceException):
    """数据验证异常"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """
        初始化数据验证异常

        Args:
            message: 错误消息
            details: 错误详情
        """
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=400
        )

class AuthenticationException(LaokeServiceException):
    """认证异常"""

    def __init__(self, message: str = "认证失败"):
        """
        初始化认证异常

        Args:
            message: 错误消息
        """
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=401
        )

class AuthorizationException(LaokeServiceException):
    """授权异常"""

    def __init__(self, message: str = "权限不足", resource: str | None = None):
        """
        初始化授权异常

        Args:
            message: 错误消息
            resource: 请求资源
        """
        details = {"resource": resource} if resource else {}
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            details=details,
            status_code=403
        )

class RateLimitException(LaokeServiceException):
    """速率限制异常"""

    def __init__(self, message: str = "请求过于频繁，请稍后再试", retry_after: int | None = None):
        """
        初始化速率限制异常

        Args:
            message: 错误消息
            retry_after: 建议重试时间（秒）
        """
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            details=details,
            status_code=429
        )

class ServiceUnavailableException(LaokeServiceException):
    """服务不可用异常"""

    def __init__(self, message: str = "服务暂时不可用，请稍后再试"):
        """
        初始化服务不可用异常

        Args:
            message: 错误消息
        """
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=503
        )

class DatabaseException(LaokeServiceException):
    """数据库异常"""

    def __init__(self, message: str, operation: str | None = None):
        """
        初始化数据库异常

        Args:
            message: 错误消息
            operation: 数据库操作
        """
        details = {"operation": operation} if operation else {}
        super().__init__(
            code="DATABASE_ERROR",
            message=message,
            details=details,
            status_code=500
        )

class ExternalServiceException(LaokeServiceException):
    """外部服务异常"""

    def __init__(self, service_name: str, message: str, status_code: int | None = None):
        """
        初始化外部服务异常

        Args:
            service_name: 服务名称
            message: 错误消息
            status_code: HTTP状态码
        """
        details = {
            "service_name": service_name,
            "status_code": status_code
        }
        super().__init__(
            code="EXTERNAL_SERVICE_ERROR",
            message=f"{service_name}: {message}",
            details=details,
            status_code=502
        )

# 异常处理器
async def exception_handler(request: Request, exc: LaokeServiceException) -> JSONResponse:
    """
    处理自定义异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSONResponse: 错误响应
    """
    logger.error(
        "API异常: %s - %s - %s - %s",
        exc.code,
        exc.message,
        exc.details,
        request.url.path
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    处理HTTP异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSONResponse: 错误响应
    """
    logger.error(
        "HTTP异常: %s - %s - %s",
        exc.status_code,
        exc.detail,
        request.url.path
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "path": request.url.path
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求验证异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSONResponse: 错误响应
    """
    # 格式化验证错误
    errors = []
    for error in exc.errors():
        loc = " -> ".join([str(location) for location in error.get("loc", [])])
        errors.append({
            "location": loc,
            "message": error.get("msg"),
            "type": error.get("type")
        })

    logger.error(
        "请求验证异常: %s - %s",
        request.url.path,
        errors
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": {"errors": errors},
            "path": request.url.path
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理通用异常

    Args:
        request: 请求对象
        exc: 异常对象

    Returns:
        JSONResponse: 错误响应
    """
    logger.exception(
        "未处理的服务器异常: %s - %s - %s",
        type(exc).__name__,
        str(exc),
        request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "path": request.url.path
        }
    )

def register_exception_handlers(app):
    """
    注册异常处理器

    Args:
        app: FastAPI应用实例
    """
    # 注册自定义异常处理器
    app.add_exception_handler(LaokeServiceException, exception_handler)

    # 注册HTTP异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)

    # 注册验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # 注册通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)
