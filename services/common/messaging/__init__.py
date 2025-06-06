"""
__init__ - 索克生活项目模块
"""

from .kafka_client import KafkaMessageQueue
from .message_queue import (
from .rabbitmq_client import RabbitMQMessageQueue

#!/usr/bin/env python3
"""
消息队列模块
提供对Kafka、RabbitMQ等消息队列的统一抽象
"""

    ConsumerConfig,
    Message,
    MessageHandler,
    MessageQueue,
    ProducerConfig,
    get_message_queue,
)

__all__ = [
    "ConsumerConfig",
    # 实现类
    "KafkaMessageQueue",
    "Message",
    "MessageHandler",
    # 基础类
    "MessageQueue",
    "ProducerConfig",
    "RabbitMQMessageQueue",
    "get_message_queue",
]
