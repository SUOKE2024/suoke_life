"""
test_database_manager_sqlite_compatible - 索克生活项目模块
"""

from auth_service.core.database import DatabaseManager
from datetime import datetime
from sqlalchemy import event, JSON, Text, String, Boolean, DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator, Optional
import asyncio
import os
import tempfile
import uuid

"""
SQLite兼容的测试专用数据库管理器
解决JSONB类型不兼容问题
"""




class SQLiteCompatibleBase(DeclarativeBase):
    """SQLite兼容的基础模型类"""
    
    # 主键
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),  # SQLite使用字符串存储UUID
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="主键ID"
    )
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="创建时间"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间"
    )


class TestUser(SQLiteCompatibleBase):
    """测试用户模型（SQLite兼容）"""
    
    __tablename__ = "users"
    
    # 基本信息
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="用户名"
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        comment="邮箱"
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="手机号"
    )
    
    # 密码相关
    password_hash: Mapped[str] = mapped_column(
        String(255),
        comment="密码哈希"
    )
    
    # 状态信息
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已验证"
    )
    
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否为超级用户"
    )
    
    # 登录信息
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="最后登录时间"
    )
    
    login_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="登录次数"
    )
    
    # 元数据（使用TEXT存储JSON字符串）
    user_metadata: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="用户元数据JSON"
    )


class TestDatabaseManager:
    """SQLite兼容的测试专用数据库管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        初始化测试数据库管理器
        
        Args:
            database_url: 数据库URL，默认使用内存SQLite
        """
        if database_url is None:
            # 使用内存SQLite数据库
            database_url = "sqlite+aiosqlite:///:memory:"
        
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库连接和表结构"""
        if self._initialized:
            return
        
        # 创建异步引擎
        self.engine = create_async_engine(
            self.database_url,
            echo=False,  # 测试时不输出SQL日志
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
            } if "sqlite" in self.database_url else {},
        )
        
        # 创建会话工厂
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # 创建所有表
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLiteCompatibleBase.metadata.create_all)
        
        self._initialized = True
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
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
    
    async def cleanup(self):
        """清理数据库连接"""
        if self.engine:
            await self.engine.dispose()
        self._initialized = False
    
    async def reset_database(self):
        """重置数据库（删除所有数据）"""
        if not self._initialized:
            return
        
        async with self.engine.begin() as conn:
            # 删除所有表
            await conn.run_sync(SQLiteCompatibleBase.metadata.drop_all)
            # 重新创建所有表
            await conn.run_sync(SQLiteCompatibleBase.metadata.create_all)


# 全局测试数据库管理器实例
_test_db_manager: Optional[TestDatabaseManager] = None


async def get_test_db_manager() -> TestDatabaseManager:
    """获取测试数据库管理器"""
    global _test_db_manager
    if _test_db_manager is None:
        _test_db_manager = TestDatabaseManager()
        await _test_db_manager.initialize()
    return _test_db_manager


async def cleanup_test_db_manager():
    """清理测试数据库管理器"""
    global _test_db_manager
    if _test_db_manager:
        await _test_db_manager.cleanup()
        _test_db_manager = None


async def setup_test_database() -> TestDatabaseManager:
    """设置测试数据库（用于pytest fixture）"""
    db_manager = TestDatabaseManager()
    await db_manager.initialize()
    return db_manager


async def teardown_test_database(db_manager: TestDatabaseManager):
    """清理测试数据库（用于pytest fixture）"""
    await db_manager.cleanup() 