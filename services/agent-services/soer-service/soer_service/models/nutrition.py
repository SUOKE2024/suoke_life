"""
营养相关数据模型

定义食物、营养分析、膳食计划等数据结构
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NutrientInfo(BaseModel):
    """营养素信息模型"""
    name: str = Field(..., description="营养素名称")
    amount: float = Field(..., description="含量")
    unit: str = Field(..., description="单位")
    daily_value_percent: Optional[float] = Field(None, description="每日推荐值百分比")


class FoodItem(BaseModel):
    """食物项目模型"""
    name: str = Field(..., description="食物名称")
    amount: float = Field(..., description="食用量")
    unit: str = Field(..., description="单位")
    calories_per_unit: Optional[float] = Field(None, description="每单位热量")
    nutrients: List[NutrientInfo] = Field(default_factory=list, description="营养素列表")
    food_id: Optional[str] = Field(None, description="食物数据库ID")


class MacroNutrients(BaseModel):
    """宏量营养素模型"""
    calories: float = Field(..., description="总热量")
    protein: float = Field(..., description="蛋白质(g)")
    carbohydrates: float = Field(..., description="碳水化合物(g)")
    fat: float = Field(..., description="脂肪(g)")
    fiber: float = Field(default=0, description="膳食纤维(g)")
    sugar: float = Field(default=0, description="糖分(g)")


class MicroNutrients(BaseModel):
    """微量营养素模型"""
    vitamins: Dict[str, float] = Field(default_factory=dict, description="维生素")
    minerals: Dict[str, float] = Field(default_factory=dict, description="矿物质")


class NutritionAnalysis(BaseModel):
    """营养分析结果模型"""
    user_id: str = Field(..., description="用户ID")
    meal_type: str = Field(..., description="餐次类型")
    food_items: List[FoodItem] = Field(..., description="食物列表")
    macro_nutrients: MacroNutrients = Field(..., description="宏量营养素")
    micro_nutrients: MicroNutrients = Field(..., description="微量营养素")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    # 营养评估
    nutrition_score: float = Field(..., description="营养评分(0-100)")
    recommendations: List[str] = Field(default_factory=list, description="营养建议")
    warnings: List[str] = Field(default_factory=list, description="营养警告")
    
    # 中医营养学分析
    tcm_analysis: Dict[str, Any] = Field(default_factory=dict, description="中医营养分析")


class MealPlan(BaseModel):
    """单餐计划模型"""
    meal_type: str = Field(..., description="餐次类型")
    food_items: List[FoodItem] = Field(..., description="食物列表")
    target_calories: float = Field(..., description="目标热量")
    preparation_time: int = Field(..., description="准备时间(分钟)")
    difficulty: str = Field(..., description="制作难度")
    recipe_url: Optional[str] = Field(None, description="食谱链接")


class DietPlan(BaseModel):
    """膳食计划模型"""
    user_id: str = Field(..., description="用户ID")
    plan_name: str = Field(..., description="计划名称")
    start_date: datetime = Field(..., description="开始日期")
    duration_days: int = Field(..., description="持续天数")
    
    # 目标设定
    daily_calorie_target: float = Field(..., description="每日热量目标")
    macro_targets: MacroNutrients = Field(..., description="宏量营养素目标")
    health_goals: List[str] = Field(default_factory=list, description="健康目标")
    dietary_restrictions: List[str] = Field(default_factory=list, description="饮食限制")
    
    # 膳食安排
    daily_meals: List[MealPlan] = Field(..., description="每日膳食安排")
    
    # 计划评估
    plan_score: float = Field(..., description="计划评分")
    expected_outcomes: List[str] = Field(default_factory=list, description="预期效果")
    
    # 中医膳食理论
    tcm_principles: Dict[str, Any] = Field(default_factory=dict, description="中医膳食原则")


class NutritionGoal(BaseModel):
    """营养目标模型"""
    user_id: str = Field(..., description="用户ID")
    goal_type: str = Field(..., description="目标类型")
    target_value: float = Field(..., description="目标值")
    current_value: float = Field(..., description="当前值")
    unit: str = Field(..., description="单位")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    progress: float = Field(default=0, description="进度百分比")


class FoodDatabase(BaseModel):
    """食物数据库条目模型"""
    food_id: str = Field(..., description="食物ID")
    name: str = Field(..., description="食物名称")
    category: str = Field(..., description="食物分类")
    brand: Optional[str] = Field(None, description="品牌")
    serving_size: float = Field(..., description="标准份量")
    serving_unit: str = Field(..., description="份量单位")
    nutrients_per_serving: List[NutrientInfo] = Field(..., description="每份营养素")
    
    # 中医属性
    tcm_properties: Dict[str, str] = Field(default_factory=dict, description="中医属性")
    seasonal_suitability: List[str] = Field(default_factory=list, description="适宜季节") 