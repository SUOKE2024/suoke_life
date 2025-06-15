"""
健康检查API路由
提供系统健康状态检查功能
"""
import time
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.logger import get_logger
from app.services.knowledge_service import KnowledgeService
from app.services.cache_service import CacheService
from app.api.rest.deps import get_knowledge_service, get_cache_service

logger = get_logger()
router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="基础健康检查")
async def health_check():
    """
    基础健康检查
    返回服务的基本状态信息
    """
    return {
        "status": "healthy",
        "service": "med-knowledge",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@router.get("/health/ready", summary="就绪检查")
async def readiness_check(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    就绪检查
    检查服务是否准备好接收请求
    """
    try:
        checks = {}
        overall_ready = True
        
        # 检查数据库连接
        try:
            await knowledge_service.health_check()
            checks["database"] = {"status": "ready", "message": "数据库连接正常"}
        except Exception as e:
            checks["database"] = {"status": "not_ready", "message": f"数据库连接失败: {str(e)}"}
            overall_ready = False
        
        # 检查缓存服务
        try:
            await cache_service.health_check()
            checks["cache"] = {"status": "ready", "message": "缓存服务正常"}
        except Exception as e:
            checks["cache"] = {"status": "not_ready", "message": f"缓存服务失败: {str(e)}"}
            overall_ready = False
        
        # 检查基本功能
        try:
            # 尝试执行一个简单的查询
            await knowledge_service.get_node_count()
            checks["basic_functionality"] = {"status": "ready", "message": "基本功能正常"}
        except Exception as e:
            checks["basic_functionality"] = {"status": "not_ready", "message": f"基本功能异常: {str(e)}"}
            overall_ready = False
        
        status_code = 200 if overall_ready else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "ready": overall_ready,
                "checks": checks,
                "timestamp": time.time()
            }
        )
        
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/live", summary="存活检查")
async def liveness_check():
    """
    存活检查
    检查服务进程是否存活
    """
    try:
        # 执行一些基本的内存和CPU检查
        start_time = time.time()
        
        # 简单的计算任务来验证进程响应
        test_data = list(range(1000))
        result = sum(test_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 如果响应时间过长，可能表示系统有问题
        if response_time > 1.0:
            logger.warning(f"存活检查响应时间过长: {response_time:.3f}s")
        
        return {
            "alive": True,
            "response_time": response_time,
            "test_result": result,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"存活检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "alive": False,
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/detailed", summary="详细健康检查")
async def detailed_health_check(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    详细健康检查
    提供系统各组件的详细状态信息
    """
    try:
        health_data = {
            "service": "med-knowledge",
            "version": "1.0.0",
            "timestamp": time.time(),
            "uptime": time.time(),  # 这里应该是实际的运行时间
            "components": {}
        }
        
        # 数据库健康检查
        try:
            db_start = time.time()
            node_count = await knowledge_service.get_node_count()
            relationship_count = await knowledge_service.get_relationship_count()
            db_time = time.time() - db_start
            
            health_data["components"]["database"] = {
                "status": "healthy",
                "response_time": db_time,
                "metrics": {
                    "node_count": node_count,
                    "relationship_count": relationship_count
                }
            }
        except Exception as e:
            health_data["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 缓存健康检查
        try:
            cache_start = time.time()
            cache_stats = await cache_service.get_stats()
            cache_time = time.time() - cache_start
            
            health_data["components"]["cache"] = {
                "status": "healthy",
                "response_time": cache_time,
                "metrics": cache_stats
            }
        except Exception as e:
            health_data["components"]["cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 系统资源检查
        try:
            system_metrics = await _get_system_metrics()
            health_data["components"]["system"] = {
                "status": "healthy",
                "metrics": system_metrics
            }
        except Exception as e:
            health_data["components"]["system"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # 确定整体健康状态
        unhealthy_components = [
            name for name, component in health_data["components"].items()
            if component["status"] == "unhealthy"
        ]
        
        health_data["overall_status"] = "healthy" if not unhealthy_components else "unhealthy"
        health_data["unhealthy_components"] = unhealthy_components
        
        status_code = 200 if health_data["overall_status"] == "healthy" else 503
        
        return JSONResponse(
            status_code=status_code,
            content=health_data
        )
        
    except Exception as e:
        logger.error(f"详细健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/health/metrics", summary="健康指标")
async def health_metrics(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    健康指标
    返回用于监控的关键指标
    """
    try:
        metrics = {
            "timestamp": time.time(),
            "service_metrics": {},
            "performance_metrics": {},
            "resource_metrics": {}
        }
        
        # 服务指标
        try:
            node_count = await knowledge_service.get_node_count()
            relationship_count = await knowledge_service.get_relationship_count()
            
            metrics["service_metrics"] = {
                "total_nodes": node_count,
                "total_relationships": relationship_count,
                "knowledge_density": relationship_count / node_count if node_count > 0 else 0
            }
        except Exception as e:
            logger.error(f"获取服务指标失败: {e}")
            metrics["service_metrics"] = {"error": str(e)}
        
        # 性能指标
        try:
            cache_stats = await cache_service.get_stats()
            metrics["performance_metrics"] = {
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "cache_size": cache_stats.get("size", 0),
                "cache_memory_usage": cache_stats.get("memory_usage", 0)
            }
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            metrics["performance_metrics"] = {"error": str(e)}
        
        # 资源指标
        try:
            system_metrics = await _get_system_metrics()
            metrics["resource_metrics"] = system_metrics
        except Exception as e:
            logger.error(f"获取资源指标失败: {e}")
            metrics["resource_metrics"] = {"error": str(e)}
        
        return metrics
        
    except Exception as e:
        logger.error(f"获取健康指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取健康指标失败: {str(e)}")


async def _get_system_metrics() -> Dict[str, Any]:
    """获取系统资源指标"""
    try:
        import psutil
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 网络统计
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "usage_percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
        
    except ImportError:
        logger.warning("psutil未安装，无法获取系统指标")
        return {"error": "psutil not available"}
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        return {"error": str(e)} 