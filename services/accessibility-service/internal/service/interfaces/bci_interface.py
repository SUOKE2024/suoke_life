#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
脑机接口(BCI)服务接口定义
为重度运动障碍用户提供思维控制和神经反馈功能的标准接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class BCIDeviceType(Enum):
    """BCI设备类型"""
    EEG = "eeg"                        # 脑电图
    FNIRS = "fnirs"                    # 功能性近红外光谱
    EMG = "emg"                        # 肌电图
    EOG = "eog"                        # 眼电图
    ECOG = "ecog"                      # 皮层脑电图
    IMPLANTED = "implanted"            # 植入式电极
    HYBRID = "hybrid"                  # 混合式BCI


class SignalType(Enum):
    """信号类型"""
    P300 = "p300"                      # P300事件相关电位
    SSVEP = "ssvep"                    # 稳态视觉诱发电位
    MI = "motor_imagery"               # 运动想象
    ERD_ERS = "erd_ers"               # 事件相关去同步/同步
    SLOW_CORTICAL = "slow_cortical"    # 慢皮层电位
    SENSORIMOTOR = "sensorimotor"      # 感觉运动节律


class BCICommand(Enum):
    """BCI命令类型"""
    CURSOR_MOVE = "cursor_move"        # 光标移动
    CLICK = "click"                    # 点击
    SCROLL = "scroll"                  # 滚动
    TYPE_TEXT = "type_text"           # 文字输入
    NAVIGATE = "navigate"              # 导航
    SELECT = "select"                  # 选择
    CONFIRM = "confirm"                # 确认
    CANCEL = "cancel"                  # 取消


class NeurofeedbackType(Enum):
    """神经反馈类型"""
    ATTENTION_TRAINING = "attention"    # 注意力训练
    RELAXATION = "relaxation"          # 放松训练
    COGNITIVE_LOAD = "cognitive_load"  # 认知负荷调节
    EMOTION_REGULATION = "emotion"     # 情绪调节
    MEMORY_ENHANCEMENT = "memory"      # 记忆增强
    MOTOR_REHABILITATION = "motor"     # 运动康复


class BCIState(Enum):
    """BCI状态"""
    DISCONNECTED = "disconnected"      # 未连接
    CONNECTING = "connecting"          # 连接中
    CALIBRATING = "calibrating"        # 校准中
    READY = "ready"                    # 就绪
    ACTIVE = "active"                  # 活跃
    TRAINING = "training"              # 训练中
    ERROR = "error"                    # 错误状态


class IBCIService(ABC):
    """
    脑机接口服务接口
    为重度运动障碍用户提供思维控制和神经反馈功能
    """
    
    @abstractmethod
    async def initialize(self):
        """
        初始化BCI服务
        """
        pass
    
    @abstractmethod
    async def detect_bci_devices(self) -> Dict[str, Any]:
        """
        检测可用的BCI设备
        
        Returns:
            设备检测结果
        """
        pass
    
    @abstractmethod
    async def connect_device(self, 
                           device_id: str,
                           device_type: BCIDeviceType,
                           connection_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        连接BCI设备
        
        Args:
            device_id: 设备ID
            device_type: 设备类型
            connection_config: 连接配置
            
        Returns:
            连接结果
        """
        pass
    
    @abstractmethod
    async def disconnect_device(self, device_id: str) -> Dict[str, Any]:
        """
        断开BCI设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            断开结果
        """
        pass
    
    @abstractmethod
    async def calibrate_user(self, 
                           user_id: str,
                           device_id: str,
                           calibration_type: str,
                           calibration_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        用户校准
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            calibration_type: 校准类型
            calibration_config: 校准配置
            
        Returns:
            校准结果
        """
        pass
    
    @abstractmethod
    async def start_signal_acquisition(self, 
                                     user_id: str,
                                     device_id: str,
                                     acquisition_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        开始信号采集
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            acquisition_config: 采集配置
            
        Returns:
            采集开始结果
        """
        pass
    
    @abstractmethod
    async def stop_signal_acquisition(self, 
                                    user_id: str,
                                    device_id: str) -> Dict[str, Any]:
        """
        停止信号采集
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            停止结果
        """
        pass
    
    @abstractmethod
    async def process_brain_signals(self, 
                                  user_id: str,
                                  device_id: str,
                                  signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理脑信号
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            signal_data: 信号数据
            
        Returns:
            处理结果
        """
        pass
    
    @abstractmethod
    async def recognize_intention(self, 
                                user_id: str,
                                processed_signals: Dict[str, Any],
                                recognition_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        识别用户意图
        
        Args:
            user_id: 用户ID
            processed_signals: 处理后的信号
            recognition_config: 识别配置
            
        Returns:
            意图识别结果
        """
        pass
    
    @abstractmethod
    async def execute_bci_command(self, 
                                user_id: str,
                                command: BCICommand,
                                command_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        执行BCI命令
        
        Args:
            user_id: 用户ID
            command: BCI命令
            command_params: 命令参数
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    async def start_neurofeedback_session(self, 
                                        user_id: str,
                                        device_id: str,
                                        feedback_type: NeurofeedbackType,
                                        session_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        开始神经反馈会话
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            feedback_type: 反馈类型
            session_config: 会话配置
            
        Returns:
            会话开始结果
        """
        pass
    
    @abstractmethod
    async def update_neurofeedback(self, 
                                 user_id: str,
                                 session_id: str,
                                 brain_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新神经反馈
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            brain_state: 脑状态数据
            
        Returns:
            反馈更新结果
        """
        pass
    
    @abstractmethod
    async def end_neurofeedback_session(self, 
                                      user_id: str,
                                      session_id: str) -> Dict[str, Any]:
        """
        结束神经反馈会话
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            
        Returns:
            会话结束结果
        """
        pass
    
    @abstractmethod
    async def monitor_brain_state(self, 
                                user_id: str,
                                device_id: str,
                                monitoring_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        监控脑状态
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            monitoring_config: 监控配置
            
        Returns:
            脑状态监控结果
        """
        pass
    
    @abstractmethod
    async def train_bci_classifier(self, 
                                 user_id: str,
                                 training_data: Dict[str, Any],
                                 training_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        训练BCI分类器
        
        Args:
            user_id: 用户ID
            training_data: 训练数据
            training_config: 训练配置
            
        Returns:
            训练结果
        """
        pass
    
    @abstractmethod
    async def update_user_model(self, 
                              user_id: str,
                              model_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新用户模型
        
        Args:
            user_id: 用户ID
            model_updates: 模型更新
            
        Returns:
            更新结果
        """
        pass
    
    @abstractmethod
    async def get_signal_quality(self, 
                               user_id: str,
                               device_id: str) -> Dict[str, Any]:
        """
        获取信号质量
        
        Args:
            user_id: 用户ID
            device_id: 设备ID
            
        Returns:
            信号质量信息
        """
        pass
    
    @abstractmethod
    async def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备状态
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备状态信息
        """
        pass
    
    @abstractmethod
    async def get_user_performance(self, 
                                 user_id: str,
                                 time_range: Dict[str, str] = None) -> Dict[str, Any]:
        """
        获取用户表现数据
        
        Args:
            user_id: 用户ID
            time_range: 时间范围
            
        Returns:
            用户表现数据
        """
        pass
    
    @abstractmethod
    async def export_session_data(self, 
                                user_id: str,
                                session_id: str,
                                export_format: str = "json") -> Dict[str, Any]:
        """
        导出会话数据
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            export_format: 导出格式
            
        Returns:
            导出结果
        """
        pass
    
    @abstractmethod
    async def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态
        
        Returns:
            服务状态信息
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """
        清理服务资源
        """
        pass 