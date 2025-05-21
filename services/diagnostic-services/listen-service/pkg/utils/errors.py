"""
错误处理模块，定义各种服务错误类型和处理函数
"""
import grpc
import logging
from enum import Enum
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

class ErrorCode(Enum):
    """错误代码枚举"""
    UNKNOWN = 0
    INVALID_REQUEST = 1
    DATABASE_ERROR = 2
    CACHE_ERROR = 3
    MODEL_ERROR = 4
    INTEGRATION_ERROR = 5
    RESOURCE_EXHAUSTED = 6
    AUDIO_PROCESSING_ERROR = 7
    NOT_FOUND = 8
    PERMISSION_DENIED = 9
    AUTHENTICATION_ERROR = 10
    TIMEOUT_ERROR = 11
    INTERNAL_ERROR = 12

class ListenServiceError(Exception):
    """闻诊服务基础错误类"""
    
    def __init__(
        self, 
        message: str, 
        code: ErrorCode = ErrorCode.UNKNOWN,
        details: Optional[Dict[str, Any]] = None,
        grpc_status_code: grpc.StatusCode = grpc.StatusCode.UNKNOWN,
        cause: Optional[Exception] = None
    ):
        """
        初始化错误
        
        参数:
            message: 错误消息
            code: 错误代码
            details: 详细错误信息
            grpc_status_code: gRPC状态代码
            cause: 原始异常
        """
        self.message = message
        self.code = code
        self.details = details or {}
        self.grpc_status_code = grpc_status_code
        self.cause = cause
        
        # 格式化错误消息
        error_msg = f"[{code.name}] {message}"
        if details:
            error_msg += f" - 详情: {details}"
        if cause:
            error_msg += f" - 原因: {str(cause)}"
        
        super().__init__(error_msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """将错误转换为字典"""
        return {
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
            "details": self.details,
            "grpc_status": self.grpc_status_code.name
        }
    
    def to_grpc_error(self) -> grpc.RpcError:
        """将错误转换为gRPC错误"""
        context = grpc.ServicerContext()
        context.set_code(self.grpc_status_code)
        context.set_details(self.message)
        
        # 在元数据中添加更多信息
        metadata = [
            ('error-code', str(self.code.value)),
            ('error-code-name', self.code.name),
        ]
        
        # 添加错误详情
        for key, value in self.details.items():
            if isinstance(value, (str, int, float, bool)):
                metadata.append((f'error-detail-{key}', str(value)))
        
        context.set_trailing_metadata(metadata)
        return context.abort(self.grpc_status_code, self.message)


class InvalidRequestError(ListenServiceError):
    """请求参数无效错误"""
    
    def __init__(
        self, 
        message: str = "请求参数无效", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INVALID_REQUEST,
            details=details,
            grpc_status_code=grpc.StatusCode.INVALID_ARGUMENT,
            cause=cause
        )


class DatabaseError(ListenServiceError):
    """数据库错误"""
    
    def __init__(
        self, 
        message: str = "数据库操作错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.DATABASE_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.INTERNAL,
            cause=cause
        )


class CacheError(ListenServiceError):
    """缓存错误"""
    
    def __init__(
        self, 
        message: str = "缓存操作错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.CACHE_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.INTERNAL,
            cause=cause
        )


class ModelError(ListenServiceError):
    """模型错误"""
    
    def __init__(
        self, 
        message: str = "模型处理错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.MODEL_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.INTERNAL,
            cause=cause
        )


class IntegrationError(ListenServiceError):
    """服务集成错误"""
    
    def __init__(
        self, 
        message: str = "服务集成错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None,
        service_name: Optional[str] = None
    ):
        details = details or {}
        if service_name:
            details["service_name"] = service_name
            
        super().__init__(
            message=message,
            code=ErrorCode.INTEGRATION_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.UNAVAILABLE,
            cause=cause
        )


class ResourceExhaustedError(ListenServiceError):
    """资源耗尽错误"""
    
    def __init__(
        self, 
        message: str = "资源耗尽", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_EXHAUSTED,
            details=details,
            grpc_status_code=grpc.StatusCode.RESOURCE_EXHAUSTED,
            cause=cause
        )


class AudioProcessingError(ListenServiceError):
    """音频处理错误"""
    
    def __init__(
        self, 
        message: str = "音频处理错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.AUDIO_PROCESSING_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.INTERNAL,
            cause=cause
        )


class NotFoundError(ListenServiceError):
    """资源未找到错误"""
    
    def __init__(
        self, 
        message: str = "资源未找到", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        details = details or {}
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
            
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND,
            details=details,
            grpc_status_code=grpc.StatusCode.NOT_FOUND,
            cause=cause
        )


class PermissionDeniedError(ListenServiceError):
    """权限拒绝错误"""
    
    def __init__(
        self, 
        message: str = "权限不足", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            details=details,
            grpc_status_code=grpc.StatusCode.PERMISSION_DENIED,
            cause=cause
        )


class AuthenticationError(ListenServiceError):
    """认证错误"""
    
    def __init__(
        self, 
        message: str = "认证失败", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHENTICATION_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.UNAUTHENTICATED,
            cause=cause
        )


class TimeoutError(ListenServiceError):
    """超时错误"""
    
    def __init__(
        self, 
        message: str = "操作超时", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.TIMEOUT_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.DEADLINE_EXCEEDED,
            cause=cause
        )


class InternalError(ListenServiceError):
    """内部服务错误"""
    
    def __init__(
        self, 
        message: str = "内部服务错误", 
        details: Optional[Dict[str, Any]] = None, 
        cause: Optional[Exception] = None
    ):
        super().__init__(
            message=message,
            code=ErrorCode.INTERNAL_ERROR,
            details=details,
            grpc_status_code=grpc.StatusCode.INTERNAL,
            cause=cause
        )


def handle_error(func):
    """
    装饰器：处理函数执行期间的异常
    
    使用方式:
        @handle_error
        def my_function():
            # 代码
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ListenServiceError as e:
            # 已经是我们定义的错误类型，直接记录日志并抛出
            logger.error(f"服务错误: {str(e)}", exc_info=True)
            raise e
        except grpc.RpcError as e:
            # gRPC错误，转换为我们的错误类型
            logger.error(f"gRPC错误: {str(e)}", exc_info=True)
            raise IntegrationError(
                message=f"gRPC调用错误: {e.details() if hasattr(e, 'details') else str(e)}",
                details={"grpc_code": e.code().name if hasattr(e, 'code') else "UNKNOWN"},
                cause=e
            )
        except Exception as e:
            # 其他未知错误，转换为内部错误
            logger.error(f"未捕获的异常: {str(e)}", exc_info=True)
            raise InternalError(
                message=f"服务内部错误: {str(e)}",
                cause=e
            )
    
    return wrapper


def handle_grpc_errors(servicer_method):
    """
    装饰器：处理gRPC服务方法中的异常，转换为适当的gRPC错误
    
    使用方式:
        @handle_grpc_errors
        def MyServiceMethod(self, request, context):
            # 代码
    """
    def wrapper(self, request, context):
        try:
            return servicer_method(self, request, context)
        except ListenServiceError as e:
            # 记录错误日志
            logger.error(f"服务错误: {str(e)}", exc_info=True)
            
            # 设置gRPC错误状态和详情
            context.set_code(e.grpc_status_code)
            context.set_details(e.message)
            
            # 在元数据中添加更多信息
            metadata = [
                ('error-code', str(e.code.value)),
                ('error-code-name', e.code.name),
            ]
            
            # 添加错误详情
            for key, value in e.details.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata.append((f'error-detail-{key}', str(value)))
            
            context.set_trailing_metadata(metadata)
            
            # 在监控系统中记录错误
            # metrics.increment_counter('grpc_errors', {'code': e.code.name})
            
            return None
        except Exception as e:
            # 记录未捕获的异常
            logger.error(f"未捕获的异常: {str(e)}", exc_info=True)
            
            # 转换为gRPC内部错误
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务内部错误: {str(e)}")
            
            # 在监控系统中记录错误
            # metrics.increment_counter('grpc_errors', {'code': 'INTERNAL'})
            
            return None
    
    return wrapper 