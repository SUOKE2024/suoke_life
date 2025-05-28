#!/usr/bin/env python3

"""
SQLite数据库连接池
"""

import asyncio
import logging
import os
import sqlite3

import aiosqlite

from pkg.utils.config import get_value
from pkg.utils.metrics import update_db_connection_metrics

# 初始化日志
logger = logging.getLogger(__name__)

class DatabasePool:
    """SQLite数据库连接池"""

    def __init__(self, db_path: str, pool_size: int = 5, timeout: int = 30):
        """
        初始化数据库连接池
        
        Args:
            db_path: 数据库文件路径
            pool_size: 连接池大小
            timeout: 连接超时时间（秒）
        """
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self.pool: list[aiosqlite.Connection | None] = [None] * pool_size
        self.in_use = [False] * pool_size
        self.lock = asyncio.Lock()

        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        logger.info(f"初始化数据库连接池，路径: {db_path}, 大小: {pool_size}")

    async def get_connection(self) -> aiosqlite.Connection:
        """
        获取数据库连接
        
        Returns:
            aiosqlite.Connection: 数据库连接
        
        Raises:
            Exception: 如果无法获取连接
        """
        async with self.lock:
            # 尝试获取一个空闲连接
            for i in range(self.pool_size):
                if not self.in_use[i]:
                    if self.pool[i] is None:
                        # 创建新连接
                        try:
                            conn = await aiosqlite.connect(
                                self.db_path,
                                timeout=self.timeout,
                                isolation_level=None  # 启用自动提交模式
                            )
                            await conn.execute("PRAGMA journal_mode = WAL")  # 使用WAL模式提高性能
                            await conn.execute("PRAGMA synchronous = NORMAL")  # 适当降低同步级别
                            await conn.execute("PRAGMA foreign_keys = ON")  # 启用外键约束
                            conn.row_factory = aiosqlite.Row
                            self.pool[i] = conn
                            logger.debug(f"创建新的数据库连接 (索引: {i})")
                        except Exception as e:
                            logger.error(f"创建数据库连接失败: {e!s}")
                            raise

                    self.in_use[i] = True
                    # 更新指标
                    used_count = sum(1 for used in self.in_use if used)
                    update_db_connection_metrics(self.pool_size, used_count)

                    return self.pool[i]

            # 如果所有连接都在使用，等待一个连接释放
            logger.warning("所有数据库连接都在使用中，等待空闲连接")
            raise Exception("数据库连接池已满，无法获取新连接")

    async def release_connection(self, conn: aiosqlite.Connection) -> None:
        """
        释放数据库连接
        
        Args:
            conn: 数据库连接
        """
        async with self.lock:
            for i, pool_conn in enumerate(self.pool):
                if pool_conn is conn:
                    self.in_use[i] = False
                    logger.debug(f"释放数据库连接 (索引: {i})")

                    # 更新指标
                    used_count = sum(1 for used in self.in_use if used)
                    update_db_connection_metrics(self.pool_size, used_count)

                    return

            logger.warning("尝试释放一个不在池中的连接")

    async def close_all(self) -> None:
        """关闭所有连接"""
        async with self.lock:
            for i, conn in enumerate(self.pool):
                if conn is not None:
                    await conn.close()
                    self.pool[i] = None
                    self.in_use[i] = False

            logger.info("已关闭所有数据库连接")

            # 更新指标
            update_db_connection_metrics(self.pool_size, 0)

    async def check_all(self) -> bool:
        """
        检查所有连接状态
        
        Returns:
            bool: 如果所有连接都正常，返回True
        """
        async with self.lock:
            for i, conn in enumerate(self.pool):
                if conn is not None and not self.in_use[i]:
                    try:
                        # 执行一个简单查询以验证连接
                        async with conn.execute("SELECT 1") as cursor:
                            await cursor.fetchone()
                    except sqlite3.Error as e:
                        logger.error(f"数据库连接 {i} 异常: {e!s}")
                        # 关闭并清除这个连接
                        try:
                            await conn.close()
                        except:
                            pass
                        self.pool[i] = None
                        return False

            return True


# 全局数据库连接池
_db_pool = None


async def get_db_pool() -> DatabasePool:
    """
    获取数据库连接池
    
    Returns:
        DatabasePool: 数据库连接池实例
    """
    global _db_pool

    if _db_pool is None:
        db_path = get_value("db.path", "data/maze.db")
        pool_size = get_value("db.pool_size", 5)
        timeout = get_value("db.timeout", 30)

        _db_pool = DatabasePool(db_path, pool_size, timeout)

    return _db_pool


class DBConnection:
    """数据库连接上下文管理器"""

    def __init__(self):
        """初始化连接上下文"""
        self.conn = None
        self.pool = None

    async def __aenter__(self) -> aiosqlite.Connection:
        """进入上下文，获取数据库连接"""
        self.pool = await get_db_pool()
        self.conn = await self.pool.get_connection()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文，释放数据库连接"""
        if self.conn and self.pool:
            await self.pool.release_connection(self.conn)

        # 不抑制异常
        return False
