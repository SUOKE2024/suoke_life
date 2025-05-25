"""
个性化医疗服务
实现中医辨证论治服务匹配、现代医学检查项目推荐、综合食疗方案制定和康复资源配置
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

import numpy as np
import pandas as pd

from ..domain.models import ConstitutionType, ResourceType, UrgencyLevel
from .resource_management_service import ResourceManagementService, ResourceCategory
from .food_agriculture_service import FoodAgricultureService

logger = logging.getLogger(__name__)


class TreatmentApproach(Enum):
    """治疗方法"""
    TCM_SYNDROME_DIFFERENTIATION = "tcm_syndrome"      # 中医辨证论治
    MODERN_MEDICAL_EXAMINATION = "modern_examination"  # 现代医学检查
    INTEGRATED_THERAPY = "integrated_therapy"          # 中西医结合
    FOOD_THERAPY = "food_therapy"                      # 食疗养生
    REHABILITATION = "rehabilitation"                   # 康复治疗
    PREVENTIVE_CARE = "preventive_care"                # 预防保健


class SyndromeType(Enum):
    """中医证型"""
    QI_DEFICIENCY_SYNDROME = "qi_deficiency"           # 气虚证
    YANG_DEFICIENCY_SYNDROME = "yang_deficiency"       # 阳虚证
    YIN_DEFICIENCY_SYNDROME = "yin_deficiency"         # 阴虚证
    BLOOD_STASIS_SYNDROME = "blood_stasis"             # 血瘀证
    QI_STAGNATION_SYNDROME = "qi_stagnation"           # 气滞证
    PHLEGM_DAMPNESS_SYNDROME = "phlegm_dampness"       # 痰湿证
    DAMP_HEAT_SYNDROME = "damp_heat"                   # 湿热证
    WIND_COLD_SYNDROME = "wind_cold"                   # 风寒证
    WIND_HEAT_SYNDROME = "wind_heat"                   # 风热证


class ExaminationType(Enum):
    """检查类型"""
    BLOOD_TEST = "blood_test"                          # 血液检查
    URINE_TEST = "urine_test"                          # 尿液检查
    IMAGING_EXAMINATION = "imaging"                     # 影像检查
    ELECTROCARDIOGRAM = "ecg"                          # 心电图
    ULTRASOUND = "ultrasound"                          # 超声检查
    ENDOSCOPY = "endoscopy"                            # 内镜检查
    PATHOLOGICAL_EXAMINATION = "pathology"             # 病理检查
    GENETIC_TESTING = "genetic"                        # 基因检测


class RehabilitationType(Enum):
    """康复类型"""
    PHYSICAL_THERAPY = "physical_therapy"              # 物理治疗
    OCCUPATIONAL_THERAPY = "occupational_therapy"     # 作业治疗
    SPEECH_THERAPY = "speech_therapy"                  # 言语治疗
    PSYCHOLOGICAL_THERAPY = "psychological_therapy"   # 心理治疗
    ACUPUNCTURE_THERAPY = "acupuncture"               # 针灸治疗
    MASSAGE_THERAPY = "massage"                        # 推拿按摩
    EXERCISE_THERAPY = "exercise"                      # 运动治疗
    MUSIC_THERAPY = "music_therapy"                    # 音乐治疗


@dataclass
class PatientProfile:
    """患者档案"""
    user_id: str
    constitution_type: ConstitutionType
    age: int
    gender: str
    height: float  # cm
    weight: float  # kg
    medical_history: List[str]
    current_symptoms: List[str]
    allergies: List[str]
    medications: List[str]
    lifestyle_factors: Dict[str, Any]
    family_history: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SyndromeAnalysis:
    """证候分析"""
    syndrome_type: SyndromeType
    confidence_score: float
    primary_symptoms: List[str]
    secondary_symptoms: List[str]
    tongue_diagnosis: Dict[str, str]
    pulse_diagnosis: Dict[str, str]
    treatment_principles: List[str]
    recommended_formulas: List[str]
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class ExaminationRecommendation:
    """检查推荐"""
    examination_type: ExaminationType
    examination_name: str
    priority_level: UrgencyLevel
    reason: str
    expected_findings: List[str]
    preparation_instructions: List[str]
    estimated_cost: float
    estimated_duration: int  # minutes
    recommended_facility: Optional[str] = None


@dataclass
class TreatmentPlan:
    """治疗方案"""
    plan_id: str
    patient_id: str
    treatment_approach: TreatmentApproach
    syndrome_analysis: Optional[SyndromeAnalysis]
    examination_recommendations: List[ExaminationRecommendation]
    food_therapy_plan: Optional[Dict[str, Any]]
    rehabilitation_plan: Optional[Dict[str, Any]]
    medication_recommendations: List[Dict[str, Any]]
    lifestyle_recommendations: List[str]
    follow_up_schedule: List[Dict[str, str]]
    estimated_duration_weeks: int
    estimated_total_cost: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class TreatmentProgress:
    """治疗进展"""
    progress_id: str
    plan_id: str
    patient_id: str
    assessment_date: datetime
    symptom_improvement: Dict[str, float]  # 症状改善程度 0-1
    side_effects: List[str]
    compliance_rate: float  # 依从性 0-1
    objective_measurements: Dict[str, float]
    patient_feedback: str
    doctor_notes: str
    next_assessment_date: datetime
    plan_adjustments: List[str]


class PersonalizedMedicalService:
    """
    个性化医疗服务
    
    负责中医辨证论治服务匹配、现代医学检查项目推荐、
    综合食疗方案制定和康复资源配置
    """
    
    def __init__(self, config: Dict[str, Any], 
                 resource_service: ResourceManagementService,
                 food_service: FoodAgricultureService):
        self.config = config
        self.resource_service = resource_service
        self.food_service = food_service
        
        # 患者档案
        self.patient_profiles: Dict[str, PatientProfile] = {}
        
        # 治疗方案
        self.treatment_plans: Dict[str, TreatmentPlan] = {}
        
        # 治疗进展记录
        self.treatment_progress: Dict[str, List[TreatmentProgress]] = defaultdict(list)
        
        # 证候分析规则
        self.syndrome_rules = self._initialize_syndrome_rules()
        
        # 检查推荐规则
        self.examination_rules = self._initialize_examination_rules()
        
        # 康复方案模板
        self.rehabilitation_templates = self._initialize_rehabilitation_templates()
        
        # 体质-治疗方法映射
        self.constitution_treatment_mapping = self._initialize_constitution_treatment_mapping()
        
        logger.info("个性化医疗服务初始化完成")
    
    def _initialize_syndrome_rules(self) -> Dict[SyndromeType, Dict[str, Any]]:
        """初始化证候分析规则"""
        return {
            SyndromeType.QI_DEFICIENCY_SYNDROME: {
                "primary_symptoms": ["乏力", "气短", "懒言", "自汗", "食欲不振"],
                "secondary_symptoms": ["头晕", "心悸", "面色萎黄", "大便溏薄"],
                "tongue_signs": ["舌淡", "苔薄白", "舌体胖大"],
                "pulse_signs": ["脉细弱", "脉缓"],
                "treatment_principles": ["补气健脾", "益气升阳"],
                "recommended_formulas": ["四君子汤", "补中益气汤", "参苓白术散"],
                "constitution_correlation": [ConstitutionType.QI_DEFICIENCY]
            },
            SyndromeType.YANG_DEFICIENCY_SYNDROME: {
                "primary_symptoms": ["畏寒", "四肢不温", "腰膝酸软", "夜尿频多"],
                "secondary_symptoms": ["精神萎靡", "面色苍白", "舌淡胖", "脉沉迟"],
                "tongue_signs": ["舌淡胖", "苔白滑"],
                "pulse_signs": ["脉沉迟", "脉弱"],
                "treatment_principles": ["温阳补肾", "温中健脾"],
                "recommended_formulas": ["金匮肾气丸", "右归丸", "附子理中汤"],
                "constitution_correlation": [ConstitutionType.YANG_DEFICIENCY]
            },
            SyndromeType.YIN_DEFICIENCY_SYNDROME: {
                "primary_symptoms": ["潮热", "盗汗", "五心烦热", "口干咽燥"],
                "secondary_symptoms": ["失眠", "头晕", "腰膝酸软", "耳鸣"],
                "tongue_signs": ["舌红", "苔少", "舌体瘦"],
                "pulse_signs": ["脉细数", "脉弦细"],
                "treatment_principles": ["滋阴降火", "养阴清热"],
                "recommended_formulas": ["六味地黄丸", "知柏地黄丸", "左归丸"],
                "constitution_correlation": [ConstitutionType.YIN_DEFICIENCY]
            },
            SyndromeType.BLOOD_STASIS_SYNDROME: {
                "primary_symptoms": ["胸痛", "腹痛", "头痛", "痛处固定"],
                "secondary_symptoms": ["面色晦暗", "肌肤甲错", "舌质紫暗"],
                "tongue_signs": ["舌质紫暗", "有瘀斑", "舌下静脉曲张"],
                "pulse_signs": ["脉涩", "脉弦"],
                "treatment_principles": ["活血化瘀", "理气止痛"],
                "recommended_formulas": ["血府逐瘀汤", "桃红四物汤", "丹参饮"],
                "constitution_correlation": [ConstitutionType.BLOOD_STASIS]
            },
            SyndromeType.QI_STAGNATION_SYNDROME: {
                "primary_symptoms": ["胸胁胀痛", "情志抑郁", "善太息", "腹胀"],
                "secondary_symptoms": ["烦躁易怒", "失眠", "食欲不振", "月经不调"],
                "tongue_signs": ["舌苔薄白", "舌边尖红"],
                "pulse_signs": ["脉弦", "脉细弦"],
                "treatment_principles": ["疏肝理气", "调畅气机"],
                "recommended_formulas": ["逍遥散", "柴胡疏肝散", "甘麦大枣汤"],
                "constitution_correlation": [ConstitutionType.QI_STAGNATION]
            },
            SyndromeType.PHLEGM_DAMPNESS_SYNDROME: {
                "primary_symptoms": ["身重困倦", "胸闷", "痰多", "食欲不振"],
                "secondary_symptoms": ["头重如裹", "恶心", "大便溏薄", "小便不利"],
                "tongue_signs": ["舌体胖大", "苔白腻", "舌边有齿痕"],
                "pulse_signs": ["脉滑", "脉缓"],
                "treatment_principles": ["健脾化湿", "燥湿化痰"],
                "recommended_formulas": ["二陈汤", "平胃散", "六君子汤"],
                "constitution_correlation": [ConstitutionType.PHLEGM_DAMPNESS]
            },
            SyndromeType.DAMP_HEAT_SYNDROME: {
                "primary_symptoms": ["发热", "身重", "胸闷", "小便黄赤"],
                "secondary_symptoms": ["口苦", "恶心", "大便黏腻", "皮肤湿疹"],
                "tongue_signs": ["舌红", "苔黄腻"],
                "pulse_signs": ["脉滑数", "脉濡数"],
                "treatment_principles": ["清热利湿", "分利湿热"],
                "recommended_formulas": ["三仁汤", "甘露消毒丹", "茵陈蒿汤"],
                "constitution_correlation": [ConstitutionType.DAMP_HEAT]
            }
        }
    
    def _initialize_examination_rules(self) -> Dict[str, Dict[str, Any]]:
        """初始化检查推荐规则"""
        return {
            "cardiovascular_symptoms": {
                "symptoms": ["胸痛", "心悸", "气短", "水肿"],
                "examinations": [
                    {
                        "type": ExaminationType.ELECTROCARDIOGRAM,
                        "name": "心电图检查",
                        "priority": UrgencyLevel.HIGH,
                        "reason": "评估心脏电活动异常"
                    },
                    {
                        "type": ExaminationType.BLOOD_TEST,
                        "name": "心肌酶谱检查",
                        "priority": UrgencyLevel.HIGH,
                        "reason": "检测心肌损伤标志物"
                    },
                    {
                        "type": ExaminationType.ULTRASOUND,
                        "name": "心脏超声检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "评估心脏结构和功能"
                    }
                ]
            },
            "digestive_symptoms": {
                "symptoms": ["腹痛", "恶心", "呕吐", "腹泻", "便血"],
                "examinations": [
                    {
                        "type": ExaminationType.BLOOD_TEST,
                        "name": "肝功能检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "评估肝脏功能状态"
                    },
                    {
                        "type": ExaminationType.ULTRASOUND,
                        "name": "腹部超声检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "检查腹部器官结构"
                    },
                    {
                        "type": ExaminationType.ENDOSCOPY,
                        "name": "胃镜检查",
                        "priority": UrgencyLevel.LOW,
                        "reason": "直接观察胃肠道病变"
                    }
                ]
            },
            "respiratory_symptoms": {
                "symptoms": ["咳嗽", "咳痰", "胸闷", "呼吸困难"],
                "examinations": [
                    {
                        "type": ExaminationType.IMAGING_EXAMINATION,
                        "name": "胸部X线检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "检查肺部病变"
                    },
                    {
                        "type": ExaminationType.BLOOD_TEST,
                        "name": "血常规检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "评估感染和炎症状态"
                    }
                ]
            },
            "neurological_symptoms": {
                "symptoms": ["头痛", "头晕", "失眠", "记忆力减退"],
                "examinations": [
                    {
                        "type": ExaminationType.IMAGING_EXAMINATION,
                        "name": "头颅CT检查",
                        "priority": UrgencyLevel.HIGH,
                        "reason": "排除颅内器质性病变"
                    },
                    {
                        "type": ExaminationType.BLOOD_TEST,
                        "name": "血糖血脂检查",
                        "priority": UrgencyLevel.MEDIUM,
                        "reason": "评估代谢状态"
                    }
                ]
            }
        }
    
    def _initialize_rehabilitation_templates(self) -> Dict[RehabilitationType, Dict[str, Any]]:
        """初始化康复方案模板"""
        return {
            RehabilitationType.PHYSICAL_THERAPY: {
                "description": "物理治疗康复方案",
                "suitable_conditions": ["骨折康复", "关节炎", "肌肉损伤", "脊柱疾病"],
                "treatment_methods": ["运动疗法", "手法治疗", "物理因子治疗"],
                "duration_weeks": 8,
                "frequency": "每周3次",
                "equipment_needed": ["康复训练器械", "理疗设备"],
                "expected_outcomes": ["改善关节活动度", "增强肌力", "减轻疼痛"]
            },
            RehabilitationType.OCCUPATIONAL_THERAPY: {
                "description": "作业治疗康复方案",
                "suitable_conditions": ["脑卒中", "脊髓损伤", "认知障碍"],
                "treatment_methods": ["日常生活活动训练", "认知训练", "手功能训练"],
                "duration_weeks": 12,
                "frequency": "每周2-3次",
                "equipment_needed": ["作业治疗器具", "认知训练软件"],
                "expected_outcomes": ["提高生活自理能力", "改善认知功能", "增强手功能"]
            },
            RehabilitationType.ACUPUNCTURE_THERAPY: {
                "description": "针灸治疗康复方案",
                "suitable_conditions": ["中风后遗症", "慢性疼痛", "失眠", "消化不良"],
                "treatment_methods": ["体针", "耳针", "电针", "艾灸"],
                "duration_weeks": 6,
                "frequency": "每周2-3次",
                "equipment_needed": ["针灸针具", "艾条", "电针仪"],
                "expected_outcomes": ["调节气血", "改善症状", "增强体质"]
            },
            RehabilitationType.MASSAGE_THERAPY: {
                "description": "推拿按摩康复方案",
                "suitable_conditions": ["颈椎病", "腰椎病", "肌肉紧张", "疲劳综合征"],
                "treatment_methods": ["推法", "拿法", "按法", "摩法"],
                "duration_weeks": 4,
                "frequency": "每周2次",
                "equipment_needed": ["按摩床", "推拿用具"],
                "expected_outcomes": ["缓解肌肉紧张", "改善血液循环", "减轻疼痛"]
            },
            RehabilitationType.EXERCISE_THERAPY: {
                "description": "运动治疗康复方案",
                "suitable_conditions": ["心血管疾病", "糖尿病", "肥胖", "骨质疏松"],
                "treatment_methods": ["有氧运动", "力量训练", "柔韧性训练", "平衡训练"],
                "duration_weeks": 16,
                "frequency": "每周3-5次",
                "equipment_needed": ["健身器械", "运动监测设备"],
                "expected_outcomes": ["改善心肺功能", "控制血糖", "增强骨密度"]
            }
        }
    
    def _initialize_constitution_treatment_mapping(self) -> Dict[ConstitutionType, Dict[str, Any]]:
        """初始化体质-治疗方法映射"""
        return {
            ConstitutionType.QI_DEFICIENCY: {
                "primary_approach": TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.ACUPUNCTURE_THERAPY,
                    TreatmentApproach.EXERCISE_THERAPY
                ],
                "examination_focus": ["血常规", "生化检查", "免疫功能"],
                "rehabilitation_types": [
                    RehabilitationType.EXERCISE_THERAPY,
                    RehabilitationType.ACUPUNCTURE_THERAPY
                ]
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "primary_approach": TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.ACUPUNCTURE_THERAPY
                ],
                "examination_focus": ["甲状腺功能", "性激素", "肾功能"],
                "rehabilitation_types": [
                    RehabilitationType.ACUPUNCTURE_THERAPY,
                    RehabilitationType.MASSAGE_THERAPY
                ]
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "primary_approach": TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.ACUPUNCTURE_THERAPY
                ],
                "examination_focus": ["激素水平", "骨密度", "肝肾功能"],
                "rehabilitation_types": [
                    RehabilitationType.ACUPUNCTURE_THERAPY,
                    RehabilitationType.MASSAGE_THERAPY
                ]
            },
            ConstitutionType.PHLEGM_DAMPNESS: {
                "primary_approach": TreatmentApproach.INTEGRATED_THERAPY,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.EXERCISE_THERAPY,
                    TreatmentApproach.MODERN_MEDICAL_EXAMINATION
                ],
                "examination_focus": ["血脂", "血糖", "肝功能", "心血管检查"],
                "rehabilitation_types": [
                    RehabilitationType.EXERCISE_THERAPY,
                    RehabilitationType.PHYSICAL_THERAPY
                ]
            },
            ConstitutionType.DAMP_HEAT: {
                "primary_approach": TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.MODERN_MEDICAL_EXAMINATION
                ],
                "examination_focus": ["肝功能", "炎症指标", "过敏原检测"],
                "rehabilitation_types": [
                    RehabilitationType.ACUPUNCTURE_THERAPY,
                    RehabilitationType.EXERCISE_THERAPY
                ]
            },
            ConstitutionType.BLOOD_STASIS: {
                "primary_approach": TreatmentApproach.INTEGRATED_THERAPY,
                "recommended_treatments": [
                    TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                    TreatmentApproach.MODERN_MEDICAL_EXAMINATION,
                    TreatmentApproach.REHABILITATION
                ],
                "examination_focus": ["凝血功能", "心血管检查", "血流变学"],
                "rehabilitation_types": [
                    RehabilitationType.PHYSICAL_THERAPY,
                    RehabilitationType.ACUPUNCTURE_THERAPY,
                    RehabilitationType.MASSAGE_THERAPY
                ]
            },
            ConstitutionType.QI_STAGNATION: {
                "primary_approach": TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION,
                "recommended_treatments": [
                    TreatmentApproach.FOOD_THERAPY,
                    TreatmentApproach.REHABILITATION
                ],
                "examination_focus": ["心理评估", "激素水平", "神经功能"],
                "rehabilitation_types": [
                    RehabilitationType.PSYCHOLOGICAL_THERAPY,
                    RehabilitationType.ACUPUNCTURE_THERAPY,
                    RehabilitationType.EXERCISE_THERAPY
                ]
            },
            ConstitutionType.ALLERGIC: {
                "primary_approach": TreatmentApproach.MODERN_MEDICAL_EXAMINATION,
                "recommended_treatments": [
                    TreatmentApproach.INTEGRATED_THERAPY,
                    TreatmentApproach.FOOD_THERAPY
                ],
                "examination_focus": ["过敏原检测", "免疫功能", "炎症指标"],
                "rehabilitation_types": [
                    RehabilitationType.EXERCISE_THERAPY,
                    RehabilitationType.ACUPUNCTURE_THERAPY
                ]
            }
        }
    
    async def create_patient_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建患者档案"""
        try:
            profile = PatientProfile(
                user_id=user_id,
                constitution_type=ConstitutionType(profile_data.get("constitution_type", "qi_deficiency")),
                age=profile_data.get("age", 30),
                gender=profile_data.get("gender", "unknown"),
                height=profile_data.get("height", 170.0),
                weight=profile_data.get("weight", 65.0),
                medical_history=profile_data.get("medical_history", []),
                current_symptoms=profile_data.get("current_symptoms", []),
                allergies=profile_data.get("allergies", []),
                medications=profile_data.get("medications", []),
                lifestyle_factors=profile_data.get("lifestyle_factors", {}),
                family_history=profile_data.get("family_history", [])
            )
            
            self.patient_profiles[user_id] = profile
            
            logger.info(f"患者档案创建成功: {user_id}")
            return {
                "success": True,
                "message": "患者档案创建成功",
                "profile_id": user_id
            }
            
        except Exception as e:
            logger.error(f"创建患者档案失败: {e}")
            return {
                "success": False,
                "message": f"创建患者档案失败: {str(e)}"
            }
    
    async def analyze_syndrome(self, user_id: str, symptoms: List[str], 
                             tongue_diagnosis: Dict[str, str] = None,
                             pulse_diagnosis: Dict[str, str] = None) -> Dict[str, Any]:
        """中医证候分析"""
        try:
            profile = self.patient_profiles.get(user_id)
            if not profile:
                return {
                    "success": False,
                    "message": "患者档案不存在"
                }
            
            # 分析症状匹配度
            syndrome_scores = {}
            
            for syndrome_type, rules in self.syndrome_rules.items():
                score = 0.0
                
                # 主症匹配
                primary_matches = len([s for s in symptoms if any(ps in s for ps in rules["primary_symptoms"])])
                score += primary_matches * 0.6
                
                # 次症匹配
                secondary_matches = len([s for s in symptoms if any(ss in s for ss in rules["secondary_symptoms"])])
                score += secondary_matches * 0.3
                
                # 体质相关性
                if profile.constitution_type in rules.get("constitution_correlation", []):
                    score += 0.1
                
                # 舌诊匹配
                if tongue_diagnosis:
                    tongue_matches = len([t for t in tongue_diagnosis.values() 
                                        if any(ts in t for ts in rules["tongue_signs"])])
                    score += tongue_matches * 0.05
                
                # 脉诊匹配
                if pulse_diagnosis:
                    pulse_matches = len([p for p in pulse_diagnosis.values() 
                                       if any(ps in p for ps in rules["pulse_signs"])])
                    score += pulse_matches * 0.05
                
                syndrome_scores[syndrome_type] = score
            
            # 选择最高分的证型
            if not syndrome_scores:
                return {
                    "success": False,
                    "message": "无法进行证候分析"
                }
            
            best_syndrome = max(syndrome_scores.items(), key=lambda x: x[1])
            syndrome_type, confidence_score = best_syndrome
            
            # 创建证候分析结果
            syndrome_analysis = SyndromeAnalysis(
                syndrome_type=syndrome_type,
                confidence_score=min(confidence_score / 5.0, 1.0),  # 标准化到0-1
                primary_symptoms=[s for s in symptoms if any(ps in s for ps in self.syndrome_rules[syndrome_type]["primary_symptoms"])],
                secondary_symptoms=[s for s in symptoms if any(ss in s for ss in self.syndrome_rules[syndrome_type]["secondary_symptoms"])],
                tongue_diagnosis=tongue_diagnosis or {},
                pulse_diagnosis=pulse_diagnosis or {},
                treatment_principles=self.syndrome_rules[syndrome_type]["treatment_principles"],
                recommended_formulas=self.syndrome_rules[syndrome_type]["recommended_formulas"]
            )
            
            logger.info(f"证候分析完成: {user_id} - {syndrome_type.value}")
            return {
                "success": True,
                "syndrome_analysis": {
                    "syndrome_type": syndrome_type.value,
                    "confidence_score": syndrome_analysis.confidence_score,
                    "primary_symptoms": syndrome_analysis.primary_symptoms,
                    "secondary_symptoms": syndrome_analysis.secondary_symptoms,
                    "treatment_principles": syndrome_analysis.treatment_principles,
                    "recommended_formulas": syndrome_analysis.recommended_formulas,
                    "analysis_date": syndrome_analysis.analysis_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"证候分析失败: {e}")
            return {
                "success": False,
                "message": f"证候分析失败: {str(e)}"
            }
    
    async def recommend_examinations(self, user_id: str, symptoms: List[str]) -> Dict[str, Any]:
        """推荐现代医学检查"""
        try:
            profile = self.patient_profiles.get(user_id)
            if not profile:
                return {
                    "success": False,
                    "message": "患者档案不存在"
                }
            
            recommendations = []
            
            # 基于症状推荐检查
            for category, rules in self.examination_rules.items():
                symptom_matches = [s for s in symptoms if any(rs in s for rs in rules["symptoms"])]
                
                if symptom_matches:
                    for exam in rules["examinations"]:
                        recommendation = ExaminationRecommendation(
                            examination_type=exam["type"],
                            examination_name=exam["name"],
                            priority_level=exam["priority"],
                            reason=exam["reason"],
                            expected_findings=[],
                            preparation_instructions=[],
                            estimated_cost=self._estimate_examination_cost(exam["type"]),
                            estimated_duration=self._estimate_examination_duration(exam["type"])
                        )
                        recommendations.append(recommendation)
            
            # 基于体质推荐检查
            constitution_mapping = self.constitution_treatment_mapping.get(profile.constitution_type, {})
            examination_focus = constitution_mapping.get("examination_focus", [])
            
            for focus in examination_focus:
                if not any(focus in r.examination_name for r in recommendations):
                    recommendation = ExaminationRecommendation(
                        examination_type=ExaminationType.BLOOD_TEST,
                        examination_name=f"{focus}检查",
                        priority_level=UrgencyLevel.MEDIUM,
                        reason=f"基于{profile.constitution_type.value}体质的常规检查",
                        expected_findings=[],
                        preparation_instructions=[],
                        estimated_cost=self._estimate_examination_cost(ExaminationType.BLOOD_TEST),
                        estimated_duration=self._estimate_examination_duration(ExaminationType.BLOOD_TEST)
                    )
                    recommendations.append(recommendation)
            
            # 去重并排序
            unique_recommendations = []
            seen_names = set()
            
            for rec in recommendations:
                if rec.examination_name not in seen_names:
                    unique_recommendations.append(rec)
                    seen_names.add(rec.examination_name)
            
            # 按优先级排序
            priority_order = {
                UrgencyLevel.URGENT: 0,
                UrgencyLevel.HIGH: 1,
                UrgencyLevel.MEDIUM: 2,
                UrgencyLevel.LOW: 3
            }
            unique_recommendations.sort(key=lambda x: priority_order.get(x.priority_level, 3))
            
            logger.info(f"检查推荐完成: {user_id} - {len(unique_recommendations)}项检查")
            return {
                "success": True,
                "recommendations": [
                    {
                        "examination_type": rec.examination_type.value,
                        "examination_name": rec.examination_name,
                        "priority_level": rec.priority_level.value,
                        "reason": rec.reason,
                        "estimated_cost": rec.estimated_cost,
                        "estimated_duration": rec.estimated_duration
                    }
                    for rec in unique_recommendations
                ]
            }
            
        except Exception as e:
            logger.error(f"检查推荐失败: {e}")
            return {
                "success": False,
                "message": f"检查推荐失败: {str(e)}"
            }
    
    def _estimate_examination_cost(self, examination_type: ExaminationType) -> float:
        """估算检查费用"""
        cost_map = {
            ExaminationType.BLOOD_TEST: 200.0,
            ExaminationType.URINE_TEST: 50.0,
            ExaminationType.IMAGING_EXAMINATION: 300.0,
            ExaminationType.ELECTROCARDIOGRAM: 80.0,
            ExaminationType.ULTRASOUND: 150.0,
            ExaminationType.ENDOSCOPY: 800.0,
            ExaminationType.PATHOLOGICAL_EXAMINATION: 500.0,
            ExaminationType.GENETIC_TESTING: 2000.0
        }
        return cost_map.get(examination_type, 100.0)
    
    def _estimate_examination_duration(self, examination_type: ExaminationType) -> int:
        """估算检查时长（分钟）"""
        duration_map = {
            ExaminationType.BLOOD_TEST: 15,
            ExaminationType.URINE_TEST: 10,
            ExaminationType.IMAGING_EXAMINATION: 30,
            ExaminationType.ELECTROCARDIOGRAM: 15,
            ExaminationType.ULTRASOUND: 20,
            ExaminationType.ENDOSCOPY: 60,
            ExaminationType.PATHOLOGICAL_EXAMINATION: 45,
            ExaminationType.GENETIC_TESTING: 30
        }
        return duration_map.get(examination_type, 30)
    
    async def create_food_therapy_plan(self, user_id: str, syndrome_type: SyndromeType = None) -> Dict[str, Any]:
        """制定食疗方案"""
        try:
            profile = self.patient_profiles.get(user_id)
            if not profile:
                return {
                    "success": False,
                    "message": "患者档案不存在"
                }
            
            # 获取食疗方案
            food_plan = await self.food_service.get_personalized_food_therapy_plan(
                constitution_type=profile.constitution_type,
                symptoms=profile.current_symptoms,
                allergies=profile.allergies,
                age=profile.age,
                gender=profile.gender
            )
            
            if not food_plan["success"]:
                return food_plan
            
            # 添加个性化调整
            personalized_plan = food_plan["plan"]
            
            # 基于BMI调整
            bmi = profile.weight / ((profile.height / 100) ** 2)
            if bmi > 25:
                personalized_plan["weight_management"] = {
                    "target": "减重",
                    "recommended_foods": ["冬瓜", "薏米", "山楂", "荷叶"],
                    "avoid_foods": ["高糖食物", "油腻食物", "精制碳水化合物"]
                }
            elif bmi < 18.5:
                personalized_plan["weight_management"] = {
                    "target": "增重",
                    "recommended_foods": ["山药", "大枣", "桂圆", "核桃"],
                    "avoid_foods": ["生冷食物", "过度节食"]
                }
            
            # 基于年龄调整
            if profile.age > 60:
                personalized_plan["elderly_care"] = {
                    "focus": "补肾养血",
                    "recommended_foods": ["黑芝麻", "核桃", "枸杞", "黑豆"],
                    "cooking_methods": ["炖煮", "蒸制", "煮粥"]
                }
            
            logger.info(f"食疗方案制定完成: {user_id}")
            return {
                "success": True,
                "food_therapy_plan": personalized_plan
            }
            
        except Exception as e:
            logger.error(f"制定食疗方案失败: {e}")
            return {
                "success": False,
                "message": f"制定食疗方案失败: {str(e)}"
            }
    
    async def create_rehabilitation_plan(self, user_id: str, 
                                       rehabilitation_types: List[RehabilitationType] = None) -> Dict[str, Any]:
        """制定康复方案"""
        try:
            profile = self.patient_profiles.get(user_id)
            if not profile:
                return {
                    "success": False,
                    "message": "患者档案不存在"
                }
            
            # 如果没有指定康复类型，基于体质推荐
            if not rehabilitation_types:
                constitution_mapping = self.constitution_treatment_mapping.get(profile.constitution_type, {})
                rehabilitation_types = constitution_mapping.get("rehabilitation_types", [RehabilitationType.EXERCISE_THERAPY])
            
            rehabilitation_plan = {
                "patient_id": user_id,
                "constitution_type": profile.constitution_type.value,
                "rehabilitation_programs": []
            }
            
            for rehab_type in rehabilitation_types:
                template = self.rehabilitation_templates.get(rehab_type, {})
                
                # 基于患者情况调整方案
                program = {
                    "type": rehab_type.value,
                    "description": template.get("description", ""),
                    "treatment_methods": template.get("treatment_methods", []),
                    "duration_weeks": template.get("duration_weeks", 8),
                    "frequency": template.get("frequency", "每周2次"),
                    "expected_outcomes": template.get("expected_outcomes", [])
                }
                
                # 基于年龄调整
                if profile.age > 65:
                    program["special_considerations"] = ["低强度训练", "安全防护", "循序渐进"]
                    program["duration_weeks"] = min(program["duration_weeks"] + 2, 16)
                
                # 基于症状调整
                if "疼痛" in profile.current_symptoms:
                    program["pain_management"] = ["热敷", "冷敷", "止痛药物配合"]
                
                rehabilitation_plan["rehabilitation_programs"].append(program)
            
            # 搜索康复资源
            rehab_resources = await self.resource_service.search_resources(
                resource_category=ResourceCategory.MODERN_MEDICAL_INSTITUTION,
                constitution_type=profile.constitution_type,
                symptoms=profile.current_symptoms,
                location={"latitude": 39.9042, "longitude": 116.4074},  # 默认位置
                max_distance_km=50.0,
                max_price=1000.0,
                availability_required=True
            )
            
            rehabilitation_plan["available_resources"] = rehab_resources[:5]  # 前5个资源
            
            logger.info(f"康复方案制定完成: {user_id}")
            return {
                "success": True,
                "rehabilitation_plan": rehabilitation_plan
            }
            
        except Exception as e:
            logger.error(f"制定康复方案失败: {e}")
            return {
                "success": False,
                "message": f"制定康复方案失败: {str(e)}"
            }
    
    async def create_comprehensive_treatment_plan(self, user_id: str, 
                                                symptoms: List[str],
                                                treatment_preferences: List[TreatmentApproach] = None) -> Dict[str, Any]:
        """制定综合治疗方案"""
        try:
            profile = self.patient_profiles.get(user_id)
            if not profile:
                return {
                    "success": False,
                    "message": "患者档案不存在"
                }
            
            plan_id = str(uuid.uuid4())
            
            # 更新患者症状
            profile.current_symptoms = symptoms
            profile.updated_at = datetime.now()
            
            # 确定治疗方法
            if not treatment_preferences:
                constitution_mapping = self.constitution_treatment_mapping.get(profile.constitution_type, {})
                primary_approach = constitution_mapping.get("primary_approach", TreatmentApproach.INTEGRATED_THERAPY)
                treatment_preferences = [primary_approach] + constitution_mapping.get("recommended_treatments", [])
            
            # 证候分析
            syndrome_analysis = None
            if TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION in treatment_preferences:
                syndrome_result = await self.analyze_syndrome(user_id, symptoms)
                if syndrome_result["success"]:
                    syndrome_data = syndrome_result["syndrome_analysis"]
                    syndrome_analysis = SyndromeAnalysis(
                        syndrome_type=SyndromeType(syndrome_data["syndrome_type"]),
                        confidence_score=syndrome_data["confidence_score"],
                        primary_symptoms=syndrome_data["primary_symptoms"],
                        secondary_symptoms=syndrome_data["secondary_symptoms"],
                        tongue_diagnosis={},
                        pulse_diagnosis={},
                        treatment_principles=syndrome_data["treatment_principles"],
                        recommended_formulas=syndrome_data["recommended_formulas"]
                    )
            
            # 检查推荐
            examination_recommendations = []
            if TreatmentApproach.MODERN_MEDICAL_EXAMINATION in treatment_preferences:
                exam_result = await self.recommend_examinations(user_id, symptoms)
                if exam_result["success"]:
                    for rec_data in exam_result["recommendations"]:
                        recommendation = ExaminationRecommendation(
                            examination_type=ExaminationType(rec_data["examination_type"]),
                            examination_name=rec_data["examination_name"],
                            priority_level=UrgencyLevel(rec_data["priority_level"]),
                            reason=rec_data["reason"],
                            expected_findings=[],
                            preparation_instructions=[],
                            estimated_cost=rec_data["estimated_cost"],
                            estimated_duration=rec_data["estimated_duration"]
                        )
                        examination_recommendations.append(recommendation)
            
            # 食疗方案
            food_therapy_plan = None
            if TreatmentApproach.FOOD_THERAPY in treatment_preferences:
                food_result = await self.create_food_therapy_plan(
                    user_id, 
                    syndrome_analysis.syndrome_type if syndrome_analysis else None
                )
                if food_result["success"]:
                    food_therapy_plan = food_result["food_therapy_plan"]
            
            # 康复方案
            rehabilitation_plan = None
            if TreatmentApproach.REHABILITATION in treatment_preferences:
                rehab_result = await self.create_rehabilitation_plan(user_id)
                if rehab_result["success"]:
                    rehabilitation_plan = rehab_result["rehabilitation_plan"]
            
            # 计算总费用和时长
            estimated_total_cost = 0.0
            estimated_duration_weeks = 4  # 默认4周
            
            if examination_recommendations:
                estimated_total_cost += sum(rec.estimated_cost for rec in examination_recommendations)
            
            if syndrome_analysis:
                estimated_total_cost += 500.0  # 中医诊疗费用
                estimated_duration_weeks = max(estimated_duration_weeks, 6)
            
            if rehabilitation_plan:
                estimated_total_cost += 2000.0  # 康复费用
                estimated_duration_weeks = max(estimated_duration_weeks, 8)
            
            # 生活方式建议
            lifestyle_recommendations = self._generate_lifestyle_recommendations(profile, syndrome_analysis)
            
            # 随访计划
            follow_up_schedule = self._generate_follow_up_schedule(treatment_preferences, estimated_duration_weeks)
            
            # 创建治疗方案
            treatment_plan = TreatmentPlan(
                plan_id=plan_id,
                patient_id=user_id,
                treatment_approach=treatment_preferences[0] if treatment_preferences else TreatmentApproach.INTEGRATED_THERAPY,
                syndrome_analysis=syndrome_analysis,
                examination_recommendations=examination_recommendations,
                food_therapy_plan=food_therapy_plan,
                rehabilitation_plan=rehabilitation_plan,
                medication_recommendations=[],
                lifestyle_recommendations=lifestyle_recommendations,
                follow_up_schedule=follow_up_schedule,
                estimated_duration_weeks=estimated_duration_weeks,
                estimated_total_cost=estimated_total_cost
            )
            
            self.treatment_plans[plan_id] = treatment_plan
            
            logger.info(f"综合治疗方案制定完成: {user_id} - {plan_id}")
            return {
                "success": True,
                "treatment_plan": {
                    "plan_id": plan_id,
                    "patient_id": user_id,
                    "treatment_approach": treatment_plan.treatment_approach.value,
                    "syndrome_analysis": syndrome_analysis.__dict__ if syndrome_analysis else None,
                    "examination_recommendations": [rec.__dict__ for rec in examination_recommendations],
                    "food_therapy_plan": food_therapy_plan,
                    "rehabilitation_plan": rehabilitation_plan,
                    "lifestyle_recommendations": lifestyle_recommendations,
                    "follow_up_schedule": follow_up_schedule,
                    "estimated_duration_weeks": estimated_duration_weeks,
                    "estimated_total_cost": estimated_total_cost,
                    "created_at": treatment_plan.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"制定综合治疗方案失败: {e}")
            return {
                "success": False,
                "message": f"制定综合治疗方案失败: {str(e)}"
            }
    
    def _generate_lifestyle_recommendations(self, profile: PatientProfile, 
                                          syndrome_analysis: SyndromeAnalysis = None) -> List[str]:
        """生成生活方式建议"""
        recommendations = []
        
        # 基于体质的建议
        constitution_advice = {
            ConstitutionType.QI_DEFICIENCY: [
                "规律作息，避免熬夜",
                "适量运动，如散步、太极拳",
                "保持心情愉悦，避免过度劳累"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "注意保暖，避免受寒",
                "多晒太阳，适当温补",
                "避免生冷食物"
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                "避免熬夜，保证充足睡眠",
                "多饮水，保持室内湿度",
                "避免辛辣燥热食物"
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                "控制体重，增加运动",
                "饮食清淡，少油少盐",
                "保持环境干燥通风"
            ]
        }
        
        recommendations.extend(constitution_advice.get(profile.constitution_type, []))
        
        # 基于年龄的建议
        if profile.age > 60:
            recommendations.extend([
                "定期体检，监测慢性病指标",
                "适当补钙，预防骨质疏松",
                "保持社交活动，预防抑郁"
            ])
        
        # 基于症状的建议
        if "失眠" in profile.current_symptoms:
            recommendations.append("睡前避免使用电子设备，创造良好睡眠环境")
        
        if "头痛" in profile.current_symptoms:
            recommendations.append("避免长时间用眼，定期休息放松")
        
        return recommendations
    
    def _generate_follow_up_schedule(self, treatment_approaches: List[TreatmentApproach], 
                                   duration_weeks: int) -> List[Dict[str, str]]:
        """生成随访计划"""
        schedule = []
        
        # 第一次随访（1周后）
        schedule.append({
            "time": "1周后",
            "type": "症状评估",
            "content": "评估治疗反应，调整方案"
        })
        
        # 中期随访（4周后）
        schedule.append({
            "time": "4周后",
            "type": "全面评估",
            "content": "评估治疗效果，检查副作用"
        })
        
        # 如果有中医治疗，增加中医随访
        if TreatmentApproach.TCM_SYNDROME_DIFFERENTIATION in treatment_approaches:
            schedule.append({
                "time": "2周后",
                "type": "中医复诊",
                "content": "舌脉诊察，方药调整"
            })
        
        # 如果有康复治疗，增加康复评估
        if TreatmentApproach.REHABILITATION in treatment_approaches:
            schedule.append({
                "time": "6周后",
                "type": "康复评估",
                "content": "功能评估，康复进度检查"
            })
        
        # 结束随访
        schedule.append({
            "time": f"{duration_weeks}周后",
            "type": "治疗总结",
            "content": "总体效果评估，后续建议"
        })
        
        return schedule
    
    async def update_treatment_progress(self, plan_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """更新治疗进展"""
        try:
            plan = self.treatment_plans.get(plan_id)
            if not plan:
                return {
                    "success": False,
                    "message": "治疗方案不存在"
                }
            
            progress = TreatmentProgress(
                progress_id=str(uuid.uuid4()),
                plan_id=plan_id,
                patient_id=plan.patient_id,
                assessment_date=datetime.now(),
                symptom_improvement=progress_data.get("symptom_improvement", {}),
                side_effects=progress_data.get("side_effects", []),
                compliance_rate=progress_data.get("compliance_rate", 0.8),
                objective_measurements=progress_data.get("objective_measurements", {}),
                patient_feedback=progress_data.get("patient_feedback", ""),
                doctor_notes=progress_data.get("doctor_notes", ""),
                next_assessment_date=datetime.now() + timedelta(weeks=2),
                plan_adjustments=progress_data.get("plan_adjustments", [])
            )
            
            self.treatment_progress[plan_id].append(progress)
            
            # 更新治疗方案
            plan.updated_at = datetime.now()
            
            logger.info(f"治疗进展更新完成: {plan_id}")
            return {
                "success": True,
                "message": "治疗进展更新成功",
                "progress_id": progress.progress_id
            }
            
        except Exception as e:
            logger.error(f"更新治疗进展失败: {e}")
            return {
                "success": False,
                "message": f"更新治疗进展失败: {str(e)}"
            }
    
    async def get_treatment_statistics(self, user_id: str = None) -> Dict[str, Any]:
        """获取治疗统计信息"""
        try:
            stats = {
                "total_patients": len(self.patient_profiles),
                "total_treatment_plans": len(self.treatment_plans),
                "constitution_distribution": {},
                "treatment_approach_distribution": {},
                "syndrome_distribution": {},
                "average_treatment_duration": 0.0,
                "average_treatment_cost": 0.0,
                "treatment_effectiveness": {}
            }
            
            # 体质分布
            constitution_counts = defaultdict(int)
            for profile in self.patient_profiles.values():
                constitution_counts[profile.constitution_type.value] += 1
            stats["constitution_distribution"] = dict(constitution_counts)
            
            # 治疗方法分布
            approach_counts = defaultdict(int)
            syndrome_counts = defaultdict(int)
            total_duration = 0
            total_cost = 0
            
            for plan in self.treatment_plans.values():
                if user_id is None or plan.patient_id == user_id:
                    approach_counts[plan.treatment_approach.value] += 1
                    total_duration += plan.estimated_duration_weeks
                    total_cost += plan.estimated_total_cost
                    
                    if plan.syndrome_analysis:
                        syndrome_counts[plan.syndrome_analysis.syndrome_type.value] += 1
            
            stats["treatment_approach_distribution"] = dict(approach_counts)
            stats["syndrome_distribution"] = dict(syndrome_counts)
            
            if len(self.treatment_plans) > 0:
                stats["average_treatment_duration"] = total_duration / len(self.treatment_plans)
                stats["average_treatment_cost"] = total_cost / len(self.treatment_plans)
            
            # 治疗效果统计
            improvement_scores = []
            for progress_list in self.treatment_progress.values():
                if progress_list:
                    latest_progress = progress_list[-1]
                    if user_id is None or latest_progress.patient_id == user_id:
                        avg_improvement = sum(latest_progress.symptom_improvement.values()) / len(latest_progress.symptom_improvement) if latest_progress.symptom_improvement else 0
                        improvement_scores.append(avg_improvement)
            
            if improvement_scores:
                stats["treatment_effectiveness"] = {
                    "average_improvement": sum(improvement_scores) / len(improvement_scores),
                    "improvement_rate": len([s for s in improvement_scores if s > 0.5]) / len(improvement_scores)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取治疗统计信息失败: {e}")
            return {}
    
    async def shutdown(self):
        """关闭个性化医疗服务"""
        try:
            logger.info("个性化医疗服务已关闭")
            
        except Exception as e:
            logger.error(f"关闭个性化医疗服务失败: {e}") 