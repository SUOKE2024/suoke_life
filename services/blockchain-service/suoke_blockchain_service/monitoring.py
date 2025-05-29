"""
监控和指标收集模块

提供 Prometheus 指标、OpenTelemetry 追踪和健康检查功能。
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorClient,
    GrpcInstrumentorServer,
)
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from .config import settings
from .logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger(__name__)

# Prometheus 指标
REQUEST_COUNT = Counter(
    "blockchain_service_requests_total",
    "区块链服务请求总数",
    ["method", "endpoint", "status_code"]
)

REQUEST_DURATION = Histogram(
    "blockchain_service_request_duration_seconds",
    "区块链服务请求持续时间",
    ["method", "endpoint"]
)

BLOCKCHAIN_OPERATIONS = Counter(
    "blockchain_service_operations_total",
    "区块链操作总数",
    ["operation", "status"]
)

DATABASE_OPERATIONS = Counter(
    "blockchain_service_database_operations_total",
    "数据库操作总数",
    ["operation", "status"]
)

GRPC_REQUESTS = Counter(
    "blockchain_service_grpc_requests_total",
    "gRPC 请求总数",
    ["method", "status"]
)


def setup_tracing() -> None:
    """设置 OpenTelemetry 追踪"""
    if not settings.monitoring.enable_tracing:
        return

    logger.info("设置 OpenTelemetry 追踪")

    # 设置追踪提供者
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # 配置导出器(如果需要的话)
    if settings.monitoring.jaeger_endpoint:
        try:
            # 尝试导入和配置 Jaeger 导出器
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            provider.add_span_processor(span_processor)
        except ImportError:
            logger.warning("Jaeger 导出器不可用, 跳过追踪导出配置")

    logger.info("OpenTelemetry 追踪设置完成")


def setup_instrumentation() -> None:
    """设置自动化仪表"""
    if not settings.monitoring.enable_tracing:
        return

    logger.info("设置自动化仪表")

    # FastAPI 仪表
    FastAPIInstrumentor.instrument()

    # SQLAlchemy 仪表
    SQLAlchemyInstrumentor().instrument()

    # gRPC 仪表 - 使用 Any 类型避免类型检查问题
    try:
        grpc_server_instrumentor: Any = GrpcInstrumentorServer()  # type: ignore
        grpc_client_instrumentor: Any = GrpcInstrumentorClient()  # type: ignore
        grpc_server_instrumentor.instrument()
        grpc_client_instrumentor.instrument()
    except Exception as e:
        logger.warning("gRPC 仪表设置失败", error=str(e))

    logger.info("自动化仪表设置完成")


def setup_monitoring(app: FastAPI) -> None:
    """设置监控"""
    if not settings.monitoring.enable_metrics:
        return

    logger.info("设置监控")

    # 设置追踪
    setup_tracing()
    setup_instrumentation()

    # 添加指标中间件
    @app.middleware("http")
    async def metrics_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """指标收集中间件"""
        start_time = time.time()

        response = await call_next(request)

        # 记录请求指标
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        return response

    # 添加指标端点
    @app.get("/metrics")
    async def metrics() -> Response:
        """Prometheus 指标端点"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

    logger.info("监控设置完成")


def record_blockchain_operation(operation: str, status: str) -> None:
    """记录区块链操作指标"""
    BLOCKCHAIN_OPERATIONS.labels(operation=operation, status=status).inc()


def record_database_operation(operation: str, status: str) -> None:
    """记录数据库操作指标"""
    DATABASE_OPERATIONS.labels(operation=operation, status=status).inc()


def record_grpc_request(method: str, status: str) -> None:
    """记录 gRPC 请求指标"""
    GRPC_REQUESTS.labels(method=method, status=status).inc()


# 健康检查
class HealthChecker:
    """健康检查器"""

    def __init__(self) -> None:
        self.checks: dict[str, Callable[[], bool]] = {}

    def add_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """添加健康检查"""
        self.checks[name] = check_func

    def get_health_status(self) -> dict[str, Any]:
        """获取健康状态"""
        status: dict[str, Any] = {"status": "healthy", "checks": {}}

        for name, check_func in self.checks.items():
            try:
                is_healthy = check_func()
                status["checks"][name] = {
                    "status": "healthy" if is_healthy else "unhealthy"
                }
                if not is_healthy:
                    status["status"] = "unhealthy"
            except Exception as e:
                status["checks"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                status["status"] = "unhealthy"

        return status


# 全局健康检查器
health_checker = HealthChecker()
