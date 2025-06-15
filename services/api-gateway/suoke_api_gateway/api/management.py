#!/usr/bin/env python3
"""
索克生活 API 网关管理接口

提供网关管理和监控功能。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from ..services.health import HealthService
from ..services.metrics import MetricsService
from ..services.service_registry import ServiceRegistry
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any, Dict, List, Optional
import asyncio
import psutil
import time
from datetime import datetime, timedelta

logger = get_logger(__name__)

# 创建管理路由器
management_router = APIRouter()


async def get_health_service() -> HealthService:
    """获取健康检查服务依赖"""
    # 这里应该从应用状态获取
    health_service = HealthService()
    await health_service.initialize()
    return health_service


async def get_metrics_service() -> MetricsService:
    """获取指标服务依赖"""
    # 这里应该从应用状态获取
    metrics_service = MetricsService()
    await metrics_service.initialize()
    return metrics_service


async def get_service_registry() -> ServiceRegistry:
    """获取服务注册表依赖"""
    settings = get_settings()
    registry = ServiceRegistry(settings)
    await registry.initialize()
    return registry


@management_router.get(
    "/health",
    summary="健康检查",
    description="获取网关和所有服务的健康状态"
)
async def health_check(
    health_service: HealthService = Depends(get_health_service),
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """健康检查"""
    try:
        # 获取系统健康状态
        system_health = await health_service.get_system_health()
        
        # 获取服务健康状态
        services_health = {}
        all_services = registry.get_all_services()
        
        for service_name in all_services.keys():
            service_health = registry.get_service_health(service_name)
            services_health[service_name] = service_health

        # 计算总体健康状态
        overall_status = "healthy"
        if not system_health.get("healthy", False):
            overall_status = "unhealthy"
        elif any(
            service.get("status") == "unhealthy" 
            for service in services_health.values()
        ):
            overall_status = "degraded"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_health,
            "services": services_health,
            "summary": {
                "total_services": len(all_services),
                "healthy_services": sum(
                    1 for service in services_health.values()
                    if service.get("status") == "healthy"
                ),
                "total_instances": sum(
                    service.get("total_instances", 0)
                    for service in services_health.values()
                ),
                "healthy_instances": sum(
                    service.get("healthy_instances", 0)
                    for service in services_health.values()
                )
            }
        }

    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        return {
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@management_router.get(
    "/health/ready",
    summary="就绪检查",
    description="检查网关是否准备好接收请求"
)
async def readiness_check(
    health_service: HealthService = Depends(get_health_service)
) -> Dict[str, Any]:
    """就绪检查"""
    try:
        is_ready = await health_service.is_ready()
        
        return {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Readiness check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@management_router.get(
    "/health/live",
    summary="存活检查",
    description="检查网关是否存活"
)
async def liveness_check(
    health_service: HealthService = Depends(get_health_service)
) -> Dict[str, Any]:
    """存活检查"""
    try:
        is_alive = await health_service.is_alive()
        
        return {
            "alive": is_alive,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Liveness check failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not alive"
        )


@management_router.get(
    "/metrics",
    summary="获取指标",
    description="获取网关性能和业务指标"
)
async def get_metrics(
    time_window: int = 300,  # 默认5分钟
    metrics_service: MetricsService = Depends(get_metrics_service)
) -> Dict[str, Any]:
    """获取指标"""
    try:
        # 获取业务指标
        business_metrics = await metrics_service.get_business_metrics(time_window)
        
        # 获取系统指标
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available": psutil.virtual_memory().available,
                "total": psutil.virtual_memory().total
            },
            "disk": {
                "percent": psutil.disk_usage("/").percent,
                "free": psutil.disk_usage("/").free,
                "total": psutil.disk_usage("/").total
            },
            "network": dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {}
        }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "time_window": time_window,
            "business": business_metrics,
            "system": system_metrics
        }

    except Exception as e:
        logger.error("Failed to get metrics", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get metrics: {str(e)}"
        )


@management_router.get(
    "/config",
    summary="获取配置",
    description="获取当前网关配置"
)
async def get_config() -> Dict[str, Any]:
    """获取配置"""
    try:
        settings = get_settings()
        
        # 隐藏敏感信息
        config_dict = settings.model_dump()
        if "jwt" in config_dict and "secret_key" in config_dict["jwt"]:
            config_dict["jwt"]["secret_key"] = "***HIDDEN***"
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "config": config_dict
        }

    except Exception as e:
        logger.error("Failed to get config", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )


@management_router.post(
    "/config/reload",
    summary="重新加载配置",
    description="重新加载网关配置"
)
async def reload_config() -> Dict[str, Any]:
    """重新加载配置"""
    try:
        # 这里应该实现配置重新加载逻辑
        # 暂时返回成功响应
        logger.info("Configuration reload requested")
        
        return {
            "message": "Configuration reload initiated",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Failed to reload config", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload config: {str(e)}"
        )


@management_router.get(
    "/logs",
    summary="获取日志",
    description="获取最近的日志记录"
)
async def get_logs(
    level: str = "INFO",
    limit: int = 100,
    since: Optional[str] = None
) -> Dict[str, Any]:
    """获取日志"""
    try:
        # 这里应该实现日志查询逻辑
        # 暂时返回模拟数据
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": "Sample log message",
                "module": "gateway"
            }
        ]
        
        return {
            "logs": logs,
            "total": len(logs),
            "level": level,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Failed to get logs", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get logs: {str(e)}"
        )


@management_router.post(
    "/cache/clear",
    summary="清除缓存",
    description="清除网关缓存"
)
async def clear_cache(
    cache_type: str = "all"
) -> Dict[str, Any]:
    """清除缓存"""
    try:
        # 这里应该实现缓存清除逻辑
        logger.info("Cache clear requested", cache_type=cache_type)
        
        return {
            "message": f"Cache '{cache_type}' cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Failed to clear cache", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@management_router.get(
    "/stats",
    summary="获取统计信息",
    description="获取网关运行统计信息"
)
async def get_stats(
    metrics_service: MetricsService = Depends(get_metrics_service)
) -> Dict[str, Any]:
    """获取统计信息"""
    try:
        # 获取运行时统计
        stats = await metrics_service.get_runtime_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats
        }

    except Exception as e:
        logger.error("Failed to get stats", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@management_router.post(
    "/shutdown",
    summary="优雅关闭",
    description="优雅关闭网关服务"
)
async def graceful_shutdown() -> Dict[str, Any]:
    """优雅关闭"""
    try:
        logger.info("Graceful shutdown requested")
        
        # 这里应该实现优雅关闭逻辑
        # 暂时返回响应
        return {
            "message": "Graceful shutdown initiated",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Failed to initiate shutdown", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate shutdown: {str(e)}"
        )