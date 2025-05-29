"""
健康画像数据模型
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PhysicalMetrics(BaseModel):
    """身体基础指标"""
    height: float | None = Field(None, description="身高(cm)")
    weight: float | None = Field(None, description="体重(kg)")
    bmi: float | None = Field(None, description="BMI指数")
    body_fat: float | None = Field(None, description="体脂率(%)")
    waist_circumference: float | None = Field(None, description="腰围(cm)")
    blood_pressure: dict[str, float] | None = Field(None, description="血压，包含收缩压(systolic)和舒张压(diastolic)")


class VitalSigns(BaseModel):
    """生命体征"""
    heart_rate: dict[str, Any] | None = Field(None, description="心率(次/分)，包含平均值、最大值、最小值、变异性等")
    breathing_rate: dict[str, Any] | None = Field(None, description="呼吸率(次/分)，包含平均值")
    body_temperature: float | None = Field(None, description="体温(°C)")
    blood_oxygen: float | None = Field(None, description="血氧饱和度(%)")
    blood_glucose: dict[str, Any] | None = Field(None, description="血糖，包含空腹和餐后值")


class TCMConstitution(BaseModel):
    """中医体质数据"""
    primary_type: str = Field(..., description="主要体质类型")
    type_scores: dict[str, float] = Field(
        ...,
        description="各体质得分，包括平和质、气虚质、阳虚质、阴虚质、痰湿质、湿热质、血瘀质、气郁质、特禀质"
    )
    imbalance_symptoms: list[str] = Field(default_factory=list, description="体质偏颇表现")
    seasonal_changes: list[dict[str, Any]] = Field(default_factory=list, description="季节性变化记录")

    class Config:
        schema_extra = {
            "example": {
                "primary_type": "阳虚质",
                "type_scores": {
                    "平和质": 0.2,
                    "气虚质": 0.3,
                    "阳虚质": 0.8,
                    "阴虚质": 0.1,
                    "痰湿质": 0.4,
                    "湿热质": 0.1,
                    "血瘀质": 0.3,
                    "气郁质": 0.2,
                    "特禀质": 0.1
                },
                "imbalance_symptoms": ["畏寒", "手脚冰凉", "喜热饮", "精神不振"],
                "seasonal_changes": [
                    {"season": "冬季", "severity": 0.9, "symptoms": ["畏寒加重", "疲乏明显"]}
                ]
            }
        }


class SleepMetrics(BaseModel):
    """睡眠指标"""
    average_duration: float | None = Field(None, description="平均睡眠时长(小时)")
    sleep_score: float | None = Field(None, description="睡眠质量评分(0-100)")
    sleep_stages: dict[str, float] | None = Field(None, description="各睡眠阶段占比（深睡眠、浅睡眠、REM、觉醒）")
    sleep_efficiency: float | None = Field(None, description="睡眠效率(%)")
    sleep_regularity: float | None = Field(None, description="睡眠规律性评分(0-100)")
    sleep_issues: list[str] | None = Field(None, description="睡眠问题列表")


class ActivityMetrics(BaseModel):
    """活动指标"""
    daily_steps: float | None = Field(None, description="日均步数")
    active_minutes: dict[str, float] | None = Field(None, description="活动时间分布(低、中、高强度)")
    exercise_frequency: float | None = Field(None, description="每周运动频率")
    exercise_types: list[str] | None = Field(None, description="常见运动类型")
    vo2_max: float | None = Field(None, description="最大摄氧量")
    activity_score: float | None = Field(None, description="活动健康评分(0-100)")


class NutritionStatus(BaseModel):
    """营养状态"""
    dietary_pattern: str | None = Field(None, description="饮食模式描述")
    meal_regularity: float | None = Field(None, description="规律进餐评分(0-100)")
    nutrition_balance: dict[str, float] | None = Field(None, description="营养平衡评分(蛋白质、脂肪、碳水、维生素等)")
    hydration: float | None = Field(None, description="每日饮水量(ml)")
    five_elements_balance: dict[str, float] | None = Field(None, description="五行食物平衡情况")
    five_tastes_distribution: dict[str, float] | None = Field(None, description="五味食物摄入分布")
    nutrition_score: float | None = Field(None, description="营养健康评分(0-100)")


class MentalStatus(BaseModel):
    """心理状态"""
    stress_level: float | None = Field(None, description="压力水平(0-100)")
    mood_stability: float | None = Field(None, description="情绪稳定性(0-100)")
    anxiety_level: float | None = Field(None, description="焦虑水平(0-100)")
    happiness_index: float | None = Field(None, description="幸福感指数(0-100)")
    tcm_emotion_balance: dict[str, float] | None = Field(None, description="中医五志(喜、怒、忧、思、恐)平衡情况")


class EnvironmentalFactors(BaseModel):
    """环境因素"""
    living_environment: dict[str, Any] | None = Field(None, description="居住环境评估")
    work_environment: dict[str, Any] | None = Field(None, description="工作环境评估")
    air_quality: dict[str, Any] | None = Field(None, description="空气质量评估")
    climate_suitability: float | None = Field(None, description="气候适宜度评分(0-100)")
    seasonal_impact: dict[str, float] | None = Field(None, description="季节对健康的影响程度")


class HealthRisks(BaseModel):
    """健康风险"""
    chronic_disease_risks: dict[str, float] = Field(default_factory=dict, description="慢性疾病风险评估")
    tcm_disease_tendency: list[str] = Field(default_factory=list, description="中医疾病倾向")
    lifestyle_related_risks: dict[str, float] = Field(default_factory=dict, description="生活方式相关风险")
    genetic_risks: dict[str, float] | None = Field(None, description="遗传相关风险(如果有)")


class HealthStrengths(BaseModel):
    """健康优势"""
    physical_strengths: list[str] = Field(default_factory=list, description="身体优势")
    mental_strengths: list[str] = Field(default_factory=list, description="心理优势")
    lifestyle_strengths: list[str] = Field(default_factory=list, description="生活方式优势")
    tcm_balance_points: list[str] = Field(default_factory=list, description="中医平衡点")


class HealthTrends(BaseModel):
    """健康趋势"""
    weight_trend: str | None = Field(None, description="体重趋势")
    vitals_trend: dict[str, str] | None = Field(None, description="生命体征趋势")
    sleep_trend: str | None = Field(None, description="睡眠趋势")
    constitution_trend: str | None = Field(None, description="体质趋势")
    lifestyle_trend: str | None = Field(None, description="生活方式趋势")
    overall_health_trend: str | None = Field(None, description="整体健康趋势")


class HealthProfile(BaseModel):
    """健康画像主模型"""
    user_id: str = Field(..., description="用户ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    profile_version: str = Field("1.0", description="健康画像版本")

    # 基本信息
    age: int | None = Field(None, description="年龄")
    gender: str | None = Field(None, description="性别")

    # 详细指标
    physical_metrics: PhysicalMetrics = Field(default_factory=PhysicalMetrics, description="身体基础指标")
    vital_signs: VitalSigns = Field(default_factory=VitalSigns, description="生命体征")
    tcm_constitution: TCMConstitution | None = Field(None, description="中医体质数据")
    sleep_metrics: SleepMetrics = Field(default_factory=SleepMetrics, description="睡眠指标")
    activity_metrics: ActivityMetrics = Field(default_factory=ActivityMetrics, description="活动指标")
    nutrition_status: NutritionStatus = Field(default_factory=NutritionStatus, description="营养状态")
    mental_status: MentalStatus = Field(default_factory=MentalStatus, description="心理状态")
    environmental_factors: EnvironmentalFactors = Field(default_factory=EnvironmentalFactors, description="环境因素")

    # 健康评估
    health_risks: HealthRisks = Field(default_factory=HealthRisks, description="健康风险")
    health_strengths: HealthStrengths = Field(default_factory=HealthStrengths, description="健康优势")
    health_trends: HealthTrends = Field(default_factory=HealthTrends, description="健康趋势")

    # 综合评分
    overall_health_score: float = Field(0.0, description="综合健康评分(0-100)")

    # 自定义标签
    tags: list[str] = Field(default_factory=list, description="健康标签")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "age": 35,
                "gender": "男",
                "overall_health_score": 78.5,
                "tags": ["阳虚", "睡眠不足", "肝郁", "适合温补"]
            }
        }
