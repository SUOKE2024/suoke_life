"""
user - 索克生活项目模块
"""

from internal.model.user import (

"""
用户模型模块
从internal.model.user导入所有用户相关模型
"""

    # 枚举类型
    UserStatus,
    UserRole,
    ConstitutionType,
    Gender,
    BloodType,
    
    # 基础模型
    User,
    DeviceInfo,
    UserHealthSummary,
    UserAuditLog,
    HealthMetric,
    HealthCondition,
    Address,
    NotificationSettings,
    PrivacySettings,
    UserSettings,
    
    # 请求模型
    CreateUserRequest,
    UpdateUserRequest,
    UpdatePasswordRequest,
    UpdateUserSettingsRequest,
    UpdateUserPreferencesRequest,
    UpdateUserHealthRequest,
    BindDeviceRequest,
    VerifyUserRequest,
    
    # 响应模型
    UserResponse,
    BindDeviceResponse,
    UserDevicesResponse,
    VerifyUserResponse,
    UserHealthSummaryResponse,
)

__all__ = [
    # 枚举类型
    "UserStatus",
    "UserRole", 
    "ConstitutionType",
    "Gender",
    "BloodType",
    
    # 基础模型
    "User",
    "DeviceInfo",
    "UserHealthSummary",
    "UserAuditLog",
    "HealthMetric",
    "HealthCondition",
    "Address",
    "NotificationSettings",
    "PrivacySettings",
    "UserSettings",
    
    # 请求模型
    "CreateUserRequest",
    "UpdateUserRequest",
    "UpdatePasswordRequest",
    "UpdateUserSettingsRequest",
    "UpdateUserPreferencesRequest",
    "UpdateUserHealthRequest",
    "BindDeviceRequest",
    "VerifyUserRequest",
    
    # 响应模型
    "UserResponse",
    "BindDeviceResponse",
    "UserDevicesResponse",
    "VerifyUserResponse",
    "UserHealthSummaryResponse",
] 