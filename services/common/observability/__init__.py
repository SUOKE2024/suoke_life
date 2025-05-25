#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可观测性模块
提供分布式追踪、指标收集、日志聚合等功能
"""

# 分布式追踪
from .tracing import (
    TracingService,
    SpanKind,
    TracingExporter,
    get_tracing_service,
    trace
)

# 指标收集
from .metrics import (
    MetricsCollector,
    MetricType,
    MetricConfig,
    MetricsMiddleware,
    get_metrics_collector,
    track_metrics
)

# 日志聚合
from .logging import (
    LogAggregator,
    LogContext,
    LogLevel,
    LogFormatter,
    JSONLogFormatter,
    StructuredLogFormatter,
    LogRouter,
    get_log_aggregator,
    setup_logging
)

__all__ = [
    # 分布式追踪
    'TracingService',
    'SpanKind',
    'TracingExporter',
    'get_tracing_service',
    'trace',
    
    # 指标收集
    'MetricsCollector',
    'MetricType',
    'MetricConfig',
    'MetricsMiddleware',
    'get_metrics_collector',
    'track_metrics',
    
    # 日志聚合
    'LogAggregator',
    'LogContext',
    'LogLevel',
    'LogFormatter',
    'JSONLogFormatter',
    'StructuredLogFormatter',
    'LogRouter',
    'get_log_aggregator',
    'setup_logging'
]