"""
增强版食农结合服务
优化与med-knowledge服务的集成，提供更智能的食疗和农业指导
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import aiohttp

try:
    from .food_agriculture_service import (
        FoodAgricultureService,
        FoodItem,
        AgriculturalProduct,
        FoodTherapyPlan,
        PlantingGuidance,
        ConstitutionType,
        SeasonType,
        FoodProperty,
        FoodTaste
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    current_dir = os.path.dirname(__file__)
    sys.path.append(current_dir)
    try:
        from food_agriculture_service import (
            FoodAgricultureService,
            FoodItem,
            AgriculturalProduct,
            FoodTherapyPlan,
            PlantingGuidance,
            ConstitutionType,
            SeasonType,
            FoodProperty,
            FoodTaste
        )
    except ImportError:
        # 如果还是失败，创建模拟类
        from dataclasses import dataclass, field
        from datetime import datetime
        from enum import Enum
        from typing import Dict, List, Any, Optional
        
        class ConstitutionType(Enum):
            BALANCED = "balanced"
            QI_DEFICIENCY = "qi_deficiency"
            YANG_DEFICIENCY = "yang_deficiency"
            YIN_DEFICIENCY = "yin_deficiency"
            PHLEGM_DAMPNESS = "phlegm_dampness"
            DAMP_HEAT = "damp_heat"
            BLOOD_STASIS = "blood_stasis"
            QI_STAGNATION = "qi_stagnation"
            SPECIAL_CONSTITUTION = "special_constitution"
        
        class SeasonType(Enum):
            SPRING = "spring"
            SUMMER = "summer"
            AUTUMN = "autumn"
            WINTER = "winter"
        
        class FoodProperty(Enum):
            NOURISHING = "nourishing"
            DETOXIFYING = "detoxifying"
            WARMING = "warming"
            COOLING = "cooling"
        
        class FoodTaste(Enum):
            SWEET = "sweet"
            SOUR = "sour"
            BITTER = "bitter"
            SPICY = "spicy"
            SALTY = "salty"
        
        @dataclass
        class FoodItem:
            food_id: str
            name: str
            category: str
            nature: str
            taste: str
            meridian_tropism: List[str] = field(default_factory=list)
            nutritional_info: Dict[str, Any] = field(default_factory=dict)
            health_benefits: List[str] = field(default_factory=list)
            contraindications: List[str] = field(default_factory=list)
            seasonal_availability: List[str] = field(default_factory=list)
            preparation_methods: List[str] = field(default_factory=list)
            storage_tips: str = ""
            origin_region: str = ""
            created_at: datetime = field(default_factory=datetime.now)
        
        @dataclass
        class AgriculturalProduct:
            product_id: str
            name: str
            variety: str = ""
            agriculture_type: str = ""
            cultivation_method: str = ""
            growing_region: str = ""
            planting_date: datetime = field(default_factory=datetime.now)
            harvest_date: Optional[datetime] = None
            quality_grade: str = ""
            certification: List[str] = field(default_factory=list)
            traceability_code: str = ""
            nutritional_analysis: Dict[str, Any] = field(default_factory=dict)
            pesticide_residue: Dict[str, float] = field(default_factory=dict)
            heavy_metals: Dict[str, float] = field(default_factory=dict)
            supplier_info: Dict[str, Any] = field(default_factory=dict)
            price_per_kg: float = 0.0
            availability_status: str = ""
        
        @dataclass
        class FoodTherapyPlan:
            plan_id: str
            name: str
            target_constitution: ConstitutionType
            target_symptoms: List[str] = field(default_factory=list)
            duration_days: int = 0
            daily_meals: Dict[str, List[str]] = field(default_factory=dict)
            preparation_instructions: List[str] = field(default_factory=list)
            expected_benefits: List[str] = field(default_factory=list)
            precautions: List[str] = field(default_factory=list)
            progress_indicators: List[str] = field(default_factory=list)
            created_at: datetime = field(default_factory=datetime.now)
        
        @dataclass
        class PlantingGuidance:
            guidance_id: str
            crop_name: str
            variety: str = ""
            region: str = ""
            season: SeasonType = SeasonType.SPRING
            soil_requirements: Dict[str, Any] = field(default_factory=dict)
            climate_conditions: Dict[str, Any] = field(default_factory=dict)
            planting_schedule: Dict[str, str] = field(default_factory=dict)
            care_instructions: List[str] = field(default_factory=list)
            pest_management: List[str] = field(default_factory=list)
            harvest_timing: str = ""
            yield_expectations: Dict[str, float] = field(default_factory=dict)
            quality_optimization: List[str] = field(default_factory=list)
            post_harvest_handling: List[str] = field(default_factory=list)
            created_at: datetime = field(default_factory=datetime.now)
        
        class FoodAgricultureService:
            def __init__(self, config: Dict[str, Any]):
                self.config = config
            
            async def recommend_foods_by_constitution(self, constitution_type: ConstitutionType, season: SeasonType = None) -> List[FoodItem]:
                return []

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeIntegration:
    """知识集成配置"""
    med_knowledge_url: str
    rag_service_url: str
    api_timeout: int = 30
    cache_ttl: int = 3600


@dataclass
class EnhancedFoodRecommendation:
    """增强版食物推荐"""
    food_item: FoodItem
    confidence_score: float
    knowledge_source: str
    scientific_evidence: List[str]
    contraindications: List[str]
    preparation_methods: List[str]
    seasonal_availability: Dict[str, bool]
    nutritional_analysis: Dict[str, Any]
    tcm_theory_basis: str


@dataclass
class PersonalizedNutritionPlan:
    """个性化营养计划"""
    plan_id: str
    user_id: str
    constitution_type: ConstitutionType
    health_goals: List[str]
    dietary_restrictions: List[str]
    daily_meal_plans: List[Dict[str, Any]]
    weekly_schedule: Dict[str, List[str]]
    shopping_list: List[Dict[str, Any]]
    cooking_instructions: List[Dict[str, Any]]
    progress_tracking: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SmartPlantingPlan:
    """智能种植计划"""
    plan_id: str
    user_id: str
    location: str
    climate_zone: str
    soil_type: str
    available_space: float  # 平方米
    recommended_crops: List[AgriculturalProduct]
    planting_calendar: Dict[str, List[str]]
    care_instructions: List[Dict[str, Any]]
    expected_yield: Dict[str, float]
    health_benefits: List[str]
    investment_analysis: Dict[str, float]


class EnhancedFoodAgricultureService(FoodAgricultureService):
    """增强版食农结合服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版食农结合服务

        Args:
            config: 配置信息
        """
        super().__init__(config)
        
        # 知识集成配置
        self.knowledge_integration = KnowledgeIntegration(
            med_knowledge_url=config.get("med_knowledge_url", "http://med-knowledge:8000"),
            rag_service_url=config.get("rag_service_url", "http://rag-service:8000"),
            api_timeout=config.get("api_timeout", 30),
            cache_ttl=config.get("cache_ttl", 3600)
        )
        
        # 增强配置
        self.enhanced_config = {
            "ai_recommendation": {
                "enabled": True,
                "confidence_threshold": 0.7,
                "max_recommendations": 10
            },
            "knowledge_fusion": {
                "tcm_weight": 0.4,
                "modern_nutrition_weight": 0.3,
                "user_preference_weight": 0.2,
                "seasonal_weight": 0.1
            },
            "personalization": {
                "learning_enabled": True,
                "feedback_weight": 0.3,
                "adaptation_rate": 0.1
            }
        }
        
        # 缓存
        self.knowledge_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.recommendation_cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # 用户偏好学习
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.user_feedback: Dict[str, List[Dict[str, Any]]] = {}

    async def get_enhanced_food_recommendations(
        self, 
        user_id: str,
        constitution_type: ConstitutionType,
        health_goals: List[str],
        current_symptoms: List[str] = None,
        dietary_restrictions: List[str] = None,
        season: SeasonType = None
    ) -> List[EnhancedFoodRecommendation]:
        """
        获取增强版食物推荐

        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_goals: 健康目标
            current_symptoms: 当前症状
            dietary_restrictions: 饮食限制
            season: 季节

        Returns:
            增强版食物推荐列表
        """
        try:
            logger.info(f"开始生成增强版食物推荐，用户ID: {user_id}")
            
            # 获取基础推荐
            basic_recommendations = await self.recommend_foods_by_constitution(constitution_type, season)
            
            # 获取中医知识增强
            tcm_knowledge = await self._get_tcm_food_knowledge(constitution_type, health_goals, current_symptoms)
            
            # 获取现代营养学知识
            nutrition_knowledge = await self._get_nutrition_knowledge(health_goals, current_symptoms)
            
            # 获取用户偏好
            user_prefs = await self._get_user_preferences(user_id)
            
            # 融合知识生成增强推荐
            enhanced_recommendations = []
            
            for food_item in basic_recommendations:
                # 计算综合推荐分数
                confidence_score = await self._calculate_enhanced_confidence_score(
                    food_item, constitution_type, health_goals, tcm_knowledge, 
                    nutrition_knowledge, user_prefs, current_symptoms
                )
                
                if confidence_score >= self.enhanced_config["ai_recommendation"]["confidence_threshold"]:
                    # 获取科学证据
                    scientific_evidence = await self._get_scientific_evidence(food_item, health_goals)
                    
                    # 获取禁忌信息
                    contraindications = await self._get_contraindications(food_item, current_symptoms, dietary_restrictions)
                    
                    # 获取制作方法
                    preparation_methods = await self._get_preparation_methods(food_item, constitution_type)
                    
                    # 获取季节性可用性
                    seasonal_availability = await self._get_seasonal_availability(food_item)
                    
                    # 获取营养分析
                    nutritional_analysis = await self._get_nutritional_analysis(food_item)
                    
                    # 获取中医理论基础
                    tcm_theory_basis = await self._get_tcm_theory_basis(food_item, constitution_type)
                    
                    enhanced_rec = EnhancedFoodRecommendation(
                        food_item=food_item,
                        confidence_score=confidence_score,
                        knowledge_source="TCM + Modern Nutrition + AI",
                        scientific_evidence=scientific_evidence,
                        contraindications=contraindications,
                        preparation_methods=preparation_methods,
                        seasonal_availability=seasonal_availability,
                        nutritional_analysis=nutritional_analysis,
                        tcm_theory_basis=tcm_theory_basis
                    )
                    
                    enhanced_recommendations.append(enhanced_rec)
            
            # 按置信度排序
            enhanced_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # 限制返回数量
            max_recs = self.enhanced_config["ai_recommendation"]["max_recommendations"]
            enhanced_recommendations = enhanced_recommendations[:max_recs]
            
            logger.info(f"生成了 {len(enhanced_recommendations)} 个增强版食物推荐")
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"生成增强版食物推荐失败: {e}")
            raise

    async def create_personalized_nutrition_plan(
        self,
        user_id: str,
        constitution_type: ConstitutionType,
        health_goals: List[str],
        dietary_restrictions: List[str] = None,
        duration_weeks: int = 4
    ) -> PersonalizedNutritionPlan:
        """
        创建个性化营养计划

        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_goals: 健康目标
            dietary_restrictions: 饮食限制
            duration_weeks: 计划持续周数

        Returns:
            个性化营养计划
        """
        try:
            logger.info(f"开始创建个性化营养计划，用户ID: {user_id}")
            
            # 获取增强版食物推荐
            food_recommendations = await self.get_enhanced_food_recommendations(
                user_id, constitution_type, health_goals, dietary_restrictions=dietary_restrictions
            )
            
            # 生成每日膳食计划
            daily_meal_plans = await self._generate_daily_meal_plans(
                food_recommendations, constitution_type, health_goals, duration_weeks * 7
            )
            
            # 生成周计划
            weekly_schedule = await self._generate_weekly_schedule(daily_meal_plans, duration_weeks)
            
            # 生成购物清单
            shopping_list = await self._generate_shopping_list(daily_meal_plans)
            
            # 生成烹饪指导
            cooking_instructions = await self._generate_cooking_instructions(food_recommendations)
            
            # 初始化进度跟踪
            progress_tracking = {
                "start_date": datetime.now().isoformat(),
                "target_goals": health_goals,
                "weekly_checkpoints": [],
                "adherence_score": 0.0,
                "health_improvements": []
            }
            
            plan = PersonalizedNutritionPlan(
                plan_id=str(uuid.uuid4()),
                user_id=user_id,
                constitution_type=constitution_type,
                health_goals=health_goals,
                dietary_restrictions=dietary_restrictions or [],
                daily_meal_plans=daily_meal_plans,
                weekly_schedule=weekly_schedule,
                shopping_list=shopping_list,
                cooking_instructions=cooking_instructions,
                progress_tracking=progress_tracking
            )
            
            logger.info(f"个性化营养计划创建成功，计划ID: {plan.plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"创建个性化营养计划失败: {e}")
            raise

    async def create_smart_planting_plan(
        self,
        user_id: str,
        location: str,
        available_space: float,
        constitution_type: ConstitutionType = None,
        health_goals: List[str] = None
    ) -> SmartPlantingPlan:
        """
        创建智能种植计划

        Args:
            user_id: 用户ID
            location: 种植地点
            available_space: 可用空间（平方米）
            constitution_type: 体质类型
            health_goals: 健康目标

        Returns:
            智能种植计划
        """
        try:
            logger.info(f"开始创建智能种植计划，用户ID: {user_id}")
            
            # 获取气候和土壤信息
            climate_info = await self._get_climate_info(location)
            soil_info = await self._get_soil_info(location)
            
            # 获取适合的农产品
            suitable_crops = await self._get_suitable_crops(
                climate_info, soil_info, available_space, constitution_type, health_goals
            )
            
            # 生成种植日历
            planting_calendar = await self._generate_planting_calendar(suitable_crops, climate_info)
            
            # 生成护理指导
            care_instructions = await self._generate_care_instructions(suitable_crops)
            
            # 预测产量
            expected_yield = await self._predict_yield(suitable_crops, available_space, climate_info)
            
            # 分析健康益处
            health_benefits = await self._analyze_health_benefits(suitable_crops, constitution_type)
            
            # 投资分析
            investment_analysis = await self._analyze_investment(suitable_crops, available_space)
            
            plan = SmartPlantingPlan(
                plan_id=str(uuid.uuid4()),
                user_id=user_id,
                location=location,
                climate_zone=climate_info.get("zone", "unknown"),
                soil_type=soil_info.get("type", "unknown"),
                available_space=available_space,
                recommended_crops=suitable_crops,
                planting_calendar=planting_calendar,
                care_instructions=care_instructions,
                expected_yield=expected_yield,
                health_benefits=health_benefits,
                investment_analysis=investment_analysis
            )
            
            logger.info(f"智能种植计划创建成功，计划ID: {plan.plan_id}")
            return plan
            
        except Exception as e:
            logger.error(f"创建智能种植计划失败: {e}")
            raise

    async def _get_tcm_food_knowledge(
        self, constitution_type: ConstitutionType, health_goals: List[str], symptoms: List[str] = None
    ) -> Dict[str, Any]:
        """从med-knowledge服务获取中医食疗知识"""
        cache_key = f"tcm_food_{constitution_type.value}_{hash(tuple(health_goals))}"
        
        # 检查缓存
        cached_data = await self._get_from_cache(cache_key, self.knowledge_cache)
        if cached_data:
            return cached_data
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.knowledge_integration.med_knowledge_url}/api/v1/tcm/food-therapy"
                payload = {
                    "constitution_type": constitution_type.value,
                    "health_goals": health_goals,
                    "symptoms": symptoms or []
                }
                
                async with session.post(
                    url, 
                    json=payload, 
                    timeout=aiohttp.ClientTimeout(total=self.knowledge_integration.api_timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._set_to_cache(cache_key, data, self.knowledge_cache)
                        return data
                    else:
                        logger.warning(f"Med-knowledge服务返回错误: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"获取中医食疗知识失败: {e}")
            return {}

    async def _get_nutrition_knowledge(self, health_goals: List[str], symptoms: List[str] = None) -> Dict[str, Any]:
        """从RAG服务获取现代营养学知识"""
        cache_key = f"nutrition_{hash(tuple(health_goals))}"
        
        # 检查缓存
        cached_data = await self._get_from_cache(cache_key, self.knowledge_cache)
        if cached_data:
            return cached_data
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.knowledge_integration.rag_service_url}/api/v1/nutrition/search"
                payload = {
                    "query": " ".join(health_goals + (symptoms or [])),
                    "domain": "nutrition",
                    "max_results": 10
                }
                
                async with session.post(
                    url, 
                    json=payload, 
                    timeout=aiohttp.ClientTimeout(total=self.knowledge_integration.api_timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self._set_to_cache(cache_key, data, self.knowledge_cache)
                        return data
                    else:
                        logger.warning(f"RAG服务返回错误: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"获取营养学知识失败: {e}")
            return {}

    async def _calculate_enhanced_confidence_score(
        self,
        food_item: FoodItem,
        constitution_type: ConstitutionType,
        health_goals: List[str],
        tcm_knowledge: Dict[str, Any],
        nutrition_knowledge: Dict[str, Any],
        user_prefs: Dict[str, Any],
        symptoms: List[str] = None
    ) -> float:
        """计算增强版置信度分数"""
        weights = self.enhanced_config["knowledge_fusion"]
        total_score = 0.0
        
        # 中医理论分数
        tcm_score = await self._calculate_tcm_score(food_item, constitution_type, tcm_knowledge)
        total_score += tcm_score * weights["tcm_weight"]
        
        # 现代营养学分数
        nutrition_score = await self._calculate_nutrition_score(food_item, health_goals, nutrition_knowledge)
        total_score += nutrition_score * weights["modern_nutrition_weight"]
        
        # 用户偏好分数
        preference_score = await self._calculate_preference_score(food_item, user_prefs)
        total_score += preference_score * weights["user_preference_weight"]
        
        # 季节性分数
        seasonal_score = await self._calculate_seasonal_score(food_item)
        total_score += seasonal_score * weights["seasonal_weight"]
        
        return min(total_score, 1.0)

    async def _calculate_tcm_score(
        self, food_item: FoodItem, constitution_type: ConstitutionType, tcm_knowledge: Dict[str, Any]
    ) -> float:
        """计算中医理论分数"""
        score = 0.0
        
        # 基础体质匹配
        if constitution_type in food_item.suitable_constitutions:
            score += 0.4
        
        # 性味归经匹配
        if tcm_knowledge.get("recommended_properties"):
            recommended_props = tcm_knowledge["recommended_properties"]
            if food_item.properties in recommended_props:
                score += 0.3
        
        if tcm_knowledge.get("recommended_tastes"):
            recommended_tastes = tcm_knowledge["recommended_tastes"]
            if food_item.taste in recommended_tastes:
                score += 0.3
        
        return min(score, 1.0)

    async def _calculate_nutrition_score(
        self, food_item: FoodItem, health_goals: List[str], nutrition_knowledge: Dict[str, Any]
    ) -> float:
        """计算现代营养学分数"""
        score = 0.0
        
        # 营养成分匹配
        if nutrition_knowledge.get("beneficial_nutrients"):
            beneficial_nutrients = nutrition_knowledge["beneficial_nutrients"]
            food_nutrients = food_item.nutritional_info.keys()
            
            matching_nutrients = set(beneficial_nutrients) & set(food_nutrients)
            if matching_nutrients:
                score += len(matching_nutrients) / len(beneficial_nutrients) * 0.6
        
        # 健康功效匹配
        if nutrition_knowledge.get("health_benefits"):
            knowledge_benefits = nutrition_knowledge["health_benefits"]
            food_benefits = food_item.health_benefits
            
            matching_benefits = set(knowledge_benefits) & set(food_benefits)
            if matching_benefits:
                score += len(matching_benefits) / len(knowledge_benefits) * 0.4
        
        return min(score, 1.0)

    async def _calculate_preference_score(self, food_item: FoodItem, user_prefs: Dict[str, Any]) -> float:
        """计算用户偏好分数"""
        if not user_prefs:
            return 0.5  # 中性分数
        
        score = 0.0
        
        # 喜好食物类型
        if "preferred_categories" in user_prefs:
            if food_item.category in user_prefs["preferred_categories"]:
                score += 0.4
        
        # 口味偏好
        if "preferred_tastes" in user_prefs:
            if food_item.taste in user_prefs["preferred_tastes"]:
                score += 0.3
        
        # 历史反馈
        if "positive_feedback_foods" in user_prefs:
            if food_item.name in user_prefs["positive_feedback_foods"]:
                score += 0.3
        
        return min(score, 1.0)

    async def _calculate_seasonal_score(self, food_item: FoodItem) -> float:
        """计算季节性分数"""
        current_season = self._get_current_season()
        
        if current_season in food_item.seasonal_availability:
            return 1.0 if food_item.seasonal_availability[current_season] else 0.3
        
        return 0.5

    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户偏好"""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]
        
        # 从数据库或其他服务获取用户偏好
        # 这里返回默认偏好
        return {
            "preferred_categories": [],
            "preferred_tastes": [],
            "positive_feedback_foods": [],
            "negative_feedback_foods": []
        }

    async def _get_scientific_evidence(self, food_item: FoodItem, health_goals: List[str]) -> List[str]:
        """获取科学证据"""
        # 这里可以集成科学文献数据库
        evidence = []
        
        # 基于食物的健康功效生成证据
        for benefit in food_item.health_benefits:
            if any(goal in benefit for goal in health_goals):
                evidence.append(f"研究表明{food_item.name}具有{benefit}的功效")
        
        return evidence

    async def _get_contraindications(
        self, food_item: FoodItem, symptoms: List[str] = None, restrictions: List[str] = None
    ) -> List[str]:
        """获取禁忌信息"""
        contraindications = []
        
        # 基于症状的禁忌
        if symptoms:
            symptom_contraindications = {
                "腹泻": ["寒性食物", "生冷食物"],
                "便秘": ["热性食物", "辛辣食物"],
                "高血压": ["高盐食物", "高脂食物"],
                "糖尿病": ["高糖食物", "精制碳水化合物"]
            }
            
            for symptom in symptoms:
                if symptom in symptom_contraindications:
                    for contraindication in symptom_contraindications[symptom]:
                        if contraindication in food_item.description or contraindication in str(food_item.properties):
                            contraindications.append(f"{symptom}患者应避免食用")
        
        # 基于饮食限制的禁忌
        if restrictions:
            for restriction in restrictions:
                if restriction.lower() in food_item.name.lower() or restriction.lower() in food_item.description.lower():
                    contraindications.append(f"不适合{restriction}限制的人群")
        
        return contraindications

    async def _get_preparation_methods(self, food_item: FoodItem, constitution_type: ConstitutionType) -> List[str]:
        """获取制作方法"""
        methods = []
        
        # 基于体质推荐制作方法
        constitution_methods = {
            ConstitutionType.QI_DEFICIENCY: ["蒸煮", "炖煮", "温热食用"],
            ConstitutionType.YANG_DEFICIENCY: ["温热烹饪", "加入温性调料", "避免生冷"],
            ConstitutionType.YIN_DEFICIENCY: ["清蒸", "水煮", "少油少盐"],
            ConstitutionType.PHLEGM_DAMPNESS: ["清淡烹饪", "少油", "配合利湿食材"],
            ConstitutionType.DAMP_HEAT: ["清淡烹饪", "水煮", "配合清热食材"]
        }
        
        if constitution_type in constitution_methods:
            methods.extend(constitution_methods[constitution_type])
        
        # 基于食物性质推荐方法
        if food_item.properties == FoodProperty.COLD:
            methods.append("温热烹饪以中和寒性")
        elif food_item.properties == FoodProperty.HOT:
            methods.append("清淡烹饪以缓解热性")
        
        return methods

    async def _get_seasonal_availability(self, food_item: FoodItem) -> Dict[str, bool]:
        """获取季节性可用性"""
        # 返回食物的季节性可用性
        return food_item.seasonal_availability

    async def _get_nutritional_analysis(self, food_item: FoodItem) -> Dict[str, Any]:
        """获取营养分析"""
        analysis = {
            "basic_nutrition": food_item.nutritional_info,
            "calorie_density": "中等",  # 可以根据实际营养信息计算
            "nutrient_highlights": [],
            "dietary_fiber_content": "丰富" if "膳食纤维" in food_item.nutritional_info else "一般"
        }
        
        # 分析营养亮点
        for nutrient, value in food_item.nutritional_info.items():
            if isinstance(value, (int, float)) and value > 10:  # 简单的阈值判断
                analysis["nutrient_highlights"].append(f"富含{nutrient}")
        
        return analysis

    async def _get_tcm_theory_basis(self, food_item: FoodItem, constitution_type: ConstitutionType) -> str:
        """获取中医理论基础"""
        basis = f"{food_item.name}性{food_item.properties.value}，味{food_item.taste.value}"
        
        # 根据体质添加理论说明
        constitution_theory = {
            ConstitutionType.QI_DEFICIENCY: "气虚体质宜食甘温之品以补气",
            ConstitutionType.YANG_DEFICIENCY: "阳虚体质宜食温热之品以助阳",
            ConstitutionType.YIN_DEFICIENCY: "阴虚体质宜食甘凉之品以滋阴",
            ConstitutionType.PHLEGM_DAMPNESS: "痰湿体质宜食淡渗之品以化湿",
            ConstitutionType.DAMP_HEAT: "湿热体质宜食清淡之品以清热利湿"
        }
        
        if constitution_type in constitution_theory:
            basis += f"。{constitution_theory[constitution_type]}"
        
        return basis

    async def _generate_daily_meal_plans(
        self, 
        food_recommendations: List[EnhancedFoodRecommendation], 
        constitution_type: ConstitutionType,
        health_goals: List[str],
        days: int
    ) -> List[Dict[str, Any]]:
        """生成每日膳食计划"""
        daily_plans = []
        
        for day in range(days):
            # 为每一天生成三餐计划
            breakfast_foods = [rec for rec in food_recommendations if "早餐" in rec.food_item.description or rec.food_item.category == "谷物"][:2]
            lunch_foods = [rec for rec in food_recommendations if "午餐" in rec.food_item.description or rec.food_item.category in ["蔬菜", "肉类"]][:3]
            dinner_foods = [rec for rec in food_recommendations if "晚餐" in rec.food_item.description or rec.food_item.category in ["蔬菜", "汤品"]][:3]
            
            daily_plan = {
                "day": day + 1,
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "meals": {
                    "breakfast": {
                        "foods": [rec.food_item.name for rec in breakfast_foods],
                        "preparation": breakfast_foods[0].preparation_methods if breakfast_foods else [],
                        "health_focus": "补充能量，调理脾胃"
                    },
                    "lunch": {
                        "foods": [rec.food_item.name for rec in lunch_foods],
                        "preparation": lunch_foods[0].preparation_methods if lunch_foods else [],
                        "health_focus": "营养均衡，增强体质"
                    },
                    "dinner": {
                        "foods": [rec.food_item.name for rec in dinner_foods],
                        "preparation": dinner_foods[0].preparation_methods if dinner_foods else [],
                        "health_focus": "清淡易消化，安神助眠"
                    }
                },
                "daily_health_tip": await self._generate_daily_health_tip(constitution_type, day)
            }
            
            daily_plans.append(daily_plan)
        
        return daily_plans

    async def _generate_weekly_schedule(self, daily_plans: List[Dict[str, Any]], weeks: int) -> Dict[str, List[str]]:
        """生成周计划"""
        weekly_schedule = {}
        
        for week in range(weeks):
            week_key = f"第{week + 1}周"
            week_plans = daily_plans[week * 7:(week + 1) * 7]
            
            weekly_schedule[week_key] = [
                f"第{plan['day']}天: {', '.join(plan['meals']['breakfast']['foods'])} | "
                f"{', '.join(plan['meals']['lunch']['foods'])} | "
                f"{', '.join(plan['meals']['dinner']['foods'])}"
                for plan in week_plans
            ]
        
        return weekly_schedule

    async def _generate_shopping_list(self, daily_plans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成购物清单"""
        food_counts = {}
        
        # 统计所有食物的使用频次
        for plan in daily_plans:
            for meal_type, meal_info in plan["meals"].items():
                for food in meal_info["foods"]:
                    food_counts[food] = food_counts.get(food, 0) + 1
        
        shopping_list = []
        for food, count in food_counts.items():
            shopping_list.append({
                "item": food,
                "quantity": f"{count}份",
                "category": "食材",  # 可以根据食物类型细分
                "priority": "高" if count > 5 else "中"
            })
        
        return shopping_list

    async def _generate_cooking_instructions(self, food_recommendations: List[EnhancedFoodRecommendation]) -> List[Dict[str, Any]]:
        """生成烹饪指导"""
        instructions = []
        
        for rec in food_recommendations[:5]:  # 取前5个推荐
            instruction = {
                "food_name": rec.food_item.name,
                "preparation_methods": rec.preparation_methods,
                "cooking_tips": [
                    f"根据{rec.tcm_theory_basis}的理论指导烹饪",
                    "注意火候控制，保持营养成分",
                    "可根据个人口味适当调整"
                ],
                "health_benefits": rec.food_item.health_benefits,
                "contraindications": rec.contraindications
            }
            instructions.append(instruction)
        
        return instructions

    async def _generate_daily_health_tip(self, constitution_type: ConstitutionType, day: int) -> str:
        """生成每日健康提示"""
        tips = {
            ConstitutionType.QI_DEFICIENCY: [
                "气虚体质应注意规律作息，避免过度劳累",
                "适当进行缓和的运动，如太极拳、八段锦",
                "饮食宜温热，避免生冷食物",
                "保持心情愉悦，避免过度思虑"
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                "阳虚体质应注意保暖，避免受寒",
                "多食温热食物，少食寒凉",
                "适当晒太阳，补充阳气",
                "早睡早起，保证充足睡眠"
            ]
        }
        
        constitution_tips = tips.get(constitution_type, ["保持健康的生活方式"])
        return constitution_tips[day % len(constitution_tips)]

    async def _get_from_cache(self, key: str, cache: Dict[str, Tuple[Any, datetime]]) -> Optional[Any]:
        """从缓存获取数据"""
        if key in cache:
            data, timestamp = cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.knowledge_integration.cache_ttl):
                return data
            else:
                del cache[key]
        return None

    async def _set_to_cache(self, key: str, data: Any, cache: Dict[str, Tuple[Any, datetime]]):
        """设置缓存数据"""
        cache[key] = (data, datetime.now())

    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        elif month in [9, 10, 11]:
            return "秋季"
        else:
            return "冬季"

    # 智能种植相关方法
    async def _get_climate_info(self, location: str) -> Dict[str, Any]:
        """获取气候信息"""
        # 这里可以集成天气API
        return {
            "zone": "温带季风气候",
            "average_temperature": 15.0,
            "annual_rainfall": 600.0,
            "frost_free_days": 200,
            "growing_season": "3-11月"
        }

    async def _get_soil_info(self, location: str) -> Dict[str, Any]:
        """获取土壤信息"""
        # 这里可以集成土壤数据库
        return {
            "type": "壤土",
            "ph": 6.5,
            "organic_matter": "中等",
            "drainage": "良好",
            "fertility": "中等"
        }

    async def _get_suitable_crops(
        self, 
        climate_info: Dict[str, Any], 
        soil_info: Dict[str, Any], 
        space: float,
        constitution_type: ConstitutionType = None,
        health_goals: List[str] = None
    ) -> List[AgriculturalProduct]:
        """获取适合的农作物"""
        # 基于气候、土壤和健康需求推荐作物
        suitable_crops = []
        
        # 从现有农产品中筛选
        for product in self.agricultural_products.values():
            # 简单的适宜性判断
            if self._is_crop_suitable(product, climate_info, soil_info, space):
                suitable_crops.append(product)
        
        return suitable_crops[:10]  # 返回前10个推荐

    def _is_crop_suitable(
        self, 
        product: AgriculturalProduct, 
        climate_info: Dict[str, Any], 
        soil_info: Dict[str, Any], 
        space: float
    ) -> bool:
        """判断作物是否适合"""
        # 简单的适宜性判断逻辑
        if space < 1.0 and product.name in ["玉米", "小麦"]:  # 大型作物需要更多空间
            return False
        
        if soil_info["ph"] < 6.0 and product.name in ["番茄", "辣椒"]:  # 某些作物对pH敏感
            return False
        
        return True

    async def _generate_planting_calendar(
        self, crops: List[AgriculturalProduct], climate_info: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """生成种植日历"""
        calendar = {}
        
        # 基于作物特性和气候生成种植时间表
        months = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
        
        for month in months:
            calendar[month] = []
            
            for crop in crops:
                # 简单的种植时间判断
                if month in ["3月", "4月", "5月"] and crop.planting_season == SeasonType.SPRING:
                    calendar[month].append(f"种植{crop.name}")
                elif month in ["6月", "7月", "8月"] and crop.planting_season == SeasonType.SUMMER:
                    calendar[month].append(f"种植{crop.name}")
                elif month in ["9月", "10月"] and crop.planting_season == SeasonType.AUTUMN:
                    calendar[month].append(f"种植{crop.name}")
        
        return calendar

    async def _generate_care_instructions(self, crops: List[AgriculturalProduct]) -> List[Dict[str, Any]]:
        """生成护理指导"""
        instructions = []
        
        for crop in crops:
            instruction = {
                "crop_name": crop.name,
                "watering": "保持土壤湿润，避免积水",
                "fertilizing": "定期施用有机肥",
                "pest_control": "采用生物防治方法",
                "harvesting": f"在{crop.harvest_season.value}收获",
                "storage": "收获后及时处理和储存"
            }
            instructions.append(instruction)
        
        return instructions

    async def _predict_yield(
        self, crops: List[AgriculturalProduct], space: float, climate_info: Dict[str, Any]
    ) -> Dict[str, float]:
        """预测产量"""
        yield_prediction = {}
        
        for crop in crops:
            # 简单的产量预测模型
            base_yield = 5.0  # 基础产量 kg/m²
            space_factor = min(space / 10.0, 1.0)  # 空间因子
            climate_factor = 0.8  # 气候因子
            
            predicted_yield = base_yield * space_factor * climate_factor
            yield_prediction[crop.name] = round(predicted_yield, 2)
        
        return yield_prediction

    async def _analyze_health_benefits(
        self, crops: List[AgriculturalProduct], constitution_type: ConstitutionType = None
    ) -> List[str]:
        """分析健康益处"""
        benefits = set()
        
        for crop in crops:
            benefits.update(crop.health_benefits)
        
        # 根据体质添加特定益处
        if constitution_type:
            constitution_benefits = {
                ConstitutionType.QI_DEFICIENCY: ["补气养血", "增强体质"],
                ConstitutionType.YANG_DEFICIENCY: ["温阳助气", "改善循环"],
                ConstitutionType.YIN_DEFICIENCY: ["滋阴润燥", "清热生津"]
            }
            
            if constitution_type in constitution_benefits:
                benefits.update(constitution_benefits[constitution_type])
        
        return list(benefits)

    async def _analyze_investment(self, crops: List[AgriculturalProduct], space: float) -> Dict[str, float]:
        """投资分析"""
        analysis = {
            "initial_investment": 0.0,  # 初始投资
            "annual_maintenance": 0.0,  # 年度维护费用
            "expected_return": 0.0,     # 预期收益
            "payback_period": 0.0       # 回本周期（年）
        }
        
        # 简单的投资计算
        analysis["initial_investment"] = len(crops) * 50.0 + space * 20.0  # 种子费用 + 土地准备
        analysis["annual_maintenance"] = len(crops) * 30.0 + space * 10.0  # 肥料 + 工具
        analysis["expected_return"] = len(crops) * 200.0 * (space / 10.0)  # 预期产值
        
        if analysis["expected_return"] > analysis["annual_maintenance"]:
            net_annual_return = analysis["expected_return"] - analysis["annual_maintenance"]
            analysis["payback_period"] = analysis["initial_investment"] / net_annual_return
        else:
            analysis["payback_period"] = float('inf')
        
        return analysis 