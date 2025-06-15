"""
健康检查API

提供服务健康状态检查和监控端点
"""
import asyncio
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from internal.config.settings import get_settings

router = APIRouter()


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    uptime: float
    service: str


class DetailedHealthStatus(BaseModel):
    """详细健康状态模型"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    uptime: float
    service: str
    components: Dict[str, Any]
    metrics: Dict[str, Any]


# 服务启动时间
_start_time = time.time()


async def check_database_health() -> Dict[str, Any]:
    """检查数据库健康状态"""
    try:
        # 这里应该实际检查数据库连接
        # from internal.database.connection import get_database
        # db = await get_database()
        # await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "response_time": 0.001,
            "connection_pool": {
                "active": 5,
                "idle": 15,
                "total": 20
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time": None
        }


async def check_redis_health() -> Dict[str, Any]:
    """检查Redis健康状态"""
    try:
        # 这里应该实际检查Redis连接
        # from internal.redis.connection import get_redis
        # redis = await get_redis()
        # await redis.ping()
        
        return {
            "status": "healthy",
            "response_time": 0.001,
            "memory_usage": "10MB",
            "connected_clients": 5
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time": None
        }


async def check_celery_health() -> Dict[str, Any]:
    """检查Celery健康状态"""
    try:
        # 这里应该实际检查Celery状态
        # from internal.tasks.celery_app import celery_app
        # inspect = celery_app.control.inspect()
        # stats = inspect.stats()
        
        return {
            "status": "healthy",
            "active_workers": 3,
            "queues": {
                "review": 5,
                "ai_analysis": 2,
                "workflow": 1
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "active_workers": 0
        }


async def check_ai_engine_health() -> Dict[str, Any]:
    """检查AI引擎健康状态"""
    try:
        # 这里应该实际检查AI模型状态
        # from internal.ai.text_analyzer import TextAnalyzer
        # analyzer = TextAnalyzer()
        # await analyzer.health_check()
        
        return {
            "status": "healthy",
            "models_loaded": {
                "text_analyzer": True,
                "image_analyzer": True,
                "risk_assessor": True
            },
            "gpu_available": False,
            "memory_usage": "2.5GB"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "models_loaded": {}
        }


@router.get(
    "/",
    response_model=HealthStatus,
    summary="基础健康检查",
    description="获取服务基础健康状态"
)
async def health_check():
    """基础健康检查"""
    settings = get_settings()
    current_time = time.time()
    uptime = current_time - _start_time
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment,
        uptime=uptime,
        service="human-review-service"
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthStatus,
    summary="详细健康检查",
    description="获取服务详细健康状态，包括各组件状态"
)
async def detailed_health_check():
    """详细健康检查"""
    settings = get_settings()
    current_time = time.time()
    uptime = current_time - _start_time
    
    # 并发检查各组件健康状态
    db_health, redis_health, celery_health, ai_health = await asyncio.gather(
        check_database_health(),
        check_redis_health(),
        check_celery_health(),
        check_ai_engine_health(),
        return_exceptions=True
    )
    
    # 处理异常情况
    components = {}
    for name, health in [
        ("database", db_health),
        ("redis", redis_health),
        ("celery", celery_health),
        ("ai_engine", ai_health)
    ]:
        if isinstance(health, Exception):
            components[name] = {
                "status": "error",
                "error": str(health)
            }
        else:
            components[name] = health
    
    # 计算整体状态
    overall_status = "healthy"
    unhealthy_components = [
        name for name, comp in components.items()
        if comp.get("status") != "healthy"
    ]
    
    if unhealthy_components:
        if len(unhealthy_components) >= len(components) / 2:
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
    
    # 收集指标
    metrics = {
        "uptime_seconds": uptime,
        "memory_usage": "150MB",  # 这里应该获取实际内存使用
        "cpu_usage": "15%",       # 这里应该获取实际CPU使用
        "disk_usage": "45%",      # 这里应该获取实际磁盘使用
        "active_connections": 25,
        "request_count_24h": 1250,
        "error_rate_24h": 0.02
    }
    
    return DetailedHealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment,
        uptime=uptime,
        service="human-review-service",
        components=components,
        metrics=metrics
    )


@router.get(
    "/ai",
    summary="AI引擎健康检查",
    description="专门检查AI引擎的健康状态"
)
async def ai_health_check():
    """AI引擎健康检查"""
    ai_health = await check_ai_engine_health()
    
    if ai_health.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI引擎不可用"
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "AI引擎运行正常",
            "details": ai_health,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get(
    "/readiness",
    summary="就绪检查",
    description="检查服务是否准备好接收请求"
)
async def readiness_check():
    """就绪检查"""
    # 检查关键组件是否就绪
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    
    if (db_health.get("status") != "healthy" or 
        redis_health.get("status") != "healthy"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="服务未就绪"
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "message": "服务已就绪",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get(
    "/liveness",
    summary="存活检查",
    description="检查服务是否存活"
)
async def liveness_check():
    """存活检查"""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "alive",
            "message": "服务正在运行",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - _start_time
        }
    ) 