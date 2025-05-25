"""
食物相关数据模型
从原始的food_agriculture_service.py中提取的数据类
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

from ..enums.food_enums import (
    FoodCategory, FoodNature, FoodTaste, PreparationMethod, 
    StorageMethod, HealthBenefit, Contraindication
)
from ..enums.season_enums import SeasonType


@dataclass
class NutritionalInfo:
    """营养信息"""
    calories_per_100g: float
    protein: float              # 蛋白质 (g)
    carbohydrates: float        # 碳水化合物 (g)
    fat: float                  # 脂肪 (g)
    fiber: float                # 纤维 (g)
    vitamins: Dict[str, float]  # 维生素含量 (mg/μg)
    minerals: Dict[str, float]  # 矿物质含量 (mg)
    antioxidants: List[str]     # 抗氧化物质
    glycemic_index: Optional[int] = None  # 血糖指数
    water_content: Optional[float] = None  # 水分含量 (%)
    
    def get_total_macronutrients(self) -> float:
        """获取总宏量营养素"""
        return self.protein + self.carbohydrates + self.fat
    
    def get_protein_percentage(self) -> float:
        """获取蛋白质占比"""
        total = self.get_total_macronutrients()
        return (self.protein / total * 100) if total > 0 else 0
    
    def get_carb_percentage(self) -> float:
        """获取碳水化合物占比"""
        total = self.get_total_macronutrients()
        return (self.carbohydrates / total * 100) if total > 0 else 0
    
    def get_fat_percentage(self) -> float:
        """获取脂肪占比"""
        total = self.get_total_macronutrients()
        return (self.fat / total * 100) if total > 0 else 0


@dataclass
class FoodItem:
    """食物项目"""
    food_id: str
    name: str
    category: FoodCategory
    nature: FoodNature
    taste: FoodTaste
    meridian_tropism: List[str]  # 归经
    nutritional_info: NutritionalInfo
    health_benefits: List[HealthBenefit]
    contraindications: List[Contraindication]
    seasonal_availability: List[SeasonType]
    preparation_methods: List[PreparationMethod]
    storage_methods: List[StorageMethod]
    storage_tips: str
    origin_region: str
    scientific_name: Optional[str] = None  # 学名
    common_names: List[str] = field(default_factory=list)  # 别名
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def is_available_in_season(self, season: SeasonType) -> bool:
        """检查是否在指定季节可用"""
        return season in self.seasonal_availability
    
    def has_health_benefit(self, benefit: HealthBenefit) -> bool:
        """检查是否具有指定健康功效"""
        return benefit in self.health_benefits
    
    def has_contraindication(self, condition: Contraindication) -> bool:
        """检查是否有指定禁忌症"""
        return condition in self.contraindications
    
    def can_be_prepared_as(self, method: PreparationMethod) -> bool:
        """检查是否可以用指定方法烹饪"""
        return method in self.preparation_methods
    
    def get_calories_per_serving(self, serving_size_g: float) -> float:
        """获取每份的卡路里"""
        return (self.nutritional_info.calories_per_100g * serving_size_g) / 100


@dataclass
class FoodCombination:
    """食物搭配"""
    combination_id: str
    name: str
    primary_food: str  # 主要食物ID
    secondary_foods: List[str]  # 搭配食物ID列表
    combination_type: str  # 搭配类型：synergistic, complementary, balanced
    health_benefits: List[HealthBenefit]
    preparation_instructions: List[str]
    nutritional_enhancement: Dict[str, float]  # 营养增强效果
    taste_profile: str
    recommended_portions: Dict[str, float]  # 推荐分量
    cooking_time: Optional[int] = None  # 烹饪时间（分钟）
    difficulty_level: str = "medium"  # 难度等级：easy, medium, hard
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FoodAllergy:
    """食物过敏信息"""
    allergy_id: str
    allergen_name: str
    allergen_type: str  # protein, carbohydrate, additive, etc.
    severity_level: str  # mild, moderate, severe
    symptoms: List[str]
    cross_reactive_foods: List[str]  # 交叉反应食物
    alternative_foods: List[str]  # 替代食物
    avoidance_tips: List[str]
    emergency_instructions: str
    
    def is_severe(self) -> bool:
        """是否为严重过敏"""
        return self.severity_level == "severe"


@dataclass
class FoodInteraction:
    """食物相互作用"""
    interaction_id: str
    food_a: str  # 食物A的ID
    food_b: str  # 食物B的ID
    interaction_type: str  # positive, negative, neutral
    effect_description: str
    mechanism: str  # 作用机制
    evidence_level: str  # high, medium, low
    recommendations: List[str]
    time_gap_required: Optional[int] = None  # 需要间隔的时间（分钟）
    
    def is_positive_interaction(self) -> bool:
        """是否为正面相互作用"""
        return self.interaction_type == "positive"
    
    def is_negative_interaction(self) -> bool:
        """是否为负面相互作用"""
        return self.interaction_type == "negative"


@dataclass
class FoodPreservation:
    """食物保存信息"""
    preservation_id: str
    food_id: str
    storage_method: StorageMethod
    optimal_temperature: Optional[float] = None  # 最佳温度（摄氏度）
    optimal_humidity: Optional[float] = None  # 最佳湿度（%）
    shelf_life_days: int = 0  # 保质期（天）
    storage_containers: List[str] = field(default_factory=list)
    preparation_before_storage: List[str] = field(default_factory=list)
    signs_of_spoilage: List[str] = field(default_factory=list)
    food_safety_tips: List[str] = field(default_factory=list)
    
    def is_expired(self, storage_date: datetime) -> bool:
        """检查是否过期"""
        days_stored = (datetime.now() - storage_date).days
        return days_stored > self.shelf_life_days


@dataclass
class FoodNutrientDensity:
    """食物营养密度"""
    food_id: str
    nutrient_density_score: float  # 营养密度评分 (0-100)
    key_nutrients: List[str]  # 关键营养素
    nutrient_per_calorie: Dict[str, float]  # 每卡路里营养素含量
    ranking_category: str  # 在同类食物中的排名：excellent, good, fair, poor
    
    def is_nutrient_dense(self) -> bool:
        """是否为营养密集型食物"""
        return self.nutrient_density_score >= 70
    
    def get_ranking_level(self) -> str:
        """获取营养密度等级"""
        if self.nutrient_density_score >= 90:
            return "excellent"
        elif self.nutrient_density_score >= 70:
            return "good"
        elif self.nutrient_density_score >= 50:
            return "fair"
        else:
            return "poor" 