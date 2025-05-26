#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能缓存管理器
支持多级缓存、LRU策略、缓存预热和智能失效
"""

import asyncio
import json
import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from collections import OrderedDict
import redis.asyncio as redis
import pickle
import zlib
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """缓存配置"""
    # 内存缓存配置
    memory_cache_size: int = 1000
    memory_ttl: int = 300  # 5分钟
    
    # Redis缓存配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl: int = 3600  # 1小时
    
    # 压缩配置
    enable_compression: bool = True
    compression_threshold: int = 1024  # 1KB
    
    # 预热配置
    enable_prewarming: bool = True
    prewarming_batch_size: int = 100


class LRUCache:
    """LRU内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            self.miss_count += 1
            return None
        
        # 检查TTL
        if time.time() - self.timestamps[key] > self.ttl:
            self._remove(key)
            self.miss_count += 1
            return None
        
        # 移动到末尾（最近使用）
        self.cache.move_to_end(key)
        self.hit_count += 1
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # 移除最久未使用的项
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def _remove(self, key: str) -> None:
        """移除缓存项"""
        if key in self.cache:
            del self.cache[key]
            del self.timestamps[key]
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
        self.hit_count = 0
        self.miss_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'memory_usage': sum(len(str(v)) for v in self.cache.values())
        }


class SmartCacheManager:
    """智能缓存管理器"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        
        # 内存缓存
        self.memory_cache = LRUCache(
            max_size=config.memory_cache_size,
            ttl=config.memory_ttl
        )
        
        # Redis连接
        self.redis_client = None
        self.redis_connected = False
        
        # 缓存键前缀
        self.key_prefix = "xiaoai:cache:"
        
        # 线程池用于异步操作
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 缓存统计
        self.stats = {
            'memory_hits': 0,
            'memory_misses': 0,
            'redis_hits': 0,
            'redis_misses': 0,
            'total_sets': 0,
            'compression_saves': 0
        }
        
        # 预热任务
        self.prewarming_tasks = []
        
        logger.info("智能缓存管理器初始化完成")
    
    async def initialize(self):
        """初始化缓存管理器"""
        try:
            # 连接Redis
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                decode_responses=False  # 保持二进制数据
            )
            
            # 测试连接
            await self.redis_client.ping()
            self.redis_connected = True
            logger.info("Redis连接成功")
            
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}，将仅使用内存缓存")
            self.redis_connected = False
    
    def _generate_cache_key(self, namespace: str, key: str) -> str:
        """生成缓存键"""
        # 使用MD5哈希来处理长键
        if len(key) > 200:
            key = hashlib.md5(key.encode()).hexdigest()
        return f"{self.key_prefix}{namespace}:{key}"
    
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        if not self.config.enable_compression or len(data) < self.config.compression_threshold:
            return data
        
        compressed = zlib.compress(data)
        if len(compressed) < len(data):
            self.stats['compression_saves'] += len(data) - len(compressed)
            return b'compressed:' + compressed
        return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """解压数据"""
        if data.startswith(b'compressed:'):
            return zlib.decompress(data[11:])
        return data
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """获取缓存值（多级缓存）"""
        cache_key = self._generate_cache_key(namespace, key)
        
        # 1. 尝试内存缓存
        value = self.memory_cache.get(cache_key)
        if value is not None:
            self.stats['memory_hits'] += 1
            logger.debug(f"内存缓存命中: {cache_key}")
            return value
        
        self.stats['memory_misses'] += 1
        
        # 2. 尝试Redis缓存
        if self.redis_connected:
            try:
                redis_value = await self.redis_client.get(cache_key)
                if redis_value is not None:
                    # 解压和反序列化
                    decompressed = self._decompress_data(redis_value)
                    value = pickle.loads(decompressed)
                    
                    # 回写到内存缓存
                    self.memory_cache.set(cache_key, value)
                    
                    self.stats['redis_hits'] += 1
                    logger.debug(f"Redis缓存命中: {cache_key}")
                    return value
                
                self.stats['redis_misses'] += 1
                
            except Exception as e:
                logger.error(f"Redis获取失败: {e}")
        
        return None
    
    async def set(self, namespace: str, key: str, value: Any, 
                  ttl: Optional[int] = None) -> None:
        """设置缓存值（多级缓存）"""
        cache_key = self._generate_cache_key(namespace, key)
        
        # 设置内存缓存
        self.memory_cache.set(cache_key, value)
        
        # 设置Redis缓存
        if self.redis_connected:
            try:
                # 序列化和压缩
                serialized = pickle.dumps(value)
                compressed = self._compress_data(serialized)
                
                # 设置TTL
                cache_ttl = ttl or self.config.redis_ttl
                
                await self.redis_client.setex(cache_key, cache_ttl, compressed)
                logger.debug(f"Redis缓存设置: {cache_key}")
                
            except Exception as e:
                logger.error(f"Redis设置失败: {e}")
        
        self.stats['total_sets'] += 1
    
    async def delete(self, namespace: str, key: str) -> None:
        """删除缓存值"""
        cache_key = self._generate_cache_key(namespace, key)
        
        # 删除内存缓存
        self.memory_cache._remove(cache_key)
        
        # 删除Redis缓存
        if self.redis_connected:
            try:
                await self.redis_client.delete(cache_key)
                logger.debug(f"缓存删除: {cache_key}")
            except Exception as e:
                logger.error(f"Redis删除失败: {e}")
    
    async def clear_namespace(self, namespace: str) -> None:
        """清空指定命名空间的缓存"""
        pattern = f"{self.key_prefix}{namespace}:*"
        
        # 清空内存缓存中匹配的键
        keys_to_remove = [k for k in self.memory_cache.cache.keys() 
                         if k.startswith(f"{self.key_prefix}{namespace}:")]
        for key in keys_to_remove:
            self.memory_cache._remove(key)
        
        # 清空Redis缓存
        if self.redis_connected:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                logger.info(f"清空命名空间 {namespace} 的缓存，共 {len(keys)} 个键")
            except Exception as e:
                logger.error(f"Redis清空失败: {e}")
    
    async def get_or_set(self, namespace: str, key: str, 
                        factory: Callable, ttl: Optional[int] = None) -> Any:
        """获取缓存值，如果不存在则通过工厂函数生成"""
        value = await self.get(namespace, key)
        if value is not None:
            return value
        
        # 生成新值
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()
        
        # 设置缓存
        await self.set(namespace, key, value, ttl)
        return value
    
    async def batch_get(self, namespace: str, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值"""
        results = {}
        
        # 批量获取内存缓存
        memory_results = {}
        redis_keys = []
        
        for key in keys:
            cache_key = self._generate_cache_key(namespace, key)
            value = self.memory_cache.get(cache_key)
            if value is not None:
                memory_results[key] = value
                self.stats['memory_hits'] += 1
            else:
                redis_keys.append((key, cache_key))
                self.stats['memory_misses'] += 1
        
        results.update(memory_results)
        
        # 批量获取Redis缓存
        if self.redis_connected and redis_keys:
            try:
                cache_keys = [cache_key for _, cache_key in redis_keys]
                redis_values = await self.redis_client.mget(cache_keys)
                
                for (original_key, cache_key), redis_value in zip(redis_keys, redis_values):
                    if redis_value is not None:
                        # 解压和反序列化
                        decompressed = self._decompress_data(redis_value)
                        value = pickle.loads(decompressed)
                        
                        results[original_key] = value
                        # 回写到内存缓存
                        self.memory_cache.set(cache_key, value)
                        self.stats['redis_hits'] += 1
                    else:
                        self.stats['redis_misses'] += 1
                        
            except Exception as e:
                logger.error(f"Redis批量获取失败: {e}")
        
        return results
    
    async def batch_set(self, namespace: str, items: Dict[str, Any], 
                       ttl: Optional[int] = None) -> None:
        """批量设置缓存值"""
        # 批量设置内存缓存
        for key, value in items.items():
            cache_key = self._generate_cache_key(namespace, key)
            self.memory_cache.set(cache_key, value)
        
        # 批量设置Redis缓存
        if self.redis_connected:
            try:
                pipe = self.redis_client.pipeline()
                cache_ttl = ttl or self.config.redis_ttl
                
                for key, value in items.items():
                    cache_key = self._generate_cache_key(namespace, key)
                    serialized = pickle.dumps(value)
                    compressed = self._compress_data(serialized)
                    pipe.setex(cache_key, cache_ttl, compressed)
                
                await pipe.execute()
                logger.debug(f"Redis批量设置完成，共 {len(items)} 个键")
                
            except Exception as e:
                logger.error(f"Redis批量设置失败: {e}")
        
        self.stats['total_sets'] += len(items)
    
    async def prewarm_cache(self, namespace: str, 
                           data_loader: Callable[[int, int], List[Tuple[str, Any]]]):
        """缓存预热"""
        if not self.config.enable_prewarming:
            return
        
        logger.info(f"开始预热缓存命名空间: {namespace}")
        
        try:
            offset = 0
            batch_size = self.config.prewarming_batch_size
            
            while True:
                # 获取数据批次
                if asyncio.iscoroutinefunction(data_loader):
                    batch_data = await data_loader(offset, batch_size)
                else:
                    batch_data = data_loader(offset, batch_size)
                
                if not batch_data:
                    break
                
                # 批量设置缓存
                items = {key: value for key, value in batch_data}
                await self.batch_set(namespace, items)
                
                offset += batch_size
                logger.debug(f"预热进度: {offset} 个项目")
            
            logger.info(f"缓存预热完成: {namespace}")
            
        except Exception as e:
            logger.error(f"缓存预热失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        memory_stats = self.memory_cache.get_stats()
        
        total_hits = self.stats['memory_hits'] + self.stats['redis_hits']
        total_misses = self.stats['memory_misses'] + self.stats['redis_misses']
        total_requests = total_hits + total_misses
        
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            'memory_cache': memory_stats,
            'redis_connected': self.redis_connected,
            'overall_stats': {
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_rate': overall_hit_rate,
                'total_sets': self.stats['total_sets'],
                'compression_saves': self.stats['compression_saves']
            },
            'detailed_stats': self.stats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            'memory_cache': True,
            'redis_cache': False,
            'overall': False
        }
        
        try:
            # 检查内存缓存
            test_key = "health_check_memory"
            self.memory_cache.set(test_key, "test")
            if self.memory_cache.get(test_key) == "test":
                health['memory_cache'] = True
                self.memory_cache._remove(test_key)
            
            # 检查Redis缓存
            if self.redis_connected:
                test_key = f"{self.key_prefix}health_check"
                await self.redis_client.setex(test_key, 10, b"test")
                if await self.redis_client.get(test_key) == b"test":
                    health['redis_cache'] = True
                    await self.redis_client.delete(test_key)
            
            health['overall'] = health['memory_cache'] and (
                health['redis_cache'] or not self.redis_connected
            )
            
        except Exception as e:
            logger.error(f"缓存健康检查失败: {e}")
        
        return health
    
    async def close(self):
        """关闭缓存管理器"""
        if self.redis_client:
            await self.redis_client.close()
        
        self.executor.shutdown(wait=True)
        logger.info("缓存管理器已关闭")


# 全局缓存管理器实例
_cache_manager = None

async def get_cache_manager(config: Optional[CacheConfig] = None) -> SmartCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    
    if _cache_manager is None:
        if config is None:
            config = CacheConfig()
        
        _cache_manager = SmartCacheManager(config)
        await _cache_manager.initialize()
    
    return _cache_manager


# 缓存装饰器
def cached(namespace: str, ttl: Optional[int] = None, 
          key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            cache_manager = await get_cache_manager()
            
            # 尝试从缓存获取
            result = await cache_manager.get(namespace, cache_key)
            if result is not None:
                return result
            
            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # 设置缓存
            await cache_manager.set(namespace, cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator 