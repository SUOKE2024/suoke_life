"""
高级缓存管理模块
提供多层缓存、智能失效、性能优化等功能
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

import redis.asyncio as redis
import structlog
from aiocache import Cache, cached
from aiocache.serializers import JsonSerializer, PickleSerializer

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CacheLevel(Enum):
    """缓存级别"""

    MEMORY = "memory"  # 内存缓存
    REDIS = "redis"  # Redis缓存
    DISTRIBUTED = "distributed"  # 分布式缓存


class CacheStrategy(Enum):
    """缓存策略"""

    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 基于时间
    ADAPTIVE = "adaptive"  # 自适应策略


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheStats:
    """缓存统计"""

    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    total_size_bytes: int = 0
    entry_count: int = 0

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0


class CacheBackend(ABC):
    """缓存后端抽象基类"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        pass


class MemoryCacheBackend(CacheBackend):
    """内存缓存后端"""

    def __init__(
        self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU
    ):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]

                # 检查TTL
                if (
                    entry.ttl
                    and (datetime.now() - entry.created_at).seconds > entry.ttl
                ):
                    await self._remove_entry(key)
                    self.stats.miss_count += 1
                    return None

                # 更新访问信息
                entry.last_accessed = datetime.now()
                entry.access_count += 1

                self.stats.hit_count += 1
                return entry.value
            else:
                self.stats.miss_count += 1
                return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        async with self._lock:
            # 检查是否需要清理空间
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_entries(1)

            # 计算值大小
            size_bytes = len(pickle.dumps(value))

            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                ttl=ttl,
                size_bytes=size_bytes,
            )

            # 更新统计
            if key in self.cache:
                self.stats.total_size_bytes -= self.cache[key].size_bytes
            else:
                self.stats.entry_count += 1

            self.cache[key] = entry
            self.stats.total_size_bytes += size_bytes

            return True

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self._lock:
            if key in self.cache:
                await self._remove_entry(key)
                return True
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self.cache

    async def clear(self) -> bool:
        """清空缓存"""
        async with self._lock:
            self.cache.clear()
            self.stats = CacheStats()
            return True

    async def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self.stats

    async def _remove_entry(self, key: str):
        """移除缓存条目"""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.stats.total_size_bytes -= entry.size_bytes
            self.stats.entry_count -= 1

    async def _evict_entries(self, count: int):
        """清理缓存条目"""
        if not self.cache:
            return

        # 根据策略选择要清理的条目
        if self.strategy == CacheStrategy.LRU:
            # 最近最少使用
            sorted_entries = sorted(
                self.cache.items(), key=lambda x: x[1].last_accessed
            )
        elif self.strategy == CacheStrategy.LFU:
            # 最少使用频率
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1].access_count)
        else:
            # 默认按创建时间
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1].created_at)

        # 移除指定数量的条目
        for i in range(min(count, len(sorted_entries))):
            key = sorted_entries[i][0]
            await self._remove_entry(key)
            self.stats.eviction_count += 1


class RedisCacheBackend(CacheBackend):
    """Redis缓存后端"""

    def __init__(self, redis_url: str, prefix: str = "medical_resource"):
        self.redis_url = redis_url
        self.prefix = prefix
        self.redis_client: Optional[redis.Redis] = None
        self.stats = CacheStats()

    async def initialize(self):
        """初始化Redis连接"""
        self.redis_client = redis.from_url(self.redis_url)
        await self.redis_client.ping()
        logger.info("Redis缓存后端初始化完成")

    async def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()

    def _make_key(self, key: str) -> str:
        """生成Redis键"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.redis_client:
            return None

        try:
            redis_key = self._make_key(key)
            data = await self.redis_client.get(redis_key)

            if data:
                self.stats.hit_count += 1
                return pickle.loads(data)
            else:
                self.stats.miss_count += 1
                return None

        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            self.stats.miss_count += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.redis_client:
            return False

        try:
            redis_key = self._make_key(key)
            data = pickle.dumps(value)

            if ttl:
                await self.redis_client.setex(redis_key, ttl, data)
            else:
                await self.redis_client.set(redis_key, data)

            return True

        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self.redis_client:
            return False

        try:
            redis_key = self._make_key(key)
            result = await self.redis_client.delete(redis_key)
            return result > 0

        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.redis_client:
            return False

        try:
            redis_key = self._make_key(key)
            return await self.redis_client.exists(redis_key) > 0

        except Exception as e:
            logger.error(f"Redis检查失败: {e}")
            return False

    async def clear(self) -> bool:
        """清空缓存"""
        if not self.redis_client:
            return False

        try:
            pattern = f"{self.prefix}:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True

        except Exception as e:
            logger.error(f"Redis清空失败: {e}")
            return False

    async def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self.stats


class MultiLevelCache:
    """多层缓存"""

    def __init__(self, backends: List[CacheBackend]):
        self.backends = backends
        self.stats = CacheStats()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值（从最快的层开始）"""
        for i, backend in enumerate(self.backends):
            value = await backend.get(key)
            if value is not None:
                # 将值写入更快的层
                for j in range(i):
                    await self.backends[j].set(key, value)

                self.stats.hit_count += 1
                return value

        self.stats.miss_count += 1
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值（写入所有层）"""
        results = []
        for backend in self.backends:
            result = await backend.set(key, value, ttl)
            results.append(result)

        return any(results)

    async def delete(self, key: str) -> bool:
        """删除缓存值（从所有层删除）"""
        results = []
        for backend in self.backends:
            result = await backend.delete(key)
            results.append(result)

        return any(results)

    async def clear(self) -> bool:
        """清空所有层缓存"""
        results = []
        for backend in self.backends:
            result = await backend.clear()
            results.append(result)

        return all(results)


class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_backends: Dict[str, CacheBackend] = {}
        self.multi_level_cache: Optional[MultiLevelCache] = None

        # 缓存策略
        self.default_ttl = config.get("default_ttl", 3600)
        self.enable_compression = config.get("enable_compression", True)
        self.enable_encryption = config.get("enable_encryption", False)

        # 性能监控
        self.performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
        }

        # 缓存预热配置
        self.warmup_config = config.get("warmup", {})

        logger.info("智能缓存管理器初始化完成")

    async def initialize(self):
        """初始化缓存管理器"""
        # 初始化内存缓存
        memory_config = self.config.get("memory", {})
        if memory_config.get("enabled", True):
            memory_backend = MemoryCacheBackend(
                max_size=memory_config.get("max_size", 1000),
                strategy=CacheStrategy(memory_config.get("strategy", "lru")),
            )
            self.cache_backends["memory"] = memory_backend

        # 初始化Redis缓存
        redis_config = self.config.get("redis", {})
        if redis_config.get("enabled", True):
            redis_backend = RedisCacheBackend(
                redis_url=redis_config.get("url", "redis://localhost:6379"),
                prefix=redis_config.get("prefix", "medical_resource"),
            )
            await redis_backend.initialize()
            self.cache_backends["redis"] = redis_backend

        # 设置多层缓存
        if len(self.cache_backends) > 1:
            backends = [
                self.cache_backends.get("memory"),
                self.cache_backends.get("redis"),
            ]
            backends = [b for b in backends if b is not None]
            self.multi_level_cache = MultiLevelCache(backends)

        # 缓存预热
        if self.warmup_config.get("enabled", False):
            await self._warmup_cache()

        logger.info("缓存管理器初始化完成")

    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        start_time = time.time()

        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(key)

            # 从多层缓存获取
            if self.multi_level_cache:
                value = await self.multi_level_cache.get(cache_key)
            else:
                # 从单一后端获取
                backend = next(iter(self.cache_backends.values()))
                value = await backend.get(cache_key)

            # 更新统计
            self.performance_stats["total_requests"] += 1
            if value is not None:
                self.performance_stats["cache_hits"] += 1
            else:
                self.performance_stats["cache_misses"] += 1
                value = default

            return value

        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            return default
        finally:
            # 更新响应时间
            response_time = time.time() - start_time
            self._update_response_time(response_time)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(key)

            # 处理TTL
            if ttl is None:
                ttl = self.default_ttl

            # 数据预处理
            processed_value = await self._preprocess_value(value)

            # 设置到多层缓存
            if self.multi_level_cache:
                return await self.multi_level_cache.set(cache_key, processed_value, ttl)
            else:
                # 设置到单一后端
                backend = next(iter(self.cache_backends.values()))
                return await backend.set(cache_key, processed_value, ttl)

        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            cache_key = self._generate_cache_key(key)

            if self.multi_level_cache:
                return await self.multi_level_cache.delete(cache_key)
            else:
                backend = next(iter(self.cache_backends.values()))
                return await backend.delete(cache_key)

        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False

    async def clear_by_pattern(self, pattern: str) -> bool:
        """按模式清除缓存"""
        try:
            # 这里需要根据具体后端实现
            # 目前简化为清空所有缓存
            if self.multi_level_cache:
                return await self.multi_level_cache.clear()
            else:
                backend = next(iter(self.cache_backends.values()))
                return await backend.clear()

        except Exception as e:
            logger.error(f"模式清除失败: {e}")
            return False

    def _generate_cache_key(self, key: str) -> str:
        """生成缓存键"""
        # 添加版本和命名空间
        namespace = self.config.get("namespace", "medical_resource")
        version = self.config.get("version", "v1")

        # 生成哈希键以避免键过长
        if len(key) > 100:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{namespace}:{version}:{key_hash}"
        else:
            return f"{namespace}:{version}:{key}"

    async def _preprocess_value(self, value: Any) -> Any:
        """预处理缓存值"""
        # 这里可以添加压缩、加密等处理
        if self.enable_compression:
            # 简化实现，实际可以使用gzip等
            pass

        if self.enable_encryption:
            # 简化实现，实际可以使用AES等
            pass

        return value

    def _update_response_time(self, response_time: float):
        """更新平均响应时间"""
        current_avg = self.performance_stats["average_response_time"]
        total_requests = self.performance_stats["total_requests"]

        if total_requests == 1:
            self.performance_stats["average_response_time"] = response_time
        else:
            # 计算移动平均
            self.performance_stats["average_response_time"] = (
                current_avg * (total_requests - 1) + response_time
            ) / total_requests

    async def _warmup_cache(self):
        """缓存预热"""
        warmup_data = self.warmup_config.get("data", [])

        for item in warmup_data:
            key = item.get("key")
            value = item.get("value")
            ttl = item.get("ttl")

            if key and value:
                await self.set(key, value, ttl)

        logger.info(f"缓存预热完成，预热了 {len(warmup_data)} 个条目")

    async def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        hit_rate = 0.0
        if self.performance_stats["total_requests"] > 0:
            hit_rate = (
                self.performance_stats["cache_hits"]
                / self.performance_stats["total_requests"]
            )

        return {
            **self.performance_stats,
            "hit_rate": hit_rate,
            "backends": list(self.cache_backends.keys()),
            "multi_level_enabled": self.multi_level_cache is not None,
        }

    async def close(self):
        """关闭缓存管理器"""
        for backend in self.cache_backends.values():
            if hasattr(backend, "close"):
                await backend.close()

        logger.info("缓存管理器已关闭")


# 缓存装饰器
def cache_result(
    key_func: Optional[Callable] = None,
    ttl: int = 3600,
    cache_manager: Optional[SmartCacheManager] = None,
):
    """缓存结果装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成策略
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in kwargs.items())
                cache_key = ":".join(key_parts)

            # 尝试从缓存获取
            if cache_manager:
                cached_result = await cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # 执行函数
            result = await func(*args, **kwargs)

            # 缓存结果
            if cache_manager and result is not None:
                await cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
