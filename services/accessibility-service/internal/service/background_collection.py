#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后台数据采集服务 - 实现设备待机、息屏条件下的唤醒与持续无感采集信息
"""

import logging
import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BackgroundCollectionService:
    """设备待机、息屏条件下持续采集用户信息的服务"""

    def __init__(self, config: Any):
        """
        初始化后台数据采集服务
        
        Args:
            config: 服务配置信息
        """
        self.config = config
        self.enabled = config.background_collection.enabled if hasattr(config, 'background_collection') else False
        self.collection_threads = {}  # 用户ID -> 采集线程
        self.user_consents = {}  # 用户ID -> 同意的数据类型集合
        self.last_sync_time = {}  # 用户ID -> 上次同步时间
        self.collection_intervals = {}  # 用户ID -> 采集间隔配置
        self.stopping = False  # 服务停止标志
        self.encryption_key = None  # 数据加密密钥
        
        # 数据缓存
        self.data_cache = {}  # 用户ID -> 数据缓存
        self.cache_lock = threading.RLock()  # 缓存访问锁
        
        # 导入其他可能需要的服务
        self.privacy_service = None  # 后续注入
        self.monitoring_service = None  # 后续注入
        
        # 电池管理相关
        self.battery_threshold_low = config.background_collection.battery_threshold_low if hasattr(config, 'background_collection') and hasattr(config.background_collection, 'battery_threshold_low') else 20
        self.battery_threshold_critical = config.background_collection.battery_threshold_critical if hasattr(config, 'background_collection') and hasattr(config.background_collection, 'battery_threshold_critical') else 10
        self.interval_multiplier_low = config.background_collection.interval_multiplier_low if hasattr(config, 'background_collection') and hasattr(config.background_collection, 'interval_multiplier_low') else 2
        self.interval_multiplier_critical = config.background_collection.interval_multiplier_critical if hasattr(config, 'background_collection') and hasattr(config.background_collection, 'interval_multiplier_critical') else 4
        
        # 数据类型及其对应的采集函数
        self.collectors = {
            "pulse": self._collect_pulse_data,
            "sleep": self._collect_sleep_data,
            "activity": self._collect_activity_data,
            "environment": self._collect_environment_data,
            "voice": self._collect_voice_data
        }
        
        logger.info("后台数据采集服务初始化完成")
    
    def setup_encryption(self):
        """设置数据加密"""
        if not self.encryption_key and hasattr(self.config, 'security') and hasattr(self.config.security, 'encryption'):
            try:
                # 实际应用中应从安全存储获取密钥
                self.encryption_key = hashlib.sha256(
                    self.config.security.encryption.get('seed', 'accessibility-service').encode()
                ).digest()
                logger.info("数据加密已设置")
            except Exception as e:
                logger.error(f"设置数据加密失败: {str(e)}")
    
    def set_crisis_alert_service(self, crisis_alert_service):
        """
        设置危机报警服务，实现数据分析与警报功能集成
        
        Args:
            crisis_alert_service: 危机报警服务实例
        """
        self.crisis_alert_service = crisis_alert_service
        # 如果危机报警服务需要访问后台采集服务
        if hasattr(crisis_alert_service, 'background_collection_service'):
            crisis_alert_service.background_collection_service = self
            logger.info("已将后台数据采集服务注入到危机报警服务")
        logger.info("已设置危机报警服务集成")
    
    def register_user_consent(self, user_id: str, data_types: List[str], 
                             expiry_days: int = 365) -> Dict[str, Any]:
        """
        注册用户对特定数据类型的采集同意
        
        Args:
            user_id: 用户ID
            data_types: 同意采集的数据类型列表
            expiry_days: 同意有效期（天）
            
        Returns:
            包含注册结果的字典
        """
        if not self.enabled:
            return {"success": False, "message": "后台数据采集服务未启用"}
        
        try:
            # 验证数据类型
            valid_types = [dt for dt in data_types if dt in self.collectors]
            invalid_types = [dt for dt in data_types if dt not in self.collectors]
            
            # 存储用户同意
            self.user_consents[user_id] = {
                "data_types": set(valid_types),
                "expiry": datetime.now() + timedelta(days=expiry_days),
                "last_updated": datetime.now().isoformat()
            }
            
            # 如果有新的同意类型，启动对应的采集线程
            if user_id not in self.collection_threads or not self.collection_threads[user_id].is_alive():
                self._start_collection_thread(user_id)
            
            logger.info(f"已注册用户 {user_id} 对数据类型 {valid_types} 的采集同意")
            
            result = {
                "success": True,
                "message": "成功注册用户同意",
                "registered_types": valid_types
            }
            
            if invalid_types:
                result["warning"] = f"不支持的数据类型: {invalid_types}"
                
            return result
            
        except Exception as e:
            logger.error(f"注册用户同意失败: {str(e)}")
            return {
                "success": False,
                "message": f"注册失败: {str(e)}"
            }
    
    def revoke_user_consent(self, user_id: str, data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        撤销用户对特定数据类型的采集同意
        
        Args:
            user_id: 用户ID
            data_types: 要撤销的数据类型列表，None表示撤销所有
            
        Returns:
            包含撤销结果的字典
        """
        if user_id not in self.user_consents:
            return {"success": False, "message": "未找到用户同意记录"}
        
        try:
            if data_types is None:
                # 撤销所有同意
                if user_id in self.collection_threads and self.collection_threads[user_id].is_alive():
                    self._stop_collection_thread(user_id)
                del self.user_consents[user_id]
                logger.info(f"已撤销用户 {user_id} 的所有数据采集同意")
                return {"success": True, "message": "已撤销所有数据采集同意"}
            else:
                # 撤销特定类型的同意
                if user_id in self.user_consents:
                    for dt in data_types:
                        self.user_consents[user_id]["data_types"].discard(dt)
                    
                    # 如果没有剩余同意，停止采集线程
                    if not self.user_consents[user_id]["data_types"]:
                        if user_id in self.collection_threads and self.collection_threads[user_id].is_alive():
                            self._stop_collection_thread(user_id)
                        del self.user_consents[user_id]
                    
                    logger.info(f"已撤销用户 {user_id} 对数据类型 {data_types} 的采集同意")
                    return {"success": True, "message": f"已撤销指定数据类型的采集同意: {data_types}"}
                
                return {"success": False, "message": "未找到用户同意记录"}
                
        except Exception as e:
            logger.error(f"撤销用户同意失败: {str(e)}")
            return {
                "success": False,
                "message": f"撤销失败: {str(e)}"
            }
    
    def get_user_consent_status(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户同意状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含用户同意状态的字典
        """
        if user_id not in self.user_consents:
            return {
                "has_consent": False,
                "message": "用户未授权数据采集"
            }
        
        consent = self.user_consents[user_id]
        
        # 检查是否过期
        if datetime.now() > consent["expiry"]:
            return {
                "has_consent": False,
                "message": "用户授权已过期",
                "expired_at": consent["expiry"].isoformat()
            }
        
        return {
            "has_consent": True,
            "data_types": list(consent["data_types"]),
            "expiry": consent["expiry"].isoformat(),
            "last_updated": consent["last_updated"]
        }
    
    def set_collection_interval(self, user_id: str, intervals: Dict[str, int]) -> Dict[str, Any]:
        """
        设置特定用户的数据采集间隔
        
        Args:
            user_id: 用户ID
            intervals: 数据类型到采集间隔（秒）的映射
            
        Returns:
            包含设置结果的字典
        """
        try:
            if user_id not in self.collection_intervals:
                self.collection_intervals[user_id] = {}
            
            # 更新间隔设置
            for data_type, interval in intervals.items():
                if data_type in self.collectors:
                    self.collection_intervals[user_id][data_type] = max(interval, 10)  # 最小间隔10秒
            
            logger.info(f"已设置用户 {user_id} 的数据采集间隔: {intervals}")
            return {
                "success": True,
                "message": "成功设置数据采集间隔",
                "current_intervals": self.collection_intervals[user_id]
            }
            
        except Exception as e:
            logger.error(f"设置采集间隔失败: {str(e)}")
            return {
                "success": False,
                "message": f"设置失败: {str(e)}"
            }
    
    def get_collection_status(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户数据采集状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含采集状态的字典
        """
        result = {
            "is_collecting": False,
            "collecting_types": [],
            "last_sync": None,
            "data_points": {}
        }
        
        # 检查用户授权
        consent_status = self.get_user_consent_status(user_id)
        if not consent_status["has_consent"]:
            result["message"] = consent_status["message"]
            return result
        
        # 检查采集线程
        if user_id in self.collection_threads and self.collection_threads[user_id].is_alive():
            result["is_collecting"] = True
            result["collecting_types"] = list(self.user_consents[user_id]["data_types"])
            
            # 获取上次同步时间
            if user_id in self.last_sync_time:
                # 将时间戳转换为ISO格式字符串
                timestamp = self.last_sync_time[user_id]
                if isinstance(timestamp, (int, float)):
                    result["last_sync"] = datetime.fromtimestamp(timestamp).isoformat()
                else:
                    result["last_sync"] = timestamp.isoformat()
            
            # 获取缓存的数据点数量
            with self.cache_lock:
                if user_id in self.data_cache:
                    for data_type in self.data_cache[user_id]:
                        result["data_points"][data_type] = len(self.data_cache[user_id][data_type])
        
        # 添加电池状态信息
        battery_level = self._get_battery_level()
        result["battery_level"] = battery_level
        
        # 添加电池优化状态
        if battery_level <= self.battery_threshold_critical:
            result["battery_optimization"] = "critical"
        elif battery_level <= self.battery_threshold_low:
            result["battery_optimization"] = "low"
        else:
            result["battery_optimization"] = "normal"
        
        return result
    
    def start(self):
        """启动后台数据采集服务"""
        if not self.enabled:
            logger.info("后台数据采集服务未启用，跳过启动")
            return
        
        logger.info("启动后台数据采集服务")
        self.stopping = False
        self.setup_encryption()
        
        # 启动所有用户的采集线程
        for user_id in list(self.user_consents.keys()):
            self._start_collection_thread(user_id)
        
        logger.info(f"后台数据采集服务已启动，当前活动用户数: {len(self.collection_threads)}")
    
    def stop(self):
        """停止后台数据采集服务"""
        if not self.enabled:
            return
            
        logger.info("停止后台数据采集服务")
        self.stopping = True
        
        # 停止所有采集线程
        for user_id in list(self.collection_threads.keys()):
            self._stop_collection_thread(user_id)
            
        # 同步所有缓存数据
        for user_id in list(self.data_cache.keys()):
            self._sync_user_data(user_id)
        
        logger.info("后台数据采集服务已停止")
    
    def _start_collection_thread(self, user_id: str):
        """启动用户的数据采集线程"""
        if self.stopping:
            return
            
        if user_id in self.collection_threads and self.collection_threads[user_id].is_alive():
            logger.debug(f"用户 {user_id} 的采集线程已在运行")
            return
        
        logger.info(f"启动用户 {user_id} 的数据采集线程")
        
        thread = threading.Thread(
            target=self._collection_worker,
            args=(user_id,),
            daemon=True,
            name=f"collector-{user_id}"
        )
        self.collection_threads[user_id] = thread
        thread.start()
    
    def _stop_collection_thread(self, user_id: str):
        """停止用户的数据采集线程"""
        if user_id not in self.collection_threads:
            return
            
        logger.info(f"停止用户 {user_id} 的数据采集线程")
        # 线程是daemon，会自然终止，只需要从字典中移除
        del self.collection_threads[user_id]
    
    def _collection_worker(self, user_id: str):
        """
        数据采集工作线程
        
        Args:
            user_id: 用户ID
        """
        logger.info(f"用户 {user_id} 的数据采集线程已启动")
        
        # 数据类型到上次采集时间的映射
        last_collection = {}
        
        # 初始化数据缓存
        with self.cache_lock:
            if user_id not in self.data_cache:
                self.data_cache[user_id] = {}
        
        # 设置默认采集间隔
        default_intervals = {
            "pulse": 60,      # 每分钟
            "sleep": 300,     # 每5分钟
            "activity": 120,  # 每2分钟
            "environment": 600,  # 每10分钟
            "voice": 1800     # 每30分钟
        }
        
        while not self.stopping and user_id in self.user_consents:
            try:
                # 检查同意是否过期
                consent = self.user_consents[user_id]
                if datetime.now() > consent["expiry"]:
                    logger.info(f"用户 {user_id} 的数据采集同意已过期，停止采集")
                    break
                
                # 获取此用户同意的数据类型
                data_types = consent["data_types"]
                
                # 检查电池状态并调整采集频率
                battery_level = self._get_battery_level()
                battery_multiplier = 1
                if battery_level <= self.battery_threshold_critical:
                    battery_multiplier = self.interval_multiplier_critical
                    logger.warning(f"电池电量严重不足 ({battery_level}%)，大幅降低采集频率")
                elif battery_level <= self.battery_threshold_low:
                    battery_multiplier = self.interval_multiplier_low
                    logger.info(f"电池电量不足 ({battery_level}%)，降低采集频率")
                
                # 检查用户活动状态来优化采集
                user_state = self._detect_user_state(user_id)
                
                # 对每种数据类型进行采集
                for data_type in data_types:
                    # 获取该类型的采集间隔
                    base_interval = self.collection_intervals.get(user_id, {}).get(
                        data_type, default_intervals.get(data_type, 300)
                    )
                    
                    # 根据电池状态和用户状态调整间隔
                    adjusted_interval = base_interval * battery_multiplier
                    
                    # 用户休眠时，除了睡眠数据外，其他类型可以进一步降低采集频率
                    if user_state == "sleeping" and data_type != "sleep":
                        adjusted_interval = adjusted_interval * 2
                    
                    # 检查是否到达采集时间
                    current_time = time.time()
                    if data_type not in last_collection or (current_time - last_collection[data_type]) >= adjusted_interval:
                        # 执行数据采集
                        collector = self.collectors.get(data_type)
                        if collector:
                            try:
                                data = collector(user_id)
                                if data:
                                    # 缓存数据
                                    self._cache_data(user_id, data_type, data)
                                    last_collection[data_type] = current_time
                            except Exception as e:
                                logger.error(f"用户 {user_id} 的 {data_type} 数据采集失败: {str(e)}")
                
                # 定期同步数据
                sync_interval = 900  # 每15分钟
                # 低电量状态下减少同步频率
                if battery_level <= self.battery_threshold_low:
                    sync_interval = 1800  # 每30分钟
                
                if user_id not in self.last_sync_time or (current_time - self.last_sync_time.get(user_id, 0)) >= sync_interval:
                    self._sync_user_data(user_id)
                
                # 睡眠一段时间
                sleep_time = 10
                if battery_level <= self.battery_threshold_critical:
                    sleep_time = 30  # 严重低电量状态下降低循环频率
                elif battery_level <= self.battery_threshold_low:
                    sleep_time = 20  # 低电量状态下降低循环频率
                
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"用户 {user_id} 的数据采集线程出错: {str(e)}")
                time.sleep(30)  # 出错后等待30秒再继续
        
        logger.info(f"用户 {user_id} 的数据采集线程已停止")
    
    def _cache_data(self, user_id: str, data_type: str, data: Any):
        """
        缓存采集的数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data: 采集的数据
        """
        with self.cache_lock:
            if user_id not in self.data_cache:
                self.data_cache[user_id] = {}
                
            if data_type not in self.data_cache[user_id]:
                self.data_cache[user_id][data_type] = []
            
            # 添加时间戳
            data_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            
            # 加密数据（如果已设置加密）
            if self.privacy_service and self.encryption_key:
                try:
                    data_str = json.dumps(data_entry)
                    encrypted_data = self.privacy_service.encrypt_data(data_str, self.encryption_key)
                    self.data_cache[user_id][data_type].append(encrypted_data)
                except Exception as e:
                    logger.error(f"数据加密失败: {str(e)}")
                    # 回退到未加密存储
                    self.data_cache[user_id][data_type].append(data_entry)
            else:
                self.data_cache[user_id][data_type].append(data_entry)
            
            # 限制缓存大小，保留最新的100条记录
            max_cache_size = 100
            if len(self.data_cache[user_id][data_type]) > max_cache_size:
                self.data_cache[user_id][data_type] = self.data_cache[user_id][data_type][-max_cache_size:]
            
            # 如果已集成危机报警服务，将数据传递给它进行分析
            if hasattr(self, 'crisis_alert_service') and self.crisis_alert_service:
                try:
                    # 传递数据给危机报警服务进行分析
                    self.crisis_alert_service._process_collected_data(user_id, data_type, data)
                except Exception as e:
                    logger.error(f"传递数据到危机报警服务失败: {str(e)}")
    
    def _sync_user_data(self, user_id: str):
        """
        同步用户缓存的数据到服务器
        
        Args:
            user_id: 用户ID
        """
        try:
            with self.cache_lock:
                if user_id not in self.data_cache:
                    return
                    
                data_to_sync = {}
                for data_type in self.data_cache[user_id]:
                    if self.data_cache[user_id][data_type]:
                        data_to_sync[data_type] = self.data_cache[user_id][data_type]
                        # 清空已同步的数据
                        self.data_cache[user_id][data_type] = []
            
            if not data_to_sync:
                return
                
            # 实际应用中，这里会调用API将数据同步到服务器
            # 此处仅记录日志
            data_counts = {dt: len(data) for dt, data in data_to_sync.items()}
            logger.info(f"同步用户 {user_id} 的数据: {data_counts}")
            
            # 更新同步时间
            self.last_sync_time[user_id] = time.time()
            
        except Exception as e:
            logger.error(f"同步用户 {user_id} 的数据失败: {str(e)}")
    
    def _get_battery_level(self) -> int:
        """
        获取设备电池电量
        
        Returns:
            电池电量百分比
        """
        try:
            # 尝试多种方式获取电池信息
            battery_level = None
            
            # 检测运行平台
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                try:
                    # 使用pmset命令获取电池信息
                    import subprocess
                    result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
                    if result.returncode == 0:
                        output = result.stdout
                        # 解析输出 - 格式通常为 "Battery status: xx% charged"
                        import re
                        match = re.search(r'(\d+)%', output)
                        if match:
                            battery_level = int(match.group(1))
                except Exception as e:
                    logger.warning(f"通过pmset获取电池信息失败: {str(e)}")
            
            elif system == "Linux":
                try:
                    # 尝试从系统文件读取电池信息
                    energy_now_path = "/sys/class/power_supply/BAT0/energy_now"
                    energy_full_path = "/sys/class/power_supply/BAT0/energy_full"
                    
                    # 读取当前和最大能量值
                    with open(energy_now_path, 'r') as f_now, open(energy_full_path, 'r') as f_full:
                        energy_now = float(f_now.read().strip())
                        energy_full = float(f_full.read().strip())
                        
                    # 计算百分比
                    if energy_full > 0:
                        battery_level = int((energy_now / energy_full) * 100)
                except Exception as e:
                    logger.warning(f"从系统文件读取电池信息失败: {str(e)}")
                    
                    # 备用方法：使用acpi命令
                    try:
                        import subprocess
                        result = subprocess.run(['acpi', '-b'], capture_output=True, text=True)
                        if result.returncode == 0:
                            output = result.stdout
                            # 解析输出 - 格式通常为 "Battery x: xx%"
                            import re
                            match = re.search(r'(\d+)%', output)
                            if match:
                                battery_level = int(match.group(1))
                    except Exception as e:
                        logger.warning(f"通过acpi获取电池信息失败: {str(e)}")
            
            elif system == "Windows":
                try:
                    # 使用WMI获取电池信息
                    import wmi
                    w = wmi.WMI()
                    for battery in w.Win32_Battery():
                        battery_level = battery.EstimatedChargeRemaining
                        break
                except Exception as e:
                    logger.warning(f"通过WMI获取电池信息失败: {str(e)}")
                    
                    # 备用方法：使用PowerShell
                    try:
                        import subprocess
                        cmd = 'powershell "(Get-WmiObject -Class Win32_Battery).EstimatedChargeRemaining"'
                        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                        if result.returncode == 0:
                            output = result.stdout.strip()
                            if output.isdigit():
                                battery_level = int(output)
                    except Exception as e:
                        logger.warning(f"通过PowerShell获取电池信息失败: {str(e)}")
            
            # 针对移动平台 - 假设我们使用某种Flutter/Native桥接
            # 在实际应用中，这部分代码会通过特定平台的桥接来获取电池信息
            if battery_level is None:
                try:
                    from internal.platform.battery_bridge import get_battery_level
                    battery_level = get_battery_level()
                except (ImportError, AttributeError) as e:
                    logger.warning(f"通过平台桥接获取电池信息失败: {str(e)}")
            
            # 如果所有方法都失败，返回默认值
            if battery_level is None:
                logger.info("无法获取电池信息，使用默认值")
                return 80
            
            return battery_level
                
        except Exception as e:
            logger.error(f"获取电池电量失败: {str(e)}")
            return 100  # 获取失败时假设电量充足，避免影响正常功能
    
    def _detect_user_state(self, user_id: str) -> str:
        """
        检测用户当前状态，用于智能调整采集策略
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户状态：'active', 'idle', 'sleeping'等
        """
        try:
            # 从数据缓存中分析用户状态
            with self.cache_lock:
                if user_id in self.data_cache:
                    # 检查最近的睡眠数据
                    if "sleep" in self.data_cache[user_id] and self.data_cache[user_id]["sleep"]:
                        recent_sleep = self.data_cache[user_id]["sleep"][-1]
                        if isinstance(recent_sleep, dict) and "data" in recent_sleep:
                            if recent_sleep["data"].get("state") == "sleeping":
                                return "sleeping"
                    
                    # 检查最近的活动数据
                    if "activity" in self.data_cache[user_id] and self.data_cache[user_id]["activity"]:
                        recent_activity = self.data_cache[user_id]["activity"][-1]
                        if isinstance(recent_activity, dict) and "data" in recent_activity:
                            activity_type = recent_activity["data"].get("activity_type")
                            if activity_type in ["walking", "running", "exercise"]:
                                return "active"
            
            # 默认为闲置状态
            return "idle"
        
        except Exception as e:
            logger.error(f"检测用户状态失败: {str(e)}")
            return "idle"  # 失败时返回默认状态
    
    # 以下是各种数据类型的具体采集函数
    def _collect_pulse_data(self, user_id: str) -> Dict[str, Any]:
        """采集脉搏数据"""
        # 在实际应用中，这里会与设备传感器交互
        # 此处仅返回模拟数据
        return {
            "pulse_rate": 75 + hash(f"{user_id}:{time.time()}")%10,  # 模拟心率在75-84之间
            "rhythm": "regular",
            "strength": "moderate"
        }
    
    def _collect_sleep_data(self, user_id: str) -> Dict[str, Any]:
        """采集睡眠数据"""
        # 在实际应用中，这里会分析加速度计、声音等数据
        # 此处仅返回模拟数据
        current_hour = datetime.now().hour
        is_night = current_hour >= 22 or current_hour <= 6
        return {
            "state": "sleeping" if is_night else "awake",
            "movement_level": 0.2 if is_night else 0.8,
            "duration": 0 if not is_night else (current_hour - 22 if current_hour >= 22 else current_hour + 8)
        }
    
    def _collect_activity_data(self, user_id: str) -> Dict[str, Any]:
        """采集活动数据"""
        # 在实际应用中，这里会使用加速度计、GPS等数据
        # 此处仅返回模拟数据
        current_hour = datetime.now().hour
        is_active_time = 8 <= current_hour <= 21
        return {
            "step_count": hash(f"{user_id}:{time.time()}")%100 if is_active_time else 0,
            "activity_type": "walking" if is_active_time else "stationary",
            "intensity": 0.6 if is_active_time else 0.1
        }
    
    def _collect_environment_data(self, user_id: str) -> Dict[str, Any]:
        """采集环境数据"""
        # 在实际应用中，这里会使用麦克风、光线传感器等
        # 此处仅返回模拟数据
        current_hour = datetime.now().hour
        is_daytime = 7 <= current_hour <= 18
        return {
            "noise_level": 40 + hash(f"{user_id}:{time.time()}")%30,  # 模拟40-70分贝
            "light_level": 800 if is_daytime else 50,  # 白天vs夜晚亮度
            "estimated_location_type": "indoor"  # 估计的位置类型
        }
    
    def _collect_voice_data(self, user_id: str) -> Dict[str, Any]:
        """采集声音特征数据"""
        # 在实际应用中，这里会使用麦克风进行被动监听
        # 此处仅返回模拟数据
        current_hour = datetime.now().hour
        is_speaking_time = 9 <= current_hour <= 22
        return {
            "speech_detected": hash(f"{user_id}:{time.time()}")%10 > 7 and is_speaking_time,  # 70%几率检测到说话
            "voice_features": {
                "pitch": 220 + hash(f"{user_id}")%40,  # 基频
                "energy": 0.6 if is_speaking_time else 0.2
            },
            "duration": hash(f"{user_id}:{time.time()}")%60 if is_speaking_time else 0  # 说话持续时间0-60秒
        }
    
    def get_recent_data(self, user_id: str, data_type: str, limit: int = 10) -> Dict[str, Any]:
        """
        获取用户最近的特定类型数据
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            limit: 返回的最大记录数
            
        Returns:
            包含最近数据的字典
        """
        result = {
            "success": False,
            "message": "未找到数据",
            "data": []
        }
        
        try:
            with self.cache_lock:
                if (user_id in self.data_cache and 
                    data_type in self.data_cache[user_id] and 
                    self.data_cache[user_id][data_type]):
                    
                    # 取最近的数据
                    recent_data = self.data_cache[user_id][data_type][-limit:]
                    
                    # 解密数据（如果需要）
                    decrypted_data = []
                    for item in recent_data:
                        if isinstance(item, str) and self.privacy_service and self.encryption_key:
                            try:
                                decrypted_item = self.privacy_service.decrypt_data(item, self.encryption_key)
                                decrypted_data.append(json.loads(decrypted_item))
                            except Exception as e:
                                logger.error(f"数据解密失败: {str(e)}")
                                # 如果解密失败，尝试直接使用
                                decrypted_data.append(item)
                        else:
                            decrypted_data.append(item)
                    
                    result = {
                        "success": True,
                        "message": "成功获取数据",
                        "data": decrypted_data
                    }
            
            return result
        
        except Exception as e:
            logger.error(f"获取用户 {user_id} 的 {data_type} 数据失败: {str(e)}")
            result["message"] = f"获取数据失败: {str(e)}"
            return result
    
    def clear_user_data(self, user_id: str, data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        清除用户数据
        
        Args:
            user_id: 用户ID
            data_types: 要清除的数据类型列表，None表示清除所有
            
        Returns:
            包含操作结果的字典
        """
        try:
            with self.cache_lock:
                if user_id not in self.data_cache:
                    return {"success": False, "message": "未找到用户数据"}
                
                if data_types is None:
                    # 清除所有数据
                    del self.data_cache[user_id]
                    logger.info(f"已清除用户 {user_id} 的所有数据")
                    return {"success": True, "message": "已清除所有数据"}
                else:
                    # 清除特定类型的数据
                    cleared_types = []
                    for dt in data_types:
                        if dt in self.data_cache[user_id]:
                            del self.data_cache[user_id][dt]
                            cleared_types.append(dt)
                    
                    if not cleared_types:
                        return {"success": False, "message": "未找到指定类型的数据"}
                    
                    logger.info(f"已清除用户 {user_id} 的数据类型: {cleared_types}")
                    return {
                        "success": True, 
                        "message": f"已清除指定类型的数据", 
                        "cleared_types": cleared_types
                    }
        
        except Exception as e:
            logger.error(f"清除用户 {user_id} 数据失败: {str(e)}")
            return {"success": False, "message": f"清除数据失败: {str(e)}"}
            
    def export_user_data(self, user_id: str, data_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        导出用户数据
        
        Args:
            user_id: 用户ID
            data_types: 要导出的数据类型列表，None表示导出所有
            
        Returns:
            包含导出数据的字典
        """
        try:
            with self.cache_lock:
                if user_id not in self.data_cache:
                    return {"success": False, "message": "未找到用户数据"}
                
                export_data = {}
                
                if data_types is None:
                    # 导出所有数据
                    data_types = list(self.data_cache[user_id].keys())
                
                for dt in data_types:
                    if dt in self.data_cache[user_id]:
                        # 解密数据（如果需要）
                        decrypted_data = []
                        for item in self.data_cache[user_id][dt]:
                            if isinstance(item, str) and self.privacy_service and self.encryption_key:
                                try:
                                    decrypted_item = self.privacy_service.decrypt_data(item, self.encryption_key)
                                    decrypted_data.append(json.loads(decrypted_item))
                                except Exception as e:
                                    logger.error(f"数据解密失败: {str(e)}")
                                    decrypted_data.append(item)
                            else:
                                decrypted_data.append(item)
                        
                        export_data[dt] = decrypted_data
                
                if not export_data:
                    return {"success": False, "message": "未找到指定类型的数据"}
                
                logger.info(f"已导出用户 {user_id} 的数据类型: {list(export_data.keys())}")
                return {
                    "success": True,
                    "message": "成功导出数据",
                    "export_data": export_data,
                    "data_types": list(export_data.keys()),
                    "timestamp": datetime.now().isoformat(),
                    "data_points": {dt: len(data) for dt, data in export_data.items()}
                }
        
        except Exception as e:
            logger.error(f"导出用户 {user_id} 数据失败: {str(e)}")
            return {"success": False, "message": f"导出数据失败: {str(e)}"} 