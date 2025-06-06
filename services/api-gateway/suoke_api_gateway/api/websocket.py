"""
websocket - 索克生活项目模块
"""

from ..core.logging import get_logger
from ..services.websocket_manager import (
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from typing import Dict, Any, Optional
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WebSocket API 端点

提供 WebSocket 连接、管理和监控功能。
"""



    get_websocket_manager,
    WebSocketManager,
    WebSocketMessage,
    MessageType,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None, description="用户ID"),
    room: Optional[str] = Query(None, description="初始房间"),
    connection_id: Optional[str] = Query(None, description="连接ID"),
):
    """
    WebSocket 连接端点
    
    支持的查询参数：
    - user_id: 用户ID，用于用户级别的消息推送
    - room: 初始加入的房间
    - connection_id: 自定义连接ID，如果不提供则自动生成
    """
    ws_manager = get_websocket_manager()
    
    # 生成连接ID
    if not connection_id:
        connection_id = str(uuid.uuid4())
    
    try:
        # 建立连接
        connection = await ws_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user_id=user_id,
            metadata={
                "initial_room": room,
                "user_agent": websocket.headers.get("user-agent", ""),
                "origin": websocket.headers.get("origin", ""),
            }
        )
        
        # 如果指定了初始房间，自动加入
        if room:
            await ws_manager.join_room(connection_id, room)
        
        # 消息处理循环
        while True:
            try:
                # 接收消息
                raw_message = await websocket.receive_text()
                
                # 处理消息
                await ws_manager.handle_message(connection_id, raw_message)
                
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected", connection_id=connection_id)
                break
            except Exception as e:
                logger.error(
                    "Error handling WebSocket message",
                    connection_id=connection_id,
                    error=str(e)
                )
                # 发送错误消息
                try:
                    await ws_manager.send_to_connection(
                        connection_id,
                        WebSocketMessage(
                            type=MessageType.MESSAGE,
                            data={
                                "error": "Message processing failed",
                                "details": str(e),
                            }
                        )
                    )
                except:
                    break
    
    except Exception as e:
        logger.error(
            "WebSocket connection failed",
            connection_id=connection_id,
            error=str(e)
        )
    
    finally:
        # 清理连接
        await ws_manager.disconnect(connection_id)

@router.post("/send/{connection_id}")
async def send_to_connection(
    connection_id: str,
    message_data: Dict[str, Any],
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    发送消息到指定连接
    
    Args:
        connection_id: 连接ID
        message_data: 消息数据，包含 type 和 data 字段
    
    Returns:
        发送结果
    """
    try:
        message = WebSocketMessage(
            type=MessageType(message_data.get("type", "message")),
            data=message_data.get("data", {}),
        )
        
        success = await ws_manager.send_to_connection(connection_id, message)
        
        return {
            "success": success,
            "connection_id": connection_id,
            "message": "Message sent successfully" if success else "Failed to send message",
        }
    
    except Exception as e:
        logger.error("Failed to send message to connection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send/user/{user_id}")
async def send_to_user(
    user_id: str,
    message_data: Dict[str, Any],
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    发送消息到用户的所有连接
    
    Args:
        user_id: 用户ID
        message_data: 消息数据
    
    Returns:
        发送结果
    """
    try:
        message = WebSocketMessage(
            type=MessageType(message_data.get("type", "message")),
            data=message_data.get("data", {}),
        )
        
        sent_count = await ws_manager.send_to_user(user_id, message)
        
        return {
            "success": sent_count > 0,
            "user_id": user_id,
            "sent_count": sent_count,
            "message": f"Message sent to {sent_count} connections",
        }
    
    except Exception as e:
        logger.error("Failed to send message to user", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast/room/{room}")
async def broadcast_to_room(
    room: str,
    message_data: Dict[str, Any],
    exclude_connection_id: Optional[str] = None,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    广播消息到房间
    
    Args:
        room: 房间名称
        message_data: 消息数据
        exclude_connection_id: 排除的连接ID
    
    Returns:
        广播结果
    """
    try:
        message = WebSocketMessage(
            type=MessageType(message_data.get("type", "broadcast")),
            data=message_data.get("data", {}),
            room=room,
        )
        
        sent_count = await ws_manager.broadcast_to_room(
            room, message, exclude_connection_id
        )
        
        return {
            "success": sent_count > 0,
            "room": room,
            "sent_count": sent_count,
            "message": f"Message broadcast to {sent_count} connections in room",
        }
    
    except Exception as e:
        logger.error("Failed to broadcast to room", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast/all")
async def broadcast_to_all(
    message_data: Dict[str, Any],
    exclude_connection_id: Optional[str] = None,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    广播消息到所有连接
    
    Args:
        message_data: 消息数据
        exclude_connection_id: 排除的连接ID
    
    Returns:
        广播结果
    """
    try:
        message = WebSocketMessage(
            type=MessageType(message_data.get("type", "broadcast")),
            data=message_data.get("data", {}),
        )
        
        sent_count = await ws_manager.broadcast_to_all(message, exclude_connection_id)
        
        return {
            "success": sent_count > 0,
            "sent_count": sent_count,
            "message": f"Message broadcast to {sent_count} connections",
        }
    
    except Exception as e:
        logger.error("Failed to broadcast to all", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/room/{room}/join/{connection_id}")
async def join_room(
    room: str,
    connection_id: str,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    让连接加入房间
    
    Args:
        room: 房间名称
        connection_id: 连接ID
    
    Returns:
        操作结果
    """
    try:
        success = await ws_manager.join_room(connection_id, room)
        
        return {
            "success": success,
            "connection_id": connection_id,
            "room": room,
            "message": "Joined room successfully" if success else "Failed to join room",
        }
    
    except Exception as e:
        logger.error("Failed to join room", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/room/{room}/leave/{connection_id}")
async def leave_room(
    room: str,
    connection_id: str,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    让连接离开房间
    
    Args:
        room: 房间名称
        connection_id: 连接ID
    
    Returns:
        操作结果
    """
    try:
        success = await ws_manager.leave_room(connection_id, room)
        
        return {
            "success": success,
            "connection_id": connection_id,
            "room": room,
            "message": "Left room successfully" if success else "Failed to leave room",
        }
    
    except Exception as e:
        logger.error("Failed to leave room", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_websocket_stats(
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    获取 WebSocket 统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = ws_manager.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
        }
    
    except Exception as e:
        logger.error("Failed to get WebSocket stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connections")
async def list_connections(
    user_id: Optional[str] = Query(None, description="按用户ID过滤"),
    room: Optional[str] = Query(None, description="按房间过滤"),
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    列出连接信息
    
    Args:
        user_id: 按用户ID过滤
        room: 按房间过滤
    
    Returns:
        连接列表
    """
    try:
        connections = []
        
        for connection_id in ws_manager.connections:
            connection_info = ws_manager.get_connection_info(connection_id)
            if not connection_info:
                continue
            
            # 按用户ID过滤
            if user_id and connection_info.get("user_id") != user_id:
                continue
            
            # 按房间过滤
            if room and room not in connection_info.get("rooms", []):
                continue
            
            connections.append(connection_info)
        
        return {
            "status": "success",
            "connections": connections,
            "total": len(connections),
        }
    
    except Exception as e:
        logger.error("Failed to list connections", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connection/{connection_id}")
async def get_connection_info(
    connection_id: str,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    获取连接详细信息
    
    Args:
        connection_id: 连接ID
    
    Returns:
        连接信息
    """
    try:
        connection_info = ws_manager.get_connection_info(connection_id)
        
        if not connection_info:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return {
            "status": "success",
            "connection": connection_info,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get connection info", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connection/{connection_id}")
async def disconnect_connection(
    connection_id: str,
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    强制断开连接
    
    Args:
        connection_id: 连接ID
    
    Returns:
        操作结果
    """
    try:
        connection_info = ws_manager.get_connection_info(connection_id)
        if not connection_info:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        await ws_manager.disconnect(connection_id)
        
        return {
            "status": "success",
            "connection_id": connection_id,
            "message": "Connection disconnected successfully",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to disconnect connection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rooms")
async def list_rooms(
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    列出所有房间
    
    Returns:
        房间列表
    """
    try:
        stats = ws_manager.get_stats()
        rooms = stats.get("rooms", {})
        
        room_list = [
            {
                "name": room,
                "connection_count": count,
                "connections": list(ws_manager.room_connections.get(room, set())),
            }
            for room, count in rooms.items()
        ]
        
        return {
            "status": "success",
            "rooms": room_list,
            "total": len(room_list),
        }
    
    except Exception as e:
        logger.error("Failed to list rooms", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def websocket_health_check(
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
) -> Dict[str, Any]:
    """
    WebSocket 健康检查
    
    Returns:
        健康状态
    """
    try:
        stats = ws_manager.get_stats()
        
        return {
            "status": "healthy",
            "active_connections": stats["active_connections"],
            "total_connections": stats["total_connections"],
            "total_messages": stats["total_messages"],
            "total_rooms": stats["total_rooms"],
            "message": "WebSocket service is running normally",
        }
    
    except Exception as e:
        logger.error("WebSocket health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "WebSocket service is experiencing issues",
        } 