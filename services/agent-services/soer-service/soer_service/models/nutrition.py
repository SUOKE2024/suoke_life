"""
营养相关模型
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FoodItem(BaseModel):
    """食物项目模型"""
    food_id: str = Field(..., description="食物ID")
    name: str = Field(..., description="食物名称")
    category: str = Field(..., description="食物类别")
    calories_per_100g: float = Field(..., description="每100克卡路里")
    protein_per_100g: float = Field(default=0.0, description="每100克蛋白质(g)")
    carbs_per_100g: float = Field(default=0.0, description="每100克碳水化合物(g)")
    fat_per_100g: float = Field(default=0.0, description="每100克脂肪(g)")
    fiber_per_100g: float = Field(default=0.0, description="每100克纤维(g)")
    nutrients: Optional[Dict[str, float]] = Field(default=None, description="其他营养素")


class NutritionAnalysis(BaseModel):
    """营养分析模型"""
    user_id: str = Field(..., description="用户ID")
    foods: List[Dict[str, Any]] = Field(..., description="食物列表")
    total_calories: float = Field(..., description="总卡路里")
    total_protein: float = Field(..., description="总蛋白质(g)")
    total_carbs: float = Field(..., description="总碳水化合物(g)")
    total_fat: float = Field(..., description="总脂肪(g)")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")
    recommendations: List[str] = Field(default_factory=list, description="营养建议")


class DietPlan(BaseModel):
    """膳食计划模型"""
    user_id: str = Field(..., description="用户ID")
    plan_name: str = Field(..., description="计划名称")
    duration_days: int = Field(..., description="计划天数")
    daily_meals: List[Dict[str, Any]] = Field(..., description="每日膳食")
    nutrition_targets: Dict[str, float] = Field(..., description="营养目标")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    notes: Optional[str] = Field(default=None, description="备注")
