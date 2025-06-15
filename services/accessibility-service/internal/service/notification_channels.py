"""
多通道告警通知系统
支持邮件、短信、钉钉、企业微信、Slack等多种通知渠道
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
import smtplib
import ssl
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any

import aiohttp


class NotificationLevel(Enum):
    """通知级别"""

    DEBUG = "debug"
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
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)
    attachments: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "title": self.title,
            "content": self.content,
            "level": self.level.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "attachments": self.attachments,
        }


@dataclass
class ChannelConfig:
    """通知渠道配置"""

    channel_type: ChannelType
    enabled: bool = True
    config: dict[str, Any] = field(default_factory=dict)
    rate_limit: int | None = None  # 每分钟最大发送数
    retry_count: int = 3
    timeout: int = 30


class NotificationChannel(ABC):
    """通知渠道抽象基类"""

    def __init__(self, config: ChannelConfig):
        self.config = config
        self.sent_count = 0
        self.last_reset_time = time.time()
        self.logger = logging.getLogger(f"notification.{config.channel_type.value}")

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """发送通知"""
        pass

    def can_send(self) -> bool:
        """检查是否可以发送（速率限制）"""
        if not self.config.enabled:
            return False

        if self.config.rate_limit is None:
            return True

        current_time = time.time()
        if current_time - self.last_reset_time >= 60:  # 重置计数器
            self.sent_count = 0
            self.last_reset_time = current_time

        return self.sent_count < self.config.rate_limit

    def record_sent(self) -> None:
        """记录发送"""
        self.sent_count += 1


class EmailChannel(NotificationChannel):
    """邮件通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送邮件通知"""
        if not self.can_send():
            return False

        try:
            config = self.config.config
            smtp_server = config.get("smtp_server", "smtp.gmail.com")
            smtp_port = config.get("smtp_port", 587)
            username = config.get("username")
            # 安全修复: 使用环境变量存储敏感信息
            password = os.getenv("SMTP_PASSWORD") or config.get("password")
            if not password and config.get("password"):
                self.logger.warning("建议使用环境变量 SMTP_PASSWORD 存储邮件密码")
            from_email = config.get("from_email", username)
            to_emails = config.get("to_emails", [])

            if not all([username, password, to_emails]):
                self.logger.error("邮件配置不完整")
                return False

            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = f"[{message.level.value.upper()}] {message.title}"

            # 邮件内容
            body = f"""
时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp))}
级别: {message.level.value.upper()}
标题: {message.title}

内容:
{message.content}

标签: {json.dumps(message.tags, ensure_ascii=False, indent=2)}
            """

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(username, password)
                server.send_message(msg)

            self.record_sent()
            self.logger.info(f"邮件发送成功: {message.title}")
            return True

        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
            return False


class DingTalkChannel(NotificationChannel):
    """钉钉通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送钉钉通知"""
        if not self.can_send():
            return False

        try:
            config = self.config.config
            webhook_url = config.get("webhook_url")
            secret = config.get("secret")

            if not webhook_url:
                self.logger.error("钉钉webhook_url未配置")
                return False

            # 构建消息
            timestamp = str(round(time.time() * 1000))
            sign = None

            if secret:
                string_to_sign = f"{timestamp}\n{secret}"
                hmac_code = hmac.new(
                    secret.encode("utf-8"),
                    string_to_sign.encode("utf-8"),
                    digestmod=hashlib.sha256,
                ).digest()
                sign = base64.b64encode(hmac_code).decode("utf-8")

            # 钉钉消息格式
            level_emoji = {
                NotificationLevel.DEBUG: "🔍",
                NotificationLevel.INFO: "ℹ️",
                NotificationLevel.WARNING: "⚠️",
                NotificationLevel.ERROR: "❌",
                NotificationLevel.CRITICAL: "🚨",
            }

            emoji = level_emoji.get(message.level, "📢")

            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"{emoji} {message.title}",
                    "text": f"""
## {emoji} {message.title}

**级别**: {message.level.value.upper()}
**时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp))}

### 详细信息
{message.content}

### 标签
{json.dumps(message.tags, ensure_ascii=False, indent=2)}
                    """,
                },
            }

            # 发送请求
            url = webhook_url
            if sign:
                url += f"&timestamp={timestamp}&sign={sign}"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            self.record_sent()
                            self.logger.info(f"钉钉消息发送成功: {message.title}")
                            return True
                        else:
                            self.logger.error(f"钉钉消息发送失败: {result}")
                            return False
                    else:
                        self.logger.error(f"钉钉请求失败: {response.status}")
                        return False

        except Exception as e:
            self.logger.error(f"钉钉通知发送失败: {e}")
            return False


class WeChatWorkChannel(NotificationChannel):
    """企业微信通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送企业微信通知"""
        if not self.can_send():
            return False

        try:
            config = self.config.config
            webhook_url = config.get("webhook_url")

            if not webhook_url:
                self.logger.error("企业微信webhook_url未配置")
                return False

            # 企业微信消息格式
            level_colors = {
                NotificationLevel.DEBUG: "info",
                NotificationLevel.INFO: "info",
                NotificationLevel.WARNING: "warning",
                NotificationLevel.ERROR: "warning",
                NotificationLevel.CRITICAL: "warning",
            }

            color = level_colors.get(message.level, "info")

            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": f"""
## <font color="{color}">{message.title}</font>

**级别**: {message.level.value.upper()}
**时间**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp))}

### 详细信息
{message.content}

### 标签
```json
{json.dumps(message.tags, ensure_ascii=False, indent=2)}
```
                    """
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("errcode") == 0:
                            self.record_sent()
                            self.logger.info(f"企业微信消息发送成功: {message.title}")
                            return True
                        else:
                            self.logger.error(f"企业微信消息发送失败: {result}")
                            return False
                    else:
                        self.logger.error(f"企业微信请求失败: {response.status}")
                        return False

        except Exception as e:
            self.logger.error(f"企业微信通知发送失败: {e}")
            return False


class SlackChannel(NotificationChannel):
    """Slack通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送Slack通知"""
        if not self.can_send():
            return False

        try:
            config = self.config.config
            webhook_url = config.get("webhook_url")
            channel = config.get("channel", "#general")
            username = config.get("username", "AlertBot")

            if not webhook_url:
                self.logger.error("Slack webhook_url未配置")
                return False

            # Slack消息格式
            level_colors = {
                NotificationLevel.DEBUG: "#36a64f",
                NotificationLevel.INFO: "#36a64f",
                NotificationLevel.WARNING: "#ff9500",
                NotificationLevel.ERROR: "#ff0000",
                NotificationLevel.CRITICAL: "#ff0000",
            }

            color = level_colors.get(message.level, "#36a64f")

            payload = {
                "channel": channel,
                "username": username,
                "attachments": [
                    {
                        "color": color,
                        "title": message.title,
                        "text": message.content,
                        "fields": [
                            {
                                "title": "级别",
                                "value": message.level.value.upper(),
                                "short": True,
                            },
                            {
                                "title": "时间",
                                "value": time.strftime(
                                    "%Y-%m-%d %H:%M:%S",
                                    time.localtime(message.timestamp),
                                ),
                                "short": True,
                            },
                        ],
                        "footer": f"标签: {json.dumps(message.tags)}",
                        "ts": int(message.timestamp),
                    }
                ],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    if response.status == 200:
                        self.record_sent()
                        self.logger.info(f"Slack消息发送成功: {message.title}")
                        return True
                    else:
                        self.logger.error(f"Slack请求失败: {response.status}")
                        return False

        except Exception as e:
            self.logger.error(f"Slack通知发送失败: {e}")
            return False


class WebhookChannel(NotificationChannel):
    """通用Webhook通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送Webhook通知"""
        if not self.can_send():
            return False

        try:
            config = self.config.config
            url = config.get("url")
            method = config.get("method", "POST").upper()
            headers = config.get("headers", {})

            if not url:
                self.logger.error("Webhook URL未配置")
                return False

            payload = message.to_dict()

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                ) as response:
                    if 200 <= response.status < 300:
                        self.record_sent()
                        self.logger.info(f"Webhook消息发送成功: {message.title}")
                        return True
                    else:
                        self.logger.error(f"Webhook请求失败: {response.status}")
                        return False

        except Exception as e:
            self.logger.error(f"Webhook通知发送失败: {e}")
            return False


class ConsoleChannel(NotificationChannel):
    """控制台通知渠道"""

    async def send(self, message: NotificationMessage) -> bool:
        """发送控制台通知"""
        if not self.can_send():
            return False

        try:
            # 级别颜色映射
            level_colors = {
                NotificationLevel.DEBUG: "\033[36m",  # 青色
                NotificationLevel.INFO: "\033[32m",  # 绿色
                NotificationLevel.WARNING: "\033[33m",  # 黄色
                NotificationLevel.ERROR: "\033[31m",  # 红色
                NotificationLevel.CRITICAL: "\033[35m",  # 紫色
            }

            reset_color = "\033[0m"
            color = level_colors.get(message.level, "")

            timestamp_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
            )

            print(
                f"{color}[{message.level.value.upper()}] {timestamp_str} - {message.title}{reset_color}"
            )
            print(f"内容: {message.content}")
            if message.tags:
                print(f"标签: {json.dumps(message.tags, ensure_ascii=False)}")
            print("-" * 50)

            self.record_sent()
            return True

        except Exception as e:
            self.logger.error(f"控制台通知发送失败: {e}")
            return False


class NotificationManager:
    """通知管理器"""

    def __init__(self) -> None:
        self.channels: dict[str, NotificationChannel] = {}
        self.logger = logging.getLogger("notification_manager")

    def add_channel(self, name: str, channel: NotificationChannel):
        """添加通知渠道"""
        self.channels[name] = channel
        self.logger.info(f"添加通知渠道: {name} ({channel.config.channel_type.value})")

    def remove_channel(self, name: str):
        """移除通知渠道"""
        if name in self.channels:
            del self.channels[name]
            self.logger.info(f"移除通知渠道: {name}")

    async def send_notification(
        self, message: NotificationMessage, channels: list[str] | None = None
    ) -> dict[str, bool]:
        """发送通知到指定渠道"""
        if channels is None:
            channels = list(self.channels.keys())

        results = {}
        tasks = []

        for channel_name in channels:
            if channel_name in self.channels:
                channel = self.channels[channel_name]
                task = asyncio.create_task(
                    self._send_with_retry(channel, message),
                    name=f"notify_{channel_name}",
                )
                tasks.append((channel_name, task))

        # 并发发送
        for channel_name, task in tasks:
            try:
                result = await task
                results[channel_name] = result
            except Exception as e:
                self.logger.error(f"通知渠道 {channel_name} 发送异常: {e}")
                results[channel_name] = False

        return results

    async def _send_with_retry(
        self, channel: NotificationChannel, message: NotificationMessage
    ) -> bool:
        """带重试的发送"""
        for attempt in range(channel.config.retry_count):
            try:
                result = await channel.send(message)
                if result:
                    return True

                if attempt < channel.config.retry_count - 1:
                    await asyncio.sleep(2**attempt)  # 指数退避

            except Exception as e:
                self.logger.error(f"发送尝试 {attempt + 1} 失败: {e}")
                if attempt < channel.config.retry_count - 1:
                    await asyncio.sleep(2**attempt)

        return False

    def get_channel_stats(self) -> dict[str, dict[str, Any]]:
        """获取渠道统计信息"""
        stats = {}
        for name, channel in self.channels.items():
            stats[name] = {
                "type": channel.config.channel_type.value,
                "enabled": channel.config.enabled,
                "sent_count": channel.sent_count,
                "rate_limit": channel.config.rate_limit,
                "last_reset_time": channel.last_reset_time,
            }
        return stats


# 工厂函数
def create_channel(
    channel_type: ChannelType, config: dict[str, Any]
) -> NotificationChannel:
    """创建通知渠道"""
    channel_config = ChannelConfig(
        channel_type=channel_type,
        enabled=config.get("enabled", True),
        config=config.get("config", {}),
        rate_limit=config.get("rate_limit"),
        retry_count=config.get("retry_count", 3),
        timeout=config.get("timeout", 30),
    )

    channel_classes = {
        ChannelType.EMAIL: EmailChannel,
        ChannelType.DINGTALK: DingTalkChannel,
        ChannelType.WECHAT_WORK: WeChatWorkChannel,
        ChannelType.SLACK: SlackChannel,
        ChannelType.WEBHOOK: WebhookChannel,
        ChannelType.CONSOLE: ConsoleChannel,
    }

    channel_class = channel_classes.get(channel_type)
    if not channel_class:
        raise ValueError(f"不支持的通知渠道类型: {channel_type}")

    return channel_class(channel_config)


# 使用示例
if __name__ == "__main__":

    async def demo_notifications() -> None:
        """演示多通道通知"""
        print("🚀 多通道通知系统演示")

        # 创建通知管理器
        manager = NotificationManager()

        # 添加控制台通知渠道
        console_channel = create_channel(
            ChannelType.CONSOLE, {"enabled": True, "rate_limit": 10}
        )
        manager.add_channel("console", console_channel)

        # 添加钉钉通知渠道（示例配置）
        dingtalk_channel = create_channel(
            ChannelType.DINGTALK,
            {
                "enabled": True,
                "config": {
                    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
                    "secret": "YOUR_SECRET",
                },
                "rate_limit": 20,
            },
        )
        manager.add_channel("dingtalk", dingtalk_channel)

        # 创建测试消息
        messages = [
            NotificationMessage(
                title="系统启动",
                content="无障碍服务已成功启动",
                level=NotificationLevel.INFO,
                tags={"service": "accessibility", "action": "startup"},
            ),
            NotificationMessage(
                title="性能告警",
                content="CPU使用率超过80%",
                level=NotificationLevel.WARNING,
                tags={"metric": "cpu", "threshold": "80%"},
            ),
            NotificationMessage(
                title="系统错误",
                content="数据库连接失败",
                level=NotificationLevel.ERROR,
                tags={"component": "database", "error": "connection_failed"},
            ),
        ]

        # 发送通知
        for i, message in enumerate(messages, 1):
            print(f"\n📢 发送通知 {i}/{len(messages)}")
            results = await manager.send_notification(message, ["console"])
            print(f"发送结果: {results}")
            await asyncio.sleep(1)

        # 显示统计信息
        print("\n📊 渠道统计信息:")
        stats = manager.get_channel_stats()
        for name, stat in stats.items():
            print(f"  {name}: {stat}")

        print("✅ 多通道通知系统演示完成")

    asyncio.run(demo_notifications())
