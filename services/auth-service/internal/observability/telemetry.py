#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
可观测性模块

提供分布式追踪、结构化日志和指标收集功能
"""
import logging
import os
import socket
import functools
import inspect
from typing import Any, Dict, Optional, Callable, TypeVar, cast

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

# 全局Tracer缓存
_tracer = None

def setup_telemetry(
    service_name: str, 
    service_version: str, 
    environment: str, 
    otlp_endpoint: Optional[str] = None
) -> None:
    """
    设置OpenTelemetry追踪
    
    参数:
        service_name: 服务名称
        service_version: 服务版本
        environment: 环境名称
        otlp_endpoint: OTLP导出端点(可选)
    """
    # 创建资源
    resource = Resource.create({
        "service.name": service_name,
        "service.version": service_version,
        "deployment.environment": environment,
        "host.name": socket.gethostname()
    })
    
    # 创建追踪提供者
    provider = TracerProvider(resource=resource)
    
    # 配置导出器
    # 开发环境添加控制台导出
    if environment.lower() == "development" or ENABLE_CONSOLE_EXPORT:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # 添加OTLP导出器(如果提供)
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # 设置全局Tracer提供者
    trace.set_tracer_provider(provider)


def create_tracer(module_name: str) -> trace.Tracer:
    """
    为指定模块创建Tracer
    
    参数:
        module_name: 模块名称
        
    返回:
        OpenTelemetry Tracer实例
    """
    return trace.get_tracer(module_name)


def get_tracer() -> trace.Tracer:
    """
    获取或创建默认Tracer
    
    返回:
        OpenTelemetry Tracer实例
    """
    global _tracer
    if _tracer is None:
        _tracer = create_tracer("auth_service")
    return _tracer


F = TypeVar('F', bound=Callable[..., Any])


def trace(operation_name: str) -> Callable[[F], F]:
    """
    用于追踪函数执行的装饰器
    
    参数:
        operation_name: 操作名称
    
    返回:
        装饰后的函数
    """
    def decorator(func: F) -> F:
        # 判断是异步函数还是同步函数
        is_async = inspect.iscoroutinefunction(func)
        
        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                tracer = get_tracer()
                with tracer.start_as_current_span(operation_name) as span:
                    # 添加函数参数作为Span属性
                    # 注意：这里应该过滤敏感信息
                    try:
                        span.set_attribute("function.name", func.__name__)
                        
                        # 异步执行原函数
                        return await func(*args, **kwargs)
                    except Exception as e:
                        # 记录异常
                        record_exception(e)
                        raise
            return cast(F, async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                tracer = get_tracer()
                with tracer.start_as_current_span(operation_name) as span:
                    # 添加函数参数作为Span属性
                    try:
                        span.set_attribute("function.name", func.__name__)
                        
                        # 执行原函数
                        return func(*args, **kwargs)
                    except Exception as e:
                        # 记录异常
                        record_exception(e)
                        raise
            return cast(F, sync_wrapper)
    return decorator


def record_exception(exception: Exception) -> None:
    """
    记录异常到当前span
    
    参数:
        exception: 要记录的异常
    """
    span = trace.get_current_span()
    span.record_exception(exception)
    span.set_attribute("error", True)
    span.set_attribute("error.message", str(exception))
    span.set_attribute("error.type", exception.__class__.__name__)


def add_span_attributes(attributes: Dict[str, Any]) -> None:
    """
    将属性添加到当前span
    
    参数:
        attributes: 要添加的属性字典
    """
    span = trace.get_current_span()
    for key, value in attributes.items():
        span.set_attribute(key, value)


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
    # 设置追踪
    setup_telemetry(
        service_name=SERVICE_NAME,
        service_version="0.1.0",
        environment=ENV,
        otlp_endpoint=OTLP_ENDPOINT if OTLP_ENDPOINT else None
    )
    
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