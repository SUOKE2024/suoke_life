#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的多级缓存系统
支持内存缓存、Redis缓存、智能失效策略和缓存预热
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum

from fastapi import Request, Response

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """缓存级别"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_PERSISTENT = "l3_persistent"

@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    default_ttl: int = 300  # 5分钟
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    max_memory_items: int = 10000
    redis_url: Optional[str] = None
    redis_db: int = 0
    compression_enabled: bool = True
    compression_threshold: int = 1024  # 1KB
    cache_warming_enabled: bool = True
    cache_warming_interval: int = 300  # 5分钟

@dataclass
class CacheItem:
    """缓存项"""
    key: str
    value: Any
    ttl: int
    created_at: float
    accessed_at: float
    access_count: int = 0
    size: int = 0
    compressed: bool = False

@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage: int = 0
    item_count: int = 0

class CacheBackend(ABC):
    """缓存后端抽象基类"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        pass

class MemoryCache(CacheBackend):
    """内存缓存后端"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: Dict[str, CacheItem] = {}
        self._stats = CacheStats()
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            item = self._cache.get(key)
            if not item:
                self._stats.misses += 1
                return None
            
            # 检查是否过期
            if self._is_expired(item):
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None
            
            # 更新访问信息
            item.accessed_at = time.time()
            item.access_count += 1
            self._stats.hits += 1
            
            return item.value
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存值"""
        async with self._lock:
            try:
                # 序列化值以计算大小
                serialized_value = json.dumps(value) if not isinstance(value, (str, bytes)) else value
                size = len(str(serialized_value))
                
                # 检查内存限制
                if self._should_evict(size):
                    await self._evict_items()
                
                # 创建缓存项
                item = CacheItem(
                    key=key,
                    value=value,
                    ttl=ttl or self.config.default_ttl,
                    created_at=time.time(),
                    accessed_at=time.time(),
                    size=size
                )
                
                self._cache[key] = item
                self._stats.sets += 1
                self._stats.memory_usage += size
                self._stats.item_count = len(self._cache)
                
                return True
            except Exception as e:
                logger.error(f"内存缓存设置失败: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self._lock:
            item = self._cache.pop(key, None)
            if item:
                self._stats.deletes += 1
                self._stats.memory_usage -= item.size
                self._stats.item_count = len(self._cache)
                return True
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._stats.memory_usage = 0
            self._stats.item_count = 0
            return True
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        async with self._lock:
            item = self._cache.get(key)
            if not item:
                return False
            
            if self._is_expired(item):
                del self._cache[key]
                return False
            
            return True
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self._stats
    
    def _is_expired(self, item: CacheItem) -> bool:
        """检查缓存项是否过期"""
        return time.time() - item.created_at > item.ttl
    
    def _should_evict(self, new_item_size: int) -> bool:
        """检查是否需要驱逐缓存项"""
        return (
            self._stats.memory_usage + new_item_size > self.config.max_memory_size or
            len(self._cache) >= self.config.max_memory_items
        )
    
    async def _evict_items(self):
        """驱逐缓存项（LRU策略）"""
        if not self._cache:
            return
        
        # 按访问时间排序，驱逐最久未访问的项
        items_by_access = sorted(
            self._cache.items(),
            key=lambda x: x[1].accessed_at
        )
        
        # 驱逐25%的项目
        evict_count = max(1, len(items_by_access) // 4)
        
        for i in range(evict_count):
            key, item = items_by_access[i]
            del self._cache[key]
            self._stats.memory_usage -= item.size
            self._stats.evictions += 1
        
        self._stats.item_count = len(self._cache)

class RedisCache(CacheBackend):
    """Redis缓存后端"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._redis: Optional[redis.Redis] = None
        self._stats = CacheStats()
    
    async def start(self):
        """启动Redis连接"""
        if self.config.redis_url:
            self._redis = redis.from_url(
                self.config.redis_url,
                db=self.config.redis_db,
                decode_responses=True
            )
            logger.info("Redis缓存后端已启动")
    
    async def stop(self):
        """停止Redis连接"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis缓存后端已停止")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value is None:
                self._stats.misses += 1
                return None
            
            self._stats.hits += 1
            return json.loads(value)
        except Exception as e:
            logger.error(f"Redis缓存获取失败: {e}")
            self._stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存值"""
        if not self._redis:
            return False
        
        try:
            serialized_value = json.dumps(value)
            ttl = ttl or self.config.default_ttl
            
            await self._redis.setex(key, ttl, serialized_value)
            self._stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"Redis缓存设置失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self._redis:
            return False
        
        try:
            result = await self._redis.delete(key)
            if result:
                self._stats.deletes += 1
            return bool(result)
        except Exception as e:
            logger.error(f"Redis缓存删除失败: {e}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        if not self._redis:
            return False
        
        try:
            await self._redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis缓存清空失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            return False
        
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.error(f"Redis缓存检查失败: {e}")
            return False
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        return self._stats

class MultiLevelCache:
    """
    多级缓存系统
    支持内存缓存和Redis缓存的多级架构
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.l1_cache = MemoryCache(config)
        self.l2_cache = RedisCache(config) if config.redis_url else None
        self._warming_task: Optional[asyncio.Task] = None
        self._warming_callbacks: List[Callable] = []
    
    async def start(self):
        """启动多级缓存"""
        if self.l2_cache:
            await self.l2_cache.start()
        
        if self.config.cache_warming_enabled:
            self._warming_task = asyncio.create_task(self._cache_warming_loop())
        
        logger.info("多级缓存系统已启动")
    
    async def stop(self):
        """停止多级缓存"""
        if self._warming_task:
            self._warming_task.cancel()
            try:
                await self._warming_task
            except asyncio.CancelledError:
                pass
        
        if self.l2_cache:
            await self.l2_cache.stop()
        
        logger.info("多级缓存系统已停止")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值（多级查找）"""
        # 先查L1缓存
        value = await self.l1_cache.get(key)
        if value is not None:
            return value
        
        # 再查L2缓存
        if self.l2_cache:
            value = await self.l2_cache.get(key)
            if value is not None:
                # 回写到L1缓存
                await self.l1_cache.set(key, value)
                return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存值（写入所有级别）"""
        results = []
        
        # 写入L1缓存
        results.append(await self.l1_cache.set(key, value, ttl))
        
        # 写入L2缓存
        if self.l2_cache:
            results.append(await self.l2_cache.set(key, value, ttl))
        
        return any(results)
    
    async def delete(self, key: str) -> bool:
        """删除缓存值（从所有级别删除）"""
        results = []
        
        results.append(await self.l1_cache.delete(key))
        
        if self.l2_cache:
            results.append(await self.l2_cache.delete(key))
        
        return any(results)
    
    async def clear(self) -> bool:
        """清空所有缓存"""
        results = []
        
        results.append(await self.l1_cache.clear())
        
        if self.l2_cache:
            results.append(await self.l2_cache.clear())
        
        return any(results)
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if await self.l1_cache.exists(key):
            return True
        
        if self.l2_cache and await self.l2_cache.exists(key):
            return True
        
        return False
    
    def get_stats(self) -> Dict[str, CacheStats]:
        """获取所有级别的缓存统计"""
        stats = {
            "l1_memory": self.l1_cache.get_stats()
        }
        
        if self.l2_cache:
            stats["l2_redis"] = self.l2_cache.get_stats()
        
        return stats
    
    def add_warming_callback(self, callback: Callable):
        """添加缓存预热回调"""
        self._warming_callbacks.append(callback)
    
    async def _cache_warming_loop(self):
        """缓存预热循环"""
        while True:
            try:
                await asyncio.sleep(self.config.cache_warming_interval)
                await self._execute_warming_callbacks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存预热出错: {e}")
    
    async def _execute_warming_callbacks(self):
        """执行缓存预热回调"""
        for callback in self._warming_callbacks:
            try:
                await callback()
            except Exception as e:
                logger.error(f"缓存预热回调执行失败: {e}")

class SmartCacheManager:
    """
    智能缓存管理器
    提供基于请求的智能缓存策略
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = MultiLevelCache(config)
        self._cache_rules: List[Dict] = []
    
    async def start(self):
        """启动缓存管理器"""
        await self.cache.start()
        logger.info("智能缓存管理器已启动")
    
    async def stop(self):
        """停止缓存管理器"""
        await self.cache.stop()
        logger.info("智能缓存管理器已停止")
    
    def add_cache_rule(self, pattern: str, ttl: int, conditions: Dict = None):
        """
        添加缓存规则
        
        Args:
            pattern: URL模式
            ttl: 缓存时间
            conditions: 缓存条件
        """
        rule = {
            "pattern": pattern,
            "ttl": ttl,
            "conditions": conditions or {}
        }
        self._cache_rules.append(rule)
    
    def create_key_from_request(self, request: Request) -> str:
        """从请求创建缓存键"""
        # 基础键：方法 + 路径 + 查询参数
        base_key = f"{request.method}:{request.url.path}"
        
        if request.query_params:
            query_string = str(request.query_params)
            base_key += f"?{query_string}"
        
        # 添加相关头部
        relevant_headers = ["authorization", "accept-language", "user-agent"]
        header_parts = []
        
        for header in relevant_headers:
            value = request.headers.get(header)
            if value:
                header_parts.append(f"{header}:{value}")
        
        if header_parts:
            base_key += f"|{':'.join(header_parts)}"
        
        # 生成哈希键
        return hashlib.md5(base_key.encode()).hexdigest()
    
    def should_cache_request(self, request: Request) -> bool:
        """判断请求是否应该缓存"""
        # 只缓存GET请求
        if request.method.upper() != "GET":
            return False
        
        # 检查缓存规则
        for rule in self._cache_rules:
            if self._match_rule(request, rule):
                return True
        
        return False
    
    def get_cache_ttl(self, request: Request) -> int:
        """获取请求的缓存TTL"""
        for rule in self._cache_rules:
            if self._match_rule(request, rule):
                return rule["ttl"]
        
        return self.config.default_ttl
    
    def _match_rule(self, request: Request, rule: Dict) -> bool:
        """检查请求是否匹配缓存规则"""
        import re
        
        # 检查URL模式
        if not re.match(rule["pattern"], request.url.path):
            return False
        
        # 检查条件
        conditions = rule.get("conditions", {})
        
        # 检查头部条件
        if "headers" in conditions:
            for header, expected_value in conditions["headers"].items():
                actual_value = request.headers.get(header)
                if actual_value != expected_value:
                    return False
        
        return True
    
    async def get_cached_response(self, request: Request) -> Optional[Response]:
        """获取缓存的响应"""
        if not self.should_cache_request(request):
            return None
        
        cache_key = self.create_key_from_request(request)
        cached_data = await self.cache.get(cache_key)
        
        if cached_data:
            return Response(
                content=cached_data["content"],
                status_code=cached_data["status_code"],
                headers=cached_data["headers"],
                media_type=cached_data.get("media_type")
            )
        
        return None
    
    async def cache_response(self, request: Request, response: Response):
        """缓存响应"""
        if not self.should_cache_request(request):
            return
        
        # 只缓存成功的响应
        if not (200 <= response.status_code < 300):
            return
        
        cache_key = self.create_key_from_request(request)
        ttl = self.get_cache_ttl(request)
        
        # 读取响应内容
        if hasattr(response, 'body'):
            content = response.body
        else:
            content = b""
        
        cached_data = {
            "content": content,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "media_type": response.media_type
        }
        
        await self.cache.set(cache_key, cached_data, ttl)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "cache_stats": self.cache.get_stats(),
            "cache_rules_count": len(self._cache_rules),
            "config": asdict(self.config)
        } 