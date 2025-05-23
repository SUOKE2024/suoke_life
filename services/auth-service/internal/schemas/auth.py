#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证服务响应模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
    认证令牌响应
    """
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    refresh_expires_in: int


class MFASetupResponse(BaseModel):
    """
    多因素认证设置响应
    """
    type: str
    secret: str
    qr_code: Optional[str] = None
    success: bool = True
    backup_codes: Optional[List[str]] = None


class RefreshRequest(BaseModel):
    """
    刷新令牌请求
    """
    refresh_token: str


class VerifyTokenRequest(BaseModel):
    """
    验证令牌请求
    """
    token: str


class RegisterRequest(BaseModel):
    """
    用户注册请求
    """
    username: str
    email: str
    password: str
    phone_number: Optional[str] = None
    profile_data: Dict[str, Any] = {}


class ResetPasswordRequest(BaseModel):
    """
    重置密码请求
    """
    token: str
    new_password: str


class MFAVerifyRequest(BaseModel):
    """
    多因素认证验证请求
    """
    code: str


class LoginResponse(BaseModel):
    """
    登录响应
    """
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: Dict[str, Any]


class RoleResponse(BaseModel):
    """
    角色响应
    """
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class PermissionResponse(BaseModel):
    """
    权限响应
    """
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None 