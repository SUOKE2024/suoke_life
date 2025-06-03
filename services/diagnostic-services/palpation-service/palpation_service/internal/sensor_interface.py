"""
脉象传感器数据对接模块
支持多种传感器设备的数据采集和处理
"""

import asyncio
import json
import logging
import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from concurrent.futures import ThreadPoolExecutor
import serial
import socket
import bluetooth

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
    raw_value: Union[float, List[float], np.ndarray]
    processed_value: Optional[Union[float, List[float], np.ndarray]] = None
    quality: DataQuality = DataQuality.GOOD
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['quality'] = self.quality.value
        if isinstance(self.raw_value, np.ndarray):
            result['raw_value'] = self.raw_value.tolist()
        if isinstance(self.processed_value, np.ndarray):
            result['processed_value'] = self.processed_value.tolist()
        return result

class SensorInterface(ABC):
    """传感器接口基类"""
    
    def __init__(self, config: SensorConfig):
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
    
    def add_callback(self, callback: Callable[[SensorReading], None]):
        """添加数据回调"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[SensorReading], None]):
        """移除数据回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, reading: SensorReading):
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

class SerialSensorInterface(SensorInterface):
    """串口传感器接口"""
    
    async def connect(self) -> bool:
        """连接串口传感器"""
        try:
            self.status = SensorStatus.CONNECTING
            params = self.config.connection_params
            
            self.connection = serial.Serial(
                port=params['port'],
                baudrate=params.get('baudrate', 9600),
                bytesize=params.get('bytesize', 8),
                parity=params.get('parity', 'N'),
                stopbits=params.get('stopbits', 1),
                timeout=params.get('timeout', 1)
            )
            
            # 等待连接稳定
            await asyncio.sleep(0.5)
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"串口传感器 {self.config.device_id} 连接成功")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"串口传感器连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开串口连接"""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
            self.status = SensorStatus.DISCONNECTED
            logger.info(f"串口传感器 {self.config.device_id} 断开连接")
            return True
        except Exception as e:
            logger.error(f"串口传感器断开失败: {e}")
            return False
    
    async def start_streaming(self) -> bool:
        """开始串口数据流"""
        if self.status != SensorStatus.CONNECTED:
            return False
        
        try:
            self.is_streaming = True
            self.status = SensorStatus.STREAMING
            
            # 启动数据读取任务
            asyncio.create_task(self._read_serial_data())
            
            logger.info(f"串口传感器 {self.config.device_id} 开始数据流")
            return True
            
        except Exception as e:
            logger.error(f"启动串口数据流失败: {e}")
            return False
    
    async def stop_streaming(self) -> bool:
        """停止串口数据流"""
        self.is_streaming = False
        self.status = SensorStatus.CONNECTED
        logger.info(f"串口传感器 {self.config.device_id} 停止数据流")
        return True
    
    async def calibrate(self) -> bool:
        """校准串口传感器"""
        try:
            self.status = SensorStatus.CALIBRATING
            
            # 发送校准命令
            calibration_cmd = self.config.calibration_params.get('command', b'CAL\r\n')
            self.connection.write(calibration_cmd)
            
            # 等待校准完成
            await asyncio.sleep(self.config.calibration_params.get('duration', 5))
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"串口传感器 {self.config.device_id} 校准完成")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"串口传感器校准失败: {e}")
            return False
    
    async def _read_serial_data(self):
        """读取串口数据"""
        while self.is_streaming and self.connection and self.connection.is_open:
            try:
                if self.connection.in_waiting > 0:
                    raw_data = self.connection.read(self.connection.in_waiting)
                    readings = self.parse_data(raw_data)
                    
                    for reading in readings:
                        reading.quality = self._assess_data_quality(reading)
                        self._notify_callbacks(reading)
                
                await asyncio.sleep(1.0 / self.config.sampling_rate)
                
            except Exception as e:
                logger.error(f"串口数据读取错误: {e}")
                await asyncio.sleep(0.1)
    
    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析串口数据"""
        readings = []
        
        try:
            # 根据数据格式解析
            data_format = self.config.data_format
            
            if data_format == "ascii_csv":
                # ASCII CSV格式: "timestamp,value1,value2\n"
                lines = raw_data.decode('utf-8').strip().split('\n')
                for line in lines:
                    if line:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            timestamp = datetime.now()
                            values = [float(p) for p in parts[1:]]
                            
                            reading = SensorReading(
                                timestamp=timestamp,
                                device_id=self.config.device_id,
                                sensor_type="pressure",
                                raw_value=values[0] if len(values) == 1 else values
                            )
                            readings.append(reading)
            
            elif data_format == "binary_float":
                # 二进制浮点格式
                num_values = len(raw_data) // 4
                values = struct.unpack(f'>{num_values}f', raw_data)
                
                for value in values:
                    reading = SensorReading(
                        timestamp=datetime.now(),
                        device_id=self.config.device_id,
                        sensor_type="pressure",
                        raw_value=value
                    )
                    readings.append(reading)
            
            elif data_format == "json":
                # JSON格式
                data = json.loads(raw_data.decode('utf-8'))
                reading = SensorReading(
                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                    device_id=self.config.device_id,
                    sensor_type=data.get('sensor_type', 'pressure'),
                    raw_value=data['value'],
                    metadata=data.get('metadata', {})
                )
                readings.append(reading)
        
        except Exception as e:
            logger.error(f"数据解析失败: {e}")
        
        return readings

class BluetoothSensorInterface(SensorInterface):
    """蓝牙传感器接口"""
    
    async def connect(self) -> bool:
        """连接蓝牙传感器"""
        try:
            self.status = SensorStatus.CONNECTING
            params = self.config.connection_params
            
            # 搜索蓝牙设备
            devices = bluetooth.discover_devices(lookup_names=True)
            target_device = None
            
            for addr, name in devices:
                if name == params.get('device_name') or addr == params.get('mac_address'):
                    target_device = addr
                    break
            
            if not target_device:
                raise Exception("未找到目标蓝牙设备")
            
            # 建立连接
            self.connection = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.connection.connect((target_device, params.get('port', 1)))
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"蓝牙传感器 {self.config.device_id} 连接成功")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"蓝牙传感器连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开蓝牙连接"""
        try:
            if self.connection:
                self.connection.close()
            self.status = SensorStatus.DISCONNECTED
            logger.info(f"蓝牙传感器 {self.config.device_id} 断开连接")
            return True
        except Exception as e:
            logger.error(f"蓝牙传感器断开失败: {e}")
            return False
    
    async def start_streaming(self) -> bool:
        """开始蓝牙数据流"""
        if self.status != SensorStatus.CONNECTED:
            return False
        
        try:
            self.is_streaming = True
            self.status = SensorStatus.STREAMING
            
            # 启动数据读取任务
            asyncio.create_task(self._read_bluetooth_data())
            
            logger.info(f"蓝牙传感器 {self.config.device_id} 开始数据流")
            return True
            
        except Exception as e:
            logger.error(f"启动蓝牙数据流失败: {e}")
            return False
    
    async def stop_streaming(self) -> bool:
        """停止蓝牙数据流"""
        self.is_streaming = False
        self.status = SensorStatus.CONNECTED
        logger.info(f"蓝牙传感器 {self.config.device_id} 停止数据流")
        return True
    
    async def calibrate(self) -> bool:
        """校准蓝牙传感器"""
        try:
            self.status = SensorStatus.CALIBRATING
            
            # 发送校准命令
            calibration_cmd = self.config.calibration_params.get('command', b'CAL')
            self.connection.send(calibration_cmd)
            
            # 等待校准完成
            await asyncio.sleep(self.config.calibration_params.get('duration', 5))
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"蓝牙传感器 {self.config.device_id} 校准完成")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"蓝牙传感器校准失败: {e}")
            return False
    
    async def _read_bluetooth_data(self):
        """读取蓝牙数据"""
        while self.is_streaming and self.connection:
            try:
                raw_data = self.connection.recv(1024)
                if raw_data:
                    readings = self.parse_data(raw_data)
                    
                    for reading in readings:
                        reading.quality = self._assess_data_quality(reading)
                        self._notify_callbacks(reading)
                
                await asyncio.sleep(1.0 / self.config.sampling_rate)
                
            except Exception as e:
                logger.error(f"蓝牙数据读取错误: {e}")
                await asyncio.sleep(0.1)
    
    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析蓝牙数据"""
        # 使用与串口相同的解析逻辑
        return super().parse_data(raw_data)

class WiFiSensorInterface(SensorInterface):
    """WiFi传感器接口"""
    
    async def connect(self) -> bool:
        """连接WiFi传感器"""
        try:
            self.status = SensorStatus.CONNECTING
            params = self.config.connection_params
            
            # 创建TCP连接
            self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connection.settimeout(params.get('timeout', 5))
            self.connection.connect((params['host'], params['port']))
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"WiFi传感器 {self.config.device_id} 连接成功")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"WiFi传感器连接失败: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """断开WiFi连接"""
        try:
            if self.connection:
                self.connection.close()
            self.status = SensorStatus.DISCONNECTED
            logger.info(f"WiFi传感器 {self.config.device_id} 断开连接")
            return True
        except Exception as e:
            logger.error(f"WiFi传感器断开失败: {e}")
            return False
    
    async def start_streaming(self) -> bool:
        """开始WiFi数据流"""
        if self.status != SensorStatus.CONNECTED:
            return False
        
        try:
            self.is_streaming = True
            self.status = SensorStatus.STREAMING
            
            # 发送开始命令
            start_cmd = self.config.connection_params.get('start_command', b'START\n')
            self.connection.send(start_cmd)
            
            # 启动数据读取任务
            asyncio.create_task(self._read_wifi_data())
            
            logger.info(f"WiFi传感器 {self.config.device_id} 开始数据流")
            return True
            
        except Exception as e:
            logger.error(f"启动WiFi数据流失败: {e}")
            return False
    
    async def stop_streaming(self) -> bool:
        """停止WiFi数据流"""
        try:
            # 发送停止命令
            stop_cmd = self.config.connection_params.get('stop_command', b'STOP\n')
            self.connection.send(stop_cmd)
            
            self.is_streaming = False
            self.status = SensorStatus.CONNECTED
            logger.info(f"WiFi传感器 {self.config.device_id} 停止数据流")
            return True
        except Exception as e:
            logger.error(f"停止WiFi数据流失败: {e}")
            return False
    
    async def calibrate(self) -> bool:
        """校准WiFi传感器"""
        try:
            self.status = SensorStatus.CALIBRATING
            
            # 发送校准命令
            calibration_cmd = self.config.calibration_params.get('command', b'CALIBRATE\n')
            self.connection.send(calibration_cmd)
            
            # 等待校准完成
            await asyncio.sleep(self.config.calibration_params.get('duration', 5))
            
            self.status = SensorStatus.CONNECTED
            logger.info(f"WiFi传感器 {self.config.device_id} 校准完成")
            return True
            
        except Exception as e:
            self.status = SensorStatus.ERROR
            logger.error(f"WiFi传感器校准失败: {e}")
            return False
    
    async def _read_wifi_data(self):
        """读取WiFi数据"""
        while self.is_streaming and self.connection:
            try:
                raw_data = self.connection.recv(4096)
                if raw_data:
                    readings = self.parse_data(raw_data)
                    
                    for reading in readings:
                        reading.quality = self._assess_data_quality(reading)
                        self._notify_callbacks(reading)
                
                await asyncio.sleep(1.0 / self.config.sampling_rate)
                
            except Exception as e:
                logger.error(f"WiFi数据读取错误: {e}")
                await asyncio.sleep(0.1)
    
    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析WiFi数据"""
        # 使用与串口相同的解析逻辑
        return super().parse_data(raw_data)

class MockSensorInterface(SensorInterface):
    """模拟传感器接口（用于测试）"""
    
    def __init__(self, config: SensorConfig):
        super().__init__(config)
        self.mock_data_generator = self._create_mock_generator()
    
    def _create_mock_generator(self):
        """创建模拟数据生成器"""
        def generator():
            t = 0
            while True:
                # 生成模拟脉搏波形
                pulse_rate = 75  # 75 BPM
                amplitude = 1.0
                noise_level = 0.1
                
                # 基础正弦波 + 谐波 + 噪声
                base_freq = pulse_rate / 60.0  # Hz
                value = (amplitude * np.sin(2 * np.pi * base_freq * t) +
                        0.3 * np.sin(2 * np.pi * 2 * base_freq * t) +
                        0.1 * np.sin(2 * np.pi * 3 * base_freq * t) +
                        noise_level * np.random.normal())
                
                t += 1.0 / self.config.sampling_rate
                yield value
        
        return generator()
    
    async def connect(self) -> bool:
        """连接模拟传感器"""
        await asyncio.sleep(0.1)  # 模拟连接延迟
        self.status = SensorStatus.CONNECTED
        logger.info(f"模拟传感器 {self.config.device_id} 连接成功")
        return True
    
    async def disconnect(self) -> bool:
        """断开模拟传感器"""
        self.status = SensorStatus.DISCONNECTED
        logger.info(f"模拟传感器 {self.config.device_id} 断开连接")
        return True
    
    async def start_streaming(self) -> bool:
        """开始模拟数据流"""
        if self.status != SensorStatus.CONNECTED:
            return False
        
        self.is_streaming = True
        self.status = SensorStatus.STREAMING
        
        # 启动数据生成任务
        asyncio.create_task(self._generate_mock_data())
        
        logger.info(f"模拟传感器 {self.config.device_id} 开始数据流")
        return True
    
    async def stop_streaming(self) -> bool:
        """停止模拟数据流"""
        self.is_streaming = False
        self.status = SensorStatus.CONNECTED
        logger.info(f"模拟传感器 {self.config.device_id} 停止数据流")
        return True
    
    async def calibrate(self) -> bool:
        """校准模拟传感器"""
        self.status = SensorStatus.CALIBRATING
        await asyncio.sleep(1)  # 模拟校准时间
        self.status = SensorStatus.CONNECTED
        logger.info(f"模拟传感器 {self.config.device_id} 校准完成")
        return True
    
    async def _generate_mock_data(self):
        """生成模拟数据"""
        while self.is_streaming:
            try:
                value = next(self.mock_data_generator)
                
                reading = SensorReading(
                    timestamp=datetime.now(),
                    device_id=self.config.device_id,
                    sensor_type="pressure",
                    raw_value=value,
                    metadata={'mock': True}
                )
                
                reading.quality = self._assess_data_quality(reading)
                self._notify_callbacks(reading)
                
                await asyncio.sleep(1.0 / self.config.sampling_rate)
                
            except Exception as e:
                logger.error(f"模拟数据生成错误: {e}")
                await asyncio.sleep(0.1)
    
    def parse_data(self, raw_data: bytes) -> List[SensorReading]:
        """解析模拟数据"""
        # 模拟传感器不需要解析原始数据
        return []

class SensorManager:
    """传感器管理器"""
    
    def __init__(self):
        self.sensors: Dict[str, SensorInterface] = {}
        self.data_handlers: List[Callable[[SensorReading], None]] = []
        self.is_recording = False
        self.recorded_data: List[SensorReading] = []
    
    def register_sensor(self, config: SensorConfig) -> bool:
        """注册传感器"""
        try:
            # 根据连接类型创建传感器接口
            if config.connection_type == SensorConnectionType.SERIAL:
                sensor = SerialSensorInterface(config)
            elif config.connection_type == SensorConnectionType.BLUETOOTH:
                sensor = BluetoothSensorInterface(config)
            elif config.connection_type == SensorConnectionType.WIFI:
                sensor = WiFiSensorInterface(config)
            elif config.connection_type == SensorConnectionType.MOCK:
                sensor = MockSensorInterface(config)
            else:
                raise ValueError(f"不支持的连接类型: {config.connection_type}")
            
            # 添加数据处理回调
            sensor.add_callback(self._handle_sensor_data)
            
            self.sensors[config.device_id] = sensor
            logger.info(f"传感器 {config.device_id} 注册成功")
            return True
            
        except Exception as e:
            logger.error(f"传感器注册失败: {e}")
            return False
    
    def unregister_sensor(self, device_id: str) -> bool:
        """注销传感器"""
        if device_id in self.sensors:
            sensor = self.sensors[device_id]
            asyncio.create_task(sensor.disconnect())
            del self.sensors[device_id]
            logger.info(f"传感器 {device_id} 注销成功")
            return True
        return False
    
    async def connect_all(self) -> Dict[str, bool]:
        """连接所有传感器"""
        results = {}
        tasks = []
        
        for device_id, sensor in self.sensors.items():
            task = asyncio.create_task(sensor.connect())
            tasks.append((device_id, task))
        
        for device_id, task in tasks:
            results[device_id] = await task
        
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """断开所有传感器"""
        results = {}
        tasks = []
        
        for device_id, sensor in self.sensors.items():
            task = asyncio.create_task(sensor.disconnect())
            tasks.append((device_id, task))
        
        for device_id, task in tasks:
            results[device_id] = await task
        
        return results
    
    async def start_all_streaming(self) -> Dict[str, bool]:
        """开始所有传感器数据流"""
        results = {}
        tasks = []
        
        for device_id, sensor in self.sensors.items():
            if sensor.status == SensorStatus.CONNECTED:
                task = asyncio.create_task(sensor.start_streaming())
                tasks.append((device_id, task))
        
        for device_id, task in tasks:
            results[device_id] = await task
        
        return results
    
    async def stop_all_streaming(self) -> Dict[str, bool]:
        """停止所有传感器数据流"""
        results = {}
        tasks = []
        
        for device_id, sensor in self.sensors.items():
            if sensor.status == SensorStatus.STREAMING:
                task = asyncio.create_task(sensor.stop_streaming())
                tasks.append((device_id, task))
        
        for device_id, task in tasks:
            results[device_id] = await task
        
        return results
    
    async def calibrate_all(self) -> Dict[str, bool]:
        """校准所有传感器"""
        results = {}
        tasks = []
        
        for device_id, sensor in self.sensors.items():
            if sensor.status == SensorStatus.CONNECTED:
                task = asyncio.create_task(sensor.calibrate())
                tasks.append((device_id, task))
        
        for device_id, task in tasks:
            results[device_id] = await task
        
        return results
    
    def get_sensor_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有传感器状态"""
        status = {}
        for device_id, sensor in self.sensors.items():
            status[device_id] = {
                'status': sensor.status.value,
                'device_name': sensor.config.device_name,
                'connection_type': sensor.config.connection_type.value,
                'sampling_rate': sensor.config.sampling_rate,
                'is_streaming': sensor.is_streaming
            }
        return status
    
    def add_data_handler(self, handler: Callable[[SensorReading], None]):
        """添加数据处理器"""
        self.data_handlers.append(handler)
    
    def remove_data_handler(self, handler: Callable[[SensorReading], None]):
        """移除数据处理器"""
        if handler in self.data_handlers:
            self.data_handlers.remove(handler)
    
    def start_recording(self):
        """开始记录数据"""
        self.is_recording = True
        self.recorded_data.clear()
        logger.info("开始记录传感器数据")
    
    def stop_recording(self) -> List[Dict[str, Any]]:
        """停止记录数据并返回记录的数据"""
        self.is_recording = False
        data = [reading.to_dict() for reading in self.recorded_data]
        logger.info(f"停止记录，共记录 {len(data)} 条数据")
        return data
    
    def _handle_sensor_data(self, reading: SensorReading):
        """处理传感器数据"""
        # 记录数据
        if self.is_recording:
            self.recorded_data.append(reading)
        
        # 调用所有数据处理器
        for handler in self.data_handlers:
            try:
                handler(reading)
            except Exception as e:
                logger.error(f"数据处理器执行失败: {e}")

# 预定义的传感器配置
PREDEFINED_SENSOR_CONFIGS = {
    "pressure_sensor_1": SensorConfig(
        device_id="pressure_sensor_1",
        device_name="压力传感器1",
        connection_type=SensorConnectionType.SERIAL,
        connection_params={
            'port': '/dev/ttyUSB0',
            'baudrate': 115200,
            'timeout': 1
        },
        sampling_rate=1000,
        data_format="ascii_csv",
        calibration_params={
            'command': b'CAL\r\n',
            'duration': 3
        },
        quality_thresholds={
            'min_value': 0.1,
            'max_value': 10.0,
            'excellent_threshold': 0.8,
            'good_threshold': 0.6
        }
    ),
    
    "bluetooth_pulse_sensor": SensorConfig(
        device_id="bluetooth_pulse_sensor",
        device_name="蓝牙脉搏传感器",
        connection_type=SensorConnectionType.BLUETOOTH,
        connection_params={
            'device_name': 'PulseSensor',
            'port': 1
        },
        sampling_rate=500,
        data_format="json",
        calibration_params={
            'command': b'CAL',
            'duration': 5
        },
        quality_thresholds={
            'min_value': 0.05,
            'max_value': 5.0,
            'excellent_threshold': 0.9,
            'good_threshold': 0.7
        }
    ),
    
    "wifi_multimodal_sensor": SensorConfig(
        device_id="wifi_multimodal_sensor",
        device_name="WiFi多模态传感器",
        connection_type=SensorConnectionType.WIFI,
        connection_params={
            'host': '192.168.1.100',
            'port': 8080,
            'start_command': b'START_STREAM\n',
            'stop_command': b'STOP_STREAM\n'
        },
        sampling_rate=1000,
        data_format="binary_float",
        calibration_params={
            'command': b'CALIBRATE\n',
            'duration': 10
        },
        quality_thresholds={
            'min_value': 0.01,
            'max_value': 20.0,
            'excellent_threshold': 0.95,
            'good_threshold': 0.8
        }
    ),
    
    "mock_sensor": SensorConfig(
        device_id="mock_sensor",
        device_name="模拟传感器",
        connection_type=SensorConnectionType.MOCK,
        connection_params={},
        sampling_rate=1000,
        data_format="mock",
        calibration_params={'duration': 1},
        quality_thresholds={
            'min_value': -2.0,
            'max_value': 2.0,
            'excellent_threshold': 0.8,
            'good_threshold': 0.6
        }
    )
}

def create_sensor_manager_with_defaults() -> SensorManager:
    """创建带有默认传感器配置的传感器管理器"""
    manager = SensorManager()
    
    # 注册预定义的传感器
    for config in PREDEFINED_SENSOR_CONFIGS.values():
        manager.register_sensor(config)
    
    return manager 