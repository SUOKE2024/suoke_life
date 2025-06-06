"""
food_therapy_manager - 索克生活项目模块
"""

            import re
from .model_factory import ModelFactory
from datetime import UTC, datetime
from internal.repository.food_repository import FoodRepository
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector, track_llm_metrics
from typing import Any
import logging
import os
import time
import uuid

#!/usr/bin/env python3
"""
食疗服务管理器
负责小克智能体的食疗相关功能，包括食疗方案生成、食药配伍分析、时令食谱推荐等
"""



# 导入项目依赖

# 初始化日志
logger = logging.getLogger(__name__)


class FoodTherapyManager:
    """食疗服务管理器，负责食疗方案生成、食药配伍和食谱推荐等功能"""

    def __init__(self, model_factory=None):
        """
        初始化食疗服务管理器

        Args:
            model_factory: 模型工厂实例，如果为None则创建新实例
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 设置模型工厂
        self.model_factory = model_factory or ModelFactory()

        # 加载模型配置
        self.llm_config = self.config.get_section("models.llm")

        # 设置默认模型
        self.primary_model = self.llm_config.get("primary_model", "gpt-4o-mini")
        self.fallback_model = self.llm_config.get("fallback_model", "llama-3-8b")

        # 加载提示语模板
        self.templates_dir = os.path.join(
            self.config.get("config_dir", "config"), "prompts", "templates"
        )
        self.templates = self._load_prompt_templates()

        # 初始化食物知识库
        self.food_repo = FoodRepository()

        # 加载食疗配置
        self.food_therapy_config = self.config.get_section("food_therapy", {})

        logger.info("食疗服务管理器初始化完成")

    def _load_prompt_templates(self) -> dict[str, str]:
        """加载所有提示语模板文件"""
        templates = {}

        templates_files = {
            "diet_plan_generation": "diet_plan_generation_prompt.txt",
            "food_medicine_pairing": "food_medicine_pairing_prompt.txt",
            "seasonal_diet_adjustment": "seasonal_diet_adjustment_prompt.txt",
            "recipe_recommendation": "recipe_recommendation_prompt.txt",
            "medicinal_diet_formulation": "medicinal_diet_formulation_prompt.txt",
            "food_safety_analysis": "food_safety_analysis_prompt.txt",
            "constitution_food_rating": "constitution_food_rating_prompt.txt",
        }

        for key, filename in templates_files.items():
            file_path = os.path.join(self.templates_dir, filename)
            try:
                with open(file_path, encoding="utf-8") as f:
                    templates[key] = f.read()
                logger.debug(f"加载提示语模板 {key} 成功")
            except Exception as e:
                logger.error(f"加载提示语模板 {key} 失败: {e!s}")
                # 设置一个简单的备用提示语
                templates[key] = (
                    f"你是小克，索克生活APP的医疗资源调度智能体中负责{key}的专家。请根据用户信息提供专业建议。"
                )

        return templates

    def _fill_template(self, template_key: str, params: dict[str, Any]) -> str:
        """
        填充提示语模板

        Args:
            template_key: 模板键名
            params: 模板参数

        Returns:
            填充后的提示语
        """
        if template_key not in self.templates:
            logger.warning(f"未找到模板 {template_key}，使用备用提示语")
            return f"你是小克，索克生活APP的医疗资源调度智能体中负责{template_key}的专家。请根据用户信息提供专业建议。"

        template = self.templates[template_key]

        # 替换模板中的占位符
        for key, value in params.items():
            placeholder = "{{" + key + "}}"
            if placeholder in template:
                template = template.replace(placeholder, str(value))

        return template

    @track_llm_metrics(model="food_therapy", query_type="diet_plan")
    async def generate_diet_plan(
        self,
        user_id: str,
        constitution_type: str,
        health_conditions: list[str] | None = None,
        preferences: list[str] | None = None,
        allergies: list[str] | None = None,
        current_medications: list[str] | None = None,
        plan_duration: int = 7,
    ) -> dict[str, Any]:
        """
        生成个性化食疗方案

        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_conditions: 健康状况列表
            preferences: 偏好列表
            allergies: 过敏源列表
            current_medications: 当前用药列表
            plan_duration: 方案天数

        Returns:
            Dict[str, Any]: 食疗方案
        """
        try:
            # 记录请求指标
            self.metrics.increment_diet_plan_generation_count()
            start_time = time.time()

            # 获取当前季节
            current_date = datetime.now()
            month = current_date.month

            if 3 <= month <= 5:
                season = "SPRING"
            elif 6 <= month <= 8:
                season = "SUMMER"
            elif 9 <= month <= 11:
                season = "AUTUMN"
            else:
                season = "WINTER"

            # 获取适合的食材
            suitable_foods = await self.get_products_for_constitution(
                constitution_type, health_conditions, season, limit=30
            )

            # 获取食物药物相互作用信息
            food_drug_interactions = []
            if current_medications:
                food_drug_interactions = (
                    await self.food_repo.get_food_drug_interactions(current_medications)
                )

            # 过滤过敏源和药物相互作用
            filtered_foods = []
            for food in suitable_foods:
                # 过滤过敏源
                if allergies and any(
                    allergen in food.get("allergens", []) for allergen in allergies
                ):
                    continue

                # 过滤药物相互作用
                if food_drug_interactions:
                    has_interaction = False
                    for interaction in food_drug_interactions:
                        if food["id"] == interaction["food_id"]:
                            has_interaction = True
                            break

                    if has_interaction:
                        continue

                filtered_foods.append(food)

            # 建立每日菜单
            daily_menus = []
            for day in range(plan_duration):
                breakfast_foods = self._select_meal_foods(
                    filtered_foods, "BREAKFAST", 2
                )
                lunch_foods = self._select_meal_foods(filtered_foods, "LUNCH", 3)
                dinner_foods = self._select_meal_foods(filtered_foods, "DINNER", 3)
                snack_foods = self._select_meal_foods(filtered_foods, "SNACK", 1)

                daily_menus.append(
                    {
                        "day": day + 1,
                        "breakfast": breakfast_foods,
                        "lunch": lunch_foods,
                        "dinner": dinner_foods,
                        "snack": snack_foods,
                        "hydration": self._generate_hydration_recommendation(
                            constitution_type, season
                        ),
                    }
                )

            # 生成食疗方案总结
            summary = {
                "principle": self._get_diet_principle(constitution_type),
                "focus_nutrients": self._get_focus_nutrients(
                    constitution_type, health_conditions
                ),
                "foods_to_favor": self._get_top_foods_to_favor(filtered_foods, 5),
                "foods_to_avoid": self._get_foods_to_avoid(constitution_type),
                "special_notes": self._get_special_notes(
                    constitution_type, health_conditions, allergies, current_medications
                ),
            }

            # 生成方案ID
            plan_id = str(uuid.uuid4())

            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_diet_plan_generation_time(response_time)

            # 构建响应
            return {
                "plan_id": plan_id,
                "user_id": user_id,
                "constitution_type": constitution_type,
                "health_conditions": health_conditions or [],
                "season": season,
                "creation_date": current_date.isoformat(),
                "duration_days": plan_duration,
                "summary": summary,
                "daily_menus": daily_menus,
                "disclaimer": "此饮食方案仅作参考，请在执行前咨询医师或营养师，特别是存在慢性疾病或特殊健康状况的人群。",
            }

        except Exception as e:
            logger.error(f"生成食疗方案失败: {e!s}", exc_info=True)
            raise

    @track_llm_metrics(model="food_therapy", query_type="food_medicine")
    async def analyze_food_medicine_pairing(
        self, medicine_data: dict[str, Any], user_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        分析食物与药物的配伍关系

        Args:
            medicine_data: 药物数据，包含药物名称、类型、成分等
            user_data: 用户数据，包含饮食习惯、体质等

        Returns:
            Dict[str, Any]: 食药配伍分析结果
        """
        # 记录指标
        self.metrics.increment_request_count("food_medicine_pairing")
        start_time = time.time()

        try:
            # 准备模板参数
            template_params = {
                "medicine_name": medicine_data.get("name", ""),
                "medicine_type": medicine_data.get("type", "未知类型"),
                "medicine_ingredients": medicine_data.get("ingredients", "未知成分"),
                "medicine_purpose": medicine_data.get("purpose", "未知用途"),
                "medicine_duration": medicine_data.get("duration", "未知时长"),
                "medicine_time": medicine_data.get("time", "未知时间"),
                "dietary_habits": user_data.get("dietary_habits", "无特殊饮食习惯"),
                "planned_foods": user_data.get("planned_foods", "无计划饮食"),
                "constitution_analysis": user_data.get(
                    "constitution_analysis", "未提供体质分析信息"
                ),
            }

            # 填充提示语模板
            prompt = self._fill_template("food_medicine_pairing", template_params)

            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是小克，索克生活APP的医疗资源调度智能体中负责食药配伍分析的专家。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用LLM生成食药配伍分析
            (
                analysis_text,
                response_meta,
            ) = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.2,  # 较低的温度，提高确定性
                max_tokens=1536,
            )

            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("food_medicine_pairing", process_time)

            # 返回结果
            return {
                "analysis_id": str(uuid.uuid4()),
                "medicine_id": medicine_data.get("id", ""),
                "user_id": user_data.get("user_id", ""),
                "analysis_text": analysis_text,
                "created_at": datetime.now(UTC).isoformat(),
                "metadata": {
                    "model": response_meta.get("model", self.primary_model),
                    "process_time": process_time,
                    "token_count": response_meta.get("token_count", 0),
                },
            }

        except Exception as e:
            # 记录错误
            logger.error(f"分析食药配伍关系失败: {e!s}")
            self.metrics.increment_error_count("food_medicine_pairing")

            # 返回错误响应
            return {
                "analysis_id": str(uuid.uuid4()),
                "medicine_id": medicine_data.get("id", ""),
                "user_id": user_data.get("user_id", ""),
                "error": str(e),
                "success": False,
                "message": "分析食药配伍关系时出现错误，请稍后重试",
            }

    @track_llm_metrics(model="food_therapy", query_type="seasonal_diet")
    async def adjust_seasonal_diet(
        self, user_data: dict[str, Any], season_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        根据季节调整饮食建议

        Args:
            user_data: 用户数据，包含体质、现有食疗方案等
            season_data: 季节数据，包含当前季节、即将到来的季节等

        Returns:
            Dict[str, Any]: 季节性饮食调整建议
        """
        # 记录指标
        self.metrics.increment_request_count("seasonal_diet_adjustment")
        start_time = time.time()

        try:
            # 准备模板参数
            template_params = {
                "user_name": user_data.get("name", "用户"),
                "user_age": user_data.get("age", ""),
                "constitution_type": user_data.get("constitution_type", "未知体质"),
                "current_diet_plan": user_data.get(
                    "current_diet_plan", "无现有食疗方案"
                ),
                "health_goals": user_data.get("health_goals", "保持健康"),
                "current_season": season_data.get(
                    "current_season", self._get_current_season()
                ),
                "upcoming_season": season_data.get(
                    "upcoming_season", self._get_next_season()
                ),
                "climate_characteristics": season_data.get("climate", ""),
                "location": user_data.get("location", "未知地区"),
            }

            # 填充提示语模板
            prompt = self._fill_template("seasonal_diet_adjustment", template_params)

            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是小克，索克生活APP的医疗资源调度智能体中负责季节性食疗调整的专家。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用LLM生成季节性饮食调整建议
            (
                adjustment_text,
                response_meta,
            ) = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1536,
            )

            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("seasonal_diet_adjustment", process_time)

            # 返回结果
            return {
                "adjustment_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "adjustment_text": adjustment_text,
                "current_season": season_data.get("current_season", ""),
                "upcoming_season": season_data.get("upcoming_season", ""),
                "created_at": datetime.now(UTC).isoformat(),
                "metadata": {
                    "model": response_meta.get("model", self.primary_model),
                    "process_time": process_time,
                    "token_count": response_meta.get("token_count", 0),
                },
            }

        except Exception as e:
            # 记录错误
            logger.error(f"生成季节性饮食调整建议失败: {e!s}")
            self.metrics.increment_error_count("seasonal_diet_adjustment")

            # 返回错误响应
            return {
                "adjustment_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "error": str(e),
                "success": False,
                "message": "生成季节性饮食调整建议时出现错误，请稍后重试",
            }

    @track_llm_metrics(model="food_therapy", query_type="recipe")
    async def recommend_recipes(
        self,
        user_id: str,
        constitution_type: str,
        health_conditions: list[str] | None = None,
        preferences: list[str] | None = None,
        difficulty_level: str = "MEDIUM",
        cooking_time: int = 30,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        推荐适合用户体质的食谱

        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_conditions: 健康状况列表
            preferences: 偏好列表
            difficulty_level: 难度级别
            cooking_time: 烹饪时间（分钟）
            limit: 最大结果数

        Returns:
            List[Dict[str, Any]]: 食谱列表
        """
        try:
            # 记录请求指标
            self.metrics.increment_recipe_recommendation_count()
            start_time = time.time()

            # 获取适合的食材
            suitable_foods = await self.get_products_for_constitution(
                constitution_type, health_conditions, limit=20
            )

            # 提取食材ID
            food_ids = [food["id"] for food in suitable_foods]

            # 查询包含这些食材的食谱
            recipes = await self.food_repo.get_recipes_by_foods(
                food_ids, difficulty_level, cooking_time, limit * 2
            )

            # 按照用户偏好过滤
            filtered_recipes = []
            if preferences:
                for recipe in recipes:
                    # 计算偏好匹配度
                    preference_match = sum(
                        1
                        for pref in preferences
                        if pref.lower() in recipe.get("tags", [])
                        or pref.lower() in recipe.get("cuisine_type", "").lower()
                    )

                    # 添加偏好匹配度
                    recipe_copy = recipe.copy()
                    recipe_copy["preference_match"] = preference_match
                    filtered_recipes.append(recipe_copy)

                # 按偏好匹配度排序
                filtered_recipes.sort(key=lambda x: x["preference_match"], reverse=True)
            else:
                filtered_recipes = recipes

            # 限制数量
            top_recipes = filtered_recipes[:limit]

            # 为每个食谱添加体质益处说明
            for recipe in top_recipes:
                recipe["constitution_benefits"] = (
                    self._get_recipe_constitution_benefits(recipe, constitution_type)
                )

            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_recipe_recommendation_time(response_time)

            return top_recipes

        except Exception as e:
            logger.error(f"推荐食谱失败: {e!s}", exc_info=True)
            return []

    def _get_current_season(self) -> str:
        """获取当前季节"""
        now = datetime.now()
        month = now.month

        if 3 <= month <= 5:
            return "春季"
        elif 6 <= month <= 8:
            return "夏季"
        elif 9 <= month <= 11:
            return "秋季"
        else:
            return "冬季"

    def _get_next_season(self) -> str:
        """获取下一个季节"""
        current_season = self._get_current_season()

        season_cycle = {"春季": "夏季", "夏季": "秋季", "秋季": "冬季", "冬季": "春季"}

        return season_cycle.get(current_season, "春季")

    @track_llm_metrics(model="food_therapy", query_type="food_safety")
    async def analyze_food_safety(
        self, food_data: dict[str, Any], user_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        分析食品安全性并提供建议

        Args:
            food_data: 食品相关数据，包含食品名称、来源、储存条件等
            user_data: 用户数据，包含体质、过敏史等

        Returns:
            Dict[str, Any]: 食品安全分析结果
        """
        # 记录指标
        self.metrics.increment_request_count("food_safety_analysis")
        start_time = time.time()

        try:
            # 准备模板参数
            template_params = {
                "food_name": food_data.get("name", ""),
                "food_category": food_data.get("category", "未知类别"),
                "food_origin": food_data.get("origin", "未知来源"),
                "production_date": food_data.get("production_date", "未知日期"),
                "acquisition_channel": food_data.get("acquisition_channel", "未知渠道"),
                "storage_method": food_data.get("storage_method", "未知存储方式"),
                "storage_duration": food_data.get("storage_duration", "未知存储时间"),
                "appearance": food_data.get("appearance", "未描述外观"),
                "smell": food_data.get("smell", "未描述气味"),
                "constitution_type": user_data.get("constitution_type", "未知体质"),
                "allergy_history": user_data.get("allergy_history", "无已知过敏史"),
                "health_condition": user_data.get("health_condition", "一般健康"),
                "medication": user_data.get("medication", "无用药情况"),
            }

            # 填充提示语模板
            prompt = self._fill_template("food_safety_analysis", template_params)

            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是小克，索克生活APP的医疗资源调度智能体中负责食品安全分析的专家。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用LLM生成食品安全分析
            (
                analysis_text,
                response_meta,
            ) = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.2,  # 较低的温度，需要高确定性
                max_tokens=1536,
            )

            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("food_safety_analysis", process_time)

            # 返回结果
            return {
                "analysis_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "food_id": food_data.get("id", ""),
                "analysis_text": analysis_text,
                "created_at": datetime.now(UTC).isoformat(),
                "metadata": {
                    "model": response_meta.get("model", self.primary_model),
                    "process_time": process_time,
                    "token_count": response_meta.get("token_count", 0),
                },
            }

        except Exception as e:
            # 记录错误
            logger.error(f"分析食品安全性失败: {e!s}")
            self.metrics.increment_error_count("food_safety_analysis")

            # 返回错误响应
            return {
                "analysis_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "food_id": food_data.get("id", ""),
                "error": str(e),
                "success": False,
                "message": "分析食品安全性时出现错误，请稍后重试",
            }

    @track_llm_metrics(model="food_therapy", query_type="medicinal_diet")
    async def design_medicinal_diet_formulation(
        self, user_data: dict[str, Any], health_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        设计个性化药膳方剂

        Args:
            user_data: 用户基本数据，包含个人信息、体质等
            health_data: 健康状况数据，包含症状、用药情况等

        Returns:
            Dict[str, Any]: 设计的药膳方剂
        """
        # 记录指标
        self.metrics.increment_request_count("medicinal_diet_formulation")
        start_time = time.time()

        try:
            # 准备模板参数
            template_params = {
                "user_name": user_data.get("name", "用户"),
                "user_age": user_data.get("age", ""),
                "user_gender": user_data.get("gender", ""),
                "user_weight": user_data.get("weight", ""),
                "constitution_type": user_data.get("constitution_type", "未知体质"),
                "health_condition": health_data.get("health_condition", "一般健康"),
                "symptoms": health_data.get("symptoms", "无特殊症状"),
                "medication_history": health_data.get(
                    "medication_history", "无用药情况"
                ),
                "dietary_preferences": user_data.get(
                    "dietary_preferences", "无特殊饮食偏好"
                ),
                "current_season": user_data.get("season", self._get_current_season()),
            }

            # 填充提示语模板
            prompt = self._fill_template("medicinal_diet_formulation", template_params)

            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是小克，索克生活APP的医疗资源调度智能体中负责药膳方剂设计的专家。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用LLM生成药膳方剂
            (
                formulation_text,
                response_meta,
            ) = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.4,  # 平衡创意性和确定性
                max_tokens=2048,
            )

            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("medicinal_diet_formulation", process_time)

            # 返回结果
            return {
                "formulation_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "formulation_text": formulation_text,
                "constitution_type": user_data.get("constitution_type", ""),
                "target_symptoms": health_data.get("symptoms", ""),
                "created_at": datetime.now(UTC).isoformat(),
                "metadata": {
                    "model": response_meta.get("model", self.primary_model),
                    "process_time": process_time,
                    "token_count": response_meta.get("token_count", 0),
                },
            }

        except Exception as e:
            # 记录错误
            logger.error(f"设计药膳方剂失败: {e!s}")
            self.metrics.increment_error_count("medicinal_diet_formulation")

            # 返回错误响应
            return {
                "formulation_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "error": str(e),
                "success": False,
                "message": "设计药膳方剂时出现错误，请稍后重试",
            }

    @track_llm_metrics(model="food_therapy", query_type="food_rating")
    async def rate_food_for_constitution(
        self, food_data: dict[str, Any], user_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        对食材进行体质适应性评分

        Args:
            food_data: 食材数据，包含食材名称、性味归经等
            user_data: 用户数据，包含体质分析等

        Returns:
            Dict[str, Any]: 食材体质评分结果
        """
        # 记录指标
        self.metrics.increment_request_count("constitution_food_rating")
        start_time = time.time()

        try:
            # 准备模板参数
            template_params = {
                "food_name": food_data.get("name", ""),
                "food_category": food_data.get("category", "未知类别"),
                "nature_flavor": food_data.get("nature_flavor", "未知性味"),
                "functions": food_data.get("functions", "未知功效"),
                "cooking_methods": food_data.get("cooking_methods", "未知烹饪方式"),
                "current_season": user_data.get("season", self._get_current_season()),
                "constitution_profile": user_data.get(
                    "constitution_profile", "未提供体质详情"
                ),
                # 以下为预填充的评分，将由LLM生成具体评分
                "rating_balanced": "待评分",
                "rating_qi_deficiency": "待评分",
                "rating_yang_deficiency": "待评分",
                "rating_yin_deficiency": "待评分",
                "rating_phlegm_dampness": "待评分",
                "rating_damp_heat": "待评分",
                "rating_blood_stasis": "待评分",
                "rating_qi_stagnation": "待评分",
                "rating_allergic": "待评分",
            }

            # 填充提示语模板
            prompt = self._fill_template("constitution_food_rating", template_params)

            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": "你是小克，索克生活APP的医疗资源调度智能体中负责食材体质评分的专家。",
                },
                {"role": "user", "content": prompt},
            ]

            # 调用LLM生成食材体质评分
            (
                rating_text,
                response_meta,
            ) = await self.model_factory.generate_chat_completion(
                model=self.primary_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2048,
            )

            # 记录成功指标
            process_time = time.time() - start_time
            self.metrics.record_request_time("constitution_food_rating", process_time)

            # 尝试提取评分数据（可选功能，需要结构化输出）
            ratings = self._extract_ratings_from_text(rating_text)

            # 返回结果
            return {
                "rating_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "food_id": food_data.get("id", ""),
                "food_name": food_data.get("name", ""),
                "rating_text": rating_text,
                "ratings": ratings,  # 结构化评分数据
                "created_at": datetime.now(UTC).isoformat(),
                "metadata": {
                    "model": response_meta.get("model", self.primary_model),
                    "process_time": process_time,
                    "token_count": response_meta.get("token_count", 0),
                },
            }

        except Exception as e:
            # 记录错误
            logger.error(f"评分食材体质适应性失败: {e!s}")
            self.metrics.increment_error_count("constitution_food_rating")

            # 返回错误响应
            return {
                "rating_id": str(uuid.uuid4()),
                "user_id": user_data.get("user_id", ""),
                "food_id": food_data.get("id", ""),
                "error": str(e),
                "success": False,
                "message": "评分食材体质适应性时出现错误，请稍后重试",
            }

    def _extract_ratings_from_text(self, rating_text: str) -> dict[str, int]:
        """
        从评分文本中提取结构化评分数据

        Args:
            rating_text: 评分文本内容

        Returns:
            Dict[str, int]: 体质评分数据
        """
        ratings = {
            "balanced": None,
            "qi_deficiency": None,
            "yang_deficiency": None,
            "yin_deficiency": None,
            "phlegm_dampness": None,
            "damp_heat": None,
            "blood_stasis": None,
            "qi_stagnation": None,
            "allergic": None,
        }

        try:
            # 简单正则表达式匹配评分

            # 匹配"评分：X"模式
            balanced_match = re.search(r"平和质\s*评分：\s*(\d)", rating_text)
            if balanced_match:
                ratings["balanced"] = int(balanced_match.group(1))

            qi_def_match = re.search(r"气虚质\s*评分：\s*(\d)", rating_text)
            if qi_def_match:
                ratings["qi_deficiency"] = int(qi_def_match.group(1))

            yang_def_match = re.search(r"阳虚质\s*评分：\s*(\d)", rating_text)
            if yang_def_match:
                ratings["yang_deficiency"] = int(yang_def_match.group(1))

            yin_def_match = re.search(r"阴虚质\s*评分：\s*(\d)", rating_text)
            if yin_def_match:
                ratings["yin_deficiency"] = int(yin_def_match.group(1))

            phlegm_match = re.search(r"痰湿质\s*评分：\s*(\d)", rating_text)
            if phlegm_match:
                ratings["phlegm_dampness"] = int(phlegm_match.group(1))

            damp_heat_match = re.search(r"湿热质\s*评分：\s*(\d)", rating_text)
            if damp_heat_match:
                ratings["damp_heat"] = int(damp_heat_match.group(1))

            blood_match = re.search(r"血瘀质\s*评分：\s*(\d)", rating_text)
            if blood_match:
                ratings["blood_stasis"] = int(blood_match.group(1))

            qi_stag_match = re.search(r"气郁质\s*评分：\s*(\d)", rating_text)
            if qi_stag_match:
                ratings["qi_stagnation"] = int(qi_stag_match.group(1))

            allergic_match = re.search(r"特禀质\s*评分：\s*(\d)", rating_text)
            if allergic_match:
                ratings["allergic"] = int(allergic_match.group(1))

        except Exception as e:
            logger.warning(f"提取评分数据失败: {e!s}")

        return ratings

    async def close(self):
        """关闭资源"""
        # 清理资源
        if self.model_factory:
            await self.model_factory.close()

        logger.info("食疗服务管理器已关闭")

    async def get_products_for_constitution(
        self,
        constitution_type: str,
        health_conditions: list[str] | None = None,
        season: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        获取适合特定体质的食材产品

        Args:
            constitution_type: 体质类型
            health_conditions: 健康状况列表
            season: 季节
            limit: 最大结果数

        Returns:
            List[Dict[str, Any]]: 体质匹配产品列表
        """
        try:
            # 记录请求指标
            self.metrics.increment_constitution_food_match_count(constitution_type)
            start_time = time.time()

            # 查询适合该体质的食物
            constitution_foods = await self.food_repo.get_foods_by_constitution(
                constitution_type, limit * 2
            )

            # 健康状况过滤
            filtered_foods = []
            if health_conditions:
                for food in constitution_foods:
                    # 检查禁忌
                    has_contraindication = False
                    for condition in health_conditions:
                        if condition in food.get("contraindications", []):
                            has_contraindication = True
                            break

                    if not has_contraindication:
                        filtered_foods.append(food)
            else:
                filtered_foods = constitution_foods

            # 季节性过滤
            seasonal_filtered_foods = []
            if season:
                for food in filtered_foods:
                    if "ALL" in food.get("seasons", []) or season in food.get(
                        "seasons", []
                    ):
                        seasonal_filtered_foods.append(food)
            else:
                seasonal_filtered_foods = filtered_foods

            # 评分和排序
            scored_foods = []
            for food in seasonal_filtered_foods:
                # 计算评分
                score = self._calculate_food_score(
                    food, constitution_type, health_conditions, season
                )

                # 添加评分
                food_copy = food.copy()
                food_copy["score"] = score
                scored_foods.append(food_copy)

            # 按评分排序
            scored_foods.sort(key=lambda x: x["score"], reverse=True)

            # 限制数量
            top_foods = scored_foods[:limit]

            # 记录响应指标
            response_time = time.time() - start_time
            self.metrics.record_constitution_food_match_time(response_time)

            return top_foods

        except Exception as e:
            logger.error(f"获取体质食材匹配失败: {e!s}", exc_info=True)
            return []

    def _calculate_food_score(
        self,
        food: dict[str, Any],
        constitution_type: str,
        health_conditions: list[str] | None = None,
        season: str | None = None,
    ) -> float:
        """计算食物匹配分数"""
        score = 0.0

        # 体质匹配分数 (0-5分)
        if constitution_type in food.get("constitution_benefits", {}):
            benefit_level = food["constitution_benefits"][constitution_type]
            if benefit_level == "HIGH":
                score += 5.0
            elif benefit_level == "MEDIUM":
                score += 3.0
            else:
                score += 1.0

        # 季节匹配分数 (0-2分)
        if season:
            if season in food.get("seasons", []):
                score += 2.0
            elif "ALL" in food.get("seasons", []):
                score += 1.0

        # 健康状况匹配分数 (0-3分)
        if health_conditions:
            matching_benefits = sum(
                1
                for condition in health_conditions
                if condition in food.get("health_benefits", [])
            )
            score += min(3.0, matching_benefits)

        # 归一化为0-1分
        return min(1.0, score / 10.0)

    def _select_meal_foods(
        self, foods: list[dict[str, Any]], meal_type: str, count: int
    ) -> list[dict[str, Any]]:
        """为特定餐点选择食物"""
        # 按餐点类型过滤
        suitable_for_meal = []
        for food in foods:
            if meal_type in food.get("suitable_meals", []) or "ALL" in food.get(
                "suitable_meals", []
            ):
                suitable_for_meal.append(food)

        # 如果没有足够的食物，使用所有食物
        if len(suitable_for_meal) < count:
            suitable_for_meal = foods

        # 按分数排序
        suitable_for_meal.sort(key=lambda x: x.get("score", 0), reverse=True)

        # 选择前count个
        selected = suitable_for_meal[:count]

        # 构建餐点食物
        meal_foods = []
        for food in selected:
            meal_foods.append(
                {
                    "id": food["id"],
                    "name": food["name"],
                    "portion": self._get_appropriate_portion(food, meal_type),
                    "preparation": self._get_preparation_method(food, meal_type),
                    "benefits": food.get("health_benefits", [])[:2],  # 只显示前两个益处
                }
            )

        return meal_foods

    def _get_appropriate_portion(self, food: dict[str, Any], meal_type: str) -> str:
        """获取适当的食物份量"""
        # 基于食物类型和餐点确定份量
        if "portion_guide" in food:
            if meal_type in food["portion_guide"]:
                return food["portion_guide"][meal_type]
            elif "DEFAULT" in food["portion_guide"]:
                return food["portion_guide"]["DEFAULT"]

        # 默认份量
        if food.get("food_type") == "GRAIN":
            return "1碗" if meal_type in ["BREAKFAST", "LUNCH", "DINNER"] else "少量"
        elif food.get("food_type") == "PROTEIN":
            return "75克" if meal_type in ["LUNCH", "DINNER"] else "30克"
        elif food.get("food_type") == "VEGETABLE":
            return "1份(约150克)" if meal_type in ["LUNCH", "DINNER"] else "半份"
        elif food.get("food_type") == "FRUIT":
            return "1个中等大小" if meal_type == "SNACK" else "半个"
        else:
            return "适量"

    def _get_preparation_method(self, food: dict[str, Any], meal_type: str) -> str:
        """获取食物烹饪方法"""
        # 如果食物有建议的烹饪方法，使用它
        if "recommended_cooking" in food:
            return food["recommended_cooking"]

        # 默认烹饪方法
        if food.get("food_type") == "GRAIN":
            return "煮熟"
        elif food.get("food_type") == "PROTEIN":
            return "清蒸或煮" if meal_type == "BREAKFAST" else "炖或煎"
        elif food.get("food_type") == "VEGETABLE":
            return "生食" if food.get("can_eat_raw", False) else "清炒或蒸"
        elif food.get("food_type") == "FRUIT":
            return "生食"
        else:
            return "适当烹饪"

    def _generate_hydration_recommendation(
        self, constitution_type: str, season: str
    ) -> dict[str, Any]:
        """生成饮水建议"""
        base_water = 1500  # 基础水分摄入量(毫升)

        # 根据体质调整
        if constitution_type == "YANG_DEFICIENCY":
            # 阳虚体质，建议适量温水，少量冷饮
            temp_guide = "温水为主，避免冷饮"
            special_drinks = ["生姜红枣茶", "红糖姜水"]
            additional_ml = 0
        elif constitution_type == "YIN_DEFICIENCY":
            # 阴虚体质，需要更多水分
            temp_guide = "常温水为主，避免过热饮品"
            special_drinks = ["菊花茶", "银耳雪梨汤"]
            additional_ml = 250
        elif constitution_type == "PHLEGM_DAMPNESS":
            # 痰湿体质，控制水分，多喝利水茶饮
            temp_guide = "温水为主，少量多次"
            special_drinks = ["荷叶茶", "薏米水"]
            additional_ml = -250
        elif constitution_type == "DAMP_HEAT":
            # 湿热体质，需要清热利湿
            temp_guide = "常温水为主"
            special_drinks = ["绿豆汤", "菊花茶"]
            additional_ml = 250
        else:
            # 其他体质
            temp_guide = "常温水为主"
            special_drinks = ["清水"]
            additional_ml = 0

        # 根据季节调整
        if season == "SUMMER":
            additional_ml += 500
            note = "夏季出汗多，应适当增加水分摄入"
        elif season == "WINTER":
            additional_ml += 0
            note = "冬季也需保持足够水分摄入，但可减少冷饮"
        else:
            additional_ml += 200
            note = "保持规律饮水习惯，避免口渴时大量饮水"

        # 计算总建议摄入量
        total_ml = base_water + additional_ml

        return {
            "total_daily_ml": total_ml,
            "temperature_guide": temp_guide,
            "recommended_drinks": special_drinks,
            "timing": "餐前30分钟或餐后1小时饮水，避免餐中大量饮水",
            "note": note,
        }

    def _get_diet_principle(self, constitution_type: str) -> str:
        """获取体质饮食原则"""
        principles = {
            "BALANCED": "饮食均衡，五谷为养，五果为助，五畜为益，五菜为充",
            "QI_DEFICIENCY": "饮食宜温，多食补气健脾之品，避免生冷",
            "YANG_DEFICIENCY": "饮食宜温热，食物以温补阳气为主，避免生冷食物",
            "YIN_DEFICIENCY": "饮食宜清润，滋阴润燥为主，避免辛辣温燥之品",
            "PHLEGM_DAMPNESS": "饮食宜清淡，少食多餐，避免油腻甜腻",
            "DAMP_HEAT": "饮食宜清淡，多食清热利湿之品，避免辛辣油腻",
            "BLOOD_STASIS": "饮食宜活血化瘀，多食温通血脉之品，避免寒凉",
            "QI_DEPRESSION": "饮食宜疏肝理气，多食疏肝之品，避免油腻",
            "SPECIAL": "根据个人特质调整，遵医嘱为主",
        }
        return principles.get(constitution_type, "均衡饮食，根据个人体质特点适当调整")

    def _get_focus_nutrients(
        self, constitution_type: str, health_conditions: list[str] | None = None
    ) -> list[dict[str, str]]:
        """获取重点营养素"""
        base_nutrients = []

        # 根据体质添加基础营养素
        if constitution_type == "QI_DEFICIENCY":
            base_nutrients.extend(
                [
                    {"name": "碳水化合物", "reason": "提供能量，改善疲劳"},
                    {"name": "蛋白质", "reason": "修复组织，增强体力"},
                    {"name": "铁", "reason": "促进造血，改善气虚"},
                ]
            )
        elif constitution_type == "YANG_DEFICIENCY":
            base_nutrients.extend(
                [
                    {"name": "优质蛋白", "reason": "提供阳气能量来源"},
                    {"name": "锌", "reason": "促进新陈代谢，增强阳气"},
                    {"name": "维生素E", "reason": "促进血液循环"},
                ]
            )
        elif constitution_type == "YIN_DEFICIENCY":
            base_nutrients.extend(
                [
                    {"name": "优质蛋白", "reason": "滋养阴液"},
                    {"name": "维生素A", "reason": "滋养黏膜，润泽肌肤"},
                    {"name": "钙", "reason": "镇静安神，养阴"},
                ]
            )
        elif constitution_type == "PHLEGM_DAMPNESS":
            base_nutrients.extend(
                [
                    {"name": "膳食纤维", "reason": "促进排毒，减轻痰湿"},
                    {"name": "维生素B群", "reason": "促进代谢，消除水湿"},
                    {"name": "钾", "reason": "平衡体液，利尿消肿"},
                ]
            )
        else:
            base_nutrients.extend(
                [
                    {"name": "膳食纤维", "reason": "促进肠道健康"},
                    {"name": "抗氧化物质", "reason": "抵抗氧化应激"},
                    {"name": "优质蛋白", "reason": "提供必需氨基酸"},
                ]
            )

        # 根据健康状况添加特定营养素
        if health_conditions:
            for condition in health_conditions:
                if condition == "高血压":
                    base_nutrients.append(
                        {"name": "钾", "reason": "平衡钠钾，降低血压"}
                    )
                    base_nutrients.append(
                        {"name": "镁", "reason": "舒张血管，降低血压"}
                    )
                elif condition == "糖尿病":
                    base_nutrients.append({"name": "铬", "reason": "改善胰岛素敏感性"})
                    base_nutrients.append(
                        {"name": "低GI碳水化合物", "reason": "稳定血糖"}
                    )
                elif condition == "贫血":
                    base_nutrients.append({"name": "铁", "reason": "造血必需元素"})
                    base_nutrients.append({"name": "维生素C", "reason": "促进铁吸收"})
                elif condition == "骨质疏松":
                    base_nutrients.append({"name": "钙", "reason": "骨骼基本构成"})
                    base_nutrients.append({"name": "维生素D", "reason": "促进钙吸收"})

        # 去重
        unique_nutrients = []
        unique_names = set()
        for nutrient in base_nutrients:
            if nutrient["name"] not in unique_names:
                unique_nutrients.append(nutrient)
                unique_names.add(nutrient["name"])

        return unique_nutrients

    def _get_top_foods_to_favor(
        self, foods: list[dict[str, Any]], count: int = 5
    ) -> list[dict[str, str]]:
        """获取最适合的食物"""
        # 按评分排序
        sorted_foods = sorted(foods, key=lambda x: x.get("score", 0), reverse=True)

        # 选择前count个
        top_foods = []
        for food in sorted_foods[:count]:
            top_foods.append(
                {"name": food["name"], "reason": food.get("top_benefit", "适合体质")}
            )

        return top_foods

    def _get_foods_to_avoid(self, constitution_type: str) -> list[dict[str, str]]:
        """获取需要避免的食物"""
        avoid_foods = []

        if constitution_type == "QI_DEFICIENCY":
            avoid_foods = [
                {"name": "生冷食物", "reason": "损伤脾胃，加重气虚"},
                {"name": "过甜食物", "reason": "损伤脾胃"},
                {"name": "过于油腻食物", "reason": "增加消化负担"},
            ]
        elif constitution_type == "YANG_DEFICIENCY":
            avoid_foods = [
                {"name": "寒凉食物", "reason": "损伤阳气"},
                {"name": "生冷水果", "reason": "损伤脾胃阳气"},
                {"name": "冷饮", "reason": "损伤脾胃阳气"},
            ]
        elif constitution_type == "YIN_DEFICIENCY":
            avoid_foods = [
                {"name": "辛辣刺激食物", "reason": "耗伤阴液"},
                {"name": "油炸食物", "reason": "助热伤阴"},
                {"name": "烈性酒", "reason": "伤阴助热"},
            ]
        elif constitution_type == "PHLEGM_DAMPNESS":
            avoid_foods = [
                {"name": "精制糖", "reason": "助湿生痰"},
                {"name": "油腻食物", "reason": "增加痰湿"},
                {"name": "乳制品", "reason": "易生痰湿"},
            ]
        elif constitution_type == "DAMP_HEAT":
            avoid_foods = [
                {"name": "辛辣食物", "reason": "助热生湿"},
                {"name": "油炸食物", "reason": "增加湿热"},
                {"name": "酒精", "reason": "加重肝脏负担"},
            ]
        else:
            avoid_foods = [
                {"name": "过度加工食品", "reason": "营养价值低，添加剂多"},
                {"name": "高糖食品", "reason": "增加慢性疾病风险"},
                {"name": "过咸食品", "reason": "增加高血压风险"},
            ]

        return avoid_foods

    def _get_special_notes(
        self,
        constitution_type: str,
        health_conditions: list[str] | None = None,
        allergies: list[str] | None = None,
        medications: list[str] | None = None,
    ) -> list[str]:
        """获取特别注意事项"""
        notes = []

        # 添加体质相关注意事项
        if constitution_type == "QI_DEFICIENCY":
            notes.append("饭后1小时内避免剧烈活动，以免影响消化吸收")
            notes.append("进食定时定量，少食多餐")
        elif constitution_type == "YANG_DEFICIENCY":
            notes.append("食物宜温热，避免生冷，进食时保持愉悦心情")
            notes.append("早晨进食尤为重要，提供一天能量")
        elif constitution_type == "YIN_DEFICIENCY":
            notes.append("晚餐宜清淡，睡前2小时内避免进食")
            notes.append("多选用蒸、煮等烹饪方式，少用煎炸")

        # 添加健康状况相关注意事项
        if health_conditions:
            for condition in health_conditions:
                if condition == "高血压":
                    notes.append("严格控制钠盐摄入，每日不超过6克")
                elif condition == "糖尿病":
                    notes.append("控制碳水化合物总量，避免单纯糖类")
                elif condition == "胃炎":
                    notes.append("定时定量进食，避免过饱或过饥")

        # 添加过敏相关注意事项
        if allergies:
            notes.append(f"严格避免过敏原食物: {', '.join(allergies)}")
            notes.append("查看食品标签，注意隐藏过敏原")

        # 添加药物相关注意事项
        if medications:
            notes.append("服药期间注意药物与食物相互作用，按医嘱服药")

        return notes

    def _get_recipe_constitution_benefits(
        self, recipe: dict[str, Any], constitution_type: str
    ) -> str:
        """获取食谱对特定体质的益处"""
        # 如果食谱已有针对该体质的益处描述，直接返回
        if (
            "constitution_benefits" in recipe
            and constitution_type in recipe["constitution_benefits"]
        ):
            return recipe["constitution_benefits"][constitution_type]

        # 根据食谱特性和体质生成益处描述
        if constitution_type == "QI_DEFICIENCY":
            if "温补" in recipe.get("properties", []):
                return "补气健脾，适合气虚体质食用，增强体力"
            else:
                return "补充营养，有助于改善气虚状态"
        elif constitution_type == "YANG_DEFICIENCY":
            if "温阳" in recipe.get("properties", []):
                return "温补阳气，驱散寒气，提升阳气水平"
            else:
                return "提供能量，改善阳虚症状"
        elif constitution_type == "YIN_DEFICIENCY":
            if "滋阴" in recipe.get("properties", []):
                return "滋阴润燥，适合阴虚体质，改善干燥症状"
            else:
                return "补充营养物质，有助于滋养阴液"
        elif constitution_type == "PHLEGM_DAMPNESS":
            if "化痰" in recipe.get("properties", []) or "祛湿" in recipe.get(
                "properties", []
            ):
                return "健脾化痰，祛湿利水，改善痰湿症状"
            else:
                return "有助于改善体内水湿代谢"
        elif constitution_type == "DAMP_HEAT":
            if "清热" in recipe.get("properties", []) or "利湿" in recipe.get(
                "properties", []
            ):
                return "清热利湿，适合湿热体质，改善湿热症状"
            else:
                return "有助于清理体内湿热"
        else:
            return "均衡营养，适合多种体质食用"


# 单例实例
_food_therapy_manager = None


    @cache(timeout=300)  # 5分钟缓存
def get_food_therapy_manager():
    """获取食疗服务管理器单例"""
    global _food_therapy_manager
    if _food_therapy_manager is None:
        _food_therapy_manager = FoodTherapyManager()
    return _food_therapy_manager
