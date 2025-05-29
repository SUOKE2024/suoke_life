"""
医学知识服务REST API主路由
集成各个功能模块的路由
"""

from fastapi import APIRouter

from app.api.rest import constitutions, graph, health, search, symptoms
from app.api.rest.legacy import legacy_routes  # 保留原有路由作为兼容
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter()

# 注册新的模块化路由
router.include_router(health.router)
router.include_router(constitutions.router, prefix="/api/v1")
router.include_router(symptoms.router, prefix="/api/v1")
router.include_router(search.router, prefix="/api/v1")
router.include_router(graph.router, prefix="/api/v1")

# 保留原有路由作为兼容(可以逐步迁移)
router.include_router(legacy_routes.router, prefix="/api/v1")
