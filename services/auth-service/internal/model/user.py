#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户模型模块

定义用户及相关实体的数据模型。
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserStatusEnum(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class MFATypeEnum(str, Enum):
    """多因素认证类型枚举"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class AuditActionEnum(str, Enum):
    """审计操作枚举"""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    MFA_SETUP = "mfa_setup"
    MFA_DISABLE = "mfa_disable"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


class Permission(BaseModel):
    """权限模型"""
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class Role(BaseModel):
    """角色模型"""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[Permission] = Field(default_factory=list)


class RefreshToken(BaseModel):
    """刷新令牌模型"""
    id: str
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime
    is_revoked: bool = False
    device_info: Optional[Dict[str, Any]] = None


class AuditLog(BaseModel):
    """审计日志模型"""
    id: str
    user_id: str
    action: AuditActionEnum
    resource: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    success: bool = True


class OAuthConnection(BaseModel):
    """OAuth连接模型"""
    id: str
    user_id: str
    provider: str  # google, wechat, alipay, etc.
    provider_user_id: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class MFASecret(BaseModel):
    """多因素认证密钥模型"""
    id: str
    user_id: str
    type: MFATypeEnum
    secret: str
    backup_codes: List[str] = Field(default_factory=list)
    is_verified: bool = False
    created_at: datetime


class User(BaseModel):
    """用户模型"""
    id: str
    username: str
    email: str
    password_hash: Optional[str] = None
    phone_number: Optional[str] = None
    status: UserStatusEnum = UserStatusEnum.ACTIVE
    roles: List[Role] = Field(default_factory=list)
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    mfa_enabled: bool = False
    mfa_secret: Optional[MFASecret] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    email_verified: bool = False
    phone_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @property
    def permissions(self) -> List[str]:
        """获取用户所有权限"""
        perms = []
        for role in self.roles:
            for perm in role.permissions:
                perm_str = f"{perm.resource}:{perm.action}"
                if perm_str not in perms:
                    perms.append(perm_str)
        return perms

    def has_permission(self, resource: str, action: str) -> bool:
        """检查用户是否有特定权限"""
        required_perm = f"{resource}:{action}"
        return required_perm in self.permissions

    def has_role(self, role_name: str) -> bool:
        """检查用户是否有特定角色"""
        return any(role.name == role_name for role in self.roles)


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    profile_data: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    status: Optional[UserStatusEnum] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    phone_number: Optional[str] = None
    status: UserStatusEnum
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    mfa_enabled: bool
    email_verified: bool
    phone_verified: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


# 修复Pydantic v2的模型重建
Role.model_rebuild() 