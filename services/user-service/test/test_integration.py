"""
用户服务集成测试

该测试验证REST和gRPC接口的端到端功能
"""
import pytest
import uuid
import grpc
from httpx import AsyncClient
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from internal.model.user import UserStatus, UserRole
from cmd.server.main import app, init_repositories
from internal.service.user_service import UserService
from protobuf.suoke.user.v1 import user_pb2, user_pb2_grpc

# 测试数据
TEST_USER = {
    "username": "test_user",
    "email": "test@suoke.life",
    "password": "securepassword123",
    "phone": "13800138000",
    "full_name": "测试用户"
}

TEST_DEVICE = {
    "device_id": "test-device-001",
    "device_type": "mobile",
    "device_name": "iPhone 13",
    "device_metadata": {"os": "iOS 16", "app_version": "1.0.0"}
}

TEST_HEALTH_SUMMARY = {
    "health_score": 85,
    "dominant_constitution": "BALANCED",
    "constitution_scores": {
        "balanced": 85.0,
        "qi_deficiency": 20.0,
        "yang_deficiency": 15.0
    }
}

@pytest.fixture
async def client():
    """创建测试客户端"""
    # 使用内存数据库进行测试
    os.environ["USER_SERVICE_DB_PATH"] = ":memory:"
    
    # 初始化仓库
    repo = await init_repositories()
    app.state.user_repository = repo
    app.state.user_service = UserService(repo)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def grpc_channel():
    """创建gRPC通道"""
    # 使用内存中服务器进行测试
    server = grpc.aio.server()
    port = 50099
    server.add_insecure_port(f'[::]:{port}')
    
    # 初始化仓库和服务
    repo = await init_repositories()
    user_service = UserService(repo)
    
    # 添加服务到服务器
    from internal.delivery.grpc.user_server import UserServicer
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserServicer(user_service), server
    )
    
    # 启动服务器
    await server.start()
    
    # 创建通道
    channel = grpc.aio.insecure_channel(f'localhost:{port}')
    
    yield channel
    
    # 关闭服务器和通道
    await channel.close()
    await server.stop(0)

@pytest.mark.asyncio
async def test_rest_create_user(client):
    """测试通过REST API创建用户"""
    response = await client.post("/api/v1/users", json=TEST_USER)
    assert response.status_code == 201
    
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]
    assert "user_id" in data
    
    # 保存用户ID用于后续测试
    return data["user_id"]

@pytest.mark.asyncio
async def test_rest_get_user(client):
    """测试通过REST API获取用户信息"""
    # 先创建用户
    user_id = await test_rest_create_user(client)
    
    # 获取用户信息
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == TEST_USER["username"]
    assert data["email"] == TEST_USER["email"]
    assert data["user_id"] == user_id

@pytest.mark.asyncio
async def test_rest_update_user(client):
    """测试通过REST API更新用户信息"""
    # 先创建用户
    user_id = await test_rest_create_user(client)
    
    # 更新用户信息
    update_data = {
        "full_name": "更新的测试用户",
        "phone": "13900139000"
    }
    
    response = await client.put(f"/api/v1/users/{user_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]

@pytest.mark.asyncio
async def test_rest_bind_device(client):
    """测试通过REST API绑定设备"""
    # 先创建用户
    user_id = await test_rest_create_user(client)
    
    # 绑定设备
    response = await client.post(f"/api/v1/users/{user_id}/devices", json=TEST_DEVICE)
    assert response.status_code == 201
    
    data = response.json()
    assert data["success"] == True
    assert "binding_id" in data

@pytest.mark.asyncio
async def test_rest_get_user_devices(client):
    """测试通过REST API获取用户设备列表"""
    # 先创建用户并绑定设备
    user_id = await test_rest_create_user(client)
    await client.post(f"/api/v1/users/{user_id}/devices", json=TEST_DEVICE)
    
    # 获取设备列表
    response = await client.get(f"/api/v1/users/{user_id}/devices")
    assert response.status_code == 200
    
    data = response.json()
    assert "devices" in data
    assert len(data["devices"]) == 1
    assert data["devices"][0]["device_id"] == TEST_DEVICE["device_id"]

@pytest.mark.asyncio
async def test_rest_unbind_device(client):
    """测试通过REST API解绑设备"""
    # 先创建用户并绑定设备
    user_id = await test_rest_create_user(client)
    await client.post(f"/api/v1/users/{user_id}/devices", json=TEST_DEVICE)
    
    # 解绑设备
    response = await client.delete(f"/api/v1/users/{user_id}/devices/{TEST_DEVICE['device_id']}")
    assert response.status_code == 204
    
    # 验证设备已解绑
    response = await client.get(f"/api/v1/users/{user_id}/devices")
    data = response.json()
    assert len(data["devices"]) == 0

@pytest.mark.asyncio
async def test_rest_update_health_summary(client):
    """测试通过REST API更新用户健康摘要"""
    # 先创建用户
    user_id = await test_rest_create_user(client)
    
    # 更新健康摘要
    response = await client.put(f"/api/v1/users/{user_id}/health-summary", json=TEST_HEALTH_SUMMARY)
    assert response.status_code == 200
    
    data = response.json()
    assert data["health_summary"]["health_score"] == TEST_HEALTH_SUMMARY["health_score"]
    assert data["health_summary"]["dominant_constitution"] == TEST_HEALTH_SUMMARY["dominant_constitution"]

@pytest.mark.asyncio
async def test_grpc_create_user(grpc_channel):
    """测试通过gRPC创建用户"""
    # 创建gRPC客户端
    stub = user_pb2_grpc.UserServiceStub(grpc_channel)
    
    # 准备创建用户请求
    request = user_pb2.CreateUserRequest(
        username=TEST_USER["username"],
        email=TEST_USER["email"],
        phone_number=TEST_USER["phone"],
        full_name=TEST_USER["full_name"],
        password_hash="hashed_password"
    )
    
    # 发送请求
    response = await stub.CreateUser(request)
    
    # 验证响应
    assert response.username == TEST_USER["username"]
    assert response.email == TEST_USER["email"]
    assert response.user_id != ""
    
    return response.user_id

@pytest.mark.asyncio
async def test_grpc_get_user(grpc_channel):
    """测试通过gRPC获取用户信息"""
    # 创建gRPC客户端
    stub = user_pb2_grpc.UserServiceStub(grpc_channel)
    
    # 先创建用户
    user_id = await test_grpc_create_user(grpc_channel)
    
    # 准备获取用户请求
    request = user_pb2.GetUserRequest(user_id=user_id)
    
    # 发送请求
    response = await stub.GetUser(request)
    
    # 验证响应
    assert response.username == TEST_USER["username"]
    assert response.email == TEST_USER["email"]

@pytest.mark.asyncio
async def test_grpc_bind_device(grpc_channel):
    """测试通过gRPC绑定设备"""
    # 创建gRPC客户端
    stub = user_pb2_grpc.UserServiceStub(grpc_channel)
    
    # 先创建用户
    user_id = await test_grpc_create_user(grpc_channel)
    
    # 准备绑定设备请求
    request = user_pb2.BindDeviceRequest(
        user_id=user_id,
        device_id=TEST_DEVICE["device_id"],
        device_name=TEST_DEVICE["device_name"],
        device_type=TEST_DEVICE["device_type"],
        device_info=TEST_DEVICE["device_metadata"]
    )
    
    # 发送请求
    response = await stub.BindUserDevice(request)
    
    # 验证响应
    assert response.device_id == TEST_DEVICE["device_id"]
    assert response.device_name == TEST_DEVICE["device_name"]

if __name__ == "__main__":
    pytest.main(["-v", "test_integration.py"]) 