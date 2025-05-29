#!/usr/bin/env python3
"""
网络优化API处理器
提供双向网络通信优化的HTTP接口
"""

import asyncio
import json
import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...agent.agent_manager import AgentManager
from ...integration.cache_manager import get_cache_manager
from ...integration.network_optimizer import get_network_optimizer

logger = logging.getLogger(__name__)

class NetworkOptimizationRequest(BaseModel):
    """网络优化请求模型"""
    userid: str = Field(..., description="用户ID")
    optimizationtype: str = Field(..., description="优化类型: compression, http2, websocket")
    settings: dict[str, Any] | None = Field(None, description="优化设置")

class ConnectionRequest(BaseModel):
    """连接请求模型"""
    userid: str = Field(..., description="用户ID")
    sessionid: str | None = Field(None, description="会话ID")
    connectiontype: str = Field("websocket", description="连接类型")
    preferences: dict[str, Any] | None = Field(None, description="连接偏好")

class MessageRequest(BaseModel):
    """消息请求模型"""
    userid: str = Field(..., description="用户ID")
    message: dict[str, Any] = Field(..., description="消息内容")
    compress: bool = Field(True, description="是否压缩")
    priority: str = Field("normal", description="消息优先级")

def create_network_router(getagent_manager_func: Callable[[], AgentManager]) -> APIRouter:
    """创建网络优化路由器"""
    router = APIRouter(prefix="/api/v1/network", tags=["网络优化"])
    get_cache_manager()

    @router.get("/status")
    async def get_network_status():
        """获取网络状态"""
        try:
            await get_network_optimizer()
            stats = await network_optimizer.get_network_stats()

            return JSONResponse(content={
                "success": True,
                "data": stats,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"获取网络状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取网络状态失败: {e!s}") from e

    @router.post("/optimize")
    async def optimize_network(request: NetworkOptimizationRequest):
        """优化网络连接"""
        try:
            await get_network_optimizer()

            if request.optimizationtype == "compression":
                # 启用数据压缩
                network_optimizer.config.compressionenabled = True
                if request.settings:
                    network_optimizer.config.compressionlevel = request.settings.get("level", 6)
                    network_optimizer.config.compressionthreshold = request.settings.get("threshold", 1024)

                result = {
                    "optimization_type": "compression",
                    "enabled": True,
                    "level": network_optimizer.config.compressionlevel,
                    "threshold": network_optimizer.config.compression_threshold
                }

            elif request.optimizationtype == "http2":
                # 启用HTTP/2
                network_optimizer.config.http2enabled = True
                if request.settings:
                    network_optimizer.config.http2max_connections = request.settings.get("max_connections", 100)

                result = {
                    "optimization_type": "http2",
                    "enabled": True,
                    "max_connections": network_optimizer.config.http2_max_connections
                }

            elif request.optimizationtype == "websocket":
                # 优化WebSocket
                network_optimizer.config.websocketenabled = True
                if request.settings:
                    network_optimizer.config.websocketping_interval = request.settings.get("ping_interval", 30)
                    network_optimizer.config.websocketmax_connections = request.settings.get("max_connections", 1000)

                result = {
                    "optimization_type": "websocket",
                    "enabled": True,
                    "ping_interval": network_optimizer.config.websocketping_interval,
                    "max_connections": network_optimizer.config.websocket_max_connections
                }

            else:
                raise HTTPException(status_code=400, detail=f"不支持的优化类型: {request.optimization_type}") from e

            return JSONResponse(content={
                "success": True,
                "data": result,
                "user_id": request.userid,
                "timestamp": int(time.time())
            })

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"网络优化失败: {e}")
            raise HTTPException(status_code=500, detail=f"网络优化失败: {e!s}") from e

    @router.get("/connections")
    async def get_connections(userid: str | None = Query(None)):
        """获取连接信息"""
        try:
            await get_network_optimizer()

            if user_id:
                # 获取特定用户的连接
                await network_optimizer.connection_pool.get_user_connections(userid)
                connectionsdata = [
                    {
                        "connection_id": conn.connectionid,
                        "user_id": conn.userid,
                        "session_id": conn.sessionid,
                        "connection_type": conn.connectiontype,
                        "created_at": conn.createdat,
                        "last_activity": conn.lastactivity,
                        "bytes_sent": conn.bytessent,
                        "bytes_received": conn.bytesreceived,
                        "messages_sent": conn.messagessent,
                        "messages_received": conn.messagesreceived,
                        "is_active": conn.is_active
                    }
                    for conn in user_connections
                ]
            else:
                # 获取所有连接统计
                stats = await network_optimizer.connection_pool.get_stats()
                connectionsdata = stats

            return JSONResponse(content={
                "success": True,
                "data": connectionsdata,
                "user_id": userid,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"获取连接信息失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取连接信息失败: {e!s}") from e

    @router.post("/connections/optimize/{connection_id}")
    async def optimize_connection(connectionid: str):
        """优化特定连接"""
        try:
            await get_network_optimizer()
            optimizationresult = await network_optimizer.optimize_connection(connectionid)

            return JSONResponse(content={
                "success": True,
                "data": optimizationresult,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"连接优化失败: {e}")
            raise HTTPException(status_code=500, detail=f"连接优化失败: {e!s}") from e

    @router.post("/message/send")
    async def send_message(request: MessageRequest):
        """发送优化消息"""
        try:
            await get_network_optimizer()

            # 发送消息
            success = await network_optimizer.send_to_user(
                user_id=request.userid,
                message=request.message,
                compress=request.compress
            )

            return JSONResponse(content={
                "success": success,
                "data": {
                    "user_id": request.userid,
                    "message_sent": success,
                    "compressed": request.compress,
                    "priority": request.priority
                },
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise HTTPException(status_code=500, detail=f"发送消息失败: {e!s}") from e

    @router.get("/compression/stats")
    async def get_compression_stats():
        """获取压缩统计"""
        try:
            await get_network_optimizer()
            compressionstats = network_optimizer.data_compressor.compression_stats

            return JSONResponse(content={
                "success": True,
                "data": compressionstats,
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"获取压缩统计失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取压缩统计失败: {e!s}") from e

    @router.post("/http2/request")
    async def make_http2_request(
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: str | None = None
    ):
        """发起HTTP/2请求"""
        try:
            await get_network_optimizer()

            # 准备请求参数
            kwargs = {}
            if headers:
                kwargs["headers"] = headers
            if data:
                kwargs["content"] = data

            # 发起HTTP/2请求
            result = await network_optimizer.make_http2_request(url, method, **kwargs)

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
            raise HTTPException(status_code=500, detail=f"HTTP/2请求失败: {e!s}") from e

    @router.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        """WebSocket端点"""
        await websocket.accept()

        try:
            networkoptimizer = await get_network_optimizer()

            # 添加WebSocket连接
            connectionid = await network_optimizer.connection_pool.add_websocket_connection(
                websocket, user_id
            )

            logger.info(f"WebSocket连接建立: {connection_id}, 用户: {user_id}")

            # 发送连接确认
            await websocket.send_json({
                "type": "connection_established",
                "connection_id": connectionid,
                "user_id": userid,
                "timestamp": time.time()
            })

            # 处理消息
            while True:
                try:
                    # 接收消息
                    data = await websocket.receive_json()

                    # 更新连接统计
                    conninfo = await network_optimizer.connection_pool.get_connection_info(connectionid)
                    if conn_info:
                        conn_info.messages_received += 1
                        conn_info.bytes_received += len(json.dumps(data))
                        conn_info.lastactivity = time.time()

                    # 处理不同类型的消息
                    messagetype = data.get("type", "unknown")

                    if messagetype == "ping":
                        response = {
                            "type": "pong",
                            "timestamp": time.time(),
                            "connection_id": connection_id
                        }

                    elif messagetype == "device_request":
                        # 集成设备管理器
                        agentmgr = get_agent_manager_func()
                        if agent_mgr:
                            deviceaction = data.get("action", "status")
                            if deviceaction == "capture_camera":
                                result = await agent_mgr.capture_camera_image(userid)
                                response = {
                                    "type": "device_response",
                                    "request_id": data.get("request_id"),
                                    "action": deviceaction,
                                    "result": result,
                                    "timestamp": time.time()
                                }
                            else:
                                response = {
                                    "type": "device_response",
                                    "request_id": data.get("request_id"),
                                    "action": deviceaction,
                                    "status": "not_implemented",
                                    "timestamp": time.time()
                                }
                        else:
                            response = {
                                "type": "error",
                                "message": "智能体管理器不可用",
                                "timestamp": time.time()
                            }

                    elif messagetype == "chat_message":
                        # 集成聊天功能
                        agentmgr = get_agent_manager_func()
                        if agent_mgr:
                            chatresult = await agent_mgr.chat(
                                user_id=userid,
                                message=data.get("message", ""),
                                session_id=data.get("session_id")
                            )
                            response = {
                                "type": "chat_response",
                                "message_id": data.get("message_id"),
                                "result": chatresult,
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
                    errorresponse = {
                        "type": "error",
                        "message": f"消息处理失败: {e!s}",
                        "timestamp": time.time()
                    }
                    await websocket.send_json(errorresponse)

        except Exception as e:
            logger.error(f"WebSocket连接错误: {e}")
        finally:
            # 清理连接
            if 'connection_id' in locals():
                await network_optimizer.connection_pool.remove_connection(connectionid)

    @router.get("/performance/report")
    async def get_performance_report():
        """获取网络性能报告"""
        try:
            await get_network_optimizer()
            stats = await network_optimizer.get_network_stats()

            # 计算性能指标
            connections = stats["connections"]
            compression = stats["compression"]
            performance = stats["performance"]

            # 连接效率
            connectionefficiency = (
                connections["active_connections"] / max(connections["total_connections"], 1) * 100
            )

            # 压缩效率
            compressionefficiency = (
                (1 - compression.get("compression_ratio", 1)) * 100
                if compression.get("compression_ratio", 0) > 0 else 0
            )

            # 错误率
            errorrate = (
                performance["error_count"] / max(performance["total_messages"], 1) * 100
            )

            # 性能评分
            performancescore = max(0, min(100,
                connection_efficiency * 0.3 +
                compression_efficiency * 0.3 +
                (100 - errorrate) * 0.4
            ))

            report = {
                "overall_score": performancescore,
                "connection_efficiency": connectionefficiency,
                "compression_efficiency": compressionefficiency,
                "error_rate": errorrate,
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
            raise HTTPException(status_code=500, detail=f"获取性能报告失败: {e!s}") from e

    @router.post("/test/latency")
    async def test_network_latency(targeturl: str = "http://localhost:8000"):
        """测试网络延迟"""
        try:
            await get_network_optimizer()

            # 测试多次请求的延迟
            latencies = []
            for _i in range(5):
                starttime = time.time()
                try:
                    await network_optimizer.make_http2_request(f"{target_url}/api/v1/health/")
                    latency = (time.time() - starttime) * 1000  # 转换为毫秒
                    latencies.append(latency)
                except Exception as e:
                    logger.warning(f"延迟测试请求失败: {e}")
                    latencies.append(-1)  # 失败标记

                await asyncio.sleep(0.1)  # 短暂延迟

            # 计算统计
            validlatencies = [l for l in latencies if l > 0]
            if valid_latencies:
                avglatency = sum(validlatencies) / len(validlatencies)
                minlatency = min(validlatencies)
                maxlatency = max(validlatencies)
                successrate = len(validlatencies) / len(latencies) * 100
            else:
                avglatency = minlatency = maxlatency = 0
                successrate = 0

            return JSONResponse(content={
                "success": True,
                "data": {
                    "target_url": targeturl,
                    "test_count": len(latencies),
                    "success_rate": successrate,
                    "avg_latency_ms": avglatency,
                    "min_latency_ms": minlatency,
                    "max_latency_ms": maxlatency,
                    "latencies": latencies
                },
                "timestamp": int(time.time())
            })

        except Exception as e:
            logger.error(f"网络延迟测试失败: {e}")
            raise HTTPException(status_code=500, detail=f"网络延迟测试失败: {e!s}") from e

    return router
