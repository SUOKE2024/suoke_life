"""
数据库连接管理模块
"""
import asyncio
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
import redis.asyncio as redis

from internal.config.settings import get_settings


class Base(DeclarativeBase):
    """SQLAlchemy基础模型类"""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._engine = None
        self._session_factory = None
        self._redis_pool = None
    
    @property
    def engine(self):
        """获取数据库引擎"""
        if self._engine is None:
            database_url = (
                f"postgresql+asyncpg://{self.settings.db_username}:"
                f"{self.settings.db_password}@{self.settings.db_host}:"
                f"{self.settings.db_port}/{self.settings.db_name}"
            )
            self._engine = create_async_engine(
                database_url,
                pool_size=self.settings.db_pool_size,
                max_overflow=self.settings.db_max_overflow,
                echo=self.settings.debug,
                future=True
            )
        return self._engine
    
    @property
    def session_factory(self):
        """获取会话工厂"""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def get_redis(self) -> redis.Redis:
        """获取Redis连接"""
        if self._redis_pool is None:
            self._redis_pool = redis.ConnectionPool(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                password=self.settings.redis_password,
                max_connections=self.settings.redis_max_connections,
                decode_responses=True
            )
        return redis.Redis(connection_pool=self._redis_pool)
    
    async def close(self):
        """关闭数据库连接"""
        if self._engine:
            await self._engine.dispose()
        if self._redis_pool:
            await self._redis_pool.disconnect()


# 全局数据库管理器实例
db_manager = DatabaseManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """依赖注入：获取数据库会话"""
    async with db_manager.get_session() as session:
        yield session


async def get_redis_client() -> redis.Redis:
    """依赖注入：获取Redis客户端"""
    return await db_manager.get_redis()


async def init_database():
    """初始化数据库"""
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """关闭数据库连接"""
    await db_manager.close() 