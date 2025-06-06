"""
performance - 索克生活项目模块
"""

        import aioredis
    import redis.asyncio as aioredis
from .config import settings
from .models import ReviewTaskDB, ReviewerDB
from datetime import datetime, timedelta, timezone
from functools import wraps
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import asyncio
import hashlib
import json
import structlog
import time

"""
性能优化模块
Performance Optimization Module

提供缓存策略、查询优化、性能监控等功能
"""


try:
except ImportError:
    try:
    except ImportError:
        aioredis = None


logger = structlog.get_logger(__name__)


class CacheManager:
    """缓存管理器"""

    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """初始化缓存管理器
        
        Args:
            redis_client: Redis客户端
        """
        self.redis_client = redis_client
        self.default_ttl = 3600  # 默认1小时过期
        self.key_prefix = "human_review_service:"

    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.key_prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._make_key(key)
            value = await self.redis_client.get(cache_key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Failed to get cache", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            serialized_value = json.dumps(value, default=str)
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(cache_key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.warning("Failed to set cache", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            result = await self.redis_client.delete(cache_key)
            return result > 0
        except Exception as e:
            logger.warning("Failed to delete cache", key=key, error=str(e))
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        if not self.redis_client:
            return 0
        
        try:
            cache_pattern = self._make_key(pattern)
            keys = await self.redis_client.keys(cache_pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("Failed to clear cache pattern", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            return await self.redis_client.exists(cache_key) > 0
        except Exception as e:
            logger.warning("Failed to check cache existence", key=key, error=str(e))
            return False

    async def get_ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        if not self.redis_client:
            return -1
        
        try:
            cache_key = self._make_key(key)
            return await self.redis_client.ttl(cache_key)
        except Exception as e:
            logger.warning("Failed to get cache TTL", key=key, error=str(e))
            return -1


class QueryOptimizer:
    """查询优化器"""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """初始化查询优化器
        
        Args:
            cache_manager: 缓存管理器
        """
        self.cache_manager = cache_manager

    def _generate_cache_key(self, query_type: str, params: Dict[str, Any]) -> str:
        """生成查询缓存键"""
        # 对参数进行排序和序列化，确保相同参数生成相同的键
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(sorted_params.encode()).hexdigest()
        return f"query:{query_type}:{param_hash}"

    async def get_cached_query_result(
        self, 
        query_type: str, 
        params: Dict[str, Any],
        ttl: int = 300
    ) -> Optional[Any]:
        """获取缓存的查询结果"""
        if not self.cache_manager:
            return None
        
        cache_key = self._generate_cache_key(query_type, params)
        return await self.cache_manager.get(cache_key)

    async def cache_query_result(
        self, 
        query_type: str, 
        params: Dict[str, Any], 
        result: Any,
        ttl: int = 300
    ) -> bool:
        """缓存查询结果"""
        if not self.cache_manager:
            return False
        
        cache_key = self._generate_cache_key(query_type, params)
        return await self.cache_manager.set(cache_key, result, ttl)

    async def get_optimized_pending_tasks(
        self, 
        session: AsyncSession, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """优化的待审核任务查询"""
        params = {"limit": limit, "offset": offset}
        
        # 尝试从缓存获取
        cached_result = await self.get_cached_query_result("pending_tasks", params, ttl=60)
        if cached_result:
            logger.debug("Using cached pending tasks", params=params)
            return cached_result
        
        # 执行优化的查询
        query = text("""
            SELECT 
                rt.id,
                rt.task_id,
                rt.review_type,
                rt.priority,
                rt.created_at,
                rt.expires_at,
                rt.risk_score,
                rt.estimated_duration,
                r.name as reviewer_name,
                r.reviewer_id
            FROM review_tasks rt
            LEFT JOIN reviewers r ON rt.assigned_to = r.reviewer_id
            WHERE rt.status = 'pending'
            ORDER BY 
                CASE rt.priority 
                    WHEN 'critical' THEN 1
                    WHEN 'urgent' THEN 2
                    WHEN 'high' THEN 3
                    WHEN 'normal' THEN 4
                    WHEN 'low' THEN 5
                END,
                rt.created_at ASC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await session.execute(query, {"limit": limit, "offset": offset})
        tasks = [dict(row._mapping) for row in result]
        
        # 缓存结果
        await self.cache_query_result("pending_tasks", params, tasks, ttl=60)
        
        logger.debug("Executed optimized pending tasks query", count=len(tasks))
        return tasks

    async def get_optimized_reviewer_workload(
        self, 
        session: AsyncSession, 
        reviewer_id: str
    ) -> Dict[str, Any]:
        """优化的审核员工作负载查询"""
        params = {"reviewer_id": reviewer_id}
        
        # 尝试从缓存获取
        cached_result = await self.get_cached_query_result("reviewer_workload", params, ttl=120)
        if cached_result:
            logger.debug("Using cached reviewer workload", reviewer_id=reviewer_id)
            return cached_result
        
        # 执行优化的查询
        query = text("""
            SELECT 
                r.reviewer_id,
                r.name,
                r.current_task_count,
                r.max_concurrent_tasks,
                r.total_reviews_completed,
                r.average_review_time,
                COUNT(CASE WHEN rt.status IN ('assigned', 'in_progress') THEN 1 END) as active_tasks,
                COUNT(CASE WHEN rt.status = 'assigned' THEN 1 END) as pending_tasks,
                COUNT(CASE WHEN rt.status = 'in_progress' THEN 1 END) as in_progress_tasks,
                AVG(CASE WHEN rt.status IN ('approved', 'rejected') AND rt.actual_duration IS NOT NULL 
                    THEN rt.actual_duration END) as avg_completion_time
            FROM reviewers r
            LEFT JOIN review_tasks rt ON r.reviewer_id = rt.assigned_to
            WHERE r.reviewer_id = :reviewer_id
            GROUP BY r.reviewer_id, r.name, r.current_task_count, r.max_concurrent_tasks, 
                     r.total_reviews_completed, r.average_review_time
        """)
        
        result = await session.execute(query, {"reviewer_id": reviewer_id})
        row = result.first()
        
        if not row:
            return {}
        
        workload = dict(row._mapping)
        
        # 计算工作负载百分比
        if workload.get("max_concurrent_tasks", 0) > 0:
            workload["workload_percentage"] = (
                workload.get("active_tasks", 0) / workload["max_concurrent_tasks"] * 100
            )
        else:
            workload["workload_percentage"] = 0
        
        # 缓存结果
        await self.cache_query_result("reviewer_workload", params, workload, ttl=120)
        
        logger.debug("Executed optimized reviewer workload query", reviewer_id=reviewer_id)
        return workload

    async def get_optimized_dashboard_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """优化的仪表板统计查询"""
        params = {}
        
        # 尝试从缓存获取
        cached_result = await self.get_cached_query_result("dashboard_stats", params, ttl=300)
        if cached_result:
            logger.debug("Using cached dashboard stats")
            return cached_result
        
        # 执行优化的统计查询
        stats_query = text("""
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                COUNT(CASE WHEN status = 'assigned' THEN 1 END) as assigned_tasks,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_tasks,
                COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_tasks,
                COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_tasks,
                AVG(CASE WHEN actual_duration IS NOT NULL THEN actual_duration END) as avg_completion_time,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as tasks_last_24h,
                COUNT(CASE WHEN expires_at < NOW() AND status IN ('pending', 'assigned', 'in_progress') THEN 1 END) as expired_tasks
            FROM review_tasks
        """)
        
        reviewer_stats_query = text("""
            SELECT 
                COUNT(*) as total_reviewers,
                COUNT(CASE WHEN is_available = true THEN 1 END) as available_reviewers,
                SUM(current_task_count) as total_active_tasks,
                AVG(current_task_count) as avg_tasks_per_reviewer
            FROM reviewers
        """)
        
        # 执行查询
        stats_result = await session.execute(stats_query)
        reviewer_result = await session.execute(reviewer_stats_query)
        
        stats = dict(stats_result.first()._mapping)
        reviewer_stats = dict(reviewer_result.first()._mapping)
        
        # 合并统计数据
        dashboard_stats = {**stats, **reviewer_stats}
        
        # 计算额外指标
        if dashboard_stats.get("total_tasks", 0) > 0:
            dashboard_stats["completion_rate"] = (
                (dashboard_stats.get("approved_tasks", 0) + dashboard_stats.get("rejected_tasks", 0)) /
                dashboard_stats["total_tasks"] * 100
            )
        else:
            dashboard_stats["completion_rate"] = 0
        
        # 缓存结果
        await self.cache_query_result("dashboard_stats", params, dashboard_stats, ttl=300)
        
        logger.debug("Executed optimized dashboard stats query")
        return dashboard_stats


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        """初始化性能监控器"""
        self.metrics = {}
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）

        @cache(timeout=300)  # 5分钟缓存
def record_query_time(self, query_type: str, duration: float):
        """记录查询时间"""
        if query_type not in self.metrics:
            self.metrics[query_type] = {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "slow_queries": 0
            }
        
        metrics = self.metrics[query_type]
        metrics["count"] += 1
        metrics["total_time"] += duration
        metrics["min_time"] = min(metrics["min_time"], duration)
        metrics["max_time"] = max(metrics["max_time"], duration)
        
        if duration > self.slow_query_threshold:
            metrics["slow_queries"] += 1
            logger.warning(
                "Slow query detected",
                query_type=query_type,
                duration=duration,
                threshold=self.slow_query_threshold
            )

    def get_query_stats(self, query_type: str) -> Dict[str, Any]:
        """获取查询统计"""
        if query_type not in self.metrics:
            return {}
        
        metrics = self.metrics[query_type]
        avg_time = metrics["total_time"] / metrics["count"] if metrics["count"] > 0 else 0
        
        return {
            "query_type": query_type,
            "count": metrics["count"],
            "avg_time": avg_time,
            "min_time": metrics["min_time"] if metrics["min_time"] != float("inf") else 0,
            "max_time": metrics["max_time"],
            "total_time": metrics["total_time"],
            "slow_queries": metrics["slow_queries"],
            "slow_query_rate": metrics["slow_queries"] / metrics["count"] * 100 if metrics["count"] > 0 else 0
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有查询统计"""
        return {query_type: self.get_query_stats(query_type) for query_type in self.metrics.keys()}

    def reset_stats(self):
        """重置统计数据"""
        self.metrics.clear()


def performance_monitor(query_type: str):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                # 这里可以记录到全局性能监控器
                logger.debug(
                    "Query performance",
                    query_type=query_type,
                    duration=duration,
                    function=func.__name__
                )
        return wrapper
    return decorator


def cache_result(cache_key_func: Callable, ttl: int = 300):
    """结果缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_key_func(*args, **kwargs)
            
            # 尝试从缓存获取
            # 这里需要访问缓存管理器实例
            # 实际使用时需要从参数或全局变量获取
            
            # 如果缓存未命中，执行原函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            # 这里需要实际的缓存逻辑
            
            return result
        return wrapper
    return decorator


class ConnectionPoolOptimizer:
    """连接池优化器"""

    def __init__(self):
        """初始化连接池优化器"""
        self.pool_stats = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
            "connection_errors": 0,
            "connection_timeouts": 0
        }

    def get_connection_stats(self) -> Dict[str, int]:
        """获取连接统计信息"""
        return {
            "active": 5,  # 模拟活跃连接数
            "idle": 3,    # 模拟空闲连接数
            "total": 8,   # 总连接数
            "max_pool_size": 20,  # 最大池大小
        }

    async def optimize_pool_size(self, current_load: float) -> Dict[str, int]:
        """根据当前负载优化连接池大小"""
        base_pool_size = settings.database.pool_size
        max_overflow = settings.database.max_overflow
        
        # 根据负载调整连接池大小
        if current_load > 0.8:
            # 高负载时增加连接池大小
            recommended_pool_size = min(base_pool_size * 2, base_pool_size + max_overflow)
            recommended_overflow = max_overflow
        elif current_load < 0.3:
            # 低负载时减少连接池大小
            recommended_pool_size = max(base_pool_size // 2, 5)
            recommended_overflow = max_overflow // 2
        else:
            # 正常负载保持默认配置
            recommended_pool_size = base_pool_size
            recommended_overflow = max_overflow
        
        return {
            "pool_size": recommended_pool_size,
            "max_overflow": recommended_overflow,
            "current_load": current_load
        }

    def record_connection_event(self, event_type: str):
        """记录连接事件"""
        if event_type in self.pool_stats:
            self.pool_stats[event_type] += 1

    def get_pool_health(self) -> Dict[str, Any]:
        """获取连接池健康状态"""
        total_events = sum(self.pool_stats.values())
        if total_events == 0:
            return {"status": "unknown", "stats": self.pool_stats}
        
        error_rate = (
            self.pool_stats["connection_errors"] + 
            self.pool_stats["connection_timeouts"]
        ) / total_events * 100
        
        if error_rate > 10:
            status = "unhealthy"
        elif error_rate > 5:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "error_rate": error_rate,
            "stats": self.pool_stats
        }


# 全局性能监控器实例
performance_monitor_instance = PerformanceMonitor()


async def get_performance_report() -> Dict[str, Any]:
    """获取性能报告"""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "query_stats": performance_monitor_instance.get_all_stats(),
        "system_info": {
            "slow_query_threshold": performance_monitor_instance.slow_query_threshold,
            "total_queries": sum(
                stats["count"] for stats in performance_monitor_instance.get_all_stats().values()
            )
        }
    } 