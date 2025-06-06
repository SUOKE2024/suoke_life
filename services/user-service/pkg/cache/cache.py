"""
cache - 索克生活项目模块
"""

            import fnmatch
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import asyncio
import hashlib
import json
import logging
import pickle

"""
缓存抽象层
提供统一的缓存接口，支持Redis和内存缓存
"""

logger = logging.getLogger(__name__)


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
        """删除缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> int:
        """清除缓存"""
        pass
    
    @abstractmethod
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        pass
    
    @abstractmethod
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        pass


class MemoryCache(CacheBackend):
    """内存缓存实现"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # 检查是否过期
            if entry.get('expires_at') and datetime.utcnow() > entry['expires_at']:
                del self._cache[key]
                return None
            
            return entry['value']
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self._max_size and key not in self._cache:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k].get('created_at', datetime.min))
                del self._cache[oldest_key]
            
            expires_at = None
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            self._cache[key] = {
                'value': value,
                'created_at': datetime.utcnow(),
                'expires_at': expires_at
            }
            return True
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        async with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                return count
            
            # 简单的模式匹配（支持*通配符）
            keys_to_delete = [key for key in self._cache.keys() 
                            if fnmatch.fnmatch(key, pattern)]
            
            for key in keys_to_delete:
                del self._cache[key]
            
            return len(keys_to_delete)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        for key, value in mapping.items():
            await self.set(key, value, ttl)
        return True


class RedisCache(CacheBackend):
    """Redis缓存实现"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        try:
            # 尝试JSON序列化
            return json.dumps(value, default=str).encode('utf-8')
        except (TypeError, ValueError):
            # 回退到pickle
            return pickle.dumps(value)
    
    def _deserialize(self, data: bytes) -> Any:
        """反序列化值"""
        try:
            # 尝试JSON反序列化
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 回退到pickle
            return pickle.loads(data)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            data = await self.redis.get(key)
            if data is None:
                return None
            return self._deserialize(data)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            data = self._serialize(value)
            if ttl:
                return await self.redis.setex(key, ttl, data)
            else:
                return await self.redis.set(key, data)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        try:
            if pattern is None:
                return await self.redis.flushdb()
            
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear error with pattern {pattern}: {e}")
            return 0
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        try:
            values = await self.redis.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)
            return result
        except Exception as e:
            logger.error(f"Redis get_many error: {e}")
            return {}
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            pipe = self.redis.pipeline()
            for key, value in mapping.items():
                data = self._serialize(value)
                if ttl:
                    pipe.setex(key, ttl, data)
                else:
                    pipe.set(key, data)
            await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Redis set_many error: {e}")
            return False


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, backend: CacheBackend, key_prefix: str = ""):
        self.backend = backend
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return await self.backend.get(self._make_key(key))
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        return await self.backend.set(self._make_key(key), value, ttl)
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        return await self.backend.delete(self._make_key(key))
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return await self.backend.exists(self._make_key(key))
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """清除缓存"""
        if pattern and self.key_prefix:
            pattern = f"{self.key_prefix}:{pattern}"
        elif self.key_prefix:
            pattern = f"{self.key_prefix}:*"
        return await self.backend.clear(pattern)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        full_keys = [self._make_key(key) for key in keys]
        result = await self.backend.get_many(full_keys)
        # 转换回原始键
        return {key: result[self._make_key(key)] 
                for key in keys if self._make_key(key) in result}
    
    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        full_mapping = {self._make_key(key): value for key, value in mapping.items()}
        return await self.backend.set_many(full_mapping, ttl)
    
    async def get_or_set(self, key: str, factory, ttl: Optional[int] = None) -> Any:
        """获取缓存，如果不存在则通过工厂函数创建"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # 调用工厂函数
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        await self.set(key, value, ttl)
        return value
    
    def cache_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并生成哈希
        key_parts = []
        for arg in args:
            key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(ttl: int = 300, key_func: Optional[callable] = None):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # 获取缓存管理器
            cache_manager = getattr(self, '_cache_manager', None)
            if not cache_manager:
                # 如果没有缓存管理器，直接调用函数
                return await func(self, *args, **kwargs)
            
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_manager.cache_key(*args, **kwargs)}"
            
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 调用原函数
            result = await func(self, *args, **kwargs)
            
            # 缓存结果
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator 