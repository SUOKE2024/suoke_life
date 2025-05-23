#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OAuth 模型

定义 OAuth 认证相关的模型
"""
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, EmailStr, validator


class OAuthProvider(str, Enum):
    """OAuth 提供商枚举"""
    GOOGLE = "google"
    FACEBOOK = "facebook"
    GITHUB = "github"
    WECHAT = "wechat"
    WEIBO = "weibo"
    APPLE = "apple"
    # 可根据需要添加更多提供商


class OAuthProviderConfig(BaseModel):
    """OAuth 提供商配置"""
    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scope: List[str]
    redirect_uri: str


class OAuthToken(BaseModel):
    """OAuth 令牌"""
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None


class OAuthUserInfo(BaseModel):
    """OAuth 用户信息"""
    provider: str
    provider_user_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class OAuthConnection(BaseModel):
    """OAuth 连接"""
    id: Optional[str] = None
    user_id: str
    provider: str
    provider_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
    user_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OAuthConnectionCreate(BaseModel):
    """创建 OAuth 连接"""
    user_id: str
    provider: str
    provider_user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
    user_data: Dict[str, Any] = Field(default_factory=dict)


class OAuthConnectionUpdate(BaseModel):
    """更新 OAuth 连接"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: Optional[List[str]] = None
    user_data: Optional[Dict[str, Any]] = None


class OAuthScope(str, Enum):
    """OAuth 授权范围枚举"""
    # 通用范围
    EMAIL = "email"
    PROFILE = "profile"
    
    # Google特定范围
    GOOGLE_DRIVE = "https://www.googleapis.com/auth/drive"
    GOOGLE_CALENDAR = "https://www.googleapis.com/auth/calendar"
    
    # GitHub特定范围
    GITHUB_REPO = "repo"
    GITHUB_USER = "user"
    
    # 微信特定范围
    WECHAT_USERINFO = "snsapi_userinfo"
    WECHAT_BASE = "snsapi_base"
    
    # 更多提供商特定范围可根据需要添加 