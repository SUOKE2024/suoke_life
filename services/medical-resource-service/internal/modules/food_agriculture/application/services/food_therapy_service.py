"""
食疗服务应用层
专门处理食疗推荐和管理的业务逻辑
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from ...domain.models.food_models import FoodItem, FoodCombination, NutritionalInfo
from ...domain.models.therapy_models import FoodTherapyPlan, TherapyRecommendation
from ...domain.enums.food_enums import FoodCategory, FoodNature, HealthBenefit
from ...domain.enums.season_enums import SeasonType, SeasonalHealthFocus
from ....infrastructure.repositories.food_repository import FoodRepository
from ....infrastructure.repositories.therapy_repository import TherapyRepository
from .....domain.models import ConstitutionType

logger = logging.getLogger(__name__)


class FoodTherapyService:
    """
    食疗服务
    
    负责食疗方案的推荐、制定和管理
    """
    
    def __init__(
        self,
        food_repository: FoodRepository,
        therapy_repository: TherapyRepository
    ):
        self.food_repository = food_repository
        self.therapy_repository = therapy_repository
        
        # 体质与食物性质映射
        self.constitution_food_nature_mapping = {
            ConstitutionType.YANG_DEFICIENCY: [FoodNature.WARM, FoodNature.HOT],
            ConstitutionType.YIN_DEFICIENCY: [FoodNature.COOL, FoodNature.NEUTRAL],
            ConstitutionType.QI_DEFICIENCY: [FoodNature.WARM, FoodNature.NEUTRAL],
            ConstitutionType.BLOOD_STASIS: [FoodNature.WARM, FoodNature.NEUTRAL],
            ConstitutionType.PHLEGM_DAMPNESS: [FoodNature.WARM, FoodNature.NEUTRAL],
            ConstitutionType.DAMP_HEAT: [FoodNature.COOL, FoodNature.COLD],
            ConstitutionType.QI_STAGNATION: [FoodNature.NEUTRAL, FoodNature.WARM],
            ConstitutionType.SPECIAL_CONSTITUTION: [FoodNature.NEUTRAL],
            ConstitutionType.BALANCED: [FoodNature.NEUTRAL]
        }
    
    async def recommend_food_therapy(
        self,
        user_id: str,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        preferences: Dict[str, Any] = None,
        allergies: List[str] = None,
        duration_days: int = 30
    ) -> TherapyRecommendation:
        """
        推荐食疗方案
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            symptoms: 症状列表
            preferences: 饮食偏好
            allergies: 过敏食物
            duration_days: 疗程天数
            
        Returns:
            食疗推荐结果
        """
        try:
            logger.info(f"为用户 {user_id} 推荐食疗方案，体质：{constitution_type.value}")
            
            # 获取当前季节
            current_season = self._get_current_season()
            
            # 根据体质和症状筛选适合的食物
            suitable_foods = await self._find_suitable_foods(
                constitution_type, symptoms, current_season, allergies
            )
            
            # 生成食疗方案
            therapy_plan = await self._create_therapy_plan(
                user_id, constitution_type, symptoms, suitable_foods, 
                duration_days, preferences
            )
            
            # 生成推荐说明
            recommendation = TherapyRecommendation(
                recommendation_id=f"therapy_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                constitution_type=constitution_type,
                target_symptoms=symptoms,
                therapy_plan=therapy_plan,
                confidence_score=self._calculate_confidence_score(
                    constitution_type, symptoms, suitable_foods
                ),
                reasoning=self._generate_reasoning(
                    constitution_type, symptoms, current_season
                ),
                precautions=self._generate_precautions(constitution_type, symptoms),
                follow_up_schedule=self._generate_follow_up_schedule(duration_days)
            )
            
            # 保存推荐记录
            await self.therapy_repository.save_recommendation(recommendation)
            
            logger.info(f"成功为用户 {user_id} 生成食疗推荐")
            return recommendation
            
        except Exception as e:
            logger.error(f"食疗推荐失败: {str(e)}")
            raise
    
    async def _find_suitable_foods(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        season: SeasonType,
        allergies: List[str] = None
    ) -> List[FoodItem]:
        """查找适合的食物"""
        
        # 获取适合的食物性质
        suitable_natures = self.constitution_food_nature_mapping.get(
            constitution_type, [FoodNature.NEUTRAL]
        )
        
        # 根据症状获取需要的健康功效
        required_benefits = self._map_symptoms_to_benefits(symptoms)
        
        # 查询食物
        foods = await self.food_repository.find_foods_by_criteria(
            natures=suitable_natures,
            health_benefits=required_benefits,
            season=season,
            exclude_allergens=allergies
        )
        
        # 按适合度排序
        sorted_foods = self._sort_foods_by_suitability(
            foods, constitution_type, symptoms, season
        )
        
        return sorted_foods[:20]  # 返回前20个最适合的食物
    
    def _map_symptoms_to_benefits(self, symptoms: List[str]) -> List[HealthBenefit]:
        """将症状映射到健康功效"""
        symptom_benefit_mapping = {
            "疲劳": [HealthBenefit.ENERGY_BOOST],
            "失眠": [HealthBenefit.SLEEP_AID],
            "消化不良": [HealthBenefit.DIGESTIVE_AID],
            "免疫力低": [HealthBenefit.IMMUNE_BOOST],
            "压力大": [HealthBenefit.STRESS_RELIEF],
            "血糖高": [HealthBenefit.BLOOD_SUGAR_CONTROL],
            "胆固醇高": [HealthBenefit.CHOLESTEROL_CONTROL],
            "心脏问题": [HealthBenefit.HEART_HEALTH],
            "记忆力差": [HealthBenefit.BRAIN_HEALTH],
            "骨质疏松": [HealthBenefit.BONE_HEALTH],
            "视力问题": [HealthBenefit.EYE_HEALTH],
            "皮肤问题": [HealthBenefit.SKIN_HEALTH],
            "体重问题": [HealthBenefit.WEIGHT_MANAGEMENT]
        }
        
        benefits = []
        for symptom in symptoms:
            if symptom in symptom_benefit_mapping:
                benefits.extend(symptom_benefit_mapping[symptom])
        
        return list(set(benefits))  # 去重
    
    def _sort_foods_by_suitability(
        self,
        foods: List[FoodItem],
        constitution_type: ConstitutionType,
        symptoms: List[str],
        season: SeasonType
    ) -> List[FoodItem]:
        """按适合度排序食物"""
        
        def calculate_suitability_score(food: FoodItem) -> float:
            score = 0.0
            
            # 体质匹配度 (40%)
            suitable_natures = self.constitution_food_nature_mapping.get(
                constitution_type, []
            )
            if food.nature in suitable_natures:
                score += 40
            
            # 症状匹配度 (30%)
            required_benefits = self._map_symptoms_to_benefits(symptoms)
            matching_benefits = set(food.health_benefits) & set(required_benefits)
            if required_benefits:
                score += 30 * (len(matching_benefits) / len(required_benefits))
            
            # 季节适应性 (20%)
            if food.is_available_in_season(season):
                score += 20
            
            # 营养密度 (10%)
            nutrition_score = self._calculate_nutrition_score(food.nutritional_info)
            score += 10 * (nutrition_score / 100)
            
            return score
        
        return sorted(foods, key=calculate_suitability_score, reverse=True)
    
    def _calculate_nutrition_score(self, nutrition: NutritionalInfo) -> float:
        """计算营养评分"""
        score = 0.0
        
        # 蛋白质含量
        if nutrition.protein > 20:
            score += 25
        elif nutrition.protein > 10:
            score += 15
        elif nutrition.protein > 5:
            score += 10
        
        # 纤维含量
        if nutrition.fiber > 10:
            score += 25
        elif nutrition.fiber > 5:
            score += 15
        elif nutrition.fiber > 2:
            score += 10
        
        # 维生素种类
        vitamin_count = len(nutrition.vitamins)
        score += min(25, vitamin_count * 3)
        
        # 矿物质种类
        mineral_count = len(nutrition.minerals)
        score += min(25, mineral_count * 3)
        
        return min(100, score)
    
    async def _create_therapy_plan(
        self,
        user_id: str,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        foods: List[FoodItem],
        duration_days: int,
        preferences: Dict[str, Any] = None
    ) -> FoodTherapyPlan:
        """创建食疗方案"""
        
        # 生成每日餐食安排
        daily_meals = self._generate_daily_meals(foods, preferences)
        
        # 生成制作说明
        preparation_instructions = self._generate_preparation_instructions(foods)
        
        # 生成预期效果
        expected_benefits = self._generate_expected_benefits(constitution_type, symptoms)
        
        # 生成注意事项
        precautions = self._generate_therapy_precautions(constitution_type, foods)
        
        # 生成进展指标
        progress_indicators = self._generate_progress_indicators(symptoms)
        
        therapy_plan = FoodTherapyPlan(
            plan_id=f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{constitution_type.value}体质食疗方案",
            target_constitution=constitution_type,
            target_symptoms=symptoms,
            duration_days=duration_days,
            daily_meals=daily_meals,
            preparation_instructions=preparation_instructions,
            expected_benefits=expected_benefits,
            precautions=precautions,
            progress_indicators=progress_indicators
        )
        
        return therapy_plan
    
    def _generate_daily_meals(
        self,
        foods: List[FoodItem],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, List[str]]:
        """生成每日餐食安排"""
        
        # 按食物类别分组
        categorized_foods = {}
        for food in foods:
            category = food.category
            if category not in categorized_foods:
                categorized_foods[category] = []
            categorized_foods[category].append(food.name)
        
        # 生成三餐安排
        daily_meals = {
            "早餐": [],
            "午餐": [],
            "晚餐": [],
            "加餐": []
        }
        
        # 早餐：谷物 + 蛋白质 + 水果
        if FoodCategory.GRAINS in categorized_foods:
            daily_meals["早餐"].extend(categorized_foods[FoodCategory.GRAINS][:2])
        if FoodCategory.PROTEINS in categorized_foods:
            daily_meals["早餐"].extend(categorized_foods[FoodCategory.PROTEINS][:1])
        if FoodCategory.FRUITS in categorized_foods:
            daily_meals["早餐"].extend(categorized_foods[FoodCategory.FRUITS][:1])
        
        # 午餐：蔬菜 + 蛋白质 + 谷物
        if FoodCategory.VEGETABLES in categorized_foods:
            daily_meals["午餐"].extend(categorized_foods[FoodCategory.VEGETABLES][:3])
        if FoodCategory.PROTEINS in categorized_foods:
            daily_meals["午餐"].extend(categorized_foods[FoodCategory.PROTEINS][1:3])
        if FoodCategory.GRAINS in categorized_foods:
            daily_meals["午餐"].extend(categorized_foods[FoodCategory.GRAINS][2:3])
        
        # 晚餐：蔬菜 + 药食同源
        if FoodCategory.VEGETABLES in categorized_foods:
            daily_meals["晚餐"].extend(categorized_foods[FoodCategory.VEGETABLES][3:5])
        if FoodCategory.HERBS in categorized_foods:
            daily_meals["晚餐"].extend(categorized_foods[FoodCategory.HERBS][:2])
        
        # 加餐：坚果 + 饮品
        if FoodCategory.NUTS_SEEDS in categorized_foods:
            daily_meals["加餐"].extend(categorized_foods[FoodCategory.NUTS_SEEDS][:1])
        if FoodCategory.BEVERAGES in categorized_foods:
            daily_meals["加餐"].extend(categorized_foods[FoodCategory.BEVERAGES][:1])
        
        return daily_meals
    
    def _generate_preparation_instructions(self, foods: List[FoodItem]) -> List[str]:
        """生成制作说明"""
        instructions = [
            "1. 选择新鲜、优质的食材",
            "2. 根据食物性质选择合适的烹饪方法",
            "3. 注意食物搭配的协调性",
            "4. 控制烹饪时间，保持营养成分",
            "5. 适量调味，避免过咸过甜"
        ]
        
        # 根据食物特点添加特殊说明
        for food in foods[:5]:  # 只处理前5个主要食物
            if food.nature == FoodNature.COLD:
                instructions.append(f"• {food.name}性寒，建议温热食用")
            elif food.nature == FoodNature.HOT:
                instructions.append(f"• {food.name}性热，建议适量食用")
        
        return instructions
    
    def _generate_expected_benefits(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str]
    ) -> List[str]:
        """生成预期效果"""
        benefits = []
        
        # 根据体质类型添加预期效果
        constitution_benefits = {
            ConstitutionType.YANG_DEFICIENCY: ["改善畏寒怕冷", "增强体力", "提升阳气"],
            ConstitutionType.YIN_DEFICIENCY: ["滋阴润燥", "改善潮热", "安神助眠"],
            ConstitutionType.QI_DEFICIENCY: ["补气健脾", "增强体力", "改善疲劳"],
            ConstitutionType.BLOOD_STASIS: ["活血化瘀", "改善循环", "缓解疼痛"],
            ConstitutionType.PHLEGM_DAMPNESS: ["化痰除湿", "健脾利水", "减轻体重"],
            ConstitutionType.DAMP_HEAT: ["清热利湿", "改善口苦", "调节代谢"],
            ConstitutionType.QI_STAGNATION: ["疏肝理气", "改善情绪", "缓解压力"],
            ConstitutionType.SPECIAL_CONSTITUTION: ["调节过敏", "增强适应性", "改善体质"],
            ConstitutionType.BALANCED: ["维持平衡", "预防疾病", "增强体质"]
        }
        
        benefits.extend(constitution_benefits.get(constitution_type, []))
        
        # 根据症状添加预期效果
        for symptom in symptoms:
            if "疲劳" in symptom:
                benefits.append("缓解疲劳感")
            elif "失眠" in symptom:
                benefits.append("改善睡眠质量")
            elif "消化" in symptom:
                benefits.append("促进消化功能")
        
        return list(set(benefits))  # 去重
    
    def _generate_therapy_precautions(
        self,
        constitution_type: ConstitutionType,
        foods: List[FoodItem]
    ) -> List[str]:
        """生成食疗注意事项"""
        precautions = [
            "请在专业医师指导下进行食疗",
            "如有不适症状，请及时停止并咨询医师",
            "保持规律的作息和适量运动",
            "注意观察身体反应，记录变化"
        ]
        
        # 根据体质添加特殊注意事项
        if constitution_type == ConstitutionType.YANG_DEFICIENCY:
            precautions.append("避免生冷食物，注意保暖")
        elif constitution_type == ConstitutionType.YIN_DEFICIENCY:
            precautions.append("避免辛辣燥热食物，多补充水分")
        elif constitution_type == ConstitutionType.DAMP_HEAT:
            precautions.append("避免油腻甜腻食物，保持清淡饮食")
        
        # 根据食物禁忌添加注意事项
        for food in foods:
            if food.contraindications:
                precautions.append(f"注意{food.name}的使用禁忌")
        
        return precautions
    
    def _generate_progress_indicators(self, symptoms: List[str]) -> List[str]:
        """生成进展指标"""
        indicators = [
            "整体精神状态改善",
            "食欲和消化功能正常",
            "睡眠质量提升",
            "体力和耐力增强"
        ]
        
        # 根据症状添加特定指标
        for symptom in symptoms:
            if "疲劳" in symptom:
                indicators.append("疲劳感明显减轻")
            elif "失眠" in symptom:
                indicators.append("入睡时间缩短，睡眠深度改善")
            elif "消化" in symptom:
                indicators.append("消化不良症状缓解")
        
        return indicators
    
    def _calculate_confidence_score(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        foods: List[FoodItem]
    ) -> float:
        """计算推荐置信度"""
        score = 0.0
        
        # 体质匹配度
        if constitution_type in self.constitution_food_nature_mapping:
            score += 30
        
        # 症状覆盖度
        required_benefits = self._map_symptoms_to_benefits(symptoms)
        if required_benefits:
            covered_benefits = set()
            for food in foods:
                covered_benefits.update(food.health_benefits)
            coverage = len(set(required_benefits) & covered_benefits) / len(required_benefits)
            score += 40 * coverage
        
        # 食物数量和质量
        if len(foods) >= 10:
            score += 20
        elif len(foods) >= 5:
            score += 15
        else:
            score += 10
        
        # 季节适应性
        current_season = self._get_current_season()
        seasonal_foods = [f for f in foods if f.is_available_in_season(current_season)]
        if seasonal_foods:
            score += 10 * (len(seasonal_foods) / len(foods))
        
        return min(100, score)
    
    def _generate_reasoning(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        season: SeasonType
    ) -> str:
        """生成推荐理由"""
        reasoning_parts = []
        
        # 体质分析
        reasoning_parts.append(f"根据您的{constitution_type.value}体质特点")
        
        # 症状分析
        if symptoms:
            reasoning_parts.append(f"结合您的{', '.join(symptoms)}等症状")
        
        # 季节考虑
        reasoning_parts.append(f"考虑到当前{season.value}季节特点")
        
        # 推荐原理
        reasoning_parts.append("为您推荐了具有针对性的食疗方案")
        reasoning_parts.append("通过食物的性味归经来调理体质，改善症状")
        
        return "，".join(reasoning_parts) + "。"
    
    def _generate_precautions(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str]
    ) -> List[str]:
        """生成注意事项"""
        return self._generate_therapy_precautions(constitution_type, [])
    
    def _generate_follow_up_schedule(self, duration_days: int) -> List[Dict[str, Any]]:
        """生成随访计划"""
        schedule = []
        
        # 第一周随访
        schedule.append({
            "day": 7,
            "type": "初期评估",
            "content": "检查适应性，调整方案"
        })
        
        # 第二周随访
        if duration_days >= 14:
            schedule.append({
                "day": 14,
                "type": "中期评估",
                "content": "评估效果，优化配方"
            })
        
        # 第四周随访
        if duration_days >= 28:
            schedule.append({
                "day": 28,
                "type": "阶段评估",
                "content": "全面评估，制定后续计划"
            })
        
        return schedule
    
    def _get_current_season(self) -> SeasonType:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return SeasonType.SPRING
        elif month in [6, 7, 8]:
            return SeasonType.SUMMER
        elif month in [9, 10, 11]:
            return SeasonType.AUTUMN
        else:
            return SeasonType.WINTER
    
    async def get_therapy_history(self, user_id: str) -> List[TherapyRecommendation]:
        """获取用户食疗历史"""
        return await self.therapy_repository.get_user_therapy_history(user_id)
    
    async def update_therapy_progress(
        self,
        recommendation_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """更新食疗进展"""
        return await self.therapy_repository.update_therapy_progress(
            recommendation_id, progress_data
        ) 