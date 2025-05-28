"""Redis管理器"""

import json
from typing import Any, Optional, Union

import aioredis
import structlog

from auth_service.config.settings import RedisSettings

logger = structlog.get_logger(__name__)


class RedisManager:
    """Redis管理器"""
    
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self._redis: Optional[aioredis.Redis] = None
    
    async def initialize(self) -> None:
        """初始化Redis连接"""
        try:
            self._redis = aioredis.from_url(
                self.settings.url,
                max_connections=self.settings.max_connections,
                retry_on_timeout=True,
                health_check_interval=30,
                decode_responses=True,
            )
            
            # 测试连接
            await self._test_connection()
            
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error("Redis连接初始化失败", error=str(e))
            raise
    
    async def _test_connection(self) -> None:
        """测试Redis连接"""
        try:
            await self._redis.ping()
            logger.info("Redis连接测试成功")
        except Exception as e:
            logger.error("Redis连接测试失败", error=str(e))
            raise
    
    async def close(self) -> None:
        """关闭Redis连接"""
        if self._redis:
            await self._redis.close()
            logger.info("Redis连接已关闭")
    
    async def get(self, key: str) -> Optional[str]:
        """获取值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error("Redis GET操作失败", key=key, error=str(e))
            raise
    
    async def set(
        self,
        key: str,
        value: Union[str, int, float, dict, list],
        expire: Optional[int] = None
    ) -> bool:
        """设置值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            # 如果值是字典或列表，序列化为JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self._redis.set(key, value, ex=expire)
            return result
        except Exception as e:
            logger.error("Redis SET操作失败", key=key, error=str(e))
            raise
    
    async def delete(self, *keys: str) -> int:
        """删除键"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.delete(*keys)
        except Exception as e:
            logger.error("Redis DELETE操作失败", keys=keys, error=str(e))
            raise
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.error("Redis EXISTS操作失败", key=key, error=str(e))
            raise
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.expire(key, seconds)
        except Exception as e:
            logger.error("Redis EXPIRE操作失败", key=key, error=str(e))
            raise
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.ttl(key)
        except Exception as e:
            logger.error("Redis TTL操作失败", key=key, error=str(e))
            raise
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.incrby(key, amount)
        except Exception as e:
            logger.error("Redis INCR操作失败", key=key, error=str(e))
            raise
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.decrby(key, amount)
        except Exception as e:
            logger.error("Redis DECR操作失败", key=key, error=str(e))
            raise
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希字段值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.hget(name, key)
        except Exception as e:
            logger.error("Redis HGET操作失败", name=name, key=key, error=str(e))
            raise
    
    async def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希字段值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return await self._redis.hset(name, key, value)
        except Exception as e:
            logger.error("Redis HSET操作失败", name=name, key=key, error=str(e))
            raise
    
    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.hdel(name, *keys)
        except Exception as e:
            logger.error("Redis HDEL操作失败", name=name, keys=keys, error=str(e))
            raise
    
    async def hgetall(self, name: str) -> dict:
        """获取哈希所有字段"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.hgetall(name)
        except Exception as e:
            logger.error("Redis HGETALL操作失败", name=name, error=str(e))
            raise
    
    async def sadd(self, name: str, *values: Any) -> int:
        """添加集合成员"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.sadd(name, *values)
        except Exception as e:
            logger.error("Redis SADD操作失败", name=name, error=str(e))
            raise
    
    async def srem(self, name: str, *values: Any) -> int:
        """删除集合成员"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.srem(name, *values)
        except Exception as e:
            logger.error("Redis SREM操作失败", name=name, error=str(e))
            raise
    
    async def sismember(self, name: str, value: Any) -> bool:
        """检查是否为集合成员"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.sismember(name, value)
        except Exception as e:
            logger.error("Redis SISMEMBER操作失败", name=name, error=str(e))
            raise
    
    async def smembers(self, name: str) -> set:
        """获取集合所有成员"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            return await self._redis.smembers(name)
        except Exception as e:
            logger.error("Redis SMEMBERS操作失败", name=name, error=str(e))
            raise
    
    @property
    def redis(self) -> aioredis.Redis:
        """获取Redis客户端"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        return self._redis


# 全局Redis管理器实例
_redis_manager: Optional[RedisManager] = None


def get_redis_manager() -> RedisManager:
    """获取Redis管理器实例"""
    global _redis_manager
    if _redis_manager is None:
        raise RuntimeError("Redis管理器未初始化")
    return _redis_manager


def set_redis_manager(manager: RedisManager) -> None:
    """设置Redis管理器实例"""
    global _redis_manager
    _redis_manager = manager 