#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, Callable, Generator
import functools

# 模拟 OpenTelemetry 依赖，实际使用时需要安装相关包
try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from prometheus_client import start_http_server
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

logger = logging.getLogger(__name__)


def setup_tracing(config):
    """
    设置分布式追踪
    
    Args:
        config: 追踪配置
    """
    if not OPENTELEMETRY_AVAILABLE:
        logger.warning("OpenTelemetry packages not available, tracing disabled")
        return
    
    if not config.enabled:
        logger.info("Tracing is disabled in configuration")
        return
    
    try:
        # 创建追踪提供程序
        provider = TracerProvider()
        
        # 根据配置创建导出器
        if config.exporter.lower() == "jaeger":
            exporter = JaegerExporter(
                agent_host_name=config.jaeger.endpoint.split(":")[0],
                agent_port=int(config.jaeger.endpoint.split(":")[1]) if ":" in config.jaeger.endpoint else 6831
            )
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        
        # 设置全局追踪提供程序
        trace.set_tracer_provider(provider)
        
        logger.info(f"Tracing initialized with {config.exporter} exporter")
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {str(e)}")


def setup_metrics(config):
    """
    设置指标监控
    
    Args:
        config: 指标配置
    """
    if not OPENTELEMETRY_AVAILABLE:
        logger.warning("OpenTelemetry packages not available, metrics disabled")
        return
    
    if not config.enabled:
        logger.info("Metrics is disabled in configuration")
        return
    
    try:
        # 创建指标读取器
        readers = []
        
        if config.exporter.lower() == "prometheus":
            # 启动Prometheus HTTP服务器
            start_http_server(config.prometheus.port)
            readers.append(PrometheusMetricReader())
            logger.info(f"Prometheus metrics server started on port {config.prometheus.port}")
        
        # 创建指标提供程序
        provider = MeterProvider(metric_readers=readers)
        
        # 设置全局指标提供程序
        metrics.set_meter_provider(provider)
        
        logger.info(f"Metrics initialized with {config.exporter} exporter")
    except Exception as e:
        logger.error(f"Failed to initialize metrics: {str(e)}")


@contextmanager
def trace_span(name: str, attributes: Optional[Dict[str, Any]] = None) -> Generator[None, None, None]:
    """
    创建追踪span的上下文管理器
    
    Args:
        name: span名称
        attributes: span属性
    
    Yields:
        无
    """
    if not OPENTELEMETRY_AVAILABLE:
        # 如果OpenTelemetry不可用，简单地产生并返回
        yield
        return
    
    # 获取当前的追踪器
    tracer = trace.get_tracer(__name__)
    
    # 创建span
    with tracer.start_as_current_span(name, attributes=attributes or {}):
        yield


def trace_method(func: Callable) -> Callable:
    """
    用于追踪方法执行的装饰器
    
    Args:
        func: 要追踪的方法
    
    Returns:
        Callable: 装饰后的方法
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取方法名称
        name = f"{func.__module__}.{func.__qualname__}"
        
        # 使用追踪span
        with trace_span(name):
            return func(*args, **kwargs)
    
    return wrapper


@contextmanager
def measure_time(name: str, logger_func: Optional[Callable] = None) -> Generator[None, None, None]:
    """
    测量操作执行时间的上下文管理器
    
    Args:
        name: 操作名称
        logger_func: 用于记录日志的函数，默认为logger.info
    
    Yields:
        无
    """
    if logger_func is None:
        logger_func = logger.info
    
    start_time = time.time()
    try:
        yield
    finally:
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        logger_func(f"{name} completed in {duration_ms:.2f}ms")


def time_method(func: Callable) -> Callable:
    """
    用于测量方法执行时间的装饰器
    
    Args:
        func: 要测量的方法
    
    Returns:
        Callable: 装饰后的方法
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取方法名称
        name = f"{func.__module__}.{func.__qualname__}"
        
        # 使用时间测量
        with measure_time(name):
            return func(*args, **kwargs)
    
    return wrapper 