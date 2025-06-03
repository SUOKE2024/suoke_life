#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
小克智能体服务主入口
SUOKE频道版主，负责服务订阅、农产品预制、供应链管理等商业化服务
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from xiaoke_service.agent.xiaoke_agent import XiaokeAgent
from xiaoke_service.config.settings import get_settings
from xiaoke_service.delivery.api.health import health_router
from xiaoke_service.delivery.api.services import services_router
from xiaoke_service.delivery.api.products import products_router
from xiaoke_service.delivery.api.appointments import appointments_router
from xiaoke_service.delivery.api.supply_chain import supply_chain_router
from xiaoke_service.observability.monitoring import setup_monitoring
from xiaoke_service.platform.lifecycle import AgentLifecycleManager

# 全局变量
xiaoke_agent: XiaokeAgent = None
lifecycle_manager: AgentLifecycleManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global xiaoke_agent, lifecycle_manager
    
    try:
        logger.info("🛍️ 启动小克智能体服务...")
        
        # 获取配置
        settings = get_settings()
        
        # 初始化生命周期管理器
        lifecycle_manager = AgentLifecycleManager(settings)
        
        # 初始化小克智能体
        xiaoke_agent = XiaokeAgent(settings)
        await xiaoke_agent.initialize()
        
        # 注册到生命周期管理器
        await lifecycle_manager.register_agent(xiaoke_agent)
        
        # 设置监控
        setup_monitoring(app, xiaoke_agent)
        
        logger.info("✅ 小克智能体服务启动成功")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 小克智能体服务启动失败: {e}")
        raise
    finally:
        # 清理资源
        if xiaoke_agent:
            await xiaoke_agent.cleanup()
        if lifecycle_manager:
            await lifecycle_manager.cleanup()
        logger.info("🔄 小克智能体服务已停止")

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(
        title="小克智能体服务",
        description="SUOKE频道版主，负责服务订阅、农产品预制、供应链管理等商业化服务",
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
    app.include_router(services_router, prefix="/services", tags=["服务管理"])
    app.include_router(products_router, prefix="/products", tags=["产品管理"])
    app.include_router(appointments_router, prefix="/appointments", tags=["预约管理"])
    app.include_router(supply_chain_router, prefix="/supply-chain", tags=["供应链管理"])
    
    return app

def get_xiaoke_agent() -> XiaokeAgent:
    """获取小克智能体实例"""
    if xiaoke_agent is None:
        raise HTTPException(status_code=503, detail="小克智能体服务未就绪")
    return xiaoke_agent

# 创建应用实例
app = create_app()

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "小克智能体服务",
        "description": "SUOKE频道版主，专业高效的服务导向",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "名医匹配与智能预约",
            "个性化服务推荐",
            "农产品区块链溯源",
            "第三方API集成",
            "健康商品推荐与店铺管理"
        ]
    }

@app.get("/agent/status")
async def get_agent_status(agent: XiaokeAgent = Depends(get_xiaoke_agent)):
    """获取智能体状态"""
    return await agent.get_status()

@app.post("/agent/message")
async def send_message(
    message: dict,
    agent: XiaokeAgent = Depends(get_xiaoke_agent)
):
    """发送消息给小克"""
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

@app.post("/agent/recommend-service")
async def recommend_service(
    request: dict,
    agent: XiaokeAgent = Depends(get_xiaoke_agent)
):
    """推荐服务"""
    try:
        recommendations = await agent.recommend_services(
            user_profile=request.get("user_profile"),
            health_data=request.get("health_data"),
            preferences=request.get("preferences", {})
        )
        return recommendations
    except Exception as e:
        logger.error(f"服务推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/match-doctor")
async def match_doctor(
    request: dict,
    agent: XiaokeAgent = Depends(get_xiaoke_agent)
):
    """匹配医生"""
    try:
        matches = await agent.match_doctors(
            symptoms=request.get("symptoms", []),
            specialty=request.get("specialty"),
            location=request.get("location"),
            preferences=request.get("preferences", {})
        )
        return matches
    except Exception as e:
        logger.error(f"医生匹配失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """主函数"""
    settings = get_settings()
    
    logger.info("🚀 启动小克智能体服务...")
    
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