"""
缓存管理器

实现多层缓存机制，提升五诊协同诊断系统的性能
"""

import asyncio
import logging
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import pickle
import weakref

import aioredis
from cachetools import TTLCache, LRUCache


logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """缓存级别"""
    MEMORY = "memory"      # 内存缓存
    REDIS = "redis"        # Redis缓存
    PERSISTENT = "persistent"  # 持久化缓存


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"           # 最近最少使用
    TTL = "ttl"           # 时间过期
    LFU = "lfu"           # 最少使用频率
    FIFO = "fifo"         # 先进先出


@dataclass
class CacheConfig:
    """缓存配置"""
    max_size: int = 1000
    ttl_seconds: int = 3600
    strategy: CacheStrategy = CacheStrategy.LRU
    enable_compression: bool = False
    enable_encryption: bool = False
    
    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # 持久化配置
    persistent_path: str = "/tmp/diagnosis_cache"


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """是否已过期"""
        if self.ttl_seconds is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """缓存年龄（秒）"""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    def touch(self) -> None:
        """更新访问时间和计数"""
        self.accessed_at = datetime.utcnow()
        self.access_count+=1


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        
        # 内存缓存
        if config.strategy==CacheStrategy.LRU:
            self.memory_cache = LRUCache(maxsize=config.max_size)
        elif config.strategy==CacheStrategy.TTL:
            self.memory_cache = TTLCache(maxsize=config.max_size, ttl=config.ttl_seconds)
        else:
            self.memory_cache = LRUCache(maxsize=config.max_size)
        
        # Redis缓存
        self.redis_client: Optional[aioredis.Redis] = None
        
        # 缓存统计
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "memory_hits": 0,
            "redis_hits": 0,
            "persistent_hits": 0
        }
        
        # 缓存键前缀
        self.key_prefix = "diagnosis_cache:"
        
        # 初始化标志
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化缓存管理器"""
        if self._initialized:
            return
        
        logger.info("初始化缓存管理器...")
        
        try:
            # 初始化Redis连接
            if self.config.redis_host:
                self.redis_client = await aioredis.from_url(
                    f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_db}",
                    password=self.config.redis_password,
                    encoding="utf-8",
                    decode_responses=False  # 保持二进制数据
                )
                
                # 测试连接
                await self.redis_client.ping()
                logger.info("Redis缓存连接成功")
            
            self._initialized = True
            logger.info("缓存管理器初始化完成")
            
        except Exception as e:
            logger.error(f"缓存管理器初始化失败: {e}")
            # 即使Redis连接失败，也可以使用内存缓存
            self._initialized = True
    
    def _generate_cache_key(self, key: str, namespace: str = "") -> str:
        """生成缓存键"""
        if namespace:
            full_key = f"{self.key_prefix}{namespace}:{key}"
        else:
            full_key = f"{self.key_prefix}{key}"
        
        # 如果键太长，使用哈希
        if len(full_key) > 250:
            hash_key = hashlib.sha256(full_key.encode()).hexdigest()
            return f"{self.key_prefix}hash:{hash_key}"
        
        return full_key
    
    def _serialize_value(self, value: Any) -> bytes:
        """序列化值"""
        try:
            # 使用pickle序列化
            data = pickle.dumps(value)
            
            # 可选压缩
            if self.config.enable_compression:
                import gzip
                data = gzip.compress(data)
            
            # 可选加密
            if self.config.enable_encryption:
                # 这里可以添加加密逻辑
                pass
            
            return data
            
        except Exception as e:
            logger.error(f"序列化值失败: {e}")
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """反序列化值"""
        try:
            # 可选解密
            if self.config.enable_encryption:
                # 这里可以添加解密逻辑
                pass
            
            # 可选解压缩
            if self.config.enable_compression:
                import gzip
                data = gzip.decompress(data)
            
            # 使用pickle反序列化
            return pickle.loads(data)
            
        except Exception as e:
            logger.error(f"反序列化值失败: {e}")
            raise
    
    async def get(
        self, 
        key: str, 
        namespace: str = "",
        levels: List[CacheLevel] = None
    ) -> Optional[Any]:
        """获取缓存值"""
        if not self._initialized:
            await self.initialize()
        
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        cache_key = self._generate_cache_key(key, namespace)
        
        # 按级别顺序查找
        for level in levels:
            try:
                if level==CacheLevel.MEMORY:
                    value = self._get_from_memory(cache_key)
                    if value is not None:
                        self.stats["hits"]+=1
                        self.stats["memory_hits"]+=1
                        return value
                
                elif level==CacheLevel.REDIS and self.redis_client:
                    value = await self._get_from_redis(cache_key)
                    if value is not None:
                        # 回填到内存缓存
                        self._set_to_memory(cache_key, value)
                        self.stats["hits"]+=1
                        self.stats["redis_hits"]+=1
                        return value
                
                elif level==CacheLevel.PERSISTENT:
                    value = await self._get_from_persistent(cache_key)
                    if value is not None:
                        # 回填到上层缓存
                        self._set_to_memory(cache_key, value)
                        if self.redis_client:
                            await self._set_to_redis(cache_key, value)
                        self.stats["hits"]+=1
                        self.stats["persistent_hits"]+=1
                        return value
                        
            except Exception as e:
                logger.warning(f"从{level.value}缓存获取失败: {e}")
                continue
        
        self.stats["misses"]+=1
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        namespace: str = "",
        ttl_seconds: Optional[int] = None,
        levels: List[CacheLevel] = None
    ) -> None:
        """设置缓存值"""
        if not self._initialized:
            await self.initialize()
        
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        cache_key = self._generate_cache_key(key, namespace)
        ttl = ttl_seconds or self.config.ttl_seconds
        
        # 设置到各个级别
        for level in levels:
            try:
                if level==CacheLevel.MEMORY:
                    self._set_to_memory(cache_key, value, ttl)
                
                elif level==CacheLevel.REDIS and self.redis_client:
                    await self._set_to_redis(cache_key, value, ttl)
                
                elif level==CacheLevel.PERSISTENT:
                    await self._set_to_persistent(cache_key, value, ttl)
                    
            except Exception as e:
                logger.warning(f"设置{level.value}缓存失败: {e}")
                continue
        
        self.stats["sets"]+=1
    
    async def delete(
        self, 
        key: str, 
        namespace: str = "",
        levels: List[CacheLevel] = None
    ) -> None:
        """删除缓存值"""
        if not self._initialized:
            await self.initialize()
        
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        cache_key = self._generate_cache_key(key, namespace)
        
        # 从各个级别删除
        for level in levels:
            try:
                if level==CacheLevel.MEMORY:
                    self._delete_from_memory(cache_key)
                
                elif level==CacheLevel.REDIS and self.redis_client:
                    await self._delete_from_redis(cache_key)
                
                elif level==CacheLevel.PERSISTENT:
                    await self._delete_from_persistent(cache_key)
                    
            except Exception as e:
                logger.warning(f"从{level.value}缓存删除失败: {e}")
                continue
        
        self.stats["deletes"]+=1
    
    def _get_from_memory(self, cache_key: str) -> Optional[Any]:
        """从内存缓存获取"""
        try:
            return self.memory_cache.get(cache_key)
        except Exception as e:
            logger.warning(f"内存缓存获取失败: {e}")
            return None
    
    def _set_to_memory(self, cache_key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """设置到内存缓存"""
        try:
            if isinstance(self.memory_cache, TTLCache) and ttl_seconds:
                # TTLCache会自动处理TTL
                self.memory_cache[cache_key] = value
            else:
                self.memory_cache[cache_key] = value
        except Exception as e:
            logger.warning(f"内存缓存设置失败: {e}")
    
    def _delete_from_memory(self, cache_key: str) -> None:
        """从内存缓存删除"""
        try:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
        except Exception as e:
            logger.warning(f"内存缓存删除失败: {e}")
    
    async def _get_from_redis(self, cache_key: str) -> Optional[Any]:
        """从Redis缓存获取"""
        try:
            data = await self.redis_client.get(cache_key)
            if data:
                return self._deserialize_value(data)
            return None
        except Exception as e:
            logger.warning(f"Redis缓存获取失败: {e}")
            return None
    
    async def _set_to_redis(self, cache_key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """设置到Redis缓存"""
        try:
            data = self._serialize_value(value)
            if ttl_seconds:
                await self.redis_client.setex(cache_key, ttl_seconds, data)
            else:
                await self.redis_client.set(cache_key, data)
        except Exception as e:
            logger.warning(f"Redis缓存设置失败: {e}")
    
    async def _delete_from_redis(self, cache_key: str) -> None:
        """从Redis缓存删除"""
        try:
            await self.redis_client.delete(cache_key)
        except Exception as e:
            logger.warning(f"Redis缓存删除失败: {e}")
    
    async def _get_from_persistent(self, cache_key: str) -> Optional[Any]:
        """从持久化缓存获取"""
        # 这里可以实现文件系统或数据库持久化
        return None
    
    async def _set_to_persistent(self, cache_key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """设置到持久化缓存"""
        # 这里可以实现文件系统或数据库持久化
        pass
    
    async def _delete_from_persistent(self, cache_key: str) -> None:
        """从持久化缓存删除"""
        # 这里可以实现文件系统或数据库持久化
        pass
    
    async def clear(self, namespace: str = "", levels: List[CacheLevel] = None) -> None:
        """清空缓存"""
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS]
        
        for level in levels:
            try:
                if level==CacheLevel.MEMORY:
                    if namespace:
                        # 清空特定命名空间
                        keys_to_delete = [
                            k for k in self.memory_cache.keys() 
                            if k.startswith(f"{self.key_prefix}{namespace}:")
                        ]
                        for key in keys_to_delete:
                            del self.memory_cache[key]
                    else:
                        self.memory_cache.clear()
                
                elif level==CacheLevel.REDIS and self.redis_client:
                    if namespace:
                        pattern = f"{self.key_prefix}{namespace}:*"
                        keys = await self.redis_client.keys(pattern)
                        if keys:
                            await self.redis_client.delete(*keys)
                    else:
                        pattern = f"{self.key_prefix}*"
                        keys = await self.redis_client.keys(pattern)
                        if keys:
                            await self.redis_client.delete(*keys)
                            
            except Exception as e:
                logger.warning(f"清空{level.value}缓存失败: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / max(total_requests, 1) * 100
        
        memory_size = len(self.memory_cache)
        
        redis_info = {}
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
            except Exception:
                pass
        
        return {
            "hit_rate": hit_rate,
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "deletes": self.stats["deletes"],
            "evictions": self.stats["evictions"],
            "memory_hits": self.stats["memory_hits"],
            "redis_hits": self.stats["redis_hits"],
            "persistent_hits": self.stats["persistent_hits"],
            "memory_cache_size": memory_size,
            "memory_cache_maxsize": self.config.max_size,
            "redis_info": redis_info
        }
    
    async def get_cache_keys(self, namespace: str = "", limit: int = 100) -> List[str]:
        """获取缓存键列表"""
        keys = []
        
        # 内存缓存键
        memory_keys = list(self.memory_cache.keys())
        if namespace:
            memory_keys = [
                k for k in memory_keys 
                if k.startswith(f"{self.key_prefix}{namespace}:")
            ]
        keys.extend(memory_keys[:limit])
        
        # Redis缓存键
        if self.redis_client and len(keys) < limit:
            try:
                if namespace:
                    pattern = f"{self.key_prefix}{namespace}:*"
                else:
                    pattern = f"{self.key_prefix}*"
                
                redis_keys = await self.redis_client.keys(pattern)
                redis_keys = [k.decode() if isinstance(k, bytes) else k for k in redis_keys]
                keys.extend(redis_keys[:limit - len(keys)])
            except Exception as e:
                logger.warning(f"获取Redis键失败: {e}")
        
        return keys[:limit]
    
    def cache_decorator(
        self, 
        namespace: str = "",
        ttl_seconds: Optional[int] = None,
        key_func: Optional[Callable] = None
    ):
        """缓存装饰器"""
        def decorator(func):
            async def wrapper(*args,**kwargs):
                # 生成缓存键
                if key_func:
                    cache_key = key_func(*args,**kwargs)
                else:
                    # 默认使用函数名和参数生成键
                    key_parts = [func.__name__]
                    key_parts.extend(str(arg) for arg in args)
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                    cache_key = ":".join(key_parts)
                
                # 尝试从缓存获取
                cached_result = await self.get(cache_key, namespace)
                if cached_result is not None:
                    return cached_result
                
                # 执行函数
                result = await func(*args,**kwargs)
                
                # 缓存结果
                await self.set(cache_key, result, namespace, ttl_seconds)
                
                return result
            
            return wrapper
        return decorator
    
    async def close(self) -> None:
        """关闭缓存管理器"""
        logger.info("关闭缓存管理器...")
        
        try:
            # 清空内存缓存
            self.memory_cache.clear()
            
            # 关闭Redis连接
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("缓存管理器已关闭")
            
        except Exception as e:
            logger.error(f"关闭缓存管理器失败: {e}")


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None


async def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """获取全局缓存管理器实例"""
    global _global_cache_manager
    if _global_cache_manager is None:
        if config is None:
            config = CacheConfig()
        _global_cache_manager = CacheManager(config)
        await _global_cache_manager.initialize()
    return _global_cache_manager


async def close_global_cache_manager() -> None:
    """关闭全局缓存管理器"""
    global _global_cache_manager
    if _global_cache_manager:
        await _global_cache_manager.close()
        _global_cache_manager = None


# 便捷函数
async def cache_get(key: str, namespace: str = "") -> Optional[Any]:
    """获取缓存值的便捷函数"""
    cache_manager = await get_cache_manager()
    return await cache_manager.get(key, namespace)


async def cache_set(key: str, value: Any, namespace: str = "", ttl_seconds: Optional[int] = None) -> None:
    """设置缓存值的便捷函数"""
    cache_manager = await get_cache_manager()
    await cache_manager.set(key, value, namespace, ttl_seconds)


async def cache_delete(key: str, namespace: str = "") -> None:
    """删除缓存值的便捷函数"""
    cache_manager = await get_cache_manager()
    await cache_manager.delete(key, namespace)


def cached(namespace: str = "", ttl_seconds: Optional[int] = None, key_func: Optional[Callable] = None):
    """缓存装饰器的便捷函数"""
    async def decorator(func):
        cache_manager = await get_cache_manager()
        return cache_manager.cache_decorator(namespace, ttl_seconds, key_func)(func)
    return decorator