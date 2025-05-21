#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth服务单元测试

测试OAuth服务的核心功能，包括：
- OAuth授权流程
- 第三方认证集成
- OAuth令牌处理
"""
import uuid
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from aiohttp import ClientSession, ClientResponse

from internal.service import oauth_service
from internal.model.user import User, UserStatusEnum, OAuthConnection
from internal.repository.user_repository import UserRepository
from internal.repository.oauth_repository import OAuthRepository
from internal.repository.audit_repository import AuditRepository
from internal.service.auth_service import create_tokens

# 测试数据
TEST_USER_ID = uuid.uuid4()
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"
TEST_OAUTH_CLIENT_ID = "test_client_id"
TEST_OAUTH_CLIENT_SECRET = "test_client_secret"
TEST_OAUTH_REDIRECT_URI = "http://localhost/callback"
TEST_OAUTH_CODE = "test_auth_code"
TEST_OAUTH_STATE = "test_state"
TEST_OAUTH_TOKEN = "test_access_token"
TEST_OAUTH_REFRESH_TOKEN = "test_refresh_token"


@pytest.fixture
def mock_session():
    """模拟数据库会话"""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def mock_user():
    """创建模拟用户"""
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.username = TEST_USERNAME
    user.email = TEST_EMAIL
    user.status = UserStatusEnum.ACTIVE
    user.roles = []
    return user


@pytest.fixture
def mock_oauth_connection():
    """创建模拟OAuth连接"""
    connection = MagicMock(spec=OAuthConnection)
    connection.id = uuid.uuid4()
    connection.user_id = TEST_USER_ID
    connection.provider = "github"
    connection.provider_user_id = "12345"
    connection.access_token = TEST_OAUTH_TOKEN
    connection.refresh_token = TEST_OAUTH_REFRESH_TOKEN
    connection.expires_at = datetime.utcnow() + timedelta(hours=1)
    connection.created_at = datetime.utcnow()
    connection.updated_at = datetime.utcnow()
    connection.scopes = ["user:email", "read:user"]
    connection.user_data = {
        "id": "12345",
        "login": "githubuser",
        "name": "GitHub User",
        "email": "github@example.com"
    }
    return connection


@pytest.fixture
def mock_repositories(mock_session, mock_user, mock_oauth_connection):
    """设置模拟仓库"""
    with patch("internal.service.oauth_service.UserRepository") as mock_user_repo_class:
        with patch("internal.service.oauth_service.OAuthRepository") as mock_oauth_repo_class:
            with patch("internal.service.oauth_service.AuditRepository") as mock_audit_repo_class:
                # 设置UserRepository
                mock_user_repo = AsyncMock(spec=UserRepository)
                mock_user_repo.get_user_by_id.return_value = mock_user
                mock_user_repo.get_user_by_email.return_value = mock_user
                mock_user_repo.create_user.return_value = mock_user
                
                mock_user_repo_class.return_value = mock_user_repo
                
                # 设置OAuthRepository
                mock_oauth_repo = AsyncMock(spec=OAuthRepository)
                mock_oauth_repo.get_connection_by_provider_and_user_id.return_value = mock_oauth_connection
                mock_oauth_repo.create_connection.return_value = mock_oauth_connection
                mock_oauth_repo.update_connection.return_value = mock_oauth_connection
                mock_oauth_repo.delete_connection.return_value = True
                mock_oauth_repo.get_user_connections.return_value = [mock_oauth_connection]
                
                mock_oauth_repo_class.return_value = mock_oauth_repo
                
                # 设置AuditRepository
                mock_audit_repo = AsyncMock(spec=AuditRepository)
                mock_audit_repo.add_audit_log.return_value = True
                
                mock_audit_repo_class.return_value = mock_audit_repo
                
                yield {
                    "user_repo": mock_user_repo,
                    "oauth_repo": mock_oauth_repo,
                    "audit_repo": mock_audit_repo
                }


class TestOAuthProviders:
    """OAuth提供商测试"""
    
    def test_get_supported_providers(self):
        """测试获取支持的OAuth提供商"""
        providers = oauth_service.get_supported_providers()
        
        # 验证至少包含主要提供商
        assert "github" in providers
        assert "wechat" in providers
        
        # 验证每个提供商都有必要的字段
        for provider_id, provider_info in providers.items():
            assert "name" in provider_info
            assert "client_id" in provider_info
            assert "authorize_url" in provider_info
            assert "token_url" in provider_info
    
    def test_get_provider_by_id_valid(self):
        """测试通过ID获取有效提供商"""
        provider = oauth_service.get_provider_by_id("github")
        
        assert provider is not None
        assert provider["name"] == "GitHub"
        assert "client_id" in provider
        assert "authorize_url" in provider
        assert "token_url" in provider
    
    def test_get_provider_by_id_invalid(self):
        """测试通过ID获取无效提供商"""
        with pytest.raises(ValueError, match="不支持的OAuth提供商"):
            oauth_service.get_provider_by_id("invalid_provider")


class TestOAuthAuthorization:
    """OAuth授权流程测试"""
    
    @pytest.mark.asyncio
    async def test_get_authorize_url(self):
        """测试获取授权URL"""
        with patch("internal.service.oauth_service.os.environ") as mock_env:
            # 模拟环境变量
            mock_env.get.side_effect = lambda key, default=None: {
                "OAUTH_GITHUB_CLIENT_ID": TEST_OAUTH_CLIENT_ID,
                "OAUTH_GITHUB_REDIRECT_URI": TEST_OAUTH_REDIRECT_URI
            }.get(key, default)
            
            result = await oauth_service.get_authorize_url("github", "test_state")
            
            # 验证结果包含必要参数
            assert "github.com/login/oauth/authorize" in result
            assert f"client_id={TEST_OAUTH_CLIENT_ID}" in result
            assert f"redirect_uri={TEST_OAUTH_REDIRECT_URI}" in result
            assert "state=test_state" in result
            assert "scope=" in result
    
    @pytest.mark.asyncio
    async def test_get_authorize_url_unsupported_provider(self):
        """测试获取不支持提供商的授权URL"""
        with pytest.raises(ValueError, match="不支持的OAuth提供商"):
            await oauth_service.get_authorize_url("invalid_provider", "test_state")
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self):
        """测试交换授权码获取令牌"""
        mock_response = MagicMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": TEST_OAUTH_TOKEN,
            "refresh_token": TEST_OAUTH_REFRESH_TOKEN,
            "expires_in": 3600,
            "token_type": "bearer"
        })
        
        mock_session = MagicMock(spec=ClientSession)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch("internal.service.oauth_service.aiohttp.ClientSession", return_value=mock_session):
            with patch("internal.service.oauth_service.os.environ") as mock_env:
                # 模拟环境变量
                mock_env.get.side_effect = lambda key, default=None: {
                    "OAUTH_GITHUB_CLIENT_ID": TEST_OAUTH_CLIENT_ID,
                    "OAUTH_GITHUB_CLIENT_SECRET": TEST_OAUTH_CLIENT_SECRET,
                    "OAUTH_GITHUB_REDIRECT_URI": TEST_OAUTH_REDIRECT_URI
                }.get(key, default)
                
                token_response = await oauth_service.exchange_code_for_token(
                    "github", TEST_OAUTH_CODE, TEST_OAUTH_REDIRECT_URI)
                
                # 验证结果
                assert token_response["access_token"] == TEST_OAUTH_TOKEN
                assert token_response["refresh_token"] == TEST_OAUTH_REFRESH_TOKEN
                assert token_response["expires_in"] == 3600
                
                # 验证请求参数
                mock_session.post.assert_called_once()
                args, kwargs = mock_session.post.call_args
                assert "github.com/login/oauth/access_token" in args[0]
                assert kwargs["json"]["client_id"] == TEST_OAUTH_CLIENT_ID
                assert kwargs["json"]["client_secret"] == TEST_OAUTH_CLIENT_SECRET
                assert kwargs["json"]["code"] == TEST_OAUTH_CODE
                assert kwargs["json"]["redirect_uri"] == TEST_OAUTH_REDIRECT_URI
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token_error(self):
        """测试交换授权码失败"""
        mock_response = MagicMock(spec=ClientResponse)
        mock_response.status = 400
        mock_response.json = AsyncMock(return_value={"error": "invalid_request"})
        
        mock_session = MagicMock(spec=ClientSession)
        mock_session.post = AsyncMock(return_value=mock_response)
        
        with patch("internal.service.oauth_service.aiohttp.ClientSession", return_value=mock_session):
            with patch("internal.service.oauth_service.os.environ") as mock_env:
                # 模拟环境变量
                mock_env.get.side_effect = lambda key, default=None: {
                    "OAUTH_GITHUB_CLIENT_ID": TEST_OAUTH_CLIENT_ID,
                    "OAUTH_GITHUB_CLIENT_SECRET": TEST_OAUTH_CLIENT_SECRET,
                    "OAUTH_GITHUB_REDIRECT_URI": TEST_OAUTH_REDIRECT_URI
                }.get(key, default)
                
                with pytest.raises(ValueError, match="获取访问令牌失败"):
                    await oauth_service.exchange_code_for_token(
                        "github", TEST_OAUTH_CODE, TEST_OAUTH_REDIRECT_URI)


class TestUserProfile:
    """用户资料获取测试"""
    
    @pytest.mark.asyncio
    async def test_get_user_profile_github(self):
        """测试获取GitHub用户资料"""
        mock_response = MagicMock(spec=ClientResponse)
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "id": "12345",
            "login": "githubuser",
            "name": "GitHub User",
            "email": "github@example.com",
            "avatar_url": "https://github.com/avatar.png"
        })
        
        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = AsyncMock(return_value=mock_response)
        
        with patch("internal.service.oauth_service.aiohttp.ClientSession", return_value=mock_session):
            profile = await oauth_service.get_user_profile("github", TEST_OAUTH_TOKEN)
            
            # 验证结果
            assert profile["id"] == "12345"
            assert profile["email"] == "github@example.com"
            assert profile["name"] == "GitHub User"
            assert profile["username"] == "githubuser"
            assert profile["avatar_url"] == "https://github.com/avatar.png"
            
            # 验证请求参数
            mock_session.get.assert_called_once()
            args, kwargs = mock_session.get.call_args
            assert "api.github.com/user" in args[0]
            assert kwargs["headers"]["Authorization"] == f"Bearer {TEST_OAUTH_TOKEN}"
    
    @pytest.mark.asyncio
    async def test_get_user_profile_error(self):
        """测试获取用户资料失败"""
        mock_response = MagicMock(spec=ClientResponse)
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={"error": "Bad credentials"})
        
        mock_session = MagicMock(spec=ClientSession)
        mock_session.get = AsyncMock(return_value=mock_response)
        
        with patch("internal.service.oauth_service.aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(ValueError, match="获取用户资料失败"):
                await oauth_service.get_user_profile("github", TEST_OAUTH_TOKEN)


class TestOAuthAuthentication:
    """OAuth认证测试"""
    
    @pytest.mark.asyncio
    async def test_authenticate_with_oauth_existing_connection(self, mock_session, mock_user, mock_oauth_connection, mock_repositories):
        """测试使用现有OAuth连接认证"""
        # 模拟已存在的连接
        user_profile = {
            "id": "12345",
            "email": "github@example.com",
            "name": "GitHub User",
            "username": "githubuser"
        }
        
        with patch("internal.service.oauth_service.create_tokens") as mock_create_tokens:
            mock_create_tokens.return_value = {"access_token": "jwt_token"}
            
            result = await oauth_service.authenticate_with_oauth(
                provider="github",
                access_token=TEST_OAUTH_TOKEN,
                refresh_token=TEST_OAUTH_REFRESH_TOKEN,
                expires_in=3600,
                user_profile=user_profile,
                session=mock_session
            )
            
            # 验证结果
            assert result == {"access_token": "jwt_token"}
            
            # 验证仓库调用
            mock_repositories["oauth_repo"].get_connection_by_provider_and_user_id.assert_called_once_with(
                "github", "12345")
            mock_repositories["oauth_repo"].update_connection.assert_called_once()
            mock_create_tokens.assert_called_once_with(mock_user, mock_session)
    
    @pytest.mark.asyncio
    async def test_authenticate_with_oauth_new_user(self, mock_session, mock_repositories):
        """测试OAuth认证创建新用户"""
        # 模拟新用户
        mock_repositories["oauth_repo"].get_connection_by_provider_and_user_id.return_value = None
        mock_repositories["user_repo"].get_user_by_email.return_value = None
        
        user_profile = {
            "id": "12345",
            "email": "newuser@example.com",
            "name": "New User",
            "username": "newuser"
        }
        
        with patch("internal.service.oauth_service.create_tokens") as mock_create_tokens:
            mock_create_tokens.return_value = {"access_token": "jwt_token"}
            
            result = await oauth_service.authenticate_with_oauth(
                provider="github",
                access_token=TEST_OAUTH_TOKEN,
                refresh_token=TEST_OAUTH_REFRESH_TOKEN,
                expires_in=3600,
                user_profile=user_profile,
                session=mock_session
            )
            
            # 验证结果
            assert result == {"access_token": "jwt_token"}
            
            # 验证仓库调用 - 创建新用户
            mock_repositories["user_repo"].create_user.assert_called_once()
            mock_repositories["oauth_repo"].create_connection.assert_called_once()
            mock_create_tokens.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authenticate_with_oauth_link_existing_user(self, mock_session, mock_user, mock_repositories):
        """测试OAuth认证链接到现有用户"""
        # 模拟新连接但存在用户
        mock_repositories["oauth_repo"].get_connection_by_provider_and_user_id.return_value = None
        mock_repositories["user_repo"].get_user_by_email.return_value = mock_user
        
        user_profile = {
            "id": "12345",
            "email": TEST_EMAIL,  # 和现有用户相同的邮箱
            "name": "GitHub User",
            "username": "githubuser"
        }
        
        with patch("internal.service.oauth_service.create_tokens") as mock_create_tokens:
            mock_create_tokens.return_value = {"access_token": "jwt_token"}
            
            result = await oauth_service.authenticate_with_oauth(
                provider="github",
                access_token=TEST_OAUTH_TOKEN,
                refresh_token=TEST_OAUTH_REFRESH_TOKEN,
                expires_in=3600,
                user_profile=user_profile,
                session=mock_session
            )
            
            # 验证结果
            assert result == {"access_token": "jwt_token"}
            
            # 验证仓库调用 - 没有创建新用户，只创建了连接
            mock_repositories["user_repo"].create_user.assert_not_called()
            mock_repositories["oauth_repo"].create_connection.assert_called_once()
            mock_create_tokens.assert_called_once_with(mock_user, mock_session)


class TestOAuthConnections:
    """OAuth连接管理测试"""
    
    @pytest.mark.asyncio
    async def test_get_user_connections(self, mock_session, mock_user, mock_oauth_connection, mock_repositories):
        """测试获取用户OAuth连接"""
        result = await oauth_service.get_user_connections(mock_user, mock_session)
        
        # 验证结果
        assert len(result) == 1
        assert result[0] == mock_oauth_connection
        
        # 验证仓库调用
        mock_repositories["oauth_repo"].get_user_connections.assert_called_once_with(TEST_USER_ID)
    
    @pytest.mark.asyncio
    async def test_unlink_oauth_connection(self, mock_session, mock_user, mock_repositories):
        """测试解除OAuth连接"""
        result = await oauth_service.unlink_oauth_connection(mock_user, "github", mock_session)
        
        # 验证结果
        assert result is True
        
        # 验证仓库调用
        mock_repositories["oauth_repo"].delete_connection.assert_called_once_with(TEST_USER_ID, "github")
        mock_repositories["audit_repo"].add_audit_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unlink_oauth_connection_not_found(self, mock_session, mock_user, mock_repositories):
        """测试解除不存在的OAuth连接"""
        # 模拟删除失败
        mock_repositories["oauth_repo"].delete_connection.return_value = False
        
        with pytest.raises(ValueError, match="未找到OAuth连接"):
            await oauth_service.unlink_oauth_connection(mock_user, "nonexistent", mock_session)