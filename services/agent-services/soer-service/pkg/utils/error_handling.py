"""
统一的错误处理和重试机制
提供结构化的异常处理、重试策略和错误恢复机制
"""
import asyncio
import logging
import random
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """错误上下文信息"""
    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    operation: str | None = None
    additional_data: dict[str, Any] | None = None

class SoerServiceException(Exception):
    """索儿服务基础异常"""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: ErrorContext | None = None,
        cause: Exception | None = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or ErrorContext()
        self.cause = cause
        self.timestamp = time.time()

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "severity": self.severity.value,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "request_id": self.context.request_id,
                "operation": self.context.operation,
                "additional_data": self.context.additional_data
            },
            "cause": str(self.cause) if self.cause else None
        }

class NetworkException(SoerServiceException):
    """网络相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="NETWORK_ERROR",
            category=ErrorCategory.NETWORK,
            **kwargs
        )

class DatabaseException(SoerServiceException):
    """数据库相关异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            **kwargs
        )

class ExternalAPIException(SoerServiceException):
    """外部API异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="EXTERNAL_API_ERROR",
            category=ErrorCategory.EXTERNAL_API,
            **kwargs
        )

class ValidationException(SoerServiceException):
    """验证异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )

class BusinessLogicException(SoerServiceException):
    """业务逻辑异常"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="BUSINESS_LOGIC_ERROR",
            category=ErrorCategory.BUSINESS_LOGIC,
            **kwargs
        )

@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: list[type[Exception]] = None

    def __post_init__(self):
        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                NetworkException,
                ExternalAPIException,
                ConnectionError,
                TimeoutError
            ]

class RetryStrategy:
    """重试策略"""

    @staticmethod
    def calculate_delay(attempt: int, config: RetryConfig) -> float:
        """计算重试延迟"""
        delay = config.base_delay * (config.exponential_base ** (attempt - 1))
        delay = min(delay, config.max_delay)

        if config.jitter:
            # 添加随机抖动，避免雷群效应
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    @staticmethod
    def should_retry(exception: Exception, config: RetryConfig) -> bool:
        """判断是否应该重试"""
        return any(isinstance(exception, exc_type) for exc_type in config.retryable_exceptions)

def retry_async(config: RetryConfig = None):
    """异步重试装饰器"""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_attempts:
                        logger.error(f"函数 {func.__name__} 重试 {config.max_attempts} 次后仍然失败")
                        break

                    if not RetryStrategy.should_retry(e, config):
                        logger.warning(f"函数 {func.__name__} 遇到不可重试异常: {e}")
                        break

                    delay = RetryStrategy.calculate_delay(attempt, config)
                    logger.warning(f"函数 {func.__name__} 第 {attempt} 次尝试失败，{delay:.2f}秒后重试: {e}")

                    await asyncio.sleep(delay)

            raise last_exception

        return wrapper
    return decorator

def retry_sync(config: RetryConfig = None):
    """同步重试装饰器"""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_attempts:
                        logger.error(f"函数 {func.__name__} 重试 {config.max_attempts} 次后仍然失败")
                        break

                    if not RetryStrategy.should_retry(e, config):
                        logger.warning(f"函数 {func.__name__} 遇到不可重试异常: {e}")
                        break

                    delay = RetryStrategy.calculate_delay(attempt, config)
                    logger.warning(f"函数 {func.__name__} 第 {attempt} 次尝试失败，{delay:.2f}秒后重试: {e}")

                    time.sleep(delay)

            raise last_exception

        return wrapper
    return decorator

class ErrorHandler:
    """统一错误处理器"""

    def __init__(self):
        self._error_callbacks: dict[ErrorCategory, list[Callable]] = {}
        self._global_callbacks: list[Callable] = []

    def register_error_callback(self, category: ErrorCategory, callback: Callable) -> None:
        """注册错误回调"""
        if category not in self._error_callbacks:
            self._error_callbacks[category] = []
        self._error_callbacks[category].append(callback)

    def register_global_callback(self, callback: Callable) -> None:
        """注册全局错误回调"""
        self._global_callbacks.append(callback)

    async def handle_error(self, error: Exception, context: ErrorContext | None = None) -> None:
        """处理错误"""
        # 转换为标准异常格式
        if isinstance(error, SoerServiceException):
            service_error = error
        else:
            service_error = SoerServiceException(
                message=str(error),
                cause=error,
                context=context
            )

        # 记录错误日志
        self._log_error(service_error)

        # 执行分类回调
        category_callbacks = self._error_callbacks.get(service_error.category, [])
        for callback in category_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(service_error)
                else:
                    callback(service_error)
            except Exception as e:
                logger.error(f"错误回调执行失败: {e}")

        # 执行全局回调
        for callback in self._global_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(service_error)
                else:
                    callback(service_error)
            except Exception as e:
                logger.error(f"全局错误回调执行失败: {e}")

    def _log_error(self, error: SoerServiceException) -> None:
        """记录错误日志"""
        log_data = {
            "error_code": error.error_code,
            "message": error.message,
            "severity": error.severity.value,
            "category": error.category.value,
            "context": error.context.__dict__ if error.context else {},
            "traceback": traceback.format_exc() if error.cause else None
        }

        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical("严重错误", extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error("高级错误", extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning("中级错误", extra=log_data)
        else:
            logger.info("低级错误", extra=log_data)

def safe_execute(func: Callable, *args, default_return=None, **kwargs):
    """安全执行函数，捕获异常并返回默认值"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"函数 {func.__name__} 执行失败: {e}")
        return default_return

async def safe_execute_async(func: Callable, *args, default_return=None, **kwargs):
    """安全执行异步函数，捕获异常并返回默认值"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"异步函数 {func.__name__} 执行失败: {e}")
        return default_return

# 全局错误处理器实例
_error_handler: ErrorHandler | None = None

def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler

def setup_error_handler(handler: ErrorHandler) -> None:
    """设置全局错误处理器"""
    global _error_handler
    _error_handler = handler
