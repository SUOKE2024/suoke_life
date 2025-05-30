#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
老克智能体服务主入口
探索频道版主，负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from laoke_service.agent.laoke_agent import LaokeAgent
from laoke_service.config.settings import get_settings
from laoke_service.delivery.api.health import health_router
from laoke_service.delivery.api.knowledge import knowledge_router
from laoke_service.delivery.api.education import education_router
from laoke_service.delivery.api.museum import museum_router
from laoke_service.delivery.api.maze import maze_router
from laoke_service.observability.monitoring import setup_monitoring
from laoke_service.platform.lifecycle import AgentLifecycleManager


# 全局变量
laoke_agent: LaokeAgent = None
lifecycle_manager: AgentLifecycleManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global laoke_agent, lifecycle_manager
    
    try:
        logger.info("📚 启动老克智能体服务...")
        
        # 获取配置
        settings = get_settings()
        
        # 初始化生命周期管理器
        lifecycle_manager = AgentLifecycleManager(settings)
        
        # 初始化老克智能体
        laoke_agent = LaokeAgent(settings)
        await laoke_agent.initialize()
        
        # 注册到生命周期管理器
        await lifecycle_manager.register_agent(laoke_agent)
        
        # 设置监控
        setup_monitoring(app, laoke_agent)
        
        logger.info("✅ 老克智能体服务启动成功")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 老克智能体服务启动失败: {e}")
        raise
    finally:
        # 清理资源
        if laoke_agent:
            await laoke_agent.cleanup()
        if lifecycle_manager:
            await lifecycle_manager.cleanup()
        logger.info("🔄 老克智能体服务已停止")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="老克智能体服务",
        description="探索频道版主，负责知识传播、培训和博物馆导览，兼任玉米迷宫NPC",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    app.include_router(knowledge_router, prefix="/knowledge", tags=["知识管理"])
    app.include_router(education_router, prefix="/education", tags=["教育培训"])
    app.include_router(museum_router, prefix="/museum", tags=["博物馆导览"])
    app.include_router(maze_router, prefix="/maze", tags=["玉米迷宫"])
    
    return app


def get_laoke_agent() -> LaokeAgent:
    """获取老克智能体实例"""
    if laoke_agent is None:
        raise HTTPException(status_code=503, detail="老克智能体服务未就绪")
    return laoke_agent


# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "老克智能体服务",
        "description": "探索频道版主，博学睿智的知识传承者",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "中医知识传播与教育",
            "学习路径规划",
            "AR/VR沉浸式教学",
            "游戏化学习引导",
            "传统文化传承"
        ]
    }


@app.get("/agent/status")
async def get_agent_status(agent: LaokeAgent = Depends(get_laoke_agent)):
    """获取智能体状态"""
    return await agent.get_status()


@app.post("/agent/message")
async def send_message(
    message: dict,
    agent: LaokeAgent = Depends(get_laoke_agent)
):
    """发送消息给老克"""
    try:
        response = await agent.process_message(
            message.get("text", ""),
            message.get("context", {}),
            message.get("user_id"),
            message.get("session_id")
        )
        return response
    except Exception as e:
        logger.error(f"处理消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/search-knowledge")
async def search_knowledge(
    request: dict,
    agent: LaokeAgent = Depends(get_laoke_agent)
):
    """搜索知识"""
    try:
        results = await agent.search_knowledge(
            query=request.get("query", ""),
            category=request.get("category"),
            filters=request.get("filters", {}),
            user_level=request.get("user_level", "beginner")
        )
        return results
    except Exception as e:
        logger.error(f"知识搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/create-learning-path")
async def create_learning_path(
    request: dict,
    agent: LaokeAgent = Depends(get_laoke_agent)
):
    """创建学习路径"""
    try:
        path = await agent.create_learning_path(
            user_profile=request.get("user_profile"),
            learning_goals=request.get("learning_goals", []),
            preferences=request.get("preferences", {}),
            time_constraints=request.get("time_constraints")
        )
        return path
    except Exception as e:
        logger.error(f"创建学习路径失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/maze-interaction")
async def maze_interaction(
    request: dict,
    agent: LaokeAgent = Depends(get_laoke_agent)
):
    """玉米迷宫交互"""
    try:
        response = await agent.maze_npc_interaction(
            player_id=request.get("player_id"),
            action=request.get("action"),
            location=request.get("location"),
            context=request.get("context", {})
        )
        return response
    except Exception as e:
        logger.error(f"迷宫交互失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """主函数"""
    settings = get_settings()
    
    logger.info("🚀 启动老克智能体服务...")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
        access_log=settings.debug
    )


if __name__ == "__main__":
    main() 