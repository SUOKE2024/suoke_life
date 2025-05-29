"""
事件总线模块
支持异步事件发布订阅、事件持久化、重试机制等功能
"""

import asyncio
import json
import logging
import pickle
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)


class EventStatus(Enum):
    """事件状态"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class EventPriority(Enum):
    """事件优先级"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """事件数据结构"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """从字典创建事件"""
        event = cls()
        event.id = data.get("id", event.id)
        event.type = data.get("type", "")
        event.source = data.get("source", "")
        event.data = data.get("data", {})
        event.timestamp = datetime.fromisoformat(
            data.get("timestamp", datetime.now().isoformat())
        )
        event.priority = EventPriority(data.get("priority", EventPriority.NORMAL.value))
        event.status = EventStatus(data.get("status", EventStatus.PENDING.value))
        event.retry_count = data.get("retry_count", 0)
        event.max_retries = data.get("max_retries", 3)
        event.correlation_id = data.get("correlation_id")
        event.metadata = data.get("metadata", {})
        return event


@dataclass
class EventHandler:
    """事件处理器"""

    handler_id: str
    event_type: str
    handler_func: Callable[[Event], Any]
    async_handler: bool = True
    priority: int = 0
    filter_func: Optional[Callable[[Event], bool]] = None

    async def handle(self, event: Event) -> Any:
        """处理事件"""
        # 检查过滤条件
        if self.filter_func and not self.filter_func(event):
            return None

        try:
            if self.async_handler:
                return await self.handler_func(event)
            else:
                return self.handler_func(event)
        except Exception as e:
            logger.error(f"事件处理器 {self.handler_id} 处理失败: {e}")
            raise


class EventStore(ABC):
    """事件存储抽象基类"""

    @abstractmethod
    async def save_event(self, event: Event) -> bool:
        """保存事件"""
        pass

    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[Event]:
        """获取事件"""
        pass

    @abstractmethod
    async def update_event_status(self, event_id: str, status: EventStatus) -> bool:
        """更新事件状态"""
        pass

    @abstractmethod
    async def get_pending_events(self, limit: int = 100) -> List[Event]:
        """获取待处理事件"""
        pass

    @abstractmethod
    async def get_failed_events(self, limit: int = 100) -> List[Event]:
        """获取失败事件"""
        pass


class MemoryEventStore(EventStore):
    """内存事件存储"""

    def __init__(self):
        self.events: Dict[str, Event] = {}
        self._lock = asyncio.Lock()

    async def save_event(self, event: Event) -> bool:
        """保存事件到内存"""
        async with self._lock:
            self.events[event.id] = event
            return True

    async def get_event(self, event_id: str) -> Optional[Event]:
        """从内存获取事件"""
        return self.events.get(event_id)

    async def update_event_status(self, event_id: str, status: EventStatus) -> bool:
        """更新事件状态"""
        async with self._lock:
            if event_id in self.events:
                self.events[event_id].status = status
                return True
            return False

    async def get_pending_events(self, limit: int = 100) -> List[Event]:
        """获取待处理事件"""
        pending_events = [
            event
            for event in self.events.values()
            if event.status == EventStatus.PENDING
        ]
        # 按优先级和时间排序
        pending_events.sort(key=lambda e: (e.priority.value, e.timestamp), reverse=True)
        return pending_events[:limit]

    async def get_failed_events(self, limit: int = 100) -> List[Event]:
        """获取失败事件"""
        failed_events = [
            event
            for event in self.events.values()
            if event.status == EventStatus.FAILED
        ]
        failed_events.sort(key=lambda e: e.timestamp, reverse=True)
        return failed_events[:limit]


class RedisEventStore(EventStore):
    """Redis事件存储"""

    def __init__(self, redis_client, prefix: str = "events"):
        self.redis = redis_client
        self.prefix = prefix

    def _make_key(self, event_id: str) -> str:
        """生成Redis键"""
        return f"{self.prefix}:{event_id}"

    async def save_event(self, event: Event) -> bool:
        """保存事件到Redis"""
        try:
            key = self._make_key(event.id)
            data = json.dumps(event.to_dict())
            await self.redis.set(key, data)

            # 添加到状态索引
            status_key = f"{self.prefix}:status:{event.status.value}"
            await self.redis.zadd(status_key, {event.id: event.timestamp.timestamp()})

            return True
        except Exception as e:
            logger.error(f"保存事件到Redis失败: {e}")
            return False

    async def get_event(self, event_id: str) -> Optional[Event]:
        """从Redis获取事件"""
        try:
            key = self._make_key(event_id)
            data = await self.redis.get(key)
            if data:
                event_dict = json.loads(data)
                return Event.from_dict(event_dict)
            return None
        except Exception as e:
            logger.error(f"从Redis获取事件失败: {e}")
            return None

    async def update_event_status(self, event_id: str, status: EventStatus) -> bool:
        """更新事件状态"""
        try:
            event = await self.get_event(event_id)
            if not event:
                return False

            # 从旧状态索引中移除
            old_status_key = f"{self.prefix}:status:{event.status.value}"
            await self.redis.zrem(old_status_key, event_id)

            # 更新事件状态
            event.status = status
            await self.save_event(event)

            return True
        except Exception as e:
            logger.error(f"更新事件状态失败: {e}")
            return False

    async def get_pending_events(self, limit: int = 100) -> List[Event]:
        """获取待处理事件"""
        try:
            status_key = f"{self.prefix}:status:{EventStatus.PENDING.value}"
            event_ids = await self.redis.zrange(status_key, 0, limit - 1)

            events = []
            for event_id in event_ids:
                event = await self.get_event(event_id.decode())
                if event:
                    events.append(event)

            return events
        except Exception as e:
            logger.error(f"获取待处理事件失败: {e}")
            return []

    async def get_failed_events(self, limit: int = 100) -> List[Event]:
        """获取失败事件"""
        try:
            status_key = f"{self.prefix}:status:{EventStatus.FAILED.value}"
            event_ids = await self.redis.zrevrange(status_key, 0, limit - 1)

            events = []
            for event_id in event_ids:
                event = await self.get_event(event_id.decode())
                if event:
                    events.append(event)

            return events
        except Exception as e:
            logger.error(f"获取失败事件失败: {e}")
            return []


class EventBus:
    """事件总线"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.event_store: Optional[EventStore] = None

        # 处理队列
        self.event_queue: asyncio.Queue = asyncio.Queue(
            maxsize=config.get("queue_size", 1000)
        )

        # 工作任务
        self.worker_tasks: List[asyncio.Task] = []
        self.retry_task: Optional[asyncio.Task] = None
        self.is_running = False

        # 配置参数
        self.worker_count = config.get("worker_count", 4)
        self.retry_interval = config.get("retry_interval", 60)
        self.enable_persistence = config.get("enable_persistence", True)

        logger.info("事件总线初始化完成")

    async def initialize(self, event_store: Optional[EventStore] = None):
        """初始化事件总线"""
        if self.enable_persistence:
            self.event_store = event_store or MemoryEventStore()

        # 启动工作线程
        await self.start_workers()

        logger.info("事件总线初始化完成")

    async def start_workers(self):
        """启动工作线程"""
        self.is_running = True

        # 启动事件处理工作线程
        for i in range(self.worker_count):
            task = asyncio.create_task(self._worker_loop(f"worker-{i}"))
            self.worker_tasks.append(task)

        # 启动重试任务
        if self.enable_persistence:
            self.retry_task = asyncio.create_task(self._retry_loop())

        logger.info(f"事件总线工作线程已启动，工作线程数: {self.worker_count}")

    async def stop_workers(self):
        """停止工作线程"""
        self.is_running = False

        # 停止工作线程
        for task in self.worker_tasks:
            task.cancel()

        if self.retry_task:
            self.retry_task.cancel()

        # 等待任务完成
        await asyncio.gather(
            *self.worker_tasks, self.retry_task, return_exceptions=True
        )

        self.worker_tasks.clear()
        self.retry_task = None

        logger.info("事件总线工作线程已停止")

    def subscribe(
        self,
        event_type: str,
        handler_func: Callable[[Event], Any],
        handler_id: Optional[str] = None,
        priority: int = 0,
        filter_func: Optional[Callable[[Event], bool]] = None,
        async_handler: bool = True,
    ) -> str:
        """订阅事件"""
        if handler_id is None:
            handler_id = f"{event_type}_{uuid.uuid4().hex[:8]}"

        handler = EventHandler(
            handler_id=handler_id,
            event_type=event_type,
            handler_func=handler_func,
            async_handler=async_handler,
            priority=priority,
            filter_func=filter_func,
        )

        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

        # 按优先级排序
        self.handlers[event_type].sort(key=lambda h: h.priority, reverse=True)

        logger.info(f"事件处理器已注册: {handler_id} -> {event_type}")
        return handler_id

    def unsubscribe(self, event_type: str, handler_id: str) -> bool:
        """取消订阅事件"""
        if event_type in self.handlers:
            self.handlers[event_type] = [
                h for h in self.handlers[event_type] if h.handler_id != handler_id
            ]
            logger.info(f"事件处理器已取消注册: {handler_id} -> {event_type}")
            return True
        return False

    async def publish(self, event: Event) -> bool:
        """发布事件"""
        try:
            # 持久化事件
            if self.event_store:
                await self.event_store.save_event(event)

            # 添加到处理队列
            await self.event_queue.put(event)

            logger.info(f"事件已发布: {event.id} ({event.type})")
            return True

        except asyncio.QueueFull:
            logger.error(f"事件队列已满，事件发布失败: {event.id}")
            return False
        except Exception as e:
            logger.error(f"事件发布失败: {e}")
            return False

    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        source: str = "unknown",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """发布事件的便捷方法"""
        event = Event(
            type=event_type,
            source=source,
            data=data,
            priority=priority,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

        success = await self.publish(event)
        return event.id if success else ""

    async def _worker_loop(self, worker_name: str):
        """工作线程循环"""
        logger.info(f"事件处理工作线程 {worker_name} 已启动")

        while self.is_running:
            try:
                # 获取事件
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # 处理事件
                await self._process_event(event)

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"工作线程 {worker_name} 处理事件失败: {e}")

        logger.info(f"事件处理工作线程 {worker_name} 已停止")

    async def _process_event(self, event: Event):
        """处理单个事件"""
        try:
            # 更新事件状态
            event.status = EventStatus.PROCESSING
            if self.event_store:
                await self.event_store.update_event_status(event.id, event.status)

            # 获取事件处理器
            handlers = self.handlers.get(event.type, [])
            if not handlers:
                logger.warning(f"没有找到事件类型 {event.type} 的处理器")
                event.status = EventStatus.COMPLETED
                if self.event_store:
                    await self.event_store.update_event_status(event.id, event.status)
                return

            # 执行所有处理器
            results = []
            for handler in handlers:
                try:
                    result = await handler.handle(event)
                    results.append(result)
                except Exception as e:
                    logger.error(f"事件处理器 {handler.handler_id} 执行失败: {e}")
                    raise

            # 标记为完成
            event.status = EventStatus.COMPLETED
            if self.event_store:
                await self.event_store.update_event_status(event.id, event.status)

            logger.debug(f"事件处理完成: {event.id} ({event.type})")

        except Exception as e:
            # 标记为失败
            event.status = EventStatus.FAILED
            event.retry_count += 1

            if self.event_store:
                await self.event_store.update_event_status(event.id, event.status)

            logger.error(f"事件处理失败: {event.id} ({event.type}) - {e}")

    async def _retry_loop(self):
        """重试循环"""
        logger.info("事件重试任务已启动")

        while self.is_running:
            try:
                # 获取失败的事件
                if self.event_store:
                    failed_events = await self.event_store.get_failed_events(50)

                    for event in failed_events:
                        # 检查是否可以重试
                        if event.retry_count < event.max_retries:
                            # 重新发布事件
                            event.status = EventStatus.RETRYING
                            await self.event_store.update_event_status(
                                event.id, event.status
                            )

                            # 添加到队列
                            await self.event_queue.put(event)
                            logger.info(
                                f"事件重试: {event.id} (第{event.retry_count}次)"
                            )

                # 等待下一次检查
                await asyncio.sleep(self.retry_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"重试任务失败: {e}")
                await asyncio.sleep(self.retry_interval)

        logger.info("事件重试任务已停止")

    async def get_event_stats(self) -> Dict[str, Any]:
        """获取事件统计"""
        stats = {
            "queue_size": self.event_queue.qsize(),
            "worker_count": len(self.worker_tasks),
            "is_running": self.is_running,
            "handlers": {
                event_type: len(handlers)
                for event_type, handlers in self.handlers.items()
            },
        }

        if self.event_store:
            pending_events = await self.event_store.get_pending_events(1000)
            failed_events = await self.event_store.get_failed_events(1000)

            stats.update(
                {
                    "pending_events": len(pending_events),
                    "failed_events": len(failed_events),
                }
            )

        return stats


# 全局事件总线实例
_event_bus: Optional[EventBus] = None


async def init_event_bus(
    config: Dict[str, Any], event_store: Optional[EventStore] = None
) -> EventBus:
    """初始化全局事件总线"""
    global _event_bus

    _event_bus = EventBus(config)
    await _event_bus.initialize(event_store)
    return _event_bus


def get_event_bus() -> EventBus:
    """获取全局事件总线"""
    if _event_bus is None:
        raise RuntimeError("事件总线未初始化，请先调用 init_event_bus")
    return _event_bus


# 装饰器支持
def event_handler(
    event_type: str, priority: int = 0, filter_func: Optional[Callable] = None
):
    """事件处理器装饰器"""

    def decorator(func):
        # 注册处理器
        get_event_bus().subscribe(
            event_type=event_type,
            handler_func=func,
            priority=priority,
            filter_func=filter_func,
        )
        return func

    return decorator
