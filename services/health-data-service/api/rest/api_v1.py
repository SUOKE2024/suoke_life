#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务REST API v1规范
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class HealthDataTypeEnum(str, Enum):
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


class DeviceTypeEnum(str, Enum):
    """设备类型"""
    APPLE_HEALTH = "apple_health"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    XIAOMI = "xiaomi"
    TCM_DEVICE = "tcm_device"
    MANUAL_ENTRY = "manual_entry"
    OTHER = "other"


class MeasurementUnitEnum(str, Enum):
    """测量单位"""
    COUNT = "count"
    STEPS = "steps"
    BPM = "bpm"
    MMHG = "mmHg"
    MGDL = "mg/dL"
    MMOLL = "mmol/L"
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
    PERCENT = "percent"
    KG = "kg"
    LB = "lb"
    MINUTES = "minutes"
    HOURS = "hours"
    KCAL = "kcal"
    ML = "ml"
    G = "g"
    MG = "mg"
    RPM = "rpm"
    CUSTOM = "custom"


class TCMConstitutionTypeEnum(str, Enum):
    """中医体质类型"""
    BALANCED = "balanced"
    QI_DEFICIENCY = "qi_deficiency"
    YANG_DEFICIENCY = "yang_deficiency"
    YIN_DEFICIENCY = "yin_deficiency"
    PHLEGM_DAMPNESS = "phlegm_dampness"
    DAMPNESS_HEAT = "dampness_heat"
    BLOOD_STASIS = "blood_stasis"
    QI_DEPRESSION = "qi_depression"
    SPECIAL = "special"


class HealthDataRequest(BaseModel):
    """健康数据请求"""
    data_type: HealthDataTypeEnum
    timestamp: datetime
    device_type: DeviceTypeEnum
    device_id: Optional[str] = None
    value: Union[float, int, str, Dict]
    unit: MeasurementUnitEnum
    source: str = "api"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthDataResponse(BaseModel):
    """健康数据响应"""
    id: UUID4
    user_id: UUID4
    data_type: HealthDataTypeEnum
    timestamp: datetime
    device_type: DeviceTypeEnum
    device_id: Optional[str] = None
    value: Union[float, int, str, Dict]
    unit: MeasurementUnitEnum
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class HealthDataListResponse(BaseModel):
    """健康数据列表响应"""
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[HealthDataResponse]


class HealthDataStatisticsResponse(BaseModel):
    """健康数据统计响应"""
    average: float
    maximum: float
    minimum: float
    count: int
    start_time: datetime
    end_time: datetime
    data_type: str


class WearableDataProcessRequest(BaseModel):
    """可穿戴设备数据处理请求"""
    device_type: DeviceTypeEnum
    source: str = "api_import"
    # 注意：实际的设备数据会通过multipart/form-data上传


class WearableDataProcessResponse(BaseModel):
    """可穿戴设备数据处理响应"""
    device_type: str
    processed_items: int
    data_types: Dict[str, int]
    time_range: Dict[str, Optional[str]]


class TCMConstitutionRequest(BaseModel):
    """中医体质请求"""
    primary_type: TCMConstitutionTypeEnum
    secondary_types: List[TCMConstitutionTypeEnum] = []
    scores: Dict[str, float]
    analysis_basis: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_by: str


class TCMConstitutionResponse(BaseModel):
    """中医体质响应"""
    id: UUID4
    user_id: UUID4
    timestamp: datetime
    primary_type: TCMConstitutionTypeEnum
    secondary_types: List[TCMConstitutionTypeEnum] = []
    scores: Dict[str, float]
    analysis_basis: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


class HealthInsightResponse(BaseModel):
    """健康洞察响应"""
    id: UUID4
    user_id: UUID4
    timestamp: datetime
    insight_type: str
    data_type: HealthDataTypeEnum
    time_range: Dict[str, datetime]
    description: str
    details: Dict[str, Any]
    severity: Optional[str] = None
    relevance_score: float
    created_at: datetime


class HealthInsightListResponse(BaseModel):
    """健康洞察列表响应"""
    count: int
    results: List[HealthInsightResponse]


class HealthProfileResponse(BaseModel):
    """健康档案响应"""
    id: UUID4
    user_id: UUID4
    timestamp: datetime
    health_index: float
    metrics: Dict[str, float]
    tcm_constitution: Dict[str, Any]
    recent_trends: Dict[str, Any]
    notable_insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """错误响应"""
    detail: str
    code: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API路径和操作定义（这部分会被FastAPI自动生成，此处仅作为参考）
API_PATHS = {
    "/api/v1/health-data": {
        "get": "获取健康数据列表",
        "post": "创建健康数据"
    },
    "/api/v1/health-data/{id}": {
        "get": "获取单条健康数据",
        "put": "更新健康数据",
        "delete": "删除健康数据"
    },
    "/api/v1/health-data/statistics": {
        "get": "获取健康数据统计"
    },
    "/api/v1/health-data/batch": {
        "post": "批量创建健康数据"
    },
    "/api/v1/wearables/process": {
        "post": "处理可穿戴设备数据"
    },
    "/api/v1/tcm/constitution": {
        "get": "获取中医体质",
        "post": "创建中医体质评估"
    },
    "/api/v1/tcm/constitution/history": {
        "get": "获取中医体质历史"
    },
    "/api/v1/insights": {
        "get": "获取健康洞察"
    },
    "/api/v1/health-profile": {
        "get": "获取健康档案"
    }
} 