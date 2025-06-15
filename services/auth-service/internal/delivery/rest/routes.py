#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务REST API路由模块

定义认证服务提供的REST API端点和路由处理。
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ...schemas import (
    LoginResponse, RefreshRequest, RegisterRequest, ResetPasswordRequest,
    TokenResponse, MFASetupResponse, MFAVerifyRequest, VerifyTokenRequest,
    RoleResponse, PermissionResponse
)
from ...model.user import User, UserCreate, UserResponse, UserUpdate
from ...service import auth_service, permission_service, role_service, user_service
from ...service.auth_service import get_current_user

# 创建API路由
router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 身份验证路由
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录获取访问令牌"""
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await auth_service.create_tokens(user)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: RegisterRequest):
    """用户注册"""
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_data: RefreshRequest):
    """使用刷新令牌获取新的访问令牌"""
    try:
        tokens = await auth_service.refresh_tokens(refresh_data.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出，使当前令牌失效"""
    await auth_service.logout(current_user)
    return {"detail": "登出成功"}


@router.post("/verify", response_model=dict)
async def verify_token(verify_data: VerifyTokenRequest):
    """验证访问令牌有效性"""
    try:
        user_data = await auth_service.verify_token(verify_data.token)
        return {
            "valid": True,
            "user_id": str(user_data.id),
            "username": user_data.username,
            "permissions": user_data.permissions,
        }
    except Exception as e:
        return {"valid": False, "detail": str(e)}


@router.post("/reset-password-request")
async def request_password_reset(email: str):
    """请求密码重置，发送重置邮件"""
    try:
        await auth_service.send_password_reset(email)
        return {"detail": "如果邮箱存在，重置邮件已发送"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/reset-password")
async def reset_password(reset_data: ResetPasswordRequest):
    """重置密码"""
    try:
        await auth_service.reset_password(reset_data.token, reset_data.new_password)
        return {"detail": "密码重置成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# 多因素认证相关路由
@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(mfa_type: str, current_user: User = Depends(get_current_user)):
    """设置多因素认证"""
    try:
        setup_data = await auth_service.setup_mfa(current_user, mfa_type)
        return setup_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/mfa/verify")
async def verify_mfa(verify_data: MFAVerifyRequest, current_user: User = Depends(get_current_user)):
    """验证多因素认证代码"""
    try:
        result = await auth_service.verify_mfa(current_user, verify_data.code)
        if result:
            return {"detail": "多因素认证验证成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码无效",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/mfa/disable")
async def disable_mfa(current_user: User = Depends(get_current_user)):
    """禁用多因素认证"""
    try:
        await auth_service.disable_mfa(current_user)
        return {"detail": "多因素认证已禁用"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# 用户管理路由
@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新当前用户信息"""
    try:
        updated_user = await user_service.update_user(current_user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取用户列表（需要管理员权限）"""
    # 检查当前用户是否有管理用户的权限
    if not await permission_service.has_permission(current_user, "users", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问用户列表",
        )
    
    users = await user_service.get_users(skip, limit, search)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    """获取特定用户信息（需要权限或是自己）"""
    # 检查权限（是自己或有读取其他用户的权限）
    if str(current_user.id) != user_id and not await permission_service.has_permission(current_user, "users", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此用户信息",
        )
    
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """创建新用户（需要管理员权限）"""
    # 检查当前用户是否有创建用户的权限
    if not await permission_service.has_permission(current_user, "users", "create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建用户",
        )
    
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新用户信息（需要管理员权限或是自己）"""
    # 检查权限（是自己或有更新其他用户的权限）
    if str(current_user.id) != user_id and not await permission_service.has_permission(current_user, "users", "update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此用户",
        )
    
    try:
        updated_user = await user_service.update_user(user_id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    """删除用户（需要管理员权限）"""
    # 检查当前用户是否有删除用户的权限
    if not await permission_service.has_permission(current_user, "users", "delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除用户",
        )
    
    # 禁止删除自己
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户",
        )
    
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )


# 角色和权限管理路由
@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(current_user: User = Depends(get_current_user)):
    """获取所有角色（需要权限）"""
    if not await permission_service.has_permission(current_user, "roles", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看角色",
        )
    
    roles = await role_service.get_roles()
    return roles


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(current_user: User = Depends(get_current_user)):
    """获取所有权限（需要管理员权限）"""
    if not await permission_service.has_permission(current_user, "permissions", "read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看权限列表",
        )
    
    permissions = await permission_service.get_permissions()
    return permissions


@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(get_current_user)
):
    """为用户分配角色（需要管理员权限）"""
    if not await permission_service.has_permission(current_user, "roles", "assign"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限分配角色",
        )
    
    try:
        await role_service.assign_role_to_user(user_id, role_id)
        return {"detail": "角色分配成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/users/{user_id}/roles/{role_id}")
async def remove_role_from_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(get_current_user)
):
    """移除用户的角色（需要管理员权限）"""
    if not await permission_service.has_permission(current_user, "roles", "remove"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限移除角色",
        )
    
    try:
        await role_service.remove_role_from_user(user_id, role_id)
        return {"detail": "角色移除成功"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


def register_routes(app):
    """
    向FastAPI应用注册所有路由
    
    Args:
        app: FastAPI应用实例
    """
    app.include_router(router, prefix="/api/v1/auth") 