from typing import Any, Dict, List, Optional, Union

"""
schemas - 索克生活项目模块
"""

import datetime

from pydantic import BaseModel, Field


# 用户模型
class User(BaseModel):
    """用户基础信息模型
    
    包含用户的基本标识信息、体质类型和个人偏好设置。
    用于个性化健康管理和推荐系统。
    """

    user_id: str
    constitution_type: str | None = None
    preferences: dict[str, list[str]] | None = None


# 健康计划相关模型
class HealthGoal(BaseModel):
    """健康目标模型
    
    定义用户的具体健康目标，包括目标类型、优先级和期望达成时间。
    支持多种健康目标的设定和跟踪。
    """

    goal_type: str = Field(..., description="目标类型，如'改善睡眠'、'增强体质'等")
    priority: float = Field(1.0, ge=0.0, le=1.0, description="优先级，0 - 1")
    target_date: datetime | None = Field(None, description="目标日期")
    description: str | None = None


class HealthPlanRequest(BaseModel):
    """健康计划请求模型
    
    用于请求生成个性化健康计划的输入数据，包含用户体质、
    健康目标、个人偏好和当前季节等信息。
    """

    user_id: str
    constitution_type: str
    health_goals: list[str]
    preferences: dict[str, list[str]]
    current_season: str


class HealthPlanResponse(BaseModel):
    """健康计划响应模型
    
    返回生成的个性化健康计划，包含饮食、运动、生活方式建议
    以及补充剂推荐和日程安排。
    """

    plan_id: str
    diet_recommendations: list[str]
    exercise_recommendations: list[str]
    lifestyle_recommendations: list[str]
    supplement_recommendations: list[str]
    schedule: dict[str, str]
    confidence_score: float


# 传感器数据相关模型
class DataPoint(BaseModel):
    """传感器数据点模型
    
    表示单个时间点的传感器测量数据，包含时间戳、
    测量值和相关元数据。
    """

    timestamp: datetime
    values: dict[str, float]
    metadata: dict[str, str] | None = None


class SensorData(BaseModel):
    """传感器数据集合模型
    
    包含特定传感器设备在一段时间内收集的所有数据点，
    用于健康监测和分析。
    """

    sensor_type: str
    device_id: str
    data_points: list[DataPoint]


class SensorDataRequest(BaseModel):
    """传感器数据分析请求模型
    
    用于提交用户的传感器数据进行健康分析，
    支持多种传感器设备的数据整合。
    """

    user_id: str
    data: list[SensorData]


class HealthMetric(BaseModel):
    """健康指标模型
    
    表示单个健康指标的当前值、参考范围、解释说明
    和变化趋势，用于健康状态评估。
    """

    metric_name: str
    current_value: float
    reference_min: float
    reference_max: float
    interpretation: str
    trend: str  # "improving", "stable", "declining"


class Insight(BaseModel):
    """健康洞察模型
    
    基于数据分析生成的健康洞察，包含分类、描述、
    置信度和相关建议。
    """

    category: str
    description: str
    confidence: float
    suggestions: list[str]


class SensorDataResponse(BaseModel):
    """传感器数据分析响应模型
    
    返回传感器数据的分析结果，包含健康指标评估
    和基于数据的健康洞察。
    """

    metrics: list[HealthMetric]
    insights: list[Insight]


# 营养相关模型
class FoodEntry(BaseModel):
    """食物条目模型
    
    记录用户摄入的单个食物信息，包含食物名称、数量、
    单位和摄入时间，用于营养分析。
    """

    food_name: str
    quantity: float
    unit: str
    timestamp: datetime
    properties: dict[str, str] | None = None


class NutritionRequest(BaseModel):
    """营养分析请求模型
    
    用于请求对用户的饮食记录进行营养分析，
    支持日度、周度和体质化分析。
    """

    user_id: str
    food_entries: list[FoodEntry]
    analysis_type: str  # "daily", "weekly", "constitutional"


class NutrientBalance(BaseModel):
    """营养素平衡模型
    
    表示单个营养素的当前摄入量、目标量和平衡状态，
    用于评估营养摄入的充足性。
    """

    nutrient: str
    current: float
    target: float
    status: str  # "excess", "balanced", "deficient"


class FoodSuggestion(BaseModel):
    """食物建议模型
    
    基于用户体质和营养状态生成的食物推荐，
    包含推荐强度和推荐理由。
    """

    food: str
    benefits: list[str]
    recommendation_strength: float  # 0 - 1
    reason: str


class ConstitutionalAnalysis(BaseModel):
    """体质化营养分析模型
    
    基于中医理论的体质化营养分析，包含五行平衡、
    五味分布和失衡纠正建议。
    """

    five_elements_balance: dict[str, float]  # 五行平衡
    five_tastes_distribution: dict[str, float]  # 五味分布
    imbalance_corrections: list[str]


class NutritionResponse(BaseModel):
    """营养分析响应模型
    
    返回营养分析结果，包含营养素摘要、平衡状态、
    食物建议和体质化分析。
    """

    nutrient_summary: dict[str, float]
    balance: list[NutrientBalance]
    suggestions: list[FoodSuggestion]
    constitutional_analysis: ConstitutionalAnalysis


# 睡眠相关模型
class SleepPhase(BaseModel):
    """睡眠阶段模型
    
    表示睡眠过程中的单个阶段，包含深睡、浅睡、
    REM睡眠和清醒状态。
    """

    phase_type: str  # "deep", "light", "rem", "awake"
    start_time: datetime
    end_time: datetime


class SleepData(BaseModel):
    """睡眠数据模型
    
    记录单次睡眠的完整数据，包含睡眠时间、各阶段详情、
    睡眠效率和夜间觉醒次数。
    """

    sleep_start: datetime
    sleep_end: datetime
    phases: list[SleepPhase]
    efficiency: float
    awakenings: int


class SleepRequest(BaseModel):
    """睡眠分析请求模型
    
    用于请求对用户的睡眠数据进行分析，结合体质类型
    和生活方式因素提供个性化建议。
    """

    user_id: str
    recent_sleep: list[SleepData]
    constitution_type: str
    lifestyle_factors: dict[str, str]


class SleepQuality(BaseModel):
    """睡眠质量评估模型
    
    提供睡眠质量的综合评分和各维度分数，
    指出需要改进的领域和积极方面。
    """

    overall_score: float
    component_scores: dict[str, float]
    improvement_areas: list[str]
    positive_aspects: list[str]


class SleepRecommendation(BaseModel):
    """睡眠建议模型
    
    基于睡眠分析结果提供的个性化建议，包含环境、
    作息、营养和冥想等方面的指导。
    """

    category: str  # "environment", "routine", "nutrition", "mindfulness"
    suggestion: str
    reasoning: str
    expected_impact: float  # 0 - 1
    is_personalized: bool


class SleepResponse(BaseModel):
    """睡眠分析响应模型
    
    返回睡眠分析结果，包含质量评估、个性化建议、
    环境因素和最佳作息时间。
    """

    sleep_quality: SleepQuality
    recommendations: list[SleepRecommendation]
    environmental_factors: list[str]
    optimal_sleep_schedule: str


# 情绪分析相关模型
class EmotionalInput(BaseModel):
    """情绪输入数据模型
    
    支持多种类型的情绪输入数据，包含文本、语音
    和生理指标，用于情绪状态分析。
    """

    input_type: str  # "text", "voice", "physiological"
    data: str  # Base64编码的数据
    metadata: dict[str, str] | None = None
    timestamp: datetime


class EmotionalStateRequest(BaseModel):
    """情绪状态分析请求模型
    
    用于请求对用户的情绪输入数据进行分析，
    支持多模态情绪识别。
    """

    user_id: str
    inputs: list[EmotionalInput]


class EmotionalImpact(BaseModel):
    """情绪健康影响模型
    
    分析情绪状态对身体健康的影响，包含受影响系统、
    中医解读和严重程度评估。
    """

    affected_systems: list[str]  # 受影响的身体系统
    tcm_interpretation: str  # 中医解读
    severity: float  # 0 - 1


class EmotionalSuggestion(BaseModel):
    """情绪干预建议模型
    
    基于情绪分析结果提供的干预建议，包含干预类型、
    描述、预期效果和紧急程度。
    """

    intervention_type: str
    description: str
    estimated_effectiveness: float
    is_urgent: bool


class EmotionalStateResponse(BaseModel):
    """情绪状态分析响应模型
    
    返回情绪分析结果，包含情绪识别结果、主要情绪、
    变化趋势、健康影响和干预建议。
    """

    emotion_scores: dict[str, float]  # 各种情绪的得分
    primary_emotion: str
    emotional_tendency: str  # "improving", "fluctuating", "declining"
    health_impact: EmotionalImpact
    suggestions: list[EmotionalSuggestion]
