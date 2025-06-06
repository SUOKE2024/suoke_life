"""
test_user_advanced - 索克生活项目模块
"""

from datetime import datetime, timezone
from internal.model.user import (
from internal.repository.exceptions import (
from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from uuid import uuid4
import asyncio
import os
import pytest
import pytest_asyncio
import tempfile
import time

"""
User-Service 高级功能测试
"""

    CreateUserRequest, UpdateUserRequest, BindDeviceRequest,
    UpdateUserHealthRequest, ConstitutionType, BloodType, HealthCondition
)
    UserNotFoundError, UserAlreadyExistsError, DeviceAlreadyBoundError
)


class TestUserServiceAdvanced:
    """User-Service 高级功能测试"""
    
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
    
    @pytest.fixture
    def sample_users_data(self):
        """示例用户数据"""
        return [
            {
                "username": f"user{i}",
                "email": f"user{i}@suoke.life",
                "password": f"SecurePass{i}23!",
                "phone": f"+861380013800{i}",
                "full_name": f"测试用户{i}"
            }
            for i in range(1, 6)
        ]
    
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, user_service, sample_users_data):
        """测试并发用户创建"""
        async def create_user(user_data):
            request = CreateUserRequest(**user_data)
            try:
                result = await user_service.create_user(request)
                return {"success": True, "user_id": result.user_id, "username": user_data["username"]}
            except Exception as e:
                return {"success": False, "error": str(e), "username": user_data["username"]}
        
        # 并发创建用户
        tasks = [create_user(user_data) for user_data in sample_users_data]
        results = await asyncio.gather(*tasks)
        
        # 验证结果
        successful_creations = [r for r in results if r["success"]]
        failed_creations = [r for r in results if not r["success"]]
        
        assert len(successful_creations) == 5
        assert len(failed_creations) == 0
        
        # 验证所有用户ID都不同
        user_ids = [r["user_id"] for r in successful_creations]
        assert len(set(user_ids)) == len(user_ids)
        
        print(f"✓ 成功并发创建 {len(successful_creations)} 个用户")
    
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
        
        # 尝试创建相同邮箱的用户
        user_data3 = {**user_data, "username": "differentuser"}
        request3 = CreateUserRequest(**user_data3)
        
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(request3)
        
        print("✓ 重复用户检测正常工作")
    
    @pytest.mark.asyncio
    async def test_batch_user_operations(self, user_service, sample_users_data):
        """测试批量用户操作"""
        # 1. 批量创建用户
        created_users = []
        for user_data in sample_users_data:
            request = CreateUserRequest(**user_data)
            result = await user_service.create_user(request)
            created_users.append(result)
        
        assert len(created_users) == 5
        
        # 2. 批量更新用户
        update_tasks = []
        for user in created_users:
            update_request = UpdateUserRequest(
                full_name=f"更新的{user.username}",
                phone=f"+861380013899{user.username[-1]}"
            )
            update_tasks.append(user_service.update_user(str(user.user_id), update_request))
        
        updated_users = await asyncio.gather(*update_tasks)
        
        for updated_user in updated_users:
            assert "更新的" in updated_user.full_name
            assert updated_user.phone.startswith("+86138001389")
        
        # 3. 批量删除用户
        delete_tasks = []
        for user in created_users:
            delete_tasks.append(user_service.delete_user(str(user.user_id)))
        
        delete_results = await asyncio.gather(*delete_tasks)
        assert all(delete_results)
        
        # 4. 验证用户已被删除
        for user in created_users:
            with pytest.raises(UserNotFoundError):
                await user_service.get_user(str(user.user_id))
        
        print("✓ 批量操作测试通过")
    
    @pytest.mark.asyncio
    async def test_complex_health_data_management(self, user_service):
        """测试复杂健康数据管理"""
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
        
        # 2. 更新复杂健康信息
        health_conditions = [
            HealthCondition(
                condition_name="高血压",
                condition_type="chronic",
                diagnosed_at=datetime.now(timezone.utc),
                status="managed",
                severity="mild",
                notes="定期服药控制"
            ),
            HealthCondition(
                condition_name="糖尿病",
                condition_type="chronic",
                diagnosed_at=datetime.now(timezone.utc),
                status="active",
                severity="medium",
                notes="需要饮食控制"
            )
        ]
        
        constitution_scores = {
            ConstitutionType.BALANCED.value: 75.0,
            ConstitutionType.QI_DEFICIENCY.value: 60.0,
            ConstitutionType.YANG_DEFICIENCY.value: 45.0,
            ConstitutionType.YIN_DEFICIENCY.value: 55.0,
            ConstitutionType.PHLEGM_DAMPNESS.value: 40.0
        }
        
        health_request = UpdateUserHealthRequest(
            health_score=78,
            dominant_constitution=ConstitutionType.BALANCED,
            constitution_scores=constitution_scores,
            height=175.5,
            weight=70.2,
            blood_type=BloodType.A_POSITIVE,
            allergies=["花粉", "海鲜", "青霉素"],
            chronic_conditions=health_conditions,
            medications=["降压药", "二甲双胍", "维生素D"]
        )
        
        updated_user = await user_service.update_user_health(user_id, health_request)
        
        # 3. 验证健康数据
        health_summary = await user_service.get_user_health_summary(user_id)
        
        assert health_summary.health_score == 78
        assert health_summary.dominant_constitution == ConstitutionType.BALANCED
        assert len(health_summary.constitution_scores) == 5
        assert health_summary.constitution_scores[ConstitutionType.BALANCED.value] == 75.0
        
        print("✓ 复杂健康数据管理测试通过")
    
    @pytest.mark.asyncio
    async def test_device_management_edge_cases(self, user_service):
        """测试设备管理边界情况"""
        # 1. 创建用户
        user_data = {
            "username": "deviceuser",
            "email": "device@suoke.life",
            "password": "SecurePass123!"
        }
        
        request = CreateUserRequest(**user_data)
        user = await user_service.create_user(request)
        user_id = str(user.user_id)
        
        # 2. 绑定多个设备
        devices = []
        for i in range(5):
            device_request = BindDeviceRequest(
                device_id=f"device-{i:03d}",
                device_type="smartphone",
                device_name=f"测试设备 {i+1}",
                platform="android",
                os_version="13.0",
                app_version="1.0.0",
                push_token=f"push_token_{i}",
                device_metadata={
                    "manufacturer": "TestBrand",
                    "model": f"TestModel-{i}",
                    "screen_size": "6.1",
                    "battery_level": str(90 - i * 10)
                }
            )
            
            bind_response = await user_service.bind_device(user_id, device_request)
            assert bind_response.success
            devices.append(device_request.device_id)
        
        # 3. 验证设备列表
        devices_response = await user_service.get_user_devices(user_id)
        assert devices_response.total == 5
        assert len(devices_response.devices) == 5
        
        # 4. 尝试重复绑定设备
        duplicate_device = BindDeviceRequest(
            device_id="device-001",  # 重复的设备ID
            device_type="tablet",
            device_name="重复设备"
        )
        
        with pytest.raises(DeviceAlreadyBoundError):
            await user_service.bind_device(user_id, duplicate_device)
        
        # 5. 解绑部分设备
        for device_id in devices[:3]:
            result = await user_service.unbind_device(user_id, device_id)
            assert result is True
        
        # 6. 验证剩余设备
        remaining_devices = await user_service.get_user_devices(user_id)
        assert remaining_devices.total == 2
        
        print("✓ 设备管理边界情况测试通过")
    
    @pytest.mark.asyncio
    async def test_performance_with_large_dataset(self, user_service):
        """测试大数据集性能"""
        # 1. 创建大量用户（适度数量以避免测试时间过长）
        start_time = time.time()
        
        users_count = 50  # 在实际性能测试中可以增加到更大数量
        created_users = []
        
        for i in range(users_count):
            user_data = {
                "username": f"perfuser{i:04d}",
                "email": f"perf{i:04d}@suoke.life",
                "password": "SecurePass123!",
                "full_name": f"性能测试用户 {i}"
            }
            
            request = CreateUserRequest(**user_data)
            user = await user_service.create_user(request)
            created_users.append(user)
        
        creation_time = time.time() - start_time
        
        # 2. 测试批量查询性能
        query_start = time.time()
        
        query_tasks = []
        for user in created_users[:20]:  # 查询前20个用户
            query_tasks.append(user_service.get_user(str(user.user_id)))
        
        queried_users = await asyncio.gather(*query_tasks)
        query_time = time.time() - query_start
        
        # 3. 输出性能指标
        print(f"✓ 性能测试结果:")
        print(f"  - 创建 {users_count} 个用户耗时: {creation_time:.2f}秒")
        print(f"  - 平均创建时间: {creation_time/users_count*1000:.2f}毫秒/用户")
        print(f"  - 查询 20 个用户耗时: {query_time:.2f}秒")
        print(f"  - 平均查询时间: {query_time/20*1000:.2f}毫秒/用户")
        
        # 4. 性能断言（根据实际需求调整阈值）
        assert creation_time < users_count * 0.1  # 每个用户创建不超过100ms
        assert query_time < 2.0  # 20个查询不超过2秒
        
        print("✓ 性能测试通过") 