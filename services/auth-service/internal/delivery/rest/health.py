#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
健康检查模块

提供系统健康状态检查，支持Kubernetes探针和监控系统
"""
import os
import time
from datetime import datetime, UTC
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis

from internal.observability.telemetry import get_logger

# 创建日志记录器
logger = get_logger(__name__)

# 获取环境变量
SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")
ENV = os.getenv("ENV", "development")

# 服务启动时间
START_TIME = time.time()

# 创建路由器
router = APIRouter(tags=["Health"])


class HealthCheck:
    """健康检查管理器"""

    def __init__(self):
        self.db_engine: Optional[AsyncEngine] = None
        self.redis_client: Optional[Redis] = None
        self.dependencies: List[str] = []
        self.readiness_checks = {
            "database": self.check_database,
            "redis": self.check_redis
        }

    def register_db(self, engine: AsyncEngine) -> None:
        """注册数据库引擎
        
        Args:
            engine: SQLAlchemy异步引擎
        """
        self.db_engine = engine
        if "database" not in self.dependencies:
            self.dependencies.append("database")

    def register_redis(self, client: Redis) -> None:
        """注册Redis客户端
        
        Args:
            client: Redis异步客户端
        """
        self.redis_client = client
        if "redis" not in self.dependencies:
            self.dependencies.append("redis")

    async def check_database(self) -> Dict[str, bool]:
        """检查数据库连接
        
        Returns:
            健康状态
        """
        try:
            if self.db_engine:
                # 执行简单查询验证连接
                async with self.db_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return {"database": True}
            return {"database": False}
        except Exception as e:
            logger.error("数据库健康检查失败", error=str(e))
            return {"database": False}

    async def check_redis(self) -> Dict[str, bool]:
        """检查Redis连接
        
        Returns:
            健康状态
        """
        try:
            if self.redis_client:
                # 执行PING命令验证连接
                await self.redis_client.ping()
                return {"redis": True}
            return {"redis": False}
        except Exception as e:
            logger.error("Redis健康检查失败", error=str(e))
            return {"redis": False}

    async def is_alive(self) -> bool:
        """存活检查
        
        简单检查服务是否运行
        
        Returns:
            服务是否存活
        """
        # 服务正在运行，认为是存活的
        return True

    async def is_ready(self) -> Dict[str, bool]:
        """就绪检查
        
        检查所有依赖服务是否正常运行
        
        Returns:
            各依赖服务的就绪状态
        """
        status = {}
        
        # 检查每个已注册的依赖服务
        for dependency in self.dependencies:
            check_func = self.readiness_checks.get(dependency)
            if check_func:
                status.update(await check_func())
        
        return status


# 创建健康检查实例
health_check = HealthCheck()


def get_health_check() -> HealthCheck:
    """获取健康检查器实例"""
    return health_check


@router.get("/health", summary="完整健康状态")
async def health(health_checker: HealthCheck = Depends(get_health_check)) -> Dict:
    """
    获取服务完整健康状态
    
    包括系统信息、正常运行时间和依赖服务状态
    """
    # 系统信息
    info = {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENV,
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": int(time.time() - START_TIME)
    }
    
    # 依赖服务状态
    dependencies = await health_checker.is_ready()
    
    # 计算总体健康状态
    is_healthy = all(dependencies.values())
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "info": info,
        "dependencies": dependencies
    }


@router.get("/health/live", summary="存活检查")
async def liveness(health_checker: HealthCheck = Depends(get_health_check), response: Response = None) -> Dict:
    """
    存活检查 - Kubernetes 存活探针
    
    检查服务是否运行
    """
    is_alive = await health_checker.is_alive()
    
    if not is_alive and response:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "alive" if is_alive else "dead"
    }


@router.get("/health/ready", summary="就绪检查")
async def readiness(health_checker: HealthCheck = Depends(get_health_check), response: Response = None) -> Dict:
    """
    就绪检查 - Kubernetes 就绪探针
    
    检查服务是否可以接受流量
    """
    dependencies = await health_checker.is_ready()
    is_ready = all(dependencies.values())
    
    if not is_ready and response:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "dependencies": dependencies
    } 