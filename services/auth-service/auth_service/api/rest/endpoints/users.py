"""用户管理相关API端点"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.auth import AuthService
from auth_service.core.database import get_db
from auth_service.repositories.user_repository import UserRepository
from auth_service.schemas.user import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    UserProfileUpdateRequest,
    ChangePasswordRequest,
    UserListRequest,
    UserListResponse,
    UserStatsResponse,
)

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户"""
    payload = auth_service.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )
    
    user_id = payload.get("sub")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """创建用户"""
    user_repo = UserRepository(db)
    
    # 检查用户名是否已存在
    existing_user = await user_repo.get_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    existing_email = await user_repo.get_by_email(request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 验证密码强度
    is_valid, message = auth_service.validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 创建用户
    password_hash = auth_service.get_password_hash(request.password)
    user = await user_repo.create_user(
        username=request.username,
        email=request.email,
        password_hash=password_hash,
        phone=request.phone
    )
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        status=user.status,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        metadata=user.metadata
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        status=current_user.status,
        is_verified=current_user.is_verified,
        is_superuser=current_user.is_superuser,
        mfa_enabled=current_user.mfa_enabled,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        metadata=current_user.metadata
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    user_repo = UserRepository(db)
    
    update_data = {}
    
    # 检查用户名
    if request.username and request.username != current_user.username:
        existing_user = await user_repo.get_by_username(request.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        update_data["username"] = request.username
    
    # 检查邮箱
    if request.email and request.email != current_user.email:
        existing_email = await user_repo.get_by_email(request.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        update_data["email"] = request.email
        update_data["is_verified"] = False  # 邮箱变更后需要重新验证
    
    # 更新手机号
    if request.phone is not None:
        update_data["phone"] = request.phone
    
    if update_data:
        user = await user_repo.update_user(current_user.id, **update_data)
    else:
        user = current_user
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        status=user.status,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        metadata=user.metadata
    )


@router.post("/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码"""
    # 验证当前密码
    if not auth_service.verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 验证新密码强度
    is_valid, message = auth_service.validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # 更新密码
    user_repo = UserRepository(db)
    new_password_hash = auth_service.get_password_hash(request.new_password)
    await user_repo.update_password(current_user.id, new_password_hash)
    
    return {"message": "密码修改成功"}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """根据ID获取用户信息（需要管理员权限）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        status=user.status,
        is_verified=user.is_verified,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        metadata=user.metadata
    )


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    size: int = 10,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表（需要管理员权限）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository(db)
    
    # 计算偏移量
    offset = (page - 1) * size
    
    # 获取用户列表
    users = await user_repo.list_users(
        offset=offset,
        limit=size,
        status=status
    )
    
    # 获取总数
    total = await user_repo.count_users(status=status)
    
    # 计算总页数
    pages = (total + size - 1) // size
    
    user_responses = [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            status=user.status,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            mfa_enabled=user.mfa_enabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at,
            login_count=user.login_count,
            metadata=user.metadata
        )
        for user in users
    ]
    
    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除用户（需要管理员权限）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository(db)
    success = await user_repo.delete_user(uuid.UUID(user_id))
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {"message": "用户删除成功"}


@router.get("/stats/overview", response_model=UserStatsResponse)
async def get_user_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息（需要管理员权限）"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user_repo = UserRepository(db)
    
    # 这里需要实现具体的统计逻辑
    # 暂时返回模拟数据
    return UserStatsResponse(
        total_users=await user_repo.count_users(),
        active_users=await user_repo.count_users(),
        verified_users=0,
        mfa_enabled_users=0,
        new_users_today=0,
        new_users_this_week=0,
        new_users_this_month=0
    ) 