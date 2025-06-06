"""
performance - 索克生活项目模块
"""

from auth_service.config.settings import get_settings
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import asyncio
import json
import logging
import psutil
import time

"""
性能监控和优化中间件
提供请求性能监控、缓存优化、数据库连接池管理等功能
"""




@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    request_id: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    request_size: int
    response_size: int
    memory_usage: float
    cpu_usage: float
    db_query_count: int
    db_query_time: float
    cache_hits: int
    cache_misses: int
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = logging.getLogger("performance")
        
        # 性能指标存储
        self.metrics_buffer: deque = deque(maxlen=1000)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_requests': 0,
            'total_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'error_count': 0,
            'last_reset': datetime.utcnow()
        })
        
        # 慢查询阈值（毫秒）
        self.slow_query_threshold = 1000
        self.slow_request_threshold = 2000
        
        # 系统资源监控
        self.system_metrics = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'disk_usage': 0.0,
            'network_io': {'bytes_sent': 0, 'bytes_recv': 0}
        }
        
        # 启动系统监控任务
        asyncio.create_task(self._monitor_system_resources())
    
    async def record_metrics(self, metrics: PerformanceMetrics):
        """记录性能指标"""
        try:
            # 添加到缓冲区
            self.metrics_buffer.append(metrics)
            
            # 更新端点统计
            self._update_endpoint_stats(metrics)
            
            # 检查性能问题
            await self._check_performance_issues(metrics)
            
            # 记录到日志
            self._log_metrics(metrics)
            
        except Exception as e:
            self.logger.error(f"记录性能指标失败: {e}")
    
    def _update_endpoint_stats(self, metrics: PerformanceMetrics):
        """更新端点统计信息"""
        endpoint_key = f"{metrics.method}:{metrics.endpoint}"
        stats = self.endpoint_stats[endpoint_key]
        
        stats['total_requests'] += 1
        stats['total_response_time'] += metrics.response_time
        stats['min_response_time'] = min(stats['min_response_time'], metrics.response_time)
        stats['max_response_time'] = max(stats['max_response_time'], metrics.response_time)
        
        if metrics.status_code >= 400:
            stats['error_count'] += 1
        
        # 计算平均响应时间
        stats['avg_response_time'] = stats['total_response_time'] / stats['total_requests']
    
    async def _check_performance_issues(self, metrics: PerformanceMetrics):
        """检查性能问题"""
        issues = []
        
        # 检查慢请求
        if metrics.response_time > self.slow_request_threshold:
            issues.append({
                'type': 'slow_request',
                'severity': 'high' if metrics.response_time > 5000 else 'medium',
                'message': f"慢请求: {metrics.endpoint} 响应时间 {metrics.response_time:.2f}ms"
            })
        
        # 检查数据库慢查询
        if metrics.db_query_time > self.slow_query_threshold:
            issues.append({
                'type': 'slow_query',
                'severity': 'high',
                'message': f"数据库慢查询: {metrics.db_query_time:.2f}ms"
            })
        
        # 检查内存使用
        if metrics.memory_usage > 80:
            issues.append({
                'type': 'high_memory',
                'severity': 'critical' if metrics.memory_usage > 90 else 'high',
                'message': f"内存使用率过高: {metrics.memory_usage:.1f}%"
            })
        
        # 检查CPU使用
        if metrics.cpu_usage > 80:
            issues.append({
                'type': 'high_cpu',
                'severity': 'critical' if metrics.cpu_usage > 90 else 'high',
                'message': f"CPU使用率过高: {metrics.cpu_usage:.1f}%"
            })
        
        # 检查缓存命中率
        total_cache_requests = metrics.cache_hits + metrics.cache_misses
        if total_cache_requests > 0:
            hit_rate = metrics.cache_hits / total_cache_requests
            if hit_rate < 0.5:
                issues.append({
                    'type': 'low_cache_hit_rate',
                    'severity': 'medium',
                    'message': f"缓存命中率过低: {hit_rate:.1%}"
                })
        
        # 发送告警
        if issues:
            await self._send_performance_alerts(metrics, issues)
    
    def _log_metrics(self, metrics: PerformanceMetrics):
        """记录性能指标到日志"""
        log_data = metrics.to_dict()
        
        if metrics.response_time > self.slow_request_threshold:
            self.logger.warning(f"SLOW_REQUEST: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            self.logger.info(f"PERFORMANCE_METRICS: {json.dumps(log_data, ensure_ascii=False)}")
    
    async def _send_performance_alerts(self, metrics: PerformanceMetrics, issues: List[Dict]):
        """发送性能告警"""
        try:
            for issue in issues:
                alert_message = f"""
🚨 性能告警 - {issue['severity'].upper()}

问题类型: {issue['type']}
端点: {metrics.endpoint}
响应时间: {metrics.response_time:.2f}ms
内存使用: {metrics.memory_usage:.1f}%
CPU使用: {metrics.cpu_usage:.1f}%
时间: {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

详细信息: {issue['message']}
                """.strip()
                
                # 这里可以集成告警系统
                self.logger.error(f"PERFORMANCE_ALERT: {alert_message}")
                
        except Exception as e:
            self.logger.error(f"发送性能告警失败: {e}")
    
    async def _monitor_system_resources(self):
        """监控系统资源"""
        while True:
            try:
                # CPU使用率
                self.system_metrics['cpu_percent'] = psutil.cpu_percent(interval=1)
                
                # 内存使用率
                memory = psutil.virtual_memory()
                self.system_metrics['memory_percent'] = memory.percent
                
                # 磁盘使用率
                disk = psutil.disk_usage('/')
                self.system_metrics['disk_usage'] = (disk.used / disk.total) * 100
                
                # 网络IO
                net_io = psutil.net_io_counters()
                self.system_metrics['network_io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv
                }
                
                await asyncio.sleep(30)  # 每30秒更新一次
                
            except Exception as e:
                self.logger.error(f"系统资源监控失败: {e}")
                await asyncio.sleep(60)
    
    def get_endpoint_stats(self, endpoint: str = None) -> Dict[str, Any]:
        """获取端点统计信息"""
        if endpoint:
            return self.endpoint_stats.get(endpoint, {})
        return dict(self.endpoint_stats)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return self.system_metrics.copy()
    
    def get_recent_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的性能指标"""
        return [metrics.to_dict() for metrics in list(self.metrics_buffer)[-limit:]]


class PerformanceMiddleware:
    """性能监控中间件"""
    
    def __init__(self, app):
        self.app = app
        self.monitor = PerformanceMonitor()
        self.settings = get_settings()
        
        # 数据库查询计数器
        self.db_query_count = 0
        self.db_query_time = 0.0
        
        # 缓存计数器
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def __call__(self, request: Request, call_next):
        """中间件处理函数"""
        start_time = time.time()
        
        # 重置计数器
        self.db_query_count = 0
        self.db_query_time = 0.0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # 获取系统资源使用情况
        process = psutil.Process()
        memory_before = process.memory_percent()
        cpu_before = process.cpu_percent()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算性能指标
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 获取请求和响应大小
        request_size = int(request.headers.get("Content-Length", 0))
        response_size = int(response.headers.get("Content-Length", 0))
        
        # 获取系统资源使用情况
        memory_after = process.memory_percent()
        cpu_after = process.cpu_percent()
        
        # 创建性能指标
        metrics = PerformanceMetrics(
            request_id=getattr(request.state, 'request_id', 'unknown'),
            endpoint=request.url.path,
            method=request.method,
            response_time=response_time,
            status_code=response.status_code,
            request_size=request_size,
            response_size=response_size,
            memory_usage=memory_after,
            cpu_usage=cpu_after,
            db_query_count=self.db_query_count,
            db_query_time=self.db_query_time,
            cache_hits=self.cache_hits,
            cache_misses=self.cache_misses,
            timestamp=datetime.utcnow(),
            user_id=getattr(request.state, 'user_id', None),
            ip_address=self._get_client_ip(request)
        )
        
        # 记录性能指标
        await self.monitor.record_metrics(metrics)
        
        # 添加性能头信息
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-DB-Queries"] = str(self.db_query_count)
        response.headers["X-Cache-Status"] = f"hits:{self.cache_hits},misses:{self.cache_misses}"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"


class DatabaseQueryTracker:
    """数据库查询跟踪器"""
    
    def __init__(self, middleware: PerformanceMiddleware):
        self.middleware = middleware
    
    @asynccontextmanager
    async     @cache(timeout=300)  # 5分钟缓存
def track_query(self, query: str):
        """跟踪数据库查询"""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            query_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            self.middleware.db_query_count += 1
            self.middleware.db_query_time += query_time
            
            # 记录慢查询
            if query_time > self.middleware.monitor.slow_query_threshold:
                self.middleware.monitor.logger.warning(
                    f"SLOW_QUERY: {query_time:.2f}ms - {query[:200]}..."
                )


class CacheTracker:
    """缓存跟踪器"""
    
    def __init__(self, middleware: PerformanceMiddleware):
        self.middleware = middleware
    
    def record_hit(self):
        """记录缓存命中"""
        self.middleware.cache_hits += 1
    
    def record_miss(self):
        """记录缓存未命中"""
        self.middleware.cache_misses += 1


# 性能优化装饰器
def performance_monitor(func):
    """性能监控装饰器"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            logger = logging.getLogger("performance")
            logger.info(f"FUNCTION_PERFORMANCE: {func.__name__} - {execution_time:.2f}ms")
    
    return wrapper


def cache_performance(cache_key: str, ttl: int = 300):
    """缓存性能装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 这里可以集成Redis缓存
            # 简化实现，实际应该使用真实的缓存系统
            
            # 尝试从缓存获取
            cached_result = None  # await redis.get(cache_key)
            
            if cached_result:
                # 缓存命中
                return cached_result
            else:
                # 缓存未命中，执行函数
                result = await func(*args, **kwargs)
                
                # 存储到缓存
                # await redis.setex(cache_key, ttl, result)
                
                return result
        
        return wrapper
    return decorator


# 性能分析工具
class PerformanceAnalyzer:
    """性能分析工具"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def analyze_endpoint_performance(self, endpoint: str, hours: int = 24) -> Dict[str, Any]:
        """分析端点性能"""
        stats = self.monitor.get_endpoint_stats(endpoint)
        
        if not stats or stats['total_requests'] == 0:
            return {"error": "没有找到该端点的性能数据"}
        
        analysis = {
            "endpoint": endpoint,
            "total_requests": stats['total_requests'],
            "avg_response_time": stats['avg_response_time'],
            "min_response_time": stats['min_response_time'],
            "max_response_time": stats['max_response_time'],
            "error_rate": stats['error_count'] / stats['total_requests'],
            "performance_grade": self._calculate_performance_grade(stats),
            "recommendations": self._generate_recommendations(stats)
        }
        
        return analysis
    
    def _calculate_performance_grade(self, stats: Dict) -> str:
        """计算性能等级"""
        avg_time = stats['avg_response_time']
        error_rate = stats['error_count'] / stats['total_requests']
        
        if avg_time < 100 and error_rate < 0.01:
            return "A"
        elif avg_time < 500 and error_rate < 0.05:
            return "B"
        elif avg_time < 1000 and error_rate < 0.1:
            return "C"
        elif avg_time < 2000 and error_rate < 0.2:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """生成性能优化建议"""
        recommendations = []
        
        avg_time = stats['avg_response_time']
        error_rate = stats['error_count'] / stats['total_requests']
        
        if avg_time > 1000:
            recommendations.append("响应时间过长，建议优化数据库查询或添加缓存")
        
        if error_rate > 0.05:
            recommendations.append("错误率过高，建议检查错误处理逻辑")
        
        if stats['max_response_time'] > stats['avg_response_time'] * 5:
            recommendations.append("响应时间波动较大，建议检查是否存在性能瓶颈")
        
        return recommendations


# 全局性能监控实例
performance_monitor_instance = None

def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控实例"""
    global performance_monitor_instance
    if performance_monitor_instance is None:
        performance_monitor_instance = PerformanceMonitor()
    return performance_monitor_instance 