#!/usr/bin/env python3
"""
索克生活 API 网关路由配置

统一管理所有API路由。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from .gateway import gateway_router
from .management import management_router
from fastapi import APIRouter, Request
from typing import Dict, Any
import time

logger = get_logger(__name__)

# 创建主路由器
api_router = APIRouter()

# 根路径处理
@api_router.get("/", summary="API网关根路径", description="返回API网关基本信息")
async def root() -> Dict[str, Any]:
    """根路径处理"""
    settings = get_settings()
    return {
        "name": "索克生活 API 网关",
        "service": "Suoke API Gateway", 
        "version": settings.app_version,
        "description": "现代化微服务API网关",
        "status": "running",
        "timestamp": time.time(),
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics", 
            "docs": "/docs",
            "redoc": "/redoc",
            "management": "/management",
            "gateway": "/api/v1"
        }
    }

@api_router.get("/info", summary="获取API信息", description="获取详细的API网关信息")
async def api_info(request: Request) -> Dict[str, Any]:
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
        "timestamp": time.time()
    }

# 包含管理路由（不带前缀，直接在根级别）
api_router.include_router(
    management_router,
    tags=["management"]
)

# 包含网关路由（用于代理请求）
api_router.include_router(
    gateway_router,
    prefix="/api/v1",
    tags=["gateway"]
)