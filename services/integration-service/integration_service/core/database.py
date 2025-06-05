"""
数据库连接和会话管理
"""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from ..config import settings
from ..models.base import Base

logger = logging.getLogger(__name__)

# 同步数据库引擎
engine = None
SessionLocal = None

# 异步数据库引擎
async_engine = None
AsyncSessionLocal = None


def init_db() -> None:
    """初始化数据库连接"""
    global engine, SessionLocal, async_engine, AsyncSessionLocal
    
    try:
        # 同步引擎配置
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=settings.debug,
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # 设置数据库事件监听器
        setup_database_events(engine)
        
        # 异步引擎配置（如果需要）
        if settings.database_url.startswith("postgresql"):
            async_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
            async_engine = create_async_engine(
                async_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.debug,
            )
            
            AsyncSessionLocal = async_sessionmaker(
                async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        
        logger.info("数据库连接初始化成功")
        
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {e}")
        raise


def create_tables() -> None:
    """创建数据库表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise


def get_db() -> Session:
    """获取数据库会话（同步）"""
    if SessionLocal is None:
        init_db()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（异步）"""
    if AsyncSessionLocal is None:
        init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    def initialize(self, database_url: str = None) -> None:
        """初始化数据库管理器"""
        if self._initialized:
            return
            
        url = database_url or settings.database_url
        
        try:
            self.engine = create_engine(
                url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=settings.debug,
            )
            
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 设置数据库事件监听器
            setup_database_events(self.engine)
            
            self._initialized = True
            logger.info("数据库管理器初始化成功")
            
        except Exception as e:
            logger.error(f"数据库管理器初始化失败: {e}")
            raise
    
    def create_tables(self) -> None:
        """创建数据库表"""
        if not self._initialized:
            self.initialize()
            
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {e}")
            raise
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self._initialized:
            self.initialize()
            
        return self.session_factory()
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            self._initialized = False
            logger.info("数据库连接已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()


def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager


def setup_database_events(db_engine):
    """设置数据库事件监听器"""
    
    @event.listens_for(db_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """SQLite 特定配置"""
        if "sqlite" in settings.database_url:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @event.listens_for(db_engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """SQL 执行前的日志记录"""
        if settings.debug:
            logger.debug(f"执行SQL: {statement}")
            if parameters:
                logger.debug(f"参数: {parameters}")


# 健康检查函数
def check_database_health() -> bool:
    """检查数据库连接健康状态"""
    try:
        if not db_manager._initialized:
            db_manager.initialize()
            
        with db_manager.get_session() as session:
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False 