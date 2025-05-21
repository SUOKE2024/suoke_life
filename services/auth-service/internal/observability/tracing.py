#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分布式追踪模块

按照索克生活APP微服务可观测性指南实现标准的分布式追踪功能。
使用OpenTelemetry和Jaeger实现追踪。
"""
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.aiohttp import AioHttpClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

logger = logging.getLogger(__name__)

def setup_tracing(app: FastAPI, config: Dict[str, Any]) -> None:
    """
    设置分布式追踪
    
    Args:
        app: FastAPI应用实例
        config: 追踪配置
    """
    if not config.get("enabled", False):
        logger.info("追踪功能已禁用")
        return
    
    try:
        # 创建TracerProvider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
        
        # 创建Jaeger导出器
        jaeger_exporter = JaegerExporter(
            agent_host_name=config.get("jaeger_host", "localhost"),
            agent_port=int(config.get("jaeger_port", 6831)),
        )
        
        # 添加批处理器
        span_processor = BatchSpanProcessor(jaeger_exporter)
        provider.add_span_processor(span_processor)
        
        # 自动检测FastAPI和其他库
        FastAPIInstrumentor.instrument_app(app)
        AioHttpClientInstrumentor().instrument()
        AsyncPGInstrumentor().instrument()
        RedisInstrumentor().instrument()
        
        # 存储tracer到app状态
        tracer = trace.get_tracer("auth_service")
        app.state.tracer = tracer
        
        logger.info("分布式追踪设置完成")
    except Exception as e:
        logger.error(f"设置分布式追踪时出错: {str(e)}")

def get_tracer() -> trace.Tracer:
    """
    获取追踪器
    
    Returns:
        trace.Tracer: 追踪器实例
    """
    return trace.get_tracer("auth_service")

def extract_context_from_request(request: Request) -> Dict[str, str]:
    """
    从请求中提取追踪上下文
    
    Args:
        request: FastAPI请求对象
    
    Returns:
        Dict[str, str]: 追踪上下文
    """
    carrier = {}
    for key, value in request.headers.items():
        carrier[key] = value
    return carrier

def inject_context_to_headers(headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    将当前追踪上下文注入到HTTP头中
    
    Args:
        headers: 现有的HTTP头
    
    Returns:
        Dict[str, str]: 包含追踪上下文的HTTP头
    """
    if headers is None:
        headers = {}
    
    inject(headers)
    return headers

async def trace_auth_operation(operation_name: str, user_id: Optional[str] = None, extra_attrs: Optional[Dict[str, Any]] = None):
    """
    追踪认证操作的上下文管理器
    
    Args:
        operation_name: 操作名称
        user_id: 用户ID（可选）
        extra_attrs: 额外的属性（可选）
    
    Yields:
        trace.Span: 追踪span
    """
    tracer = get_tracer()
    
    with tracer.start_as_current_span(f"auth.{operation_name}") as span:
        # 添加基本属性
        span.set_attribute("service.name", "auth_service")
        span.set_attribute("operation", operation_name)
        
        # 添加用户ID（如果有）
        if user_id:
            span.set_attribute("user.id", user_id)
        
        # 添加额外属性（如果有）
        if extra_attrs:
            for key, value in extra_attrs.items():
                span.set_attribute(key, value)
        
        try:
            yield span
        except Exception as e:
            # 记录异常
            span.record_exception(e)
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.set_attribute("error.type", e.__class__.__name__)
            raise