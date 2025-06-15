"""
高级缓存管理器
包含多级缓存、缓存预热和失效策略
"""

import asyncio
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import pickle
import zlib
from redis.asyncio import Redis
from functools import wraps
import time

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheLevel(Enum):
    """缓存级别"""
    MEMORY = "memory"  # 内存缓存
    REDIS = "redis"    # Redis缓存
    BOTH = "both"      # 双级缓存


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"        # 最近最少使用
    LFU = "lfu"        # 最少使用频率
    TTL = "ttl"        # 基于时间


@dataclass
class CacheConfig:
    """缓存配置"""
    ttl: int = 300  # 默认5分钟
    max_size: int = 1000  # 内存缓存最大条目数
    strategy: CacheStrategy = CacheStrategy.LRU
    level: CacheLevel = CacheLevel.BOTH
    compress: bool = False  # 是否压缩
    serialize_method: str = "json"  # json, pickle
    prefix: str = ""
    version: int = 1  # 缓存版本，用于批量失效


@dataclass
class CacheItem:
    """缓存项"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size: int = 0  # 字节大小


class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: Dict[str, CacheItem] = {}
        self._access_order: List[str] = []  # LRU顺序
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # 检查过期
            if item.expires_at and datetime.now() > item.expires_at:
                await self._remove(key)
                return None
            
            # 更新访问信息
            item.access_count += 1
            item.last_accessed = datetime.now()
            
            # 更新LRU顺序
            if self.strategy == CacheStrategy.LRU:
                self._access_order.remove(key)
                self._access_order.append(key)
            
            return item.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存项"""
        async with self._lock:
            # 计算过期时间
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # 计算大小
            size = len(str(value).encode('utf-8'))
            
            # 创建缓存项
            item = CacheItem(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                size=size
            )
            
            # 检查是否需要清理空间
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict()
            
            # 存储缓存项
            self._cache[key] = item
            
            # 更新访问顺序
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        async with self._lock:
            return await self._remove(key)
    
    async def clear(self):
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    async def _remove(self, key: str) -> bool:
        """内部删除方法"""
        if key in self._cache:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False
    
    async def _evict(self):
        """缓存淘汰"""
        if not self._cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # 删除最近最少使用的项
            if self._access_order:
                key_to_remove = self._access_order[0]
                await self._remove(key_to_remove)
        
        elif self.strategy == CacheStrategy.LFU:
            # 删除使用频率最低的项
            min_access_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].access_count
            )
            await self._remove(min_access_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_size = sum(item.size for item in self._cache.values())
        
        return {
            'total_items': len(self._cache),
            'max_size': self.max_size,
            'total_memory_bytes': total_size,
            'strategy': self.strategy.value
        }


class AdvancedCacheManager(Generic[T]):
    """高级缓存管理器"""
    
    def __init__(self, redis: Redis, config: CacheConfig = None):
        self.redis = redis
        self.config = config or CacheConfig()
        self.memory_cache = MemoryCache(
            max_size=self.config.max_size,
            strategy=self.config.strategy
        )
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'memory_hits': 0,
            'redis_hits': 0
        }
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        prefix = f"{self.config.prefix}:" if self.config.prefix else ""
        version = f"v{self.config.version}:"
        return f"{prefix}{version}{key}"
    
    async def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        full_key = self._make_key(key)
        
        # 尝试从内存缓存获取
        if self.config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
            value = await self.memory_cache.get(full_key)
            if value is not None:
                self._stats['hits'] += 1
                self._stats['memory_hits'] += 1
                return value
        
        # 尝试从Redis获取
        if self.config.level in [CacheLevel.REDIS, CacheLevel.BOTH]:
            try:
                redis_value = await self.redis.get(full_key)
                if redis_value is not None:
                    # 反序列化
                    value = self._deserialize(redis_value)
                    
                    # 回填到内存缓存
                    if self.config.level == CacheLevel.BOTH:
                        await self.memory_cache.set(full_key, value, self.config.ttl)
                    
                    self._stats['hits'] += 1
                    self._stats['redis_hits'] += 1
                    return value
            except Exception as e:
                logger.error(f"Redis获取缓存失败: {e}")
        
        self._stats['misses'] += 1
        return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        tags: List[str] = None
    ) -> bool:
        """设置缓存值"""
        full_key = self._make_key(key)
        cache_ttl = ttl or self.config.ttl
        
        try:
            # 设置到内存缓存
            if self.config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
                await self.memory_cache.set(full_key, value, cache_ttl)
            
            # 设置到Redis
            if self.config.level in [CacheLevel.REDIS, CacheLevel.BOTH]:
                serialized_value = self._serialize(value)
                await self.redis.setex(full_key, cache_ttl, serialized_value)
                
                # 设置标签索引
                if tags:
                    await self._set_tags(full_key, tags, cache_ttl)
            
            self._stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        full_key = self._make_key(key)
        
        success = True
        
        # 从内存缓存删除
        if self.config.level in [CacheLevel.MEMORY, CacheLevel.BOTH]:
            await self.memory_cache.delete(full_key)
        
        # 从Redis删除
        if self.config.level in [CacheLevel.REDIS, CacheLevel.BOTH]:
            try:
                result = await self.redis.delete(full_key)
                success = success and (result > 0)
            except Exception as e:
                logger.error(f"Redis删除缓存失败: {e}")
                success = False
        
        if success:
            self._stats['deletes'] += 1
        
        return success
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        if self.config.serialize_method == "json":
            serialized = json.dumps(value, default=str).encode('utf-8')
        elif self.config.serialize_method == "pickle":
            serialized = pickle.dumps(value)
        else:
            serialized = str(value).encode('utf-8')
        
        # 压缩
        if self.config.compress:
            serialized = zlib.compress(serialized)
        
        return serialized
    
    def _deserialize(self, data: bytes) -> Any:
        """反序列化值"""
        # 解压缩
        if self.config.compress:
            data = zlib.decompress(data)
        
        if self.config.serialize_method == "json":
            return json.loads(data.decode('utf-8'))
        elif self.config.serialize_method == "pickle":
            return pickle.loads(data)
        else:
            return data.decode('utf-8')
    
    async def _set_tags(self, key: str, tags: List[str], ttl: int):
        """设置标签索引"""
        for tag in tags:
            tag_key = f"tag:{tag}"
            await self.redis.sadd(tag_key, key)
            await self.redis.expire(tag_key, ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_ratio = (self._stats['hits'] / total_requests) if total_requests > 0 else 0
        
        memory_stats = self.memory_cache.get_stats()
        
        return {
            **self._stats,
            'hit_ratio': hit_ratio,
            'memory_cache': memory_stats,
            'config': {
                'ttl': self.config.ttl,
                'max_size': self.config.max_size,
                'strategy': self.config.strategy.value,
                'level': self.config.level.value,
                'compress': self.config.compress
            }
        }


# 缓存装饰器
def cached(
    ttl: int = 300,
    key_prefix: str = "",
    tags: List[str] = None,
    cache_manager: AdvancedCacheManager = None
):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if cache_manager is None:
                # 如果没有提供缓存管理器，直接执行函数
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # 生成缓存键
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 设置到缓存
            await cache_manager.set(cache_key, result, ttl, tags)
            
            return result
        
        return wrapper
    return decorator