"""
test_repository - 索克生活项目模块
"""

    from aiokafka.errors import KafkaError
from config.settings import Settings
from internal.model.message import Message
from internal.model.topic import Topic
from internal.repository.message_repository import KafkaMessageRepository
from internal.repository.topic_repository import TopicRepository
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import pytest

"""
存储库层单元测试
"""

try:
except ImportError:
    # 模拟KafkaError用于测试
    class KafkaError(Exception):
        pass



@pytest.fixture
def mock_settings():
    """创建模拟配置"""
    settings = MagicMock(spec=Settings)
    settings.kafka.bootstrap_servers = ["localhost:9092"]
    settings.kafka.topic_prefix = "test_"
    return settings


@pytest.fixture
def kafka_repository(mock_settings):
    """创建Kafka消息存储库"""
    return KafkaMessageRepository(mock_settings)


class TestKafkaMessageRepository:
    """Kafka消息存储库测试类"""
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, kafka_repository):
        """测试成功初始化"""
        with patch('aiokafka.AIOKafkaProducer') as mock_producer:
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance
            
            await kafka_repository.initialize()
            
            assert kafka_repository.producer is not None
            mock_producer_instance.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_success(self, kafka_repository):
        """测试成功关闭"""
        # 设置模拟生产者
        kafka_repository.producer = AsyncMock()
        
        await kafka_repository.close()
        
        kafka_repository.producer.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_message_success(self, kafka_repository):
        """测试成功保存消息"""
        # 设置模拟生产者
        kafka_repository.producer = AsyncMock()
        kafka_repository.producer.send_and_wait.return_value = MagicMock()
        
        # 创建测试消息
        message = Message(
            message_id="test-id",
            topic="test-topic",
            payload="test payload",
            attributes={"key": "value"},
            publish_time=1234567890,
            publisher_id="test-publisher"
        )
        
        # 调用被测方法
        result = await kafka_repository.save_message(message)
        
        # 验证结果
        assert result is True
        kafka_repository.producer.send_and_wait.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_message_failure(self, kafka_repository):
        """测试保存消息失败"""
        # 设置模拟生产者抛出异常
        kafka_repository.producer = AsyncMock()
        kafka_repository.producer.send_and_wait.side_effect = KafkaError("Connection failed")
        
        # 创建测试消息
        message = Message(
            message_id="test-id",
            topic="test-topic",
            payload="test payload",
            attributes={},
            publish_time=1234567890,
            publisher_id="test-publisher"
        )
        
        # 调用被测方法
        result = await kafka_repository.save_message(message)
        
        # 验证结果
        assert result is False
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self, kafka_repository):
        """测试断路器打开状态"""
        # 模拟断路器打开
        kafka_repository._circuit_open = True
        kafka_repository._last_failure_time = 1234567890
        
        # 创建测试消息
        message = Message(
            message_id="test-id",
            topic="test-topic",
            payload="test payload",
            attributes={},
            publish_time=1234567890,
            publisher_id="test-publisher"
        )
        
        # 调用被测方法
        result = await kafka_repository.save_message(message)
        
        # 验证结果
        assert result is False
    
    def test_get_kafka_topic(self, kafka_repository):
        """测试获取Kafka主题名称"""
        topic_name = kafka_repository._get_kafka_topic("user-events")
        assert topic_name == "test_user-events"
    
    def test_check_circuit_breaker_closed(self, kafka_repository):
        """测试断路器关闭状态"""
        kafka_repository._circuit_open = False
        result = kafka_repository._check_circuit_breaker()
        assert result is False
    
    def test_update_circuit_breaker_success(self, kafka_repository):
        """测试断路器成功更新"""
        kafka_repository._failure_count = 3
        kafka_repository._circuit_open = True
        
        kafka_repository._update_circuit_breaker(True)
        
        assert kafka_repository._failure_count == 0
        assert kafka_repository._circuit_open is False
    
    def test_update_circuit_breaker_failure(self, kafka_repository):
        """测试断路器失败更新"""
        kafka_repository._failure_count = 4
        kafka_repository._circuit_open = False
        
        kafka_repository._update_circuit_breaker(False)
        
        assert kafka_repository._failure_count == 5
        assert kafka_repository._circuit_open is True


class TestTopicRepository:
    """主题存储库测试类"""
    
    @pytest.fixture
    def topic_repository(self, mock_settings):
        """创建主题存储库"""
        return TopicRepository(mock_settings)
    
    @pytest.mark.asyncio
    async def test_create_topic_success(self, topic_repository):
        """测试成功创建主题"""
        topic = Topic(
            name="test-topic",
            description="Test Topic",
            properties={"key": "value"},
            creation_time=1234567890,
            partition_count=3,
            retention_hours=24
        )
        
        with patch.object(topic_repository, '_store_topic') as mock_store:
            mock_store.return_value = True
            
            result = await topic_repository.create_topic(topic)
            
            assert result == topic
            mock_store.assert_called_once_with(topic)
    
    @pytest.mark.asyncio
    async def test_create_topic_failure(self, topic_repository):
        """测试创建主题失败"""
        topic = Topic(
            name="test-topic",
            description="Test Topic",
            properties={},
            creation_time=1234567890,
            partition_count=1,
            retention_hours=24
        )
        
        with patch.object(topic_repository, '_store_topic') as mock_store:
            mock_store.return_value = False
            
            with pytest.raises(Exception):
                await topic_repository.create_topic(topic)
    
    @pytest.mark.asyncio
    async def test_get_topic_success(self, topic_repository):
        """测试成功获取主题"""
        expected_topic = Topic(
            name="test-topic",
            description="Test Topic",
            properties={},
            creation_time=1234567890,
            partition_count=1,
            retention_hours=24
        )
        
        with patch.object(topic_repository, '_load_topic') as mock_load:
            mock_load.return_value = expected_topic
            
            result = await topic_repository.get_topic("test-topic")
            
            assert result == expected_topic
            mock_load.assert_called_once_with("test-topic")
    
    @pytest.mark.asyncio
    async def test_get_topic_not_found(self, topic_repository):
        """测试获取不存在的主题"""
        with patch.object(topic_repository, '_load_topic') as mock_load:
            mock_load.return_value = None
            
            result = await topic_repository.get_topic("non-existent")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_topic_success(self, topic_repository):
        """测试成功删除主题"""
        with patch.object(topic_repository, '_remove_topic') as mock_remove:
            mock_remove.return_value = True
            
            result = await topic_repository.delete_topic("test-topic")
            
            assert result is True
            mock_remove.assert_called_once_with("test-topic")
    
    @pytest.mark.asyncio
    async def test_list_topics_success(self, topic_repository):
        """测试成功列出主题"""
        expected_topics = [
            Topic(
                name=f"topic-{i}",
                description=f"Topic {i}",
                properties={},
                creation_time=1234567890,
                partition_count=1,
                retention_hours=24
            )
            for i in range(3)
        ]
        
        with patch.object(topic_repository, '_load_all_topics') as mock_load_all:
            mock_load_all.return_value = expected_topics
            
            topics, next_token, total_count = await topic_repository.list_topics(
                page_size=10, page_token=None
            )
            
            assert len(topics) == 3
            assert next_token is None
            assert total_count == 3
    
    @pytest.mark.asyncio
    async def test_list_topics_with_pagination(self, topic_repository):
        """测试分页列出主题"""
        all_topics = [
            Topic(
                name=f"topic-{i}",
                description=f"Topic {i}",
                properties={},
                creation_time=1234567890,
                partition_count=1,
                retention_hours=24
            )
            for i in range(15)
        ]
        
        with patch.object(topic_repository, '_load_all_topics') as mock_load_all:
            mock_load_all.return_value = all_topics
            
            topics, next_token, total_count = await topic_repository.list_topics(
                page_size=10, page_token=None
            )
            
            assert len(topics) == 10
            assert next_token is not None
            assert total_count == 15


@pytest.mark.asyncio
async def test_repository_integration():
    """存储库集成测试"""
    # 这里可以添加存储库之间的集成测试
    pass 