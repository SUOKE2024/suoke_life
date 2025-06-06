"""
retry - 索克生活项目模块
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import functools
import inspect
import logging
import random
import time

"""
重试和错误处理模块

提供智能重试机制、错误恢复和故障处理功能
"""


logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """重试策略"""

    FIXED = "fixed"  # 固定间隔
    EXPONENTIAL = "exponential"  # 指数退避
    LINEAR = "linear"  # 线性增长
    RANDOM = "random"  # 随机间隔


@dataclass
class RetryConfig:
    """重试配置"""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    backoff_factor: float = 2.0
    jitter: bool = True
    exceptions: tuple = (Exception,)
    on_retry: Callable | None = None
    on_failure: Callable | None = None


class RetryError(Exception):
    """重试失败异常"""

    def __init__(self, message: str, attempts: int, last_exception: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception


class CircuitBreakerState(str, Enum):
    """熔断器状态"""

    CLOSED = "closed"  # 关闭状态，正常工作
    OPEN = "open"  # 开启状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""

    failure_threshold: int = 5  # 失败阈值
    recovery_timeout: float = 60.0  # 恢复超时
    expected_exception: type[Exception] = Exception
    success_threshold: int = 3  # 半开状态成功阈值


class CircuitBreaker:
    """熔断器"""

    def __init__(self, config: CircuitBreakerConfig):
        """
        初始化熔断器

        Args:
            config: 熔断器配置
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0

        logger.info(f"熔断器初始化完成，失败阈值: {config.failure_threshold}")

    def call(self, func: Callable, *args, **kwargs):
        """
        调用函数并应用熔断器逻辑

        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            CircuitBreakerError: 熔断器开启时
        """
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time < self.config.recovery_timeout:
                raise CircuitBreakerError("熔断器开启，拒绝请求")
            else:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("熔断器进入半开状态")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func: Callable, *args, **kwargs):
        """异步版本的调用"""
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time < self.config.recovery_timeout:
                raise CircuitBreakerError("熔断器开启，拒绝请求")
            else:
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("熔断器进入半开状态")

        try:
            if inspect.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """成功回调"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("熔断器恢复到关闭状态")
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """失败回调"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("熔断器从半开状态回到开启状态")
        elif (
            self.state == CircuitBreakerState.CLOSED
            and self.failure_count >= self.config.failure_threshold
        ):
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"熔断器开启，失败次数: {self.failure_count}")


class CircuitBreakerError(Exception):
    """熔断器异常"""

    pass


class RetryManager:
    """重试管理器"""

    def __init__(self, config: RetryConfig):
        """
        初始化重试管理器

        Args:
            config: 重试配置
        """
        self.config = config

    def retry(self, func: Callable, *args, **kwargs):
        """
        执行重试逻辑

        Args:
            func: 要重试的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数执行结果

        Raises:
            RetryError: 重试失败
        """
        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 1:
                    logger.info(f"重试成功，尝试次数: {attempt}")
                return result

            except self.config.exceptions as e:
                last_exception = e

                if attempt == self.config.max_attempts:
                    break

                delay = self._calculate_delay(attempt)

                logger.warning(
                    f"第 {attempt} 次尝试失败: {str(e)}, {delay:.2f}秒后重试"
                )

                if self.config.on_retry:
                    try:
                        self.config.on_retry(attempt, e, delay)
                    except Exception as callback_error:
                        logger.error(f"重试回调函数出错: {callback_error}")

                time.sleep(delay)

        # 所有重试都失败了
        error_msg = f"重试 {self.config.max_attempts} 次后仍然失败"

        if self.config.on_failure:
            try:
                self.config.on_failure(self.config.max_attempts, last_exception)
            except Exception as callback_error:
                logger.error(f"失败回调函数出错: {callback_error}")

        raise RetryError(error_msg, self.config.max_attempts, last_exception)

    async def retry_async(self, func: Callable, *args, **kwargs):
        """异步重试"""
        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                if attempt > 1:
                    logger.info(f"异步重试成功，尝试次数: {attempt}")
                return result

            except self.config.exceptions as e:
                last_exception = e

                if attempt == self.config.max_attempts:
                    break

                delay = self._calculate_delay(attempt)

                logger.warning(
                    f"第 {attempt} 次异步尝试失败: {str(e)}, {delay:.2f}秒后重试"
                )

                if self.config.on_retry:
                    try:
                        if inspect.iscoroutinefunction(self.config.on_retry):
                            await self.config.on_retry(attempt, e, delay)
                        else:
                            self.config.on_retry(attempt, e, delay)
                    except Exception as callback_error:
                        logger.error(f"异步重试回调函数出错: {callback_error}")

                await asyncio.sleep(delay)

        # 所有重试都失败了
        error_msg = f"异步重试 {self.config.max_attempts} 次后仍然失败"

        if self.config.on_failure:
            try:
                if inspect.iscoroutinefunction(self.config.on_failure):
                    await self.config.on_failure(
                        self.config.max_attempts, last_exception
                    )
                else:
                    self.config.on_failure(self.config.max_attempts, last_exception)
            except Exception as callback_error:
                logger.error(f"异步失败回调函数出错: {callback_error}")

        raise RetryError(error_msg, self.config.max_attempts, last_exception)

    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay * (
                self.config.backoff_factor ** (attempt - 1)
            )
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay * attempt
        elif self.config.strategy == RetryStrategy.RANDOM:
            delay = random.uniform(self.config.base_delay, self.config.max_delay)
        else:
            delay = self.config.base_delay

        # 应用最大延迟限制
        delay = min(delay, self.config.max_delay)

        # 添加抖动
        if self.config.jitter:
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,),
    on_retry: Callable | None = None,
    on_failure: Callable | None = None,
):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        strategy: 重试策略
        backoff_factor: 退避因子
        jitter: 是否添加抖动
        exceptions: 需要重试的异常类型
        on_retry: 重试回调函数
        on_failure: 失败回调函数
    """

    def decorator(func):
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            strategy=strategy,
            backoff_factor=backoff_factor,
            jitter=jitter,
            exceptions=exceptions,
            on_retry=on_retry,
            on_failure=on_failure,
        )

        retry_manager = RetryManager(config)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await retry_manager.retry_async(func, *args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return retry_manager.retry(func, *args, **kwargs)

            return sync_wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: type[Exception] = Exception,
    success_threshold: int = 3,
):
    """
    熔断器装饰器

    Args:
        failure_threshold: 失败阈值
        recovery_timeout: 恢复超时
        expected_exception: 预期异常类型
        success_threshold: 成功阈值
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        expected_exception=expected_exception,
        success_threshold=success_threshold,
    )

    breaker = CircuitBreaker(config)

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await breaker.call_async(func, *args, **kwargs)

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return breaker.call(func, *args, **kwargs)

            return sync_wrapper

    return decorator


# 预定义的重试配置
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_attempts=3, base_delay=1.0, strategy=RetryStrategy.EXPONENTIAL
)

AGGRESSIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=0.5,
    max_delay=30.0,
    strategy=RetryStrategy.EXPONENTIAL,
    backoff_factor=1.5,
)

CONSERVATIVE_RETRY_CONFIG = RetryConfig(
    max_attempts=2, base_delay=2.0, max_delay=10.0, strategy=RetryStrategy.FIXED
)


# 预定义的熔断器配置
DEFAULT_CIRCUIT_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=5, recovery_timeout=60.0
)

SENSITIVE_CIRCUIT_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=3, recovery_timeout=30.0, success_threshold=2
)

ROBUST_CIRCUIT_BREAKER_CONFIG = CircuitBreakerConfig(
    failure_threshold=10, recovery_timeout=120.0, success_threshold=5
)
