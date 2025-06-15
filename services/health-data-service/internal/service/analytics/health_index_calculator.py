#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康指标计算器
计算用户的综合健康指数和各项健康指标
"""

import asyncio
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger

from ...model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit


@dataclass
class HealthMetrics:
    """健康指标"""
    heart_rate_score: float = 0.0
    steps_score: float = 0.0
    sleep_score: float = 0.0
    blood_pressure_score: float = 0.0
    blood_glucose_score: float = 0.0
    body_temperature_score: float = 0.0
    oxygen_saturation_score: float = 0.0
    overall_score: float = 0.0
    grade: str = "未知"
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class TrendAnalysis:
    """趋势分析"""
    direction: str  # "improving", "stable", "declining"
    change_rate: float  # 变化率
    confidence: float  # 置信度
    period_days: int  # 分析周期


class HealthIndexCalculator:
    """健康指标计算器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化健康指标计算器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.weights = config.get('weights', {})
        self.cache_duration = config.get('cache_duration', 3600)
        self.is_initialized = False
        
        # 默认权重配置
        self.default_weights = {
            'heart_rate': 0.2,
            'steps': 0.15,
            'sleep': 0.25,
            'blood_pressure': 0.2,
            'blood_glucose': 0.1,
            'body_temperature': 0.05,
            'oxygen_saturation': 0.05
        }
        
        # 合并配置权重
        self.weights = {**self.default_weights, **self.weights}
        
        # 参考标准
        self.reference_standards = {}
    
    async def initialize(self) -> None:
        """初始化计算器"""
        if self.is_initialized:
            return
        
        await self._load_reference_standards()
        self.is_initialized = True
        logger.info("健康指标计算器初始化完成")
    
    async def _load_reference_standards(self) -> None:
        """加载参考标准"""
        self.reference_standards = {
            HealthDataType.HEART_RATE: {
                'excellent': (60, 70),
                'good': (70, 85),
                'fair': (85, 100),
                'poor': (100, 120),
                'very_poor': (120, 220)
            },
            
            HealthDataType.STEPS: {
                'excellent': (12000, 20000),
                'good': (10000, 12000),
                'fair': (7500, 10000),
                'poor': (5000, 7500),
                'very_poor': (0, 5000)
            },
            
            HealthDataType.SLEEP: {
                'excellent': (7.5, 9),
                'good': (7, 7.5),
                'fair': (6, 7),
                'poor': (5, 6),
                'very_poor': (0, 5)
            },
            
            HealthDataType.BLOOD_PRESSURE: {
                'excellent': {'systolic': (90, 120), 'diastolic': (60, 80)},
                'good': {'systolic': (120, 130), 'diastolic': (80, 85)},
                'fair': {'systolic': (130, 140), 'diastolic': (85, 90)},
                'poor': {'systolic': (140, 160), 'diastolic': (90, 100)},
                'very_poor': {'systolic': (160, 250), 'diastolic': (100, 150)}
            },
            
            HealthDataType.BLOOD_GLUCOSE: {
                'excellent': (3.9, 5.6),  # mmol/L
                'good': (5.6, 6.1),
                'fair': (6.1, 7.0),
                'poor': (7.0, 11.1),
                'very_poor': (11.1, 30.0)
            },
            
            HealthDataType.BODY_TEMPERATURE: {
                'excellent': (36.1, 37.2),
                'good': (36.0, 36.1),
                'fair': (35.8, 36.0),
                'poor': (35.5, 35.8),
                'very_poor': (35.0, 35.5)
            },
            
            HealthDataType.OXYGEN_SATURATION: {
                'excellent': (98, 100),
                'good': (95, 98),
                'fair': (92, 95),
                'poor': (88, 92),
                'very_poor': (70, 88)
            }
        }
    
    async def calculate_health_index(
        self, 
        user_id: str, 
        data_list: List[HealthData],
        days: int = 30
    ) -> HealthMetrics:
        """
        计算用户健康指数
        
        Args:
            user_id: 用户ID
            data_list: 健康数据列表
            days: 计算周期（天）
            
        Returns:
            健康指标
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 按数据类型分组
        data_by_type = self._group_data_by_type(data_list)
        
        # 计算各项指标得分
        metrics = HealthMetrics()
        
        # 心率得分
        if HealthDataType.HEART_RATE in data_by_type:
            metrics.heart_rate_score = await self._calculate_heart_rate_score(
                data_by_type[HealthDataType.HEART_RATE]
            )
        
        # 步数得分
        if HealthDataType.STEPS in data_by_type:
            metrics.steps_score = await self._calculate_steps_score(
                data_by_type[HealthDataType.STEPS]
            )
        
        # 睡眠得分
        if HealthDataType.SLEEP in data_by_type:
            metrics.sleep_score = await self._calculate_sleep_score(
                data_by_type[HealthDataType.SLEEP]
            )
        
        # 血压得分
        if HealthDataType.BLOOD_PRESSURE in data_by_type:
            metrics.blood_pressure_score = await self._calculate_blood_pressure_score(
                data_by_type[HealthDataType.BLOOD_PRESSURE]
            )
        
        # 血糖得分
        if HealthDataType.BLOOD_GLUCOSE in data_by_type:
            metrics.blood_glucose_score = await self._calculate_blood_glucose_score(
                data_by_type[HealthDataType.BLOOD_GLUCOSE]
            )
        
        # 体温得分
        if HealthDataType.BODY_TEMPERATURE in data_by_type:
            metrics.body_temperature_score = await self._calculate_body_temperature_score(
                data_by_type[HealthDataType.BODY_TEMPERATURE]
            )
        
        # 血氧得分
        if HealthDataType.OXYGEN_SATURATION in data_by_type:
            metrics.oxygen_saturation_score = await self._calculate_oxygen_saturation_score(
                data_by_type[HealthDataType.OXYGEN_SATURATION]
            )
        
        # 计算综合得分
        metrics.overall_score = await self._calculate_overall_score(metrics)
        
        # 确定健康等级
        metrics.grade = self._determine_health_grade(metrics.overall_score)
        
        # 生成建议
        metrics.recommendations = await self._generate_recommendations(metrics, data_by_type)
        
        return metrics
    
    def _group_data_by_type(self, data_list: List[HealthData]) -> Dict[HealthDataType, List[HealthData]]:
        """按数据类型分组"""
        grouped = {}
        for data in data_list:
            if data.data_type not in grouped:
                grouped[data.data_type] = []
            grouped[data.data_type].append(data)
        return grouped
    
    async def _calculate_heart_rate_score(self, heart_rate_data: List[HealthData]) -> float:
        """计算心率得分"""
        if not heart_rate_data:
            return 0.0
        
        # 计算平均心率
        values = [float(data.value) for data in heart_rate_data if isinstance(data.value, (int, float))]
        if not values:
            return 0.0
        
        avg_heart_rate = statistics.mean(values)
        
        # 计算静息心率（取最低的20%）
        sorted_values = sorted(values)
        resting_hr_count = max(1, len(sorted_values) // 5)
        resting_heart_rate = statistics.mean(sorted_values[:resting_hr_count])
        
        # 基于静息心率评分
        standards = self.reference_standards[HealthDataType.HEART_RATE]
        score = self._calculate_score_by_range(resting_heart_rate, standards)
        
        # 心率变异性加分
        if len(values) > 10:
            hr_variability = statistics.stdev(values)
            # 适度的心率变异性是健康的标志
            if 5 <= hr_variability <= 15:
                score += 5  # 额外加分
        
        return min(score, 100.0)
    
    async def _calculate_steps_score(self, steps_data: List[HealthData]) -> float:
        """计算步数得分"""
        if not steps_data:
            return 0.0
        
        # 按天聚合步数
        daily_steps = self._aggregate_daily_steps(steps_data)
        if not daily_steps:
            return 0.0
        
        avg_daily_steps = statistics.mean(daily_steps)
        
        # 基于平均日步数评分
        standards = self.reference_standards[HealthDataType.STEPS]
        score = self._calculate_score_by_range(avg_daily_steps, standards)
        
        # 一致性加分
        if len(daily_steps) > 7:
            consistency = 1 - (statistics.stdev(daily_steps) / avg_daily_steps)
            score += consistency * 10  # 一致性加分
        
        return min(score, 100.0)
    
    async def _calculate_sleep_score(self, sleep_data: List[HealthData]) -> float:
        """计算睡眠得分"""
        if not sleep_data:
            return 0.0
        
        # 计算平均睡眠时长
        sleep_durations = []
        for data in sleep_data:
            if isinstance(data.value, (int, float)):
                sleep_durations.append(float(data.value))
            elif isinstance(data.value, dict) and 'duration' in data.value:
                sleep_durations.append(float(data.value['duration']))
        
        if not sleep_durations:
            return 0.0
        
        avg_sleep_duration = statistics.mean(sleep_durations)
        
        # 基于睡眠时长评分
        standards = self.reference_standards[HealthDataType.SLEEP]
        score = self._calculate_score_by_range(avg_sleep_duration, standards)
        
        # 睡眠质量加分
        quality_scores = []
        for data in sleep_data:
            if isinstance(data.value, dict) and 'quality' in data.value:
                quality_scores.append(float(data.value['quality']))
        
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            score += (avg_quality / 100) * 20  # 质量加分
        
        return min(score, 100.0)
    
    async def _calculate_blood_pressure_score(self, bp_data: List[HealthData]) -> float:
        """计算血压得分"""
        if not bp_data:
            return 0.0
        
        systolic_values = []
        diastolic_values = []
        
        for data in bp_data:
            if isinstance(data.value, dict):
                if 'systolic' in data.value:
                    systolic_values.append(float(data.value['systolic']))
                if 'diastolic' in data.value:
                    diastolic_values.append(float(data.value['diastolic']))
        
        if not systolic_values or not diastolic_values:
            return 0.0
        
        avg_systolic = statistics.mean(systolic_values)
        avg_diastolic = statistics.mean(diastolic_values)
        
        # 分别计算收缩压和舒张压得分
        standards = self.reference_standards[HealthDataType.BLOOD_PRESSURE]
        
        systolic_score = 0
        diastolic_score = 0
        
        for grade, ranges in standards.items():
            if isinstance(ranges, dict):
                sys_min, sys_max = ranges['systolic']
                dia_min, dia_max = ranges['diastolic']
                
                if sys_min <= avg_systolic <= sys_max:
                    systolic_score = self._grade_to_score(grade)
                
                if dia_min <= avg_diastolic <= dia_max:
                    diastolic_score = self._grade_to_score(grade)
        
        # 综合得分
        score = (systolic_score + diastolic_score) / 2
        
        # 脉压差检查
        pulse_pressure = avg_systolic - avg_diastolic
        if 30 <= pulse_pressure <= 50:
            score += 5  # 正常脉压差加分
        
        return min(score, 100.0)
    
    async def _calculate_blood_glucose_score(self, glucose_data: List[HealthData]) -> float:
        """计算血糖得分"""
        if not glucose_data:
            return 0.0
        
        values = [float(data.value) for data in glucose_data if isinstance(data.value, (int, float))]
        if not values:
            return 0.0
        
        avg_glucose = statistics.mean(values)
        
        # 基于平均血糖评分
        standards = self.reference_standards[HealthDataType.BLOOD_GLUCOSE]
        score = self._calculate_score_by_range(avg_glucose, standards)
        
        # 血糖稳定性加分
        if len(values) > 5:
            glucose_cv = statistics.stdev(values) / avg_glucose  # 变异系数
            if glucose_cv < 0.2:  # 变异系数小于20%
                score += 10
        
        return min(score, 100.0)
    
    async def _calculate_body_temperature_score(self, temp_data: List[HealthData]) -> float:
        """计算体温得分"""
        if not temp_data:
            return 0.0
        
        values = [float(data.value) for data in temp_data if isinstance(data.value, (int, float))]
        if not values:
            return 0.0
        
        avg_temperature = statistics.mean(values)
        
        # 基于平均体温评分
        standards = self.reference_standards[HealthDataType.BODY_TEMPERATURE]
        score = self._calculate_score_by_range(avg_temperature, standards)
        
        return min(score, 100.0)
    
    async def _calculate_oxygen_saturation_score(self, spo2_data: List[HealthData]) -> float:
        """计算血氧饱和度得分"""
        if not spo2_data:
            return 0.0
        
        values = [float(data.value) for data in spo2_data if isinstance(data.value, (int, float))]
        if not values:
            return 0.0
        
        avg_spo2 = statistics.mean(values)
        
        # 基于平均血氧饱和度评分
        standards = self.reference_standards[HealthDataType.OXYGEN_SATURATION]
        score = self._calculate_score_by_range(avg_spo2, standards)
        
        return min(score, 100.0)
    
    def _calculate_score_by_range(self, value: float, standards: Dict[str, Tuple[float, float]]) -> float:
        """根据范围计算得分"""
        for grade, (min_val, max_val) in standards.items():
            if min_val <= value <= max_val:
                return self._grade_to_score(grade)
        
        # 如果不在任何范围内，返回最低分
        return 20.0
    
    def _grade_to_score(self, grade: str) -> float:
        """等级转换为得分"""
        grade_scores = {
            'excellent': 95.0,
            'good': 80.0,
            'fair': 65.0,
            'poor': 45.0,
            'very_poor': 25.0
        }
        return grade_scores.get(grade, 50.0)
    
    async def _calculate_overall_score(self, metrics: HealthMetrics) -> float:
        """计算综合得分"""
        total_score = 0.0
        total_weight = 0.0
        
        # 根据权重计算加权平均分
        score_weight_pairs = [
            (metrics.heart_rate_score, self.weights.get('heart_rate', 0)),
            (metrics.steps_score, self.weights.get('steps', 0)),
            (metrics.sleep_score, self.weights.get('sleep', 0)),
            (metrics.blood_pressure_score, self.weights.get('blood_pressure', 0)),
            (metrics.blood_glucose_score, self.weights.get('blood_glucose', 0)),
            (metrics.body_temperature_score, self.weights.get('body_temperature', 0)),
            (metrics.oxygen_saturation_score, self.weights.get('oxygen_saturation', 0))
        ]
        
        for score, weight in score_weight_pairs:
            if score > 0:  # 只计算有数据的指标
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def _determine_health_grade(self, overall_score: float) -> str:
        """确定健康等级"""
        if overall_score >= 90:
            return "优秀"
        elif overall_score >= 80:
            return "良好"
        elif overall_score >= 70:
            return "一般"
        elif overall_score >= 60:
            return "较差"
        else:
            return "差"
    
    async def _generate_recommendations(
        self, 
        metrics: HealthMetrics, 
        data_by_type: Dict[HealthDataType, List[HealthData]]
    ) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 心率建议
        if metrics.heart_rate_score < 70:
            recommendations.append("建议进行有氧运动来改善心率健康，如快走、游泳或骑自行车")
        
        # 步数建议
        if metrics.steps_score < 70:
            recommendations.append("建议增加日常活动量，目标每天至少10000步")
        
        # 睡眠建议
        if metrics.sleep_score < 70:
            recommendations.append("建议改善睡眠质量，保持规律作息，每晚7-9小时睡眠")
        
        # 血压建议
        if metrics.blood_pressure_score < 70:
            recommendations.append("建议控制血压，减少盐分摄入，保持健康体重")
        
        # 血糖建议
        if metrics.blood_glucose_score < 70:
            recommendations.append("建议控制血糖，注意饮食平衡，减少糖分摄入")
        
        # 体温建议
        if metrics.body_temperature_score < 70:
            recommendations.append("建议关注体温变化，如有异常请及时就医")
        
        # 血氧建议
        if metrics.oxygen_saturation_score < 70:
            recommendations.append("建议进行深呼吸练习，如有持续异常请咨询医生")
        
        # 综合建议
        if metrics.overall_score < 60:
            recommendations.append("建议全面改善生活方式，包括饮食、运动和睡眠")
        elif metrics.overall_score < 80:
            recommendations.append("健康状况良好，建议继续保持并适当改进")
        else:
            recommendations.append("健康状况优秀，请继续保持良好的生活习惯")
        
        return recommendations
    
    def _aggregate_daily_steps(self, steps_data: List[HealthData]) -> List[float]:
        """聚合每日步数"""
        daily_steps = {}
        
        for data in steps_data:
            if isinstance(data.value, (int, float)):
                date_key = data.timestamp.date()
                if date_key not in daily_steps:
                    daily_steps[date_key] = 0
                daily_steps[date_key] += float(data.value)
        
        return list(daily_steps.values())
    
    async def analyze_trend(
        self, 
        user_id: str, 
        data_type: HealthDataType,
        data_list: List[HealthData],
        days: int = 30
    ) -> TrendAnalysis:
        """
        分析健康指标趋势
        
        Args:
            user_id: 用户ID
            data_type: 数据类型
            data_list: 健康数据列表
            days: 分析周期
            
        Returns:
            趋势分析结果
        """
        if len(data_list) < 7:  # 至少需要7个数据点
            return TrendAnalysis(
                direction="stable",
                change_rate=0.0,
                confidence=0.0,
                period_days=days
            )
        
        # 按时间排序
        sorted_data = sorted(data_list, key=lambda x: x.timestamp)
        
        # 提取数值
        values = []
        timestamps = []
        
        for data in sorted_data:
            if isinstance(data.value, (int, float)):
                values.append(float(data.value))
                timestamps.append(data.timestamp)
            elif isinstance(data.value, dict) and 'value' in data.value:
                values.append(float(data.value['value']))
                timestamps.append(data.timestamp)
        
        if len(values) < 7:
            return TrendAnalysis(
                direction="stable",
                change_rate=0.0,
                confidence=0.0,
                period_days=days
            )
        
        # 计算趋势
        direction, change_rate, confidence = self._calculate_trend(values, timestamps)
        
        return TrendAnalysis(
            direction=direction,
            change_rate=change_rate,
            confidence=confidence,
            period_days=days
        )
    
    def _calculate_trend(
        self, 
        values: List[float], 
        timestamps: List[datetime]
    ) -> Tuple[str, float, float]:
        """计算趋势方向和变化率"""
        if len(values) < 2:
            return "stable", 0.0, 0.0
        
        # 简单线性回归计算趋势
        n = len(values)
        
        # 将时间戳转换为数值（天数）
        base_time = timestamps[0]
        x_values = [(ts - base_time).total_seconds() / 86400 for ts in timestamps]
        
        # 计算回归系数
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable", 0.0, 0.0
        
        slope = numerator / denominator
        
        # 计算相关系数作为置信度
        y_variance = sum((y - y_mean) ** 2 for y in values)
        if y_variance == 0:
            confidence = 0.0
        else:
            r_squared = (numerator ** 2) / (denominator * y_variance)
            confidence = r_squared
        
        # 确定趋势方向
        change_rate = abs(slope)
        
        # 根据斜率和置信度确定趋势
        if confidence < 0.3:  # 置信度太低
            direction = "stable"
        elif slope > 0.1:  # 正向趋势
            direction = "improving"
        elif slope < -0.1:  # 负向趋势
            direction = "declining"
        else:
            direction = "stable"
        
        return direction, change_rate, confidence
    
    async def update_health_index(self, user_id: str) -> Optional[HealthMetrics]:
        """
        更新用户健康指数
        
        Args:
            user_id: 用户ID
            
        Returns:
            更新后的健康指标
        """
        try:
            # 这里应该从数据库获取用户的健康数据
            # 由于这是服务层，我们假设数据已经传入
            logger.info(f"更新用户 {user_id} 的健康指数")
            
            # 实际实现中，这里会调用数据仓库获取数据
            # data_list = await self.repository.get_recent_health_data(user_id, days=30)
            # metrics = await self.calculate_health_index(user_id, data_list)
            
            # 暂时返回None，实际使用时需要完整实现
            return None
            
        except Exception as e:
            logger.error(f"更新健康指数失败: {e}")
            return None 