"""
API 路由模块

定义所有的 API 端点
"""

from fastapi import APIRouter

from .endpoints import nutrition, health, lifestyle, agent

# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    nutrition.router,
    prefix="/nutrition",
    tags=["营养分析"]
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
    agent.router,
    prefix="/agent",
    tags=["智能体交互"]
) 