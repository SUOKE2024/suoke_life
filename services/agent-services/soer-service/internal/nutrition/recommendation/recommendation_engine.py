#!/usr/bin/env python3
"""
营养推荐引擎
基于中医体质理论和现代营养学原理，提供个性化食物推荐
"""

import json
import logging
import os
from typing import Any

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """营养推荐引擎，负责提供个性化食物推荐"""

    def __init__(self):
        """初始化推荐引擎"""
        logger.info("初始化营养推荐引擎")
        self.config = get_config()
        self.food_db = self._load_food_database()
        self.five_elements_foods = self._init_five_elements_foods()
        self.five_tastes_foods = self._init_five_tastes_foods()
        self.constitution_food_rules = self._init_constitution_food_rules()
        logger.info("营养推荐引擎初始化完成")

    def _load_food_database(self) -> dict[str, Any]:
        """加载食物数据库"""
        try:
            food_db_path = self.config.get('nutrition', {}).get('food_db_path', 'config/food_db.json')
            if os.path.exists(food_db_path):
                with open(food_db_path, encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"食物数据库文件 {food_db_path} 不存在，使用内置数据")
                return {}
        except Exception as e:
            logger.error(f"加载食物数据库失败: {str(e)}")
            return {}

    def _init_five_elements_foods(self) -> dict[str, list[str]]:
        """初始化五行食物分类"""
        return {
            "木": ["小麦", "鸡肉", "菠菜", "生菜", "青椒", "西兰花", "柠檬", "青苹果", "猕猴桃", "青梅", "醋"],
            "火": ["玉米", "羊肉", "韭菜", "茴香", "茄子", "红椒", "咖啡", "荔枝", "樱桃", "石榴", "辣椒"],
            "土": ["粳米", "牛肉", "南瓜", "土豆", "胡萝卜", "香菇", "大枣", "香蕉", "菠萝", "龙眼", "甘蔗"],
            "金": ["粟米", "鸭肉", "芥菜", "洋葱", "白萝卜", "莲藕", "梨", "桃子", "杏", "葡萄", "花椒"],
            "水": ["黑米", "猪肉", "黑豆", "海带", "茭白", "冬瓜", "西瓜", "香瓜", "黑枣", "乌梅", "盐"]
        }

    def _init_five_tastes_foods(self) -> dict[str, list[str]]:
        """初始化五味食物分类"""
        return {
            "酸": ["山楂", "柠檬", "番茄", "杨梅", "乌梅", "醋", "酸奶", "芒果", "猕猴桃", "葡萄"],
            "苦": ["苦瓜", "芹菜", "芥菜", "苦菊", "莴苣", "咖啡", "可可", "茶叶", "菊花", "枸杞叶"],
            "甘": ["大米", "小米", "红薯", "土豆", "南瓜", "蜂蜜", "大枣", "白糖", "藕", "葡萄"],
            "辛": ["生姜", "大蒜", "葱", "辣椒", "胡椒", "八角", "桂皮", "茴香", "香菜", "韭菜"],
            "咸": ["海带", "海参", "虾", "海鱼", "紫菜", "海蜇", "盐", "咸菜", "腌制品", "蛤蜊"]
        }

    def _init_constitution_food_rules(self) -> dict[str, dict[str, Any]]:
        """初始化体质食物规则"""
        return {
            "阳虚质": {
                "suitable_elements": ["火", "土"],
                "suitable_tastes": ["辛", "甘"],
                "avoid_elements": ["水"],
                "avoid_tastes": ["酸", "咸"],
                "principles": ["温补阳气", "健脾益肾", "避免生冷"],
                "recommendations": ["羊肉", "牛肉", "生姜", "桂圆", "大枣", "韭菜", "胡桃", "桂皮", "小茴香", "黑米"]
            },
            "阴虚质": {
                "suitable_elements": ["水", "金"],
                "suitable_tastes": ["甘", "酸"],
                "avoid_elements": ["火"],
                "avoid_tastes": ["辛", "苦"],
                "principles": ["滋阴润燥", "清热生津", "避免辛温燥热"],
                "recommendations": ["银耳", "百合", "梨", "莲子", "豆腐", "黑芝麻", "冬瓜", "菠菜", "猪肉", "鸭肉"]
            },
            "气虚质": {
                "suitable_elements": ["土", "金"],
                "suitable_tastes": ["甘", "辛"],
                "avoid_elements": ["木"],
                "avoid_tastes": ["酸", "苦"],
                "principles": ["补气健脾", "益肺和胃", "避免过于寒凉"],
                "recommendations": ["黄豆", "大枣", "山药", "白术", "莲子", "扁豆", "牛肉", "鸡肉", "桂圆", "粳米"]
            },
            "痰湿质": {
                "suitable_elements": ["木", "火"],
                "suitable_tastes": ["苦", "辛"],
                "avoid_elements": ["土", "水"],
                "avoid_tastes": ["甘", "咸"],
                "principles": ["健脾利湿", "化痰消滞", "避免甜腻滋腻"],
                "recommendations": ["薏苡仁", "赤小豆", "冬瓜", "荷叶", "山楂", "萝卜", "绿茶", "丝瓜", "海带", "香菇"]
            },
            "湿热质": {
                "suitable_elements": ["金", "水"],
                "suitable_tastes": ["苦", "甘淡"],
                "avoid_elements": ["火", "土"],
                "avoid_tastes": ["辛", "甘温"],
                "principles": ["清热利湿", "健脾祛湿", "避免辛辣温热"],
                "recommendations": ["绿豆", "苦瓜", "冬瓜", "荷叶", "莲子", "薏苡仁", "赤小豆", "芹菜", "黄瓜", "西瓜"]
            },
            "血瘀质": {
                "suitable_elements": ["木", "火"],
                "suitable_tastes": ["辛", "酸"],
                "avoid_elements": ["土"],
                "avoid_tastes": ["甘滞"],
                "principles": ["活血化瘀", "行气通络", "避免油腻厚味"],
                "recommendations": ["桃仁", "红枣", "黑木耳", "玫瑰花", "醋", "山楂", "胡萝卜", "洋葱", "番茄", "紫葡萄"]
            },
            "气郁质": {
                "suitable_elements": ["木", "火"],
                "suitable_tastes": ["辛", "甘"],
                "avoid_elements": ["金", "水"],
                "avoid_tastes": ["酸", "苦"],
                "principles": ["疏肝解郁", "理气和胃", "避免辛燥助热"],
                "recommendations": ["香橙", "玫瑰花", "柴胡", "薄荷", "佛手", "茉莉花", "青皮", "陈皮", "荷叶", "菊花"]
            },
            "特禀质": {
                "suitable_elements": ["土", "金"],
                "suitable_tastes": ["甘平"],
                "avoid_elements": [],
                "avoid_tastes": [],
                "principles": ["个体化原则", "避免过敏原", "增强免疫力"],
                "recommendations": ["燕麦", "枸杞", "蜂蜜", "木耳", "香菇", "银耳", "莲子", "山药", "百合", "葛根"]
            },
            "平和质": {
                "suitable_elements": ["木", "火", "土", "金", "水"],
                "suitable_tastes": ["酸", "苦", "甘", "辛", "咸"],
                "avoid_elements": [],
                "avoid_tastes": [],
                "principles": ["饮食平衡", "动静结合", "顺应四时"],
                "recommendations": ["糙米", "燕麦", "小米", "豆类", "杂粮", "时令蔬果", "鱼类", "瘦肉", "坚果", "菌菇"]
            }
        }

    def analyze_nutrition(self, user_id: str, food_entries: list[dict[str, Any]],
                         analysis_type: str, constitution_type: str) -> dict[str, Any]:
        """
        分析用户营养摄入情况

        Args:
            user_id: 用户ID
            food_entries: 食物条目列表
            analysis_type: 分析类型，如"daily"、"weekly"、"constitutional"
            constitution_type: 体质类型

        Returns:
            Dict[str, Any]: 营养分析结果
        """
        logger.info(f"分析用户 {user_id} 的营养摄入情况，分析类型: {analysis_type}")

        # 营养素汇总
        nutrient_summary = self._calculate_nutrient_summary(food_entries)

        # 营养素平衡分析
        nutrient_balance = self._analyze_nutrient_balance(nutrient_summary, constitution_type)

        # 五行五味分析
        five_elements_balance, five_tastes_distribution = self._analyze_five_elements_tastes(food_entries)

        # 食物建议
        food_suggestions = self._generate_food_suggestions(
            constitution_type,
            nutrient_balance,
            five_elements_balance,
            five_tastes_distribution
        )

        # 体质分析
        constitutional_analysis = {
            "five_elements_balance": five_elements_balance,
            "five_tastes_distribution": five_tastes_distribution,
            "imbalance_corrections": self._generate_imbalance_corrections(
                constitution_type,
                five_elements_balance,
                five_tastes_distribution
            )
        }

        result = {
            "nutrient_summary": nutrient_summary,
            "balance": nutrient_balance,
            "suggestions": food_suggestions,
            "constitutional_analysis": constitutional_analysis
        }

        logger.info(f"用户 {user_id} 的营养分析完成")
        return result

    def _calculate_nutrient_summary(self, food_entries: list[dict[str, Any]]) -> dict[str, float]:
        """计算营养素摄入汇总"""
        summary = {
            "calories": 0.0,
            "protein": 0.0,
            "fat": 0.0,
            "carbs": 0.0,
            "fiber": 0.0,
            "calcium": 0.0,
            "iron": 0.0,
            "vitamin_a": 0.0,
            "vitamin_c": 0.0,
            "vitamin_e": 0.0
        }

        for entry in food_entries:
            food_name = entry.get("food_name", "")
            quantity = entry.get("quantity", 0.0)

            # 从数据库获取食物营养素含量
            food_data = {}
            if self.food_db and food_name in self.food_db:
                food_data = self.food_db[food_name].get("nutrients", {})

            # 累加营养素
            for nutrient, _value in summary.items():
                if nutrient in food_data:
                    # 按比例计算营养素含量
                    summary[nutrient] += food_data[nutrient] * quantity

        return summary

    def _analyze_nutrient_balance(self, nutrient_summary: dict[str, float],
                                 constitution_type: str) -> list[dict[str, Any]]:
        """分析营养素平衡情况"""
        # 获取参考值
        daily_reference = self.config.get('nutrition', {}).get('daily_reference', {})

        # 根据体质调整参考值
        adjusted_reference = self._adjust_reference_by_constitution(daily_reference, constitution_type)

        # 分析平衡状态
        balance = []
        for nutrient, current in nutrient_summary.items():
            if nutrient in adjusted_reference:
                target = adjusted_reference[nutrient]
                ratio = current / target if target > 0 else 0

                status = "balanced"
                if ratio < 0.7:
                    status = "deficient"
                elif ratio > 1.3:
                    status = "excess"

                balance.append({
                    "nutrient": nutrient,
                    "current": current,
                    "target": target,
                    "status": status
                })

        return balance

    def _adjust_reference_by_constitution(self, reference: dict[str, float],
                                        constitution_type: str) -> dict[str, float]:
        """根据体质调整营养素参考值"""
        adjusted = reference.copy()

        # 根据体质特点调整参考值
        if constitution_type == "阳虚质":
            # 阳虚体质需要更多热量和蛋白质
            adjusted["calories"] = adjusted.get("calories", 2000) * 1.1
            adjusted["protein"] = adjusted.get("protein", 50) * 1.2
        elif constitution_type == "阴虚质":
            # 阴虚体质需要更多水分和维生素
            adjusted["vitamin_e"] = adjusted.get("vitamin_e", 15) * 1.3
            adjusted["vitamin_c"] = adjusted.get("vitamin_c", 100) * 1.2
        elif constitution_type == "气虚质":
            # 气虚体质需要更多碳水和铁质
            adjusted["carbs"] = adjusted.get("carbs", 275) * 1.15
            adjusted["iron"] = adjusted.get("iron", 18) * 1.2
        elif constitution_type == "痰湿质":
            # 痰湿体质需要更少碳水和脂肪
            adjusted["carbs"] = adjusted.get("carbs", 275) * 0.85
            adjusted["fat"] = adjusted.get("fat", 60) * 0.8
            adjusted["fiber"] = adjusted.get("fiber", 25) * 1.3

        return adjusted

    def _analyze_five_elements_tastes(self, food_entries: list[dict[str, Any]]) -> tuple:
        """分析食物的五行五味分布"""
        # 初始化计数器
        elements_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
        tastes_count = {"酸": 0, "苦": 0, "甘": 0, "辛": 0, "咸": 0}

        # 遍历食物条目
        for entry in food_entries:
            food_name = entry.get("food_name", "")

            # 分析五行属性
            for element, foods in self.five_elements_foods.items():
                if food_name in foods:
                    elements_count[element] += 1

            # 分析五味属性
            for taste, foods in self.five_tastes_foods.items():
                if food_name in foods:
                    tastes_count[taste] += 1

        # 转换为百分比
        total_elements = sum(elements_count.values()) or 1  # 避免除以零
        total_tastes = sum(tastes_count.values()) or 1

        elements_balance = {e: count / total_elements for e, count in elements_count.items()}
        tastes_distribution = {t: count / total_tastes for t, count in tastes_count.items()}

        return elements_balance, tastes_distribution

    def _generate_food_suggestions(self, constitution_type: str,
                                  nutrient_balance: list[dict[str, Any]],
                                  five_elements_balance: dict[str, float],
                                  five_tastes_distribution: dict[str, float]) -> list[dict[str, Any]]:
        """生成食物建议"""
        suggestions = []

        # 获取体质食物规则
        rules = self.constitution_food_rules.get(constitution_type, self.constitution_food_rules["平和质"])

        # 添加体质推荐食物
        for food in rules["recommendations"][:5]:  # 最多5个基础推荐
            suggestions.append({
                "food": food,
                "benefits": [f"适合{constitution_type}", "符合体质调理原则"],
                "strength": 0.9,
                "reason": f"根据中医理论，适合{constitution_type}的推荐食物"
            })

        # 根据营养素不足添加建议
        deficient_nutrients = [item for item in nutrient_balance if item["status"] == "deficient"]
        for item in deficient_nutrients[:3]:  # 最多3个营养素建议
            nutrient = item["nutrient"]
            food_candidates = self._find_foods_rich_in(nutrient, constitution_type)

            if food_candidates:
                suggestions.append({
                    "food": food_candidates[0],
                    "benefits": [f"补充{nutrient}", "均衡营养"],
                    "strength": 0.8,
                    "reason": f"您的{nutrient}摄入不足，建议适当增加"
                })

        # 根据五行五味平衡添加建议
        weak_elements = self._find_weak_elements(five_elements_balance)
        if weak_elements:
            element = weak_elements[0]
            element_foods = self._get_element_foods(element, constitution_type)

            if element_foods:
                suggestions.append({
                    "food": element_foods[0],
                    "benefits": [f"平衡{element}行食物", "调和五行"],
                    "strength": 0.7,
                    "reason": f"您的{element}行食物摄入较少，建议适当增加"
                })

        # 确保建议不重复
        unique_suggestions = []
        seen_foods = set()

        for suggestion in suggestions:
            if suggestion["food"] not in seen_foods:
                unique_suggestions.append(suggestion)
                seen_foods.add(suggestion["food"])

        return unique_suggestions[:8]  # 最多返回8个建议

    def _find_foods_rich_in(self, nutrient: str, constitution_type: str) -> list[str]:
        """查找富含特定营养素且符合体质的食物"""
        rich_foods = []
        rules = self.constitution_food_rules.get(constitution_type, {})
        rules.get("suitable_elements", [])
        avoid_elements = rules.get("avoid_elements", [])

        # 示例逻辑，实际应结合完整食物数据库
        if nutrient == "protein":
            candidates = ["鸡胸肉", "豆腐", "鱼肉", "瘦牛肉", "鸡蛋"]
        elif nutrient == "calcium":
            candidates = ["豆腐", "牛奶", "芝麻", "小鱼干", "海带"]
        elif nutrient == "vitamin_c":
            candidates = ["猕猴桃", "柑橘", "西红柿", "青椒", "草莓"]
        elif nutrient == "iron":
            candidates = ["瘦牛肉", "菠菜", "红枣", "黑木耳", "黑豆"]
        elif nutrient == "fiber":
            candidates = ["燕麦", "糙米", "胡萝卜", "苹果", "豆类"]
        else:
            candidates = []

        # 过滤不适合体质的食物
        for food in candidates:
            is_suitable = True

            # 检查是否属于应避免的五行
            for element, foods in self.five_elements_foods.items():
                if food in foods and element in avoid_elements:
                    is_suitable = False
                    break

            if is_suitable:
                rich_foods.append(food)

        return rich_foods

    def _find_weak_elements(self, elements_balance: dict[str, float]) -> list[str]:
        """找出比例较低的五行元素"""
        avg_value = sum(elements_balance.values()) / len(elements_balance)
        threshold = avg_value * 0.7

        weak_elements = [
            element for element, value in elements_balance.items()
            if value < threshold
        ]

        return sorted(weak_elements, key=lambda e: elements_balance[e])

    def _get_element_foods(self, element: str, constitution_type: str) -> list[str]:
        """获取特定五行且适合体质的食物"""
        foods = self.five_elements_foods.get(element, [])

        # 过滤不适合体质的食物
        rules = self.constitution_food_rules.get(constitution_type, {})
        avoid_tastes = rules.get("avoid_tastes", [])

        suitable_foods = []
        for food in foods:
            is_suitable = True

            # 检查是否属于应避免的口味
            for taste, taste_foods in self.five_tastes_foods.items():
                if food in taste_foods and taste in avoid_tastes:
                    is_suitable = False
                    break

            if is_suitable:
                suitable_foods.append(food)

        return suitable_foods

    def _generate_imbalance_corrections(self, constitution_type: str,
                                      five_elements_balance: dict[str, float],
                                      five_tastes_distribution: dict[str, float]) -> list[str]:
        """生成不平衡修正建议"""
        corrections = []
        rules = self.constitution_food_rules.get(constitution_type, {})

        # 分析五行平衡
        weak_elements = self._find_weak_elements(five_elements_balance)
        for element in weak_elements:
            if element in rules["suitable_elements"]:
                corrections.append(f"增加{element}行食物，如{', '.join(self._get_element_foods(element, constitution_type)[:3])}")

        # 分析五味分布
        avg_taste = sum(five_tastes_distribution.values()) / len(five_tastes_distribution)
        for taste, value in five_tastes_distribution.items():
            # 某种口味过少
            if value < avg_taste * 0.7 and taste in rules["suitable_tastes"]:
                taste_foods = list(self.five_tastes_foods.get(taste, [])[:3])
                corrections.append(f"适当增加{taste}味食物，如{', '.join(taste_foods)}")

            # 某种口味过多
            elif value > avg_taste * 1.5 and taste in rules["avoid_tastes"]:
                corrections.append(f"减少{taste}味食物摄入，避免{constitution_type}偏颇加重")

        # 添加体质原则
        principles = rules.get("principles", [])
        if principles:
            corrections.append(f"遵循{constitution_type}饮食原则：{', '.join(principles)}")

        return corrections[:5]  # 最多返回5条建议
