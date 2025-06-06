"""
metrics - 索克生活项目模块
"""

        import platform
        import sys
from ..core.logging import get_logger
from collections import defaultdict, deque
from prometheus_client import (
from threading import Lock
from typing import Dict, List, Optional, Set
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
指标收集和监控模块

实现 Prometheus 指标导出和自定义指标收集。
"""


    Counter, Histogram, Gauge, Info, Enum,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
)


logger = get_logger(__name__)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        初始化指标收集器
        
        Args:
            registry: Prometheus 注册表，如果为 None 则使用默认注册表
        """
        self.registry = registry
        self._lock = Lock()
        
        # 请求相关指标
        self.request_total = Counter(
            'gateway_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status_code'],
            registry=registry
        )
        
        self.request_duration = Histogram(
            'gateway_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=registry
        )
        
        self.request_size = Histogram(
            'gateway_request_size_bytes',
            'Request size in bytes',
            ['method', 'endpoint'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576],
            registry=registry
        )
        
        self.response_size = Histogram(
            'gateway_response_size_bytes',
            'Response size in bytes',
            ['method', 'endpoint'],
            buckets=[64, 256, 1024, 4096, 16384, 65536, 262144, 1048576],
            registry=registry
        )
        
        # 后端服务相关指标
        self.backend_requests_total = Counter(
            'gateway_backend_requests_total',
            'Total number of backend requests',
            ['service', 'method', 'status_code'],
            registry=registry
        )
        
        self.backend_request_duration = Histogram(
            'gateway_backend_request_duration_seconds',
            'Backend request duration in seconds',
            ['service', 'method'],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=registry
        )
        
        # 缓存相关指标
        self.cache_operations_total = Counter(
            'gateway_cache_operations_total',
            'Total number of cache operations',
            ['operation', 'result'],
            registry=registry
        )
        
        self.cache_hit_ratio = Gauge(
            'gateway_cache_hit_ratio',
            'Cache hit ratio',
            registry=registry
        )
        
        # 限流相关指标
        self.rate_limit_total = Counter(
            'gateway_rate_limit_total',
            'Total number of rate limit checks',
            ['result'],
            registry=registry
        )
        
        # 熔断器相关指标
        self.circuit_breaker_state = Enum(
            'gateway_circuit_breaker_state',
            'Circuit breaker state',
            ['service'],
            states=['closed', 'open', 'half_open'],
            registry=registry
        )
        
        self.circuit_breaker_failures = Counter(
            'gateway_circuit_breaker_failures_total',
            'Total number of circuit breaker failures',
            ['service'],
            registry=registry
        )
        
        # 连接池相关指标
        self.connection_pool_active = Gauge(
            'gateway_connection_pool_active',
            'Number of active connections in pool',
            ['pool'],
            registry=registry
        )
        
        self.connection_pool_idle = Gauge(
            'gateway_connection_pool_idle',
            'Number of idle connections in pool',
            ['pool'],
            registry=registry
        )
        
        # 系统相关指标
        self.system_info = Info(
            'gateway_system_info',
            'System information',
            registry=registry
        )
        
        self.active_connections = Gauge(
            'gateway_active_connections',
            'Number of active connections',
            registry=registry
        )
        
        # 内部统计
        self._cache_stats = {
            'hits': 0,
            'misses': 0,
            'total': 0
        }
        
        # 响应时间统计（用于计算 P95, P99 等）
        self._response_times = defaultdict(lambda: deque(maxlen=1000))
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """记录请求指标"""
        with self._lock:
            # 记录基本指标
            self.request_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            if request_size > 0:
                self.request_size.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(request_size)
            
            if response_size > 0:
                self.response_size.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            # 记录响应时间用于统计
            key = f"{method}:{endpoint}"
            self._response_times[key].append(duration)
    
    def record_backend_request(
        self,
        service: str,
        method: str,
        status_code: int,
        duration: float,
    ) -> None:
        """记录后端请求指标"""
        self.backend_requests_total.labels(
            service=service,
            method=method,
            status_code=str(status_code)
        ).inc()
        
        self.backend_request_duration.labels(
            service=service,
            method=method
        ).observe(duration)
    
    def record_cache_operation(self, operation: str, result: str) -> None:
        """记录缓存操作指标"""
        self.cache_operations_total.labels(
            operation=operation,
            result=result
        ).inc()
        
        # 更新缓存统计
        with self._lock:
            if operation == 'get':
                self._cache_stats['total'] += 1
                if result == 'hit':
                    self._cache_stats['hits'] += 1
                else:
                    self._cache_stats['misses'] += 1
                
                # 更新命中率
                if self._cache_stats['total'] > 0:
                    hit_ratio = self._cache_stats['hits'] / self._cache_stats['total']
                    self.cache_hit_ratio.set(hit_ratio)
    
    def record_rate_limit(self, result: str) -> None:
        """记录限流指标"""
        self.rate_limit_total.labels(result=result).inc()
    
    def set_circuit_breaker_state(self, service: str, state: str) -> None:
        """设置熔断器状态"""
        self.circuit_breaker_state.labels(service=service).state(state)
    
    def record_circuit_breaker_failure(self, service: str) -> None:
        """记录熔断器失败"""
        self.circuit_breaker_failures.labels(service=service).inc()
    
    def set_connection_pool_stats(self, pool: str, active: int, idle: int) -> None:
        """设置连接池统计"""
        self.connection_pool_active.labels(pool=pool).set(active)
        self.connection_pool_idle.labels(pool=pool).set(idle)
    
    def set_active_connections(self, count: int) -> None:
        """设置活跃连接数"""
        self.active_connections.set(count)
    
    def set_system_info(self, info: Dict[str, str]) -> None:
        """设置系统信息"""
        self.system_info.info(info)
    
    def get_response_time_percentiles(self, endpoint: str) -> Dict[str, float]:
        """获取响应时间百分位数"""
        with self._lock:
            times = list(self._response_times.get(endpoint, []))
            
            if not times:
                return {}
            
            times.sort()
            length = len(times)
            
            return {
                'p50': times[int(length * 0.5)] if length > 0 else 0,
                'p90': times[int(length * 0.9)] if length > 0 else 0,
                'p95': times[int(length * 0.95)] if length > 0 else 0,
                'p99': times[int(length * 0.99)] if length > 0 else 0,
            }
    
    def get_cache_stats(self) -> Dict[str, float]:
        """获取缓存统计"""
        with self._lock:
            stats = self._cache_stats.copy()
            
        if stats['total'] > 0:
            stats['hit_ratio'] = stats['hits'] / stats['total']
            stats['miss_ratio'] = stats['misses'] / stats['total']
        else:
            stats['hit_ratio'] = 0.0
            stats['miss_ratio'] = 0.0
        
        return stats
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        with self._lock:
            self._cache_stats = {
                'hits': 0,
                'misses': 0,
                'total': 0
            }
            self._response_times.clear()


class MetricsManager:
    """指标管理器"""
    
    def __init__(self):
        """初始化指标管理器"""
        self.registry = CollectorRegistry()
        self.collector = MetricsCollector(self.registry)
        self._start_time = time.time()
        
        # 设置系统信息
        
        self.collector.set_system_info({
            'version': '0.1.0',
            'python_version': sys.version,
            'platform': platform.platform(),
            'hostname': platform.node(),
        })
    
    def get_metrics(self) -> str:
        """获取 Prometheus 格式的指标"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_content_type(self) -> str:
        """获取指标内容类型"""
        return CONTENT_TYPE_LATEST
    
    def get_uptime(self) -> float:
        """获取运行时间"""
        return time.time() - self._start_time
    
    def get_health_metrics(self) -> Dict[str, any]:
        """获取健康指标摘要"""
        cache_stats = self.collector.get_cache_stats()
        
        return {
            'uptime_seconds': self.get_uptime(),
            'cache_hit_ratio': cache_stats.get('hit_ratio', 0.0),
            'total_requests': self.collector.request_total._value.sum(),
            'active_connections': self.collector.active_connections._value.get(),
        }


# 全局指标管理器实例
metrics_manager = MetricsManager()


def get_metrics_manager() -> MetricsManager:
    """获取全局指标管理器"""
    return metrics_manager


# 便捷函数
def record_request(method: str, endpoint: str, status_code: int, duration: float, **kwargs) -> None:
    """记录请求指标的便捷函数"""
    metrics_manager.collector.record_request(method, endpoint, status_code, duration, **kwargs)


def record_backend_request(service: str, method: str, status_code: int, duration: float) -> None:
    """记录后端请求指标的便捷函数"""
    metrics_manager.collector.record_backend_request(service, method, status_code, duration)


def record_cache_operation(operation: str, result: str) -> None:
    """记录缓存操作指标的便捷函数"""
    metrics_manager.collector.record_cache_operation(operation, result)


def record_rate_limit(result: str) -> None:
    """记录限流指标的便捷函数"""
    metrics_manager.collector.record_rate_limit(result) 