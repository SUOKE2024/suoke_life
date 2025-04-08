"""
OpenTelemetry 配置模块
用于配置及初始化OpenTelemetry的追踪和指标收集
"""

import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.semconv.resource import ResourceAttributes

# 自动检测的工具导入
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXInstrumentor
from opentelemetry.instrumentation.neo4j import Neo4jInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from loguru import logger


def setup_telemetry():
    """
    设置OpenTelemetry的追踪和指标收集
    """
    # 获取环境变量
    service_name = os.getenv("SERVICE_NAME", "rag-service")
    service_version = os.getenv("SERVICE_VERSION", "0.1.0")
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://jaeger-collector.observability:4317")
    
    # 配置资源
    resource = Resource.create({
        SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
        ResourceAttributes.SERVICE_NAMESPACE: "suoke-life",
        "service.instance.id": os.getenv("POD_NAME", "unknown")
    })
    
    # 配置追踪
    tracer_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    
    # 配置指标
    metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
    reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=15000)
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
    
    # 自动检测
    RequestsInstrumentor().instrument()
    HTTPXInstrumentor().instrument()
    LoggingInstrumentor().instrument()
    
    # 有条件地检测特定框架
    try:
        Neo4jInstrumentor().instrument()
    except Exception as e:
        logger.warning(f"Neo4j instrumentation failed: {e}")
    
    try:
        RedisInstrumentor().instrument()
    except Exception as e:
        logger.warning(f"Redis instrumentation failed: {e}")

    logger.info("OpenTelemetry instrumentation setup completed")
    return tracer_provider, meter_provider


def instrument_app(app, app_type="fastapi"):
    """
    为不同类型的应用程序添加检测
    
    Args:
        app: 应用程序实例
        app_type: 应用程序类型 ("fastapi" 或 "flask")
    """
    if app_type.lower() == "fastapi":
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI application instrumented")
    elif app_type.lower() == "flask":
        FlaskInstrumentor.instrument_app(app)
        logger.info("Flask application instrumented")
    else:
        logger.warning(f"Unsupported application type for instrumentation: {app_type}")