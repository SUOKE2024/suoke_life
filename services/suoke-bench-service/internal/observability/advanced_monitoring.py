"""高级监控模块

提供系统指标收集、基准测试监控、模型性能监控等功能
"""

import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, Summary, Info

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

from internal.suokebench.config import BenchConfig


@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    disk_used_gb: float
    disk_total_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    gpu_metrics: List[Dict[str, Any]]


@dataclass
class BenchmarkMetrics:
    """基准测试指标"""
    benchmark_id: str
    model_id: str
    task_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    status: str
    samples_processed: int
    samples_per_second: float
    memory_peak_mb: float
    gpu_utilization_percent: float
    error_count: int
    retry_count: int


@dataclass
class ModelMetrics:
    """模型指标"""
    model_id: str
    model_version: str
    load_time_seconds: float
    memory_usage_mb: float
    inference_count: int
    avg_inference_time_ms: float
    error_rate: float
    cache_hit_rate: float


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.system_metrics_history = deque(maxlen=1000)
        self.benchmark_metrics = {}
        self.model_metrics = {}
        
        # Prometheus 指标
        self._init_prometheus_metrics()
        
        # 收集间隔
        self.collection_interval = 5  # 秒
        self.is_collecting = False
        
    def _init_prometheus_metrics(self):
        """初始化 Prometheus 指标"""
        
        # 系统指标
        self.system_cpu_percent = Gauge('system_cpu_percent', 'CPU使用率')
        self.system_memory_percent = Gauge('system_memory_percent', '内存使用率')
        self.system_memory_used_gb = Gauge('system_memory_used_gb', '已使用内存(GB)')
        self.system_disk_percent = Gauge('system_disk_percent', '磁盘使用率')
        self.system_gpu_utilization = Gauge('system_gpu_utilization', 'GPU使用率', ['gpu_id'])
        self.system_gpu_memory_used = Gauge('system_gpu_memory_used', 'GPU内存使用(MB)', ['gpu_id'])
        
        # 基准测试指标
        self.benchmark_requests_total = Counter(
            'benchmark_requests_total',
            '基准测试请求总数',
            ['benchmark_id', 'model_id', 'status']
        )
        
        self.benchmark_duration_seconds = Histogram(
            'benchmark_duration_seconds',
            '基准测试执行时间',
            ['benchmark_id', 'model_id'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600]
        )
        
        self.benchmark_samples_processed = Counter(
            'benchmark_samples_processed_total',
            '处理的样本总数',
            ['benchmark_id', 'model_id']
        )
        
        self.benchmark_samples_per_second = Gauge(
            'benchmark_samples_per_second',
            '每秒处理样本数',
            ['benchmark_id', 'model_id']
        )
        
        self.benchmark_memory_peak_mb = Gauge(
            'benchmark_memory_peak_mb',
            '基准测试内存峰值(MB)',
            ['benchmark_id', 'model_id']
        )
        
        self.benchmark_error_rate = Gauge(
            'benchmark_error_rate',
            '基准测试错误率',
            ['benchmark_id', 'model_id']
        )
        
        # 模型指标
        self.model_load_time_seconds = Histogram(
            'model_load_time_seconds',
            '模型加载时间',
            ['model_id', 'model_version'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
        )
        
        self.model_memory_usage_mb = Gauge(
            'model_memory_usage_mb',
            '模型内存使用(MB)',
            ['model_id', 'model_version']
        )
        
        self.model_inference_time_ms = Histogram(
            'model_inference_time_ms',
            '模型推理时间(毫秒)',
            ['model_id', 'model_version'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
        )
        
        self.model_inference_total = Counter(
            'model_inference_total',
            '模型推理总次数',
            ['model_id', 'model_version', 'status']
        )
        
        self.model_cache_hit_rate = Gauge(
            'model_cache_hit_rate',
            '模型缓存命中率',
            ['model_id', 'model_version']
        )
        
        # 业务指标
        self.active_benchmarks = Gauge('active_benchmarks', '活跃基准测试数量')
        self.queued_benchmarks = Gauge('queued_benchmarks', '排队基准测试数量')
        self.cached_models = Gauge('cached_models', '缓存模型数量')
        self.total_models_registered = Gauge('total_models_registered', '注册模型总数')
        
        # 服务信息
        self.service_info = Info('suokebench_service', 'SuokeBench服务信息')
        self.service_info.info({
            'version': self.config.get('version', '1.0.0'),
            'environment': self.config.get('environment', 'development'),
            'start_time': datetime.now().isoformat()
        })
    
    async def start_collection(self):
        """开始指标收集"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        asyncio.create_task(self._collect_system_metrics())
    
    async def stop_collection(self):
        """停止指标收集"""
        self.is_collecting = False
    
    async def _collect_system_metrics(self):
        """收集系统指标"""
        while self.is_collecting:
            try:
                metrics = await self._get_system_metrics()
                self.system_metrics_history.append(metrics)
                self._update_prometheus_system_metrics(metrics)
                
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                print(f"收集系统指标失败: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _get_system_metrics(self) -> SystemMetrics:
        """获取系统指标"""
        # CPU 指标
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存指标
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # 磁盘指标
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_used_gb = disk.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        
        # 网络指标
        network = psutil.net_io_counters()
        network_bytes_sent = network.bytes_sent
        network_bytes_recv = network.bytes_recv
        
        # GPU 指标
        gpu_metrics = []
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_metrics.append({
                        'id': gpu.id,
                        'name': gpu.name,
                        'utilization': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
                        'temperature': gpu.temperature
                    })
            except Exception:
                # GPU 不可用或未安装 GPU 驱动
                pass
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            disk_usage_percent=disk_usage_percent,
            disk_used_gb=disk_used_gb,
            disk_total_gb=disk_total_gb,
            network_bytes_sent=network_bytes_sent,
            network_bytes_recv=network_bytes_recv,
            gpu_metrics=gpu_metrics
        )
    
    def _update_prometheus_system_metrics(self, metrics: SystemMetrics):
        """更新 Prometheus 系统指标"""
        self.system_cpu_percent.set(metrics.cpu_percent)
        self.system_memory_percent.set(metrics.memory_percent)
        self.system_memory_used_gb.set(metrics.memory_used_gb)
        self.system_disk_percent.set(metrics.disk_usage_percent)
        
        # GPU 指标
        for gpu in metrics.gpu_metrics:
            gpu_id = str(gpu['id'])
            self.system_gpu_utilization.labels(gpu_id=gpu_id).set(gpu['utilization'])
            self.system_gpu_memory_used.labels(gpu_id=gpu_id).set(gpu['memory_used'])
    
    def record_benchmark_start(self, benchmark_id: str, model_id: str, task_id: str):
        """记录基准测试开始"""
        metrics = BenchmarkMetrics(
            benchmark_id=benchmark_id,
            model_id=model_id,
            task_id=task_id,
            start_time=datetime.now(),
            end_time=None,
            duration_seconds=None,
            status="running",
            samples_processed=0,
            samples_per_second=0.0,
            memory_peak_mb=0.0,
            gpu_utilization_percent=0.0,
            error_count=0,
            retry_count=0
        )
        
        self.benchmark_metrics[task_id] = metrics
        self.active_benchmarks.inc()
    
    def record_benchmark_end(
        self,
        task_id: str,
        status: str,
        samples_processed: int,
        memory_peak_mb: float,
        error_count: int = 0,
        retry_count: int = 0
    ):
        """记录基准测试结束"""
        if task_id not in self.benchmark_metrics:
            return
        
        metrics = self.benchmark_metrics[task_id]
        metrics.end_time = datetime.now()
        metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.status = status
        metrics.samples_processed = samples_processed
        metrics.samples_per_second = samples_processed / metrics.duration_seconds if metrics.duration_seconds > 0 else 0
        metrics.memory_peak_mb = memory_peak_mb
        metrics.error_count = error_count
        metrics.retry_count = retry_count
        
        # 更新 Prometheus 指标
        self.benchmark_requests_total.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id,
            status=status
        ).inc()
        
        self.benchmark_duration_seconds.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id
        ).observe(metrics.duration_seconds)
        
        self.benchmark_samples_processed.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id
        ).inc(samples_processed)
        
        self.benchmark_samples_per_second.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id
        ).set(metrics.samples_per_second)
        
        self.benchmark_memory_peak_mb.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id
        ).set(memory_peak_mb)
        
        error_rate = error_count / samples_processed if samples_processed > 0 else 0
        self.benchmark_error_rate.labels(
            benchmark_id=metrics.benchmark_id,
            model_id=metrics.model_id
        ).set(error_rate)
        
        self.active_benchmarks.dec()
    
    def record_model_load(
        self,
        model_id: str,
        model_version: str,
        load_time_seconds: float,
        memory_usage_mb: float
    ):
        """记录模型加载"""
        self.model_load_time_seconds.labels(
            model_id=model_id,
            model_version=model_version
        ).observe(load_time_seconds)
        
        self.model_memory_usage_mb.labels(
            model_id=model_id,
            model_version=model_version
        ).set(memory_usage_mb)
        
        # 更新模型指标
        key = f"{model_id}:{model_version}"
        if key not in self.model_metrics:
            self.model_metrics[key] = ModelMetrics(
                model_id=model_id,
                model_version=model_version,
                load_time_seconds=load_time_seconds,
                memory_usage_mb=memory_usage_mb,
                inference_count=0,
                avg_inference_time_ms=0.0,
                error_rate=0.0,
                cache_hit_rate=0.0
            )
        else:
            self.model_metrics[key].load_time_seconds = load_time_seconds
            self.model_metrics[key].memory_usage_mb = memory_usage_mb
    
    def record_model_inference(
        self,
        model_id: str,
        model_version: str,
        inference_time_ms: float,
        status: str = "success"
    ):
        """记录模型推理"""
        self.model_inference_time_ms.labels(
            model_id=model_id,
            model_version=model_version
        ).observe(inference_time_ms)
        
        self.model_inference_total.labels(
            model_id=model_id,
            model_version=model_version,
            status=status
        ).inc()
        
        # 更新模型指标
        key = f"{model_id}:{model_version}"
        if key in self.model_metrics:
            metrics = self.model_metrics[key]
            metrics.inference_count += 1
            
            # 计算平均推理时间
            if metrics.avg_inference_time_ms == 0:
                metrics.avg_inference_time_ms = inference_time_ms
            else:
                metrics.avg_inference_time_ms = (
                    (metrics.avg_inference_time_ms * (metrics.inference_count - 1) + inference_time_ms)
                    / metrics.inference_count
                )
    
    def record_cache_hit(self, model_id: str, model_version: str, hit: bool):
        """记录缓存命中"""
        key = f"{model_id}:{model_version}"
        if key in self.model_metrics:
            metrics = self.model_metrics[key]
            # 简单的滑动窗口缓存命中率计算
            if not hasattr(metrics, '_cache_hits'):
                metrics._cache_hits = deque(maxlen=100)
            
            metrics._cache_hits.append(1 if hit else 0)
            metrics.cache_hit_rate = sum(metrics._cache_hits) / len(metrics._cache_hits)
            
            self.model_cache_hit_rate.labels(
                model_id=model_id,
                model_version=model_version
            ).set(metrics.cache_hit_rate)
    
    def get_system_metrics_summary(self, minutes: int = 10) -> Dict[str, Any]:
        """获取系统指标摘要"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.system_metrics_history
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "time_range_minutes": minutes,
            "samples_count": len(recent_metrics),
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "average": np.mean(cpu_values),
                "max": np.max(cpu_values),
                "min": np.min(cpu_values)
            },
            "memory": {
                "current": memory_values[-1] if memory_values else 0,
                "average": np.mean(memory_values),
                "max": np.max(memory_values),
                "min": np.min(memory_values)
            },
            "gpu": [
                {
                    "id": gpu["id"],
                    "name": gpu["name"],
                    "utilization": gpu["utilization"],
                    "memory_percent": gpu["memory_percent"]
                }
                for gpu in recent_metrics[-1].gpu_metrics
            ] if recent_metrics and recent_metrics[-1].gpu_metrics else []
        }
    
    def get_benchmark_metrics_summary(self) -> Dict[str, Any]:
        """获取基准测试指标摘要"""
        completed_benchmarks = [
            m for m in self.benchmark_metrics.values()
            if m.status in ["completed", "failed"]
        ]
        
        if not completed_benchmarks:
            return {
                "total_benchmarks": 0,
                "active_benchmarks": len([m for m in self.benchmark_metrics.values() if m.status == "running"]),
                "success_rate": 0.0,
                "average_duration": 0.0,
                "total_samples_processed": 0
            }
        
        successful = [m for m in completed_benchmarks if m.status == "completed"]
        durations = [m.duration_seconds for m in completed_benchmarks if m.duration_seconds]
        
        return {
            "total_benchmarks": len(completed_benchmarks),
            "active_benchmarks": len([m for m in self.benchmark_metrics.values() if m.status == "running"]),
            "success_rate": len(successful) / len(completed_benchmarks),
            "average_duration": np.mean(durations) if durations else 0.0,
            "total_samples_processed": sum(m.samples_processed for m in completed_benchmarks),
            "average_samples_per_second": np.mean([m.samples_per_second for m in successful if m.samples_per_second > 0])
        }
    
    def get_model_metrics_summary(self) -> Dict[str, Any]:
        """获取模型指标摘要"""
        if not self.model_metrics:
            return {
                "total_models": 0,
                "average_load_time": 0.0,
                "total_inferences": 0,
                "average_inference_time": 0.0
            }
        
        load_times = [m.load_time_seconds for m in self.model_metrics.values()]
        inference_times = [m.avg_inference_time_ms for m in self.model_metrics.values() if m.avg_inference_time_ms > 0]
        
        return {
            "total_models": len(self.model_metrics),
            "average_load_time": np.mean(load_times) if load_times else 0.0,
            "total_inferences": sum(m.inference_count for m in self.model_metrics.values()),
            "average_inference_time": np.mean(inference_times) if inference_times else 0.0,
            "models": [
                {
                    "model_id": m.model_id,
                    "model_version": m.model_version,
                    "memory_usage_mb": m.memory_usage_mb,
                    "inference_count": m.inference_count,
                    "avg_inference_time_ms": m.avg_inference_time_ms,
                    "cache_hit_rate": m.cache_hit_rate
                }
                for m in self.model_metrics.values()
            ]
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """导出所有指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_metrics_summary(),
            "benchmarks": self.get_benchmark_metrics_summary(),
            "models": self.get_model_metrics_summary()
        }


# 全局指标收集器
global_metrics_collector: Optional[MetricsCollector] = None


def get_global_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global global_metrics_collector
    if global_metrics_collector is None:
        raise RuntimeError("指标收集器未初始化")
    return global_metrics_collector


def init_metrics_collector(config: Optional[Dict] = None) -> MetricsCollector:
    """初始化指标收集器"""
    global global_metrics_collector
    global_metrics_collector = MetricsCollector(config)
    return global_metrics_collector 