"""
营养推荐服务
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class NutritionService:
    """营养推荐服务"""
    
    def __init__(self, config: Dict, repos):
        """初始化营养推荐服务
        
        Args:
            config: 配置信息
            repos: 依赖的数据仓库
        """
        self.config = config
        self.repos = repos
        logger.info("初始化营养推荐服务")
    
    async def generate_diet_recommendations(self, user_id: str, constitution_type: str,
                                        season: str, 
                                        preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成饮食推荐
        
        基于用户体质类型、当前季节和偏好生成个性化饮食推荐
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            season: 当前季节
            preferences: 用户偏好
            
        Returns:
            饮食推荐
        """
        logger.info(f"为用户 {user_id} 生成饮食推荐")
        
        # 获取用户健康画像
        health_profile = await self.repos.health_profile_repo.get_by_user_id(user_id)
        
        # 确保有默认值
        if preferences is None:
            preferences = {}
        
        # 获取体质食物数据库
        constitution_food_data = await self.repos.nutrition_repo.get_constitution_food_data(constitution_type)
        
        # 获取季节食物数据库
        seasonal_food_data = await self.repos.nutrition_repo.get_seasonal_food_data(season)
        
        # 获取用户食物偏好和限制
        food_preferences = preferences.get("food_preferences", [])
        food_restrictions = preferences.get("food_restrictions", [])
        
        # 生成推荐和避免的食物列表
        recommended_foods = self._filter_foods(
            constitution_food_data.get("recommended_foods", []),
            seasonal_food_data.get("recommended_foods", []),
            food_preferences,
            food_restrictions
        )
        
        avoid_foods = self._filter_foods(
            constitution_food_data.get("avoid_foods", []),
            seasonal_food_data.get("avoid_foods", []),
            [],
            []
        )
        
        # 获取食材营养数据
        nutritional_data = await self._get_nutritional_data(recommended_foods)
        
        # 生成膳食计划
        meal_plans = await self._generate_meal_plans(
            user_id, constitution_type, season, recommended_foods, avoid_foods, preferences
        )
        
        # 生成饮食原则
        diet_principles = await self._generate_diet_principles(constitution_type, season)
        
        # 构建响应
        response = {
            "recommended_foods": recommended_foods,
            "avoid_foods": avoid_foods,
            "nutritional_data": nutritional_data,
            "meal_plans": meal_plans,
            "diet_principles": diet_principles,
            "dietary_suggestions": {
                "distribution": {
                    "早餐": "30%",
                    "午餐": "40%",
                    "晚餐": "25%",
                    "加餐": "5%"
                },
                "meal_timing": {
                    "早餐": "7:00-8:30",
                    "午餐": "12:00-13:00",
                    "晚餐": "18:00-19:00"
                },
                "hydration": "每日饮水2000-2500ml，分次少量饮用"
            }
        }
        
        # 添加中医食疗建议
        if constitution_type == "阳虚质":
            response["tcm_suggestions"] = {
                "dietary_nature": "温补",
                "five_flavors_focus": ["辛", "甘"],
                "meal_temperature": "温热",
                "seasonal_focus": {
                    "冬季": "重点温补阳气",
                    "夏季": "清淡不寒凉"
                }
            }
        elif constitution_type == "阴虚质":
            response["tcm_suggestions"] = {
                "dietary_nature": "滋阴",
                "five_flavors_focus": ["甘", "酸"],
                "meal_temperature": "温凉",
                "seasonal_focus": {
                    "冬季": "适当进补不温燥",
                    "夏季": "清热生津"
                }
            }
        elif constitution_type == "痰湿质":
            response["tcm_suggestions"] = {
                "dietary_nature": "化湿",
                "five_flavors_focus": ["苦", "辛"],
                "meal_temperature": "温热偏干",
                "seasonal_focus": {
                    "冬季": "温阳化湿",
                    "夏季": "清热祛湿"
                }
            }
        
        # 保存推荐历史
        await self._save_recommendation_history(user_id, "diet", response)
        
        return response
    
    async def track_nutrition(self, user_id: str, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """跟踪用户营养摄入
        
        记录和分析用户的营养摄入数据
        
        Args:
            user_id: 用户ID
            nutrition_data: 营养数据
            
        Returns:
            分析结果
        """
        logger.info(f"跟踪用户 {user_id} 的营养摄入")
        
        # 获取用户健康画像
        health_profile = await self.repos.health_profile_repo.get_by_user_id(user_id)
        constitution_type = health_profile.tcm_constitution.primary_type if (
            health_profile and health_profile.tcm_constitution) else None
        
        # 提取食物列表
        food_items = nutrition_data.get("food_items", [])
        if not food_items:
            return {"error": "未提供食物数据"}
        
        # 计算总营养摄入
        total_nutrition = await self._calculate_total_nutrition(food_items)
        
        # 获取用户推荐营养需求
        recommended_nutrition = await self._get_recommended_nutrition(user_id)
        
        # 营养平衡分析
        nutrition_balance = self._analyze_nutrition_balance(total_nutrition, recommended_nutrition)
        
        # 中医五味分析
        five_flavors_analysis = await self._analyze_five_flavors(food_items, constitution_type)
        
        # 中医四性分析
        four_natures_analysis = await self._analyze_four_natures(food_items, constitution_type)
        
        # 生成改进建议
        improvement_suggestions = self._generate_improvement_suggestions(
            nutrition_balance, five_flavors_analysis, four_natures_analysis, constitution_type
        )
        
        # 构建响应
        response = {
            "timestamp": datetime.now().isoformat(),
            "total_nutrition": total_nutrition,
            "nutrition_balance": nutrition_balance,
            "five_flavors_analysis": five_flavors_analysis,
            "four_natures_analysis": four_natures_analysis,
            "improvement_suggestions": improvement_suggestions
        }
        
        # 保存跟踪数据
        await self.repos.nutrition_repo.save_nutrition_tracking(user_id, response)
        
        return response
    
    async def get_food_details(self, food_name: str) -> Dict[str, Any]:
        """获取食物详情
        
        获取特定食物的详细信息，包括营养成分和中医属性
        
        Args:
            food_name: 食物名称
            
        Returns:
            食物详情
        """
        logger.info(f"获取食物详情: {food_name}")
        
        # 从食物数据库获取详情
        food_details = await self.repos.nutrition_repo.get_food_details(food_name)
        if not food_details:
            return {"error": "食物不存在"}
        
        # 获取中医食物属性
        tcm_properties = await self.repos.nutrition_repo.get_food_tcm_properties(food_name)
        
        # 合并信息
        result = {**food_details}
        if tcm_properties:
            result["tcm_properties"] = tcm_properties
        
        # 添加食物适宜体质
        suitable_constitutions = await self.repos.nutrition_repo.get_suitable_constitutions(food_name)
        if suitable_constitutions:
            result["suitable_constitutions"] = suitable_constitutions
        
        # 添加食物禁忌体质
        unsuitable_constitutions = await self.repos.nutrition_repo.get_unsuitable_constitutions(food_name)
        if unsuitable_constitutions:
            result["unsuitable_constitutions"] = unsuitable_constitutions
        
        # 添加食疗价值
        medicinal_value = await self.repos.nutrition_repo.get_food_medicinal_value(food_name)
        if medicinal_value:
            result["medicinal_value"] = medicinal_value
        
        return result
    
    async def get_recipe_by_constitution(self, constitution_type: str, season: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取适合特定体质的食谱
        
        Args:
            constitution_type: 体质类型
            season: 季节（可选）
            
        Returns:
            适合的食谱列表
        """
        logger.info(f"获取适合{constitution_type}的食谱")
        
        # 从食谱数据库获取适合该体质的食谱
        recipes = await self.repos.nutrition_repo.get_recipes_for_constitution(constitution_type, season)
        
        return recipes
    
    def _filter_foods(self, constitution_foods: List[str], seasonal_foods: List[str],
                   preferences: List[str], restrictions: List[str]) -> List[str]:
        """过滤食物列表
        
        根据季节性、偏好和限制过滤食物列表
        
        Args:
            constitution_foods: 基于体质的食物列表
            seasonal_foods: 季节性食物列表
            preferences: 偏好食物列表
            restrictions: 限制食物列表
            
        Returns:
            过滤后的食物列表
        """
        # 交集:体质食物与季节食物
        foods = [food for food in constitution_foods if food in seasonal_foods]
        
        # 如果交集太小，添加更多体质相关食物
        if len(foods) < 10:
            additional_foods = [food for food in constitution_foods if food not in foods]
            foods.extend(additional_foods[:20])  # 最多添加20个
        
        # 优先考虑偏好食物
        if preferences:
            preferred = [food for food in foods if food in preferences]
            other = [food for food in foods if food not in preferences]
            foods = preferred + other
        
        # 排除限制食物
        if restrictions:
            foods = [food for food in foods if food not in restrictions]
        
        return foods[:30]  # 限制列表长度
    
    async def _get_nutritional_data(self, foods: List[str]) -> Dict[str, Dict[str, float]]:
        """获取食物的营养数据
        
        Args:
            foods: 食物列表
            
        Returns:
            食物的营养数据
        """
        result = {}
        for food in foods[:10]:  # 为了简化，仅获取前10种食物的数据
            food_data = await self.repos.nutrition_repo.get_food_nutrition(food)
            if food_data:
                result[food] = food_data
        return result
    
    async def _generate_meal_plans(self, user_id: str, constitution_type: str, season: str,
                               recommended_foods: List[str], avoid_foods: List[str],
                               preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成膳食计划
        
        基于推荐食物和用户偏好生成一周膳食计划
        
        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            season: 季节
            recommended_foods: 推荐食物列表
            avoid_foods: 避免食物列表
            preferences: 用户偏好
            
        Returns:
            膳食计划
        """
        # 获取体质食谱
        recipes = await self.repos.nutrition_repo.get_recipes_for_constitution(constitution_type, season)
        
        # 简化起见，这里只返回三天的示例膳食计划
        return [
            {
                "day": "第一天",
                "meals": {
                    "早餐": "五谷豆浆 + 全麦面包 + 煮鸡蛋",
                    "午餐": "糙米饭 + 清蒸鱼 + 西兰花 + 胡萝卜汤",
                    "晚餐": "小米粥 + 清炒菠菜 + 蒸山药",
                    "加餐": "核桃 + 苹果"
                }
            },
            {
                "day": "第二天",
                "meals": {
                    "早餐": "黑米粥 + 蒸红薯 + 熟核桃",
                    "午餐": "糙米饭 + 蒸鸡胸肉 + 炒青菜 + 紫菜汤",
                    "晚餐": "小米粥 + 清蒸豆腐 + 凉拌黄瓜",
                    "加餐": "杏仁 + 梨"
                }
            },
            {
                "day": "第三天",
                "meals": {
                    "早餐": "燕麦粥 + 蒸红枣 + 黑芝麻",
                    "午餐": "糙米饭 + 炖牛肉 + 炒西葫芦 + 冬瓜汤",
                    "晚餐": "小米粥 + 蒸鸡蛋 + 凉拌豆芽",
                    "加餐": "腰果 + 橙子"
                }
            }
        ]
    
    async def _generate_diet_principles(self, constitution_type: str, season: str) -> List[str]:
        """生成饮食原则
        
        基于体质类型和季节生成饮食原则
        
        Args:
            constitution_type: 体质类型
            season: 季节
            
        Returns:
            饮食原则列表
        """
        # 基于体质的通用原则
        common_principles = [
            "遵循食不过量，每餐七分饱的原则",
            "定时定量进餐，避免暴饮暴食",
            "细嚼慢咽，有助消化吸收",
            "饮食多样化，确保营养均衡"
        ]
        
        # 体质特定原则
        if constitution_type == "阳虚质":
            specific_principles = [
                "饮食宜温不宜凉，少食生冷",
                "多食温阳补气之品",
                "少食寒凉食物",
                "适当增加优质蛋白质摄入",
                "晚餐宜早不宜晚，避免睡前进食"
            ]
        elif constitution_type == "阴虚质":
            specific_principles = [
                "饮食宜清淡滋润，避免辛辣刺激",
                "多食滋阴润燥之品",
                "少食温燥食物",
                "增加水分摄入",
                "午后可适当加餐，补充能量"
            ]
        elif constitution_type == "痰湿质":
            specific_principles = [
                "饮食宜清淡，少油腻",
                "多食健脾化湿之品",
                "少食甜腻黏滞食物",
                "控制总热量摄入",
                "晚餐宜少食清淡"
            ]
        else:
            specific_principles = ["根据个人体质特点，合理调配饮食"]
        
        # 季节特定原则
        if season == "春季":
            seasonal_principles = [
                "春季饮食宜养肝",
                "适当增加酸味食物",
                "多食春季时令蔬菜水果"
            ]
        elif season == "夏季":
            seasonal_principles = [
                "夏季饮食宜清淡",
                "适当增加苦味食物",
                "注意补充水分，预防暑热"
            ]
        elif season == "秋季":
            seasonal_principles = [
                "秋季饮食宜滋阴润燥",
                "适当增加辛味食物",
                "多食滋润生津食物"
            ]
        elif season == "冬季":
            seasonal_principles = [
                "冬季饮食宜温补",
                "适当增加咸味食物",
                "注意温补不燥热"
            ]
        else:
            seasonal_principles = []
        
        # 合并原则
        return common_principles + specific_principles + seasonal_principles
    
    async def _calculate_total_nutrition(self, food_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算总营养摄入
        
        Args:
            food_items: 食物项目列表
            
        Returns:
            总营养摄入
        """
        total = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbohydrate": 0,
            "fiber": 0,
            "vitamin_a": 0,
            "vitamin_c": 0,
            "vitamin_e": 0,
            "calcium": 0,
            "iron": 0,
            "zinc": 0
        }
        
        for item in food_items:
            food_name = item.get("name")
            amount = item.get("amount", 0)  # 以克为单位
            
            if not food_name or amount <= 0:
                continue
            
            # 获取食物营养数据
            nutrition = await self.repos.nutrition_repo.get_food_nutrition(food_name)
            if not nutrition:
                continue
            
            # 累加各营养素
            for nutrient in total:
                if nutrient in nutrition:
                    # 根据食用量按比例计算
                    total[nutrient] += nutrition[nutrient] * amount / 100  # 假设营养数据是基于100克
        
        return total
    
    async def _get_recommended_nutrition(self, user_id: str) -> Dict[str, Dict[str, float]]:
        """获取用户推荐营养需求
        
        Args:
            user_id: 用户ID
            
        Returns:
            推荐营养需求
        """
        # 获取用户信息
        user_info = await self.repos.user_repo.get_user_info(user_id)
        
        # 根据年龄、性别、体重等计算推荐摄入量
        # 此处略去实现，返回示例数据
        return {
            "min": {
                "calories": 1800,
                "protein": 60,
                "fat": 40,
                "carbohydrate": 230,
                "fiber": 25,
                "vitamin_a": 700,
                "vitamin_c": 75,
                "vitamin_e": 14,
                "calcium": 800,
                "iron": 12,
                "zinc": 11
            },
            "max": {
                "calories": 2200,
                "protein": 100,
                "fat": 70,
                "carbohydrate": 300,
                "fiber": 35,
                "vitamin_a": 1500,
                "vitamin_c": 200,
                "vitamin_e": 30,
                "calcium": 1200,
                "iron": 25,
                "zinc": 20
            }
        }
    
    def _analyze_nutrition_balance(self, total_nutrition: Dict[str, float], 
                               recommended_nutrition: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """分析营养平衡
        
        比较实际摄入与推荐摄入，分析营养平衡性
        
        Args:
            total_nutrition: 总营养摄入
            recommended_nutrition: 推荐营养需求
            
        Returns:
            营养平衡分析结果
        """
        balance = {}
        
        # 计算每种营养素的摄入比例
        for nutrient, value in total_nutrition.items():
            min_value = recommended_nutrition["min"].get(nutrient, 0)
            max_value = recommended_nutrition["max"].get(nutrient, float('inf'))
            
            if min_value <= 0:
                continue
            
            # 计算摄入比例
            ratio = value / min_value
            
            # 判断摄入状态
            if ratio < 0.7:
                status = "不足"
            elif ratio <= 1.0:
                status = "适中偏低"
            elif ratio <= 1.3:
                status = "适中"
            elif ratio <= 1.5:
                status = "适中偏高"
            else:
                status = "过量"
            
            balance[nutrient] = {
                "value": value,
                "min_recommended": min_value,
                "max_recommended": max_value,
                "ratio": ratio,
                "status": status
            }
        
        return balance
    
    async def _analyze_five_flavors(self, food_items: List[Dict[str, Any]], 
                               constitution_type: Optional[str]) -> Dict[str, Any]:
        """分析五味摄入情况
        
        计算五味(酸、苦、甘、辛、咸)摄入分布及其与体质的适应性
        
        Args:
            food_items: 食物项目列表
            constitution_type: 体质类型
            
        Returns:
            五味分析结果
        """
        flavors = {
            "酸": 0,
            "苦": 0,
            "甘": 0,
            "辛": 0,
            "咸": 0
        }
        
        total_amount = 0
        
        for item in food_items:
            food_name = item.get("name")
            amount = item.get("amount", 0)
            
            if not food_name or amount <= 0:
                continue
            
            total_amount += amount
            
            # 获取食物五味属性
            tcm_properties = await self.repos.nutrition_repo.get_food_tcm_properties(food_name)
            if not tcm_properties or "flavors" not in tcm_properties:
                continue
            
            # 累加各种味道
            for flavor, intensity in tcm_properties["flavors"].items():
                if flavor in flavors:
                    flavors[flavor] += amount * intensity
        
        # 计算百分比
        if total_amount > 0:
            for flavor in flavors:
                flavors[flavor] = round(flavors[flavor] / total_amount, 3)
        
        # 分析与体质的适应性
        balance_analysis = {}
        if constitution_type:
            if constitution_type == "阳虚质":
                balance_analysis = {
                    "适宜": ["辛", "甘"],
                    "适量": ["咸"],
                    "减少": ["苦", "酸"],
                    "评估": "辛甘味摄入充足，有助温阳散寒" if flavors["辛"] > 0.2 and flavors["甘"] > 0.3 else "辛甘味摄入不足，不利于阳气温补"
                }
            elif constitution_type == "阴虚质":
                balance_analysis = {
                    "适宜": ["甘", "酸"],
                    "适量": ["咸"],
                    "减少": ["辛", "苦"],
                    "评估": "甘酸味摄入充足，有助滋阴润燥" if flavors["甘"] > 0.3 and flavors["酸"] > 0.2 else "甘酸味摄入不足，不利于阴液滋养"
                }
            elif constitution_type == "痰湿质":
                balance_analysis = {
                    "适宜": ["苦", "辛"],
                    "适量": ["酸"],
                    "减少": ["甘", "咸"],
                    "评估": "苦辛味摄入充足，有助化痰祛湿" if flavors["苦"] > 0.2 and flavors["辛"] > 0.2 else "苦辛味摄入不足，不利于湿痰化解"
                }
        
        return {
            "flavor_distribution": flavors,
            "balance_analysis": balance_analysis
        }
    
    async def _analyze_four_natures(self, food_items: List[Dict[str, Any]], 
                               constitution_type: Optional[str]) -> Dict[str, Any]:
        """分析四性摄入情况
        
        计算四性(寒、凉、温、热)摄入分布及其与体质的适应性
        
        Args:
            food_items: 食物项目列表
            constitution_type: 体质类型
            
        Returns:
            四性分析结果
        """
        natures = {
            "寒": 0,
            "凉": 0,
            "平": 0,
            "温": 0,
            "热": 0
        }
        
        total_amount = 0
        
        for item in food_items:
            food_name = item.get("name")
            amount = item.get("amount", 0)
            
            if not food_name or amount <= 0:
                continue
            
            total_amount += amount
            
            # 获取食物四性属性
            tcm_properties = await self.repos.nutrition_repo.get_food_tcm_properties(food_name)
            if not tcm_properties or "nature" not in tcm_properties:
                continue
            
            # 累加各种性质
            nature = tcm_properties["nature"]
            if nature in natures:
                natures[nature] += amount
        
        # 计算百分比
        if total_amount > 0:
            for nature in natures:
                natures[nature] = round(natures[nature] / total_amount, 3)
        
        # 分析与体质的适应性
        balance_analysis = {}
        if constitution_type:
            if constitution_type == "阳虚质":
                balance_analysis = {
                    "适宜": ["温", "热"],
                    "适量": ["平"],
                    "减少": ["寒", "凉"],
                    "评估": "温热性食物摄入充足，有助温阳散寒" if natures["温"] + natures["热"] > 0.5 else "温热性食物摄入不足，不利于阳气温补"
                }
            elif constitution_type == "阴虚质":
                balance_analysis = {
                    "适宜": ["凉", "平"],
                    "适量": ["寒"],
                    "减少": ["温", "热"],
                    "评估": "凉平性食物摄入充足，有助滋阴降火" if natures["凉"] + natures["平"] > 0.5 else "凉平性食物摄入不足，不利于阴液滋养"
                }
            elif constitution_type == "痰湿质":
                balance_analysis = {
                    "适宜": ["温", "凉"],
                    "适量": ["平"],
                    "减少": ["寒", "热"],
                    "评估": "温性与凉性食物搭配适宜，有助化痰祛湿" if natures["温"] > 0.3 and natures["凉"] > 0.2 else "温凉食物搭配不当，不利于湿痰化解"
                }
        
        return {
            "nature_distribution": natures,
            "balance_analysis": balance_analysis
        }
    
    def _generate_improvement_suggestions(self, nutrition_balance: Dict[str, Any],
                                      five_flavors_analysis: Dict[str, Any],
                                      four_natures_analysis: Dict[str, Any],
                                      constitution_type: Optional[str]) -> List[Dict[str, Any]]:
        """生成改进建议
        
        基于营养分析结果生成改进建议
        
        Args:
            nutrition_balance: 营养平衡分析结果
            five_flavors_analysis: 五味分析结果
            four_natures_analysis: 四性分析结果
            constitution_type: 体质类型
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 营养素建议
        nutrient_issues = []
        for nutrient, data in nutrition_balance.items():
            if data["status"] == "不足":
                nutrient_issues.append({
                    "nutrient": nutrient,
                    "issue": "不足",
                    "ratio": data["ratio"]
                })
            elif data["status"] == "过量":
                nutrient_issues.append({
                    "nutrient": nutrient,
                    "issue": "过量",
                    "ratio": data["ratio"]
                })
        
        # 按严重程度排序
        nutrient_issues.sort(key=lambda x: abs(1 - x["ratio"]), reverse=True)
        
        # 添加最严重的问题
        for issue in nutrient_issues[:3]:
            nutrient = issue["nutrient"]
            if issue["issue"] == "不足":
                suggestion = {
                    "category": "营养素",
                    "issue": f"{nutrient}摄入不足",
                    "suggestion": f"增加{nutrient}的摄入",
                    "foods": []
                }
                
                # 添加富含该营养素的食物建议
                if nutrient == "protein":
                    suggestion["foods"] = ["瘦肉", "鱼", "鸡蛋", "豆腐", "坚果"]
                elif nutrient == "calcium":
                    suggestion["foods"] = ["牛奶", "豆腐", "绿叶蔬菜", "小鱼干", "芝麻"]
                elif nutrient == "iron":
                    suggestion["foods"] = ["动物肝脏", "瘦肉", "深绿色蔬菜", "豆类", "黑木耳"]
                elif nutrient == "vitamin_c":
                    suggestion["foods"] = ["柑橘类水果", "猕猴桃", "青椒", "西兰花", "草莓"]
                
                suggestions.append(suggestion)
            elif issue["issue"] == "过量":
                suggestions.append({
                    "category": "营养素",
                    "issue": f"{nutrient}摄入过量",
                    "suggestion": f"减少{nutrient}的摄入",
                    "foods": []
                })
        
        # 五味建议
        if constitution_type and "balance_analysis" in five_flavors_analysis:
            analysis = five_flavors_analysis["balance_analysis"]
            if "评估" in analysis and "不足" in analysis["评估"]:
                suitable_flavors = analysis.get("适宜", [])
                if suitable_flavors:
                    suggestions.append({
                        "category": "五味",
                        "issue": f"体质所需的{','.join(suitable_flavors)}味食物摄入不足",
                        "suggestion": f"适当增加{','.join(suitable_flavors)}味食物的摄入",
                        "reason": f"{constitution_type}宜{','.join(suitable_flavors)}"
                    })
        
        # 四性建议
        if constitution_type and "balance_analysis" in four_natures_analysis:
            analysis = four_natures_analysis["balance_analysis"]
            if "评估" in analysis and "不足" in analysis["评估"]:
                suitable_natures = analysis.get("适宜", [])
                if suitable_natures:
                    suggestions.append({
                        "category": "四性",
                        "issue": f"体质所需的{','.join(suitable_natures)}性食物摄入不足",
                        "suggestion": f"适当增加{','.join(suitable_natures)}性食物的摄入",
                        "reason": f"{constitution_type}宜{','.join(suitable_natures)}"
                    })
        
        return suggestions
    
    async def _save_recommendation_history(self, user_id: str, recommendation_type: str, 
                                       recommendation_data: Dict[str, Any]) -> None:
        """保存推荐历史
        
        将推荐数据保存到数据库
        
        Args:
            user_id: 用户ID
            recommendation_type: 推荐类型
            recommendation_data: 推荐数据
        """
        try:
            await self.repos.nutrition_repo.save_recommendation(
                user_id,
                recommendation_type,
                datetime.now(),
                recommendation_data
            )
        except Exception as e:
            logger.error(f"保存推荐历史失败: {str(e)}")
            # 这里可以添加失败重试逻辑