"""
设备连接器模块
实现主流健康设备的API连接和数据获取
支持MCP跨设备数据整合
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import aiohttp
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ExtendedHealthMetrics(Enum):
    """扩展健康指标类型"""
    # 基础生命体征
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BODY_TEMPERATURE = "body_temperature"
    RESPIRATORY_RATE = "respiratory_rate"
    BLOOD_OXYGEN = "blood_oxygen"
    
    # 活动指标
    STEPS = "steps"
    DISTANCE = "distance"
    CALORIES = "calories"
    ACTIVE_MINUTES = "active_minutes"
    FLOORS_CLIMBED = "floors_climbed"
    
    # 睡眠指标
    SLEEP_DURATION = "sleep_duration"
    DEEP_SLEEP = "deep_sleep"
    REM_SLEEP = "rem_sleep"
    LIGHT_SLEEP = "light_sleep"
    SLEEP_EFFICIENCY = "sleep_efficiency"
    SLEEP_SCORE = "sleep_score"
    
    # 高级指标
    HRV = "heart_rate_variability"
    STRESS_LEVEL = "stress_level"
    RECOVERY_SCORE = "recovery_score"
    READINESS_SCORE = "readiness_score"
    STRAIN_SCORE = "strain_score"
    
    # 身体成分
    WEIGHT = "weight"
    BMI = "bmi"
    BODY_FAT = "body_fat"
    MUSCLE_MASS = "muscle_mass"
    BONE_MASS = "bone_mass"
    WATER_PERCENTAGE = "water_percentage"
    
    # 女性健康
    MENSTRUAL_CYCLE = "menstrual_cycle"
    OVULATION = "ovulation"
    
    # 血糖和营养
    BLOOD_GLUCOSE = "blood_glucose"
    HYDRATION = "hydration"
    NUTRITION_INTAKE = "nutrition_intake"

@dataclass
class DeviceData:
    """设备数据标准格式"""
    device_id: str
    device_type: str
    device_name: str
    data_type: str
    value: Union[float, int, str, Dict[str, Any]]
    unit: Optional[str]
    timestamp: datetime
    quality_score: float
    raw_data: Dict[str, Any]
    # 新增字段
    metric_type: Optional[ExtendedHealthMetrics] = None
    confidence_level: Optional[float] = None
    data_source: Optional[str] = None
    sync_status: Optional[str] = None
    processing_time: Optional[float] = None

class BaseDeviceConnector(ABC):
    """设备连接器基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device_type = config.get('device_type', 'unknown')
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.timeout = config.get('timeout', 30)
        self.is_connected = False
        self.last_sync_time = None
        
    @abstractmethod
    async def authenticate(self) -> bool:
        """设备认证"""
        pass
        
    @abstractmethod
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取健康数据"""
        pass
        
    @abstractmethod
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取设备信息"""
        pass

class AppleHealthConnector(BaseDeviceConnector):
    """Apple Health 连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "apple_health"
        
    async def authenticate(self) -> bool:
        """Apple Health认证"""
        try:
            # 模拟Apple Health认证流程
            # 实际实现需要使用HealthKit API
            self.is_connected = True
            logger.info(f"Apple Health认证成功")
            return True
        except Exception as e:
            logger.error(f"Apple Health认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取Apple Health数据"""
        try:
            # 模拟从Apple Health获取数据
            mock_data = [
                DeviceData(
                    device_id="iphone_14_pro",
                    device_type="apple_health",
                    device_name="iPhone 14 Pro",
                    data_type="heart_rate",
                    value=72,
                    unit="bpm",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.95,
                    raw_data={"source": "Apple Watch", "confidence": 0.95},
                    metric_type=ExtendedHealthMetrics.HEART_RATE,
                    confidence_level=0.95,
                    data_source="apple_healthkit",
                    sync_status="synced",
                    processing_time=0.08
                ),
                DeviceData(
                    device_id="iphone_14_pro",
                    device_type="apple_health",
                    device_name="iPhone 14 Pro",
                    data_type="steps",
                    value=8500,
                    unit="steps",
                    timestamp=datetime.now() - timedelta(hours=2),
                    quality_score=0.98,
                    raw_data={"source": "iPhone", "confidence": 0.98},
                    metric_type=ExtendedHealthMetrics.STEPS,
                    confidence_level=0.98,
                    data_source="apple_healthkit",
                    sync_status="synced",
                    processing_time=0.05
                ),
                # 新增HRV数据
                DeviceData(
                    device_id="apple_watch_series_9",
                    device_type="apple_health",
                    device_name="Apple Watch Series 9",
                    data_type="hrv",
                    value=45.2,
                    unit="ms",
                    timestamp=datetime.now() - timedelta(hours=3),
                    quality_score=0.93,
                    raw_data={"source": "Apple Watch", "measurement_type": "RMSSD"},
                    metric_type=ExtendedHealthMetrics.HRV,
                    confidence_level=0.93,
                    data_source="apple_healthkit",
                    sync_status="synced",
                    processing_time=0.12
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从Apple Health获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取Apple Health数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取Apple设备信息"""
        return {
            "device_id": device_id,
            "device_type": "apple_health",
            "device_name": "iPhone 14 Pro",
            "manufacturer": "Apple",
            "model": "iPhone14,2",
            "os_version": "iOS 17.0",
            "app_version": "Health 16.0",
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "heart_rate", "steps", "distance", "calories", "sleep_duration", "hrv", "blood_oxygen"
            ]]
        }

class FitbitConnector(BaseDeviceConnector):
    """Fitbit 连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "fitbit"
        self.base_url = "https://api.fitbit.com/1"
        
    async def authenticate(self) -> bool:
        """Fitbit OAuth认证"""
        try:
            # 模拟Fitbit OAuth认证
            self.is_connected = True
            logger.info(f"Fitbit认证成功")
            return True
        except Exception as e:
            logger.error(f"Fitbit认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取Fitbit数据"""
        try:
            # 模拟从Fitbit API获取数据
            mock_data = [
                DeviceData(
                    device_id="fitbit_versa_3",
                    device_type="fitbit",
                    device_name="Fitbit Versa 3",
                    data_type="sleep_duration",
                    value=7.5,
                    unit="hours",
                    timestamp=datetime.now() - timedelta(hours=8),
                    quality_score=0.92,
                    raw_data={"sleep_stages": {"deep": 1.2, "light": 4.8, "rem": 1.5}},
                    metric_type=ExtendedHealthMetrics.SLEEP_DURATION,
                    confidence_level=0.92,
                    data_source="fitbit_api",
                    sync_status="synced",
                    processing_time=0.15
                ),
                # 新增压力水平数据
                DeviceData(
                    device_id="fitbit_versa_3",
                    device_type="fitbit",
                    device_name="Fitbit Versa 3",
                    data_type="stress_level",
                    value=65,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.88,
                    raw_data={"stress_management_score": 65, "responsiveness": "moderate"},
                    metric_type=ExtendedHealthMetrics.STRESS_LEVEL,
                    confidence_level=0.88,
                    data_source="fitbit_api",
                    sync_status="synced",
                    processing_time=0.18
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从Fitbit获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取Fitbit数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取Fitbit设备信息"""
        return {
            "device_id": device_id,
            "device_type": "fitbit",
            "device_name": "Fitbit Versa 3",
            "manufacturer": "Fitbit",
            "model": "FB511",
            "battery_level": 85,
            "last_sync": datetime.now().isoformat(),
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "heart_rate", "steps", "sleep_duration", "stress_level", "calories", "distance"
            ]]
        }

class XiaomiConnector(BaseDeviceConnector):
    """小米手环连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "xiaomi"
        self.base_url = "https://api-mifit.huami.com"
        
    async def authenticate(self) -> bool:
        """小米账号认证"""
        try:
            # 模拟小米账号认证
            self.is_connected = True
            logger.info(f"小米设备认证成功")
            return True
        except Exception as e:
            logger.error(f"小米设备认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取小米手环数据"""
        try:
            # 模拟从小米API获取数据
            mock_data = [
                DeviceData(
                    device_id="mi_band_7",
                    device_type="xiaomi",
                    device_name="小米手环7",
                    data_type="heart_rate",
                    value=68,
                    unit="bpm",
                    timestamp=datetime.now() - timedelta(minutes=30),
                    quality_score=0.89,
                    raw_data={"measurement_type": "automatic", "activity_state": "resting"},
                    metric_type=ExtendedHealthMetrics.HEART_RATE,
                    confidence_level=0.89,
                    data_source="xiaomi_mifit_api",
                    sync_status="synced",
                    processing_time=0.12
                ),
                # 新增血氧数据
                DeviceData(
                    device_id="mi_band_7",
                    device_type="xiaomi",
                    device_name="小米手环7",
                    data_type="blood_oxygen",
                    value=98,
                    unit="%",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.91,
                    raw_data={"measurement_duration": 30, "measurement_quality": "good"},
                    metric_type=ExtendedHealthMetrics.BLOOD_OXYGEN,
                    confidence_level=0.91,
                    data_source="xiaomi_mifit_api",
                    sync_status="synced",
                    processing_time=0.10
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从小米设备获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取小米设备数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取小米设备信息"""
        return {
            "device_id": device_id,
            "device_type": "xiaomi",
            "device_name": "小米手环7",
            "manufacturer": "小米",
            "model": "XMSH15HM",
            "firmware_version": "1.6.0.8",
            "battery_level": 78,
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "heart_rate", "steps", "sleep_duration", "blood_oxygen", "calories"
            ]]
        }

# 新增设备连接器

class SamsungHealthConnector(BaseDeviceConnector):
    """三星健康连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "samsung_health"
        self.base_url = "https://shealth.samsung.com/api"
        
    async def authenticate(self) -> bool:
        """三星健康认证"""
        try:
            self.is_connected = True
            logger.info("三星健康认证成功")
            return True
        except Exception as e:
            logger.error(f"三星健康认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取三星健康数据"""
        try:
            mock_data = [
                DeviceData(
                    device_id="galaxy_watch_6",
                    device_type="samsung_health",
                    device_name="Galaxy Watch 6",
                    data_type="stress_level",
                    value=42,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.94,
                    raw_data={"stress_category": "low", "measurement_method": "hrv_analysis"},
                    metric_type=ExtendedHealthMetrics.STRESS_LEVEL,
                    confidence_level=0.94,
                    data_source="samsung_health_api",
                    sync_status="synced",
                    processing_time=0.11
                ),
                DeviceData(
                    device_id="galaxy_watch_6",
                    device_type="samsung_health",
                    device_name="Galaxy Watch 6",
                    data_type="body_composition",
                    value={"body_fat": 15.2, "muscle_mass": 32.8, "water_percentage": 58.5},
                    unit="percentage",
                    timestamp=datetime.now() - timedelta(hours=2),
                    quality_score=0.87,
                    raw_data={"measurement_type": "bioelectrical_impedance"},
                    metric_type=ExtendedHealthMetrics.BODY_FAT,
                    confidence_level=0.87,
                    data_source="samsung_health_api",
                    sync_status="synced",
                    processing_time=0.20
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从三星健康获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取三星健康数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取三星设备信息"""
        return {
            "device_id": device_id,
            "device_type": "samsung_health",
            "device_name": "Galaxy Watch 6",
            "manufacturer": "Samsung",
            "model": "SM-R950F",
            "os_version": "Wear OS 4.0",
            "app_version": "Samsung Health 6.22",
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "heart_rate", "steps", "stress_level", "body_fat", "sleep_duration", "blood_oxygen"
            ]]
        }

class GarminConnector(BaseDeviceConnector):
    """佳明连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "garmin"
        self.base_url = "https://connect.garmin.com/modern/proxy"
        
    async def authenticate(self) -> bool:
        """佳明认证"""
        try:
            self.is_connected = True
            logger.info("佳明设备认证成功")
            return True
        except Exception as e:
            logger.error(f"佳明设备认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取佳明健康数据"""
        try:
            mock_data = [
                DeviceData(
                    device_id="fenix_7",
                    device_type="garmin",
                    device_name="Fenix 7",
                    data_type="recovery_score",
                    value=78,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.96,
                    raw_data={"recovery_advisor": "good", "training_readiness": "high"},
                    metric_type=ExtendedHealthMetrics.RECOVERY_SCORE,
                    confidence_level=0.96,
                    data_source="garmin_connect_api",
                    sync_status="synced",
                    processing_time=0.14
                ),
                DeviceData(
                    device_id="fenix_7",
                    device_type="garmin",
                    device_name="Fenix 7",
                    data_type="hrv",
                    value=52.3,
                    unit="ms",
                    timestamp=datetime.now() - timedelta(hours=2),
                    quality_score=0.93,
                    raw_data={"measurement_type": "RMSSD", "measurement_duration": 300},
                    metric_type=ExtendedHealthMetrics.HRV,
                    confidence_level=0.93,
                    data_source="garmin_connect_api",
                    sync_status="synced",
                    processing_time=0.16
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从佳明设备获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取佳明设备数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取佳明设备信息"""
        return {
            "device_id": device_id,
            "device_type": "garmin",
            "device_name": "Fenix 7",
            "manufacturer": "Garmin",
            "model": "010-02540-00",
            "software_version": "20.26",
            "battery_level": 92,
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "heart_rate", "hrv", "recovery_score", "stress_level", "sleep_duration", "steps"
            ]]
        }

class OuraConnector(BaseDeviceConnector):
    """Oura智能戒指连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "oura"
        self.base_url = "https://api.ouraring.com/v2"
        
    async def authenticate(self) -> bool:
        """Oura认证"""
        try:
            self.is_connected = True
            logger.info("Oura设备认证成功")
            return True
        except Exception as e:
            logger.error(f"Oura设备认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取Oura健康数据"""
        try:
            mock_data = [
                DeviceData(
                    device_id="oura_ring_gen3",
                    device_type="oura",
                    device_name="Oura Ring Gen3",
                    data_type="readiness_score",
                    value=85,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.98,
                    raw_data={"contributors": {"hrv": 85, "resting_hr": 90, "temperature": 80}},
                    metric_type=ExtendedHealthMetrics.READINESS_SCORE,
                    confidence_level=0.98,
                    data_source="oura_api_v2",
                    sync_status="synced",
                    processing_time=0.08
                ),
                DeviceData(
                    device_id="oura_ring_gen3",
                    device_type="oura",
                    device_name="Oura Ring Gen3",
                    data_type="sleep_score",
                    value=88,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=8),
                    quality_score=0.97,
                    raw_data={"sleep_efficiency": 92, "restfulness": 85, "timing": 90},
                    metric_type=ExtendedHealthMetrics.SLEEP_SCORE,
                    confidence_level=0.97,
                    data_source="oura_api_v2",
                    sync_status="synced",
                    processing_time=0.09
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从Oura设备获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取Oura设备数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取Oura设备信息"""
        return {
            "device_id": device_id,
            "device_type": "oura",
            "device_name": "Oura Ring Gen3",
            "manufacturer": "Oura",
            "model": "OURA-3.0",
            "firmware_version": "2.0.1",
            "battery_level": 65,
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "readiness_score", "sleep_score", "hrv", "body_temperature", "heart_rate"
            ]]
        }

class WHOOPConnector(BaseDeviceConnector):
    """WHOOP连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_type = "whoop"
        self.base_url = "https://api.prod.whoop.com/developer/v1"
        
    async def authenticate(self) -> bool:
        """WHOOP认证"""
        try:
            self.is_connected = True
            logger.info("WHOOP设备认证成功")
            return True
        except Exception as e:
            logger.error(f"WHOOP设备认证失败: {e}")
            return False
            
    async def get_health_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取WHOOP健康数据"""
        try:
            mock_data = [
                DeviceData(
                    device_id="whoop_4_0",
                    device_type="whoop",
                    device_name="WHOOP 4.0",
                    data_type="strain_score",
                    value=14.2,
                    unit="score",
                    timestamp=datetime.now() - timedelta(hours=1),
                    quality_score=0.96,
                    raw_data={"strain_category": "moderate", "kilojoules": 1250},
                    metric_type=ExtendedHealthMetrics.STRAIN_SCORE,
                    confidence_level=0.96,
                    data_source="whoop_api_v1",
                    sync_status="synced",
                    processing_time=0.12
                ),
                DeviceData(
                    device_id="whoop_4_0",
                    device_type="whoop",
                    device_name="WHOOP 4.0",
                    data_type="recovery_score",
                    value=72,
                    unit="percentage",
                    timestamp=datetime.now() - timedelta(hours=2),
                    quality_score=0.94,
                    raw_data={"recovery_category": "green", "hrv_rmssd": 48.5},
                    metric_type=ExtendedHealthMetrics.RECOVERY_SCORE,
                    confidence_level=0.94,
                    data_source="whoop_api_v1",
                    sync_status="synced",
                    processing_time=0.15
                )
            ]
            
            self.last_sync_time = datetime.now()
            logger.info(f"从WHOOP设备获取到 {len(mock_data)} 条数据")
            return mock_data
            
        except Exception as e:
            logger.error(f"获取WHOOP设备数据失败: {e}")
            return []
            
    async def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """获取WHOOP设备信息"""
        return {
            "device_id": device_id,
            "device_type": "whoop",
            "device_name": "WHOOP 4.0",
            "manufacturer": "WHOOP",
            "model": "WHOOP-4.0",
            "firmware_version": "4.0.12",
            "battery_level": 88,
            "supported_metrics": [metric.value for metric in ExtendedHealthMetrics if metric.value in [
                "strain_score", "recovery_score", "hrv", "heart_rate", "sleep_duration"
            ]]
        }

class DeviceConnectorManager:
    """设备连接器管理器"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseDeviceConnector] = {}
        self.supported_devices = [
            "apple_health", "fitbit", "xiaomi", "samsung_health", 
            "garmin", "oura", "whoop"
        ]
        self.sync_performance_metrics = {
            "total_devices": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "avg_sync_time": 0.0,
            "data_quality_score": 0.0,
            "supported_metrics_count": len(ExtendedHealthMetrics)
        }
        
    async def register_device(self, device_type: str, config: Dict[str, Any]) -> bool:
        """注册设备连接器"""
        try:
            connector_class = self._get_connector_class(device_type)
            if connector_class:
                connector = connector_class(config)
                if await connector.authenticate():
                    self.connectors[device_type] = connector
                    self.sync_performance_metrics["total_devices"]+=1
                    logger.info(f"设备注册成功: {device_type}")
                    return True
            else:
                logger.error(f"不支持的设备类型: {device_type}")
                
        except Exception as e:
            logger.error(f"设备注册失败: {device_type}, {str(e)}")
            
        return False
        
    def _get_connector_class(self, device_type: str):
        """获取连接器类"""
        connector_map = {
            "apple_health": AppleHealthConnector,
            "fitbit": FitbitConnector,
            "xiaomi": XiaomiConnector,
            "samsung_health": SamsungHealthConnector,
            "garmin": GarminConnector,
            "oura": OuraConnector,
            "whoop": WHOOPConnector
        }
        return connector_map.get(device_type)
        
    async def get_cross_device_data(self, user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """获取跨设备数据"""
        sync_start = datetime.now()
        all_data = []
        successful_syncs = 0
        failed_syncs = 0
        
        # 并行获取所有设备数据
        tasks = []
        for device_type, connector in self.connectors.items():
            task = asyncio.create_task(
                self._get_device_data_with_metrics(connector, user_id, start_time, end_time)
            )
            tasks.append(task)
            
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_syncs+=1
                logger.error(f"设备数据获取失败: {list(self.connectors.keys())[i]}")
            else:
                all_data.extend(result)
                successful_syncs+=1
                
        # 数据去重和质量评估
        deduplicated_data = self._deduplicate_data(all_data)
        
        # 更新性能指标
        sync_duration = (datetime.now() - sync_start).total_seconds()
        self.sync_performance_metrics.update({
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "avg_sync_time": sync_duration,
            "data_quality_score": self._calculate_data_quality(deduplicated_data)
        })
        
        logger.info(f"跨设备数据同步完成: {len(deduplicated_data)}条数据, 耗时{sync_duration:.2f}秒")
        return deduplicated_data
        
    async def _get_device_data_with_metrics(self, connector: BaseDeviceConnector, 
                                          user_id: str, start_time: datetime, end_time: datetime) -> List[DeviceData]:
        """带性能指标的设备数据获取"""
        try:
            data = await connector.get_health_data(user_id, start_time, end_time)
            return data
        except Exception as e:
            logger.error(f"设备数据获取异常: {connector.device_type}, {str(e)}")
            raise
            
    def _deduplicate_data(self, data_list: List[DeviceData]) -> List[DeviceData]:
        """数据去重"""
        seen = set()
        deduplicated = []
        
        for data in data_list:
            # 创建唯一标识符
            key = f"{data.device_type}_{data.data_type}_{data.timestamp.isoformat()}"
            if key not in seen:
                seen.add(key)
                deduplicated.append(data)
                
        return deduplicated
        
    def _calculate_data_quality(self, data_list: List[DeviceData]) -> float:
        """计算数据质量分数"""
        if not data_list:
            return 0.0
            
        total_quality = sum(data.quality_score for data in data_list)
        return total_quality / len(data_list)
        
    async def get_all_device_info(self) -> Dict[str, Dict[str, Any]]:
        """获取所有设备信息"""
        device_info = {}
        
        for device_type, connector in self.connectors.items():
            try:
                info = await connector.get_device_info(connector.config.get('device_id', 'unknown'))
                device_info[device_type] = info
            except Exception as e:
                logger.error(f"获取设备信息失败: {device_type}, {str(e)}")
                device_info[device_type] = {"error": str(e)}
                
        return device_info
        
    def get_supported_devices(self) -> List[str]:
        """获取支持的设备列表"""
        return self.supported_devices
        
    def get_connected_devices(self) -> List[str]:
        """获取已连接的设备列表"""
        return list(self.connectors.keys())
        
    def get_supported_metrics(self) -> List[str]:
        """获取支持的健康指标列表"""
        return [metric.value for metric in ExtendedHealthMetrics]
        
    async def optimize_sync_performance(self) -> Dict[str, Any]:
        """优化同步性能"""
        optimizations = []
        
        # 检查同步时间
        if self.sync_performance_metrics["avg_sync_time"] > 3.0:
            optimizations.append({
                "type": "sync_time_optimization",
                "description": "启用并行同步和数据缓存",
                "expected_improvement": "60%性能提升"
            })
            
        # 检查数据质量
        if self.sync_performance_metrics["data_quality_score"] < 0.9:
            optimizations.append({
                "type": "data_quality_optimization", 
                "description": "增强数据验证和清洗",
                "expected_improvement": "提升数据质量至95%+"
            })
            
        return {
            "current_performance": self.sync_performance_metrics,
            "optimization_suggestions": optimizations,
            "supported_devices": len(self.supported_devices),
            "supported_metrics": len(ExtendedHealthMetrics)
        }

class UnifiedDataFormatter:
    """统一数据格式化器"""
    
    @staticmethod
    def to_standard_format(device_data: List[DeviceData]) -> Dict[str, Any]:
        """转换为标准格式"""
        formatted_data = {
            "timestamp": datetime.now().isoformat(),
            "total_records": len(device_data),
            "data_sources": list(set(data.device_type for data in device_data)),
            "metrics": {},
            "quality_summary": {
                "avg_quality_score": sum(data.quality_score for data in device_data) / len(device_data) if device_data else 0,
                "avg_confidence_level": sum(data.confidence_level or 0 for data in device_data) / len(device_data) if device_data else 0,
                "total_processing_time": sum(data.processing_time or 0 for data in device_data)
            }
        }
        
        # 按指标类型分组数据
        for data in device_data:
            metric_type = data.metric_type.value if data.metric_type else data.data_type
            if metric_type not in formatted_data["metrics"]:
                formatted_data["metrics"][metric_type] = []
                
            formatted_data["metrics"][metric_type].append({
                "device": data.device_name,
                "value": data.value,
                "unit": data.unit,
                "timestamp": data.timestamp.isoformat(),
                "quality_score": data.quality_score,
                "confidence_level": data.confidence_level,
                "data_source": data.data_source
            })
            
        return formatted_data