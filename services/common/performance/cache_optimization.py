"""
cache_optimization - 索克生活项目模块
"""

from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from prometheus_client import Counter, Gauge, Histogram
from typing import Any
import aioredis
import asyncio
import contextlib
import hashlib
import json
import logging
import time

#!/usr/bin/env python3
"""
缓存优化模块
提供多级缓存、缓存预热、缓存策略等功能
"""



logger = logging.getLogger(__name__)

# Prometheus 指标
cache_hits = Counter(
    "cache_hits_total", "Total cache hits", ["cache_level", "cache_name"]
)
cache_misses = Counter("cache_misses_total", "Total cache misses", ["cache_name"])
cache_operations = Histogram(
    "cache_operation_duration_seconds",
    "Cache operation duration",
    ["operation", "cache_name"],
)
cache_size = Gauge(
    "cache_size_items", "Number of items in cache", ["cache_level", "cache_name"]
)


class CacheStrategy(Enum):
    """缓存策略"""

    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最不经常使用
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 基于过期时间


@dataclass
class CacheStats:
    """缓存统计"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def l1_hit(self):
        self.hits += 1
        cache_hits.labels(cache_level="l1", cache_name="multi_level").inc()

    def l2_hit(self):
        self.hits += 1
        cache_hits.labels(cache_level="l2", cache_name="multi_level").inc()

    def miss(self):
        self.misses += 1
        cache_misses.labels(cache_name="multi_level").inc()


class LRUCache:
    """LRU 缓存实现"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key in self.cache:
            # 移到末尾（最近使用）
            self.cache.move_to_end(key)
            self.stats["hits"] += 1
            return self.cache[key]["value"]

        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: Any, ttl: int | None = None):
        """设置缓存值"""
        current_time = time.time()

        # 检查是否需要驱逐
        if key not in self.cache and len(self.cache) >= self.capacity:
            # 驱逐最旧的项
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1

        self.cache[key] = {
            "value": value,
            "expire_at": current_time + ttl if ttl else None,
            "created_at": current_time,
        }

        # 移到末尾
        self.cache.move_to_end(key)

    def delete(self, key: str) -> bool:
        """删除缓存项"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self):
        """清空缓存"""
        self.cache.clear()

    def _evict_expired(self):
        """驱逐过期项"""
        current_time = time.time()
        expired_keys = []

        for key, item in self.cache.items():
            if item["expire_at"] and item["expire_at"] < current_time:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]
            self.stats["evictions"] += 1


class MultiLevelCache:
    """多级缓存系统"""

    def __init__(
        self,
        cache_name: str = "default",
        l1_size: int = 1000,
        l2_ttl: int = 300,
        l2_client: aioredis.Redis | None = None,
    ):
        self.cache_name = cache_name
        # L1: 内存缓存（LRU）
        self.l1_cache = LRUCache(l1_size)
        # L2: Redis 缓存
        self.l2_cache = l2_client
        self.l2_ttl = l2_ttl

        # 缓存预热
        self.warmer = CacheWarmer()

        # 缓存统计
        self.stats = CacheStats()

        # 定期清理过期项
        self._cleanup_task = None

        logger.info(f"多级缓存系统初始化: {cache_name}")

    async def start(self):
        """启动缓存系统"""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """停止缓存系统"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._cleanup_task

    async def _cleanup_loop(self):
        """定期清理过期项"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                self.l1_cache._evict_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存清理错误: {e}")

    @cache_operations.labels(operation="get", cache_name="multi_level").time()
    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        # L1 查找
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats.l1_hit()
            return value

        # L2 查找
        if self.l2_cache:
            try:
                value = await self.l2_cache.get(key)
                if value is not None:
                    self.stats.l2_hit()
                    # 提升到 L1
                    deserialized_value = json.loads(value)
                    self.l1_cache.set(key, deserialized_value)
                    return deserialized_value
            except Exception as e:
                logger.error(f"L2缓存读取错误: {e}")

        self.stats.miss()
        return None

    @cache_operations.labels(operation="set", cache_name="multi_level").time()
    async def set(self, key: str, value: Any, ttl: int | None = None):
        """设置缓存值"""
        # 设置 L1
        self.l1_cache.set(key, value, ttl)

        # 设置 L2
        if self.l2_cache:
            try:
                ttl = ttl or self.l2_ttl
                await self.l2_cache.setex(key, ttl, json.dumps(value))
            except Exception as e:
                logger.error(f"L2缓存写入错误: {e}")

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        # 删除 L1
        l1_deleted = self.l1_cache.delete(key)

        # 删除 L2
        l2_deleted = False
        if self.l2_cache:
            try:
                l2_deleted = await self.l2_cache.delete(key) > 0
            except Exception as e:
                logger.error(f"L2缓存删除错误: {e}")

        return l1_deleted or l2_deleted

    async def clear(self):
        """清空所有缓存"""
        # 清空 L1
        self.l1_cache.clear()

        # 清空 L2（需要谨慎使用）
        if self.l2_cache:
            logger.warning("清空L2缓存需要手动执行，以防止误操作")

    def cache_aside(self, ttl: int = 300, key_prefix: str = ""):
        """Cache-Aside 模式装饰器"""

        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(func.__name__, args, kwargs, key_prefix)

                # 尝试从缓存获取
                cached = await self.get(cache_key)
                if cached is not None:
                    return cached

                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # 写入缓存
                await self.set(cache_key, result, ttl)

                return result

            return wrapper

        return decorator

    def _generate_key(
        self, func_name: str, args: tuple, kwargs: dict, prefix: str = ""
    ) -> str:
        """生成缓存键"""
        key_data = {"func": func_name, "args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True)
        hash_key = hashlib.md5(key_str.encode()).hexdigest()

        if prefix:
            return f"{prefix}:{hash_key}"
        return hash_key

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return {
            "hit_rate": self.stats.hit_rate,
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "l1_stats": self.l1_cache.stats,
            "l1_size": len(self.l1_cache.cache),
            "l1_capacity": self.l1_cache.capacity,
        }

    async def warm_cache(self, keys_values: dict[str, Any]):
        """预热缓存"""
        for key, value in keys_values.items():
            await self.set(key, value)
        logger.info(f"预热了 {len(keys_values)} 个缓存项")


class CacheWarmer:
    """缓存预热器"""

    def __init__(self):
        self.warmup_tasks: list[Callable] = []
        self.warmup_data: dict[str, Any] = {}

    def register_warmup_task(self, task: Callable):
        """注册预热任务"""
        self.warmup_tasks.append(task)

    def add_warmup_data(self, key: str, value: Any):
        """添加预热数据"""
        self.warmup_data[key] = value

    async def warm_cache(self, cache: MultiLevelCache):
        """执行缓存预热"""
        # 预热静态数据
        if self.warmup_data:
            await cache.warm_cache(self.warmup_data)

        # 执行预热任务
        if self.warmup_tasks:
            tasks = [task() for task in self.warmup_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if not isinstance(r, Exception))
            logger.info(f"执行了 {len(tasks)} 个预热任务，成功 {success_count} 个")


class CacheInvalidator:
    """缓存失效管理器"""

    def __init__(self, cache: MultiLevelCache):
        self.cache = cache
        self.invalidation_patterns: dict[str, list[str]] = {}

    def register_pattern(self, event: str, patterns: list[str]):
        """注册失效模式"""
        if event not in self.invalidation_patterns:
            self.invalidation_patterns[event] = []
        self.invalidation_patterns[event].extend(patterns)

    async def invalidate_by_event(self, event: str):
        """根据事件失效缓存"""
        patterns = self.invalidation_patterns.get(event, [])

        for pattern in patterns:
            # 这里可以实现更复杂的模式匹配
            await self.cache.delete(pattern)

        logger.info(f"事件 {event} 触发了 {len(patterns)} 个缓存失效")

    async def invalidate_by_tags(self, tags: list[str]):
        """根据标签失效缓存"""
        # 这需要缓存系统支持标签功能
        # 可以通过维护标签到键的映射来实现
        pass


# 全局缓存注册表
_cache_registry: dict[str, MultiLevelCache] = {}


async def get_cache(name: str = "default", **kwargs) -> MultiLevelCache:
    """获取或创建缓存实例"""
    if name not in _cache_registry:
        _cache_registry[name] = MultiLevelCache(cache_name=name, **kwargs)
        await _cache_registry[name].start()

    return _cache_registry[name]


# 便捷装饰器
def cached(cache_name: str = "default", ttl: int = 300, key_prefix: str = ""):
    """
    缓存装饰器

    Args:
        cache_name: 缓存名称
        ttl: 过期时间（秒）
        key_prefix: 键前缀
    """

    async def decorator(func: Callable):
        cache = await get_cache(cache_name)
        return cache.cache_aside(ttl, key_prefix)(func)

    return decorator
