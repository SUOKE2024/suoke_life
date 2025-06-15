#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能中医体质辨识引擎 - 基于中医理论的体质辨识和个性化调理
结合传统中医体质学说和现代数据分析技术，为用户提供精准的体质辨识和个性化调理方案
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class TCMConstitution(str, Enum):
    """中医体质类型（九种体质）"""
    BALANCED = "balanced"                       # 平和质
    QI_DEFICIENCY = "qi_deficiency"             # 气虚质
    YANG_DEFICIENCY = "yang_deficiency"         # 阳虚质
    YIN_DEFICIENCY = "yin_deficiency"           # 阴虚质
    PHLEGM_DAMPNESS = "phlegm_dampness"         # 痰湿质
    DAMP_HEAT = "damp_heat"                     # 湿热质
    BLOOD_STASIS = "blood_stasis"               # 血瘀质
    QI_STAGNATION = "qi_stagnation"             # 气郁质
    SPECIAL_DIATHESIS = "special_diathesis"     # 特禀质


class ConstitutionSeverity(str, Enum):
    """体质偏颇程度"""
    NONE = "none"                  # 无偏颇
    MILD = "mild"                  # 轻度偏颇
    MODERATE = "moderate"          # 中度偏颇
    SEVERE = "severe"              # 重度偏颇


class SeasonType(str, Enum):
    """季节类型"""
    SPRING = "spring"              # 春季
    SUMMER = "summer"              # 夏季
    AUTUMN = "autumn"              # 秋季
    WINTER = "winter"              # 冬季


class AdjustmentType(str, Enum):
    """调理类型"""
    DIETARY = "dietary"                         # 饮食调理
    LIFESTYLE = "lifestyle"                     # 生活起居
    EXERCISE = "exercise"                       # 运动调理
    EMOTIONAL = "emotional"                     # 情志调理
    HERBAL = "herbal"                          # 中药调理
    ACUPUNCTURE = "acupuncture"                # 针灸调理
    MASSAGE = "massage"                        # 推拿按摩
    SEASONAL = "seasonal"                      # 季节调养


@dataclass
class ConstitutionSymptom:
    """体质症状"""
    symptom_id: str
    name: str
    description: str
    constitution_type: TCMConstitution
    weight: float                               # 权重 (0.0-1.0)
    category: str                               # 症状类别
    severity_mapping: Dict[str, float] = field(default_factory=dict)  # 严重程度映射
    related_organs: List[str] = field(default_factory=list)  # 相关脏腑
    manifestation_areas: List[str] = field(default_factory=list)  # 表现部位


@dataclass
class ConstitutionQuestionnaire:
    """体质问卷"""
    questionnaire_id: str
    name: str
    description: str
    questions: List[Dict[str, Any]] = field(default_factory=list)
    scoring_rules: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    created_date: datetime = field(default_factory=datetime.now)


@dataclass
class ConstitutionAssessment:
    """体质评估结果"""
    user_id: str
    assessment_date: datetime
    primary_constitution: TCMConstitution
    primary_score: float                        # 主要体质得分
    primary_severity: ConstitutionSeverity
    
    # 所有体质得分
    constitution_scores: Dict[TCMConstitution, float] = field(default_factory=dict)
    
    # 次要体质（混合体质）
    secondary_constitutions: List[Tuple[TCMConstitution, float]] = field(default_factory=list)
    
    # 体质特征
    physical_characteristics: List[str] = field(default_factory=list)
    psychological_characteristics: List[str] = field(default_factory=list)
    pathological_tendencies: List[str] = field(default_factory=list)
    
    # 环境适应性
    climate_adaptability: Dict[str, str] = field(default_factory=dict)
    seasonal_variations: Dict[SeasonType, str] = field(default_factory=dict)
    
    # 易感疾病
    susceptible_diseases: List[str] = field(default_factory=list)
    
    # 调理建议
    adjustment_recommendations: List[str] = field(default_factory=list)
    
    # 评估信心度
    confidence_score: float = 0.0
    
    # 问卷回答
    questionnaire_responses: Dict[str, Any] = field(default_factory=dict)
    
    # 评估方法
    assessment_method: str = "questionnaire"
    
    # 下次评估建议时间
    next_assessment_date: Optional[datetime] = None


@dataclass
class ConstitutionAdjustmentPlan:
    """体质调理方案"""
    plan_id: str
    user_id: str
    constitution_assessment: ConstitutionAssessment
    plan_name: str
    description: str
    
    # 调理目标
    adjustment_goals: List[str] = field(default_factory=list)
    
    # 饮食调理
    dietary_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 生活起居
    lifestyle_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 运动调理
    exercise_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 情志调理
    emotional_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 中药调理
    herbal_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 针灸调理
    acupuncture_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 推拿按摩
    massage_recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 季节调养
    seasonal_adjustments: Dict[SeasonType, Dict[str, Any]] = field(default_factory=dict)
    
    # 禁忌事项
    contraindications: List[str] = field(default_factory=list)
    
    # 调理周期
    adjustment_duration: int = 90  # 天数
    
    # 效果评估指标
    evaluation_metrics: List[str] = field(default_factory=list)
    
    # 创建时间
    created_date: datetime = field(default_factory=datetime.now)
    
    # 状态
    status: str = "active"


@dataclass
class ConstitutionProgress:
    """体质调理进展"""
    user_id: str
    plan_id: str
    progress_date: datetime
    
    # 症状改善情况
    symptom_improvements: Dict[str, float] = field(default_factory=dict)
    
    # 体质得分变化
    constitution_score_changes: Dict[TCMConstitution, float] = field(default_factory=dict)
    
    # 生活质量评分
    quality_of_life_score: Optional[float] = None
    
    # 依从性评分
    adherence_score: float = 0.0
    
    # 满意度评分
    satisfaction_score: Optional[float] = None
    
    # 副作用或不适
    adverse_effects: List[str] = field(default_factory=list)
    
    # 调理效果评价
    effectiveness_rating: Optional[str] = None
    
    # 下一步建议
    next_steps: List[str] = field(default_factory=list)


class ConstitutionAnalyzer:
    """体质分析器"""
    
    def __init__(self):
        self.constitution_database = self._load_constitution_database()
        self.symptom_patterns = self._load_symptom_patterns()
        self.questionnaire_templates = self._load_questionnaire_templates()
        self.scoring_algorithms = self._load_scoring_algorithms()
    
    def _load_constitution_database(self) -> Dict[str, Any]:
        """加载体质数据库"""
        return {
            TCMConstitution.BALANCED: {
                "name": "平和质",
                "description": "阴阳气血调和，体态适中，面色红润，精力充沛",
                "characteristics": {
                    "physical": [
                        "体形匀称健壮", "面色润泽", "头发稠密有光泽", "目光有神",
                        "鼻色明润", "嗅觉通利", "唇色红润", "不易疲劳"
                    ],
                    "psychological": [
                        "性格随和开朗", "情绪稳定", "适应能力强", "社交能力好"
                    ],
                    "pathological": [
                        "平素患病较少", "抗病能力较强", "病后恢复较快"
                    ]
                },
                "climate_adaptability": {
                    "cold": "适应良好",
                    "hot": "适应良好",
                    "humid": "适应良好",
                    "dry": "适应良好"
                },
                "susceptible_diseases": [],
                "key_symptoms": []
            },
            TCMConstitution.QI_DEFICIENCY: {
                "name": "气虚质",
                "description": "元气不足，以疲乏、气短、自汗等气虚表现为主要特征",
                "characteristics": {
                    "physical": [
                        "肌肉松软不实", "平素语音低弱", "气短懒言", "容易疲乏",
                        "精神不振", "易出汗", "舌淡红", "舌边有齿痕"
                    ],
                    "psychological": [
                        "性格内向", "情绪不稳定", "胆小不喜冒险"
                    ],
                    "pathological": [
                        "易患感冒", "病后恢复缓慢", "易患内脏下垂等病"
                    ]
                },
                "climate_adaptability": {
                    "cold": "不耐受",
                    "hot": "不耐受",
                    "humid": "不耐受",
                    "wind": "不耐受"
                },
                "susceptible_diseases": [
                    "感冒", "疲劳综合征", "胃下垂", "子宫脱垂", "慢性腹泻"
                ],
                "key_symptoms": [
                    "疲乏无力", "气短", "自汗", "语音低弱", "精神不振"
                ]
            },
            TCMConstitution.YANG_DEFICIENCY: {
                "name": "阳虚质",
                "description": "阳气不足，以畏寒怕冷、手足不温等虚寒表现为主要特征",
                "characteristics": {
                    "physical": [
                        "肌肉松软不实", "平素畏冷", "手足不温", "喜热饮食",
                        "精神不振", "睡眠偏多", "舌淡胖嫩", "脉沉迟"
                    ],
                    "psychological": [
                        "性格多沉静", "情绪低落", "精神不振"
                    ],
                    "pathological": [
                        "易患痰饮", "肿胀", "泄泻等病", "病理上多表现为寒证"
                    ]
                },
                "climate_adaptability": {
                    "cold": "不耐受",
                    "winter": "不适应",
                    "summer": "较适应"
                },
                "susceptible_diseases": [
                    "慢性腹泻", "阳痿", "水肿", "痰饮", "不孕症"
                ],
                "key_symptoms": [
                    "畏寒怕冷", "手足不温", "精神不振", "睡眠偏多", "大便溏薄"
                ]
            },
            TCMConstitution.YIN_DEFICIENCY: {
                "name": "阴虚质",
                "description": "阴液亏少，以口燥咽干、手足心热等虚热表现为主要特征",
                "characteristics": {
                    "physical": [
                        "体形偏瘦", "手足心热", "面颊潮红", "口燥咽干",
                        "喜冷饮", "大便干燥", "舌红少津", "脉细数"
                    ],
                    "psychological": [
                        "性情急躁", "外向好动", "活泼", "情绪易波动"
                    ],
                    "pathological": [
                        "易患虚劳", "失精", "不寐等病", "病理上多表现为热证"
                    ]
                },
                "climate_adaptability": {
                    "hot": "不耐受",
                    "dry": "不耐受",
                    "summer": "不适应",
                    "autumn": "较适应"
                },
                "susceptible_diseases": [
                    "失眠", "便秘", "更年期综合征", "甲亢", "糖尿病"
                ],
                "key_symptoms": [
                    "手足心热", "口燥咽干", "面颊潮红", "眼干", "皮肤干燥"
                ]
            },
            TCMConstitution.PHLEGM_DAMPNESS: {
                "name": "痰湿质",
                "description": "痰湿凝聚，以形体肥胖、腹部肥满、口黏苔腻等痰湿表现为主要特征",
                "characteristics": {
                    "physical": [
                        "体形肥胖", "腹部肥满松软", "面部皮肤油脂较多",
                        "多汗且黏", "胸闷", "痰多", "舌体胖大", "苔白腻"
                    ],
                    "psychological": [
                        "性格偏温和", "稳重恭谦", "多善忍耐"
                    ],
                    "pathological": [
                        "易患消渴", "中风", "胸痹等病"
                    ]
                },
                "climate_adaptability": {
                    "humid": "不耐受",
                    "rainy": "不适应"
                },
                "susceptible_diseases": [
                    "糖尿病", "高血压", "高血脂", "冠心病", "脂肪肝"
                ],
                "key_symptoms": [
                    "形体肥胖", "腹部肥满", "胸闷", "痰多", "身重不爽"
                ]
            },
            TCMConstitution.DAMP_HEAT: {
                "name": "湿热质",
                "description": "湿热内蕴，以面垢油腻、口苦、苔黄腻等湿热表现为主要特征",
                "characteristics": {
                    "physical": [
                        "面垢油腻", "易生痤疮", "口苦口干", "身重困倦",
                        "大便黏滞", "小便短赤", "舌质偏红", "苔黄腻"
                    ],
                    "psychological": [
                        "容易心烦急躁"
                    ],
                    "pathological": [
                        "易患疮疖", "黄疸", "火热等病"
                    ]
                },
                "climate_adaptability": {
                    "humid": "不耐受",
                    "hot_humid": "不耐受"
                },
                "susceptible_diseases": [
                    "痤疮", "湿疹", "泌尿系感染", "带下病", "胆囊炎"
                ],
                "key_symptoms": [
                    "面垢油腻", "口苦", "身重困倦", "大便黏滞", "小便短赤"
                ]
            },
            TCMConstitution.BLOOD_STASIS: {
                "name": "血瘀质",
                "description": "血行不畅，以肤色晦暗、舌质紫暗等血瘀表现为主要特征",
                "characteristics": {
                    "physical": [
                        "肤色晦暗", "色素沉着", "容易出现瘀斑", "口唇暗淡",
                        "舌暗或有瘀点", "舌下络脉紫暗", "脉涩"
                    ],
                    "psychological": [
                        "易烦", "健忘"
                    ],
                    "pathological": [
                        "易患症瘕", "痛证", "血证等病"
                    ]
                },
                "climate_adaptability": {
                    "cold": "不耐受"
                },
                "susceptible_diseases": [
                    "冠心病", "脑血管病", "肿瘤", "痛经", "子宫肌瘤"
                ],
                "key_symptoms": [
                    "肤色晦暗", "口唇暗淡", "易出现瘀斑", "疼痛如针刺", "健忘"
                ]
            },
            TCMConstitution.QI_STAGNATION: {
                "name": "气郁质",
                "description": "气机郁滞，以神情抑郁、忧虑脆弱等气郁表现为主要特征",
                "characteristics": {
                    "physical": [
                        "神情抑郁", "情感脆弱", "烦闷不乐", "舌淡红",
                        "苔薄白", "脉弦"
                    ],
                    "psychological": [
                        "性格内向不稳定", "敏感多虑", "忧郁脆弱",
                        "对精神刺激适应能力较差"
                    ],
                    "pathological": [
                        "易患脏躁", "梅核气", "百合病等病"
                    ]
                },
                "climate_adaptability": {
                    "rainy": "不适应",
                    "cloudy": "不适应"
                },
                "susceptible_diseases": [
                    "抑郁症", "焦虑症", "失眠", "乳腺增生", "甲状腺结节"
                ],
                "key_symptoms": [
                    "神情抑郁", "情感脆弱", "胸胁胀满", "善太息", "易惊易怒"
                ]
            },
            TCMConstitution.SPECIAL_DIATHESIS: {
                "name": "特禀质",
                "description": "先天失常，以生理缺陷、过敏反应等为主要特征",
                "characteristics": {
                    "physical": [
                        "过敏体质者常见哮喘", "风团", "咽痒", "鼻塞",
                        "喷嚏等", "患遗传性疾病者有垂直遗传", "先天性家族性特征"
                    ],
                    "psychological": [
                        "随禀质不同情况各异"
                    ],
                    "pathological": [
                        "易患过敏性疾病", "遗传性疾病", "胎传性疾病"
                    ]
                },
                "climate_adaptability": {
                    "allergen_season": "不耐受"
                },
                "susceptible_diseases": [
                    "哮喘", "过敏性鼻炎", "荨麻疹", "药物过敏", "遗传性疾病"
                ],
                "key_symptoms": [
                    "过敏反应", "哮喘", "皮肤过敏", "鼻塞流涕", "遗传性症状"
                ]
            }
        }
    
    def _load_symptom_patterns(self) -> Dict[str, Any]:
        """加载症状模式"""
        return {
            "questionnaire_symptoms": {
                # 气虚质症状
                "qi_deficiency": [
                    {"id": "fatigue", "question": "您是否经常感到疲乏无力？", "weight": 0.25},
                    {"id": "shortness_of_breath", "question": "您是否容易气短？", "weight": 0.2},
                    {"id": "spontaneous_sweating", "question": "您是否容易出汗？", "weight": 0.15},
                    {"id": "low_voice", "question": "您说话声音是否低弱？", "weight": 0.1},
                    {"id": "poor_spirit", "question": "您是否精神不振？", "weight": 0.15},
                    {"id": "pale_tongue", "question": "您的舌质是否淡红？", "weight": 0.1},
                    {"id": "tooth_marks", "question": "您的舌边是否有齿痕？", "weight": 0.05}
                ],
                # 阳虚质症状
                "yang_deficiency": [
                    {"id": "cold_limbs", "question": "您的手足是否经常不温？", "weight": 0.3},
                    {"id": "fear_cold", "question": "您是否畏寒怕冷？", "weight": 0.25},
                    {"id": "prefer_hot_drinks", "question": "您是否喜欢热饮？", "weight": 0.15},
                    {"id": "poor_spirit", "question": "您是否精神不振？", "weight": 0.1},
                    {"id": "sleepy", "question": "您是否睡眠偏多？", "weight": 0.1},
                    {"id": "loose_stool", "question": "您的大便是否偏稀？", "weight": 0.1}
                ],
                # 阴虚质症状
                "yin_deficiency": [
                    {"id": "hot_palms", "question": "您的手足心是否发热？", "weight": 0.25},
                    {"id": "dry_mouth", "question": "您是否口燥咽干？", "weight": 0.2},
                    {"id": "flushed_cheeks", "question": "您的面颊是否潮红？", "weight": 0.15},
                    {"id": "prefer_cold_drinks", "question": "您是否喜欢冷饮？", "weight": 0.1},
                    {"id": "dry_stool", "question": "您的大便是否干燥？", "weight": 0.15},
                    {"id": "red_tongue", "question": "您的舌质是否偏红？", "weight": 0.1},
                    {"id": "little_saliva", "question": "您的舌津是否偏少？", "weight": 0.05}
                ],
                # 痰湿质症状
                "phlegm_dampness": [
                    {"id": "obesity", "question": "您的体形是否肥胖？", "weight": 0.3},
                    {"id": "abdominal_fullness", "question": "您的腹部是否肥满？", "weight": 0.2},
                    {"id": "oily_face", "question": "您的面部皮肤是否油腻？", "weight": 0.15},
                    {"id": "sticky_sweat", "question": "您出汗是否黏腻？", "weight": 0.1},
                    {"id": "chest_tightness", "question": "您是否胸闷？", "weight": 0.1},
                    {"id": "phlegm", "question": "您是否痰多？", "weight": 0.1},
                    {"id": "fat_tongue", "question": "您的舌体是否胖大？", "weight": 0.05}
                ],
                # 湿热质症状
                "damp_heat": [
                    {"id": "oily_dirty_face", "question": "您的面部是否垢腻？", "weight": 0.2},
                    {"id": "acne", "question": "您是否容易生痤疮？", "weight": 0.15},
                    {"id": "bitter_mouth", "question": "您是否口苦？", "weight": 0.2},
                    {"id": "heavy_body", "question": "您是否身重困倦？", "weight": 0.15},
                    {"id": "sticky_stool", "question": "您的大便是否黏滞？", "weight": 0.15},
                    {"id": "yellow_urine", "question": "您的小便是否短赤？", "weight": 0.1},
                    {"id": "yellow_coating", "question": "您的舌苔是否黄腻？", "weight": 0.05}
                ],
                # 血瘀质症状
                "blood_stasis": [
                    {"id": "dark_complexion", "question": "您的肤色是否晦暗？", "weight": 0.25},
                    {"id": "pigmentation", "question": "您是否容易色素沉着？", "weight": 0.15},
                    {"id": "bruises", "question": "您是否容易出现瘀斑？", "weight": 0.2},
                    {"id": "dark_lips", "question": "您的口唇是否暗淡？", "weight": 0.15},
                    {"id": "forgetful", "question": "您是否健忘？", "weight": 0.1},
                    {"id": "dark_tongue", "question": "您的舌质是否暗或有瘀点？", "weight": 0.1},
                    {"id": "purple_vessels", "question": "您的舌下络脉是否紫暗？", "weight": 0.05}
                ],
                # 气郁质症状
                "qi_stagnation": [
                    {"id": "depressed", "question": "您是否神情抑郁？", "weight": 0.3},
                    {"id": "emotional_fragile", "question": "您是否情感脆弱？", "weight": 0.2},
                    {"id": "chest_fullness", "question": "您是否胸胁胀满？", "weight": 0.15},
                    {"id": "sighing", "question": "您是否善太息？", "weight": 0.15},
                    {"id": "easily_startled", "question": "您是否易惊易怒？", "weight": 0.1},
                    {"id": "insomnia", "question": "您是否失眠多梦？", "weight": 0.1}
                ],
                # 特禀质症状
                "special_diathesis": [
                    {"id": "allergic_reactions", "question": "您是否容易过敏？", "weight": 0.3},
                    {"id": "asthma", "question": "您是否有哮喘？", "weight": 0.25},
                    {"id": "skin_allergy", "question": "您是否皮肤容易过敏？", "weight": 0.2},
                    {"id": "nasal_congestion", "question": "您是否鼻塞流涕？", "weight": 0.15},
                    {"id": "hereditary_disease", "question": "您是否有遗传性疾病？", "weight": 0.1}
                ]
            }
        }
    
    def _load_questionnaire_templates(self) -> Dict[str, Any]:
        """加载问卷模板"""
        return {
            "standard_constitution_questionnaire": {
                "name": "中医体质量表-60",
                "description": "标准化中医体质辨识问卷",
                "total_questions": 60,
                "constitution_questions": {
                    TCMConstitution.BALANCED: list(range(1, 9)),
                    TCMConstitution.QI_DEFICIENCY: list(range(9, 17)),
                    TCMConstitution.YANG_DEFICIENCY: list(range(17, 25)),
                    TCMConstitution.YIN_DEFICIENCY: list(range(25, 33)),
                    TCMConstitution.PHLEGM_DAMPNESS: list(range(33, 41)),
                    TCMConstitution.DAMP_HEAT: list(range(41, 47)),
                    TCMConstitution.BLOOD_STASIS: list(range(47, 54)),
                    TCMConstitution.QI_STAGNATION: list(range(54, 61)),
                    TCMConstitution.SPECIAL_DIATHESIS: list(range(61, 69))
                },
                "scoring_method": "likert_5_point"
            },
            "simplified_constitution_questionnaire": {
                "name": "简化体质问卷",
                "description": "快速体质辨识问卷",
                "total_questions": 27,
                "constitution_questions": {
                    TCMConstitution.QI_DEFICIENCY: list(range(1, 4)),
                    TCMConstitution.YANG_DEFICIENCY: list(range(4, 7)),
                    TCMConstitution.YIN_DEFICIENCY: list(range(7, 10)),
                    TCMConstitution.PHLEGM_DAMPNESS: list(range(10, 13)),
                    TCMConstitution.DAMP_HEAT: list(range(13, 16)),
                    TCMConstitution.BLOOD_STASIS: list(range(16, 19)),
                    TCMConstitution.QI_STAGNATION: list(range(19, 22)),
                    TCMConstitution.SPECIAL_DIATHESIS: list(range(22, 25)),
                    TCMConstitution.BALANCED: list(range(25, 28))
                },
                "scoring_method": "likert_3_point"
            }
        }
    
    def _load_scoring_algorithms(self) -> Dict[str, Any]:
        """加载评分算法"""
        return {
            "standard_scoring": {
                "method": "weighted_sum",
                "scale": "1-5",
                "thresholds": {
                    "balanced": {"min": 60, "max": 100},
                    "tendency": {"min": 40, "max": 59},
                    "obvious": {"min": 30, "max": 39},
                    "none": {"min": 0, "max": 29}
                }
            },
            "normalized_scoring": {
                "method": "percentage",
                "scale": "0-100",
                "thresholds": {
                    "primary": {"min": 60},
                    "secondary": {"min": 40},
                    "mild": {"min": 30}
                }
            }
        }
    
    @trace_operation("constitution_analyzer.analyze_constitution", SpanKind.INTERNAL)
    async def analyze_constitution(
        self,
        user_id: str,
        questionnaire_responses: Dict[str, Any],
        assessment_method: str = "questionnaire"
    ) -> ConstitutionAssessment:
        """分析体质"""
        
        try:
            # 计算各体质得分
            constitution_scores = await self._calculate_constitution_scores(questionnaire_responses)
            
            # 确定主要体质
            primary_constitution, primary_score = self._determine_primary_constitution(constitution_scores)
            
            # 确定体质偏颇程度
            primary_severity = self._determine_constitution_severity(primary_score)
            
            # 识别次要体质
            secondary_constitutions = self._identify_secondary_constitutions(constitution_scores, primary_constitution)
            
            # 获取体质特征
            characteristics = self._get_constitution_characteristics(primary_constitution)
            
            # 分析环境适应性
            climate_adaptability = self._analyze_climate_adaptability(primary_constitution)
            seasonal_variations = self._analyze_seasonal_variations(primary_constitution)
            
            # 识别易感疾病
            susceptible_diseases = self._identify_susceptible_diseases(primary_constitution, secondary_constitutions)
            
            # 生成调理建议
            adjustment_recommendations = await self._generate_adjustment_recommendations(
                primary_constitution, primary_severity, secondary_constitutions
            )
            
            # 计算评估信心度
            confidence_score = self._calculate_confidence_score(constitution_scores, questionnaire_responses)
            
            # 计算下次评估时间
            next_assessment_date = self._calculate_next_assessment_date(primary_severity)
            
            return ConstitutionAssessment(
                user_id=user_id,
                assessment_date=datetime.now(),
                primary_constitution=primary_constitution,
                primary_score=primary_score,
                primary_severity=primary_severity,
                constitution_scores=constitution_scores,
                secondary_constitutions=secondary_constitutions,
                physical_characteristics=characteristics["physical"],
                psychological_characteristics=characteristics["psychological"],
                pathological_tendencies=characteristics["pathological"],
                climate_adaptability=climate_adaptability,
                seasonal_variations=seasonal_variations,
                susceptible_diseases=susceptible_diseases,
                adjustment_recommendations=adjustment_recommendations,
                confidence_score=confidence_score,
                questionnaire_responses=questionnaire_responses,
                assessment_method=assessment_method,
                next_assessment_date=next_assessment_date
            )
            
        except Exception as e:
            logger.error(f"体质分析失败: {e}")
            raise
    
    async def _calculate_constitution_scores(self, responses: Dict[str, Any]) -> Dict[TCMConstitution, float]:
        """计算各体质得分"""
        scores = {}
        
        # 获取症状模式
        symptom_patterns = self.symptom_patterns["questionnaire_symptoms"]
        
        for constitution in TCMConstitution:
            if constitution == TCMConstitution.BALANCED:
                # 平和质特殊计算
                scores[constitution] = await self._calculate_balanced_score(responses)
            else:
                # 其他体质计算
                constitution_key = constitution.value
                if constitution_key in symptom_patterns:
                    symptoms = symptom_patterns[constitution_key]
                    total_score = 0.0
                    total_weight = 0.0
                    
                    for symptom in symptoms:
                        symptom_id = symptom["id"]
                        weight = symptom["weight"]
                        
                        if symptom_id in responses:
                            # 假设回答是1-5分制
                            response_score = responses[symptom_id]
                            weighted_score = response_score * weight
                            total_score += weighted_score
                            total_weight += weight
                    
                    # 标准化得分到0-100
                    if total_weight > 0:
                        normalized_score = (total_score / total_weight) * 20  # 5分制转100分制
                        scores[constitution] = min(100.0, max(0.0, normalized_score))
                    else:
                        scores[constitution] = 0.0
                else:
                    scores[constitution] = 0.0
        
        return scores
    
    async def _calculate_balanced_score(self, responses: Dict[str, Any]) -> float:
        """计算平和质得分"""
        # 平和质得分 = 100 - 其他体质偏颇程度的平均值
        other_scores = []
        
        # 计算其他体质的偏颇程度
        for constitution in TCMConstitution:
            if constitution != TCMConstitution.BALANCED:
                constitution_key = constitution.value
                if constitution_key in self.symptom_patterns["questionnaire_symptoms"]:
                    symptoms = self.symptom_patterns["questionnaire_symptoms"][constitution_key]
                    total_score = 0.0
                    total_weight = 0.0
                    
                    for symptom in symptoms:
                        symptom_id = symptom["id"]
                        weight = symptom["weight"]
                        
                        if symptom_id in responses:
                            response_score = responses[symptom_id]
                            weighted_score = response_score * weight
                            total_score += weighted_score
                            total_weight += weight
                    
                    if total_weight > 0:
                        normalized_score = (total_score / total_weight) * 20
                        other_scores.append(normalized_score)
        
        if other_scores:
            avg_other_score = sum(other_scores) / len(other_scores)
            balanced_score = max(0.0, 100.0 - avg_other_score)
        else:
            balanced_score = 80.0  # 默认值
        
        return balanced_score
    
    def _determine_primary_constitution(self, scores: Dict[TCMConstitution, float]) -> Tuple[TCMConstitution, float]:
        """确定主要体质"""
        max_score = 0.0
        primary_constitution = TCMConstitution.BALANCED
        
        for constitution, score in scores.items():
            if score > max_score:
                max_score = score
                primary_constitution = constitution
        
        return primary_constitution, max_score
    
    def _determine_constitution_severity(self, score: float) -> ConstitutionSeverity:
        """确定体质偏颇程度"""
        if score >= 70:
            return ConstitutionSeverity.NONE
        elif score >= 50:
            return ConstitutionSeverity.MILD
        elif score >= 30:
            return ConstitutionSeverity.MODERATE
        else:
            return ConstitutionSeverity.SEVERE
    
    def _identify_secondary_constitutions(
        self,
        scores: Dict[TCMConstitution, float],
        primary_constitution: TCMConstitution
    ) -> List[Tuple[TCMConstitution, float]]:
        """识别次要体质"""
        secondary = []
        
        for constitution, score in scores.items():
            if constitution != primary_constitution and score >= 40:
                secondary.append((constitution, score))
        
        # 按得分排序
        secondary.sort(key=lambda x: x[1], reverse=True)
        
        # 最多返回2个次要体质
        return secondary[:2]
    
    def _get_constitution_characteristics(self, constitution: TCMConstitution) -> Dict[str, List[str]]:
        """获取体质特征"""
        constitution_data = self.constitution_database.get(constitution, {})
        return constitution_data.get("characteristics", {
            "physical": [],
            "psychological": [],
            "pathological": []
        })
    
    def _analyze_climate_adaptability(self, constitution: TCMConstitution) -> Dict[str, str]:
        """分析气候适应性"""
        constitution_data = self.constitution_database.get(constitution, {})
        return constitution_data.get("climate_adaptability", {})
    
    def _analyze_seasonal_variations(self, constitution: TCMConstitution) -> Dict[SeasonType, str]:
        """分析季节变化"""
        # 基于中医理论的季节适应性
        seasonal_patterns = {
            TCMConstitution.QI_DEFICIENCY: {
                SeasonType.SPRING: "需要温补阳气",
                SeasonType.SUMMER: "相对较好",
                SeasonType.AUTUMN: "需要润燥养阴",
                SeasonType.WINTER: "需要温阳补气"
            },
            TCMConstitution.YANG_DEFICIENCY: {
                SeasonType.SPRING: "需要助阳升发",
                SeasonType.SUMMER: "最适宜季节",
                SeasonType.AUTUMN: "需要温阳防寒",
                SeasonType.WINTER: "最不适宜，需要重点温阳"
            },
            TCMConstitution.YIN_DEFICIENCY: {
                SeasonType.SPRING: "需要滋阴润燥",
                SeasonType.SUMMER: "最不适宜，需要清热滋阴",
                SeasonType.AUTUMN: "最适宜季节",
                SeasonType.WINTER: "需要滋阴潜阳"
            },
            TCMConstitution.PHLEGM_DAMPNESS: {
                SeasonType.SPRING: "需要健脾化湿",
                SeasonType.SUMMER: "需要清热化湿",
                SeasonType.AUTUMN: "需要燥湿化痰",
                SeasonType.WINTER: "需要温阳化湿"
            },
            TCMConstitution.DAMP_HEAT: {
                SeasonType.SPRING: "需要疏肝清热",
                SeasonType.SUMMER: "最不适宜，需要清热利湿",
                SeasonType.AUTUMN: "需要清热润燥",
                SeasonType.WINTER: "相对较好"
            },
            TCMConstitution.BLOOD_STASIS: {
                SeasonType.SPRING: "需要疏肝活血",
                SeasonType.SUMMER: "需要清热活血",
                SeasonType.AUTUMN: "需要润燥活血",
                SeasonType.WINTER: "最不适宜，需要温阳活血"
            },
            TCMConstitution.QI_STAGNATION: {
                SeasonType.SPRING: "最适宜季节，疏肝理气",
                SeasonType.SUMMER: "需要清心安神",
                SeasonType.AUTUMN: "需要疏肝解郁",
                SeasonType.WINTER: "需要温阳理气"
            },
            TCMConstitution.SPECIAL_DIATHESIS: {
                SeasonType.SPRING: "注意花粉过敏",
                SeasonType.SUMMER: "注意湿热过敏",
                SeasonType.AUTUMN: "注意干燥过敏",
                SeasonType.WINTER: "注意寒冷过敏"
            }
        }
        
        return seasonal_patterns.get(constitution, {})
    
    def _identify_susceptible_diseases(
        self,
        primary_constitution: TCMConstitution,
        secondary_constitutions: List[Tuple[TCMConstitution, float]]
    ) -> List[str]:
        """识别易感疾病"""
        diseases = []
        
        # 主要体质的易感疾病
        primary_data = self.constitution_database.get(primary_constitution, {})
        diseases.extend(primary_data.get("susceptible_diseases", []))
        
        # 次要体质的易感疾病
        for constitution, score in secondary_constitutions:
            if score >= 50:  # 只考虑得分较高的次要体质
                secondary_data = self.constitution_database.get(constitution, {})
                diseases.extend(secondary_data.get("susceptible_diseases", []))
        
        # 去重并返回
        return list(set(diseases))
    
    async def _generate_adjustment_recommendations(
        self,
        primary_constitution: TCMConstitution,
        severity: ConstitutionSeverity,
        secondary_constitutions: List[Tuple[TCMConstitution, float]]
    ) -> List[str]:
        """生成调理建议"""
        recommendations = []
        
        # 基于主要体质的基础建议
        base_recommendations = {
            TCMConstitution.QI_DEFICIENCY: [
                "适当进行有氧运动，如散步、太极拳",
                "多食用补气食物，如黄芪、人参、山药",
                "保证充足睡眠，避免过度劳累",
                "保持心情愉快，避免过度思虑"
            ],
            TCMConstitution.YANG_DEFICIENCY: [
                "注意保暖，避免受寒",
                "多食用温阳食物，如羊肉、生姜、肉桂",
                "适当进行温和运动，避免大汗淋漓",
                "早睡早起，顺应自然规律"
            ],
            TCMConstitution.YIN_DEFICIENCY: [
                "避免熬夜，保证充足睡眠",
                "多食用滋阴食物，如银耳、百合、枸杞",
                "避免剧烈运动，选择瑜伽、太极等",
                "保持情绪稳定，避免急躁"
            ],
            TCMConstitution.PHLEGM_DAMPNESS: [
                "控制体重，适当减肥",
                "少食肥甘厚腻，多食清淡食物",
                "加强运动，促进新陈代谢",
                "保持环境干燥，避免潮湿"
            ],
            TCMConstitution.DAMP_HEAT: [
                "清淡饮食，避免辛辣油腻",
                "多食用清热利湿食物，如绿豆、冬瓜",
                "保持皮肤清洁，避免化妆品过敏",
                "避免熬夜，保持大便通畅"
            ],
            TCMConstitution.BLOOD_STASIS: [
                "适当运动，促进血液循环",
                "多食用活血化瘀食物，如山楂、红花",
                "保持情绪舒畅，避免生气",
                "注意保暖，避免受寒"
            ],
            TCMConstitution.QI_STAGNATION: [
                "保持心情愉快，学会释放压力",
                "多参加社交活动，避免独处",
                "适当运动，如散步、游泳",
                "多食用疏肝理气食物，如柑橘、玫瑰花"
            ],
            TCMConstitution.SPECIAL_DIATHESIS: [
                "避免接触过敏原",
                "增强体质，提高免疫力",
                "注意环境卫生，保持空气清新",
                "必要时进行脱敏治疗"
            ]
        }
        
        recommendations.extend(base_recommendations.get(primary_constitution, []))
        
        # 根据严重程度调整建议
        if severity in [ConstitutionSeverity.MODERATE, ConstitutionSeverity.SEVERE]:
            recommendations.append("建议寻求专业中医师指导")
            recommendations.append("可考虑中药调理")
        
        # 考虑次要体质的建议
        for constitution, score in secondary_constitutions:
            if score >= 50:
                secondary_recommendations = base_recommendations.get(constitution, [])
                # 选择1-2个最重要的建议
                recommendations.extend(secondary_recommendations[:2])
        
        return list(set(recommendations))  # 去重
    
    def _calculate_confidence_score(
        self,
        scores: Dict[TCMConstitution, float],
        responses: Dict[str, Any]
    ) -> float:
        """计算评估信心度"""
        # 基于得分差异和回答完整性计算信心度
        
        # 1. 得分差异度
        score_values = list(scores.values())
        if len(score_values) > 1:
            max_score = max(score_values)
            second_max = sorted(score_values, reverse=True)[1]
            score_diff = max_score - second_max
            diff_confidence = min(1.0, score_diff / 30)  # 差异越大，信心度越高
        else:
            diff_confidence = 0.5
        
        # 2. 回答完整性
        total_questions = 60  # 假设标准问卷有60题
        answered_questions = len(responses)
        completeness = answered_questions / total_questions
        
        # 3. 主要体质得分高低
        max_score = max(score_values) if score_values else 0
        score_confidence = max_score / 100
        
        # 综合信心度
        confidence = (diff_confidence * 0.4 + completeness * 0.3 + score_confidence * 0.3)
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_next_assessment_date(self, severity: ConstitutionSeverity) -> datetime:
        """计算下次评估时间"""
        intervals = {
            ConstitutionSeverity.NONE: 365,      # 1年
            ConstitutionSeverity.MILD: 180,      # 6个月
            ConstitutionSeverity.MODERATE: 90,   # 3个月
            ConstitutionSeverity.SEVERE: 30      # 1个月
        }
        
        days = intervals.get(severity, 180)
        return datetime.now() + timedelta(days=days)


class ConstitutionAdjustmentPlanGenerator:
    """体质调理方案生成器"""
    
    def __init__(self):
        self.adjustment_templates = self._load_adjustment_templates()
        self.seasonal_adjustments = self._load_seasonal_adjustments()
        self.food_therapy_database = self._load_food_therapy_database()
        self.exercise_recommendations = self._load_exercise_recommendations()
    
    def _load_adjustment_templates(self) -> Dict[str, Any]:
        """加载调理模板"""
        return {
            TCMConstitution.QI_DEFICIENCY: {
                "goals": ["补益元气", "增强体质", "改善疲劳"],
                "dietary": {
                    "recommended_foods": [
                        "黄芪", "人参", "党参", "白术", "山药", "大枣", "桂圆",
                        "小米", "糯米", "牛肉", "鸡肉", "鲫鱼"
                    ],
                    "avoid_foods": [
                        "生冷食物", "过于油腻食物", "辛辣刺激食物"
                    ],
                    "cooking_methods": ["炖煮", "蒸制", "温热食用"],
                    "meal_timing": "规律进餐，少食多餐"
                },
                "lifestyle": {
                    "sleep": "早睡早起，保证8小时睡眠",
                    "work_rest": "避免过度劳累，适当休息",
                    "environment": "保持室内温暖，避免受风寒"
                },
                "exercise": {
                    "recommended": ["散步", "太极拳", "八段锦", "瑜伽"],
                    "intensity": "低到中等强度",
                    "duration": "30-45分钟",
                    "frequency": "每日或隔日"
                },
                "emotional": {
                    "principles": ["保持心情愉快", "避免过度思虑"],
                    "methods": ["冥想", "听音乐", "与朋友交流"]
                },
                "herbal": {
                    "classic_formulas": ["四君子汤", "补中益气汤", "参苓白术散"],
                    "single_herbs": ["黄芪", "人参", "党参", "白术"]
                },
                "acupuncture": {
                    "main_points": ["足三里", "气海", "关元", "百会"],
                    "methods": ["温针灸", "艾灸"],
                    "frequency": "每周2-3次"
                }
            },
            TCMConstitution.YANG_DEFICIENCY: {
                "goals": ["温补阳气", "驱寒保暖", "增强体质"],
                "dietary": {
                    "recommended_foods": [
                        "羊肉", "狗肉", "鹿肉", "韭菜", "生姜", "肉桂",
                        "干姜", "附子", "核桃", "栗子", "荔枝"
                    ],
                    "avoid_foods": [
                        "生冷食物", "寒凉水果", "冷饮", "苦寒药物"
                    ],
                    "cooking_methods": ["温热烹调", "加入温性调料"],
                    "meal_timing": "温热食用，避免过饱"
                },
                "lifestyle": {
                    "sleep": "早睡晚起，保暖睡眠",
                    "clothing": "注意保暖，特别是腰腹部",
                    "environment": "居住环境温暖干燥"
                },
                "exercise": {
                    "recommended": ["慢跑", "游泳", "太极拳", "瑜伽"],
                    "timing": "上午阳气升发时运动",
                    "precautions": "避免大汗淋漓"
                },
                "herbal": {
                    "classic_formulas": ["金匮肾气丸", "右归丸", "附子理中汤"],
                    "single_herbs": ["附子", "肉桂", "干姜", "鹿茸"]
                }
            },
            TCMConstitution.YIN_DEFICIENCY: {
                "goals": ["滋阴润燥", "清虚热", "安神定志"],
                "dietary": {
                    "recommended_foods": [
                        "银耳", "百合", "枸杞", "麦冬", "玉竹", "沙参",
                        "鸭肉", "猪肉", "甲鱼", "海参", "梨", "葡萄"
                    ],
                    "avoid_foods": [
                        "辛辣食物", "煎炸食物", "温燥食物", "烟酒"
                    ],
                    "cooking_methods": ["清蒸", "炖煮", "凉拌"],
                    "meal_timing": "清淡饮食，适量进食"
                },
                "lifestyle": {
                    "sleep": "早睡，避免熬夜",
                    "environment": "保持室内湿润，避免干燥",
                    "stress": "避免过度紧张和焦虑"
                },
                "exercise": {
                    "recommended": ["瑜伽", "太极拳", "散步", "游泳"],
                    "intensity": "轻到中等强度",
                    "timing": "避免在炎热时段运动"
                },
                "herbal": {
                    "classic_formulas": ["六味地黄丸", "左归丸", "麦味地黄丸"],
                    "single_herbs": ["熟地黄", "山茱萸", "枸杞子", "麦冬"]
                }
            }
            # 其他体质的调理模板...
        }
    
    def _load_seasonal_adjustments(self) -> Dict[str, Any]:
        """加载季节调养方案"""
        return {
            "spring": {
                "principles": ["养肝", "疏肝理气", "升发阳气"],
                "foods": ["春笋", "韭菜", "菠菜", "香椿", "豆芽"],
                "activities": ["踏青", "放风筝", "春游"],
                "precautions": ["防风邪", "避免过度劳累"]
            },
            "summer": {
                "principles": ["养心", "清热解暑", "健脾利湿"],
                "foods": ["绿豆", "西瓜", "苦瓜", "冬瓜", "莲子"],
                "activities": ["游泳", "早晚散步", "避免暴晒"],
                "precautions": ["防暑降温", "避免贪凉"]
            },
            "autumn": {
                "principles": ["养肺", "润燥", "收敛阳气"],
                "foods": ["梨", "百合", "银耳", "蜂蜜", "芝麻"],
                "activities": ["登山", "深呼吸", "保持室内湿度"],
                "precautions": ["防燥邪", "适当进补"]
            },
            "winter": {
                "principles": ["养肾", "温阳", "藏精"],
                "foods": ["羊肉", "核桃", "黑芝麻", "桂圆", "栗子"],
                "activities": ["室内运动", "保暖", "早睡晚起"],
                "precautions": ["防寒保暖", "避免过度出汗"]
            }
        }
    
    def _load_food_therapy_database(self) -> Dict[str, Any]:
        """加载食疗数据库"""
        return {
            "qi_deficiency_recipes": [
                {
                    "name": "黄芪炖鸡",
                    "ingredients": ["黄芪30g", "母鸡1只", "生姜3片", "大枣5枚"],
                    "method": "将黄芪、生姜、大枣放入鸡腹内，加水炖煮2小时",
                    "effects": "补气养血，增强体质",
                    "frequency": "每周1-2次"
                },
                {
                    "name": "人参粥",
                    "ingredients": ["人参3g", "大米100g", "冰糖适量"],
                    "method": "人参研末，与大米同煮粥，加冰糖调味",
                    "effects": "大补元气，健脾益胃",
                    "frequency": "每日早餐"
                }
            ],
            "yang_deficiency_recipes": [
                {
                    "name": "当归生姜羊肉汤",
                    "ingredients": ["当归20g", "生姜30g", "羊肉500g"],
                    "method": "羊肉洗净切块，与当归、生姜同煮",
                    "effects": "温中补虚，祛寒止痛",
                    "frequency": "每周2-3次"
                }
            ],
            "yin_deficiency_recipes": [
                {
                    "name": "银耳莲子汤",
                    "ingredients": ["银耳15g", "莲子30g", "冰糖适量"],
                    "method": "银耳泡发，与莲子同煮，加冰糖调味",
                    "effects": "滋阴润肺，清心安神",
                    "frequency": "每日晚餐后"
                }
            ]
        }
    
    def _load_exercise_recommendations(self) -> Dict[str, Any]:
        """加载运动推荐"""
        return {
            "constitution_exercises": {
                TCMConstitution.QI_DEFICIENCY: {
                    "primary": ["太极拳", "八段锦", "五禽戏"],
                    "secondary": ["散步", "瑜伽", "气功"],
                    "intensity": "低到中等",
                    "duration": "30-45分钟",
                    "frequency": "每日或隔日"
                },
                TCMConstitution.YANG_DEFICIENCY: {
                    "primary": ["慢跑", "游泳", "太极拳"],
                    "secondary": ["瑜伽", "健身操", "爬山"],
                    "intensity": "中等",
                    "duration": "30-60分钟",
                    "frequency": "每周3-5次"
                },
                TCMConstitution.YIN_DEFICIENCY: {
                    "primary": ["瑜伽", "太极拳", "散步"],
                    "secondary": ["游泳", "八段锦", "冥想"],
                    "intensity": "轻到中等",
                    "duration": "30-45分钟",
                    "frequency": "每日"
                }
            }
        }
    
    @trace_operation("adjustment_plan_generator.generate_plan", SpanKind.INTERNAL)
    async def generate_adjustment_plan(
        self,
        user_id: str,
        constitution_assessment: ConstitutionAssessment,
        user_preferences: Dict[str, Any] = None
    ) -> ConstitutionAdjustmentPlan:
        """生成体质调理方案"""
        
        try:
            primary_constitution = constitution_assessment.primary_constitution
            severity = constitution_assessment.primary_severity
            
            # 获取调理模板
            template = self.adjustment_templates.get(primary_constitution, {})
            
            # 生成调理目标
            goals = template.get("goals", [])
            
            # 生成饮食调理建议
            dietary_recommendations = await self._generate_dietary_recommendations(
                primary_constitution, severity, user_preferences
            )
            
            # 生成生活起居建议
            lifestyle_recommendations = await self._generate_lifestyle_recommendations(
                primary_constitution, severity
            )
            
            # 生成运动调理建议
            exercise_recommendations = await self._generate_exercise_recommendations(
                primary_constitution, severity, user_preferences
            )
            
            # 生成情志调理建议
            emotional_recommendations = await self._generate_emotional_recommendations(
                primary_constitution, severity
            )
            
            # 生成中药调理建议
            herbal_recommendations = await self._generate_herbal_recommendations(
                primary_constitution, severity
            )
            
            # 生成针灸调理建议
            acupuncture_recommendations = await self._generate_acupuncture_recommendations(
                primary_constitution, severity
            )
            
            # 生成推拿按摩建议
            massage_recommendations = await self._generate_massage_recommendations(
                primary_constitution, severity
            )
            
            # 生成季节调养建议
            seasonal_adjustments = await self._generate_seasonal_adjustments(
                primary_constitution
            )
            
            # 生成禁忌事项
            contraindications = await self._generate_contraindications(
                primary_constitution, constitution_assessment.susceptible_diseases
            )
            
            # 生成评估指标
            evaluation_metrics = self._generate_evaluation_metrics(primary_constitution)
            
            # 确定调理周期
            duration = self._determine_adjustment_duration(severity)
            
            plan_id = f"constitution_plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            plan_name = f"{primary_constitution.value}体质调理方案"
            description = f"针对{primary_constitution.value}体质的个性化调理方案，调理程度：{severity.value}"
            
            return ConstitutionAdjustmentPlan(
                plan_id=plan_id,
                user_id=user_id,
                constitution_assessment=constitution_assessment,
                plan_name=plan_name,
                description=description,
                adjustment_goals=goals,
                dietary_recommendations=dietary_recommendations,
                lifestyle_recommendations=lifestyle_recommendations,
                exercise_recommendations=exercise_recommendations,
                emotional_recommendations=emotional_recommendations,
                herbal_recommendations=herbal_recommendations,
                acupuncture_recommendations=acupuncture_recommendations,
                massage_recommendations=massage_recommendations,
                seasonal_adjustments=seasonal_adjustments,
                contraindications=contraindications,
                adjustment_duration=duration,
                evaluation_metrics=evaluation_metrics
            )
            
        except Exception as e:
            logger.error(f"体质调理方案生成失败: {e}")
            raise
    
    async def _generate_dietary_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成饮食调理建议"""
        
        template = self.adjustment_templates.get(constitution, {})
        dietary_template = template.get("dietary", {})
        
        recommendations = {
            "recommended_foods": dietary_template.get("recommended_foods", []),
            "avoid_foods": dietary_template.get("avoid_foods", []),
            "cooking_methods": dietary_template.get("cooking_methods", []),
            "meal_timing": dietary_template.get("meal_timing", ""),
            "recipes": []
        }
        
        # 添加食疗方
        constitution_key = f"{constitution.value}_recipes"
        if constitution_key in self.food_therapy_database:
            recommendations["recipes"] = self.food_therapy_database[constitution_key]
        
        # 根据严重程度调整
        if severity in [ConstitutionSeverity.MODERATE, ConstitutionSeverity.SEVERE]:
            recommendations["special_notes"] = "建议咨询中医师制定更详细的食疗方案"
        
        # 考虑用户偏好
        if preferences:
            dietary_restrictions = preferences.get("dietary_restrictions", [])
            if dietary_restrictions:
                # 过滤掉用户不能吃的食物
                recommendations["recommended_foods"] = [
                    food for food in recommendations["recommended_foods"]
                    if food not in dietary_restrictions
                ]
        
        return recommendations
    
    async def _generate_lifestyle_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity
    ) -> Dict[str, Any]:
        """生成生活起居建议"""
        
        template = self.adjustment_templates.get(constitution, {})
        lifestyle_template = template.get("lifestyle", {})
        
        recommendations = {
            "sleep_schedule": lifestyle_template.get("sleep", ""),
            "work_rest_balance": lifestyle_template.get("work_rest", ""),
            "environmental_factors": lifestyle_template.get("environment", ""),
            "daily_routine": []
        }
        
        # 基于体质的日常作息建议
        if constitution == TCMConstitution.QI_DEFICIENCY:
            recommendations["daily_routine"] = [
                "早上6-7点起床",
                "上午进行轻度运动",
                "中午适当午休",
                "晚上9-10点入睡"
            ]
        elif constitution == TCMConstitution.YANG_DEFICIENCY:
            recommendations["daily_routine"] = [
                "早上7-8点起床",
                "注意保暖，特别是腰腹部",
                "避免长时间待在空调房",
                "晚上10点前入睡"
            ]
        elif constitution == TCMConstitution.YIN_DEFICIENCY:
            recommendations["daily_routine"] = [
                "早上6-7点起床",
                "避免熬夜，最晚10点入睡",
                "保持室内适当湿度",
                "避免过度用眼"
            ]
        
        return recommendations
    
    async def _generate_exercise_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """生成运动调理建议"""
        
        exercise_data = self.exercise_recommendations["constitution_exercises"].get(constitution, {})
        
        recommendations = {
            "primary_exercises": exercise_data.get("primary", []),
            "secondary_exercises": exercise_data.get("secondary", []),
            "intensity": exercise_data.get("intensity", "中等"),
            "duration": exercise_data.get("duration", "30分钟"),
            "frequency": exercise_data.get("frequency", "每周3次"),
            "precautions": [],
            "detailed_plans": []
        }
        
        # 基于体质的运动注意事项
        if constitution == TCMConstitution.QI_DEFICIENCY:
            recommendations["precautions"] = [
                "避免过度出汗",
                "运动后及时休息",
                "选择温和的运动方式",
                "避免空腹运动"
            ]
        elif constitution == TCMConstitution.YANG_DEFICIENCY:
            recommendations["precautions"] = [
                "运动前充分热身",
                "避免在寒冷环境中运动",
                "运动后注意保暖",
                "选择阳光充足的时间运动"
            ]
        
        # 根据严重程度调整
        if severity == ConstitutionSeverity.SEVERE:
            recommendations["intensity"] = "轻度"
            recommendations["duration"] = "15-20分钟"
            recommendations["frequency"] = "每周2-3次"
        
        return recommendations
    
    async def _generate_emotional_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity
    ) -> Dict[str, Any]:
        """生成情志调理建议"""
        
        template = self.adjustment_templates.get(constitution, {})
        emotional_template = template.get("emotional", {})
        
        recommendations = {
            "principles": emotional_template.get("principles", []),
            "methods": emotional_template.get("methods", []),
            "stress_management": [],
            "mood_regulation": []
        }
        
        # 基于体质的情志调理
        if constitution == TCMConstitution.QI_STAGNATION:
            recommendations["stress_management"] = [
                "学习放松技巧",
                "培养兴趣爱好",
                "多与朋友交流",
                "避免独处过久"
            ]
            recommendations["mood_regulation"] = [
                "练习深呼吸",
                "听舒缓音乐",
                "进行户外活动",
                "保持积极心态"
            ]
        elif constitution == TCMConstitution.YIN_DEFICIENCY:
            recommendations["stress_management"] = [
                "避免过度紧张",
                "学会情绪管理",
                "保持内心平静",
                "避免急躁情绪"
            ]
        
        return recommendations
    
    async def _generate_herbal_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity
    ) -> Dict[str, Any]:
        """生成中药调理建议"""
        
        template = self.adjustment_templates.get(constitution, {})
        herbal_template = template.get("herbal", {})
        
        recommendations = {
            "classic_formulas": herbal_template.get("classic_formulas", []),
            "single_herbs": herbal_template.get("single_herbs", []),
            "usage_instructions": "请在中医师指导下使用",
            "precautions": [
                "孕妇慎用",
                "过敏体质者注意",
                "服药期间忌食生冷",
                "如有不适立即停药"
            ]
        }
        
        # 根据严重程度调整
        if severity in [ConstitutionSeverity.MODERATE, ConstitutionSeverity.SEVERE]:
            recommendations["professional_consultation"] = "强烈建议寻求专业中医师诊治"
        
        return recommendations
    
    async def _generate_acupuncture_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity
    ) -> Dict[str, Any]:
        """生成针灸调理建议"""
        
        template = self.adjustment_templates.get(constitution, {})
        acupuncture_template = template.get("acupuncture", {})
        
        recommendations = {
            "main_points": acupuncture_template.get("main_points", []),
            "methods": acupuncture_template.get("methods", []),
            "frequency": acupuncture_template.get("frequency", "每周2次"),
            "course_duration": "4-6周为一个疗程",
            "precautions": [
                "请寻求专业针灸师治疗",
                "治疗前告知身体状况",
                "治疗后注意休息",
                "孕妇特殊穴位慎用"
            ]
        }
        
        return recommendations
    
    async def _generate_massage_recommendations(
        self,
        constitution: TCMConstitution,
        severity: ConstitutionSeverity
    ) -> Dict[str, Any]:
        """生成推拿按摩建议"""
        
        recommendations = {
            "self_massage_points": [],
            "massage_techniques": [],
            "frequency": "每日1-2次",
            "duration": "每次10-15分钟",
            "precautions": []
        }
        
        # 基于体质的按摩建议
        if constitution == TCMConstitution.QI_DEFICIENCY:
            recommendations["self_massage_points"] = [
                "足三里", "气海", "关元", "百会"
            ]
            recommendations["massage_techniques"] = [
                "轻柔按压", "顺时针揉动", "温和推拿"
            ]
        elif constitution == TCMConstitution.BLOOD_STASIS:
            recommendations["self_massage_points"] = [
                "血海", "三阴交", "太冲", "膈俞"
            ]
            recommendations["massage_techniques"] = [
                "适度按压", "推拿活血", "拍打经络"
            ]
        
        return recommendations
    
    async def _generate_seasonal_adjustments(
        self,
        constitution: TCMConstitution
    ) -> Dict[SeasonType, Dict[str, Any]]:
        """生成季节调养建议"""
        
        adjustments = {}
        
        for season in SeasonType:
            seasonal_data = self.seasonal_adjustments.get(season.value, {})
            
            adjustments[season] = {
                "principles": seasonal_data.get("principles", []),
                "recommended_foods": seasonal_data.get("foods", []),
                "activities": seasonal_data.get("activities", []),
                "precautions": seasonal_data.get("precautions", []),
                "constitution_specific": []
            }
            
            # 添加体质特异性建议
            if constitution == TCMConstitution.YANG_DEFICIENCY and season == SeasonType.WINTER:
                adjustments[season]["constitution_specific"] = [
                    "加强温阳食物摄入",
                    "增加艾灸频率",
                    "避免寒冷刺激"
                ]
            elif constitution == TCMConstitution.YIN_DEFICIENCY and season == SeasonType.SUMMER:
                adjustments[season]["constitution_specific"] = [
                    "增加滋阴食物",
                    "避免暴晒",
                    "保持充足水分"
                ]
        
        return adjustments
    
    async def _generate_contraindications(
        self,
        constitution: TCMConstitution,
        susceptible_diseases: List[str]
    ) -> List[str]:
        """生成禁忌事项"""
        
        contraindications = []
        
        # 基于体质的一般禁忌
        constitution_contraindications = {
            TCMConstitution.QI_DEFICIENCY: [
                "避免过度劳累",
                "避免大汗淋漓",
                "避免长期熬夜",
                "避免过度节食"
            ],
            TCMConstitution.YANG_DEFICIENCY: [
                "避免生冷食物",
                "避免长期待在空调房",
                "避免冷水洗浴",
                "避免过度出汗"
            ],
            TCMConstitution.YIN_DEFICIENCY: [
                "避免辛辣刺激食物",
                "避免熬夜",
                "避免过度用眼",
                "避免情绪激动"
            ],
            TCMConstitution.PHLEGM_DAMPNESS: [
                "避免肥甘厚腻食物",
                "避免久坐不动",
                "避免潮湿环境",
                "避免暴饮暴食"
            ],
            TCMConstitution.DAMP_HEAT: [
                "避免辛辣油腻食物",
                "避免熬夜",
                "避免过度化妆",
                "避免情绪急躁"
            ],
            TCMConstitution.BLOOD_STASIS: [
                "避免久坐久立",
                "避免情绪郁闷",
                "避免受寒",
                "避免外伤"
            ],
            TCMConstitution.QI_STAGNATION: [
                "避免情绪压抑",
                "避免独处过久",
                "避免过度思虑",
                "避免生闷气"
            ],
            TCMConstitution.SPECIAL_DIATHESIS: [
                "避免接触过敏原",
                "避免滥用药物",
                "避免环境污染",
                "避免过度疲劳"
            ]
        }
        
        contraindications.extend(constitution_contraindications.get(constitution, []))
        
        # 基于易感疾病的禁忌
        if "高血压" in susceptible_diseases:
            contraindications.extend(["控制盐分摄入", "避免情绪激动"])
        if "糖尿病" in susceptible_diseases:
            contraindications.extend(["控制糖分摄入", "避免暴饮暴食"])
        
        return list(set(contraindications))  # 去重
    
    def _generate_evaluation_metrics(self, constitution: TCMConstitution) -> List[str]:
        """生成评估指标"""
        
        base_metrics = [
            "体质症状改善程度",
            "生活质量评分",
            "睡眠质量",
            "精神状态",
            "体重变化",
            "血压变化"
        ]
        
        # 基于体质的特异性指标
        constitution_metrics = {
            TCMConstitution.QI_DEFICIENCY: [
                "疲劳程度", "气短改善", "出汗情况"
            ],
            TCMConstitution.YANG_DEFICIENCY: [
                "畏寒程度", "手足温度", "大便性状"
            ],
            TCMConstitution.YIN_DEFICIENCY: [
                "口干程度", "手足心热", "潮热盗汗"
            ],
            TCMConstitution.PHLEGM_DAMPNESS: [
                "体重变化", "胸闷改善", "痰量减少"
            ],
            TCMConstitution.DAMP_HEAT: [
                "皮肤状况", "口苦改善", "大便性状"
            ],
            TCMConstitution.BLOOD_STASIS: [
                "肤色改善", "瘀斑减少", "疼痛缓解"
            ],
            TCMConstitution.QI_STAGNATION: [
                "情绪状态", "胸胁胀满", "睡眠质量"
            ],
            TCMConstitution.SPECIAL_DIATHESIS: [
                "过敏反应", "哮喘发作", "皮肤症状"
            ]
        }
        
        base_metrics.extend(constitution_metrics.get(constitution, []))
        
        return base_metrics
    
    def _determine_adjustment_duration(self, severity: ConstitutionSeverity) -> int:
        """确定调理周期"""
        
        durations = {
            ConstitutionSeverity.NONE: 30,       # 1个月
            ConstitutionSeverity.MILD: 60,       # 2个月
            ConstitutionSeverity.MODERATE: 90,   # 3个月
            ConstitutionSeverity.SEVERE: 120     # 4个月
        }
        
        return durations.get(severity, 90)


class IntelligentTCMConstitutionEngine:
    """智能中医体质辨识引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.constitution_analyzer = None
        self.adjustment_plan_generator = None
        
        # 数据存储
        self.constitution_assessments = {}
        self.adjustment_plans = {}
        self.progress_records = {}
        self.questionnaire_templates = {}
        
        # 配置
        self.assessment_settings = {}
        
        logger.info("智能中医体质辨识引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            logger.info("智能中医体质辨识引擎初始化成功")
        except Exception as e:
            logger.error(f"智能中医体质辨识引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        self.assessment_settings = self.config.get("assessment_settings", {})
    
    async def _initialize_components(self):
        """初始化组件"""
        self.constitution_analyzer = ConstitutionAnalyzer()
        self.adjustment_plan_generator = ConstitutionAdjustmentPlanGenerator()
    
    @trace_operation("tcm_constitution_engine.assess_constitution", SpanKind.INTERNAL)
    async def assess_constitution(
        self,
        user_id: str,
        questionnaire_responses: Dict[str, Any],
        assessment_method: str = "questionnaire"
    ) -> ConstitutionAssessment:
        """进行体质辨识"""
        
        try:
            # 进行体质分析
            assessment = await self.constitution_analyzer.analyze_constitution(
                user_id=user_id,
                questionnaire_responses=questionnaire_responses,
                assessment_method=assessment_method
            )
            
            # 存储评估结果
            if user_id not in self.constitution_assessments:
                self.constitution_assessments[user_id] = []
            self.constitution_assessments[user_id].append(assessment)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "constitution_assessments_total",
                    {
                        "constitution": assessment.primary_constitution.value,
                        "severity": assessment.primary_severity.value
                    }
                )
            
            logger.info(f"用户 {user_id} 的体质辨识完成，主要体质: {assessment.primary_constitution.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"体质辨识失败: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("constitution_assessment_errors_total")
            raise
    
    @trace_operation("tcm_constitution_engine.generate_adjustment_plan", SpanKind.INTERNAL)
    async def generate_adjustment_plan(
        self,
        user_id: str,
        user_preferences: Dict[str, Any] = None
    ) -> ConstitutionAdjustmentPlan:
        """生成体质调理方案"""
        
        try:
            # 获取最新的体质评估
            latest_assessment = self._get_latest_assessment(user_id)
            if not latest_assessment:
                raise ValueError(f"用户 {user_id} 没有体质评估数据")
            
            # 生成调理方案
            plan = await self.adjustment_plan_generator.generate_adjustment_plan(
                user_id=user_id,
                constitution_assessment=latest_assessment,
                user_preferences=user_preferences
            )
            
            # 存储调理方案
            self.adjustment_plans[user_id] = plan
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "adjustment_plans_generated_total",
                    {"constitution": latest_assessment.primary_constitution.value}
                )
            
            logger.info(f"用户 {user_id} 的体质调理方案生成完成")
            return plan
            
        except Exception as e:
            logger.error(f"体质调理方案生成失败: {e}")
            if self.metrics_collector:
                self.metrics_collector.increment_counter("adjustment_plan_generation_errors_total")
            raise
    
    async def track_constitution_progress(
        self,
        user_id: str,
        progress_data: Dict[str, Any]
    ) -> ConstitutionProgress:
        """跟踪体质调理进展"""
        
        try:
            # 获取当前调理方案
            current_plan = self.adjustment_plans.get(user_id)
            if not current_plan:
                raise ValueError(f"用户 {user_id} 没有活跃的调理方案")
            
            # 创建进展记录
            progress = ConstitutionProgress(
                user_id=user_id,
                plan_id=current_plan.plan_id,
                progress_date=datetime.now(),
                symptom_improvements=progress_data.get("symptom_improvements", {}),
                constitution_score_changes=progress_data.get("constitution_score_changes", {}),
                quality_of_life_score=progress_data.get("quality_of_life_score"),
                adherence_score=progress_data.get("adherence_score", 0.0),
                satisfaction_score=progress_data.get("satisfaction_score"),
                adverse_effects=progress_data.get("adverse_effects", []),
                effectiveness_rating=progress_data.get("effectiveness_rating"),
                next_steps=progress_data.get("next_steps", [])
            )
            
            # 存储进展记录
            if user_id not in self.progress_records:
                self.progress_records[user_id] = []
            self.progress_records[user_id].append(progress)
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.histogram(
                    "constitution_adherence_rate",
                    progress.adherence_score,
                    {"user_id": user_id}
                )
            
            logger.info(f"用户 {user_id} 的体质调理进展已记录")
            return progress
            
        except Exception as e:
            logger.error(f"体质调理进展跟踪失败: {e}")
            raise
    
    def _get_latest_assessment(self, user_id: str) -> Optional[ConstitutionAssessment]:
        """获取最新的体质评估"""
        assessments = self.constitution_assessments.get(user_id, [])
        if assessments:
            return max(assessments, key=lambda x: x.assessment_date)
        return None
    
    async def get_constitution_summary(self, user_id: str) -> Dict[str, Any]:
        """获取体质总结"""
        
        try:
            # 获取最新评估
            latest_assessment = self._get_latest_assessment(user_id)
            if not latest_assessment:
                return {"error": "没有体质评估数据"}
            
            # 获取调理方案
            adjustment_plan = self.adjustment_plans.get(user_id)
            
            # 获取进展记录
            progress_records = self.progress_records.get(user_id, [])
            
            # 计算调理效果
            adjustment_effectiveness = self._calculate_adjustment_effectiveness(progress_records)
            
            # 生成建议
            recommendations = await self._generate_summary_recommendations(
                latest_assessment, adjustment_plan, progress_records
            )
            
            return {
                "user_id": user_id,
                "summary_date": datetime.now().isoformat(),
                "constitution_assessment": {
                    "primary_constitution": latest_assessment.primary_constitution.value,
                    "primary_score": latest_assessment.primary_score,
                    "severity": latest_assessment.primary_severity.value,
                    "secondary_constitutions": [
                        {"constitution": const.value, "score": score}
                        for const, score in latest_assessment.secondary_constitutions
                    ],
                    "assessment_date": latest_assessment.assessment_date.isoformat(),
                    "confidence_score": latest_assessment.confidence_score
                },
                "adjustment_plan": {
                    "plan_id": adjustment_plan.plan_id if adjustment_plan else None,
                    "plan_name": adjustment_plan.plan_name if adjustment_plan else None,
                    "status": adjustment_plan.status if adjustment_plan else None,
                    "duration": adjustment_plan.adjustment_duration if adjustment_plan else None
                } if adjustment_plan else None,
                "adjustment_effectiveness": adjustment_effectiveness,
                "susceptible_diseases": latest_assessment.susceptible_diseases,
                "recommendations": recommendations,
                "next_actions": self._get_next_actions(latest_assessment, adjustment_plan, progress_records)
            }
            
        except Exception as e:
            logger.error(f"获取体质总结失败: {e}")
            raise
    
    def _calculate_adjustment_effectiveness(self, progress_records: List[ConstitutionProgress]) -> Dict[str, Any]:
        """计算调理效果"""
        if not progress_records:
            return {"status": "no_data"}
        
        latest_progress = progress_records[-1]
        
        # 计算症状改善率
        symptom_improvements = latest_progress.symptom_improvements
        if symptom_improvements:
            avg_improvement = sum(symptom_improvements.values()) / len(symptom_improvements)
        else:
            avg_improvement = 0.0
        
        return {
            "symptom_improvement_rate": avg_improvement,
            "adherence_rate": latest_progress.adherence_score,
            "quality_of_life_score": latest_progress.quality_of_life_score,
            "satisfaction_score": latest_progress.satisfaction_score,
            "effectiveness_rating": latest_progress.effectiveness_rating,
            "progress_date": latest_progress.progress_date.isoformat()
        }
    
    async def _generate_summary_recommendations(
        self,
        assessment: ConstitutionAssessment,
        plan: Optional[ConstitutionAdjustmentPlan],
        progress_records: List[ConstitutionProgress]
    ) -> List[str]:
        """生成总结建议"""
        recommendations = []
        
        # 基于体质的基础建议
        recommendations.extend(assessment.adjustment_recommendations)
        
        # 基于调理进展的建议
        if progress_records:
            latest_progress = progress_records[-1]
            
            if latest_progress.adherence_score < 0.7:
                recommendations.append("提高调理方案的依从性")
            
            if latest_progress.adverse_effects:
                recommendations.append("注意调理过程中的不良反应，必要时调整方案")
            
            if latest_progress.quality_of_life_score and latest_progress.quality_of_life_score < 7:
                recommendations.append("关注生活质量改善，调整调理重点")
        
        # 季节性建议
        current_season = self._get_current_season()
        recommendations.append(f"注意{current_season}季节调养")
        
        return recommendations
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    def _get_next_actions(
        self,
        assessment: ConstitutionAssessment,
        plan: Optional[ConstitutionAdjustmentPlan],
        progress_records: List[ConstitutionProgress]
    ) -> List[str]:
        """获取下一步行动"""
        actions = []
        
        # 检查是否需要重新评估体质
        if assessment.next_assessment_date and assessment.next_assessment_date <= datetime.now():
            actions.append("进行体质重新评估")
        
        # 检查调理方案状态
        if plan:
            plan_end_date = plan.created_date + timedelta(days=plan.adjustment_duration)
            if plan_end_date <= datetime.now():
                actions.append("更新体质调理方案")
        else:
            actions.append("制定体质调理方案")
        
        # 基于进展记录的行动
        if progress_records:
            latest_progress = progress_records[-1]
            if latest_progress.next_steps:
                actions.extend(latest_progress.next_steps)
        
        # 通用行动
        actions.extend([
            "继续执行体质调理方案",
            "定期记录调理效果",
            "注意季节性调养"
        ])
        
        return actions
    
    async def get_constitution_statistics(self) -> Dict[str, Any]:
        """获取体质统计信息"""
        
        try:
            total_users = len(self.constitution_assessments)
            total_assessments = sum(len(assessments) for assessments in self.constitution_assessments.values())
            total_plans = len(self.adjustment_plans)
            
            # 体质分布统计
            constitution_distribution = {}
            for assessments in self.constitution_assessments.values():
                if assessments:
                    latest = max(assessments, key=lambda x: x.assessment_date)
                    constitution = latest.primary_constitution.value
                    constitution_distribution[constitution] = constitution_distribution.get(constitution, 0) + 1
            
            # 严重程度分布
            severity_distribution = {}
            for assessments in self.constitution_assessments.values():
                if assessments:
                    latest = max(assessments, key=lambda x: x.assessment_date)
                    severity = latest.primary_severity.value
                    severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
            
            # 调理效果统计
            effectiveness_stats = {}
            if self.progress_records:
                all_progress = []
                for records in self.progress_records.values():
                    all_progress.extend(records)
                
                if all_progress:
                    avg_adherence = sum(p.adherence_score for p in all_progress) / len(all_progress)
                    avg_satisfaction = sum(p.satisfaction_score for p in all_progress if p.satisfaction_score]) / len([p for p in all_progress if p.satisfaction_score])
                    
                    effectiveness_stats = {
                        "average_adherence_rate": avg_adherence,
                        "average_satisfaction_score": avg_satisfaction,
                        "total_progress_records": len(all_progress)
                    }
            
            return {
                "total_users": total_users,
                "total_assessments": total_assessments,
                "total_adjustment_plans": total_plans,
                "constitution_distribution": constitution_distribution,
                "severity_distribution": severity_distribution,
                "adjustment_effectiveness": effectiveness_stats,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取体质统计信息失败: {e}")
            raise


def initialize_tcm_constitution_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentTCMConstitutionEngine:
    """初始化智能中医体质辨识引擎"""
    engine = IntelligentTCMConstitutionEngine(config, metrics_collector)
    return engine


# 全局引擎实例
_tcm_constitution_engine: Optional[IntelligentTCMConstitutionEngine] = None


def get_tcm_constitution_engine() -> Optional[IntelligentTCMConstitutionEngine]:
    """获取智能中医体质辨识引擎实例"""
    return _tcm_constitution_engine 