"""
性能监控API

提供系统性能监控和健康检查的API端点。
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging
import time
from datetime import datetime

from internal.database.connection_manager import get_connection_manager
from internal.database.query_optimizer import get_query_optimizer
from internal.cache.redis_cache import get_redis_cache
from internal.async_tasks.task_manager import get_task_manager
from internal.middleware.rate_limiter import get_rate_limiter
from internal.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 创建路由器
router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health", summary="系统健康检查")
async def health_check() -> Dict[str, Any]:
    """
    系统健康检查
    
    Returns:
        Dict[str, Any]: 健康状态信息
    """
    try:
        # 检查各个组件的健康状态
        db_manager = get_connection_manager()
        cache = get_redis_cache()
        task_manager = get_task_manager()
        
        # 数据库健康检查
        db_health = await db_manager.health_check()
        
        # 缓存健康检查
        cache_health = await cache.health_check()
        
        # 任务管理器状态
        task_stats = task_manager.get_stats()
        
        # 整体健康状态
        overall_status = "healthy"
        if (db_health.get("status") != "healthy" or 
            cache_health.get("status") != "healthy"):
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": db_health.get("timestamp"),
            "components": {
                "database": {
                    "status": db_health.get("status", "unknown"),
                    "response_time_ms": db_health.get("response_time_ms", 0),
                    "active_connections": db_health.get("active_connections", 0)
                },
                "cache": {
                    "status": cache_health.get("status", "unknown"),
                    "response_time_ms": cache_health.get("response_time_ms", 0),
                    "hit_rate": cache_health.get("hit_rate", 0)
                },
                "task_manager": {
                    "status": "healthy" if task_stats.get("is_initialized") else "unhealthy",
                    "total_queues": task_stats.get("total_queues", 0),
                    "total_tasks": sum(
                        queue_stats.get("total_tasks", 0) 
                        for queue_stats in task_stats.get("queues", {}).values()
                    )
                }
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": None
        }


@router.get("/database", summary="数据库性能监控")
async def database_metrics() -> Dict[str, Any]:
    """
    获取数据库性能指标
    
    Returns:
        Dict[str, Any]: 数据库性能指标
    """
    try:
        db_manager = get_connection_manager()
        query_optimizer = get_query_optimizer()
        
        # 连接池指标
        pool_metrics = await db_manager.get_pool_metrics()
        
        # 查询性能报告
        performance_report = query_optimizer.get_performance_report()
        
        # 表统计信息
        table_stats = await query_optimizer.get_table_statistics()
        
        # 索引使用统计
        index_stats = await query_optimizer.get_index_usage_stats()
        
        return {
            "connection_pool": pool_metrics,
            "query_performance": performance_report,
            "table_statistics": table_stats,
            "index_usage": index_stats[:10]  # 只返回前10个索引
        }
        
    except Exception as e:
        logger.error(f"获取数据库指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取数据库指标失败")


@router.get("/cache", summary="缓存性能监控")
async def cache_metrics() -> Dict[str, Any]:
    """
    获取缓存性能指标
    
    Returns:
        Dict[str, Any]: 缓存性能指标
    """
    try:
        cache = get_redis_cache()
        
        # 缓存统计信息
        cache_stats = cache.get_stats()
        
        # 缓存健康检查
        cache_health = await cache.health_check()
        
        return {
            "statistics": cache_stats,
            "health": cache_health
        }
        
    except Exception as e:
        logger.error(f"获取缓存指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取缓存指标失败")


@router.get("/tasks", summary="任务队列监控")
async def task_metrics() -> Dict[str, Any]:
    """
    获取任务队列性能指标
    
    Returns:
        Dict[str, Any]: 任务队列指标
    """
    try:
        task_manager = get_task_manager()
        
        # 任务管理器统计信息
        task_stats = task_manager.get_stats()
        
        return task_stats
        
    except Exception as e:
        logger.error(f"获取任务队列指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取任务队列指标失败")


@router.get("/rate-limits", summary="速率限制监控")
async def rate_limit_metrics() -> Dict[str, Any]:
    """
    获取速率限制指标
    
    Returns:
        Dict[str, Any]: 速率限制指标
    """
    try:
        rate_limiter = get_rate_limiter()
        
        # 速率限制统计信息
        stats = rate_limiter.get_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"获取速率限制指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取速率限制指标失败")


@router.post("/database/optimize", summary="数据库优化")
async def optimize_database(dry_run: bool = True) -> Dict[str, Any]:
    """
    执行数据库优化
    
    Args:
        dry_run: 是否为试运行模式
    
    Returns:
        Dict[str, Any]: 优化结果
    """
    try:
        query_optimizer = get_query_optimizer()
        
        # 创建推荐索引
        index_results = await query_optimizer.create_recommended_indexes(dry_run=dry_run)
        
        # 表维护建议
        maintenance_results = await query_optimizer.optimize_table_maintenance()
        
        return {
            "dry_run": dry_run,
            "index_optimization": index_results,
            "maintenance_recommendations": maintenance_results
        }
        
    except Exception as e:
        logger.error(f"数据库优化失败: {str(e)}")
        raise HTTPException(status_code=500, detail="数据库优化失败")


@router.post("/cache/clear", summary="清理缓存")
async def clear_cache(pattern: str = "*") -> Dict[str, Any]:
    """
    清理缓存
    
    Args:
        pattern: 缓存键模式
    
    Returns:
        Dict[str, Any]: 清理结果
    """
    try:
        cache = get_redis_cache()
        
        # 清理匹配的缓存
        cleared_count = await cache.clear_pattern(pattern)
        
        return {
            "pattern": pattern,
            "cleared_keys": cleared_count,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"清理缓存失败: {str(e)}")
        raise HTTPException(status_code=500, detail="清理缓存失败")


@router.get("/performance-summary", summary="性能总览")
async def performance_summary() -> Dict[str, Any]:
    """
    获取系统性能总览
    
    Returns:
        Dict[str, Any]: 性能总览
    """
    try:
        db_manager = get_connection_manager()
        cache = get_redis_cache()
        task_manager = get_task_manager()
        query_optimizer = get_query_optimizer()
        
        # 数据库指标
        db_health = await db_manager.health_check()
        pool_metrics = await db_manager.get_pool_metrics()
        
        # 缓存指标
        cache_stats = cache.get_stats()
        
        # 任务队列指标
        task_stats = task_manager.get_stats()
        
        # 查询性能
        query_performance = query_optimizer.get_performance_report()
        
        return {
            "summary": {
                "database": {
                    "status": db_health.get("status"),
                    "response_time_ms": db_health.get("response_time_ms"),
                    "pool_usage_rate": pool_metrics.get("usage_rate", 0),
                    "slow_queries": query_performance.get("slow_queries", 0)
                },
                "cache": {
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "total_operations": cache_stats.get("total_operations", 0),
                    "errors": cache_stats.get("errors", 0)
                },
                "tasks": {
                    "total_queues": task_stats.get("total_queues", 0),
                    "total_completed": sum(
                        queue_stats.get("completed_tasks", 0)
                        for queue_stats in task_stats.get("queues", {}).values()
                    ),
                    "total_failed": sum(
                        queue_stats.get("failed_tasks", 0)
                        for queue_stats in task_stats.get("queues", {}).values()
                    )
                }
            },
            "recommendations": self._generate_recommendations(
                db_health, pool_metrics, cache_stats, query_performance
            )
        }
        
    except Exception as e:
        logger.error(f"获取性能总览失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取性能总览失败")


def _generate_recommendations(
    db_health: Dict[str, Any],
    pool_metrics: Dict[str, Any], 
    cache_stats: Dict[str, Any],
    query_performance: Dict[str, Any]
) -> List[str]:
    """生成性能优化建议"""
    recommendations = []
    
    # 数据库建议
    if db_health.get("response_time_ms", 0) > 100:
        recommendations.append("数据库响应时间较慢，建议检查查询优化")
    
    if pool_metrics.get("usage_rate", 0) > 80:
        recommendations.append("数据库连接池使用率过高，建议增加连接数")
    
    # 缓存建议
    if cache_stats.get("hit_rate", 0) < 70:
        recommendations.append("缓存命中率较低，建议优化缓存策略")
    
    if cache_stats.get("errors", 0) > 0:
        recommendations.append("缓存出现错误，建议检查Redis连接")
    
    # 查询性能建议
    if query_performance.get("slow_query_ratio", 0) > 10:
        recommendations.append("慢查询比例过高，建议添加索引或优化查询")
    
    if not recommendations:
        recommendations.append("系统性能良好，无需特别优化")
    
    return recommendations


@router.get("/ha/status", summary="高可用状态")
async def get_ha_status() -> Dict[str, Any]:
    """获取高可用状态"""
    try:
        from internal.ha.failover_manager import get_failover_manager
        
        if not settings.ha_enabled:
            return {
                "status": "disabled",
                "message": "高可用功能未启用"
            }
        
        failover_manager = get_failover_manager()
        cluster_status = failover_manager.get_cluster_status()
        
        return {
            "status": "success",
            "data": cluster_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取高可用状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取高可用状态失败: {str(e)}")


@router.get("/service-discovery/status", summary="服务发现状态")
async def get_service_discovery_status() -> Dict[str, Any]:
    """获取服务发现状态"""
    try:
        from internal.discovery.service_registry import get_service_registry
        
        if not settings.service_discovery_enabled:
            return {
                "status": "disabled",
                "message": "服务发现功能未启用"
            }
        
        service_registry = get_service_registry()
        registry_stats = service_registry.get_registry_stats()
        
        return {
            "status": "success",
            "data": registry_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取服务发现状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取服务发现状态失败: {str(e)}")


@router.get("/grpc/status", summary="gRPC客户端状态")
async def get_grpc_status() -> Dict[str, Any]:
    """获取gRPC客户端状态"""
    try:
        from internal.grpc_client.client_manager import get_grpc_client_manager
        
        if not settings.grpc_enabled:
            return {
                "status": "disabled",
                "message": "gRPC功能未启用"
            }
        
        grpc_manager = get_grpc_client_manager()
        manager_stats = grpc_manager.get_manager_stats()
        
        return {
            "status": "success",
            "data": manager_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取gRPC状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取gRPC状态失败: {str(e)}")


@router.post("/performance/benchmark", summary="性能基准测试")
async def run_performance_benchmark() -> Dict[str, Any]:
    """运行性能基准测试"""
    try:
        from internal.testing.performance_test import benchmark_auth_service
        
        if not settings.performance_test_enabled:
            return {
                "status": "disabled",
                "message": "性能测试功能未启用，请在配置中启用 performance_test_enabled"
            }
        
        # 运行基准测试（异步执行，避免阻塞）
        import asyncio
        
        # 创建后台任务执行基准测试
        async def run_benchmark():
            return await benchmark_auth_service()
        
        # 启动基准测试任务
        task = asyncio.create_task(run_benchmark())
        
        return {
            "status": "started",
            "message": "性能基准测试已启动，请稍后查看结果",
            "test_id": f"benchmark_{int(time.time())}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"启动性能基准测试失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"启动性能基准测试失败: {str(e)}")


@router.get("/system/comprehensive", summary="系统综合状态")
async def get_comprehensive_status() -> Dict[str, Any]:
    """获取系统综合状态"""
    try:
        # 基础健康检查
        health_status = await health_check()
        
        # 数据库状态
        db_status = await database_metrics()
        
        # 缓存状态
        cache_status = await cache_metrics()
        
        # 任务管理器状态
        task_status = await task_metrics()
        
        # 高可用状态
        ha_status = None
        if settings.ha_enabled:
            try:
                ha_response = await get_ha_status()
                ha_status = ha_response.get("data")
            except Exception:
                ha_status = {"status": "error", "message": "无法获取高可用状态"}
        
        # 服务发现状态
        sd_status = None
        if settings.service_discovery_enabled:
            try:
                sd_response = await get_service_discovery_status()
                sd_status = sd_response.get("data")
            except Exception:
                sd_status = {"status": "error", "message": "无法获取服务发现状态"}
        
        # gRPC状态
        grpc_status = None
        if settings.grpc_enabled:
            try:
                grpc_response = await get_grpc_status()
                grpc_status = grpc_response.get("data")
            except Exception:
                grpc_status = {"status": "error", "message": "无法获取gRPC状态"}
        
        # 计算总体健康评分
        health_score = _calculate_overall_health_score({
            "health": health_status,
            "database": db_status,
            "cache": cache_status,
            "tasks": task_status,
            "ha": ha_status,
            "service_discovery": sd_status,
            "grpc": grpc_status
        })
        
        return {
            "status": "success",
            "overall_health_score": health_score,
            "health_grade": _get_health_grade(health_score),
            "components": {
                "basic_health": health_status,
                "database": db_status,
                "cache": cache_status,
                "task_manager": task_status,
                "high_availability": ha_status,
                "service_discovery": sd_status,
                "grpc_client": grpc_status
            },
            "configuration": {
                "ha_enabled": settings.ha_enabled,
                "service_discovery_enabled": settings.service_discovery_enabled,
                "grpc_enabled": settings.grpc_enabled,
                "performance_test_enabled": settings.performance_test_enabled,
                "redis_enabled": settings.redis_enabled,
                "task_manager_enabled": settings.task_manager_enabled
            },
            "optimization_level": "第4周: 高可用性与负载均衡优化",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取综合状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取综合状态失败: {str(e)}")


def _calculate_overall_health_score(components: dict) -> float:
    """计算总体健康评分"""
    try:
        scores = []
        weights = {
            "health": 0.2,
            "database": 0.25,
            "cache": 0.15,
            "tasks": 0.1,
            "ha": 0.1,
            "service_discovery": 0.1,
            "grpc": 0.1
        }
        
        for component, weight in weights.items():
            component_data = components.get(component)
            if component_data is None:
                continue
                
            if isinstance(component_data, dict):
                status = component_data.get("status", "unknown")
                if status == "healthy" or status == "success":
                    scores.append(100 * weight)
                elif status == "degraded" or status == "warning":
                    scores.append(70 * weight)
                elif status == "error" or status == "unhealthy":
                    scores.append(30 * weight)
                else:
                    scores.append(50 * weight)
            else:
                scores.append(50 * weight)
        
        return round(sum(scores), 2) if scores else 0.0
        
    except Exception:
        return 0.0


def _get_health_grade(score: float) -> str:
    """根据健康评分获取等级"""
    if score >= 95:
        return "A+ (优秀)"
    elif score >= 90:
        return "A (良好)"
    elif score >= 80:
        return "B (一般)"
    elif score >= 70:
        return "C (需要关注)"
    else:
        return "D (需要紧急处理)" 