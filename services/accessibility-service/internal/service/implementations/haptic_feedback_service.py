#!/usr/bin/env python

"""
振动反馈服务实现
为听力障碍用户提供触觉反馈，将声音信号转换为振动模式
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

from pkg.utils.dependency_manager import get_module, is_available

from ..interfaces.haptic_feedback_interface import (
    HapticDeviceType,
    HapticIntensity,
    HapticLocation,
    HapticModality,
    HapticPattern,
    IHapticFeedbackService,
)

logger = logging.getLogger(__name__)

# 可选依赖
numpy = get_module("numpy")
scipy = get_module("scipy")


@dataclass
class VibrationPattern:
    """振动模式"""

    name: str
    duration_ms: int
    intensity: float  # 0.0-1.0
    frequency: float  # Hz
    pulse_pattern: list[tuple[int, int]]  # [(on_ms, off_ms), ...]
    description: str


@dataclass
class HapticEvent:
    """触觉事件"""

    event_id: str
    timestamp: float
    device_type: HapticDeviceType
    modality: HapticModality
    pattern: HapticPattern
    location: HapticLocation
    intensity: HapticIntensity
    duration_ms: int
    metadata: dict[str, Any]


class AudioToHapticConverter:
    """音频到触觉转换器"""

    def __init__(self):
        self.frequency_bands = {
            "bass": (20, 250),  # 低频 -> 强烈振动
            "mid_low": (250, 500),  # 中低频 -> 中等振动
            "mid": (500, 2000),  # 中频 -> 轻微振动
            "mid_high": (2000, 4000),  # 中高频 -> 快速脉冲
            "high": (4000, 20000),  # 高频 -> 细微振动
        }

        self.pattern_mapping = {
            "bass": VibrationPattern(
                name="bass_rumble",
                duration_ms=500,
                intensity=0.8,
                frequency=30,
                pulse_pattern=[(200, 50), (200, 50)],
                description="低频隆隆声",
            ),
            "mid_low": VibrationPattern(
                name="mid_pulse",
                duration_ms=300,
                intensity=0.6,
                frequency=50,
                pulse_pattern=[(100, 30), (100, 30), (100, 30)],
                description="中低频脉冲",
            ),
            "mid": VibrationPattern(
                name="gentle_tap",
                duration_ms=200,
                intensity=0.4,
                frequency=70,
                pulse_pattern=[(50, 20), (50, 20), (50, 20), (50, 20)],
                description="轻柔敲击",
            ),
            "mid_high": VibrationPattern(
                name="rapid_buzz",
                duration_ms=150,
                intensity=0.5,
                frequency=100,
                pulse_pattern=[(25, 10)] * 6,
                description="快速嗡鸣",
            ),
            "high": VibrationPattern(
                name="fine_tingle",
                duration_ms=100,
                intensity=0.3,
                frequency=150,
                pulse_pattern=[(10, 5)] * 10,
                description="细微刺痛",
            ),
        }

    async def convert_audio_to_haptic(
        self, audio_data: bytes, sample_rate: int = 44100
    ) -> list[VibrationPattern]:
        """将音频数据转换为触觉模式"""
        if not is_available("numpy") or not is_available("scipy"):
            # 简化版本：基于音频长度和基本特征
            return await self._simple_audio_conversion(audio_data)

        try:
            # 解析音频数据
            audio_array = numpy.frombuffer(audio_data, dtype=numpy.int16)

            # 计算频谱
            fft = numpy.fft.fft(audio_array)
            freqs = numpy.fft.fftfreq(len(fft), 1 / sample_rate)
            magnitude = numpy.abs(fft)

            # 分析各频段能量
            patterns = []
            for band_name, (low_freq, high_freq) in self.frequency_bands.items():
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_energy = numpy.sum(magnitude[band_mask])

                # 如果该频段有足够能量，添加对应的振动模式
                if band_energy > numpy.mean(magnitude) * 0.5:
                    pattern = self.pattern_mapping[band_name]
                    # 根据能量调整强度
                    energy_ratio = min(band_energy / numpy.max(magnitude), 1.0)
                    adjusted_pattern = VibrationPattern(
                        name=pattern.name,
                        duration_ms=int(pattern.duration_ms * energy_ratio),
                        intensity=pattern.intensity * energy_ratio,
                        frequency=pattern.frequency,
                        pulse_pattern=pattern.pulse_pattern,
                        description=pattern.description,
                    )
                    patterns.append(adjusted_pattern)

            return patterns

        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            return await self._simple_audio_conversion(audio_data)

    async def _simple_audio_conversion(
        self, audio_data: bytes
    ) -> list[VibrationPattern]:
        """简化的音频转换（无需科学计算库）"""
        # 基于音频数据长度和简单统计
        data_length = len(audio_data)

        if data_length < 1000:
            # 短音频 -> 快速脉冲
            return [self.pattern_mapping["high"]]
        elif data_length < 5000:
            # 中等音频 -> 中频振动
            return [self.pattern_mapping["mid"]]
        else:
            # 长音频 -> 低频隆隆
            return [self.pattern_mapping["bass"]]


class HapticDeviceManager:
    """触觉设备管理器"""

    def __init__(self):
        self.connected_devices: dict[str, dict[str, Any]] = {}
        self.device_capabilities: dict[HapticDeviceType, dict[str, Any]] = {
            HapticDeviceType.SMARTPHONE: {
                "max_intensity": 1.0,
                "frequency_range": (10, 200),
                "supported_patterns": ["pulse", "continuous", "custom"],
                "locations": [HapticLocation.PALM],
            },
            HapticDeviceType.SMARTWATCH: {
                "max_intensity": 0.8,
                "frequency_range": (20, 150),
                "supported_patterns": ["pulse", "tap"],
                "locations": [HapticLocation.WRIST],
            },
            HapticDeviceType.HAPTIC_VEST: {
                "max_intensity": 1.0,
                "frequency_range": (5, 300),
                "supported_patterns": ["pulse", "continuous", "wave", "custom"],
                "locations": [
                    HapticLocation.CHEST,
                    HapticLocation.BACK,
                    HapticLocation.SHOULDER,
                ],
            },
            HapticDeviceType.HAPTIC_GLOVES: {
                "max_intensity": 0.9,
                "frequency_range": (10, 250),
                "supported_patterns": ["pulse", "pressure", "texture"],
                "locations": [HapticLocation.PALM, HapticLocation.FINGERS],
            },
            HapticDeviceType.TACTILE_DISPLAY: {
                "max_intensity": 0.7,
                "frequency_range": (50, 500),
                "supported_patterns": ["dot_matrix", "braille", "texture"],
                "locations": [HapticLocation.FINGERTIP],
            },
        }

    async def discover_devices(self) -> list[dict[str, Any]]:
        """发现可用的触觉设备"""
        discovered = []

        # 检查智能手机（通过Web API）
        if await self._check_smartphone_vibration():
            discovered.append(
                {
                    "device_id": "smartphone_primary",
                    "type": HapticDeviceType.SMARTPHONE,
                    "name": "智能手机振动",
                    "status": "connected",
                    "capabilities": self.device_capabilities[
                        HapticDeviceType.SMARTPHONE
                    ],
                }
            )

        # 检查其他设备（模拟）
        # 在实际实现中，这里会通过蓝牙、USB等协议发现设备

        return discovered

    async def _check_smartphone_vibration(self) -> bool:
        """检查智能手机振动功能"""
        try:
            # 在Web环境中，可以通过JavaScript API检查
            # 这里返回True表示假设有振动功能
            return True
        except Exception as e:
            return False

    async def connect_device(
        self, device_id: str, device_type: HapticDeviceType
    ) -> bool:
        """连接触觉设备"""
        try:
            # 模拟设备连接
            self.connected_devices[device_id] = {
                "type": device_type,
                "status": "connected",
                "last_ping": time.time(),
                "capabilities": self.device_capabilities[device_type],
            }
            logger.info(f"已连接触觉设备: {device_id} ({device_type.value})")
            return True
        except Exception as e:
            logger.error(f"连接设备失败 {device_id}: {e}")
            return False

    async def send_haptic_command(
        self,
        device_id: str,
        pattern: VibrationPattern,
        location: HapticLocation = HapticLocation.PALM,
    ) -> bool:
        """发送触觉命令到设备"""
        if device_id not in self.connected_devices:
            logger.error(f"设备未连接: {device_id}")
            return False

        device = self.connected_devices[device_id]
        device_type = device["type"]

        try:
            # 根据设备类型发送不同的命令
            if device_type == HapticDeviceType.SMARTPHONE:
                return await self._send_smartphone_vibration(pattern)
            elif device_type == HapticDeviceType.SMARTWATCH:
                return await self._send_smartwatch_haptic(pattern)
            elif device_type == HapticDeviceType.HAPTIC_VEST:
                return await self._send_vest_haptic(pattern, location)
            else:
                logger.warning(f"不支持的设备类型: {device_type}")
                return False

        except Exception as e:
            logger.error(f"发送触觉命令失败: {e}")
            return False

    async def _send_smartphone_vibration(self, pattern: VibrationPattern) -> bool:
        """发送智能手机振动命令"""
        # 在实际实现中，这里会调用平台特定的API
        # 例如：Android的Vibrator API或iOS的Core Haptics
        logger.info(f"发送手机振动: {pattern.name}, 强度: {pattern.intensity}")

        # 模拟振动执行
        for on_ms, off_ms in pattern.pulse_pattern:
            await asyncio.sleep(on_ms / 1000)  # 振动时间
            await asyncio.sleep(off_ms / 1000)  # 停止时间

        return True

    async def _send_smartwatch_haptic(self, pattern: VibrationPattern) -> bool:
        """发送智能手表触觉反馈"""
        logger.info(f"发送手表触觉: {pattern.name}")
        # 智能手表通常支持更精细的触觉反馈
        return True

    async def _send_vest_haptic(
        self, pattern: VibrationPattern, location: HapticLocation
    ) -> bool:
        """发送触觉背心反馈"""
        logger.info(f"发送背心触觉: {pattern.name} 位置: {location.value}")
        # 触觉背心可以在不同位置提供反馈
        return True


class HapticFeedbackService(IHapticFeedbackService):
    """触觉反馈服务实现"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = config.get("haptic_feedback", {}).get("enabled", True)

        # 核心组件
        self.audio_converter = AudioToHapticConverter()
        self.device_manager = HapticDeviceManager()

        # 状态管理
        self.active_patterns: dict[str, HapticEvent] = {}
        self.pattern_queue: list[HapticEvent] = []
        self.is_running = False

        # 预定义模式
        self.predefined_patterns = self._load_predefined_patterns()

        # 统计信息
        self.stats = {
            "patterns_sent": 0,
            "devices_connected": 0,
            "conversion_time_ms": 0,
            "last_activity": None,
        }

        logger.info(f"触觉反馈服务初始化完成 - 启用: {self.enabled}")

    def _load_predefined_patterns(self) -> dict[str, VibrationPattern]:
        """加载预定义的振动模式"""
        return {
            # 通知类型
            "notification_gentle": VibrationPattern(
                name="notification_gentle",
                duration_ms=200,
                intensity=0.3,
                frequency=50,
                pulse_pattern=[(100, 50), (100, 0)],
                description="轻柔通知",
            ),
            "notification_urgent": VibrationPattern(
                name="notification_urgent",
                duration_ms=500,
                intensity=0.8,
                frequency=100,
                pulse_pattern=[(100, 50)] * 5,
                description="紧急通知",
            ),
            # 导航类型
            "navigation_turn_left": VibrationPattern(
                name="navigation_turn_left",
                duration_ms=300,
                intensity=0.6,
                frequency=70,
                pulse_pattern=[(50, 20), (100, 20), (150, 0)],
                description="左转提示",
            ),
            "navigation_turn_right": VibrationPattern(
                name="navigation_turn_right",
                duration_ms=300,
                intensity=0.6,
                frequency=70,
                pulse_pattern=[(150, 20), (100, 20), (50, 0)],
                description="右转提示",
            ),
            # 警告类型
            "warning_obstacle": VibrationPattern(
                name="warning_obstacle",
                duration_ms=400,
                intensity=0.9,
                frequency=120,
                pulse_pattern=[(50, 25)] * 8,
                description="障碍物警告",
            ),
            "warning_danger": VibrationPattern(
                name="warning_danger",
                duration_ms=1000,
                intensity=1.0,
                frequency=150,
                pulse_pattern=[(100, 50)] * 10,
                description="危险警告",
            ),
            # 反馈类型
            "feedback_success": VibrationPattern(
                name="feedback_success",
                duration_ms=150,
                intensity=0.4,
                frequency=80,
                pulse_pattern=[(75, 25), (75, 0)],
                description="成功反馈",
            ),
            "feedback_error": VibrationPattern(
                name="feedback_error",
                duration_ms=300,
                intensity=0.7,
                frequency=60,
                pulse_pattern=[(100, 50), (100, 50), (100, 0)],
                description="错误反馈",
            ),
        }

    async def initialize(self) -> bool:
        """初始化服务"""
        if not self.enabled:
            logger.info("触觉反馈服务已禁用")
            return True

        try:
            # 发现并连接设备
            devices = await self.device_manager.discover_devices()
            for device in devices:
                await self.device_manager.connect_device(
                    device["device_id"], device["type"]
                )

            self.stats["devices_connected"] = len(devices)
            self.is_running = True

            logger.info(f"触觉反馈服务初始化成功，连接了 {len(devices)} 个设备")
            return True

        except Exception as e:
            logger.error(f"触觉反馈服务初始化失败: {e}")
            return False

    async def send_haptic_feedback(
        self,
        device_id: str,
        pattern: HapticPattern,
        location: HapticLocation = HapticLocation.PALM,
        intensity: HapticIntensity = HapticIntensity.MEDIUM,
    ) -> bool:
        """发送触觉反馈"""
        if not self.enabled or not self.is_running:
            return False

        try:
            # 创建触觉事件
            event = HapticEvent(
                event_id=f"haptic_{int(time.time() * 1000)}",
                timestamp=time.time(),
                device_type=HapticDeviceType.SMARTPHONE,  # 默认
                modality=HapticModality.VIBRATION,
                pattern=pattern,
                location=location,
                intensity=intensity,
                duration_ms=pattern.duration_ms,
                metadata={},
            )

            # 发送到设备
            success = await self.device_manager.send_haptic_command(
                device_id, pattern, location
            )

            if success:
                self.active_patterns[event.event_id] = event
                self.stats["patterns_sent"] += 1
                self.stats["last_activity"] = time.time()

                # 设置清理定时器
                asyncio.create_task(
                    self._cleanup_pattern(event.event_id, pattern.duration_ms)
                )

            return success

        except Exception as e:
            logger.error(f"发送触觉反馈失败: {e}")
            return False

    async def send_predefined_pattern(
        self,
        pattern_name: str,
        device_id: str,
        location: HapticLocation = HapticLocation.PALM,
    ) -> bool:
        """发送预定义模式"""
        if pattern_name not in self.predefined_patterns:
            logger.error(f"未知的预定义模式: {pattern_name}")
            return False

        pattern = self.predefined_patterns[pattern_name]
        return await self.send_haptic_feedback(device_id, pattern, location)

    async def convert_audio_to_haptic(
        self, audio_data: bytes, device_id: str, sample_rate: int = 44100
    ) -> bool:
        """将音频转换为触觉反馈"""
        start_time = time.time()

        try:
            # 转换音频为触觉模式
            patterns = await self.audio_converter.convert_audio_to_haptic(
                audio_data, sample_rate
            )

            # 发送所有模式
            success_count = 0
            for pattern in patterns:
                if await self.send_haptic_feedback(device_id, pattern):
                    success_count += 1
                # 添加小延迟避免重叠
                await asyncio.sleep(0.1)

            # 更新统计
            conversion_time = (time.time() - start_time) * 1000
            self.stats["conversion_time_ms"] = conversion_time

            logger.info(f"音频转触觉完成: {success_count}/{len(patterns)} 个模式成功")
            return success_count > 0

        except Exception as e:
            logger.error(f"音频转触觉失败: {e}")
            return False

    async def create_custom_pattern(
        self,
        name: str,
        duration_ms: int,
        intensity: float,
        frequency: float,
        pulse_pattern: list[tuple[int, int]],
    ) -> bool:
        """创建自定义触觉模式"""
        try:
            pattern = VibrationPattern(
                name=name,
                duration_ms=duration_ms,
                intensity=max(0.0, min(1.0, intensity)),  # 限制范围
                frequency=frequency,
                pulse_pattern=pulse_pattern,
                description=f"自定义模式: {name}",
            )

            self.predefined_patterns[name] = pattern
            logger.info(f"创建自定义触觉模式: {name}")
            return True

        except Exception as e:
            logger.error(f"创建自定义模式失败: {e}")
            return False

    async def get_device_capabilities(self, device_id: str) -> dict[str, Any] | None:
        """获取设备能力"""
        if device_id in self.device_manager.connected_devices:
            return self.device_manager.connected_devices[device_id]["capabilities"]
        return None

    async def list_connected_devices(self) -> list[dict[str, Any]]:
        """列出已连接的设备"""
        devices = []
        for device_id, device_info in self.device_manager.connected_devices.items():
            devices.append(
                {
                    "device_id": device_id,
                    "type": device_info["type"].value,
                    "status": device_info["status"],
                    "capabilities": device_info["capabilities"],
                }
            )
        return devices

    async def stop_all_patterns(self) -> bool:
        """停止所有触觉模式"""
        try:
            self.active_patterns.clear()
            self.pattern_queue.clear()
            logger.info("已停止所有触觉模式")
            return True
        except Exception as e:
            logger.error(f"停止触觉模式失败: {e}")
            return False

    async def get_service_stats(self) -> dict[str, Any]:
        """获取服务统计信息"""
        return {
            **self.stats,
            "active_patterns": len(self.active_patterns),
            "queued_patterns": len(self.pattern_queue),
            "predefined_patterns": len(self.predefined_patterns),
            "connected_devices": len(self.device_manager.connected_devices),
            "service_status": "running" if self.is_running else "stopped",
        }

    async def _cleanup_pattern(self, event_id: str, delay_ms: int):
        """清理已完成的模式"""
        await asyncio.sleep(delay_ms / 1000)
        if event_id in self.active_patterns:
            del self.active_patterns[event_id]

    async def shutdown(self):
        """关闭服务"""
        self.is_running = False
        await self.stop_all_patterns()
        self.device_manager.connected_devices.clear()
        logger.info("触觉反馈服务已关闭")
