#!/usr/bin/env python

"""
高级触觉反馈系统接口定义
为用户提供多模态触觉交互和高级触觉体验的标准接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class HapticDeviceType(Enum):
    """触觉设备类型"""

    HAPTIC_GLOVES = "haptic_gloves"  # 触觉手套
    HAPTIC_VEST = "haptic_vest"  # 触觉背心
    HAPTIC_HEADBAND = "haptic_headband"  # 触觉头带
    HAPTIC_CHAIR = "haptic_chair"  # 触觉椅子
    HAPTIC_CONTROLLER = "haptic_controller"  # 触觉控制器
    ULTRASOUND_HAPTIC = "ultrasound"  # 超声波触觉
    ELECTROTACTILE = "electrotactile"  # 电触觉
    PNEUMATIC = "pneumatic"  # 气动触觉


class HapticModality(Enum):
    """触觉模态"""

    VIBRATION = "vibration"  # 振动
    PRESSURE = "pressure"  # 压力
    TEMPERATURE = "temperature"  # 温度
    TEXTURE = "texture"  # 纹理
    FORCE = "force"  # 力反馈
    ELECTRICAL = "electrical"  # 电刺激
    ULTRASONIC = "ultrasonic"  # 超声波
    MAGNETIC = "magnetic"  # 磁场


class HapticPattern(Enum):
    """触觉模式"""

    PULSE = "pulse"  # 脉冲
    CONTINUOUS = "continuous"  # 连续
    RHYTHMIC = "rhythmic"  # 节律性
    WAVE = "wave"  # 波形
    BURST = "burst"  # 突发
    GRADIENT = "gradient"  # 渐变
    RANDOM = "random"  # 随机
    CUSTOM = "custom"  # 自定义


class HapticIntensity(Enum):
    """触觉强度级别"""

    VERY_LOW = "very_low"  # 极低
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中等
    HIGH = "high"  # 高
    VERY_HIGH = "very_high"  # 极高
    ADAPTIVE = "adaptive"  # 自适应


class HapticLocation(Enum):
    """触觉位置"""

    FINGERTIP = "fingertip"  # 指尖
    PALM = "palm"  # 手掌
    WRIST = "wrist"  # 手腕
    FOREARM = "forearm"  # 前臂
    UPPER_ARM = "upper_arm"  # 上臂
    SHOULDER = "shoulder"  # 肩膀
    BACK = "back"  # 背部
    CHEST = "chest"  # 胸部
    HEAD = "head"  # 头部
    NECK = "neck"  # 颈部


class IHapticFeedbackService(ABC):
    """
    高级触觉反馈系统接口
    为用户提供多模态触觉交互和高级触觉体验
    """

    @abstractmethod
    async def initialize(self):
        """
        初始化触觉反馈服务
        """
        pass

    @abstractmethod
    async def detect_haptic_devices(self) -> dict[str, Any]:
        """
        检测可用的触觉设备

        Returns:
            设备检测结果
        """
        pass

    @abstractmethod
    async def connect_haptic_device(
        self,
        device_id: str,
        device_type: HapticDeviceType,
        connection_config: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        连接触觉设备

        Args:
            device_id: 设备ID
            device_type: 设备类型
            connection_config: 连接配置

        Returns:
            连接结果
        """
        pass

    @abstractmethod
    async def calibrate_haptic_device(
        self, user_id: str, device_id: str, calibration_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        校准触觉设备

        Args:
            user_id: 用户ID
            device_id: 设备ID
            calibration_config: 校准配置

        Returns:
            校准结果
        """
        pass

    @abstractmethod
    async def create_haptic_pattern(
        self, pattern_name: str, pattern_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建触觉模式

        Args:
            pattern_name: 模式名称
            pattern_config: 模式配置

        Returns:
            创建结果
        """
        pass

    @abstractmethod
    async def play_haptic_pattern(
        self,
        user_id: str,
        device_id: str,
        pattern_name: str,
        play_config: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        播放触觉模式

        Args:
            user_id: 用户ID
            device_id: 设备ID
            pattern_name: 模式名称
            play_config: 播放配置

        Returns:
            播放结果
        """
        pass

    @abstractmethod
    async def send_haptic_signal(
        self, user_id: str, device_id: str, signal_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        发送触觉信号

        Args:
            user_id: 用户ID
            device_id: 设备ID
            signal_config: 信号配置

        Returns:
            发送结果
        """
        pass

    @abstractmethod
    async def create_spatial_haptic_map(
        self, user_id: str, device_id: str, spatial_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建空间触觉映射

        Args:
            user_id: 用户ID
            device_id: 设备ID
            spatial_config: 空间配置

        Returns:
            映射创建结果
        """
        pass

    @abstractmethod
    async def render_spatial_haptics(
        self, user_id: str, device_id: str, spatial_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        渲染空间触觉

        Args:
            user_id: 用户ID
            device_id: 设备ID
            spatial_data: 空间数据

        Returns:
            渲染结果
        """
        pass

    @abstractmethod
    async def create_haptic_texture(
        self, texture_name: str, texture_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建触觉纹理

        Args:
            texture_name: 纹理名称
            texture_config: 纹理配置

        Returns:
            创建结果
        """
        pass

    @abstractmethod
    async def simulate_texture_interaction(
        self,
        user_id: str,
        device_id: str,
        texture_name: str,
        interaction_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        模拟纹理交互

        Args:
            user_id: 用户ID
            device_id: 设备ID
            texture_name: 纹理名称
            interaction_data: 交互数据

        Returns:
            模拟结果
        """
        pass

    @abstractmethod
    async def create_haptic_language(
        self, language_name: str, language_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建触觉语言

        Args:
            language_name: 语言名称
            language_config: 语言配置

        Returns:
            创建结果
        """
        pass

    @abstractmethod
    async def encode_message_to_haptic(
        self,
        user_id: str,
        message: str,
        language_name: str,
        encoding_config: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        将消息编码为触觉信号

        Args:
            user_id: 用户ID
            message: 消息内容
            language_name: 触觉语言名称
            encoding_config: 编码配置

        Returns:
            编码结果
        """
        pass

    @abstractmethod
    async def decode_haptic_to_message(
        self, user_id: str, haptic_data: dict[str, Any], language_name: str
    ) -> dict[str, Any]:
        """
        将触觉信号解码为消息

        Args:
            user_id: 用户ID
            haptic_data: 触觉数据
            language_name: 触觉语言名称

        Returns:
            解码结果
        """
        pass

    @abstractmethod
    async def train_haptic_recognition(
        self,
        user_id: str,
        training_data: dict[str, Any],
        training_config: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        训练触觉识别

        Args:
            user_id: 用户ID
            training_data: 训练数据
            training_config: 训练配置

        Returns:
            训练结果
        """
        pass

    @abstractmethod
    async def adapt_haptic_intensity(
        self, user_id: str, device_id: str, adaptation_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        自适应触觉强度

        Args:
            user_id: 用户ID
            device_id: 设备ID
            adaptation_data: 适应数据

        Returns:
            适应结果
        """
        pass

    @abstractmethod
    async def monitor_haptic_response(
        self, user_id: str, device_id: str, monitoring_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        监控触觉响应

        Args:
            user_id: 用户ID
            device_id: 设备ID
            monitoring_config: 监控配置

        Returns:
            监控结果
        """
        pass

    @abstractmethod
    async def create_haptic_notification(
        self, user_id: str, notification_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建触觉通知

        Args:
            user_id: 用户ID
            notification_config: 通知配置

        Returns:
            创建结果
        """
        pass

    @abstractmethod
    async def send_haptic_notification(
        self, user_id: str, notification_id: str, urgency_level: str = "normal"
    ) -> dict[str, Any]:
        """
        发送触觉通知

        Args:
            user_id: 用户ID
            notification_id: 通知ID
            urgency_level: 紧急程度

        Returns:
            发送结果
        """
        pass

    @abstractmethod
    async def create_haptic_navigation(
        self, user_id: str, navigation_config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        创建触觉导航

        Args:
            user_id: 用户ID
            navigation_config: 导航配置

        Returns:
            创建结果
        """
        pass

    @abstractmethod
    async def provide_haptic_guidance(
        self, user_id: str, device_id: str, guidance_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        提供触觉引导

        Args:
            user_id: 用户ID
            device_id: 设备ID
            guidance_data: 引导数据

        Returns:
            引导结果
        """
        pass

    @abstractmethod
    async def get_haptic_preferences(self, user_id: str) -> dict[str, Any]:
        """
        获取用户触觉偏好

        Args:
            user_id: 用户ID

        Returns:
            触觉偏好设置
        """
        pass

    @abstractmethod
    async def update_haptic_preferences(
        self, user_id: str, preferences: dict[str, Any]
    ) -> dict[str, Any]:
        """
        更新用户触觉偏好

        Args:
            user_id: 用户ID
            preferences: 偏好设置

        Returns:
            更新结果
        """
        pass

    @abstractmethod
    async def get_device_capabilities(self, device_id: str) -> dict[str, Any]:
        """
        获取设备能力

        Args:
            device_id: 设备ID

        Returns:
            设备能力信息
        """
        pass

    @abstractmethod
    async def test_haptic_functionality(
        self, user_id: str, device_id: str, test_config: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        测试触觉功能

        Args:
            user_id: 用户ID
            device_id: 设备ID
            test_config: 测试配置

        Returns:
            测试结果
        """
        pass

    @abstractmethod
    async def get_haptic_analytics(
        self, user_id: str, time_range: dict[str, str] = None
    ) -> dict[str, Any]:
        """
        获取触觉分析数据

        Args:
            user_id: 用户ID
            time_range: 时间范围

        Returns:
            分析数据
        """
        pass

    @abstractmethod
    async def export_haptic_profile(
        self, user_id: str, export_format: str = "json"
    ) -> dict[str, Any]:
        """
        导出触觉配置文件

        Args:
            user_id: 用户ID
            export_format: 导出格式

        Returns:
            导出结果
        """
        pass

    @abstractmethod
    async def get_service_status(self) -> dict[str, Any]:
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
