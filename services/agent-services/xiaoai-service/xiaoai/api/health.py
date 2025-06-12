"""
健康检查API端点
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..monitoring.health_checker import get_health_checker
from ..monitoring.performance_monitor import get_performance_monitor

router = APIRouter(prefix="/health", tags=["健康检查"])
logger = logging.getLogger(__name__)


@router.get("/", summary="整体健康状态")
async def get_health():
    """
    获取服务整体健康状态

    Returns:
        Dict: 包含整体健康状态的字典
    """
    try:
        health_checker = await get_health_checker()
        health_status = await health_checker.get_health_status()

        return {"status": "success", "data": health_status}
    except Exception as e:
        logger.error(f"获取健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取健康状态失败: {e}")


@router.get("/components", summary="组件健康状态")
async def get_components_health():
    """
    获取所有组件的健康状态

    Returns:
        Dict: 包含所有组件健康状态的字典
    """
    try:
        health_checker = await get_health_checker()
        components = await health_checker.check_all_components()

        return {
            "status": "success",
            "data": {
                name: {
                    "name": health.name,
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "last_check": health.last_check.isoformat(),
                    "error_message": health.error_message,
                    "metadata": health.metadata,
                }
                for name, health in components.items()
            },
        }
    except Exception as e:
        logger.error(f"获取组件健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取组件健康状态失败: {e}")


@router.get("/components/{component_name}", summary="特定组件健康状态")
async def get_component_health(component_name: str):
    """
    获取特定组件的健康状态

    Args:
        component_name: 组件名称

    Returns:
        Dict: 包含组件健康状态的字典
    """
    try:
        health_checker = await get_health_checker()
        component_health = await health_checker.get_component_health(component_name)

        if component_health is None:
            raise HTTPException(status_code=404, detail=f"组件 {component_name} 未找到")

        return {
            "status": "success",
            "data": {
                "name": component_health.name,
                "status": component_health.status.value,
                "response_time": component_health.response_time,
                "last_check": component_health.last_check.isoformat(),
                "error_message": component_health.error_message,
                "metadata": component_health.metadata,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取组件 {component_name} 健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取组件健康状态失败: {e}")


@router.post("/check", summary="强制健康检查")
async def force_health_check(component_name: Optional[str] = None):
    """
    强制执行健康检查

    Args:
        component_name: 可选的组件名称，如果不提供则检查所有组件

    Returns:
        Dict: 检查结果
    """
    try:
        health_checker = await get_health_checker()
        results = await health_checker.force_check(component_name)

        return {
            "status": "success",
            "message": "健康检查完成",
            "data": {
                name: {
                    "name": health.name,
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "last_check": health.last_check.isoformat(),
                    "error_message": health.error_message,
                }
                for name, health in results.items()
            },
        }
    except Exception as e:
        logger.error(f"强制健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {e}")


@router.get("/metrics", summary="系统指标")
async def get_system_metrics(
    hours: int = Query(1, ge=1, le=24, description="指标时间范围（小时）")
):
    """
    获取系统指标

    Args:
        hours: 指标时间范围（小时）

    Returns:
        Dict: 系统指标数据
    """
    try:
        health_checker = await get_health_checker()
        metrics_history = await health_checker.get_metrics_history(hours)

        if not metrics_history:
            return {
                "status": "success",
                "data": {"message": "暂无指标数据", "time_range_hours": hours, "data_points": 0},
            }

        # 计算统计信息
        cpu_values = [m.cpu_usage for m in metrics_history]
        memory_values = [m.memory_usage for m in metrics_history]
        disk_values = [m.disk_usage for m in metrics_history]

        return {
            "status": "success",
            "data": {
                "time_range_hours": hours,
                "data_points": len(metrics_history),
                "cpu_usage": {
                    "current": cpu_values[-1] if cpu_values else 0,
                    "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "min": min(cpu_values) if cpu_values else 0,
                    "max": max(cpu_values) if cpu_values else 0,
                },
                "memory_usage": {
                    "current": memory_values[-1] if memory_values else 0,
                    "average": sum(memory_values) / len(memory_values) if memory_values else 0,
                    "min": min(memory_values) if memory_values else 0,
                    "max": max(memory_values) if memory_values else 0,
                },
                "disk_usage": {
                    "current": disk_values[-1] if disk_values else 0,
                    "average": sum(disk_values) / len(disk_values) if disk_values else 0,
                    "min": min(disk_values) if disk_values else 0,
                    "max": max(disk_values) if disk_values else 0,
                },
                "latest_metrics": (
                    {
                        "cpu_usage": metrics_history[-1].cpu_usage,
                        "memory_usage": metrics_history[-1].memory_usage,
                        "disk_usage": metrics_history[-1].disk_usage,
                        "network_io": metrics_history[-1].network_io,
                        "process_count": metrics_history[-1].process_count,
                        "uptime": metrics_history[-1].uptime,
                    }
                    if metrics_history
                    else None
                ),
            },
        }
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统指标失败: {e}")


@router.get("/performance", summary="性能统计")
async def get_performance_stats(
    hours: int = Query(1, ge=1, le=24, description="统计时间范围（小时）"),
    endpoint: Optional[str] = Query(None, description="特定端点"),
):
    """
    获取性能统计信息

    Args:
        hours: 统计时间范围（小时）
        endpoint: 可选的特定端点

    Returns:
        Dict: 性能统计数据
    """
    try:
        performance_monitor = await get_performance_monitor()

        # 获取响应时间统计
        response_time_stats = performance_monitor.get_response_time_stats(endpoint, hours)

        # 获取错误率
        error_rate = performance_monitor.get_error_rate(endpoint, hours)

        # 获取吞吐量
        throughput = performance_monitor.get_throughput(endpoint, hours)

        # 获取服务统计
        service_stats = performance_monitor.get_service_stats(hours=hours)

        return {
            "status": "success",
            "data": {
                "time_range_hours": hours,
                "endpoint": endpoint,
                "response_time_stats": response_time_stats,
                "error_rate": error_rate,
                "throughput": throughput,
                "service_stats": service_stats,
            },
        }
    except Exception as e:
        logger.error(f"获取性能统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能统计失败: {e}")


@router.get("/performance/report", summary="性能报告")
async def get_performance_report(
    hours: int = Query(1, ge=1, le=24, description="报告时间范围（小时）")
):
    """
    获取详细的性能报告

    Args:
        hours: 报告时间范围（小时）

    Returns:
        Dict: 详细的性能报告
    """
    try:
        performance_monitor = await get_performance_monitor()
        report = performance_monitor.get_performance_report(hours)

        return {"status": "success", "data": report}
    except Exception as e:
        logger.error(f"获取性能报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能报告失败: {e}")


@router.get("/performance/slow-requests", summary="慢请求列表")
async def get_slow_requests(
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    hours: int = Query(1, ge=1, le=24, description="时间范围（小时）"),
):
    """
    获取最慢的请求列表

    Args:
        limit: 返回数量限制
        hours: 时间范围（小时）

    Returns:
        Dict: 慢请求列表
    """
    try:
        performance_monitor = await get_performance_monitor()
        slow_requests = performance_monitor.get_top_slow_requests(limit, hours)

        return {
            "status": "success",
            "data": {"time_range_hours": hours, "limit": limit, "slow_requests": slow_requests},
        }
    except Exception as e:
        logger.error(f"获取慢请求列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取慢请求列表失败: {e}")


@router.get("/performance/summary", summary="性能摘要")
async def get_performance_summary():
    """
    获取性能摘要

    Returns:
        Dict: 性能摘要数据
    """
    try:
        health_checker = await get_health_checker()
        performance_summary = await health_checker.get_performance_summary()

        return {"status": "success", "data": performance_summary}
    except Exception as e:
        logger.error(f"获取性能摘要失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能摘要失败: {e}")


@router.get("/readiness", summary="就绪检查")
async def readiness_check():
    """
    Kubernetes就绪检查端点

    Returns:
        Dict: 就绪状态
    """
    try:
        health_checker = await get_health_checker()
        health_status = await health_checker.get_health_status()

        # 检查关键组件是否健康
        critical_components = ["database", "redis"]
        unhealthy_critical = [
            comp
            for comp in critical_components
            if comp in health_status.get("unhealthy_components", [])
        ]

        if unhealthy_critical:
            raise HTTPException(status_code=503, detail=f"关键组件不健康: {unhealthy_critical}")

        return {"status": "ready", "timestamp": health_status["timestamp"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"就绪检查失败: {e}")


@router.get("/liveness", summary="存活检查")
async def liveness_check():
    """
    Kubernetes存活检查端点

    Returns:
        Dict: 存活状态
    """
    try:
        # 简单的存活检查，只要服务能响应就认为存活
        return {"status": "alive", "timestamp": "2024-01-01T00:00:00"}  # 使用当前时间
    except Exception as e:
        logger.error(f"存活检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"存活检查失败: {e}")


@router.get("/startup", summary="启动检查")
async def startup_check():
    """
    Kubernetes启动检查端点

    Returns:
        Dict: 启动状态
    """
    try:
        health_checker = await get_health_checker()

        # 检查服务是否已完全启动
        health_status = await health_checker.get_health_status()

        # 如果有太多组件不健康，认为还在启动中
        total_components = len(health_status.get("components", {}))
        unhealthy_count = len(health_status.get("unhealthy_components", []))

        if total_components > 0 and unhealthy_count / total_components > 0.5:
            raise HTTPException(status_code=503, detail="服务仍在启动中，等待组件就绪")

        return {"status": "started", "timestamp": health_status["timestamp"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动检查失败: {e}")
        raise HTTPException(status_code=503, detail=f"启动检查失败: {e}")
