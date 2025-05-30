"""
错误处理中间件

统一处理应用异常
"""

import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..exceptions import CalculationError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """错误处理中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """统一异常处理"""
        try:
            response = await call_next(request)
            return response
            
        except CalculationError as e:
            # 处理算诊相关异常
            logger.warning(f"算诊异常: {e.message} (错误码: {e.error_code})")
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": e.error_code,
                    "message": e.message,
                    "type": "calculation_error"
                }
            )
            
        except ValueError as e:
            # 处理值错误
            logger.warning(f"参数错误: {str(e)}")
            
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_PARAMETER",
                    "message": f"参数错误: {str(e)}",
                    "type": "validation_error"
                }
            )
            
        except Exception as e:
            # 处理其他未知异常
            logger.error(f"未知异常: {str(e)}", exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error_code": "INTERNAL_ERROR",
                    "message": "服务内部错误，请稍后重试",
                    "type": "internal_error"
                }
            ) 