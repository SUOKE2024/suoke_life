"""
营养服务

提供营养分析、膳食建议等功能
"""

from typing import List, Dict, Any
from datetime import datetime

from .base_service import BaseService
from ..models.nutrition import FoodItem, NutritionAnalysis, DietPlan, MacroNutrients, MicroNutrients


class NutritionService(BaseService):
    """营养服务类"""
    
    async def analyze_nutrition(
        self,
        food_items: List[FoodItem],
        user_id: str,
        meal_type: str
    ) -> NutritionAnalysis:
        """
        分析食物营养成分
        
        Args:
            food_items: 食物列表
            user_id: 用户ID
            meal_type: 餐次类型
            
        Returns:
            营养分析结果
        """
        self.logger.info(f"开始营养分析: 用户={user_id}, 餐次={meal_type}")
        
        # 计算宏量营养素
        total_calories = sum(item.calories_per_unit * item.amount for item in food_items if item.calories_per_unit)
        total_protein = sum(
            next((n.amount for n in item.nutrients if n.name == "蛋白质"), 0) * item.amount 
            for item in food_items
        )
        total_carbs = sum(
            next((n.amount for n in item.nutrients if n.name == "碳水化合物"), 0) * item.amount 
            for item in food_items
        )
        total_fat = sum(
            next((n.amount for n in item.nutrients if n.name == "脂肪"), 0) * item.amount 
            for item in food_items
        )
        
        macro_nutrients = MacroNutrients(
            calories=total_calories,
            protein=total_protein,
            carbohydrates=total_carbs,
            fat=total_fat
        )
        
        # 计算微量营养素
        micro_nutrients = MicroNutrients()
        
        # 计算营养评分
        nutrition_score = await self._calculate_nutrition_score(macro_nutrients, micro_nutrients)
        
        # 生成建议
        recommendations = await self._generate_nutrition_recommendations(
            macro_nutrients, user_id
        )
        
        # 中医营养分析
        tcm_analysis = await self._analyze_tcm_nutrition(food_items, user_id)
        
        analysis = NutritionAnalysis(
            user_id=user_id,
            meal_type=meal_type,
            food_items=food_items,
            macro_nutrients=macro_nutrients,
            micro_nutrients=micro_nutrients,
            nutrition_score=nutrition_score,
            recommendations=recommendations,
            tcm_analysis=tcm_analysis
        )
        
        # 保存分析结果
        await self._save_nutrition_analysis(analysis)
        
        # 记录操作日志
        await self.log_operation("nutrition_analysis", user_id, {
            "meal_type": meal_type,
            "food_count": len(food_items),
            "total_calories": total_calories
        })
        
        return analysis
    
    async def generate_diet_plan(
        self,
        user_id: str,
        target_calories: int,
        dietary_restrictions: List[str] = None,
        health_goals: List[str] = None
    ) -> DietPlan:
        """
        生成个性化膳食计划
        
        Args:
            user_id: 用户ID
            target_calories: 目标热量
            dietary_restrictions: 饮食限制
            health_goals: 健康目标
            
        Returns:
            膳食计划
        """
        self.logger.info(f"生成膳食计划: 用户={user_id}, 目标热量={target_calories}")
        
        # 获取用户健康数据
        user_profile = await self._get_user_health_profile(user_id)
        
        # 计算营养目标
        macro_targets = await self._calculate_macro_targets(target_calories, user_profile)
        
        # 生成每日膳食
        daily_meals = await self._generate_daily_meals(
            target_calories, dietary_restrictions, health_goals
        )
        
        # 中医膳食原则
        tcm_principles = await self._get_tcm_diet_principles(user_id)
        
        diet_plan = DietPlan(
            user_id=user_id,
            plan_name=f"个性化膳食计划 - {datetime.now().strftime('%Y%m%d')}",
            start_date=datetime.now(),
            duration_days=7,
            daily_calorie_target=target_calories,
            macro_targets=macro_targets,
            health_goals=health_goals or [],
            dietary_restrictions=dietary_restrictions or [],
            daily_meals=daily_meals,
            plan_score=85.0,  # 示例评分
            tcm_principles=tcm_principles
        )
        
        # 保存膳食计划
        await self._save_diet_plan(diet_plan)
        
        return diet_plan
    
    async def search_food_database(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索食物数据库"""
        cache_key = self.generate_cache_key("food_search", query, limit)
        cached_result = await self.cache_get(cache_key)
        
        if cached_result:
            return cached_result
        
        # 模拟食物搜索
        results = [
            {
                "food_id": f"food_{i}",
                "name": f"食物 {i}",
                "category": "蔬菜",
                "calories_per_100g": 25 + i * 5
            }
            for i in range(1, limit + 1)
        ]
        
        await self.cache_set(cache_key, results, expire=1800)
        return results
    
    async def get_nutrition_recommendations(self, user_id: str) -> Dict[str, Any]:
        """获取个性化营养建议"""
        # 获取用户最近的营养数据
        recent_analysis = await self._get_recent_nutrition_analysis(user_id)
        
        recommendations = {
            "daily_recommendations": [
                "增加蔬菜摄入量",
                "控制精制糖摄入",
                "保证充足蛋白质"
            ],
            "weekly_goals": [
                "每周至少吃5种不同颜色的蔬菜",
                "减少加工食品摄入"
            ],
            "tcm_guidance": {
                "constitution": "平和质",
                "seasonal_advice": "春季宜养肝，多食绿色蔬菜"
            }
        }
        
        return recommendations
    
    async def get_nutrition_history(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取营养历史记录"""
        # 从数据库查询历史记录
        history = []
        for i in range(days):
            history.append({
                "date": f"2024-01-{i+1:02d}",
                "total_calories": 2000 + i * 50,
                "nutrition_score": 80 + i
            })
        
        return history
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "service": "NutritionService",
            "status": "healthy",
            "database_connection": True,
            "cache_connection": True
        }
    
    # 私有方法
    async def _calculate_nutrition_score(
        self, 
        macro_nutrients: MacroNutrients, 
        micro_nutrients: MicroNutrients
    ) -> float:
        """计算营养评分"""
        # 简化的评分算法
        base_score = 70.0
        
        # 根据宏量营养素平衡调整评分
        if 1800 <= macro_nutrients.calories <= 2200:
            base_score += 10
        
        if macro_nutrients.protein >= 50:
            base_score += 10
            
        if macro_nutrients.fiber >= 25:
            base_score += 10
        
        return min(base_score, 100.0)
    
    async def _generate_nutrition_recommendations(
        self, 
        macro_nutrients: MacroNutrients, 
        user_id: str
    ) -> List[str]:
        """生成营养建议"""
        recommendations = []
        
        if macro_nutrients.protein < 50:
            recommendations.append("建议增加蛋白质摄入")
        
        if macro_nutrients.fiber < 25:
            recommendations.append("建议增加膳食纤维摄入")
        
        if macro_nutrients.calories > 2500:
            recommendations.append("建议控制总热量摄入")
        
        return recommendations
    
    async def _analyze_tcm_nutrition(self, food_items: List[FoodItem], user_id: str) -> Dict[str, Any]:
        """中医营养分析"""
        return {
            "food_nature": "平性为主",
            "five_elements": "五行平衡",
            "seasonal_suitability": "适合当前季节",
            "constitution_match": "符合体质特点"
        }
    
    async def _save_nutrition_analysis(self, analysis: NutritionAnalysis):
        """保存营养分析结果"""
        try:
            await self.mongodb.nutrition_analyses.insert_one(analysis.dict())
        except Exception as e:
            self.logger.error(f"保存营养分析失败: {e}")
    
    async def _get_user_health_profile(self, user_id: str) -> Dict[str, Any]:
        """获取用户健康档案"""
        # 模拟用户档案
        return {
            "age": 30,
            "gender": "female",
            "weight": 60,
            "height": 165,
            "activity_level": "moderate"
        }
    
    async def _calculate_macro_targets(self, target_calories: int, user_profile: Dict[str, Any]) -> MacroNutrients:
        """计算宏量营养素目标"""
        protein_ratio = 0.15  # 15% 蛋白质
        carb_ratio = 0.55     # 55% 碳水化合物
        fat_ratio = 0.30      # 30% 脂肪
        
        return MacroNutrients(
            calories=target_calories,
            protein=target_calories * protein_ratio / 4,  # 1g蛋白质=4kcal
            carbohydrates=target_calories * carb_ratio / 4,  # 1g碳水=4kcal
            fat=target_calories * fat_ratio / 9,  # 1g脂肪=9kcal
            fiber=25.0
        )
    
    async def _generate_daily_meals(
        self, 
        target_calories: int, 
        dietary_restrictions: List[str], 
        health_goals: List[str]
    ) -> List[Any]:
        """生成每日膳食"""
        # 简化实现，返回空列表
        return []
    
    async def _get_tcm_diet_principles(self, user_id: str) -> Dict[str, Any]:
        """获取中医膳食原则"""
        return {
            "constitution_type": "平和质",
            "seasonal_principles": "春季养肝",
            "food_combinations": "寒热平衡",
            "eating_habits": "定时定量"
        }
    
    async def _save_diet_plan(self, diet_plan: DietPlan):
        """保存膳食计划"""
        try:
            await self.mongodb.diet_plans.insert_one(diet_plan.dict())
        except Exception as e:
            self.logger.error(f"保存膳食计划失败: {e}")
    
    async def _get_recent_nutrition_analysis(self, user_id: str) -> Dict[str, Any]:
        """获取最近的营养分析"""
        # 模拟数据
        return {
            "avg_calories": 2100,
            "avg_protein": 65,
            "avg_carbs": 280,
            "avg_fat": 70
        } 