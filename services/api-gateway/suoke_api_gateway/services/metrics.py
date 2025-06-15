#!/usr/bin/env python3
"""
索克生活 API 网关指标服务

提供性能监控和业务指标收集功能。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional, Tuple
import asyncio
import time
from datetime import datetime, timedelta
import threading

logger = get_logger(__name__)


class MetricsCollector:
    """指标收集器"""

    def __init__(self, max_size: int = 10000):
        """初始化指标收集器"""
        self.max_size = max_size
        self.lock = threading.RLock()
        
        # 请求指标
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(deque)
        self.request_errors = defaultdict(int)
        
        # 服务指标
        self.service_requests = defaultdict(int)
        self.service_errors = defaultdict(int)
        self.service_response_times = defaultdict(deque)
        
        # 系统指标
        self.system_metrics = deque(maxlen=max_size)
        
        # 业务指标
        self.business_metrics = defaultdict(int)

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        """记录请求指标"""
        with self.lock:
            key = f"{method}:{path}"
            
            # 记录请求数量
            self.request_count[key] += 1
            self.request_count["total"] += 1
            
            # 记录响应时间
            if len(self.request_duration[key]) >= self.max_size:
                self.request_duration[key].popleft()
            self.request_duration[key].append((time.time(), duration))
            
            # 记录错误
            if status_code >= 400:
                self.request_errors[key] += 1
                self.request_errors["total"] += 1

    def record_service_request(self, service: str, instance: str, duration: float, success: bool = True) -> None:
        """记录服务请求指标"""
        with self.lock:
            key = f"{service}:{instance}"
            
            # 记录请求数量
            self.service_requests[key] += 1
            self.service_requests[service] += 1
            
            # 记录响应时间
            if len(self.service_response_times[key]) >= self.max_size:
                self.service_response_times[key].popleft()
            self.service_response_times[key].append((time.time(), duration))
            
            # 记录错误
            if not success:
                self.service_errors[key] += 1
                self.service_errors[service] += 1

    def record_system_metrics(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> None:
        """记录系统指标"""
        with self.lock:
            if len(self.system_metrics) >= self.max_size:
                self.system_metrics.popleft()
            
            self.system_metrics.append({
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            })

    def increment_business_metric(self, metric_name: str, value: int = 1) -> None:
        """增加业务指标"""
        with self.lock:
            self.business_metrics[metric_name] += value

    def get_request_stats(self, time_window: int = 300) -> Dict[str, Any]:
        """获取请求统计"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window
            
            stats = {}
            
            for key, durations in self.request_duration.items():
                # 过滤时间窗口内的数据
                recent_durations = [
                    duration for timestamp, duration in durations
                    if timestamp >= cutoff_time
                ]
                
                if recent_durations:
                    stats[key] = {
                        "count": len(recent_durations),
                        "avg_duration": sum(recent_durations) / len(recent_durations),
                        "min_duration": min(recent_durations),
                        "max_duration": max(recent_durations),
                        "error_count": self.request_errors.get(key, 0)
                    }
            
            return stats

    def get_service_stats(self, time_window: int = 300) -> Dict[str, Any]:
        """获取服务统计"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window
            
            stats = {}
            
            for key, durations in self.service_response_times.items():
                # 过滤时间窗口内的数据
                recent_durations = [
                    duration for timestamp, duration in durations
                    if timestamp >= cutoff_time
                ]
                
                if recent_durations:
                    stats[key] = {
                        "count": len(recent_durations),
                        "avg_response_time": sum(recent_durations) / len(recent_durations),
                        "min_response_time": min(recent_durations),
                        "max_response_time": max(recent_durations),
                        "error_count": self.service_errors.get(key, 0)
                    }
            
            return stats

    def get_system_stats(self, time_window: int = 300) -> Dict[str, Any]:
        """获取系统统计"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - time_window
            
            # 过滤时间窗口内的数据
            recent_metrics = [
                metric for metric in self.system_metrics
                if metric["timestamp"] >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            cpu_values = [m["cpu_percent"] for m in recent_metrics]
            memory_values = [m["memory_percent"] for m in recent_metrics]
            disk_values = [m["disk_percent"] for m in recent_metrics]
            
            return {
                "cpu": {
                    "avg": sum(cpu_values) / len(cpu_values),
                    "min": min(cpu_values),
                    "max": max(cpu_values)
                },
                "memory": {
                    "avg": sum(memory_values) / len(memory_values),
                    "min": min(memory_values),
                    "max": max(memory_values)
                },
                "disk": {
                    "avg": sum(disk_values) / len(disk_values),
                    "min": min(disk_values),
                    "max": max(disk_values)
                },
                "sample_count": len(recent_metrics)
            }


class MetricsService:
    """指标服务"""

    def __init__(self, settings=None):
        """初始化指标服务"""
        self.settings = settings or get_settings()
        self.collector = MetricsCollector()
        self._initialized = False
        self._collection_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """初始化服务"""
        if self._initialized:
            return

        logger.info("Initializing metrics service")
        
        # 启动系统指标收集任务
        self._collection_task = asyncio.create_task(self._collect_system_metrics())
        
        self._initialized = True
        logger.info("Metrics service initialized")

    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("Cleaning up metrics service")
        
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
        
        self._initialized = False

    def record_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        """记录请求指标"""
        self.collector.record_request(method, path, status_code, duration)

    def record_service_request(self, service: str, instance: str, duration: float, success: bool = True) -> None:
        """记录服务请求指标"""
        self.collector.record_service_request(service, instance, duration, success)

    def increment_business_metric(self, metric_name: str, value: int = 1) -> None:
        """增加业务指标"""
        self.collector.increment_business_metric(metric_name, value)

    async def get_business_metrics(self, time_window: int = 300) -> Dict[str, Any]:
        """获取业务指标"""
        try:
            request_stats = self.collector.get_request_stats(time_window)
            service_stats = self.collector.get_service_stats(time_window)
            
            # 计算总体统计
            total_requests = sum(stats["count"] for stats in request_stats.values())
            total_errors = sum(stats["error_count"] for stats in request_stats.values())
            
            avg_response_time = 0
            if request_stats:
                response_times = [stats["avg_duration"] for stats in request_stats.values()]
                avg_response_time = sum(response_times) / len(response_times)

            return {
                "requests": {
                    "total": total_requests,
                    "error_rate": (total_errors / total_requests * 100) if total_requests > 0 else 0,
                    "avg_response_time": avg_response_time,
                    "details": request_stats
                },
                "services": {
                    "details": service_stats
                },
                "business": dict(self.collector.business_metrics),
                "time_window": time_window,
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error("Failed to get business metrics", error=str(e), exc_info=True)
            return {
                "error": str(e),
                "timestamp": time.time()
            }

    async def get_runtime_stats(self) -> Dict[str, Any]:
        """获取运行时统计"""
        try:
            system_stats = self.collector.get_system_stats()
            
            return {
                "system": system_stats,
                "collector": {
                    "request_count": dict(self.collector.request_count),
                    "service_requests": dict(self.collector.service_requests),
                    "business_metrics": dict(self.collector.business_metrics)
                },
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error("Failed to get runtime stats", error=str(e), exc_info=True)
            return {
                "error": str(e),
                "timestamp": time.time()
            }

    async def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        import psutil
        
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage("/").percent
                
                self.collector.record_system_metrics(cpu_percent, memory_percent, disk_percent)
                
                # 每30秒收集一次
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Failed to collect system metrics", error=str(e))
                await asyncio.sleep(30)


# 全局指标服务实例
_metrics_service: Optional[MetricsService] = None


async def get_metrics_service() -> MetricsService:
    """获取指标服务实例"""
    global _metrics_service
    
    if _metrics_service is None:
        _metrics_service = MetricsService()
        await _metrics_service.initialize()
    
    return _metrics_service


async def cleanup_metrics_service() -> None:
    """清理指标服务"""
    global _metrics_service
    
    if _metrics_service is not None:
        await _metrics_service.cleanup()
        _metrics_service = None