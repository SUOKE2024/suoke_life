"""认证相关数据模型"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_service.models.base import BaseModel


class LoginResult(str, Enum):
    """登录结果枚举"""
    SUCCESS = "success"
    FAILED_INVALID_CREDENTIALS = "failed_invalid_credentials"
    FAILED_ACCOUNT_LOCKED = "failed_account_locked"
    FAILED_ACCOUNT_DISABLED = "failed_account_disabled"
    FAILED_MFA_REQUIRED = "failed_mfa_required"
    FAILED_MFA_INVALID = "failed_mfa_invalid"


class MFADeviceType(str, Enum):
    """MFA设备类型枚举"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class OAuthProvider(str, Enum):
    """OAuth提供商枚举"""
    GOOGLE = "google"
    WECHAT = "wechat"
    GITHUB = "github"
    APPLE = "apple"


class PermissionType(str, Enum):
    """权限类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class LoginAttempt(BaseModel):
    """登录尝试记录模型"""
    
    __tablename__ = "login_attempts"
    
    # 用户信息
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        comment="用户ID"
    )
    
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
        comment="用户名"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        index=True,
        comment="邮箱"
    )
    
    # 登录信息
    ip_address: Mapped[str] = mapped_column(
        String(45),
        index=True,
        comment="IP地址"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="用户代理"
    )
    
    # 结果信息
    result: Mapped[LoginResult] = mapped_column(
        SQLEnum(LoginResult),
        index=True,
        comment="登录结果"
    )
    
    failure_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="失败原因"
    )
    
    # 位置信息
    location: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="登录位置"
    )
    
    # 元数据
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="额外元数据"
    )


class MFADevice(BaseModel):
    """MFA设备模型"""
    
    __tablename__ = "mfa_devices"
    
    # 关联用户
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        comment="用户ID"
    )
    
    # 设备信息
    device_type: Mapped[MFADeviceType] = mapped_column(
        SQLEnum(MFADeviceType),
        comment="设备类型"
    )
    
    device_name: Mapped[str] = mapped_column(
        String(100),
        comment="设备名称"
    )
    
    # 密钥信息
    secret_key: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="密钥"
    )
    
    backup_codes: Mapped[Optional[List[str]]] = mapped_column(
        JSONB,
        comment="备用代码"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已验证"
    )
    
    # 使用统计
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="最后使用时间"
    )
    
    use_count: Mapped[int] = mapped_column(
        default=0,
        comment="使用次数"
    )
    
    # 元数据
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="设备元数据"
    )


class OAuthAccount(BaseModel):
    """OAuth账户模型"""
    
    __tablename__ = "oauth_accounts"
    
    # 关联用户
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        comment="用户ID"
    )
    
    # OAuth信息
    provider: Mapped[OAuthProvider] = mapped_column(
        SQLEnum(OAuthProvider),
        index=True,
        comment="OAuth提供商"
    )
    
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
        comment="提供商用户ID"
    )
    
    provider_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="提供商用户名"
    )
    
    provider_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="提供商邮箱"
    )
    
    # 令牌信息
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="访问令牌"
    )
    
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="刷新令牌"
    )
    
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="令牌过期时间"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    # 最后同步时间
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="最后同步时间"
    )
    
    # 元数据
    metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        comment="OAuth元数据"
    )


class RefreshToken(BaseModel):
    """刷新令牌模型"""
    
    __tablename__ = "refresh_tokens"
    
    # 关联用户
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        comment="用户ID"
    )
    
    # 令牌信息
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        comment="刷新令牌"
    )
    
    # 时间信息
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        comment="过期时间"
    )
    
    # 设备信息
    device_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="设备ID"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        comment="IP地址"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="用户代理"
    )
    
    # 状态信息
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已撤销"
    )
    
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="撤销时间"
    )
    
    # 使用信息
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        comment="最后使用时间"
    )
    
    use_count: Mapped[int] = mapped_column(
        default=0,
        comment="使用次数"
    )
    
    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """检查令牌是否有效"""
        return not self.is_revoked and not self.is_expired()


class UserRole(BaseModel):
    """用户角色模型"""
    
    __tablename__ = "user_roles"
    
    # 角色信息
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="角色名称"
    )
    
    display_name: Mapped[str] = mapped_column(
        String(100),
        comment="显示名称"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="角色描述"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否为系统角色"
    )
    
    # 权限关联
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )


class Permission(BaseModel):
    """权限模型"""
    
    __tablename__ = "permissions"
    
    # 权限信息
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        comment="权限名称"
    )
    
    resource: Mapped[str] = mapped_column(
        String(50),
        index=True,
        comment="资源名称"
    )
    
    action: Mapped[PermissionType] = mapped_column(
        SQLEnum(PermissionType),
        comment="操作类型"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="权限描述"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )
    
    # 角色关联
    roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        secondary="role_permissions",
        back_populates="permissions"
    )


# 角色权限关联表
from sqlalchemy import Table, Column, ForeignKey

role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("user_roles.id"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
) 