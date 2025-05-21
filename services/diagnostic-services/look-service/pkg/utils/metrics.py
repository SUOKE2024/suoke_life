#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
指标监控工具
设置和记录服务性能指标
"""

import time
from typing import Callable, Dict, Optional

import structlog
from prometheus_client import Counter, Gauge, Histogram, Summary

logger = structlog.get_logger()

# 定义指标
REQUEST_COUNT = Counter(
    'look_service_request_total', 
    'Total number of requests processed',
    ['method', 'status']
)

REQUEST_LATENCY = Histogram(
    'look_service_request_latency_seconds', 
    'Request latency in seconds',
    ['method'],
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, 100.0, float("inf"))
)

ANALYSIS_LATENCY = Histogram(
    'look_service_analysis_latency_seconds', 
    'Analysis processing latency in seconds',
    ['analysis_type'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0, 60.0, float("inf"))
)

MODEL_LATENCY = Histogram(
    'look_service_model_latency_seconds', 
    'Model inference latency in seconds',
    ['model_name', 'operation'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, float("inf"))
)

ACTIVE_REQUESTS = Gauge(
    'look_service_active_requests',
    'Number of requests currently being processed',
    ['method']
)

SYSTEM_MEMORY = Gauge(
    'look_service_memory_usage_bytes',
    'Memory usage in bytes'
)

SYSTEM_CPU = Gauge(
    'look_service_cpu_usage_percent',
    'CPU usage percentage'
)

DB_OPERATION_LATENCY = Histogram(
    'look_service_db_operation_latency_seconds',
    'Database operation latency in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf"))
)

IMAGE_SIZE = Histogram(
    'look_service_image_size_bytes',
    'Size of processed images in bytes',
    ['analysis_type'],
    buckets=(10000, 50000, 100000, 500000, 1000000, 5000000, 10000000, float("inf"))
)

ANALYSIS_CONFIDENCE = Histogram(
    'look_service_analysis_confidence',
    'Confidence scores of analysis results',
    ['feature_type'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)


def setup_metrics(config: Dict):
    """
    设置度量指标
    
    Args:
        config: 配置字典
    """
    try:
        # 这里可以根据配置进行自定义指标设置
        logger.info("Metrics initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize metrics", error=str(e))
        raise


def timing_decorator(metric: Histogram):
    """
    计时装饰器，用于测量函数执行时间
    
    Args:
        metric: 要更新的度量指标
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable):
        def wrapped(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # 提取标签值（如果有的话）
            labels = {}
            if hasattr(func, 'metric_labels'):
                for label_name, arg_name in func.metric_labels.items():
                    if arg_name in kwargs:
                        labels[label_name] = kwargs[arg_name]
                    elif len(args) > arg_name:
                        labels[label_name] = args[arg_name]
            
            # 更新指标
            if labels:
                metric.labels(**labels).observe(duration)
            else:
                metric.observe(duration)
            
            return result
        return wrapped
    return decorator


def request_counter(func: Callable) -> Callable:
    """
    请求计数装饰器
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    def wrapped(*args, **kwargs):
        method_name = func.__name__
        ACTIVE_REQUESTS.labels(method=method_name).inc()
        try:
            result = func(*args, **kwargs)
            REQUEST_COUNT.labels(method=method_name, status="success").inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=method_name, status="error").inc()
            raise
        finally:
            ACTIVE_REQUESTS.labels(method=method_name).dec()
    return wrapped


def track_model_latency(model_name: str, operation: str):
    """
    记录模型延迟
    
    Args:
        model_name: 模型名称
        operation: 操作类型
        duration: 持续时间（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            MODEL_LATENCY.labels(model_name=model_name, operation=operation).observe(duration)
            return result
        return wrapper
    return decorator


def track_db_operation(operation: str):
    """
    记录数据库操作延迟
    
    Args:
        operation: 操作类型
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            DB_OPERATION_LATENCY.labels(operation=operation).observe(duration)
            return result
        return wrapper
    return decorator


def record_image_size(analysis_type: str, size_bytes: int):
    """
    记录图像大小
    
    Args:
        analysis_type: 分析类型
        size_bytes: 图像大小（字节）
    """
    IMAGE_SIZE.labels(analysis_type=analysis_type).observe(size_bytes)


def record_confidence_score(feature_type: str, confidence: float):
    """
    记录置信度分数
    
    Args:
        feature_type: 特征类型
        confidence: 置信度分数
    """
    ANALYSIS_CONFIDENCE.labels(feature_type=feature_type).observe(confidence) 