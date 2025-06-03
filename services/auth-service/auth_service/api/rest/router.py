"""认证服务REST API路由器"""

from fastapi import APIRouter

from auth_service.api.rest.endpoints import auth, users, security

# 创建API路由器
api_router = APIRouter()

# 健康检查路由
@api_router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "auth-service"}

# 包含各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(security.router, prefix="/security", tags=["安全"]) 