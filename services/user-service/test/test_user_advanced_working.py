"""
User-Service 工作的高级功能测试
"""
import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
from uuid import uuid4

from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from internal.model.user import (
    CreateUserRequest, UpdateUserRequest, BindDeviceRequest,
    UpdateUserPreferencesRequest
)
from internal.repository.exceptions import (
    UserNotFoundError, UserAlreadyExistsError, DeviceAlreadyBoundError
)


class TestUserServiceAdvancedWorking:
    """User-Service 工作的高级功能测试"""
    
    @pytest_asyncio.fixture
    async def repository(self):
        """创建测试repository"""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        repo = SQLiteUserRepository(temp_db.name)
        await repo.initialize()
        
        yield repo
        
        # 清理
        try:
            os.unlink(temp_db.name)
        except:
            pass
    
    @pytest_asyncio.fixture
    async def user_service(self, repository):
        """创建用户服务实例"""
        return UserService(repository)
    
    @pytest.mark.asyncio
    async def test_duplicate_user_handling(self, user_service):
        """测试重复用户处理"""
        # 创建第一个用户
        user_data = {
            "username": "duplicatetest",
            "email": "duplicate@suoke.life",
            "password": "SecurePass123!",
            "phone": "+8613800138000"
        }
        
        request1 = CreateUserRequest(**user_data)
        result1 = await user_service.create_user(request1)
        assert result1.user_id is not None
        
        # 尝试创建相同用户名的用户
        user_data2 = {**user_data, "email": "different@suoke.life"}
        request2 = CreateUserRequest(**user_data2)
        
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(request2)
        
        print("✓ 重复用户检测正常工作")
    
    @pytest.mark.asyncio
    async def test_device_management(self, user_service):
        """测试设备管理功能"""
        # 1. 创建用户
        user_data = {
            "username": "deviceuser",
            "email": "device@suoke.life",
            "password": "SecurePass123!",
            "full_name": "设备测试用户"
        }
        
        request = CreateUserRequest(**user_data)
        user = await user_service.create_user(request)
        user_id = str(user.user_id)
        
        # 2. 绑定设备
        device_request = BindDeviceRequest(
            device_id="device-001",
            device_type="smartphone",
            device_name="iPhone 15 Pro"
        )
        
        bind_response = await user_service.bind_device(user_id, device_request)
        assert bind_response.success is True
        assert bind_response.device_id == "device-001"
        
        # 3. 获取用户设备列表
        devices_response = await user_service.get_user_devices(user_id)
        assert devices_response.total == 1
        assert len(devices_response.devices) == 1
        
        print("✓ 设备管理功能测试通过")
    
    @pytest.mark.asyncio
    async def test_user_preferences(self, user_service):
        """测试用户偏好设置"""
        # 1. 创建用户
        user_data = {
            "username": "prefuser",
            "email": "pref@suoke.life",
            "password": "SecurePass123!",
            "full_name": "偏好测试用户"
        }
        
        request = CreateUserRequest(**user_data)
        user = await user_service.create_user(request)
        user_id = str(user.user_id)
        
        # 2. 更新用户偏好设置
        preferences = {
            "language": "zh-CN",
            "timezone": "Asia/Shanghai",
            "notifications": {
                "email": True,
                "sms": False
            }
        }
        
        pref_request = UpdateUserPreferencesRequest(preferences=preferences)
        updated_user = await user_service.update_user_preferences(user_id, pref_request)
        
        # 3. 验证偏好设置
        assert updated_user.preferences["language"] == "zh-CN"
        assert updated_user.preferences["timezone"] == "Asia/Shanghai"
        
        print("✓ 用户偏好设置测试通过")
    
    @pytest.mark.asyncio
    async def test_health_summary_access(self, user_service):
        """测试健康摘要访问"""
        # 1. 创建用户
        user_data = {
            "username": "healthuser",
            "email": "health@suoke.life",
            "password": "SecurePass123!",
            "full_name": "健康测试用户"
        }
        
        request = CreateUserRequest(**user_data)
        user = await user_service.create_user(request)
        user_id = str(user.user_id)
        
        # 2. 获取健康摘要
        health_summary = await user_service.get_user_health_summary(user_id)
        assert health_summary.user_id == user_id
        assert health_summary.health_score is not None
        
        print("✓ 健康摘要访问测试通过")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, user_service):
        """测试错误处理"""
        # 测试不存在的用户ID
        fake_user_id = str(uuid4())
        
        with pytest.raises(UserNotFoundError):
            await user_service.get_user(fake_user_id)
        
        # 测试无效的用户ID格式
        invalid_user_id = "invalid-uuid"
        
        with pytest.raises(UserNotFoundError):
            await user_service.get_user(invalid_user_id)
        
        print("✓ 错误处理测试通过") 