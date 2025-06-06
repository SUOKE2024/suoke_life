"""
distributed_storage - 索克生活项目模块
"""

from .message_processor import MessageEnvelope
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, ConfigResource, ConfigResourceType
from aiokafka.admin.config_resource import ConfigResource
from aiokafka.admin.new_partitions import NewPartitions
from aiokafka.admin.new_topic import NewTopic
from aiokafka.errors import TopicAlreadyExistsError, KafkaError
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import aiokafka
import aioredis
import asyncio
import hashlib
import json
import logging
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
分布式消息存储管理器
支持Kafka集群管理、分区动态调整、副本管理和数据一致性保证
"""




logger = logging.getLogger(__name__)


class StorageStatus(Enum):
    """存储状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"


class ReplicationStrategy(Enum):
    """副本策略"""
    SYNC = "sync"
    ASYNC = "async"
    QUORUM = "quorum"


@dataclass
class StorageConfig:
    """存储配置"""
    # Kafka配置
    kafka_bootstrap_servers: List[str] = field(default_factory=lambda: ['localhost:9092'])
    kafka_security_protocol: str = 'PLAINTEXT'
    kafka_sasl_mechanism: Optional[str] = None
    kafka_sasl_username: Optional[str] = None
    kafka_sasl_password: Optional[str] = None
    
    # 主题配置
    default_partitions: int = 3
    default_replication_factor: int = 2
    default_retention_ms: int = 604800000  # 7天
    default_cleanup_policy: str = 'delete'
    
    # 性能配置
    batch_size: int = 16384
    linger_ms: int = 10
    compression_type: str = 'gzip'
    acks: str = 'all'
    max_in_flight_requests: int = 5
    
    # 监控配置
    health_check_interval: float = 30.0
    metrics_collection_interval: float = 60.0
    
    # Redis配置（用于元数据存储）
    redis_url: str = 'redis://localhost:6379'
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 分区管理
    auto_partition_scaling: bool = True
    partition_scale_threshold: float = 0.8  # 80%使用率时扩容
    max_partitions_per_topic: int = 100
    
    # 副本管理
    replication_strategy: ReplicationStrategy = ReplicationStrategy.QUORUM
    min_in_sync_replicas: int = 1
    unclean_leader_election: bool = False


@dataclass
class TopicMetadata:
    """主题元数据"""
    name: str
    partitions: int
    replication_factor: int
    config: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    status: StorageStatus = StorageStatus.HEALTHY
    
    # 分区信息
    partition_leaders: Dict[int, int] = field(default_factory=dict)  # partition -> leader_broker_id
    partition_replicas: Dict[int, List[int]] = field(default_factory=dict)  # partition -> replica_broker_ids
    partition_isr: Dict[int, List[int]] = field(default_factory=dict)  # partition -> in_sync_replica_ids
    
    # 统计信息
    message_count: int = 0
    total_size_bytes: int = 0
    avg_message_size: float = 0.0
    throughput_per_sec: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'partitions': self.partitions,
            'replication_factor': self.replication_factor,
            'config': self.config,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status.value,
            'partition_leaders': self.partition_leaders,
            'partition_replicas': self.partition_replicas,
            'partition_isr': self.partition_isr,
            'message_count': self.message_count,
            'total_size_bytes': self.total_size_bytes,
            'avg_message_size': self.avg_message_size,
            'throughput_per_sec': self.throughput_per_sec
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TopicMetadata':
        """从字典创建"""
        return cls(
            name=data['name'],
            partitions=data['partitions'],
            replication_factor=data['replication_factor'],
            config=data.get('config', {}),
            created_at=data.get('created_at', time.time()),
            updated_at=data.get('updated_at', time.time()),
            status=StorageStatus(data.get('status', StorageStatus.HEALTHY.value)),
            partition_leaders=data.get('partition_leaders', {}),
            partition_replicas=data.get('partition_replicas', {}),
            partition_isr=data.get('partition_isr', {}),
            message_count=data.get('message_count', 0),
            total_size_bytes=data.get('total_size_bytes', 0),
            avg_message_size=data.get('avg_message_size', 0.0),
            throughput_per_sec=data.get('throughput_per_sec', 0.0)
        )


@dataclass
class BrokerMetadata:
    """Broker元数据"""
    id: int
    host: str
    port: int
    rack: Optional[str] = None
    status: StorageStatus = StorageStatus.HEALTHY
    last_seen: float = field(default_factory=time.time)
    
    # 性能指标
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_in: float = 0.0
    network_out: float = 0.0
    
    # 分区信息
    leader_partitions: Set[Tuple[str, int]] = field(default_factory=set)  # (topic, partition)
    replica_partitions: Set[Tuple[str, int]] = field(default_factory=set)
    
    def get_load_score(self) -> float:
        """计算负载分数"""
        return (self.cpu_usage + self.memory_usage + self.disk_usage) / 3.0
    
    def is_healthy(self) -> bool:
        """检查是否健康"""
        return (
            self.status == StorageStatus.HEALTHY and
            time.time() - self.last_seen < 60 and  # 1分钟内有心跳
            self.cpu_usage < 90 and
            self.memory_usage < 90 and
            self.disk_usage < 85
        )


class PartitionManager:
    """分区管理器"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.partition_usage: Dict[Tuple[str, int], float] = {}  # (topic, partition) -> usage_ratio
        self.partition_stats: Dict[Tuple[str, int], Dict] = {}
    
    def calculate_partition_usage(self, topic: str, partition: int, stats: Dict[str, Any]) -> float:
        """计算分区使用率"""
        # 基于消息数量、大小和吞吐量计算使用率
        message_count = stats.get('message_count', 0)
        size_bytes = stats.get('size_bytes', 0)
        throughput = stats.get('throughput_per_sec', 0)
        
        # 归一化指标
        message_ratio = min(message_count / 1000000, 1.0)  # 100万消息为满
        size_ratio = min(size_bytes / (1024 * 1024 * 1024), 1.0)  # 1GB为满
        throughput_ratio = min(throughput / 10000, 1.0)  # 10k msg/s为满
        
        # 加权平均
        usage = (message_ratio * 0.3 + size_ratio * 0.4 + throughput_ratio * 0.3)
        
        self.partition_usage[(topic, partition)] = usage
        self.partition_stats[(topic, partition)] = stats
        
        return usage
    
    def should_scale_partitions(self, topic: str) -> bool:
        """判断是否需要扩容分区"""
        if not self.config.auto_partition_scaling:
            return False
        
        topic_partitions = [
            (t, p) for t, p in self.partition_usage.keys() if t == topic
        ]
        
        if not topic_partitions:
            return False
        
        # 检查是否有分区使用率超过阈值
        high_usage_partitions = [
            (t, p) for t, p in topic_partitions
            if self.partition_usage[(t, p)] > self.config.partition_scale_threshold
        ]
        
        # 如果超过50%的分区使用率过高，则扩容
        return len(high_usage_partitions) > len(topic_partitions) * 0.5
    
    def calculate_optimal_partitions(self, topic: str, current_partitions: int) -> int:
        """计算最优分区数"""
        if current_partitions >= self.config.max_partitions_per_topic:
            return current_partitions
        
        # 基于当前负载计算建议的分区数
        total_usage = sum(
            self.partition_usage.get((topic, p), 0)
            for p in range(current_partitions)
        )
        
        if total_usage == 0:
            return current_partitions
        
        avg_usage = total_usage / current_partitions
        
        if avg_usage > self.config.partition_scale_threshold:
            # 计算需要的分区数以将平均使用率降到目标水平
            target_usage = self.config.partition_scale_threshold * 0.7  # 目标70%使用率
            suggested_partitions = int(total_usage / target_usage)
            
            # 限制扩容幅度，一次最多翻倍
            max_new_partitions = min(
                suggested_partitions,
                current_partitions * 2,
                self.config.max_partitions_per_topic
            )
            
            return max(current_partitions + 1, max_new_partitions)
        
        return current_partitions


class ReplicationManager:
    """副本管理器"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.broker_loads: Dict[int, float] = {}
    
    def calculate_replica_placement(
        self, 
        topic: str, 
        partitions: int, 
        replication_factor: int,
        brokers: List[BrokerMetadata]
    ) -> Dict[int, List[int]]:
        """计算副本放置策略"""
        healthy_brokers = [b for b in brokers if b.is_healthy()]
        
        if len(healthy_brokers) < replication_factor:
            raise ValueError(f"健康的broker数量({len(healthy_brokers)})少于副本因子({replication_factor})")
        
        replica_assignment = {}
        
        # 按负载排序broker
        sorted_brokers = sorted(healthy_brokers, key=lambda b: b.get_load_score())
        
        for partition in range(partitions):
            replicas = []
            
            # 选择负载最低的broker作为leader
            leader_broker = sorted_brokers[partition % len(sorted_brokers)]
            replicas.append(leader_broker.id)
            
            # 选择其他副本，避免在同一机架
            remaining_brokers = [b for b in sorted_brokers if b.id != leader_broker.id]
            
            # 优先选择不同机架的broker
            different_rack_brokers = [
                b for b in remaining_brokers 
                if b.rack != leader_broker.rack
            ]
            
            replica_candidates = different_rack_brokers if different_rack_brokers else remaining_brokers
            
            # 选择剩余的副本
            for i in range(replication_factor - 1):
                if i < len(replica_candidates):
                    broker = replica_candidates[i]
                    replicas.append(broker.id)
            
            replica_assignment[partition] = replicas
        
        return replica_assignment
    
    def should_rebalance_replicas(self, topic_metadata: TopicMetadata, brokers: List[BrokerMetadata]) -> bool:
        """判断是否需要重新平衡副本"""
        healthy_brokers = [b for b in brokers if b.is_healthy()]
        
        if len(healthy_brokers) < topic_metadata.replication_factor:
            return True
        
        # 检查是否有分区的ISR数量不足
        for partition, isr in topic_metadata.partition_isr.items():
            if len(isr) < self.config.min_in_sync_replicas:
                return True
        
        # 检查负载是否不均衡
        broker_partition_counts = defaultdict(int)
        for replicas in topic_metadata.partition_replicas.values():
            for broker_id in replicas:
                broker_partition_counts[broker_id] += 1
        
        if broker_partition_counts:
            max_count = max(broker_partition_counts.values())
            min_count = min(broker_partition_counts.values())
            
            # 如果最大和最小分区数差异超过阈值，需要重新平衡
            if max_count - min_count > len(healthy_brokers) * 0.3:
                return True
        
        return False


class ConsistencyManager:
    """一致性管理器"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.pending_operations: Dict[str, Dict] = {}  # operation_id -> operation_info
    
    async def ensure_write_consistency(
        self, 
        producer: AIOKafkaProducer,
        topic: str,
        message: MessageEnvelope,
        required_acks: int = None
    ) -> bool:
        """确保写入一致性"""
        required_acks = required_acks or self._get_required_acks()
        
        try:
            # 发送消息并等待确认
            future = await producer.send(
                topic=topic,
                value=message.payload,
                headers=[(k, v.encode()) for k, v in message.attributes.items()],
                partition=self._calculate_partition(message, topic)
            )
            
            # 等待指定数量的副本确认
            record_metadata = await future
            
            # 验证写入是否成功
            if self.config.replication_strategy == ReplicationStrategy.QUORUM:
                return await self._verify_quorum_write(topic, record_metadata)
            elif self.config.replication_strategy == ReplicationStrategy.SYNC:
                return await self._verify_sync_write(topic, record_metadata)
            else:
                return True  # 异步模式不需要额外验证
        
        except Exception as e:
            logger.error(f"写入一致性检查失败: {e}")
            return False
    
    def _get_required_acks(self) -> int:
        """获取所需的确认数"""
        if self.config.acks == 'all' or self.config.acks == '-1':
            return -1
        elif self.config.acks == '1':
            return 1
        else:
            return 0
    
    def _calculate_partition(self, message: MessageEnvelope, topic: str) -> Optional[int]:
        """计算消息应该发送到的分区"""
        # 基于消息ID的哈希值计算分区
        hash_value = hashlib.md5(message.id.encode()).hexdigest()
        # 这里需要知道主题的分区数，实际实现中应该从元数据获取
        # 暂时返回None，让Kafka自动选择分区
        return None
    
    async def _verify_quorum_write(self, topic: str, record_metadata) -> bool:
        """验证仲裁写入"""
        # 实际实现中需要检查ISR中的副本数量
        # 这里简化处理
        return True
    
    async def _verify_sync_write(self, topic: str, record_metadata) -> bool:
        """验证同步写入"""
        # 实际实现中需要检查所有副本的同步状态
        # 这里简化处理
        return True


class DistributedStorageManager:
    """
    分布式消息存储管理器
    支持Kafka集群管理、分区动态调整、副本管理和数据一致性保证
    """
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.partition_manager = PartitionManager(config)
        self.replication_manager = ReplicationManager(config)
        self.consistency_manager = ConsistencyManager(config)
        
        # Kafka客户端
        self.admin_client: Optional[AIOKafkaAdminClient] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.redis_client: Optional[aioredis.Redis] = None
        
        # 元数据缓存
        self.topic_metadata: Dict[str, TopicMetadata] = {}
        self.broker_metadata: Dict[int, BrokerMetadata] = {}
        
        # 运行状态
        self._running = False
        self._health_check_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None
        self._rebalance_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """启动存储管理器"""
        if self._running:
            return
        
        self._running = True
        
        # 初始化Kafka客户端
        await self._init_kafka_clients()
        
        # 初始化Redis客户端
        await self._init_redis_client()
        
        # 加载元数据
        await self._load_metadata()
        
        # 启动后台任务
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self._rebalance_task = asyncio.create_task(self._rebalance_loop())
        
        logger.info("分布式存储管理器已启动")
    
    async def stop(self):
        """停止存储管理器"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止后台任务
        for task in [self._health_check_task, self._metrics_task, self._rebalance_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # 关闭客户端
        if self.admin_client:
            await self.admin_client.close()
        
        if self.producer:
            await self.producer.stop()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("分布式存储管理器已停止")
    
    async def _init_kafka_clients(self):
        """初始化Kafka客户端"""
        # 创建管理客户端
        self.admin_client = AIOKafkaAdminClient(
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            security_protocol=self.config.kafka_security_protocol,
            sasl_mechanism=self.config.kafka_sasl_mechanism,
            sasl_plain_username=self.config.kafka_sasl_username,
            sasl_plain_password=self.config.kafka_sasl_password
        )
        await self.admin_client.start()
        
        # 创建生产者
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.config.kafka_bootstrap_servers,
            security_protocol=self.config.kafka_security_protocol,
            sasl_mechanism=self.config.kafka_sasl_mechanism,
            sasl_plain_username=self.config.kafka_sasl_username,
            sasl_plain_password=self.config.kafka_sasl_password,
            batch_size=self.config.batch_size,
            linger_ms=self.config.linger_ms,
            compression_type=self.config.compression_type,
            acks=self.config.acks,
            max_in_flight_requests_per_connection=self.config.max_in_flight_requests
        )
        await self.producer.start()
    
    async def _init_redis_client(self):
        """初始化Redis客户端"""
        self.redis_client = aioredis.from_url(
            self.config.redis_url,
            db=self.config.redis_db,
            password=self.config.redis_password,
            decode_responses=True
        )
    
    async def _load_metadata(self):
        """加载元数据"""
        try:
            # 从Kafka加载主题元数据
            metadata = await self.admin_client.describe_cluster()
            
            # 更新broker元数据
            for broker in metadata.brokers:
                self.broker_metadata[broker.id] = BrokerMetadata(
                    id=broker.id,
                    host=broker.host,
                    port=broker.port,
                    rack=broker.rack
                )
            
            # 加载主题信息
            topic_metadata = await self.admin_client.list_topics()
            for topic_name in topic_metadata.topics:
                await self._load_topic_metadata(topic_name)
            
            logger.info(f"加载了 {len(self.topic_metadata)} 个主题和 {len(self.broker_metadata)} 个broker的元数据")
        
        except Exception as e:
            logger.error(f"加载元数据失败: {e}")
    
    async def _load_topic_metadata(self, topic_name: str):
        """加载单个主题的元数据"""
        try:
            # 获取主题详细信息
            topic_metadata = await self.admin_client.describe_topics([topic_name])
            topic_info = topic_metadata[topic_name]
            
            # 获取主题配置
            config_resources = [ConfigResource(ConfigResourceType.TOPIC, topic_name)]
            configs = await self.admin_client.describe_configs(config_resources)
            topic_config = {
                config.name: config.value 
                for config in configs[config_resources[0]].configs
            }
            
            # 创建主题元数据
            metadata = TopicMetadata(
                name=topic_name,
                partitions=len(topic_info.partitions),
                replication_factor=len(topic_info.partitions[0].replicas) if topic_info.partitions else 0,
                config=topic_config
            )
            
            # 更新分区信息
            for partition_info in topic_info.partitions:
                partition_id = partition_info.partition
                metadata.partition_leaders[partition_id] = partition_info.leader
                metadata.partition_replicas[partition_id] = list(partition_info.replicas)
                metadata.partition_isr[partition_id] = list(partition_info.isr)
            
            self.topic_metadata[topic_name] = metadata
            
            # 从Redis加载统计信息
            await self._load_topic_stats_from_redis(topic_name)
        
        except Exception as e:
            logger.error(f"加载主题 {topic_name} 元数据失败: {e}")
    
    async def _load_topic_stats_from_redis(self, topic_name: str):
        """从Redis加载主题统计信息"""
        try:
            stats_key = f"topic_stats:{topic_name}"
            stats_data = await self.redis_client.hgetall(stats_key)
            
            if stats_data:
                metadata = self.topic_metadata[topic_name]
                metadata.message_count = int(stats_data.get('message_count', 0))
                metadata.total_size_bytes = int(stats_data.get('total_size_bytes', 0))
                metadata.avg_message_size = float(stats_data.get('avg_message_size', 0.0))
                metadata.throughput_per_sec = float(stats_data.get('throughput_per_sec', 0.0))
        
        except Exception as e:
            logger.error(f"从Redis加载主题 {topic_name} 统计信息失败: {e}")
    
    async def create_topic(
        self, 
        name: str, 
        partitions: Optional[int] = None,
        replication_factor: Optional[int] = None,
        config: Optional[Dict[str, str]] = None
    ) -> bool:
        """创建主题"""
        try:
            partitions = partitions or self.config.default_partitions
            replication_factor = replication_factor or self.config.default_replication_factor
            config = config or {}
            
            # 设置默认配置
            default_config = {
                'retention.ms': str(self.config.default_retention_ms),
                'cleanup.policy': self.config.default_cleanup_policy,
                'min.insync.replicas': str(self.config.min_in_sync_replicas),
                'unclean.leader.election.enable': str(self.config.unclean_leader_election).lower()
            }
            default_config.update(config)
            
            # 创建主题
            new_topic = NewTopic(
                name=name,
                num_partitions=partitions,
                replication_factor=replication_factor,
                topic_configs=default_config
            )
            
            await self.admin_client.create_topics([new_topic])
            
            # 更新元数据
            await self._load_topic_metadata(name)
            
            logger.info(f"成功创建主题: {name} (分区: {partitions}, 副本: {replication_factor})")
            return True
        
        except TopicAlreadyExistsError:
            logger.warning(f"主题 {name} 已存在")
            return True
        except Exception as e:
            logger.error(f"创建主题 {name} 失败: {e}")
            return False
    
    async def delete_topic(self, name: str) -> bool:
        """删除主题"""
        try:
            await self.admin_client.delete_topics([name])
            
            # 清理元数据
            self.topic_metadata.pop(name, None)
            
            # 清理Redis中的统计信息
            stats_key = f"topic_stats:{name}"
            await self.redis_client.delete(stats_key)
            
            logger.info(f"成功删除主题: {name}")
            return True
        
        except Exception as e:
            logger.error(f"删除主题 {name} 失败: {e}")
            return False
    
    async def scale_topic_partitions(self, topic_name: str, new_partition_count: int) -> bool:
        """扩容主题分区"""
        try:
            current_metadata = self.topic_metadata.get(topic_name)
            if not current_metadata:
                logger.error(f"主题 {topic_name} 不存在")
                return False
            
            if new_partition_count <= current_metadata.partitions:
                logger.warning(f"新分区数 {new_partition_count} 不大于当前分区数 {current_metadata.partitions}")
                return False
            
            # 创建分区扩容请求
            partition_update = {topic_name: NewPartitions(total_count=new_partition_count)}
            await self.admin_client.create_partitions(partition_update)
            
            # 重新加载元数据
            await self._load_topic_metadata(topic_name)
            
            logger.info(f"成功扩容主题 {topic_name} 分区数从 {current_metadata.partitions} 到 {new_partition_count}")
            return True
        
        except Exception as e:
            logger.error(f"扩容主题 {topic_name} 分区失败: {e}")
            return False
    
    async def store_message(self, topic: str, message: MessageEnvelope) -> bool:
        """存储消息"""
        try:
            # 确保主题存在
            if topic not in self.topic_metadata:
                await self.create_topic(topic)
            
            # 使用一致性管理器存储消息
            success = await self.consistency_manager.ensure_write_consistency(
                self.producer, topic, message
            )
            
            if success:
                # 更新统计信息
                await self._update_topic_stats(topic, message)
            
            return success
        
        except Exception as e:
            logger.error(f"存储消息到主题 {topic} 失败: {e}")
            return False
    
    async def _update_topic_stats(self, topic: str, message: MessageEnvelope):
        """更新主题统计信息"""
        try:
            metadata = self.topic_metadata.get(topic)
            if not metadata:
                return
            
            # 更新内存中的统计信息
            metadata.message_count += 1
            message_size = len(message.payload)
            metadata.total_size_bytes += message_size
            
            if metadata.message_count > 0:
                metadata.avg_message_size = metadata.total_size_bytes / metadata.message_count
            
            # 更新Redis中的统计信息
            stats_key = f"topic_stats:{topic}"
            await self.redis_client.hset(stats_key, mapping={
                'message_count': metadata.message_count,
                'total_size_bytes': metadata.total_size_bytes,
                'avg_message_size': metadata.avg_message_size,
                'last_updated': time.time()
            })
        
        except Exception as e:
            logger.error(f"更新主题 {topic} 统计信息失败: {e}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查出错: {e}")
    
    async def _perform_health_checks(self):
        """执行健康检查"""
        try:
            # 检查Kafka集群健康状态
            metadata = await self.admin_client.describe_cluster()
            
            # 更新broker状态
            current_time = time.time()
            active_broker_ids = {broker.id for broker in metadata.brokers}
            
            for broker_id, broker_metadata in self.broker_metadata.items():
                if broker_id in active_broker_ids:
                    broker_metadata.last_seen = current_time
                    broker_metadata.status = StorageStatus.HEALTHY
                else:
                    # Broker离线
                    if current_time - broker_metadata.last_seen > 60:
                        broker_metadata.status = StorageStatus.UNAVAILABLE
            
            # 检查主题健康状态
            for topic_name, topic_metadata in self.topic_metadata.items():
                await self._check_topic_health(topic_name, topic_metadata)
        
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
    
    async def _check_topic_health(self, topic_name: str, topic_metadata: TopicMetadata):
        """检查主题健康状态"""
        try:
            # 检查分区的ISR状态
            unhealthy_partitions = 0
            
            for partition, isr in topic_metadata.partition_isr.items():
                # 检查ISR中的副本数量
                if len(isr) < self.config.min_in_sync_replicas:
                    unhealthy_partitions += 1
                
                # 检查leader是否健康
                leader_id = topic_metadata.partition_leaders.get(partition)
                if leader_id and leader_id in self.broker_metadata:
                    leader_broker = self.broker_metadata[leader_id]
                    if not leader_broker.is_healthy():
                        unhealthy_partitions += 1
            
            # 更新主题状态
            total_partitions = topic_metadata.partitions
            if unhealthy_partitions == 0:
                topic_metadata.status = StorageStatus.HEALTHY
            elif unhealthy_partitions < total_partitions * 0.3:
                topic_metadata.status = StorageStatus.DEGRADED
            else:
                topic_metadata.status = StorageStatus.UNAVAILABLE
        
        except Exception as e:
            logger.error(f"检查主题 {topic_name} 健康状态失败: {e}")
            topic_metadata.status = StorageStatus.UNAVAILABLE
    
    async def _metrics_collection_loop(self):
        """指标收集循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.metrics_collection_interval)
                await self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集出错: {e}")
    
    async def _collect_metrics(self):
        """收集指标"""
        try:
            # 收集主题指标
            for topic_name, topic_metadata in self.topic_metadata.items():
                # 这里应该实现实际的指标收集逻辑
                # 例如从Kafka JMX或其他监控系统获取指标
                pass
            
            # 收集broker指标
            for broker_id, broker_metadata in self.broker_metadata.items():
                # 这里应该实现实际的broker指标收集逻辑
                pass
        
        except Exception as e:
            logger.error(f"收集指标失败: {e}")
    
    async def _rebalance_loop(self):
        """重新平衡循环"""
        while self._running:
            try:
                await asyncio.sleep(300)  # 每5分钟检查一次
                await self._check_and_rebalance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"重新平衡检查出错: {e}")
    
    async def _check_and_rebalance(self):
        """检查并执行重新平衡"""
        try:
            brokers = list(self.broker_metadata.values())
            
            for topic_name, topic_metadata in self.topic_metadata.items():
                # 检查是否需要扩容分区
                if self.partition_manager.should_scale_partitions(topic_name):
                    optimal_partitions = self.partition_manager.calculate_optimal_partitions(
                        topic_name, topic_metadata.partitions
                    )
                    
                    if optimal_partitions > topic_metadata.partitions:
                        logger.info(f"主题 {topic_name} 需要扩容分区: {topic_metadata.partitions} -> {optimal_partitions}")
                        await self.scale_topic_partitions(topic_name, optimal_partitions)
                
                # 检查是否需要重新平衡副本
                if self.replication_manager.should_rebalance_replicas(topic_metadata, brokers):
                    logger.info(f"主题 {topic_name} 需要重新平衡副本")
                    # 这里应该实现副本重新平衡逻辑
                    # 由于Kafka的副本重新分配比较复杂，这里暂时跳过实现
        
        except Exception as e:
            logger.error(f"重新平衡检查失败: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        healthy_brokers = sum(1 for b in self.broker_metadata.values() if b.is_healthy())
        healthy_topics = sum(1 for t in self.topic_metadata.values() if t.status == StorageStatus.HEALTHY)
        
        total_messages = sum(t.message_count for t in self.topic_metadata.values())
        total_size = sum(t.total_size_bytes for t in self.topic_metadata.values())
        
        return {
            'cluster_health': {
                'total_brokers': len(self.broker_metadata),
                'healthy_brokers': healthy_brokers,
                'total_topics': len(self.topic_metadata),
                'healthy_topics': healthy_topics
            },
            'storage_metrics': {
                'total_messages': total_messages,
                'total_size_bytes': total_size,
                'avg_message_size': total_size / max(total_messages, 1)
            },
            'topic_stats': {
                name: metadata.to_dict()
                for name, metadata in self.topic_metadata.items()
            },
            'broker_stats': {
                broker_id: {
                    'id': broker.id,
                    'host': broker.host,
                    'port': broker.port,
                    'status': broker.status.value,
                    'load_score': broker.get_load_score(),
                    'leader_partitions': len(broker.leader_partitions),
                    'replica_partitions': len(broker.replica_partitions)
                }
                for broker_id, broker in self.broker_metadata.items()
            }
        }
    
    def get_topic_metadata(self, topic_name: str) -> Optional[TopicMetadata]:
        """获取主题元数据"""
        return self.topic_metadata.get(topic_name)
    
    def get_broker_metadata(self, broker_id: int) -> Optional[BrokerMetadata]:
        """获取broker元数据"""
        return self.broker_metadata.get(broker_id)


# 存储管理器工厂
class StorageManagerFactory:
    """存储管理器工厂"""
    
    @staticmethod
    def create_distributed_storage_manager(
        config: Optional[StorageConfig] = None
    ) -> DistributedStorageManager:
        """创建分布式存储管理器"""
        if config is None:
            config = StorageConfig()
        
        return DistributedStorageManager(config) 