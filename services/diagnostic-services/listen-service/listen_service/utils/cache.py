"""
缓存管理模块

提供内存缓存和Redis缓存的统一接口。
"""

import asyncio
import hashlib
import json
import pickle
import time
import weakref
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import redis.asyncio as redis
import structlog

from ..config.settings import get_settings

logger = structlog.get_logger(__name__)


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
    async def clear(self) -> bool:
        """清空缓存"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass


class MemoryCache(CacheBackend):
    """内存缓存实现"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None

            cache_item = self._cache[key]
            
            # 检查是否过期
            if cache_item["expires_at"] and time.time() > cache_item["expires_at"]:
                await self._remove_key(key)
                return None

            # 更新访问时间
            self._access_times[key] = time.time()
            return cache_item["value"]

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        async with self._lock:
            # 检查缓存大小限制
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()

            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl > 0 else None

            self._cache[key] = {
                "value": value,
                "created_at": time.time(),
                "expires_at": expires_at,
                "ttl": ttl
            }
            self._access_times[key] = time.time()
            return True

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self._lock:
            return await self._remove_key(key)

    async def clear(self) -> bool:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._access_times.clear()
            return True

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.get(key) is not None

    async def _remove_key(self, key: str) -> bool:
        """移除键"""
        removed = key in self._cache
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        return removed

    async def _evict_lru(self) -> None:
        """移除最近最少使用的项"""
        if not self._access_times:
            return

        # 找到最少使用的键
        lru_key = min(self._access_times, key=self._access_times.get)
        await self._remove_key(lru_key)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "type": "memory",
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": 0.0,  # 需要实现命中率统计
            "memory_usage": sum(len(str(item)) for item in self._cache.values())
        }


class RedisCache(CacheBackend):
    """Redis缓存实现"""

    def __init__(self, redis_url: str, prefix: str = "listen_service:", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        """获取Redis连接"""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url)
        return self._redis

    def _make_key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            redis = await self._get_redis()
            data = await redis.get(self._make_key(key))
            if data is None:
                return None
            return pickle.loads(data)
        except Exception as e:
            logger.error("Redis获取失败", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            redis = await self._get_redis()
            data = pickle.dumps(value)
            ttl = ttl or self.default_ttl
            
            if ttl > 0:
                await redis.setex(self._make_key(key), ttl, data)
            else:
                await redis.set(self._make_key(key), data)
            return True
        except Exception as e:
            logger.error("Redis设置失败", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            redis = await self._get_redis()
            result = await redis.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error("Redis删除失败", key=key, error=str(e))
            return False

    async def clear(self) -> bool:
        """清空缓存"""
        try:
            redis = await self._get_redis()
            keys = await redis.keys(f"{self.prefix}*")
            if keys:
                await redis.delete(*keys)
            return True
        except Exception as e:
            logger.error("Redis清空失败", error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            redis = await self._get_redis()
            result = await redis.exists(self._make_key(key))
            return result > 0
        except Exception as e:
            logger.error("Redis检查存在失败", key=key, error=str(e))
            return False

    async def close(self) -> None:
        """关闭Redis连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "type": "redis",
            "url": self.redis_url,
            "prefix": self.prefix,
            "connected": self._redis is not None
        }


class AudioCache:
    """音频分析缓存管理器"""

    def __init__(self, backend: Optional[CacheBackend] = None):
        self.settings = get_settings()
        self.backend = backend or self._create_backend()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }

    def _create_backend(self) -> CacheBackend:
        """创建缓存后端"""
        cache_config = self.settings.get_cache_config()
        
        if cache_config["backend"] == "redis":
            return RedisCache(
                redis_url=cache_config["redis_url"],
                prefix=cache_config["redis_prefix"],
                default_ttl=cache_config["default_ttl"]
            )
        else:
            return MemoryCache(
                max_size=cache_config["max_size"],
                default_ttl=cache_config["default_ttl"]
            )

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = await self.backend.get(key)
            if value is not None:
                self._stats["hits"] += 1
                logger.debug("缓存命中", key=key)
            else:
                self._stats["misses"] += 1
                logger.debug("缓存未命中", key=key)
            return value
        except Exception as e:
            logger.error("缓存获取失败", key=key, error=str(e))
            self._stats["misses"] += 1
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            result = await self.backend.set(key, value, ttl)
            if result:
                self._stats["sets"] += 1
                logger.debug("缓存设置成功", key=key, ttl=ttl)
            return result
        except Exception as e:
            logger.error("缓存设置失败", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            result = await self.backend.delete(key)
            if result:
                self._stats["deletes"] += 1
                logger.debug("缓存删除成功", key=key)
            return result
        except Exception as e:
            logger.error("缓存删除失败", key=key, error=str(e))
            return False

    async def clear(self) -> bool:
        """清空缓存"""
        try:
            result = await self.backend.clear()
            if result:
                logger.info("缓存清空成功")
            return result
        except Exception as e:
            logger.error("缓存清空失败", error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.backend.exists(key)

    def generate_key(self, *args: Any) -> str:
        """生成缓存键"""
        key_data = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        backend_stats = self.backend.get_stats()
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            **backend_stats,
            "requests": {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "sets": self._stats["sets"],
                "deletes": self._stats["deletes"],
                "total": total_requests,
                "hit_rate": hit_rate
            }
        }

    async def cleanup(self) -> None:
        """清理资源"""
        if isinstance(self.backend, RedisCache):
            await self.backend.close()
        logger.info("缓存资源清理完成")


# 全局缓存实例
_cache_instance: Optional[AudioCache] = None


def get_cache() -> AudioCache:
    """获取全局缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AudioCache()
    return _cache_instance


async def cleanup_cache() -> None:
    """清理全局缓存"""
    global _cache_instance
    if _cache_instance:
        await _cache_instance.cleanup()
        _cache_instance = None