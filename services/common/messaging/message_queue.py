"""
message_queue - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
import asyncio
import json
import logging

#!/usr/bin/env python3
"""
消息队列抽象基类
提供统一的消息队列接口
"""


logger = logging.getLogger(__name__)


class MessageFormat(Enum):
    """消息格式"""

    JSON = "json"
    BINARY = "binary"
    TEXT = "text"


@dataclass
class Message:
    """消息对象"""

    topic: str
    key: str | None = None
    value: Any = None
    headers: dict[str, str] | None = None
    timestamp: datetime | None = None
    partition: int | None = None
    offset: int | None = None
    format: MessageFormat = MessageFormat.JSON

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.headers is None:
            self.headers = {}

    def serialize(self) -> bytes:
        """序列化消息"""
        if self.format == MessageFormat.JSON:
            if isinstance(self.value, dict | list):
                return json.dumps(self.value, ensure_ascii=False).encode("utf-8")
            else:
                return json.dumps({"value": self.value}, ensure_ascii=False).encode(
                    "utf-8"
                )
        elif self.format == MessageFormat.BINARY:
            if isinstance(self.value, bytes):
                return self.value
            else:
                return str(self.value).encode("utf-8")
        else:  # TEXT
            return str(self.value).encode("utf-8")

    @classmethod
    def deserialize(
        cls, data: bytes, format: MessageFormat = MessageFormat.JSON
    ) -> Any:
        """反序列化消息"""
        if format == MessageFormat.JSON:
            return json.loads(data.decode("utf-8"))
        elif format == MessageFormat.BINARY:
            return data
        else:  # TEXT
            return data.decode("utf-8")


@dataclass
class ProducerConfig:
    """生产者配置"""

    client_id: str
    acks: str = "all"  # all, 1, 0
    retries: int = 3
    batch_size: int = 16384
    linger_ms: int = 10
    compression_type: str = "gzip"  # none, gzip, snappy, lz4
    max_in_flight_requests: int = 5
    enable_idempotence: bool = True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "client_id": self.client_id,
            "acks": self.acks,
            "retries": self.retries,
            "batch_size": self.batch_size,
            "linger_ms": self.linger_ms,
            "compression_type": self.compression_type,
            "max_in_flight_requests_per_connection": self.max_in_flight_requests,
            "enable_idempotence": self.enable_idempotence,
        }


@dataclass
class ConsumerConfig:
    """消费者配置"""

    group_id: str
    client_id: str
    auto_offset_reset: str = "latest"  # latest, earliest, none
    enable_auto_commit: bool = True
    auto_commit_interval_ms: int = 5000
    max_poll_records: int = 500
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 3000

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "group_id": self.group_id,
            "client_id": self.client_id,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "auto_commit_interval_ms": self.auto_commit_interval_ms,
            "max_poll_records": self.max_poll_records,
            "session_timeout_ms": self.session_timeout_ms,
            "heartbeat_interval_ms": self.heartbeat_interval_ms,
        }


class MessageHandler(ABC):
    """消息处理器抽象基类"""

    @abstractmethod
    async def handle(self, message: Message) -> bool:
        """
        处理消息

        Args:
            message: 消息对象

        Returns:
            bool: 处理是否成功
        """
        pass

    async def on_error(self, message: Message, error: Exception):
        """错误处理"""
        logger.error(f"消息处理失败: {error}", exc_info=True)


class MessageQueue(ABC):
    """消息队列抽象基类"""

    @abstractmethod
    async def connect(self):
        """连接到消息队列"""
        pass

    @abstractmethod
    async def disconnect(self):
        """断开连接"""
        pass

    @abstractmethod
    async def create_topic(
        self, topic: str, partitions: int = 1, replication_factor: int = 1
    ):
        """创建主题"""
        pass

    @abstractmethod
    async def delete_topic(self, topic: str):
        """删除主题"""
        pass

    @abstractmethod
    async def list_topics(self) -> list[str]:
        """列出所有主题"""
        pass

    @abstractmethod
    async def send(self, message: Message) -> bool:
        """
        发送消息

        Args:
            message: 消息对象

        Returns:
            bool: 发送是否成功
        """
        pass

    @abstractmethod
    async def send_batch(self, messages: list[Message]) -> list[bool]:
        """
        批量发送消息

        Args:
            messages: 消息列表

        Returns:
            List[bool]: 每条消息的发送结果
        """
        pass

    @abstractmethod
    async def subscribe(self, topics: str | list[str], handler: MessageHandler):
        """
        订阅主题

        Args:
            topics: 主题或主题列表
            handler: 消息处理器
        """
        pass

    @abstractmethod
    async def unsubscribe(self, topics: str | list[str] | None = None):
        """
        取消订阅

        Args:
            topics: 要取消的主题，None表示取消所有
        """
        pass

    @abstractmethod
    async def consume(self, timeout: float = 1.0) -> Message | None:
        """
        消费单条消息

        Args:
            timeout: 超时时间（秒）

        Returns:
            Optional[Message]: 消息对象，超时返回None
        """
        pass

    @abstractmethod
    async def consume_batch(
        self, max_messages: int = 10, timeout: float = 1.0
    ) -> list[Message]:
        """
        批量消费消息

        Args:
            max_messages: 最大消息数
            timeout: 超时时间（秒）

        Returns:
            List[Message]: 消息列表
        """
        pass

    @abstractmethod
    async def commit(self, message: Message | None = None):
        """
        提交偏移量

        Args:
            message: 要提交的消息，None表示提交当前偏移量
        """
        pass

    @abstractmethod
    async def seek(self, topic: str, partition: int, offset: int):
        """
        设置偏移量

        Args:
            topic: 主题
            partition: 分区
            offset: 偏移量
        """
        pass

    async def start_consuming(self, handler: MessageHandler, topics: str | list[str]):
        """
        开始消费循环

        Args:
            handler: 消息处理器
            topics: 主题或主题列表
        """
        await self.subscribe(topics, handler)

        while True:
            try:
                # 批量消费
                messages = await self.consume_batch(max_messages=100, timeout=1.0)

                for message in messages:
                    try:
                        # 处理消息
                        success = await handler.handle(message)

                        if success:
                            # 提交偏移量
                            await self.commit(message)
                        else:
                            logger.warning(f"消息处理失败，将重试: {message}")

                    except Exception as e:
                        await handler.on_error(message, e)

            except asyncio.CancelledError:
                logger.info("消费循环被取消")
                break
            except Exception as e:
                logger.error(f"消费循环错误: {e}")
                await asyncio.sleep(5)


# 全局消息队列注册表
_queues: dict[str, MessageQueue] = {}


def register_message_queue(name: str, queue: MessageQueue):
    """注册消息队列实例"""
    _queues[name] = queue
    logger.info(f"注册消息队列: {name}")


def get_message_queue(name: str) -> MessageQueue | None:
    """获取消息队列实例"""
    return _queues.get(name)


def list_message_queues() -> list[str]:
    """列出所有已注册的消息队列"""
    return list(_queues.keys())
