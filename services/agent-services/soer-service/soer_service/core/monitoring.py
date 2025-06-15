"""
监控和指标模块

提供 Prometheus 指标收集和健康检查
"""

import logging
import time
from typing import Dict, Any

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import psutil

logger = logging.getLogger(__name__)

# Prometheus 指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['database', 'operation', 'status']
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)


class PrometheusMiddleware:
    """Prometheus 指标收集中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        # 跳过监控端点自身
        if path in ["/metrics", "/health"]:
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                
                # 记录请求计数
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
                
                # 记录请求耗时
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def setup_monitoring() -> None:
    """设置监控系统"""
    logger.info("📊 监控系统初始化完成")


def update_system_metrics() -> None:
    """更新系统指标"""
    try:
        # 更新内存使用率
        memory = psutil.virtual_memory()
        SYSTEM_MEMORY_USAGE.set(memory.used)
        
        # 更新CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        SYSTEM_CPU_USAGE.set(cpu_percent)
        
    except Exception as e:
        logger.error(f"更新系统指标失败: {e}")


def get_metrics() -> str:
    """获取 Prometheus 格式的指标"""
    # 更新系统指标
    update_system_metrics()
    
    return generate_latest()


def get_health_status() -> Dict[str, Any]:
    """获取健康状态"""
    try:
        # 检查系统资源
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "memory": {
                    "used_percent": memory.percent,
                    "available_gb": round(memory.available / 1024**3, 2)
                },
                "disk": {
                    "used_percent": disk.percent,
                    "free_gb": round(disk.free / 1024**3, 2)
                },
                "cpu_percent": psutil.cpu_percent(interval=None)
            }
        }
        
        # 检查关键资源状态
        if memory.percent > 90:
            health_status["status"] = "warning"
            health_status["warnings"] = ["High memory usage"]
        
        if disk.percent > 90:
            health_status["status"] = "warning"
            health_status.setdefault("warnings", []).append("High disk usage")
        
        return health_status
        
    except Exception as e:
        logger.error(f"获取健康状态失败: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e)
        }


def record_database_operation(database: str, operation: str, success: bool) -> None:
    """记录数据库操作指标"""
    status = "success" if success else "error"
    DATABASE_OPERATIONS.labels(
        database=database,
        operation=operation,
        status=status
    ).inc()


def increment_active_connections() -> None:
    """增加活跃连接数"""
    ACTIVE_CONNECTIONS.inc()


def decrement_active_connections() -> None:
    """减少活跃连接数"""
    ACTIVE_CONNECTIONS.dec()