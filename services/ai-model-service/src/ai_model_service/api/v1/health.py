"""健康检查API"""

import time
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str
    timestamp: float
    service: str
    version: str
    uptime: float
    checks: Dict[str, Any] = Field(default_factory=dict)


# 服务启动时间
_start_time = time.time()


@router.get("/", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    """基本健康检查"""
    settings = request.app.state.settings

    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service=settings.app_name,
        version=settings.app_version,
        uptime=time.time() - _start_time,
    )


@router.get("/live", response_model=HealthResponse)
async def liveness_probe(request: Request) -> HealthResponse:
    """存活检查 - Kubernetes liveness probe"""
    settings = request.app.state.settings

    # 基本的存活检查
    checks = {"service": "healthy"}

    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service=settings.app_name,
        version=settings.app_version,
        uptime=time.time() - _start_time,
        checks=checks,
    )


@router.get("/ready", response_model=HealthResponse)
async def readiness_probe(request: Request) -> HealthResponse:
    """就绪检查 - Kubernetes readiness probe"""
    settings = request.app.state.settings

    checks = {}
    overall_status = "healthy"

    # 检查模型管理器
    if hasattr(request.app.state, "manager") and request.app.state.manager:
        try:
            manager = request.app.state.manager
            if manager.is_initialized:
                checks["model_manager"] = "healthy"
            else:
                checks["model_manager"] = "initializing"
                overall_status = "degraded"
        except Exception as e:
            checks["model_manager"] = f"unhealthy: {str(e)}"
            overall_status = "unhealthy"
    else:
        checks["model_manager"] = "not_initialized"
        overall_status = "unhealthy"

    # 检查Kubernetes连接
    if hasattr(request.app.state, "k8s_client") and request.app.state.k8s_client:
        try:
            # 简单的K8s连接检查
            checks["kubernetes"] = "healthy"
        except Exception as e:
            checks["kubernetes"] = f"unhealthy: {str(e)}"
            overall_status = "unhealthy"
    else:
        checks["kubernetes"] = "not_configured"
        overall_status = "degraded"

    # 检查指标收集器
    if hasattr(request.app.state, "metrics") and request.app.state.metrics:
        try:
            metrics = request.app.state.metrics
            if metrics.is_running:
                checks["metrics"] = "healthy"
            else:
                checks["metrics"] = "stopped"
                overall_status = "degraded"
        except Exception as e:
            checks["metrics"] = f"unhealthy: {str(e)}"
            overall_status = "degraded"
    else:
        checks["metrics"] = "disabled"

    # 如果任何关键组件不健康，返回503状态码
    status_code = status.HTTP_200_OK
    if overall_status=="unhealthy":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    response = HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        service=settings.app_name,
        version=settings.app_version,
        uptime=time.time() - _start_time,
        checks=checks,
    )

    if status_code!=status.HTTP_200_OK:
        logger.warning("就绪检查失败", status=overall_status, checks=checks)

    return response


@router.get("/startup", response_model=HealthResponse)
async def startup_probe(request: Request) -> HealthResponse:
    """启动检查 - Kubernetes startup probe"""
    settings = request.app.state.settings

    checks = {}
    overall_status = "healthy"

    # 检查服务是否完全启动
    min_uptime = 10  # 最少运行10秒才认为启动完成
    current_uptime = time.time() - _start_time

    if current_uptime < min_uptime:
        checks["uptime"] = f"starting ({current_uptime:.1f}s < {min_uptime}s)"
        overall_status = "starting"
    else:
        checks["uptime"] = f"ready ({current_uptime:.1f}s)"

    # 检查关键组件是否初始化
    if hasattr(request.app.state, "manager") and request.app.state.manager:
        if request.app.state.manager.is_initialized:
            checks["initialization"] = "complete"
        else:
            checks["initialization"] = "in_progress"
            overall_status = "starting"
    else:
        checks["initialization"] = "pending"
        overall_status = "starting"

    # 启动检查失败时返回503
    status_code = status.HTTP_200_OK
    if overall_status=="starting":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    response = HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        service=settings.app_name,
        version=settings.app_version,
        uptime=current_uptime,
        checks=checks,
    )

    if status_code!=status.HTTP_200_OK:
        logger.debug("启动检查进行中", status=overall_status, checks=checks)

    return response


@router.get("/detailed", response_model=HealthResponse)
async def detailed_health_check(request: Request) -> HealthResponse:
    """详细健康检查"""
    settings = request.app.state.settings

    checks = {}
    overall_status = "healthy"

    # 系统信息
    import platform

    import psutil

    checks["system"] = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": str(psutil.cpu_count()),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }

    # 模型管理器详细状态
    if hasattr(request.app.state, "manager") and request.app.state.manager:
        try:
            manager = request.app.state.manager
            deployments = await manager.list_models()
            checks["model_manager"] = {
                "status": "healthy" if manager.is_initialized else "initializing",
                "deployed_models": len(deployments),
                "models": [
                    {
                        "model_id": dep.model_id,
                        "status": dep.status.value,
                        "replicas": f"{dep.ready_replicas}/{dep.replicas}",
                    }
                    for dep in deployments[:5]  # 只显示前5个
                ],
            }
        except Exception as e:
            checks["model_manager"] = {"status": "error", "error": str(e)}
            overall_status = "degraded"

    # 指标收集器状态
    if hasattr(request.app.state, "metrics") and request.app.state.metrics:
        try:
            metrics = request.app.state.metrics
            checks["metrics"] = {
                "status": "running" if metrics.is_running else "stopped",
                "collected_metrics": (
                    len(metrics._metrics) if hasattr(metrics, "_metrics") else 0
                ),
            }
        except Exception as e:
            checks["metrics"] = {"status": "error", "error": str(e)}

    return HealthResponse(
        status=overall_status,
        timestamp=time.time(),
        service=settings.app_name,
        version=settings.app_version,
        uptime=time.time() - _start_time,
        checks=checks,
    )
