#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
危机报警服务单元测试
"""

import unittest
import json
import time
import threading
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from types import SimpleNamespace

# 导入被测试模块
from internal.service.crisis_alert import CrisisAlertService


class TestCrisisAlertService(unittest.TestCase):
    """危机报警服务单元测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建配置对象
        self.config = SimpleNamespace(
            crisis_alert=SimpleNamespace(
                enabled=True,
                default_thresholds={
                    "pulse": {
                        "warning": 100,
                        "danger": 120,
                        "critical": 140
                    }
                }
            )
        )
        
        # 创建危机报警服务实例
        self.crisis_service = CrisisAlertService(self.config)
        
        # 创建模拟的后台数据采集服务
        self.mock_background_collection = MagicMock()
        self.mock_background_collection.data_cache = {}
        self.mock_background_collection.user_consents = {
            "test_user": {
                "data_types": set(["pulse", "sleep", "activity"]),
                "expiry": datetime.now() + timedelta(days=30)
            }
        }
        
        # 设置模拟获取采集状态的方法
        def mock_get_status(user_id):
            return {
                "is_collecting": True,
                "collecting_types": ["pulse", "sleep", "activity"]
            }
        self.mock_background_collection.get_collection_status = mock_get_status
        
        # 注入模拟的后台数据采集服务
        self.crisis_service.background_collection_service = self.mock_background_collection
        
        # 创建模拟的通知服务
        self.mock_notification_service = MagicMock()
        self.crisis_service.notification_service = self.mock_notification_service
        
        # 创建模拟的智能体协作服务
        self.mock_agent_coordination = MagicMock()
        self.mock_agent_coordination.event_bus = MagicMock()
        self.crisis_service.agent_coordination = self.mock_agent_coordination
        
        # 创建模拟的监控服务
        self.mock_monitoring_service = MagicMock()
        self.mock_monitoring_service.metrics_client = MagicMock()
        self.crisis_service.monitoring_service = self.mock_monitoring_service

    def tearDown(self):
        """测试后清理"""
        # 停止危机报警服务
        self.crisis_service.stop()

    def test_service_initialization(self):
        """测试服务初始化"""
        self.assertTrue(self.crisis_service.enabled)
        self.assertIsNotNone(self.crisis_service.alert_handlers)
        self.assertIsNotNone(self.crisis_service.data_analyzers)
        self.assertEqual(len(self.crisis_service.alert_handlers), 4)  # info, warning, danger, critical
        self.assertEqual(len(self.crisis_service.data_analyzers), 5)  # pulse, sleep, activity, environment, voice
        
    def test_set_user_thresholds(self):
        """测试设置用户警报阈值"""
        # 测试设置阈值
        thresholds = {
            "pulse": {
                "warning": 110,
                "danger": 130,
                "critical": 150
            },
            "sleep": {
                "warning": 4,
                "danger": 3,
                "critical": 2
            }
        }
        
        result = self.crisis_service.set_user_thresholds("test_user", thresholds)
        
        self.assertTrue(result["success"])
        self.assertEqual(self.crisis_service.alert_thresholds["test_user"]["pulse"]["warning"], 110)
        self.assertEqual(self.crisis_service.alert_thresholds["test_user"]["sleep"]["critical"], 2)
        
    def test_set_emergency_contacts(self):
        """测试设置紧急联系人"""
        contacts = [
            {
                "name": "紧急联系人1",
                "relation": "家人",
                "phone": "13800138001",
                "notify_level": "warning"
            },
            {
                "name": "紧急联系人2",
                "relation": "医生",
                "phone": "13900139002",
                "notify_level": "danger"
            }
        ]
        
        result = self.crisis_service.set_emergency_contacts("test_user", contacts)
        
        self.assertTrue(result["success"])
        self.assertEqual(len(self.crisis_service.alert_contacts["test_user"]), 2)
        self.assertEqual(self.crisis_service.alert_contacts["test_user"][0]["name"], "紧急联系人1")
        self.assertEqual(self.crisis_service.alert_contacts["test_user"][1]["notify_level"], "danger")
        
    def test_get_emergency_contacts(self):
        """测试获取紧急联系人"""
        # 先设置联系人
        contacts = [{"name": "测试联系人", "phone": "13800138000"}]
        self.crisis_service.alert_contacts["test_user"] = contacts
        
        # 获取联系人
        result = self.crisis_service.get_emergency_contacts("test_user")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["contacts"], contacts)
        
        # 测试获取不存在的用户联系人
        result = self.crisis_service.get_emergency_contacts("non_exist_user")
        self.assertFalse(result["success"])
        
    def test_alert_history(self):
        """测试警报历史记录"""
        # 先添加一些历史记录
        self.crisis_service.alert_history["test_user"] = [
            {
                "level": "warning",
                "message": "心率异常",
                "timestamp": datetime.now().isoformat(),
                "data_type": "pulse"
            },
            {
                "level": "info",
                "message": "睡眠不足",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "data_type": "sleep"
            }
        ]
        
        # 获取历史记录
        result = self.crisis_service.get_alert_history("test_user")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["alerts"]), 2)
        # 验证按时间倒序排列
        self.assertEqual(result["alerts"][0]["level"], "warning")
        
        # 测试获取空历史记录
        result = self.crisis_service.get_alert_history("new_user")
        self.assertTrue(result["success"])
        self.assertEqual(len(result["alerts"]), 0)
        
    @patch("internal.service.crisis_alert.threading.Thread")
    def test_start_stop_service(self, mock_thread):
        """测试启动和停止服务"""
        # 模拟线程
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # 启动服务
        self.crisis_service.start()
        
        # 验证线程创建
        self.assertTrue(mock_thread.called)
        self.assertTrue(mock_thread_instance.start.called)
        self.assertFalse(self.crisis_service.stopping)
        
        # 停止服务
        self.crisis_service.stop()
        
        # 验证停止标志设置
        self.assertTrue(self.crisis_service.stopping)
        
    def test_analyze_pulse_data(self):
        """测试脉搏数据分析"""
        # 设置用户阈值
        self.crisis_service.set_user_thresholds("test_user", {
            "pulse": {
                "warning": 100,
                "danger": 120,
                "critical": 140
            }
        })
        
        # 正常数据
        normal_data = {"pulse_rate": 75, "oxygen": 98}
        result = self.crisis_service._analyze_pulse_data("test_user", normal_data, 
                                                       self.crisis_service.alert_thresholds["test_user"]["pulse"])
        self.assertIsNone(result)  # 正常数据不触发警报
        
        # 警告级别数据
        warning_data = {"pulse_rate": 105, "oxygen": 97}
        result = self.crisis_service._analyze_pulse_data("test_user", warning_data,
                                                       self.crisis_service.alert_thresholds["test_user"]["pulse"])
        self.assertIsNotNone(result)
        self.assertEqual(result["level"], "warning")
        
        # 危险级别数据
        danger_data = {"pulse_rate": 125, "oxygen": 94}
        result = self.crisis_service._analyze_pulse_data("test_user", danger_data,
                                                       self.crisis_service.alert_thresholds["test_user"]["pulse"])
        self.assertIsNotNone(result)
        self.assertEqual(result["level"], "danger")
        
        # 严重级别数据
        critical_data = {"pulse_rate": 145, "oxygen": 90}
        result = self.crisis_service._analyze_pulse_data("test_user", critical_data,
                                                       self.crisis_service.alert_thresholds["test_user"]["pulse"])
        self.assertIsNotNone(result)
        self.assertEqual(result["level"], "critical")
        
    def test_process_collected_data(self):
        """测试处理采集数据"""
        # 设置用户阈值
        self.crisis_service.set_user_thresholds("test_user", {
            "pulse": {
                "warning": 100,
                "danger": 120,
                "critical": 140
            }
        })
        
        # 模拟分析函数
        original_analyze = self.crisis_service._analyze_pulse_data
        mock_analyze = MagicMock()
        mock_alert = {
            "level": "warning",
            "message": "检测到心率异常",
            "data_type": "pulse"
        }
        mock_analyze.return_value = mock_alert
        self.crisis_service._analyze_pulse_data = mock_analyze
        
        # 处理数据
        test_data = {"pulse_rate": 110, "oxygen": 96}
        self.crisis_service._process_collected_data("test_user", "pulse", test_data)
        
        # 验证分析函数被调用
        mock_analyze.assert_called_once_with("test_user", test_data, 
                                           self.crisis_service.alert_thresholds["test_user"]["pulse"])
        
        # 恢复原始函数
        self.crisis_service._analyze_pulse_data = original_analyze
        
    def test_alert_handlers(self):
        """测试警报处理器"""
        # 准备测试数据
        alert_info = {
            "level": "warning",
            "message": "检测到心率异常",
            "data_type": "pulse",
            "timestamp": datetime.now().isoformat()
        }
        
        # 测试警告处理器
        self.crisis_service._handle_warning_alert("test_user", alert_info)
        
        # 验证通知服务被调用
        self.mock_notification_service.send_notification.assert_called_once()
        
        # 验证智能体协作被调用
        self.mock_agent_coordination.event_bus.publish.assert_called_once()
        
        # 验证指标被记录
        self.mock_monitoring_service.metrics_client.counter.assert_called_once()

    def test_should_notify_contact(self):
        """测试联系人通知判断"""
        # 各种级别组合测试
        self.assertTrue(self.crisis_service._should_notify_contact("critical", "warning"))
        self.assertTrue(self.crisis_service._should_notify_contact("danger", "danger"))
        self.assertTrue(self.crisis_service._should_notify_contact("critical", "critical"))
        self.assertFalse(self.crisis_service._should_notify_contact("warning", "danger"))
        self.assertFalse(self.crisis_service._should_notify_contact("info", "warning"))
        
    def test_determine_responsible_agent(self):
        """测试确定负责的智能体"""
        # 不同类型的警报分配给不同的智能体
        pulse_alert = {"data_type": "pulse", "level": "warning"}
        self.assertEqual(self.crisis_service._determine_responsible_agent(pulse_alert), "xiaoai")
        
        sleep_alert = {"data_type": "sleep", "level": "warning"}
        self.assertEqual(self.crisis_service._determine_responsible_agent(sleep_alert), "laoke")
        
        activity_alert = {"data_type": "activity", "level": "danger"}
        self.assertEqual(self.crisis_service._determine_responsible_agent(activity_alert), "soer")
        
        # 严重级别总是分配给小艾
        critical_alert = {"data_type": "environment", "level": "critical"}
        self.assertEqual(self.crisis_service._determine_responsible_agent(critical_alert), "xiaoai")


if __name__ == '__main__':
    unittest.main() 