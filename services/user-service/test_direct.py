"""
直接测试用户服务功能
"""
import asyncio
import tempfile
import os
from uuid import UUID

from internal.repository.sqlite_user_repository import SQLiteUserRepository
from internal.service.user_service import UserService
from internal.model.user import CreateUserRequest, UpdateUserRequest, BindDeviceRequest

async def test_user_service():
    """测试用户服务的完整功能"""
    # 创建临时数据库文件
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # 初始化repository和service
        repository = SQLiteUserRepository(temp_db.name)
        await repository.initialize()
        user_service = UserService(repository)
        
        print("✓ 服务初始化成功")
        
        # 测试1: 创建用户
        create_request = CreateUserRequest(
            username="testuser",
            email="test@suoke.life",
            password="securepassword123",
            phone="13800138000",
            full_name="测试用户"
        )
        
        user_response = await user_service.create_user(create_request)
        user_id = user_response.user_id
        print(f"✓ 用户创建成功: {user_response.username} (ID: {user_id})")
        
        # 测试2: 获取用户
        get_response = await user_service.get_user(str(user_id))
        print(f"✓ 用户获取成功: {get_response.username}")
        
        # 测试3: 更新用户
        update_request = UpdateUserRequest(
            full_name="更新的测试用户",
            phone="13900139000"
        )
        
        update_response = await user_service.update_user(str(user_id), update_request)
        print(f"✓ 用户更新成功: {update_response.full_name}")
        
        # 测试4: 绑定设备
        bind_request = BindDeviceRequest(
            device_id="test-device-001",
            device_type="mobile",
            device_name="iPhone 13",
            device_metadata={"os": "iOS 16", "app_version": "1.0.0"}
        )
        
        bind_response = await user_service.bind_device(str(user_id), bind_request)
        print(f"✓ 设备绑定成功: {bind_response.binding_id}")
        
        # 测试5: 获取用户设备
        devices_response = await user_service.get_user_devices(str(user_id))
        print(f"✓ 获取设备列表成功: {len(devices_response.devices)} 个设备")
        
        # 测试6: 解绑设备
        unbind_success = await user_service.unbind_device(str(user_id), "test-device-001")
        print(f"✓ 设备解绑成功: {unbind_success}")
        
        # 测试7: 获取健康摘要
        health_response = await user_service.get_user_health_summary(str(user_id))
        print(f"✓ 获取健康摘要成功: 健康分数 {health_response.health_score}")
        
        # 测试8: 删除用户
        delete_success = await user_service.delete_user(str(user_id))
        print(f"✓ 用户删除成功: {delete_success}")
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_db.name)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_user_service()) 