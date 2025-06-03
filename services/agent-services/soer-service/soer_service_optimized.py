#!/usr/bin/env python3
"""
索克生活 - 索儿智能体优化服务
基于OptimizedAgentBase实现的生活服务智能体
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from optimized_agent_base import OptimizedAgentBase, AgentRequest, cpu_intensive_task, cached_result
from aiohttp import web

class SoerOptimizedService(OptimizedAgentBase):
    """索儿智能体优化服务 - 生活服务专家"""
    
    def __init__(self):
        super().__init__(
            agent_name="soer",
            max_workers=int(os.getenv("MAX_WORKERS", "8")),
            redis_url=os.getenv("REDIS_URL"),
            database_url=os.getenv("DATABASE_URL")
        )
        
        # 生活服务知识库
        self.service_knowledge = self._initialize_service_knowledge()
    
    def _register_agent_routes(self):
        """注册索儿特定路由"""
        self.app.router.add_post("/lifestyle_plan", self._lifestyle_plan_handler)
        self.app.router.add_post("/nutrition_advice", self._nutrition_advice_handler)
        self.app.router.add_post("/exercise_plan", self._exercise_plan_handler)
        self.app.router.add_post("/wellness_activities", self._wellness_activities_handler)
        self.app.router.add_get("/services", self._services_handler)
    
    async def _process_action(self, request: AgentRequest) -> Dict[str, Any]:
        """处理索儿的具体动作"""
        action = request.action
        input_data = request.input_data
        
        if action == "lifestyle_plan":
            return await self._handle_lifestyle_plan(input_data)
        elif action == "nutrition_advice":
            return await self._handle_nutrition_advice(input_data)
        elif action == "exercise_plan":
            return await self._handle_exercise_plan(input_data)
        elif action == "wellness_activities":
            return await self._handle_wellness_activities(input_data)
        elif action == "food_recommendation":
            return await self._handle_food_recommendation(input_data)
        else:
            raise ValueError(f"未知的动作类型: {action}")
    
    @cached_result(ttl=1800)  # 30分钟缓存
    async def _handle_lifestyle_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理生活方式规划请求"""
        user_profile = input_data.get("user_profile", {})
        goals = input_data.get("goals", [])
        preferences = input_data.get("preferences", {})
        
        # 生成个性化生活方式计划
        lifestyle_plan = await self._create_comprehensive_lifestyle_plan(
            user_profile, goals, preferences
        )
        
        return {
            "lifestyle_plan": lifestyle_plan,
            "implementation_guide": self._create_implementation_guide(lifestyle_plan),
            "progress_tracking": self._setup_progress_tracking(goals),
            "adjustment_recommendations": self._suggest_plan_adjustments(user_profile),
            "timestamp": datetime.now().isoformat()
        }
    
    @cpu_intensive_task
    def _optimize_nutrition_plan(self, nutritional_data: np.ndarray, 
                                constraints: np.ndarray) -> Dict[str, Any]:
        """优化营养计划 - CPU密集型任务"""
        # 营养优化算法
        # 使用线性规划思想优化营养搭配
        
        # 计算营养密度矩阵
        nutrition_density = nutritional_data / np.sum(nutritional_data, axis=1, keepdims=True)
        
        # 权重优化
        weights = np.random.rand(nutritional_data.shape[1])
        optimized_scores = np.dot(nutrition_density, weights)
        
        # 约束条件检查
        constraint_violations = np.sum(nutritional_data > constraints, axis=1)
        
        # 生成推荐食物组合
        food_combinations = []
        for i in range(min(5, len(optimized_scores))):
            idx = np.argmax(optimized_scores)
            food_combinations.append({
                "food_id": int(idx),
                "nutrition_score": float(optimized_scores[idx]),
                "constraint_violations": int(constraint_violations[idx]),
                "recommended_portion": float(np.random.uniform(0.5, 2.0))
            })
            optimized_scores[idx] = -1  # 避免重复选择
        
        return {
            "optimized_combinations": food_combinations,
            "overall_nutrition_score": float(np.mean([c["nutrition_score"] for c in food_combinations])),
            "constraint_satisfaction": float(1.0 - np.mean([c["constraint_violations"] for c in food_combinations]) / len(constraints))
        }
    
    async def _handle_nutrition_advice(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理营养建议请求"""
        dietary_preferences = input_data.get("dietary_preferences", {})
        health_conditions = input_data.get("health_conditions", [])
        nutritional_goals = input_data.get("nutritional_goals", {})
        
        # 模拟营养数据
        nutritional_data = np.random.rand(50, 10)  # 50种食物，10种营养素
        constraints = np.random.rand(10) * 2  # 营养约束
        
        # 使用CPU密集型任务优化营养计划
        nutrition_optimization = await self._optimize_nutrition_plan(nutritional_data, constraints)
        
        # 生成具体建议
        nutrition_advice = await self._generate_nutrition_advice(
            dietary_preferences, health_conditions, nutritional_goals, nutrition_optimization
        )
        
        return {
            "nutrition_advice": nutrition_advice,
            "meal_plans": self._create_meal_plans(nutrition_optimization),
            "shopping_list": self._generate_shopping_list(nutrition_optimization),
            "cooking_tips": self._provide_cooking_tips(dietary_preferences),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_exercise_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理运动计划请求"""
        fitness_level = input_data.get("fitness_level", "beginner")
        goals = input_data.get("goals", [])
        available_time = input_data.get("available_time", 30)
        equipment = input_data.get("equipment", [])
        
        # 生成个性化运动计划
        exercise_plan = await self._create_exercise_plan(
            fitness_level, goals, available_time, equipment
        )
        
        return {
            "exercise_plan": exercise_plan,
            "workout_schedule": self._create_workout_schedule(exercise_plan),
            "progress_milestones": self._set_progress_milestones(goals),
            "safety_guidelines": self._provide_safety_guidelines(fitness_level),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_wellness_activities(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理养生活动请求"""
        interests = input_data.get("interests", [])
        location = input_data.get("location", "")
        season = input_data.get("season", self._get_current_season())
        budget = input_data.get("budget", "medium")
        
        # 推荐养生活动
        wellness_activities = await self._recommend_wellness_activities(
            interests, location, season, budget
        )
        
        return {
            "wellness_activities": wellness_activities,
            "seasonal_recommendations": self._get_seasonal_wellness_activities(season),
            "local_resources": self._find_local_wellness_resources(location),
            "activity_calendar": self._create_activity_calendar(wellness_activities),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_food_recommendation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理食物推荐请求"""
        constitution = input_data.get("constitution", "")
        season = input_data.get("season", self._get_current_season())
        symptoms = input_data.get("symptoms", [])
        preferences = input_data.get("preferences", {})
        
        # 基于中医理论的食物推荐
        food_recommendations = await self._recommend_therapeutic_foods(
            constitution, season, symptoms, preferences
        )
        
        return {
            "food_recommendations": food_recommendations,
            "therapeutic_recipes": self._provide_therapeutic_recipes(constitution, symptoms),
            "seasonal_foods": self._recommend_seasonal_foods(season),
            "preparation_methods": self._suggest_preparation_methods(constitution),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _create_comprehensive_lifestyle_plan(self, user_profile: Dict[str, Any], 
                                                 goals: List[str], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """创建综合生活方式计划"""
        age = user_profile.get("age", 30)
        occupation = user_profile.get("occupation", "")
        lifestyle = user_profile.get("lifestyle", "moderate")
        
        plan = {
            "daily_routine": self._design_daily_routine(age, occupation, preferences),
            "weekly_schedule": self._create_weekly_schedule(goals, preferences),
            "monthly_goals": self._set_monthly_goals(goals),
            "seasonal_adjustments": self._plan_seasonal_adjustments(),
            "wellness_integration": self._integrate_wellness_practices(preferences)
        }
        
        return plan
    
    async def _generate_nutrition_advice(self, dietary_preferences: Dict[str, Any],
                                       health_conditions: List[str],
                                       nutritional_goals: Dict[str, Any],
                                       optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成营养建议"""
        advice = {
            "general_principles": self._get_nutrition_principles(health_conditions),
            "specific_recommendations": self._create_specific_recommendations(optimization_result),
            "portion_guidance": self._provide_portion_guidance(nutritional_goals),
            "timing_advice": self._suggest_meal_timing(),
            "hydration_plan": self._create_hydration_plan(),
            "supplement_suggestions": self._suggest_supplements(health_conditions)
        }
        
        return advice
    
    async def _create_exercise_plan(self, fitness_level: str, goals: List[str],
                                  available_time: int, equipment: List[str]) -> Dict[str, Any]:
        """创建运动计划"""
        plan = {
            "workout_types": self._select_workout_types(goals, equipment),
            "intensity_levels": self._determine_intensity_levels(fitness_level),
            "frequency": self._calculate_workout_frequency(available_time, goals),
            "progression_plan": self._design_progression_plan(fitness_level, goals),
            "recovery_protocols": self._include_recovery_protocols(fitness_level)
        }
        
        return plan
    
    async def _recommend_wellness_activities(self, interests: List[str], location: str,
                                           season: str, budget: str) -> List[Dict[str, Any]]:
        """推荐养生活动"""
        activities = []
        
        # 基于兴趣的活动推荐
        interest_activities = {
            "meditation": {"name": "冥想练习", "type": "mental", "cost": "free"},
            "yoga": {"name": "瑜伽课程", "type": "physical", "cost": "low"},
            "hiking": {"name": "户外徒步", "type": "outdoor", "cost": "free"},
            "cooking": {"name": "健康烹饪", "type": "lifestyle", "cost": "medium"},
            "gardening": {"name": "园艺种植", "type": "outdoor", "cost": "medium"}
        }
        
        for interest in interests:
            if interest in interest_activities:
                activity = interest_activities[interest].copy()
                activity["seasonal_suitability"] = self._check_seasonal_suitability(interest, season)
                activity["location_availability"] = self._check_location_availability(interest, location)
                activities.append(activity)
        
        # 添加季节性推荐
        seasonal_activities = self._get_seasonal_activities(season)
        activities.extend(seasonal_activities)
        
        return activities[:10]  # 返回前10个推荐
    
    async def _recommend_therapeutic_foods(self, constitution: str, season: str,
                                         symptoms: List[str], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """推荐食疗食物"""
        # 基于体质的食物推荐
        constitution_foods = {
            "气虚质": ["山药", "大枣", "桂圆", "小米", "牛肉"],
            "阳虚质": ["羊肉", "生姜", "肉桂", "核桃", "韭菜"],
            "阴虚质": ["银耳", "百合", "梨", "蜂蜜", "鸭肉"],
            "痰湿质": ["薏米", "冬瓜", "白萝卜", "茯苓", "陈皮"],
            "湿热质": ["绿豆", "苦瓜", "黄瓜", "薏米", "莲子"]
        }
        
        # 基于症状的食物推荐
        symptom_foods = {
            "失眠": ["酸枣仁", "百合", "莲子", "小麦"],
            "便秘": ["香蕉", "蜂蜜", "芝麻", "菠菜"],
            "咳嗽": ["梨", "川贝", "枇杷", "百合"],
            "疲劳": ["人参", "黄芪", "大枣", "桂圆"]
        }
        
        recommended_foods = constitution_foods.get(constitution, [])
        
        # 添加症状相关食物
        for symptom in symptoms:
            if symptom in symptom_foods:
                recommended_foods.extend(symptom_foods[symptom])
        
        # 去重并限制数量
        recommended_foods = list(set(recommended_foods))[:15]
        
        return {
            "primary_foods": recommended_foods[:8],
            "supplementary_foods": recommended_foods[8:],
            "foods_to_avoid": self._get_foods_to_avoid(constitution, symptoms),
            "preparation_notes": self._get_preparation_notes(constitution)
        }
    
    def _initialize_service_knowledge(self) -> Dict[str, Any]:
        """初始化生活服务知识库"""
        return {
            "nutrition": {
                "macronutrients": ["蛋白质", "碳水化合物", "脂肪"],
                "micronutrients": ["维生素", "矿物质", "微量元素"],
                "food_categories": ["谷物", "蔬菜", "水果", "蛋白质", "乳制品"]
            },
            "exercise": {
                "types": ["有氧运动", "力量训练", "柔韧性训练", "平衡训练"],
                "intensities": ["低强度", "中等强度", "高强度"],
                "equipment": ["哑铃", "瑜伽垫", "跑步机", "阻力带"]
            },
            "wellness": {
                "practices": ["冥想", "瑜伽", "太极", "气功", "按摩"],
                "environments": ["室内", "户外", "水中", "山地"],
                "seasons": ["春", "夏", "秋", "冬"]
            }
        }
    
    def _create_implementation_guide(self, lifestyle_plan: Dict[str, Any]) -> Dict[str, Any]:
        """创建实施指南"""
        return {
            "getting_started": "从简单的改变开始，逐步建立新习惯",
            "weekly_focus": "每周专注于一个主要改变",
            "tracking_methods": ["日记记录", "手机应用", "定期评估"],
            "common_challenges": ["时间管理", "动机维持", "环境适应"],
            "success_strategies": ["设定小目标", "寻找支持", "庆祝进步"]
        }
    
    def _setup_progress_tracking(self, goals: List[str]) -> Dict[str, Any]:
        """设置进度跟踪"""
        return {
            "tracking_frequency": "每周评估",
            "key_metrics": ["目标完成度", "健康指标", "生活满意度"],
            "milestone_rewards": "达成阶段性目标时的奖励机制",
            "adjustment_triggers": "需要调整计划的信号"
        }
    
    def _suggest_plan_adjustments(self, user_profile: Dict[str, Any]) -> List[str]:
        """建议计划调整"""
        return [
            "根据季节变化调整活动类型",
            "基于进度反馈优化目标设定",
            "考虑生活变化调整时间安排",
            "根据身体反应调整强度"
        ]
    
    def _create_meal_plans(self, nutrition_optimization: Dict[str, Any]) -> Dict[str, Any]:
        """创建膳食计划"""
        return {
            "breakfast": "营养均衡的早餐搭配",
            "lunch": "丰富多样的午餐选择",
            "dinner": "清淡易消化的晚餐",
            "snacks": "健康的零食选项",
            "weekly_rotation": "一周不重样的搭配方案"
        }
    
    def _generate_shopping_list(self, nutrition_optimization: Dict[str, Any]) -> List[str]:
        """生成购物清单"""
        return [
            "新鲜蔬菜类",
            "优质蛋白质",
            "全谷物食品",
            "健康油脂",
            "时令水果"
        ]
    
    def _provide_cooking_tips(self, dietary_preferences: Dict[str, Any]) -> List[str]:
        """提供烹饪技巧"""
        return [
            "选择健康的烹饪方式",
            "保持食材的营养价值",
            "合理搭配食材",
            "控制调料使用",
            "注意食品安全"
        ]
    
    def _create_workout_schedule(self, exercise_plan: Dict[str, Any]) -> Dict[str, Any]:
        """创建锻炼时间表"""
        return {
            "monday": "力量训练",
            "tuesday": "有氧运动",
            "wednesday": "柔韧性训练",
            "thursday": "力量训练",
            "friday": "有氧运动",
            "saturday": "户外活动",
            "sunday": "休息或轻度活动"
        }
    
    def _set_progress_milestones(self, goals: List[str]) -> List[Dict[str, Any]]:
        """设置进度里程碑"""
        milestones = []
        for i, goal in enumerate(goals):
            milestones.append({
                "goal": goal,
                "milestone_1": f"第2周：{goal}的基础建立",
                "milestone_2": f"第4周：{goal}的习惯形成",
                "milestone_3": f"第8周：{goal}的显著改善",
                "final_target": f"第12周：{goal}的目标达成"
            })
        return milestones
    
    def _provide_safety_guidelines(self, fitness_level: str) -> List[str]:
        """提供安全指导"""
        guidelines = {
            "beginner": [
                "从低强度开始",
                "注意正确姿势",
                "充分热身和拉伸",
                "循序渐进增加强度"
            ],
            "intermediate": [
                "保持训练的多样性",
                "注意身体信号",
                "合理安排休息",
                "定期评估进度"
            ],
            "advanced": [
                "避免过度训练",
                "注重恢复质量",
                "定期调整训练计划",
                "寻求专业指导"
            ]
        }
        
        return guidelines.get(fitness_level, guidelines["beginner"])
    
    def _get_seasonal_wellness_activities(self, season: str) -> List[Dict[str, Any]]:
        """获取季节性养生活动"""
        seasonal_activities = {
            "春": [
                {"name": "踏青赏花", "benefit": "舒缓情绪"},
                {"name": "春季排毒", "benefit": "清理身体"},
                {"name": "户外瑜伽", "benefit": "增强活力"}
            ],
            "夏": [
                {"name": "游泳健身", "benefit": "清热降温"},
                {"name": "晨练太极", "benefit": "养心安神"},
                {"name": "避暑养生", "benefit": "防暑保健"}
            ],
            "秋": [
                {"name": "登高远眺", "benefit": "养肺润燥"},
                {"name": "收获体验", "benefit": "感恩自然"},
                {"name": "温补调理", "benefit": "储备能量"}
            ],
            "冬": [
                {"name": "室内运动", "benefit": "保持活力"},
                {"name": "温泉养生", "benefit": "温阳散寒"},
                {"name": "静心冥想", "benefit": "养精蓄锐"}
            ]
        }
        
        return seasonal_activities.get(season, [])
    
    def _find_local_wellness_resources(self, location: str) -> List[str]:
        """寻找本地养生资源"""
        return [
            "附近的健身中心",
            "公园和绿地",
            "瑜伽工作室",
            "中医养生馆",
            "健康食品店"
        ]
    
    def _create_activity_calendar(self, wellness_activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建活动日历"""
        return {
            "weekly_plan": "每周的养生活动安排",
            "monthly_themes": "每月的养生主题",
            "seasonal_focus": "季节性养生重点",
            "special_events": "特殊节日的养生活动"
        }
    
    def _provide_therapeutic_recipes(self, constitution: str, symptoms: List[str]) -> List[Dict[str, Any]]:
        """提供食疗配方"""
        recipes = [
            {
                "name": "山药薏米粥",
                "ingredients": ["山药", "薏米", "大米"],
                "function": "健脾祛湿",
                "suitable_for": ["痰湿质", "脾虚"]
            },
            {
                "name": "银耳莲子汤",
                "ingredients": ["银耳", "莲子", "冰糖"],
                "function": "滋阴润燥",
                "suitable_for": ["阴虚质", "失眠"]
            }
        ]
        
        return recipes
    
    def _recommend_seasonal_foods(self, season: str) -> List[str]:
        """推荐时令食物"""
        seasonal_foods = {
            "春": ["春笋", "韭菜", "菠菜", "草莓"],
            "夏": ["西瓜", "苦瓜", "绿豆", "荷叶"],
            "秋": ["梨", "银耳", "百合", "莲藕"],
            "冬": ["萝卜", "白菜", "羊肉", "核桃"]
        }
        
        return seasonal_foods.get(season, [])
    
    def _suggest_preparation_methods(self, constitution: str) -> List[str]:
        """建议制作方法"""
        methods = {
            "气虚质": ["蒸", "炖", "煮", "温补"],
            "阳虚质": ["炖煮", "温热", "少寒凉"],
            "阴虚质": ["清蒸", "凉拌", "润燥"],
            "痰湿质": ["清淡", "少油", "祛湿"],
            "湿热质": ["清热", "利湿", "少辛辣"]
        }
        
        return methods.get(constitution, ["均衡搭配"])
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    def _design_daily_routine(self, age: int, occupation: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """设计日常作息"""
        return {
            "wake_time": "6:30-7:00",
            "morning_routine": "晨练、冥想、健康早餐",
            "work_breaks": "每2小时休息10分钟",
            "lunch_time": "12:00-13:00",
            "afternoon_activities": "适度运动或放松",
            "evening_routine": "轻松活动、准备睡眠",
            "sleep_time": "22:00-23:00"
        }
    
    def _create_weekly_schedule(self, goals: List[str], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """创建周计划"""
        return {
            "monday": "新周开始，制定目标",
            "tuesday": "专注工作，保持节奏",
            "wednesday": "中周调整，评估进度",
            "thursday": "持续努力，克服困难",
            "friday": "总结一周，准备休息",
            "saturday": "放松娱乐，社交活动",
            "sunday": "休息恢复，准备新周"
        }
    
    def _set_monthly_goals(self, goals: List[str]) -> List[Dict[str, Any]]:
        """设置月度目标"""
        monthly_goals = []
        for goal in goals:
            monthly_goals.append({
                "goal": goal,
                "week_1": f"建立{goal}的基础",
                "week_2": f"强化{goal}的实践",
                "week_3": f"优化{goal}的效果",
                "week_4": f"巩固{goal}的成果"
            })
        return monthly_goals
    
    def _plan_seasonal_adjustments(self) -> Dict[str, Any]:
        """规划季节性调整"""
        return {
            "spring": "增加户外活动，注重排毒",
            "summer": "调整作息时间，防暑降温",
            "autumn": "加强营养补充，预防疾病",
            "winter": "保暖养生，储备能量"
        }
    
    def _integrate_wellness_practices(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """整合养生实践"""
        return {
            "daily_practices": "每日必做的养生活动",
            "weekly_practices": "每周进行的深度养生",
            "monthly_practices": "每月的专项调理",
            "seasonal_practices": "季节性的养生重点"
        }
    
    def _get_nutrition_principles(self, health_conditions: List[str]) -> List[str]:
        """获取营养原则"""
        return [
            "均衡搭配各类营养素",
            "控制总热量摄入",
            "增加膳食纤维",
            "减少加工食品",
            "保持规律饮食"
        ]
    
    def _create_specific_recommendations(self, optimization_result: Dict[str, Any]) -> List[str]:
        """创建具体建议"""
        return [
            "优先选择营养密度高的食物",
            "合理搭配蛋白质来源",
            "增加蔬菜水果摄入",
            "选择健康的烹饪方式",
            "注意食物的新鲜度"
        ]
    
    def _provide_portion_guidance(self, nutritional_goals: Dict[str, Any]) -> Dict[str, Any]:
        """提供分量指导"""
        return {
            "protein": "每餐一掌心大小",
            "vegetables": "每餐两拳头大小",
            "carbs": "每餐一拳头大小",
            "fats": "每餐一拇指大小"
        }
    
    def _suggest_meal_timing(self) -> Dict[str, Any]:
        """建议用餐时间"""
        return {
            "breakfast": "7:00-8:00",
            "morning_snack": "10:00-10:30",
            "lunch": "12:00-13:00",
            "afternoon_snack": "15:00-15:30",
            "dinner": "18:00-19:00",
            "evening_limit": "睡前3小时停止进食"
        }
    
    def _create_hydration_plan(self) -> Dict[str, Any]:
        """创建水分补充计划"""
        return {
            "daily_target": "8-10杯水",
            "timing": "餐前30分钟，餐后1小时",
            "quality": "优质饮用水",
            "temperature": "温水为佳",
            "alternatives": "花茶、柠檬水"
        }
    
    def _suggest_supplements(self, health_conditions: List[str]) -> List[str]:
        """建议补充剂"""
        return [
            "根据个人需求选择",
            "优先从食物获取营养",
            "咨询专业人士意见",
            "注意补充剂质量",
            "避免过量摄入"
        ]
    
    def _select_workout_types(self, goals: List[str], equipment: List[str]) -> List[str]:
        """选择锻炼类型"""
        workout_types = []
        
        if "减重" in goals:
            workout_types.append("有氧运动")
        if "增肌" in goals:
            workout_types.append("力量训练")
        if "柔韧性" in goals:
            workout_types.append("瑜伽或拉伸")
        
        return workout_types if workout_types else ["综合训练"]
    
    def _determine_intensity_levels(self, fitness_level: str) -> Dict[str, str]:
        """确定强度水平"""
        intensity_map = {
            "beginner": "低到中等强度",
            "intermediate": "中等到高强度",
            "advanced": "高强度间歇训练"
        }
        
        return {"recommended": intensity_map.get(fitness_level, "中等强度")}
    
    def _calculate_workout_frequency(self, available_time: int, goals: List[str]) -> str:
        """计算锻炼频率"""
        if available_time >= 60:
            return "每周5-6次"
        elif available_time >= 30:
            return "每周3-4次"
        else:
            return "每周2-3次"
    
    def _design_progression_plan(self, fitness_level: str, goals: List[str]) -> Dict[str, Any]:
        """设计进阶计划"""
        return {
            "week_1_2": "适应期，建立基础",
            "week_3_4": "强化期，增加强度",
            "week_5_8": "提升期，优化效果",
            "week_9_12": "巩固期，保持成果"
        }
    
    def _include_recovery_protocols(self, fitness_level: str) -> Dict[str, Any]:
        """包含恢复方案"""
        return {
            "rest_days": "每周1-2天完全休息",
            "active_recovery": "轻度活动如散步",
            "sleep": "保证7-9小时睡眠",
            "nutrition": "及时补充营养",
            "hydration": "充足水分补充"
        }
    
    def _check_seasonal_suitability(self, activity: str, season: str) -> str:
        """检查季节适宜性"""
        seasonal_suitability = {
            "hiking": {"春": "很适合", "夏": "需防暑", "秋": "最佳", "冬": "需保暖"},
            "yoga": {"春": "适合", "夏": "适合", "秋": "适合", "冬": "适合"},
            "swimming": {"春": "适合", "夏": "最佳", "秋": "适合", "冬": "室内"}
        }
        
        return seasonal_suitability.get(activity, {}).get(season, "适合")
    
    def _check_location_availability(self, activity: str, location: str) -> str:
        """检查地点可用性"""
        # 简化实现，实际应该根据具体位置查询
        return "本地可用"
    
    def _get_seasonal_activities(self, season: str) -> List[Dict[str, Any]]:
        """获取季节性活动"""
        activities = {
            "春": [{"name": "踏青", "type": "outdoor", "cost": "free"}],
            "夏": [{"name": "游泳", "type": "water", "cost": "low"}],
            "秋": [{"name": "登山", "type": "outdoor", "cost": "free"}],
            "冬": [{"name": "温泉", "type": "wellness", "cost": "medium"}]
        }
        
        return activities.get(season, [])
    
    def _get_foods_to_avoid(self, constitution: str, symptoms: List[str]) -> List[str]:
        """获取应避免的食物"""
        avoid_foods = {
            "气虚质": ["生冷食物", "过于油腻"],
            "阳虚质": ["寒凉食物", "生冷瓜果"],
            "阴虚质": ["辛辣食物", "煎炸食品"],
            "痰湿质": ["甜腻食物", "油腻食品"],
            "湿热质": ["辛辣食物", "油炸食品"]
        }
        
        return avoid_foods.get(constitution, ["过度加工食品"])
    
    def _get_preparation_notes(self, constitution: str) -> List[str]:
        """获取制作注意事项"""
        return [
            "选择新鲜食材",
            "适合的烹饪方式",
            "合理的调味",
            "适当的温度",
            "适量的分量"
        ]
    
    async def _lifestyle_plan_handler(self, request):
        """生活方式规划接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'life_' + str(hash(str(data)))),
                agent_type="soer",
                action="lifestyle_plan",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _nutrition_advice_handler(self, request):
        """营养建议接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'nut_' + str(hash(str(data)))),
                agent_type="soer",
                action="nutrition_advice",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _exercise_plan_handler(self, request):
        """运动计划接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'exe_' + str(hash(str(data)))),
                agent_type="soer",
                action="exercise_plan",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _wellness_activities_handler(self, request):
        """养生活动接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'wel_' + str(hash(str(data)))),
                agent_type="soer",
                action="wellness_activities",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _services_handler(self, request):
        """服务信息接口处理器"""
        return web.json_response({
            "agent": "soer",
            "service_knowledge": self.service_knowledge,
            "capabilities": [
                "生活方式规划",
                "营养建议",
                "运动计划",
                "养生活动推荐",
                "食疗指导"
            ],
            "specialties": [
                "个性化生活方案",
                "健康饮食指导",
                "运动健身规划",
                "养生活动安排",
                "生活习惯优化"
            ]
        })

async def main():
    """主函数"""
    service = SoerOptimizedService()
    
    port = int(os.getenv("PORT", "8003"))
    host = os.getenv("HOST", "0.0.0.0")
    
    await service.start_server(host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main()) 