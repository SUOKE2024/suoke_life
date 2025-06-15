"""
增强的错误处理机制
提供统一的异常处理、重试和恢复机制
"""

import asyncio
import functools
import logging
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorContext:
    """错误上下文信息"""

    function_name: str
    args: tuple
    kwargs: dict
    timestamp: float
    attempt: int
    max_attempts: int
    error: Exception
    severity: ErrorSeverity

    def to_dict(self) -> dict:
        return {
            "function_name": self.function_name,
            "timestamp": self.timestamp,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "severity": self.severity.value,
        }


class RetryConfig:
    """重试配置"""

    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        exceptions: tuple = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.exceptions = exceptions

    def get_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)


def enhanced_error_handler(
    retry_config: RetryConfig | None = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    fallback_value: Any = None,
    log_errors: bool = True,
    raise_on_failure: bool = True,
):
    """
    增强的错误处理装饰器

    Args:
        retry_config: 重试配置
        severity: 错误严重程度
        fallback_value: 失败时的回退值
        log_errors: 是否记录错误日志
        raise_on_failure: 最终失败时是否抛出异常
    """
    retry_config = retry_config or RetryConfig()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

                except retry_config.exceptions as e:
                    last_error = e

                    error_context = ErrorContext(
                        function_name=func.__name__,
                        args=args,
                        kwargs=kwargs,
                        timestamp=time.time(),
                        attempt=attempt,
                        max_attempts=retry_config.max_attempts,
                        error=e,
                        severity=severity,
                    )

                    if log_errors:
                        log_level = _get_log_level(severity)
                        logger.log(
                            log_level,
                            f"函数 {func.__name__} 第 {attempt} 次尝试失败: {e}",
                        )

                        if attempt == retry_config.max_attempts:
                            logger.error(f"函数 {func.__name__} 所有重试均失败")
                            logger.debug(f"错误详情: {traceback.format_exc()}")

                    # 如果不是最后一次尝试，等待后重试
                    if attempt < retry_config.max_attempts:
                        delay = retry_config.get_delay(attempt)
                        await asyncio.sleep(delay)

                except Exception as e:
                    # 不在重试范围内的异常直接抛出
                    if log_errors:
                        logger.error(f"函数 {func.__name__} 发生不可重试的错误: {e}")
                        logger.debug(f"错误详情: {traceback.format_exc()}")

                    if raise_on_failure:
                        raise
                    return fallback_value

            # 所有重试都失败了
            if raise_on_failure:
                raise last_error
            return fallback_value

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(1, retry_config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except retry_config.exceptions as e:
                    last_error = e

                    if log_errors:
                        log_level = _get_log_level(severity)
                        logger.log(
                            log_level,
                            f"函数 {func.__name__} 第 {attempt} 次尝试失败: {e}",
                        )

                        if attempt == retry_config.max_attempts:
                            logger.error(f"函数 {func.__name__} 所有重试均失败")
                            logger.debug(f"错误详情: {traceback.format_exc()}")

                    if attempt < retry_config.max_attempts:
                        delay = retry_config.get_delay(attempt)
                        time.sleep(delay)

                except Exception as e:
                    if log_errors:
                        logger.error(f"函数 {func.__name__} 发生不可重试的错误: {e}")
                        logger.debug(f"错误详情: {traceback.format_exc()}")

                    if raise_on_failure:
                        raise
                    return fallback_value

            if raise_on_failure:
                raise last_error
            return fallback_value

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def _get_log_level(severity: ErrorSeverity) -> int:
    """根据严重程度获取日志级别"""
    level_map = {
        ErrorSeverity.LOW: logging.INFO,
        ErrorSeverity.MEDIUM: logging.WARNING,
        ErrorSeverity.HIGH: logging.ERROR,
        ErrorSeverity.CRITICAL: logging.CRITICAL,
    }
    return level_map.get(severity, logging.WARNING)


# 预定义的重试配置
QUICK_RETRY = RetryConfig(max_attempts=2, delay=0.1, backoff_factor=1.5)
STANDARD_RETRY = RetryConfig(max_attempts=3, delay=1.0, backoff_factor=2.0)
PERSISTENT_RETRY = RetryConfig(
    max_attempts=5, delay=2.0, backoff_factor=2.0, max_delay=30.0
)
NETWORK_RETRY = RetryConfig(
    max_attempts=3,
    delay=1.0,
    backoff_factor=2.0,
    exceptions=(ConnectionError, TimeoutError),
)


# 便捷装饰器
def quick_retry(func):
    """快速重试装饰器"""
    return enhanced_error_handler(retry_config=QUICK_RETRY)(func)


def standard_retry(func):
    """标准重试装饰器"""
    return enhanced_error_handler(retry_config=STANDARD_RETRY)(func)


def persistent_retry(func):
    """持久重试装饰器"""
    return enhanced_error_handler(retry_config=PERSISTENT_RETRY)(func)


def network_retry(func):
    """网络重试装饰器"""
    return enhanced_error_handler(retry_config=NETWORK_RETRY)(func)
