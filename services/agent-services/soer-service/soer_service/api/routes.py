"""
API 路由模块

集成所有API端点路由
"""

from fastapi import APIRouter
from .endpoints import agent, health, lifestyle, nutrition

# 创建主路由器
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(
    agent.router,
    prefix="/agent",
    tags=["智能体"]
)

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["健康管理"]
)

api_router.include_router(
    lifestyle.router,
    prefix="/lifestyle",
    tags=["生活方式"]
)

api_router.include_router(
    nutrition.router,
    prefix="/nutrition",
    tags=["营养分析"]
)