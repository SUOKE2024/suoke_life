"""
metrics - 索克生活项目模块
"""

            import asyncio
        import asyncio
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from prometheus_client import (
from typing import Any
import logging
import time

#!/usr/bin/env python3
"""
指标收集模块
提供Prometheus指标收集、自定义指标和指标聚合功能
"""


    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    push_to_gateway,
)

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricConfig:
    """指标配置"""

    name: str
    description: str
    metric_type: MetricType
    labels: list[str] = None
    buckets: list[float] = None  # 用于Histogram

    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if self.buckets is None and self.metric_type == MetricType.HISTOGRAM:
            # 默认的bucket配置
            self.buckets = [
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ]


class MetricsCollector:
    """指标收集器"""

    def __init__(
        self,
        service_name: str,
        namespace: str = "suoke_life",
        registry: CollectorRegistry | None = None,
    ):
        self.service_name = service_name
        self.namespace = namespace
        self.registry = registry or REGISTRY
        self.metrics: dict[str, Any] = {}

        # 预定义的通用指标
        self._init_common_metrics()

        logger.info(f"指标收集器初始化: {service_name}")

    def _init_common_metrics(self):
        """初始化通用指标"""
        # HTTP请求指标
        self.register_metric(
            MetricConfig(
                name="http_requests_total",
                description="Total HTTP requests",
                metric_type=MetricType.COUNTER,
                labels=["method", "endpoint", "status"],
            )
        )

        self.register_metric(
            MetricConfig(
                name="http_request_duration_seconds",
                description="HTTP request duration in seconds",
                metric_type=MetricType.HISTOGRAM,
                labels=["method", "endpoint"],
            )
        )

        # 数据库操作指标
        self.register_metric(
            MetricConfig(
                name="db_operations_total",
                description="Total database operations",
                metric_type=MetricType.COUNTER,
                labels=["operation", "table", "status"],
            )
        )

        self.register_metric(
            MetricConfig(
                name="db_operation_duration_seconds",
                description="Database operation duration in seconds",
                metric_type=MetricType.HISTOGRAM,
                labels=["operation", "table"],
            )
        )

        # 缓存指标
        self.register_metric(
            MetricConfig(
                name="cache_operations_total",
                description="Total cache operations",
                metric_type=MetricType.COUNTER,
                labels=["operation", "cache_name", "status"],
            )
        )

        # 业务指标
        self.register_metric(
            MetricConfig(
                name="business_operations_total",
                description="Total business operations",
                metric_type=MetricType.COUNTER,
                labels=["operation", "status"],
            )
        )

        # 系统资源指标
        self.register_metric(
            MetricConfig(
                name="active_connections",
                description="Number of active connections",
                metric_type=MetricType.GAUGE,
                labels=["connection_type"],
            )
        )

        self.register_metric(
            MetricConfig(
                name="queue_size",
                description="Size of various queues",
                metric_type=MetricType.GAUGE,
                labels=["queue_name"],
            )
        )

    def register_metric(self, config: MetricConfig) -> Any:
        """注册指标"""
        metric_name = f"{self.namespace}_{self.service_name}_{config.name}"

        if metric_name in self.metrics:
            return self.metrics[metric_name]

        # 创建指标
        if config.metric_type == MetricType.COUNTER:
            metric = Counter(
                metric_name, config.description, config.labels, registry=self.registry
            )
        elif config.metric_type == MetricType.GAUGE:
            metric = Gauge(
                metric_name, config.description, config.labels, registry=self.registry
            )
        elif config.metric_type == MetricType.HISTOGRAM:
            metric = Histogram(
                metric_name,
                config.description,
                config.labels,
                buckets=config.buckets,
                registry=self.registry,
            )
        elif config.metric_type == MetricType.SUMMARY:
            metric = Summary(
                metric_name, config.description, config.labels, registry=self.registry
            )
        else:
            raise ValueError(f"不支持的指标类型: {config.metric_type}")

        self.metrics[metric_name] = metric
        logger.debug(f"注册指标: {metric_name}")

        return metric

    def get_metric(self, name: str) -> Any:
        """获取指标"""
        metric_name = f"{self.namespace}_{self.service_name}_{name}"
        return self.metrics.get(metric_name)

    def increment_counter(
        self, name: str, labels: dict[str, str] | None = None, value: float = 1
    ):
        """增加计数器"""
        metric = self.get_metric(name)
        if metric:
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None):
        """设置仪表值"""
        metric = self.get_metric(name)
        if metric:
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)

    def observe_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ):
        """观察直方图值"""
        metric = self.get_metric(name)
        if metric:
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)

    @contextmanager
    def timer(self, name: str, labels: dict[str, str] | None = None):
        """计时器上下文管理器"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.observe_histogram(name, duration, labels)

    def track_http_request(
        self, method: str, endpoint: str, status: int, duration: float
    ):
        """跟踪HTTP请求"""
        # 增加请求计数
        self.increment_counter(
            "http_requests_total",
            {"method": method, "endpoint": endpoint, "status": str(status)},
        )

        # 记录请求时长
        self.observe_histogram(
            "http_request_duration_seconds",
            duration,
            {"method": method, "endpoint": endpoint},
        )

    def track_db_operation(
        self, operation: str, table: str, status: str, duration: float
    ):
        """跟踪数据库操作"""
        # 增加操作计数
        self.increment_counter(
            "db_operations_total",
            {"operation": operation, "table": table, "status": status},
        )

        # 记录操作时长
        self.observe_histogram(
            "db_operation_duration_seconds",
            duration,
            {"operation": operation, "table": table},
        )

    def track_cache_operation(self, operation: str, cache_name: str, status: str):
        """跟踪缓存操作"""
        self.increment_counter(
            "cache_operations_total",
            {"operation": operation, "cache_name": cache_name, "status": status},
        )

    def track_business_operation(self, operation: str, status: str):
        """跟踪业务操作"""
        self.increment_counter(
            "business_operations_total", {"operation": operation, "status": status}
        )

    def export_metrics(self) -> bytes:
        """导出指标（Prometheus格式）"""
        return generate_latest(self.registry)

    def push_to_gateway(self, gateway_url: str, job: str):
        """推送指标到Pushgateway"""
        try:
            push_to_gateway(gateway_url, job=job, registry=self.registry)
            logger.info(f"指标已推送到 {gateway_url}")
        except Exception as e:
            logger.error(f"推送指标失败: {e}")


class MetricsMiddleware:
    """指标收集中间件"""

    def __init__(self, collector: MetricsCollector):
        self.collector = collector

    def track_request(self):
        """请求跟踪装饰器"""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time

                    # 从函数参数中提取信息
                    method = kwargs.get("method", "UNKNOWN")
                    endpoint = kwargs.get("endpoint", func.__name__)
                    status_code = 200 if status == "success" else 500

                    self.collector.track_http_request(
                        method, endpoint, status_code, duration
                    )

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time

                    # 从函数参数中提取信息
                    method = kwargs.get("method", "UNKNOWN")
                    endpoint = kwargs.get("endpoint", func.__name__)
                    status_code = 200 if status == "success" else 500

                    self.collector.track_http_request(
                        method, endpoint, status_code, duration
                    )

            # 根据函数类型返回相应的包装器

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def track_db_operation(self, operation: str, table: str):
        """数据库操作跟踪装饰器"""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    self.collector.track_db_operation(
                        operation, table, status, duration
                    )

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"

                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    status = "error"
                    raise
                finally:
                    duration = time.time() - start_time
                    self.collector.track_db_operation(
                        operation, table, status, duration
                    )

            # 根据函数类型返回相应的包装器

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator


# 全局指标收集器注册表
_collectors: dict[str, MetricsCollector] = {}


def get_metrics_collector(
    service_name: str, namespace: str = "suoke_life"
) -> MetricsCollector:
    """获取或创建指标收集器"""
    if service_name not in _collectors:
        _collectors[service_name] = MetricsCollector(service_name, namespace)

    return _collectors[service_name]


# 便捷装饰器
def track_metrics(metric_type: str = "http_request", **kwargs):
    """
    通用指标跟踪装饰器

    Args:
        metric_type: 指标类型 (http_request, db_operation, business_operation)
        **kwargs: 额外参数
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs_inner):
            # 获取服务名（从模块名推断）
            service_name = func.__module__.split(".")[0]
            collector = get_metrics_collector(service_name)

            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs_inner)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time

                if metric_type == "http_request":
                    method = kwargs.get("method", "UNKNOWN")
                    endpoint = kwargs.get("endpoint", func.__name__)
                    status_code = 200 if status == "success" else 500
                    collector.track_http_request(
                        method, endpoint, status_code, duration
                    )

                elif metric_type == "db_operation":
                    operation = kwargs.get("operation", "query")
                    table = kwargs.get("table", "unknown")
                    collector.track_db_operation(operation, table, status, duration)

                elif metric_type == "business_operation":
                    operation = kwargs.get("operation", func.__name__)
                    collector.track_business_operation(operation, status)

        @wraps(func)
        def sync_wrapper(*args, **kwargs_inner):
            # 获取服务名（从模块名推断）
            service_name = func.__module__.split(".")[0]
            collector = get_metrics_collector(service_name)

            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs_inner)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time

                if metric_type == "http_request":
                    method = kwargs.get("method", "UNKNOWN")
                    endpoint = kwargs.get("endpoint", func.__name__)
                    status_code = 200 if status == "success" else 500
                    collector.track_http_request(
                        method, endpoint, status_code, duration
                    )

                elif metric_type == "db_operation":
                    operation = kwargs.get("operation", "query")
                    table = kwargs.get("table", "unknown")
                    collector.track_db_operation(operation, table, status, duration)

                elif metric_type == "business_operation":
                    operation = kwargs.get("operation", func.__name__)
                    collector.track_business_operation(operation, status)

        # 根据函数类型返回相应的包装器

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
