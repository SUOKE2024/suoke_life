"""
数据库连接和会话管理
Database Connection and Session Management

管理 PostgreSQL 数据库连接、会话和事务
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool

from .config import settings
from .models import Base

logger = structlog.get_logger(__name__)

# 全局数据库引擎和会话工厂
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_engine() -> AsyncEngine:
    """
    创建数据库引擎
    
    Returns:
        异步数据库引擎
    """
    logger.info("Creating database engine", url=settings.database.url)
    
    # 根据环境选择连接池
    if settings.is_testing:
        # 测试环境使用 NullPool
        poolclass = NullPool
        pool_kwargs = {}
    else:
        # 生产环境使用 QueuePool
        poolclass = QueuePool
        pool_kwargs = {
            "pool_size": settings.database.pool_size,
            "max_overflow": settings.database.max_overflow,
            "pool_timeout": settings.database.pool_timeout,
            "pool_recycle": settings.database.pool_recycle,
        }
    
    engine = create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
        poolclass=poolclass,
        **pool_kwargs,
        # 连接参数
        connect_args={
            "server_settings": {
                "application_name": "human_review_service",
                "jit": "off",  # 禁用 JIT 以提高连接速度
            }
        },
    )
    
    logger.info("Database engine created successfully")
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    创建会话工厂
    
    Args:
        engine: 数据库引擎
        
    Returns:
        异步会话工厂
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )


async def init_database() -> None:
    """
    初始化数据库连接
    """
    global _engine, _session_factory
    
    if _engine is not None:
        logger.warning("Database already initialized")
        return
    
    logger.info("Initializing database connection")
    
    _engine = create_engine()
    _session_factory = create_session_factory(_engine)
    
    # 测试连接
    try:
        async with _session_factory() as session:
            await session.execute("SELECT 1")
        logger.info("Database connection test successful")
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        raise
    
    logger.info("Database initialized successfully")


async def close_database() -> None:
    """
    关闭数据库连接
    """
    global _engine, _session_factory
    
    if _engine is None:
        logger.warning("Database not initialized")
        return
    
    logger.info("Closing database connection")
    
    await _engine.dispose()
    _engine = None
    _session_factory = None
    
    logger.info("Database connection closed")


async def create_tables() -> None:
    """
    创建数据库表
    """
    if _engine is None:
        raise RuntimeError("Database not initialized")
    
    logger.info("Creating database tables")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")


async def drop_tables() -> None:
    """
    删除数据库表（仅用于测试）
    """
    if _engine is None:
        raise RuntimeError("Database not initialized")
    
    if not settings.is_testing:
        raise RuntimeError("Can only drop tables in testing environment")
    
    logger.warning("Dropping all database tables")
    
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    logger.warning("All database tables dropped")


def get_engine() -> AsyncEngine:
    """
    获取数据库引擎
    
    Returns:
        数据库引擎
        
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    获取会话工厂
    
    Returns:
        会话工厂
        
    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话（上下文管理器）
    
    Yields:
        数据库会话
        
    Example:
        async with get_session() as session:
            result = await session.execute(query)
    """
    session_factory = get_session_factory()
    
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 依赖注入用的会话获取函数
    
    Yields:
        数据库会话
    """
    async with get_session() as session:
        yield session


class DatabaseHealthCheck:
    """数据库健康检查"""
    
    @staticmethod
    async def check_connection() -> bool:
        """
        检查数据库连接是否正常
        
        Returns:
            连接是否正常
        """
        try:
            async with get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    @staticmethod
    async def check_tables() -> bool:
        """
        检查数据库表是否存在
        
        Returns:
            表是否存在
        """
        try:
            async with get_session() as session:
                # 检查主要表是否存在
                result = await session.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('review_tasks', 'reviewers', 'review_history')
                """)
                count = result.scalar()
                return count == 3
        except Exception as e:
            logger.error("Database table check failed", error=str(e))
            return False
    
    @staticmethod
    async def get_connection_info() -> dict:
        """
        获取数据库连接信息
        
        Returns:
            连接信息字典
        """
        try:
            async with get_session() as session:
                # 获取数据库版本
                version_result = await session.execute("SELECT version()")
                version = version_result.scalar()
                
                # 获取当前连接数
                connections_result = await session.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                connections = connections_result.scalar()
                
                # 获取数据库大小
                size_result = await session.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                size = size_result.scalar()
                
                return {
                    "version": version,
                    "connections": connections,
                    "size": size,
                    "status": "healthy"
                }
        except Exception as e:
            logger.error("Failed to get database info", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# 数据库事务装饰器
def transactional(func):
    """
    数据库事务装饰器
    
    自动处理事务的提交和回滚
    """
    async def wrapper(*args, **kwargs):
        async with get_session() as session:
            try:
                # 将 session 注入到函数参数中
                if 'session' not in kwargs:
                    kwargs['session'] = session
                
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
    
    return wrapper


# 数据库迁移辅助函数
async def run_migrations() -> None:
    """
    运行数据库迁移
    
    注意：这里只是创建表，实际的迁移应该使用 Alembic
    """
    logger.info("Running database migrations")
    
    try:
        await create_tables()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error("Database migrations failed", error=str(e))
        raise


# 数据库备份和恢复（生产环境使用）
class DatabaseBackup:
    """数据库备份管理"""
    
    @staticmethod
    async def create_backup(backup_name: str) -> bool:
        """
        创建数据库备份
        
        Args:
            backup_name: 备份名称
            
        Returns:
            备份是否成功
        """
        # 这里应该实现实际的备份逻辑
        # 例如调用 pg_dump 或使用云服务的备份功能
        logger.info("Creating database backup", backup_name=backup_name)
        
        try:
            # 实际实现会调用外部命令或API
            # 这里只是示例
            return True
        except Exception as e:
            logger.error("Database backup failed", error=str(e))
            return False
    
    @staticmethod
    async def restore_backup(backup_name: str) -> bool:
        """
        恢复数据库备份
        
        Args:
            backup_name: 备份名称
            
        Returns:
            恢复是否成功
        """
        if not settings.is_testing:
            raise RuntimeError("Backup restore only allowed in testing environment")
        
        logger.warning("Restoring database backup", backup_name=backup_name)
        
        try:
            # 实际实现会调用外部命令或API
            return True
        except Exception as e:
            logger.error("Database restore failed", error=str(e))
            return False 