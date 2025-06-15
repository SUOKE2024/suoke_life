"""
健康检查路由处理器

提供服务健康状态和指标接口。
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from ...service.metrics_service import get_metrics_service, MetricsService
from ...config.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", summary="基础健康检查")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0"
    }


@router.get("/live", summary="存活检查")
async def liveness_check():
    """Kubernetes存活检查"""
    return {"status": "alive"}


@router.get("/ready", summary="就绪检查")
async def readiness_check(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Kubernetes就绪检查"""
    try:
        health_status = await metrics_service.get_health_status()
        
        if health_status["status"] in ["healthy", "warning"]:
            return {
                "status": "ready",
                "checks": health_status["checks"]
            }
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "not ready",
                    "checks": health_status["checks"]
                }
            )
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not ready",
                "error": str(e)
            }
        )


@router.get("/detailed", summary="详细健康检查")
async def detailed_health_check(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """详细健康检查"""
    try:
        health_status = await metrics_service.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"详细健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": health_status.get("timestamp")
            }
        )


@router.get("/stats", summary="服务统计")
async def service_stats(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """获取服务统计信息"""
    try:
        stats = await metrics_service.get_service_stats()
        return stats
    except Exception as e:
        logger.error(f"获取服务统计失败: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "获取统计信息失败",
                "message": str(e)
            }
        )


@router.get("/metrics", summary="Prometheus指标")
async def prometheus_metrics():
    """Prometheus指标端点（如果启用了指标收集）"""
    settings = get_settings()
    
    if not settings.enable_metrics:
        raise HTTPException(
            status_code=404,
            detail="指标收集未启用"
        )
    
    # 这个端点通常由prometheus_fastapi_instrumentator自动处理
    # 这里只是提供一个备用端点
    return {"message": "请访问 /metrics 获取Prometheus指标"}


@router.get("/version", summary="版本信息")
async def version_info():
    """获取版本信息"""
    settings = get_settings()
    
    return {
        "service": "auth-service",
        "version": "1.0.0",
        "environment": settings.environment,
        "python_version": "3.13+",
        "framework": "FastAPI"
    } 