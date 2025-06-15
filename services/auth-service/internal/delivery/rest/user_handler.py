#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户管理路由处理器

处理用户管理相关的HTTP请求，包括用户CRUD操作、权限管理、个人资料管理等。
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request

from ...model.user import User, UserCreate, UserResponse, UserUpdate
from ...schemas.auth import RoleResponse, PermissionResponse
from ...service.auth_service_complete import AuthService, get_auth_service
from ...service.user_service import UserService, get_user_service
from ...service.metrics_service import MetricsService, get_metrics_service
from ...repository.role_repository import RoleRepository, PermissionRepository
from ...repository.user_repository_new import UserRepository

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])


class UserHandler:
    """用户管理路由处理器类"""
    
    def __init__(
        self,
        auth_service: AuthService,
        user_service: UserService,
        metrics_service: MetricsService
    ):
        self.auth_service = auth_service
        self.user_service = user_service
        self.metrics_service = metrics_service
    
    async def get_current_user_info(
        self,
        current_user: User
    ) -> UserResponse:
        """
        获取当前用户信息
        
        Args:
            current_user: 当前用户
        
        Returns:
            UserResponse: 用户信息响应
        """
        logger.info(f"获取当前用户信息: {current_user.id}")
        
        try:
            # 获取完整的用户信息
            user = await self.user_service.get_user_by_id(current_user.id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            return UserResponse.from_orm(user)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取当前用户信息失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户信息失败"
            )
    
    async def update_current_user(
        self,
        request: Request,
        user_data: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """
        更新当前用户信息
        
        Args:
            request: HTTP请求对象
            user_data: 用户更新数据
            current_user: 当前用户
        
        Returns:
            UserResponse: 更新后的用户信息
        """
        logger.info(f"更新当前用户信息: {current_user.id}")
        
        try:
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 更新用户信息
            updated_user = await self.user_service.update_user(
                user_id=current_user.id,
                user_data=user_data,
                ip_address=client_ip
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_update_success_total",
                {"user_id": str(current_user.id)}
            )
            
            return UserResponse.from_orm(updated_user)
            
        except ValueError as e:
            logger.warning(f"用户信息更新失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_update_failures_total",
                {"reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_update_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
    
    async def get_users(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        role_filter: Optional[str] = None
    ) -> List[UserResponse]:
        """
        获取用户列表（需要管理员权限）
        
        Args:
            current_user: 当前用户
            skip: 跳过记录数
            limit: 限制记录数
            search: 搜索关键词
            status_filter: 状态过滤
            role_filter: 角色过滤
        
        Returns:
            List[UserResponse]: 用户列表
        """
        logger.info(f"获取用户列表请求: {current_user.id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "users", "read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限访问用户列表",
                )
            
            # 构建过滤条件
            filters = {}
            if status_filter:
                filters["status"] = status_filter
            if role_filter:
                filters["role"] = role_filter
            
            # 获取用户列表
            users = await self.user_service.get_users(
                skip=skip,
                limit=limit,
                search=search,
                filters=filters
            )
            
            return [UserResponse.from_orm(user) for user in users]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户列表失败"
            )
    
    async def get_user_by_id(
        self,
        user_id: UUID,
        current_user: User
    ) -> UserResponse:
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
            current_user: 当前用户
        
        Returns:
            UserResponse: 用户信息
        """
        logger.info(f"获取用户信息: {user_id}")
        
        try:
            # 检查权限（管理员或本人）
            if str(current_user.id) != str(user_id):
                if not await self._check_permission(current_user, "users", "read"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="没有权限访问该用户信息",
                    )
            
            # 获取用户信息
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            return UserResponse.from_orm(user)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户信息失败"
            )
    
    async def create_user(
        self,
        request: Request,
        user_data: UserCreate,
        current_user: User
    ) -> UserResponse:
        """
        创建新用户（需要管理员权限）
        
        Args:
            request: HTTP请求对象
            user_data: 用户创建数据
            current_user: 当前用户
        
        Returns:
            UserResponse: 创建的用户信息
        """
        logger.info(f"创建用户请求: {user_data.username}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "users", "create"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限创建用户",
                )
            
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 创建用户
            user = await self.user_service.create_user(user_data, client_ip)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_create_success_total",
                {"created_by": str(current_user.id)}
            )
            
            return UserResponse.from_orm(user)
            
        except ValueError as e:
            logger.warning(f"用户创建失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_create_failures_total",
                {"reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_create_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败"
            )
    
    async def update_user(
        self,
        request: Request,
        user_id: UUID,
        user_data: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """
        更新用户信息
        
        Args:
            request: HTTP请求对象
            user_id: 用户ID
            user_data: 用户更新数据
            current_user: 当前用户
        
        Returns:
            UserResponse: 更新后的用户信息
        """
        logger.info(f"更新用户信息: {user_id}")
        
        try:
            # 检查权限（管理员或本人）
            if str(current_user.id) != str(user_id):
                if not await self._check_permission(current_user, "users", "update"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="没有权限更新该用户信息",
                    )
            
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 更新用户信息
            updated_user = await self.user_service.update_user(
                user_id=user_id,
                user_data=user_data,
                ip_address=client_ip
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_update_success_total",
                {"updated_by": str(current_user.id)}
            )
            
            return UserResponse.from_orm(updated_user)
            
        except ValueError as e:
            logger.warning(f"用户信息更新失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_update_failures_total",
                {"reason": "validation_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新用户信息失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_update_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )
    
    async def delete_user(
        self,
        request: Request,
        user_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        删除用户（需要管理员权限）
        
        Args:
            request: HTTP请求对象
            user_id: 用户ID
            current_user: 当前用户
        
        Returns:
            Dict[str, str]: 删除响应
        """
        logger.info(f"删除用户请求: {user_id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "users", "delete"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限删除用户",
                )
            
            # 不能删除自己
            if str(current_user.id) == str(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能删除自己的账户",
                )
            
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 删除用户
            await self.user_service.delete_user(user_id, client_ip)
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_delete_success_total",
                {"deleted_by": str(current_user.id)}
            )
            
            return {"detail": "用户删除成功"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_delete_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败"
            )
    
    async def get_roles(
        self,
        current_user: User
    ) -> List[RoleResponse]:
        """
        获取角色列表
        
        Args:
            current_user: 当前用户
        
        Returns:
            List[RoleResponse]: 角色列表
        """
        logger.info(f"获取角色列表请求: {current_user.id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "roles", "read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限访问角色列表",
                )
            
            # 获取角色列表
            roles = await self.user_service.get_all_roles()
            
            return [
                RoleResponse(
                    id=str(role.id),
                    name=role.name,
                    description=role.description,
                    permissions=[perm.name for perm in role.permissions]
                )
                for role in roles
            ]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取角色列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取角色列表失败"
            )
    
    async def get_permissions(
        self,
        current_user: User
    ) -> List[PermissionResponse]:
        """
        获取权限列表
        
        Args:
            current_user: 当前用户
        
        Returns:
            List[PermissionResponse]: 权限列表
        """
        logger.info(f"获取权限列表请求: {current_user.id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "permissions", "read"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限访问权限列表",
                )
            
            # 获取权限列表
            permissions = await self.user_service.get_all_permissions()
            
            return [
                PermissionResponse(
                    id=str(perm.id),
                    name=perm.name,
                    resource=perm.resource,
                    action=perm.action,
                    description=perm.description
                )
                for perm in permissions
            ]
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取权限列表失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取权限列表失败"
            )
    
    async def assign_role_to_user(
        self,
        request: Request,
        user_id: UUID,
        role_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        为用户分配角色
        
        Args:
            request: HTTP请求对象
            user_id: 用户ID
            role_id: 角色ID
            current_user: 当前用户
        
        Returns:
            Dict[str, str]: 分配响应
        """
        logger.info(f"为用户分配角色: {user_id} -> {role_id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "user_roles", "create"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限分配角色",
                )
            
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 分配角色
            await self.user_service.assign_role_to_user(
                user_id=user_id,
                role_id=role_id,
                assigned_by=current_user.id,
                ip_address=client_ip
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_role_assign_success_total",
                {"assigned_by": str(current_user.id)}
            )
            
            return {"detail": "角色分配成功"}
            
        except ValueError as e:
            logger.warning(f"角色分配失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"分配角色失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_role_assign_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="分配角色失败"
            )
    
    async def remove_role_from_user(
        self,
        request: Request,
        user_id: UUID,
        role_id: UUID,
        current_user: User
    ) -> Dict[str, str]:
        """
        从用户移除角色
        
        Args:
            request: HTTP请求对象
            user_id: 用户ID
            role_id: 角色ID
            current_user: 当前用户
        
        Returns:
            Dict[str, str]: 移除响应
        """
        logger.info(f"从用户移除角色: {user_id} -> {role_id}")
        
        try:
            # 检查权限
            if not await self._check_permission(current_user, "user_roles", "delete"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限移除角色",
                )
            
            # 获取客户端IP地址
            client_ip = self._get_client_ip(request)
            
            # 移除角色
            await self.user_service.remove_role_from_user(
                user_id=user_id,
                role_id=role_id,
                removed_by=current_user.id,
                ip_address=client_ip
            )
            
            # 记录成功指标
            await self.metrics_service.increment_counter(
                "user_role_remove_success_total",
                {"removed_by": str(current_user.id)}
            )
            
            return {"detail": "角色移除成功"}
            
        except ValueError as e:
            logger.warning(f"角色移除失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"移除角色失败: {str(e)}")
            await self.metrics_service.increment_counter(
                "user_role_remove_errors_total",
                {"error": "system_error"}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="移除角色失败"
            )
    
    async def get_user_permissions(
        self,
        user_id: UUID,
        current_user: User
    ) -> List[str]:
        """
        获取用户权限列表
        
        Args:
            user_id: 用户ID
            current_user: 当前用户
        
        Returns:
            List[str]: 权限列表
        """
        logger.info(f"获取用户权限: {user_id}")
        
        try:
            # 检查权限（管理员或本人）
            if str(current_user.id) != str(user_id):
                if not await self._check_permission(current_user, "users", "read"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="没有权限查看该用户权限",
                    )
            
            # 获取用户权限
            permissions = await self.user_service.get_user_permissions(user_id)
            
            return permissions
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取用户权限失败"
            )
    
    async def _check_permission(
        self,
        user: User,
        resource: str,
        action: str
    ) -> bool:
        """检查用户权限"""
        try:
            return await self.user_service.check_user_permission(
                user_id=user.id,
                resource=resource,
                action=action
            )
        except Exception as e:
            logger.error(f"权限检查失败: {str(e)}")
            return False
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 回退到直接连接IP
        return request.client.host if request.client else "unknown"


# 依赖注入函数
async def get_user_handler(
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
) -> UserHandler:
    """获取用户处理器实例"""
    return UserHandler(auth_service, user_service, metrics_service)


# 路由端点定义
@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """获取当前用户信息"""
    return await handler.get_current_user_info(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    request: Request,
    user_data: UserUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """更新当前用户信息"""
    return await handler.update_current_user(request, user_data, current_user)


@router.get("", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="限制记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    role_filter: Optional[str] = Query(None, description="角色过滤"),
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """获取用户列表（需要管理员权限）"""
    return await handler.get_users(
        current_user, skip, limit, search, status_filter, role_filter
    )


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户信息")
async def get_user(
    user_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """根据ID获取用户信息"""
    return await handler.get_user_by_id(user_id, current_user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """创建新用户（需要管理员权限）"""
    return await handler.create_user(request, user_data, current_user)


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户信息")
async def update_user(
    request: Request,
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """更新用户信息"""
    return await handler.update_user(request, user_id, user_data, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户")
async def delete_user(
    request: Request,
    user_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """删除用户（需要管理员权限）"""
    return await handler.delete_user(request, user_id, current_user)


@router.get("/roles", response_model=List[RoleResponse], summary="获取角色列表")
async def get_roles(
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """获取角色列表"""
    return await handler.get_roles(current_user)


@router.get("/permissions", response_model=List[PermissionResponse], summary="获取权限列表")
async def get_permissions(
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """获取权限列表"""
    return await handler.get_permissions(current_user)


@router.post("/{user_id}/roles/{role_id}", summary="分配角色")
async def assign_role_to_user(
    request: Request,
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """为用户分配角色"""
    return await handler.assign_role_to_user(request, user_id, role_id, current_user)


@router.delete("/{user_id}/roles/{role_id}", summary="移除角色")
async def remove_role_from_user(
    request: Request,
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """从用户移除角色"""
    return await handler.remove_role_from_user(request, user_id, role_id, current_user)


@router.get("/{user_id}/permissions", response_model=List[str], summary="获取用户权限")
async def get_user_permissions(
    user_id: UUID,
    current_user: User = Depends(AuthService.get_current_user),
    handler: UserHandler = Depends(get_user_handler)
):
    """获取用户权限列表"""
    return await handler.get_user_permissions(user_id, current_user)