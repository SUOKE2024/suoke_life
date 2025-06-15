#!/usr/bin/env python3
"""
高级健康检查模块
扩展健康检查功能，包含更多检查器、告警机制和自动恢复
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

# Email imports (optional, for future email notifications)
# import smtplib
# from email.mime.text import MimeText
# from email.mime.multipart import MimeMultipart
from .health_check import (
    HealthChecker,
    HealthCheckResult,
    HealthStatus,
    global_health_manager,
)

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """告警严重程度"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    condition: str  # 条件表达式
    severity: AlertSeverity
    message_template: str
    cooldown_seconds: int = 300  # 冷却时间，防止重复告警
    enabled: bool = True
    last_triggered: float = 0.0


@dataclass
class Alert:
    """告警信息"""

    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: float = field(default_factory=time.time)
    health_check_result: HealthCheckResult | None = None
    resolved: bool = False
    resolved_at: float | None = None


class NetworkHealthChecker(HealthChecker):
    """网络连接健康检查器"""

    def __init__(self, endpoints: list[str], timeout: float = 5.0):
        super().__init__("network_connectivity", timeout)
        self.endpoints = endpoints

    async def _perform_check(self) -> dict[str, Any]:
        """检查网络连接"""
        results = {}
        failed_endpoints = []

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            for endpoint in self.endpoints:
                try:
                    start_time = time.time()
                    async with session.get(endpoint) as response:
                        response_time = (time.time() - start_time) * 1000  # ms
                        results[endpoint] = {
                            "status": response.status,
                            "response_time_ms": round(response_time, 2),
                            "success": response.status < 400,
                        }

                        if response.status >= 400:
                            failed_endpoints.append(endpoint)

                except Exception as e:
                    results[endpoint] = {
                        "status": 0,
                        "response_time_ms": 0,
                        "success": False,
                        "error": str(e),
                    }
                    failed_endpoints.append(endpoint)

        # 计算健康状态
        total_endpoints = len(self.endpoints)
        failed_count = len(failed_endpoints)
        success_rate = (total_endpoints - failed_count) / total_endpoints * 100

        if success_rate == 100:
            status = HealthStatus.HEALTHY
            message = f"所有网络端点正常 ({total_endpoints}/{total_endpoints})"
        elif success_rate >= 80:
            status = HealthStatus.DEGRADED
            message = (
                f"部分网络端点异常 ({total_endpoints - failed_count}/{total_endpoints})"
            )
        else:
            status = HealthStatus.UNHEALTHY
            message = (
                f"多个网络端点异常 ({total_endpoints - failed_count}/{total_endpoints})"
            )

        return {
            "status": status,
            "message": message,
            "details": {
                "endpoints": results,
                "success_rate": round(success_rate, 1),
                "failed_endpoints": failed_endpoints,
            },
        }


class DiskSpaceHealthChecker(HealthChecker):
    """磁盘空间健康检查器"""

    def __init__(
        self,
        paths: list[str] = None,
        warning_threshold: float = 80.0,
        critical_threshold: float = 90.0,
        timeout: float = 2.0,
    ):
        super().__init__("disk_space", timeout)
        self.paths = paths or ["/", "/tmp"]
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold

    async def _perform_check(self) -> dict[str, Any]:
        """检查磁盘空间"""
        try:
            import psutil

            disk_info = {}
            issues = []
            max_usage = 0.0

            for path in self.paths:
                try:
                    usage = psutil.disk_usage(path)
                    usage_percent = (usage.used / usage.total) * 100
                    max_usage = max(max_usage, usage_percent)

                    disk_info[path] = {
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "usage_percent": round(usage_percent, 1),
                    }

                    if usage_percent >= self.critical_threshold:
                        issues.append(f"{path}: {usage_percent:.1f}% (严重)")
                    elif usage_percent >= self.warning_threshold:
                        issues.append(f"{path}: {usage_percent:.1f}% (警告)")

                except Exception as e:
                    disk_info[path] = {"error": str(e)}
                    issues.append(f"{path}: 检查失败")

            # 确定健康状态
            if max_usage >= self.critical_threshold:
                status = HealthStatus.UNHEALTHY
                message = f"磁盘空间严重不足: {'; '.join(issues)}"
            elif max_usage >= self.warning_threshold:
                status = HealthStatus.DEGRADED
                message = f"磁盘空间不足: {'; '.join(issues)}"
            else:
                status = HealthStatus.HEALTHY
                message = f"磁盘空间正常 (最高使用率: {max_usage:.1f}%)"

            return {
                "status": status,
                "message": message,
                "details": {
                    "disks": disk_info,
                    "max_usage_percent": round(max_usage, 1),
                    "warning_threshold": self.warning_threshold,
                    "critical_threshold": self.critical_threshold,
                },
            }

        except ImportError:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "psutil库未安装，无法检查磁盘空间",
                "details": {"psutil_available": False},
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"磁盘空间检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class ProcessHealthChecker(HealthChecker):
    """进程健康检查器"""

    def __init__(self, required_processes: list[str], timeout: float = 3.0):
        super().__init__("required_processes", timeout)
        self.required_processes = required_processes

    async def _perform_check(self) -> dict[str, Any]:
        """检查必需进程"""
        try:
            import psutil

            running_processes = []
            for proc in psutil.process_iter(
                ["pid", "name", "status", "cpu_percent", "memory_percent"]
            ):
                try:
                    running_processes.append(proc.info["name"])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            process_status = {}
            missing_processes = []

            for required_proc in self.required_processes:
                is_running = any(
                    required_proc in proc_name for proc_name in running_processes
                )
                process_status[required_proc] = {
                    "running": is_running,
                    "status": "运行中" if is_running else "未运行",
                }

                if not is_running:
                    missing_processes.append(required_proc)

            # 确定健康状态
            if not missing_processes:
                status = HealthStatus.HEALTHY
                message = f"所有必需进程正常运行 ({len(self.required_processes)}个)"
            elif len(missing_processes) <= len(self.required_processes) // 2:
                status = HealthStatus.DEGRADED
                message = f"部分必需进程未运行: {', '.join(missing_processes)}"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"多个必需进程未运行: {', '.join(missing_processes)}"

            return {
                "status": status,
                "message": message,
                "details": {
                    "processes": process_status,
                    "missing_count": len(missing_processes),
                    "total_required": len(self.required_processes),
                },
            }

        except ImportError:
            return {
                "status": HealthStatus.DEGRADED,
                "message": "psutil库未安装，无法检查进程",
                "details": {"psutil_available": False},
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"进程检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class MemoryLeakHealthChecker(HealthChecker):
    """内存泄漏检查器"""

    def __init__(self, threshold_mb: float = 1000.0, timeout: float = 2.0):
        super().__init__("memory_leak", timeout)
        self.threshold_mb = threshold_mb
        self.memory_history = []
        self.max_history = 10

    async def _perform_check(self) -> dict[str, Any]:
        """检查内存泄漏"""
        try:
            import os

            import psutil

            # 获取当前进程内存使用
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            current_memory_mb = memory_info.rss / (1024 * 1024)

            # 记录内存历史
            self.memory_history.append(
                {"timestamp": time.time(), "memory_mb": current_memory_mb}
            )

            # 保持历史记录大小
            if len(self.memory_history) > self.max_history:
                self.memory_history = self.memory_history[-self.max_history :]

            # 分析内存趋势
            memory_trend = "stable"
            growth_rate = 0.0

            if len(self.memory_history) >= 3:
                recent_memories = [h["memory_mb"] for h in self.memory_history[-3:]]
                if all(
                    recent_memories[i] < recent_memories[i + 1]
                    for i in range(len(recent_memories) - 1)
                ):
                    memory_trend = "increasing"
                    growth_rate = (recent_memories[-1] - recent_memories[0]) / len(
                        recent_memories
                    )
                elif all(
                    recent_memories[i] > recent_memories[i + 1]
                    for i in range(len(recent_memories) - 1)
                ):
                    memory_trend = "decreasing"

            # 确定健康状态
            if current_memory_mb > self.threshold_mb:
                status = HealthStatus.UNHEALTHY
                message = f"内存使用过高: {current_memory_mb:.1f}MB (阈值: {self.threshold_mb}MB)"
            elif (
                memory_trend == "increasing" and growth_rate > 50
            ):  # 每次检查增长超过50MB
                status = HealthStatus.DEGRADED
                message = f"检测到内存增长趋势: {growth_rate:.1f}MB/检查"
            else:
                status = HealthStatus.HEALTHY
                message = f"内存使用正常: {current_memory_mb:.1f}MB"

            return {
                "status": status,
                "message": message,
                "details": {
                    "current_memory_mb": round(current_memory_mb, 1),
                    "threshold_mb": self.threshold_mb,
                    "memory_trend": memory_trend,
                    "growth_rate_mb": round(growth_rate, 1),
                    "history_points": len(self.memory_history),
                },
            }

        except Exception as e:
            return {
                "status": HealthStatus.UNHEALTHY,
                "message": f"内存泄漏检查失败: {str(e)}",
                "details": {"error": str(e)},
            }


class AlertManager:
    """告警管理器"""

    def __init__(self) -> None:
        self.alert_rules: list[AlertRule] = []
        self.active_alerts: list[Alert] = []
        self.alert_history: list[Alert] = []
        self.max_history = 1000
        self.notification_handlers: list[Callable] = []

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules.append(rule)
        logger.info(f"添加告警规则: {rule.name}")

    def add_notification_handler(self, handler: Callable):
        """添加通知处理器"""
        self.notification_handlers.append(handler)

    async def evaluate_alerts(self, health_results: list[HealthCheckResult]):
        """评估告警条件"""
        current_time = time.time()

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            # 检查冷却时间
            if current_time - rule.last_triggered < rule.cooldown_seconds:
                continue

            # 评估告警条件
            should_alert = self._evaluate_condition(rule.condition, health_results)

            if should_alert:
                # 创建告警
                alert = Alert(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=self._format_alert_message(
                        rule.message_template, health_results
                    ),
                    health_check_result=self._get_relevant_health_result(
                        rule.condition, health_results
                    ),
                )

                # 记录告警
                self.active_alerts.append(alert)
                self.alert_history.append(alert)
                rule.last_triggered = current_time

                # 发送通知
                await self._send_notifications(alert)

                logger.warning(f"触发告警: {alert.rule_name} - {alert.message}")

    def _evaluate_condition(
        self, condition: str, health_results: list[HealthCheckResult]
    ) -> bool:
        """评估告警条件"""
        try:
            # 创建评估上下文
            context = {
                "results": {result.name: result for result in health_results},
                "any_unhealthy": any(
                    r.status == HealthStatus.UNHEALTHY for r in health_results
                ),
                "any_degraded": any(
                    r.status == HealthStatus.DEGRADED for r in health_results
                ),
                "unhealthy_count": sum(
                    1 for r in health_results if r.status == HealthStatus.UNHEALTHY
                ),
                "degraded_count": sum(
                    1 for r in health_results if r.status == HealthStatus.DEGRADED
                ),
                "total_checks": len(health_results),
            }

            # 安全的条件评估
            return eval(condition, {"__builtins__": {}}, context)

        except Exception as e:
            logger.error(f"告警条件评估失败: {condition} - {e}")
            return False

    def _format_alert_message(
        self, template: str, health_results: list[HealthCheckResult]
    ) -> str:
        """格式化告警消息"""
        try:
            context = {
                "unhealthy_checks": [
                    r.name for r in health_results if r.status == HealthStatus.UNHEALTHY
                ],
                "degraded_checks": [
                    r.name for r in health_results if r.status == HealthStatus.DEGRADED
                ],
                "unhealthy_count": sum(
                    1 for r in health_results if r.status == HealthStatus.UNHEALTHY
                ),
                "degraded_count": sum(
                    1 for r in health_results if r.status == HealthStatus.DEGRADED
                ),
                "total_checks": len(health_results),
            }

            return template.format(**context)

        except Exception as e:
            logger.error(f"告警消息格式化失败: {e}")
            return template

    def _get_relevant_health_result(
        self, condition: str, health_results: list[HealthCheckResult]
    ) -> HealthCheckResult | None:
        """获取相关的健康检查结果"""
        # 简单实现：返回第一个不健康的结果
        for result in health_results:
            if result.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                return result
        return None

    async def _send_notifications(self, alert: Alert):
        """发送通知"""
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"通知发送失败: {e}")

    def resolve_alert(self, rule_name: str):
        """解决告警"""
        current_time = time.time()
        for alert in self.active_alerts:
            if alert.rule_name == rule_name and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = current_time
                logger.info(f"告警已解决: {rule_name}")

        # 移除已解决的告警
        self.active_alerts = [a for a in self.active_alerts if not a.resolved]

    def get_active_alerts(self) -> list[Alert]:
        """获取活跃告警"""
        return self.active_alerts.copy()

    def get_alert_summary(self) -> dict[str, Any]:
        """获取告警摘要"""
        return {
            "active_alerts": len(self.active_alerts),
            "total_rules": len(self.alert_rules),
            "enabled_rules": sum(1 for r in self.alert_rules if r.enabled),
            "alert_history_count": len(self.alert_history),
            "alerts_by_severity": {
                severity.value: sum(
                    1 for a in self.active_alerts if a.severity == severity
                )
                for severity in AlertSeverity
            },
        }


# 通知处理器
async def console_notification_handler(alert: Alert):
    """控制台通知处理器"""
    severity_icons = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.CRITICAL: "🚨",
        AlertSeverity.EMERGENCY: "🆘",
    }

    icon = severity_icons.get(alert.severity, "📢")
    print(f"{icon} [{alert.severity.value.upper()}] {alert.message}")


async def log_notification_handler(alert: Alert):
    """日志通知处理器"""
    log_levels = {
        AlertSeverity.INFO: logging.INFO,
        AlertSeverity.WARNING: logging.WARNING,
        AlertSeverity.CRITICAL: logging.ERROR,
        AlertSeverity.EMERGENCY: logging.CRITICAL,
    }

    level = log_levels.get(alert.severity, logging.WARNING)
    logger.log(level, f"ALERT [{alert.rule_name}]: {alert.message}")


# 全局告警管理器
global_alert_manager = AlertManager()


def setup_default_alert_rules() -> None:
    """设置默认告警规则"""
    rules = [
        AlertRule(
            name="system_unhealthy",
            condition="any_unhealthy",
            severity=AlertSeverity.CRITICAL,
            message_template="系统检测到 {unhealthy_count} 个严重问题: {unhealthy_checks}",
            cooldown_seconds=300,
        ),
        AlertRule(
            name="multiple_degraded",
            condition="degraded_count >= 2",
            severity=AlertSeverity.WARNING,
            message_template="系统检测到 {degraded_count} 个性能问题: {degraded_checks}",
            cooldown_seconds=600,
        ),
        AlertRule(
            name="high_failure_rate",
            condition="(unhealthy_count + degraded_count) / total_checks > 0.5",
            severity=AlertSeverity.CRITICAL,
            message_template="系统健康检查失败率过高: {unhealthy_count}个严重 + {degraded_count}个警告 / {total_checks}个检查",
            cooldown_seconds=300,
        ),
    ]

    for rule in rules:
        global_alert_manager.add_alert_rule(rule)

    # 添加默认通知处理器
    global_alert_manager.add_notification_handler(console_notification_handler)
    global_alert_manager.add_notification_handler(log_notification_handler)

    logger.info("默认告警规则已设置")


def setup_advanced_health_checks() -> None:
    """设置高级健康检查"""
    # 网络连接检查
    network_endpoints = [
        "https://www.baidu.com",
        "https://www.google.com",
        "http://httpbin.org/status/200",
    ]
    global_health_manager.add_checker(NetworkHealthChecker(network_endpoints))

    # 磁盘空间检查
    global_health_manager.add_checker(DiskSpaceHealthChecker())

    # 内存泄漏检查
    global_health_manager.add_checker(MemoryLeakHealthChecker())

    # 必需进程检查（示例）
    required_processes = ["python", "python3"]  # 根据实际需要调整
    global_health_manager.add_checker(ProcessHealthChecker(required_processes))

    logger.info("高级健康检查已设置")


async def run_health_check_with_alerts() -> None:
    """运行健康检查并评估告警"""
    # 执行健康检查
    health = await global_health_manager.check_health()

    # 评估告警
    await global_alert_manager.evaluate_alerts(health.checks)

    return health
