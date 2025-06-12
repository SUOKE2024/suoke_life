"""
health_monitor - 索克生活项目模块
"""

import asyncio
import contextlib
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .health_checker import HealthChecker

"""
健康监控器
提供持续的健康状态监控和告警功能
"""


logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """健康告警"""

    level: AlertLevel
    component: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolved_at: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "level": self.level.value,
            "component": self.component,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }


class HealthMonitor:
    """健康监控器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.health_checker = HealthChecker()
        self.config = {}
        self.monitoring = False
        self.monitor_task = None
        self.alert_handlers: list[Callable] = []
        self.active_alerts: dict[str, HealthAlert] = {}
        self.alert_history: list[HealthAlert] = []
        self.health_history: list[dict[str, Any]] = []
        self.max_history_size = 1000

    async def initialize(self, config: dict[str, Any]):
        """初始化健康监控器"""
        self.config = config

        # 初始化健康检查器
        await self.health_checker.initialize(config.get("health_checker", {}))

        # 监控配置
        self.monitor_interval = config.get("monitor_interval", 30)  # 监控间隔（秒）
        self.alert_cooldown = config.get("alert_cooldown", 300)  # 告警冷却时间（秒）
        self.max_history_size = config.get("max_history_size", 1000)

        # 告警阈值配置
        self.alert_thresholds = config.get(
            "alert_thresholds",
            {
                "consecutive_failures": 3,  # 连续失败次数
                "failure_rate": 0.5,  # 失败率阈值
                "response_time_threshold": 5.0,  # 响应时间阈值（秒）
            },
        )

        logger.info("健康监控器初始化完成")

    def add_alert_handler(self, handler: Callable[[HealthAlert], None]):
        """添加告警处理器"""
        self.alert_handlers.append(handler)

    async def start_monitoring(self) -> None:
        """开始监控"""
        if self.monitoring:
            logger.warning("健康监控已在运行")
            return

        self.monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("开始健康监控")

    async def stop_monitoring(self) -> None:
        """停止监控"""
        if not self.monitoring:
            return

        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitor_task

        logger.info("停止健康监控")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        consecutive_failures = {}

        while self.monitoring:
            try:
                # 执行健康检查
                health_result = await self.health_checker.health_check()

                # 记录健康历史
                self._record_health_history(health_result)

                # 分析健康状态并生成告警
                await self._analyze_health_status(health_result, consecutive_failures)

                # 等待下次检查
                await asyncio.sleep(self.monitor_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康监控循环异常: {e}")
                await asyncio.sleep(self.monitor_interval)

    def _record_health_history(self, health_result: dict[str, Any]):
        """记录健康历史"""
        self.health_history.append(health_result)

        # 限制历史记录大小
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size :]

    async def _analyze_health_status(
        self, health_result: dict[str, Any], consecutive_failures: dict[str, int]
    ):
        """分析健康状态并生成告警"""
        overall_status = health_result.get("status", "unknown")
        checks = health_result.get("checks", {})

        # 检查整体状态
        if overall_status == "unhealthy":
            await self._create_alert(
                AlertLevel.CRITICAL,
                "system",
                "系统整体状态不健康",
                {"overall_status": overall_status, "checks": len(checks)},
            )
        elif overall_status == "degraded":
            await self._create_alert(
                AlertLevel.WARNING,
                "system",
                "系统状态降级",
                {"overall_status": overall_status, "checks": len(checks)},
            )
        else:
            # 解决系统级告警
            await self._resolve_alert("system")

        # 检查各个组件
        for check_name, check_result in checks.items():
            await self._analyze_component_health(
                check_name, check_result, consecutive_failures
            )

    async def _analyze_component_health(
        self,
        component_name: str,
        check_result: dict[str, Any],
        consecutive_failures: dict[str, int],
    ):
        """分析组件健康状态"""
        status = check_result.get("status", "unknown")
        duration_ms = check_result.get("duration_ms", 0)

        # 初始化连续失败计数
        if component_name not in consecutive_failures:
            consecutive_failures[component_name] = 0

        if status == "unhealthy":
            consecutive_failures[component_name] += 1

            # 检查连续失败次数
            if (
                consecutive_failures[component_name]
                >= self.alert_thresholds["consecutive_failures"]
            ):
                await self._create_alert(
                    AlertLevel.ERROR,
                    component_name,
                    f"组件连续失败 {consecutive_failures[component_name]} 次",
                    {
                        "consecutive_failures": consecutive_failures[component_name],
                        "check_result": check_result,
                    },
                )

        elif status == "degraded":
            await self._create_alert(
                AlertLevel.WARNING,
                component_name,
                "组件性能降级",
                {"check_result": check_result},
            )

        else:
            # 组件恢复正常，重置失败计数并解决告警
            consecutive_failures[component_name] = 0
            await self._resolve_alert(component_name)

        # 检查响应时间
        if duration_ms > self.alert_thresholds["response_time_threshold"] * 1000:
            await self._create_alert(
                AlertLevel.WARNING,
                component_name,
                f"组件响应时间过长: {duration_ms:.1f}ms",
                {
                    "duration_ms": duration_ms,
                    "threshold_ms": self.alert_thresholds["response_time_threshold"]
                    * 1000,
                },
            )

    async def _create_alert(
        self,
        level: AlertLevel,
        component: str,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """创建告警"""
        alert_key = f"{component}:{level.value}"

        # 检查是否已存在相同告警（避免重复告警）
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            # 检查冷却时间
            if time.time() - existing_alert.timestamp < self.alert_cooldown:
                return

        # 创建新告警
        alert = HealthAlert(
            level=level, component=component, message=message, details=details or {}
        )

        self.active_alerts[alert_key] = alert
        self.alert_history.append(alert)

        # 限制告警历史大小
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size :]

        # 通知告警处理器
        for handler in self.alert_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"告警处理器异常: {e}")

        logger.warning(f"创建告警 [{level.value}] {component}: {message}")

    async def _resolve_alert(self, component: str):
        """解决告警"""
        resolved_alerts = []

        for alert_key, alert in list(self.active_alerts.items()):
            if alert.component == component and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = time.time()
                resolved_alerts.append(alert)
                del self.active_alerts[alert_key]

        for alert in resolved_alerts:
            logger.info(
                f"解决告警 [{alert.level.value}] {alert.component}: {alert.message}"
            )

    async def get_health_summary(self) -> dict[str, Any]:
        """获取健康状态摘要"""
        if not self.health_history:
            return {"status": "unknown", "message": "暂无健康数据"}

        latest_health = self.health_history[-1]

        # 统计告警
        active_alerts_by_level = {}
        for alert in self.active_alerts.values():
            level = alert.level.value
            if level not in active_alerts_by_level:
                active_alerts_by_level[level] = 0
            active_alerts_by_level[level] += 1

        # 计算健康趋势
        trend = self._calculate_health_trend()

        return {
            "status": latest_health.get("status", "unknown"),
            "timestamp": latest_health.get("timestamp", time.time()),
            "checks_summary": latest_health.get("summary", {}),
            "active_alerts": {
                "total": len(self.active_alerts),
                "by_level": active_alerts_by_level,
            },
            "trend": trend,
            "monitoring": self.monitoring,
            "last_check": latest_health.get("timestamp", 0),
        }

    def _calculate_health_trend(self) -> str:
        """计算健康趋势"""
        if len(self.health_history) < 2:
            return "stable"

        # 取最近10次检查结果
        recent_checks = self.health_history[-10:]

        healthy_count = len([h for h in recent_checks if h.get("status") == "healthy"])
        total_count = len(recent_checks)

        if len(self.health_history) >= 20:
            # 比较前10次和后10次
            previous_checks = self.health_history[-20:-10]
            previous_healthy = len(
                [h for h in previous_checks if h.get("status") == "healthy"]
            )
            previous_rate = previous_healthy / len(previous_checks)
            current_rate = healthy_count / total_count

            if current_rate > previous_rate + 0.2:
                return "improving"
            elif current_rate < previous_rate - 0.2:
                return "degrading"

        return "stable"

    async def get_alerts(
        self,
        active_only: bool = False,
        level: AlertLevel | None = None,
        component: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """获取告警列表"""
        alerts = (
            list(self.active_alerts.values()) if active_only else self.alert_history
        )

        # 过滤条件
        if level:
            alerts = [a for a in alerts if a.level == level]

        if component:
            alerts = [a for a in alerts if a.component == component]

        # 按时间倒序排序
        alerts.sort(key=lambda a: a.timestamp, reverse=True)

        # 限制数量
        alerts = alerts[:limit]

        return [alert.to_dict() for alert in alerts]

    async def get_health_metrics(self) -> dict[str, Any]:
        """获取健康指标"""
        if not self.health_history:
            return {}

        # 计算可用性
        recent_checks = self.health_history[-100:]  # 最近100次检查
        healthy_count = len([h for h in recent_checks if h.get("status") == "healthy"])
        availability = healthy_count / len(recent_checks) if recent_checks else 0

        # 计算平均响应时间
        total_duration = 0
        check_count = 0

        for health_result in recent_checks:
            checks = health_result.get("checks", {})
            for check_result in checks.values():
                duration = check_result.get("duration_ms", 0)
                if duration > 0:
                    total_duration += duration
                    check_count += 1

        avg_response_time = total_duration / check_count if check_count > 0 else 0

        return {
            "availability": availability,
            "avg_response_time_ms": avg_response_time,
            "total_checks": len(self.health_history),
            "active_alerts": len(self.active_alerts),
            "monitoring_uptime": (
                time.time() - self.health_history[0].get("timestamp", time.time())
                if self.health_history
                else 0
            ),
        }

    async def health_check(self) -> dict[str, Any]:
        """监控器自身健康检查"""
        return {
            "status": "healthy" if self.monitoring else "stopped",
            "monitoring": self.monitoring,
            "active_alerts": len(self.active_alerts),
            "health_history_size": len(self.health_history),
            "alert_handlers": len(self.alert_handlers),
        }

    async def shutdown(self) -> None:
        """关闭监控器"""
        await self.stop_monitoring()
        await self.health_checker.shutdown()
        self.alert_handlers.clear()
        self.active_alerts.clear()
        logger.info("健康监控器已关闭")
