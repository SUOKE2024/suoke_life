import asyncio
import logging
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable, Union

from internal.model.message import Message
from internal.model.topic import Topic
from internal.repository.topic_repository import TopicRepository
from internal.repository.message_repository import MessageRepository

logger = logging.getLogger(__name__)

class MessageService:
    """
    消息服务实现，提供消息发布和订阅功能
    """
    
    def __init__(
        self, 
        message_repository: MessageRepository,
        topic_repository: TopicRepository
    ):
        """
        初始化消息服务
        
        Args:
            message_repository: 消息存储库
            topic_repository: 主题存储库
        """
        self.message_repository = message_repository
        self.topic_repository = topic_repository
        self._subscriptions: Dict[str, List[Dict[str, Any]]] = {}
    
    async def publish_message(
        self, 
        topic: str, 
        payload: Union[bytes, str, Dict[str, Any]], 
        attributes: Optional[Dict[str, str]] = None,
        publisher_id: Optional[str] = None
    ) -> Message:
        """
        发布消息到指定主题
        
        Args:
            topic: 主题名称
            payload: 消息内容
            attributes: 消息属性
            publisher_id: 发布者ID
        
        Returns:
            Message: 已发布的消息
            
        Raises:
            ValueError: 如果主题不存在
        """
        # 检查主题是否存在
        topic_exists = await self.topic_repository.topic_exists(topic)
        if not topic_exists:
            raise ValueError(f"主题不存在: {topic}")
        
        # 创建消息
        message = Message(
            topic=topic,
            payload=payload,
            attributes=attributes,
            publisher_id=publisher_id
        )
        
        # 持久化消息
        await self.message_repository.save_message(message)
        
        # 通知订阅者
        await self._notify_subscribers(message)
        
        logger.info(f"发布消息: {message}")
        return message
    
    async def create_topic(
        self, 
        name: str, 
        description: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None,
        partition_count: int = 3,
        retention_hours: int = 24
    ) -> Topic:
        """
        创建新主题
        
        Args:
            name: 主题名称
            description: 主题描述
            properties: 主题属性
            partition_count: 分区数量
            retention_hours: 消息保留时间(小时)
        
        Returns:
            Topic: 已创建的主题
            
        Raises:
            ValueError: 如果主题名称无效或已存在
        """
        # 验证主题名称
        if not Topic.validate_topic_name(name):
            raise ValueError(f"无效的主题名称: {name}")
        
        # 检查主题是否已存在
        topic_exists = await self.topic_repository.topic_exists(name)
        if topic_exists:
            raise ValueError(f"主题已存在: {name}")
        
        # 创建主题
        topic = Topic(
            name=name,
            description=description,
            properties=properties,
            partition_count=partition_count,
            retention_hours=retention_hours
        )
        
        # 持久化主题
        await self.topic_repository.save_topic(topic)
        
        logger.info(f"创建主题: {topic}")
        return topic
    
    async def delete_topic(self, name: str) -> bool:
        """
        删除主题
        
        Args:
            name: 主题名称
        
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 如果主题不存在
        """
        # 检查主题是否存在
        topic_exists = await self.topic_repository.topic_exists(name)
        if not topic_exists:
            raise ValueError(f"主题不存在: {name}")
        
        # 删除主题
        success = await self.topic_repository.delete_topic(name)
        
        # 删除主题相关的订阅
        if name in self._subscriptions:
            del self._subscriptions[name]
        
        logger.info(f"删除主题: {name}, 成功: {success}")
        return success
    
    async def get_topic(self, name: str) -> Topic:
        """
        获取主题详情
        
        Args:
            name: 主题名称
        
        Returns:
            Topic: 主题对象
            
        Raises:
            ValueError: 如果主题不存在
        """
        topic = await self.topic_repository.get_topic(name)
        if not topic:
            raise ValueError(f"主题不存在: {name}")
        
        return topic
    
    async def list_topics(self, page_size: int = 100, page_token: Optional[str] = None) -> tuple[List[Topic], Optional[str], int]:
        """
        获取主题列表
        
        Args:
            page_size: 每页大小
            page_token: 分页标记
        
        Returns:
            Tuple[List[Topic], Optional[str], int]: 主题列表, 下一页标记, 总主题数
        """
        return await self.topic_repository.list_topics(page_size, page_token)
    
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[Message], Awaitable[None]],
        filter_attributes: Optional[Dict[str, str]] = None,
        subscription_name: Optional[str] = None
    ) -> str:
        """
        订阅主题
        
        Args:
            topic: 主题名称
            callback: 消息处理回调函数
            filter_attributes: 消息过滤属性
            subscription_name: 订阅名称
        
        Returns:
            str: 订阅ID
            
        Raises:
            ValueError: 如果主题不存在
        """
        # 检查主题是否存在
        topic_exists = await self.topic_repository.topic_exists(topic)
        if not topic_exists:
            raise ValueError(f"主题不存在: {topic}")
        
        # 生成订阅ID
        subscription_id = str(uuid.uuid4())
        
        # 创建订阅
        subscription = {
            "id": subscription_id,
            "name": subscription_name or f"sub-{subscription_id[:8]}",
            "callback": callback,
            "filter_attributes": filter_attributes or {}
        }
        
        # 添加到订阅列表
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
        
        self._subscriptions[topic].append(subscription)
        
        logger.info(f"订阅主题 {topic}: {subscription_name or subscription_id}")
        return subscription_id
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """
        取消订阅
        
        Args:
            topic: 主题名称
            subscription_id: 订阅ID
        
        Returns:
            bool: 是否成功取消
        """
        if topic not in self._subscriptions:
            return False
        
        # 查找并移除订阅
        subscriptions = self._subscriptions[topic]
        for i, sub in enumerate(subscriptions):
            if sub["id"] == subscription_id:
                subscriptions.pop(i)
                logger.info(f"取消订阅 {topic}: {subscription_id}")
                return True
        
        return False
    
    async def _notify_subscribers(self, message: Message) -> None:
        """
        通知主题订阅者
        
        Args:
            message: 消息对象
        """
        topic = message.topic
        if topic not in self._subscriptions:
            return
        
        subscribers = self._subscriptions[topic]
        if not subscribers:
            return
        
        # 异步通知所有匹配的订阅者
        notification_tasks = []
        
        for sub in subscribers:
            # 检查消息是否匹配过滤条件
            if self._message_matches_filter(message, sub["filter_attributes"]):
                callback = sub["callback"]
                notification_tasks.append(self._safe_notify(callback, message))
        
        # 并行执行所有通知任务
        if notification_tasks:
            await asyncio.gather(*notification_tasks)
    
    @staticmethod
    def _message_matches_filter(message: Message, filter_attributes: Dict[str, str]) -> bool:
        """
        检查消息是否匹配过滤条件
        
        Args:
            message: 消息对象
            filter_attributes: 过滤属性
        
        Returns:
            bool: 是否匹配
        """
        if not filter_attributes:
            return True
        
        # 所有过滤条件必须匹配
        for key, value in filter_attributes.items():
            if key not in message.attributes or message.attributes[key] != value:
                return False
        
        return True
    
    @staticmethod
    async def _safe_notify(callback: Callable[[Message], Awaitable[None]], message: Message) -> None:
        """
        安全地执行通知回调
        
        Args:
            callback: 回调函数
            message: 消息对象
        """
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"订阅者回调异常: {str(e)}", exc_info=True) 