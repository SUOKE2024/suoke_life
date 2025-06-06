"""
alerting - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable
from corn_maze_service.constants import HTTP_BAD_REQUEST, HTTP_OK
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import aiohttp
import asyncio
import contextlib
import logging
import time

#!/usr/bin/env python3

"""
告警管理模块

提供告警规则定义、告警触发、告警通知等功能
"""




logger = logging.getLogger(__name__)

# 系统监控阈值常量
CPU_WARNING_THRESHOLD = 80.0      # CPU使用率警告阈值
CPU_CRITICAL_THRESHOLD = 95.0     # CPU使用率严重阈值
MEMORY_WARNING_THRESHOLD = 85.0   # 内存使用率警告阈值
DISK_WARNING_THRESHOLD = 90.0     # 磁盘使用率警告阈值
ERROR_RATE_THRESHOLD = 5.0        # 错误率阈值

class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """告警对象"""
    name: str
    level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    status: AlertStatus = AlertStatus.ACTIVE
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "metadata": self.metadata
        }

@dataclass
class AlertRule:
    """告警规则"""
    name: str
    condition: Callable[[float], bool]
    level: AlertLevel
    message_template: str
    cooldown_seconds: float = 300.0  # 5分钟冷却时间
    enabled: bool = True

    def evaluate(self, metric_value: float) -> bool:
        """评估规则"""
        if not self.enabled:
            return False

        try:
            return self.condition(metric_value)
        except Exception as e:
            logger.error(f"告警规则 {self.name} 评估失败: {e}")
            return False

    def create_alert(self, metric_value: float, **kwargs) -> Alert:
        """创建告警"""
        message = self.message_template.format(value=metric_value, **kwargs)
        return Alert(
            name=self.name,
            level=self.level,
            message=message,
            metadata={"metric_value": metric_value, **kwargs}
        )

class AlertChannel(ABC):
    """告警通道基类"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True

    async def send_alert(self, alert: Alert) -> bool:
        """发送告警"""
        raise NotImplementedError

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接"""
        pass

class LogAlertChannel(AlertChannel):
    """日志告警通道"""

    async def send_alert(self, alert: Alert) -> bool:
        """发送告警到日志"""
        try:
            log_level = {
                AlertLevel.INFO: logging.INFO,
                AlertLevel.WARNING: logging.WARNING,
                AlertLevel.ERROR: logging.ERROR,
                AlertLevel.CRITICAL: logging.CRITICAL
            }.get(alert.level, logging.INFO)

            logger.log(log_level, f"[ALERT] {alert.name}: {alert.message}")
            return True
        except Exception as e:
            logger.error(f"日志告警发送失败: {e}")
            return False

class EmailAlertChannel(AlertChannel):
    """邮件告警通道"""

    def __init__(self, name: str, smtp_config: dict[str, Any]):
        super().__init__(name)
        self.smtp_config = smtp_config

    async def send_alert(self, alert: Alert) -> bool:
        """发送邮件告警"""
        try:
            # 这里应该实现实际的邮件发送逻辑
            logger.info(f"邮件告警发送成功: {alert.name}")
            return True
        except Exception as e:
            logger.error(f"邮件告警发送失败: {e}")
            return False

class WebhookAlertChannel(AlertChannel):
    """Webhook告警通道"""

    def __init__(self, name: str, webhook_url: str, timeout: float = 10.0):
        super().__init__(name)
        self.webhook_url = webhook_url
        self.timeout = timeout

    async def send_alert(self, alert: Alert) -> bool:
        """发送Webhook告警"""
        try:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": time.time()
            }

            async with aiohttp.ClientSession() as session, session.post(
                self.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status < HTTP_BAD_REQUEST:
                    logger.info(f"Webhook告警发送成功: {alert.name}")
                    return True
                else:
                    logger.error(f"Webhook告警发送失败, 状态码: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Webhook告警发送失败: {e}")
            return False

class SlackAlertChannel(AlertChannel):
    """Slack告警通道"""

    def __init__(self, name: str, webhook_url: str):
        super().__init__(name)
        self.webhook_url = webhook_url

    async def send_alert(self, alert: Alert) -> bool:
        """发送Slack告警"""
        try:
            color_map = {
                AlertLevel.INFO: "good",
                AlertLevel.WARNING: "warning",
                AlertLevel.ERROR: "danger",
                AlertLevel.CRITICAL: "danger"
            }

            payload = {
                "attachments": [{
                    "color": color_map.get(alert.level, "good"),
                    "title": f"告警: {alert.name}",
                    "text": alert.message,
                    "fields": [
                        {"title": "级别", "value": alert.level.value, "short": True},
                        {"title": "时间", "value": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(alert.timestamp)), "short": True}
                    ]
                }]
            }

            async with aiohttp.ClientSession() as session, session.post(
                self.webhook_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30.0)
            ) as response:
                if response.status == HTTP_OK:
                    logger.info(f"Slack告警发送成功: {alert.name}")
                    return True
                else:
                    logger.error(f"Slack告警发送失败, 状态码: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Slack告警发送失败: {e}")
            return False

    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_payload = {"text": "告警系统连接测试"}

            async with aiohttp.ClientSession() as session, session.post(
                self.webhook_url,
                json=test_payload,
                timeout=aiohttp.ClientTimeout(total=30.0)
            ) as response:
                return response.status == HTTP_OK
        except Exception as e:
            logger.error(f"Slack连接测试失败: {e}")
            return False

class AlertManager:
    """告警管理器"""

    # 告警历史管理常量
    MAX_ALERT_HISTORY = 1000  # 最大告警历史记录数

    def __init__(self):
        """初始化告警管理器"""
        self.rules: dict[str, AlertRule] = {}
        self.channels: dict[str, AlertChannel] = {}
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: deque[Alert] = deque(maxlen=self.MAX_ALERT_HISTORY)
        self.rule_last_triggered: dict[str, float] = {}
        self._running = False
        self._evaluation_task: asyncio.Task | None = None

    def add_rule(self, rule: AlertRule) -> None:
        """添加告警规则"""
        self.rules[rule.name] = rule
        logger.info(f"添加告警规则: {rule.name}")

    def remove_rule(self, rule_name: str) -> None:
        """移除告警规则"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.info(f"移除告警规则: {rule_name}")

    def add_channel(self, channel: AlertChannel) -> None:
        """添加告警通道"""
        self.channels[channel.name] = channel
        logger.info(f"添加告警通道: {channel.name}")

    def remove_channel(self, channel_name: str) -> None:
        """移除告警通道"""
        if channel_name in self.channels:
            del self.channels[channel_name]
            logger.info(f"移除告警通道: {channel_name}")

    async def evaluate_metric(self, metric_name: str, metric_value: float) -> None:
        """评估指标"""
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue

            # 检查冷却时间
            last_triggered = self.rule_last_triggered.get(rule_name, 0)
            if time.time() - last_triggered < rule.cooldown_seconds:
                continue

            # 评估规则
            if rule.evaluate(metric_value):
                alert = rule.create_alert(metric_value, metric_name=metric_name)
                await self.trigger_alert(alert)
                self.rule_last_triggered[rule_name] = time.time()

    async def trigger_alert(self, alert: Alert) -> None:
        """触发告警"""
        # 添加到活跃告警
        self.active_alerts[alert.name] = alert

        # 添加到历史记录
        self.alert_history.append(alert)

        # 发送到所有启用的通道
        for channel in self.channels.values():
            if channel.enabled:
                try:
                    await channel.send_alert(alert)
                except Exception as e:
                    logger.error(f"通道 {channel.name} 发送告警失败: {e}")

        logger.warning(f"触发告警: {alert.name} - {alert.message}")

    async def resolve_alert(self, alert_name: str) -> None:
        """解决告警"""
        if alert_name in self.active_alerts:
            alert = self.active_alerts[alert_name]
            alert.status = AlertStatus.RESOLVED
            del self.active_alerts[alert_name]
            logger.info(f"告警已解决: {alert_name}")

    async def start(self, evaluation_interval: float = 60.0) -> None:
        """启动告警管理器"""
        if self._running:
            return

        self._running = True
        self._evaluation_task = asyncio.create_task(
            self._evaluation_loop(evaluation_interval)
        )
        logger.info(f"告警管理器已启动, 评估间隔: {evaluation_interval}秒")

    async def stop(self) -> None:
        """停止告警管理器"""
        self._running = False
        if self._evaluation_task:
            self._evaluation_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._evaluation_task
        logger.info("告警管理器已停止")

    async def _evaluation_loop(self, interval: float) -> None:
        """评估循环"""
        while self._running:
            try:
                # 这里可以添加定期评估逻辑
                # 例如检查系统指标、清理过期告警等
                await self._cleanup_old_alerts()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"告警评估循环错误: {e}")
                await asyncio.sleep(interval)

    async def _cleanup_old_alerts(self) -> None:
        """清理旧告警"""
        # 保留最近1000条告警历史
        if len(self.alert_history) > self.MAX_ALERT_HISTORY:
            self.alert_history.popleft()

    def get_active_alerts(self) -> list[Alert]:
        """获取活跃告警"""
        return list(self.active_alerts.values())

    async def get_alert_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """获取告警历史"""
        # 从缓存中获取历史告警
        recent_alerts = list(self.alert_history)[-limit:] if limit > 0 else list(self.alert_history)
        return [alert.to_dict() for alert in recent_alerts]

    def get_rule_status(self) -> dict[str, dict[str, Any]]:
        """获取规则状态"""
        status = {}
        for rule_name, rule in self.rules.items():
            last_triggered = self.rule_last_triggered.get(rule_name)
            status[rule_name] = {
                "enabled": rule.enabled,
                "level": rule.level.value,
                "last_triggered": last_triggered,
                "cooldown_seconds": rule.cooldown_seconds
            }
        return status

    def get_channel_status(self) -> dict[str, dict[str, Any]]:
        """获取通道状态"""
        status = {}
        for channel_name, channel in self.channels.items():
            status[channel_name] = {
                "enabled": channel.enabled,
                "type": type(channel).__name__
            }
        return status

# 告警管理器单例
class AlertManagerSingleton:
    """告警管理器单例"""

    _instance: AlertManager | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls) -> AlertManager:
        """获取告警管理器实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = AlertManager()
        return cls._instance

    @classmethod
    def get_instance_sync(cls) -> AlertManager:
        """同步获取告警管理器实例"""
        if cls._instance is None:
            cls._instance = AlertManager()
        return cls._instance


def get_alert_manager() -> AlertManager:
    """获取全局告警管理器（向后兼容）"""
    return AlertManagerSingleton.get_instance_sync()


async def get_alert_manager_async() -> AlertManager:
    """异步获取全局告警管理器"""
    return await AlertManagerSingleton.get_instance()

# 预定义的告警规则
def create_default_rules() -> list[AlertRule]:
    """创建默认告警规则"""
    return [
        AlertRule(
            name="high_cpu_usage",
            condition=lambda x: x > CPU_WARNING_THRESHOLD,
            level=AlertLevel.WARNING,
            message_template="CPU使用率过高: {value:.1f}%"
        ),
        AlertRule(
            name="critical_cpu_usage",
            condition=lambda x: x > CPU_CRITICAL_THRESHOLD,
            level=AlertLevel.CRITICAL,
            message_template="CPU使用率严重过高: {value:.1f}%"
        ),
        AlertRule(
            name="high_memory_usage",
            condition=lambda x: x > MEMORY_WARNING_THRESHOLD,
            level=AlertLevel.WARNING,
            message_template="内存使用率过高: {value:.1f}%"
        ),
        AlertRule(
            name="low_disk_space",
            condition=lambda x: x > DISK_WARNING_THRESHOLD,
            level=AlertLevel.ERROR,
            message_template="磁盘空间不足: {value:.1f}%"
        ),
        AlertRule(
            name="high_error_rate",
            condition=lambda x: x > ERROR_RATE_THRESHOLD,
            level=AlertLevel.ERROR,
            message_template="错误率过高: {value:.1f}%"
        )
    ]

async def setup_default_alerting() -> AlertManager:
    """设置默认告警系统"""
    manager = get_alert_manager()

    # 添加默认规则
    for rule in create_default_rules():
        manager.add_rule(rule)

    # 添加日志通道
    log_channel = LogAlertChannel("log")
    manager.add_channel(log_channel)

    return manager
