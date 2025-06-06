"""
schemas - 索克生活项目模块
"""

from datetime import datetime
from pydantic import BaseModel, Field




# 用户模型
class User(BaseModel):
    user_id: str
    constitution_type: str | None = None
    preferences: dict[str, list[str]] | None = None

# 健康计划相关模型
class HealthGoal(BaseModel):
    goal_type: str = Field(..., description="目标类型，如'改善睡眠'、'增强体质'等")
    priority: float = Field(1.0, ge=0.0, le=1.0, description="优先级，0-1")
    target_date: datetime | None = Field(None, description="目标日期")
    description: str | None = None

class HealthPlanRequest(BaseModel):
    user_id: str
    constitution_type: str
    health_goals: list[str]
    preferences: dict[str, list[str]]
    current_season: str

class HealthPlanResponse(BaseModel):
    plan_id: str
    diet_recommendations: list[str]
    exercise_recommendations: list[str]
    lifestyle_recommendations: list[str]
    supplement_recommendations: list[str]
    schedule: dict[str, str]
    confidence_score: float

# 传感器数据相关模型
class DataPoint(BaseModel):
    timestamp: datetime
    values: dict[str, float]
    metadata: dict[str, str] | None = None

class SensorData(BaseModel):
    sensor_type: str
    device_id: str
    data_points: list[DataPoint]

class SensorDataRequest(BaseModel):
    user_id: str
    data: list[SensorData]

class HealthMetric(BaseModel):
    metric_name: str
    current_value: float
    reference_min: float
    reference_max: float
    interpretation: str
    trend: str  # "improving", "stable", "declining"

class Insight(BaseModel):
    category: str
    description: str
    confidence: float
    suggestions: list[str]

class SensorDataResponse(BaseModel):
    metrics: list[HealthMetric]
    insights: list[Insight]

# 营养相关模型
class FoodEntry(BaseModel):
    food_name: str
    quantity: float
    unit: str
    timestamp: datetime
    properties: dict[str, str] | None = None

class NutritionRequest(BaseModel):
    user_id: str
    food_entries: list[FoodEntry]
    analysis_type: str  # "daily", "weekly", "constitutional"

class NutrientBalance(BaseModel):
    nutrient: str
    current: float
    target: float
    status: str  # "excess", "balanced", "deficient"

class FoodSuggestion(BaseModel):
    food: str
    benefits: list[str]
    recommendation_strength: float  # 0-1
    reason: str

class ConstitutionalAnalysis(BaseModel):
    five_elements_balance: dict[str, float]  # 五行平衡
    five_tastes_distribution: dict[str, float]  # 五味分布
    imbalance_corrections: list[str]

class NutritionResponse(BaseModel):
    nutrient_summary: dict[str, float]
    balance: list[NutrientBalance]
    suggestions: list[FoodSuggestion]
    constitutional_analysis: ConstitutionalAnalysis

# 睡眠相关模型
class SleepPhase(BaseModel):
    phase_type: str  # "deep", "light", "rem", "awake"
    start_time: datetime
    end_time: datetime

class SleepData(BaseModel):
    sleep_start: datetime
    sleep_end: datetime
    phases: list[SleepPhase]
    efficiency: float
    awakenings: int

class SleepRequest(BaseModel):
    user_id: str
    recent_sleep: list[SleepData]
    constitution_type: str
    lifestyle_factors: dict[str, str]

class SleepQuality(BaseModel):
    overall_score: float
    component_scores: dict[str, float]
    improvement_areas: list[str]
    positive_aspects: list[str]

class SleepRecommendation(BaseModel):
    category: str  # "environment", "routine", "nutrition", "mindfulness"
    suggestion: str
    reasoning: str
    expected_impact: float  # 0-1
    is_personalized: bool

class SleepResponse(BaseModel):
    sleep_quality: SleepQuality
    recommendations: list[SleepRecommendation]
    environmental_factors: list[str]
    optimal_sleep_schedule: str

# 情绪分析相关模型
class EmotionalInput(BaseModel):
    input_type: str  # "text", "voice", "physiological"
    data: str  # Base64编码的数据
    metadata: dict[str, str] | None = None
    timestamp: datetime

class EmotionalStateRequest(BaseModel):
    user_id: str
    inputs: list[EmotionalInput]

class EmotionalImpact(BaseModel):
    affected_systems: list[str]  # 受影响的身体系统
    tcm_interpretation: str  # 中医解读
    severity: float  # 0-1

class EmotionalSuggestion(BaseModel):
    intervention_type: str
    description: str
    estimated_effectiveness: float
    is_urgent: bool

class EmotionalStateResponse(BaseModel):
    emotion_scores: dict[str, float]  # 各种情绪的得分
    primary_emotion: str
    emotional_tendency: str  # "improving", "fluctuating", "declining"
    health_impact: EmotionalImpact
    suggestions: list[EmotionalSuggestion]
