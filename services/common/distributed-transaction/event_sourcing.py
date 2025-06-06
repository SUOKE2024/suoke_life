"""
event_sourcing - 索克生活项目模块
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import asyncio
import logging
import uuid

#!/usr/bin/env python3
"""
事件溯源（Event Sourcing）实现
提供基于事件的最终一致性解决方案
"""


logger = logging.getLogger(__name__)


@dataclass
class Event:
    """事件基类"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_id: str = ""
    aggregate_type: str = ""
    event_type: str = ""
    event_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """从字典创建"""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class EventStore(ABC):
    """事件存储抽象接口"""

    @abstractmethod
    async def append_event(self, event: Event) -> None:
        """追加事件"""
        pass

    @abstractmethod
    async def get_events(
        self, aggregate_id: str, from_version: int = 0, to_version: int | None = None
    ) -> list[Event]:
        """获取聚合的事件历史"""
        pass

    @abstractmethod
    async def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
        after_timestamp: datetime | None = None,
    ) -> list[Event]:
        """根据类型获取事件"""
        pass

    @abstractmethod
    async def get_snapshot(self, aggregate_id: str) -> dict[str, Any] | None:
        """获取快照"""
        pass

    @abstractmethod
    async def save_snapshot(
        self, aggregate_id: str, snapshot: dict[str, Any], version: int
    ) -> None:
        """保存快照"""
        pass


class InMemoryEventStore(EventStore):
    """内存事件存储（用于测试）"""

    def __init__(self):
        self.events: list[Event] = []
        self.snapshots: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def append_event(self, event: Event) -> None:
        """追加事件"""
        async with self._lock:
            self.events.append(event)
            logger.debug(f"追加事件: {event.event_type} for {event.aggregate_id}")

    async def get_events(
        self, aggregate_id: str, from_version: int = 0, to_version: int | None = None
    ) -> list[Event]:
        """获取聚合的事件历史"""
        async with self._lock:
            events = [
                e
                for e in self.events
                if e.aggregate_id == aggregate_id and e.version > from_version
            ]

            if to_version is not None:
                events = [e for e in events if e.version <= to_version]

            return sorted(events, key=lambda e: e.version)

    async def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100,
        after_timestamp: datetime | None = None,
    ) -> list[Event]:
        """根据类型获取事件"""
        async with self._lock:
            events = [e for e in self.events if e.event_type == event_type]

            if after_timestamp:
                events = [e for e in events if e.timestamp > after_timestamp]

            return sorted(events, key=lambda e: e.timestamp)[:limit]

    async def get_snapshot(self, aggregate_id: str) -> dict[str, Any] | None:
        """获取快照"""
        return self.snapshots.get(aggregate_id)

    async def save_snapshot(
        self, aggregate_id: str, snapshot: dict[str, Any], version: int
    ) -> None:
        """保存快照"""
        async with self._lock:
            self.snapshots[aggregate_id] = {
                "data": snapshot,
                "version": version,
                "timestamp": datetime.now().isoformat(),
            }


class AggregateRoot(ABC):
    """聚合根基类"""

    def __init__(self, aggregate_id: str | None = None):
        self.aggregate_id = aggregate_id or str(uuid.uuid4())
        self.version = 0
        self.uncommitted_events: list[Event] = []

    def apply_event(self, event: Event):
        """应用事件到聚合"""
        # 调用对应的事件处理方法
        handler_name = f"_handle_{event.event_type}"
        handler = getattr(self, handler_name, None)

        if handler:
            handler(event)
        else:
            logger.warning(f"未找到事件处理器: {handler_name}")

        self.version = event.version

    def raise_event(self, event_type: str, event_data: dict[str, Any]):
        """触发新事件"""
        event = Event(
            aggregate_id=self.aggregate_id,
            aggregate_type=self.__class__.__name__,
            event_type=event_type,
            event_data=event_data,
            version=self.version + 1,
        )

        # 应用事件
        self.apply_event(event)

        # 添加到未提交事件列表
        self.uncommitted_events.append(event)

    def mark_events_as_committed(self):
        """标记事件已提交"""
        self.uncommitted_events.clear()

    @abstractmethod
    def get_snapshot(self) -> dict[str, Any]:
        """获取聚合快照"""
        pass

    @abstractmethod
    def restore_from_snapshot(self, snapshot: dict[str, Any]):
        """从快照恢复"""
        pass


class EventBus:
    """事件总线"""

    def __init__(self):
        self.handlers: dict[str, list[Callable]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        async with self._lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)
            logger.info(f"订阅事件: {event_type}")

    async def unsubscribe(self, event_type: str, handler: Callable):
        """取消订阅"""
        async with self._lock:
            if event_type in self.handlers:
                self.handlers[event_type].remove(handler)

    async def publish(self, event: Event):
        """发布事件"""
        handlers = self.handlers.get(event.event_type, [])

        # 并行处理所有处理器
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                task = handler(event)
            else:
                task = asyncio.get_event_loop().run_in_executor(None, handler, event)
            tasks.append(task)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 记录错误
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        f"事件处理器错误: {handlers[i].__name__}, 错误: {result}"
                    )

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "subscribed_events": list(self.handlers.keys()),
            "handler_counts": {
                event_type: len(handlers)
                for event_type, handlers in self.handlers.items()
            },
        }


class EventSourcingRepository:
    """事件溯源仓库"""

    def __init__(
        self,
        event_store: EventStore,
        event_bus: EventBus | None = None,
        snapshot_frequency: int = 10,
    ):
        self.event_store = event_store
        self.event_bus = event_bus
        self.snapshot_frequency = snapshot_frequency

    async def save(self, aggregate: AggregateRoot):
        """保存聚合"""
        # 保存未提交的事件
        for event in aggregate.uncommitted_events:
            await self.event_store.append_event(event)

            # 发布事件
            if self.event_bus:
                await self.event_bus.publish(event)

        # 检查是否需要创建快照
        if aggregate.version % self.snapshot_frequency == 0:
            await self.event_store.save_snapshot(
                aggregate.aggregate_id, aggregate.get_snapshot(), aggregate.version
            )

        # 标记事件已提交
        aggregate.mark_events_as_committed()

    async def load(
        self, aggregate_type: type[AggregateRoot], aggregate_id: str
    ) -> AggregateRoot | None:
        """加载聚合"""
        # 尝试从快照加载
        snapshot = await self.event_store.get_snapshot(aggregate_id)

        if snapshot:
            # 从快照恢复
            aggregate = aggregate_type(aggregate_id)
            aggregate.restore_from_snapshot(snapshot["data"])
            aggregate.version = snapshot["version"]

            # 应用快照之后的事件
            events = await self.event_store.get_events(
                aggregate_id, from_version=snapshot["version"]
            )
        else:
            # 从头开始重建
            aggregate = aggregate_type(aggregate_id)
            events = await self.event_store.get_events(aggregate_id)

        # 应用事件
        for event in events:
            aggregate.apply_event(event)

        return aggregate if aggregate.version > 0 else None


class EventProjection(ABC):
    """事件投影基类"""

    @abstractmethod
    async def handle_event(self, event: Event):
        """处理事件"""
        pass

    @abstractmethod
    async def rebuild(self, events: list[Event]):
        """重建投影"""
        pass


class ReadModelProjection(EventProjection):
    """读模型投影"""

    def __init__(self):
        self.read_models: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def handle_event(self, event: Event):
        """处理事件更新读模型"""
        async with self._lock:
            # 根据事件类型更新读模型
            handler_name = f"_project_{event.event_type}"
            handler = getattr(self, handler_name, None)

            if handler:
                await handler(event)

    async def rebuild(self, events: list[Event]):
        """重建投影"""
        async with self._lock:
            self.read_models.clear()

            for event in events:
                await self.handle_event(event)

    async def get_read_model(self, model_id: str) -> dict[str, Any] | None:
        """获取读模型"""
        return self.read_models.get(model_id)

    async def query(self, criteria: dict[str, Any]) -> list[dict[str, Any]]:
        """查询读模型"""
        results = []

        for _model_id, model in self.read_models.items():
            match = all(model.get(key) == value for key, value in criteria.items())

            if match:
                results.append(model)

        return results


# 全局组件
_event_store = InMemoryEventStore()
_event_bus = EventBus()


def get_event_store() -> EventStore:
    """获取事件存储"""
    return _event_store


def get_event_bus() -> EventBus:
    """获取事件总线"""
    return _event_bus
