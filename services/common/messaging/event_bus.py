"""
event_bus - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable
import asyncio
import json
import logging
import threading

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件驱动架构 - 消息总线
支持事件发布订阅、处理器管理、消费者组等功能
"""


logger = logging.getLogger(__name__)

class EventType(Enum):
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    DIAGNOSIS_COMPLETED = "diagnosis.completed"
    HEALTH_RECORD_UPDATED = "health_record.updated"
    RECOMMENDATION_GENERATED = "recommendation.generated"
    SYSTEM_ALERT = "system.alert"

@dataclass
class Event:
    """事件基类"""

    event_id: str
    event_type: str
    source_service: str
    timestamp: datetime
    data: dict[str, Any]
    correlation_id: str = None
    user_id: str = None
    metadata: dict[str, Any] = None

class EventHandler(ABC):
    """事件处理器抽象基类"""

    @abstractmethod
    async def handle(self, event: Event) -> bool:
        """处理事件"""
        pass

    @abstractmethod
    def get_event_types(self) -> list[str]:
        """获取处理的事件类型"""
        pass

class EventBus:
    """事件总线"""

    def __init__(self, backend: str = 'kafka', config: dict = None):
        self.backend = backend
        self.config = config or {}
        self.subscribers = {}
        self.redis = None
        self.handlers: dict[str, list[EventHandler]] = {}
        self.running = False
        self.consumer_tasks = []

    def register_handler(self, handler: EventHandler):
        """注册事件处理器"""
        for event_type in handler.get_event_types():
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

        logger.info(f"Registered handler for events: {handler.get_event_types()}")

    async def publish(self, topic: str, event: dict):
        """发布事件到指定topic"""
        # TODO: 实现Kafka/RabbitMQ消息发布
        print(f"[EventBus] 发布事件到{topic}: {event}")

    def subscribe(self, topic: str, handler: Callable[[dict], Any]):
        """订阅指定topic的事件，handler为回调函数"""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)
        # TODO: 实现Kafka/RabbitMQ消息消费监听
        print(f"[EventBus] 订阅{topic}")

    def _mock_receive(self, topic: str, event: dict):
        """模拟接收事件，仅用于本地测试"""
        for handler in self.subscribers.get(topic, []):
            threading.Thread(target=handler, args=(event,)).start()

    async def start_consuming(self):
        """开始消费事件"""
        if self.running:
            return

        self.running = True

        # 为每种事件类型创建消费者任务
        for event_type in self.handlers:
            task = asyncio.create_task(self._consume_events(event_type))
            self.consumer_tasks.append(task)

        logger.info(f"Started consuming events for {len(self.handlers)} event types")

    async def stop_consuming(self):
        """停止消费事件"""
        self.running = False

        # 取消所有消费者任务
        for task in self.consumer_tasks:
            task.cancel()

        # 等待任务完成
        await asyncio.gather(*self.consumer_tasks, return_exceptions=True)
        self.consumer_tasks.clear()

        logger.info("Stopped consuming events")

    async def _consume_events(self, event_type: str):
        """消费特定类型的事件"""
        stream_key = f"events:{event_type}"
        consumer_group = f"group:{event_type}"
        consumer_name = f"consumer:{asyncio.current_task().get_name()}"

        try:
            # 创建消费者组
            try:
                await self.redis.xgroup_create(
                    stream_key, consumer_group, id="0", mkstream=True
                )
            except Exception:
                pass  # 组可能已存在

            while self.running:
                try:
                    # 读取事件
                    messages = await self.redis.xreadgroup(
                        consumer_group,
                        consumer_name,
                        {stream_key: ">"},
                        count=10,
                        block=1000,
                    )

                    for _stream, msgs in messages:
                        for msg_id, fields in msgs:
                            await self._process_message(event_type, msg_id, fields)

                except Exception as e:
                    logger.error(f"Error consuming events for {event_type}: {e}")
                    await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"Event consumer for {event_type} cancelled")
        except Exception as e:
            logger.error(f"Event consumer for {event_type} failed: {e}")

    async def _process_message(self, event_type: str, msg_id: str, fields: dict):
        """处理消息"""
        try:
            # 反序列化事件
            event = Event(
                event_id=fields.get("event_id"),
                event_type=fields.get("event_type"),
                source_service=fields.get("source_service"),
                timestamp=datetime.fromisoformat(fields.get("timestamp")),
                data=json.loads(fields.get("data", "{}")),
                correlation_id=fields.get("correlation_id"),
                user_id=fields.get("user_id"),
                metadata=json.loads(fields.get("metadata", "{}")),
            )

            # 调用处理器
            handlers = self.handlers.get(event_type, [])
            for handler in handlers:
                try:
                    success = await handler.handle(event)
                    if not success:
                        logger.warning(f"Handler failed for event {event.event_id}")
                except Exception as e:
                    logger.error(f"Handler error for event {event.event_id}: {e}")

            # 确认消息处理完成
            stream_key = f"events:{event_type}"
            consumer_group = f"group:{event_type}"
            await self.redis.xack(stream_key, consumer_group, msg_id)

        except Exception as e:
            logger.error(f"Failed to process message {msg_id}: {e}")

# 具体事件处理器示例
class DiagnosisEventHandler(EventHandler):
    """诊断事件处理器"""

    def __init__(self, health_data_service, notification_service):
        self.health_data_service = health_data_service
        self.notification_service = notification_service

    def get_event_types(self) -> list[str]:
        return [EventType.DIAGNOSIS_COMPLETED.value]

    async def handle(self, event: Event) -> bool:
        """处理诊断完成事件"""
        try:
            diagnosis_data = event.data
            user_id = event.user_id

            # 保存诊断结果到健康数据服务
            await self.health_data_service.save_diagnosis_result(
                user_id, diagnosis_data
            )

            # 发送通知
            await self.notification_service.send_diagnosis_notification(
                user_id, diagnosis_data
            )

            logger.info(f"Processed diagnosis event for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to handle diagnosis event: {e}")
            return False

class UserEventHandler(EventHandler):
    """用户事件处理器"""

    def __init__(self, user_service, email_service):
        self.user_service = user_service
        self.email_service = email_service

    def get_event_types(self) -> list[str]:
        return [EventType.USER_REGISTERED.value, EventType.USER_LOGIN.value]

    async def handle(self, event: Event) -> bool:
        """处理用户事件"""
        try:
            if event.event_type == EventType.USER_REGISTERED.value:
                return await self._handle_user_registered(event)
            elif event.event_type == EventType.USER_LOGIN.value:
                return await self._handle_user_login(event)

            return True

        except Exception as e:
            logger.error(f"Failed to handle user event: {e}")
            return False

    async def _handle_user_registered(self, event: Event) -> bool:
        """处理用户注册事件"""
        user_data = event.data
        user_id = event.user_id

        # 发送欢迎邮件
        await self.email_service.send_welcome_email(
            user_data.get("email"), user_data.get("username")
        )

        # 创建默认健康档案
        await self.user_service.create_default_health_profile(user_id)

        logger.info(f"Processed user registration for {user_id}")
        return True

    async def _handle_user_login(self, event: Event) -> bool:
        """处理用户登录事件"""
        login_data = event.data
        user_id = event.user_id

        # 更新最后登录时间
        await self.user_service.update_last_login(user_id)

        # 检查异常登录
        if login_data.get("suspicious"):
            await self.email_service.send_security_alert(
                login_data.get("email"), login_data
            )

        logger.info(f"Processed user login for {user_id}")
        return True

class HealthRecordEventHandler(EventHandler):
    """健康记录事件处理器"""

    def __init__(self, analytics_service, recommendation_service):
        self.analytics_service = analytics_service
        self.recommendation_service = recommendation_service

    def get_event_types(self) -> list[str]:
        return [EventType.HEALTH_RECORD_UPDATED.value]

    async def handle(self, event: Event) -> bool:
        """处理健康记录更新事件"""
        try:
            record_data = event.data
            user_id = event.user_id

            # 更新健康分析
            await self.analytics_service.update_health_analysis(user_id, record_data)

            # 生成新的推荐
            recommendations = (
                await self.recommendation_service.generate_recommendations(
                    user_id, record_data
                )
            )

            # 发布推荐生成事件
            if recommendations:
                Event(
                    event_id=f"rec_{event.event_id}",
                    event_type=EventType.RECOMMENDATION_GENERATED.value,
                    source_service="health-record-handler",
                    timestamp=datetime.utcnow(),
                    data={"recommendations": recommendations},
                    user_id=user_id,
                    correlation_id=event.correlation_id,
                )

                # 这里需要访问事件总线实例来发布新事件
                # 在实际实现中，可以通过依赖注入或其他方式获取

            logger.info(f"Processed health record update for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to handle health record event: {e}")
            return False

class SystemAlertEventHandler(EventHandler):
    """系统告警事件处理器"""

    def __init__(self, alert_service, monitoring_service):
        self.alert_service = alert_service
        self.monitoring_service = monitoring_service

    def get_event_types(self) -> list[str]:
        return [EventType.SYSTEM_ALERT.value]

    async def handle(self, event: Event) -> bool:
        """处理系统告警事件"""
        try:
            alert_data = event.data
            severity = alert_data.get("severity", "info")

            # 记录告警
            await self.monitoring_service.record_alert(alert_data)

            # 根据严重程度决定处理方式
            if severity in ["critical", "high"]:
                # 立即通知运维团队
                await self.alert_service.send_immediate_alert(alert_data)
            elif severity == "medium":
                # 发送邮件通知
                await self.alert_service.send_email_alert(alert_data)
            else:
                # 仅记录日志
                logger.info(f"System alert: {alert_data.get('message')}")

            logger.info(f"Processed system alert: {alert_data.get('alert_id')}")
            return True

        except Exception as e:
            logger.error(f"Failed to handle system alert event: {e}")
            return False
