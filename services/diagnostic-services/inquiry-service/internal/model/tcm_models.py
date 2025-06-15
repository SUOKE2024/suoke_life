from typing import Dict, List, Any, Optional, Union

"""
tcm_models - 索克生活项目模块
"""

from dataclasses import dataclass

#! / usr / bin / env python

"""
中医模型定义
"""



@dataclass
class Symptom:
    """症状"""

    name: str
    severity: str  # "MILD", "MODERATE", "SEVERE"
    onset_time: int | None = None
    duration: int | None = None
    description: str | None = None
    confidence: float = 0.8


@dataclass
class BodyLocation:
    """身体部位"""

    name: str
    side: str  # "left", "right", "central", "bilateral"
    associated_symptoms: list[str]


@dataclass
class TemporalFactor:
    """时间因素"""

    factor_type: str  # "diurnal", "seasonal", "durational", "frequency", "triggers"
    description: str
    symptoms_affected: list[str]


@dataclass
class TCMPattern:
    """中医证型"""

    id: str
    name: str
    english_name: str
    category: str
    confidence: float
    matched_symptoms: list[str]
    rule_id: str | None = None


@dataclass
class DetailedTCMPattern:
    """详细中医证型"""

    id: str
    name: str
    english_name: str
    category: str
    description: str
    main_symptoms: list[str]
    secondary_symptoms: list[str]
    dietary_recommendations: list[str]
    lifestyle_recommendations: list[str]
    confidence: float = 0.0
    matched_symptoms: list[str] = None
    rule_id: str = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.matched_symptoms is None:
            self.matched_symptoms = []


@dataclass
class SymptomTCMMapping:
    """症状中医映射"""

    symptom_name: str
    tcm_interpretations: list[dict]
    pattern_associations: dict[str, float]
    confidence: float = 0.0

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if not self.tcm_interpretations:
            self.tcm_interpretations = []
        if not self.pattern_associations:
            self.pattern_associations = {}


@dataclass
class TCMDiagnosisRule:
    """中医诊断规则"""

    rule_id: str
    pattern_name: str
    required_symptoms: list[str]
    supporting_symptoms: dict[str, float]
    exclusion_symptoms: list[str]
    minimum_required_count: int
    minimum_supporting_score: float
    tongue_rules: dict = None
    pulse_rules: dict = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if not self.required_symptoms:
            self.required_symptoms = []
        if not self.supporting_symptoms:
            self.supporting_symptoms = {}
        if not self.exclusion_symptoms:
            self.exclusion_symptoms = []
        if self.tongue_rules is None:
            self.tongue_rules = {}
        if self.pulse_rules is None:
            self.pulse_rules = {}


@dataclass
class Constitution:
    """体质类型"""

    type_code: str
    type_name: str
    confidence: float
    description: str
    characteristics: list[str]
