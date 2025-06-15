"""
角色仓储实现

处理角色和权限数据的存储和检索。
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, func

from .base import CacheableRepository
from internal.db.models import RoleModel, PermissionModel, RolePermissionModel


class RoleRepository(CacheableRepository[RoleModel]):
    """角色仓储类"""
    
    def __init__(self):
        super().__init__(RoleModel, cache_ttl=1800)  # 30分钟缓存
    
    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """根据名称获取角色"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(RoleModel)
                .options(selectinload(RoleModel.permissions).selectinload(RolePermissionModel.permission))
                .where(RoleModel.name == name)
            )
            return result.scalar_one_or_none()
    
    async def get_roles(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[RoleModel]:
        """获取角色列表"""
        async with await self.get_session() as session:
            query = select(RoleModel).options(
                selectinload(RoleModel.permissions).selectinload(RolePermissionModel.permission)
            )
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        RoleModel.name.ilike(search_pattern),
                        RoleModel.description.ilike(search_pattern)
                    )
                )
            
            # 添加活跃状态过滤
            if is_active is not None:
                query = query.where(RoleModel.is_active == is_active)
            
            # 添加分页
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def count_roles(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """统计角色数量"""
        async with await self.get_session() as session:
            query = select(func.count(RoleModel.id))
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        RoleModel.name.ilike(search_pattern),
                        RoleModel.description.ilike(search_pattern)
                    )
                )
            
            # 添加活跃状态过滤
            if is_active is not None:
                query = query.where(RoleModel.is_active == is_active)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def assign_permission(self, role_id: str, permission_id: str) -> bool:
        """为角色分配权限"""
        async with await self.get_session() as session:
            # 检查角色和权限是否存在
            role = await session.get(RoleModel, role_id)
            permission = await session.get(PermissionModel, permission_id)
            if not role or not permission:
                return False
            
            # 检查是否已经分配
            existing = await session.execute(
                select(RolePermissionModel).where(
                    and_(
                        RolePermissionModel.role_id == role_id,
                        RolePermissionModel.permission_id == permission_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                return True  # 已经分配
            
            # 创建角色权限关联
            role_permission = RolePermissionModel(
                role_id=role_id,
                permission_id=permission_id,
                assigned_at=datetime.utcnow()
            )
            session.add(role_permission)
            await session.commit()
            
            # 使缓存失效
            await self.invalidate_cache(role_id)
            return True
    
    async def remove_permission(self, role_id: str, permission_id: str) -> bool:
        """移除角色权限"""
        async with await self.get_session() as session:
            # 删除角色权限关联
            result = await session.execute(
                select(RolePermissionModel).where(
                    and_(
                        RolePermissionModel.role_id == role_id,
                        RolePermissionModel.permission_id == permission_id
                    )
                )
            )
            role_permission = result.scalar_one_or_none()
            if role_permission:
                await session.delete(role_permission)
                await session.commit()
                
                # 使缓存失效
                await self.invalidate_cache(role_id)
                return True
            
            return False
    
    async def get_role_permissions(self, role_id: str) -> List[PermissionModel]:
        """获取角色权限"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel)
                .join(RolePermissionModel)
                .where(RolePermissionModel.role_id == role_id)
            )
            return list(result.scalars().all())
    
    async def has_permission(self, role_id: str, resource: str, action: str) -> bool:
        """检查角色是否有特定权限"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel)
                .join(RolePermissionModel)
                .where(
                    and_(
                        RolePermissionModel.role_id == role_id,
                        PermissionModel.resource == resource,
                        PermissionModel.action == action
                    )
                )
            )
            return result.scalar_one_or_none() is not None


class PermissionRepository(CacheableRepository[PermissionModel]):
    """权限仓储类"""
    
    def __init__(self):
        super().__init__(PermissionModel, cache_ttl=3600)  # 1小时缓存
    
    async def get_by_resource_action(self, resource: str, action: str) -> Optional[PermissionModel]:
        """根据资源和动作获取权限"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel).where(
                    and_(
                        PermissionModel.resource == resource,
                        PermissionModel.action == action
                    )
                )
            )
            return result.scalar_one_or_none()
    
    async def get_permissions(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        resource: Optional[str] = None
    ) -> List[PermissionModel]:
        """获取权限列表"""
        async with await self.get_session() as session:
            query = select(PermissionModel)
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        PermissionModel.name.ilike(search_pattern),
                        PermissionModel.description.ilike(search_pattern),
                        PermissionModel.resource.ilike(search_pattern),
                        PermissionModel.action.ilike(search_pattern)
                    )
                )
            
            # 添加资源过滤
            if resource:
                query = query.where(PermissionModel.resource == resource)
            
            # 添加分页
            query = query.offset(skip).limit(limit)
            
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def count_permissions(
        self,
        search: Optional[str] = None,
        resource: Optional[str] = None
    ) -> int:
        """统计权限数量"""
        async with await self.get_session() as session:
            query = select(func.count(PermissionModel.id))
            
            # 添加搜索条件
            if search:
                search_pattern = f"%{search}%"
                query = query.where(
                    or_(
                        PermissionModel.name.ilike(search_pattern),
                        PermissionModel.description.ilike(search_pattern),
                        PermissionModel.resource.ilike(search_pattern),
                        PermissionModel.action.ilike(search_pattern)
                    )
                )
            
            # 添加资源过滤
            if resource:
                query = query.where(PermissionModel.resource == resource)
            
            result = await session.execute(query)
            return result.scalar()
    
    async def get_resources(self) -> List[str]:
        """获取所有资源列表"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel.resource).distinct()
            )
            return [row[0] for row in result.fetchall()]
    
    async def get_actions_by_resource(self, resource: str) -> List[str]:
        """获取指定资源的所有动作"""
        async with await self.get_session() as session:
            result = await session.execute(
                select(PermissionModel.action)
                .where(PermissionModel.resource == resource)
                .distinct()
            )
            return [row[0] for row in result.fetchall()]