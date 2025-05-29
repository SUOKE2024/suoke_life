#!/usr/bin/env python3
"""
性能优化模块
提供异步处理、缓存、数据库查询等性能优化功能
"""

from .async_optimization import (
    AsyncBatcher,
    ConnectionPoolConfig,
    ConnectionPoolManager,
    batch_process,
    get_pool_manager,
)
from .cache_optimization import (
    CacheInvalidator,
    CacheStats,
    CacheStrategy,
    CacheWarmer,
    LRUCache,
    MultiLevelCache,
    cached,
    get_cache,
)
from .db_optimization import (
    PreparedStatementCache,
    QueryBatcher,
    QueryOptimizer,
    QueryPlan,
    optimize_query,
)

__all__ = [
    # 异步优化
    "AsyncBatcher",
    "CacheInvalidator",
    "CacheStats",
    "CacheStrategy",
    "CacheWarmer",
    "ConnectionPoolConfig",
    "ConnectionPoolManager",
    "LRUCache",
    # 缓存优化
    "MultiLevelCache",
    "PreparedStatementCache",
    "QueryBatcher",
    # 数据库优化
    "QueryOptimizer",
    "QueryPlan",
    "batch_process",
    "cached",
    "get_cache",
    "get_pool_manager",
    "optimize_query",
]
