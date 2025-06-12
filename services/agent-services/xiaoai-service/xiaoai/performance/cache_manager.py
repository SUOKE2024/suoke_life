"""
高性能缓存管理器

提供多级缓存、智能预热、缓存策略等功能
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import json
import logging
import pickle
import time
from typing import Any, Callable, Dict, Optional, Union

import redis.asyncio as redis

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """缓存策略"""

    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    TTL = "ttl"  # 时间过期
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BACK = "write_back"  # 写回


@dataclass
class CacheConfig:
    """缓存配置"""

    strategy: CacheStrategy = CacheStrategy.LRU
    ttl: int = 3600  # 默认1小时
    max_size: int = 1000
    serialize_method: str = "json"  # json, pickle
    compress: bool = False


class AdvancedCacheManager:
    """高级缓存管理器"""

    def __init__(self):
        self.settings = get_settings()
        self.local_cache: Dict[str, Any] = {}
        self.cache_stats: Dict[str, int] = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0}
        self.redis_client: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()

    async def initialize(self):
        """初始化缓存管理器"""
        try:
            # 初始化Redis连接
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=False,
                max_connections=self.settings.redis_max_connections,
            )

            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis缓存连接成功")

        except Exception as e:
            logger.warning(f"Redis连接失败，使用本地缓存: {e}")
            self.redis_client = None

    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            # 先尝试本地缓存
            if key in self.local_cache:
                self.cache_stats["hits"] += 1
                return self.local_cache[key]

            # 尝试Redis缓存
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    deserialized_value = self._deserialize(value)
                    # 回写到本地缓存
                    self.local_cache[key] = deserialized_value
                    self.cache_stats["hits"] += 1
                    return deserialized_value

            self.cache_stats["misses"] += 1
            return default

        except Exception as e:
            logger.error(f"缓存获取失败: {key}, 错误: {e}")
            self.cache_stats["misses"] += 1
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.LRU,
    ):
        """设置缓存值"""
        try:
            async with self._lock:
                # 设置本地缓存
                self.local_cache[key] = value

                # 本地缓存大小控制
                if len(self.local_cache) > 1000:  # 本地缓存最大1000条
                    self._evict_local_cache(strategy)

                # 设置Redis缓存
                if self.redis_client:
                    serialized_value = self._serialize(value)
                    if ttl:
                        await self.redis_client.setex(key, ttl, serialized_value)
                    else:
                        await self.redis_client.set(key, serialized_value)

                self.cache_stats["sets"] += 1

        except Exception as e:
            logger.error(f"缓存设置失败: {key}, 错误: {e}")

    async def delete(self, key: str):
        """删除缓存"""
        try:
            # 删除本地缓存
            self.local_cache.pop(key, None)

            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(key)

            self.cache_stats["deletes"] += 1

        except Exception as e:
            logger.error(f"缓存删除失败: {key}, 错误: {e}")

    async def clear(self):
        """清空所有缓存"""
        try:
            self.local_cache.clear()

            if self.redis_client:
                await self.redis_client.flushdb()

            logger.info("缓存清空完成")

        except Exception as e:
            logger.error(f"缓存清空失败: {e}")

    def _evict_local_cache(self, strategy: CacheStrategy):
        """本地缓存淘汰"""
        if strategy == CacheStrategy.LRU:
            # 简单LRU实现：删除最早的25%
            items_to_remove = len(self.local_cache) // 4
            keys_to_remove = list(self.local_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.local_cache[key]

    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return json.dumps(value).encode()
            else:
                return pickle.dumps(value)
        except Exception:
            return pickle.dumps(value)

    def _deserialize(self, value: bytes) -> Any:
        """反序列化值"""
        try:
            # 先尝试JSON
            return json.loads(value.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 回退到pickle
            return pickle.loads(value)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "local_cache_size": len(self.local_cache),
            **self.cache_stats,
        }


def cache(ttl: int = 3600, key_prefix: str = "", strategy: CacheStrategy = CacheStrategy.LRU):
    """缓存装饰器"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = (
                f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            )

            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = await func(*args, **kwargs)

            # 存储到缓存
            await cache_manager.set(cache_key, result, ttl, strategy)

            return result

        return wrapper

    return decorator


class SmartCacheWarmer:
    """智能缓存预热器"""

    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.warmup_tasks = []

    async def add_warmup_task(self, key: str, value_func: Callable, ttl: int = 3600):
        """添加预热任务"""
        self.warmup_tasks.append({"key": key, "value_func": value_func, "ttl": ttl})

    async def warmup(self):
        """执行缓存预热"""
        logger.info(f"开始缓存预热，任务数: {len(self.warmup_tasks)}")

        for task in self.warmup_tasks:
            try:
                value = await task["value_func"]()
                await self.cache_manager.set(task["key"], value, task["ttl"])
                logger.debug(f"预热缓存成功: {task['key']}")
            except Exception as e:
                logger.error(f"预热缓存失败: {task['key']}, 错误: {e}")

        logger.info("缓存预热完成")


# 全局缓存管理器实例
cache_manager = AdvancedCacheManager()
cache_warmer = SmartCacheWarmer(cache_manager)
