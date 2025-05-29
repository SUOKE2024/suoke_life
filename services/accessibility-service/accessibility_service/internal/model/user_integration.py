"""
User Integration Models
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field
from sqlalchemy import JSON, Boolean, Column, String, Text, UniqueConstraint

from .base import BaseDBModel, BaseModel


class PlatformType(Enum):
    """平台类型枚举"""
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    SAMSUNG_HEALTH = "samsung_health"
    XIAOMI_HEALTH = "xiaomi_health"
    HUAWEI_HEALTH = "huawei_health"


class AuthStatus(Enum):
    """认证状态枚举"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


class UserIntegrationDB(BaseDBModel):
    """用户集成配置数据库模型"""
    __tablename__ = "user_integrations"

    user_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    status = Column(String(20), default=AuthStatus.PENDING)
    is_enabled = Column(Boolean, default=True)

    # 平台特定配置
    platform_config = Column(JSON, default={})

    # 同步配置
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(20), default="hourly")  # hourly, daily, weekly
    last_sync_at = Column(String(50), nullable=True)

    # 数据权限
    permissions = Column(JSON, default=[])  # 允许同步的数据类型

    # 错误信息
    last_error = Column(Text, nullable=True)
    error_count = Column(String(10), default="0")

    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='uk_user_platform'),
    )


class PlatformAuthDB(BaseDBModel):
    """平台认证信息数据库模型"""
    __tablename__ = "platform_auths"

    user_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False)

    # OAuth 认证信息
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_type = Column(String(20), default="Bearer")
    expires_at = Column(String(50), nullable=True)

    # 平台用户信息
    platform_user_id = Column(String(200), nullable=True)
    platform_username = Column(String(200), nullable=True)

    # 授权范围
    scopes = Column(JSON, default=[])

    # 额外认证数据
    auth_data = Column(JSON, default={})

    # 唯一约束
    __table_args__ = (
        UniqueConstraint('user_id', 'platform', name='uk_user_platform_auth'),
    )


# Pydantic Models

@dataclass
class PlatformAuth(BaseDBModel):
    """平台认证信息"""
    user_id: str
    platform: PlatformType
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    status: AuthStatus = AuthStatus.ACTIVE

    # 权限范围
    scopes: list[str] = field(default_factory=list)

    # 平台特定配置
    platform_config: dict[str, Any] = field(default_factory=dict)

    def is_token_expired(self) -> bool:
        """检查token是否过期"""
        if not self.token_expires_at:
            return False
        return datetime.now() >= self.token_expires_at

    def refresh_access_token(self, new_token: str, expires_at: datetime | None = None):
        """刷新访问令牌"""
        self.access_token = new_token
        if expires_at:
            self.token_expires_at = expires_at
        self.status = AuthStatus.ACTIVE
        self.update_timestamp()


@dataclass
class UserIntegration(BaseDBModel):
    """用户集成配置"""
    user_id: str
    platform: PlatformType
    is_enabled: bool = True

    # 同步配置
    sync_frequency: str = "daily"  # hourly, daily, weekly
    auto_sync: bool = True
    sync_data_types: list[str] = field(default_factory=list)

    # 最后同步信息
    last_sync_at: datetime | None = None
    last_sync_status: str | None = None

    # 集成设置
    settings: dict[str, Any] = field(default_factory=dict)

    # 认证信息
    auth_info: PlatformAuth | None = None

    def update_last_sync(self, status: str, timestamp: datetime | None = None):
        """更新最后同步信息"""
        self.last_sync_status = status
        self.last_sync_at = timestamp or datetime.now()
        self.update_timestamp()

    def enable_integration(self):
        """启用集成"""
        self.is_enabled = True
        self.update_timestamp()

    def disable_integration(self):
        """禁用集成"""
        self.is_enabled = False
        self.update_timestamp()

    @property
    def is_auth_valid(self) -> bool:
        """检查认证是否有效"""
        if not self.auth_info:
            return False
        return (self.auth_info.status == AuthStatus.ACTIVE and
                not self.auth_info.is_token_expired())

    @property
    def platform_name(self) -> str:
        """获取平台显示名称"""
        platform_names = {
            PlatformType.APPLE_HEALTH: "Apple Health",
            PlatformType.GOOGLE_FIT: "Google Fit",
            PlatformType.FITBIT: "Fitbit",
            PlatformType.SAMSUNG_HEALTH: "Samsung Health",
            PlatformType.XIAOMI_HEALTH: "小米健康",
            PlatformType.HUAWEI_HEALTH: "华为健康"
        }
        return platform_names.get(self.platform, self.platform.value)


class PlatformAuth(BaseModel):
    """平台认证信息"""
    id: int | None = None
    user_id: str = Field(..., description="用户ID")
    platform: PlatformType = Field(..., description="平台类型")

    access_token: str | None = Field(None, description="访问令牌")
    refresh_token: str | None = Field(None, description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_at: datetime | None = Field(None, description="过期时间")

    platform_user_id: str | None = Field(None, description="平台用户ID")
    platform_username: str | None = Field(None, description="平台用户名")

    scopes: list[str] = Field(default_factory=list, description="授权范围")
    auth_data: dict[str, Any] = Field(default_factory=dict, description="额外认证数据")

    created_at: datetime | None = None
    updated_at: datetime | None = None


class IntegrationRequest(BaseModel):
    """集成请求"""
    platform: PlatformType = Field(..., description="平台类型")
    permissions: list[str] = Field(default_factory=list, description="请求的权限")
    sync_frequency: str = Field(default="hourly", description="同步频率")
    platform_config: dict[str, Any] = Field(default_factory=dict, description="平台配置")


class IntegrationResponse(BaseModel):
    """集成响应"""
    integration: UserIntegration
    auth_url: str | None = Field(None, description="授权URL")
    message: str = Field(default="集成配置成功")


class AuthCallbackRequest(BaseModel):
    """认证回调请求"""
    platform: PlatformType = Field(..., description="平台类型")
    code: str | None = Field(None, description="授权码")
    state: str | None = Field(None, description="状态参数")
    error: str | None = Field(None, description="错误信息")
    error_description: str | None = Field(None, description="错误描述")
