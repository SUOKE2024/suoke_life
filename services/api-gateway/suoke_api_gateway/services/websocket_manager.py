#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebSocket 连接管理器

管理 WebSocket 连接、消息路由、房间管理等功能。
"""

import asyncio
import json
import time
from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from ..core.logging import get_logger

logger = get_logger(__name__)

class MessageType(Enum):
    """消息类型"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    BROADCAST = "broadcast"
    ROOM_JOIN = "room_join"
    ROOM_LEAVE = "room_leave"
    PING = "ping"
    PONG = "pong"

@dataclass
class WebSocketConnection:
    """WebSocket 连接信息"""
    websocket: WebSocket
    connection_id: str
    user_id: Optional[str] = None
    rooms: Set[str] = None
    metadata: Dict[str, Any] = None
    connected_at: float = None
    last_ping: float = None
    
    def __post_init__(self):
        if self.rooms is None:
            self.rooms = set()
        if self.metadata is None:
            self.metadata = {}
        if self.connected_at is None:
            self.connected_at = time.time()
        if self.last_ping is None:
            self.last_ping = time.time()

@dataclass
class WebSocketMessage:
    """WebSocket 消息"""
    type: MessageType
    data: Any
    from_connection_id: Optional[str] = None
    to_connection_id: Optional[str] = None
    room: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value,
            "data": self.data,
            "from_connection_id": self.from_connection_id,
            "to_connection_id": self.to_connection_id,
            "room": self.room,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketMessage':
        """从字典创建消息"""
        return cls(
            type=MessageType(data["type"]),
            data=data["data"],
            from_connection_id=data.get("from_connection_id"),
            to_connection_id=data.get("to_connection_id"),
            room=data.get("room"),
            timestamp=data.get("timestamp", time.time()),
        )

class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 连接管理
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)
        self.room_connections: Dict[str, Set[str]] = defaultdict(set)
        
        # 消息处理器
        self.message_handlers: Dict[MessageType, List[Callable]] = defaultdict(list)
        
        # 统计信息
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "total_messages": 0,
            "total_rooms": 0,
        }
        
        # 心跳检查
        self.ping_interval = 30  # 30秒
        self.ping_timeout = 10   # 10秒超时
        self._ping_task: Optional[asyncio.Task] = None
        
        # 注册默认消息处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """注册默认消息处理器"""
        self.add_message_handler(MessageType.PING, self._handle_ping)
        self.add_message_handler(MessageType.ROOM_JOIN, self._handle_room_join)
        self.add_message_handler(MessageType.ROOM_LEAVE, self._handle_room_leave)
    
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WebSocketConnection:
        """建立 WebSocket 连接"""
        try:
            await websocket.accept()
            
            connection = WebSocketConnection(
                websocket=websocket,
                connection_id=connection_id,
                user_id=user_id,
                metadata=metadata or {},
            )
            
            # 存储连接
            self.connections[connection_id] = connection
            
            # 用户连接映射
            if user_id:
                self.user_connections[user_id].add(connection_id)
            
            # 更新统计
            self.stats["total_connections"] += 1
            self.stats["active_connections"] = len(self.connections)
            
            # 启动心跳检查
            if not self._ping_task or self._ping_task.done():
                self._ping_task = asyncio.create_task(self._ping_loop())
            
            logger.info(
                "WebSocket connection established",
                connection_id=connection_id,
                user_id=user_id,
                metadata=metadata,
            )
            
            # 发送连接确认消息
            await self.send_to_connection(
                connection_id,
                WebSocketMessage(
                    type=MessageType.CONNECT,
                    data={"connection_id": connection_id, "status": "connected"},
                )
            )
            
            return connection
            
        except Exception as e:
            logger.error(
                "Failed to establish WebSocket connection",
                connection_id=connection_id,
                error=str(e)
            )
            raise
    
    async def disconnect(self, connection_id: str) -> None:
        """断开 WebSocket 连接"""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        try:
            # 从所有房间中移除
            for room in list(connection.rooms):
                await self.leave_room(connection_id, room)
            
            # 从用户连接映射中移除
            if connection.user_id:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
            
            # 关闭 WebSocket 连接
            if connection.websocket.client_state == WebSocketState.CONNECTED:
                await connection.websocket.close()
            
            # 移除连接
            del self.connections[connection_id]
            
            # 更新统计
            self.stats["active_connections"] = len(self.connections)
            
            logger.info(
                "WebSocket connection disconnected",
                connection_id=connection_id,
                user_id=connection.user_id,
            )
            
        except Exception as e:
            logger.error(
                "Error during WebSocket disconnection",
                connection_id=connection_id,
                error=str(e)
            )
    
    async def send_to_connection(
        self,
        connection_id: str,
        message: WebSocketMessage,
    ) -> bool:
        """发送消息到指定连接"""
        connection = self.connections.get(connection_id)
        if not connection:
            logger.warning("Connection not found", connection_id=connection_id)
            return False
        
        try:
            if connection.websocket.client_state == WebSocketState.CONNECTED:
                await connection.websocket.send_text(json.dumps(message.to_dict()))
                self.stats["total_messages"] += 1
                return True
            else:
                # 连接已断开，清理连接
                await self.disconnect(connection_id)
                return False
                
        except Exception as e:
            logger.error(
                "Failed to send message to connection",
                connection_id=connection_id,
                error=str(e)
            )
            await self.disconnect(connection_id)
            return False
    
    async def send_to_user(
        self,
        user_id: str,
        message: WebSocketMessage,
    ) -> int:
        """发送消息到用户的所有连接"""
        connection_ids = self.user_connections.get(user_id, set())
        sent_count = 0
        
        for connection_id in list(connection_ids):
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_room(
        self,
        room: str,
        message: WebSocketMessage,
        exclude_connection_id: Optional[str] = None,
    ) -> int:
        """广播消息到房间"""
        connection_ids = self.room_connections.get(room, set())
        sent_count = 0
        
        for connection_id in list(connection_ids):
            if connection_id != exclude_connection_id:
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def broadcast_to_all(
        self,
        message: WebSocketMessage,
        exclude_connection_id: Optional[str] = None,
    ) -> int:
        """广播消息到所有连接"""
        sent_count = 0
        
        for connection_id in list(self.connections.keys()):
            if connection_id != exclude_connection_id:
                if await self.send_to_connection(connection_id, message):
                    sent_count += 1
        
        return sent_count
    
    async def join_room(self, connection_id: str, room: str) -> bool:
        """加入房间"""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        # 添加到房间
        connection.rooms.add(room)
        self.room_connections[room].add(connection_id)
        
        # 更新房间统计
        self.stats["total_rooms"] = len(self.room_connections)
        
        logger.info(
            "Connection joined room",
            connection_id=connection_id,
            room=room,
            user_id=connection.user_id,
        )
        
        # 通知房间其他成员
        await self.broadcast_to_room(
            room,
            WebSocketMessage(
                type=MessageType.ROOM_JOIN,
                data={
                    "connection_id": connection_id,
                    "user_id": connection.user_id,
                    "room": room,
                },
                from_connection_id=connection_id,
            ),
            exclude_connection_id=connection_id,
        )
        
        return True
    
    async def leave_room(self, connection_id: str, room: str) -> bool:
        """离开房间"""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        # 从房间移除
        connection.rooms.discard(room)
        self.room_connections[room].discard(connection_id)
        
        # 清理空房间
        if not self.room_connections[room]:
            del self.room_connections[room]
        
        # 更新房间统计
        self.stats["total_rooms"] = len(self.room_connections)
        
        logger.info(
            "Connection left room",
            connection_id=connection_id,
            room=room,
            user_id=connection.user_id,
        )
        
        # 通知房间其他成员
        await self.broadcast_to_room(
            room,
            WebSocketMessage(
                type=MessageType.ROOM_LEAVE,
                data={
                    "connection_id": connection_id,
                    "user_id": connection.user_id,
                    "room": room,
                },
                from_connection_id=connection_id,
            ),
        )
        
        return True
    
    def add_message_handler(
        self,
        message_type: MessageType,
        handler: Callable[[WebSocketMessage, WebSocketConnection], None],
    ) -> None:
        """添加消息处理器"""
        self.message_handlers[message_type].append(handler)
        logger.info("Message handler added", message_type=message_type.value)
    
    async def handle_message(
        self,
        connection_id: str,
        raw_message: str,
    ) -> None:
        """处理接收到的消息"""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        try:
            # 解析消息
            message_data = json.loads(raw_message)
            message = WebSocketMessage.from_dict(message_data)
            message.from_connection_id = connection_id
            
            # 更新连接活跃时间
            connection.last_ping = time.time()
            
            # 调用消息处理器
            handlers = self.message_handlers.get(message.type, [])
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message, connection)
                    else:
                        handler(message, connection)
                except Exception as e:
                    logger.error(
                        "Message handler failed",
                        handler=handler.__name__,
                        error=str(e)
                    )
            
            self.stats["total_messages"] += 1
            
        except Exception as e:
            logger.error(
                "Failed to handle message",
                connection_id=connection_id,
                raw_message=raw_message,
                error=str(e)
            )
    
    async def _handle_ping(self, message: WebSocketMessage, connection: WebSocketConnection) -> None:
        """处理 ping 消息"""
        await self.send_to_connection(
            connection.connection_id,
            WebSocketMessage(
                type=MessageType.PONG,
                data={"timestamp": time.time()},
            )
        )
    
    async def _handle_room_join(self, message: WebSocketMessage, connection: WebSocketConnection) -> None:
        """处理加入房间消息"""
        room = message.data.get("room")
        if room:
            await self.join_room(connection.connection_id, room)
    
    async def _handle_room_leave(self, message: WebSocketMessage, connection: WebSocketConnection) -> None:
        """处理离开房间消息"""
        room = message.data.get("room")
        if room:
            await self.leave_room(connection.connection_id, room)
    
    async def _ping_loop(self) -> None:
        """心跳检查循环"""
        while self.connections:
            try:
                current_time = time.time()
                disconnected_connections = []
                
                for connection_id, connection in self.connections.items():
                    # 检查连接是否超时
                    if current_time - connection.last_ping > self.ping_timeout + self.ping_interval:
                        disconnected_connections.append(connection_id)
                        continue
                    
                    # 发送 ping
                    if current_time - connection.last_ping > self.ping_interval:
                        try:
                            await self.send_to_connection(
                                connection_id,
                                WebSocketMessage(
                                    type=MessageType.PING,
                                    data={"timestamp": current_time},
                                )
                            )
                        except Exception as e:
                            logger.warning(
                                "Failed to send ping",
                                connection_id=connection_id,
                                error=str(e)
                            )
                            disconnected_connections.append(connection_id)
                
                # 清理超时连接
                for connection_id in disconnected_connections:
                    logger.info("Disconnecting inactive connection", connection_id=connection_id)
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(self.ping_interval)
                
            except Exception as e:
                logger.error("Error in ping loop", error=str(e))
                await asyncio.sleep(5)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.stats,
            "rooms": {
                room: len(connections)
                for room, connections in self.room_connections.items()
            },
            "users": {
                user_id: len(connections)
                for user_id, connections in self.user_connections.items()
            },
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """获取连接信息"""
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        return {
            "connection_id": connection.connection_id,
            "user_id": connection.user_id,
            "rooms": list(connection.rooms),
            "metadata": connection.metadata,
            "connected_at": connection.connected_at,
            "last_ping": connection.last_ping,
            "uptime": time.time() - connection.connected_at,
        }

# 全局 WebSocket 管理器实例
websocket_manager = WebSocketManager()

def get_websocket_manager() -> WebSocketManager:
    """获取全局 WebSocket 管理器"""
    return websocket_manager 