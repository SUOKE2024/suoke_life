"""
metrics_collector - 索克生活项目模块
"""

from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram, Gauge, Summary, Info
from typing import Dict, List, Optional, Any, Callable
import logging
import prometheus_client
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的监控和指标收集系统
集成Prometheus指标、OpenTelemetry追踪和自定义业务指标
"""



logger = logging.getLogger(__name__)

@dataclass
class MetricsConfig:
    """指标配置"""
    enabled: bool = True
    prometheus_enabled: bool = True
    opentelemetry_enabled: bool = True
    otlp_endpoint: Optional[str] = None
    service_name: str = "api-gateway"
    service_version: str = "1.0.0"
    export_interval: int = 30
    custom_metrics_enabled: bool = True

@dataclass
class RequestMetrics:
    """请求指标"""
    timestamp: float
    method: str
    path: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    service_name: Optional[str] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

class PrometheusMetrics:
    """Prometheus指标收集器"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        
        # 请求相关指标
        self.request_count = Counter(
            'gateway_requests_total',
            'Total number of requests',
            ['method', 'path', 'status_code', 'service']
        )
        
        self.request_duration = Histogram(
            'gateway_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'path', 'service'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.request_size = Histogram(
            'gateway_request_size_bytes',
            'Request size in bytes',
            ['method', 'path', 'service'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
        )
        
        self.response_size = Histogram(
            'gateway_response_size_bytes',
            'Response size in bytes',
            ['method', 'path', 'service'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576]
        )
        
        # 连接相关指标
        self.active_connections = Gauge(
            'gateway_active_connections',
            'Number of active connections',
            ['service']
        )
        
        self.connection_pool_size = Gauge(
            'gateway_connection_pool_size',
            'Connection pool size',
            ['service']
        )
        
        # 缓存相关指标
        self.cache_hits = Counter(
            'gateway_cache_hits_total',
            'Total number of cache hits',
            ['cache_level']
        )
        
        self.cache_misses = Counter(
            'gateway_cache_misses_total',
            'Total number of cache misses',
            ['cache_level']
        )
        
        self.cache_size = Gauge(
            'gateway_cache_size_bytes',
            'Cache size in bytes',
            ['cache_level']
        )
        
        # 负载均衡相关指标
        self.backend_requests = Counter(
            'gateway_backend_requests_total',
            'Total number of backend requests',
            ['backend', 'status']
        )
        
        self.backend_response_time = Histogram(
            'gateway_backend_response_time_seconds',
            'Backend response time in seconds',
            ['backend'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        self.backend_health = Gauge(
            'gateway_backend_health',
            'Backend health status (1=healthy, 0=unhealthy)',
            ['backend']
        )
        
        # 限流相关指标
        self.rate_limit_hits = Counter(
            'gateway_rate_limit_hits_total',
            'Total number of rate limit hits',
            ['limit_type', 'client_id']
        )
        
        # 错误相关指标
        self.errors = Counter(
            'gateway_errors_total',
            'Total number of errors',
            ['error_type', 'service']
        )
        
        # 系统指标
        self.memory_usage = Gauge(
            'gateway_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'gateway_cpu_usage_percent',
            'CPU usage percentage'
        )
        
        # 服务信息
        self.service_info = Info(
            'gateway_service_info',
            'Service information'
        )
        
        # 设置服务信息
        self.service_info.info({
            'service_name': service_name,
            'version': '1.0.0'
        })

class OpenTelemetryMetrics:
    """OpenTelemetry指标收集器"""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.tracer = None
        self.meter = None
        
        if config.opentelemetry_enabled:
            self._setup_tracing()
            self._setup_metrics()
    
    def _setup_tracing(self):
        """设置分布式追踪"""
        # 创建追踪提供者
        trace.set_tracer_provider(TracerProvider())
        
        # 配置OTLP导出器
        if self.config.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(endpoint=self.config.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
        
        # 获取追踪器
        self.tracer = trace.get_tracer(
            self.config.service_name,
            self.config.service_version
        )
        
        logger.info("OpenTelemetry追踪已设置")
    
    def _setup_metrics(self):
        """设置指标收集"""
        # 创建指标读取器
        if self.config.otlp_endpoint:
            metric_exporter = OTLPMetricExporter(endpoint=self.config.otlp_endpoint)
            metric_reader = PeriodicExportingMetricReader(
                exporter=metric_exporter,
                export_interval_millis=self.config.export_interval * 1000
            )
            
            # 创建指标提供者
            metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
        
        # 获取指标器
        self.meter = metrics.get_meter(
            self.config.service_name,
            self.config.service_version
        )
        
        logger.info("OpenTelemetry指标已设置")
    
    @asynccontextmanager
    async def trace_request(self, operation_name: str, attributes: Dict[str, Any] = None):
        """追踪请求"""
        if not self.tracer:
            yield None
            return
        
        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise

class CustomMetrics:
    """自定义业务指标"""
    
    def __init__(self):
        self._metrics: Dict[str, Any] = {}
        self._time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._aggregations: Dict[str, Dict] = {}
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """记录自定义指标"""
        timestamp = time.time()
        metric_data = {
            'timestamp': timestamp,
            'value': value,
            'labels': labels or {}
        }
        
        self._time_series[name].append(metric_data)
        self._update_aggregations(name, value)
    
    def _update_aggregations(self, name: str, value: float):
        """更新聚合统计"""
        if name not in self._aggregations:
            self._aggregations[name] = {
                'count': 0,
                'sum': 0.0,
                'min': float('inf'),
                'max': float('-inf'),
                'avg': 0.0
            }
        
        agg = self._aggregations[name]
        agg['count'] += 1
        agg['sum'] += value
        agg['min'] = min(agg['min'], value)
        agg['max'] = max(agg['max'], value)
        agg['avg'] = agg['sum'] / agg['count']
    
    def get_metric_summary(self, name: str) -> Optional[Dict]:
        """获取指标摘要"""
        return self._aggregations.get(name)
    
    def get_time_series(self, name: str, limit: int = 100) -> List[Dict]:
        """获取时间序列数据"""
        series = self._time_series.get(name, deque())
        return list(series)[-limit:]

class MetricsCollector:
    """
    统一的指标收集器
    整合Prometheus、OpenTelemetry和自定义指标
    """
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.prometheus_metrics = None
        self.opentelemetry_metrics = None
        self.custom_metrics = None
        
        if config.enabled:
            self._initialize_collectors()
    
    def _initialize_collectors(self):
        """初始化指标收集器"""
        if self.config.prometheus_enabled:
            self.prometheus_metrics = PrometheusMetrics(self.config.service_name)
            logger.info("Prometheus指标收集器已初始化")
        
        if self.config.opentelemetry_enabled:
            self.opentelemetry_metrics = OpenTelemetryMetrics(self.config)
            logger.info("OpenTelemetry指标收集器已初始化")
        
        if self.config.custom_metrics_enabled:
            self.custom_metrics = CustomMetrics()
            logger.info("自定义指标收集器已初始化")
    
    def record_request(self, metrics: RequestMetrics):
        """记录请求指标"""
        if not self.config.enabled:
            return
        
        # Prometheus指标
        if self.prometheus_metrics:
            labels = [
                metrics.method,
                metrics.path,
                str(metrics.status_code),
                metrics.service_name or 'unknown'
            ]
            
            self.prometheus_metrics.request_count.labels(*labels).inc()
            
            duration_labels = [
                metrics.method,
                metrics.path,
                metrics.service_name or 'unknown'
            ]
            
            self.prometheus_metrics.request_duration.labels(*duration_labels).observe(metrics.response_time)
            self.prometheus_metrics.request_size.labels(*duration_labels).observe(metrics.request_size)
            self.prometheus_metrics.response_size.labels(*duration_labels).observe(metrics.response_size)
        
        # 自定义指标
        if self.custom_metrics:
            self.custom_metrics.record_metric(
                'request_response_time',
                metrics.response_time,
                {
                    'method': metrics.method,
                    'path': metrics.path,
                    'service': metrics.service_name or 'unknown'
                }
            )
    
    def record_cache_hit(self, cache_level: str):
        """记录缓存命中"""
        if self.prometheus_metrics:
            self.prometheus_metrics.cache_hits.labels(cache_level).inc()
    
    def record_cache_miss(self, cache_level: str):
        """记录缓存未命中"""
        if self.prometheus_metrics:
            self.prometheus_metrics.cache_misses.labels(cache_level).inc()
    
    def update_cache_size(self, cache_level: str, size: int):
        """更新缓存大小"""
        if self.prometheus_metrics:
            self.prometheus_metrics.cache_size.labels(cache_level).set(size)
    
    def record_backend_request(self, backend: str, status: str, response_time: float):
        """记录后端请求"""
        if self.prometheus_metrics:
            self.prometheus_metrics.backend_requests.labels(backend, status).inc()
            self.prometheus_metrics.backend_response_time.labels(backend).observe(response_time)
    
    def update_backend_health(self, backend: str, is_healthy: bool):
        """更新后端健康状态"""
        if self.prometheus_metrics:
            self.prometheus_metrics.backend_health.labels(backend).set(1 if is_healthy else 0)
    
    def record_rate_limit_hit(self, limit_type: str, client_id: str):
        """记录限流命中"""
        if self.prometheus_metrics:
            self.prometheus_metrics.rate_limit_hits.labels(limit_type, client_id).inc()
    
    def record_error(self, error_type: str, service: str):
        """记录错误"""
        if self.prometheus_metrics:
            self.prometheus_metrics.errors.labels(error_type, service).inc()
    
    def update_active_connections(self, service: str, count: int):
        """更新活跃连接数"""
        if self.prometheus_metrics:
            self.prometheus_metrics.active_connections.labels(service).set(count)
    
    def update_connection_pool_size(self, service: str, size: int):
        """更新连接池大小"""
        if self.prometheus_metrics:
            self.prometheus_metrics.connection_pool_size.labels(service).set(size)
    
    def update_system_metrics(self, memory_usage: int, cpu_usage: float):
        """更新系统指标"""
        if self.prometheus_metrics:
            self.prometheus_metrics.memory_usage.set(memory_usage)
            self.prometheus_metrics.cpu_usage.set(cpu_usage)
    
    @asynccontextmanager
    async def trace_request(self, operation_name: str, attributes: Dict[str, Any] = None):
        """追踪请求"""
        if self.opentelemetry_metrics:
            async with self.opentelemetry_metrics.trace_request(operation_name, attributes) as span:
                yield span
        else:
            yield None
    
    def record_custom_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """记录自定义指标"""
        if self.custom_metrics:
            self.custom_metrics.record_metric(name, value, labels)
    
    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        if not self.prometheus_metrics:
            return ""
        
        return prometheus_client.generate_latest().decode('utf-8')
    
    def get_custom_metrics_summary(self) -> Dict[str, Dict]:
        """获取自定义指标摘要"""
        if not self.custom_metrics:
            return {}
        
        return {
            name: self.custom_metrics.get_metric_summary(name)
            for name in self.custom_metrics._aggregations.keys()
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """获取健康检查指标"""
        return {
            'prometheus_enabled': self.prometheus_metrics is not None,
            'opentelemetry_enabled': self.opentelemetry_metrics is not None,
            'custom_metrics_enabled': self.custom_metrics is not None,
            'config': {
                'service_name': self.config.service_name,
                'service_version': self.config.service_version,
                'export_interval': self.config.export_interval
            }
        }

class MetricsMiddleware:
    """指标收集中间件"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
    
    async def __call__(self, request, call_next):
        """中间件处理函数"""
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent')
        
        # 计算请求大小
        request_size = 0
        if hasattr(request, 'body'):
            body = await request.body()
            request_size = len(body)
        
        # 追踪请求
        async with self.metrics_collector.trace_request(
            f"{method} {path}",
            {
                'http.method': method,
                'http.url': str(request.url),
                'http.client_ip': client_ip,
                'http.user_agent': user_agent
            }
        ) as span:
            try:
                # 处理请求
                response = await call_next(request)
                
                # 计算响应时间和大小
                response_time = time.time() - start_time
                response_size = 0
                
                if hasattr(response, 'body'):
                    response_size = len(response.body)
                
                # 记录指标
                metrics = RequestMetrics(
                    timestamp=start_time,
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    response_time=response_time,
                    request_size=request_size,
                    response_size=response_size,
                    client_ip=client_ip,
                    user_agent=user_agent
                )
                
                self.metrics_collector.record_request(metrics)
                
                # 更新追踪信息
                if span:
                    span.set_attribute('http.status_code', response.status_code)
                    span.set_attribute('http.response_size', response_size)
                
                return response
                
            except Exception as e:
                # 记录错误
                response_time = time.time() - start_time
                self.metrics_collector.record_error('request_error', 'gateway')
                
                # 更新追踪信息
                if span:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                
                raise

# 全局指标收集器实例
_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> Optional[MetricsCollector]:
    """获取全局指标收集器"""
    return _metrics_collector

def initialize_metrics(config: MetricsConfig) -> MetricsCollector:
    """初始化指标收集器"""
    global _metrics_collector
    _metrics_collector = MetricsCollector(config)
    return _metrics_collector

def setup_instrumentation(app):
    """设置自动化仪表"""
    # FastAPI自动仪表
    FastAPIInstrumentor.instrument_app(app)
    
    # aiohttp客户端自动仪表
    AioHttpClientInstrumentor().instrument()
    
    logger.info("自动化仪表已设置") 