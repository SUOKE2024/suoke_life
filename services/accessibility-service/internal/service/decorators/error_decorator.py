#!/usr/bin/env python

"""
错误处理装饰器
提供函数级别的错误处理、重试和断路器功能
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# 全局错误处理器实例
_error_handler = None


def set_error_handler(handler):
    """设置全局错误处理器"""
    global _error_handler
    _error_handler = handler


def error_handler(
    operation_name: str = None,
    handle_exceptions: list[type[Exception]] = None,
    ignore_exceptions: list[type[Exception]] = None,
    default_return: Any = None,
):
    """
    错误处理装饰器

    Args:
        operation_name: 操作名称
        handle_exceptions: 需要处理的异常类型列表
        ignore_exceptions: 需要忽略的异常类型列表
        default_return: 发生错误时的默认返回值
    """

    def decorator(func: Callable):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # 检查是否需要忽略此异常
                if ignore_exceptions and any(
                    isinstance(e, exc_type) for exc_type in ignore_exceptions
                ):
                    raise

                # 检查是否需要处理此异常
                if handle_exceptions and not any(
                    isinstance(e, exc_type) for exc_type in handle_exceptions
                ):
                    raise

                # 记录错误
                logger.error(f"错误处理: {op_name} 发生异常: {type(e).__name__}: {e!s}")

                # 使用错误处理器处理
                if _error_handler:
                    error_info = _error_handler._classifier.classify(
                        e,
                        {
                            "operation": op_name,
                            "function": func.__name__,
                            "module": func.__module__,
                        },
                    )
                    _error_handler._record_error(op_name, error_info)

                # 返回默认值或重新抛出异常
                if default_return is not None:
                    return default_return
                else:
                    raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 检查是否需要忽略此异常
                if ignore_exceptions and any(
                    isinstance(e, exc_type) for exc_type in ignore_exceptions
                ):
                    raise

                # 检查是否需要处理此异常
                if handle_exceptions and not any(
                    isinstance(e, exc_type) for exc_type in handle_exceptions
                ):
                    raise

                # 记录错误
                logger.error(f"错误处理: {op_name} 发生异常: {type(e).__name__}: {e!s}")

                # 使用错误处理器处理
                if _error_handler:
                    error_info = _error_handler._classifier.classify(
                        e,
                        {
                            "operation": op_name,
                            "function": func.__name__,
                            "module": func.__module__,
                        },
                    )
                    _error_handler._record_error(op_name, error_info)

                # 返回默认值或重新抛出异常
                if default_return is not None:
                    return default_return
                else:
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    backoff_strategy: str = "exponential",
    retry_on: list[type[Exception]] = None,
    stop_on: list[type[Exception]] = None,
):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        base_delay: 基础延迟时间
        max_delay: 最大延迟时间
        exponential_base: 指数退避基数
        jitter: 是否添加随机抖动
        backoff_strategy: 退避策略
        retry_on: 需要重试的异常类型
        stop_on: 不重试的异常类型
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if _error_handler:
                from ..error_handler import RetryConfig

                config = RetryConfig(
                    max_attempts=max_attempts,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                    backoff_strategy=backoff_strategy,
                    retry_on=retry_on or [],
                    stop_on=stop_on or [],
                )
                return await _error_handler._retry_with_config(
                    func, config, *args, **kwargs
                )
            else:
                # 简单重试逻辑
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            delay = min(
                                base_delay * (exponential_base**attempt), max_delay
                            )
                            await asyncio.sleep(delay)
                        else:
                            raise
                raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if _error_handler:
                # 对于同步函数，需要特殊处理
                import asyncio

                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                async def async_func(*args, **kwargs):
                    return func(*args, **kwargs)

                from ..error_handler import RetryConfig

                config = RetryConfig(
                    max_attempts=max_attempts,
                    base_delay=base_delay,
                    max_delay=max_delay,
                    exponential_base=exponential_base,
                    jitter=jitter,
                    backoff_strategy=backoff_strategy,
                    retry_on=retry_on or [],
                    stop_on=stop_on or [],
                )
                return loop.run_until_complete(
                    _error_handler._retry_with_config(
                        async_func, config, *args, **kwargs
                    )
                )
            else:
                # 简单重试逻辑
                import time

                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            delay = min(
                                base_delay * (exponential_base**attempt), max_delay
                            )
                            time.sleep(delay)
                        else:
                            raise
                raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: type[Exception] = Exception,
    success_threshold: int = 3,
):
    """
    断路器装饰器

    Args:
        name: 断路器名称
        failure_threshold: 失败阈值
        recovery_timeout: 恢复超时时间
        expected_exception: 预期异常类型
        success_threshold: 成功阈值
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if _error_handler:
                from ..error_handler import CircuitBreakerConfig

                config = CircuitBreakerConfig(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    expected_exception=expected_exception,
                    success_threshold=success_threshold,
                )
                circuit_breaker_instance = _error_handler.circuit_breaker(name, config)
                return await circuit_breaker_instance.call(func, *args, **kwargs)
            else:
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if _error_handler:
                from ..error_handler import CircuitBreakerConfig

                config = CircuitBreakerConfig(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    expected_exception=expected_exception,
                    success_threshold=success_threshold,
                )
                circuit_breaker_instance = _error_handler.circuit_breaker(name, config)

                # 对于同步函数，需要特殊处理
                import asyncio

                loop = None
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                async def async_func(*args, **kwargs):
                    return func(*args, **kwargs)

                return loop.run_until_complete(
                    circuit_breaker_instance.call(async_func, *args, **kwargs)
                )
            else:
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
