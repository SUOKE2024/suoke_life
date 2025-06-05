"""
简化的测试文件，用于验证基本功能
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# 基本模型测试
def test_message_model():
    """测试消息模型"""
    from internal.model.message import Message
    
    message = Message(
        message_id="test-id",
        topic="test-topic",
        payload="test payload",
        attributes={"key": "value"},
        publish_time=1234567890,
        publisher_id="test-publisher"
    )
    
    assert message.message_id == "test-id"
    assert message.topic == "test-topic"
    assert message.payload_as_string == "test payload"  # 使用payload_as_string属性
    assert message.attributes == {"key": "value"}
    assert message.publish_time == 1234567890
    assert message.publisher_id == "test-publisher"


def test_topic_model():
    """测试主题模型"""
    from internal.model.topic import Topic
    
    topic = Topic(
        name="test-topic",
        description="Test Topic",
        properties={"key": "value"},
        creation_time=1234567890,
        partition_count=3,
        retention_hours=24
    )
    
    assert topic.name == "test-topic"
    assert topic.description == "Test Topic"
    assert topic.properties == {"key": "value"}
    assert topic.creation_time == 1234567890
    assert topic.partition_count == 3
    assert topic.retention_hours == 24


def test_error_handler():
    """测试错误处理器"""
    from internal.error.error_handler import ErrorHandler, MessageBusError, ErrorCode
    
    handler = ErrorHandler()
    
    # 测试标准异常处理
    error = ValueError("Test error")
    result = handler.handle_error(error, component="test")
    
    assert isinstance(result, MessageBusError)
    assert result.error_code == ErrorCode.VALIDATION_ERROR
    assert "Test error" in result.message


@pytest.mark.asyncio
async def test_retry_handler():
    """测试重试处理器"""
    from internal.reliability.retry_handler import DeadLetterQueue, RetryHandler
    
    dlq = DeadLetterQueue(max_size=100)
    retry_handler = RetryHandler(dlq)
    
    # 测试基本初始化
    assert retry_handler.dead_letter_queue == dlq
    assert len(retry_handler.pending_retries) == 0
    assert retry_handler.running is False


def test_performance_metrics():
    """测试性能指标"""
    from internal.performance.optimizer import PerformanceMetrics
    
    metrics = PerformanceMetrics(
        cpu_usage=50.0,
        memory_usage=60.0,
        memory_available=1024.0,
        active_connections=10,
        message_throughput=100.0,
        latency_p95=50.0,
        latency_p99=100.0,
        error_rate=0.1,
        timestamp=1234567890.0
    )
    
    assert metrics.cpu_usage == 50.0
    assert metrics.memory_usage == 60.0
    assert metrics.active_connections == 10
    assert metrics.message_throughput == 100.0


def test_memory_manager():
    """测试内存管理器"""
    from internal.performance.optimizer import MemoryManager
    
    manager = MemoryManager(max_memory_mb=1024)
    
    assert manager.max_memory_mb == 1024
    assert manager.memory_threshold == 0.8
    assert manager.gc_interval == 30


def test_connection_pool():
    """测试连接池"""
    from internal.performance.optimizer import ConnectionPool
    
    pool = ConnectionPool(max_connections=100)
    
    assert pool.max_connections == 100
    assert pool.active_connections == 0
    
    stats = pool.get_stats()
    assert stats['max'] == 100
    assert stats['active'] == 0


@pytest.mark.asyncio
async def test_message_batcher():
    """测试消息批处理器"""
    from internal.performance.optimizer import MessageBatcher
    
    processed_batches = []
    
    async def processor(batch):
        processed_batches.append(batch)
    
    batcher = MessageBatcher(
        batch_size=3,
        batch_timeout=1.0,
        processor=processor
    )
    
    # 添加消息
    await batcher.add_message("msg1")
    await batcher.add_message("msg2")
    await batcher.add_message("msg3")  # 应该触发批处理
    
    # 等待处理
    await asyncio.sleep(0.1)
    
    assert len(processed_batches) == 1
    assert processed_batches[0] == ["msg1", "msg2", "msg3"]


def test_latency_tracker():
    """测试延迟跟踪器"""
    from internal.performance.optimizer import LatencyTracker
    
    tracker = LatencyTracker(window_size=100)
    
    # 记录一些延迟
    for i in range(10):
        tracker.record_latency(i * 10)
    
    percentiles = tracker.get_percentiles()
    assert 'p50' in percentiles
    assert 'p95' in percentiles
    assert 'p99' in percentiles
    
    average = tracker.get_average()
    assert average == 45.0  # (0+10+20+...+90)/10


def test_throughput_counter():
    """测试吞吐量计数器"""
    from internal.performance.optimizer import ThroughputCounter
    
    counter = ThroughputCounter(window_seconds=60)
    
    # 增加计数
    for _ in range(10):
        counter.increment()
    
    rate = counter.get_rate()
    assert rate >= 0  # 应该有一些速率


def test_retry_config():
    """测试重试配置"""
    from internal.reliability.retry_handler import RetryConfig, RetryStrategy
    
    config = RetryConfig(
        max_attempts=5,
        initial_delay=2.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF
    )
    
    assert config.max_attempts == 5
    assert config.initial_delay == 2.0
    assert config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF


@pytest.mark.asyncio
async def test_dead_letter_queue():
    """测试死信队列"""
    from internal.reliability.retry_handler import DeadLetterQueue, RetryableMessage, RetryConfig
    from internal.model.message import Message
    
    dlq = DeadLetterQueue(max_size=10)
    
    # 创建测试消息
    message = Message(
        message_id="test-id",
        topic="test-topic",
        payload="test payload",
        attributes={},
        publish_time=1234567890,
        publisher_id="test-publisher"
    )
    
    retryable_message = RetryableMessage(
        original_message=message,
        retry_config=RetryConfig(),
        attempts=[],
        next_retry_time=0,
        created_at=1234567890
    )
    
    # 添加到死信队列
    await dlq.add_message(retryable_message)
    
    # 验证
    stats = await dlq.get_stats()
    assert stats['total_messages'] == 1
    
    # 获取消息
    retrieved = await dlq.get_message("test-id")
    assert retrieved is not None
    assert retrieved.original_message.message_id == "test-id"


def test_circuit_breaker_error():
    """测试断路器错误"""
    from internal.error.error_handler import CircuitBreakerError, ErrorCode
    
    error = CircuitBreakerError("kafka")
    
    assert "kafka" in error.message
    assert error.error_code == ErrorCode.INTERNAL_ERROR
    assert error.details["component"] == "kafka"


def test_rate_limit_error():
    """测试限流错误"""
    from internal.error.error_handler import RateLimitError, ErrorCode
    
    error = RateLimitError(limit=100, window=60)
    
    assert "100 requests per 60 seconds" in error.message
    assert error.error_code == ErrorCode.INTERNAL_ERROR
    assert error.details["limit"] == 100
    assert error.details["window"] == 60


def test_validation_error():
    """测试验证错误"""
    from internal.error.error_handler import ValidationError, ErrorCode
    
    error = ValidationError("Invalid field", field="username")
    
    assert error.message == "Invalid field"
    assert error.error_code == ErrorCode.VALIDATION_ERROR
    assert error.details["field"] == "username"


def test_topic_error():
    """测试主题错误"""
    from internal.error.error_handler import TopicError
    
    error = TopicError("Topic not found", topic_name="test-topic")
    
    assert error.message == "Topic not found"
    assert error.details["topic_name"] == "test-topic"


def test_message_error():
    """测试消息错误"""
    from internal.error.error_handler import MessageError
    
    error = MessageError(
        "Message failed", 
        message_id="msg-123", 
        topic="test-topic"
    )
    
    assert error.message == "Message failed"
    assert error.details["message_id"] == "msg-123"
    assert error.details["topic"] == "test-topic"


def test_infrastructure_error():
    """测试基础设施错误"""
    from internal.error.error_handler import InfrastructureError, ErrorSeverity
    
    error = InfrastructureError("Database connection failed", component="postgres")
    
    assert error.message == "Database connection failed"
    assert error.severity == ErrorSeverity.HIGH
    assert error.details["component"] == "postgres" 