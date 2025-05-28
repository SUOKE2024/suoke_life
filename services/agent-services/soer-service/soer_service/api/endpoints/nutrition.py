"""
营养分析 API 端点

提供食物营养分析、膳食建议等功能
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ...core.monitoring import record_nutrition_analysis
from ...services.nutrition_service import NutritionService
from ...models.nutrition import FoodItem, NutritionAnalysis, DietPlan

router = APIRouter()


class FoodAnalysisRequest(BaseModel):
    """食物分析请求模型"""
    food_items: List[FoodItem]
    user_id: str
    meal_type: str = "breakfast"  # breakfast, lunch, dinner, snack


class DietPlanRequest(BaseModel):
    """膳食计划请求模型"""
    user_id: str
    target_calories: int
    dietary_restrictions: List[str] = []
    health_goals: List[str] = []


@router.post("/analyze", response_model=NutritionAnalysis)
async def analyze_nutrition(
    request: FoodAnalysisRequest,
    nutrition_service: NutritionService = Depends()
) -> NutritionAnalysis:
    """
    分析食物营养成分
    
    Args:
        request: 食物分析请求
        nutrition_service: 营养服务实例
        
    Returns:
        营养分析结果
    """
    try:
        # 记录指标
        record_nutrition_analysis()
        
        # 执行营养分析
        analysis = await nutrition_service.analyze_nutrition(
            food_items=request.food_items,
            user_id=request.user_id,
            meal_type=request.meal_type
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"营养分析失败: {str(e)}")


@router.post("/diet-plan", response_model=DietPlan)
async def generate_diet_plan(
    request: DietPlanRequest,
    nutrition_service: NutritionService = Depends()
) -> DietPlan:
    """
    生成个性化膳食计划
    
    Args:
        request: 膳食计划请求
        nutrition_service: 营养服务实例
        
    Returns:
        膳食计划
    """
    try:
        diet_plan = await nutrition_service.generate_diet_plan(
            user_id=request.user_id,
            target_calories=request.target_calories,
            dietary_restrictions=request.dietary_restrictions,
            health_goals=request.health_goals
        )
        
        return diet_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"膳食计划生成失败: {str(e)}")


@router.get("/food-database/search")
async def search_food_database(
    query: str,
    limit: int = 10,
    nutrition_service: NutritionService = Depends()
) -> List[Dict[str, Any]]:
    """
    搜索食物数据库
    
    Args:
        query: 搜索关键词
        limit: 返回结果数量限制
        nutrition_service: 营养服务实例
        
    Returns:
        食物搜索结果
    """
    try:
        results = await nutrition_service.search_food_database(
            query=query,
            limit=limit
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"食物搜索失败: {str(e)}")


@router.get("/recommendations/{user_id}")
async def get_nutrition_recommendations(
    user_id: str,
    nutrition_service: NutritionService = Depends()
) -> Dict[str, Any]:
    """
    获取个性化营养建议
    
    Args:
        user_id: 用户ID
        nutrition_service: 营养服务实例
        
    Returns:
        营养建议
    """
    try:
        recommendations = await nutrition_service.get_nutrition_recommendations(
            user_id=user_id
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取营养建议失败: {str(e)}")


@router.get("/history/{user_id}")
async def get_nutrition_history(
    user_id: str,
    days: int = 7,
    nutrition_service: NutritionService = Depends()
) -> List[Dict[str, Any]]:
    """
    获取用户营养历史记录
    
    Args:
        user_id: 用户ID
        days: 查询天数
        nutrition_service: 营养服务实例
        
    Returns:
        营养历史记录
    """
    try:
        history = await nutrition_service.get_nutrition_history(
            user_id=user_id,
            days=days
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取营养历史失败: {str(e)}") 