#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
危机报警服务 - 实现设备待机和息屏条件下的健康危机检测和报警
"""

import logging
import time
import threading
import json
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime, timedelta
import queue

logger = logging.getLogger(__name__)


class CrisisAlertService:
    """健康数据危机报警服务"""

    def __init__(self, config: Any):
        """
        初始化危机报警服务
        
        Args:
            config: 服务配置信息
        """
        self.config = config
        self.enabled = config.crisis_alert.enabled if hasattr(config, 'crisis_alert') else False
        self.alert_threads = {}  # 用户ID -> 报警监控线程
        self.alert_handlers = {}  # 警报级别 -> 处理函数
        self.alert_history = {}  # 用户ID -> 警报历史
        self.alert_contacts = {}  # 用户ID -> 紧急联系人列表
        self.alert_queue = queue.Queue()  # 待处理警报队列
        self.stopping = False  # 服务停止标志
        
        # 危机检测相关变量
        self.data_analyzers = {}  # 数据类型 -> 分析函数
        self.alert_thresholds = {}  # 用户ID -> 阈值配置
        
        # 后台数据采集服务引用（后续会注入）
        self.background_collection_service = None
        
        # 其他依赖的服务（后续会注入）
        self.monitoring_service = None
        self.notification_service = None  # 用于发送通知
        self.agent_coordination = None  # 智能体协作服务
        
        # 初始化默认分析器
        self._init_default_analyzers()
        # 初始化默认警报处理器
        self._init_default_alert_handlers()
        
        logger.info("危机报警服务初始化完成")
    
    def _init_default_analyzers(self):
        """初始化默认的数据分析器"""
        self.data_analyzers = {
            "pulse": self._analyze_pulse_data,
            "sleep": self._analyze_sleep_data,
            "activity": self._analyze_activity_data,
            "environment": self._analyze_environment_data,
            "voice": self._analyze_voice_data
        }
    
    def _init_default_alert_handlers(self):
        """初始化默认的警报处理器"""
        self.alert_handlers = {
            "info": self._handle_info_alert,
            "warning": self._handle_warning_alert,
            "danger": self._handle_danger_alert,
            "critical": self._handle_critical_alert
        }
    
    def register_analyzer(self, data_type: str, analyzer_func: Callable):
        """
        注册数据分析器
        
        Args:
            data_type: 数据类型
            analyzer_func: 分析函数，接收(user_id, data)参数，返回警报信息或None
        """
        self.data_analyzers[data_type] = analyzer_func
        logger.info(f"已注册 {data_type} 类型的数据分析器")
    
    def register_alert_handler(self, level: str, handler_func: Callable):
        """
        注册警报处理器
        
        Args:
            level: 警报级别
            handler_func: 处理函数，接收(user_id, alert_info)参数
        """
        self.alert_handlers[level] = handler_func
        logger.info(f"已注册 {level} 级别的警报处理器")
    
    def set_user_thresholds(self, user_id: str, thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        设置用户的警报阈值
        
        Args:
            user_id: 用户ID
            thresholds: 阈值配置
            
        Returns:
            设置结果
        """
        if user_id not in self.alert_thresholds:
            self.alert_thresholds[user_id] = {}
        
        # 合并新阈值
        for data_type, values in thresholds.items():
            if data_type not in self.alert_thresholds[user_id]:
                self.alert_thresholds[user_id][data_type] = {}
            
            self.alert_thresholds[user_id][data_type].update(values)
        
        logger.info(f"已为用户 {user_id} 设置警报阈值: {thresholds}")
        
        return {
            "success": True,
            "message": "成功设置警报阈值",
            "current_thresholds": self.alert_thresholds[user_id]
        }
    
    def get_user_thresholds(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的警报阈值
        
        Args:
            user_id: 用户ID
            
        Returns:
            阈值配置
        """
        if user_id not in self.alert_thresholds:
            return {"success": False, "message": "未找到用户阈值配置"}
        
        return {
            "success": True,
            "thresholds": self.alert_thresholds[user_id]
        }
    
    def set_emergency_contacts(self, user_id: str, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        设置用户的紧急联系人
        
        Args:
            user_id: 用户ID
            contacts: 联系人列表，每个联系人包含name, relation, phone, notify_level等字段
            
        Returns:
            设置结果
        """
        self.alert_contacts[user_id] = contacts
        logger.info(f"已为用户 {user_id} 设置 {len(contacts)} 个紧急联系人")
        
        return {
            "success": True,
            "message": f"成功设置 {len(contacts)} 个紧急联系人",
            "contacts": contacts
        }
    
    def get_emergency_contacts(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户的紧急联系人
        
        Args:
            user_id: 用户ID
            
        Returns:
            联系人列表
        """
        if user_id not in self.alert_contacts:
            return {"success": False, "message": "未找到用户紧急联系人"}
        
        return {
            "success": True,
            "contacts": self.alert_contacts[user_id]
        }
    
    def get_alert_history(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """
        获取用户的警报历史
        
        Args:
            user_id: 用户ID
            limit: 返回的最大记录数
            
        Returns:
            警报历史记录
        """
        if user_id not in self.alert_history:
            return {"success": True, "alerts": []}
        
        alerts = sorted(
            self.alert_history[user_id], 
            key=lambda x: x["timestamp"], 
            reverse=True
        )[:limit]
        
        return {
            "success": True,
            "alerts": alerts
        }
    
    def start(self):
        """启动危机报警服务"""
        if not self.enabled:
            logger.info("危机报警服务未启用，跳过启动")
            return
        
        if not self.background_collection_service:
            logger.error("后台数据采集服务未注入，无法启动危机报警服务")
            return
        
        logger.info("启动危机报警服务")
        self.stopping = False
        
        # 启动警报处理线程
        self.alert_processor_thread = threading.Thread(
            target=self._alert_processor_worker,
            daemon=True,
            name="alert-processor"
        )
        self.alert_processor_thread.start()
        
        # 启动所有用户的警报监控线程
        user_consents = getattr(self.background_collection_service, 'user_consents', {})
        for user_id in list(user_consents.keys()):
            self._start_alert_thread(user_id)
        
        # 注册数据采集回调
        if hasattr(self.background_collection_service, '_cache_data'):
            original_cache_data = self.background_collection_service._cache_data
            
            def wrapped_cache_data(user_id, data_type, data):
                # 调用原始函数
                original_cache_data(user_id, data_type, data)
                # 分析数据是否需要触发警报
                self._process_collected_data(user_id, data_type, data)
            
            self.background_collection_service._cache_data = wrapped_cache_data
            logger.info("已注册数据采集回调")
        
        logger.info("危机报警服务已启动")
    
    def stop(self):
        """停止危机报警服务"""
        if not self.enabled:
            return
        
        logger.info("停止危机报警服务")
        self.stopping = True
        
        # 停止所有警报监控线程
        for user_id in list(self.alert_threads.keys()):
            self._stop_alert_thread(user_id)
        
        # 恢复原始数据采集方法（如果之前修改过）
        if hasattr(self.background_collection_service, '_original_cache_data'):
            self.background_collection_service._cache_data = getattr(
                self.background_collection_service, '_original_cache_data'
            )
        
        logger.info("危机报警服务已停止")
    
    def _start_alert_thread(self, user_id: str):
        """
        启动用户的警报监控线程
        
        Args:
            user_id: 用户ID
        """
        if self.stopping:
            return
        
        if user_id in self.alert_threads and self.alert_threads[user_id].is_alive():
            logger.debug(f"用户 {user_id} 的警报监控线程已在运行")
            return
        
        logger.info(f"启动用户 {user_id} 的警报监控线程")
        
        thread = threading.Thread(
            target=self._alert_monitor_worker,
            args=(user_id,),
            daemon=True,
            name=f"alert-monitor-{user_id}"
        )
        self.alert_threads[user_id] = thread
        thread.start()
    
    def _stop_alert_thread(self, user_id: str):
        """
        停止用户的警报监控线程
        
        Args:
            user_id: 用户ID
        """
        if user_id not in self.alert_threads:
            return
        
        logger.info(f"停止用户 {user_id} 的警报监控线程")
        # 线程是daemon，会自然终止，只需要从字典中移除
        del self.alert_threads[user_id]
    
    def _alert_monitor_worker(self, user_id: str):
        """
        警报监控工作线程
        
        Args:
            user_id: 用户ID
        """
        logger.info(f"用户 {user_id} 的警报监控线程已启动")
        
        # 获取数据缓存
        data_cache = {}
        if hasattr(self.background_collection_service, 'data_cache'):
            data_cache = self.background_collection_service.data_cache.get(user_id, {})
        
        # 监控间隔
        monitor_interval = 30  # 秒
        
        while not self.stopping:
            try:
                # 检查用户数据，查找需要报警的情况
                self._check_user_data(user_id, data_cache)
                
                # 检查用户状态
                if self.background_collection_service:
                    collection_status = self.background_collection_service.get_collection_status(user_id)
                    if not collection_status.get("is_collecting", False):
                        logger.info(f"用户 {user_id} 的数据采集已停止，终止警报监控")
                        break
                
                # 睡眠一段时间
                time.sleep(monitor_interval)
                
            except Exception as e:
                logger.error(f"用户 {user_id} 的警报监控出错: {str(e)}")
                time.sleep(60)  # 出错后等待一分钟再继续
        
        logger.info(f"用户 {user_id} 的警报监控线程已停止")
    
    def _alert_processor_worker(self):
        """警报处理工作线程"""
        logger.info("警报处理线程已启动")
        
        while not self.stopping:
            try:
                # 从队列中获取警报
                try:
                    user_id, alert_info = self.alert_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # 处理警报
                self._process_alert(user_id, alert_info)
                
                # 标记任务完成
                self.alert_queue.task_done()
                
            except Exception as e:
                logger.error(f"警报处理出错: {str(e)}")
                time.sleep(5)
        
        logger.info("警报处理线程已停止")
    
    def _check_user_data(self, user_id: str, data_cache: Dict[str, List[Dict]]):
        """
        检查用户的数据缓存，查找需要报警的情况
        
        Args:
            user_id: 用户ID
            data_cache: 数据缓存
        """
        # 从数据采集服务获取最新缓存
        if self.background_collection_service and hasattr(self.background_collection_service, 'data_cache'):
            user_cache = self.background_collection_service.data_cache.get(user_id, {})
            for data_type, data_list in user_cache.items():
                # 只处理最新的数据
                if data_list and len(data_list) > 0:
                    latest_data = data_list[-1]
                    self._process_collected_data(user_id, data_type, latest_data.get("data", {}))
    
    def _process_collected_data(self, user_id: str, data_type: str, data: Dict[str, Any]):
        """
        处理采集的数据，分析是否需要触发警报
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data: 数据内容
        """
        if data_type not in self.data_analyzers:
            logger.debug(f"未找到数据类型 {data_type} 的分析器，跳过处理")
            return
        
        try:
            # 获取用户的警报阈值
            if user_id not in self.alert_thresholds or data_type not in self.alert_thresholds.get(user_id, {}):
                logger.debug(f"用户 {user_id} 未设置 {data_type} 数据的警报阈值，使用默认阈值")
                thresholds = {}
            else:
                thresholds = self.alert_thresholds.get(user_id, {}).get(data_type, {})
            
            # 分析数据
            analyzer = self.data_analyzers[data_type]
            logger.debug(f"调用 {data_type} 数据分析器处理用户 {user_id} 的数据")
            alert_info = analyzer(user_id, data, thresholds)
            
            # 如果需要触发警报
            if alert_info:
                logger.info(f"数据分析触发警报: 用户={user_id}, 类型={data_type}, 级别={alert_info.get('level', 'info')}")
                # 添加一些基本信息
                if "timestamp" not in alert_info:
                    alert_info["timestamp"] = datetime.now().isoformat()
                if "data_type" not in alert_info:
                    alert_info["data_type"] = data_type
                if "data" not in alert_info:
                    alert_info["data"] = data
                
                # 加入警报队列
                self.alert_queue.put((user_id, alert_info))
            else:
                logger.debug(f"数据分析未触发警报: 用户={user_id}, 类型={data_type}")
        except Exception as e:
            logger.error(f"处理 {data_type} 数据出错: {str(e)}")
    
    def _process_alert(self, user_id: str, alert_info: Dict[str, Any]):
        """
        处理警报
        
        Args:
            user_id: 用户ID
            alert_info: 警报信息
        """
        # 记录警报历史
        if user_id not in self.alert_history:
            self.alert_history[user_id] = []
        
        self.alert_history[user_id].append(alert_info)
        
        # 限制历史记录数量
        max_history = 100
        if len(self.alert_history[user_id]) > max_history:
            self.alert_history[user_id] = self.alert_history[user_id][-max_history:]
        
        # 根据警报级别调用相应的处理器
        level = alert_info.get("level", "info")
        if level in self.alert_handlers:
            handler = self.alert_handlers[level]
            handler(user_id, alert_info)
        else:
            logger.warning(f"未找到警报级别 {level} 的处理器")
            # 使用默认的info处理器
            self._handle_info_alert(user_id, alert_info)
    
    # 警报处理器
    def _handle_info_alert(self, user_id: str, alert_info: Dict[str, Any]):
        """处理信息级别警报"""
        logger.info(f"信息级别警报: 用户={user_id}, 内容={alert_info.get('message', '')}")
        
        # 记录指标
        if self.monitoring_service:
            self.monitoring_service.metrics_client.counter("crisis_alerts", 1, {"level": "info"})
        
        # 可以选择发送通知给用户
        if self.notification_service:
            self.notification_service.send_notification(
                user_id, 
                title="健康提示", 
                body=alert_info.get("message", ""),
                priority="normal",
                data=alert_info
            )
    
    def _handle_warning_alert(self, user_id: str, alert_info: Dict[str, Any]):
        """处理警告级别警报"""
        logger.warning(f"警告级别警报: 用户={user_id}, 内容={alert_info.get('message', '')}")
        
        # 记录指标
        if self.monitoring_service:
            self.monitoring_service.metrics_client.counter("crisis_alerts", 1, {"level": "warning"})
        
        # 发送通知给用户
        if self.notification_service:
            self.notification_service.send_notification(
                user_id, 
                title="健康警告", 
                body=alert_info.get("message", ""),
                priority="high",
                data=alert_info
            )
        
        # 通知智能体
        if self.agent_coordination:
            self.agent_coordination.event_bus.publish(
                "crisis_alert.warning",
                {
                    "user_id": user_id,
                    "alert": alert_info,
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _handle_danger_alert(self, user_id: str, alert_info: Dict[str, Any]):
        """处理危险级别警报"""
        logger.error(f"危险级别警报: 用户={user_id}, 内容={alert_info.get('message', '')}")
        
        # 记录指标
        if self.monitoring_service:
            self.monitoring_service.metrics_client.counter("crisis_alerts", 1, {"level": "danger"})
        
        # 发送高优先级通知给用户
        if self.notification_service:
            self.notification_service.send_notification(
                user_id, 
                title="健康危险警报", 
                body=alert_info.get("message", ""),
                priority="critical",
                data=alert_info
            )
        
        # 通知智能体
        if self.agent_coordination:
            self.agent_coordination.event_bus.publish(
                "crisis_alert.danger",
                {
                    "user_id": user_id,
                    "alert": alert_info,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # 通知紧急联系人
        self._notify_emergency_contacts(user_id, alert_info)
    
    def _handle_critical_alert(self, user_id: str, alert_info: Dict[str, Any]):
        """处理严重级别警报"""
        logger.critical(f"严重级别警报: 用户={user_id}, 内容={alert_info.get('message', '')}")
        
        # 记录指标
        if self.monitoring_service:
            self.monitoring_service.metrics_client.counter("crisis_alerts", 1, {"level": "critical"})
        
        # 发送高优先级通知给用户
        if self.notification_service:
            self.notification_service.send_notification(
                user_id, 
                title="严重健康警报", 
                body=alert_info.get("message", ""),
                priority="emergency",
                data=alert_info
            )
        
        # 通知智能体
        if self.agent_coordination:
            self.agent_coordination.event_bus.publish(
                "crisis_alert.critical",
                {
                    "user_id": user_id,
                    "alert": alert_info,
                    "timestamp": datetime.now().isoformat(),
                    "emergency": True
                }
            )
        
        # 通知紧急联系人
        self._notify_emergency_contacts(user_id, alert_info)
        
        # 可以考虑自动拨打紧急电话
        self._initiate_emergency_call(user_id, alert_info)
    
    def _notify_emergency_contacts(self, user_id: str, alert_info: Dict[str, Any]):
        """
        通知紧急联系人
        
        Args:
            user_id: 用户ID
            alert_info: 警报信息
        """
        if user_id not in self.alert_contacts:
            logger.warning(f"用户 {user_id} 未设置紧急联系人")
            return
        
        alert_level = alert_info.get("level", "info")
        
        for contact in self.alert_contacts[user_id]:
            # 检查联系人的通知级别
            notify_level = contact.get("notify_level", "critical")
            
            if self._should_notify_contact(alert_level, notify_level):
                # 发送通知
                if self.notification_service:
                    self.notification_service.send_emergency_notification(
                        recipient=contact,
                        user_id=user_id,
                        title=f"紧急健康警报：{alert_info.get('message', '')}",
                        body=f"用户 {user_id} 可能需要您的帮助。",
                        priority="emergency",
                        data=alert_info
                    )
                
                logger.info(f"已通知紧急联系人: {contact.get('name')} ({contact.get('relation')})")
    
    def _should_notify_contact(self, alert_level: str, notify_level: str) -> bool:
        """
        判断是否应该通知联系人
        
        Args:
            alert_level: 警报级别
            notify_level: 联系人的通知级别
            
        Returns:
            是否应该通知
        """
        level_order = {
            "info": 0,
            "warning": 1,
            "danger": 2,
            "critical": 3
        }
        
        alert_value = level_order.get(alert_level, 0)
        notify_value = level_order.get(notify_level, 3)  # 默认只在危急情况通知
        
        return alert_value >= notify_value
    
    def _initiate_emergency_call(self, user_id: str, alert_info: Dict[str, Any]):
        """
        启动紧急呼叫
        
        Args:
            user_id: 用户ID
            alert_info: 警报信息
        """
        # 实际应用中应实现紧急呼叫功能
        logger.critical(f"为用户 {user_id} 启动紧急呼叫")
        
        # 记录紧急呼叫事件
        if self.monitoring_service:
            self.monitoring_service.metrics_client.counter("emergency_calls", 1)
    
    # 数据分析器
    def _analyze_pulse_data(self, user_id: str, data: Dict[str, Any], thresholds: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析脉搏数据
        
        Args:
            user_id: 用户ID
            data: 脉搏数据
            thresholds: 阈值配置
            
        Returns:
            警报信息，如果不需要警报则返回None
        """
        if "pulse_rate" not in data:
            return None
        
        pulse_rate = data["pulse_rate"]
        
        # 默认阈值
        default_thresholds = {
            "min_normal": 60,  # 正常最低心率
            "max_normal": 100,  # 正常最高心率
            "min_warning": 50,  # 警告最低心率
            "max_warning": 120,  # 警告最高心率
            "min_danger": 40,   # 危险最低心率
            "max_danger": 140,  # 危险最高心率
            "min_critical": 30, # 严重最低心率
            "max_critical": 160 # 严重最高心率
        }
        
        # 合并用户自定义阈值
        for key, value in thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        # 判断警报级别
        if pulse_rate <= default_thresholds["min_critical"] or pulse_rate >= default_thresholds["max_critical"]:
            return {
                "level": "critical",
                "message": f"心率异常：{pulse_rate}次/分钟，需要立即就医！",
                "data_values": {"pulse_rate": pulse_rate}
            }
        elif pulse_rate <= default_thresholds["min_danger"] or pulse_rate >= default_thresholds["max_danger"]:
            return {
                "level": "danger",
                "message": f"心率异常：{pulse_rate}次/分钟，请注意您的健康状况！",
                "data_values": {"pulse_rate": pulse_rate}
            }
        elif pulse_rate <= default_thresholds["min_warning"] or pulse_rate >= default_thresholds["max_warning"]:
            return {
                "level": "warning",
                "message": f"心率波动：{pulse_rate}次/分钟，建议休息并监测变化",
                "data_values": {"pulse_rate": pulse_rate}
            }
        elif pulse_rate < default_thresholds["min_normal"] or pulse_rate > default_thresholds["max_normal"]:
            return {
                "level": "warning",
                "message": f"心率轻微偏离正常范围：{pulse_rate}次/分钟",
                "data_values": {"pulse_rate": pulse_rate}
            }
        
        return None
    
    def _analyze_sleep_data(self, user_id: str, data: Dict[str, Any], thresholds: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析睡眠数据
        
        Args:
            user_id: 用户ID
            data: 睡眠数据
            thresholds: 阈值配置
            
        Returns:
            警报信息，如果不需要警报则返回None
        """
        if "state" not in data:
            return None
        
        sleep_state = data["state"]
        movement_level = data.get("movement_level", 0.5)
        
        # 默认阈值
        default_thresholds = {
            "high_movement": 0.8,  # 睡眠中高活动水平阈值
            "very_high_movement": 0.9,  # 睡眠中极高活动水平阈值
            "low_movement_duration": 120  # 连续低活动持续时间阈值（分钟）
        }
        
        # 合并用户自定义阈值
        for key, value in thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        # 判断是否需要警报
        if sleep_state == "sleeping":
            # 检测睡眠中异常活动
            if movement_level >= default_thresholds["very_high_movement"]:
                return {
                    "level": "warning",
                    "message": "睡眠中检测到异常高活动，可能是睡眠障碍或紧急情况",
                    "data_values": {"sleep_state": sleep_state, "movement_level": movement_level}
                }
            elif movement_level >= default_thresholds["high_movement"]:
                return {
                    "level": "info",
                    "message": "睡眠质量不佳，活动水平较高",
                    "data_values": {"sleep_state": sleep_state, "movement_level": movement_level}
                }
        
        return None
    
    def _analyze_activity_data(self, user_id: str, data: Dict[str, Any], thresholds: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析活动数据
        
        Args:
            user_id: 用户ID
            data: 活动数据
            thresholds: 阈值配置
            
        Returns:
            警报信息，如果不需要警报则返回None
        """
        if "activity_type" not in data or "duration" not in data:
            return None
        
        activity_type = data["activity_type"]
        duration = data["duration"]  # 持续时间（分钟）
        intensity = data.get("intensity", 0.5)  # 活动强度（0-1）
        
        # 默认阈值
        default_thresholds = {
            "no_movement_duration": 120,  # 无活动持续时间阈值（分钟）
            "high_intensity_duration": 60,  # 高强度活动持续时间阈值（分钟）
            "fall_detection": 0.8  # 跌倒检测阈值
        }
        
        # 合并用户自定义阈值
        for key, value in thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        # 跌倒检测
        if activity_type == "fall" and data.get("fall_probability", 0) >= default_thresholds["fall_detection"]:
            return {
                "level": "critical",
                "message": "检测到可能的跌倒，请确认用户安全状况",
                "data_values": {"activity_type": activity_type, "fall_probability": data.get("fall_probability")}
            }
        
        # 长时间无活动检测
        if activity_type == "stationary" and duration >= default_thresholds["no_movement_duration"]:
            return {
                "level": "warning",
                "message": f"用户已经保持静止状态超过{duration}分钟，可能需要检查",
                "data_values": {"activity_type": activity_type, "duration": duration}
            }
        
        # 过长高强度活动检测
        if activity_type in ["running", "exercise"] and intensity > 0.7 and duration >= default_thresholds["high_intensity_duration"]:
            return {
                "level": "info",
                "message": f"用户高强度活动已持续{duration}分钟，建议适时休息",
                "data_values": {"activity_type": activity_type, "duration": duration, "intensity": intensity}
            }
        
        return None
    
    def _analyze_environment_data(self, user_id: str, data: Dict[str, Any], thresholds: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析环境数据
        
        Args:
            user_id: 用户ID
            data: 环境数据
            thresholds: 阈值配置
            
        Returns:
            警报信息，如果不需要警报则返回None
        """
        if "noise_level" not in data:
            return None
        
        noise_level = data["noise_level"]
        
        # 默认阈值（分贝）
        default_thresholds = {
            "high_noise": 85,  # 高噪音阈值
            "very_high_noise": 100  # 极高噪音阈值
        }
        
        # 合并用户自定义阈值
        for key, value in thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        # 判断是否需要警报
        if noise_level >= default_thresholds["very_high_noise"]:
            return {
                "level": "warning",
                "message": f"环境噪音极高：{noise_level}分贝，可能损伤听力",
                "data_values": {"noise_level": noise_level}
            }
        elif noise_level >= default_thresholds["high_noise"]:
            return {
                "level": "info",
                "message": f"环境噪音较高：{noise_level}分贝，建议注意听力保护",
                "data_values": {"noise_level": noise_level}
            }
        
        return None
    
    def _analyze_voice_data(self, user_id: str, data: Dict[str, Any], thresholds: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        分析语音数据
        
        Args:
            user_id: 用户ID
            data: 语音数据
            thresholds: 阈值配置
            
        Returns:
            警报信息，如果不需要警报则返回None
        """
        if "voice_features" not in data:
            return None
        
        voice_features = data["voice_features"]
        sentiment = data.get("sentiment", {})
        content = data.get("content", "")
        
        # 默认阈值
        default_thresholds = {
            "stress_level": 0.75,  # 压力水平阈值
            "negative_emotion": 0.8,  # 负面情绪阈值
            "speech_clarity_change": 0.3  # 语音清晰度变化阈值
        }
        
        # 合并用户自定义阈值
        for key, value in thresholds.items():
            if key in default_thresholds:
                default_thresholds[key] = value
        
        # 检测紧急关键词
        emergency_keywords = [
            "救命", "帮帮我", "紧急", "危险", "不行了", "晕倒", "摔倒",
            "help", "emergency", "urgent", "danger", "faint", "fall"
        ]
        
        for keyword in emergency_keywords:
            if keyword in content.lower():
                return {
                    "level": "critical",
                    "message": f"语音中检测到紧急关键词：{keyword}",
                    "data_values": {"content": content, "keyword": keyword}
                }
        
        # 检测压力水平
        if voice_features.get("stress_level", 0) >= default_thresholds["stress_level"]:
            return {
                "level": "warning",
                "message": "语音分析显示用户压力水平较高",
                "data_values": {"stress_level": voice_features.get("stress_level")}
            }
        
        # 检测负面情绪
        if sentiment.get("negative", 0) >= default_thresholds["negative_emotion"]:
            return {
                "level": "warning",
                "message": "语音情感分析显示用户情绪低落",
                "data_values": {"negative_emotion": sentiment.get("negative")}
            }
        
        # 检测语音清晰度变化（可能表明健康状况变化）
        if "clarity_change" in voice_features and abs(voice_features["clarity_change"]) >= default_thresholds["speech_clarity_change"]:
            change_direction = "下降" if voice_features["clarity_change"] < 0 else "上升"
            return {
                "level": "info",
                "message": f"语音清晰度{change_direction}，可能表明健康状况变化",
                "data_values": {"clarity_change": voice_features["clarity_change"]}
            }
        
        return None
    
    # 智能体协作相关方法
    def integrate_with_agents(self, agent_coordination_service):
        """
        与智能体协作服务集成
        
        Args:
            agent_coordination_service: 智能体协作服务
        """
        self.agent_coordination = agent_coordination_service
        logger.info("危机报警服务已与智能体协作服务集成")
        
        # 注册事件监听
        if hasattr(agent_coordination_service, 'event_bus'):
            agent_coordination_service.event_bus.subscribe(
                "agent.health_recommendation", 
                self._handle_agent_recommendation
            )
            logger.info("已订阅智能体健康建议事件")
    
    def _handle_agent_recommendation(self, event_data):
        """
        处理智能体发送的健康建议
        
        Args:
            event_data: 事件数据
        """
        user_id = event_data.get("user_id")
        if not user_id:
            return
        
        recommendation = event_data.get("recommendation", {})
        priority = recommendation.get("priority", "normal")
        
        # 高优先级建议可能需要报警
        if priority in ["high", "urgent"]:
            alert_info = {
                "level": "warning" if priority == "high" else "danger",
                "message": recommendation.get("message", "智能体发现潜在健康风险"),
                "source": recommendation.get("agent_id", "unknown_agent"),
                "data_type": "agent_recommendation",
                "timestamp": datetime.now().isoformat(),
                "recommendation_data": recommendation
            }
            
            # 加入警报队列
            self.alert_queue.put((user_id, alert_info))
            
            logger.info(f"已将智能体{recommendation.get('agent_id')}的建议转为警报")
    
    def request_agent_assistance(self, user_id: str, alert_info: Dict[str, Any]):
        """
        请求智能体协助处理警报
        
        Args:
            user_id: 用户ID
            alert_info: 警报信息
            
        Returns:
            协助请求结果
        """
        if not self.agent_coordination:
            logger.warning("未集成智能体协作服务，无法请求协助")
            return {"success": False, "message": "未集成智能体协作服务"}
        
        # 根据警报类型确定请求哪个智能体
        agent_id = self._determine_responsible_agent(alert_info)
        
        # 发送协助请求
        response = self.agent_coordination.request_assistance(
            agent_id=agent_id,
            user_id=user_id,
            context={
                "alert_info": alert_info,
                "alert_history": self.get_alert_history(user_id, limit=5).get("alerts", []),
                "request_time": datetime.now().isoformat()
            },
            priority="high" if alert_info.get("level") in ["danger", "critical"] else "normal"
        )
        
        logger.info(f"已请求智能体{agent_id}协助处理警报，响应：{response}")
        return response
    
    def _determine_responsible_agent(self, alert_info: Dict[str, Any]) -> str:
        """
        确定应该处理警报的智能体
        
        Args:
            alert_info: 警报信息
            
        Returns:
            智能体ID
        """
        data_type = alert_info.get("data_type", "")
        level = alert_info.get("level", "info")
        
        # 对应于项目中的四大智能体
        if level in ["danger", "critical"]:
            return "xiaoke"  # 小克负责医疗资源调度，适合处理紧急情况
        elif data_type == "sleep":
            return "laoke"   # 老克负责睡眠相关问题
        elif data_type in ["pulse", "voice", "activity"]:
            return "xiaoai"  # 小艾负责四诊协调，适合处理生理数据异常
        elif "environment" in data_type:
            return "soer"    # 索儿负责健康管理，适合处理环境因素
        else:
            return "laoke"   # 老克负责知识传播，可以提供健康建议 