"""
性能监控模块

提供性能监控、指标收集和性能分析功能。
"""

import asyncio
import functools
import psutil
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import structlog
from prometheus_client import Counter, Histogram, Gauge, start_http_server

from ..config.settings import get_settings

logger = structlog.get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """性能指标"""
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: float
    function_name: str
    args_count: int
    kwargs_count: int


@dataclass
class SystemMetrics:
    """系统指标"""
    cpu_percent: float
    memory_percent: float
    memory_available: int
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: float


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.function_stats: Dict[str, List[float]] = defaultdict(list)
        self.system_metrics: deque = deque(maxlen=100)
        
        # Prometheus指标
        self.request_count = Counter(
            'listen_service_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'listen_service_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.audio_analysis_duration = Histogram(
            'listen_service_audio_analysis_duration_seconds',
            'Audio analysis duration in seconds',
            ['analysis_type']
        )
        
        self.memory_usage = Gauge(
            'listen_service_memory_usage_bytes',
            'Memory usage in bytes'
        )
        
        self.cpu_usage = Gauge(
            'listen_service_cpu_usage_percent',
            'CPU usage percentage'
        )
        
        self.cache_operations = Counter(
            'listen_service_cache_operations_total',
            'Total cache operations',
            ['operation', 'result']
        )
        
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_enabled = False

    def _start_monitoring(self) -> None:
        """启动系统监控"""
        if self._monitoring_task is None and not self._monitoring_enabled:
            try:
                self._monitoring_task = asyncio.create_task(self._monitor_system())
                self._monitoring_enabled = True
            except RuntimeError:
                # 如果没有运行的事件循环，稍后再启动
                self._monitoring_enabled = False

    async def _monitor_system(self) -> None:
        """监控系统指标"""
        while True:
            try:
                # 收集系统指标
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_available=memory.available,
                    disk_usage=disk.percent,
                    network_io={
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    },
                    timestamp=time.time()
                )
                
                self.system_metrics.append(metrics)
                
                # 更新Prometheus指标
                self.memory_usage.set(memory.used)
                self.cpu_usage.set(cpu_percent)
                
                await asyncio.sleep(30)  # 每30秒收集一次
                
            except Exception as e:
                logger.error("系统监控失败", error=str(e))
                await asyncio.sleep(60)

    def record_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """记录请求指标"""
        self.request_count.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_audio_analysis(self, analysis_type: str, duration: float) -> None:
        """记录音频分析指标"""
        self.audio_analysis_duration.labels(analysis_type=analysis_type).observe(duration)

    def record_cache_operation(self, operation: str, result: str) -> None:
        """记录缓存操作指标"""
        self.cache_operations.labels(operation=operation, result=result).inc()

    def add_metrics(self, metrics: PerformanceMetrics) -> None:
        """添加性能指标"""
        self.metrics_history.append(metrics)
        self.function_stats[metrics.function_name].append(metrics.execution_time)
        
        # 限制每个函数的历史记录
        if len(self.function_stats[metrics.function_name]) > 100:
            self.function_stats[metrics.function_name] = \
                self.function_stats[metrics.function_name][-100:]

    def get_function_stats(self, function_name: str) -> Dict[str, float]:
        """获取函数统计信息"""
        times = self.function_stats.get(function_name, [])
        if not times:
            return {}
        
        return {
            "count": len(times),
            "avg_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "total_time": sum(times)
        }

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        if not self.system_metrics:
            return {}
        
        latest = self.system_metrics[-1]
        return {
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "memory_available_mb": latest.memory_available / (1024 * 1024),
            "disk_usage_percent": latest.disk_usage,
            "network_io": latest.network_io,
            "timestamp": latest.timestamp
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        total_functions = len(self.function_stats)
        total_calls = sum(len(times) for times in self.function_stats.values())
        
        if self.metrics_history:
            avg_execution_time = sum(m.execution_time for m in self.metrics_history) / len(self.metrics_history)
            avg_memory_usage = sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history)
        else:
            avg_execution_time = 0
            avg_memory_usage = 0
        
        return {
            "total_functions_monitored": total_functions,
            "total_function_calls": total_calls,
            "avg_execution_time": avg_execution_time,
            "avg_memory_usage_mb": avg_memory_usage / (1024 * 1024),
            "metrics_history_size": len(self.metrics_history),
            "system_metrics": self.get_system_stats()
        }

    async def start_monitoring_if_needed(self) -> None:
        """如果需要的话启动监控"""
        if not self._monitoring_enabled and self._monitoring_task is None:
            self._start_monitoring()

    async def cleanup(self) -> None:
        """清理监控任务"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None
            self._monitoring_enabled = False
        logger.info("性能监控器清理完成")


# 全局性能监控器实例
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def async_timer(func: F) -> F:
    """异步函数性能计时装饰器"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        start_cpu = psutil.cpu_percent()
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=psutil.cpu_percent() - start_cpu,
                timestamp=end_time,
                function_name=func.__name__,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            monitor = get_performance_monitor()
            monitor.add_metrics(metrics)
            
            logger.debug(
                "函数执行完成",
                function=func.__name__,
                execution_time=execution_time,
                memory_usage=memory_usage
            )
    
    return wrapper


def sync_timer(func: F) -> F:
    """同步函数性能计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        start_cpu = psutil.cpu_percent()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=psutil.cpu_percent() - start_cpu,
                timestamp=end_time,
                function_name=func.__name__,
                args_count=len(args),
                kwargs_count=len(kwargs)
            )
            
            monitor = get_performance_monitor()
            monitor.add_metrics(metrics)
            
            logger.debug(
                "函数执行完成",
                function=func.__name__,
                execution_time=execution_time,
                memory_usage=memory_usage
            )
    
    return wrapper


class PerformanceContext:
    """性能监控上下文管理器"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.start_memory: Optional[int] = None
        self.start_cpu: Optional[float] = None

    async def __aenter__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
        self.start_cpu = psutil.cpu_percent()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            execution_time = end_time - self.start_time
            memory_usage = end_memory - self.start_memory
            
            metrics = PerformanceMetrics(
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=psutil.cpu_percent() - self.start_cpu,
                timestamp=end_time,
                function_name=self.name,
                args_count=0,
                kwargs_count=0
            )
            
            monitor = get_performance_monitor()
            monitor.add_metrics(metrics)


def start_metrics_server(port: int = 9090) -> None:
    """启动Prometheus指标服务器"""
    try:
        start_http_server(port)
        logger.info("Prometheus指标服务器启动", port=port)
    except Exception as e:
        logger.error("启动指标服务器失败", port=port, error=str(e))


async def cleanup_performance_monitor() -> None:
    """清理性能监控器"""
    global _performance_monitor
    if _performance_monitor:
        await _performance_monitor.cleanup()
        _performance_monitor = None


# 性能分析工具
class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, monitor: Optional[PerformanceMonitor] = None):
        self.monitor = monitor or get_performance_monitor()

    def analyze_bottlenecks(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """分析性能瓶颈"""
        bottlenecks = []
        
        for func_name, times in self.monitor.function_stats.items():
            if not times:
                continue
                
            avg_time = sum(times) / len(times)
            max_time = max(times)
            
            if avg_time > threshold or max_time > threshold * 2:
                bottlenecks.append({
                    "function": func_name,
                    "avg_time": avg_time,
                    "max_time": max_time,
                    "call_count": len(times),
                    "severity": "high" if avg_time > threshold * 2 else "medium"
                })
        
        return sorted(bottlenecks, key=lambda x: x["avg_time"], reverse=True)

    def get_memory_trends(self) -> Dict[str, Any]:
        """获取内存使用趋势"""
        if not self.monitor.system_metrics:
            return {}
        
        memory_usage = [m.memory_percent for m in self.monitor.system_metrics]
        
        return {
            "current": memory_usage[-1] if memory_usage else 0,
            "average": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
            "peak": max(memory_usage) if memory_usage else 0,
            "trend": "increasing" if len(memory_usage) > 1 and memory_usage[-1] > memory_usage[0] else "stable"
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        return {
            "summary": self.monitor.get_performance_summary(),
            "bottlenecks": self.analyze_bottlenecks(),
            "memory_trends": self.get_memory_trends(),
            "system_health": self._assess_system_health(),
            "recommendations": self._generate_recommendations()
        }

    def _assess_system_health(self) -> str:
        """评估系统健康状况"""
        system_stats = self.monitor.get_system_stats()
        if not system_stats:
            return "unknown"
        
        cpu = system_stats.get("cpu_percent", 0)
        memory = system_stats.get("memory_percent", 0)
        
        if cpu > 80 or memory > 85:
            return "critical"
        elif cpu > 60 or memory > 70:
            return "warning"
        else:
            return "healthy"

    def _generate_recommendations(self) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        bottlenecks = self.analyze_bottlenecks(0.5)
        if bottlenecks:
            recommendations.append(f"发现{len(bottlenecks)}个性能瓶颈，建议优化慢函数")
        
        memory_trends = self.get_memory_trends()
        if memory_trends.get("current", 0) > 80:
            recommendations.append("内存使用率过高，建议检查内存泄漏")
        
        system_health = self._assess_system_health()
        if system_health == "critical":
            recommendations.append("系统资源紧张，建议增加硬件资源或优化代码")
        
        return recommendations