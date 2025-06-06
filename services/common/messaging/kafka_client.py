"""
kafka_client - 索克生活项目模块
"""

                from kafka import TopicPartition
            from kafka import TopicPartition
    from kafka import KafkaAdminClient, KafkaConsumer, KafkaProducer
    from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
from .message_queue import (
from datetime import datetime
from typing import Any
import asyncio
import contextlib
import logging

#!/usr/bin/env python3
"""
Kafka消息队列客户端
实现MessageQueue接口的Kafka版本
"""


try:

    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False


    ConsumerConfig,
    Message,
    MessageHandler,
    MessageQueue,
    ProducerConfig,
)

logger = logging.getLogger(__name__)

class KafkaMessageQueue(MessageQueue):
    """Kafka消息队列实现"""

    def __init__(
        self,
        bootstrap_servers: str | list[str],
        producer_config: ProducerConfig | None = None,
        consumer_config: ConsumerConfig | None = None,
        security_protocol: str = "PLAINTEXT",
        sasl_mechanism: str | None = None,
        sasl_username: str | None = None,
        sasl_password: str | None = None,
    ):
        if not HAS_KAFKA:
            raise ImportError("kafka-python未安装，请安装: pip install kafka-python")

        # 服务器配置
        if isinstance(bootstrap_servers, str):
            self.bootstrap_servers = bootstrap_servers
        else:
            self.bootstrap_servers = ",".join(bootstrap_servers)

        # 安全配置
        self.security_protocol = security_protocol
        self.sasl_mechanism = sasl_mechanism
        self.sasl_username = sasl_username
        self.sasl_password = sasl_password

        # 生产者和消费者配置
        self.producer_config = producer_config
        self.consumer_config = consumer_config

        # 客户端实例
        self.producer: KafkaProducer | None = None
        self.consumer: KafkaConsumer | None = None
        self.admin_client: KafkaAdminClient | None = None

        # 消息处理器
        self.handlers: dict[str, MessageHandler] = {}

        # 消费任务
        self._consume_task: asyncio.Task | None = None

    def _get_common_config(self) -> dict[str, Any]:
        """获取通用配置"""
        config = {
            "bootstrap_servers": self.bootstrap_servers,
            "security_protocol": self.security_protocol,
        }

        if self.sasl_mechanism:
            config.update(
                {
                    "sasl_mechanism": self.sasl_mechanism,
                    "sasl_plain_username": self.sasl_username,
                    "sasl_plain_password": self.sasl_password,
                }
            )

        return config

    async def connect(self):
        """连接到Kafka"""
        try:
            # 创建管理客户端
            admin_config = self._get_common_config()
            self.admin_client = KafkaAdminClient(**admin_config)

            # 创建生产者
            if self.producer_config:
                producer_config = self._get_common_config()
                producer_config.update(self.producer_config.to_dict())
                producer_config["value_serializer"] = (
                    lambda v: v if isinstance(v, bytes) else str(v).encode("utf-8")
                )
                producer_config["key_serializer"] = (
                    lambda k: k.encode("utf-8") if k else None
                )

                self.producer = KafkaProducer(**producer_config)

            logger.info(f"已连接到Kafka: {self.bootstrap_servers}")

        except Exception as e:
            logger.error(f"连接Kafka失败: {e}")
            raise

    async def disconnect(self):
        """断开连接"""
        try:
            # 停止消费任务
            if self._consume_task:
                self._consume_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._consume_task

            # 关闭消费者
            if self.consumer:
                self.consumer.close()
                self.consumer = None

            # 关闭生产者
            if self.producer:
                self.producer.close()
                self.producer = None

            # 关闭管理客户端
            if self.admin_client:
                self.admin_client.close()
                self.admin_client = None

            logger.info("已断开Kafka连接")

        except Exception as e:
            logger.error(f"断开Kafka连接失败: {e}")

    async def create_topic(
        self, topic: str, partitions: int = 1, replication_factor: int = 1
    ):
        """创建主题"""
        if not self.admin_client:
            raise RuntimeError("未连接到Kafka")

        try:
            new_topic = NewTopic(
                name=topic,
                num_partitions=partitions,
                replication_factor=replication_factor,
            )

            # 在事件循环中执行
            await asyncio.get_event_loop().run_in_executor(
                None, self.admin_client.create_topics, [new_topic]
            )

            logger.info(f"创建主题成功: {topic}")

        except Exception as e:
            if "already exists" in str(e):
                logger.warning(f"主题已存在: {topic}")
            else:
                logger.error(f"创建主题失败: {e}")
                raise

    async def delete_topic(self, topic: str):
        """删除主题"""
        if not self.admin_client:
            raise RuntimeError("未连接到Kafka")

        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.admin_client.delete_topics, [topic]
            )

            logger.info(f"删除主题成功: {topic}")

        except Exception as e:
            logger.error(f"删除主题失败: {e}")
            raise

    async def list_topics(self) -> list[str]:
        """列出所有主题"""
        if not self.admin_client:
            raise RuntimeError("未连接到Kafka")

        try:
            metadata = await asyncio.get_event_loop().run_in_executor(
                None, self.admin_client.list_topics
            )

            return list(metadata)

        except Exception as e:
            logger.error(f"列出主题失败: {e}")
            raise

    async def send(self, message: Message) -> bool:
        """发送消息"""
        if not self.producer:
            raise RuntimeError("生产者未初始化")

        try:
            # 序列化消息
            value = message.serialize()

            # 发送消息
            future = self.producer.send(
                topic=message.topic,
                key=message.key.encode("utf-8") if message.key else None,
                value=value,
                headers=[(k, v.encode("utf-8")) for k, v in message.headers.items()],
                partition=message.partition,
            )

            # 等待发送完成
            await asyncio.get_event_loop().run_in_executor(
                None,
                future.get,
                10,  # 超时10秒
            )

            return True

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def send_batch(self, messages: list[Message]) -> list[bool]:
        """批量发送消息"""
        if not self.producer:
            raise RuntimeError("生产者未初始化")

        results = []

        # 批量发送
        for message in messages:
            try:
                value = message.serialize()

                self.producer.send(
                    topic=message.topic,
                    key=message.key.encode("utf-8") if message.key else None,
                    value=value,
                    headers=[
                        (k, v.encode("utf-8")) for k, v in message.headers.items()
                    ],
                    partition=message.partition,
                )

                results.append(True)

            except Exception as e:
                logger.error(f"批量发送消息失败: {e}")
                results.append(False)

        # 刷新缓冲区
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.producer.flush,
                10,  # 超时10秒
            )
        except Exception as e:
            logger.error(f"刷新生产者缓冲区失败: {e}")

        return results

    async def subscribe(self, topics: str | list[str], handler: MessageHandler):
        """订阅主题"""
        if isinstance(topics, str):
            topics = [topics]

        # 保存处理器
        for topic in topics:
            self.handlers[topic] = handler

        # 创建消费者
        if not self.consumer:
            if not self.consumer_config:
                raise RuntimeError("消费者配置未提供")

            consumer_config = self._get_common_config()
            consumer_config.update(self.consumer_config.to_dict())
            consumer_config["value_deserializer"] = lambda v: v
            consumer_config["key_deserializer"] = (
                lambda k: k.decode("utf-8") if k else None
            )

            self.consumer = KafkaConsumer(**consumer_config)

        # 订阅主题
        self.consumer.subscribe(topics)

        # 启动消费任务
        if not self._consume_task or self._consume_task.done():
            self._consume_task = asyncio.create_task(self._consume_loop())

        logger.info(f"已订阅主题: {topics}")

    async def unsubscribe(self, topics: str | list[str] | None = None):
        """取消订阅"""
        if not self.consumer:
            return

        if topics is None:
            # 取消所有订阅
            self.consumer.unsubscribe()
            self.handlers.clear()
        else:
            # 取消特定主题
            if isinstance(topics, str):
                topics = [topics]

            for topic in topics:
                self.handlers.pop(topic, None)

            # 重新订阅剩余主题
            remaining_topics = list(self.handlers.keys())
            if remaining_topics:
                self.consumer.subscribe(remaining_topics)
            else:
                self.consumer.unsubscribe()

    async def consume(self, timeout: float = 1.0) -> Message | None:
        """消费单条消息"""
        if not self.consumer:
            raise RuntimeError("消费者未初始化")

        try:
            # 轮询消息
            records = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.consumer.poll(
                    timeout_ms=int(timeout * 1000), max_records=1
                ),
            )

            # 提取第一条消息
            for _topic_partition, messages in records.items():
                if messages:
                    record = messages[0]

                    # 构造消息对象
                    return Message(
                        topic=record.topic,
                        key=record.key,
                        value=Message.deserialize(record.value),
                        headers={k: v.decode("utf-8") for k, v in record.headers or []},
                        timestamp=datetime.fromtimestamp(record.timestamp / 1000),
                        partition=record.partition,
                        offset=record.offset,
                    )

            return None

        except Exception as e:
            logger.error(f"消费消息失败: {e}")
            return None

    async def consume_batch(
        self, max_messages: int = 10, timeout: float = 1.0
    ) -> list[Message]:
        """批量消费消息"""
        if not self.consumer:
            raise RuntimeError("消费者未初始化")

        messages = []

        try:
            # 轮询消息
            records = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.consumer.poll(
                    timeout_ms=int(timeout * 1000), max_records=max_messages
                ),
            )

            # 提取所有消息
            for _topic_partition, topic_messages in records.items():
                for record in topic_messages:
                    message = Message(
                        topic=record.topic,
                        key=record.key,
                        value=Message.deserialize(record.value),
                        headers={k: v.decode("utf-8") for k, v in record.headers or []},
                        timestamp=datetime.fromtimestamp(record.timestamp / 1000),
                        partition=record.partition,
                        offset=record.offset,
                    )
                    messages.append(message)

            return messages

        except Exception as e:
            logger.error(f"批量消费消息失败: {e}")
            return []

    async def commit(self, message: Message | None = None):
        """提交偏移量"""
        if not self.consumer:
            raise RuntimeError("消费者未初始化")

        try:
            if message:
                # 提交特定消息的偏移量

                tp = TopicPartition(message.topic, message.partition)
                offsets = {tp: message.offset + 1}

                await asyncio.get_event_loop().run_in_executor(
                    None, self.consumer.commit, offsets
                )
            else:
                # 提交当前偏移量
                await asyncio.get_event_loop().run_in_executor(
                    None, self.consumer.commit
                )

        except Exception as e:
            logger.error(f"提交偏移量失败: {e}")

    async def seek(self, topic: str, partition: int, offset: int):
        """设置偏移量"""
        if not self.consumer:
            raise RuntimeError("消费者未初始化")

        try:

            tp = TopicPartition(topic, partition)

            await asyncio.get_event_loop().run_in_executor(
                None, self.consumer.seek, tp, offset
            )

        except Exception as e:
            logger.error(f"设置偏移量失败: {e}")

    async def _consume_loop(self):
        """消费循环"""
        while True:
            try:
                # 批量消费消息
                messages = await self.consume_batch(max_messages=100, timeout=1.0)

                for message in messages:
                    # 获取处理器
                    handler = self.handlers.get(message.topic)
                    if handler:
                        try:
                            # 处理消息
                            success = await handler.handle(message)

                            if success and self.consumer_config.enable_auto_commit:
                                # 自动提交偏移量
                                await self.commit(message)

                        except Exception as e:
                            await handler.on_error(message, e)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"消费循环错误: {e}")
                await asyncio.sleep(5)
