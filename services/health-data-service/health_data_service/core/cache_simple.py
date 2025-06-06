"""
cache_simple - 索克生活项目模块
"""

            import fnmatch
from .config import get_settings
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from loguru import logger
from typing import Any, Dict, List, Optional, Union, Callable
import asyncio
import json
import time

#!/usr/bin/env python3
"""
简化缓存管理模块

提供内存缓存操作，避免Redis依赖问题。
"""




settings = get_settings()


class SimpleCacheManager:
    """简化缓存管理器 - 使用内存缓存"""

    def __init__(self):
        self.settings = settings
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def initialize(self):
        """初始化缓存"""
        try:
            self._cache = {}
            self._locks = {}
            logger.info("内存缓存初始化成功")
        except Exception as e:
            logger.error(f"缓存初始化失败: {e}")
            raise

    async def close(self):
        """关闭缓存"""
        self._cache.clear()
        self._locks.clear()
        logger.info("缓存已关闭")

    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """检查缓存项是否过期"""
        if 'expire_time' not in item:
            return False
        return time.time() > item['expire_time']

    def _cleanup_expired(self):
        """清理过期的缓存项"""
        expired_keys = []
        for key, item in self._cache.items():
            if self._is_expired(item):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """设置缓存值"""
        try:
            # 序列化值
            if serialize:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_value = str(value)
            else:
                serialized_value = value

            # 设置缓存项
            cache_item = {
                'value': serialized_value,
                'created_time': time.time()
            }
            
            if expire:
                cache_item['expire_time'] = time.time() + expire

            self._cache[key] = cache_item
            return True

        except Exception as e:
            logger.error(f"设置缓存失败 key={key}: {e}")
            return False

    async def get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True
    ) -> Any:
        """获取缓存值"""
        try:
            # 清理过期缓存
            self._cleanup_expired()
            
            if key not in self._cache:
                return default
            
            item = self._cache[key]
            if self._is_expired(item):
                del self._cache[key]
                return default

            value = item['value']
            
            # 反序列化值
            if deserialize:
                try:
                    # 尝试JSON反序列化
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # 返回原始值
                    return value
            else:
                return value

        except Exception as e:
            logger.error(f"获取缓存失败 key={key}: {e}")
            return default

    async def delete(self, *keys: str) -> int:
        """删除缓存键"""
        try:
            deleted_count = 0
            for key in keys:
                if key in self._cache:
                    del self._cache[key]
                    deleted_count += 1
            return deleted_count
        except Exception as e:
            logger.error(f"删除缓存失败 keys={keys}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            self._cleanup_expired()
            return key in self._cache and not self._is_expired(self._cache[key])
        except Exception as e:
            logger.error(f"检查缓存存在性失败 key={key}: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        try:
            if key in self._cache:
                self._cache[key]['expire_time'] = time.time() + seconds
                return True
            return False
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 key={key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        try:
            if key not in self._cache:
                return -2  # 键不存在
            
            item = self._cache[key]
            if 'expire_time' not in item:
                return -1  # 永不过期
            
            remaining = item['expire_time'] - time.time()
            return int(remaining) if remaining > 0 else -2
        except Exception as e:
            logger.error(f"获取缓存TTL失败 key={key}: {e}")
            return -1

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的所有键"""
        try:
            self._cleanup_expired()
            if pattern == "*":
                return list(self._cache.keys())
            
            # 简单的模式匹配
            return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
        except Exception as e:
            logger.error(f"获取缓存键列表失败 pattern={pattern}: {e}")
            return []

    async def flushdb(self) -> bool:
        """清空当前数据库"""
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"清空缓存数据库失败: {e}")
            return False

    async def ping(self) -> bool:
        """检查缓存连接状态"""
        try:
            # 对于内存缓存，总是返回True
            return True
        except Exception as e:
            logger.error(f"缓存ping失败: {e}")
            return False


class SimpleDistributedLock:
    """简化分布式锁"""

    def __init__(self, cache_manager: SimpleCacheManager, key: str, timeout: int = 30):
        self.cache_manager = cache_manager
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.identifier = f"{time.time()}_{id(self)}"

    async def acquire(self) -> bool:
        """获取锁"""
        try:
            # 检查锁是否已存在
            if await self.cache_manager.exists(self.key):
                return False
            
            # 设置锁
            return await self.cache_manager.set(
                self.key, 
                self.identifier, 
                expire=self.timeout,
                serialize=False
            )
        except Exception as e:
            logger.error(f"获取分布式锁失败 key={self.key}: {e}")
            return False

    async def release(self) -> bool:
        """释放锁"""
        try:
            # 检查锁的所有者
            current_value = await self.cache_manager.get(
                self.key, 
                deserialize=False
            )
            
            if current_value == self.identifier:
                await self.cache_manager.delete(self.key)
                return True
            return False
        except Exception as e:
            logger.error(f"释放分布式锁失败 key={self.key}: {e}")
            return False

    @asynccontextmanager
    async def __aenter__(self):
        """异步上下文管理器入口"""
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError(f"无法获取锁: {self.key}")
        try:
            yield self
        finally:
            await self.release()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.release()


# 全局缓存管理器实例
_cache_manager: Optional[SimpleCacheManager] = None


async def get_cache_manager() -> SimpleCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SimpleCacheManager()
        await _cache_manager.initialize()
    return _cache_manager


def cached(
    key_prefix: str = "",
    expire: int = 3600,
    serialize: bool = True
) -> Callable:
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            cache_manager = await get_cache_manager()
            
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key, serialize=serialize)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, expire=expire, serialize=serialize)
            return result
        
        return wrapper
    return decorator


async def distributed_lock(key: str, timeout: int = 30) -> SimpleDistributedLock:
    """创建分布式锁"""
    cache_manager = await get_cache_manager()
    return SimpleDistributedLock(cache_manager, key, timeout) 