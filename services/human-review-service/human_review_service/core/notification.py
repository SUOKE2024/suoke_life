"""
notification - 索克生活项目模块
"""

        import aioredis
    import redis.asyncio as aioredis
from .config import settings
from .models import ReviewStatus, ReviewTask, Reviewer
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional, Union
import asyncio
import json
import structlog

"""
通知服务
Notification Service

处理审核系统的各种通知需求，包括邮件、短信、WebSocket推送等
"""


try:
except ImportError:
    try:
    except ImportError:
        aioredis = None


logger = structlog.get_logger(__name__)


class NotificationType(str, Enum):
    """通知类型枚举"""
    
    TASK_ASSIGNED = "task_assigned"  # 任务分配
    TASK_COMPLETED = "task_completed"  # 任务完成
    TASK_EXPIRED = "task_expired"  # 任务过期
    TASK_CANCELLED = "task_cancelled"  # 任务取消
    REVIEWER_ACTIVATED = "reviewer_activated"  # 审核员激活
    REVIEWER_DEACTIVATED = "reviewer_deactivated"  # 审核员停用
    SYSTEM_ALERT = "system_alert"  # 系统告警
    PERFORMANCE_REPORT = "performance_report"  # 绩效报告


class NotificationChannel(str, Enum):
    """通知渠道枚举"""
    
    EMAIL = "email"  # 邮件
    SMS = "sms"  # 短信
    WEBSOCKET = "websocket"  # WebSocket推送
    WEBHOOK = "webhook"  # Webhook回调
    SLACK = "slack"  # Slack消息
    DINGTALK = "dingtalk"  # 钉钉消息


class NotificationPriority(str, Enum):
    """通知优先级枚举"""
    
    LOW = "low"  # 低优先级
    NORMAL = "normal"  # 普通优先级
    HIGH = "high"  # 高优先级
    URGENT = "urgent"  # 紧急优先级


class NotificationMessage(BaseModel):
    """通知消息模型"""
    
    id: str
    type: NotificationType
    channel: NotificationChannel
    priority: NotificationPriority = NotificationPriority.NORMAL
    recipient: str  # 接收者ID或地址
    subject: str
    content: str
    data: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str = "pending"  # pending, sent, failed, cancelled


class NotificationProvider(ABC):
    """通知提供者抽象基类"""
    
    @abstractmethod
    async def send(self, message: NotificationMessage) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """检查提供者是否可用"""
        pass


class EmailProvider(NotificationProvider):
    """邮件通知提供者"""
    
    def __init__(self):
        self.smtp_host = settings.notification.smtp_host
        self.smtp_port = settings.notification.smtp_port
        self.smtp_user = settings.notification.smtp_user
        self.smtp_password = settings.notification.smtp_password
        self.from_email = settings.notification.from_email
    
    async def send(self, message: NotificationMessage) -> bool:
        """发送邮件通知"""
        try:
            # 这里应该集成实际的邮件发送服务
            # 例如使用 aiosmtplib 或 SendGrid API
            logger.info(
                "Sending email notification",
                recipient=message.recipient,
                subject=message.subject,
                type=message.type
            )
            
            # 模拟邮件发送
            await asyncio.sleep(0.1)
            
            logger.info(
                "Email notification sent successfully",
                message_id=message.id,
                recipient=message.recipient
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send email notification",
                message_id=message.id,
                recipient=message.recipient,
                error=str(e)
            )
            return False
    
    async def is_available(self) -> bool:
        """检查邮件服务是否可用"""
        return bool(self.smtp_host and self.smtp_user)


class WebSocketProvider(NotificationProvider):
    """WebSocket通知提供者"""

    def __init__(self, redis_client: Optional[Any] = None):
        self.redis_client = redis_client
    
    async def send(self, message: NotificationMessage) -> bool:
        """发送WebSocket通知"""
        try:
            if not self.redis_client:
                logger.warning("Redis client not available for WebSocket notifications")
                return False
            
            # 发布到Redis频道，由WebSocket服务器监听
            channel = f"notifications:{message.recipient}"
            payload = {
                "id": message.id,
                "type": message.type,
                "subject": message.subject,
                "content": message.content,
                "data": message.data,
                "created_at": message.created_at.isoformat(),
                "priority": message.priority
            }
            
            await self.redis_client.publish(channel, json.dumps(payload))
            
            logger.info(
                "WebSocket notification published",
                message_id=message.id,
                recipient=message.recipient,
                channel=channel
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send WebSocket notification",
                message_id=message.id,
                recipient=message.recipient,
                error=str(e)
            )
            return False
    
    async def is_available(self) -> bool:
        """检查WebSocket服务是否可用"""
        return self.redis_client is not None


class WebhookProvider(NotificationProvider):
    """Webhook通知提供者"""
    
    def __init__(self):
        self.webhook_urls = settings.notification.webhook_urls or {}
    
    async def send(self, message: NotificationMessage) -> bool:
        """发送Webhook通知"""
        try:
            webhook_url = self.webhook_urls.get(message.type.value)
            if not webhook_url:
                logger.warning(
                    "No webhook URL configured for notification type",
                    type=message.type
                )
                return False
            
            # 这里应该使用 httpx 发送HTTP请求
            logger.info(
                "Sending webhook notification",
                message_id=message.id,
                webhook_url=webhook_url,
                type=message.type
            )
            
            # 模拟webhook发送
            await asyncio.sleep(0.1)
            
            logger.info(
                "Webhook notification sent successfully",
                message_id=message.id,
                webhook_url=webhook_url
            )
            return True
            
        except Exception as e:
            logger.error(
                "Failed to send webhook notification",
                message_id=message.id,
                error=str(e)
            )
            return False
    
    async def is_available(self) -> bool:
        """检查Webhook服务是否可用"""
        return bool(self.webhook_urls)


class NotificationService:
    """通知服务主类"""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """初始化通知服务
        
        Args:
            redis_client: Redis客户端，用于WebSocket通知
        """
        self.providers: Dict[NotificationChannel, NotificationProvider] = {}
        self.redis_client = redis_client
        
        # 初始化通知提供者
        self._init_providers()
    
    def _init_providers(self):
        """初始化通知提供者"""
        # 邮件提供者
        if settings.notification.enable_email:
            self.providers[NotificationChannel.EMAIL] = EmailProvider()
        
        # WebSocket提供者
        if settings.notification.enable_websocket and self.redis_client:
            self.providers[NotificationChannel.WEBSOCKET] = WebSocketProvider(self.redis_client)
        
        # Webhook提供者
        if settings.notification.enable_webhook:
            self.providers[NotificationChannel.WEBHOOK] = WebhookProvider()
    
    async def send_notification(
        self,
        type: NotificationType,
        recipient: str,
        subject: str,
        content: str,
        channels: List[NotificationChannel],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        scheduled_at: Optional[datetime] = None
    ) -> List[str]:
        """发送通知
        
        Args:
            type: 通知类型
            recipient: 接收者
            subject: 主题
            content: 内容
            channels: 通知渠道列表
            priority: 优先级
            data: 附加数据
            template: 模板名称
            scheduled_at: 计划发送时间
            
        Returns:
            成功发送的消息ID列表
        """
        sent_messages = []
        
        for channel in channels:
            provider = self.providers.get(channel)
            if not provider:
                logger.warning(
                    "No provider available for notification channel",
                    channel=channel
                )
                continue
            
            if not await provider.is_available():
                logger.warning(
                    "Provider not available for notification channel",
                    channel=channel
                )
                continue
            
            # 创建通知消息
            message = NotificationMessage(
                id=f"{type.value}_{channel.value}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{recipient}",
                type=type,
                channel=channel,
                priority=priority,
                recipient=recipient,
                subject=subject,
                content=content,
                data=data,
                template=template,
                created_at=datetime.now(timezone.utc),
                scheduled_at=scheduled_at
            )
            
            # 发送通知
            try:
                success = await provider.send(message)
                if success:
                    sent_messages.append(message.id)
                    message.status = "sent"
                    message.sent_at = datetime.now(timezone.utc)
                else:
                    message.status = "failed"
                
                logger.info(
                    "Notification send attempt completed",
                    message_id=message.id,
                    channel=channel,
                    success=success
                )
                
            except Exception as e:
                logger.error(
                    "Failed to send notification",
                    type=type,
                    channel=channel,
                    recipient=recipient,
                    error=str(e)
                )
        
        return sent_messages
    
    async def notify_task_assigned(
        self,
        task: ReviewTask,
        reviewer: Reviewer,
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """通知任务分配"""
        if not channels:
            channels = [NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
        
        subject = f"新审核任务分配 - {task.review_type.value}"
        content = f"""
您好 {reviewer.name}，

您有一个新的审核任务需要处理：

任务ID: {task.task_id}
任务类型: {task.review_type.value}
优先级: {task.priority.value}
预估时长: {task.estimated_duration // 60} 分钟
过期时间: {task.expires_at.strftime('%Y-%m-%d %H:%M:%S') if task.expires_at else '无'}

请及时登录系统处理该任务。

索克生活审核系统
        """.strip()
        
        return await self.send_notification(
            type=NotificationType.TASK_ASSIGNED,
            recipient=reviewer.reviewer_id,
            subject=subject,
            content=content,
            channels=channels,
            priority=NotificationPriority.HIGH if task.priority.value in ['urgent', 'critical'] else NotificationPriority.NORMAL,
            data={
                "task_id": task.task_id,
                "task_type": task.review_type.value,
                "priority": task.priority.value,
                "reviewer_id": reviewer.reviewer_id
            }
        )
    
    async def notify_task_completed(
        self,
        task: ReviewTask,
        reviewer: Reviewer,
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """通知任务完成"""
        if not channels:
            channels = [NotificationChannel.WEBSOCKET]
        
        subject = f"审核任务已完成 - {task.task_id}"
        content = f"""
任务 {task.task_id} 已由审核员 {reviewer.name} 完成。

审核结果: {task.status.value}
完成时间: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else '未知'}
审核时长: {task.actual_duration // 60 if task.actual_duration else 0} 分钟

索克生活审核系统
        """.strip()
        
        return await self.send_notification(
            type=NotificationType.TASK_COMPLETED,
            recipient="system",  # 系统通知
            subject=subject,
            content=content,
            channels=channels,
            data={
                "task_id": task.task_id,
                "reviewer_id": reviewer.reviewer_id,
                "status": task.status.value,
                "duration": task.actual_duration
            }
        )
    
    async def notify_task_expired(
        self,
        task: ReviewTask,
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """通知任务过期"""
        if not channels:
            channels = [NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
        
        subject = f"审核任务已过期 - {task.task_id}"
        content = f"""
任务 {task.task_id} 已过期，需要重新分配。

任务类型: {task.review_type.value}
优先级: {task.priority.value}
过期时间: {task.expires_at.strftime('%Y-%m-%d %H:%M:%S') if task.expires_at else '未知'}
分配给: {task.assigned_to or '未分配'}

请管理员及时处理。

索克生活审核系统
        """.strip()
        
        return await self.send_notification(
            type=NotificationType.TASK_EXPIRED,
            recipient="admin",  # 管理员通知
            subject=subject,
            content=content,
            channels=channels,
            priority=NotificationPriority.HIGH,
            data={
                "task_id": task.task_id,
                "assigned_to": task.assigned_to,
                "expires_at": task.expires_at.isoformat() if task.expires_at else None
            }
        )
    
    async def notify_system_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """发送系统告警通知"""
        if not channels:
            channels = [NotificationChannel.EMAIL, NotificationChannel.WEBHOOK]
        
        priority_map = {
            "info": NotificationPriority.LOW,
            "warning": NotificationPriority.NORMAL,
            "error": NotificationPriority.HIGH,
            "critical": NotificationPriority.URGENT
        }
        
        subject = f"系统告警 - {alert_type}"
        content = f"""
系统告警详情：

告警类型: {alert_type}
严重程度: {severity}
告警时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}

告警信息:
{message}

请及时检查系统状态。

索克生活审核系统
        """.strip()
        
        return await self.send_notification(
            type=NotificationType.SYSTEM_ALERT,
            recipient="admin",
            subject=subject,
            content=content,
            channels=channels,
            priority=priority_map.get(severity, NotificationPriority.NORMAL),
            data={
                "alert_type": alert_type,
                "severity": severity,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    async def get_provider_status(self) -> Dict[str, bool]:
        """获取所有通知提供者的状态"""
        status = {}
        for channel, provider in self.providers.items():
            try:
                status[channel.value] = await provider.is_available()
            except Exception as e:
                logger.error(
                    "Failed to check provider status",
                    channel=channel,
                    error=str(e)
                )
                status[channel.value] = False
        
        return status 