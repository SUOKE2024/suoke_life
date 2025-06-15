#!/usr/bin/env python

"""
健康监控系统
提供服务健康检查、性能指标收集、资源监控和告警功能
"""

import asyncio
import gc
import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """指标类型枚举"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class HealthCheck:
    """健康检查定义"""

    name: str
    check_func: Callable
    interval: int = 30  # 检查间隔（秒）
    timeout: int = 10  # 超时时间（秒）
    critical: bool = False  # 是否为关键检查
    enabled: bool = True


@dataclass
class HealthCheckResult:
    """健康检查结果"""

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0
    timestamp: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """指标定义"""

    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: dict[str, str] = field(default_factory=dict)
    description: str = ""


class MetricsCollector:
    """指标收集器"""

    def __init__(self, max_history: int = 1000):
        self._metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def increment_counter(
        self, name: str, value: float = 1, labels: dict[str, str] = None
    ):
        """增加计数器"""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
            self._add_metric(name, MetricType.COUNTER, self._counters[key], labels)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] = None):
        """设置仪表盘值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
            self._add_metric(name, MetricType.GAUGE, value, labels)

    def record_histogram(self, name: str, value: float, labels: dict[str, str] = None):
        """记录直方图值"""
        with self._lock:
            self._add_metric(name, MetricType.HISTOGRAM, value, labels)

    def record_timer(
        self, name: str, duration_ms: float, labels: dict[str, str] = None
    ):
        """记录计时器值"""
        with self._lock:
            self._add_metric(name, MetricType.TIMER, duration_ms, labels)

    def _make_key(self, name: str, labels: dict[str, str] = None) -> str:
        """生成指标键"""
        if not labels:
            return name

        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def _add_metric(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        labels: dict[str, str] = None,
    ):
        """添加指标"""
        metric = Metric(
            name=name,
            type=metric_type,
            value=value,
            labels=labels or {},
            timestamp=time.time(),
        )
        self._metrics[name].append(metric)

    def get_metrics(self, name: str = None) -> list[Metric]:
        """获取指标"""
        with self._lock:
            if name:
                return list(self._metrics.get(name, []))

            all_metrics = []
            for metrics in self._metrics.values():
                all_metrics.extend(metrics)
            return all_metrics

    def get_latest_metrics(self) -> dict[str, Metric]:
        """获取最新指标"""
        with self._lock:
            latest = {}
            for name, metrics in self._metrics.items():
                if metrics:
                    latest[name] = metrics[-1]
            return latest


class ResourceMonitor:
    """资源监控器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None

    async def start_monitoring(self, interval: int = 30):
        """开始资源监控"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval))
        logger.info("资源监控已启动")

    async def stop_monitoring(self) -> None:
        """停止资源监控"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("资源监控已停止")

    async def _monitor_loop(self, interval: int):
        """监控循环"""
        while self._monitoring:
            try:
                await self._collect_system_metrics()
                await self._collect_process_metrics()
                await self._collect_python_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"资源监控异常: {e!s}")
                await asyncio.sleep(interval)

    async def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("system_cpu_usage_percent", cpu_percent)

            # 内存使用情况
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_usage_percent", memory.percent)
            self.metrics.set_gauge("system_memory_available_bytes", memory.available)
            self.metrics.set_gauge("system_memory_total_bytes", memory.total)

            # 磁盘使用情况
            disk = psutil.disk_usage("/")
            self.metrics.set_gauge("system_disk_usage_percent", disk.percent)
            self.metrics.set_gauge("system_disk_free_bytes", disk.free)
            self.metrics.set_gauge("system_disk_total_bytes", disk.total)

            # 网络IO
            net_io = psutil.net_io_counters()
            self.metrics.set_gauge("system_network_bytes_sent", net_io.bytes_sent)
            self.metrics.set_gauge("system_network_bytes_recv", net_io.bytes_recv)

        except Exception as e:
            logger.error(f"收集系统指标失败: {e!s}")

    async def _collect_process_metrics(self) -> None:
        """收集进程指标"""
        try:
            process = psutil.Process()

            # 进程CPU使用率
            cpu_percent = process.cpu_percent()
            self.metrics.set_gauge("process_cpu_usage_percent", cpu_percent)

            # 进程内存使用情况
            memory_info = process.memory_info()
            self.metrics.set_gauge("process_memory_rss_bytes", memory_info.rss)
            self.metrics.set_gauge("process_memory_vms_bytes", memory_info.vms)

            # 进程文件描述符
            num_fds = process.num_fds()
            self.metrics.set_gauge("process_open_fds", num_fds)

            # 进程线程数
            num_threads = process.num_threads()
            self.metrics.set_gauge("process_threads", num_threads)

        except Exception as e:
            logger.error(f"收集进程指标失败: {e!s}")

    async def _collect_python_metrics(self) -> None:
        """收集Python指标"""
        try:
            # 垃圾回收统计
            gc_stats = gc.get_stats()
            for i, stats in enumerate(gc_stats):
                self.metrics.set_gauge(
                    f"python_gc_generation_{i}_collections", stats["collections"]
                )
                self.metrics.set_gauge(
                    f"python_gc_generation_{i}_collected", stats["collected"]
                )
                self.metrics.set_gauge(
                    f"python_gc_generation_{i}_uncollectable", stats["uncollectable"]
                )

            # 对象计数
            gc_count = gc.get_count()
            for i, count in enumerate(gc_count):
                self.metrics.set_gauge(f"python_gc_objects_generation_{i}", count)

        except Exception as e:
            logger.error(f"收集Python指标失败: {e!s}")


class AlertManager:
    """告警管理器"""

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self._alert_rules: list[dict[str, Any]] = []
        self._alert_handlers: list[Callable] = []
        self._checking = False
        self._check_task: asyncio.Task | None = None

    def add_alert_rule(
        self,
        name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        duration: int = 60,
        severity: str = "warning",
    ):
        """添加告警规则"""
        rule = {
            "name": name,
            "metric_name": metric_name,
            "condition": condition,  # 'gt', 'lt', 'eq', 'gte', 'lte'
            "threshold": threshold,
            "duration": duration,
            "severity": severity,
            "triggered_at": None,
            "active": False,
        }
        self._alert_rules.append(rule)
        logger.info(f"添加告警规则: {name}")

    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self._alert_handlers.append(handler)

    async def start_checking(self, interval: int = 30):
        """开始告警检查"""
        if self._checking:
            return

        self._checking = True
        self._check_task = asyncio.create_task(self._check_loop(interval))
        logger.info("告警检查已启动")

    async def stop_checking(self) -> None:
        """停止告警检查"""
        self._checking = False
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
        logger.info("告警检查已停止")

    async def _check_loop(self, interval: int):
        """检查循环"""
        while self._checking:
            try:
                await self._check_alerts()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"告警检查异常: {e!s}")
                await asyncio.sleep(interval)

    async def _check_alerts(self) -> None:
        """检查告警"""
        current_time = time.time()
        latest_metrics = self.metrics.get_latest_metrics()

        for rule in self._alert_rules:
            metric_name = rule["metric_name"]
            if metric_name not in latest_metrics:
                continue

            metric = latest_metrics[metric_name]
            condition_met = self._evaluate_condition(
                metric.value, rule["condition"], rule["threshold"]
            )

            if condition_met:
                if not rule["active"]:
                    rule["triggered_at"] = current_time
                    rule["active"] = True
                elif current_time - rule["triggered_at"] >= rule["duration"]:
                    # 触发告警
                    await self._trigger_alert(rule, metric)
            else:
                if rule["active"]:
                    rule["active"] = False
                    rule["triggered_at"] = None
                    # 恢复告警
                    await self._resolve_alert(rule, metric)

    def _evaluate_condition(
        self, value: float, condition: str, threshold: float
    ) -> bool:
        """评估条件"""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "eq":
            return value == threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lte":
            return value <= threshold
        else:
            return False

    async def _trigger_alert(self, rule: dict[str, Any], metric: Metric):
        """触发告警"""
        alert = {
            "type": "alert",
            "rule_name": rule["name"],
            "metric_name": rule["metric_name"],
            "metric_value": metric.value,
            "threshold": rule["threshold"],
            "severity": rule["severity"],
            "timestamp": time.time(),
            "message": f"告警: {rule['name']} - {rule['metric_name']}={metric.value} {rule['condition']} {rule['threshold']}",
        }

        logger.warning(f"触发告警: {alert['message']}")

        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"告警处理器异常: {e!s}")

    async def _resolve_alert(self, rule: dict[str, Any], metric: Metric):
        """恢复告警"""
        alert = {
            "type": "resolve",
            "rule_name": rule["name"],
            "metric_name": rule["metric_name"],
            "metric_value": metric.value,
            "threshold": rule["threshold"],
            "severity": rule["severity"],
            "timestamp": time.time(),
            "message": f"恢复: {rule['name']} - {rule['metric_name']}={metric.value}",
        }

        logger.info(f"告警恢复: {alert['message']}")

        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"告警处理器异常: {e!s}")


class HealthMonitor:
    """健康监控器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._health_checks: dict[str, HealthCheck] = {}
        self._check_results: dict[str, HealthCheckResult] = {}
        self._metrics = MetricsCollector()
        self._resource_monitor = ResourceMonitor(self._metrics)
        self._alert_manager = AlertManager(self._metrics)
        self._monitoring = False
        self._check_tasks: dict[str, asyncio.Task] = {}

        # 初始化默认健康检查
        self._setup_default_checks()

        # 初始化默认告警规则
        self._setup_default_alerts()

    def _setup_default_checks(self) -> None:
        """设置默认健康检查"""
        # 内存使用检查
        self.add_health_check(
            "memory_usage", self._check_memory_usage, interval=30, critical=True
        )

        # CPU使用检查
        self.add_health_check(
            "cpu_usage", self._check_cpu_usage, interval=30, critical=False
        )

        # 磁盘空间检查
        self.add_health_check(
            "disk_space", self._check_disk_space, interval=60, critical=True
        )

    def _setup_default_alerts(self) -> None:
        """设置默认告警规则"""
        # 内存使用告警
        self._alert_manager.add_alert_rule(
            "high_memory_usage",
            "system_memory_usage_percent",
            "gt",
            85.0,
            duration=120,
            severity="warning",
        )

        # CPU使用告警
        self._alert_manager.add_alert_rule(
            "high_cpu_usage",
            "system_cpu_usage_percent",
            "gt",
            80.0,
            duration=300,
            severity="warning",
        )

        # 磁盘空间告警
        self._alert_manager.add_alert_rule(
            "low_disk_space",
            "system_disk_usage_percent",
            "gt",
            90.0,
            duration=60,
            severity="critical",
        )

    def add_health_check(
        self,
        name: str,
        check_func: Callable,
        interval: int = 30,
        timeout: int = 10,
        critical: bool = False,
        enabled: bool = True,
    ):
        """添加健康检查"""
        health_check = HealthCheck(
            name=name,
            check_func=check_func,
            interval=interval,
            timeout=timeout,
            critical=critical,
            enabled=enabled,
        )
        self._health_checks[name] = health_check
        logger.info(f"添加健康检查: {name}")

    def remove_health_check(self, name: str):
        """移除健康检查"""
        if name in self._health_checks:
            del self._health_checks[name]
            if name in self._check_tasks:
                self._check_tasks[name].cancel()
                del self._check_tasks[name]
            logger.info(f"移除健康检查: {name}")

    async def start_monitoring(self) -> None:
        """开始监控"""
        if self._monitoring:
            return

        self._monitoring = True

        # 启动健康检查任务
        for name, health_check in self._health_checks.items():
            if health_check.enabled:
                self._check_tasks[name] = asyncio.create_task(
                    self._run_health_check(health_check)
                )

        # 启动资源监控
        await self._resource_monitor.start_monitoring()

        # 启动告警检查
        await self._alert_manager.start_checking()

        logger.info("健康监控已启动")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        self._monitoring = False

        # 停止健康检查任务
        for task in self._check_tasks.values():
            task.cancel()

        await asyncio.gather(*self._check_tasks.values(), return_exceptions=True)
        self._check_tasks.clear()

        # 停止资源监控
        await self._resource_monitor.stop_monitoring()

        # 停止告警检查
        await self._alert_manager.stop_checking()

        logger.info("健康监控已停止")

    async def _run_health_check(self, health_check: HealthCheck):
        """运行健康检查"""
        while self._monitoring:
            try:
                start_time = time.time()

                # 执行健康检查
                try:
                    result = await asyncio.wait_for(
                        self._execute_check(health_check), timeout=health_check.timeout
                    )
                except TimeoutError:
                    result = HealthCheckResult(
                        name=health_check.name,
                        status=HealthStatus.UNHEALTHY,
                        message="检查超时",
                        duration_ms=(time.time() - start_time) * 1000,
                    )
                except Exception as e:
                    result = HealthCheckResult(
                        name=health_check.name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"检查异常: {e!s}",
                        duration_ms=(time.time() - start_time) * 1000,
                    )

                # 保存结果
                self._check_results[health_check.name] = result

                # 记录指标
                self._metrics.record_timer(
                    "health_check_duration_ms",
                    result.duration_ms,
                    {"check_name": health_check.name},
                )

                self._metrics.set_gauge(
                    "health_check_status",
                    1 if result.status == HealthStatus.HEALTHY else 0,
                    {"check_name": health_check.name},
                )

                await asyncio.sleep(health_check.interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查任务异常: {health_check.name}, 错误: {e!s}")
                await asyncio.sleep(health_check.interval)

    async def _execute_check(self, health_check: HealthCheck) -> HealthCheckResult:
        """执行健康检查"""
        start_time = time.time()

        if asyncio.iscoroutinefunction(health_check.check_func):
            result = await health_check.check_func()
        else:
            result = health_check.check_func()

        duration_ms = (time.time() - start_time) * 1000

        if isinstance(result, HealthCheckResult):
            result.duration_ms = duration_ms
            return result
        elif isinstance(result, dict):
            return HealthCheckResult(
                name=health_check.name,
                status=HealthStatus(result.get("status", "unknown")),
                message=result.get("message", ""),
                duration_ms=duration_ms,
                details=result.get("details", {}),
            )
        else:
            return HealthCheckResult(
                name=health_check.name,
                status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                message="检查完成",
                duration_ms=duration_ms,
            )

    async def _check_memory_usage(self) -> dict[str, Any]:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"内存使用过高: {usage_percent:.1f}%"
            elif usage_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"内存使用较高: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"内存使用正常: {usage_percent:.1f}%"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "usage_percent": usage_percent,
                    "available_mb": memory.available // 1024 // 1024,
                    "total_mb": memory.total // 1024 // 1024,
                },
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"内存检查失败: {e!s}",
            }

    async def _check_cpu_usage(self) -> dict[str, Any]:
        """检查CPU使用"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU使用过高: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"CPU使用较高: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU使用正常: {cpu_percent:.1f}%"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "usage_percent": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                },
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"CPU检查失败: {e!s}",
            }

    async def _check_disk_space(self) -> dict[str, Any]:
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage("/")
            usage_percent = disk.percent

            if usage_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"磁盘空间不足: {usage_percent:.1f}%"
            elif usage_percent > 90:
                status = HealthStatus.DEGRADED
                message = f"磁盘空间较少: {usage_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"磁盘空间正常: {usage_percent:.1f}%"

            return {
                "status": status.value,
                "message": message,
                "details": {
                    "usage_percent": usage_percent,
                    "free_gb": disk.free // 1024 // 1024 // 1024,
                    "total_gb": disk.total // 1024 // 1024 // 1024,
                },
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": f"磁盘检查失败: {e!s}",
            }

    async def check_health(self) -> dict[str, Any]:
        """获取整体健康状态"""
        overall_status = HealthStatus.HEALTHY
        critical_issues = []
        warnings = []

        for name, result in self._check_results.items():
            health_check = self._health_checks.get(name)
            if not health_check:
                continue

            if result.status == HealthStatus.UNHEALTHY:
                if health_check.critical:
                    overall_status = HealthStatus.UNHEALTHY
                    critical_issues.append(result.message)
                else:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED
                    warnings.append(result.message)
            elif result.status == HealthStatus.DEGRADED:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                warnings.append(result.message)

        return {
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "duration_ms": result.duration_ms,
                    "timestamp": result.timestamp,
                    "details": result.details,
                }
                for name, result in self._check_results.items()
            },
            "critical_issues": critical_issues,
            "warnings": warnings,
            "uptime_seconds": (
                time.time() - self._start_time if hasattr(self, "_start_time") else 0
            ),
        }

    async def get_metrics(self) -> dict[str, Any]:
        """获取指标"""
        latest_metrics = self._metrics.get_latest_metrics()

        metrics_data = {}
        for name, metric in latest_metrics.items():
            metrics_data[name] = {
                "value": metric.value,
                "type": metric.type.value,
                "timestamp": metric.timestamp,
                "labels": metric.labels,
            }

        return {"metrics": metrics_data, "timestamp": time.time()}

    def get_metrics_collector(self) -> MetricsCollector:
        """获取指标收集器"""
        return self._metrics

    def get_alert_manager(self) -> AlertManager:
        """获取告警管理器"""
        return self._alert_manager

    async def cleanup(self) -> None:
        """清理资源"""
        logger.info("开始清理健康监控器")
        await self.stop_monitoring()
        logger.info("健康监控器清理完成")
