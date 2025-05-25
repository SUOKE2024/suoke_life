#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存服务模块
提供Redis和内存缓存的统一接口
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import asyncio
from functools import wraps

import aioredis
from cachetools import TTLCache, LRUCache
from loguru import logger
import orjson


class CacheService:
    """统一缓存服务"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化缓存服务
        
        Args:
            config: 缓存配置
        """
        self.config = config
        self.redis_client: Optional[aioredis.Redis] = None
        self.memory_cache: Optional[Union[TTLCache, LRUCache]] = None
        self.is_initialized = False
        
        # 缓存策略配置
        self.strategies = config.get('strategies', {})
        self.default_ttl = config.get('ttl', 3600)
        
    async def initialize(self) -> None:
        """初始化缓存服务"""
        if self.is_initialized:
            return
            
        # 初始化Redis缓存
        if self.config.get('enabled', False) and self.config.get('type') == 'redis':
            await self._init_redis()
        
        # 初始化内存缓存
        memory_config = self.config.get('memory_cache', {})
        if memory_config.get('enabled', False):
            await self._init_memory_cache(memory_config)
        
        self.is_initialized = True
        logger.info("缓存服务初始化完成")
    
    async def _init_redis(self) -> None:
        """初始化Redis连接"""
        try:
            redis_url = self.config.get('url', 'redis://localhost:6379/0')
            max_connections = self.config.get('max_connections', 10)
            
            self.redis_client = aioredis.from_url(
                redis_url,
                max_connections=max_connections,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis缓存连接成功")
            
        except Exception as e:
            logger.error(f"Redis缓存连接失败: {e}")
            self.redis_client = None
    
    async def _init_memory_cache(self, config: Dict[str, Any]) -> None:
        """初始化内存缓存"""
        max_size = config.get('max_size', 1000)
        ttl = config.get('ttl', 300)
        
        self.memory_cache = TTLCache(maxsize=max_size, ttl=ttl)
        logger.info(f"内存缓存初始化完成，最大容量: {max_size}, TTL: {ttl}秒")
    
    def _generate_key(self, key: str, prefix: str = "") -> str:
        """生成缓存键"""
        if prefix:
            key = f"{prefix}:{key}"
        return key
    
    def _serialize_value(self, value: Any) -> bytes:
        """序列化值"""
        try:
            # 优先使用orjson进行JSON序列化
            if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
                return orjson.dumps(value)
            else:
                # 复杂对象使用pickle
                return pickle.dumps(value)
        except Exception as e:
            logger.warning(f"序列化失败，使用pickle: {e}")
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """反序列化值"""
        try:
            # 尝试JSON反序列化
            return orjson.loads(data)
        except (orjson.JSONDecodeError, ValueError):
            try:
                # 尝试pickle反序列化
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"反序列化失败: {e}")
                return None
    
    async def get(self, key: str, prefix: str = "") -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            prefix: 键前缀
            
        Returns:
            缓存值或None
        """
        cache_key = self._generate_key(key, prefix)
        
        # 先尝试内存缓存
        if self.memory_cache is not None:
            try:
                value = self.memory_cache.get(cache_key)
                if value is not None:
                    return value
            except Exception as e:
                logger.warning(f"内存缓存获取失败: {e}")
        
        # 再尝试Redis缓存
        if self.redis_client is not None:
            try:
                data = await self.redis_client.get(cache_key)
                if data is not None:
                    value = self._deserialize_value(data)
                    # 回写到内存缓存
                    if self.memory_cache is not None:
                        self.memory_cache[cache_key] = value
                    return value
            except Exception as e:
                logger.warning(f"Redis缓存获取失败: {e}")
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None, 
        prefix: str = ""
    ) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            prefix: 键前缀
            
        Returns:
            是否设置成功
        """
        cache_key = self._generate_key(key, prefix)
        ttl = ttl or self.default_ttl
        
        success = False
        
        # 设置内存缓存
        if self.memory_cache is not None:
            try:
                self.memory_cache[cache_key] = value
                success = True
            except Exception as e:
                logger.warning(f"内存缓存设置失败: {e}")
        
        # 设置Redis缓存
        if self.redis_client is not None:
            try:
                data = self._serialize_value(value)
                await self.redis_client.setex(cache_key, ttl, data)
                success = True
            except Exception as e:
                logger.warning(f"Redis缓存设置失败: {e}")
        
        return success
    
    async def delete(self, key: str, prefix: str = "") -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            prefix: 键前缀
            
        Returns:
            是否删除成功
        """
        cache_key = self._generate_key(key, prefix)
        
        success = False
        
        # 删除内存缓存
        if self.memory_cache is not None:
            try:
                self.memory_cache.pop(cache_key, None)
                success = True
            except Exception as e:
                logger.warning(f"内存缓存删除失败: {e}")
        
        # 删除Redis缓存
        if self.redis_client is not None:
            try:
                await self.redis_client.delete(cache_key)
                success = True
            except Exception as e:
                logger.warning(f"Redis缓存删除失败: {e}")
        
        return success
    
    async def exists(self, key: str, prefix: str = "") -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            prefix: 键前缀
            
        Returns:
            是否存在
        """
        cache_key = self._generate_key(key, prefix)
        
        # 检查内存缓存
        if self.memory_cache is not None:
            if cache_key in self.memory_cache:
                return True
        
        # 检查Redis缓存
        if self.redis_client is not None:
            try:
                return bool(await self.redis_client.exists(cache_key))
            except Exception as e:
                logger.warning(f"Redis缓存检查失败: {e}")
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存
        
        Args:
            pattern: 匹配模式
            
        Returns:
            清除的键数量
        """
        count = 0
        
        # 清除Redis缓存
        if self.redis_client is not None:
            try:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    count = await self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis缓存模式清除失败: {e}")
        
        # 清除内存缓存（简单实现）
        if self.memory_cache is not None:
            try:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    self.memory_cache.pop(key, None)
                    count += 1
            except Exception as e:
                logger.warning(f"内存缓存模式清除失败: {e}")
        
        return count
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = {
            "redis_connected": self.redis_client is not None,
            "memory_cache_enabled": self.memory_cache is not None,
            "memory_cache_size": 0,
            "memory_cache_maxsize": 0
        }
        
        if self.memory_cache is not None:
            stats["memory_cache_size"] = len(self.memory_cache)
            stats["memory_cache_maxsize"] = self.memory_cache.maxsize
        
        if self.redis_client is not None:
            try:
                info = await self.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed")
                }
            except Exception as e:
                logger.warning(f"获取Redis统计信息失败: {e}")
        
        return stats
    
    async def close(self) -> None:
        """关闭缓存连接"""
        if self.redis_client is not None:
            await self.redis_client.close()
            logger.info("Redis连接已关闭")
        
        if self.memory_cache is not None:
            self.memory_cache.clear()
            logger.info("内存缓存已清空")


def cache_result(
    ttl: int = 3600,
    prefix: str = "",
    key_func: Optional[callable] = None
):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存时间（秒）
        prefix: 缓存键前缀
        key_func: 自定义键生成函数
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成逻辑
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # 尝试从缓存获取
            cache_service = getattr(func, '_cache_service', None)
            if cache_service:
                cached_result = await cache_service.get(cache_key, prefix)
                if cached_result is not None:
                    return cached_result
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if cache_service and result is not None:
                await cache_service.set(cache_key, result, ttl, prefix)
            
            return result
        
        return wrapper
    return decorator


# 全局缓存服务实例
_cache_service: Optional[CacheService] = None


async def get_cache_service() -> Optional[CacheService]:
    """获取全局缓存服务实例"""
    return _cache_service


async def init_cache_service(config: Dict[str, Any]) -> CacheService:
    """初始化全局缓存服务"""
    global _cache_service
    _cache_service = CacheService(config)
    await _cache_service.initialize()
    return _cache_service


async def close_cache_service() -> None:
    """关闭全局缓存服务"""
    global _cache_service
    if _cache_service:
        await _cache_service.close()
        _cache_service = None 