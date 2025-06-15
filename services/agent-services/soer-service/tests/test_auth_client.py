"""
认证客户端测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from soer_service.clients.auth_client import AuthClient, get_auth_client


class TestAuthClient:
    """认证客户端测试类"""

    @pytest.fixture
    def auth_client(self):
        """创建认证客户端实例"""
        return AuthClient()

    @pytest.mark.asyncio
    async def test_verify_token_success(self, auth_client):
        """测试令牌验证成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "test_user_id",
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
            "is_active": True
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_client.verify_token("valid_token")
            
            assert result is not None
            assert result["user_id"] == "test_user_id"
            assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_client):
        """测试令牌验证失败"""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_client.verify_token("invalid_token")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_timeout(self, auth_client):
        """测试令牌验证超时"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Timeout")
            )
            
            result = await auth_client.verify_token("test_token")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, auth_client):
        """测试获取用户信息成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "test_user_id",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_client.get_user_info("test_user_id")
            
            assert result is not None
            assert result["user_id"] == "test_user_id"
            assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, auth_client):
        """测试获取用户档案成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": "test_user_id",
            "activity_level": "moderate",
            "dietary_preferences": ["vegetarian"],
            "health_goals": ["weight_loss"]
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_client.get_user_profile("test_user_id")
            
            assert result is not None
            assert result["user_id"] == "test_user_id"
            assert result["activity_level"] == "moderate"

    @pytest.mark.asyncio
    async def test_health_check_success(self, auth_client):
        """测试健康检查成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
            
            result = await auth_client.health_check()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, auth_client):
        """测试健康检查失败"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=Exception("Connection failed")
            )
            
            result = await auth_client.health_check()
            
            assert result is False

    def test_token_cache(self, auth_client):
        """测试令牌缓存功能"""
        # 测试缓存清理
        auth_client._token_cache["test_key"] = ("test_data", datetime.now())
        auth_client.clear_token_cache()
        assert len(auth_client._token_cache) == 0

        # 测试特定令牌缓存清理
        auth_client._token_cache["token:test_token_123456"] = ("test_data", datetime.now())
        auth_client.clear_token_cache("test_token_123456789")
        assert len(auth_client._token_cache) == 0

    def test_get_auth_client_singleton(self):
        """测试认证客户端单例模式"""
        client1 = get_auth_client()
        client2 = get_auth_client()
        
        assert client1 is client2