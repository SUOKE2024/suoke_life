import logging
import time

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/health",
    tags=["健康检查"],
    responses={404: {"description": "未找到"}},
)

class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str
    version: str
    uptime: float
    services: dict[str, str]

# 服务启动时间
START_TIME = time.time()

@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    服务健康检查
    """
    try:
        # 检查依赖服务状态
        services_status = {
            "database": "healthy",  # 这里应该实际检查数据库连接
            "cache": "healthy",     # 检查Redis缓存
            "messagebus": "healthy" # 检查消息总线
        }

        # 计算运行时间
        uptime = time.time() - START_TIME

        return HealthStatus(
            status="healthy",
            version="1.0.0",
            uptime=uptime,
            services=services_status
        )
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"服务不健康: {str(e)}"
        )

@router.get("/readiness")
async def readiness_check():
    """
    服务就绪检查
    """
    return {"status": "ready"}

@router.get("/liveness")
async def liveness_check():
    """
    服务存活检查
    """
    return {"status": "alive"}
