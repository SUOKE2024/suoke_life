#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Garmin FIT文件解析器
"""

import io
from datetime import datetime
from typing import Dict, List, Any, Union
import logging

from .base_parser import BaseParser
from ....model.health_data import HealthDataType, MeasurementUnit

# 使用fitparse库解析FIT文件
try:
    import fitparse
except ImportError:
    logging.warning("fitparse库未安装，无法解析Garmin FIT文件")


class GarminParser(BaseParser):
    """Garmin数据解析器"""
    
    async def parse(self, data: Union[str, bytes], config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        解析Garmin FIT数据
        
        Args:
            data: FIT二进制数据
            config: 解析配置
            
        Returns:
            解析后的健康数据列表
        """
        try:
            # 确保数据是二进制
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # 检查fitparse是否可用
            if 'fitparse' not in globals():
                raise ImportError("fitparse库未安装，请先安装: pip install fitparse")
            
            # 获取支持的数据类型
            supported_types = []
            if config and 'data_types' in config:
                supported_types = config['data_types']
            
            # 解析FIT文件
            fit_file = fitparse.FitFile(io.BytesIO(data))
            
            # 初始化结果
            results = []
            
            # 解析各种数据记录
            activity_data = self._extract_activity_data(fit_file)
            
            # 解析步数数据
            if 'steps' in activity_data and ('steps' in supported_types or not supported_types):
                results.extend(self._parse_steps(activity_data['steps']))
            
            # 解析心率数据
            if 'heart_rate' in activity_data and ('heart_rate' in supported_types or not supported_types):
                results.extend(self._parse_heart_rate(activity_data['heart_rate']))
            
            # 解析睡眠数据
            if 'sleep' in activity_data and ('sleep' in supported_types or not supported_types):
                results.extend(self._parse_sleep(activity_data['sleep']))
            
            # 解析活动数据
            if 'activity' in activity_data and ('activity' in supported_types or not supported_types):
                results.extend(self._parse_activity(activity_data['activity']))
            
            # 解析压力数据
            if 'stress' in activity_data and ('stress' in supported_types or not supported_types):
                results.extend(self._parse_stress(activity_data['stress']))
            
            # 解析体能电量数据
            if 'body_battery' in activity_data and ('body_battery' in supported_types or not supported_types):
                results.extend(self._parse_body_battery(activity_data['body_battery']))
            
            # 解析呼吸率数据
            if 'respiration' in activity_data and ('respiration' in supported_types or not supported_types):
                results.extend(self._parse_respiration(activity_data['respiration']))
            
            return results
        
        except ImportError as e:
            logging.error(f"未安装必要的库: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"解析Garmin数据时出错: {str(e)}")
            raise ValueError(f"无法解析Garmin数据: {str(e)}")
    
    def _extract_activity_data(self, fit_file) -> Dict[str, List[Dict[str, Any]]]:
        """
        从FIT文件中提取各类活动数据
        
        Args:
            fit_file: FIT文件对象
            
        Returns:
            分类整理的活动数据
        """
        # 初始化结果数据结构
        activity_data = {
            'steps': [],
            'heart_rate': [],
            'sleep': [],
            'activity': [],
            'stress': [],
            'body_battery': [],
            'respiration': []
        }
        
        # 处理文件中的消息
        for message in fit_file.get_messages():
            # 获取消息类型
            message_type = message.name
            
            # 提取记录字段
            fields = {field.name: field.value for field in message.fields}
            
            # 根据消息类型分类处理
            if message_type == 'record':
                # 处理活动记录
                if 'timestamp' in fields:
                    # 心率数据
                    if 'heart_rate' in fields and fields['heart_rate'] is not None:
                        activity_data['heart_rate'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['heart_rate'],
                            'metadata': fields
                        })
                    
                    # 步数数据（累计步数）
                    if 'steps' in fields and fields['steps'] is not None:
                        activity_data['steps'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['steps'],
                            'metadata': fields
                        })
                    
                    # 活动数据
                    activity_data['activity'].append({
                        'timestamp': fields['timestamp'],
                        'type': fields.get('activity_type', 'unknown'),
                        'metadata': fields
                    })
            
            elif message_type == 'monitoring':
                # 处理监测数据
                if 'timestamp' in fields:
                    # 心率数据
                    if 'heart_rate' in fields and fields['heart_rate'] is not None:
                        activity_data['heart_rate'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['heart_rate'],
                            'metadata': fields
                        })
                    
                    # 步数数据
                    if 'steps' in fields and fields['steps'] is not None:
                        activity_data['steps'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['steps'],
                            'metadata': fields
                        })
                    
                    # 压力数据
                    if 'stress_level' in fields and fields['stress_level'] is not None:
                        activity_data['stress'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['stress_level'],
                            'metadata': fields
                        })
                    
                    # 体能电量数据
                    if 'body_battery' in fields and fields['body_battery'] is not None:
                        activity_data['body_battery'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['body_battery'],
                            'metadata': fields
                        })
                    
                    # 呼吸率数据
                    if 'respiration_rate' in fields and fields['respiration_rate'] is not None:
                        activity_data['respiration'].append({
                            'timestamp': fields['timestamp'],
                            'value': fields['respiration_rate'],
                            'metadata': fields
                        })
            
            elif message_type == 'sleep_level':
                # 处理睡眠数据
                if 'timestamp' in fields and 'sleep_level' in fields:
                    activity_data['sleep'].append({
                        'timestamp': fields['timestamp'],
                        'sleep_level': fields['sleep_level'],
                        'metadata': fields
                    })
            
            elif message_type == 'event':
                # 处理事件数据（通常包含活动开始/结束等信息）
                if 'event' in fields and 'event_type' in fields:
                    if fields['event'] == 'timer' and fields['event_type'] == 'start':
                        # 活动开始
                        pass
                    elif fields['event'] == 'timer' and fields['event_type'] == 'stop':
                        # 活动结束
                        pass
        
        return activity_data
    
    def _parse_steps(self, steps_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析步数数据"""
        results = []
        
        current_day = None
        daily_steps = 0
        
        for entry in sorted(steps_data, key=lambda x: x['timestamp']):
            try:
                timestamp = entry['timestamp']
                value = entry['value']
                
                # 检查是否是新的一天
                day = timestamp.date()
                
                if current_day is None:
                    current_day = day
                    daily_steps = value
                elif day != current_day:
                    # 保存前一天的数据
                    results.append({
                        "data_type": HealthDataType.STEPS,
                        "timestamp": datetime.combine(current_day, datetime.max.time().replace(microsecond=0)),
                        "value": daily_steps,
                        "unit": MeasurementUnit.STEPS,
                        "device_id": "garmin",
                        "source": "Garmin Connect",
                        "metadata": {
                            "original_type": "steps",
                            "date": current_day.isoformat()
                        }
                    })
                    
                    # 重置为新的一天
                    current_day = day
                    daily_steps = value
                else:
                    # 更新当天的步数
                    daily_steps = max(daily_steps, value)  # 取最大值，因为Garmin通常是累计步数
            
            except Exception as e:
                logging.warning(f"解析步数数据时出错: {str(e)}")
                continue
        
        # 添加最后一天的数据
        if current_day is not None:
            results.append({
                "data_type": HealthDataType.STEPS,
                "timestamp": datetime.combine(current_day, datetime.max.time().replace(microsecond=0)),
                "value": daily_steps,
                "unit": MeasurementUnit.STEPS,
                "device_id": "garmin",
                "source": "Garmin Connect",
                "metadata": {
                    "original_type": "steps",
                    "date": current_day.isoformat()
                }
            })
        
        return results
    
    def _parse_heart_rate(self, heart_rate_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析心率数据"""
        results = []
        
        # 按时间排序
        sorted_data = sorted(heart_rate_data, key=lambda x: x['timestamp'])
        
        # 对心率数据进行采样，避免数据过多
        sampled_data = self._sample_data(sorted_data, interval_minutes=5)
        
        for entry in sampled_data:
            try:
                timestamp = entry['timestamp']
                value = entry['value']
                
                results.append({
                    "data_type": HealthDataType.HEART_RATE,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.BPM,
                    "device_id": "garmin",
                    "source": "Garmin Connect",
                    "metadata": {
                        "original_type": "heart_rate",
                        "date": timestamp.date().isoformat(),
                        "time": timestamp.time().isoformat()
                    }
                })
            except Exception as e:
                logging.warning(f"解析心率数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_sleep(self, sleep_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析睡眠数据"""
        # Garmin的睡眠数据通常需要合并处理
        if not sleep_data:
            return []
        
        try:
            # 按时间排序
            sorted_data = sorted(sleep_data, key=lambda x: x['timestamp'])
            
            # 获取睡眠开始和结束时间
            start_time = sorted_data[0]['timestamp']
            end_time = sorted_data[-1]['timestamp']
            
            # 计算睡眠阶段时间
            stages = {'deep': 0, 'light': 0, 'rem': 0, 'awake': 0}
            
            current_stage = None
            stage_start_time = None
            
            # Garmin睡眠级别映射
            sleep_level_map = {
                0: 'awake',    # 清醒
                1: 'light',    # 轻度睡眠
                2: 'deep',     # 深度睡眠
                3: 'rem'       # REM睡眠
            }
            
            for i, entry in enumerate(sorted_data):
                level = entry.get('sleep_level')
                timestamp = entry['timestamp']
                
                # 映射睡眠级别
                stage = sleep_level_map.get(level, 'unknown')
                
                if stage == 'unknown':
                    continue
                
                # 处理第一个记录
                if current_stage is None:
                    current_stage = stage
                    stage_start_time = timestamp
                    continue
                
                # 当阶段变化或达到最后一个记录时计算持续时间
                if stage != current_stage or i == len(sorted_data) - 1:
                    # 计算当前阶段持续时间（分钟）
                    if i == len(sorted_data) - 1:
                        duration = (timestamp - stage_start_time).total_seconds() / 60
                    else:
                        duration = (timestamp - stage_start_time).total_seconds() / 60
                    
                    # 累加到相应阶段
                    if current_stage in stages:
                        stages[current_stage] += duration
                    
                    # 更新当前阶段
                    current_stage = stage
                    stage_start_time = timestamp
            
            # 计算总睡眠时间
            total_sleep_min = sum(stages.values())
            
            # 创建睡眠数据对象
            sleep_value = {
                "duration": total_sleep_min,
                "stages": stages,
                "efficiency": 0  # Garmin通常不直接提供睡眠效率
            }
            
            # 计算睡眠效率（深睡+REM占比）
            if total_sleep_min > 0:
                sleep_value["efficiency"] = int(((stages['deep'] + stages['rem']) / total_sleep_min) * 100)
            
            return [{
                "data_type": HealthDataType.SLEEP,
                "timestamp": start_time,
                "value": sleep_value,
                "unit": MeasurementUnit.MINUTES,
                "device_id": "garmin",
                "source": "Garmin Connect",
                "metadata": {
                    "original_type": "sleep",
                    "date": start_time.date().isoformat(),
                    "end_time": end_time.isoformat(),
                    "total_sleep_time": total_sleep_min
                }
            }]
            
        except Exception as e:
            logging.warning(f"解析睡眠数据时出错: {str(e)}")
            return []
    
    def _parse_activity(self, activity_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析活动数据"""
        results = []
        
        # 需要找出活动的开始和结束点
        activity_blocks = self._identify_activity_blocks(activity_data)
        
        for block in activity_blocks:
            try:
                start_time = block['start_time']
                end_time = block['end_time']
                activity_type = block['type']
                
                # 计算持续时间（分钟）
                duration_min = (end_time - start_time).total_seconds() / 60
                
                # 统计数据
                stats = block['stats']
                
                # 创建活动数据对象
                activity_value = {
                    "type": activity_type,
                    "duration": duration_min,
                    "calories": stats.get('calories', 0),
                    "steps": stats.get('steps', 0),
                    "distance": stats.get('distance', 0),
                    "avg_heart_rate": stats.get('avg_heart_rate', 0)
                }
                
                results.append({
                    "data_type": HealthDataType.ACTIVITY,
                    "timestamp": start_time,
                    "value": activity_value,
                    "unit": MeasurementUnit.MINUTES,
                    "device_id": "garmin",
                    "source": "Garmin Connect",
                    "metadata": {
                        "original_type": "activity",
                        "end_time": end_time.isoformat(),
                        "max_heart_rate": stats.get('max_heart_rate', 0),
                        "elevation_gain": stats.get('elevation_gain', 0)
                    }
                })
                
            except Exception as e:
                logging.warning(f"解析活动数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_stress(self, stress_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析压力数据"""
        results = []
        
        # 按时间排序
        sorted_data = sorted(stress_data, key=lambda x: x['timestamp'])
        
        # 对数据进行采样，避免数据过多
        sampled_data = self._sample_data(sorted_data, interval_minutes=30)
        
        for entry in sampled_data:
            try:
                timestamp = entry['timestamp']
                value = entry['value']
                
                # Garmin压力级别通常为0-100，值越高表示压力越大
                results.append({
                    "data_type": HealthDataType.CUSTOM,
                    "timestamp": timestamp,
                    "value": {
                        "stress_level": value
                    },
                    "unit": MeasurementUnit.CUSTOM,
                    "device_id": "garmin",
                    "source": "Garmin Connect",
                    "metadata": {
                        "original_type": "stress",
                        "date": timestamp.date().isoformat(),
                        "time": timestamp.time().isoformat()
                    }
                })
            except Exception as e:
                logging.warning(f"解析压力数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_body_battery(self, body_battery_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析体能电量数据"""
        results = []
        
        # 按时间排序
        sorted_data = sorted(body_battery_data, key=lambda x: x['timestamp'])
        
        # 对数据进行采样，避免数据过多
        sampled_data = self._sample_data(sorted_data, interval_minutes=60)
        
        for entry in sampled_data:
            try:
                timestamp = entry['timestamp']
                value = entry['value']
                
                # Garmin体能电量通常为0-100，值越高表示能量越充足
                results.append({
                    "data_type": HealthDataType.CUSTOM,
                    "timestamp": timestamp,
                    "value": {
                        "body_battery": value
                    },
                    "unit": MeasurementUnit.CUSTOM,
                    "device_id": "garmin",
                    "source": "Garmin Connect",
                    "metadata": {
                        "original_type": "body_battery",
                        "date": timestamp.date().isoformat(),
                        "time": timestamp.time().isoformat()
                    }
                })
            except Exception as e:
                logging.warning(f"解析体能电量数据时出错: {str(e)}")
                continue
        
        return results
    
    def _parse_respiration(self, respiration_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """解析呼吸率数据"""
        results = []
        
        # 按时间排序
        sorted_data = sorted(respiration_data, key=lambda x: x['timestamp'])
        
        # 对数据进行采样，避免数据过多
        sampled_data = self._sample_data(sorted_data, interval_minutes=60)
        
        for entry in sampled_data:
            try:
                timestamp = entry['timestamp']
                value = entry['value']
                
                results.append({
                    "data_type": HealthDataType.RESPIRATORY_RATE,
                    "timestamp": timestamp,
                    "value": value,
                    "unit": MeasurementUnit.RPM,
                    "device_id": "garmin",
                    "source": "Garmin Connect",
                    "metadata": {
                        "original_type": "respiration",
                        "date": timestamp.date().isoformat(),
                        "time": timestamp.time().isoformat()
                    }
                })
            except Exception as e:
                logging.warning(f"解析呼吸率数据时出错: {str(e)}")
                continue
        
        return results
    
    def _sample_data(self, data: List[Dict[str, Any]], interval_minutes: int = 5) -> List[Dict[str, Any]]:
        """
        对数据进行采样，减少数据点数量
        
        Args:
            data: 按时间排序的数据列表
            interval_minutes: 采样间隔（分钟）
            
        Returns:
            采样后的数据列表
        """
        if not data:
            return []
        
        sampled_data = []
        last_timestamp = None
        
        for entry in data:
            timestamp = entry['timestamp']
            
            # 第一个数据点总是包含
            if last_timestamp is None:
                sampled_data.append(entry)
                last_timestamp = timestamp
                continue
            
            # 检查时间间隔
            time_diff = (timestamp - last_timestamp).total_seconds() / 60
            
            if time_diff >= interval_minutes:
                sampled_data.append(entry)
                last_timestamp = timestamp
        
        # 确保包含最后一个数据点
        if data and sampled_data and data[-1]['timestamp'] != sampled_data[-1]['timestamp']:
            sampled_data.append(data[-1])
        
        return sampled_data
    
    def _identify_activity_blocks(self, activity_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        识别活动块（一段连续的活动记录）
        
        Args:
            activity_data: 活动数据列表
            
        Returns:
            活动块列表
        """
        if not activity_data:
            return []
        
        # 按时间排序
        sorted_data = sorted(activity_data, key=lambda x: x['timestamp'])
        
        blocks = []
        current_block = None
        
        for entry in sorted_data:
            timestamp = entry['timestamp']
            metadata = entry.get('metadata', {})
            
            # 检查是否是新的活动块
            if current_block is None:
                current_block = {
                    'start_time': timestamp,
                    'end_time': timestamp,
                    'type': entry.get('type', 'unknown'),
                    'data_points': [entry],
                    'stats': {
                        'steps': metadata.get('steps', 0),
                        'calories': metadata.get('calories', 0),
                        'distance': metadata.get('distance', 0),
                        'heart_rates': [metadata.get('heart_rate')] if 'heart_rate' in metadata else []
                    }
                }
            else:
                # 检查时间间隔
                time_diff = (timestamp - current_block['end_time']).total_seconds()
                
                # 如果间隔超过5分钟，认为是新的活动块
                if time_diff > 300:  # 5分钟 = 300秒
                    # 完成当前块的统计信息
                    if current_block['stats']['heart_rates']:
                        current_block['stats']['avg_heart_rate'] = sum(filter(None, current_block['stats']['heart_rates'])) / len(current_block['stats']['heart_rates'])
                        current_block['stats']['max_heart_rate'] = max(filter(None, current_block['stats']['heart_rates']))
                    
                    # 添加到结果并创建新块
                    blocks.append(current_block)
                    
                    current_block = {
                        'start_time': timestamp,
                        'end_time': timestamp,
                        'type': entry.get('type', 'unknown'),
                        'data_points': [entry],
                        'stats': {
                            'steps': metadata.get('steps', 0),
                            'calories': metadata.get('calories', 0),
                            'distance': metadata.get('distance', 0),
                            'heart_rates': [metadata.get('heart_rate')] if 'heart_rate' in metadata else []
                        }
                    }
                else:
                    # 更新当前块
                    current_block['end_time'] = timestamp
                    current_block['data_points'].append(entry)
                    
                    # 更新统计信息
                    if 'steps' in metadata and metadata['steps'] is not None:
                        current_block['stats']['steps'] = metadata['steps']
                    if 'calories' in metadata and metadata['calories'] is not None:
                        current_block['stats']['calories'] = metadata['calories']
                    if 'distance' in metadata and metadata['distance'] is not None:
                        current_block['stats']['distance'] = metadata['distance']
                    if 'heart_rate' in metadata and metadata['heart_rate'] is not None:
                        current_block['stats']['heart_rates'].append(metadata['heart_rate'])
        
        # 添加最后一个块
        if current_block:
            # 完成当前块的统计信息
            if current_block['stats']['heart_rates']:
                heart_rates = list(filter(None, current_block['stats']['heart_rates']))
                if heart_rates:
                    current_block['stats']['avg_heart_rate'] = sum(heart_rates) / len(heart_rates)
                    current_block['stats']['max_heart_rate'] = max(heart_rates)
            
            blocks.append(current_block)
        
        return blocks 