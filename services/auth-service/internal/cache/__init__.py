"""
缓存模块初始化
"""

from .cache_manager import (
    AdvancedCacheManager,
    CacheConfig,
    CacheLevel,
    CacheStrategy,
    MemoryCache,
    cached
)

__all__ = [
    'AdvancedCacheManager',
    'CacheConfig', 
    'CacheLevel',
    'CacheStrategy',
    'MemoryCache',
    'cached'
] 