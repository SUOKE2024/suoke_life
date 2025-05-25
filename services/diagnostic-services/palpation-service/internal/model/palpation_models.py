#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
腹诊和皮肤触诊数据模型定义
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class AbdominalRegion(Enum):
    """腹部区域枚举"""
    EPIGASTRIC = "上脘"  # 上腹部
    UMBILICAL = "中脘"  # 脐部
    HYPOGASTRIC = "下脘"  # 下腹部
    RIGHT_HYPOCHONDRIUM = "右胁"  # 右季肋部
    LEFT_HYPOCHONDRIUM = "左胁"  # 左季肋部
    RIGHT_ILIAC = "右少腹"  # 右髂部
    LEFT_ILIAC = "左少腹"  # 左髂部
    RIGHT_LUMBAR = "右腰"  # 右腰部
    LEFT_LUMBAR = "左腰"  # 左腰部


class TendernessLevel(Enum):
    """压痛程度枚举"""
    NONE = "无压痛"
    MILD = "轻度压痛"
    MODERATE = "中度压痛"
    SEVERE = "重度压痛"
    REBOUND = "反跳痛"


class TensionLevel(Enum):
    """腹部紧张度枚举"""
    RELAXED = "松软"
    NORMAL = "正常"
    TENSE = "紧张"
    RIGID = "板状"


class SkinTexture(Enum):
    """皮肤质地枚举"""
    SMOOTH = "光滑"
    ROUGH = "粗糙"
    DRY = "干燥"
    OILY = "油腻"
    SCALY = "鳞状"
    NORMAL = "正常"


class SkinMoistureLevel(Enum):
    """皮肤湿度级别"""
    VERY_DRY = "极干"
    DRY = "干燥"
    NORMAL = "正常"
    MOIST = "湿润"
    VERY_MOIST = "极湿"


class SkinElasticityLevel(Enum):
    """皮肤弹性级别"""
    POOR = "差"
    FAIR = "一般"
    GOOD = "良好"
    VERY_GOOD = "很好"
    EXCELLENT = "极佳"


class SkinTemperatureLevel(Enum):
    """皮肤温度级别"""
    COLD = "冷"
    COOL = "凉"
    NORMAL = "正常"
    WARM = "温"
    HOT = "热"


@dataclass
class AbdominalRegionData:
    """腹部区域数据"""
    region_id: str
    region_name: str
    region_type: AbdominalRegion
    tenderness_level: TendernessLevel
    tension_level: TensionLevel
    has_mass: bool = False
    mass_description: Optional[str] = None
    texture_description: str = ""
    pulsation: bool = False
    gurgling: bool = False  # 肠鸣音
    comments: str = ""
    examined_time: datetime = field(default_factory=datetime.now)
    pressure_applied: float = 0.0  # 施加的压力 (N)
    examiner_notes: List[str] = field(default_factory=list)


@dataclass
class AbdominalFinding:
    """腹诊发现"""
    region_id: str
    region_name: str
    finding_type: str  # 压痛、肿块、紧张等
    description: str
    severity: float  # 0-1
    confidence: float  # 0-1
    potential_causes: List[str] = field(default_factory=list)
    related_meridians: List[str] = field(default_factory=list)
    tcm_interpretation: str = ""
    western_interpretation: str = ""


@dataclass
class SkinRegionData:
    """皮肤区域数据"""
    region_id: str
    region_name: str
    moisture_level: SkinMoistureLevel
    elasticity: SkinElasticityLevel
    texture: SkinTexture
    temperature: SkinTemperatureLevel
    color: str  # 颜色描述
    temperature_value: Optional[float] = None  # 实际温度值
    moisture_value: Optional[float] = None  # 实际湿度值
    special_markings: List[str] = field(default_factory=list)  # 特殊标记（痣、斑等）
    examined_time: datetime = field(default_factory=datetime.now)


@dataclass
class SkinFinding:
    """皮肤触诊发现"""
    region_id: str
    region_name: str
    finding_type: str
    description: str
    related_conditions: List[str] = field(default_factory=list)
    tcm_interpretation: str = ""
    severity: float = 0.0  # 0-1
    requires_attention: bool = False


@dataclass
class PalpationOverview:
    """切诊总览"""
    examination_id: str
    user_id: str
    examination_time: datetime
    pulse_overview: Optional[Dict[str, Any]] = None
    abdominal_overview: Optional[Dict[str, Any]] = None
    skin_overview: Optional[Dict[str, Any]] = None
    general_condition: str = ""
    examiner_id: Optional[str] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class TCMPattern:
    """中医证型"""
    pattern_name: str  # 证型名称
    pattern_type: str  # 证型类别（气虚、血虚、阴虚、阳虚等）
    element: str  # 五行属性
    nature: str  # 寒热属性
    confidence: float  # 置信度
    description: str  # 描述
    supporting_findings: List[str] = field(default_factory=list)  # 支持的发现
    contradicting_findings: List[str] = field(default_factory=list)  # 矛盾的发现
    related_symptoms: List[str] = field(default_factory=list)  # 相关症状
    treatment_principles: List[str] = field(default_factory=list)  # 治则


@dataclass
class HealthAlert:
    """健康警报"""
    alert_id: str
    alert_type: str  # 警报类型
    description: str  # 描述
    severity: float  # 严重程度 0-1
    urgency: str  # 紧急程度：low, medium, high, critical
    recommendation: str  # 建议
    requires_immediate_attention: bool
    related_findings: List[str] = field(default_factory=list)
    created_time: datetime = field(default_factory=datetime.now)


@dataclass
class ComprehensivePalpationAnalysis:
    """综合切诊分析"""
    analysis_id: str
    user_id: str
    analysis_time: datetime
    
    # 各项切诊结果
    pulse_session_id: Optional[str] = None
    pulse_analysis: Optional[Dict[str, Any]] = None
    abdominal_findings: List[AbdominalFinding] = field(default_factory=list)
    skin_findings: List[SkinFinding] = field(default_factory=list)
    
    # 综合分析
    tcm_patterns: List[TCMPattern] = field(default_factory=list)
    health_alerts: List[HealthAlert] = field(default_factory=list)
    overall_assessment: str = ""
    
    # 建议
    dietary_recommendations: List[str] = field(default_factory=list)
    lifestyle_recommendations: List[str] = field(default_factory=list)
    treatment_suggestions: List[str] = field(default_factory=list)
    followup_recommendations: List[str] = field(default_factory=list)
    
    # 元数据
    confidence_score: float = 0.0
    quality_score: float = 0.0
    examiner_notes: List[str] = field(default_factory=list)
    

@dataclass
class PalpationReport:
    """切诊报告"""
    report_id: str
    analysis_id: str
    user_id: str
    generation_time: datetime
    report_format: str  # PDF, HTML, JSON
    
    # 报告内容
    executive_summary: str
    detailed_findings: Dict[str, Any]
    visualizations: List[Dict[str, Any]] = field(default_factory=list)
    
    # 历史对比
    historical_comparison: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    
    # 建议和计划
    action_items: List[str] = field(default_factory=list)
    followup_schedule: Optional[Dict[str, Any]] = None
    
    # 元数据
    report_url: Optional[str] = None
    report_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict) 