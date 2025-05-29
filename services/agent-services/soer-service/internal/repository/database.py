#!/usr/bin/env python3
"""
数据库连接工具
"""
import logging
import os
from typing import Any

import aiosqlite
import asyncpg

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class Database:
    """数据库连接管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    async def initialize(self):
        """初始化数据库连接"""
        if self.initialized:
            return

        self.config = get_config()
        db_config = self.config.get_section('database', {})
        self.db_type = db_config.get('type', 'sqlite')

        if self.db_type == 'postgresql':
            self.pool = await self._init_postgres(db_config)
        elif self.db_type == 'sqlite':
            self.conn = await self._init_sqlite(db_config)
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

        self.initialized = True
        logger.info(f"数据库连接初始化完成，类型: {self.db_type}")

    async def _init_postgres(self, config: dict[str, Any]) -> asyncpg.Pool:
        """初始化PostgreSQL连接池"""
        host = config.get('host', 'localhost')
        port = config.get('port', 5432)
        user = config.get('user', 'postgres')
        password = config.get('password', '')
        db_name = config.get('name', 'soer_db')

        # 处理环境变量
        if password.startswith('${') and password.endswith('}'):
            env_var = password[2:-1]
            password = os.environ.get(env_var, '')

        pool = await asyncpg.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            min_size=5,
            max_size=config.get('pool_size', 10)
        )

        logger.info(f"PostgreSQL连接池创建成功，服务器: {host}:{port}, 数据库: {db_name}")
        return pool

    async def _init_sqlite(self, config: dict[str, Any]) -> aiosqlite.Connection:
        """初始化SQLite连接"""
        db_path = config.get('path', 'soer_db.sqlite')

        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        conn = await aiosqlite.connect(db_path)

        # 启用外键约束
        await conn.execute("PRAGMA foreign_keys = ON")

        # 设置连接为返回字典的行工厂
        conn.row_factory = aiosqlite.Row

        logger.info(f"SQLite连接创建成功，数据库路径: {db_path}")
        return conn

    async def execute(self, query: str, *args, **kwargs) -> Any:
        """执行数据库查询"""
        if not self.initialized:
            await self.initialize()

        if self.db_type == 'postgresql':
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args, **kwargs)
        elif self.db_type == 'sqlite':
            return await self.conn.execute(query, *args, **kwargs)

    async def fetch(self, query: str, *args, **kwargs) -> list[dict[str, Any]]:
        """执行查询并获取所有结果"""
        if not self.initialized:
            await self.initialize()

        if self.db_type == 'postgresql':
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *args, **kwargs)
                return [dict(row) for row in rows]
        elif self.db_type == 'sqlite':
            async with self.conn.execute(query, *args, **kwargs) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def fetchone(self, query: str, *args, **kwargs) -> dict[str, Any] | None:
        """执行查询并获取单个结果"""
        if not self.initialized:
            await self.initialize()

        if self.db_type == 'postgresql':
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(query, *args, **kwargs)
                return dict(row) if row else None
        elif self.db_type == 'sqlite':
            async with self.conn.execute(query, *args, **kwargs) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def close(self):
        """关闭数据库连接"""
        if not self.initialized:
            return

        if self.db_type == 'postgresql':
            await self.pool.close()
        elif self.db_type == 'sqlite':
            await self.conn.close()

        self.initialized = False
        logger.info("数据库连接已关闭")

# 单例实例
_db = None

def get_database() -> Database:
    """获取数据库实例"""
    global _db
    if _db is None:
        _db = Database()
    return _db
