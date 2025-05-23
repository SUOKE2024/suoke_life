#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户模型模块

定义用户及相关实体的数据模型。
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Role(BaseModel):
    """角色模型"""
    id: str
    name: str
    description: Optional[str] = None
    permissions: List["Permission"] = []


class Permission(BaseModel):
    """权限模型"""
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class User(BaseModel):
    """用户模型"""
    id: str
    username: str
    email: str
    roles: List[Role] = []
    profile_data: Dict[str, Any] = {}
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    profile_data: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    profile_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    email: str
    phone_number: Optional[str] = None
    profile_data: Dict[str, Any] = {}
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    roles: List[str] = []


Role.update_forward_refs() 