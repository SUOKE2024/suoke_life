"""
database - 索克生活项目模块
"""

from auth_service.config.settings import DatabaseSettings
from auth_service.models.base import BaseModel
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from typing import AsyncGenerator, Optional
import structlog

"""数据库管理器"""




logger = structlog.get_logger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, settings: DatabaseSettings):
        self.settings = settings
        self._async_engine = None
        self._sync_engine = None
        self._async_session_factory = None
        self._sync_session_factory = None
        
    async def initialize(self) -> None:
        """初始化数据库连接"""
        try:
            # 创建异步引擎
            self._async_engine = create_async_engine(
                self.settings.url,
                poolclass=QueuePool,
                pool_size=self.settings.pool_size,
                max_overflow=self.settings.max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.echo,
            )
            
            # 创建同步引擎（用于迁移等）
            self._sync_engine = create_engine(
                self.settings.sync_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=self.settings.echo,
            )
            
            # 创建会话工厂
            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            self._sync_session_factory = sessionmaker(
                bind=self._sync_engine,
                expire_on_commit=False,
            )
            
            # 测试连接
            await self._test_connection()
            
            logger.info("数据库连接初始化成功")
            
        except Exception as e:
            logger.error("数据库连接初始化失败", error=str(e))
            raise
    
    async def _test_connection(self) -> None:
        """测试数据库连接"""
        try:
            async with self._async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            logger.info("数据库连接测试成功")
        except Exception as e:
            logger.error("数据库连接测试失败", error=str(e))
            raise
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._async_engine:
            await self._async_engine.dispose()
            logger.info("异步数据库连接已关闭")
        
        if self._sync_engine:
            self._sync_engine.dispose()
            logger.info("同步数据库连接已关闭")
    
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话"""
        if not self._async_session_factory:
            raise RuntimeError("数据库未初始化")
        
        async with self._async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
        @cache(timeout=300)  # 5分钟缓存
def get_sync_session(self):
        """获取同步数据库会话"""
        if not self._sync_session_factory:
            raise RuntimeError("数据库未初始化")
        
        return self._sync_session_factory()
    
    async def create_tables(self) -> None:
        """创建数据库表"""
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.create_all)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error("数据库表创建失败", error=str(e))
            raise
    
    async def drop_tables(self) -> None:
        """删除数据库表"""
        try:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(BaseModel.metadata.drop_all)
            logger.info("数据库表删除成功")
        except Exception as e:
            logger.error("数据库表删除失败", error=str(e))
            raise
    
    @property
    def async_engine(self):
        """获取异步引擎"""
        return self._async_engine
    
    @property
    def sync_engine(self):
        """获取同步引擎"""
        return self._sync_engine

# 全局数据库管理器实例
_db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        raise RuntimeError("数据库管理器未初始化")
    return _db_manager

def set_db_manager(manager: DatabaseManager) -> None:
    """设置数据库管理器实例"""
    global _db_manager
    _db_manager = manager

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入函数"""
    db_manager = get_db_manager()
    async for session in db_manager.get_async_session():
        yield session

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖注入函数（别名）"""
    async for session in get_db_session():
        yield session 