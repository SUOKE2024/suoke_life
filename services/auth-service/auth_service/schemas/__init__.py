"""
__init__ - 索克生活项目模块
"""

from auth_service.schemas.auth import (
from auth_service.schemas.user import (

"""API数据传输对象模块"""

    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    MFASetupResponse,
    MFAVerifyRequest,
)
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
)

__all__ = [
    "LoginRequest",
    "LoginResponse", 
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "LogoutRequest",
    "MFASetupResponse",
    "MFAVerifyRequest",
    "UserCreateRequest",
    "UserResponse",
    "UserUpdateRequest",
    "ChangePasswordRequest",
] 