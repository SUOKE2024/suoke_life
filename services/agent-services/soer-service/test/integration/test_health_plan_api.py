"""
test_health_plan_api - 索克生活项目模块
"""

from fastapi.testclient import TestClient
from internal.delivery.rest import init_rest_app
import os
import sys
import unittest
import uuid

#!/usr/bin/env python3
"""
健康计划API集成测试
"""


# 确保能够导入应用代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))



class TestHealthPlanAPI(unittest.TestCase):
    """健康计划API集成测试"""

    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        # 启动REST应用(不启动实际服务器)
        cls.client = TestClient(init_rest_app())

        # 测试数据
        cls.test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"

        # 测试健康计划请求
        cls.test_plan_request = {
            "user_id": cls.test_user_id,
            "constitution_type": "平和质",
            "health_goals": ["改善睡眠", "增强体质"],
            "health_data": {
                "height": 170,
                "weight": 65,
                "blood_pressure": "120/80",
                "heart_rate": 68,
                "sleep_duration": 7.5,
                "activity_level": "moderate"
            },
            "preferences": {
                "diet_restrictions": ["海鲜", "乳制品"],
                "exercise_preferences": ["瑜伽", "游泳", "步行"]
            },
            "current_season": "春季"
        }

        # 创建一个测试健康计划
        response = cls.client.post(
            "/health-plans/",
            json=cls.test_plan_request
        )
        cls.plan_id = response.json()["plan_id"]

    def test_create_health_plan(self):
        """测试创建健康计划"""
        response = self.client.post(
            "/health-plans/",
            json=self.test_plan_request
        )

        self.assertEqual(response.status_code, 201)

        # 验证响应数据
        data = response.json()
        self.assertIn("plan_id", data)
        self.assertEqual(data["user_id"], self.test_plan_request["user_id"])
        self.assertEqual(data["constitution_type"], self.test_plan_request["constitution_type"])
        self.assertEqual(data["health_goals"], self.test_plan_request["health_goals"])

        # 验证计划内容
        self.assertIn("diet_recommendations", data)
        self.assertIn("exercise_recommendations", data)
        self.assertIn("lifestyle_recommendations", data)
        self.assertIn("supplement_recommendations", data)
        self.assertIn("schedule", data)

        # 检查是否考虑了用户偏好
        diet_recommendations = " ".join(data["diet_recommendations"]).lower()
        self.assertNotIn("海鲜", diet_recommendations)
        self.assertNotIn("乳制品", diet_recommendations)

        # 检查运动推荐是否包含用户偏好
        exercise_recommendations = " ".join(data["exercise_recommendations"]).lower()
        preferences_found = False
        for pref in self.test_plan_request["preferences"]["exercise_preferences"]:
            if pref.lower() in exercise_recommendations:
                preferences_found = True
                break
        self.assertTrue(preferences_found, "运动偏好未被采纳")

        @cache(timeout=300)  # 5分钟缓存
def test_get_health_plan(self):
        """测试获取健康计划"""
        response = self.client.get(
            f"/health-plans/{self.plan_id}",
            params={"user_id": self.test_user_id}
        )

        self.assertEqual(response.status_code, 200)

        # 验证响应数据
        data = response.json()
        self.assertEqual(data["plan_id"], self.plan_id)
        self.assertEqual(data["user_id"], self.test_user_id)

        # 验证计划内容
        self.assertIn("diet_recommendations", data)
        self.assertIn("exercise_recommendations", data)
        self.assertIn("lifestyle_recommendations", data)
        self.assertIn("schedule", data)

    def test_update_health_plan_progress(self):
        """测试更新健康计划进度"""
        progress_request = {
            "user_id": self.test_user_id,
            "plan_id": self.plan_id,
            "completed_items": ["完成30分钟有氧运动", "早餐食用全麦面包和鸡蛋"],
            "progress_notes": "今天感觉不错，完成了运动计划，但水果摄入不足。"
        }

        response = self.client.post(
            "/health-plans/progress",
            json=progress_request
        )

        self.assertEqual(response.status_code, 200)

        # 验证响应数据
        data = response.json()
        self.assertEqual(data["user_id"], self.test_user_id)
        self.assertEqual(data["plan_id"], self.plan_id)
        self.assertIn("progress_percentage", data)
        self.assertIn("next_steps", data)
        self.assertIn("encouragement_message", data)

        # 验证进度
        self.assertGreater(data["progress_percentage"], 0)
        self.assertLessEqual(data["    @cache(timeout=300)  # 5分钟缓存
progress_percentage"], 100)

    def test_invalid_get_health_plan(self):
        """测试无效的健康计划获取请求"""
        # 测试无效的计划ID
        response = self.client.get(
            "/health-plans/invalid_id",
            params={"user_id": self.test_user_id}
        )

        self.assertEqual(response.status_code, 500)

    def test_missing_parameters(self):
        """测试缺少参数的情况"""
        # 缺少必要参数的健康计划请求
        invalid_request = {
            "user_id": self.test_user_id,
            # 缺少体质类型
            "health_goals": ["改善睡眠"]
        }

        response = self.client.post(
            "/health-plans/",
            json=invalid_request
        )

        self.assertEqual(response.status_code, 422)  # 验证请求错误


if __name__ == "__main__":
    unittest.main()
