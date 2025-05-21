#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
老克智能体服务 - 缓存管理器
提供多级缓存支持：本地内存缓存和Redis分布式缓存
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Union, List, Set, Tuple
import asyncio
from functools import wraps

from cachetools import TTLCache
import aioredis

from pkg.utils.config import Config

logger = logging.getLogger(__name__)

class CacheManager:
    """缓存管理器，支持内存缓存和Redis缓存"""
    
    def __init__(self, config: Config):
        """初始化缓存管理器"""
        self.config = config
        self.cache_config = config.get_section('cache')
        
        # 初始化内存缓存
        self.memory_cache_size = self.cache_config.get('memory_cache_size', 10000)
        self.memory_cache_ttl = self.cache_config.get('memory_cache_ttl', 60)  # 60秒
        self.memory_cache = TTLCache(maxsize=self.memory_cache_size, ttl=self.memory_cache_ttl)
        
        # Redis 配置
        self.redis_enabled = self.cache_config.get('type', 'memory') == 'redis'
        self.redis_client = None
        
        # 如果启用Redis，异步初始化连接
        if self.redis_enabled:
            asyncio.create_task(self._init_redis())
        
        logger.info("缓存管理器初始化完成，内存缓存大小：%d，TTL：%d秒，Redis：%s", 
                 self.memory_cache_size, self.memory_cache_ttl, 
                 "启用" if self.redis_enabled else "禁用")
    
    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            redis_host = self.cache_config.get('host', 'localhost')
            redis_port = int(self.cache_config.get('port', 6379))
            redis_db = int(self.cache_config.get('db', 0))
            redis_password = self.cache_config.get('password', None)
            redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"
            
            self.redis_client = await aioredis.from_url(
                redis_url,
                password=redis_password
            )
            
            logger.info("Redis缓存连接成功：%s", redis_url)
        except Exception as e:
            logger.error("Redis缓存连接失败：%s", str(e))
            self.redis_enabled = False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        从缓存获取值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的值，如果不存在则返回None
        """
        # 先从内存缓存获取
        if key in self.memory_cache:
            logger.debug("内存缓存命中：%s", key)
            return self.memory_cache[key]
        
        # 如果Redis可用，从Redis获取
        if self.redis_enabled and self.redis_client:
            try:
                value = await self.redis_client.get(key)
                if value:
                    logger.debug("Redis缓存命中：%s", key)
                    # 将值解析为对象并存入内存缓存
                    deserialized = json.loads(value)
                    self.memory_cache[key] = deserialized
                    return deserialized
            except Exception as e:
                logger.error("从Redis获取缓存失败，键：%s，错误：%s", key, str(e))
        
        return None
    
    async def set(self, key: str, value: Any, expire: int = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 要缓存的值
            expire: 过期时间（秒），如果为None则使用默认TTL
            
        Returns:
            是否成功设置缓存
        """
        # 设置内存缓存
        self.memory_cache[key] = value
        
        # 如果Redis可用，也设置Redis缓存
        if self.redis_enabled and self.redis_client:
            try:
                # 序列化值
                serialized = json.dumps(value)
                
                # 设置过期时间，如果未提供则使用配置中的TTL
                if expire is None:
                    expire = int(self.cache_config.get('ttl', 3600))
                
                # 设置Redis缓存
                await self.redis_client.set(key, serialized, ex=expire)
                logger.debug("Redis缓存已设置：%s，过期时间：%d秒", key, expire)
                return True
            except Exception as e:
                logger.error("设置Redis缓存失败，键：%s，错误：%s", key, str(e))
                return False
        
        return True
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除缓存
        """
        # 删除内存缓存
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # 如果Redis可用，也删除Redis缓存
        if self.redis_enabled and self.redis_client:
            try:
                await self.redis_client.delete(key)
                logger.debug("Redis缓存已删除：%s", key)
                return True
            except Exception as e:
                logger.error("删除Redis缓存失败，键：%s，错误：%s", key, str(e))
                return False
        
        return True
    
    async def exists(self, key: str) -> bool:
        """
        检查缓存键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            缓存键是否存在
        """
        # 检查内存缓存
        if key in self.memory_cache:
            return True
        
        # 如果Redis可用，检查Redis缓存
        if self.redis_enabled and self.redis_client:
            try:
                return await self.redis_client.exists(key) > 0
            except Exception as e:
                logger.error("检查Redis缓存失败，键：%s，错误：%s", key, str(e))
        
        return False
    
    async def clear(self, pattern: str = None) -> bool:
        """
        清空缓存
        
        Args:
            pattern: 模式匹配，如果提供则只清除匹配的键
            
        Returns:
            是否成功清空缓存
        """
        # 清空内存缓存
        if pattern:
            # 清除匹配的键
            keys_to_remove = [k for k in self.memory_cache if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
        else:
            # 清空所有
            self.memory_cache.clear()
        
        # 如果Redis可用，也清空Redis缓存
        if self.redis_enabled and self.redis_client:
            try:
                if pattern:
                    # 获取匹配的键
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        await self.redis_client.delete(*keys)
                else:
                    # 清空所有（危险操作，生产环境谨慎使用）
                    await self.redis_client.flushdb()
                
                logger.debug("Redis缓存已清空：%s", pattern or "所有")
                return True
            except Exception as e:
                logger.error("清空Redis缓存失败，模式：%s，错误：%s", pattern or "所有", str(e))
                return False
        
        return True

    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        """
        从哈希表获取字段值
        
        Args:
            key: 哈希表键
            field: 字段名
            
        Returns:
            字段值，如果不存在则返回None
        """
        # 内存缓存键
        mem_key = f"{key}:{field}"
        
        # 先从内存缓存获取
        if mem_key in self.memory_cache:
            return self.memory_cache[mem_key]
        
        # 如果Redis可用，从Redis获取
        if self.redis_enabled and self.redis_client:
            try:
                value = await self.redis_client.hget(key, field)
                if value:
                    # 将值解析为对象并存入内存缓存
                    deserialized = json.loads(value)
                    self.memory_cache[mem_key] = deserialized
                    return deserialized
            except Exception as e:
                logger.error("从Redis哈希表获取缓存失败，键：%s，字段：%s，错误：%s", 
                           key, field, str(e))
        
        return None
    
    async def set_hash(self, key: str, field: str, value: Any) -> bool:
        """
        设置哈希表字段值
        
        Args:
            key: 哈希表键
            field: 字段名
            value: 要缓存的值
            
        Returns:
            是否成功设置缓存
        """
        # 内存缓存键
        mem_key = f"{key}:{field}"
        
        # 设置内存缓存
        self.memory_cache[mem_key] = value
        
        # 如果Redis可用，也设置Redis缓存
        if self.redis_enabled and self.redis_client:
            try:
                # 序列化值
                serialized = json.dumps(value)
                
                # 设置Redis哈希表字段
                await self.redis_client.hset(key, field, serialized)
                return True
            except Exception as e:
                logger.error("设置Redis哈希表缓存失败，键：%s，字段：%s，错误：%s", 
                           key, field, str(e))
                return False
        
        return True
    
    async def close(self):
        """关闭缓存管理器"""
        # 关闭Redis连接
        if self.redis_enabled and self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis缓存连接已关闭")
            except Exception as e:
                logger.error("关闭Redis缓存连接失败：%s", str(e))

def cached(ttl: int = 300):
    """
    缓存装饰器，用于缓存方法结果
    
    Args:
        ttl: 缓存过期时间（秒）
        
    Returns:
        装饰后的方法
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # 获取缓存管理器
            cache_manager = getattr(self, 'cache_manager', None)
            if not cache_manager:
                # 如果没有缓存管理器，直接调用原方法
                return await func(self, *args, **kwargs)
            
            # 构建缓存键
            # 使用函数名、参数和关键字参数生成唯一键
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = f"cache:{':'.join(key_parts)}"
            
            # 尝试从缓存获取
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 调用原方法
            result = await func(self, *args, **kwargs)
            
            # 存入缓存
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator 