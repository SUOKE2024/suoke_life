"""
Redis缓存管理器

提供高效的Redis缓存功能，支持用户会话、权限数据和查询结果缓存。
"""
import json
import pickle
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis
from internal.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    errors: int = 0
    total_operations: int = 0
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total_reads = self.hits + self.misses
        return (self.hits / total_reads * 100) if total_reads > 0 else 0.0


class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
        self._stats = CacheStats()
        self._is_connected = False
        self._lock = asyncio.Lock()
        
        # 缓存键前缀
        self.KEY_PREFIXES = {
            "user_session": "session:user:",
            "user_profile": "profile:user:",
            "user_permissions": "perms:user:",
            "role_permissions": "perms:role:",
            "query_cache": "query:",
            "rate_limit": "rate_limit:",
            "mfa_code": "mfa:",
            "password_reset": "pwd_reset:",
            "email_verify": "email_verify:",
            "login_attempts": "login_attempts:"
        }
        
        # 默认过期时间（秒）
        self.DEFAULT_TTL = {
            "user_session": 1800,  # 30分钟
            "user_profile": 3600,  # 1小时
            "user_permissions": 1800,  # 30分钟
            "role_permissions": 3600,  # 1小时
            "query_cache": 300,  # 5分钟
            "mfa_code": 300,  # 5分钟
            "password_reset": 3600,  # 1小时
            "email_verify": 86400,  # 24小时
            "login_attempts": 900  # 15分钟
        }
    
    async def connect(self) -> None:
        """连接Redis"""
        if self._is_connected:
            return
        
        async with self._lock:
            if self._is_connected:
                return
            
            try:
                # 构建Redis连接
                if settings.redis_url:
                    self._redis = redis.from_url(
                        settings.redis_url,
                        max_connections=settings.redis_max_connections,
                        socket_timeout=settings.redis_socket_timeout,
                        socket_connect_timeout=settings.redis_socket_connect_timeout,
                        decode_responses=False  # 保持二进制数据
                    )
                else:
                    self._redis = redis.Redis(
                        host=settings.redis_host,
                        port=settings.redis_port,
                        db=settings.redis_db,
                        password=settings.redis_password,
                        max_connections=settings.redis_max_connections,
                        socket_timeout=settings.redis_socket_timeout,
                        socket_connect_timeout=settings.redis_socket_connect_timeout,
                        decode_responses=False
                    )
                
                # 测试连接
                await self._redis.ping()
                self._is_connected = True
                
                logger.info("Redis缓存连接成功")
                
            except Exception as e:
                logger.error(f"Redis连接失败: {str(e)}")
                self._redis = None
                raise
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._is_connected = False
            logger.info("Redis缓存连接已关闭")
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        deserializer: Optional[Callable] = None
    ) -> Any:
        """获取缓存值"""
        if not self._is_connected:
            await self.connect()
        
        try:
            value = await self._redis.get(key)
            self._stats.total_operations += 1
            
            if value is None:
                self._stats.misses += 1
                logger.debug(f"缓存未命中: {key}")
                return default
            
            self._stats.hits += 1
            logger.debug(f"缓存命中: {key}")
            
            # 反序列化
            if deserializer:
                return deserializer(value)
            else:
                try:
                    # 尝试JSON反序列化
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # 回退到pickle
                    return pickle.loads(value)
                    
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"获取缓存失败 {key}: {str(e)}")
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        serializer: Optional[Callable] = None
    ) -> bool:
        """设置缓存值"""
        if not self._is_connected:
            await self.connect()
        
        try:
            # 序列化
            if serializer:
                serialized_value = serializer(value)
            else:
                try:
                    # 尝试JSON序列化
                    serialized_value = json.dumps(value, ensure_ascii=False).encode('utf-8')
                except (TypeError, ValueError):
                    # 回退到pickle
                    serialized_value = pickle.dumps(value)
            
            # 设置缓存
            if ttl:
                await self._redis.setex(key, ttl, serialized_value)
            else:
                await self._redis.set(key, serialized_value)
            
            self._stats.sets += 1
            self._stats.total_operations += 1
            logger.debug(f"缓存设置成功: {key}, TTL: {ttl}")
            return True
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"设置缓存失败 {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self._is_connected:
            await self.connect()
        
        try:
            result = await self._redis.delete(key)
            self._stats.deletes += 1
            self._stats.total_operations += 1
            logger.debug(f"缓存删除: {key}, 结果: {result}")
            return result > 0
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"删除缓存失败 {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        if not self._is_connected:
            await self.connect()
        
        try:
            result = await self._redis.exists(key)
            self._stats.total_operations += 1
            return result > 0
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"检查缓存存在性失败 {key}: {str(e)}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        if not self._is_connected:
            await self.connect()
        
        try:
            result = await self._redis.expire(key, ttl)
            self._stats.total_operations += 1
            return result
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"设置缓存过期时间失败 {key}: {str(e)}")
            return False
    
    async def get_ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        if not self._is_connected:
            await self.connect()
        
        try:
            ttl = await self._redis.ttl(key)
            self._stats.total_operations += 1
            return ttl
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"获取缓存TTL失败 {key}: {str(e)}")
            return -1
    
    async def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        if not self._is_connected:
            await self.connect()
        
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                deleted = await self._redis.delete(*keys)
                self._stats.deletes += deleted
                self._stats.total_operations += 1
                logger.info(f"清除缓存模式 {pattern}: {deleted} 个键")
                return deleted
            return 0
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"清除缓存模式失败 {pattern}: {str(e)}")
            return 0
    
    # 业务相关的缓存方法
    
    async def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话"""
        key = f"{self.KEY_PREFIXES['user_session']}{user_id}"
        return await self.get(key)
    
    async def set_user_session(
        self, 
        user_id: str, 
        session_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户会话"""
        key = f"{self.KEY_PREFIXES['user_session']}{user_id}"
        ttl = ttl or self.DEFAULT_TTL['user_session']
        return await self.set(key, session_data, ttl)
    
    async def delete_user_session(self, user_id: str) -> bool:
        """删除用户会话"""
        key = f"{self.KEY_PREFIXES['user_session']}{user_id}"
        return await self.delete(key)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户资料缓存"""
        key = f"{self.KEY_PREFIXES['user_profile']}{user_id}"
        return await self.get(key)
    
    async def set_user_profile(
        self, 
        user_id: str, 
        profile_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户资料缓存"""
        key = f"{self.KEY_PREFIXES['user_profile']}{user_id}"
        ttl = ttl or self.DEFAULT_TTL['user_profile']
        return await self.set(key, profile_data, ttl)
    
    async def delete_user_profile(self, user_id: str) -> bool:
        """删除用户资料缓存"""
        key = f"{self.KEY_PREFIXES['user_profile']}{user_id}"
        return await self.delete(key)
    
    async def get_user_permissions(self, user_id: str) -> Optional[List[str]]:
        """获取用户权限缓存"""
        key = f"{self.KEY_PREFIXES['user_permissions']}{user_id}"
        return await self.get(key)
    
    async def set_user_permissions(
        self, 
        user_id: str, 
        permissions: List[str],
        ttl: Optional[int] = None
    ) -> bool:
        """设置用户权限缓存"""
        key = f"{self.KEY_PREFIXES['user_permissions']}{user_id}"
        ttl = ttl or self.DEFAULT_TTL['user_permissions']
        return await self.set(key, permissions, ttl)
    
    async def delete_user_permissions(self, user_id: str) -> bool:
        """删除用户权限缓存"""
        key = f"{self.KEY_PREFIXES['user_permissions']}{user_id}"
        return await self.delete(key)
    
    async def get_query_cache(self, query_hash: str) -> Optional[Any]:
        """获取查询结果缓存"""
        key = f"{self.KEY_PREFIXES['query_cache']}{query_hash}"
        return await self.get(key)
    
    async def set_query_cache(
        self, 
        query_hash: str, 
        result: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置查询结果缓存"""
        key = f"{self.KEY_PREFIXES['query_cache']}{query_hash}"
        ttl = ttl or self.DEFAULT_TTL['query_cache']
        return await self.set(key, result, ttl)
    
    async def increment_login_attempts(self, identifier: str) -> int:
        """增加登录尝试次数"""
        key = f"{self.KEY_PREFIXES['login_attempts']}{identifier}"
        
        try:
            if not self._is_connected:
                await self.connect()
            
            # 使用管道操作保证原子性
            pipe = self._redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.DEFAULT_TTL['login_attempts'])
            results = await pipe.execute()
            
            attempts = results[0]
            self._stats.total_operations += 2
            
            logger.debug(f"登录尝试次数: {identifier} = {attempts}")
            return attempts
            
        except Exception as e:
            self._stats.errors += 1
            logger.error(f"增加登录尝试次数失败 {identifier}: {str(e)}")
            return 1
    
    async def get_login_attempts(self, identifier: str) -> int:
        """获取登录尝试次数"""
        key = f"{self.KEY_PREFIXES['login_attempts']}{identifier}"
        attempts = await self.get(key, default=0)
        return int(attempts) if attempts else 0
    
    async def clear_login_attempts(self, identifier: str) -> bool:
        """清除登录尝试次数"""
        key = f"{self.KEY_PREFIXES['login_attempts']}{identifier}"
        return await self.delete(key)
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            if not self._is_connected:
                await self.connect()
            
            start_time = asyncio.get_event_loop().time()
            await self._redis.ping()
            response_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            # 获取Redis信息
            info = await self._redis.info()
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "hit_rate": round(self._stats.hit_rate, 2),
                "total_operations": self._stats.total_operations,
                "errors": self._stats.errors
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "hit_rate": round(self._stats.hit_rate, 2),
                "total_operations": self._stats.total_operations,
                "errors": self._stats.errors
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "sets": self._stats.sets,
            "deletes": self._stats.deletes,
            "errors": self._stats.errors,
            "total_operations": self._stats.total_operations,
            "hit_rate": round(self._stats.hit_rate, 2),
            "is_connected": self._is_connected
        }
    
    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = CacheStats()
        logger.info("缓存统计信息已重置")


# 全局缓存实例
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    """获取Redis缓存实例"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache


async def init_cache() -> None:
    """初始化缓存"""
    cache = get_redis_cache()
    await cache.connect()


async def close_cache() -> None:
    """关闭缓存"""
    global _redis_cache
    if _redis_cache:
        await _redis_cache.disconnect()
        _redis_cache = None


# 缓存装饰器
def cache_result(
    key_prefix: str, 
    ttl: int = 300,
    key_func: Optional[Callable] = None
):
    """缓存结果装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = get_redis_cache()
            
            # 生成缓存键
            if key_func:
                cache_key = f"{key_prefix}:{key_func(*args, **kwargs)}"
            else:
                # 使用函数参数生成键
                key_parts = [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
                cache_key = f"{key_prefix}:{':'.join(key_parts)}"
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator 