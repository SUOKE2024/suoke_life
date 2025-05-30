"""
数据库连接管理

提供异步数据库连接池和会话管理功能。
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings
from .logging import get_logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncEngine

logger = get_logger(__name__)

# 全局数据库引擎和会话工厂
_engine = None
_session_factory = None


class DatabaseManager:
    """数据库管理器"""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def init_database(self) -> None:
        """初始化数据库连接"""
        logger.info("初始化数据库连接", url=settings.database.url)

        # 创建异步引擎
        self._engine = create_async_engine(
            settings.database.url,
            echo=settings.debug,  # 使用 debug 设置而不是 echo
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_recycle=settings.database.pool_recycle,
            pool_pre_ping=True,
        )

        # 创建会话工厂
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info("数据库连接初始化完成")

    async def close_database(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            logger.info("关闭数据库连接")
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("数据库连接已关闭")

    def get_engine(self) -> AsyncEngine:
        """获取数据库引擎"""
        if self._engine is None:
            raise RuntimeError("数据库引擎未初始化, 请先调用 init_database()")
        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """获取会话工厂"""
        if self._session_factory is None:
            raise RuntimeError("数据库会话工厂未初始化, 请先调用 init_database()")
        return self._session_factory

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """获取数据库会话上下文管理器"""
        session_factory = self.get_session_factory()
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()

# 兼容性函数
async def init_database() -> None:
    """初始化数据库连接"""
    await db_manager.init_database()


async def close_database() -> None:
    """关闭数据库连接"""
    await db_manager.close_database()


def get_engine() -> AsyncEngine:
    """获取数据库引擎"""
    return db_manager.get_engine()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂"""
    return db_manager.get_session_factory()


@asynccontextmanager
async def get_database_session() -> AsyncGenerator[AsyncSession]:
    """获取数据库会话上下文管理器"""
    async with db_manager.get_session() as session:
        yield session


async def get_async_session() -> AsyncSession:
    """获取异步数据库会话(用于依赖注入)"""
    session_factory = get_session_factory()
    return session_factory()
