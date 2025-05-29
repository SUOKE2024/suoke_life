#!/usr/bin/env python3
"""
缓存管理器
Cache Manager

提供多层次的缓存管理功能，支持设备状态、图像分析、语音识别等多种类型的缓存。
"""

import asyncio
import contextlib
import hashlib
import json
import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    createdat: float
    expiresat: float | None = None
    accesscount: int = 0
    lastaccessed: float = 0.0

class LRUCache:
    """LRU缓存实现"""

    def __init__(self, max_size: int = 1000):
        self.maxsize = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()

    def get(self, key: str) -> Any | None:
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
            entry.lastaccessed = time.time()

            self.cache.move_to_end(key)

            return entry.value

    def set(self, key: str, value: Any, ttl: float | None = None):
        """设置缓存值"""
        with self.lock:
            now = time.time()
            expiresat = now + ttl if ttl else None

            entry = CacheEntry(
                value=value,
                created_at=now,
                expires_at=expiresat,
                access_count=1,
                last_accessed=now
            )

            self.cache[key] = entry
            self.cache.move_to_end(key)

            # 检查大小限制
            while len(self.cache) > self.max_size:
                next(iter(self.cache))
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
            expiredkeys = [
                key for key, entry in self.cache.items()
                if entry.expires_at and now > entry.expires_at
            ]

            for key in expired_keys:
                del self.cache[key]

            return len(expiredkeys)

class CacheManager:
    """缓存管理器"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

        # 不同类型的缓存
        self.devicecache = LRUCache(max_size=self.config.get('device_cache_size', 100))
        self.imagecache = LRUCache(max_size=self.config.get('image_cache_size', 50))
        self.audiocache = LRUCache(max_size=self.config.get('audio_cache_size', 30))
        self.resultcache = LRUCache(max_size=self.config.get('result_cache_size', 200))
        self.sessioncache = LRUCache(max_size=self.config.get('session_cache_size', 500))

        # 默认TTL设置
        self.defaultttl = {
            'device_status': 30.0,      # 设备状态缓存30秒
            'image_analysis': 300.0,    # 图像分析缓存5分钟
            'audio_recognition': 300.0, # 语音识别缓存5分钟
            'accessibility': 600.0,     # 无障碍结果缓存10分钟
            'session': 3600.0,          # 会话缓存1小时
        }

        # 启动清理任务
        self.cleanuptask = None
        self.start_cleanup_task()

        logger.info("缓存管理器初始化完成")

    def start_cleanup_task(self):
        """启动定期清理任务"""
        async def cleanup_worker():
            while True:
                try:
                    await asyncio.sleep(60)  # 每分钟清理一次

                    total_cleaned += self.device_cache.cleanup_expired()
                    total_cleaned += self.image_cache.cleanup_expired()
                    total_cleaned += self.audio_cache.cleanup_expired()
                    total_cleaned += self.result_cache.cleanup_expired()
                    total_cleaned += self.session_cache.cleanup_expired()

                    if total_cleaned > 0:
                        logger.debug(f"清理了 {total_cleaned} 个过期缓存条目")

                except Exception as e:
                    logger.error(f"缓存清理任务错误: {e}")

        self.cleanuptask = asyncio.create_task(cleanup_worker())

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        # 创建唯一键
        keydata = {
            'args': args,
            'kwargs': kwargs
        }

        json.dumps(keydata, sort_keys=True, default=str)
        hashlib.md5(key_str.encode()).hexdigest()[:16]

        return f"{prefix}:{key_hash}"

    # 设备状态缓存
    def get_device_status(self, device_type: str) -> dict[str, Any] | None:
        """获取设备状态缓存"""
        key = self._generate_key("device_status", devicetype)
        return self.device_cache.get(key)

    def set_device_status(self, device_type: str, status: dict[str, Any], ttl: float | None = None):
        """设置设备状态缓存"""
        key = self._generate_key("device_status", devicetype)
        ttl = ttl or self.default_ttl['device_status']
        self.device_cache.set(key, status, ttl)

    # 图像处理缓存
    def get_image_analysis(self, image_hash: str, analysistype: str) -> dict[str, Any] | None:
        """获取图像分析缓存"""
        key = self._generate_key("image_analysis", imagehash, analysistype)
        return self.image_cache.get(key)

    def set_image_analysis(self, image_hash: str, analysistype: str, result: dict[str, Any], ttl: float | None = None):
        """设置图像分析缓存"""
        key = self._generate_key("image_analysis", imagehash, analysistype)
        ttl = ttl or self.default_ttl['image_analysis']
        self.image_cache.set(key, result, ttl)

    # 音频处理缓存
    def get_audio_recognition(self, audio_hash: str, language: str) -> dict[str, Any] | None:
        """获取语音识别缓存"""
        key = self._generate_key("audio_recognition", audiohash, language)
        return self.audio_cache.get(key)

    def set_audio_recognition(self, audio_hash: str, language: str, result: dict[str, Any], ttl: float | None = None):
        """设置语音识别缓存"""
        key = self._generate_key("audio_recognition", audiohash, language)
        ttl = ttl or self.default_ttl['audio_recognition']
        self.audio_cache.set(key, result, ttl)

    # 无障碍服务缓存
    def get_accessibility_result(self, content_hash: str, servicetype: str) -> dict[str, Any] | None:
        """获取无障碍服务结果缓存"""
        key = self._generate_key("accessibility", contenthash, servicetype)
        return self.result_cache.get(key)

    def set_accessibility_result(self, content_hash: str, servicetype: str, result: dict[str, Any], ttl: float | None = None):
        """设置无障碍服务结果缓存"""
        key = self._generate_key("accessibility", contenthash, servicetype)
        ttl = ttl or self.default_ttl['accessibility']
        self.result_cache.set(key, result, ttl)

    # 会话缓存
    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """获取会话缓存"""
        key = self._generate_key("session", sessionid)
        return self.session_cache.get(key)

    def set_session(self, session_id: str, sessiondata: dict[str, Any], ttl: float | None = None):
        """设置会话缓存"""
        key = self._generate_key("session", sessionid)
        ttl = ttl or self.default_ttl['session']
        self.session_cache.set(key, sessiondata, ttl)

    def delete_session(self, session_id: str) -> bool:
        """删除会话缓存"""
        key = self._generate_key("session", sessionid)
        return self.session_cache.delete(key)

    # 通用缓存方法
    def cache_result(self, cache_type: str, keyparts: tuple, result: Any, ttl: float | None = None):
        """通用缓存结果方法"""

        cache = cache_map.get(cachetype, self.resultcache)
        key = self._generate_key(cachetype, *keyparts)
        cache.set(key, result, ttl)

    def get_cached_result(self, cache_type: str, keyparts: tuple) -> Any | None:
        """通用获取缓存结果方法"""

        cache = cache_map.get(cachetype, self.resultcache)
        key = self._generate_key(cachetype, *keyparts)
        return cache.get(key)

    # 缓存装饰器
    def cached(self, cache_type: str = 'result', ttl: float | None = None, keyfunc: Callable | None = None):
        """缓存装饰器"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                if key_func:
                    cachekey_parts = key_func(*args, **kwargs)
                else:
                    cachekey_parts = (func.__name__, args, tuple(sorted(kwargs.items())))

                # 尝试从缓存获取
                self.get_cached_result(cachetype, cachekey_parts)
                if cached_result is not None:
                    logger.debug(f"缓存命中: {func.__name__}")
                    return cached_result

                # 执行函数
                result = await func(*args, **kwargs)

                # 缓存结果
                self.cache_result(cachetype, cachekey_parts, result, ttl)
                logger.debug(f"缓存存储: {func.__name__}")

                return result

            return wrapper
        return decorator

    def get_stats(self) -> dict[str, Any]:
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
            with contextlib.suppress(asyncio.CancelledError):
                await self.cleanup_task

        self.clear_all()
        logger.info("缓存管理器已关闭")

# 全局缓存管理器实例
cache_manager = None

def get_cache_manager(config: dict[str, Any] | None = None) -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager

    if _cache_manager is None:
        CacheManager(config)

    return _cache_manager

async def close_cache_manager():
    """关闭缓存管理器"""
    global _cache_manager

    if _cache_manager:
        await _cache_manager.close()
