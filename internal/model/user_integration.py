"""
User Integration Models
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from sqlalchemy import Column, String, Boolean, JSON, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from pydantic import Field

from .base import BaseDBModel, BaseModel


class PlatformType(str, Enum):
    """支持的平台类型"""
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    XIAOMI = "xiaomi"
    HUAWEI = "huawei"
    WECHAT = "wechat"
    ALIPAY = "alipay"


class IntegrationStatus(str, Enum):
    """集成状态"""
    PENDING = "pending"      # 待授权
    ACTIVE = "active"        # 已激活
    EXPIRED = "expired"      # 已过期
    REVOKED = "revoked"      # 已撤销
    ERROR = "error"          # 错误状态


class UserIntegrationDB(BaseDBModel):
    """用户集成配置数据库模型"""
    __tablename__ = "user_integrations"
    
    user_id = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False)
    status = Column(String(20), default=IntegrationStatus.PENDING)
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

class UserIntegration(BaseModel):
    """用户集成配置"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    platform: PlatformType = Field(..., description="平台类型")
    status: IntegrationStatus = Field(default=IntegrationStatus.PENDING, description="集成状态")
    is_enabled: bool = Field(default=True, description="是否启用")
    
    platform_config: Dict[str, Any] = Field(default_factory=dict, description="平台配置")
    sync_enabled: bool = Field(default=True, description="是否启用同步")
    sync_frequency: str = Field(default="hourly", description="同步频率")
    last_sync_at: Optional[datetime] = Field(None, description="最后同步时间")
    
    permissions: list[str] = Field(default_factory=list, description="数据权限")
    last_error: Optional[str] = Field(None, description="最后错误信息")
    error_count: int = Field(default=0, description="错误次数")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PlatformAuth(BaseModel):
    """平台认证信息"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    platform: PlatformType = Field(..., description="平台类型")
    
    access_token: Optional[str] = Field(None, description="访问令牌")
    refresh_token: Optional[str] = Field(None, description="刷新令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
    
    platform_user_id: Optional[str] = Field(None, description="平台用户ID")
    platform_username: Optional[str] = Field(None, description="平台用户名")
    
    scopes: list[str] = Field(default_factory=list, description="授权范围")
    auth_data: Dict[str, Any] = Field(default_factory=dict, description="额外认证数据")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IntegrationRequest(BaseModel):
    """集成请求"""
    platform: PlatformType = Field(..., description="平台类型")
    permissions: list[str] = Field(default_factory=list, description="请求的权限")
    sync_frequency: str = Field(default="hourly", description="同步频率")
    platform_config: Dict[str, Any] = Field(default_factory=dict, description="平台配置")


class IntegrationResponse(BaseModel):
    """集成响应"""
    integration: UserIntegration
    auth_url: Optional[str] = Field(None, description="授权URL")
    message: str = Field(default="集成配置成功")


class AuthCallbackRequest(BaseModel):
    """认证回调请求"""
    platform: PlatformType = Field(..., description="平台类型")
    code: Optional[str] = Field(None, description="授权码")
    state: Optional[str] = Field(None, description="状态参数")
    error: Optional[str] = Field(None, description="错误信息")
    error_description: Optional[str] = Field(None, description="错误描述") 