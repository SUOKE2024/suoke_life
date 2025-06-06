"""
monitoring - 索克生活项目模块
"""

from fastapi import FastAPI, Request, Response
from prometheus_client import (
from typing import Any
import psutil
import time

"""
监控和指标收集模块

提供 Prometheus 指标和健康检查功能
"""


    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# 定义指标
REQUEST_COUNT = Counter(
    "soer_service_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "soer_service_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_CONNECTIONS = Gauge(
    "soer_service_active_connections", "Number of active connections"
)

MEMORY_USAGE = Gauge("soer_service_memory_usage_bytes", "Memory usage in bytes")

CPU_USAGE = Gauge("soer_service_cpu_usage_percent", "CPU usage percentage")

NUTRITION_ANALYSIS_COUNT = Counter(
    "soer_service_nutrition_analysis_total",
    "Total number of nutrition analyses performed",
)

HEALTH_RECOMMENDATIONS_COUNT = Counter(
    "soer_service_health_recommendations_total",
    "Total number of health recommendations generated",
)


def setup_monitoring(app: FastAPI) -> None:
    """
    设置监控中间件和指标端点

    Args:
        app: FastAPI 应用实例
    """

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next) -> Response:
        """指标收集中间件"""
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 记录指标
        duration = time.time() - start_time
        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)

        REQUEST_COUNT.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        return response

    @app.get("/metrics")
    async def metrics_endpoint() -> Response:
        """Prometheus 指标端点"""
        # 更新系统指标
        update_system_metrics()

        # 生成指标数据
        metrics_data = generate_latest()

        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

    # 健康检查端点在 main.py 中定义，这里不重复定义

    @app.get("/health/ready")
    async def readiness_check() -> dict[str, Any]:
        """就绪检查端点"""
        checks = {
            "database": await check_database_health(),
            "redis": await check_redis_health(),
        }

        all_healthy = all(checks.values())

        return {"status": "ready" if all_healthy else "not_ready", "checks": checks}

    @app.get("/health/live")
    async def liveness_check() -> dict[str, str]:
        """存活检查端点"""
        return {"status": "alive"}


def update_system_metrics() -> None:
    """更新系统指标"""
    try:
        # 内存使用率
        memory_info = psutil.virtual_memory()
        MEMORY_USAGE.set(memory_info.used)

        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)

    except Exception:
        # 忽略指标收集错误
        pass


async def check_database_health() -> bool:
    """检查数据库健康状态"""
    try:
        # TODO: 实现数据库连接检查
        return True
    except Exception:
        return False


async def check_redis_health() -> bool:
    """检查 Redis 健康状态"""
    try:
        # TODO: 实现 Redis 连接检查
        return True
    except Exception:
        return False


async def check_ai_services_health() -> bool:
    """检查 AI 服务健康状态"""
    try:
        # TODO: 实现 AI 服务连接检查
        return True
    except Exception:
        return False


def record_nutrition_analysis() -> None:
    """记录营养分析指标"""
    NUTRITION_ANALYSIS_COUNT.inc()


def record_health_recommendation() -> None:
    """记录健康建议指标"""
    HEALTH_RECOMMENDATIONS_COUNT.inc()
