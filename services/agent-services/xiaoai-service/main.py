#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小艾智能体服务主入口
健康助手 & 首页聊天频道版主，提供语音引导、交互、问诊及无障碍服务
"""

import os
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from xiaoai.agent.xiaoai_agent import XiaoaiAgent
    from xiaoai.config.settings import get_settings
    from xiaoai.delivery.api.health import health_router
    from xiaoai.delivery.api.chat import chat_router
    from xiaoai.platform.lifecycle import AgentLifecycleManager
    from xiaoai.observability.monitoring import setup_monitoring
except ImportError as e:
    logger.warning(f"导入模块失败: {e}")
    # 创建占位符类
    from fastapi import APIRouter
    
    class XiaoaiAgent:
        def __init__(self, settings=None):
            self.settings = settings
            self.status = "ready"
            self.capabilities = ["基础聊天功能"]
            self.multimodal_config = {}
        
        async def initialize(self):
            pass
        
        async def cleanup(self):
            pass
        
        async def get_status(self):
            return {"status": "ok", "agent": "xiaoai"}
        
        async def process_message(self, text, context=None, user_id=None, session_id=None):
            return {"response": f"收到消息: {text}", "agent": "xiaoai", "session_id": session_id or "default"}
    
    class AgentLifecycleManager:
        def __init__(self, settings):
            self.settings = settings
        
        async def register_agent(self, agent):
            pass
        
        async def cleanup(self):
            pass
    
    def get_settings():
        class Settings:
            debug = True
            host = "0.0.0.0"
            port = 8001
            allowed_origins = ["*"]
        return Settings()
    
    # 创建占位符路由
    health_router = APIRouter()
    chat_router = APIRouter()
    
    @health_router.get("/")
    async def health_check():
        return {"status": "ok", "service": "xiaoai-service"}
    
    @chat_router.post("/message")
    async def send_message(message: dict):
        return {"response": f"收到消息: {message.get('text', '')}", "agent": "xiaoai"}
    
    def setup_monitoring(app, agent):
        pass

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
        allow_headers=["*"]
    )

    # 性能优化: 添加响应压缩
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 注册路由
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    app.include_router(chat_router, prefix="/chat", tags=["聊天交互"])

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
            message.get("context"),
            message.get("user_id"),
            message.get("session_id")
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """主函数"""
    settings = get_settings()
    
    logger.info(f"启动小艾智能体服务 - {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
