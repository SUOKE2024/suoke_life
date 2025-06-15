"""
性能优化服务
提供查询优化、缓存策略、批处理等功能
"""
import asyncio
import time
from typing import List, Dict, Any, Optional, Callable, Union
from functools import wraps
from collections import defaultdict
import hashlib
import json

from app.core.logger import get_logger
from app.core.exceptions import ServiceUnavailableException, ValidationException
from app.services.cache_service import CacheService

logger = get_logger()


class PerformanceService:
    """性能优化服务"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.query_stats = defaultdict(list)
        self.batch_processors = {}
        
    async def optimize_query(self, query: str, params: Dict[str, Any] = None) -> str:
        """
        优化查询语句
        
        Args:
            query: 原始查询语句
            params: 查询参数
            
        Returns:
            优化后的查询语句
        """
        try:
            # 记录查询统计
            await self._record_query_stats(query, params)
            
            # 应用查询优化规则
            optimized_query = await self._apply_optimization_rules(query)
            
            logger.debug(f"查询优化完成: {len(query)} -> {len(optimized_query)} 字符")
            return optimized_query
            
        except Exception as e:
            logger.error(f"查询优化失败: {e}")
            return query  # 返回原始查询
    
    async def batch_process(
        self, 
        items: List[Any], 
        processor: Callable,
        batch_size: int = 100,
        max_concurrency: int = 5
    ) -> List[Any]:
        """
        批处理数据
        
        Args:
            items: 待处理的数据列表
            processor: 处理函数
            batch_size: 批处理大小
            max_concurrency: 最大并发数
            
        Returns:
            处理结果列表
        """
        try:
            if not items:
                return []
            
            # 分批处理
            batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
            
            # 创建信号量控制并发
            semaphore = asyncio.Semaphore(max_concurrency)
            
            async def process_batch(batch):
                async with semaphore:
                    return await processor(batch)
            
            # 并发处理所有批次
            tasks = [process_batch(batch) for batch in batches]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            results = []
            for batch_result in batch_results:
                if isinstance(batch_result, Exception):
                    logger.error(f"批处理失败: {batch_result}")
                    continue
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                else:
                    results.append(batch_result)
            
            logger.info(f"批处理完成: {len(items)} 项 -> {len(results)} 结果")
            return results
            
        except Exception as e:
            logger.error(f"批处理失败: {e}")
            raise ServiceUnavailableException("批处理服务", {"error": str(e)})
    
    async def smart_cache(
        self,
        key: str,
        fetch_func: Callable,
        ttl: int = 3600,
        cache_strategy: str = "lru"
    ) -> Any:
        """
        智能缓存
        
        Args:
            key: 缓存键
            fetch_func: 数据获取函数
            ttl: 缓存时间（秒）
            cache_strategy: 缓存策略
            
        Returns:
            缓存或获取的数据
        """
        try:
            # 尝试从缓存获取
            cached_data = await self.cache_service.get(key)
            if cached_data is not None:
                logger.debug(f"缓存命中: {key}")
                return cached_data
            
            # 缓存未命中，获取数据
            logger.debug(f"缓存未命中，获取数据: {key}")
            start_time = time.time()
            data = await fetch_func()
            fetch_time = time.time() - start_time
            
            # 根据获取时间调整TTL
            adjusted_ttl = await self._adjust_ttl(ttl, fetch_time)
            
            # 存储到缓存
            await self.cache_service.set(key, data, ttl=adjusted_ttl)
            
            logger.debug(f"数据已缓存: {key}, TTL: {adjusted_ttl}s, 获取时间: {fetch_time:.3f}s")
            return data
            
        except Exception as e:
            logger.error(f"智能缓存失败: {e}")
            # 如果缓存失败，直接返回数据
            return await fetch_func()
    
    async def preload_cache(self, preload_config: Dict[str, Any]) -> None:
        """
        预加载缓存
        
        Args:
            preload_config: 预加载配置
        """
        try:
            logger.info("开始预加载缓存")
            
            for cache_key, config in preload_config.items():
                try:
                    fetch_func = config.get("fetch_func")
                    ttl = config.get("ttl", 3600)
                    
                    if not fetch_func:
                        continue
                    
                    # 检查是否已缓存
                    if await self.cache_service.exists(cache_key):
                        logger.debug(f"缓存已存在，跳过: {cache_key}")
                        continue
                    
                    # 获取并缓存数据
                    data = await fetch_func()
                    await self.cache_service.set(cache_key, data, ttl=ttl)
                    
                    logger.debug(f"预加载完成: {cache_key}")
                    
                except Exception as e:
                    logger.error(f"预加载失败 {cache_key}: {e}")
                    continue
            
            logger.info("缓存预加载完成")
            
        except Exception as e:
            logger.error(f"预加载缓存失败: {e}")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标
        
        Returns:
            性能指标数据
        """
        try:
            # 缓存统计
            cache_stats = await self.cache_service.get_stats()
            
            # 查询统计
            query_stats = await self._get_query_statistics()
            
            # 系统资源统计
            system_stats = await self._get_system_statistics()
            
            return {
                "cache": cache_stats,
                "queries": query_stats,
                "system": system_stats,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {}
    
    async def optimize_database_queries(self, queries: List[str]) -> List[str]:
        """
        优化数据库查询
        
        Args:
            queries: 查询列表
            
        Returns:
            优化后的查询列表
        """
        try:
            optimized_queries = []
            
            for query in queries:
                # 应用优化规则
                optimized = await self._optimize_single_query(query)
                optimized_queries.append(optimized)
            
            return optimized_queries
            
        except Exception as e:
            logger.error(f"数据库查询优化失败: {e}")
            return queries
    
    async def _record_query_stats(self, query: str, params: Dict[str, Any] = None) -> None:
        """记录查询统计"""
        try:
            query_hash = hashlib.md5(query.encode()).hexdigest()
            stats = {
                "query_hash": query_hash,
                "query_length": len(query),
                "params_count": len(params) if params else 0,
                "timestamp": time.time()
            }
            
            self.query_stats[query_hash].append(stats)
            
            # 保持最近1000条记录
            if len(self.query_stats[query_hash]) > 1000:
                self.query_stats[query_hash] = self.query_stats[query_hash][-1000:]
                
        except Exception as e:
            logger.error(f"记录查询统计失败: {e}")
    
    async def _apply_optimization_rules(self, query: str) -> str:
        """应用查询优化规则"""
        try:
            optimized = query
            
            # 规则1: 移除多余的空格
            optimized = " ".join(optimized.split())
            
            # 规则2: 优化LIMIT子句
            if "LIMIT" in optimized.upper():
                optimized = await self._optimize_limit_clause(optimized)
            
            # 规则3: 优化WHERE子句
            if "WHERE" in optimized.upper():
                optimized = await self._optimize_where_clause(optimized)
            
            # 规则4: 添加索引提示
            optimized = await self._add_index_hints(optimized)
            
            return optimized
            
        except Exception as e:
            logger.error(f"应用优化规则失败: {e}")
            return query
    
    async def _optimize_limit_clause(self, query: str) -> str:
        """优化LIMIT子句"""
        # 这里可以实现具体的LIMIT优化逻辑
        return query
    
    async def _optimize_where_clause(self, query: str) -> str:
        """优化WHERE子句"""
        # 这里可以实现具体的WHERE优化逻辑
        return query
    
    async def _add_index_hints(self, query: str) -> str:
        """添加索引提示"""
        # 这里可以实现具体的索引提示逻辑
        return query
    
    async def _optimize_single_query(self, query: str) -> str:
        """优化单个查询"""
        return await self._apply_optimization_rules(query)
    
    async def _adjust_ttl(self, base_ttl: int, fetch_time: float) -> int:
        """根据获取时间调整TTL"""
        try:
            # 如果获取时间很长，增加TTL
            if fetch_time > 1.0:  # 超过1秒
                return int(base_ttl * 1.5)
            elif fetch_time > 0.5:  # 超过0.5秒
                return int(base_ttl * 1.2)
            else:
                return base_ttl
                
        except Exception:
            return base_ttl
    
    async def _get_query_statistics(self) -> Dict[str, Any]:
        """获取查询统计"""
        try:
            total_queries = sum(len(stats) for stats in self.query_stats.values())
            unique_queries = len(self.query_stats)
            
            # 计算平均查询长度
            all_lengths = []
            for stats_list in self.query_stats.values():
                all_lengths.extend([s["query_length"] for s in stats_list])
            
            avg_length = sum(all_lengths) / len(all_lengths) if all_lengths else 0
            
            return {
                "total_queries": total_queries,
                "unique_queries": unique_queries,
                "average_query_length": avg_length
            }
            
        except Exception as e:
            logger.error(f"获取查询统计失败: {e}")
            return {}
    
    async def _get_system_statistics(self) -> Dict[str, Any]:
        """获取系统统计"""
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free": disk.free
            }
            
        except ImportError:
            logger.warning("psutil未安装，无法获取系统统计")
            return {}
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {}


def performance_monitor(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.debug(f"性能监控 - {function_name}: {execution_time:.3f}s")
                
                # 如果执行时间过长，记录警告
                if execution_time > 5.0:
                    logger.warning(f"慢查询检测 - {function_name}: {execution_time:.3f}s")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"性能监控 - {function_name} 失败: {e}, 耗时: {execution_time:.3f}s")
                raise
                
        return wrapper
    return decorator


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.optimization_rules = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """加载默认优化规则"""
        self.optimization_rules = [
            self._remove_redundant_spaces,
            self._optimize_joins,
            self._optimize_subqueries,
            self._add_query_hints
        ]
    
    async def optimize(self, query: str) -> str:
        """优化查询"""
        optimized = query
        
        for rule in self.optimization_rules:
            try:
                optimized = await rule(optimized)
            except Exception as e:
                logger.error(f"优化规则失败: {e}")
                continue
        
        return optimized
    
    async def _remove_redundant_spaces(self, query: str) -> str:
        """移除多余空格"""
        return " ".join(query.split())
    
    async def _optimize_joins(self, query: str) -> str:
        """优化JOIN操作"""
        # 这里可以实现JOIN优化逻辑
        return query
    
    async def _optimize_subqueries(self, query: str) -> str:
        """优化子查询"""
        # 这里可以实现子查询优化逻辑
        return query
    
    async def _add_query_hints(self, query: str) -> str:
        """添加查询提示"""
        # 这里可以实现查询提示逻辑
        return query 