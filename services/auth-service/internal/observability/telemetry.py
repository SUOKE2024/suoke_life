#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可观测性模块

提供分布式追踪、结构化日志和指标收集功能
"""
import logging
import os
import socket
from typing import Any, Dict, Optional

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_client import Counter, Histogram

# 获取环境变量
SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")
ENV = os.getenv("ENV", "development")
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_CONSOLE_EXPORT = os.getenv("ENABLE_CONSOLE_EXPORT", "true").lower() == "true"

# 定义性能指标
REQUEST_COUNT = Counter(
    "auth_request_total",
    "认证服务请求总数",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "auth_request_latency_seconds",
    "认证服务请求延迟(秒)",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

AUTH_ATTEMPT_COUNT = Counter(
    "auth_attempt_total",
    "认证尝试总数",
    ["method", "status"]
)

TOKEN_OPERATION_COUNT = Counter(
    "auth_token_operation_total",
    "令牌操作总数",
    ["operation", "status"]
)

USER_OPERATION_COUNT = Counter(
    "auth_user_operation_total",
    "用户操作总数",
    ["operation", "status"]
)


def configure_tracer() -> None:
    """配置分布式追踪器
    
    设置OpenTelemetry追踪器提供者和导出器
    """
    # 创建资源
    resource = Resource.create({
        "service.name": SERVICE_NAME,
        "service.namespace": "suoke",
        "service.instance.id": socket.gethostname(),
        "deployment.environment": ENV
    })
    
    # 创建追踪器提供者
    tracer_provider = TracerProvider(resource=resource)
    
    # 添加控制台导出器(开发环境)
    if ENABLE_CONSOLE_EXPORT:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )
    
    # 添加OTLP导出器(如果配置了端点)
    if OTLP_ENDPOINT:
        otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT)
        tracer_provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
    
    # 设置全局追踪器提供者
    trace.set_tracer_provider(tracer_provider)
    
    # 获取追踪器
    return trace.get_tracer(__name__, "0.1.0")


def configure_logging() -> None:
    """配置结构化日志
    
    设置structlog处理器和格式化器
    """
    # 设置时间戳处理器
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    
    # 开发环境使用漂亮的控制台输出
    if ENV == "development":
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ]
    # 生产环境使用JSON格式
    else:
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ]
    
    # 配置structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 设置Python标准库日志级别
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, LOG_LEVEL)
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取命名日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        绑定了上下文的结构化日志记录器
    """
    return structlog.stdlib.get_logger(name)


def instrument_app(app: Any, engine: Optional[Any] = None, redis_client: Optional[Any] = None) -> None:
    """为应用程序添加检测
    
    为FastAPI、SQLAlchemy和Redis添加OpenTelemetry检测
    
    Args:
        app: FastAPI应用程序实例
        engine: SQLAlchemy引擎实例
        redis_client: Redis客户端实例
    """
    # 检测FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # 检测SQLAlchemy(如果提供)
    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    
    # 检测Redis(如果提供)
    if redis_client:
        RedisInstrumentor().instrument()


def initialize_telemetry(app: Any = None, engine: Optional[Any] = None, redis_client: Optional[Any] = None) -> None:
    """初始化所有遥测功能
    
    一次性配置所有可观测性组件
    
    Args:
        app: FastAPI应用程序实例
        engine: SQLAlchemy引擎实例
        redis_client: Redis客户端实例
    """
    # 配置追踪器
    configure_tracer()
    
    # 配置日志
    configure_logging()
    
    # 如果提供了应用程序，添加检测
    if app:
        instrument_app(app, engine, redis_client)
    
    logger = get_logger(__name__)
    logger.info(
        "遥测系统初始化完成",
        service=SERVICE_NAME,
        environment=ENV,
        log_level=LOG_LEVEL,
        otlp_endpoint=OTLP_ENDPOINT or "未配置"
    ) 