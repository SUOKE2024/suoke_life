"""
用户仓储实现 - 基于SQLAlchemy ORM

处理用户数据的存储和检索，使用现代化的ORM模式。
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, func

from .base import CacheableRepository
from internal.db.models import UserModel, RoleModel, UserRoleModel, PermissionModel
from internal.model.user import User, UserStatusEnum


class UserRepository(CacheableRepository[UserModel]):
    """用户仓储类"""
    
    def __init__(self):
        super().__init__(UserModel, cache_ttl=600)  # 10分钟缓存
    
    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """根据用户名获取用户"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.roles).selectinload(UserRoleModel.role))
                .where(UserModel.username == username)
            )
            return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """根据邮箱获取用户"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.roles).selectinload(UserRoleModel.role))
                .where(UserModel.email == email)
            )
            return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone_number: str) -> Optional[UserModel]:
        """根据手机号获取用户"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(UserModel)
                .options(selectinload(UserModel.roles).selectinload(UserRoleModel.role))
                .where(UserModel.phone_number == phone_number)
            )
            return result.scalar_one_or_none()
    
    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        status: Optional[UserStatusEnum] = None,
        is_active: Optional[bool] = None
    ) -> List[UserModel]:
        """获取用户列表"""
        async with await self.get_session() as session:
            query = select(UserModel).options(
                selectinload(UserModel.roles).selectinload(UserRoleModel.role)
            )
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        UserModel.username.ilike(search_pattern),
                        UserModel.email.ilike(search_pattern),
                        UserModel.phone_number.ilike(search_pattern)
                    )
                )
            
            # 添加状态过滤
            if status:
                query = query.where(UserModel.status == status.value)
            
            # 添加活跃状态过滤
            if is_active is not None:
                query = query.where(UserModel.is_active == is_active)
            
            # 添加分页
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def count_users(
        self,
        search: Optional[str] = None,
        status: Optional[UserStatusEnum] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """统计用户数量"""
        async with await self.get_session() as session:
            query = select(func.count(UserModel.id))
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        UserModel.username.ilike(search_pattern),
                        UserModel.email.ilike(search_pattern),
                        UserModel.phone_number.ilike(search_pattern)
                    )
                )
            
            # 添加状态过滤
            if status:
                query = query.where(UserModel.status == status.value)
            
            # 添加活跃状态过滤
            if is_active is not None:
                query = query.where(UserModel.is_active == is_active)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def create_user_with_roles(
        self, 
        user: UserModel, 
        role_names: List[str] = None
    ) -> UserModel:
        """创建用户并分配角色"""
        async with await self.get_session() as session:
            # 添加用户
            session.add(user)
            await session.flush()  # 获取用户ID
            
            # 分配角色
            if role_names:
                roles_result = await session.execute(
                    select(RoleModel).where(RoleModel.name.in_(role_names))
                )
                roles = list(roles_result.scalars().all())
                
                for role in roles:
                    user_role = UserRoleModel(
                        user_id=user.id,
                        role_id=role.id,
                        assigned_at=datetime.utcnow()
                    )
                    session.add(user_role)
            else:
                # 分配默认用户角色
                default_role = await session.execute(
                    select(RoleModel).where(RoleModel.name == "user")
                )
                role = default_role.scalar_one_or_none()
                if role:
                    user_role = UserRoleModel(
                        user_id=user.id,
                        role_id=role.id,
                        assigned_at=datetime.utcnow()
                    )
                    session.add(user_role)
            
            await session.commit()
            await session.refresh(user)
            return user
    
    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """为用户分配角色"""
        async with await self.get_session() as session:
            # 检查用户是否存在
            user = await session.get(UserModel, user_id)
            if not user:
                return False
            
            # 获取角色
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            if not role:
                return False
            
            # 检查是否已经分配
            existing = await session.execute(
                select(UserRoleModel).where(
                    and_(
                        UserRoleModel.user_id == user_id,
                        UserRoleModel.role_id == role.id
                    )
                )
            )
            if existing.scalar_one_or_none():
                return True  # 已经分配
            
            # 创建用户角色关联
            user_role = UserRoleModel(
                user_id=user_id,
                role_id=role.id,
                assigned_at=datetime.utcnow()
            )
            session.add(user_role)
            await session.commit()
            
            # 使缓存失效
            await self.invalidate_cache(user_id)
            return True
    
    async def remove_role(self, user_id: str, role_name: str) -> bool:
        """移除用户角色"""
        async with await self.get_session() as session:
            # 获取角色
            role_result = await session.execute(
                select(RoleModel).where(RoleModel.name == role_name)
            )
            role = role_result.scalar_one_or_none()
            if not role:
                return False
            
            # 删除用户角色关联
            result = await session.execute(
                select(UserRoleModel).where(
                    and_(
                        UserRoleModel.user_id == user_id,
                        UserRoleModel.role_id == role.id
                    )
                )
            )
            user_role = result.scalar_one_or_none()
            if user_role:
                await session.delete(user_role)
                await session.commit()
                
                # 使缓存失效
                await self.invalidate_cache(user_id)
                return True
            
            return False
    
    async def get_user_roles(self, user_id: str) -> List[RoleModel]:
        """获取用户角色"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RoleModel)
                .join(UserRoleModel)
                .where(UserRoleModel.user_id == user_id)
            )
            return list(result.scalars().all())
    
    async def get_user_permissions(self, user_id: str) -> List[PermissionModel]:
        """获取用户权限"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel)
                .join(RoleModel.permissions)
                .join(UserRoleModel)
                .where(UserRoleModel.user_id == user_id)
                .distinct()
            )
            return list(result.scalars().all())
    
    async def has_permission(self, user_id: str, resource: str, action: str) -> bool:
        """检查用户是否有特定权限"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel)
                .join(RoleModel.permissions)
                .join(UserRoleModel)
                .where(
                    and_(
                        UserRoleModel.user_id == user_id,
                        PermissionModel.resource == resource,
                        PermissionModel.action == action
                    )
                )
            )
            return result.scalar_one_or_none() is not None
    
    async def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        return await self.update(user_id, {
            "last_login": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }) is not None
    
    async def increment_failed_login_attempts(self, user_id: str) -> int:
        """增加失败登录次数"""
        async with await self.get_session() as session:
            user = await session.get(UserModel, user_id)
            if user:
                user.failed_login_attempts += 1
                user.updated_at = datetime.utcnow()
                await session.commit()
                await self.invalidate_cache(user_id)
                return user.failed_login_attempts
            return 0
    
    async def reset_failed_login_attempts(self, user_id: str) -> bool:
        """重置失败登录次数"""
        return await self.update(user_id, {
            "failed_login_attempts": 0,
            "locked_until": None,
            "updated_at": datetime.utcnow()
        }) is not None
    
    async def lock_user(self, user_id: str, locked_until: datetime) -> bool:
        """锁定用户"""
        return await self.update(user_id, {
            "locked_until": locked_until,
            "updated_at": datetime.utcnow()
        }) is not None
    
    async def unlock_user(self, user_id: str) -> bool:
        """解锁用户"""
        return await self.update(user_id, {
            "locked_until": None,
            "failed_login_attempts": 0,
            "updated_at": datetime.utcnow()
        }) is not None
    
    async def is_user_locked(self, user_id: str) -> bool:
        """检查用户是否被锁定"""
        user = await self.get_by_id(user_id)
        if not user or not user.locked_until:
            return False
        return user.locked_until > datetime.utcnow()
    
    async def activate_user(self, user_id: str) -> bool:
        """激活用户"""
        return await self.update(user_id, {
            "status": UserStatusEnum.ACTIVE.value,
            "is_active": True,
            "updated_at": datetime.utcnow()
        }) is not None
    
    async def deactivate_user(self, user_id: str) -> bool:
        """停用用户"""
        return await self.update(user_id, {
            "status": UserStatusEnum.INACTIVE.value,
            "is_active": False,
            "updated_at": datetime.utcnow()
        }) is not None 