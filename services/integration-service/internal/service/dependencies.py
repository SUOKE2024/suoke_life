"""
Dependency Injection for FastAPI
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .integration_service import IntegrationService
from .database import db_service
from .redis_client import redis_service
from .logging_config import get_logger

# 安全相关
security = HTTPBearer()
logger = get_logger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """获取当前用户ID"""
    try:
        # 这里应该验证JWT token并提取用户ID
        # 暂时使用模拟实现
        token = credentials.credentials
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供访问令牌"
            )
        
        # 模拟用户ID提取
        if token == "mock_token":
            return "user_001"
        
        # 这里应该解析JWT token
        # user_id = jwt.decode(token, secret_key, algorithms=["HS256"])["user_id"]
        
        # 暂时返回模拟用户ID
        return "user_001"
        
    except Exception as e:
        logger.error("用户认证失败", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """获取可选的当前用户ID"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def get_integration_service() -> IntegrationService:
    """获取集成服务实例"""
    return IntegrationService()


async def get_database_service():
    """获取数据库服务"""
    return db_service


async def get_redis_service():
    """获取Redis服务"""
    return redis_service


# 健康检查依赖
async def check_database_health():
    """检查数据库健康状态"""
    try:
        return await db_service.health_check()
    except Exception as e:
        logger.error("数据库健康检查失败", error=str(e))
        return False


async def check_redis_health():
    """检查Redis健康状态"""
    try:
        return await redis_service.health_check()
    except Exception as e:
        logger.error("Redis健康检查失败", error=str(e))
        return False


# 权限检查依赖
async def require_admin_user(user_id: str = Depends(get_current_user)) -> str:
    """要求管理员用户"""
    # 这里应该检查用户是否为管理员
    # 暂时允许所有用户
    return user_id


async def require_platform_access(
    platform: str,
    user_id: str = Depends(get_current_user)
) -> str:
    """要求平台访问权限"""
    # 这里应该检查用户是否有访问特定平台的权限
    # 暂时允许所有用户访问所有平台
    return user_id


# 限流依赖
class RateLimiter:
    """简单的内存限流器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    async def check_rate_limit(self, user_id: str) -> bool:
        """检查用户是否超过限流"""
        import time
        
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # 清理过期记录
        if user_id in self.requests:
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > window_start
            ]
        else:
            self.requests[user_id] = []
        
        # 检查是否超限
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        
        # 记录当前请求
        self.requests[user_id].append(current_time)
        return True


# 全局限流器实例
rate_limiter = RateLimiter()


async def check_rate_limit(user_id: str = Depends(get_current_user)):
    """检查用户请求限流"""
    if not await rate_limiter.check_rate_limit(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试"
        )
    return user_id


# 验证依赖
async def validate_integration_access(
    integration_id: int,
    user_id: str = Depends(get_current_user)
) -> tuple[int, str]:
    """验证用户对集成的访问权限"""
    # 这里可以添加额外的权限检查逻辑
    return integration_id, user_id


async def validate_platform_enabled(platform: str) -> str:
    """验证平台是否启用"""
    from .config import get_settings
    
    settings = get_settings()
    platform_config = settings.get_platform_config(platform)
    
    if not platform_config.get("enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"平台 {platform} 未启用"
        )
    
    return platform 