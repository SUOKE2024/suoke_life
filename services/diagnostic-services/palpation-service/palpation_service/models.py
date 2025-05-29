"""
数据模型定义
定义触诊服务的所有数据模型和Pydantic模式
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


# 枚举类型定义
class SessionStatus(str, Enum):
    """触诊会话状态"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class SessionType(str, Enum):
    """触诊会话类型"""

    STANDARD = "standard"
    QUICK = "quick"
    DETAILED = "detailed"
    RESEARCH = "research"


class SensorType(str, Enum):
    """传感器类型"""

    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    TEXTURE = "texture"
    VIBRATION = "vibration"
    HUMIDITY = "humidity"
    CONDUCTIVITY = "conductivity"


class AnalysisType(str, Enum):
    """分析类型"""

    PRESSURE_ANALYSIS = "pressure_analysis"
    TEMPERATURE_ANALYSIS = "temperature_analysis"
    TEXTURE_ANALYSIS = "texture_analysis"
    MULTIMODAL_FUSION = "multimodal_fusion"
    HEALTH_ASSESSMENT = "health_assessment"


class Gender(str, Enum):
    """性别"""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# SQLAlchemy数据库模型
class PalpationSession(Base):
    """触诊会话表"""

    __tablename__ = "palpation_sessions"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    session_type = Column(String(50), nullable=False, default=SessionType.STANDARD)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default=SessionStatus.ACTIVE, index=True)
    session_metadata = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SensorData(Base):
    """传感器数据表"""

    __tablename__ = "sensor_data"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    raw_data = Column(JSONB, nullable=False)
    processed_data = Column(JSONB, nullable=True)
    quality_score = Column(Float, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AnalysisResult(Base):
    """分析结果表"""

    __tablename__ = "analysis_results"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False, index=True)
    algorithm_version = Column(String(20), nullable=False)
    confidence_score = Column(Float, nullable=True, index=True)
    results = Column(JSONB, nullable=False)
    recommendations = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    """用户配置表"""

    __tablename__ = "user_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    medical_history = Column(JSONB, default={})
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ModelConfig(Base):
    """模型配置表"""

    __tablename__ = "model_configs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(20), nullable=False)
    config_data = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Pydantic模型（API模式）
class SensorDataPoint(BaseModel):
    """传感器数据点"""

    timestamp: datetime
    value: float
    unit: str
    metadata: dict[str, Any] | None = {}


class SensorDataInput(BaseModel):
    """传感器数据输入"""

    sensor_type: SensorType
    data_points: list[SensorDataPoint]
    quality_indicators: dict[str, float] | None = {}

    @field_validator("data_points")
    @classmethod
    def validate_data_points(cls, v):
        if not v:
            raise ValueError("数据点不能为空")
        if len(v) > 10000:
            raise ValueError("数据点数量不能超过10000")
        return v


class SessionCreateRequest(BaseModel):
    """创建会话请求"""

    user_id: str = Field(..., min_length=1, max_length=255)
    session_type: SessionType = SessionType.STANDARD
    metadata: dict[str, Any] | None = {}

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if not v.strip():
            raise ValueError("用户ID不能为空")
        return v.strip()


class SessionResponse(BaseModel):
    """会话响应"""

    id: UUID
    user_id: str
    session_type: SessionType
    status: SessionStatus
    start_time: datetime
    end_time: datetime | None = None
    metadata: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """分析请求"""

    session_id: UUID
    analysis_types: list[AnalysisType]
    parameters: dict[str, Any] | None = {}

    @field_validator("analysis_types")
    @classmethod
    def validate_analysis_types(cls, v):
        if not v:
            raise ValueError("分析类型不能为空")
        return v


class AnalysisResponse(BaseModel):
    """分析响应"""

    id: UUID
    session_id: UUID
    analysis_type: AnalysisType
    algorithm_version: str
    confidence_score: float | None = None
    results: dict[str, Any]
    recommendations: dict[str, Any] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthAssessment(BaseModel):
    """健康评估结果"""

    overall_score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    key_findings: list[str] = []
    recommendations: list[str] = []
    confidence: float = Field(..., ge=0, le=1)
    timestamp: datetime

    @field_validator("overall_score")
    @classmethod
    def validate_score(cls, v):
        return round(v, 2)


class MultimodalFusionResult(BaseModel):
    """多模态融合结果"""

    fusion_algorithm: str
    modality_weights: dict[str, float]
    fused_features: dict[str, Any]
    quality_metrics: dict[str, float]
    health_assessment: HealthAssessment

    @field_validator("modality_weights")
    @classmethod
    def validate_weights(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError("模态权重总和必须为1.0")
        return v


class UserProfileCreate(BaseModel):
    """创建用户配置"""

    user_id: str = Field(..., min_length=1, max_length=255)
    age: int | None = Field(None, ge=0, le=150)
    gender: Gender | None = None
    medical_history: dict[str, Any] | None = {}
    preferences: dict[str, Any] | None = {}


class UserProfileResponse(BaseModel):
    """用户配置响应"""

    id: UUID
    user_id: str
    age: int | None = None
    gender: Gender | None = None
    medical_history: dict[str, Any] = {}
    preferences: dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelConfigResponse(BaseModel):
    """模型配置响应"""

    id: UUID
    model_name: str
    model_version: str
    config_data: dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class HealthMetrics(BaseModel):
    """健康指标"""

    pulse_characteristics: dict[str, float] | None = {}
    temperature_patterns: dict[str, float] | None = {}
    texture_analysis: dict[str, float] | None = {}
    pressure_distribution: dict[str, float] | None = {}

    def get_summary_score(self) -> float:
        """计算综合评分"""
        scores = []
        for metrics in [
            self.pulse_characteristics,
            self.temperature_patterns,
            self.texture_analysis,
            self.pressure_distribution,
        ]:
            if metrics and "score" in metrics:
                scores.append(metrics["score"])

        return sum(scores) / len(scores) if scores else 0.0


class ErrorResponse(BaseModel):
    """错误响应"""

    error_code: str
    error_message: str
    details: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """成功响应"""

    message: str
    data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


# 分页模型
class PaginationParams(BaseModel):
    """分页参数"""

    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """分页响应"""

    items: list[Any]
    total: int
    page: int
    size: int
    pages: int

    @field_validator("pages", mode="before")
    @classmethod
    def calculate_pages(cls, v, info):
        values = info.data if hasattr(info, "data") else {}
        total = values.get("total", 0)
        size = values.get("size", 20)
        return (total + size - 1) // size if total > 0 else 0
