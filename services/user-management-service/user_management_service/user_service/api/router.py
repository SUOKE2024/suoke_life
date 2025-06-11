
"""
router - 索克生活项目模块
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from user_service.api.endpoints import analytics, health, monitoring, users
from user_service.auth import get_current_user

"""用户服务主API路由器"""



# 创建主API路由器
api_router = APIRouter()

# 健康检查端点
@api_router.get(" / health")
async def health_check() -> None:
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "user - service",
        "version": "1.0.0",
        "timestamp": "2024 - 01 - 01T00:00:00Z"
    }

# 服务信息端点
@api_router.get(" / info")
async def service_info() -> None:
    """服务信息端点"""
    return {
        "name": "索克生活用户服务",
        "description": "提供用户认证、授权和用户数据管理功能",
        "version": "1.0.0",
        "features": [
            "用户管理",
            "设备绑定",
            "健康数据管理",
            "用户分析",
            "性能监控"
        ],
        "endpoints": {
            "users": " / api / v1 / users",
            "health": " / api / v1 / health",
            "analytics": " / api / v1 / analytics",
            "monitoring": " / api / v1 / monitoring"
        }
    }

# 认证状态检查端点
@api_router.get(" / auth / status")
async def auth_status(current_user: dict = Depends(get_current_user)):
    """检查认证状态"""
    return {
        "authenticated": True,
        "user_id": current_user.get("id"),
        "username": current_user.get("username"),
        "is_verified": current_user.get("is_verified", False),
        "is_superuser": current_user.get("is_superuser", False)
    }

# 包含各个模块的路由
api_router.include_router(
    users.router,
    prefix = " / users",
    tags = ["用户管理"]
)

api_router.include_router(
    health.router,
    prefix = " / health",
    tags = ["健康数据"]
)

api_router.include_router(
    analytics.router,
    prefix = " / analytics",
    tags = ["用户分析"]
)

api_router.include_router(
    monitoring.router,
    prefix = " / monitoring",
    tags = ["性能监控"]
)

# 错误处理
@api_router.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code = exc.status_code,
        content = {
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            },
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": "2024 - 01 - 01T00:00:00Z"
        }
    )

@api_router.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content = {
            "error": {
                "code": 500,
                "message": "内部服务器错误",
                "type": "InternalServerError",
                "details": str(exc) if hasattr(exc, '__str__') else "未知错误"
            },
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": "2024 - 01 - 01T00:00:00Z"
        }
    )