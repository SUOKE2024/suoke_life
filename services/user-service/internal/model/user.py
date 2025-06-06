"""
user - 索克生活项目模块
"""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, SecretStr, EmailStr, field_validator, model_validator
from typing import Dict, List, Optional, Union, Set
from uuid import UUID

"""
用户相关的数据模型定义
"""



class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"  # 标记为已删除但保留数据


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"
    HEALTH_PROVIDER = "health_provider"
    RESEARCHER = "researcher"
    AGENT = "agent"  # AI代理角色


class ConstitutionType(str, Enum):
    """中医体质类型枚举"""
    BALANCED = "balanced"  # 平和质
    QI_DEFICIENCY = "qi_deficiency"  # 气虚质
    YANG_DEFICIENCY = "yang_deficiency"  # 阳虚质
    YIN_DEFICIENCY = "yin_deficiency"  # 阴虚质
    PHLEGM_DAMPNESS = "phlegm_dampness"  # 痰湿质
    DAMP_HEAT = "damp_heat"  # 湿热质
    BLOOD_STASIS = "blood_stasis"  # 血瘀质
    QI_DEPRESSION = "qi_depression"  # 气郁质
    SPECIAL = "special"  # 特禀质


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class BloodType(str, Enum):
    """血型枚举"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
    UNKNOWN = "unknown"


class HealthMetric(BaseModel):
    """健康指标模型"""
    metric_name: str
    value: float
    unit: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[str] = None  # 数据来源
    confidence: Optional[float] = None  # 置信度(0-1)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Address(BaseModel):
    """地址模型"""
    province: str
    city: str
    district: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    is_default: bool = False


class NotificationSettings(BaseModel):
    """通知设置"""
    enable_push: bool = True
    enable_email: bool = True
    enable_sms: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM格式
    quiet_hours_end: Optional[str] = None    # HH:MM格式
    topic_settings: Dict[str, bool] = Field(default_factory=dict)


class PrivacySettings(BaseModel):
    """隐私设置"""
    data_sharing_level: str = "anonymous"  # none, anonymous, restricted, full
    allow_research_use: bool = False
    show_profile: bool = True
    show_health_status: bool = False


class UserSettings(BaseModel):
    """用户设置"""
    notification: NotificationSettings = Field(default_factory=NotificationSettings)
    privacy: PrivacySettings = Field(default_factory=PrivacySettings)
    theme: str = "system"  # system, light, dark
    language: str = "zh_CN"
    font_size: str = "medium"  # small, medium, large
    high_contrast: bool = False
    reduce_motion: bool = False


class User(BaseModel):
    """用户模型"""
    user_id: UUID
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
    status: UserStatus = UserStatus.ACTIVE
    metadata: Dict[str, str] = Field(default_factory=dict)
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.USER])
    preferences: Dict[str, str] = Field(default_factory=dict)
    addresses: List[Address] = Field(default_factory=list)
    settings: UserSettings = Field(default_factory=UserSettings)
    agent_assignments: Dict[str, str] = Field(default_factory=dict)  # 用户分配的AI代理

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class DeviceInfo(BaseModel):
    """设备信息模型"""
    device_id: str
    device_type: str
    device_name: Optional[str] = None
    binding_time: datetime
    binding_id: str
    is_active: bool = True
    last_active_time: datetime
    device_metadata: Dict[str, str] = Field(default_factory=dict)
    platform: Optional[str] = None  # android, ios, web
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    push_token: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCondition(BaseModel):
    """健康状况"""
    condition_name: str
    condition_type: str  # chronic, acute, allergy, etc
    diagnosed_at: Optional[datetime] = None
    status: str = "active"  # active, resolved, managed
    severity: str = "medium"  # mild, medium, severe
    notes: Optional[str] = None


class UserHealthSummary(BaseModel):
    """用户健康摘要模型"""
    user_id: Union[UUID, str]
    health_score: int = Field(default=60, ge=0, le=100)
    dominant_constitution: Optional[ConstitutionType] = None
    constitution_scores: Dict[str, float] = Field(default_factory=dict)
    recent_metrics: List[HealthMetric] = Field(default_factory=list)
    last_assessment_date: Optional[datetime] = None
    height: Optional[float] = None  # 身高(cm)
    weight: Optional[float] = None  # 体重(kg)
    bmi: Optional[float] = None  # 体质指数
    blood_type: Optional[BloodType] = None  # 血型
    allergies: List[str] = Field(default_factory=list)  # 过敏物
    chronic_conditions: List[HealthCondition] = Field(default_factory=list)  # 慢性病情况
    medications: List[str] = Field(default_factory=list)  # 当前药物
    family_history: Dict[str, List[str]] = Field(default_factory=dict)  # 家族病史

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    
    @field_validator('constitution_scores')
    @classmethod
    def validate_constitution_scores(cls, v):
        """验证体质评分"""
        for constitution_type, score in v.items():
            # 检查体质类型是否有效
            if constitution_type not in [c.value for c in ConstitutionType]:
                raise ValueError(f"无效的体质类型: {constitution_type}")
            
            # 检查分数范围
            if not 0 <= score <= 100:
                raise ValueError(f"体质评分必须在0-100之间: {score}")
        
        return v
    
    @model_validator(mode='before')
    @classmethod
    def calculate_bmi(cls, values):
        """计算BMI"""
        if isinstance(values, dict):
            height = values.get('height')
            weight = values.get('weight')
            
            if height and weight and height > 0:
                # 身高单位是cm，需要转换为m
                height_in_meters = height / 100
                bmi = weight / (height_in_meters * height_in_meters)
                values['bmi'] = round(bmi, 2)
        
        return values


class UserAuditLog(BaseModel):
    """用户审计日志"""
    log_id: str
    user_id: Union[UUID, str]
    action: str  # create, update, login, etc
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    changes: Dict[str, Dict[str, str]] = Field(default_factory=dict)  # old_value, new_value
    metadata: Dict[str, str] = Field(default_factory=dict)


# 请求和响应模型
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
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
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
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if v is not None and not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v


class UpdatePasswordRequest(BaseModel):
    """更新密码请求"""
    current_password: SecretStr
    new_password: SecretStr = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def password_strength(cls, v):
        """检查密码强度"""
        password = v.get_secret_value()
        
        # 检查密码是否满足复杂性要求
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError('密码必须包含大写字母、小写字母、数字和特殊字符')
        
        return v


class UpdateUserSettingsRequest(BaseModel):
    """更新用户设置请求"""
    notification: Optional[NotificationSettings] = None
    privacy: Optional[PrivacySettings] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    font_size: Optional[str] = None
    high_contrast: Optional[bool] = None
    reduce_motion: Optional[bool] = None


class UpdateUserPreferencesRequest(BaseModel):
    """更新用户偏好设置请求"""
    preferences: Dict[str, str]


class UpdateUserHealthRequest(BaseModel):
    """更新用户健康信息请求"""
    health_score: Optional[int] = Field(None, ge=0, le=100)
    dominant_constitution: Optional[ConstitutionType] = None
    constitution_scores: Optional[Dict[str, float]] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    blood_type: Optional[BloodType] = None
    allergies: Optional[List[str]] = None
    chronic_conditions: Optional[List[HealthCondition]] = None
    medications: Optional[List[str]] = None
    
    @field_validator('constitution_scores')
    @classmethod
    def validate_constitution_scores(cls, v):
        if v is None:
            return v
            
        for constitution_type, score in v.items():
            # 检查体质类型是否有效
            if constitution_type not in [c.value for c in ConstitutionType]:
                raise ValueError(f"无效的体质类型: {constitution_type}")
            
            # 检查分数范围
            if not 0 <= score <= 100:
                raise ValueError(f"体质评分必须在0-100之间: {score}")
        
        return v


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


class UserDevicesResponse(BaseModel):
    """用户设备列表响应"""
    user_id: Union[UUID, str]
    devices: List[DeviceInfo]
    total: int


class UserResponse(BaseModel):
    """用户信息响应"""
    user_id: UUID
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
    metadata: Dict[str, str]
    roles: List[UserRole]
    preferences: Dict[str, str]
    settings: Optional[UserSettings] = None
    agent_assignments: Dict[str, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class VerifyUserRequest(BaseModel):
    """用户验证请求"""
    user_id: UUID
    token: Optional[str] = None
    permissions: Optional[List[str]] = None


class VerifyUserResponse(BaseModel):
    """用户验证响应"""
    is_valid: bool
    user_id: Optional[UUID] = None
    roles: List[UserRole] = Field(default_factory=list)
    permissions: Optional[Set[str]] = None


class UserHealthSummaryResponse(BaseModel):
    """用户健康摘要响应"""
    user_id: str
    health_score: int = Field(default=60, ge=0, le=100)
    dominant_constitution: Optional[ConstitutionType] = None
    constitution_scores: Dict[str, float] = Field(default_factory=dict)
    recent_metrics: List[HealthMetric] = Field(default_factory=list)
    last_assessment_date: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        } 