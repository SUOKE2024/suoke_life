#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户数据模型模块

定义认证服务使用的数据模型，包括用户、角色、权限等。
"""
import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")


class UserStatusEnum(enum.Enum):
    """用户状态枚举"""
    PENDING = "pending"       # 待验证
    ACTIVE = "active"         # 活跃
    DISABLED = "disabled"     # 已禁用
    LOCKED = "locked"         # 已锁定


class MFATypeEnum(enum.Enum):
    """多因素认证类型枚举"""
    NONE = "none"             # 无
    TOTP = "totp"             # 基于时间的一次性密码
    SMS = "sms"               # 短信验证码
    EMAIL = "email"           # 邮件验证码


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    
    status = Column(Enum(UserStatusEnum), nullable=False, default=UserStatusEnum.PENDING)
    
    profile_data = Column(Text, nullable=True)  # 存储用户额外资料（JSON字符串）
    
    # 多因素认证设置
    mfa_enabled = Column(Boolean, nullable=False, default=False)
    mfa_type = Column(Enum(MFATypeEnum), nullable=False, default=MFATypeEnum.NONE)
    mfa_secret = Column(String(100), nullable=True)
    
    # 时间记录
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
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


class Role(Base):
    """角色模型"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
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
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class RefreshToken(Base):
    """刷新令牌模型"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
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
    attempt_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="login_attempts")


class AuditLog(Base):
    """审计日志模型"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="audit_logs") 