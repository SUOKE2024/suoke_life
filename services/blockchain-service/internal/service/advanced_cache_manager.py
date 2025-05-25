#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
高级缓存管理器

该模块提供分层缓存、缓存预热、智能失效、压缩优化等高级缓存功能，
进一步提升系统性能和缓存效率。
"""

import asyncio
import json
import logging
import pickle
import time
import zlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import weakref

from internal.model.config import AppConfig
from internal.service.cache_service import CacheService, CacheKeyTypes


class CacheLevel(Enum):
    """缓存级别枚举"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DISK = "l3_disk"


class CacheStrategy(Enum):
    """缓存策略枚举"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


@dataclass
class CacheItem:
    """缓存项数据类"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: Optional[int] = None
    compressed: bool = False
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at
    
    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    @property
    def age_seconds(self) -> float:
        """获取缓存项年龄（秒）"""
        return (datetime.now() - self.created_at).total_seconds()
    
    def access(self):
        """记录访问"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class AdvancedCacheManager:
    """高级缓存管理器"""

    def __init__(self, config: AppConfig, cache_service: CacheService):
        """
        初始化高级缓存管理器
        
        Args:
            config: 应用配置对象
            cache_service: 基础缓存服务
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.cache_service = cache_service
        
        # L1内存缓存
        self.l1_cache: Dict[str, CacheItem] = {}
        self.l1_cache_lock = threading.RLock()
        
        # 缓存配置
        self.l1_max_size = 1000  # L1缓存最大项目数
        self.l1_max_memory_mb = 100  # L1缓存最大内存使用（MB）
        self.compression_threshold = 1024  # 压缩阈值（字节）
        self.cache_strategy = CacheStrategy.ADAPTIVE
        
        # 缓存统计
        self.stats = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "compressions": 0,
            "decompressions": 0,
            "evictions": 0,
            "preloads": 0
        }
        
        # 预热配置
        self.preload_patterns = []
        self.preload_enabled = True
        
        # 清理任务
        self.cleanup_interval = 300  # 5分钟
        self.cleanup_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        self.logger.info("高级缓存管理器初始化完成")
    
    async def start(self):
        """启动缓存管理器"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 启动清理任务
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # 执行缓存预热
        if self.preload_enabled:
            await self._preload_cache()
        
        self.logger.info("高级缓存管理器已启动")
    
    async def stop(self):
        """停止缓存管理器"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("高级缓存管理器已停止")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值（分层查找）
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值
        """
        # 1. 尝试从L1内存缓存获取
        l1_result = self._get_from_l1(key)
        if l1_result is not None:
            self.stats["l1_hits"] += 1
            return l1_result
        
        self.stats["l1_misses"] += 1
        
        # 2. 尝试从L2 Redis缓存获取
        l2_result = await self._get_from_l2(key)
        if l2_result is not None:
            self.stats["l2_hits"] += 1
            # 将结果放入L1缓存
            await self._set_to_l1(key, l2_result)
            return l2_result
        
        self.stats["l2_misses"] += 1
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_levels: List[CacheLevel] = None
    ) -> bool:
        """
        设置缓存值（多级存储）
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            cache_levels: 要存储的缓存级别
            
        Returns:
            是否设置成功
        """
        if cache_levels is None:
            cache_levels = [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]
        
        success = True
        
        # 存储到指定的缓存级别
        for level in cache_levels:
            if level == CacheLevel.L1_MEMORY:
                success &= await self._set_to_l1(key, value, ttl)
            elif level == CacheLevel.L2_REDIS:
                success &= await self._set_to_l2(key, value, ttl)
        
        return success
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存（所有级别）
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        l1_success = self._delete_from_l1(key)
        l2_success = await self._delete_from_l2(key)
        
        return l1_success or l2_success
    
    async def clear_level(self, level: CacheLevel) -> bool:
        """
        清空指定级别的缓存
        
        Args:
            level: 缓存级别
            
        Returns:
            是否清空成功
        """
        if level == CacheLevel.L1_MEMORY:
            return self._clear_l1()
        elif level == CacheLevel.L2_REDIS:
            return await self._clear_l2()
        
        return False
    
    def _get_from_l1(self, key: str) -> Any:
        """从L1内存缓存获取"""
        with self.l1_cache_lock:
            cache_item = self.l1_cache.get(key)
            if cache_item is None:
                return None
            
            # 检查是否过期
            if cache_item.is_expired:
                del self.l1_cache[key]
                return None
            
            # 记录访问
            cache_item.access()
            
            # 解压缩（如果需要）
            value = cache_item.value
            if cache_item.compressed:
                try:
                    value = pickle.loads(zlib.decompress(value))
                    self.stats["decompressions"] += 1
                except Exception as e:
                    self.logger.warning(f"解压缩失败: {str(e)}")
                    return None
            
            return value
    
    async def _get_from_l2(self, key: str) -> Any:
        """从L2 Redis缓存获取"""
        try:
            # 使用基础缓存服务
            parts = key.split(":", 2)
            if len(parts) >= 2:
                key_type = parts[0]
                identifier = parts[1]
                kwargs = {}
                if len(parts) > 2:
                    # 解析额外参数
                    try:
                        kwargs = json.loads(parts[2])
                    except:
                        pass
                
                return self.cache_service.get(key_type, identifier, **kwargs)
            
            return None
        except Exception as e:
            self.logger.warning(f"从L2缓存获取失败: {str(e)}")
            return None
    
    async def _set_to_l1(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置到L1内存缓存"""
        try:
            with self.l1_cache_lock:
                # 序列化和压缩
                serialized_value = value
                compressed = False
                size_bytes = 0
                
                if isinstance(value, (dict, list, tuple)):
                    serialized_value = pickle.dumps(value)
                    size_bytes = len(serialized_value)
                    
                    # 如果超过压缩阈值，进行压缩
                    if size_bytes > self.compression_threshold:
                        try:
                            compressed_value = zlib.compress(serialized_value)
                            if len(compressed_value) < size_bytes:
                                serialized_value = compressed_value
                                compressed = True
                                size_bytes = len(compressed_value)
                                self.stats["compressions"] += 1
                        except Exception as e:
                            self.logger.warning(f"压缩失败: {str(e)}")
                
                # 创建缓存项
                cache_item = CacheItem(
                    key=key,
                    value=serialized_value,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    ttl=ttl,
                    compressed=compressed,
                    size_bytes=size_bytes
                )
                
                # 检查是否需要清理空间
                if len(self.l1_cache) >= self.l1_max_size:
                    self._evict_l1_items()
                
                self.l1_cache[key] = cache_item
                return True
                
        except Exception as e:
            self.logger.warning(f"设置L1缓存失败: {str(e)}")
            return False
    
    async def _set_to_l2(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置到L2 Redis缓存"""
        try:
            # 使用基础缓存服务
            parts = key.split(":", 2)
            if len(parts) >= 2:
                key_type = parts[0]
                identifier = parts[1]
                kwargs = {}
                if len(parts) > 2:
                    try:
                        kwargs = json.loads(parts[2])
                    except:
                        pass
                
                return self.cache_service.set(key_type, identifier, value, ttl, **kwargs)
            
            return False
        except Exception as e:
            self.logger.warning(f"设置L2缓存失败: {str(e)}")
            return False
    
    def _delete_from_l1(self, key: str) -> bool:
        """从L1内存缓存删除"""
        with self.l1_cache_lock:
            if key in self.l1_cache:
                del self.l1_cache[key]
                return True
            return False
    
    async def _delete_from_l2(self, key: str) -> bool:
        """从L2 Redis缓存删除"""
        try:
            parts = key.split(":", 2)
            if len(parts) >= 2:
                key_type = parts[0]
                identifier = parts[1]
                kwargs = {}
                if len(parts) > 2:
                    try:
                        kwargs = json.loads(parts[2])
                    except:
                        pass
                
                return self.cache_service.delete(key_type, identifier, **kwargs)
            
            return False
        except Exception as e:
            self.logger.warning(f"从L2缓存删除失败: {str(e)}")
            return False
    
    def _clear_l1(self) -> bool:
        """清空L1内存缓存"""
        with self.l1_cache_lock:
            self.l1_cache.clear()
            return True
    
    async def _clear_l2(self) -> bool:
        """清空L2 Redis缓存"""
        return self.cache_service.clear_all()
    
    def _evict_l1_items(self):
        """清理L1缓存项"""
        if not self.l1_cache:
            return
        
        # 根据策略选择要清理的项目
        if self.cache_strategy == CacheStrategy.LRU:
            # 最近最少使用
            items_to_remove = sorted(
                self.l1_cache.items(),
                key=lambda x: x[1].last_accessed
            )[:len(self.l1_cache) // 4]  # 清理25%
        elif self.cache_strategy == CacheStrategy.LFU:
            # 最少使用频率
            items_to_remove = sorted(
                self.l1_cache.items(),
                key=lambda x: x[1].access_count
            )[:len(self.l1_cache) // 4]
        elif self.cache_strategy == CacheStrategy.TTL:
            # 按TTL清理
            items_to_remove = [
                (k, v) for k, v in self.l1_cache.items()
                if v.is_expired
            ]
        else:  # ADAPTIVE
            # 自适应策略：结合多个因素
            items_to_remove = sorted(
                self.l1_cache.items(),
                key=lambda x: (
                    x[1].access_count / max(x[1].age_seconds, 1),  # 访问频率/年龄
                    x[1].last_accessed
                )
            )[:len(self.l1_cache) // 4]
        
        # 删除选中的项目
        for key, _ in items_to_remove:
            if key in self.l1_cache:
                del self.l1_cache[key]
                self.stats["evictions"] += 1
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired_items()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"清理循环错误: {str(e)}")
    
    async def _cleanup_expired_items(self):
        """清理过期项目"""
        with self.l1_cache_lock:
            expired_keys = [
                key for key, item in self.l1_cache.items()
                if item.is_expired
            ]
            
            for key in expired_keys:
                del self.l1_cache[key]
            
            if expired_keys:
                self.logger.debug(f"清理了 {len(expired_keys)} 个过期的L1缓存项")
    
    async def _preload_cache(self):
        """缓存预热"""
        if not self.preload_patterns:
            return
        
        try:
            for pattern in self.preload_patterns:
                # 这里可以根据模式预加载常用数据
                # 例如：用户配置、常用查询结果等
                await self._preload_pattern(pattern)
                self.stats["preloads"] += 1
            
            self.logger.info(f"缓存预热完成，预加载了 {len(self.preload_patterns)} 个模式")
        except Exception as e:
            self.logger.error(f"缓存预热失败: {str(e)}")
    
    async def _preload_pattern(self, pattern: str):
        """预加载指定模式的数据"""
        # 这里可以实现具体的预加载逻辑
        # 例如：从数据库加载常用数据到缓存
        pass
    
    def add_preload_pattern(self, pattern: str):
        """添加预加载模式"""
        if pattern not in self.preload_patterns:
            self.preload_patterns.append(pattern)
    
    def remove_preload_pattern(self, pattern: str):
        """移除预加载模式"""
        if pattern in self.preload_patterns:
            self.preload_patterns.remove(pattern)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.l1_cache_lock:
            l1_size = len(self.l1_cache)
            l1_memory_usage = sum(item.size_bytes for item in self.l1_cache.values())
        
        # 计算命中率
        total_l1_requests = self.stats["l1_hits"] + self.stats["l1_misses"]
        total_l2_requests = self.stats["l2_hits"] + self.stats["l2_misses"]
        
        l1_hit_rate = self.stats["l1_hits"] / total_l1_requests if total_l1_requests > 0 else 0
        l2_hit_rate = self.stats["l2_hits"] / total_l2_requests if total_l2_requests > 0 else 0
        
        return {
            "l1_cache": {
                "size": l1_size,
                "max_size": self.l1_max_size,
                "memory_usage_bytes": l1_memory_usage,
                "memory_usage_mb": l1_memory_usage / (1024 * 1024),
                "hit_rate": l1_hit_rate
            },
            "l2_cache": {
                "hit_rate": l2_hit_rate
            },
            "stats": self.stats.copy(),
            "config": {
                "cache_strategy": self.cache_strategy.value,
                "compression_threshold": self.compression_threshold,
                "preload_enabled": self.preload_enabled,
                "preload_patterns": len(self.preload_patterns)
            }
        }
    
    def optimize_settings(self):
        """自动优化缓存设置"""
        stats = self.get_stats()
        
        # 根据命中率调整L1缓存大小
        l1_hit_rate = stats["l1_cache"]["hit_rate"]
        if l1_hit_rate < 0.5 and self.l1_max_size < 2000:
            self.l1_max_size = min(self.l1_max_size * 1.2, 2000)
            self.logger.info(f"增加L1缓存大小到 {self.l1_max_size}")
        elif l1_hit_rate > 0.9 and self.l1_max_size > 500:
            self.l1_max_size = max(self.l1_max_size * 0.8, 500)
            self.logger.info(f"减少L1缓存大小到 {self.l1_max_size}")
        
        # 根据压缩效果调整压缩阈值
        if self.stats["compressions"] > 0:
            compression_ratio = self.stats["compressions"] / (self.stats["compressions"] + self.stats["decompressions"])
            if compression_ratio > 0.8:
                self.compression_threshold = max(self.compression_threshold * 0.8, 512)
            elif compression_ratio < 0.2:
                self.compression_threshold = min(self.compression_threshold * 1.2, 4096)


# 缓存装饰器增强版
def advanced_cached(
    key_pattern: str,
    ttl: Optional[int] = None,
    cache_levels: List[CacheLevel] = None,
    compression: bool = True
):
    """
    高级缓存装饰器
    
    Args:
        key_pattern: 缓存键模式
        ttl: 过期时间（秒）
        cache_levels: 缓存级别
        compression: 是否启用压缩
    """
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # 检查是否有高级缓存管理器
            if not hasattr(self, 'advanced_cache_manager') or not self.advanced_cache_manager:
                return await func(self, *args, **kwargs)
            
            # 生成缓存键
            cache_key = key_pattern.format(*args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = await self.advanced_cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数
            result = await func(self, *args, **kwargs)
            
            # 缓存结果
            await self.advanced_cache_manager.set(
                cache_key, result, ttl, cache_levels
            )
            
            return result
        
        return wrapper
    return decorator 