"""
监控指标模块

提供详细的性能监控、指标收集和可观测性功能
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics

from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """指标数据点"""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        初始化指标收集器
        
        Args:
            registry: Prometheus注册表
        """
        self.registry = registry or CollectorRegistry()
        self._lock = threading.RLock()
        
        # 基础指标
        self.benchmark_runs_total = Counter(
            'suoke_benchmark_runs_total',
            'Total number of benchmark runs',
            ['benchmark_id', 'model_id', 'status'],
            registry=self.registry
        )
        
        self.benchmark_duration_seconds = Histogram(
            'suoke_benchmark_duration_seconds',
            'Benchmark execution duration',
            ['benchmark_id', 'model_id'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600],
            registry=self.registry
        )
        
        self.model_inference_duration_seconds = Histogram(
            'suoke_model_inference_duration_seconds',
            'Model inference duration',
            ['model_id', 'model_version', 'task_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10],
            registry=self.registry
        )
        
        self.model_cache_hits_total = Counter(
            'suoke_model_cache_hits_total',
            'Total number of model cache hits',
            ['model_id', 'model_version'],
            registry=self.registry
        )
        
        self.model_cache_misses_total = Counter(
            'suoke_model_cache_misses_total',
            'Total number of model cache misses',
            ['model_id', 'model_version'],
            registry=self.registry
        )
        
        self.active_benchmarks = Gauge(
            'suoke_active_benchmarks',
            'Number of currently running benchmarks',
            registry=self.registry
        )
        
        self.cached_models = Gauge(
            'suoke_cached_models',
            'Number of models in cache',
            registry=self.registry
        )
        
        self.cache_memory_usage_bytes = Gauge(
            'suoke_cache_memory_usage_bytes',
            'Memory usage of model cache in bytes',
            registry=self.registry
        )
        
        self.api_requests_total = Counter(
            'suoke_api_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration_seconds = Histogram(
            'suoke_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5],
            registry=self.registry
        )
        
        # 评测质量指标
        self.benchmark_accuracy = Gauge(
            'suoke_benchmark_accuracy',
            'Benchmark accuracy score',
            ['benchmark_id', 'model_id', 'metric_name'],
            registry=self.registry
        )
        
        self.benchmark_latency_p95 = Gauge(
            'suoke_benchmark_latency_p95_ms',
            'Benchmark 95th percentile latency in milliseconds',
            ['benchmark_id', 'model_id'],
            registry=self.registry
        )
        
        # 系统资源指标
        self.system_cpu_usage = Gauge(
            'suoke_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'suoke_system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'suoke_system_disk_usage_bytes',
            'System disk usage in bytes',
            ['path'],
            registry=self.registry
        )
        
        # 服务信息
        self.service_info = Info(
            'suoke_service_info',
            'Service information',
            registry=self.registry
        )
        
        # 内部指标存储
        self._custom_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        logger.info("指标收集器初始化完成")
    
    def record_benchmark_run(
        self,
        benchmark_id: str,
        model_id: str,
        status: str,
        duration: float
    ):
        """记录基准测试运行"""
        with self._lock:
            self.benchmark_runs_total.labels(
                benchmark_id=benchmark_id,
                model_id=model_id,
                status=status
            ).inc()
            
            if status == "SUCCESS":
                self.benchmark_duration_seconds.labels(
                    benchmark_id=benchmark_id,
                    model_id=model_id
                ).observe(duration)
    
    def record_model_inference(
        self,
        model_id: str,
        model_version: str,
        task_type: str,
        duration: float
    ):
        """记录模型推理"""
        with self._lock:
            self.model_inference_duration_seconds.labels(
                model_id=model_id,
                model_version=model_version,
                task_type=task_type
            ).observe(duration)
    
    def record_cache_hit(self, model_id: str, model_version: str):
        """记录缓存命中"""
        with self._lock:
            self.model_cache_hits_total.labels(
                model_id=model_id,
                model_version=model_version
            ).inc()
    
    def record_cache_miss(self, model_id: str, model_version: str):
        """记录缓存未命中"""
        with self._lock:
            self.model_cache_misses_total.labels(
                model_id=model_id,
                model_version=model_version
            ).inc()
    
    def update_active_benchmarks(self, count: int):
        """更新活跃基准测试数量"""
        self.active_benchmarks.set(count)
    
    def update_cache_stats(self, model_count: int, memory_usage: int):
        """更新缓存统计"""
        self.cached_models.set(model_count)
        self.cache_memory_usage_bytes.set(memory_usage)
    
    def record_api_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """记录API请求"""
        with self._lock:
            self.api_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.api_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    def record_benchmark_quality(
        self,
        benchmark_id: str,
        model_id: str,
        metrics: Dict[str, float]
    ):
        """记录基准测试质量指标"""
        with self._lock:
            for metric_name, value in metrics.items():
                if metric_name in ['accuracy', 'precision', 'recall', 'f1']:
                    self.benchmark_accuracy.labels(
                        benchmark_id=benchmark_id,
                        model_id=model_id,
                        metric_name=metric_name
                    ).set(value)
                elif metric_name == 'latency_p95':
                    self.benchmark_latency_p95.labels(
                        benchmark_id=benchmark_id,
                        model_id=model_id
                    ).set(value)
    
    def update_system_metrics(self, cpu_percent: float, memory_bytes: int, disk_usage: Dict[str, int]):
        """更新系统指标"""
        self.system_cpu_usage.set(cpu_percent)
        self.system_memory_usage.set(memory_bytes)
        
        for path, usage in disk_usage.items():
            self.system_disk_usage.labels(path=path).set(usage)
    
    def set_service_info(self, version: str, build_time: str, git_commit: str = ""):
        """设置服务信息"""
        self.service_info.info({
            'version': version,
            'build_time': build_time,
            'git_commit': git_commit
        })
    
    def record_custom_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """记录自定义指标"""
        with self._lock:
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                labels=labels or {}
            )
            self._custom_metrics[name].append(point)
    
    def get_custom_metric_stats(self, name: str, window_seconds: int = 300) -> Dict[str, float]:
        """获取自定义指标统计"""
        with self._lock:
            if name not in self._custom_metrics:
                return {}
            
            current_time = time.time()
            cutoff_time = current_time - window_seconds
            
            # 过滤时间窗口内的数据点
            recent_points = [
                point for point in self._custom_metrics[name]
                if point.timestamp >= cutoff_time
            ]
            
            if not recent_points:
                return {}
            
            values = [point.value for point in recent_points]
            
            return {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0.0,
                'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
                'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
            }
    
    def export_metrics(self) -> str:
        """导出Prometheus格式的指标"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'active_benchmarks': self.active_benchmarks._value._value,
                'cached_models': self.cached_models._value._value,
                'cache_memory_mb': self.cache_memory_usage_bytes._value._value / 1024 / 1024,
                'system_cpu_percent': self.system_cpu_usage._value._value,
                'system_memory_mb': self.system_memory_usage._value._value / 1024 / 1024,
                'custom_metrics': {
                    name: self.get_custom_metric_stats(name)
                    for name in self._custom_metrics.keys()
                }
            }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        初始化性能监控器
        
        Args:
            metrics_collector: 指标收集器
        """
        self.metrics = metrics_collector
        self._monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self, interval: int = 30):
        """
        开始监控
        
        Args:
            interval: 监控间隔（秒）
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        
        def monitor_loop():
            import psutil
            
            while self._monitoring:
                try:
                    # 收集系统指标
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    disk_usage = {}
                    for partition in psutil.disk_partitions():
                        try:
                            usage = psutil.disk_usage(partition.mountpoint)
                            disk_usage[partition.mountpoint] = usage.used
                        except PermissionError:
                            continue
                    
                    # 更新指标
                    self.metrics.update_system_metrics(
                        cpu_percent=cpu_percent,
                        memory_bytes=memory.used,
                        disk_usage=disk_usage
                    )
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    time.sleep(interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info(f"性能监控已启动，间隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("性能监控已停止")


# 全局指标收集器
_global_metrics: Optional[MetricsCollector] = None
_global_monitor: Optional[PerformanceMonitor] = None


def get_global_metrics() -> MetricsCollector:
    """获取全局指标收集器"""
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = MetricsCollector()
    return _global_metrics


def init_monitoring(registry: Optional[CollectorRegistry] = None) -> tuple[MetricsCollector, PerformanceMonitor]:
    """初始化监控系统"""
    global _global_metrics, _global_monitor
    
    _global_metrics = MetricsCollector(registry)
    _global_monitor = PerformanceMonitor(_global_metrics)
    
    return _global_metrics, _global_monitor


def start_global_monitoring(interval: int = 30):
    """启动全局监控"""
    global _global_monitor
    if _global_monitor is None:
        init_monitoring()
    
    _global_monitor.start_monitoring(interval)


def stop_global_monitoring():
    """停止全局监控"""
    global _global_monitor
    if _global_monitor:
        _global_monitor.stop_monitoring() 