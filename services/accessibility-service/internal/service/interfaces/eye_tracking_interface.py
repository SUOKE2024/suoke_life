#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
眼动追踪服务接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class EyeGesture(Enum):
    """眼动手势"""
    BLINK = "blink"
    DOUBLE_BLINK = "double_blink"
    LONG_BLINK = "long_blink"
    WINK_LEFT = "wink_left"
    WINK_RIGHT = "wink_right"
    LOOK_UP = "look_up"
    LOOK_DOWN = "look_down"
    LOOK_LEFT = "look_left"
    LOOK_RIGHT = "look_right"
    FIXATION = "fixation"
    SACCADE = "saccade"


class EyeTrackingMode(Enum):
    """眼动追踪模式"""
    CALIBRATION = "calibration"
    NAVIGATION = "navigation"
    SELECTION = "selection"
    TYPING = "typing"
    GAMING = "gaming"
    READING = "reading"


class IEyeTrackingService(ABC):
    """眼动追踪服务接口"""
    
    @abstractmethod
    async def initialize(self):
        """初始化服务"""
        pass
    
    @abstractmethod
    async def start_eye_tracking(self, 
                               user_id: str,
                               mode: EyeTrackingMode = EyeTrackingMode.NAVIGATION,
                               settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        开始眼动追踪
        
        Args:
            user_id: 用户ID
            mode: 追踪模式
            settings: 追踪设置
            
        Returns:
            追踪会话信息
        """
        pass
    
    @abstractmethod
    async def calibrate_eye_tracking(self, 
                                   user_id: str,
                                   calibration_points: List[Tuple[float, float]],
                                   eye_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        眼动追踪校准
        
        Args:
            user_id: 用户ID
            calibration_points: 校准点坐标列表
            eye_data: 对应的眼动数据
            
        Returns:
            校准结果
        """
        pass
    
    @abstractmethod
    async def detect_eye_gesture(self, 
                               session_id: str,
                               eye_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测眼动手势
        
        Args:
            session_id: 追踪会话ID
            eye_data: 眼动数据
            
        Returns:
            手势检测结果
        """
        pass
    
    @abstractmethod
    async def stop_eye_tracking(self, session_id: str) -> Dict[str, Any]:
        """
        停止眼动追踪
        
        Args:
            session_id: 追踪会话ID
            
        Returns:
            停止结果
        """
        pass
    
    @abstractmethod
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """清理服务资源"""
        pass 