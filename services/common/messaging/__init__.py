"""
消息队列模块

提供统一的消息队列接口，包括：
- Kafka消息队列
- RabbitMQ消息队列
- 事件总线
- 消息路由
"""

from typing import Any, Dict, List, Optional, Union

try:
    from .event_bus import EventBus, EventHandler
    from .kafka_client import KafkaClient, KafkaMessageQueue
    from .message_queue import MessageBroker, MessageQueue
    from .rabbitmq_client import RabbitMQClient, RabbitMQMessageQueue

    __all__ = [
        "KafkaClient",
        "KafkaMessageQueue",
        "RabbitMQClient",
        "RabbitMQMessageQueue",
        "MessageQueue",
        "MessageBroker",
        "EventBus",
        "EventHandler",
    ]

except ImportError as e:
    import logging

    logging.warning(f"消息队列模块导入失败: {e}")
    __all__ = []


def main() -> None:
    """主函数 - 用于测试消息队列功能"""
    import asyncio

    async def test_messaging():
        """测试消息队列"""
        try:
            print("消息队列模块测试开始...")

            # 测试Kafka客户端
            try:
                kafka_client = KafkaClient()
                print("Kafka客户端初始化成功")
            except Exception as e:
                print(f"Kafka客户端不可用: {e}")

            # 测试RabbitMQ客户端
            try:
                rabbitmq_client = RabbitMQClient()
                print("RabbitMQ客户端初始化成功")
            except Exception as e:
                print(f"RabbitMQ客户端不可用: {e}")

            # 测试事件总线
            try:
                event_bus = EventBus()
                print("事件总线初始化成功")
            except Exception as e:
                print(f"事件总线不可用: {e}")

            print("消息队列模块测试完成")

        except Exception as e:
            print(f"消息队列模块测试失败: {e}")

    asyncio.run(test_messaging())


if __name__ == "__main__":
    main()
