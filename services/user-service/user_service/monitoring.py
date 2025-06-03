"""用户服务监控模块"""

import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
import structlog

from user_service.config import get_settings

logger = structlog.get_logger()

# Prometheus指标定义
REQUEST_COUNT = Counter(
    'user_service_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'user_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'user_service_active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'user_service_database_connections',
    'Number of database connections',
    ['state']
)

CACHE_OPERATIONS = Counter(
    'user_service_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

CACHE_HIT_RATE = Gauge(
    'user_service_cache_hit_rate',
    'Cache hit rate percentage'
)

USER_OPERATIONS = Counter(
    'user_service_user_operations_total',
    'Total user operations',
    ['operation', 'result']
)

HEALTH_DATA_OPERATIONS = Counter(
    'user_service_health_data_operations_total',
    'Total health data operations',
    ['operation', 'result']
)

DEVICE_OPERATIONS = Counter(
    'user_service_device_operations_total',
    'Total device operations',
    ['operation', 'result']
)

# 系统指标
CPU_USAGE = Gauge(
    'user_service_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'user_service_memory_usage_bytes',
    'Memory usage in bytes'
)

DISK_USAGE = Gauge(
    'user_service_disk_usage_percent',
    'Disk usage percentage'
)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._cache_hits = 0
        self._cache_misses = 0
        self._start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录请求指标"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_cache_operation(self, operation: str, hit: bool):
        """记录缓存操作"""
        result = "hit" if hit else "miss"
        CACHE_OPERATIONS.labels(operation=operation, result=result).inc()
        
        if hit:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        
        # 更新缓存命中率
        total = self._cache_hits + self._cache_misses
        if total > 0:
            hit_rate = (self._cache_hits / total) * 100
            CACHE_HIT_RATE.set(hit_rate)
    
    def record_user_operation(self, operation: str, success: bool):
        """记录用户操作"""
        result = "success" if success else "error"
        USER_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_health_data_operation(self, operation: str, success: bool):
        """记录健康数据操作"""
        result = "success" if success else "error"
        HEALTH_DATA_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_device_operation(self, operation: str, success: bool):
        """记录设备操作"""
        result = "success" if success else "error"
        DEVICE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def update_system_metrics(self):
        """更新系统指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # 内存使用
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            DISK_USAGE.set(disk_percent)
            
        except Exception as e:
            logger.error("Failed to update system metrics", error=str(e))
    
    def get_uptime(self) -> float:
        """获取服务运行时间"""
        return time.time() - self._start_time


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._checks = {}
    
    async def check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            # 这里应该实际检查数据库连接
            # 暂时返回模拟结果
            return {
                "status": "healthy",
                "response_time": 0.05,
                "details": "Database connection is healthy"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """检查缓存连接"""
        try:
            from user_service.cache import get_cache_manager
            cache_manager = get_cache_manager()
            
            if not cache_manager:
                return {
                    "status": "disabled",
                    "details": "Cache is disabled"
                }
            
            start_time = time.time()
            await cache_manager.redis.ping()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "details": "Cache connection is healthy"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Cache connection failed"
            }
    
    async def check_auth_service(self) -> Dict[str, Any]:
        """检查认证服务连接"""
        try:
            import httpx
            
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.auth.auth_service_url}/health",
                    timeout=5.0
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "response_time": response_time,
                        "details": "Auth service is healthy"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "status_code": response.status_code,
                        "details": "Auth service returned non-200 status"
                    }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Auth service connection failed"
            }
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """检查磁盘空间"""
        try:
            disk = psutil.disk_usage('/')
            usage_percent = (disk.used / disk.total) * 100
            
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "free_bytes": disk.free,
                "total_bytes": disk.total,
                "details": f"Disk usage: {usage_percent:.1f}%"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Failed to check disk space"
            }
    
    async def check_memory(self) -> Dict[str, Any]:
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            if usage_percent > 90:
                status = "critical"
            elif usage_percent > 80:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "usage_percent": usage_percent,
                "available_bytes": memory.available,
                "total_bytes": memory.total,
                "details": f"Memory usage: {usage_percent:.1f}%"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Failed to check memory"
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """运行所有健康检查"""
        checks = {
            "database": await self.check_database(),
            "cache": await self.check_cache(),
            "auth_service": await self.check_auth_service(),
            "disk_space": await self.check_disk_space(),
            "memory": await self.check_memory()
        }
        
        # 确定整体状态
        overall_status = "healthy"
        for check_name, check_result in checks.items():
            if check_result["status"] == "critical":
                overall_status = "critical"
                break
            elif check_result["status"] == "unhealthy":
                overall_status = "unhealthy"
            elif check_result["status"] == "warning" and overall_status == "healthy":
                overall_status = "warning"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }


class RequestMetricsMiddleware:
    """请求指标中间件"""
    
    def __init__(self, app):
        self.app = app
        self.metrics_collector = MetricsCollector()
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # 包装send函数以捕获响应状态码
        status_code = 500
        
        async def wrapped_send(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            # 记录请求指标
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]
            
            # 简化路径（移除参数）
            endpoint = self._normalize_endpoint(path)
            
            self.metrics_collector.record_request(method, endpoint, status_code, duration)
    
    def _normalize_endpoint(self, path: str) -> str:
        """标准化端点路径"""
        # 移除查询参数
        if "?" in path:
            path = path.split("?")[0]
        
        # 替换UUID和数字ID为占位符
        import re
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path


# 全局实例
_metrics_collector: Optional[MetricsCollector] = None
_health_checker: Optional[HealthChecker] = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器"""
    global _metrics_collector
    if not _metrics_collector:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_health_checker() -> HealthChecker:
    """获取健康检查器"""
    global _health_checker
    if not _health_checker:
        _health_checker = HealthChecker()
    return _health_checker


async def metrics_endpoint() -> Response:
    """Prometheus指标端点"""
    # 更新系统指标
    metrics_collector = get_metrics_collector()
    metrics_collector.update_system_metrics()
    
    # 生成Prometheus格式的指标
    metrics_data = generate_latest()
    return PlainTextResponse(metrics_data, media_type=CONTENT_TYPE_LATEST)


async def health_endpoint() -> Dict[str, Any]:
    """健康检查端点"""
    health_checker = get_health_checker()
    return await health_checker.run_all_checks()


async def readiness_endpoint() -> Dict[str, Any]:
    """就绪检查端点"""
    health_checker = get_health_checker()
    
    # 只检查关键服务
    checks = {
        "database": await health_checker.check_database(),
        "cache": await health_checker.check_cache()
    }
    
    # 确定就绪状态
    ready = all(
        check["status"] in ["healthy", "disabled"] 
        for check in checks.values()
    )
    
    return {
        "ready": ready,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


async def liveness_endpoint() -> Dict[str, Any]:
    """存活检查端点"""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": get_metrics_collector().get_uptime()
    } 