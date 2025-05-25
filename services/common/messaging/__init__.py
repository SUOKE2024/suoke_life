#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息队列模块
提供对Kafka、RabbitMQ等消息队列的统一抽象
"""

from .message_queue import (
    MessageQueue,
    Message,
    MessageHandler,
    ConsumerConfig,
    ProducerConfig,
    get_message_queue
)

from .kafka_client import KafkaMessageQueue
from .rabbitmq_client import RabbitMQMessageQueue

__all__ = [
    # 基础类
    'MessageQueue',
    'Message',
    'MessageHandler',
    'ConsumerConfig',
    'ProducerConfig',
    'get_message_queue',
    
    # 实现类
    'KafkaMessageQueue',
    'RabbitMQMessageQueue'
] 