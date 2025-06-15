#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务集成测试 - 角色和权限管理
测试角色和权限管理的完整流程
"""
import pytest
from httpx import AsyncClient

from cmd.server.main import app
from test.conftest import admin_user_data, test_user_data


@pytest.mark.asyncio
async def test_get_roles(http_client, admin_token):
    """测试获取角色列表"""
    # 使用管理员令牌获取角色列表
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.get("/api/v1/roles", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert len(data["roles"]) >= 3  # 应至少包含admin, user, guest三个角色
    
    # 验证角色结构
    for role in data["roles"]:
        assert "id" in role
        assert "name" in role
        assert "description" in role
        assert "permissions" in role


@pytest.mark.asyncio
async def test_get_permissions(http_client, admin_token):
    """测试获取权限列表"""
    # 使用管理员令牌获取权限列表
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.get("/api/v1/permissions", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert len(data["permissions"]) >= 10  # 应有至少10个基本权限
    
    # 验证权限结构
    for permission in data["permissions"]:
        assert "id" in permission
        assert "name" in permission
        assert "description" in permission


@pytest.mark.asyncio
async def test_get_user_roles(http_client, admin_token, normal_user_id):
    """测试获取用户角色"""
    # 使用管理员令牌获取普通用户的角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.get(f"/api/v1/users/{normal_user_id}/roles", headers=headers)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    
    assert "roles" in data
    assert len(data["roles"]) >= 1  # 普通用户应至少有一个角色
    
    # 检查是否包含"user"角色
    has_user_role = any(role["name"] == "user" for role in data["roles"])
    assert has_user_role is True


@pytest.mark.asyncio
async def test_assign_role_to_user(http_client, admin_token, normal_user_id):
    """测试为用户分配角色"""
    # 准备角色分配数据
    role_data = {
        "role_names": ["guest"]  # 添加guest角色
    }
    
    # 使用管理员令牌为普通用户分配角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.post(
        f"/api/v1/users/{normal_user_id}/roles",
        json=role_data,
        headers=headers
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # 验证角色已分配
    response = await http_client.get(f"/api/v1/users/{normal_user_id}/roles", headers=headers)
    data = response.json()
    
    # 检查是否同时包含"user"和"guest"角色
    role_names = [role["name"] for role in data["roles"]]
    assert "user" in role_names
    assert "guest" in role_names


@pytest.mark.asyncio
async def test_remove_role_from_user(http_client, admin_token, normal_user_id):
    """测试从用户移除角色"""
    # 准备角色移除数据
    role_data = {
        "role_name": "guest"  # 移除guest角色
    }
    
    # 使用管理员令牌从普通用户移除角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.delete(
        f"/api/v1/users/{normal_user_id}/roles",
        json=role_data,
        headers=headers
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # 验证角色已移除
    response = await http_client.get(f"/api/v1/users/{normal_user_id}/roles", headers=headers)
    data = response.json()
    
    # 检查是否只包含"user"角色
    role_names = [role["name"] for role in data["roles"]]
    assert "user" in role_names
    assert "guest" not in role_names


@pytest.mark.asyncio
async def test_check_user_permission(http_client, admin_token, normal_user_id, normal_token):
    """测试检查用户权限"""
    # 使用管理员令牌检查普通用户的权限
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 检查用户应有的权限
    response = await http_client.get(
        f"/api/v1/users/{normal_user_id}/permissions/user:read",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is True
    
    # 检查用户不应有的权限
    response = await http_client.get(
        f"/api/v1/users/{normal_user_id}/permissions/user:delete",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is False
    
    # 使用普通用户自己的令牌检查自己的权限
    headers = {"Authorization": f"Bearer {normal_token}"}
    response = await http_client.get(
        "/api/v1/auth/permissions/user:read",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is True


@pytest.mark.asyncio
async def test_permission_access_control(http_client, admin_token, normal_token):
    """测试基于权限的访问控制"""
    # 管理员可以访问权限管理接口
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.get("/api/v1/permissions", headers=admin_headers)
    assert response.status_code == 200
    
    # 普通用户不能访问权限管理接口
    user_headers = {"Authorization": f"Bearer {normal_token}"}
    response = await http_client.get("/api/v1/permissions", headers=user_headers)
    assert response.status_code == 403  # 应返回禁止访问
    
    # 普通用户不能创建新角色
    new_role = {
        "name": "test_role",
        "description": "Test role",
        "permissions": ["user:read"]
    }
    response = await http_client.post("/api/v1/roles", json=new_role, headers=user_headers)
    assert response.status_code == 403  # 应返回禁止访问
    
    # 管理员可以创建新角色
    response = await http_client.post("/api/v1/roles", json=new_role, headers=admin_headers)
    assert response.status_code == 201  # 应成功创建


# 测试夹具
@pytest.fixture
async def admin_token(http_client, admin_user_data):
    """获取管理员令牌"""
    # 注册管理员用户
    await http_client.post("/api/v1/auth/register", json=admin_user_data)
    
    # 登录获取令牌
    login_data = {
        "username": admin_user_data["username"],
        "password": admin_user_data["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    
    # 添加管理员角色
    user_id = data["user_id"]
    
    # 使用系统管理员权限为该用户分配admin角色
    # 注意：在实际系统中，需要一个初始的超级管理员账户或直接的数据库操作
    # 这里为了测试，我们假设系统允许这种操作
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    await http_client.post(
        f"/api/v1/users/{user_id}/roles",
        json={"role_names": ["admin"]},
        headers=headers
    )
    
    # 重新登录获取包含管理员权限的令牌
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    
    return data["access_token"]


@pytest.fixture
async def normal_user_id(http_client, test_user_data):
    """创建普通用户并返回其ID"""
    # 注册普通用户
    response = await http_client.post("/api/v1/auth/register", json=test_user_data)
    data = response.json()
    return data["user_id"]


@pytest.fixture
async def normal_token(http_client, test_user_data):
    """获取普通用户令牌"""
    # 注册普通用户
    await http_client.post("/api/v1/auth/register", json=test_user_data)
    
    # 登录获取令牌
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=login_data)
    data = response.json()
    
    return data["access_token"] 