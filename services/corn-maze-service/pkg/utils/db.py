#!/usr/bin/env python3

"""
数据库连接池管理

提供SQLite数据库连接池功能，支持异步操作
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import aiosqlite

from corn_maze_service.constants import DEFAULT_POOL_SIZE

logger = logging.getLogger(__name__)


class DatabasePool:
    """数据库连接池"""

    def __init__(self, db_path: str, pool_size: int = DEFAULT_POOL_SIZE):
        self.db_path = db_path
        self.pool_size = pool_size
        self._pool: list[aiosqlite.Connection] = []
        self._in_use: set[aiosqlite.Connection] = set()
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """初始化连接池"""
        if self._initialized:
            return

        # 确保数据库目录存在
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"初始化数据库连接池, 路径: {self.db_path}, 大小: {self.pool_size}")

    async def get_connection(self) -> aiosqlite.Connection:
        """获取数据库连接"""
        async with self._lock:
            # 如果池中有可用连接，直接返回
            if self._pool:
                conn = self._pool.pop()
                self._in_use.add(conn)
                return conn

            # 如果正在使用的连接数未达到上限，创建新连接
            if len(self._in_use) < self.pool_size:
                conn = await aiosqlite.connect(self.db_path)
                # 启用外键约束
                await conn.execute("PRAGMA foreign_keys = ON")
                # 设置WAL模式以提高并发性能
                await conn.execute("PRAGMA journal_mode = WAL")
                # 设置同步模式
                await conn.execute("PRAGMA synchronous = NORMAL")

                self._in_use.add(conn)
                logger.debug(f"创建新数据库连接: {id(conn)}")
                return conn

            # 如果所有连接都在使用, 等待一个连接释放
            logger.warning("所有数据库连接都在使用中, 等待空闲连接")
            raise Exception("数据库连接池已满, 无法获取新连接")

    async def release_connection(self, conn: aiosqlite.Connection) -> None:
        """释放数据库连接"""
        async with self._lock:
            if conn in self._in_use:
                self._in_use.remove(conn)
                self._pool.append(conn)
                logger.debug(f"释放数据库连接: {id(conn)}")

    async def close_all(self) -> None:
        """关闭所有连接"""
        async with self._lock:
            # 关闭正在使用的连接
            for conn in self._in_use:
                await conn.close()
            self._in_use.clear()

            # 关闭池中的连接
            for conn in self._pool:
                await conn.close()
            self._pool.clear()

            logger.info("所有数据库连接已关闭")

    async def execute_query(
        self,
        query: str,
        params: tuple | None = None
    ) -> list[dict[str, Any]]:
        """执行查询并返回结果"""
        conn = await self.get_connection()
        try:
            async with conn.execute(query, params or ()) as cursor:
                rows = await cursor.fetchall()
                # 获取列名
                columns = [description[0] for description in cursor.description]
                # 转换为字典列表
                return [dict(zip(columns, row, strict=False)) for row in rows]
        finally:
            await self.release_connection(conn)

    async def execute_update(
        self,
        query: str,
        params: tuple | None = None
    ) -> int:
        """执行更新操作并返回影响的行数"""
        conn = await self.get_connection()
        try:
            async with conn.execute(query, params or ()) as cursor:
                await conn.commit()
                return cursor.rowcount
        finally:
            await self.release_connection(conn)

    async def execute_many(
        self,
        query: str,
        params_list: list[tuple]
    ) -> int:
        """批量执行操作"""
        conn = await self.get_connection()
        try:
            await conn.executemany(query, params_list)
            await conn.commit()
            return len(params_list)
        finally:
            await self.release_connection(conn)

    def get_pool_status(self) -> dict[str, Any]:
        """获取连接池状态"""
        return {
            "pool_size": self.pool_size,
            "available_connections": len(self._pool),
            "in_use_connections": len(self._in_use),
            "total_connections": len(self._pool) + len(self._in_use)
        }


# 数据库连接池单例
class DatabasePoolSingleton:
    """数据库连接池单例"""

    _instance: DatabasePool | None = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls, db_path: str | None = None, pool_size: int | None = None) -> DatabasePool:
        """获取数据库连接池实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    default_db_path = "./data/corn_maze.db"
                    default_pool_size = DEFAULT_POOL_SIZE
                    cls._instance = DatabasePool(
                        db_path or default_db_path,
                        pool_size or default_pool_size
                    )
                    await cls._instance.initialize()
        return cls._instance

    @classmethod
    def get_instance_sync(cls, db_path: str | None = None, pool_size: int | None = None) -> DatabasePool:
        """同步获取数据库连接池实例"""
        if cls._instance is None:
            default_db_path = "./data/corn_maze.db"
            default_pool_size = DEFAULT_POOL_SIZE
            cls._instance = DatabasePool(
                db_path or default_db_path,
                pool_size or default_pool_size
            )
        return cls._instance

    @classmethod
    async def close_instance(cls):
        """关闭数据库连接池实例"""
        if cls._instance:
            await cls._instance.close_all()
            cls._instance = None


def get_database_pool() -> DatabasePool:
    """
    获取全局数据库连接池（向后兼容）

    Returns:
        DatabasePool: 数据库连接池实例
    """
    return DatabasePoolSingleton.get_instance_sync()


async def get_database_pool_async(db_path: str | None = None, pool_size: int | None = None) -> DatabasePool:
    """
    异步获取全局数据库连接池

    Args:
        db_path: 数据库文件路径
        pool_size: 连接池大小

    Returns:
        DatabasePool: 数据库连接池实例
    """
    return await DatabasePoolSingleton.get_instance(db_path, pool_size)


async def init_database_pool(db_path: str, pool_size: int = DEFAULT_POOL_SIZE) -> None:
    """
    初始化全局数据库连接池（向后兼容）

    Args:
        db_path: 数据库文件路径
        pool_size: 连接池大小
    """
    await DatabasePoolSingleton.get_instance(db_path, pool_size)


async def close_database_pool() -> None:
    """关闭全局数据库连接池（向后兼容）"""
    await DatabasePoolSingleton.close_instance()


# 便捷函数
async def execute_query(query: str, params: tuple | None = None) -> list[dict[str, Any]]:
    """执行查询"""
    pool = await get_database_pool_async()
    return await pool.execute_query(query, params)


async def execute_update(query: str, params: tuple | None = None) -> int:
    """执行更新"""
    pool = await get_database_pool_async()
    return await pool.execute_update(query, params)


async def execute_many(query: str, params_list: list[tuple]) -> int:
    """批量执行"""
    pool = await get_database_pool_async()
    return await pool.execute_many(query, params_list)
