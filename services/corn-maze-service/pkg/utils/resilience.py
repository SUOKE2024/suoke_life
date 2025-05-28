#!/usr/bin/env python3

"""
重试和故障恢复工具
"""

import asyncio
from collections.abc import Callable
import functools
import logging
import random
import time
from typing import Any, TypeVar, cast

# 初始化日志
logger = logging.getLogger(__name__)

# 类型定义
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

def retry(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    重试装饰器，支持指数退避和抖动

    Args:
        max_retries: 最大重试次数
        retry_delay: 初始重试延迟（秒）
        backoff_factor: 退避因子
        jitter: 抖动因子
        exceptions: 需要重试的异常类型

    Returns:
        装饰后的函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        # 计算延迟时间
                        delay = retry_delay * (backoff_factor ** attempt)
                        # 添加随机抖动
                        delay = delay * (1 + random.uniform(-jitter, jitter))

                        logger.warning(
                            f"调用 {func.__name__} 失败，尝试 {attempt+1}/{max_retries}，"
                            f"将在 {delay:.2f} 秒后重试: {e!s}"
                        )

                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"调用 {func.__name__} 失败，已达到最大重试次数 {max_retries}: {e!s}"
                        )

            if last_exception:
                raise last_exception
            return None

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        # 计算延迟时间
                        delay = retry_delay * (backoff_factor ** attempt)
                        # 添加随机抖动
                        delay = delay * (1 + random.uniform(-jitter, jitter))

                        logger.warning(
                            f"调用 {func.__name__} 失败，尝试 {attempt+1}/{max_retries}，"
                            f"将在 {delay:.2f} 秒后重试: {e!s}"
                        )

                        time.sleep(delay)
                    else:
                        logger.error(
                            f"调用 {func.__name__} 失败，已达到最大重试次数 {max_retries}: {e!s}"
                        )

            if last_exception:
                raise last_exception
            return None

        # 根据原函数类型选择包装器
        if asyncio.iscoroutinefunction(func):
            return cast('F', async_wrapper)
        else:
            return cast('F', sync_wrapper)

    return decorator

class CircuitBreaker:
    """
    断路器模式实现
    
    用于在远程服务调用失败时提供故障隔离
    """

    # 断路器状态
    CLOSED = "CLOSED"       # 正常状态，允许请求通过
    OPEN = "OPEN"           # 断开状态，快速失败
    HALF_OPEN = "HALF_OPEN" # 半开状态，允许有限请求通过

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        expected_exceptions: tuple = (Exception,)
    ):
        """
        初始化断路器
        
        Args:
            name: 断路器名称
            failure_threshold: 触发断路器的连续失败次数
            recovery_timeout: 从OPEN到HALF_OPEN的恢复超时时间（秒）
            expected_exceptions: 计入失败次数的异常类型
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self._lock = asyncio.Lock()

    async def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        执行函数，应用断路器逻辑
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
            
        Raises:
            CircuitOpenError: 断路器处于打开状态
            原始异常: 如果函数执行失败并且断路器处于关闭或半开状态
        """
        async with self._lock:
            # 检查断路器状态
            if self.state == self.OPEN:
                # 检查是否应该转为半开状态
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(f"断路器 {self.name} 从 OPEN 变为 HALF_OPEN")
                    self.state = self.HALF_OPEN
                else:
                    logger.warning(f"断路器 {self.name} 处于 OPEN 状态，快速失败")
                    raise CircuitOpenError(f"断路器 {self.name} 处于打开状态")

        try:
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 成功执行，重置断路器
            async with self._lock:
                if self.state == self.HALF_OPEN:
                    logger.info(f"断路器 {self.name} 从 HALF_OPEN 变为 CLOSED")
                    self.state = self.CLOSED
                self.failure_count = 0

            return result

        except self.expected_exceptions:
            # 函数执行失败
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()

                # 检查是否应该打开断路器
                if self.state == self.CLOSED and self.failure_count >= self.failure_threshold:
                    logger.warning(f"断路器 {self.name} 从 CLOSED 变为 OPEN，连续失败 {self.failure_count} 次")
                    self.state = self.OPEN
                elif self.state == self.HALF_OPEN:
                    logger.warning(f"断路器 {self.name} 从 HALF_OPEN 变为 OPEN，测试请求失败")
                    self.state = self.OPEN

            # 重新抛出异常
            raise

class CircuitOpenError(Exception):
    """断路器打开异常"""
    pass

# 全局断路器注册表
_circuit_breakers: dict[str, CircuitBreaker] = {}

def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    expected_exceptions: tuple = (Exception,)
) -> CircuitBreaker:
    """
    获取或创建断路器
    
    Args:
        name: 断路器名称
        failure_threshold: 触发断路器的连续失败次数
        recovery_timeout: 从OPEN到HALF_OPEN的恢复超时时间（秒）
        expected_exceptions: 计入失败次数的异常类型
        
    Returns:
        CircuitBreaker: 断路器实例
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name,
            failure_threshold,
            recovery_timeout,
            expected_exceptions
        )
    return _circuit_breakers[name]

def with_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    expected_exceptions: tuple = (Exception,)
) -> Callable[[F], F]:
    """
    断路器装饰器
    
    Args:
        name: 断路器名称
        failure_threshold: 触发断路器的连续失败次数
        recovery_timeout: 从OPEN到HALF_OPEN的恢复超时时间（秒）
        expected_exceptions: 计入失败次数的异常类型
        
    Returns:
        装饰后的函数
    """
    circuit_breaker = get_circuit_breaker(
        name,
        failure_threshold,
        recovery_timeout,
        expected_exceptions
    )

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            return await circuit_breaker.execute(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # 同步函数需要用事件循环运行异步断路器
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(circuit_breaker.execute(func, *args, **kwargs))

        # 根据原函数类型选择包装器
        if asyncio.iscoroutinefunction(func):
            return cast('F', async_wrapper)
        else:
            return cast('F', sync_wrapper)

    return decorator
