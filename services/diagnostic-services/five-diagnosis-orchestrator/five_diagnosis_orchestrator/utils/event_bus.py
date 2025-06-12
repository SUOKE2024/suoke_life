"""
事件总线

实现异步事件发布和订阅机制，支持诊断过程中的事件通信
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import json
import weakref

from ..models.diagnosis_models import DiagnosisEvent


logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class EventHandler:
    """事件处理器"""
    handler_id: str
    callback: Callable[[DiagnosisEvent], Awaitable[None]]
    priority: EventPriority = EventPriority.NORMAL
    filter_func: Optional[Callable[[DiagnosisEvent], bool]] = None
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def __hash__(self):
        return hash(self.handler_id)


@dataclass
class EventMetrics:
    """事件指标"""
    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    total_handlers: int = 0
    active_subscriptions: int = 0
    average_processing_time: float = 0.0
    event_types: Dict[str, int] = field(default_factory=dict)


class EventBus:
    """事件总线"""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.metrics = EventMetrics()
        self.processing_task: Optional[asyncio.Task] = None
        self.dead_letter_queue: List[DiagnosisEvent] = []
        self.max_dead_letters = 1000
        self._initialized = False
        self._shutdown = False
        
        # 使用弱引用避免内存泄漏
        self._handler_refs: Dict[str, weakref.ref] = {}
    
    async def initialize(self) -> None:
        """初始化事件总线"""
        if self._initialized:
            return
            
        logger.info("初始化事件总线...")
        
        try:
            # 启动事件处理任务
            self.processing_task = asyncio.create_task(self._process_events())
            
            self._initialized = True
            logger.info("事件总线初始化完成")
            
        except Exception as e:
            logger.error(f"事件总线初始化失败: {e}")
            raise
    
    async def subscribe(
        self, 
        event_type: str, 
        callback: Callable[[DiagnosisEvent], Awaitable[None]],
        priority: EventPriority = EventPriority.NORMAL,
        filter_func: Optional[Callable[[DiagnosisEvent], bool]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """订阅事件"""
        if not self._initialized:
            await self.initialize()
        
        handler_id = f"{event_type}_{id(callback)}_{datetime.now().timestamp()}"
        
        handler = EventHandler(
            handler_id=handler_id,
            callback=callback,
            priority=priority,
            filter_func=filter_func,
            max_retries=max_retries,
            retry_delay=retry_delay
        )
        
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        
        # 按优先级排序
        self.subscribers[event_type].sort(key=lambda h: h.priority.value, reverse=True)
        
        # 更新指标
        self.metrics.total_handlers+=1
        self.metrics.active_subscriptions+=1
        
        logger.info(f"订阅事件: {event_type}, 处理器ID: {handler_id}")
        return handler_id
    
    async def unsubscribe(self, event_type: str, handler_id: str) -> bool:
        """取消订阅"""
        if event_type not in self.subscribers:
            return False
        
        handlers = self.subscribers[event_type]
        for i, handler in enumerate(handlers):
            if handler.handler_id==handler_id:
                del handlers[i]
                self.metrics.active_subscriptions-=1
                logger.info(f"取消订阅: {event_type}, 处理器ID: {handler_id}")
                return True
        
        return False
    
    async def publish(self, event_type: str, event: DiagnosisEvent) -> None:
        """发布事件"""
        if not self._initialized:
            await self.initialize()
        
        if self._shutdown:
            logger.warning("事件总线已关闭，无法发布事件")
            return
        
        try:
            # 设置事件类型
            event.event_type = event_type
            
            # 添加到队列
            await self.event_queue.put(event)
            
            # 更新指标
            self.metrics.total_events+=1
            self.metrics.event_types[event_type] = self.metrics.event_types.get(event_type, 0) + 1
            
            logger.debug(f"发布事件: {event_type}, 会话ID: {event.session_id}")
            
        except asyncio.QueueFull:
            logger.error(f"事件队列已满，丢弃事件: {event_type}")
            self._add_to_dead_letter_queue(event)
        except Exception as e:
            logger.error(f"发布事件失败: {event_type}, 错误: {e}")
            self._add_to_dead_letter_queue(event)
    
    async def publish_sync(self, event_type: str, event: DiagnosisEvent) -> None:
        """同步发布事件（立即处理）"""
        if not self._initialized:
            await self.initialize()
        
        event.event_type = event_type
        await self._handle_event(event)
    
    async def _process_events(self) -> None:
        """处理事件队列"""
        logger.info("开始处理事件队列...")
        
        while not self._shutdown:
            try:
                # 等待事件，设置超时避免无限等待
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # 处理事件
                await self._handle_event(event)
                
                # 标记任务完成
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                logger.error(f"处理事件时发生错误: {e}")
                await asyncio.sleep(0.1)  # 短暂延迟避免快速循环
    
    async def _handle_event(self, event: DiagnosisEvent) -> None:
        """处理单个事件"""
        start_time = datetime.now()
        
        try:
            event_type = event.event_type
            
            if event_type not in self.subscribers:
                logger.debug(f"没有订阅者处理事件: {event_type}")
                return
            
            handlers = self.subscribers[event_type]
            if not handlers:
                return
            
            # 并行处理所有处理器
            tasks = []
            for handler in handlers:
                # 应用过滤器
                if handler.filter_func and not handler.filter_func(event):
                    continue
                
                task = asyncio.create_task(
                    self._execute_handler(handler, event)
                )
                tasks.append(task)
            
            if tasks:
                # 等待所有处理器完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 检查结果
                success_count = 0
                for result in results:
                    if not isinstance(result, Exception):
                        success_count+=1
                    else:
                        logger.warning(f"事件处理器执行失败: {result}")
                
                if success_count > 0:
                    self.metrics.successful_events+=1
                else:
                    self.metrics.failed_events+=1
                    self._add_to_dead_letter_queue(event)
            
            # 更新处理时间指标
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_processing_time(processing_time)
            
        except Exception as e:
            logger.error(f"处理事件失败: {event.event_type}, 错误: {e}")
            self.metrics.failed_events+=1
            self._add_to_dead_letter_queue(event)
    
    async def _execute_handler(self, handler: EventHandler, event: DiagnosisEvent) -> None:
        """执行事件处理器"""
        retry_count = 0
        
        while retry_count<=handler.max_retries:
            try:
                await handler.callback(event)
                return  # 成功执行，退出重试循环
                
            except Exception as e:
                retry_count+=1
                logger.warning(
                    f"事件处理器执行失败 (重试 {retry_count}/{handler.max_retries}): "
                    f"{handler.handler_id}, 错误: {e}"
                )
                
                if retry_count<=handler.max_retries:
                    await asyncio.sleep(handler.retry_delay * retry_count)  # 指数退避
                else:
                    logger.error(f"事件处理器最终失败: {handler.handler_id}")
                    raise
    
    def _add_to_dead_letter_queue(self, event: DiagnosisEvent) -> None:
        """添加到死信队列"""
        if len(self.dead_letter_queue)>=self.max_dead_letters:
            # 移除最旧的事件
            self.dead_letter_queue.pop(0)
        
        self.dead_letter_queue.append(event)
        logger.warning(f"事件添加到死信队列: {event.event_type}")
    
    def _update_processing_time(self, processing_time: float) -> None:
        """更新平均处理时间"""
        total_processed = self.metrics.successful_events + self.metrics.failed_events
        if total_processed==1:
            self.metrics.average_processing_time = processing_time
        else:
            current_avg = self.metrics.average_processing_time
            self.metrics.average_processing_time = (
                (current_avg * (total_processed - 1) + processing_time) / total_processed
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """获取事件总线指标"""
        return {
            "total_events": self.metrics.total_events,
            "successful_events": self.metrics.successful_events,
            "failed_events": self.metrics.failed_events,
            "success_rate": (
                self.metrics.successful_events / max(self.metrics.total_events, 1)
            ),
            "total_handlers": self.metrics.total_handlers,
            "active_subscriptions": self.metrics.active_subscriptions,
            "average_processing_time": self.metrics.average_processing_time,
            "queue_size": self.event_queue.qsize(),
            "dead_letter_count": len(self.dead_letter_queue),
            "event_types": self.metrics.event_types.copy(),
            "subscribers_count": {
                event_type: len(handlers) 
                for event_type, handlers in self.subscribers.items()
            }
        }
    
    async def get_dead_letter_events(self, limit: int = 100) -> List[DiagnosisEvent]:
        """获取死信队列中的事件"""
        return self.dead_letter_queue[-limit:] if self.dead_letter_queue else []
    
    async def retry_dead_letter_events(self, event_types: Optional[List[str]] = None) -> int:
        """重试死信队列中的事件"""
        if not self.dead_letter_queue:
            return 0
        
        retry_count = 0
        events_to_retry = []
        
        # 筛选要重试的事件
        for event in self.dead_letter_queue:
            if event_types is None or event.event_type in event_types:
                events_to_retry.append(event)
        
        # 从死信队列中移除要重试的事件
        for event in events_to_retry:
            if event in self.dead_letter_queue:
                self.dead_letter_queue.remove(event)
        
        # 重新发布事件
        for event in events_to_retry:
            try:
                await self.publish(event.event_type, event)
                retry_count+=1
            except Exception as e:
                logger.error(f"重试死信事件失败: {event.event_type}, 错误: {e}")
                # 重新添加到死信队列
                self._add_to_dead_letter_queue(event)
        
        logger.info(f"重试了 {retry_count} 个死信事件")
        return retry_count
    
    async def clear_dead_letter_queue(self) -> int:
        """清空死信队列"""
        count = len(self.dead_letter_queue)
        self.dead_letter_queue.clear()
        logger.info(f"清空了 {count} 个死信事件")
        return count
    
    async def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """等待所有事件处理完成"""
        try:
            await asyncio.wait_for(self.event_queue.join(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning("等待事件处理完成超时")
    
    async def get_subscription_info(self) -> Dict[str, Any]:
        """获取订阅信息"""
        subscription_info = {}
        
        for event_type, handlers in self.subscribers.items():
            subscription_info[event_type] = {
                "handler_count": len(handlers),
                "handlers": [
                    {
                        "handler_id": handler.handler_id,
                        "priority": handler.priority.value,
                        "max_retries": handler.max_retries,
                        "retry_delay": handler.retry_delay,
                        "has_filter": handler.filter_func is not None
                    }
                    for handler in handlers
                ]
            }
        
        return subscription_info
    
    async def remove_all_subscribers(self, event_type: str) -> int:
        """移除指定事件类型的所有订阅者"""
        if event_type not in self.subscribers:
            return 0
        
        count = len(self.subscribers[event_type])
        self.subscribers[event_type].clear()
        self.metrics.active_subscriptions-=count
        
        logger.info(f"移除了事件类型 {event_type} 的 {count} 个订阅者")
        return count
    
    async def close(self) -> None:
        """关闭事件总线"""
        logger.info("关闭事件总线...")
        
        self._shutdown = True
        
        # 等待当前事件处理完成
        try:
            await asyncio.wait_for(self.wait_for_completion(), timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("等待事件处理完成超时，强制关闭")
        
        # 取消处理任务
        if self.processing_task and not self.processing_task.done():
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # 清理资源
        self.subscribers.clear()
        self._handler_refs.clear()
        
        # 清空队列
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                self.event_queue.task_done()
            except asyncio.QueueEmpty:
                break
        
        logger.info("事件总线已关闭")


# 全局事件总线实例
_global_event_bus: Optional[EventBus] = None


async def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
        await _global_event_bus.initialize()
    return _global_event_bus


async def close_global_event_bus() -> None:
    """关闭全局事件总线"""
    global _global_event_bus
    if _global_event_bus:
        await _global_event_bus.close()
        _global_event_bus = None


# 便捷函数
async def publish_event(event_type: str, session_id: str, data: Dict[str, Any]) -> None:
    """发布事件的便捷函数"""
    event_bus = await get_event_bus()
    event = DiagnosisEvent(
        session_id=session_id,
        event_type=event_type,
        data=data
    )
    await event_bus.publish(event_type, event)


async def subscribe_event(
    event_type: str, 
    callback: Callable[[DiagnosisEvent], Awaitable[None]],
   **kwargs
) -> str:
    """订阅事件的便捷函数"""
    event_bus = await get_event_bus()
    return await event_bus.subscribe(event_type, callback,**kwargs)