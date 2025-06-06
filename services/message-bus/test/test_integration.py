"""
test_integration - 索克生活项目模块
"""

    from internal.error.error_handler import ErrorHandler
    from internal.error.error_handler import ErrorHandler, CircuitBreakerError
    from internal.error.error_handler import ErrorHandler, InfrastructureError
    from internal.error.error_handler import ErrorHandler, MessageBusError
    from internal.error.error_handler import ErrorHandler, RateLimitError
    from internal.error.error_handler import ErrorHandler, TopicError
    from internal.error.error_handler import ErrorHandler, ValidationError
    from internal.model.message import Message
    from internal.model.topic import Topic
    from internal.performance.optimizer import (
    from internal.performance.optimizer import MessageBatcher
    from internal.performance.optimizer import PerformanceOptimizer
    from internal.performance.optimizer import PerformanceOptimizer, MessageBatcher
    from internal.reliability.retry_handler import DeadLetterQueue, RetryHandler
    from internal.reliability.retry_handler import DeadLetterQueue, RetryHandler, RetryableMessage, RetryConfig
from pkg.client.message_bus_client import MessageBusClient
from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import json
import logging
import os
import pytest
import sys
import time
import unittest

#!/usr/bin/env python3
"""
消息总线服务集成测试
"""

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试配置
TEST_ENDPOINT = os.getenv("TEST_ENDPOINT", "localhost:50051")
TEST_AUTH_TOKEN = os.getenv("TEST_AUTH_TOKEN", None)

class IntegrationTest(unittest.IsolatedAsyncioTestCase):
    """消息总线服务集成测试"""
    
    async def asyncSetUp(self):
        """测试准备"""
        self.client = MessageBusClient(
            endpoint=TEST_ENDPOINT,
            auth_token=TEST_AUTH_TOKEN,
            timeout=10
        )
        
        # 接收到的消息列表
        self.received_messages = []
        
        # 测试主题
        self.test_topic = f"integration-test-{int(asyncio.get_event_loop().time())}"
        
        # 创建测试主题
        try:
            topic_info = self.client.create_topic(
                name=self.test_topic,
                description="集成测试主题",
                partition_count=1,
                retention_hours=1
            )
            logger.info(f"创建测试主题: {topic_info['name']}")
        except Exception as e:
            logger.error(f"创建测试主题失败: {str(e)}")
            raise
    
    async def asyncTearDown(self):
        """测试清理"""
        # 删除测试主题
        try:
            if hasattr(self, 'test_topic'):
                success = self.client.delete_topic(self.test_topic)
                logger.info(f"删除测试主题: {self.test_topic}, 成功: {success}")
        except Exception as e:
            logger.warning(f"删除测试主题失败: {str(e)}")
        
        # 关闭客户端
        if hasattr(self, 'client'):
            self.client.close()
    
    async def message_handler(self, message: Dict[str, Any]):
        """消息处理回调"""
        logger.info(f"收到消息: {message['id']}")
        self.received_messages.append(message)
    
    async def test_publish_and_subscribe(self):
        """测试消息发布和订阅"""
        # 订阅主题
        subscription = self.client.subscribe(
            topic=self.test_topic,
            callback=self.message_handler
        )
        
        # 等待一下，确保订阅已建立
        await asyncio.sleep(1)
        
        # 发布测试消息
        test_payload = {"test": "data", "value": 123}
        test_attributes = {"priority": "high", "source": "integration-test"}
        
        # 发布消息
        result = self.client.publish(
            topic=self.test_topic,
            payload=test_payload,
            attributes=test_attributes
        )
        
        logger.info(f"发布消息: {result['message_id']}")
        
        # 等待接收消息
        retry_count = 0
        while len(self.received_messages) == 0 and retry_count < 10:
            await asyncio.sleep(1)
            retry_count += 1
        
        # 取消订阅
        subscription.unsubscribe()
        
        # 验证已接收到消息
        self.assertGreater(len(self.received_messages), 0, "未接收到消息")
        
        # 验证消息内容
        message = self.received_messages[0]
        payload = json.loads(message["payload"].decode('utf-8'))
        
        self.assertEqual(payload, test_payload, "消息内容不匹配")
        
        # 验证消息属性
        for key, value in test_attributes.items():
            self.assertEqual(message["attributes"].get(key), value, f"消息属性 {key} 不匹配")
    
    async def test_topic_management(self):
        """测试主题管理功能"""
        # 创建另一个测试主题
        test_topic2 = f"{self.test_topic}-2"
        
        # 创建主题
        topic_info = self.client.create_topic(
            name=test_topic2,
            description="另一个测试主题",
            properties={"purpose": "test"},
            partition_count=2,
            retention_hours=2
        )
        
        # 验证创建结果
        self.assertEqual(topic_info["name"], test_topic2)
        self.assertEqual(topic_info["description"], "另一个测试主题")
        self.assertEqual(topic_info["properties"], {"purpose": "test"})
        
        # 获取主题信息
        topic_info = self.client.get_topic(test_topic2)
        
        # 验证主题信息
        self.assertEqual(topic_info["name"], test_topic2)
        self.assertEqual(topic_info["partition_count"], 2)
        
        # 列出主题
        topics, next_page_token, total_count = self.client.list_topics()
        
        # 验证主题列表
        self.assertGreaterEqual(total_count, 2, "主题总数不正确")
        
        # 检查测试主题是否在列表中
        topic_names = [t["name"] for t in topics]
        self.assertIn(self.test_topic, topic_names)
        self.assertIn(test_topic2, topic_names)
        
        # 删除主题
        success = self.client.delete_topic(test_topic2)
        self.assertTrue(success)
        
        # 验证主题已删除
        with self.assertRaises(ValueError):
            self.client.get_topic(test_topic2)
    
    async def test_filtered_subscription(self):
        """测试消息过滤订阅"""
        # 订阅主题，设置过滤条件
        subscription = self.client.subscribe(
            topic=self.test_topic,
            callback=self.message_handler,
            filter_attributes={"priority": "high"}
        )
        
        # 等待订阅建立
        await asyncio.sleep(1)
        
        # 清空接收消息列表
        self.received_messages = []
        
        # 发布高优先级消息
        self.client.publish(
            topic=self.test_topic,
            payload={"type": "important"},
            attributes={"priority": "high"}
        )
        
        # 发布普通优先级消息
        self.client.publish(
            topic=self.test_topic,
            payload={"type": "normal"},
            attributes={"priority": "normal"}
        )
        
        # 等待接收消息
        await asyncio.sleep(3)
        
        # 取消订阅
        subscription.unsubscribe()
        
        # 验证只接收到高优先级消息
        self.assertEqual(len(self.received_messages), 1, "应该只接收一条消息")
        
        # 验证消息类型
        message = self.received_messages[0]
        payload = json.loads(message["payload"].decode('utf-8'))
        self.assertEqual(payload["type"], "important", "接收到的不是高优先级消息")
    
    async def test_health_check(self):
        """测试健康检查"""
        status = self.client.health_check()
        self.assertEqual(status, "SERVING", "服务健康状态不正常")

@pytest.mark.asyncio
async def test_message_flow_integration():
    """测试完整的消息流程集成"""
    
    # 创建组件
    error_handler = ErrorHandler()
    dlq = DeadLetterQueue(max_size=100)
    retry_handler = RetryHandler(dlq)
    performance_optimizer = PerformanceOptimizer()
    
    # 创建测试消息
    message = Message(
        message_id="integration-test-1",
        topic="test-integration",
        payload="Integration test payload",
        attributes={"test": "true"},
        publish_time=int(time.time()),
        publisher_id="integration-test-publisher"
    )
    
    # 验证消息创建
    assert message.message_id == "integration-test-1"
    assert message.topic == "test-integration"
    
    # 测试错误处理
    try:
        raise ValueError("Test integration error")
    except Exception as e:
        handled_error = error_handler.handle_error(e, component="integration-test")
        assert handled_error is not None
    
    # 测试性能优化器初始化
    assert performance_optimizer.memory_manager is not None
    assert performance_optimizer.connection_pool is not None
    
    # 测试重试处理器
    assert retry_handler.dead_letter_queue == dlq
    assert not retry_handler.running

@pytest.mark.asyncio
async def test_error_handling_with_retry():
    """测试错误处理与重试机制的集成"""
    
    # 创建组件
    error_handler = ErrorHandler()
    dlq = DeadLetterQueue(max_size=10)
    retry_handler = RetryHandler(dlq)
    
    # 创建测试消息
    message = Message(
        message_id="retry-test-1",
        topic="test-retry",
        payload="Retry test payload",
        attributes={},
        publish_time=int(time.time()),
        publisher_id="retry-test-publisher"
    )
    
    # 创建重试配置
    retry_config = RetryConfig(max_attempts=3, initial_delay=1.0)
    
    # 创建可重试消息
    retryable_message = RetryableMessage(
        original_message=message,
        retry_config=retry_config,
        attempts=[],
        next_retry_time=time.time() + 1,
        created_at=time.time()
    )
    
    # 添加到死信队列
    await dlq.add_message(retryable_message)
    
    # 验证消息在队列中
    stats = await dlq.get_stats()
    assert stats['total_messages'] == 1
    
    # 测试错误处理
    error = ValueError("Retry test error")
    handled_error = error_handler.handle_error(error, component="retry-test")
    assert isinstance(handled_error, MessageBusError)

@pytest.mark.asyncio
async def test_performance_monitoring_integration():
    """测试性能监控集成"""
        PerformanceOptimizer, MemoryManager, ConnectionPool,
        MessageBatcher, LatencyTracker, ThroughputCounter
    )
    
    # 创建性能优化器
    optimizer = PerformanceOptimizer()
    
    # 测试内存管理器
    memory_manager = optimizer.memory_manager
    assert memory_manager.max_memory_mb > 0
    
    # 测试连接池
    connection_pool = optimizer.connection_pool
    stats = connection_pool.get_stats()
    assert 'max' in stats
    assert 'active' in stats
    
    # 测试延迟跟踪器
    latency_tracker = optimizer.latency_tracker
    latency_tracker.record_latency(10.0)
    latency_tracker.record_latency(20.0)
    latency_tracker.record_latency(30.0)
    
    percentiles = latency_tracker.get_percentiles()
    assert 'p50' in percentiles
    assert 'p95' in percentiles
    assert 'p99' in percentiles
    
    # 测试吞吐量计数器
    throughput_counter = optimizer.throughput_counter
    for _ in range(5):
        throughput_counter.increment()
    
    rate = throughput_counter.get_rate()
    assert rate >= 0

@pytest.mark.asyncio
async def test_message_batching_integration():
    """测试消息批处理集成"""
    
    processed_batches = []
    
    async def batch_processor(batch):
        """批处理器"""
        processed_batches.append(batch)
        # 模拟处理时间
        await asyncio.sleep(0.01)
    
    # 创建批处理器
    batcher = MessageBatcher(
        batch_size=3,
        batch_timeout=0.5,
        processor=batch_processor
    )
    
    # 添加消息
    messages = ["msg1", "msg2", "msg3", "msg4", "msg5"]
    for msg in messages:
        await batcher.add_message(msg)
    
    # 等待批处理完成
    await asyncio.sleep(0.1)
    
    # 验证批处理结果
    assert len(processed_batches) >= 1
    
    # 验证第一个批次
    first_batch = processed_batches[0]
    assert len(first_batch) == 3
    assert first_batch == ["msg1", "msg2", "msg3"]

@pytest.mark.asyncio
async def test_circuit_breaker_integration():
    """测试断路器集成"""
    
    error_handler = ErrorHandler()
    
    # 模拟断路器错误
    circuit_error = CircuitBreakerError("kafka")
    handled_error = error_handler.handle_error(circuit_error, component="kafka")
    
    assert "kafka" in handled_error.message
    assert handled_error.details["component"] == "kafka"

@pytest.mark.asyncio
async def test_rate_limiting_integration():
    """测试限流集成"""
    
    error_handler = ErrorHandler()
    
    # 模拟限流错误
    rate_limit_error = RateLimitError(limit=100, window=60)
    handled_error = error_handler.handle_error(rate_limit_error, component="rate-limiter")
    
    assert "100 requests per 60 seconds" in handled_error.message
    assert handled_error.details["limit"] == 100
    assert handled_error.details["window"] == 60

@pytest.mark.asyncio
async def test_topic_management_integration():
    """测试主题管理集成"""
    
    error_handler = ErrorHandler()
    
    # 创建主题
    topic = Topic(
        name="integration-test-topic",
        description="Integration Test Topic",
        properties={"test": "true"},
        creation_time=int(time.time()),
        partition_count=3,
        retention_hours=24
    )
    
    assert topic.name == "integration-test-topic"
    assert topic.partition_count == 3
    
    # 测试主题错误处理
    topic_error = TopicError("Topic not found", topic_name="missing-topic")
    handled_error = error_handler.handle_error(topic_error, component="topic-manager")
    
    assert "Topic not found" in handled_error.message
    assert handled_error.details["topic_name"] == "missing-topic"

@pytest.mark.asyncio
async def test_message_validation_integration():
    """测试消息验证集成"""
    
    error_handler = ErrorHandler()
    
    # 创建有效消息
    valid_message = Message(
        message_id="valid-msg-1",
        topic="valid-topic",
        payload="Valid payload",
        attributes={"valid": "true"},
        publish_time=int(time.time()),
        publisher_id="valid-publisher"
    )
    
    assert valid_message.message_id == "valid-msg-1"
    assert valid_message.topic == "valid-topic"
    
    # 测试验证错误
    validation_error = ValidationError("Invalid message format", field="payload")
    handled_error = error_handler.handle_error(validation_error, component="validator")
    
    assert "Invalid message format" in handled_error.message
    assert handled_error.details["field"] == "payload"

@pytest.mark.asyncio
async def test_infrastructure_monitoring_integration():
    """测试基础设施监控集成"""
    
    error_handler = ErrorHandler()
    optimizer = PerformanceOptimizer()
    
    # 测试基础设施错误
    infra_error = InfrastructureError("Database connection failed", component="postgres")
    handled_error = error_handler.handle_error(infra_error, component="infrastructure")
    
    assert "Database connection failed" in handled_error.message
    assert handled_error.details["component"] == "postgres"
    
    # 测试性能监控
    metrics = await optimizer.get_current_metrics()
    assert metrics is not None
    assert hasattr(metrics, 'cpu_usage')
    assert hasattr(metrics, 'memory_usage')

@pytest.mark.asyncio
async def test_end_to_end_message_processing():
    """端到端消息处理测试"""
    
    # 创建所有组件
    error_handler = ErrorHandler()
    dlq = DeadLetterQueue(max_size=100)
    retry_handler = RetryHandler(dlq)
    optimizer = PerformanceOptimizer()
    
    processed_messages = []
    
    async def message_processor(batch):
        """消息处理器"""
        for msg in batch:
            processed_messages.append(msg)
    
    batcher = MessageBatcher(
        batch_size=2,
        batch_timeout=0.5,
        processor=message_processor
    )
    
    # 创建测试消息
    messages = []
    for i in range(5):
        message = Message(
            message_id=f"e2e-msg-{i}",
            topic="e2e-test",
            payload=f"End-to-end test message {i}",
            attributes={"batch": "true"},
            publish_time=int(time.time()),
            publisher_id="e2e-test-publisher"
        )
        messages.append(message)
    
    # 处理消息
    for message in messages:
        # 记录延迟
        optimizer.latency_tracker.record_latency(1.0)
        
        # 增加吞吐量计数
        optimizer.throughput_counter.increment()
        
        # 添加到批处理器
        await batcher.add_message(message)
    
    # 等待处理完成
    await asyncio.sleep(1.0)
    
    # 验证结果
    assert len(processed_messages) == 5
    
    # 验证性能指标
    percentiles = optimizer.latency_tracker.get_percentiles()
    assert 'p50' in percentiles
    
    rate = optimizer.throughput_counter.get_rate()
    assert rate >= 0
    
    # 验证错误处理器正常工作
    test_error = ValueError("E2E test error")
    handled_error = error_handler.handle_error(test_error, component="e2e-test")
    assert handled_error is not None

@pytest.mark.asyncio
async def test_concurrent_processing():
    """并发处理测试"""
    
    optimizer = PerformanceOptimizer()
    processed_count = 0
    
    async def concurrent_processor(batch):
        """并发处理器"""
        nonlocal processed_count
        processed_count += len(batch)
        await asyncio.sleep(0.01)  # 模拟处理时间
    
    batcher = MessageBatcher(
        batch_size=5,
        batch_timeout=0.1,
        processor=concurrent_processor
    )
    
    # 并发添加消息
    tasks = []
    for i in range(20):
        task = asyncio.create_task(batcher.add_message(f"concurrent-msg-{i}"))
        tasks.append(task)
    
    # 等待所有任务完成
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.5)  # 等待批处理完成
    
    # 验证所有消息都被处理
    assert processed_count == 20

# 运行测试
if __name__ == "__main__":
    unittest.main() 