"""
营养服务类

处理营养分析、膳食计划、食物数据库等相关业务逻辑
"""

import uuid
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .base_service import BaseService
from ..config.settings import get_settings
from ..models.nutrition import (
    FoodItem, NutritionAnalysis, DietPlan, 
    NutritionGoals, MealPlan, FoodDatabase
)


class NutritionService(BaseService):
    """营养服务类"""

    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.collection_name = "nutrition_data"
        self.food_db_collection = "food_database"
        self.meal_plans_collection = "meal_plans"
        
        # 营养数据库配置
        self.usda_api_key = self.settings.nutrition_api_key
        self.usda_base_url = "https://api.nal.usda.gov/fdc/v1"

    async def analyze_food(self, food_items: List[Dict[str, Any]], user_id: str) -> NutritionAnalysis:
        """分析食物营养成分"""
        try:
            total_nutrition = {
                "calories": 0.0,
                "protein": 0.0,
                "carbohydrates": 0.0,
                "fat": 0.0,
                "fiber": 0.0,
                "sugar": 0.0,
                "sodium": 0.0,
                "vitamins": {},
                "minerals": {}
            }
            
            analyzed_foods = []
            
            for food_item in food_items:
                # 查找食物营养信息
                nutrition_info = await self._get_food_nutrition(
                    food_item.get("name", ""),
                    food_item.get("quantity", 100),
                    food_item.get("unit", "g")
                )
                
                if nutrition_info:
                    # 累加营养成分
                    for key in ["calories", "protein", "carbohydrates", "fat", "fiber", "sugar", "sodium"]:
                        total_nutrition[key] += nutrition_info.get(key, 0)
                    
                    # 处理维生素和矿物质
                    for vitamin, amount in nutrition_info.get("vitamins", {}).items():
                        total_nutrition["vitamins"][vitamin] = total_nutrition["vitamins"].get(vitamin, 0) + amount
                    
                    for mineral, amount in nutrition_info.get("minerals", {}).items():
                        total_nutrition["minerals"][mineral] = total_nutrition["minerals"].get(mineral, 0) + amount
                    
                    analyzed_foods.append({
                        "name": food_item.get("name"),
                        "quantity": food_item.get("quantity"),
                        "unit": food_item.get("unit"),
                        "nutrition": nutrition_info
                    })

            # 生成营养分析
            analysis = NutritionAnalysis(
                analysis_id=str(uuid.uuid4()),
                user_id=user_id,
                food_items=analyzed_foods,
                total_nutrition=total_nutrition,
                nutritional_score=self._calculate_nutrition_score(total_nutrition),
                recommendations=await self._generate_nutrition_recommendations(total_nutrition, user_id),
                deficiencies=self._identify_deficiencies(total_nutrition),
                excesses=self._identify_excesses(total_nutrition),
                created_at=datetime.now()
            )

            # 保存分析结果
            if self.mongodb:
                await self.mongodb[self.collection_name].insert_one(analysis.dict())

            await self.log_operation("analyze_food", True, {"user_id": user_id, "food_count": len(food_items)})
            return analysis

        except Exception as e:
            await self.log_operation("analyze_food", False, {"error": str(e)})
            raise

    async def create_diet_plan(self, user_id: str, goals: Dict[str, Any], preferences: Dict[str, Any]) -> DietPlan:
        """创建个性化膳食计划"""
        try:
            # 获取用户基本信息
            user_profile = await self._get_user_profile(user_id)
            
            # 计算营养目标
            nutrition_goals = self._calculate_nutrition_goals(user_profile, goals)
            
            # 生成膳食计划
            meal_plans = await self._generate_meal_plans(nutrition_goals, preferences, user_profile)
            
            diet_plan = DietPlan(
                plan_id=str(uuid.uuid4()),
                user_id=user_id,
                plan_name=f"个性化膳食计划 - {datetime.now().strftime('%Y%m%d')}",
                duration_days=goals.get("duration_days", 7),
                nutrition_goals=nutrition_goals,
                meal_plans=meal_plans,
                shopping_list=self._generate_shopping_list(meal_plans),
                preparation_tips=self._generate_preparation_tips(meal_plans),
                created_at=datetime.now()
            )

            # 保存膳食计划
            if self.mongodb:
                await self.mongodb[self.meal_plans_collection].insert_one(diet_plan.dict())

            await self.log_operation("create_diet_plan", True, {"user_id": user_id})
            return diet_plan

        except Exception as e:
            await self.log_operation("create_diet_plan", False, {"error": str(e)})
            raise

    async def search_food_database(self, query: str, limit: int = 20) -> List[FoodDatabase]:
        """搜索食物数据库"""
        try:
            results = []
            
            # 首先搜索本地数据库
            if self.mongodb:
                local_results = await self.mongodb[self.food_db_collection].find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).limit(limit).to_list(length=limit)
                
                for result in local_results:
                    results.append(FoodDatabase(**result))
            
            # 如果本地结果不足，搜索USDA数据库
            if len(results) < limit and self.usda_api_key:
                usda_results = await self._search_usda_database(query, limit - len(results))
                results.extend(usda_results)

            await self.log_operation("search_food_database", True, {"query": query, "results": len(results)})
            return results[:limit]

        except Exception as e:
            await self.log_operation("search_food_database", False, {"error": str(e)})
            return []

    async def get_nutrition_recommendations(self, user_id: str) -> Dict[str, Any]:
        """获取个性化营养建议"""
        try:
            # 获取用户最近的营养分析
            recent_analyses = await self._get_recent_nutrition_analyses(user_id, 7)
            
            # 获取用户档案
            user_profile = await self._get_user_profile(user_id)
            
            # 分析营养趋势
            trends = self._analyze_nutrition_trends(recent_analyses)
            
            # 生成个性化建议
            recommendations = {
                "daily_targets": self._get_daily_nutrition_targets(user_profile),
                "current_status": trends,
                "improvement_areas": self._identify_improvement_areas(trends),
                "food_suggestions": await self._get_food_suggestions(user_profile, trends),
                "meal_timing": self._get_meal_timing_advice(user_profile),
                "hydration": self._get_hydration_advice(user_profile),
                "supplements": self._get_supplement_suggestions(trends),
                "weekly_goals": self._set_weekly_nutrition_goals(trends)
            }

            await self.log_operation("get_nutrition_recommendations", True, {"user_id": user_id})
            return recommendations

        except Exception as e:
            await self.log_operation("get_nutrition_recommendations", False, {"error": str(e)})
            return {}

    async def track_meal(self, user_id: str, meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """记录用餐"""
        try:
            meal_record = {
                "record_id": str(uuid.uuid4()),
                "user_id": user_id,
                "meal_type": meal_data.get("meal_type", "other"),
                "foods": meal_data.get("foods", []),
                "timestamp": datetime.now(),
                "location": meal_data.get("location"),
                "mood": meal_data.get("mood"),
                "hunger_level": meal_data.get("hunger_level"),
                "satisfaction": meal_data.get("satisfaction"),
                "notes": meal_data.get("notes", "")
            }

            # 分析这餐的营养
            nutrition_analysis = await self.analyze_food(meal_data.get("foods", []), user_id)
            meal_record["nutrition_analysis"] = nutrition_analysis.dict()

            # 保存记录
            if self.mongodb:
                await self.mongodb["meal_records"].insert_one(meal_record)

            # 更新每日营养统计
            await self._update_daily_nutrition_stats(user_id, nutrition_analysis)

            await self.log_operation("track_meal", True, {"user_id": user_id})
            return {
                "record_id": meal_record["record_id"],
                "nutrition_summary": nutrition_analysis.total_nutrition,
                "recommendations": nutrition_analysis.recommendations
            }

        except Exception as e:
            await self.log_operation("track_meal", False, {"error": str(e)})
            raise

    async def _get_food_nutrition(self, food_name: str, quantity: float, unit: str) -> Optional[Dict[str, Any]]:
        """获取食物营养信息"""
        try:
            # 首先查找本地数据库
            if self.mongodb:
                food_data = await self.mongodb[self.food_db_collection].find_one(
                    {"name": {"$regex": food_name, "$options": "i"}}
                )
                if food_data:
                    return self._calculate_nutrition_for_quantity(food_data["nutrition"], quantity, unit)

            # 如果本地没有，查询USDA数据库
            if self.usda_api_key:
                return await self._get_usda_nutrition(food_name, quantity, unit)

            # 如果都没有，返回估算值
            return self._estimate_nutrition(food_name, quantity, unit)

        except Exception as e:
            print(f"获取食物营养信息失败: {e}")
            return None

    async def _search_usda_database(self, query: str, limit: int) -> List[FoodDatabase]:
        """搜索USDA食物数据库"""
        if not self.usda_api_key:
            return []

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.usda_base_url}/foods/search"
                params = {
                    "api_key": self.usda_api_key,
                    "query": query,
                    "pageSize": limit,
                    "dataType": ["Foundation", "SR Legacy"]
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for food in data.get("foods", []):
                            food_db = FoodDatabase(
                                food_id=str(food.get("fdcId")),
                                name=food.get("description", ""),
                                brand=food.get("brandOwner", ""),
                                category=food.get("foodCategory", ""),
                                nutrition=self._parse_usda_nutrition(food.get("foodNutrients", [])),
                                serving_size=100,
                                serving_unit="g",
                                source="USDA"
                            )
                            results.append(food_db)
                        
                        return results
        except Exception as e:
            print(f"USDA数据库搜索失败: {e}")
            return []

    def _calculate_nutrition_score(self, nutrition: Dict[str, Any]) -> float:
        """计算营养评分"""
        score = 0.0
        
        # 基于营养密度计算评分
        calories = nutrition.get("calories", 0)
        if calories > 0:
            protein_score = min((nutrition.get("protein", 0) * 4 / calories) * 100, 30)
            fiber_score = min((nutrition.get("fiber", 0) / calories) * 1000, 20)
            vitamin_score = len(nutrition.get("vitamins", {})) * 2
            mineral_score = len(nutrition.get("minerals", {})) * 2
            
            score = protein_score + fiber_score + vitamin_score + mineral_score
            
            # 减分项
            sugar_penalty = min((nutrition.get("sugar", 0) / calories) * 50, 20)
            sodium_penalty = min((nutrition.get("sodium", 0) / calories) * 10, 15)
            
            score = max(0, score - sugar_penalty - sodium_penalty)
        
        return min(score, 100.0)

    async def _generate_nutrition_recommendations(self, nutrition: Dict[str, Any], user_id: str) -> List[str]:
        """生成营养建议"""
        recommendations = []
        
        # 基于营养成分生成建议
        if nutrition.get("protein", 0) < 50:
            recommendations.append("建议增加蛋白质摄入，可以选择瘦肉、鱼类、豆类等")
        
        if nutrition.get("fiber", 0) < 25:
            recommendations.append("建议增加膳食纤维摄入，多吃蔬菜、水果和全谷物")
        
        if nutrition.get("sodium", 0) > 2300:
            recommendations.append("钠摄入量偏高，建议减少盐分和加工食品的摄入")
        
        if nutrition.get("sugar", 0) > 50:
            recommendations.append("糖分摄入较高，建议减少甜食和含糖饮料")
        
        return recommendations

    def _identify_deficiencies(self, nutrition: Dict[str, Any]) -> List[str]:
        """识别营养缺乏"""
        deficiencies = []
        
        # 基于推荐摄入量判断
        if nutrition.get("protein", 0) < 50:
            deficiencies.append("蛋白质")
        
        if nutrition.get("fiber", 0) < 25:
            deficiencies.append("膳食纤维")
        
        # 检查维生素
        vitamins = nutrition.get("vitamins", {})
        if vitamins.get("vitamin_c", 0) < 90:
            deficiencies.append("维生素C")
        
        if vitamins.get("vitamin_d", 0) < 15:
            deficiencies.append("维生素D")
        
        return deficiencies

    def _identify_excesses(self, nutrition: Dict[str, Any]) -> List[str]:
        """识别营养过量"""
        excesses = []
        
        if nutrition.get("sodium", 0) > 2300:
            excesses.append("钠")
        
        if nutrition.get("sugar", 0) > 50:
            excesses.append("糖分")
        
        if nutrition.get("fat", 0) > 65:
            excesses.append("脂肪")
        
        return excesses

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "NutritionService",
            "status": "healthy",
            "mongodb_connected": self.mongodb is not None,
            "redis_connected": self.redis is not None,
            "usda_api_configured": self.usda_api_key is not None
        }

        # 测试数据库连接
        if self.mongodb:
            try:
                await self.mongodb.command("ping")
                status["mongodb_ping"] = True
            except Exception:
                status["mongodb_ping"] = False
                status["status"] = "degraded"

        return status