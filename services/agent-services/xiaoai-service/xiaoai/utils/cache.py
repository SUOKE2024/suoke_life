"""
缓存管理器

提供统一的缓存接口和管理功能
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""

    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class CacheManager:
    """缓存管理器"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        初始化缓存管理器

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间(秒)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            # 检查是否过期
            if entry.expires_at and datetime.now() > entry.expires_at:
                del self._cache[key]
                return None

            # 更新访问信息
            entry.access_count += 1
            entry.last_accessed = datetime.now()

            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        async with self._lock:
            # 检查缓存大小限制
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()

            # 计算过期时间
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.default_ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=self.default_ttl)

            # 创建缓存条目
            entry = CacheEntry(value=value, created_at=datetime.now(), expires_at=expires_at)

            self._cache[key] = entry

    async def delete(self, key: str) -> bool:
        """删除缓存条目"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False

            # 检查是否过期
            if entry.expires_at and datetime.now() > entry.expires_at:
                del self._cache[key]
                return False

            return True

    async def size(self) -> int:
        """获取缓存大小"""
        async with self._lock:
            return len(self._cache)

    async def cleanup_expired(self) -> int:
        """清理过期缓存"""
        async with self._lock:
            now = datetime.now()
            expired_keys = []

            for key, entry in self._cache.items():
                if entry.expires_at and now > entry.expires_at:
                    expired_keys.append(key)

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    async def _evict_lru(self) -> None:
        """淘汰最近最少使用的缓存条目"""
        if not self._cache:
            return

        # 找到最近最少访问的条目
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (
                self._cache[k].last_accessed or self._cache[k].created_at,
                self._cache[k].access_count,
            ),
        )

        del self._cache[lru_key]
        logger.debug(f"淘汰LRU缓存条目: {lru_key}")

    def generate_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数序列化为字符串
        key_data = {'args': args, 'kwargs': sorted(kwargs.items()) if kwargs else {}}

        key_str = json.dumps(key_data, sort_keys=True, default=str)

        # 生成哈希值
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        async with self._lock:
            now = datetime.now()
            total_entries = len(self._cache)
            expired_entries = 0
            total_access_count = 0

            for entry in self._cache.values():
                if entry.expires_at and now > entry.expires_at:
                    expired_entries += 1
                total_access_count += entry.access_count

            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'total_access_count': total_access_count,
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
            }


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = CacheManager()
    return _global_cache_manager


async def cache_result(key: str, ttl: Optional[int] = None):
    """缓存装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            cache_key = f"{key}:{cache_manager.generate_key(*args,**kwargs)}"

            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
