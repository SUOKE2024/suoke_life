"""用户服务性能优化模块"""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any, Callable, TypeVar, Union
from functools import wraps, lru_cache
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog
import psutil
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.config import get_settings
from user_service.database import get_async_session

logger = structlog.get_logger()

T = TypeVar('T')


@dataclass
class PerformanceMetrics:
    """性能指标"""
    operation_name: str
    execution_time: float
    memory_usage: int
    cache_hit: bool
    timestamp: datetime


@dataclass
class QueryOptimization:
    """查询优化配置"""
    use_index_hints: bool = True
    batch_size: int = 1000
    connection_timeout: int = 30
    query_timeout: int = 60
    enable_query_cache: bool = True
    cache_ttl: int = 300


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.metrics: List[PerformanceMetrics] = []
        self._slow_queries: List[Dict[str, Any]] = []
        self._performance_thresholds = {
            "query_time": 1.0,  # 秒
            "memory_usage": 100 * 1024 * 1024,  # 100MB
            "cache_hit_rate": 0.8  # 80%
        }
    
    def record_metric(self, metric: PerformanceMetrics):
        """记录性能指标"""
        self.metrics.append(metric)
        
        # 检查是否为慢查询
        if metric.execution_time > self._performance_thresholds["query_time"]:
            self._slow_queries.append({
                "operation": metric.operation_name,
                "execution_time": metric.execution_time,
                "timestamp": metric.timestamp,
                "memory_usage": metric.memory_usage
            })
        
        # 保持最近1000条记录
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
        
        # 保持最近100条慢查询记录
        if len(self._slow_queries) > 100:
            self._slow_queries = self._slow_queries[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics:
            return {"message": "No metrics available"}
        
        recent_metrics = [m for m in self.metrics if m.timestamp > datetime.utcnow() - timedelta(hours=1)]
        
        if not recent_metrics:
            return {"message": "No recent metrics available"}
        
        avg_execution_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        avg_memory_usage = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        cache_hits = sum(1 for m in recent_metrics if m.cache_hit)
        cache_hit_rate = cache_hits / len(recent_metrics) if recent_metrics else 0
        
        slow_queries_count = len([m for m in recent_metrics if m.execution_time > self._performance_thresholds["query_time"]])
        
        return {
            "time_range": "last_hour",
            "total_operations": len(recent_metrics),
            "avg_execution_time": avg_execution_time,
            "avg_memory_usage": avg_memory_usage,
            "cache_hit_rate": cache_hit_rate,
            "slow_queries_count": slow_queries_count,
            "performance_score": self._calculate_performance_score(recent_metrics)
        }
    
    def get_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        return sorted(self._slow_queries, key=lambda x: x["execution_time"], reverse=True)[:limit]
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetrics]) -> float:
        """计算性能评分"""
        if not metrics:
            return 0.0
        
        # 基于执行时间、内存使用和缓存命中率计算评分
        avg_time = sum(m.execution_time for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_usage for m in metrics) / len(metrics)
        cache_hit_rate = sum(1 for m in metrics if m.cache_hit) / len(metrics)
        
        time_score = max(0, 100 - (avg_time * 100))  # 时间越短分数越高
        memory_score = max(0, 100 - (avg_memory / (1024 * 1024)))  # 内存使用越少分数越高
        cache_score = cache_hit_rate * 100  # 缓存命中率越高分数越高
        
        return (time_score * 0.4 + memory_score * 0.3 + cache_score * 0.3)


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.optimization_config = QueryOptimization()
        self._query_cache: Dict[str, Any] = {}
        self._query_stats: Dict[str, Dict[str, Any]] = {}
    
    def optimize_query(self, query: str, params: Optional[Dict] = None) -> str:
        """优化查询语句"""
        # 添加查询提示
        if self.optimization_config.use_index_hints:
            query = self._add_index_hints(query)
        
        # 添加查询限制
        if "LIMIT" not in query.upper() and "SELECT" in query.upper():
            query += f" LIMIT {self.optimization_config.batch_size}"
        
        return query
    
    def _add_index_hints(self, query: str) -> str:
        """添加索引提示"""
        # 简化的索引提示逻辑
        if "WHERE" in query.upper():
            # 为常见的查询模式添加索引提示
            if "user_id" in query.lower():
                query = query.replace("WHERE", "/*+ INDEX(users idx_user_id) */ WHERE")
            elif "email" in query.lower():
                query = query.replace("WHERE", "/*+ INDEX(users idx_email) */ WHERE")
        
        return query
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """获取缓存结果"""
        if not self.optimization_config.enable_query_cache:
            return None
        
        cached_data = self._query_cache.get(cache_key)
        if cached_data:
            # 检查是否过期
            if datetime.utcnow() - cached_data["timestamp"] < timedelta(seconds=self.optimization_config.cache_ttl):
                return cached_data["result"]
            else:
                # 删除过期缓存
                del self._query_cache[cache_key]
        
        return None
    
    def cache_result(self, cache_key: str, result: Any):
        """缓存查询结果"""
        if self.optimization_config.enable_query_cache:
            self._query_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.utcnow()
            }
    
    def record_query_stats(self, query: str, execution_time: float, result_count: int):
        """记录查询统计"""
        query_hash = str(hash(query))
        
        if query_hash not in self._query_stats:
            self._query_stats[query_hash] = {
                "query": query[:200],  # 只保存前200个字符
                "execution_count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "max_time": 0.0,
                "min_time": float('inf'),
                "total_results": 0
            }
        
        stats = self._query_stats[query_hash]
        stats["execution_count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["execution_count"]
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["min_time"] = min(stats["min_time"], execution_time)
        stats["total_results"] += result_count
    
    def get_query_stats(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取查询统计"""
        return sorted(
            list(self._query_stats.values()),
            key=lambda x: x["avg_time"],
            reverse=True
        )[:limit]


class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._pool_stats = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
            "connection_errors": 0,
            "pool_exhausted_count": 0
        }
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """获取连接池状态"""
        try:
            from user_service.database import _async_engine
            
            if _async_engine:
                pool = _async_engine.pool
                return {
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                    "invalid": pool.invalid(),
                    "status": "healthy" if pool.checkedin() > 0 else "warning"
                }
            else:
                return {"status": "not_initialized"}
        except Exception as e:
            logger.error("Failed to get pool status", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def record_connection_event(self, event_type: str):
        """记录连接事件"""
        if event_type == "connection_error":
            self._pool_stats["connection_errors"] += 1
        elif event_type == "pool_exhausted":
            self._pool_stats["pool_exhausted_count"] += 1
    
    def get_pool_metrics(self) -> Dict[str, Any]:
        """获取连接池指标"""
        return self._pool_stats.copy()


class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._memory_usage_history: List[Dict[str, Any]] = []
    
    def optimize_memory_usage(self):
        """优化内存使用"""
        import gc
        
        # 强制垃圾回收
        collected = gc.collect()
        
        # 记录内存使用情况
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        self._memory_usage_history.append({
            "timestamp": datetime.utcnow(),
            "rss": memory_info.rss,
            "vms": memory_info.vms,
            "collected_objects": collected
        })
        
        # 保持最近100条记录
        if len(self._memory_usage_history) > 100:
            self._memory_usage_history = self._memory_usage_history[-100:]
        
        logger.info(
            "Memory optimization completed",
            collected_objects=collected,
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计"""
        if not self._memory_usage_history:
            return {"message": "No memory history available"}
        
        recent_usage = self._memory_usage_history[-10:]  # 最近10次记录
        
        avg_rss = sum(record["rss"] for record in recent_usage) / len(recent_usage)
        avg_vms = sum(record["vms"] for record in recent_usage) / len(recent_usage)
        
        return {
            "avg_rss_mb": avg_rss / 1024 / 1024,
            "avg_vms_mb": avg_vms / 1024 / 1024,
            "optimization_count": len(self._memory_usage_history),
            "last_optimization": self._memory_usage_history[-1]["timestamp"].isoformat()
        }


def performance_monitor(operation_name: str):
    """性能监控装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            start_memory = _get_memory_usage()
            
            try:
                result = await func(*args, **kwargs)
                cache_hit = kwargs.get('_cache_hit', False)
                
                # 记录性能指标
                execution_time = time.time() - start_time
                memory_usage = _get_memory_usage() - start_memory
                
                metric = PerformanceMetrics(
                    operation_name=operation_name,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    cache_hit=cache_hit,
                    timestamp=datetime.utcnow()
                )
                
                monitor = get_performance_monitor()
                monitor.record_metric(metric)
                
                return result
            except Exception as e:
                # 记录错误指标
                execution_time = time.time() - start_time
                logger.error(
                    "Performance monitoring error",
                    operation=operation_name,
                    execution_time=execution_time,
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            start_memory = _get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                cache_hit = kwargs.get('_cache_hit', False)
                
                # 记录性能指标
                execution_time = time.time() - start_time
                memory_usage = _get_memory_usage() - start_memory
                
                metric = PerformanceMetrics(
                    operation_name=operation_name,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    cache_hit=cache_hit,
                    timestamp=datetime.utcnow()
                )
                
                monitor = get_performance_monitor()
                monitor.record_metric(metric)
                
                return result
            except Exception as e:
                # 记录错误指标
                execution_time = time.time() - start_time
                logger.error(
                    "Performance monitoring error",
                    operation=operation_name,
                    execution_time=execution_time,
                    error=str(e)
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def query_cache(cache_key_func: Callable = None, ttl: int = 300):
    """查询缓存装饰器"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            optimizer = get_query_optimizer()
            
            # 尝试从缓存获取结果
            cached_result = optimizer.get_cached_result(cache_key)
            if cached_result is not None:
                kwargs['_cache_hit'] = True
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            optimizer.cache_result(cache_key, result)
            kwargs['_cache_hit'] = False
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            optimizer = get_query_optimizer()
            
            # 尝试从缓存获取结果
            cached_result = optimizer.get_cached_result(cache_key)
            if cached_result is not None:
                kwargs['_cache_hit'] = True
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            optimizer.cache_result(cache_key, result)
            kwargs['_cache_hit'] = False
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def _get_memory_usage() -> int:
    """获取当前内存使用量"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss
    except Exception:
        return 0


class BatchProcessor:
    """批处理器"""
    
    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
    
    async def process_in_batches(
        self, 
        items: List[Any], 
        processor: Callable[[List[Any]], Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """批量处理数据"""
        results = []
        total_items = len(items)
        
        for i in range(0, total_items, self.batch_size):
            batch = items[i:i + self.batch_size]
            
            try:
                batch_result = await processor(batch) if asyncio.iscoroutinefunction(processor) else processor(batch)
                results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
                
                if progress_callback:
                    progress_callback(i + len(batch), total_items)
                
            except Exception as e:
                logger.error(
                    "Batch processing error",
                    batch_start=i,
                    batch_size=len(batch),
                    error=str(e)
                )
                raise
        
        return results


# 全局实例
_performance_monitor: Optional[PerformanceMonitor] = None
_query_optimizer: Optional[QueryOptimizer] = None
_connection_pool_manager: Optional[ConnectionPoolManager] = None
_memory_optimizer: Optional[MemoryOptimizer] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器"""
    global _performance_monitor
    if not _performance_monitor:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_query_optimizer() -> QueryOptimizer:
    """获取查询优化器"""
    global _query_optimizer
    if not _query_optimizer:
        _query_optimizer = QueryOptimizer()
    return _query_optimizer


def get_connection_pool_manager() -> ConnectionPoolManager:
    """获取连接池管理器"""
    global _connection_pool_manager
    if not _connection_pool_manager:
        _connection_pool_manager = ConnectionPoolManager()
    return _connection_pool_manager


def get_memory_optimizer() -> MemoryOptimizer:
    """获取内存优化器"""
    global _memory_optimizer
    if not _memory_optimizer:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer