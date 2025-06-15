"""
重试工具模块

提供异步函数的重试装饰器和配置。
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 60.0
    exceptions: tuple[type[Exception], ...] = (Exception,)
    jitter: bool = True


def retry_async(
    config: RetryConfig | None = None,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    jitter: bool = True
) -> Callable:
    """异步函数重试装饰器

    Args:
        config: 重试配置对象，如果提供则忽略其他参数
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        max_delay: 最大延迟时间（秒）
        exceptions: 需要重试的异常类型
        jitter: 是否添加随机抖动

    Returns:
        装饰器函数
    """
    if config is None:
        if isinstance(exceptions, type):
            exceptions = (exceptions,)
        config = RetryConfig(
            max_attempts=max_attempts,
            delay=delay,
            backoff_factor=backoff_factor,
            max_delay=max_delay,
            exceptions=exceptions,
            jitter=jitter
        )

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = config.delay

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)

                except config.exceptions as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        # 最后一次尝试失败
                        logger.error(
                            f"函数 {func.__name__} 重试 {config.max_attempts} 次后仍然失败",
                            extra={
                                "function": func.__name__,
                                "attempts": config.max_attempts,
                                "error": str(e)
                            }
                        )
                        raise e

                    # 计算延迟时间
                    actual_delay = min(current_delay, config.max_delay)

                    if config.jitter:
                        # 添加随机抖动（±25%）
                        import random
                        jitter_factor = 0.75 + random.random() * 0.5
                        actual_delay *= jitter_factor

                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{actual_delay:.2f}秒后重试",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "delay": actual_delay,
                            "error": str(e)
                        }
                    )

                    await asyncio.sleep(actual_delay)
                    current_delay *= config.backoff_factor

                except Exception as e:
                    # 不在重试范围内的异常直接抛出
                    logger.error(
                        f"函数 {func.__name__} 遇到不可重试的异常",
                        extra={
                            "function": func.__name__,
                            "error": str(e),
                            "error_type": type(e).__name__
                        }
                    )
                    raise e

            # 理论上不会到达这里
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def create_retry_config(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: type[Exception] | tuple[type[Exception], ...] = Exception,
    jitter: bool = True
) -> RetryConfig:
    """创建重试配置

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        max_delay: 最大延迟时间（秒）
        exceptions: 需要重试的异常类型
        jitter: 是否添加随机抖动

    Returns:
        重试配置对象
    """
    if isinstance(exceptions, type):
        exceptions = (exceptions,)

    return RetryConfig(
        max_attempts=max_attempts,
        delay=delay,
        backoff_factor=backoff_factor,
        max_delay=max_delay,
        exceptions=exceptions,
        jitter=jitter
    )


# 别名，保持向后兼容
async_retry = retry_async
