#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能监控服务
监控健康数据服务的性能指标和系统状态
"""

import asyncio
import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from loguru import logger

import aioredis
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    database_connections: int
    cache_hit_rate: float
    api_response_time: float
    error_rate: float
    throughput: float  # 每秒处理请求数


@dataclass
class APIMetrics:
    """API指标"""
    endpoint: str
    method: str
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    request_count: int = 0
    error_count: int = 0
    last_request_time: Optional[datetime] = None


@dataclass
class DatabaseMetrics:
    """数据库指标"""
    query_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    connection_count: int = 0
    slow_query_count: int = 0
    error_count: int = 0


@dataclass
class CacheMetrics:
    """缓存指标"""
    hit_count: int = 0
    miss_count: int = 0
    set_count: int = 0
    delete_count: int = 0
    memory_usage: float = 0.0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能监控器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.is_running = False
        self.monitor_thread = None
        
        # 指标存储
        self.metrics_history: deque = deque(maxlen=1000)
        self.api_metrics: Dict[str, APIMetrics] = defaultdict(APIMetrics)
        self.database_metrics = DatabaseMetrics()
        self.cache_metrics = CacheMetrics()
        
        # 告警配置
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'api_response_time': 5.0,  # 秒
            'error_rate': 5.0,  # 百分比
            'database_connections': 50
        }
        
        # 告警回调
        self.alert_callbacks: List[Callable] = []
        
        # Redis连接（用于分布式监控）
        self.redis_client: Optional[aioredis.Redis] = None
        
        # 监控间隔
        self.monitor_interval = config.get('monitor_interval', 30)  # 秒
    
    async def initialize(self) -> None:
        """初始化监控器"""
        try:
            # 初始化Redis连接
            redis_config = self.config.get('redis', {})
            if redis_config:
                self.redis_client = aioredis.from_url(
                    f"redis://{redis_config.get('host', 'localhost')}:"
                    f"{redis_config.get('port', 6379)}/{redis_config.get('db', 0)}"
                )
            
            logger.info("性能监控器初始化完成")
            
        except Exception as e:
            logger.error(f"性能监控器初始化失败: {e}")
            raise
    
    def start_monitoring(self) -> None:
        """开始监控"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self) -> None:
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("性能监控已停止")
    
    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.is_running:
            try:
                # 收集系统指标
                metrics = self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # 检查告警
                self._check_alerts(metrics)
                
                # 保存到Redis（如果配置了）
                if self.redis_client:
                    asyncio.create_task(self._save_metrics_to_redis(metrics))
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"监控循环出错: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """收集系统指标"""
        # CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # 网络IO
        network_io = psutil.net_io_counters()._asdict()
        
        # 计算API响应时间平均值
        api_response_time = self._calculate_average_response_time()
        
        # 计算错误率
        error_rate = self._calculate_error_rate()
        
        # 计算吞吐量
        throughput = self._calculate_throughput()
        
        # 计算缓存命中率
        cache_hit_rate = self._calculate_cache_hit_rate()
        
        return PerformanceMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_io=network_io,
            database_connections=self.database_metrics.connection_count,
            cache_hit_rate=cache_hit_rate,
            api_response_time=api_response_time,
            error_rate=error_rate,
            throughput=throughput
        )
    
    def _calculate_average_response_time(self) -> float:
        """计算平均API响应时间"""
        all_times = []
        for api_metric in self.api_metrics.values():
            all_times.extend(api_metric.response_times)
        
        if all_times:
            return sum(all_times) / len(all_times)
        return 0.0
    
    def _calculate_error_rate(self) -> float:
        """计算错误率"""
        total_requests = sum(api.request_count for api in self.api_metrics.values())
        total_errors = sum(api.error_count for api in self.api_metrics.values())
        
        if total_requests > 0:
            return (total_errors / total_requests) * 100
        return 0.0
    
    def _calculate_throughput(self) -> float:
        """计算吞吐量（每秒请求数）"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        recent_requests = 0
        for api_metric in self.api_metrics.values():
            if api_metric.last_request_time and api_metric.last_request_time >= one_minute_ago:
                recent_requests += 1
        
        return recent_requests / 60.0  # 每秒请求数
    
    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        total_requests = self.cache_metrics.hit_count + self.cache_metrics.miss_count
        if total_requests > 0:
            return (self.cache_metrics.hit_count / total_requests) * 100
        return 0.0
    
    def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        """检查告警条件"""
        alerts = []
        
        # CPU使用率告警
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            alerts.append({
                'type': 'cpu_high',
                'message': f'CPU使用率过高: {metrics.cpu_usage:.1f}%',
                'value': metrics.cpu_usage,
                'threshold': self.alert_thresholds['cpu_usage']
            })
        
        # 内存使用率告警
        if metrics.memory_usage > self.alert_thresholds['memory_usage']:
            alerts.append({
                'type': 'memory_high',
                'message': f'内存使用率过高: {metrics.memory_usage:.1f}%',
                'value': metrics.memory_usage,
                'threshold': self.alert_thresholds['memory_usage']
            })
        
        # 磁盘使用率告警
        if metrics.disk_usage > self.alert_thresholds['disk_usage']:
            alerts.append({
                'type': 'disk_high',
                'message': f'磁盘使用率过高: {metrics.disk_usage:.1f}%',
                'value': metrics.disk_usage,
                'threshold': self.alert_thresholds['disk_usage']
            })
        
        # API响应时间告警
        if metrics.api_response_time > self.alert_thresholds['api_response_time']:
            alerts.append({
                'type': 'response_time_high',
                'message': f'API响应时间过长: {metrics.api_response_time:.2f}秒',
                'value': metrics.api_response_time,
                'threshold': self.alert_thresholds['api_response_time']
            })
        
        # 错误率告警
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'error_rate_high',
                'message': f'错误率过高: {metrics.error_rate:.1f}%',
                'value': metrics.error_rate,
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # 数据库连接数告警
        if metrics.database_connections > self.alert_thresholds['database_connections']:
            alerts.append({
                'type': 'db_connections_high',
                'message': f'数据库连接数过多: {metrics.database_connections}',
                'value': metrics.database_connections,
                'threshold': self.alert_thresholds['database_connections']
            })
        
        # 触发告警回调
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Dict[str, Any]) -> None:
        """触发告警"""
        logger.warning(f"性能告警: {alert['message']}")
        
        # 调用注册的告警回调
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"告警回调执行失败: {e}")
    
    async def _save_metrics_to_redis(self, metrics: PerformanceMetrics) -> None:
        """保存指标到Redis"""
        try:
            if not self.redis_client:
                return
            
            # 保存最新指标
            metrics_data = {
                'timestamp': metrics.timestamp.isoformat(),
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'disk_usage': metrics.disk_usage,
                'database_connections': metrics.database_connections,
                'cache_hit_rate': metrics.cache_hit_rate,
                'api_response_time': metrics.api_response_time,
                'error_rate': metrics.error_rate,
                'throughput': metrics.throughput
            }
            
            await self.redis_client.hset('health_data_service:metrics', mapping=metrics_data)
            
            # 保存历史指标（保留24小时）
            await self.redis_client.zadd(
                'health_data_service:metrics_history',
                {str(metrics_data): time.time()}
            )
            
            # 清理过期数据
            cutoff_time = time.time() - 24 * 3600  # 24小时前
            await self.redis_client.zremrangebyscore(
                'health_data_service:metrics_history',
                0,
                cutoff_time
            )
            
        except Exception as e:
            logger.error(f"保存指标到Redis失败: {e}")
    
    def record_api_request(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        is_error: bool = False
    ) -> None:
        """记录API请求指标"""
        key = f"{method}:{endpoint}"
        
        if key not in self.api_metrics:
            self.api_metrics[key] = APIMetrics(endpoint=endpoint, method=method)
        
        api_metric = self.api_metrics[key]
        api_metric.response_times.append(response_time)
        api_metric.request_count += 1
        api_metric.last_request_time = datetime.utcnow()
        
        if is_error:
            api_metric.error_count += 1
    
    def record_database_query(self, query_time: float, is_slow: bool = False, is_error: bool = False) -> None:
        """记录数据库查询指标"""
        self.database_metrics.query_times.append(query_time)
        
        if is_slow:
            self.database_metrics.slow_query_count += 1
        
        if is_error:
            self.database_metrics.error_count += 1
    
    def record_database_connection(self, count: int) -> None:
        """记录数据库连接数"""
        self.database_metrics.connection_count = count
    
    def record_cache_operation(self, operation: str, hit: bool = False) -> None:
        """记录缓存操作指标"""
        if operation == 'get':
            if hit:
                self.cache_metrics.hit_count += 1
            else:
                self.cache_metrics.miss_count += 1
        elif operation == 'set':
            self.cache_metrics.set_count += 1
        elif operation == 'delete':
            self.cache_metrics.delete_count += 1
    
    def add_alert_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前指标"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, hours: int = 1) -> List[PerformanceMetrics]:
        """获取历史指标"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if metrics.timestamp >= cutoff_time
        ]
    
    def get_api_metrics_summary(self) -> Dict[str, Any]:
        """获取API指标摘要"""
        summary = {}
        
        for key, api_metric in self.api_metrics.items():
            if api_metric.response_times:
                avg_response_time = sum(api_metric.response_times) / len(api_metric.response_times)
                max_response_time = max(api_metric.response_times)
                min_response_time = min(api_metric.response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0.0
            
            error_rate = 0.0
            if api_metric.request_count > 0:
                error_rate = (api_metric.error_count / api_metric.request_count) * 100
            
            summary[key] = {
                'endpoint': api_metric.endpoint,
                'method': api_metric.method,
                'request_count': api_metric.request_count,
                'error_count': api_metric.error_count,
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'max_response_time': max_response_time,
                'min_response_time': min_response_time,
                'last_request_time': api_metric.last_request_time.isoformat() if api_metric.last_request_time else None
            }
        
        return summary
    
    def get_database_metrics_summary(self) -> Dict[str, Any]:
        """获取数据库指标摘要"""
        if self.database_metrics.query_times:
            avg_query_time = sum(self.database_metrics.query_times) / len(self.database_metrics.query_times)
            max_query_time = max(self.database_metrics.query_times)
            min_query_time = min(self.database_metrics.query_times)
        else:
            avg_query_time = max_query_time = min_query_time = 0.0
        
        return {
            'connection_count': self.database_metrics.connection_count,
            'query_count': len(self.database_metrics.query_times),
            'slow_query_count': self.database_metrics.slow_query_count,
            'error_count': self.database_metrics.error_count,
            'avg_query_time': avg_query_time,
            'max_query_time': max_query_time,
            'min_query_time': min_query_time
        }
    
    def get_cache_metrics_summary(self) -> Dict[str, Any]:
        """获取缓存指标摘要"""
        total_requests = self.cache_metrics.hit_count + self.cache_metrics.miss_count
        hit_rate = 0.0
        if total_requests > 0:
            hit_rate = (self.cache_metrics.hit_count / total_requests) * 100
        
        return {
            'hit_count': self.cache_metrics.hit_count,
            'miss_count': self.cache_metrics.miss_count,
            'set_count': self.cache_metrics.set_count,
            'delete_count': self.cache_metrics.delete_count,
            'hit_rate': hit_rate,
            'memory_usage': self.cache_metrics.memory_usage
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        current_metrics = self.get_current_metrics()
        
        if not current_metrics:
            return {
                'status': 'unknown',
                'message': '无法获取当前指标'
            }
        
        # 检查各项指标是否正常
        issues = []
        
        if current_metrics.cpu_usage > self.alert_thresholds['cpu_usage']:
            issues.append(f'CPU使用率过高: {current_metrics.cpu_usage:.1f}%')
        
        if current_metrics.memory_usage > self.alert_thresholds['memory_usage']:
            issues.append(f'内存使用率过高: {current_metrics.memory_usage:.1f}%')
        
        if current_metrics.disk_usage > self.alert_thresholds['disk_usage']:
            issues.append(f'磁盘使用率过高: {current_metrics.disk_usage:.1f}%')
        
        if current_metrics.api_response_time > self.alert_thresholds['api_response_time']:
            issues.append(f'API响应时间过长: {current_metrics.api_response_time:.2f}秒')
        
        if current_metrics.error_rate > self.alert_thresholds['error_rate']:
            issues.append(f'错误率过高: {current_metrics.error_rate:.1f}%')
        
        if issues:
            status = 'warning' if len(issues) <= 2 else 'critical'
            message = '; '.join(issues)
        else:
            status = 'healthy'
            message = '所有指标正常'
        
        return {
            'status': status,
            'message': message,
            'timestamp': current_metrics.timestamp.isoformat(),
            'metrics': {
                'cpu_usage': current_metrics.cpu_usage,
                'memory_usage': current_metrics.memory_usage,
                'disk_usage': current_metrics.disk_usage,
                'api_response_time': current_metrics.api_response_time,
                'error_rate': current_metrics.error_rate,
                'throughput': current_metrics.throughput,
                'cache_hit_rate': current_metrics.cache_hit_rate
            }
        }
    
    async def cleanup(self) -> None:
        """清理资源"""
        self.stop_monitoring()
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("性能监控器已清理")


# 装饰器：监控API性能
def monitor_api_performance(monitor: PerformanceMonitor):
    """API性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            is_error = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                is_error = True
                raise
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                
                # 从函数名或路由信息获取endpoint
                endpoint = getattr(func, '__name__', 'unknown')
                method = 'GET'  # 默认方法，实际应该从请求中获取
                
                monitor.record_api_request(endpoint, method, response_time, is_error)
        
        return wrapper
    return decorator


# 装饰器：监控数据库查询性能
def monitor_database_performance(monitor: PerformanceMonitor, slow_threshold: float = 1.0):
    """数据库性能监控装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            is_error = False
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                is_error = True
                raise
            finally:
                end_time = time.time()
                query_time = end_time - start_time
                is_slow = query_time > slow_threshold
                
                monitor.record_database_query(query_time, is_slow, is_error)
        
        return wrapper
    return decorator 