#!/usr/bin/env python3
"""
缓存管理模块

提供Redis缓存操作、分布式锁、会话管理等功能。
"""

import asyncio
import json
import pickle
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

try:
    import redis.asyncio as aioredis
except ImportError:
    import aioredis
from loguru import logger

from .config import get_settings

settings = get_settings()


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.settings = settings
        self._redis: Optional[aioredis.Redis] = None
        self._connection_pool: Optional[aioredis.ConnectionPool] = None

    async def initialize(self):
        """初始化Redis连接"""
        try:
            # 创建连接池
            self._connection_pool = aioredis.ConnectionPool.from_url(
                self.settings.redis.url,
                max_connections=self.settings.redis.max_connections,
                retry_on_timeout=self.settings.redis.retry_on_timeout,
                decode_responses=True,
                encoding="utf-8"
            )
            
            # 创建Redis客户端
            self._redis = aioredis.Redis(connection_pool=self._connection_pool)
            
            # 测试连接
            await self._redis.ping()
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise

    async def close(self):
        """关闭Redis连接"""
        if self._redis:
            await self._redis.close()
        if self._connection_pool:
            await self._connection_pool.disconnect()
        logger.info("Redis连接已关闭")

    @property
    def redis(self) -> aioredis.Redis:
        """获取Redis客户端"""
        if not self._redis:
            raise RuntimeError("Redis未初始化，请先调用initialize()")
        return self._redis

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """设置缓存值"""
        try:
            # 序列化值
            if serialize:
                if isinstance(value, (dict, list)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = value

            # 设置缓存
            result = await self.redis.set(key, serialized_value, ex=expire)
            return bool(result)

        except Exception as e:
            logger.error(f"设置缓存失败 key={key}: {e}")
            return False

    async def get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True
    ) -> Any:
        """获取缓存值"""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default

            # 反序列化值
            if deserialize:
                try:
                    # 尝试JSON反序列化
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    try:
                        # 尝试pickle反序列化
                        return pickle.loads(value)
                    except (pickle.PickleError, TypeError):
                        # 返回原始值
                        return value
            else:
                return value

        except Exception as e:
            logger.error(f"获取缓存失败 key={key}: {e}")
            return default

    async def delete(self, *keys: str) -> int:
        """删除缓存键"""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"删除缓存失败 keys={keys}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"检查缓存存在性失败 key={key}: {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        try:
            return bool(await self.redis.expire(key, seconds))
        except Exception as e:
            logger.error(f"设置缓存过期时间失败 key={key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"获取缓存TTL失败 key={key}: {e}")
            return -1

    async def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的所有键"""
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"获取缓存键列表失败 pattern={pattern}: {e}")
            return []

    async def flushdb(self) -> bool:
        """清空当前数据库"""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"清空缓存数据库失败: {e}")
            return False

    # 哈希操作
    async def hset(self, name: str, mapping: Dict[str, Any]) -> int:
        """设置哈希字段"""
        try:
            # 序列化值
            serialized_mapping = {}
            for key, value in mapping.items():
                if isinstance(value, (dict, list)):
                    serialized_mapping[key] = json.dumps(value, ensure_ascii=False)
                else:
                    serialized_mapping[key] = str(value)
            
            return await self.redis.hset(name, mapping=serialized_mapping)
        except Exception as e:
            logger.error(f"设置哈希缓存失败 name={name}: {e}")
            return 0

    async def hget(self, name: str, key: str, default: Any = None) -> Any:
        """获取哈希字段值"""
        try:
            value = await self.redis.hget(name, key)
            if value is None:
                return default
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"获取哈希缓存失败 name={name} key={key}: {e}")
            return default

    async def hgetall(self, name: str) -> Dict[str, Any]:
        """获取哈希所有字段"""
        try:
            data = await self.redis.hgetall(name)
            result = {}
            for key, value in data.items():
                try:
                    result[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[key] = value
            return result
        except Exception as e:
            logger.error(f"获取哈希所有字段失败 name={name}: {e}")
            return {}

    async def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        try:
            return await self.redis.hdel(name, *keys)
        except Exception as e:
            logger.error(f"删除哈希字段失败 name={name} keys={keys}: {e}")
            return 0

    # 列表操作
    async def lpush(self, name: str, *values: Any) -> int:
        """从左侧推入列表"""
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return await self.redis.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"列表左推失败 name={name}: {e}")
            return 0

    async def rpush(self, name: str, *values: Any) -> int:
        """从右侧推入列表"""
        try:
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return await self.redis.rpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"列表右推失败 name={name}: {e}")
            return 0

    async def lpop(self, name: str) -> Any:
        """从左侧弹出列表元素"""
        try:
            value = await self.redis.lpop(name)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"列表左弹失败 name={name}: {e}")
            return None

    async def rpop(self, name: str) -> Any:
        """从右侧弹出列表元素"""
        try:
            value = await self.redis.rpop(name)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"列表右弹失败 name={name}: {e}")
            return None

    async def lrange(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """获取列表范围元素"""
        try:
            values = await self.redis.lrange(name, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(value)
            return result
        except Exception as e:
            logger.error(f"获取列表范围失败 name={name}: {e}")
            return []

    async def llen(self, name: str) -> int:
        """获取列表长度"""
        try:
            return await self.redis.llen(name)
        except Exception as e:
            logger.error(f"获取列表长度失败 name={name}: {e}")
            return 0


class DistributedLock:
    """分布式锁"""

    def __init__(self, cache_manager: CacheManager, key: str, timeout: int = 30):
        self.cache_manager = cache_manager
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.identifier = f"{time.time()}:{id(self)}"

    async def acquire(self) -> bool:
        """获取锁"""
        try:
            # 使用SET NX EX原子操作获取锁
            result = await self.cache_manager.redis.set(
                self.key,
                self.identifier,
                nx=True,
                ex=self.timeout
            )
            return bool(result)
        except Exception as e:
            logger.error(f"获取分布式锁失败 key={self.key}: {e}")
            return False

    async def release(self) -> bool:
        """释放锁"""
        try:
            # 使用Lua脚本确保原子性释放
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            result = await self.cache_manager.redis.eval(
                lua_script,
                1,
                self.key,
                self.identifier
            )
            return bool(result)
        except Exception as e:
            logger.error(f"释放分布式锁失败 key={self.key}: {e}")
            return False

    async def extend(self, additional_time: int) -> bool:
        """延长锁时间"""
        try:
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """
            result = await self.cache_manager.redis.eval(
                lua_script,
                1,
                self.key,
                self.identifier,
                additional_time
            )
            return bool(result)
        except Exception as e:
            logger.error(f"延长分布式锁失败 key={self.key}: {e}")
            return False

    @asynccontextmanager
    async def __aenter__(self):
        """异步上下文管理器入口"""
        acquired = await self.acquire()
        if not acquired:
            raise RuntimeError(f"无法获取分布式锁: {self.key}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.release()


class CacheDecorator:
    """缓存装饰器"""

    def __init__(
        self,
        cache_manager: CacheManager,
        key_prefix: str = "",
        expire: int = 3600,
        serialize: bool = True
    ):
        self.cache_manager = cache_manager
        self.key_prefix = key_prefix
        self.expire = expire
        self.serialize = serialize

    def __call__(self, func: Callable) -> Callable:
        """装饰器调用"""
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = self._generate_cache_key(func.__name__, args, kwargs)
            
            # 尝试从缓存获取
            cached_result = await self.cache_manager.get(
                cache_key,
                deserialize=self.serialize
            )
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存储到缓存
            await self.cache_manager.set(
                cache_key,
                result,
                expire=self.expire,
                serialize=self.serialize
            )
            logger.debug(f"缓存存储: {cache_key}")
            
            return result
        
        return wrapper

    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        key_parts = [self.key_prefix, func_name] if self.key_prefix else [func_name]
        
        # 添加参数到键中
        if args:
            key_parts.extend(str(arg) for arg in args)
        if kwargs:
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        
        return ":".join(key_parts)


# 全局缓存管理器实例
cache_manager = CacheManager()


async def get_cache_manager() -> CacheManager:
    """获取缓存管理器"""
    if not cache_manager._redis:
        await cache_manager.initialize()
    return cache_manager


def cached(
    key_prefix: str = "",
    expire: int = 3600,
    serialize: bool = True
) -> Callable:
    """缓存装饰器工厂"""
    def decorator(func: Callable) -> Callable:
        return CacheDecorator(
            cache_manager,
            key_prefix=key_prefix,
            expire=expire,
            serialize=serialize
        )(func)
    return decorator


async def distributed_lock(key: str, timeout: int = 30) -> DistributedLock:
    """创建分布式锁"""
    return DistributedLock(cache_manager, key, timeout) 