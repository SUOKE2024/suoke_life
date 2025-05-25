#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化模块
提供异步处理、缓存、数据库查询等性能优化功能
"""

from .async_optimization import (
    AsyncBatcher,
    ConnectionPoolManager,
    ConnectionPoolConfig,
    get_pool_manager,
    batch_process
)

from .cache_optimization import (
    MultiLevelCache,
    LRUCache,
    CacheStrategy,
    CacheStats,
    CacheWarmer,
    CacheInvalidator,
    get_cache,
    cached
)

from .db_optimization import (
    QueryOptimizer,
    QueryPlan,
    QueryBatcher,
    PreparedStatementCache,
    optimize_query
)

__all__ = [
    # 异步优化
    'AsyncBatcher',
    'ConnectionPoolManager',
    'ConnectionPoolConfig',
    'get_pool_manager',
    'batch_process',
    
    # 缓存优化
    'MultiLevelCache',
    'LRUCache',
    'CacheStrategy',
    'CacheStats',
    'CacheWarmer',
    'CacheInvalidator',
    'get_cache',
    'cached',
    
    # 数据库优化
    'QueryOptimizer',
    'QueryPlan',
    'QueryBatcher',
    'PreparedStatementCache',
    'optimize_query'
] 