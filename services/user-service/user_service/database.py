"""
database - 索克生活项目模块
"""

from contextlib import asynccontextmanager
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from typing import AsyncGenerator, Optional
from user_service.config import get_settings
import asyncio
import structlog

"""用户服务数据库模块"""



logger = structlog.get_logger()

# 数据库基类
Base = declarative_base()

# 全局数据库引擎和会话
_async_engine = None
_async_session_factory = None
_sync_engine = None
_sync_session_factory = None


async def init_database():
    """初始化数据库连接"""
    global _async_engine, _async_session_factory, _sync_engine, _sync_session_factory
    
    settings = get_settings()
    
    # 创建异步引擎
    _async_engine = create_async_engine(
        settings.database.url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
        pool_recycle=settings.database.pool_recycle,
        echo=settings.database.echo,
        echo_pool=settings.database.echo_pool,
        poolclass=QueuePool,
    )
    
    # 创建异步会话工厂
    _async_session_factory = async_sessionmaker(
        bind=_async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    # 创建同步引擎（用于迁移）
    _sync_engine = create_engine(
        settings.database.sync_url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
        pool_recycle=settings.database.pool_recycle,
        echo=settings.database.echo,
        poolclass=QueuePool,
    )
    
    # 创建同步会话工厂
    _sync_session_factory = sessionmaker(bind=_sync_engine)
    
    logger.info("Database initialized successfully")


async def close_database():
    """关闭数据库连接"""
    global _async_engine, _sync_engine
    
    if _async_engine:
        await _async_engine.dispose()
        logger.info("Async database engine disposed")
    
    if _sync_engine:
        _sync_engine.dispose()
        logger.info("Sync database engine disposed")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    if not _async_session_factory:
        raise RuntimeError("Database not initialized")
    
    async with _async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


    @cache(timeout=300)  # 5分钟缓存
def get_sync_session():
    """获取同步数据库会话"""
    if not _sync_session_factory:
        raise RuntimeError("Database not initialized")
    
    return _sync_session_factory()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依赖注入：获取数据库会话"""
    async with get_async_session() as session:
        yield session


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            async with get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error("Database connection check failed", error=str(e))
            return False
    
    async def get_connection_info(self) -> dict:
        """获取数据库连接信息"""
        try:
            async with get_async_session() as session:
                # 获取数据库版本
                version_result = await session.execute(text("SELECT version()"))
                version = version_result.scalar()
                
                # 获取当前数据库名
                db_result = await session.execute(text("SELECT current_database()"))
                database = db_result.scalar()
                
                # 获取连接数统计
                conn_result = await session.execute(text("""
                    SELECT state, count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                    GROUP BY state
                """))
                connections = {row[0]: row[1] for row in conn_result.fetchall()}
                
                return {
                    "version": version,
                    "database": database,
                    "connections": connections,
                    "pool_size": self.settings.database.pool_size,
                    "max_overflow": self.settings.database.max_overflow
                }
        except Exception as e:
            logger.error("Failed to get database info", error=str(e))
            return {"error": str(e)}
    
    async def create_tables(self):
        """创建数据库表"""
        try:
            async with _async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            raise
    
    async def drop_tables(self):
        """删除数据库表"""
        try:
            async with _async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error("Failed to drop database tables", error=str(e))
            raise
    
    def create_tables_sync(self):
        """同步创建数据库表"""
        try:
            Base.metadata.create_all(_sync_engine)
            logger.info("Database tables created successfully (sync)")
        except Exception as e:
            logger.error("Failed to create database tables (sync)", error=str(e))
            raise
    
    def drop_tables_sync(self):
        """同步删除数据库表"""
        try:
            Base.metadata.drop_all(_sync_engine)
            logger.info("Database tables dropped successfully (sync)")
        except Exception as e:
            logger.error("Failed to drop database tables (sync)", error=str(e))
            raise


class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
    
    async def init_migration_table(self):
        """初始化迁移表"""
        try:
            async with get_async_session() as session:
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(255) PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                await session.commit()
            logger.info("Migration table initialized")
        except Exception as e:
            logger.error("Failed to initialize migration table", error=str(e))
            raise
    
    async def get_applied_migrations(self) -> list:
        """获取已应用的迁移"""
        try:
            async with get_async_session() as session:
                result = await session.execute(text("""
                    SELECT version FROM schema_migrations ORDER BY version
                """))
                return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error("Failed to get applied migrations", error=str(e))
            return []
    
    async def apply_migration(self, version: str, sql: str):
        """应用迁移"""
        try:
            async with get_async_session() as session:
                # 执行迁移SQL
                await session.execute(text(sql))
                
                # 记录迁移版本
                await session.execute(text("""
                    INSERT INTO schema_migrations (version) VALUES (:version)
                """), {"version": version})
                
                await session.commit()
            logger.info("Migration applied successfully", version=version)
        except Exception as e:
            logger.error("Failed to apply migration", version=version, error=str(e))
            raise
    
    async def rollback_migration(self, version: str, rollback_sql: str):
        """回滚迁移"""
        try:
            async with get_async_session() as session:
                # 执行回滚SQL
                await session.execute(text(rollback_sql))
                
                # 删除迁移记录
                await session.execute(text("""
                    DELETE FROM schema_migrations WHERE version = :version
                """), {"version": version})
                
                await session.commit()
            logger.info("Migration rolled back successfully", version=version)
        except Exception as e:
            logger.error("Failed to rollback migration", version=version, error=str(e))
            raise
    
    async def get_migration_status(self) -> dict:
        """获取迁移状态"""
        try:
            applied = await self.get_applied_migrations()
            return {
                "applied_count": len(applied),
                "applied_migrations": applied,
                "last_migration": applied[-1] if applied else None
            }
        except Exception as e:
            logger.error("Failed to get migration status", error=str(e))
            return {"error": str(e)}


# 全局实例
_db_manager: Optional[DatabaseManager] = None
_migration_manager: Optional[MigrationManager] = None


def get_database_manager() -> DatabaseManager:
    """获取数据库管理器"""
    global _db_manager
    if not _db_manager:
        _db_manager = DatabaseManager()
    return _db_manager


def get_migration_manager() -> MigrationManager:
    """获取迁移管理器"""
    global _migration_manager
    if not _migration_manager:
        _migration_manager = MigrationManager()
    return _migration_manager 