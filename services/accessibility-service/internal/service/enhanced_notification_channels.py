#!/usr/bin/env python3
"""
增强版通知渠道模块
支持多种通知方式：邮件、短信、钉钉、微信、Slack、Teams、Telegram等
特性：
1. 多渠道并发发送
2. 失败重试机制
3. 通知模板系统
4. 频率限制和去重
5. 渠道健康检查
"""

import asyncio
import base64
import hashlib
import hmac
import logging
import os
import smtplib
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from enum import Enum
from typing import Any
from urllib.parse import quote_plus

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
    WECHAT = "wechat"
    SLACK = "slack"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class NotificationMessage:
    """通知消息"""

    title: str
    content: str
    level: NotificationLevel
    timestamp: float = field(default_factory=time.time)
    source: str = "accessibility-service"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_hash(self) -> str:
        """获取消息哈希用于去重"""
        content_str = f"{self.title}:{self.content}:{self.level.value}"
        return hashlib.sha256(content_str.encode()).hexdigest()


@dataclass
class ChannelConfig:
    """渠道配置"""

    enabled: bool = True
    levels: list[NotificationLevel] = field(
        default_factory=lambda: list(NotificationLevel)
    )
    rate_limit: int = 10  # 每分钟最大发送数
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: float = 10.0
    config: dict[str, Any] = field(default_factory=dict)


class NotificationChannel(ABC):
    """通知渠道基类"""

    def __init__(self, channel_type: ChannelType, config: ChannelConfig):
        self.channel_type = channel_type
        self.config = config
        self.sent_count = 0
        self.last_reset_time = time.time()
        self.recent_hashes = set()  # 用于去重
        self.last_cleanup_time = time.time()

    def can_send(self, message: NotificationMessage) -> bool:
        """检查是否可以发送"""
        # 检查渠道是否启用
        if not self.config.enabled:
            return False

        # 检查级别过滤
        if message.level not in self.config.levels:
            return False

        # 检查频率限制
        current_time = time.time()
        if current_time - self.last_reset_time > 60:  # 每分钟重置
            self.sent_count = 0
            self.last_reset_time = current_time

        if self.sent_count >= self.config.rate_limit:
            logger.warning(f"{self.channel_type.value} 渠道达到频率限制")
            return False

        # 检查消息去重
        message_hash = message.get_hash()
        if message_hash in self.recent_hashes:
            logger.debug(f"消息重复，跳过发送: {message.title}")
            return False

        return True

    def mark_sent(self, message: NotificationMessage):
        """标记消息已发送"""
        self.sent_count += 1
        self.recent_hashes.add(message.get_hash())

        # 定期清理哈希缓存
        current_time = time.time()
        if current_time - self.last_cleanup_time > 300:  # 5分钟清理一次
            self.recent_hashes.clear()
            self.last_cleanup_time = current_time

    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """发送通知"""
        pass

    async def send_with_retry(self, message: NotificationMessage) -> bool:
        """带重试的发送"""
        if not self.can_send(message):
            return False

        for attempt in range(self.config.retry_count):
            try:
                success = await asyncio.wait_for(
                    self.send(message), timeout=self.config.timeout
                )

                if success:
                    self.mark_sent(message)
                    return True

            except TimeoutError:
                logger.warning(
                    f"{self.channel_type.value} 发送超时 (尝试 {attempt + 1})"
                )
            except Exception as e:
                logger.error(
                    f"{self.channel_type.value} 发送失败 (尝试 {attempt + 1}): {e}"
                )

            if attempt < self.config.retry_count - 1:
                await asyncio.sleep(self.config.retry_delay * (attempt + 1))

        return False


class EmailChannel(NotificationChannel):
    """邮件通知渠道"""

    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.EMAIL, config)
        self.smtp_server = config.config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.config.get("smtp_port", 587)
        self.username = config.config.get("username", "")
        # 安全修复: 使用环境变量存储敏感信息
        self.password = os.getenv("SMTP_PASSWORD") or config.config.get("password", "")
        if not self.password and config.config.get("password"):
            logger.warning("建议使用环境变量 SMTP_PASSWORD 存储邮件密码")
        self.from_email = config.config.get("from_email", self.username)
        self.from_name = config.config.get("from_name", "索克生活监控")
        self.to_emails = config.config.get("to_emails", [])

    async def send(self, message: NotificationMessage) -> bool:
        """发送邮件"""
        if not self.to_emails:
            logger.warning("邮件收件人列表为空")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[{message.level.value.upper()}] {message.title}"
            msg["From"] = formataddr((self.from_name, self.from_email))
            msg["To"] = ", ".join(self.to_emails)

            # HTML内容
            html_content = self._create_html_content(message)
            html_part = MIMEText(html_content, "html", "utf-8")

            # 纯文本内容
            text_content = self._create_text_content(message)
            text_part = MIMEText(text_content, "plain", "utf-8")

            msg.attach(text_part)
            msg.attach(html_part)

            # 发送邮件
            await self._send_email(msg)
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"邮件认证失败: {e} - 请检查用户名和密码")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"邮件服务器连接失败: {e} - 请检查SMTP服务器配置")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"收件人被拒绝: {e} - 请检查收件人邮箱地址")
            return False
        except (ConnectionError, OSError) as e:
            logger.warning(f"网络连接问题: {e} - 将重试发送")
            return False
        except Exception as e:
            logger.error(f"邮件发送未知错误: {type(e).__name__}: {e}")
            return False

    async def _send_email(self, msg: MIMEMultipart) -> None:
        """异步发送邮件"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_email_sync, msg)

    def _send_email_sync(self, msg: MIMEMultipart) -> None:
        """同步发送邮件"""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)

    def _create_html_content(self, message: NotificationMessage) -> str:
        """创建HTML邮件内容"""
        level_colors = {
            NotificationLevel.INFO: "#17a2b8",
            NotificationLevel.WARNING: "#ffc107",
            NotificationLevel.ERROR: "#dc3545",
            NotificationLevel.CRITICAL: "#6f42c1",
        }

        color = level_colors.get(message.level, "#6c757d")
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
        )

        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f8f9fa;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background-color: {color}; color: white; padding: 20px;">
                    <h1 style="margin: 0; font-size: 24px;">🚨 索克生活监控告警</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{message.level.value.upper()} 级别告警</p>
                </div>
                <div style="padding: 20px;">
                    <h2 style="color: #333; margin-top: 0;">{message.title}</h2>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <pre style="margin: 0; white-space: pre-wrap; font-family: 'Courier New', monospace;">{message.content}</pre>
                    </div>
                    <div style="border-top: 1px solid #dee2e6; padding-top: 15px; margin-top: 20px;">
                        <p style="margin: 5px 0; color: #6c757d;"><strong>时间:</strong> {timestamp}</p>
                        <p style="margin: 5px 0; color: #6c757d;"><strong>来源:</strong> {message.source}</p>
                        {f'<p style="margin: 5px 0; color: #6c757d;"><strong>标签:</strong> {", ".join(message.tags)}</p>' if message.tags else ''}
                    </div>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; text-align: center; color: #6c757d; font-size: 12px;">
                    <p style="margin: 0;">此邮件由索克生活无障碍服务监控系统自动发送</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_text_content(self, message: NotificationMessage) -> str:
        """创建纯文本邮件内容"""
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
        )

        content = f"""
索克生活监控告警

级别: {message.level.value.upper()}
标题: {message.title}
时间: {timestamp}
来源: {message.source}

内容:
{message.content}
"""

        if message.tags:
            content += f"\n标签: {', '.join(message.tags)}"

        content += "\n\n---\n此邮件由索克生活无障碍服务监控系统自动发送"

        return content


class DingTalkChannel(NotificationChannel):
    """钉钉通知渠道"""

    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.DINGTALK, config)
        self.webhook_url = config.config.get("webhook_url", "")
        self.secret = config.config.get("secret", "")
        self.at_mobiles = config.config.get("at_mobiles", [])
        self.at_all = config.config.get("at_all", False)

    async def send(self, message: NotificationMessage) -> bool:
        """发送钉钉消息"""
        if not self.webhook_url:
            logger.warning("钉钉webhook URL未配置")
            return False

        try:
            # 构建消息
            timestamp = str(round(time.time() * 1000))
            sign = self._generate_sign(timestamp) if self.secret else None

            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"[{message.level.value.upper()}] {message.title}",
                    "text": self._create_markdown_content(message),
                },
            }

            # 添加@功能
            if self.at_mobiles or self.at_all:
                payload["at"] = {"atMobiles": self.at_mobiles, "isAtAll": self.at_all}

            # 发送请求
            url = self.webhook_url
            if sign:
                url += f"&timestamp={timestamp}&sign={sign}"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()
                    return result.get("errcode") == 0

        except aiohttp.ClientTimeout as e:
            logger.warning(f"钉钉请求超时: {e} - 将重试发送")
            return False
        except aiohttp.ClientConnectorError as e:
            logger.error(f"钉钉连接失败: {e} - 请检查网络连接")
            return False
        except aiohttp.ClientResponseError as e:
            logger.error(f"钉钉响应错误: {e.status} - {e.message}")
            return False
        except ValueError as e:
            logger.error(f"钉钉消息格式错误: {e} - 请检查消息内容")
            return False
        except Exception as e:
            logger.error(f"钉钉消息发送未知错误: {type(e).__name__}: {e}")
            return False

    def _generate_sign(self, timestamp: str) -> str:
        """生成钉钉签名"""
        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            self.secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return sign

    def _create_markdown_content(self, message: NotificationMessage) -> str:
        """创建Markdown内容"""
        level_emojis = {
            NotificationLevel.INFO: "ℹ️",
            NotificationLevel.WARNING: "⚠️",
            NotificationLevel.ERROR: "❌",
            NotificationLevel.CRITICAL: "🚨",
        }

        emoji = level_emojis.get(message.level, "📢")
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
        )

        content = f"""
# {emoji} 索克生活监控告警

**级别:** {message.level.value.upper()}
**标题:** {message.title}
**时间:** {timestamp}
**来源:** {message.source}

## 详细信息
```
{message.content}
```
"""

        if message.tags:
            content += f"\n**标签:** {', '.join(message.tags)}"

        # 添加@信息
        if self.at_mobiles:
            for mobile in self.at_mobiles:
                content += f"\n@{mobile}"

        return content


class WeChatWorkChannel(NotificationChannel):
    """企业微信通知渠道"""

    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.WECHAT, config)
        self.webhook_url = config.config.get("webhook_url", "")
        self.mentioned_list = config.config.get("mentioned_list", [])
        self.mentioned_mobile_list = config.config.get("mentioned_mobile_list", [])

    async def send(self, message: NotificationMessage) -> bool:
        """发送企业微信消息"""
        if not self.webhook_url:
            logger.warning("企业微信webhook URL未配置")
            return False

        try:
            payload = {
                "msgtype": "markdown",
                "markdown": {
                    "content": self._create_wechat_content(message),
                    "mentioned_list": self.mentioned_list,
                    "mentioned_mobile_list": self.mentioned_mobile_list,
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    result = await response.json()
                    return result.get("errcode") == 0

        except Exception as e:
            logger.error(f"企业微信消息发送失败: {e}")
            return False

    def _create_wechat_content(self, message: NotificationMessage) -> str:
        """创建企业微信内容"""
        level_colors = {
            NotificationLevel.INFO: "info",
            NotificationLevel.WARNING: "warning",
            NotificationLevel.ERROR: "comment",
            NotificationLevel.CRITICAL: "comment",
        }

        color = level_colors.get(message.level, "info")
        timestamp = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(message.timestamp)
        )

        content = f"""
# 🚨 索克生活监控告警

> **级别:** <font color="{color}">{message.level.value.upper()}</font>
> **标题:** {message.title}
> **时间:** {timestamp}
> **来源:** {message.source}

## 详细信息
```
{message.content}
```
"""

        if message.tags:
            content += f"\n> **标签:** {', '.join(message.tags)}"

        return content


class SlackChannel(NotificationChannel):
    """Slack通知渠道"""

    def __init__(self, config: ChannelConfig):
        super().__init__(ChannelType.SLACK, config)
        self.webhook_url = config.config.get("webhook_url", "")
        self.channel = config.config.get("channel", "#general")
        self.username = config.config.get("username", "索克生活监控")
        self.icon_emoji = config.config.get("icon_emoji", ":robot_face:")

    async def send(self, message: NotificationMessage) -> bool:
        """发送Slack消息"""
        if not self.webhook_url:
            logger.warning("Slack webhook URL未配置")
            return False

        try:
            payload = {
                "channel": self.channel,
                "username": self.username,
                "icon_emoji": self.icon_emoji,
                "attachments": [self._create_slack_attachment(message)],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Slack消息发送失败: {e}")
            return False

    def _create_slack_attachment(self, message: NotificationMessage) -> dict[str, Any]:
        """创建Slack附件"""
        level_colors = {
            NotificationLevel.INFO: "#36a64f",
            NotificationLevel.WARNING: "#ffcc00",
            NotificationLevel.ERROR: "#ff0000",
            NotificationLevel.CRITICAL: "#800080",
        }

        color = level_colors.get(message.level, "#cccccc")
        timestamp = int(message.timestamp)

        return {
            "color": color,
            "title": f"[{message.level.value.upper()}] {message.title}",
            "text": message.content,
            "fields": [
                {"title": "来源", "value": message.source, "short": True},
                {"title": "级别", "value": message.level.value.upper(), "short": True},
            ]
            + (
                [{"title": "标签", "value": ", ".join(message.tags), "short": False}]
                if message.tags
                else []
            ),
            "ts": timestamp,
        }


class EnhancedNotificationManager:
    """增强版通知管理器"""

    def __init__(self) -> None:
        self.channels: dict[ChannelType, NotificationChannel] = {}
        self.message_queue = asyncio.Queue()
        self.worker_task: asyncio.Task | None = None
        self.running = False

        # 统计信息
        self.total_sent = 0
        self.total_failed = 0
        self.channel_stats: dict[ChannelType, dict[str, int]] = defaultdict(
            lambda: {"sent": 0, "failed": 0}
        )

    def add_channel(self, channel: NotificationChannel):
        """添加通知渠道"""
        self.channels[channel.channel_type] = channel
        logger.info(f"已添加通知渠道: {channel.channel_type.value}")

    def remove_channel(self, channel_type: ChannelType):
        """移除通知渠道"""
        if channel_type in self.channels:
            del self.channels[channel_type]
            logger.info(f"已移除通知渠道: {channel_type.value}")

    async def send_notification(
        self, message: NotificationMessage, channels: list[ChannelType] | None = None
    ):
        """发送通知"""
        if channels is None:
            channels = list(self.channels.keys())

        # 添加到队列
        await self.message_queue.put((message, channels))

    async def _worker(self) -> None:
        """通知发送工作器"""
        while self.running:
            try:
                # 获取消息
                message, channels = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )

                # 并发发送到所有渠道
                tasks = []
                for channel_type in channels:
                    if channel_type in self.channels:
                        channel = self.channels[channel_type]
                        task = asyncio.create_task(
                            self._send_to_channel(channel, message)
                        )
                        tasks.append((channel_type, task))

                # 等待所有发送完成
                if tasks:
                    results = await asyncio.gather(
                        *[task for _, task in tasks], return_exceptions=True
                    )

                    # 更新统计
                    for (channel_type, _), result in zip(tasks, results, strict=False):
                        if isinstance(result, bool) and result:
                            self.total_sent += 1
                            self.channel_stats[channel_type]["sent"] += 1
                        else:
                            self.total_failed += 1
                            self.channel_stats[channel_type]["failed"] += 1

            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"通知发送工作器异常: {e}")

    async def _send_to_channel(
        self, channel: NotificationChannel, message: NotificationMessage
    ) -> bool:
        """发送到指定渠道"""
        try:
            return await channel.send_with_retry(message)
        except Exception as e:
            logger.error(f"渠道 {channel.channel_type.value} 发送失败: {e}")
            return False

    async def start(self) -> None:
        """启动通知管理器"""
        if self.running:
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("通知管理器已启动")

    async def stop(self) -> None:
        """停止通知管理器"""
        if not self.running:
            return

        self.running = False

        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        logger.info("通知管理器已停止")

    def get_statistics(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "total_sent": self.total_sent,
            "total_failed": self.total_failed,
            "success_rate": (
                self.total_sent / max(self.total_sent + self.total_failed, 1)
            )
            * 100,
            "channels": dict(self.channel_stats),
            "active_channels": len(self.channels),
            "queue_size": self.message_queue.qsize(),
        }

    async def test_channels(self) -> dict[ChannelType, bool]:
        """测试所有渠道"""
        test_message = NotificationMessage(
            title="通知渠道测试",
            content="这是一条测试消息，用于验证通知渠道是否正常工作。",
            level=NotificationLevel.INFO,
            tags=["test"],
        )

        results = {}
        tasks = []

        for channel_type, channel in self.channels.items():
            task = asyncio.create_task(self._send_to_channel(channel, test_message))
            tasks.append((channel_type, task))

        if tasks:
            test_results = await asyncio.gather(
                *[task for _, task in tasks], return_exceptions=True
            )

            for (channel_type, _), result in zip(tasks, test_results, strict=False):
                results[channel_type] = isinstance(result, bool) and result

        return results


# 全局通知管理器
enhanced_notification_manager = EnhancedNotificationManager()


def setup_notification_channels(config: dict[str, Any]):
    """设置通知渠道"""
    # 邮件渠道
    if "email" in config and config["email"].get("enabled", False):
        email_config = ChannelConfig(
            enabled=True,
            levels=[
                NotificationLevel.WARNING,
                NotificationLevel.ERROR,
                NotificationLevel.CRITICAL,
            ],
            rate_limit=5,
            config=config["email"],
        )
        enhanced_notification_manager.add_channel(EmailChannel(email_config))

    # 钉钉渠道
    if "dingtalk" in config and config["dingtalk"].get("enabled", False):
        dingtalk_config = ChannelConfig(
            enabled=True,
            levels=[NotificationLevel.ERROR, NotificationLevel.CRITICAL],
            rate_limit=10,
            config=config["dingtalk"],
        )
        enhanced_notification_manager.add_channel(DingTalkChannel(dingtalk_config))

    # 企业微信渠道
    if "wechat" in config and config["wechat"].get("enabled", False):
        wechat_config = ChannelConfig(
            enabled=True,
            levels=[NotificationLevel.ERROR, NotificationLevel.CRITICAL],
            rate_limit=10,
            config=config["wechat"],
        )
        enhanced_notification_manager.add_channel(WeChatWorkChannel(wechat_config))

    # Slack渠道
    if "slack" in config and config["slack"].get("enabled", False):
        slack_config = ChannelConfig(
            enabled=True,
            levels=[
                NotificationLevel.WARNING,
                NotificationLevel.ERROR,
                NotificationLevel.CRITICAL,
            ],
            rate_limit=15,
            config=config["slack"],
        )
        enhanced_notification_manager.add_channel(SlackChannel(slack_config))

    logger.info(f"已设置 {len(enhanced_notification_manager.channels)} 个通知渠道")


async def send_alert_notification(
    title: str, content: str, level: NotificationLevel = NotificationLevel.WARNING
):
    """发送告警通知"""
    message = NotificationMessage(
        title=title,
        content=content,
        level=level,
        tags=["alert", "accessibility-service"],
    )

    await enhanced_notification_manager.send_notification(message)


async def demo_notification_channels() -> None:
    """演示通知渠道"""
    print("🚀 增强版通知渠道演示")

    # 示例配置
    demo_config = {
        "email": {
            "enabled": False,  # 需要真实SMTP配置
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-password",
            "to_emails": ["admin@example.com"],
        },
        "dingtalk": {
            "enabled": False,  # 需要真实webhook URL
            "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
            "secret": "YOUR_SECRET",
        },
        "wechat": {
            "enabled": False,  # 需要真实webhook URL
            "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY",
        },
        "slack": {
            "enabled": False,  # 需要真实webhook URL
            "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
        },
    }

    # 设置渠道
    setup_notification_channels(demo_config)

    # 启动管理器
    await enhanced_notification_manager.start()

    try:
        # 发送测试消息
        test_messages = [
            ("系统启动", "索克生活无障碍服务已成功启动", NotificationLevel.INFO),
            ("性能警告", "CPU使用率达到85%，请关注系统性能", NotificationLevel.WARNING),
            ("服务错误", "健康检查失败，部分服务不可用", NotificationLevel.ERROR),
            ("严重故障", "系统出现严重故障，需要立即处理", NotificationLevel.CRITICAL),
        ]

        for title, content, level in test_messages:
            await send_alert_notification(title, content, level)
            print(f"✅ 已发送 {level.value} 级别通知: {title}")
            await asyncio.sleep(1)

        # 等待发送完成
        await asyncio.sleep(3)

        # 显示统计
        stats = enhanced_notification_manager.get_statistics()
        print("\n📊 发送统计:")
        print(f"总发送数: {stats['total_sent']}")
        print(f"失败数: {stats['total_failed']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"活跃渠道: {stats['active_channels']}")

        # 测试渠道
        print("\n🧪 测试渠道连通性...")
        test_results = await enhanced_notification_manager.test_channels()
        for channel_type, success in test_results.items():
            status = "✅ 正常" if success else "❌ 失败"
            print(f"{channel_type.value}: {status}")

    finally:
        await enhanced_notification_manager.stop()


if __name__ == "__main__":
    asyncio.run(demo_notification_channels())
