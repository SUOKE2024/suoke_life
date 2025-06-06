"""
cache - 索克生活项目模块
"""

            import redis
            import sys
from datetime import datetime, timedelta
from typing import Any
import asyncio
import json
import logging
import os
import re

#!/usr/bin/env python3

"""
缓存管理器 - 支持Redis和内存缓存 - 增强版本
"""


try:
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class MemoryCache:
    """内存缓存实现 - 增强版本"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: dict[str, dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times: dict[str, datetime] = {}
        self.hit_count = 0
        self.miss_count = 0

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key not in self.cache:
            self.miss_count += 1
            return None

        item = self.cache[key]

        # 检查是否过期
        if item["expires_at"] and datetime.now() > item["expires_at"]:
            await self.delete(key)
            self.miss_count += 1
            return None

        # 更新访问时间
        self.access_times[key] = datetime.now()
        self.hit_count += 1
        return item["value"]

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        try:
            # 如果缓存已满，清理最旧的项
            if len(self.cache) >= self.max_size:
                await self._evict_oldest()

            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)

            self.cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": datetime.now()
            }
            self.access_times[key] = datetime.now()

            return True
        except Exception as e:
            logger.error(f"设置内存缓存失败: {e!s}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        except Exception as e:
            logger.error(f"删除内存缓存失败: {e!s}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存键"""
        try:
            regex = re.compile(pattern.replace('*', '.*'))
            keys_to_delete = [key for key in self.cache if regex.match(key)]

            for key in keys_to_delete:
                await self.delete(key)

            return len(keys_to_delete)
        except Exception as e:
            logger.error(f"删除模式缓存失败: {e!s}")
            return 0

    async def clear(self) -> bool:
        """清空缓存"""
        try:
            self.cache.clear()
            self.access_times.clear()
            self.hit_count = 0
            self.miss_count = 0
            return True
        except Exception as e:
            logger.error(f"清空内存缓存失败: {e!s}")
            return False

    async def _evict_oldest(self):
        """清理最旧的缓存项"""
        if not self.access_times:
            return

        # 找到最旧的键
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        await self.delete(oldest_key)

    async def cleanup_expired(self) -> int:
        """清理过期的缓存项"""
        now = datetime.now()
        expired_keys = []

        for key, item in self.cache.items():
            if item["expires_at"] and now > item["expires_at"]:
                expired_keys.append(key)

        for key in expired_keys:
            await self.delete(key)

        return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        now = datetime.now()
        expired_count = 0

        for _key, item in self.cache.items():
            if item["expires_at"] and now > item["expires_at"]:
                expired_count += 1

        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0

        return {
            "total_items": len(self.cache),
            "expired_items": expired_count,
            "max_size": self.max_size,
            "memory_usage_mb": self._estimate_memory_usage(),
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate
        }

    def _estimate_memory_usage(self) -> float:
        """估算内存使用量（MB）"""
        try:
            total_size = 0
            for key, item in self.cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(item)
                total_size += sys.getsizeof(item["value"])
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

class RedisCache:
    """Redis缓存实现 - 增强版本"""

    def __init__(self, redis_url: str = "redis://localhost:6379", prefix: str = "corn_maze:",
                 max_retries: int = 3, retry_delay: float = 1.0):
        self.redis_url = redis_url
        self.prefix = prefix
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.redis_client: redis.Redis | None = None
        self._connected = False
        self._connection_pool = None

    async def _ensure_connected(self):
        """确保Redis连接"""
        if not self._connected:
            try:
                # 创建连接池
                if not self._connection_pool:
                    self._connection_pool = redis.ConnectionPool.from_url(
                        self.redis_url,
                        decode_responses=True,
                        max_connections=20,
                        retry_on_timeout=True
                    )

                self.redis_client = redis.Redis(connection_pool=self._connection_pool)
                await self.redis_client.ping()
                self._connected = True
                logger.info("Redis连接成功")
            except Exception as e:
                logger.error(f"Redis连接失败: {e!s}")
                self._connected = False
                raise

    async def _execute_with_retry(self, operation, *args, **kwargs):
        """带重试的Redis操作执行"""
        for attempt in range(self.max_retries):
            try:
                await self._ensure_connected()
                return await operation(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Redis操作失败 (尝试 {attempt + 1}/{self.max_retries}): {e!s}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay * (attempt + 1))

    def _make_key(self, key: str) -> str:
        """生成带前缀的键"""
        return f"{self.prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        try:
            redis_key = self._make_key(key)
            value = await self._execute_with_retry(self.redis_client.get, redis_key)

            if value is None:
                return None

            # 尝试解析JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

        except Exception as e:
            logger.error(f"获取Redis缓存失败: {e!s}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        try:
            redis_key = self._make_key(key)

            # 序列化值
            if isinstance(value, dict | list):
                serialized_value = json.dumps(value, ensure_ascii=False, default=str)
            else:
                serialized_value = str(value)

            # 设置值
            if ttl:
                await self._execute_with_retry(self.redis_client.setex, redis_key, ttl, serialized_value)
            else:
                await self._execute_with_retry(self.redis_client.set, redis_key, serialized_value)

            return True

        except Exception as e:
            logger.error(f"设置Redis缓存失败: {e!s}")
            return False

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            redis_key = self._make_key(key)
            result = await self._execute_with_retry(self.redis_client.delete, redis_key)
            return result > 0

        except Exception as e:
            logger.error(f"删除Redis缓存失败: {e!s}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存键"""
        try:
            redis_pattern = self._make_key(pattern)
            keys = await self._execute_with_retry(self.redis_client.keys, redis_pattern)

            if keys:
                result = await self._execute_with_retry(self.redis_client.delete, *keys)
                return result
            return 0

        except Exception as e:
            logger.error(f"删除模式缓存失败: {e!s}")
            return 0

    async def clear(self) -> bool:
        """清空所有带前缀的缓存"""
        try:
            pattern = f"{self.prefix}*"
            keys = await self._execute_with_retry(self.redis_client.keys, pattern)

            if keys:
                await self._execute_with_retry(self.redis_client.delete, *keys)

            return True

        except Exception as e:
            logger.error(f"清空Redis缓存失败: {e!s}")
            return False

    async def get_stats(self) -> dict[str, Any]:
        """获取Redis统计信息"""
        try:
            info = await self._execute_with_retry(self.redis_client.info)
            pattern = f"{self.prefix}*"
            keys = await self._execute_with_retry(self.redis_client.keys, pattern)

            return {
                "total_keys": len(keys),
                "redis_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                "connected_clients": info.get("connected_clients", 0),
                "redis_version": info.get("redis_version", "unknown"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }

        except Exception as e:
            logger.error(f"获取Redis统计信息失败: {e!s}")
            return {}

    async def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
        if self._connection_pool:
            await self._connection_pool.disconnect()

class CacheManager:
    """缓存管理器 - 统一的缓存接口 - 增强版本"""

    def __init__(self, use_redis: bool | None = None, redis_url: str | None = None, fallback_to_memory: bool = True):
        """
        初始化缓存管理器

        Args:
            use_redis: 是否使用Redis，None表示自动检测
            redis_url: Redis连接URL
            fallback_to_memory: Redis不可用时是否回退到内存缓存
        """
        self.use_redis = use_redis
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.fallback_to_memory = fallback_to_memory

        # 自动检测是否使用Redis
        if self.use_redis is None:
            self.use_redis = REDIS_AVAILABLE and self._test_redis_connection()

        # 初始化缓存后端
        self.primary_backend = None
        self.fallback_backend = None

        if self.use_redis and REDIS_AVAILABLE:
            try:
                self.primary_backend = RedisCache(self.redis_url)
                logger.info("使用Redis作为主缓存")

                if self.fallback_to_memory:
                    self.fallback_backend = MemoryCache()
                    logger.info("使用内存缓存作为备用")
            except Exception as e:
                logger.warning(f"Redis初始化失败: {e!s}")
                if self.fallback_to_memory:
                    self.primary_backend = MemoryCache()
                    logger.info("回退到内存缓存")
        else:
            self.primary_backend = MemoryCache()
            logger.info("使用内存缓存")

    def _test_redis_connection(self) -> bool:
        """测试Redis连接"""
        try:
            r = redis.from_url(self.redis_url, socket_timeout=2, socket_connect_timeout=2)
            r.ping()
            r.close()
            return True
        except Exception:
            return False

    async def get(self, key: str) -> Any | None:
        """获取缓存值"""
        try:
            result = await self.primary_backend.get(key)
            if result is not None:
                return result

            # 如果主缓存未命中且有备用缓存，尝试备用缓存
            if self.fallback_backend:
                return await self.fallback_backend.get(key)

            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e!s}")
            if self.fallback_backend:
                try:
                    return await self.fallback_backend.get(key)
                except Exception:
                    pass
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """设置缓存值"""
        success = False

        try:
            success = await self.primary_backend.set(key, value, ttl)
        except Exception as e:
            logger.error(f"设置主缓存失败: {e!s}")

        # 同时设置备用缓存
        if self.fallback_backend:
            try:
                await self.fallback_backend.set(key, value, ttl)
            except Exception as e:
                logger.error(f"设置备用缓存失败: {e!s}")

        return success

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        success = False

        try:
            success = await self.primary_backend.delete(key)
        except Exception as e:
            logger.error(f"删除主缓存失败: {e!s}")

        # 同时删除备用缓存
        if self.fallback_backend:
            try:
                await self.fallback_backend.delete(key)
            except Exception as e:
                logger.error(f"删除备用缓存失败: {e!s}")

        return success

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的缓存键"""
        total_deleted = 0

        try:
            if hasattr(self.primary_backend, 'delete_pattern'):
                total_deleted += await self.primary_backend.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"删除主缓存模式失败: {e!s}")

        # 同时删除备用缓存
        if self.fallback_backend and hasattr(self.fallback_backend, 'delete_pattern'):
            try:
                total_deleted += await self.fallback_backend.delete_pattern(pattern)
            except Exception as e:
                logger.error(f"删除备用缓存模式失败: {e!s}")

        return total_deleted

    async def clear(self) -> bool:
        """清空缓存"""
        success = False

        try:
            success = await self.primary_backend.clear()
        except Exception as e:
            logger.error(f"清空主缓存失败: {e!s}")

        # 同时清空备用缓存
        if self.fallback_backend:
            try:
                await self.fallback_backend.clear()
            except Exception as e:
                logger.error(f"清空备用缓存失败: {e!s}")

        return success

    async def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "backend_type": "redis" if isinstance(self.primary_backend, RedisCache) else "memory",
            "has_fallback": self.fallback_backend is not None
        }

        try:
            primary_stats = await self.primary_backend.get_stats()
            stats["primary"] = primary_stats
        except Exception as e:
            logger.error(f"获取主缓存统计失败: {e!s}")
            stats["primary"] = {}

        if self.fallback_backend:
            try:
                fallback_stats = await self.fallback_backend.get_stats()
                stats["fallback"] = fallback_stats
            except Exception as e:
                logger.error(f"获取备用缓存统计失败: {e!s}")
                stats["fallback"] = {}

        return stats

    async def close(self):
        """关闭缓存连接"""
        if hasattr(self.primary_backend, 'close'):
            await self.primary_backend.close()
        if self.fallback_backend and hasattr(self.fallback_backend, 'close'):
            await self.fallback_backend.close()

# 缓存管理器单例
class CacheManagerSingleton:
    """缓存管理器单例"""

    _instance: CacheManager | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls, use_redis: bool | None = None, redis_url: str | None = None) -> CacheManager:
        """获取缓存管理器实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = CacheManager(use_redis=use_redis, redis_url=redis_url)
        return cls._instance

    @classmethod
    def get_instance_sync(cls, use_redis: bool | None = None, redis_url: str | None = None) -> CacheManager:
        """同步获取缓存管理器实例"""
        if cls._instance is None:
            cls._instance = CacheManager(use_redis=use_redis, redis_url=redis_url)
        return cls._instance

    @classmethod
    async def close_instance(cls):
        """关闭缓存管理器实例"""
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例（向后兼容）"""
    return CacheManagerSingleton.get_instance_sync()

async def get_cache_manager_async(use_redis: bool | None = None, redis_url: str | None = None) -> CacheManager:
    """异步获取全局缓存管理器实例"""
    return await CacheManagerSingleton.get_instance(use_redis=use_redis, redis_url=redis_url)

async def init_cache_manager(use_redis: bool | None = None, redis_url: str | None = None):
    """初始化全局缓存管理器（向后兼容）"""
    await CacheManagerSingleton.get_instance(use_redis=use_redis, redis_url=redis_url)

async def close_cache_manager():
    """关闭全局缓存管理器（向后兼容）"""
    await CacheManagerSingleton.close_instance()
