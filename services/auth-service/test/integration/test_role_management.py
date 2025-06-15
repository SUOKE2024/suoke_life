#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务集成测试 - 高级角色管理
测试角色管理的高级功能，包括动态权限、角色继承等
"""
import pytest
import uuid
from httpx import AsyncClient

from cmd.server.main import app
from test.conftest import admin_user_data, test_user_data


@pytest.mark.asyncio
async def test_role_hierarchy(http_client, admin_token):
    """测试角色层次结构和继承"""
    # 准备测试数据 - 创建角色层次结构
    parent_role = {
        "name": f"parent_role_{uuid.uuid4().hex[:8]}",
        "description": "父级角色",
        "permissions": ["user:read", "role:read"]
    }
    
    child_role = {
        "name": f"child_role_{uuid.uuid4().hex[:8]}",
        "description": "子级角色",
        "permissions": ["user:create"],
        "parent_roles": []  # 将在创建后填充
    }
    
    grandchild_role = {
        "name": f"grandchild_role_{uuid.uuid4().hex[:8]}",
        "description": "孙级角色",
        "permissions": ["user:update"],
        "parent_roles": []  # 将在创建后填充
    }
    
    # 创建父级角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.post("/api/v1/roles", json=parent_role, headers=headers)
    assert response.status_code == 201
    parent_data = response.json()
    parent_id = parent_data["id"]
    
    # 更新子级角色，设置父级
    child_role["parent_roles"] = [parent_id]
    response = await http_client.post("/api/v1/roles", json=child_role, headers=headers)
    assert response.status_code == 201
    child_data = response.json()
    child_id = child_data["id"]
    
    # 更新孙级角色，设置父级
    grandchild_role["parent_roles"] = [child_id]
    response = await http_client.post("/api/v1/roles", json=grandchild_role, headers=headers)
    assert response.status_code == 201
    grandchild_data = response.json()
    grandchild_id = grandchild_data["id"]
    
    # 创建一个测试用户
    unique_id = uuid.uuid4().hex[:8]
    test_user = {
        "username": f"role_test_user_{unique_id}",
        "email": f"role_test_{unique_id}@example.com",
        "password": "TestPassword123!",
        "profile_data": {"display_name": "角色测试用户"}
    }
    
    response = await http_client.post("/api/v1/auth/register", json=test_user)
    assert response.status_code == 201
    user_data = response.json()
    user_id = user_data["user_id"]
    
    # 为用户分配孙级角色
    role_assignment = {
        "role_ids": [grandchild_id]
    }
    response = await http_client.post(
        f"/api/v1/users/{user_id}/roles", 
        json=role_assignment, 
        headers=headers
    )
    assert response.status_code == 200
    
    # 获取用户的有效权限
    response = await http_client.get(
        f"/api/v1/users/{user_id}/effective-permissions",
        headers=headers
    )
    assert response.status_code == 200
    permissions_data = response.json()
    
    # 验证权限继承
    # 用户应该有孙级角色的权限，以及通过继承得到的子级和父级角色的权限
    assert "user:update" in permissions_data["permissions"]  # 孙级角色直接权限
    assert "user:create" in permissions_data["permissions"]  # 子级角色继承权限
    assert "user:read" in permissions_data["permissions"]  # 父级角色继承权限
    assert "role:read" in permissions_data["permissions"]  # 父级角色继承权限


@pytest.mark.asyncio
async def test_dynamic_permission_assignment(http_client, admin_token):
    """测试动态权限分配"""
    # 创建一个测试角色
    dynamic_role = {
        "name": f"dynamic_role_{uuid.uuid4().hex[:8]}",
        "description": "动态权限测试角色",
        "permissions": ["user:read"]
    }
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.post("/api/v1/roles", json=dynamic_role, headers=headers)
    assert response.status_code == 201
    role_data = response.json()
    role_id = role_data["id"]
    
    # 获取当前权限列表
    response = await http_client.get(f"/api/v1/roles/{role_id}/permissions", headers=headers)
    assert response.status_code == 200
    initial_permissions = response.json()["permissions"]
    assert len(initial_permissions) == 1
    assert "user:read" in [p["name"] for p in initial_permissions]
    
    # 添加新权限
    new_permissions = {
        "permissions": ["user:create", "user:update"]
    }
    response = await http_client.post(
        f"/api/v1/roles/{role_id}/permissions", 
        json=new_permissions, 
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证权限已添加
    response = await http_client.get(f"/api/v1/roles/{role_id}/permissions", headers=headers)
    assert response.status_code == 200
    updated_permissions = response.json()["permissions"]
    permission_names = [p["name"] for p in updated_permissions]
    assert len(updated_permissions) == 3
    assert "user:read" in permission_names
    assert "user:create" in permission_names
    assert "user:update" in permission_names
    
    # 移除权限
    remove_permissions = {
        "permissions": ["user:create"]
    }
    response = await http_client.delete(
        f"/api/v1/roles/{role_id}/permissions", 
        json=remove_permissions, 
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证权限已移除
    response = await http_client.get(f"/api/v1/roles/{role_id}/permissions", headers=headers)
    assert response.status_code == 200
    final_permissions = response.json()["permissions"]
    permission_names = [p["name"] for p in final_permissions]
    assert len(final_permissions) == 2
    assert "user:read" in permission_names
    assert "user:update" in permission_names
    assert "user:create" not in permission_names


@pytest.mark.asyncio
async def test_role_based_access_control(http_client, admin_token):
    """测试基于角色的访问控制"""
    # 创建权限受限和非受限资源
    restricted_resource = {
        "name": f"restricted_resource_{uuid.uuid4().hex[:8]}",
        "description": "需要特殊权限的资源",
        "data": {"content": "机密信息"}
    }
    
    public_resource = {
        "name": f"public_resource_{uuid.uuid4().hex[:8]}",
        "description": "公开资源",
        "data": {"content": "公开信息"}
    }
    
    # 创建两个测试角色
    admin_role = {
        "name": f"test_admin_{uuid.uuid4().hex[:8]}",
        "description": "管理员测试角色",
        "permissions": ["resource:read:all", "resource:write:all"]
    }
    
    user_role = {
        "name": f"test_user_{uuid.uuid4().hex[:8]}",
        "description": "用户测试角色",
        "permissions": ["resource:read:public"]
    }
    
    # 创建角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.post("/api/v1/roles", json=admin_role, headers=headers)
    assert response.status_code == 201
    admin_role_id = response.json()["id"]
    
    response = await http_client.post("/api/v1/roles", json=user_role, headers=headers)
    assert response.status_code == 201
    user_role_id = response.json()["id"]
    
    # 创建两个测试用户
    admin_test_user = {
        "username": f"admin_rbac_{uuid.uuid4().hex[:8]}",
        "email": f"admin_rbac_{uuid.uuid4().hex[:8]}@example.com",
        "password": "AdminPass123!",
        "profile_data": {"display_name": "RBAC管理员测试"}
    }
    
    normal_test_user = {
        "username": f"user_rbac_{uuid.uuid4().hex[:8]}",
        "email": f"user_rbac_{uuid.uuid4().hex[:8]}@example.com",
        "password": "UserPass123!",
        "profile_data": {"display_name": "RBAC普通用户测试"}
    }
    
    # 注册用户
    response = await http_client.post("/api/v1/auth/register", json=admin_test_user)
    assert response.status_code == 201
    admin_user_id = response.json()["user_id"]
    
    response = await http_client.post("/api/v1/auth/register", json=normal_test_user)
    assert response.status_code == 201
    normal_user_id = response.json()["user_id"]
    
    # 分配角色
    admin_assignment = {"role_ids": [admin_role_id]}
    response = await http_client.post(
        f"/api/v1/users/{admin_user_id}/roles", 
        json=admin_assignment, 
        headers=headers
    )
    assert response.status_code == 200
    
    user_assignment = {"role_ids": [user_role_id]}
    response = await http_client.post(
        f"/api/v1/users/{normal_user_id}/roles", 
        json=user_assignment, 
        headers=headers
    )
    assert response.status_code == 200
    
    # 创建资源
    response = await http_client.post(
        "/api/v1/resources", 
        json=restricted_resource, 
        headers=headers
    )
    assert response.status_code == 201
    restricted_id = response.json()["id"]
    
    response = await http_client.post(
        "/api/v1/resources", 
        json=public_resource, 
        headers=headers
    )
    assert response.status_code == 201
    public_id = response.json()["id"]
    
    # 设置资源访问控制
    access_control = {
        "resource_id": restricted_id,
        "is_public": False,
        "required_permissions": ["resource:read:all"]
    }
    response = await http_client.post(
        "/api/v1/resources/access-control", 
        json=access_control, 
        headers=headers
    )
    assert response.status_code == 200
    
    access_control = {
        "resource_id": public_id,
        "is_public": True,
        "required_permissions": ["resource:read:public"]
    }
    response = await http_client.post(
        "/api/v1/resources/access-control", 
        json=access_control, 
        headers=headers
    )
    assert response.status_code == 200
    
    # 用户登录获取令牌
    admin_login = {
        "username": admin_test_user["username"],
        "password": admin_test_user["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=admin_login)
    assert response.status_code == 200
    admin_test_token = response.json()["access_token"]
    
    user_login = {
        "username": normal_test_user["username"],
        "password": normal_test_user["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=user_login)
    assert response.status_code == 200
    user_test_token = response.json()["access_token"]
    
    # 测试访问控制
    # 管理员应该能访问所有资源
    admin_headers = {"Authorization": f"Bearer {admin_test_token}"}
    response = await http_client.get(f"/api/v1/resources/{restricted_id}", headers=admin_headers)
    assert response.status_code == 200
    
    response = await http_client.get(f"/api/v1/resources/{public_id}", headers=admin_headers)
    assert response.status_code == 200
    
    # 普通用户只能访问公开资源
    user_headers = {"Authorization": f"Bearer {user_test_token}"}
    response = await http_client.get(f"/api/v1/resources/{restricted_id}", headers=user_headers)
    assert response.status_code == 403  # 访问受限
    
    response = await http_client.get(f"/api/v1/resources/{public_id}", headers=user_headers)
    assert response.status_code == 200  # 可以访问


@pytest.mark.asyncio
async def test_permission_checking_with_context(http_client, admin_token):
    """测试带上下文的权限检查"""
    # 创建一个拥有所有者权限的角色
    owner_role = {
        "name": f"owner_role_{uuid.uuid4().hex[:8]}",
        "description": "资源所有者角色",
        "permissions": ["resource:own"]
    }
    
    # 创建角色
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await http_client.post("/api/v1/roles", json=owner_role, headers=headers)
    assert response.status_code == 201
    owner_role_id = response.json()["id"]
    
    # 创建两个测试用户
    user1 = {
        "username": f"owner_user_{uuid.uuid4().hex[:8]}",
        "email": f"owner_{uuid.uuid4().hex[:8]}@example.com",
        "password": "OwnerPass123!",
        "profile_data": {"display_name": "资源所有者"}
    }
    
    user2 = {
        "username": f"other_user_{uuid.uuid4().hex[:8]}",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "OtherPass123!",
        "profile_data": {"display_name": "其他用户"}
    }
    
    # 注册用户
    response = await http_client.post("/api/v1/auth/register", json=user1)
    assert response.status_code == 201
    user1_id = response.json()["user_id"]
    
    response = await http_client.post("/api/v1/auth/register", json=user2)
    assert response.status_code == 201
    user2_id = response.json()["user_id"]
    
    # 分配角色
    role_assignment = {"role_ids": [owner_role_id]}
    await http_client.post(
        f"/api/v1/users/{user1_id}/roles", 
        json=role_assignment, 
        headers=headers
    )
    await http_client.post(
        f"/api/v1/users/{user2_id}/roles", 
        json=role_assignment, 
        headers=headers
    )
    
    # 用户登录获取令牌
    user1_login = {
        "username": user1["username"],
        "password": user1["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=user1_login)
    user1_token = response.json()["access_token"]
    
    user2_login = {
        "username": user2["username"],
        "password": user2["password"]
    }
    response = await http_client.post("/api/v1/auth/login", json=user2_login)
    user2_token = response.json()["access_token"]
    
    # 用户1创建资源
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    resource = {
        "name": f"test_resource_{uuid.uuid4().hex[:8]}",
        "description": "测试资源",
        "data": {"content": "测试内容"}
    }
    
    response = await http_client.post("/api/v1/resources", json=resource, headers=user1_headers)
    assert response.status_code == 201
    resource_id = response.json()["id"]
    
    # 创建带上下文的权限检查
    # 检查用户1对资源的权限 - 应该有权限因为是所有者
    check_data = {
        "permission": "resource:update",
        "resource_id": resource_id,
        "context": {"owner_id": user1_id}
    }
    
    response = await http_client.post(
        "/api/v1/permissions/check-with-context", 
        json=check_data,
        headers=user1_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is True
    
    # 检查用户2对资源的权限 - 不应该有权限因为不是所有者
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    response = await http_client.post(
        "/api/v1/permissions/check-with-context", 
        json=check_data,
        headers=user2_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_permission"] is False
    
    # 测试直接访问资源
    # 用户1应该能修改自己的资源
    update_data = {
        "description": "已更新的描述"
    }
    response = await http_client.patch(
        f"/api/v1/resources/{resource_id}", 
        json=update_data,
        headers=user1_headers
    )
    assert response.status_code == 200
    
    # 用户2不应该能修改用户1的资源
    response = await http_client.patch(
        f"/api/v1/resources/{resource_id}", 
        json=update_data,
        headers=user2_headers
    )
    assert response.status_code == 403 