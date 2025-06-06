"""
tcm_models - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医数据模型 - 定义中医相关的数据结构
"""



class ConstitutionType(Enum):
    """中医体质分类"""
    PEACEFUL = "平和质"              # 平和体质
    QI_DEFICIENCY = "气虚质"         # 气虚体质
    YANG_DEFICIENCY = "阳虚质"       # 阳虚体质
    YIN_DEFICIENCY = "阴虚质"        # 阴虚体质
    PHLEGM_DAMPNESS = "痰湿质"       # 痰湿体质
    DAMP_HEAT = "湿热质"             # 湿热体质
    BLOOD_STASIS = "血瘀质"          # 血瘀体质
    QI_STAGNATION = "气郁质"         # 气郁体质
    SPECIAL_DIATHESIS = "特禀质"     # 特禀体质


class SymptomCategory(Enum):
    """症状分类"""
    HEAD_NECK = "头颈部"
    CHEST_HEART = "胸心部"
    DIGESTIVE = "消化系统"
    UROGENITAL = "泌尿生殖"
    MUSCULOSKELETAL = "筋骨肢体"
    SKIN = "皮肤"
    CONSTITUTIONAL = "全身症状"
    EMOTIONAL = "情志症状"
    SLEEP = "睡眠"
    GENERAL = "一般症状"


class OrganSystem(Enum):
    """脏腑系统"""
    HEART = "心"
    LIVER = "肝"
    SPLEEN = "脾"
    LUNG = "肺"
    KIDNEY = "肾"
    GALLBLADDER = "胆"
    STOMACH = "胃"
    SMALL_INTESTINE = "小肠"
    LARGE_INTESTINE = "大肠"
    BLADDER = "膀胱"
    TRIPLE_HEATER = "三焦"
    PERICARDIUM = "心包"


class PathologicalFactor(Enum):
    """病理因素"""
    QI_DEFICIENCY = "气虚"
    BLOOD_DEFICIENCY = "血虚"
    YIN_DEFICIENCY = "阴虚"
    YANG_DEFICIENCY = "阳虚"
    QI_STAGNATION = "气滞"
    BLOOD_STASIS = "血瘀"
    PHLEGM = "痰"
    DAMPNESS = "湿"
    HEAT = "热"
    COLD = "寒"
    WIND = "风"
    DRYNESS = "燥"
    FIRE = "火"


@dataclass
class Syndrome:
    """证型"""
    name: str
    type: Any  # SyndromeType enum
    confidence: float
    description: str
    primary_symptoms: List[str] = field(default_factory=list)
    secondary_symptoms: List[str] = field(default_factory=list)
    tongue_manifestation: Optional[str] = None
    pulse_manifestation: Optional[str] = None
    pathological_factors: List[PathologicalFactor] = field(default_factory=list)
    affected_organs: List[OrganSystem] = field(default_factory=list)


@dataclass
class SyndromePattern:
    """证型模式"""
    syndrome_type: Any  # SyndromeType
    required_symptoms: List[str]
    optional_symptoms: List[str]
    exclusion_symptoms: List[str]
    tongue_patterns: List[str]
    pulse_patterns: List[str]
    severity_weights: Dict[str, float]
    confidence_threshold: float


@dataclass
class TreatmentPrinciple:
    """治疗原则"""
    name: str
    description: str
    priority: int
    methods: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)


@dataclass
class HerbFormula:
    """方剂"""
    name: str
    composition: Dict[str, str]  # 药物名称 -> 用量
    functions: List[str]
    indications: List[str]
    contraindications: List[str]
    modifications: Dict[str, Dict[str, str]] = field(default_factory=dict)
    source: Optional[str] = None


@dataclass
class SingleHerb:
    """单味药"""
    name: str
    pinyin: str
    latin_name: str
    properties: Dict[str, str]  # 性味归经
    functions: List[str]
    dosage: str
    contraindications: List[str]
    incompatibilities: List[str] = field(default_factory=list)
    processing_methods: List[str] = field(default_factory=list)


@dataclass
class Acupoint:
    """穴位"""
    name: str
    pinyin: str
    code: str  # 国际标准代码
    location: str
    meridian: str
    functions: List[str]
    indications: List[str]
    needling_method: str
    depth: str
    contraindications: List[str] = field(default_factory=list)


@dataclass
class PulsePattern:
    """脉象"""
    name: str
    characteristics: List[str]
    clinical_significance: List[str]
    associated_syndromes: List[str]
    frequency_range: Optional[tuple] = None  # (min, max) beats per minute
    strength: Optional[str] = None
    rhythm: Optional[str] = None


@dataclass
class TonguePattern:
    """舌象"""
    tongue_body_color: str
    tongue_body_shape: str
    coating_color: str
    coating_thickness: str
    coating_moisture: str
    clinical_significance: List[str]
    associated_syndromes: List[str]


@dataclass
class ConstitutionAssessment:
    """体质评估"""
    constitution_type: ConstitutionType
    score: float
    characteristics: List[str]
    tendencies: List[str]
    health_risks: List[str]
    lifestyle_recommendations: Dict[str, List[str]]
    dietary_recommendations: Dict[str, List[str]]
    exercise_recommendations: List[str]


@dataclass
class TCMDiagnosis:
    """中医诊断"""
    primary_syndrome: Syndrome
    secondary_syndromes: List[Syndrome]
    constitution_assessment: ConstitutionAssessment
    pulse_pattern: Optional[PulsePattern]
    tongue_pattern: Optional[TonguePattern]
    pathogenesis: str  # 病机
    treatment_principles: List[TreatmentPrinciple]
    recommended_formulas: List[HerbFormula]
    recommended_acupoints: List[Acupoint]
    lifestyle_guidance: Dict[str, List[str]]
    prognosis: str
    follow_up_recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SymptomRecord:
    """症状记录"""
    symptom: str
    severity: int  # 1-10
    duration: str
    frequency: str
    triggers: List[str] = field(default_factory=list)
    relieving_factors: List[str] = field(default_factory=list)
    associated_symptoms: List[str] = field(default_factory=list)
    recorded_at: datetime = field(default_factory=datetime.now)


@dataclass
class PatientProfile:
    """患者档案"""
    age: int
    gender: str
    constitution_type: Optional[ConstitutionType]
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    lifestyle_factors: Dict[str, Any] = field(default_factory=dict)
    family_history: List[str] = field(default_factory=list)


@dataclass
class TreatmentPlan:
    """治疗方案"""
    diagnosis: TCMDiagnosis
    herbal_prescription: Optional[HerbFormula]
    acupuncture_points: List[Acupoint]
    lifestyle_modifications: Dict[str, List[str]]
    dietary_therapy: Dict[str, List[str]]
    exercise_prescription: List[str]
    follow_up_schedule: List[str]
    expected_outcomes: List[str]
    duration: str
    monitoring_parameters: List[str]


@dataclass
class KnowledgeGraphNode:
    """知识图谱节点"""
    id: str
    type: str  # syndrome, herb, formula, acupoint, etc.
    name: str
    properties: Dict[str, Any]
    relationships: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KnowledgeGraphRelation:
    """知识图谱关系"""
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0


@dataclass
class TCMKnowledgeBase:
    """中医知识库"""
    syndromes: Dict[str, Syndrome] = field(default_factory=dict)
    herbs: Dict[str, SingleHerb] = field(default_factory=dict)
    formulas: Dict[str, HerbFormula] = field(default_factory=dict)
    acupoints: Dict[str, Acupoint] = field(default_factory=dict)
    pulse_patterns: Dict[str, PulsePattern] = field(default_factory=dict)
    tongue_patterns: Dict[str, TonguePattern] = field(default_factory=dict)
    constitution_types: Dict[str, ConstitutionAssessment] = field(default_factory=dict)
    knowledge_graph: Dict[str, KnowledgeGraphNode] = field(default_factory=dict)
    relations: List[KnowledgeGraphRelation] = field(default_factory=list)


# 常用的中医术语映射
TCM_TERMINOLOGY = {
    "organs": {
        "心": ["heart", "心脏", "心系"],
        "肝": ["liver", "肝脏", "肝系"],
        "脾": ["spleen", "脾脏", "脾系"],
        "肺": ["lung", "肺脏", "肺系"],
        "肾": ["kidney", "肾脏", "肾系"]
    },
    "pathological_factors": {
        "气虚": ["qi deficiency", "气不足", "元气虚"],
        "血虚": ["blood deficiency", "血不足", "血少"],
        "阴虚": ["yin deficiency", "阴液不足", "阴亏"],
        "阳虚": ["yang deficiency", "阳气不足", "阳衰"],
        "气滞": ["qi stagnation", "气机不畅", "气郁"],
        "血瘀": ["blood stasis", "血行不畅", "瘀血"]
    },
    "constitutions": {
        "平和质": ["balanced constitution", "正常体质"],
        "气虚质": ["qi deficiency constitution", "气虚体质"],
        "阳虚质": ["yang deficiency constitution", "阳虚体质"],
        "阴虚质": ["yin deficiency constitution", "阴虚体质"],
        "痰湿质": ["phlegm-dampness constitution", "痰湿体质"],
        "湿热质": ["damp-heat constitution", "湿热体质"],
        "血瘀质": ["blood stasis constitution", "血瘀体质"],
        "气郁质": ["qi stagnation constitution", "气郁体质"],
        "特禀质": ["special diathesis constitution", "特禀体质"]
    }
} 