#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
监控指标服务

提供全面的监控指标收集和上报功能，支持Prometheus和OpenTelemetry。
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from contextlib import asynccontextmanager

from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from structlog import get_logger

logger = get_logger()


@dataclass
class MetricDefinition:
    """指标定义"""
    name: str
    description: str
    metric_type: str  # counter, histogram, gauge, summary
    labels: List[str] = field(default_factory=list)
    buckets: Optional[List[float]] = None  # 用于histogram


class MetricsService:
    """监控指标服务"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.registry = CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self.tracer = None
        self.meter = None
        
        # 预定义的指标
        self.metric_definitions = {
            # 请求相关指标
            "requests_total": MetricDefinition(
                name="look_service_requests_total",
                description="Total number of requests",
                metric_type="counter",
                labels=["method", "status", "endpoint"]
            ),
            "request_duration": MetricDefinition(
                name="look_service_request_duration_seconds",
                description="Request duration in seconds",
                metric_type="histogram",
                labels=["method", "endpoint"],
                buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
            ),
            "active_requests": MetricDefinition(
                name="look_service_active_requests",
                description="Number of active requests",
                metric_type="gauge",
                labels=["method"]
            ),
            
            # 分析相关指标
            "analysis_total": MetricDefinition(
                name="look_service_analysis_total",
                description="Total number of analyses performed",
                metric_type="counter",
                labels=["analysis_type", "status"]
            ),
            "analysis_duration": MetricDefinition(
                name="look_service_analysis_duration_seconds",
                description="Analysis processing duration in seconds",
                metric_type="histogram",
                labels=["analysis_type"],
                buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
            ),
            "analysis_queue_size": MetricDefinition(
                name="look_service_analysis_queue_size",
                description="Number of analyses in queue",
                metric_type="gauge"
            ),
            
            # 模型相关指标
            "model_inference_duration": MetricDefinition(
                name="look_service_model_inference_duration_seconds",
                description="Model inference duration in seconds",
                metric_type="histogram",
                labels=["model_name"],
                buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
            ),
            "model_memory_usage": MetricDefinition(
                name="look_service_model_memory_usage_bytes",
                description="Model memory usage in bytes",
                metric_type="gauge",
                labels=["model_name"]
            ),
            
            # 缓存相关指标
            "cache_hits_total": MetricDefinition(
                name="look_service_cache_hits_total",
                description="Total number of cache hits",
                metric_type="counter",
                labels=["cache_type"]
            ),
            "cache_misses_total": MetricDefinition(
                name="look_service_cache_misses_total",
                description="Total number of cache misses",
                metric_type="counter",
                labels=["cache_type"]
            ),
            
            # 数据库相关指标
            "db_operations_total": MetricDefinition(
                name="look_service_db_operations_total",
                description="Total number of database operations",
                metric_type="counter",
                labels=["operation", "status"]
            ),
            "db_operation_duration": MetricDefinition(
                name="look_service_db_operation_duration_seconds",
                description="Database operation duration in seconds",
                metric_type="histogram",
                labels=["operation"],
                buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
            ),
            
            # 系统资源指标
            "memory_usage": MetricDefinition(
                name="look_service_memory_usage_bytes",
                description="Memory usage in bytes",
                metric_type="gauge"
            ),
            "cpu_usage": MetricDefinition(
                name="look_service_cpu_usage_percent",
                description="CPU usage percentage",
                metric_type="gauge"
            ),
            
            # 错误相关指标
            "errors_total": MetricDefinition(
                name="look_service_errors_total",
                description="Total number of errors",
                metric_type="counter",
                labels=["error_type", "component"]
            )
        }
    
    async def initialize(self):
        """初始化监控服务"""
        try:
            # 初始化Prometheus指标
            await self._init_prometheus_metrics()
            
            # 初始化OpenTelemetry
            if self.config.get("opentelemetry", {}).get("enabled", False):
                await self._init_opentelemetry()
            
            logger.info("监控指标服务初始化成功")
            
        except Exception as e:
            logger.error("监控指标服务初始化失败", error=str(e))
            raise
    
    async def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        for metric_name, definition in self.metric_definitions.items():
            if definition.metric_type == "counter":
                metric = Counter(
                    definition.name,
                    definition.description,
                    definition.labels,
                    registry=self.registry
                )
            elif definition.metric_type == "histogram":
                metric = Histogram(
                    definition.name,
                    definition.description,
                    definition.labels,
                    buckets=definition.buckets,
                    registry=self.registry
                )
            elif definition.metric_type == "gauge":
                metric = Gauge(
                    definition.name,
                    definition.description,
                    definition.labels,
                    registry=self.registry
                )
            elif definition.metric_type == "summary":
                metric = Summary(
                    definition.name,
                    definition.description,
                    definition.labels,
                    registry=self.registry
                )
            else:
                continue
            
            self.metrics[metric_name] = metric
        
        logger.info("Prometheus指标初始化完成", metrics_count=len(self.metrics))
    
    async def _init_opentelemetry(self):
        """初始化OpenTelemetry"""
        otel_config = self.config.get("opentelemetry", {})
        
        # 创建资源
        resource = Resource.create({
            "service.name": "look-service",
            "service.version": "1.0.0",
            "service.namespace": "diagnostic-services"
        })
        
        # 初始化追踪
        if otel_config.get("tracing", {}).get("enabled", False):
            trace.set_tracer_provider(TracerProvider(resource=resource))
            
            # 配置Jaeger导出器
            jaeger_config = otel_config.get("tracing", {}).get("jaeger", {})
            if jaeger_config.get("enabled", False):
                jaeger_exporter = JaegerExporter(
                    agent_host_name=jaeger_config.get("host", "localhost"),
                    agent_port=jaeger_config.get("port", 6831),
                )
                span_processor = BatchSpanProcessor(jaeger_exporter)
                trace.get_tracer_provider().add_span_processor(span_processor)
            
            self.tracer = trace.get_tracer(__name__)
        
        # 初始化指标
        if otel_config.get("metrics", {}).get("enabled", False):
            # 配置Prometheus指标读取器
            prometheus_reader = PrometheusMetricReader()
            metrics.set_meter_provider(
                MeterProvider(resource=resource, metric_readers=[prometheus_reader])
            )
            self.meter = metrics.get_meter(__name__)
        
        logger.info("OpenTelemetry初始化完成")
    
    def inc_counter(self, metric_name: str, labels: Optional[Dict[str, str]] = None, value: float = 1):
        """增加计数器指标"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
    
    def observe_histogram(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """观察直方图指标"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)
    
    def set_gauge(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """设置仪表盘指标"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)
    
    def inc_gauge(self, metric_name: str, value: float = 1, labels: Optional[Dict[str, str]] = None):
        """增加仪表盘指标"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
    
    def dec_gauge(self, metric_name: str, value: float = 1, labels: Optional[Dict[str, str]] = None):
        """减少仪表盘指标"""
        if metric_name in self.metrics:
            metric = self.metrics[metric_name]
            if labels:
                metric.labels(**labels).dec(value)
            else:
                metric.dec(value)
    
    @asynccontextmanager
    async def time_histogram(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """计时上下文管理器"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.observe_histogram(metric_name, duration, labels)
    
    @asynccontextmanager
    async def track_active_requests(self, method: str):
        """跟踪活跃请求数"""
        self.inc_gauge("active_requests", labels={"method": method})
        try:
            yield
        finally:
            self.dec_gauge("active_requests", labels={"method": method})
    
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """开始一个追踪span"""
        if self.tracer:
            span = self.tracer.start_span(name)
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            return span
        return None
    
    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_content_type(self) -> str:
        """获取指标内容类型"""
        return CONTENT_TYPE_LATEST
    
    async def collect_system_metrics(self):
        """收集系统指标"""
        try:
            import psutil
            
            # 内存使用情况
            memory_info = psutil.virtual_memory()
            self.set_gauge("memory_usage", memory_info.used)
            
            # CPU使用情况
            cpu_percent = psutil.cpu_percent(interval=1)
            self.set_gauge("cpu_usage", cpu_percent)
            
        except ImportError:
            logger.warning("psutil未安装，无法收集系统指标")
        except Exception as e:
            logger.error("收集系统指标失败", error=str(e))
    
    async def start_background_collection(self):
        """启动后台指标收集"""
        async def collect_loop():
            while True:
                try:
                    await self.collect_system_metrics()
                    await asyncio.sleep(30)  # 每30秒收集一次
                except Exception as e:
                    logger.error("后台指标收集失败", error=str(e))
                    await asyncio.sleep(60)  # 出错时等待更长时间
        
        # 启动后台任务
        asyncio.create_task(collect_loop())
        logger.info("后台指标收集已启动")


class MetricsMiddleware:
    """指标中间件"""
    
    def __init__(self, metrics_service: MetricsService):
        self.metrics = metrics_service
    
    async def __call__(self, request, call_next):
        """中间件处理函数"""
        method = request.method
        endpoint = request.url.path
        
        # 增加活跃请求数
        async with self.metrics.track_active_requests(method):
            start_time = time.time()
            
            try:
                # 处理请求
                response = await call_next(request)
                
                # 记录成功指标
                duration = time.time() - start_time
                self.metrics.inc_counter(
                    "requests_total",
                    labels={"method": method, "status": str(response.status_code), "endpoint": endpoint}
                )
                self.metrics.observe_histogram(
                    "request_duration",
                    duration,
                    labels={"method": method, "endpoint": endpoint}
                )
                
                return response
                
            except Exception as e:
                # 记录错误指标
                duration = time.time() - start_time
                self.metrics.inc_counter(
                    "requests_total",
                    labels={"method": method, "status": "error", "endpoint": endpoint}
                )
                self.metrics.observe_histogram(
                    "request_duration",
                    duration,
                    labels={"method": method, "endpoint": endpoint}
                )
                self.metrics.inc_counter(
                    "errors_total",
                    labels={"error_type": type(e).__name__, "component": "middleware"}
                )
                raise


# 装饰器
def track_analysis_metrics(analysis_type: str):
    """分析指标跟踪装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 获取指标服务实例（这里需要根据实际情况调整）
            from internal.container.container import get_container
            container = get_container()
            metrics_service = container.get("metrics_service")
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # 记录成功指标
                duration = time.time() - start_time
                metrics_service.inc_counter(
                    "analysis_total",
                    labels={"analysis_type": analysis_type, "status": "success"}
                )
                metrics_service.observe_histogram(
                    "analysis_duration",
                    duration,
                    labels={"analysis_type": analysis_type}
                )
                
                return result
                
            except Exception as e:
                # 记录错误指标
                duration = time.time() - start_time
                metrics_service.inc_counter(
                    "analysis_total",
                    labels={"analysis_type": analysis_type, "status": "error"}
                )
                metrics_service.observe_histogram(
                    "analysis_duration",
                    duration,
                    labels={"analysis_type": analysis_type}
                )
                metrics_service.inc_counter(
                    "errors_total",
                    labels={"error_type": type(e).__name__, "component": "analyzer"}
                )
                raise
        
        return wrapper
    return decorator


def track_model_metrics(model_name: str):
    """模型指标跟踪装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            from internal.container.container import get_container
            container = get_container()
            metrics_service = container.get("metrics_service")
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # 记录推理时间
                duration = time.time() - start_time
                metrics_service.observe_histogram(
                    "model_inference_duration",
                    duration,
                    labels={"model_name": model_name}
                )
                
                return result
                
            except Exception as e:
                metrics_service.inc_counter(
                    "errors_total",
                    labels={"error_type": type(e).__name__, "component": "model"}
                )
                raise
        
        return wrapper
    return decorator 