#!/usr/bin/env python3
"""
索克生活无障碍服务 - 增强通知系统

支持多种通知渠道：邮件、短信、钉钉、企业微信、Slack等
"""

import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import aiohttp

logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """通知级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ChannelType(Enum):
    """通知渠道类型"""

    EMAIL = "email"
    SMS = "sms"
    DINGTALK = "dingtalk"
    WECHAT_WORK = "wechat_work"
    SLACK = "slack"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class NotificationMessage:
    """通知消息"""

    title: str
    content: str
    level: NotificationLevel
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }


class NotificationChannel(ABC):
    """通知渠道抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.name = config.get("name", self.__class__.__name__)

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """发送通知"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """验证配置"""
        pass


class EmailChannel(NotificationChannel):
    """邮件通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email")
        self.to_emails = config.get("to_emails", [])
        self.use_tls = config.get("use_tls", True)

    def validate_config(self) -> bool:
        """验证邮件配置"""
        required_fields = [
            "smtp_server",
            "username",
            "password",
            "from_email",
            "to_emails",
        ]
        return all(self.config.get(field) for field in required_fields)

    async def send(self, message: NotificationMessage) -> bool:
        """发送邮件通知"""
        if not self.enabled or not self.validate_config():
            return False

        try:
            # 创建邮件消息
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = ", ".join(self.to_emails)
            msg["Subject"] = f"[{message.level.value.upper()}] {message.title}"

            # 邮件内容
            body = f"""
时间: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
级别: {message.level.value.upper()}
标题: {message.title}

内容:
{message.content}

---
索克生活无障碍服务监控系统
            """.strip()

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"邮件通知发送成功: {message.title}")
            return True

        except Exception as e:
            logger.error(f"邮件通知发送失败: {e}")
            return False


class DingTalkChannel(NotificationChannel):
    """钉钉通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.secret = config.get("secret")
        self.at_mobiles = config.get("at_mobiles", [])
        self.at_all = config.get("at_all", False)

    def validate_config(self) -> bool:
        """验证钉钉配置"""
        return bool(self.webhook_url)

    async def send(self, message: NotificationMessage) -> bool:
        """发送钉钉通知"""
        if not self.enabled or not self.validate_config():
            return False

        try:
            # 构建钉钉消息
            level_emoji = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = level_emoji.get(message.level, "📢")

            content = f"{emoji} **{message.title}**\n\n"
            content += f"**时间:** {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**级别:** {message.level.value.upper()}\n\n"
            content += f"**详情:**\n{message.content}\n\n"
            content += "---\n索克生活无障碍服务监控"

            payload = {
                "msgtype": "markdown",
                "markdown": {"title": message.title, "text": content},
            }

            # 添加@功能
            if self.at_mobiles or self.at_all:
                payload["at"] = {"atMobiles": self.at_mobiles, "isAtAll": self.at_all}

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            logger.info(f"钉钉通知发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"钉钉通知发送失败: {result}")
                            return False
                    else:
                        logger.error(f"钉钉通知请求失败: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"钉钉通知发送失败: {e}")
            return False


class WeChatWorkChannel(NotificationChannel):
    """企业微信通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.mentioned_list = config.get("mentioned_list", [])
        self.mentioned_mobile_list = config.get("mentioned_mobile_list", [])

    def validate_config(self) -> bool:
        """验证企业微信配置"""
        return bool(self.webhook_url)

    async def send(self, message: NotificationMessage) -> bool:
        """发送企业微信通知"""
        if not self.enabled or not self.validate_config():
            return False

        try:
            # 构建企业微信消息
            level_colors = {
                NotificationLevel.INFO: "info",
                NotificationLevel.WARNING: "warning",
                NotificationLevel.ERROR: "warning",
                NotificationLevel.CRITICAL: "warning",
            }

            color = level_colors.get(message.level, "info")

            content = f"**{message.title}**\n"
            content += f"时间: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += (
                f'级别: <font color="{color}">{message.level.value.upper()}</font>\n\n'
            )
            content += f"{message.content}\n\n"
            content += "---\n索克生活无障碍服务监控"

            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content,
                    "mentioned_list": self.mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list,
                },
            }

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            logger.info(f"企业微信通知发送成功: {message.title}")
                            return True
                        else:
                            logger.error(f"企业微信通知发送失败: {result}")
                            return False
                    else:
                        logger.error(f"企业微信通知请求失败: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"企业微信通知发送失败: {e}")
            return False


class SlackChannel(NotificationChannel):
    """Slack通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url")
        self.channel = config.get("channel")
        self.username = config.get("username", "索克生活监控")

    def validate_config(self) -> bool:
        """验证Slack配置"""
        return bool(self.webhook_url)

    async def send(self, message: NotificationMessage) -> bool:
        """发送Slack通知"""
        if not self.enabled or not self.validate_config():
            return False

        try:
            # 构建Slack消息
            level_colors = {
                NotificationLevel.INFO: "good",
                NotificationLevel.WARNING: "warning",
                NotificationLevel.ERROR: "danger",
                NotificationLevel.CRITICAL: "danger",
            }

            color = level_colors.get(message.level, "good")

            payload = {
                "username": self.username,
                "attachments": [
                    {
                        "color": color,
                        "title": message.title,
                        "text": message.content,
                        "fields": [
                            {
                                "title": "时间",
                                "value": message.timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "short": True,
                            },
                            {
                                "title": "级别",
                                "value": message.level.value.upper(),
                                "short": True,
                            },
                        ],
                        "footer": "索克生活无障碍服务监控",
                        "ts": int(message.timestamp.timestamp()),
                    }
                ],
            }

            if self.channel:
                payload["channel"] = self.channel

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack通知发送成功: {message.title}")
                        return True
                    else:
                        logger.error(f"Slack通知请求失败: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Slack通知发送失败: {e}")
            return False


class WebhookChannel(NotificationChannel):
    """自定义Webhook通知渠道"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.url = config.get("url")
        self.method = config.get("method", "POST")
        self.headers = config.get("headers", {})
        self.timeout = config.get("timeout", 10)

    def validate_config(self) -> bool:
        """验证Webhook配置"""
        return bool(self.url)

    async def send(self, message: NotificationMessage) -> bool:
        """发送Webhook通知"""
        if not self.enabled or not self.validate_config():
            return False

        try:
            payload = message.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    self.method,
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    if 200 <= response.status < 300:
                        logger.info(f"Webhook通知发送成功: {message.title}")
                        return True
                    else:
                        logger.error(f"Webhook通知请求失败: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Webhook通知发送失败: {e}")
            return False


class ConsoleChannel(NotificationChannel):
    """控制台通知渠道"""

    def validate_config(self) -> bool:
        """验证控制台配置"""
        return True

    async def send(self, message: NotificationMessage) -> bool:
        """发送控制台通知"""
        if not self.enabled:
            return False

        try:
            level_symbols = {
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            symbol = level_symbols.get(message.level, "📢")

            print(f"\n{symbol} [{message.level.value.upper()}] {message.title}")
            print(f"时间: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"内容: {message.content}")
            print("-" * 50)

            return True

        except Exception as e:
            logger.error(f"控制台通知发送失败: {e}")
            return False


class EnhancedNotificationManager:
    """增强通知管理器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化通知管理器

        Args:
            config: 通知配置
        """
        self.config = config
        self.channels: Dict[str, NotificationChannel] = {}
        self.channel_factories = {
            ChannelType.EMAIL: EmailChannel,
            ChannelType.DINGTALK: DingTalkChannel,
            ChannelType.WECHAT_WORK: WeChatWorkChannel,
            ChannelType.SLACK: SlackChannel,
            ChannelType.WEBHOOK: WebhookChannel,
            ChannelType.CONSOLE: ConsoleChannel,
        }

        # 统计信息
        self.sent_count = 0
        self.failed_count = 0
        self.channel_stats: Dict[str, Dict[str, int]] = {}

        self._setup_channels()

        logger.info("增强通知管理器初始化完成")

    def _setup_channels(self):
        """设置通知渠道"""
        channels_config = self.config.get("channels", {})

        for channel_name, channel_config in channels_config.items():
            try:
                channel_type = ChannelType(channel_config.get("type"))
                channel_class = self.channel_factories.get(channel_type)

                if channel_class:
                    channel = channel_class(channel_config)
                    if channel.validate_config():
                        self.channels[channel_name] = channel
                        self.channel_stats[channel_name] = {"sent": 0, "failed": 0}
                        logger.info(
                            f"通知渠道已设置: {channel_name} ({channel_type.value})"
                        )
                    else:
                        logger.warning(f"通知渠道配置无效: {channel_name}")
                else:
                    logger.warning(f"不支持的通知渠道类型: {channel_type}")

            except Exception as e:
                logger.error(f"设置通知渠道失败 {channel_name}: {e}")

    async def send_notification(
        self,
        title: str,
        content: str,
        level: NotificationLevel = NotificationLevel.INFO,
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, bool]:
        """
        发送通知

        Args:
            title: 通知标题
            content: 通知内容
            level: 通知级别
            channels: 指定的通知渠道列表，None表示所有渠道
            metadata: 附加元数据

        Returns:
            各渠道发送结果
        """
        message = NotificationMessage(
            title=title,
            content=content,
            level=level,
            timestamp=datetime.now(),
            metadata=metadata,
        )

        # 确定要发送的渠道
        target_channels = channels or list(self.channels.keys())
        results = {}

        # 并发发送到所有渠道
        tasks = []
        for channel_name in target_channels:
            if channel_name in self.channels:
                task = self._send_to_channel(channel_name, message)
                tasks.append((channel_name, task))

        # 等待所有发送完成
        for channel_name, task in tasks:
            try:
                success = await task
                results[channel_name] = success

                # 更新统计
                if success:
                    self.sent_count += 1
                    self.channel_stats[channel_name]["sent"] += 1
                else:
                    self.failed_count += 1
                    self.channel_stats[channel_name]["failed"] += 1

            except Exception as e:
                logger.error(f"通知发送异常 {channel_name}: {e}")
                results[channel_name] = False
                self.failed_count += 1
                self.channel_stats[channel_name]["failed"] += 1

        logger.info(f"通知发送完成: {title} -> {results}")
        return results

    async def _send_to_channel(
        self, channel_name: str, message: NotificationMessage
    ) -> bool:
        """发送到指定渠道"""
        channel = self.channels.get(channel_name)
        if not channel:
            logger.warning(f"通知渠道不存在: {channel_name}")
            return False

        return await channel.send(message)

    async def send_health_alert(self, health_result):
        """发送健康检查告警"""
        if not health_result.overall_healthy:
            failed_checks = [c for c in health_result.checks if not c.healthy]

            title = f"健康检查失败 ({len(failed_checks)}个检查项)"
            content = "以下健康检查项失败:\n\n"

            for check in failed_checks:
                content += f"• {check.name}: {check.message}\n"

            content += f"\n总检查时间: {health_result.total_duration:.2f}秒"

            await self.send_notification(
                title=title,
                content=content,
                level=NotificationLevel.ERROR,
                metadata={"type": "health_check", "failed_count": len(failed_checks)},
            )

    async def send_performance_alert(
        self, metric_name: str, current_value: float, threshold: float
    ):
        """发送性能告警"""
        title = f"性能指标异常: {metric_name}"
        content = (
            f"指标 {metric_name} 当前值 {current_value:.2f} 超过阈值 {threshold:.2f}"
        )

        level = NotificationLevel.WARNING
        if current_value > threshold * 1.5:
            level = NotificationLevel.ERROR
        if current_value > threshold * 2:
            level = NotificationLevel.CRITICAL

        await self.send_notification(
            title=title,
            content=content,
            level=level,
            metadata={
                "type": "performance",
                "metric": metric_name,
                "value": current_value,
                "threshold": threshold,
            },
        )

    def get_statistics(self) -> Dict[str, Any]:
        """获取通知统计信息"""
        return {
            "total_sent": self.sent_count,
            "total_failed": self.failed_count,
            "success_rate": (
                self.sent_count / (self.sent_count + self.failed_count) * 100
                if (self.sent_count + self.failed_count) > 0
                else 0
            ),
            "channels": self.channel_stats,
            "active_channels": len(self.channels),
        }

    def get_channel_status(self) -> Dict[str, Dict[str, Any]]:
        """获取渠道状态"""
        status = {}
        for name, channel in self.channels.items():
            status[name] = {
                "enabled": channel.enabled,
                "type": channel.__class__.__name__,
                "config_valid": channel.validate_config(),
                "stats": self.channel_stats.get(name, {"sent": 0, "failed": 0}),
            }
        return status


# 全局通知管理器实例
notification_manager = None


def get_notification_manager(
    config: Dict[str, Any] = None,
) -> EnhancedNotificationManager:
    """获取通知管理器实例"""
    global notification_manager
    if notification_manager is None:
        notification_manager = EnhancedNotificationManager(config or {})
    return notification_manager


# 示例配置
EXAMPLE_CONFIG = {
    "channels": {
        "console": {"type": "console", "enabled": True},
        "email": {
            "type": "email",
            "enabled": True,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "from_email": "your-email@gmail.com",
            "to_emails": ["admin@company.com"],
            "use_tls": True,
        },
        "dingtalk": {
            "type": "dingtalk",
            "enabled": True,
            "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
            "secret": "YOUR_SECRET",
            "at_mobiles": [],
            "at_all": False,
        },
        "wechat_work": {
            "type": "wechat_work",
            "enabled": True,
            "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",
            "mentioned_list": [],
            "mentioned_mobile_list": [],
        },
        "slack": {
            "type": "slack",
            "enabled": False,
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "channel": "#monitoring",
            "username": "索克生活监控",
        },
    }
}
