"""
health_data - 索克生活项目模块
"""

from .base import BaseRequest
from .base import BaseResponse
import datetime
from enum import Enum
from pydantic import Field
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""健康数据模型"""





class DataType(str, Enum):
    """数据类型枚举"""
    VITAL_SIGNS = "vital_signs"  # 生命体征
    BLOOD_TEST = "blood_test"    # 血液检测
    URINE_TEST = "urine_test"    # 尿液检测
    IMAGING = "imaging"          # 影像检查
    SYMPTOMS = "symptoms"        # 症状记录
    MEDICATION = "medication"    # 用药记录
    EXERCISE = "exercise"        # 运动数据
    SLEEP = "sleep"             # 睡眠数据
    DIET = "diet"               # 饮食记录
    MOOD = "mood"               # 情绪记录


class DataSource(str, Enum):
    """数据来源枚举"""
    MANUAL = "manual"           # 手动输入
    DEVICE = "device"           # 设备采集
    HOSPITAL = "hospital"       # 医院系统
    THIRD_PARTY = "third_party" # 第三方平台
    AI_ANALYSIS = "ai_analysis" # AI分析


class HealthData(Base):
    """健康数据表"""
    __tablename__ = 'health_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    data_type = Column(String(100), nullable=False, index=True)
    data_value = Column(Text)
    unit = Column(String(50))
    source = Column(String(100))
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VitalSigns(Base):
    """生命体征表"""
    __tablename__ = 'vital_signs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    heart_rate = Column(Float)
    blood_pressure_systolic = Column(Float)
    blood_pressure_diastolic = Column(Float)
    temperature = Column(Float)
    oxygen_saturation = Column(Float)
    respiratory_rate = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreateHealthDataRequest(BaseRequest):
    """创建健康数据请求"""

    user_id: int = Field(description = "用户ID")
    data_type: DataType = Field(description = "数据类型")
    data_source: DataSource = Field(description = "数据来源")
    raw_data: dict[str, Any] = Field(description = "原始数据")
    device_id: Optional[str] = Field(default = None, description = "设备ID")
    location: Optional[str] = Field(default = None, description = "采集位置")
    tags: list[str] = Field(default_factory = list, description = "标签")
    recorded_at: Optional[datetime] = Field(default = None, description = "记录时间")


class UpdateHealthDataRequest(BaseRequest):
    """更新健康数据请求"""

    processed_data: Optional[dict[str, Any]] = Field(default = None, description = "处理后数据")
    quality_score: Optional[float] = Field(default = None, ge = 0, le = 1, description = "数据质量评分")
    confidence_score: Optional[float] = Field(default = None, ge = 0, le = 1, description = "置信度评分")
    is_validated: Optional[bool] = Field(default = None, description = "是否已验证")
    is_anomaly: Optional[bool] = Field(default = None, description = "是否异常")
    tags: Optional[list[str]] = Field(default = None, description = "标签")


class HealthDataResponse(BaseResponse):
    """健康数据响应"""

    data: HealthData = Field(description = "健康数据")


class HealthDataListResponse(BaseResponse):
    """健康数据列表响应"""

    data: list[HealthData] = Field(description = "健康数据列表")
    total: int = Field(description = "总数量")


class CreateVitalSignsRequest(BaseRequest):
    """创建生命体征请求"""

    user_id: int = Field(description = "用户ID")
    heart_rate: Optional[int] = Field(default = None, ge = 30, le = 220, description = "心率(bpm)")
    blood_pressure_systolic: Optional[int] = Field(default = None, ge = 70, le = 250, description = "收缩压(mmHg)")
    blood_pressure_diastolic: Optional[int] = Field(default = None, ge = 40, le = 150, description = "舒张压(mmHg)")
    body_temperature: Optional[float] = Field(default = None, ge = 35.0, le = 42.0, description = "体温(°C)")
    respiratory_rate: Optional[int] = Field(default = None, ge = 8, le = 40, description = "呼吸频率(次 / 分)")
    oxygen_saturation: Optional[float] = Field(default = None, ge = 70.0, le = 100.0, description = "血氧饱和度(%)")
    weight: Optional[float] = Field(default = None, ge = 20.0, le = 300.0, description = "体重(kg)")
    height: Optional[float] = Field(default = None, ge = 100.0, le = 250.0, description = "身高(cm)")
    device_id: Optional[str] = Field(default = None, description = "设备ID")
    notes: Optional[str] = Field(default = None, description = "备注")
    recorded_at: Optional[datetime] = Field(default = None, description = "记录时间")


class VitalSignsResponse(BaseResponse):
    """生命体征响应"""

    data: VitalSigns = Field(description = "生命体征数据")


class DiagnosticData(Base):
    """诊断数据表"""
    __tablename__ = 'diagnostic_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    diagnosis_type = Column(String(100), nullable=False)
    diagnosis_result = Column(Text, nullable=False)
    confidence_score = Column(Float)
    raw_data = Column(JSON)
    processed_data = Column(JSON)
    doctor_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TCMSummary(Base):
    """中医诊断摘要表"""
    __tablename__ = 'tcm_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    mongo_id = Column(String(255))  # 对应MongoDB中的详细数据
    diagnosis_method = Column(String(50))  # 望、闻、问、切
    main_syndrome = Column(String(200))
    constitution_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class HealthTrendAnalysis(BaseModel):
    """健康趋势分析"""
    user_id: str
    data_type: str
    period_days: int
    data_points: int
    trend_direction: str
    change_percent: float
    mean_value: float
    median_value: float
    analysis: str


class HealthReport(BaseModel):
    """健康报告"""
    user_id: str
    generated_at: datetime
    vital_signs: Optional[VitalSignsResponse]
    recent_diagnostics: list[DiagnosticDataResponse]
    tcm_analysis: list[dict[str, Any]]
    health_score: float
    recommendations: list[str]
    risk_assessment: str


class DataQualityScore(BaseModel):
    """数据质量评分"""
    overall_score: float
    completeness_score: float
    accuracy_score: float
    timeliness_score: float
    consistency_score: float
    details: dict[str, Any]


class DiagnosticDataResponse(BaseModel):
    """诊断数据响应"""
    id: int
    user_id: str
    diagnosis_type: str
    diagnosis_result: str
    confidence_score: Optional[float]
    raw_data: Optional[dict[str, Any]]
    processed_data: Optional[dict[str, Any]]
    doctor_id: Optional[str]
    created_at: datetime
    updated_at: datetime
