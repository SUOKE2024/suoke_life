"""
sensor_integration - 索克生活项目模块
"""

            from scipy import signal
        import random
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
import asyncio
import json
import logging
import numpy as np
import threading
import time

"""
切诊传感器集成模块

负责管理各种传感器设备，包括压力传感器、脉搏传感器、温度传感器等，
实现数据采集、预处理、质量控制和设备状态监控。
"""


logger = logging.getLogger(__name__)

class SensorType(str, Enum):
    """传感器类型"""
    PRESSURE = "压力传感器"
    PULSE = "脉搏传感器"
    TEMPERATURE = "温度传感器"
    VIBRATION = "振动传感器"
    FORCE = "力传感器"
    POSITION = "位置传感器"

class SensorStatus(str, Enum):
    """传感器状态"""
    CONNECTED = "已连接"
    DISCONNECTED = "已断开"
    ERROR = "错误"
    CALIBRATING = "校准中"
    READY = "就绪"
    COLLECTING = "采集中"

class DataQuality(str, Enum):
    """数据质量"""
    EXCELLENT = "优秀"
    GOOD = "良好"
    FAIR = "一般"
    POOR = "较差"
    INVALID = "无效"

@dataclass
class SensorConfig:
    """传感器配置"""
    sensor_id: str
    sensor_type: SensorType
    sample_rate: float          # 采样率 (Hz)
    resolution: int             # 分辨率 (bits)
    range_min: float           # 测量范围最小值
    range_max: float           # 测量范围最大值
    calibration_params: Dict[str, float] = field(default_factory=dict)
    filter_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SensorData:
    """传感器数据"""
    sensor_id: str
    timestamp: datetime
    values: np.ndarray         # 传感器数值
    quality: DataQuality       # 数据质量
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DeviceInfo:
    """设备信息"""
    device_id: str
    device_name: str
    manufacturer: str
    model: str
    firmware_version: str
    serial_number: str
    connection_type: str       # USB, Bluetooth, WiFi等
    last_calibration: Optional[datetime] = None

class SensorCalibrator:
    """传感器校准器"""
    
    def __init__(self):
        self.calibration_history = {}
        self.calibration_standards = {
            SensorType.PRESSURE: {
                "zero_point": 0.0,
                "reference_pressure": 101325.0,  # 标准大气压 Pa
                "tolerance": 0.01
            },
            SensorType.TEMPERATURE: {
                "ice_point": 0.0,
                "boiling_point": 100.0,
                "tolerance": 0.1
            },
            SensorType.FORCE: {
                "zero_point": 0.0,
                "reference_weight": 1.0,  # 1kg
                "tolerance": 0.005
            }
        }
    
    async def calibrate_sensor(self, sensor_id: str, sensor_type: SensorType,
                             calibration_data: Dict[str, Any]) -> Dict[str, float]:
        """校准传感器"""
        try:
            logger.info(f"开始校准传感器: {sensor_id}")
            
            # 获取校准标准
            standards = self.calibration_standards.get(sensor_type, {})
            
            # 执行校准算法
            calibration_params = await self._perform_calibration(
                sensor_type, calibration_data, standards
            )
            
            # 验证校准结果
            validation_result = await self._validate_calibration(
                sensor_id, calibration_params
            )
            
            if validation_result["valid"]:
                # 保存校准参数
                self.calibration_history[sensor_id] = {
                    "timestamp": datetime.now(),
                    "parameters": calibration_params,
                    "validation": validation_result
                }
                logger.info(f"传感器 {sensor_id} 校准成功")
                return calibration_params
            else:
                logger.error(f"传感器 {sensor_id} 校准验证失败")
                raise ValueError("校准验证失败")
                
        except Exception as e:
            logger.error(f"传感器校准失败: {e}")
            raise
    
    async def _perform_calibration(self, sensor_type: SensorType,
                                 calibration_data: Dict[str, Any],
                                 standards: Dict[str, float]) -> Dict[str, float]:
        """执行校准算法"""
        if sensor_type == SensorType.PRESSURE:
            return await self._calibrate_pressure_sensor(calibration_data, standards)
        elif sensor_type == SensorType.TEMPERATURE:
            return await self._calibrate_temperature_sensor(calibration_data, standards)
        elif sensor_type == SensorType.FORCE:
            return await self._calibrate_force_sensor(calibration_data, standards)
        else:
            # 通用线性校准
            return await self._calibrate_linear_sensor(calibration_data)
    
    async def _calibrate_pressure_sensor(self, data: Dict[str, Any],
                                       standards: Dict[str, float]) -> Dict[str, float]:
        """校准压力传感器"""
        # 零点校准
        zero_readings = data.get("zero_readings", [])
        zero_offset = np.mean(zero_readings) if zero_readings else 0.0
        
        # 满量程校准
        reference_readings = data.get("reference_readings", [])
        reference_pressure = standards.get("reference_pressure", 101325.0)
        
        if reference_readings:
            reference_mean = np.mean(reference_readings)
            scale_factor = reference_pressure / (reference_mean - zero_offset)
        else:
            scale_factor = 1.0
        
        return {
            "zero_offset": zero_offset,
            "scale_factor": scale_factor,
            "linearity_error": 0.0  # 简化处理
        }
    
    async def _calibrate_temperature_sensor(self, data: Dict[str, Any],
                                          standards: Dict[str, float]) -> Dict[str, float]:
        """校准温度传感器"""
        # 冰点校准
        ice_readings = data.get("ice_readings", [])
        ice_offset = np.mean(ice_readings) if ice_readings else 0.0
        
        # 沸点校准
        boiling_readings = data.get("boiling_readings", [])
        if boiling_readings:
            boiling_mean = np.mean(boiling_readings)
            scale_factor = 100.0 / (boiling_mean - ice_offset)
        else:
            scale_factor = 1.0
        
        return {
            "zero_offset": ice_offset,
            "scale_factor": scale_factor,
            "thermal_drift": 0.0
        }
    
    async def _calibrate_force_sensor(self, data: Dict[str, Any],
                                    standards: Dict[str, float]) -> Dict[str, float]:
        """校准力传感器"""
        # 零点校准
        zero_readings = data.get("zero_readings", [])
        zero_offset = np.mean(zero_readings) if zero_readings else 0.0
        
        # 标准重量校准
        weight_readings = data.get("weight_readings", [])
        reference_weight = standards.get("reference_weight", 1.0)
        
        if weight_readings:
            weight_mean = np.mean(weight_readings)
            scale_factor = reference_weight / (weight_mean - zero_offset)
        else:
            scale_factor = 1.0
        
        return {
            "zero_offset": zero_offset,
            "scale_factor": scale_factor,
            "nonlinearity": 0.0
        }
    
    async def _calibrate_linear_sensor(self, data: Dict[str, Any]) -> Dict[str, float]:
        """通用线性传感器校准"""
        # 简单的两点校准
        point1 = data.get("calibration_point1", {"input": 0, "output": 0})
        point2 = data.get("calibration_point2", {"input": 1, "output": 1})
        
        x1, y1 = point1["input"], point1["output"]
        x2, y2 = point2["input"], point2["output"]
        
        if x2 != x1:
            scale_factor = (y2 - y1) / (x2 - x1)
            zero_offset = y1 - scale_factor * x1
        else:
            scale_factor = 1.0
            zero_offset = 0.0
        
        return {
            "zero_offset": zero_offset,
            "scale_factor": scale_factor
        }
    
    async def _validate_calibration(self, sensor_id: str,
                                  calibration_params: Dict[str, float]) -> Dict[str, Any]:
        """验证校准结果"""
        # 简化的验证逻辑
        validation_result = {
            "valid": True,
            "accuracy": 0.95,
            "repeatability": 0.98,
            "stability": 0.97,
            "errors": []
        }
        
        # 检查参数合理性
        scale_factor = calibration_params.get("scale_factor", 1.0)
        if scale_factor <= 0 or scale_factor > 1000:
            validation_result["valid"] = False
            validation_result["errors"].append("Scale factor out of range")
        
        zero_offset = calibration_params.get("zero_offset", 0.0)
        if abs(zero_offset) > 1000:  # 假设的合理范围
            validation_result["valid"] = False
            validation_result["errors"].append("Zero offset out of range")
        
        return validation_result

class DataQualityAssessor:
    """数据质量评估器"""
    
    def __init__(self):
        self.quality_thresholds = {
            "signal_to_noise_ratio": {
                DataQuality.EXCELLENT: 40.0,
                DataQuality.GOOD: 30.0,
                DataQuality.FAIR: 20.0,
                DataQuality.POOR: 10.0
            },
            "stability": {
                DataQuality.EXCELLENT: 0.95,
                DataQuality.GOOD: 0.85,
                DataQuality.FAIR: 0.70,
                DataQuality.POOR: 0.50
            },
            "completeness": {
                DataQuality.EXCELLENT: 0.98,
                DataQuality.GOOD: 0.90,
                DataQuality.FAIR: 0.80,
                DataQuality.POOR: 0.60
            }
        }
    
    async def assess_data_quality(self, sensor_data: SensorData) -> Dict[str, Any]:
        """评估数据质量"""
        try:
            # 计算各项质量指标
            snr = self._calculate_snr(sensor_data.values)
            stability = self._calculate_stability(sensor_data.values)
            completeness = self._calculate_completeness(sensor_data.values)
            
            # 检测异常值
            outliers = self._detect_outliers(sensor_data.values)
            
            # 综合评估
            overall_quality = self._determine_overall_quality(snr, stability, completeness)
            
            quality_report = {
                "overall_quality": overall_quality,
                "signal_to_noise_ratio": snr,
                "stability": stability,
                "completeness": completeness,
                "outlier_percentage": len(outliers) / len(sensor_data.values) * 100,
                "outlier_indices": outliers.tolist(),
                "recommendations": self._generate_quality_recommendations(
                    snr, stability, completeness, outliers
                )
            }
            
            return quality_report
            
        except Exception as e:
            logger.error(f"数据质量评估失败: {e}")
            return {
                "overall_quality": DataQuality.INVALID,
                "error": str(e)
            }
    
    def _calculate_snr(self, data: np.ndarray) -> float:
        """计算信噪比"""
        if len(data) < 2:
            return 0.0
        
        # 简化的SNR计算：信号功率/噪声功率
        signal_power = np.var(data)
        
        # 估算噪声（使用高频成分）
        if len(data) > 10:
            diff = np.diff(data)
            noise_power = np.var(diff) / 2  # 差分的方差除以2
        else:
            noise_power = signal_power * 0.1  # 假设噪声为信号的10%
        
        if noise_power > 0:
            snr_db = 10 * np.log10(signal_power / noise_power)
        else:
            snr_db = 60.0  # 很高的SNR
        
        return max(0.0, snr_db)
    
    def _calculate_stability(self, data: np.ndarray) -> float:
        """计算稳定性"""
        if len(data) < 2:
            return 0.0
        
        # 使用变异系数的倒数作为稳定性指标
        mean_val = np.mean(data)
        if mean_val != 0:
            cv = np.std(data) / abs(mean_val)
            stability = 1.0 / (1.0 + cv)
        else:
            stability = 1.0 if np.std(data) < 1e-6 else 0.0
        
        return stability
    
    def _calculate_completeness(self, data: np.ndarray) -> float:
        """计算完整性"""
        if len(data) == 0:
            return 0.0
        
        # 检查缺失值和无效值
        valid_count = np.sum(np.isfinite(data))
        completeness = valid_count / len(data)
        
        return completeness
    
    def _detect_outliers(self, data: np.ndarray) -> np.ndarray:
        """检测异常值"""
        if len(data) < 4:
            return np.array([])
        
        # 使用IQR方法检测异常值
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outlier_mask = (data < lower_bound) | (data > upper_bound)
        outlier_indices = np.where(outlier_mask)[0]
        
        return outlier_indices
    
    def _determine_overall_quality(self, snr: float, stability: float, 
                                 completeness: float) -> DataQuality:
        """确定整体质量等级"""
        # 加权评分
        weights = {"snr": 0.4, "stability": 0.3, "completeness": 0.3}
        
        # 将SNR转换为0-1分数
        snr_score = min(snr / 40.0, 1.0)  # 40dB为满分
        
        weighted_score = (
            weights["snr"] * snr_score +
            weights["stability"] * stability +
            weights["completeness"] * completeness
        )
        
        if weighted_score >= 0.9:
            return DataQuality.EXCELLENT
        elif weighted_score >= 0.75:
            return DataQuality.GOOD
        elif weighted_score >= 0.6:
            return DataQuality.FAIR
        elif weighted_score >= 0.4:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID
    
    def _generate_quality_recommendations(self, snr: float, stability: float,
                                        completeness: float, 
                                        outliers: np.ndarray) -> List[str]:
        """生成质量改进建议"""
        recommendations = []
        
        if snr < 20:
            recommendations.append("信噪比较低，建议检查传感器连接和屏蔽")
        
        if stability < 0.8:
            recommendations.append("信号稳定性不足，建议检查传感器固定和环境干扰")
        
        if completeness < 0.9:
            recommendations.append("数据完整性不足，建议检查数据传输和存储")
        
        if len(outliers) > len(outliers) * 0.05:  # 超过5%的异常值
            recommendations.append("异常值较多，建议检查传感器校准和测量环境")
        
        if not recommendations:
            recommendations.append("数据质量良好，无需特殊处理")
        
        return recommendations

class SensorDataProcessor:
    """传感器数据处理器"""
    
    def __init__(self):
        self.filter_configs = {
            SensorType.PULSE: {
                "lowpass_cutoff": 5.0,  # Hz
                "highpass_cutoff": 0.5,  # Hz
                "notch_frequency": 50.0  # Hz (工频干扰)
            },
            SensorType.PRESSURE: {
                "lowpass_cutoff": 10.0,
                "highpass_cutoff": 0.1
            },
            SensorType.TEMPERATURE: {
                "lowpass_cutoff": 1.0,
                "highpass_cutoff": 0.01
            }
        }
    
    async def process_sensor_data(self, raw_data: SensorData,
                                config: SensorConfig) -> SensorData:
        """处理传感器数据"""
        try:
            # 应用校准参数
            calibrated_data = self._apply_calibration(raw_data.values, config)
            
            # 滤波处理
            filtered_data = await self._apply_filters(
                calibrated_data, config.sensor_type, config.sample_rate
            )
            
            # 数据平滑
            smoothed_data = self._apply_smoothing(filtered_data)
            
            # 创建处理后的数据对象
            processed_data = SensorData(
                sensor_id=raw_data.sensor_id,
                timestamp=raw_data.timestamp,
                values=smoothed_data,
                quality=raw_data.quality,
                metadata={
                    **raw_data.metadata,
                    "processing_applied": True,
                    "calibration_applied": True,
                    "filtering_applied": True,
                    "smoothing_applied": True
                }
            )
            
            return processed_data
            
        except Exception as e:
            logger.error(f"数据处理失败: {e}")
            raise
    
    def _apply_calibration(self, data: np.ndarray, config: SensorConfig) -> np.ndarray:
        """应用校准参数"""
        calibration_params = config.calibration_params
        
        # 零点偏移校正
        zero_offset = calibration_params.get("zero_offset", 0.0)
        calibrated = data - zero_offset
        
        # 比例因子校正
        scale_factor = calibration_params.get("scale_factor", 1.0)
        calibrated = calibrated * scale_factor
        
        # 非线性校正（如果有）
        nonlinearity = calibration_params.get("nonlinearity", 0.0)
        if nonlinearity != 0.0:
            calibrated = calibrated + nonlinearity * calibrated**2
        
        return calibrated
    
    async def _apply_filters(self, data: np.ndarray, sensor_type: SensorType,
                           sample_rate: float) -> np.ndarray:
        """应用滤波器"""
        if len(data) < 4:  # 数据太少，无法滤波
            return data
        
        filter_config = self.filter_configs.get(sensor_type, {})
        filtered_data = data.copy()
        
        # 低通滤波
        lowpass_cutoff = filter_config.get("lowpass_cutoff")
        if lowpass_cutoff:
            filtered_data = self._lowpass_filter(filtered_data, lowpass_cutoff, sample_rate)
        
        # 高通滤波
        highpass_cutoff = filter_config.get("highpass_cutoff")
        if highpass_cutoff:
            filtered_data = self._highpass_filter(filtered_data, highpass_cutoff, sample_rate)
        
        # 陷波滤波（去除工频干扰）
        notch_frequency = filter_config.get("notch_frequency")
        if notch_frequency:
            filtered_data = self._notch_filter(filtered_data, notch_frequency, sample_rate)
        
        return filtered_data
    
    def _lowpass_filter(self, data: np.ndarray, cutoff: float, 
                       sample_rate: float) -> np.ndarray:
        """低通滤波器"""
        try:
            nyquist = sample_rate / 2
            normalized_cutoff = cutoff / nyquist
            
            if normalized_cutoff >= 1.0:
                return data  # 截止频率太高，不滤波
            
            b, a = signal.butter(4, normalized_cutoff, btype='low')
            filtered = signal.filtfilt(b, a, data)
            return filtered
        except ImportError:
            # 如果没有scipy，使用简单的移动平均
            window_size = max(1, int(sample_rate / cutoff))
            return self._moving_average(data, window_size)
    
    def _highpass_filter(self, data: np.ndarray, cutoff: float,
                        sample_rate: float) -> np.ndarray:
        """高通滤波器"""
        try:
            nyquist = sample_rate / 2
            normalized_cutoff = cutoff / nyquist
            
            if normalized_cutoff <= 0.0:
                return data  # 截止频率太低，不滤波
            
            b, a = signal.butter(4, normalized_cutoff, btype='high')
            filtered = signal.filtfilt(b, a, data)
            return filtered
        except ImportError:
            # 简单的高通滤波：原信号减去低频成分
            window_size = max(1, int(sample_rate / cutoff))
            low_freq = self._moving_average(data, window_size)
            return data - low_freq
    
    def _notch_filter(self, data: np.ndarray, notch_freq: float,
                     sample_rate: float) -> np.ndarray:
        """陷波滤波器"""
        try:
            nyquist = sample_rate / 2
            
            if notch_freq >= nyquist:
                return data  # 陷波频率太高，不滤波
            
            # 设计陷波滤波器
            quality_factor = 30  # Q值
            b, a = signal.iirnotch(notch_freq, quality_factor, sample_rate)
            filtered = signal.filtfilt(b, a, data)
            return filtered
        except ImportError:
            # 没有scipy时返回原数据
            return data
    
    def _moving_average(self, data: np.ndarray, window_size: int) -> np.ndarray:
        """移动平均滤波"""
        if window_size <= 1:
            return data
        
        # 使用卷积实现移动平均
        kernel = np.ones(window_size) / window_size
        
        # 处理边界
        padded_data = np.pad(data, (window_size//2, window_size//2), mode='edge')
        filtered = np.convolve(padded_data, kernel, mode='valid')
        
        return filtered
    
    def _apply_smoothing(self, data: np.ndarray) -> np.ndarray:
        """数据平滑"""
        if len(data) < 5:
            return data
        
        # 使用Savitzky-Golay滤波器进行平滑
        try:
            window_length = min(5, len(data) if len(data) % 2 == 1 else len(data) - 1)
            if window_length >= 3:
                smoothed = signal.savgol_filter(data, window_length, 2)
                return smoothed
        except ImportError:
            pass
        
        # 简单的3点平滑
        smoothed = data.copy()
        for i in range(1, len(data) - 1):
            smoothed[i] = (data[i-1] + data[i] + data[i+1]) / 3
        
        return smoothed

class SensorManager:
    """传感器管理器"""
    
    def __init__(self):
        self.sensors: Dict[str, SensorConfig] = {}
        self.sensor_status: Dict[str, SensorStatus] = {}
        self.data_buffers: Dict[str, deque] = {}
        self.calibrator = SensorCalibrator()
        self.quality_assessor = DataQualityAssessor()
        self.data_processor = SensorDataProcessor()
        
        # 数据采集线程
        self.collection_threads: Dict[str, threading.Thread] = {}
        self.collection_active: Dict[str, bool] = {}
        
        # 回调函数
        self.data_callbacks: List[Callable[[SensorData], None]] = []
        
        logger.info("传感器管理器初始化完成")
    
    async def register_sensor(self, config: SensorConfig, device_info: DeviceInfo) -> bool:
        """注册传感器"""
        try:
            sensor_id = config.sensor_id
            
            # 保存配置
            self.sensors[sensor_id] = config
            self.sensor_status[sensor_id] = SensorStatus.DISCONNECTED
            self.data_buffers[sensor_id] = deque(maxlen=10000)  # 最多保存10000个数据点
            
            # 尝试连接传感器
            connected = await self._connect_sensor(sensor_id, device_info)
            
            if connected:
                self.sensor_status[sensor_id] = SensorStatus.READY
                logger.info(f"传感器 {sensor_id} 注册成功")
                return True
            else:
                logger.error(f"传感器 {sensor_id} 连接失败")
                return False
                
        except Exception as e:
            logger.error(f"传感器注册失败: {e}")
            return False
    
    async def _connect_sensor(self, sensor_id: str, device_info: DeviceInfo) -> bool:
        """连接传感器"""
        # 这里应该实现具体的设备连接逻辑
        # 根据不同的连接类型（USB、蓝牙、WiFi等）使用不同的连接方法
        
        connection_type = device_info.connection_type.lower()
        
        if connection_type == "usb":
            return await self._connect_usb_sensor(sensor_id, device_info)
        elif connection_type == "bluetooth":
            return await self._connect_bluetooth_sensor(sensor_id, device_info)
        elif connection_type == "wifi":
            return await self._connect_wifi_sensor(sensor_id, device_info)
        else:
            logger.warning(f"不支持的连接类型: {connection_type}")
            return False
    
    async def _connect_usb_sensor(self, sensor_id: str, device_info: DeviceInfo) -> bool:
        """连接USB传感器"""
        # 模拟USB连接
        logger.info(f"正在连接USB传感器 {sensor_id}")
        await asyncio.sleep(0.1)  # 模拟连接延迟
        return True
    
    async def _connect_bluetooth_sensor(self, sensor_id: str, device_info: DeviceInfo) -> bool:
        """连接蓝牙传感器"""
        # 模拟蓝牙连接
        logger.info(f"正在连接蓝牙传感器 {sensor_id}")
        await asyncio.sleep(0.2)  # 模拟连接延迟
        return True
    
    async def _connect_wifi_sensor(self, sensor_id: str, device_info: DeviceInfo) -> bool:
        """连接WiFi传感器"""
        # 模拟WiFi连接
        logger.info(f"正在连接WiFi传感器 {sensor_id}")
        await asyncio.sleep(0.15)  # 模拟连接延迟
        return True
    
    async def start_data_collection(self, sensor_id: str) -> bool:
        """开始数据采集"""
        try:
            if sensor_id not in self.sensors:
                logger.error(f"传感器 {sensor_id} 未注册")
                return False
            
            if self.sensor_status[sensor_id] != SensorStatus.READY:
                logger.error(f"传感器 {sensor_id} 状态不正确: {self.sensor_status[sensor_id]}")
                return False
            
            # 启动数据采集线程
            self.collection_active[sensor_id] = True
            collection_thread = threading.Thread(
                target=self._data_collection_loop,
                args=(sensor_id,),
                daemon=True
            )
            collection_thread.start()
            self.collection_threads[sensor_id] = collection_thread
            
            self.sensor_status[sensor_id] = SensorStatus.COLLECTING
            logger.info(f"传感器 {sensor_id} 开始数据采集")
            return True
            
        except Exception as e:
            logger.error(f"启动数据采集失败: {e}")
            return False
    
    def _data_collection_loop(self, sensor_id: str):
        """数据采集循环"""
        config = self.sensors[sensor_id]
        sample_interval = 1.0 / config.sample_rate
        
        while self.collection_active.get(sensor_id, False):
            try:
                # 模拟读取传感器数据
                raw_value = self._simulate_sensor_reading(config.sensor_type)
                
                # 创建传感器数据对象
                sensor_data = SensorData(
                    sensor_id=sensor_id,
                    timestamp=datetime.now(),
                    values=np.array([raw_value]),
                    quality=DataQuality.GOOD,
                    metadata={"raw": True}
                )
                
                # 添加到缓冲区
                self.data_buffers[sensor_id].append(sensor_data)
                
                # 调用回调函数
                for callback in self.data_callbacks:
                    try:
                        callback(sensor_data)
                    except Exception as e:
                        logger.error(f"数据回调函数执行失败: {e}")
                
                time.sleep(sample_interval)
                
            except Exception as e:
                logger.error(f"数据采集错误: {e}")
                time.sleep(0.1)
    
    def _simulate_sensor_reading(self, sensor_type: SensorType) -> float:
        """模拟传感器读数"""
        
        if sensor_type == SensorType.PRESSURE:
            # 模拟压力传感器：0-1000 Pa
            base_value = 500 + 100 * np.sin(time.time() * 2)
            noise = random.gauss(0, 5)
            return base_value + noise
        
        elif sensor_type == SensorType.PULSE:
            # 模拟脉搏传感器：心率60-100 bpm
            heart_rate = 75  # bpm
            pulse_freq = heart_rate / 60  # Hz
            amplitude = 100 + 20 * np.sin(time.time() * pulse_freq * 2 * np.pi)
            noise = random.gauss(0, 2)
            return amplitude + noise
        
        elif sensor_type == SensorType.TEMPERATURE:
            # 模拟温度传感器：35-38°C
            base_temp = 36.5 + 0.5 * np.sin(time.time() * 0.1)
            noise = random.gauss(0, 0.1)
            return base_temp + noise
        
        elif sensor_type == SensorType.FORCE:
            # 模拟力传感器：0-100 N
            base_force = 50 + 20 * np.sin(time.time() * 0.5)
            noise = random.gauss(0, 1)
            return max(0, base_force + noise)
        
        else:
            # 默认值
            return random.gauss(0, 1)
    
    async def stop_data_collection(self, sensor_id: str) -> bool:
        """停止数据采集"""
        try:
            if sensor_id in self.collection_active:
                self.collection_active[sensor_id] = False
            
            if sensor_id in self.collection_threads:
                thread = self.collection_threads[sensor_id]
                thread.join(timeout=1.0)  # 等待线程结束
                del self.collection_threads[sensor_id]
            
            if sensor_id in self.sensor_status:
                self.sensor_status[sensor_id] = SensorStatus.READY
            
            logger.info(f"传感器 {sensor_id} 停止数据采集")
            return True
            
        except Exception as e:
            logger.error(f"停止数据采集失败: {e}")
            return False
    
    async def get_sensor_data(self, sensor_id: str, 
                            duration_seconds: float = 1.0) -> List[SensorData]:
        """获取传感器数据"""
        if sensor_id not in self.data_buffers:
            return []
        
        # 获取指定时间段内的数据
        current_time = datetime.now()
        start_time = current_time - timedelta(seconds=duration_seconds)
        
        buffer = self.data_buffers[sensor_id]
        filtered_data = [
            data for data in buffer
            if data.timestamp >= start_time
        ]
        
        return filtered_data
    
    async def calibrate_sensor(self, sensor_id: str, 
                             calibration_data: Dict[str, Any]) -> bool:
        """校准传感器"""
        try:
            if sensor_id not in self.sensors:
                logger.error(f"传感器 {sensor_id} 未注册")
                return False
            
            config = self.sensors[sensor_id]
            self.sensor_status[sensor_id] = SensorStatus.CALIBRATING
            
            # 执行校准
            calibration_params = await self.calibrator.calibrate_sensor(
                sensor_id, config.sensor_type, calibration_data
            )
            
            # 更新配置
            config.calibration_params = calibration_params
            self.sensor_status[sensor_id] = SensorStatus.READY
            
            logger.info(f"传感器 {sensor_id} 校准完成")
            return True
            
        except Exception as e:
            logger.error(f"传感器校准失败: {e}")
            if sensor_id in self.sensor_status:
                self.sensor_status[sensor_id] = SensorStatus.ERROR
            return False
    
    def add_data_callback(self, callback: Callable[[SensorData], None]):
        """添加数据回调函数"""
        self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable[[SensorData], None]):
        """移除数据回调函数"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    async def get_sensor_status(self, sensor_id: str) -> Optional[SensorStatus]:
        """获取传感器状态"""
        return self.sensor_status.get(sensor_id)
    
    async def get_all_sensors_status(self) -> Dict[str, SensorStatus]:
        """获取所有传感器状态"""
        return self.sensor_status.copy()
    
    async def disconnect_sensor(self, sensor_id: str) -> bool:
        """断开传感器连接"""
        try:
            # 停止数据采集
            await self.stop_data_collection(sensor_id)
            
            # 更新状态
            if sensor_id in self.sensor_status:
                self.sensor_status[sensor_id] = SensorStatus.DISCONNECTED
            
            # 清理缓冲区
            if sensor_id in self.data_buffers:
                self.data_buffers[sensor_id].clear()
            
            logger.info(f"传感器 {sensor_id} 已断开连接")
            return True
            
        except Exception as e:
            logger.error(f"断开传感器连接失败: {e}")
            return False
    
    async def cleanup(self):
        """清理资源"""
        try:
            # 停止所有数据采集
            for sensor_id in list(self.collection_active.keys()):
                await self.stop_data_collection(sensor_id)
            
            # 断开所有传感器
            for sensor_id in list(self.sensors.keys()):
                await self.disconnect_sensor(sensor_id)
            
            logger.info("传感器管理器清理完成")
            
        except Exception as e:
            logger.error(f"传感器管理器清理失败: {e}")

# 导出主要类
__all__ = [
    'SensorManager',
    'SensorCalibrator',
    'DataQualityAssessor',
    'SensorDataProcessor',
    'SensorConfig',
    'SensorData',
    'DeviceInfo',
    'SensorType',
    'SensorStatus',
    'DataQuality'
]