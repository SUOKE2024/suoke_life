#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控和指标收集工具
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class MetricEntry:
    """指标条目"""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_entries))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = threading.RLock()
        
        # 性能统计
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.start_time = time.time()
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """增加计数器"""
        with self.lock:
            self.counters[name] += value
            self._add_metric(name, value, tags or {})
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """设置仪表值"""
        with self.lock:
            self.gauges[name] = value
            self._add_metric(name, value, tags or {})
    
    def record_timer(self, name: str, duration: float, tags: Dict[str, str] = None):
        """记录计时器"""
        with self.lock:
            self.timers[name].append(duration)
            # 保持最近1000个记录
            if len(self.timers[name]) > 1000:
                self.timers[name] = self.timers[name][-1000:]
            self._add_metric(name, duration, tags or {})
    
    def _add_metric(self, name: str, value: float, tags: Dict[str, str]):
        """添加指标"""
        entry = MetricEntry(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags
        )
        self.metrics[name].append(entry)
    
    def get_counter(self, name: str) -> float:
        """获取计数器值"""
        with self.lock:
            return self.counters.get(name, 0.0)
    
    def get_gauge(self, name: str) -> float:
        """获取仪表值"""
        with self.lock:
            return self.gauges.get(name, 0.0)
    
    def get_timer_stats(self, name: str) -> Dict[str, float]:
        """获取计时器统计"""
        with self.lock:
            values = self.timers.get(name, [])
            if not values:
                return {}
            
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            return {
                "count": count,
                "min": min(sorted_values),
                "max": max(sorted_values),
                "avg": sum(sorted_values) / count,
                "p50": sorted_values[int(count * 0.5)],
                "p90": sorted_values[int(count * 0.9)],
                "p95": sorted_values[int(count * 0.95)],
                "p99": sorted_values[int(count * 0.99)]
            }
    
    def record_request(self, response_time: float, success: bool = True):
        """记录请求"""
        with self.lock:
            self.request_count += 1
            self.total_response_time += response_time
            
            if not success:
                self.error_count += 1
            
            self.record_timer("request_duration", response_time)
            self.increment_counter("requests_total")
            
            if not success:
                self.increment_counter("errors_total")
    
    def get_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self.lock:
            uptime = time.time() - self.start_time
            avg_response_time = (self.total_response_time / self.request_count 
                               if self.request_count > 0 else 0.0)
            error_rate = (self.error_count / self.request_count 
                         if self.request_count > 0 else 0.0)
            
            return {
                "uptime_seconds": uptime,
                "requests_total": self.request_count,
                "errors_total": self.error_count,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "timer_stats": {
                    name: self.get_timer_stats(name) 
                    for name in self.timers.keys()
                }
            }
    
    def reset(self):
        """重置所有指标"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.timers.clear()
            self.request_count = 0
            self.error_count = 0
            self.total_response_time = 0.0
            self.start_time = time.time()
    
    # 为 AgentManager 添加的专用方法
    def update_active_sessions(self, count: int):
        """更新活跃会话数"""
        self.set_gauge("active_sessions", float(count))
    
    def increment_chat_message_count(self, direction: str, message_type: str):
        """增加聊天消息计数"""
        tags = {"direction": direction, "type": message_type}
        self.increment_counter("chat_messages_total", 1.0, tags)
    
    def increment_session_count(self, action: str):
        """增加会话计数"""
        tags = {"action": action}
        self.increment_counter("sessions_total", 1.0, tags)
    
    def track_multimodal_process(self, input_type: str, status: str, latency: float, input_size: int):
        """跟踪多模态处理指标"""
        tags = {"input_type": input_type, "status": status}
        self.increment_counter("multimodal_processes_total", 1.0, tags)
        self.record_timer("multimodal_process_duration", latency, tags)
        self.set_gauge("multimodal_input_size_bytes", float(input_size), tags)
    
    def increment_active_requests(self, endpoint: str):
        """增加活跃请求数"""
        tags = {"endpoint": endpoint}
        self.increment_counter("active_requests", 1.0, tags)
        current_active = self.get_gauge(f"active_requests_{endpoint}")
        self.set_gauge(f"active_requests_{endpoint}", current_active + 1)
    
    def decrement_active_requests(self, endpoint: str):
        """减少活跃请求数"""
        tags = {"endpoint": endpoint}
        self.increment_counter("active_requests", -1.0, tags)
        current_active = self.get_gauge(f"active_requests_{endpoint}")
        self.set_gauge(f"active_requests_{endpoint}", max(0, current_active - 1))
    
    def track_request(self, protocol: str, endpoint: str, status_code: int, latency: float):
        """跟踪请求指标"""
        tags = {"protocol": protocol, "endpoint": endpoint, "status": str(status_code)}
        self.increment_counter("requests_total", 1.0, tags)
        self.record_timer("request_duration", latency, tags)
        
        if status_code >= 400:
            self.increment_counter("errors_total", 1.0, tags)

class PerformanceTimer:
    """性能计时器上下文管理器"""
    
    def __init__(self, metrics_collector: MetricsCollector, name: str, tags: Dict[str, str] = None):
        self.metrics_collector = metrics_collector
        self.name = name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_timer(self.name, duration, self.tags)
            
            # 记录成功/失败
            success = exc_type is None
            self.metrics_collector.record_request(duration, success)

class AsyncPerformanceTimer:
    """异步性能计时器"""
    
    def __init__(self, metrics_collector: MetricsCollector, name: str, tags: Dict[str, str] = None):
        self.metrics_collector = metrics_collector
        self.name = name
        self.tags = tags or {}
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.record_timer(self.name, duration, self.tags)
            
            # 记录成功/失败
            success = exc_type is None
            self.metrics_collector.record_request(duration, success)

# 全局指标收集器
_global_metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """获取全局指标收集器"""
    global _global_metrics_collector
    if _global_metrics_collector is None:
        _global_metrics_collector = MetricsCollector()
    return _global_metrics_collector

def timer(name: str, tags: Dict[str, str] = None) -> PerformanceTimer:
    """创建性能计时器"""
    return PerformanceTimer(get_metrics_collector(), name, tags)

def async_timer(name: str, tags: Dict[str, str] = None) -> AsyncPerformanceTimer:
    """创建异步性能计时器"""
    return AsyncPerformanceTimer(get_metrics_collector(), name, tags)

def increment(name: str, value: float = 1.0, tags: Dict[str, str] = None):
    """增加计数器"""
    get_metrics_collector().increment_counter(name, value, tags)

def gauge(name: str, value: float, tags: Dict[str, str] = None):
    """设置仪表值"""
    get_metrics_collector().set_gauge(name, value, tags)

def record_time(name: str, duration: float, tags: Dict[str, str] = None):
    """记录时间"""
    get_metrics_collector().record_timer(name, duration, tags)

def track_db_metrics(db_type: str = None, operation: str = None, table: str = None):
    """跟踪数据库操作指标装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                
                # 构建标签
                tags = {}
                if db_type:
                    tags["db_type"] = db_type
                if operation:
                    tags["operation"] = operation
                if table:
                    tags["table"] = table
                
                # 记录指标
                increment("db_operations_total", 1.0, tags)
                record_time("db_operation_duration", duration, tags)
                
                if success:
                    increment("db_operations_success_total", 1.0, tags)
                else:
                    increment("db_operations_error_total", 1.0, tags)
                
                logger.debug(f"数据库操作指标记录: {db_type} {operation} on {table}, 成功: {success}, 耗时: {duration:.3f}s")
        
        return wrapper
    return decorator

def track_api_metrics(endpoint: str, method: str, status_code: int, duration: float):
    """跟踪API请求指标"""
    tags = {
        "endpoint": endpoint,
        "method": method,
        "status_code": str(status_code)
    }
    
    # 增加API请求计数
    increment("api_requests_total", 1.0, tags)
    
    # 记录响应时间
    record_time("api_request_duration", duration, tags)
    
    # 记录错误
    if status_code >= 400:
        increment("api_errors_total", 1.0, tags)
    
    logger.debug(f"API指标记录: {method} {endpoint}, 状态码: {status_code}, 耗时: {duration}s")

def track_cache_metrics(operation: str, hit: bool = None, size: int = None):
    """跟踪缓存操作指标"""
    tags = {"operation": operation}
    
    # 增加缓存操作计数
    increment("cache_operations_total", 1.0, tags)
    
    # 记录缓存命中/未命中
    if hit is not None:
        if hit:
            increment("cache_hits_total", 1.0, tags)
        else:
            increment("cache_misses_total", 1.0, tags)
    
    # 记录缓存大小
    if size is not None:
        gauge("cache_size_bytes", float(size), tags)
    
    logger.debug(f"缓存指标记录: {operation}, 命中: {hit}, 大小: {size}")

def track_device_metrics(device_type: str, operation: str, success: bool, duration: float = None):
    """跟踪设备操作指标"""
    tags = {
        "device_type": device_type,
        "operation": operation,
        "success": str(success)
    }
    
    # 增加设备操作计数
    increment("device_operations_total", 1.0, tags)
    
    # 记录成功/失败
    if success:
        increment("device_operations_success_total", 1.0, tags)
    else:
        increment("device_operations_error_total", 1.0, tags)
    
    # 记录操作时间
    if duration is not None:
        record_time("device_operation_duration", duration, tags)
    
    logger.debug(f"设备指标记录: {device_type} {operation}, 成功: {success}, 耗时: {duration}s")

def track_agent_metrics(agent_name: str, action: str, success: bool, duration: float = None):
    """跟踪智能体操作指标"""
    tags = {
        "agent": agent_name,
        "action": action,
        "success": str(success)
    }
    
    # 增加智能体操作计数
    increment("agent_operations_total", 1.0, tags)
    
    # 记录成功/失败
    if success:
        increment("agent_operations_success_total", 1.0, tags)
    else:
        increment("agent_operations_error_total", 1.0, tags)
    
    # 记录操作时间
    if duration is not None:
        record_time("agent_operation_duration", duration, tags)
    
    logger.debug(f"智能体指标记录: {agent_name} {action}, 成功: {success}, 耗时: {duration}s")

def track_llm_metrics(model: str = None, model_name: str = None, operation: str = None, query_type: str = None, tokens: int = None):
    """跟踪大语言模型操作指标装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                
                # 构建标签
                tags = {}
                # 支持多种参数名
                model_value = model or model_name
                operation_value = operation or query_type
                
                if model_value:
                    tags["model"] = model_value
                if operation_value:
                    tags["operation"] = operation_value
                
                # 记录指标
                increment("llm_operations_total", 1.0, tags)
                record_time("llm_operation_duration", duration, tags)
                
                if tokens:
                    increment("llm_tokens_total", float(tokens), tags)
                    gauge("llm_tokens_per_second", float(tokens) / duration if duration > 0 else 0, tags)
                
                if success:
                    increment("llm_operations_success_total", 1.0, tags)
                else:
                    increment("llm_operations_error_total", 1.0, tags)
                
                logger.debug(f"LLM指标记录: {model_value} {operation_value}, 成功: {success}, 耗时: {duration:.3f}s, tokens: {tokens}")
        
        return wrapper
    return decorator

def track_service_call_metrics(service: str, method: str = None):
    """跟踪服务调用指标的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_type = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
            finally:
                duration = time.time() - start_time
                
                # 记录指标
                collector = get_metrics_collector()
                tags = {
                    "service": service,
                    "method": method or func.__name__,
                    "success": str(success).lower()
                }
                
                if error_type:
                    tags["error_type"] = error_type
                
                collector.record_timer(f"service_call_duration", duration, tags)
                collector.increment_counter(f"service_calls_total", 1.0, tags)
                
                if not success:
                    collector.increment_counter(f"service_call_errors_total", 1.0, tags)
                
                logger.debug(f"服务调用指标记录: {service}.{method or func.__name__}, 成功: {success}, 耗时: {duration:.3f}s")
        
        return wrapper
    return decorator

def track_request_metrics(endpoint: str = None, method: str = None):
    """跟踪请求指标的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_type = None
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                status_code = 500
                raise
            finally:
                duration = time.time() - start_time
                
                # 记录指标
                collector = get_metrics_collector()
                tags = {
                    "endpoint": endpoint or func.__name__,
                    "method": method or "unknown",
                    "status_code": str(status_code),
                    "success": str(success).lower()
                }
                
                if error_type:
                    tags["error_type"] = error_type
                
                collector.record_timer(f"request_duration", duration, tags)
                collector.increment_counter(f"requests_total", 1.0, tags)
                
                if not success:
                    collector.increment_counter(f"request_errors_total", 1.0, tags)
                
                logger.debug(f"请求指标记录: {method} {endpoint}, 状态码: {status_code}, 耗时: {duration:.3f}s")
        
        return wrapper
    return decorator

# 为 AgentManager 添加的专用指标方法
def update_active_sessions(count: int):
    """更新活跃会话数"""
    gauge("active_sessions", float(count))

def increment_chat_message_count(direction: str, message_type: str):
    """增加聊天消息计数"""
    tags = {"direction": direction, "type": message_type}
    increment("chat_messages_total", 1.0, tags)

def increment_session_count(action: str):
    """增加会话计数"""
    tags = {"action": action}
    increment("sessions_total", 1.0, tags)

def track_multimodal_process(input_type: str, status: str, latency: float, input_size: int):
    """跟踪多模态处理指标"""
    tags = {"input_type": input_type, "status": status}
    increment("multimodal_processes_total", 1.0, tags)
    record_time("multimodal_process_duration", latency, tags)
    gauge("multimodal_input_size_bytes", float(input_size), tags) 