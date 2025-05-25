#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据质量评估器
评估健康数据的完整性、准确性、一致性和及时性
"""

import asyncio
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger

from ...model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit


@dataclass
class DataQualityMetrics:
    """数据质量指标"""
    completeness: float  # 完整性 0-1
    accuracy: float      # 准确性 0-1
    consistency: float   # 一致性 0-1
    timeliness: float    # 及时性 0-1
    overall_score: float # 总体评分 0-1
    details: Dict[str, Any] = None  # 详细信息


class DataQualityAssessor:
    """数据质量评估器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据质量评估器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.quality_rules = {}
        self.reference_ranges = {}
        self.is_initialized = False
        
        # 质量权重配置
        self.quality_weights = {
            'completeness': 0.3,
            'accuracy': 0.3,
            'consistency': 0.2,
            'timeliness': 0.2
        }
    
    async def initialize(self) -> None:
        """初始化质量评估器"""
        if self.is_initialized:
            return
        
        # 加载质量规则
        await self._load_quality_rules()
        
        # 加载参考范围
        await self._load_reference_ranges()
        
        self.is_initialized = True
        logger.info("数据质量评估器初始化完成")
    
    async def _load_quality_rules(self) -> None:
        """加载数据质量规则"""
        self.quality_rules = {
            # 心率质量规则
            HealthDataType.HEART_RATE: {
                'min_value': 30,
                'max_value': 220,
                'expected_frequency': timedelta(minutes=5),  # 期望采集频率
                'outlier_threshold': 3,  # 异常值阈值（标准差倍数）
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 步数质量规则
            HealthDataType.STEPS: {
                'min_value': 0,
                'max_value': 100000,
                'expected_frequency': timedelta(hours=1),
                'outlier_threshold': 3,
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 睡眠质量规则
            HealthDataType.SLEEP: {
                'min_value': 0,
                'max_value': 24,  # 小时
                'expected_frequency': timedelta(days=1),
                'outlier_threshold': 2,
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 血压质量规则
            HealthDataType.BLOOD_PRESSURE: {
                'min_systolic': 70,
                'max_systolic': 250,
                'min_diastolic': 40,
                'max_diastolic': 150,
                'expected_frequency': timedelta(hours=12),
                'outlier_threshold': 2.5,
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 血糖质量规则
            HealthDataType.BLOOD_GLUCOSE: {
                'min_value': 2.0,  # mmol/L
                'max_value': 30.0,
                'expected_frequency': timedelta(hours=8),
                'outlier_threshold': 2.5,
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 体温质量规则
            HealthDataType.BODY_TEMPERATURE: {
                'min_value': 35.0,  # 摄氏度
                'max_value': 42.0,
                'expected_frequency': timedelta(hours=12),
                'outlier_threshold': 2,
                'required_fields': ['value', 'timestamp', 'device_type']
            },
            
            # 血氧饱和度质量规则
            HealthDataType.OXYGEN_SATURATION: {
                'min_value': 70,  # 百分比
                'max_value': 100,
                'expected_frequency': timedelta(hours=6),
                'outlier_threshold': 2,
                'required_fields': ['value', 'timestamp', 'device_type']
            }
        }
    
    async def _load_reference_ranges(self) -> None:
        """加载参考范围数据"""
        self.reference_ranges = {
            HealthDataType.HEART_RATE: {
                'normal_range': (60, 100),
                'age_adjustments': {
                    (0, 1): (100, 160),
                    (1, 3): (90, 150),
                    (3, 5): (80, 140),
                    (5, 12): (70, 110),
                    (12, 18): (60, 100),
                    (18, 65): (60, 100),
                    (65, 100): (50, 90)
                }
            },
            
            HealthDataType.BLOOD_PRESSURE: {
                'normal_systolic': (90, 140),
                'normal_diastolic': (60, 90),
                'hypertension_stage1_systolic': (140, 160),
                'hypertension_stage1_diastolic': (90, 100)
            },
            
            HealthDataType.BLOOD_GLUCOSE: {
                'fasting_normal': (3.9, 6.1),  # mmol/L
                'postprandial_normal': (3.9, 7.8),
                'diabetes_threshold': 7.0
            },
            
            HealthDataType.BODY_TEMPERATURE: {
                'normal_range': (36.1, 37.2),
                'fever_threshold': 37.3,
                'high_fever_threshold': 39.0
            },
            
            HealthDataType.OXYGEN_SATURATION: {
                'normal_range': (95, 100),
                'mild_hypoxia': (90, 94),
                'moderate_hypoxia': (85, 89)
            }
        }
    
    async def assess_data_quality(self, data: HealthData) -> DataQualityMetrics:
        """
        评估单条健康数据的质量
        
        Args:
            data: 健康数据
            
        Returns:
            数据质量指标
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 评估各个维度
        completeness = await self._assess_completeness(data)
        accuracy = await self._assess_accuracy(data)
        consistency = await self._assess_consistency(data)
        timeliness = await self._assess_timeliness(data)
        
        # 计算总体评分
        overall_score = (
            completeness * self.quality_weights['completeness'] +
            accuracy * self.quality_weights['accuracy'] +
            consistency * self.quality_weights['consistency'] +
            timeliness * self.quality_weights['timeliness']
        )
        
        details = {
            'completeness_details': await self._get_completeness_details(data),
            'accuracy_details': await self._get_accuracy_details(data),
            'consistency_details': await self._get_consistency_details(data),
            'timeliness_details': await self._get_timeliness_details(data)
        }
        
        return DataQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            consistency=consistency,
            timeliness=timeliness,
            overall_score=overall_score,
            details=details
        )
    
    async def assess_batch_quality(self, data_list: List[HealthData]) -> Dict[str, Any]:
        """
        评估批量健康数据的质量
        
        Args:
            data_list: 健康数据列表
            
        Returns:
            批量质量评估结果
        """
        if not data_list:
            return {
                'overall_quality': 0.0,
                'individual_scores': [],
                'summary': {
                    'total_records': 0,
                    'high_quality_count': 0,
                    'medium_quality_count': 0,
                    'low_quality_count': 0
                }
            }
        
        # 评估每条数据
        individual_metrics = []
        for data in data_list:
            metrics = await self.assess_data_quality(data)
            individual_metrics.append(metrics)
        
        # 计算统计信息
        scores = [m.overall_score for m in individual_metrics]
        overall_quality = sum(scores) / len(scores)
        
        # 质量分级统计
        high_quality_count = sum(1 for score in scores if score >= 0.8)
        medium_quality_count = sum(1 for score in scores if 0.5 <= score < 0.8)
        low_quality_count = sum(1 for score in scores if score < 0.5)
        
        # 按数据类型分组统计
        type_quality = {}
        for data, metrics in zip(data_list, individual_metrics):
            data_type = data.data_type.value
            if data_type not in type_quality:
                type_quality[data_type] = []
            type_quality[data_type].append(metrics.overall_score)
        
        type_averages = {
            data_type: sum(scores) / len(scores)
            for data_type, scores in type_quality.items()
        }
        
        return {
            'overall_quality': overall_quality,
            'individual_scores': [m.overall_score for m in individual_metrics],
            'summary': {
                'total_records': len(data_list),
                'high_quality_count': high_quality_count,
                'medium_quality_count': medium_quality_count,
                'low_quality_count': low_quality_count,
                'high_quality_rate': high_quality_count / len(data_list),
                'medium_quality_rate': medium_quality_count / len(data_list),
                'low_quality_rate': low_quality_count / len(data_list)
            },
            'quality_by_type': type_averages,
            'detailed_metrics': individual_metrics
        }
    
    async def _assess_completeness(self, data: HealthData) -> float:
        """评估数据完整性"""
        rules = self.quality_rules.get(data.data_type, {})
        required_fields = rules.get('required_fields', [])
        
        if not required_fields:
            return 1.0  # 没有特定要求，认为完整
        
        score = 0.0
        total_fields = len(required_fields)
        
        for field in required_fields:
            if field == 'value' and data.value is not None:
                score += 1.0
            elif field == 'timestamp' and data.timestamp is not None:
                score += 1.0
            elif field == 'device_type' and data.device_type is not None:
                score += 1.0
            elif field == 'device_id' and data.device_id is not None:
                score += 1.0
            elif field == 'source' and data.source is not None:
                score += 1.0
        
        # 检查元数据完整性
        if data.metadata:
            metadata_score = min(len(data.metadata) / 3, 1.0)  # 期望至少3个元数据字段
            score += metadata_score * 0.2  # 元数据占20%权重
            total_fields += 0.2
        
        return min(score / total_fields, 1.0)
    
    async def _assess_accuracy(self, data: HealthData) -> float:
        """评估数据准确性"""
        rules = self.quality_rules.get(data.data_type, {})
        
        if not rules:
            return 1.0  # 没有规则，认为准确
        
        score = 1.0
        
        # 检查数值范围
        if isinstance(data.value, (int, float)):
            value = float(data.value)
            
            # 基本范围检查
            min_value = rules.get('min_value')
            max_value = rules.get('max_value')
            
            if min_value is not None and value < min_value:
                score *= 0.3  # 严重超出范围
            elif max_value is not None and value > max_value:
                score *= 0.3
            
            # 参考范围检查
            ref_ranges = self.reference_ranges.get(data.data_type, {})
            normal_range = ref_ranges.get('normal_range')
            
            if normal_range:
                min_normal, max_normal = normal_range
                if min_normal <= value <= max_normal:
                    score *= 1.0  # 在正常范围内
                elif value < min_normal * 0.5 or value > max_normal * 2:
                    score *= 0.4  # 严重异常
                else:
                    score *= 0.7  # 轻度异常
        
        # 血压特殊处理
        elif data.data_type == HealthDataType.BLOOD_PRESSURE and isinstance(data.value, dict):
            systolic = data.value.get('systolic')
            diastolic = data.value.get('diastolic')
            
            if systolic and diastolic:
                # 检查收缩压和舒张压的合理性
                if systolic <= diastolic:
                    score *= 0.2  # 收缩压不应小于等于舒张压
                elif systolic - diastolic < 20:
                    score *= 0.6  # 脉压差过小
                elif systolic - diastolic > 100:
                    score *= 0.7  # 脉压差过大
        
        # 设备一致性检查
        if data.device_type and data.device_id:
            # 检查设备类型和设备ID的一致性
            device_consistency = await self._check_device_consistency(data)
            score *= device_consistency
        
        return max(score, 0.0)
    
    async def _assess_consistency(self, data: HealthData) -> float:
        """评估数据一致性"""
        score = 1.0
        
        # 时间戳一致性检查
        if data.timestamp:
            now = datetime.utcnow()
            time_diff = abs((now - data.timestamp).total_seconds())
            
            # 数据不应该来自未来
            if data.timestamp > now:
                score *= 0.5
            
            # 数据不应该过于陈旧（超过1年）
            elif time_diff > 365 * 24 * 3600:
                score *= 0.7
        
        # 单位一致性检查
        if data.unit and data.data_type:
            expected_units = self._get_expected_units(data.data_type)
            if expected_units and data.unit not in expected_units:
                score *= 0.6
        
        # 数值类型一致性检查
        if data.data_type in [HealthDataType.HEART_RATE, HealthDataType.STEPS]:
            if not isinstance(data.value, (int, float)):
                score *= 0.4
        elif data.data_type == HealthDataType.BLOOD_PRESSURE:
            if not isinstance(data.value, dict) or 'systolic' not in data.value or 'diastolic' not in data.value:
                score *= 0.3
        
        return max(score, 0.0)
    
    async def _assess_timeliness(self, data: HealthData) -> float:
        """评估数据及时性"""
        if not data.timestamp:
            return 0.5  # 没有时间戳，中等评分
        
        now = datetime.utcnow()
        time_diff = (now - data.timestamp).total_seconds()
        
        # 数据来自未来
        if time_diff < 0:
            return 0.2
        
        # 根据数据类型的期望频率评估及时性
        rules = self.quality_rules.get(data.data_type, {})
        expected_frequency = rules.get('expected_frequency')
        
        if not expected_frequency:
            # 没有期望频率，基于通用规则
            if time_diff <= 3600:  # 1小时内
                return 1.0
            elif time_diff <= 86400:  # 1天内
                return 0.8
            elif time_diff <= 604800:  # 1周内
                return 0.6
            else:
                return 0.3
        
        # 基于期望频率计算
        expected_seconds = expected_frequency.total_seconds()
        
        if time_diff <= expected_seconds:
            return 1.0
        elif time_diff <= expected_seconds * 2:
            return 0.8
        elif time_diff <= expected_seconds * 5:
            return 0.6
        elif time_diff <= expected_seconds * 10:
            return 0.4
        else:
            return 0.2
    
    async def _get_completeness_details(self, data: HealthData) -> Dict[str, Any]:
        """获取完整性详细信息"""
        rules = self.quality_rules.get(data.data_type, {})
        required_fields = rules.get('required_fields', [])
        
        field_status = {}
        for field in required_fields:
            if field == 'value':
                field_status[field] = data.value is not None
            elif field == 'timestamp':
                field_status[field] = data.timestamp is not None
            elif field == 'device_type':
                field_status[field] = data.device_type is not None
            elif field == 'device_id':
                field_status[field] = data.device_id is not None
            elif field == 'source':
                field_status[field] = data.source is not None
        
        return {
            'required_fields': required_fields,
            'field_status': field_status,
            'metadata_count': len(data.metadata) if data.metadata else 0
        }
    
    async def _get_accuracy_details(self, data: HealthData) -> Dict[str, Any]:
        """获取准确性详细信息"""
        rules = self.quality_rules.get(data.data_type, {})
        ref_ranges = self.reference_ranges.get(data.data_type, {})
        
        details = {
            'value_in_range': True,
            'value_in_normal_range': True,
            'device_consistent': True
        }
        
        if isinstance(data.value, (int, float)):
            value = float(data.value)
            
            # 检查基本范围
            min_value = rules.get('min_value')
            max_value = rules.get('max_value')
            
            if min_value is not None and value < min_value:
                details['value_in_range'] = False
                details['range_violation'] = f"值 {value} 小于最小值 {min_value}"
            elif max_value is not None and value > max_value:
                details['value_in_range'] = False
                details['range_violation'] = f"值 {value} 大于最大值 {max_value}"
            
            # 检查正常范围
            normal_range = ref_ranges.get('normal_range')
            if normal_range:
                min_normal, max_normal = normal_range
                if not (min_normal <= value <= max_normal):
                    details['value_in_normal_range'] = False
                    details['normal_range'] = normal_range
                    details['actual_value'] = value
        
        return details
    
    async def _get_consistency_details(self, data: HealthData) -> Dict[str, Any]:
        """获取一致性详细信息"""
        details = {
            'timestamp_valid': True,
            'unit_consistent': True,
            'type_consistent': True
        }
        
        # 时间戳检查
        if data.timestamp:
            now = datetime.utcnow()
            if data.timestamp > now:
                details['timestamp_valid'] = False
                details['timestamp_issue'] = "时间戳来自未来"
            elif (now - data.timestamp).days > 365:
                details['timestamp_valid'] = False
                details['timestamp_issue'] = "时间戳过于陈旧"
        
        # 单位检查
        if data.unit and data.data_type:
            expected_units = self._get_expected_units(data.data_type)
            if expected_units and data.unit not in expected_units:
                details['unit_consistent'] = False
                details['expected_units'] = expected_units
                details['actual_unit'] = data.unit
        
        return details
    
    async def _get_timeliness_details(self, data: HealthData) -> Dict[str, Any]:
        """获取及时性详细信息"""
        if not data.timestamp:
            return {'has_timestamp': False}
        
        now = datetime.utcnow()
        time_diff = (now - data.timestamp).total_seconds()
        
        rules = self.quality_rules.get(data.data_type, {})
        expected_frequency = rules.get('expected_frequency')
        
        details = {
            'has_timestamp': True,
            'time_diff_seconds': time_diff,
            'time_diff_human': self._format_time_diff(time_diff)
        }
        
        if expected_frequency:
            expected_seconds = expected_frequency.total_seconds()
            details['expected_frequency_seconds'] = expected_seconds
            details['within_expected_frequency'] = time_diff <= expected_seconds
        
        return details
    
    def _format_time_diff(self, seconds: float) -> str:
        """格式化时间差"""
        if seconds < 60:
            return f"{int(seconds)}秒前"
        elif seconds < 3600:
            return f"{int(seconds/60)}分钟前"
        elif seconds < 86400:
            return f"{int(seconds/3600)}小时前"
        else:
            return f"{int(seconds/86400)}天前"
    
    def _get_expected_units(self, data_type: HealthDataType) -> List[MeasurementUnit]:
        """获取数据类型的期望单位"""
        unit_mapping = {
            HealthDataType.HEART_RATE: [MeasurementUnit.BPM],
            HealthDataType.STEPS: [MeasurementUnit.COUNT],
            HealthDataType.SLEEP: [MeasurementUnit.HOURS, MeasurementUnit.MINUTES],
            HealthDataType.BLOOD_PRESSURE: [MeasurementUnit.MMHG],
            HealthDataType.BLOOD_GLUCOSE: [MeasurementUnit.MMOL_L, MeasurementUnit.MG_DL],
            HealthDataType.BODY_TEMPERATURE: [MeasurementUnit.CELSIUS, MeasurementUnit.FAHRENHEIT],
            HealthDataType.OXYGEN_SATURATION: [MeasurementUnit.PERCENTAGE]
        }
        
        return unit_mapping.get(data_type, [])
    
    async def _check_device_consistency(self, data: HealthData) -> float:
        """检查设备一致性"""
        # 这里可以实现更复杂的设备一致性检查逻辑
        # 例如检查设备类型和设备ID的匹配关系
        
        if not data.device_type or not data.device_id:
            return 0.8  # 缺少设备信息，轻微扣分
        
        # 简单的设备ID格式检查
        device_id = str(data.device_id)
        
        if data.device_type == DeviceType.APPLE_WATCH:
            # Apple Watch设备ID通常包含特定格式
            if len(device_id) < 10:
                return 0.7
        elif data.device_type == DeviceType.FITBIT:
            # Fitbit设备ID检查
            if not device_id.startswith('FB'):
                return 0.8
        
        return 1.0
    
    async def get_quality_report(self, data_list: List[HealthData]) -> Dict[str, Any]:
        """生成质量报告"""
        if not data_list:
            return {"error": "没有数据可分析"}
        
        batch_result = await self.assess_batch_quality(data_list)
        
        # 生成详细报告
        report = {
            "summary": batch_result["summary"],
            "overall_quality": batch_result["overall_quality"],
            "quality_by_type": batch_result["quality_by_type"],
            "recommendations": []
        }
        
        # 生成改进建议
        if batch_result["summary"]["low_quality_rate"] > 0.2:
            report["recommendations"].append("建议检查数据采集设备和流程，低质量数据比例较高")
        
        if batch_result["overall_quality"] < 0.7:
            report["recommendations"].append("整体数据质量需要改进，建议加强数据验证")
        
        # 按数据类型提供建议
        for data_type, quality in batch_result["quality_by_type"].items():
            if quality < 0.6:
                report["recommendations"].append(f"{data_type}数据质量较低，建议检查相关设备和采集流程")
        
        return report 