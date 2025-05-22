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