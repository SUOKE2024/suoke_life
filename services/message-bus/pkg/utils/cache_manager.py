#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存管理器
支持多级缓存、LRU策略、TTL过期和性能优化
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable, Union, Tuple
from collections import OrderedDict, defaultdict
import threading

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """缓存级别"""
    L1_MEMORY = "l1_memory"      # 内存缓存
    L2_REDIS = "l2_redis"        # Redis缓存
    L3_DISK = "l3_disk"          # 磁盘缓存

class EvictionPolicy(Enum):
    """淘汰策略"""
    LRU = "lru"                  # 最近最少使用
    LFU = "lfu"                  # 最少使用频率
    FIFO = "fifo"                # 先进先出
    TTL = "ttl"                  # 基于过期时间
    RANDOM = "random"            # 随机淘汰

class CacheType(Enum):
    """缓存类型"""
    MESSAGE = "message"          # 消息缓存
    TOPIC = "topic"              # 主题缓存
    USER = "user"                # 用户缓存
    ROUTING = "routing"          # 路由缓存
    METADATA = "metadata"        # 元数据缓存

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """更新访问时间和计数"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def get_age(self) -> float:
        """获取年龄（秒）"""
        return time.time() - self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at,
            'accessed_at': self.accessed_at,
            'access_count': self.access_count,
            'ttl': self.ttl,
            'size': self.size,
            'metadata': self.metadata
        }

@dataclass
class CacheConfig:
    """缓存配置"""
    # 基础配置
    enable_cache: bool = True
    cache_levels: List[CacheLevel] = field(default_factory=lambda: [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS])
    
    # L1内存缓存配置
    l1_max_size: int = 1000        # 最大条目数
    l1_max_memory: int = 100 * 1024 * 1024  # 100MB
    l1_eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    l1_default_ttl: Optional[float] = 3600.0  # 1小时
    
    # L2 Redis缓存配置
    l2_redis_host: str = "localhost"
    l2_redis_port: int = 6379
    l2_redis_db: int = 0
    l2_key_prefix: str = "cache"
    l2_default_ttl: Optional[float] = 86400.0  # 24小时
    
    # L3磁盘缓存配置
    l3_cache_dir: str = "/tmp/message_bus_cache"
    l3_max_size: int = 1024 * 1024 * 1024  # 1GB
    l3_default_ttl: Optional[float] = 604800.0  # 7天
    
    # 性能配置
    enable_compression: bool = True
    compression_threshold: int = 1024  # 1KB
    enable_async_write: bool = True
    write_batch_size: int = 100
    
    # 监控配置
    enable_metrics: bool = True
    stats_interval: float = 60.0

class CacheStats:
    """缓存统计"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.errors = 0
        self.total_size = 0
        self.entry_count = 0
        self._lock = threading.Lock()
    
    def record_hit(self):
        """记录命中"""
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        """记录未命中"""
        with self._lock:
            self.misses += 1
    
    def record_set(self, size: int = 0):
        """记录设置"""
        with self._lock:
            self.sets += 1
            self.total_size += size
            self.entry_count += 1
    
    def record_delete(self, size: int = 0):
        """记录删除"""
        with self._lock:
            self.deletes += 1
            self.total_size -= size
            self.entry_count -= 1
    
    def record_eviction(self, size: int = 0):
        """记录淘汰"""
        with self._lock:
            self.evictions += 1
            self.total_size -= size
            self.entry_count -= 1
    
    def record_error(self):
        """记录错误"""
        with self._lock:
            self.errors += 1
    
    def get_hit_rate(self) -> float:
        """获取命中率"""
        with self._lock:
            total = self.hits + self.misses
            return self.hits / total if total > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'evictions': self.evictions,
                'errors': self.errors,
                'total_size': self.total_size,
                'entry_count': self.entry_count,
                'hit_rate': self.get_hit_rate()
            }
    
    def reset(self):
        """重置统计"""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.evictions = 0
            self.errors = 0
            self.total_size = 0
            self.entry_count = 0

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int, max_memory: int, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.max_memory = max_memory
        self.default_ttl = default_ttl
        
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_memory = 0
        self._lock = threading.RLock()
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self.stats.record_miss()
                return None
            
            # 检查是否过期
            if entry.is_expired():
                self._remove_entry(key)
                self.stats.record_miss()
                return None
            
            # 更新访问信息
            entry.touch()
            
            # 移动到末尾（最近使用）
            self._cache.move_to_end(key)
            
            self.stats.record_hit()
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        with self._lock:
            try:
                # 计算大小
                size = self._calculate_size(value)
                
                # 检查是否已存在
                if key in self._cache:
                    old_entry = self._cache[key]
                    self._current_memory -= old_entry.size
                    self.stats.record_delete(old_entry.size)
                
                # 创建新条目
                entry = CacheEntry(
                    key=key,
                    value=value,
                    ttl=ttl or self.default_ttl,
                    size=size
                )
                
                # 检查内存限制
                if self._current_memory + size > self.max_memory:
                    self._evict_by_memory(size)
                
                # 检查大小限制
                if len(self._cache) >= self.max_size:
                    self._evict_by_size()
                
                # 添加到缓存
                self._cache[key] = entry
                self._current_memory += size
                self.stats.record_set(size)
                
                return True
                
            except Exception as e:
                logger.error(f"设置缓存失败: {e}")
                self.stats.record_error()
                return False
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                self._remove_entry(key)
                self.stats.record_delete(entry.size)
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._current_memory = 0
            self.stats.reset()
    
    def _remove_entry(self, key: str):
        """移除条目"""
        if key in self._cache:
            entry = self._cache.pop(key)
            self._current_memory -= entry.size
    
    def _evict_by_size(self):
        """按大小淘汰"""
        if self._cache:
            # LRU: 移除最久未使用的
            oldest_key = next(iter(self._cache))
            entry = self._cache[oldest_key]
            self._remove_entry(oldest_key)
            self.stats.record_eviction(entry.size)
    
    def _evict_by_memory(self, needed_size: int):
        """按内存淘汰"""
        while self._current_memory + needed_size > self.max_memory and self._cache:
            oldest_key = next(iter(self._cache))
            entry = self._cache[oldest_key]
            self._remove_entry(oldest_key)
            self.stats.record_eviction(entry.size)
    
    def _calculate_size(self, value: Any) -> int:
        """计算值的大小"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, dict):
                return len(json.dumps(value).encode())
            else:
                return len(str(value).encode())
        except:
            return 100  # 默认大小
    
    def cleanup_expired(self):
        """清理过期条目"""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                entry = self._cache[key]
                self._remove_entry(key)
                self.stats.record_eviction(entry.size)
    
    def get_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage': self._current_memory,
                'max_memory': self.max_memory,
                'memory_utilization': self._current_memory / self.max_memory if self.max_memory > 0 else 0,
                'stats': self.stats.get_stats()
            }

class RedisCache:
    """Redis缓存实现"""
    
    def __init__(self, host: str, port: int, db: int, key_prefix: str, default_ttl: Optional[float] = None):
        self.host = host
        self.port = port
        self.db = db
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        
        self.redis_client = None
        self.stats = CacheStats()
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis客户端"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
        except ImportError:
            logger.error("Redis客户端未安装，请安装redis-py")
            raise
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def _get_key(self, key: str) -> str:
        """获取完整的Redis键"""
        return f"{self.key_prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            redis_key = self._get_key(key)
            data = self.redis_client.get(redis_key)
            
            if data is None:
                self.stats.record_miss()
                return None
            
            # 反序列化
            try:
                value = json.loads(data)
                self.stats.record_hit()
                return value
            except json.JSONDecodeError:
                # 如果不是JSON，直接返回字符串
                self.stats.record_hit()
                return data
                
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            self.stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        try:
            redis_key = self._get_key(key)
            
            # 序列化
            if isinstance(value, (str, bytes)):
                data = value
            else:
                data = json.dumps(value)
            
            # 设置TTL
            expire_time = ttl or self.default_ttl
            
            if expire_time:
                self.redis_client.setex(redis_key, int(expire_time), data)
            else:
                self.redis_client.set(redis_key, data)
            
            self.stats.record_set(len(data) if isinstance(data, str) else len(str(data)))
            return True
            
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
            self.stats.record_error()
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            redis_key = self._get_key(key)
            result = self.redis_client.delete(redis_key)
            
            if result > 0:
                self.stats.record_delete()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
            self.stats.record_error()
            return False
    
    async def clear(self):
        """清空缓存"""
        try:
            pattern = f"{self.key_prefix}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            self.stats.reset()
            
        except Exception as e:
            logger.error(f"Redis清空失败: {e}")
            self.stats.record_error()
    
    def get_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            info = self.redis_client.info('memory')
            pattern = f"{self.key_prefix}:*"
            key_count = len(self.redis_client.keys(pattern))
            
            return {
                'key_count': key_count,
                'memory_usage': info.get('used_memory', 0),
                'stats': self.stats.get_stats()
            }
        except Exception as e:
            logger.error(f"获取Redis信息失败: {e}")
            return {'stats': self.stats.get_stats()}

class MultiLevelCache:
    """多级缓存"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.caches: Dict[CacheLevel, Any] = {}
        self.stats = CacheStats()
        
        # 初始化各级缓存
        self._init_caches()
        
        # 后台任务
        self._background_tasks: List[asyncio.Task] = []
        self._running = False
    
    def _init_caches(self):
        """初始化缓存"""
        try:
            if CacheLevel.L1_MEMORY in self.config.cache_levels:
                self.caches[CacheLevel.L1_MEMORY] = LRUCache(
                    max_size=self.config.l1_max_size,
                    max_memory=self.config.l1_max_memory,
                    default_ttl=self.config.l1_default_ttl
                )
            
            if CacheLevel.L2_REDIS in self.config.cache_levels:
                self.caches[CacheLevel.L2_REDIS] = RedisCache(
                    host=self.config.l2_redis_host,
                    port=self.config.l2_redis_port,
                    db=self.config.l2_redis_db,
                    key_prefix=self.config.l2_key_prefix,
                    default_ttl=self.config.l2_default_ttl
                )
            
            logger.info(f"初始化缓存级别: {[level.value for level in self.caches.keys()]}")
            
        except Exception as e:
            logger.error(f"缓存初始化失败: {e}")
            raise
    
    async def start(self):
        """启动缓存管理器"""
        if self._running:
            return
        
        try:
            # 启动后台任务
            await self._start_background_tasks()
            
            self._running = True
            logger.info("缓存管理器启动成功")
            
        except Exception as e:
            logger.error(f"缓存管理器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止缓存管理器"""
        if not self._running:
            return
        
        try:
            self._running = False
            
            # 停止后台任务
            await self._stop_background_tasks()
            
            logger.info("缓存管理器已停止")
            
        except Exception as e:
            logger.error(f"缓存管理器停止失败: {e}")
    
    async def get(self, key: str, cache_type: CacheType = CacheType.MESSAGE) -> Optional[Any]:
        """获取缓存值"""
        if not self.config.enable_cache:
            return None
        
        try:
            # 按级别顺序查找
            for level in self.config.cache_levels:
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                if level == CacheLevel.L1_MEMORY:
                    value = cache.get(key)
                else:
                    value = await cache.get(key)
                
                if value is not None:
                    # 回填到更高级别的缓存
                    await self._backfill_cache(key, value, level)
                    self.stats.record_hit()
                    return value
            
            self.stats.record_miss()
            return None
            
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            self.stats.record_error()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None, 
                 cache_type: CacheType = CacheType.MESSAGE) -> bool:
        """设置缓存值"""
        if not self.config.enable_cache:
            return False
        
        try:
            success = True
            
            # 设置到所有级别的缓存
            for level in self.config.cache_levels:
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                if level == CacheLevel.L1_MEMORY:
                    result = cache.set(key, value, ttl)
                else:
                    result = await cache.set(key, value, ttl)
                
                if not result:
                    success = False
            
            if success:
                self.stats.record_set()
            else:
                self.stats.record_error()
            
            return success
            
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            self.stats.record_error()
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            success = True
            
            # 从所有级别删除
            for level in self.config.cache_levels:
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                if level == CacheLevel.L1_MEMORY:
                    result = cache.delete(key)
                else:
                    result = await cache.delete(key)
                
                if not result:
                    success = False
            
            if success:
                self.stats.record_delete()
            
            return success
            
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            self.stats.record_error()
            return False
    
    async def clear(self, cache_type: Optional[CacheType] = None):
        """清空缓存"""
        try:
            for level in self.config.cache_levels:
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                if level == CacheLevel.L1_MEMORY:
                    cache.clear()
                else:
                    await cache.clear()
            
            self.stats.reset()
            
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
    
    async def _backfill_cache(self, key: str, value: Any, found_level: CacheLevel):
        """回填缓存到更高级别"""
        try:
            # 找到更高级别的缓存并回填
            for level in self.config.cache_levels:
                if level == found_level:
                    break
                
                cache = self.caches.get(level)
                if not cache:
                    continue
                
                if level == CacheLevel.L1_MEMORY:
                    cache.set(key, value)
                else:
                    await cache.set(key, value)
                    
        except Exception as e:
            logger.error(f"缓存回填失败: {e}")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        # 清理过期条目任务
        task = asyncio.create_task(self._cleanup_loop())
        self._background_tasks.append(task)
        
        # 统计报告任务
        if self.config.enable_metrics:
            task = asyncio.create_task(self._stats_loop())
            self._background_tasks.append(task)
    
    async def _stop_background_tasks(self):
        """停止后台任务"""
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._running:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                
                # 清理L1内存缓存的过期条目
                l1_cache = self.caches.get(CacheLevel.L1_MEMORY)
                if l1_cache:
                    l1_cache.cleanup_expired()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存清理失败: {e}")
    
    async def _stats_loop(self):
        """统计循环"""
        while self._running:
            try:
                await asyncio.sleep(self.config.stats_interval)
                
                # 记录统计信息
                stats = self.get_cache_stats()
                logger.info(f"缓存统计: {stats}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存统计失败: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        stats = {
            'overall': self.stats.get_stats(),
            'levels': {}
        }
        
        for level, cache in self.caches.items():
            try:
                if hasattr(cache, 'get_info'):
                    stats['levels'][level.value] = cache.get_info()
            except Exception as e:
                logger.error(f"获取{level.value}缓存统计失败: {e}")
        
        return stats

class CacheManager:
    """
    缓存管理器
    支持多级缓存、智能淘汰和性能优化
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        
        # 缓存实例
        self.caches: Dict[CacheType, MultiLevelCache] = {}
        
        # 全局统计
        self.global_stats = CacheStats()
        
        # 初始化缓存
        self._init_caches()
    
    def _init_caches(self):
        """初始化各类型缓存"""
        try:
            for cache_type in CacheType:
                self.caches[cache_type] = MultiLevelCache(self.config)
            
            logger.info(f"初始化缓存类型: {[t.value for t in self.caches.keys()]}")
            
        except Exception as e:
            logger.error(f"缓存管理器初始化失败: {e}")
            raise
    
    async def start(self):
        """启动缓存管理器"""
        try:
            for cache in self.caches.values():
                await cache.start()
            
            logger.info("缓存管理器启动成功")
            
        except Exception as e:
            logger.error(f"缓存管理器启动失败: {e}")
            raise
    
    async def stop(self):
        """停止缓存管理器"""
        try:
            for cache in self.caches.values():
                await cache.stop()
            
            logger.info("缓存管理器已停止")
            
        except Exception as e:
            logger.error(f"缓存管理器停止失败: {e}")
    
    async def get(self, key: str, cache_type: CacheType = CacheType.MESSAGE) -> Optional[Any]:
        """获取缓存值"""
        cache = self.caches.get(cache_type)
        if not cache:
            return None
        
        value = await cache.get(key, cache_type)
        
        if value is not None:
            self.global_stats.record_hit()
        else:
            self.global_stats.record_miss()
        
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None,
                 cache_type: CacheType = CacheType.MESSAGE) -> bool:
        """设置缓存值"""
        cache = self.caches.get(cache_type)
        if not cache:
            return False
        
        success = await cache.set(key, value, ttl, cache_type)
        
        if success:
            self.global_stats.record_set()
        else:
            self.global_stats.record_error()
        
        return success
    
    async def delete(self, key: str, cache_type: CacheType = CacheType.MESSAGE) -> bool:
        """删除缓存值"""
        cache = self.caches.get(cache_type)
        if not cache:
            return False
        
        success = await cache.delete(key)
        
        if success:
            self.global_stats.record_delete()
        
        return success
    
    async def clear(self, cache_type: Optional[CacheType] = None):
        """清空缓存"""
        if cache_type:
            cache = self.caches.get(cache_type)
            if cache:
                await cache.clear(cache_type)
        else:
            for cache in self.caches.values():
                await cache.clear()
        
        self.global_stats.reset()
    
    # 便捷方法
    async def get_message(self, message_id: str) -> Optional[Any]:
        """获取消息缓存"""
        return await self.get(f"message:{message_id}", CacheType.MESSAGE)
    
    async def set_message(self, message_id: str, message: Any, ttl: Optional[float] = None) -> bool:
        """设置消息缓存"""
        return await self.set(f"message:{message_id}", message, ttl, CacheType.MESSAGE)
    
    async def get_topic_info(self, topic: str) -> Optional[Any]:
        """获取主题信息缓存"""
        return await self.get(f"topic:{topic}", CacheType.TOPIC)
    
    async def set_topic_info(self, topic: str, info: Any, ttl: Optional[float] = None) -> bool:
        """设置主题信息缓存"""
        return await self.set(f"topic:{topic}", info, ttl, CacheType.TOPIC)
    
    async def get_user_info(self, user_id: str) -> Optional[Any]:
        """获取用户信息缓存"""
        return await self.get(f"user:{user_id}", CacheType.USER)
    
    async def set_user_info(self, user_id: str, info: Any, ttl: Optional[float] = None) -> bool:
        """设置用户信息缓存"""
        return await self.set(f"user:{user_id}", info, ttl, CacheType.USER)
    
    async def get_routing_info(self, key: str) -> Optional[Any]:
        """获取路由信息缓存"""
        return await self.get(f"routing:{key}", CacheType.ROUTING)
    
    async def set_routing_info(self, key: str, info: Any, ttl: Optional[float] = None) -> bool:
        """设置路由信息缓存"""
        return await self.set(f"routing:{key}", info, ttl, CacheType.ROUTING)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        stats = {
            'global': self.global_stats.get_stats(),
            'by_type': {}
        }
        
        for cache_type, cache in self.caches.items():
            try:
                stats['by_type'][cache_type.value] = cache.get_cache_stats()
            except Exception as e:
                logger.error(f"获取{cache_type.value}缓存统计失败: {e}")
        
        return stats
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'config': {
                'enable_cache': self.config.enable_cache,
                'cache_levels': [level.value for level in self.config.cache_levels],
                'l1_max_size': self.config.l1_max_size,
                'l1_max_memory': self.config.l1_max_memory,
                'l2_redis_host': self.config.l2_redis_host,
                'l2_redis_port': self.config.l2_redis_port
            },
            'cache_types': [t.value for t in self.caches.keys()],
            'stats': self.get_cache_stats()
        }

class CacheManagerFactory:
    """缓存管理器工厂"""
    
    @staticmethod
    def create_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
        """创建缓存管理器"""
        if config is None:
            config = CacheConfig()
        
        return CacheManager(config)
    
    @staticmethod
    def create_from_dict(config_dict: Dict[str, Any]) -> CacheManager:
        """从字典创建缓存管理器"""
        # 这里可以实现从字典配置创建的逻辑
        config = CacheConfig()
        return CacheManager(config) 