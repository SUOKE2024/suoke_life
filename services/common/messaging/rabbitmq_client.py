"""
rabbitmq_client - 索克生活项目模块
"""

    from aio_pika import Message as RabbitMessage
    import aio_pika
from .message_queue import (
import asyncio
import contextlib
import logging

#!/usr/bin/env python3
"""
RabbitMQ消息队列客户端
实现MessageQueue接口的RabbitMQ版本
"""


try:

    HAS_RABBITMQ = True
except ImportError:
    HAS_RABBITMQ = False


    ConsumerConfig,
    Message,
    MessageFormat,
    MessageHandler,
    MessageQueue,
    ProducerConfig,
)

logger = logging.getLogger(__name__)


class RabbitMQMessageQueue(MessageQueue):
    """RabbitMQ消息队列实现"""

    def __init__(
        self,
        url: str = "amqp://guest:guest@localhost/",
        producer_config: ProducerConfig | None = None,
        consumer_config: ConsumerConfig | None = None,
        exchange_type: str = "topic",
        durable: bool = True,
        auto_delete: bool = False,
    ):
        if not HAS_RABBITMQ:
            raise ImportError("aio-pika未安装，请安装: pip install aio-pika")

        self.url = url
        self.producer_config = producer_config
        self.consumer_config = consumer_config
        self.exchange_type = exchange_type
        self.durable = durable
        self.auto_delete = auto_delete

        # 连接和通道
        self.connection: aio_pika.Connection | None = None
        self.channel: aio_pika.Channel | None = None
        self.exchanges: dict[str, aio_pika.Exchange] = {}
        self.queues: dict[str, aio_pika.Queue] = {}

        # 消息处理器
        self.handlers: dict[str, MessageHandler] = {}

        # 消费任务
        self._consume_tasks: dict[str, asyncio.Task] = {}

    async def connect(self):
        """连接到RabbitMQ"""
        try:
            # 创建连接
            self.connection = await aio_pika.connect_robust(self.url)

            # 创建通道
            self.channel = await self.connection.channel()

            # 设置预取数量
            if self.consumer_config:
                await self.channel.set_qos(
                    prefetch_count=self.consumer_config.max_poll_records
                )

            logger.info(f"已连接到RabbitMQ: {self.url}")

        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            raise

    async def disconnect(self):
        """断开连接"""
        try:
            # 停止所有消费任务
            for task in self._consume_tasks.values():
                task.cancel()

            if self._consume_tasks:
                await asyncio.gather(
                    *self._consume_tasks.values(), return_exceptions=True
                )

            self._consume_tasks.clear()

            # 关闭通道和连接
            if self.channel:
                await self.channel.close()
                self.channel = None

            if self.connection:
                await self.connection.close()
                self.connection = None

            self.exchanges.clear()
            self.queues.clear()

            logger.info("已断开RabbitMQ连接")

        except Exception as e:
            logger.error(f"断开RabbitMQ连接失败: {e}")

    async def _get_or_create_exchange(self, name: str) -> aio_pika.Exchange:
        """获取或创建交换机"""
        if name not in self.exchanges:
            exchange = await self.channel.declare_exchange(
                name=name,
                type=self.exchange_type,
                durable=self.durable,
                auto_delete=self.auto_delete,
            )
            self.exchanges[name] = exchange

        return self.exchanges[name]

    async def create_topic(
        self, topic: str, partitions: int = 1, replication_factor: int = 1
    ):
        """创建主题（在RabbitMQ中创建交换机）"""
        if not self.channel:
            raise RuntimeError("未连接到RabbitMQ")

        try:
            await self._get_or_create_exchange(topic)
            logger.info(f"创建交换机成功: {topic}")

        except Exception as e:
            logger.error(f"创建交换机失败: {e}")
            raise

    async def delete_topic(self, topic: str):
        """删除主题（在RabbitMQ中删除交换机）"""
        if not self.channel:
            raise RuntimeError("未连接到RabbitMQ")

        try:
            if topic in self.exchanges:
                exchange = self.exchanges[topic]
                await exchange.delete()
                del self.exchanges[topic]

            logger.info(f"删除交换机成功: {topic}")

        except Exception as e:
            logger.error(f"删除交换机失败: {e}")
            raise

    async def list_topics(self) -> list[str]:
        """列出所有主题（交换机）"""
        # RabbitMQ不提供直接列出交换机的API
        # 返回已知的交换机列表
        return list(self.exchanges.keys())

    async def send(self, message: Message) -> bool:
        """发送消息"""
        if not self.channel:
            raise RuntimeError("未连接到RabbitMQ")

        try:
            # 获取或创建交换机
            exchange = await self._get_or_create_exchange(message.topic)

            # 序列化消息
            body = message.serialize()

            # 创建RabbitMQ消息
            rabbit_message = RabbitMessage(
                body=body,
                content_type="application/json"
                if message.format == MessageFormat.JSON
                else "text/plain",
                headers=message.headers,
                timestamp=message.timestamp,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                if self.durable
                else aio_pika.DeliveryMode.NOT_PERSISTENT,
            )

            # 发送消息
            await exchange.publish(rabbit_message, routing_key=message.key or "")

            return True

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def send_batch(self, messages: list[Message]) -> list[bool]:
        """批量发送消息"""
        results = []

        for message in messages:
            result = await self.send(message)
            results.append(result)

        return results

    async def subscribe(self, topics: str | list[str], handler: MessageHandler):
        """订阅主题"""
        if not self.channel:
            raise RuntimeError("未连接到RabbitMQ")

        if isinstance(topics, str):
            topics = [topics]

        for topic in topics:
            try:
                # 保存处理器
                self.handlers[topic] = handler

                # 创建队列
                queue_name = (
                    f"{self.consumer_config.group_id}.{topic}"
                    if self.consumer_config
                    else topic
                )
                queue = await self.channel.declare_queue(
                    name=queue_name, durable=self.durable, auto_delete=self.auto_delete
                )
                self.queues[topic] = queue

                # 获取或创建交换机
                exchange = await self._get_or_create_exchange(topic)

                # 绑定队列到交换机
                await queue.bind(exchange, routing_key="#")

                # 启动消费任务
                if (
                    topic not in self._consume_tasks
                    or self._consume_tasks[topic].done()
                ):
                    self._consume_tasks[topic] = asyncio.create_task(
                        self._consume_queue(queue, topic, handler)
                    )

                logger.info(f"已订阅主题: {topic}")

            except Exception as e:
                logger.error(f"订阅主题失败 {topic}: {e}")
                raise

    async def unsubscribe(self, topics: str | list[str] | None = None):
        """取消订阅"""
        if topics is None:
            topics = list(self.handlers.keys())
        elif isinstance(topics, str):
            topics = [topics]

        for topic in topics:
            # 停止消费任务
            if topic in self._consume_tasks:
                self._consume_tasks[topic].cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._consume_tasks[topic]
                del self._consume_tasks[topic]

            # 删除队列
            if topic in self.queues:
                try:
                    await self.queues[topic].delete()
                except Exception as e:
                    logger.error(f"删除队列失败 {topic}: {e}")
                del self.queues[topic]

            # 删除处理器
            self.handlers.pop(topic, None)

    async def consume(self, timeout: float = 1.0) -> Message | None:
        """消费单条消息"""
        # RabbitMQ使用基于推送的模型，这里模拟拉取
        messages = await self.consume_batch(max_messages=1, timeout=timeout)
        return messages[0] if messages else None

    async def consume_batch(
        self, max_messages: int = 10, timeout: float = 1.0
    ) -> list[Message]:
        """批量消费消息"""
        messages = []

        # 从所有队列收集消息
        for topic, queue in self.queues.items():
            try:
                # 使用超时获取消息
                async with asyncio.timeout(timeout):
                    async for rabbit_message in queue:
                        # 转换为通用消息格式
                        message = Message(
                            topic=topic,
                            key=rabbit_message.routing_key,
                            value=Message.deserialize(
                                rabbit_message.body,
                                MessageFormat.JSON
                                if rabbit_message.content_type == "application/json"
                                else MessageFormat.TEXT,
                            ),
                            headers=dict(rabbit_message.headers)
                            if rabbit_message.headers
                            else {},
                            timestamp=rabbit_message.timestamp,
                        )

                        messages.append(message)

                        # 确认消息
                        await rabbit_message.ack()

                        if len(messages) >= max_messages:
                            break

            except TimeoutError:
                pass
            except Exception as e:
                logger.error(f"消费消息失败: {e}")

        return messages

    async def commit(self, message: Message | None = None):
        """提交偏移量（RabbitMQ中为确认消息）"""
        # RabbitMQ使用消息确认机制，在consume时已经确认
        pass

    async def seek(self, topic: str, partition: int, offset: int):
        """设置偏移量（RabbitMQ不支持）"""
        logger.warning("RabbitMQ不支持设置偏移量")

    async def _consume_queue(
        self, queue: aio_pika.Queue, topic: str, handler: MessageHandler
    ):
        """消费队列消息"""
        try:
            async for rabbit_message in queue:
                try:
                    # 转换消息格式
                    message = Message(
                        topic=topic,
                        key=rabbit_message.routing_key,
                        value=Message.deserialize(
                            rabbit_message.body,
                            MessageFormat.JSON
                            if rabbit_message.content_type == "application/json"
                            else MessageFormat.TEXT,
                        ),
                        headers=dict(rabbit_message.headers)
                        if rabbit_message.headers
                        else {},
                        timestamp=rabbit_message.timestamp,
                    )

                    # 处理消息
                    success = await handler.handle(message)

                    if success:
                        # 确认消息
                        await rabbit_message.ack()
                    else:
                        # 拒绝消息并重新入队
                        await rabbit_message.nack(requeue=True)

                except Exception as e:
                    await handler.on_error(message, e)
                    # 拒绝消息但不重新入队
                    await rabbit_message.nack(requeue=False)

        except asyncio.CancelledError:
            logger.info(f"停止消费队列: {topic}")
            raise
        except Exception as e:
            logger.error(f"消费队列错误 {topic}: {e}")
