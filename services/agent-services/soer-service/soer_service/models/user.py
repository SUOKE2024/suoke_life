"""
用户相关模型（简化版）

注意：用户认证相关的模型已移至用户管理服务
这里只保留索儿智能体服务需要的基本数据结构
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ProfileUpdateRequest(BaseModel):
    """档案更新请求模型"""
    full_name: Optional[str] = Field(default=None, description="真实姓名")
    gender: Optional[str] = Field(default=None, description="性别")
    birth_date: Optional[datetime] = Field(default=None, description="出生日期")
    height: Optional[float] = Field(default=None, description="身高")
    weight: Optional[float] = Field(default=None, description="体重")
    health_goals: Optional[List[str]] = Field(default=None, description="健康目标")
    dietary_preferences: Optional[List[str]] = Field(default=None, description="饮食偏好")
    activity_level: Optional[str] = Field(default=None, description="活动水平")
    preferences: Optional[Dict[str, Any]] = Field(default=None, description="用户偏好")


class UserContext(BaseModel):
    """用户上下文模型（从认证服务获取的用户信息）"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    role: str = Field(..., description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")
    is_verified: bool = Field(default=False, description="是否已验证")
    is_superuser: bool = Field(default=False, description="是否超级用户")
    roles: List[str] = Field(default_factory=list, description="用户角色列表")
    permissions: List[str] = Field(default_factory=list, description="用户权限列表")
    profile: Optional[Dict[str, Any]] = Field(default=None, description="用户档案信息")