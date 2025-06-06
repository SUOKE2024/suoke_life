"""
router - 索克生活项目模块
"""

from auth_service.api.rest.endpoints import auth, users, security
from fastapi import APIRouter

"""认证服务REST API路由器"""



# 创建API路由器
api_router = APIRouter()

# 根路径端点
@api_router.get("/")
async async def api_info(
    """API信息端点"""
    return {"message": "auth-service is running", "version": "1.0.0"}

# 健康检查路由
@api_router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "auth-service"}

# 包含各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(security.router, prefix="/security", tags=["安全"]) 