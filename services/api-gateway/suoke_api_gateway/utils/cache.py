"""
cache - 索克生活项目模块
"""

from ..core.config import Settings
from ..core.logging import get_logger
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union
import json

"""
缓存管理器

基于 Redis 的分布式缓存实现。
"""




logger = get_logger(__name__)

class CacheItem(BaseModel):
    """缓存项模型"""
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0

class CacheStats(BaseModel):
    """缓存统计信息"""
    total_keys: int
    hit_count: int
    miss_count: int
    hit_rate: float
    memory_usage: int
    expired_keys: int

class CacheManager:
    """缓存管理器"""

    def __init__(self, settings: Settings):
"""TODO: 添加文档字符串"""
self.settings = settings
self.redis_client: Optional[redis.Redis] = None
self.enabled = True
self.default_ttl = 3600  # 1小时
self.key_prefix = "suoke:gateway:"

# 统计信息
self.hit_count = 0
self.miss_count = 0

    async def initialize(self) -> None:
"""初始化缓存管理器"""
try:
            self.redis_client = redis.from_url(
                self.settings.get_redis_url(),
                decode_responses = True,
            )
            # 测试连接
            await self.redis_client.ping()
            logger.info("Cache manager initialized")
except Exception as e:
            logger.error("Failed to initialize cache manager", error = str(e))
            self.enabled = False
            raise

    async def cleanup(self) -> None:
"""清理资源"""
if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
"""获取缓存值"""
if not self.enabled or not self.redis_client:
            return None

try:
            full_key = self._get_full_key(key)
            value = await self.redis_client.get(full_key)

            if value is not None:
                self.hit_count += 1
                # 尝试解析JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                self.miss_count += 1
                return None

except Exception as e:
            logger.error("Cache get failed", key = key, error = str(e))
            self.miss_count += 1
            return None

    async def set(
self,
key: str,
value: Any,
ttl: Optional[int] = None
    ) -> bool:
"""设置缓存值"""
if not self.enabled or not self.redis_client:
            return False

try:
            full_key = self._get_full_key(key)

            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = str(value)

            # 设置TTL
            expire_time = ttl or self.default_ttl

            await self.redis_client.setex(full_key, expire_time, serialized_value)
            return True

except Exception as e:
            logger.error("Cache set failed", key = key, error = str(e))
            return False

    async def delete(self, key: str) -> bool:
"""删除缓存值"""
if not self.enabled or not self.redis_client:
            return False

try:
            full_key = self._get_full_key(key)
            result = await self.redis_client.delete(full_key)
            return result > 0

except Exception as e:
            logger.error("Cache delete failed", key = key, error = str(e))
            return False

    async def exists(self, key: str) -> bool:
"""检查缓存键是否存在"""
if not self.enabled or not self.redis_client:
            return False

try:
            full_key = self._get_full_key(key)
            result = await self.redis_client.exists(full_key)
            return result > 0

except Exception as e:
            logger.error("Cache exists check failed", key = key, error = str(e))
            return False

    async def get_or_set(
self,
key: str,
factory_func,
ttl: Optional[int] = None,
* args,
**kwargs
    ) -> Any:
"""获取缓存值，如果不存在则调用工厂函数设置"""
# 先尝试获取
value = await self.get(key)
if value is not None:
            return value

# 调用工厂函数
try:
            if callable(factory_func):
                if hasattr(factory_func, '__call__') and hasattr(factory_func, '__await__'):
                    # 异步函数
                    value = await factory_func( * args, **kwargs)
                else:
                    # 同步函数
                    value = factory_func( * args, **kwargs)
            else:
                value = factory_func

            # 设置缓存
            await self.set(key, value, ttl)
            return value

except Exception as e:
            logger.error("Factory function failed", key = key, error = str(e))
            return None

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
"""递增计数器"""
if not self.enabled or not self.redis_client:
            return None

try:
            full_key = self._get_full_key(key)
            result = await self.redis_client.incrby(full_key, amount)
            return result

except Exception as e:
            logger.error("Cache increment failed", key = key, error = str(e))
            return None

    async def expire(self, key: str, ttl: int) -> bool:
"""设置键的过期时间"""
if not self.enabled or not self.redis_client:
            return False

try:
            full_key = self._get_full_key(key)
            result = await self.redis_client.expire(full_key, ttl)
            return result

except Exception as e:
            logger.error("Cache expire failed", key = key, error = str(e))
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
"""获取键的剩余生存时间"""
if not self.enabled or not self.redis_client:
            return None

try:
            full_key = self._get_full_key(key)
            ttl = await self.redis_client.ttl(full_key)
            return ttl if ttl > 0 else None

except Exception as e:
            logger.error("Cache TTL check failed", key = key, error = str(e))
            return None

    async def clear_pattern(self, pattern: str) -> int:
"""清除匹配模式的所有键"""
if not self.enabled or not self.redis_client:
            return 0

try:
            full_pattern = self._get_full_key(pattern)
            keys = await self.redis_client.keys(full_pattern)

            if keys:
                result = await self.redis_client.delete( * keys)
                return result

            return 0

except Exception as e:
            logger.error("Cache clear pattern failed", pattern = pattern, error = str(e))
            return 0

    async def get_stats(self) -> CacheStats:
"""获取缓存统计信息"""
try:
            if not self.enabled or not self.redis_client:
                return CacheStats(
                    total_keys = 0,
                    hit_count = self.hit_count,
                    miss_count = self.miss_count,
                    hit_rate = 0.0,
                    memory_usage = 0,
                    expired_keys = 0,
                )

            # 获取Redis信息
            info = await self.redis_client.info()

            # 计算命中率
            total_requests = self.hit_count + self.miss_count
            hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0.0

            # 获取键数量
            pattern = self._get_full_key(" * ")
            keys = await self.redis_client.keys(pattern)

            return CacheStats(
                total_keys = len(keys),
                hit_count = self.hit_count,
                miss_count = self.miss_count,
                hit_rate = hit_rate,
                memory_usage = info.get("used_memory", 0),
                expired_keys = info.get("expired_keys", 0),
            )

except Exception as e:
            logger.error("Failed to get cache stats", error = str(e))
            return CacheStats(
                total_keys = 0,
                hit_count = self.hit_count,
                miss_count = self.miss_count,
                hit_rate = 0.0,
                memory_usage = 0,
                expired_keys = 0,
            )

    def _get_full_key(self, key: str) -> str:
"""获取完整的缓存键"""
return f"{self.key_prefix}{key}"
