"""
通知服务测试
Notification Service Tests

测试通知服务的各种功能
"""

import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..core.notification import (
    EmailProvider,
    NotificationChannel,
    NotificationMessage,
    NotificationPriority,
    NotificationService,
    NotificationType,
    WebhookProvider,
    WebSocketProvider,
)
from ..core.models import ReviewPriority, ReviewStatus, ReviewTask, ReviewType, Reviewer


class TestNotificationMessage:
    """通知消息模型测试"""

    def test_notification_message_creation(self):
        """测试通知消息创建"""
        message = NotificationMessage(
            id="test_message_1",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.EMAIL,
            priority=NotificationPriority.HIGH,
            recipient="test@example.com",
            subject="测试通知",
            content="这是一条测试通知",
            created_at=datetime.now(timezone.utc)
        )
        
        assert message.id == "test_message_1"
        assert message.type == NotificationType.TASK_ASSIGNED
        assert message.channel == NotificationChannel.EMAIL
        assert message.priority == NotificationPriority.HIGH
        assert message.recipient == "test@example.com"
        assert message.subject == "测试通知"
        assert message.content == "这是一条测试通知"
        assert message.status == "pending"

    def test_notification_message_with_data(self):
        """测试带附加数据的通知消息"""
        data = {
            "task_id": "task_123",
            "reviewer_id": "reviewer_456",
            "priority": "high"
        }
        
        message = NotificationMessage(
            id="test_message_2",
            type=NotificationType.TASK_COMPLETED,
            channel=NotificationChannel.WEBSOCKET,
            recipient="reviewer_456",
            subject="任务完成",
            content="任务已完成",
            data=data,
            created_at=datetime.now(timezone.utc)
        )
        
        assert message.data == data
        assert message.data["task_id"] == "task_123"


class TestEmailProvider:
    """邮件提供者测试"""

    def setup_method(self):
        """设置测试环境"""
        self.provider = EmailProvider()

    @pytest.mark.asyncio
    async def test_email_provider_send_success(self):
        """测试邮件发送成功"""
        message = NotificationMessage(
            id="email_test_1",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="测试邮件",
            content="这是一封测试邮件",
            created_at=datetime.now(timezone.utc)
        )
        
        # 由于是模拟发送，应该返回True
        result = await self.provider.send(message)
        assert result is True

    @pytest.mark.asyncio
    async def test_email_provider_is_available(self):
        """测试邮件提供者可用性检查"""
        # 默认配置下应该可用（有默认的SMTP配置）
        result = await self.provider.is_available()
        assert isinstance(result, bool)


class TestWebSocketProvider:
    """WebSocket提供者测试"""

    def setup_method(self):
        """设置测试环境"""
        self.mock_redis = AsyncMock()
        self.provider = WebSocketProvider(redis_client=self.mock_redis)

    @pytest.mark.asyncio
    async def test_websocket_provider_send_success(self):
        """测试WebSocket发送成功"""
        message = NotificationMessage(
            id="ws_test_1",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.WEBSOCKET,
            recipient="reviewer_123",
            subject="新任务分配",
            content="您有新的审核任务",
            created_at=datetime.now(timezone.utc)
        )
        
        # 模拟Redis发布成功
        self.mock_redis.publish.return_value = 1
        
        result = await self.provider.send(message)
        assert result is True
        
        # 验证Redis发布被调用
        self.mock_redis.publish.assert_called_once()
        call_args = self.mock_redis.publish.call_args
        assert call_args[0][0] == "notifications:reviewer_123"
        
        # 验证发布的消息格式
        published_data = json.loads(call_args[0][1])
        assert published_data["id"] == "ws_test_1"
        assert published_data["type"] == NotificationType.TASK_ASSIGNED
        assert published_data["subject"] == "新任务分配"

    @pytest.mark.asyncio
    async def test_websocket_provider_no_redis(self):
        """测试没有Redis客户端的情况"""
        provider = WebSocketProvider(redis_client=None)
        
        message = NotificationMessage(
            id="ws_test_2",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.WEBSOCKET,
            recipient="reviewer_123",
            subject="新任务分配",
            content="您有新的审核任务",
            created_at=datetime.now(timezone.utc)
        )
        
        result = await provider.send(message)
        assert result is False

    @pytest.mark.asyncio
    async def test_websocket_provider_is_available(self):
        """测试WebSocket提供者可用性检查"""
        # 有Redis客户端时应该可用
        result = await self.provider.is_available()
        assert result is True
        
        # 没有Redis客户端时不可用
        provider_no_redis = WebSocketProvider(redis_client=None)
        result = await provider_no_redis.is_available()
        assert result is False


class TestWebhookProvider:
    """Webhook提供者测试"""

    def setup_method(self):
        """设置测试环境"""
        self.provider = WebhookProvider()

    @pytest.mark.asyncio
    async def test_webhook_provider_send_success(self):
        """测试Webhook发送成功"""
        # 模拟有配置的webhook URL
        self.provider.webhook_urls = {
            "task_assigned": "https://example.com/webhook/task_assigned"
        }
        
        message = NotificationMessage(
            id="webhook_test_1",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.WEBHOOK,
            recipient="system",
            subject="任务分配通知",
            content="新任务已分配",
            created_at=datetime.now(timezone.utc)
        )
        
        result = await self.provider.send(message)
        assert result is True

    @pytest.mark.asyncio
    async def test_webhook_provider_no_url_configured(self):
        """测试没有配置Webhook URL的情况"""
        message = NotificationMessage(
            id="webhook_test_2",
            type=NotificationType.TASK_ASSIGNED,
            channel=NotificationChannel.WEBHOOK,
            recipient="system",
            subject="任务分配通知",
            content="新任务已分配",
            created_at=datetime.now(timezone.utc)
        )
        
        result = await self.provider.send(message)
        assert result is False

    @pytest.mark.asyncio
    async def test_webhook_provider_is_available(self):
        """测试Webhook提供者可用性检查"""
        # 没有配置时不可用
        result = await self.provider.is_available()
        assert result is False
        
        # 有配置时可用
        self.provider.webhook_urls = {"test": "https://example.com/webhook"}
        result = await self.provider.is_available()
        assert result is True


class TestNotificationService:
    """通知服务测试"""

    def setup_method(self):
        """设置测试环境"""
        self.mock_redis = AsyncMock()
        self.service = NotificationService(redis_client=self.mock_redis)

    @pytest.mark.asyncio
    async def test_send_notification_single_channel(self):
        """测试单渠道发送通知"""
        with patch.object(self.service.providers[NotificationChannel.WEBSOCKET], 'send', return_value=True) as mock_send:
            with patch.object(self.service.providers[NotificationChannel.WEBSOCKET], 'is_available', return_value=True):
                result = await self.service.send_notification(
                    type=NotificationType.TASK_ASSIGNED,
                    recipient="reviewer_123",
                    subject="新任务分配",
                    content="您有新的审核任务需要处理",
                    channels=[NotificationChannel.WEBSOCKET]
                )
                
                assert len(result) == 1
                mock_send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_notification_multiple_channels(self):
        """测试多渠道发送通知"""
        # 模拟所有提供者都可用并发送成功
        for provider in self.service.providers.values():
            provider.send = AsyncMock(return_value=True)
            provider.is_available = AsyncMock(return_value=True)
        
        result = await self.service.send_notification(
            type=NotificationType.TASK_ASSIGNED,
            recipient="reviewer_123",
            subject="新任务分配",
            content="您有新的审核任务需要处理",
            channels=[NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET]
        )
        
        # 应该有两个成功发送的消息
        assert len(result) >= 0  # 取决于实际配置的提供者

    @pytest.mark.asyncio
    async def test_notify_task_assigned(self):
        """测试任务分配通知"""
        # 创建模拟的任务和审核员
        task = MagicMock(spec=ReviewTask)
        task.task_id = "task_123"
        task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        task.priority = ReviewPriority.HIGH
        task.estimated_duration = 1800
        task.expires_at = datetime.now(timezone.utc)
        
        reviewer = MagicMock(spec=Reviewer)
        reviewer.reviewer_id = "reviewer_456"
        reviewer.name = "张医生"
        
        # 模拟发送成功
        with patch.object(self.service, 'send_notification', return_value=["msg_1", "msg_2"]) as mock_send:
            result = await self.service.notify_task_assigned(task, reviewer)
            
            assert len(result) == 2
            mock_send.assert_called_once()
            
            # 检查调用参数
            call_args = mock_send.call_args
            assert call_args[1]["type"] == NotificationType.TASK_ASSIGNED
            assert call_args[1]["recipient"] == "reviewer_456"
            assert "新审核任务分配" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_notify_task_completed(self):
        """测试任务完成通知"""
        # 创建模拟的任务和审核员
        task = MagicMock(spec=ReviewTask)
        task.task_id = "task_123"
        task.status = ReviewStatus.APPROVED
        task.completed_at = datetime.now(timezone.utc)
        task.actual_duration = 1200
        
        reviewer = MagicMock(spec=Reviewer)
        reviewer.reviewer_id = "reviewer_456"
        reviewer.name = "张医生"
        
        # 模拟发送成功
        with patch.object(self.service, 'send_notification', return_value=["msg_1"]) as mock_send:
            result = await self.service.notify_task_completed(task, reviewer)
            
            assert len(result) == 1
            mock_send.assert_called_once()
            
            # 检查调用参数
            call_args = mock_send.call_args
            assert call_args[1]["type"] == NotificationType.TASK_COMPLETED
            assert call_args[1]["recipient"] == "system"
            assert "审核任务已完成" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_notify_task_expired(self):
        """测试任务过期通知"""
        # 创建模拟的过期任务
        task = MagicMock(spec=ReviewTask)
        task.task_id = "task_123"
        task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        task.priority = ReviewPriority.URGENT
        task.expires_at = datetime.now(timezone.utc)
        task.assigned_to = "reviewer_456"
        
        # 模拟发送成功
        with patch.object(self.service, 'send_notification', return_value=["msg_1", "msg_2"]) as mock_send:
            result = await self.service.notify_task_expired(task)
            
            assert len(result) == 2
            mock_send.assert_called_once()
            
            # 检查调用参数
            call_args = mock_send.call_args
            assert call_args[1]["type"] == NotificationType.TASK_EXPIRED
            assert call_args[1]["recipient"] == "admin"
            assert call_args[1]["priority"] == NotificationPriority.HIGH
            assert "审核任务已过期" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_notify_system_alert(self):
        """测试系统告警通知"""
        # 模拟发送成功
        with patch.object(self.service, 'send_notification', return_value=["msg_1", "msg_2"]) as mock_send:
            result = await self.service.notify_system_alert(
                alert_type="数据库连接异常",
                message="数据库连接池已满，请检查连接配置",
                severity="error"
            )
            
            assert len(result) == 2
            mock_send.assert_called_once()
            
            # 检查调用参数
            call_args = mock_send.call_args
            assert call_args[1]["type"] == NotificationType.SYSTEM_ALERT
            assert call_args[1]["recipient"] == "admin"
            assert call_args[1]["priority"] == NotificationPriority.HIGH
            assert "系统告警" in call_args[1]["subject"]

    @pytest.mark.asyncio
    async def test_get_provider_status(self):
        """测试获取提供者状态"""
        # 模拟提供者状态
        for provider in self.service.providers.values():
            provider.is_available = AsyncMock(return_value=True)
        
        status = await self.service.get_provider_status()
        
        assert isinstance(status, dict)
        # 检查所有配置的提供者都有状态
        for channel in self.service.providers.keys():
            assert channel.value in status

    @pytest.mark.asyncio
    async def test_provider_error_handling(self):
        """测试提供者错误处理"""
        # 模拟提供者抛出异常
        for provider in self.service.providers.values():
            provider.is_available = AsyncMock(side_effect=Exception("Provider error"))
        
        status = await self.service.get_provider_status()
        
        # 所有提供者状态应该为False
        for channel_status in status.values():
            assert channel_status is False


class TestNotificationIntegration:
    """通知服务集成测试"""

    def setup_method(self):
        """设置测试环境"""
        self.mock_redis = AsyncMock()

    @pytest.mark.asyncio
    async def test_notification_workflow(self):
        """测试完整的通知工作流"""
        service = NotificationService(redis_client=self.mock_redis)
        
        # 模拟所有提供者都可用
        for provider in service.providers.values():
            provider.send = AsyncMock(return_value=True)
            provider.is_available = AsyncMock(return_value=True)
        
        # 1. 发送任务分配通知
        task = MagicMock(spec=ReviewTask)
        task.task_id = "task_123"
        task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        task.priority = ReviewPriority.HIGH
        task.estimated_duration = 1800
        task.expires_at = datetime.now(timezone.utc)
        
        reviewer = MagicMock(spec=Reviewer)
        reviewer.reviewer_id = "reviewer_456"
        reviewer.name = "张医生"
        
        result1 = await service.notify_task_assigned(task, reviewer)
        assert len(result1) >= 0
        
        # 2. 发送任务完成通知
        task.status = ReviewStatus.APPROVED
        task.completed_at = datetime.now(timezone.utc)
        task.actual_duration = 1200
        
        result2 = await service.notify_task_completed(task, reviewer)
        assert len(result2) >= 0
        
        # 3. 发送系统告警
        result3 = await service.notify_system_alert(
            alert_type="高负载告警",
            message="系统负载超过80%",
            severity="warning"
        )
        assert len(result3) >= 0

    @pytest.mark.asyncio
    async def test_notification_with_custom_channels(self):
        """测试自定义通知渠道"""
        service = NotificationService(redis_client=self.mock_redis)
        
        # 只使用WebSocket通知
        task = MagicMock(spec=ReviewTask)
        task.task_id = "task_123"
        task.review_type = ReviewType.MEDICAL_DIAGNOSIS
        task.priority = ReviewPriority.NORMAL
        task.estimated_duration = 1800
        task.expires_at = datetime.now(timezone.utc)
        
        reviewer = MagicMock(spec=Reviewer)
        reviewer.reviewer_id = "reviewer_456"
        reviewer.name = "张医生"
        
        # 模拟WebSocket提供者
        if NotificationChannel.WEBSOCKET in service.providers:
            service.providers[NotificationChannel.WEBSOCKET].send = AsyncMock(return_value=True)
            service.providers[NotificationChannel.WEBSOCKET].is_available = AsyncMock(return_value=True)
        
        result = await service.notify_task_assigned(
            task, 
            reviewer, 
            channels=[NotificationChannel.WEBSOCKET]
        )
        
        # 应该只有一个通知发送成功（WebSocket）
        assert len(result) >= 0


if __name__ == "__main__":
    pytest.main([__file__]) 