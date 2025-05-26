"""
Database Service
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from ..model.base import SQLAlchemyBase
from .config import get_settings

logger = logging.getLogger(__name__)

# 全局变量
engine = None
async_session_maker = None


async def init_database():
    """初始化数据库连接"""
    global engine, async_session_maker
    
    settings = get_settings()
    
    # 将PostgreSQL URL转换为异步版本
    database_url = settings.database.url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    
    # 创建异步引擎
    engine = create_async_engine(
        database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        poolclass=NullPool if "sqlite" in database_url else None
    )
    
    # 创建会话工厂
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(SQLAlchemyBase.metadata.create_all)
    
    logger.info("数据库初始化完成")


async def close_database():
    """关闭数据库连接"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("数据库连接已关闭")


async def get_db_session() -> AsyncSession:
    """获取数据库会话"""
    if not async_session_maker:
        raise RuntimeError("数据库未初始化")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        if not async_session_maker:
            raise RuntimeError("数据库未初始化")
        return async_session_maker()
    
    async def execute_transaction(self, func, *args, **kwargs):
        """执行事务"""
        async with async_session_maker() as session:
            try:
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                self.logger.error(f"事务执行失败: {str(e)}")
                raise
            finally:
                await session.close()
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            async with async_session_maker() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"数据库健康检查失败: {str(e)}")
            return False


# 全局数据库服务实例
db_service = DatabaseService() 