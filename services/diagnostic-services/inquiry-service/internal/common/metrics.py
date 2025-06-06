"""
metrics - 索克生活项目模块
"""

    from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
import asyncio
import logging
import threading
import time

#!/usr/bin/env python

"""
性能监控和指标收集模块
"""


try:

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


@dataclass
class MetricPoint:
    """指标数据点"""

    name: str
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
        }


@dataclass
class PerformanceStats:
    """性能统计信息"""

    operation: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    error_count: int = 0

    @property
    def avg_time(self) -> float:
        """平均执行时间"""
        return self.total_time / self.count if self.count > 0 else 0.0

    @property
    def error_rate(self) -> float:
        """错误率"""
        return self.error_count / self.count if self.count > 0 else 0.0

    def add_measurement(self, duration: float, is_error: bool = False) -> None:
        """添加测量数据"""
        self.count += 1
        self.total_time += duration
        self.min_time = min(self.min_time, duration)
        self.max_time = max(self.max_time, duration)

        if is_error:
            self.error_count += 1

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "operation": self.operation,
            "count": self.count,
            "total_time": self.total_time,
            "avg_time": self.avg_time,
            "min_time": self.min_time if self.min_time != float("inf") else 0.0,
            "max_time": self.max_time,
            "error_count": self.error_count,
            "error_rate": self.error_rate,
        }


class MetricsCollector:
    """指标收集器"""

    def __init__(self, enable_prometheus: bool = False, prometheus_port: int = 8000):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.prometheus_port = prometheus_port

        # 内存中的指标存储
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)
        self._performance_stats: dict[str, PerformanceStats] = {}
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}

        # 时间窗口配置
        self.max_points_per_metric = 1000
        self.retention_hours = 24

        # 线程锁
        self._lock = threading.RLock()

        # Prometheus指标
        if self.enable_prometheus:
            self._setup_prometheus_metrics()

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info(f"指标收集器初始化完成，Prometheus: {self.enable_prometheus}")

    def _setup_prometheus_metrics(self) -> None:
        """设置Prometheus指标"""
        if not PROMETHEUS_AVAILABLE:
            return

        # 计数器
        self.prom_request_total = Counter(
            "inquiry_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
        )

        self.prom_symptom_extractions_total = Counter(
            "symptom_extractions_total",
            "Total number of symptom extractions",
            ["status"],
        )

        self.prom_tcm_mappings_total = Counter(
            "tcm_mappings_total", "Total number of TCM pattern mappings", ["status"]
        )

        self.prom_risk_assessments_total = Counter(
            "risk_assessments_total", "Total number of risk assessments", ["status"]
        )

        # 直方图（用于延迟测量）
        self.prom_request_duration = Histogram(
            "inquiry_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
        )

        self.prom_symptom_extraction_duration = Histogram(
            "symptom_extraction_duration_seconds",
            "Symptom extraction duration in seconds",
        )

        self.prom_tcm_mapping_duration = Histogram(
            "tcm_mapping_duration_seconds", "TCM pattern mapping duration in seconds"
        )

        self.prom_risk_assessment_duration = Histogram(
            "risk_assessment_duration_seconds", "Risk assessment duration in seconds"
        )

        # 仪表盘
        self.prom_active_sessions = Gauge(
            "inquiry_active_sessions", "Number of active inquiry sessions"
        )

        self.prom_cache_size = Gauge("inquiry_cache_size", "Current cache size")

        self.prom_memory_usage = Gauge(
            "inquiry_memory_usage_bytes", "Memory usage in bytes"
        )

        # 信息
        self.prom_service_info = Info("inquiry_service_info", "Service information")

    def start_prometheus_server(self) -> None:
        """启动Prometheus HTTP服务器"""
        if not self.enable_prometheus:
            return

        try:
            start_http_server(self.prometheus_port)
            self._logger.info(f"Prometheus指标服务器启动在端口 {self.prometheus_port}")
        except Exception as e:
            self._logger.error(f"启动Prometheus服务器失败: {e!s}")

    def record_metric(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """记录指标"""
        with self._lock:
            point = MetricPoint(
                name=name, value=value, timestamp=datetime.now(), labels=labels or {}
            )

            self._metrics[name].append(point)

            # 清理旧数据
            self._cleanup_old_metrics(name)

    def increment_counter(
        self, name: str, value: int = 1, labels: dict[str, str] | None = None
    ) -> None:
        """增加计数器"""
        with self._lock:
            key = f"{name}:{labels}" if labels else name
            self._counters[key] += value

            # 记录到时间序列
            self.record_metric(f"{name}_total", self._counters[key], labels)

            # Prometheus计数器
            if self.enable_prometheus and hasattr(self, "prom_request_total"):
                if name == "requests":
                    self.prom_request_total.labels(**labels).inc(value)
                elif name == "symptom_extractions":
                    self.prom_symptom_extractions_total.labels(**labels).inc(value)
                elif name == "tcm_mappings":
                    self.prom_tcm_mappings_total.labels(**labels).inc(value)
                elif name == "risk_assessments":
                    self.prom_risk_assessments_total.labels(**labels).inc(value)

    def set_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """设置仪表盘值"""
        with self._lock:
            key = f"{name}:{labels}" if labels else name
            self._gauges[key] = value

            # 记录到时间序列
            self.record_metric(name, value, labels)

            # Prometheus仪表盘
            if self.enable_prometheus:
                if name == "active_sessions" and hasattr(self, "prom_active_sessions"):
                    self.prom_active_sessions.set(value)
                elif name == "cache_size" and hasattr(self, "prom_cache_size"):
                    self.prom_cache_size.set(value)
                elif name == "memory_usage" and hasattr(self, "prom_memory_usage"):
                    self.prom_memory_usage.set(value)

    def record_duration(
        self,
        operation: str,
        duration: float,
        is_error: bool = False,
        labels: dict[str, str] | None = None,
    ) -> None:
        """记录操作持续时间"""
        with self._lock:
            # 更新性能统计
            if operation not in self._performance_stats:
                self._performance_stats[operation] = PerformanceStats(operation)

            self._performance_stats[operation].add_measurement(duration, is_error)

            # 记录到时间序列
            self.record_metric(f"{operation}_duration", duration, labels)

            # Prometheus直方图
            if self.enable_prometheus:
                if operation == "request" and hasattr(self, "prom_request_duration"):
                    self.prom_request_duration.labels(**labels).observe(duration)
                elif operation == "symptom_extraction" and hasattr(
                    self, "prom_symptom_extraction_duration"
                ):
                    self.prom_symptom_extraction_duration.observe(duration)
                elif operation == "tcm_mapping" and hasattr(
                    self, "prom_tcm_mapping_duration"
                ):
                    self.prom_tcm_mapping_duration.observe(duration)
                elif operation == "risk_assessment" and hasattr(
                    self, "prom_risk_assessment_duration"
                ):
                    self.prom_risk_assessment_duration.observe(duration)

    def get_metrics(
        self,
        name: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """获取指标数据"""
        with self._lock:
            result = {}

            metrics_to_query = [name] if name else list(self._metrics.keys())

            for metric_name in metrics_to_query:
                if metric_name not in self._metrics:
                    continue

                points = self._metrics[metric_name]

                # 时间过滤
                if start_time or end_time:
                    filtered_points = []
                    for point in points:
                        if start_time and point.timestamp < start_time:
                            continue
                        if end_time and point.timestamp > end_time:
                            continue
                        filtered_points.append(point)
                    points = filtered_points

                result[metric_name] = [point.to_dict() for point in points]

            return result

    def get_performance_stats(
        self, operation: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """获取性能统计信息"""
        with self._lock:
            if operation:
                if operation in self._performance_stats:
                    return {operation: self._performance_stats[operation].to_dict()}
                else:
                    return {}

            return {
                op: stats.to_dict() for op, stats in self._performance_stats.items()
            }

    def get_counters(self) -> dict[str, int]:
        """获取计数器值"""
        with self._lock:
            return dict(self._counters)

    def get_gauges(self) -> dict[str, float]:
        """获取仪表盘值"""
        with self._lock:
            return dict(self._gauges)

    def get_summary(self) -> dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            return {
                "metrics_count": len(self._metrics),
                "total_data_points": sum(
                    len(points) for points in self._metrics.values()
                ),
                "performance_stats": self.get_performance_stats(),
                "counters": self.get_counters(),
                "gauges": self.get_gauges(),
                "collection_time": datetime.now().isoformat(),
            }

    def _cleanup_old_metrics(self, name: str) -> None:
        """清理旧的指标数据"""
        points = self._metrics[name]

        # 按数量限制
        if len(points) > self.max_points_per_metric:
            self._metrics[name] = points[-self.max_points_per_metric :]

        # 按时间限制
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        self._metrics[name] = [
            point for point in self._metrics[name] if point.timestamp > cutoff_time
        ]

    def clear_metrics(self, name: str | None = None) -> None:
        """清空指标数据"""
        with self._lock:
            if name:
                if name in self._metrics:
                    del self._metrics[name]
                if name in self._performance_stats:
                    del self._performance_stats[name]
            else:
                self._metrics.clear()
                self._performance_stats.clear()
                self._counters.clear()
                self._gauges.clear()

        self._logger.info(f"指标数据已清空: {name or 'all'}")


def timer(
    metrics: MetricsCollector, operation: str, labels: dict[str, str] | None = None
):
    """计时装饰器"""

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            is_error = False

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                is_error = True
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_duration(operation, duration, is_error, labels)

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            is_error = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                is_error = True
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_duration(operation, duration, is_error, labels)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def counter(metrics: MetricsCollector, name: str, labels: dict[str, str] | None = None):
    """计数装饰器"""

    def decorator(func: Callable) -> Callable:
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                metrics.increment_counter(
                    name, 1, {**(labels or {}), "status": "success"}
                )
                return result
            except Exception:
                metrics.increment_counter(
                    name, 1, {**(labels or {}), "status": "error"}
                )
                raise

        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metrics.increment_counter(
                    name, 1, {**(labels or {}), "status": "success"}
                )
                return result
            except Exception:
                metrics.increment_counter(
                    name, 1, {**(labels or {}), "status": "error"}
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
