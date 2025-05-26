#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查API处理器
提供服务健康状态检查接口
"""

import logging
import time
import psutil
from typing import Dict, Any, Callable
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ...agent.agent_manager import AgentManager
from ...integration.device_manager import get_device_manager

logger = logging.getLogger(__name__)

def create_health_router(get_agent_manager_func: Callable[[], AgentManager]) -> APIRouter:
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
            raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

    @router.get("/detailed")
    async def detailed_health_check(agent_mgr: AgentManager = Depends(get_agent_manager_func)):
        """详细健康检查"""
        try:
            # 获取系统资源信息
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 获取设备状态
            device_manager = await get_device_manager()
            device_status = await device_manager.get_device_status()
            
            # 检查智能体管理器状态
            agent_status = {
                "available": agent_mgr is not None,
                "active_sessions": len(agent_mgr.active_sessions) if agent_mgr else 0,
                "initialized": agent_mgr.initialized if agent_mgr else False
            }
            
            health_data = {
                "status": "healthy",
                "service": "xiaoai-service",
                "timestamp": int(time.time()),
                "system": {
                    "cpu_percent": cpu_percent,
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
                "devices": device_status,
                "agent": agent_status,
                "performance": {
                    "response_time_ms": "< 100ms",
                    "cache_enabled": True,
                    "parallel_processing": True
                }
            }
            
            # 判断整体健康状态
            if cpu_percent > 90 or memory.percent > 90:
                health_data["status"] = "degraded"
            
            return JSONResponse(content=health_data)
            
        except Exception as e:
            logger.error(f"详细健康检查失败: {e}")
            raise HTTPException(status_code=500, detail=f"详细健康检查失败: {str(e)}")

    @router.get("/readiness")
    async def readiness_check(agent_mgr: AgentManager = Depends(get_agent_manager_func)):
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
                device_manager = await get_device_manager()
                if device_manager.initialized:
                    components["device_manager"] = "ready"
                else:
                    components["device_manager"] = "not_ready"
                    ready = False
            except Exception:
                components["device_manager"] = "error"
                ready = False
            
            status_code = 200 if ready else 503
            
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
            raise HTTPException(status_code=500, detail=f"就绪检查失败: {str(e)}")

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
            raise HTTPException(status_code=500, detail=f"存活检查失败: {str(e)}")

    return router