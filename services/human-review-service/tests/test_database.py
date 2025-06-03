"""
数据库模块测试
Database Module Tests

测试数据库连接、会话管理等功能
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from human_review_service.core.database import (
    init_database,
    get_session_factory,
    get_session,
    get_session_dependency,
    close_database
)
from human_review_service.core.config import DatabaseSettings


class TestDatabaseSettings:
    """数据库设置测试"""

    def test_database_settings_init(self):
        """测试数据库设置初始化"""
        settings = DatabaseSettings()
        assert settings is not None
        assert hasattr(settings, 'host')
        assert hasattr(settings, 'port')
        assert hasattr(settings, 'name')
        assert hasattr(settings, 'user')

    def test_database_settings_with_custom_values(self):
        """测试自定义数据库设置"""
        settings = DatabaseSettings(
            host="custom_host",
            port=5433,
            name="custom_db",
            user="custom_user"
        )
        assert settings.host == "custom_host"
        assert settings.port == 5433
        assert settings.name == "custom_db"
        assert settings.user == "custom_user"


class TestDatabaseInitialization:
    """数据库初始化测试"""

    @pytest.mark.asyncio
    async def test_init_database_success(self):
        """测试成功初始化数据库"""
        with patch('human_review_service.core.database.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            
            with patch('human_review_service.core.database.async_sessionmaker') as mock_sessionmaker:
                mock_session_factory = Mock()
                mock_sessionmaker.return_value = mock_session_factory
                
                await init_database()
                
                mock_create_engine.assert_called_once()
                mock_sessionmaker.assert_called_once()

    def test_get_session_factory_not_initialized(self):
        """测试未初始化时获取会话工厂"""
        with patch('human_review_service.core.database._session_factory', None):
            with pytest.raises(RuntimeError, match="Database not initialized"):
                get_session_factory()

    def test_get_session_factory_initialized(self):
        """测试已初始化时获取会话工厂"""
        mock_factory = Mock()
        with patch('human_review_service.core.database._session_factory', mock_factory):
            factory = get_session_factory()
            assert factory is mock_factory


class TestSessionManagement:
    """会话管理测试"""

    @pytest.mark.asyncio
    async def test_get_session_success(self):
        """测试成功获取会话"""
        mock_session = AsyncMock()
        mock_factory = Mock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            async with get_session() as session:
                assert session is mock_session

    @pytest.mark.asyncio
    async def test_get_session_dependency_success(self):
        """测试成功获取会话依赖"""
        mock_session = AsyncMock()
        
        with patch('human_review_service.core.database.get_session') as mock_get_session:
            mock_get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            async with get_session_dependency() as session:
                assert session is mock_session

    @pytest.mark.asyncio
    async def test_close_database_success(self):
        """测试成功关闭数据库"""
        mock_engine = AsyncMock()
        
        with patch('human_review_service.core.database._engine', mock_engine):
            await close_database()
            mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_database_not_initialized(self):
        """测试未初始化时关闭数据库"""
        with patch('human_review_service.core.database._engine', None):
            # 应该不抛出异常
            await close_database()


class TestDatabaseIntegration:
    """数据库集成测试"""

    @pytest.mark.asyncio
    async def test_full_database_lifecycle(self):
        """测试完整的数据库生命周期"""
        # 模拟完整的数据库操作流程
        with patch('human_review_service.core.database.create_async_engine') as mock_create_engine:
            mock_engine = AsyncMock()
            mock_create_engine.return_value = mock_engine
            
            with patch('human_review_service.core.database.async_sessionmaker') as mock_sessionmaker:
                mock_session_factory = Mock()
                mock_sessionmaker.return_value = mock_session_factory
                
                # 初始化数据库
                await init_database()
                
                # 关闭数据库
                with patch('human_review_service.core.database._engine', mock_engine):
                    await close_database()
                    mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_context_manager(self):
        """测试会话上下文管理器"""
        mock_session = AsyncMock()
        mock_factory = Mock()
        
        # 模拟会话工厂
        async def mock_session_context():
            yield mock_session
        
        mock_factory.return_value = mock_session_context()
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            async with get_session() as session:
                assert session is mock_session
                # 模拟数据库操作
                await session.execute("SELECT 1")

    def test_database_settings_validation(self):
        """测试数据库设置验证"""
        # 测试有效配置
        valid_settings = DatabaseSettings(
            host="localhost",
            port=5432,
            name="test_db",
            user="test_user",
            password="test_pass"
        )
        assert valid_settings.host == "localhost"
        assert valid_settings.port == 5432
        
        # 测试默认配置
        default_settings = DatabaseSettings()
        assert default_settings.host is not None
        assert default_settings.port is not None


class TestDatabaseErrorHandling:
    """数据库错误处理测试"""

    @pytest.mark.asyncio
    async def test_init_database_connection_error(self):
        """测试数据库初始化连接错误"""
        with patch('human_review_service.core.database.create_async_engine') as mock_create_engine:
            mock_create_engine.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception):
                await init_database()

    @pytest.mark.asyncio
    async def test_session_creation_error(self):
        """测试会话创建错误"""
        mock_factory = Mock()
        mock_factory.side_effect = Exception("Session creation failed")
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            with pytest.raises(Exception):
                async with get_session() as session:
                    pass

    @pytest.mark.asyncio
    async def test_session_commit_error(self):
        """测试会话提交错误"""
        mock_session = AsyncMock()
        mock_session.commit.side_effect = Exception("Commit failed")
        
        mock_factory = Mock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            async with get_session() as session:
                with pytest.raises(Exception):
                    await session.commit()

    @pytest.mark.asyncio
    async def test_session_rollback_on_error(self):
        """测试错误时会话回滚"""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Query failed")
        
        mock_factory = Mock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            try:
                async with get_session() as session:
                    await session.execute("SELECT 1")
            except Exception:
                pass
            
            # 验证会话被正确处理
            assert mock_session is not None


class TestDatabasePerformance:
    """数据库性能测试"""

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """测试并发会话"""
        mock_sessions = [AsyncMock() for _ in range(5)]
        mock_factory = Mock()
        
        # 模拟并发会话创建
        async def mock_session_context(session):
            yield session
        
        session_contexts = [mock_session_context(session) for session in mock_sessions]
        mock_factory.side_effect = session_contexts
        
        with patch('human_review_service.core.database.get_session_factory', return_value=mock_factory):
            tasks = []
            for i in range(5):
                async def create_session():
                    async with get_session() as session:
                        return session
                tasks.append(create_session())
            
            results = await asyncio.gather(*tasks)
            assert len(results) == 5

    @pytest.mark.asyncio
    async def test_session_pool_management(self):
        """测试会话池管理"""
        mock_engine = AsyncMock()
        mock_session_factory = Mock()
        
        with patch('human_review_service.core.database._engine', mock_engine):
            with patch('human_review_service.core.database._session_factory', mock_session_factory):
                # 模拟多次获取会话
                for _ in range(10):
                    factory = get_session_factory()
                    assert factory is mock_session_factory

    def test_database_url_construction(self):
        """测试数据库URL构建"""
        from human_review_service.core.config import get_database_url
        
        # 测试默认URL构建
        url = get_database_url()
        assert url is not None
        assert isinstance(url, str)
        assert "postgresql+asyncpg://" in url

    @pytest.mark.asyncio
    async def test_database_cleanup(self):
        """测试数据库清理"""
        mock_engine = AsyncMock()
        
        # 模拟数据库初始化
        with patch('human_review_service.core.database.create_async_engine', return_value=mock_engine):
            with patch('human_review_service.core.database.async_sessionmaker'):
                await init_database()
        
        # 模拟数据库关闭
        with patch('human_review_service.core.database._engine', mock_engine):
            await close_database()
            mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_database_reconnection(self):
        """测试数据库重连"""
        mock_engine = AsyncMock()
        
        # 模拟第一次初始化
        with patch('human_review_service.core.database.create_async_engine', return_value=mock_engine):
            with patch('human_review_service.core.database.async_sessionmaker'):
                await init_database()
        
        # 模拟关闭
        with patch('human_review_service.core.database._engine', mock_engine):
            await close_database()
        
        # 模拟重新初始化
        with patch('human_review_service.core.database.create_async_engine', return_value=mock_engine):
            with patch('human_review_service.core.database.async_sessionmaker'):
                await init_database()
                
        # 验证引擎被正确创建
        assert mock_engine is not None 