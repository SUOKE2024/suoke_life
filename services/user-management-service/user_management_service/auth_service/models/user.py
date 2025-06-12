"""
user - 索克生活项目模块
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from auth_service.models.base import BaseModel
from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

"""用户相关数据模型"""


class UserStatus(str, Enum):
    """用户状态枚举"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class Gender(str, Enum):
    """性别枚举"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class User(BaseModel):
    """用户模型"""

    __tablename__ = "users"

    # 基本信息
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="用户名"
    )

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, comment="邮箱"
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20), unique=True, index=True, comment="手机号"
    )

    # 密码相关
    password_hash: Mapped[str] = mapped_column(String(255), comment="密码哈希")

    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), comment="密码修改时间"
    )

    # 状态信息
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE, comment="用户状态"
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否已验证"
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否为超级用户"
    )

    # 登录信息
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), comment="最后登录时间"
    )

    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45), comment="最后登录IP"
    )

    login_count: Mapped[int] = mapped_column(default=0, comment="登录次数")

    # 安全信息
    failed_login_attempts: Mapped[int] = mapped_column(
        default=0, comment="失败登录尝试次数"
    )

    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), comment="锁定到期时间"
    )

    # MFA设置
    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否启用MFA"
    )

    mfa_secret: Mapped[Optional[str]] = mapped_column(String(32), comment="MFA密钥")

    # 元数据
    user_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, comment="用户元数据")

    # 关联关系
    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete - orphan",
    )

    sessions: Mapped[List["UserSession"]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete - orphan"
    )

    def is_locked(self) -> bool:
        """检查用户是否被锁定"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def is_active_user(self) -> bool:
        """检查用户是否为活跃状态"""
        return self.status == UserStatus.ACTIVE and not self.is_locked()

    class Meta:
        """TODO: 添加文档字符串"""

        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields = ['created_at']),
            # models.Index(fields = ['user_id']),
            # models.Index(fields = ['status']),
        ]
        # 数据库表选项
        db_table = "user"
        ordering = [" - created_at"]


class UserProfile(BaseModel):
    """用户档案模型"""

    __tablename__ = "user_profiles"

    # 关联用户
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, comment="用户ID"
    )

    # 个人信息
    first_name: Mapped[Optional[str]] = mapped_column(String(50), comment="名")

    last_name: Mapped[Optional[str]] = mapped_column(String(50), comment="姓")

    display_name: Mapped[Optional[str]] = mapped_column(String(100), comment="显示名称")

    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), comment="头像URL")

    bio: Mapped[Optional[str]] = mapped_column(Text, comment="个人简介")

    # 基本信息
    gender: Mapped[Optional[Gender]] = mapped_column(SQLEnum(Gender), comment="性别")

    birth_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), comment="出生日期"
    )

    location: Mapped[Optional[str]] = mapped_column(String(100), comment="所在地")

    timezone: Mapped[Optional[str]] = mapped_column(String(50), comment="时区")

    language: Mapped[Optional[str]] = mapped_column(
        String(10), default="zh - CN", comment="语言偏好"
    )

    # 联系信息
    website: Mapped[Optional[str]] = mapped_column(String(500), comment="个人网站")

    # 偏好设置
    preferences: Mapped[Optional[dict]] = mapped_column(JSONB, comment="用户偏好设置")

    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="profile")

    class Meta:
        """TODO: 添加文档字符串"""

        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields = ['created_at']),
            # models.Index(fields = ['user_id']),
            # models.Index(fields = ['status']),
        ]
        # 数据库表选项
        db_table = "usersession"
        ordering = [" - created_at"]


class UserSession(BaseModel):
    """用户会话模型"""

    __tablename__ = "user_sessions"

    # 关联用户
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, comment="用户ID"
    )

    # 会话信息
    session_token: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, comment="会话令牌"
    )

    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True, comment="刷新令牌"
    )

    # 设备信息
    device_id: Mapped[Optional[str]] = mapped_column(String(255), comment="设备ID")

    device_name: Mapped[Optional[str]] = mapped_column(String(100), comment="设备名称")

    user_agent: Mapped[Optional[str]] = mapped_column(Text, comment="用户代理")

    # 网络信息
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), comment="IP地址")

    location: Mapped[Optional[str]] = mapped_column(String(100), comment="登录位置")

    # 时间信息
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), comment="过期时间"
    )

    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="最后活动时间"
    )

    # 状态
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否活跃")

    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """检查会话是否有效"""
        return self.is_active and not self.is_expired()
