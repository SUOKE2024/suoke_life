#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户数据模型模块

定义认证服务使用的数据模型，包括用户、角色、权限等。
"""
import enum
import uuid
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any

import sqlalchemy as sa
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Table, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, declarative_base, relationship

# 创建基类
Base = declarative_base()

# 用户角色关联表（多对多）
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
)

# 角色权限关联表（多对多）
class RolePermission(Base):
    """角色权限关联模型"""
    __tablename__ = "role_permissions"
    
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class UserStatusEnum(str, enum.Enum):
    """用户状态枚举"""
    PENDING = "pending"       # 待验证
    ACTIVE = "active"         # 活跃
    DISABLED = "disabled"     # 已禁用
    LOCKED = "locked"         # 已锁定


class MFATypeEnum(str, enum.Enum):
    """多因素认证类型枚举"""
    NONE = "none"             # 无
    TOTP = "totp"             # 基于时间的一次性密码
    SMS = "sms"               # 短信验证码
    EMAIL = "email"           # 邮件验证码


class AuditActionEnum(str, enum.Enum):
    """审计操作类型枚举"""
    LOGIN = "login"                       # 登录
    LOGOUT = "logout"                     # 登出
    REGISTER = "register"                 # 注册
    PASSWORD_CHANGE = "password_change"   # 修改密码
    PASSWORD_RESET = "password_reset"     # 重置密码
    MFA_ENABLE = "mfa_enable"             # 启用多因素认证
    MFA_DISABLE = "mfa_disable"           # 禁用多因素认证
    PROFILE_UPDATE = "profile_update"     # 更新个人资料
    ROLE_ASSIGN = "role_assign"           # 分配角色
    ROLE_REVOKE = "role_revoke"           # 撤销角色
    USER_LOCK = "user_lock"               # 锁定用户
    USER_UNLOCK = "user_unlock"           # 解锁用户
    TOKEN_REVOKE = "token_revoke"         # 撤销令牌
    ACCESS_DENIED = "access_denied"       # 访问拒绝
    ADMIN_ACTION = "admin_action"         # 管理员操作
    MFA_SETUP = "mfa_setup"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True, index=True)
    
    status = Column(Enum(UserStatusEnum), nullable=False, default=UserStatusEnum.PENDING)
    
    profile_data = Column(JSONB, default={})
    
    # 多因素认证设置
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_type = Column(String(20), nullable=False, default=MFATypeEnum.NONE.value)
    mfa_secret = Column(String(100), nullable=True)
    
    # 时间记录
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(UTC))
    last_login = Column(DateTime, nullable=True)
    
    # 关系
    roles: Mapped[List["Role"]] = relationship(
        "Role", 
        secondary=user_roles, 
        lazy="joined",
        backref="users"
    )
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    oauth_connections = relationship("OAuthConnection", back_populates="user", cascade="all, delete-orphan")


class Role(Base):
    """角色模型"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(UTC))
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        viewonly=True
    )


class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # 资源和操作定义（如："users:read"，"users:write"）
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(UTC))
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RefreshToken(Base):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_value = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)
    client_id = Column(String(100), nullable=True)  # 用于记录客户端设备
    client_info = Column(JSONB, nullable=True)  # 客户端信息（如设备类型、IP等）
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    
    # 关系
    user = relationship("User", back_populates="refresh_tokens")


class LoginAttempt(Base):
    """登录尝试记录模型"""
    __tablename__ = "login_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(50), nullable=False)
    user_agent = Column(String(255), nullable=True)
    success = Column(Boolean, nullable=False, default=False)
    attempt_time = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    
    # 关系
    user = relationship("User", back_populates="login_attempts")


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditActionEnum), nullable=False)
    resource = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    
    # 关系
    user = relationship("User", back_populates="audit_logs")


class OAuthConnection(Base):
    """OAuth连接模型"""
    __tablename__ = "oauth_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # 例如: 'github', 'wechat', 'qq'
    provider_user_id = Column(String(100), nullable=False)
    access_token = Column(String(1000), nullable=False)
    refresh_token = Column(String(1000), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scopes = Column(JSONB, default=[])
    user_data = Column(JSONB, default={})
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, nullable=True, onupdate=lambda: datetime.now(UTC))
    
    # 关系
    user = relationship("User", back_populates="oauth_connections") 