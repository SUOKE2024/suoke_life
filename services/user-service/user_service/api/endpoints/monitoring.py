"""
monitoring - 索克生活项目模块
"""

        from datetime import datetime
        import platform
        import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from user_service.auth import get_current_user, require_superuser
from user_service.cache import get_cache_manager
from user_service.database import get_db
from user_service.models.user import User
from user_service.monitoring import (
from user_service.performance import (

"""用户服务监控API端点"""


    get_metrics_collector,
    get_health_checker,
    metrics_endpoint,
    health_endpoint,
    readiness_endpoint,
    liveness_endpoint
)
    get_performance_monitor,
    get_query_optimizer,
    get_connection_pool_manager,
    get_memory_optimizer
)

router = APIRouter()


@router.get("/metrics")
async def get_prometheus_metrics():
    """获取Prometheus格式的指标"""
    return await metrics_endpoint()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return await health_endpoint()


@router.get("/ready")
async def readiness_check():
    """就绪检查端点"""
    return await readiness_endpoint()


@router.get("/live")
async def liveness_check():
    """存活检查端点"""
    return await liveness_endpoint()


@router.get("/performance/summary")
async def get_performance_summary(
    current_user: User = Depends(require_superuser)
):
    """获取性能摘要（管理员功能）"""
    try:
        monitor = get_performance_monitor()
        summary = monitor.get_performance_summary()
        
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取性能摘要失败: {str(e)}"
        )


@router.get("/performance/slow-queries")
async def get_slow_queries(
    limit: int = 20,
    current_user: User = Depends(require_superuser)
):
    """获取慢查询列表（管理员功能）"""
    try:
        monitor = get_performance_monitor()
        slow_queries = monitor.get_slow_queries(limit)
        
        return {
            "status": "success",
            "data": {
                "slow_queries": slow_queries,
                "total_count": len(slow_queries)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取慢查询失败: {str(e)}"
        )


@router.get("/performance/query-stats")
async def get_query_stats(
    limit: int = 20,
    current_user: User = Depends(require_superuser)
):
    """获取查询统计（管理员功能）"""
    try:
        optimizer = get_query_optimizer()
        stats = optimizer.get_query_stats(limit)
        
        return {
            "status": "success",
            "data": {
                "query_stats": stats,
                "total_count": len(stats)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取查询统计失败: {str(e)}"
        )


@router.get("/database/pool-status")
async def get_database_pool_status(
    current_user: User = Depends(require_superuser)
):
    """获取数据库连接池状态（管理员功能）"""
    try:
        pool_manager = get_connection_pool_manager()
        status_info = await pool_manager.get_pool_status()
        metrics = pool_manager.get_pool_metrics()
        
        return {
            "status": "success",
            "data": {
                "pool_status": status_info,
                "pool_metrics": metrics
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取连接池状态失败: {str(e)}"
        )


@router.get("/cache/status")
async def get_cache_status(
    current_user: User = Depends(require_superuser)
):
    """获取缓存状态（管理员功能）"""
    try:
        cache_manager = get_cache_manager()
        status_info = await cache_manager.get_cache_status()
        stats = cache_manager.get_cache_stats()
        
        return {
            "status": "success",
            "data": {
                "cache_status": status_info,
                "cache_stats": stats
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取缓存状态失败: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    current_user: User = Depends(require_superuser)
):
    """清理缓存（管理员功能）"""
    try:
        cache_manager = get_cache_manager()
        
        if pattern:
            cleared_count = await cache_manager.clear_pattern(pattern)
            message = f"已清理匹配模式 '{pattern}' 的 {cleared_count} 个缓存项"
        else:
            await cache_manager.clear_all()
            message = "已清理所有缓存"
        
        return {
            "status": "success",
            "message": message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清理缓存失败: {str(e)}"
        )


@router.get("/memory/stats")
async def get_memory_stats(
    current_user: User = Depends(require_superuser)
):
    """获取内存统计（管理员功能）"""
    try:
        memory_optimizer = get_memory_optimizer()
        stats = memory_optimizer.get_memory_stats()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取内存统计失败: {str(e)}"
        )


@router.post("/memory/optimize")
async def optimize_memory(
    current_user: User = Depends(require_superuser)
):
    """优化内存使用（管理员功能）"""
    try:
        memory_optimizer = get_memory_optimizer()
        memory_optimizer.optimize_memory_usage()
        
        return {
            "status": "success",
            "message": "内存优化完成"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内存优化失败: {str(e)}"
        )


@router.get("/system/info")
async def get_system_info(
    current_user: User = Depends(require_superuser)
):
    """获取系统信息（管理员功能）"""
    try:
        
        # 获取系统基本信息
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            },
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "current_time": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "data": system_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统信息失败: {str(e)}"
        )


@router.get("/logs/recent")
async def get_recent_logs(
    level: str = "INFO",
    limit: int = 100,
    current_user: User = Depends(require_superuser)
):
    """获取最近的日志（管理员功能）"""
    try:
        # 这里应该实现从日志系统获取最近日志的逻辑
        # 由于我们使用structlog，可能需要配置日志收集器
        
        # 模拟日志数据
        logs = [
            {
                "timestamp": "2024-01-01T12:00:00Z",
                "level": "INFO",
                "message": "User service started successfully",
                "module": "main"
            },
            {
                "timestamp": "2024-01-01T12:01:00Z",
                "level": "INFO",
                "message": "Database connection established",
                "module": "database"
            }
        ]
        
        return {
            "status": "success",
            "data": {
                "logs": logs,
                "total_count": len(logs),
                "level_filter": level,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取日志失败: {str(e)}"
        )


@router.get("/alerts")
async def get_system_alerts(
    current_user: User = Depends(require_superuser)
):
    """获取系统告警（管理员功能）"""
    try:
        alerts = []
        
        # 检查性能指标
        monitor = get_performance_monitor()
        summary = monitor.get_performance_summary()
        
        if isinstance(summary, dict) and "performance_score" in summary:
            if summary["performance_score"] < 60:
                alerts.append({
                    "type": "performance",
                    "level": "warning",
                    "message": f"系统性能评分较低: {summary['performance_score']:.1f}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # 检查内存使用
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 90:
            alerts.append({
                "type": "memory",
                "level": "critical",
                "message": f"内存使用率过高: {memory_percent:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        elif memory_percent > 80:
            alerts.append({
                "type": "memory",
                "level": "warning",
                "message": f"内存使用率较高: {memory_percent:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # 检查磁盘使用
        disk_percent = psutil.disk_usage('/').percent
        if disk_percent > 90:
            alerts.append({
                "type": "disk",
                "level": "critical",
                "message": f"磁盘使用率过高: {disk_percent:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        elif disk_percent > 80:
            alerts.append({
                "type": "disk",
                "level": "warning",
                "message": f"磁盘使用率较高: {disk_percent:.1f}%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "total_count": len(alerts),
                "critical_count": len([a for a in alerts if a["level"] == "critical"]),
                "warning_count": len([a for a in alerts if a["level"] == "warning"])
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统告警失败: {str(e)}"
        )


@router.get("/dashboard")
async def get_monitoring_dashboard(
    current_user: User = Depends(require_superuser)
):
    """获取监控仪表板数据（管理员功能）"""
    try:
        
        # 获取各种监控数据
        monitor = get_performance_monitor()
        performance_summary = monitor.get_performance_summary()
        
        pool_manager = get_connection_pool_manager()
        pool_status = await pool_manager.get_pool_status()
        
        cache_manager = get_cache_manager()
        cache_stats = cache_manager.get_cache_stats()
        
        memory_optimizer = get_memory_optimizer()
        memory_stats = memory_optimizer.get_memory_stats()
        
        # 获取系统资源使用情况
        system_resources = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        return {
            "status": "success",
            "data": {
                "timestamp": datetime.utcnow().isoformat(),
                "performance": performance_summary,
                "database": {
                    "pool_status": pool_status,
                    "connection_health": "healthy" if pool_status.get("status") == "healthy" else "warning"
                },
                "cache": {
                    "stats": cache_stats,
                    "health": "healthy"  # 简化的健康状态
                },
                "memory": memory_stats,
                "system_resources": system_resources,
                "service_status": {
                    "uptime": "running",  # 简化的运行时间
                    "version": "1.0.0",
                    "environment": "production"
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取监控仪表板失败: {str(e)}"
        ) 