"""
metrics - 索克生活项目模块
"""

        from ..core.config import get_settings
        import os
        import platform
        import psutil
        import sys
from ..core.logging import get_logger
from ..utils.health_check import get_health_checker
from ..utils.metrics import get_metrics_manager
from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import PlainTextResponse
from typing import Dict, Any

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标 API 端点

提供 Prometheus 指标导出和健康状态查询。
"""



logger = get_logger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics() -> str:
    """
    获取 Prometheus 格式的指标
    
    Returns:
        Prometheus 格式的指标数据
    """
    try:
        metrics_manager = get_metrics_manager()
        metrics_data = metrics_manager.get_metrics()
        
        return Response(
            content=metrics_data,
            media_type=metrics_manager.get_content_type(),
        )
    
    except Exception as e:
        logger.error("Failed to get Prometheus metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/health")
async def get_health_metrics() -> Dict[str, Any]:
    """
    获取健康指标摘要
    
    Returns:
        健康指标摘要
    """
    try:
        metrics_manager = get_metrics_manager()
        health_metrics = metrics_manager.get_health_metrics()
        
        return {
            "status": "healthy",
            "timestamp": health_metrics.get("timestamp"),
            "metrics": health_metrics,
        }
    
    except Exception as e:
        logger.error("Failed to get health metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get health metrics")


@router.get("/stats")
async def get_detailed_stats() -> Dict[str, Any]:
    """
    获取详细统计信息
    
    Returns:
        详细的统计信息
    """
    try:
        metrics_manager = get_metrics_manager()
        collector = metrics_manager.collector
        
        # 获取缓存统计
        cache_stats = collector.get_cache_stats()
        
        # 获取系统信息
        uptime = metrics_manager.get_uptime()
        
        return {
            "uptime_seconds": uptime,
            "cache": cache_stats,
            "requests": {
                "total": collector.request_total._value.sum() if hasattr(collector.request_total, '_value') else 0,
            },
            "connections": {
                "active": collector.active_connections._value.get() if hasattr(collector.active_connections, '_value') else 0,
            },
        }
    
    except Exception as e:
        logger.error("Failed to get detailed stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get stats")


@router.get("/response-times/{endpoint:path}")
async def get_response_time_percentiles(endpoint: str) -> Dict[str, float]:
    """
    获取指定端点的响应时间百分位数
    
    Args:
        endpoint: API 端点路径
        
    Returns:
        响应时间百分位数
    """
    try:
        metrics_manager = get_metrics_manager()
        collector = metrics_manager.collector
        
        percentiles = collector.get_response_time_percentiles(endpoint)
        
        if not percentiles:
            raise HTTPException(status_code=404, detail="No data found for endpoint")
        
        return percentiles
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get response time percentiles", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get response time data")


@router.post("/reset")
async def reset_metrics() -> Dict[str, str]:
    """
    重置指标统计
    
    Returns:
        重置结果
    """
    try:
        metrics_manager = get_metrics_manager()
        collector = metrics_manager.collector
        
        collector.reset_stats()
        
        logger.info("Metrics reset successfully")
        
        return {"message": "Metrics reset successfully"}
    
    except Exception as e:
        logger.error("Failed to reset metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to reset metrics")


@router.get("/health-check")
async def get_health_check() -> Dict[str, Any]:
    """
    获取详细的健康检查结果
    
    Returns:
        健康检查结果
    """
    try:
        health_checker = get_health_checker()
        health_result = await health_checker.check_all()
        
        return {
            "status": "healthy" if health_result.is_healthy else "unhealthy",
            "timestamp": health_result.timestamp,
            "checks": {
                check.name: {
                    "status": "healthy" if check.is_healthy else "unhealthy",
                    "message": check.message,
                    "details": check.details,
                    "duration": check.duration,
                }
                for check in health_result.checks
            },
            "overall": {
                "healthy_count": len([c for c in health_result.checks if c.is_healthy]),
                "total_count": len(health_result.checks),
                "duration": health_result.duration,
            }
        }
    
    except Exception as e:
        logger.error("Failed to get health check", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get health check")


@router.get("/system-info")
async def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        系统信息
    """
    try:
        
        # 获取系统基本信息
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "python": {
                "version": sys.version,
                "executable": sys.executable,
                "platform": sys.platform,
            },
            "process": {
                "pid": os.getpid(),
                "cwd": os.getcwd(),
            }
        }
        
        # 获取资源使用情况
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            system_info["resources"] = {
                "cpu_percent": process.cpu_percent(),
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": process.memory_percent(),
                },
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections()),
            }
            
            # 系统资源
            system_info["system_resources"] = {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent,
                },
            }
            
        except Exception as e:
            logger.warning("Failed to get resource info", error=str(e))
            system_info["resources"] = {"error": "Failed to get resource info"}
        
        return system_info
    
    except Exception as e:
        logger.error("Failed to get system info", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get system info")


@router.get("/config")
async def get_config_info() -> Dict[str, Any]:
    """
    获取配置信息（脱敏）
    
    Returns:
        配置信息
    """
    try:
        
        settings = get_settings()
        
        # 创建脱敏的配置信息
        config_info = {
            "server": {
                "host": settings.server.host,
                "port": settings.server.port,
                "environment": settings.environment,
                "debug": settings.debug,
            },
            "redis": {
                "host": settings.redis.host,
                "port": settings.redis.port,
                "db": settings.redis.db,
                "max_connections": settings.redis.max_connections,
            },
            "logging": {
                "level": settings.logging.level,
                "format": settings.logging.format,
            },
            "security": {
                "cors_enabled": bool(settings.security.cors_origins),
                "jwt_algorithm": settings.security.jwt_algorithm,
            },
        }
        
        return config_info
    
    except Exception as e:
        logger.error("Failed to get config info", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get config info") 