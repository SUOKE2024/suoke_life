#!/usr/bin/env python3
"""
数据库连接池管理器
提供PostgreSQL和MongoDB的连接池管理，包含监控和自动重连机制
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from typing import Any

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

@dataclass
class PostgreSQLConfig:
    """PostgreSQL配置"""

    host: str = "localhost"
    port: int = 5432
    database: str = "xiaoke_db"
    username: str = "postgres"
    password: str = ""
    min_size: int = 5
    max_size: int = 20
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0
    timeout: float = 60.0
    command_timeout: float = 60.0
    server_settings: dict[str, str] = None

@dataclass
class MongoDBConfig:
    """MongoDB配置"""

    host: str = "localhost"
    port: int = 27017
    database: str = "xiaoke_db"
    username: str | None = None
    password: str | None = None
    min_pool_size: int = 5
    max_pool_size: int = 20
    max_idle_time_ms: int = 300000
    connect_timeout_ms: int = 20000
    server_selection_timeout_ms: int = 30000
    replica_set: str | None = None

class ConnectionPoolManager:
    """数据库连接池管理器"""

    def __init__(
        self, pg_config: PostgreSQLConfig = None, mongo_config: MongoDBConfig = None
    ):
        """
        初始化连接池管理器

        Args:
            pg_config: PostgreSQL配置
            mongo_config: MongoDB配置
        """
        self.pg_config = pg_config or PostgreSQLConfig()
        self.mongo_config = mongo_config or MongoDBConfig()

        # PostgreSQL连接池
        self.pg_pool: asyncpg.Pool | None = None
        self.sqlalchemy_engine = None
        self.async_session_maker = None

        # MongoDB连接
        self.mongo_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
        self.mongo_db = None

        # 连接池统计
        self.stats = {
            "pg_connections_created": 0,
            "pg_connections_closed": 0,
            "pg_queries_executed": 0,
            "mongo_operations": 0,
            "connection_errors": 0,
            "last_health_check": 0,
        }

        # 健康检查任务
        self._health_check_task: asyncio.Task | None = None

        logger.info("数据库连接池管理器初始化完成")

    async def initialize(self):
        """初始化所有数据库连接"""
        await self._initialize_postgresql()
        await self._initialize_mongodb()

        # 启动健康检查
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info("数据库连接池初始化完成")

    async def _initialize_postgresql(self):
        """初始化PostgreSQL连接池"""
        try:
            # 构建连接字符串
            dsn = (
                f"postgresql://{self.pg_config.username}:{self.pg_config.password}@"
                f"{self.pg_config.host}:{self.pg_config.port}/{self.pg_config.database}"
            )

            # 创建asyncpg连接池
            self.pg_pool = await asyncpg.create_pool(
                dsn,
                min_size=self.pg_config.min_size,
                max_size=self.pg_config.max_size,
                max_queries=self.pg_config.max_queries,
                max_inactive_connection_lifetime=self.pg_config.max_inactive_connection_lifetime,
                timeout=self.pg_config.timeout,
                command_timeout=self.pg_config.command_timeout,
                server_settings=self.pg_config.server_settings or {},
            )

            # 创建SQLAlchemy异步引擎
            self.sqlalchemy_engine = create_async_engine(
                f"postgresql+asyncpg://{self.pg_config.username}:{self.pg_config.password}@"
                f"{self.pg_config.host}:{self.pg_config.port}/{self.pg_config.database}",
                poolclass=QueuePool,
                pool_size=self.pg_config.min_size,
                max_overflow=self.pg_config.max_size - self.pg_config.min_size,
                pool_timeout=self.pg_config.timeout,
                pool_recycle=3600,  # 1小时回收连接
                echo=False,
            )

            # 创建会话工厂
            self.async_session_maker = async_sessionmaker(
                self.sqlalchemy_engine, class_=AsyncSession, expire_on_commit=False
            )

            logger.info(
                "PostgreSQL连接池创建成功，最小连接数: %d, 最大连接数: %d",
                self.pg_config.min_size,
                self.pg_config.max_size,
            )

        except Exception as e:
            logger.error("PostgreSQL连接池初始化失败: %s", str(e))
            self.stats["connection_errors"] += 1
            raise

    async def _initialize_mongodb(self):
        """初始化MongoDB连接"""
        try:
            # 构建连接字符串
            if self.mongo_config.username and self.mongo_config.password:
                connection_string = (
                    f"mongodb://{self.mongo_config.username}:{self.mongo_config.password}@"
                    f"{self.mongo_config.host}:{self.mongo_config.port}/{self.mongo_config.database}"
                )
            else:
                connection_string = (
                    f"mongodb://{self.mongo_config.host}:{self.mongo_config.port}"
                )

            # 添加连接选项
            options = {
                "minPoolSize": self.mongo_config.min_pool_size,
                "maxPoolSize": self.mongo_config.max_pool_size,
                "maxIdleTimeMS": self.mongo_config.max_idle_time_ms,
                "connectTimeoutMS": self.mongo_config.connect_timeout_ms,
                "serverSelectionTimeoutMS": self.mongo_config.server_selection_timeout_ms,
            }

            if self.mongo_config.replica_set:
                options["replicaSet"] = self.mongo_config.replica_set

            # 创建MongoDB客户端
            self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
                connection_string, **options
            )

            # 获取数据库
            self.mongo_db = self.mongo_client[self.mongo_config.database]

            # 测试连接
            await self.mongo_client.admin.command("ping")

            logger.info("MongoDB连接创建成功，数据库: %s", self.mongo_config.database)

        except Exception as e:
            logger.error("MongoDB连接初始化失败: %s", str(e))
            self.stats["connection_errors"] += 1
            raise

    @asynccontextmanager
    async def get_pg_connection(self):
        """获取PostgreSQL连接的上下文管理器"""
        if not self.pg_pool:
            raise RuntimeError("PostgreSQL连接池未初始化")

        connection = None
        try:
            connection = await self.pg_pool.acquire()
            self.stats["pg_connections_created"] += 1
            yield connection
        finally:
            if connection:
                await self.pg_pool.release(connection)
                self.stats["pg_connections_closed"] += 1

    @asynccontextmanager
    async def get_sqlalchemy_session(self):
        """获取SQLAlchemy会话的上下文管理器"""
        if not self.async_session_maker:
            raise RuntimeError("SQLAlchemy会话工厂未初始化")

        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def get_mongo_db(self):
        """获取MongoDB数据库实例"""
        if not self.mongo_db:
            raise RuntimeError("MongoDB连接未初始化")
        return self.mongo_db

    def get_mongo_collection(self, collection_name: str):
        """获取MongoDB集合"""
        return self.get_mongo_db()[collection_name]

    async def execute_pg_query(self, query: str, *args) -> list[dict[str, Any]]:
        """执行PostgreSQL查询"""
        async with self.get_pg_connection() as conn:
            try:
                result = await conn.fetch(query, *args)
                self.stats["pg_queries_executed"] += 1
                return [dict(row) for row in result]
            except Exception as e:
                logger.error("PostgreSQL查询执行失败: %s", str(e))
                self.stats["connection_errors"] += 1
                raise

    async def execute_pg_command(self, command: str, *args) -> str:
        """执行PostgreSQL命令"""
        async with self.get_pg_connection() as conn:
            try:
                result = await conn.execute(command, *args)
                self.stats["pg_queries_executed"] += 1
                return result
            except Exception as e:
                logger.error("PostgreSQL命令执行失败: %s", str(e))
                self.stats["connection_errors"] += 1
                raise

    async def get_pg_pool_stats(self) -> dict[str, Any]:
        """获取PostgreSQL连接池统计"""
        if not self.pg_pool:
            return {}

        return {
            "size": self.pg_pool.get_size(),
            "min_size": self.pg_pool.get_min_size(),
            "max_size": self.pg_pool.get_max_size(),
            "idle_connections": self.pg_pool.get_idle_size(),
            "queries_executed": self.stats["pg_queries_executed"],
            "connections_created": self.stats["pg_connections_created"],
            "connections_closed": self.stats["pg_connections_closed"],
        }

    async def get_mongo_stats(self) -> dict[str, Any]:
        """获取MongoDB连接统计"""
        if not self.mongo_client:
            return {}

        try:
            server_info = await self.mongo_client.server_info()
            return {
                "server_version": server_info.get("version", "unknown"),
                "operations": self.stats["mongo_operations"],
                "database": self.mongo_config.database,
            }
        except Exception as e:
            logger.error("获取MongoDB统计失败: %s", str(e))
            return {"error": str(e)}

    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                await self._perform_health_check()
                self.stats["last_health_check"] = int(time.time())
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("健康检查失败: %s", str(e))

    async def _perform_health_check(self):
        """执行健康检查"""
        # 检查PostgreSQL
        if self.pg_pool:
            try:
                async with self.get_pg_connection() as conn:
                    await conn.fetchval("SELECT 1")
                logger.debug("PostgreSQL健康检查通过")
            except Exception as e:
                logger.warning("PostgreSQL健康检查失败: %s", str(e))
                self.stats["connection_errors"] += 1

        # 检查MongoDB
        if self.mongo_client:
            try:
                await self.mongo_client.admin.command("ping")
                logger.debug("MongoDB健康检查通过")
            except Exception as e:
                logger.warning("MongoDB健康检查失败: %s", str(e))
                self.stats["connection_errors"] += 1

    async def get_overall_stats(self) -> dict[str, Any]:
        """获取整体统计信息"""
        pg_stats = await self.get_pg_pool_stats()
        mongo_stats = await self.get_mongo_stats()

        return {
            "postgresql": pg_stats,
            "mongodb": mongo_stats,
            "general": {
                "connection_errors": self.stats["connection_errors"],
                "last_health_check": self.stats["last_health_check"],
            },
        }

    async def close(self):
        """关闭所有连接"""
        # 停止健康检查
        if self._health_check_task:
            self._health_check_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._health_check_task

        # 关闭PostgreSQL连接池
        if self.pg_pool:
            await self.pg_pool.close()
            logger.info("PostgreSQL连接池已关闭")

        if self.sqlalchemy_engine:
            await self.sqlalchemy_engine.dispose()
            logger.info("SQLAlchemy引擎已关闭")

        # 关闭MongoDB连接
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB连接已关闭")

# 全局连接池管理器实例
_connection_pool_manager: ConnectionPoolManager | None = None

async def get_connection_pool_manager(
    pg_config: PostgreSQLConfig | None = None,
    mongo_config: MongoDBConfig | None = None,
) -> ConnectionPoolManager:
    """获取连接池管理器实例"""
    global _connection_pool_manager

    if _connection_pool_manager is None:
        _connection_pool_manager = ConnectionPoolManager(pg_config, mongo_config)
        await _connection_pool_manager.initialize()

    return _connection_pool_manager

async def close_connection_pool_manager():
    """关闭连接池管理器"""
    global _connection_pool_manager

    if _connection_pool_manager:
        await _connection_pool_manager.close()
        _connection_pool_manager = None
