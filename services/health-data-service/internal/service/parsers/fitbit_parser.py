#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fitbit JSON数据解析器
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Union
import logging

from .base_parser import BaseParser
from ....model.health_data import HealthDataType, MeasurementUnit


class FitbitParser(BaseParser):
    """Fitbit数据解析器"""
    
    async def parse(self, data: Union[str, Dict, bytes], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        解析Fitbit JSON数据
        
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
            if 'activities-steps' in data and ('steps' in supported_types or not supported_types):
                results.extend(self._parse_steps(data['activities-steps']))
            
            # 解析心率数据
            if 'activities-heart' in data and ('heart_rate' in supported_types or not supported_types):
                results.extend(self._parse_heart_rate(data['activities-heart']))
            
            # 解析睡眠数据
            if 'sleep' in data and ('sleep' in supported_types or not supported_types):
                results.extend(self._parse_sleep(data['sleep']))
            
            # 解析活动数据
            if 'activities' in data and ('activities' in supported_types or not supported_types):
                results.extend(self._parse_activities(data['activities']))
            
            # 解析卡路里数据
            if 'activities-calories' in data and ('calories' in supported_types or not supported_types):
                results.extend(self._parse_calories(data['activities-calories']))
            
            return results
        
        except Exception as e:
            logging.error(f"解析Fitbit数据时出错: {str(e)}")
            raise ValueError(f"无法解析Fitbit数据: {str(e)}")
    
    def _parse_steps(self, steps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析步数数据"""
        results = []
        
        for entry in steps_data:
            try:
                # 解析日期时间
                date_str = entry.get('dateTime')
                if not date_str:
                    continue
                
                # Fitbit通常提供日期而非具体时间，所以假设是当天结束
                timestamp = datetime.fromisoformat(f"{date_str}T23:59:59")
                
                # 获取步数值
                value = int(entry.get('value', 0))
                
                results.append({
                    "data_type": HealthDataType.STEPS,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.STEPS,
                    "device_id": "fitbit",
                    "source": "Fitbit",
                    "metadata": {
                        "original_type": "steps",
                        "date": date_str
                    }
                })
            except Exception as e:
                logging.warning(f"解析步数数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_heart_rate(self, heart_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析心率数据"""
        results = []
        
        for entry in heart_data:
            try:
                # 解析日期时间
                date_str = entry.get('dateTime')
                if not date_str:
                    continue
                
                # 检查是否有详细数据
                value_entry = entry.get('value')
                if not value_entry or not isinstance(value_entry, dict):
                    continue
                
                # 处理当天的平均心率
                if 'restingHeartRate' in value_entry:
                    resting_hr = int(value_entry['restingHeartRate'])
                    timestamp = datetime.fromisoformat(f"{date_str}T12:00:00")
                    
                    results.append({
                        "data_type": HealthDataType.HEART_RATE,
                        "timestamp": timestamp,
                        "value": resting_hr,
                        "unit": MeasurementUnit.BPM,
                        "device_id": "fitbit",
                        "source": "Fitbit",
                        "metadata": {
                            "original_type": "resting_heart_rate",
                            "date": date_str
                        }
                    })
                
                # 处理心率区间数据
                if 'heartRateZones' in value_entry:
                    zones = value_entry['heartRateZones']
                    for zone in zones:
                        if 'minutes' in zone and int(zone.get('minutes', 0)) > 0:
                            zone_name = zone.get('name', '')
                            max_hr = zone.get('max', 0)
                            min_hr = zone.get('min', 0)
                            avg_hr = (max_hr + min_hr) // 2
                            
                            results.append({
                                "data_type": HealthDataType.HEART_RATE,
                                "timestamp": datetime.fromisoformat(f"{date_str}T12:00:00"),
                                "value": avg_hr,
                                "unit": MeasurementUnit.BPM,
                                "device_id": "fitbit",
                                "source": "Fitbit",
                                "metadata": {
                                    "original_type": "heart_rate_zone",
                                    "zone_name": zone_name,
                                    "zone_min": min_hr,
                                    "zone_max": max_hr,
                                    "minutes": zone.get('minutes', 0),
                                    "date": date_str
                                }
                            })
                
                # 处理详细心率数据
                if 'heartRateDetails' in value_entry and 'data' in value_entry['heartRateDetails']:
                    hr_details = value_entry['heartRateDetails']['data']
                    for hr_detail in hr_details:
                        if 'time' in hr_detail and 'heartRate' in hr_detail:
                            time_str = hr_detail['time']
                            hr_value = int(hr_detail['heartRate'])
                            timestamp = datetime.fromisoformat(f"{date_str}T{time_str}")
                            
                            results.append({
                                "data_type": HealthDataType.HEART_RATE,
                                "timestamp": timestamp,
                                "value": hr_value,
                                "unit": MeasurementUnit.BPM,
                                "device_id": "fitbit",
                                "source": "Fitbit",
                                "metadata": {
                                    "original_type": "heart_rate_detail",
                                    "date": date_str,
                                    "time": time_str
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
                # 获取基本睡眠数据
                date_str = entry.get('dateOfSleep')
                start_time = entry.get('startTime')
                end_time = entry.get('endTime')
                
                if not date_str or not start_time or not end_time:
                    continue
                
                # 解析时间
                start_timestamp = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_timestamp = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                # 计算持续时间（分钟）
                duration_ms = entry.get('duration', 0)
                duration_min = duration_ms // 60000
                
                # 解析睡眠阶段
                stages = {}
                if 'levels' in entry and 'summary' in entry['levels']:
                    summary = entry['levels']['summary']
                    
                    # 映射Fitbit睡眠阶段到我们的格式
                    stage_mapping = {
                        'deep': 'deep',
                        'light': 'light',
                        'rem': 'rem',
                        'wake': 'awake',
                        'awake': 'awake'
                    }
                    
                    for stage, fitbit_stage in stage_mapping.items():
                        if fitbit_stage in summary:
                            minutes = summary[fitbit_stage].get('minutes', 0)
                            stages[stage] = minutes
                
                # 创建睡眠数据条目
                sleep_value = {
                    "duration": duration_min,
                    "stages": stages,
                    "efficiency": entry.get('efficiency', 0)
                }
                
                results.append({
                    "data_type": HealthDataType.SLEEP,
                    "timestamp": start_timestamp,
                    "value": sleep_value,
                    "unit": MeasurementUnit.MINUTES,
                    "device_id": "fitbit",
                    "source": "Fitbit",
                    "metadata": {
                        "original_type": "sleep",
                        "date": date_str,
                        "end_time": end_time,
                        "total_minutes_asleep": entry.get('minutesAsleep', 0),
                        "total_time_in_bed": entry.get('timeInBed', 0)
                    }
                })
            except Exception as e:
                logging.warning(f"解析睡眠数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_activities(self, activities_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析活动数据"""
        results = []
        
        for entry in activities_data:
            try:
                # 解析活动数据
                activity_name = entry.get('activityName', '')
                start_time = entry.get('startTime', '')
                
                if not activity_name or not start_time:
                    continue
                
                # 解析时间
                timestamp = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                
                # 活动持续时间
                duration_ms = entry.get('duration', 0)
                duration_min = duration_ms // 60000
                
                # 活动数据
                activity_value = {
                    "name": activity_name,
                    "duration": duration_min,
                    "calories": entry.get('calories', 0),
                    "steps": entry.get('steps', 0),
                    "distance": entry.get('distance', 0),
                    "active_minutes": entry.get('activeMinutes', 0)
                }
                
                results.append({
                    "data_type": HealthDataType.ACTIVITY,
                    "timestamp": timestamp,
                    "value": activity_value,
                    "unit": MeasurementUnit.MINUTES,
                    "device_id": "fitbit",
                    "source": "Fitbit",
                    "metadata": {
                        "original_type": "activity",
                        "activity_id": entry.get('activityId', 0),
                        "activity_level": entry.get('activityLevel', []),
                        "has_active_zone_minutes": entry.get('hasActiveZoneMinutes', False)
                    }
                })
            except Exception as e:
                logging.warning(f"解析活动数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_calories(self, calories_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析卡路里数据"""
        results = []
        
        for entry in calories_data:
            try:
                # 解析日期时间
                date_str = entry.get('dateTime')
                if not date_str:
                    continue
                
                # Fitbit通常提供日期而非具体时间
                timestamp = datetime.fromisoformat(f"{date_str}T23:59:59")
                
                # 获取卡路里值
                value = int(entry.get('value', 0))
                
                results.append({
                    "data_type": HealthDataType.ACTIVITY,
                    "timestamp": timestamp,
                    "value": {
                        "calories": value
                    },
                    "unit": MeasurementUnit.KCAL,
                    "device_id": "fitbit",
                    "source": "Fitbit",
                    "metadata": {
                        "original_type": "calories",
                        "date": date_str
                    }
                })
            except Exception as e:
                logging.warning(f"解析卡路里数据时出错: {str(e)}")
                continue
        
        return results 