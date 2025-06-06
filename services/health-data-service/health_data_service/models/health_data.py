"""
health_data - 索克生活项目模块
"""

from .base import BaseEntity
from .base import BaseRequest
from .base import BaseResponse
from datetime import datetime
from enum import Enum
from pydantic import Field
from pydantic import field_validator
from typing import Any, Dict, List, Optional, Union

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


class HealthData(BaseEntity):
    """健康数据模型"""

    user_id: int = Field(description="用户ID")
    data_type: DataType = Field(description="数据类型")
    data_source: DataSource = Field(description="数据来源")

    # 数据内容
    raw_data: Dict[str, Any] = Field(description="原始数据")
    processed_data: Optional[Dict[str, Any]] = Field(default=None, description="处理后数据")

    # 元数据
    device_id: Optional[str] = Field(default=None, description="设备ID")
    location: Optional[str] = Field(default=None, description="采集位置")
    tags: List[str] = Field(default_factory=list, description="标签")

    # 质量评估
    quality_score: Optional[float] = Field(default=None, ge=0, le=1, description="数据质量评分")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="置信度评分")

    # 状态
    is_validated: bool = Field(default=False, description="是否已验证")
    is_anomaly: bool = Field(default=False, description="是否异常")

    # 时间信息
    recorded_at: datetime = Field(description="记录时间")

    @field_validator("quality_score", "confidence_score")
    @classmethod
    def validate_scores(cls, v: Optional[float]) -> Optional[float]:
        """验证评分范围"""
        if v is not None and not (0 <= v <= 1):
            raise ValueError("评分必须在0-1之间")
        return v


class VitalSigns(BaseEntity):
    """生命体征数据"""

    user_id: int = Field(description="用户ID")

    # 基础生命体征
    heart_rate: Optional[int] = Field(default=None, ge=30, le=220, description="心率(bpm)")
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=70, le=250, description="收缩压(mmHg)")
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=40, le=150, description="舒张压(mmHg)")
    body_temperature: Optional[float] = Field(default=None, ge=35.0, le=42.0, description="体温(°C)")
    respiratory_rate: Optional[int] = Field(default=None, ge=8, le=40, description="呼吸频率(次/分)")
    oxygen_saturation: Optional[float] = Field(default=None, ge=70.0, le=100.0, description="血氧饱和度(%)")

    # 身体指标
    weight: Optional[float] = Field(default=None, ge=20.0, le=300.0, description="体重(kg)")
    height: Optional[float] = Field(default=None, ge=100.0, le=250.0, description="身高(cm)")
    bmi: Optional[float] = Field(default=None, ge=10.0, le=50.0, description="BMI指数")

    # 记录信息
    recorded_at: datetime = Field(description="记录时间")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    notes: Optional[str] = Field(default=None, description="备注")


class CreateHealthDataRequest(BaseRequest):
    """创建健康数据请求"""

    user_id: int = Field(description="用户ID")
    data_type: DataType = Field(description="数据类型")
    data_source: DataSource = Field(description="数据来源")
    raw_data: Dict[str, Any] = Field(description="原始数据")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    location: Optional[str] = Field(default=None, description="采集位置")
    tags: List[str] = Field(default_factory=list, description="标签")
    recorded_at: Optional[datetime] = Field(default=None, description="记录时间")


class UpdateHealthDataRequest(BaseRequest):
    """更新健康数据请求"""

    processed_data: Optional[Dict[str, Any]] = Field(default=None, description="处理后数据")
    quality_score: Optional[float] = Field(default=None, ge=0, le=1, description="数据质量评分")
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="置信度评分")
    is_validated: Optional[bool] = Field(default=None, description="是否已验证")
    is_anomaly: Optional[bool] = Field(default=None, description="是否异常")
    tags: Optional[List[str]] = Field(default=None, description="标签")


class HealthDataResponse(BaseResponse):
    """健康数据响应"""

    data: HealthData = Field(description="健康数据")


class HealthDataListResponse(BaseResponse):
    """健康数据列表响应"""

    data: List[HealthData] = Field(description="健康数据列表")
    total: int = Field(description="总数量")


class CreateVitalSignsRequest(BaseRequest):
    """创建生命体征请求"""

    user_id: int = Field(description="用户ID")
    heart_rate: Optional[int] = Field(default=None, ge=30, le=220, description="心率(bpm)")
    blood_pressure_systolic: Optional[int] = Field(default=None, ge=70, le=250, description="收缩压(mmHg)")
    blood_pressure_diastolic: Optional[int] = Field(default=None, ge=40, le=150, description="舒张压(mmHg)")
    body_temperature: Optional[float] = Field(default=None, ge=35.0, le=42.0, description="体温(°C)")
    respiratory_rate: Optional[int] = Field(default=None, ge=8, le=40, description="呼吸频率(次/分)")
    oxygen_saturation: Optional[float] = Field(default=None, ge=70.0, le=100.0, description="血氧饱和度(%)")
    weight: Optional[float] = Field(default=None, ge=20.0, le=300.0, description="体重(kg)")
    height: Optional[float] = Field(default=None, ge=100.0, le=250.0, description="身高(cm)")
    device_id: Optional[str] = Field(default=None, description="设备ID")
    notes: Optional[str] = Field(default=None, description="备注")
    recorded_at: Optional[datetime] = Field(default=None, description="记录时间")


class VitalSignsResponse(BaseResponse):
    """生命体征响应"""

    data: VitalSigns = Field(description="生命体征数据")
