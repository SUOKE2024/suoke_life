#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据初始化脚本

创建默认角色、权限和管理员用户。
"""
import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from internal.db import get_async_engine, get_db_session
from internal.db.models import (
    UserModel, RoleModel, PermissionModel, 
    UserRoleModel, RolePermissionModel
)
from internal.security.password import PasswordManager
from internal.model.user import UserStatusEnum


async def create_default_permissions():
    """创建默认权限"""
    permissions = [
        # 用户管理权限
        ("user:create", "user", "create", "创建用户"),
        ("user:read", "user", "read", "查看用户"),
        ("user:update", "user", "update", "更新用户"),
        ("user:delete", "user", "delete", "删除用户"),
        ("user:list", "user", "list", "列出用户"),
        
        # 角色管理权限
        ("role:create", "role", "create", "创建角色"),
        ("role:read", "role", "read", "查看角色"),
        ("role:update", "role", "update", "更新角色"),
        ("role:delete", "role", "delete", "删除角色"),
        ("role:list", "role", "list", "列出角色"),
        ("role:assign", "role", "assign", "分配角色"),
        
        # 权限管理权限
        ("permission:create", "permission", "create", "创建权限"),
        ("permission:read", "permission", "read", "查看权限"),
        ("permission:update", "permission", "update", "更新权限"),
        ("permission:delete", "permission", "delete", "删除权限"),
        ("permission:list", "permission", "list", "列出权限"),
        ("permission:assign", "permission", "assign", "分配权限"),
        
        # 审计日志权限
        ("audit:read", "audit", "read", "查看审计日志"),
        ("audit:list", "audit", "list", "列出审计日志"),
        
        # 系统管理权限
        ("system:config", "system", "config", "系统配置"),
        ("system:monitor", "system", "monitor", "系统监控"),
        ("system:backup", "system", "backup", "系统备份"),
        
        # 个人资料权限
        ("profile:read", "profile", "read", "查看个人资料"),
        ("profile:update", "profile", "update", "更新个人资料"),
    ]
    
    permission_objects = []
    for name, resource, action, description in permissions:
        permission = PermissionModel(
            id=str(uuid.uuid4()),
            name=name,
            resource=resource,
            action=action,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        permission_objects.append(permission)
    
    return permission_objects


async def create_default_roles():
    """创建默认角色"""
    roles = [
        ("admin", "管理员", "系统管理员，拥有所有权限"),
        ("user", "普通用户", "普通用户，拥有基本权限"),
        ("moderator", "版主", "版主，拥有部分管理权限"),
        ("guest", "访客", "访客用户，只读权限"),
    ]
    
    role_objects = []
    for name, display_name, description in roles:
        role = RoleModel(
            id=str(uuid.uuid4()),
            name=name,
            display_name=display_name,
            description=description,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        role_objects.append(role)
    
    return role_objects


async def assign_permissions_to_roles(session, roles, permissions):
    """为角色分配权限"""
    # 创建权限映射
    permission_map = {p.name: p for p in permissions}
    role_map = {r.name: r for r in roles}
    
    # 管理员拥有所有权限
    admin_role = role_map["admin"]
    for permission in permissions:
        role_permission = RolePermissionModel(
            id=str(uuid.uuid4()),
            role_id=admin_role.id,
            permission_id=permission.id,
            assigned_at=datetime.utcnow()
        )
        session.add(role_permission)
    
    # 普通用户权限
    user_permissions = [
        "profile:read", "profile:update"
    ]
    user_role = role_map["user"]
    for perm_name in user_permissions:
        if perm_name in permission_map:
            role_permission = RolePermissionModel(
                id=str(uuid.uuid4()),
                role_id=user_role.id,
                permission_id=permission_map[perm_name].id,
                assigned_at=datetime.utcnow()
            )
            session.add(role_permission)
    
    # 版主权限
    moderator_permissions = [
        "user:read", "user:list", "user:update",
        "role:read", "role:list",
        "audit:read", "audit:list",
        "profile:read", "profile:update"
    ]
    moderator_role = role_map["moderator"]
    for perm_name in moderator_permissions:
        if perm_name in permission_map:
            role_permission = RolePermissionModel(
                id=str(uuid.uuid4()),
                role_id=moderator_role.id,
                permission_id=permission_map[perm_name].id,
                assigned_at=datetime.utcnow()
            )
            session.add(role_permission)
    
    # 访客权限
    guest_permissions = [
        "profile:read"
    ]
    guest_role = role_map["guest"]
    for perm_name in guest_permissions:
        if perm_name in permission_map:
            role_permission = RolePermissionModel(
                id=str(uuid.uuid4()),
                role_id=guest_role.id,
                permission_id=permission_map[perm_name].id,
                assigned_at=datetime.utcnow()
            )
            session.add(role_permission)


async def create_admin_user(session, admin_role):
    """创建管理员用户"""
    password_manager = PasswordManager()
    
    # 创建管理员用户
    admin_user = UserModel(
        id=str(uuid.uuid4()),
        username="admin",
        email="admin@suokelife.com",
        password_hash=password_manager.hash_password("Admin123!"),
        first_name="系统",
        last_name="管理员",
        status=UserStatusEnum.ACTIVE.value,
        is_active=True,
        is_verified=True,
        profile_data={
            "role": "系统管理员",
            "department": "技术部"
        },
        preferences={
            "language": "zh-CN",
            "timezone": "Asia/Shanghai"
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(admin_user)
    await session.flush()  # 获取用户ID
    
    # 分配管理员角色
    user_role = UserRoleModel(
        id=str(uuid.uuid4()),
        user_id=admin_user.id,
        role_id=admin_role.id,
        assigned_at=datetime.utcnow()
    )
    session.add(user_role)
    
    return admin_user


async def init_database():
    """初始化数据库数据"""
    print("开始初始化数据库数据...")
    
    # 获取数据库会话
    async for session in get_db_session():
        try:
            # 检查是否已经初始化
            existing_roles = await session.execute(
                "SELECT COUNT(*) FROM roles"
            )
            if existing_roles.scalar() > 0:
                print("数据库已经初始化，跳过...")
                return
            
            # 创建权限
            print("创建默认权限...")
            permissions = await create_default_permissions()
            for permission in permissions:
                session.add(permission)
            
            # 创建角色
            print("创建默认角色...")
            roles = await create_default_roles()
            for role in roles:
                session.add(role)
            
            await session.flush()  # 确保角色和权限已保存
            
            # 分配权限给角色
            print("分配权限给角色...")
            await assign_permissions_to_roles(session, roles, permissions)
            
            # 创建管理员用户
            print("创建管理员用户...")
            admin_role = next(r for r in roles if r.name == "admin")
            admin_user = await create_admin_user(session, admin_role)
            
            # 提交事务
            await session.commit()
            
            print("数据库初始化完成！")
            print(f"管理员用户: {admin_user.username}")
            print(f"管理员邮箱: {admin_user.email}")
            print("管理员密码: Admin123!")
            print(f"创建了 {len(permissions)} 个权限")
            print(f"创建了 {len(roles)} 个角色")
            
        except Exception as e:
            await session.rollback()
            print(f"初始化失败: {e}")
            raise
        finally:
            await session.close()


async def main():
    """主函数"""
    try:
        await init_database()
    except Exception as e:
        print(f"初始化过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 