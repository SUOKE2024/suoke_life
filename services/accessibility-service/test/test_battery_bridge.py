#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
电池信息桥接模块的单元测试
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# 导入测试模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.platform.battery_bridge import get_battery_level, get_battery_info, set_cache_expiry

class TestBatteryBridge(unittest.TestCase):
    """电池桥接模块的测试用例"""
    
    def setUp(self):
        """测试前准备"""
        # 设置测试环境变量
        os.environ["TEST_ENVIRONMENT"] = "true"
        os.environ["MOCK_BATTERY_LEVEL"] = "75"
        os.environ["MOCK_BATTERY_CHARGING"] = "true"
        
        # 重置缓存过期时间
        set_cache_expiry(60)
    
    def tearDown(self):
        """测试后清理"""
        # 清除测试环境变量
        for key in ["TEST_ENVIRONMENT", "MOCK_BATTERY_LEVEL", "MOCK_BATTERY_CHARGING"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_get_battery_level(self):
        """测试获取电池电量"""
        # 从环境变量获取模拟值
        battery_level = get_battery_level()
        self.assertEqual(battery_level, 75)
        
        # 改变环境变量，模拟不同电量
        os.environ["MOCK_BATTERY_LEVEL"] = "30"
        battery_level = get_battery_level()
        self.assertEqual(battery_level, 30)
    
    def test_get_battery_info(self):
        """测试获取完整电池信息"""
        # 从环境变量获取模拟值
        battery_info = get_battery_info()
        self.assertEqual(battery_info["level"], 75)
        self.assertEqual(battery_info["charging"], True)
        
        # 改变环境变量，模拟不同状态
        os.environ["MOCK_BATTERY_LEVEL"] = "45"
        os.environ["MOCK_BATTERY_CHARGING"] = "false"
        battery_info = get_battery_info()
        self.assertEqual(battery_info["level"], 45)
        self.assertEqual(battery_info["charging"], False)
    
    def test_cache_expiry(self):
        """测试缓存过期机制"""
        # 设置较短的缓存时间用于测试
        set_cache_expiry(0.1)  # 0.1秒
        
        # 临时禁用测试环境标志，以便测试缓存
        del os.environ["TEST_ENVIRONMENT"]
        
        # 获取初始电池信息
        battery_info = get_battery_info()
        initial_level = battery_info["level"]
        
        # 改变环境变量，但由于缓存，应该仍返回旧值
        os.environ["MOCK_BATTERY_LEVEL"] = "20"
        battery_info = get_battery_info()
        self.assertEqual(battery_info["level"], initial_level)  # 应该仍是缓存的值
        
        # 等待缓存过期
        import time
        time.sleep(0.2)  # 等待0.2秒，确保缓存过期
        
        # 再次获取，应该获得新值
        os.environ["TEST_ENVIRONMENT"] = "true"  # 重新设置测试环境标志
        battery_info = get_battery_info()
        self.assertEqual(battery_info["level"], 20)  # 现在应该是新值
    
    @patch('internal.platform.battery_bridge.os.environ.get')
    def test_platform_detection(self, mock_env_get):
        """测试平台检测逻辑"""
        # 模拟Flutter环境
        mock_env_get.side_effect = lambda key, default=None: {
            "FLUTTER_RUNTIME": "true",
            "MOBILE_PLATFORM": "android"
        }.get(key, default)
        
        # 由于我们无法实际导入Flutter桥接，这里只能测试回退到测试环境
        battery_info = get_battery_info()
        self.assertIsNotNone(battery_info["level"])
    
    def test_invalid_battery_values(self):
        """测试无效的电池值处理"""
        # 设置无效的电池电量值
        os.environ["MOCK_BATTERY_LEVEL"] = "invalid"
        
        # 应该返回默认值而不是崩溃
        battery_info = get_battery_info()
        self.assertEqual(battery_info["level"], 100)  # 默认值
        self.assertEqual(battery_info["charging"], True)  # 默认值

if __name__ == "__main__":
    unittest.main()