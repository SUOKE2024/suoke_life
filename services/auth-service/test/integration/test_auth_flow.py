#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务集成测试 - 认证流程
测试完整的认证流程，包括注册、登录、刷新令牌等
"""
import os
import uuid
import asyncio
import pytest
from httpx import AsyncClient
import grpc

# 导入要测试的模块
from cmd.server.main import app
from internal.model.errors import CredentialsError, UserExistsError
from api.grpc import auth_pb2, auth_pb2_grpc


# 测试配置
TEST_SERVER_HOST = os.getenv("TEST_SERVER_HOST", "localhost")
TEST_SERVER_HTTP_PORT = int(os.getenv("TEST_SERVER_HTTP_PORT", "8080"))
TEST_SERVER_GRPC_PORT = int(os.getenv("TEST_SERVER_GRPC_PORT", "50051"))
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_REDIS_HOST = os.getenv("TEST_REDIS_HOST", "localhost")


@pytest.fixture
def test_user_data():
    """生成测试用户数据"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "TestPassword123!",
        "phone_number": f"+8613800{unique_id}",
        "profile_data": {
            "display_name": "测试用户",
            "age": 30,
            "location": "北京"
        }
    }


@pytest.fixture
async def http_client():
    """创建HTTP客户端"""
    base_url = f"http://{TEST_SERVER_HOST}:{TEST_SERVER_HTTP_PORT}"
    async with AsyncClient(app=app, base_url=base_url) as client:
        yield client


@pytest.fixture
async def grpc_channel():
    """创建gRPC通道"""
    channel = grpc.aio.insecure_channel(f"{TEST_SERVER_HOST}:{TEST_SERVER_GRPC_PORT}")
    yield channel
    await channel.close()


@pytest.fixture
async def grpc_stub(grpc_channel):
    """创建gRPC存根"""
    return auth_pb2_grpc.AuthServiceStub(grpc_channel)


@pytest.mark.asyncio
async def test_http_user_registration(http_client, test_user_data):
    """测试HTTP用户注册"""
    # 发送注册请求
    response = await http_client.post("/api/v1/auth/register", json=test_user_data)
    
    # 验证响应
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user_id"] is not None
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    
    # 测试重复注册
    response = await http_client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "已被注册" in data["message"]


@pytest.mark.asyncio
async def test_http_user_login(http_client, test_user_data):
    """测试HTTP用户登录"""
    # 先注册用户
    await http_client.post("/api/v1/auth/register", json=test_user_data)
    
    # 登录测试
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    
    # 保存令牌用于后续测试
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    # 测试错误密码
    wrong_login_data = {
        "username": test_user_data["username"],
        "password": "WrongPassword123!"
    }
    response = await http_client.post("/api/v1/auth/login", json=wrong_login_data)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "密码错误" in data["message"]
    
    return access_token, refresh_token


@pytest.mark.asyncio
async def test_http_token_verification(http_client, test_user_data):
    """测试HTTP令牌验证"""
    # 获取有效令牌
    access_token, _ = await test_http_user_login(http_client, test_user_data)
    
    # 验证令牌
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await http_client.get("/api/v1/auth/verify", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["user_id"] is not None
    
    # 测试无效令牌
    invalid_token = "invalid.token.string"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    response = await http_client.get("/api/v1/auth/verify", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert data["valid"] is False


@pytest.mark.asyncio
async def test_http_token_refresh(http_client, test_user_data):
    """测试HTTP令牌刷新"""
    # 获取有效令牌
    _, refresh_token = await test_http_user_login(http_client, test_user_data)
    
    # 刷新令牌
    refresh_data = {"refresh_token": refresh_token}
    response = await http_client.post("/api/v1/auth/refresh", json=refresh_data)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    
    # 测试无效刷新令牌
    invalid_refresh = {"refresh_token": "invalid.refresh.token"}
    response = await http_client.post("/api/v1/auth/refresh", json=invalid_refresh)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_http_user_logout(http_client, test_user_data):
    """测试HTTP用户登出"""
    # 获取有效令牌
    access_token, refresh_token = await test_http_user_login(http_client, test_user_data)
    
    # 登出
    logout_data = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await http_client.post("/api/v1/auth/logout", json=logout_data, headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # 验证令牌已失效
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await http_client.get("/api/v1/auth/verify", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_grpc_user_registration(grpc_stub, test_user_data):
    """测试gRPC用户注册"""
    # 创建请求
    request = auth_pb2.RegisterRequest(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        phone_number=test_user_data["phone_number"],
        profile_data=test_user_data["profile_data"]
    )
    
    # 发送请求
    response = await grpc_stub.Register(request)
    
    # 验证响应
    assert response.success is True
    assert response.user_id is not None
    assert response.username == test_user_data["username"]
    assert response.email == test_user_data["email"]
    
    # 测试重复注册
    try:
        await grpc_stub.Register(request)
        assert False, "应该抛出异常"
    except grpc.RpcError as e:
        assert e.code() == grpc.StatusCode.INVALID_ARGUMENT
        assert "已被注册" in e.details()


@pytest.mark.asyncio
async def test_grpc_user_login(grpc_stub, test_user_data):
    """测试gRPC用户登录"""
    # 先注册用户
    register_request = auth_pb2.RegisterRequest(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        phone_number=test_user_data["phone_number"]
    )
    await grpc_stub.Register(register_request)
    
    # 登录测试
    login_request = auth_pb2.LoginRequest(
        username=test_user_data["username"],
        password=test_user_data["password"],
        auth_method=auth_pb2.PASSWORD
    )
    
    response = await grpc_stub.Login(login_request)
    
    # 验证响应
    assert response.success is True
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.token_type == "bearer"
    assert response.expires_in > 0
    
    # 保存令牌用于后续测试
    access_token = response.access_token
    refresh_token = response.refresh_token
    
    # 测试错误密码
    wrong_login_request = auth_pb2.LoginRequest(
        username=test_user_data["username"],
        password="WrongPassword123!",
        auth_method=auth_pb2.PASSWORD
    )
    
    try:
        await grpc_stub.Login(wrong_login_request)
        assert False, "应该抛出异常"
    except grpc.RpcError as e:
        assert e.code() == grpc.StatusCode.UNAUTHENTICATED
    
    return access_token, refresh_token


@pytest.mark.asyncio
async def test_grpc_token_verification(grpc_stub, test_user_data):
    """测试gRPC令牌验证"""
    # 获取有效令牌
    access_token, _ = await test_grpc_user_login(grpc_stub, test_user_data)
    
    # 验证令牌
    verify_request = auth_pb2.VerifyTokenRequest(token=access_token)
    response = await grpc_stub.VerifyToken(verify_request)
    
    # 验证响应
    assert response.valid is True
    assert response.user_id is not None
    
    # 测试无效令牌
    invalid_verify_request = auth_pb2.VerifyTokenRequest(token="invalid.token.string")
    try:
        await grpc_stub.VerifyToken(invalid_verify_request)
        assert False, "应该抛出异常"
    except grpc.RpcError as e:
        assert e.code() == grpc.StatusCode.INVALID_ARGUMENT 