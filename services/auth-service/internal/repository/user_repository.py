#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户仓储实现
处理用户数据的存储和检索
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import asyncpg
from sqlalchemy.ext.asyncio import AsyncEngine

from internal.model.errors import DatabaseError, UserExistsError, UserNotFoundError


class UserRepository:
    """用户仓储，管理用户相关数据的持久化"""

    def __init__(self, pool: asyncpg.Pool):
        """
        初始化用户仓储
        
        Args:
            pool: 数据库连接池
        """
        self.pool = pool
        self.logger = logging.getLogger(__name__)
    
    async def create_user(self, username: str, email: str, hashed_password: str, 
                          phone_number: Optional[str] = None, 
                          profile_data: Optional[Dict[str, Any]] = None) -> Tuple[str, str, str]:
        """
        创建新用户
        
        Args:
            username: 用户名
            email: 电子邮件
            hashed_password: 哈希后的密码
            phone_number: 手机号码，可选
            profile_data: 用户个人资料数据，可选
            
        Returns:
            Tuple[str, str, str]: 用户ID、用户名和电子邮件
            
        Raises:
            UserExistsError: 如果用户名或电子邮件已存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                # 检查用户名和电子邮件是否已存在
                existing = await conn.fetchrow(
                    "SELECT id FROM users WHERE username = $1 OR email = $2",
                    username, email
                )
                
                if existing:
                    # 确定是用户名还是电子邮件冲突
                    is_username_conflict = await conn.fetchval(
                        "SELECT EXISTS(SELECT 1 FROM users WHERE username = $1)",
                        username
                    )
                    
                    if is_username_conflict:
                        raise UserExistsError("用户名", username)
                    else:
                        raise UserExistsError("电子邮件", email)
                
                # 生成用户ID
                user_id = str(uuid.uuid4())
                now = datetime.utcnow()
                
                # 创建用户记录
                await conn.execute(
                    """
                    INSERT INTO users (id, username, email, password, phone_number, 
                                       profile_data, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $7)
                    """,
                    user_id, username, email, hashed_password, phone_number,
                    profile_data or {}, now
                )
                
                # 分配默认角色
                await conn.execute(
                    """
                    INSERT INTO user_roles (user_id, role_id)
                    SELECT $1, id FROM roles WHERE name = 'user'
                    """,
                    user_id
                )
                
                return user_id, username, email
                
            except UserExistsError:
                # 重新抛出用户存在错误
                raise
            except Exception as e:
                self.logger.exception("创建用户时发生数据库错误")
                raise DatabaseError(f"创建用户失败: {str(e)}")
    
    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户数据
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    """
                    SELECT id, username, email, password, phone_number, profile_data,
                           is_active, is_locked, mfa_enabled, mfa_type, mfa_secret,
                           created_at, updated_at, last_login_at
                    FROM users
                    WHERE id = $1
                    """,
                    user_id
                )
                
                if not user:
                    raise UserNotFoundError(user_id)
                
                return dict(user)
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"根据ID获取用户时发生数据库错误: {user_id}")
                raise DatabaseError(f"获取用户失败: {str(e)}")
    
    async def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Dict: 用户数据
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    """
                    SELECT id, username, email, password, phone_number, profile_data,
                           is_active, is_locked, mfa_enabled, mfa_type, mfa_secret,
                           created_at, updated_at, last_login_at
                    FROM users
                    WHERE username = $1
                    """,
                    username
                )
                
                if not user:
                    raise UserNotFoundError(username)
                
                return dict(user)
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"根据用户名获取用户时发生数据库错误: {username}")
                raise DatabaseError(f"获取用户失败: {str(e)}")
    
    async def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        根据电子邮件获取用户
        
        Args:
            email: 电子邮件
            
        Returns:
            Dict: 用户数据
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    """
                    SELECT id, username, email, password, phone_number, profile_data,
                           is_active, is_locked, mfa_enabled, mfa_type, mfa_secret,
                           created_at, updated_at, last_login_at
                    FROM users
                    WHERE email = $1
                    """,
                    email
                )
                
                if not user:
                    raise UserNotFoundError(email)
                
                return dict(user)
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"根据电子邮件获取用户时发生数据库错误: {email}")
                raise DatabaseError(f"获取用户失败: {str(e)}")
    
    async def get_user_by_phone(self, phone_number: str) -> Dict[str, Any]:
        """
        根据手机号码获取用户
        
        Args:
            phone_number: 手机号码
            
        Returns:
            Dict: 用户数据
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                user = await conn.fetchrow(
                    """
                    SELECT id, username, email, password, phone_number, profile_data,
                           is_active, is_locked, mfa_enabled, mfa_type, mfa_secret,
                           created_at, updated_at, last_login_at
                    FROM users
                    WHERE phone_number = $1
                    """,
                    phone_number
                )
                
                if not user:
                    raise UserNotFoundError(phone_number)
                
                return dict(user)
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"根据手机号码获取用户时发生数据库错误: {phone_number}")
                raise DatabaseError(f"获取用户失败: {str(e)}")
    
    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """
        更新用户密码
        
        Args:
            user_id: 用户ID
            hashed_password: 哈希后的新密码
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute(
                    """
                    UPDATE users
                    SET password = $2, updated_at = $3
                    WHERE id = $1
                    """,
                    user_id, hashed_password, datetime.utcnow()
                )
                
                if result == "UPDATE 0":
                    raise UserNotFoundError(user_id)
                
                return True
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"更新用户密码时发生数据库错误: {user_id}")
                raise DatabaseError(f"更新密码失败: {str(e)}")
    
    async def update_login_timestamp(self, user_id: str) -> bool:
        """
        更新用户最后登录时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                now = datetime.utcnow()
                result = await conn.execute(
                    """
                    UPDATE users
                    SET last_login_at = $2, updated_at = $2
                    WHERE id = $1
                    """,
                    user_id, now
                )
                
                if result == "UPDATE 0":
                    raise UserNotFoundError(user_id)
                
                return True
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"更新用户登录时间戳时发生数据库错误: {user_id}")
                raise DatabaseError(f"更新登录时间失败: {str(e)}")
    
    async def enable_mfa(self, user_id: str, mfa_type: str, mfa_secret: str) -> bool:
        """
        为用户启用多因素认证
        
        Args:
            user_id: 用户ID
            mfa_type: 多因素认证类型 (totp, sms, email)
            mfa_secret: 多因素认证密钥
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                now = datetime.utcnow()
                result = await conn.execute(
                    """
                    UPDATE users
                    SET mfa_enabled = true, mfa_type = $2, mfa_secret = $3, updated_at = $4
                    WHERE id = $1
                    """,
                    user_id, mfa_type, mfa_secret, now
                )
                
                if result == "UPDATE 0":
                    raise UserNotFoundError(user_id)
                
                return True
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"启用用户多因素认证时发生数据库错误: {user_id}")
                raise DatabaseError(f"启用多因素认证失败: {str(e)}")
    
    async def disable_mfa(self, user_id: str) -> bool:
        """
        为用户禁用多因素认证
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                now = datetime.utcnow()
                result = await conn.execute(
                    """
                    UPDATE users
                    SET mfa_enabled = false, updated_at = $2
                    WHERE id = $1
                    """,
                    user_id, now
                )
                
                if result == "UPDATE 0":
                    raise UserNotFoundError(user_id)
                
                return True
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"禁用用户多因素认证时发生数据库错误: {user_id}")
                raise DatabaseError(f"禁用多因素认证失败: {str(e)}")
    
    async def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        获取用户角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 角色列表，每个角色包含id, name, description和permissions
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                # 首先检查用户是否存在
                user_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)",
                    user_id
                )
                
                if not user_exists:
                    raise UserNotFoundError(user_id)
                
                # 获取用户角色
                roles = await conn.fetch(
                    """
                    SELECT r.id, r.name, r.description
                    FROM roles r
                    JOIN user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = $1
                    """,
                    user_id
                )
                
                # 将角色转换为字典格式
                role_dicts = []
                for role in roles:
                    role_dict = dict(role)
                    
                    # 获取每个角色的权限
                    permissions = await conn.fetch(
                        """
                        SELECT p.name
                        FROM permissions p
                        JOIN role_permissions rp ON p.id = rp.permission_id
                        WHERE rp.role_id = $1
                        """,
                        role['id']
                    )
                    
                    role_dict['permissions'] = [p['name'] for p in permissions]
                    role_dicts.append(role_dict)
                
                return role_dicts
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"获取用户角色时发生数据库错误: {user_id}")
                raise DatabaseError(f"获取用户角色失败: {str(e)}")
    
    async def check_permission(self, user_id: str, permission_name: str, 
                               resource_id: Optional[str] = None) -> bool:
        """
        检查用户是否拥有特定权限
        
        Args:
            user_id: 用户ID
            permission_name: 权限名称
            resource_id: 资源ID (可选，用于资源特定权限)
            
        Returns:
            bool: 用户是否拥有权限
            
        Raises:
            UserNotFoundError: 如果用户不存在
            DatabaseError: 数据库操作失败
        """
        async with self.pool.acquire() as conn:
            try:
                # 首先检查用户是否存在
                user_exists = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)",
                    user_id
                )
                
                if not user_exists:
                    raise UserNotFoundError(user_id)
                
                # 检查用户是否有此权限(通过角色)
                has_permission = await conn.fetchval(
                    """
                    SELECT EXISTS(
                        SELECT 1
                        FROM permissions p
                        JOIN role_permissions rp ON p.id = rp.permission_id
                        JOIN user_roles ur ON rp.role_id = ur.role_id
                        WHERE ur.user_id = $1 AND p.name = $2
                    )
                    """,
                    user_id, permission_name
                )
                
                # 如果指定了资源ID，还需要检查用户是否有权限访问该资源
                if has_permission and resource_id:
                    # 此处简化实现，实际场景可能需要根据不同资源类型有不同的检查逻辑
                    resource_permission = await conn.fetchval(
                        """
                        SELECT EXISTS(
                            SELECT 1
                            FROM user_resource_permissions
                            WHERE user_id = $1 AND resource_id = $2 AND permission = $3
                        )
                        """,
                        user_id, resource_id, permission_name
                    )
                    
                    return bool(resource_permission)
                
                return bool(has_permission)
                
            except UserNotFoundError:
                # 重新抛出用户未找到错误
                raise
            except Exception as e:
                self.logger.exception(f"检查用户权限时发生数据库错误: {user_id}, {permission_name}")
                raise DatabaseError(f"检查权限失败: {str(e)}") 