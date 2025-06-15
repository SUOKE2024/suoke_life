#!/usr/bin/env python

"""
危机报警服务集成测试
"""

import os
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# 确保能够导入服务模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# 导入被测试模块
from internal.service.background_collection import BackgroundCollectionService
from internal.service.crisis_alert import CrisisAlertService


class TestCrisisAlertIntegration(unittest.TestCase):
    """危机报警服务集成测试类"""

    def setUp(self) -> None:
        """测试前准备"""
        # 创建临时目录用于存储测试数据
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建配置对象
        self.config = SimpleNamespace(
            crisis_alert=SimpleNamespace(
                enabled=True, temporary_storage_path=self.temp_dir.name
            ),
            background_collection=SimpleNamespace(
                enabled=True,
                battery_threshold_low=20,
                battery_threshold_critical=10,
                interval_multiplier_low=2,
                interval_multiplier_critical=4,
                temporary_storage_path=self.temp_dir.name,
            ),
        )

        # 创建服务实例
        self.background_service = BackgroundCollectionService(self.config)
        self.crisis_service = CrisisAlertService(self.config)

        # 集成两个服务
        self.crisis_service.background_collection_service = self.background_service
        self.background_service.set_crisis_alert_service(self.crisis_service)

        # 创建模拟的通知服务
        self.mock_notification_service = MagicMock()
        self.crisis_service.notification_service = self.mock_notification_service

        # 创建模拟的智能体协作服务
        self.mock_agent_coordination = MagicMock()
        self.mock_agent_coordination.event_bus = MagicMock()
        self.crisis_service.agent_coordination = self.mock_agent_coordination

        # 设置模拟电池级别函数
        self.battery_level = 100  # 初始电量100%

        def mock_battery_level() -> None:
            return self.battery_level

        self.background_service._get_battery_level = mock_battery_level

        # 设置一些测试用户数据
        self.setup_test_user()

    def tearDown(self) -> None:
        """测试后清理"""
        # 停止服务
        self.background_service.stop()
        self.crisis_service.stop()

        # 清理临时目录
        self.temp_dir.cleanup()

    def setup_test_user(self) -> None:
        """设置测试用户数据"""
        # 注册用户同意数据采集
        self.background_service.register_user_consent(
            "test_user", ["pulse", "sleep", "activity"]
        )

        # 设置用户警报阈值
        self.crisis_service.set_user_thresholds(
            "test_user",
            {
                "pulse": {"warning": 100, "danger": 120, "critical": 140},
                "sleep": {
                    "warning": 6,  # 小于6小时
                    "danger": 4,  # 小于4小时
                    "critical": 2,  # 小于2小时
                },
                "activity": {
                    "warning": 500,  # 少于500步/天
                    "danger": 200,  # 少于200步/天
                    "critical": 50,  # 少于50步/天
                },
            },
        )

        # 设置紧急联系人
        self.crisis_service.set_emergency_contacts(
            "test_user",
            [
                {
                    "name": "紧急联系人",
                    "relation": "家人",
                    "phone": "13800138000",
                    "notify_level": "warning",
                }
            ],
        )

    def simulate_data_collection(self, user_id, data_type, data):
        """模拟数据采集"""
        # 直接调用数据处理方法，模拟数据采集
        self.background_service._cache_data(user_id, data_type, data)

    def test_service_integration(self) -> None:
        """测试服务集成"""
        # 启动服务
        self.background_service.start()
        self.crisis_service.start()

        # 等待服务完全启动
        time.sleep(0.5)

        # 验证服务集成状态
        self.assertEqual(
            self.background_service.crisis_alert_service, self.crisis_service
        )
        self.assertEqual(
            self.crisis_service.background_collection_service, self.background_service
        )

        # 停止服务并验证
        self.background_service.stop()
        self.crisis_service.stop()

        self.assertTrue(self.background_service.stopping)
        self.assertTrue(self.crisis_service.stopping)

    def test_normal_data_no_alert(self) -> None:
        """测试正常数据不触发警报"""
        # 采集正常脉搏数据
        normal_pulse = {"pulse_rate": 75, "oxygen": 98}
        self.simulate_data_collection("test_user", "pulse", normal_pulse)

        # 采集正常睡眠数据
        normal_sleep = {"duration_hours": 7.5, "quality": "good", "interruptions": 1}
        self.simulate_data_collection("test_user", "sleep", normal_sleep)

        # 验证没有警报生成
        self.assertEqual(len(self.crisis_service.alert_history.get("test_user", [])), 0)

        # 验证通知服务没有被调用
        self.mock_notification_service.send_notification.assert_not_called()

    def test_warning_level_alert(self) -> None:
        """测试警告级别警报"""
        # 采集异常脉搏数据
        warning_pulse = {"pulse_rate": 105, "oxygen": 96}
        self.simulate_data_collection("test_user", "pulse", warning_pulse)

        # 给处理警报的时间
        time.sleep(0.5)

        # 验证警报生成
        alerts = self.crisis_service.alert_history.get("test_user", [])
        self.assertGreaterEqual(len(alerts), 1)

        # 验证警报级别
        latest_alert = alerts[-1]
        self.assertEqual(latest_alert["level"], "warning")
        self.assertEqual(latest_alert["data_type"], "pulse")

        # 验证通知服务被调用
        self.mock_notification_service.send_notification.assert_called()

        # 验证智能体协作被调用
        self.mock_agent_coordination.event_bus.publish.assert_called()

    def test_danger_level_alert(self) -> None:
        """测试危险级别警报"""
        # 采集非常异常的脉搏数据
        danger_pulse = {"pulse_rate": 125, "oxygen": 93}
        self.simulate_data_collection("test_user", "pulse", danger_pulse)

        # 给处理警报的时间
        time.sleep(0.5)

        # 验证警报生成
        alerts = self.crisis_service.alert_history.get("test_user", [])
        self.assertGreaterEqual(len(alerts), 1)

        # 验证警报级别
        latest_alert = alerts[-1]
        self.assertEqual(latest_alert["level"], "danger")
        self.assertEqual(latest_alert["data_type"], "pulse")

    def test_multiple_data_types(self) -> None:
        """测试多种数据类型警报"""
        # 采集异常睡眠数据
        warning_sleep = {"duration_hours": 5.5, "quality": "poor", "interruptions": 4}
        self.simulate_data_collection("test_user", "sleep", warning_sleep)

        # 采集异常活动数据
        warning_activity = {"steps": 450, "active_minutes": 25, "calories": 200}
        self.simulate_data_collection("test_user", "activity", warning_activity)

        # 给处理警报的时间
        time.sleep(1.0)

        # 验证警报生成
        alerts = self.crisis_service.alert_history.get("test_user", [])
        self.assertGreaterEqual(len(alerts), 2)  # 至少两个警报

        # 验证警报类型
        alert_types = [alert["data_type"] for alert in alerts]
        self.assertIn("sleep", alert_types)
        self.assertIn("activity", alert_types)

    def test_critical_alert_emergency_contacts(self) -> None:
        """测试严重警报时通知紧急联系人"""
        # 重写notify_emergency_contacts方法进行监控
        original_notify = self.crisis_service._notify_emergency_contacts
        notify_mock = MagicMock()
        self.crisis_service._notify_emergency_contacts = notify_mock

        # 采集严重异常的脉搏数据
        critical_pulse = {"pulse_rate": 150, "oxygen": 89}
        self.simulate_data_collection("test_user", "pulse", critical_pulse)

        # 给处理警报的时间
        time.sleep(0.5)

        # 验证警报生成
        alerts = self.crisis_service.alert_history.get("test_user", [])
        self.assertGreaterEqual(len(alerts), 1)

        # 验证警报级别
        latest_alert = alerts[-1]
        self.assertEqual(latest_alert["level"], "critical")

        # 验证紧急联系人通知被调用
        notify_mock.assert_called()

        # 恢复原方法
        self.crisis_service._notify_emergency_contacts = original_notify

    def test_battery_optimization(self) -> None:
        """测试电池优化对数据采集和警报的影响"""
        # 采集正常数据设置基线
        self.battery_level = 100  # 充足电量
        normal_pulse = {"pulse_rate": 75, "oxygen": 98}
        self.simulate_data_collection("test_user", "pulse", normal_pulse)

        # 设置低电量
        self.battery_level = 15  # 低电量

        # 检查采集间隔是否根据电池电量调整
        # 这里无法直接测量采集间隔，但可以检查采集线程睡眠时间逻辑
        if hasattr(self.background_service, "_collection_worker"):
            # 修改_collection_worker方法记录睡眠时间
            original_worker = self.background_service._collection_worker
            self.sleep_times = []

            def mock_time_sleep(seconds):
                self.sleep_times.append(seconds)
                # 不实际睡眠，加快测试
                return

            with patch("time.sleep", side_effect=mock_time_sleep):
                # 启动一个短时间的采集任务
                thread = threading.Thread(
                    target=self.background_service._collection_worker,
                    args=("test_user2",),
                    daemon=True,
                )
                # 注册用户，这样线程不会立即退出
                self.background_service.user_consents["test_user2"] = {
                    "data_types": {"pulse"},
                    "expiry": datetime.now() + timedelta(days=30),
                }
                thread.start()

                # 等待几次循环
                time.sleep(0.5)

                # 停止用户同意，使线程退出
                del self.background_service.user_consents["test_user2"]

                # 等待线程结束
                time.sleep(0.5)

                # 验证电池优化 - 睡眠时间应该增加
                if self.sleep_times:
                    self.assertGreater(
                        max(self.sleep_times), 10
                    )  # 低电量时睡眠时间应大于默认的10秒

    def test_long_term_data_trend_alert(self) -> None:
        """测试长期数据趋势警报"""
        # 模拟一周的睡眠数据，逐渐变差
        for day in range(7):
            hours = 8.0 - (day * 0.5)  # 从8小时逐渐减少到5小时
            sleep_data = {
                "duration_hours": hours,
                "quality": "deteriorating",
                "day": day,
            }
            self.simulate_data_collection("test_user", "sleep", sleep_data)

        # 最后一天严重不足的睡眠
        critical_sleep = {"duration_hours": 3.5, "quality": "very_poor", "day": 7}
        self.simulate_data_collection("test_user", "sleep", critical_sleep)

        # 给处理警报的时间
        time.sleep(0.5)

        # 验证警报生成
        alerts = [
            a
            for a in self.crisis_service.alert_history.get("test_user", [])
            if a["data_type"] == "sleep"
        ]
        self.assertGreaterEqual(len(alerts), 1)

        # 验证最后一次警报级别至少是警告
        latest_sleep_alert = alerts[-1]
        self.assertIn(latest_sleep_alert["level"], ["warning", "danger", "critical"])


if __name__ == "__main__":
    unittest.main()
