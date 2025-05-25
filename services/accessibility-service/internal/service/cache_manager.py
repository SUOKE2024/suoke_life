#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
缓存管理器 - 支持多级缓存和智能过期策略
"""

import logging
import asyncio
import time
import json
import hashlib
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
import pickle
import weakref

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """缓存级别"""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


@dataclass
class CacheItem:
    """缓存项"""
    key: str
    value: Any
    created_at: float
    ttl: int
    access_count: int = 0
    last_accessed: float = None
    size: int = 0


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        cache_config = config.get('cache', {})
        
        # 内存缓存配置
        self._memory_cache: Dict[str, CacheItem] = {}
        self._memory_max_size = cache_config.get('memory_max_size_mb', 256) * 1024 * 1024
        self._memory_max_items = cache_config.get('memory_max_items', 10000)
        
        # Redis缓存配置
        self._redis_enabled = cache_config.get('redis_enabled', False)
        self._redis_client = None
        
        # 磁盘缓存配置
        self._disk_enabled = cache_config.get('disk_enabled', False)
        self._disk_cache_dir = cache_config.get('disk_cache_dir', '/tmp/accessibility_cache')
        
        # 清理配置
        self._cleanup_interval = cache_config.get('cleanup_interval_seconds', 300)
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # 统计信息
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        
        self._lock = asyncio.Lock()
        
        # 初始化缓存
        asyncio.create_task(self._initialize())
    
    async def _initialize(self):
        """初始化缓存管理器"""
        try:
            # 初始化Redis连接
            if self._redis_enabled:
                await self._init_redis()
            
            # 初始化磁盘缓存
            if self._disk_enabled:
                await self._init_disk_cache()
            
            # 启动清理任务
            self._start_cleanup_task()
            
            logger.info("缓存管理器初始化完成")
            
        except Exception as e:
            logger.error(f"缓存管理器初始化失败: {str(e)}")
    
    async def _init_redis(self):
        """初始化Redis连接"""
        try:
            import redis.asyncio as redis
            
            redis_config = self.config.get('redis', {})
            self._redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                decode_responses=False
            )
            
            # 测试连接
            await self._redis_client.ping()
            logger.info("Redis缓存连接成功")
            
        except Exception as e:
            logger.warning(f"Redis缓存初始化失败: {str(e)}, 禁用Redis缓存")
            self._redis_enabled = False
            self._redis_client = None
    
    async def _init_disk_cache(self):
        """初始化磁盘缓存"""
        try:
            import os
            
            if not os.path.exists(self._disk_cache_dir):
                os.makedirs(self._disk_cache_dir, exist_ok=True)
            
            logger.info(f"磁盘缓存目录: {self._disk_cache_dir}")
            
        except Exception as e:
            logger.warning(f"磁盘缓存初始化失败: {str(e)}, 禁用磁盘缓存")
            self._disk_enabled = False
    
    def _start_cleanup_task(self):
        """启动清理任务"""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self._cleanup_interval)
                    await self._cleanup_expired_items()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"缓存清理任务异常: {str(e)}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在返回None
        """
        try:
            # 首先尝试内存缓存
            value = await self._get_from_memory(key)
            if value is not None:
                self._stats['hits'] += 1
                return value
            
            # 尝试Redis缓存
            if self._redis_enabled:
                value = await self._get_from_redis(key)
                if value is not None:
                    # 回写到内存缓存
                    await self._set_to_memory(key, value, ttl=3600)
                    self._stats['hits'] += 1
                    return value
            
            # 尝试磁盘缓存
            if self._disk_enabled:
                value = await self._get_from_disk(key)
                if value is not None:
                    # 回写到内存缓存
                    await self._set_to_memory(key, value, ttl=3600)
                    self._stats['hits'] += 1
                    return value
            
            self._stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {key}, 错误: {str(e)}")
            self._stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        try:
            success = True
            
            # 设置到内存缓存
            await self._set_to_memory(key, value, ttl)
            
            # 设置到Redis缓存
            if self._redis_enabled:
                redis_success = await self._set_to_redis(key, value, ttl)
                success = success and redis_success
            
            # 设置到磁盘缓存（仅对大对象）
            if self._disk_enabled and self._should_cache_to_disk(value):
                disk_success = await self._set_to_disk(key, value, ttl)
                success = success and disk_success
            
            if success:
                self._stats['sets'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"设置缓存失败: {key}, 错误: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        try:
            success = True
            
            # 从内存缓存删除
            await self._delete_from_memory(key)
            
            # 从Redis缓存删除
            if self._redis_enabled:
                redis_success = await self._delete_from_redis(key)
                success = success and redis_success
            
            # 从磁盘缓存删除
            if self._disk_enabled:
                disk_success = await self._delete_from_disk(key)
                success = success and disk_success
            
            if success:
                self._stats['deletes'] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"删除缓存失败: {key}, 错误: {str(e)}")
            return False
    
    async def _get_from_memory(self, key: str) -> Optional[Any]:
        """从内存缓存获取"""
        async with self._lock:
            if key in self._memory_cache:
                item = self._memory_cache[key]
                
                # 检查是否过期
                if self._is_expired(item):
                    del self._memory_cache[key]
                    return None
                
                # 更新访问信息
                item.access_count += 1
                item.last_accessed = time.time()
                
                return item.value
            
            return None
    
    async def _set_to_memory(self, key: str, value: Any, ttl: int):
        """设置到内存缓存"""
        async with self._lock:
            # 检查是否需要清理空间
            await self._ensure_memory_space()
            
            # 计算值的大小
            size = self._calculate_size(value)
            
            # 创建缓存项
            item = CacheItem(
                key=key,
                value=value,
                created_at=time.time(),
                ttl=ttl,
                last_accessed=time.time(),
                size=size
            )
            
            self._memory_cache[key] = item
    
    async def _delete_from_memory(self, key: str):
        """从内存缓存删除"""
        async with self._lock:
            if key in self._memory_cache:
                del self._memory_cache[key]
    
    async def _get_from_redis(self, key: str) -> Optional[Any]:
        """从Redis缓存获取"""
        if not self._redis_client:
            return None
        
        try:
            data = await self._redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logger.error(f"Redis获取失败: {key}, 错误: {str(e)}")
            return None
    
    async def _set_to_redis(self, key: str, value: Any, ttl: int) -> bool:
        """设置到Redis缓存"""
        if not self._redis_client:
            return False
        
        try:
            data = pickle.dumps(value)
            await self._redis_client.setex(key, ttl, data)
            return True
        except Exception as e:
            logger.error(f"Redis设置失败: {key}, 错误: {str(e)}")
            return False
    
    async def _delete_from_redis(self, key: str) -> bool:
        """从Redis缓存删除"""
        if not self._redis_client:
            return False
        
        try:
            await self._redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis删除失败: {key}, 错误: {str(e)}")
            return False
    
    async def _get_from_disk(self, key: str) -> Optional[Any]:
        """从磁盘缓存获取"""
        if not self._disk_enabled:
            return None
        
        try:
            import os
            
            file_path = self._get_disk_cache_path(key)
            if not os.path.exists(file_path):
                return None
            
            # 检查文件是否过期
            stat = os.stat(file_path)
            if time.time() - stat.st_mtime > 3600:  # 1小时过期
                os.remove(file_path)
                return None
            
            with open(file_path, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            logger.error(f"磁盘缓存获取失败: {key}, 错误: {str(e)}")
            return None
    
    async def _set_to_disk(self, key: str, value: Any, ttl: int) -> bool:
        """设置到磁盘缓存"""
        if not self._disk_enabled:
            return False
        
        try:
            file_path = self._get_disk_cache_path(key)
            
            # 在线程池中执行磁盘IO
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._write_disk_cache(file_path, value)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"磁盘缓存设置失败: {key}, 错误: {str(e)}")
            return False
    
    async def _delete_from_disk(self, key: str) -> bool:
        """从磁盘缓存删除"""
        if not self._disk_enabled:
            return False
        
        try:
            import os
            
            file_path = self._get_disk_cache_path(key)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"磁盘缓存删除失败: {key}, 错误: {str(e)}")
            return False
    
    def _get_disk_cache_path(self, key: str) -> str:
        """获取磁盘缓存文件路径"""
        import os
        
        # 使用MD5哈希作为文件名
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._disk_cache_dir, f"{hash_key}.cache")
    
    def _write_disk_cache(self, file_path: str, value: Any):
        """写入磁盘缓存"""
        import os
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            pickle.dump(value, f)
    
    def _should_cache_to_disk(self, value: Any) -> bool:
        """判断是否应该缓存到磁盘"""
        # 只有大对象才缓存到磁盘
        size = self._calculate_size(value)
        return size > 1024 * 1024  # 1MB
    
    def _calculate_size(self, value: Any) -> int:
        """计算值的大小"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return 1024  # 默认1KB
    
    def _is_expired(self, item: CacheItem) -> bool:
        """检查缓存项是否过期"""
        return time.time() - item.created_at > item.ttl
    
    async def _ensure_memory_space(self):
        """确保内存缓存有足够空间"""
        # 检查项目数量
        if len(self._memory_cache) >= self._memory_max_items:
            await self._evict_memory_items(count=self._memory_max_items // 10)
        
        # 检查内存使用
        total_size = sum(item.size for item in self._memory_cache.values())
        if total_size > self._memory_max_size:
            await self._evict_memory_items(target_size=self._memory_max_size * 0.8)
    
    async def _evict_memory_items(self, count: int = None, target_size: float = None):
        """清理内存缓存项"""
        if not self._memory_cache:
            return
        
        # 按LRU策略排序
        items = list(self._memory_cache.values())
        items.sort(key=lambda x: x.last_accessed or x.created_at)
        
        evicted = 0
        current_size = sum(item.size for item in self._memory_cache.values())
        
        for item in items:
            if count and evicted >= count:
                break
            if target_size and current_size <= target_size:
                break
            
            del self._memory_cache[item.key]
            current_size -= item.size
            evicted += 1
            self._stats['evictions'] += 1
        
        if evicted > 0:
            logger.debug(f"清理内存缓存项: {evicted}个")
    
    async def _cleanup_expired_items(self):
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = []
        
        async with self._lock:
            for key, item in self._memory_cache.items():
                if self._is_expired(item):
                    expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            logger.debug(f"清理过期缓存项: {len(expired_keys)}个")
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        memory_size = sum(item.size for item in self._memory_cache.values())
        
        return {
            'memory': {
                'items': len(self._memory_cache),
                'size_mb': memory_size / 1024 / 1024,
                'max_items': self._memory_max_items,
                'max_size_mb': self._memory_max_size / 1024 / 1024
            },
            'redis': {
                'enabled': self._redis_enabled,
                'connected': self._redis_client is not None
            },
            'disk': {
                'enabled': self._disk_enabled,
                'cache_dir': self._disk_cache_dir if self._disk_enabled else None
            },
            'stats': self._stats.copy(),
            'hit_rate': self._stats['hits'] / (self._stats['hits'] + self._stats['misses']) if (self._stats['hits'] + self._stats['misses']) > 0 else 0
        }
    
    async def clear(self):
        """清空所有缓存"""
        async with self._lock:
            self._memory_cache.clear()
        
        if self._redis_enabled and self._redis_client:
            try:
                await self._redis_client.flushdb()
            except Exception as e:
                logger.error(f"清空Redis缓存失败: {str(e)}")
        
        if self._disk_enabled:
            try:
                import os
                import shutil
                
                if os.path.exists(self._disk_cache_dir):
                    shutil.rmtree(self._disk_cache_dir)
                    os.makedirs(self._disk_cache_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"清空磁盘缓存失败: {str(e)}")
        
        logger.info("缓存已清空")
    
    async def cleanup(self):
        """清理资源"""
        logger.info("开始清理缓存管理器")
        
        # 停止清理任务
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 关闭Redis连接
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception as e:
                logger.error(f"关闭Redis连接失败: {str(e)}")
        
        # 清空内存缓存
        self._memory_cache.clear()
        
        logger.info("缓存管理器清理完成") 