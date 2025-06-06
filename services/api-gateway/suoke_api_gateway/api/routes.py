"""
routes - 索克生活项目模块
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from .gateway import gateway_router
from .management import management_router
from fastapi import APIRouter, Depends, HTTPException, Request, status

"""
API 路由定义

定义网关的主要 API 端点。
"""



logger = get_logger(__name__)

# 创建主路由器
api_router = APIRouter()

# 包含子路由
api_router.include_router(gateway_router, prefix="/gateway", tags=["gateway"])
api_router.include_router(management_router, prefix="/management", tags=["management"])

@api_router.get("/")
async def api_root():
    """API 根端点"""
    settings = get_settings()
    return {
        "service": "Suoke API Gateway",
        "version": settings.app_version,
        "status": "running",
        "endpoints": {
            "gateway": "/api/v1/gateway",
            "management": "/api/v1/management",
            "health": "/health",
            "metrics": "/metrics",
        }
    }

@api_router.get("/info")
async def api_info(request: Request):
    """获取 API 信息"""
    settings = get_settings()
    
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "features": {
            "authentication": True,
            "rate_limiting": settings.rate_limit.enabled,
            "monitoring": settings.monitoring.enabled,
            "grpc": settings.grpc.enabled,
        },
        "request_id": getattr(request.state, "request_id", None),
    } 