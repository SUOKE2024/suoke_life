"""
health_plan_routes - 索克生活项目模块
"""

from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from internal.lifecycle.plan_generator.plan_generator import PlanGenerator
from pydantic import BaseModel, Field
from typing import Any
import logging



# 导入服务层组件

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/health-plans",
    tags=["健康计划"],
    responses={404: {"description": "未找到"}},
)

# 请求和响应模型
class HealthPlanRequest(BaseModel):
    """健康计划请求模型"""
    user_id: str
    constitution_type: str
    health_goals: list[str]
    health_data: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] | None = None
    current_season: str | None = None

class HealthPlanResponse(BaseModel):
    """健康计划响应模型"""
    plan_id: str
    user_id: str
    constitution_type: str
    creation_date: str
    health_goals: list[str]
    diet_recommendations: list[str]
    exercise_recommendations: list[str]
    lifestyle_recommendations: list[str]
    supplement_recommendations: list[str]
    schedule: dict[str, str]

class HealthPlanProgressRequest(BaseModel):
    """健康计划进度更新请求"""
    user_id: str
    plan_id: str
    completed_items: list[str]
    progress_notes: str | None = None
    timestamp: str | None = None

class HealthPlanProgressResponse(BaseModel):
    """健康计划进度响应"""
    user_id: str
    plan_id: str
    progress_percentage: float
    next_steps: list[str]
    encouragement_message: str

# 健康计划生成器实例
plan_generator = PlanGenerator()

@router.post("/", response_model=HealthPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_health_plan(plan_request: HealthPlanRequest, background_tasks: BackgroundTasks):
    """
    创建新的健康计划
    """
    try:
        # 生成健康计划
        plan = plan_generator.generate_health_plan(
            plan_request.user_id,
            plan_request.constitution_type,
            plan_request.health_goals,
            plan_request.health_data,
            plan_request.preferences,
            plan_request.current_season
        )

        # 添加后台任务记录健康计划活动
        background_tasks.add_task(
            log_health_plan_creation,
            plan["user_id"],
            plan["plan_id"]
        )

        return plan
    except Exception as e:
        logger.error(f"创建健康计划失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建健康计划失败: {str(e)}"
        )

@router.get("/{plan_id}", response_model=HealthPlanResponse)
async def get_health_plan(plan_id: str, user_id: str):
    """
    获取特定健康计划
    """
    try:
        # 这里应该从数据库或缓存获取健康计划
        # 模拟数据，实际应用中需要替换
        if not user_id or not plan_id:
            raise ValueError("用户ID和计划ID不能为空")

        # 模拟检索计划
        plan = {
            "plan_id": plan_id,
            "user_id": user_id,
            "constitution_type": "平和质",
            "creation_date": datetime.now().isoformat(),
            "health_goals": ["改善睡眠", "增强体质"],
            "diet_recommendations": ["保持清淡饮食", "多摄入蔬菜水果"],
            "exercise_recommendations": ["每天30分钟中等强度有氧运动", "适当进行力量训练"],
            "lifestyle_recommendations": ["保持规律作息", "减少电子设备使用时间"],
            "supplement_recommendations": ["根据需要补充维生素D", "适量补充Omega-3脂肪酸"],
            "schedule": {
                "早晨": "6:30起床，热水泡脚",
                "上午": "适当运动，保持活力",
                "中午": "午餐清淡，适当午休",
                "下午": "工作学习，保持专注",
                "晚上": "轻松活动，避免过度兴奋",
                "睡前": "热水泡脚，冥想放松，22:30前入睡"
            }
        }

        return plan
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"获取健康计划失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取健康计划失败: {str(e)}"
        )

@router.post("/progress", response_model=HealthPlanProgressResponse)
async def update_health_plan_progress(progress: HealthPlanProgressRequest):
    """
    更新健康计划进度
    """
    try:
        # 这里应该更新数据库中的进度记录
        # 并计算完成百分比
        # 模拟响应数据
        response = HealthPlanProgressResponse(
            user_id=progress.user_id,
            plan_id=progress.plan_id,
            progress_percentage=75.5,  # 计算的进度百分比
            next_steps=["完成今天的有氧运动", "记录今日的饮食情况"],
            encouragement_message="做得很好！你已经完成了75%的计划内容，继续保持！"
        )

        return response
    except Exception as e:
        logger.error(f"更新健康计划进度失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新健康计划进度失败: {str(e)}"
        )

async def log_health_plan_creation(user_id: str, plan_id: str):
    """记录健康计划创建活动的后台任务"""
    logger.info(f"用户 {user_id} 创建了健康计划 {plan_id}")
    # 这里可以添加更多操作，如发送通知、更新统计等
