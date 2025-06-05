"""
统一错误处理机制
"""

import logging
import traceback
from typing import Dict, Any, Optional, Type
from enum import Enum
import grpc
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# 错误计数器
error_counter = Counter(
    'message_bus_errors_total',
    'Total number of errors',
    ['error_type', 'component', 'severity']
)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCode(Enum):
    """错误代码"""
    # 通用错误
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    
    # 消息相关错误
    MESSAGE_PUBLISH_FAILED = "MESSAGE_PUBLISH_FAILED"
    MESSAGE_CONSUME_FAILED = "MESSAGE_CONSUME_FAILED"
    MESSAGE_SERIALIZATION_FAILED = "MESSAGE_SERIALIZATION_FAILED"
    MESSAGE_DESERIALIZATION_FAILED = "MESSAGE_DESERIALIZATION_FAILED"
    
    # 主题相关错误
    TOPIC_NOT_FOUND = "TOPIC_NOT_FOUND"
    TOPIC_ALREADY_EXISTS = "TOPIC_ALREADY_EXISTS"
    TOPIC_CREATION_FAILED = "TOPIC_CREATION_FAILED"
    TOPIC_DELETION_FAILED = "TOPIC_DELETION_FAILED"
    
    # 订阅相关错误
    SUBSCRIPTION_FAILED = "SUBSCRIPTION_FAILED"
    SUBSCRIPTION_NOT_FOUND = "SUBSCRIPTION_NOT_FOUND"
    
    # 基础设施错误
    KAFKA_CONNECTION_ERROR = "KAFKA_CONNECTION_ERROR"
    REDIS_CONNECTION_ERROR = "REDIS_CONNECTION_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # 配置错误
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INVALID_PARAMETER = "INVALID_PARAMETER"


class MessageBusError(Exception):
    """消息总线基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.details = details or {}
        self.cause = cause
        self.timestamp = None
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "timestamp": self.timestamp,
            "cause": str(self.cause) if self.cause else None
        }


class ValidationError(MessageBusError):
    """验证错误"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(
            message,
            error_code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.LOW,
            **kwargs
        )
        if field:
            self.details["field"] = field


class TopicError(MessageBusError):
    """主题相关错误"""
    
    def __init__(self, message: str, topic_name: str = None, **kwargs):
        super().__init__(message, **kwargs)
        if topic_name:
            self.details["topic_name"] = topic_name


class MessageError(MessageBusError):
    """消息相关错误"""
    
    def __init__(self, message: str, message_id: str = None, topic: str = None, **kwargs):
        super().__init__(message, **kwargs)
        if message_id:
            self.details["message_id"] = message_id
        if topic:
            self.details["topic"] = topic


class InfrastructureError(MessageBusError):
    """基础设施错误"""
    
    def __init__(self, message: str, component: str = None, **kwargs):
        super().__init__(
            message,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if component:
            self.details["component"] = component


class ErrorHandler:
    """统一错误处理器"""
    
    def __init__(self):
        self.error_mappings = self._initialize_error_mappings()
    
    def _initialize_error_mappings(self) -> Dict[Type[Exception], ErrorCode]:
        """初始化错误映射"""
        return {
            ValueError: ErrorCode.VALIDATION_ERROR,
            TypeError: ErrorCode.VALIDATION_ERROR,
            KeyError: ErrorCode.INVALID_PARAMETER,
            ConnectionError: ErrorCode.NETWORK_ERROR,
            TimeoutError: ErrorCode.NETWORK_ERROR,
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        component: str = "unknown"
    ) -> MessageBusError:
        """
        处理错误并转换为标准格式
        
        Args:
            error: 原始异常
            context: 错误上下文信息
            component: 发生错误的组件名称
            
        Returns:
            MessageBusError: 标准化的错误对象
        """
        context = context or {}
        
        # 如果已经是MessageBusError，直接返回
        if isinstance(error, MessageBusError):
            self._log_error(error, context, component)
            self._record_error_metrics(error, component)
            return error
        
        # 映射标准异常到错误代码
        error_code = self.error_mappings.get(type(error), ErrorCode.UNKNOWN_ERROR)
        
        # 创建标准化错误
        message_bus_error = MessageBusError(
            message=str(error),
            error_code=error_code,
            severity=self._determine_severity(error),
            details=context,
            cause=error
        )
        
        self._log_error(message_bus_error, context, component)
        self._record_error_metrics(message_bus_error, component)
        
        return message_bus_error
    
    def _determine_severity(self, error: Exception) -> ErrorSeverity:
        """确定错误严重程度"""
        if isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorSeverity.HIGH
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM
    
    def _log_error(
        self,
        error: MessageBusError,
        context: Dict[str, Any],
        component: str
    ):
        """记录错误日志"""
        log_data = {
            "component": component,
            "error_code": error.error_code.value,
            "severity": error.severity.value,
            "message": error.message,
            "details": error.details,
            "context": context
        }
        
        if error.cause:
            log_data["cause"] = str(error.cause)
            log_data["traceback"] = traceback.format_exc()
        
        if error.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.error("Error occurred", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning("Warning occurred", extra=log_data)
        else:
            logger.info("Info occurred", extra=log_data)
    
    def _record_error_metrics(self, error: MessageBusError, component: str):
        """记录错误指标"""
        error_counter.labels(
            error_type=error.error_code.value,
            component=component,
            severity=error.severity.value
        ).inc()
    
    def to_grpc_error(self, error: MessageBusError) -> grpc.StatusCode:
        """将错误转换为gRPC状态码"""
        error_to_grpc_mapping = {
            ErrorCode.VALIDATION_ERROR: grpc.StatusCode.INVALID_ARGUMENT,
            ErrorCode.AUTHENTICATION_ERROR: grpc.StatusCode.UNAUTHENTICATED,
            ErrorCode.AUTHORIZATION_ERROR: grpc.StatusCode.PERMISSION_DENIED,
            ErrorCode.TOPIC_NOT_FOUND: grpc.StatusCode.NOT_FOUND,
            ErrorCode.TOPIC_ALREADY_EXISTS: grpc.StatusCode.ALREADY_EXISTS,
            ErrorCode.KAFKA_CONNECTION_ERROR: grpc.StatusCode.UNAVAILABLE,
            ErrorCode.REDIS_CONNECTION_ERROR: grpc.StatusCode.UNAVAILABLE,
            ErrorCode.NETWORK_ERROR: grpc.StatusCode.UNAVAILABLE,
            ErrorCode.CONFIGURATION_ERROR: grpc.StatusCode.FAILED_PRECONDITION,
        }
        
        return error_to_grpc_mapping.get(error.error_code, grpc.StatusCode.INTERNAL)


class CircuitBreakerError(MessageBusError):
    """断路器错误"""
    
    def __init__(self, component: str, **kwargs):
        super().__init__(
            f"Circuit breaker is open for component: {component}",
            error_code=ErrorCode.INTERNAL_ERROR,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        self.details["component"] = component


class RateLimitError(MessageBusError):
    """限流错误"""
    
    def __init__(self, limit: int, window: int, **kwargs):
        super().__init__(
            f"Rate limit exceeded: {limit} requests per {window} seconds",
            error_code=ErrorCode.INTERNAL_ERROR,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )
        self.details.update({
            "limit": limit,
            "window": window
        })


# 全局错误处理器实例
error_handler = ErrorHandler()


def handle_async_errors(func):
    """异步函数错误处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            component = getattr(func, '__qualname__', 'unknown')
            error = error_handler.handle_error(e, component=component)
            raise error
    return wrapper


def handle_sync_errors(func):
    """同步函数错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            component = getattr(func, '__qualname__', 'unknown')
            error = error_handler.handle_error(e, component=component)
            raise error
    return wrapper 