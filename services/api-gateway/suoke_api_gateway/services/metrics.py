"""
指标监控服务

收集和暴露 Prometheus 指标。
"""

import time
from typing import Dict, Optional

from prometheus_client import Counter, Gauge, Histogram, Info

from ..core.config import Settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class MetricsService:
    """指标监控服务"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.enabled = settings.monitoring.enabled
        
        if self.enabled:
            self._init_metrics()
    
    def _init_metrics(self) -> None:
        """初始化 Prometheus 指标"""
        # 应用信息
        self.app_info = Info(
            'suoke_gateway_info',
            'Application information',
        )
        self.app_info.info({
            'version': self.settings.app_version,
            'environment': self.settings.environment,
        })
        
        # 请求指标
        self.request_count = Counter(
            'suoke_gateway_requests_total',
            'Total number of requests',
            ['method', 'path', 'status_code'],
        )
        
        self.request_duration = Histogram(
            'suoke_gateway_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'path'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        )
        
        self.request_size = Histogram(
            'suoke_gateway_request_size_bytes',
            'Request size in bytes',
            ['method', 'path'],
            buckets=[100, 1000, 10000, 100000, 1000000],
        )
        
        self.response_size = Histogram(
            'suoke_gateway_response_size_bytes',
            'Response size in bytes',
            ['method', 'path'],
            buckets=[100, 1000, 10000, 100000, 1000000],
        )
        
        # 错误指标
        self.error_count = Counter(
            'suoke_gateway_errors_total',
            'Total number of errors',
            ['error_type', 'path'],
        )
        
        # 认证指标
        self.auth_attempts = Counter(
            'suoke_gateway_auth_attempts_total',
            'Total authentication attempts',
            ['result'],  # success, failure
        )
        
        # 限流指标
        self.rate_limit_hits = Counter(
            'suoke_gateway_rate_limit_hits_total',
            'Total rate limit hits',
            ['limit_type'],
        )
        
        # 服务指标
        self.service_requests = Counter(
            'suoke_gateway_service_requests_total',
            'Total requests to backend services',
            ['service', 'method', 'status_code'],
        )
        
        self.service_duration = Histogram(
            'suoke_gateway_service_duration_seconds',
            'Backend service response time',
            ['service', 'method'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        )
        
        # 连接指标
        self.active_connections = Gauge(
            'suoke_gateway_active_connections',
            'Number of active connections',
        )
        
        # 缓存指标
        self.cache_hits = Counter(
            'suoke_gateway_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
        )
        
        self.cache_misses = Counter(
            'suoke_gateway_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
        )
        
        # 健康检查指标
        self.health_check_duration = Histogram(
            'suoke_gateway_health_check_duration_seconds',
            'Health check duration',
            ['service'],
        )
        
        self.service_health = Gauge(
            'suoke_gateway_service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service'],
        )
        
        logger.info("Prometheus metrics initialized")
    
    async def initialize(self) -> None:
        """初始化指标服务"""
        if self.enabled:
            logger.info("Metrics service initialized")
    
    async def cleanup(self) -> None:
        """清理资源"""
        pass
    
    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """记录请求指标"""
        if not self.enabled:
            return
        
        # 清理路径（移除查询参数和路径参数）
        clean_path = self._clean_path(path)
        
        # 记录指标
        self.request_count.labels(
            method=method,
            path=clean_path,
            status_code=str(status_code),
        ).inc()
        
        self.request_duration.labels(
            method=method,
            path=clean_path,
        ).observe(duration)
        
        if request_size > 0:
            self.request_size.labels(
                method=method,
                path=clean_path,
            ).observe(request_size)
        
        if response_size > 0:
            self.response_size.labels(
                method=method,
                path=clean_path,
            ).observe(response_size)
    
    def record_error(self, error_type: str, path: str) -> None:
        """记录错误指标"""
        if not self.enabled:
            return
        
        clean_path = self._clean_path(path)
        self.error_count.labels(
            error_type=error_type,
            path=clean_path,
        ).inc()
    
    def record_auth_attempt(self, success: bool) -> None:
        """记录认证尝试"""
        if not self.enabled:
            return
        
        result = "success" if success else "failure"
        self.auth_attempts.labels(result=result).inc()
    
    def record_rate_limit_hit(self, limit_type: str) -> None:
        """记录限流命中"""
        if not self.enabled:
            return
        
        self.rate_limit_hits.labels(limit_type=limit_type).inc()
    
    def record_service_request(
        self,
        service: str,
        method: str,
        status_code: int,
        duration: float,
    ) -> None:
        """记录服务请求指标"""
        if not self.enabled:
            return
        
        self.service_requests.labels(
            service=service,
            method=method,
            status_code=str(status_code),
        ).inc()
        
        self.service_duration.labels(
            service=service,
            method=method,
        ).observe(duration)
    
    def set_active_connections(self, count: int) -> None:
        """设置活跃连接数"""
        if not self.enabled:
            return
        
        self.active_connections.set(count)
    
    def record_cache_hit(self, cache_type: str) -> None:
        """记录缓存命中"""
        if not self.enabled:
            return
        
        self.cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str) -> None:
        """记录缓存未命中"""
        if not self.enabled:
            return
        
        self.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_health_check(self, service: str, duration: float, healthy: bool) -> None:
        """记录健康检查指标"""
        if not self.enabled:
            return
        
        self.health_check_duration.labels(service=service).observe(duration)
        self.service_health.labels(service=service).set(1 if healthy else 0)
    
    def _clean_path(self, path: str) -> str:
        """清理路径，移除动态部分"""
        # 移除查询参数
        if '?' in path:
            path = path.split('?')[0]
        
        # 替换常见的动态路径参数
        import re
        
        # UUID 模式
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path)
        
        # 数字 ID 模式
        path = re.sub(r'/\d+', '/{id}', path)
        
        # 限制路径长度
        if len(path) > 100:
            path = path[:100] + "..."
        
        return path
    
    def get_metrics_summary(self) -> Dict[str, float]:
        """获取指标摘要"""
        if not self.enabled:
            return {}
        
        # 这里可以返回一些关键指标的摘要
        # 实际实现需要从 Prometheus 客户端获取当前值
        return {
            "total_requests": 0,  # 需要实现获取当前计数器值的逻辑
            "error_rate": 0,
            "avg_response_time": 0,
        } 