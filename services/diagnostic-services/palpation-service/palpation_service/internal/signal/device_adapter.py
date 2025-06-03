#!/usr/bin/env python3

"""
脉诊设备适配层 - 支持多种压力传感器设备和实时数据处理

本模块提供了对各种脉诊硬件设备的统一接口适配，包括传统脉诊仪、
可穿戴设备和移动端传感器等，实现设备无关的数据采集、预处理和
校准功能，确保数据质量和兼容性。
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any

from internal.model.pulse_models import (
    DeviceInfo,
    PulseDataPacket,
    PulsePosition,
    SensorCalibrationData,
)

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """脉诊设备类型枚举"""

    TRADITIONAL = auto()  # 传统脉诊仪
    WEARABLE = auto()  # 可穿戴设备
    MOBILE = auto()  # 移动设备
    PROTOTYPE = auto()  # 原型设备
    SIMULATOR = auto()  # 模拟器

class PressurePosition(Enum):
    """按压位置枚举"""

    CUNKUO = "寸口"  # 桡动脉寸口
    CUN = "寸"  # 寸
    GUAN = "关"  # 关
    CHI = "尺"  # 尺
    LEFT_CUN = "左寸"
    LEFT_GUAN = "左关"
    LEFT_CHI = "左尺"
    RIGHT_CUN = "右寸"
    RIGHT_GUAN = "右关"
    RIGHT_CHI = "右尺"

@dataclass
class DeviceCapability:
    """设备能力描述"""

    max_sample_rate: int  # 最大采样率(Hz)
    resolution: int  # 分辨率(bit)
    channels: int  # 通道数
    pressure_levels: int  # 支持的压力等级数
    wireless: bool  # 是否支持无线连接
    battery_powered: bool  # 是否电池供电
    requires_calibration: bool  # 是否需要校准

@dataclass
class SignalMetadata:
    """信号元数据"""

    device_id: str
    device_type: DeviceType
    timestamp: float
    sample_rate: int
    duration: float
    position: PressurePosition
    user_id: str
    session_id: str
    pressure_level: int  # 1-轻按, 2-中按, 3-重按
    calibrated: bool
    custom_metadata: dict

class SignalProcessor:
    """信号处理器"""

    def __init__(self, config: dict = None):
        """
        初始化信号处理器

        Args:
            config: 配置字典
        """
        self.config = config or {}

        # 滤波器参数
        self.use_bandpass = self.config.get("use_bandpass", True)
        self.low_cutoff = self.config.get("low_cutoff", 0.5)  # Hz
        self.high_cutoff = self.config.get("high_cutoff", 40.0)  # Hz

        # 降噪设置
        self.denoise_method = self.config.get("denoise_method", "wavelet")
        self.snr_threshold = self.config.get("snr_threshold", 10.0)

        logger.info(f"信号处理器初始化完成，滤波范围: {self.low_cutoff}-{self.high_cutoff}Hz")

    def preprocess(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        预处理脉搏信号

        Args:
            signal: 脉搏信号数组
            sample_rate: 采样率

        Returns:
            处理后的信号
        """
        # 1. 去基线漂移
        signal = self._remove_baseline(signal, sample_rate)

        # 2. 带通滤波
        if self.use_bandpass:
            signal = self._apply_bandpass(signal, sample_rate)

        # 3. 降噪
        signal = self._denoise(signal, sample_rate)

        return signal

    def detect_pulse_features(self, signal: np.ndarray, sample_rate: int) -> dict:
        """
        检测脉搏特征

        Args:
            signal: 脉搏信号数组
            sample_rate: 采样率

        Returns:
            脉搏特征字典
        """
        # 检测脉搏波峰
        peaks = self._detect_peaks(signal, sample_rate)

        # 计算脉率
        if len(peaks) > 1:
            # 计算相邻峰值间距的平均值
            intervals = np.diff(peaks) / sample_rate  # 转换为秒
            pulse_rate = 60 / np.mean(intervals)  # 转换为每分钟脉搏数
        else:
            pulse_rate = 0

        # 计算其他特征
        features = {
            "pulse_rate": pulse_rate,
            "peak_count": len(peaks),
            "peak_indices": peaks.tolist(),
            "pulse_strength": np.max(signal) - np.min(signal),
            "regularity": self._calculate_regularity(peaks, sample_rate) if len(peaks) > 2 else 0,
        }

        # 如果有足够的峰值，计算脉搏波形特征
        if len(peaks) > 2:
            wave_features = self._extract_wave_features(signal, peaks, sample_rate)
            features.update(wave_features)

        return features

    def _remove_baseline(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """去除基线漂移"""
        # 简单实现，使用高通滤波器
        from scipy import signal as sp_signal

        # 设计高通滤波器，截止频率0.5Hz
        b, a = sp_signal.butter(4, 0.5 / (sample_rate / 2), "high")

        # 应用滤波器
        return sp_signal.filtfilt(b, a, signal)

    def _apply_bandpass(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """应用带通滤波"""
        from scipy import signal as sp_signal

        # 设计带通滤波器
        nyq = 0.5 * sample_rate
        low = self.low_cutoff / nyq
        high = self.high_cutoff / nyq
        b, a = sp_signal.butter(4, [low, high], btype="band")

        # 应用滤波器
        return sp_signal.filtfilt(b, a, signal)

    def _denoise(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """信号降噪"""
        if self.denoise_method == "wavelet":
            try:
                # 使用小波变换降噪
                # 注意: 真实实现应当引入PyWavelets，这里只是概念示例
                # import pywt
                # coeffs = pywt.wavedec(signal, 'db4', level=4)
                # coeffs[1:] = [pywt.threshold(c, np.std(c)*0.1, mode='soft') for c in coeffs[1:]]
                # return pywt.waverec(coeffs, 'db4')
                return signal  # 实际应用应替换为真实实现

            except Exception as e:
                logger.error(f"小波降噪失败: {e!s}")
                return signal
        else:
            # 简单的移动平均平滑
            window_size = int(sample_rate / 10)  # 约0.1秒窗口
            if window_size < 3:
                window_size = 3

            from scipy import signal as sp_signal

            return sp_signal.savgol_filter(signal, window_size, 2)

    def _detect_peaks(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """检测脉搏波峰"""
        from scipy import signal as sp_signal

        # 设置最小峰值间距为0.5秒
        min_distance = int(sample_rate * 0.4)

        # 设置峰值高度阈值
        height = 0.6 * np.max(signal) if len(signal) > 0 else 0

        # 检测峰值
        peaks, _ = sp_signal.find_peaks(signal, height=height, distance=min_distance)

        return peaks

    def _calculate_regularity(self, peaks: np.ndarray, sample_rate: int) -> float:
        """计算脉搏规律性"""
        if len(peaks) < 3:
            return 0.0

        # 计算峰值间隔
        intervals = np.diff(peaks) / sample_rate

        # 计算间隔的变异系数(CV)，CV越小表示越规律
        cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else float("inf")

        # 转换为0-1的规律性得分，CV越小，得分越高
        regularity = np.exp(-cv)

        return float(regularity)

    def _extract_wave_features(
        self, signal: np.ndarray, peaks: np.ndarray, sample_rate: int
    ) -> dict:
        """提取脉搏波形特征"""
        # 平均波形分析
        wave_features = {}

        try:
            # 提取完整周期
            cycles = []
            for i in range(len(peaks) - 1):
                start = peaks[i]
                end = peaks[i + 1]
                if end > start:
                    cycle = signal[start:end]
                    # 重采样到固定长度以便比较
                    from scipy import signal as sp_signal

                    cycle_resampled = sp_signal.resample(cycle, 100)
                    cycles.append(cycle_resampled)

            if not cycles:
                return {"wave_quality": 0}

            # 计算平均周期波形
            mean_cycle = np.mean(cycles, axis=0)

            # 计算重搏波特征
            dicrotic_notch_idx = self._find_dicrotic_notch(mean_cycle)
            if dicrotic_notch_idx > 0:
                # 有明显的重搏波
                primary_peak = np.max(mean_cycle[:dicrotic_notch_idx])
                dicrotic_peak = np.max(mean_cycle[dicrotic_notch_idx:])
                dicrotic_ratio = dicrotic_peak / primary_peak if primary_peak > 0 else 0

                wave_features["dicrotic_ratio"] = float(dicrotic_ratio)
                wave_features["has_dicrotic_wave"] = dicrotic_ratio > 0.1
            else:
                wave_features["has_dicrotic_wave"] = False

            # 计算上升/下降速率
            rise_time, fall_time = self._calculate_rise_fall_time(mean_cycle)
            wave_features["rise_time"] = float(rise_time)
            wave_features["fall_time"] = float(fall_time)
            wave_features["rise_fall_ratio"] = float(rise_time / fall_time) if fall_time > 0 else 0

            # 波形宽度
            width_50 = self._calculate_width(mean_cycle, 0.5)
            width_80 = self._calculate_width(mean_cycle, 0.8)
            wave_features["width_50"] = float(width_50)
            wave_features["width_80"] = float(width_80)

            # 波形质量估计(0-1)
            wave_features["wave_quality"] = min(1.0, len(cycles) / 10)

        except Exception as e:
            logger.error(f"波形特征提取失败: {e!s}")
            wave_features["wave_quality"] = 0

        return wave_features

    def _find_dicrotic_notch(self, cycle: np.ndarray) -> int:
        """寻找重搏波切迹位置"""
        # 简化实现：寻找主峰后的局部最小值
        main_peak = np.argmax(cycle)
        if main_peak >= len(cycle) - 10:
            return -1

        # 搜索主峰后的区域
        search_region = cycle[main_peak : main_peak + int(len(cycle) * 0.5)]
        if len(search_region) < 5:
            return -1

        # 使用简单的峰值检测
        from scipy import signal as sp_signal

        valleys, _ = sp_signal.find_peaks(-search_region)

        if len(valleys) > 0:
            return main_peak + valleys[0]
        return -1

    def _calculate_rise_fall_time(self, cycle: np.ndarray) -> tuple[float, float]:
        """计算上升和下降时间"""
        # 找到峰值位置
        peak_idx = np.argmax(cycle)

        # 计算10%到90%的上升时间
        threshold_low = 0.1 * cycle[peak_idx]
        threshold_high = 0.9 * cycle[peak_idx]

        rise_start = 0
        for i in range(peak_idx):
            if cycle[i] >= threshold_low:
                rise_start = i
                break

        rise_end = 0
        for i in range(rise_start, peak_idx):
            if cycle[i] >= threshold_high:
                rise_end = i
                break

        rise_time = (rise_end - rise_start) / 100  # 归一化到0-1范围

        # 计算90%到10%的下降时间
        fall_start = 0
        for i in range(peak_idx, len(cycle)):
            if cycle[i] <= threshold_high:
                fall_start = i
                break

        fall_end = len(cycle) - 1
        for i in range(fall_start, len(cycle)):
            if cycle[i] <= threshold_low:
                fall_end = i
                break

        fall_time = (fall_end - fall_start) / 100  # 归一化到0-1范围

        return max(0.01, rise_time), max(0.01, fall_time)

    def _calculate_width(self, cycle: np.ndarray, height_ratio: float) -> float:
        """计算指定高度比例处的波形宽度"""
        threshold = height_ratio * np.max(cycle)

        # 寻找左右交叉点
        left_idx = 0
        for i in range(len(cycle)):
            if cycle[i] >= threshold:
                left_idx = i
                break

        right_idx = len(cycle) - 1
        for i in range(len(cycle) - 1, 0, -1):
            if cycle[i] >= threshold:
                right_idx = i
                break

        width = (right_idx - left_idx) / 100  # 归一化到0-1范围
        return max(0.01, width)

class BaseDeviceAdapter(ABC):
    """设备适配器基类"""

    def __init__(self, device_config: dict[str, Any]):
        """
        初始化设备适配器

        Args:
            device_config: 设备配置
        """
        self.device_config = device_config
        self.device_id = device_config.get("device_id", "unknown")
        self.device_name = device_config.get("name", "Unknown Device")
        self.sampling_rate = device_config.get("sampling_rate", 1000)
        self.channels = device_config.get("channels", 6)
        self.is_connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def connect(self) -> bool:
        """连接设备"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """断开设备连接"""
        pass

    @abstractmethod
    def calibrate(self, operator: str) -> SensorCalibrationData:
        """校准设备"""
        pass

    @abstractmethod
    def start_acquisition(self, session_id: str) -> bool:
        """开始数据采集"""
        pass

    @abstractmethod
    def stop_acquisition(self) -> bool:
        """停止数据采集"""
        pass

    @abstractmethod
    def read_data(self) -> PulseDataPacket | None:
        """读取数据"""
        pass

    @abstractmethod
    def get_device_info(self) -> DeviceInfo:
        """获取设备信息"""
        pass

    @abstractmethod
    def check_health(self) -> tuple[bool, str]:
        """检查设备健康状态"""
        pass

    def map_channel_to_position(self, channel: int) -> PulsePosition:
        """
        将通道号映射到脉诊位置

        Args:
            channel: 通道号 (0-5)

        Returns:
            脉诊位置
        """
        channel_position_map = {
            0: PulsePosition.CUN_LEFT,
            1: PulsePosition.GUAN_LEFT,
            2: PulsePosition.CHI_LEFT,
            3: PulsePosition.CUN_RIGHT,
            4: PulsePosition.GUAN_RIGHT,
            5: PulsePosition.CHI_RIGHT,
        }
        return channel_position_map.get(channel, PulsePosition.CUN_LEFT)

class SuokeWP100Adapter(BaseDeviceAdapter):
    """索克WP-100设备适配器"""

    def __init__(self, device_config: dict[str, Any]):
        super().__init__(device_config)
        self.firmware_version = "1.2.0"
        self.current_session_id = None
        self.acquisition_active = False

    def connect(self) -> bool:
        """连接设备"""
        try:
            # TODO: 实际的设备连接代码
            # 这里是模拟实现
            self.logger.info(f"正在连接{self.device_name}...")

            # 模拟连接过程
            import time

            time.sleep(0.5)

            self.is_connected = True
            self.logger.info(f"{self.device_name}连接成功")
            return True

        except Exception as e:
            self.logger.error(f"连接{self.device_name}失败: {e}")
            self.is_connected = False
            return False

    def disconnect(self) -> bool:
        """断开设备连接"""
        try:
            if self.acquisition_active:
                self.stop_acquisition()

            # TODO: 实际的断开连接代码
            self.is_connected = False
            self.logger.info(f"{self.device_name}已断开连接")
            return True

        except Exception as e:
            self.logger.error(f"断开{self.device_name}连接失败: {e}")
            return False

    def calibrate(self, operator: str) -> SensorCalibrationData:
        """校准设备"""
        if not self.is_connected:
            raise Exception("设备未连接")

        self.logger.info(f"开始校准{self.device_name}...")

        # TODO: 实际的校准代码
        # 这里是模拟实现
        calibration_values = []
        for i in range(self.channels):
            # 模拟每个通道的校准值
            baseline = np.random.normal(100, 2)  # 基线压力
            sensitivity = np.random.normal(1.0, 0.02)  # 灵敏度
            calibration_values.extend([baseline, sensitivity])

        calibration_data = SensorCalibrationData(
            calibration_values=calibration_values,
            calibration_timestamp=datetime.now(),
            calibration_operator=operator,
            calibration_result=True,
            error_margin=0.02,
        )

        self.logger.info(f"{self.device_name}校准完成")
        return calibration_data

    def start_acquisition(self, session_id: str) -> bool:
        """开始数据采集"""
        if not self.is_connected:
            raise Exception("设备未连接")

        if self.acquisition_active:
            self.logger.warning("数据采集已在进行中")
            return False

        try:
            # TODO: 实际的开始采集代码
            self.current_session_id = session_id
            self.acquisition_active = True
            self.logger.info(f"{self.device_name}开始数据采集，会话ID: {session_id}")
            return True

        except Exception as e:
            self.logger.error(f"开始数据采集失败: {e}")
            return False

    def stop_acquisition(self) -> bool:
        """停止数据采集"""
        if not self.acquisition_active:
            self.logger.warning("数据采集未在进行中")
            return False

        try:
            # TODO: 实际的停止采集代码
            self.acquisition_active = False
            self.logger.info(f"{self.device_name}停止数据采集")
            return True

        except Exception as e:
            self.logger.error(f"停止数据采集失败: {e}")
            return False

    def read_data(self) -> PulseDataPacket | None:
        """读取数据"""
        if not self.acquisition_active:
            return None

        try:
            # TODO: 实际的数据读取代码
            # 这里是模拟实现

            # 模拟6个通道的数据
            data_packets = []
            for channel in range(self.channels):
                # 生成模拟脉搏波形数据
                t = np.linspace(0, 1, self.sampling_rate)

                # 基础脉搏波形（简化的双峰模型）
                heart_rate = 72  # 次/分
                frequency = heart_rate / 60  # Hz

                # 主波
                main_wave = 50 * np.sin(2 * np.pi * frequency * t) + 100

                # 重搏波
                dicrotic_wave = 15 * np.sin(4 * np.pi * frequency * t - np.pi / 4)

                # 合成脉搏波
                pressure_data = main_wave + dicrotic_wave

                # 添加噪声
                noise = np.random.normal(0, 2, len(pressure_data))
                pressure_data += noise

                # 计算速度数据（压力的导数）
                velocity_data = np.gradient(pressure_data) * self.sampling_rate

                # 模拟皮肤温度和湿度
                skin_temperature = 36.5 + np.random.normal(0, 0.5)
                skin_moisture = 45 + np.random.normal(0, 10)

                # 创建数据包
                packet = PulseDataPacket(
                    session_id=self.current_session_id,
                    timestamp=datetime.now(),
                    position=self.map_channel_to_position(channel),
                    pressure_data=pressure_data,
                    velocity_data=velocity_data,
                    skin_temperature=skin_temperature,
                    skin_moisture=skin_moisture,
                    quality_indicators={"signal_strength": 0.95, "contact_quality": 0.92},
                )
                data_packets.append(packet)

            # 返回第一个通道的数据（实际应用中可能需要返回所有通道）
            return data_packets[0] if data_packets else None

        except Exception as e:
            self.logger.error(f"读取数据失败: {e}")
            return None

    def get_device_info(self) -> DeviceInfo:
        """获取设备信息"""
        return DeviceInfo(
            device_id=self.device_id,
            model="WP-100",
            firmware_version=self.firmware_version,
            sensor_types=["pressure", "temperature", "moisture"],
            sampling_rate=self.sampling_rate,
            channels=self.channels,
            features=self.device_config.get("features", []),
            calibration_date=datetime.now(),  # 应该从设备读取实际校准日期
        )

    def check_health(self) -> tuple[bool, str]:
        """检查设备健康状态"""
        if not self.is_connected:
            return False, "设备未连接"

        # TODO: 实际的健康检查代码
        # 检查各项指标
        checks = {
            "连接状态": self.is_connected,
            "传感器状态": True,  # 模拟
            "电池电量": True,  # 模拟
            "固件版本": True,  # 模拟
        }

        failed_checks = [k for k, v in checks.items() if not v]

        if failed_checks:
            return False, f"健康检查失败: {', '.join(failed_checks)}"

        return True, "设备运行正常"

class TCMPulseWaveProAdapter(BaseDeviceAdapter):
    """TCM Diagnostics PulseWave Pro设备适配器"""

    def __init__(self, device_config: dict[str, Any]):
        super().__init__(device_config)
        self.firmware_version = "2.1.0"
        self.current_session_id = None
        self.acquisition_active = False

    def connect(self) -> bool:
        """连接设备"""
        try:
            self.logger.info(f"正在连接{self.device_name}...")
            # TODO: 实际的设备连接代码
            import time

            time.sleep(0.5)
            self.is_connected = True
            self.logger.info(f"{self.device_name}连接成功")
            return True
        except Exception as e:
            self.logger.error(f"连接{self.device_name}失败: {e}")
            self.is_connected = False
            return False

    def disconnect(self) -> bool:
        """断开设备连接"""
        try:
            if self.acquisition_active:
                self.stop_acquisition()
            self.is_connected = False
            self.logger.info(f"{self.device_name}已断开连接")
            return True
        except Exception as e:
            self.logger.error(f"断开{self.device_name}连接失败: {e}")
            return False

    def calibrate(self, operator: str) -> SensorCalibrationData:
        """校准设备"""
        if not self.is_connected:
            raise Exception("设备未连接")

        self.logger.info(f"开始校准{self.device_name}...")

        # 模拟校准过程
        calibration_values = []
        for i in range(self.channels):
            baseline = np.random.normal(95, 3)
            sensitivity = np.random.normal(0.98, 0.03)
            calibration_values.extend([baseline, sensitivity])

        calibration_data = SensorCalibrationData(
            calibration_values=calibration_values,
            calibration_timestamp=datetime.now(),
            calibration_operator=operator,
            calibration_result=True,
            error_margin=0.03,
        )

        self.logger.info(f"{self.device_name}校准完成")
        return calibration_data

    def start_acquisition(self, session_id: str) -> bool:
        """开始数据采集"""
        if not self.is_connected:
            raise Exception("设备未连接")

        if self.acquisition_active:
            self.logger.warning("数据采集已在进行中")
            return False

        try:
            self.current_session_id = session_id
            self.acquisition_active = True
            self.logger.info(f"{self.device_name}开始数据采集，会话ID: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"开始数据采集失败: {e}")
            return False

    def stop_acquisition(self) -> bool:
        """停止数据采集"""
        if not self.acquisition_active:
            self.logger.warning("数据采集未在进行中")
            return False

        try:
            self.acquisition_active = False
            self.logger.info(f"{self.device_name}停止数据采集")
            return True
        except Exception as e:
            self.logger.error(f"停止数据采集失败: {e}")
            return False

    def read_data(self) -> PulseDataPacket | None:
        """读取数据"""
        if not self.acquisition_active:
            return None

        try:
            # 生成模拟数据（采样率较低）
            t = np.linspace(0, 1, self.sampling_rate)
            heart_rate = 75
            frequency = heart_rate / 60

            # PulseWave Pro的波形特征略有不同
            main_wave = 45 * np.sin(2 * np.pi * frequency * t) + 105
            dicrotic_wave = 12 * np.sin(4 * np.pi * frequency * t - np.pi / 3)
            pressure_data = main_wave + dicrotic_wave
            noise = np.random.normal(0, 1.5, len(pressure_data))
            pressure_data += noise

            velocity_data = np.gradient(pressure_data) * self.sampling_rate

            packet = PulseDataPacket(
                session_id=self.current_session_id,
                timestamp=datetime.now(),
                position=PulsePosition.CUN_LEFT,
                pressure_data=pressure_data,
                velocity_data=velocity_data,
                skin_temperature=36.2 + np.random.normal(0, 0.3),
                skin_moisture=50 + np.random.normal(0, 8),
                quality_indicators={"signal_strength": 0.93, "contact_quality": 0.90},
            )

            return packet

        except Exception as e:
            self.logger.error(f"读取数据失败: {e}")
            return None

    def get_device_info(self) -> DeviceInfo:
        """获取设备信息"""
        return DeviceInfo(
            device_id=self.device_id,
            model="PulseWave Pro",
            firmware_version=self.firmware_version,
            sensor_types=["pressure", "temperature", "moisture"],
            sampling_rate=self.sampling_rate,
            channels=self.channels,
            features=self.device_config.get("features", []),
            calibration_date=datetime.now(),
        )

    def check_health(self) -> tuple[bool, str]:
        """检查设备健康状态"""
        if not self.is_connected:
            return False, "设备未连接"

        # 模拟健康检查
        return True, "设备运行正常"

class MedSensePR2000Adapter(BaseDeviceAdapter):
    """MedSense PulseReader 2000设备适配器"""

    def __init__(self, device_config: dict[str, Any]):
        super().__init__(device_config)
        self.firmware_version = "3.0.1"
        self.current_session_id = None
        self.acquisition_active = False
        self.battery_level = 85  # 模拟电池电量

    def connect(self) -> bool:
        """连接设备（无线）"""
        try:
            self.logger.info(f"正在通过蓝牙连接{self.device_name}...")
            # TODO: 实际的蓝牙连接代码
            import time

            time.sleep(0.8)  # 无线连接需要更长时间
            self.is_connected = True
            self.logger.info(f"{self.device_name}无线连接成功")
            return True
        except Exception as e:
            self.logger.error(f"连接{self.device_name}失败: {e}")
            self.is_connected = False
            return False

    def disconnect(self) -> bool:
        """断开设备连接"""
        try:
            if self.acquisition_active:
                self.stop_acquisition()
            self.is_connected = False
            self.logger.info(f"{self.device_name}已断开连接")
            return True
        except Exception as e:
            self.logger.error(f"断开{self.device_name}连接失败: {e}")
            return False

    def calibrate(self, operator: str) -> SensorCalibrationData:
        """校准设备"""
        if not self.is_connected:
            raise Exception("设备未连接")

        self.logger.info(f"开始校准{self.device_name}...")

        # PulseReader 2000的校准过程
        calibration_values = []
        for i in range(self.channels):
            baseline = np.random.normal(98, 2.5)
            sensitivity = np.random.normal(0.95, 0.04)
            calibration_values.extend([baseline, sensitivity])

        calibration_data = SensorCalibrationData(
            calibration_values=calibration_values,
            calibration_timestamp=datetime.now(),
            calibration_operator=operator,
            calibration_result=True,
            error_margin=0.04,  # 精度稍低
        )

        self.logger.info(f"{self.device_name}校准完成")
        return calibration_data

    def start_acquisition(self, session_id: str) -> bool:
        """开始数据采集"""
        if not self.is_connected:
            raise Exception("设备未连接")

        # 检查电池电量
        if self.battery_level < 20:
            self.logger.warning(f"电池电量低: {self.battery_level}%")

        if self.acquisition_active:
            self.logger.warning("数据采集已在进行中")
            return False

        try:
            self.current_session_id = session_id
            self.acquisition_active = True
            self.logger.info(f"{self.device_name}开始数据采集，会话ID: {session_id}")
            return True
        except Exception as e:
            self.logger.error(f"开始数据采集失败: {e}")
            return False

    def stop_acquisition(self) -> bool:
        """停止数据采集"""
        if not self.acquisition_active:
            self.logger.warning("数据采集未在进行中")
            return False

        try:
            self.acquisition_active = False
            self.logger.info(f"{self.device_name}停止数据采集")
            return True
        except Exception as e:
            self.logger.error(f"停止数据采集失败: {e}")
            return False

    def read_data(self) -> PulseDataPacket | None:
        """读取数据"""
        if not self.acquisition_active:
            return None

        try:
            # 生成模拟数据（采样率最低）
            t = np.linspace(0, 1, self.sampling_rate)
            heart_rate = 70
            frequency = heart_rate / 60

            # PulseReader 2000的波形（便携式设备，精度稍低）
            main_wave = 40 * np.sin(2 * np.pi * frequency * t) + 100
            dicrotic_wave = 10 * np.sin(4 * np.pi * frequency * t - np.pi / 2)
            pressure_data = main_wave + dicrotic_wave
            noise = np.random.normal(0, 3, len(pressure_data))  # 噪声较大
            pressure_data += noise

            velocity_data = np.gradient(pressure_data) * self.sampling_rate

            # 模拟电池消耗
            self.battery_level -= 0.01

            packet = PulseDataPacket(
                session_id=self.current_session_id,
                timestamp=datetime.now(),
                position=PulsePosition.CUN_LEFT,
                pressure_data=pressure_data,
                velocity_data=velocity_data,
                skin_temperature=36.3 + np.random.normal(0, 0.4),
                skin_moisture=None,  # 该设备不支持湿度测量
                quality_indicators={
                    "signal_strength": 0.88,
                    "contact_quality": 0.85,
                    "battery_level": self.battery_level,
                },
            )

            return packet

        except Exception as e:
            self.logger.error(f"读取数据失败: {e}")
            return None

    def get_device_info(self) -> DeviceInfo:
        """获取设备信息"""
        return DeviceInfo(
            device_id=self.device_id,
            model="PulseReader 2000",
            firmware_version=self.firmware_version,
            sensor_types=["pressure", "temperature"],  # 不支持湿度
            sampling_rate=self.sampling_rate,
            channels=self.channels,
            features=self.device_config.get("features", []),
            calibration_date=datetime.now(),
        )

    def check_health(self) -> tuple[bool, str]:
        """检查设备健康状态"""
        if not self.is_connected:
            return False, "设备未连接"

        # 检查电池电量
        if self.battery_level < 10:
            return False, f"电池电量严重不足: {self.battery_level}%"
        elif self.battery_level < 20:
            return True, f"电池电量低: {self.battery_level}%"

        return True, f"设备运行正常，电池电量: {self.battery_level}%"

class DeviceAdapterFactory:
    """设备适配器工厂"""

    @staticmethod
    def create_adapter(device_config: dict[str, Any]) -> BaseDeviceAdapter:
        """
        根据设备配置创建适配器

        Args:
            device_config: 设备配置

        Returns:
            设备适配器实例
        """
        device_id = device_config.get("device_id", "")

        adapter_map = {
            "suoke_wp100": SuokeWP100Adapter,
            "tcm_pulsewave_pro": TCMPulseWaveProAdapter,
            "medsense_pr2000": MedSensePR2000Adapter,
        }

        adapter_class = adapter_map.get(device_id)
        if not adapter_class:
            raise ValueError(f"不支持的设备类型: {device_id}")

        return adapter_class(device_config)
