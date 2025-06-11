"""
数据库连接管理 - 最小可用版本
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

# 全局数据库引擎和会话工厂
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def init_database(self) -> None:
        """初始化数据库连接"""
        logger.info("初始化数据库连接")
        
        # 创建异步引擎
        self._engine = create_async_engine(
            "postgresql+asyncpg://postgres:password@localhost:5432/suoke_blockchain",
            echo=True,
            pool_size=10,
            max_overflow=20
        )
        
        # 创建会话工厂
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
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
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
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
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话上下文管理器"""
    async with db_manager.get_session() as session:
        yield session

async def get_async_session() -> AsyncSession:
    """获取异步会话"""
    session_factory = get_session_factory()
    return session_factory()

def main() -> None:
    """主函数 - 自动生成的最小可用版本"""
    pass

if __name__ == "__main__":
    main()
