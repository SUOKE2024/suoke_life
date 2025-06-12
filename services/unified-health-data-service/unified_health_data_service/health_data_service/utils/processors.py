"""
健康数据处理器
提供健康数据的处理、分析和转换功能
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from statistics import mean, median, stdev
import json

logger = logging.getLogger(__name__)

class HealthDataProcessor:
    """健康数据处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self.normal_ranges = {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (90, 140),
            'blood_pressure_diastolic': (60, 90),
            'temperature': (36.1, 37.2),
            'oxygen_saturation': (95, 100),
            'respiratory_rate': (12, 20)
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理健康数据"""
        try:
            processed_data = data.copy()
            
            # 数据标准化
            processed_data = await self._normalize_data(processed_data)
            
            # 异常检测
            processed_data['anomalies'] = await self._detect_anomalies(processed_data)
            
            # 数据质量评估
            processed_data['quality_score'] = await self._assess_data_quality(processed_data)
            
            # 添加处理时间戳
            processed_data['processed_at'] = datetime.utcnow().isoformat()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"数据处理失败: {e}")
            raise
    
    async def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数据标准化"""
        normalized_data = data.copy()
        
        # 标准化生命体征数据
        if data.get('data_type')=='vital_signs':
            for key, value in data.items():
                if key in self.normal_ranges and value is not None:
                    # 转换为浮点数
                    try:
                        normalized_data[key] = float(value)
                    except (ValueError, TypeError):
                        logger.warning(f"无法转换 {key} 的值: {value}")
                        
        # 标准化时间格式
        for key in ['recorded_at', 'created_at', 'updated_at']:
            if key in data and data[key]:
                if isinstance(data[key], str):
                    try:
                        normalized_data[key] = datetime.fromisoformat(data[key].replace('Z', '+00:00'))
                    except ValueError:
                        logger.warning(f"无法解析时间格式: {data[key]}")
                        
        return normalized_data
    
    async def _detect_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """异常检测"""
        anomalies = []
        
        if data.get('data_type')=='vital_signs':
            for key, value in data.items():
                if key in self.normal_ranges and value is not None:
                    normal_min, normal_max = self.normal_ranges[key]
                    
                    if value < normal_min:
                        anomalies.append({
                            'field': key,
                            'value': value,
                            'type': 'below_normal',
                            'normal_range': self.normal_ranges[key],
                            'severity': self._calculate_severity(value, normal_min, normal_max)
                        })
                    elif value > normal_max:
                        anomalies.append({
                            'field': key,
                            'value': value,
                            'type': 'above_normal',
                            'normal_range': self.normal_ranges[key],
                            'severity': self._calculate_severity(value, normal_min, normal_max)
                        })
                        
        return anomalies
    
    def _calculate_severity(self, value: float, normal_min: float, normal_max: float) -> str:
        """计算异常严重程度"""
        if value < normal_min:
            deviation = (normal_min - value) / normal_min
        else:
            deviation = (value - normal_max) / normal_max
            
        if deviation < 0.1:
            return 'mild'
        elif deviation < 0.3:
            return 'moderate'
        else:
            return 'severe'
    
    async def _assess_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """评估数据质量"""
        quality_score = {
            'overall': 0.0,
            'completeness': 0.0,
            'accuracy': 0.0,
            'timeliness': 0.0,
            'consistency': 0.0
        }
        
        # 完整性评分
        required_fields = ['user_id', 'data_type']
        if data.get('data_type')=='vital_signs':
            required_fields.extend(['heart_rate', 'blood_pressure_systolic', 'blood_pressure_diastolic'])
            
        present_fields = sum(1 for field in required_fields if data.get(field) is not None)
        quality_score['completeness'] = present_fields / len(required_fields)
        
        # 准确性评分（基于异常检测）
        anomalies = data.get('anomalies', [])
        severe_anomalies = sum(1 for a in anomalies if a.get('severity')=='severe')
        quality_score['accuracy'] = max(0.0, 1.0 - (severe_anomalies * 0.3))
        
        # 时效性评分
        if 'recorded_at' in data:
            try:
                recorded_time = data['recorded_at']
                if isinstance(recorded_time, str):
                    recorded_time = datetime.fromisoformat(recorded_time.replace('Z', '+00:00'))
                
                time_diff = datetime.utcnow() - recorded_time
                if time_diff.total_seconds() < 3600:  # 1小时内
                    quality_score['timeliness'] = 1.0
                elif time_diff.total_seconds() < 86400:  # 24小时内
                    quality_score['timeliness'] = 0.8
                else:
                    quality_score['timeliness'] = 0.5
            except:
                quality_score['timeliness'] = 0.5
        else:
            quality_score['timeliness'] = 0.7
            
        # 一致性评分（暂时设为固定值）
        quality_score['consistency'] = 0.9
        
        # 总体评分
        quality_score['overall'] = (
            quality_score['completeness'] * 0.3 +
            quality_score['accuracy'] * 0.3 +
            quality_score['timeliness'] * 0.2 +
            quality_score['consistency'] * 0.2
        )
        
        return quality_score
    
    async def analyze_trends(self, data_points: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析健康数据趋势"""
        try:
            if not data_points:
                return {
                    'trend_direction': 'no_data',
                    'change_percent': 0.0,
                    'analysis': '无足够数据进行趋势分析'
                }
            
            # 提取数值数据
            values = []
            timestamps = []
            
            for point in data_points:
                if 'data_value' in point and point['data_value'] is not None:
                    try:
                        values.append(float(point['data_value']))
                        if 'created_at' in point:
                            timestamps.append(point['created_at'])
                    except (ValueError, TypeError):
                        continue
            
            if len(values) < 2:
                return {
                    'trend_direction': 'insufficient_data',
                    'change_percent': 0.0,
                    'analysis': '数据点不足，无法分析趋势'
                }
            
            # 计算趋势
            trend_analysis = await self._calculate_trend(values, timestamps)
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return {
                'trend_direction': 'error',
                'change_percent': 0.0,
                'analysis': f'趋势分析出错: {str(e)}'
            }
    
    async def _calculate_trend(self, values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """计算趋势指标"""
        # 基本统计
        mean_value = mean(values)
        median_value = median(values)
        
        # 计算变化趋势
        if len(values)>=2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            
            first_mean = mean(first_half)
            second_mean = mean(second_half)
            
            change_percent = ((second_mean - first_mean) / first_mean) * 100 if first_mean!=0 else 0
            
            if change_percent > 5:
                trend_direction = 'increasing'
            elif change_percent < -5:
                trend_direction = 'decreasing'
            else:
                trend_direction = 'stable'
        else:
            change_percent = 0.0
            trend_direction = 'stable'
        
        # 生成分析文本
        analysis = self._generate_trend_analysis(trend_direction, change_percent, mean_value)
        
        return {
            'trend_direction': trend_direction,
            'change_percent': round(change_percent, 2),
            'mean_value': round(mean_value, 2),
            'median_value': round(median_value, 2),
            'data_points': len(values),
            'analysis': analysis
        }
    
    def _generate_trend_analysis(self, direction: str, change_percent: float, mean_value: float) -> str:
        """生成趋势分析文本"""
        if direction=='increasing':
            return f"数据呈上升趋势，平均增长 {abs(change_percent):.1f}%，当前均值为 {mean_value:.2f}"
        elif direction=='decreasing':
            return f"数据呈下降趋势，平均下降 {abs(change_percent):.1f}%，当前均值为 {mean_value:.2f}"
        else:
            return f"数据保持稳定，变化幅度在 ±5% 以内，当前均值为 {mean_value:.2f}"
    
    async def calculate_health_score(self, user_data: Dict[str, Any]) -> float:
        """计算健康评分"""
        try:
            score = 100.0  # 基础分数
            
            # 生命体征评分
            vital_signs = user_data.get('vital_signs', {})
            if vital_signs:
                vital_score = await self._score_vital_signs(vital_signs)
                score = score * 0.4 + vital_score * 0.6
            
            # 诊断数据评分
            diagnostics = user_data.get('diagnostics', [])
            if diagnostics:
                diagnostic_score = await self._score_diagnostics(diagnostics)
                score = score * 0.7 + diagnostic_score * 0.3
            
            # 数据质量影响
            quality_scores = []
            for data in [vital_signs] + diagnostics:
                if 'quality_score' in data:
                    quality_scores.append(data['quality_score']['overall'])
            
            if quality_scores:
                avg_quality = mean(quality_scores)
                score = score * avg_quality
            
            return max(0.0, min(100.0, score))
            
        except Exception as e:
            logger.error(f"健康评分计算失败: {e}")
            return 50.0  # 默认中等分数
    
    async def _score_vital_signs(self, vital_signs: Dict[str, Any]) -> float:
        """评分生命体征"""
        score = 100.0
        
        for key, value in vital_signs.items():
            if key in self.normal_ranges and value is not None:
                normal_min, normal_max = self.normal_ranges[key]
                
                if normal_min<=value<=normal_max:
                    continue  # 正常范围，不扣分
                else:
                    # 根据偏离程度扣分
                    if value < normal_min:
                        deviation = (normal_min - value) / normal_min
                    else:
                        deviation = (value - normal_max) / normal_max
                    
                    penalty = min(30, deviation * 50)  # 最多扣30分
                    score-=penalty
        
        return max(0.0, score)
    
    async def _score_diagnostics(self, diagnostics: List[Dict[str, Any]]) -> float:
        """评分诊断数据"""
        if not diagnostics:
            return 100.0
        
        # 简化评分：根据最近诊断的置信度
        recent_diagnostic = diagnostics[0] if diagnostics else {}
        confidence = recent_diagnostic.get('confidence_score', 0.8)
        
        # 如果诊断结果表明有问题，降低分数
        result = recent_diagnostic.get('diagnosis_result', '').lower()
        if any(word in result for word in ['异常', '问题', '疾病', 'abnormal', 'disease']):
            return 60.0 * confidence
        else:
            return 90.0 * confidence
    
    async def generate_recommendations(self, user_data: Dict[str, Any]) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 基于生命体征的建议
        vital_signs = user_data.get('vital_signs', {})
        if vital_signs:
            recommendations.extend(await self._vital_signs_recommendations(vital_signs))
        
        # 基于异常的建议
        anomalies = user_data.get('anomalies', [])
        if anomalies:
            recommendations.extend(await self._anomaly_recommendations(anomalies))
        
        # 基于趋势的建议
        trends = user_data.get('trends', {})
        if trends:
            recommendations.extend(await self._trend_recommendations(trends))
        
        # 通用健康建议
        recommendations.extend([
            "保持规律作息，每天7-8小时睡眠",
            "适量运动，每周至少150分钟中等强度运动",
            "均衡饮食，多吃蔬菜水果，少吃高盐高糖食物",
            "定期体检，及时发现健康问题"
        ])
        
        # 去重并限制数量
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:8]
    
    async def _vital_signs_recommendations(self, vital_signs: Dict[str, Any]) -> List[str]:
        """基于生命体征的建议"""
        recommendations = []
        
        heart_rate = vital_signs.get('heart_rate')
        if heart_rate:
            if heart_rate > 100:
                recommendations.append("心率偏高，建议减少咖啡因摄入，保持放松")
            elif heart_rate < 60:
                recommendations.append("心率偏低，如有不适请咨询医生")
        
        bp_systolic = vital_signs.get('blood_pressure_systolic')
        if bp_systolic and bp_systolic > 140:
            recommendations.append("血压偏高，建议低盐饮食，适量运动")
        
        temperature = vital_signs.get('temperature')
        if temperature and temperature > 37.5:
            recommendations.append("体温偏高，注意休息，多喝水")
        
        return recommendations
    
    async def _anomaly_recommendations(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """基于异常的建议"""
        recommendations = []
        
        severe_anomalies = [a for a in anomalies if a.get('severity')=='severe']
        if severe_anomalies:
            recommendations.append("检测到严重异常指标，建议尽快咨询医生")
        
        moderate_anomalies = [a for a in anomalies if a.get('severity')=='moderate']
        if moderate_anomalies:
            recommendations.append("部分指标异常，建议关注并定期监测")
        
        return recommendations
    
    async def _trend_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """基于趋势的建议"""
        recommendations = []
        
        direction = trends.get('trend_direction')
        if direction=='increasing':
            recommendations.append("指标呈上升趋势，请持续关注")
        elif direction=='decreasing':
            recommendations.append("指标呈下降趋势，建议分析原因")
        
        return recommendations