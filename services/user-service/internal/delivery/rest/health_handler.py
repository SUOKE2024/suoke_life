"""
健康检查API处理器
提供健康检查、状态监控和指标暴露等功能
"""
import logging
import os
import platform
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST

from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.observability.metrics import prometheus_metrics

# 日志记录器
logger = logging.getLogger(__name__)

# 服务启动时间
SERVICE_START_TIME = datetime.utcnow()

# 服务版本
SERVICE_VERSION = os.getenv("USER_SERVICE_VERSION", "1.0.0")


def create_health_api_router(repository: SQLiteUserRepository) -> APIRouter:
    """
    创建健康检查API路由器
    
    Args:
        repository: 用户数据库存储库
        
    Returns:
        APIRouter: 路由器
    """
    router = APIRouter(tags=["health"])
    
    @router.get("/health")
    async def health_check(request: Request, detailed: bool = False) -> Dict[str, Any]:
        """
        健康检查端点
        提供服务健康状态，用于监控和负载均衡检查
        
        Args:
            request: 请求对象
            detailed: 是否返回详细信息
            
        Returns:
            Dict[str, Any]: 健康状态
        """
        start_time = time.time()
        
        # 计算服务运行时间
        uptime = datetime.utcnow() - SERVICE_START_TIME
        uptime_seconds = uptime.total_seconds()
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        # 检查数据库连接
        db_status = "unknown"
        db_latency = -1
        db_error = None
        db_message = None
        
        try:
            db_check_start = time.time()
            await repository.health_check()
            db_latency = round((time.time() - db_check_start) * 1000, 2)  # 毫秒
            db_status = "up" if db_latency < 1000 else "degraded"  # 如果数据库响应时间超过1秒，认为是性能降级
            db_message = "数据库连接正常"
        except Exception as e:
            db_status = "down"
            db_error = str(e)
            db_message = "数据库连接失败"
            logger.error(f"数据库健康检查失败: {e}")
        
        # 系统信息
        system_info = {
            "os": platform.system(),
            "version": platform.version(),
            "python": sys.version,
            "pid": os.getpid(),
            "machine": platform.machine()
        }
        
        # 收集健康状态
        health_status = {
            "status": "up" if db_status == "up" else ("degraded" if db_status == "degraded" else "down"),
            "version": SERVICE_VERSION,
            "name": "user-service",
            "uptime": uptime_str,
            "uptime_seconds": int(uptime_seconds),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 如果请求详细信息，添加更多数据
        if detailed:
            health_status.update({
                "database": {
                    "status": db_status,
                    "latency_ms": db_latency,
                    "message": db_message,
                    "error": db_error
                },
                "system": system_info,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "memory_usage_mb": get_process_memory_mb()
            })
        
        # 计算API响应时间
        response_time = time.time() - start_time
        
        # 记录性能指标
        prometheus_metrics.health_check_count.inc()
        prometheus_metrics.health_check_latency.observe(response_time)
        prometheus_metrics.database_latency.observe(db_latency / 1000.0)  # 秒
        
        # 返回健康状态
        response = JSONResponse(
            content=health_status,
            status_code=200 if health_status["status"] == "up" else (
                503 if health_status["status"] == "down" else 429
            )
        )
        
        # 添加指标响应头
        response.headers["X-Response-Time"] = f"{response_time:.6f}"
        
        return response
    
    @router.get("/status")
    async def status_check() -> Dict[str, str]:
        """
        简化版状态检查端点
        提供简单的服务状态，用于快速检查
        
        Returns:
            Dict[str, str]: 服务状态
        """
        return {
            "status": "ok",
            "service": "user-service",
            "version": SERVICE_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @router.get("/metrics")
    async def metrics(request: Request) -> Response:
        """
        Prometheus指标端点
        提供服务指标，用于监控和性能分析
        
        Args:
            request: 请求对象
            
        Returns:
            Response: 包含Prometheus格式指标的响应
        """
        return Response(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )
    
    return router


def get_process_memory_mb() -> float:
    """
    获取当前进程内存使用量（MB）
    
    Returns:
        float: 内存使用量（MB）
    """
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return round(memory_info.rss / (1024 * 1024), 2)  # 转换为MB
    except ImportError:
        return -1  # 如果psutil不可用，返回-1
    except Exception as e:
        logger.warning(f"获取进程内存使用量失败: {e}")
        return -1 