#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
指标收集模块

为服务提供指标收集、导出和监控功能。
"""
import logging
from typing import Dict, Any

from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Info, Gauge
from prometheus_fastapi_instrumentator import Instrumentator


# 定义主要指标
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation", "table"]
)

AUTH_FAILURES = Counter(
    "auth_failures_total",
    "Total number of authentication failures",
    ["reason"]
)

ACTIVE_USERS = Gauge(
    "active_users",
    "Number of active users"
)

APP_INFO = Info(
    "auth_service_info", 
    "Information about the auth service"
)


def setup_metrics(app: FastAPI, version: str, labels: Dict[str, Any]) -> None:
    """
    设置指标收集
    
    Args:
        app: FastAPI应用实例
        version: 应用版本
        labels: 标签信息
    """
    logging.info("设置指标收集")
    
    # 设置应用信息
    label_dict = {"version": version}
    label_dict.update(labels)
    APP_INFO.info(label_dict)
    
    # 配置FastAPI指标收集器
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
    
    # 自定义指标中间件
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        response = await call_next(request)
        
        # 在真实项目中，这里可以添加自定义指标收集逻辑
        
        return response
    
    logging.info("指标收集设置完成")