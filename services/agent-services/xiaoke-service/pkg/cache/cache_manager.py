#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器
提供统一的缓存接口，支持Redis和内存缓存，包含缓存策略和过期管理
"""

import json
import time
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import aioredis
from cachetools import TTLCache, LRUCache

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """缓存策略枚举"""

    TTL = "ttl"  # 基于时间的过期
    LRU = "lru"  # 最近最少使用
    WRITE_THROUGH = "write_through"  # 写穿透
    WRITE_BACK = "write_back"  # 写回


@dataclass
class CacheConfig:
    """缓存配置"""

    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    memory_cache_size: int = 1000
    default_ttl: int = 3600  # 默认1小时
    enable_redis: bool = True
    enable_memory: bool = True
    key_prefix: str = "xiaoke:"


class CacheManager:
    """统一缓存管理器"""

    def __init__(self, config: CacheConfig):
        """
        初始化缓存管理器

        Args:
            config: 缓存配置
        """
        self.config = config
        self.redis_client: Optional[aioredis.Redis] = None

        # 初始化内存缓存
        if config.enable_memory:
            self.memory_cache = TTLCache(
                maxsize=config.memory_cache_size, ttl=config.default_ttl
            )
            self.lru_cache = LRUCache(maxsize=config.memory_cache_size)
        else:
            self.memory_cache = None
            self.lru_cache = None

        # 缓存统计
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "errors": 0}

        logger.info(
            "缓存管理器初始化完成，Redis: %s, 内存缓存: %s",
            config.enable_redis,
            config.enable_memory,
        )

    async def initialize(self):
        """初始化Redis连接"""
        if self.config.enable_redis:
            try:
                self.redis_client = aioredis.from_url(
                    self.config.redis_url,
                    db=self.config.redis_db,
                    password=self.config.redis_password,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30,
                )

                # 测试连接
                await self.redis_client.ping()
                logger.info("Redis连接建立成功")

            except Exception as e:
                logger.error("Redis连接失败: %s", str(e))
                self.redis_client = None
                self.stats["errors"] += 1

    def _build_key(self, key: str) -> str:
        """构建缓存键"""
        return f"{self.config.key_prefix}{key}"

    async def get(
        self, key: str, strategy: CacheStrategy = CacheStrategy.TTL
    ) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键
            strategy: 缓存策略

        Returns:
            缓存值或None
        """
        cache_key = self._build_key(key)

        try:
            # 首先尝试内存缓存
            if self.memory_cache and strategy == CacheStrategy.TTL:
                if cache_key in self.memory_cache:
                    self.stats["hits"] += 1
                    logger.debug("内存缓存命中: %s", key)
                    return self.memory_cache[cache_key]

            elif self.lru_cache and strategy == CacheStrategy.LRU:
                if cache_key in self.lru_cache:
                    self.stats["hits"] += 1
                    logger.debug("LRU缓存命中: %s", key)
                    return self.lru_cache[cache_key]

            # 尝试Redis缓存
            if self.redis_client:
                value = await self.redis_client.get(cache_key)
                if value is not None:
                    self.stats["hits"] += 1
                    logger.debug("Redis缓存命中: %s", key)

                    # 反序列化
                    try:
                        result = json.loads(value)

                        # 同时更新内存缓存
                        if self.memory_cache and strategy == CacheStrategy.TTL:
                            self.memory_cache[cache_key] = result
                        elif self.lru_cache and strategy == CacheStrategy.LRU:
                            self.lru_cache[cache_key] = result

                        return result
                    except json.JSONDecodeError:
                        logger.warning("缓存值反序列化失败: %s", key)
                        return value

            # 缓存未命中
            self.stats["misses"] += 1
            logger.debug("缓存未命中: %s", key)
            return None

        except Exception as e:
            logger.error("获取缓存失败，key: %s, 错误: %s", key, str(e))
            self.stats["errors"] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        strategy: CacheStrategy = CacheStrategy.TTL,
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            strategy: 缓存策略

        Returns:
            是否设置成功
        """
        cache_key = self._build_key(key)
        ttl = ttl or self.config.default_ttl

        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)

            # 设置Redis缓存
            if self.redis_client:
                await self.redis_client.setex(cache_key, ttl, serialized_value)
                logger.debug("Redis缓存设置成功: %s", key)

            # 设置内存缓存
            if strategy == CacheStrategy.TTL and self.memory_cache:
                self.memory_cache[cache_key] = value
            elif strategy == CacheStrategy.LRU and self.lru_cache:
                self.lru_cache[cache_key] = value

            self.stats["sets"] += 1
            return True

        except Exception as e:
            logger.error("设置缓存失败，key: %s, 错误: %s", key, str(e))
            self.stats["errors"] += 1
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        cache_key = self._build_key(key)

        try:
            # 删除Redis缓存
            if self.redis_client:
                await self.redis_client.delete(cache_key)

            # 删除内存缓存
            if self.memory_cache and cache_key in self.memory_cache:
                del self.memory_cache[cache_key]

            if self.lru_cache and cache_key in self.lru_cache:
                del self.lru_cache[cache_key]

            self.stats["deletes"] += 1
            logger.debug("缓存删除成功: %s", key)
            return True

        except Exception as e:
            logger.error("删除缓存失败，key: %s, 错误: %s", key, str(e))
            self.stats["errors"] += 1
            return False

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        cache_key = self._build_key(key)

        try:
            # 检查内存缓存
            if self.memory_cache and cache_key in self.memory_cache:
                return True

            if self.lru_cache and cache_key in self.lru_cache:
                return True

            # 检查Redis缓存
            if self.redis_client:
                return await self.redis_client.exists(cache_key) > 0

            return False

        except Exception as e:
            logger.error("检查缓存存在性失败，key: %s, 错误: %s", key, str(e))
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存

        Args:
            pattern: 匹配模式

        Returns:
            清除的缓存数量
        """
        try:
            count = 0

            if self.redis_client:
                # 获取匹配的键
                keys = await self.redis_client.keys(
                    f"{self.config.key_prefix}{pattern}"
                )
                if keys:
                    count = await self.redis_client.delete(*keys)
                    logger.info("清除Redis缓存 %d 个，模式: %s", count, pattern)

            # 清除内存缓存中匹配的键
            if self.memory_cache:
                keys_to_delete = [
                    k
                    for k in self.memory_cache.keys()
                    if k.startswith(f"{self.config.key_prefix}{pattern}")
                ]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    count += 1

            if self.lru_cache:
                keys_to_delete = [
                    k
                    for k in self.lru_cache.keys()
                    if k.startswith(f"{self.config.key_prefix}{pattern}")
                ]
                for key in keys_to_delete:
                    del self.lru_cache[key]
                    count += 1

            return count

        except Exception as e:
            logger.error("清除缓存模式失败，pattern: %s, 错误: %s", pattern, str(e))
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = self.stats.copy()

        # 添加缓存大小信息
        if self.memory_cache:
            stats["memory_cache_size"] = len(self.memory_cache)

        if self.lru_cache:
            stats["lru_cache_size"] = len(self.lru_cache)

        # 计算命中率
        total_requests = stats["hits"] + stats["misses"]
        if total_requests > 0:
            stats["hit_rate"] = stats["hits"] / total_requests
        else:
            stats["hit_rate"] = 0.0

        return stats

    async def close(self):
        """关闭缓存连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis连接已关闭")


# 全局缓存管理器实例
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager(config: Optional[CacheConfig] = None) -> CacheManager:
    """获取缓存管理器实例"""
    global _cache_manager

    if _cache_manager is None:
        if config is None:
            config = CacheConfig()

        _cache_manager = CacheManager(config)
        await _cache_manager.initialize()

    return _cache_manager


async def close_cache_manager():
    """关闭缓存管理器"""
    global _cache_manager

    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None
