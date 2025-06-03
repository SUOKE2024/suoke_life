"""
用户服务的单元测试
测试用户服务的核心功能
"""
import datetime
import os
import sys
import uuid
from typing import List, Optional, Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

import pytest

# 确保能够导入内部模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from internal.model.user import User, UserStatus, UserProfile, UserRole, ConstitutionType
from internal.model.user import UserCreate, UserUpdate, UserProfileUpdate
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from internal.repository.exceptions import UserNotFoundError, UserAlreadyExistsError

@pytest.fixture
def mock_user_repo():
    """创建模拟的用户存储库"""
    mock_repo = AsyncMock(spec=SQLiteUserRepository)
    
    # 模拟数据
    users = {}
    
    # 模拟用户ID生成器
    def generate_id():
        return str(uuid.uuid4())
    
    # 模拟查询方法
    async def get_user_by_id(user_id: str) -> Optional[User]:
        if user_id not in users:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        return users[user_id]
    
    async def get_user_by_email(email: str) -> Optional[User]:
        for user in users.values():
            if user.email == email:
                return user
        return None
    
    async def get_user_by_phone(phone: str) -> Optional[User]:
        for user in users.values():
            if user.phone == phone:
                return user
        return None
    
    async def create_user(user_data: UserCreate) -> User:
        # 检查是否已存在同样的邮箱或手机
        existing_email = await get_user_by_email(user_data.email)
        if existing_email:
            raise UserAlreadyExistsError(f"邮箱已被注册: {user_data.email}")
        
        if user_data.phone:
            existing_phone = await get_user_by_phone(user_data.phone)
            if existing_phone:
                raise UserAlreadyExistsError(f"手机号已被注册: {user_data.phone}")
        
        # 创建新用户
        user_id = generate_id()
        now = datetime.datetime.utcnow()
        
        user = User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            password_hash="fake_hashed_password",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            profile=UserProfile(
                user_id=user_id,
                display_name=user_data.username,
                avatar_url=None,
                gender=user_data.profile.gender if user_data.profile else None,
                birthday=user_data.profile.birthday if user_data.profile else None,
                constitution_type=ConstitutionType.BALANCED,
            ),
            created_at=now,
            updated_at=now,
            last_login=None,
        )
        
        users[user_id] = user
        return user
    
    async def update_user(user_id: str, user_data: UserUpdate) -> User:
        if user_id not in users:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        
        user = users[user_id]
        
        # 更新字段
        for field, value in user_data.dict(exclude_unset=True).items():
            if field != "profile" and hasattr(user, field):
                setattr(user, field, value)
        
        # 更新个人资料
        if user_data.profile:
            for field, value in user_data.profile.dict(exclude_unset=True).items():
                if hasattr(user.profile, field):
                    setattr(user.profile, field, value)
        
        user.updated_at = datetime.datetime.utcnow()
        users[user_id] = user
        
        return user
    
    async def delete_user(user_id: str) -> bool:
        if user_id not in users:
            raise UserNotFoundError(f"用户不存在: {user_id}")
        
        del users[user_id]
        return True
    
    async def list_users(
        limit: int = 100,
        offset: int = 0,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None
    ) -> List[User]:
        result = list(users.values())
        
        # 应用过滤
        if status:
            result = [u for u in result if u.status == status]
        
        if role:
            result = [u for u in result if role in u.roles]
        
        # 应用分页
        return result[offset:offset+limit]
    
    async def count_users(
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None
    ) -> int:
        result = list(users.values())
        
        # 应用过滤
        if status:
            result = [u for u in result if u.status == status]
        
        if role:
            result = [u for u in result if role in u.roles]
        
        return len(result)
    
    # 设置方法
    mock_repo.get_user_by_id = get_user_by_id
    mock_repo.get_user_by_email = get_user_by_email
    mock_repo.get_user_by_phone = get_user_by_phone
    mock_repo.create_user = create_user
    mock_repo.update_user = update_user
    mock_repo.delete_user = delete_user
    mock_repo.list_users = list_users
    mock_repo.count_users = count_users
    
    return mock_repo

@pytest.fixture
def user_service(mock_user_repo):
    """创建用户服务实例"""
    return UserService(mock_user_repo)

class TestUserService:
    """用户服务测试类"""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_service, mock_user_repo):
        """测试创建用户"""
        # 准备测试数据
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            phone="13800138000",
            password="Password123",
            profile=UserProfileUpdate(
                display_name="Test User",
                gender="male",
                birthday="1990-01-01"
            )
        )
        
        # 调用服务方法
        user = await user_service.create_user(user_data)
        
        # 验证结果
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.phone == "13800138000"
        assert user.status == UserStatus.ACTIVE
        assert UserRole.USER in user.roles
        
        # 验证个人资料
        assert user.profile is not None
        assert user.profile.display_name == "Test User"
        assert user.profile.gender == "male"
        assert str(user.profile.birthday) == "1990-01-01"
        
        # 验证存储库调用
        mock_user_repo.create_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_user_repo):
        """测试创建用户时邮箱重复"""
        # 准备测试数据
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123"
        )
        
        # 模拟已存在的用户
        mock_user_repo.get_user_by_email.return_value = User(
            id="existing-id",
            username="existing",
            email="test@example.com",
            password_hash="hashed",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id="existing-id",
                display_name="Existing User"
            )
        )
        
        # 验证抛出预期异常
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_service, mock_user_repo):
        """测试通过ID获取用户"""
        # 准备测试数据
        user_id = "test-id"
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟返回值
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 调用服务方法
        user = await user_service.get_user_by_id(user_id)
        
        # 验证结果
        assert user is not None
        assert user.id == user_id
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        
        # 验证存储库调用
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        """测试通过ID获取不存在的用户"""
        # 设置模拟行为
        user_id = "non-existent-id"
        mock_user_repo.get_user_by_id.side_effect = UserNotFoundError(f"用户不存在: {user_id}")
        
        # 验证抛出预期异常
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_id(user_id)
        
        # 验证存储库调用
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service, mock_user_repo):
        """测试更新用户"""
        # 准备测试数据
        user_id = "test-id"
        existing_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = existing_user
        mock_user_repo.update_user.return_value = User(
            id=user_id,
            username="updateduser",
            email="updated@example.com",
            password_hash="hashed",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=existing_user.created_at,
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Updated User"
            )
        )
        
        # 更新数据
        update_data = UserUpdate(
            username="updateduser",
            email="updated@example.com",
            profile=UserProfileUpdate(
                display_name="Updated User"
            )
        )
        
        # 调用服务方法
        updated_user = await user_service.update_user(user_id, update_data)
        
        # 验证结果
        assert updated_user is not None
        assert updated_user.id == user_id
        assert updated_user.username == "updateduser"
        assert updated_user.email == "updated@example.com"
        assert updated_user.profile.display_name == "Updated User"
        
        # 验证存储库调用
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
        mock_user_repo.update_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, mock_user_repo):
        """测试删除用户"""
        # 准备测试数据
        user_id = "test-id"
        
        # 设置模拟行为
        mock_user_repo.delete_user.return_value = True
        
        # 调用服务方法
        result = await user_service.delete_user(user_id)
        
        # 验证结果
        assert result is True
        
        # 验证存储库调用
        mock_user_repo.delete_user.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_list_users(self, user_service, mock_user_repo):
        """测试列出用户"""
        # 准备测试数据
        users = [
            User(
                id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash="hashed",
                status=UserStatus.ACTIVE,
                roles=[UserRole.USER],
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
                profile=UserProfile(
                    user_id=f"user-{i}",
                    display_name=f"User {i}"
                )
            )
            for i in range(5)
        ]
        
        # 设置模拟行为
        mock_user_repo.list_users.return_value = users
        mock_user_repo.count_users.return_value = len(users)
        
        # 调用服务方法
        result, total = await user_service.list_users(limit=10, offset=0)
        
        # 验证结果
        assert len(result) == 5
        assert total == 5
        
        # 验证存储库调用
        mock_user_repo.list_users.assert_called_once()
        mock_user_repo.count_users.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password(self, user_service, mock_user_repo):
        """测试修改密码"""
        # 准备测试数据
        user_id = "test-id"
        old_password = "OldPassword123"
        new_password = "NewPassword456"
        
        # 创建模拟用户
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_old_password",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 模拟密码验证
        with patch('internal.service.user_service.verify_password', return_value=True):
            # 模拟密码哈希
            with patch('internal.service.user_service.hash_password', return_value="hashed_new_password"):
                # 调用服务方法
                result = await user_service.change_password(user_id, old_password, new_password)
                
                # 验证结果
                assert result is True
                
                # 验证方法调用
                mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
                mock_user_repo.update_user.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_change_password_incorrect_old_password(self, user_service, mock_user_repo):
        """测试修改密码时旧密码不正确"""
        # 准备测试数据
        user_id = "test-id"
        old_password = "WrongPassword"
        new_password = "NewPassword456"
        
        # 创建模拟用户
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_old_password",
            status=UserStatus.ACTIVE,
            roles=[UserRole.USER],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 模拟密码验证失败
        with patch('internal.service.user_service.verify_password', return_value=False):
            # 调用服务方法并验证异常
            with pytest.raises(ValueError, match="旧密码不正确"):
                await user_service.change_password(user_id, old_password, new_password)
            
            # 验证方法调用
            mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
            mock_user_repo.update_user.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_verify_email(self, user_service, mock_user_repo):
        """测试验证邮箱"""
        # 准备测试数据
        user_id = "test-id"
        verification_code = "123456"
        
        # 创建模拟用户
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            status=UserStatus.PENDING,
            roles=[UserRole.USER],
            email_verified=False,
            verification_code=verification_code,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 调用服务方法
        result = await user_service.verify_email(user_id, verification_code)
        
        # 验证结果
        assert result is True
        
        # 验证方法调用
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
        mock_user_repo.update_user.assert_called_once()
        
        # 验证更新参数
        update_args = mock_user_repo.update_user.call_args[0]
        assert update_args[0] == user_id
        assert update_args[1].email_verified is True
        assert update_args[1].status == UserStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_verify_email_invalid_code(self, user_service, mock_user_repo):
        """测试验证邮箱时验证码无效"""
        # 准备测试数据
        user_id = "test-id"
        verification_code = "123456"
        wrong_code = "654321"
        
        # 创建模拟用户
        mock_user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            status=UserStatus.PENDING,
            roles=[UserRole.USER],
            email_verified=False,
            verification_code=verification_code,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
            profile=UserProfile(
                user_id=user_id,
                display_name="Test User"
            )
        )
        
        # 设置模拟行为
        mock_user_repo.get_user_by_id.return_value = mock_user
        
        # 调用服务方法并验证异常
        with pytest.raises(ValueError, match="验证码无效"):
            await user_service.verify_email(user_id, wrong_code)
        
        # 验证方法调用
        mock_user_repo.get_user_by_id.assert_called_once_with(user_id)
        mock_user_repo.update_user.assert_not_called()

if __name__ == "__main__":
    pytest.main(["-v", "test_user_service.py"]) 