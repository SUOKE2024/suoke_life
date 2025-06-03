"""
健康检查模块

实现各种健康检查器和健康状态管理。
"""

import asyncio
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel

from ..core.config import Settings
from ..core.logging import get_logger

logger = get_logger(__name__)

class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class HealthCheckResult(BaseModel):
    """健康检查结果"""
    name: str
    status: HealthStatus
    message: str
    duration: float
    timestamp: float
    details: Optional[Dict[str, Any]] = None

class HealthSummary(BaseModel):
    """健康状态摘要"""
    status: HealthStatus
    checks: List[HealthCheckResult]
    timestamp: float
    duration: float

class HealthChecker(ABC):
    """健康检查器基类"""
    
    def __init__(self, name: str, timeout: float = 10.0):
        self.name = name
        self.timeout = timeout
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """执行健康检查"""
        pass

class DatabaseHealthChecker(HealthChecker):
    """数据库健康检查器"""
    
    def __init__(self, name: str = "database", connection_string: str = "", timeout: float = 5.0):
        super().__init__(name, timeout)
        self.connection_string = connection_string
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            # 这里应该根据实际数据库类型实现连接检查
            # 示例：PostgreSQL 检查
            # async with asyncpg.connect(self.connection_string) as conn:
            #     await conn.fetchval("SELECT 1")
            
            # 模拟检查
            await asyncio.sleep(0.1)
            
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Database connection successful",
                duration=duration,
                timestamp=time.time(),
                details={"connection_string": self.connection_string[:20] + "..."},
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Database connection failed: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={"error": str(e)},
            )

class RedisHealthChecker(HealthChecker):
    """Redis健康检查器"""
    
    def __init__(self, name: str = "redis", redis_url: str = "", timeout: float = 5.0):
        super().__init__(name, timeout)
        self.redis_url = redis_url
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            redis_client = redis.from_url(self.redis_url)
            
            # 执行ping命令
            await asyncio.wait_for(redis_client.ping(), timeout=self.timeout)
            
            # 获取Redis信息
            info = await redis_client.info()
            
            await redis_client.close()
            
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Redis connection successful",
                duration=duration,
                timestamp=time.time(),
                details={
                    "version": info.get("redis_version"),
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                },
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={"error": str(e)},
            )

class HTTPHealthChecker(HealthChecker):
    """HTTP服务健康检查器"""
    
    def __init__(
        self,
        name: str,
        url: str,
        method: str = "GET",
        expected_status: int = 200,
        timeout: float = 10.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(name, timeout)
        self.url = url
        self.method = method
        self.expected_status = expected_status
        self.headers = headers or {}
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.request(
                    self.method,
                    self.url,
                    headers=self.headers,
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == self.expected_status:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"HTTP check successful: {response.status}",
                            duration=duration,
                            timestamp=time.time(),
                            details={
                                "url": self.url,
                                "status_code": response.status,
                                "response_time": duration,
                            },
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"Unexpected status code: {response.status}",
                            duration=duration,
                            timestamp=time.time(),
                            details={
                                "url": self.url,
                                "status_code": response.status,
                                "expected_status": self.expected_status,
                            },
                        )
                        
        except Exception as e:
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP check failed: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={"error": str(e), "url": self.url},
            )

class DiskSpaceHealthChecker(HealthChecker):
    """磁盘空间健康检查器"""
    
    def __init__(
        self,
        name: str = "disk_space",
        path: str = "/",
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.9,
        timeout: float = 5.0,
    ):
        super().__init__(name, timeout)
        self.path = path
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            import shutil
            
            total, used, free = shutil.disk_usage(self.path)
            usage_ratio = used / total
            
            duration = time.time() - start_time
            
            if usage_ratio >= self.critical_threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Critical disk usage: {usage_ratio:.1%}"
            elif usage_ratio >= self.warning_threshold:
                status = HealthStatus.DEGRADED
                message = f"High disk usage: {usage_ratio:.1%}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {usage_ratio:.1%}"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                duration=duration,
                timestamp=time.time(),
                details={
                    "path": self.path,
                    "total_gb": round(total / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "free_gb": round(free / (1024**3), 2),
                    "usage_ratio": round(usage_ratio, 3),
                },
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={"error": str(e)},
            )

class MemoryHealthChecker(HealthChecker):
    """内存健康检查器"""
    
    def __init__(
        self,
        name: str = "memory",
        warning_threshold: float = 0.8,
        critical_threshold: float = 0.9,
        timeout: float = 5.0,
    ):
        super().__init__(name, timeout)
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
    
    async def check(self) -> HealthCheckResult:
        start_time = time.time()
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            usage_ratio = memory.percent / 100
            
            duration = time.time() - start_time
            
            if usage_ratio >= self.critical_threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Critical memory usage: {usage_ratio:.1%}"
            elif usage_ratio >= self.warning_threshold:
                status = HealthStatus.DEGRADED
                message = f"High memory usage: {usage_ratio:.1%}"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {usage_ratio:.1%}"
            
            return HealthCheckResult(
                name=self.name,
                status=status,
                message=message,
                duration=duration,
                timestamp=time.time(),
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_ratio": round(usage_ratio, 3),
                },
            )
            
        except Exception as e:
            duration = time.time() - start_time
            
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                duration=duration,
                timestamp=time.time(),
                details={"error": str(e)},
            )

class HealthManager:
    """健康检查管理器"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.checkers: List[HealthChecker] = []
        self.last_check_time: Optional[float] = None
        self.last_results: List[HealthCheckResult] = []
    
    def add_checker(self, checker: HealthChecker) -> None:
        """添加健康检查器"""
        self.checkers.append(checker)
        logger.info("Health checker added", name=checker.name)
    
    def remove_checker(self, name: str) -> bool:
        """移除健康检查器"""
        for i, checker in enumerate(self.checkers):
            if checker.name == name:
                del self.checkers[i]
                logger.info("Health checker removed", name=name)
                return True
        return False
    
    async def check_all(self) -> HealthSummary:
        """执行所有健康检查"""
        start_time = time.time()
        
        # 并发执行所有检查
        tasks = [checker.check() for checker in self.checkers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        check_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # 处理检查器异常
                check_results.append(
                    HealthCheckResult(
                        name=self.checkers[i].name,
                        status=HealthStatus.UNHEALTHY,
                        message=f"Health check failed: {str(result)}",
                        duration=0.0,
                        timestamp=time.time(),
                        details={"error": str(result)},
                    )
                )
            else:
                check_results.append(result)
        
        # 计算总体状态
        overall_status = self._calculate_overall_status(check_results)
        
        duration = time.time() - start_time
        self.last_check_time = time.time()
        self.last_results = check_results
        
        return HealthSummary(
            status=overall_status,
            checks=check_results,
            timestamp=time.time(),
            duration=duration,
        )
    
    async def check_single(self, name: str) -> Optional[HealthCheckResult]:
        """执行单个健康检查"""
        for checker in self.checkers:
            if checker.name == name:
                return await checker.check()
        return None
    
    def _calculate_overall_status(self, results: List[HealthCheckResult]) -> HealthStatus:
        """计算总体健康状态"""
        if not results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in results]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_last_results(self) -> Optional[HealthSummary]:
        """获取最后一次检查结果"""
        if not self.last_results or not self.last_check_time:
            return None
        
        overall_status = self._calculate_overall_status(self.last_results)
        
        return HealthSummary(
            status=overall_status,
            checks=self.last_results,
            timestamp=self.last_check_time,
            duration=0.0,  # 历史结果不计算持续时间
        )

def create_default_health_manager(settings: Settings) -> HealthManager:
    """创建默认的健康检查管理器"""
    manager = HealthManager(settings)
    
    # 添加Redis检查器
    if hasattr(settings, 'redis') and settings.redis.host:
        redis_checker = RedisHealthChecker(
            redis_url=settings.get_redis_url(),
            timeout=5.0,
        )
        manager.add_checker(redis_checker)
    
    # 添加系统资源检查器
    manager.add_checker(DiskSpaceHealthChecker())
    manager.add_checker(MemoryHealthChecker())
    
    return manager 