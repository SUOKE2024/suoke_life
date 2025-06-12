"""
指标监控模块

提供性能指标收集、监控和报告功能
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import time
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""

    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """系统指标"""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ApplicationMetrics:
    """应用指标"""

    request_count: int = 0
    request_duration_avg: float = 0.0
    error_count: int = 0
    active_connections: int = 0
    cache_hit_rate: float = 0.0
    model_inference_count: int = 0
    model_inference_duration_avg: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """指标收集器"""

    def __init__(self, max_points: int = 1000):
        self.max_points = max_points
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._start_time = time.time()

    def increment_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """增加计数器"""
        key = self._make_key(name, tags)
        self.counters[key] += value

        # 记录时间序列
        self.metrics[key].append(
            MetricPoint(timestamp=datetime.now(), value=self.counters[key], tags=tags or {})
        )

    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """设置仪表盘值"""
        key = self._make_key(name, tags)
        self.gauges[key] = value

        # 记录时间序列
        self.metrics[key].append(
            MetricPoint(timestamp=datetime.now(), value=value, tags=tags or {})
        )

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录直方图值"""
        key = self._make_key(name, tags)
        self.histograms[key].append(value)

        # 保持最近1000个值
        if len(self.histograms[key]) > 1000:
            self.histograms[key] = self.histograms[key][-1000:]

        # 记录时间序列
        self.metrics[key].append(
            MetricPoint(timestamp=datetime.now(), value=value, tags=tags or {})
        )

    def _make_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """生成指标键"""
        if not tags:
            return name

        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"

    def get_counter(self, name: str, tags: Dict[str, str] = None) -> int:
        """获取计数器值"""
        key = self._make_key(name, tags)
        return self.counters.get(key, 0)

    def get_gauge(self, name: str, tags: Dict[str, str] = None) -> float:
        """获取仪表盘值"""
        key = self._make_key(name, tags)
        return self.gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """获取直方图统计"""
        key = self._make_key(name, tags)
        values = self.histograms.get(key, [])

        if not values:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_values = sorted(values)
        count = len(sorted_values)

        return {
            "count": count,
            "avg": sum(sorted_values) / count,
            "min": sorted_values[0],
            "max": sorted_values[-1],
            "p95": sorted_values[int(count * 0.95)] if count > 0 else 0.0,
            "p99": sorted_values[int(count * 0.99)] if count > 0 else 0.0,
        }

    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        return time.time() - self._start_time


class SystemMonitor:
    """系统监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.process = psutil.Process()

    async def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用情况
            memory = psutil.virtual_memory()

            # 磁盘使用情况
            disk = psutil.disk_usage('/')

            # 网络使用情况
            network = psutil.net_io_counters()

            # 进程数量
            process_count = len(psutil.pids())

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_percent=disk.percent,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                process_count=process_count,
            )

            # 记录到指标收集器
            self.metrics_collector.set_gauge("system.cpu.percent", cpu_percent)
            self.metrics_collector.set_gauge("system.memory.percent", memory.percent)
            self.metrics_collector.set_gauge("system.memory.used_mb", memory.used / 1024 / 1024)
            self.metrics_collector.set_gauge("system.disk.percent", disk.percent)
            self.metrics_collector.set_gauge("system.process.count", process_count)

            return metrics

        except Exception as e:
            logger.error(f"系统指标收集失败: {e}")
            raise


class ApplicationMonitor:
    """应用监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.request_durations = deque(maxlen=1000)
        self.model_inference_durations = deque(maxlen=1000)

    def record_request(self, duration: float, status_code: int, endpoint: str):
        """记录请求"""
        self.request_durations.append(duration)

        # 记录指标
        self.metrics_collector.increment_counter(
            "http.requests.total", tags={"status_code": str(status_code), "endpoint": endpoint}
        )

        self.metrics_collector.record_histogram(
            "http.request.duration", duration, tags={"endpoint": endpoint}
        )

        if status_code >= 400:
            self.metrics_collector.increment_counter(
                "http.errors.total", tags={"status_code": str(status_code), "endpoint": endpoint}
            )

    def record_model_inference(self, duration: float, model_name: str, success: bool):
        """记录模型推理"""
        self.model_inference_durations.append(duration)

        # 记录指标
        self.metrics_collector.increment_counter(
            "model.inference.total", tags={"model_name": model_name, "success": str(success)}
        )

        self.metrics_collector.record_histogram(
            "model.inference.duration", duration, tags={"model_name": model_name}
        )

        if not success:
            self.metrics_collector.increment_counter(
                "model.inference.errors", tags={"model_name": model_name}
            )

    def get_application_metrics(self) -> ApplicationMetrics:
        """获取应用指标"""
        request_count = self.metrics_collector.get_counter("http.requests.total")
        error_count = self.metrics_collector.get_counter("http.errors.total")
        model_inference_count = self.metrics_collector.get_counter("model.inference.total")

        # 计算平均响应时间
        request_duration_avg = (
            sum(self.request_durations) / len(self.request_durations)
            if self.request_durations
            else 0.0
        )

        # 计算平均推理时间
        model_inference_duration_avg = (
            sum(self.model_inference_durations) / len(self.model_inference_durations)
            if self.model_inference_durations
            else 0.0
        )

        return ApplicationMetrics(
            request_count=request_count,
            request_duration_avg=request_duration_avg,
            error_count=error_count,
            model_inference_count=model_inference_count,
            model_inference_duration_avg=model_inference_duration_avg,
        )


class MetricsExporter:
    """指标导出器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector

    def export_prometheus_format(self) -> str:
        """导出Prometheus格式指标"""
        lines = []

        # 导出计数器
        for key, value in self.metrics_collector.counters.items():
            metric_name = key.split('[')[0]
            lines.append(f"# TYPE {metric_name} counter")
            lines.append(f"{key} {value}")

        # 导出仪表盘
        for key, value in self.metrics_collector.gauges.items():
            metric_name = key.split('[')[0]
            lines.append(f"# TYPE {metric_name} gauge")
            lines.append(f"{key} {value}")

        return "\n".join(lines)

    def export_json_format(self) -> Dict[str, Any]:
        """导出JSON格式指标"""
        return {
            "counters": dict(self.metrics_collector.counters),
            "gauges": dict(self.metrics_collector.gauges),
            "histograms": {
                key: self.metrics_collector.get_histogram_stats(key.split('[')[0])
                for key in self.metrics_collector.histograms.keys()
            },
            "uptime": self.metrics_collector.get_uptime(),
            "timestamp": datetime.now().isoformat(),
        }


# 全局指标收集器实例
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
application_monitor = ApplicationMonitor(metrics_collector)
metrics_exporter = MetricsExporter(metrics_collector)
