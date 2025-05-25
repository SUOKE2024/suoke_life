#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
缓存服务

提供统一的缓存接口，支持Redis和内存缓存。
"""

import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass, asdict

import redis.asyncio as redis
from structlog import get_logger

logger = get_logger()


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    
    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class CacheService(ABC):
    """缓存服务抽象基类"""
    
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
    async def ping(self) -> bool:
        """健康检查"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        pass


class RedisCacheService(CacheService):
    """Redis缓存服务实现"""
    
    def __init__(self, redis_client: redis.Redis, config: Dict):
        self.redis = redis_client
        self.config = config
        self.default_ttl = config.get("default_ttl", 3600)  # 默认1小时
        self.key_prefix = config.get("key_prefix", "look_service:")
        self.stats = CacheStats()
        
    async def initialize(self):
        """初始化缓存服务"""
        try:
            await self.ping()
            logger.info("Redis缓存服务初始化成功")
        except Exception as e:
            logger.error("Redis缓存服务初始化失败", error=str(e))
            raise
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            return value
        else:
            return json.dumps(value, ensure_ascii=False)
    
    def _deserialize_value(self, value: str) -> Any:
        """反序列化值"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            full_key = self._make_key(key)
            value = await self.redis.get(full_key)
            
            if value is not None:
                self.stats.hits += 1
                return self._deserialize_value(value)
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            self.stats.errors += 1
            logger.error("获取缓存失败", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            full_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.default_ttl
            
            await self.redis.setex(full_key, ttl, serialized_value)
            self.stats.sets += 1
            return True
            
        except Exception as e:
            self.stats.errors += 1
            logger.error("设置缓存失败", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            full_key = self._make_key(key)
            result = await self.redis.delete(full_key)
            self.stats.deletes += 1
            return result > 0
            
        except Exception as e:
            self.stats.errors += 1
            logger.error("删除缓存失败", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            full_key = self._make_key(key)
            return await self.redis.exists(full_key) > 0
        except Exception as e:
            self.stats.errors += 1
            logger.error("检查缓存键失败", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        try:
            pattern = f"{self.key_prefix}*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            self.stats.errors += 1
            logger.error("清空缓存失败", error=str(e))
            return False
    
    async def ping(self) -> bool:
        """健康检查"""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error("Redis健康检查失败", error=str(e))
            return False
    
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        return self.stats
    
    async def close(self):
        """关闭连接"""
        try:
            await self.redis.close()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error("关闭Redis连接失败", error=str(e))


class MemoryCacheService(CacheService):
    """内存缓存服务实现"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache: Dict[str, Dict] = {}
        self.default_ttl = config.get("default_ttl", 3600)
        self.max_size = config.get("max_size", 1000)
        self.stats = CacheStats()
        
    async def initialize(self):
        """初始化缓存服务"""
        logger.info("内存缓存服务初始化成功")
    
    def _is_expired(self, item: Dict) -> bool:
        """检查项目是否过期"""
        if item.get("ttl") is None:
            return False
        return time.time() > item["created_at"] + item["ttl"]
    
    def _cleanup_expired(self):
        """清理过期项目"""
        current_time = time.time()
        expired_keys = []
        
        for key, item in self.cache.items():
            if item.get("ttl") and current_time > item["created_at"] + item["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def _evict_if_needed(self):
        """如果需要，执行LRU淘汰"""
        if len(self.cache) >= self.max_size:
            # 简单的LRU实现：删除最旧的项目
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["accessed_at"])
            del self.cache[oldest_key]
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            self._cleanup_expired()
            
            if key in self.cache:
                item = self.cache[key]
                if not self._is_expired(item):
                    item["accessed_at"] = time.time()
                    self.stats.hits += 1
                    return item["value"]
                else:
                    del self.cache[key]
            
            self.stats.misses += 1
            return None
            
        except Exception as e:
            self.stats.errors += 1
            logger.error("获取内存缓存失败", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            self._cleanup_expired()
            self._evict_if_needed()
            
            current_time = time.time()
            self.cache[key] = {
                "value": value,
                "created_at": current_time,
                "accessed_at": current_time,
                "ttl": ttl or self.default_ttl
            }
            
            self.stats.sets += 1
            return True
            
        except Exception as e:
            self.stats.errors += 1
            logger.error("设置内存缓存失败", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if key in self.cache:
                del self.cache[key]
                self.stats.deletes += 1
                return True
            return False
            
        except Exception as e:
            self.stats.errors += 1
            logger.error("删除内存缓存失败", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            self._cleanup_expired()
            return key in self.cache and not self._is_expired(self.cache[key])
        except Exception as e:
            self.stats.errors += 1
            logger.error("检查内存缓存键失败", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        try:
            self.cache.clear()
            return True
        except Exception as e:
            self.stats.errors += 1
            logger.error("清空内存缓存失败", error=str(e))
            return False
    
    async def ping(self) -> bool:
        """健康检查"""
        return True
    
    async def get_stats(self) -> CacheStats:
        """获取统计信息"""
        return self.stats
    
    async def close(self):
        """关闭服务"""
        self.cache.clear()
        logger.info("内存缓存服务已关闭")


class CacheManager:
    """缓存管理器，提供高级缓存功能"""
    
    def __init__(self, cache_service: CacheService):
        self.cache = cache_service
        
    async def get_or_set(
        self, 
        key: str, 
        factory_func, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """获取缓存值，如果不存在则调用工厂函数生成"""
        value = await self.cache.get(key)
        
        if value is not None:
            return value
        
        # 调用工厂函数生成值
        if asyncio.iscoroutinefunction(factory_func):
            value = await factory_func(*args, **kwargs)
        else:
            value = factory_func(*args, **kwargs)
        
        # 设置缓存
        await self.cache.set(key, value, ttl)
        return value
    
    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 将参数转换为字符串并生成哈希
        key_parts = [prefix]
        
        for arg in args:
            if isinstance(arg, (dict, list)):
                key_parts.append(json.dumps(arg, sort_keys=True, ensure_ascii=False))
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (dict, list)):
                key_parts.append(f"{k}:{json.dumps(v, sort_keys=True, ensure_ascii=False)}")
            else:
                key_parts.append(f"{k}:{v}")
        
        key_string = "|".join(key_parts)
        
        # 如果键太长，使用哈希
        if len(key_string) > 200:
            hash_obj = hashlib.md5(key_string.encode('utf-8'))
            return f"{prefix}:hash:{hash_obj.hexdigest()}"
        
        return key_string
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """根据模式删除缓存键"""
        # 注意：这个功能在内存缓存中比较容易实现，在Redis中需要特殊处理
        if isinstance(self.cache, RedisCacheService):
            try:
                keys = await self.cache.redis.keys(f"{self.cache.key_prefix}{pattern}")
                if keys:
                    await self.cache.redis.delete(*keys)
                return len(keys)
            except Exception as e:
                logger.error("根据模式删除Redis缓存失败", pattern=pattern, error=str(e))
                return 0
        elif isinstance(self.cache, MemoryCacheService):
            import fnmatch
            matching_keys = [
                key for key in self.cache.cache.keys() 
                if fnmatch.fnmatch(key, pattern)
            ]
            for key in matching_keys:
                await self.cache.delete(key)
            return len(matching_keys)
        
        return 0


# 缓存装饰器
def cached(
    key_prefix: str, 
    ttl: Optional[int] = None,
    cache_manager: Optional[CacheManager] = None
):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if cache_manager is None:
                # 如果没有提供缓存管理器，直接调用函数
                return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # 生成缓存键
            cache_key = cache_manager.cache_key(key_prefix, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = await cache_manager.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 调用原函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 设置缓存
            await cache_manager.cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator 