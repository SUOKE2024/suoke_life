#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能设备管理器
提供设备自动发现、连接管理、故障检测和自动恢复功能
支持多设备并发管理和负载均衡
"""

import asyncio
import logging
import time
import json
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import weakref

from internal.signal.device_adapter import (
    BaseDeviceAdapter, DeviceAdapterFactory, DeviceType, PressurePosition
)
from internal.model.pulse_models import DeviceInfo, SensorCalibrationData

logger = logging.getLogger(__name__)

class DeviceStatus(Enum):
    """设备状态枚举"""
    UNKNOWN = auto()
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    CALIBRATING = auto()
    READY = auto()
    ACQUIRING = auto()
    ERROR = auto()
    MAINTENANCE = auto()

class ConnectionType(Enum):
    """连接类型枚举"""
    USB = auto()
    BLUETOOTH = auto()
    WIFI = auto()
    SERIAL = auto()
    NETWORK = auto()

@dataclass
class DeviceHealth:
    """设备健康状态"""
    status: DeviceStatus
    last_heartbeat: datetime
    error_count: int = 0
    connection_quality: float = 1.0  # 0-1
    signal_quality: float = 1.0      # 0-1
    battery_level: Optional[float] = None  # 0-1
    temperature: Optional[float] = None    # 摄氏度
    uptime: timedelta = field(default_factory=lambda: timedelta())
    last_error: Optional[str] = None

@dataclass
class DeviceMetrics:
    """设备性能指标"""
    total_sessions: int = 0
    successful_sessions: int = 0
    failed_sessions: int = 0
    average_session_duration: float = 0.0
    data_throughput: float = 0.0  # 数据吞吐量 (samples/sec)
    last_calibration: Optional[datetime] = None
    calibration_drift: float = 0.0

class SmartDeviceManager:
    """智能设备管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能设备管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.devices: Dict[str, BaseDeviceAdapter] = {}
        self.device_health: Dict[str, DeviceHealth] = {}
        self.device_metrics: Dict[str, DeviceMetrics] = {}
        
        # 管理配置
        self.auto_discovery = config.get('auto_discovery', True)
        self.auto_reconnect = config.get('auto_reconnect', True)
        self.health_check_interval = config.get('health_check_interval', 30)  # 秒
        self.max_retry_attempts = config.get('max_retry_attempts', 3)
        self.connection_timeout = config.get('connection_timeout', 10)  # 秒
        
        # 负载均衡配置
        self.load_balancing = config.get('load_balancing', {})
        self.max_concurrent_sessions = self.load_balancing.get('max_concurrent_sessions', 5)
        self.session_distribution = self.load_balancing.get('strategy', 'round_robin')
        
        # 故障检测配置
        self.fault_detection = config.get('fault_detection', {})
        self.max_error_rate = self.fault_detection.get('max_error_rate', 0.1)
        self.min_signal_quality = self.fault_detection.get('min_signal_quality', 0.7)
        
        # 内部状态
        self.active_sessions: Dict[str, Set[str]] = {}  # device_id -> session_ids
        self.session_queue: asyncio.Queue = asyncio.Queue()
        self.device_locks: Dict[str, asyncio.Lock] = {}
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = {
            'device_connected': [],
            'device_disconnected': [],
            'device_error': [],
            'session_started': [],
            'session_completed': [],
            'calibration_required': []
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        
        logger.info("智能设备管理器初始化完成")
    
    async def start(self):
        """启动设备管理器"""
        if self.running:
            return
        
        self.running = True
        
        # 启动后台任务
        self.background_tasks = [
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._auto_discovery_task()),
            asyncio.create_task(self._session_processor()),
            asyncio.create_task(self._metrics_collector())
        ]
        
        # 初始设备发现
        if self.auto_discovery:
            await self._discover_devices()
        
        logger.info("设备管理器已启动")
    
    async def stop(self):
        """停止设备管理器"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止所有会话
        for device_id in list(self.active_sessions.keys()):
            await self._stop_device_sessions(device_id)
        
        # 断开所有设备
        for device_id in list(self.devices.keys()):
            await self._disconnect_device(device_id)
        
        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()
        
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        logger.info("设备管理器已停止")
    
    async def register_device(self, device_config: Dict[str, Any]) -> str:
        """
        注册新设备
        
        Args:
            device_config: 设备配置
            
        Returns:
            设备ID
        """
        try:
            # 创建设备适配器
            adapter = DeviceAdapterFactory.create_adapter(device_config)
            device_id = device_config.get('device_id', f"device_{len(self.devices)}")
            
            # 注册设备
            self.devices[device_id] = adapter
            self.device_locks[device_id] = asyncio.Lock()
            self.active_sessions[device_id] = set()
            
            # 初始化健康状态
            self.device_health[device_id] = DeviceHealth(
                status=DeviceStatus.DISCONNECTED,
                last_heartbeat=datetime.now()
            )
            
            # 初始化指标
            self.device_metrics[device_id] = DeviceMetrics()
            
            logger.info(f"设备已注册: {device_id}")
            return device_id
            
        except Exception as e:
            logger.error(f"设备注册失败: {e}")
            raise
    
    async def connect_device(self, device_id: str) -> bool:
        """
        连接设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            连接是否成功
        """
        if device_id not in self.devices:
            logger.error(f"设备不存在: {device_id}")
            return False
        
        async with self.device_locks[device_id]:
            try:
                # 更新状态
                self.device_health[device_id].status = DeviceStatus.CONNECTING
                
                # 连接设备
                adapter = self.devices[device_id]
                success = await asyncio.get_event_loop().run_in_executor(
                    self.executor, adapter.connect
                )
                
                if success:
                    self.device_health[device_id].status = DeviceStatus.CONNECTED
                    self.device_health[device_id].last_heartbeat = datetime.now()
                    self.device_health[device_id].error_count = 0
                    
                    # 触发连接事件
                    await self._trigger_event('device_connected', device_id)
                    
                    logger.info(f"设备连接成功: {device_id}")
                else:
                    self.device_health[device_id].status = DeviceStatus.ERROR
                    self.device_health[device_id].error_count += 1
                    
                    logger.error(f"设备连接失败: {device_id}")
                
                return success
                
            except Exception as e:
                self.device_health[device_id].status = DeviceStatus.ERROR
                self.device_health[device_id].last_error = str(e)
                self.device_health[device_id].error_count += 1
                
                logger.error(f"设备连接异常: {device_id}, {e}")
                return False
    
    async def disconnect_device(self, device_id: str) -> bool:
        """
        断开设备连接
        
        Args:
            device_id: 设备ID
            
        Returns:
            断开是否成功
        """
        return await self._disconnect_device(device_id)
    
    async def _disconnect_device(self, device_id: str) -> bool:
        """内部断开设备方法"""
        if device_id not in self.devices:
            return False
        
        async with self.device_locks[device_id]:
            try:
                # 停止所有会话
                await self._stop_device_sessions(device_id)
                
                # 断开设备
                adapter = self.devices[device_id]
                success = await asyncio.get_event_loop().run_in_executor(
                    self.executor, adapter.disconnect
                )
                
                # 更新状态
                self.device_health[device_id].status = DeviceStatus.DISCONNECTED
                
                # 触发断开事件
                await self._trigger_event('device_disconnected', device_id)
                
                logger.info(f"设备已断开: {device_id}")
                return success
                
            except Exception as e:
                logger.error(f"设备断开异常: {device_id}, {e}")
                return False
    
    async def calibrate_device(self, device_id: str, operator: str) -> Optional[SensorCalibrationData]:
        """
        校准设备
        
        Args:
            device_id: 设备ID
            operator: 操作员
            
        Returns:
            校准数据
        """
        if device_id not in self.devices:
            logger.error(f"设备不存在: {device_id}")
            return None
        
        async with self.device_locks[device_id]:
            try:
                # 更新状态
                self.device_health[device_id].status = DeviceStatus.CALIBRATING
                
                # 执行校准
                adapter = self.devices[device_id]
                calibration_data = await asyncio.get_event_loop().run_in_executor(
                    self.executor, adapter.calibrate, operator
                )
                
                if calibration_data:
                    # 更新指标
                    self.device_metrics[device_id].last_calibration = datetime.now()
                    self.device_metrics[device_id].calibration_drift = 0.0
                    
                    # 更新状态
                    self.device_health[device_id].status = DeviceStatus.READY
                    
                    logger.info(f"设备校准完成: {device_id}")
                else:
                    self.device_health[device_id].status = DeviceStatus.ERROR
                    logger.error(f"设备校准失败: {device_id}")
                
                return calibration_data
                
            except Exception as e:
                self.device_health[device_id].status = DeviceStatus.ERROR
                self.device_health[device_id].last_error = str(e)
                logger.error(f"设备校准异常: {device_id}, {e}")
                return None
    
    async def start_session(self, session_id: str, device_preference: Optional[str] = None) -> Optional[str]:
        """
        开始数据采集会话
        
        Args:
            session_id: 会话ID
            device_preference: 首选设备ID
            
        Returns:
            分配的设备ID
        """
        # 选择最佳设备
        device_id = await self._select_best_device(device_preference)
        
        if not device_id:
            logger.error(f"没有可用设备用于会话: {session_id}")
            return None
        
        async with self.device_locks[device_id]:
            try:
                # 检查设备状态
                if self.device_health[device_id].status not in [DeviceStatus.READY, DeviceStatus.CONNECTED]:
                    logger.error(f"设备状态不可用: {device_id}, {self.device_health[device_id].status}")
                    return None
                
                # 启动采集
                adapter = self.devices[device_id]
                success = await asyncio.get_event_loop().run_in_executor(
                    self.executor, adapter.start_acquisition, session_id
                )
                
                if success:
                    # 更新状态
                    self.device_health[device_id].status = DeviceStatus.ACQUIRING
                    self.active_sessions[device_id].add(session_id)
                    
                    # 更新指标
                    self.device_metrics[device_id].total_sessions += 1
                    
                    # 触发事件
                    await self._trigger_event('session_started', device_id, session_id)
                    
                    logger.info(f"会话已启动: {session_id} on {device_id}")
                    return device_id
                else:
                    logger.error(f"会话启动失败: {session_id} on {device_id}")
                    return None
                
            except Exception as e:
                logger.error(f"会话启动异常: {session_id} on {device_id}, {e}")
                return None
    
    async def stop_session(self, session_id: str, device_id: str) -> bool:
        """
        停止数据采集会话
        
        Args:
            session_id: 会话ID
            device_id: 设备ID
            
        Returns:
            停止是否成功
        """
        if device_id not in self.devices:
            return False
        
        async with self.device_locks[device_id]:
            try:
                # 停止采集
                adapter = self.devices[device_id]
                success = await asyncio.get_event_loop().run_in_executor(
                    self.executor, adapter.stop_acquisition
                )
                
                # 更新状态
                if session_id in self.active_sessions[device_id]:
                    self.active_sessions[device_id].remove(session_id)
                
                if not self.active_sessions[device_id]:
                    self.device_health[device_id].status = DeviceStatus.READY
                
                # 更新指标
                if success:
                    self.device_metrics[device_id].successful_sessions += 1
                else:
                    self.device_metrics[device_id].failed_sessions += 1
                
                # 触发事件
                await self._trigger_event('session_completed', device_id, session_id)
                
                logger.info(f"会话已停止: {session_id} on {device_id}")
                return success
                
            except Exception as e:
                logger.error(f"会话停止异常: {session_id} on {device_id}, {e}")
                return False
    
    async def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备状态
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备状态信息
        """
        if device_id not in self.devices:
            return None
        
        health = self.device_health[device_id]
        metrics = self.device_metrics[device_id]
        
        return {
            'device_id': device_id,
            'status': health.status.name,
            'connection_quality': health.connection_quality,
            'signal_quality': health.signal_quality,
            'battery_level': health.battery_level,
            'temperature': health.temperature,
            'error_count': health.error_count,
            'last_error': health.last_error,
            'uptime': health.uptime.total_seconds(),
            'active_sessions': len(self.active_sessions[device_id]),
            'total_sessions': metrics.total_sessions,
            'success_rate': metrics.successful_sessions / max(metrics.total_sessions, 1),
            'last_calibration': metrics.last_calibration.isoformat() if metrics.last_calibration else None
        }
    
    async def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有设备状态"""
        status = {}
        for device_id in self.devices:
            status[device_id] = await self.get_device_status(device_id)
        return status
    
    async def _select_best_device(self, preference: Optional[str] = None) -> Optional[str]:
        """选择最佳设备"""
        available_devices = []
        
        for device_id, health in self.device_health.items():
            # 检查设备是否可用
            if health.status in [DeviceStatus.READY, DeviceStatus.CONNECTED]:
                # 检查并发限制
                if len(self.active_sessions[device_id]) < self.max_concurrent_sessions:
                    available_devices.append(device_id)
        
        if not available_devices:
            return None
        
        # 如果有首选设备且可用，优先使用
        if preference and preference in available_devices:
            return preference
        
        # 根据负载均衡策略选择
        if self.session_distribution == 'round_robin':
            # 选择活跃会话最少的设备
            return min(available_devices, key=lambda d: len(self.active_sessions[d]))
        elif self.session_distribution == 'quality_based':
            # 选择信号质量最好的设备
            return max(available_devices, key=lambda d: self.device_health[d].signal_quality)
        else:
            # 默认选择第一个可用设备
            return available_devices[0]
    
    async def _health_monitor(self):
        """健康监控后台任务"""
        while self.running:
            try:
                for device_id in list(self.devices.keys()):
                    await self._check_device_health(device_id)
                
                await asyncio.sleep(self.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康监控异常: {e}")
                await asyncio.sleep(5)
    
    async def _check_device_health(self, device_id: str):
        """检查单个设备健康状态"""
        try:
            adapter = self.devices[device_id]
            health = self.device_health[device_id]
            
            # 执行健康检查
            is_healthy, message = await asyncio.get_event_loop().run_in_executor(
                self.executor, adapter.check_health
            )
            
            if is_healthy:
                health.last_heartbeat = datetime.now()
                health.connection_quality = min(health.connection_quality + 0.1, 1.0)
                
                # 如果设备从错误状态恢复
                if health.status == DeviceStatus.ERROR:
                    health.status = DeviceStatus.READY
                    health.error_count = 0
                    logger.info(f"设备已恢复: {device_id}")
            else:
                health.error_count += 1
                health.last_error = message
                health.connection_quality = max(health.connection_quality - 0.2, 0.0)
                
                # 如果错误次数过多，标记为错误状态
                if health.error_count >= self.max_retry_attempts:
                    health.status = DeviceStatus.ERROR
                    await self._trigger_event('device_error', device_id, message)
                    
                    # 自动重连
                    if self.auto_reconnect:
                        await self._attempt_reconnect(device_id)
        
        except Exception as e:
            logger.error(f"设备健康检查异常: {device_id}, {e}")
    
    async def _attempt_reconnect(self, device_id: str):
        """尝试重新连接设备"""
        try:
            logger.info(f"尝试重新连接设备: {device_id}")
            
            # 先断开
            await self._disconnect_device(device_id)
            
            # 等待一段时间
            await asyncio.sleep(5)
            
            # 重新连接
            success = await self.connect_device(device_id)
            
            if success:
                logger.info(f"设备重连成功: {device_id}")
            else:
                logger.error(f"设备重连失败: {device_id}")
                
        except Exception as e:
            logger.error(f"设备重连异常: {device_id}, {e}")
    
    async def _auto_discovery_task(self):
        """自动发现设备任务"""
        while self.running:
            try:
                if self.auto_discovery:
                    await self._discover_devices()
                
                await asyncio.sleep(60)  # 每分钟扫描一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"设备发现异常: {e}")
                await asyncio.sleep(10)
    
    async def _discover_devices(self):
        """发现新设备"""
        try:
            # 这里应该实现实际的设备发现逻辑
            # 例如：扫描USB端口、蓝牙设备、网络设备等
            logger.debug("执行设备发现扫描")
            
        except Exception as e:
            logger.error(f"设备发现失败: {e}")
    
    async def _session_processor(self):
        """会话处理器"""
        while self.running:
            try:
                # 处理会话队列中的任务
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"会话处理异常: {e}")
                await asyncio.sleep(1)
    
    async def _metrics_collector(self):
        """指标收集器"""
        while self.running:
            try:
                # 收集和更新设备指标
                for device_id in self.devices:
                    await self._update_device_metrics(device_id)
                
                await asyncio.sleep(30)  # 每30秒更新一次指标
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集异常: {e}")
                await asyncio.sleep(5)
    
    async def _update_device_metrics(self, device_id: str):
        """更新设备指标"""
        try:
            metrics = self.device_metrics[device_id]
            health = self.device_health[device_id]
            
            # 更新运行时间
            if health.status != DeviceStatus.DISCONNECTED:
                health.uptime += timedelta(seconds=30)
            
            # 计算成功率
            if metrics.total_sessions > 0:
                success_rate = metrics.successful_sessions / metrics.total_sessions
                
                # 如果成功率过低，触发警告
                if success_rate < (1 - self.max_error_rate):
                    await self._trigger_event('device_error', device_id, f"成功率过低: {success_rate:.2%}")
            
        except Exception as e:
            logger.error(f"指标更新异常: {device_id}, {e}")
    
    async def _stop_device_sessions(self, device_id: str):
        """停止设备的所有会话"""
        sessions = list(self.active_sessions[device_id])
        for session_id in sessions:
            await self.stop_session(session_id, device_id)
    
    async def _trigger_event(self, event_type: str, *args):
        """触发事件回调"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
        except Exception as e:
            logger.error(f"事件回调异常: {event_type}, {e}")
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """注册事件回调"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
        else:
            logger.warning(f"未知事件类型: {event_type}")
    
    def unregister_event_callback(self, event_type: str, callback: Callable):
        """取消注册事件回调"""
        if event_type in self.event_callbacks:
            try:
                self.event_callbacks[event_type].remove(callback)
            except ValueError:
                pass 