"""
optimizer - 索克生活项目模块
"""

from .logging import get_logger
from collections import deque
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import wraps
from typing import Any
import asyncio
import gc
import psutil
import time
import weakref

#!/usr/bin/env python

"""
性能优化器
"""





class BatchProcessor:
    """批处理器"""

    def __init__(self, batch_size: int = 10, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.pending_items = []
        self.pending_futures = []
        self.last_batch_time = time.time()
        self.logger = get_logger(__name__)
        self._processing = False

    async def add_item(self, item: Any, processor: Callable) -> Any:
        """添加项目到批处理队列"""
        future = asyncio.Future()

        self.pending_items.append(item)
        self.pending_futures.append((future, processor))

        # 检查是否需要立即处理
        if (
            len(self.pending_items) >= self.batch_size
            or time.time() - self.last_batch_time >= self.max_wait_time
        ):
            await self._process_batch()

        return await future

    async def _process_batch(self):
        """处理当前批次"""
        if self._processing or not self.pending_items:
            return

        self._processing = True

        try:
            items = self.pending_items.copy()
            futures_and_processors = self.pending_futures.copy()

            # 清空队列
            self.pending_items.clear()
            self.pending_futures.clear()
            self.last_batch_time = time.time()

            # 按处理器分组
            processor_groups = {}
            for i, (future, processor) in enumerate(futures_and_processors):
                if processor not in processor_groups:
                    processor_groups[processor] = []
                processor_groups[processor].append((i, items[i], future))

            # 并行处理每个组
            tasks = []
            for processor, group_items in processor_groups.items():
                task = asyncio.create_task(self._process_group(processor, group_items))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as e:
            self.logger.error(f"批处理失败: {e!s}")
            # 设置所有future为异常
            for future, _ in self.pending_futures:
                if not future.done():
                    future.set_exception(e)
        finally:
            self._processing = False

    async def _process_group(self, processor: Callable, group_items: list):
        """处理同一处理器的项目组"""
        try:
            items = [item for _, item, _ in group_items]

            if asyncio.iscoroutinefunction(processor):
                results = await processor(items)
            else:
                results = processor(items)

            # 设置结果
            for i, (_, _, future) in enumerate(group_items):
                if i < len(results):
                    future.set_result(results[i])
                else:
                    future.set_exception(IndexError("结果数量不匹配"))

        except Exception as e:
            # 设置所有future为异常
            for _, _, future in group_items:
                if not future.done():
                    future.set_exception(e)


class ParallelProcessor:
    """并行处理器"""

    def __init__(self, max_workers: int = None, use_processes: bool = False):
        self.max_workers = max_workers or min(32, (psutil.cpu_count() or 1) + 4)
        self.use_processes = use_processes
        self.logger = get_logger(__name__)

        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

    async def process_parallel(
        self, items: list[Any], processor: Callable, chunk_size: int = None
    ) -> list[Any]:
        """并行处理项目列表"""
        if not items:
            return []

        chunk_size = chunk_size or max(1, len(items) // self.max_workers)
        chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

        loop = asyncio.get_event_loop()
        tasks = []

        for chunk in chunks:
            if self.use_processes:
                task = loop.run_in_executor(
                    self.executor, self._process_chunk, processor, chunk
                )
            else:
                task = loop.run_in_executor(
                    self.executor, self._process_chunk_sync, processor, chunk
                )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"并行处理出错: {result!s}")
                raise result
            final_results.extend(result)

        return final_results

    def _process_chunk(self, processor: Callable, chunk: list[Any]) -> list[Any]:
        """处理数据块（用于进程池）"""
        return [processor(item) for item in chunk]

    def _process_chunk_sync(self, processor: Callable, chunk: list[Any]) -> list[Any]:
        """同步处理数据块（用于线程池）"""
        if asyncio.iscoroutinefunction(processor):
            # 对于异步函数，在新的事件循环中运行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self._process_chunk_async(processor, chunk)
                )
            finally:
                loop.close()
        else:
            return [processor(item) for item in chunk]

    async def _process_chunk_async(
        self, processor: Callable, chunk: list[Any]
    ) -> list[Any]:
        """异步处理数据块"""
        tasks = [processor(item) for item in chunk]
        return await asyncio.gather(*tasks)

    def __del__(self):
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)


class MemoryOptimizer:
    """内存优化器"""

    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.logger = get_logger(__name__)
        self.object_pool = {}
        self.weak_refs = weakref.WeakSet()

    def get_memory_usage(self) -> dict[str, float]:
        """获取内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # 物理内存
            "vms_mb": memory_info.vms / 1024 / 1024,  # 虚拟内存
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }

    async def check_memory_pressure(self) -> bool:
        """检查内存压力"""
        memory_usage = self.get_memory_usage()

        if memory_usage["rss_mb"] > self.max_memory_mb:
            self.logger.warning(f"内存使用过高: {memory_usage['rss_mb']:.2f}MB")
            return True

        if memory_usage["percent"] > 80:
            self.logger.warning(f"内存使用率过高: {memory_usage['percent']:.2f}%")
            return True

        return False

    async def optimize_memory(self):
        """优化内存使用"""
        self.logger.info("开始内存优化")

        # 清理对象池
        self._cleanup_object_pool()

        # 强制垃圾回收
        collected = gc.collect()
        self.logger.info(f"垃圾回收清理了 {collected} 个对象")

        # 检查优化后的内存使用
        memory_usage = self.get_memory_usage()
        self.logger.info(f"优化后内存使用: {memory_usage['rss_mb']:.2f}MB")

    def _cleanup_object_pool(self):
        """清理对象池"""
        before_count = len(self.object_pool)

        # 移除未使用的对象
        keys_to_remove = []
        for key, obj_list in self.object_pool.items():
            # 保留最近使用的对象
            self.object_pool[key] = obj_list[-10:]  # 只保留最后10个
            if not self.object_pool[key]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.object_pool[key]

        after_count = sum(len(obj_list) for obj_list in self.object_pool.values())
        self.logger.info(f"对象池清理: {before_count} -> {after_count}")

        @cache(timeout=300)  # 5分钟缓存
def get_object(self, obj_type: str, factory: Callable = None):
        """从对象池获取对象"""
        if obj_type not in self.object_pool:
            self.object_pool[obj_type] = deque(maxlen=50)

        pool = self.object_pool[obj_type]

        if pool:
            return pool.popleft()
        elif factory:
            return factory()
        else:
            return None

    def return_object(self, obj_type: str, obj: Any):
        """将对象返回到对象池"""
        if obj_type not in self.object_pool:
            self.object_pool[obj_type] = deque(maxlen=50)

        # 重置对象状态（如果有reset方法）
        if hasattr(obj, "reset"):
            obj.reset()

        self.object_pool[obj_type].append(obj)


class CacheOptimizer:
    """缓存优化器"""

    def __init__(self, max_cache_size: int = 1000):
        self.max_cache_size = max_cache_size
        self.cache_stats = {"hits": 0, "misses": 0, "evictions": 0}
        self.logger = get_logger(__name__)

    def get_cache_efficiency(self) -> dict[str, float]:
        """获取缓存效率"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]

        if total_requests == 0:
            return {"hit_rate": 0.0, "miss_rate": 0.0}

        hit_rate = self.cache_stats["hits"] / total_requests
        miss_rate = self.cache_stats["misses"] / total_requests

        return {
            "hit_rate": hit_rate,
            "miss_rate": miss_rate,
            "total_requests": total_requests,
            "evictions": self.cache_stats["evictions"],
        }

    async def optimize_cache_strategy(self, cache_manager) -> dict[str, Any]:
        """优化缓存策略"""
        efficiency = self.get_cache_efficiency()

        recommendations = []

        # 分析命中率
        if efficiency["hit_rate"] < 0.5:
            recommendations.append("缓存命中率较低，建议增加缓存大小或调整TTL")

        # 分析驱逐率
        if efficiency["evictions"] > efficiency["total_requests"] * 0.1:
            recommendations.append("缓存驱逐频繁，建议增加缓存容量")

        # 获取缓存统计
        cache_stats = (
            await cache_manager.get_stats()
            if hasattr(cache_manager, "get_stats")
            else {}
        )

        return {
            "efficiency": efficiency,
            "cache_stats": cache_stats,
            "recommendations": recommendations,
        }


class QueryOptimizer:
    """查询优化器"""

    def __init__(self):
        self.query_stats = {}
        self.slow_queries = deque(maxlen=100)
        self.lo    @cache(timeout=300)  # 5分钟缓存
gger = get_logger(__name__)

    def record_query(self, query_id: str, duration: float, result_count: int = 0):
        """记录查询统计"""
        if query_id not in self.query_stats:
            self.query_stats[query_id] = {
                "count": 0,
                "total_duration": 0,
                "max_duration": 0,
                "min_duration": float("inf"),
                "total_results": 0,
            }

        stats = self.query_stats[query_id]
        stats["count"] += 1
        stats["total_duration"] += duration
        stats["max_duration"] = max(stats["max_duration"], duration)
        stats["min_duration"] = min(stats["min_duration"], duration)
        stats["total_results"] += result_count

        # 记录慢查询
        if duration > 1.0:  # 超过1秒的查询
            self.slow_queries.append(
                {
                    "query_id": query_id,
                    "duration": duration,
                    "result_count": result_count,
                    "timestamp": time.time(),
                }
            )

    def get_query_analysis(self) -> dict[str, Any]:
        """获取查询分析"""
        if not self.query_stats:
            return {"total_queries": 0}

        total_queries = sum(stats["count"] for stats in self.query_stats.values())
        total_duration = sum(
            stats["total_duration"] for stats in self.query_stats.values()
        )

        # 找出最慢的查询
        slowest_queries = sorted(
            [(qid, stats["max_duration"]) for qid, stats in self.query_stats.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        # 找出最频繁的查询
        frequent_queries = sorted(
            [(qid, stats["count"]) for qid, stats in self.query_stats.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        return {
            "total_queries": total_queries,
            "average_duration": total_duration / total_queries
            if total_queries > 0
            else 0,
            "slowest_queries": slowest_queries,
            "frequent_queries": frequent_queries,
            "slow_query_count": len(self.slow_queries),
        }


# 装饰器函数
def batch_process(batch_size: int = 10, max_wait_time: float = 1.0):
    """批处理装饰器"""
    processor = BatchProcessor(batch_size, max_wait_time)

    def decorator(func):
        @wraps(func)
        async def wrapper(item):
            return await processor.add_item(item, func)

        return wrapper

    return decorator


def parallel_process(max_workers: int = None, use_processes: bool = False):
    """并行处理装饰器"""
    processor = ParallelProcessor(max_workers, use_processes)

    def decorator(func):
        @wraps(func)
        async def wrapper(items: list[Any], chunk_size: int = None):
            return await processor.process_parallel(items, func, chunk_size)

        return wrapper

    return decorator


def memory_optimized(max_memory_mb: int = 1024):
    """内存优化装饰器"""
    optimizer = MemoryOptimizer(max_memory_mb)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 检查内存压力
            if await optimizer.check_memory_pressure():
                await optimizer.optimize_memory()

            return await func    @cache(timeout=300)  # 5分钟缓存
(*args, **kwargs)

        return wrapper

    return decorator


def query_optimized(query_id: str = None):
    """查询优化装饰器"""
    optimizer = QueryOptimizer()

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            qid = query_id or f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # 记录查询统计
                result_count = len(result) if isinstance(result, (list, tuple)) else 1
                optimizer.record_query(qid, duration, result_count)

                return result
            except Exception:
                duration = time.time() - start_time
                optimizer.record_query(qid, duration, 0)
                raise

        return wrapper

    return decorator
