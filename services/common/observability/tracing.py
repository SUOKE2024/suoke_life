#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布式追踪系统
基于OpenTelemetry实现的分布式链路追踪
支持Jaeger、Zipkin等后端，提供自动仪表化和手动追踪功能
"""

import functools
import asyncio
import logging
import time
import socket
import os
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

# OpenTelemetry imports
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient, GrpcInstrumentorServer
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace import Status, StatusCode
from opentelemetry.semconv.trace import SpanAttributes

logger = logging.getLogger(__name__)

@dataclass
class TracingConfig:
    """追踪配置"""
    service_name: str
    service_version: str = "1.0.0"
    environment: str = "development"
    jaeger_endpoint: str = "localhost:6831"
    zipkin_endpoint: str = "http://localhost:9411/api/v2/spans"
    sample_rate: float = 1.0
    enable_console_export: bool = False
    enable_auto_instrumentation: bool = True
    custom_attributes: Dict[str, str] = None

class TracingManager:
    """追踪管理器"""
    
    def __init__(self, config: TracingConfig):
        self.config = config
        self.tracer_provider = None
        self.tracer = None
        self._initialized = False
        
        # 初始化追踪
        self._initialize_tracing()
    
    def _initialize_tracing(self):
        """初始化追踪系统"""
        try:
            # 创建资源
            resource = Resource.create({
                "service.name": self.config.service_name,
                "service.version": self.config.service_version,
                "deployment.environment": self.config.environment,
                "host.name": socket.gethostname(),
                "process.pid": os.getpid(),
                **(self.config.custom_attributes or {})
            })
            
            # 设置追踪提供者
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # 配置导出器
            self._setup_exporters()
            
            # 设置全局传播器
            set_global_textmap(TraceContextTextMapPropagator())
            
            # 获取追踪器
            self.tracer = trace.get_tracer(
                self.config.service_name,
                self.config.service_version
            )
            
            # 自动仪表化
            if self.config.enable_auto_instrumentation:
                self._setup_auto_instrumentation()
            
            self._initialized = True
            logger.info(f"Tracing initialized for service: {self.config.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")
            raise
    
    def _setup_exporters(self):
        """设置导出器"""
        # Jaeger导出器
        if self.config.jaeger_endpoint:
            try:
                host, port = self.config.jaeger_endpoint.split(':')
                jaeger_exporter = JaegerExporter(
                    agent_host_name=host,
                    agent_port=int(port),
                )
                span_processor = BatchSpanProcessor(jaeger_exporter)
                self.tracer_provider.add_span_processor(span_processor)
                logger.info(f"Jaeger exporter configured: {self.config.jaeger_endpoint}")
            except Exception as e:
                logger.warning(f"Failed to configure Jaeger exporter: {e}")
        
        # Zipkin导出器
        if self.config.zipkin_endpoint:
            try:
                zipkin_exporter = ZipkinExporter(
                    endpoint=self.config.zipkin_endpoint
                )
                span_processor = BatchSpanProcessor(zipkin_exporter)
                self.tracer_provider.add_span_processor(span_processor)
                logger.info(f"Zipkin exporter configured: {self.config.zipkin_endpoint}")
            except Exception as e:
                logger.warning(f"Failed to configure Zipkin exporter: {e}")
        
        # 控制台导出器（用于调试）
        if self.config.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            self.tracer_provider.add_span_processor(span_processor)
            logger.info("Console exporter configured")
    
    def _setup_auto_instrumentation(self):
        """设置自动仪表化"""
        try:
            # FastAPI自动仪表化
            FastAPIInstrumentor.instrument()
            
            # HTTP请求自动仪表化
            RequestsInstrumentor.instrument()
            
            # Redis自动仪表化
            RedisInstrumentor.instrument()
            
            # gRPC自动仪表化
            GrpcInstrumentorClient().instrument()
            GrpcInstrumentorServer().instrument()
            
            # 数据库自动仪表化
            try:
                Psycopg2Instrumentor().instrument()
                SQLAlchemyInstrumentor().instrument()
            except ImportError:
                logger.debug("Database instrumentation skipped (dependencies not available)")
            
            logger.info("Auto-instrumentation configured")
            
        except Exception as e:
            logger.warning(f"Failed to configure auto-instrumentation: {e}")
    
    def trace_function(self, 
                      operation_name: str = None, 
                      attributes: Dict[str, Any] = None,
                      record_exception: bool = True):
        """函数追踪装饰器"""
        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self._initialized:
                    return await func(*args, **kwargs)
                
                span_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    try:
                        # 添加基本属性
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("function.module", func.__module__)
                        span.set_attribute("function.type", "async")
                        
                        # 添加自定义属性
                        if attributes:
                            for key, value in attributes.items():
                                span.set_attribute(key, str(value))
                        
                        # 添加函数参数（限制长度避免过大）
                        if args:
                            span.set_attribute("function.args.count", len(args))
                            span.set_attribute("function.args", str(args)[:500])
                        
                        if kwargs:
                            span.set_attribute("function.kwargs.count", len(kwargs))
                            span.set_attribute("function.kwargs", str(kwargs)[:500])
                        
                        # 执行函数
                        start_time = time.time()
                        result = await func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        
                        # 记录执行时间
                        span.set_attribute("function.execution_time", execution_time)
                        span.set_attribute("function.success", True)
                        
                        return result
                        
                    except Exception as e:
                        # 记录异常
                        span.set_attribute("function.success", False)
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        
                        if record_exception:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                        
                        raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self._initialized:
                    return func(*args, **kwargs)
                
                span_name = operation_name or f"{func.__module__}.{func.__name__}"
                
                with self.tracer.start_as_current_span(span_name) as span:
                    try:
                        # 添加基本属性
                        span.set_attribute("function.name", func.__name__)
                        span.set_attribute("function.module", func.__module__)
                        span.set_attribute("function.type", "sync")
                        
                        # 添加自定义属性
                        if attributes:
                            for key, value in attributes.items():
                                span.set_attribute(key, str(value))
                        
                        # 添加函数参数
                        if args:
                            span.set_attribute("function.args.count", len(args))
                            span.set_attribute("function.args", str(args)[:500])
                        
                        if kwargs:
                            span.set_attribute("function.kwargs.count", len(kwargs))
                            span.set_attribute("function.kwargs", str(kwargs)[:500])
                        
                        # 执行函数
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        execution_time = time.time() - start_time
                        
                        # 记录执行时间
                        span.set_attribute("function.execution_time", execution_time)
                        span.set_attribute("function.success", True)
                        
                        return result
                        
                    except Exception as e:
                        # 记录异常
                        span.set_attribute("function.success", False)
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        
                        if record_exception:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                        
                        raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    @contextmanager
    def trace_span(self, name: str, attributes: Dict[str, Any] = None):
        """创建手动span上下文管理器"""
        if not self._initialized:
            yield None
            return
        
        with self.tracer.start_as_current_span(name) as span:
            try:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                
                yield span
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise
    
    def create_span(self, name: str, attributes: Dict[str, Any] = None) -> Optional[trace.Span]:
        """创建新的span"""
        if not self._initialized:
            return None
        
        span = self.tracer.start_span(name)
        
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
        
        return span
    
    def get_current_span(self) -> Optional[trace.Span]:
        """获取当前span"""
        if not self._initialized:
            return None
        
        return trace.get_current_span()
    
    def get_trace_id(self) -> Optional[str]:
        """获取当前追踪ID"""
        span = self.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, '032x')
        return None
    
    def get_span_id(self) -> Optional[str]:
        """获取当前span ID"""
        span = self.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().span_id, '016x')
        return None
    
    def inject_context(self, headers: Dict[str, str]) -> Dict[str, str]:
        """注入追踪上下文到headers"""
        if not self._initialized:
            return headers
        
        from opentelemetry.propagators import inject
        inject(headers)
        return headers
    
    def extract_context(self, headers: Dict[str, str]):
        """从headers提取追踪上下文"""
        if not self._initialized:
            return None
        
        from opentelemetry.propagators import extract
        return extract(headers)
    
    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """添加事件到当前span"""
        span = self.get_current_span()
        if span:
            span.add_event(name, attributes or {})
    
    def set_attribute(self, key: str, value: Any):
        """设置当前span属性"""
        span = self.get_current_span()
        if span:
            span.set_attribute(key, str(value))
    
    def set_status(self, status_code: StatusCode, description: str = ""):
        """设置当前span状态"""
        span = self.get_current_span()
        if span:
            span.set_status(Status(status_code, description))
    
    def record_exception(self, exception: Exception):
        """记录异常到当前span"""
        span = self.get_current_span()
        if span:
            span.record_exception(exception)
    
    def shutdown(self):
        """关闭追踪系统"""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
        logger.info("Tracing system shutdown")

# 业务特定的追踪装饰器
class BusinessTracing:
    """业务追踪装饰器集合"""
    
    def __init__(self, tracing_manager: TracingManager):
        self.tracing = tracing_manager
    
    def trace_api_endpoint(self, endpoint_name: str = None):
        """API端点追踪"""
        def decorator(func):
            operation_name = endpoint_name or f"api.{func.__name__}"
            return self.tracing.trace_function(
                operation_name=operation_name,
                attributes={
                    "component": "api",
                    "api.endpoint": endpoint_name or func.__name__
                }
            )(func)
        return decorator
    
    def trace_database_operation(self, table_name: str = None, operation: str = None):
        """数据库操作追踪"""
        def decorator(func):
            operation_name = f"db.{operation or func.__name__}"
            attributes = {
                "component": "database",
                "db.operation": operation or func.__name__
            }
            if table_name:
                attributes["db.table"] = table_name
            
            return self.tracing.trace_function(
                operation_name=operation_name,
                attributes=attributes
            )(func)
        return decorator
    
    def trace_ai_inference(self, model_name: str = None, model_version: str = None):
        """AI推理追踪"""
        def decorator(func):
            operation_name = f"ai.inference.{func.__name__}"
            attributes = {
                "component": "ai",
                "ai.operation": "inference"
            }
            if model_name:
                attributes["ai.model.name"] = model_name
            if model_version:
                attributes["ai.model.version"] = model_version
            
            return self.tracing.trace_function(
                operation_name=operation_name,
                attributes=attributes
            )(func)
        return decorator
    
    def trace_external_service(self, service_name: str, operation: str = None):
        """外部服务调用追踪"""
        def decorator(func):
            operation_name = f"external.{service_name}.{operation or func.__name__}"
            return self.tracing.trace_function(
                operation_name=operation_name,
                attributes={
                    "component": "external_service",
                    "service.name": service_name,
                    "service.operation": operation or func.__name__
                }
            )(func)
        return decorator
    
    def trace_message_processing(self, message_type: str = None):
        """消息处理追踪"""
        def decorator(func):
            operation_name = f"message.process.{func.__name__}"
            attributes = {
                "component": "message_processor",
                "message.operation": "process"
            }
            if message_type:
                attributes["message.type"] = message_type
            
            return self.tracing.trace_function(
                operation_name=operation_name,
                attributes=attributes
            )(func)
        return decorator

# 全局追踪管理器
_tracing_manager = None
_business_tracing = None

def initialize_tracing(config: TracingConfig) -> TracingManager:
    """初始化全局追踪管理器"""
    global _tracing_manager, _business_tracing
    
    _tracing_manager = TracingManager(config)
    _business_tracing = BusinessTracing(_tracing_manager)
    
    return _tracing_manager

def get_tracing_manager() -> Optional[TracingManager]:
    """获取全局追踪管理器"""
    return _tracing_manager

def get_business_tracing() -> Optional[BusinessTracing]:
    """获取业务追踪装饰器"""
    return _business_tracing

# 便捷函数
def trace_function(operation_name: str = None, attributes: Dict[str, Any] = None):
    """函数追踪装饰器（便捷函数）"""
    if _tracing_manager:
        return _tracing_manager.trace_function(operation_name, attributes)
    else:
        # 如果追踪未初始化，返回空装饰器
        def decorator(func):
            return func
        return decorator

def trace_span(name: str, attributes: Dict[str, Any] = None):
    """创建追踪span（便捷函数）"""
    if _tracing_manager:
        return _tracing_manager.trace_span(name, attributes)
    else:
        @contextmanager
        def dummy_span():
            yield None
        return dummy_span()

# 使用示例
if __name__ == "__main__":
    # 配置追踪
    config = TracingConfig(
        service_name="xiaoai-service",
        service_version="1.0.0",
        environment="development",
        jaeger_endpoint="localhost:6831",
        enable_console_export=True
    )
    
    # 初始化追踪
    tracing = initialize_tracing(config)
    business = get_business_tracing()
    
    # 使用装饰器
    @business.trace_ai_inference("tcm_diagnosis", "v2.1.0")
    async def analyze_symptoms(symptoms: List[str]) -> Dict[str, Any]:
        """分析症状"""
        with trace_span("preprocess_symptoms") as span:
            if span:
                span.set_attribute("symptoms.count", len(symptoms))
            
            # 预处理症状
            processed_symptoms = [s.lower().strip() for s in symptoms]
        
        with trace_span("ai_inference") as span:
            if span:
                span.set_attribute("model.input_size", len(processed_symptoms))
            
            # 模拟AI推理
            await asyncio.sleep(0.1)
            result = {
                "diagnosis": "气虚",
                "confidence": 0.85,
                "recommendations": ["补气", "调理脾胃"]
            }
            
            if span:
                span.set_attribute("model.output.diagnosis", result["diagnosis"])
                span.set_attribute("model.output.confidence", result["confidence"])
        
        return result
    
    @business.trace_database_operation("health_records", "insert")
    async def save_health_record(user_id: str, data: Dict[str, Any]) -> bool:
        """保存健康记录"""
        # 模拟数据库操作
        await asyncio.sleep(0.05)
        return True
    
    @business.trace_api_endpoint("health_analysis")
    async def health_analysis_endpoint(user_id: str, symptoms: List[str]):
        """健康分析API端点"""
        # 分析症状
        diagnosis_result = await analyze_symptoms(symptoms)
        
        # 保存记录
        await save_health_record(user_id, {
            "symptoms": symptoms,
            "diagnosis": diagnosis_result
        })
        
        return {
            "user_id": user_id,
            "result": diagnosis_result,
            "trace_id": tracing.get_trace_id()
        }
    
    # 运行示例
    async def main():
        result = await health_analysis_endpoint(
            "user123", 
            ["头痛", "乏力", "食欲不振"]
        )
        print(f"Analysis result: {result}")
    
    # 运行
    asyncio.run(main())
    
    # 关闭追踪
    tracing.shutdown() 