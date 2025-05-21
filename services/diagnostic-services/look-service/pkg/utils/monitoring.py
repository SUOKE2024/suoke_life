#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
监控工具模块

提供用于监控和追踪服务性能的工具，包括：
- 请求追踪
- 日志记录
- Prometheus指标收集
- 性能计时器
"""

import time
import functools
import uuid
from typing import Dict, Any, Callable, Optional, TypeVar, cast

import structlog
from prometheus_client import Counter, Histogram, Summary, Gauge

# 类型变量定义
F = TypeVar('F', bound=Callable[..., Any])

# 日志
logger = structlog.get_logger()

# 全局指标
REQUEST_COUNTER = Counter(
    'look_service_requests_total',
    'Total number of requests',
    ['method', 'status']
)

REQUEST_LATENCY = Histogram(
    'look_service_request_latency_seconds',
    'Request latency in seconds',
    ['method'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

ACTIVE_REQUESTS = Gauge(
    'look_service_active_requests',
    'Number of active requests',
    ['method']
)

IMAGE_SIZE_SUMMARY = Summary(
    'look_service_image_size_bytes',
    'Image size in bytes',
    ['analysis_type']
)

PROCESSING_ERRORS = Counter(
    'look_service_errors_total',
    'Processing errors by type',
    ['method', 'error_type']
)

MODEL_EXECUTION_TIME = Histogram(
    'look_service_model_execution_seconds',
    'Model execution time in seconds',
    ['model_name'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 10.0)
)

DATABASE_OPERATION_TIME = Histogram(
    'look_service_db_operation_seconds',
    'Database operation time in seconds',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
)


def trace_request(method_name: str) -> Callable[[F], F]:
    """
    请求追踪装饰器，用于跟踪API方法的执行
    
    记录请求的开始、结束时间，计算执行时间，并更新Prometheus指标。
    同时还提供请求的唯一ID，存储在结构化日志的上下文中。
    
    Args:
        method_name: API方法名
        
    Returns:
        装饰过的函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成请求ID
            request_id = str(uuid.uuid4())
            start_time = time.time()
            
            # 更新活跃请求计数
            ACTIVE_REQUESTS.labels(method=method_name).inc()
            
            # 提取调用上下文
            context = None
            request = None
            
            # 尝试获取gRPC上下文和请求
            if len(args) > 1:
                request = args[1]  # gRPC请求通常是第二个参数
                context = args[2] if len(args) > 2 else None  # gRPC上下文通常是第三个参数
            
            # 设置结构化日志上下文
            log = logger.bind(
                request_id=request_id,
                method=method_name
            )
            
            # 记录请求开始
            request_log = {"event": "request_start"}
            
            # 如果请求对象存在，尝试记录用户ID和其他元数据
            if request and hasattr(request, "user_id") and getattr(request, "user_id"):
                request_log["user_id"] = getattr(request, "user_id")
            
            log.info(**request_log)
            
            try:
                # 执行原始方法
                result = func(*args, **kwargs)
                
                # 记录成功请求
                REQUEST_COUNTER.labels(method=method_name, status="success").inc()
                
                # 返回结果
                return result
            except Exception as e:
                # 记录失败请求
                REQUEST_COUNTER.labels(method=method_name, status="error").inc()
                
                # 更新错误计数
                error_type = type(e).__name__
                PROCESSING_ERRORS.labels(method=method_name, error_type=error_type).inc()
                
                # 记录错误日志
                log.error(
                    "request_error",
                    error=str(e),
                    error_type=error_type
                )
                
                # 重新抛出异常
                raise
            finally:
                # 计算执行时间
                execution_time = time.time() - start_time
                
                # 更新延迟直方图
                REQUEST_LATENCY.labels(method=method_name).observe(execution_time)
                
                # 减少活跃请求计数
                ACTIVE_REQUESTS.labels(method=method_name).dec()
                
                # 记录请求结束
                log.info(
                    "request_end",
                    execution_time=execution_time
                )
                
                # 如果有gRPC上下文，添加跟踪元数据
                if context:
                    try:
                        context.set_trailing_metadata([
                            ('request-id', request_id),
                            ('execution-time', str(execution_time))
                        ])
                    except:
                        pass  # 忽略设置元数据的错误
        
        return cast(F, wrapper)
    return decorator


class PerformanceTimer:
    """
    性能计时器类，用于测量代码块的执行时间
    
    示例:
        with PerformanceTimer("preprocess_image") as timer:
            # 执行耗时操作
            processed_image = process_image(raw_image)
            
        # 计时结果已自动记录到日志和Prometheus
    """
    
    def __init__(self, operation_name: str, record_prometheus: bool = True,
                 metric: Optional[Histogram] = None, labels: Optional[Dict[str, str]] = None):
        """
        初始化计时器
        
        Args:
            operation_name: 操作名称，用于日志和指标标识
            record_prometheus: 是否记录到Prometheus指标
            metric: 自定义Prometheus指标，如果不提供则使用默认的REQUEST_LATENCY
            labels: Prometheus指标的标签值
        """
        self.operation_name = operation_name
        self.record_prometheus = record_prometheus
        self.metric = metric or REQUEST_LATENCY
        self.labels = labels or {}
        self.start_time = 0
        self.execution_time = 0
    
    def __enter__(self):
        """进入上下文"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        self.execution_time = time.time() - self.start_time
        
        # 记录到日志
        logger.debug(
            "performance_measurement",
            operation=self.operation_name,
            execution_time=self.execution_time
        )
        
        # 记录到Prometheus
        if self.record_prometheus:
            if self.operation_name.startswith("model:"):
                # 如果是模型操作，使用模型执行时间指标
                model_name = self.operation_name.split(":")[1]
                MODEL_EXECUTION_TIME.labels(model_name=model_name).observe(self.execution_time)
            elif self.operation_name.startswith("db:"):
                # 如果是数据库操作，使用数据库操作时间指标
                operation = self.operation_name.split(":")[1]
                DATABASE_OPERATION_TIME.labels(operation=operation).observe(self.execution_time)
            else:
                # 使用通用指标或提供的自定义指标
                if self.labels:
                    self.metric.labels(**self.labels).observe(self.execution_time)
                else:
                    self.metric.labels(method=self.operation_name).observe(self.execution_time)


def record_image_size(analysis_type: str, size_bytes: int) -> None:
    """
    记录图像大小指标
    
    Args:
        analysis_type: 分析类型 (e.g., "tongue", "face", "body")
        size_bytes: 图像大小，以字节为单位
    """
    IMAGE_SIZE_SUMMARY.labels(analysis_type=analysis_type).observe(size_bytes)


def track_model_execution(model_name: str) -> Callable[[F], F]:
    """
    跟踪模型执行时间的装饰器
    
    Args:
        model_name: 模型名称
        
    Returns:
        装饰过的函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceTimer(f"model:{model_name}"):
                return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator


def track_db_operation(operation: str) -> Callable[[F], F]:
    """
    跟踪数据库操作时间的装饰器
    
    Args:
        operation: 操作名称
        
    Returns:
        装饰过的函数
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceTimer(f"db:{operation}"):
                return func(*args, **kwargs)
        return cast(F, wrapper)
    return decorator 