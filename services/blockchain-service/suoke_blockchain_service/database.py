"""
数据库模块

提供异步数据库连接和会话管理。
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings
from .logging import database_logger as logger


class Base(DeclarativeBase):
    """数据库模型基类"""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


# 全局数据库引擎和会话工厂
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """获取数据库引擎"""
    if _engine is None:
        raise RuntimeError("数据库引擎未初始化，请先调用 init_database()")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂"""
    if _session_factory is None:
        raise RuntimeError("数据库会话工厂未初始化，请先调用 init_database()")
    return _session_factory


async def init_database() -> None:
    """初始化数据库连接"""
    global _engine, _session_factory

    logger.info("初始化数据库连接", url=settings.database.url)

    _engine = create_async_engine(
        settings.database.url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
        pool_recycle=settings.database.pool_recycle,
        echo=settings.debug,
    )

    _session_factory = async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info("数据库连接初始化完成")


async def close_database() -> None:
    """关闭数据库连接"""
    global _engine, _session_factory

    if _engine:
        logger.info("关闭数据库连接")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("数据库连接已关闭")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    """获取数据库会话上下文管理器"""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话（用于依赖注入）"""
    session_factory = get_session_factory()
    return session_factory()
