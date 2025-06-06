"""
__init__ - 索克生活项目模块
"""

from .auth import router as auth_router
from .health_data import router as health_data_router
from .integration import router as integration_router
from .platforms import router as platforms_router
from fastapi import APIRouter

"""
API Delivery Layer
"""



# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(integration_router, prefix="/integrations", tags=["集成管理"])
router.include_router(auth_router, prefix="/auth", tags=["认证授权"])
router.include_router(health_data_router, prefix="/health-data", tags=["健康数据"])
router.include_router(platforms_router, prefix="/platforms", tags=["平台信息"])

__all__ = ["router"]
