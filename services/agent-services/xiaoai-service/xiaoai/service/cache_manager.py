#!/usr/bin/env python3
"""
cache_manager - 索克生活项目模块
"""

import time
from typing import Any

"""
缓存管理模块 - 提供智能缓存管理功能
"""

class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.memory_cache: dict[str, dict[str, Any]] = {}
        self.stats = {
            "memory_hits": 0,
            "memory_misses": 0,
            "memory_sets": 0,
            "total_sets": 0,
            "compression_saves": 0,
        }
        self.redis_connected = False

    def get(self, cache_key: str) -> Any | None:
        """获取缓存值"""
        # 尝试从内存缓存获取
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            if not self._is_expired(cache_entry):
                self.stats["memory_hits"] += 1
                return cache_entry["value"]
            else:
                # 缓存已过期，删除
                del self.memory_cache[cache_key]

        self.stats["memory_misses"] += 1
        return None

    def set(self, cache_key: str, value: Any, ttl: int = 3600):
        """设置缓存值"""
        try:
            # 存储到内存缓存
            self.memory_cache[cache_key] = {
                "value": value,
                "timestamp": time.time(),
                "ttl": ttl,
            }

            self.stats["memory_sets"] += 1
            self.stats["total_sets"] += 1

        except Exception as e:
            print(f"Cache set error: {e}")

    def delete(self, cache_key: str):
        """删除缓存"""
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]

    def clear(self):
        """清空缓存"""
        self.memory_cache.clear()

    def get_keys(self) -> list[str]:
        """获取所有缓存键"""
        return list(self.memory_cache.keys())

    def _is_expired(self, cache_entry: dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if "timestamp" not in cache_entry or "ttl" not in cache_entry:
            return True

        current_time = time.time()
        expiry_time = cache_entry["timestamp"] + cache_entry["ttl"]
        return current_time > expiry_time

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        total_hits = self.stats["memory_hits"]
        total_misses = self.stats["memory_misses"]
        total_requests = total_hits + total_misses

        hit_rate = total_hits / total_requests if total_requests > 0 else 0.0

        return {
            "memory_cache": {
                "size": len(self.memory_cache),
                "hits": self.stats["memory_hits"],
                "misses": self.stats["memory_misses"],
                "sets": self.stats["memory_sets"],
                "hit_rate": hit_rate,
            },
            "redis_connected": self.redis_connected,
            "overall_stats": {
                "total_hits": total_hits,
                "total_misses": total_misses,
                "hit_rate": hit_rate,
                "total_sets": self.stats["total_sets"],
                "compression_saves": self.stats["compression_saves"],
            },
            "detailed_stats": self.stats,
        }

    def health_check(self) -> dict[str, Any]:
        """健康检查"""
        try:
            # 测试内存缓存
            test_key = f"health_check_{int(time.time())}"
            self.set(test_key, "test")
            retrieved_value = self.get(test_key)
            memory_healthy = retrieved_value == "test"

            if memory_healthy:
                self.delete(test_key)

            return {
                "memory_cache": memory_healthy,
                "redis_cache": False,  # Redis未实现
                "overall": memory_healthy,
            }

        except Exception as e:
            return {
                "memory_cache": False,
                "redis_cache": False,
                "overall": False,
                "error": str(e),
            }

    def cleanup(self):
        """清理资源"""
        self.memory_cache.clear()

# 全局缓存管理器实例
_cache_manager: SmartCacheManager | None = None

def get_cache_manager(config: dict[str, Any] | None = None) -> SmartCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = SmartCacheManager(config)

    return _cache_manager
