"""
auth - 索克生活项目模块
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

"""认证相关的API数据传输对象"""




class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    device_id: Optional[str] = Field(None, description="设备ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    remember_me: bool = Field(False, description="记住我")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    mfa_required: bool = Field(False, description="是否需要MFA验证")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenResponse(BaseModel):
    """刷新令牌响应"""
    access_token: str = Field(..., description="新的访问令牌")
    refresh_token: str = Field(..., description="新的刷新令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")


class LogoutRequest(BaseModel):
    """登出请求"""
    all_devices: bool = Field(False, description="是否登出所有设备")


class MFASetupResponse(BaseModel):
    """MFA设置响应"""
    secret: str = Field(..., description="MFA密钥")
    qr_code_url: str = Field(..., description="二维码URL")
    backup_codes: list[str] = Field(..., description="备用代码")


class MFAVerifyRequest(BaseModel):
    """MFA验证请求"""
    token: str = Field(..., description="MFA令牌")
    backup_code: Optional[str] = Field(None, description="备用代码")


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class PasswordResetConfirmRequest(BaseModel):
    """密码重置确认请求"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class EmailVerificationConfirmRequest(BaseModel):
    """邮箱验证确认请求"""
    token: str = Field(..., description="验证令牌")


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str = Field(..., description="会话ID")
    device_name: Optional[str] = Field(None, description="设备名称")
    ip_address: Optional[str] = Field(None, description="IP地址")
    location: Optional[str] = Field(None, description="位置")
    created_at: datetime = Field(..., description="创建时间")
    last_activity_at: datetime = Field(..., description="最后活动时间")
    is_current: bool = Field(..., description="是否为当前会话")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: list[SessionInfo] = Field(..., description="会话列表")
    total: int = Field(..., description="总数") 