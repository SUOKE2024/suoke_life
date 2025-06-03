#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能缓存管理器
支持多级缓存、智能预热、压缩和缓存规则引擎
"""

import asyncio
import gzip
import hashlib
import json
import logging
import pickle
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union
from collections import OrderedDict

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

@dataclass
class CacheRule:
    """缓存规则"""
    pattern: Pattern[str]
    ttl: int
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    compress: bool = False
    tags: Set[str] = field(default_factory=set)

@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    memory_usage: int = 0
    redis_usage: int = 0
    compression_ratio: float = 0.0
    avg_response_time: float = 0.0

@dataclass
class SmartCacheConfig:
    """智能缓存配置"""
    # 基础配置
    enabled: bool = True
    default_ttl: int = 300
    
    # 内存缓存
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    max_memory_items: int = 10000
    memory_cleanup_interval: float = 60.0
    
    # Redis配置
    redis_url: Optional[str] = None
    redis_db: int = 0
    redis_max_connections: int = 20
    redis_retry_on_timeout: bool = True
    
    # 压缩配置
    compression_enabled: bool = True
    compression_threshold: int = 1024  # 1KB
    compression_level: int = 6
    
    # 预热配置
    cache_warming_enabled: bool = True
    cache_warming_interval: float = 300.0
    cache_warming_batch_size: int = 100
    
    # 性能配置
    async_write: bool = True
    write_behind_delay: float = 0.1
    batch_write_size: int = 50

class MemoryCache:
    """内存缓存实现"""
    
    def __init__(self, max_size: int, max_items: int):
        self.max_size = max_size
        self.max_items = max_items
        self._cache: OrderedDict = OrderedDict()
        self._size = 0
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """获取缓存项"""
        async with self._lock:
            if key in self._cache:
                value, expire_time = self._cache[key]
                if expire_time > time.time():
                    # 移到末尾（LRU）
                    self._cache.move_to_end(key)
                    return value, expire_time
                else:
                    # 过期删除
                    del self._cache[key]
                    self._size -= len(pickle.dumps(value))
        return None
    
    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """设置缓存项"""
        expire_time = time.time() + ttl
        serialized_value = pickle.dumps(value)
        value_size = len(serialized_value)
        
        async with self._lock:
            # 检查是否需要清理空间
            while (self._size + value_size > self.max_size or 
                   len(self._cache) >= self.max_items) and self._cache:
                oldest_key = next(iter(self._cache))
                oldest_value, _ = self._cache.pop(oldest_key)
                self._size -= len(pickle.dumps(oldest_value))
            
            # 如果值太大，直接拒绝
            if value_size > self.max_size:
                return False
            
            # 更新缓存
            if key in self._cache:
                old_value, _ = self._cache[key]
                self._size -= len(pickle.dumps(old_value))
            
            self._cache[key] = (value, expire_time)
            self._size += value_size
            
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存项"""
        async with self._lock:
            if key in self._cache:
                value, _ = self._cache.pop(key)
                self._size -= len(pickle.dumps(value))
                return True
            return False
    
    async def clear(self):
        """清空缓存"""
        async with self._lock:
            self._cache.clear()
            self._size = 0
    
    async def cleanup_expired(self):
        """清理过期项"""
        current_time = time.time()
        expired_keys = []
        
        async with self._lock:
            for key, (value, expire_time) in self._cache.items():
                if expire_time <= current_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                value, _ = self._cache.pop(key)
                self._size -= len(pickle.dumps(value))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'items': len(self._cache),
            'size': self._size,
            'max_size': self.max_size,
            'max_items': self.max_items,
            'utilization': self._size / self.max_size if self.max_size > 0 else 0
        }

class SmartCacheManager:
    """智能缓存管理器"""
    
    def __init__(self, config: SmartCacheConfig):
        self.config = config
        self.stats = CacheStats()
        
        # 缓存层
        self.memory_cache = MemoryCache(config.max_memory_size, config.max_memory_items)
        self.redis_client: Optional[Redis] = None
        
        # 缓存规则
        self.cache_rules: List[CacheRule] = []
        
        # 预热相关
        self.warming_queue: asyncio.Queue = asyncio.Queue()
        self.warming_tasks: List[asyncio.Task] = []
        
        # 写入队列（异步写入）
        self.write_queue: asyncio.Queue = asyncio.Queue()
        self.write_tasks: List[asyncio.Task] = []
        
        # 控制标志
        self._running = False
        self._background_tasks: List[asyncio.Task] = []
    
    async def start(self):
        """启动缓存管理器"""
        if self._running:
            return
        
        # 初始化Redis连接
        if self.config.redis_url:
            await self._init_redis()
        
        # 启动后台任务
        self._background_tasks.extend([
            asyncio.create_task(self._memory_cleanup_loop()),
            asyncio.create_task(self._stats_update_loop())
        ])
        
        if self.config.cache_warming_enabled:
            self._background_tasks.append(
                asyncio.create_task(self._cache_warming_loop())
            )
        
        if self.config.async_write:
            self._background_tasks.append(
                asyncio.create_task(self._async_write_loop())
            )
        
        self._running = True
        logger.info("智能缓存管理器已启动")
    
    async def stop(self):
        """停止缓存管理器"""
        if not self._running:
            return
        
        self._running = False
        
        # 取消后台任务
        for task in self._background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        
        # 关闭Redis连接
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("智能缓存管理器已停止")
    
    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                db=self.config.redis_db,
                max_connections=self.config.redis_max_connections,
                retry_on_timeout=self.config.redis_retry_on_timeout,
                decode_responses=False  # 保持二进制数据
            )
            
            # 测试连接
            await self.redis_client.ping()
            logger.info("Redis连接已建立")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            self.redis_client = None
    
    def add_cache_rule(self, pattern: str, ttl: int, **kwargs):
        """添加缓存规则"""
        rule = CacheRule(
            pattern=re.compile(pattern),
            ttl=ttl,
            conditions=kwargs.get('conditions', {}),
            priority=kwargs.get('priority', 0),
            compress=kwargs.get('compress', False),
            tags=set(kwargs.get('tags', []))
        )
        
        # 按优先级插入
        inserted = False
        for i, existing_rule in enumerate(self.cache_rules):
            if rule.priority > existing_rule.priority:
                self.cache_rules.insert(i, rule)
                inserted = True
                break
        
        if not inserted:
            self.cache_rules.append(rule)
        
        logger.info(f"添加缓存规则: {pattern}, TTL: {ttl}s")
    
    def _find_matching_rule(self, key: str, headers: Dict[str, str] = None) -> Optional[CacheRule]:
        """查找匹配的缓存规则"""
        headers = headers or {}
        
        for rule in self.cache_rules:
            if rule.pattern.match(key):
                # 检查条件
                if self._check_rule_conditions(rule, headers):
                    return rule
        
        return None
    
    def _check_rule_conditions(self, rule: CacheRule, headers: Dict[str, str]) -> bool:
        """检查规则条件"""
        conditions = rule.conditions
        
        # 检查头部条件
        if 'headers' in conditions:
            for header_name, expected_value in conditions['headers'].items():
                if headers.get(header_name) != expected_value:
                    return False
        
        # 可以添加更多条件检查
        return True
    
    def _generate_cache_key(self, key: str, **kwargs) -> str:
        """生成缓存键"""
        # 添加前缀
        cache_key = f"suoke:gateway:{key}"
        
        # 如果有额外参数，添加到键中
        if kwargs:
            params_str = json.dumps(kwargs, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            cache_key += f":{params_hash}"
        
        return cache_key
    
    def _compress_data(self, data: bytes) -> bytes:
        """压缩数据"""
        if not self.config.compression_enabled or len(data) < self.config.compression_threshold:
            return data
        
        return gzip.compress(data, compresslevel=self.config.compression_level)
    
    def _decompress_data(self, data: bytes) -> bytes:
        """解压数据"""
        try:
            return gzip.decompress(data)
        except gzip.BadGzipFile:
            # 数据未压缩
            return data
    
    async def get(self, key: str, headers: Dict[str, str] = None) -> Optional[Any]:
        """获取缓存值"""
        if not self.config.enabled:
            return None
        
        start_time = time.time()
        cache_key = self._generate_cache_key(key)
        
        try:
            # 先查内存缓存
            result = await self.memory_cache.get(cache_key)
            if result:
                value, _ = result
                self.stats.hits += 1
                return value
            
            # 再查Redis缓存
            if self.redis_client:
                data = await self.redis_client.get(cache_key)
                if data:
                    # 解压和反序列化
                    decompressed_data = self._decompress_data(data)
                    value = pickle.loads(decompressed_data)
                    
                    # 回写到内存缓存
                    rule = self._find_matching_rule(key, headers)
                    ttl = rule.ttl if rule else self.config.default_ttl
                    await self.memory_cache.set(cache_key, value, ttl)
                    
                    self.stats.hits += 1
                    return value
            
            self.stats.misses += 1
            return None
            
        except Exception as e:
            logger.error(f"缓存获取失败 {cache_key}: {e}")
            self.stats.misses += 1
            return None
        
        finally:
            response_time = time.time() - start_time
            self._update_response_time(response_time)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, headers: Dict[str, str] = None):
        """设置缓存值"""
        if not self.config.enabled:
            return
        
        cache_key = self._generate_cache_key(key)
        
        # 确定TTL
        if ttl is None:
            rule = self._find_matching_rule(key, headers)
            ttl = rule.ttl if rule else self.config.default_ttl
        
        try:
            # 设置内存缓存
            await self.memory_cache.set(cache_key, value, ttl)
            
            # 异步设置Redis缓存
            if self.redis_client:
                if self.config.async_write:
                    await self.write_queue.put((cache_key, value, ttl))
                else:
                    await self._write_to_redis(cache_key, value, ttl)
            
            self.stats.sets += 1
            
        except Exception as e:
            logger.error(f"缓存设置失败 {cache_key}: {e}")
    
    async def _write_to_redis(self, cache_key: str, value: Any, ttl: int):
        """写入Redis"""
        try:
            # 序列化和压缩
            serialized_data = pickle.dumps(value)
            compressed_data = self._compress_data(serialized_data)
            
            # 写入Redis
            await self.redis_client.setex(cache_key, ttl, compressed_data)
            
        except Exception as e:
            logger.error(f"Redis写入失败 {cache_key}: {e}")
    
    async def delete(self, key: str):
        """删除缓存"""
        cache_key = self._generate_cache_key(key)
        
        try:
            # 删除内存缓存
            await self.memory_cache.delete(cache_key)
            
            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(cache_key)
            
            self.stats.deletes += 1
            
        except Exception as e:
            logger.error(f"缓存删除失败 {cache_key}: {e}")
    
    async def delete_by_tags(self, tags: Set[str]):
        """根据标签删除缓存"""
        # 这里需要维护标签到键的映射，简化实现
        logger.info(f"删除标签缓存: {tags}")
    
    async def clear(self):
        """清空所有缓存"""
        await self.memory_cache.clear()
        
        if self.redis_client:
            # 删除所有以前缀开头的键
            pattern = "suoke:gateway:*"
            async for key in self.redis_client.scan_iter(match=pattern):
                await self.redis_client.delete(key)
    
    async def _memory_cleanup_loop(self):
        """内存清理循环"""
        while self._running:
            try:
                await self.memory_cache.cleanup_expired()
                await asyncio.sleep(self.config.memory_cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"内存清理失败: {e}")
                await asyncio.sleep(self.config.memory_cleanup_interval)
    
    async def _cache_warming_loop(self):
        """缓存预热循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.cache_warming_interval)
                # 这里可以实现预热逻辑
                logger.debug("执行缓存预热")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存预热失败: {e}")
    
    async def _async_write_loop(self):
        """异步写入循环"""
        batch = []
        
        while self._running:
            try:
                # 收集批量写入数据
                try:
                    item = await asyncio.wait_for(
                        self.write_queue.get(), 
                        timeout=self.config.write_behind_delay
                    )
                    batch.append(item)
                except asyncio.TimeoutError:
                    pass
                
                # 批量写入
                if batch and len(batch) >= self.config.batch_write_size:
                    await self._batch_write_to_redis(batch)
                    batch.clear()
                
            except asyncio.CancelledError:
                # 处理剩余批次
                if batch:
                    await self._batch_write_to_redis(batch)
                break
            except Exception as e:
                logger.error(f"异步写入失败: {e}")
    
    async def _batch_write_to_redis(self, batch: List[Tuple[str, Any, int]]):
        """批量写入Redis"""
        if not self.redis_client or not batch:
            return
        
        try:
            pipe = self.redis_client.pipeline()
            
            for cache_key, value, ttl in batch:
                serialized_data = pickle.dumps(value)
                compressed_data = self._compress_data(serialized_data)
                pipe.setex(cache_key, ttl, compressed_data)
            
            await pipe.execute()
            
        except Exception as e:
            logger.error(f"批量写入Redis失败: {e}")
    
    async def _stats_update_loop(self):
        """统计更新循环"""
        while self._running:
            try:
                await self._update_stats()
                await asyncio.sleep(60)  # 每分钟更新一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"统计更新失败: {e}")
    
    async def _update_stats(self):
        """更新统计信息"""
        # 更新内存使用情况
        memory_stats = self.memory_cache.get_stats()
        self.stats.memory_usage = memory_stats['size']
        
        # 更新Redis使用情况
        if self.redis_client:
            try:
                info = await self.redis_client.info('memory')
                self.stats.redis_usage = info.get('used_memory', 0)
            except Exception:
                pass
    
    def _update_response_time(self, response_time: float):
        """更新响应时间统计"""
        # 简单的移动平均
        alpha = 0.1
        self.stats.avg_response_time = (
            alpha * response_time + 
            (1 - alpha) * self.stats.avg_response_time
        )
    
    @property
    def hit_ratio(self) -> float:
        """缓存命中率"""
        total = self.stats.hits + self.stats.misses
        return self.stats.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        memory_stats = self.memory_cache.get_stats()
        
        return {
            'enabled': self.config.enabled,
            'hit_ratio': self.hit_ratio,
            'stats': {
                'hits': self.stats.hits,
                'misses': self.stats.misses,
                'sets': self.stats.sets,
                'deletes': self.stats.deletes,
                'avg_response_time': self.stats.avg_response_time
            },
            'memory_cache': memory_stats,
            'redis_connected': self.redis_client is not None,
            'redis_usage': self.stats.redis_usage,
            'rules_count': len(self.cache_rules)
        } 