from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import json
import logging
import time
from datetime import datetime, timedelta
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
import asyncio
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaError
from prometheus_client import Counter, Histogram, Gauge

from internal.model.message import Message
from config.settings import Settings
from internal.observability.metrics import message_publish_latency, message_publish_failures, message_consume_latency

logger = logging.getLogger(__name__)

class MessageRepository(ABC):
    """消息存储库接口"""
    
    @abstractmethod
    async def save_message(self, message: Message) -> bool:
        """
        保存消息
        
        Args:
            message: 消息对象
            
        Returns:
            bool: 是否保存成功
        """
        pass
    
    @abstractmethod
    async def get_message(self, topic: str, message_id: str) -> Optional[Message]:
        """
        获取指定消息
        
        Args:
            topic: 主题名称
            message_id: 消息ID
            
        Returns:
            Optional[Message]: 消息对象，如不存在则返回None
        """
        pass
    
    @abstractmethod
    async def get_messages(
        self, 
        topic: str, 
        max_count: int = 100,
        filter_attributes: Optional[Dict[str, str]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Message]:
        """
        获取主题消息列表
        
        Args:
            topic: 主题名称
            max_count: 最大消息数量
            filter_attributes: 过滤属性
            start_time: 开始时间戳(毫秒)
            end_time: 结束时间戳(毫秒)
            
        Returns:
            List[Message]: 消息列表
        """
        pass

class KafkaMessageRepository(MessageRepository):
    """
    基于Kafka的消息存储库实现
    
    提供消息的持久化存储和检索功能，使用Kafka作为底层存储介质。
    支持错误重试、断路器模式和详细的监控指标。
    """
    
    def __init__(self, settings: Settings):
        """
        初始化Kafka消息存储库
        
        Args:
            settings: 应用程序配置
        """
        self.settings = settings
        self.producer = None
        self.bootstrap_servers = settings.kafka.bootstrap_servers
        self.topic_prefix = settings.kafka.topic_prefix
        
        # 断路器状态
        self._circuit_open = False
        self._failure_count = 0
        self._last_failure_time = 0
        self._reset_timeout = 30  # 断路器重置超时(秒)
        self._failure_threshold = 5  # 触发断路器的错误阈值
        
        # 监控指标
        self.circuit_breaker_status = Gauge(
            'message_bus_circuit_breaker_status',
            'Circuit breaker status (1=open, 0=closed)',
            ['repository']
        )
        self.circuit_breaker_status.labels(repository='kafka').set(0)
        
        self.message_operations = Counter(
            'message_bus_repository_operations_total',
            'Number of message repository operations',
            ['operation', 'status']
        )
    
    async def initialize(self) -> None:
        """初始化Kafka生产者"""
        logger.info(f"初始化Kafka生产者: {self.bootstrap_servers}")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks="all",  # 要求所有副本确认
            retries=5,
            retry_backoff_ms=100,
            max_in_flight_requests_per_connection=1,  # 确保消息顺序
            enable_idempotence=True  # 避免重复消息
        )
        await self.producer.start()
        logger.info("Kafka生产者初始化完成")
    
    async def close(self) -> None:
        """关闭Kafka资源"""
        if self.producer:
            logger.info("关闭Kafka生产者")
            await self.producer.stop()
            logger.info("Kafka生产者已关闭")
    
    def _get_kafka_topic(self, topic: str) -> str:
        """
        获取Kafka主题名称，添加前缀
        
        Args:
            topic: 业务主题名
            
        Returns:
            str: 带前缀的Kafka主题名
        """
        return f"{self.topic_prefix}{topic}"
    
    def _check_circuit_breaker(self) -> bool:
        """
        检查断路器状态
        
        如果断路器打开，会检查是否超过重置超时时间，
        如果超过则尝试半开状态，允许一次尝试
        
        Returns:
            bool: 断路器是否打开
        """
        if not self._circuit_open:
            return False
        
        # 检查是否超过重置超时时间
        current_time = time.time()
        if current_time - self._last_failure_time > self._reset_timeout:
            logger.info("断路器超时重置，尝试半开状态")
            self._circuit_open = False
            self.circuit_breaker_status.labels(repository='kafka').set(0)
            return False
        
        logger.warning(f"断路器打开，拒绝操作，将在{int(self._reset_timeout - (current_time - self._last_failure_time))}秒后重置")
        return True
    
    def _update_circuit_breaker(self, success: bool) -> None:
        """
        更新断路器状态
        
        根据操作成功或失败来调整断路器状态
        
        Args:
            success: 操作是否成功
        """
        if success:
            # 操作成功，重置计数器
            self._failure_count = 0
            if self._circuit_open:
                logger.info("操作成功，关闭断路器")
                self._circuit_open = False
                self.circuit_breaker_status.labels(repository='kafka').set(0)
        else:
            # 操作失败，增加计数器
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            # 检查是否超过阈值
            if not self._circuit_open and self._failure_count >= self._failure_threshold:
                logger.warning(f"连续失败{self._failure_count}次，打开断路器")
                self._circuit_open = True
                self.circuit_breaker_status.labels(repository='kafka').set(1)
    
    async def save_message(self, message: Message) -> bool:
        """
        保存消息到Kafka
        
        Args:
            message: 消息对象
            
        Returns:
            bool: 是否成功保存
            
        Raises:
            RuntimeError: 如果断路器打开或Kafka操作失败
        """
        # 检查断路器
        if self._check_circuit_breaker():
            self.message_operations.labels(operation='save', status='circuit_open').inc()
            raise RuntimeError("断路器已打开，暂时不接受新请求")
        
        if not self.producer:
            await self.initialize()
        
        kafka_topic = self._get_kafka_topic(message.topic)
        success = False
        
        start_time = time.time()
        try:
            # 准备消息数据
            message_data = message.to_dict()
            
            # 发送到Kafka
            partition_key = message.message_id
            
            # 发送消息
            send_future = await self.producer.send_and_wait(
                topic=kafka_topic,
                value=message_data,
                key=partition_key
            )
            
            logger.info(f"消息已保存到Kafka: {kafka_topic}, partition={send_future.partition}, offset={send_future.offset}")
            self.message_operations.labels(operation='save', status='success').inc()
            
            # 更新延迟指标
            message_publish_latency.observe(time.time() - start_time)
            
            success = True
            return True
            
        except KafkaError as e:
            logger.error(f"保存消息到Kafka失败: {str(e)}", exc_info=True)
            self.message_operations.labels(operation='save', status='error').inc()
            message_publish_failures.labels(error=type(e).__name__).inc()
            
            # 尝试创建主题(仅在首次尝试时)
            if "unknown topic" in str(e).lower() and self.settings.kafka.auto_create_topics:
                try:
                    # 尝试创建主题
                    admin_client = AIOKafkaProducer(
                        bootstrap_servers=self.bootstrap_servers
                    )
                    await admin_client.start()
                    topic_exists = await admin_client._client.cluster.leader_for_partition(kafka_topic, 0) is not None
                    
                    if not topic_exists:
                        logger.info(f"尝试创建主题: {kafka_topic}")
                        # 这里使用了低级API创建主题，生产环境建议使用Admin API
                        # 或通过Kafka配置设置auto.create.topics.enable=true
                        new_topics = [(
                            kafka_topic, 
                            self.settings.kafka.num_partitions, 
                            self.settings.kafka.replication_factor
                        )]
                        await admin_client._client.create_topics(new_topics)
                        logger.info(f"主题创建成功: {kafka_topic}")
                        
                        # 重试一次保存
                        await asyncio.sleep(1)  # 等待主题创建
                        return await self.save_message(message)
                    
                    await admin_client.stop()
                except Exception as create_error:
                    logger.error(f"创建主题失败: {str(create_error)}", exc_info=True)
            
            raise RuntimeError(f"保存消息失败: {str(e)}") from e
        finally:
            # 更新断路器状态
            self._update_circuit_breaker(success)
    
    async def get_message(self, topic: str, message_id: str) -> Optional[Message]:
        """
        获取特定消息
        
        Args:
            topic: 主题名称
            message_id: 消息ID
            
        Returns:
            Optional[Message]: 消息对象或None
        """
        # 检查断路器
        if self._check_circuit_breaker():
            self.message_operations.labels(operation='get', status='circuit_open').inc()
            raise RuntimeError("断路器已打开，暂时不接受新请求")
        
        success = False
        try:
            # 从Kafka中获取消息
            messages = await self.get_messages(topic, max_count=100)
            
            # 查找特定消息
            for message in messages:
                if message.message_id == message_id:
                    self.message_operations.labels(operation='get', status='success').inc()
                    success = True
                    return message
            
            self.message_operations.labels(operation='get', status='not_found').inc()
            return None
            
        except Exception as e:
            logger.error(f"获取消息失败: {str(e)}", exc_info=True)
            self.message_operations.labels(operation='get', status='error').inc()
            raise RuntimeError(f"获取消息失败: {str(e)}") from e
        finally:
            # 更新断路器状态
            self._update_circuit_breaker(success)
    
    async def get_messages(
        self, 
        topic: str, 
        max_count: int = 100,
        filter_attributes: Optional[Dict[str, str]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[Message]:
        """
        获取主题消息列表
        
        Args:
            topic: 主题名称
            max_count: 最大消息数量
            filter_attributes: 过滤属性
            start_time: 开始时间戳(毫秒)
            end_time: 结束时间戳(毫秒)
            
        Returns:
            List[Message]: 消息列表
        """
        # 检查断路器
        if self._check_circuit_breaker():
            self.message_operations.labels(operation='list', status='circuit_open').inc()
            raise RuntimeError("断路器已打开，暂时不接受新请求")
        
        kafka_topic = self._get_kafka_topic(topic)
        success = False
        consumer = None
        
        try:
            # 创建消费者
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=f"{self.settings.kafka.consumer_group_id}-temp-{int(time.time())}",
                auto_offset_reset="earliest",
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                enable_auto_commit=False
            )
            
            start_time_consume = time.time()
            await consumer.start()
            
            # 获取所有分区的消息
            result = []
            
            try:
                # 尝试获取消息，设置超时防止长时间阻塞
                await asyncio.wait_for(self._fetch_messages(
                    consumer, result, max_count, filter_attributes, start_time, end_time
                ), timeout=30)
            except asyncio.TimeoutError:
                logger.warning(f"获取消息超时，返回已收集的{len(result)}条消息")
            
            # 更新延迟指标
            message_consume_latency.observe(time.time() - start_time_consume)
            
            self.message_operations.labels(operation='list', status='success').inc()
            success = True
            return result
        
        except Exception as e:
            logger.error(f"获取消息列表失败: {str(e)}", exc_info=True)
            self.message_operations.labels(operation='list', status='error').inc()
            raise RuntimeError(f"获取消息列表失败: {str(e)}") from e
        
        finally:
            # 关闭消费者
            if consumer:
                await consumer.stop()
            
            # 更新断路器状态
            self._update_circuit_breaker(success)
    
    async def _fetch_messages(
        self,
        consumer,
        result: List[Message],
        max_count: int,
        filter_attributes: Optional[Dict[str, str]],
        start_time: Optional[int],
        end_time: Optional[int]
    ) -> None:
        """
        从Kafka消费者获取消息
        
        Args:
            consumer: Kafka消费者
            result: 结果列表
            max_count: 最大消息数量
            filter_attributes: 过滤属性
            start_time: 开始时间戳
            end_time: 结束时间戳
        """
        # 获取消息
        async for msg in consumer:
            # 获取消息数据
            try:
                message_data = msg.value
                
                # 创建消息对象
                message = Message.from_dict(message_data)
                
                # 检查时间范围
                if start_time and message.publish_time < start_time:
                    continue
                if end_time and message.publish_time > end_time:
                    continue
                
                # 检查属性过滤
                if filter_attributes:
                    match = True
                    for key, value in filter_attributes.items():
                        if key not in message.attributes or message.attributes[key] != value:
                            match = False
                            break
                    if not match:
                        continue
                
                result.append(message)
                
                # 检查是否达到最大数量
                if len(result) >= max_count:
                    break
                    
            except Exception as e:
                logger.error(f"处理消息失败: {str(e)}", exc_info=True)
                continue 