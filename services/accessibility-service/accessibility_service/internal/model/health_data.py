"""
Health Data Models
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from enum import Enum
from sqlalchemy import Column, String, Float, Integer, Date, JSON, Text, Index
from pydantic import Field, validator
from dataclasses import dataclass, field

from .base import BaseDBModel, BaseModel


class DataType(str, Enum):
    """健康数据类型"""
    ACTIVITY = "activity"           # 活动数据
    SLEEP = "sleep"                # 睡眠数据
    HEART_RATE = "heart_rate"      # 心率数据
    BLOOD_PRESSURE = "blood_pressure"  # 血压数据
    WEIGHT = "weight"              # 体重数据
    STEPS = "steps"                # 步数数据
    CALORIES = "calories"          # 卡路里数据
    DISTANCE = "distance"          # 距离数据
    EXERCISE = "exercise"          # 运动数据
    NUTRITION = "nutrition"        # 营养数据
    MOOD = "mood"                  # 情绪数据
    MEDICATION = "medication"      # 用药数据


class DataSource(str, Enum):
    """数据来源"""
    APPLE_HEALTH = "apple_health"
    GOOGLE_FIT = "google_fit"
    FITBIT = "fitbit"
    XIAOMI = "xiaomi"
    HUAWEI = "huawei"
    WECHAT = "wechat"
    ALIPAY = "alipay"
    MANUAL = "manual"              # 手动输入
    DEVICE = "device"
    APP = "app"
    SYNC = "sync"


class HealthDataDB(BaseDBModel):
    """健康数据数据库模型"""
    __tablename__ = "health_data"
    
    user_id = Column(String(100), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=False)
    
    # 时间信息
    record_date = Column(Date, nullable=False)
    record_time = Column(String(50), nullable=True)  # ISO格式时间戳
    
    # 数据值
    value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    
    # 扩展数据
    extra_metadata = Column(JSON, default={})
    raw_data = Column(JSON, default={})
    
    # 数据质量
    confidence = Column(Float, default=1.0)  # 数据置信度 0-1
    is_validated = Column(String(10), default="false")
    
    # 平台特定ID
    platform_id = Column(String(200), nullable=True)
    platform_updated_at = Column(String(50), nullable=True)
    
    # 索引
    __table_args__ = (
        Index('idx_user_type_date', 'user_id', 'data_type', 'record_date'),
        Index('idx_user_source_date', 'user_id', 'source', 'record_date'),
    )


class ActivityDataDB(BaseDBModel):
    """活动数据数据库模型"""
    __tablename__ = "activity_data"
    
    user_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    record_date = Column(Date, nullable=False)
    
    # 基础活动数据
    steps = Column(Integer, default=0)
    distance = Column(Float, default=0.0)  # 公里
    calories = Column(Float, default=0.0)  # 卡路里
    active_minutes = Column(Integer, default=0)  # 活跃分钟数
    
    # 详细活动数据
    floors_climbed = Column(Integer, default=0)  # 爬楼层数
    elevation_gain = Column(Float, default=0.0)  # 海拔增益(米)
    
    # 活动强度分布
    sedentary_minutes = Column(Integer, default=0)  # 久坐分钟
    light_minutes = Column(Integer, default=0)      # 轻度活动分钟
    moderate_minutes = Column(Integer, default=0)   # 中度活动分钟
    vigorous_minutes = Column(Integer, default=0)   # 剧烈活动分钟
    
    # 扩展数据
    extra_metadata = Column(JSON, default={})
    platform_id = Column(String(200), nullable=True)


class SleepDataDB(BaseDBModel):
    """睡眠数据数据库模型"""
    __tablename__ = "sleep_data"
    
    user_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    sleep_date = Column(Date, nullable=False)  # 睡眠日期
    
    # 睡眠时间
    bedtime = Column(String(50), nullable=True)      # 上床时间
    sleep_start = Column(String(50), nullable=True)  # 入睡时间
    sleep_end = Column(String(50), nullable=True)    # 醒来时间
    wake_time = Column(String(50), nullable=True)    # 起床时间
    
    # 睡眠时长(分钟)
    total_sleep_time = Column(Integer, default=0)    # 总睡眠时间
    deep_sleep_time = Column(Integer, default=0)     # 深睡时间
    light_sleep_time = Column(Integer, default=0)    # 浅睡时间
    rem_sleep_time = Column(Integer, default=0)      # REM睡眠时间
    awake_time = Column(Integer, default=0)          # 清醒时间
    
    # 睡眠质量
    sleep_efficiency = Column(Float, default=0.0)    # 睡眠效率 0-1
    sleep_score = Column(Float, default=0.0)         # 睡眠评分 0-100
    
    # 扩展数据
    extra_metadata = Column(JSON, default={})
    platform_id = Column(String(200), nullable=True)


class HeartRateDataDB(BaseDBModel):
    """心率数据数据库模型"""
    __tablename__ = "heart_rate_data"
    
    user_id = Column(String(100), nullable=False, index=True)
    source = Column(String(50), nullable=False)
    record_date = Column(Date, nullable=False)
    record_time = Column(String(50), nullable=False)
    
    # 心率数据
    heart_rate = Column(Integer, nullable=False)     # 心率值(bpm)
    heart_rate_type = Column(String(20), default="resting")  # resting, active, max
    
    # 心率变异性
    hrv = Column(Float, nullable=True)               # 心率变异性
    
    # 扩展数据
    extra_metadata = Column(JSON, default={})
    platform_id = Column(String(200), nullable=True)


# Pydantic Models

class HealthData(BaseModel):
    """健康数据"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    data_type: DataType = Field(..., description="数据类型")
    source: DataSource = Field(..., description="数据来源")
    
    record_date: date = Field(..., description="记录日期")
    record_time: Optional[datetime] = Field(None, description="记录时间")
    
    value: Optional[float] = Field(None, description="数据值")
    unit: Optional[str] = Field(None, description="单位")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="原始数据")
    
    confidence: float = Field(default=1.0, ge=0, le=1, description="数据置信度")
    is_validated: bool = Field(default=False, description="是否已验证")
    
    platform_id: Optional[str] = Field(None, description="平台ID")
    platform_updated_at: Optional[datetime] = Field(None, description="平台更新时间")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ActivityData(BaseModel):
    """活动数据"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    source: DataSource = Field(..., description="数据来源")
    record_date: date = Field(..., description="记录日期")
    
    steps: int = Field(default=0, ge=0, description="步数")
    distance: float = Field(default=0.0, ge=0, description="距离(公里)")
    calories: float = Field(default=0.0, ge=0, description="卡路里")
    active_minutes: int = Field(default=0, ge=0, description="活跃分钟数")
    
    floors_climbed: int = Field(default=0, ge=0, description="爬楼层数")
    elevation_gain: float = Field(default=0.0, description="海拔增益(米)")
    
    sedentary_minutes: int = Field(default=0, ge=0, description="久坐分钟")
    light_minutes: int = Field(default=0, ge=0, description="轻度活动分钟")
    moderate_minutes: int = Field(default=0, ge=0, description="中度活动分钟")
    vigorous_minutes: int = Field(default=0, ge=0, description="剧烈活动分钟")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    platform_id: Optional[str] = Field(None, description="平台ID")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SleepData(BaseModel):
    """睡眠数据"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    source: DataSource = Field(..., description="数据来源")
    sleep_date: date = Field(..., description="睡眠日期")
    
    bedtime: Optional[datetime] = Field(None, description="上床时间")
    sleep_start: Optional[datetime] = Field(None, description="入睡时间")
    sleep_end: Optional[datetime] = Field(None, description="醒来时间")
    wake_time: Optional[datetime] = Field(None, description="起床时间")
    
    total_sleep_time: int = Field(default=0, ge=0, description="总睡眠时间(分钟)")
    deep_sleep_time: int = Field(default=0, ge=0, description="深睡时间(分钟)")
    light_sleep_time: int = Field(default=0, ge=0, description="浅睡时间(分钟)")
    rem_sleep_time: int = Field(default=0, ge=0, description="REM睡眠时间(分钟)")
    awake_time: int = Field(default=0, ge=0, description="清醒时间(分钟)")
    
    sleep_efficiency: float = Field(default=0.0, ge=0, le=1, description="睡眠效率")
    sleep_score: float = Field(default=0.0, ge=0, le=100, description="睡眠评分")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    platform_id: Optional[str] = Field(None, description="平台ID")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HeartRateData(BaseModel):
    """心率数据"""
    id: Optional[int] = None
    user_id: str = Field(..., description="用户ID")
    source: DataSource = Field(..., description="数据来源")
    record_date: date = Field(..., description="记录日期")
    record_time: datetime = Field(..., description="记录时间")
    
    heart_rate: int = Field(..., ge=30, le=250, description="心率值(bpm)")
    heart_rate_type: str = Field(default="resting", description="心率类型")
    
    hrv: Optional[float] = Field(None, ge=0, description="心率变异性")
    
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    platform_id: Optional[str] = Field(None, description="平台ID")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HealthDataQuery(BaseModel):
    """健康数据查询参数"""
    data_types: Optional[List[DataType]] = Field(None, description="数据类型列表")
    sources: Optional[List[DataSource]] = Field(None, description="数据来源列表")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    limit: int = Field(default=100, ge=1, le=1000, description="返回数量限制")


class HealthDataSummary(BaseModel):
    """健康数据汇总"""
    user_id: str = Field(..., description="用户ID")
    date_range: str = Field(..., description="日期范围")
    
    total_records: int = Field(..., description="总记录数")
    data_types: List[str] = Field(..., description="数据类型列表")
    sources: List[str] = Field(..., description="数据来源列表")
    
    latest_sync: Optional[datetime] = Field(None, description="最新同步时间")
    data_quality_score: float = Field(..., ge=0, le=1, description="数据质量评分")


@dataclass
class HealthData(BaseDBModel):
    """基础健康数据模型"""
    user_id: str
    data_type: DataType
    value: float
    unit: str
    source: DataSource = DataSource.MANUAL
    
    # 时间信息
    recorded_at: datetime = field(default_factory=datetime.now)
    date: date = field(default_factory=date.today)
    
    # 设备信息
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    
    # 附加数据
    additional_data: Dict[str, Any] = field(default_factory=dict)
    
    # 数据质量
    confidence: float = 1.0  # 0.0 - 1.0
    is_validated: bool = False
    
    def validate_data(self):
        """验证数据"""
        self.is_validated = True
        self.update_timestamp()


@dataclass
class HeartRateData(BaseDBModel):
    """心率数据"""
    user_id: str
    heart_rate: int  # bpm
    recorded_at: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.DEVICE
    
    # 心率类型
    measurement_type: str = "resting"  # resting, active, max
    
    # 设备信息
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    
    # 上下文信息
    activity_context: Optional[str] = None
    stress_level: Optional[int] = None  # 1-10
    
    @property
    def is_normal(self) -> bool:
        """判断心率是否正常"""
        if self.measurement_type == "resting":
            return 60 <= self.heart_rate <= 100
        return True  # 其他类型需要更复杂的判断


@dataclass
class SleepData(BaseDBModel):
    """睡眠数据"""
    user_id: str
    sleep_date: date
    bedtime: datetime
    wake_time: datetime
    source: DataSource = DataSource.DEVICE
    
    # 睡眠阶段时长（分钟）
    deep_sleep_minutes: Optional[int] = None
    light_sleep_minutes: Optional[int] = None
    rem_sleep_minutes: Optional[int] = None
    awake_minutes: Optional[int] = None
    
    # 睡眠质量评分
    sleep_score: Optional[int] = None  # 0-100
    
    # 设备信息
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    
    @property
    def total_sleep_minutes(self) -> int:
        """总睡眠时间（分钟）"""
        return int((self.wake_time - self.bedtime).total_seconds() / 60)
    
    @property
    def sleep_efficiency(self) -> Optional[float]:
        """睡眠效率"""
        if not all([self.deep_sleep_minutes, self.light_sleep_minutes, self.rem_sleep_minutes]):
            return None
        
        actual_sleep = (self.deep_sleep_minutes + self.light_sleep_minutes + 
                       self.rem_sleep_minutes)
        return (actual_sleep / self.total_sleep_minutes) * 100


@dataclass
class ActivityData(BaseDBModel):
    """活动数据"""
    user_id: str
    activity_type: str
    start_time: datetime
    end_time: datetime
    source: DataSource = DataSource.DEVICE
    
    # 活动指标
    steps: Optional[int] = None
    distance_meters: Optional[float] = None
    calories_burned: Optional[float] = None
    duration_minutes: Optional[int] = None
    
    # 强度信息
    average_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    intensity_level: Optional[str] = None  # low, moderate, high
    
    # 设备信息
    device_id: Optional[str] = None
    device_name: Optional[str] = None
    
    # GPS数据
    gps_data: Optional[List[Dict[str, float]]] = field(default_factory=list)
    
    @property
    def duration_minutes_calculated(self) -> int:
        """计算活动持续时间"""
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    @property
    def average_pace(self) -> Optional[float]:
        """平均配速（分钟/公里）"""
        if not self.distance_meters or self.distance_meters == 0:
            return None
        
        duration_hours = self.duration_minutes_calculated / 60
        distance_km = self.distance_meters / 1000
        return duration_hours / distance_km * 60  # 分钟/公里 