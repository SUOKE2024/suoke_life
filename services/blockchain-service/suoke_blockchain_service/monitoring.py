"""
监控和指标收集模块

提供 Prometheus 指标和 OpenTelemetry 追踪功能。
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.grpc import (
    GrpcInstrumentorClient,
    GrpcInstrumentorServer,
)
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    Info,
    generate_latest,
)

from .config import settings
from .logging import logger

# Prometheus 指标
REQUEST_COUNT = Counter(
    "blockchain_service_requests_total",
    "区块链服务请求总数",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = Histogram(
    "blockchain_service_request_duration_seconds",
    "区块链服务请求持续时间",
    ["method", "endpoint"],
)

BLOCKCHAIN_OPERATIONS = Counter(
    "blockchain_service_blockchain_operations_total",
    "区块链操作总数",
    ["operation", "status"],
)

BLOCKCHAIN_OPERATION_DURATION = Histogram(
    "blockchain_service_blockchain_operation_duration_seconds",
    "区块链操作持续时间",
    ["operation"],
)

DATABASE_OPERATIONS = Counter(
    "blockchain_service_database_operations_total",
    "数据库操作总数",
    ["operation", "table", "status"],
)

SERVICE_INFO = Info(
    "blockchain_service_info",
    "区块链服务信息",
)


def setup_monitoring(app: FastAPI) -> None:
    """设置监控"""

    # 设置服务信息
    SERVICE_INFO.info({
        "version": settings.app_version,
        "environment": settings.environment,
    })

    # 设置 OpenTelemetry 追踪
    if settings.monitoring.enable_tracing:
        setup_tracing()

        # 自动仪表化
        FastAPIInstrumentor.instrument_app(app)
        GrpcInstrumentorServer().instrument()
        GrpcInstrumentorClient().instrument()
        SQLAlchemyInstrumentor().instrument()

    # 添加指标中间件
    if settings.monitoring.enable_metrics:
        app.middleware("http")(metrics_middleware)

        # 添加指标端点
        @app.get("/metrics")
        async def metrics():
            """Prometheus 指标端点"""
            return Response(
                generate_latest(),
                media_type=CONTENT_TYPE_LATEST,
            )


def setup_tracing() -> None:
    """设置 OpenTelemetry 追踪"""

    resource = Resource.create({
        "service.name": "blockchain-service",
        "service.version": settings.app_version,
        "service.environment": settings.environment,
    })

    provider = TracerProvider(resource=resource)

    if settings.monitoring.jaeger_endpoint:
        # 配置 OTLP 导出器
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.monitoring.jaeger_endpoint,
            insecure=True,
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(span_processor)

    trace.set_tracer_provider(provider)

    logger.info("OpenTelemetry 追踪已配置")


async def metrics_middleware(request: Request, call_next) -> Response:
    """指标收集中间件"""

    start_time = time.time()
    method = request.method
    path = request.url.path

    try:
        response = await call_next(request)
        status_code = response.status_code

        # 记录请求指标
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status_code=status_code,
        ).inc()

        REQUEST_DURATION.labels(
            method=method,
            endpoint=path,
        ).observe(time.time() - start_time)

        return response

    except Exception:
        # 记录错误指标
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status_code=500,
        ).inc()

        raise


class MetricsCollector:
    """指标收集器"""

    @staticmethod
    def record_blockchain_operation(
        operation: str,
        duration: float,
        status: str = "success",
    ) -> None:
        """记录区块链操作指标"""
        BLOCKCHAIN_OPERATIONS.labels(
            operation=operation,
            status=status,
        ).inc()

        BLOCKCHAIN_OPERATION_DURATION.labels(
            operation=operation,
        ).observe(duration)

    @staticmethod
    def record_database_operation(
        operation: str,
        table: str,
        status: str = "success",
    ) -> None:
        """记录数据库操作指标"""
        DATABASE_OPERATIONS.labels(
            operation=operation,
            table=table,
            status=status,
        ).inc()


# 全局指标收集器实例
metrics = MetricsCollector()
