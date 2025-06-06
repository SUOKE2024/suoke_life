"""
monitoring - 索克生活项目模块
"""

from .cache_simple import get_cache_manager
from .config import get_settings
from .database import get_database
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
from typing import Dict, Any, Optional, List
import asyncio
import psutil
import time

"""
监控和指标模块

提供应用程序的监控指标、健康检查、性能监控等功能。
"""




# Prometheus 指标注册表
REGISTRY = CollectorRegistry()

# 应用指标
APP_INFO = Info('health_data_service_info', 'Application information', registry=REGISTRY)
APP_UPTIME = Gauge('health_data_service_uptime_seconds', 'Application uptime in seconds', registry=REGISTRY)

# HTTP 请求指标
HTTP_REQUESTS_TOTAL = Counter(
    'health_data_service_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

HTTP_REQUEST_DURATION = Histogram(
    'health_data_service_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    'health_data_service_http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    registry=REGISTRY
)

# 数据库指标
DB_CONNECTIONS_ACTIVE = Gauge(
    'health_data_service_db_connections_active',
    'Number of active database connections',
    registry=REGISTRY
)

DB_CONNECTIONS_IDLE = Gauge(
    'health_data_service_db_connections_idle',
    'Number of idle database connections',
    registry=REGISTRY
)

DB_QUERY_DURATION = Histogram(
    'health_data_service_db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table'],
    registry=REGISTRY
)

DB_QUERIES_TOTAL = Counter(
    'health_data_service_db_queries_total',
    'Total number of database queries',
    ['operation', 'table', 'status'],
    registry=REGISTRY
)

# 缓存指标
CACHE_OPERATIONS_TOTAL = Counter(
    'health_data_service_cache_operations_total',
    'Total number of cache operations',
    ['operation', 'status'],
    registry=REGISTRY
)

CACHE_HIT_RATIO = Gauge(
    'health_data_service_cache_hit_ratio',
    'Cache hit ratio',
    registry=REGISTRY
)

# 业务指标
HEALTH_DATA_RECORDS_TOTAL = Counter(
    'health_data_service_records_total',
    'Total number of health data records',
    ['data_type', 'source'],
    registry=REGISTRY
)

HEALTH_DATA_PROCESSING_DURATION = Histogram(
    'health_data_service_processing_duration_seconds',
    'Health data processing duration in seconds',
    ['data_type', 'stage'],
    registry=REGISTRY
)

# 系统指标
SYSTEM_CPU_USAGE = Gauge(
    'health_data_service_system_cpu_usage_percent',
    'System CPU usage percentage',
    registry=REGISTRY
)

SYSTEM_MEMORY_USAGE = Gauge(
    'health_data_service_system_memory_usage_bytes',
    'System memory usage in bytes',
    registry=REGISTRY
)

SYSTEM_DISK_USAGE = Gauge(
    'health_data_service_system_disk_usage_bytes',
    'System disk usage in bytes',
    registry=REGISTRY
)


@dataclass
class HealthStatus:
    """健康状态"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    checks: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSnapshot:
    """指标快照"""
    timestamp: datetime
    http_requests_per_second: float
    avg_response_time: float
    db_connections: int
    cache_hit_ratio: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._last_check: Optional[HealthStatus] = None
        self._check_interval = 30  # 30秒检查一次
        
    async def check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            # 在测试环境中，简化数据库检查
            if self.settings.is_testing:
                return {
                    "status": "healthy",
                    "response_time": 0.001,
                    "details": "Database check skipped in testing mode"
                }
            
            start_time = time.time()
            db_manager = await get_database()
            
            # 执行简单查询测试连接
            async with db_manager.get_async_session() as session:
                result = await session.execute("SELECT 1")
                await result.fetchone()
            
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": duration,
                "details": "Database connection successful"
            }
        except Exception as e:
            logger.error(f"数据库健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }
    
    async def check_cache(self) -> Dict[str, Any]:
        """检查缓存连接"""
        try:
            start_time = time.time()
            cache_manager = await get_cache_manager()
            
            # 测试缓存连接
            await cache_manager.ping()
            
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": duration,
                "details": "Cache connection successful"
            }
        except Exception as e:
            logger.warning(f"缓存健康检查失败: {e}")
            return {
                "status": "degraded",
                "error": str(e),
                "details": "Cache connection failed, running without cache"
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """检查系统资源"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 更新Prometheus指标
            SYSTEM_CPU_USAGE.set(cpu_percent)
            SYSTEM_MEMORY_USAGE.set(memory.used)
            SYSTEM_DISK_USAGE.set(disk.used)
            
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 80 or disk.percent > 80:
                status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "unhealthy"
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "details": f"CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%"
            }
        except Exception as e:
            logger.error(f"系统资源检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "System resource check failed"
            }
    
    async def perform_health_check(self) -> HealthStatus:
        """执行完整的健康检查"""
        start_time = datetime.now()
        
        # 并行执行各项检查
        db_check, cache_check, system_check = await asyncio.gather(
            self.check_database(),
            self.check_cache(),
            self.check_system_resources(),
            return_exceptions=True
        )
        
        checks = {
            "database": db_check if not isinstance(db_check, Exception) else {"status": "unhealthy", "error": str(db_check)},
            "cache": cache_check if not isinstance(cache_check, Exception) else {"status": "unhealthy", "error": str(cache_check)},
            "system": system_check if not isinstance(system_check, Exception) else {"status": "unhealthy", "error": str(system_check)}
        }
        
        # 确定整体状态
        statuses = [check["status"] for check in checks.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        health_status = HealthStatus(
            status=overall_status,
            timestamp=start_time,
            checks=checks,
            details={
                "check_duration": (datetime.now() - start_time).total_seconds(),
                "service": "health-data-service",
                "version": "1.0.0"
            }
        )
        
        self._last_check = health_status
        return health_status
    
    def get_last_check(self) -> Optional[HealthStatus]:
        """获取最后一次健康检查结果"""
        return self._last_check


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._start_time = time.time()
        self._request_count = 0
        self._response_times: List[float] = []
        
        # 设置应用信息
        APP_INFO.info({
            'version': '1.0.0',
            'service': 'health-data-service',
            'environment': self.settings.environment
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录HTTP请求指标"""
        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        HTTP_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        self._request_count += 1
        self._response_times.append(duration)
        
        # 保持最近1000个响应时间
        if len(self._response_times) > 1000:
            self._response_times = self._response_times[-1000:]
    
        @cache(timeout=300)  # 5分钟缓存
def record_db_query(self, operation: str, table: str, duration: float, success: bool):
        """记录数据库查询指标"""
        status = "success" if success else "error"
        
        DB_QUERIES_TOTAL.labels(
            operation=operation,
            table=table,
            status=status
        ).inc()
        
        DB_QUERY_DURATION.labels(
            operation=operation,
            table=table
        ).observe(duration)
    
    def record_cache_operation(self, operation: str, success: bool):
        """记录缓存操作指标"""
        status = "hit" if success and operation == "get" else "miss" if not success and operation == "get" else "success" if success else "error"
        
        CACHE_OPERATIONS_TOTAL.labels(
            operation=operation,
            status=status
        ).inc()
    
    def record_health_data(self, data_type: str, source: str, processing_duration: float, stage: str):
        """记录健康数据处理指标"""
        HEALTH_DATA_RECORDS_TOTAL.labels(
            data_type=data_type,
            source=source
        ).inc()
        
        HEALTH_DATA_PROCESSING_DURATION.labels(
            data_type=data_type,
            stage=stage
        ).observe(processing_duration)
    
    def update_uptime(self):
        """更新运行时间"""
        uptime = time.time() - self._start_time
        APP_UPTIME.set(uptime)
    
    def get_metrics_snapshot(self) -> MetricSnapshot:
        """获取指标快照"""
        now = datetime.now()
        
        # 计算每秒请求数（最近5分钟）
        recent_requests = len([t for t in self._response_times if t > (time.time() - 300)])
        rps = recent_requests / 300 if recent_requests > 0 else 0
        
        # 计算平均响应时间
        avg_response_time = sum(self._response_times) / len(self._response_times) if self._response_times else 0
        
        return MetricSnapshot(
            timestamp=now,
            http_requests_per_second=rps,
            avg_response_time=avg_response_time,
            db_connections=0,  # 这里需要从数据库连接池获取
            cache_hit_ratio=0.0,  # 这里需要从缓存管理器获取
            cpu_usage=psutil.cpu_percent(),
            memory_usage=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage('/').percent
        )
    
    def export_metrics(self) -> str:
        """导出Prometheus格式的指标"""
        self.update_uptime()
        return generate_latest(REGISTRY).decode('utf-8')


# 全局实例
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


async def get_health_status() -> HealthStatus:
    """获取健康状态"""
    return await health_checker.perform_health_check()


def get_metrics() -> str:
    """获取指标数据"""
    return metrics_collector.export_metrics()


def record_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """记录请求指标"""
    metrics_collector.record_request(method, endpoint, status_code, duration)


def record_db_metrics(operation: str, table: str, duration: float, success: bool = True):
    """记录数据库指标"""
    metrics_collector.record_db_query(operation, table, duration, success)


def record_cache_metrics(operation: str, success: bool = True):
    """记录缓存指标"""
    metrics_collector.record_cache_operation(operation, success)


def record_business_metrics(data_type: str, source: str, processing_duration: float, stage: str = "processing"):
    """记录业务指标"""
    metrics_collector.record_health_data(data_type, source, processing_duration, stage) 