"""
test_database_manager_fixed - 索克生活项目模块
"""

from auth_service.core.database import DatabaseManager
from auth_service.models.base import BaseModel
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator, Optional
import asyncio
import os
import tempfile

"""
测试专用数据库管理器（修复版）
解决TestClient不触发FastAPI lifespan事件的问题
"""




class TestDatabaseManager:
    """测试专用数据库管理器"""

    def __init__(self, database_url: Optional[str] = None):
        """
        初始化测试数据库管理器

        Args:
            database_url: 数据库URL，默认使用内存SQLite
        """
        if database_url is None:
            # 使用内存SQLite数据库
            database_url = "sqlite + aiosqlite: / / / :memory:"

        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self._initialized = False

    async def initialize(self) - > None:
        """初始化数据库连接和表结构"""
        if self._initialized:
            return

        # 创建异步引擎
        self.engine = create_async_engine(
            self.database_url,
            echo = False,  # 测试时不输出SQL日志
            poolclass = StaticPool,
            connect_args = {
                "check_same_thread": False,
            } if "sqlite" in self.database_url else {},
        )

        # 创建会话工厂
        self.session_factory = async_sessionmaker(
            bind = self.engine,
            class_ = AsyncSession,
            expire_on_commit = False,
        )

        # 创建所有表
        async with self.engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

        self._initialized = True

    async def get_session(self) - > AsyncGenerator[AsyncSession, None]:
        """获取数据库会话"""
        if not self._initialized:
            await self.initialize()

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def cleanup(self) - > None:
        """清理数据库连接"""
        if self.engine:
            await self.engine.dispose()
        self._initialized = False

    async def reset_database(self) - > None:
        """重置数据库（删除所有数据）"""
        if not self._initialized:
            return

        async with self.engine.begin() as conn:
            # 删除所有表
            await conn.run_sync(BaseModel.metadata.drop_all)
            # 重新创建所有表
            await conn.run_sync(BaseModel.metadata.create_all)


class TestDatabaseManagerSingleton:
    """测试数据库管理器单例"""

    _instance: Optional[TestDatabaseManager] = None
    _lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls, database_url: Optional[str] = None) - > TestDatabaseManager:
        """获取测试数据库管理器实例"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = TestDatabaseManager(database_url)
                    await cls._instance.initialize()
        return cls._instance

    @classmethod
    async def cleanup_instance(cls):
        """清理测试数据库管理器实例"""
        if cls._instance:
            await cls._instance.cleanup()
            cls._instance = None


# 全局测试数据库管理器实例
_test_db_manager: Optional[TestDatabaseManager] = None


async def get_test_db_manager() - > TestDatabaseManager:
    """获取测试数据库管理器"""
    global _test_db_manager
    if _test_db_manager is None:
        _test_db_manager = TestDatabaseManager()
        await _test_db_manager.initialize()
    return _test_db_manager


async def cleanup_test_db_manager() - > None:
    """清理测试数据库管理器"""
    global _test_db_manager
    if _test_db_manager:
        await _test_db_manager.cleanup()
        _test_db_manager = None


async def get_test_db_session() - > AsyncGenerator[AsyncSession, None]:
    """获取测试数据库会话"""
    db_manager = await get_test_db_manager()
    async with db_manager.get_session() as session:
        yield session


def create_test_database_manager() - > TestDatabaseManager:
    """创建新的测试数据库管理器实例（用于隔离测试）"""
    return TestDatabaseManager()


async def setup_test_database() - > TestDatabaseManager:
    """设置测试数据库（用于pytest fixture）"""
    db_manager = TestDatabaseManager()
    await db_manager.initialize()
    return db_manager


async def teardown_test_database(db_manager: TestDatabaseManager):
    """清理测试数据库（用于pytest fixture）"""
    await db_manager.cleanup()