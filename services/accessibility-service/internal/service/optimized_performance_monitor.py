"""
优化版性能监控器
目标：提升监控性能，减少资源占用，支持更高效的数据收集和分析
"""

import asyncio
import gc
import statistics
import threading
import time
import weakref
from collections import deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import psutil


class MetricType(Enum):
    """指标类型枚举"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    RATE = "rate"
    SUMMARY = "summary"


@dataclass
class OptimizedMetric:
    """优化的指标数据结构"""

    name: str
    metric_type: MetricType
    value: float = 0.0
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """优化内存使用"""
        # 使用 __slots__ 减少内存占用
        if not hasattr(self.__class__, "__slots__"):
            self.__class__.__slots__ = [
                "name",
                "metric_type",
                "value",
                "timestamp",
                "labels",
            ]


class OptimizedCircularBuffer:
    """优化的循环缓冲区，内存友好"""

    def __init__(self, max_size: int = 500):  # 减少默认大小
        self.max_size = max_size
        self.data = deque(maxlen=max_size)
        self._lock = threading.RLock()
        self._stats_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 5.0  # 缓存5秒

    def append(self, value: float) -> None:
        """添加数据点"""
        with self._lock:
            self.data.append(value)
            # 清除缓存
            self._stats_cache.clear()

    def get_stats(self) -> dict[str, float]:
        """获取统计信息（带缓存）"""
        current_time = time.time()

        with self._lock:
            # 检查缓存是否有效
            if (
                current_time - self._cache_timestamp < self._cache_ttl
                and self._stats_cache
            ):
                return self._stats_cache.copy()

            if not self.data:
                return {}

            data_list = list(self.data)

            # 计算统计信息
            stats = {
                "count": len(data_list),
                "mean": statistics.mean(data_list),
                "min": min(data_list),
                "max": max(data_list),
            }

            # 只在数据量足够时计算更复杂的统计
            if len(data_list) >= 2:
                stats["stdev"] = statistics.stdev(data_list)
                stats["median"] = statistics.median(data_list)

                # 百分位数（仅在数据量足够时计算）
                if len(data_list) >= 10:
                    sorted_data = sorted(data_list)
                    stats["p95"] = sorted_data[int(0.95 * len(sorted_data))]
                    stats["p99"] = sorted_data[int(0.99 * len(sorted_data))]

            # 更新缓存
            self._stats_cache = stats
            self._cache_timestamp = current_time

            return stats.copy()


class OptimizedPerformanceCollector:
    """优化的性能指标收集器"""

    def __init__(self, max_metrics: int = 1000, cleanup_interval: int = 300):
        self.metrics: dict[str, OptimizedMetric] = {}
        self.metric_history: dict[str, OptimizedCircularBuffer] = {}
        self.max_metrics = max_metrics
        self.cleanup_interval = cleanup_interval

        # 线程安全
        self._lock = threading.RLock()

        # 性能优化
        self._executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="perf_monitor"
        )
        self._last_cleanup = time.time()

        # 弱引用回调，用于自动清理
        self._metric_refs = weakref.WeakValueDictionary()

        # 系统资源监控缓存
        self._system_cache = {}
        self._system_cache_timestamp = 0
        self._system_cache_ttl = 1.0  # 系统信息缓存1秒

    def record_counter(
        self, name: str, value: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """记录计数器指标（优化版）"""
        self._record_metric_fast(
            name, MetricType.COUNTER, value, labels, increment=True
        )

    def record_gauge(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """记录仪表盘指标（优化版）"""
        self._record_metric_fast(name, MetricType.GAUGE, value, labels)

    def record_histogram(
        self, name: str, value: float, labels: dict[str, str] | None = None
    ) -> None:
        """记录直方图指标（优化版）"""
        self._record_metric_fast(
            name, MetricType.HISTOGRAM, value, labels, store_history=True
        )

    def record_timer(
        self, name: str, duration: float, labels: dict[str, str] | None = None
    ) -> None:
        """记录计时器指标（优化版）"""
        self._record_metric_fast(
            name, MetricType.TIMER, duration, labels, store_history=True
        )

    def _record_metric_fast(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        labels: dict[str, str] | None = None,
        increment: bool = False,
        store_history: bool = False,
    ) -> None:
        """快速记录指标的内部方法"""
        current_time = time.time()
        labels = labels or {}

        # 生成指标键
        metric_key = self._generate_metric_key(name, labels)

        with self._lock:
            # 检查是否需要清理
            if current_time - self._last_cleanup > self.cleanup_interval:
                self._cleanup_old_metrics()
                self._last_cleanup = current_time

            # 更新或创建指标
            if metric_key in self.metrics:
                metric = self.metrics[metric_key]
                if increment:
                    metric.value += value
                else:
                    metric.value = value
                metric.timestamp = current_time
            else:
                # 检查指标数量限制
                if len(self.metrics) >= self.max_metrics:
                    self._remove_oldest_metric()

                metric = OptimizedMetric(
                    name=name,
                    metric_type=metric_type,
                    value=value,
                    timestamp=current_time,
                    labels=labels,
                )
                self.metrics[metric_key] = metric

            # 存储历史数据
            if store_history:
                if metric_key not in self.metric_history:
                    self.metric_history[metric_key] = OptimizedCircularBuffer()
                self.metric_history[metric_key].append(value)

    def _generate_metric_key(self, name: str, labels: dict[str, str]) -> str:
        """生成指标键"""
        if not labels:
            return name

        # 优化标签排序和字符串生成
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"

    def _cleanup_old_metrics(self) -> None:
        """清理旧指标"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # 1小时前的指标

        # 清理过期指标
        expired_keys = [
            key
            for key, metric in self.metrics.items()
            if metric.timestamp < cutoff_time
        ]

        for key in expired_keys:
            self.metrics.pop(key, None)
            self.metric_history.pop(key, None)

        # 强制垃圾回收
        if len(expired_keys) > 10:
            gc.collect()

    def _remove_oldest_metric(self) -> None:
        """移除最旧的指标"""
        if not self.metrics:
            return

        oldest_key = min(self.metrics.keys(), key=lambda k: self.metrics[k].timestamp)
        self.metrics.pop(oldest_key, None)
        self.metric_history.pop(oldest_key, None)

    def get_system_metrics(self) -> dict[str, float]:
        """获取系统指标（带缓存）"""
        current_time = time.time()

        # 检查缓存
        if (
            current_time - self._system_cache_timestamp < self._system_cache_ttl
            and self._system_cache
        ):
            return self._system_cache.copy()

        try:
            # 获取系统指标
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics = {
                "system.cpu.usage": cpu_percent,
                "system.memory.usage": memory.percent,
                "system.memory.available": memory.available / (1024**3),  # GB
                "system.disk.usage": disk.percent,
                "system.disk.free": disk.free / (1024**3),  # GB
            }

            # 更新缓存
            self._system_cache = metrics
            self._system_cache_timestamp = current_time

            return metrics.copy()

        except Exception as e:
            print(f"获取系统指标失败: {e}")
            return {}

    def get_metric_stats(
        self, name: str, labels: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """获取指标统计信息"""
        metric_key = self._generate_metric_key(name, labels or {})

        with self._lock:
            result = {"current_value": None, "timestamp": None, "history_stats": {}}

            # 当前值
            if metric_key in self.metrics:
                metric = self.metrics[metric_key]
                result["current_value"] = metric.value
                result["timestamp"] = metric.timestamp

            # 历史统计
            if metric_key in self.metric_history:
                result["history_stats"] = self.metric_history[metric_key].get_stats()

            return result

    def get_all_metrics(self) -> dict[str, dict[str, Any]]:
        """获取所有指标"""
        with self._lock:
            result = {}

            for key, metric in self.metrics.items():
                result[key] = {
                    "name": metric.name,
                    "type": metric.metric_type.value,
                    "value": metric.value,
                    "timestamp": metric.timestamp,
                    "labels": metric.labels,
                    "history_stats": {},
                }

                # 添加历史统计
                if key in self.metric_history:
                    result[key]["history_stats"] = self.metric_history[key].get_stats()

            return result

    def cleanup(self) -> None:
        """清理资源"""
        with self._lock:
            self.metrics.clear()
            self.metric_history.clear()
            self._system_cache.clear()

        self._executor.shutdown(wait=True)


class PerformanceTimer:
    """优化的性能计时器上下文管理器"""

    def __init__(
        self,
        collector: OptimizedPerformanceCollector,
        name: str,
        labels: dict[str, str] | None = None,
    ):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None

    def __enter__(self) -> None:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            self.collector.record_timer(self.name, duration, self.labels)


# 全局优化的性能收集器实例
optimized_performance_collector = OptimizedPerformanceCollector()


def performance_timer(name: str, labels: dict[str, str] | None = None):
    """性能计时装饰器"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            with PerformanceTimer(optimized_performance_collector, name, labels):
                return func(*args, **kwargs)

        return wrapper

    return decorator


async def async_performance_timer(name: str, labels: dict[str, str] | None = None):
    """异步性能计时上下文管理器"""
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start_time
        optimized_performance_collector.record_timer(name, duration, labels)


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def demo_optimized_performance() -> None:
        """演示优化的性能监控"""
        print("🚀 优化性能监控演示")

        collector = OptimizedPerformanceCollector()

        # 记录各种指标
        collector.record_counter("requests.total", 1, {"method": "GET"})
        collector.record_gauge("memory.usage", 75.5)
        collector.record_histogram("response.time", 0.123)

        # 使用计时器
        with PerformanceTimer(collector, "database.query"):
            await asyncio.sleep(0.01)  # 模拟数据库查询

        # 获取系统指标
        system_metrics = collector.get_system_metrics()
        print(f"📊 系统指标: {len(system_metrics)} 项")

        # 获取所有指标
        all_metrics = collector.get_all_metrics()
        print(f"📈 总指标数: {len(all_metrics)}")

        # 性能测试
        start_time = time.perf_counter()
        for i in range(1000):
            collector.record_counter("test.counter", 1)
        duration = time.perf_counter() - start_time
        print(f"⚡ 性能测试: 1000次记录耗时 {duration:.4f}秒")

        collector.cleanup()
        print("✅ 优化性能监控演示完成")

    asyncio.run(demo_optimized_performance())
