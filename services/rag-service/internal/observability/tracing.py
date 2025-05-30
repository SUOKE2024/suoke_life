#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分布式追踪模块 - 实现Jaeger分布式追踪
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import asynccontextmanager
import json
from loguru import logger

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.status import Status, StatusCode


class SpanKind(str, Enum):
    """Span类型"""
    INTERNAL = "internal"        # 内部操作
    SERVER = "server"           # 服务器端
    CLIENT = "client"           # 客户端
    PRODUCER = "producer"       # 生产者
    CONSUMER = "consumer"       # 消费者


class SpanStatus(str, Enum):
    """Span状态"""
    OK = "ok"                   # 成功
    ERROR = "error"             # 错误
    TIMEOUT = "timeout"         # 超时
    CANCELLED = "cancelled"     # 取消


@dataclass
class SpanContext:
    """Span上下文"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    baggage: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TraceEvent:
    """追踪事件"""
    timestamp: float
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    level: str = "info"


@dataclass
class SpanData:
    """Span数据"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    status: SpanStatus = SpanStatus.OK
    kind: SpanKind = SpanKind.INTERNAL
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[TraceEvent] = field(default_factory=list)
    references: List[Dict[str, Any]] = field(default_factory=list)


class TracingConfig:
    """追踪配置"""
    
    def __init__(
        self,
        service_name: str = "rag-service",
        jaeger_endpoint: str = "http://localhost:14268/api/traces",
        sampling_rate: float = 1.0,
        max_tag_value_length: int = 1024,
        enabled: bool = True
    ):
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.sampling_rate = sampling_rate
        self.max_tag_value_length = max_tag_value_length
        self.enabled = enabled


class SpanManager:
    """Span管理器"""
    
    def __init__(self):
        self.active_spans: Dict[str, SpanData] = {}
        self.completed_spans: List[SpanData] = []
        self.max_completed_spans = 1000
    
    def create_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None
    ) -> SpanData:
        """创建新的Span"""
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        
        span = SpanData(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            kind=kind,
            tags=tags or {}
        )
        
        self.active_spans[span_id] = span
        return span
    
    def finish_span(
        self,
        span_id: str,
        status: SpanStatus = SpanStatus.OK,
        error: Optional[Exception] = None
    ):
        """完成Span"""
        if span_id not in self.active_spans:
            logger.warning(f"Span {span_id} not found in active spans")
            return
        
        span = self.active_spans.pop(span_id)
        span.end_time = time.time()
        span.duration = span.end_time - span.start_time
        span.status = status
        
        if error:
            span.tags["error"] = True
            span.tags["error.message"] = str(error)
            span.tags["error.type"] = type(error).__name__
            
            # 添加错误日志
            span.logs.append(TraceEvent(
                timestamp=time.time(),
                name="error",
                attributes={
                    "event": "error",
                    "error.object": str(error),
                    "error.kind": type(error).__name__
                },
                level="error"
            ))
        
        # 添加到已完成列表
        self.completed_spans.append(span)
        
        # 限制已完成Span数量
        if len(self.completed_spans) > self.max_completed_spans:
            self.completed_spans = self.completed_spans[-self.max_completed_spans:]
    
    def add_span_tag(self, span_id: str, key: str, value: Any):
        """添加Span标签"""
        if span_id in self.active_spans:
            self.active_spans[span_id].tags[key] = value
    
    def add_span_log(
        self,
        span_id: str,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        level: str = "info"
    ):
        """添加Span日志"""
        if span_id in self.active_spans:
            event = TraceEvent(
                timestamp=time.time(),
                name=event_name,
                attributes=attributes or {},
                level=level
            )
            self.active_spans[span_id].logs.append(event)
    
    def get_active_span(self, span_id: str) -> Optional[SpanData]:
        """获取活跃Span"""
        return self.active_spans.get(span_id)
    
    def get_completed_spans(self, limit: int = 100) -> List[SpanData]:
        """获取已完成的Span"""
        return self.completed_spans[-limit:]


class TracingInstrumentation:
    """追踪工具"""
    
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self.span_manager = SpanManager()
        
        if config.enabled:
            self._setup_tracer()
    
    def _setup_tracer(self):
        """设置追踪器"""
        try:
            # 创建TracerProvider
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            
            # 创建Jaeger导出器
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
                collector_endpoint=self.config.jaeger_endpoint,
            )
            
            # 创建Span处理器
            span_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            
            # 获取追踪器
            self.tracer = trace.get_tracer(self.config.service_name)
            
            # 自动工具化
            self._setup_auto_instrumentation()
            
            logger.info(f"分布式追踪已启用: {self.config.service_name}")
            
        except Exception as e:
            logger.error(f"追踪器设置失败: {e}")
            self.config.enabled = False
    
    def _setup_auto_instrumentation(self):
        """设置自动工具化"""
        try:
            # FastAPI工具化
            FastAPIInstrumentor().instrument()
            
            # HTTP请求工具化
            RequestsInstrumentor().instrument()
            
            # 数据库工具化
            AsyncPGInstrumentor().instrument()
            
            # Redis工具化
            RedisInstrumentor().instrument()
            
            logger.info("自动工具化设置完成")
            
        except Exception as e:
            logger.warning(f"自动工具化设置失败: {e}")
    
    @asynccontextmanager
    async def trace_operation(
        self,
        operation_name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None,
        parent_span_id: Optional[str] = None
    ):
        """追踪操作上下文管理器"""
        if not self.config.enabled:
            yield None
            return
        
        span = None
        try:
            # 创建Span
            span = self.span_manager.create_span(
                operation_name=operation_name,
                parent_span_id=parent_span_id,
                kind=kind,
                tags=tags
            )
            
            # 添加基础标签
            span.tags.update({
                "service.name": self.config.service_name,
                "operation.name": operation_name,
                "span.kind": kind.value
            })
            
            yield span
            
        except Exception as e:
            if span:
                self.span_manager.finish_span(
                    span.span_id,
                    status=SpanStatus.ERROR,
                    error=e
                )
            raise
        else:
            if span:
                self.span_manager.finish_span(span.span_id, status=SpanStatus.OK)
    
    def trace_function(
        self,
        operation_name: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tags: Optional[Dict[str, Any]] = None
    ):
        """函数追踪装饰器"""
        def decorator(func: Callable):
            async def async_wrapper(*args, **kwargs):
                op_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                async with self.trace_operation(
                    operation_name=op_name,
                    kind=kind,
                    tags=tags
                ) as span:
                    if span:
                        # 添加函数信息
                        span.tags.update({
                            "function.name": func.__name__,
                            "function.module": func.__module__,
                            "function.args_count": len(args),
                            "function.kwargs_count": len(kwargs)
                        })
                    
                    return await func(*args, **kwargs)
            
            def sync_wrapper(*args, **kwargs):
                # 对于同步函数的简化处理
                return func(*args, **kwargs)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def add_tag(self, span_id: str, key: str, value: Any):
        """添加标签"""
        if self.config.enabled:
            self.span_manager.add_span_tag(span_id, key, value)
    
    def add_log(
        self,
        span_id: str,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        level: str = "info"
    ):
        """添加日志"""
        if self.config.enabled:
            self.span_manager.add_span_log(span_id, event_name, attributes, level)
    
    def inject_context(self, headers: Dict[str, str]) -> Dict[str, str]:
        """注入追踪上下文到HTTP头"""
        if not self.config.enabled:
            return headers
        
        try:
            inject(headers)
        except Exception as e:
            logger.warning(f"上下文注入失败: {e}")
        
        return headers
    
    def extract_context(self, headers: Dict[str, str]) -> Optional[SpanContext]:
        """从HTTP头提取追踪上下文"""
        if not self.config.enabled:
            return None
        
        try:
            context = extract(headers)
            if context:
                # 简化的上下文提取
                return SpanContext(
                    trace_id=str(uuid.uuid4()),
                    span_id=str(uuid.uuid4())
                )
        except Exception as e:
            logger.warning(f"上下文提取失败: {e}")
        
        return None
    
    def get_trace_statistics(self) -> Dict[str, Any]:
        """获取追踪统计"""
        active_spans = len(self.span_manager.active_spans)
        completed_spans = len(self.span_manager.completed_spans)
        
        # 计算平均持续时间
        durations = [
            span.duration for span in self.span_manager.completed_spans
            if span.duration is not None
        ]
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # 统计状态分布
        status_counts = {}
        for span in self.span_manager.completed_spans:
            status = span.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "enabled": self.config.enabled,
            "service_name": self.config.service_name,
            "active_spans": active_spans,
            "completed_spans": completed_spans,
            "average_duration": avg_duration,
            "status_distribution": status_counts,
            "sampling_rate": self.config.sampling_rate
        }
    
    async def export_traces(self, format: str = "json") -> str:
        """导出追踪数据"""
        traces = []
        
        for span in self.span_manager.get_completed_spans():
            trace_data = {
                "traceID": span.trace_id,
                "spanID": span.span_id,
                "parentSpanID": span.parent_span_id,
                "operationName": span.operation_name,
                "startTime": span.start_time,
                "endTime": span.end_time,
                "duration": span.duration,
                "status": span.status.value,
                "kind": span.kind.value,
                "tags": span.tags,
                "logs": [
                    {
                        "timestamp": log.timestamp,
                        "name": log.name,
                        "attributes": log.attributes,
                        "level": log.level
                    }
                    for log in span.logs
                ]
            }
            traces.append(trace_data)
        
        if format == "json":
            return json.dumps(traces, indent=2, ensure_ascii=False)
        else:
            return str(traces)
    
    async def cleanup(self):
        """清理资源"""
        if self.tracer_provider:
            try:
                # 强制导出剩余的Span
                for processor in self.tracer_provider._active_span_processor._span_processors:
                    processor.force_flush()
                
                logger.info("追踪资源清理完成")
            except Exception as e:
                logger.error(f"追踪资源清理失败: {e}")


# 全局追踪实例
_tracing_instance: Optional[TracingInstrumentation] = None


def initialize_tracing(config: TracingConfig) -> TracingInstrumentation:
    """初始化追踪"""
    global _tracing_instance
    _tracing_instance = TracingInstrumentation(config)
    return _tracing_instance


def get_tracer() -> Optional[TracingInstrumentation]:
    """获取追踪器实例"""
    return _tracing_instance


def trace_operation(
    operation_name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    tags: Optional[Dict[str, Any]] = None
):
    """操作追踪装饰器"""
    def decorator(func: Callable):
        if _tracing_instance:
            return _tracing_instance.trace_function(operation_name, kind, tags)(func)
        return func
    return decorator


# 便捷的追踪装饰器
def trace_rag_operation(operation_name: str, tags: Optional[Dict[str, Any]] = None):
    """RAG操作追踪装饰器"""
    return trace_operation(
        operation_name=f"rag.{operation_name}",
        kind=SpanKind.INTERNAL,
        tags={**(tags or {}), "component": "rag"}
    )


def trace_tcm_operation(operation_name: str, tags: Optional[Dict[str, Any]] = None):
    """中医操作追踪装饰器"""
    return trace_operation(
        operation_name=f"tcm.{operation_name}",
        kind=SpanKind.INTERNAL,
        tags={**(tags or {}), "component": "tcm"}
    )


def trace_agent_operation(agent_name: str, operation_name: str, tags: Optional[Dict[str, Any]] = None):
    """智能体操作追踪装饰器"""
    return trace_operation(
        operation_name=f"agent.{agent_name}.{operation_name}",
        kind=SpanKind.INTERNAL,
        tags={**(tags or {}), "component": "agent", "agent.name": agent_name}
    ) 