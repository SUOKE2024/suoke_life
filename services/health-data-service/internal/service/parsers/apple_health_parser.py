#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
苹果健康数据解析器
用于解析Apple Health导出的XML数据
"""

import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid
import re

from internal.model.health_data import HealthDataType, DeviceType, MeasurementUnit

logger = logging.getLogger(__name__)


class AppleHealthParser:
    """苹果健康数据解析器"""
    
    # 数据类型映射
    TYPE_MAPPING = {
        # 步数
        "HKQuantityTypeIdentifierStepCount": HealthDataType.STEPS.value,
        # 心率
        "HKQuantityTypeIdentifierHeartRate": HealthDataType.HEART_RATE.value,
        # 血压 - 收缩压
        "HKQuantityTypeIdentifierBloodPressureSystolic": HealthDataType.BLOOD_PRESSURE.value,
        # 血压 - 舒张压
        "HKQuantityTypeIdentifierBloodPressureDiastolic": HealthDataType.BLOOD_PRESSURE.value,
        # 体温
        "HKQuantityTypeIdentifierBodyTemperature": HealthDataType.BODY_TEMPERATURE.value,
        # 睡眠分析
        "HKCategoryTypeIdentifierSleepAnalysis": HealthDataType.SLEEP.value,
        # 血氧饱和度
        "HKQuantityTypeIdentifierOxygenSaturation": HealthDataType.OXYGEN_SATURATION.value,
        # 呼吸速率
        "HKQuantityTypeIdentifierRespiratoryRate": HealthDataType.RESPIRATORY_RATE.value,
        # 体重
        "HKQuantityTypeIdentifierBodyMass": HealthDataType.BODY_MASS.value,
        # 体脂率
        "HKQuantityTypeIdentifierBodyFatPercentage": HealthDataType.BODY_FAT.value,
        # 活动能量
        "HKQuantityTypeIdentifierActiveEnergyBurned": HealthDataType.ACTIVITY.value,
        # 基础能量
        "HKQuantityTypeIdentifierBasalEnergyBurned": HealthDataType.ACTIVITY.value,
        # 水摄入量
        "HKQuantityTypeIdentifierDietaryWater": HealthDataType.WATER_INTAKE.value,
        # 营养摄入 - 蛋白质
        "HKQuantityTypeIdentifierDietaryProtein": HealthDataType.NUTRITION.value,
        # 营养摄入 - 碳水化合物
        "HKQuantityTypeIdentifierDietaryCarbohydrates": HealthDataType.NUTRITION.value,
        # 营养摄入 - 脂肪
        "HKQuantityTypeIdentifierDietaryFatTotal": HealthDataType.NUTRITION.value,
        # 营养摄入 - 能量
        "HKQuantityTypeIdentifierDietaryEnergyConsumed": HealthDataType.NUTRITION.value,
    }
    
    # 单位映射
    UNIT_MAPPING = {
        # 步数
        "count": MeasurementUnit.COUNT.value,
        # 心率
        "count/min": MeasurementUnit.BPM.value,
        # 血压
        "mmHg": MeasurementUnit.MMHG.value,
        # 体温
        "degC": MeasurementUnit.CELSIUS.value,
        "degF": MeasurementUnit.FAHRENHEIT.value,
        # 血氧
        "%": MeasurementUnit.PERCENT.value,
        # 体重
        "kg": MeasurementUnit.KG.value,
        "lb": MeasurementUnit.LB.value,
        # 时间
        "min": MeasurementUnit.MINUTES.value,
        "hour": MeasurementUnit.HOURS.value,
        # 能量
        "kcal": MeasurementUnit.KCAL.value,
        # 体积
        "mL": MeasurementUnit.ML.value,
        # 质量
        "g": MeasurementUnit.G.value,
        "mg": MeasurementUnit.MG.value,
        # 呼吸速率
        "count/min": MeasurementUnit.RPM.value,
    }
    
    def __init__(self):
        """初始化解析器"""
        pass
    
    def parse_file(self, file_path: str, user_id: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """解析Apple Health导出的XML文件
        
        Args:
            file_path: XML文件路径
            user_id: 用户ID
            
        Returns:
            Tuple: (健康数据列表, 解析统计信息)
        """
        logger.info(f"开始解析Apple Health导出文件: {file_path}")
        
        try:
            # 解析XML
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 保存解析结果
            health_data = []
            
            # 解析统计信息
            stats = {
                "total_records": 0,
                "processed_records": 0,
                "skipped_records": 0,
                "data_types": {},
                "time_range": {
                    "start": None,
                    "end": None
                }
            }
            
            # 解析记录
            record_elements = root.findall('.//Record')
            stats["total_records"] = len(record_elements)
            
            # 血压数据临时存储，需要配对收缩压和舒张压
            blood_pressure_data = {}
            
            for record in record_elements:
                try:
                    # 获取记录类型
                    record_type = record.get('type')
                    
                    # 检查是否是支持的数据类型
                    if record_type not in self.TYPE_MAPPING:
                        stats["skipped_records"] += 1
                        continue
                    
                    # 获取数据类型
                    data_type = self.TYPE_MAPPING[record_type]
                    
                    # 特殊处理血压数据（需要将收缩压和舒张压配对）
                    if data_type == HealthDataType.BLOOD_PRESSURE.value:
                        bp_data = self._process_blood_pressure(record, blood_pressure_data, user_id)
                        if bp_data:
                            health_data.append(bp_data)
                            stats["processed_records"] += 1
                            if data_type not in stats["data_types"]:
                                stats["data_types"][data_type] = 0
                            stats["data_types"][data_type] += 1
                        continue
                    
                    # 解析其他数据
                    data = self._parse_record(record, user_id)
                    if data:
                        health_data.append(data)
                        stats["processed_records"] += 1
                        
                        # 更新统计信息
                        if data_type not in stats["data_types"]:
                            stats["data_types"][data_type] = 0
                        stats["data_types"][data_type] += 1
                        
                        # 更新时间范围
                        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
                        if stats["time_range"]["start"] is None or timestamp < stats["time_range"]["start"]:
                            stats["time_range"]["start"] = timestamp
                        if stats["time_range"]["end"] is None or timestamp > stats["time_range"]["end"]:
                            stats["time_range"]["end"] = timestamp
                    else:
                        stats["skipped_records"] += 1
                
                except Exception as e:
                    logger.warning(f"解析记录时出错: {e}")
                    stats["skipped_records"] += 1
            
            # 格式化时间范围
            if stats["time_range"]["start"]:
                stats["time_range"]["start"] = stats["time_range"]["start"].isoformat() + "Z"
            if stats["time_range"]["end"]:
                stats["time_range"]["end"] = stats["time_range"]["end"].isoformat() + "Z"
            
            logger.info(f"完成解析Apple Health数据，共处理 {stats['processed_records']} 条记录，跳过 {stats['skipped_records']} 条记录")
            return health_data, stats
        
        except Exception as e:
            logger.error(f"解析Apple Health数据失败: {e}")
            return [], {
                "error": str(e),
                "total_records": 0,
                "processed_records": 0,
                "skipped_records": 0,
                "data_types": {},
                "time_range": {
                    "start": None,
                    "end": None
                }
            }
    
    def _parse_record(self, record: ET.Element, user_id: str) -> Optional[Dict[str, Any]]:
        """解析单条记录
        
        Args:
            record: XML记录元素
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 解析后的健康数据，如果无法解析则返回None
        """
        try:
            # 获取记录类型
            record_type = record.get('type')
            
            # 检查是否是支持的数据类型
            if record_type not in self.TYPE_MAPPING:
                return None
            
            # 获取数据类型
            data_type = self.TYPE_MAPPING[record_type]
            
            # 获取基本数据
            value = record.get('value')
            unit = record.get('unit', '')
            start_date = record.get('startDate')
            end_date = record.get('endDate')
            source_name = record.get('sourceName', 'Apple Health')
            device = record.get('device', '')
            
            # 获取设备ID
            device_id = None
            if device:
                match = re.search(r'name:([^,]+)', device)
                if match:
                    device_id = match.group(1).strip()
            
            # 转换单位
            if unit in self.UNIT_MAPPING:
                converted_unit = self.UNIT_MAPPING[unit]
            else:
                converted_unit = MeasurementUnit.CUSTOM.value
            
            # 特殊处理睡眠数据
            if data_type == HealthDataType.SLEEP.value:
                return self._process_sleep_data(record, user_id)
            
            # 转换值到适当的类型
            try:
                numeric_value = float(value)
                # 处理某些整数值
                if data_type == HealthDataType.STEPS.value:
                    numeric_value = int(numeric_value)
            except ValueError:
                # 如果不能转为数值，保留为字符串
                numeric_value = value
            
            # 构建健康数据
            health_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "data_type": data_type,
                "timestamp": self._format_datetime(start_date),
                "device_type": DeviceType.APPLE_HEALTH.value,
                "device_id": device_id,
                "value": numeric_value,
                "unit": converted_unit,
                "source": source_name,
                "metadata": {
                    "record_type": record_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "original_unit": unit,
                    "device": device
                }
            }
            
            return health_data
        
        except Exception as e:
            logger.warning(f"解析记录失败: {e}")
            return None
    
    def _process_blood_pressure(self, 
                               record: ET.Element, 
                               blood_pressure_data: Dict[str, Dict], 
                               user_id: str) -> Optional[Dict[str, Any]]:
        """处理血压数据，将收缩压和舒张压配对
        
        Args:
            record: 血压记录
            blood_pressure_data: 血压数据临时存储
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 配对后的血压数据，如果还没有配对完成则返回None
        """
        try:
            record_type = record.get('type')
            start_date = record.get('startDate')
            value = float(record.get('value', '0'))
            source_name = record.get('sourceName', 'Apple Health')
            
            # 创建唯一键（使用时间和来源组合）
            key = f"{start_date}_{source_name}"
            
            # 如果是收缩压
            if record_type == "HKQuantityTypeIdentifierBloodPressureSystolic":
                if key not in blood_pressure_data:
                    blood_pressure_data[key] = {}
                blood_pressure_data[key]["systolic"] = value
            
            # 如果是舒张压
            elif record_type == "HKQuantityTypeIdentifierBloodPressureDiastolic":
                if key not in blood_pressure_data:
                    blood_pressure_data[key] = {}
                blood_pressure_data[key]["diastolic"] = value
            
            # 检查是否已经有配对的数据
            if key in blood_pressure_data and "systolic" in blood_pressure_data[key] and "diastolic" in blood_pressure_data[key]:
                # 提取完整的血压数据
                bp_data = blood_pressure_data[key]
                
                # 删除已处理的数据
                del blood_pressure_data[key]
                
                # 构建健康数据
                health_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "data_type": HealthDataType.BLOOD_PRESSURE.value,
                    "timestamp": self._format_datetime(start_date),
                    "device_type": DeviceType.APPLE_HEALTH.value,
                    "value": {
                        "systolic": bp_data["systolic"],
                        "diastolic": bp_data["diastolic"]
                    },
                    "unit": MeasurementUnit.MMHG.value,
                    "source": source_name,
                    "metadata": {
                        "record_type": "BloodPressure",
                        "start_date": start_date,
                        "original_unit": "mmHg"
                    }
                }
                
                return health_data
            
            # 如果还没有配对完成，返回None
            return None
        
        except Exception as e:
            logger.warning(f"处理血压数据失败: {e}")
            return None
    
    def _process_sleep_data(self, record: ET.Element, user_id: str) -> Optional[Dict[str, Any]]:
        """处理睡眠数据
        
        Args:
            record: 睡眠记录
            user_id: 用户ID
            
        Returns:
            Optional[Dict]: 处理后的睡眠数据
        """
        try:
            start_date = record.get('startDate')
            end_date = record.get('endDate')
            value = record.get('value')
            source_name = record.get('sourceName', 'Apple Health')
            
            # 计算睡眠时长（小时）
            start_time = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S %z")
            end_time = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S %z")
            duration_seconds = (end_time - start_time).total_seconds()
            duration_hours = duration_seconds / 3600
            
            # 睡眠状态映射
            sleep_state = "unknown"
            if value == "HKCategoryValueSleepAnalysisInBed":
                sleep_state = "in_bed"
            elif value == "HKCategoryValueSleepAnalysisAsleep":
                sleep_state = "asleep"
            elif value == "HKCategoryValueSleepAnalysisAwake":
                sleep_state = "awake"
            
            # 构建健康数据
            health_data = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "data_type": HealthDataType.SLEEP.value,
                "timestamp": self._format_datetime(start_date),
                "device_type": DeviceType.APPLE_HEALTH.value,
                "value": {
                    "duration_hours": round(duration_hours, 2),
                    "sleep_state": sleep_state,
                    "start_time": self._format_datetime(start_date),
                    "end_time": self._format_datetime(end_date)
                },
                "unit": MeasurementUnit.HOURS.value,
                "source": source_name,
                "metadata": {
                    "record_type": "SleepAnalysis",
                    "start_date": start_date,
                    "end_date": end_date,
                    "original_value": value,
                    "duration_seconds": duration_seconds
                }
            }
            
            return health_data
        
        except Exception as e:
            logger.warning(f"处理睡眠数据失败: {e}")
            return None
    
    def _format_datetime(self, datetime_str: str) -> str:
        """格式化日期时间字符串为ISO 8601格式
        
        Args:
            datetime_str: 日期时间字符串
            
        Returns:
            str: ISO 8601格式的日期时间字符串
        """
        try:
            # 解析Apple Health格式的日期时间
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S %z")
            # 转换为ISO 8601格式
            return dt.isoformat().replace("+00:00", "Z")
        except Exception:
            # 如果解析失败，尝试其他格式
            try:
                dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                return dt.isoformat() + "Z"
            except Exception:
                # 返回原始字符串
                return datetime_str 