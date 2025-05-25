#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能缓存管理器
提供多层缓存策略、自动过期管理、缓存预热和性能监控功能
支持内存缓存、Redis缓存、文件缓存等多种缓存后端
"""

import asyncio
import json
import logging
import pickle
import hashlib
import time
import threading
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import weakref
import gc
from collections import OrderedDict, defaultdict
import redis
import sqlite3
import aiofiles
import psutil

logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """缓存级别枚举"""
    L1_MEMORY = "l1_memory"         # L1内存缓存
    L2_REDIS = "l2_redis"           # L2 Redis缓存
    L3_FILE = "l3_file"             # L3文件缓存
    L4_DATABASE = "l4_database"     # L4数据库缓存

class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"                     # 最近最少使用
    LFU = "lfu"                     # 最少使用频率
    FIFO = "fifo"                   # 先进先出
    TTL = "ttl"                     # 基于时间
    ADAPTIVE = "adaptive"           # 自适应策略

class CacheStatus(Enum):
    """缓存状态枚举"""
    HIT = "hit"                     # 命中
    MISS = "miss"                   # 未命中
    EXPIRED = "expired"             # 已过期
    EVICTED = "evicted"             # 被驱逐

@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None       # 生存时间（秒）
    size: int = 0                   # 数据大小（字节）
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl
    
    def update_access(self):
        """更新访问信息"""
        self.last_accessed = datetime.now()
        self.access_count += 1

@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    total_size: int = 0
    avg_access_time: float = 0.0
    hit_rate: float = 0.0
    memory_usage: float = 0.0
    
    def update_hit_rate(self):
        """更新命中率"""
        if self.total_requests > 0:
            self.hit_rate = self.hits / self.total_requests

@dataclass
class CacheConfig:
    """缓存配置"""
    max_size: int = 1000            # 最大条目数
    max_memory: int = 100 * 1024 * 1024  # 最大内存（字节）
    default_ttl: int = 3600         # 默认TTL（秒）
    strategy: CacheStrategy = CacheStrategy.LRU
    enable_compression: bool = True
    enable_encryption: bool = False
    auto_cleanup: bool = True
    cleanup_interval: int = 300     # 清理间隔（秒）
    preload_patterns: List[str] = field(default_factory=list)

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """获取缓存项"""
        with self.lock:
            if key in self.cache:
                entry = self.cache.pop(key)
                self.cache[key] = entry  # 移到末尾
                entry.update_access()
                return entry
            return None
    
    def put(self, key: str, entry: CacheEntry):
        """存储缓存项"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # 移除最久未使用的项
                self.cache.popitem(last=False)
            
            self.cache[key] = entry
    
    def remove(self, key: str) -> bool:
        """移除缓存项"""
        with self.lock:
            return self.cache.pop(key, None) is not None
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def keys(self) -> List[str]:
        """获取所有键"""
        with self.lock:
            return list(self.cache.keys())

class IntelligentCacheManager:
    """智能缓存管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能缓存管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 缓存配置
        self.cache_config = CacheConfig(**config.get('cache_config', {}))
        self.enabled_levels = config.get('enabled_levels', [CacheLevel.L1_MEMORY])
        
        # Redis配置
        self.redis_config = config.get('redis_config', {})
        self.redis_client = None
        
        # 文件缓存配置
        self.file_cache_dir = config.get('file_cache_dir', 'cache/files')
        
        # 数据库缓存配置
        self.db_cache_path = config.get('db_cache_path', 'cache/cache.db')
        
        # 缓存层
        self.l1_cache = LRUCache(self.cache_config.max_size)
        self.cache_stats = {level: CacheStats() for level in CacheLevel}
        
        # 性能监控
        self.performance_monitor = {}
        self.access_patterns = defaultdict(list)
        
        # 后台任务
        self.cleanup_task = None
        self.preload_task = None
        self.monitor_task = None
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 初始化组件
        self._initialize_components()
        
        logger.info("智能缓存管理器初始化完成")
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化Redis连接
            if CacheLevel.L2_REDIS in self.enabled_levels:
                self._initialize_redis()
            
            # 初始化文件缓存目录
            if CacheLevel.L3_FILE in self.enabled_levels:
                Path(self.file_cache_dir).mkdir(parents=True, exist_ok=True)
            
            # 初始化数据库缓存
            if CacheLevel.L4_DATABASE in self.enabled_levels:
                self._initialize_database()
            
            # 启动后台任务
            self._start_background_tasks()
            
            logger.info("缓存组件初始化完成")
            
        except Exception as e:
            logger.error(f"缓存组件初始化失败: {e}")
            raise
    
    def _initialize_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_config.get('host', 'localhost'),
                port=self.redis_config.get('port', 6379),
                db=self.redis_config.get('db', 0),
                password=self.redis_config.get('password'),
                decode_responses=False,
                socket_timeout=self.redis_config.get('timeout', 5)
            )
            
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.warning(f"Redis连接初始化失败: {e}")
            self.redis_client = None
    
    def _initialize_database(self):
        """初始化数据库缓存"""
        try:
            # 创建缓存目录
            Path(self.db_cache_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 创建缓存表
            conn = sqlite3.connect(self.db_cache_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    created_at TIMESTAMP,
                    last_accessed TIMESTAMP,
                    access_count INTEGER,
                    ttl INTEGER,
                    size INTEGER,
                    metadata TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_last_accessed 
                ON cache_entries(last_accessed)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at 
                ON cache_entries(created_at)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("数据库缓存初始化成功")
            
        except Exception as e:
            logger.error(f"数据库缓存初始化失败: {e}")
            raise
    
    def _start_background_tasks(self):
        """启动后台任务"""
        if self.cache_config.auto_cleanup:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        if self.cache_config.preload_patterns:
            self.preload_task = asyncio.create_task(self._preload_loop())
        
        self.monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def get(
        self,
        key: str,
        default: Any = None,
        levels: Optional[List[CacheLevel]] = None
    ) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值
            levels: 指定缓存级别
            
        Returns:
            缓存值或默认值
        """
        start_time = time.time()
        
        try:
            if levels is None:
                levels = self.enabled_levels
            
            # 按级别顺序查找
            for level in levels:
                entry = await self._get_from_level(key, level)
                if entry and not entry.is_expired():
                    # 更新统计
                    self.cache_stats[level].hits += 1
                    self.cache_stats[level].total_requests += 1
                    self.cache_stats[level].update_hit_rate()
                    
                    # 记录访问模式
                    self._record_access_pattern(key, level)
                    
                    # 提升到更高级别缓存
                    await self._promote_to_higher_levels(key, entry, level, levels)
                    
                    # 更新性能监控
                    access_time = time.time() - start_time
                    self._update_performance_stats(level, access_time, True)
                    
                    return entry.value
                else:
                    # 缓存未命中
                    self.cache_stats[level].misses += 1
                    self.cache_stats[level].total_requests += 1
                    self.cache_stats[level].update_hit_rate()
            
            # 所有级别都未命中
            access_time = time.time() - start_time
            for level in levels:
                self._update_performance_stats(level, access_time, False)
            
            return default
            
        except Exception as e:
            logger.error(f"缓存获取失败: {key}, {e}")
            return default
    
    async def put(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        levels: Optional[List[CacheLevel]] = None
    ) -> bool:
        """
        存储缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            levels: 指定缓存级别
            
        Returns:
            是否成功
        """
        try:
            if levels is None:
                levels = self.enabled_levels
            
            if ttl is None:
                ttl = self.cache_config.default_ttl
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                ttl=ttl,
                size=self._calculate_size(value)
            )
            
            # 存储到各级别缓存
            success = True
            for level in levels:
                if not await self._put_to_level(key, entry, level):
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"缓存存储失败: {key}, {e}")
            return False
    
    async def remove(
        self,
        key: str,
        levels: Optional[List[CacheLevel]] = None
    ) -> bool:
        """
        移除缓存值
        
        Args:
            key: 缓存键
            levels: 指定缓存级别
            
        Returns:
            是否成功
        """
        try:
            if levels is None:
                levels = self.enabled_levels
            
            success = True
            for level in levels:
                if not await self._remove_from_level(key, level):
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"缓存移除失败: {key}, {e}")
            return False
    
    async def clear(self, levels: Optional[List[CacheLevel]] = None) -> bool:
        """
        清空缓存
        
        Args:
            levels: 指定缓存级别
            
        Returns:
            是否成功
        """
        try:
            if levels is None:
                levels = self.enabled_levels
            
            success = True
            for level in levels:
                if not await self._clear_level(level):
                    success = False
            
            return success
            
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
            return False
    
    async def _get_from_level(self, key: str, level: CacheLevel) -> Optional[CacheEntry]:
        """从指定级别获取缓存"""
        if level == CacheLevel.L1_MEMORY:
            return self.l1_cache.get(key)
        
        elif level == CacheLevel.L2_REDIS and self.redis_client:
            try:
                data = self.redis_client.get(f"cache:{key}")
                if data:
                    entry = pickle.loads(data)
                    return entry
            except Exception as e:
                logger.warning(f"Redis获取失败: {key}, {e}")
        
        elif level == CacheLevel.L3_FILE:
            try:
                file_path = Path(self.file_cache_dir) / f"{self._hash_key(key)}.cache"
                if file_path.exists():
                    async with aiofiles.open(file_path, 'rb') as f:
                        data = await f.read()
                        entry = pickle.loads(data)
                        return entry
            except Exception as e:
                logger.warning(f"文件缓存获取失败: {key}, {e}")
        
        elif level == CacheLevel.L4_DATABASE:
            try:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT value, created_at, last_accessed, access_count, ttl, size, metadata '
                    'FROM cache_entries WHERE key = ?',
                    (key,)
                )
                
                row = cursor.fetchone()
                if row:
                    value, created_at, last_accessed, access_count, ttl, size, metadata = row
                    entry = CacheEntry(
                        key=key,
                        value=pickle.loads(value),
                        created_at=datetime.fromisoformat(created_at),
                        last_accessed=datetime.fromisoformat(last_accessed),
                        access_count=access_count,
                        ttl=ttl,
                        size=size,
                        metadata=json.loads(metadata) if metadata else {}
                    )
                    
                    # 更新访问时间
                    cursor.execute(
                        'UPDATE cache_entries SET last_accessed = ?, access_count = ? WHERE key = ?',
                        (datetime.now().isoformat(), access_count + 1, key)
                    )
                    conn.commit()
                    conn.close()
                    
                    return entry
                
                conn.close()
                
            except Exception as e:
                logger.warning(f"数据库缓存获取失败: {key}, {e}")
        
        return None
    
    async def _put_to_level(self, key: str, entry: CacheEntry, level: CacheLevel) -> bool:
        """存储到指定级别"""
        try:
            if level == CacheLevel.L1_MEMORY:
                self.l1_cache.put(key, entry)
                return True
            
            elif level == CacheLevel.L2_REDIS and self.redis_client:
                data = pickle.dumps(entry)
                self.redis_client.setex(
                    f"cache:{key}",
                    entry.ttl or self.cache_config.default_ttl,
                    data
                )
                return True
            
            elif level == CacheLevel.L3_FILE:
                file_path = Path(self.file_cache_dir) / f"{self._hash_key(key)}.cache"
                data = pickle.dumps(entry)
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(data)
                return True
            
            elif level == CacheLevel.L4_DATABASE:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_entries 
                    (key, value, created_at, last_accessed, access_count, ttl, size, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key,
                    pickle.dumps(entry.value),
                    entry.created_at.isoformat(),
                    entry.last_accessed.isoformat(),
                    entry.access_count,
                    entry.ttl,
                    entry.size,
                    json.dumps(entry.metadata)
                ))
                
                conn.commit()
                conn.close()
                return True
            
        except Exception as e:
            logger.error(f"存储到{level}失败: {key}, {e}")
            return False
        
        return False
    
    async def _remove_from_level(self, key: str, level: CacheLevel) -> bool:
        """从指定级别移除缓存"""
        try:
            if level == CacheLevel.L1_MEMORY:
                return self.l1_cache.remove(key)
            
            elif level == CacheLevel.L2_REDIS and self.redis_client:
                return bool(self.redis_client.delete(f"cache:{key}"))
            
            elif level == CacheLevel.L3_FILE:
                file_path = Path(self.file_cache_dir) / f"{self._hash_key(key)}.cache"
                if file_path.exists():
                    file_path.unlink()
                    return True
                return False
            
            elif level == CacheLevel.L4_DATABASE:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
                affected = cursor.rowcount > 0
                
                conn.commit()
                conn.close()
                return affected
            
        except Exception as e:
            logger.error(f"从{level}移除失败: {key}, {e}")
            return False
        
        return False
    
    async def _clear_level(self, level: CacheLevel) -> bool:
        """清空指定级别缓存"""
        try:
            if level == CacheLevel.L1_MEMORY:
                self.l1_cache.clear()
                return True
            
            elif level == CacheLevel.L2_REDIS and self.redis_client:
                keys = self.redis_client.keys("cache:*")
                if keys:
                    self.redis_client.delete(*keys)
                return True
            
            elif level == CacheLevel.L3_FILE:
                cache_files = Path(self.file_cache_dir).glob("*.cache")
                for file_path in cache_files:
                    file_path.unlink()
                return True
            
            elif level == CacheLevel.L4_DATABASE:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM cache_entries')
                
                conn.commit()
                conn.close()
                return True
            
        except Exception as e:
            logger.error(f"清空{level}失败: {e}")
            return False
        
        return False
    
    async def _promote_to_higher_levels(
        self,
        key: str,
        entry: CacheEntry,
        current_level: CacheLevel,
        enabled_levels: List[CacheLevel]
    ):
        """提升到更高级别缓存"""
        try:
            level_priority = {
                CacheLevel.L1_MEMORY: 1,
                CacheLevel.L2_REDIS: 2,
                CacheLevel.L3_FILE: 3,
                CacheLevel.L4_DATABASE: 4
            }
            
            current_priority = level_priority[current_level]
            
            for level in enabled_levels:
                if level_priority[level] < current_priority:
                    await self._put_to_level(key, entry, level)
                    
        except Exception as e:
            logger.warning(f"缓存提升失败: {key}, {e}")
    
    def _record_access_pattern(self, key: str, level: CacheLevel):
        """记录访问模式"""
        pattern = {
            'timestamp': datetime.now(),
            'level': level,
            'key_hash': self._hash_key(key)[:8]  # 只记录哈希前缀保护隐私
        }
        
        self.access_patterns[key].append(pattern)
        
        # 限制记录数量
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key] = self.access_patterns[key][-50:]
    
    def _update_performance_stats(self, level: CacheLevel, access_time: float, hit: bool):
        """更新性能统计"""
        if level not in self.performance_monitor:
            self.performance_monitor[level] = {
                'total_time': 0.0,
                'total_requests': 0,
                'avg_time': 0.0
            }
        
        stats = self.performance_monitor[level]
        stats['total_time'] += access_time
        stats['total_requests'] += 1
        stats['avg_time'] = stats['total_time'] / stats['total_requests']
        
        # 更新缓存统计
        cache_stats = self.cache_stats[level]
        cache_stats.avg_access_time = stats['avg_time']
    
    def _calculate_size(self, value: Any) -> int:
        """计算数据大小"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return 0
    
    def _hash_key(self, key: str) -> str:
        """生成键的哈希值"""
        return hashlib.md5(key.encode()).hexdigest()
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(self.cache_config.cleanup_interval)
                await self._cleanup_expired_entries()
                await self._cleanup_memory_pressure()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")
    
    async def _cleanup_expired_entries(self):
        """清理过期条目"""
        try:
            # 清理L1内存缓存
            expired_keys = []
            for key in self.l1_cache.keys():
                entry = self.l1_cache.get(key)
                if entry and entry.is_expired():
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.l1_cache.remove(key)
                self.cache_stats[CacheLevel.L1_MEMORY].evictions += 1
            
            # 清理数据库缓存
            if CacheLevel.L4_DATABASE in self.enabled_levels:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM cache_entries 
                    WHERE ttl IS NOT NULL 
                    AND (julianday('now') - julianday(created_at)) * 86400 > ttl
                ''')
                
                evicted = cursor.rowcount
                self.cache_stats[CacheLevel.L4_DATABASE].evictions += evicted
                
                conn.commit()
                conn.close()
            
            logger.debug(f"清理过期条目完成，L1: {len(expired_keys)}")
            
        except Exception as e:
            logger.error(f"清理过期条目失败: {e}")
    
    async def _cleanup_memory_pressure(self):
        """内存压力清理"""
        try:
            # 检查系统内存使用率
            memory_percent = psutil.virtual_memory().percent
            
            if memory_percent > 85:  # 内存使用率超过85%
                # 清理L1缓存中最久未使用的条目
                cache_size = self.l1_cache.size()
                target_size = int(cache_size * 0.7)  # 清理30%
                
                # 获取所有条目并按最后访问时间排序
                entries = []
                for key in self.l1_cache.keys():
                    entry = self.l1_cache.get(key)
                    if entry:
                        entries.append((key, entry.last_accessed))
                
                entries.sort(key=lambda x: x[1])  # 按时间升序排序
                
                # 移除最久未使用的条目
                for i in range(min(len(entries), cache_size - target_size)):
                    key = entries[i][0]
                    self.l1_cache.remove(key)
                    self.cache_stats[CacheLevel.L1_MEMORY].evictions += 1
                
                logger.info(f"内存压力清理完成，移除 {cache_size - target_size} 个条目")
            
        except Exception as e:
            logger.error(f"内存压力清理失败: {e}")
    
    async def _preload_loop(self):
        """预加载循环"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次
                await self._preload_cache()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"预加载循环错误: {e}")
    
    async def _preload_cache(self):
        """预加载缓存"""
        try:
            # 基于访问模式预加载热点数据
            hot_keys = self._identify_hot_keys()
            
            for key in hot_keys:
                # 检查是否已在L1缓存中
                if not self.l1_cache.get(key):
                    # 尝试从低级别缓存加载到高级别
                    for level in reversed(self.enabled_levels):
                        entry = await self._get_from_level(key, level)
                        if entry and not entry.is_expired():
                            await self._put_to_level(key, entry, CacheLevel.L1_MEMORY)
                            break
            
            logger.debug(f"预加载完成，处理 {len(hot_keys)} 个热点键")
            
        except Exception as e:
            logger.error(f"预加载失败: {e}")
    
    def _identify_hot_keys(self) -> List[str]:
        """识别热点键"""
        key_scores = {}
        
        for key, patterns in self.access_patterns.items():
            if not patterns:
                continue
            
            # 计算访问频率
            recent_accesses = [
                p for p in patterns 
                if (datetime.now() - p['timestamp']).total_seconds() < 3600
            ]
            
            frequency_score = len(recent_accesses)
            
            # 计算访问级别权重（L1访问权重更高）
            level_score = sum(
                4 - list(CacheLevel).index(p['level']) 
                for p in recent_accesses
            )
            
            key_scores[key] = frequency_score + level_score * 0.1
        
        # 返回评分最高的键
        sorted_keys = sorted(key_scores.items(), key=lambda x: x[1], reverse=True)
        return [key for key, score in sorted_keys[:50]]  # 返回前50个热点键
    
    async def _monitor_loop(self):
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟更新一次
                await self._update_monitoring_stats()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
    
    async def _update_monitoring_stats(self):
        """更新监控统计"""
        try:
            # 更新内存使用情况
            for level in self.enabled_levels:
                if level == CacheLevel.L1_MEMORY:
                    total_size = sum(
                        entry.size for entry in self.l1_cache.cache.values()
                    )
                    self.cache_stats[level].total_size = total_size
                    self.cache_stats[level].memory_usage = (
                        total_size / self.cache_config.max_memory * 100
                    )
            
            # 记录统计日志
            for level, stats in self.cache_stats.items():
                if stats.total_requests > 0:
                    logger.debug(
                        f"{level.value}: 命中率={stats.hit_rate:.2%}, "
                        f"请求数={stats.total_requests}, "
                        f"平均访问时间={stats.avg_access_time:.3f}ms"
                    )
            
        except Exception as e:
            logger.error(f"监控统计更新失败: {e}")
    
    async def get_cache_stats(self) -> Dict[str, CacheStats]:
        """获取缓存统计"""
        return self.cache_stats.copy()
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return {
            'cache_stats': self.cache_stats,
            'performance_monitor': self.performance_monitor,
            'access_patterns_count': {
                key: len(patterns) 
                for key, patterns in self.access_patterns.items()
            },
            'system_memory': psutil.virtual_memory().percent,
            'cache_sizes': {
                level.value: await self._get_cache_size(level)
                for level in self.enabled_levels
            }
        }
    
    async def _get_cache_size(self, level: CacheLevel) -> int:
        """获取指定级别缓存大小"""
        try:
            if level == CacheLevel.L1_MEMORY:
                return self.l1_cache.size()
            
            elif level == CacheLevel.L2_REDIS and self.redis_client:
                keys = self.redis_client.keys("cache:*")
                return len(keys)
            
            elif level == CacheLevel.L3_FILE:
                cache_files = list(Path(self.file_cache_dir).glob("*.cache"))
                return len(cache_files)
            
            elif level == CacheLevel.L4_DATABASE:
                conn = sqlite3.connect(self.db_cache_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM cache_entries')
                count = cursor.fetchone()[0]
                conn.close()
                return count
            
        except Exception as e:
            logger.error(f"获取{level}缓存大小失败: {e}")
            return 0
        
        return 0
    
    async def optimize_cache(self):
        """优化缓存"""
        try:
            # 分析访问模式
            hot_keys = self._identify_hot_keys()
            
            # 调整缓存策略
            if len(hot_keys) > self.cache_config.max_size * 0.8:
                # 热点数据过多，增加缓存大小或调整策略
                logger.info("检测到大量热点数据，建议增加缓存大小")
            
            # 清理冷数据
            await self._cleanup_cold_data()
            
            # 预加载热点数据
            await self._preload_cache()
            
            logger.info("缓存优化完成")
            
        except Exception as e:
            logger.error(f"缓存优化失败: {e}")
    
    async def _cleanup_cold_data(self):
        """清理冷数据"""
        try:
            # 识别冷数据（长时间未访问）
            cold_threshold = datetime.now() - timedelta(hours=24)
            cold_keys = []
            
            for key in self.l1_cache.keys():
                entry = self.l1_cache.get(key)
                if entry and entry.last_accessed < cold_threshold:
                    cold_keys.append(key)
            
            # 移除冷数据
            for key in cold_keys:
                self.l1_cache.remove(key)
                self.cache_stats[CacheLevel.L1_MEMORY].evictions += 1
            
            logger.debug(f"清理冷数据完成，移除 {len(cold_keys)} 个条目")
            
        except Exception as e:
            logger.error(f"清理冷数据失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        # 取消后台任务
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.preload_task:
            self.preload_task.cancel()
        if self.monitor_task:
            self.monitor_task.cancel()
        
        # 关闭Redis连接
        if self.redis_client:
            self.redis_client.close()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        # 清理内存
        self.l1_cache.clear()
        self.access_patterns.clear()
        
        logger.info("智能缓存管理器资源清理完成") 