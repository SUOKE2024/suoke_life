"""
索克生活统一事件总线
提供高性能、可靠的事件发布订阅机制
"""

import asyncio
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

import aioredis
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Event:
    """事件数据结构"""
    id: str
    type: str
    data: Dict[str, Any]
    timestamp: str
    source: str
    correlation_id: Optional[str] = None
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """从字典创建事件"""
        return cls(**data)


class SuokeEventBus:
    """索克生活事件总线"""
    
    def __init__(self, redis_url: Optional[str] = None, service_name: Optional[str] = None):
        """初始化事件总线"""
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.service_name = service_name or os.getenv('SERVICE_NAME', 'unknown-service')
        
        self.redis_client: Optional[aioredis.Redis] = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.subscriptions: Set[str] = set()
        self.running = False
        
        # 事件统计
        self.published_events = 0
        self.processed_events = 0
        self.failed_events = 0
        
    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding='utf-8',
                decode_responses=True,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("事件总线Redis连接成功", service=self.service_name)
            
        except Exception as e:
            logger.error("事件总线Redis连接失败", error=str(e), service=self.service_name)
            raise
    
    async def start(self) -> None:
        """启动事件总线"""
        if not self.redis_client:
            await self.initialize()
        
        self.running = True
        logger.info("事件总线启动成功", service=self.service_name)
        
        # 启动订阅监听
        if self.subscriptions:
            asyncio.create_task(self._start_subscriptions())
    
    async def stop(self) -> None:
        """停止事件总线"""
        self.running = False
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("事件总线已停止", 
                   service=self.service_name,
                   published=self.published_events,
                   processed=self.processed_events,
                   failed=self.failed_events)
    
    async def publish(self, event_type: str, data: Dict[str, Any], 
                     correlation_id: Optional[str] = None) -> str:
        """发布事件"""
        try:
            event = Event(
                id=str(uuid4()),
                type=event_type,
                data=data,
                timestamp=datetime.utcnow().isoformat(),
                source=self.service_name,
                correlation_id=correlation_id
            )
            
            # 发布到Redis
            await self.redis_client.publish(event_type, json.dumps(event.to_dict()))
            
            # 同时发布到通用频道（用于监控）
            await self.redis_client.publish('suoke.events.all', json.dumps(event.to_dict()))
            
            self.published_events+=1
            
            logger.info("事件发布成功", 
                       event_id=event.id,
                       event_type=event_type,
                       source=self.service_name)
            
            return event.id
            
        except Exception as e:
            self.failed_events+=1
            logger.error("事件发布失败", 
                        event_type=event_type,
                        error=str(e),
                        source=self.service_name)
            raise
    
    async def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        """订阅事件"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.subscriptions.add(event_type)
        
        logger.info("事件订阅成功", 
                   event_type=event_type,
                   service=self.service_name)
        
        # 如果事件总线已启动，立即开始监听
        if self.running:
            asyncio.create_task(self._subscribe_to_channel(event_type))
    
    async def subscribe_pattern(self, pattern: str, handler: Callable[[Event], None]) -> None:
        """订阅事件模式"""
        # Redis模式订阅
        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe(pattern)
        
        asyncio.create_task(self._handle_pattern_subscription(pubsub, handler))
        
        logger.info("事件模式订阅成功", 
                   pattern=pattern,
                   service=self.service_name)
    
    async def _start_subscriptions(self) -> None:
        """启动所有订阅"""
        tasks = []
        for event_type in self.subscriptions:
            task = asyncio.create_task(self._subscribe_to_channel(event_type))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _subscribe_to_channel(self, event_type: str) -> None:
        """订阅单个频道"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(event_type)
            
            logger.info("开始监听事件频道", 
                       event_type=event_type,
                       service=self.service_name)
            
            async for message in pubsub.listen():
                if not self.running:
                    break
                
                if message['type']=='message':
                    await self._handle_message(event_type, message['data'])
                    
        except Exception as e:
            logger.error("事件频道监听失败", 
                        event_type=event_type,
                        error=str(e),
                        service=self.service_name)
    
    async def _handle_pattern_subscription(self, pubsub, handler: Callable) -> None:
        """处理模式订阅"""
        try:
            async for message in pubsub.listen():
                if not self.running:
                    break
                
                if message['type']=='pmessage':
                    event_data = json.loads(message['data'])
                    event = Event.from_dict(event_data)
                    await self._safe_call_handler(handler, event)
                    
        except Exception as e:
            logger.error("模式订阅处理失败", error=str(e), service=self.service_name)
    
    async def _handle_message(self, event_type: str, message_data: str) -> None:
        """处理接收到的消息"""
        try:
            event_data = json.loads(message_data)
            event = Event.from_dict(event_data)
            
            # 调用所有注册的处理器
            handlers = self.event_handlers.get(event_type, [])
            for handler in handlers:
                await self._safe_call_handler(handler, event)
            
            self.processed_events+=1
            
        except Exception as e:
            self.failed_events+=1
            logger.error("消息处理失败", 
                        event_type=event_type,
                        error=str(e),
                        service=self.service_name)
    
    async def _safe_call_handler(self, handler: Callable, event: Event) -> None:
        """安全调用事件处理器"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
                
        except Exception as e:
            self.failed_events+=1
            logger.error("事件处理器执行失败", 
                        event_id=event.id,
                        event_type=event.type,
                        handler=handler.__name__,
                        error=str(e),
                        service=self.service_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取事件总线统计信息"""
        return {
            "service_name": self.service_name,
            "running": self.running,
            "published_events": self.published_events,
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "subscriptions": list(self.subscriptions),
            "handler_count": sum(len(handlers) for handlers in self.event_handlers.values())
        }


# 全局事件总线实例
_global_event_bus: Optional[SuokeEventBus] = None


def get_event_bus() -> SuokeEventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = SuokeEventBus()
    return _global_event_bus


async def initialize_event_bus(redis_url: Optional[str] = None, 
                              service_name: Optional[str] = None) -> SuokeEventBus:
    """初始化全局事件总线"""
    global _global_event_bus
    _global_event_bus = SuokeEventBus(redis_url, service_name)
    await _global_event_bus.initialize()
    await _global_event_bus.start()
    return _global_event_bus 