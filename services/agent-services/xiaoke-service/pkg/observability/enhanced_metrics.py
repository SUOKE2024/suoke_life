#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的监控和指标收集器
提供详细的性能监控、业务指标和健康检查功能
"""

import time
import asyncio
import logging
import psutil
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
)

logger = logging.getLogger(__name__)


@dataclass
class MetricConfig:
    """指标配置"""

    enable_prometheus: bool = True
    enable_custom_metrics: bool = True
    metric_retention_hours: int = 24
    health_check_interval: int = 60
    performance_sampling_rate: float = 1.0


class EnhancedMetricsCollector:
    """增强的指标收集器"""

    def __init__(self, config: MetricConfig = None):
        """
        初始化指标收集器

        Args:
            config: 指标配置
        """
        self.config = config or MetricConfig()

        # Prometheus注册表
        self.registry = CollectorRegistry()

        # 初始化Prometheus指标
        self._init_prometheus_metrics()

        # 自定义指标存储
        self.custom_metrics = defaultdict(list)
        self.time_series_metrics = defaultdict(lambda: deque(maxlen=1000))

        # 性能监控
        self.performance_data = {
            "request_times": deque(maxlen=1000),
            "error_rates": deque(maxlen=100),
            "throughput": deque(maxlen=100),
        }

        # 业务指标
        self.business_metrics = {
            "diet_plans_generated": 0,
            "food_recommendations": 0,
            "resource_allocations": 0,
            "user_sessions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # 健康检查状态
        self.health_status = {
            "overall": "healthy",
            "database": "unknown",
            "cache": "unknown",
            "external_apis": "unknown",
            "last_check": None,
        }

        # 启动监控任务
        self._monitoring_task = None
        if self.config.enable_custom_metrics:
            self._start_monitoring()

        logger.info("增强指标收集器初始化完成")

    def _init_prometheus_metrics(self):
        """初始化Prometheus指标"""
        if not self.config.enable_prometheus:
            return

        # 请求计数器
        self.request_counter = Counter(
            "xiaoke_requests_total",
            "Total number of requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        # 请求延迟直方图
        self.request_duration = Histogram(
            "xiaoke_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # 活跃连接数
        self.active_connections = Gauge(
            "xiaoke_active_connections",
            "Number of active connections",
            ["type"],
            registry=self.registry,
        )

        # 缓存指标
        self.cache_operations = Counter(
            "xiaoke_cache_operations_total",
            "Total cache operations",
            ["operation", "result"],
            registry=self.registry,
        )

        # 业务指标
        self.diet_plans_counter = Counter(
            "xiaoke_diet_plans_generated_total",
            "Total diet plans generated",
            registry=self.registry,
        )

        self.food_recommendations_counter = Counter(
            "xiaoke_food_recommendations_total",
            "Total food recommendations",
            registry=self.registry,
        )

        self.resource_allocations_counter = Counter(
            "xiaoke_resource_allocations_total",
            "Total resource allocations",
            registry=self.registry,
        )

        # 系统资源指标
        self.cpu_usage = Gauge(
            "xiaoke_cpu_usage_percent", "CPU usage percentage", registry=self.registry
        )

        self.memory_usage = Gauge(
            "xiaoke_memory_usage_bytes", "Memory usage in bytes", registry=self.registry
        )

        self.disk_usage = Gauge(
            "xiaoke_disk_usage_percent", "Disk usage percentage", registry=self.registry
        )

        # 错误率
        self.error_rate = Gauge(
            "xiaoke_error_rate", "Current error rate", registry=self.registry
        )

        # 服务信息
        self.service_info = Info(
            "xiaoke_service_info", "Service information", registry=self.registry
        )

        logger.debug("Prometheus指标初始化完成")

    def _start_monitoring(self):
        """启动监控任务"""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._collect_system_metrics()
                await self._perform_health_checks()
                self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("监控循环错误: %s", str(e))

    async def _collect_system_metrics(self):
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            if self.config.enable_prometheus:
                self.cpu_usage.set(cpu_percent)

            # 内存使用
            memory = psutil.virtual_memory()
            if self.config.enable_prometheus:
                self.memory_usage.set(memory.used)

            # 磁盘使用
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            if self.config.enable_prometheus:
                self.disk_usage.set(disk_percent)

            # 存储到自定义指标
            timestamp = time.time()
            self.time_series_metrics["cpu_usage"].append((timestamp, cpu_percent))
            self.time_series_metrics["memory_usage"].append((timestamp, memory.used))
            self.time_series_metrics["disk_usage"].append((timestamp, disk_percent))

        except Exception as e:
            logger.error("收集系统指标失败: %s", str(e))

    async def _perform_health_checks(self):
        """执行健康检查"""
        try:
            # 更新健康检查时间
            self.health_status["last_check"] = datetime.now().isoformat()

            # 这里可以添加具体的健康检查逻辑
            # 例如检查数据库连接、缓存状态等

            # 简单的健康状态评估
            overall_status = "healthy"
            for component, status in self.health_status.items():
                if component != "overall" and component != "last_check":
                    if status == "unhealthy":
                        overall_status = "unhealthy"
                        break
                    elif status == "degraded":
                        overall_status = "degraded"

            self.health_status["overall"] = overall_status

        except Exception as e:
            logger.error("健康检查失败: %s", str(e))
            self.health_status["overall"] = "unhealthy"

    def _cleanup_old_metrics(self):
        """清理过期指标"""
        cutoff_time = time.time() - (self.config.metric_retention_hours * 3600)

        for metric_name, data in self.time_series_metrics.items():
            # 移除过期数据
            while data and data[0][0] < cutoff_time:
                data.popleft()

    @asynccontextmanager
    async def track_request(self, method: str, endpoint: str):
        """跟踪请求的上下文管理器"""
        start_time = time.time()
        status = "success"

        try:
            yield
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time

            # 记录Prometheus指标
            if self.config.enable_prometheus:
                self.request_counter.labels(
                    method=method, endpoint=endpoint, status=status
                ).inc()

                self.request_duration.labels(method=method, endpoint=endpoint).observe(
                    duration
                )

            # 记录性能数据
            self.performance_data["request_times"].append(duration)

            # 更新错误率
            self._update_error_rate(status == "error")

    def _update_error_rate(self, is_error: bool):
        """更新错误率"""
        self.performance_data["error_rates"].append(1 if is_error else 0)

        # 计算最近100个请求的错误率
        if len(self.performance_data["error_rates"]) > 0:
            error_rate = sum(self.performance_data["error_rates"]) / len(
                self.performance_data["error_rates"]
            )

            if self.config.enable_prometheus:
                self.error_rate.set(error_rate)

    def increment_business_metric(
        self, metric_name: str, value: int = 1, labels: Dict[str, str] = None
    ):
        """增加业务指标"""
        if metric_name in self.business_metrics:
            self.business_metrics[metric_name] += value

        # 更新Prometheus指标
        if self.config.enable_prometheus:
            if metric_name == "diet_plans_generated":
                self.diet_plans_counter.inc(value)
            elif metric_name == "food_recommendations":
                self.food_recommendations_counter.inc(value)
            elif metric_name == "resource_allocations":
                self.resource_allocations_counter.inc(value)

    def record_cache_operation(self, operation: str, result: str):
        """记录缓存操作"""
        if self.config.enable_prometheus:
            self.cache_operations.labels(operation=operation, result=result).inc()

        # 更新业务指标
        if result == "hit":
            self.business_metrics["cache_hits"] += 1
        elif result == "miss":
            self.business_metrics["cache_misses"] += 1

    def set_active_connections(self, connection_type: str, count: int):
        """设置活跃连接数"""
        if self.config.enable_prometheus:
            self.active_connections.labels(type=connection_type).set(count)

    def record_custom_metric(
        self, name: str, value: float, labels: Dict[str, str] = None
    ):
        """记录自定义指标"""
        timestamp = time.time()
        metric_data = {"timestamp": timestamp, "value": value, "labels": labels or {}}

        self.custom_metrics[name].append(metric_data)
        self.time_series_metrics[name].append((timestamp, value))

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        request_times = list(self.performance_data["request_times"])
        error_rates = list(self.performance_data["error_rates"])

        summary = {
            "request_count": len(request_times),
            "avg_response_time": sum(request_times) / len(request_times)
            if request_times
            else 0,
            "p95_response_time": self._calculate_percentile(request_times, 95),
            "p99_response_time": self._calculate_percentile(request_times, 99),
            "error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
            "throughput": len(request_times) / 60
            if request_times
            else 0,  # 每分钟请求数
        }

        return summary

    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        index = min(index, len(sorted_data) - 1)

        return sorted_data[index]

    def get_business_metrics(self) -> Dict[str, Any]:
        """获取业务指标"""
        return self.business_metrics.copy()

    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return self.health_status.copy()

    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_used_bytes": memory.used,
                "memory_total_bytes": memory.total,
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "disk_used_bytes": disk.used,
                "disk_total_bytes": disk.total,
            }
        except Exception as e:
            logger.error("获取系统指标失败: %s", str(e))
            return {}

    def get_prometheus_metrics(self) -> str:
        """获取Prometheus格式的指标"""
        if not self.config.enable_prometheus:
            return ""

        return generate_latest(self.registry).decode("utf-8")

    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            "performance": self.get_performance_summary(),
            "business": self.get_business_metrics(),
            "health": self.get_health_status(),
            "system": self.get_system_metrics(),
            "timestamp": datetime.now().isoformat(),
        }

    def update_health_component(self, component: str, status: str):
        """更新健康组件状态"""
        if component in self.health_status:
            self.health_status[component] = status

    async def close(self):
        """关闭监控"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("指标收集器已关闭")


# 全局指标收集器实例
_metrics_collector: Optional[EnhancedMetricsCollector] = None


def get_metrics_collector(
    config: Optional[MetricConfig] = None,
) -> EnhancedMetricsCollector:
    """获取指标收集器实例"""
    global _metrics_collector

    if _metrics_collector is None:
        _metrics_collector = EnhancedMetricsCollector(config)

    return _metrics_collector


async def close_metrics_collector():
    """关闭指标收集器"""
    global _metrics_collector

    if _metrics_collector:
        await _metrics_collector.close()
        _metrics_collector = None


# 装饰器函数
def track_performance(endpoint: str, method: str = "POST"):
    """性能跟踪装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()
            async with metrics.track_request(method, endpoint):
                return await func(*args, **kwargs)

        return wrapper

    return decorator
