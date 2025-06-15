"""
用户相关模型

定义用户配置和访问权限的数据库模型。
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, JSON, Boolean, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserRole(PyEnum):
    """用户角色枚举"""
    PATIENT = "patient"
    DOCTOR = "doctor"
    RESEARCHER = "researcher"
    ADMIN = "admin"


class PermissionType(PyEnum):
    """权限类型枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SHARE = "share"
    ADMIN = "admin"


class UserProfile(Base):
    """用户配置文件"""

    __tablename__ = "user_profiles"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="用户配置ID"
    )

    # 用户基本信息
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        unique=True,
        nullable=False,
        comment="用户ID"
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="用户名"
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        comment="邮箱"
    )

    # 区块链相关
    wallet_address: Mapped[str | None] = mapped_column(
        String(42),  # 0x + 40 hex chars
        unique=True,
        comment="钱包地址"
    )

    public_key: Mapped[str | None] = mapped_column(
        Text,
        comment="公钥"
    )

    # 用户角色和权限
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.PATIENT,
        comment="用户角色"
    )

    permissions: Mapped[list[str] | None] = mapped_column(
        ARRAY(String),
        comment="权限列表"
    )

    # 隐私设置
    privacy_settings: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="隐私设置"
    )

    # 加密设置
    encryption_preferences: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="加密偏好"
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

    # 最后活动时间
    last_login_at: Mapped[datetime | None] = mapped_column(
        comment="最后登录时间"
    )

    last_activity_at: Mapped[datetime | None] = mapped_column(
        comment="最后活动时间"
    )

    # 元数据
    user_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="用户元数据"
    )


class AccessPermission(Base):
    """访问权限记录"""

    __tablename__ = "access_permissions"

    # 主键
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment="权限记录ID"
    )

    # 权限主体
    grantor_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="授权者ID"
    )

    grantee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="被授权者ID"
    )

    # 权限对象
    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="资源类型"
    )

    resource_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        comment="资源ID"
    )

    # 权限详情
    permission_type: Mapped[PermissionType] = mapped_column(
        Enum(PermissionType),
        nullable=False,
        comment="权限类型"
    )

    permissions: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        comment="具体权限列表"
    )

    # 权限条件
    conditions: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="权限条件"
    )

    # 时间限制
    valid_from: Mapped[datetime | None] = mapped_column(
        comment="生效时间"
    )

    valid_until: Mapped[datetime | None] = mapped_column(
        comment="失效时间"
    )

    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否激活"
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否已撤销"
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        comment="撤销时间"
    )

    revoked_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        comment="撤销者ID"
    )

    # 区块链记录
    blockchain_hash: Mapped[str | None] = mapped_column(
        String(66),
        comment="区块链哈希"
    )

    # 元数据
    permission_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        comment="权限元数据"
    )
