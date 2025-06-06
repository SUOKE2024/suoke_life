"""
intelligent_nutrition_engine - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, date, time, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
import logging

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能营养管理引擎

提供个性化营养管理服务，包括：
- 营养状态评估
- 个性化膳食规划
- 中医食疗建议
- 营养监测和调整
- 特殊人群营养管理
"""



class NutrientType(str, Enum):
    """营养素类型"""
    MACRONUTRIENT = "macronutrient"         # 宏量营养素
    MICRONUTRIENT = "micronutrient"         # 微量营养素
    VITAMIN = "vitamin"                     # 维生素
    MINERAL = "mineral"                     # 矿物质
    AMINO_ACID = "amino_acid"               # 氨基酸
    FATTY_ACID = "fatty_acid"               # 脂肪酸

class FoodCategory(str, Enum):
    """食物类别"""
    GRAINS = "grains"                       # 谷物类
    VEGETABLES = "vegetables"               # 蔬菜类
    FRUITS = "fruits"                       # 水果类
    PROTEINS = "proteins"                   # 蛋白质类
    DAIRY = "dairy"                         # 乳制品类
    FATS_OILS = "fats_oils"                 # 油脂类
    NUTS_SEEDS = "nuts_seeds"               # 坚果种子类
    BEVERAGES = "beverages"                 # 饮品类

class TCMFoodNature(str, Enum):
    """中医食物性质"""
    HOT = "hot"                             # 热性
    WARM = "warm"                           # 温性
    NEUTRAL = "neutral"                     # 平性
    COOL = "cool"                           # 凉性
    COLD = "cold"                           # 寒性

class TCMFoodFlavor(str, Enum):
    """中医食物味道"""
    SWEET = "sweet"                         # 甘味
    SOUR = "sour"                           # 酸味
    BITTER = "bitter"                       # 苦味
    SPICY = "spicy"                         # 辛味
    SALTY = "salty"                         # 咸味

class NutritionalStatus(str, Enum):
    """营养状态"""
    EXCELLENT = "excellent"                 # 优秀
    GOOD = "good"                          # 良好
    ADEQUATE = "adequate"                  # 充足
    MARGINAL = "marginal"                  # 边缘
    DEFICIENT = "deficient"                # 缺乏
    UNDERWEIGHT = "underweight"               # 体重不足
    NORMAL = "normal"                        # 正常
    OVERWEIGHT = "overweight"                # 超重
    OBESE = "obese"                          # 肥胖

class DietaryGoal(str, Enum):
    """膳食目标"""
    WEIGHT_LOSS = "weight_loss"             # 减重
    WEIGHT_GAIN = "weight_gain"             # 增重
    MUSCLE_BUILDING = "muscle_building"     # 增肌
    HEALTH_MAINTENANCE = "health_maintenance" # 健康维持
    DISEASE_MANAGEMENT = "disease_management" # 疾病管理
    SPORTS_PERFORMANCE = "sports_performance" # 运动表现

class MealType(str, Enum):
    """餐次类型"""
    BREAKFAST = "breakfast"                 # 早餐
    MORNING_SNACK = "morning_snack"         # 上午加餐
    LUNCH = "lunch"                         # 午餐
    AFTERNOON_SNACK = "afternoon_snack"     # 下午加餐
    DINNER = "dinner"                       # 晚餐
    EVENING_SNACK = "evening_snack"         # 晚间加餐

@dataclass
class Nutrient:
    """营养素信息"""
    nutrient_id: str
    name: str
    nutrient_type: NutrientType
    unit: str
    rda_adult_male: Optional[float] = None
    rda_adult_female: Optional[float] = None
    upper_limit: Optional[float] = None
    functions: List[str] = field(default_factory=list)
    food_sources: List[str] = field(default_factory=list)

@dataclass
class Food:
    """食物信息"""
    food_id: str
    name: str
    category: FoodCategory
    energy_kcal: float = 0.0
    protein: float = 0.0
    carbohydrate: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    nutrients: Dict[str, float] = field(default_factory=dict)
    tcm_nature: Optional[TCMFoodNature] = None
    tcm_flavor: List[TCMFoodFlavor] = field(default_factory=list)
    tcm_effects: List[str] = field(default_factory=list)

@dataclass
class NutritionalAssessment:
    """营养评估"""
    user_id: str
    assessment_date: datetime
    age: int
    gender: str
    height: float
    weight: float
    bmi: float = field(init=False)
    activity_level: str = "moderate"
    nutrient_intake: Dict[str, float] = field(default_factory=dict)
    nutrient_status: Dict[str, NutritionalStatus] = field(default_factory=dict)
    overall_status: NutritionalStatus = NutritionalStatus.ADEQUATE
    priority_nutrients: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    tcm_constitution: Optional[str] = None
    
    def __post_init__(self):
        self.bmi = self.weight / ((self.height / 100) ** 2)

@dataclass
class MealPlan:
    """膳食计划"""
    plan_id: str
    user_id: str
    plan_name: str
    description: str
    start_date: date
    end_date: Optional[date] = None
    dietary_goals: List[DietaryGoal] = field(default_factory=list)
    daily_energy_target: float = 0.0
    daily_meals: Dict[MealType, Dict[str, Any]] = field(default_factory=dict)
    food_list: List[Dict[str, Any]] = field(default_factory=list)
    tcm_food_therapy: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    created_date: datetime = field(default_factory=datetime.now)

@dataclass
class FoodIntake:
    """食物摄入记录"""
    user_id: str
    date: date
    meal_type: MealType
    foods: List[Dict[str, Any]] = field(default_factory=list)
    total_energy: float = 0.0
    total_nutrients: Dict[str, float] = field(default_factory=dict)
    meal_time: Optional[time] = None
    notes: Optional[str] = None
    recorded_at: datetime = field(default_factory=datetime.now)

@dataclass
class NutritionGoal:
    """营养目标"""
    user_id: str
    goal_type: str
    target_value: float
    current_value: float
    unit: str
    target_date: date
    progress_percentage: float = 0.0
    is_achieved: bool = False
    strategies: List[str] = field(default_factory=list)
    created_date: date = field(default_factory=date.today)

class NutritionDatabase:
    """营养数据库"""
    
    def __init__(self):
        self.foods = {}
        self.nutrients = {}
        self.recipes = {}
    
    async def initialize(self):
        """初始化数据库"""
        # 加载基础营养数据
        await self._load_basic_nutrition_data()
    
    async def _load_basic_nutrition_data(self):
        """加载基础营养数据"""
        # 示例数据，实际应从数据库加载
        self.foods = {
            "rice": {"energy_kcal": 130, "protein": 2.7, "carbohydrate": 28, "fat": 0.3},
            "chicken": {"energy_kcal": 165, "protein": 31, "carbohydrate": 0, "fat": 3.6},
            "broccoli": {"energy_kcal": 34, "protein": 2.8, "carbohydrate": 7, "fat": 0.4}
        }

class NutritionalAssessor:
    """营养评估器"""
    
    def __init__(self):
        self.assessment_algorithms = {}
    
    async def initialize(self):
        """初始化评估器"""
        pass
    
    async def conduct_nutritional_assessment(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        dietary_records: List[Any]
    ) -> NutritionalAssessment:
        """进行营养评估"""
        
        # 计算BMI
        height_m = user_data["height"] / 100
        weight = user_data["weight"]
        bmi = weight / (height_m ** 2)
        
        # 确定营养状态
        if bmi < 18.5:
            status = NutritionalStatus.UNDERWEIGHT
        elif bmi < 25:
            status = NutritionalStatus.NORMAL
        elif bmi < 30:
            status = NutritionalStatus.OVERWEIGHT
        else:
            status = NutritionalStatus.OBESE
        
        # 生成建议
        recommendations = [
            "保持均衡饮食",
            "适量运动",
            "定期监测体重"
        ]
        
        return NutritionalAssessment(
            user_id=user_id,
            assessment_date=date.today(),
            overall_status=status,
            bmi=bmi,
            priority_nutrients=["protein", "fiber", "vitamin_c"],
            recommendations=recommendations
        )

class MealPlanGenerator:
    """膳食计划生成器"""
    
    def __init__(self):
        self.meal_templates = {}
    
    async def initialize(self):
        """初始化生成器"""
        pass
    
    async def generate_meal_plan(
        self,
        user_id: str,
        nutritional_assessment: NutritionalAssessment,
        dietary_goals: List[DietaryGoal],
        user_preferences: Dict[str, Any],
        duration_days: int
    ) -> MealPlan:
        """生成膳食计划"""
        
        plan_id = f"plan_{user_id}_{int(datetime.now().timestamp())}"
        
        # 生成每日膳食
        daily_meals = []
        for day in range(duration_days):
            daily_meal = {
                "day": day + 1,
                "breakfast": ["燕麦粥", "鸡蛋", "牛奶"],
                "lunch": ["米饭", "鸡胸肉", "西兰花"],
                "dinner": ["小米粥", "鱼肉", "青菜"],
                "snacks": ["苹果", "坚果"]
            }
            daily_meals.append(daily_meal)
        
        return MealPlan(
            plan_id=plan_id,
            user_id=user_id,
            plan_name=f"{user_id}的个性化膳食计划",
            dietary_goals=dietary_goals,
            duration_days=duration_days,
            daily_meals=daily_meals,
            nutritional_targets={
                "energy": 2000,
                "protein": 60,
                "carbohydrate": 250,
                "fat": 67
            },
            tcm_food_therapy={
                "constitution_type": "平和质",
                "seasonal_foods": [],
                "therapeutic_foods": []
            }
        )

class IntelligentNutritionEngine:
    """智能营养管理引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(__name__)
        
        # 核心组件
        self.nutrition_db: Optional[NutritionDatabase] = None
        self.assessor: Optional[NutritionalAssessor] = None
        self.meal_planner: Optional[MealPlanGenerator] = None
        
        # 数据存储（实际应用中应使用数据库）
        self.assessments: Dict[str, NutritionalAssessment] = {}
        self.meal_plans: Dict[str, MealPlan] = {}
        self.food_intakes: Dict[str, List[FoodIntake]] = defaultdict(list)
        self.nutrition_goals: Dict[str, List[NutritionGoal]] = defaultdict(list)
        
        # 性能优化
        self._assessment_cache = {}
        self._cache_ttl = config.get("cache_ttl", 3600)  # 缓存1小时
        self._max_cache_size = config.get("max_cache_size", 1000)
        
        # 健康状态
        self._is_healthy = True
        self._last_error: Optional[Exception] = None
        self._error_count = 0
        self._max_errors = config.get("max_errors", 10)
        
        # 引擎协同
        self._data_bus = None
        self._engine_manager = None
        
        # 指标收集
        if self.metrics_collector:
            self.metrics_collector.register_counter(
                "nutrition_assessments_total",
                "Total number of nutrition assessments conducted"
            )
            self.metrics_collector.register_counter(
                "meal_plans_generated_total",
                "Total number of meal plans generated"
            )
            self.metrics_collector.register_counter(
                "nutrition_engine_errors_total",
                "Total number of nutrition engine errors"
            )
            self.metrics_collector.register_histogram(
                "nutrition_assessment_duration_seconds",
                "Duration of nutrition assessments in seconds"
            )
    
    async def initialize(self):
        """初始化引擎"""
        try:
            await self._initialize_components()
            self._is_healthy = True
            self._error_count = 0
            self.logger.info("智能营养管理引擎初始化完成")
        except Exception as e:
            self._is_healthy = False
            self._last_error = e
            self._error_count += 1
            self.logger.error(f"营养引擎初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 清理缓存
            self._assessment_cache.clear()
            
            # 保存重要数据（实际应用中保存到数据库）
            await self._save_critical_data()
            
            self.logger.info("智能营养管理引擎清理完成")
        except Exception as e:
            self.logger.error(f"营养引擎清理失败: {e}")
    
    async def _initialize_components(self):
        """初始化组件"""
        try:
            self.nutrition_db = NutritionDatabase()
            self.assessor = NutritionalAssessor()
            self.meal_planner = MealPlanGenerator()
            
            # 初始化组件
            await self.nutrition_db.initialize()
            await self.assessor.initialize()
            await self.meal_planner.initialize()
            
        except Exception as e:
            self.logger.error(f"组件初始化失败: {e}")
            raise
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            # 检查核心组件
            if not all([self.nutrition_db, self.assessor, self.meal_planner]):
                return False
            
            # 检查错误计数
            if self._error_count >= self._max_errors:
                return False
            
            # 执行简单的功能测试
            test_user_data = {
                "age": 30,
                "gender": "female",
                "height": 165.0,
                "weight": 60.0
            }
            
            # 测试营养评估功能
            assessment = await self.assessor.conduct_nutritional_assessment(
                user_id="health_check_test",
                user_data=test_user_data,
                dietary_records=[]
            )
            
            if not assessment:
                return False
            
            self._is_healthy = True
            return True
            
        except Exception as e:
            self._is_healthy = False
            self._last_error = e
            self._error_count += 1
            self.logger.error(f"营养引擎健康检查失败: {e}")
            return False
    
    def set_data_bus(self, data_bus):
        """设置数据总线"""
        self._data_bus = data_bus
        
        # 订阅相关数据
        if data_bus:
            data_bus.subscribe("user_health_data", self._on_health_data_updated)
            data_bus.subscribe("environment_data", self._on_environment_data_updated)
    
    def set_engine_manager(self, engine_manager):
        """设置引擎管理器"""
        self._engine_manager = engine_manager
    
    async def _on_health_data_updated(self, topic: str, data: Any):
        """处理健康数据更新"""
        try:
            if isinstance(data, dict) and "user_id" in data:
                user_id = data["user_id"]
                
                # 如果有该用户的营养评估，更新相关建议
                if user_id in self.assessments:
                    await self._update_nutrition_recommendations(user_id, data)
                    
        except Exception as e:
            self.logger.error(f"处理健康数据更新失败: {e}")
    
    async def _on_environment_data_updated(self, topic: str, data: Any):
        """处理环境数据更新"""
        try:
            if isinstance(data, dict) and "location" in data:
                # 根据环境数据调整营养建议
                await self._adjust_nutrition_for_environment(data)
                
        except Exception as e:
            self.logger.error(f"处理环境数据更新失败: {e}")
    
    async def _update_nutrition_recommendations(self, user_id: str, health_data: Dict[str, Any]):
        """更新营养建议"""
        try:
            assessment = self.assessments.get(user_id)
            if not assessment:
                return
            
            # 根据新的健康数据更新建议
            new_recommendations = []
            
            # 血压相关建议
            if "blood_pressure" in health_data:
                bp = health_data["blood_pressure"]
                if bp.get("systolic", 0) > 140 or bp.get("diastolic", 0) > 90:
                    new_recommendations.extend([
                        "减少钠盐摄入，每日不超过6克",
                        "增加钾元素摄入，多食用香蕉、橙子等",
                        "控制饱和脂肪摄入"
                    ])
            
            # 血糖相关建议
            if "blood_glucose" in health_data:
                glucose = health_data["blood_glucose"]
                if glucose > 7.0:  # 空腹血糖
                    new_recommendations.extend([
                        "控制碳水化合物摄入，选择低GI食物",
                        "增加膳食纤维摄入",
                        "少食多餐，避免血糖波动"
                    ])
            
            # 更新评估建议
            if new_recommendations:
                assessment.recommendations.extend(new_recommendations)
                assessment.recommendations = list(set(assessment.recommendations))  # 去重
                
                # 发布更新通知
                if self._data_bus:
                    await self._data_bus.publish_data(
                        f"nutrition_recommendations_updated:{user_id}",
                        {
                            "user_id": user_id,
                            "recommendations": new_recommendations,
                            "updated_at": datetime.now().isoformat()
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"更新营养建议失败: {e}")
    
    async def _adjust_nutrition_for_environment(self, environment_data: Dict[str, Any]):
        """根据环境调整营养建议"""
        try:
            # 根据季节调整
            season = environment_data.get("season")
            if season:
                seasonal_adjustments = {
                    "spring": ["多食绿色蔬菜", "适量酸味食物", "疏肝理气"],
                    "summer": ["清淡饮食", "多食苦味", "清热解暑"],
                    "autumn": ["润燥食物", "白色食物", "养阴润肺"],
                    "winter": ["温补食物", "黑色食物", "温阳补肾"]
                }
                
                adjustments = seasonal_adjustments.get(season, [])
                if adjustments and self._data_bus:
                    await self._data_bus.publish_data(
                        "seasonal_nutrition_adjustments",
                        {
                            "season": season,
                            "adjustments": adjustments,
                            "updated_at": datetime.now().isoformat()
                        }
                    )
            
            # 根据空气质量调整
            air_quality = environment_data.get("air_quality_level")
            if air_quality in ["unhealthy", "hazardous"]:
                pollution_adjustments = [
                    "增加抗氧化食物摄入",
                    "多食用富含维生素C的食物",
                    "增加绿茶等清肺食物"
                ]
                
                if self._data_bus:
                    await self._data_bus.publish_data(
                        "pollution_nutrition_adjustments",
                        {
                            "air_quality": air_quality,
                            "adjustments": pollution_adjustments,
                            "updated_at": datetime.now().isoformat()
                        }
                    )
                    
        except Exception as e:
            self.logger.error(f"根据环境调整营养建议失败: {e}")
    
    async def _save_critical_data(self):
        """保存关键数据"""
        try:
            # 实际应用中应保存到数据库
            critical_data = {
                "assessments_count": len(self.assessments),
                "meal_plans_count": len(self.meal_plans),
                "total_users": len(set(list(self.assessments.keys()) + list(self.meal_plans.keys()))),
                "last_save": datetime.now().isoformat()
            }
            
            self.logger.info(f"保存关键数据: {critical_data}")
            
        except Exception as e:
            self.logger.error(f"保存关键数据失败: {e}")
    
    @trace_operation("nutrition_engine.conduct_assessment", SpanKind.INTERNAL)
    async def conduct_nutritional_assessment(
        self,
        user_id: str,
        user_data: Dict[str, Any],
        dietary_records: List[Dict[str, Any]] = None
    ) -> NutritionalAssessment:
        """进行营养评估"""
        
        start_time = datetime.now()
        
        try:
            # 检查缓存
            cache_key = f"assessment_{user_id}_{hash(str(user_data))}"
            if cache_key in self._assessment_cache:
                cached_result = self._assessment_cache[cache_key]
                if (datetime.now() - cached_result["timestamp"]).seconds < self._cache_ttl:
                    self.logger.info(f"从缓存返回用户 {user_id} 的营养评估")
                    return cached_result["assessment"]
            
            # 转换膳食记录格式
            food_intakes = []
            if dietary_records:
                for record in dietary_records:
                    intake = FoodIntake(
                        user_id=user_id,
                        date=record.get("date", date.today()),
                        meal_type=MealType(record.get("meal_type", "lunch")),
                        foods=record.get("foods", []),
                        total_energy=record.get("total_energy", 0.0),
                        total_nutrients=record.get("total_nutrients", {})
                    )
                    food_intakes.append(intake)
            
            # 进行营养评估
            assessment = await self.assessor.conduct_nutritional_assessment(
                user_id=user_id,
                user_data=user_data,
                dietary_records=food_intakes
            )
            
            # 保存评估结果
            self.assessments[user_id] = assessment
            
            # 缓存结果
            if len(self._assessment_cache) >= self._max_cache_size:
                # 清理最旧的缓存
                oldest_key = min(self._assessment_cache.keys(), 
                               key=lambda k: self._assessment_cache[k]["timestamp"])
                del self._assessment_cache[oldest_key]
            
            self._assessment_cache[cache_key] = {
                "assessment": assessment,
                "timestamp": datetime.now()
            }
            
            # 记录指标
            processing_time = (datetime.now() - start_time).total_seconds()
            if self.metrics_collector:
                self.metrics_collector.increment_counter("nutrition_assessments_total")
                self.metrics_collector.record_histogram(
                    "nutrition_assessment_duration_seconds",
                    processing_time
                )
            
            # 发布评估完成事件
            if self._data_bus:
                await self._data_bus.publish_data(
                    f"nutrition_assessment_completed:{user_id}",
                    {
                        "user_id": user_id,
                        "assessment_id": f"assess_{user_id}_{int(start_time.timestamp())}",
                        "overall_status": assessment.overall_status.value,
                        "bmi": assessment.bmi,
                        "priority_nutrients": assessment.priority_nutrients,
                        "completed_at": datetime.now().isoformat()
                    }
                )
            
            self.logger.info(f"用户 {user_id} 营养评估完成，耗时 {processing_time:.2f}秒")
            return assessment
            
        except Exception as e:
            self._error_count += 1
            self._last_error = e
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("nutrition_engine_errors_total")
            
            self.logger.error(f"营养评估失败: {e}")
            raise
    
    @trace_operation("nutrition_engine.generate_meal_plan", SpanKind.INTERNAL)
    async def generate_meal_plan(
        self,
        user_id: str,
        dietary_goals: List[str],
        user_preferences: Dict[str, Any] = None,
        duration_days: int = 7
    ) -> MealPlan:
        """生成膳食计划"""
        
        start_time = datetime.now()
        
        try:
            # 获取最新的营养评估
            if user_id not in self.assessments:
                raise ValueError(f"用户 {user_id} 尚未进行营养评估")
            
            assessment = self.assessments[user_id]
            
            # 转换膳食目标
            goal_enums = []
            for goal in dietary_goals:
                try:
                    goal_enums.append(DietaryGoal(goal))
                except ValueError:
                    self.logger.warning(f"未知的膳食目标: {goal}")
            
            if not goal_enums:
                goal_enums = [DietaryGoal.HEALTH_MAINTENANCE]
            
            # 获取环境数据进行调整
            environment_adjustments = {}
            if self._data_bus:
                env_data = await self._data_bus.get_data("current_environment")
                if env_data:
                    environment_adjustments = await self._get_environment_adjustments(env_data)
            
            # 生成膳食计划
            meal_plan = await self.meal_planner.generate_meal_plan(
                user_id=user_id,
                nutritional_assessment=assessment,
                dietary_goals=goal_enums,
                user_preferences=user_preferences or {},
                duration_days=duration_days
            )
            
            # 应用环境调整
            if environment_adjustments:
                await self._apply_environment_adjustments(meal_plan, environment_adjustments)
            
            # 保存膳食计划
            self.meal_plans[meal_plan.plan_id] = meal_plan
            
            # 记录指标
            processing_time = (datetime.now() - start_time).total_seconds()
            if self.metrics_collector:
                self.metrics_collector.increment_counter("meal_plans_generated_total")
            
            # 发布膳食计划生成事件
            if self._data_bus:
                await self._data_bus.publish_data(
                    f"meal_plan_generated:{user_id}",
                    {
                        "user_id": user_id,
                        "plan_id": meal_plan.plan_id,
                        "plan_name": meal_plan.plan_name,
                        "duration_days": duration_days,
                        "dietary_goals": [goal.value for goal in goal_enums],
                        "generated_at": datetime.now().isoformat()
                    }
                )
            
            self.logger.info(f"用户 {user_id} 膳食计划生成完成，耗时 {processing_time:.2f}秒")
            return meal_plan
            
        except Exception as e:
            self._error_count += 1
            self._last_error = e
            
            if self.metrics_collector:
                self.metrics_collector.increment_counter("nutrition_engine_errors_total")
            
            self.logger.error(f"膳食计划生成失败: {e}")
            raise
    
    async def _get_environment_adjustments(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """获取环境调整建议"""
        adjustments = {}
        
        # 季节调整
        season = env_data.get("season")
        if season:
            seasonal_foods = {
                "spring": ["韭菜", "春笋", "菠菜", "芹菜"],
                "summer": ["苦瓜", "冬瓜", "丝瓜", "黄瓜"],
                "autumn": ["梨", "柿子", "银耳", "百合"],
                "winter": ["萝卜", "白菜", "山药", "红枣"]
            }
            adjustments["seasonal_foods"] = seasonal_foods.get(season, [])
        
        # 空气质量调整
        air_quality = env_data.get("air_quality_level")
        if air_quality in ["unhealthy", "hazardous"]:
            adjustments["anti_pollution_foods"] = [
                "绿茶", "胡萝卜", "西兰花", "菠菜", "蓝莓"
            ]
        
        return adjustments
    
    async def _apply_environment_adjustments(
        self, 
        meal_plan: MealPlan, 
        adjustments: Dict[str, Any]
    ):
        """应用环境调整"""
        try:
            # 添加季节性食物建议
            if "seasonal_foods" in adjustments:
                meal_plan.tcm_food_therapy["seasonal_recommendations"] = adjustments["seasonal_foods"]
            
            # 添加抗污染食物建议
            if "anti_pollution_foods" in adjustments:
                meal_plan.tcm_food_therapy["anti_pollution_foods"] = adjustments["anti_pollution_foods"]
            
        except Exception as e:
            self.logger.error(f"应用环境调整失败: {e}")
    
    async def get_collaborative_recommendations(self, user_id: str) -> Dict[str, Any]:
        """获取协同推荐"""
        try:
            recommendations = {
                "nutrition": [],
                "environment": [],
                "exercise": [],
                "lifestyle": []
            }
            
            # 获取营养评估
            assessment = self.assessments.get(user_id)
            if assessment:
                recommendations["nutrition"] = assessment.recommendations
            
            # 从其他引擎获取建议
            if self._engine_manager:
                # 获取环境健康建议
                try:
                    env_response = await self._engine_manager.execute_request(
                        engine_type="environment_health",
                        method_name="get_health_recommendations",
                        user_id=user_id
                    )
                    if env_response.success:
                        recommendations["environment"] = env_response.result.get("recommendations", [])
                except Exception as e:
                    self.logger.warning(f"获取环境健康建议失败: {e}")
                
                # 获取运动建议（如果有运动引擎）
                try:
                    exercise_response = await self._engine_manager.execute_request(
                        engine_type="health_monitoring",
                        method_name="get_exercise_recommendations",
                        user_id=user_id,
                        capability="recommendation"
                    )
                    if exercise_response.success:
                        recommendations["exercise"] = exercise_response.result.get("recommendations", [])
                except Exception as e:
                    self.logger.warning(f"获取运动建议失败: {e}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"获取协同推荐失败: {e}")
            return {"error": str(e)}

def initialize_nutrition_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentNutritionEngine:
    """初始化智能营养管理引擎"""
    
    engine = IntelligentNutritionEngine(config, metrics_collector)
    return engine

# 全局引擎实例
_nutrition_engine: Optional[IntelligentNutritionEngine] = None

def get_nutrition_engine() -> Optional[IntelligentNutritionEngine]:
    """获取营养引擎实例"""
    return _nutrition_engine