"""
user - 索克生活项目模块
"""

from auth_service.models.user import UserStatus, Gender
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Dict, Optional

"""用户相关的API数据传输对象"""





class UserCreateRequest(BaseModel):
    """用户创建请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, description="密码")
    phone: Optional[str] = Field(None, description="手机号")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v


class UserResponse(BaseModel):
    """用户响应"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号")
    status: UserStatus = Field(..., description="用户状态")
    is_verified: bool = Field(..., description="是否已验证")
    is_superuser: bool = Field(..., description="是否为超级用户")
    mfa_enabled: bool = Field(..., description="是否启用MFA")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    login_count: int = Field(..., description="登录次数")
    metadata: Optional[Dict] = Field(None, description="用户元数据")
    
    # 用户档案信息
    profile: Optional["UserProfileResponse"] = Field(None, description="用户档案")


class UserProfileResponse(BaseModel):
    """用户档案响应"""
    first_name: Optional[str] = Field(None, description="名")
    last_name: Optional[str] = Field(None, description="姓")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    gender: Optional[Gender] = Field(None, description="性别")
    birth_date: Optional[datetime] = Field(None, description="出生日期")
    location: Optional[str] = Field(None, description="所在地")
    timezone: Optional[str] = Field(None, description="时区")
    language: Optional[str] = Field(None, description="语言偏好")
    website: Optional[str] = Field(None, description="个人网站")


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, description="手机号")
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v


class UserProfileUpdateRequest(BaseModel):
    """用户档案更新请求"""
    first_name: Optional[str] = Field(None, max_length=50, description="名")
    last_name: Optional[str] = Field(None, max_length=50, description="姓")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    gender: Optional[Gender] = Field(None, description="性别")
    birth_date: Optional[datetime] = Field(None, description="出生日期")
    location: Optional[str] = Field(None, max_length=100, description="所在地")
    timezone: Optional[str] = Field(None, max_length=50, description="时区")
    language: Optional[str] = Field(None, max_length=10, description="语言偏好")
    website: Optional[str] = Field(None, description="个人网站")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")
    confirm_password: str = Field(..., description="确认新密码")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v


class UserListRequest(BaseModel):
    """用户列表请求"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    status: Optional[UserStatus] = Field(None, description="用户状态筛选")
    search: Optional[str] = Field(None, description="搜索关键词")


class UserListResponse(BaseModel):
    """用户列表响应"""
    users: list[UserResponse] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    verified_users: int = Field(..., description="已验证用户数")
    mfa_enabled_users: int = Field(..., description="启用MFA的用户数")
    new_users_today: int = Field(..., description="今日新增用户数")
    new_users_this_week: int = Field(..., description="本周新增用户数")
    new_users_this_month: int = Field(..., description="本月新增用户数")


# 更新UserResponse以包含profile
UserResponse.model_rebuild()