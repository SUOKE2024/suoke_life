"""
性能监控模块
提供全面的性能监控、指标收集和分析功能
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes_sent: int
    network_io_bytes_recv: int
    process_count: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ServiceMetrics:
    """服务指标"""
    request_count: int
    error_count: int
    response_time_avg: float
    response_time_p95: float
    response_time_p99: float
    active_connections: int
    queue_size: int
    cache_hit_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.collection_interval = config.get("collection_interval", 30)
        self.retention_period = config.get("retention_period", 3600)  # 1小时
        
        # 指标存储
        self.metrics_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.retention_period // self.collection_interval)
        )
        
        # Prometheus指标
        self.registry = CollectorRegistry()
        self._init_prometheus_metrics()
        
        # 系统监控
        self.system_monitor = SystemMonitor()
        
        # 收集任务
        self.collection_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        self.request_counter = Counter(
            'medical_resource_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.response_time_histogram = Histogram(
            'medical_resource_response_time_seconds',
            'Response time in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.active_connections_gauge = Gauge(
            'medical_resource_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        self.queue_size_gauge = Gauge(
            'medical_resource_queue_size',
            'Size of request queue',
            registry=self.registry
        )
        
        self.cache_hit_rate_gauge = Gauge(
            'medical_resource_cache_hit_rate',
            'Cache hit rate',
            registry=self.registry
        )
        
        self.system_cpu_gauge = Gauge(
            'medical_resource_system_cpu_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_gauge = Gauge(
            'medical_resource_system_memory_percent',
            'System memory usage percentage',
            registry=self.registry
        )
    
    async def start(self):
        """启动指标收集"""
        if not self.enabled:
            logger.info("性能监控已禁用")
            return
        
        self.is_running = True
        self.collection_task = asyncio.create_task(self._collection_loop())
        logger.info("性能监控已启动")
    
    async def stop(self):
        """停止指标收集"""
        self.is_running = False
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
        logger.info("性能监控已停止")
    
    async def _collection_loop(self):
        """指标收集循环"""
        while self.is_running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集失败: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_metrics(self):
        """收集指标"""
        # 收集系统指标
        system_metrics = await self.system_monitor.get_system_metrics()
        self._store_metric("system_cpu", system_metrics.cpu_percent)
        self._store_metric("system_memory", system_metrics.memory_percent)
        self._store_metric("system_disk", system_metrics.disk_usage_percent)
        
        # 更新Prometheus指标
        self.system_cpu_gauge.set(system_metrics.cpu_percent)
        self.system_memory_gauge.set(system_metrics.memory_percent)
    
    def _store_metric(self, name: str, value: float):
        """存储指标"""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit="percent" if "percent" in name else "count",
            timestamp=datetime.now()
        )
        self.metrics_history[name].append(metric)
    
    def record_request(self, method: str, endpoint: str, status: int, response_time: float):
        """记录请求指标"""
        if not self.enabled:
            return
        
        # Prometheus指标
        self.request_counter.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        self.response_time_histogram.labels(method=method, endpoint=endpoint).observe(response_time)
        
        # 内部指标
        self._store_metric("request_count", 1)
        self._store_metric("response_time", response_time)
        if status >= 400:
            self._store_metric("error_count", 1)
    
    def update_active_connections(self, count: int):
        """更新活跃连接数"""
        if self.enabled:
            self.active_connections_gauge.set(count)
            self._store_metric("active_connections", count)
    
    def update_queue_size(self, size: int):
        """更新队列大小"""
        if self.enabled:
            self.queue_size_gauge.set(size)
            self._store_metric("queue_size", size)
    
    def update_cache_hit_rate(self, rate: float):
        """更新缓存命中率"""
        if self.enabled:
            self.cache_hit_rate_gauge.set(rate)
            self._store_metric("cache_hit_rate", rate)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        summary = {}
        
        for metric_name, history in self.metrics_history.items():
            if not history:
                continue
            
            values = [m.value for m in history]
            summary[metric_name] = {
                "current": values[-1] if values else 0,
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        
        return summary


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.process = psutil.Process()
    
    async def get_system_metrics(self) -> SystemMetrics:
        """获取系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 网络IO
        network_io = psutil.net_io_counters()
        
        # 进程数量
        process_count = len(psutil.pids())
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=disk.percent,
            network_io_bytes_sent=network_io.bytes_sent,
            network_io_bytes_recv=network_io.bytes_recv,
            process_count=process_count
        )


class PerformanceProfiler:
    """性能分析器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.active_profiles: Dict[str, float] = {}
    
    @asynccontextmanager
    async def profile(self, operation_name: str, tags: Dict[str, str] = None):
        """性能分析上下文管理器"""
        start_time = time.time()
        profile_id = f"{operation_name}_{id(self)}"
        
        self.active_profiles[profile_id] = start_time
        
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            # 记录性能指标
            metric = PerformanceMetric(
                name=f"operation_{operation_name}",
                value=duration,
                unit="seconds",
                tags=tags or {},
                description=f"Execution time for {operation_name}"
            )
            
            # 移除活跃分析
            self.active_profiles.pop(profile_id, None)
            
            logger.info(f"操作 {operation_name} 耗时: {duration:.3f}秒", tags=tags)
    
    def get_active_profiles(self) -> Dict[str, float]:
        """获取活跃的性能分析"""
        current_time = time.time()
        return {
            profile_id: current_time - start_time
            for profile_id, start_time in self.active_profiles.items()
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.thresholds = config.get("thresholds", {})
        self.alert_handlers: List[Callable] = []
        
        # 默认阈值
        self.default_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "response_time_avg": 5.0,
            "error_rate": 0.05,
            "queue_size": 1000
        }
        
        # 合并配置的阈值
        self.thresholds = {**self.default_thresholds, **self.thresholds}
    
    def add_alert_handler(self, handler: Callable[[str, Dict[str, Any]], None]):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    async def check_metrics(self, metrics: Dict[str, Any]):
        """检查指标并触发告警"""
        if not self.enabled:
            return
        
        for metric_name, metric_data in metrics.items():
            if metric_name not in self.thresholds:
                continue
            
            threshold = self.thresholds[metric_name]
            current_value = metric_data.get("current", 0)
            
            if current_value > threshold:
                await self._trigger_alert(metric_name, current_value, threshold)
    
    async def _trigger_alert(self, metric_name: str, value: float, threshold: float):
        """触发告警"""
        alert_data = {
            "metric": metric_name,
            "value": value,
            "threshold": threshold,
            "severity": self._get_severity(value, threshold),
            "timestamp": datetime.now().isoformat()
        }
        
        message = f"告警: {metric_name} 超过阈值 (当前值: {value}, 阈值: {threshold})"
        
        logger.warning(message, alert_data=alert_data)
        
        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                await handler(message, alert_data)
            except Exception as e:
                logger.error(f"告警处理器执行失败: {e}")
    
    def _get_severity(self, value: float, threshold: float) -> str:
        """获取告警严重程度"""
        ratio = value / threshold
        if ratio >= 2.0:
            return "critical"
        elif ratio >= 1.5:
            return "high"
        elif ratio >= 1.2:
            return "medium"
        else:
            return "low"


class PerformanceMonitor:
    """性能监控主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # 组件初始化
        self.metrics_collector = MetricsCollector(config.get("metrics", {}))
        self.profiler = PerformanceProfiler(self.metrics_collector)
        self.alert_manager = AlertManager(config.get("alerts", {}))
        
        # 监控任务
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def start(self):
        """启动性能监控"""
        await self.metrics_collector.start()
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("性能监控系统已启动")
    
    async def stop(self):
        """停止性能监控"""
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        await self.metrics_collector.stop()
        logger.info("性能监控系统已停止")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                # 获取指标摘要
                metrics_summary = self.metrics_collector.get_metrics_summary()
                
                # 检查告警
                await self.alert_manager.check_metrics(metrics_summary)
                
                # 等待下一次检查
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环失败: {e}")
                await asyncio.sleep(60)
    
    def get_profiler(self) -> PerformanceProfiler:
        """获取性能分析器"""
        return self.profiler
    
    def get_metrics_collector(self) -> MetricsCollector:
        """获取指标收集器"""
        return self.metrics_collector
    
    def get_alert_manager(self) -> AlertManager:
        """获取告警管理器"""
        return self.alert_manager
    
    async def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        metrics_summary = self.metrics_collector.get_metrics_summary()
        active_profiles = self.profiler.get_active_profiles()
        
        return {
            "status": "healthy" if self.is_running else "unhealthy",
            "metrics_summary": metrics_summary,
            "active_profiles": active_profiles,
            "monitoring_enabled": self.is_running,
            "timestamp": datetime.now().isoformat()
        } 