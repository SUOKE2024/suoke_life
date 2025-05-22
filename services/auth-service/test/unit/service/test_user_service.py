#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户服务单元测试
测试用户相关服务功能
"""
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC, timedelta

from internal.service.user_service import UserService
from internal.repository.user_repository import UserRepository
from internal.security.password import PasswordHasher
from internal.security.jwt import JWTSecurity
from internal.model.user import User, UserCreate, UserResponse
from internal.model.errors import (
    AuthenticationError, 
    ValidationError, 
    UserNotFoundError,
    DatabaseError
)


@pytest.fixture
def mock_user_repo():
    """模拟用户仓储"""
    repo = AsyncMock(spec=UserRepository)
    return repo


@pytest.fixture
def mock_password_hasher():
    """模拟密码哈希器"""
    hasher = MagicMock(spec=PasswordHasher)
    hasher.hash_password.return_value = "hashed_password"
    hasher.verify_password.return_value = True
    return hasher


@pytest.fixture
def mock_jwt_security():
    """模拟JWT安全工具"""
    jwt = MagicMock(spec=JWTSecurity)
    jwt.create_access_token.return_value = "access_token"
    jwt.create_refresh_token.return_value = "refresh_token"
    return jwt


@pytest.fixture
def user_service(mock_user_repo, mock_password_hasher, mock_jwt_security):
    """创建用户服务实例"""
    return UserService(
        user_repository=mock_user_repo,
        password_hasher=mock_password_hasher,
        jwt_security=mock_jwt_security
    )


@pytest.fixture
def mock_user():
    """创建模拟用户"""
    user = MagicMock(spec=User)
    user.id = str(uuid.uuid4())
    user.username = "testuser"
    user.email = "test@example.com"
    user.password = "hashed_password"
    user.phone_number = "13800138000"
    user.profile_data = {}
    user.is_active = True
    user.is_locked = False
    user.failed_login_attempts = 0
    user.lock_until = None
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


class TestUserService:
    """用户服务测试类"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user_repo):
        """测试成功创建用户"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = None
        mock_user_repo.get_user_by_email.return_value = None
        mock_user_repo.create_user.return_value = MagicMock(
            id="user123",
            username="newuser",
            email="new@example.com"
        )
        
        # 创建测试数据
        user_data = UserCreate(
            username="newuser",
            email="new@example.com", 
            password="password123",
            phone_number="13800138000"
        )
        
        # 调用服务
        user = await user_service.create_user(user_data)
        
        # 验证结果
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert "id" in user.__dict__
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("newuser")
        mock_user_repo.get_user_by_email.assert_called_once_with("new@example.com")
        mock_user_repo.create_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_username_exists(self, user_service, mock_user_repo, mock_user):
        """测试创建用户时用户名已存在"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = mock_user
        
        # 创建测试数据
        user_data = UserCreate(
            username="testuser",  # 已存在的用户名
            email="new@example.com", 
            password="password123",
            phone_number="13800138000"
        )
        
        # 调用服务，应该抛出异常
        with pytest.raises(ValidationError, match="用户名已存在"):
            await user_service.create_user(user_data)
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_user_repo.create_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_user_email_exists(self, user_service, mock_user_repo, mock_user):
        """测试创建用户时邮箱已存在"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = None
        mock_user_repo.get_user_by_email.return_value = mock_user
        
        # 创建测试数据
        user_data = UserCreate(
            username="newuser",
            email="test@example.com",  # 已存在的邮箱
            password="password123",
            phone_number="13800138000"
        )
        
        # 调用服务，应该抛出异常
        with pytest.raises(ValidationError, match="邮箱已被注册"):
            await user_service.create_user(user_data)
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("newuser")
        mock_user_repo.get_user_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.create_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_service, mock_user_repo, mock_user, mock_password_hasher):
        """测试用户认证成功"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = mock_user
        
        # 调用服务
        user = await user_service.authenticate_user("testuser", "password123")
        
        # 验证结果
        assert user.id == mock_user.id
        assert user.username == mock_user.username
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_password_hasher.verify_password.assert_called_once_with("password123", mock_user.password)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service, mock_user_repo):
        """测试认证时用户不存在"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = None
        
        # 调用服务，应该抛出异常
        with pytest.raises(AuthenticationError, match="用户名或密码错误"):
            await user_service.authenticate_user("wronguser", "password123")
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("wronguser")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_service, mock_user_repo, mock_user, mock_password_hasher):
        """测试认证时密码错误"""
        # 设置模拟行为
        mock_user_repo.get_user_by_username.return_value = mock_user
        mock_password_hasher.verify_password.return_value = False
        
        # 调用服务，应该抛出异常
        with pytest.raises(AuthenticationError, match="用户名或密码错误"):
            await user_service.authenticate_user("testuser", "wrongpassword")
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_password_hasher.verify_password.assert_called_once_with("wrongpassword", mock_user.password)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, user_service, mock_user_repo, mock_user):
        """测试认证时用户不活跃"""
        # 设置模拟行为
        mock_user = MagicMock(spec=User)
        mock_user.is_active = False
        mock_user_repo.get_user_by_username.return_value = mock_user
        
        # 调用服务，应该抛出异常
        with pytest.raises(AuthenticationError, match="账户已禁用"):
            await user_service.authenticate_user("testuser", "password123")
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_locked(self, user_service, mock_user_repo, mock_user):
        """测试认证时用户被锁定"""
        # 设置模拟行为
        mock_user.is_locked = True
        mock_user.lock_until = datetime.now(UTC) + timedelta(minutes=10)
        mock_user_repo.get_user_by_username.return_value = mock_user
        
        # 调用服务，应该抛出异常
        with pytest.raises(AuthenticationError, match="账户已锁定"):
            await user_service.authenticate_user("testuser", "password123")
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_unlocks_expired_lock(self, user_service, mock_user_repo, mock_user, mock_password_hasher):
        """测试认证时自动解锁过期锁定"""
        # 设置模拟行为
        mock_user.is_locked = True
        mock_user.lock_until = datetime.now(UTC) - timedelta(minutes=10)  # 锁定已过期
        mock_user_repo.get_user_by_username.return_value = mock_user
        
        # 调用服务
        user = await user_service.authenticate_user("testuser", "password123")
        
        # 验证结果
        assert user.id == mock_user.id
        
        # 验证函数调用
        mock_user_repo.get_user_by_username.assert_called_once_with("testuser")
        mock_user_repo.update_user.assert_called_once()  # 应该更新用户解锁
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, mock_user_repo, mock_user):
        """测试成功获取用户"""
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 调用服务
        user = await user_service.get_user(mock_user.id)
        
        # 验证结果
        assert user.id == mock_user.id
        assert user.username == mock_user.username
        
        # 验证函数调用
        mock_user_repo.get_user_by_id.assert_called_once_with(mock_user.id)
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user_repo):
        """测试获取不存在的用户"""
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = None
        
        # 调用服务，应该抛出异常
        with pytest.raises(UserNotFoundError):
            await user_service.get_user("nonexistent_id")
        
        # 验证函数调用
        mock_user_repo.get_user_by_id.assert_called_once_with("nonexistent_id")
    
    @pytest.mark.asyncio
    async def test_login_success(self, user_service, mock_user_repo, mock_user, mock_jwt_security):
        """测试用户登录成功"""
        # 设置模拟行为
        user_service.authenticate_user = AsyncMock(return_value=mock_user)
        mock_jwt_security.create_access_token.return_value = "access_token"
        mock_jwt_security.create_refresh_token.return_value = "refresh_token"
        
        # 调用服务
        token_response = await user_service.login("testuser", "password123")
        
        # 验证结果
        assert token_response.access_token == "access_token"
        assert token_response.refresh_token == "refresh_token"
        assert token_response.token_type == "bearer"
        
        # 验证函数调用
        user_service.authenticate_user.assert_called_once_with("testuser", "password123")
        mock_jwt_security.create_access_token.assert_called_once()
        mock_jwt_security.create_refresh_token.assert_called_once() 