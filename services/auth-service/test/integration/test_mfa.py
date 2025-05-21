#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务集成测试 - 多因素认证
测试多因素认证的完整流程
"""
import re
import pytest
import pyotp
from httpx import AsyncClient

from cmd.server.main import app


@pytest.mark.asyncio
async def test_enable_mfa_totp(http_client, user_token, user_id):
    """测试启用TOTP多因素认证"""
    # 准备启用TOTP的请求
    mfa_data = {
        "mfa_type": "totp"
    }
    
    # 使用用户令牌启用MFA
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await http_client.post("/api/v1/auth/mfa/enable", json=mfa_data, headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "secret_key" in data
    assert "qr_code_url" in data
    
    # 验证密钥格式是否正确
    secret_key = data["secret_key"]
    assert re.match(r'^[A-Z2-7]+=*$', secret_key) is not None
    
    # 验证二维码链接格式
    assert data["qr_code_url"].startswith("data:image/png;base64,")
    
    return secret_key


@pytest.mark.asyncio
async def test_verify_mfa_totp(http_client, user_token, user_id):
    """测试验证TOTP多因素认证"""
    # 先启用TOTP
    secret_key = await test_enable_mfa_totp(http_client, user_token, user_id)
    
    # 生成TOTP验证码
    totp = pyotp.TOTP(secret_key)
    mfa_code = totp.now()
    
    # 准备验证请求
    verify_data = {
        "mfa_code": mfa_code
    }
    
    # 使用用户令牌验证MFA
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await http_client.post("/api/v1/auth/mfa/verify", json=verify_data, headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["verified"] is True


@pytest.mark.asyncio
async def test_enable_mfa_sms(http_client, user_token):
    """测试启用短信多因素认证"""
    # 准备启用SMS的请求
    mfa_data = {
        "mfa_type": "sms"
    }
    
    # 使用用户令牌启用MFA
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await http_client.post("/api/v1/auth/mfa/enable", json=mfa_data, headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    
    # 短信验证应该触发发送验证码
    assert "验证码已发送" in data["message"]


@pytest.mark.asyncio
async def test_mfa_login_flow(http_client, test_user_data, mfa_setup):
    """测试带MFA的完整登录流程"""
    username, password, secret_key = mfa_setup
    
    # 第一步：常规登录
    login_data = {
        "username": username,
        "password": password
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    
    # 验证响应，应该要求MFA验证
    assert response.status_code == 200
    data = response.json()
    assert data["mfa_required"] is True
    assert "mfa_token" in data
    
    mfa_token = data["mfa_token"]
    
    # 生成有效的TOTP码
    totp = pyotp.TOTP(secret_key)
    mfa_code = totp.now()
    
    # 第二步：提交MFA验证
    mfa_data = {
        "mfa_token": mfa_token,
        "mfa_code": mfa_code
    }
    response = await http_client.post("/api/v1/auth/mfa/verify", json=mfa_data)
    
    # 验证响应，应返回完整的访问令牌
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_disable_mfa(http_client, user_token, user_id):
    """测试禁用多因素认证"""
    # 先启用MFA
    await test_enable_mfa_totp(http_client, user_token, user_id)
    
    # 准备禁用MFA的请求
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await http_client.delete("/api/v1/auth/mfa", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # 验证MFA状态
    response = await http_client.get("/api/v1/auth/mfa/status", headers=headers)
    data = response.json()
    assert data["mfa_enabled"] is False


@pytest.mark.asyncio
async def test_invalid_mfa_code(http_client, user_token, user_id):
    """测试无效的MFA验证码"""
    # 先启用TOTP
    await test_enable_mfa_totp(http_client, user_token, user_id)
    
    # 使用错误的验证码
    verify_data = {
        "mfa_code": "000000"  # 假设这不是有效的验证码
    }
    
    # 使用用户令牌验证MFA
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await http_client.post("/api/v1/auth/mfa/verify", json=verify_data, headers=headers)
    
    # 验证响应
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "验证失败" in data["message"]


# 测试夹具
@pytest.fixture
async def user_token(http_client, test_user_data):
    """创建用户并获取令牌"""
    # 注册用户
    await http_client.post("/api/v1/auth/register", json=test_user_data)
    
    # 登录获取令牌
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    
    return data["access_token"]


@pytest.fixture
async def user_id(http_client, test_user_data):
    """获取用户ID"""
    # 注册用户
    response = await http_client.post("/api/v1/auth/register", json=test_user_data)
    data = response.json()
    
    return data["user_id"]


@pytest.fixture
async def mfa_setup(http_client, test_user_data):
    """设置带MFA的用户"""
    # 注册用户
    await http_client.post("/api/v1/auth/register", json=test_user_data)
    
    # 登录获取令牌
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    token = data["access_token"]
    
    # 启用TOTP
    mfa_data = {
        "mfa_type": "totp"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = await http_client.post("/api/v1/auth/mfa/enable", json=mfa_data, headers=headers)
    data = response.json()
    secret_key = data["secret_key"]
    
    return test_user_data["username"], test_user_data["password"], secret_key 