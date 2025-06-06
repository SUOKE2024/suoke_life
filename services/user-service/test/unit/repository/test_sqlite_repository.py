"""
test_sqlite_repository - 索克生活项目模块
"""

from datetime import datetime
from internal.model.user import User, UserStatus, UserRole, DeviceInfo, UserHealthSummary, ConstitutionType
from internal.repository.sqlite_user_repository import SQLiteUserRepository, UserNotFoundError, DeviceAlreadyBoundError
from pathlib import Path
import pytest
import sys
import uuid

"""
SQLite用户仓库单元测试
"""

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


# 测试数据
TEST_USER_DATA = {
    "username": "test_user",
    "email": "test@suoke.life",
    "phone": "13800138000",
    "full_name": "测试用户",
    "status": UserStatus.ACTIVE,
    "roles": [UserRole.USER]
}

TEST_DEVICE_DATA = {
    "device_id": "test-device-001",
    "device_type": "mobile",
    "device_name": "iPhone 13",
    "device_metadata": {"os": "iOS 16", "app_version": "1.0.0"}
}

@pytest.fixture
async def repository():
    """创建测试仓库"""
    # 使用内存数据库进行测试
    repo = SQLiteUserRepository(":memory:")
    await repo.initialize()
    return repo

@pytest.mark.asyncio
async def test_create_user(repository):
    """测试创建用户"""
    # 创建用户
    user = await repository.create_user(
        username=TEST_USER_DATA["username"],
        email=TEST_USER_DATA["email"],
        password_hash="hashed_password",
        phone=TEST_USER_DATA["phone"],
        full_name=TEST_USER_DATA["full_name"]
    )
    
    # 验证用户数据
    assert user.username == TEST_USER_DATA["username"]
    assert user.email == TEST_USER_DATA["email"]
    assert user.phone == TEST_USER_DATA["phone"]
    assert user.full_name == TEST_USER_DATA["full_name"]
    assert user.status == UserStatus.ACTIVE
    assert UserRole.USER in user.roles
    assert isinstance(user.user_id, uuid.UUID)
    
    return user

@pytest.mark.asyncio
async def test_get_user_by_id(repository):
    """测试通过ID获取用户"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 通过ID获取用户
    user = await repository.get_user_by_id(created_user.user_id)
    
    # 验证用户数据
    assert user.username == TEST_USER_DATA["username"]
    assert user.email == TEST_USER_DATA["email"]
    assert user.user_id == created_user.user_id

@pytest.mark.asyncio
async def test_get_user_by_username(repository):
    """测试通过用户名获取用户"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 通过用户名获取用户
    user = await repository.get_user_by_username(TEST_USER_DATA["username"])
    
    # 验证用户数据
    assert user.username == TEST_USER_DATA["username"]
    assert user.email == TEST_USER_DATA["email"]
    assert user.user_id == created_user.user_id

@pytest.mark.asyncio
async def test_update_user(repository):
    """测试更新用户信息"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 更新数据
    update_data = {
        "full_name": "更新的测试用户",
        "phone": "13900139000",
        "status": UserStatus.INACTIVE
    }
    
    # 更新用户
    updated_user = await repository.update_user(
        created_user.user_id,
        full_name=update_data["full_name"],
        phone=update_data["phone"],
        status=update_data["status"]
    )
    
    # 验证更新后的数据
    assert updated_user.full_name == update_data["full_name"]
    assert updated_user.phone == update_data["phone"]
    assert updated_user.status == update_data["status"]
    assert updated_user.user_id == created_user.user_id
    assert updated_user.username == created_user.username

@pytest.mark.asyncio
async def test_delete_user(repository):
    """测试删除用户"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 删除用户
    result = await repository.delete_user(created_user.user_id)
    assert result == True
    
    # 验证用户已删除
    with pytest.raises(UserNotFoundError):
        await repository.get_user_by_id(created_user.user_id)

@pytest.mark.asyncio
async def test_bind_user_device(repository):
    """测试绑定用户设备"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 绑定设备
    device_info = await repository.bind_user_device(
        user_id=created_user.user_id,
        device_id=TEST_DEVICE_DATA["device_id"],
        device_type=TEST_DEVICE_DATA["device_type"],
        device_name=TEST_DEVICE_DATA["device_name"],
        device_metadata=TEST_DEVICE_DATA["device_metadata"]
    )
    
    # 验证设备数据
    assert device_info.device_id == TEST_DEVICE_DATA["device_id"]
    assert device_info.device_type == TEST_DEVICE_DATA["device_type"]
    assert device_info.device_name == TEST_DEVICE_DATA["device_name"]
    assert device_info.is_active == True
    
    # 测试重复绑定同一设备
    with pytest.raises(DeviceAlreadyBoundError):
        await repository.bind_user_device(
            user_id=created_user.user_id,
            device_id=TEST_DEVICE_DATA["device_id"],
            device_type=TEST_DEVICE_DATA["device_type"],
            device_name=TEST_DEVICE_DATA["device_name"]
        )

@pytest.mark.asyncio
async def test_get_user_devices(repository):
    """测试获取用户设备列表"""
    # 先创建用户并绑定设备
    created_user = await test_create_user(repository)
    await repository.bind_user_device(
        user_id=created_user.user_id,
        device_id=TEST_DEVICE_DATA["device_id"],
        device_type=TEST_DEVICE_DATA["device_type"],
        device_name=TEST_DEVICE_DATA["device_name"],
        device_metadata=TEST_DEVICE_DATA["device_metadata"]
    )
    
    # 获取设备列表
    devices = await repository.get_user_devices(created_user.user_id)
    
    # 验证设备列表
    assert len(devices) == 1
    assert devices[0].device_id == TEST_DEVICE_DATA["device_id"]
    assert devices[0].device_type == TEST_DEVICE_DATA["device_type"]
    assert devices[0].device_name == TEST_DEVICE_DATA["device_name"]

@pytest.mark.asyncio
async def test_unbind_user_device(repository):
    """测试解绑用户设备"""
    # 先创建用户并绑定设备
    created_user = await test_create_user(repository)
    await repository.bind_user_device(
        user_id=created_user.user_id,
        device_id=TEST_DEVICE_DATA["device_id"],
        device_type=TEST_DEVICE_DATA["device_type"],
        device_name=TEST_DEVICE_DATA["device_name"]
    )
    
    # 解绑设备
    result = await repository.unbind_user_device(
        user_id=created_user.user_id,
        device_id=TEST_DEVICE_DATA["device_id"]
    )
    assert result == True
    
    # 验证设备已解绑
    devices = await repository.get_user_devices(created_user.user_id)
    assert len(devices) == 0

@pytest.mark.asyncio
async def test_update_user_health_summary(repository):
    """测试更新用户健康摘要"""
    # 先创建用户
    created_user = await test_create_user(repository)
    
    # 健康摘要数据
    health_summary = UserHealthSummary(
        user_id=created_user.user_id,
        health_score=85,
        dominant_constitution=ConstitutionType.BALANCED,
        constitution_scores={
            "balanced": 85.0,
            "qi_deficiency": 20.0,
            "yang_deficiency": 15.0
        },
        last_assessment_date=datetime.now()
    )
    
    # 更新健康摘要
    result = await repository.update_user_health_summary(health_summary)
    assert result == True
    
    # 获取健康摘要
    updated_summary = await repository.get_user_health_summary(created_user.user_id)
    
    # 验证健康摘要数据
    assert updated_summary.health_score == health_summary.health_score
    assert updated_summary.dominant_constitution == health_summary.dominant_constitution
    assert updated_summary.constitution_scores["balanced"] == health_summary.constitution_scores["balanced"]
    assert updated_summary.constitution_scores["qi_deficiency"] == health_summary.constitution_scores["qi_deficiency"]

if __name__ == "__main__":
    pytest.main(["-v", "test_sqlite_repository.py"]) 