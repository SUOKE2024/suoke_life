"""认证服务REST API路由器"""

from fastapi import APIRouter

# 创建API路由器
api_router = APIRouter()

# 健康检查路由
@api_router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "auth-service"}

# 认证相关路由组
auth_router = APIRouter(prefix="/auth", tags=["认证"])
user_router = APIRouter(prefix="/users", tags=["用户"])
security_router = APIRouter(prefix="/security", tags=["安全"])

# 将子路由添加到主路由器
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(security_router)

# TODO: 实现具体的认证、用户和安全端点 