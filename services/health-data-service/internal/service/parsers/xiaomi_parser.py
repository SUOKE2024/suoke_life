#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小米健康数据解析器 (支持小米手环/手表等设备)
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Union
import logging

from .base_parser import BaseParser
from ....model.health_data import HealthDataType, MeasurementUnit


class XiaomiParser(BaseParser):
    """小米健康数据解析器"""
    
    async def parse(self, data: Union[str, Dict, bytes], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        解析小米健康JSON数据
        
        Args:
            data: JSON数据
            config: 解析配置
            
        Returns:
            解析后的健康数据列表
        """
        try:
            # 确保数据是字典
            if isinstance(data, str):
                data = json.loads(data)
            elif isinstance(data, bytes):
                data = json.loads(data.decode('utf-8'))
            
            # 获取支持的数据类型
            supported_types = []
            if config and 'data_types' in config:
                supported_types = config['data_types']
            
            # 记录结果
            results = []
            
            # 解析步数数据
            if 'steps' in data and ('steps' in supported_types or not supported_types):
                results.extend(self._parse_steps(data['steps']))
            
            # 解析心率数据
            if 'heart_rate' in data and ('heart_rate' in supported_types or not supported_types):
                results.extend(self._parse_heart_rate(data['heart_rate']))
            
            # 解析睡眠数据
            if 'sleep' in data and ('sleep' in supported_types or not supported_types):
                results.extend(self._parse_sleep(data['sleep']))
            
            # 解析活动数据
            if 'activity' in data and ('activity' in supported_types or not supported_types):
                results.extend(self._parse_activity(data['activity']))
            
            # 解析体重数据
            if 'weight' in data and ('body_mass' in supported_types or not supported_types):
                results.extend(self._parse_weight(data['weight']))
            
            # 解析血氧数据
            if 'spo2' in data and ('oxygen_saturation' in supported_types or not supported_types):
                results.extend(self._parse_spo2(data['spo2']))
                
            return results
        
        except Exception as e:
            logging.error(f"解析小米健康数据时出错: {str(e)}")
            raise ValueError(f"无法解析小米健康数据: {str(e)}")
    
    def _parse_steps(self, steps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析步数数据"""
        results = []
        
        for entry in steps_data:
            try:
                # 获取时间戳
                if 'timestamp' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['timestamp'], int):
                        timestamp = datetime.fromtimestamp(entry['timestamp'] / 1000)
                    # ISO日期字符串
                    else:
                        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                elif 'date' in entry:
                    # 日期字符串，假设是当天结束
                    date_str = entry['date']
                    timestamp = datetime.fromisoformat(f"{date_str}T23:59:59")
                else:
                    continue
                
                # 获取步数值
                value = int(entry.get('value', entry.get('steps', 0)))
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                # 创建结果
                results.append({
                    "data_type": HealthDataType.STEPS,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.STEPS,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "steps",
                        "distance": entry.get('distance', 0),
                        "calories": entry.get('calories', 0)
                    }
                })
            except Exception as e:
                logging.warning(f"解析步数数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_heart_rate(self, heart_rate_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析心率数据"""
        results = []
        
        for entry in heart_rate_data:
            try:
                # 获取时间戳
                if 'timestamp' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['timestamp'], int):
                        timestamp = datetime.fromtimestamp(entry['timestamp'] / 1000)
                    # ISO日期字符串
                    else:
                        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                elif 'time' in entry:
                    timestamp = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                elif 'date' in entry and 'time' in entry:
                    timestamp = datetime.fromisoformat(f"{entry['date']}T{entry['time']}")
                else:
                    continue
                
                # 获取心率值
                value = int(entry.get('value', entry.get('heart_rate', 0)))
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                # 创建结果
                results.append({
                    "data_type": HealthDataType.HEART_RATE,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.BPM,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "heart_rate",
                        "measurement_type": entry.get('measurement_type', 'manual' if entry.get('is_manual', False) else 'automatic')
                    }
                })
            except Exception as e:
                logging.warning(f"解析心率数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_sleep(self, sleep_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析睡眠数据"""
        results = []
        
        for entry in sleep_data:
            try:
                # 获取基础睡眠数据
                start_time = None
                end_time = None
                date_str = None
                
                # 解析时间戳
                if 'start_time' in entry and 'end_time' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['start_time'], int):
                        start_time = datetime.fromtimestamp(entry['start_time'] / 1000)
                        end_time = datetime.fromtimestamp(entry['end_time'] / 1000)
                    # ISO日期字符串
                    else:
                        start_time = datetime.fromisoformat(entry['start_time'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(entry['end_time'].replace('Z', '+00:00'))
                    
                    date_str = start_time.strftime('%Y-%m-%d')
                elif 'date' in entry:
                    date_str = entry['date']
                    
                    # 如果有详细时间
                    if 'start' in entry and 'end' in entry:
                        start_time = datetime.fromisoformat(f"{date_str}T{entry['start']}")
                        
                        # 处理跨天情况
                        end_str = entry['end']
                        if entry['start'] > entry['end']:  # 例如 22:30 > 06:30
                            next_day = (datetime.fromisoformat(date_str) + timedelta(days=1)).strftime('%Y-%m-%d')
                            end_time = datetime.fromisoformat(f"{next_day}T{end_str}")
                        else:
                            end_time = datetime.fromisoformat(f"{date_str}T{end_str}")
                else:
                    continue
                
                # 如果没有获取到时间，跳过
                if not start_time or not end_time:
                    continue
                
                # 计算持续时间（分钟）
                if 'duration' in entry:
                    duration_min = int(entry['duration'])
                else:
                    duration_sec = (end_time - start_time).total_seconds()
                    duration_min = int(duration_sec / 60)
                
                # 解析睡眠阶段
                stages = {}
                
                # 小米健康通常提供deep_sleep、light_sleep和awake的时间
                if 'deep_sleep' in entry:
                    stages['deep'] = int(entry['deep_sleep'])
                if 'light_sleep' in entry:
                    stages['light'] = int(entry['light_sleep'])
                if 'awake' in entry:
                    stages['awake'] = int(entry['awake'])
                if 'rem' in entry:
                    stages['rem'] = int(entry['rem'])
                
                # 创建睡眠数据条目
                sleep_value = {
                    "duration": duration_min,
                    "stages": stages,
                    "efficiency": entry.get('efficiency', 0)
                }
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                results.append({
                    "data_type": HealthDataType.SLEEP,
                    "timestamp": start_time,
                    "value": sleep_value,
                    "unit": MeasurementUnit.MINUTES,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "sleep",
                        "date": date_str,
                        "end_time": end_time.isoformat(),
                        "sleep_score": entry.get('score', 0),
                        "deep_sleep_percentage": entry.get('deep_sleep_percentage', 0)
                    }
                })
            except Exception as e:
                logging.warning(f"解析睡眠数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_activity(self, activity_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析活动数据"""
        results = []
        
        for entry in activity_data:
            try:
                # 获取时间戳
                if 'timestamp' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['timestamp'], int):
                        timestamp = datetime.fromtimestamp(entry['timestamp'] / 1000)
                    # ISO日期字符串
                    else:
                        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                elif 'start_time' in entry:
                    if isinstance(entry['start_time'], int):
                        timestamp = datetime.fromtimestamp(entry['start_time'] / 1000)
                    else:
                        timestamp = datetime.fromisoformat(entry['start_time'].replace('Z', '+00:00'))
                elif 'date' in entry:
                    date_str = entry['date']
                    if 'time' in entry:
                        timestamp = datetime.fromisoformat(f"{date_str}T{entry['time']}")
                    else:
                        timestamp = datetime.fromisoformat(f"{date_str}T00:00:00")
                else:
                    continue
                
                # 获取活动类型
                activity_type = entry.get('type', entry.get('activity_type', 'unknown'))
                
                # 活动持续时间
                if 'duration' in entry:
                    duration_min = int(entry['duration'])
                elif 'duration_seconds' in entry:
                    duration_min = int(entry['duration_seconds'] / 60)
                else:
                    duration_min = 0
                
                # 活动数据
                activity_value = {
                    "type": activity_type,
                    "duration": duration_min,
                    "calories": entry.get('calories', 0),
                    "steps": entry.get('steps', 0),
                    "distance": entry.get('distance', 0)
                }
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                results.append({
                    "data_type": HealthDataType.ACTIVITY,
                    "timestamp": timestamp,
                    "value": activity_value,
                    "unit": MeasurementUnit.MINUTES,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "activity",
                        "activity_id": entry.get('id', ''),
                        "avg_heart_rate": entry.get('avg_heart_rate', 0),
                        "max_heart_rate": entry.get('max_heart_rate', 0)
                    }
                })
            except Exception as e:
                logging.warning(f"解析活动数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_weight(self, weight_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析体重数据"""
        results = []
        
        for entry in weight_data:
            try:
                # 获取时间戳
                if 'timestamp' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['timestamp'], int):
                        timestamp = datetime.fromtimestamp(entry['timestamp'] / 1000)
                    # ISO日期字符串
                    else:
                        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                elif 'time' in entry:
                    timestamp = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                elif 'date' in entry and 'time' in entry:
                    timestamp = datetime.fromisoformat(f"{entry['date']}T{entry['time']}")
                elif 'date' in entry:
                    date_str = entry['date']
                    timestamp = datetime.fromisoformat(f"{date_str}T12:00:00")
                else:
                    continue
                
                # 获取体重值（千克）
                value = float(entry.get('value', entry.get('weight', 0)))
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi_scale')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                results.append({
                    "data_type": HealthDataType.BODY_MASS,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.KG,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "weight",
                        "bmi": entry.get('bmi', 0),
                        "body_fat": entry.get('body_fat', 0),
                        "muscle_mass": entry.get('muscle_mass', 0),
                        "is_manual": entry.get('is_manual', False)
                    }
                })
                
                # 如果有体脂数据，单独保存
                if 'body_fat' in entry and entry['body_fat'] > 0:
                    results.append({
                        "data_type": HealthDataType.BODY_FAT,
                        "timestamp": timestamp,
                        "value": float(entry['body_fat']),
                        "unit": MeasurementUnit.PERCENT,
                        "device_id": device_id,
                        "source": source,
                        "metadata": {
                            "original_type": "body_fat",
                            "weight": value,
                            "bmi": entry.get('bmi', 0),
                            "is_manual": entry.get('is_manual', False)
                        }
                    })
            except Exception as e:
                logging.warning(f"解析体重数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_spo2(self, spo2_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析血氧数据"""
        results = []
        
        for entry in spo2_data:
            try:
                # 获取时间戳
                if 'timestamp' in entry:
                    # Unix时间戳（毫秒）
                    if isinstance(entry['timestamp'], int):
                        timestamp = datetime.fromtimestamp(entry['timestamp'] / 1000)
                    # ISO日期字符串
                    else:
                        timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                elif 'time' in entry:
                    timestamp = datetime.fromisoformat(entry['time'].replace('Z', '+00:00'))
                elif 'date' in entry and 'time' in entry:
                    timestamp = datetime.fromisoformat(f"{entry['date']}T{entry['time']}")
                else:
                    continue
                
                # 获取血氧值（百分比）
                value = float(entry.get('value', entry.get('spo2', 0)))
                
                # 获取设备ID
                device_id = entry.get('device_id', 'xiaomi')
                
                # 源数据
                source = entry.get('source', 'Xiaomi Health')
                
                results.append({
                    "data_type": HealthDataType.OXYGEN_SATURATION,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.PERCENT,
                    "device_id": device_id,
                    "source": source,
                    "metadata": {
                        "original_type": "spo2",
                        "measurement_type": entry.get('measurement_type', 'manual' if entry.get('is_manual', False) else 'automatic')
                    }
                })
            except Exception as e:
                logging.warning(f"解析血氧数据时出错: {str(e)}")
                continue
        
        return results 