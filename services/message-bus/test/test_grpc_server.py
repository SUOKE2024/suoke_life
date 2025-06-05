"""
gRPC服务器单元测试
"""

import asyncio
import pytest
import grpc
from unittest.mock import AsyncMock, MagicMock, patch
# from grpc_testing import server_from_dictionary, strict_real_time

from internal.delivery.grpc_server import MessageBusServicer, GrpcServer
from internal.service.message_service import MessageService
from internal.model.message import Message
from internal.model.topic import Topic
from api.grpc.message_bus_pb2 import (
    PublishRequest, PublishResponse,
    CreateTopicRequest, CreateTopicResponse,
    ListTopicsRequest, ListTopicsResponse,
    GetTopicRequest, GetTopicResponse,
    DeleteTopicRequest, DeleteTopicResponse,
    SubscribeRequest, SubscribeResponse,
    HealthCheckRequest, HealthCheckResponse
)
from api.grpc.message_bus_pb2_grpc import MessageBusServiceServicer


@pytest.fixture
def mock_message_service():
    """创建消息服务的模拟对象"""
    service = AsyncMock(spec=MessageService)
    
    # 模拟发布消息
    async def publish_message_mock(topic, payload, attributes=None, publisher_id=None):
        return Message(
            message_id="test-message-id",
            topic=topic,
            payload=payload,
            attributes=attributes or {},
            publish_time=1234567890,
            publisher_id=publisher_id or "test-publisher"
        )
    service.publish_message.side_effect = publish_message_mock
    
    # 模拟创建主题
    async def create_topic_mock(name, description=None, properties=None, partition_count=1, retention_hours=24):
        return Topic(
            name=name,
            description=description or "",
            properties=properties or {},
            creation_time=1234567890,
            partition_count=partition_count,
            retention_hours=retention_hours
        )
    service.create_topic.side_effect = create_topic_mock
    
    # 模拟列出主题
    async def list_topics_mock(page_size=10, page_token=None):
        topics = [
            Topic(
                name=f"topic-{i}",
                description=f"Test Topic {i}",
                properties={},
                creation_time=1234567890,
                partition_count=1,
                retention_hours=24
            )
            for i in range(3)
        ]
        return topics, None, len(topics)
    service.list_topics.side_effect = list_topics_mock
    
    # 模拟获取主题
    async def get_topic_mock(name):
        return Topic(
            name=name,
            description="Test Topic",
            properties={},
            creation_time=1234567890,
            partition_count=1,
            retention_hours=24
        )
    service.get_topic.side_effect = get_topic_mock
    
    # 模拟删除主题
    async def delete_topic_mock(name):
        return True
    service.delete_topic.side_effect = delete_topic_mock
    
    return service


@pytest.fixture
def message_bus_servicer(mock_message_service):
    """创建消息总线服务实现"""
    return MessageBusServicer(mock_message_service)


class TestMessageBusServicer:
    """消息总线gRPC服务测试类"""
    
    @pytest.mark.asyncio
    async def test_publish_message_success(self, message_bus_servicer):
        """测试成功发布消息"""
        # 准备测试数据
        request = PublishRequest(
            topic="test-topic",
            payload=b"test payload",
            attributes={"key": "value"}
        )
        
        # 创建模拟上下文
        context = MagicMock()
        context.get_value.return_value = "test-user"
        
        # 调用被测方法
        response = await message_bus_servicer.PublishMessage(request, context)
        
        # 验证结果
        assert response.success is True
        assert response.message_id == "test-message-id"
        assert response.publish_time == 1234567890
        assert response.error_message == ""
    
    @pytest.mark.asyncio
    async def test_publish_message_failure(self, message_bus_servicer):
        """测试发布消息失败"""
        # 配置模拟服务抛出异常
        message_bus_servicer.message_service.publish_message.side_effect = ValueError("主题不存在")
        
        # 准备测试数据
        request = PublishRequest(
            topic="non-existent-topic",
            payload=b"test payload"
        )
        
        # 创建模拟上下文
        context = MagicMock()
        context.get_value.return_value = "test-user"
        
        # 调用被测方法
        response = await message_bus_servicer.PublishMessage(request, context)
        
        # 验证结果
        assert response.success is False
        assert "主题不存在" in response.error_message
        
        # 验证上下文设置
        context.set_code.assert_called_with(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details.assert_called_with("主题不存在")
    
    @pytest.mark.asyncio
    async def test_create_topic_success(self, message_bus_servicer):
        """测试成功创建主题"""
        # 准备测试数据
        request = CreateTopicRequest(
            name="new-topic",
            description="New Test Topic",
            properties={"key": "value"},
            partition_count=3,
            retention_hours=48
        )
        
        # 创建模拟上下文
        context = MagicMock()
        
        # 调用被测方法
        response = await message_bus_servicer.CreateTopic(request, context)
        
        # 验证结果
        assert response.success is True
        assert response.topic.name == "new-topic"
        assert response.topic.description == "New Test Topic"
        assert response.topic.partition_count == 3
        assert response.topic.retention_hours == 48
        assert response.error_message == ""
    
    @pytest.mark.asyncio
    async def test_list_topics_success(self, message_bus_servicer):
        """测试成功列出主题"""
        # 准备测试数据
        request = ListTopicsRequest(
            page_size=10,
            page_token=""
        )
        
        # 创建模拟上下文
        context = MagicMock()
        
        # 调用被测方法
        response = await message_bus_servicer.ListTopics(request, context)
        
        # 验证结果
        assert len(response.topics) == 3
        assert response.total_count == 3
        assert response.next_page_token == ""
        
        # 验证主题内容
        for i, topic in enumerate(response.topics):
            assert topic.name == f"topic-{i}"
            assert topic.description == f"Test Topic {i}"
    
    @pytest.mark.asyncio
    async def test_get_topic_success(self, message_bus_servicer):
        """测试成功获取主题"""
        # 准备测试数据
        request = GetTopicRequest(name="test-topic")
        
        # 创建模拟上下文
        context = MagicMock()
        
        # 调用被测方法
        response = await message_bus_servicer.GetTopic(request, context)
        
        # 验证结果
        assert response.success is True
        assert response.topic.name == "test-topic"
        assert response.topic.description == "Test Topic"
        assert response.error_message == ""
    
    @pytest.mark.asyncio
    async def test_delete_topic_success(self, message_bus_servicer):
        """测试成功删除主题"""
        # 准备测试数据
        request = DeleteTopicRequest(name="test-topic")
        
        # 创建模拟上下文
        context = MagicMock()
        
        # 调用被测方法
        response = await message_bus_servicer.DeleteTopic(request, context)
        
        # 验证结果
        assert response.success is True
        assert response.error_message == ""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, message_bus_servicer):
        """测试健康检查成功"""
        # 准备测试数据
        request = HealthCheckRequest(service="message-bus")
        
        # 创建模拟上下文
        context = MagicMock()
        
        # 调用被测方法
        response = await message_bus_servicer.HealthCheck(request, context)
        
        # 验证结果
        assert response.status == 1  # SERVING


class TestGrpcServer:
    """gRPC服务器测试类"""
    
    @pytest.fixture
    def mock_settings(self):
        """创建模拟配置"""
        settings = MagicMock()
        settings.server.host = "localhost"
        settings.server.port = 50051
        settings.server.max_workers = 10
        settings.enable_auth = False
        return settings
    
    def test_grpc_server_init(self, mock_settings, mock_message_service):
        """测试gRPC服务器初始化"""
        server = GrpcServer(mock_settings, mock_message_service)
        
        assert server.settings == mock_settings
        assert server.message_service == mock_message_service
        assert server.server is None
        assert server.server_interceptors == []
    
    @pytest.mark.asyncio
    async def test_grpc_server_start_stop(self, mock_settings, mock_message_service):
        """测试gRPC服务器启动和停止"""
        server = GrpcServer(mock_settings, mock_message_service)
        
        # 模拟gRPC服务器
        with patch('grpc.aio.server') as mock_grpc_server:
            mock_server_instance = AsyncMock()
            mock_grpc_server.return_value = mock_server_instance
            
            # 启动服务器
            await server.start()
            
            # 验证服务器已启动
            assert server.server is not None
            mock_server_instance.add_insecure_port.assert_called_once()
            mock_server_instance.start.assert_called_once()
            
            # 停止服务器
            await server.stop()
            
            # 验证服务器已停止
            mock_server_instance.stop.assert_called_once()


@pytest.mark.asyncio
async def test_message_bus_integration():
    """消息总线集成测试"""
    # 这里可以添加更复杂的集成测试
    # 例如测试完整的消息发布-订阅流程
    pass 