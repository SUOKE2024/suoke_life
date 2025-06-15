"""
认证服务测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from soer_service.services.auth_service import AuthService
from soer_service.models.auth import User, UserProfile


class TestAuthService:
    """认证服务测试类"""

    @pytest.mark.asyncio
    async def test_hash_password(self, auth_service):
        """测试密码哈希"""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrongpassword", hashed)

    @pytest.mark.asyncio
    async def test_create_access_token(self, auth_service):
        """测试访问令牌创建"""
        user_data = {
            "user_id": "test_user_id",
            "username": "testuser",
            "role": "user"
        }
        
        token = auth_service.create_access_token(user_data)
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, auth_service):
        """测试有效令牌验证"""
        user_data = {
            "user_id": "test_user_id",
            "username": "testuser",
            "role": "user"
        }
        
        token = auth_service.create_access_token(user_data)
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == "test_user_id"
        assert payload["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service):
        """测试无效令牌验证"""
        invalid_token = "invalid.token.here"
        payload = auth_service.verify_token(invalid_token)
        assert payload is None

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, sample_user_data):
        """测试用户注册成功"""
        # 模拟数据库查询返回None（用户不存在）
        auth_service.mongodb["users"].find_one = AsyncMock(return_value=None)
        auth_service.mongodb["users"].insert_one = AsyncMock()
        auth_service.mongodb["user_profiles"].insert_one = AsyncMock()

        result = await auth_service.register_user(sample_user_data)
        
        assert result["success"] is True
        assert "user_id" in result
        assert "access_token" in result

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, auth_service, sample_user_data):
        """测试重复用户名注册"""
        # 模拟数据库查询返回现有用户
        existing_user = {"username": sample_user_data["username"]}
        auth_service.mongodb["users"].find_one = AsyncMock(return_value=existing_user)

        result = await auth_service.register_user(sample_user_data)
        
        assert result["success"] is False
        assert "用户名已存在" in result["message"]

    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service, sample_user_data):
        """测试用户登录成功"""
        # 创建模拟用户数据
        hashed_password = auth_service.hash_password(sample_user_data["password"])
        mock_user = {
            "user_id": "test_user_id",
            "username": sample_user_data["username"],
            "email": sample_user_data["email"],
            "password_hash": hashed_password,
            "is_active": True,
            "role": "user"
        }
        
        auth_service.mongodb["users"].find_one = AsyncMock(return_value=mock_user)
        auth_service.mongodb["user_sessions"].insert_one = AsyncMock()

        result = await auth_service.login_user(
            sample_user_data["username"], 
            sample_user_data["password"]
        )
        
        assert result["success"] is True
        assert "access_token" in result
        assert result["user"]["username"] == sample_user_data["username"]

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, auth_service):
        """测试无效凭据登录"""
        # 模拟数据库查询返回None
        auth_service.mongodb["users"].find_one = AsyncMock(return_value=None)

        result = await auth_service.login_user("nonexistent", "wrongpassword")
        
        assert result["success"] is False
        assert "用户名或密码错误" in result["message"]

    @pytest.mark.asyncio
    async def test_login_user_inactive_account(self, auth_service, sample_user_data):
        """测试非活跃账户登录"""
        hashed_password = auth_service.hash_password(sample_user_data["password"])
        mock_user = {
            "user_id": "test_user_id",
            "username": sample_user_data["username"],
            "password_hash": hashed_password,
            "is_active": False,
            "role": "user"
        }
        
        auth_service.mongodb["users"].find_one = AsyncMock(return_value=mock_user)

        result = await auth_service.login_user(
            sample_user_data["username"], 
            sample_user_data["password"]
        )
        
        assert result["success"] is False
        assert "账户已被禁用" in result["message"]

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, auth_service):
        """测试令牌刷新成功"""
        user_data = {
            "user_id": "test_user_id",
            "username": "testuser",
            "role": "user"
        }
        
        # 创建有效的刷新令牌
        refresh_token = auth_service.create_refresh_token(user_data)
        
        # 模拟数据库查询
        mock_session = {
            "user_id": "test_user_id",
            "refresh_token": refresh_token,
            "expires_at": datetime.now() + timedelta(days=7),
            "is_active": True
        }
        auth_service.mongodb["user_sessions"].find_one = AsyncMock(return_value=mock_session)

        result = await auth_service.refresh_token(refresh_token)
        
        assert result["success"] is True
        assert "access_token" in result

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, auth_service):
        """测试无效刷新令牌"""
        # 模拟数据库查询返回None
        auth_service.mongodb["user_sessions"].find_one = AsyncMock(return_value=None)

        result = await auth_service.refresh_token("invalid_refresh_token")
        
        assert result["success"] is False
        assert "无效的刷新令牌" in result["message"]

    @pytest.mark.asyncio
    async def test_logout_user_success(self, auth_service):
        """测试用户登出成功"""
        user_id = "test_user_id"
        session_id = "test_session_id"
        
        auth_service.mongodb["user_sessions"].update_one = AsyncMock()

        result = await auth_service.logout_user(user_id, session_id)
        
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_check_permission_admin(self, auth_service):
        """测试管理员权限检查"""
        user_data = {"role": "admin"}
        
        assert auth_service.check_permission(user_data, "admin")
        assert auth_service.check_permission(user_data, "premium")
        assert auth_service.check_permission(user_data, "user")

    @pytest.mark.asyncio
    async def test_check_permission_user(self, auth_service):
        """测试普通用户权限检查"""
        user_data = {"role": "user"}
        
        assert not auth_service.check_permission(user_data, "admin")
        assert not auth_service.check_permission(user_data, "premium")
        assert auth_service.check_permission(user_data, "user")

    @pytest.mark.asyncio
    async def test_rate_limit_check(self, auth_service):
        """测试速率限制检查"""
        user_id = "test_user_id"
        action = "login"
        
        # 模拟Redis操作
        auth_service.redis.get = AsyncMock(return_value=None)
        auth_service.redis.set = AsyncMock()
        auth_service.redis.incr = AsyncMock(return_value=1)
        auth_service.redis.expire = AsyncMock()

        # 第一次检查应该通过
        is_allowed = await auth_service.check_rate_limit(user_id, action)
        assert is_allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, auth_service):
        """测试速率限制超出"""
        user_id = "test_user_id"
        action = "login"
        
        # 模拟已达到限制
        auth_service.redis.get = AsyncMock(return_value="6")  # 超过5次限制

        is_allowed = await auth_service.check_rate_limit(user_id, action)
        assert is_allowed is False

    @pytest.mark.asyncio
    async def test_health_check(self, auth_service):
        """测试健康检查"""
        result = await auth_service.health_check()
        
        assert result["service"] == "AuthService"
        assert "status" in result
        assert "mongodb_connected" in result
        assert "redis_connected" in result