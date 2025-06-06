"""
deps - 索克生活项目模块
"""

        import time
from app.core.container import get_container
from app.core.logger import get_logger
from app.services.cache_service import CacheService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.knowledge_service import KnowledgeService
from app.services.performance_service import PerformanceService
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

"""
依赖注入模块
提供FastAPI路由的依赖注入
"""



logger = get_logger()
security = HTTPBearer(auto_error=False)


async def get_knowledge_service() -> KnowledgeService:
    """获取知识服务实例"""
    try:
        container = get_container()
        return container.knowledge_service
    except Exception as e:
        logger.error(f"获取知识服务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="知识服务不可用"
        )


async def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    try:
        container = get_container()
        return container.cache_service
    except Exception as e:
        logger.error(f"获取缓存服务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="缓存服务不可用"
        )


async def get_performance_service() -> PerformanceService:
    """获取性能服务实例"""
    try:
        container = get_container()
        return container.performance_service
    except Exception as e:
        logger.error(f"获取性能服务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="性能服务不可用"
        )


async def get_knowledge_graph_service() -> KnowledgeGraphService:
    """获取知识图谱服务实例"""
    try:
        container = get_container()
        return container.knowledge_graph_service
    except Exception as e:
        logger.error(f"获取知识图谱服务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="知识图谱服务不可用"
        )


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """验证API密钥"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要API密钥认证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 这里应该实现实际的API密钥验证逻辑
    # 目前为演示目的,简单检查是否存在token
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


async def get_current_user(api_key: str = Depends(verify_api_key)) -> dict:
    """获取当前用户信息"""
    # 这里应该根据API密钥获取用户信息
    # 目前为演示目的,返回模拟用户
    return {"user_id": "demo_user", "username": "demo", "permissions": ["read", "write"]}


def require_permission(permission: str):
    """权限检查装饰器"""

    async def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_permissions = current_user.get("permissions", [])
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"需要权限: {permission}"
            )
        return current_user

    return permission_checker


# 可选的认证依赖(不强制要求认证)
async def optional_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """可选认证,不强制要求"""
    if not credentials or not credentials.credentials:
        return {"user_id": "anonymous", "permissions": ["read"]}

    try:
        return await get_current_user(credentials.credentials)
    except HTTPException:
        return {"user_id": "anonymous", "permissions": ["read"]}


# 限流依赖
class RateLimiter:
    """简单的限流器"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def __call__(self, request_id: str | None = None) -> bool:
        """检查是否超过限流"""

        current_time = time.time()
        window_start = current_time - self.window_seconds

        # 清理过期记录
        self.requests = {
            req_id: timestamps
            for req_id, timestamps in self.requests.items()
            if any(t > window_start for t in timestamps)
        }

        # 检查当前请求
        if request_id not in self.requests:
            self.requests[request_id] = []

        # 过滤当前窗口内的请求
        self.requests[request_id] = [t for t in self.requests[request_id] if t > window_start]

        # 检查是否超过限制
        if len(self.requests[request_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="请求频率过高,请稍后再试"
            )

        # 记录当前请求
        self.requests[request_id].append(current_time)
        return True


# 创建限流器实例
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


async def check_rate_limit(
    request_id: str = "default", limiter: RateLimiter = Depends(lambda: rate_limiter)
) -> bool:
    """检查限流"""
    return await limiter(request_id)


# 健康检查依赖
async def health_check_dependency() -> bool:
    """健康检查依赖,确保服务健康"""
    try:
        container = get_container()

        # 检查关键服务是否可用
        if not container.knowledge_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="知识服务不可用"
            )

        return True

    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="服务不健康")


# 数据库连接依赖
async def get_database_session():
    """获取数据库会话"""
    try:
        container = get_container()
        repository = container.neo4j_repository

        # 这里可以实现数据库会话管理
        yield repository

    except Exception as e:
        logger.error(f"获取数据库会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="数据库连接失败"
        )


# 缓存会话依赖
async def get_cache_session():
    """获取缓存会话"""
    try:
        container = get_container()
        cache_service = container.cache_service

        yield cache_service

    except Exception as e:
        logger.error(f"获取缓存会话失败: {e}")
        # 缓存失败不应该阻止请求,只记录日志
        yield None


# 监控依赖
async def get_metrics_service():
    """获取监控服务"""
    try:
        container = get_container()
        return container.metrics_service
    except Exception as e:
        logger.error(f"获取监控服务失败: {e}")
        # 监控服务失败不应该阻止请求
        return None


# 配置依赖
async def get_config():
    """获取配置"""
    try:
        container = get_container()
        return container.config
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="配置加载失败"
        )


# 日志依赖
async def get_request_logger():
    """获取请求日志器"""
    return get_logger("request")


# 验证请求大小的依赖
def validate_request_size(max_size: int = 1024 * 1024):  # 1MB
    """验证请求大小"""

    async def size_validator(request) -> bool:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"请求体过大,最大允许 {max_size} 字节",
            )
        return True

    return size_validator


# 内容类型验证依赖
def validate_content_type(allowed_types: list | None = None):
    """验证内容类型"""
    if allowed_types is None:
        allowed_types = ["application/json"]

    async def content_type_validator(request) -> bool:
        content_type = request.headers.get("content-type", "").split(";")[0]
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"不支持的内容类型: {content_type}",
            )
        return True

    return content_type_validator
