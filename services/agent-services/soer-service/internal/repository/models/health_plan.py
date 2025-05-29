"""
健康计划数据模型
"""
from datetime import datetime, time
from typing import Any

from pydantic import BaseModel, Field


class DietRecommendation(BaseModel):
    """饮食建议"""
    food_category: str = Field(..., description="食物类别，如'谷物'、'肉类'、'蔬菜'等")
    recommended_foods: list[str] = Field(..., description="推荐食物列表")
    avoid_foods: list[str] = Field(..., description="避免食物列表")
    meal_distribution: dict[str, float] = Field(..., description="膳食分配比例，如早餐、午餐、晚餐的比例")
    portion_guidance: str = Field(..., description="食物份量指导")
    special_guidance: str | None = Field(None, description="特殊饮食指导")
    tcm_principles: list[str] = Field(default_factory=list, description="中医饮食原则")
    recipes: list[dict[str, Any]] = Field(default_factory=list, description="推荐食谱")


class ExerciseRecommendation(BaseModel):
    """运动建议"""
    exercise_types: list[str] = Field(..., description="推荐运动类型")
    weekly_frequency: int = Field(..., description="每周建议频率")
    duration: int = Field(..., description="每次建议时长(分钟)")
    intensity: str = Field(..., description="建议强度，如'低'、'中'、'高'")
    steps_target: int | None = Field(None, description="每日步数目标")
    precautions: list[str] = Field(default_factory=list, description="运动注意事项")
    tcm_exercises: list[str] = Field(default_factory=list, description="中医养生功法推荐")
    custom_routine: dict[str, Any] | None = Field(None, description="个性化运动方案")


class SleepRecommendation(BaseModel):
    """睡眠建议"""
    recommended_duration: float = Field(..., description="建议睡眠时长(小时)")
    bedtime: time = Field(..., description="建议就寝时间")
    wake_time: time = Field(..., description="建议起床时间")
    pre_sleep_routine: list[str] = Field(default_factory=list, description="睡前建议活动")
    environment_tips: list[str] = Field(default_factory=list, description="睡眠环境建议")
    avoid_activities: list[str] = Field(default_factory=list, description="睡前应避免的活动")
    tcm_sleep_aids: list[str] = Field(default_factory=list, description="中医助眠方法")


class StressManagement(BaseModel):
    """压力管理"""
    relaxation_techniques: list[str] = Field(default_factory=list, description="放松技巧")
    meditation_practice: dict[str, Any] | None = Field(None, description="冥想练习")
    emotional_regulation: list[str] = Field(default_factory=list, description="情绪调节方法")
    leisure_activities: list[str] = Field(default_factory=list, description="推荐休闲活动")
    tcm_emotion_regulation: list[str] = Field(default_factory=list, description="中医情志调节法")


class SupplementRecommendation(BaseModel):
    """营养补充建议"""
    supplements: list[dict[str, Any]] = Field(default_factory=list, description="补充剂列表及用量")
    herbs: list[dict[str, Any]] = Field(default_factory=list, description="中草药建议")
    special_notes: str | None = Field(None, description="特殊注意事项")


class EnvironmentalSuggestion(BaseModel):
    """环境建议"""
    living_environment: list[str] = Field(default_factory=list, description="生活环境建议")
    work_environment: list[str] = Field(default_factory=list, description="工作环境建议")
    seasonal_adjustments: dict[str, list[str]] = Field(default_factory=dict, description="季节性调整建议")
    travel_suggestions: list[str] | None = Field(None, description="旅行建议")


class DailySchedule(BaseModel):
    """日常作息建议"""
    weekday_schedule: dict[str, str] = Field(..., description="工作日时间表")
    weekend_schedule: dict[str, str] = Field(..., description="周末时间表")
    key_timings: dict[str, time] = Field(..., description="关键时间点")
    tcm_timing_principles: list[str] = Field(default_factory=list, description="中医时辰养生原则")


class MonitoringPlan(BaseModel):
    """监测计划"""
    metrics_to_track: list[str] = Field(..., description="需要追踪的指标")
    tracking_frequency: dict[str, str] = Field(..., description="追踪频率")
    target_values: dict[str, Any] = Field(..., description="目标值")
    warning_thresholds: dict[str, Any] = Field(..., description="预警阈值")


class ProgressMilestone(BaseModel):
    """进度里程碑"""
    milestone_name: str = Field(..., description="里程碑名称")
    target_date: datetime = Field(..., description="目标日期")
    description: str = Field(..., description="描述")
    metrics: list[dict[str, Any]] = Field(..., description="衡量指标")
    rewards: list[str] | None = Field(None, description="达成奖励")


class HealthPlan(BaseModel):
    """健康计划主模型"""
    plan_id: str = Field(..., description="计划ID")
    user_id: str = Field(..., description="用户ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    plan_version: str = Field("1.0", description="计划版本")
    plan_name: str = Field(..., description="计划名称")

    # 计划基本信息
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime | None = Field(None, description="结束日期")
    health_goals: list[str] = Field(..., description="健康目标")
    constitution_type: str = Field(..., description="体质类型")
    current_season: str = Field(..., description="当前季节")

    # 具体建议
    diet_recommendations: DietRecommendation = Field(..., description="饮食建议")
    exercise_recommendations: ExerciseRecommendation = Field(..., description="运动建议")
    sleep_recommendations: SleepRecommendation = Field(..., description="睡眠建议")
    stress_management: StressManagement = Field(..., description="压力管理")
    supplement_recommendations: SupplementRecommendation | None = Field(None, description="营养补充建议")
    environmental_suggestions: EnvironmentalSuggestion = Field(..., description="环境建议")

    # 实施计划
    daily_schedule: DailySchedule = Field(..., description="日常作息建议")
    monitoring_plan: MonitoringPlan = Field(..., description="监测计划")
    milestones: list[ProgressMilestone] = Field(..., description="进度里程碑")

    # 评估指标
    expected_outcomes: dict[str, Any] = Field(..., description="预期结果")
    adjustment_triggers: list[str] = Field(..., description="计划调整触发条件")

    # 计划标签
    tags: list[str] = Field(default_factory=list, description="计划标签")

    # 个性化备注
    notes: str | None = Field(None, description="备注")

    class Config:
        schema_extra = {
            "example": {
                "plan_id": "plan_12345",
                "user_id": "user_12345",
                "plan_name": "阳虚体质调理三月计划",
                "start_date": "2024-07-01T00:00:00Z",
                "end_date": "2024-09-30T23:59:59Z",
                "health_goals": ["改善睡眠", "增强体质抵抗力", "缓解腰膝酸痛"],
                "constitution_type": "阳虚质",
                "current_season": "夏季",
                "tags": ["温补阳气", "强健脾胃", "固肾壮腰"]
            }
        }
