#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证数据模式模块
定义认证相关的API请求和响应模型
"""
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, EmailStr, Field, validator
import re


class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期时间（秒）


class MFASetupResponse(BaseModel):
    """多因素认证设置响应模型"""
    mfa_type: str
    secret_key: str
    qr_code_url: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str
    mfa_code: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


class RegisterRequest(BaseModel):
    """注册请求模型"""
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    
    @validator('password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度必须至少为8个字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符')
        return v


class MFASetupRequest(BaseModel):
    """多因素认证设置请求模型"""
    mfa_type: str = Field(..., description="多因素认证类型: 'totp', 'sms', 或 'email'")
    verification_code: Optional[str] = Field(None, description="验证码，用于验证MFA设置")


class PasswordResetRequest(BaseModel):
    """密码重置请求模型"""
    email: EmailStr
    

class PasswordUpdateRequest(BaseModel):
    """密码更新请求模型"""
    token: str  # 重置令牌或当前密码
    new_password: str
    
    @validator('new_password')
    def password_strength(cls, v):
        """验证密码强度"""
        if len(v) < 8:
            raise ValueError('密码长度必须至少为8个字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('密码必须包含至少一个特殊字符')
        return v 