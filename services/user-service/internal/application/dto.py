"""
应用层数据传输对象(DTO)
定义API请求和响应的数据结构
"""
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, SecretStr, validator

from internal.domain.user import UserStatus, UserRole, Gender
from internal.model.user import ConstitutionType, HealthCondition

# 用户相关DTO
class CreateUserRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: SecretStr = Field(..., min_length=8)
    phone: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v

class UpdateUserRequest(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime] = None
    avatar_url: Optional[str] = None
    status: Optional[UserStatus] = None
    metadata: Optional[Dict[str, str]] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if v and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v

class UserResponse(BaseModel):
    """用户响应"""
    user_id: str
    username: str
    email: str
    phone: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[datetime] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    status: UserStatus
    roles: List[UserRole]
    metadata: Dict[str, str]
    preferences: Dict[str, str]
    agent_assignments: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserListResponse(BaseModel):
    """用户列表响应"""
    users: List[UserResponse]
    total: int
    offset: int
    limit: int

# 认证相关DTO
class LoginRequest(BaseModel):
    """登录请求"""
    email: EmailStr
    password: SecretStr
    device_id: Optional[str] = None
    device_info: Optional[Dict[str, str]] = None

class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: SecretStr
    new_password: SecretStr = Field(..., min_length=8)
    
    @validator('new_password')
    def password_strength(cls, v):
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError('密码长度不能少于8个字符')
        if not any(c.isupper() for c in password):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in password):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in password):
            raise ValueError('密码必须包含至少一个数字')
        return v

class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    email: EmailStr

class ConfirmResetPasswordRequest(BaseModel):
    """确认重置密码请求"""
    token: str
    new_password: SecretStr = Field(..., min_length=8)

# 健康数据相关DTO
class UpdateUserHealthRequest(BaseModel):
    """更新用户健康信息请求"""
    health_score: Optional[int] = Field(None, ge=0, le=100)
    dominant_constitution: Optional[ConstitutionType] = None
    constitution_scores: Optional[Dict[str, float]] = None
    height: Optional[float] = Field(None, gt=0, le=300)  # 身高(cm)
    weight: Optional[float] = Field(None, gt=0, le=500)  # 体重(kg)
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[HealthCondition]] = None
    medications: Optional[List[str]] = None
    
    @validator('constitution_scores')
    def validate_constitution_scores(cls, v):
        if v:
            for score in v.values():
                if not 0 <= score <= 100:
                    raise ValueError('体质评分必须在0-100之间')
        return v

class UserHealthSummaryResponse(BaseModel):
    """用户健康摘要响应"""
    user_id: str
    health_score: int
    dominant_constitution: Optional[ConstitutionType] = None
    constitution_scores: Dict[str, float]
    last_assessment_date: Optional[datetime] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    bmi: Optional[float] = None
    blood_type: Optional[str] = None
    allergies: List[str]
    chronic_conditions: List[HealthCondition]
    medications: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 设备相关DTO
class BindDeviceRequest(BaseModel):
    """绑定设备请求"""
    device_id: str
    device_type: str
    device_name: Optional[str] = None
    platform: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_token: Optional[str] = None
    device_metadata: Dict[str, str] = Field(default_factory=dict)

class BindDeviceResponse(BaseModel):
    """绑定设备响应"""
    success: bool
    binding_id: Optional[str] = None
    binding_time: Optional[datetime] = None
    device_id: str
    device_type: str
    message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DeviceInfoResponse(BaseModel):
    """设备信息响应"""
    device_id: str
    device_type: str
    device_name: Optional[str] = None
    binding_time: datetime
    binding_id: str
    is_active: bool
    last_active_time: datetime
    platform: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserDevicesResponse(BaseModel):
    """用户设备列表响应"""
    user_id: str
    devices: List[DeviceInfoResponse]
    total: int

# 角色和权限相关DTO
class UpdateUserRolesRequest(BaseModel):
    """更新用户角色请求"""
    roles: List[UserRole]

class UserPermissionsResponse(BaseModel):
    """用户权限响应"""
    user_id: str
    roles: List[UserRole]
    permissions: Set[str]

# 审计日志相关DTO
class AuditLogResponse(BaseModel):
    """审计日志响应"""
    log_id: str
    user_id: str
    action: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    target_user_id: Optional[str] = None
    changes: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    logs: List[AuditLogResponse]
    total: int
    offset: int
    limit: int

# 统计相关DTO
class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_users: int
    active_users: int
    inactive_users: int
    suspended_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    user_growth_rate: float  # 用户增长率

class UserActivitySummaryResponse(BaseModel):
    """用户活动摘要响应"""
    user_id: str
    login_count: int
    last_login: Optional[datetime] = None
    profile_updates: int
    device_bindings: int
    health_data_updates: int
    total_actions: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# 搜索相关DTO
class UserSearchRequest(BaseModel):
    """用户搜索请求"""
    query: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    last_login_after: Optional[datetime] = None
    last_login_before: Optional[datetime] = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$")

# 批量操作相关DTO
class BulkUpdateUsersRequest(BaseModel):
    """批量更新用户请求"""
    user_ids: List[str]
    updates: Dict[str, str]  # 要更新的字段和值

class BulkUpdateUsersResponse(BaseModel):
    """批量更新用户响应"""
    success_count: int
    failed_count: int
    failed_user_ids: List[str]
    errors: List[str]

# 导出相关DTO
class ExportUsersRequest(BaseModel):
    """导出用户请求"""
    format: str = Field(default="csv", regex="^(csv|json|xlsx)$")
    filters: Optional[UserSearchRequest] = None
    fields: Optional[List[str]] = None  # 要导出的字段

class ExportUsersResponse(BaseModel):
    """导出用户响应"""
    export_id: str
    status: str
    download_url: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 