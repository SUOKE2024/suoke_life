"""
监控服务
提供Prometheus指标收集和性能监控功能
"""

from functools import wraps
import time
from typing import Any

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from app.core.logger import get_logger

# Prometheus 内容类型常量
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


class MetricsService:
    """监控服务"""

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or CollectorRegistry()
        self.logger = get_logger()

        # 初始化指标
        self._init_metrics()

    def _init_metrics(self):
        """初始化Prometheus指标"""

        # HTTP请求指标
        self.http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.http_request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # 数据库操作指标
        self.db_operations_total = Counter(
            "db_operations_total",
            "Total database operations",
            ["operation", "status"],
            registry=self.registry,
        )

        self.db_operation_duration = Histogram(
            "db_operation_duration_seconds",
            "Database operation duration in seconds",
            ["operation"],
            registry=self.registry,
        )

        # 缓存指标
        self.cache_operations_total = Counter(
            "cache_operations_total",
            "Total cache operations",
            ["operation", "status"],
            registry=self.registry,
        )

        self.cache_hit_ratio = Gauge("cache_hit_ratio", "Cache hit ratio", registry=self.registry)

        # 知识图谱指标
        self.graph_queries_total = Counter(
            "graph_queries_total",
            "Total graph queries",
            ["query_type", "status"],
            registry=self.registry,
        )

        self.graph_query_duration = Histogram(
            "graph_query_duration_seconds",
            "Graph query duration in seconds",
            ["query_type"],
            registry=self.registry,
        )

        # 业务指标
        self.knowledge_requests_total = Counter(
            "knowledge_requests_total",
            "Total knowledge requests",
            ["entity_type", "operation"],
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "active_connections", "Number of active connections", registry=self.registry
        )

        # 系统指标
        self.memory_usage = Gauge(
            "memory_usage_bytes", "Memory usage in bytes", registry=self.registry
        )

        self.cpu_usage = Gauge("cpu_usage_percent", "CPU usage percentage", registry=self.registry)

        # 应用信息
        self.app_info = Info("app_info", "Application information", registry=self.registry)

        # 设置应用信息
        self.app_info.info(
            {"version": "1.0.0", "service": "med-knowledge", "environment": "production"}
        )

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录HTTP请求指标"""
        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_db_operation(self, operation: str, status: str, duration: float):
        """记录数据库操作指标"""
        self.db_operations_total.labels(operation=operation, status=status).inc()

        self.db_operation_duration.labels(operation=operation).observe(duration)

    def record_cache_operation(self, operation: str, status: str):
        """记录缓存操作指标"""
        self.cache_operations_total.labels(operation=operation, status=status).inc()

    def update_cache_hit_ratio(self, ratio: float):
        """更新缓存命中率"""
        self.cache_hit_ratio.set(ratio)

    def record_graph_query(self, query_type: str, status: str, duration: float):
        """记录图查询指标"""
        self.graph_queries_total.labels(query_type=query_type, status=status).inc()

        self.graph_query_duration.labels(query_type=query_type).observe(duration)

    def record_knowledge_request(self, entity_type: str, operation: str):
        """记录知识请求指标"""
        self.knowledge_requests_total.labels(entity_type=entity_type, operation=operation).inc()

    def update_active_connections(self, count: int):
        """更新活跃连接数"""
        self.active_connections.set(count)

    def update_memory_usage(self, bytes_used: int):
        """更新内存使用量"""
        self.memory_usage.set(bytes_used)

    def update_cpu_usage(self, percentage: float):
        """更新CPU使用率"""
        self.cpu_usage.set(percentage)

    def get_metrics(self) -> str:
        """获取Prometheus格式的指标数据"""
        return generate_latest(self.registry).decode("utf-8")

    def get_content_type(self) -> str:
        """获取指标内容类型"""
        return CONTENT_TYPE_LATEST

    def get_summary(self) -> dict[str, Any]:
        """获取指标摘要"""
        try:
            # 这里可以添加更复杂的指标聚合逻辑
            return {
                "total_requests": self._get_counter_value(self.http_requests_total),
                "total_db_operations": self._get_counter_value(self.db_operations_total),
                "total_cache_operations": self._get_counter_value(self.cache_operations_total),
                "total_graph_queries": self._get_counter_value(self.graph_queries_total),
                "active_connections": self.active_connections._value._value,
                "cache_hit_ratio": self.cache_hit_ratio._value._value,
            }
        except Exception as e:
            self.logger.error(f"获取指标摘要失败: {e}")
            return {}

    def _get_counter_value(self, counter: Counter) -> float:
        """获取计数器总值"""
        try:
            total = 0
            for sample in counter.collect()[0].samples:
                total += sample.value
            return total
        except Exception:
            return 0.0


def monitor_performance(metrics_service: MetricsService | None = None):
    """性能监控装饰器"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not metrics_service:
                return await func(*args, **kwargs)

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
                operation = func.__name__

                if "db" in operation.lower() or "repository" in operation.lower():
                    metrics_service.record_db_operation(operation, status, duration)
                elif "cache" in operation.lower():
                    metrics_service.record_cache_operation(operation, status)
                elif "graph" in operation.lower():
                    metrics_service.record_graph_query(operation, status, duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not metrics_service:
                return func(*args, **kwargs)

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
                operation = func.__name__

                if "db" in operation.lower() or "repository" in operation.lower():
                    metrics_service.record_db_operation(operation, status, duration)
                elif "cache" in operation.lower():
                    metrics_service.record_cache_operation(operation, status)
                elif "graph" in operation.lower():
                    metrics_service.record_graph_query(operation, status, duration)

        # 检查函数是否是协程
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
