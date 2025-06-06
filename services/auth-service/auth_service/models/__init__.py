"""
__init__ - 索克生活项目模块
"""

from auth_service.models.auth import (
from auth_service.models.base import BaseModel
from auth_service.models.user import User, UserProfile, UserSession

"""数据模型"""

    LoginAttempt,
    MFADevice,
    OAuthAccount,
    RefreshToken,
    UserRole,
    Permission,
)

__all__ = [
    "BaseModel",
    "User",
    "UserProfile", 
    "UserSession",
    "LoginAttempt",
    "MFADevice",
    "OAuthAccount",
    "RefreshToken",
    "UserRole",
    "Permission",
] 