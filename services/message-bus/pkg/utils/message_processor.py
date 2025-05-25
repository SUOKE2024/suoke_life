#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高性能消息处理引擎
支持异步消息处理、批处理、压缩和内存优化
"""

import asyncio
import gzip
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor

import aiokafka
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import aioredis

logger = logging.getLogger(__name__)


class CompressionType(Enum):
    """压缩类型"""
    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"


class MessagePriority(Enum):
    """消息优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ProcessorConfig:
    """消息处理器配置"""
    # 批处理配置
    batch_size: int = 100
    batch_timeout: float = 1.0
    max_batch_size: int = 1000
    
    # 压缩配置
    compression_enabled: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    compression_threshold: int = 1024  # 1KB
    
    # 性能配置
    worker_threads: int = 4
    max_queue_size: int = 10000
    memory_pool_size: int = 1000
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    
    # 监控配置
    metrics_enabled: bool = True
    stats_interval: float = 30.0


@dataclass
class MessageEnvelope:
    """消息信封"""
    id: str
    topic: str
    payload: bytes
    attributes: Dict[str, str] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0
    compressed: bool = False
    compression_type: Optional[CompressionType] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'topic': self.topic,
            'payload': self.payload,
            'attributes': self.attributes,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'retry_count': self.retry_count,
            'compressed': self.compressed,
            'compression_type': self.compression_type.value if self.compression_type else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageEnvelope':
        """从字典创建"""
        return cls(
            id=data['id'],
            topic=data['topic'],
            payload=data['payload'],
            attributes=data.get('attributes', {}),
            priority=MessagePriority(data.get('priority', MessagePriority.NORMAL.value)),
            timestamp=data.get('timestamp', time.time()),
            retry_count=data.get('retry_count', 0),
            compressed=data.get('compressed', False),
            compression_type=CompressionType(data['compression_type']) if data.get('compression_type') else None
        )


@dataclass
class ProcessingStats:
    """处理统计信息"""
    total_processed: int = 0
    total_failed: int = 0
    total_retries: int = 0
    avg_processing_time: float = 0.0
    avg_batch_size: float = 0.0
    compression_ratio: float = 0.0
    memory_usage: int = 0
    queue_size: int = 0


class MessageCompressor:
    """消息压缩器"""
    
    @staticmethod
    def compress(data: bytes, compression_type: CompressionType) -> bytes:
        """压缩数据"""
        if compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression_type == CompressionType.SNAPPY:
            try:
                import snappy
                return snappy.compress(data)
            except ImportError:
                logger.warning("snappy not available, falling back to gzip")
                return gzip.compress(data)
        elif compression_type == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.compress(data)
            except ImportError:
                logger.warning("lz4 not available, falling back to gzip")
                return gzip.compress(data)
        else:
            return data
    
    @staticmethod
    def decompress(data: bytes, compression_type: CompressionType) -> bytes:
        """解压缩数据"""
        if compression_type == CompressionType.GZIP:
            return gzip.decompress(data)
        elif compression_type == CompressionType.SNAPPY:
            try:
                import snappy
                return snappy.decompress(data)
            except ImportError:
                logger.warning("snappy not available")
                return data
        elif compression_type == CompressionType.LZ4:
            try:
                import lz4.frame
                return lz4.frame.decompress(data)
            except ImportError:
                logger.warning("lz4 not available")
                return data
        else:
            return data


class MemoryPool:
    """内存池管理器"""
    
    def __init__(self, pool_size: int = 1000):
        self.pool_size = pool_size
        self._pool: deque = deque()
        self._lock = threading.Lock()
        self._stats = {
            'allocated': 0,
            'reused': 0,
            'pool_hits': 0,
            'pool_misses': 0
        }
    
    def get_buffer(self, size: int) -> bytearray:
        """获取缓冲区"""
        with self._lock:
            # 尝试从池中获取合适大小的缓冲区
            for i, buffer in enumerate(self._pool):
                if len(buffer) >= size:
                    self._pool.remove(buffer)
                    self._stats['pool_hits'] += 1
                    self._stats['reused'] += 1
                    return buffer
            
            # 池中没有合适的缓冲区，创建新的
            self._stats['pool_misses'] += 1
            self._stats['allocated'] += 1
            return bytearray(size)
    
    def return_buffer(self, buffer: bytearray):
        """归还缓冲区"""
        with self._lock:
            if len(self._pool) < self.pool_size:
                # 清空缓冲区内容
                buffer[:] = b'\x00' * len(buffer)
                self._pool.append(buffer)
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        with self._lock:
            return self._stats.copy()


class MessageProcessor(ABC):
    """消息处理器抽象基类"""
    
    @abstractmethod
    async def process_message(self, message: MessageEnvelope) -> bool:
        """处理单个消息"""
        pass
    
    @abstractmethod
    async def process_batch(self, messages: List[MessageEnvelope]) -> List[bool]:
        """批处理消息"""
        pass


class HighPerformanceMessageProcessor:
    """
    高性能消息处理引擎
    支持异步处理、批处理、压缩和内存优化
    """
    
    def __init__(self, config: ProcessorConfig):
        self.config = config
        self.compressor = MessageCompressor()
        self.memory_pool = MemoryPool(config.memory_pool_size)
        
        # 处理队列
        self._processing_queue: asyncio.Queue = asyncio.Queue(maxsize=config.max_queue_size)
        self._priority_queues: Dict[MessagePriority, asyncio.Queue] = {
            priority: asyncio.Queue(maxsize=config.max_queue_size // 4)
            for priority in MessagePriority
        }
        
        # 批处理缓冲区
        self._batch_buffer: List[MessageEnvelope] = []
        self._batch_lock = asyncio.Lock()
        self._last_batch_time = time.time()
        
        # 工作线程池
        self._thread_pool = ThreadPoolExecutor(max_workers=config.worker_threads)
        
        # 统计信息
        self._stats = ProcessingStats()
        self._stats_lock = asyncio.Lock()
        
        # 运行状态
        self._running = False
        self._workers: List[asyncio.Task] = []
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._stats_task: Optional[asyncio.Task] = None
        
        # 消息处理器
        self._processors: List[MessageProcessor] = []
    
    def add_processor(self, processor: MessageProcessor):
        """添加消息处理器"""
        self._processors.append(processor)
    
    async def start(self):
        """启动消息处理引擎"""
        if self._running:
            return
        
        self._running = True
        
        # 启动工作线程
        for i in range(self.config.worker_threads):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self._workers.append(worker)
        
        # 启动批处理器
        self._batch_processor_task = asyncio.create_task(self._batch_processor_loop())
        
        # 启动统计收集器
        if self.config.metrics_enabled:
            self._stats_task = asyncio.create_task(self._stats_loop())
        
        logger.info("高性能消息处理引擎已启动")
    
    async def stop(self):
        """停止消息处理引擎"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止工作线程
        for worker in self._workers:
            worker.cancel()
            try:
                await worker
            except asyncio.CancelledError:
                pass
        
        # 停止批处理器
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass
        
        # 停止统计收集器
        if self._stats_task:
            self._stats_task.cancel()
            try:
                await self._stats_task
            except asyncio.CancelledError:
                pass
        
        # 关闭线程池
        self._thread_pool.shutdown(wait=True)
        
        logger.info("高性能消息处理引擎已停止")
    
    async def submit_message(self, message: MessageEnvelope) -> bool:
        """提交消息进行处理"""
        if not self._running:
            return False
        
        try:
            # 压缩消息（如果需要）
            if self.config.compression_enabled and len(message.payload) > self.config.compression_threshold:
                compressed_payload = self.compressor.compress(message.payload, self.config.compression_type)
                if len(compressed_payload) < len(message.payload):
                    message.payload = compressed_payload
                    message.compressed = True
                    message.compression_type = self.config.compression_type
            
            # 根据优先级放入相应队列
            priority_queue = self._priority_queues[message.priority]
            await priority_queue.put(message)
            
            return True
        except asyncio.QueueFull:
            logger.warning(f"优先级队列 {message.priority} 已满，消息被丢弃")
            return False
        except Exception as e:
            logger.error(f"提交消息失败: {e}")
            return False
    
    async def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        logger.info(f"工作线程 {worker_name} 已启动")
        
        while self._running:
            try:
                # 按优先级处理消息
                message = await self._get_next_message()
                if message:
                    await self._process_single_message(message)
                else:
                    # 没有消息时短暂休眠
                    await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"工作线程 {worker_name} 处理消息时出错: {e}")
        
        logger.info(f"工作线程 {worker_name} 已停止")
    
    async def _get_next_message(self) -> Optional[MessageEnvelope]:
        """按优先级获取下一个消息"""
        # 按优先级顺序检查队列
        for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                        MessagePriority.NORMAL, MessagePriority.LOW]:
            queue = self._priority_queues[priority]
            try:
                return queue.get_nowait()
            except asyncio.QueueEmpty:
                continue
        
        return None
    
    async def _process_single_message(self, message: MessageEnvelope):
        """处理单个消息"""
        start_time = time.time()
        
        try:
            # 解压缩消息（如果需要）
            if message.compressed and message.compression_type:
                message.payload = self.compressor.decompress(message.payload, message.compression_type)
                message.compressed = False
                message.compression_type = None
            
            # 调用所有处理器
            success = True
            for processor in self._processors:
                try:
                    result = await processor.process_message(message)
                    if not result:
                        success = False
                        break
                except Exception as e:
                    logger.error(f"处理器处理消息失败: {e}")
                    success = False
                    break
            
            # 更新统计信息
            processing_time = time.time() - start_time
            await self._update_stats(success, processing_time, 1)
            
            if not success and message.retry_count < self.config.max_retries:
                # 重试消息
                await self._retry_message(message)
        
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            await self._update_stats(False, time.time() - start_time, 1)
    
    async def _retry_message(self, message: MessageEnvelope):
        """重试消息"""
        message.retry_count += 1
        
        # 计算重试延迟
        delay = self.config.retry_delay
        if self.config.exponential_backoff:
            delay *= (2 ** (message.retry_count - 1))
        
        # 延迟后重新提交
        await asyncio.sleep(delay)
        await self.submit_message(message)
        
        async with self._stats_lock:
            self._stats.total_retries += 1
    
    async def _batch_processor_loop(self):
        """批处理器循环"""
        logger.info("批处理器已启动")
        
        while self._running:
            try:
                await asyncio.sleep(0.1)  # 检查间隔
                
                async with self._batch_lock:
                    current_time = time.time()
                    
                    # 检查是否需要处理批次
                    should_process = (
                        len(self._batch_buffer) >= self.config.batch_size or
                        (len(self._batch_buffer) > 0 and 
                         current_time - self._last_batch_time >= self.config.batch_timeout)
                    )
                    
                    if should_process and self._batch_buffer:
                        batch = self._batch_buffer.copy()
                        self._batch_buffer.clear()
                        self._last_batch_time = current_time
                        
                        # 异步处理批次
                        asyncio.create_task(self._process_batch(batch))
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"批处理器出错: {e}")
        
        logger.info("批处理器已停止")
    
    async def _process_batch(self, batch: List[MessageEnvelope]):
        """处理消息批次"""
        start_time = time.time()
        
        try:
            # 调用所有处理器的批处理方法
            results = []
            for processor in self._processors:
                try:
                    batch_results = await processor.process_batch(batch)
                    results.extend(batch_results)
                except Exception as e:
                    logger.error(f"批处理器处理失败: {e}")
                    results.extend([False] * len(batch))
            
            # 统计成功和失败的消息
            successful = sum(1 for result in results if result)
            failed = len(results) - successful
            
            # 更新统计信息
            processing_time = time.time() - start_time
            await self._update_stats(failed == 0, processing_time, len(batch))
            
            # 处理失败的消息
            for i, (message, success) in enumerate(zip(batch, results)):
                if not success and message.retry_count < self.config.max_retries:
                    await self._retry_message(message)
        
        except Exception as e:
            logger.error(f"批处理出错: {e}")
            await self._update_stats(False, time.time() - start_time, len(batch))
    
    async def _update_stats(self, success: bool, processing_time: float, message_count: int):
        """更新统计信息"""
        async with self._stats_lock:
            if success:
                self._stats.total_processed += message_count
            else:
                self._stats.total_failed += message_count
            
            # 更新平均处理时间
            total_messages = self._stats.total_processed + self._stats.total_failed
            if total_messages > 0:
                self._stats.avg_processing_time = (
                    (self._stats.avg_processing_time * (total_messages - message_count) + 
                     processing_time * message_count) / total_messages
                )
            
            # 更新队列大小
            self._stats.queue_size = sum(
                queue.qsize() for queue in self._priority_queues.values()
            )
    
    async def _stats_loop(self):
        """统计信息收集循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.stats_interval)
                
                # 收集内存池统计
                pool_stats = self.memory_pool.get_stats()
                
                # 记录统计信息
                async with self._stats_lock:
                    logger.info(
                        f"消息处理统计 - "
                        f"已处理: {self._stats.total_processed}, "
                        f"失败: {self._stats.total_failed}, "
                        f"重试: {self._stats.total_retries}, "
                        f"平均处理时间: {self._stats.avg_processing_time:.3f}s, "
                        f"队列大小: {self._stats.queue_size}, "
                        f"内存池命中率: {pool_stats.get('pool_hits', 0) / max(1, pool_stats.get('pool_hits', 0) + pool_stats.get('pool_misses', 0)) * 100:.1f}%"
                    )
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"统计收集出错: {e}")
    
    def get_stats(self) -> ProcessingStats:
        """获取处理统计信息"""
        return self._stats
    
    def get_queue_sizes(self) -> Dict[str, int]:
        """获取队列大小"""
        return {
            priority.name: queue.qsize()
            for priority, queue in self._priority_queues.items()
        }


class KafkaMessageProcessor(MessageProcessor):
    """Kafka消息处理器"""
    
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer
    
    async def process_message(self, message: MessageEnvelope) -> bool:
        """处理单个消息"""
        try:
            await self.producer.send(
                topic=message.topic,
                value=message.payload,
                headers=[(k, v.encode()) for k, v in message.attributes.items()]
            )
            return True
        except Exception as e:
            logger.error(f"Kafka消息发送失败: {e}")
            return False
    
    async def process_batch(self, messages: List[MessageEnvelope]) -> List[bool]:
        """批处理消息"""
        results = []
        
        try:
            # 发送所有消息
            futures = []
            for message in messages:
                future = await self.producer.send(
                    topic=message.topic,
                    value=message.payload,
                    headers=[(k, v.encode()) for k, v in message.attributes.items()]
                )
                futures.append(future)
            
            # 等待所有消息发送完成
            for future in futures:
                try:
                    await future
                    results.append(True)
                except Exception as e:
                    logger.error(f"批处理消息发送失败: {e}")
                    results.append(False)
        
        except Exception as e:
            logger.error(f"批处理发送失败: {e}")
            results = [False] * len(messages)
        
        return results


# 消息处理器工厂
class MessageProcessorFactory:
    """消息处理器工厂"""
    
    @staticmethod
    def create_high_performance_processor(
        config: Optional[ProcessorConfig] = None
    ) -> HighPerformanceMessageProcessor:
        """创建高性能消息处理器"""
        if config is None:
            config = ProcessorConfig()
        
        return HighPerformanceMessageProcessor(config)
    
    @staticmethod
    def create_kafka_processor(producer: AIOKafkaProducer) -> KafkaMessageProcessor:
        """创建Kafka消息处理器"""
        return KafkaMessageProcessor(producer) 