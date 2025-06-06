"""
health_monitor - 索克生活项目模块
"""

            import gc
from ..common.base import BaseService
from ..common.exceptions import InquiryServiceError
from ..common.metrics import memory_optimized, timer
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from typing import Any
import asyncio
import psutil
import time

#!/usr/bin/env python3

"""
实时健康监测模块

该模块实现服务的实时健康监测，包括健康检查、性能监控、
异常检测和自动恢复机制。
"""





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


@dataclass
class HealthCheck:
    """健康检查"""

    name: str
    check_function: Callable
    interval: float  # 检查间隔（秒）
    timeout: float  # 超时时间（秒）
    critical: bool = False  # 是否为关键检查
    enabled: bool = True
    last_check: datetime | None = None
    last_status: HealthStatus = HealthStatus.HEALTHY
    consecutive_failures: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetric:
    """性能指标"""

    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """告警"""

    id: str
    name: str
    level: str  # info, warning, critical
    message: str
    timestamp: datetime
    source: str
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemResources:
    """系统资源"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: dict[str, int]
    process_count: int
    load_average: list[float]
    timestamp: datetime


class HealthMonitor(BaseService):
    """健康监测器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化健康监测器

        Args:
            config: 配置信息
        """
        super().__init__(config)

        # 健康检查
        self.health_checks: dict[str, HealthCheck] = {}

        # 性能指标
        self.metrics: dict[str, list[PerformanceMetric]] = {}
        self.metric_retention = timedelta(hours=24)  # 指标保留时间

        # 告警
        self.alerts: dict[str, Alert] = {}
        self.alert_handlers: list[Callable] = []

        # 监控配置
        self.monitor_config = {
            "check_interval": 30.0,  # 默认检查间隔
            "metric_collection_interval": 10.0,  # 指标收集间隔
            "alert_cooldown": 300.0,  # 告警冷却时间
            "max_consecutive_failures": 3,  # 最大连续失败次数
            "resource_thresholds": {
                "cpu_warning": 70.0,
                "cpu_critical": 90.0,
                "memory_warning": 80.0,
                "memory_critical": 95.0,
                "disk_warning": 85.0,
                "disk_critical": 95.0,
            },
        }

        # 运行状态
        self.is_monitoring = False
        self.monitor_tasks: list[asyncio.Task] = []

        # 统计信息
        self.stats = {
            "total_checks": 0,
            "failed_checks": 0,
            "alerts_generated": 0,
            "uptime_start": datetime.now(),
            "last_health_check": None,
        }

        self._initialize_default_checks()

        logger.info("健康监测器初始化完成")

    def _initialize_default_checks(self):
        """初始化默认健康检查"""
        # 系统资源检查
        self.add_health_check(
            name="system_resources",
            check_function=self._check_system_resources,
            interval=30.0,
            timeout=5.0,
            critical=True,
        )

        # 内存使用检查
        self.add_health_check(
            name="memory_usage",
            check_function=self._check_memory_usage,
            interval=60.0,
            timeout=5.0,
            critical=True,
        )

        # 数据库连接检查
        self.add_health_check(
            name="database_connection",
            check_function=self._check_database_connection,
            interval=120.0,
            timeout=10.0,
            critical=True,
        )

        # 缓存服务检查
        self.add_health_check(
            name="cache_service",
            check_function=self._check_cache_service,
            interval=60.0,
            timeout=5.0,
            critical=False,
        )

        # 外部API检查
        self.add_health_check(
            name="external_apis",
            check_function=self._check_external_apis,
            interval=300.0,
            timeout=15.0,
            critical=False,
        )

    def add_health_check(
        self,
        name: str,
        check_function: Callable,
        interval: float,
        timeout: float,
        critical: bool = False,
    ):
        """
        添加健康检查

        Args:
            name: 检查名称
            check_function: 检查函数
            interval: 检查间隔
            timeout: 超时时间
            critical: 是否为关键检查
        """
        health_check = HealthCheck(
            name=name,
            check_function=check_function,
            interval=interval,
            timeout=timeout,
            critical=critical,
        )

        self.health_checks[name] = health_check
        logger.info(f"健康检查已添加: {name}")

    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
        logger.info("告警处理器已添加")

    async def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            logger.warning("监控已在运行中")
            return

        self.is_monitoring = True

        # 启动健康检查任务
        check_task = asyncio.create_task(self._health_check_loop())
        self.monitor_tasks.append(check_task)

        # 启动指标收集任务
        metric_task = asyncio.create_task(self._metric_collection_loop())
        self.monitor_tasks.append(metric_task)

        # 启动告警处理任务
        alert_task = asyncio.create_task(self._alert_processing_loop())
        self.monitor_tasks.append(alert_task)

        # 启动清理任务
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.monitor_tasks.append(cleanup_task)

        logger.info("健康监控已启动")

    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False

        # 取消所有监控任务
        for task in self.monitor_tasks:
            task.cancel()

        # 等待任务完成
        await asyncio.gather(*self.monitor_tasks, return_exceptions=True)
        self.monitor_tasks.clear()

        logger.info("健康监控已停止")

    async def _health_check_loop(self):
        """健康检查循环"""
        while self.is_monitoring:
            try:
                await self._run_health_checks()
                await asyncio.sleep(self.monitor_config["check_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查循环错误: {e}")
                await asyncio.sleep(5.0)

    async def _run_health_checks(self):
        """运行健康检查"""
        current_time = datetime.now()

        for check_name, health_check in self.health_checks.items():
            if not health_check.enabled:
                continue

            # 检查是否到了执行时间
            if (
                health_check.last_check
                and (current_time - health_check.last_check).total_seconds()
                < health_check.interval
            ):
                continue

            try:
                # 执行健康检查
                result = await asyncio.wait_for(
                    health_check.check_function(), timeout=health_check.timeout
                )

                # 更新检查状态
                health_check.last_check = current_time

                if result.get("status") == "healthy":
                    health_check.last_status = HealthStatus.HEALTHY
                    health_check.consecutive_failures = 0
                else:
                    health_check.consecutive_failures += 1

                    if (
                        health_check.consecutive_failures
                        >= self.monitor_config["max_consecutive_failures"]
                    ):
                        health_check.last_status = HealthStatus.CRITICAL
                        await self._generate_alert(
                            name=f"health_check_{check_name}",
                            level="critical",
                            message=f"健康检查 {check_name} 连续失败 {health_check.consecutive_failures} 次",
                            source="health_monitor",
                        )
                    else:
                        health_check.last_status = HealthStatus.WARNING

                self.stats["total_checks"] += 1

            except TimeoutError:
                health_check.consecutive_failures += 1
                health_check.last_status = HealthStatus.CRITICAL
                self.stats["failed_checks"] += 1

                await self._generate_alert(
                    name=f"health_check_timeout_{check_name}",
                    level="critical",
                    message=f"健康检查 {check_name} 超时",
                    source="health_monitor",
                )

            except Exception as e:
                health_check.consecutive_failures += 1
                health_check.last_status = HealthStatus.CRITICAL
                self.stats["failed_checks"] += 1

                logger.error(f"健康检查 {check_name} 失败: {e}")

                await self._generate_alert(
                    name=f"health_check_error_{check_name}",
                    level="critical",
                    message=f"健康检查 {check_name} 执行失败: {e!s}",
                    source="health_monitor",
                )

        self.stats["last_health_check"] = current_time

    async def _metric_collection_loop(self):
        """指标收集循环"""
        while self.is_monitoring:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.monitor_config["metric_collection_interval"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集循环错误: {e}")
                await asyncio.sleep(5.0)

    async def _collect_system_metrics(self):
        """收集系统指标"""
        current_time = datetime.now()

        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        await self._record_metric(
            name="system.cpu.percent",
            metric_type=MetricType.GAUGE,
            value=cpu_percent,
            timestamp=current_time,
        )

        # 内存使用率
        memory = psutil.virtual_memory()
        await self._record_metric(
            name="system.memory.percent",
            metric_type=MetricType.GAUGE,
            value=memory.percent,
            timestamp=current_time,
        )

        # 磁盘使用率
        disk = psutil.disk_usage("/")
        disk_percent = (disk.used / disk.total) * 100
        await self._record_metric(
            name="system.disk.percent",
            metric_type=MetricType.GAUGE,
            value=disk_percent,
            timestamp=current_time,
        )

        # 网络IO
        network = psutil.net_io_counters()
        await self._record_metric(
            name="system.network.bytes_sent",
            metric_type=MetricType.COUNTER,
            value=network.bytes_sent,
            timestamp=current_time,
        )
        await self._record_metric(
            name="system.network.bytes_recv",
            metric_type=MetricType.COUNTER,
            value=network.bytes_recv,
            timestamp=current_time,
        )

        # 进程数量
        process_count = len(psutil.pids())
        await self._record_metric(
            name="system.process.count",
            metric_type=MetricType.GAUGE,
            value=process_count,
            timestamp=current_time,
        )

        # 检查阈值并生成告警
        await self._check_metric_thresholds(cpu_percent, memory.percent, disk_percent)

    async def _record_metric(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        timestamp: datetime,
        tags: dict[str, str] | None = None,
    ):
        """记录指标"""
        metric = PerformanceMetric(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=timestamp,
            tags=tags or {},
        )

        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(metric)

        # 限制指标数量
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-500:]

    async def _check_metric_thresholds(
        self, cpu_percent: float, memory_percent: float, disk_percent: float
    ):
        """检查指标阈值"""
        thresholds = self.monitor_config["resource_thresholds"]

        # CPU检查
        if cpu_percent >= thresholds["cpu_critical"]:
            await self._generate_alert(
                name="high_cpu_usage",
                level="critical",
                message=f"CPU使用率过高: {cpu_percent:.1f}%",
                source="metric_monitor",
            )
        elif cpu_percent >= thresholds["cpu_warning"]:
            await self._generate_alert(
                name="high_cpu_usage",
                level="warning",
                message=f"CPU使用率较高: {cpu_percent:.1f}%",
                source="metric_monitor",
            )

        # 内存检查
        if memory_percent >= thresholds["memory_critical"]:
            await self._generate_alert(
                name="high_memory_usage",
                level="critical",
                message=f"内存使用率过高: {memory_percent:.1f}%",
                source="metric_monitor",
            )
        elif memory_percent >= thresholds["memory_warning"]:
            await self._generate_alert(
                name="high_memory_usage",
                level="warning",
                message=f"内存使用率较高: {memory_percent:.1f}%",
                source="metric_monitor",
            )

        # 磁盘检查
        if disk_percent >= thresholds["disk_critical"]:
            await self._generate_alert(
                name="high_disk_usage",
                level="critical",
                message=f"磁盘使用率过高: {disk_percent:.1f}%",
                source="metric_monitor",
            )
        elif disk_percent >= thresholds["disk_warning"]:
            await self._generate_alert(
                name="high_disk_usage",
                level="warning",
                message=f"磁盘使用率较高: {disk_percent:.1f}%",
                source="metric_monitor",
            )

    async def _alert_processing_loop(self):
        """告警处理循环"""
        while self.is_monitoring:
            try:
                await self._process_alerts()
                await asyncio.sleep(10.0)  # 每10秒处理一次告警
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"告警处理循环错误: {e}")
                await asyncio.sleep(5.0)

    async def _process_alerts(self):
        """处理告警"""
        current_time = datetime.now()

        for alert_id, alert in list(self.alerts.items()):
            if alert.resolved:
                continue

            # 检查告警冷却时间
            time_since_alert = (current_time - alert.timestamp).total_seconds()
            if time_since_alert < self.monitor_config["alert_cooldown"]:
                continue

            # 调用告警处理器
            for handler in self.alert_handlers:
                try:
                    await handler(alert)
                except Exception as e:
                    logger.error(f"告警处理器执行失败: {e}")

    async def _cleanup_loop(self):
        """清理循环"""
        while self.is_monitoring:
            try:
                await self._cleanup_old_data()
                await asyncio.sleep(3600.0)  # 每小时清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")
                await asyncio.sleep(300.0)

    async def _cleanup_old_data(self):
        """清理旧数据"""
        current_time = datetime.now()
        cutoff_time = current_time - self.metric_retention

        # 清理旧指标
        for metric_name, metric_list in self.metrics.items():
            self.metrics[metric_name] = [
                metric for metric in metric_list if metric.timestamp > cutoff_time
            ]

        # 清理已解决的告警
        resolved_alerts = [
            alert_id
            for alert_id, alert in self.alerts.items()
            if alert.resolved and (current_time - alert.timestamp).days > 7
        ]

        for alert_id in resolved_alerts:
            del self.alerts[alert_id]

        logger.debug("旧数据清理完成")

    async def _generate_alert(
        self,
        name: str,
        level: str,
        message: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ):
        """生成告警"""
        alert_id = f"{name}_{int(time.time())}"

        alert = Alert(
            id=alert_id,
            name=name,
            level=level,
            message=message,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {},
        )

        self.alerts[alert_id] = alert
        self.stats["alerts_generated"] += 1

        logger.warning(f"告警生成: {level} - {message}")

    # 默认健康检查函数
    async def _check_system_resources(self) -> dict[str, Any]:
        """检查系统资源"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # 检查资源使用是否正常
            if (
                cpu_percent < 95
                and memory.percent < 95
                and (disk.used / disk.total) * 100 < 95
            ):
                return {
                    "status": "healthy",
                    "details": {
                        "cpu": cpu_percent,
                        "memory": memory.percent,
                        "disk": (disk.used / disk.total) * 100,
                    },
                }
            else:
                return {
                    "status": "unhealthy",
                    "details": {
                        "cpu": cpu_percent,
                        "memory": memory.percent,
                        "disk": (disk.used / disk.total) * 100,
                    },
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _check_memory_usage(self) -> dict[str, Any]:
        """检查内存使用"""
        try:

            # 强制垃圾回收
            gc.collect()

            # 获取内存信息
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()

            return {
                "status": "healthy" if memory.percent < 90 else "unhealthy",
                "details": {
                    "system_memory_percent": memory.percent,
                    "process_memory_mb": process_memory.rss / 1024 / 1024,
                    "gc_objects": len(gc.get_objects()),
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _check_database_connection(self) -> dict[str, Any]:
        """检查数据库连接"""
        try:
            # 这里应该实现实际的数据库连接检查
            # 简化实现
            await asyncio.sleep(0.1)  # 模拟数据库查询
            return {"status": "healthy", "details": {"connection": "ok"}}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _check_cache_service(self) -> dict[str, Any]:
        """检查缓存服务"""
        try:
            # 这里应该实现实际的缓存服务检查
            # 简化实现
            await asyncio.sleep(0.05)  # 模拟缓存操作
            return {"status": "healthy", "details": {"cache": "ok"}}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _check_external_apis(self) -> dict[str, Any]:
        """检查外部API"""
        try:
            # 这里应该实现实际的外部API检查
            # 简化实现
            await asyncio.sleep(0.2)  # 模拟API调用
            return {"status": "healthy", "details": {"apis": "ok"}}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @timer("health_monitor.get_health_status")
    async def get_health_status(self) -> dict[str, Any]:
        """获取健康状态"""
        overall_status = HealthStatus.HEALTHY
        check_results = {}

        for check_name, health_check in self.health_checks.items():
            check_results[check_name] = {
                "status": health_check.last_status.value,
                "last_check": health_check.last_check.isoformat()
                if health_check.last_check
                else None,
                "consecutive_failures": health_check.consecutive_failures,
                "critical": health_check.critical,
            }

            # 更新整体状态
            if (
                health_check.critical
                and health_check.last_status == HealthStatus.CRITICAL
            ):
                overall_status = HealthStatus.CRITICAL
            elif (
                health_check.last_status == HealthStatus.WARNING
                and overall_status == HealthStatus.HEALTHY
            ):
                overall_status = HealthStatus.WARNING

        return {
            "overall_status": overall_status.value,
            "checks": check_results,
            "uptime_seconds": (
                datetime.now() - self.stats["uptime_start"]
            ).total_seconds(),
            "stats": self.stats,
        }

    @memory_optimized
    async def get_metrics(
        self,
        metric_names: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """获取指标数据"""
        result = {}

        target_metrics = metric_names or list(self.metrics.keys())
        start_time = start_time or (datetime.now() - timedelta(hours=1))
        end_time = end_time or datetime.now()

        for metric_name in target_metrics:
            if metric_name not in self.metrics:
                continue

            filtered_metrics = [
                {
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "tags": metric.tags,
                }
                for metric in self.metrics[metric_name]
                if start_time <= metric.timestamp <= end_time
            ]

            result[metric_name] = filtered_metrics

        return result

    async def get_alerts(
        self, resolved: bool | None = None, level: str | None = None
    ) -> list[dict[str, Any]]:
        """获取告警列表"""
        alerts = []

        for alert in self.alerts.values():
            if resolved is not None and alert.resolved != resolved:
                continue
            if level is not None and alert.level != level:
                continue

            alerts.append(
                {
                    "id": alert.id,
                    "name": alert.name,
                    "level": alert.level,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "source": alert.source,
                    "resolved": alert.resolved,
                    "metadata": alert.metadata,
                }
            )

        # 按时间倒序排列
        alerts.sort(key=lambda x: x["timestamp"], reverse=True)

        return alerts

    async def resolve_alert(self, alert_id: str):
        """解决告警"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            logger.info(f"告警已解决: {alert_id}")
        else:
            raise InquiryServiceError(f"告警不存在: {alert_id}")

    async def get_system_resources(self) -> SystemResources:
        """获取系统资源信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        network = psutil.net_io_counters()
        process_count = len(psutil.pids())
        load_avg = (
            psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0.0, 0.0, 0.0]
        )

        return SystemResources(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=(disk.used / disk.total) * 100,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            },
            process_count=process_count,
            load_average=list(load_avg),
            timestamp=datetime.now(),
        )
