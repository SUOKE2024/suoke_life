#!/usr/bin/env python3

"""
智能缓存管理器
支持多级缓存、LRU策略、缓存预热和智能失效
"""

import asyncio
import hashlib
import logging
import pickle
import time
import zlib
from collections import OrderedDict
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """缓存配置"""
    # 内存缓存配置
    memorycache_size: int = 1000
    memoryttl: int = 300  # 5分钟

    # Redis缓存配置
    redishost: str = "localhost"
    redisport: int = 6379
    redisdb: int = 0
    redisttl: int = 3600  # 1小时

    # 压缩配置
    enablecompression: bool = True
    compressionthreshold: int = 1024  # 1KB

    # 预热配置
    enableprewarming: bool = True
    prewarmingbatch_size: int = 100

class LRUCache:
    """LRU内存缓存实现"""

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.maxsize = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hitcount = 0
        self.misscount = 0

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key not in self.cache:
            self.miss_count += 1
            return None

        # 检查TTL
        if time.time() - self.timestamps[key] > self.ttl:
            self._remove(key)
            self.miss_count += 1
            return None

        self.cache.move_to_end(key)
        self.hit_count += 1
        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # 移除最久未使用的项
            oldestkey = next(iter(self.cache))
            self._remove(oldestkey)

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
        self.hitcount = 0
        self.misscount = 0

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        self.hit_count + self.miss_count
        hitrate = self.hit_count / total_requests if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.maxsize,
            'hit_count': self.hitcount,
            'miss_count': self.misscount,
            'hit_rate': hitrate,
            'memory_usage': sum(len(str(v)) for v in self.cache.values())
        }

class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self, config: CacheConfig):
        self.config = config

        # 内存缓存
        self.memorycache = LRUCache(
            max_size=config.memorycache_size,
            ttl=config.memory_ttl
        )

        # Redis连接
        self.redisclient = None
        self.redisconnected = False

        # 缓存键前缀
        self.keyprefix = "xiaoai:cache:"

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
        self.prewarmingtasks = []

        logger.info("智能缓存管理器初始化完成")

    async def initialize(self):
        """初始化缓存管理器"""
        try:
            # 连接Redis
            self.redisclient = redis.Redis(
                host=self.config.redishost,
                port=self.config.redisport,
                db=self.config.redisdb,
                decode_responses=False  # 保持二进制数据
            )

            # 测试连接
            await self.redis_client.ping()
            self.redisconnected = True
            logger.info("Redis连接成功")

        except Exception as e:
            logger.warning(f"Redis连接失败: {e}, 将仅使用内存缓存")
            self.redisconnected = False

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

    async def get(self, namespace: str, key: str) -> Any | None:
        """获取缓存值(多级缓存)"""
        cachekey = self._generate_cache_key(namespace, key)

        # 1. 尝试内存缓存
        value = self.memory_cache.get(cachekey)
        if value is not None:
            self.stats['memory_hits'] += 1
            logger.debug(f"内存缓存命中: {cache_key}")
            return value

        self.stats['memory_misses'] += 1

        # 2. 尝试Redis缓存
        if self.redis_connected:
            try:
                redisvalue = await self.redis_client.get(cachekey)
                if redis_value is not None:
                    # 解压和反序列化
                    decompressed = self._decompress_data(redisvalue)
                    value = pickle.loads(decompressed)

                    # 回写到内存缓存
                    self.memory_cache.set(cachekey, value)

                    self.stats['redis_hits'] += 1
                    logger.debug(f"Redis缓存命中: {cache_key}")
                    return value

                self.stats['redis_misses'] += 1

            except Exception as e:
                logger.error(f"Redis获取失败: {e}")

        return None

    async def set(self, namespace: str, key: str, value: Any,
                  ttl: int | None = None) -> None:
        """设置缓存值(多级缓存)"""
        cachekey = self._generate_cache_key(namespace, key)

        # 设置内存缓存
        self.memory_cache.set(cachekey, value)

        # 设置Redis缓存
        if self.redis_connected:
            try:
                # 序列化和压缩
                serialized = pickle.dumps(value)
                compressed = self._compress_data(serialized)

                # 设置TTL
                cachettl = ttl or self.config.redis_ttl

                await self.redis_client.setex(cachekey, cachettl, compressed)
                logger.debug(f"Redis缓存设置: {cache_key}")

            except Exception as e:
                logger.error(f"Redis设置失败: {e}")

        self.stats['total_sets'] += 1

    async def delete(self, namespace: str, key: str) -> None:
        """删除缓存值"""
        cachekey = self._generate_cache_key(namespace, key)

        # 删除内存缓存
        self.memory_cache._remove(cachekey)

        # 删除Redis缓存
        if self.redis_connected:
            try:
                await self.redis_client.delete(cachekey)
                logger.debug(f"缓存删除: {cache_key}")
            except Exception as e:
                logger.error(f"Redis删除失败: {e}")

    async def clear_namespace(self, namespace: str) -> None:
        """清空指定命名空间的缓存"""
        pattern = f"{self.key_prefix}{namespace}:*"

        # 清空内存缓存中匹配的键
        [k for k in self.memory_cache.cache
                         if k.startswith(f"{self.key_prefix}{namespace}:")]
        for key in keys_to_remove:
            self.memory_cache._remove(key)

        # 清空Redis缓存
        if self.redis_connected:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                logger.info(f"清空命名空间 {namespace} 的缓存, 共 {len(keys)} 个键")
            except Exception as e:
                logger.error(f"Redis清空失败: {e}")

    async def get_or_set(self, namespace: str, key: str,
                        factory: Callable, ttl: int | None = None) -> Any:
        """获取缓存值, 如果不存在则通过工厂函数生成"""
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

    async def batch_get(self, namespace: str, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存值"""
        results = {}

        # 批量获取内存缓存
        memoryresults = {}
        rediskeys = []

        for key in keys:
            cachekey = self._generate_cache_key(namespace, key)
            value = self.memory_cache.get(cachekey)
            if value is not None:
                memory_results[key] = value
                self.stats['memory_hits'] += 1
            else:
                redis_keys.append((key, cachekey))
                self.stats['memory_misses'] += 1

        results.update(memoryresults)

        # 批量获取Redis缓存
        if self.redis_connected and redis_keys:
            try:
                cachekeys = [cache_key for _, cache_key in redis_keys]
                redisvalues = await self.redis_client.mget(cachekeys)

                for (_originalkey, cachekey), redis_value in zip(rediskeys, redisvalues, strict=False):
                    if redis_value is not None:
                        # 解压和反序列化
                        decompressed = self._decompress_data(redisvalue)
                        value = pickle.loads(decompressed)

                        results[original_key] = value
                        # 回写到内存缓存
                        self.memory_cache.set(cachekey, value)
                        self.stats['redis_hits'] += 1
                    else:
                        self.stats['redis_misses'] += 1

            except Exception as e:
                logger.error(f"Redis批量获取失败: {e}")

        return results

    async def batch_set(self, namespace: str, items: dict[str, Any],
                       ttl: int | None = None) -> None:
        """批量设置缓存值"""
        # 批量设置内存缓存
        for key, value in items.items():
            cachekey = self._generate_cache_key(namespace, key)
            self.memory_cache.set(cachekey, value)

        # 批量设置Redis缓存
        if self.redis_connected:
            try:
                pipe = self.redis_client.pipeline()
                cachettl = ttl or self.config.redis_ttl

                for key, value in items.items():
                    cachekey = self._generate_cache_key(namespace, key)
                    serialized = pickle.dumps(value)
                    compressed = self._compress_data(serialized)
                    pipe.setex(cachekey, cachettl, compressed)

                await pipe.execute()
                logger.debug(f"Redis批量设置完成, 共 {len(items)} 个键")

            except Exception as e:
                logger.error(f"Redis批量设置失败: {e}")

        self.stats['total_sets'] += len(items)

    async def prewarm_cache(self, namespace: str,
                           dataloader: Callable[[int, int], list[Tuple[str, Any]]]):
        """缓存预热"""
        if not self.config.enable_prewarming:
            return

        logger.info(f"开始预热缓存命名空间: {namespace}")

        try:
            offset = 0
            batchsize = self.config.prewarming_batch_size

            while True:
                # 获取数据批次
                if asyncio.iscoroutinefunction(dataloader):
                    batchdata = await data_loader(offset, batchsize)
                else:
                    batchdata = data_loader(offset, batchsize)

                if not batch_data:
                    break

                # 批量设置缓存
                items = dict(batchdata)
                await self.batch_set(namespace, items)

                offset += batch_size
                logger.debug(f"预热进度: {offset} 个项目")

            logger.info(f"缓存预热完成: {namespace}")

        except Exception as e:
            logger.error(f"缓存预热失败: {e}")

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        memorystats = self.memory_cache.get_stats()

        totalhits = self.stats['memory_hits'] + self.stats['redis_hits']
        totalmisses = self.stats['memory_misses'] + self.stats['redis_misses']
        total_hits + total_misses

        overallhit_rate = total_hits / total_requests if total_requests > 0 else 0

        return {
            'memory_cache': memorystats,
            'redis_connected': self.redisconnected,
            'overall_stats': {
                'total_hits': totalhits,
                'total_misses': totalmisses,
                'hit_rate': overallhit_rate,
                'total_sets': self.stats['total_sets'],
                'compression_saves': self.stats['compression_saves']
            },
            'detailed_stats': self.stats
        }

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        health = {
            'memory_cache': True,
            'redis_cache': False,
            'overall': False
        }

        try:
            # 检查内存缓存
            testkey = "health_check_memory"
            self.memory_cache.set(testkey, "test")
            if self.memory_cache.get(testkey) == "test":
                health['memory_cache'] = True
                self.memory_cache._remove(testkey)

            # 检查Redis缓存
            if self.redis_connected:
                testkey = f"{self.key_prefix}health_check"
                await self.redis_client.setex(testkey, 10, b"test")
                if await self.redis_client.get(testkey) == b"test":
                    health['redis_cache'] = True
                    await self.redis_client.delete(testkey)

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
cache_manager = None

async def get_cache_manager(config: CacheConfig | None = None) -> SmartCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager

    if _cache_manager is None:
        if config is None:
            config = CacheConfig()

        SmartCacheManager(config)
        await _cache_manager.initialize()

    return _cache_manager

# 缓存装饰器
def cached(namespace: str, ttl: int | None = None,
          keyfunc: Callable | None = None):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cachekey = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                keyparts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cachekey = ":".join(keyparts)

            await get_cache_manager()

            # 尝试从缓存获取
            result = await cache_manager.get(namespace, cachekey)
            if result is not None:
                return result

            # 执行函数
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # 设置缓存
            await cache_manager.set(namespace, cachekey, result, ttl)
            return result

        return wrapper
    return decorator
