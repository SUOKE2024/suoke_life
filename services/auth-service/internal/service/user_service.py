#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户服务模块

提供用户管理相关的业务逻辑。
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from internal.model.user import (
    User, UserCreate, UserUpdate, UserResponse, UserStatusEnum
)
from internal.repository.user_repository import UserRepository
from internal.security.password import PasswordManager
from internal.config.settings import get_settings


class UserService:
    """用户服务类"""
    
    def __init__(self, user_repository: UserRepository, password_manager: PasswordManager):
        self.user_repository = user_repository
        self.password_manager = password_manager
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        创建新用户
        
        Args:
            user_data: 用户创建数据
            
        Returns:
            UserResponse: 创建的用户响应
            
        Raises:
            ValueError: 用户已存在或数据无效
        """
        self.logger.info(f"创建用户: {user_data.username}")
        
        # 检查用户名是否已存在
        existing_user = await self.user_repository.get_by_username(user_data.username)
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = await self.user_repository.get_by_email(user_data.email)
        if existing_email:
            raise ValueError("邮箱已存在")
        
        # 验证密码强度
        if not self.password_manager.validate_password_strength(user_data.password):
            raise ValueError("密码强度不符合要求")
        
        # 创建用户对象
        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            password_hash=self.password_manager.hash_password(user_data.password),
            phone_number=user_data.phone_number,
            profile_data=user_data.profile_data,
            status=UserStatusEnum.PENDING_VERIFICATION,
            created_at=datetime.utcnow()
        )
        
        # 保存用户
        created_user = await self.user_repository.create(user)
        
        # 返回用户响应
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            phone_number=created_user.phone_number,
            status=created_user.status,
            profile_data=created_user.profile_data,
            is_active=created_user.is_active,
            mfa_enabled=created_user.mfa_enabled,
            email_verified=created_user.email_verified,
            phone_verified=created_user.phone_verified,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at,
            last_login=created_user.last_login,
            roles=[role.name for role in created_user.roles],
            permissions=created_user.permissions
        )
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserResponse]: 用户响应或None
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
            status=user.status,
            profile_data=user.profile_data,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            roles=[role.name for role in user.roles],
            permissions=user.permissions
        )
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 用户对象或None
        """
        return await self.user_repository.get_by_username(username)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            Optional[User]: 用户对象或None
        """
        return await self.user_repository.get_by_email(email)
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新数据
            
        Returns:
            UserResponse: 更新后的用户响应
            
        Raises:
            ValueError: 用户不存在或数据无效
        """
        self.logger.info(f"更新用户: {user_id}")
        
        # 获取现有用户
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("用户不存在")
        
        # 检查用户名是否已被其他用户使用
        if user_data.username and user_data.username != user.username:
            existing_user = await self.user_repository.get_by_username(user_data.username)
            if existing_user and existing_user.id != user_id:
                raise ValueError("用户名已存在")
        
        # 检查邮箱是否已被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_email = await self.user_repository.get_by_email(user_data.email)
            if existing_email and existing_email.id != user_id:
                raise ValueError("邮箱已存在")
        
        # 更新用户信息
        update_data = {}
        if user_data.username:
            update_data["username"] = user_data.username
        if user_data.email:
            update_data["email"] = user_data.email
        if user_data.phone_number is not None:
            update_data["phone_number"] = user_data.phone_number
        if user_data.profile_data is not None:
            update_data["profile_data"] = user_data.profile_data
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        if user_data.status is not None:
            update_data["status"] = user_data.status
        
        update_data["updated_at"] = datetime.utcnow()
        
        # 执行更新
        updated_user = await self.user_repository.update(user_id, update_data)
        
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            phone_number=updated_user.phone_number,
            status=updated_user.status,
            profile_data=updated_user.profile_data,
            is_active=updated_user.is_active,
            mfa_enabled=updated_user.mfa_enabled,
            email_verified=updated_user.email_verified,
            phone_verified=updated_user.phone_verified,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            last_login=updated_user.last_login,
            roles=[role.name for role in updated_user.roles],
            permissions=updated_user.permissions
        )
    
    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        self.logger.info(f"删除用户: {user_id}")
        return await self.user_repository.delete(user_id)
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None
    ) -> List[UserResponse]:
        """
        获取用户列表
        
        Args:
            skip: 跳过数量
            limit: 限制数量
            search: 搜索关键词
            
        Returns:
            List[UserResponse]: 用户响应列表
        """
        users = await self.user_repository.get_users(skip, limit, search)
        
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                phone_number=user.phone_number,
                status=user.status,
                profile_data=user.profile_data,
                is_active=user.is_active,
                mfa_enabled=user.mfa_enabled,
                email_verified=user.email_verified,
                phone_verified=user.phone_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login=user.last_login,
                roles=[role.name for role in user.roles],
                permissions=user.permissions
            )
            for user in users
        ]
    
    async def activate_user(self, user_id: str) -> bool:
        """
        激活用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 激活是否成功
        """
        self.logger.info(f"激活用户: {user_id}")
        
        update_data = {
            "status": UserStatusEnum.ACTIVE,
            "is_active": True,
            "updated_at": datetime.utcnow()
        }
        
        updated_user = await self.user_repository.update(user_id, update_data)
        return updated_user is not None
    
    async def deactivate_user(self, user_id: str) -> bool:
        """
        停用用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 停用是否成功
        """
        self.logger.info(f"停用用户: {user_id}")
        
        update_data = {
            "status": UserStatusEnum.INACTIVE,
            "is_active": False,
            "updated_at": datetime.utcnow()
        }
        
        updated_user = await self.user_repository.update(user_id, update_data)
        return updated_user is not None
    
    async def verify_email(self, user_id: str) -> bool:
        """
        验证用户邮箱
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 验证是否成功
        """
        self.logger.info(f"验证用户邮箱: {user_id}")
        
        update_data = {
            "email_verified": True,
            "updated_at": datetime.utcnow()
        }
        
        updated_user = await self.user_repository.update(user_id, update_data)
        return updated_user is not None
    
    async def verify_phone(self, user_id: str) -> bool:
        """
        验证用户手机
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 验证是否成功
        """
        self.logger.info(f"验证用户手机: {user_id}")
        
        update_data = {
            "phone_verified": True,
            "updated_at": datetime.utcnow()
        }
        
        updated_user = await self.user_repository.update(user_id, update_data)
        return updated_user is not None
    
    async def update_last_login(self, user_id: str) -> bool:
        """
        更新用户最后登录时间
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 更新是否成功
        """
        update_data = {
            "last_login": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        updated_user = await self.user_repository.update(user_id, update_data)
        return updated_user is not None


# 兼容性函数，保持向后兼容
async def create_user(user_data: Dict[str, Any]) -> User:
    """创建用户的兼容性函数"""
    # 这里应该注入UserService实例，暂时返回简单实现
    return User(
        id=str(uuid.uuid4()),
        username=user_data.get("username"),
        email=user_data.get("email"),
        roles=[],
        is_active=True
    )


async def get_user(user_id: str) -> Optional[User]:
    """获取用户的兼容性函数"""
    # 这里应该注入UserService实例，暂时返回简单实现
    if user_id == "1":
        return User(
            id="1",
            username="admin",
            email="admin@example.com",
            roles=[],
            is_active=True
        )
    return None


async def get_users(skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[User]:
    """获取用户列表的兼容性函数"""
    # 这里应该注入UserService实例，暂时返回简单实现
    return [
        User(
            id="1",
            username="admin",
            email="admin@example.com",
            roles=[],
            is_active=True
        )
    ]


async def update_user(user_id: str, user_data: Dict[str, Any]) -> User:
    """更新用户的兼容性函数"""
    # 这里应该注入UserService实例，暂时返回简单实现
    user = await get_user(user_id)
    if not user:
        raise ValueError("用户不存在")
    return user


async def delete_user(user_id: str) -> bool:
    """删除用户的兼容性函数"""
    # 这里应该注入UserService实例，暂时返回简单实现
    return True 