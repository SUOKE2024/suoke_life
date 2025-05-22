#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
电池桥接模块 - 提供跨平台电池状态检测功能
"""

import logging
import platform
import os
import subprocess
import re
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class BatteryBridge:
    """电池信息桥接类，提供跨平台的电池状态检测"""

    def __init__(self):
        """初始化电池桥接"""
        self.platform = self._detect_platform()
        self.battery_cache = None
        self.cache_ttl = 60  # 缓存有效期（秒）
        self.last_update = 0  # 上次更新时间
        logger.info(f"电池桥接初始化完成，当前平台: {self.platform}")

    def _detect_platform(self) -> str:
        """检测当前运行平台"""
        system = platform.system().lower()
        
        if system == 'darwin':
            return 'macos'
        elif system == 'linux':
            # 判断是否为Android
            if 'ANDROID_ROOT' in os.environ:
                return 'android'
            return 'linux'
        elif system == 'windows':
            return 'windows'
        elif system == 'java':
            # 可能是Android的某些环境
            return 'android'
        else:
            logger.warning(f"未知平台: {system}，使用通用实现")
            return 'generic'

    def get_battery_info(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        获取电池信息
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            包含电池信息的字典，包括电量百分比、是否充电等
        """
        import time
        current_time = time.time()
        
        # 检查是否需要刷新缓存
        if force_refresh or not self.battery_cache or (current_time - self.last_update) > self.cache_ttl:
            try:
                if self.platform == 'android':
                    self.battery_cache = self._get_battery_android()
                elif self.platform == 'macos':
                    self.battery_cache = self._get_battery_macos()
                elif self.platform == 'ios':
                    self.battery_cache = self._get_battery_ios()
                elif self.platform == 'linux':
                    self.battery_cache = self._get_battery_linux()
                elif self.platform == 'windows':
                    self.battery_cache = self._get_battery_windows()
                else:
                    self.battery_cache = self._get_battery_generic()
                
                self.last_update = current_time
                logger.debug(f"电池信息已更新: {self.battery_cache}")
            except Exception as e:
                logger.error(f"获取电池信息失败: {str(e)}")
                # 如果缓存不可用，返回默认值
                if not self.battery_cache:
                    self.battery_cache = {
                        'level': 100,
                        'is_charging': True,
                        'power_mode': 'unknown',
                        'error': str(e)
                    }
        
        return self.battery_cache

    def get_battery_level(self) -> int:
        """
        获取电池电量百分比
        
        Returns:
            电池电量百分比（0-100）
        """
        battery_info = self.get_battery_info()
        return battery_info.get('level', 100)

    def is_charging(self) -> bool:
        """
        检查设备是否正在充电
        
        Returns:
            设备是否正在充电
        """
        battery_info = self.get_battery_info()
        return battery_info.get('is_charging', False)

    def get_power_mode(self) -> str:
        """
        获取当前电源模式
        
        Returns:
            电源模式（normal, low_power, ultra_low_power等）
        """
        battery_info = self.get_battery_info()
        return battery_info.get('power_mode', 'normal')

    def _get_battery_android(self) -> Dict[str, Any]:
        """获取Android设备电池信息"""
        try:
            # 尝试使用Android API
            import jnius_config
            import jnius
            
            # 配置Android环境
            if not jnius_config.vm_running:
                logger.debug("初始化Android JVM")
                jnius_config.set_up()
            
            # 使用Android电池管理器API
            PythonActivity = jnius.autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            context = activity.getApplicationContext()
            intent = context.registerReceiver(None, jnius.autoclass('android.content.IntentFilter')
                                             (jnius.autoclass('android.content.Intent').ACTION_BATTERY_CHANGED))
            
            level = intent.getIntExtra(jnius.autoclass('android.os.BatteryManager').EXTRA_LEVEL, -1)
            scale = intent.getIntExtra(jnius.autoclass('android.os.BatteryManager').EXTRA_SCALE, -1)
            
            battery_pct = level * 100 / scale if scale > 0 else -1
            
            # 检查充电状态
            status = intent.getIntExtra(jnius.autoclass('android.os.BatteryManager').EXTRA_STATUS, -1)
            is_charging = (status == jnius.autoclass('android.os.BatteryManager').BATTERY_STATUS_CHARGING or 
                          status == jnius.autoclass('android.os.BatteryManager').BATTERY_STATUS_FULL)
            
            # 获取电源模式
            power_manager = context.getSystemService(jnius.autoclass('android.content.Context').POWER_SERVICE)
            power_mode = 'low_power' if power_manager.isPowerSaveMode() else 'normal'
            
            return {
                'level': int(battery_pct),
                'is_charging': is_charging,
                'power_mode': power_mode
            }
            
        except ImportError as e:
            logger.warning(f"无法导入Android特定库: {str(e)}，尝试使用命令行方法")
            return self._get_battery_android_shell()
        except Exception as e:
            logger.warning(f"Android API方法失败: {str(e)}，尝试使用命令行方法")
            return self._get_battery_android_shell()

    def _get_battery_android_shell(self) -> Dict[str, Any]:
        """使用shell命令获取Android电池信息"""
        try:
            # 使用adb命令获取电池信息
            if self._is_adb_available():
                # 使用adb dumpsys命令
                dumpsys_output = subprocess.check_output(
                    ['adb', 'shell', 'dumpsys', 'battery'],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # 解析输出
                level_match = re.search(r'level: (\d+)', dumpsys_output)
                charging_match = re.search(r'status: (\d+)', dumpsys_output)
                
                level = int(level_match.group(1)) if level_match else 100
                # 充电状态: 2=充电中, 5=已充满
                is_charging = charging_match and charging_match.group(1) in ('2', '5')
                
                return {
                    'level': level,
                    'is_charging': is_charging,
                    'power_mode': 'normal'
                }
            else:
                # 如果在Android设备上直接运行
                if os.path.exists('/sys/class/power_supply/battery/capacity'):
                    with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                        level = int(f.read().strip())
                    
                    # 检查充电状态
                    is_charging = False
                    if os.path.exists('/sys/class/power_supply/battery/status'):
                        with open('/sys/class/power_supply/battery/status', 'r') as f:
                            status = f.read().strip()
                            is_charging = status in ['Charging', 'Full']
                    
                    return {
                        'level': level,
                        'is_charging': is_charging,
                        'power_mode': 'normal'
                    }
        except Exception as e:
            logger.error(f"获取Android电池信息失败: {str(e)}")
        
        # 返回默认值
        return {
            'level': 100,
            'is_charging': True,
            'power_mode': 'normal',
            'error': 'Failed to get Android battery info'
        }

    def _get_battery_ios(self) -> Dict[str, Any]:
        """获取iOS设备电池信息"""
        try:
            # 尝试使用pyobjc库
            import objc
            from Foundation import NSBundle
            
            UIKit = NSBundle.bundleWithIdentifier_('com.apple.UIKit')
            functions = [
                ('UIDevice', b'UIDevice'),
                ('UIDevice.currentDevice', b'currentDevice'),
                ('UIDevice.batteryLevel', b'batteryLevel'),
                ('UIDevice.batteryState', b'batteryState')
            ]
            
            objc.loadBundleFunctions(UIKit, globals(), functions)
            
            device = UIDevice.currentDevice()
            device.setBatteryMonitoringEnabled_(True)
            
            level = int(device.batteryLevel() * 100)
            # 充电状态: 0=未知, 1=未充电, 2=充电中, 3=已充满
            state = device.batteryState()
            is_charging = state in (2, 3)
            
            # 获取低电量模式状态
            power_mode = 'normal'
            try:
                NSProcessInfo = objc.lookUpClass('NSProcessInfo')
                process_info = NSProcessInfo.processInfo()
                if process_info.respondsToSelector_('isLowPowerModeEnabled'):
                    power_mode = 'low_power' if process_info.isLowPowerModeEnabled() else 'normal'
            except:
                pass
            
            return {
                'level': level,
                'is_charging': is_charging,
                'power_mode': power_mode
            }
            
        except Exception as e:
            logger.error(f"获取iOS电池信息失败: {str(e)}")
            
            # 返回默认值
            return {
                'level': 100,
                'is_charging': True,
                'power_mode': 'normal',
                'error': str(e)
            }

    def _get_battery_macos(self) -> Dict[str, Any]:
        """获取MacOS设备电池信息"""
        try:
            # 使用pmset命令获取电池信息
            output = subprocess.check_output(
                ['pmset', '-g', 'batt'],
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 解析输出
            percentage_match = re.search(r'(\d+)%', output)
            charging_match = re.search(r'(charging|discharging|charged)', output, re.IGNORECASE)
            
            level = int(percentage_match.group(1)) if percentage_match else 100
            is_charging = charging_match and 'discharging' not in charging_match.group(1).lower()
            
            # 检查低电量模式
            power_mode = 'normal'
            try:
                power_output = subprocess.check_output(
                    ['pmset', '-g', 'therm'],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                if 'lowpowermode 1' in power_output.lower():
                    power_mode = 'low_power'
            except:
                pass
            
            return {
                'level': level,
                'is_charging': is_charging,
                'power_mode': power_mode
            }
            
        except Exception as e:
            logger.error(f"获取MacOS电池信息失败: {str(e)}")
            
            # 返回默认值
            return {
                'level': 100,
                'is_charging': True,
                'power_mode': 'normal',
                'error': str(e)
            }

    def _get_battery_linux(self) -> Dict[str, Any]:
        """获取Linux设备电池信息"""
        try:
            # 尝试使用upower
            if self._is_command_available('upower'):
                output = subprocess.check_output(
                    ['upower', '-i', '/org/freedesktop/UPower/devices/battery_BAT0'],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # 解析输出
                percentage_match = re.search(r'percentage:\s*(\d+)%', output)
                state_match = re.search(r'state:\s*(\w+)', output)
                
                level = int(percentage_match.group(1)) if percentage_match else 100
                is_charging = state_match and state_match.group(1).lower() in ['charging', 'fully-charged']
                
                return {
                    'level': level,
                    'is_charging': is_charging,
                    'power_mode': 'normal'
                }
            
            # 尝试直接读取系统文件
            elif os.path.exists('/sys/class/power_supply/BAT0/capacity'):
                with open('/sys/class/power_supply/BAT0/capacity', 'r') as f:
                    level = int(f.read().strip())
                
                is_charging = False
                if os.path.exists('/sys/class/power_supply/BAT0/status'):
                    with open('/sys/class/power_supply/BAT0/status', 'r') as f:
                        status = f.read().strip()
                        is_charging = status in ['Charging', 'Full']
                
                return {
                    'level': level,
                    'is_charging': is_charging,
                    'power_mode': 'normal'
                }
                
            # 尝试使用acpi命令
            elif self._is_command_available('acpi'):
                output = subprocess.check_output(
                    ['acpi', '-b'],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # 解析输出
                percentage_match = re.search(r'(\d+)%', output)
                charging_match = re.search(r'(Charging|Discharging|Full)', output)
                
                level = int(percentage_match.group(1)) if percentage_match else 100
                is_charging = charging_match and charging_match.group(1) in ['Charging', 'Full']
                
                return {
                    'level': level,
                    'is_charging': is_charging,
                    'power_mode': 'normal'
                }
        except Exception as e:
            logger.error(f"获取Linux电池信息失败: {str(e)}")
        
        # 返回默认值
        return {
            'level': 100,
            'is_charging': True,
            'power_mode': 'normal',
            'error': 'Failed to get Linux battery info'
        }

    def _get_battery_windows(self) -> Dict[str, Any]:
        """获取Windows设备电池信息"""
        try:
            # 使用WMIC命令获取电池信息
            output = subprocess.check_output(
                ['WMIC', 'PATH', 'Win32_Battery', 'GET', 'EstimatedChargeRemaining,BatteryStatus', '/FORMAT:LIST'],
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 解析输出
            level_match = re.search(r'EstimatedChargeRemaining=(\d+)', output)
            status_match = re.search(r'BatteryStatus=(\d+)', output)
            
            level = int(level_match.group(1)) if level_match else 100
            # BatteryStatus: 1=放电中, 2=交流电源供电, 其他值表示不同状态
            is_charging = status_match and status_match.group(1) != '1'
            
            # 检查电源模式
            power_mode = 'normal'
            try:
                power_output = subprocess.check_output(
                    ['powercfg', '/GETACTIVESCHEME'],
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                if 'Power saver' in power_output:
                    power_mode = 'low_power'
            except:
                pass
            
            return {
                'level': level,
                'is_charging': is_charging,
                'power_mode': power_mode
            }
            
        except Exception as e:
            logger.error(f"获取Windows电池信息失败: {str(e)}")
            
            # 返回默认值
            return {
                'level': 100,
                'is_charging': True,
                'power_mode': 'normal',
                'error': str(e)
            }

    def _get_battery_generic(self) -> Dict[str, Any]:
        """通用电池信息获取实现，尝试所有可能的方法"""
        # 尝试psutil库
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'level': int(battery.percent),
                    'is_charging': battery.power_plugged,
                    'power_mode': 'normal'
                }
        except:
            pass
        
        # 如果psutil失败，根据平台尝试其他方法
        if platform.system() == 'Darwin':
            return self._get_battery_macos()
        elif platform.system() == 'Linux':
            return self._get_battery_linux()
        elif platform.system() == 'Windows':
            return self._get_battery_windows()
        
        # 无法确定电池状态，返回默认值
        logger.warning("无法确定电池状态，使用默认值")
        return {
            'level': 100,
            'is_charging': True,
            'power_mode': 'normal',
            'error': 'Unknown platform, using default values'
        }

    def _is_command_available(self, command: str) -> bool:
        """检查命令是否可用"""
        try:
            subprocess.run(
                [command, '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return True
        except:
            return False

    def _is_adb_available(self) -> bool:
        """检查ADB是否可用"""
        return self._is_command_available('adb')


# 单例实例
battery_bridge = BatteryBridge()


def get_battery_level() -> int:
    """
    全局函数：获取电池电量百分比
    
    Returns:
        电池电量百分比（0-100）
    """
    # 检查是否在测试环境中
    import os
    if os.environ.get("TEST_ENVIRONMENT") == "true":
        try:
            return int(os.environ.get("MOCK_BATTERY_LEVEL", "100"))
        except (ValueError, TypeError):
            return 100
            
    bridge = BatteryBridge()
    return bridge.get_battery_level()


def set_cache_expiry(seconds: int) -> None:
    """
    全局函数：设置电池信息缓存有效期
    
    Args:
        seconds: 缓存有效期（秒）
    """
    bridge = BatteryBridge()
    bridge.cache_ttl = seconds
    logger.debug(f"已设置电池信息缓存有效期为 {seconds} 秒")


def is_charging() -> bool:
    """
    全局函数：检查设备是否正在充电
    
    Returns:
        设备是否正在充电
    """
    return battery_bridge.is_charging()


def get_power_mode() -> str:
    """获取当前电源模式（全局函数）"""
    return battery_bridge.get_power_mode()


def get_battery_info(force_refresh: bool = False) -> Dict[str, Any]:
    """
    全局函数：获取电池信息
    
    Args:
        force_refresh: 是否强制刷新缓存
    
    Returns:
        包含电池信息的字典
    """
    # 检查是否在测试环境中
    import os
    if os.environ.get("TEST_ENVIRONMENT") == "true":
        try:
            level = int(os.environ.get("MOCK_BATTERY_LEVEL", "100"))
        except (ValueError, TypeError):
            level = 100
            
        charging = os.environ.get("MOCK_BATTERY_CHARGING", "true").lower() in ("true", "1", "yes")
        
        return {
            "level": level,
            "charging": charging,
            "power_mode": "normal",
            "source": "mock"
        }
            
    bridge = BatteryBridge()
    return bridge.get_battery_info(force_refresh)