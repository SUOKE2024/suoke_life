"""
retry_handler - 索克生活项目模块
"""

from collections import defaultdict
from dataclasses import dataclass, asdict
from enum import Enum
from internal.error.error_handler import MessageBusError, ErrorCode
from internal.model.message import Message
from typing import Dict, Any, Optional, Callable, List
import asyncio
import json
import logging
import random
import time

"""
消息重试和死信队列处理机制
"""



logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """重试策略"""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CUSTOM = "custom"


@dataclass
class RetryConfig:
    """重试配置"""
    max_attempts: int = 3
    initial_delay: float = 1.0  # 秒
    max_delay: float = 300.0  # 最大延迟5分钟
    backoff_multiplier: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True  # 添加随机抖动
    retry_on_errors: List[ErrorCode] = None


@dataclass
class RetryAttempt:
    """重试尝试记录"""
    attempt_number: int
    timestamp: float
    error_code: str
    error_message: str
    delay_before_retry: float


@dataclass
class RetryableMessage:
    """可重试消息"""
    original_message: Message
    retry_config: RetryConfig
    attempts: List[RetryAttempt]
    next_retry_time: float
    created_at: float
    last_error: Optional[MessageBusError] = None
    
    @property
    def attempt_count(self) -> int:
        return len(self.attempts)
    
    @property
    def is_exhausted(self) -> bool:
        return self.attempt_count >= self.retry_config.max_attempts
    
    @property
    def should_retry_now(self) -> bool:
        return time.time() >= self.next_retry_time


class DeadLetterQueue:
    """死信队列"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.messages: Dict[str, RetryableMessage] = {}
        self.stats = defaultdict(int)
        
    async def add_message(self, retryable_message: RetryableMessage):
        """添加消息到死信队列"""
        if len(self.messages) >= self.max_size:
            # 移除最旧的消息
            oldest_key = min(self.messages.keys(), 
                           key=lambda k: self.messages[k].created_at)
            del self.messages[oldest_key]
            self.stats['evicted'] += 1
        
        message_id = retryable_message.original_message.message_id
        self.messages[message_id] = retryable_message
        self.stats['added'] += 1
        
        logger.warning(
            f"Message {message_id} added to dead letter queue after "
            f"{retryable_message.attempt_count} attempts"
        )
    
    async def get_message(self, message_id: str) -> Optional[RetryableMessage]:
        """获取死信消息"""
        return self.messages.get(message_id)
    
    async def remove_message(self, message_id: str) -> bool:
        """从死信队列移除消息"""
        if message_id in self.messages:
            del self.messages[message_id]
            self.stats['removed'] += 1
            return True
        return False
    
    async def list_messages(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[RetryableMessage]:
        """列出死信消息"""
        messages = list(self.messages.values())
        messages.sort(key=lambda m: m.created_at, reverse=True)
        return messages[offset:offset + limit]
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取死信队列统计"""
        return {
            'total_messages': len(self.messages),
            'max_size': self.max_size,
            'stats': dict(self.stats)
        }
    
    async def clear(self):
        """清空死信队列"""
        count = len(self.messages)
        self.messages.clear()
        self.stats['cleared'] += count
        logger.info(f"Cleared {count} messages from dead letter queue")


class RetryHandler:
    """重试处理器"""
    
    def __init__(self, dead_letter_queue: DeadLetterQueue):
        self.dead_letter_queue = dead_letter_queue
        self.pending_retries: Dict[str, RetryableMessage] = {}
        self.retry_queue = asyncio.PriorityQueue()
        self.running = False
        self.stats = defaultdict(int)
        
    async def start(self):
        """启动重试处理器"""
        self.running = True
        asyncio.create_task(self._process_retries())
        logger.info("Retry handler started")
    
    async def stop(self):
        """停止重试处理器"""
        self.running = False
        logger.info("Retry handler stopped")
    
    async def schedule_retry(
        self,
        message: Message,
        error: MessageBusError,
        retry_config: RetryConfig,
        retry_callback: Callable[[Message], Any]
    ) -> bool:
        """
        调度消息重试
        
        Args:
            message: 原始消息
            error: 发生的错误
            retry_config: 重试配置
            retry_callback: 重试回调函数
            
        Returns:
            bool: 是否成功调度重试
        """
        message_id = message.message_id
        
        # 检查是否应该重试此错误
        if not self._should_retry_error(error, retry_config):
            logger.info(f"Error {error.error_code} not configured for retry")
            return False
        
        # 获取或创建可重试消息
        if message_id in self.pending_retries:
            retryable_message = self.pending_retries[message_id]
        else:
            retryable_message = RetryableMessage(
                original_message=message,
                retry_config=retry_config,
                attempts=[],
                next_retry_time=0,
                created_at=time.time()
            )
            self.pending_retries[message_id] = retryable_message
        
        # 检查是否已达到最大重试次数
        if retryable_message.is_exhausted:
            await self._move_to_dead_letter_queue(retryable_message)
            return False
        
        # 记录重试尝试
        delay = self._calculate_delay(retryable_message)
        attempt = RetryAttempt(
            attempt_number=retryable_message.attempt_count + 1,
            timestamp=time.time(),
            error_code=error.error_code.value,
            error_message=error.message,
            delay_before_retry=delay
        )
        
        retryable_message.attempts.append(attempt)
        retryable_message.last_error = error
        retryable_message.next_retry_time = time.time() + delay
        
        # 添加到重试队列
        await self.retry_queue.put((
            retryable_message.next_retry_time,
            message_id,
            retry_callback
        ))
        
        self.stats['scheduled'] += 1
        logger.info(
            f"Scheduled retry for message {message_id}, "
            f"attempt {attempt.attempt_number}, delay {delay}s"
        )
        
        return True
    
    def _should_retry_error(
        self, 
        error: MessageBusError, 
        retry_config: RetryConfig
    ) -> bool:
        """判断是否应该重试此错误"""
        if retry_config.retry_on_errors is None:
            # 默认重试所有错误，除了验证错误
            return error.error_code != ErrorCode.VALIDATION_ERROR
        
        return error.error_code in retry_config.retry_on_errors
    
    def _calculate_delay(self, retryable_message: RetryableMessage) -> float:
        """计算重试延迟"""
        config = retryable_message.retry_config
        attempt_number = retryable_message.attempt_count
        
        if config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.initial_delay
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.initial_delay * (config.backoff_multiplier ** (attempt_number - 1))
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.initial_delay * attempt_number
        else:
            delay = config.initial_delay
        
        # 限制最大延迟
        delay = min(delay, config.max_delay)
        
        # 添加随机抖动
        if config.jitter:
            jitter_range = delay * 0.1  # 10%的抖动
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(delay, 0.1)  # 最小延迟0.1秒
    
    async def _process_retries(self):
        """处理重试队列"""
        while self.running:
            try:
                # 等待下一个重试任务
                retry_time, message_id, retry_callback = await asyncio.wait_for(
                    self.retry_queue.get(), timeout=1.0
                )
                
                # 检查是否到了重试时间
                current_time = time.time()
                if current_time < retry_time:
                    # 重新放回队列
                    await self.retry_queue.put((retry_time, message_id, retry_callback))
                    await asyncio.sleep(0.1)
                    continue
                
                # 执行重试
                await self._execute_retry(message_id, retry_callback)
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                logger.error(f"Error processing retries: {e}")
                await asyncio.sleep(1)
    
    async def _execute_retry(self, message_id: str, retry_callback: Callable):
        """执行重试"""
        if message_id not in self.pending_retries:
            logger.warning(f"Retry message {message_id} not found in pending retries")
            return
        
        retryable_message = self.pending_retries[message_id]
        
        try:
            # 执行重试回调
            await retry_callback(retryable_message.original_message)
            
            # 重试成功，从待重试列表中移除
            del self.pending_retries[message_id]
            self.stats['succeeded'] += 1
            
            logger.info(
                f"Message {message_id} retry succeeded after "
                f"{retryable_message.attempt_count} attempts"
            )
            
        except Exception as e:
            # 重试失败
            self.stats['failed'] += 1
            
            if isinstance(e, MessageBusError):
                error = e
            else:
                error = MessageBusError(
                    message=str(e),
                    error_code=ErrorCode.UNKNOWN_ERROR
                )
            
            # 检查是否需要继续重试
            if retryable_message.is_exhausted:
                await self._move_to_dead_letter_queue(retryable_message)
            else:
                # 重新调度重试
                await self.schedule_retry(
                    retryable_message.original_message,
                    error,
                    retryable_message.retry_config,
                    retry_callback
                )
    
    async def _move_to_dead_letter_queue(self, retryable_message: RetryableMessage):
        """将消息移动到死信队列"""
        message_id = retryable_message.original_message.message_id
        
        # 从待重试列表中移除
        if message_id in self.pending_retries:
            del self.pending_retries[message_id]
        
        # 添加到死信队列
        await self.dead_letter_queue.add_message(retryable_message)
        self.stats['moved_to_dlq'] += 1
    
    async def get_pending_retries(self) -> List[RetryableMessage]:
        """获取待重试消息列表"""
        return list(self.pending_retries.values())
    
    async def cancel_retry(self, message_id: str) -> bool:
        """取消消息重试"""
        if message_id in self.pending_retries:
            del self.pending_retries[message_id]
            self.stats['cancelled'] += 1
            logger.info(f"Cancelled retry for message {message_id}")
            return True
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取重试统计"""
        return {
            'pending_retries': len(self.pending_retries),
            'stats': dict(self.stats)
        }


class ReliabilityManager:
    """可靠性管理器"""
    
    def __init__(self):
        self.dead_letter_queue = DeadLetterQueue()
        self.retry_handler = RetryHandler(self.dead_letter_queue)
        
        # 默认重试配置
        self.default_retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )
    
    async def start(self):
        """启动可靠性管理器"""
        await self.retry_handler.start()
        logger.info("Reliability manager started")
    
    async def stop(self):
        """停止可靠性管理器"""
        await self.retry_handler.stop()
        logger.info("Reliability manager stopped")
    
    async def handle_message_failure(
        self,
        message: Message,
        error: MessageBusError,
        retry_callback: Callable[[Message], Any],
        retry_config: Optional[RetryConfig] = None
    ) -> bool:
        """
        处理消息失败
        
        Args:
            message: 失败的消息
            error: 错误信息
            retry_callback: 重试回调函数
            retry_config: 重试配置
            
        Returns:
            bool: 是否成功调度重试
        """
        config = retry_config or self.default_retry_config
        
        return await self.retry_handler.schedule_retry(
            message, error, config, retry_callback
        )
    
    async def get_dead_letter_messages(
        self, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[RetryableMessage]:
        """获取死信消息"""
        return await self.dead_letter_queue.list_messages(limit, offset)
    
    async def reprocess_dead_letter_message(
        self,
        message_id: str,
        retry_callback: Callable[[Message], Any]
    ) -> bool:
        """重新处理死信消息"""
        retryable_message = await self.dead_letter_queue.get_message(message_id)
        if not retryable_message:
            return False
        
        # 从死信队列移除
        await self.dead_letter_queue.remove_message(message_id)
        
        # 重置重试计数
        retryable_message.attempts.clear()
        
        # 重新调度重试
        return await self.retry_handler.schedule_retry(
            retryable_message.original_message,
            retryable_message.last_error or MessageBusError("Reprocessing from DLQ"),
            retryable_message.retry_config,
            retry_callback
        )
    
    async def get_reliability_stats(self) -> Dict[str, Any]:
        """获取可靠性统计"""
        retry_stats = await self.retry_handler.get_stats()
        dlq_stats = await self.dead_letter_queue.get_stats()
        
        return {
            'retry_handler': retry_stats,
            'dead_letter_queue': dlq_stats
        } 