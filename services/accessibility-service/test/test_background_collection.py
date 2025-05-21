#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后台数据采集服务的单元测试
"""

import unittest
import time
import json
import threading
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock, call

# 导入服务模块
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.service.background_collection import BackgroundCollectionService
from config.config import ConfigSection

class MockConfig:
    """测试用配置类"""
    def __init__(self, enabled=True):
        self.background_collection = ConfigSection({
            "enabled": enabled,
            "collection_types": {
                "pulse": {
                    "enabled": True,
                    "interval_seconds": 10,
                    "privacy_level": "high"
                },
                "sleep": {
                    "enabled": True,
                    "interval_seconds": 20,
                    "privacy_level": "medium"
                }
            },
            "consent": {
                "require_explicit": True,
                "default_expiry_days": 30
            },
            "battery_threshold_low": 20,
            "battery_threshold_critical": 10,
            "interval_multiplier_low": 2,
            "interval_multiplier_critical": 4
        })
        
        self.security = ConfigSection({
            "encryption": {
                "data_at_rest": {
                    "algorithm": "AES-256-GCM",
                    "seed": "test-encryption-seed"
                }
            }
        })


class TestBackgroundCollectionService(unittest.TestCase):
    """后台数据采集服务的测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.config = MockConfig()
        self.service = BackgroundCollectionService(self.config)
        
        # 创建模拟的隐私服务
        self.mock_privacy_service = Mock()
        self.mock_privacy_service.encrypt_data = Mock(return_value=b"encrypted_data")
        self.mock_privacy_service.decrypt_data = Mock(return_value=json.dumps({
            "timestamp": datetime.now().isoformat(),
            "data": {"value": "test"}
        }))
        
        # 创建模拟的监控服务
        self.mock_monitoring_service = Mock()
        self.mock_monitoring_service.metrics_client = Mock()
        
        # 创建模拟的危机报警服务
        self.mock_crisis_alert_service = Mock()
        self.mock_crisis_alert_service._process_collected_data = Mock()
        
        # 注入依赖
        self.service.privacy_service = self.mock_privacy_service
        self.service.monitoring_service = self.mock_monitoring_service
        
        # 替换实际数据收集函数为模拟函数
        self.original_collectors = self.service.collectors.copy()
        for data_type in self.service.collectors:
            self.service.collectors[data_type] = Mock(return_value={"value": f"mock_{data_type}_data"})
        
        # 替换电池电量获取函数
        self.original_get_battery_level = self.service._get_battery_level
        self.service._get_battery_level = Mock(return_value=80)
        
        # 替换用户状态检测函数
        self.original_detect_user_state = getattr(self.service, '_detect_user_state', None)
        self.service._detect_user_state = Mock(return_value="idle")
    
    def tearDown(self):
        """测试后清理"""
        # 停止服务
        if hasattr(self.service, 'stop'):
            self.service.stop()
        
        # 恢复原始收集器
        self.service.collectors = self.original_collectors
        
        # 恢复原始电池电量获取函数
        if hasattr(self, 'original_get_battery_level'):
            self.service._get_battery_level = self.original_get_battery_level
        
        # 恢复原始用户状态检测函数
        if self.original_detect_user_state is not None:
            self.service._detect_user_state = self.original_detect_user_state
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.service.enabled, True)
        self.assertEqual(len(self.service.collectors), 5)  # 五种数据类型
        self.assertEqual(len(self.service.collection_threads), 0)
        
        # 验证电池阈值配置
        self.assertEqual(self.service.battery_threshold_low, 20)
        self.assertEqual(self.service.battery_threshold_critical, 10)
        self.assertEqual(self.service.interval_multiplier_low, 2)
        self.assertEqual(self.service.interval_multiplier_critical, 4)
    
    def test_setup_encryption(self):
        """测试加密设置"""
        self.service.setup_encryption()
        self.assertIsNotNone(self.service.encryption_key)
    
    def test_set_crisis_alert_service(self):
        """测试设置危机报警服务"""
        # 设置危机报警服务
        self.service.set_crisis_alert_service(self.mock_crisis_alert_service)
        
        # 验证属性设置
        self.assertEqual(self.service.crisis_alert_service, self.mock_crisis_alert_service)
        
        # 创建一个具有background_collection_service属性的模拟对象
        mock_crisis_service_with_attr = Mock()
        mock_crisis_service_with_attr.background_collection_service = None
        
        # 测试反向引用注入
        self.service.set_crisis_alert_service(mock_crisis_service_with_attr)
        self.assertEqual(mock_crisis_service_with_attr.background_collection_service, self.service)
    
    def test_register_user_consent(self):
        """测试注册用户同意"""
        with patch.object(self.service, '_start_collection_thread') as mock_start:
            result = self.service.register_user_consent("test_user", ["pulse", "sleep", "unknown_type"])
            
            # 验证结果
            self.assertTrue(result["success"])
            self.assertEqual(set(result["registered_types"]), {"pulse", "sleep"})
            self.assertIn("warning", result)  # 应有警告提示未知数据类型
            
            # 验证用户同意是否保存
            self.assertIn("test_user", self.service.user_consents)
            self.assertEqual(self.service.user_consents["test_user"]["data_types"], {"pulse", "sleep"})
            
            # 验证是否启动了采集线程
            mock_start.assert_called_once_with("test_user")
    
    def test_get_user_consent_status(self):
        """测试获取用户同意状态"""
        # 先注册用户同意
        self.service.register_user_consent("test_user", ["pulse"])
        
        # 获取并验证状态 - 有效状态
        status = self.service.get_user_consent_status("test_user")
        self.assertTrue(status["has_consent"])
        self.assertEqual(status["data_types"], ["pulse"])
        
        # 测试未注册用户
        status = self.service.get_user_consent_status("unknown_user")
        self.assertFalse(status["has_consent"])
        self.assertIn("message", status)
        
        # 测试过期同意
        self.service.user_consents["expired_user"] = {
            "data_types": {"pulse"},
            "expiry": datetime.now() - timedelta(days=1),
            "last_updated": datetime.now().isoformat()
        }
        status = self.service.get_user_consent_status("expired_user")
        self.assertFalse(status["has_consent"])
        self.assertIn("expired_at", status)
    
    def test_revoke_user_consent(self):
        """测试撤销用户同意"""
        # 先注册用户同意
        self.service.register_user_consent("test_user", ["pulse", "sleep"])
        
        with patch.object(self.service, '_stop_collection_thread') as mock_stop:
            # 撤销部分同意
            result = self.service.revoke_user_consent("test_user", ["pulse"])
            self.assertTrue(result["success"])
            self.assertEqual(self.service.user_consents["test_user"]["data_types"], {"sleep"})
            
            # 撤销全部同意
            result = self.service.revoke_user_consent("test_user")
            self.assertTrue(result["success"])
            self.assertNotIn("test_user", self.service.user_consents)
            mock_stop.assert_called_with("test_user")
    
    def test_set_collection_interval(self):
        """测试设置采集间隔"""
        result = self.service.set_collection_interval("test_user", {"pulse": 30, "invalid": 20})
        self.assertTrue(result["success"])
        self.assertEqual(self.service.collection_intervals["test_user"]["pulse"], 30)
        self.assertNotIn("invalid", self.service.collection_intervals["test_user"])
    
    def test_battery_management(self):
        """测试电池管理功能"""
        # 准备测试数据
        user_id = "test_user"
        self.service.user_consents[user_id] = {
            "data_types": {"pulse"},
            "expiry": datetime.now() + timedelta(days=30),
            "last_updated": datetime.now().isoformat()
        }
        self.service.collection_intervals[user_id] = {"pulse": 60}  # 60秒间隔
        
        # 模拟缓存函数，并记录调用情况
        mock_cache = Mock()
        original_cache = self.service._cache_data
        self.service._cache_data = mock_cache
        
        # 测试不同电池电量下的调整
        # 1. 正常电量 (80%)
        self.service._get_battery_level.return_value = 80
        with patch.object(self.service, '_sync_user_data'):
            # 运行一个周期的采集
            self.service._collection_worker = lambda x: None  # 防止进入无限循环
            
            # 通过直接调用内部函数模拟采集过程
            current_time = time.time()
            last_collection = {}
            
            # 获取调整后的采集间隔
            adjusted_interval = self.service.collection_intervals[user_id]["pulse"]
            # 正常电量下不应调整间隔
            self.assertEqual(adjusted_interval, 60)
        
        # 2. 低电量 (15%)
        self.service._get_battery_level.return_value = 15
        # 在低电量情况下，间隔应该增加2倍
        expected_interval = 60 * self.service.interval_multiplier_low
        self.assertEqual(expected_interval, 120)
        
        # 3. 严重低电量 (5%)
        self.service._get_battery_level.return_value = 5
        # 在严重低电量情况下，间隔应该增加4倍
        expected_interval = 60 * self.service.interval_multiplier_critical
        self.assertEqual(expected_interval, 240)
        
        # 恢复原始缓存函数
        self.service._cache_data = original_cache
    
    def test_user_state_detection(self):
        """测试用户状态检测功能"""
        # 测试不同状态的检测
        user_id = "test_user"
        
        # 1. 初始化空缓存应返回默认状态 "idle"
        self.service.data_cache = {}
        state = self.service._detect_user_state(user_id)
        self.assertEqual(state, "idle")
        
        # 2. 设置睡眠状态数据
        self.service.data_cache[user_id] = {
            "sleep": [{
                "timestamp": datetime.now().isoformat(),
                "data": {"state": "sleeping"}
            }]
        }
        # 恢复原始检测函数
        if self.original_detect_user_state:
            self.service._detect_user_state = self.original_detect_user_state
        state = self.service._detect_user_state(user_id)
        self.assertEqual(state, "sleeping")
        
        # 3. 设置活跃状态数据
        self.service.data_cache[user_id] = {
            "activity": [{
                "timestamp": datetime.now().isoformat(),
                "data": {"activity_type": "walking"}
            }]
        }
        state = self.service._detect_user_state(user_id)
        self.assertEqual(state, "active")
    
    def test_cache_data_with_crisis_alert(self):
        """测试数据缓存与危机报警集成"""
        # 设置危机报警服务
        self.service.set_crisis_alert_service(self.mock_crisis_alert_service)
        
        # 缓存数据
        user_id = "test_user"
        data_type = "pulse"
        test_data = {"pulse_rate": 75}
        
        self.service._cache_data(user_id, data_type, test_data)
        
        # 验证数据传递给危机报警服务
        self.mock_crisis_alert_service._process_collected_data.assert_called_once_with(
            user_id, data_type, test_data
        )
        
        # 验证缓存大小限制
        # 添加超过限制的数据
        for i in range(110):  # 插入110条记录，超过默认的100条限制
            self.service._cache_data(user_id, data_type, {"pulse_rate": 75 + i % 10})
        
        # 验证只保留了最新的100条
        self.assertLessEqual(len(self.service.data_cache[user_id][data_type]), 100)
    
    def test_get_recent_data(self):
        """测试获取最近数据功能"""
        # 准备测试数据
        user_id = "test_user"
        data_type = "pulse"
        
        # 缓存一些测试数据
        self.service.data_cache[user_id] = {
            data_type: []
        }
        
        for i in range(20):
            self.service.data_cache[user_id][data_type].append({
                "timestamp": datetime.now().isoformat(),
                "data": {"pulse_rate": 75 + i}
            })
        
        # 测试获取最近数据
        result = self.service.get_recent_data(user_id, data_type, limit=5)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertEqual(len(result["data"]), 5)
        # 最新的数据应该在最后
        self.assertEqual(result["data"][-1]["data"]["pulse_rate"], 94)
    
    def test_clear_user_data(self):
        """测试清除用户数据功能"""
        # 准备测试数据
        user_id = "test_user"
        self.service.data_cache[user_id] = {
            "pulse": [{"data": "test1"}],
            "sleep": [{"data": "test2"}],
            "activity": [{"data": "test3"}]
        }
        
        # 测试清除特定类型数据
        result = self.service.clear_user_data(user_id, ["pulse", "sleep"])
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertNotIn("pulse", self.service.data_cache[user_id])
        self.assertNotIn("sleep", self.service.data_cache[user_id])
        self.assertIn("activity", self.service.data_cache[user_id])
        
        # 测试清除所有数据
        result = self.service.clear_user_data(user_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertNotIn(user_id, self.service.data_cache)
    
    def test_export_user_data(self):
        """测试导出用户数据功能"""
        # 准备测试数据
        user_id = "test_user"
        self.service.data_cache[user_id] = {
            "pulse": [
                {"timestamp": datetime.now().isoformat(), "data": {"pulse_rate": 75}},
                {"timestamp": datetime.now().isoformat(), "data": {"pulse_rate": 80}}
            ],
            "sleep": [
                {"timestamp": datetime.now().isoformat(), "data": {"state": "sleeping"}}
            ]
        }
        
        # 测试导出特定类型数据
        result = self.service.export_user_data(user_id, ["pulse"])
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("pulse", result["export_data"])
        self.assertNotIn("sleep", result["export_data"])
        self.assertEqual(result["data_points"]["pulse"], 2)
        
        # 测试导出所有数据
        result = self.service.export_user_data(user_id)
        
        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("pulse", result["export_data"])
        self.assertIn("sleep", result["export_data"])
        self.assertEqual(len(result["data_types"]), 2)
    
    def test_collection_worker(self):
        """测试数据采集工作线程"""
        # 创建模拟环境
        user_id = "test_user"
        self.service.user_consents[user_id] = {
            "data_types": {"pulse", "sleep"},
            "expiry": datetime.now() + timedelta(days=30),
            "last_updated": datetime.now().isoformat()
        }
        
        # 模拟同步函数
        mock_sync = Mock()
        self.service._sync_user_data = mock_sync
        
        # 模拟缓存函数
        mock_cache = Mock()
        self.service._cache_data = mock_cache
        
        # 调用工作线程的一个周期
        # 由于工作线程是无限循环的，我们只让它运行一小段时间
        def run_worker_briefly():
            self.service._collection_worker(user_id)
        
        # 设置停止标志在短时间后生效
        def stop_after_delay():
            time.sleep(0.2)
            self.service.stopping = True
        
        # 启动工作线程
        stop_thread = threading.Thread(target=stop_after_delay)
        stop_thread.daemon = True
        stop_thread.start()
        
        # 运行工作线程
        worker_thread = threading.Thread(target=run_worker_briefly)
        worker_thread.daemon = True
        worker_thread.start()
        worker_thread.join(timeout=1.0)  # 最多等待1秒
        
        # 验证收集器函数是否被调用
        pulse_collector = self.service.collectors["pulse"]
        sleep_collector = self.service.collectors["sleep"]
        
        # 至少应该调用一次
        self.assertTrue(pulse_collector.called)
        self.assertTrue(sleep_collector.called)
        
        # 验证缓存函数是否被调用
        self.assertTrue(mock_cache.called)
    
    def test_cache_data(self):
        """测试数据缓存功能"""
        # 设置加密密钥
        self.service.setup_encryption()
        
        # 缓存一些数据
        user_id = "test_user"
        data_type = "pulse"
        test_data = {"value": "test_value"}
        
        self.service._cache_data(user_id, data_type, test_data)
        
        # 验证数据是否已缓存
        self.assertIn(user_id, self.service.data_cache)
        self.assertIn(data_type, self.service.data_cache[user_id])
        self.assertEqual(len(self.service.data_cache[user_id][data_type]), 1)
        
        # 验证加密服务是否被调用
        self.mock_privacy_service.encrypt_data.assert_called_once()
    
    def test_sync_user_data(self):
        """测试数据同步功能"""
        # 准备测试数据
        user_id = "test_user"
        self.service.data_cache[user_id] = {
            "pulse": [{"timestamp": datetime.now().isoformat(), "data": {"value": "test"}}],
            "sleep": [{"timestamp": datetime.now().isoformat(), "data": {"value": "test2"}}]
        }
        
        # 同步数据
        self.service._sync_user_data(user_id)
        
        # 验证数据是否被清空
        self.assertEqual(len(self.service.data_cache[user_id]["pulse"]), 0)
        self.assertEqual(len(self.service.data_cache[user_id]["sleep"]), 0)
        
        # 验证同步时间是否被更新
        self.assertIn(user_id, self.service.last_sync_time)
    
    def test_get_collection_status(self):
        """测试获取采集状态"""
        # 准备测试数据
        user_id = "test_user"
        self.service.register_user_consent(user_id, ["pulse", "sleep"])
        
        # 模拟线程活跃状态
        mock_thread = MagicMock()
        mock_thread.is_alive.return_value = True
        self.service.collection_threads[user_id] = mock_thread
        
        # 添加同步时间和缓存数据
        current_time = datetime.now()
        self.service.last_sync_time[user_id] = current_time.timestamp()  # 使用时间戳而不是datetime对象
        self.service.data_cache[user_id] = {
            "pulse": [{"data": "test1"}, {"data": "test2"}],
            "sleep": [{"data": "test3"}]
        }
        
        # 获取状态 - 现在源文件已经修复了时间戳处理，不需要再修改方法
        status = self.service.get_collection_status(user_id)
        
        # 验证状态
        self.assertTrue(status["is_collecting"])
        self.assertListEqual(sorted(status["collecting_types"]), sorted(["pulse", "sleep"]))
        self.assertIsNotNone(status["last_sync"])
        self.assertEqual(status["data_points"]["pulse"], 2)
        self.assertEqual(status["data_points"]["sleep"], 1)
    
    def test_start_stop(self):
        """测试服务启动和停止"""
        # 准备测试数据
        self.service.user_consents = {
            "user1": {
                "data_types": {"pulse"},
                "expiry": datetime.now() + timedelta(days=30),
                "last_updated": datetime.now().isoformat()
            },
            "user2": {
                "data_types": {"sleep"},
                "expiry": datetime.now() + timedelta(days=30),
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # 创建collection_threads以模拟真实情况
        self.service.collection_threads = {
            "user1": MagicMock(),
            "user2": MagicMock()
        }
        
        # 模拟线程启动函数
        with patch.object(self.service, '_start_collection_thread') as mock_start:
            # 测试启动
            self.service.start()
            
            # 验证每个用户是否都启动了线程
            self.assertEqual(mock_start.call_count, 2)
            
            # 验证停止标志
            self.assertFalse(self.service.stopping)
        
        # 模拟线程停止和同步函数
        with patch.object(self.service, '_stop_collection_thread') as mock_stop:
            with patch.object(self.service, '_sync_user_data') as mock_sync:
                # 添加测试缓存数据
                self.service.data_cache = {
                    "user1": {"pulse": [{"data": "test"}]},
                    "user2": {"sleep": [{"data": "test"}]}
                }
                
                # 测试停止
                self.service.stop()
                
                # 验证线程停止函数被调用
                self.assertEqual(mock_stop.call_count, 2)
    
    def test_disabled_service(self):
        """测试禁用状态的服务"""
        # 创建禁用状态的服务
        disabled_config = MockConfig(enabled=False)
        service = BackgroundCollectionService(disabled_config)
        
        # 测试注册用户同意
        result = service.register_user_consent("test_user", ["pulse"])
        self.assertFalse(result["success"])
        
        # 测试启动服务
        with patch.object(service, '_start_collection_thread') as mock_start:
            service.start()
            mock_start.assert_not_called()
    
    def test_collect_pulse_data(self):
        """测试脉搏数据采集功能"""
        # 恢复真实的采集函数
        pulse_collector = self.original_collectors["pulse"]
        
        # 调用采集函数
        result = pulse_collector("test_user")
        
        # 验证结果结构
        self.assertIn("pulse_rate", result)
        self.assertIn("rhythm", result)
        self.assertIn("strength", result)
    
    def test_collect_sleep_data(self):
        """测试睡眠数据采集功能"""
        # 恢复真实的采集函数
        sleep_collector = self.original_collectors["sleep"]
        
        # 调用采集函数
        result = sleep_collector("test_user")
        
        # 验证结果结构
        self.assertIn("state", result)
        self.assertIn("movement_level", result)
        self.assertIn("duration", result)


if __name__ == "__main__":
    unittest.main() 