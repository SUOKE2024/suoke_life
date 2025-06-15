#!/usr/bin/env python

"""
性能监控装饰器
提供函数级别的性能监控和指标收集
"""

import asyncio
import functools
import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)

# 全局性能监控器实例
_performance_monitor = None


def set_performance_monitor(monitor):
    """设置全局性能监控器"""
    global _performance_monitor
    _performance_monitor = monitor


def performance_monitor(
    operation_name: str = None, tags: dict[str, str] = None, record_args: bool = False
):
    """
    性能监控装饰器

    Args:
        operation_name: 操作名称，默认使用函数名
        tags: 额外的标签
        record_args: 是否记录函数参数
    """

    def decorator(func: Callable):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_type = None

            # 准备标签
            func_tags = (tags or {}).copy()
            func_tags.update(
                {"function": func.__name__, "module": func.__module__, "type": "async"}
            )

            # 记录参数（如果启用）
            if record_args and _performance_monitor:
                func_tags["args_count"] = str(len(args))
                func_tags["kwargs_count"] = str(len(kwargs))

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                func_tags["error"] = "true"
                func_tags["error_type"] = error_type
                raise
            finally:
                duration = time.time() - start_time

                if _performance_monitor:
                    # 记录执行时间
                    _performance_monitor._collector.record_timer(
                        f"{op_name}.duration", duration * 1000, func_tags  # 转换为毫秒
                    )

                    # 记录调用次数
                    _performance_monitor._collector.record_counter(
                        f"{op_name}.calls", 1, func_tags
                    )

                    # 记录成功/失败
                    status_tags = func_tags.copy()
                    status_tags["success"] = str(success)
                    _performance_monitor._collector.record_counter(
                        f"{op_name}.status", 1, status_tags
                    )

                logger.debug(
                    f"性能监控: {op_name} 耗时 {duration*1000:.2f}ms, 成功: {success}"
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_type = None

            # 准备标签
            func_tags = (tags or {}).copy()
            func_tags.update(
                {"function": func.__name__, "module": func.__module__, "type": "sync"}
            )

            # 记录参数（如果启用）
            if record_args and _performance_monitor:
                func_tags["args_count"] = str(len(args))
                func_tags["kwargs_count"] = str(len(kwargs))

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                func_tags["error"] = "true"
                func_tags["error_type"] = error_type
                raise
            finally:
                duration = time.time() - start_time

                if _performance_monitor:
                    # 记录执行时间
                    _performance_monitor._collector.record_timer(
                        f"{op_name}.duration", duration * 1000, func_tags  # 转换为毫秒
                    )

                    # 记录调用次数
                    _performance_monitor._collector.record_counter(
                        f"{op_name}.calls", 1, func_tags
                    )

                    # 记录成功/失败
                    status_tags = func_tags.copy()
                    status_tags["success"] = str(success)
                    _performance_monitor._collector.record_counter(
                        f"{op_name}.status", 1, status_tags
                    )

                logger.debug(
                    f"性能监控: {op_name} 耗时 {duration*1000:.2f}ms, 成功: {success}"
                )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def timer(name: str, tags: dict[str, str] = None):
    """
    计时器装饰器

    Args:
        name: 计时器名称
        tags: 额外标签
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if _performance_monitor:
                    _performance_monitor._collector.record_timer(
                        name, duration * 1000, tags
                    )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if _performance_monitor:
                    _performance_monitor._collector.record_timer(
                        name, duration * 1000, tags
                    )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def counter(name: str, tags: dict[str, str] = None, increment: float = 1):
    """
    计数器装饰器

    Args:
        name: 计数器名称
        tags: 额外标签
        increment: 增量值
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                if _performance_monitor:
                    success_tags = (tags or {}).copy()
                    success_tags["status"] = "success"
                    _performance_monitor._collector.record_counter(
                        name, increment, success_tags
                    )
                return result
            except Exception as e:
                if _performance_monitor:
                    error_tags = (tags or {}).copy()
                    error_tags["status"] = "error"
                    error_tags["error_type"] = type(e).__name__
                    _performance_monitor._collector.record_counter(
                        name, increment, error_tags
                    )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if _performance_monitor:
                    success_tags = (tags or {}).copy()
                    success_tags["status"] = "success"
                    _performance_monitor._collector.record_counter(
                        name, increment, success_tags
                    )
                return result
            except Exception as e:
                if _performance_monitor:
                    error_tags = (tags or {}).copy()
                    error_tags["status"] = "error"
                    error_tags["error_type"] = type(e).__name__
                    _performance_monitor._collector.record_counter(
                        name, increment, error_tags
                    )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
