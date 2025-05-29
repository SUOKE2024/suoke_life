"""
数据库连接管理模块

提供 MongoDB、Redis 和 PostgreSQL 连接管理
"""

import logging
from typing import Optional

import motor.motor_asyncio
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config.settings import get_settings

logger = logging.getLogger(__name__)

# 全局数据库连接实例
mongodb_client: motor.motor_asyncio.AsyncIOMotorClient | None = None
mongodb_database: motor.motor_asyncio.AsyncIOMotorDatabase | None = None
redis_client: redis.Redis | None = None
postgres_engine: Optional = None
postgres_session_factory: async_sessionmaker | None = None


async def init_database() -> None:
    """初始化数据库连接"""
    settings = get_settings()

    # 初始化 MongoDB
    await init_mongodb(settings.mongodb_url, settings.mongodb_database)

    # 初始化 Redis
    await init_redis(settings.redis_url)

    # 初始化 PostgreSQL (如果配置了)
    if settings.postgres_url:
        await init_postgres(settings.postgres_url)

    logger.info("数据库连接初始化完成")


async def close_database() -> None:
    """关闭数据库连接"""
    global mongodb_client, redis_client, postgres_engine

    # 关闭 MongoDB
    if mongodb_client:
        mongodb_client.close()
        mongodb_client = None
        logger.info("MongoDB 连接已关闭")

    # 关闭 Redis
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis 连接已关闭")

    # 关闭 PostgreSQL
    if postgres_engine:
        await postgres_engine.dispose()
        postgres_engine = None
        logger.info("PostgreSQL 连接已关闭")


async def init_mongodb(url: str, database_name: str) -> None:
    """
    初始化 MongoDB 连接

    Args:
        url: MongoDB 连接 URL
        database_name: 数据库名称
    """
    global mongodb_client, mongodb_database

    try:
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(url)
        mongodb_database = mongodb_client[database_name]

        # 测试连接
        await mongodb_client.admin.command("ping")
        logger.info(f"MongoDB 连接成功: {database_name}")

    except Exception as e:
        logger.error(f"MongoDB 连接失败: {e}")
        raise


async def init_redis(url: str) -> None:
    """
    初始化 Redis 连接

    Args:
        url: Redis 连接 URL
    """
    global redis_client

    try:
        redis_client = redis.from_url(url, decode_responses=True)

        # 测试连接
        await redis_client.ping()
        logger.info("Redis 连接成功")

    except Exception as e:
        logger.error(f"Redis 连接失败: {e}")
        raise


async def init_postgres(url: str) -> None:
    """
    初始化 PostgreSQL 连接

    Args:
        url: PostgreSQL 连接 URL
    """
    global postgres_engine, postgres_session_factory

    try:
        postgres_engine = create_async_engine(
            url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )

        postgres_session_factory = async_sessionmaker(
            postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # 测试连接
        async with postgres_engine.begin() as conn:
            await conn.execute("SELECT 1")

        logger.info("PostgreSQL 连接成功")

    except Exception as e:
        logger.error(f"PostgreSQL 连接失败: {e}")
        raise


def get_mongodb() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """
    获取 MongoDB 数据库实例

    Returns:
        MongoDB 数据库实例
    """
    if mongodb_database is None:
        raise RuntimeError("MongoDB 未初始化")
    return mongodb_database


def get_redis() -> redis.Redis:
    """
    获取 Redis 客户端实例

    Returns:
        Redis 客户端实例
    """
    if redis_client is None:
        raise RuntimeError("Redis 未初始化")
    return redis_client


def get_postgres_session() -> AsyncSession:
    """
    获取 PostgreSQL 会话

    Returns:
        PostgreSQL 异步会话
    """
    if postgres_session_factory is None:
        raise RuntimeError("PostgreSQL 未初始化")
    return postgres_session_factory()


# 数据库健康检查函数
async def check_mongodb_health() -> bool:
    """检查 MongoDB 健康状态"""
    try:
        if mongodb_client:
            await mongodb_client.admin.command("ping")
            return True
    except Exception:
        pass
    return False


async def check_redis_health() -> bool:
    """检查 Redis 健康状态"""
    try:
        if redis_client:
            await redis_client.ping()
            return True
    except Exception:
        pass
    return False


async def check_postgres_health() -> bool:
    """检查 PostgreSQL 健康状态"""
    try:
        if postgres_engine:
            async with postgres_engine.begin() as conn:
                await conn.execute("SELECT 1")
            return True
    except Exception:
        pass
    return False
