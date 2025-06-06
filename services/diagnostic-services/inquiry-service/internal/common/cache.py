"""
cache - 索克生活项目模块
"""

        import fnmatch
from .exceptions import ConfigurationError, ServiceUnavailableError
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
import asyncio
import json
import logging

#!/usr/bin/env python

"""
缓存管理模块
"""


try:

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: datetime
    expires_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime | None = None

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """更新访问时间和计数"""
        self.last_accessed = datetime.now()
        self.access_count += 1

class MemoryCache:
    """内存缓存实现"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        entry = self._cache.get(key)
        if entry is None:
            return None

        if entry.is_expired():
            await self.delete(key)
            return None

        entry.touch()
        return entry.value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置缓存值"""
        if len(self._cache) >= self.max_size:
            await self._evict_lru()

        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

        entry = CacheEntry(
            key=key, value=value, created_at=datetime.now(), expires_at=expires_at
        )

        self._cache[key] = entry
        self._logger.debug(f"缓存设置: {key}")

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]
            self._logger.debug(f"缓存删除: {key}")
            return True
        return False

    async def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._logger.info("缓存已清空")

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        entry = self._cache.get(key)
        if entry is None:
            return False

        if entry.is_expired():
            await self.delete(key)
            return False

        return True

    async def keys(self, pattern: str = "*") -> list[str]:
        """获取匹配的键列表"""
        # 简单的通配符匹配
        if pattern == "*":
            return list(self._cache.keys())


        return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

    async def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    async def stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "max_size": self.max_size,
            "usage_ratio": total_entries / self.max_size if self.max_size > 0 else 0,
        }

    async def _evict_lru(self) -> None:
        """LRU淘汰策略"""
        if not self._cache:
            return

        # 找到最少使用的条目
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (
                self._cache[k].last_accessed or self._cache[k].created_at,
                self._cache[k].access_count,
            ),
        )

        await self.delete(lru_key)
        self._logger.debug(f"LRU淘汰: {lru_key}")

class RedisCache:
    """Redis缓存实现"""

    def __init__(
        self, redis_url: str, default_ttl: int = 3600, key_prefix: str = "inquiry:"
    ):
        if not REDIS_AVAILABLE:
            raise ConfigurationError("Redis不可用，请安装redis-py库")

        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self._redis: redis.Redis | None = None
        self._logger = logging.getLogger(self.__class__.__name__)

    async def connect(self) -> None:
        """连接Redis"""
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            self._logger.info("Redis连接成功")
        except Exception as e:
            self._logger.error(f"Redis连接失败: {e!s}")
            raise ServiceUnavailableError(f"Redis连接失败: {e!s}", "redis")

    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._logger.info("Redis连接已断开")

    def _get_full_key(self, key: str) -> str:
        """获取完整的键名"""
        return f"{self.key_prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            full_key = self._get_full_key(key)
            value = await self._redis.get(full_key)

            if value is None:
                return None

            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            self._logger.error(f"Redis获取失败: {e!s}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置缓存值"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            full_key = self._get_full_key(key)
            ttl = ttl or self.default_ttl

            # JSON序列化
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)

            if ttl > 0:
                await self._redis.setex(full_key, ttl, value)
            else:
                await self._redis.set(full_key, value)

            self._logger.debug(f"Redis缓存设置: {key}")
        except Exception as e:
            self._logger.error(f"Redis设置失败: {e!s}")
            raise

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            full_key = self._get_full_key(key)
            result = await self._redis.delete(full_key)
            self._logger.debug(f"Redis缓存删除: {key}")
            return result > 0
        except Exception as e:
            self._logger.error(f"Redis删除失败: {e!s}")
            return False

    async def clear(self) -> None:
        """清空缓存"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            pattern = f"{self.key_prefix}*"
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
            self._logger.info("Redis缓存已清空")
        except Exception as e:
            self._logger.error(f"Redis清空失败: {e!s}")
            raise

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            full_key = self._get_full_key(key)
            return await self._redis.exists(full_key) > 0
        except Exception as e:
            self._logger.error(f"Redis存在检查失败: {e!s}")
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """获取匹配的键列表"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            full_pattern = f"{self.key_prefix}{pattern}"
            keys = await self._redis.keys(full_pattern)
            # 移除前缀
            return [key[len(self.key_prefix) :] for key in keys]
        except Exception as e:
            self._logger.error(f"Redis键列表获取失败: {e!s}")
            return []

    async def size(self) -> int:
        """获取缓存大小"""
        keys = await self.keys()
        return len(keys)

    async def stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        if not self._redis:
            raise ServiceUnavailableError("Redis未连接", "redis")

        try:
            info = await self._redis.info()
            size = await self.size()

            return {
                "total_entries": size,
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "redis_version": info.get("redis_version", "unknown"),
            }
        except Exception as e:
            self._logger.error(f"Redis统计信息获取失败: {e!s}")
            return {}

class CacheManager:
    """缓存管理器"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._cache = None
        self._logger = logging.getLogger(self.__class__.__name__)

        # 初始化缓存实现
        cache_type = config.get("cache", {}).get("type", "memory")

        if cache_type == "redis":
            redis_config = config.get("cache", {}).get("redis", {})
            redis_url = redis_config.get("url", "redis://localhost:6379/0")
            default_ttl = redis_config.get("default_ttl", 3600)
            key_prefix = redis_config.get("key_prefix", "inquiry:")

            self._cache = RedisCache(redis_url, default_ttl, key_prefix)
        else:
            memory_config = config.get("cache", {}).get("memory", {})
            max_size = memory_config.get("max_size", 1000)
            default_ttl = memory_config.get("default_ttl", 3600)

            self._cache = MemoryCache(max_size, default_ttl)

        self._logger.info(f"缓存管理器初始化完成，类型: {cache_type}")

    async def initialize(self) -> None:
        """初始化缓存"""
        if isinstance(self._cache, RedisCache):
            await self._cache.connect()

    async def cleanup(self) -> None:
        """清理缓存"""
        if isinstance(self._cache, RedisCache):
            await self._cache.disconnect()

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        return await self._cache.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置缓存值"""
        await self._cache.set(key, value, ttl)

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        return await self._cache.delete(key)

    async def clear(self) -> None:
        """清空缓存"""
        await self._cache.clear()

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self._cache.exists(key)

    async def keys(self, pattern: str = "*") -> list[str]:
        """获取匹配的键列表"""
        return await self._cache.keys(pattern)

    async def size(self) -> int:
        """获取缓存大小"""
        return await self._cache.size()

    async def stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        return await self._cache.stats()

    def cache_key(self, *parts: str) -> str:
        """生成缓存键"""
        return ":".join(str(part) for part in parts)

    async def get_or_set(self, key: str, factory, ttl: int | None = None) -> Any:
        """获取缓存值，如果不存在则通过工厂函数创建"""
        value = await self.get(key)
        if value is not None:
            return value

        # 调用工厂函数创建值
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        await self.set(key, value, ttl)
        return value
