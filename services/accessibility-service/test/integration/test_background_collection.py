#!/usr/bin/env python

"""
后台数据收集服务集成测试
"""

import os
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

# 确保能够导入服务模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from internal.service.background_collection import BackgroundCollectionService

# 测试用户ID
TEST_USER_ID = "user_test_001"
TEST_DEVICE_ID = "device_test_001"


class TestBackgroundCollectionIntegration(unittest.TestCase):
    """后台数据收集服务集成测试类"""

    def setUp(self) -> None:
        """测试前准备"""
        # 创建临时目录用于存储测试数据
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建配置对象
        self.config = SimpleNamespace(
            background_collection=SimpleNamespace(
                enabled=True,
                battery_threshold_low=20,
                battery_threshold_critical=10,
                interval_multiplier_low=2,
                interval_multiplier_critical=4,
                temporary_storage_path=self.temp_dir.name,
            ),
            security=SimpleNamespace(
                encryption=SimpleNamespace(seed="test-encryption-seed")
            ),
        )

        # 创建服务实例
        self.collection_service = BackgroundCollectionService(self.config)

        # 设置模拟电池级别函数
        self.battery_level = 85  # 初始电量85%

        def mock_battery_level() -> None:
            return self.battery_level

        self.collection_service._get_battery_level = mock_battery_level

    def tearDown(self) -> None:
        """测试后清理"""
        # 停止服务
        self.collection_service.stop()

        # 清理临时目录
        self.temp_dir.cleanup()

    def test_configure_background_collection(self) -> None:
        """测试配置后台收集"""
        # 注册用户同意数据采集
        result = self.collection_service.register_user_consent(
            TEST_USER_ID, ["pulse", "sleep", "activity"], expiry_days=30
        )

        # 验证注册成功
        self.assertTrue(result["success"])
        self.assertEqual(result["registered_types"], ["pulse", "sleep", "activity"])

        # 设置采集间隔
        intervals = {
            "pulse": 300,  # 5分钟
            "sleep": 3600,  # 1小时
            "activity": 600,  # 10分钟
        }

        interval_result = self.collection_service.set_collection_interval(
            TEST_USER_ID, intervals
        )
        self.assertTrue(interval_result["success"])

        # 验证用户同意状态
        consent_status = self.collection_service.get_user_consent_status(TEST_USER_ID)
        self.assertTrue(consent_status["has_consent"])
        self.assertEqual(
            set(consent_status["data_types"]), {"pulse", "sleep", "activity"}
        )

    def test_get_collection_status(self) -> None:
        """测试获取收集状态"""
        # 先注册用户同意
        self.collection_service.register_user_consent(
            TEST_USER_ID, ["pulse", "sleep", "activity"]
        )

        # 获取收集状态
        status = self.collection_service.get_collection_status(TEST_USER_ID)

        # 验证响应（根据实际实现的返回格式）
        self.assertIn("is_collecting", status)
        self.assertIn("collecting_types", status)
        self.assertIn("data_points", status)
        self.assertTrue(status["is_collecting"])
        self.assertEqual(
            set(status["collecting_types"]), {"pulse", "sleep", "activity"}
        )

    def test_submit_collected_data(self) -> None:
        """测试提交收集的数据"""
        # 先注册用户同意
        self.collection_service.register_user_consent(
            TEST_USER_ID, ["pulse", "sleep", "activity"]
        )

        # 模拟数据采集
        pulse_data = {
            "pulse_rate": 72,
            "oxygen": 98,
            "timestamp": int(time.time()),
            "confidence": 0.95,
        }

        sleep_data = {
            "duration_hours": 7.5,
            "quality": "good",
            "interruptions": 1,
            "timestamp": int(time.time()) - 3600,
        }

        # 缓存数据
        self.collection_service._cache_data(TEST_USER_ID, "pulse", pulse_data)
        self.collection_service._cache_data(TEST_USER_ID, "sleep", sleep_data)

        # 获取最近的数据
        recent_pulse = self.collection_service.get_recent_data(
            TEST_USER_ID, "pulse", limit=1
        )
        recent_sleep = self.collection_service.get_recent_data(
            TEST_USER_ID, "sleep", limit=1
        )

        # 验证数据已被正确存储
        self.assertTrue(recent_pulse["success"])
        self.assertTrue(recent_sleep["success"])
        self.assertEqual(len(recent_pulse["data"]), 1)
        self.assertEqual(len(recent_sleep["data"]), 1)

    def test_e2e_background_collection_flow(self) -> None:
        """端到端测试后台数据收集流程"""
        # 步骤1: 注册用户同意
        consent_result = self.collection_service.register_user_consent(
            TEST_USER_ID, ["pulse", "sleep", "activity"], expiry_days=30
        )
        self.assertTrue(consent_result["success"])

        # 步骤2: 设置采集间隔
        intervals = {"pulse": 300, "sleep": 3600, "activity": 600}
        interval_result = self.collection_service.set_collection_interval(
            TEST_USER_ID, intervals
        )
        self.assertTrue(interval_result["success"])

        # 步骤3: 启动服务
        self.collection_service.start()
        time.sleep(0.5)  # 等待服务启动

        # 步骤4: 检查收集状态
        status = self.collection_service.get_collection_status(TEST_USER_ID)
        self.assertTrue(status["is_collecting"])

        # 步骤5: 模拟数据采集
        test_data = {
            "pulse": {"pulse_rate": 75, "oxygen": 98},
            "sleep": {"duration_hours": 8, "quality": "excellent"},
            "activity": {"steps": 8500, "calories": 320},
        }

        for data_type, data in test_data.items():
            self.collection_service._cache_data(TEST_USER_ID, data_type, data)

        # 步骤6: 验证数据存储
        for data_type in test_data.keys():
            recent_data = self.collection_service.get_recent_data(
                TEST_USER_ID, data_type, limit=1
            )
            self.assertTrue(recent_data["success"])
            self.assertEqual(len(recent_data["data"]), 1)

        # 步骤7: 测试数据导出
        export_result = self.collection_service.export_user_data(TEST_USER_ID)
        self.assertTrue(export_result["success"])
        self.assertIn("export_data", export_result)  # 实际的字段名是export_data

        # 步骤8: 撤销同意并清理
        revoke_result = self.collection_service.revoke_user_consent(TEST_USER_ID)
        self.assertTrue(revoke_result["success"])

    def test_battery_optimization(self) -> None:
        """测试电池优化功能"""
        # 注册用户同意
        self.collection_service.register_user_consent(
            TEST_USER_ID, ["pulse", "activity"]
        )

        # 设置正常采集间隔
        intervals = {"pulse": 300, "activity": 600}
        self.collection_service.set_collection_interval(TEST_USER_ID, intervals)

        # 测试低电量情况
        self.battery_level = 15  # 低电量
        status = self.collection_service.get_collection_status(TEST_USER_ID)

        # 验证低电量时的优化措施
        self.assertEqual(status["battery_level"], 15)
        self.assertIn("battery_optimization", status)

        # 测试极低电量情况
        self.battery_level = 5  # 极低电量
        status = self.collection_service.get_collection_status(TEST_USER_ID)
        self.assertEqual(status["battery_level"], 5)


if __name__ == "__main__":
    unittest.main()
