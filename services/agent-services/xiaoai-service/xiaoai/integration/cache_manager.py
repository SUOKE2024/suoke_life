#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器
提供高性能的内存缓存，减少重复计算和I/O操作
"""

import asyncio
import time
import logging
import hashlib
import json
from typing import Dict, Any, Optional, Union, Callable
from dataclasses import dataclass
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    created_at: float
    expires_at: Optional[float] = None
    access_count: int = 0
    last_accessed: float = 0.0

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            
            # 检查是否过期
            if entry.expires_at and time.time() > entry.expires_at:
                del self.cache[key]
                return None
            
            # 更新访问信息
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # 移动到末尾（最近使用）
            self.cache.move_to_end(key)
            
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """设置缓存值"""
        with self.lock:
            now = time.time()
            expires_at = now + ttl if ttl else None
            
            entry = CacheEntry(
                value=value,
                created_at=now,
                expires_at=expires_at,
                access_count=1,
                last_accessed=now
            )
            
            self.cache[key] = entry
            self.cache.move_to_end(key)
            
            # 检查大小限制
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
    
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def cleanup_expired(self):
        """清理过期条目"""
        with self.lock:
            now = time.time()
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.expires_at and now > entry.expires_at
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 不同类型的缓存
        self.device_cache = LRUCache(max_size=self.config.get('device_cache_size', 100))
        self.image_cache = LRUCache(max_size=self.config.get('image_cache_size', 50))
        self.audio_cache = LRUCache(max_size=self.config.get('audio_cache_size', 30))
        self.result_cache = LRUCache(max_size=self.config.get('result_cache_size', 200))
        self.session_cache = LRUCache(max_size=self.config.get('session_cache_size', 500))
        
        # 默认TTL设置
        self.default_ttl = {
            'device_status': 30.0,      # 设备状态缓存30秒
            'image_analysis': 300.0,    # 图像分析缓存5分钟
            'audio_recognition': 300.0, # 语音识别缓存5分钟
            'accessibility': 600.0,     # 无障碍结果缓存10分钟
            'session': 3600.0,          # 会话缓存1小时
        }
        
        # 启动清理任务
        self.cleanup_task = None
        self.start_cleanup_task()
        
        logger.info("缓存管理器初始化完成")
    
    def start_cleanup_task(self):
        """启动定期清理任务"""
        async def cleanup_worker():
            while True:
                try:
                    await asyncio.sleep(60)  # 每分钟清理一次
                    
                    total_cleaned = 0
                    total_cleaned += self.device_cache.cleanup_expired()
                    total_cleaned += self.image_cache.cleanup_expired()
                    total_cleaned += self.audio_cache.cleanup_expired()
                    total_cleaned += self.result_cache.cleanup_expired()
                    total_cleaned += self.session_cache.cleanup_expired()
                    
                    if total_cleaned > 0:
                        logger.debug(f"清理了 {total_cleaned} 个过期缓存条目")
                        
                except Exception as e:
                    logger.error(f"缓存清理任务错误: {e}")
        
        self.cleanup_task = asyncio.create_task(cleanup_worker())
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 创建唯一键
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()[:16]
        
        return f"{prefix}:{key_hash}"
    
    # 设备状态缓存
    def get_device_status(self, device_type: str) -> Optional[Dict[str, Any]]:
        """获取设备状态缓存"""
        key = self._generate_key("device_status", device_type)
        return self.device_cache.get(key)
    
    def set_device_status(self, device_type: str, status: Dict[str, Any], ttl: Optional[float] = None):
        """设置设备状态缓存"""
        key = self._generate_key("device_status", device_type)
        ttl = ttl or self.default_ttl['device_status']
        self.device_cache.set(key, status, ttl)
    
    # 图像处理缓存
    def get_image_analysis(self, image_hash: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """获取图像分析缓存"""
        key = self._generate_key("image_analysis", image_hash, analysis_type)
        return self.image_cache.get(key)
    
    def set_image_analysis(self, image_hash: str, analysis_type: str, result: Dict[str, Any], ttl: Optional[float] = None):
        """设置图像分析缓存"""
        key = self._generate_key("image_analysis", image_hash, analysis_type)
        ttl = ttl or self.default_ttl['image_analysis']
        self.image_cache.set(key, result, ttl)
    
    # 音频处理缓存
    def get_audio_recognition(self, audio_hash: str, language: str) -> Optional[Dict[str, Any]]:
        """获取语音识别缓存"""
        key = self._generate_key("audio_recognition", audio_hash, language)
        return self.audio_cache.get(key)
    
    def set_audio_recognition(self, audio_hash: str, language: str, result: Dict[str, Any], ttl: Optional[float] = None):
        """设置语音识别缓存"""
        key = self._generate_key("audio_recognition", audio_hash, language)
        ttl = ttl or self.default_ttl['audio_recognition']
        self.audio_cache.set(key, result, ttl)
    
    # 无障碍服务缓存
    def get_accessibility_result(self, content_hash: str, service_type: str) -> Optional[Dict[str, Any]]:
        """获取无障碍服务结果缓存"""
        key = self._generate_key("accessibility", content_hash, service_type)
        return self.result_cache.get(key)
    
    def set_accessibility_result(self, content_hash: str, service_type: str, result: Dict[str, Any], ttl: Optional[float] = None):
        """设置无障碍服务结果缓存"""
        key = self._generate_key("accessibility", content_hash, service_type)
        ttl = ttl or self.default_ttl['accessibility']
        self.result_cache.set(key, result, ttl)
    
    # 会话缓存
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话缓存"""
        key = self._generate_key("session", session_id)
        return self.session_cache.get(key)
    
    def set_session(self, session_id: str, session_data: Dict[str, Any], ttl: Optional[float] = None):
        """设置会话缓存"""
        key = self._generate_key("session", session_id)
        ttl = ttl or self.default_ttl['session']
        self.session_cache.set(key, session_data, ttl)
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话缓存"""
        key = self._generate_key("session", session_id)
        return self.session_cache.delete(key)
    
    # 通用缓存方法
    def cache_result(self, cache_type: str, key_parts: tuple, result: Any, ttl: Optional[float] = None):
        """通用缓存结果方法"""
        cache_map = {
            'device': self.device_cache,
            'image': self.image_cache,
            'audio': self.audio_cache,
            'result': self.result_cache,
            'session': self.session_cache
        }
        
        cache = cache_map.get(cache_type, self.result_cache)
        key = self._generate_key(cache_type, *key_parts)
        cache.set(key, result, ttl)
    
    def get_cached_result(self, cache_type: str, key_parts: tuple) -> Optional[Any]:
        """通用获取缓存结果方法"""
        cache_map = {
            'device': self.device_cache,
            'image': self.image_cache,
            'audio': self.audio_cache,
            'result': self.result_cache,
            'session': self.session_cache
        }
        
        cache = cache_map.get(cache_type, self.result_cache)
        key = self._generate_key(cache_type, *key_parts)
        return cache.get(key)
    
    # 缓存装饰器
    def cached(self, cache_type: str = 'result', ttl: Optional[float] = None, key_func: Optional[Callable] = None):
        """缓存装饰器"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cache_key_parts = key_func(*args, **kwargs)
                else:
                    cache_key_parts = (func.__name__, args, tuple(sorted(kwargs.items())))
                
                # 尝试从缓存获取
                cached_result = self.get_cached_result(cache_type, cache_key_parts)
                if cached_result is not None:
                    logger.debug(f"缓存命中: {func.__name__}")
                    return cached_result
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                self.cache_result(cache_type, cache_key_parts, result, ttl)
                logger.debug(f"缓存存储: {func.__name__}")
                
                return result
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'device_cache': {
                'size': self.device_cache.size(),
                'max_size': self.device_cache.max_size
            },
            'image_cache': {
                'size': self.image_cache.size(),
                'max_size': self.image_cache.max_size
            },
            'audio_cache': {
                'size': self.audio_cache.size(),
                'max_size': self.audio_cache.max_size
            },
            'result_cache': {
                'size': self.result_cache.size(),
                'max_size': self.result_cache.max_size
            },
            'session_cache': {
                'size': self.session_cache.size(),
                'max_size': self.session_cache.max_size
            }
        }
    
    def clear_all(self):
        """清空所有缓存"""
        self.device_cache.clear()
        self.image_cache.clear()
        self.audio_cache.clear()
        self.result_cache.clear()
        self.session_cache.clear()
        logger.info("所有缓存已清空")
    
    async def close(self):
        """关闭缓存管理器"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        self.clear_all()
        logger.info("缓存管理器已关闭")

# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager(config: Dict[str, Any] = None) -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager(config)
    
    return _cache_manager

async def close_cache_manager():
    """关闭缓存管理器"""
    global _cache_manager
    
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None 