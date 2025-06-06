"""
error_handler - 索克生活项目模块
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Type, Union
import logging
import traceback

"""增强的错误处理模块"""




class ErrorCode(str, Enum):
    """错误代码枚举"""
    
    # 通用错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMITED = "RATE_LIMITED"
    
    # 基准测试相关错误
    BENCHMARK_NOT_FOUND = "BENCHMARK_NOT_FOUND"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INVALID_BENCHMARK_CONFIG = "INVALID_BENCHMARK_CONFIG"
    BENCHMARK_EXECUTION_FAILED = "BENCHMARK_EXECUTION_FAILED"
    
    # 模型相关错误
    MODEL_LOAD_FAILED = "MODEL_LOAD_FAILED"
    MODEL_PREDICTION_FAILED = "MODEL_PREDICTION_FAILED"
    MODEL_REGISTRATION_FAILED = "MODEL_REGISTRATION_FAILED"
    
    # 数据相关错误
    INVALID_DATA_FORMAT = "INVALID_DATA_FORMAT"
    DATA_PROCESSING_FAILED = "DATA_PROCESSING_FAILED"
    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    
    # 缓存相关错误
    CACHE_ERROR = "CACHE_ERROR"
    CACHE_FULL = "CACHE_FULL"
    
    # 资源相关错误
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"
    TIMEOUT = "TIMEOUT"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"


@dataclass
class ErrorDetail:
    """错误详情"""
    
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "request_id": self.request_id,
            "user_id": self.user_id
        }


class SuokeBenchException(Exception):
    """SuokeBench 基础异常类"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.cause = cause
        super().__init__(message)
    
    def to_error_detail(self) -> ErrorDetail:
        """转换为错误详情"""
        return ErrorDetail(
            code=self.error_code,
            message=self.message,
            details=self.details
        )


class BenchmarkException(SuokeBenchException):
    """基准测试异常"""
    pass


class ModelException(SuokeBenchException):
    """模型异常"""
    pass


class DataException(SuokeBenchException):
    """数据异常"""
    pass


class CacheException(SuokeBenchException):
    """缓存异常"""
    pass


class ResourceException(SuokeBenchException):
    """资源异常"""
    pass


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error_stats = {}
    
    def handle_exception(
        self,
        exception: Exception,
        request: Optional[Request] = None
    ) -> JSONResponse:
        """处理异常并返回适当的响应"""
        
        # 记录错误统计
        error_type = type(exception).__name__
        self._error_stats[error_type] = self._error_stats.get(error_type, 0) + 1
        
        # 获取请求ID
        request_id = None
        if request:
            request_id = getattr(request.state, 'request_id', None)
        
        # 处理不同类型的异常
        if isinstance(exception, SuokeBenchException):
            return self._handle_suokebench_exception(exception, request_id)
        elif isinstance(exception, HTTPException):
            return self._handle_http_exception(exception, request_id)
        elif isinstance(exception, ValueError):
            return self._handle_validation_exception(exception, request_id)
        elif isinstance(exception, TimeoutError):
            return self._handle_timeout_exception(exception, request_id)
        else:
            return self._handle_generic_exception(exception, request_id)
    
    def _handle_suokebench_exception(
        self,
        exception: SuokeBenchException,
        request_id: Optional[str]
    ) -> JSONResponse:
        """处理 SuokeBench 异常"""
        
        error_detail = exception.to_error_detail()
        error_detail.request_id = request_id
        
        # 记录错误日志
        self.logger.error(
            f"SuokeBench异常: {exception.error_code.value} - {exception.message}",
            extra={
                "error_code": exception.error_code.value,
                "details": exception.details,
                "request_id": request_id,
                "cause": str(exception.cause) if exception.cause else None
            }
        )
        
        # 确定HTTP状态码
        status_code = self._get_http_status_code(exception.error_code)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": error_detail.to_dict(),
                "success": False
            }
        )
    
    def _handle_http_exception(
        self,
        exception: HTTPException,
        request_id: Optional[str]
    ) -> JSONResponse:
        """处理 HTTP 异常"""
        
        error_detail = ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message=exception.detail,
            request_id=request_id
        )
        
        self.logger.warning(
            f"HTTP异常: {exception.status_code} - {exception.detail}",
            extra={"request_id": request_id}
        )
        
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "error": error_detail.to_dict(),
                "success": False
            }
        )
    
    def _handle_validation_exception(
        self,
        exception: ValueError,
        request_id: Optional[str]
    ) -> JSONResponse:
        """处理验证异常"""
        
        error_detail = ErrorDetail(
            code=ErrorCode.VALIDATION_ERROR,
            message=f"数据验证失败: {str(exception)}",
            request_id=request_id
        )
        
        self.logger.warning(
            f"验证异常: {str(exception)}",
            extra={"request_id": request_id}
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": error_detail.to_dict(),
                "success": False
            }
        )
    
    def _handle_timeout_exception(
        self,
        exception: TimeoutError,
        request_id: Optional[str]
    ) -> JSONResponse:
        """处理超时异常"""
        
        error_detail = ErrorDetail(
            code=ErrorCode.TIMEOUT,
            message=f"操作超时: {str(exception)}",
            request_id=request_id
        )
        
        self.logger.error(
            f"超时异常: {str(exception)}",
            extra={"request_id": request_id}
        )
        
        return JSONResponse(
            status_code=408,
            content={
                "error": error_detail.to_dict(),
                "success": False
            }
        )
    
    def _handle_generic_exception(
        self,
        exception: Exception,
        request_id: Optional[str]
    ) -> JSONResponse:
        """处理通用异常"""
        
        error_detail = ErrorDetail(
            code=ErrorCode.INTERNAL_ERROR,
            message="内部服务器错误",
            details={
                "exception_type": type(exception).__name__,
                "exception_message": str(exception)
            },
            request_id=request_id
        )
        
        # 记录完整的错误堆栈
        self.logger.error(
            f"未处理的异常: {type(exception).__name__} - {str(exception)}",
            extra={
                "request_id": request_id,
                "traceback": traceback.format_exc()
            }
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": error_detail.to_dict(),
                "success": False
            }
        )
    
    def _get_http_status_code(self, error_code: ErrorCode) -> int:
        """根据错误代码获取HTTP状态码"""
        
        status_mapping = {
            ErrorCode.NOT_FOUND: 404,
            ErrorCode.BENCHMARK_NOT_FOUND: 404,
            ErrorCode.MODEL_NOT_FOUND: 404,
            ErrorCode.TASK_NOT_FOUND: 404,
            ErrorCode.DATASET_NOT_FOUND: 404,
            
            ErrorCode.VALIDATION_ERROR: 422,
            ErrorCode.INVALID_BENCHMARK_CONFIG: 422,
            ErrorCode.INVALID_DATA_FORMAT: 422,
            
            ErrorCode.UNAUTHORIZED: 401,
            ErrorCode.FORBIDDEN: 403,
            ErrorCode.RATE_LIMITED: 429,
            ErrorCode.QUOTA_EXCEEDED: 429,
            
            ErrorCode.TIMEOUT: 408,
            ErrorCode.RESOURCE_EXHAUSTED: 503,
            ErrorCode.CACHE_FULL: 503,
        }
        
        return status_mapping.get(error_code, 500)
    
    def get_error_stats(self) -> Dict[str, int]:
        """获取错误统计"""
        return self._error_stats.copy()
    
    def reset_error_stats(self):
        """重置错误统计"""
        self._error_stats.clear()


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def create_benchmark_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None
) -> BenchmarkException:
    """创建基准测试异常"""
    return BenchmarkException(
        error_code=ErrorCode.BENCHMARK_EXECUTION_FAILED,
        message=message,
        details=details,
        cause=cause
    )


def create_model_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None
) -> ModelException:
    """创建模型异常"""
    return ModelException(
        error_code=ErrorCode.MODEL_LOAD_FAILED,
        message=message,
        details=details,
        cause=cause
    )


def create_data_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None
) -> DataException:
    """创建数据异常"""
    return DataException(
        error_code=ErrorCode.DATA_PROCESSING_FAILED,
        message=message,
        details=details,
        cause=cause
    )


def create_cache_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None
) -> CacheException:
    """创建缓存异常"""
    return CacheException(
        error_code=ErrorCode.CACHE_ERROR,
        message=message,
        details=details,
        cause=cause
    )


def create_resource_exception(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    cause: Optional[Exception] = None
) -> ResourceException:
    """创建资源异常"""
    return ResourceException(
        error_code=ErrorCode.RESOURCE_EXHAUSTED,
        message=message,
        details=details,
        cause=cause
    )


# 装饰器：自动错误处理
def handle_errors(func):
    """自动错误处理装饰器"""
    
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return global_error_handler.handle_exception(e)
    
    return wrapper


# 异步装饰器：自动错误处理
def handle_errors_async(func):
    """异步自动错误处理装饰器"""
    
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return global_error_handler.handle_exception(e)
    
    return wrapper 