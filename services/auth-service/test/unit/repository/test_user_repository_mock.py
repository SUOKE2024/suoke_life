import pytest
import pytest_asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta, UTC
import asyncio
import asyncpg

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
class TestUserRepositoryMock:
    """使用mock对象测试用户仓储"""

    async def setup_async(self):
        """异步设置，为每个测试方法准备必要对象"""
        # 创建mock连接
        self.conn = AsyncMock()
        
        # 创建mock数据库池
        self.pool = MockPool(self.conn)
        
        # 返回仓储实例
        return UserRepository(self.pool)

    def setup_method(self):
        """每个测试方法之前的设置"""
        # 创建mock用户数据
        self.user_id = str(uuid.uuid4())
        self.mock_profile = {
            "display_name": "测试用户",
            "bio": "这是一个测试账户",
            "avatar_url": None
        }
        
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self):
        """测试成功更新用户个人资料"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = self.mock_profile
        self.conn.execute.return_value = "UPDATE 1"
        
        # 执行测试
        update_data = {"display_name": "新名称"}
        result = await repo.update_user_profile(self.user_id, update_data)
        
        # 验证结果
        assert result is True
        self.conn.fetchval.assert_called_once()
        self.conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_profile_not_found(self):
        """测试更新不存在的用户个人资料"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = None  # 用户不存在
        
        # 执行测试
        update_data = {"display_name": "新名称"}
        with pytest.raises(UserNotFoundError):
            await repo.update_user_profile(self.user_id, update_data)

    @pytest.mark.asyncio
    async def test_update_user_profile_db_error(self):
        """测试更新用户个人资料时数据库错误"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = self.mock_profile
        self.conn.execute.side_effect = Exception("Database error")
        
        # 执行测试
        update_data = {"display_name": "新名称"}
        with pytest.raises(DatabaseError):
            await repo.update_user_profile(self.user_id, update_data)

    @pytest.mark.asyncio
    async def test_update_user_email_success(self):
        """测试成功更新用户邮箱"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = None  # 邮箱未被其他用户使用
        self.conn.execute.return_value = "UPDATE 1"
        
        # 执行测试
        new_email = "new_email@example.com"
        result = await repo.update_user_email(self.user_id, new_email)
        
        # 验证结果
        assert result is True
        self.conn.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_user_email_already_exists(self):
        """测试更新用户邮箱为已存在的邮箱"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = str(uuid.uuid4())  # 邮箱已被其他用户使用
        
        # 执行测试
        new_email = "existing@example.com"
        with pytest.raises(UserExistsError):
            await repo.update_user_email(self.user_id, new_email)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self):
        """测试通过邮箱成功获取用户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 准备测试数据
        email = "test@example.com"
        mock_user = {
            "id": self.user_id,
            "username": "test_user",
            "email": email,
            "phone_number": "13800138000",
            "profile_data": self.mock_profile
        }
        
        # 配置mock对象
        self.conn.fetchrow.return_value = mock_user
        
        # 执行测试
        result = await repo.get_user_by_email(email)
        
        # 验证结果
        assert result is not None
        assert result["email"] == email
        assert result["id"] == self.user_id
        self.conn.fetchrow.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """测试通过邮箱获取不存在的用户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchrow.return_value = None
        
        # 执行测试
        email = "nonexistent@example.com"
        with pytest.raises(UserNotFoundError):
            await repo.get_user_by_email(email)

    @pytest.mark.asyncio
    async def test_lock_user_account_success(self):
        """测试成功锁定用户账户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.execute.return_value = "UPDATE 1"
        
        # 执行测试
        lock_reason = "多次登录失败"
        lock_duration = 30  # 30分钟
        result = await repo.lock_user_account(self.user_id, lock_reason, lock_duration)
        
        # 验证结果
        assert result is True
        self.conn.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_unlock_user_account_success(self):
        """测试成功解锁用户账户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.execute.return_value = "UPDATE 1"
        
        # 执行测试
        result = await repo.unlock_user_account(self.user_id)
        
        # 验证结果
        assert result is True
        self.conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_role_to_user_success(self):
        """测试成功为用户分配角色"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象 - 模拟用户存在、角色存在，但用户尚未拥有该角色
        self.conn.fetchval.side_effect = [True, True, False]
        self.conn.execute.return_value = None
        
        # 执行测试
        role_id = str(uuid.uuid4())
        result = await repo.assign_role_to_user(self.user_id, role_id)
        
        # 验证结果
        assert result is True  # 方法在成功时返回True
        assert self.conn.fetchval.call_count == 3  # 验证fetchval被调用了三次
        assert self.conn.execute.called  # 验证execute被调用
        
    @pytest.mark.asyncio
    async def test_remove_role_from_user_success(self):
        """测试成功从用户移除角色"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = True  # 用户存在
        self.conn.execute.return_value = None
        
        # 执行测试
        role_id = str(uuid.uuid4())
        await repo.remove_role_from_user(self.user_id, role_id)
        
        # 验证结果
        self.conn.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_permissions_success(self):
        """测试成功获取用户权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 准备测试数据
        mock_permissions = [
            {"permission_id": str(uuid.uuid4()), "name": "read:users", "description": "可以读取用户信息"},
            {"permission_id": str(uuid.uuid4()), "name": "write:users", "description": "可以修改用户信息"}
        ]
        
        # 配置mock对象
        self.conn.fetchval.return_value = True  # 用户存在
        self.conn.fetch.return_value = mock_permissions
        
        # 执行测试
        result = await repo.get_user_permissions(self.user_id)
        
        # 验证结果
        assert len(result) == 2
        assert result[0]["name"] == "read:users"
        assert result[1]["name"] == "write:users"
        self.conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_user_has_permission_true(self):
        """测试用户有特定权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.side_effect = [True, True]  # 第一次查询用户是否存在，第二次查询权限
        
        # 执行测试
        permission_name = "read:users"
        result = await repo.check_user_has_permission(self.user_id, permission_name)
        
        # 验证结果
        assert result is True
        assert self.conn.fetchval.call_count == 2
        
    @pytest.mark.asyncio
    async def test_check_user_has_permission_false(self):
        """测试用户没有特定权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.side_effect = [True, False]  # 第一次查询用户是否存在，第二次查询权限
        
        # 执行测试
        permission_name = "admin:users"
        result = await repo.check_user_has_permission(self.user_id, permission_name)
        
        # 验证结果
        assert result is False
        assert self.conn.fetchval.call_count == 2

    @pytest.mark.asyncio
    async def test_get_user_by_phone_success(self):
        """测试通过手机号成功获取用户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 准备测试数据
        phone_number = "13800138000"
        mock_user = {
            "id": self.user_id,
            "username": "test_user",
            "email": "test@example.com",
            "phone_number": phone_number,
            "profile_data": self.mock_profile
        }
        
        # 配置mock对象
        self.conn.fetchrow.return_value = mock_user
        
        # 执行测试
        result = await repo.get_user_by_phone(phone_number)
        
        # 验证结果
        assert result is not None
        assert result["phone_number"] == phone_number
        assert result["id"] == self.user_id
        self.conn.fetchrow.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_user_by_phone_not_found(self):
        """测试通过手机号获取不存在的用户"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchrow.return_value = None
        
        # 执行测试
        phone_number = "13900139000"
        with pytest.raises(UserNotFoundError):
            await repo.get_user_by_phone(phone_number)

    @pytest.mark.asyncio
    async def test_update_login_timestamp_success(self):
        """测试成功更新用户登录时间戳"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.execute.return_value = "UPDATE 1"  # 模拟成功更新
        
        # 执行测试
        result = await repo.update_login_timestamp(self.user_id)
        
        # 验证结果
        assert result is True
        self.conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_login_timestamp_user_not_found(self):
        """测试更新不存在用户的登录时间戳"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.execute.return_value = "UPDATE 0"  # 模拟没有更新任何行
        
        # 执行测试
        with pytest.raises(UserNotFoundError):
            await repo.update_login_timestamp(self.user_id)

    @pytest.mark.asyncio
    async def test_update_login_timestamp_db_error(self):
        """测试更新用户登录时间戳时数据库错误"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.execute.side_effect = Exception("Database error")
        
        # 执行测试
        with pytest.raises(DatabaseError):
            await repo.update_login_timestamp(self.user_id)

    @pytest.mark.asyncio
    async def test_update_mfa_settings_success(self):
        """测试成功更新MFA设置"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchrow.return_value = {"id": self.user_id}  # 用户存在
        self.conn.execute.return_value = "UPDATE 1"
        
        # 执行测试
        result = await repo.update_mfa_settings(
            self.user_id, 
            mfa_enabled=True, 
            mfa_type="totp", 
            mfa_secret="ABCDEFGHIJKLMNOP", 
            mfa_backup_codes=["12345678", "87654321"]
        )
        
        # 验证结果
        assert result is True
        self.conn.fetchrow.assert_called_once()
        self.conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_mfa_settings_user_not_found(self):
        """测试更新不存在用户的MFA设置"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchrow.return_value = None  # 用户不存在
        
        # 执行测试
        with pytest.raises(UserNotFoundError):
            await repo.update_mfa_settings(
                self.user_id, 
                mfa_enabled=True, 
                mfa_type="totp"
            )

    @pytest.mark.asyncio
    async def test_update_mfa_settings_db_error(self):
        """测试更新用户MFA设置时数据库错误"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchrow.return_value = {"id": self.user_id}  # 用户存在
        self.conn.execute.side_effect = asyncpg.exceptions.PostgresError("ERROR", "42P01", "relation does not exist")
        
        # 执行测试
        with pytest.raises(DatabaseError):
            await repo.update_mfa_settings(
                self.user_id, 
                mfa_enabled=True, 
                mfa_type="totp"
            )

    @pytest.mark.asyncio
    async def test_check_permission_with_resource_has_permission(self):
        """测试用户对特定资源有权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象 - 3步：用户存在，有直接权限，有基于资源的权限
        self.conn.fetchval.side_effect = [True, True, True]
        
        # 执行测试
        permission_name = "edit:document"
        resource_id = str(uuid.uuid4())
        result = await repo.check_permission(self.user_id, permission_name, resource_id)
        
        # 验证结果
        assert result is True
        assert self.conn.fetchval.call_count == 3
        
    @pytest.mark.asyncio
    async def test_check_permission_no_resource_has_permission(self):
        """测试用户具有普通权限（无需资源ID）"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.side_effect = [True, True]
        
        # 执行测试
        permission_name = "view:dashboard"
        result = await repo.check_permission(self.user_id, permission_name)
        
        # 验证结果
        assert result is True
        assert self.conn.fetchval.call_count == 2
        
    @pytest.mark.asyncio
    async def test_check_permission_no_permission(self):
        """测试用户没有权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象 - 模拟用户存在，但无权限
        self.conn.fetchval.side_effect = [True, False]
        
        # 执行测试
        permission_name = "admin:system"
        resource_id = str(uuid.uuid4())
        result = await repo.check_permission(self.user_id, permission_name, resource_id)
        
        # 验证结果
        assert result is False
        assert self.conn.fetchval.call_count == 2
        
    @pytest.mark.asyncio
    async def test_check_permission_user_not_found(self):
        """测试检查不存在用户的权限"""
        # 初始化仓储
        repo = await self.setup_async()
        
        # 配置mock对象
        self.conn.fetchval.return_value = False  # 用户不存在
        
        # 执行测试
        permission_name = "view:dashboard"
        with pytest.raises(UserNotFoundError):
            await repo.check_permission(self.user_id, permission_name)
