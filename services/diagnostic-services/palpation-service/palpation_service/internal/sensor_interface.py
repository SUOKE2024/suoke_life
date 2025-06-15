"""
sensor_interface - 索克生活项目模块
脉象传感器数据对接模块
支持多种传感器设备的数据采集和处理
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class SensorConnectionType(Enum):
    """传感器连接类型"""
    SERIAL = "serial"
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    ETHERNET = "ethernet"
    MOCK = "mock"

class SensorStatus(Enum):
    """传感器状态"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"
    CALIBRATING = "calibrating"

class DataQuality(Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class SensorConfig:
    """传感器配置"""
    device_id: str
    device_name: str
    connection_type: SensorConnectionType
    connection_params: Dict[str, Any]
    sampling_rate: int
    data_format: str
    calibration_params: Dict[str, float]
    quality_thresholds: Dict[str, float]

@dataclass
class SensorReading:
    """传感器读数"""
    timestamp: datetime
    device_id: str
    sensor_type: str
    raw_value: Union[float, List[float]]
    processed_value: Optional[Union[float, List[float]]] = None
    quality: DataQuality = DataQuality.GOOD
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['quality'] = self.quality.value
        return result

class SensorInterface(ABC):
    """传感器接口基类"""

    def __init__(self, config: SensorConfig):
        """初始化传感器接口"""
        self.config = config
        self.status = SensorStatus.DISCONNECTED
        self.connection = None
        self.data_buffer = []
        self.callbacks: List[Callable[[SensorReading], None]] = []
        self.is_streaming = False
        self.executor = ThreadPoolExecutor(max_workers=2)

    @abstractmethod
    async def connect(self) -> bool:
        """连接传感器"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """断开连接"""
        pass

    @abstractmethod
    async def start_streaming(self) -> bool:
        """开始数据流"""
        pass

    @abstractmethod
    async def stop_streaming(self) -> bool:
        """停止数据流"""
        pass

    @abstractmethod
    async def calibrate(self) -> bool:
        """校准传感器"""
        pass

    @abstractmethod
    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析原始数据"""
        pass

    def add_callback(self, callback: Callable[[SensorReading], None]) -> None:
        """添加数据回调"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[SensorReading], None]) -> None:
        """移除数据回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _notify_callbacks(self, reading: SensorReading) -> None:
        """通知所有回调"""
        for callback in self.callbacks:
            try:
                callback(reading)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")

    def _assess_data_quality(self, reading: SensorReading) -> DataQuality:
        """评估数据质量"""
        if reading.raw_value is None:
            return DataQuality.INVALID

        # 基于配置的质量阈值评估
        thresholds = self.config.quality_thresholds

        if isinstance(reading.raw_value, (int, float)):
            value = abs(reading.raw_value)
            if value < thresholds.get('min_value', 0):
                return DataQuality.POOR
            elif value > thresholds.get('max_value', float('inf')):
                return DataQuality.POOR
            elif value > thresholds.get('excellent_threshold', 0.8):
                return DataQuality.EXCELLENT
            elif value > thresholds.get('good_threshold', 0.6):
                return DataQuality.GOOD
            else:
                return DataQuality.FAIR

        return DataQuality.GOOD

class MockSensorInterface(SensorInterface):
    """模拟传感器接口"""

    def __init__(self, config: SensorConfig):
        """初始化模拟传感器"""
        super().__init__(config)
        self.mock_data_generator = None

    async def connect(self) -> bool:
        """连接模拟传感器"""
        try:
            self.status = SensorStatus.CONNECTING
            await asyncio.sleep(0.1)  # 模拟连接延迟
            self.status = SensorStatus.CONNECTED
            logger.info(f"模拟传感器 {self.config.device_id} 连接成功")
            return True
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"模拟传感器连接失败: {e}")
            return False

    async def disconnect(self) -> bool:
        """断开模拟传感器连接"""
        try:
            self.status = SensorStatus.DISCONNECTED
            logger.info(f"模拟传感器 {self.config.device_id} 断开连接")
            return True
        except Exception as e:
            logger.error(f"模拟传感器断开连接失败: {e}")
            return False

    async def start_streaming(self) -> bool:
        """开始模拟数据流"""
        try:
            if self.status != SensorStatus.CONNECTED:
                return False
            
            self.is_streaming = True
            self.status = SensorStatus.STREAMING
            
            # 启动数据生成任务
            asyncio.create_task(self._generate_mock_data())
            
            logger.info(f"模拟传感器 {self.config.device_id} 开始数据流")
            return True
        except Exception as e:
            logger.error(f"启动模拟数据流失败: {e}")
            return False

    async def stop_streaming(self) -> bool:
        """停止模拟数据流"""
        try:
            self.is_streaming = False
            self.status = SensorStatus.CONNECTED
            logger.info(f"模拟传感器 {self.config.device_id} 停止数据流")
            return True
        except Exception as e:
            logger.error(f"停止模拟数据流失败: {e}")
            return False

    async def calibrate(self) -> bool:
        """校准模拟传感器"""
        try:
            self.status = SensorStatus.CALIBRATING
            await asyncio.sleep(1)  # 模拟校准时间
            self.status = SensorStatus.CONNECTED
            logger.info(f"模拟传感器 {self.config.device_id} 校准完成")
            return True
        except Exception as e:
            logger.error(f"模拟传感器校准失败: {e}")
            return False

    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析模拟数据"""
        try:
            data = json.loads(raw_data.decode('utf-8'))
            readings = []
            
            reading = SensorReading(
                timestamp=datetime.now(),
                device_id=self.config.device_id,
                sensor_type="pressure",
                raw_value=data.get('value', 0.0),
                quality=DataQuality.GOOD,
                metadata=data.get('metadata', {})
            )
            
            readings.append(reading)
            return readings
        except Exception as e:
            logger.error(f"解析模拟数据失败: {e}")
            return []

    async def _generate_mock_data(self) -> None:
        """生成模拟数据"""
        import random
        
        while self.is_streaming:
            try:
                # 生成模拟脉象数据
                pressure_value = random.uniform(80, 120)  # 模拟压力值
                
                reading = SensorReading(
                    timestamp=datetime.now(),
                    device_id=self.config.device_id,
                    sensor_type="pressure",
                    raw_value=pressure_value,
                    quality=self._assess_data_quality_mock(pressure_value),
                    metadata={
                        "temperature": random.uniform(36.0, 37.5),
                        "humidity": random.uniform(40, 60)
                    }
                )
                
                self._notify_callbacks(reading)
                
                # 根据采样率控制生成频率
                await asyncio.sleep(1.0 / self.config.sampling_rate)
                
            except Exception as e:
                logger.error(f"生成模拟数据失败: {e}")
                break

    def _assess_data_quality_mock(self, value: float) -> DataQuality:
        """评估模拟数据质量"""
        if 90 <= value <= 110:
            return DataQuality.EXCELLENT
        elif 85 <= value <= 115:
            return DataQuality.GOOD
        elif 80 <= value <= 120:
            return DataQuality.FAIR
        else:
            return DataQuality.POOR

class SensorManager:
    """传感器管理器"""

    def __init__(self):
        """初始化传感器管理器"""
        self.sensors: Dict[str, SensorInterface] = {}
        self.active_sessions: Dict[str, List[str]] = {}

    def register_sensor(self, sensor: SensorInterface) -> bool:
        """注册传感器"""
        try:
            device_id = sensor.config.device_id
            if device_id in self.sensors:
                logger.warning(f"传感器 {device_id} 已存在，将被替换")
            
            self.sensors[device_id] = sensor
            logger.info(f"传感器 {device_id} 注册成功")
            return True
        except Exception as e:
            logger.error(f"注册传感器失败: {e}")
            return False

    def unregister_sensor(self, device_id: str) -> bool:
        """注销传感器"""
        try:
            if device_id in self.sensors:
                del self.sensors[device_id]
                logger.info(f"传感器 {device_id} 注销成功")
                return True
            else:
                logger.warning(f"传感器 {device_id} 不存在")
                return False
        except Exception as e:
            logger.error(f"注销传感器失败: {e}")
            return False

    def get_sensor(self, device_id: str) -> Optional[SensorInterface]:
        """获取传感器"""
        return self.sensors.get(device_id)

    def list_sensors(self) -> List[str]:
        """列出所有传感器"""
        return list(self.sensors.keys())

    async def connect_all(self) -> Dict[str, bool]:
        """连接所有传感器"""
        results = {}
        for device_id, sensor in self.sensors.items():
            try:
                results[device_id] = await sensor.connect()
            except Exception as e:
                logger.error(f"连接传感器 {device_id} 失败: {e}")
                results[device_id] = False
        return results

    async def disconnect_all(self) -> Dict[str, bool]:
        """断开所有传感器连接"""
        results = {}
        for device_id, sensor in self.sensors.items():
            try:
                results[device_id] = await sensor.disconnect()
            except Exception as e:
                logger.error(f"断开传感器 {device_id} 连接失败: {e}")
                results[device_id] = False
        return results

def create_sensor_manager_with_defaults() -> SensorManager:
    """创建带有默认传感器的管理器"""
    manager = SensorManager()
    
    # 创建默认的模拟传感器
    mock_config = SensorConfig(
        device_id="mock_sensor_001",
        device_name="模拟脉象传感器",
        connection_type=SensorConnectionType.MOCK,
        connection_params={},
        sampling_rate=10,
        data_format="json",
        calibration_params={},
        quality_thresholds={
            'min_value': 60,
            'max_value': 140,
            'excellent_threshold': 0.9,
            'good_threshold': 0.7
        }
    )
    
    mock_sensor = MockSensorInterface(mock_config)
    manager.register_sensor(mock_sensor)
    
    return manager