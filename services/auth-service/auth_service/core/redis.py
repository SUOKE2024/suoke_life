"""
redis - 索克生活项目模块
"""

from auth_service.config.settings import RedisSettings, get_settings
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union
import json
import pickle
import redis.asyncio as redis
import structlog

"""Redis核心模块"""



logger = structlog.get_logger()


class RedisManager:
    """Redis管理器"""
    
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self._pool: Optional[redis.ConnectionPool] = None
        self._redis: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            self._pool = redis.ConnectionPool.from_url(
                self.settings.url,
                max_connections=self.settings.max_connections,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self._redis = redis.Redis(connection_pool=self._pool)
            
            # 测试连接
            await self._redis.ping()
            logger.info("Redis connected successfully", url=self.settings.url)
            
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis disconnected")
    
    @property
    def redis(self) -> redis.Redis:
        """获取Redis客户端"""
        if not self._redis:
            raise RuntimeError("Redis not connected")
        return self._redis
    
    async def get(self, key: str) -> Optional[bytes]:
        """获取值"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error("Redis get failed", key=key, error=str(e))
            return None
    
    async def set(
        self,
        key: str,
        value: Union[str, bytes],
        ex: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置值"""
        try:
            return await self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error("Redis set failed", key=key, error=str(e))
            return False
    
    async def setex(
        self,
        key: str,
        time: Union[int, timedelta],
        value: Union[str, bytes]
    ) -> bool:
        """设置值并指定过期时间"""
        try:
            return await self.redis.setex(key, time, value)
        except Exception as e:
            logger.error("Redis setex failed", key=key, error=str(e))
            return False
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error("Redis delete failed", keys=keys, error=str(e))
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error("Redis exists failed", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """设置键的过期时间"""
        try:
            return await self.redis.expire(key, time)
        except Exception as e:
            logger.error("Redis expire failed", key=key, error=str(e))
            return False
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error("Redis ttl failed", key=key, error=str(e))
            return -1
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数器"""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            logger.error("Redis incr failed", key=key, error=str(e))
            return None
    
    async def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数器"""
        try:
            return await self.redis.decr(key, amount)
        except Exception as e:
            logger.error("Redis decr failed", key=key, error=str(e))
            return None


class CacheService:
    """缓存服务"""
    
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """获取JSON数据"""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data.decode())
            return None
        except Exception as e:
            logger.error("Failed to get JSON from cache", key=key, error=str(e))
            return None
    
    async def set_json(
        self,
        key: str,
        value: Dict,
        ex: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置JSON数据"""
        try:
            json_data = json.dumps(value, ensure_ascii=False)
            return await self.redis.set(key, json_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set JSON to cache", key=key, error=str(e))
            return False
    
    async def get_object(self, key: str) -> Optional[Any]:
        """获取Python对象（使用pickle）"""
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error("Failed to get object from cache", key=key, error=str(e))
            return None
    
    async def set_object(
        self,
        key: str,
        value: Any,
        ex: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置Python对象（使用pickle）"""
        try:
            pickled_data = pickle.dumps(value)
            return await self.redis.set(key, pickled_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set object to cache", key=key, error=str(e))
            return False
    
    async def get_user_cache(self, user_id: str) -> Optional[Dict]:
        """获取用户缓存"""
        key = f"user:{user_id}"
        return await self.get_json(key)
    
    async def set_user_cache(
        self,
        user_id: str,
        user_data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户缓存"""
        key = f"user:{user_id}"
        settings = get_settings()
        ex = ttl or settings.cache.user_cache_ttl
        return await self.set_json(key, user_data, ex=ex)
    
    async def delete_user_cache(self, user_id: str) -> bool:
        """删除用户缓存"""
        key = f"user:{user_id}"
        return bool(await self.redis.delete(key))
    
    async def get_session_cache(self, session_id: str) -> Optional[Dict]:
        """获取会话缓存"""
        key = f"session:{session_id}"
        return await self.get_json(key)
    
    async def set_session_cache(
        self,
        session_id: str,
        session_data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """设置会话缓存"""
        key = f"session:{session_id}"
        settings = get_settings()
        ex = ttl or settings.cache.session_cache_ttl
        return await self.set_json(key, session_data, ex=ex)
    
    async def delete_session_cache(self, session_id: str) -> bool:
        """删除会话缓存"""
        key = f"session:{session_id}"
        return bool(await self.redis.delete(key))


# 全局Redis管理器实例
_redis_manager: Optional[RedisManager] = None
_cache_service: Optional[CacheService] = None


async def init_redis() -> None:
    """初始化Redis"""
    global _redis_manager, _cache_service
    
    settings = get_settings()
    _redis_manager = RedisManager(settings.redis)
    await _redis_manager.connect()
    
    _cache_service = CacheService(_redis_manager)


async def close_redis() -> None:
    """关闭Redis连接"""
    global _redis_manager
    if _redis_manager:
        await _redis_manager.disconnect()


def get_redis() -> RedisManager:
    """获取Redis管理器"""
    if not _redis_manager:
        raise RuntimeError("Redis not initialized")
    return _redis_manager


def get_redis_manager() -> RedisManager:
    """获取Redis管理器（别名）"""
    return get_redis()


def get_cache() -> CacheService:
    """获取缓存服务"""
    if not _cache_service:
        raise RuntimeError("Cache service not initialized")
    return _cache_service 