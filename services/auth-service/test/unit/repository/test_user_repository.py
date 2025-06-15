#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户仓储单元测试
"""
import uuid
from datetime import datetime, UTC
import pytest
from unittest.mock import MagicMock, AsyncMock

import asyncpg
from internal.repository.user_repository import UserRepository
from internal.model.errors import DatabaseError, UserExistsError, UserNotFoundError


@pytest.fixture
def mock_pool():
    """创建模拟数据库连接池"""
    pool = MagicMock(spec=asyncpg.Pool)
    conn = AsyncMock(spec=asyncpg.Connection)
    
    # 正确设置AsyncMock作为异步上下文管理器
    async_context = AsyncMock()
    async_context.__aenter__.return_value = conn
    
    # 确保pool.acquire()返回异步上下文管理器而不是协程
    pool.acquire.return_value = async_context
    
    return pool, conn


@pytest.fixture
def user_repository(mock_pool):
    """创建用户仓储实例"""
    pool, _ = mock_pool
    return UserRepository(pool)


class TestUserRepository:
    """用户仓储测试"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository, mock_pool):
        """测试成功创建用户"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "testuser"
        email = "test@example.com"
        hashed_password = "hashed_password_value"
        phone_number = "1234567890"
        profile_data = {"displayName": "Test User"}
        
        # 模拟数据库返回值
        user_id = str(uuid.uuid4())
        conn.fetchrow.return_value = None  # 不存在冲突的用户
        conn.fetchval.return_value = False  # 用户名不存在
        
        # 执行方法
        result = await user_repository.create_user(
            username, email, hashed_password, phone_number, profile_data
        )
        
        # 验证结果 - 返回的是(user_id, username, email)元组
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert result[1] == username
        assert result[2] == email
        
        # 验证数据库操作
        conn.execute.assert_called()
        
    @pytest.mark.asyncio
    async def test_create_user_username_exists(self, user_repository, mock_pool):
        """测试创建用户时用户名已存在"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "existinguser"
        email = "test@example.com"
        hashed_password = "hashed_password_value"
        
        # 模拟用户已存在的返回
        conn.fetchrow.return_value = {"id": str(uuid.uuid4())}  # 存在冲突用户
        conn.fetchval.return_value = True  # 用户名冲突
        
        # 执行方法，期望抛出异常
        with pytest.raises(UserExistsError) as exc_info:
            await user_repository.create_user(username, email, hashed_password)
        
        # 验证异常信息
        assert "用户名" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_create_user_email_exists(self, user_repository, mock_pool):
        """测试创建用户时邮箱已存在"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "newuser"
        email = "existing@example.com"
        hashed_password = "hashed_password_value"
        
        # 模拟邮箱已存在
        conn.fetchrow.return_value = {"id": str(uuid.uuid4())}  # 存在冲突用户
        conn.fetchval.return_value = False  # 不是用户名冲突，而是邮箱冲突
        
        # 执行方法，期望抛出异常
        with pytest.raises(UserExistsError) as exc_info:
            await user_repository.create_user(username, email, hashed_password)
        
        # 验证异常信息
        assert "电子邮件" in str(exc_info.value)
        
    @pytest.mark.asyncio
    async def test_create_user_db_error(self, user_repository, mock_pool):
        """测试创建用户时数据库错误"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "testuser"
        email = "test@example.com"
        hashed_password = "hashed_password_value"
        
        # 模拟数据库错误
        conn.fetchval.side_effect = Exception("Database connection error")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await user_repository.create_user(username, email, hashed_password)
            
    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, user_repository, mock_pool):
        """测试通过ID获取用户成功"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        expected_user = {
            "id": user_id,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.now(UTC),
            "mfa_enabled": False
        }
        
        # 模拟数据库返回值
        conn.fetchrow.return_value = expected_user
        
        # 执行方法
        result = await user_repository.get_user_by_id(user_id)
        
        # 验证结果
        assert result == expected_user
        
        # 验证数据库操作
        conn.fetchrow.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repository, mock_pool):
        """测试通过ID获取不存在的用户"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟数据库返回空结果
        conn.fetchrow.return_value = None
        
        # 执行方法，期望抛出异常
        with pytest.raises(UserNotFoundError):
            await user_repository.get_user_by_id(user_id)
            
    @pytest.mark.asyncio
    async def test_get_user_by_id_db_error(self, user_repository, mock_pool):
        """测试通过ID获取用户时数据库错误"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟数据库错误
        conn.fetchrow.side_effect = Exception("Database connection error")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await user_repository.get_user_by_id(user_id)
            
    @pytest.mark.asyncio
    async def test_get_user_by_username_found(self, user_repository, mock_pool):
        """测试通过用户名获取用户成功"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "testuser"
        expected_user = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": "test@example.com",
            "created_at": datetime.now(UTC),
            "mfa_enabled": False
        }
        
        # 模拟数据库返回值
        conn.fetchrow.return_value = expected_user
        
        # 执行方法
        result = await user_repository.get_user_by_username(username)
        
        # 验证结果
        assert result == expected_user
        
        # 验证数据库操作
        conn.fetchrow.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_repository, mock_pool):
        """测试通过用户名获取不存在的用户"""
        pool, conn = mock_pool
        
        # 准备测试数据
        username = "nonexistentuser"
        
        # 模拟数据库返回空结果
        conn.fetchrow.return_value = None
        
        # 执行方法，期望抛出异常
        with pytest.raises(UserNotFoundError):
            await user_repository.get_user_by_username(username)
            
    @pytest.mark.asyncio
    async def test_update_password_success(self, user_repository, mock_pool):
        """测试成功更新密码"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        hashed_password = "new_hashed_password"
        
        # 模拟数据库返回值
        conn.execute.return_value = "UPDATE 1"
        
        # 执行方法
        result = await user_repository.update_password(user_id, hashed_password)
        
        # 验证结果
        assert result is True
        
        # 验证数据库操作
        conn.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_password_user_not_found(self, user_repository, mock_pool):
        """测试更新不存在用户的密码"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        hashed_password = "new_hashed_password"
        
        # 模拟数据库返回值（没有更新任何行）
        conn.execute.return_value = "UPDATE 0"
        
        # 执行方法，期望抛出异常
        with pytest.raises(UserNotFoundError):
            await user_repository.update_password(user_id, hashed_password)
            
    @pytest.mark.asyncio
    async def test_update_password_db_error(self, user_repository, mock_pool):
        """测试更新密码时数据库错误"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        hashed_password = "new_hashed_password"
        
        # 模拟数据库错误
        conn.execute.side_effect = Exception("Database connection error")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await user_repository.update_password(user_id, hashed_password)
            
    @pytest.mark.asyncio
    async def test_enable_mfa_success(self, user_repository, mock_pool):
        """测试成功启用MFA"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        mfa_type = "totp"
        mfa_secret = "secret_key_value"
        
        # 模拟数据库返回值
        conn.execute.return_value = "UPDATE 1"
        
        # 执行方法
        result = await user_repository.enable_mfa(user_id, mfa_type, mfa_secret)
        
        # 验证结果
        assert result is True
        
        # 验证数据库操作
        conn.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_disable_mfa_success(self, user_repository, mock_pool):
        """测试成功禁用MFA"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟数据库返回值
        conn.execute.return_value = "UPDATE 1"
        
        # 执行方法
        result = await user_repository.disable_mfa(user_id)
        
        # 验证结果
        assert result is True
        
        # 验证数据库操作
        conn.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_roles_success(self, user_repository, mock_pool):
        """测试成功获取用户角色"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        expected_roles = [
            {"id": "1", "name": "admin", "description": "Administrator", "permissions": ["admin", "user"]},
            {"id": "2", "name": "user", "description": "Regular User", "permissions": ["admin", "user"]}
        ]
        
        # 模拟数据库返回值和权限查询结果
        conn.fetch.return_value = [
            {"id": "1", "name": "admin", "description": "Administrator"},
            {"id": "2", "name": "user", "description": "Regular User"}
        ]
        
        # 模拟角色权限查询，返回权限列表
        permission_query_result = AsyncMock()
        permission_query_result.fetch.return_value = [
            {"name": "admin"}, 
            {"name": "user"}
        ]
        conn.transaction.return_value.__aenter__.return_value = permission_query_result
        
        # 执行方法
        result = await user_repository.get_user_roles(user_id)
        
        # 验证结果
        assert result == expected_roles
        
    @pytest.mark.asyncio
    async def test_get_user_roles_empty(self, user_repository, mock_pool):
        """测试获取无角色用户的角色"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟数据库返回空结果
        conn.fetch.return_value = []
        
        # 执行方法
        result = await user_repository.get_user_roles(user_id)
        
        # 验证结果
        assert result == []
        
        # 验证数据库操作
        conn.fetch.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_roles_db_error(self, user_repository, mock_pool):
        """测试获取用户角色时数据库错误"""
        pool, conn = mock_pool
        
        # 准备测试数据
        user_id = str(uuid.uuid4())
        
        # 模拟数据库错误
        conn.fetch.side_effect = Exception("Database connection error")
        
        # 执行方法，期望抛出异常
        with pytest.raises(DatabaseError):
            await user_repository.get_user_roles(user_id)