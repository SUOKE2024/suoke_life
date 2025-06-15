#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实时流处理引擎 - 支持事件驱动的RAG处理和流式查询
"""

import asyncio
import time
import uuid
import json
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import weakref
from loguru import logger

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class EventType(str, Enum):
    """事件类型"""
    USER_QUERY = "user_query"           # 用户查询
    DATA_UPDATE = "data_update"         # 数据更新
    MODEL_UPDATE = "model_update"       # 模型更新
    SYSTEM_ALERT = "system_alert"       # 系统告警
    HEALTH_CHECK = "health_check"       # 健康检查
    CACHE_INVALIDATION = "cache_invalidation"  # 缓存失效
    USER_FEEDBACK = "user_feedback"     # 用户反馈
    BATCH_COMPLETE = "batch_complete"   # 批处理完成


class EventPriority(int, Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class StreamState(str, Enum):
    """流状态"""
    IDLE = "idle"                       # 空闲
    PROCESSING = "processing"           # 处理中
    BACKPRESSURE = "backpressure"      # 背压
    ERROR = "error"                     # 错误
    SHUTDOWN = "shutdown"               # 关闭


@dataclass
class StreamEvent:
    """流事件"""
    id: str
    type: EventType
    priority: EventPriority
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


@dataclass
class ProcessingResult:
    """处理结果"""
    event_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "processing_time": self.processing_time,
            "metadata": self.metadata
        }


class EventHandler:
    """事件处理器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.processed_count = 0
        self.error_count = 0
    
    async def can_handle(self, event: StreamEvent) -> bool:
        """检查是否能处理该事件"""
        return self.enabled
    
    async def handle(self, event: StreamEvent) -> ProcessingResult:
        """处理事件"""
        raise NotImplementedError
    
    async def on_error(self, event: StreamEvent, error: Exception) -> bool:
        """错误处理，返回是否应该重试"""
        logger.error(f"事件处理失败: {self.name} - {error}")
        self.error_count += 1
        return event.retry_count < event.max_retries


class RAGQueryHandler(EventHandler):
    """RAG查询处理器"""
    
    def __init__(self, rag_service):
        super().__init__("rag_query_handler")
        self.rag_service = rag_service
    
    async def can_handle(self, event: StreamEvent) -> bool:
        """检查是否能处理RAG查询事件"""
        return (await super().can_handle(event) and 
                event.type == EventType.USER_QUERY)
    
    @trace_operation("stream.rag_query", SpanKind.INTERNAL)
    async def handle(self, event: StreamEvent) -> ProcessingResult:
        """处理RAG查询"""
        start_time = time.time()
        
        try:
            query = event.payload.get("query", "")
            user_id = event.payload.get("user_id", "anonymous")
            context = event.payload.get("context", {})
            
            # 执行RAG查询
            result = await self.rag_service.query(
                query=query,
                user_id=user_id,
                context=context
            )
            
            self.processed_count += 1
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                event_id=event.id,
                success=True,
                result=result,
                processing_time=processing_time,
                metadata={
                    "query_length": len(query),
                    "user_id": user_id,
                    "handler": self.name
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                event_id=event.id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                metadata={"handler": self.name}
            )


class DataUpdateHandler(EventHandler):
    """数据更新处理器"""
    
    def __init__(self, indexer_service):
        super().__init__("data_update_handler")
        self.indexer_service = indexer_service
    
    async def can_handle(self, event: StreamEvent) -> bool:
        """检查是否能处理数据更新事件"""
        return (await super().can_handle(event) and 
                event.type == EventType.DATA_UPDATE)
    
    @trace_operation("stream.data_update", SpanKind.INTERNAL)
    async def handle(self, event: StreamEvent) -> ProcessingResult:
        """处理数据更新"""
        start_time = time.time()
        
        try:
            operation = event.payload.get("operation", "update")  # update, delete, insert
            document_id = event.payload.get("document_id")
            document_data = event.payload.get("document_data", {})
            
            if operation == "update" or operation == "insert":
                result = await self.indexer_service.index_document(
                    document_id, document_data
                )
            elif operation == "delete":
                result = await self.indexer_service.delete_document(document_id)
            else:
                raise ValueError(f"不支持的操作类型: {operation}")
            
            self.processed_count += 1
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                event_id=event.id,
                success=True,
                result=result,
                processing_time=processing_time,
                metadata={
                    "operation": operation,
                    "document_id": document_id,
                    "handler": self.name
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                event_id=event.id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                metadata={"handler": self.name}
            )


class CacheInvalidationHandler(EventHandler):
    """缓存失效处理器"""
    
    def __init__(self, cache_service):
        super().__init__("cache_invalidation_handler")
        self.cache_service = cache_service
    
    async def can_handle(self, event: StreamEvent) -> bool:
        """检查是否能处理缓存失效事件"""
        return (await super().can_handle(event) and 
                event.type == EventType.CACHE_INVALIDATION)
    
    @trace_operation("stream.cache_invalidation", SpanKind.INTERNAL)
    async def handle(self, event: StreamEvent) -> ProcessingResult:
        """处理缓存失效"""
        start_time = time.time()
        
        try:
            cache_keys = event.payload.get("cache_keys", [])
            cache_patterns = event.payload.get("cache_patterns", [])
            
            # 删除指定的缓存键
            for key in cache_keys:
                await self.cache_service.delete(key)
            
            # 删除匹配模式的缓存
            for pattern in cache_patterns:
                await self.cache_service.delete_pattern(pattern)
            
            self.processed_count += 1
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                event_id=event.id,
                success=True,
                result={"invalidated_keys": len(cache_keys), "patterns": len(cache_patterns)},
                processing_time=processing_time,
                metadata={"handler": self.name}
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                event_id=event.id,
                success=False,
                error=str(e),
                processing_time=processing_time,
                metadata={"handler": self.name}
            )


class EventQueue:
    """事件队列"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues = {priority: deque() for priority in EventPriority}
        self.total_size = 0
        self._lock = asyncio.Lock()
    
    async def put(self, event: StreamEvent) -> bool:
        """添加事件到队列"""
        async with self._lock:
            if self.total_size >= self.max_size:
                # 队列满了，丢弃低优先级事件
                if await self._drop_low_priority_event():
                    logger.warning("队列满，丢弃低优先级事件")
                else:
                    logger.error("队列满，无法添加新事件")
                    return False
            
            self.queues[event.priority].append(event)
            self.total_size += 1
            return True
    
    async def get(self) -> Optional[StreamEvent]:
        """从队列获取事件（按优先级）"""
        async with self._lock:
            # 按优先级从高到低获取事件
            for priority in sorted(EventPriority, key=lambda x: x.value, reverse=True):
                if self.queues[priority]:
                    event = self.queues[priority].popleft()
                    self.total_size -= 1
                    return event
            return None
    
    async def _drop_low_priority_event(self) -> bool:
        """丢弃低优先级事件"""
        for priority in sorted(EventPriority, key=lambda x: x.value):
            if self.queues[priority]:
                self.queues[priority].popleft()
                self.total_size -= 1
                return True
        return False
    
    async def size(self) -> int:
        """获取队列大小"""
        return self.total_size
    
    async def is_empty(self) -> bool:
        """检查队列是否为空"""
        return self.total_size == 0


class BackpressureController:
    """背压控制器"""
    
    def __init__(
        self,
        max_queue_size: int = 10000,
        max_processing_rate: int = 1000,  # 每秒最大处理数
        backpressure_threshold: float = 0.8
    ):
        self.max_queue_size = max_queue_size
        self.max_processing_rate = max_processing_rate
        self.backpressure_threshold = backpressure_threshold
        self.processing_count = 0
        self.last_reset_time = time.time()
        self.backpressure_active = False
    
    async def should_apply_backpressure(self, queue_size: int) -> bool:
        """检查是否应该应用背压"""
        current_time = time.time()
        
        # 重置处理计数（每秒）
        if current_time - self.last_reset_time >= 1.0:
            self.processing_count = 0
            self.last_reset_time = current_time
        
        # 检查队列大小
        queue_pressure = queue_size / self.max_queue_size
        
        # 检查处理速率
        rate_pressure = self.processing_count / self.max_processing_rate
        
        # 如果任一指标超过阈值，应用背压
        should_apply = (queue_pressure > self.backpressure_threshold or 
                       rate_pressure > self.backpressure_threshold)
        
        if should_apply != self.backpressure_active:
            self.backpressure_active = should_apply
            if should_apply:
                logger.warning(f"背压激活: 队列压力={queue_pressure:.2f}, 速率压力={rate_pressure:.2f}")
            else:
                logger.info("背压解除")
        
        return should_apply
    
    async def record_processing(self):
        """记录处理事件"""
        self.processing_count += 1
    
    async def get_delay(self) -> float:
        """获取背压延迟时间"""
        if self.backpressure_active:
            return 0.1  # 100ms延迟
        return 0.0


class StreamProcessor:
    """流处理器"""
    
    def __init__(
        self,
        metrics_collector: Optional[MetricsCollector] = None,
        max_workers: int = 10,
        max_queue_size: int = 10000
    ):
        self.metrics_collector = metrics_collector
        self.max_workers = max_workers
        self.event_queue = EventQueue(max_queue_size)
        self.backpressure_controller = BackpressureController(max_queue_size)
        
        # 事件处理器
        self.handlers: List[EventHandler] = []
        self.handler_registry: Dict[EventType, List[EventHandler]] = {}
        
        # 状态管理
        self.state = StreamState.IDLE
        self.workers: List[asyncio.Task] = []
        self.running = False
        
        # 统计信息
        self.processed_events = 0
        self.failed_events = 0
        self.start_time = None
        
        # 结果回调
        self.result_callbacks: List[Callable] = []
    
    def register_handler(self, handler: EventHandler):
        """注册事件处理器"""
        self.handlers.append(handler)
        logger.info(f"注册事件处理器: {handler.name}")
    
    def add_result_callback(self, callback: Callable):
        """添加结果回调"""
        self.result_callbacks.append(callback)
    
    async def start(self):
        """启动流处理器"""
        if self.running:
            logger.warning("流处理器已在运行")
            return
        
        self.running = True
        self.state = StreamState.PROCESSING
        self.start_time = time.time()
        
        # 启动工作线程
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.workers.append(worker)
        
        logger.info(f"流处理器已启动，工作线程数: {self.max_workers}")
    
    async def stop(self):
        """停止流处理器"""
        if not self.running:
            return
        
        self.running = False
        self.state = StreamState.SHUTDOWN
        
        # 等待所有工作线程完成
        if self.workers:
            await asyncio.gather(*self.workers, return_exceptions=True)
            self.workers.clear()
        
        logger.info("流处理器已停止")
    
    async def submit_event(self, event: StreamEvent) -> bool:
        """提交事件到处理队列"""
        if not self.running:
            logger.error("流处理器未运行，无法提交事件")
            return False
        
        # 检查背压
        queue_size = await self.event_queue.size()
        if await self.backpressure_controller.should_apply_backpressure(queue_size):
            self.state = StreamState.BACKPRESSURE
            delay = await self.backpressure_controller.get_delay()
            if delay > 0:
                await asyncio.sleep(delay)
        else:
            self.state = StreamState.PROCESSING
        
        success = await self.event_queue.put(event)
        
        if success and self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "stream_events_submitted",
                {"type": event.type.value, "priority": event.priority.name}
            )
        
        return success
    
    async def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        logger.info(f"工作线程启动: {worker_name}")
        
        while self.running:
            try:
                # 获取事件
                event = await self.event_queue.get()
                if event is None:
                    await asyncio.sleep(0.01)  # 短暂休眠
                    continue
                
                # 处理事件
                result = await self._process_event(event)
                
                # 记录处理
                await self.backpressure_controller.record_processing()
                
                # 更新统计
                if result.success:
                    self.processed_events += 1
                else:
                    self.failed_events += 1
                
                # 调用结果回调
                for callback in self.result_callbacks:
                    try:
                        await callback(event, result)
                    except Exception as e:
                        logger.error(f"结果回调失败: {e}")
                
                # 记录指标
                if self.metrics_collector:
                    await self.metrics_collector.increment_counter(
                        "stream_events_processed",
                        {
                            "type": event.type.value,
                            "success": str(result.success),
                            "worker": worker_name
                        }
                    )
                    
                    await self.metrics_collector.record_histogram(
                        "stream_processing_duration",
                        result.processing_time,
                        {"type": event.type.value, "worker": worker_name}
                    )
                
            except Exception as e:
                logger.error(f"工作线程错误 {worker_name}: {e}")
                await asyncio.sleep(1)  # 错误后休眠
        
        logger.info(f"工作线程停止: {worker_name}")
    
    @trace_operation("stream.process_event", SpanKind.INTERNAL)
    async def _process_event(self, event: StreamEvent) -> ProcessingResult:
        """处理单个事件"""
        # 查找合适的处理器
        suitable_handlers = []
        for handler in self.handlers:
            if await handler.can_handle(event):
                suitable_handlers.append(handler)
        
        if not suitable_handlers:
            return ProcessingResult(
                event_id=event.id,
                success=False,
                error="没有找到合适的处理器",
                metadata={"event_type": event.type.value}
            )
        
        # 使用第一个合适的处理器
        handler = suitable_handlers[0]
        
        try:
            result = await handler.handle(event)
            return result
            
        except Exception as e:
            # 错误处理
            should_retry = await handler.on_error(event, e)
            
            if should_retry and event.retry_count < event.max_retries:
                # 重试
                event.retry_count += 1
                await self.event_queue.put(event)
                
                return ProcessingResult(
                    event_id=event.id,
                    success=False,
                    error=f"处理失败，已重试: {str(e)}",
                    metadata={"retry_count": event.retry_count, "handler": handler.name}
                )
            else:
                return ProcessingResult(
                    event_id=event.id,
                    success=False,
                    error=str(e),
                    metadata={"handler": handler.name, "max_retries_exceeded": True}
                )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计"""
        uptime = time.time() - self.start_time if self.start_time else 0
        queue_size = await self.event_queue.size()
        
        handler_stats = {}
        for handler in self.handlers:
            handler_stats[handler.name] = {
                "processed_count": handler.processed_count,
                "error_count": handler.error_count,
                "enabled": handler.enabled
            }
        
        return {
            "state": self.state.value,
            "running": self.running,
            "uptime": uptime,
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "queue_size": queue_size,
            "active_workers": len(self.workers),
            "backpressure_active": self.backpressure_controller.backpressure_active,
            "handlers": handler_stats
        }


class StreamingRAGProcessor:
    """流式RAG处理器"""
    
    def __init__(self, stream_processor: StreamProcessor):
        self.stream_processor = stream_processor
    
    async def stream_query(
        self,
        query: str,
        user_id: str = "anonymous",
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """流式RAG查询"""
        correlation_id = str(uuid.uuid4())
        
        # 创建查询事件
        event = StreamEvent(
            id=str(uuid.uuid4()),
            type=EventType.USER_QUERY,
            priority=EventPriority.NORMAL,
            payload={
                "query": query,
                "user_id": user_id,
                "context": context or {},
                "streaming": True
            },
            correlation_id=correlation_id
        )
        
        # 提交事件
        success = await self.stream_processor.submit_event(event)
        if not success:
            yield {"error": "无法提交查询事件"}
            return
        
        # 等待并流式返回结果
        # 这里应该实现实际的流式处理逻辑
        # 简化示例：
        yield {"status": "processing", "correlation_id": correlation_id}
        
        # 模拟流式响应
        for i in range(5):
            await asyncio.sleep(0.1)
            yield {
                "chunk": f"响应片段 {i+1}",
                "correlation_id": correlation_id,
                "progress": (i + 1) / 5
            }
        
        yield {"status": "completed", "correlation_id": correlation_id}


# 全局流处理器实例
_stream_processor: Optional[StreamProcessor] = None


def initialize_stream_processor(
    metrics_collector: Optional[MetricsCollector] = None,
    max_workers: int = 10,
    max_queue_size: int = 10000
) -> StreamProcessor:
    """初始化流处理器"""
    global _stream_processor
    _stream_processor = StreamProcessor(metrics_collector, max_workers, max_queue_size)
    return _stream_processor


def get_stream_processor() -> Optional[StreamProcessor]:
    """获取流处理器实例"""
    return _stream_processor


# 便捷的事件提交函数
async def submit_user_query(
    query: str,
    user_id: str = "anonymous",
    context: Optional[Dict[str, Any]] = None,
    priority: EventPriority = EventPriority.NORMAL
) -> bool:
    """提交用户查询事件"""
    if not _stream_processor:
        return False
    
    event = StreamEvent(
        id=str(uuid.uuid4()),
        type=EventType.USER_QUERY,
        priority=priority,
        payload={
            "query": query,
            "user_id": user_id,
            "context": context or {}
        }
    )
    
    return await _stream_processor.submit_event(event)


async def submit_data_update(
    operation: str,
    document_id: str,
    document_data: Optional[Dict[str, Any]] = None,
    priority: EventPriority = EventPriority.HIGH
) -> bool:
    """提交数据更新事件"""
    if not _stream_processor:
        return False
    
    event = StreamEvent(
        id=str(uuid.uuid4()),
        type=EventType.DATA_UPDATE,
        priority=priority,
        payload={
            "operation": operation,
            "document_id": document_id,
            "document_data": document_data or {}
        }
    )
    
    return await _stream_processor.submit_event(event)


async def submit_cache_invalidation(
    cache_keys: Optional[List[str]] = None,
    cache_patterns: Optional[List[str]] = None,
    priority: EventPriority = EventPriority.HIGH
) -> bool:
    """提交缓存失效事件"""
    if not _stream_processor:
        return False
    
    event = StreamEvent(
        id=str(uuid.uuid4()),
        type=EventType.CACHE_INVALIDATION,
        priority=priority,
        payload={
            "cache_keys": cache_keys or [],
            "cache_patterns": cache_patterns or []
        }
    )
    
    return await _stream_processor.submit_event(event) 