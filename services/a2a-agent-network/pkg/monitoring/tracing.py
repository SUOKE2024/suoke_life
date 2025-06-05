#!/usr/bin/env python3
"""
分布式追踪模块
Distributed Tracing Module
"""

import asyncio
import functools
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Optional

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
    from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


class TracingManager:
    """分布式追踪管理器"""

    def __init__(self, service_name: str = "a2a-agent-network"):
        """初始化追踪管理器"""
        self.service_name = service_name
        self.tracer_provider: Optional[Any] = None
        self.tracer: Optional[Any] = None
        self._initialized = False

    def initialize(self, config: Dict[str, Any]) -> None:
        """
        初始化分布式追踪

        Args:
            config: 追踪配置
        """
        if self._initialized or not OPENTELEMETRY_AVAILABLE:
            return

        # 创建资源
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": config.get("version", "1.0.0"),
            "deployment.environment": config.get("environment", "development"),
        })

        # 创建追踪提供者
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)

        # 配置 Jaeger 导出器
        jaeger_config = config.get("jaeger", {})
        if jaeger_config.get("enabled", False):
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_config.get("host", "localhost"),
                agent_port=jaeger_config.get("port", 6831),
                collector_endpoint=jaeger_config.get("collector_endpoint"),
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(span_processor)

        # 获取追踪器
        self.tracer = trace.get_tracer(self.service_name)

        # 启用自动仪表化
        if config.get("auto_instrumentation", True):
            self._enable_auto_instrumentation()

        self._initialized = True

    def _enable_auto_instrumentation(self) -> None:
        """启用自动仪表化"""
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        # HTTP 客户端仪表化
        AioHttpClientInstrumentor().instrument()
        
        # 异步 IO 仪表化
        AsyncioInstrumentor().instrument()
        
        # 日志仪表化
        LoggingInstrumentor().instrument()

    @contextmanager
    def start_span(self, name: str, **kwargs):
        """
        启动一个追踪跨度

        Args:
            name: 跨度名称
            **kwargs: 额外的跨度属性
        """
        if not self.tracer or not OPENTELEMETRY_AVAILABLE:
            yield None
            return

        with self.tracer.start_as_current_span(name) as span:
            # 设置跨度属性
            for key, value in kwargs.items():
                span.set_attribute(key, str(value))
            
            yield span

    def trace_function(self, name: Optional[str] = None):
        """
        函数追踪装饰器

        Args:
            name: 跨度名称，默认使用函数名
        """
        def decorator(func):
            span_name = name or f"{func.__module__}.{func.__qualname__}"
            
            if asyncio.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    with self.start_span(span_name) as span:
                        try:
                            result = await func(*args, **kwargs)
                            if span:
                                span.set_attribute("function.result", "success")
                            return result
                        except Exception as e:
                            if span:
                                span.set_attribute("function.result", "error")
                                span.set_attribute("error.message", str(e))
                                span.set_attribute("error.type", type(e).__name__)
                            raise
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    with self.start_span(span_name) as span:
                        try:
                            result = func(*args, **kwargs)
                            if span:
                                span.set_attribute("function.result", "success")
                            return result
                        except Exception as e:
                            if span:
                                span.set_attribute("function.result", "error")
                                span.set_attribute("error.message", str(e))
                                span.set_attribute("error.type", type(e).__name__)
                            raise
                return sync_wrapper
        return decorator

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """
        添加追踪事件

        Args:
            name: 事件名称
            attributes: 事件属性
        """
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes or {})

    def set_attribute(self, key: str, value: Any) -> None:
        """
        设置当前跨度属性

        Args:
            key: 属性键
            value: 属性值
        """
        if not OPENTELEMETRY_AVAILABLE:
            return
            
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, str(value))

    def get_trace_id(self) -> Optional[str]:
        """获取当前追踪ID"""
        if not OPENTELEMETRY_AVAILABLE:
            return None
            
        current_span = trace.get_current_span()
        if current_span:
            return format(current_span.get_span_context().trace_id, '032x')
        return None

    def get_span_id(self) -> Optional[str]:
        """获取当前跨度ID"""
        if not OPENTELEMETRY_AVAILABLE:
            return None
            
        current_span = trace.get_current_span()
        if current_span:
            return format(current_span.get_span_context().span_id, '016x')
        return None


class PerformanceTracker:
    """性能追踪器"""

    def __init__(self, tracing_manager: TracingManager):
        """初始化性能追踪器"""
        self.tracing_manager = tracing_manager
        self._metrics: Dict[str, list] = {}

    @contextmanager
    def track_performance(self, operation: str, **attributes):
        """
        追踪操作性能

        Args:
            operation: 操作名称
            **attributes: 额外属性
        """
        start_time = time.time()
        
        with self.tracing_manager.start_span(f"performance.{operation}") as span:
            try:
                # 设置属性
                if span:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                
                yield
                
                # 记录成功
                duration = time.time() - start_time
                self._record_metric(operation, duration, "success")
                
                if span:
                    span.set_attribute("performance.duration_ms", duration * 1000)
                    span.set_attribute("performance.status", "success")
                
            except Exception as e:
                # 记录失败
                duration = time.time() - start_time
                self._record_metric(operation, duration, "error")
                
                if span:
                    span.set_attribute("performance.duration_ms", duration * 1000)
                    span.set_attribute("performance.status", "error")
                    span.set_attribute("error.message", str(e))
                
                raise

    def _record_metric(self, operation: str, duration: float, status: str) -> None:
        """记录性能指标"""
        if operation not in self._metrics:
            self._metrics[operation] = []
        
        self._metrics[operation].append({
            "duration": duration,
            "status": status,
            "timestamp": time.time(),
        })
        
        # 保持最近1000条记录
        if len(self._metrics[operation]) > 1000:
            self._metrics[operation] = self._metrics[operation][-1000:]

    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """
        获取性能指标

        Args:
            operation: 操作名称，None表示获取所有

        Returns:
            性能指标数据
        """
        if operation:
            return self._calculate_operation_metrics(operation)
        
        return {
            op: self._calculate_operation_metrics(op)
            for op in self._metrics.keys()
        }

    def _calculate_operation_metrics(self, operation: str) -> Dict[str, Any]:
        """计算操作指标"""
        if operation not in self._metrics:
            return {}
        
        records = self._metrics[operation]
        if not records:
            return {}
        
        durations = [r["duration"] for r in records]
        success_count = len([r for r in records if r["status"] == "success"])
        error_count = len([r for r in records if r["status"] == "error"])
        
        return {
            "total_count": len(records),
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / len(records) if records else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "p50_duration": self._percentile(durations, 0.5),
            "p90_duration": self._percentile(durations, 0.9),
            "p95_duration": self._percentile(durations, 0.95),
            "p99_duration": self._percentile(durations, 0.99),
        }

    def _percentile(self, data: list, percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]


# 全局追踪管理器实例
tracing_manager = TracingManager()
performance_tracker = PerformanceTracker(tracing_manager)


def initialize_tracing(config: Dict[str, Any]) -> None:
    """初始化全局追踪"""
    tracing_manager.initialize(config)


def trace(name: Optional[str] = None):
    """追踪装饰器"""
    return tracing_manager.trace_function(name)


def track_performance(operation: str, **attributes):
    """性能追踪装饰器"""
    return performance_tracker.track_performance(operation, **attributes) 