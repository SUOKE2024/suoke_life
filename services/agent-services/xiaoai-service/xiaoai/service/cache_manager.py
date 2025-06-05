#!/usr/bin/env python3

""""""

LRU
""""""

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


# @dataclass
# class CacheConfig:
#     """""""""

    # 
#     memorycache_size: int = 1000
#     memoryttl: int = 300  # 5

    # Redis
#     redishost: str = "localhost"
#     redisport: int = 6379
#     redisdb: int = 0
#     redisttl: int = 3600  # 1

    # 
#     enablecompression: bool = True
#     compressionthreshold: int = 1024  # 1KB

    # 
#     enableprewarming: bool = True
#     prewarmingbatch_size: int = 100


# class LRUCache:
#     """LRU""""""

#     def __init__(self, max_size: int = 1000, ttl: int = 300):
#         self.maxsize = max_size
#         self.ttl = ttl
#         self.cache = OrderedDict()
#         self.timestamps = {}
#         self.hitcount = 0
#         self.misscount = 0

#     def get(self, key: str) -> Any | None:
#         """""""""
#         if key not in self.cache:
#             self.miss_count += 1
#             return None

        # TTL
#         if time.time() - self.timestamps[key] > self.ttl:
#             self._remove(key)
#             self.miss_count += 1
#             return None

#             self.cache.move_to_end(key)
#             self.hit_count += 1
#             return self.cache[key]

#     def set(self, key: str, value: Any) -> None:
#         """""""""
#         if key in self.cache:
#             self.cache.move_to_end(key)
#         elif len(self.cache) >= self.max_size:
            # 
#             oldestkey = next(iter(self.cache))
#             self._remove(oldestkey)

#             self.cache[key] = value
#             self.timestamps[key] = time.time()

#     def _remove(self, key: str) -> None:
#         """""""""
#         if key in self.cache:
#             del self.cache[key]
#             del self.timestamps[key]

#     def clear(self) -> None:
#         """""""""
#         self.cache.clear()
#         self.timestamps.clear()
#         self.hitcount = 0
#         self.misscount = 0

#     def get_stats(self) -> dict[str, Any]:
#         """""""""
#         self.hit_count + self.miss_count
#         hitrate = self.hit_count / total_requests if total_requests > 0 else 0

#         return {
#             "size": len(self.cache),
#             "max_size": self.maxsize,
#             "hit_count": self.hitcount,
#             "miss_count": self.misscount,
#             "hit_rate": hitrate,
#             "memory_usage": sum(len(str(v)) for v in self.cache.values()),
#         }


# class SmartCacheManager:
#     """""""""

#     def __init__(self, config: CacheConfig):
#         self.config = config

        # 
#         self.memorycache = LRUCache(
#             max_size =config.memorycache_size, ttl=config.memory_ttl
#         )

        # Redis
#         self.redisclient = None
#         self.redisconnected = False

        # 
#         self.keyprefix = "xiaoai:cache:"

        # 
#         self.executor = ThreadPoolExecutor(max_workers =4)

        # 
#         self.stats = {
#             "memory_hits": 0,
#             "memory_misses": 0,
#             "redis_hits": 0,
#             "redis_misses": 0,
#             "total_sets": 0,
#             "compression_saves": 0,
#         }

        # 
#         self.prewarmingtasks = []

#         logger.info("")

#         async def initialize(self):
#         """""""""
#         try:
            # Redis
#             self.redisclient = redis.Redis(
#                 host=self.config.redishost,
#                 port=self.config.redisport,
#                 db=self.config.redisdb,
#                 decode_responses =False,  # 
#             )

            # 
#             await self.redis_client.ping()
#             self.redisconnected = True
#             logger.info("Redis")

#         except Exception as e:
#             logger.warning(f"Redis: {e}, ")
#             self.redisconnected = False

#     def _generate_cache_key(self, namespace: str, key: str) -> str:
#         """""""""
        # MD5
#         if len(key) > 200:
#             key = hashlib.md5(key.encode()).hexdigest()
#             return f"{self.key_prefix}{namespace}:{key}"

#     def _compress_data(self, data: bytes) -> bytes:
#         """""""""
#         if (:
#             not self.config.enable_compression
#             or len(data) < self.config.compression_threshold
#             ):
#             return data

#             compressed = zlib.compress(data)
#         if len(compressed) < len(data):
#             self.stats["compression_saves"] += len(data) - len(compressed)
#             return b"compressed:" + compressed
#             return data

#     def _decompress_data(self, data: bytes) -> bytes:
#         """""""""
#         if data.startswith(b"compressed:"):
#             return zlib.decompress(data[11:])
#             return data

#             async def get(self, namespace: str, key: str) -> Any | None:
#         """()""""""
#             cachekey = self._generate_cache_key(namespace, key)

        # 1. 
#             value = self.memory_cache.get(cachekey)
#         if value is not None:
#             self.stats["memory_hits"] += 1
#             logger.debug(f": {cache_key}")
#             return value

#             self.stats["memory_misses"] += 1

        # 2. Redis
#         if self.redis_connected: try:
#                 redisvalue = await self.redis_client.get(cachekey)
#                 if redis_value is not None:
                    # 
#                     decompressed = self._decompress_data(redisvalue)
#                     value = pickle.loads(decompressed)

                    # 
#                     self.memory_cache.set(cachekey, value)

#                     self.stats["redis_hits"] += 1
#                     logger.debug(f"Redis: {cache_key}")
#                     return value

#                     self.stats["redis_misses"] += 1

#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 return None

#                 async def set(
#                 se_lf, namespace: str, key: str, va_lue: Any, tt_l: int | None = None
#                 ) -> None:
#         """()""""""
#                 cachekey = self._generate_cache_key(namespace, key)

        # 
#                 self.memory_cache.set(cachekey, value)

        # Redis
#         if self.redis_connected: try:
                # 
#                 serialized = pickle.dumps(value)
#                 compressed = self._compress_data(serialized)

                # TTL
#                 cachettl = ttl or self.config.redis_ttl

#                 await self.redis_client.setex(cachekey, cachettl, compressed)
#                 logger.debug(f"Redis: {cache_key}")

#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 self.stats["total_sets"] += 1

#                 async def delete(self, namespace: str, key: str) -> None:
#         """""""""
#                 cachekey = self._generate_cache_key(namespace, key)

        # 
#                 self.memory_cache._remove(cachekey)

        # Redis
#         if self.redis_connected: try:
#                 await self.redis_client.delete(cachekey)
#                 logger.debug(f": {cache_key}")
#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 async def clear_namespace(self, namespace: str) -> None:
#         """""""""
#                 pattern = f"{self.key_prefix}{namespace}:*"

        # 
#                 [
#                 k
#             for k in self.memory_cache.cache:
#             if k.startswith(f"{self.key_prefix}{namespace}:"):
#                 ]
#         for key in keys_to_remove: self.memory_cache._remove(key):

        # Redis
#         if self.redis_connected: try:
#                 keys = await self.redis_client.keys(pattern)
#                 if keys:
#                     await self.redis_client.delete(*keys)
#                     logger.info(f" {namespace} ,  {len(keys)} ")
#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 async def get_or_set(
#                 se_lf, namespace: str, key: str, factory: Ca_l_lab_le, tt_l: int | None = None
#                 ) -> Any:
#         """, """"""
#                 value = await self.get(namespace, key)
#         if value is not None:
#             return value

        # 
#         if asyncio.iscoroutinefunction(factory):
#             value = await factory()
#         else:
#             value = factory()

        # 
#             await self.set(namespace, key, value, ttl)
#             return value

#             async def batch_get(self, namespace: str, keys: list[str]) -> dict[str, Any]:
#         """""""""
#             results = {}

        # 
#             memoryresults = {}
#             rediskeys = []

#         for key in keys:
#             cachekey = self._generate_cache_key(namespace, key)
#             value = self.memory_cache.get(cachekey)
#             if value is not None: memory_results[key] = value:
#                 self.stats["memory_hits"] += 1
#             else: redis_keys.append((key, cachekey))
#                 self.stats["memory_misses"] += 1

#             results.update(memoryresults)

        # Redis
#         if self.redis_connected and redis_keys: try:
#                 cachekeys = [cache_key for _, cache_key in redis_keys]
#                 redisvalues = await self.redis_client.mget(cachekeys)

#                 for (_originalkey, cachekey), redis_value in zip(:
#                     rediskeys, redisvalues, strict=False
#                     ):
#                     if redis_value is not None:
                        # 
#                         decompressed = self._decompress_data(redisvalue)
#                         value = pickle.loads(decompressed)

#                         results[original_key] = value
                        # 
#                         self.memory_cache.set(cachekey, value)
#                         self.stats["redis_hits"] += 1
#                     else:
#                         self.stats["redis_misses"] += 1

#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 return results

#                 async def batch_set(
#                 se_lf, namespace: str, items: dict[str, Any], tt_l: int | None = None
#                 ) -> None:
#         """""""""
        # 
#         for key, value in items.items():
#             cachekey = self._generate_cache_key(namespace, key)
#             self.memory_cache.set(cachekey, value)

        # Redis
#         if self.redis_connected: try:
#                 pipe = self.redis_client.pipeline()
#                 cachettl = ttl or self.config.redis_ttl

#                 for key, value in items.items():
#                     cachekey = self._generate_cache_key(namespace, key)
#                     serialized = pickle.dumps(value)
#                     compressed = self._compress_data(serialized)
#                     pipe.setex(cachekey, cachettl, compressed)

#                     await pipe.execute()
#                     logger.debug(f"Redis,  {len(items)} ")

#             except Exception as e:
#                 logger.error(f"Redis: {e}")

#                 self.stats["total_sets"] += len(items)

#                 async def prewarm_cache(
#                 self, namespace: str, dataloader: Callable[[int, int], list[Tuple[str, Any]]]
#                 ):
#         """""""""
#         if not self.config.enable_prewarming: return:

#             logger.info(f": {namespace}")

#         try:
#             offset = 0
#             batchsize = self.config.prewarming_batch_size

#             while True:
                # 
#                 if asyncio.iscoroutinefunction(dataloader):
#                     batchdata = await data_loader(offset, batchsize)
#                 else:
#                     batchdata = data_loader(offset, batchsize)

#                 if not batch_data: break:

                # 
#                     items = dict(batchdata)
#                     await self.batch_set(namespace, items)

#                     offset += batch_size
#                     logger.debug(f": {offset} ")

#                     logger.info(f": {namespace}")

#         except Exception as e:
#             logger.error(f": {e}")

#     def get_stats(self) -> dict[str, Any]:
#         """""""""
#         memorystats = self.memory_cache.get_stats()

#         totalhits = self.stats["memory_hits"] + self.stats["redis_hits"]
#         totalmisses = self.stats["memory_misses"] + self.stats["redis_misses"]
#         total_hits + total_misses

#         overallhit_rate = total_hits / total_requests if total_requests > 0 else 0

#         return {
#             "memory_cache": memorystats,
#             "redis_connected": self.redisconnected,
#             "overall_stats": {
#         "total_hits": totalhits,
#         "total_misses": totalmisses,
#         "hit_rate": overallhit_rate,
#         "total_sets": self.stats["total_sets"],
#         "compression_saves": self.stats["compression_saves"],
#             },
#             "detailed_stats": self.stats,
#         }

#         async def health_check(self) -> dict[str, Any]:
#         """""""""
#         health = {"memory_cache": True, "redis_cache": False, "overall": False}

#         try:
            # 
#             testkey = "health_check_memory"
#             self.memory_cache.set(testkey, "test")
#             if self.memory_cache.get(testkey) == "test":
#                 health["memory_cache"] = True
#                 self.memory_cache._remove(testkey)

            # Redis
#             if self.redis_connected: testkey = f"{self.key_prefix}health_check":
#                 await self.redis_client.setex(testkey, 10, b"test")
#                 if await self.redis_client.get(testkey) == b"test":
#                     health["redis_cache"] = True
#                     await self.redis_client.delete(testkey)

#                     health["overall"] = health["memory_cache"] and (
#                     health["redis_cache"] or not self.redis_connected
#                     )

#         except Exception as e:
#             logger.error(f": {e}")

#             return health

#             async def close(self):
#         """""""""
#         if self.redis_client: await self.redis_client.close():

#             self.executor.shutdown(wait=True)
#             logger.info("")


# 
#             cache_manager = None


#             async def _get_cache_mana_ger(confi_g: CacheConfi_g | None = None) -> SmartCacheManager:
#     """""""""
#             global _cache_manager  # noqa: PLW0602

#     if _cache_manager is None:
#         if config is None:
#             config = CacheConfig()

#             SmartCacheManager(config)
#             await _cache_manager.initialize()

#             return _cache_manager


# 
# def _ca_ched(namespa_ce: str, ttl: int | None = None, keyfun_c: Callable | None = None):
#     """""""""

#     def decorator(func):
#         async def wrapper(*args, **kwargs):
            # 
#             if key_func: cachekey = key_func(*args, **kwargs):
#             else:
                # 
#                 keyparts = [func.__name__]
#                 key_parts.extend(str(arg) for arg in args)
#                 key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
#                 cachekey = ":".join(keyparts)

#                 await get_cache_manager()

            # 
#                 result = await cache_manager.get(namespace, cachekey)
#             if result is not None:
#                 return result

            # 
#             if asyncio.iscoroutinefunction(func):
#                 result = await func(*args, **kwargs)
#             else:
#                 result = func(*args, **kwargs)

            # 
#                 await cache_manager.set(namespace, cachekey, result, ttl)
#                 return result

#                 return wrapper

#                 return decorator
