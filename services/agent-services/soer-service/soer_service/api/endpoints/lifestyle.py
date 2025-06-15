"""
lifestyle - 索克生活项目模块
"""

from ...models.lifestyle import ExercisePlan, SleepAnalysis, StressAssessment
from ...services.lifestyle_service import LifestyleService
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any

"""
生活方式管理 API 端点

提供运动计划、睡眠管理、压力管理等功能
"""




router = APIRouter()


class ExercisePlanRequest(BaseModel):
    """运动计划请求模型"""

    user_id: str
    fitness_level: str = "beginner"  # beginner, intermediate, advanced
    goals: list[str] = []  # weight_loss, muscle_gain, endurance, etc.
    available_time: int = 30  # minutes per day
    preferred_activities: list[str] = []


class SleepDataRequest(BaseModel):
    """睡眠数据请求模型"""

    user_id: str
    sleep_duration: float  # hours
    sleep_quality: int  # 1 - 10 scale
    bedtime: str
    wake_time: str
    date: str


class StressAssessmentRequest(BaseModel):
    """压力评估请求模型"""

    user_id: str
    stress_level: int  # 1 - 10 scale
    stress_factors: list[str] = []
    symptoms: list[str] = []


@router.post(" / exercise / plan", response_model = ExercisePlan)
async def create_exercise_plan(
    request: ExercisePlanRequest, lifestyle_service: LifestyleService = Depends()
) -> ExercisePlan:
    """
    创建个性化运动计划

    Args:
        request: 运动计划请求
        lifestyle_service: 生活方式服务实例

    Returns:
        运动计划
    """
    try:
        plan = await lifestyle_service.create_exercise_plan(
            user_id = request.user_id,
            fitness_level = request.fitness_level,
            goals = request.goals,
            available_time = request.available_time,
            preferred_activities = request.preferred_activities,
        )

        return plan

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"运动计划创建失败: {str(e)}")


@router.post(" / sleep / data")
async def submit_sleep_data(
    request: SleepDataRequest, lifestyle_service: LifestyleService = Depends()
) -> dict[str, str]:
    """
    提交睡眠数据

    Args:
        request: 睡眠数据请求
        lifestyle_service: 生活方式服务实例

    Returns:
        提交结果
    """
    try:
        await lifestyle_service.submit_sleep_data(
            user_id = request.user_id,
            sleep_duration = request.sleep_duration,
            sleep_quality = request.sleep_quality,
            bedtime = request.bedtime,
            wake_time = request.wake_time,
            date = request.date,
        )

        return {"status": "success", "message": "睡眠数据提交成功"}

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"睡眠数据提交失败: {str(e)}")


@router.get(" / sleep / analysis / {user_id}", response_model = SleepAnalysis)
async def get_sleep_analysis(
    user_id: str, days: int = 7, lifestyle_service: LifestyleService = Depends()
) -> SleepAnalysis:
    """
    获取睡眠分析

    Args:
        user_id: 用户ID
        days: 分析天数
        lifestyle_service: 生活方式服务实例

    Returns:
        睡眠分析结果
    """
    try:
        analysis = await lifestyle_service.analyze_sleep_patterns(
            user_id = user_id, days = days
        )

        return analysis

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"睡眠分析失败: {str(e)}")


@router.post(" / stress / assessment", response_model = StressAssessment)
async def assess_stress(
    request: StressAssessmentRequest, lifestyle_service: LifestyleService = Depends()
) -> StressAssessment:
    """
    进行压力评估

    Args:
        request: 压力评估请求
        lifestyle_service: 生活方式服务实例

    Returns:
        压力评估结果
    """
    try:
        assessment = await lifestyle_service.assess_stress_level(
            user_id = request.user_id,
            stress_level = request.stress_level,
            stress_factors = request.stress_factors,
            symptoms = request.symptoms,
        )

        return assessment

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"压力评估失败: {str(e)}")


@router.get(" / recommendations / {user_id}")
async def get_lifestyle_recommendations(
    user_id: str,
    category: str = "all",  # all, exercise, sleep, stress
    lifestyle_service: LifestyleService = Depends(),
) -> dict[str, Any]:
    """
    获取生活方式建议

    Args:
        user_id: 用户ID
        category: 建议类别
        lifestyle_service: 生活方式服务实例

    Returns:
        生活方式建议
    """
    try:
        recommendations = await lifestyle_service.get_lifestyle_recommendations(
            user_id = user_id, category = category
        )

        return recommendations

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"获取生活方式建议失败: {str(e)}")


@router.get(" / progress / {user_id}")
async def get_lifestyle_progress(
    user_id: str,
    metric: str,
    period: str = "week",  # week, month, year
    lifestyle_service: LifestyleService = Depends(),
) -> dict[str, Any]:
    """
    获取生活方式进展

    Args:
        user_id: 用户ID
        metric: 进展指标
        period: 时间周期
        lifestyle_service: 生活方式服务实例

    Returns:
        进展数据
    """
    try:
        progress = await lifestyle_service.get_lifestyle_progress(
            user_id = user_id, metric = metric, period = period
        )

        return progress

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"获取生活方式进展失败: {str(e)}")
