#!/usr/bin/env python3
"""
小艾智能体健康检查API模块
提供服务健康状态检查、监控指标和就绪状态检查功能
"""

import time

from fastapi import APIRouter, Depends, HTTPException

from xiaoai.core.agent import XiaoaiAgent

health_router = APIRouter()

async def get_xiaoai_agent() -> XiaoaiAgent:
    """获取小艾智能体实例的依赖注入函数"""
    # 这个函数会在main.py中被重新定义
    raise HTTPException(status_code=503, detail="智能体服务未就绪") from None

@health_router.get("/")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "xiaoai-agent",
        "timestamp": time.time(),
        "version": "1.0.0",
    }

@health_router.get("/detailed")
async def detailed_health_check(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    """详细健康检查"""
    try:
        # 检查智能体状态
        agent_status = await agent.get_health_status()

        return {
            "status": "healthy",
            "service": "xiaoai-agent",
            "timestamp": time.time(),
            "agent_status": agent_status,
            "components": {
                "agent_manager": "healthy" if agent.agent_manager else "unavailable",
                "multimodal_config": "healthy" if agent.multimodal_config else "unavailable",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"健康检查失败: {e!s}") from None

@health_router.get("/metrics")
async def get_metrics(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    """获取监控指标"""
    try:
        # 获取智能体指标
        metrics = await agent.get_metrics()

        return {
            "timestamp": time.time(),
            "service": "xiaoai-agent",
            "metrics": metrics,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取指标失败: {e!s}") from None

@health_router.get("/readiness")
async def readiness_check(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    """就绪状态检查"""
    try:
        # 检查服务是否就绪
        is_ready = await agent.is_ready()

        return {
            "ready": is_ready,
            "service": "xiaoai-agent",
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"就绪检查失败: {e!s}") from None

@health_router.get("/liveness")
async def liveness_check():
    """存活状态检查"""
    return {
        "alive": True,
        "service": "xiaoai-agent",
        "timestamp": time.time(),
    }
