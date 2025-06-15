"""
性能监控器
包含API响应时间、数据库查询性能和系统资源监控
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json
from redis.asyncio import Redis
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
import threading

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class APIMetrics:
    """API指标"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None


@dataclass
class DatabaseMetrics:
    """数据库指标"""
    query_type: str  # SELECT, INSERT, UPDATE, DELETE
    table_name: str
    execution_time: float
    rows_affected: int
    timestamp: datetime
    query_hash: Optional[str] = None


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, redis: Redis, enable_prometheus: bool = True):
        self.redis = redis
        self.enable_prometheus = enable_prometheus
        
        # 内存中的指标存储（用于快速访问）
        self._api_metrics = deque(maxlen=10000)
        self._db_metrics = deque(maxlen=10000)
        self._system_metrics = deque(maxlen=1000)
        
        # 指标聚合数据
        self._api_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0,
            'error_count': 0
        })
        
        self._db_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
        
        # Prometheus指标
        if self.enable_prometheus:
            self._setup_prometheus_metrics()
        
        # 启动后台任务
        self._monitoring_task = None
        self._start_monitoring()
    
    def _setup_prometheus_metrics(self):
        """设置Prometheus指标"""
        self.registry = CollectorRegistry()
        
        # API指标
        self.api_request_count = Counter(
            'auth_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'auth_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        # 数据库指标
        self.db_query_count = Counter(
            'auth_db_queries_total',
            'Total database queries',
            ['query_type', 'table'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'auth_db_query_duration_seconds',
            'Database query duration',
            ['query_type', 'table'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )
        
        # 系统指标
        self.system_cpu_usage = Gauge(
            'auth_system_cpu_usage_percent',
            'System CPU usage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'auth_system_memory_usage_bytes',
            'System memory usage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'auth_system_disk_usage_percent',
            'System disk usage',
            registry=self.registry
        )
    
    def _start_monitoring(self):
        """启动监控任务"""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_system_metrics())
    
    async def _monitor_system_metrics(self):
        """监控系统指标"""
        while True:
            try:
                # 收集系统指标
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # 创建系统指标
                timestamp = datetime.now()
                
                cpu_metric = PerformanceMetric(
                    name="system_cpu_usage",
                    value=cpu_percent,
                    timestamp=timestamp,
                    unit="percent"
                )
                
                memory_metric = PerformanceMetric(
                    name="system_memory_usage",
                    value=memory.used,
                    timestamp=timestamp,
                    unit="bytes",
                    tags={"total": str(memory.total), "percent": str(memory.percent)}
                )
                
                disk_metric = PerformanceMetric(
                    name="system_disk_usage",
                    value=disk.percent,
                    timestamp=timestamp,
                    unit="percent",
                    tags={"total": str(disk.total), "used": str(disk.used)}
                )
                
                # 存储指标
                self._system_metrics.extend([cpu_metric, memory_metric, disk_metric])
                
                # 更新Prometheus指标
                if self.enable_prometheus:
                    self.system_cpu_usage.set(cpu_percent)
                    self.system_memory_usage.set(memory.used)
                    self.system_disk_usage.set(disk.percent)
                
                # 存储到Redis
                await self._store_metrics_to_redis([cpu_metric, memory_metric, disk_metric])
                
                # 每30秒收集一次系统指标
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"系统指标监控错误: {e}")
                await asyncio.sleep(60)
    
    @asynccontextmanager
    async def track_api_request(
        self,
        endpoint: str,
        method: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """跟踪API请求性能"""
        start_time = time.time()
        status_code = 200
        
        try:
            yield
        except Exception as e:
            status_code = getattr(e, 'status_code', 500)
            raise
        finally:
            end_time = time.time()
            response_time = end_time - start_time
            
            # 创建API指标
            api_metric = APIMetrics(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                timestamp=datetime.now(),
                user_id=user_id,
                ip_address=ip_address
            )
            
            # 记录指标
            await self.record_api_metric(api_metric)
    
    @asynccontextmanager
    async def track_database_query(
        self,
        query_type: str,
        table_name: str,
        query_hash: Optional[str] = None
    ):
        """跟踪数据库查询性能"""
        start_time = time.time()
        rows_affected = 0
        
        try:
            result = yield
            # 尝试获取影响的行数
            if hasattr(result, 'rowcount'):
                rows_affected = result.rowcount
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 创建数据库指标
            db_metric = DatabaseMetrics(
                query_type=query_type,
                table_name=table_name,
                execution_time=execution_time,
                rows_affected=rows_affected,
                timestamp=datetime.now(),
                query_hash=query_hash
            )
            
            # 记录指标
            await self.record_database_metric(db_metric)
    
    async def record_api_metric(self, metric: APIMetrics):
        """记录API指标"""
        # 存储到内存
        self._api_metrics.append(metric)
        
        # 更新聚合统计
        key = f"{metric.method}:{metric.endpoint}"
        stats = self._api_stats[key]
        stats['count'] += 1
        stats['total_time'] += metric.response_time
        stats['min_time'] = min(stats['min_time'], metric.response_time)
        stats['max_time'] = max(stats['max_time'], metric.response_time)
        
        if metric.status_code >= 400:
            stats['error_count'] += 1
        
        # 更新Prometheus指标
        if self.enable_prometheus:
            self.api_request_count.labels(
                method=metric.method,
                endpoint=metric.endpoint,
                status_code=str(metric.status_code)
            ).inc()
            
            self.api_request_duration.labels(
                method=metric.method,
                endpoint=metric.endpoint
            ).observe(metric.response_time)
        
        # 存储到Redis（异步）
        asyncio.create_task(self._store_api_metric_to_redis(metric))
    
    async def record_database_metric(self, metric: DatabaseMetrics):
        """记录数据库指标"""
        # 存储到内存
        self._db_metrics.append(metric)
        
        # 更新聚合统计
        key = f"{metric.query_type}:{metric.table_name}"
        stats = self._db_stats[key]
        stats['count'] += 1
        stats['total_time'] += metric.execution_time
        stats['min_time'] = min(stats['min_time'], metric.execution_time)
        stats['max_time'] = max(stats['max_time'], metric.execution_time)
        
        # 更新Prometheus指标
        if self.enable_prometheus:
            self.db_query_count.labels(
                query_type=metric.query_type,
                table=metric.table_name
            ).inc()
            
            self.db_query_duration.labels(
                query_type=metric.query_type,
                table=metric.table_name
            ).observe(metric.execution_time)
        
        # 存储到Redis（异步）
        asyncio.create_task(self._store_db_metric_to_redis(metric))
    
    async def get_api_performance_summary(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """获取API性能摘要"""
        cutoff_time = datetime.now() - time_range
        
        # 过滤时间范围内的指标
        recent_metrics = [
            m for m in self._api_metrics
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # 计算统计信息
        total_requests = len(recent_metrics)
        total_errors = sum(1 for m in recent_metrics if m.status_code >= 400)
        response_times = [m.response_time for m in recent_metrics]
        
        # 按端点分组统计
        endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'avg_response_time': 0.0,
            'error_rate': 0.0
        })
        
        for metric in recent_metrics:
            key = f"{metric.method} {metric.endpoint}"
            endpoint_stats[key]['count'] += 1
            endpoint_stats[key]['total_time'] = endpoint_stats[key].get('total_time', 0) + metric.response_time
            if metric.status_code >= 400:
                endpoint_stats[key]['errors'] = endpoint_stats[key].get('errors', 0) + 1
        
        # 计算平均值和错误率
        for key, stats in endpoint_stats.items():
            stats['avg_response_time'] = stats['total_time'] / stats['count']
            stats['error_rate'] = (stats.get('errors', 0) / stats['count']) * 100
            del stats['total_time']  # 清理临时字段
        
        return {
            'time_range_hours': time_range.total_seconds() / 3600,
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': (total_errors / total_requests) * 100 if total_requests > 0 else 0,
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'p95_response_time': self._calculate_percentile(response_times, 95),
            'p99_response_time': self._calculate_percentile(response_times, 99),
            'endpoint_stats': dict(endpoint_stats)
        }
    
    async def get_database_performance_summary(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """获取数据库性能摘要"""
        cutoff_time = datetime.now() - time_range
        
        # 过滤时间范围内的指标
        recent_metrics = [
            m for m in self._db_metrics
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        # 计算统计信息
        total_queries = len(recent_metrics)
        execution_times = [m.execution_time for m in recent_metrics]
        
        # 按查询类型分组统计
        query_type_stats = defaultdict(lambda: {
            'count': 0,
            'avg_execution_time': 0.0,
            'total_rows_affected': 0
        })
        
        for metric in recent_metrics:
            key = f"{metric.query_type}:{metric.table_name}"
            query_type_stats[key]['count'] += 1
            query_type_stats[key]['total_time'] = query_type_stats[key].get('total_time', 0) + metric.execution_time
            query_type_stats[key]['total_rows_affected'] += metric.rows_affected
        
        # 计算平均值
        for key, stats in query_type_stats.items():
            stats['avg_execution_time'] = stats['total_time'] / stats['count']
            del stats['total_time']  # 清理临时字段
        
        return {
            'time_range_hours': time_range.total_seconds() / 3600,
            'total_queries': total_queries,
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'p95_execution_time': self._calculate_percentile(execution_times, 95),
            'p99_execution_time': self._calculate_percentile(execution_times, 99),
            'query_type_stats': dict(query_type_stats)
        }
    
    async def get_slow_queries(
        self,
        threshold_seconds: float = 1.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        slow_queries = [
            {
                'query_type': m.query_type,
                'table_name': m.table_name,
                'execution_time': m.execution_time,
                'rows_affected': m.rows_affected,
                'timestamp': m.timestamp.isoformat(),
                'query_hash': m.query_hash
            }
            for m in self._db_metrics
            if m.execution_time >= threshold_seconds
        ]
        
        # 按执行时间降序排序
        slow_queries.sort(key=lambda x: x['execution_time'], reverse=True)
        
        return slow_queries[:limit]
    
    async def get_error_analysis(
        self,
        time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, Any]:
        """获取错误分析"""
        cutoff_time = datetime.now() - time_range
        
        # 过滤错误请求
        error_metrics = [
            m for m in self._api_metrics
            if m.timestamp >= cutoff_time and m.status_code >= 400
        ]
        
        if not error_metrics:
            return {'total_errors': 0, 'error_breakdown': {}}
        
        # 按状态码分组
        error_breakdown = defaultdict(lambda: {
            'count': 0,
            'endpoints': defaultdict(int)
        })
        
        for metric in error_metrics:
            status_code = str(metric.status_code)
            error_breakdown[status_code]['count'] += 1
            error_breakdown[status_code]['endpoints'][f"{metric.method} {metric.endpoint}"] += 1
        
        return {
            'total_errors': len(error_metrics),
            'error_breakdown': dict(error_breakdown),
            'time_range_hours': time_range.total_seconds() / 3600
        }
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        index = min(index, len(sorted_values) - 1)
        
        return sorted_values[index]
    
    async def _store_api_metric_to_redis(self, metric: APIMetrics):
        """存储API指标到Redis"""
        try:
            metric_data = {
                'endpoint': metric.endpoint,
                'method': metric.method,
                'status_code': metric.status_code,
                'response_time': metric.response_time,
                'timestamp': metric.timestamp.isoformat(),
                'user_id': metric.user_id,
                'ip_address': metric.ip_address
            }
            
            # 存储到时间序列
            key = f"api_metrics:{datetime.now().strftime('%Y%m%d%H')}"
            await self.redis.lpush(key, json.dumps(metric_data))
            await self.redis.expire(key, 86400 * 7)  # 保留7天
            
        except Exception as e:
            logger.error(f"存储API指标到Redis失败: {e}")
    
    async def _store_db_metric_to_redis(self, metric: DatabaseMetrics):
        """存储数据库指标到Redis"""
        try:
            metric_data = {
                'query_type': metric.query_type,
                'table_name': metric.table_name,
                'execution_time': metric.execution_time,
                'rows_affected': metric.rows_affected,
                'timestamp': metric.timestamp.isoformat(),
                'query_hash': metric.query_hash
            }
            
            # 存储到时间序列
            key = f"db_metrics:{datetime.now().strftime('%Y%m%d%H')}"
            await self.redis.lpush(key, json.dumps(metric_data))
            await self.redis.expire(key, 86400 * 7)  # 保留7天
            
        except Exception as e:
            logger.error(f"存储数据库指标到Redis失败: {e}")
    
    async def _store_metrics_to_redis(self, metrics: List[PerformanceMetric]):
        """存储性能指标到Redis"""
        try:
            for metric in metrics:
                metric_data = {
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'tags': metric.tags,
                    'unit': metric.unit
                }
                
                key = f"system_metrics:{metric.name}:{datetime.now().strftime('%Y%m%d%H')}"
                await self.redis.lpush(key, json.dumps(metric_data))
                await self.redis.expire(key, 86400 * 7)  # 保留7天
                
        except Exception as e:
            logger.error(f"存储系统指标到Redis失败: {e}")
    
    async def cleanup(self):
        """清理资源"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass


# 性能监控装饰器
def monitor_performance(
    monitor: PerformanceMonitor,
    endpoint: str = "",
    query_type: str = "",
    table_name: str = ""
):
    """性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if endpoint:
                # API监控
                async with monitor.track_api_request(endpoint, "FUNC"):
                    return await func(*args, **kwargs)
            elif query_type and table_name:
                # 数据库监控
                async with monitor.track_database_query(query_type, table_name):
                    return await func(*args, **kwargs)
            else:
                # 普通函数监控
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    execution_time = time.time() - start_time
                    logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.3f}s")
        
        return wrapper
    return decorator