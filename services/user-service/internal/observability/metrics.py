"""
指标收集模块
使用Prometheus客户端库收集和暴露服务指标
"""
import time
from typing import Dict

from prometheus_client import Counter, Gauge, Histogram, Info

class PrometheusMetrics:
    """Prometheus指标收集类"""

    def __init__(self):
        """初始化Prometheus指标"""
        # 通用指标
        self.request_count = Counter(
            'user_service_requests_total',
            '请求总数',
            ['method', 'endpoint', 'status_code']
        )
        self.request_latency = Histogram(
            'user_service_request_duration_seconds',
            '请求处理时间（秒）',
            ['method', 'endpoint'],
            buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
        )
        
        # 健康检查相关指标
        self.health_check_count = Counter(
            'user_service_health_checks_total',
            '健康检查请求总数'
        )
        self.health_check_latency = Histogram(
            'user_service_health_check_duration_seconds',
            '健康检查处理时间（秒）',
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, float('inf'))
        )
        self.database_latency = Histogram(
            'user_service_database_operation_duration_seconds',
            '数据库操作时间（秒）',
            ['operation'],
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, float('inf'))
        )
        
        # 用户相关指标
        self.active_users = Gauge(
            'user_service_active_users',
            '活跃用户数量'
        )
        self.user_operations = Counter(
            'user_service_user_operations_total',
            '用户操作总数',
            ['operation']
        )
        self.user_profiles_count = Gauge(
            'user_service_user_profiles_count',
            '用户档案数量'
        )
        self.user_registrations = Counter(
            'user_service_user_registrations_total',
            '用户注册总数'
        )
        self.user_deletions = Counter(
            'user_service_user_deletions_total',
            '用户删除总数'
        )
        
        # API安全指标
        self.auth_failures = Counter(
            'user_service_auth_failures_total',
            '认证失败总数',
            ['endpoint']
        )
        self.rate_limit_hits = Counter(
            'user_service_rate_limit_hits_total',
            '速率限制命中总数',
            ['endpoint']
        )
        
        # 系统资源指标
        self.memory_usage = Gauge(
            'user_service_memory_usage_bytes',
            '内存使用量（字节）'
        )
        self.cpu_usage = Gauge(
            'user_service_cpu_usage_percent',
            'CPU使用率'
        )
        
        # 服务信息
        self.service_info = Info(
            'user_service',
            '用户服务信息'
        )
    
    def record_request_start(self, method: str, endpoint: str) -> float:
        """
        记录请求开始时间
        
        Args:
            method: HTTP方法
            endpoint: 请求路径
            
        Returns:
            float: 请求开始时间
        """
        return time.time()
    
    def record_request_end(self, start_time: float, method: str, endpoint: str, status_code: int):
        """
        记录请求结束并更新相关指标
        
        Args:
            start_time: 请求开始时间
            method: HTTP方法
            endpoint: 请求路径
            status_code: 响应状态码
        """
        duration = time.time() - start_time
        self.request_latency.labels(method=method, endpoint=endpoint).observe(duration)
        self.request_count.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()
    
    def update_service_info(self, info: Dict[str, str]):
        """
        更新服务信息
        
        Args:
            info: 服务信息字典
        """
        self.service_info.info(info)
    
    def record_user_operation(self, operation: str):
        """
        记录用户操作
        
        Args:
            operation: 操作类型
        """
        self.user_operations.labels(operation=operation).inc()
    
    def record_database_operation(self, operation: str, duration: float):
        """
        记录数据库操作时间
        
        Args:
            operation: 操作类型
            duration: 操作时间（秒）
        """
        self.database_latency.labels(operation=operation).observe(duration)
    
    def record_auth_failure(self, endpoint: str):
        """
        记录认证失败
        
        Args:
            endpoint: 请求路径
        """
        self.auth_failures.labels(endpoint=endpoint).inc()
    
    def record_rate_limit_hit(self, endpoint: str):
        """
        记录速率限制命中
        
        Args:
            endpoint: 请求路径
        """
        self.rate_limit_hits.labels(endpoint=endpoint).inc()
    
    def update_active_users_count(self, count: int):
        """
        更新活跃用户数量
        
        Args:
            count: 用户数量
        """
        self.active_users.set(count)
    
    def update_user_profiles_count(self, count: int):
        """
        更新用户档案数量
        
        Args:
            count: 档案数量
        """
        self.user_profiles_count.set(count)
    
    def update_system_resources(self, memory_bytes: float, cpu_percent: float):
        """
        更新系统资源使用情况
        
        Args:
            memory_bytes: 内存使用量（字节）
            cpu_percent: CPU使用率
        """
        self.memory_usage.set(memory_bytes)
        self.cpu_usage.set(cpu_percent)

# 创建全局指标实例
prometheus_metrics = PrometheusMetrics()

class MetricsMiddleware:
    """
    指标中间件
    自动记录请求处理时间和请求计数
    """
    
    async def __call__(self, request, call_next):
        """
        处理请求并记录指标
        
        Args:
            request: FastAPI请求对象
            call_next: 下一个中间件或路由处理函数
            
        Returns:
            响应对象
        """
        method = request.method
        path = request.url.path
        
        # 忽略对/metrics和/health端点的监控，避免循环记录
        if path in ["/metrics", "/health", "/favicon.ico"]:
            return await call_next(request)
        
        # 记录请求开始
        start_time = prometheus_metrics.record_request_start(method, path)
        
        # 处理请求
        response = await call_next(request)
        
        # 记录请求结束
        prometheus_metrics.record_request_end(
            start_time, method, path, response.status_code
        )
        
        return response 