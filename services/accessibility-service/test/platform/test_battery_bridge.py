#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
电池桥接模块单元测试
"""

import unittest
import os
import sys
import platform
from unittest.mock import patch, MagicMock

# 确保能够导入服务模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 导入被测试模块
from internal.platform.battery_bridge import BatteryBridge, get_battery_level, is_charging, get_power_mode, get_battery_info


class TestBatteryBridge(unittest.TestCase):
    """电池桥接模块单元测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建电池桥接实例
        self.battery_bridge = BatteryBridge()
        # 清除缓存
        self.battery_bridge.battery_cache = None
        self.battery_bridge.last_update = 0

    def test_platform_detection(self):
        """测试平台检测功能"""
        # 记录原始系统信息
        original_system = platform.system
        
        try:
            # 模拟不同平台
            platforms = {
                'Darwin': 'macos',
                'Linux': 'linux',
                'Windows': 'windows'
            }
            
            for sys_name, expected_platform in platforms.items():
                with patch('platform.system', return_value=sys_name):
                    bridge = BatteryBridge()
                    self.assertEqual(bridge._detect_platform(), expected_platform)
            
            # 测试Android平台检测
            with patch('platform.system', return_value='Linux'):
                with patch.dict('os.environ', {'ANDROID_ROOT': '/system'}):
                    bridge = BatteryBridge()
                    self.assertEqual(bridge._detect_platform(), 'android')
            
            # 测试Java环境（可能是Android）
            with patch('platform.system', return_value='Java'):
                bridge = BatteryBridge()
                self.assertEqual(bridge._detect_platform(), 'android')
            
            # 测试未知平台
            with patch('platform.system', return_value='Unknown'):
                bridge = BatteryBridge()
                self.assertEqual(bridge._detect_platform(), 'generic')
                
        finally:
            # 恢复原始系统信息
            platform.system = original_system

    def test_battery_info_caching(self):
        """测试电池信息缓存机制"""
        # 模拟电池信息获取方法
        mock_battery_info = {'level': 75, 'is_charging': True, 'power_mode': 'normal'}
        
        # 根据当前平台选择要模拟的方法
        platform_method = f"_get_battery_{self.battery_bridge.platform}"
        
        with patch.object(self.battery_bridge, platform_method, return_value=mock_battery_info):
            # 首次调用应该触发平台特定方法
            info1 = self.battery_bridge.get_battery_info()
            self.assertEqual(info1, mock_battery_info)
            
            # 更改模拟返回值
            new_mock_info = {'level': 50, 'is_charging': False, 'power_mode': 'low_power'}
            with patch.object(self.battery_bridge, platform_method, return_value=new_mock_info):
                # 由于缓存，应该返回旧值
                info2 = self.battery_bridge.get_battery_info()
                self.assertEqual(info2, mock_battery_info)
                
                # 强制刷新应该返回新值
                info3 = self.battery_bridge.get_battery_info(force_refresh=True)
                self.assertEqual(info3, new_mock_info)

    def test_battery_level_method(self):
        """测试获取电池电量方法"""
        # 模拟电池信息
        mock_battery_info = {'level': 60, 'is_charging': True, 'power_mode': 'normal'}
        
        with patch.object(self.battery_bridge, 'get_battery_info', return_value=mock_battery_info):
            level = self.battery_bridge.get_battery_level()
            self.assertEqual(level, 60)
            
            # 测试缺少level字段的情况
            with patch.object(self.battery_bridge, 'get_battery_info', return_value={}):
                level = self.battery_bridge.get_battery_level()
                self.assertEqual(level, 100)  # 应该返回默认值

    def test_is_charging_method(self):
        """测试获取充电状态方法"""
        # 模拟电池信息
        mock_battery_info = {'level': 80, 'is_charging': True, 'power_mode': 'normal'}
        
        with patch.object(self.battery_bridge, 'get_battery_info', return_value=mock_battery_info):
            charging = self.battery_bridge.is_charging()
            self.assertTrue(charging)
            
            # 测试缺少is_charging字段的情况
            with patch.object(self.battery_bridge, 'get_battery_info', return_value={}):
                charging = self.battery_bridge.is_charging()
                self.assertFalse(charging)  # 应该返回默认值

    def test_get_power_mode_method(self):
        """测试获取电源模式方法"""
        # 模拟电池信息
        mock_battery_info = {'level': 30, 'is_charging': False, 'power_mode': 'low_power'}
        
        with patch.object(self.battery_bridge, 'get_battery_info', return_value=mock_battery_info):
            mode = self.battery_bridge.get_power_mode()
            self.assertEqual(mode, 'low_power')
            
            # 测试缺少power_mode字段的情况
            with patch.object(self.battery_bridge, 'get_battery_info', return_value={}):
                mode = self.battery_bridge.get_power_mode()
                self.assertEqual(mode, 'normal')  # 应该返回默认值

    def test_error_handling(self):
        """测试错误处理机制"""
        # 模拟电池信息获取抛出异常
        error_message = "模拟的电池信息获取错误"
        
        # 根据当前平台选择要模拟的方法
        platform_method = f"_get_battery_{self.battery_bridge.platform}"
        
        with patch.object(self.battery_bridge, platform_method, side_effect=Exception(error_message)):
            # 获取电池信息应该返回默认值
            info = self.battery_bridge.get_battery_info()
            self.assertEqual(info['level'], 100)
            self.assertTrue(info['is_charging'])
            self.assertEqual(info['power_mode'], 'unknown')
            self.assertEqual(info['error'], error_message)

    @unittest.skipIf(platform.system() != 'Linux', "仅在Linux平台上运行")
    def test_linux_battery_detection(self):
        """测试Linux平台电池检测"""
        # 模拟upower命令输出
        upower_output = """
        native-path:          BAT0
        power supply:         yes
        updated:              Mon, 06 May 2024 10:15:42 CST
        has history:          yes
        has statistics:       yes
        battery
          present:             yes
          rechargeable:        yes
          state:               discharging
          energy:              41.9 Wh
          energy-full:         56.4 Wh
          percentage:          74%
        """
        
        # 测试upower检测方法
        with patch('subprocess.check_output', return_value=upower_output):
            with patch.object(self.battery_bridge, '_is_command_available', return_value=True):
                info = self.battery_bridge._get_battery_linux()
                self.assertEqual(info['level'], 74)
                self.assertFalse(info['is_charging'])
        
        # 测试系统文件检测方法
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data='85')):
                with patch.object(self.battery_bridge, '_is_command_available', return_value=False):
                    info = self.battery_bridge._get_battery_linux()
                    self.assertEqual(info['level'], 85)

    @unittest.skipIf(platform.system() != 'Darwin', "仅在macOS平台上运行")
    def test_macos_battery_detection(self):
        """测试macOS平台电池检测"""
        # 模拟pmset命令输出
        pmset_output = """
        Now drawing from 'Battery Power'
         -InternalBattery-0 (id=4522349)	68%; discharging; 3:15 remaining present: true
        """
        
        with patch('subprocess.check_output', return_value=pmset_output):
            info = self.battery_bridge._get_battery_macos()
            self.assertEqual(info['level'], 68)
            self.assertFalse(info['is_charging'])
        
        # 测试充电状态
        pmset_charging_output = """
        Now drawing from 'AC Power'
         -InternalBattery-0 (id=4522349)	90%; charging; 0:20 remaining present: true
        """
        
        with patch('subprocess.check_output', return_value=pmset_charging_output):
            info = self.battery_bridge._get_battery_macos()
            self.assertEqual(info['level'], 90)
            self.assertTrue(info['is_charging'])

    @unittest.skipIf(platform.system() != 'Windows', "仅在Windows平台上运行")
    def test_windows_battery_detection(self):
        """测试Windows平台电池检测"""
        # 模拟WMIC命令输出
        wmic_output = """
        BatteryStatus=2
        EstimatedChargeRemaining=82
        """
        
        with patch('subprocess.check_output', return_value=wmic_output):
            info = self.battery_bridge._get_battery_windows()
            self.assertEqual(info['level'], 82)
            self.assertTrue(info['is_charging'])
        
        # 测试放电状态
        wmic_discharging_output = """
        BatteryStatus=1
        EstimatedChargeRemaining=45
        """
        
        with patch('subprocess.check_output', return_value=wmic_discharging_output):
            info = self.battery_bridge._get_battery_windows()
            self.assertEqual(info['level'], 45)
            self.assertFalse(info['is_charging'])

    def test_android_battery_detection(self):
        """测试Android平台电池检测"""
        # 测试shell方法
        with patch.object(self.battery_bridge, '_is_adb_available', return_value=True):
            # 模拟adb dumpsys battery输出
            dumpsys_output = """
            Current Battery Service state:
              AC powered: false
              USB powered: true
              Wireless powered: false
              status: 2
              health: 2
              present: true
              level: 78
              scale: 100
              temperature: 280
              technology: Li-ion
            """
            
            with patch('subprocess.check_output', return_value=dumpsys_output):
                info = self.battery_bridge._get_battery_android_shell()
                self.assertEqual(info['level'], 78)
                self.assertTrue(info['is_charging'])
        
        # 测试系统文件方法
        with patch.object(self.battery_bridge, '_is_adb_available', return_value=False):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', unittest.mock.mock_open(read_data='65')):
                    info = self.battery_bridge._get_battery_android_shell()
                    self.assertEqual(info['level'], 65)

    def test_global_functions(self):
        """测试全局函数"""
        # 模拟电池桥接实例
        mock_battery_bridge = MagicMock()
        mock_battery_bridge.get_battery_level.return_value = 55
        mock_battery_bridge.is_charging.return_value = True
        mock_battery_bridge.get_power_mode.return_value = 'low_power'
        mock_battery_bridge.get_battery_info.return_value = {
            'level': 55, 
            'is_charging': True, 
            'power_mode': 'low_power'
        }
        
        # 替换单例实例
        with patch('internal.platform.battery_bridge.battery_bridge', mock_battery_bridge):
            # 测试全局函数
            self.assertEqual(get_battery_level(), 55)
            self.assertTrue(is_charging())
            self.assertEqual(get_power_mode(), 'low_power')
            self.assertEqual(get_battery_info()['level'], 55)
            
            # 测试强制刷新参数传递
            get_battery_info(force_refresh=True)
            mock_battery_bridge.get_battery_info.assert_called_with(True)


if __name__ == '__main__':
    unittest.main() 