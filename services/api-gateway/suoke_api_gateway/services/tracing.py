"""
tracing - 索克生活项目模块
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.status import Status, StatusCode
from typing import Dict, Any, Optional, List, Callable
import time
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分布式追踪服务

集成 Jaeger 和 OpenTelemetry，提供分布式追踪功能。
"""




logger = get_logger(__name__)
settings = get_settings()


class SpanKind(Enum):
    """Span 类型"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class SpanContext:
    """Span 上下文"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = None
    
    def __post_init__(self):
        if self.baggage is None:
            self.baggage = {}


@dataclass
class SpanData:
    """Span 数据"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float]
    duration: Optional[float]
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]
    status: str
    kind: str
    
    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time


class TracingService:
    """分布式追踪服务"""
    
    def __init__(self):
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self.jaeger_exporter: Optional[JaegerExporter] = None
        
        # 本地存储（用于测试和调试）
        self.spans: Dict[str, SpanData] = {}
        self.traces: Dict[str, List[str]] = {}  # trace_id -> span_ids
        
        # 配置
        self.service_name = settings.service_name or "suoke-api-gateway"
        self.jaeger_endpoint = settings.jaeger_endpoint or "http://localhost:14268/api/traces"
        self.enabled = getattr(settings, 'tracing_enabled', True)
        
        if self.enabled:
            self._setup_tracing()
    
    def _setup_tracing(self) -> None:
        """设置分布式追踪"""
        try:
            # 创建资源
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": getattr(settings, 'environment', 'development'),
            })
            
            # 创建 TracerProvider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # 创建 Jaeger 导出器
            self.jaeger_exporter = JaegerExporter(
                agent_host_name=getattr(settings, 'jaeger_agent_host', 'localhost'),
                agent_port=getattr(settings, 'jaeger_agent_port', 6831),
                collector_endpoint=self.jaeger_endpoint,
            )
            
            # 创建 Span 处理器
            span_processor = BatchSpanProcessor(self.jaeger_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # 创建 Tracer
            self.tracer = trace.get_tracer(__name__)
            
            # 自动仪表化
            self._setup_auto_instrumentation()
            
            logger.info(
                "Distributed tracing initialized",
                service_name=self.service_name,
                jaeger_endpoint=self.jaeger_endpoint,
            )
            
        except Exception as e:
            logger.error("Failed to setup distributed tracing", error=str(e))
            self.enabled = False
    
    def _setup_auto_instrumentation(self) -> None:
        """设置自动仪表化"""
        try:
            # FastAPI 自动仪表化
            FastAPIInstrumentor.instrument()
            
            # Requests 自动仪表化
            RequestsInstrumentor().instrument()
            
            # Redis 自动仪表化
            RedisInstrumentor().instrument()
            
            logger.info("Auto-instrumentation setup completed")
            
        except Exception as e:
            logger.warning("Failed to setup auto-instrumentation", error=str(e))
    
    def start_span(
        self,
        operation_name: str,
        parent_context: Optional[SpanContext] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None,
    ) -> SpanContext:
        """开始一个新的 Span"""
        if not self.enabled or not self.tracer:
            # 返回模拟的 SpanContext
            return SpanContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4()),
                parent_span_id=parent_context.span_id if parent_context else None,
            )
        
        try:
            # 创建 Span
            with self.tracer.start_as_current_span(
                operation_name,
                kind=getattr(trace.SpanKind, kind.value.upper(), trace.SpanKind.INTERNAL),
            ) as span:
                # 设置标签
                if tags:
                    for key, value in tags.items():
                        span.set_attribute(key, str(value))
                
                # 获取 Span 上下文
                span_context = span.get_span_context()
                
                context = SpanContext(
                    trace_id=format(span_context.trace_id, '032x'),
                    span_id=format(span_context.span_id, '016x'),
                    parent_span_id=parent_context.span_id if parent_context else None,
                )
                
                # 存储到本地（用于查询）
                span_data = SpanData(
                    trace_id=context.trace_id,
                    span_id=context.span_id,
                    parent_span_id=context.parent_span_id,
                    operation_name=operation_name,
                    start_time=time.time(),
                    end_time=None,
                    duration=None,
                    tags=tags or {},
                    logs=[],
                    status="started",
                    kind=kind.value,
                )
                
                self.spans[context.span_id] = span_data
                
                # 添加到 trace
                if context.trace_id not in self.traces:
                    self.traces[context.trace_id] = []
                self.traces[context.trace_id].append(context.span_id)
                
                return context
        
        except Exception as e:
            logger.error("Failed to start span", operation_name=operation_name, error=str(e))
            return SpanContext(
                trace_id=str(uuid.uuid4()),
                span_id=str(uuid.uuid4()),
                parent_span_id=parent_context.span_id if parent_context else None,
            )
    
    def finish_span(
        self,
        span_context: SpanContext,
        status: StatusCode = StatusCode.OK,
        error: Optional[Exception] = None,
    ) -> None:
        """结束 Span"""
        if not self.enabled:
            return
        
        try:
            # 更新本地存储的 Span 数据
            span_data = self.spans.get(span_context.span_id)
            if span_data:
                span_data.end_time = time.time()
                span_data.duration = span_data.end_time - span_data.start_time
                span_data.status = "finished" if status == StatusCode.OK else "error"
                
                if error:
                    span_data.tags["error"] = True
                    span_data.tags["error.message"] = str(error)
                    span_data.tags["error.type"] = type(error).__name__
            
            # 如果有当前活跃的 Span，设置状态
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_status(Status(status))
                
                if error:
                    current_span.record_exception(error)
                    current_span.set_attribute("error", True)
        
        except Exception as e:
            logger.error("Failed to finish span", error=str(e))
    
    def add_span_tag(self, span_context: SpanContext, key: str, value: Any) -> None:
        """添加 Span 标签"""
        if not self.enabled:
            return
        
        try:
            # 更新本地存储
            span_data = self.spans.get(span_context.span_id)
            if span_data:
                span_data.tags[key] = value
            
            # 更新当前 Span
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.set_attribute(key, str(value))
        
        except Exception as e:
            logger.error("Failed to add span tag", error=str(e))
    
    def add_span_log(
        self,
        span_context: SpanContext,
        message: str,
        level: str = "info",
        **kwargs
    ) -> None:
        """添加 Span 日志"""
        if not self.enabled:
            return
        
        try:
            log_entry = {
                "timestamp": time.time(),
                "level": level,
                "message": message,
                **kwargs
            }
            
            # 更新本地存储
            span_data = self.spans.get(span_context.span_id)
            if span_data:
                span_data.logs.append(log_entry)
            
            # 添加事件到当前 Span
            current_span = trace.get_current_span()
            if current_span and current_span.is_recording():
                current_span.add_event(message, log_entry)
        
        except Exception as e:
            logger.error("Failed to add span log", error=str(e))
    
    @contextmanager
    def trace_operation(
        self,
        operation_name: str,
        parent_context: Optional[SpanContext] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None,
    ):
        """追踪操作的上下文管理器"""
        span_context = self.start_span(
            operation_name=operation_name,
            parent_context=parent_context,
            kind=kind,
            tags=tags,
        )
        
        try:
            yield span_context
            self.finish_span(span_context, StatusCode.OK)
        except Exception as e:
            self.finish_span(span_context, StatusCode.ERROR, e)
            raise
    
    def inject_headers(self, span_context: SpanContext) -> Dict[str, str]:
        """注入追踪头部"""
        if not self.enabled:
            return {}
        
        try:
            headers = {}
            inject(headers)
            return headers
        except Exception as e:
            logger.error("Failed to inject headers", error=str(e))
            return {}
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """从头部提取追踪上下文"""
        if not self.enabled:
            return None
        
        try:
            context = extract(headers)
            if context:
                span = trace.get_current_span(context)
                if span:
                    span_context_obj = span.get_span_context()
                    return SpanContext(
                        trace_id=format(span_context_obj.trace_id, '032x'),
                        span_id=format(span_context_obj.span_id, '016x'),
                    )
        except Exception as e:
            logger.error("Failed to extract context", error=str(e))
        
        return None
    
    def get_trace(self, trace_id: str) -> Optional[List[SpanData]]:
        """获取完整的 Trace"""
        span_ids = self.traces.get(trace_id)
        if not span_ids:
            return None
        
        spans = []
        for span_id in span_ids:
            span_data = self.spans.get(span_id)
            if span_data:
                spans.append(span_data)
        
        # 按开始时间排序
        spans.sort(key=lambda x: x.start_time)
        return spans
    
    def get_span(self, span_id: str) -> Optional[SpanData]:
        """获取单个 Span"""
        return self.spans.get(span_id)
    
    def search_traces(
        self,
        service_name: Optional[str] = None,
        operation_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100,
    ) -> List[SpanData]:
        """搜索 Traces"""
        results = []
        
        for span_data in self.spans.values():
            # 过滤条件
            if service_name and service_name != self.service_name:
                continue
            
            if operation_name and operation_name != span_data.operation_name:
                continue
            
            if start_time and span_data.start_time < start_time:
                continue
            
            if end_time and span_data.start_time > end_time:
                continue
            
            if tags:
                match = True
                for key, value in tags.items():
                    if key not in span_data.tags or span_data.tags[key] != value:
                        match = False
                        break
                if not match:
                    continue
            
            results.append(span_data)
            
            if len(results) >= limit:
                break
        
        # 按开始时间倒序排序
        results.sort(key=lambda x: x.start_time, reverse=True)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取追踪统计信息"""
        total_spans = len(self.spans)
        total_traces = len(self.traces)
        
        # 计算平均持续时间
        durations = [span.duration for span in self.spans.values() if span.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # 统计错误数量
        error_spans = [span for span in self.spans.values() if span.status == "error"]
        error_rate = len(error_spans) / total_spans if total_spans > 0 else 0
        
        # 统计操作类型
        operations = {}
        for span in self.spans.values():
            operations[span.operation_name] = operations.get(span.operation_name, 0) + 1
        
        return {
            "enabled": self.enabled,
            "service_name": self.service_name,
            "total_spans": total_spans,
            "total_traces": total_traces,
            "avg_duration": avg_duration,
            "error_rate": error_rate,
            "error_count": len(error_spans),
            "operations": operations,
        }
    
    def cleanup_old_spans(self, max_age_seconds: int = 3600) -> None:
        """清理旧的 Span 数据"""
        current_time = time.time()
        cutoff_time = current_time - max_age_seconds
        
        # 找到需要删除的 Span
        spans_to_delete = []
        for span_id, span_data in self.spans.items():
            if span_data.start_time < cutoff_time:
                spans_to_delete.append(span_id)
        
        # 删除旧的 Span
        for span_id in spans_to_delete:
            span_data = self.spans[span_id]
            del self.spans[span_id]
            
            # 从 trace 中移除
            trace_id = span_data.trace_id
            if trace_id in self.traces:
                self.traces[trace_id] = [
                    sid for sid in self.traces[trace_id] if sid != span_id
                ]
                # 如果 trace 为空，删除它
                if not self.traces[trace_id]:
                    del self.traces[trace_id]
        
        if spans_to_delete:
            logger.info(
                "Cleaned up old spans",
                deleted_spans=len(spans_to_delete),
                cutoff_time=cutoff_time,
            )


# 全局追踪服务实例
tracing_service = TracingService()


def get_tracing_service() -> TracingService:
    """获取全局追踪服务"""
    return tracing_service


def trace_function(
    operation_name: Optional[str] = None,
    kind: SpanKind = SpanKind.INTERNAL,
    tags: Optional[Dict[str, Any]] = None,
):
    """函数装饰器，用于自动追踪函数调用"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracing_service.trace_operation(
                operation_name=op_name,
                kind=kind,
                tags=tags,
            ) as span_context:
                # 添加函数参数作为标签
                if args:
                    tracing_service.add_span_tag(span_context, "args.count", len(args))
                if kwargs:
                    tracing_service.add_span_tag(span_context, "kwargs.count", len(kwargs))
                
                try:
                    result = func(*args, **kwargs)
                    tracing_service.add_span_tag(span_context, "result.type", type(result).__name__)
                    return result
                except Exception as e:
                    tracing_service.add_span_tag(span_context, "error", True)
                    tracing_service.add_span_tag(span_context, "error.type", type(e).__name__)
                    raise
        
        return wrapper
    return decorator 