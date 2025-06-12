"""
API模块初始化
"""

from fastapi import APIRouter

from .accessibility import router as accessibility_router
from .diagnosis import router as diagnosis_router
from .health import router as health_router


def create_api_router() -> APIRouter:
    """创建API路由器"""
    api_router = APIRouter(prefix="/api/v1")

    # 注册各个模块的路由
    api_router.include_router(diagnosis_router)
    api_router.include_router(health_router)
    api_router.include_router(accessibility_router)

    return api_router


__all__ = ["create_api_router"]
