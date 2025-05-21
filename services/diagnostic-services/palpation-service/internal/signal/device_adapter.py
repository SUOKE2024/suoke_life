#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脉诊设备适配层 - 支持多种压力传感器设备和实时数据处理

本模块提供了对各种脉诊硬件设备的统一接口适配，包括传统脉诊仪、
可穿戴设备和移动端传感器等，实现设备无关的数据采集、预处理和
校准功能，确保数据质量和兼容性。
"""

import os
import time
import json
import logging
import asyncio
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
from enum import Enum, auto
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class DeviceType(Enum):
    """脉诊设备类型枚举"""
    TRADITIONAL = auto()  # 传统脉诊仪
    WEARABLE = auto()     # 可穿戴设备
    MOBILE = auto()       # 移动设备
    PROTOTYPE = auto()    # 原型设备
    SIMULATOR = auto()    # 模拟器

class PressurePosition(Enum):
    """按压位置枚举"""
    CUNKUO = "寸口"  # 桡动脉寸口
    CUN = "寸"       # 寸
    GUAN = "关"      # 关
    CHI = "尺"       # 尺
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
    resolution: int       # 分辨率(bit)
    channels: int         # 通道数
    pressure_levels: int  # 支持的压力等级数
    wireless: bool        # 是否支持无线连接
    battery_powered: bool # 是否电池供电
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
    custom_metadata: Dict

class SignalProcessor:
    """信号处理器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化信号处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 滤波器参数
        self.use_bandpass = self.config.get('use_bandpass', True)
        self.low_cutoff = self.config.get('low_cutoff', 0.5)  # Hz
        self.high_cutoff = self.config.get('high_cutoff', 40.0)  # Hz
        
        # 降噪设置
        self.denoise_method = self.config.get('denoise_method', 'wavelet')
        self.snr_threshold = self.config.get('snr_threshold', 10.0)
        
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
    
    def detect_pulse_features(
        self, 
        signal: np.ndarray, 
        sample_rate: int
    ) -> Dict:
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
            "regularity": self._calculate_regularity(peaks, sample_rate) if len(peaks) > 2 else 0
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
        b, a = sp_signal.butter(4, 0.5 / (sample_rate / 2), 'high')
        
        # 应用滤波器
        return sp_signal.filtfilt(b, a, signal)
    
    def _apply_bandpass(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """应用带通滤波"""
        from scipy import signal as sp_signal
        
        # 设计带通滤波器
        nyq = 0.5 * sample_rate
        low = self.low_cutoff / nyq
        high = self.high_cutoff / nyq
        b, a = sp_signal.butter(4, [low, high], btype='band')
        
        # 应用滤波器
        return sp_signal.filtfilt(b, a, signal)
    
    def _denoise(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """信号降噪"""
        if self.denoise_method == 'wavelet':
            try:
                # 使用小波变换降噪
                # 注意: 真实实现应当引入PyWavelets，这里只是概念示例
                # import pywt
                # coeffs = pywt.wavedec(signal, 'db4', level=4)
                # coeffs[1:] = [pywt.threshold(c, np.std(c)*0.1, mode='soft') for c in coeffs[1:]]
                # return pywt.waverec(coeffs, 'db4')
                return signal  # 实际应用应替换为真实实现
                
            except Exception as e:
                logger.error(f"小波降噪失败: {str(e)}")
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
        peaks, _ = sp_signal.find_peaks(
            signal, 
            height=height, 
            distance=min_distance
        )
        
        return peaks
    
    def _calculate_regularity(self, peaks: np.ndarray, sample_rate: int) -> float:
        """计算脉搏规律性"""
        if len(peaks) < 3:
            return 0.0
            
        # 计算峰值间隔
        intervals = np.diff(peaks) / sample_rate
        
        # 计算间隔的变异系数(CV)，CV越小表示越规律
        cv = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else float('inf')
        
        # 转换为0-1的规律性得分，CV越小，得分越高
        regularity = np.exp(-cv)
        
        return float(regularity)
    
    def _extract_wave_features(
        self, 
        signal: np.ndarray, 
        peaks: np.ndarray, 
        sample_rate: int
    ) -> Dict:
        """提取脉搏波形特征"""
        # 平均波形分析
        wave_features = {}
        
        try:
            # 提取完整周期
            cycles = []
            for i in range(len(peaks) - 1):
                start = peaks[i]
                end = peaks[i+1]
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
            logger.error(f"波形特征提取失败: {str(e)}")
            wave_features["wave_quality"] = 0
        
        return wave_features
    
    def _find_dicrotic_notch(self, cycle: np.ndarray) -> int:
        """寻找重搏波切迹位置"""
        # 简化实现：寻找主峰后的局部最小值
        main_peak = np.argmax(cycle)
        if main_peak >= len(cycle) - 10:
            return -1
            
        # 搜索主峰后的区域
        search_region = cycle[main_peak:main_peak + int(len(cycle) * 0.5)]
        if len(search_region) < 5:
            return -1
            
        # 使用简单的峰值检测
        from scipy import signal as sp_signal
        valleys, _ = sp_signal.find_peaks(-search_region)
        
        if len(valleys) > 0:
            return main_peak + valleys[0]
        return -1
    
    def _calculate_rise_fall_time(self, cycle: np.ndarray) -> Tuple[float, float]:
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

class DeviceAdapter:
    """
    设备适配器基类，提供通用的设备数据处理方法
    """
    
    def __init__(self, config):
        """
        初始化设备适配器
        
        Args:
            config: 设备配置字典
        """
        self.config = config
        self.supported_models = config.get('supported_models', [])
        self.model_adapters = self._init_model_adapters()
        logger.info(f"初始化设备适配器，支持{len(self.supported_models)}种设备型号")
    
    def _init_model_adapters(self) -> Dict[str, Any]:
        """
        初始化各型号设备的适配器
        
        Returns:
            Dict: 设备型号到适配器对象的映射
        """
        adapters = {}
        for model_info in self.supported_models:
            model = model_info.get('model')
            manufacturer = model_info.get('manufacturer')
            
            if model == "WP-100" and manufacturer == "SuokeHealth":
                adapters[model] = SuokeWP100Adapter(model_info)
            elif model == "PulseWave Pro" and manufacturer == "TCMDiagnostics":
                adapters[model] = TCMDiagnosticsPWAdapter(model_info)
            elif model == "PulseReader 2000" and manufacturer == "MedSense":
                adapters[model] = MedSensePR2000Adapter(model_info)
            else:
                logger.warning(f"未知设备型号: {model}, 制造商: {manufacturer}")
        
        return adapters
    
    def validate_device(self, device_info: Dict[str, Any]) -> bool:
        """
        验证设备信息是否受支持
        
        Args:
            device_info: 设备信息字典
            
        Returns:
            bool: 如果设备受支持则返回True，否则返回False
        """
        model = device_info.get('model')
        firmware_version = device_info.get('firmware_version')
        
        if model not in self.model_adapters:
            logger.warning(f"不支持的设备型号: {model}")
            return False
        
        # 检查固件版本是否符合要求
        for supported_model in self.supported_models:
            if supported_model.get('model') == model:
                min_firmware = supported_model.get('firmware_min_version')
                if min_firmware and not self._check_version(firmware_version, min_firmware):
                    logger.warning(f"设备固件版本过低: {firmware_version}, 最低要求: {min_firmware}")
                    return False
                break
        
        return True
    
    def _check_version(self, version: str, min_version: str) -> bool:
        """
        检查版本是否满足最低要求
        
        Args:
            version: 当前版本
            min_version: 最低要求版本
            
        Returns:
            bool: 如果当前版本高于或等于最低要求则返回True
        """
        try:
            current = [int(x) for x in version.split('.')]
            minimum = [int(x) for x in min_version.split('.')]
            
            for i in range(max(len(current), len(minimum))):
                c = current[i] if i < len(current) else 0
                m = minimum[i] if i < len(minimum) else 0
                
                if c > m:
                    return True
                elif c < m:
                    return False
            
            return True  # 版本相等
        except Exception as e:
            logger.error(f"版本比较错误: {e}")
            return False
    
    def get_adapter_for_device(self, device_info: Dict[str, Any]) -> Any:
        """
        获取设备对应的适配器
        
        Args:
            device_info: 设备信息字典
            
        Returns:
            DeviceModelAdapter: 设备型号适配器对象
            
        Raises:
            ValueError: 如果设备不受支持
        """
        model = device_info.get('model')
        
        if not self.validate_device(device_info):
            raise ValueError(f"不支持的设备: {model}")
        
        return self.model_adapters[model]
    
    def preprocess_data(self, data_packet: Dict[str, Any], device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理数据包
        
        Args:
            data_packet: 原始数据包
            device_info: 设备信息
            
        Returns:
            Dict: 标准化的数据包
        """
        adapter = self.get_adapter_for_device(device_info)
        return adapter.preprocess_data(data_packet)
    
    def calibrate_device(self, calibration_data: Dict[str, Any], device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        校准设备
        
        Args:
            calibration_data: 校准数据
            device_info: 设备信息
            
        Returns:
            Dict: 校准结果
        """
        adapter = self.get_adapter_for_device(device_info)
        return adapter.calibrate(calibration_data)
    
    def validate_calibration(self, device_info: Dict[str, Any], calibration_data: Dict[str, Any]) -> bool:
        """
        验证校准数据是否有效
        
        Args:
            device_info: 设备信息
            calibration_data: 校准数据
            
        Returns:
            bool: 如果校准数据有效则返回True
        """
        # 检查校准时间是否在有效期内
        if 'calibration_timestamp' in calibration_data:
            calibration_time = calibration_data.get('calibration_timestamp')
            current_time = int(time.time())
            calibration_interval = self.config.get('calibration_interval_days', 30) * 24 * 60 * 60
            
            if current_time - calibration_time > calibration_interval:
                logger.warning(f"设备校准已过期，校准时间: {calibration_time}，当前时间: {current_time}")
                return False
        
        # 调用具体型号的校准验证
        adapter = self.get_adapter_for_device(device_info)
        return adapter.validate_calibration(calibration_data)


class DeviceModelAdapter:
    """设备型号适配器基类"""
    
    def __init__(self, model_config):
        """初始化设备型号适配器"""
        self.model_config = model_config
        self.model = model_config.get('model')
        self.manufacturer = model_config.get('manufacturer')
        logger.info(f"初始化设备型号适配器: {self.model}, 制造商: {self.manufacturer}")
    
    def preprocess_data(self, data_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理数据包，将厂商特定格式转换为标准格式
        
        Args:
            data_packet: 原始数据包
            
        Returns:
            Dict: 标准化的数据包
        """
        raise NotImplementedError("子类必须实现预处理方法")
    
    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        校准设备
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            Dict: 校准结果
        """
        raise NotImplementedError("子类必须实现校准方法")
    
    def validate_calibration(self, calibration_data: Dict[str, Any]) -> bool:
        """
        验证校准数据
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            bool: 如果校准数据有效则返回True
        """
        raise NotImplementedError("子类必须实现校准验证方法")


class SuokeWP100Adapter(DeviceModelAdapter):
    """索克WP-100脉诊仪适配器"""
    
    def preprocess_data(self, data_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理索克WP-100脉诊仪数据
        
        Args:
            data_packet: 原始数据包
            
        Returns:
            Dict: 标准化的数据包
        """
        try:
            # 转换数据格式
            standardized_packet = {
                'session_id': data_packet.get('sessionId'),
                'timestamp': int(time.time() * 1000),
                'pressure_data': data_packet.get('pressureData', []),
                'velocity_data': data_packet.get('velocityData', []),
                'position': self._map_position(data_packet.get('position')),
                'skin_temperature': data_packet.get('skinTemp', 0.0),
                'skin_moisture': data_packet.get('skinMoisture', 0.0)
            }
            
            # 应用校准系数
            if 'calibration' in data_packet:
                calibration_factor = data_packet.get('calibration', 1.0)
                standardized_packet['pressure_data'] = [p * calibration_factor for p in standardized_packet['pressure_data']]
            
            return standardized_packet
        except Exception as e:
            logger.error(f"索克WP-100数据预处理失败: {e}")
            raise
    
    def _map_position(self, position_code: str) -> int:
        """
        映射设备特定的部位代码到标准位置枚举
        
        Args:
            position_code: 设备特定的部位代码
            
        Returns:
            int: 标准位置枚举值
        """
        position_map = {
            'L1': 1,  # 左寸
            'L2': 2,  # 左关
            'L3': 3,  # 左尺
            'R1': 4,  # 右寸
            'R2': 5,  # 右关
            'R3': 6,  # 右尺
            'UNKNOWN': 0
        }
        
        return position_map.get(position_code, 0)
    
    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        校准索克WP-100脉诊仪
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            Dict: 校准结果
        """
        try:
            # 提取校准值
            calibration_values = calibration_data.get('calibration_values', [])
            
            if not calibration_values or len(calibration_values) < 5:
                raise ValueError("校准数据不足")
            
            # 计算校准系数
            reference_value = 100.0  # 标准压力参考值
            measured_value = np.mean(calibration_values)
            calibration_factor = reference_value / measured_value if measured_value != 0 else 1.0
            
            # 返回校准结果
            return {
                'calibration_factor': calibration_factor,
                'reference_value': reference_value,
                'measured_value': measured_value,
                'calibration_timestamp': int(time.time()),
                'success': True
            }
        except Exception as e:
            logger.error(f"索克WP-100校准失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_calibration(self, calibration_data: Dict[str, Any]) -> bool:
        """
        验证索克WP-100校准数据
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            bool: 如果校准数据有效则返回True
        """
        # 检查必要字段
        required_fields = ['calibration_factor', 'calibration_timestamp']
        if not all(field in calibration_data for field in required_fields):
            logger.warning("校准数据缺少必要字段")
            return False
        
        # 检查校准系数是否在合理范围内
        factor = calibration_data.get('calibration_factor', 0)
        if factor <= 0.5 or factor >= 2.0:
            logger.warning(f"校准系数超出合理范围: {factor}")
            return False
        
        return True


class TCMDiagnosticsPWAdapter(DeviceModelAdapter):
    """TCM Diagnostics PulseWave Pro适配器"""
    
    def preprocess_data(self, data_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理TCM Diagnostics PulseWave Pro数据
        
        Args:
            data_packet: 原始数据包
            
        Returns:
            Dict: 标准化的数据包
        """
        try:
            # TCM Diagnostics设备的数据格式转换
            # 这里假设TCM设备使用不同的数据结构
            
            # 提取波形数据
            waveform = data_packet.get('waveform', {})
            pressure = waveform.get('pressure', [])
            velocity = waveform.get('velocity', [])
            
            # 映射位置
            location = data_packet.get('location', {})
            position_mapping = {
                'left_cun': 1,
                'left_guan': 2,
                'left_chi': 3,
                'right_cun': 4,
                'right_guan': 5,
                'right_chi': 6
            }
            position = position_mapping.get(location.get('name'), 0)
            
            # 构建标准格式数据包
            standardized_packet = {
                'session_id': data_packet.get('session_id'),
                'timestamp': data_packet.get('timestamp', int(time.time() * 1000)),
                'pressure_data': pressure,
                'velocity_data': velocity,
                'position': position,
                'skin_temperature': data_packet.get('environmental', {}).get('temperature', 0.0),
                'skin_moisture': data_packet.get('environmental', {}).get('humidity', 0.0) / 100.0  # 转换为0-1范围
            }
            
            return standardized_packet
        except Exception as e:
            logger.error(f"TCM Diagnostics数据预处理失败: {e}")
            raise
    
    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        校准TCM Diagnostics PulseWave Pro
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            Dict: 校准结果
        """
        try:
            # TCM Diagnostics设备特有的校准逻辑
            baseline_measures = calibration_data.get('baseline_measures', [])
            offset_value = calibration_data.get('offset_value', 0)
            
            if not baseline_measures:
                raise ValueError("校准基线数据不足")
            
            # 计算校准参数
            avg_baseline = np.mean(baseline_measures)
            scale_factor = 1.0
            if avg_baseline != 0:
                scale_factor = 100.0 / avg_baseline
            
            # 返回校准结果
            return {
                'scale_factor': scale_factor,
                'offset': offset_value,
                'baseline_avg': avg_baseline,
                'calibration_timestamp': int(time.time()),
                'success': True
            }
        except Exception as e:
            logger.error(f"TCM Diagnostics校准失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_calibration(self, calibration_data: Dict[str, Any]) -> bool:
        """
        验证TCM Diagnostics校准数据
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            bool: 如果校准数据有效则返回True
        """
        # 检查必要字段
        if 'scale_factor' not in calibration_data or 'offset' not in calibration_data:
            logger.warning("TCM校准数据缺少必要字段")
            return False
        
        # 检查值是否合理
        scale_factor = calibration_data.get('scale_factor', 0)
        if scale_factor <= 0.1 or scale_factor >= 10.0:
            logger.warning(f"TCM校准比例因子超出合理范围: {scale_factor}")
            return False
        
        return True


class MedSensePR2000Adapter(DeviceModelAdapter):
    """MedSense PulseReader 2000适配器"""
    
    def preprocess_data(self, data_packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理MedSense PulseReader 2000数据
        
        Args:
            data_packet: 原始数据包
            
        Returns:
            Dict: 标准化的数据包
        """
        try:
            # MedSense设备的数据可能是JSON字符串
            if isinstance(data_packet, str):
                try:
                    data_packet = json.loads(data_packet)
                except json.JSONDecodeError:
                    raise ValueError(f"无效的JSON数据: {data_packet[:100]}...")
            
            # 提取波形数据
            sensor_data = data_packet.get('sensor_data', {})
            pressure_array = sensor_data.get('pressure_array', [])
            velocity_array = sensor_data.get('velocity_array', [])
            
            # 位置转换
            position_code = data_packet.get('position', 'UNKNOWN')
            position_map = {
                'LC': 1,  # 左寸
                'LG': 2,  # 左关
                'LH': 3,  # 左尺
                'RC': 4,  # 右寸
                'RG': 5,  # 右关
                'RH': 6,  # 右尺
                'UNKNOWN': 0
            }
            position = position_map.get(position_code, 0)
            
            # 构建标准格式数据包
            standardized_packet = {
                'session_id': data_packet.get('session_id'),
                'timestamp': data_packet.get('timestamp', int(time.time() * 1000)),
                'pressure_data': pressure_array,
                'velocity_data': velocity_array,
                'position': position,
                'skin_temperature': sensor_data.get('temperature', 0.0),
                'skin_moisture': sensor_data.get('humidity', 0.0)
            }
            
            # 应用校准
            if 'calibration' in data_packet:
                calibration = data_packet.get('calibration', {})
                offset = calibration.get('offset', 0.0)
                gain = calibration.get('gain', 1.0)
                standardized_packet['pressure_data'] = [(p + offset) * gain for p in standardized_packet['pressure_data']]
            
            return standardized_packet
        except Exception as e:
            logger.error(f"MedSense数据预处理失败: {e}")
            raise
    
    def calibrate(self, calibration_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        校准MedSense PulseReader 2000
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            Dict: 校准结果
        """
        try:
            # MedSense设备特有的校准逻辑
            reference_samples = calibration_data.get('reference_samples', [])
            
            if not reference_samples or len(reference_samples) < 10:
                raise ValueError("校准样本数据不足")
            
            # 计算偏移和增益
            avg_sample = np.mean(reference_samples)
            std_sample = np.std(reference_samples)
            
            offset = -avg_sample if avg_sample != 0 else 0
            gain = 1.0 / (std_sample / 20.0) if std_sample != 0 else 1.0
            
            # 限制增益范围
            gain = max(0.5, min(gain, 2.0))
            
            # 返回校准结果
            return {
                'offset': offset,
                'gain': gain,
                'avg_sample': avg_sample,
                'std_sample': std_sample,
                'calibration_timestamp': int(time.time()),
                'success': True
            }
        except Exception as e:
            logger.error(f"MedSense校准失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_calibration(self, calibration_data: Dict[str, Any]) -> bool:
        """
        验证MedSense校准数据
        
        Args:
            calibration_data: 校准数据
            
        Returns:
            bool: 如果校准数据有效则返回True
        """
        # 检查必要字段
        required_fields = ['offset', 'gain', 'calibration_timestamp']
        if not all(field in calibration_data for field in required_fields):
            logger.warning("MedSense校准数据缺少必要字段")
            return False
        
        # 检查校准参数是否在合理范围内
        gain = calibration_data.get('gain', 0)
        if gain <= 0.2 or gain >= 5.0:
            logger.warning(f"MedSense增益参数超出合理范围: {gain}")
            return False
        
        return True 