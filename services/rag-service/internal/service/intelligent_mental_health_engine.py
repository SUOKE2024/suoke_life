#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能心理健康引擎 - 提供全面的心理健康管理服务
结合现代心理学理论和中医情志理论，为用户提供个性化的心理健康评估、情绪管理和心理干预建议
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
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class MentalHealthCondition(str, Enum):
    """心理健康状况"""
    EXCELLENT = "excellent"         # 优秀
    GOOD = "good"                  # 良好
    FAIR = "fair"                  # 一般
    POOR = "poor"                  # 较差
    CRITICAL = "critical"          # 危急


class EmotionType(str, Enum):
    """情绪类型"""
    JOY = "joy"                    # 喜悦
    SADNESS = "sadness"            # 悲伤
    ANGER = "anger"                # 愤怒
    FEAR = "fear"                  # 恐惧
    ANXIETY = "anxiety"            # 焦虑
    STRESS = "stress"              # 压力
    DEPRESSION = "depression"      # 抑郁
    EXCITEMENT = "excitement"      # 兴奋
    CALM = "calm"                  # 平静
    CONFUSION = "confusion"        # 困惑
    GUILT = "guilt"                # 内疚
    SHAME = "shame"                # 羞耻


class TCMEmotion(str, Enum):
    """中医七情"""
    JOY = "joy"                    # 喜
    ANGER = "anger"                # 怒
    WORRY = "worry"                # 忧
    PENSIVENESS = "pensiveness"    # 思
    SADNESS = "sadness"            # 悲
    FEAR = "fear"                  # 恐
    FRIGHT = "fright"              # 惊


class StressLevel(str, Enum):
    """压力水平"""
    MINIMAL = "minimal"            # 极低
    LOW = "low"                    # 低
    MODERATE = "moderate"          # 中等
    HIGH = "high"                  # 高
    SEVERE = "severe"              # 严重


class InterventionType(str, Enum):
    """干预类型"""
    COGNITIVE_BEHAVIORAL = "cognitive_behavioral"       # 认知行为疗法
    MINDFULNESS = "mindfulness"                         # 正念疗法
    RELAXATION = "relaxation"                           # 放松训练
    BREATHING_EXERCISE = "breathing_exercise"           # 呼吸练习
    MEDITATION = "meditation"                           # 冥想
    PHYSICAL_ACTIVITY = "physical_activity"             # 体育活动
    SOCIAL_SUPPORT = "social_support"                   # 社会支持
    PROFESSIONAL_HELP = "professional_help"             # 专业帮助
    TCM_THERAPY = "tcm_therapy"                         # 中医疗法
    LIFESTYLE_CHANGE = "lifestyle_change"               # 生活方式改变


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"                    # 低风险
    MODERATE = "moderate"          # 中等风险
    HIGH = "high"                  # 高风险
    CRITICAL = "critical"          # 危急风险


class AssessmentType(str, Enum):
    """评估类型"""
    DEPRESSION_SCALE = "depression_scale"               # 抑郁量表
    ANXIETY_SCALE = "anxiety_scale"                     # 焦虑量表
    STRESS_SCALE = "stress_scale"                       # 压力量表
    MOOD_ASSESSMENT = "mood_assessment"                 # 情绪评估
    COGNITIVE_ASSESSMENT = "cognitive_assessment"       # 认知评估
    BEHAVIORAL_ASSESSMENT = "behavioral_assessment"     # 行为评估
    TCM_EMOTION_ASSESSMENT = "tcm_emotion_assessment"   # 中医情志评估
    COMPREHENSIVE = "comprehensive"                     # 综合评估


@dataclass
class EmotionRecord:
    """情绪记录"""
    user_id: str
    timestamp: datetime
    emotion_type: EmotionType
    intensity: float                        # 强度 (0.0-1.0)
    duration_minutes: Optional[int] = None
    triggers: List[str] = field(default_factory=list)
    context: Optional[str] = None
    physical_symptoms: List[str] = field(default_factory=list)
    coping_strategies: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class MoodEntry:
    """心情记录"""
    user_id: str
    date: datetime
    mood_score: float                       # 心情评分 (1.0-10.0)
    energy_level: float                     # 精力水平 (1.0-10.0)
    sleep_quality: float                    # 睡眠质量 (1.0-10.0)
    stress_level: StressLevel
    dominant_emotions: List[EmotionType] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    social_interactions: int = 0            # 社交互动次数
    exercise_minutes: int = 0               # 运动时长
    meditation_minutes: int = 0             # 冥想时长
    notes: Optional[str] = None


@dataclass
class PsychologicalAssessment:
    """心理评估"""
    user_id: str
    assessment_type: AssessmentType
    assessment_date: datetime
    scores: Dict[str, float] = field(default_factory=dict)
    raw_responses: Dict[str, Any] = field(default_factory=dict)
    interpretation: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    recommendations: List[str] = field(default_factory=list)
    follow_up_date: Optional[datetime] = None
    assessor: str = "system"
    notes: Optional[str] = None


@dataclass
class TCMEmotionAnalysis:
    """中医情志分析"""
    user_id: str
    analysis_date: datetime
    dominant_emotion: TCMEmotion
    emotion_scores: Dict[TCMEmotion, float] = field(default_factory=dict)
    organ_imbalance: Dict[str, float] = field(default_factory=dict)  # 脏腑失调
    qi_stagnation_level: float = 0.0        # 气滞程度
    blood_stasis_level: float = 0.0         # 血瘀程度
    constitution_impact: Dict[str, float] = field(default_factory=dict)
    treatment_principles: List[str] = field(default_factory=list)
    herbal_recommendations: List[str] = field(default_factory=list)
    acupoint_recommendations: List[str] = field(default_factory=list)
    lifestyle_adjustments: List[str] = field(default_factory=list)


@dataclass
class InterventionPlan:
    """干预计划"""
    user_id: str
    plan_id: str
    name: str
    description: str
    intervention_types: List[InterventionType]
    target_conditions: List[str]
    start_date: datetime
    end_date: datetime
    daily_activities: List[Dict[str, Any]] = field(default_factory=list)
    weekly_goals: List[str] = field(default_factory=list)
    progress_metrics: List[str] = field(default_factory=list)
    emergency_contacts: List[Dict[str, str]] = field(default_factory=list)
    crisis_plan: Optional[str] = None
    created_by: str = "system"
    status: str = "active"


@dataclass
class CrisisAssessment:
    """危机评估"""
    user_id: str
    assessment_time: datetime
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    suicide_risk_score: float = 0.0        # 自杀风险评分
    self_harm_risk_score: float = 0.0       # 自伤风险评分
    immediate_safety_concerns: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    emergency_level: RiskLevel = RiskLevel.LOW
    requires_immediate_intervention: bool = False
    professional_referral_needed: bool = False


class EmotionAnalyzer:
    """情绪分析器"""
    
    def __init__(self):
        self.emotion_patterns = self._load_emotion_patterns()
        self.tcm_emotion_mapping = self._load_tcm_emotion_mapping()
        
    def _load_emotion_patterns(self) -> Dict[str, Any]:
        """加载情绪模式数据"""
        return {
            "emotion_keywords": {
                EmotionType.JOY: ["开心", "快乐", "兴奋", "愉悦", "满足", "幸福"],
                EmotionType.SADNESS: ["悲伤", "难过", "沮丧", "失落", "痛苦", "绝望"],
                EmotionType.ANGER: ["愤怒", "生气", "恼火", "暴躁", "愤慨", "怒火"],
                EmotionType.FEAR: ["害怕", "恐惧", "担心", "紧张", "不安", "惊慌"],
                EmotionType.ANXIETY: ["焦虑", "忧虑", "紧张", "不安", "烦躁", "担忧"],
                EmotionType.STRESS: ["压力", "紧张", "疲惫", "overwhelmed", "忙碌", "疲劳"],
                EmotionType.DEPRESSION: ["抑郁", "消沉", "无望", "空虚", "麻木", "孤独"],
                EmotionType.CALM: ["平静", "放松", "安详", "宁静", "舒适", "安心"]
            },
            "intensity_indicators": {
                "high": ["非常", "极其", "特别", "超级", "异常", "严重"],
                "medium": ["比较", "有点", "稍微", "一些", "还算", "相当"],
                "low": ["轻微", "一点点", "略微", "偶尔", "有时", "不太"]
            }
        }
    
    def _load_tcm_emotion_mapping(self) -> Dict[str, Any]:
        """加载中医情志映射"""
        return {
            "emotion_organ_mapping": {
                TCMEmotion.JOY: "heart",        # 喜伤心
                TCMEmotion.ANGER: "liver",      # 怒伤肝
                TCMEmotion.WORRY: "spleen",     # 忧伤脾
                TCMEmotion.PENSIVENESS: "spleen", # 思伤脾
                TCMEmotion.SADNESS: "lung",     # 悲伤肺
                TCMEmotion.FEAR: "kidney",      # 恐伤肾
                TCMEmotion.FRIGHT: "kidney"     # 惊伤肾
            },
            "organ_emotion_symptoms": {
                "heart": ["心悸", "失眠", "多梦", "健忘", "面红"],
                "liver": ["胸胁胀痛", "易怒", "头痛", "目赤", "口苦"],
                "spleen": ["食欲不振", "腹胀", "便溏", "倦怠", "思虑过度"],
                "lung": ["胸闷", "气短", "咳嗽", "悲伤", "皮肤干燥"],
                "kidney": ["腰膝酸软", "耳鸣", "恐惧", "夜尿频", "发脱齿摇"]
            }
        }
    
    async def analyze_emotion_text(self, text: str) -> Dict[str, Any]:
        """分析文本中的情绪"""
        emotions_detected = {}
        
        for emotion, keywords in self.emotion_patterns["emotion_keywords"].items():
            score = 0.0
            for keyword in keywords:
                if keyword in text:
                    score += 1.0
            
            # 检查强度指示词
            intensity_multiplier = 1.0
            for intensity, indicators in self.emotion_patterns["intensity_indicators"].items():
                for indicator in indicators:
                    if indicator in text:
                        if intensity == "high":
                            intensity_multiplier = 1.5
                        elif intensity == "medium":
                            intensity_multiplier = 1.2
                        elif intensity == "low":
                            intensity_multiplier = 0.8
                        break
            
            if score > 0:
                emotions_detected[emotion] = min(score * intensity_multiplier / len(keywords), 1.0)
        
        return {
            "detected_emotions": emotions_detected,
            "dominant_emotion": max(emotions_detected.items(), key=lambda x: x[1])[0] if emotions_detected else None,
            "emotional_intensity": max(emotions_detected.values()) if emotions_detected else 0.0,
            "emotional_complexity": len(emotions_detected)
        }
    
    async def analyze_tcm_emotions(self, emotion_records: List[EmotionRecord]) -> TCMEmotionAnalysis:
        """分析中医情志"""
        if not emotion_records:
            return TCMEmotionAnalysis(
                user_id="",
                analysis_date=datetime.now(),
                dominant_emotion=TCMEmotion.JOY
            )
        
        user_id = emotion_records[0].user_id
        
        # 统计七情分布
        tcm_emotion_scores = {emotion: 0.0 for emotion in TCMEmotion}
        
        for record in emotion_records:
            # 映射现代情绪到中医七情
            tcm_emotion = self._map_to_tcm_emotion(record.emotion_type)
            tcm_emotion_scores[tcm_emotion] += record.intensity
        
        # 归一化分数
        total_score = sum(tcm_emotion_scores.values())
        if total_score > 0:
            tcm_emotion_scores = {k: v/total_score for k, v in tcm_emotion_scores.items()}
        
        # 确定主导情志
        dominant_emotion = max(tcm_emotion_scores.items(), key=lambda x: x[1])[0]
        
        # 分析脏腑失调
        organ_imbalance = self._analyze_organ_imbalance(tcm_emotion_scores)
        
        # 生成治疗建议
        treatment_principles = self._generate_tcm_treatment_principles(dominant_emotion, organ_imbalance)
        herbal_recommendations = self._generate_herbal_recommendations(dominant_emotion)
        acupoint_recommendations = self._generate_acupoint_recommendations(dominant_emotion)
        lifestyle_adjustments = self._generate_lifestyle_adjustments(dominant_emotion)
        
        return TCMEmotionAnalysis(
            user_id=user_id,
            analysis_date=datetime.now(),
            dominant_emotion=dominant_emotion,
            emotion_scores=tcm_emotion_scores,
            organ_imbalance=organ_imbalance,
            qi_stagnation_level=self._calculate_qi_stagnation(tcm_emotion_scores),
            blood_stasis_level=self._calculate_blood_stasis(tcm_emotion_scores),
            treatment_principles=treatment_principles,
            herbal_recommendations=herbal_recommendations,
            acupoint_recommendations=acupoint_recommendations,
            lifestyle_adjustments=lifestyle_adjustments
        )
    
    def _map_to_tcm_emotion(self, emotion: EmotionType) -> TCMEmotion:
        """映射现代情绪到中医七情"""
        mapping = {
            EmotionType.JOY: TCMEmotion.JOY,
            EmotionType.EXCITEMENT: TCMEmotion.JOY,
            EmotionType.ANGER: TCMEmotion.ANGER,
            EmotionType.SADNESS: TCMEmotion.SADNESS,
            EmotionType.DEPRESSION: TCMEmotion.SADNESS,
            EmotionType.FEAR: TCMEmotion.FEAR,
            EmotionType.ANXIETY: TCMEmotion.FEAR,
            EmotionType.STRESS: TCMEmotion.WORRY,
            EmotionType.CONFUSION: TCMEmotion.PENSIVENESS,
            EmotionType.GUILT: TCMEmotion.WORRY,
            EmotionType.SHAME: TCMEmotion.WORRY
        }
        return mapping.get(emotion, TCMEmotion.WORRY)
    
    def _analyze_organ_imbalance(self, tcm_emotion_scores: Dict[TCMEmotion, float]) -> Dict[str, float]:
        """分析脏腑失调"""
        organ_imbalance = {}
        
        for emotion, score in tcm_emotion_scores.items():
            organ = self.tcm_emotion_mapping["emotion_organ_mapping"][emotion]
            if organ not in organ_imbalance:
                organ_imbalance[organ] = 0.0
            organ_imbalance[organ] += score
        
        return organ_imbalance
    
    def _calculate_qi_stagnation(self, tcm_emotion_scores: Dict[TCMEmotion, float]) -> float:
        """计算气滞程度"""
        # 怒、忧、思容易导致气滞
        qi_stagnation_emotions = [TCMEmotion.ANGER, TCMEmotion.WORRY, TCMEmotion.PENSIVENESS]
        return sum(tcm_emotion_scores.get(emotion, 0.0) for emotion in qi_stagnation_emotions)
    
    def _calculate_blood_stasis(self, tcm_emotion_scores: Dict[TCMEmotion, float]) -> float:
        """计算血瘀程度"""
        # 长期情志不畅容易导致血瘀
        return sum(tcm_emotion_scores.values()) * 0.3  # 简化计算
    
    def _generate_tcm_treatment_principles(self, dominant_emotion: TCMEmotion, organ_imbalance: Dict[str, float]) -> List[str]:
        """生成中医治疗原则"""
        principles = []
        
        if dominant_emotion == TCMEmotion.ANGER:
            principles.extend(["疏肝理气", "清肝泻火", "养肝柔肝"])
        elif dominant_emotion == TCMEmotion.JOY:
            principles.extend(["养心安神", "清心火", "补心血"])
        elif dominant_emotion == TCMEmotion.WORRY:
            principles.extend(["健脾益气", "疏肝解郁", "调理脾胃"])
        elif dominant_emotion == TCMEmotion.PENSIVENESS:
            principles.extend(["健脾养心", "安神定志", "补益心脾"])
        elif dominant_emotion == TCMEmotion.SADNESS:
            principles.extend(["补肺气", "养肺阴", "宣肺理气"])
        elif dominant_emotion in [TCMEmotion.FEAR, TCMEmotion.FRIGHT]:
            principles.extend(["补肾固精", "养心安神", "镇惊定志"])
        
        return principles
    
    def _generate_herbal_recommendations(self, dominant_emotion: TCMEmotion) -> List[str]:
        """生成中药推荐"""
        herbs = {
            TCMEmotion.ANGER: ["柴胡", "白芍", "当归", "川芎", "香附", "郁金"],
            TCMEmotion.JOY: ["甘草", "小麦", "大枣", "龙骨", "牡蛎", "远志"],
            TCMEmotion.WORRY: ["党参", "白术", "茯苓", "甘草", "陈皮", "半夏"],
            TCMEmotion.PENSIVENESS: ["人参", "当归", "白术", "茯神", "远志", "石菖蒲"],
            TCMEmotion.SADNESS: ["人参", "麦冬", "五味子", "百合", "杏仁", "桔梗"],
            TCMEmotion.FEAR: ["熟地黄", "山茱萸", "山药", "茯苓", "牡丹皮", "泽泻"],
            TCMEmotion.FRIGHT: ["龙骨", "牡蛎", "朱砂", "琥珀", "远志", "石菖蒲"]
        }
        return herbs.get(dominant_emotion, [])
    
    def _generate_acupoint_recommendations(self, dominant_emotion: TCMEmotion) -> List[str]:
        """生成穴位推荐"""
        acupoints = {
            TCMEmotion.ANGER: ["太冲", "行间", "期门", "章门", "肝俞", "胆俞"],
            TCMEmotion.JOY: ["神门", "心俞", "内关", "通里", "少府", "少冲"],
            TCMEmotion.WORRY: ["太白", "脾俞", "足三里", "三阴交", "中脘", "天枢"],
            TCMEmotion.PENSIVENESS: ["百会", "四神聪", "印堂", "神庭", "心俞", "脾俞"],
            TCMEmotion.SADNESS: ["太渊", "肺俞", "中府", "云门", "列缺", "尺泽"],
            TCMEmotion.FEAR: ["太溪", "肾俞", "关元", "气海", "涌泉", "照海"],
            TCMEmotion.FRIGHT: ["神门", "安眠", "四神聪", "百会", "印堂", "太冲"]
        }
        return acupoints.get(dominant_emotion, [])
    
    def _generate_lifestyle_adjustments(self, dominant_emotion: TCMEmotion) -> List[str]:
        """生成生活方式调整建议"""
        adjustments = {
            TCMEmotion.ANGER: [
                "避免过度劳累和熬夜",
                "保持心情舒畅，避免情绪激动",
                "适当运动，如散步、太极拳",
                "饮食清淡，少食辛辣刺激食物",
                "多食绿色蔬菜和酸味食物"
            ],
            TCMEmotion.JOY: [
                "避免过度兴奋和刺激",
                "保持作息规律，充足睡眠",
                "适当静心活动，如冥想、书法",
                "饮食宜清淡，多食红色食物",
                "避免过量饮酒和咖啡"
            ],
            TCMEmotion.WORRY: [
                "保持乐观心态，避免过度忧虑",
                "规律饮食，细嚼慢咽",
                "适当运动，增强体质",
                "多食甘味食物，如山药、大枣",
                "避免生冷寒凉食物"
            ],
            TCMEmotion.PENSIVENESS: [
                "避免过度思虑和用脑",
                "保证充足睡眠和休息",
                "适当户外活动，接触自然",
                "饮食营养均衡，多食健脾食物",
                "练习放松技巧，如深呼吸"
            ],
            TCMEmotion.SADNESS: [
                "保持积极心态，多与人交流",
                "适当运动，增强肺功能",
                "多食白色食物，如梨、百合",
                "避免悲伤情绪的刺激",
                "练习呼吸功法，如八段锦"
            ],
            TCMEmotion.FEAR: [
                "增强自信心，避免恐惧刺激",
                "保持温暖，避免寒冷",
                "适当温补，多食黑色食物",
                "规律作息，避免熬夜",
                "练习壮胆功法，如站桩"
            ],
            TCMEmotion.FRIGHT: [
                "保持环境安静，避免惊吓",
                "充足睡眠，安神定志",
                "适当静心活动，如冥想",
                "饮食清淡，避免刺激性食物",
                "练习安神功法，如静坐"
            ]
        }
        return adjustments.get(dominant_emotion, [])


class MentalHealthAssessor:
    """心理健康评估器"""
    
    def __init__(self):
        self.assessment_scales = self._load_assessment_scales()
        self.risk_indicators = self._load_risk_indicators()
        
    def _load_assessment_scales(self) -> Dict[str, Any]:
        """加载评估量表"""
        return {
            "depression_scale": {
                "name": "抑郁自评量表(SDS)",
                "questions": [
                    {"id": 1, "text": "我感到情绪沮丧，郁闷", "weight": 1.0},
                    {"id": 2, "text": "我感到早晨心情最好", "weight": -1.0},
                    {"id": 3, "text": "我要哭或想哭", "weight": 1.0},
                    {"id": 4, "text": "我夜间睡眠不好", "weight": 1.0},
                    {"id": 5, "text": "我吃饭象平时一样多", "weight": -1.0},
                    {"id": 6, "text": "我的性功能正常", "weight": -1.0},
                    {"id": 7, "text": "我感到体重减轻", "weight": 1.0},
                    {"id": 8, "text": "我为便秘烦恼", "weight": 1.0},
                    {"id": 9, "text": "我的心跳比平时快", "weight": 1.0},
                    {"id": 10, "text": "我无故感到疲劳", "weight": 1.0}
                ],
                "scoring": {
                    "mild": (0.5, 0.59),
                    "moderate": (0.6, 0.69),
                    "severe": (0.7, 1.0)
                }
            },
            "anxiety_scale": {
                "name": "焦虑自评量表(SAS)",
                "questions": [
                    {"id": 1, "text": "我感到比平常容易紧张或着急", "weight": 1.0},
                    {"id": 2, "text": "我无缘无故感到害怕", "weight": 1.0},
                    {"id": 3, "text": "我容易心里烦乱或感到惊恐", "weight": 1.0},
                    {"id": 4, "text": "我感到我可能将要发疯", "weight": 1.0},
                    {"id": 5, "text": "我觉得一切都很好", "weight": -1.0},
                    {"id": 6, "text": "我手脚发抖打颤", "weight": 1.0},
                    {"id": 7, "text": "我因为头痛、颈痛和背痛而苦恼", "weight": 1.0},
                    {"id": 8, "text": "我感觉容易衰弱和疲乏", "weight": 1.0},
                    {"id": 9, "text": "我觉得心平气和，并且容易安静坐着", "weight": -1.0},
                    {"id": 10, "text": "我感到心跳得很快", "weight": 1.0}
                ],
                "scoring": {
                    "mild": (0.5, 0.59),
                    "moderate": (0.6, 0.69),
                    "severe": (0.7, 1.0)
                }
            },
            "stress_scale": {
                "name": "压力感知量表",
                "questions": [
                    {"id": 1, "text": "在过去一个月中，您有多经常因为发生了意想不到的事情而感到心烦？", "weight": 1.0},
                    {"id": 2, "text": "在过去一个月中，您有多经常感到无法控制生活中重要的事情？", "weight": 1.0},
                    {"id": 3, "text": "在过去一个月中，您有多经常感到紧张和压力？", "weight": 1.0},
                    {"id": 4, "text": "在过去一个月中，您有多经常成功地处理恼人的生活麻烦？", "weight": -1.0},
                    {"id": 5, "text": "在过去一个月中，您有多经常感到您在有效地处理生活中出现的重要变化？", "weight": -1.0}
                ],
                "scoring": {
                    "low": (0.0, 0.3),
                    "moderate": (0.3, 0.6),
                    "high": (0.6, 1.0)
                }
            }
        }
    
    def _load_risk_indicators(self) -> Dict[str, Any]:
        """加载风险指标"""
        return {
            "suicide_risk_factors": [
                "有自杀想法或计划",
                "既往自杀未遂史",
                "严重抑郁症状",
                "物质滥用",
                "社会支持缺乏",
                "慢性疾病",
                "重大生活事件",
                "家族自杀史"
            ],
            "protective_factors": [
                "强烈的社会支持",
                "积极的应对技能",
                "宗教或精神信仰",
                "获得心理健康服务",
                "稳定的人际关系",
                "责任感和义务感",
                "未来导向的思维"
            ],
            "warning_signs": [
                "谈论死亡或自杀",
                "寻找自杀方法",
                "绝望感",
                "愤怒或报复心理",
                "鲁莽行为",
                "情绪剧烈波动",
                "社会退缩",
                "睡眠模式改变"
            ]
        }
    
    async def conduct_assessment(
        self,
        user_id: str,
        assessment_type: AssessmentType,
        responses: Dict[str, Any]
    ) -> PsychologicalAssessment:
        """进行心理评估"""
        
        if assessment_type not in [AssessmentType.DEPRESSION_SCALE, AssessmentType.ANXIETY_SCALE, AssessmentType.STRESS_SCALE]:
            # 对于其他类型的评估，使用综合评估方法
            return await self._conduct_comprehensive_assessment(user_id, responses)
        
        scale = self.assessment_scales[assessment_type.value]
        
        # 计算得分
        total_score = 0.0
        max_score = 0.0
        
        for question in scale["questions"]:
            question_id = str(question["id"])
            if question_id in responses:
                response_value = float(responses[question_id])
                weighted_score = response_value * question["weight"]
                total_score += weighted_score
                max_score += abs(question["weight"]) * 4  # 假设4分制
        
        # 归一化得分
        normalized_score = total_score / max_score if max_score > 0 else 0.0
        normalized_score = max(0.0, min(1.0, normalized_score))
        
        # 确定风险等级和解释
        risk_level, interpretation = self._interpret_score(assessment_type, normalized_score, scale)
        
        # 生成建议
        recommendations = self._generate_recommendations(assessment_type, risk_level, normalized_score)
        
        return PsychologicalAssessment(
            user_id=user_id,
            assessment_type=assessment_type,
            assessment_date=datetime.now(),
            scores={assessment_type.value: normalized_score},
            raw_responses=responses,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations,
            follow_up_date=self._calculate_follow_up_date(risk_level)
        )
    
    async def _conduct_comprehensive_assessment(
        self,
        user_id: str,
        responses: Dict[str, Any]
    ) -> PsychologicalAssessment:
        """进行综合心理评估"""
        
        # 分析各个维度
        mood_score = self._analyze_mood_indicators(responses)
        cognitive_score = self._analyze_cognitive_indicators(responses)
        behavioral_score = self._analyze_behavioral_indicators(responses)
        social_score = self._analyze_social_indicators(responses)
        
        # 计算综合得分
        overall_score = (mood_score + cognitive_score + behavioral_score + social_score) / 4
        
        # 确定风险等级
        if overall_score >= 0.8:
            risk_level = RiskLevel.LOW
        elif overall_score >= 0.6:
            risk_level = RiskLevel.MODERATE
        elif overall_score >= 0.4:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        # 生成解释
        interpretation = self._generate_comprehensive_interpretation(
            mood_score, cognitive_score, behavioral_score, social_score, overall_score
        )
        
        # 生成建议
        recommendations = self._generate_comprehensive_recommendations(
            mood_score, cognitive_score, behavioral_score, social_score, risk_level
        )
        
        return PsychologicalAssessment(
            user_id=user_id,
            assessment_type=AssessmentType.COMPREHENSIVE,
            assessment_date=datetime.now(),
            scores={
                "mood": mood_score,
                "cognitive": cognitive_score,
                "behavioral": behavioral_score,
                "social": social_score,
                "overall": overall_score
            },
            raw_responses=responses,
            interpretation=interpretation,
            risk_level=risk_level,
            recommendations=recommendations,
            follow_up_date=self._calculate_follow_up_date(risk_level)
        )
    
    def _interpret_score(self, assessment_type: AssessmentType, score: float, scale: Dict[str, Any]) -> Tuple[RiskLevel, str]:
        """解释评估得分"""
        scoring = scale["scoring"]
        
        if assessment_type in [AssessmentType.DEPRESSION_SCALE, AssessmentType.ANXIETY_SCALE]:
            if score < scoring["mild"][0]:
                return RiskLevel.LOW, "心理状态良好，无明显症状"
            elif score < scoring["moderate"][0]:
                return RiskLevel.MODERATE, "存在轻度症状，建议关注和自我调节"
            elif score < scoring["severe"][0]:
                return RiskLevel.HIGH, "存在中度症状，建议寻求专业帮助"
            else:
                return RiskLevel.CRITICAL, "存在重度症状，强烈建议立即寻求专业治疗"
        
        elif assessment_type == AssessmentType.STRESS_SCALE:
            if score < scoring["low"][1]:
                return RiskLevel.LOW, "压力水平较低，心理状态稳定"
            elif score < scoring["moderate"][1]:
                return RiskLevel.MODERATE, "压力水平中等，需要适当调节"
            else:
                return RiskLevel.HIGH, "压力水平较高，建议采取积极的应对措施"
        
        return RiskLevel.LOW, "评估结果正常"
    
    def _generate_recommendations(self, assessment_type: AssessmentType, risk_level: RiskLevel, score: float) -> List[str]:
        """生成评估建议"""
        recommendations = []
        
        # 基于评估类型的建议
        if assessment_type == AssessmentType.DEPRESSION_SCALE:
            if risk_level == RiskLevel.LOW:
                recommendations.extend([
                    "保持当前良好的心理状态",
                    "继续进行规律的体育锻炼",
                    "维持健康的社交关系"
                ])
            elif risk_level == RiskLevel.MODERATE:
                recommendations.extend([
                    "增加户外活动和阳光照射",
                    "尝试放松技巧，如深呼吸或冥想",
                    "与信任的朋友或家人分享感受"
                ])
            elif risk_level == RiskLevel.HIGH:
                recommendations.extend([
                    "考虑寻求心理咨询师的专业帮助",
                    "建立规律的作息时间",
                    "避免酒精和药物滥用"
                ])
            else:  # CRITICAL
                recommendations.extend([
                    "立即寻求精神科医生的专业治疗",
                    "考虑药物治疗的可能性",
                    "建立强有力的支持系统"
                ])
        
        elif assessment_type == AssessmentType.ANXIETY_SCALE:
            if risk_level == RiskLevel.LOW:
                recommendations.extend([
                    "继续保持良好的应对策略",
                    "定期进行放松练习",
                    "保持充足的睡眠"
                ])
            elif risk_level == RiskLevel.MODERATE:
                recommendations.extend([
                    "学习和练习焦虑管理技巧",
                    "限制咖啡因摄入",
                    "尝试渐进性肌肉放松"
                ])
            elif risk_level == RiskLevel.HIGH:
                recommendations.extend([
                    "寻求认知行为疗法(CBT)治疗",
                    "考虑参加焦虑症支持小组",
                    "学习正念冥想技巧"
                ])
            else:  # CRITICAL
                recommendations.extend([
                    "立即寻求专业医疗帮助",
                    "考虑短期药物干预",
                    "避免可能触发焦虑的情况"
                ])
        
        elif assessment_type == AssessmentType.STRESS_SCALE:
            if risk_level == RiskLevel.LOW:
                recommendations.extend([
                    "维持当前的压力管理策略",
                    "继续保持工作生活平衡",
                    "定期进行自我评估"
                ])
            elif risk_level == RiskLevel.MODERATE:
                recommendations.extend([
                    "学习时间管理技巧",
                    "设定现实的目标和期望",
                    "增加休闲和娱乐活动"
                ])
            else:  # HIGH
                recommendations.extend([
                    "重新评估生活优先级",
                    "寻求压力管理培训",
                    "考虑减少工作负荷"
                ])
        
        return recommendations
    
    def _analyze_mood_indicators(self, responses: Dict[str, Any]) -> float:
        """分析情绪指标"""
        mood_questions = ["mood_rating", "happiness_level", "sadness_frequency", "irritability"]
        scores = []
        
        for question in mood_questions:
            if question in responses:
                score = float(responses[question])
                if question in ["sadness_frequency", "irritability"]:
                    score = 1.0 - score  # 反向计分
                scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _analyze_cognitive_indicators(self, responses: Dict[str, Any]) -> float:
        """分析认知指标"""
        cognitive_questions = ["concentration", "memory", "decision_making", "negative_thoughts"]
        scores = []
        
        for question in cognitive_questions:
            if question in responses:
                score = float(responses[question])
                if question == "negative_thoughts":
                    score = 1.0 - score  # 反向计分
                scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _analyze_behavioral_indicators(self, responses: Dict[str, Any]) -> float:
        """分析行为指标"""
        behavioral_questions = ["activity_level", "social_engagement", "sleep_quality", "appetite"]
        scores = []
        
        for question in behavioral_questions:
            if question in responses:
                scores.append(float(responses[question]))
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _analyze_social_indicators(self, responses: Dict[str, Any]) -> float:
        """分析社交指标"""
        social_questions = ["relationship_satisfaction", "social_support", "communication", "isolation"]
        scores = []
        
        for question in social_questions:
            if question in responses:
                score = float(responses[question])
                if question == "isolation":
                    score = 1.0 - score  # 反向计分
                scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _generate_comprehensive_interpretation(
        self,
        mood_score: float,
        cognitive_score: float,
        behavioral_score: float,
        social_score: float,
        overall_score: float
    ) -> str:
        """生成综合解释"""
        interpretation = f"综合心理健康评估结果：总体得分 {overall_score:.2f}\n\n"
        
        interpretation += f"情绪状态：{mood_score:.2f} - "
        if mood_score >= 0.8:
            interpretation += "情绪状态良好，心情积极稳定\n"
        elif mood_score >= 0.6:
            interpretation += "情绪状态一般，偶有波动\n"
        elif mood_score >= 0.4:
            interpretation += "情绪状态较差，需要关注\n"
        else:
            interpretation += "情绪状态不佳，建议寻求帮助\n"
        
        interpretation += f"认知功能：{cognitive_score:.2f} - "
        if cognitive_score >= 0.8:
            interpretation += "认知功能正常，思维清晰\n"
        elif cognitive_score >= 0.6:
            interpretation += "认知功能基本正常，略有影响\n"
        elif cognitive_score >= 0.4:
            interpretation += "认知功能受到一定影响\n"
        else:
            interpretation += "认知功能明显受损\n"
        
        interpretation += f"行为表现：{behavioral_score:.2f} - "
        if behavioral_score >= 0.8:
            interpretation += "行为表现正常，生活规律\n"
        elif behavioral_score >= 0.6:
            interpretation += "行为表现基本正常，略有变化\n"
        elif behavioral_score >= 0.4:
            interpretation += "行为表现有所改变\n"
        else:
            interpretation += "行为表现明显异常\n"
        
        interpretation += f"社交功能：{social_score:.2f} - "
        if social_score >= 0.8:
            interpretation += "社交功能良好，人际关系和谐\n"
        elif social_score >= 0.6:
            interpretation += "社交功能基本正常\n"
        elif social_score >= 0.4:
            interpretation += "社交功能有所下降\n"
        else:
            interpretation += "社交功能明显受损\n"
        
        return interpretation
    
    def _generate_comprehensive_recommendations(
        self,
        mood_score: float,
        cognitive_score: float,
        behavioral_score: float,
        social_score: float,
        risk_level: RiskLevel
    ) -> List[str]:
        """生成综合建议"""
        recommendations = []
        
        # 基于各维度得分的具体建议
        if mood_score < 0.6:
            recommendations.extend([
                "练习情绪调节技巧，如深呼吸和正念",
                "保持规律的运动习惯",
                "寻找积极的情绪出口"
            ])
        
        if cognitive_score < 0.6:
            recommendations.extend([
                "进行认知训练活动，如阅读、解谜",
                "保证充足的睡眠",
                "减少多任务处理"
            ])
        
        if behavioral_score < 0.6:
            recommendations.extend([
                "建立规律的日常作息",
                "设定小而可实现的目标",
                "增加有意义的活动"
            ])
        
        if social_score < 0.6:
            recommendations.extend([
                "主动维护重要的人际关系",
                "参加社交活动或兴趣小组",
                "寻求社会支持"
            ])
        
        # 基于风险等级的建议
        if risk_level == RiskLevel.HIGH:
            recommendations.append("建议寻求专业心理咨询")
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.append("强烈建议立即寻求专业医疗帮助")
        
        return recommendations
    
    def _calculate_follow_up_date(self, risk_level: RiskLevel) -> datetime:
        """计算随访日期"""
        days_map = {
            RiskLevel.LOW: 90,      # 3个月
            RiskLevel.MODERATE: 30, # 1个月
            RiskLevel.HIGH: 14,     # 2周
            RiskLevel.CRITICAL: 7   # 1周
        }
        return datetime.now() + timedelta(days=days_map[risk_level])


class CrisisInterventionSystem:
    """危机干预系统"""
    
    def __init__(self):
        self.crisis_protocols = self._load_crisis_protocols()
        self.emergency_contacts = self._load_emergency_contacts()
        
    def _load_crisis_protocols(self) -> Dict[str, Any]:
        """加载危机干预协议"""
        return {
            "suicide_risk_protocol": {
                "immediate_actions": [
                    "确保个人安全",
                    "移除潜在危险物品",
                    "保持持续监护",
                    "联系紧急服务"
                ],
                "assessment_questions": [
                    "您是否有伤害自己的想法？",
                    "您是否有具体的计划？",
                    "您是否有实施的方法？",
                    "您是否设定了时间？"
                ],
                "safety_planning": [
                    "识别警告信号",
                    "制定应对策略",
                    "建立支持网络",
                    "移除危险因素"
                ]
            },
            "acute_anxiety_protocol": {
                "immediate_actions": [
                    "引导深呼吸",
                    "使用接地技巧",
                    "提供安全环境",
                    "保持冷静陪伴"
                ],
                "coping_strategies": [
                    "4-7-8呼吸法",
                    "5-4-3-2-1感官技巧",
                    "渐进性肌肉放松",
                    "正念观察"
                ]
            },
            "psychotic_episode_protocol": {
                "immediate_actions": [
                    "保持冷静和非威胁性",
                    "避免争论或纠正妄想",
                    "确保环境安全",
                    "寻求专业帮助"
                ],
                "communication_guidelines": [
                    "使用简单清晰的语言",
                    "保持眼神接触",
                    "避免突然动作",
                    "表达理解和支持"
                ]
            }
        }
    
    def _load_emergency_contacts(self) -> Dict[str, Any]:
        """加载紧急联系方式"""
        return {
            "crisis_hotlines": [
                {"name": "全国心理危机干预热线", "number": "400-161-9995"},
                {"name": "北京危机干预热线", "number": "400-161-9995"},
                {"name": "上海心理援助热线", "number": "021-64383562"}
            ],
            "emergency_services": [
                {"name": "急救中心", "number": "120"},
                {"name": "公安报警", "number": "110"},
                {"name": "消防救援", "number": "119"}
            ],
            "professional_services": [
                {"name": "心理咨询预约", "number": "400-xxx-xxxx"},
                {"name": "精神科急诊", "number": "xxx-xxx-xxxx"}
            ]
        }
    
    async def assess_crisis_risk(
        self,
        user_id: str,
        assessment_data: Dict[str, Any],
        recent_records: List[EmotionRecord] = None
    ) -> CrisisAssessment:
        """评估危机风险"""
        
        # 分析风险因素
        risk_factors = self._identify_risk_factors(assessment_data, recent_records)
        
        # 分析保护因素
        protective_factors = self._identify_protective_factors(assessment_data)
        
        # 计算自杀风险
        suicide_risk_score = self._calculate_suicide_risk(assessment_data, risk_factors)
        
        # 计算自伤风险
        self_harm_risk_score = self._calculate_self_harm_risk(assessment_data, risk_factors)
        
        # 确定紧急程度
        emergency_level = self._determine_emergency_level(suicide_risk_score, self_harm_risk_score)
        
        # 生成即时安全关注
        immediate_safety_concerns = self._identify_immediate_concerns(assessment_data, emergency_level)
        
        # 生成推荐行动
        recommended_actions = self._generate_crisis_actions(emergency_level, risk_factors)
        
        # 判断是否需要立即干预
        requires_immediate_intervention = emergency_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # 判断是否需要专业转介
        professional_referral_needed = emergency_level != RiskLevel.LOW
        
        return CrisisAssessment(
            user_id=user_id,
            assessment_time=datetime.now(),
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            suicide_risk_score=suicide_risk_score,
            self_harm_risk_score=self_harm_risk_score,
            immediate_safety_concerns=immediate_safety_concerns,
            recommended_actions=recommended_actions,
            emergency_level=emergency_level,
            requires_immediate_intervention=requires_immediate_intervention,
            professional_referral_needed=professional_referral_needed
        )
    
    def _identify_risk_factors(self, assessment_data: Dict[str, Any], recent_records: List[EmotionRecord] = None) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        # 检查直接的自杀/自伤想法
        if assessment_data.get("suicidal_thoughts", False):
            risk_factors.append("有自杀想法")
        
        if assessment_data.get("self_harm_thoughts", False):
            risk_factors.append("有自伤想法")
        
        if assessment_data.get("suicide_plan", False):
            risk_factors.append("有自杀计划")
        
        # 检查既往史
        if assessment_data.get("previous_suicide_attempt", False):
            risk_factors.append("既往自杀未遂史")
        
        if assessment_data.get("previous_self_harm", False):
            risk_factors.append("既往自伤史")
        
        # 检查心理健康状况
        if assessment_data.get("depression_score", 0) > 0.7:
            risk_factors.append("严重抑郁症状")
        
        if assessment_data.get("anxiety_score", 0) > 0.7:
            risk_factors.append("严重焦虑症状")
        
        if assessment_data.get("hopelessness_score", 0) > 0.7:
            risk_factors.append("严重绝望感")
        
        # 检查社会因素
        if assessment_data.get("social_isolation", False):
            risk_factors.append("社会孤立")
        
        if assessment_data.get("recent_loss", False):
            risk_factors.append("近期重大丧失")
        
        if assessment_data.get("financial_stress", False):
            risk_factors.append("经济压力")
        
        # 检查物质使用
        if assessment_data.get("substance_abuse", False):
            risk_factors.append("物质滥用")
        
        # 分析近期情绪记录
        if recent_records:
            negative_emotions = [EmotionType.DEPRESSION, EmotionType.SADNESS, EmotionType.ANXIETY, EmotionType.FEAR]
            recent_negative_count = sum(1 for record in recent_records[-10:] 
                                      if record.emotion_type in negative_emotions and record.intensity > 0.7)
            
            if recent_negative_count >= 5:
                risk_factors.append("近期持续负面情绪")
        
        return risk_factors
    
    def _identify_protective_factors(self, assessment_data: Dict[str, Any]) -> List[str]:
        """识别保护因素"""
        protective_factors = []
        
        if assessment_data.get("strong_social_support", False):
            protective_factors.append("强有力的社会支持")
        
        if assessment_data.get("good_coping_skills", False):
            protective_factors.append("良好的应对技能")
        
        if assessment_data.get("religious_beliefs", False):
            protective_factors.append("宗教或精神信仰")
        
        if assessment_data.get("access_to_mental_health_care", False):
            protective_factors.append("可获得心理健康服务")
        
        if assessment_data.get("stable_relationships", False):
            protective_factors.append("稳定的人际关系")
        
        if assessment_data.get("sense_of_responsibility", False):
            protective_factors.append("责任感和义务感")
        
        if assessment_data.get("future_oriented", False):
            protective_factors.append("未来导向的思维")
        
        if assessment_data.get("problem_solving_skills", False):
            protective_factors.append("问题解决能力")
        
        return protective_factors
    
    def _calculate_suicide_risk(self, assessment_data: Dict[str, Any], risk_factors: List[str]) -> float:
        """计算自杀风险评分"""
        base_score = 0.0
        
        # 直接风险因素权重
        if "有自杀想法" in risk_factors:
            base_score += 0.3
        
        if "有自杀计划" in risk_factors:
            base_score += 0.4
        
        if "既往自杀未遂史" in risk_factors:
            base_score += 0.2
        
        # 间接风险因素
        if "严重抑郁症状" in risk_factors:
            base_score += 0.15
        
        if "严重绝望感" in risk_factors:
            base_score += 0.15
        
        if "社会孤立" in risk_factors:
            base_score += 0.1
        
        if "物质滥用" in risk_factors:
            base_score += 0.1
        
        # 其他风险因素
        other_risk_count = len([rf for rf in risk_factors if rf not in [
            "有自杀想法", "有自杀计划", "既往自杀未遂史", 
            "严重抑郁症状", "严重绝望感", "社会孤立", "物质滥用"
        ]])
        base_score += other_risk_count * 0.05
        
        return min(1.0, base_score)
    
    def _calculate_self_harm_risk(self, assessment_data: Dict[str, Any], risk_factors: List[str]) -> float:
        """计算自伤风险评分"""
        base_score = 0.0
        
        if "有自伤想法" in risk_factors:
            base_score += 0.4
        
        if "既往自伤史" in risk_factors:
            base_score += 0.3
        
        if "严重焦虑症状" in risk_factors:
            base_score += 0.2
        
        if "近期持续负面情绪" in risk_factors:
            base_score += 0.15
        
        # 年龄因素（青少年和年轻成人风险较高）
        age = assessment_data.get("age", 30)
        if 13 <= age <= 25:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _determine_emergency_level(self, suicide_risk_score: float, self_harm_risk_score: float) -> RiskLevel:
        """确定紧急程度"""
        max_risk = max(suicide_risk_score, self_harm_risk_score)
        
        if max_risk >= 0.8:
            return RiskLevel.CRITICAL
        elif max_risk >= 0.6:
            return RiskLevel.HIGH
        elif max_risk >= 0.3:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def _identify_immediate_concerns(self, assessment_data: Dict[str, Any], emergency_level: RiskLevel) -> List[str]:
        """识别即时安全关注"""
        concerns = []
        
        if emergency_level == RiskLevel.CRITICAL:
            concerns.extend([
                "存在即时自杀或自伤风险",
                "需要24小时监护",
                "可能需要住院治疗"
            ])
        elif emergency_level == RiskLevel.HIGH:
            concerns.extend([
                "存在较高的自杀或自伤风险",
                "需要密切监护",
                "应移除潜在危险物品"
            ])
        elif emergency_level == RiskLevel.MODERATE:
            concerns.extend([
                "存在一定的心理健康风险",
                "需要定期评估",
                "建议增加支持"
            ])
        
        # 检查特定关注点
        if assessment_data.get("access_to_means", False):
            concerns.append("有获得自杀手段的途径")
        
        if assessment_data.get("social_isolation", False):
            concerns.append("缺乏社会支持")
        
        if assessment_data.get("substance_use", False):
            concerns.append("物质使用可能增加冲动性")
        
        return concerns
    
    def _generate_crisis_actions(self, emergency_level: RiskLevel, risk_factors: List[str]) -> List[str]:
        """生成危机行动建议"""
        actions = []
        
        if emergency_level == RiskLevel.CRITICAL:
            actions.extend([
                "立即联系紧急服务(120或110)",
                "确保个人不独处",
                "移除所有潜在危险物品",
                "联系精神科急诊",
                "通知紧急联系人",
                "考虑非自愿住院治疗"
            ])
        elif emergency_level == RiskLevel.HIGH:
            actions.extend([
                "联系心理危机干预热线",
                "安排紧急心理咨询",
                "确保有人陪伴",
                "制定安全计划",
                "联系信任的朋友或家人",
                "考虑短期住院评估"
            ])
        elif emergency_level == RiskLevel.MODERATE:
            actions.extend([
                "安排心理咨询预约",
                "增加社会支持",
                "制定应对策略",
                "定期风险评估",
                "考虑药物治疗评估"
            ])
        else:  # LOW
            actions.extend([
                "继续监测心理状态",
                "维持现有支持系统",
                "定期自我评估",
                "保持健康的生活方式"
            ])
        
        # 基于特定风险因素的行动
        if "物质滥用" in risk_factors:
            actions.append("寻求物质滥用治疗")
        
        if "社会孤立" in risk_factors:
            actions.append("建立或重建社会联系")
        
        return actions


class InterventionPlanGenerator:
    """干预计划生成器"""
    
    def __init__(self):
        self.intervention_templates = self._load_intervention_templates()
        
    def _load_intervention_templates(self) -> Dict[str, Any]:
        """加载干预模板"""
        return {
            "depression_intervention": {
                "name": "抑郁症干预计划",
                "duration_weeks": 12,
                "intervention_types": [
                    InterventionType.COGNITIVE_BEHAVIORAL,
                    InterventionType.PHYSICAL_ACTIVITY,
                    InterventionType.SOCIAL_SUPPORT
                ],
                "daily_activities": [
                    {"activity": "情绪记录", "duration_minutes": 10, "frequency": "daily"},
                    {"activity": "体育锻炼", "duration_minutes": 30, "frequency": "daily"},
                    {"activity": "社交互动", "duration_minutes": 60, "frequency": "daily"},
                    {"activity": "正念练习", "duration_minutes": 15, "frequency": "daily"}
                ],
                "weekly_goals": [
                    "完成每日情绪记录",
                    "进行至少5次体育锻炼",
                    "参与至少3次有意义的社交活动",
                    "练习认知重构技巧"
                ]
            },
            "anxiety_intervention": {
                "name": "焦虑症干预计划",
                "duration_weeks": 8,
                "intervention_types": [
                    InterventionType.RELAXATION,
                    InterventionType.BREATHING_EXERCISE,
                    InterventionType.MINDFULNESS
                ],
                "daily_activities": [
                    {"activity": "深呼吸练习", "duration_minutes": 10, "frequency": "3x daily"},
                    {"activity": "渐进性肌肉放松", "duration_minutes": 20, "frequency": "daily"},
                    {"activity": "正念冥想", "duration_minutes": 15, "frequency": "daily"},
                    {"activity": "焦虑日记", "duration_minutes": 10, "frequency": "daily"}
                ],
                "weekly_goals": [
                    "掌握深呼吸技巧",
                    "完成每日放松练习",
                    "识别焦虑触发因素",
                    "练习应对策略"
                ]
            },
            "stress_management": {
                "name": "压力管理计划",
                "duration_weeks": 6,
                "intervention_types": [
                    InterventionType.RELAXATION,
                    InterventionType.LIFESTYLE_CHANGE,
                    InterventionType.PHYSICAL_ACTIVITY
                ],
                "daily_activities": [
                    {"activity": "压力评估", "duration_minutes": 5, "frequency": "3x daily"},
                    {"activity": "放松技巧", "duration_minutes": 15, "frequency": "daily"},
                    {"activity": "时间管理", "duration_minutes": 30, "frequency": "daily"},
                    {"activity": "运动锻炼", "duration_minutes": 30, "frequency": "daily"}
                ],
                "weekly_goals": [
                    "识别主要压力源",
                    "实施时间管理策略",
                    "保持规律运动",
                    "练习放松技巧"
                ]
            },
            "tcm_emotional_regulation": {
                "name": "中医情志调节计划",
                "duration_weeks": 10,
                "intervention_types": [
                    InterventionType.TCM_THERAPY,
                    InterventionType.MEDITATION,
                    InterventionType.LIFESTYLE_CHANGE
                ],
                "daily_activities": [
                    {"activity": "穴位按摩", "duration_minutes": 15, "frequency": "daily"},
                    {"activity": "八段锦练习", "duration_minutes": 20, "frequency": "daily"},
                    {"activity": "情志调节", "duration_minutes": 10, "frequency": "daily"},
                    {"activity": "饮食调理", "duration_minutes": 30, "frequency": "daily"}
                ],
                "weekly_goals": [
                    "掌握情志调节方法",
                    "坚持中医养生功法",
                    "调整饮食结构",
                    "保持情绪平衡"
                ]
            }
        }
    
    async def generate_intervention_plan(
        self,
        user_id: str,
        assessment_result: PsychologicalAssessment,
        tcm_analysis: Optional[TCMEmotionAnalysis] = None,
        preferences: Dict[str, Any] = None
    ) -> InterventionPlan:
        """生成干预计划"""
        
        # 选择合适的模板
        template = self._select_intervention_template(assessment_result, tcm_analysis, preferences)
        
        # 个性化调整
        personalized_plan = await self._personalize_intervention_plan(
            template, user_id, assessment_result, tcm_analysis, preferences
        )
        
        # 生成计划ID
        plan_id = f"intervention_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 计算日期
        start_date = datetime.now()
        end_date = start_date + timedelta(weeks=template["duration_weeks"])
        
        # 生成紧急联系人
        emergency_contacts = self._generate_emergency_contacts(assessment_result.risk_level)
        
        # 生成危机计划
        crisis_plan = self._generate_crisis_plan(assessment_result.risk_level)
        
        return InterventionPlan(
            user_id=user_id,
            plan_id=plan_id,
            name=personalized_plan["name"],
            description=personalized_plan["description"],
            intervention_types=template["intervention_types"],
            target_conditions=self._identify_target_conditions(assessment_result),
            start_date=start_date,
            end_date=end_date,
            daily_activities=personalized_plan["daily_activities"],
            weekly_goals=personalized_plan["weekly_goals"],
            progress_metrics=self._generate_progress_metrics(template["intervention_types"]),
            emergency_contacts=emergency_contacts,
            crisis_plan=crisis_plan
        )
    
    def _select_intervention_template(
        self,
        assessment_result: PsychologicalAssessment,
        tcm_analysis: Optional[TCMEmotionAnalysis] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """选择干预模板"""
        
        # 基于评估结果选择主要模板
        if assessment_result.assessment_type == AssessmentType.DEPRESSION_SCALE:
            if assessment_result.scores.get("depression_scale", 0) > 0.6:
                return self.intervention_templates["depression_intervention"]
        
        elif assessment_result.assessment_type == AssessmentType.ANXIETY_SCALE:
            if assessment_result.scores.get("anxiety_scale", 0) > 0.6:
                return self.intervention_templates["anxiety_intervention"]
        
        elif assessment_result.assessment_type == AssessmentType.STRESS_SCALE:
            return self.intervention_templates["stress_management"]
        
        # 如果有中医分析且用户偏好中医方法
        if tcm_analysis and preferences and preferences.get("prefer_tcm", False):
            return self.intervention_templates["tcm_emotional_regulation"]
        
        # 综合评估的情况
        if assessment_result.assessment_type == AssessmentType.COMPREHENSIVE:
            mood_score = assessment_result.scores.get("mood", 0.5)
            if mood_score < 0.4:
                return self.intervention_templates["depression_intervention"]
            elif assessment_result.scores.get("overall", 0.5) < 0.6:
                return self.intervention_templates["stress_management"]
        
        # 默认返回压力管理模板
        return self.intervention_templates["stress_management"]
    
    async def _personalize_intervention_plan(
        self,
        template: Dict[str, Any],
        user_id: str,
        assessment_result: PsychologicalAssessment,
        tcm_analysis: Optional[TCMEmotionAnalysis] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """个性化干预计划"""
        
        personalized = template.copy()
        
        # 个性化名称和描述
        personalized["name"] = f"{template['name']} - {user_id}"
        personalized["description"] = f"基于个人评估结果定制的{template['name']}"
        
        # 调整活动强度和频率
        if preferences:
            activity_level = preferences.get("activity_level", "moderate")
            
            for activity in personalized["daily_activities"]:
                if activity_level == "low":
                    activity["duration_minutes"] = int(activity["duration_minutes"] * 0.7)
                elif activity_level == "high":
                    activity["duration_minutes"] = int(activity["duration_minutes"] * 1.3)
        
        # 基于风险等级调整
        if assessment_result.risk_level == RiskLevel.HIGH:
            # 增加监测频率
            personalized["daily_activities"].append({
                "activity": "风险自评", 
                "duration_minutes": 5, 
                "frequency": "3x daily"
            })
        
        # 添加中医元素（如果适用）
        if tcm_analysis:
            tcm_activities = self._generate_tcm_activities(tcm_analysis)
            personalized["daily_activities"].extend(tcm_activities)
        
        return personalized
    
    def _identify_target_conditions(self, assessment_result: PsychologicalAssessment) -> List[str]:
        """识别目标症状"""
        conditions = []
        
        if assessment_result.assessment_type == AssessmentType.DEPRESSION_SCALE:
            conditions.append("抑郁症状")
        elif assessment_result.assessment_type == AssessmentType.ANXIETY_SCALE:
            conditions.append("焦虑症状")
        elif assessment_result.assessment_type == AssessmentType.STRESS_SCALE:
            conditions.append("压力症状")
        
        # 基于风险等级添加
        if assessment_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            conditions.append("自杀/自伤风险")
        
        return conditions
    
    def _generate_progress_metrics(self, intervention_types: List[InterventionType]) -> List[str]:
        """生成进度指标"""
        metrics = [
            "症状严重程度评分",
            "功能改善程度",
            "生活质量评分",
            "治疗依从性"
        ]
        
        if InterventionType.PHYSICAL_ACTIVITY in intervention_types:
            metrics.append("运动完成率")
        
        if InterventionType.MINDFULNESS in intervention_types:
            metrics.append("正念练习频率")
        
        if InterventionType.SOCIAL_SUPPORT in intervention_types:
            metrics.append("社交活动参与度")
        
        return metrics
    
    def _generate_emergency_contacts(self, risk_level: RiskLevel) -> List[Dict[str, str]]:
        """生成紧急联系人"""
        contacts = [
            {"name": "心理危机干预热线", "phone": "400-161-9995", "type": "hotline"},
            {"name": "急救中心", "phone": "120", "type": "emergency"}
        ]
        
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            contacts.extend([
                {"name": "精神科急诊", "phone": "xxx-xxx-xxxx", "type": "medical"},
                {"name": "公安报警", "phone": "110", "type": "police"}
            ])
        
        return contacts
    
    def _generate_crisis_plan(self, risk_level: RiskLevel) -> str:
        """生成危机计划"""
        if risk_level == RiskLevel.CRITICAL:
            return """
            危机计划：
            1. 如有自杀或自伤想法，立即联系120或110
            2. 移除所有潜在危险物品
            3. 确保不独处，联系信任的人陪伴
            4. 联系心理危机干预热线：400-161-9995
            5. 前往最近的精神科急诊科
            """
        elif risk_level == RiskLevel.HIGH:
            return """
            危机计划：
            1. 如感到无法应对，立即联系心理危机干预热线
            2. 联系信任的朋友或家人
            3. 使用学到的应对技巧
            4. 如情况恶化，寻求专业帮助
            """
        else:
            return """
            应对计划：
            1. 识别早期警告信号
            2. 使用学到的应对策略
            3. 寻求社会支持
            4. 必要时联系心理咨询师
            """
    
    def _generate_tcm_activities(self, tcm_analysis: TCMEmotionAnalysis) -> List[Dict[str, Any]]:
        """生成中医活动"""
        activities = []
        
        # 基于主导情志添加特定活动
        if tcm_analysis.dominant_emotion == TCMEmotion.ANGER:
            activities.extend([
                {"activity": "太冲穴按摩", "duration_minutes": 10, "frequency": "daily"},
                {"activity": "疏肝理气茶饮", "duration_minutes": 5, "frequency": "daily"}
            ])
        elif tcm_analysis.dominant_emotion == TCMEmotion.WORRY:
            activities.extend([
                {"activity": "足三里穴按摩", "duration_minutes": 10, "frequency": "daily"},
                {"activity": "健脾养胃粥", "duration_minutes": 20, "frequency": "daily"}
            ])
        
        # 添加通用中医活动
        activities.extend([
            {"activity": "八段锦练习", "duration_minutes": 20, "frequency": "daily"},
            {"activity": "情志调节冥想", "duration_minutes": 15, "frequency": "daily"}
        ])
        
        return activities


class IntelligentMentalHealthEngine:
    """智能心理健康引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.emotion_analyzer = None
        self.mental_health_assessor = None
        self.crisis_intervention_system = None
        self.intervention_plan_generator = None
        
        # 数据存储
        self.emotion_records: Dict[str, List[EmotionRecord]] = {}
        self.mood_entries: Dict[str, List[MoodEntry]] = {}
        self.assessments: Dict[str, List[PsychologicalAssessment]] = {}
        self.tcm_analyses: Dict[str, List[TCMEmotionAnalysis]] = {}
        self.intervention_plans: Dict[str, List[InterventionPlan]] = {}
        self.crisis_assessments: Dict[str, List[CrisisAssessment]] = {}
        
        logger.info("智能心理健康引擎初始化完成")
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._load_configuration()
            await self._initialize_components()
            logger.info("智能心理健康引擎初始化成功")
        except Exception as e:
            logger.error(f"智能心理健康引擎初始化失败: {e}")
            raise
    
    async def _load_configuration(self):
        """加载配置"""
        # 加载默认配置
        self.config.setdefault("emotion_analysis", {
            "sentiment_threshold": 0.5,
            "emotion_history_days": 30
        })
        
        self.config.setdefault("assessment", {
            "auto_assessment_interval_days": 7,
            "crisis_assessment_threshold": 0.7
        })
        
        self.config.setdefault("intervention", {
            "plan_duration_weeks": 8,
            "follow_up_interval_days": 7
        })
    
    async def _initialize_components(self):
        """初始化组件"""
        self.emotion_analyzer = EmotionAnalyzer()
        self.mental_health_assessor = MentalHealthAssessor()
        self.crisis_intervention_system = CrisisInterventionSystem()
        self.intervention_plan_generator = InterventionPlanGenerator()
    
    @trace_operation("mental_health_engine.record_emotion", SpanKind.INTERNAL)
    async def record_emotion(
        self,
        user_id: str,
        emotion_data: Dict[str, Any]
    ) -> EmotionRecord:
        """记录情绪"""
        try:
            # 创建情绪记录
            emotion_record = EmotionRecord(
                user_id=user_id,
                timestamp=datetime.now(),
                emotion_type=EmotionType(emotion_data["emotion_type"]),
                intensity=float(emotion_data["intensity"]),
                duration_minutes=emotion_data.get("duration_minutes"),
                triggers=emotion_data.get("triggers", []),
                context=emotion_data.get("context"),
                physical_symptoms=emotion_data.get("physical_symptoms", []),
                coping_strategies=emotion_data.get("coping_strategies", []),
                notes=emotion_data.get("notes")
            )
            
            # 存储记录
            if user_id not in self.emotion_records:
                self.emotion_records[user_id] = []
            self.emotion_records[user_id].append(emotion_record)
            
            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "emotion_records_total",
                    {"user_id": user_id, "emotion_type": emotion_record.emotion_type.value}
                )
            
            # 检查是否需要危机评估
            await self._check_crisis_indicators(user_id, emotion_record)
            
            logger.info(f"用户 {user_id} 情绪记录已保存: {emotion_record.emotion_type}")
            return emotion_record
            
        except Exception as e:
            logger.error(f"记录情绪失败: {e}")
            raise
    
    @trace_operation("mental_health_engine.record_mood", SpanKind.INTERNAL)
    async def record_mood_entry(
        self,
        user_id: str,
        mood_data: Dict[str, Any]
    ) -> MoodEntry:
        """记录心情"""
        try:
            mood_entry = MoodEntry(
                user_id=user_id,
                date=datetime.now(),
                mood_score=float(mood_data["mood_score"]),
                energy_level=float(mood_data["energy_level"]),
                sleep_quality=float(mood_data["sleep_quality"]),
                stress_level=StressLevel(mood_data["stress_level"]),
                dominant_emotions=[EmotionType(e) for e in mood_data.get("dominant_emotions", [])],
                activities=mood_data.get("activities", []),
                social_interactions=int(mood_data.get("social_interactions", 0)),
                exercise_minutes=int(mood_data.get("exercise_minutes", 0)),
                meditation_minutes=int(mood_data.get("meditation_minutes", 0)),
                notes=mood_data.get("notes")
            )
            
            # 存储记录
            if user_id not in self.mood_entries:
                self.mood_entries[user_id] = []
            self.mood_entries[user_id].append(mood_entry)
            
            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.record_histogram(
                    "mood_score",
                    mood_entry.mood_score,
                    {"user_id": user_id}
                )
            
            logger.info(f"用户 {user_id} 心情记录已保存: 评分 {mood_entry.mood_score}")
            return mood_entry
            
        except Exception as e:
            logger.error(f"记录心情失败: {e}")
            raise
    
    @trace_operation("mental_health_engine.conduct_assessment", SpanKind.INTERNAL)
    async def conduct_psychological_assessment(
        self,
        user_id: str,
        assessment_type: AssessmentType,
        responses: Dict[str, Any]
    ) -> PsychologicalAssessment:
        """进行心理评估"""
        try:
            # 进行评估
            assessment = await self.mental_health_assessor.conduct_assessment(
                user_id, assessment_type, responses
            )
            
            # 存储评估结果
            if user_id not in self.assessments:
                self.assessments[user_id] = []
            self.assessments[user_id].append(assessment)
            
            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "psychological_assessments_total",
                    {"user_id": user_id, "assessment_type": assessment_type.value, "risk_level": assessment.risk_level.value}
                )
            
            # 如果风险等级较高，进行危机评估
            if assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                await self._conduct_crisis_assessment(user_id, responses)
            
            logger.info(f"用户 {user_id} 心理评估完成: {assessment_type.value}, 风险等级: {assessment.risk_level.value}")
            return assessment
            
        except Exception as e:
            logger.error(f"心理评估失败: {e}")
            raise
    
    @trace_operation("mental_health_engine.analyze_tcm_emotions", SpanKind.INTERNAL)
    async def analyze_tcm_emotions(self, user_id: str) -> TCMEmotionAnalysis:
        """分析中医情志"""
        try:
            # 获取近期情绪记录
            recent_records = self._get_recent_emotion_records(user_id, days=30)
            
            # 进行中医情志分析
            tcm_analysis = await self.emotion_analyzer.analyze_tcm_emotions(recent_records)
            tcm_analysis.user_id = user_id
            
            # 存储分析结果
            if user_id not in self.tcm_analyses:
                self.tcm_analyses[user_id] = []
            self.tcm_analyses[user_id].append(tcm_analysis)
            
            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "tcm_emotion_analyses_total",
                    {"user_id": user_id, "dominant_emotion": tcm_analysis.dominant_emotion.value}
                )
            
            logger.info(f"用户 {user_id} 中医情志分析完成: 主导情志 {tcm_analysis.dominant_emotion.value}")
            return tcm_analysis
            
        except Exception as e:
            logger.error(f"中医情志分析失败: {e}")
            raise
    
    @trace_operation("mental_health_engine.generate_intervention_plan", SpanKind.INTERNAL)
    async def generate_intervention_plan(
        self,
        user_id: str,
        preferences: Dict[str, Any] = None
    ) -> InterventionPlan:
        """生成干预计划"""
        try:
            # 获取最新的评估结果
            latest_assessment = self._get_latest_assessment(user_id)
            if not latest_assessment:
                raise ValueError(f"用户 {user_id} 没有可用的评估结果")
            
            # 获取最新的中医分析
            latest_tcm_analysis = self._get_latest_tcm_analysis(user_id)
            
            # 生成干预计划
            intervention_plan = await self.intervention_plan_generator.generate_intervention_plan(
                user_id, latest_assessment, latest_tcm_analysis, preferences
            )
            
            # 存储计划
            if user_id not in self.intervention_plans:
                self.intervention_plans[user_id] = []
            self.intervention_plans[user_id].append(intervention_plan)
            
            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "intervention_plans_generated_total",
                    {"user_id": user_id}
                )
            
            logger.info(f"用户 {user_id} 干预计划生成完成: {intervention_plan.name}")
            return intervention_plan
            
        except Exception as e:
            logger.error(f"生成干预计划失败: {e}")
            raise
    
    async def _conduct_crisis_assessment(self, user_id: str, assessment_data: Dict[str, Any]) -> CrisisAssessment:
        """进行危机评估"""
        try:
            # 获取近期情绪记录
            recent_records = self._get_recent_emotion_records(user_id, days=7)
            
            # 进行危机评估
            crisis_assessment = await self.crisis_intervention_system.assess_crisis_risk(
                user_id, assessment_data, recent_records
            )
            
            # 存储评估结果
            if user_id not in self.crisis_assessments:
                self.crisis_assessments[user_id] = []
            self.crisis_assessments[user_id].append(crisis_assessment)
            
            # 如果需要立即干预，触发警报
            if crisis_assessment.requires_immediate_intervention:
                await self._trigger_crisis_alert(user_id, crisis_assessment)
            
            logger.info(f"用户 {user_id} 危机评估完成: 风险等级 {crisis_assessment.emergency_level.value}")
            return crisis_assessment
            
        except Exception as e:
            logger.error(f"危机评估失败: {e}")
            raise
    
    async def _check_crisis_indicators(self, user_id: str, emotion_record: EmotionRecord):
        """检查危机指标"""
        # 检查高强度负面情绪
        if (emotion_record.emotion_type in [EmotionType.DEPRESSION, EmotionType.SADNESS, EmotionType.ANXIETY] 
            and emotion_record.intensity > 0.8):
            
            # 检查是否有自杀/自伤相关的触发因素或症状
            crisis_keywords = ["自杀", "自伤", "死亡", "结束", "无望", "绝望"]
            
            triggers_text = " ".join(emotion_record.triggers)
            context_text = emotion_record.context or ""
            notes_text = emotion_record.notes or ""
            
            combined_text = f"{triggers_text} {context_text} {notes_text}".lower()
            
            if any(keyword in combined_text for keyword in crisis_keywords):
                # 触发危机评估
                assessment_data = {
                    "high_intensity_negative_emotion": True,
                    "crisis_keywords_detected": True,
                    "emotion_intensity": emotion_record.intensity
                }
                await self._conduct_crisis_assessment(user_id, assessment_data)
    
    async def _trigger_crisis_alert(self, user_id: str, crisis_assessment: CrisisAssessment):
        """触发危机警报"""
        logger.critical(f"危机警报: 用户 {user_id} 需要立即干预")
        
        # 这里可以集成实际的警报系统
        # 例如：发送通知给医护人员、家属等
        
        if self.metrics_collector:
            self.metrics_collector.increment_counter(
                "crisis_alerts_triggered_total",
                {"user_id": user_id, "emergency_level": crisis_assessment.emergency_level.value}
            )
    
    def _get_recent_emotion_records(self, user_id: str, days: int = 30) -> List[EmotionRecord]:
        """获取近期情绪记录"""
        if user_id not in self.emotion_records:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            record for record in self.emotion_records[user_id]
            if record.timestamp >= cutoff_date
        ]
    
    def _get_latest_assessment(self, user_id: str) -> Optional[PsychologicalAssessment]:
        """获取最新评估结果"""
        if user_id not in self.assessments or not self.assessments[user_id]:
            return None
        
        return max(self.assessments[user_id], key=lambda x: x.assessment_date)
    
    def _get_latest_tcm_analysis(self, user_id: str) -> Optional[TCMEmotionAnalysis]:
        """获取最新中医分析"""
        if user_id not in self.tcm_analyses or not self.tcm_analyses[user_id]:
            return None
        
        return max(self.tcm_analyses[user_id], key=lambda x: x.analysis_date)
    
    async def get_mental_health_summary(self, user_id: str) -> Dict[str, Any]:
        """获取心理健康摘要"""
        try:
            # 获取各类数据
            recent_emotions = self._get_recent_emotion_records(user_id, days=30)
            recent_moods = self.mood_entries.get(user_id, [])[-30:] if user_id in self.mood_entries else []
            latest_assessment = self._get_latest_assessment(user_id)
            latest_tcm_analysis = self._get_latest_tcm_analysis(user_id)
            active_plans = [plan for plan in self.intervention_plans.get(user_id, []) if plan.status == "active"]
            
            # 计算统计信息
            emotion_stats = self._calculate_emotion_statistics(recent_emotions)
            mood_trends = self._calculate_mood_trends(recent_moods)
            
            # 生成建议
            recommendations = self._generate_mental_health_recommendations(
                latest_assessment, latest_tcm_analysis, emotion_stats, mood_trends
            )
            
            summary = {
                "user_id": user_id,
                "summary_date": datetime.now().isoformat(),
                "emotion_statistics": emotion_stats,
                "mood_trends": mood_trends,
                "latest_assessment": {
                    "type": latest_assessment.assessment_type.value if latest_assessment else None,
                    "risk_level": latest_assessment.risk_level.value if latest_assessment else None,
                    "date": latest_assessment.assessment_date.isoformat() if latest_assessment else None
                } if latest_assessment else None,
                "tcm_analysis": {
                    "dominant_emotion": latest_tcm_analysis.dominant_emotion.value if latest_tcm_analysis else None,
                    "date": latest_tcm_analysis.analysis_date.isoformat() if latest_tcm_analysis else None
                } if latest_tcm_analysis else None,
                "active_intervention_plans": len(active_plans),
                "recommendations": recommendations
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取心理健康摘要失败: {e}")
            raise
    
    def _calculate_emotion_statistics(self, emotion_records: List[EmotionRecord]) -> Dict[str, Any]:
        """计算情绪统计"""
        if not emotion_records:
            return {"total_records": 0}
        
        # 情绪类型分布
        emotion_counts = {}
        total_intensity = 0
        
        for record in emotion_records:
            emotion_type = record.emotion_type.value
            emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            total_intensity += record.intensity
        
        # 最常见的情绪
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        # 平均强度
        average_intensity = total_intensity / len(emotion_records)
        
        # 负面情绪比例
        negative_emotions = [EmotionType.SADNESS, EmotionType.ANGER, EmotionType.FEAR, 
                           EmotionType.ANXIETY, EmotionType.DEPRESSION]
        negative_count = sum(1 for record in emotion_records if record.emotion_type in negative_emotions)
        negative_ratio = negative_count / len(emotion_records)
        
        return {
            "total_records": len(emotion_records),
            "emotion_distribution": emotion_counts,
            "most_common_emotion": most_common_emotion,
            "average_intensity": round(average_intensity, 2),
            "negative_emotion_ratio": round(negative_ratio, 2)
        }
    
    def _calculate_mood_trends(self, mood_entries: List[MoodEntry]) -> Dict[str, Any]:
        """计算心情趋势"""
        if not mood_entries:
            return {"total_entries": 0}
        
        # 按时间排序
        sorted_entries = sorted(mood_entries, key=lambda x: x.date)
        
        # 计算趋势
        mood_scores = [entry.mood_score for entry in sorted_entries]
        energy_levels = [entry.energy_level for entry in sorted_entries]
        sleep_qualities = [entry.sleep_quality for entry in sorted_entries]
        
        # 简单的趋势计算（最近7天 vs 之前7天）
        if len(mood_scores) >= 14:
            recent_mood = np.mean(mood_scores[-7:])
            previous_mood = np.mean(mood_scores[-14:-7])
            mood_trend = "improving" if recent_mood > previous_mood else "declining" if recent_mood < previous_mood else "stable"
        else:
            mood_trend = "insufficient_data"
        
        return {
            "total_entries": len(mood_entries),
            "average_mood_score": round(np.mean(mood_scores), 2),
            "average_energy_level": round(np.mean(energy_levels), 2),
            "average_sleep_quality": round(np.mean(sleep_qualities), 2),
            "mood_trend": mood_trend,
            "latest_mood_score": mood_scores[-1] if mood_scores else None
        }
    
    def _generate_mental_health_recommendations(
        self,
        latest_assessment: Optional[PsychologicalAssessment],
        latest_tcm_analysis: Optional[TCMEmotionAnalysis],
        emotion_stats: Dict[str, Any],
        mood_trends: Dict[str, Any]
    ) -> List[str]:
        """生成心理健康建议"""
        recommendations = []
        
        # 基于评估结果的建议
        if latest_assessment:
            if latest_assessment.risk_level == RiskLevel.HIGH:
                recommendations.append("建议寻求专业心理咨询")
            elif latest_assessment.risk_level == RiskLevel.CRITICAL:
                recommendations.append("强烈建议立即寻求专业医疗帮助")
        
        # 基于情绪统计的建议
        if emotion_stats.get("negative_emotion_ratio", 0) > 0.6:
            recommendations.append("注意到您最近负面情绪较多，建议增加积极活动")
        
        if emotion_stats.get("average_intensity", 0) > 0.7:
            recommendations.append("情绪强度较高，建议学习情绪调节技巧")
        
        # 基于心情趋势的建议
        if mood_trends.get("mood_trend") == "declining":
            recommendations.append("心情呈下降趋势，建议关注心理健康")
        
        if mood_trends.get("average_sleep_quality", 0) < 6:
            recommendations.append("睡眠质量较差，建议改善睡眠习惯")
        
        # 基于中医分析的建议
        if latest_tcm_analysis:
            if latest_tcm_analysis.dominant_emotion == TCMEmotion.ANGER:
                recommendations.append("建议进行疏肝理气的调理")
            elif latest_tcm_analysis.dominant_emotion == TCMEmotion.WORRY:
                recommendations.append("建议进行健脾益气的调理")
        
        # 通用建议
        if not recommendations:
            recommendations.extend([
                "保持规律的作息时间",
                "进行适量的体育锻炼",
                "维持良好的社交关系"
            ])
        
        return recommendations
    
    async def get_mental_health_statistics(self) -> Dict[str, Any]:
        """获取心理健康统计信息"""
        try:
            total_users = len(set(
                list(self.emotion_records.keys()) + 
                list(self.mood_entries.keys()) + 
                list(self.assessments.keys())
            ))
            
            total_emotion_records = sum(len(records) for records in self.emotion_records.values())
            total_mood_entries = sum(len(entries) for entries in self.mood_entries.values())
            total_assessments = sum(len(assessments) for assessments in self.assessments.values())
            total_intervention_plans = sum(len(plans) for plans in self.intervention_plans.values())
            
            # 风险等级分布
            risk_distribution = {}
            for user_assessments in self.assessments.values():
                for assessment in user_assessments:
                    risk_level = assessment.risk_level.value
                    risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # 危机评估统计
            crisis_assessments_count = sum(len(assessments) for assessments in self.crisis_assessments.values())
            
            return {
                "total_users": total_users,
                "total_emotion_records": total_emotion_records,
                "total_mood_entries": total_mood_entries,
                "total_assessments": total_assessments,
                "total_intervention_plans": total_intervention_plans,
                "total_crisis_assessments": crisis_assessments_count,
                "risk_level_distribution": risk_distribution,
                "statistics_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取心理健康统计信息失败: {e}")
            raise


def initialize_mental_health_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentMentalHealthEngine:
    """初始化智能心理健康引擎"""
    engine = IntelligentMentalHealthEngine(config, metrics_collector)
    return engine


def get_mental_health_engine() -> Optional[IntelligentMentalHealthEngine]:
    """获取智能心理健康引擎实例"""
    # 这里可以实现单例模式或从容器中获取
    return None 