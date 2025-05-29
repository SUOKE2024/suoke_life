"""
健康检查端点
提供服务状态监控功能
"""
import asyncio
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pkg.utils.connection_pool import get_pool_manager
from pkg.utils.dependency_injection import get_container
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    checks: dict[str, Any]

class ComponentHealth(BaseModel):
    """组件健康状态"""
    name: str
    status: str
    message: str
    response_time_ms: float | None = None
    details: dict[str, Any] | None = None

class HealthChecker:
    """健康检查器"""

    def __init__(self):
        self.container = get_container()
        self.metrics = get_metrics_collector()
        self.pool_manager = get_pool_manager()
        self.start_time = datetime.now()
        self.version = "1.0.0"  # 从配置或环境变量获取

    async def check_overall_health(self) -> HealthStatus:
        """检查整体健康状态"""
        try:
            # 执行所有健康检查
            checks = await self._run_all_checks()

            # 确定整体状态
            overall_status = self._determine_overall_status(checks)

            # 计算运行时间
            uptime = (datetime.now() - self.start_time).total_seconds()

            return HealthStatus(
                status=overall_status,
                timestamp=datetime.now().isoformat(),
                version=self.version,
                uptime_seconds=uptime,
                checks={check.name: check.dict() for check in checks}
            )

        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return HealthStatus(
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                version=self.version,
                uptime_seconds=0,
                checks={"error": {"status": "unhealthy", "message": str(e)}}
            )

    async def _run_all_checks(self) -> list[ComponentHealth]:
        """运行所有健康检查"""
        checks = []

        # 并发执行所有检查
        check_tasks = [
            self._check_database(),
            self._check_redis(),
            self._check_agent_manager(),
            self._check_model_factory(),
            self._check_memory_usage(),
            self._check_disk_space(),
        ]

        results = await asyncio.gather(*check_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, ComponentHealth):
                checks.append(result)
            elif isinstance(result, Exception):
                checks.append(ComponentHealth(
                    name="unknown",
                    status="unhealthy",
                    message=str(result)
                ))

        return checks

    async def _check_database(self) -> ComponentHealth:
        """检查数据库连接"""
        start_time = datetime.now()

        try:
            db_pool = self.pool_manager.get_pool('database')

            async with db_pool.get_session() as session:
                await session.execute("SELECT 1")

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return ComponentHealth(
                name="database",
                status="healthy",
                message="数据库连接正常",
                response_time_ms=response_time,
                details={
                    "pool_size": db_pool.pool.get_size(),
                    "checked_in": db_pool.pool.checked_in(),
                    "checked_out": db_pool.pool.checked_out()
                }
            )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ComponentHealth(
                name="database",
                status="unhealthy",
                message=f"数据库连接失败: {e}",
                response_time_ms=response_time
            )

    async def _check_redis(self) -> ComponentHealth:
        """检查Redis连接"""
        start_time = datetime.now()

        try:
            redis_pool = self.pool_manager.get_pool('redis')
            await redis_pool.ping()

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            # 获取Redis信息
            info = await redis_pool.info()

            return ComponentHealth(
                name="redis",
                status="healthy",
                message="Redis连接正常",
                response_time_ms=response_time,
                details={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "redis_version": info.get("redis_version", "unknown")
                }
            )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ComponentHealth(
                name="redis",
                status="unhealthy",
                message=f"Redis连接失败: {e}",
                response_time_ms=response_time
            )

    async def _check_agent_manager(self) -> ComponentHealth:
        """检查智能体管理器"""
        start_time = datetime.now()

        try:
            agent_manager = self.container.get_service("agent_manager")
            is_healthy = await agent_manager.health_check()

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            if is_healthy:
                return ComponentHealth(
                    name="agent_manager",
                    status="healthy",
                    message="智能体管理器运行正常",
                    response_time_ms=response_time
                )
            else:
                return ComponentHealth(
                    name="agent_manager",
                    status="unhealthy",
                    message="智能体管理器健康检查失败",
                    response_time_ms=response_time
                )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ComponentHealth(
                name="agent_manager",
                status="unhealthy",
                message=f"智能体管理器检查失败: {e}",
                response_time_ms=response_time
            )

    async def _check_model_factory(self) -> ComponentHealth:
        """检查模型工厂"""
        start_time = datetime.now()

        try:
            model_factory = self.container.get_service("model_factory")
            is_healthy = await model_factory.health_check()

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            loaded_models = model_factory.list_loaded_models()

            if is_healthy:
                return ComponentHealth(
                    name="model_factory",
                    status="healthy",
                    message="模型工厂运行正常",
                    response_time_ms=response_time,
                    details={
                        "loaded_models": loaded_models,
                        "model_count": len(loaded_models)
                    }
                )
            else:
                return ComponentHealth(
                    name="model_factory",
                    status="unhealthy",
                    message="模型工厂健康检查失败",
                    response_time_ms=response_time
                )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ComponentHealth(
                name="model_factory",
                status="unhealthy",
                message=f"模型工厂检查失败: {e}",
                response_time_ms=response_time
            )

    async def _check_memory_usage(self) -> ComponentHealth:
        """检查内存使用情况"""
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 内存使用超过90%认为不健康
            if memory_percent > 90:
                status = "unhealthy"
                message = f"内存使用率过高: {memory_percent:.1f}%"
            elif memory_percent > 80:
                status = "warning"
                message = f"内存使用率较高: {memory_percent:.1f}%"
            else:
                status = "healthy"
                message = f"内存使用正常: {memory_percent:.1f}%"

            return ComponentHealth(
                name="memory",
                status=status,
                message=message,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_percent": memory_percent
                }
            )

        except ImportError:
            return ComponentHealth(
                name="memory",
                status="unknown",
                message="psutil库未安装，无法检查内存使用情况"
            )
        except Exception as e:
            return ComponentHealth(
                name="memory",
                status="unhealthy",
                message=f"内存检查失败: {e}"
            )

    async def _check_disk_space(self) -> ComponentHealth:
        """检查磁盘空间"""
        try:
            import psutil

            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100

            # 磁盘使用超过90%认为不健康
            if disk_percent > 90:
                status = "unhealthy"
                message = f"磁盘使用率过高: {disk_percent:.1f}%"
            elif disk_percent > 80:
                status = "warning"
                message = f"磁盘使用率较高: {disk_percent:.1f}%"
            else:
                status = "healthy"
                message = f"磁盘使用正常: {disk_percent:.1f}%"

            return ComponentHealth(
                name="disk",
                status=status,
                message=message,
                details={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "used_percent": disk_percent
                }
            )

        except ImportError:
            return ComponentHealth(
                name="disk",
                status="unknown",
                message="psutil库未安装，无法检查磁盘使用情况"
            )
        except Exception as e:
            return ComponentHealth(
                name="disk",
                status="unhealthy",
                message=f"磁盘检查失败: {e}"
            )

    def _determine_overall_status(self, checks: list[ComponentHealth]) -> str:
        """确定整体健康状态"""
        if not checks:
            return "unhealthy"

        statuses = [check.status for check in checks]

        if "unhealthy" in statuses:
            return "unhealthy"
        elif "warning" in statuses:
            return "warning"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"

# 创建健康检查器实例
health_checker = HealthChecker()

# 创建路由器
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    健康检查端点
    返回服务的整体健康状态
    """
    try:
        health_status = await health_checker.check_overall_health()

        # 根据状态设置HTTP状态码
        if health_status.status == "healthy":
            status_code = 200
        elif health_status.status == "warning":
            status_code = 200  # 警告状态仍返回200
        else:
            status_code = 503  # 服务不可用

        return JSONResponse(
            content=health_status.dict(),
            status_code=status_code
        )

    except Exception as e:
        logger.error(f"健康检查端点错误: {e}")
        raise HTTPException(status_code=500, detail="健康检查失败")

@router.get("/ready")
async def readiness_check():
    """
    就绪检查端点
    检查服务是否准备好接收请求
    """
    try:
        # 检查关键组件
        checks = await asyncio.gather(
            health_checker._check_database(),
            health_checker._check_redis(),
            health_checker._check_agent_manager(),
            return_exceptions=True
        )

        # 检查是否有关键组件不健康
        for check in checks:
            if isinstance(check, ComponentHealth) and check.status == "unhealthy":
                return JSONResponse(
                    content={"status": "not_ready", "message": f"{check.name}不可用"},
                    status_code=503
                )

        return {"status": "ready", "message": "服务已准备就绪"}

    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        return JSONResponse(
            content={"status": "not_ready", "message": "就绪检查失败"},
            status_code=503
        )

@router.get("/live")
async def liveness_check():
    """
    存活检查端点
    检查服务是否仍在运行
    """
    try:
        # 简单的存活检查，只要能响应就认为存活
        uptime = (datetime.now() - health_checker.start_time).total_seconds()

        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime
        }

    except Exception as e:
        logger.error(f"存活检查失败: {e}")
        raise HTTPException(status_code=500, detail="存活检查失败")

@router.get("/metrics")
async def metrics_endpoint():
    """
    指标端点
    返回Prometheus格式的指标
    """
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        metrics_data = generate_latest()

        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )

    except Exception as e:
        logger.error(f"指标端点错误: {e}")
        raise HTTPException(status_code=500, detail="指标获取失败")

@router.get("/version")
async def version_info():
    """
    版本信息端点
    """
    return {
        "version": health_checker.version,
        "service": "soer-service",
        "build_time": "2024-01-01T00:00:00Z",  # 从构建时设置
        "git_commit": "unknown"  # 从构建时设置
    }
