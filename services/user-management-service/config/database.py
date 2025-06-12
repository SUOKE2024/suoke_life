"""
数据库配置和连接管理
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .settings import get_settings

logger = logging.getLogger(__name__)

# 获取配置
settings = get_settings()

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()

# 异步数据库引擎
async_engine = create_async_engine(
    settings.database.url,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    echo=settings.debug,
    future=True,
)

# 同步数据库引擎（用于迁移等）
sync_engine = create_engine(
    settings.database.sync_url,
    poolclass=QueuePool,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    echo=settings.debug,
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# 同步会话工厂
SessionLocal = sessionmaker(bind=sync_engine, autoflush=True, autocommit=False)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入用的数据库会话获取器"""
    async with get_async_session() as session:
        yield session


async def init_database():
    """初始化数据库"""
    try:
        logger.info("🔄 初始化数据库连接...")

        # 测试连接
        async with async_engine.begin() as conn:
            # 这里可以执行一些初始化SQL
            pass

        logger.info("✅ 数据库连接初始化成功")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def close_database():
    """关闭数据库连接"""
    try:
        logger.info("🔄 关闭数据库连接...")
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


# 导出
__all__ = [
    "Base",
    "metadata",
    "async_engine",
    "sync_engine",
    "AsyncSessionLocal",
    "SessionLocal",
    "get_async_session",
    "get_db",
    "init_database",
    "close_database",
]
