"""
Health Check API Routes
"""

from fastapi import APIRouter, Depends
from datetime import datetime

from ...internal.service.dependencies import check_database_health, check_redis_health

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("", summary="服务健康检查")
async def health_check(
    db_healthy: bool = Depends(check_database_health),
    redis_healthy: bool = Depends(check_redis_health)
):
    """检查服务整体健康状态"""
    
    overall_healthy = db_healthy and redis_healthy
    
    health_status = {
        "service": "integration-service",
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": "数据库连接正常" if db_healthy else "数据库连接异常"
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy", 
                "message": "Redis连接正常" if redis_healthy else "Redis连接异常"
            }
        }
    }
    
    return health_status


@router.get("/ready", summary="服务就绪检查")
async def readiness_check(
    db_healthy: bool = Depends(check_database_health),
    redis_healthy: bool = Depends(check_redis_health)
):
    """检查服务是否就绪"""
    
    ready = db_healthy and redis_healthy
    
    return {
        "ready": ready,
        "timestamp": datetime.now().isoformat(),
        "message": "服务就绪" if ready else "服务未就绪"
    }


@router.get("/live", summary="服务存活检查")
async def liveness_check():
    """检查服务是否存活"""
    
    return {
        "alive": True,
        "timestamp": datetime.now().isoformat(),
        "message": "服务正常运行"
    } 