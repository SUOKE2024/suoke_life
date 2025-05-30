"""
实时健康监测模块

该模块实现了完整的服务健康监测系统，包括：
- 实时健康检查
- 性能指标监控
- 智能告警管理
- 自动恢复机制
- 系统资源监控
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import time
from typing import Any

import psutil

from .base import BaseService
from .cache import CacheManager
from .exceptions import InquiryServiceError
from .metrics import MetricsCollector
from .utils import timer


class HealthStatus(Enum):
    """健康状态"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


class MetricType(Enum):
    """指标类型"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """告警严重程度"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class HealthCheck:
    """健康检查配置"""

    name: str
    check_function: Callable
    interval: int = 30  # 检查间隔（秒）
    timeout: int = 10  # 超时时间（秒）
    retries: int = 3  # 重试次数
    enabled: bool = True
    dependencies: list[str] = field(default_factory=list)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class HealthResult:
    """健康检查结果"""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    error: str | None = None


@dataclass
class MetricValue:
    """指标值"""

    name: str
    value: int | float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.now)
    tags: dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class Alert:
    """告警"""

    id: str
    name: str
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: datetime | None = None
    tags: dict[str, str] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ThresholdRule:
    """阈值规则"""

    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    threshold: float
    severity: AlertSeverity
    duration: int = 60  # 持续时间（秒）
    message_template: str = ""


class HealthMonitor(BaseService):
    """实时健康监测器"""

    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        config: dict[str, Any] | None = None,
    ):
        super().__init__()
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.config = config or {}

        # 配置参数
        self.check_interval = self.config.get("check_interval", 30)
        self.metric_retention = self.config.get("metric_retention", 3600)  # 1小时
        self.alert_cooldown = self.config.get("alert_cooldown", 300)  # 5分钟
        self.auto_recovery_enabled = self.config.get("auto_recovery_enabled", True)

        # 健康检查
        self.health_checks: dict[str, HealthCheck] = {}
        self.health_results: dict[str, HealthResult] = {}
        self.check_tasks: dict[str, asyncio.Task] = {}

        # 指标监控
        self.metrics: dict[str, list[MetricValue]] = {}
        self.threshold_rules: list[ThresholdRule] = []

        # 告警管理
        self.alerts: dict[str, Alert] = {}
        self.alert_handlers: list[Callable] = []
        self.alert_history: list[Alert] = []

        # 系统监控
        self.system_metrics_enabled = self.config.get("system_metrics_enabled", True)
        self.system_check_interval = self.config.get("system_check_interval", 60)

        # 统计信息
        self.stats = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "total_alerts": 0,
            "active_alerts": 0,
            "resolved_alerts": 0,
            "uptime": time.time(),
            "last_check_time": None,
        }

        self._initialize_default_checks()
        self._initialize_default_thresholds()

        # 启动监控任务
        self._monitoring_task = None
        self._system_monitoring_task = None

    def _initialize_default_checks(self) -> None:
        """初始化默认健康检查"""
        # 数据库连接检查
        self.add_health_check(
            HealthCheck(
                name="database_connection",
                check_function=self._check_database_connection,
                interval=60,
                timeout=5,
                tags={"component": "database"},
            )
        )

        # 缓存连接检查
        self.add_health_check(
            HealthCheck(
                name="cache_connection",
                check_function=self._check_cache_connection,
                interval=30,
                timeout=3,
                tags={"component": "cache"},
            )
        )

        # 内存使用检查
        self.add_health_check(
            HealthCheck(
                name="memory_usage",
                check_function=self._check_memory_usage,
                interval=30,
                timeout=2,
                tags={"component": "system"},
            )
        )

        # 磁盘空间检查
        self.add_health_check(
            HealthCheck(
                name="disk_space",
                check_function=self._check_disk_space,
                interval=300,  # 5分钟
                timeout=5,
                tags={"component": "system"},
            )
        )

        # API响应时间检查
        self.add_health_check(
            HealthCheck(
                name="api_response_time",
                check_function=self._check_api_response_time,
                interval=60,
                timeout=10,
                tags={"component": "api"},
            )
        )

    def _initialize_default_thresholds(self) -> None:
        """初始化默认阈值规则"""
        self.threshold_rules = [
            # 内存使用率阈值
            ThresholdRule(
                metric_name="memory_usage_percent",
                operator=">=",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                duration=120,
                message_template="内存使用率过高: {value}%",
            ),
            ThresholdRule(
                metric_name="memory_usage_percent",
                operator=">=",
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                duration=60,
                message_template="内存使用率严重过高: {value}%",
            ),
            # CPU使用率阈值
            ThresholdRule(
                metric_name="cpu_usage_percent",
                operator=">=",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                duration=180,
                message_template="CPU使用率过高: {value}%",
            ),
            ThresholdRule(
                metric_name="cpu_usage_percent",
                operator=">=",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                duration=60,
                message_template="CPU使用率严重过高: {value}%",
            ),
            # 磁盘使用率阈值
            ThresholdRule(
                metric_name="disk_usage_percent",
                operator=">=",
                threshold=85.0,
                severity=AlertSeverity.WARNING,
                duration=300,
                message_template="磁盘使用率过高: {value}%",
            ),
            ThresholdRule(
                metric_name="disk_usage_percent",
                operator=">=",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                duration=60,
                message_template="磁盘使用率严重过高: {value}%",
            ),
            # API响应时间阈值
            ThresholdRule(
                metric_name="api_response_time_ms",
                operator=">=",
                threshold=1000.0,
                severity=AlertSeverity.WARNING,
                duration=120,
                message_template="API响应时间过长: {value}ms",
            ),
            ThresholdRule(
                metric_name="api_response_time_ms",
                operator=">=",
                threshold=5000.0,
                severity=AlertSeverity.CRITICAL,
                duration=60,
                message_template="API响应时间严重过长: {value}ms",
            ),
        ]

    def add_health_check(self, health_check: HealthCheck) -> None:
        """添加健康检查"""
        self.health_checks[health_check.name] = health_check
        self.logger.info(f"Added health check: {health_check.name}")

    def remove_health_check(self, name: str) -> None:
        """移除健康检查"""
        if name in self.health_checks:
            del self.health_checks[name]
            if name in self.check_tasks:
                self.check_tasks[name].cancel()
                del self.check_tasks[name]
            self.logger.info(f"Removed health check: {name}")

    def add_threshold_rule(self, rule: ThresholdRule) -> None:
        """添加阈值规则"""
        self.threshold_rules.append(rule)
        self.logger.info(f"Added threshold rule for {rule.metric_name}")

    def add_alert_handler(self, handler: Callable[[Alert], None]) -> None:
        """添加告警处理器"""
        self.alert_handlers.append(handler)

    async def start_monitoring(self) -> None:
        """启动监控"""
        try:
            # 启动健康检查任务
            for name, check in self.health_checks.items():
                if check.enabled:
                    task = asyncio.create_task(self._run_health_check_loop(check))
                    self.check_tasks[name] = task

            # 启动主监控任务
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            # 启动系统监控任务
            if self.system_metrics_enabled:
                self._system_monitoring_task = asyncio.create_task(
                    self._system_monitoring_loop()
                )

            self.logger.info("Health monitoring started")

        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise InquiryServiceError(f"Failed to start monitoring: {e}")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        try:
            # 停止健康检查任务
            for task in self.check_tasks.values():
                task.cancel()
            self.check_tasks.clear()

            # 停止主监控任务
            if self._monitoring_task:
                self._monitoring_task.cancel()

            # 停止系统监控任务
            if self._system_monitoring_task:
                self._system_monitoring_task.cancel()

            self.logger.info("Health monitoring stopped")

        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")

    async def _run_health_check_loop(self, check: HealthCheck) -> None:
        """运行健康检查循环"""
        while True:
            try:
                await self._execute_health_check(check)
                await asyncio.sleep(check.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop {check.name}: {e}")
                await asyncio.sleep(check.interval)

    async def _execute_health_check(self, check: HealthCheck) -> HealthResult:
        """执行健康检查"""
        start_time = time.time()
        result = None

        for attempt in range(check.retries + 1):
            try:
                self.stats["total_checks"] += 1

                # 执行检查函数
                check_result = await asyncio.wait_for(
                    check.check_function(), timeout=check.timeout
                )

                # 创建结果对象
                if isinstance(check_result, HealthResult):
                    result = check_result
                elif isinstance(check_result, dict):
                    result = HealthResult(
                        name=check.name,
                        status=HealthStatus(check_result.get("status", "healthy")),
                        message=check_result.get("message", ""),
                        details=check_result.get("details", {}),
                    )
                else:
                    result = HealthResult(
                        name=check.name,
                        status=HealthStatus.HEALTHY,
                        message="Check passed",
                    )

                result.duration = time.time() - start_time
                self.stats["successful_checks"] += 1
                break

            except TimeoutError:
                error_msg = (
                    f"Health check {check.name} timed out after {check.timeout}s"
                )
                if attempt < check.retries:
                    self.logger.warning(
                        f"{error_msg}, retrying ({attempt + 1}/{check.retries})"
                    )
                    continue
                else:
                    result = HealthResult(
                        name=check.name,
                        status=HealthStatus.CRITICAL,
                        message="Check timed out",
                        error=error_msg,
                        duration=time.time() - start_time,
                    )
                    self.stats["failed_checks"] += 1

            except Exception as e:
                error_msg = f"Health check {check.name} failed: {e!s}"
                if attempt < check.retries:
                    self.logger.warning(
                        f"{error_msg}, retrying ({attempt + 1}/{check.retries})"
                    )
                    continue
                else:
                    result = HealthResult(
                        name=check.name,
                        status=HealthStatus.DOWN,
                        message="Check failed",
                        error=error_msg,
                        duration=time.time() - start_time,
                    )
                    self.stats["failed_checks"] += 1

        # 保存结果
        self.health_results[check.name] = result
        self.stats["last_check_time"] = datetime.now()

        # 检查是否需要触发告警
        await self._check_health_alerts(result)

        # 更新指标
        await self.metrics_collector.gauge(
            f"health_check_{check.name}_status",
            1 if result.status == HealthStatus.HEALTHY else 0,
            tags=check.tags,
        )
        await self.metrics_collector.histogram(
            f"health_check_{check.name}_duration", result.duration, tags=check.tags
        )

        return result

    async def _monitoring_loop(self) -> None:
        """主监控循环"""
        while True:
            try:
                # 检查阈值规则
                await self._check_threshold_rules()

                # 清理过期数据
                await self._cleanup_expired_data()

                # 更新统计信息
                await self._update_statistics()

                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _system_monitoring_loop(self) -> None:
        """系统监控循环"""
        while True:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.system_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(self.system_check_interval)

    async def _collect_system_metrics(self) -> None:
        """收集系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(
                MetricValue(
                    name="cpu_usage_percent",
                    value=cpu_percent,
                    metric_type=MetricType.GAUGE,
                    unit="%",
                )
            )

            # 内存使用率
            memory = psutil.virtual_memory()
            await self.record_metric(
                MetricValue(
                    name="memory_usage_percent",
                    value=memory.percent,
                    metric_type=MetricType.GAUGE,
                    unit="%",
                )
            )
            await self.record_metric(
                MetricValue(
                    name="memory_usage_bytes",
                    value=memory.used,
                    metric_type=MetricType.GAUGE,
                    unit="bytes",
                )
            )

            # 磁盘使用率
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            await self.record_metric(
                MetricValue(
                    name="disk_usage_percent",
                    value=disk_percent,
                    metric_type=MetricType.GAUGE,
                    unit="%",
                )
            )
            await self.record_metric(
                MetricValue(
                    name="disk_usage_bytes",
                    value=disk.used,
                    metric_type=MetricType.GAUGE,
                    unit="bytes",
                )
            )

            # 网络I/O
            network = psutil.net_io_counters()
            await self.record_metric(
                MetricValue(
                    name="network_bytes_sent",
                    value=network.bytes_sent,
                    metric_type=MetricType.COUNTER,
                    unit="bytes",
                )
            )
            await self.record_metric(
                MetricValue(
                    name="network_bytes_recv",
                    value=network.bytes_recv,
                    metric_type=MetricType.COUNTER,
                    unit="bytes",
                )
            )

            # 进程数
            process_count = len(psutil.pids())
            await self.record_metric(
                MetricValue(
                    name="process_count",
                    value=process_count,
                    metric_type=MetricType.GAUGE,
                    unit="count",
                )
            )

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")

    async def record_metric(self, metric: MetricValue) -> None:
        """记录指标"""
        if metric.name not in self.metrics:
            self.metrics[metric.name] = []

        self.metrics[metric.name].append(metric)

        # 限制指标数量
        max_metrics = self.metric_retention // 60  # 假设每分钟一个指标
        if len(self.metrics[metric.name]) > max_metrics:
            self.metrics[metric.name] = self.metrics[metric.name][-max_metrics:]

        # 发送到指标收集器
        if metric.metric_type == MetricType.COUNTER:
            await self.metrics_collector.increment(
                metric.name, metric.value, metric.tags
            )
        elif metric.metric_type == MetricType.GAUGE:
            await self.metrics_collector.gauge(metric.name, metric.value, metric.tags)
        elif metric.metric_type == MetricType.HISTOGRAM:
            await self.metrics_collector.histogram(
                metric.name, metric.value, metric.tags
            )

    async def _check_threshold_rules(self) -> None:
        """检查阈值规则"""
        for rule in self.threshold_rules:
            if rule.metric_name in self.metrics:
                recent_metrics = self._get_recent_metrics(
                    rule.metric_name, rule.duration
                )
                if recent_metrics:
                    latest_value = recent_metrics[-1].value

                    # 检查阈值
                    if self._evaluate_threshold(
                        latest_value, rule.operator, rule.threshold
                    ):
                        # 检查是否持续超过阈值
                        if self._check_duration_threshold(recent_metrics, rule):
                            await self._trigger_threshold_alert(rule, latest_value)

    def _get_recent_metrics(self, metric_name: str, duration: int) -> list[MetricValue]:
        """获取最近的指标"""
        if metric_name not in self.metrics:
            return []

        cutoff_time = datetime.now() - timedelta(seconds=duration)
        return [
            metric
            for metric in self.metrics[metric_name]
            if metric.timestamp >= cutoff_time
        ]

    def _evaluate_threshold(
        self, value: float, operator: str, threshold: float
    ) -> bool:
        """评估阈值条件"""
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        return False

    def _check_duration_threshold(
        self, metrics: list[MetricValue], rule: ThresholdRule
    ) -> bool:
        """检查持续时间阈值"""
        if len(metrics) < 2:
            return False

        # 检查最近的指标是否都超过阈值
        violation_count = 0
        for metric in metrics:
            if self._evaluate_threshold(metric.value, rule.operator, rule.threshold):
                violation_count += 1
            else:
                violation_count = 0  # 重置计数

        # 简化实现：如果最近的指标都超过阈值，则认为满足持续时间条件
        return violation_count >= len(metrics) * 0.8  # 80%的指标都超过阈值

    async def _trigger_threshold_alert(self, rule: ThresholdRule, value: float) -> None:
        """触发阈值告警"""
        alert_id = f"threshold_{rule.metric_name}_{rule.operator}_{rule.threshold}"

        # 检查是否已经有活跃的告警
        if alert_id in self.alerts and not self.alerts[alert_id].resolved:
            return

        message = (
            rule.message_template.format(value=value)
            if rule.message_template
            else f"{rule.metric_name} {rule.operator} {rule.threshold}"
        )

        alert = Alert(
            id=alert_id,
            name=f"Threshold Alert: {rule.metric_name}",
            severity=rule.severity,
            message=message,
            source="threshold_monitor",
            tags={"metric": rule.metric_name, "threshold": str(rule.threshold)},
            details={
                "value": value,
                "threshold": rule.threshold,
                "operator": rule.operator,
            },
        )

        await self._create_alert(alert)

    async def _create_alert(self, alert: Alert) -> None:
        """创建告警"""
        self.alerts[alert.id] = alert
        self.alert_history.append(alert)
        self.stats["total_alerts"] += 1
        self.stats["active_alerts"] += 1

        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")

        # 记录告警指标
        await self.metrics_collector.increment(
            "alerts_created",
            1,
            tags={"severity": alert.severity.value, "source": alert.source},
        )

        self.logger.warning(f"Alert created: {alert.name} - {alert.message}")

    async def resolve_alert(self, alert_id: str, message: str = "") -> bool:
        """解决告警"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            if not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                self.stats["active_alerts"] -= 1
                self.stats["resolved_alerts"] += 1

                # 记录解决指标
                await self.metrics_collector.increment(
                    "alerts_resolved",
                    1,
                    tags={"severity": alert.severity.value, "source": alert.source},
                )

                self.logger.info(f"Alert resolved: {alert.name} - {message}")
                return True

        return False

    async def _check_health_alerts(self, result: HealthResult) -> None:
        """检查健康状态告警"""
        alert_id = f"health_{result.name}"

        if result.status in [HealthStatus.CRITICAL, HealthStatus.DOWN]:
            # 创建或更新告警
            if alert_id not in self.alerts or self.alerts[alert_id].resolved:
                severity = (
                    AlertSeverity.CRITICAL
                    if result.status == HealthStatus.DOWN
                    else AlertSeverity.WARNING
                )

                alert = Alert(
                    id=alert_id,
                    name=f"Health Check Failed: {result.name}",
                    severity=severity,
                    message=result.message or f"Health check {result.name} failed",
                    source="health_monitor",
                    tags={"check": result.name, "status": result.status.value},
                    details=result.details,
                )

                await self._create_alert(alert)

        elif result.status == HealthStatus.HEALTHY:
            # 解决告警
            if alert_id in self.alerts and not self.alerts[alert_id].resolved:
                await self.resolve_alert(alert_id, "Health check recovered")

    async def _cleanup_expired_data(self) -> None:
        """清理过期数据"""
        cutoff_time = datetime.now() - timedelta(seconds=self.metric_retention)

        # 清理过期指标
        for metric_name in list(self.metrics.keys()):
            self.metrics[metric_name] = [
                metric
                for metric in self.metrics[metric_name]
                if metric.timestamp >= cutoff_time
            ]

            if not self.metrics[metric_name]:
                del self.metrics[metric_name]

        # 清理过期告警历史
        alert_retention = timedelta(days=7)  # 保留7天
        cutoff_time = datetime.now() - alert_retention
        self.alert_history = [
            alert for alert in self.alert_history if alert.timestamp >= cutoff_time
        ]

    async def _update_statistics(self) -> None:
        """更新统计信息"""
        # 计算运行时间
        uptime = time.time() - self.stats["uptime"]

        # 更新指标
        await self.metrics_collector.gauge("health_monitor_uptime", uptime)
        await self.metrics_collector.gauge(
            "health_monitor_active_alerts", self.stats["active_alerts"]
        )
        await self.metrics_collector.gauge(
            "health_monitor_total_checks", self.stats["total_checks"]
        )

        # 计算成功率
        if self.stats["total_checks"] > 0:
            success_rate = self.stats["successful_checks"] / self.stats["total_checks"]
            await self.metrics_collector.gauge(
                "health_monitor_success_rate", success_rate
            )

    # 默认健康检查函数
    async def _check_database_connection(self) -> HealthResult:
        """检查数据库连接"""
        try:
            # 这里应该实际检查数据库连接
            # 简化实现
            await asyncio.sleep(0.1)  # 模拟检查
            return HealthResult(
                name="database_connection",
                status=HealthStatus.HEALTHY,
                message="Database connection is healthy",
            )
        except Exception as e:
            return HealthResult(
                name="database_connection",
                status=HealthStatus.DOWN,
                message="Database connection failed",
                error=str(e),
            )

    async def _check_cache_connection(self) -> HealthResult:
        """检查缓存连接"""
        try:
            # 测试缓存连接
            test_key = "health_check_test"
            await self.cache_manager.set(test_key, "test_value", ttl=10)
            value = await self.cache_manager.get(test_key)

            if value == "test_value":
                return HealthResult(
                    name="cache_connection",
                    status=HealthStatus.HEALTHY,
                    message="Cache connection is healthy",
                )
            else:
                return HealthResult(
                    name="cache_connection",
                    status=HealthStatus.WARNING,
                    message="Cache connection issue: value mismatch",
                )
        except Exception as e:
            return HealthResult(
                name="cache_connection",
                status=HealthStatus.DOWN,
                message="Cache connection failed",
                error=str(e),
            )

    async def _check_memory_usage(self) -> HealthResult:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()

            if memory.percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Memory usage is normal: {memory.percent:.1f}%"
            elif memory.percent < 90:
                status = HealthStatus.WARNING
                message = f"Memory usage is high: {memory.percent:.1f}%"
            else:
                status = HealthStatus.CRITICAL
                message = f"Memory usage is critical: {memory.percent:.1f}%"

            return HealthResult(
                name="memory_usage",
                status=status,
                message=message,
                details={
                    "percent": memory.percent,
                    "used": memory.used,
                    "available": memory.available,
                    "total": memory.total,
                },
            )
        except Exception as e:
            return HealthResult(
                name="memory_usage",
                status=HealthStatus.DOWN,
                message="Memory check failed",
                error=str(e),
            )

    async def _check_disk_space(self) -> HealthResult:
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage("/")
            percent = (disk.used / disk.total) * 100

            if percent < 80:
                status = HealthStatus.HEALTHY
                message = f"Disk usage is normal: {percent:.1f}%"
            elif percent < 90:
                status = HealthStatus.WARNING
                message = f"Disk usage is high: {percent:.1f}%"
            else:
                status = HealthStatus.CRITICAL
                message = f"Disk usage is critical: {percent:.1f}%"

            return HealthResult(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "percent": percent,
                    "used": disk.used,
                    "free": disk.free,
                    "total": disk.total,
                },
            )
        except Exception as e:
            return HealthResult(
                name="disk_space",
                status=HealthStatus.DOWN,
                message="Disk check failed",
                error=str(e),
            )

    async def _check_api_response_time(self) -> HealthResult:
        """检查API响应时间"""
        try:
            start_time = time.time()

            # 这里应该实际调用API
            # 简化实现
            await asyncio.sleep(0.05)  # 模拟API调用

            response_time = (time.time() - start_time) * 1000  # 转换为毫秒

            if response_time < 500:
                status = HealthStatus.HEALTHY
                message = f"API response time is good: {response_time:.1f}ms"
            elif response_time < 1000:
                status = HealthStatus.WARNING
                message = f"API response time is slow: {response_time:.1f}ms"
            else:
                status = HealthStatus.CRITICAL
                message = f"API response time is very slow: {response_time:.1f}ms"

            # 记录响应时间指标
            await self.record_metric(
                MetricValue(
                    name="api_response_time_ms",
                    value=response_time,
                    metric_type=MetricType.HISTOGRAM,
                    unit="ms",
                )
            )

            return HealthResult(
                name="api_response_time",
                status=status,
                message=message,
                details={"response_time_ms": response_time},
            )
        except Exception as e:
            return HealthResult(
                name="api_response_time",
                status=HealthStatus.DOWN,
                message="API response time check failed",
                error=str(e),
            )

    @timer
    async def get_health_status(self) -> dict[str, Any]:
        """获取整体健康状态"""
        overall_status = HealthStatus.HEALTHY
        failed_checks = []
        warning_checks = []

        for name, result in self.health_results.items():
            if result.status == HealthStatus.DOWN:
                overall_status = HealthStatus.DOWN
                failed_checks.append(name)
            elif result.status == HealthStatus.CRITICAL:
                if overall_status != HealthStatus.DOWN:
                    overall_status = HealthStatus.CRITICAL
                failed_checks.append(name)
            elif result.status == HealthStatus.WARNING:
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.WARNING
                warning_checks.append(name)

        return {
            "status": overall_status.value,
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.stats["uptime"],
            "checks": {
                name: {
                    "status": result.status.value,
                    "message": result.message,
                    "last_check": result.timestamp.isoformat(),
                    "duration": result.duration,
                }
                for name, result in self.health_results.items()
            },
            "failed_checks": failed_checks,
            "warning_checks": warning_checks,
            "active_alerts": self.stats["active_alerts"],
            "statistics": self.stats,
        }

    async def get_metrics(self, metric_name: str | None = None) -> dict[str, Any]:
        """获取指标数据"""
        if metric_name:
            return {
                metric_name: [
                    {
                        "value": metric.value,
                        "timestamp": metric.timestamp.isoformat(),
                        "tags": metric.tags,
                        "unit": metric.unit,
                    }
                    for metric in self.metrics.get(metric_name, [])
                ]
            }
        else:
            return {
                name: [
                    {
                        "value": metric.value,
                        "timestamp": metric.timestamp.isoformat(),
                        "tags": metric.tags,
                        "unit": metric.unit,
                    }
                    for metric in metrics
                ]
                for name, metrics in self.metrics.items()
            }

    async def get_alerts(self, active_only: bool = False) -> list[dict[str, Any]]:
        """获取告警列表"""
        alerts = self.alerts.values() if active_only else self.alert_history

        if active_only:
            alerts = [alert for alert in alerts if not alert.resolved]

        return [
            {
                "id": alert.id,
                "name": alert.name,
                "severity": alert.severity.value,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat()
                if alert.resolved_at
                else None,
                "tags": alert.tags,
                "details": alert.details,
            }
            for alert in alerts
        ]

    async def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "health_monitor_stats": self.stats,
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
                "boot_time": psutil.boot_time(),
            },
            "cache_stats": await self.cache_manager.get_stats(),
            "metrics_stats": await self.metrics_collector.get_metrics(),
        }
