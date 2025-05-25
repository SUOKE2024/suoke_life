#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 缓存管理器
提供高效的缓存功能，支持Redis和内存缓存
"""

import json
import logging
import asyncio
import time
from typing import Any, Optional, Dict, Union, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import hashlib
import pickle
from functools import wraps

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from pkg.utils.config import Config

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """缓存配置"""
    backend: str = "memory"  # memory, redis
    redis_url: str = "redis://localhost:6379"
    default_ttl: int = 3600  # 默认过期时间（秒）
    max_memory_items: int = 10000  # 内存缓存最大条目数
    key_prefix: str = "laoke:"
    serializer: str = "json"  # json, pickle

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
    async def close(self) -> None:
        """关闭连接"""
        pass

class MemoryCacheBackend(CacheBackend):
    """内存缓存后端"""
    
    def __init__(self, max_items: int = 10000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_items = max_items
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None
            
            item = self._cache[key]
            
            # 检查是否过期
            if item['expires_at'] and time.time() > item['expires_at']:
                del self._cache[key]
                return None
            
            return item['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        async with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self._max_items and key not in self._cache:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k]['created_at'])
                del self._cache[oldest_key]
            
            expires_at = None
            if ttl:
                expires_at = time.time() + ttl
            
            self._cache[key] = {
                'value': value,
                'created_at': time.time(),
                'expires_at': expires_at
            }
            
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.get(key) is not None
    
    async def clear(self) -> bool:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            return True
    
    async def close(self) -> None:
        """关闭连接"""
        await self.clear()

class RedisCacheBackend(CacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._connected = False
    
    async def _ensure_connected(self) -> None:
        """确保Redis连接"""
        if not self._connected:
            try:
                self._redis = aioredis.from_url(self._redis_url)
                await self._redis.ping()
                self._connected = True
                logger.info("Redis缓存连接成功")
            except Exception as e:
                logger.error(f"Redis连接失败: {str(e)}")
                raise
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        await self._ensure_connected()
        try:
            value = await self._redis.get(key)
            if value is None:
                return None
            return json.loads(value.decode('utf-8'))
        except Exception as e:
            logger.error(f"Redis获取失败: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        await self._ensure_connected()
        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            if ttl:
                await self._redis.setex(key, ttl, serialized_value)
            else:
                await self._redis.set(key, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Redis设置失败: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        await self._ensure_connected()
        try:
            result = await self._redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis删除失败: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        await self._ensure_connected()
        try:
            result = await self._redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis检查存在失败: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        await self._ensure_connected()
        try:
            await self._redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis清空失败: {str(e)}")
            return False
    
    async def close(self) -> None:
        """关闭连接"""
        if self._redis:
            await self._redis.close()
            self._connected = False

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._backend: Optional[CacheBackend] = None
        self._initialized = False
        
        # 统计信息
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    async def _ensure_initialized(self) -> None:
        """确保缓存已初始化"""
        if not self._initialized:
            await self._initialize_backend()
    
    async def _initialize_backend(self) -> None:
        """初始化缓存后端"""
        try:
            if self.config.backend == "redis" and REDIS_AVAILABLE:
                self._backend = RedisCacheBackend(self.config.redis_url)
                logger.info("使用Redis缓存后端")
            else:
                if self.config.backend == "redis" and not REDIS_AVAILABLE:
                    logger.warning("Redis不可用，回退到内存缓存")
                self._backend = MemoryCacheBackend(self.config.max_memory_items)
                logger.info("使用内存缓存后端")
            
            self._initialized = True
            
        except Exception as e:
            logger.error(f"缓存后端初始化失败: {str(e)}")
            # 回退到内存缓存
            self._backend = MemoryCacheBackend(self.config.max_memory_items)
            self._initialized = True
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.config.key_prefix}{key}"
    
    def _hash_key(self, key: str) -> str:
        """对键进行哈希处理（用于长键）"""
        if len(key) > 250:  # Redis键长度限制
            return hashlib.md5(key.encode('utf-8')).hexdigest()
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        await self._ensure_initialized()
        
        full_key = self._make_key(self._hash_key(key))
        
        try:
            value = await self._backend.get(full_key)
            if value is not None:
                self._stats['hits'] += 1
                logger.debug(f"缓存命中: {key}")
                return value
            else:
                self._stats['misses'] += 1
                logger.debug(f"缓存未命中: {key}")
                return None
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"缓存获取错误: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        await self._ensure_initialized()
        
        full_key = self._make_key(self._hash_key(key))
        cache_ttl = ttl or self.config.default_ttl
        
        try:
            result = await self._backend.set(full_key, value, cache_ttl)
            if result:
                self._stats['sets'] += 1
                logger.debug(f"缓存设置成功: {key}, TTL: {cache_ttl}")
            return result
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"缓存设置错误: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        await self._ensure_initialized()
        
        full_key = self._make_key(self._hash_key(key))
        
        try:
            result = await self._backend.delete(full_key)
            if result:
                self._stats['deletes'] += 1
                logger.debug(f"缓存删除成功: {key}")
            return result
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"缓存删除错误: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        await self._ensure_initialized()
        
        full_key = self._make_key(self._hash_key(key))
        
        try:
            return await self._backend.exists(full_key)
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"缓存检查存在错误: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        await self._ensure_initialized()
        
        try:
            result = await self._backend.clear()
            if result:
                logger.info("缓存已清空")
            return result
        except Exception as e:
            self._stats['errors'] += 1
            logger.error(f"缓存清空错误: {str(e)}")
            return False
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """获取缓存值，如果不存在则通过工厂函数生成并缓存"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # 生成新值
        if asyncio.iscoroutinefunction(factory_func):
            value = await factory_func()
        else:
            value = factory_func()
        
        # 缓存新值
        await self.set(key, value, ttl)
        return value
    
    async def mget(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值"""
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def mset(self, items: Dict[str, Any], ttl: Optional[int] = None) -> int:
        """批量设置缓存值"""
        success_count = 0
        for key, value in items.items():
            if await self.set(key, value, ttl):
                success_count += 1
        return success_count
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': hit_rate,
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'errors': self._stats['errors'],
            'backend': self.config.backend
        }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
    
    async def close(self) -> None:
        """关闭缓存管理器"""
        if self._backend:
            await self._backend.close()
            logger.info("缓存管理器已关闭")

def cache_result(key_func=None, ttl: int = 3600):
    """缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成策略
                func_name = func.__name__
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func_name}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cache_manager = CacheManager()
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None

def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(config)
    return _cache_manager 