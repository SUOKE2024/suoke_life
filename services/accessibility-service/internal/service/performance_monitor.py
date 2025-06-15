#!/usr/bin/env python

"""
性能监控和链路追踪组件
提供请求追踪、性能指标收集、分布式追踪和性能分析功能
"""

import asyncio
import contextvars
import functools
import logging
import threading
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)

# 上下文变量用于追踪
trace_context: contextvars.ContextVar[Optional["TraceContext"]] = (
    contextvars.ContextVar("trace_context", default=None)
)


class SpanKind(Enum):
    """Span类型"""

    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    INTERNAL = "internal"


class SpanStatus(Enum):
    """Span状态"""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TraceContext:
    """追踪上下文"""

    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    baggage: dict[str, str] = field(default_factory=dict)

    def child_context(self) -> "TraceContext":
        """创建子上下文"""
        return TraceContext(
            trace_id=self.trace_id,
            span_id=self._generate_span_id(),
            parent_span_id=self.span_id,
            baggage=self.baggage.copy(),
        )

    @staticmethod
    def _generate_span_id() -> str:
        """生成Span ID"""
        return str(uuid.uuid4())[:16]


@dataclass
class Span:
    """追踪Span"""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    operation_name: str
    kind: SpanKind
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration: float | None = None
    status: SpanStatus = SpanStatus.OK
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)

    def finish(self, status: SpanStatus = SpanStatus.OK):
        """结束Span"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status

    def set_tag(self, key: str, value: Any):
        """设置标签"""
        self.tags[key] = value

    def log(self, message: str, level: str = "info", **kwargs):
        """记录日志"""
        log_entry = {
            "timestamp": time.time(),
            "level": level,
            "message": message,
            **kwargs,
        }
        self.logs.append(log_entry)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "kind": self.kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "status": self.status.value,
            "tags": self.tags,
            "logs": self.logs,
        }


@dataclass
class PerformanceMetric:
    """性能指标"""

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)
    unit: str = ""


class PerformanceCollector:
    """性能指标收集器"""

    def __init__(self, max_history: int = 10000):
        self._metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = defaultdict(float)
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def record_counter(self, name: str, value: float = 1, tags: dict[str, str] = None):
        """记录计数器"""
        with self._lock:
            key = self._make_key(name, tags)
            self._counters[key] += value
            self._add_metric(name, value, tags, "count")

    def record_gauge(self, name: str, value: float, tags: dict[str, str] = None):
        """记录仪表盘"""
        with self._lock:
            key = self._make_key(name, tags)
            self._gauges[key] = value
            self._add_metric(name, value, tags, "gauge")

    def record_histogram(self, name: str, value: float, tags: dict[str, str] = None):
        """记录直方图"""
        with self._lock:
            key = self._make_key(name, tags)
            self._histograms[key].append(value)
            # 保持最近1000个值
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
            self._add_metric(name, value, tags, "histogram")

    def record_timer(self, name: str, duration: float, tags: dict[str, str] = None):
        """记录计时器"""
        self.record_histogram(f"{name}_duration", duration, tags)

    def _make_key(self, name: str, tags: dict[str, str] = None) -> str:
        """生成指标键"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}{{{tag_str}}}"

    def _add_metric(
        self, name: str, value: float, tags: dict[str, str] = None, unit: str = ""
    ):
        """添加指标"""
        metric = PerformanceMetric(name=name, value=value, tags=tags or {}, unit=unit)
        self._metrics[name].append(metric)

    def get_metrics(self, name: str = None) -> dict[str, Any]:
        """获取指标"""
        with self._lock:
            if name:
                return {
                    "name": name,
                    "history": list(self._metrics.get(name, [])),
                    "current_value": self._gauges.get(name, 0),
                    "total_count": self._counters.get(name, 0),
                }

            result = {}
            for metric_name in self._metrics:
                result[metric_name] = {
                    "history": list(self._metrics[metric_name])[-100:],  # 最近100个值
                    "current_value": self._gauges.get(metric_name, 0),
                    "total_count": self._counters.get(metric_name, 0),
                }

            return result

    def get_histogram_stats(
        self, name: str, tags: dict[str, str] = None
    ) -> dict[str, float]:
        """获取直方图统计"""
        key = self._make_key(name, tags)
        values = self._histograms.get(key, [])

        if not values:
            return {}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)],
            "p90": sorted_values[int(count * 0.9)],
            "p95": sorted_values[int(count * 0.95)],
            "p99": sorted_values[int(count * 0.99)],
        }


class Tracer:
    """分布式追踪器"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._spans: dict[str, Span] = {}
        self._active_spans: dict[str, Span] = {}
        self._span_processors: list[Callable] = []
        self._lock = threading.Lock()

    def start_span(
        self,
        operation_name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent_context: TraceContext = None,
    ) -> Span:
        """开始一个新的Span"""
        # 获取当前上下文或创建新的
        current_context = parent_context or trace_context.get()

        if current_context:
            # 创建子Span
            new_context = current_context.child_context()
            span = Span(
                trace_id=new_context.trace_id,
                span_id=new_context.span_id,
                parent_span_id=new_context.parent_span_id,
                operation_name=operation_name,
                kind=kind,
            )
        else:
            # 创建根Span
            trace_id = str(uuid.uuid4())
            span_id = TraceContext._generate_span_id()
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=None,
                operation_name=operation_name,
                kind=kind,
            )

            # 创建新的追踪上下文
            new_context = TraceContext(trace_id=trace_id, span_id=span_id)

        # 设置服务标签
        span.set_tag("service.name", self.service_name)
        span.set_tag("span.kind", kind.value)

        # 保存Span
        with self._lock:
            self._spans[span.span_id] = span
            self._active_spans[span.span_id] = span

        # 设置上下文
        trace_context.set(new_context)

        return span

    def finish_span(self, span: Span, status: SpanStatus = SpanStatus.OK):
        """结束Span"""
        span.finish(status)

        with self._lock:
            if span.span_id in self._active_spans:
                del self._active_spans[span.span_id]

        # 处理Span
        for processor in self._span_processors:
            try:
                processor(span)
            except Exception as e:
                logger.error(f"Span处理器异常: {e!s}")

    def get_active_span(self) -> Span | None:
        """获取当前活跃的Span"""
        current_context = trace_context.get()
        if current_context:
            return self._active_spans.get(current_context.span_id)
        return None

    def add_span_processor(self, processor: Callable):
        """添加Span处理器"""
        self._span_processors.append(processor)

    def get_trace(self, trace_id: str) -> list[Span]:
        """获取完整的追踪链"""
        with self._lock:
            return [span for span in self._spans.values() if span.trace_id == trace_id]

    def get_spans(self, limit: int = 100) -> list[Span]:
        """获取最近的Spans"""
        with self._lock:
            spans = list(self._spans.values())
            return sorted(spans, key=lambda x: x.start_time, reverse=True)[:limit]


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.service_name = config.get("service", {}).get(
            "name", "accessibility-service"
        )

        self._collector = PerformanceCollector()
        self._tracer = Tracer(self.service_name)
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None

        # 设置Span处理器
        self._tracer.add_span_processor(self._process_span)

        # 启动监控
        asyncio.create_task(self._start_monitoring())

    async def _start_monitoring(self) -> None:
        """启动监控"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("性能监控已启动")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self._monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(30)  # 每30秒收集一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"性能监控异常: {e!s}")
                await asyncio.sleep(30)

    async def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            import psutil

            # CPU使用率
            cpu_percent = psutil.cpu_percent()
            self._collector.record_gauge(
                "system.cpu.usage", cpu_percent, {"unit": "percent"}
            )

            # 内存使用情况
            memory = psutil.virtual_memory()
            self._collector.record_gauge(
                "system.memory.usage", memory.percent, {"unit": "percent"}
            )
            self._collector.record_gauge(
                "system.memory.available", memory.available, {"unit": "bytes"}
            )

            # 进程信息
            process = psutil.Process()
            self._collector.record_gauge(
                "process.cpu.usage", process.cpu_percent(), {"unit": "percent"}
            )
            self._collector.record_gauge(
                "process.memory.rss", process.memory_info().rss, {"unit": "bytes"}
            )
            self._collector.record_gauge(
                "process.threads", process.num_threads(), {"unit": "count"}
            )

        except Exception as e:
            logger.error(f"收集系统指标失败: {e!s}")

    def _process_span(self, span: Span):
        """处理Span"""
        # 记录性能指标
        if span.duration:
            self._collector.record_timer(
                "span.duration",
                span.duration * 1000,  # 转换为毫秒
                {
                    "operation": span.operation_name,
                    "status": span.status.value,
                    "kind": span.kind.value,
                },
            )

        # 记录Span计数
        self._collector.record_counter(
            "span.count",
            1,
            {
                "operation": span.operation_name,
                "status": span.status.value,
                "kind": span.kind.value,
            },
        )

        # 如果是错误状态，记录错误计数
        if span.status == SpanStatus.ERROR:
            self._collector.record_counter(
                "span.errors", 1, {"operation": span.operation_name}
            )

    def trace(self, operation_name: str, kind: SpanKind = SpanKind.INTERNAL):
        """追踪装饰器"""

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                span = self._tracer.start_span(operation_name, kind)
                try:
                    # 记录函数参数
                    span.set_tag("function.name", func.__name__)
                    span.set_tag("function.module", func.__module__)

                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    # 记录成功信息
                    span.set_tag("success", True)
                    span.set_tag("duration", duration)

                    self._tracer.finish_span(span, SpanStatus.OK)
                    return result

                except Exception as e:
                    # 记录错误信息
                    span.set_tag("error", True)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.log(f"异常: {e!s}", level="error")

                    self._tracer.finish_span(span, SpanStatus.ERROR)
                    raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                span = self._tracer.start_span(operation_name, kind)
                try:
                    # 记录函数参数
                    span.set_tag("function.name", func.__name__)
                    span.set_tag("function.module", func.__module__)

                    start_time = time.time()
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    # 记录成功信息
                    span.set_tag("success", True)
                    span.set_tag("duration", duration)

                    self._tracer.finish_span(span, SpanStatus.OK)
                    return result

                except Exception as e:
                    # 记录错误信息
                    span.set_tag("error", True)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.log(f"异常: {e!s}", level="error")

                    self._tracer.finish_span(span, SpanStatus.ERROR)
                    raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def timer(self, name: str, tags: dict[str, str] = None):
        """计时器装饰器"""

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self._collector.record_timer(name, duration * 1000, tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    error_tags = (tags or {}).copy()
                    error_tags["error"] = "true"
                    self._collector.record_timer(name, duration * 1000, error_tags)
                    raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self._collector.record_timer(name, duration * 1000, tags)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    error_tags = (tags or {}).copy()
                    error_tags["error"] = "true"
                    self._collector.record_timer(name, duration * 1000, error_tags)
                    raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def counter(self, name: str, tags: dict[str, str] = None):
        """计数器装饰器"""

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    result = await func(*args, **kwargs)
                    self._collector.record_counter(name, 1, tags)
                    return result
                except Exception as e:
                    error_tags = (tags or {}).copy()
                    error_tags["error"] = "true"
                    self._collector.record_counter(name, 1, error_tags)
                    raise

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    result = func(*args, **kwargs)
                    self._collector.record_counter(name, 1, tags)
                    return result
                except Exception as e:
                    error_tags = (tags or {}).copy()
                    error_tags["error"] = "true"
                    self._collector.record_counter(name, 1, error_tags)
                    raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def get_metrics(self) -> dict[str, Any]:
        """获取性能指标"""
        return self._collector.get_metrics()

    def get_traces(self, trace_id: str = None, limit: int = 100) -> dict[str, Any]:
        """获取追踪信息"""
        if trace_id:
            spans = self._tracer.get_trace(trace_id)
            return {"trace_id": trace_id, "spans": [span.to_dict() for span in spans]}
        else:
            spans = self._tracer.get_spans(limit)
            return {"spans": [span.to_dict() for span in spans]}

    def get_performance_summary(self) -> dict[str, Any]:
        """获取性能摘要"""
        metrics = self._collector.get_metrics()

        # 计算关键指标
        summary = {
            "service_name": self.service_name,
            "timestamp": time.time(),
            "metrics": {},
        }

        # 请求统计
        if "span.count" in metrics:
            span_count = metrics["span.count"]["total_count"]
            summary["metrics"]["total_requests"] = span_count

        # 错误率
        if "span.errors" in metrics and "span.count" in metrics:
            error_count = metrics["span.errors"]["total_count"]
            total_count = metrics["span.count"]["total_count"]
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            summary["metrics"]["error_rate_percent"] = error_rate

        # 响应时间统计
        duration_stats = self._collector.get_histogram_stats("span.duration")
        if duration_stats:
            summary["metrics"]["response_time_ms"] = duration_stats

        return summary

    async def stop_monitoring(self) -> None:
        """停止监控"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("性能监控已停止")

    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("开始清理性能监控器")
        await self.stop_monitoring()
        logger.info("性能监控器清理完成")
