"""
error_handler - 索克生活项目模块
"""

import logging
import traceback
from collections.abc import Callable

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from ..exceptions import CalculationError

"""
错误处理中间件

统一处理应用异常
"""


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""

    def __init__(self, app, debug: bool = False):
        """
        初始化错误处理中间件

        Args:
            app: FastAPI应用实例
            debug: 是否启用调试模式
        """
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并捕获异常"""
        try:
            response = await call_next(request)
            return response

        except HTTPException as e:
            # FastAPI HTTP异常，直接返回
            return await self._handle_http_exception(request, e)

        except ValueError as e:
            # 值错误，通常是输入参数问题
            return await self._handle_value_error(request, e)

        except KeyError as e:
            # 键错误，通常是缺少必要参数
            return await self._handle_key_error(request, e)

        except TypeError as e:
            # 类型错误，通常是参数类型不匹配
            return await self._handle_type_error(request, e)

        except Exception as e:
            # 其他未预期的异常
            return await self._handle_general_exception(request, e)

    async def _handle_http_exception(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:
        """处理HTTP异常"""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"HTTP异常: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "http_exception",
                },
                "request_id": request_id,
                "path": request.url.path,
            },
        )

    async def _handle_value_error(
        self, request: Request, exc: ValueError
    ) -> JSONResponse:
        """处理值错误"""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"参数值错误: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": "ValueError",
            },
        )

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": 400,
                    "message": f"参数值错误: {str(exc)}",
                    "type": "value_error",
                },
                "request_id": request_id,
                "path": request.url.path,
            },
        )

    async def _handle_key_error(self, request: Request, exc: KeyError) -> JSONResponse:
        """处理键错误"""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"缺少必要参数: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": "KeyError",
            },
        )

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": 400,
                    "message": f"缺少必要参数: {str(exc)}",
                    "type": "key_error",
                },
                "request_id": request_id,
                "path": request.url.path,
            },
        )

    async def _handle_type_error(
        self, request: Request, exc: TypeError
    ) -> JSONResponse:
        """处理类型错误"""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"参数类型错误: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": "TypeError",
            },
        )

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": 400,
                    "message": f"参数类型错误: {str(exc)}",
                    "type": "type_error",
                },
                "request_id": request_id,
                "path": request.url.path,
            },
        )

    async def _handle_general_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """处理一般异常"""
        request_id = getattr(request.state, "request_id", "unknown")

        # 记录详细错误信息
        logger.error(
            f"服务器内部错误: {type(exc).__name__}: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__,
                "traceback": traceback.format_exc() if self.debug else None,
            },
            exc_info=True,
        )

        # 构建错误响应
        error_content = {
            "success": False,
            "error": {
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "服务器内部错误，请稍后重试",
                "type": "internal_server_error",
            },
            "request_id": request_id,
            "path": request.url.path,
        }

        # 在调试模式下包含详细错误信息
        if self.debug:
            error_content["error"]["debug_info"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "traceback": traceback.format_exc(),
            }

        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=error_content
        )


# CalculationError 已在 exceptions 模块中定义，这里移除重复定义


class ZiwuCalculationError(CalculationError):
    """子午流注计算错误"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "ZIWU_CALCULATION_ERROR", details)


class ConstitutionCalculationError(CalculationError):
    """体质分析计算错误"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONSTITUTION_CALCULATION_ERROR", details)


class BaguaCalculationError(CalculationError):
    """八卦分析计算错误"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "BAGUA_CALCULATION_ERROR", details)


class WuyunLiuqiCalculationError(CalculationError):
    """五运六气计算错误"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "WUYUN_LIUQI_CALCULATION_ERROR", details)


class DataValidationError(CalculationError):
    """数据验证错误"""

    def __init__(self, message: str, field: str = None, details: dict = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "DATA_VALIDATION_ERROR", error_details)


class CacheError(Exception):
    """缓存操作错误"""

    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        super().__init__(self.message)


def create_error_response(
    error: Exception, status_code: int = 500, request_id: str = None, path: str = None
) -> JSONResponse:
    """
    创建标准化错误响应

    Args:
        error: 异常对象
        status_code: HTTP状态码
        request_id: 请求ID
        path: 请求路径

    Returns:
        JSONResponse: 标准化错误响应
    """
    error_content = {
        "success": False,
        "error": {
            "code": status_code,
            "message": str(error),
            "type": type(error).__name__.lower(),
        },
    }

    if request_id:
        error_content["request_id"] = request_id

    if path:
        error_content["path"] = path

    # 如果是自定义计算错误，添加额外信息
    if isinstance(error, CalculationError):
        error_content["error"]["error_code"] = error.error_code
        if error.details:
            error_content["error"]["details"] = error.details

    return JSONResponse(status_code=status_code, content=error_content)
