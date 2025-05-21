#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集工具

提供用于收集和导出服务指标的功能，支持Prometheus监控集成。
"""
import os
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
from functools import wraps

# 配置日志
logger = logging.getLogger(__name__)

# 全局指标注册表
METRICS = {
    # API指标
    "api_requests_total": Counter(
        "soer_api_requests_total", 
        "API请求总数", 
        ["method", "endpoint", "status"]
    ),
    "api_request_duration_seconds": Histogram(
        "soer_api_request_duration_seconds", 
        "API请求持续时间（秒）",
        ["method", "endpoint"]
    ),
    
    # 服务指标
    "health_plan_generations_total": Counter(
        "soer_health_plan_generations_total", 
        "健康计划生成总数",
        ["constitution_type", "status"]
    ),
    "emotional_analyses_total": Counter(
        "soer_emotional_analyses_total", 
        "情绪分析总数",
        ["input_type", "status"]
    ),
    
    # 性能指标
    "function_execution_time_seconds": Histogram(
        "soer_function_execution_time_seconds", 
        "函数执行时间（秒）",
        ["function_name", "module"]
    ),
    
    # 资源指标
    "active_connections": Gauge(
        "soer_active_connections", 
        "当前活动连接数",
        ["connection_type"]
    ),
    "database_query_duration_seconds": Histogram(
        "soer_database_query_duration_seconds", 
        "数据库查询持续时间（秒）",
        ["query_type", "database"]
    ),
    
    # LLM调用指标
    "llm_api_calls_total": Counter(
        "soer_llm_api_calls_total", 
        "LLM API调用总数",
        ["model", "status"]
    ),
    "llm_api_duration_seconds": Histogram(
        "soer_llm_api_duration_seconds", 
        "LLM API调用持续时间（秒）",
        ["model"]
    ),
    "llm_token_usage": Counter(
        "soer_llm_token_usage", 
        "LLM令牌使用量",
        ["model", "token_type"]
    )
}

# HTTP服务器状态
_http_server_started = False
_http_server_lock = threading.Lock()


def initialize_metrics(config: Dict[str, Any]):
    """
    初始化指标收集
    
    Args:
        config: 指标收集配置
    """
    global _http_server_started
    
    try:
        # 获取指标服务器端口
        port = config.get("port", 9098)
        
        # 启动HTTP服务器（如果尚未启动）
        with _http_server_lock:
            if not _http_server_started:
                start_http_server(port)
                _http_server_started = True
                logger.info(f"Prometheus指标服务器已启动在端口 {port}")
    except Exception as e:
        logger.error(f"启动指标服务器失败: {str(e)}")


def track_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """
    记录API请求指标
    
    Args:
        method: HTTP方法
        endpoint: API端点
        status_code: HTTP状态码
        duration: 请求持续时间（秒）
    """
    try:
        METRICS["api_requests_total"].labels(
            method=method, 
            endpoint=endpoint, 
            status=str(status_code)
        ).inc()
        
        METRICS["api_request_duration_seconds"].labels(
            method=method, 
            endpoint=endpoint
        ).observe(duration)
    except Exception as e:
        logger.error(f"记录API请求指标失败: {str(e)}")


def track_health_plan_generation(constitution_type: str, status: str = "success"):
    """
    记录健康计划生成指标
    
    Args:
        constitution_type: 体质类型
        status: 生成状态 ("success" 或 "failure")
    """
    try:
        METRICS["health_plan_generations_total"].labels(
            constitution_type=constitution_type, 
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"记录健康计划生成指标失败: {str(e)}")


def track_emotional_analysis(input_type: str, status: str = "success"):
    """
    记录情绪分析指标
    
    Args:
        input_type: 输入类型 ("text", "voice", "physiological")
        status: 分析状态 ("success" 或 "failure")
    """
    try:
        METRICS["emotional_analyses_total"].labels(
            input_type=input_type, 
            status=status
        ).inc()
    except Exception as e:
        logger.error(f"记录情绪分析指标失败: {str(e)}")


def track_llm_api_call(model: str, duration: float, status: str = "success",
                        input_tokens: int = 0, output_tokens: int = 0):
    """
    记录LLM API调用指标
    
    Args:
        model: 模型名称
        duration: 调用持续时间（秒）
        status: 调用状态 ("success" 或 "failure")
        input_tokens: 输入令牌数量
        output_tokens: 输出令牌数量
    """
    try:
        METRICS["llm_api_calls_total"].labels(
            model=model, 
            status=status
        ).inc()
        
        METRICS["llm_api_duration_seconds"].labels(
            model=model
        ).observe(duration)
        
        METRICS["llm_token_usage"].labels(
            model=model, 
            token_type="input"
        ).inc(input_tokens)
        
        METRICS["llm_token_usage"].labels(
            model=model, 
            token_type="output"
        ).inc(output_tokens)
    except Exception as e:
        logger.error(f"记录LLM API调用指标失败: {str(e)}")


def track_database_query(query_type: str, database: str, duration: float):
    """
    记录数据库查询指标
    
    Args:
        query_type: 查询类型 ("select", "insert", "update", "delete")
        database: 数据库名称
        duration: 查询持续时间（秒）
    """
    try:
        METRICS["database_query_duration_seconds"].labels(
            query_type=query_type, 
            database=database
        ).observe(duration)
    except Exception as e:
        logger.error(f"记录数据库查询指标失败: {str(e)}")


def update_active_connections(connection_type: str, count: int):
    """
    更新活动连接计数
    
    Args:
        connection_type: 连接类型 ("grpc", "http", "database")
        count: 连接数量
    """
    try:
        METRICS["active_connections"].labels(
            connection_type=connection_type
        ).set(count)
    except Exception as e:
        logger.error(f"更新活动连接计数失败: {str(e)}")


def track_function_time(module: str = "unknown"):
    """
    函数执行时间跟踪装饰器
    
    Args:
        module: 模块名称
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                try:
                    METRICS["function_execution_time_seconds"].labels(
                        function_name=func.__name__, 
                        module=module
                    ).observe(duration)
                except Exception as e:
                    logger.error(f"记录函数执行时间指标失败: {str(e)}")
        return wrapper
    return decorator


def track_async_function_time(module: str = "unknown"):
    """
    异步函数执行时间跟踪装饰器
    
    Args:
        module: 模块名称
    
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                try:
                    METRICS["function_execution_time_seconds"].labels(
                        function_name=func.__name__, 
                        module=module
                    ).observe(duration)
                except Exception as e:
                    logger.error(f"记录异步函数执行时间指标失败: {str(e)}")
        return wrapper
    return decorator