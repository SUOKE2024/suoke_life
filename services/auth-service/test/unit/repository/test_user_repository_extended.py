import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, UTC

from internal.repository.user_repository import UserRepository
from internal.model.user import User, Role, Permission
from internal.model.errors import UserNotFoundError, UserExistsError, DatabaseError


class AsyncContextManager:
    """手动实现异步上下文管理器类"""
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockPool:
    """模拟asyncpg.Pool的类"""
    def __init__(self, conn):
        self.conn = conn
        
    def acquire(self):
        """返回一个异步上下文管理器，而不是协程"""
        return AsyncContextManager(self.conn)


@pytest.mark.asyncio
class TestUserRepositoryExtended:
    """扩展用户仓储测试，用于提高测试覆盖率"""

    @pytest_asyncio.fixture
    async def user_repo(self):
        """创建用户仓储实例"""
        # 创建连接模拟对象
        conn = AsyncMock()
        
        # 创建数据库池模拟对象
        pool = MockPool(conn)
        
        # 创建仓储实例
        repo = UserRepository(pool)
        return repo, conn

    @pytest.fixture
    def mock_user(self):
        """模拟用户数据"""
        return {
            "id": str(uuid.uuid4()),
            "username": "test_user",
            "email": "test@example.com",
            "password": "hashed_password",
            "phone_number": "13800138000",
            "profile_data": {
                "display_name": "测试用户",
                "bio": "这是一个测试账户",
                "avatar_url": None
            },
            "status": "active",
            "is_active": True,
            "is_locked": False,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
            "last_login_at": datetime.now(UTC) - timedelta(days=1),
            "mfa_enabled": False,
            "mfa_type": "none",
            "mfa_secret": None
        }

    async def test_update_user_profile_success(self, user_repo, mock_user):
        """测试成功更新用户个人资料"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        conn.fetchval.return_value = mock_user["profile_data"]
        conn.execute.return_value = "UPDATE 1"

        update_data = {
            "display_name": "Test User",
            "bio": "User biography",
            "avatar_url": "https://example.com/avatar.jpg"
        }

        result = await repo.update_user_profile(user_id, update_data)
        assert result is True
        conn.execute.assert_called_once()

    async def test_update_user_profile_not_found(self, user_repo, mock_user):
        """测试更新不存在的用户个人资料"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        conn.fetchval.return_value = None  # 用户不存在
        
        update_data = {"display_name": "Test User"}

        with pytest.raises(UserNotFoundError):
            await repo.update_user_profile(user_id, update_data)

    async def test_update_user_profile_db_error(self, user_repo, mock_user):
        """测试更新用户个人资料时数据库错误"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        conn.fetchval.return_value = mock_user["profile_data"]
        conn.execute.side_effect = Exception("Database error")

        update_data = {"display_name": "Test User"}

        with pytest.raises(DatabaseError):
            await repo.update_user_profile(user_id, update_data)

    async def test_update_user_email_success(self, user_repo, mock_user):
        """测试成功更新用户邮箱"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        new_email = "new_email@example.com"
        conn.fetchval.return_value = None  # 邮箱未被其他用户使用
        conn.execute.return_value = "UPDATE 1"

        result = await repo.update_user_email(user_id, new_email)
        assert result is True

    async def test_update_user_email_already_exists(self, user_repo, mock_user):
        """测试更新用户邮箱为已存在的邮箱"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        new_email = "existing@example.com"
        conn.fetchval.return_value = str(uuid.uuid4())  # 邮箱已被其他用户使用

        with pytest.raises(UserExistsError):
            await repo.update_user_email(user_id, new_email)

    async def test_get_user_by_email(self, user_repo, mock_user):
        """测试通过邮箱获取用户"""
        repo, conn = user_repo
        email = mock_user["email"]
        conn.fetchrow.return_value = mock_user

        user = await repo.get_user_by_email(email)
        assert user is not None
        assert isinstance(user, dict)
        assert user["email"] == email

    async def test_get_user_by_email_not_found(self, user_repo):
        """测试通过邮箱获取不存在的用户"""
        repo, conn = user_repo
        email = "nonexistent@example.com"
        conn.fetchrow.return_value = None

        with pytest.raises(UserNotFoundError):
            await repo.get_user_by_email(email)

    async def test_lock_user_account(self, user_repo, mock_user):
        """测试锁定用户账户"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        lock_reason = "多次登录失败"
        lock_duration = 30  # 30分钟
        conn.execute.return_value = "UPDATE 1"

        result = await repo.lock_user_account(user_id, lock_reason, lock_duration)
        assert result is True
        conn.execute.assert_called_once()

    async def test_unlock_user_account(self, user_repo, mock_user):
        """测试解锁用户账户"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        conn.execute.return_value = "UPDATE 1"

        result = await repo.unlock_user_account(user_id)
        assert result is True
        conn.execute.assert_called_once()
        
    async def test_assign_role_to_user(self, user_repo, mock_user):
        """测试为用户分配角色"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        role_id = str(uuid.uuid4())
        # 必须修改为side_effect
        conn.fetchval.side_effect = [True, True, False]  # 用户存在、角色存在、用户尚未拥有该角色
        conn.execute.return_value = None

        result = await repo.assign_role_to_user(user_id, role_id)
        assert result is True
        assert conn.fetchval.call_count == 3
        conn.execute.assert_called_once()

    async def test_remove_role_from_user(self, user_repo, mock_user):
        """测试从用户移除角色"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        role_id = str(uuid.uuid4())
        conn.fetchval.return_value = True  # 用户存在
        conn.execute.return_value = None

        await repo.remove_role_from_user(user_id, role_id)
        conn.execute.assert_called_once()

    async def test_get_user_permissions(self, user_repo, mock_user):
        """测试获取用户权限"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        permissions = [
            {"permission_id": str(uuid.uuid4()), "name": "read:users", "description": "可以读取用户信息"},
            {"permission_id": str(uuid.uuid4()), "name": "write:users", "description": "可以修改用户信息"}
        ]
        conn.fetchval.return_value = True  # 用户存在
        conn.fetch.return_value = permissions

        result = await repo.get_user_permissions(user_id)
        assert len(result) == 2
        assert result[0]["name"] == "read:users"
        assert result[1]["name"] == "write:users"
        
    async def test_check_user_has_permission(self, user_repo, mock_user):
        """测试检查用户是否有特定权限"""
        repo, conn = user_repo
        user_id = mock_user["id"]
        permission_name = "read:users"
        conn.fetchval.side_effect = [True, True]  # 第一次查询用户是否存在，第二次查询权限

        result = await repo.check_user_has_permission(user_id, permission_name)
        assert result is True 