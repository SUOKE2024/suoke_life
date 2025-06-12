"""
users - 索克生活项目模块
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from user_service.auth import (
    get_current_active_user,
    get_current_superuser,
    get_current_user,
)
from user_service.database import get_db
from user_service.models.user import User, UserRole, UserStatus
from user_service.performance import performance_monitor, query_cache
from user_service.services.user_service import UserService

"""用户管理API端点"""


router = APIRouter()


# Pydantic 模型定义
class UserCreate(BaseModel):
    """创建用户请求模型"""

    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="用户元数据"
    )


class UserUpdate(BaseModel):
    """更新用户请求模型"""

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="用户名"
    )
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    status: Optional[UserStatus] = Field(None, description="用户状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="用户元数据")


class UserResponse(BaseModel):
    """用户响应模型"""

    user_id: str
    username: str
    email: str
    phone: Optional[str]
    full_name: Optional[str]
    status: UserStatus
    roles: List[UserRole]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    preferences: Dict[str, Any]


class DeviceBindRequest(BaseModel):
    """设备绑定请求模型"""

    device_id: str = Field(..., description="设备ID")
    device_type: str = Field(..., description="设备类型")
    device_name: Optional[str] = Field(None, description="设备名称")
    device_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="设备元数据"
    )


class DeviceResponse(BaseModel):
    """设备响应模型"""

    device_id: str
    device_type: str
    device_name: Optional[str]
    binding_id: str
    binding_time: datetime
    is_active: bool
    last_active_time: datetime
    device_metadata: Dict[str, Any]


class PreferencesUpdate(BaseModel):
    """用户偏好设置更新模型"""

    preferences: Dict[str, Any] = Field(..., description="用户偏好设置")


# 用户CRUD端点
@router.post(" / ", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@performance_monitor("create_user")
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),  # 只有管理员可以创建用户
):
    """创建新用户"""
    try:
        user_service = UserService(db)

        # 创建用户
        user = await user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            full_name=user_data.full_name,
            metadata=user_data.metadata,
        )

        return UserResponse(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=user.roles,
            created_at=user.created_at,
            updated_at=user.updated_at,
            metadata=user.metadata,
            preferences=user.preferences,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"创建用户失败: {str(e)}"
        )


@router.get(" / me", response_model=UserResponse)
@performance_monitor("get_current_user_profile")
@query_cache(ttl=300)  # 缓存5分钟
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(current_user["id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return UserResponse(
        user_id=str(user.user_id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        status=user.status,
        roles=user.roles,
        created_at=user.created_at,
        updated_at=user.updated_at,
        metadata=user.metadata,
        preferences=user.preferences,
    )


@router.get(" / {user_id}", response_model=UserResponse)
@performance_monitor("get_user_by_id")
@query_cache(ttl=600)  # 缓存10分钟
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """根据ID获取用户信息"""
    # 权限检查：只能查看自己的信息或管理员可以查看所有
    if current_user["id"] != user_id and not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此用户信息"
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return UserResponse(
        user_id=str(user.user_id),
        username=user.username,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        status=user.status,
        roles=user.roles,
        created_at=user.created_at,
        updated_at=user.updated_at,
        metadata=user.metadata,
        preferences=user.preferences,
    )


@router.put(" / me", response_model=UserResponse)
@performance_monitor("update_current_user")
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户信息"""
    try:
        user_service = UserService(db)

        # 准备更新数据
        update_data = {}
        if user_data.username is not None:
            update_data["username"] = user_data.username
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.phone is not None:
            update_data["phone"] = user_data.phone
        if user_data.full_name is not None:
            update_data["full_name"] = user_data.full_name
        if user_data.metadata is not None:
            update_data["metadata"] = user_data.metadata

        # 更新用户
        user = await user_service.update_user(current_user["id"], **update_data)

        return UserResponse(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=user.roles,
            created_at=user.created_at,
            updated_at=user.updated_at,
            metadata=user.metadata,
            preferences=user.preferences,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新用户信息失败: {str(e)}",
        )


@router.put(" / {user_id}", response_model=UserResponse)
@performance_monitor("update_user_by_id")
async def update_user_by_id(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superuser),  # 只有管理员可以更新其他用户
    db: AsyncSession = Depends(get_db),
):
    """更新指定用户信息（管理员功能）"""
    try:
        user_service = UserService(db)

        # 准备更新数据
        update_data = {}
        if user_data.username is not None:
            update_data["username"] = user_data.username
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.phone is not None:
            update_data["phone"] = user_data.phone
        if user_data.full_name is not None:
            update_data["full_name"] = user_data.full_name
        if user_data.status is not None:
            update_data["status"] = user_data.status
        if user_data.metadata is not None:
            update_data["metadata"] = user_data.metadata

        # 更新用户
        user = await user_service.update_user(user_id, **update_data)

        return UserResponse(
            user_id=str(user.user_id),
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            status=user.status,
            roles=user.roles,
            created_at=user.created_at,
            updated_at=user.updated_at,
            metadata=user.metadata,
            preferences=user.preferences,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新用户信息失败: {str(e)}",
        )


@router.delete(" / {user_id}")
@performance_monitor("delete_user")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),  # 只有管理员可以删除用户
    db: AsyncSession = Depends(get_db),
):
    """删除用户（管理员功能）"""
    try:
        user_service = UserService(db)
        success = await user_service.delete_user(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在"
            )

        return {"message": "用户删除成功", "user_id": user_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"删除用户失败: {str(e)}"
        )


# 用户偏好设置端点
@router.get(" / me / preferences")
@performance_monitor("get_user_preferences")
@query_cache(ttl=300)  # 缓存5分钟
async def get_user_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户偏好设置"""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(current_user["id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return {
        "user_id": str(user.user_id),
        "preferences": user.preferences,
        "updated_at": user.updated_at.isoformat(),
    }


@router.put(" / me / preferences")
@performance_monitor("update_user_preferences")
async def update_user_preferences(
    preferences_data: PreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """更新当前用户偏好设置"""
    try:
        user_service = UserService(db)
        user = await user_service.update_user_preferences(
            current_user["id"], preferences_data.preferences
        )

        return {
            "message": "偏好设置更新成功",
            "user_id": str(user.user_id),
            "preferences": user.preferences,
            "updated_at": user.updated_at.isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"更新偏好设置失败: {str(e)}",
        )


# 设备管理端点
@router.post(
    " / me / devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
@performance_monitor("bind_device")
async def bind_device(
    device_data: DeviceBindRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """绑定设备到当前用户"""
    try:
        user_service = UserService(db)
        binding_id = await user_service.bind_device(
            user_id=current_user["id"],
            device_id=device_data.device_id,
            device_type=device_data.device_type,
            device_name=device_data.device_name,
            device_metadata=device_data.device_metadata,
        )

        # 获取绑定的设备信息
        devices = await user_service.get_user_devices(current_user["id"])
        device = next((d for d in devices if d.binding_id == binding_id), None)

        if not device:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="设备绑定成功但无法获取设备信息",
            )

        return DeviceResponse(
            device_id=device.device_id,
            device_type=device.device_type,
            device_name=device.device_name,
            binding_id=device.binding_id,
            binding_time=device.binding_time,
            is_active=device.is_active,
            last_active_time=device.last_active_time,
            device_metadata=device.device_metadata,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"设备绑定失败: {str(e)}"
        )


@router.get(" / me / devices", response_model=List[DeviceResponse])
@performance_monitor("get_user_devices")
@query_cache(ttl=300)  # 缓存5分钟
async def get_user_devices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的设备列表"""
    try:
        user_service = UserService(db)
        devices = await user_service.get_user_devices(current_user["id"])

        return [
            DeviceResponse(
                device_id=device.device_id,
                device_type=device.device_type,
                device_name=device.device_name,
                binding_id=device.binding_id,
                binding_time=device.binding_time,
                is_active=device.is_active,
                last_active_time=device.last_active_time,
                device_metadata=device.device_metadata,
            )
            for device in devices
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取设备列表失败: {str(e)}",
        )


@router.delete(" / me / devices / {device_id}")
@performance_monitor("unbind_device")
async def unbind_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """解绑设备"""
    try:
        user_service = UserService(db)
        success = await user_service.unbind_device(current_user["id"], device_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="设备不存在或未绑定到当前用户",
            )

        return {
            "message": "设备解绑成功",
            "device_id": device_id,
            "user_id": current_user["id"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"设备解绑失败: {str(e)}"
        )


# 健康数据端点
@router.get(" / me / health - summary")
@performance_monitor("get_health_summary")
@query_cache(ttl=600)  # 缓存10分钟
async def get_health_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户健康摘要"""
    try:
        user_service = UserService(db)
        health_summary = await user_service.get_user_health_summary(current_user["id"])

        return {
            "user_id": str(health_summary.user_id),
            "health_score": health_summary.health_score,
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康摘要失败: {str(e)}",
        )


# 用户列表端点（管理员功能）
@router.get(" / ", response_model=List[UserResponse])
@performance_monitor("list_users")
@query_cache(ttl=300)  # 缓存5分钟
async def list_users(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    status_filter: Optional[UserStatus] = Query(None, description="按状态过滤"),
    current_user: User = Depends(get_current_superuser),  # 只有管理员可以查看用户列表
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（管理员功能）"""
    try:
        user_service = UserService(db)
        users = await user_service.list_users(
            skip=skip, limit=limit, status_filter=status_filter
        )

        return [
            UserResponse(
                user_id=str(user.user_id),
                username=user.username,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                status=user.status,
                roles=user.roles,
                created_at=user.created_at,
                updated_at=user.updated_at,
                metadata=user.metadata,
                preferences=user.preferences,
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}",
        )
