#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络优化API处理器
提供双向网络通信优化的HTTP接口
"""

import logging
import json
import time
import asyncio
from typing import Dict, Any, Optional, Callable
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ...integration.network_optimizer import get_network_optimizer, NetworkConfig
from ...integration.cache_manager import get_cache_manager
from ...agent.agent_manager import AgentManager

logger = logging.getLogger(__name__)

class NetworkOptimizationRequest(BaseModel):
    """网络优化请求模型"""
    user_id: str = Field(..., description="用户ID")
    optimization_type: str = Field(..., description="优化类型: compression, http2, websocket")
    settings: Optional[Dict[str, Any]] = Field(None, description="优化设置")

class ConnectionRequest(BaseModel):
    """连接请求模型"""
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    connection_type: str = Field("websocket", description="连接类型")
    preferences: Optional[Dict[str, Any]] = Field(None, description="连接偏好")

class MessageRequest(BaseModel):
    """消息请求模型"""
    user_id: str = Field(..., description="用户ID")
    message: Dict[str, Any] = Field(..., description="消息内容")
    compress: bool = Field(True, description="是否压缩")
    priority: str = Field("normal", description="消息优先级")

def create_network_router(get_agent_manager_func: Callable[[], AgentManager]) -> APIRouter:
    """创建网络优化路由器"""
    router = APIRouter(prefix="/api/v1/network", tags=["网络优化"])
    cache_manager = get_cache_manager()

    @router.get("/status")
    async def get_network_status():
        """获取网络状态"""
        try:
            network_optimizer = await get_network_optimizer()
            stats = await network_optimizer.get_network_stats()
            
            return JSONResponse(content={
                "success": True,
                "data": stats,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取网络状态失败: {str(e)}")

    @router.post("/optimize")
    async def optimize_network(request: NetworkOptimizationRequest):
        """优化网络连接"""
        try:
            network_optimizer = await get_network_optimizer()
            
            if request.optimization_type == "compression":
                # 启用数据压缩
                network_optimizer.config.compression_enabled = True
                if request.settings:
                    network_optimizer.config.compression_level = request.settings.get("level", 6)
                    network_optimizer.config.compression_threshold = request.settings.get("threshold", 1024)
                
                result = {
                    "optimization_type": "compression",
                    "enabled": True,
                    "level": network_optimizer.config.compression_level,
                    "threshold": network_optimizer.config.compression_threshold
                }
                
            elif request.optimization_type == "http2":
                # 启用HTTP/2
                network_optimizer.config.http2_enabled = True
                if request.settings:
                    network_optimizer.config.http2_max_connections = request.settings.get("max_connections", 100)
                
                result = {
                    "optimization_type": "http2",
                    "enabled": True,
                    "max_connections": network_optimizer.config.http2_max_connections
                }
                
            elif request.optimization_type == "websocket":
                # 优化WebSocket
                network_optimizer.config.websocket_enabled = True
                if request.settings:
                    network_optimizer.config.websocket_ping_interval = request.settings.get("ping_interval", 30)
                    network_optimizer.config.websocket_max_connections = request.settings.get("max_connections", 1000)
                
                result = {
                    "optimization_type": "websocket",
                    "enabled": True,
                    "ping_interval": network_optimizer.config.websocket_ping_interval,
                    "max_connections": network_optimizer.config.websocket_max_connections
                }
                
            else:
                raise HTTPException(status_code=400, detail=f"不支持的优化类型: {request.optimization_type}")
            
            return JSONResponse(content={
                "success": True,
                "data": result,
                "user_id": request.user_id,
                "timestamp": int(time.time())
            })
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"网络优化失败: {e}")
            raise HTTPException(status_code=500, detail=f"网络优化失败: {str(e)}")

    @router.get("/connections")
    async def get_connections(user_id: Optional[str] = Query(None)):
        """获取连接信息"""
        try:
            network_optimizer = await get_network_optimizer()
            
            if user_id:
                # 获取特定用户的连接
                user_connections = await network_optimizer.connection_pool.get_user_connections(user_id)
                connections_data = [
                    {
                        "connection_id": conn.connection_id,
                        "user_id": conn.user_id,
                        "session_id": conn.session_id,
                        "connection_type": conn.connection_type,
                        "created_at": conn.created_at,
                        "last_activity": conn.last_activity,
                        "bytes_sent": conn.bytes_sent,
                        "bytes_received": conn.bytes_received,
                        "messages_sent": conn.messages_sent,
                        "messages_received": conn.messages_received,
                        "is_active": conn.is_active
                    }
                    for conn in user_connections
                ]
            else:
                # 获取所有连接统计
                stats = await network_optimizer.connection_pool.get_stats()
                connections_data = stats
            
            return JSONResponse(content={
                "success": True,
                "data": connections_data,
                "user_id": user_id,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"获取连接信息失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取连接信息失败: {str(e)}")

    @router.post("/connections/optimize/{connection_id}")
    async def optimize_connection(connection_id: str):
        """优化特定连接"""
        try:
            network_optimizer = await get_network_optimizer()
            optimization_result = await network_optimizer.optimize_connection(connection_id)
            
            return JSONResponse(content={
                "success": True,
                "data": optimization_result,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"连接优化失败: {e}")
            raise HTTPException(status_code=500, detail=f"连接优化失败: {str(e)}")

    @router.post("/message/send")
    async def send_message(request: MessageRequest):
        """发送优化消息"""
        try:
            network_optimizer = await get_network_optimizer()
            
            # 发送消息
            success = await network_optimizer.send_to_user(
                user_id=request.user_id,
                message=request.message,
                compress=request.compress
            )
            
            return JSONResponse(content={
                "success": success,
                "data": {
                    "user_id": request.user_id,
                    "message_sent": success,
                    "compressed": request.compress,
                    "priority": request.priority
                },
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")

    @router.get("/compression/stats")
    async def get_compression_stats():
        """获取压缩统计"""
        try:
            network_optimizer = await get_network_optimizer()
            compression_stats = network_optimizer.data_compressor.compression_stats
            
            return JSONResponse(content={
                "success": True,
                "data": compression_stats,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"获取压缩统计失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取压缩统计失败: {str(e)}")

    @router.post("/http2/request")
    async def make_http2_request(
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[str] = None
    ):
        """发起HTTP/2请求"""
        try:
            network_optimizer = await get_network_optimizer()
            
            # 准备请求参数
            kwargs = {}
            if headers:
                kwargs["headers"] = headers
            if data:
                kwargs["content"] = data
            
            # 发起HTTP/2请求
            result = await network_optimizer.make_http2_request(url, method, **kwargs)
            
            # 转换响应内容为字符串（如果是字节）
            if isinstance(result.get("content"), bytes):
                try:
                    result["content"] = result["content"].decode("utf-8")
                except UnicodeDecodeError:
                    result["content"] = "<binary data>"
            
            return JSONResponse(content={
                "success": True,
                "data": result,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"HTTP/2请求失败: {e}")
            raise HTTPException(status_code=500, detail=f"HTTP/2请求失败: {str(e)}")

    @router.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        """WebSocket端点"""
        await websocket.accept()
        
        try:
            network_optimizer = await get_network_optimizer()
            
            # 添加WebSocket连接
            connection_id = await network_optimizer.connection_pool.add_websocket_connection(
                websocket, user_id
            )
            
            logger.info(f"WebSocket连接建立: {connection_id}, 用户: {user_id}")
            
            # 发送连接确认
            await websocket.send_json({
                "type": "connection_established",
                "connection_id": connection_id,
                "user_id": user_id,
                "timestamp": time.time()
            })
            
            # 处理消息
            while True:
                try:
                    # 接收消息
                    data = await websocket.receive_json()
                    
                    # 更新连接统计
                    conn_info = await network_optimizer.connection_pool.get_connection_info(connection_id)
                    if conn_info:
                        conn_info.messages_received += 1
                        conn_info.bytes_received += len(json.dumps(data))
                        conn_info.last_activity = time.time()
                    
                    # 处理不同类型的消息
                    message_type = data.get("type", "unknown")
                    
                    if message_type == "ping":
                        response = {
                            "type": "pong",
                            "timestamp": time.time(),
                            "connection_id": connection_id
                        }
                        
                    elif message_type == "device_request":
                        # 集成设备管理器
                        agent_mgr = get_agent_manager_func()
                        if agent_mgr:
                            device_action = data.get("action", "status")
                            if device_action == "capture_camera":
                                result = await agent_mgr.capture_camera_image(user_id)
                                response = {
                                    "type": "device_response",
                                    "request_id": data.get("request_id"),
                                    "action": device_action,
                                    "result": result,
                                    "timestamp": time.time()
                                }
                            else:
                                response = {
                                    "type": "device_response",
                                    "request_id": data.get("request_id"),
                                    "action": device_action,
                                    "status": "not_implemented",
                                    "timestamp": time.time()
                                }
                        else:
                            response = {
                                "type": "error",
                                "message": "智能体管理器不可用",
                                "timestamp": time.time()
                            }
                    
                    elif message_type == "chat_message":
                        # 集成聊天功能
                        agent_mgr = get_agent_manager_func()
                        if agent_mgr:
                            chat_result = await agent_mgr.chat(
                                user_id=user_id,
                                message=data.get("message", ""),
                                session_id=data.get("session_id")
                            )
                            response = {
                                "type": "chat_response",
                                "message_id": data.get("message_id"),
                                "result": chat_result,
                                "timestamp": time.time()
                            }
                        else:
                            response = {
                                "type": "error",
                                "message": "智能体管理器不可用",
                                "timestamp": time.time()
                            }
                    
                    else:
                        response = {
                            "type": "error",
                            "message": f"未知消息类型: {message_type}",
                            "timestamp": time.time()
                        }
                    
                    # 发送响应
                    await websocket.send_json(response)
                    
                    # 更新发送统计
                    if conn_info:
                        conn_info.messages_sent += 1
                        conn_info.bytes_sent += len(json.dumps(response))
                    
                except WebSocketDisconnect:
                    logger.info(f"WebSocket连接断开: {connection_id}")
                    break
                except Exception as e:
                    logger.error(f"处理WebSocket消息失败: {e}")
                    error_response = {
                        "type": "error",
                        "message": f"消息处理失败: {str(e)}",
                        "timestamp": time.time()
                    }
                    await websocket.send_json(error_response)
                    
        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            # 清理连接
            if 'connection_id' in locals():
                await network_optimizer.connection_pool.remove_connection(connection_id)

    @router.get("/performance/report")
    async def get_performance_report():
        """获取网络性能报告"""
        try:
            network_optimizer = await get_network_optimizer()
            stats = await network_optimizer.get_network_stats()
            
            # 计算性能指标
            connections = stats["connections"]
            compression = stats["compression"]
            performance = stats["performance"]
            
            # 连接效率
            connection_efficiency = (
                connections["active_connections"] / max(connections["total_connections"], 1) * 100
            )
            
            # 压缩效率
            compression_efficiency = (
                (1 - compression.get("compression_ratio", 1)) * 100
                if compression.get("compression_ratio", 0) > 0 else 0
            )
            
            # 错误率
            error_rate = (
                performance["error_count"] / max(performance["total_messages"], 1) * 100
            )
            
            # 性能评分
            performance_score = max(0, min(100, 
                connection_efficiency * 0.3 + 
                compression_efficiency * 0.3 + 
                (100 - error_rate) * 0.4
            ))
            
            report = {
                "overall_score": performance_score,
                "connection_efficiency": connection_efficiency,
                "compression_efficiency": compression_efficiency,
                "error_rate": error_rate,
                "avg_response_time": performance["avg_response_time"],
                "total_messages": performance["total_messages"],
                "total_bytes_sent": performance["total_bytes_sent"],
                "total_bytes_received": performance["total_bytes_received"],
                "active_connections": connections["active_connections"],
                "websocket_connections": connections["websocket_connections"],
                "recommendations": []
            }
            
            # 生成优化建议
            if connection_efficiency < 70:
                report["recommendations"].append("考虑清理闲置连接")
            
            if compression_efficiency < 30 and stats["config"]["compression_enabled"]:
                report["recommendations"].append("调整压缩参数以提高效率")
            
            if error_rate > 5:
                report["recommendations"].append("检查网络稳定性和错误处理")
            
            if performance["avg_response_time"] > 1.0:
                report["recommendations"].append("优化响应时间")
            
            return JSONResponse(content={
                "success": True,
                "data": report,
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"获取性能报告失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取性能报告失败: {str(e)}")

    @router.post("/test/latency")
    async def test_network_latency(target_url: str = "http://localhost:8000"):
        """测试网络延迟"""
        try:
            network_optimizer = await get_network_optimizer()
            
            # 测试多次请求的延迟
            latencies = []
            for i in range(5):
                start_time = time.time()
                try:
                    result = await network_optimizer.make_http2_request(f"{target_url}/api/v1/health/")
                    latency = (time.time() - start_time) * 1000  # 转换为毫秒
                    latencies.append(latency)
                except Exception as e:
                    logger.warning(f"延迟测试请求失败: {e}")
                    latencies.append(-1)  # 失败标记
                
                await asyncio.sleep(0.1)  # 短暂延迟
            
            # 计算统计
            valid_latencies = [l for l in latencies if l > 0]
            if valid_latencies:
                avg_latency = sum(valid_latencies) / len(valid_latencies)
                min_latency = min(valid_latencies)
                max_latency = max(valid_latencies)
                success_rate = len(valid_latencies) / len(latencies) * 100
            else:
                avg_latency = min_latency = max_latency = 0
                success_rate = 0
            
            return JSONResponse(content={
                "success": True,
                "data": {
                    "target_url": target_url,
                    "test_count": len(latencies),
                    "success_rate": success_rate,
                    "avg_latency_ms": avg_latency,
                    "min_latency_ms": min_latency,
                    "max_latency_ms": max_latency,
                    "latencies": latencies
                },
                "timestamp": int(time.time())
            })
            
        except Exception as e:
            logger.error(f"网络延迟测试失败: {e}")
            raise HTTPException(status_code=500, detail=f"网络延迟测试失败: {str(e)}")

    return router 