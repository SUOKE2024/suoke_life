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
mongodb_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
mongodb_database: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None
redis_client: Optional[redis.Redis] = None
postgres_engine: Optional = None
postgres_session_factory: Optional[async_sessionmaker] = None


async def init_mongodb(mongodb_url: str, database_name: str) -> None:
    """初始化 MongoDB 连接"""
    global mongodb_client, mongodb_database
    
    try:
        mongodb_client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)
        mongodb_database = mongodb_client[database_name]
        
        # 测试连接
        await mongodb_client.admin.command('ping')
        logger.info(f"✅ MongoDB 连接成功: {database_name}")
        
    except Exception as e:
        logger.error(f"❌ MongoDB 连接失败: {e}")
        mongodb_client = None
        mongodb_database = None


async def init_redis(redis_url: str) -> None:
    """初始化 Redis 连接"""
    global redis_client
    
    try:
        redis_client = redis.from_url(redis_url)
        
        # 测试连接
        await redis_client.ping()
        logger.info("✅ Redis 连接成功")
        
    except Exception as e:
        logger.error(f"❌ Redis 连接失败: {e}")
        redis_client = None


async def init_postgres(postgres_url: str) -> None:
    """初始化 PostgreSQL 连接"""
    global postgres_engine, postgres_session_factory
    
    try:
        postgres_engine = create_async_engine(postgres_url, echo=False)
        postgres_session_factory = async_sessionmaker(
            postgres_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # 测试连接
        async with postgres_session_factory() as session:
            await session.execute("SELECT 1")
        
        logger.info("✅ PostgreSQL 连接成功")
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL 连接失败: {e}")
        postgres_engine = None
        postgres_session_factory = None


async def init_database() -> None:
    """初始化数据库连接"""
    settings = get_settings()

    # 初始化 MongoDB
    await init_mongodb(settings.mongodb_url, settings.mongodb_database)

    # 初始化 Redis
    await init_redis(settings.redis_url)

    # 初始化 PostgreSQL (如果配置了)
    if hasattr(settings, 'postgres_url') and settings.postgres_url:
        await init_postgres(settings.postgres_url)

    logger.info("📦 数据库连接初始化完成")


async def close_database() -> None:
    """关闭数据库连接"""
    global mongodb_client, redis_client, postgres_engine

    # 关闭 MongoDB
    if mongodb_client:
        mongodb_client.close()
        mongodb_client = None
        logger.info("🔒 MongoDB 连接已关闭")

    # 关闭 Redis
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("🔒 Redis 连接已关闭")

    # 关闭 PostgreSQL
    if postgres_engine:
        await postgres_engine.dispose()
        postgres_engine = None
        logger.info("🔒 PostgreSQL 连接已关闭")


def get_mongodb() -> Optional[motor.motor_asyncio.AsyncIOMotorDatabase]:
    """获取 MongoDB 数据库实例"""
    return mongodb_database


def get_redis() -> Optional[redis.Redis]:
    """获取 Redis 客户端实例"""
    return redis_client


def get_postgres_session() -> Optional[async_sessionmaker]:
    """获取 PostgreSQL 会话工厂"""
    return postgres_session_factory