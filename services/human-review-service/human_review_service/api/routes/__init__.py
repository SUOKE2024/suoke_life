"""
API 路由
API Routes

定义所有的 API 端点和路由
"""

from fastapi import APIRouter

from .dashboard import router as dashboard_router
from .reviews import router as reviews_router
from .reviewers import router as reviewers_router
from .websocket import router as websocket_router

# 创建主路由器
router = APIRouter()

# 注册子路由
router.include_router(reviews_router, prefix="/tasks", tags=["Tasks"])
router.include_router(reviewers_router, prefix="/reviewers", tags=["Reviewers"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

__all__ = ["router"] 