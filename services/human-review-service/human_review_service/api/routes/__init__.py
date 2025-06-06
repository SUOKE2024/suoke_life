"""
__init__ - 索克生活项目模块
"""

from .dashboard import router as dashboard_router
from .reviewers import router as reviewers_router
from .reviews import router as reviews_router
from .websocket import router as websocket_router
from fastapi import APIRouter

"""
API 路由
API Routes

定义所有的 API 端点和路由
"""



# 创建主路由器
router = APIRouter()

# 根端点
@router.get("/", tags=["Root"])
async def root():
    """API根端点"""
    return {
        "message": "human-review-service is running",
        "service": "Human Review Service",
        "version": "1.0.0",
        "status": "active"
    }

# 注册子路由
router.include_router(reviews_router, prefix="/tasks", tags=["Tasks"])
router.include_router(reviewers_router, prefix="/reviewers", tags=["Reviewers"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
router.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])

__all__ = ["router"]
