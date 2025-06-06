"""
metrics - 索克生活项目模块
"""

from collections.abc import Callable
from functools import wraps
from prometheus_client import (
from typing import Any, Optional, TypeVar
import asyncio
import functools
import time

#!/usr/bin/env python3

"""
老克智能体服务 - 指标收集器
提供Prometheus指标收集和监控功能
"""


    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
)

# 全局指标收集器实例
_metrics_collector: Optional['MetricsCollector'] = None

# 全局指标函数
_increment_counter_fn: Callable[[str, dict[str, Any] | None], None] | None = None
_observe_latency_fn: Callable[[str, float], None] | None = None

# 类型变量
F = TypeVar('F', bound=Callable[..., Any])

def get_metrics_collector() -> 'MetricsCollector':
    """获取全局指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector("laoke_service")
    return _metrics_collector

def set_metrics_collector(collector: 'MetricsCollector') -> None:
    """设置全局指标收集器实例"""
    global _metrics_collector
    _metrics_collector = collector

class MetricsCollector:
    """指标收集器"""

    def __init__(self, namespace: str):
        self.namespace = namespace
        self.registry = CollectorRegistry()

        # 请求相关指标
        self.request_count = Counter(
            'requests_total',
            'Total number of requests',
            ['type', 'status'],
            registry=self.registry
        )

        self.request_latency = Histogram(
            'request_duration_seconds',
            'Request latency in seconds',
            ['type'],
            registry=self.registry
        )

        # 模型调用指标
        self.model_calls = Counter(
            'model_calls_total',
            'Total number of model calls',
            ['model', 'status'],
            registry=self.registry
        )

        self.model_latency = Histogram(
            'model_call_duration_seconds',
            'Model call latency in seconds',
            ['model', 'query_type'],
            registry=self.registry
        )

        # 系统指标
        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active sessions',
            registry=self.registry
        )

        # 知识库指标
        self.knowledge_queries = Counter(
            'knowledge_queries_total',
            'Total number of knowledge queries',
            ['status'],
            registry=self.registry
        )

        # 社区指标
        self.community_actions = Counter(
            'community_actions_total',
            'Total number of community actions',
            ['action', 'status'],
            registry=self.registry
        )

        # 错误指标
        self.errors = Counter(
            'errors_total',
            'Total number of errors',
            ['type'],
            registry=self.registry
        )

        # 内部计数器（用于计算成功率等）
        self._internal_counters: dict[str, int] = {}

    def increment_request_count(self, request_type: str, status: str = "success") -> None:
        """增加请求计数"""
        self.request_count.labels(type=request_type, status=status).inc()

        # 更新内部计数器
        key = f"request_{request_type}_{status}"
        self._internal_counters[key] = self._internal_counters.get(key, 0) + 1

    def record_request_latency(self, request_type: str, seconds: float) -> None:
        """记录请求延迟"""
        self.request_latency.labels(type=request_type).observe(seconds)

    def increment_model_call(self, model: str, status: str = "success") -> None:
        """增加模型调用计数"""
        self.model_calls.labels(model=model, status=status).inc()

        # 更新内部计数器
        key = f"model_{model}_{status}"
        self._internal_counters[key] = self._internal_counters.get(key, 0) + 1

    def record_model_latency(self, model: str, query_type: str, seconds: float) -> None:
        """记录模型调用延迟"""
        self.model_latency.labels(model=model, query_type=query_type).observe(seconds)

    def update_active_sessions(self, count: int) -> None:
        """更新活跃会话数"""
        self.active_sessions.set(count)

    def increment_knowledge_query(self, status: str = "success") -> None:
        """增加知识查询计数"""
        self.knowledge_queries.labels(status=status).inc()

    def increment_community_action(self, action: str, status: str = "success") -> None:
        """增加社区动作计数"""
        self.community_actions.labels(action=action, status=status).inc()

    def increment_error(self, error_type: str) -> None:
        """增加错误计数"""
        self.errors.labels(type=error_type).inc()

    def collect_metrics(self) -> dict[str, Any]:
        """收集所有指标"""
        metrics = {}

        # 收集Prometheus指标
        for metric_family in self.registry.collect():
            for sample in metric_family.samples:
                metrics[sample.name] = sample.value

        # 计算成功率
        metrics.update({
            'request_success_rate': self._calculate_success_rate(self._internal_counters),
            'model_success_rate': self._calculate_model_success_rate(),
            'knowledge_success_rate': self._calculate_knowledge_success_rate(),
        })

        return metrics

    def reset_counters(self) -> None:
        """重置内部计数器"""
        self._internal_counters.clear()

    def _calculate_success_rate(self, metrics: dict[str, int]) -> float:
        """计算成功率"""
        total_requests = sum(v for k, v in metrics.items() if k.startswith('request_'))
        successful_requests = sum(v for k, v in metrics.items() if k.endswith('_success'))

        if total_requests == 0:
            return 1.0

        return successful_requests / total_requests

    def _calculate_model_success_rate(self) -> float:
        """计算模型调用成功率"""
        total_calls = sum(v for k, v in self._internal_counters.items() if k.startswith('model_'))
        successful_calls = sum(v for k, v in self._internal_counters.items() if k.startswith('model_') and k.endswith('_success'))

        if total_calls == 0:
            return 1.0

        return successful_calls / total_calls

    def _calculate_knowledge_success_rate(self) -> float:
        """计算知识查询成功率"""
        total_queries = sum(v for k, v in self._internal_counters.items() if k.startswith('knowledge_'))
        successful_queries = sum(v for k, v in self._internal_counters.items() if k.startswith('knowledge_') and k.endswith('_success'))

        if total_queries == 0:
            return 1.0

        return successful_queries / total_queries

    def measure_execution_time(self, metric_name: str) -> Callable[[F], F]:
        """
        测量函数执行时间的装饰器

        Args:
            metric_name: 指标名称

        Returns:
            Callable: 装饰器函数
        """
        def decorator(func: F) -> F:
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        duration = time.time() - start_time
                        self.request_latency.labels(type=metric_name).observe(duration)
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        self.request_latency.labels(type=f"{metric_name}_error").observe(duration)
                        raise e
                return async_wrapper  # type: ignore
            else:
                @wraps(func)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        duration = time.time() - start_time
                        self.request_latency.labels(type=metric_name).observe(duration)
                        return result
                    except Exception as e:
                        duration = time.time() - start_time
                        self.request_latency.labels(type=f"{metric_name}_error").observe(duration)
                        raise e
                return wrapper  # type: ignore
        return decorator

def track_request_metrics(request_type: str) -> Callable[[F], F]:
    """
    请求指标跟踪装饰器

    Args:
        request_type: 请求类型

    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                metrics.increment_request_count(request_type, "success")
                return result
            except Exception as e:
                metrics.increment_request_count(request_type, "error")
                metrics.increment_error(type(e).__name__)
                raise
            finally:
                elapsed_time = time.time() - start_time
                metrics.record_request_latency(request_type, elapsed_time)

        return wrapper  # type: ignore
    return decorator

def track_llm_metrics(model: str, query_type: str) -> Callable[[F], F]:
    """
    LLM调用指标跟踪装饰器

    Args:
        model: 模型名称
        query_type: 查询类型

    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            metrics = get_metrics_collector()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                metrics.increment_model_call(model, "success")
                return result
            except Exception as e:
                metrics.increment_model_call(model, "error")
                metrics.increment_error(f"llm_{type(e).__name__}")
                raise
            finally:
                elapsed_time = time.time() - start_time
                metrics.record_model_latency(model, query_type, elapsed_time)

        return wrapper  # type: ignore
    return decorator

def init_metrics(increment_counter_fn: Callable[[str, dict[str, Any] | None], None], observe_latency_fn: Callable[[str, float], None]) -> None:
    """
    初始化指标函数

    参数:
        increment_counter_fn: 增加计数器的函数
        observe_latency_fn: 观察延迟的函数
    """
    global _increment_counter_fn, _observe_latency_fn
    _increment_counter_fn = increment_counter_fn
    _observe_latency_fn = observe_latency_fn


def increment_counter(name: str, labels: dict[str, Any] | None = None) -> None:
    """
    增加计数器

    参数:
        name: 计数器名称
        labels: 标签值字典（可选）
    """
    if _increment_counter_fn:
        _increment_counter_fn(name, labels)


def observe_latency(name: str, value_ms: float) -> None:
    """
    观察延迟

    参数:
        name: 延迟指标名称
        value_ms: 延迟值（毫秒）
    """
    if _observe_latency_fn:
        _observe_latency_fn(name, value_ms)


def timed_function(metric_name: str) -> Callable[[F], F]:
    """
    计时函数装饰器
    用于测量函数执行时间并记录指标

    参数:
        metric_name: 指标名称

    返回:
        装饰器函数
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    raise e
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    raise e
            return wrapper  # type: ignore
    return decorator


def counted_function(success_metric: str, error_metric: str | None = None) -> Callable[[F], F]:
    """
    计数函数装饰器
    用于计数函数调用次数并记录成功/失败

    参数:
        success_metric: 成功指标名称
        error_metric: 失败指标名称（可选）

    返回:
        装饰器函数
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    result = await func(*args, **kwargs)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    result = func(*args, **kwargs)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return wrapper  # type: ignore
    return decorator


def timed_and_counted_function(
    metric_name: str,
    success_metric: str | None = None,
    error_metric: str | None = None
) -> Callable[[F], F]:
    """
    计时和计数函数装饰器
    同时测量执行时间和计数调用次数

    参数:
        metric_name: 时间指标名称
        success_metric: 成功计数指标名称（可选）
        error_metric: 失败计数指标名称（可选）

    返回:
        装饰器函数
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    if success_metric:
                        increment_counter(success_metric)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    if success_metric:
                        increment_counter(success_metric)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return wrapper  # type: ignore
    return decorator
