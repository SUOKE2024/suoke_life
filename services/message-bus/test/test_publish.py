"""
test_publish - 索克生活项目模块
"""

from internal.model.message import Message
from internal.model.topic import Topic
from internal.repository.message_repository import MessageRepository
from internal.repository.topic_repository import TopicRepository
from internal.service.message_service import MessageService
from typing import Dict, Any, List
import asyncio
import json
import logging
import os
import sys
import unittest

#!/usr/bin/env python3
"""
消息发布功能测试
"""

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockTopicRepository(TopicRepository):
    """模拟的主题存储库"""
    
    def __init__(self):
        """初始化模拟存储库"""
        self.topics = {}
    
    async def save_topic(self, topic: Topic) -> bool:
        """保存主题"""
        self.topics[topic.name] = topic
        return True
    
    async def get_topic(self, name: str) -> Topic:
        """获取主题"""
        return self.topics.get(name)
    
    async def topic_exists(self, name: str) -> bool:
        """检查主题是否存在"""
        return name in self.topics
    
    async def delete_topic(self, name: str) -> bool:
        """删除主题"""
        if name in self.topics:
            del self.topics[name]
            return True
        return False
    
    async def list_topics(self, page_size: int = 100, page_token: str = None) -> tuple:
        """获取主题列表"""
        topics = list(self.topics.values())
        return topics, None, len(topics)

class MockMessageRepository(MessageRepository):
    """模拟的消息存储库"""
    
    def __init__(self):
        """初始化模拟存储库"""
        self.messages = {}
    
    async def save_message(self, message: Message) -> bool:
        """保存消息"""
        topic = message.topic
        if topic not in self.messages:
            self.messages[topic] = []
        self.messages[topic].append(message)
        return True
    
    async def get_message(self, topic: str, message_id: str) -> Message:
        """获取指定消息"""
        if topic in self.messages:
            for msg in self.messages[topic]:
                if msg.message_id == message_id:
                    return msg
        return None
    
    async def get_messages(
        self, 
        topic: str, 
        max_count: int = 100,
        filter_attributes: Dict[str, str] = None,
        start_time: int = None,
        end_time: int = None
    ) -> List[Message]:
        """获取主题消息列表"""
        if topic not in self.messages:
            return []
            
        messages = self.messages[topic]
        result = []
        
        for msg in messages:
            # 检查时间范围
            if start_time and msg.publish_time < start_time:
                continue
            if end_time and msg.publish_time > end_time:
                continue
                
            # 检查属性过滤
            if filter_attributes:
                match = True
                for key, value in filter_attributes.items():
                    if key not in msg.attributes or msg.attributes[key] != value:
                        match = False
                        break
                if not match:
                    continue
                    
            result.append(msg)
            if len(result) >= max_count:
                break
                
        return result

class MessagePublishTest(unittest.TestCase):
    """消息发布测试类"""
    
    def setUp(self):
        """测试准备"""
        self.topic_repo = MockTopicRepository()
        self.message_repo = MockMessageRepository()
        self.message_service = MessageService(
            message_repository=self.message_repo,
            topic_repository=self.topic_repo
        )
        self.received_messages = []
        
        # 创建事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 创建测试主题
        self.loop.run_until_complete(self._create_test_topics())
    
    def tearDown(self):
        """测试清理"""
        # 关闭事件循环
        self.loop.close()
    
    async def _create_test_topics(self):
        """创建测试主题"""
        # 创建测试主题
        test_topics = [
            Topic(
                name="test.events",
                description="测试事件主题",
                partition_count=1,
                retention_hours=1
            ),
            Topic(
                name="test.notifications",
                description="测试通知主题",
                partition_count=1,
                retention_hours=1
            )
        ]
        
        for topic in test_topics:
            await self.topic_repo.save_topic(topic)
    
    async def _message_callback(self, message: Message):
        """消息回调"""
        self.received_messages.append(message)
    
    def test_publish_message(self):
        """测试发布消息"""
        # 测试发布消息
        message_payload = {"event": "test_event", "data": {"key": "value"}}
        message_attributes = {"priority": "high", "source": "test"}
        
        # 运行测试
        async def run_test():
            # 发布消息
            message = await self.message_service.publish_message(
                topic="test.events",
                payload=message_payload,
                attributes=message_attributes
            )
            
            # 验证消息ID
            self.assertIsNotNone(message.message_id)
            
            # 验证消息已保存
            saved_messages = await self.message_repo.get_messages(
                topic="test.events",
                max_count=1
            )
            
            self.assertEqual(len(saved_messages), 1)
            saved_message = saved_messages[0]
            
            # 验证消息属性
            self.assertEqual(saved_message.topic, "test.events")
            self.assertEqual(json.loads(saved_message.payload_as_string), message_payload)
            
            for key, value in message_attributes.items():
                self.assertEqual(saved_message.attributes.get(key), value)
        
        self.loop.run_until_complete(run_test())
    
    def test_subscribe_and_publish(self):
        """测试订阅和发布消息"""
        # 测试发布消息并订阅
        async def run_test():
            # 订阅主题
            subscription_id = await self.message_service.subscribe(
                topic="test.notifications",
                callback=self._message_callback,
                filter_attributes={"priority": "high"}
            )
            
            # 发布消息
            await self.message_service.publish_message(
                topic="test.notifications",
                payload={"notification": "test"},
                attributes={"priority": "high"}
            )
            
            # 发布不匹配过滤条件的消息
            await self.message_service.publish_message(
                topic="test.notifications",
                payload={"notification": "low_priority"},
                attributes={"priority": "low"}
            )
            
            # 等待消息处理
            await asyncio.sleep(0.1)
            
            # 验证只接收到符合过滤条件的消息
            self.assertEqual(len(self.received_messages), 1)
            self.assertEqual(
                json.loads(self.received_messages[0].payload_as_string),
                {"notification": "test"}
            )
            
            # 取消订阅
            result = self.message_service.unsubscribe(
                topic="test.notifications",
                subscription_id=subscription_id
            )
            self.assertTrue(result)
        
        self.loop.run_until_complete(run_test())
    
    def test_publish_to_nonexistent_topic(self):
        """测试发布到不存在的主题"""
        async def run_test():
            # 尝试发布到不存在的主题
            with self.assertRaises(ValueError):
                await self.message_service.publish_message(
                    topic="nonexistent.topic",
                    payload={"test": "data"}
                )
        
        self.loop.run_until_complete(run_test())

if __name__ == "__main__":
    unittest.main() 