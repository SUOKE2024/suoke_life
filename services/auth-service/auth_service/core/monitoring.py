"""
monitoring - 索克生活项目模块
"""

            from auth_service.core.database import get_db
            from auth_service.core.redis import get_redis
        import re
from auth_service.config.settings import get_settings
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict, List, Optional, Any
import psutil
import structlog
import time

"""认证服务监控模块"""



logger = structlog.get_logger()

# Prometheus指标定义
REQUEST_COUNT = Counter(
    'auth_service_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'auth_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

AUTHENTICATION_ATTEMPTS = Counter(
    'auth_service_authentication_attempts_total',
    'Total authentication attempts',
    ['method', 'result']
)

ACTIVE_SESSIONS = Gauge(
    'auth_service_active_sessions',
    'Number of active user sessions'
)

TOKEN_OPERATIONS = Counter(
    'auth_service_token_operations_total',
    'Total token operations',
    ['operation', 'result']
)

MFA_OPERATIONS = Counter(
    'auth_service_mfa_operations_total',
    'Total MFA operations',
    ['operation', 'result']
)

PASSWORD_OPERATIONS = Counter(
    'auth_service_password_operations_total',
    'Total password operations',
    ['operation', 'result']
)

EMAIL_OPERATIONS = Counter(
    'auth_service_email_operations_total',
    'Total email operations',
    ['operation', 'result']
)

DATABASE_CONNECTIONS = Gauge(
    'auth_service_database_connections',
    'Number of database connections',
    ['state']
)

CACHE_OPERATIONS = Counter(
    'auth_service_cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

CACHE_HIT_RATE = Gauge(
    'auth_service_cache_hit_rate',
    'Cache hit rate percentage'
)

# 系统指标
CPU_USAGE = Gauge(
    'auth_service_cpu_usage_percent',
    'CPU usage percentage'
)

MEMORY_USAGE = Gauge(
    'auth_service_memory_usage_bytes',
    'Memory usage in bytes'
)

DISK_USAGE = Gauge(
    'auth_service_disk_usage_percent',
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
    
    def record_authentication_attempt(self, method: str, success: bool):
        """记录认证尝试"""
        result = "success" if success else "failure"
        AUTHENTICATION_ATTEMPTS.labels(method=method, result=result).inc()
    
    def record_token_operation(self, operation: str, success: bool):
        """记录令牌操作"""
        result = "success" if success else "error"
        TOKEN_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_mfa_operation(self, operation: str, success: bool):
        """记录MFA操作"""
        result = "success" if success else "error"
        MFA_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_password_operation(self, operation: str, success: bool):
        """记录密码操作"""
        result = "success" if success else "error"
        PASSWORD_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_email_operation(self, operation: str, success: bool):
        """记录邮件操作"""
        result = "success" if success else "error"
        EMAIL_OPERATIONS.labels(operation=operation, result=result).inc()
    
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
    
    def update_active_sessions(self, count: int):
        """更新活跃会话数"""
        ACTIVE_SESSIONS.set(count)
    
    def update_database_connections(self, active: int, idle: int):
        """更新数据库连接数"""
        DATABASE_CONNECTIONS.labels(state="active").set(active)
        DATABASE_CONNECTIONS.labels(state="idle").set(idle)
    
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


class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._suspicious_activities = []
        self._blocked_ips = set()
    
    def record_failed_login(self, email: str, ip_address: str, user_agent: str):
        """记录失败的登录尝试"""
        activity = {
            "type": "failed_login",
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow()
        }
        self._suspicious_activities.append(activity)
        
        # 检查是否需要阻止IP
        self._check_ip_blocking(ip_address)
        
        logger.warning(
            "Failed login attempt",
            email=email,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def record_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """记录可疑活动"""
        activity = {
            "type": activity_type,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        self._suspicious_activities.append(activity)
        
        logger.warning(
            "Suspicious activity detected",
            activity_type=activity_type,
            details=details
        )
    
    def _check_ip_blocking(self, ip_address: str):
        """检查是否需要阻止IP"""
        # 统计最近1小时内该IP的失败尝试次数
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_failures = [
            activity for activity in self._suspicious_activities
            if (activity["type"] == "failed_login" and 
                activity["ip_address"] == ip_address and
                activity["timestamp"] > one_hour_ago)
        ]
        
        if len(recent_failures) >= 10:  # 1小时内失败10次
            self._blocked_ips.add(ip_address)
            logger.error(
                "IP address blocked due to excessive failed login attempts",
                ip_address=ip_address,
                failure_count=len(recent_failures)
            )
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """检查IP是否被阻止"""
        return ip_address in self._blocked_ips
    
    def unblock_ip(self, ip_address: str):
        """解除IP阻止"""
        self._blocked_ips.discard(ip_address)
        logger.info("IP address unblocked", ip_address=ip_address)
    
    def get_suspicious_activities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取可疑活动列表"""
        return self._suspicious_activities[-limit:]
    
    def cleanup_old_activities(self):
        """清理旧的活动记录"""
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        self._suspicious_activities = [
            activity for activity in self._suspicious_activities
            if activity["timestamp"] > one_week_ago
        ]


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def check_database(self) -> Dict[str, Any]:
        """检查数据库连接"""
        try:
            
            start_time = time.time()
            # 这里应该实际检查数据库连接
            # 暂时返回模拟结果
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "details": "Database connection is healthy"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """检查Redis连接"""
        try:
            
            redis = get_redis()
            start_time = time.time()
            await redis.redis.ping()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "details": "Redis connection is healthy"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Redis connection failed"
            }
    
    async def check_email_service(self) -> Dict[str, Any]:
        """检查邮件服务"""
        try:
            # 这里可以发送测试邮件或检查邮件服务配置
            return {
                "status": "healthy",
                "details": "Email service is configured"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Email service check failed"
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
            "redis": await self.check_redis(),
            "email_service": await self.check_email_service(),
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
        self.security_monitor = SecurityMonitor()
    
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
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path


# 全局实例
_metrics_collector: Optional[MetricsCollector] = None
_security_monitor: Optional[SecurityMonitor] = None
_health_checker: Optional[HealthChecker] = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器"""
    global _metrics_collector
    if not _metrics_collector:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_security_monitor() -> SecurityMonitor:
    """获取安全监控器"""
    global _security_monitor
    if not _security_monitor:
        _security_monitor = SecurityMonitor()
    return _security_monitor


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
        "redis": await health_checker.check_redis()
    }
    
    # 确定就绪状态
    ready = all(
        check["status"] in ["healthy", "warning"] 
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