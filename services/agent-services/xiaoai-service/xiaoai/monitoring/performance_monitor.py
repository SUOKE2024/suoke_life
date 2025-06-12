"""
性能监控模块
"""

import asyncio
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import functools
import logging
import statistics
import time
from typing import Any, Callable, Dict, List, Optional

from ..utils.exceptions import MonitoringError


@dataclass
class PerformanceMetric:
    """性能指标"""

    name: str
    value: float
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None
    unit: Optional[str] = None


@dataclass
class RequestMetrics:
    """请求指标"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ServiceMetrics:
    """服务指标"""

    service_name: str
    operation: str
    duration: float
    success: bool
    timestamp: datetime
    error_message: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # 指标存储
        self.metrics: List[PerformanceMetric] = []
        self.request_metrics: List[RequestMetrics] = []
        self.service_metrics: List[ServiceMetrics] = []

        # 实时统计
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)

        # 配置
        self.max_metrics_size = 10000
        self.cleanup_interval = 3600  # 1小时
        self.percentiles = [50, 90, 95, 99]

        # 监控任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self.running = False

    async def initialize(self):
        """初始化性能监控器"""
        try:
            self.logger.info("初始化性能监控器...")

            # 启动清理任务
            await self.start_monitoring()

            self.logger.info("性能监控器初始化完成")

        except Exception as e:
            self.logger.error(f"性能监控器初始化失败: {e}")
            raise MonitoringError(f"性能监控器初始化失败: {e}")

    async def start_monitoring(self):
        """启动监控"""
        if self.running:
            return

        self.running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("性能监控已启动")

    async def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info("性能监控已停止")

    async def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                await self._cleanup_old_metrics()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"清理循环错误: {e}")
                await asyncio.sleep(self.cleanup_interval)

    async def _cleanup_old_metrics(self):
        """清理旧指标"""
        cutoff_time = datetime.now() - timedelta(hours=24)

        # 清理通用指标
        self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

        # 清理请求指标
        self.request_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        # 清理服务指标
        self.service_metrics = [m for m in self.service_metrics if m.timestamp > cutoff_time]

        # 限制指标数量
        if len(self.metrics) > self.max_metrics_size:
            self.metrics = self.metrics[-self.max_metrics_size :]

        if len(self.request_metrics) > self.max_metrics_size:
            self.request_metrics = self.request_metrics[-self.max_metrics_size :]

        if len(self.service_metrics) > self.max_metrics_size:
            self.service_metrics = self.service_metrics[-self.max_metrics_size :]

        self.logger.debug("完成指标清理")

    def record_metric(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None,
    ):
        """记录性能指标"""
        metric = PerformanceMetric(
            name=name, value=value, timestamp=datetime.now(), tags=tags or {}, unit=unit
        )
        self.metrics.append(metric)

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """记录请求指标"""
        request_metric = RequestMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            timestamp=datetime.now(),
            user_id=user_id,
            session_id=session_id,
        )
        self.request_metrics.append(request_metric)

        # 更新实时统计
        key = f"{method}:{endpoint}"
        self.response_times[key].append(response_time)
        self.request_counts[key] += 1

        if status_code >= 400:
            self.error_counts[key] += 1

    def record_service_call(
        self,
        service_name: str,
        operation: str,
        duration: float,
        success: bool,
        error_message: Optional[str] = None,
    ):
        """记录服务调用指标"""
        service_metric = ServiceMetrics(
            service_name=service_name,
            operation=operation,
            duration=duration,
            success=success,
            timestamp=datetime.now(),
            error_message=error_message,
        )
        self.service_metrics.append(service_metric)

        # 更新实时统计
        key = f"{service_name}:{operation}"
        self.response_times[key].append(duration)
        self.request_counts[key] += 1

        if not success:
            self.error_counts[key] += 1

    @asynccontextmanager
    async def measure_time(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """测量操作耗时的上下文管理器"""
        start_time = time.time()
        success = True
        error_message = None

        try:
            yield
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            duration = time.time() - start_time

            # 记录指标
            self.record_metric(
                name=f"{operation_name}_duration", value=duration, tags=tags, unit="seconds"
            )

            # 如果有服务名称标签，也记录为服务指标
            if tags and "service" in tags:
                self.record_service_call(
                    service_name=tags["service"],
                    operation=operation_name,
                    duration=duration,
                    success=success,
                    error_message=error_message,
                )

    def measure_function(
        self, operation_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None
    ):
        """装饰器：测量函数执行时间"""

        def decorator(func: Callable):
            name = operation_name or f"{func.__module__}.{func.__name__}"

            if asyncio.iscoroutinefunction(func):

                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    async with self.measure_time(name, tags):
                        return await func(*args, **kwargs)

                return async_wrapper
            else:

                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()

                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        str(e)
                        raise
                    finally:
                        duration = time.time() - start_time
                        self.record_metric(
                            name=f"{name}_duration", value=duration, tags=tags, unit="seconds"
                        )

                return sync_wrapper

        return decorator

    def get_response_time_stats(
        self, endpoint: Optional[str] = None, hours: int = 1
    ) -> Dict[str, Any]:
        """获取响应时间统计"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        if endpoint:
            # 特定端点的统计
            filtered_metrics = [
                m
                for m in self.request_metrics
                if m.endpoint == endpoint and m.timestamp > cutoff_time
            ]
        else:
            # 所有端点的统计
            filtered_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        if not filtered_metrics:
            return {}

        response_times = [m.response_time for m in filtered_metrics]

        stats = {
            "count": len(response_times),
            "min": min(response_times),
            "max": max(response_times),
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0,
        }

        # 计算百分位数
        for p in self.percentiles:
            try:
                stats[f"p{p}"] = statistics.quantiles(response_times, n=100)[p - 1]
            except (statistics.StatisticsError, IndexError):
                stats[f"p{p}"] = 0

        return stats

    def get_error_rate(self, endpoint: Optional[str] = None, hours: int = 1) -> float:
        """获取错误率"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        if endpoint:
            filtered_metrics = [
                m
                for m in self.request_metrics
                if m.endpoint == endpoint and m.timestamp > cutoff_time
            ]
        else:
            filtered_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        if not filtered_metrics:
            return 0.0

        error_count = len([m for m in filtered_metrics if m.status_code >= 400])
        total_count = len(filtered_metrics)

        return error_count / total_count if total_count > 0 else 0.0

    def get_throughput(self, endpoint: Optional[str] = None, hours: int = 1) -> float:
        """获取吞吐量（请求/秒）"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        if endpoint:
            filtered_metrics = [
                m
                for m in self.request_metrics
                if m.endpoint == endpoint and m.timestamp > cutoff_time
            ]
        else:
            filtered_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        if not filtered_metrics:
            return 0.0

        request_count = len(filtered_metrics)
        time_span = hours * 3600  # 转换为秒

        return request_count / time_span

    def get_service_stats(
        self, service_name: Optional[str] = None, hours: int = 1
    ) -> Dict[str, Any]:
        """获取服务统计"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        if service_name:
            filtered_metrics = [
                m
                for m in self.service_metrics
                if m.service_name == service_name and m.timestamp > cutoff_time
            ]
        else:
            filtered_metrics = [m for m in self.service_metrics if m.timestamp > cutoff_time]

        if not filtered_metrics:
            return {}

        durations = [m.duration for m in filtered_metrics]
        success_count = len([m for m in filtered_metrics if m.success])
        total_count = len(filtered_metrics)

        stats = {
            "total_calls": total_count,
            "success_calls": success_count,
            "error_calls": total_count - success_count,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
        }

        # 按操作分组的统计
        operations = defaultdict(list)
        for metric in filtered_metrics:
            operations[metric.operation].append(metric)

        operation_stats = {}
        for operation, metrics in operations.items():
            op_durations = [m.duration for m in metrics]
            op_success = len([m for m in metrics if m.success])

            operation_stats[operation] = {
                "calls": len(metrics),
                "success_rate": op_success / len(metrics),
                "avg_duration": statistics.mean(op_durations),
            }

        stats["operations"] = operation_stats

        return stats

    def get_top_slow_requests(self, limit: int = 10, hours: int = 1) -> List[Dict[str, Any]]:
        """获取最慢的请求"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        # 按响应时间排序
        sorted_metrics = sorted(filtered_metrics, key=lambda x: x.response_time, reverse=True)

        return [
            {
                "endpoint": m.endpoint,
                "method": m.method,
                "response_time": m.response_time,
                "status_code": m.status_code,
                "timestamp": m.timestamp.isoformat(),
                "user_id": m.user_id,
                "session_id": m.session_id,
            }
            for m in sorted_metrics[:limit]
        ]

    def get_endpoint_summary(self, hours: int = 1) -> Dict[str, Any]:
        """获取端点摘要"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_metrics = [m for m in self.request_metrics if m.timestamp > cutoff_time]

        # 按端点分组
        endpoints = defaultdict(list)
        for metric in filtered_metrics:
            key = f"{metric.method}:{metric.endpoint}"
            endpoints[key].append(metric)

        summary = {}
        for endpoint, metrics in endpoints.items():
            response_times = [m.response_time for m in metrics]
            error_count = len([m for m in metrics if m.status_code >= 400])

            summary[endpoint] = {
                "total_requests": len(metrics),
                "error_count": error_count,
                "error_rate": error_count / len(metrics),
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
            }

        return summary

    def get_performance_report(self, hours: int = 1) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "response_time_stats": self.get_response_time_stats(hours=hours),
            "error_rate": self.get_error_rate(hours=hours),
            "throughput": self.get_throughput(hours=hours),
            "service_stats": self.get_service_stats(hours=hours),
            "top_slow_requests": self.get_top_slow_requests(hours=hours),
            "endpoint_summary": self.get_endpoint_summary(hours=hours),
            "total_metrics": {
                "general_metrics": len(self.metrics),
                "request_metrics": len(self.request_metrics),
                "service_metrics": len(self.service_metrics),
            },
        }

    async def cleanup(self):
        """清理资源"""
        await self.stop_monitoring()
        self.metrics.clear()
        self.request_metrics.clear()
        self.service_metrics.clear()
        self.response_times.clear()
        self.error_counts.clear()
        self.request_counts.clear()
        self.logger.info("性能监控器已清理")


# 全局性能监控器实例
_performance_monitor: Optional[PerformanceMonitor] = None


async def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
        await _performance_monitor.initialize()
    return _performance_monitor


async def cleanup_performance_monitor():
    """清理性能监控器"""
    global _performance_monitor
    if _performance_monitor:
        await _performance_monitor.cleanup()
        _performance_monitor = None
