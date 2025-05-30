#!/usr/bin/env python3
"""
数据库连接管理器

提供SQL数据库和Redis缓存的连接管理功能
"""
import asyncio
import logging
import time
from functools import wraps
from typing import Any

import asyncpg
import redis.asyncio as redis

from pkg.utils.metrics import track_database_query

# 配置日志
logger = logging.getLogger(__name__)

class DBManager:
    """数据库连接管理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化数据库连接管理器

        Args:
            config: 数据库配置
        """
        self.config = config
        self.postgres_pool = None
        self.redis_client = None
        self._initialized = False

    async def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return

        # 初始化Postgres连接池
        postgres_config = self.config.get('postgres', {})
        if postgres_config.get('enabled', True):
            try:
                self.postgres_pool = await asyncpg.create_pool(
                    host=postgres_config.get('host', 'localhost'),
                    port=postgres_config.get('port', 5432),
                    user=postgres_config.get('user', 'postgres'),
                    password=postgres_config.get('password', ''),
                    database=postgres_config.get('database', 'soer_service'),
                    min_size=postgres_config.get('min_connections', 5),
                    max_size=postgres_config.get('max_connections', 20)
                )
                logger.info(f"PostgreSQL连接池初始化成功: {postgres_config.get('host')}:{postgres_config.get('port')}")
            except Exception as e:
                logger.error(f"PostgreSQL连接池初始化失败: {str(e)}")
                self.postgres_pool = None

        # 初始化Redis客户端
        redis_config = self.config.get('redis', {})
        if redis_config.get('enabled', True):
            try:
                self.redis_client = redis.Redis(
                    host=redis_config.get('host', 'localhost'),
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    password=redis_config.get('password', None),
                    decode_responses=True
                )
                # 测试连接
                await self.redis_client.ping()
                logger.info(f"Redis客户端初始化成功: {redis_config.get('host')}:{redis_config.get('port')}")
            except Exception as e:
                logger.error(f"Redis客户端初始化失败: {str(e)}")
                self.redis_client = None

        self._initialized = True

    async def close(self):
        """关闭数据库连接"""
        if self.postgres_pool:
            await self.postgres_pool.close()
            logger.info("PostgreSQL连接池已关闭")

        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis客户端已关闭")

    async def execute_query(self, query: str, *args, query_type: str = "select", timeout: float = 30.0) -> list[dict[str, Any]]:
        """
        执行SQL查询

        Args:
            query: SQL查询语句
            *args: 查询参数
            query_type: 查询类型 (select, insert, update, delete)
            timeout: 查询超时时间（秒）

        Returns:
            查询结果列表

        Raises:
            asyncpg.PostgresError: 数据库错误
            TimeoutError: 查询超时
        """
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL连接池未初始化")

        start_time = time.time()
        try:
            async with asyncio.timeout(timeout):
                async with self.postgres_pool.acquire() as conn:
                    if query_type.lower() == "select":
                        # 对于SELECT查询，返回记录列表
                        records = await conn.fetch(query, *args)
                        return [dict(record) for record in records]
                    else:
                        # 对于其他查询类型，返回受影响的行数
                        result = await conn.execute(query, *args)
                        return [{"affected_rows": result}]
        except TimeoutError:
            logger.error(f"查询超时: {query}")
            raise TimeoutError(f"查询超时: {query}")
        except Exception as e:
            logger.error(f"查询失败: {str(e)}, 查询: {query}")
            raise
        finally:
            duration = time.time() - start_time
            track_database_query(query_type, "postgres", duration)

    async def cache_get(self, key: str) -> str | None:
        """
        从Redis缓存获取值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回None
        """
        if not self.redis_client:
            logger.warning("Redis客户端未初始化，无法获取缓存")
            return None

        start_time = time.time()
        try:
            value = await self.redis_client.get(key)
            return value
        except Exception as e:
            logger.error(f"缓存获取失败: {str(e)}, 键: {key}")
            return None
        finally:
            duration = time.time() - start_time
            track_database_query("get", "redis", duration)

    async def cache_set(self, key: str, value: str, expiry: int = 3600) -> bool:
        """
        设置Redis缓存值

        Args:
            key: 缓存键
            value: 缓存值
            expiry: 过期时间（秒）

        Returns:
            操作是否成功
        """
        if not self.redis_client:
            logger.warning("Redis客户端未初始化，无法设置缓存")
            return False

        start_time = time.time()
        try:
            result = await self.redis_client.set(key, value, ex=expiry)
            return result
        except Exception as e:
            logger.error(f"缓存设置失败: {str(e)}, 键: {key}")
            return False
        finally:
            duration = time.time() - start_time
            track_database_query("set", "redis", duration)

    async def cache_delete(self, key: str) -> bool:
        """
        删除Redis缓存值

        Args:
            key: 缓存键

        Returns:
            操作是否成功
        """
        if not self.redis_client:
            logger.warning("Redis客户端未初始化，无法删除缓存")
            return False

        start_time = time.time()
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"缓存删除失败: {str(e)}, 键: {key}")
            return False
        finally:
            duration = time.time() - start_time
            track_database_query("delete", "redis", duration)


# 全局数据库管理器实例
_db_manager: DBManager | None = None

def get_db_manager() -> DBManager:
    """
    获取数据库管理器实例

    Returns:
        数据库管理器实例

    Raises:
        RuntimeError: 数据库管理器未初始化
    """
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化，请先调用init_db_manager")
    return _db_manager

async def init_db_manager(config: dict[str, Any]) -> DBManager:
    """
    初始化数据库管理器

    Args:
        config: 数据库配置

    Returns:
        数据库管理器实例
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DBManager(config)
        await _db_manager.initialize()
    return _db_manager

def with_db_transaction(func):
    """
    数据库事务装饰器，确保函数在事务中执行

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        db_manager = get_db_manager()
        if not db_manager.postgres_pool:
            raise RuntimeError("PostgreSQL连接池未初始化")

        async with db_manager.postgres_pool.acquire() as conn:
            async with conn.transaction():
                # 将连接传递给被装饰的函数
                return await func(conn, *args, **kwargs)

    return wrapper
