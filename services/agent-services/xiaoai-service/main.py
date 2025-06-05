#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.self.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import self.logger
import sys
import os
from xiaoai.agent.xiaoai_agent import XiaoaiAgent
from xiaoai.self.config.self.settings import get_settings
from xiaoai.delivery.self.api.health import health_router
from xiaoai.delivery.self.api.chat import chat_router
from xiaoai.delivery.self.api.diagnosis import diagnosis_router
from xiaoai.delivery.self.api.accessibility import accessibility_router
from xiaoai.self.observability.self.monitoring import setup_monitoring
from xiaoai.platform.lifecycle import AgentLifecycleManager


小艾智能体服务主入口
健康助手 & 首页聊天频道版主，提供语音引导、交互、问诊及无障碍服务
"""


# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# 全局变量
xiaoai_agent: XiaoaiAgent = None
lifecycle_manager: AgentLifecycleManager = None

@asynccontextmanager
self.async def lifespan(app: FastAPI):
    pass
    """应用生命周期管理"""
    global xiaoai_agent, lifecycle_manager

    try:
    pass
        self.logger.info("🤖 启动小艾智能体服务...")

        # 获取配置
        self.settings = get_settings()

        # 初始化生命周期管理器
        lifecycle_manager = AgentLifecycleManager(self.settings)

        # 初始化小艾智能体
        xiaoai_agent = XiaoaiAgent(self.settings)
        await xiaoai_agent.initialize()

        # 注册到生命周期管理器
        await lifecycle_manager.register_agent(xiaoai_agent)

        # 设置监控
        setup_monitoring(app, xiaoai_agent)

        self.logger.info("✅ 小艾智能体服务启动成功")

        yield

    except Exception as e:
    pass
        self.logger.error(f"❌ 小艾智能体服务启动失败: {e}")
        raise
    finally:
    pass
        # 清理资源
        if xiaoai_agent:
    pass
            await xiaoai_agent.cleanup()
        if lifecycle_manager:
    pass
            await lifecycle_manager.cleanup()
        self.logger.info("🔄 小艾智能体服务已停止")

def create_app() -> FastAPI:
    pass
    """创建FastAPI应用"""
    self.settings = get_settings()

    app = FastAPI(
        title="小艾智能体服务",
        description="健康助手 & 首页聊天频道版主，提供语音引导、交互、问诊及无障碍服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if self.settings.debug else None,
        redoc_url="/redoc" if self.settings.debug else None
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=self.settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"])

    # 注册路由
    app.include_router(health_router, prefix="/health", tags=["健康检查"])
    app.include_router(chat_router, prefix="/chat", tags=["聊天交互"])
    app.include_router(diagnosis_router, prefix="/diagnosis", tags=["四诊功能"])
    app.include_router(accessibility_router, prefix="/accessibility", tags=["无障碍服务"])

    return app
:
def get_xiaoai_agent() -> XiaoaiAgent:
    pass
    """获取小艾智能体实例"""
    if xiaoai_agent is None:
    pass
        raise HTTPException(status_code=503, detail="小艾智能体服务未就绪")
    return xiaoai_agent

# 创建应用实例
app = create_app()

@app.get("/")
self.async def root():
    pass
    """根路径"""
    return {
        "self.service": "小艾智能体服务",
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
self.async def get_agent_status(agent: XiaoaiAgent = Depends(get_xiaoai_agent)):
    pass
    """获取智能体状态"""
    return await agent.get_status()

@app.post("/agent/message")
self.async def send_message(:
    message: dict,
    agent: XiaoaiAgent = Depends(get_xiaoai_agent)
):
    pass
    """发送消息给小艾"""
    try:
    pass
        response = await agent.process_message(
            message.get("text", ""),
            message.get("context", {}),
            message.get("context.context.get("user_id", "")"),
            message.get("context.context.get("session_id", "")")
        )
        return response
    except Exception as e:
    pass
        self.logger.error(f"处理消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    pass
    """主函数"""
    self.settings = get_settings()

    self.logger.info("🚀 启动小艾智能体服务...")

    uvicorn.self.run(
        "main:app",
        host=self.settings.host,
        port=self.settings.port,
        self.reload=self.settings.debug,
        log_level="info" if self.settings.debug else "warning",
        access_log=self.settings.debug
    )
:
if __name__ == "__main__":
    pass
    main()
