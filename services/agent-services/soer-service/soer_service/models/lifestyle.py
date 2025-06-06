"""
lifestyle - 索克生活项目模块
"""

from datetime import datetime, time
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

"""
生活方式相关数据模型

定义运动计划、睡眠分析、压力评估等数据结构
"""




class ExerciseType(str, Enum):
    """运动类型枚举"""

    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    BALANCE = "balance"
    SPORTS = "sports"
    YOGA = "yoga"
    WALKING = "walking"
    RUNNING = "running"
    CYCLING = "cycling"
    SWIMMING = "swimming"


class ExerciseIntensity(str, Enum):
    """运动强度枚举"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class Exercise(BaseModel):
    """单次运动模型"""

    exercise_id: str = Field(..., description="运动ID")
    name: str = Field(..., description="运动名称")
    type: ExerciseType = Field(..., description="运动类型")
    intensity: ExerciseIntensity = Field(..., description="运动强度")
    duration: int = Field(..., description="持续时间(分钟)")
    calories_burned: float | None = Field(None, description="消耗热量")
    description: str | None = Field(None, description="运动描述")
    equipment_needed: list[str] = Field(default_factory=list, description="所需器材")
    muscle_groups: list[str] = Field(default_factory=list, description="锻炼肌群")

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'exercise'
        ordering = ['-created_at']


class ExercisePlan(BaseModel):
    """运动计划模型"""

    plan_id: str = Field(..., description="计划ID")
    user_id: str = Field(..., description="用户ID")
    plan_name: str = Field(..., description="计划名称")
    description: str = Field(..., description="计划描述")

    # 计划设定
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    frequency_per_week: int = Field(..., description="每周频次")

    # 运动安排
    exercises: list[Exercise] = Field(..., description="运动列表")
    weekly_schedule: dict[str, list[str]] = Field(
        default_factory=dict, description="每周安排"
    )

    # 目标设定
    fitness_goals: list[str] = Field(default_factory=list, description="健身目标")
    target_calories_per_week: float | None = Field(None, description="每周目标消耗热量")

    # 进度跟踪
    completion_rate: float = Field(default=0, description="完成率")
    total_workouts: int = Field(default=0, description="总锻炼次数")
    completed_workouts: int = Field(default=0, description="已完成锻炼次数")

    # 中医运动理论
    tcm_exercise_principles: dict[str, Any] = Field(
        default_factory=dict, description="中医运动原则"
    )

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'workoutsession'
        ordering = ['-created_at']


class WorkoutSession(BaseModel):
    """锻炼记录模型"""

    session_id: str = Field(..., description="锻炼记录ID")
    user_id: str = Field(..., description="用户ID")
    plan_id: str | None = Field(None, description="所属计划ID")

    # 锻炼信息
    date: datetime = Field(..., description="锻炼日期")
    exercises_performed: list[Exercise] = Field(..., description="完成的运动")
    total_duration: int = Field(..., description="总时长(分钟)")
    total_calories_burned: float = Field(..., description="总消耗热量")

    # 主观感受
    perceived_exertion: int | None = Field(None, description="主观疲劳度(1-10)")
    mood_before: int | None = Field(None, description="运动前情绪(1-10)")
    mood_after: int | None = Field(None, description="运动后情绪(1-10)")
    energy_level: int | None = Field(None, description="精力水平(1-10)")

    # 备注
    notes: str | None = Field(None, description="备注")
    achievements: list[str] = Field(default_factory=list, description="成就")

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'sleepdata'
        ordering = ['-created_at']


class SleepStage(str, Enum):
    """睡眠阶段枚举"""

    AWAKE = "awake"
    LIGHT = "light"
    DEEP = "deep"
    REM = "rem"


class SleepData(BaseModel):
    """睡眠数据模型"""

    user_id: str = Field(..., description="用户ID")
    sleep_date: datetime = Field(..., description="睡眠日期")

    # 睡眠时间
    bedtime: time = Field(..., description="就寝时间")
    sleep_onset_time: time | None = Field(None, description="入睡时间")
    wake_up_time: time = Field(..., description="起床时间")

    # 睡眠质量
    total_sleep_time: float = Field(..., description="总睡眠时间(小时)")
    sleep_efficiency: float = Field(..., description="睡眠效率(%)")
    sleep_latency: int | None = Field(None, description="入睡潜伏期(分钟)")

    # 睡眠阶段
    light_sleep_duration: float | None = Field(None, description="浅睡眠时长(小时)")
    deep_sleep_duration: float | None = Field(None, description="深睡眠时长(小时)")
    rem_sleep_duration: float | None = Field(None, description="REM睡眠时长(小时)")

    # 睡眠中断
    wake_up_count: int = Field(default=0, description="夜间醒来次数")
    restless_periods: int = Field(default=0, description="不安稳期数")

    # 主观评价
    sleep_quality_rating: int | None = Field(None, description="睡眠质量评分(1-10)")
    morning_mood: int | None = Field(None, description="晨起情绪(1-10)")

    # 环境因素
    room_temperature: float | None = Field(None, description="室温(°C)")
    noise_level: str | None = Field(None, description="噪音水平")
    light_exposure: str | None = Field(None, description="光照情况")

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'sleepanalysis'
        ordering = ['-created_at']


class SleepAnalysis(BaseModel):
    """睡眠分析模型"""

    user_id: str = Field(..., description="用户ID")
    analysis_period: int = Field(..., description="分析周期(天)")
    analysis_date: datetime = Field(
        default_factory=datetime.now, description="分析时间"
    )

    # 睡眠统计
    average_sleep_duration: float = Field(..., description="平均睡眠时长")
    average_sleep_efficiency: float = Field(..., description="平均睡眠效率")
    average_bedtime: time = Field(..., description="平均就寝时间")
    average_wake_time: time = Field(..., description="平均起床时间")

    # 睡眠模式
    sleep_consistency_score: float = Field(..., description="睡眠一致性评分")
    sleep_debt: float = Field(..., description="睡眠债务(小时)")
    optimal_bedtime: time = Field(..., description="建议就寝时间")
    optimal_wake_time: time = Field(..., description="建议起床时间")

    # 睡眠质量趋势
    quality_trend: str = Field(..., description="质量趋势")
    improvement_areas: list[str] = Field(default_factory=list, description="改善领域")
    sleep_recommendations: list[str] = Field(
        default_factory=list, description="睡眠建议"
    )

    # 中医睡眠理论
    tcm_sleep_analysis: dict[str, Any] = Field(
        default_factory=dict, description="中医睡眠分析"
    )

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'stressassessment'
        ordering = ['-created_at']


class StressLevel(str, Enum):
    """压力水平枚举"""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class StressSource(str, Enum):
    """压力来源枚举"""

    WORK = "work"
    FAMILY = "family"
    HEALTH = "health"
    FINANCIAL = "financial"
    RELATIONSHIP = "relationship"
    ACADEMIC = "academic"
    OTHER = "other"


class StressAssessment(BaseModel):
    """压力评估模型"""

    assessment_id: str = Field(..., description="评估ID")
    user_id: str = Field(..., description="用户ID")
    assessment_date: datetime = Field(
        default_factory=datetime.now, description="评估时间"
    )

    # 压力水平
    overall_stress_level: StressLevel = Field(..., description="整体压力水平")
    stress_score: int = Field(..., description="压力评分(1-100)")

    # 压力来源
    stress_sources: list[StressSource] = Field(..., description="压力来源")
    primary_stressor: StressSource = Field(..., description="主要压力源")

    # 生理指标
    heart_rate_variability: float | None = Field(None, description="心率变异性")
    cortisol_level: float | None = Field(None, description="皮质醇水平")
    blood_pressure: dict[str, float] | None = Field(None, description="血压")

    # 心理症状
    anxiety_level: int = Field(..., description="焦虑水平(1-10)")
    irritability_level: int = Field(..., description="易怒程度(1-10)")
    concentration_difficulty: int = Field(..., description="注意力困难(1-10)")

    # 行为表现
    sleep_quality_impact: int = Field(..., description="对睡眠质量影响(1-10)")
    appetite_change: str = Field(..., description="食欲变化")
    social_withdrawal: int = Field(..., description="社交回避程度(1-10)")

    # 应对策略
    current_coping_strategies: list[str] = Field(
        default_factory=list, description="当前应对策略"
    )
    effective_strategies: list[str] = Field(
        default_factory=list, description="有效策略"
    )

    # 建议
    stress_management_recommendations: list[str] = Field(
        default_factory=list, description="压力管理建议"
    )

    # 中医情志调节
    tcm_emotional_regulation: dict[str, Any] = Field(
        default_factory=dict, description="中医情志调节"
    )

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'lifestylegoal'
        ordering = ['-created_at']


class LifestyleGoal(BaseModel):
    """生活方式目标模型"""

    goal_id: str = Field(..., description="目标ID")
    user_id: str = Field(..., description="用户ID")
    category: str = Field(..., description="目标类别")
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
    weekly_targets: list[float] = Field(default_factory=list, description="每周目标")

    # 状态
    status: str = Field(default="active", description="目标状态")
    motivation_level: int = Field(default=5, description="动机水平(1-10)")


class HabitTracker(BaseModel):
    """习惯追踪模型"""

    habit_id: str = Field(..., description="习惯ID")
    user_id: str = Field(..., description="用户ID")
    habit_name: str = Field(..., description="习惯名称")
    description: str = Field(..., description="习惯描述")
    category: str = Field(..., description="习惯类别")

    # 习惯设定
    target_frequency: str = Field(..., description="目标频率")
    reminder_time: time | None = Field(None, description="提醒时间")

    # 追踪记录
    streak_count: int = Field(default=0, description="连续天数")
    completion_rate: float = Field(default=0, description="完成率")
    total_completions: int = Field(default=0, description="总完成次数")

    # 状态
    is_active: bool = Field(default=True, description="是否活跃")
    created_date: datetime = Field(default_factory=datetime.now, description="创建日期")
    last_completed: datetime | None = Field(None, description="最后完成时间")
