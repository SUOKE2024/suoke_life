"""
test_message_service - 索克生活项目模块
"""

from datetime import datetime, timedelta
from internal.model.message import Message
from internal.model.topic import Topic
from internal.repository.message_repository import MessageRepository
from internal.service.message_service import MessageService
from unittest.mock import AsyncMock, MagicMock, patch
import json
import logging
import pytest

"""
消息服务单元测试
"""



# 禁用日志输出
logging.disable(logging.CRITICAL)

@pytest.fixture
def mock_repository():
    """创建消息存储库的模拟对象"""
    repository = AsyncMock(spec=MessageRepository)
    
    # 模拟保存消息
    async def save_message_mock(message):
        return True
    repository.save_message.side_effect = save_message_mock
    
    # 模拟获取消息
    async def get_message_mock(topic, message_id):
        if message_id == "not_found":
            return None
        return Message(
            message_id=message_id,
            topic=topic,
            payload="test payload",
            attributes={"key": "value"},
            publish_time=int(datetime.now().timestamp()),
            publisher_id="test-publisher"
        )
    repository.get_message.side_effect = get_message_mock
    
    # 模拟获取主题消息
    async def get_topic_messages_mock(topic, max_count, filter_attributes):
        messages = []
        for i in range(3):
            messages.append(Message(
                message_id=f"msg-{i}",
                topic=topic,
                payload=f"test payload {i}",
                attributes={"key": "value", "index": str(i)},
                publish_time=int(datetime.now().timestamp()),
                publisher_id="test-publisher"
            ))
        return messages
    repository.get_topic_messages.side_effect = get_topic_messages_mock
    
    # 模拟创建主题
    async def create_topic_mock(topic):
        return topic
    repository.create_topic.side_effect = create_topic_mock
    
    # 模拟删除主题
    async def delete_topic_mock(name):
        if name == "non_existing_topic":
            return False
        return True
    repository.delete_topic.side_effect = delete_topic_mock
    
    # 模拟获取主题
    async def get_topic_mock(name):
        if name == "non_existing_topic":
            return None
        return Topic(
            name=name,
            description="Test Topic",
            properties={"key": "value"},
            creation_time=int(datetime.now().timestamp()),
            partition_count=3,
            retention_hours=24
        )
    repository.get_topic.side_effect = get_topic_mock
    
    # 模拟列出主题
    async def list_topics_mock(page_size, page_token):
        topics = []
        for i in range(3):
            topics.append(Topic(
                name=f"topic-{i}",
                description=f"Test Topic {i}",
                properties={"key": "value", "index": str(i)},
                creation_time=int(datetime.now().timestamp()),
                partition_count=3,
                retention_hours=24
            ))
        next_token = None if len(topics) < page_size else "next-page"
        return topics, next_token, len(topics)
    repository.list_topics.side_effect = list_topics_mock
    
    return repository

@pytest.fixture
def mock_settings():
    """创建应用程序配置的模拟对象"""
    settings = MagicMock()
    settings.messages.default_ttl_hours = 24
    settings.debug = False
    return settings

@pytest.fixture
def message_service(mock_repository, mock_settings):
    """创建消息服务实例"""
    return MessageService(mock_repository, mock_settings)

class TestMessageService:
    """消息服务测试类"""
    
    @pytest.mark.asyncio
    async def test_publish_message(self, message_service, mock_repository):
        """测试发布消息功能"""
        # 准备测试数据
        topic = "test-topic"
        payload = json.dumps({"test": "data"})
        attributes = {"source": "test", "priority": "high"}
        publisher_id = "test-client"
        
        # 调用被测方法
        message = await message_service.publish_message(
            topic=topic,
            payload=payload,
            attributes=attributes,
            publisher_id=publisher_id
        )
        
        # 验证结果
        assert message is not None
        assert message.topic == topic
        assert message.payload == payload
        assert "source" in message.attributes
        assert message.attributes["source"] == "high"
        assert message.publisher_id == publisher_id
        
        # 验证存储库调用
        mock_repository.save_message.assert_called_once()
        call_args = mock_repository.save_message.call_args[0][0]
        assert call_args.topic == topic
        assert call_args.payload == payload
    
    @pytest.mark.asyncio
    async def test_publish_message_with_invalid_topic(self, message_service, mock_repository):
        """测试发布消息到无效主题"""
        # 配置模拟行为，模拟主题不存在
        mock_repository.get_topic.side_effect = lambda name: None
        
        # 准备测试数据
        topic = "non_existing_topic"
        payload = json.dumps({"test": "data"})
        
        # 调用被测方法，预期抛出异常
        with pytest.raises(ValueError) as excinfo:
            await message_service.publish_message(
                topic=topic,
                payload=payload
            )
        
        # 验证异常消息
        assert "主题不存在" in str(excinfo.value)
        
        # 验证存储库调用
        mock_repository.save_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_message(self, message_service, mock_repository):
        """测试获取消息功能"""
        # 准备测试数据
        topic = "test-topic"
        message_id = "test-message-id"
        
        # 调用被测方法
        message = await message_service.get_message(topic, message_id)
        
        # 验证结果
        assert message is not None
        assert message.message_id == message_id
        assert message.topic == topic
        
        # 验证存储库调用
        mock_repository.get_message.assert_called_once_with(topic, message_id)
    
    @pytest.mark.asyncio
    async def test_get_message_not_found(self, message_service, mock_repository):
        """测试获取不存在的消息"""
        # 准备测试数据
        topic = "test-topic"
        message_id = "not_found"
        
        # 调用被测方法
        with pytest.raises(ValueError) as excinfo:
            await message_service.get_message(topic, message_id)
        
        # 验证异常消息
        assert "消息不存在" in str(excinfo.value)
        
        # 验证存储库调用
        mock_repository.get_message.assert_called_once_with(topic, message_id)
    
    @pytest.mark.asyncio
    async def test_create_topic(self, message_service, mock_repository):
        """测试创建主题功能"""
        # 准备测试数据
        name = "new-topic"
        description = "New Test Topic"
        properties = {"key": "value"}
        partition_count = 5
        retention_hours = 48
        
        # 配置模拟行为，确保主题不存在
        mock_repository.get_topic.side_effect = lambda topic_name: None if topic_name == name else MagicMock()
        
        # 调用被测方法
        topic = await message_service.create_topic(
            name=name,
            description=description,
            properties=properties,
            partition_count=partition_count,
            retention_hours=retention_hours
        )
        
        # 验证结果
        assert topic is not None
        assert topic.name == name
        assert topic.description == description
        assert topic.properties == properties
        assert topic.partition_count == partition_count
        assert topic.retention_hours == retention_hours
        
        # 验证存储库调用
        mock_repository.create_topic.assert_called_once()
        call_args = mock_repository.create_topic.call_args[0][0]
        assert call_args.name == name
        assert call_args.description == description
    
    @pytest.mark.asyncio
    async def test_create_topic_already_exists(self, message_service, mock_repository):
        """测试创建已存在的主题"""
        # 准备测试数据
        name = "existing-topic"
        
        # 配置模拟行为，模拟主题已存在
        mock_repository.get_topic.side_effect = lambda topic_name: Topic(
            name=topic_name, 
            description="Existing Topic", 
            properties={}, 
            creation_time=int(datetime.now().timestamp()),
            partition_count=3,
            retention_hours=24
        ) if topic_name == name else None
        
        # 调用被测方法，预期抛出异常
        with pytest.raises(ValueError) as excinfo:
            await message_service.create_topic(
                name=name,
                description="New description"
            )
        
        # 验证异常消息
        assert "主题已存在" in str(excinfo.value)
        
        # 验证存储库调用
        mock_repository.create_topic.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_topic(self, message_service, mock_repository):
        """测试删除主题功能"""
        # 准备测试数据
        name = "test-topic"
        
        # 调用被测方法
        success = await message_service.delete_topic(name)
        
        # 验证结果
        assert success is True
        
        # 验证存储库调用
        mock_repository.delete_topic.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_delete_non_existing_topic(self, message_service, mock_repository):
        """测试删除不存在的主题"""
        # 准备测试数据
        name = "non_existing_topic"
        
        # 调用被测方法
        with pytest.raises(ValueError) as excinfo:
            await message_service.delete_topic(name)
        
        # 验证异常消息
        assert "主题不存在" in str(excinfo.value)
        
        # 验证存储库调用
        mock_repository.delete_topic.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_topic(self, message_service, mock_repository):
        """测试获取主题功能"""
        # 准备测试数据
        name = "test-topic"
        
        # 调用被测方法
        topic = await message_service.get_topic(name)
        
        # 验证结果
        assert topic is not None
        assert topic.name == name
        
        # 验证存储库调用
        mock_repository.get_topic.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_get_non_existing_topic(self, message_service, mock_repository):
        """测试获取不存在的主题"""
        # 准备测试数据
        name = "non_existing_topic"
        
        # 调用被测方法
        with pytest.raises(ValueError) as excinfo:
            await message_service.get_topic(name)
        
        # 验证异常消息
        assert "主题不存在" in str(excinfo.value)
        
        # 验证存储库调用
        mock_repository.get_topic.assert_called_once_with(name)
    
    @pytest.mark.asyncio
    async def test_list_topics(self, message_service, mock_repository):
        """测试列出主题功能"""
        # 准备测试数据
        page_size = 10
        page_token = None
        
        # 调用被测方法
        topics, next_token, total_count = await message_service.list_topics(
            page_size=page_size,
            page_token=page_token
        )
        
        # 验证结果
        assert len(topics) == 3
        assert topics[0].name == "topic-0"
        assert topics[1].name == "topic-1"
        assert topics[2].name == "topic-2"
        
        # 验证存储库调用
        mock_repository.list_topics.assert_called_once_with(page_size, page_token)
    
    @pytest.mark.asyncio
    async def test_subscribe(self, message_service, mock_repository):
        """测试订阅功能"""
        # 准备测试数据
        topic = "test-topic"
        callback = AsyncMock()
        filter_attributes = {"key": "value"}
        subscription_name = "test-subscription"
        
        # 调用被测方法
        subscription_id = await message_service.subscribe(
            topic=topic,
            callback=callback,
            filter_attributes=filter_attributes,
            subscription_name=subscription_name
        )
        
        # 验证结果
        assert subscription_id is not None
        assert len(subscription_id) > 0
        
        # 验证存储库调用
        mock_repository.get_topic.assert_called_with(topic)
        
        # 验证订阅处理逻辑
        # 这里我们模拟接收一条消息
        msg = Message(
            message_id="test-message",
            topic=topic,
            payload="test payload",
            attributes={"key": "value"},
            publish_time=int(datetime.now().timestamp())
        )
        
        # 获取订阅处理函数并调用
        subscription = message_service.subscriptions.get(subscription_id)
        assert subscription is not None
        
        # 尝试处理消息
        result = await subscription.process_message(msg)
        assert result is True
        
        # 验证回调被调用
        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args.message_id == "test-message"
        
        # 测试取消订阅
        message_service.unsubscribe(topic, subscription_id)
        assert subscription_id not in message_service.subscriptions
    
    @pytest.mark.asyncio
    async def test_subscribe_nonexisting_topic(self, message_service, mock_repository):
        """测试订阅不存在的主题"""
        # 准备测试数据
        topic = "non_existing_topic"
        callback = AsyncMock()
        
        # 调用被测方法
        with pytest.raises(ValueError) as excinfo:
            await message_service.subscribe(
                topic=topic,
                callback=callback
            )
        
        # 验证异常消息
        assert "主题不存在" in str(excinfo.value)

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 