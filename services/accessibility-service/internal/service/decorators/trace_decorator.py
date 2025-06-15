#!/usr/bin/env python

"""
链路追踪装饰器
提供函数级别的分布式追踪功能
"""

import asyncio
import functools
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

# 全局性能监控器实例（包含追踪器）
_performance_monitor = None


def set_performance_monitor(monitor):
    """设置全局性能监控器"""
    global _performance_monitor
    _performance_monitor = monitor


def trace(
    operation_name: str = None, kind: str = "internal", tags: dict[str, Any] = None
):
    """
    追踪装饰器

    Args:
        operation_name: 操作名称
        kind: Span类型 (server, client, producer, consumer, internal)
        tags: 额外标签
    """

    def decorator(func: Callable):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _performance_monitor:
                return await func(*args, **kwargs)

            # 导入SpanKind枚举
            from ..performance_monitor import SpanKind

            span_kind = getattr(SpanKind, kind.upper(), SpanKind.INTERNAL)

            # 开始追踪
            span = _performance_monitor._tracer.start_span(op_name, span_kind)

            try:
                # 设置基础标签
                span.set_tag("function.name", func.__name__)
                span.set_tag("function.module", func.__module__)
                span.set_tag("function.type", "async")

                # 设置额外标签
                if tags:
                    for key, value in tags.items():
                        span.set_tag(key, value)

                # 记录参数信息（可选）
                if len(args) > 0:
                    span.set_tag("args.count", len(args))
                if len(kwargs) > 0:
                    span.set_tag("kwargs.count", len(kwargs))

                # 执行函数
                result = await func(*args, **kwargs)

                # 记录成功信息
                span.set_tag("success", True)
                span.log("函数执行成功")

                return result

            except Exception as e:
                # 记录错误信息
                span.set_tag("error", True)
                span.set_tag("error.type", type(e).__name__)
                span.set_tag("error.message", str(e))
                span.log(f"函数执行异常: {e!s}", level="error")

                # 重新抛出异常
                raise

            finally:
                # 结束追踪
                from ..performance_monitor import SpanStatus

                status = SpanStatus.ERROR if span.tags.get("error") else SpanStatus.OK
                _performance_monitor._tracer.finish_span(span, status)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _performance_monitor:
                return func(*args, **kwargs)

            # 导入SpanKind枚举
            from ..performance_monitor import SpanKind

            span_kind = getattr(SpanKind, kind.upper(), SpanKind.INTERNAL)

            # 开始追踪
            span = _performance_monitor._tracer.start_span(op_name, span_kind)

            try:
                # 设置基础标签
                span.set_tag("function.name", func.__name__)
                span.set_tag("function.module", func.__module__)
                span.set_tag("function.type", "sync")

                # 设置额外标签
                if tags:
                    for key, value in tags.items():
                        span.set_tag(key, value)

                # 记录参数信息（可选）
                if len(args) > 0:
                    span.set_tag("args.count", len(args))
                if len(kwargs) > 0:
                    span.set_tag("kwargs.count", len(kwargs))

                # 执行函数
                result = func(*args, **kwargs)

                # 记录成功信息
                span.set_tag("success", True)
                span.log("函数执行成功")

                return result

            except Exception as e:
                # 记录错误信息
                span.set_tag("error", True)
                span.set_tag("error.type", type(e).__name__)
                span.set_tag("error.message", str(e))
                span.log(f"函数执行异常: {e!s}", level="error")

                # 重新抛出异常
                raise

            finally:
                # 结束追踪
                from ..performance_monitor import SpanStatus

                status = SpanStatus.ERROR if span.tags.get("error") else SpanStatus.OK
                _performance_monitor._tracer.finish_span(span, status)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def trace_async(
    operation_name: str = None, kind: str = "internal", tags: dict[str, Any] = None
):
    """
    异步追踪装饰器（专门用于异步函数）

    Args:
        operation_name: 操作名称
        kind: Span类型
        tags: 额外标签
    """

    def decorator(func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("trace_async 装饰器只能用于异步函数")

        op_name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not _performance_monitor:
                return await func(*args, **kwargs)

            # 导入SpanKind枚举
            from ..performance_monitor import SpanKind

            span_kind = getattr(SpanKind, kind.upper(), SpanKind.INTERNAL)

            # 开始追踪
            span = _performance_monitor._tracer.start_span(op_name, span_kind)

            try:
                # 设置基础标签
                span.set_tag("function.name", func.__name__)
                span.set_tag("function.module", func.__module__)
                span.set_tag("function.type", "async")

                # 设置额外标签
                if tags:
                    for key, value in tags.items():
                        span.set_tag(key, value)

                # 记录参数信息
                if len(args) > 0:
                    span.set_tag("args.count", len(args))
                if len(kwargs) > 0:
                    span.set_tag("kwargs.count", len(kwargs))

                # 记录协程信息
                span.set_tag("coroutine.name", func.__name__)

                # 执行函数
                result = await func(*args, **kwargs)

                # 记录成功信息
                span.set_tag("success", True)
                span.log("异步函数执行成功")

                return result

            except asyncio.CancelledError:
                # 处理取消异常
                span.set_tag("cancelled", True)
                span.log("异步函数被取消", level="warning")
                raise

            except Exception as e:
                # 记录错误信息
                span.set_tag("error", True)
                span.set_tag("error.type", type(e).__name__)
                span.set_tag("error.message", str(e))
                span.log(f"异步函数执行异常: {e!s}", level="error")

                # 重新抛出异常
                raise

            finally:
                # 结束追踪
                from ..performance_monitor import SpanStatus

                if span.tags.get("cancelled"):
                    status = SpanStatus.CANCELLED
                elif span.tags.get("error"):
                    status = SpanStatus.ERROR
                else:
                    status = SpanStatus.OK

                _performance_monitor._tracer.finish_span(span, status)

        return wrapper

    return decorator


def trace_context(context_data: dict[str, Any] = None):
    """
    追踪上下文装饰器

    Args:
        context_data: 上下文数据
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _performance_monitor:
                return await func(*args, **kwargs)

            # 获取当前追踪上下文
            current_span = _performance_monitor._tracer.get_active_span()

            if current_span and context_data:
                # 添加上下文数据到当前Span
                for key, value in context_data.items():
                    current_span.set_tag(f"context.{key}", value)

                current_span.log("添加上下文数据")

            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _performance_monitor:
                return func(*args, **kwargs)

            # 获取当前追踪上下文
            current_span = _performance_monitor._tracer.get_active_span()

            if current_span and context_data:
                # 添加上下文数据到当前Span
                for key, value in context_data.items():
                    current_span.set_tag(f"context.{key}", value)

                current_span.log("添加上下文数据")

            return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
