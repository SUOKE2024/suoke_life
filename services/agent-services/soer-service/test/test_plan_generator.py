#!/usr/bin/env python3
"""
健康计划生成器测试
"""
import json
import os
import sys
import unittest

# 确保能够导入应用代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.lifecycle.plan_generator.plan_generator import PlanGenerator


class TestPlanGenerator(unittest.TestCase):
    """健康计划生成器测试"""

    def setUp(self):
        """设置测试环境"""
        self.plan_generator = PlanGenerator()

        # 测试用户数据
        self.user_id = "test_user_001"

        # 模拟健康数据
        self.health_data = {
            "height": 170,
            "weight": 65,
            "blood_pressure": "120/80",
            "heart_rate": 68,
            "sleep_duration": 7.5,
            "activity_level": "moderate"
        }

        # 用户偏好
        self.preferences = {
            "diet_restrictions": ["海鲜", "乳制品"],
            "exercise_preferences": ["瑜伽", "游泳", "步行"],
            "schedule": {
                "早晨": "6:00-6:30 起床，热水泡脚",
                "睡前": "22:00 热水泡脚，22:30 睡觉"
            }
        }

        # 各种体质类型
        self.constitution_types = [
            "阳虚质", "阴虚质", "气虚质", "痰湿质",
            "湿热质", "血瘀质", "气郁质", "特禀质", "平和质"
        ]

        # 健康目标
        self.health_goals = ["改善睡眠", "增强体质", "减轻压力"]

    def test_generate_health_plan_default(self):
        """测试默认健康计划生成"""
        plan = self.plan_generator.generate_health_plan(
            self.user_id,
            "平和质",
            self.health_goals,
            self.health_data
        )

        # 基础断言
        self.assertIsNotNone(plan)
        self.assertEqual(plan["user_id"], self.user_id)
        self.assertEqual(plan["constitution_type"], "平和质")
        self.assertEqual(plan["health_goals"], self.health_goals)
        self.assertIn("plan_id", plan)
        self.assertIn("creation_date", plan)

        # 检查核心内容
        self.assertIn("diet_recommendations", plan)
        self.assertIn("exercise_recommendations", plan)
        self.assertIn("lifestyle_recommendations", plan)
        self.assertIn("supplement_recommendations", plan)
        self.assertIn("schedule", plan)

        # 检查内容长度
        self.assertGreater(len(plan["diet_recommendations"]), 0)
        self.assertGreater(len(plan["exercise_recommendations"]), 0)
        self.assertGreater(len(plan["lifestyle_recommendations"]), 0)

    def test_generate_health_plan_with_preferences(self):
        """测试包含用户偏好的健康计划生成"""
        plan = self.plan_generator.generate_health_plan(
            self.user_id,
            "气虚质",
            self.health_goals,
            self.health_data,
            self.preferences
        )

        # 检查偏好是否被处理
        diet_recommendations = " ".join(plan["diet_recommendations"])
        self.assertNotIn("海鲜", diet_recommendations.lower())
        self.assertNotIn("乳制品", diet_recommendations.lower())

        # 检查运动偏好是否被应用
        exercise_recommendations = " ".join(plan["exercise_recommendations"])
        # 至少一个偏好应该被采纳
        preferences_found = False
        for pref in self.preferences["exercise_preferences"]:
            if pref.lower() in exercise_recommendations.lower():
                preferences_found = True
                break
        self.assertTrue(preferences_found, "运动偏好未被采纳")

        # 检查日程表是否采纳了用户偏好
        schedule = plan["schedule"]
        self.assertEqual(schedule["早晨"], self.preferences["schedule"]["早晨"])
        self.assertEqual(schedule["睡前"], self.preferences["schedule"]["睡前"])

    def test_health_data_adjustment(self):
        """测试健康数据调整功能"""
        # 测试超重情况
        overweight_data = self.health_data.copy()
        overweight_data["height"] = 170
        overweight_data["weight"] = 90  # BMI约为31.14，属于肥胖

        plan = self.plan_generator.generate_health_plan(
            self.user_id,
            "平和质",
            self.health_goals,
            overweight_data
        )

        # 检查是否有针对体重的饮食建议
        diet_recommendations = " ".join(plan["diet_recommendations"])
        weight_related_terms = ["控制热量", "减少", "控制", "碳水", "糖分"]
        weight_adjustment_found = False
        for term in weight_related_terms:
            if term in diet_recommendations:
                weight_adjustment_found = True
                break
        self.assertTrue(weight_adjustment_found, "没有针对超重的饮食建议")

        # 检查是否有增加运动的建议
        exercise_recommendations = " ".join(plan["exercise_recommendations"])
        exercise_related_terms = ["增加", "有氧", "频率"]
        exercise_adjustment_found = False
        for term in exercise_related_terms:
            if term in exercise_recommendations:
                exercise_adjustment_found = True
                break
        self.assertTrue(exercise_adjustment_found, "没有针对超重的运动建议")

    def test_constitution_specific_recommendations(self):
        """测试不同体质类型生成的健康计划差异"""
        plans = {}

        # 为每种体质生成计划
        for constitution_type in self.constitution_types:
            plans[constitution_type] = self.plan_generator.generate_health_plan(
                self.user_id,
                constitution_type,
                self.health_goals,
                self.health_data
            )

        # 检查阳虚质和阴虚质的计划差异
        yang_deficiency_diet = " ".join(plans["阳虚质"]["diet_recommendations"])
        yin_deficiency_diet = " ".join(plans["阴虚质"]["diet_recommendations"])

        # 阳虚质应该有温补建议
        warm_terms = ["温补", "温热", "温性", "姜", "桂", "羊肉"]
        warm_found = False
        for term in warm_terms:
            if term in yang_deficiency_diet:
                warm_found = True
                break
        self.assertTrue(warm_found, "阳虚质没有温补建议")

        # 阴虚质应该有滋阴建议
        cool_terms = ["滋阴", "润燥", "清热", "生津", "百合", "银耳", "梨"]
        cool_found = False
        for term in cool_terms:
            if term in yin_deficiency_diet:
                cool_found = True
                break
        self.assertTrue(cool_found, "阴虚质没有滋阴建议")

        # 检查痰湿质和湿热质的差异
        phlegm_damp_diet = " ".join(plans["痰湿质"]["diet_recommendations"])
        damp_heat_diet = " ".join(plans["湿热质"]["diet_recommendations"])

        # 痰湿质应该避免甜腻
        phlegm_terms = ["健脾", "化痰", "祛湿", "避免甜腻", "薏苡仁", "赤小豆"]
        phlegm_found = False
        for term in phlegm_terms:
            if term in phlegm_damp_diet:
                phlegm_found = True
                break
        self.assertTrue(phlegm_found, "痰湿质没有化痰祛湿建议")

        # 湿热质应该有清热利湿
        damp_heat_terms = ["清热", "利湿", "苦瓜", "绿豆", "冬瓜"]
        damp_heat_found = False
        for term in damp_heat_terms:
            if term in damp_heat_diet:
                damp_heat_found = True
                break
        self.assertTrue(damp_heat_found, "湿热质没有清热利湿建议")

    def test_plan_schedule_generation(self):
        """测试日程安排生成"""
        plan = self.plan_generator.generate_health_plan(
            self.user_id,
            "平和质",
            ["改善睡眠"],  # 只有睡眠目标
            self.health_data
        )

        # 检查日程安排是否包含必要的时间段
        schedule = plan["schedule"]

        self.assertIn("早晨", schedule)
        self.assertIn("上午", schedule)
        self.assertIn("中午", schedule)
        self.assertIn("下午", schedule)
        self.assertIn("晚上", schedule)
        self.assertIn("睡前", schedule)

        # 检查睡眠目标是否反映在日程中
        sleep_related_terms = ["睡眠", "就寝", "睡觉", "放松", "冥想"]
        sleep_recommendations_found = False

        for term in sleep_related_terms:
            if term in schedule["睡前"]:
                sleep_recommendations_found = True
                break

        self.assertTrue(sleep_recommendations_found, "睡前时间没有针对睡眠的建议")

    def test_plan_serialization(self):
        """测试计划序列化为JSON"""
        plan = self.plan_generator.generate_health_plan(
            self.user_id,
            "平和质",
            self.health_goals,
            self.health_data
        )

        # 尝试序列化为JSON
        try:
            plan_json = json.dumps(plan, ensure_ascii=False)
            # 反序列化检查
            loaded_plan = json.loads(plan_json)
            self.assertEqual(loaded_plan["user_id"], self.user_id)
        except Exception as e:
            self.fail(f"计划序列化失败: {str(e)}")


if __name__ == "__main__":
    unittest.main()
