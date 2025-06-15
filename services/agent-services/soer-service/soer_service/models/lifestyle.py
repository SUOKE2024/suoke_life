"""
生活方式相关模型
"""

from datetime import datetime, time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExercisePlan(BaseModel):
    """运动计划模型"""
    user_id: str = Field(..., description="用户ID")
    plan_name: str = Field(..., description="计划名称")
    exercise_type: str = Field(..., description="运动类型")
    duration_minutes: int = Field(..., description="持续时间(分钟)")
    intensity: str = Field(..., description="强度等级")
    frequency_per_week: int = Field(..., description="每周频率")
    target_calories: Optional[float] = Field(default=None, description="目标消耗卡路里")
    equipment_needed: List[str] = Field(default_factory=list, description="所需设备")
    instructions: List[str] = Field(default_factory=list, description="指导说明")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class SleepAnalysis(BaseModel):
    """睡眠分析模型"""
    user_id: str = Field(..., description="用户ID")
    sleep_date: datetime = Field(..., description="睡眠日期")
    bedtime: time = Field(..., description="就寝时间")
    wake_time: time = Field(..., description="起床时间")
    total_sleep_hours: float = Field(..., description="总睡眠时长")
    sleep_quality_score: float = Field(ge=0.0, le=10.0, description="睡眠质量评分")
    deep_sleep_minutes: Optional[int] = Field(default=None, description="深度睡眠时长(分钟)")
    rem_sleep_minutes: Optional[int] = Field(default=None, description="REM睡眠时长(分钟)")
    wake_count: Optional[int] = Field(default=None, description="觉醒次数")
    recommendations: List[str] = Field(default_factory=list, description="改善建议")


class StressAssessment(BaseModel):
    """压力评估模型"""
    user_id: str = Field(..., description="用户ID")
    assessment_date: datetime = Field(default_factory=datetime.now, description="评估日期")
    stress_level: int = Field(ge=1, le=10, description="压力等级(1-10)")
    stress_sources: List[str] = Field(default_factory=list, description="压力来源")
    physical_symptoms: List[str] = Field(default_factory=list, description="身体症状")
    emotional_symptoms: List[str] = Field(default_factory=list, description="情绪症状")
    coping_strategies: List[str] = Field(default_factory=list, description="应对策略")
    recommendations: List[str] = Field(default_factory=list, description="缓解建议")
    follow_up_date: Optional[datetime] = Field(default=None, description="后续评估日期")
