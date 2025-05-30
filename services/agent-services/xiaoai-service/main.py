#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾智能体服务主入口
健康助手 & 首页聊天频道版主，提供语音引导、交互、问诊及无障碍服务
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

from xiaoai.agent.xiaoai_agent import XiaoaiAgent
from xiaoai.config.settings import get_settings
from xiaoai.delivery.api.health import health_router
from xiaoai.delivery.api.chat import chat_router
from xiaoai.delivery.api.diagnosis import diagnosis_router
from xiaoai.delivery.api.accessibility import accessibility_router
from xiaoai.observability.monitoring import setup_monitoring
from xiaoai.platform.lifecycle import AgentLifecycleManager


# 全局变量
xiaoai_agent: XiaoaiAgent = None
lifecycle_manager: AgentLifecycleManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global xiaoai_agent, lifecycle_manager
    
    try:
        logger.info("🤖 启动小艾智能体服务...")
        
        # 获取配置
        settings = get_settings()
        
        # 初始化生命周期管理器
        lifecycle_manager = AgentLifecycleManager(settings)
        
        # 初始化小艾智能体
        xiaoai_agent = XiaoaiAgent(settings)
        await xiaoai_agent.initialize()
        
        # 注册到生命周期管理器
        await lifecycle_manager.register_agent(xiaoai_agent)
        
        # 设置监控
        setup_monitoring(app, xiaoai_agent)
        
        logger.info("✅ 小艾智能体服务启动成功")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 小艾智能体服务启动失败: {e}")
        raise
    finally:
        # 清理资源
        if xiaoai_agent:
            await xiaoai_agent.cleanup()
        if lifecycle_manager:
            await lifecycle_manager.cleanup()
        logger.info("🔄 小艾智能体服务已停止")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="小艾智能体服务",
        description="健康助手 & 首页聊天频道版主，提供语音引导、交互、问诊及无障碍服务",
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
    app.include_router(chat_router, prefix="/chat", tags=["聊天交互"])
    app.include_router(diagnosis_router, prefix="/diagnosis", tags=["四诊功能"])
    app.include_router(accessibility_router, prefix="/accessibility", tags=["无障碍服务"])
    
    return app


def get_xiaoai_agent() -> XiaoaiAgent:
    """获取小艾智能体实例"""
    if xiaoai_agent is None:
        raise HTTPException(status_code=503, detail="小艾智能体服务未就绪")
    return xiaoai_agent


# 创建应用实例
app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "小艾智能体服务",
        "description": "健康助手 & 首页聊天频道版主",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "语音交互与多模态理解",
            "中医望诊与智能问诊", 
            "无障碍服务（导盲导医、手语识别）",
            "实时健康档案管理"
        ]
    }


@app.get("/agent/status")
async def get_agent_status(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    """获取智能体状态"""
    return await agent.get_status()


@app.post("/agent/message")
async def send_message(
    message: dict,
    agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    """发送消息给小艾"""
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


def main():
    """主函数"""
    settings = get_settings()
    
    logger.info("🚀 启动小艾智能体服务...")
    
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
