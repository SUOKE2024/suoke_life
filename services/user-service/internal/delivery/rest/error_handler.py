"""
REST API错误处理器
提供统一的错误处理和响应格式
"""
import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from pkg.errors.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError,
    UserInactiveError, UserSuspendedError, ValidationError,
    DeviceNotFoundError, DeviceAlreadyBoundError, DeviceLimitExceededError,
    HealthDataNotFoundError, AuthorizationError, DatabaseError
)

logger = logging.getLogger(__name__)

class ErrorResponse:
    """标准错误响应格式"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        request_id: Optional[str] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp or datetime.utcnow()
        self.request_id = request_id
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "timestamp": self.timestamp.isoformat(),
            }
        }
        
        if self.details:
            result["error"]["details"] = self.details
        
        if self.request_id:
            result["error"]["request_id"] = self.request_id
        
        return result

def get_request_id(request: Request) -> Optional[str]:
    """从请求中获取请求ID"""
    return getattr(request.state, 'request_id', None)

def create_error_response(
    request: Request,
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """创建标准错误响应"""
    request_id = get_request_id(request)
    
    error_response = ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )

def add_error_handlers(app: FastAPI):
    """添加错误处理器到FastAPI应用"""
    
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        """用户不存在错误处理"""
        logger.warning(f"用户不存在: {exc}")
        return create_error_response(
            request=request,
            error_code="USER_NOT_FOUND",
            message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
        """用户已存在错误处理"""
        logger.warning(f"用户已存在: {exc}")
        return create_error_response(
            request=request,
            error_code="USER_ALREADY_EXISTS",
            message=str(exc),
            status_code=status.HTTP_409_CONFLICT
        )
    
    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
        """无效凭据错误处理"""
        logger.warning(f"无效凭据: {exc}")
        return create_error_response(
            request=request,
            error_code="INVALID_CREDENTIALS",
            message="用户名或密码错误",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @app.exception_handler(UserInactiveError)
    async def user_inactive_handler(request: Request, exc: UserInactiveError):
        """用户未激活错误处理"""
        logger.warning(f"用户未激活: {exc}")
        return create_error_response(
            request=request,
            error_code="USER_INACTIVE",
            message="用户账户未激活",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @app.exception_handler(UserSuspendedError)
    async def user_suspended_handler(request: Request, exc: UserSuspendedError):
        """用户被暂停错误处理"""
        logger.warning(f"用户被暂停: {exc}")
        return create_error_response(
            request=request,
            error_code="USER_SUSPENDED",
            message="用户账户已被暂停",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @app.exception_handler(AuthorizationError)
    async def authorization_handler(request: Request, exc: AuthorizationError):
        """授权错误处理"""
        logger.warning(f"授权失败: {exc}")
        return create_error_response(
            request=request,
            error_code="AUTHORIZATION_ERROR",
            message=str(exc),
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """数据验证错误处理"""
        logger.warning(f"数据验证失败: {exc}")
        return create_error_response(
            request=request,
            error_code="VALIDATION_ERROR",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST,
            details=getattr(exc, 'details', None)
        )
    
    @app.exception_handler(DeviceNotFoundError)
    async def device_not_found_handler(request: Request, exc: DeviceNotFoundError):
        """设备不存在错误处理"""
        logger.warning(f"设备不存在: {exc}")
        return create_error_response(
            request=request,
            error_code="DEVICE_NOT_FOUND",
            message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @app.exception_handler(DeviceAlreadyBoundError)
    async def device_already_bound_handler(request: Request, exc: DeviceAlreadyBoundError):
        """设备已绑定错误处理"""
        logger.warning(f"设备已绑定: {exc}")
        return create_error_response(
            request=request,
            error_code="DEVICE_ALREADY_BOUND",
            message=str(exc),
            status_code=status.HTTP_409_CONFLICT
        )
    
    @app.exception_handler(DeviceLimitExceededError)
    async def device_limit_exceeded_handler(request: Request, exc: DeviceLimitExceededError):
        """设备数量超限错误处理"""
        logger.warning(f"设备数量超限: {exc}")
        return create_error_response(
            request=request,
            error_code="DEVICE_LIMIT_EXCEEDED",
            message=str(exc),
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @app.exception_handler(HealthDataNotFoundError)
    async def health_data_not_found_handler(request: Request, exc: HealthDataNotFoundError):
        """健康数据不存在错误处理"""
        logger.warning(f"健康数据不存在: {exc}")
        return create_error_response(
            request=request,
            error_code="HEALTH_DATA_NOT_FOUND",
            message=str(exc),
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        """数据库错误处理"""
        logger.error(f"数据库错误: {exc}")
        return create_error_response(
            request=request,
            error_code="DATABASE_ERROR",
            message="数据库操作失败",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求验证错误处理"""
        logger.warning(f"请求验证失败: {exc}")
        
        # 格式化验证错误详情
        details = []
        for error in exc.errors():
            details.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        return create_error_response(
            request=request,
            error_code="VALIDATION_ERROR",
            message="请求数据验证失败",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": details}
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """HTTP异常处理"""
        logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
        
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "UNPROCESSABLE_ENTITY",
            429: "TOO_MANY_REQUESTS",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE",
            504: "GATEWAY_TIMEOUT"
        }
        
        error_code = error_codes.get(exc.status_code, "HTTP_ERROR")
        
        return create_error_response(
            request=request,
            error_code=error_code,
            message=exc.detail,
            status_code=exc.status_code
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """通用异常处理"""
        request_id = get_request_id(request)
        
        logger.error(
            f"未处理的异常 (request_id: {request_id}): {exc}",
            exc_info=True
        )
        
        # 在开发环境中返回详细错误信息
        import os
        if os.getenv("ENVIRONMENT", "production") == "development":
            details = {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        else:
            details = None
        
        return create_error_response(
            request=request,
            error_code="INTERNAL_SERVER_ERROR",
            message="服务器内部错误",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        ) 