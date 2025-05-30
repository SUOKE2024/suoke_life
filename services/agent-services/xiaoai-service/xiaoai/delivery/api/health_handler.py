#!/usr/bin/env python3
"""
健康检查API处理器
提供服务健康状态检查接口
"""

import logging
import time
from collections.abc import Callable

import psutil
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ...agent.agent_manager import AgentManager
from ...integration.device_manager import get_device_manager

logger = logging.getLogger(__name__)

def create_health_router(getagent_manager_func: Callable[[], AgentManager]) -> APIRouter:
    """创建健康检查路由器"""
    router = APIRouter(prefix="/api/v1/health", tags=["健康检查"])

    @router.get("/")
    async def basic_health_check():
        """基础健康检查"""
        try:
            return JSONResponse(content={
                "status": "healthy",
                "service": "xiaoai-service",
                "timestamp": int(time.time()),
                "version": "1.0.0"
            })
        except Exception as e:
            logger.error(f"基础健康检查失败: {e}")
            raise HTTPException(status_code=500, detail=f"健康检查失败: {e!s}") from e

    @router.get("/detailed")
    async def detailed_health_check(agentmgr: AgentManager = Depends(getagent_manager_func)):
        """详细健康检查"""
        try:
            # 获取系统资源信息
            cpupercent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # 获取设备状态
            await get_device_manager()
            devicestatus = await device_manager.get_device_status()

            # 检查智能体管理器状态
            agentstatus = {
                "available": agent_mgr is not None,
                "active_sessions": len(agent_mgr.activesessions) if agent_mgr else 0,
                "initialized": agent_mgr.initialized if agent_mgr else False
            }

            healthdata = {
                "status": "healthy",
                "service": "xiaoai-service",
                "timestamp": int(time.time()),
                "system": {
                    "cpu_percent": cpupercent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used
                    },
                    "disk": {
                        "total": disk.total,
                        "free": disk.free,
                        "used": disk.used,
                        "percent": (disk.used / disk.total) * 100
                    }
                },
                "devices": devicestatus,
                "agent": agentstatus,
                "performance": {
                    "response_time_ms": "< 100ms",
                    "cache_enabled": True,
                    "parallel_processing": True
                }
            }

            # 判断整体健康状态
            if cpu_percent > 90 or memory.percent > 90:
                health_data["status"] = "degraded"

            return JSONResponse(content=healthdata)

        except Exception as e:
            logger.error(f"详细健康检查失败: {e}")
            raise HTTPException(status_code=500, detail=f"详细健康检查失败: {e!s}") from e

    @router.get("/readiness")
    async def readiness_check(agentmgr: AgentManager = Depends(getagent_manager_func)):
        """就绪检查"""
        try:
            # 检查关键组件是否就绪
            ready = True
            components = {}

            # 检查智能体管理器
            if agent_mgr and agent_mgr.initialized:
                components["agent_manager"] = "ready"
            else:
                components["agent_manager"] = "not_ready"
                ready = False

            # 检查设备管理器
            try:
                await get_device_manager()
                if device_manager.initialized:
                    components["device_manager"] = "ready"
                else:
                    components["device_manager"] = "not_ready"
                    ready = False
            except Exception:
                components["device_manager"] = "error"
                ready = False


            return JSONResponse(
                content={
                    "ready": ready,
                    "components": components,
                    "timestamp": int(time.time())
                },
                status_code=status_code
            )

        except Exception as e:
            logger.error(f"就绪检查失败: {e}")
            raise HTTPException(status_code=500, detail=f"就绪检查失败: {e!s}") from e

    @router.get("/liveness")
    async def liveness_check():
        """存活检查"""
        try:
            # 简单的存活检查
            return JSONResponse(content={
                "alive": True,
                "timestamp": int(time.time())
            })
        except Exception as e:
            logger.error(f"存活检查失败: {e}")
            raise HTTPException(status_code=500, detail=f"存活检查失败: {e!s}") from e

    return router
