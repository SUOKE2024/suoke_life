"""
Redis配置和连接管理
"""

import json
import logging
import pickle
from typing import Any, Dict, Optional

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from .settings import get_settings

logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# Redis连接池
redis_pool: Optional[ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """初始化Redis连接"""
    global redis_pool, redis_client
    
    try:
        logger.info("🔄 初始化Redis连接...")
        
        # 创建连接池
        redis_pool = ConnectionPool.from_url(
            settings.redis.url,
            max_connections=settings.redis.max_connections,
            retry_on_timeout=settings.redis.retry_on_timeout,
            socket_timeout=settings.redis.socket_timeout,
            decode_responses=True
        )
        
        # 创建Redis客户端
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # 测试连接
        await redis_client.ping()
        
        logger.info("✅ Redis连接初始化成功")
        
    except Exception as e:
        logger.error(f"❌ Redis初始化失败: {e}")
        raise


async def close_redis():
    """关闭Redis连接"""
    global redis_client, redis_pool
    
    try:
        logger.info("🔄 关闭Redis连接...")
        
        if redis_client:
            await redis_client.close()
        
        if redis_pool:
            await redis_pool.disconnect()
        
        logger.info("✅ Redis连接已关闭")
        
    except Exception as e:
        logger.error(f"❌ 关闭Redis连接失败: {e}")


def get_redis() -> redis.Redis:
    """获取Redis客户端"""
    if redis_client is None:
        raise RuntimeError("Redis客户端未初始化")
    return redis_client


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, client: redis.Redis):
        self.client = client
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # 尝试JSON解析
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # 如果JSON解析失败，尝试pickle
                try:
                    return pickle.loads(value.encode() if isinstance(value, str) else value)
                except (pickle.PickleError, TypeError):
                    # 如果都失败，返回原始值
                    return value
                    
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialize_method: str = "json"
    ) -> bool:
        """设置缓存值"""
        try:
            # 序列化值
            if serialize_method == "json":
                try:
                    serialized_value = json.dumps(value, ensure_ascii=False)
                except (TypeError, ValueError):
                    # JSON序列化失败，使用pickle
                    serialized_value = pickle.dumps(value)
            elif serialize_method == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                serialized_value = str(value)
            
            # 设置缓存
            if ttl:
                await self.client.setex(key, ttl, serialized_value)
            else:
                await self.client.set(key, serialized_value)
            
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            return await self.client.expire(key, ttl)
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"获取缓存TTL失败 {key}: {e}")
            return -1
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配的键列表"""
        try:
            return await self.client.keys(pattern)
        except Exception as e:
            logger.error(f"获取键列表失败 {pattern}: {e}")
            return []
    
    async def flush_db(self) -> bool:
        """清空当前数据库"""
        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空数据库失败: {e}")
            return False


class UserCache(RedisCache):
    """用户缓存管理器"""
    
    def __init__(self, client: redis.Redis):
        super().__init__(client)
        self.prefix = "user:"
        self.default_ttl = settings.cache.user_cache_ttl
    
    def _make_key(self, user_id: str, suffix: str = "") -> str:
        """生成用户缓存键"""
        key = f"{self.prefix}{user_id}"
        if suffix:
            key += f":{suffix}"
        return key
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户缓存"""
        key = self._make_key(user_id)
        return await self.get(key)
    
    async def set_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """设置用户缓存"""
        key = self._make_key(user_id)
        return await self.set(key, user_data, self.default_ttl)
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户缓存"""
        key = self._make_key(user_id)
        return await self.delete(key)
    
    async def get_user_sessions(self, user_id: str) -> Optional[list]:
        """获取用户会话缓存"""
        key = self._make_key(user_id, "sessions")
        return await self.get(key)
    
    async def set_user_sessions(self, user_id: str, sessions: list) -> bool:
        """设置用户会话缓存"""
        key = self._make_key(user_id, "sessions")
        return await self.set(key, sessions, settings.cache.session_cache_ttl)


class SessionCache(RedisCache):
    """会话缓存管理器"""
    
    def __init__(self, client: redis.Redis):
        super().__init__(client)
        self.prefix = "session:"
        self.default_ttl = settings.cache.session_cache_ttl
    
    def _make_key(self, session_token: str) -> str:
        """生成会话缓存键"""
        return f"{self.prefix}{session_token}"
    
    async def get_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """获取会话缓存"""
        key = self._make_key(session_token)
        return await self.get(key)
    
    async def set_session(self, session_token: str, session_data: Dict[str, Any]) -> bool:
        """设置会话缓存"""
        key = self._make_key(session_token)
        return await self.set(key, session_data, self.default_ttl)
    
    async def delete_session(self, session_token: str) -> bool:
        """删除会话缓存"""
        key = self._make_key(session_token)
        return await self.delete(key)


# 全局缓存实例
user_cache: Optional[UserCache] = None
session_cache: Optional[SessionCache] = None


def get_user_cache() -> UserCache:
    """获取用户缓存实例"""
    global user_cache
    if user_cache is None:
        redis_client = get_redis()
        user_cache = UserCache(redis_client)
    return user_cache


def get_session_cache() -> SessionCache:
    """获取会话缓存实例"""
    global session_cache
    if session_cache is None:
        redis_client = get_redis()
        session_cache = SessionCache(redis_client)
    return session_cache


# 导出
__all__ = [
    "init_redis",
    "close_redis",
    "get_redis",
    "RedisCache",
    "UserCache",
    "SessionCache",
    "get_user_cache",
    "get_session_cache"
]