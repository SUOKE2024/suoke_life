"""
健康检查服务

监控系统和依赖服务的健康状态。
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
import redis.asyncio as redis
from pydantic import BaseModel

from ..core.config import Settings
from ..core.logging import get_logger
from ..models.gateway import HealthCheckResult

logger = get_logger(__name__)


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str  # healthy, unhealthy, degraded
    timestamp: datetime
    details: Dict[str, HealthCheckResult]
    overall_score: float  # 0-100


class HealthService:
    """健康检查服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client: Optional[redis.Redis] = None
        self.last_check_time: Optional[datetime] = None
        self.check_interval = 30  # 秒
        self.health_cache: Optional[HealthStatus] = None
        
    async def initialize(self) -> None:
        """初始化健康检查服务"""
        try:
            # 初始化 Redis 连接
            self.redis_client = redis.from_url(
                self.settings.get_redis_url(),
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info("Health service initialized")
        except Exception as e:
            logger.error("Failed to initialize health service", error=str(e))
            raise
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def check_health(self, force: bool = False) -> HealthStatus:
        """检查系统健康状态"""
        now = datetime.utcnow()
        
        # 检查是否需要更新缓存
        if (not force and 
            self.health_cache and 
            self.last_check_time and 
            (now - self.last_check_time).seconds < self.check_interval):
            return self.health_cache
        
        logger.info("Performing health check")
        
        # 并发检查各个组件
        tasks = [
            self._check_redis(),
            self._check_registered_services(),
            self._check_system_resources(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 整理检查结果
        details = {}
        for result in results:
            if isinstance(result, dict):
                details.update(result)
            elif isinstance(result, Exception):
                logger.error("Health check failed", error=str(result))
        
        # 计算整体健康分数
        overall_score = self._calculate_health_score(details)
        
        # 确定整体状态
        if overall_score >= 90:
            status = "healthy"
        elif overall_score >= 70:
            status = "degraded"
        else:
            status = "unhealthy"
        
        # 创建健康状态
        health_status = HealthStatus(
            status=status,
            timestamp=now,
            details=details,
            overall_score=overall_score,
        )
        
        # 更新缓存
        self.health_cache = health_status
        self.last_check_time = now
        
        logger.info(
            "Health check completed",
            status=status,
            score=overall_score,
            components=len(details),
        )
        
        return health_status
    
    async def check_readiness(self) -> bool:
        """检查服务是否就绪"""
        try:
            health_status = await self.check_health()
            return health_status.status in ["healthy", "degraded"]
        except Exception as e:
            logger.error("Readiness check failed", error=str(e))
            return False
    
    async def _check_redis(self) -> Dict[str, HealthCheckResult]:
        """检查 Redis 连接"""
        start_time = time.time()
        
        try:
            if not self.redis_client:
                raise Exception("Redis client not initialized")
            
            # 执行 ping 命令
            await self.redis_client.ping()
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "redis": HealthCheckResult(
                    service_name="redis",
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                )
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return {
                "redis": HealthCheckResult(
                    service_name="redis",
                    status="unhealthy",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    error_message=str(e),
                )
            }
    
    async def _check_registered_services(self) -> Dict[str, HealthCheckResult]:
        """检查注册的服务"""
        results = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, service_config in self.settings.services.items():
                start_time = time.time()
                
                try:
                    url = f"http://{service_config.host}:{service_config.port}{service_config.health_check_path}"
                    response = await client.get(url)
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        status = "healthy"
                        error_message = None
                    else:
                        status = "unhealthy"
                        error_message = f"HTTP {response.status_code}"
                    
                    results[service_name] = HealthCheckResult(
                        service_name=service_name,
                        status=status,
                        response_time=response_time,
                        last_check=datetime.utcnow(),
                        error_message=error_message,
                    )
                    
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    
                    results[service_name] = HealthCheckResult(
                        service_name=service_name,
                        status="unhealthy",
                        response_time=response_time,
                        last_check=datetime.utcnow(),
                        error_message=str(e),
                    )
        
        return results
    
    async def _check_system_resources(self) -> Dict[str, HealthCheckResult]:
        """检查系统资源"""
        start_time = time.time()
        
        try:
            import psutil
            
            # 获取系统信息
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            response_time = (time.time() - start_time) * 1000
            
            # 判断系统状态
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                status = "unhealthy"
                error_message = f"High resource usage: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%"
            elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
                status = "degraded"
                error_message = f"Moderate resource usage: CPU {cpu_percent}%, Memory {memory.percent}%, Disk {disk.percent}%"
            else:
                status = "healthy"
                error_message = None
            
            return {
                "system": HealthCheckResult(
                    service_name="system",
                    status=status,
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    error_message=error_message,
                )
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            return {
                "system": HealthCheckResult(
                    service_name="system",
                    status="unhealthy",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    error_message=str(e),
                )
            }
    
    def _calculate_health_score(self, details: Dict[str, HealthCheckResult]) -> float:
        """计算健康分数"""
        if not details:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        # 权重配置
        weights = {
            "redis": 0.3,
            "system": 0.2,
        }
        
        for service_name, result in details.items():
            # 获取权重
            weight = weights.get(service_name, 0.1)
            
            # 计算分数
            if result.status == "healthy":
                score = 100.0
            elif result.status == "degraded":
                score = 70.0
            else:
                score = 0.0
            
            # 根据响应时间调整分数
            if result.response_time > 5000:  # 5秒
                score *= 0.5
            elif result.response_time > 1000:  # 1秒
                score *= 0.8
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0 