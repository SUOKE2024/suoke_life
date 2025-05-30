"""
健康检查器组件
提供微服务健康状态检查功能
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
from typing import Any

import aiohttp
import psutil
import pymongo
import redis
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """健康检查结果"""

    name: str
    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
        }


class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.checks: dict[str, Callable] = {}
        self.config = {}
        self.initialized = False

    async def initialize(self, config: dict[str, Any]):
        """初始化健康检查器"""
        self.config = config

        # 注册默认检查项
        await self._register_default_checks()

        self.initialized = True
        logger.info("健康检查器初始化完成")

    async def _register_default_checks(self):
        """注册默认健康检查项"""
        # 系统资源检查
        self.register_check("system_cpu", self._check_cpu_usage)
        self.register_check("system_memory", self._check_memory_usage)
        self.register_check("system_disk", self._check_disk_usage)

        # 网络连接检查
        if "database" in self.config:
            db_config = self.config["database"]
            if "postgresql" in db_config:
                self.register_check(
                    "database_postgresql",
                    lambda: self._check_postgresql(db_config["postgresql"]),
                )
            if "mongodb" in db_config:
                self.register_check(
                    "database_mongodb",
                    lambda: self._check_mongodb(db_config["mongodb"]),
                )
            if "redis" in db_config:
                self.register_check(
                    "database_redis", lambda: self._check_redis(db_config["redis"])
                )

        # HTTP服务检查
        if "services" in self.config:
            for service_name, service_config in self.config["services"].items():
                self.register_check(
                    f"service_{service_name}",
                    lambda cfg=service_config: self._check_http_service(cfg),
                )

    def register_check(self, name: str, check_func: Callable):
        """注册健康检查项"""
        self.checks[name] = check_func
        logger.debug(f"注册健康检查项: {name}")

    def unregister_check(self, name: str):
        """取消注册健康检查项"""
        if name in self.checks:
            del self.checks[name]
            logger.debug(f"取消注册健康检查项: {name}")

    async def check_health(
        self, check_names: list[str] | None = None
    ) -> dict[str, HealthCheckResult]:
        """执行健康检查"""
        if not self.initialized:
            raise RuntimeError("健康检查器未初始化")

        checks_to_run = check_names or list(self.checks.keys())
        results = {}

        # 并行执行检查
        tasks = []
        for check_name in checks_to_run:
            if check_name in self.checks:
                task = asyncio.create_task(self._run_single_check(check_name))
                tasks.append(task)

        if tasks:
            check_results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in check_results:
                if isinstance(result, HealthCheckResult):
                    results[result.name] = result
                elif isinstance(result, Exception):
                    logger.error(f"健康检查异常: {result}")

        return results

    async def _run_single_check(self, check_name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        start_time = time.time()

        try:
            check_func = self.checks[check_name]
            result = await check_func()

            if isinstance(result, HealthCheckResult):
                result.duration_ms = (time.time() - start_time) * 1000
                return result
            else:
                # 如果返回的不是HealthCheckResult，包装一下
                return HealthCheckResult(
                    name=check_name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    message=str(result) if result else "检查失败",
                    duration_ms=(time.time() - start_time) * 1000,
                )

        except Exception as e:
            logger.error(f"健康检查 {check_name} 失败: {e}")
            return HealthCheckResult(
                name=check_name,
                status=HealthStatus.UNHEALTHY,
                message=f"检查异常: {e!s}",
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def _check_cpu_usage(self) -> HealthCheckResult:
        """检查CPU使用率"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = self.config.get("thresholds", {}).get("cpu_percent", 80)

            if cpu_percent > threshold:
                status = HealthStatus.DEGRADED
                message = f"CPU使用率过高: {cpu_percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU使用率正常: {cpu_percent}%"

            return HealthCheckResult(
                name="system_cpu",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "threshold": threshold,
                    "cpu_count": psutil.cpu_count(),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_cpu",
                status=HealthStatus.UNHEALTHY,
                message=f"CPU检查失败: {e!s}",
            )

    async def _check_memory_usage(self) -> HealthCheckResult:
        """检查内存使用率"""
        try:
            memory = psutil.virtual_memory()
            threshold = self.config.get("thresholds", {}).get("memory_percent", 85)

            if memory.percent > threshold:
                status = HealthStatus.DEGRADED
                message = f"内存使用率过高: {memory.percent}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"内存使用率正常: {memory.percent}%"

            return HealthCheckResult(
                name="system_memory",
                status=status,
                message=message,
                details={
                    "memory_percent": memory.percent,
                    "threshold": threshold,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_memory",
                status=HealthStatus.UNHEALTHY,
                message=f"内存检查失败: {e!s}",
            )

    async def _check_disk_usage(self) -> HealthCheckResult:
        """检查磁盘使用率"""
        try:
            disk = psutil.disk_usage("/")
            threshold = self.config.get("thresholds", {}).get("disk_percent", 90)
            disk_percent = (disk.used / disk.total) * 100

            if disk_percent > threshold:
                status = HealthStatus.DEGRADED
                message = f"磁盘使用率过高: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"磁盘使用率正常: {disk_percent:.1f}%"

            return HealthCheckResult(
                name="system_disk",
                status=status,
                message=message,
                details={
                    "disk_percent": round(disk_percent, 1),
                    "threshold": threshold,
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                },
            )

        except Exception as e:
            return HealthCheckResult(
                name="system_disk",
                status=HealthStatus.UNHEALTHY,
                message=f"磁盘检查失败: {e!s}",
            )

    async def _check_postgresql(self, config: dict[str, Any]) -> HealthCheckResult:
        """检查PostgreSQL连接"""
        try:
            url = config.get("url", "postgresql://localhost:5432/postgres")
            timeout = config.get("timeout", 5)

            engine = create_engine(url, pool_timeout=timeout)

            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()

            return HealthCheckResult(
                name="database_postgresql",
                status=HealthStatus.HEALTHY,
                message="PostgreSQL连接正常",
                details={"url": url.split("@")[-1] if "@" in url else url},
            )

        except Exception as e:
            return HealthCheckResult(
                name="database_postgresql",
                status=HealthStatus.UNHEALTHY,
                message=f"PostgreSQL连接失败: {e!s}",
            )

    async def _check_mongodb(self, config: dict[str, Any]) -> HealthCheckResult:
        """检查MongoDB连接"""
        try:
            url = config.get("url", "mongodb://localhost:27017")
            timeout = config.get("timeout", 5000)

            client = pymongo.MongoClient(url, serverSelectionTimeoutMS=timeout)
            client.admin.command("ping")

            return HealthCheckResult(
                name="database_mongodb",
                status=HealthStatus.HEALTHY,
                message="MongoDB连接正常",
                details={"url": url.split("@")[-1] if "@" in url else url},
            )

        except Exception as e:
            return HealthCheckResult(
                name="database_mongodb",
                status=HealthStatus.UNHEALTHY,
                message=f"MongoDB连接失败: {e!s}",
            )

    async def _check_redis(self, config: dict[str, Any]) -> HealthCheckResult:
        """检查Redis连接"""
        try:
            host = config.get("host", "localhost")
            port = config.get("port", 6379)
            timeout = config.get("timeout", 5)

            r = redis.Redis(host=host, port=port, socket_timeout=timeout)
            r.ping()

            return HealthCheckResult(
                name="database_redis",
                status=HealthStatus.HEALTHY,
                message="Redis连接正常",
                details={"host": host, "port": port},
            )

        except Exception as e:
            return HealthCheckResult(
                name="database_redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis连接失败: {e!s}",
            )

    async def _check_http_service(self, config: dict[str, Any]) -> HealthCheckResult:
        """检查HTTP服务"""
        try:
            url = config.get("url", "http://localhost:8080/health")
            timeout = config.get("timeout", 10)
            expected_status = config.get("expected_status", 200)

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as session:
                async with session.get(url) as response:
                    if response.status == expected_status:
                        status = HealthStatus.HEALTHY
                        message = f"HTTP服务正常 (状态码: {response.status})"
                    else:
                        status = HealthStatus.UNHEALTHY
                        message = f"HTTP服务异常 (状态码: {response.status}, 期望: {expected_status})"

                    return HealthCheckResult(
                        name="http_service",
                        status=status,
                        message=message,
                        details={
                            "url": url,
                            "status_code": response.status,
                            "expected_status": expected_status,
                        },
                    )

        except Exception as e:
            return HealthCheckResult(
                name="http_service",
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP服务检查失败: {e!s}",
            )

    async def get_overall_status(
        self, check_results: dict[str, HealthCheckResult]
    ) -> HealthStatus:
        """获取整体健康状态"""
        if not check_results:
            return HealthStatus.UNKNOWN

        statuses = [result.status for result in check_results.values()]

        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            return HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNKNOWN

    async def health_check(self) -> dict[str, Any]:
        """执行完整健康检查并返回结果"""
        check_results = await self.check_health()
        overall_status = await self.get_overall_status(check_results)

        return {
            "status": overall_status.value,
            "timestamp": time.time(),
            "checks": {
                name: result.to_dict() for name, result in check_results.items()
            },
            "summary": {
                "total_checks": len(check_results),
                "healthy_checks": len(
                    [
                        r
                        for r in check_results.values()
                        if r.status == HealthStatus.HEALTHY
                    ]
                ),
                "unhealthy_checks": len(
                    [
                        r
                        for r in check_results.values()
                        if r.status == HealthStatus.UNHEALTHY
                    ]
                ),
                "degraded_checks": len(
                    [
                        r
                        for r in check_results.values()
                        if r.status == HealthStatus.DEGRADED
                    ]
                ),
            },
        }

    async def shutdown(self):
        """关闭健康检查器"""
        self.checks.clear()
        self.initialized = False
        logger.info("健康检查器已关闭")
