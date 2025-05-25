#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知服务

提供异步通知和事件发布功能，支持多种通知渠道。
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import httpx
from structlog import get_logger

logger = get_logger()


class NotificationLevel(Enum):
    """通知级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationChannel(Enum):
    """通知渠道"""
    WEBHOOK = "webhook"
    MESSAGE_QUEUE = "message_queue"
    EMAIL = "email"
    SMS = "sms"
    INTERNAL = "internal"


@dataclass
class NotificationEvent:
    """通知事件"""
    event_id: str
    event_type: str
    level: NotificationLevel
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: float
    source: str
    user_id: Optional[str] = None
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result["level"] = self.level.value
        result["tags"] = self.tags or []
        return result


class NotificationHandler(ABC):
    """通知处理器抽象基类"""
    
    @abstractmethod
    async def send(self, event: NotificationEvent) -> bool:
        """发送通知"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class InternalNotificationHandler(NotificationHandler):
    """内部通知处理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self.subscribers:
            try:
                self.subscribers[event_type].remove(callback)
            except ValueError:
                pass
    
    async def send(self, event: NotificationEvent) -> bool:
        """发送内部通知"""
        try:
            callbacks = self.subscribers.get(event.event_type, [])
            callbacks.extend(self.subscribers.get("*", []))  # 通配符订阅
            
            for callback in callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error("内部通知回调执行失败", callback=str(callback), error=str(e))
            
            logger.debug("内部通知发送成功", event_id=event.event_id, callbacks_count=len(callbacks))
            return True
            
        except Exception as e:
            logger.error("内部通知发送失败", event_id=event.event_id, error=str(e))
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        return True


class NotificationService:
    """通知服务"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.handlers: Dict[NotificationChannel, NotificationHandler] = {}
        self.enabled_channels = set()
        self.event_queue = asyncio.Queue()
        self.worker_tasks = []
        self.running = False
        
    async def initialize(self):
        """初始化通知服务"""
        try:
            # 初始化各种通知处理器
            await self._init_handlers()
            
            # 启动工作线程
            await self._start_workers()
            
            self.running = True
            logger.info("通知服务初始化成功", enabled_channels=list(self.enabled_channels))
            
        except Exception as e:
            logger.error("通知服务初始化失败", error=str(e))
            raise
    
    async def _init_handlers(self):
        """初始化通知处理器"""
        # 内部通知处理器
        internal_config = self.config.get("internal", {})
        if internal_config.get("enabled", True):  # 默认启用
            handler = InternalNotificationHandler(internal_config)
            self.handlers[NotificationChannel.INTERNAL] = handler
            self.enabled_channels.add(NotificationChannel.INTERNAL)
    
    async def _start_workers(self):
        """启动工作线程"""
        worker_count = self.config.get("worker_count", 2)
        
        for i in range(worker_count):
            task = asyncio.create_task(self._worker())
            self.worker_tasks.append(task)
        
        logger.info("通知工作线程已启动", worker_count=worker_count)
    
    async def _worker(self):
        """工作线程"""
        while self.running:
            try:
                # 从队列获取事件
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                # 发送到所有启用的渠道
                await self._send_to_channels(event)
                
                # 标记任务完成
                self.event_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("通知工作线程异常", error=str(e))
                await asyncio.sleep(1)
    
    async def _send_to_channels(self, event: NotificationEvent):
        """发送到所有渠道"""
        tasks = []
        
        for channel in self.enabled_channels:
            if channel in self.handlers:
                handler = self.handlers[channel]
                task = asyncio.create_task(self._send_with_retry(handler, event))
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for result in results if result is True)
            logger.debug(
                "通知发送完成",
                event_id=event.event_id,
                total_channels=len(tasks),
                success_count=success_count
            )
    
    async def _send_with_retry(self, handler: NotificationHandler, event: NotificationEvent) -> bool:
        """带重试的发送"""
        try:
            return await handler.send(event)
        except Exception as e:
            logger.error("通知发送异常", handler=type(handler).__name__, error=str(e))
            return False
    
    async def notify(
        self,
        event_type: str,
        level: NotificationLevel,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        immediate: bool = False
    ) -> str:
        """发送通知"""
        import uuid
        
        event = NotificationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            level=level,
            title=title,
            message=message,
            data=data or {},
            timestamp=time.time(),
            source="look-service",
            user_id=user_id,
            tags=tags
        )
        
        if immediate:
            # 立即发送
            await self._send_to_channels(event)
        else:
            # 加入队列异步发送
            await self.event_queue.put(event)
        
        logger.debug("通知已提交", event_id=event.event_id, event_type=event_type, immediate=immediate)
        return event.event_id
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅内部事件"""
        internal_handler = self.handlers.get(NotificationChannel.INTERNAL)
        if isinstance(internal_handler, InternalNotificationHandler):
            internal_handler.subscribe(event_type, callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅内部事件"""
        internal_handler = self.handlers.get(NotificationChannel.INTERNAL)
        if isinstance(internal_handler, InternalNotificationHandler):
            internal_handler.unsubscribe(event_type, callback)
    
    async def health_check(self) -> Dict[str, bool]:
        """健康检查"""
        results = {}
        
        for channel, handler in self.handlers.items():
            try:
                results[channel.value] = await handler.health_check()
            except Exception as e:
                logger.error("通知渠道健康检查失败", channel=channel.value, error=str(e))
                results[channel.value] = False
        
        return results
    
    async def get_queue_size(self) -> int:
        """获取队列大小"""
        return self.event_queue.qsize()
    
    async def shutdown(self):
        """关闭通知服务"""
        logger.info("开始关闭通知服务")
        
        self.running = False
        
        # 等待队列处理完成
        await self.event_queue.join()
        
        # 取消工作任务
        for task in self.worker_tasks:
            task.cancel()
        
        # 等待任务完成
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        
        logger.info("通知服务已关闭") 