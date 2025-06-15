#!/usr/bin/env python

"""
传感器管理器 - 统一管理各种传感器数据
支持14种传感器类型，包含数据处理、滤波、校准、融合等功能
"""

import asyncio
import logging
import math
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SensorType(Enum):
    """传感器类型枚举"""

    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    MAGNETOMETER = "magnetometer"
    LIGHT = "light"
    PROXIMITY = "proximity"
    MICROPHONE = "microphone"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    GPS = "gps"
    HEART_RATE = "heart_rate"
    STEP_COUNTER = "step_counter"
    ORIENTATION = "orientation"
    GRAVITY = "gravity"


class SensorStatus(Enum):
    """传感器状态枚举"""

    INACTIVE = "inactive"
    ACTIVE = "active"
    ERROR = "error"
    CALIBRATING = "calibrating"


@dataclass
class SensorReading:
    """传感器读数数据结构"""

    sensor_type: SensorType
    timestamp: float
    values: list[float]
    accuracy: float
    metadata: dict[str, Any] = field(default_factory=dict)
    processed: bool = False


@dataclass
class SensorConfig:
    """传感器配置"""

    enabled: bool
    sampling_rate: float  # Hz
    buffer_size: int
    filters: list[str] = field(default_factory=list)
    calibration: dict[str, float] = field(default_factory=dict)
    thresholds: dict[str, float] = field(default_factory=dict)


class SensorHandler:
    """传感器处理器基类"""

    def __init__(self, sensor_type: SensorType, config: SensorConfig):
        self.sensor_type = sensor_type
        self.config = config
        self.status = SensorStatus.INACTIVE
        self.last_reading = None
        self.error_count = 0

    async def start(self) -> bool:
        """启动传感器"""
        try:
            self.status = SensorStatus.ACTIVE
            logger.info(f"传感器 {self.sensor_type.value} 启动成功")
            return True
        except Exception as e:
            logger.error(f"传感器 {self.sensor_type.value} 启动失败: {e!s}")
            self.status = SensorStatus.ERROR
            return False

    async def stop(self) -> bool:
        """停止传感器"""
        try:
            self.status = SensorStatus.INACTIVE
            logger.info(f"传感器 {self.sensor_type.value} 停止成功")
            return True
        except Exception as e:
            logger.error(f"传感器 {self.sensor_type.value} 停止失败: {e!s}")
            return False

    async def read(self) -> SensorReading | None:
        """读取传感器数据"""
        if self.status != SensorStatus.ACTIVE:
            return None

        try:
            # 子类需要实现具体的读取逻辑
            values = await self._read_raw_data()
            if values is None:
                return None

            reading = SensorReading(
                sensor_type=self.sensor_type,
                timestamp=time.time(),
                values=values,
                accuracy=self._calculate_accuracy(values),
                metadata=self._get_metadata(),
            )

            self.last_reading = reading
            return reading

        except Exception as e:
            logger.error(f"传感器 {self.sensor_type.value} 读取失败: {e!s}")
            self.error_count += 1
            if self.error_count > 5:
                self.status = SensorStatus.ERROR
            return None

    async def _read_raw_data(self) -> list[float] | None:
        """读取原始数据 - 子类需要实现"""
        raise NotImplementedError

    def _calculate_accuracy(self, values: list[float]) -> float:
        """计算读数精度 - 子类可以重写"""
        return 1.0

    def _get_metadata(self) -> dict[str, Any]:
        """获取元数据 - 子类可以重写"""
        return {}


class AccelerometerHandler(SensorHandler):
    """加速度计处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取加速度计数据 (x, y, z)"""
        # 模拟加速度计数据，实际实现中会调用硬件API
        import random

        base_gravity = 9.8
        noise = 0.1

        x = random.uniform(-noise, noise)
        y = random.uniform(-noise, noise)
        z = base_gravity + random.uniform(-noise, noise)

        return [x, y, z]

    def _calculate_accuracy(self, values: list[float]) -> float:
        """基于重力向量计算精度"""
        magnitude = math.sqrt(sum(v**2 for v in values))
        expected_gravity = 9.8
        error = abs(magnitude - expected_gravity) / expected_gravity
        return max(0.0, 1.0 - error)


class GyroscopeHandler(SensorHandler):
    """陀螺仪处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取陀螺仪数据 (角速度 x, y, z)"""
        import random

        noise = 0.05

        return [
            random.uniform(-noise, noise),
            random.uniform(-noise, noise),
            random.uniform(-noise, noise),
        ]


class MagnetometerHandler(SensorHandler):
    """磁力计处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取磁力计数据 (磁场强度 x, y, z)"""
        import random

        # 地球磁场强度约为25-65微特斯拉
        base_field = 45.0
        noise = 5.0

        return [
            base_field + random.uniform(-noise, noise),
            random.uniform(-noise, noise),
            random.uniform(-noise, noise),
        ]


class LightHandler(SensorHandler):
    """光线传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取光线强度数据 (勒克斯)"""
        import random

        # 模拟不同环境的光线强度
        current_hour = datetime.now().hour

        if 6 <= current_hour <= 18:  # 白天
            base_light = random.uniform(100, 1000)
        elif 19 <= current_hour <= 22:  # 傍晚
            base_light = random.uniform(10, 100)
        else:  # 夜晚
            base_light = random.uniform(0, 10)

        return [base_light]


class ProximityHandler(SensorHandler):
    """接近传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取接近距离数据 (厘米)"""
        import random

        # 模拟接近距离，0表示很近，大值表示远
        return [random.uniform(0, 100)]


class MicrophoneHandler(SensorHandler):
    """麦克风处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取音频特征数据 (音量、频率特征等)"""
        import random

        # 模拟音频特征：音量(dB)、主频率(Hz)、频谱能量
        volume = random.uniform(30, 80)  # 分贝
        dominant_freq = random.uniform(100, 4000)  # 主频率
        spectral_energy = random.uniform(0.1, 1.0)  # 频谱能量

        return [volume, dominant_freq, spectral_energy]


class TemperatureHandler(SensorHandler):
    """温度传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取温度数据 (摄氏度)"""
        import random

        # 模拟室内温度
        base_temp = 22.0
        variation = random.uniform(-3, 3)
        return [base_temp + variation]


class HumidityHandler(SensorHandler):
    """湿度传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取湿度数据 (百分比)"""
        import random

        # 模拟室内湿度
        return [random.uniform(40, 70)]


class PressureHandler(SensorHandler):
    """气压传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取气压数据 (百帕)"""
        import random

        # 模拟海平面气压
        base_pressure = 1013.25
        variation = random.uniform(-20, 20)
        return [base_pressure + variation]


class GPSHandler(SensorHandler):
    """GPS传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取GPS数据 (纬度, 经度, 海拔, 精度)"""
        import random

        # 模拟北京地区的GPS数据
        base_lat = 39.9042
        base_lon = 116.4074
        base_alt = 50.0

        lat = base_lat + random.uniform(-0.01, 0.01)
        lon = base_lon + random.uniform(-0.01, 0.01)
        alt = base_alt + random.uniform(-10, 10)
        accuracy = random.uniform(3, 15)  # GPS精度（米）

        return [lat, lon, alt, accuracy]


class HeartRateHandler(SensorHandler):
    """心率传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取心率数据 (BPM)"""
        import random

        # 模拟正常成人心率
        base_hr = 75
        variation = random.uniform(-15, 15)
        return [max(50, base_hr + variation)]


class StepCounterHandler(SensorHandler):
    """计步器处理器"""

    def __init__(self, sensor_type: SensorType, config: SensorConfig):
        super().__init__(sensor_type, config)
        self.total_steps = 0
        self.last_step_time = 0

    async def _read_raw_data(self) -> list[float] | None:
        """读取步数数据 (总步数, 步频)"""
        import random

        current_time = time.time()

        # 模拟步数增加
        if secrets.SystemRandom().random() < 0.3:  # 30%概率增加步数
            self.total_steps += secrets.randbelow(1, 3)
            step_interval = current_time - self.last_step_time
            step_frequency = 1.0 / step_interval if step_interval > 0 else 0
            self.last_step_time = current_time
        else:
            step_frequency = 0

        return [float(self.total_steps), step_frequency]


class OrientationHandler(SensorHandler):
    """方向传感器处理器"""

    async def _read_raw_data(self) -> list[float] | None:
        """读取设备方向数据 (方位角, 俯仰角, 翻滚角)"""
        import random

        # 模拟设备方向（度）
        azimuth = random.uniform(0, 360)  # 方位角
        pitch = random.uniform(-90, 90)  # 俯仰角
        roll = random.uniform(-180, 180)  # 翻滚角

        return [azimuth, pitch, roll]


class DataProcessor:
    """数据处理器"""

    def __init__(self, sensor_type: SensorType):
        self.sensor_type = sensor_type
        self.history = deque(maxlen=100)

    def process(self, reading: SensorReading) -> dict[str, Any]:
        """处理传感器读数"""
        self.history.append(reading)

        processed_data = {
            "raw_values": reading.values,
            "timestamp": reading.timestamp,
            "accuracy": reading.accuracy,
        }

        # 添加统计特征
        if len(self.history) > 1:
            processed_data.update(self._calculate_statistics())

        # 添加传感器特定的处理
        processed_data.update(self._sensor_specific_processing(reading))

        return processed_data

    def _calculate_statistics(self) -> dict[str, Any]:
        """计算统计特征"""
        if not self.history:
            return {}

        # 收集最近的值
        recent_values = []
        for reading in list(self.history)[-10:]:  # 最近10个读数
            recent_values.extend(reading.values)

        if not recent_values:
            return {}

        return {
            "mean": np.mean(recent_values),
            "std": np.std(recent_values),
            "min": np.min(recent_values),
            "max": np.max(recent_values),
            "trend": self._calculate_trend(),
        }

    def _calculate_trend(self) -> str:
        """计算数据趋势"""
        if len(self.history) < 3:
            return "stable"

        recent_readings = list(self.history)[-3:]
        values = [np.mean(r.values) for r in recent_readings]

        if values[-1] > values[0] * 1.1:
            return "increasing"
        elif values[-1] < values[0] * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _sensor_specific_processing(self, reading: SensorReading) -> dict[str, Any]:
        """传感器特定的处理"""
        if self.sensor_type == SensorType.ACCELEROMETER:
            return self._process_accelerometer(reading)
        elif self.sensor_type == SensorType.LIGHT:
            return self._process_light(reading)
        elif self.sensor_type == SensorType.MICROPHONE:
            return self._process_microphone(reading)
        elif self.sensor_type == SensorType.GPS:
            return self._process_gps(reading)
        else:
            return {}

    def _process_accelerometer(self, reading: SensorReading) -> dict[str, Any]:
        """处理加速度计数据"""
        x, y, z = reading.values[:3]
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        # 检测运动状态
        motion_threshold = 10.5  # 重力加速度 + 阈值
        is_moving = magnitude > motion_threshold

        # 检测设备方向
        if abs(z) > abs(x) and abs(z) > abs(y):
            orientation = "vertical" if z > 0 else "upside_down"
        elif abs(x) > abs(y):
            orientation = "landscape"
        else:
            orientation = "portrait"

        return {
            "magnitude": magnitude,
            "is_moving": is_moving,
            "orientation": orientation,
            "tilt_angle": math.degrees(math.atan2(math.sqrt(x**2 + y**2), z)),
        }

    def _process_light(self, reading: SensorReading) -> dict[str, Any]:
        """处理光线传感器数据"""
        lux = reading.values[0]

        # 环境分类
        if lux < 1:
            environment = "dark"
        elif lux < 10:
            environment = "dim"
        elif lux < 100:
            environment = "indoor"
        elif lux < 1000:
            environment = "bright_indoor"
        else:
            environment = "outdoor"

        return {
            "lux": lux,
            "environment": environment,
            "brightness_level": min(100, lux / 10),  # 0-100的亮度级别
        }

    def _process_microphone(self, reading: SensorReading) -> dict[str, Any]:
        """处理麦克风数据"""
        volume, freq, energy = reading.values[:3]

        # 噪音级别分类
        if volume < 40:
            noise_level = "quiet"
        elif volume < 60:
            noise_level = "moderate"
        elif volume < 80:
            noise_level = "loud"
        else:
            noise_level = "very_loud"

        # 声音类型推测
        if freq < 300:
            sound_type = "low_frequency"
        elif freq < 2000:
            sound_type = "speech_range"
        else:
            sound_type = "high_frequency"

        return {
            "volume_db": volume,
            "dominant_frequency": freq,
            "spectral_energy": energy,
            "noise_level": noise_level,
            "sound_type": sound_type,
        }

    def _process_gps(self, reading: SensorReading) -> dict[str, Any]:
        """处理GPS数据"""
        lat, lon, alt, accuracy = reading.values[:4]

        # 计算移动速度（如果有历史数据）
        speed = 0.0
        if len(self.history) > 1:
            prev_reading = self.history[-2]
            prev_lat, prev_lon = prev_reading.values[:2]

            # 计算距离（简化的球面距离）
            dlat = math.radians(lat - prev_lat)
            dlon = math.radians(lon - prev_lon)
            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(math.radians(prev_lat))
                * math.cos(math.radians(lat))
                * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = 6371000 * c  # 地球半径 * 角度 = 距离（米）

            time_diff = reading.timestamp - prev_reading.timestamp
            if time_diff > 0:
                speed = distance / time_diff  # 米/秒

        return {
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "accuracy_meters": accuracy,
            "speed_mps": speed,
            "speed_kmh": speed * 3.6,
        }


class SensorFusionEngine:
    """传感器融合引擎"""

    def __init__(self) -> None:
        self.fusion_algorithms = {
            "orientation": self._fuse_orientation,
            "motion": self._fuse_motion,
            "environment": self._fuse_environment,
            "location": self._fuse_location,
        }

    def fuse_data(
        self, sensor_data: dict[SensorType, list[SensorReading]]
    ) -> dict[str, Any]:
        """融合多传感器数据"""
        fused_results = {}

        for fusion_type, algorithm in self.fusion_algorithms.items():
            try:
                result = algorithm(sensor_data)
                if result:
                    fused_results[fusion_type] = result
            except Exception as e:
                logger.error(f"传感器融合失败 {fusion_type}: {e!s}")

        return fused_results

    def _fuse_orientation(
        self, sensor_data: dict[SensorType, list[SensorReading]]
    ) -> dict[str, Any] | None:
        """融合方向相关的传感器数据"""
        accel_data = sensor_data.get(SensorType.ACCELEROMETER, [])
        gyro_data = sensor_data.get(SensorType.GYROSCOPE, [])
        mag_data = sensor_data.get(SensorType.MAGNETOMETER, [])

        if not accel_data:
            return None

        # 使用最新的加速度计数据计算倾斜角
        latest_accel = accel_data[-1]
        x, y, z = latest_accel.values[:3]

        # 计算俯仰角和翻滚角
        pitch = math.degrees(math.atan2(-x, math.sqrt(y**2 + z**2)))
        roll = math.degrees(math.atan2(y, z))

        # 如果有磁力计数据，计算方位角
        yaw = 0.0
        if mag_data:
            latest_mag = mag_data[-1]
            mx, my, mz = latest_mag.values[:3]
            # 简化的方位角计算
            yaw = math.degrees(math.atan2(my, mx))

        return {
            "pitch": pitch,
            "roll": roll,
            "yaw": yaw,
            "confidence": latest_accel.accuracy,
        }

    def _fuse_motion(
        self, sensor_data: dict[SensorType, list[SensorReading]]
    ) -> dict[str, Any] | None:
        """融合运动相关的传感器数据"""
        accel_data = sensor_data.get(SensorType.ACCELEROMETER, [])
        gyro_data = sensor_data.get(SensorType.GYROSCOPE, [])
        step_data = sensor_data.get(SensorType.STEP_COUNTER, [])

        if not accel_data:
            return None

        # 分析运动状态
        motion_intensity = 0.0
        is_walking = False

        if len(accel_data) >= 5:
            # 计算加速度变化
            recent_magnitudes = []
            for reading in accel_data[-5:]:
                x, y, z = reading.values[:3]
                magnitude = math.sqrt(x**2 + y**2 + z**2)
                recent_magnitudes.append(magnitude)

            # 运动强度基于加速度变化的标准差
            motion_intensity = np.std(recent_magnitudes)

            # 步行检测：规律的加速度变化
            if 0.5 < motion_intensity < 3.0:
                is_walking = True

        # 结合计步器数据
        step_frequency = 0.0
        if step_data:
            latest_step = step_data[-1]
            if len(latest_step.values) > 1:
                step_frequency = latest_step.values[1]

        return {
            "motion_intensity": motion_intensity,
            "is_walking": is_walking,
            "step_frequency": step_frequency,
            "activity_level": self._classify_activity_level(motion_intensity),
        }

    def _fuse_environment(
        self, sensor_data: dict[SensorType, list[SensorReading]]
    ) -> dict[str, Any] | None:
        """融合环境相关的传感器数据"""
        light_data = sensor_data.get(SensorType.LIGHT, [])
        temp_data = sensor_data.get(SensorType.TEMPERATURE, [])
        humidity_data = sensor_data.get(SensorType.HUMIDITY, [])
        pressure_data = sensor_data.get(SensorType.PRESSURE, [])
        mic_data = sensor_data.get(SensorType.MICROPHONE, [])

        environment_score = {}

        # 光线环境
        if light_data:
            lux = light_data[-1].values[0]
            if lux < 10:
                environment_score["lighting"] = "dark"
            elif lux < 100:
                environment_score["lighting"] = "indoor"
            else:
                environment_score["lighting"] = "bright"

        # 温度舒适度
        if temp_data:
            temp = temp_data[-1].values[0]
            if 18 <= temp <= 26:
                environment_score["temperature"] = "comfortable"
            elif temp < 18:
                environment_score["temperature"] = "cold"
            else:
                environment_score["temperature"] = "hot"

        # 湿度舒适度
        if humidity_data:
            humidity = humidity_data[-1].values[0]
            if 40 <= humidity <= 60:
                environment_score["humidity"] = "comfortable"
            elif humidity < 40:
                environment_score["humidity"] = "dry"
            else:
                environment_score["humidity"] = "humid"

        # 噪音环境
        if mic_data:
            volume = mic_data[-1].values[0]
            if volume < 40:
                environment_score["noise"] = "quiet"
            elif volume < 70:
                environment_score["noise"] = "moderate"
            else:
                environment_score["noise"] = "noisy"

        # 综合环境评分
        comfort_score = self._calculate_comfort_score(environment_score)

        return {
            "environment_factors": environment_score,
            "comfort_score": comfort_score,
            "environment_type": self._classify_environment_type(environment_score),
        }

    def _fuse_location(
        self, sensor_data: dict[SensorType, list[SensorReading]]
    ) -> dict[str, Any] | None:
        """融合位置相关的传感器数据"""
        gps_data = sensor_data.get(SensorType.GPS, [])

        if not gps_data:
            return None

        latest_gps = gps_data[-1]
        lat, lon, alt, accuracy = latest_gps.values[:4]

        # 计算移动轨迹
        trajectory = []
        if len(gps_data) > 1:
            for reading in gps_data[-10:]:  # 最近10个位置点
                trajectory.append(
                    {
                        "lat": reading.values[0],
                        "lon": reading.values[1],
                        "timestamp": reading.timestamp,
                    }
                )

        return {
            "current_location": {"lat": lat, "lon": lon, "alt": alt},
            "accuracy": accuracy,
            "trajectory": trajectory,
            "location_stability": self._calculate_location_stability(gps_data),
        }

    def _classify_activity_level(self, motion_intensity: float) -> str:
        """分类活动水平"""
        if motion_intensity < 0.5:
            return "stationary"
        elif motion_intensity < 1.5:
            return "light_activity"
        elif motion_intensity < 3.0:
            return "moderate_activity"
        else:
            return "vigorous_activity"

    def _calculate_comfort_score(self, environment_factors: dict[str, str]) -> float:
        """计算环境舒适度评分"""
        comfort_weights = {
            "comfortable": 1.0,
            "moderate": 0.7,
            "indoor": 0.8,
            "bright": 0.9,
            "quiet": 1.0,
        }

        total_score = 0.0
        factor_count = 0

        for factor, value in environment_factors.items():
            if value in comfort_weights:
                total_score += comfort_weights[value]
                factor_count += 1

        return total_score / factor_count if factor_count > 0 else 0.5

    def _classify_environment_type(self, environment_factors: dict[str, str]) -> str:
        """分类环境类型"""
        lighting = environment_factors.get("lighting", "")
        noise = environment_factors.get("noise", "")

        if lighting == "dark" and noise == "quiet":
            return "bedroom"
        elif lighting == "indoor" and noise == "moderate":
            return "office"
        elif lighting == "bright" and noise == "noisy":
            return "outdoor"
        else:
            return "unknown"

    def _calculate_location_stability(self, gps_data: list[SensorReading]) -> float:
        """计算位置稳定性"""
        if len(gps_data) < 3:
            return 0.5

        # 计算最近几个位置点的变化
        recent_positions = gps_data[-5:]
        distances = []

        for i in range(1, len(recent_positions)):
            prev_pos = recent_positions[i - 1]
            curr_pos = recent_positions[i]

            # 简化的距离计算
            dlat = curr_pos.values[0] - prev_pos.values[0]
            dlon = curr_pos.values[1] - prev_pos.values[1]
            distance = math.sqrt(dlat**2 + dlon**2) * 111000  # 转换为米
            distances.append(distance)

        # 稳定性基于位置变化的标准差
        if distances:
            std_distance = np.std(distances)
            # 标准差越小，稳定性越高
            stability = max(0.0, 1.0 - std_distance / 100.0)
            return min(1.0, stability)

        return 0.5


class SensorManager:
    """传感器管理器核心类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化传感器管理器

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("sensor_manager", {}).get("enabled", False)

        # 传感器配置和处理器
        self.sensor_configs = {}
        self.sensor_handlers = {}
        self.data_processors = {}

        # 数据存储
        self.sensor_data = {}  # sensor_type -> deque of readings
        self.callbacks = {}  # sensor_type -> list of callbacks

        # 传感器融合引擎
        self.fusion_engine = SensorFusionEngine()

        # 统计信息
        self.stats = {
            "total_readings": 0,
            "readings_per_sensor": {},
            "errors_per_sensor": {},
            "average_latency": 0.0,
            "fusion_results": 0,
        }

        # 控制变量
        self.stop_event = asyncio.Event()
        self.data_collection_task = None

        if self.enabled:
            self._initialize_sensors()

        logger.info(f"传感器管理器初始化完成 - 启用: {self.enabled}")

    def _initialize_sensors(self) -> None:
        """初始化传感器"""
        sensor_configs = self.config.get("sensor_manager", {}).get("sensors", {})

        # 创建传感器处理器映射
        handler_classes = {
            SensorType.ACCELEROMETER: AccelerometerHandler,
            SensorType.GYROSCOPE: GyroscopeHandler,
            SensorType.MAGNETOMETER: MagnetometerHandler,
            SensorType.LIGHT: LightHandler,
            SensorType.PROXIMITY: ProximityHandler,
            SensorType.MICROPHONE: MicrophoneHandler,
            SensorType.TEMPERATURE: TemperatureHandler,
            SensorType.HUMIDITY: HumidityHandler,
            SensorType.PRESSURE: PressureHandler,
            SensorType.GPS: GPSHandler,
            SensorType.HEART_RATE: HeartRateHandler,
            SensorType.STEP_COUNTER: StepCounterHandler,
            SensorType.ORIENTATION: OrientationHandler,
        }

        # 初始化每个传感器
        for sensor_name, sensor_config in sensor_configs.items():
            try:
                sensor_type = SensorType(sensor_name)

                # 创建传感器配置对象
                config_obj = SensorConfig(
                    enabled=sensor_config.get("enabled", False),
                    sampling_rate=sensor_config.get("sampling_rate", 1.0),
                    buffer_size=sensor_config.get("buffer_size", 100),
                    filters=sensor_config.get("filters", []),
                    calibration=sensor_config.get("calibration", {}),
                    thresholds=sensor_config.get("thresholds", {}),
                )

                self.sensor_configs[sensor_type] = config_obj

                # 创建传感器处理器
                if sensor_type in handler_classes and config_obj.enabled:
                    handler_class = handler_classes[sensor_type]
                    self.sensor_handlers[sensor_type] = handler_class(
                        sensor_type, config_obj
                    )

                    # 创建数据处理器
                    self.data_processors[sensor_type] = DataProcessor(sensor_type)

                    # 初始化数据存储
                    self.sensor_data[sensor_type] = deque(maxlen=config_obj.buffer_size)
                    self.callbacks[sensor_type] = []

                    # 初始化统计信息
                    self.stats["readings_per_sensor"][sensor_type.value] = 0
                    self.stats["errors_per_sensor"][sensor_type.value] = 0

                    logger.info(f"传感器 {sensor_type.value} 初始化成功")

            except ValueError:
                logger.warning(f"未知的传感器类型: {sensor_name}")
            except Exception as e:
                logger.error(f"传感器 {sensor_name} 初始化失败: {e!s}")

    async def start_sensor(self, sensor_type: SensorType) -> bool:
        """启动指定传感器"""
        if sensor_type not in self.sensor_handlers:
            logger.warning(f"传感器 {sensor_type.value} 未配置或未启用")
            return False

        handler = self.sensor_handlers[sensor_type]
        success = await handler.start()

        if success:
            logger.info(f"传感器 {sensor_type.value} 启动成功")

            # 启动数据收集任务（如果还没有启动）
            if self.data_collection_task is None:
                self.data_collection_task = asyncio.create_task(
                    self._data_collection_loop()
                )

        return success

    async def stop_sensor(self, sensor_type: SensorType) -> bool:
        """停止指定传感器"""
        if sensor_type not in self.sensor_handlers:
            return False

        handler = self.sensor_handlers[sensor_type]
        success = await handler.stop()

        if success:
            logger.info(f"传感器 {sensor_type.value} 停止成功")

        return success

    async def _data_collection_loop(self) -> None:
        """数据收集循环"""
        logger.info("传感器数据收集循环启动")

        while not self.stop_event.is_set():
            try:
                # 收集所有活跃传感器的数据
                for sensor_type, handler in self.sensor_handlers.items():
                    if handler.status == SensorStatus.ACTIVE:
                        reading = await handler.read()
                        if reading:
                            await self._process_reading(sensor_type, reading)

                # 执行传感器融合
                if len(self.sensor_data) > 1:
                    await self._perform_sensor_fusion()

                # 等待下一次采集
                await asyncio.sleep(0.1)  # 100ms间隔

            except Exception as e:
                logger.error(f"数据收集循环异常: {e!s}")
                await asyncio.sleep(1.0)  # 错误时等待更长时间

    async def _process_reading(self, sensor_type: SensorType, reading: SensorReading):
        """处理传感器读数"""
        try:
            # 应用校准
            if sensor_type in self.sensor_configs:
                calibration = self.sensor_configs[sensor_type].calibration
                if calibration:
                    reading = self._apply_calibration(reading, calibration)

            # 存储读数
            self._store_reading(sensor_type, reading)

            # 更新统计信息
            self.stats["total_readings"] += 1
            self.stats["readings_per_sensor"][sensor_type.value] += 1

            # 触发回调
            self._trigger_callbacks(sensor_type, reading)

        except Exception as e:
            logger.error(f"处理传感器读数失败 {sensor_type.value}: {e!s}")
            self.stats["errors_per_sensor"][sensor_type.value] += 1

    def _apply_calibration(
        self, reading: SensorReading, calibration: dict[str, float]
    ) -> SensorReading:
        """应用传感器校准"""
        calibrated_values = []

        for i, value in enumerate(reading.values):
            offset_key = f"offset_{i}"
            scale_key = f"scale_{i}"

            offset = calibration.get(offset_key, 0.0)
            scale = calibration.get(scale_key, 1.0)

            calibrated_value = (value - offset) * scale
            calibrated_values.append(calibrated_value)

        # 创建新的读数对象
        calibrated_reading = SensorReading(
            sensor_type=reading.sensor_type,
            timestamp=reading.timestamp,
            values=calibrated_values,
            accuracy=reading.accuracy,
            metadata=reading.metadata.copy(),
        )
        calibrated_reading.metadata["calibrated"] = True

        return calibrated_reading

    def _store_reading(self, sensor_type: SensorType, reading: SensorReading):
        """存储传感器读数"""
        if sensor_type in self.sensor_data:
            self.sensor_data[sensor_type].append(reading)

    def _trigger_callbacks(self, sensor_type: SensorType, data: Any):
        """触发传感器数据回调"""
        if sensor_type in self.callbacks:
            for callback in self.callbacks[sensor_type]:
                try:
                    callback(sensor_type, data)
                except Exception as e:
                    logger.error(f"传感器回调执行失败: {e!s}")

    async def _perform_sensor_fusion(self) -> None:
        """执行传感器融合"""
        try:
            # 收集最近的传感器数据
            recent_data = {}
            for sensor_type, readings in self.sensor_data.items():
                if readings:
                    # 获取最近5个读数
                    recent_data[sensor_type] = list(readings)[-5:]

            if len(recent_data) > 1:
                fusion_result = self.fusion_engine.fuse_data(recent_data)
                if fusion_result:
                    self.stats["fusion_results"] += 1

                    # 触发融合结果回调
                    self._trigger_callbacks(
                        SensorType.ORIENTATION, fusion_result
                    )  # 使用特殊类型表示融合结果

        except Exception as e:
            logger.error(f"传感器融合失败: {e!s}")

    def get_latest_reading(self, sensor_type: SensorType) -> SensorReading | None:
        """获取最新的传感器读数"""
        if self.sensor_data.get(sensor_type):
            return self.sensor_data[sensor_type][-1]
        return None

    def get_readings(
        self, sensor_type: SensorType, count: int = 10
    ) -> list[SensorReading]:
        """获取指定数量的传感器读数"""
        if sensor_type in self.sensor_data:
            readings = list(self.sensor_data[sensor_type])
            return readings[-count:] if len(readings) > count else readings
        return []

    def get_sensor_status(self, sensor_type: SensorType) -> SensorStatus:
        """获取传感器状态"""
        if sensor_type in self.sensor_handlers:
            return self.sensor_handlers[sensor_type].status
        return SensorStatus.INACTIVE

    def get_all_sensor_status(self) -> dict[str, str]:
        """获取所有传感器状态"""
        status = {}
        for sensor_type, handler in self.sensor_handlers.items():
            status[sensor_type.value] = handler.status.value
        return status

    def register_callback(self, sensor_type: SensorType, callback: Callable):
        """注册传感器数据回调"""
        if sensor_type not in self.callbacks:
            self.callbacks[sensor_type] = []
        self.callbacks[sensor_type].append(callback)

    def unregister_callback(self, sensor_type: SensorType, callback: Callable):
        """取消注册传感器数据回调"""
        if sensor_type in self.callbacks and callback in self.callbacks[sensor_type]:
            self.callbacks[sensor_type].remove(callback)

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "active_sensors": len(
                [
                    h
                    for h in self.sensor_handlers.values()
                    if h.status == SensorStatus.ACTIVE
                ]
            ),
            "total_sensors": len(self.sensor_handlers),
            **self.stats,
        }

    async def shutdown(self) -> None:
        """关闭传感器管理器"""
        logger.info("正在关闭传感器管理器...")

        # 设置停止事件
        self.stop_event.set()

        # 停止所有传感器
        for sensor_type in list(self.sensor_handlers.keys()):
            await self.stop_sensor(sensor_type)

        # 等待数据收集任务结束
        if self.data_collection_task:
            try:
                await asyncio.wait_for(self.data_collection_task, timeout=5.0)
            except TimeoutError:
                logger.warning("数据收集任务停止超时")
                self.data_collection_task.cancel()

        logger.info("传感器管理器已关闭")


class MockSensorHandler:
    """模拟传感器处理器"""

    def __init__(self, sensor_type: SensorType, config: SensorConfig):
        self.sensor_type = sensor_type
        self.config = config
        self.status = SensorStatus.INACTIVE
        self.last_reading = None
        self.error_count = 0

    async def start(self) -> bool:
        """启动传感器"""
        try:
            self.status = SensorStatus.ACTIVE
            logger.info(f"模拟传感器 {self.sensor_type.value} 启动成功")
            return True
        except Exception as e:
            logger.error(f"模拟传感器 {self.sensor_type.value} 启动失败: {e!s}")
            self.status = SensorStatus.ERROR
            return False

    async def stop(self) -> bool:
        """停止传感器"""
        try:
            self.status = SensorStatus.INACTIVE
            logger.info(f"模拟传感器 {self.sensor_type.value} 停止成功")
            return True
        except Exception as e:
            logger.error(f"模拟传感器 {self.sensor_type.value} 停止失败: {e!s}")
            return False

    async def read(self) -> SensorReading | None:
        """读取传感器数据"""
        if self.status != SensorStatus.ACTIVE:
            return None

        try:
            # 生成模拟数据
            values = self._generate_mock_data()
            if values is None:
                return None

            reading = SensorReading(
                sensor_type=self.sensor_type,
                timestamp=time.time(),
                values=values,
                accuracy=0.8,  # 模拟精度
                metadata={"mock": True},
            )

            self.last_reading = reading
            return reading

        except Exception as e:
            logger.error(f"模拟传感器 {self.sensor_type.value} 读取失败: {e!s}")
            self.error_count += 1
            if self.error_count > 5:
                self.status = SensorStatus.ERROR
            return None

    def _generate_mock_data(self) -> list[float] | None:
        """生成模拟传感器数据"""
        import random

        if self.sensor_type == SensorType.ACCELEROMETER:
            return [
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                9.8 + random.uniform(-0.5, 0.5),
            ]
        elif self.sensor_type == SensorType.LIGHT:
            return [random.uniform(0, 1000)]
        elif self.sensor_type == SensorType.TEMPERATURE:
            return [random.uniform(18, 28)]
        elif self.sensor_type == SensorType.HUMIDITY:
            return [random.uniform(40, 70)]
        elif self.sensor_type == SensorType.GPS:
            return [
                39.9042 + random.uniform(-0.01, 0.01),
                116.4074 + random.uniform(-0.01, 0.01),
                50 + random.uniform(-10, 10),
                random.uniform(3, 15),
            ]
        else:
            return [random.uniform(0, 100)]
