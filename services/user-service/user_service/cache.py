"""用户服务缓存层"""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import aioredis
import structlog

from user_service.config import get_settings

logger = structlog.get_logger()


class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._redis: Optional[aioredis.Redis] = None
        self._pool: Optional[aioredis.ConnectionPool] = None
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            self._pool = aioredis.ConnectionPool.from_url(
                self.settings.redis.url,
                max_connections=self.settings.redis.max_connections,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self._redis = aioredis.Redis(connection_pool=self._pool)
            
            # 测试连接
            await self._redis.ping()
            logger.info("Cache connected successfully", url=self.settings.redis.url)
            
        except Exception as e:
            logger.error("Failed to connect to cache", error=str(e))
            raise
    
    async def disconnect(self) -> None:
        """断开连接"""
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Cache disconnected")
    
    @property
    def redis(self) -> aioredis.Redis:
        """获取Redis客户端"""
        if not self._redis:
            raise RuntimeError("Cache not connected")
        return self._redis
    
    async def get(self, key: str) -> Optional[bytes]:
        """获取原始值"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(
        self,
        key: str,
        value: Union[str, bytes],
        ex: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置原始值"""
        try:
            return await self.redis.set(key, value, ex=ex)
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error("Cache delete failed", keys=keys, error=str(e))
            return 0
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error("Cache exists failed", key=key, error=str(e))
            return False
    
    async def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """设置过期时间"""
        try:
            return await self.redis.expire(key, time)
        except Exception as e:
            logger.error("Cache expire failed", key=key, error=str(e))
            return False
    
    async def ttl(self, key: str) -> int:
        """获取剩余生存时间"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error("Cache ttl failed", key=key, error=str(e))
            return -1


class UserCache:
    """用户缓存服务"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.settings = get_settings()
    
    def _get_user_key(self, user_id: str) -> str:
        """获取用户缓存键"""
        return f"user:{user_id}"
    
    def _get_profile_key(self, user_id: str) -> str:
        """获取用户档案缓存键"""
        return f"user_profile:{user_id}"
    
    def _get_devices_key(self, user_id: str) -> str:
        """获取用户设备缓存键"""
        return f"user_devices:{user_id}"
    
    def _get_health_data_key(self, user_id: str, date: str = None) -> str:
        """获取健康数据缓存键"""
        if date:
            return f"health_data:{user_id}:{date}"
        return f"health_data:{user_id}"
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """获取用户缓存"""
        try:
            key = self._get_user_key(user_id)
            data = await self.cache.get(key)
            if data:
                return json.loads(data.decode())
            return None
        except Exception as e:
            logger.error("Failed to get user from cache", user_id=user_id, error=str(e))
            return None
    
    async def set_user(
        self,
        user_id: str,
        user_data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户缓存"""
        try:
            key = self._get_user_key(user_id)
            json_data = json.dumps(user_data, ensure_ascii=False, default=str)
            ex = ttl or self.settings.cache.user_cache_ttl
            return await self.cache.set(key, json_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set user cache", user_id=user_id, error=str(e))
            return False
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户缓存"""
        try:
            key = self._get_user_key(user_id)
            return bool(await self.cache.delete(key))
        except Exception as e:
            logger.error("Failed to delete user cache", user_id=user_id, error=str(e))
            return False
    
    async def get_profile(self, user_id: str) -> Optional[Dict]:
        """获取用户档案缓存"""
        try:
            key = self._get_profile_key(user_id)
            data = await self.cache.get(key)
            if data:
                return json.loads(data.decode())
            return None
        except Exception as e:
            logger.error("Failed to get profile from cache", user_id=user_id, error=str(e))
            return None
    
    async def set_profile(
        self,
        user_id: str,
        profile_data: Dict,
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户档案缓存"""
        try:
            key = self._get_profile_key(user_id)
            json_data = json.dumps(profile_data, ensure_ascii=False, default=str)
            ex = ttl or self.settings.cache.profile_cache_ttl
            return await self.cache.set(key, json_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set profile cache", user_id=user_id, error=str(e))
            return False
    
    async def delete_profile(self, user_id: str) -> bool:
        """删除用户档案缓存"""
        try:
            key = self._get_profile_key(user_id)
            return bool(await self.cache.delete(key))
        except Exception as e:
            logger.error("Failed to delete profile cache", user_id=user_id, error=str(e))
            return False
    
    async def get_devices(self, user_id: str) -> Optional[List[Dict]]:
        """获取用户设备缓存"""
        try:
            key = self._get_devices_key(user_id)
            data = await self.cache.get(key)
            if data:
                return json.loads(data.decode())
            return None
        except Exception as e:
            logger.error("Failed to get devices from cache", user_id=user_id, error=str(e))
            return None
    
    async def set_devices(
        self,
        user_id: str,
        devices_data: List[Dict],
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户设备缓存"""
        try:
            key = self._get_devices_key(user_id)
            json_data = json.dumps(devices_data, ensure_ascii=False, default=str)
            ex = ttl or self.settings.cache.device_cache_ttl
            return await self.cache.set(key, json_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set devices cache", user_id=user_id, error=str(e))
            return False
    
    async def delete_devices(self, user_id: str) -> bool:
        """删除用户设备缓存"""
        try:
            key = self._get_devices_key(user_id)
            return bool(await self.cache.delete(key))
        except Exception as e:
            logger.error("Failed to delete devices cache", user_id=user_id, error=str(e))
            return False
    
    async def get_health_data(self, user_id: str, date: str = None) -> Optional[Dict]:
        """获取健康数据缓存"""
        try:
            key = self._get_health_data_key(user_id, date)
            data = await self.cache.get(key)
            if data:
                return json.loads(data.decode())
            return None
        except Exception as e:
            logger.error("Failed to get health data from cache", user_id=user_id, error=str(e))
            return None
    
    async def set_health_data(
        self,
        user_id: str,
        health_data: Dict,
        date: str = None,
        ttl: Optional[int] = None
    ) -> bool:
        """设置健康数据缓存"""
        try:
            key = self._get_health_data_key(user_id, date)
            json_data = json.dumps(health_data, ensure_ascii=False, default=str)
            ex = ttl or self.settings.cache.default_ttl
            return await self.cache.set(key, json_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set health data cache", user_id=user_id, error=str(e))
            return False
    
    async def delete_health_data(self, user_id: str, date: str = None) -> bool:
        """删除健康数据缓存"""
        try:
            key = self._get_health_data_key(user_id, date)
            return bool(await self.cache.delete(key))
        except Exception as e:
            logger.error("Failed to delete health data cache", user_id=user_id, error=str(e))
            return False
    
    async def invalidate_user_cache(self, user_id: str) -> bool:
        """清除用户相关的所有缓存"""
        try:
            keys = [
                self._get_user_key(user_id),
                self._get_profile_key(user_id),
                self._get_devices_key(user_id),
                self._get_health_data_key(user_id)
            ]
            
            # 删除所有相关键
            deleted = await self.cache.delete(*keys)
            
            # 删除健康数据的日期相关缓存（使用模式匹配）
            try:
                pattern = f"health_data:{user_id}:*"
                async for key in self.cache.redis.scan_iter(match=pattern):
                    await self.cache.delete(key.decode())
            except Exception as e:
                logger.warning("Failed to delete health data pattern cache", error=str(e))
            
            logger.info("User cache invalidated", user_id=user_id, deleted_keys=deleted)
            return True
            
        except Exception as e:
            logger.error("Failed to invalidate user cache", user_id=user_id, error=str(e))
            return False


class QueryCache:
    """查询结果缓存"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.settings = get_settings()
    
    def _get_query_key(self, query_type: str, params: Dict) -> str:
        """生成查询缓存键"""
        # 将参数排序并序列化，确保相同查询生成相同键
        sorted_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
        import hashlib
        param_hash = hashlib.md5(sorted_params.encode()).hexdigest()
        return f"query:{query_type}:{param_hash}"
    
    async def get_query_result(self, query_type: str, params: Dict) -> Optional[Any]:
        """获取查询结果缓存"""
        try:
            key = self._get_query_key(query_type, params)
            data = await self.cache.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error("Failed to get query cache", query_type=query_type, error=str(e))
            return None
    
    async def set_query_result(
        self,
        query_type: str,
        params: Dict,
        result: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置查询结果缓存"""
        try:
            key = self._get_query_key(query_type, params)
            pickled_data = pickle.dumps(result)
            ex = ttl or self.settings.cache.default_ttl
            return await self.cache.set(key, pickled_data, ex=ex)
        except Exception as e:
            logger.error("Failed to set query cache", query_type=query_type, error=str(e))
            return False
    
    async def invalidate_query_cache(self, query_type: str) -> bool:
        """清除特定类型的查询缓存"""
        try:
            pattern = f"query:{query_type}:*"
            deleted_count = 0
            async for key in self.cache.redis.scan_iter(match=pattern):
                await self.cache.delete(key.decode())
                deleted_count += 1
            
            logger.info("Query cache invalidated", query_type=query_type, deleted_count=deleted_count)
            return True
        except Exception as e:
            logger.error("Failed to invalidate query cache", query_type=query_type, error=str(e))
            return False


# 全局缓存实例
_cache_manager: Optional[CacheManager] = None
_user_cache: Optional[UserCache] = None
_query_cache: Optional[QueryCache] = None


async def init_cache() -> None:
    """初始化缓存"""
    global _cache_manager, _user_cache, _query_cache
    
    settings = get_settings()
    if not settings.cache.enabled:
        logger.info("Cache disabled")
        return
    
    _cache_manager = CacheManager()
    await _cache_manager.connect()
    
    _user_cache = UserCache(_cache_manager)
    _query_cache = QueryCache(_cache_manager)
    
    logger.info("Cache initialized successfully")


async def close_cache() -> None:
    """关闭缓存连接"""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.disconnect()


def get_cache_manager() -> Optional[CacheManager]:
    """获取缓存管理器"""
    return _cache_manager


def get_user_cache() -> Optional[UserCache]:
    """获取用户缓存"""
    return _user_cache


def get_query_cache() -> Optional[QueryCache]:
    """获取查询缓存"""
    return _query_cache


def cache_enabled() -> bool:
    """检查缓存是否启用"""
    settings = get_settings()
    return settings.cache.enabled and _cache_manager is not None 