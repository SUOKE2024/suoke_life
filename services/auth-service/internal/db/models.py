"""
SQLAlchemy ORM模型定义

定义认证服务的所有数据库表模型。
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, JSON, LargeBinary,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from internal.db import Base


class UserModel(Base):
    """用户表模型"""
    __tablename__ = "users"
    
    # 主键
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    
    # 基本信息
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    
    # 状态字段
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default="pending_verification"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # MFA相关
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 验证状态
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 安全字段
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 扩展数据
    profile_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 关系
    roles: Mapped[List["UserRoleModel"]] = relationship(
        "UserRoleModel", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[List["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    oauth_connections: Mapped[List["OAuthConnectionModel"]] = relationship(
        "OAuthConnectionModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    mfa_secrets: Mapped[List["MFASecretModel"]] = relationship(
        "MFASecretModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLogModel"]] = relationship(
        "AuditLogModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    biometric_credentials: Mapped[List["BiometricCredentialModel"]] = relationship(
        "BiometricCredentialModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # 索引
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_status", "status"),
        Index("idx_users_created_at", "created_at"),
        CheckConstraint(
            "status IN ('active', 'inactive', 'suspended', 'pending_verification')",
            name="ck_users_status"
        ),
    )


class RoleModel(Base):
    """角色表模型"""
    __tablename__ = "roles"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # 关系
    users: Mapped[List["UserRoleModel"]] = relationship(
        "UserRoleModel", 
        back_populates="role"
    )
    permissions: Mapped[List["RolePermissionModel"]] = relationship(
        "RolePermissionModel",
        back_populates="role",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_roles_name", "name"),
    )


class PermissionModel(Base):
    """权限表模型"""
    __tablename__ = "permissions"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    roles: Mapped[List["RolePermissionModel"]] = relationship(
        "RolePermissionModel",
        back_populates="permission"
    )
    
    __table_args__ = (
        Index("idx_permissions_resource_action", "resource", "action"),
        UniqueConstraint("resource", "action", name="uq_permissions_resource_action"),
    )


class UserRoleModel(Base):
    """用户角色关联表模型"""
    __tablename__ = "user_roles"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    role_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 时间戳
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    assigned_by: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="roles")
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="users")
    
    __table_args__ = (
        Index("idx_user_roles_user_id", "user_id"),
        Index("idx_user_roles_role_id", "role_id"),
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )


class RolePermissionModel(Base):
    """角色权限关联表模型"""
    __tablename__ = "role_permissions"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    role_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False
    )
    permission_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # 时间戳
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    role: Mapped["RoleModel"] = relationship("RoleModel", back_populates="permissions")
    permission: Mapped["PermissionModel"] = relationship("PermissionModel", back_populates="roles")
    
    __table_args__ = (
        Index("idx_role_permissions_role_id", "role_id"),
        Index("idx_role_permissions_permission_id", "permission_id"),
        UniqueConstraint("role_id", "permission_id", name="uq_role_permissions_role_permission"),
    )


class RefreshTokenModel(Base):
    """刷新令牌表模型"""
    __tablename__ = "refresh_tokens"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    device_info: Mapped[Optional[dict]] = mapped_column(JSONB)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="refresh_tokens")
    
    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token", "token"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )


class OAuthConnectionModel(Base):
    """OAuth连接表模型"""
    __tablename__ = "oauth_connections"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="oauth_connections")
    
    __table_args__ = (
        Index("idx_oauth_connections_user_id", "user_id"),
        Index("idx_oauth_connections_provider", "provider"),
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_connections_provider_user"),
    )


class MFASecretModel(Base):
    """MFA密钥表模型"""
    __tablename__ = "mfa_secrets"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    backup_codes: Mapped[Optional[list]] = mapped_column(JSONB)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="mfa_secrets")
    
    __table_args__ = (
        Index("idx_mfa_secrets_user_id", "user_id"),
        CheckConstraint(
            "type IN ('totp', 'sms', 'email', 'backup_codes')",
            name="ck_mfa_secrets_type"
        ),
    )


class BiometricCredentialModel(Base):
    """生物识别凭证表模型"""
    __tablename__ = "biometric_credentials"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    credential_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    device_type: Mapped[Optional[str]] = mapped_column(String(50))
    authenticator_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    attestation_object: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="biometric_credentials")
    
    __table_args__ = (
        Index("idx_biometric_credentials_user_id", "user_id"),
        Index("idx_biometric_credentials_credential_id", "credential_id"),
    )


class AuditLogModel(Base):
    """审计日志表模型"""
    __tablename__ = "audit_logs"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    resource: Mapped[Optional[str]] = mapped_column(String(100))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # 时间戳
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # 关系
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="audit_logs")
    
    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_ip_address", "ip_address"),
        CheckConstraint(
            """action IN ('login', 'logout', 'register', 'password_change', 
                         'password_reset', 'mfa_setup', 'mfa_disable', 
                         'role_assigned', 'role_removed', 'account_locked', 
                         'account_unlocked', 'social_login', 'social_unlink',
                         'biometric_register', 'biometric_auth', 'biometric_revoke')""",
            name="ck_audit_logs_action"
        ),
    ) 

# 导出别名，用于兼容性
BiometricCredential = BiometricCredentialModel
OAuthConnection = OAuthConnectionModel
User = UserModel
Role = RoleModel
Permission = PermissionModel
UserRole = UserRoleModel
RolePermission = RolePermissionModel
RefreshToken = RefreshTokenModel
MFASecret = MFASecretModel
AuditLog = AuditLogModel
