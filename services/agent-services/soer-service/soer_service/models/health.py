"""
健康相关数据模型

定义健康数据、分析结果、建议等数据结构
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class HealthDataType(str, Enum):
    """健康数据类型枚举"""

    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_SUGAR = "blood_sugar"
    WEIGHT = "weight"
    BMI = "bmi"
    BODY_FAT = "body_fat"
    SLEEP_DURATION = "sleep_duration"
    STEPS = "steps"
    EXERCISE_DURATION = "exercise_duration"
    STRESS_LEVEL = "stress_level"
    MOOD = "mood"
    TEMPERATURE = "temperature"


class HealthData(BaseModel):
    """健康数据模型"""

    user_id: str = Field(..., description="用户ID")
    data_type: HealthDataType = Field(..., description="数据类型")
    value: float = Field(..., description="数值")
    unit: str = Field(..., description="单位")
    timestamp: datetime = Field(..., description="记录时间")
    source: str = Field(default="manual", description="数据来源")
    device_id: str | None = Field(None, description="设备ID")
    notes: str | None = Field(None, description="备注")


class VitalSigns(BaseModel):
    """生命体征模型"""

    heart_rate: float | None = Field(None, description="心率(bpm)")
    systolic_bp: float | None = Field(None, description="收缩压(mmHg)")
    diastolic_bp: float | None = Field(None, description="舒张压(mmHg)")
    blood_sugar: float | None = Field(None, description="血糖(mg/dL)")
    body_temperature: float | None = Field(None, description="体温(°C)")
    oxygen_saturation: float | None = Field(None, description="血氧饱和度(%)")


class PhysicalMetrics(BaseModel):
    """身体指标模型"""

    weight: float | None = Field(None, description="体重(kg)")
    height: float | None = Field(None, description="身高(cm)")
    bmi: float | None = Field(None, description="BMI")
    body_fat_percentage: float | None = Field(None, description="体脂率(%)")
    muscle_mass: float | None = Field(None, description="肌肉量(kg)")
    bone_density: float | None = Field(None, description="骨密度")


class ActivityMetrics(BaseModel):
    """活动指标模型"""

    daily_steps: int | None = Field(None, description="每日步数")
    exercise_duration: int | None = Field(None, description="运动时长(分钟)")
    calories_burned: float | None = Field(None, description="消耗热量(kcal)")
    active_minutes: int | None = Field(None, description="活跃时长(分钟)")
    sedentary_time: int | None = Field(None, description="久坐时间(分钟)")


class SleepMetrics(BaseModel):
    """睡眠指标模型"""

    sleep_duration: float | None = Field(None, description="睡眠时长(小时)")
    deep_sleep_duration: float | None = Field(None, description="深度睡眠时长(小时)")
    rem_sleep_duration: float | None = Field(None, description="REM睡眠时长(小时)")
    sleep_efficiency: float | None = Field(None, description="睡眠效率(%)")
    wake_up_count: int | None = Field(None, description="夜间醒来次数")
    sleep_quality_score: float | None = Field(None, description="睡眠质量评分")


class MentalHealthMetrics(BaseModel):
    """心理健康指标模型"""

    stress_level: int | None = Field(None, description="压力水平(1-10)")
    mood_score: int | None = Field(None, description="情绪评分(1-10)")
    anxiety_level: int | None = Field(None, description="焦虑水平(1-10)")
    energy_level: int | None = Field(None, description="精力水平(1-10)")
    focus_level: int | None = Field(None, description="专注度(1-10)")


class HealthAnalysis(BaseModel):
    """健康分析结果模型"""

    user_id: str = Field(..., description="用户ID")
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="分析时间"
    )
    analysis_type: str = Field(..., description="分析类型")
    time_range: int = Field(..., description="分析时间范围(天)")

    # 各项指标
    vital_signs: VitalSigns = Field(default_factory=VitalSigns, description="生命体征")
    physical_metrics: PhysicalMetrics = Field(
        default_factory=PhysicalMetrics, description="身体指标"
    )
    activity_metrics: ActivityMetrics = Field(
        default_factory=ActivityMetrics, description="活动指标"
    )
    sleep_metrics: SleepMetrics = Field(
        default_factory=SleepMetrics, description="睡眠指标"
    )
    mental_health_metrics: MentalHealthMetrics = Field(
        default_factory=MentalHealthMetrics, description="心理健康指标"
    )

    # 分析结果
    overall_health_score: float = Field(..., description="整体健康评分(0-100)")
    health_trends: dict[str, str] = Field(default_factory=dict, description="健康趋势")
    risk_factors: list[str] = Field(default_factory=list, description="风险因素")
    improvement_areas: list[str] = Field(default_factory=list, description="改善领域")

    # 中医体质分析
    tcm_constitution: dict[str, Any] = Field(
        default_factory=dict, description="中医体质分析"
    )


class HealthRecommendation(BaseModel):
    """健康建议模型"""

    recommendation_id: str = Field(..., description="建议ID")
    user_id: str = Field(..., description="用户ID")
    category: str = Field(..., description="建议类别")
    priority: str = Field(..., description="优先级")
    title: str = Field(..., description="建议标题")
    description: str = Field(..., description="建议描述")
    action_items: list[str] = Field(default_factory=list, description="行动项目")
    expected_benefits: list[str] = Field(default_factory=list, description="预期收益")

    # 时间相关
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    valid_until: datetime | None = Field(None, description="有效期至")

    # 执行状态
    status: str = Field(default="pending", description="执行状态")
    progress: float = Field(default=0, description="执行进度")

    # 中医建议
    tcm_guidance: dict[str, Any] | None = Field(None, description="中医指导")


class HealthGoal(BaseModel):
    """健康目标模型"""

    goal_id: str = Field(..., description="目标ID")
    user_id: str = Field(..., description="用户ID")
    goal_type: str = Field(..., description="目标类型")
    title: str = Field(..., description="目标标题")
    description: str = Field(..., description="目标描述")

    # 目标设定
    target_value: float = Field(..., description="目标值")
    current_value: float = Field(..., description="当前值")
    unit: str = Field(..., description="单位")

    # 时间设定
    start_date: datetime = Field(..., description="开始日期")
    target_date: datetime = Field(..., description="目标日期")

    # 进度跟踪
    progress_percentage: float = Field(default=0, description="进度百分比")
    milestones: list[dict[str, Any]] = Field(default_factory=list, description="里程碑")

    # 状态
    status: str = Field(default="active", description="目标状态")
    achievement_date: datetime | None = Field(None, description="达成日期")


class HealthAlert(BaseModel):
    """健康警报模型"""

    alert_id: str = Field(..., description="警报ID")
    user_id: str = Field(..., description="用户ID")
    alert_type: str = Field(..., description="警报类型")
    severity: str = Field(..., description="严重程度")
    title: str = Field(..., description="警报标题")
    message: str = Field(..., description="警报消息")

    # 触发条件
    trigger_condition: dict[str, Any] = Field(..., description="触发条件")
    trigger_value: float = Field(..., description="触发值")

    # 时间信息
    triggered_at: datetime = Field(default_factory=datetime.now, description="触发时间")
    acknowledged_at: datetime | None = Field(None, description="确认时间")
    resolved_at: datetime | None = Field(None, description="解决时间")

    # 状态
    status: str = Field(default="active", description="警报状态")
    actions_taken: list[str] = Field(default_factory=list, description="已采取行动")
