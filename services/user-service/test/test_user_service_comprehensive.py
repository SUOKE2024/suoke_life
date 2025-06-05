"""
User Service 全面测试
建立完整的测试覆盖率体系，覆盖用户管理、健康数据、设备管理等功能
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.main import app
from user_service.models.user import User, UserProfile, UserStatus
from user_service.models.health import HealthData, HealthMetrics, TCMConstitution
from user_service.models.device import UserDevice, DeviceType, DeviceStatus
from user_service.internal.service.user_service import UserService
from user_service.internal.repository.user_repository import UserRepository


class TestUserService:
    """用户服务核心逻辑测试"""
    
    @pytest.fixture
    def user_service(self):
        """创建用户服务实例"""
        return UserService()
    
    @pytest.fixture
    def mock_user(self):
        """创建模拟用户"""
        return User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            phone="13800138000",
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def mock_user_profile(self):
        """创建模拟用户档案"""
        return UserProfile(
            user_id="test-user-id",
            nickname="测试用户",
            avatar_url="https://example.com/avatar.jpg",
            gender="male",
            birth_date=datetime(1990, 1, 1),
            height=175.0,
            weight=70.0,
            occupation="软件工程师",
            location="北京市",
            bio="这是一个测试用户"
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service):
        """测试创建用户成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "phone": "13900139000",
            "password": "password123"
        }
        
        # 模拟用户不存在
        mock_repo.get_by_username.return_value = None
        mock_repo.get_by_email.return_value = None
        mock_repo.get_by_phone.return_value = None
        
        # 模拟创建成功
        created_user = User(id="new-user-id", **user_data)
        mock_repo.create.return_value = created_user
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            result = await user_service.create_user(mock_db, user_data)
        
        assert result.id == "new-user-id"
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        mock_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, user_service, mock_user):
        """测试创建用户失败 - 用户名重复"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        user_data = {
            "username": "testuser",  # 已存在的用户名
            "email": "new@example.com",
            "phone": "13900139000",
            "password": "password123"
        }
        
        # 模拟用户名已存在
        mock_repo.get_by_username.return_value = mock_user
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            with pytest.raises(ValueError, match="用户名已存在"):
                await user_service.create_user(mock_db, user_data)
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_service, mock_user):
        """测试创建用户失败 - 邮箱重复"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        user_data = {
            "username": "newuser",
            "email": "test@example.com",  # 已存在的邮箱
            "phone": "13900139000",
            "password": "password123"
        }
        
        # 模拟邮箱已存在
        mock_repo.get_by_username.return_value = None
        mock_repo.get_by_email.return_value = mock_user
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            with pytest.raises(ValueError, match="邮箱已存在"):
                await user_service.create_user(mock_db, user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service, mock_user):
        """测试根据ID获取用户成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = mock_user
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            result = await user_service.get_user_by_id(mock_db, "test-user-id")
        
        assert result == mock_user
        mock_repo.get_by_id.assert_called_once_with("test-user-id")
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service):
        """测试根据ID获取用户失败 - 用户不存在"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            result = await user_service.get_user_by_id(mock_db, "nonexistent-id")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, user_service, mock_user):
        """测试更新用户档案成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        mock_profile_repo = AsyncMock()
        
        update_data = {
            "nickname": "新昵称",
            "bio": "更新的个人简介",
            "height": 180.0,
            "weight": 75.0
        }
        
        # 模拟用户存在
        mock_repo.get_by_id.return_value = mock_user
        
        # 模拟档案更新成功
        updated_profile = UserProfile(user_id="test-user-id", **update_data)
        mock_profile_repo.update_profile.return_value = updated_profile
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            with patch('user_service.internal.repository.profile_repository.ProfileRepository', return_value=mock_profile_repo):
                result = await user_service.update_user_profile(mock_db, "test-user-id", update_data)
        
        assert result.nickname == "新昵称"
        assert result.bio == "更新的个人简介"
        assert result.height == 180.0
        assert result.weight == 75.0
    
    @pytest.mark.asyncio
    async def test_deactivate_user_success(self, user_service, mock_user):
        """测试停用用户成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟用户存在且为活跃状态
        mock_user.status = UserStatus.ACTIVE
        mock_repo.get_by_id.return_value = mock_user
        
        # 模拟停用成功
        deactivated_user = mock_user
        deactivated_user.status = UserStatus.INACTIVE
        mock_repo.update_status.return_value = deactivated_user
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            result = await user_service.deactivate_user(mock_db, "test-user-id")
        
        assert result.status == UserStatus.INACTIVE
        mock_repo.update_status.assert_called_once_with("test-user-id", UserStatus.INACTIVE)
    
    @pytest.mark.asyncio
    async def test_search_users_by_keyword(self, user_service):
        """测试根据关键词搜索用户"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟搜索结果
        search_results = [
            User(id="user1", username="testuser1", email="test1@example.com"),
            User(id="user2", username="testuser2", email="test2@example.com")
        ]
        mock_repo.search_by_keyword.return_value = search_results
        
        with patch('user_service.internal.repository.user_repository.UserRepository', return_value=mock_repo):
            results = await user_service.search_users(mock_db, keyword="test", limit=10, offset=0)
        
        assert len(results) == 2
        assert results[0].username == "testuser1"
        assert results[1].username == "testuser2"
        mock_repo.search_by_keyword.assert_called_once_with("test", 10, 0)


class TestHealthDataService:
    """健康数据服务测试"""
    
    @pytest.fixture
    def health_service(self):
        from user_service.internal.service.health_service import HealthService
        return HealthService()
    
    @pytest.fixture
    def mock_health_data(self):
        """创建模拟健康数据"""
        return HealthData(
            id="health-data-id",
            user_id="test-user-id",
            data_type="blood_pressure",
            value={"systolic": 120, "diastolic": 80},
            unit="mmHg",
            measured_at=datetime.utcnow(),
            source="manual",
            device_id="device123"
        )
    
    @pytest.mark.asyncio
    async def test_record_health_data_success(self, health_service, mock_health_data):
        """测试记录健康数据成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        health_data = {
            "user_id": "test-user-id",
            "data_type": "blood_pressure",
            "value": {"systolic": 120, "diastolic": 80},
            "unit": "mmHg",
            "source": "manual"
        }
        
        mock_repo.create.return_value = mock_health_data
        
        with patch('user_service.internal.repository.health_repository.HealthRepository', return_value=mock_repo):
            result = await health_service.record_health_data(mock_db, health_data)
        
        assert result.data_type == "blood_pressure"
        assert result.value["systolic"] == 120
        assert result.value["diastolic"] == 80
        mock_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_health_data_by_type(self, health_service):
        """测试根据类型获取健康数据"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟查询结果
        health_records = [
            HealthData(id="1", user_id="test-user-id", data_type="blood_pressure", value={"systolic": 120, "diastolic": 80}),
            HealthData(id="2", user_id="test-user-id", data_type="blood_pressure", value={"systolic": 125, "diastolic": 82})
        ]
        mock_repo.get_by_user_and_type.return_value = health_records
        
        with patch('user_service.internal.repository.health_repository.HealthRepository', return_value=mock_repo):
            results = await health_service.get_health_data_by_type(
                mock_db, "test-user-id", "blood_pressure", limit=10
            )
        
        assert len(results) == 2
        assert all(record.data_type == "blood_pressure" for record in results)
    
    @pytest.mark.asyncio
    async def test_calculate_health_metrics(self, health_service):
        """测试计算健康指标"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟血压数据
        bp_data = [
            HealthData(id="1", value={"systolic": 120, "diastolic": 80}, measured_at=datetime.utcnow()),
            HealthData(id="2", value={"systolic": 125, "diastolic": 82}, measured_at=datetime.utcnow()),
            HealthData(id="3", value={"systolic": 118, "diastolic": 78}, measured_at=datetime.utcnow())
        ]
        mock_repo.get_by_user_and_type.return_value = bp_data
        
        with patch('user_service.internal.repository.health_repository.HealthRepository', return_value=mock_repo):
            metrics = await health_service.calculate_health_metrics(mock_db, "test-user-id", "blood_pressure")
        
        # 验证计算结果
        assert "average_systolic" in metrics
        assert "average_diastolic" in metrics
        assert "trend" in metrics
        assert metrics["average_systolic"] == 121.0  # (120+125+118)/3
        assert metrics["average_diastolic"] == 80.0   # (80+82+78)/3
    
    @pytest.mark.asyncio
    async def test_tcm_constitution_analysis(self, health_service):
        """测试中医体质分析"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟体质分析数据
        constitution_data = {
            "user_id": "test-user-id",
            "questionnaire_answers": {
                "q1": 3, "q2": 2, "q3": 4, "q4": 1, "q5": 3
            }
        }
        
        # 模拟分析结果
        analysis_result = TCMConstitution(
            user_id="test-user-id",
            constitution_type="平和质",
            score=85.5,
            characteristics=["体质平和", "精力充沛", "睡眠良好"],
            recommendations=["保持规律作息", "适量运动", "均衡饮食"],
            analyzed_at=datetime.utcnow()
        )
        
        mock_repo.analyze_constitution.return_value = analysis_result
        
        with patch('user_service.internal.repository.tcm_repository.TCMRepository', return_value=mock_repo):
            result = await health_service.analyze_tcm_constitution(mock_db, constitution_data)
        
        assert result.constitution_type == "平和质"
        assert result.score == 85.5
        assert len(result.characteristics) == 3
        assert len(result.recommendations) == 3


class TestDeviceManagement:
    """设备管理测试"""
    
    @pytest.fixture
    def device_service(self):
        from user_service.internal.service.device_service import DeviceService
        return DeviceService()
    
    @pytest.fixture
    def mock_device(self):
        """创建模拟设备"""
        return UserDevice(
            id="device-id",
            user_id="test-user-id",
            device_name="iPhone 15",
            device_type=DeviceType.MOBILE,
            device_id="device123",
            os_version="iOS 17.0",
            app_version="1.0.0",
            status=DeviceStatus.ACTIVE,
            last_active_at=datetime.utcnow(),
            registered_at=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_register_device_success(self, device_service):
        """测试注册设备成功"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        device_data = {
            "user_id": "test-user-id",
            "device_name": "iPhone 15",
            "device_type": "mobile",
            "device_id": "device123",
            "os_version": "iOS 17.0",
            "app_version": "1.0.0"
        }
        
        # 模拟设备不存在
        mock_repo.get_by_device_id.return_value = None
        
        # 模拟注册成功
        registered_device = UserDevice(id="new-device-id", **device_data)
        mock_repo.create.return_value = registered_device
        
        with patch('user_service.internal.repository.device_repository.DeviceRepository', return_value=mock_repo):
            result = await device_service.register_device(mock_db, device_data)
        
        assert result.device_name == "iPhone 15"
        assert result.device_type == DeviceType.MOBILE
        assert result.status == DeviceStatus.ACTIVE
        mock_repo.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_device_already_exists(self, device_service, mock_device):
        """测试注册已存在的设备"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        device_data = {
            "user_id": "test-user-id",
            "device_id": "device123"  # 已存在的设备ID
        }
        
        # 模拟设备已存在
        mock_repo.get_by_device_id.return_value = mock_device
        
        with patch('user_service.internal.repository.device_repository.DeviceRepository', return_value=mock_repo):
            with pytest.raises(ValueError, match="设备已注册"):
                await device_service.register_device(mock_db, device_data)
    
    @pytest.mark.asyncio
    async def test_get_user_devices(self, device_service):
        """测试获取用户设备列表"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟用户设备列表
        user_devices = [
            UserDevice(id="device1", device_name="iPhone 15", device_type=DeviceType.MOBILE),
            UserDevice(id="device2", device_name="Apple Watch", device_type=DeviceType.WEARABLE),
            UserDevice(id="device3", device_name="iPad Pro", device_type=DeviceType.TABLET)
        ]
        mock_repo.get_by_user_id.return_value = user_devices
        
        with patch('user_service.internal.repository.device_repository.DeviceRepository', return_value=mock_repo):
            results = await device_service.get_user_devices(mock_db, "test-user-id")
        
        assert len(results) == 3
        assert results[0].device_name == "iPhone 15"
        assert results[1].device_name == "Apple Watch"
        assert results[2].device_name == "iPad Pro"
    
    @pytest.mark.asyncio
    async def test_update_device_activity(self, device_service, mock_device):
        """测试更新设备活跃状态"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟设备存在
        mock_repo.get_by_device_id.return_value = mock_device
        
        # 模拟更新成功
        updated_device = mock_device
        updated_device.last_active_at = datetime.utcnow()
        mock_repo.update_last_active.return_value = updated_device
        
        with patch('user_service.internal.repository.device_repository.DeviceRepository', return_value=mock_repo):
            result = await device_service.update_device_activity(mock_db, "device123")
        
        assert result.last_active_at is not None
        mock_repo.update_last_active.assert_called_once_with("device123")
    
    @pytest.mark.asyncio
    async def test_deactivate_device(self, device_service, mock_device):
        """测试停用设备"""
        mock_db = AsyncMock()
        mock_repo = AsyncMock()
        
        # 模拟设备存在
        mock_repo.get_by_device_id.return_value = mock_device
        
        # 模拟停用成功
        deactivated_device = mock_device
        deactivated_device.status = DeviceStatus.INACTIVE
        mock_repo.update_status.return_value = deactivated_device
        
        with patch('user_service.internal.repository.device_repository.DeviceRepository', return_value=mock_repo):
            result = await device_service.deactivate_device(mock_db, "device123")
        
        assert result.status == DeviceStatus.INACTIVE
        mock_repo.update_status.assert_called_once_with("device123", DeviceStatus.INACTIVE)


class TestUserAPI:
    """用户API端点测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)
    
    def test_create_user_endpoint_success(self, client):
        """测试创建用户端点成功"""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "phone": "13900139000",
            "password": "password123"
        }
        
        with patch('user_service.api.endpoints.users.get_user_service') as mock_get_service:
            mock_service = Mock()
            created_user = User(id="new-user-id", **user_data)
            mock_service.create_user.return_value = created_user
            mock_get_service.return_value = mock_service
            
            with patch('user_service.api.endpoints.users.get_db'):
                response = client.post("/api/v1/users", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "new-user-id"
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
    
    def test_create_user_endpoint_validation_error(self, client):
        """测试创建用户端点验证错误"""
        # 缺少必填字段
        invalid_data = {
            "username": "newuser"
            # 缺少email, phone, password
        }
        
        response = client.post("/api/v1/users", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_user_endpoint_success(self, client):
        """测试获取用户端点成功"""
        mock_user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            phone="13800138000"
        )
        
        with patch('user_service.api.endpoints.users.get_user_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_user_by_id.return_value = mock_user
            mock_get_service.return_value = mock_service
            
            with patch('user_service.api.endpoints.users.get_db'):
                response = client.get("/api/v1/users/test-user-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-user-id"
        assert data["username"] == "testuser"
    
    def test_get_user_endpoint_not_found(self, client):
        """测试获取用户端点用户不存在"""
        with patch('user_service.api.endpoints.users.get_user_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_user_by_id.return_value = None
            mock_get_service.return_value = mock_service
            
            with patch('user_service.api.endpoints.users.get_db'):
                response = client.get("/api/v1/users/nonexistent-id")
        
        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]
    
    def test_update_user_profile_endpoint_success(self, client):
        """测试更新用户档案端点成功"""
        update_data = {
            "nickname": "新昵称",
            "bio": "更新的个人简介"
        }
        
        updated_profile = UserProfile(
            user_id="test-user-id",
            nickname="新昵称",
            bio="更新的个人简介"
        )
        
        with patch('user_service.api.endpoints.users.get_user_service') as mock_get_service:
            mock_service = Mock()
            mock_service.update_user_profile.return_value = updated_profile
            mock_get_service.return_value = mock_service
            
            with patch('user_service.api.endpoints.users.get_db'):
                response = client.put("/api/v1/users/test-user-id/profile", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nickname"] == "新昵称"
        assert data["bio"] == "更新的个人简介"
    
    def test_search_users_endpoint(self, client):
        """测试搜索用户端点"""
        search_results = [
            User(id="user1", username="testuser1", email="test1@example.com"),
            User(id="user2", username="testuser2", email="test2@example.com")
        ]
        
        with patch('user_service.api.endpoints.users.get_user_service') as mock_get_service:
            mock_service = Mock()
            mock_service.search_users.return_value = search_results
            mock_get_service.return_value = mock_service
            
            with patch('user_service.api.endpoints.users.get_db'):
                response = client.get("/api/v1/users/search?keyword=test&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["username"] == "testuser1"
        assert data[1]["username"] == "testuser2"


class TestDataValidation:
    """数据验证测试"""
    
    def test_user_data_validation(self):
        """测试用户数据验证"""
        from user_service.schemas.user import UserCreateRequest
        
        # 有效数据
        valid_data = {
            "username": "validuser",
            "email": "valid@example.com",
            "phone": "13800138000",
            "password": "ValidPass123!"
        }
        
        user_request = UserCreateRequest(**valid_data)
        assert user_request.username == "validuser"
        assert user_request.email == "valid@example.com"
        
        # 无效邮箱格式
        with pytest.raises(ValueError):
            UserCreateRequest(
                username="user",
                email="invalid-email",
                phone="13800138000",
                password="password"
            )
        
        # 无效手机号格式
        with pytest.raises(ValueError):
            UserCreateRequest(
                username="user",
                email="valid@example.com",
                phone="invalid-phone",
                password="password"
            )
    
    def test_health_data_validation(self):
        """测试健康数据验证"""
        from user_service.schemas.health import HealthDataRequest
        
        # 有效血压数据
        valid_bp_data = {
            "data_type": "blood_pressure",
            "value": {"systolic": 120, "diastolic": 80},
            "unit": "mmHg",
            "source": "manual"
        }
        
        health_request = HealthDataRequest(**valid_bp_data)
        assert health_request.data_type == "blood_pressure"
        assert health_request.value["systolic"] == 120
        
        # 无效数据类型
        with pytest.raises(ValueError):
            HealthDataRequest(
                data_type="invalid_type",
                value={"test": "value"},
                unit="unit",
                source="manual"
            )


class TestPerformanceAndConcurrency:
    """性能和并发测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self):
        """测试并发用户创建"""
        from user_service.internal.service.user_service import UserService
        
        user_service = UserService()
        mock_db = AsyncMock()
        
        # 创建多个并发任务
        tasks = []
        for i in range(10):
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "phone": f"1380013800{i}",
                "password": "password123"
            }
            
            with patch('user_service.internal.repository.user_repository.UserRepository') as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.get_by_username.return_value = None
                mock_repo.get_by_email.return_value = None
                mock_repo.get_by_phone.return_value = None
                mock_repo.create.return_value = User(id=f"user-{i}", **user_data)
                mock_repo_class.return_value = mock_repo
                
                task = user_service.create_user(mock_db, user_data)
                tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证结果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 10
    
    @pytest.mark.asyncio
    async def test_bulk_health_data_processing(self):
        """测试批量健康数据处理"""
        from user_service.internal.service.health_service import HealthService
        
        health_service = HealthService()
        mock_db = AsyncMock()
        
        # 创建大量健康数据
        health_data_list = []
        for i in range(100):
            health_data = {
                "user_id": "test-user-id",
                "data_type": "heart_rate",
                "value": {"bpm": 70 + i % 30},
                "unit": "bpm",
                "source": "device"
            }
            health_data_list.append(health_data)
        
        with patch('user_service.internal.repository.health_repository.HealthRepository') as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo.create_batch.return_value = len(health_data_list)
            mock_repo_class.return_value = mock_repo
            
            # 批量处理
            result = await health_service.batch_record_health_data(mock_db, health_data_list)
        
        assert result == 100
        mock_repo.create_batch.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=user_service", "--cov-report=html"]) 