"""数据库连接管理"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from user_service.config import get_settings

logger = logging.getLogger(__name__)

# 全局变量
engine = None
async_session_maker = None


class Base(DeclarativeBase):
    """数据库模型基类"""
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )


async def init_database() -> None:
    """初始化数据库连接"""
    global engine, async_session_maker
    
    settings = get_settings()
    
    try:
        # 创建异步引擎
        engine = create_async_engine(
            settings.database.url,
            echo=settings.database.echo,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_recycle=settings.database.pool_recycle,
            pool_pre_ping=True,
        )
        
        # 创建会话工厂
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("数据库连接初始化成功")
        
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        raise


async def close_database() -> None:
    """关闭数据库连接"""
    global engine
    
    if engine:
        try:
            await engine.dispose()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {e}")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    if not async_session_maker:
        raise RuntimeError("数据库未初始化")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话出错: {e}")
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """创建数据库表"""
    if not engine:
        raise RuntimeError("数据库引擎未初始化")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"创建数据库表失败: {e}")
        raise


async def drop_tables() -> None:
    """删除数据库表"""
    if not engine:
        raise RuntimeError("数据库引擎未初始化")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("数据库表删除成功")
    except Exception as e:
        logger.error(f"删除数据库表失败: {e}")
        raise 