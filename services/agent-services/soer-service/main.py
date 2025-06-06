"""
main - 索克生活项目模块
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from soer_service.agent.soer_agent import SoerAgent
from soer_service.config.settings import get_settings
from soer_service.delivery.api.analytics import analytics_router
from soer_service.delivery.api.companion import companion_router
from soer_service.delivery.api.devices import devices_router
from soer_service.delivery.api.health import health_router
from soer_service.delivery.api.lifestyle import lifestyle_router
from soer_service.observability.monitoring import setup_monitoring
from soer_service.platform.lifecycle import AgentLifecycleManager
import os
import sys
import uvicorn

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索儿智能体服务主入口
LIFE频道版主，提供生活健康管理、陪伴服务和数据整合分析
"""


# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# 全局变量
soer_agent: SoerAgent = None
lifecycle_manager: AgentLifecycleManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global soer_agent, lifecycle_manager
    
    try:
        logger.info("💖 启动索儿智能体服务...")
        
        # 获取配置
        settings = get_settings()
        
        # 初始化生命周期管理器
        lifecycle_manager = AgentLifecycleManager(settings)
        
        # 初始化索儿智能体
        soer_agent = SoerAgent(settings)
        await soer_agent.initialize()
        
        # 注册到生命周期管理器
        await lifecycle_manager.register_agent(soer_agent)
        
        # 设置监控
        setup_monitoring(app, soer_agent)
        
        logger.info("✅ 索儿智能体服务启动成功")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 索儿智能体服务启动失败: {e}")
        raise
    finally:
        # 清理资源
        if soer_agent:
            await soer_agent.cleanup()
        if lifecycle_manager:
            await lifecycle_manager.cleanup()
        logger.info("🔄 索儿智能体服务已停止")

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()
    
    app = FastAPI(

# 性能优化: 添加响应压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
        title="索儿智能体服务",
        description="LIFE频道版主，提供生活健康管理、陪伴服务和数据整合分析",
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
    app.include_router(lifestyle_router, prefix="/lifestyle", tags=["生活方式"])
    app.include_router(companion_router, prefix="/companion", tags=["陪伴服务"])
    app.include_router(analytics_router, prefix="/analytics", tags=["数据分析"])
    app.include_router(devices_router, prefix="/devices", tags=["设备管理"])
    
    return app

def get_soer_agent() -> SoerAgent:
    """获取索儿智能体实例"""
    if soer_agent is None:
        raise HTTPException(status_code=503, detail="索儿智能体服务未就绪")
    return soer_agent

# 创建应用实例
app = create_app()

@cache(expire=300)  # 5分钟缓存
@limiter.limit("100/minute")  # 每分钟100次请求
@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "索儿智能体服务",
        "description": "LIFE频道版主，贴心温暖的全方位陪伴",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "个性化健康管理",
            "生活陪伴与情感支持",
            "多源数据整合分析",
            "智能设备协调",
            @cache(expire=@limiter.limit("100/minute")  # 每分钟100次请求
300)  # 5分钟缓存
"生活方式优化建议"
        ]
    }

@app.get("/agent/status")
async def get_agent_status(agent: SoerAgent = Depends(get_soer_agent)):
    """获取智能体状态"""
    return await agent.get_status()

@app.post("/agent/message")
async def send_message(
    message: dict,
    agent: SoerAgent = Depends(get_soer_agent)
):
    """发送消息给索儿"""
    try:
        response = await agent.process_message(
            message.get("text", ""),
            message.get("context", {}),
            message.get("user_id"),
            message.get("session_id")
        )
        return response
    except Exception as e:
        logger@limiter.limit("100/minute")  # 每分钟100次请求
.error(f"处理消息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/analyze-health-data")
async def analyze_health_data(
    request: dict,
    agent: SoerAgent = Depends(get_soer_agent)
):
    """分析健康数据"""
    try:
        analysis = await agent.analyze_health_data(
            user_id=request.get("user_id"),
            data_sources=request.get("data_sources", []),
            time_range=request.get("time_range"),
            analysis_type=request.get("analysis_type", "comprehensive")
        )
        return analysis
 @limiter.limit("100/minute")  # 每分钟100次请求
   except Exception as e:
        logger.error(f"健康数据分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/create-lifestyle-plan")
async def create_lifestyle_plan(
    request: dict,
    agent: SoerAgent = Depends(get_soer_agent)
):
    """创建生活方式计划"""
    try:
        plan = await agent.create_lifestyle_plan(
            user_profile=request.get("user_profile"),
            health_goals=request.get("health_goals", []),
            constraints=request.get("constraints", {}),
            preferences=request.get("preferenc@limiter.limit("100/minute")  # 每分钟100次请求
es", {})
        )
        return plan
    except Exception as e:
        logger.error(f"创建生活方式计划失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/companion-chat")
async def companion_chat(
    request: dict,
    agent: SoerAgent = Depends(get_soer_agent)
):
    """陪伴聊天"""
    try:
        response = await agent.companion_chat(
            user_id=request.get("user_id"),
            message=request.get("message", ""),
            mood=request.get("mood@limiter.limit("100/minute")  # 每分钟100次请求
"),
            context=request.get("context", {})
        )
        return response
    except Exception as e:
        logger.error(f"陪伴聊天失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/coordinate-devices")
async def coordinate_devices(
    request: dict,
    agent: SoerAgent = Depends(get_soer_agent)
):
    """协调智能设备"""
    try:
        result = await agent.coordinate_devices(
            user_id=request.get("user_id"),
            devices=request.get("devices", []),
            scenario=request.get("scenario"),
            preferences=request.get("preferences", {})
        )
        return result
    except Exception as e:
        logger.error(f"设备协调失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """主函数"""
    settings = get_settings()
    
    logger.info("🚀 启动索儿智能体服务...")
    
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