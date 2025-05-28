"""
WebSocket 路由
WebSocket Routes

提供实时通信功能，包括审核状态更新、通知等
"""

import json
from typing import Dict, List

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = structlog.get_logger(__name__)

router = APIRouter()

# 连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 活跃连接列表
        self.active_connections: List[WebSocket] = []
        # 用户连接映射
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # 审核员连接映射
        self.reviewer_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None, reviewer_id: str = None):
        """
        接受WebSocket连接
        
        Args:
            websocket: WebSocket连接
            user_id: 用户ID（可选）
            reviewer_id: 审核员ID（可选）
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # 记录用户连接
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        # 记录审核员连接
        if reviewer_id:
            if reviewer_id not in self.reviewer_connections:
                self.reviewer_connections[reviewer_id] = []
            self.reviewer_connections[reviewer_id].append(websocket)
        
        logger.info(
            "WebSocket connected",
            user_id=user_id,
            reviewer_id=reviewer_id,
            total_connections=len(self.active_connections)
        )
    
    def disconnect(self, websocket: WebSocket, user_id: str = None, reviewer_id: str = None):
        """
        断开WebSocket连接
        
        Args:
            websocket: WebSocket连接
            user_id: 用户ID（可选）
            reviewer_id: 审核员ID（可选）
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # 移除用户连接
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # 移除审核员连接
        if reviewer_id and reviewer_id in self.reviewer_connections:
            if websocket in self.reviewer_connections[reviewer_id]:
                self.reviewer_connections[reviewer_id].remove(websocket)
            if not self.reviewer_connections[reviewer_id]:
                del self.reviewer_connections[reviewer_id]
        
        logger.info(
            "WebSocket disconnected",
            user_id=user_id,
            reviewer_id=reviewer_id,
            total_connections=len(self.active_connections)
        )
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        发送个人消息
        
        Args:
            message: 消息内容
            websocket: WebSocket连接
        """
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error("Failed to send personal message", error=str(e))
    
    async def send_to_user(self, message: str, user_id: str):
        """
        发送消息给指定用户
        
        Args:
            message: 消息内容
            user_id: 用户ID
        """
        if user_id in self.user_connections:
            for websocket in self.user_connections[user_id]:
                await self.send_personal_message(message, websocket)
    
    async def send_to_reviewer(self, message: str, reviewer_id: str):
        """
        发送消息给指定审核员
        
        Args:
            message: 消息内容
            reviewer_id: 审核员ID
        """
        if reviewer_id in self.reviewer_connections:
            for websocket in self.reviewer_connections[reviewer_id]:
                await self.send_personal_message(message, websocket)
    
    async def broadcast(self, message: str):
        """
        广播消息给所有连接
        
        Args:
            message: 消息内容
        """
        for websocket in self.active_connections:
            await self.send_personal_message(message, websocket)
    
    async def broadcast_to_reviewers(self, message: str):
        """
        广播消息给所有审核员
        
        Args:
            message: 消息内容
        """
        for reviewer_connections in self.reviewer_connections.values():
            for websocket in reviewer_connections:
                await self.send_personal_message(message, websocket)


# 全局连接管理器实例
manager = ConnectionManager()


@router.websocket("/reviews")
async def websocket_reviews_endpoint(websocket: WebSocket):
    """
    审核任务WebSocket端点
    
    Args:
        websocket: WebSocket连接
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # 处理不同类型的消息
                if message_type == "ping":
                    # 心跳检测
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                        websocket
                    )
                
                elif message_type == "subscribe":
                    # 订阅特定事件
                    event_type = message.get("event_type")
                    logger.info("Client subscribed to event", event_type=event_type)
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "subscription_confirmed",
                            "event_type": event_type
                        }),
                        websocket
                    )
                
                else:
                    logger.warning("Unknown message type", message_type=message_type)
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON message received", data=data)
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        manager.disconnect(websocket)


@router.websocket("/reviewers/{reviewer_id}")
async def websocket_reviewer_endpoint(websocket: WebSocket, reviewer_id: str):
    """
    审核员专用WebSocket端点
    
    Args:
        websocket: WebSocket连接
        reviewer_id: 审核员ID
    """
    await manager.connect(websocket, reviewer_id=reviewer_id)
    
    try:
        while True:
            # 接收审核员消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # 处理审核员特定消息
                if message_type == "status_update":
                    # 审核员状态更新
                    status = message.get("status")
                    logger.info("Reviewer status updated", reviewer_id=reviewer_id, status=status)
                    
                    # 广播状态更新给管理员
                    await manager.broadcast_to_reviewers(
                        json.dumps({
                            "type": "reviewer_status_changed",
                            "reviewer_id": reviewer_id,
                            "status": status
                        })
                    )
                
                elif message_type == "task_progress":
                    # 任务进度更新
                    task_id = message.get("task_id")
                    progress = message.get("progress")
                    
                    logger.info(
                        "Task progress updated",
                        reviewer_id=reviewer_id,
                        task_id=task_id,
                        progress=progress
                    )
                
                elif message_type == "ping":
                    # 心跳检测
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                        websocket
                    )
                
                else:
                    logger.warning("Unknown reviewer message type", message_type=message_type)
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON message from reviewer", reviewer_id=reviewer_id, data=data)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, reviewer_id=reviewer_id)
    except Exception as e:
        logger.error("Reviewer WebSocket error", reviewer_id=reviewer_id, error=str(e))
        manager.disconnect(websocket, reviewer_id=reviewer_id)


@router.websocket("/users/{user_id}")
async def websocket_user_endpoint(websocket: WebSocket, user_id: str):
    """
    用户专用WebSocket端点
    
    Args:
        websocket: WebSocket连接
        user_id: 用户ID
    """
    await manager.connect(websocket, user_id=user_id)
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                # 处理用户特定消息
                if message_type == "ping":
                    # 心跳检测
                    await manager.send_personal_message(
                        json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                        websocket
                    )
                
                elif message_type == "subscribe_task":
                    # 订阅任务状态更新
                    task_id = message.get("task_id")
                    logger.info("User subscribed to task", user_id=user_id, task_id=task_id)
                    
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "task_subscription_confirmed",
                            "task_id": task_id
                        }),
                        websocket
                    )
                
                else:
                    logger.warning("Unknown user message type", message_type=message_type)
                    
            except json.JSONDecodeError:
                logger.error("Invalid JSON message from user", user_id=user_id, data=data)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id=user_id)
    except Exception as e:
        logger.error("User WebSocket error", user_id=user_id, error=str(e))
        manager.disconnect(websocket, user_id=user_id)


# 消息发送函数（供其他模块调用）

async def notify_task_status_change(task_id: str, status: str, user_id: str = None):
    """
    通知任务状态变更
    
    Args:
        task_id: 任务ID
        status: 新状态
        user_id: 用户ID（可选）
    """
    message = json.dumps({
        "type": "task_status_changed",
        "task_id": task_id,
        "status": status
    })
    
    if user_id:
        await manager.send_to_user(message, user_id)
    else:
        await manager.broadcast(message)


async def notify_task_assigned(task_id: str, reviewer_id: str):
    """
    通知任务分配
    
    Args:
        task_id: 任务ID
        reviewer_id: 审核员ID
    """
    message = json.dumps({
        "type": "task_assigned",
        "task_id": task_id,
        "reviewer_id": reviewer_id
    })
    
    await manager.send_to_reviewer(message, reviewer_id)


async def notify_task_completed(task_id: str, decision: str, user_id: str):
    """
    通知任务完成
    
    Args:
        task_id: 任务ID
        decision: 审核决策
        user_id: 用户ID
    """
    message = json.dumps({
        "type": "task_completed",
        "task_id": task_id,
        "decision": decision
    })
    
    await manager.send_to_user(message, user_id)


async def broadcast_system_alert(alert_type: str, message: str, severity: str = "info"):
    """
    广播系统告警
    
    Args:
        alert_type: 告警类型
        message: 告警消息
        severity: 严重程度
    """
    alert_message = json.dumps({
        "type": "system_alert",
        "alert_type": alert_type,
        "message": message,
        "severity": severity
    })
    
    await manager.broadcast(alert_message) 