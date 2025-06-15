"""
异常处理器
"""

import traceback
from typing import Any, Dict, List, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from ..core.logging import get_logger
from .base import (
    DatabaseError,
    ImageProcessingError,
    LookServiceError,
    MLModelError,
    ValidationError,
)

logger = get_logger(__name__)


async def look_service_exception_handler(
    request: Request, exc: LookServiceError
) -> JSONResponse:
    """处理Look Service自定义异常"""
    logger.error(
        "Look Service异常",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
            "path": request.url.path,
        },
    )


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """处理验证异常"""
    logger.warning(
        "验证异常",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
            },
            "path": request.url.path,
        },
    )


async def image_processing_exception_handler(
    request: Request, exc: ImageProcessingError
) -> JSONResponse:
    """处理图像处理异常"""
    logger.error(
        "图像处理异常",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": "IMAGE_PROCESSING_ERROR",
                "message": exc.message,
                "details": exc.details,
            },
            "path": request.url.path,
        },
    )


async def ml_model_exception_handler(
    request: Request, exc: MLModelError
) -> JSONResponse:
    """处理机器学习模型异常"""
    logger.error(
        "机器学习模型异常",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": {
                "code": "ML_MODEL_ERROR",
                "message": "模型服务暂时不可用",
                "details": {"original_error": exc.message},
            },
            "path": request.url.path,
        },
    )


async def database_exception_handler(
    request: Request, exc: DatabaseError
) -> JSONResponse:
    """处理数据库异常"""
    logger.error(
        "数据库异常",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "数据库服务暂时不可用",
                "details": {},
            },
            "path": request.url.path,
        },
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: PydanticValidationError
) -> JSONResponse:
    """处理Pydantic验证异常"""
    logger.warning(
        "Pydantic验证异常",
        errors=exc.errors(),
        path=request.url.path,
    )
    
    # 格式化错误信息
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "请求数据验证失败",
                "details": {"validation_errors": formatted_errors},
            },
            "path": request.url.path,
        },
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """处理通用异常"""
    logger.error(
        "未处理的异常",
        exception_type=type(exc).__name__,
        message=str(exc),
        traceback=traceback.format_exc(),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误",
                "details": {},
            },
            "path": request.url.path,
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    
    # 自定义异常处理器
    app.add_exception_handler(LookServiceError, look_service_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(ImageProcessingError, image_processing_exception_handler)
    app.add_exception_handler(MLModelError, ml_model_exception_handler)
    app.add_exception_handler(DatabaseError, database_exception_handler)
    
    # Pydantic验证异常处理器
    app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
    
    # 通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("异常处理器设置完成")


def main() -> None:
    """主函数 - 用于测试"""
    logger.info("异常处理器模块加载完成")


if __name__ == "__main__":
    main() 