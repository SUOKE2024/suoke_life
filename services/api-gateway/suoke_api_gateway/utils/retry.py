"""
retry - 索克生活项目模块
"""

from ..core.logging import get_logger
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Type, Union
import asyncio
import random
import time

"""
重试机制模块

实现各种重试策略和重试管理器。
"""



logger = get_logger(__name__)


class RetryError(Exception):
    """重试异常"""

    def __init__(self, message: str, attempts: int, last_exception: Exception):
"""TODO: 添加文档字符串"""
super().__init__(message)
self.attempts = attempts
self.last_exception = last_exception


class RetryStrategy(ABC):
    """重试策略基类"""

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
"""获取延迟时间"""
pass


class FixedDelayStrategy(RetryStrategy):
    """固定延迟策略"""

    def __init__(self, delay: float):
"""TODO: 添加文档字符串"""
self.delay = delay

    def get_delay(self, attempt: int) -> float:
"""TODO: 添加文档字符串"""
return self.delay


class ExponentialBackoffStrategy(RetryStrategy):
    """指数退避策略"""

    def __init__(
self,
initial_delay: float = 1.0,
multiplier: float = 2.0,
max_delay: float = 60.0,
jitter: bool = True,
    ):
self.initial_delay = initial_delay
self.multiplier = multiplier
self.max_delay = max_delay
self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
"""TODO: 添加文档字符串"""
delay = self.initial_delay * (self.multiplier**(attempt - 1))
delay = min(delay, self.max_delay)

if self.jitter:
            # 添加随机抖动，避免雷群效应
            delay = delay * (0.5 + random.random() * 0.5)

return delay


class LinearBackoffStrategy(RetryStrategy):
    """线性退避策略"""

    def __init__(
self,
initial_delay: float = 1.0,
increment: float = 1.0,
max_delay: float = 60.0,
    ):
self.initial_delay = initial_delay
self.increment = increment
self.max_delay = max_delay

    def get_delay(self, attempt: int) -> float:
"""TODO: 添加文档字符串"""
delay = self.initial_delay + (attempt - 1) * self.increment
return min(delay, self.max_delay)


class RetryManager:
    """重试管理器"""

    def __init__(
self,
max_attempts: int = 3,
strategy: Optional[RetryStrategy] = None,
timeout: Optional[float] = None,
stop_on: Optional[List[Type[Exception]]] = None,
retry_on: Optional[List[Type[Exception]]] = None,
    ):
"""
初始化重试管理器

Args:
            max_attempts: 最大重试次数
            strategy: 重试策略
            timeout: 总超时时间
            stop_on: 遇到这些异常时停止重试
            retry_on: 只对这些异常进行重试
"""
self.max_attempts = max_attempts
self.strategy = strategy or ExponentialBackoffStrategy()
self.timeout = timeout
self.stop_on = stop_on or []
self.retry_on = retry_on

# 统计信息
self.total_attempts = 0
self.total_successes = 0
self.total_failures = 0

    async def execute(self, func: Callable, * args,**kwargs) -> Any:
"""
执行函数并在失败时重试

Args:
            func: 要执行的函数
            * args: 函数参数
           **kwargs: 函数关键字参数

Returns:
            函数返回值

Raises:
            RetryError: 重试次数耗尽或遇到不可重试的异常
"""
start_time = time.time()
last_exception = None

for attempt in range(1, self.max_attempts + 1):
            self.total_attempts+=1

            try:
                # 检查超时
                if self.timeout and (time.time() - start_time) > self.timeout:
                    raise RetryError(
                        f"Timeout after {self.timeout}s",
                        attempt,
                        last_exception or TimeoutError("Timeout"),
                    )

                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func( * args,**kwargs)
                else:
                    result = func( * args,**kwargs)

                self.total_successes+=1

                if attempt > 1:
                    logger.info(
                        "Function succeeded after retry",
                        attempt = attempt,
                        total_attempts = self.total_attempts,
                    )

                return result

            except Exception as e:
                last_exception = e

                # 检查是否应该停止重试
                if self._should_stop_retry(e):
                    logger.info(
                        "Stopping retry due to exception type",
                        exception = type(e).__name__,
                        attempt = attempt,
                    )
                    raise e

                # 检查是否应该重试
                if not self._should_retry(e):
                    logger.info(
                        "Not retrying due to exception type",
                        exception = type(e).__name__,
                        attempt = attempt,
                    )
                    raise e

                # 如果是最后一次尝试，抛出重试错误
                if attempt==self.max_attempts:
                    self.total_failures+=1
                    raise RetryError(
                        f"Failed after {attempt} attempts",
                        attempt,
                        e,
                    )

                # 计算延迟时间
                delay = self.strategy.get_delay(attempt)

                logger.warning(
                    "Function failed, retrying",
                    attempt = attempt,
                    max_attempts = self.max_attempts,
                    delay = delay,
                    exception = type(e).__name__,
                    error = str(e),
                )

                # 等待重试
                await asyncio.sleep(delay)

# 这里不应该到达
self.total_failures+=1
raise RetryError(
            f"Failed after {self.max_attempts} attempts",
            self.max_attempts,
            last_exception,
)

    def _should_stop_retry(self, exception: Exception) -> bool:
"""检查是否应该停止重试"""
return any(isinstance(exception, exc_type) for exc_type in self.stop_on)

    def _should_retry(self, exception: Exception) -> bool:
"""检查是否应该重试"""
if self.retry_on:
            return any(isinstance(exception, exc_type) for exc_type in self.retry_on)
return True

    def get_stats(self) -> dict:
"""获取统计信息"""
return {
            "total_attempts": self.total_attempts,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "success_rate": (
                self.total_successes / self.total_attempts * 100
                if self.total_attempts > 0 else 0
            ),
}


def retry(
    max_attempts: int = 3,
    strategy: Optional[RetryStrategy] = None,
    timeout: Optional[float] = None,
    stop_on: Optional[List[Type[Exception]]] = None,
    retry_on: Optional[List[Type[Exception]]] = None,
):
    """重试装饰器"""
    def decorator(func: Callable):
"""TODO: 添加文档字符串"""
retry_manager = RetryManager(
            max_attempts = max_attempts,
            strategy = strategy,
            timeout = timeout,
            stop_on = stop_on,
            retry_on = retry_on,
)

async def async_wrapper( * args,**kwargs):
            return await retry_manager.execute(func, * args,**kwargs)

def sync_wrapper( * args,**kwargs):
            """TODO: 添加文档字符串"""
            return asyncio.run(retry_manager.execute(func, * args,**kwargs))

if asyncio.iscoroutinefunction(func):
            return async_wrapper
else:
            return sync_wrapper

    return decorator


# 预定义的重试策略
DEFAULT_STRATEGY = ExponentialBackoffStrategy()
FAST_STRATEGY = ExponentialBackoffStrategy(initial_delay = 0.1, max_delay = 5.0)
SLOW_STRATEGY = ExponentialBackoffStrategy(initial_delay = 2.0, max_delay = 120.0)
FIXED_STRATEGY = FixedDelayStrategy(1.0)