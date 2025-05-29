#!/usr/bin/env python3
"""
健康计划生成器
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

class PlanGenerator:
    """健康计划生成器，负责生成个性化健康计划"""

    def __init__(self):
        """初始化计划生成器"""
        logger.info("初始化健康计划生成器")

        # 计划模板
        self.plan_templates = {
            "阳虚质": {
                "diet": [
                    "增加温补食物，如羊肉、牛肉等温性食物",
                    "早晚加餐，增加热量摄入",
                    "少食生冷食物，避免寒凉蔬果",
                    "适量饮用生姜红枣茶、桂圆红枣茶"
                ],
                "exercise": [
                    "选择温和运动，如太极、瑜伽",
                    "避免剧烈运动和大量出汗",
                    "坚持适度锻炼，避免过度疲劳",
                    "晨练时注意保暖，避免受寒"
                ],
                "lifestyle": [
                    "保持居室温暖干燥",
                    "注意腰腹部保暖",
                    "避免久坐吹风",
                    "保持良好睡眠，早睡早起"
                ],
                "supplements": [
                    "西洋参粉",
                    "黄芪",
                    "枸杞子",
                    "桂圆干"
                ]
            },
            "阴虚质": {
                "diet": [
                    "多食滋阴润燥食物，如百合、银耳",
                    "少食辛辣燥热食物",
                    "适量饮用莲子百合羹、麦冬石斛茶",
                    "增加水分摄入，保持充分水分"
                ],
                "exercise": [
                    "选择柔和运动，如游泳、散步",
                    "避免剧烈运动和大量出汗",
                    "适宜傍晚或晚上运动",
                    "可考虑八段锦、易筋经等养生功法"
                ],
                "lifestyle": [
                    "保持居室湿度，避免过于干燥",
                    "保持情绪稳定，避免大喜大悲",
                    "注意适当午休",
                    "避免熬夜，保证充足睡眠"
                ],
                "supplements": [
                    "沙参",
                    "天冬",
                    "石斛",
                    "女贞子"
                ]
            },
            "气虚质": {
                "diet": [
                    "适量增加优质蛋白质，如禽肉、鱼肉",
                    "多食补气食物，如山药、红枣",
                    "少食生冷食物，避免过于寒凉",
                    "三餐规律，适量加餐"
                ],
                "exercise": [
                    "循序渐进进行有氧运动",
                    "避免一次性长时间运动",
                    "适宜打太极拳、气功等养生运动",
                    "重视运动后的休息和恢复"
                ],
                "lifestyle": [
                    "保证充足睡眠，午间小憩",
                    "避免长时间站立或体力劳动",
                    "调整工作和休息节奏",
                    "保持良好心态，避免精神紧张"
                ],
                "supplements": [
                    "太子参",
                    "黄芪",
                    "党参",
                    "白术"
                ]
            },
            "痰湿质": {
                "diet": [
                    "清淡饮食，少食多餐",
                    "减少精制碳水化合物和糖分摄入",
                    "多食祛湿食材，如薏米、赤小豆",
                    "避免油腻、甜腻、寒凉食物"
                ],
                "exercise": [
                    "坚持有氧运动，如快走、慢跑",
                    "适当增加运动强度和时间",
                    "健身操、动感单车等消耗热量的运动",
                    "保持规律运动，每周至少5次"
                ],
                "lifestyle": [
                    "保持居室通风干燥",
                    "避免潮湿环境长时间停留",
                    "保持情绪舒畅，避免郁闷",
                    "避免久坐，保持活动"
                ],
                "supplements": [
                    "茯苓",
                    "陈皮",
                    "藿香",
                    "佩兰"
                ]
            },
            "血瘀质": {
                "diet": [
                    "多食活血化瘀食物，如胡萝卜、洋葱",
                    "增加富含欧米伽3脂肪酸的食物，如深海鱼",
                    "适量饮用玫瑰花茶、红枣茶",
                    "少食油腻、辛辣刺激性食物"
                ],
                "exercise": [
                    "中低强度有氧运动，如散步、慢跑",
                    "太极拳、八段锦等柔和运动",
                    "避免高强度、高冲击力运动",
                    "保持运动频率，每周至少4次"
                ],
                "lifestyle": [
                    "保持情绪稳定，避免暴怒",
                    "保证充足睡眠，避免过度劳累",
                    "避免长时间久坐或站立",
                    "适当按摩，促进血液循环"
                ],
                "supplements": [
                    "丹参",
                    "三七",
                    "红花",
                    "益母草"
                ]
            },
            "特禀质": {
                "diet": [
                    "记录并避免过敏食物",
                    "增加富含维生素C、E和抗氧化物质的食物",
                    "适量补充益生菌食物，增强肠道免疫",
                    "规律进餐，避免暴饮暴食"
                ],
                "exercise": [
                    "选择适合体质的运动方式",
                    "避免在花粉高发季节户外运动",
                    "避免在极端天气条件下运动",
                    "注意运动中的防护措施"
                ],
                "lifestyle": [
                    "保持居室整洁，减少过敏原",
                    "使用防过敏床上用品",
                    "避免接触已知过敏物质",
                    "保持情绪稳定，减少应激反应"
                ],
                "supplements": [
                    "葡萄籽提取物",
                    "螺旋藻",
                    "蜂胶",
                    "维生素C和E"
                ]
            },
            "平和质": {
                "diet": [
                    "均衡饮食，多样化食物摄入",
                    "适量粗粮，增加膳食纤维",
                    "五谷为养，蔬果为辅，荤素搭配",
                    "规律三餐，不暴饮暴食"
                ],
                "exercise": [
                    "多样化运动，如有氧运动、力量训练结合",
                    "保持运动频率，每周3-5次",
                    "适当提高强度，挑战自我",
                    "根据季节调整运动时间和方式"
                ],
                "lifestyle": [
                    "作息规律，早睡早起",
                    "工作学习劳逸结合",
                    "培养积极乐观的心态",
                    "保持社交活动，丰富生活"
                ],
                "supplements": [
                    "通常无需额外补充",
                    "多元维生素矿物质（季节性补充）",
                    "根据生活状态适当调整",
                    "优先从食物中获取营养"
                ]
            }
        }

    def generate_health_plan(self, user_id: str, constitution_type: str,
                          health_goals: list[str], health_data: dict[str, Any],
                          preferences: dict[str, Any] = None) -> dict[str, Any]:
        """
        生成健康计划

        Args:
            user_id: 用户ID
            constitution_type: 体质类型
            health_goals: 健康目标
            health_data: 健康数据
            preferences: 偏好设置

        Returns:
            Dict[str, Any]: 健康计划
        """
        logger.info(f"为用户 {user_id} 生成健康计划，体质类型: {constitution_type}")

        # 确定使用的体质模板
        if constitution_type not in self.plan_templates:
            constitution_type = "平和质"  # 默认使用平和质模板
            logger.warning(f"未找到体质类型 {constitution_type} 的模板，使用平和质模板")

        template = self.plan_templates[constitution_type]

        # 创建基础计划
        plan = {
            "plan_id": str(uuid.uuid4()),
            "user_id": user_id,
            "constitution_type": constitution_type,
            "creation_date": datetime.now().isoformat(),
            "valid_period": {
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=30)).isoformat()
            },
            "health_goals": health_goals,
            "diet_recommendations": template["diet"],
            "exercise_recommendations": template["exercise"],
            "lifestyle_recommendations": template["lifestyle"],
            "supplement_recommendations": template["supplements"],
            "schedule": self._generate_schedule(constitution_type, health_goals, preferences)
        }

        # 根据健康数据调整计划
        self._adjust_plan_based_on_health_data(plan, health_data)

        # 根据偏好调整计划
        if preferences:
            self._adjust_plan_based_on_preferences(plan, preferences)

        logger.info(f"健康计划生成成功，计划ID: {plan['plan_id']}")
        return plan

    def _generate_schedule(self, constitution_type: str, health_goals: list[str],
                        preferences: dict[str, Any] = None) -> dict[str, str]:
        """生成日程安排"""
        # 基础日程
        base_schedule = {
            "早晨": "6:30-7:00 起床，热水泡脚",
            "上午": "9:00-9:30 适量运动",
            "中午": "12:00-12:30 午餐，13:00-13:30 午休",
            "下午": "16:00-16:30 茶歇，补充水分",
            "晚上": "19:00-19:30 晚餐，20:30-21:00 散步",
            "睡前": "22:00-22:30 热水泡脚，放松心情，23:00前睡觉"
        }

        # 根据体质类型调整
        if constitution_type == "阳虚质":
            base_schedule["早晨"] = "7:00-7:30 起床，热姜水泡脚"
            base_schedule["上午"] = "9:30-10:00 太极拳或八段锦"
            base_schedule["睡前"] = "21:30-22:00 热水泡脚，22:30前睡觉"
        elif constitution_type == "阴虚质":
            base_schedule["中午"] = "12:00-12:30 午餐(清淡)，13:00-14:00 午休"
            base_schedule["晚上"] = "18:30-19:00 晚餐(七分饱)，20:00-20:30 缓和散步"

        # 根据健康目标调整
        if "改善睡眠" in health_goals:
            base_schedule["睡前"] = "21:00-21:30 热水泡脚，冥想放松，22:00前睡觉"
        if "减轻压力" in health_goals:
            base_schedule["上午"] = base_schedule["上午"] + "，10:30-10:40 深呼吸练习"
            base_schedule["下午"] = "16:00-16:30 茶歇，正念冥想10分钟"
        if "增强体质" in health_goals:
            base_schedule["早晨"] = base_schedule["早晨"] + "，7:30-8:00 体能训练"

        # 根据偏好调整
        if preferences and "schedule" in preferences:
            for time_slot, pref in preferences["schedule"].items():
                if time_slot in base_schedule:
                    base_schedule[time_slot] = pref

        return base_schedule

    def _adjust_plan_based_on_health_data(self, plan: dict[str, Any], health_data: dict[str, Any]) -> None:
        """根据健康数据调整计划"""
        # 身高体重调整
        if "weight" in health_data and "height" in health_data:
            height_m = health_data["height"] / 100
            bmi = health_data["weight"] / (height_m * height_m)

            if bmi >= 24:
                plan["diet_recommendations"].append("控制总热量摄入，减少精制碳水和糖分")
                plan["exercise_recommendations"].append("增加有氧运动频率，每周至少5次，每次30分钟以上")
            elif bmi < 18.5:
                plan["diet_recommendations"].append("适度增加热量摄入，增加优质蛋白质来源")
                plan["exercise_recommendations"].append("增加力量训练，建议每周3-4次")

        # 血压调整
        if "blood_pressure" in health_data:
            try:
                sys, dia = map(int, health_data["blood_pressure"].split("/"))
                if sys >= 140 or dia >= 90:
                    plan["diet_recommendations"].append("控制钠盐摄入，多食富钾食物")
                    plan["lifestyle_recommendations"].append("定期监测血压，保持情绪稳定")
                    plan["supplement_recommendations"].append("益生菌")
            except:
                pass

        # 心率调整
        if "heart_rate" in health_data:
            heart_rate = health_data["heart_rate"]
            if heart_rate > 100:
                plan["lifestyle_recommendations"].append("增加休息时间，减少咖啡因摄入")
                plan["exercise_recommendations"] = [rec for rec in plan["exercise_recommendations"]
                                                if "剧烈" not in rec and "强度" not in rec]
                plan["exercise_recommendations"].append("选择缓和运动，如散步、太极")

    def _adjust_plan_based_on_preferences(self, plan: dict[str, Any], preferences: dict[str, Any]) -> None:
        """根据偏好调整计划"""
        # 饮食偏好
        if "diet_restrictions" in preferences:
            restrictions = preferences["diet_restrictions"]
            adjusted_diet = []
            for rec in plan["diet_recommendations"]:
                should_keep = True
                for restriction in restrictions:
                    if restriction.lower() in rec.lower():
                        should_keep = False
                        break
                if should_keep:
                    adjusted_diet.append(rec)

            # 确保至少有3条建议
            while len(adjusted_diet) < 3:
                adjusted_diet.append("根据个人体质特点，合理搭配膳食")

            plan["diet_recommendations"] = adjusted_diet

        # 运动偏好
        if "exercise_preferences" in preferences:
            exercise_prefs = preferences["exercise_preferences"]
            for pref in exercise_prefs:
                plan["exercise_recommendations"].append(f"可选择{pref}作为主要运动方式")

            # 保留最多6条建议
            if len(plan["exercise_recommendations"]) > 6:
                plan["exercise_recommendations"] = plan["exercise_recommendations"][:6]
