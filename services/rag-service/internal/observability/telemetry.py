"""
telemetry - 索克生活项目模块
"""

from functools import wraps
from loguru import logger
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aiohttp import AioHttpClientInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, start_http_server
from typing import Dict, Optional
import asyncio
import socket
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
遥测模块，实现OpenTelemetry分布式追踪和指标收集
"""




class Telemetry:
    """遥测服务类，管理分布式追踪和指标收集"""

    def __init__(self, config: Dict):
        """
        初始化遥测服务
        
        Args:
            config (Dict): 配置信息，包含服务基本信息和遥测配置
        """
        self.config = config
        self.service_name = config.get("service", {}).get("name", "rag-service")
        self.service_version = config.get("service", {}).get("version", "unknown")
        self.service_env = config.get("service", {}).get("env", "development")
        
        # OpenTelemetry配置
        self.otlp_endpoint = config.get("telemetry", {}).get("otlp_endpoint", "")
        self.enable_tracing = config.get("telemetry", {}).get("enable_tracing", False)
        self.enable_metrics = config.get("telemetry", {}).get("enable_metrics", False)
        
        # Prometheus配置
        self.prometheus_port = config.get("telemetry", {}).get("prometheus_port", 8081)
        self.enable_prometheus = config.get("telemetry", {}).get("enable_prometheus", False)
        
        # 组件初始化标志
        self.tracing_initialized = False
        self.metrics_initialized = False
        self.prometheus_initialized = False
        
        # OpenTelemetry组件
        self.tracer_provider = None
        self.tracer = None
        self.meter_provider = None
        self.meter = None
        
        # Prometheus监控指标
        self.metrics = {}
        
        # 监控状态
        self.is_healthy = True
    
    def setup(self):
        """设置遥测服务，初始化追踪和指标收集"""
        # 初始化资源信息
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
            "deployment.environment": self.service_env,
            "host.hostname": socket.gethostname(),
        })
        
        # 初始化追踪
        if self.enable_tracing:
            self._setup_tracing(resource)
        
        # 初始化OpenTelemetry指标
        if self.enable_metrics:
            self._setup_metrics(resource)
        
        # 初始化Prometheus监控
        if self.enable_prometheus:
            self._setup_prometheus()
            
        logger.info(f"Telemetry service initialized: tracing={self.enable_tracing}, metrics={self.enable_metrics}, prometheus={self.enable_prometheus}")
    
    def _setup_tracing(self, resource: Resource):
        """
        设置分布式追踪
        
        Args:
            resource (Resource): OpenTelemetry资源对象
        """
        # 创建Tracer Provider
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
        
        # 添加OTLP导出器（如果配置了端点）
        if self.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
            self.tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        
        # 创建tracer
        self.tracer = trace.get_tracer(self.service_name, self.service_version)
        
        # 自动检测和注入工具
        GrpcInstrumentor().instrument()
        AioHttpClientInstrumentor().instrument()
        RedisInstrumentor().instrument()
        
        self.tracing_initialized = True
        logger.info("Distributed tracing initialized")
    
    def _setup_metrics(self, resource: Resource):
        """
        设置指标收集
        
        Args:
            resource (Resource): OpenTelemetry资源对象
        """
        # 创建度量收集器
        readers = []
        
        if self.otlp_endpoint:
            otlp_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
            readers.append(PeriodicExportingMetricReader(otlp_exporter))
        
        self.meter_provider = MeterProvider(resource=resource, metric_readers=readers)
        metrics.set_meter_provider(self.meter_provider)
        
        # 创建meter
        self.meter = metrics.get_meter(self.service_name, self.service_version)
        
        # 创建基本指标
        self._create_base_metrics()
        
        self.metrics_initialized = True
        logger.info("Metrics collection initialized")
    
    def _setup_prometheus(self):
        """设置Prometheus监控服务器和基本指标"""
        # 启动Prometheus HTTP服务器
        start_http_server(self.prometheus_port)
        
        # 创建基本的Prometheus指标
        self.metrics["http_requests_total"] = Counter(
            "http_requests_total", 
            "Total number of HTTP requests",
            ["method", "endpoint", "status"]
        )
        
        self.metrics["http_request_duration_seconds"] = Histogram(
            "http_request_duration_seconds", 
            "HTTP request duration in seconds",
            ["method", "endpoint"]
        )
        
        self.metrics["grpc_requests_total"] = Counter(
            "grpc_requests_total", 
            "Total number of gRPC requests",
            ["method", "status"]
        )
        
        self.metrics["grpc_request_duration_seconds"] = Histogram(
            "grpc_request_duration_seconds", 
            "gRPC request duration in seconds",
            ["method"]
        )
        
        self.metrics["retrieval_duration_seconds"] = Histogram(
            "retrieval_duration_seconds", 
            "Document retrieval duration in seconds"
        )
        
        self.metrics["generation_duration_seconds"] = Histogram(
            "generation_duration_seconds", 
            "Answer generation duration in seconds"
        )
        
        self.metrics["cache_hits_total"] = Counter(
            "cache_hits_total", 
            "Total number of cache hits",
            ["cache_type"]
        )
        
        self.metrics["cache_misses_total"] = Counter(
            "cache_misses_total", 
            "Total number of cache misses",
            ["cache_type"]
        )
        
        self.prometheus_initialized = True
        logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
    
    def _create_base_metrics(self):
        """使用OpenTelemetry Meter创建基本指标"""
        if not self.meter:
            return
        
        # 创建请求计数器
        self.request_counter = self.meter.create_counter(
            name="rag_service.requests",
            description="Number of requests",
            unit="1"
        )
        
        # 创建检索时间直方图
        self.retrieval_histogram = self.meter.create_histogram(
            name="rag_service.retrieval_duration",
            description="Time taken for document retrieval",
            unit="ms"
        )
        
        # 创建生成时间直方图
        self.generation_histogram = self.meter.create_histogram(
            name="rag_service.generation_duration",
            description="Time taken for answer generation",
            unit="ms"
        )
        
        # 创建缓存命中计数器
        self.cache_hit_counter = self.meter.create_counter(
            name="rag_service.cache_hits",
            description="Number of cache hits",
            unit="1"
        )
        
        # 创建缓存未命中计数器
        self.cache_miss_counter = self.meter.create_counter(
            name="rag_service.cache_misses",
            description="Number of cache misses",
            unit="1"
        )
        
        # 创建错误计数器
        self.error_counter = self.meter.create_counter(
            name="rag_service.errors",
            description="Number of errors",
            unit="1"
        )
    
    def record_request(self, method_name: str, attributes: Optional[Dict] = None):
        """
        记录请求
        
        Args:
            method_name (str): 方法名
            attributes (Optional[Dict]): 附加属性
        """
        if self.metrics_initialized and self.request_counter:
            attrs = {"method": method_name}
            if attributes:
                attrs.update(attributes)
            self.request_counter.add(1, attrs)
    
    def record_retrieval_time(self, duration_ms: float, attributes: Optional[Dict] = None):
        """
        记录检索时间
        
        Args:
            duration_ms (float): 检索时间（毫秒）
            attributes (Optional[Dict]): 附加属性
        """
        if self.metrics_initialized and self.retrieval_histogram:
            self.retrieval_histogram.record(duration_ms, attributes)
        
        if self.prometheus_initialized and "retrieval_duration_seconds" in self.metrics:
            self.metrics["retrieval_duration_seconds"].observe(duration_ms / 1000.0)
    
    def record_generation_time(self, duration_ms: float, attributes: Optional[Dict] = None):
        """
        记录生成时间
        
        Args:
            duration_ms (float): 生成时间（毫秒）
            attributes (Optional[Dict]): 附加属性
        """
        if self.metrics_initialized and self.generation_histogram:
            self.generation_histogram.record(duration_ms, attributes)
        
        if self.prometheus_initialized and "generation_duration_seconds" in self.metrics:
            self.metrics["generation_duration_seconds"].observe(duration_ms / 1000.0)
    
    def record_cache_hit(self, cache_type: str):
        """
        记录缓存命中
        
        Args:
            cache_type (str): 缓存类型
        """
        if self.metrics_initialized and self.cache_hit_counter:
            self.cache_hit_counter.add(1, {"cache_type": cache_type})
        
        if self.prometheus_initialized and "cache_hits_total" in self.metrics:
            self.metrics["cache_hits_total"].labels(cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """
        记录缓存未命中
        
        Args:
            cache_type (str): 缓存类型
        """
        if self.metrics_initialized and self.cache_miss_counter:
            self.cache_miss_counter.add(1, {"cache_type": cache_type})
        
        if self.prometheus_initialized and "cache_misses_total" in self.metrics:
            self.metrics["cache_misses_total"].labels(cache_type).inc()
    
    def record_error(self, error_type: str, attributes: Optional[Dict] = None):
        """
        记录错误
        
        Args:
            error_type (str): 错误类型
            attributes (Optional[Dict]): 附加属性
        """
        if self.metrics_initialized and self.error_counter:
            attrs = {"error_type": error_type}
            if attributes:
                attrs.update(attributes)
            self.error_counter.add(1, attrs)
    
    def start_span(self, name: str, context=None, kind=None, attributes=None):
        """
        创建并开始一个追踪span
        
        Args:
            name (str): Span名称
            context: 可选的父上下文
            kind: Span类型
            attributes: Span属性
            
        Returns:
            span: 追踪span对象
        """
        if not self.tracing_initialized or not self.tracer:
            # 创建一个空的上下文管理器，不做任何事情
            class NoopContextManager:
                def __enter__(self):
                    return self
                
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            
            return NoopContextManager()
        
        return self.tracer.start_as_current_span(name, context, kind, attributes)
    
    async def close(self):
        """关闭遥测服务，释放资源"""
        if self.tracing_initialized and self.tracer_provider:
            await asyncio.shield(asyncio.to_thread(self.tracer_provider.shutdown))
        
        if self.metrics_initialized and self.meter_provider:
            await asyncio.shield(asyncio.to_thread(self.meter_provider.shutdown))
        
        logger.info("Telemetry service closed")

def trace_method(method_name=None):
    """
    装饰器：为方法创建追踪span
    
    Args:
        method_name (str, optional): 方法名称，默认使用被装饰方法的名称
        
    Returns:
        decorator: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            # 获取遥测服务
            telemetry = getattr(self, "telemetry", None)
            if not telemetry or not telemetry.tracing_initialized:
                return await func(self, *args, **kwargs)
            
            span_name = method_name or func.__name__
            with telemetry.start_span(f"{self.__class__.__name__}.{span_name}") as span:
                # 记录参数（注意不记录敏感信息）
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)):
                        span.set_attribute(f"arg{i}", str(arg))
                
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"kwarg.{key}", str(value))
                
                start_time = time.time()
                try:
                    result = await func(self, *args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", e.__class__.__name__)
                    span.set_attribute("error.message", str(e))
                    raise
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("duration_ms", duration_ms)
        
        @wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            # 获取遥测服务
            telemetry = getattr(self, "telemetry", None)
            if not telemetry or not telemetry.tracing_initialized:
                return func(self, *args, **kwargs)
            
            span_name = method_name or func.__name__
            with telemetry.start_span(f"{self.__class__.__name__}.{span_name}") as span:
                # 记录参数（注意不记录敏感信息）
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)):
                        span.set_attribute(f"arg{i}", str(arg))
                
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"kwarg.{key}", str(value))
                
                start_time = time.time()
                try:
                    result = func(self, *args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", e.__class__.__name__)
                    span.set_attribute("error.message", str(e))
                    raise
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    span.set_attribute("duration_ms", duration_ms)
        
        # 判断是异步函数还是同步函数
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    # 支持直接@trace_method使用
    if callable(method_name):
        func = method_name
        method_name = None
        return decorator(func)
    
    return decorator 