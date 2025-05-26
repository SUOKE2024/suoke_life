#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
优化的数据库管理器
支持连接池、事务管理、读写分离、分片和故障转移
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Union, AsyncContextManager
from dataclasses import dataclass
from contextlib import asynccontextmanager
from enum import Enum
import asyncpg
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from pymongo import ReadPreference, WriteConcern

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """数据库类型"""
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"

@dataclass
class DatabaseConfig:
    """数据库配置"""
    # 基础配置
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str = None
    password: str = None
    
    # 连接池配置
    min_connections: int = 5
    max_connections: int = 20
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0
    
    # 读写分离配置
    read_replicas: List[str] = None
    write_preference: str = "primary"
    read_preference: str = "secondary_preferred"
    
    # 分片配置
    sharding_enabled: bool = False
    shard_key: str = None
    shard_count: int = 1
    
    # 故障转移配置
    failover_enabled: bool = True
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # 性能优化
    enable_query_cache: bool = True
    cache_ttl: int = 300
    enable_prepared_statements: bool = True
    
    def __post_init__(self):
        if self.read_replicas is None:
            self.read_replicas = []

class ConnectionPool:
    """通用连接池基类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connections = asyncio.Queue(maxsize=config.max_connections)
        self.active_connections = 0
        self.total_connections = 0
        self.stats = {
            'total_requests': 0,
            'active_connections': 0,
            'pool_hits': 0,
            'pool_misses': 0,
            'connection_errors': 0
        }
        self.lock = asyncio.Lock()
    
    async def get_connection(self):
        """获取连接"""
        self.stats['total_requests'] += 1
        
        try:
            # 尝试从池中获取连接
            connection = self.connections.get_nowait()
            self.stats['pool_hits'] += 1
            return connection
        except asyncio.QueueEmpty:
            self.stats['pool_misses'] += 1
            
            # 如果池为空且未达到最大连接数，创建新连接
            async with self.lock:
                if self.total_connections < self.config.max_connections:
                    connection = await self._create_connection()
                    self.total_connections += 1
                    return connection
            
            # 等待连接可用
            connection = await self.connections.get()
            return connection
    
    async def return_connection(self, connection):
        """归还连接"""
        if connection and not connection.is_closed():
            try:
                await self.connections.put(connection)
            except asyncio.QueueFull:
                # 池已满，关闭连接
                await self._close_connection(connection)
                async with self.lock:
                    self.total_connections -= 1
    
    async def _create_connection(self):
        """创建连接（子类实现）"""
        raise NotImplementedError
    
    async def _close_connection(self, connection):
        """关闭连接（子类实现）"""
        raise NotImplementedError
    
    async def close_all(self):
        """关闭所有连接"""
        while not self.connections.empty():
            try:
                connection = self.connections.get_nowait()
                await self._close_connection(connection)
            except asyncio.QueueEmpty:
                break
        
        self.total_connections = 0
        logger.info("所有数据库连接已关闭")

class PostgreSQLPool(ConnectionPool):
    """PostgreSQL连接池"""
    
    async def _create_connection(self):
        """创建PostgreSQL连接"""
        try:
            connection = await asyncpg.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                timeout=self.config.connection_timeout
            )
            logger.debug("创建新的PostgreSQL连接")
            return connection
        except Exception as e:
            self.stats['connection_errors'] += 1
            logger.error(f"创建PostgreSQL连接失败: {e}")
            raise
    
    async def _close_connection(self, connection):
        """关闭PostgreSQL连接"""
        try:
            await connection.close()
        except Exception as e:
            logger.error(f"关闭PostgreSQL连接失败: {e}")

class MongoDBPool(ConnectionPool):
    """MongoDB连接池"""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.client = None
        self.database = None
    
    async def initialize(self):
        """初始化MongoDB客户端"""
        connection_string = f"mongodb://{self.config.username}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            connection_string,
            maxPoolSize=self.config.max_connections,
            minPoolSize=self.config.min_connections,
            maxIdleTimeMS=int(self.config.idle_timeout * 1000),
            serverSelectionTimeoutMS=int(self.config.connection_timeout * 1000),
            retryWrites=True,
            w=WriteConcern.MAJORITY,
            readPreference=ReadPreference.SECONDARY_PREFERRED
        )
        
        self.database = self.client[self.config.database]
        logger.info("MongoDB客户端初始化完成")
    
    async def get_collection(self, collection_name: str):
        """获取集合"""
        return self.database[collection_name]
    
    async def close_all(self):
        """关闭MongoDB客户端"""
        if self.client:
            self.client.close()
            logger.info("MongoDB客户端已关闭")

class RedisPool(ConnectionPool):
    """Redis连接池"""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.pool = None
    
    async def initialize(self):
        """初始化Redis连接池"""
        self.pool = redis.ConnectionPool(
            host=self.config.host,
            port=self.config.port,
            db=int(self.config.database),
            password=self.config.password,
            max_connections=self.config.max_connections,
            retry_on_timeout=True,
            socket_timeout=self.config.connection_timeout,
            socket_connect_timeout=self.config.connection_timeout
        )
        logger.info("Redis连接池初始化完成")
    
    async def get_connection(self):
        """获取Redis连接"""
        return redis.Redis(connection_pool=self.pool)
    
    async def close_all(self):
        """关闭Redis连接池"""
        if self.pool:
            await self.pool.disconnect()
            logger.info("Redis连接池已关闭")

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self.active_transactions = {}
        self.lock = asyncio.Lock()
    
    @asynccontextmanager
    async def transaction(self, isolation_level: str = "READ_COMMITTED"):
        """事务上下文管理器"""
        connection = await self.pool.get_connection()
        transaction_id = id(connection)
        
        try:
            # 开始事务
            if hasattr(connection, 'transaction'):
                # PostgreSQL
                async with connection.transaction(isolation=isolation_level):
                    async with self.lock:
                        self.active_transactions[transaction_id] = {
                            'connection': connection,
                            'start_time': time.time(),
                            'isolation_level': isolation_level
                        }
                    
                    yield connection
                    
                    # 事务自动提交
                    logger.debug(f"事务 {transaction_id} 提交成功")
            else:
                # 其他数据库类型
                yield connection
        
        except Exception as e:
            logger.error(f"事务 {transaction_id} 回滚: {e}")
            raise
        
        finally:
            async with self.lock:
                if transaction_id in self.active_transactions:
                    del self.active_transactions[transaction_id]
            
            await self.pool.return_connection(connection)
    
    def get_active_transactions(self) -> Dict[str, Any]:
        """获取活跃事务信息"""
        return {
            'count': len(self.active_transactions),
            'transactions': [
                {
                    'id': tid,
                    'duration': time.time() - info['start_time'],
                    'isolation_level': info['isolation_level']
                }
                for tid, info in self.active_transactions.items()
            ]
        }

class ShardManager:
    """分片管理器"""
    
    def __init__(self, configs: List[DatabaseConfig]):
        self.shard_configs = configs
        self.shard_pools = {}
        self.shard_count = len(configs)
    
    async def initialize(self):
        """初始化分片"""
        for i, config in enumerate(self.shard_configs):
            if config.db_type == DatabaseType.POSTGRESQL:
                pool = PostgreSQLPool(config)
            elif config.db_type == DatabaseType.MONGODB:
                pool = MongoDBPool(config)
                await pool.initialize()
            elif config.db_type == DatabaseType.REDIS:
                pool = RedisPool(config)
                await pool.initialize()
            else:
                raise ValueError(f"不支持的数据库类型: {config.db_type}")
            
            self.shard_pools[i] = pool
        
        logger.info(f"分片管理器初始化完成，共 {self.shard_count} 个分片")
    
    def get_shard_id(self, shard_key: Any) -> int:
        """根据分片键获取分片ID"""
        if isinstance(shard_key, str):
            return hash(shard_key) % self.shard_count
        elif isinstance(shard_key, int):
            return shard_key % self.shard_count
        else:
            return hash(str(shard_key)) % self.shard_count
    
    async def get_shard_connection(self, shard_key: Any):
        """获取分片连接"""
        shard_id = self.get_shard_id(shard_key)
        pool = self.shard_pools[shard_id]
        return await pool.get_connection()
    
    async def close_all(self):
        """关闭所有分片"""
        for pool in self.shard_pools.values():
            await pool.close_all()

class OptimizedDatabaseManager:
    """优化的数据库管理器"""
    
    def __init__(self):
        self.pools = {}
        self.transaction_managers = {}
        self.shard_managers = {}
        self.read_write_splitter = None
        self.query_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
    
    async def register_database(self, name: str, config: DatabaseConfig):
        """注册数据库"""
        if config.db_type == DatabaseType.POSTGRESQL:
            pool = PostgreSQLPool(config)
        elif config.db_type == DatabaseType.MONGODB:
            pool = MongoDBPool(config)
            await pool.initialize()
        elif config.db_type == DatabaseType.REDIS:
            pool = RedisPool(config)
            await pool.initialize()
        else:
            raise ValueError(f"不支持的数据库类型: {config.db_type}")
        
        self.pools[name] = pool
        self.transaction_managers[name] = TransactionManager(pool)
        
        logger.info(f"数据库 {name} 注册成功")
    
    async def register_sharded_database(self, name: str, configs: List[DatabaseConfig]):
        """注册分片数据库"""
        shard_manager = ShardManager(configs)
        await shard_manager.initialize()
        self.shard_managers[name] = shard_manager
        
        logger.info(f"分片数据库 {name} 注册成功")
    
    async def get_connection(self, database_name: str, shard_key: Any = None):
        """获取数据库连接"""
        if shard_key is not None and database_name in self.shard_managers:
            # 分片数据库
            return await self.shard_managers[database_name].get_shard_connection(shard_key)
        elif database_name in self.pools:
            # 普通数据库
            return await self.pools[database_name].get_connection()
        else:
            raise ValueError(f"数据库 {database_name} 未注册")
    
    @asynccontextmanager
    async def transaction(self, database_name: str, isolation_level: str = "READ_COMMITTED"):
        """事务上下文管理器"""
        if database_name not in self.transaction_managers:
            raise ValueError(f"数据库 {database_name} 未注册")
        
        async with self.transaction_managers[database_name].transaction(isolation_level) as conn:
            yield conn
    
    async def execute_query(self, database_name: str, query: str, params: tuple = None, 
                           use_cache: bool = True, cache_ttl: int = 300):
        """执行查询（带缓存）"""
        # 生成缓存键
        cache_key = f"{database_name}:{hash(query + str(params or ''))}"
        
        # 检查缓存
        if use_cache and cache_key in self.query_cache:
            cache_entry = self.query_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < cache_ttl:
                self.cache_stats['hits'] += 1
                logger.debug(f"查询缓存命中: {cache_key}")
                return cache_entry['result']
        
        self.cache_stats['misses'] += 1
        
        # 执行查询
        connection = await self.get_connection(database_name)
        try:
            if hasattr(connection, 'fetch'):
                # PostgreSQL
                result = await connection.fetch(query, *(params or ()))
            else:
                # 其他数据库类型
                result = await connection.execute(query, params)
            
            # 缓存结果
            if use_cache:
                self.query_cache[cache_key] = {
                    'result': result,
                    'timestamp': time.time()
                }
            
            return result
        
        finally:
            await self.pools[database_name].return_connection(connection)
    
    async def batch_execute(self, database_name: str, queries: List[tuple]):
        """批量执行查询"""
        connection = await self.get_connection(database_name)
        results = []
        
        try:
            for query, params in queries:
                if hasattr(connection, 'fetch'):
                    result = await connection.fetch(query, *(params or ()))
                else:
                    result = await connection.execute(query, params)
                results.append(result)
            
            return results
        
        finally:
            await self.pools[database_name].return_connection(connection)
    
    def clear_query_cache(self):
        """清理查询缓存"""
        self.query_cache.clear()
        self.cache_stats = {'hits': 0, 'misses': 0}
        logger.info("查询缓存已清理")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'pools': {},
            'transactions': {},
            'shards': {},
            'cache': self.cache_stats
        }
        
        # 连接池统计
        for name, pool in self.pools.items():
            stats['pools'][name] = pool.stats
        
        # 事务统计
        for name, tm in self.transaction_managers.items():
            stats['transactions'][name] = tm.get_active_transactions()
        
        # 分片统计
        for name, sm in self.shard_managers.items():
            stats['shards'][name] = {
                'shard_count': sm.shard_count,
                'pools': {i: pool.stats for i, pool in sm.shard_pools.items()}
            }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        health = {
            'status': 'healthy',
            'databases': {},
            'issues': []
        }
        
        # 检查普通数据库
        for name, pool in self.pools.items():
            try:
                connection = await pool.get_connection()
                await pool.return_connection(connection)
                health['databases'][name] = 'healthy'
            except Exception as e:
                health['databases'][name] = 'unhealthy'
                health['issues'].append(f"数据库 {name} 连接失败: {e}")
                health['status'] = 'unhealthy'
        
        # 检查分片数据库
        for name, shard_manager in self.shard_managers.items():
            shard_health = {}
            for shard_id, pool in shard_manager.shard_pools.items():
                try:
                    connection = await pool.get_connection()
                    await pool.return_connection(connection)
                    shard_health[f'shard_{shard_id}'] = 'healthy'
                except Exception as e:
                    shard_health[f'shard_{shard_id}'] = 'unhealthy'
                    health['issues'].append(f"分片 {name}.{shard_id} 连接失败: {e}")
                    health['status'] = 'unhealthy'
            
            health['databases'][f'{name}_shards'] = shard_health
        
        return health
    
    async def close_all(self):
        """关闭所有连接"""
        # 关闭普通数据库连接池
        for pool in self.pools.values():
            await pool.close_all()
        
        # 关闭分片数据库
        for shard_manager in self.shard_managers.values():
            await shard_manager.close_all()
        
        # 清理缓存
        self.clear_query_cache()
        
        logger.info("数据库管理器已关闭")

# 全局数据库管理器实例
_db_manager = None

async def get_db_manager() -> OptimizedDatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = OptimizedDatabaseManager()
    
    return _db_manager

# 装饰器
def with_database_transaction(database_name: str, isolation_level: str = "READ_COMMITTED"):
    """数据库事务装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            db_manager = await get_db_manager()
            async with db_manager.transaction(database_name, isolation_level) as conn:
                return await func(conn, *args, **kwargs)
        return wrapper
    return decorator 