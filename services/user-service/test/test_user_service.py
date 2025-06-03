"""
用户服务单元测试模块
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest

from internal.model.user import (DeviceInfo, User, UserHealthSummary, UserResponse,
                          UserRole, UserStatus, VerifyUserResponse)
from internal.repository.sqlite_user_repository import (DeviceAlreadyBoundError,
                                                 DeviceNotFoundError,
                                                 UserAlreadyExistsError,
                                                 UserNotFoundError)
from internal.service.user_service import UserService

class MockUserRepository:
    """用户仓库模拟实现"""
    
    def __init__(self):
        """初始化模拟仓库"""
        self.users: Dict[str, User] = {}
        self.health_summaries: Dict[str, UserHealthSummary] = {}
        self.devices: Dict[str, List[DeviceInfo]] = {}
        
    async def create_user(self, username: str, email: str, password_hash: str,
                   phone: Optional[str] = None, full_name: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None) -> User:
        """创建用户"""
        # 检查用户名和邮箱是否已存在
        for user in self.users.values():
            if user.username == username or user.email == email:
                raise UserAlreadyExistsError(f"用户名 '{username}' 或邮箱 '{email}' 已存在")
        
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        user = User(
            user_id=uuid.UUID(user_id),
            username=username,
            email=email,
            phone=phone,
            full_name=full_name,
            created_at=now,
            updated_at=now,
            status=UserStatus.ACTIVE,
            metadata=metadata or {},
            roles=[UserRole.USER],
            preferences={}
        )
        
        self.users[user_id] = user
        return user
    
    async def get_user_by_id(self, user_id) -> Optional[User]:
        """通过ID获取用户"""
        return self.users.get(str(user_id))
    
    async def update_user(self, user_id, **kwargs) -> User:
        """更新用户信息"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        # 检查用户名和邮箱是否已被其他用户使用
        username = kwargs.get('username')
        email = kwargs.get('email')
        
        if username and username != user.username:
            for u in self.users.values():
                if u.username == username and str(u.user_id) != str(user_id):
                    raise UserAlreadyExistsError(f"用户名 '{username}' 已存在")
        
        if email and email != user.email:
            for u in self.users.values():
                if u.email == email and str(u.user_id) != str(user_id):
                    raise UserAlreadyExistsError(f"邮箱 '{email}' 已存在")
        
        # 更新用户属性
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        return user
    
    async def delete_user(self, user_id) -> bool:
        """删除用户"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        del self.users[user_id_str]
        if user_id_str in self.health_summaries:
            del self.health_summaries[user_id_str]
        if user_id_str in self.devices:
            del self.devices[user_id_str]
        
        return True
    
    async def get_user_health_summary(self, user_id) -> Optional[UserHealthSummary]:
        """获取用户健康摘要"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        if user_id_str not in self.health_summaries:
            # 返回默认健康摘要
            return UserHealthSummary(
                user_id=user_id,
                health_score=60
            )
        
        return self.health_summaries[user_id_str]
    
    async def update_user_preferences(self, user_id, preferences: Dict[str, str]) -> User:
        """更新用户偏好设置"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        user.preferences = preferences
        user.updated_at = datetime.utcnow()
        return user
    
    async def bind_device(self, user_id, device_id: str, device_type: str,
                   device_name: Optional[str] = None,
                   device_metadata: Optional[Dict[str, str]] = None) -> str:
        """绑定设备"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        # 检查设备是否已绑定
        for devices in self.devices.values():
            for device in devices:
                if device.device_id == device_id:
                    raise DeviceAlreadyBoundError(f"设备ID '{device_id}' 已绑定")
        
        binding_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        device = DeviceInfo(
            device_id=device_id,
            device_type=device_type,
            device_name=device_name,
            binding_time=now,
            binding_id=binding_id,
            is_active=True,
            last_active_time=now,
            device_metadata=device_metadata or {}
        )
        
        if user_id_str not in self.devices:
            self.devices[user_id_str] = []
        
        self.devices[user_id_str].append(device)
        return binding_id
    
    async def unbind_device(self, user_id, device_id: str) -> bool:
        """解绑设备"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        if user_id_str not in self.devices:
            raise DeviceNotFoundError(f"设备ID '{device_id}' 未绑定到用户ID '{user_id}'")
        
        devices = self.devices[user_id_str]
        for i, device in enumerate(devices):
            if device.device_id == device_id:
                devices.pop(i)
                return True
        
        raise DeviceNotFoundError(f"设备ID '{device_id}' 未绑定到用户ID '{user_id}'")
    
    async def get_user_devices(self, user_id) -> List[DeviceInfo]:
        """获取用户设备列表"""
        user_id_str = str(user_id)
        if user_id_str not in self.users:
            raise UserNotFoundError(f"用户ID '{user_id}' 不存在")
        
        return self.devices.get(user_id_str, [])

@pytest.fixture
def mock_user_repository():
    """用户仓库模拟fixture"""
    return MockUserRepository()

@pytest.fixture
def user_service(mock_user_repository):
    """用户服务fixture"""
    return UserService(mock_user_repository)

@pytest.mark.asyncio
async def test_create_user(user_service, mock_user_repository):
    """测试创建用户"""
    # 构建请求
    from internal.model.user import CreateUserRequest
    from pydantic import SecretStr
    
    request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        phone="+1234567890",
        full_name="Test User",
        password=SecretStr("password123"),
        metadata={"country": "China"}
    )
    
    # 执行服务调用
    response = await user_service.create_user(request)
    
    # 验证结果
    assert response.username == "testuser"
    assert response.email == "test@example.com"
    assert response.phone == "+1234567890"
    assert response.full_name == "Test User"
    assert response.metadata == {"country": "China"}
    assert UserRole.USER in response.roles
    
    # 验证仓库调用
    users = list(mock_user_repository.users.values())
    assert len(users) == 1
    assert users[0].username == "testuser"

@pytest.mark.asyncio
async def test_create_user_already_exists(user_service, mock_user_repository):
    """测试创建已存在的用户"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest
    from pydantic import SecretStr
    
    request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    await user_service.create_user(request)
    
    # 尝试创建同名用户
    with pytest.raises(UserAlreadyExistsError):
        await user_service.create_user(request)

@pytest.mark.asyncio
async def test_get_user(user_service, mock_user_repository):
    """测试获取用户"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest
    from pydantic import SecretStr
    
    request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(request)
    
    # 获取用户
    user = await user_service.get_user(created_user.user_id)
    
    # 验证结果
    assert user.user_id == created_user.user_id
    assert user.username == "testuser"
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_get_user_not_found(user_service):
    """测试获取不存在的用户"""
    with pytest.raises(UserNotFoundError):
        await user_service.get_user(str(uuid.uuid4()))

@pytest.mark.asyncio
async def test_update_user(user_service, mock_user_repository):
    """测试更新用户"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest, UpdateUserRequest
    from pydantic import SecretStr
    
    create_request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(create_request)
    
    # 更新用户
    update_request = UpdateUserRequest(
        username="updateduser",
        email="updated@example.com",
        phone="+9876543210",
        full_name="Updated User",
        metadata={"country": "USA"}
    )
    
    updated_user = await user_service.update_user(created_user.user_id, update_request)
    
    # 验证结果
    assert updated_user.user_id == created_user.user_id
    assert updated_user.username == "updateduser"
    assert updated_user.email == "updated@example.com"
    assert updated_user.phone == "+9876543210"
    assert updated_user.full_name == "Updated User"
    assert updated_user.metadata == {"country": "USA"}

@pytest.mark.asyncio
async def test_update_user_not_found(user_service):
    """测试更新不存在的用户"""
    from internal.model.user import UpdateUserRequest
    
    update_request = UpdateUserRequest(
        username="updateduser"
    )
    
    with pytest.raises(UserNotFoundError):
        await user_service.update_user(str(uuid.uuid4()), update_request)

@pytest.mark.asyncio
async def test_delete_user(user_service, mock_user_repository):
    """测试删除用户"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest
    from pydantic import SecretStr
    
    request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(request)
    
    # 删除用户
    result = await user_service.delete_user(created_user.user_id)
    
    # 验证结果
    assert result is True
    assert len(mock_user_repository.users) == 0

@pytest.mark.asyncio
async def test_delete_user_not_found(user_service):
    """测试删除不存在的用户"""
    with pytest.raises(UserNotFoundError):
        await user_service.delete_user(str(uuid.uuid4()))

@pytest.mark.asyncio
async def test_update_user_preferences(user_service, mock_user_repository):
    """测试更新用户偏好设置"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest, UpdateUserPreferencesRequest
    from pydantic import SecretStr
    
    create_request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(create_request)
    
    # 更新偏好设置
    preferences_request = UpdateUserPreferencesRequest(
        preferences={"theme": "dark", "language": "zh-CN"}
    )
    
    updated_user = await user_service.update_user_preferences(
        created_user.user_id, preferences_request
    )
    
    # 验证结果
    assert updated_user.user_id == created_user.user_id
    assert updated_user.preferences == {"theme": "dark", "language": "zh-CN"}

@pytest.mark.asyncio
async def test_bind_device(user_service, mock_user_repository):
    """测试绑定设备"""
    # 先创建一个用户
    from internal.model.user import BindDeviceRequest, CreateUserRequest
    from pydantic import SecretStr
    
    create_request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(create_request)
    
    # 绑定设备
    device_request = BindDeviceRequest(
        device_id="device-123",
        device_type="smartphone",
        device_name="My Phone",
        device_metadata={"os": "Android", "model": "Pixel 6"}
    )
    
    result = await user_service.bind_device(created_user.user_id, device_request)
    
    # 验证结果
    assert result.success is True
    assert result.binding_id is not None
    
    # 验证设备已绑定
    devices = await user_service.get_user_devices(created_user.user_id)
    assert len(devices.devices) == 1
    assert devices.devices[0].device_id == "device-123"
    assert devices.devices[0].device_type == "smartphone"
    assert devices.devices[0].device_name == "My Phone"
    assert devices.devices[0].device_metadata == {"os": "Android", "model": "Pixel 6"}

@pytest.mark.asyncio
async def test_unbind_device(user_service, mock_user_repository):
    """测试解绑设备"""
    # 先创建用户和绑定设备
    from internal.model.user import BindDeviceRequest, CreateUserRequest
    from pydantic import SecretStr
    
    create_request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(create_request)
    
    device_request = BindDeviceRequest(
        device_id="device-123",
        device_type="smartphone"
    )
    
    await user_service.bind_device(created_user.user_id, device_request)
    
    # 解绑设备
    result = await user_service.unbind_device(created_user.user_id, "device-123")
    
    # 验证结果
    assert result is True
    
    # 验证设备已解绑
    devices = await user_service.get_user_devices(created_user.user_id)
    assert len(devices.devices) == 0

@pytest.mark.asyncio
async def test_get_user_health_summary(user_service, mock_user_repository):
    """测试获取用户健康摘要"""
    # 先创建一个用户
    from internal.model.user import CreateUserRequest
    from pydantic import SecretStr
    
    create_request = CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password=SecretStr("password123")
    )
    
    created_user = await user_service.create_user(create_request)
    
    # 获取健康摘要
    health_summary = await user_service.get_user_health_summary(created_user.user_id)
    
    # 验证结果
    assert health_summary.user_id == created_user.user_id
    assert health_summary.health_score == 60  # 默认值 