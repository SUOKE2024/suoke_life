#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 指标收集工具
提供服务指标收集和跟踪
"""

import time
import logging
import functools
from typing import Dict, Any, Callable, Optional
import threading
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import asyncio
import inspect

logger = logging.getLogger(__name__)

# 全局指标收集器实例
_instance = None
_lock = threading.Lock()

# 全局变量，存储引用
_increment_counter_fn = None
_observe_latency_fn = None

def get_metrics_collector() -> 'MetricsCollector':
    """
    获取指标收集器的单例实例
    
    Returns:
        MetricsCollector: 指标收集器实例
    """
    global _instance
    with _lock:
        if _instance is None:
            _instance = MetricsCollector("laoke_service")
    return _instance

class MetricsCollector:
    """指标收集器，用于收集服务性能指标"""
    
    def __init__(self, namespace: str):
        """
        初始化指标收集器
        
        Args:
            namespace: 指标命名空间
        """
        self.namespace = namespace
        
        # 服务信息
        self.info = Info(
            f"{namespace}_info", 
            "Service information"
        )
        self.info.info({'service': 'laoke_service'})
        
        # 请求计数器
        self.request_counter = Counter(
            f"{namespace}_requests_total", 
            "Total number of requests",
            ['type', 'status']
        )
        
        # 请求延迟直方图
        self.request_latency = Histogram(
            f"{namespace}_request_latency_seconds", 
            "Request latency in seconds",
            ['type'],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
        )
        
        # 模型调用计数器
        self.model_call_counter = Counter(
            f"{namespace}_model_calls_total", 
            "Total number of model calls",
            ['model', 'status']
        )
        
        # 模型延迟直方图
        self.model_latency = Histogram(
            f"{namespace}_model_latency_seconds", 
            "Model latency in seconds",
            ['model', 'query_type'],
            buckets=(0.1, 0.5, 1, 2, 5, 10, 20, 30, 60, 120)
        )
        
        # 活跃会话数量
        self.active_sessions = Gauge(
            f"{namespace}_active_sessions", 
            "Number of active sessions"
        )
        
        # 知识库查询计数器
        self.knowledge_query_counter = Counter(
            f"{namespace}_knowledge_queries_total", 
            "Total number of knowledge queries",
            ['status']
        )
        
        # 社区相关计数器
        self.community_action_counter = Counter(
            f"{namespace}_community_actions_total", 
            "Total number of community actions",
            ['action', 'status']
        )
        
        # 错误计数器
        self.error_counter = Counter(
            f"{namespace}_errors_total", 
            "Total number of errors",
            ['type']
        )
        
        logger.info(f"指标收集器初始化完成，命名空间: {namespace}")
    
    def increment_request_count(self, request_type: str, status: str = "success") -> None:
        """
        增加请求计数
        
        Args:
            request_type: 请求类型
            status: 请求状态（success/error）
        """
        self.request_counter.labels(type=request_type, status=status).inc()
    
    def record_request_latency(self, request_type: str, seconds: float) -> None:
        """
        记录请求延迟
        
        Args:
            request_type: 请求类型
            seconds: 延迟时间（秒）
        """
        self.request_latency.labels(type=request_type).observe(seconds)
    
    def increment_model_call(self, model: str, status: str = "success") -> None:
        """
        增加模型调用计数
        
        Args:
            model: 模型名称
            status: 调用状态（success/error）
        """
        self.model_call_counter.labels(model=model, status=status).inc()
    
    def record_model_latency(self, model: str, query_type: str, seconds: float) -> None:
        """
        记录模型调用延迟
        
        Args:
            model: 模型名称
            query_type: 查询类型
            seconds: 延迟时间（秒）
        """
        self.model_latency.labels(model=model, query_type=query_type).observe(seconds)
    
    def update_active_sessions(self, count: int) -> None:
        """
        更新活跃会话数量
        
        Args:
            count: 会话数量
        """
        self.active_sessions.set(count)
    
    def increment_knowledge_query(self, status: str = "success") -> None:
        """
        增加知识库查询计数
        
        Args:
            status: 查询状态（success/error）
        """
        self.knowledge_query_counter.labels(status=status).inc()
    
    def increment_community_action(self, action: str, status: str = "success") -> None:
        """
        增加社区动作计数
        
        Args:
            action: 动作类型
            status: 动作状态（success/error）
        """
        self.community_action_counter.labels(action=action, status=status).inc()
    
    def increment_error(self, error_type: str) -> None:
        """
        增加错误计数
        
        Args:
            error_type: 错误类型
        """
        self.error_counter.labels(type=error_type).inc()
    
    def collect_metrics(self) -> Dict[str, Any]:
        """
        收集所有指标的当前值
        
        Returns:
            Dict[str, Any]: 指标数据字典
        """
        # 这里只能获取简单指标的当前值
        # Prometheus Counter/Histogram等需要通过API端点暴露
        return {
            "active_sessions": self.active_sessions._value.get(),
            "request_counts": {
                "total": sum(self.request_counter._metrics.values()),
                "by_type": {
                    k[0]: v 
                    for k, v in self.request_counter._metrics.items() 
                    if k[1] == "success"
                }
            },
            "model_calls": {
                "total": sum(self.model_call_counter._metrics.values()),
                "success_rate": self._calculate_success_rate(self.model_call_counter._metrics)
            },
            "errors": {
                "total": sum(self.error_counter._metrics.values()),
                "by_type": {k[0]: v for k, v in self.error_counter._metrics.items()}
            }
        }
    
    def reset_counters(self) -> None:
        """重置计数器类型的指标（用于测试）"""
        # 注意：这在生产环境中通常不应该使用
        # 仅用于测试或特殊情况
        for metric_name in dir(self):
            metric = getattr(self, metric_name)
            if isinstance(metric, Counter) and hasattr(metric, '_metrics'):
                metric._metrics.clear()
    
    def _calculate_success_rate(self, metrics: Dict) -> float:
        """
        计算成功率
        
        Args:
            metrics: 指标数据字典
            
        Returns:
            float: 成功率（0-1之间）
        """
        success_count = 0
        total_count = 0
        
        for key, value in metrics.items():
            total_count += value
            if key[-1] == "success":
                success_count += value
        
        if total_count == 0:
            return 1.0  # 如果没有调用，默认为100%成功率
        
        return success_count / total_count

    def measure_execution_time(self, metric_name: str) -> Callable:
        """
        测量函数执行时间的装饰器
        
        Args:
            metric_name: 指标名称
            
        Returns:
            Callable: 装饰器函数
        """
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                @wraps(func)
                async def async_wrapper(*args, **kwargs):
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
                return async_wrapper
            else:
                @wraps(func)
                def wrapper(*args, **kwargs):
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
                return wrapper
        return decorator

def track_request_metrics(request_type: str) -> Callable:
    """
    请求指标跟踪装饰器
    
    Args:
        request_type: 请求类型
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
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
        
        return wrapper
    return decorator

def track_llm_metrics(model: str, query_type: str) -> Callable:
    """
    LLM调用指标跟踪装饰器
    
    Args:
        model: 模型名称
        query_type: 查询类型
        
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
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
        
        return wrapper
    return decorator

def init_metrics(increment_counter_fn, observe_latency_fn):
    """
    初始化指标函数
    
    参数:
        increment_counter_fn: 增加计数器的函数
        observe_latency_fn: 观察延迟的函数
    """
    global _increment_counter_fn, _observe_latency_fn
    _increment_counter_fn = increment_counter_fn
    _observe_latency_fn = observe_latency_fn


def increment_counter(name: str, labels: Optional[Dict[str, Any]] = None):
    """
    增加计数器
    
    参数:
        name: 计数器名称
        labels: 标签值字典（可选）
    """
    if _increment_counter_fn:
        _increment_counter_fn(name, labels)


def observe_latency(name: str, value_ms: float):
    """
    观察延迟
    
    参数:
        name: 延迟指标名称
        value_ms: 延迟值（毫秒）
    """
    if _observe_latency_fn:
        _observe_latency_fn(name, value_ms)


def timed_function(metric_name: str):
    """
    计时函数装饰器
    用于测量函数执行时间并记录指标
    
    参数:
        metric_name: 指标名称
        
    返回:
        装饰器函数
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    observe_latency(metric_name, (time.time() - start_time) * 1000)
                    return result
                except Exception as e:
                    observe_latency(f"{metric_name}_error", (time.time() - start_time) * 1000)
                    raise e
            return wrapper
    return decorator


def counted_function(success_metric: str, error_metric: Optional[str] = None):
    """
    计数函数装饰器
    用于计数函数调用次数并记录成功/失败
    
    参数:
        success_metric: 成功指标名称
        error_metric: 失败指标名称（可选）
        
    返回:
        装饰器函数
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    if error_metric:
                        increment_counter(error_metric)
                    raise e
            return wrapper
    return decorator


def timed_and_counted_function(
    metric_name: str, 
    success_metric: Optional[str] = None, 
    error_metric: Optional[str] = None
):
    """
    计时和计数函数装饰器
    结合timed_function和counted_function的功能
    
    参数:
        metric_name: 指标名称（用于计时）
        success_metric: 成功指标名称（用于计数，可选）
        error_metric: 失败指标名称（用于计数，可选）
        
    返回:
        装饰器函数
    """
    success_metric = success_metric or f"{metric_name}_success"
    error_metric = error_metric or f"{metric_name}_error"
    
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    observe_latency(metric_name, duration_ms)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    observe_latency(f"{metric_name}_error", duration_ms)
                    increment_counter(error_metric)
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    observe_latency(metric_name, duration_ms)
                    increment_counter(success_metric)
                    return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    observe_latency(f"{metric_name}_error", duration_ms)
                    increment_counter(error_metric)
                    raise e
            return wrapper
    return decorator