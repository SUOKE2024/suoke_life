"""
重试装饰器工具

提供带有指数退避的重试功能
"""

import asyncio
from functools import wraps
import logging
import random
from typing import Any, Callable, Tuple, Type

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    带有指数退避的重试装饰器

    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟时间(秒)
        max_delay: 最大延迟时间(秒)
        exponential_base: 指数退避基数
        jitter: 是否添加随机抖动
        exceptions: 需要重试的异常类型
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败: {e}")
                        raise e

                    # 计算延迟时间
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # 添加随机抖动
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, {delay:.2f}秒后重试"
                    )
                    await asyncio.sleep(delay)

            # 这行代码理论上不会执行到
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败: {e}")
                        raise e

                    # 计算延迟时间
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # 添加随机抖动
                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, {delay:.2f}秒后重试"
                    )
                    import time

                    time.sleep(delay)

            # 这行代码理论上不会执行到
            raise last_exception

        # 根据函数是否为协程选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 便捷的重试装饰器
def retry_on_failure(max_retries: int = 3):
    """简单的重试装饰器"""
    return retry_with_backoff(max_retries=max_retries)


def retry_on_network_error(max_retries: int = 3):
    """网络错误重试装饰器"""
    import aiohttp

    network_exceptions = (
        aiohttp.ClientError,
        aiohttp.ServerTimeoutError,
        ConnectionError,
        TimeoutError,
    )
    return retry_with_backoff(max_retries=max_retries, exceptions=network_exceptions)
