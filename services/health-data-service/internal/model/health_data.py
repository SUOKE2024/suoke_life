#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据模型
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


class HealthDataType(str, Enum):
    """健康数据类型"""
    STEPS = "steps"
    HEART_RATE = "heart_rate"
    SLEEP = "sleep"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_GLUCOSE = "blood_glucose"
    BODY_TEMPERATURE = "body_temperature"
    OXYGEN_SATURATION = "oxygen_saturation"
    RESPIRATORY_RATE = "respiratory_rate"
    BODY_MASS = "body_mass"
    BODY_FAT = "body_fat"
    ACTIVITY = "activity"
    WATER_INTAKE = "water_intake"
    NUTRITION = "nutrition"
    MEDICATION = "medication"
    SYMPTOM = "symptom"
    PULSE = "pulse"
    TONGUE = "tongue"
    FACE = "face"
    VOICE = "voice"
    CUSTOM = "custom"


class DeviceType(str, Enum):
    """设备类型"""
    APPLE_HEALTH = "apple_health"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    XIAOMI = "xiaomi"
    TCM_DEVICE = "tcm_device"
    MANUAL_ENTRY = "manual_entry"
    OTHER = "other"


class SleepStage(str, Enum):
    """睡眠阶段"""
    DEEP = "deep"
    LIGHT = "light"
    REM = "rem"
    AWAKE = "awake"
    UNKNOWN = "unknown"


class MeasurementUnit(str, Enum):
    """测量单位"""
    COUNT = "count"               # 计数
    STEPS = "steps"               # 步数
    BPM = "bpm"                   # 心率
    MMHG = "mmHg"                 # 血压
    MGDL = "mg/dL"                # 血糖
    MMOLL = "mmol/L"              # 血糖(国际单位)
    CELSIUS = "celsius"           # 温度
    FAHRENHEIT = "fahrenheit"     # 温度
    PERCENT = "percent"           # 百分比
    KG = "kg"                     # 体重
    LB = "lb"                     # 体重
    MINUTES = "minutes"           # 时间
    HOURS = "hours"               # 时间
    KCAL = "kcal"                 # 卡路里
    ML = "ml"                     # 毫升
    G = "g"                       # 克
    MG = "mg"                     # 毫克
    RPM = "rpm"                   # 呼吸率
    CUSTOM = "custom"             # 自定义


class HealthData(BaseModel):
    """健康数据基类"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    data_type: HealthDataType
    timestamp: datetime
    device_type: DeviceType
    device_id: Optional[str] = None
    value: Union[float, int, str, Dict]
    unit: MeasurementUnit
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class StepsData(HealthData):
    """步数数据"""
    data_type: HealthDataType = HealthDataType.STEPS
    value: int
    unit: MeasurementUnit = MeasurementUnit.STEPS
    
    @validator('value')
    def validate_steps(cls, v):
        if v < 0:
            raise ValueError('步数不能为负')
        return v


class HeartRateData(HealthData):
    """心率数据"""
    data_type: HealthDataType = HealthDataType.HEART_RATE
    value: int
    unit: MeasurementUnit = MeasurementUnit.BPM
    
    @validator('value')
    def validate_heart_rate(cls, v):
        if v < 20 or v > 250:
            raise ValueError('心率值超出正常范围(20-250)')
        return v


class BloodPressureData(HealthData):
    """血压数据"""
    data_type: HealthDataType = HealthDataType.BLOOD_PRESSURE
    value: Dict[str, float]  # {"systolic": 120, "diastolic": 80}
    unit: MeasurementUnit = MeasurementUnit.MMHG
    
    @validator('value')
    def validate_blood_pressure(cls, v):
        if 'systolic' not in v or 'diastolic' not in v:
            raise ValueError('血压数据必须包含收缩压和舒张压')
        if v['systolic'] < 50 or v['systolic'] > 250:
            raise ValueError('收缩压超出正常范围(50-250)')
        if v['diastolic'] < 30 or v['diastolic'] > 150:
            raise ValueError('舒张压超出正常范围(30-150)')
        return v


class BloodGlucoseData(HealthData):
    """血糖数据"""
    data_type: HealthDataType = HealthDataType.BLOOD_GLUCOSE
    value: float
    unit: MeasurementUnit  # mg/dL 或 mmol/L
    
    @validator('unit')
    def validate_unit(cls, v):
        if v not in [MeasurementUnit.MGDL, MeasurementUnit.MMOLL]:
            raise ValueError('血糖单位必须是 mg/dL 或 mmol/L')
        return v
    
    @validator('value')
    def validate_blood_glucose(cls, v, values):
        unit = values.get('unit')
        if unit == MeasurementUnit.MGDL:
            if v < 20 or v > 600:
                raise ValueError('血糖值(mg/dL)超出正常范围(20-600)')
        elif unit == MeasurementUnit.MMOLL:
            if v < 1.1 or v > 33.3:
                raise ValueError('血糖值(mmol/L)超出正常范围(1.1-33.3)')
        return v


class SleepData(HealthData):
    """睡眠数据"""
    data_type: HealthDataType = HealthDataType.SLEEP
    value: Dict[str, Any]  # {"duration": 480, "stages": {"deep": 120, "light": 240, "rem": 90, "awake": 30}}
    unit: MeasurementUnit = MeasurementUnit.MINUTES
    
    @validator('value')
    def validate_sleep(cls, v):
        if 'duration' not in v:
            raise ValueError('睡眠数据必须包含持续时间')
        if v['duration'] < 0 or v['duration'] > 1440:  # 不超过24小时
            raise ValueError('睡眠持续时间超出正常范围(0-1440分钟)')
        
        if 'stages' in v:
            stages = v['stages']
            for stage in stages:
                if stage not in [s.value for s in SleepStage]:
                    raise ValueError(f'无效的睡眠阶段: {stage}')
                if stages[stage] < 0:
                    raise ValueError(f'睡眠阶段时间不能为负: {stage}')
        
        return v


class BiometricData(HealthData):
    """生物指标数据"""
    data_type: HealthDataType  # pulse, tongue, face, voice
    value: Dict[str, Any]  # 原始特征和分析结果
    raw_data_url: Optional[str] = None  # 原始数据存储URL (如图像或语音文件)
    analysis_version: str  # 分析算法版本


class TCMConstitutionType(str, Enum):
    """中医体质类型"""
    BALANCED = "balanced"  # 平和质
    QI_DEFICIENCY = "qi_deficiency"  # 气虚质
    YANG_DEFICIENCY = "yang_deficiency"  # 阳虚质
    YIN_DEFICIENCY = "yin_deficiency"  # 阴虚质
    PHLEGM_DAMPNESS = "phlegm_dampness"  # 痰湿质
    DAMPNESS_HEAT = "dampness_heat"  # 湿热质
    BLOOD_STASIS = "blood_stasis"  # 血瘀质
    QI_DEPRESSION = "qi_depression"  # 气郁质
    SPECIAL = "special"  # 特禀质


class TCMConstitutionData(BaseModel):
    """中医体质数据"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    timestamp: datetime
    primary_type: TCMConstitutionType
    secondary_types: List[TCMConstitutionType] = []
    scores: Dict[str, float]  # 各体质的得分
    analysis_basis: Dict[str, Any]  # 分析依据
    recommendations: Dict[str, Any]  # 调理建议
    created_by: str  # 分析来源："ai", "tcm_doctor", "self_assessment"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class HealthInsight(BaseModel):
    """健康洞察"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    timestamp: datetime
    insight_type: str  # "trend", "anomaly", "correlation", "recommendation"
    data_type: HealthDataType
    time_range: Dict[str, datetime]  # {"start": timestamp, "end": timestamp}
    description: str
    details: Dict[str, Any]
    severity: Optional[str] = None  # "info", "warning", "alert"
    relevance_score: float  # 相关性/重要性分数
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class HealthProfile(BaseModel):
    """用户健康档案"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    timestamp: datetime
    health_index: float  # 综合健康指数
    metrics: Dict[str, float]  # 各项指标评分
    tcm_constitution: Dict[str, Any]  # 中医体质信息
    recent_trends: Dict[str, Any]  # 近期趋势
    notable_insights: List[Dict[str, Any]]  # 显著洞察
    recommendations: List[Dict[str, Any]]  # 健康建议
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True 