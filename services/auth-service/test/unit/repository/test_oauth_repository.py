#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OAuth仓储单元测试
测试OAuth连接相关存储操作
"""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from internal.repository.oauth_repository import OAuthRepository
from internal.model.user import OAuthConnection
from internal.model.errors import DatabaseError, ValidationError


@pytest.fixture
def mock_session():
    """创建模拟会话"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def oauth_repo(mock_session):
    """创建OAuth仓储实例"""
    return OAuthRepository(mock_session)


@pytest.fixture
def mock_oauth_connection():
    """创建模拟OAuth连接"""
    connection = MagicMock(spec=OAuthConnection)
    connection.id = str(uuid.uuid4())
    connection.user_id = str(uuid.uuid4())
    connection.provider = "github"
    connection.provider_user_id = "12345"
    connection.access_token = "access_token_123"
    connection.refresh_token = "refresh_token_123"
    connection.expires_at = datetime.now(UTC) + timedelta(hours=1)
    connection.user_data = {"name": "Test User", "email": "test@example.com"}
    connection.created_at = datetime.now(UTC)
    connection.updated_at = datetime.now(UTC)
    return connection


class TestOAuthRepository:
    """OAuth仓储单元测试"""

    @pytest.mark.asyncio
    async def test_create_connection_success(self, oauth_repo, mock_session):
        """测试成功创建OAuth连接"""
        # 设置模拟行为
        user_id = str(uuid.uuid4())
        provider = "github"
        provider_user_id = "12345"
        access_token = "test_access_token"
        refresh_token = "test_refresh_token"
        user_data = {"name": "Test User", "email": "test@example.com"}
        
        # 模拟get_connection_by_provider_id返回None
        oauth_repo.get_connection_by_provider_id = AsyncMock(return_value=None)
        
        # 创建一个返回结果的模拟对象
        result = MagicMock()
        result.scalar_one.return_value = MagicMock(spec=OAuthConnection)
        mock_session.execute.return_value = result
        
        # 调用方法
        await oauth_repo.create_connection(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            user_data=user_data
        )
        
        # 验证结果
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_create_connection_already_exists(self, oauth_repo, mock_oauth_connection):
        """测试创建已存在的OAuth连接"""
        # 设置模拟行为
        oauth_repo.get_connection_by_provider_id = AsyncMock(return_value=mock_oauth_connection)
        
        # 调用方法并验证异常
        with pytest.raises(ValidationError, match="此github账号已关联到其他用户"):
            await oauth_repo.create_connection(
                user_id=str(uuid.uuid4()),
                provider="github",
                provider_user_id="12345",
                access_token="test_access_token"
            )
            
    @pytest.mark.asyncio
    async def test_create_connection_database_error(self, oauth_repo, mock_session):
        """测试创建OAuth连接数据库错误"""
        # 设置模拟行为
        oauth_repo.get_connection_by_provider_id = AsyncMock(return_value=None)
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="创建OAuth连接失败"):
            await oauth_repo.create_connection(
                user_id=str(uuid.uuid4()),
                provider="github",
                provider_user_id="12345",
                access_token="test_access_token"
            )
        
        # 验证回滚
        mock_session.rollback.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_connection_success(self, oauth_repo, mock_session):
        """测试成功更新OAuth连接"""
        # 设置模拟行为
        connection_id = str(uuid.uuid4())
        access_token = "new_access_token"
        user_data = {"name": "Updated User", "email": "updated@example.com"}
        
        result = MagicMock()
        result.rowcount = 1
        mock_session.execute.return_value = result
        
        # 调用方法
        success = await oauth_repo.update_connection(
            connection_id=connection_id,
            access_token=access_token,
            user_data=user_data
        )
        
        # 验证结果
        assert success is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_connection_no_data(self, oauth_repo, mock_session):
        """测试更新OAuth连接没有数据"""
        # 调用方法不提供任何更新数据
        success = await oauth_repo.update_connection(
            connection_id=str(uuid.uuid4())
        )
        
        # 验证结果 - 不应该执行数据库操作
        assert success is True
        mock_session.execute.assert_not_called()
        mock_session.commit.assert_not_called()
        
    @pytest.mark.asyncio
    async def test_update_connection_error(self, oauth_repo, mock_session):
        """测试更新OAuth连接错误"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="更新OAuth连接失败"):
            await oauth_repo.update_connection(
                connection_id=str(uuid.uuid4()),
                access_token="test_token"
            )
        
        # 验证回滚
        mock_session.rollback.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_connection_by_id_found(self, oauth_repo, mock_session, mock_oauth_connection):
        """测试通过ID获取存在的OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_oauth_connection
        mock_session.execute.return_value = result
        
        # 调用方法
        connection = await oauth_repo.get_connection_by_id(mock_oauth_connection.id)
        
        # 验证结果
        assert connection == mock_oauth_connection
        mock_session.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_connection_by_id_not_found(self, oauth_repo, mock_session):
        """测试通过ID获取不存在的OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = result
        
        # 调用方法
        connection = await oauth_repo.get_connection_by_id(str(uuid.uuid4()))
        
        # 验证结果
        assert connection is None
        mock_session.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_connection_by_id_error(self, oauth_repo, mock_session):
        """测试通过ID获取OAuth连接出错"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="获取OAuth连接失败"):
            await oauth_repo.get_connection_by_id(str(uuid.uuid4()))
    
    @pytest.mark.asyncio
    async def test_get_connection_by_provider_id_found(self, oauth_repo, mock_session, mock_oauth_connection):
        """测试通过提供商ID获取存在的OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_oauth_connection
        mock_session.execute.return_value = result
        
        # 调用方法
        connection = await oauth_repo.get_connection_by_provider_id(
            provider="github",
            provider_user_id="12345"
        )
        
        # 验证结果
        assert connection == mock_oauth_connection
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_connection_by_provider_and_user_id_found(self, oauth_repo, mock_session, mock_oauth_connection):
        """测试通过提供商和用户ID获取存在的OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar_one_or_none.return_value = mock_oauth_connection
        mock_session.execute.return_value = result
        
        # 调用方法
        connection = await oauth_repo.get_connection_by_provider_and_user_id(
            provider="github",
            user_id=mock_oauth_connection.user_id
        )
        
        # 验证结果
        assert connection == mock_oauth_connection
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_connections(self, oauth_repo, mock_session, mock_oauth_connection):
        """测试获取用户的所有OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.scalars().all.return_value = [mock_oauth_connection]
        mock_session.execute.return_value = result
        
        # 调用方法
        connections = await oauth_repo.get_user_connections(mock_oauth_connection.user_id)
        
        # 验证结果
        assert len(connections) == 1
        assert connections[0] == mock_oauth_connection
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_connections_error(self, oauth_repo, mock_session):
        """测试获取用户的所有OAuth连接出错"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="获取用户OAuth连接失败"):
            await oauth_repo.get_user_connections(str(uuid.uuid4()))
    
    @pytest.mark.asyncio
    async def test_delete_connection_success(self, oauth_repo, mock_session):
        """测试成功删除OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.rowcount = 1
        mock_session.execute.return_value = result
        
        # 调用方法
        success = await oauth_repo.delete_connection(str(uuid.uuid4()))
        
        # 验证结果
        assert success is True
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_connection_not_found(self, oauth_repo, mock_session):
        """测试删除不存在的OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.rowcount = 0
        mock_session.execute.return_value = result
        
        # 调用方法
        success = await oauth_repo.delete_connection(str(uuid.uuid4()))
        
        # 验证结果
        assert success is False
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_connection_error(self, oauth_repo, mock_session):
        """测试删除OAuth连接出错"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="删除OAuth连接失败"):
            await oauth_repo.delete_connection(str(uuid.uuid4()))
        
        # 验证回滚
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_user_connections(self, oauth_repo, mock_session):
        """测试计算用户连接数量"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar.return_value = 3
        mock_session.execute.return_value = result
        
        # 调用方法
        count = await oauth_repo.count_user_connections(str(uuid.uuid4()))
        
        # 验证结果
        assert count == 3
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_user_connections_zero(self, oauth_repo, mock_session):
        """测试计算用户连接数量为零"""
        # 设置模拟行为
        result = MagicMock()
        result.scalar.return_value = None
        mock_session.execute.return_value = result
        
        # 调用方法
        count = await oauth_repo.count_user_connections(str(uuid.uuid4()))
        
        # 验证结果
        assert count == 0
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_count_user_connections_error(self, oauth_repo, mock_session):
        """测试计算用户连接数量出错"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="计算用户OAuth连接数量失败"):
            await oauth_repo.count_user_connections(str(uuid.uuid4()))
    
    @pytest.mark.asyncio
    async def test_delete_user_connections(self, oauth_repo, mock_session):
        """测试删除用户的所有OAuth连接"""
        # 设置模拟行为
        result = MagicMock()
        result.rowcount = 3
        mock_session.execute.return_value = result
        
        # 调用方法
        count = await oauth_repo.delete_user_connections(str(uuid.uuid4()))
        
        # 验证结果
        assert count == 3
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user_connections_error(self, oauth_repo, mock_session):
        """测试删除用户的所有OAuth连接出错"""
        # 设置模拟行为
        mock_session.execute.side_effect = Exception("数据库错误")
        
        # 调用方法并验证异常
        with pytest.raises(DatabaseError, match="删除用户OAuth连接失败"):
            await oauth_repo.delete_user_connections(str(uuid.uuid4()))