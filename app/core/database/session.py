from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """SQLAlchemy 基础模型类"""
    pass

class Database:
    """数据库会话管理类"""
    
    def __init__(self, url: str):
        self._engine = create_async_engine(url, echo=False)
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_database(self) -> None:
        """创建数据库"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_database(self) -> None:
        """删除数据库"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def create_all(self, base: DeclarativeBase) -> None:
        """创建所有表"""
        async with self._engine.begin() as conn:
            await conn.run_sync(base.metadata.create_all)
    
    async def drop_all(self, base: DeclarativeBase) -> None:
        """删除所有表"""
        async with self._engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
    
    async def dispose(self) -> None:
        """释放数据库连接"""
        await self._engine.dispose()

# 默认数据库实例
default_database = Database(
    "mysql+asyncmy://suoke:Ht123!@#@localhost:3306/suoke_test"
) 