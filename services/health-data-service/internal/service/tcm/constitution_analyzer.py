#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医体质分析器
基于健康数据进行中医体质辨识和分析
"""

import asyncio
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from loguru import logger

from ...model.health_data import HealthData, HealthDataType, DeviceType, MeasurementUnit


@dataclass
class ConstitutionScore:
    """体质得分"""
    constitution_type: str  # 体质类型
    score: float           # 得分 0-100
    confidence: float      # 置信度 0-1
    characteristics: List[str]  # 特征描述
    recommendations: List[str]  # 调理建议


@dataclass
class ConstitutionAnalysis:
    """体质分析结果"""
    primary_constitution: ConstitutionScore    # 主要体质
    secondary_constitution: Optional[ConstitutionScore]  # 次要体质
    all_scores: List[ConstitutionScore]       # 所有体质得分
    analysis_date: datetime                   # 分析日期
    data_period_days: int                     # 数据周期
    reliability: float                        # 分析可靠性


class TCMConstitutionAnalyzer:
    """中医体质分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化体质分析器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.is_initialized = False
        
        # 九种体质类型
        self.constitution_types = [
            "平和质",    # 正常体质
            "气虚质",    # 气虚体质
            "阳虚质",    # 阳虚体质
            "阴虚质",    # 阴虚体质
            "痰湿质",    # 痰湿体质
            "湿热质",    # 湿热体质
            "血瘀质",    # 血瘀体质
            "气郁质",    # 气郁体质
            "特禀质"     # 特禀体质
        ]
        
        # 体质特征权重
        self.constitution_weights = {}
        
        # 健康指标与体质的关联规则
        self.constitution_rules = {}
    
    async def initialize(self) -> None:
        """初始化分析器"""
        if self.is_initialized:
            return
        
        await self._load_constitution_rules()
        await self._load_constitution_weights()
        self.is_initialized = True
        logger.info("中医体质分析器初始化完成")
    
    async def _load_constitution_rules(self) -> None:
        """加载体质辨识规则"""
        self.constitution_rules = {
            # 平和质 - 正常体质
            "平和质": {
                "heart_rate": {
                    "optimal_range": (60, 80),
                    "weight": 0.15,
                    "description": "心率平稳，气血调和"
                },
                "blood_pressure": {
                    "optimal_systolic": (110, 130),
                    "optimal_diastolic": (70, 85),
                    "weight": 0.20,
                    "description": "血压正常，脉象有力"
                },
                "sleep": {
                    "optimal_duration": (7, 8.5),
                    "optimal_quality": (80, 100),
                    "weight": 0.15,
                    "description": "睡眠充足，精神饱满"
                },
                "steps": {
                    "optimal_range": (8000, 15000),
                    "weight": 0.10,
                    "description": "活动适度，体力充沛"
                },
                "body_temperature": {
                    "optimal_range": (36.2, 37.0),
                    "weight": 0.10,
                    "description": "体温正常，阴阳平衡"
                }
            },
            
            # 气虚质
            "气虚质": {
                "heart_rate": {
                    "characteristic_range": (50, 70),  # 心率偏慢
                    "weight": 0.20,
                    "description": "心率偏慢，气血不足"
                },
                "blood_pressure": {
                    "characteristic_systolic": (90, 110),  # 血压偏低
                    "characteristic_diastolic": (60, 75),
                    "weight": 0.25,
                    "description": "血压偏低，脉象无力"
                },
                "steps": {
                    "characteristic_range": (3000, 7000),  # 活动量少
                    "weight": 0.15,
                    "description": "容易疲劳，活动量少"
                },
                "sleep": {
                    "characteristic_duration": (8, 10),  # 睡眠时间长但质量不高
                    "characteristic_quality": (40, 70),
                    "weight": 0.15,
                    "description": "睡眠时间长但易醒"
                },
                "oxygen_saturation": {
                    "characteristic_range": (92, 96),  # 血氧偏低
                    "weight": 0.10,
                    "description": "血氧偏低，气虚明显"
                }
            },
            
            # 阳虚质
            "阳虚质": {
                "body_temperature": {
                    "characteristic_range": (35.8, 36.5),  # 体温偏低
                    "weight": 0.30,
                    "description": "体温偏低，阳气不足"
                },
                "heart_rate": {
                    "characteristic_range": (55, 75),  # 心率偏慢
                    "weight": 0.20,
                    "description": "心率偏慢，心阳不振"
                },
                "blood_pressure": {
                    "characteristic_systolic": (85, 105),  # 血压偏低
                    "characteristic_diastolic": (55, 70),
                    "weight": 0.20,
                    "description": "血压偏低，阳气虚弱"
                },
                "steps": {
                    "characteristic_range": (2000, 6000),  # 活动量少
                    "weight": 0.15,
                    "description": "畏寒怕冷，活动减少"
                }
            },
            
            # 阴虚质
            "阴虚质": {
                "body_temperature": {
                    "characteristic_range": (36.8, 37.5),  # 体温偏高
                    "weight": 0.25,
                    "description": "体温偏高，阴虚内热"
                },
                "heart_rate": {
                    "characteristic_range": (80, 100),  # 心率偏快
                    "weight": 0.25,
                    "description": "心率偏快，阴虚火旺"
                },
                "sleep": {
                    "characteristic_duration": (5, 7),  # 睡眠时间短
                    "characteristic_quality": (30, 60),  # 睡眠质量差
                    "weight": 0.20,
                    "description": "失眠多梦，睡眠不安"
                },
                "blood_pressure": {
                    "characteristic_systolic": (130, 150),  # 血压偏高
                    "characteristic_diastolic": (85, 95),
                    "weight": 0.15,
                    "description": "血压偏高，阴虚阳亢"
                }
            },
            
            # 痰湿质
            "痰湿质": {
                "steps": {
                    "characteristic_range": (2000, 5000),  # 活动量少
                    "weight": 0.25,
                    "description": "身体沉重，不喜运动"
                },
                "sleep": {
                    "characteristic_duration": (8.5, 11),  # 睡眠时间长
                    "characteristic_quality": (50, 75),
                    "weight": 0.20,
                    "description": "嗜睡，睡不解乏"
                },
                "heart_rate": {
                    "characteristic_range": (65, 85),  # 心率正常偏慢
                    "weight": 0.15,
                    "description": "心率平缓，痰湿困脾"
                },
                "blood_pressure": {
                    "characteristic_systolic": (120, 140),  # 血压正常偏高
                    "characteristic_diastolic": (80, 90),
                    "weight": 0.20,
                    "description": "血压偏高，痰湿内阻"
                }
            },
            
            # 湿热质
            "湿热质": {
                "body_temperature": {
                    "characteristic_range": (36.8, 37.3),  # 体温偏高
                    "weight": 0.25,
                    "description": "体温偏高，湿热内蕴"
                },
                "heart_rate": {
                    "characteristic_range": (75, 95),  # 心率偏快
                    "weight": 0.20,
                    "description": "心率偏快，湿热扰心"
                },
                "blood_pressure": {
                    "characteristic_systolic": (125, 145),  # 血压偏高
                    "characteristic_diastolic": (80, 95),
                    "weight": 0.20,
                    "description": "血压偏高，湿热上扰"
                },
                "sleep": {
                    "characteristic_duration": (6, 8),
                    "characteristic_quality": (40, 70),  # 睡眠质量差
                    "weight": 0.15,
                    "description": "睡眠不安，湿热扰神"
                }
            },
            
            # 血瘀质
            "血瘀质": {
                "heart_rate": {
                    "characteristic_range": (70, 90),
                    "weight": 0.20,
                    "description": "心率不齐，血行不畅"
                },
                "blood_pressure": {
                    "characteristic_systolic": (120, 140),
                    "characteristic_diastolic": (80, 95),
                    "weight": 0.25,
                    "description": "血压偏高，血瘀阻络"
                },
                "steps": {
                    "characteristic_range": (4000, 8000),
                    "weight": 0.15,
                    "description": "活动受限，血瘀疼痛"
                },
                "sleep": {
                    "characteristic_quality": (30, 60),  # 睡眠质量差
                    "weight": 0.15,
                    "description": "睡眠不佳，血瘀扰神"
                }
            },
            
            # 气郁质
            "气郁质": {
                "heart_rate": {
                    "characteristic_range": (75, 95),  # 心率波动大
                    "weight": 0.20,
                    "description": "心率不稳，情志不畅"
                },
                "sleep": {
                    "characteristic_duration": (5.5, 7.5),
                    "characteristic_quality": (25, 55),  # 睡眠质量很差
                    "weight": 0.30,
                    "description": "失眠多梦，情志抑郁"
                },
                "steps": {
                    "characteristic_range": (3000, 7000),  # 活动量不稳定
                    "weight": 0.15,
                    "description": "活动不规律，情绪影响"
                },
                "blood_pressure": {
                    "characteristic_systolic": (115, 135),
                    "characteristic_diastolic": (75, 90),
                    "weight": 0.15,
                    "description": "血压波动，气机不畅"
                }
            },
            
            # 特禀质
            "特禀质": {
                "heart_rate": {
                    "characteristic_range": (60, 100),  # 范围较宽
                    "weight": 0.15,
                    "description": "心率变异，体质特殊"
                },
                "sleep": {
                    "characteristic_quality": (30, 80),  # 质量不稳定
                    "weight": 0.20,
                    "description": "睡眠不稳，过敏体质"
                },
                "body_temperature": {
                    "characteristic_range": (36.0, 37.2),  # 体温波动
                    "weight": 0.15,
                    "description": "体温不稳，易过敏"
                }
            }
        }
    
    async def _load_constitution_weights(self) -> None:
        """加载体质权重配置"""
        self.constitution_weights = {
            "平和质": 1.0,    # 基准权重
            "气虚质": 0.9,
            "阳虚质": 0.9,
            "阴虚质": 0.9,
            "痰湿质": 0.85,
            "湿热质": 0.85,
            "血瘀质": 0.8,
            "气郁质": 0.8,
            "特禀质": 0.7     # 特殊体质权重较低
        }
    
    async def analyze_constitution(
        self,
        user_id: str,
        health_data_list: List[HealthData],
        days: int = 30
    ) -> ConstitutionAnalysis:
        """
        分析用户体质
        
        Args:
            user_id: 用户ID
            health_data_list: 健康数据列表
            days: 分析周期
            
        Returns:
            体质分析结果
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 按数据类型分组
        data_by_type = self._group_data_by_type(health_data_list)
        
        # 计算各体质得分
        constitution_scores = []
        
        for constitution_type in self.constitution_types:
            score = await self._calculate_constitution_score(
                constitution_type,
                data_by_type
            )
            constitution_scores.append(score)
        
        # 排序得分
        constitution_scores.sort(key=lambda x: x.score, reverse=True)
        
        # 确定主要和次要体质
        primary_constitution = constitution_scores[0]
        secondary_constitution = None
        
        # 如果第二高分与第一高分差距不大，则认为是混合体质
        if (len(constitution_scores) > 1 and 
            constitution_scores[1].score > 60 and
            primary_constitution.score - constitution_scores[1].score < 15):
            secondary_constitution = constitution_scores[1]
        
        # 计算分析可靠性
        reliability = self._calculate_reliability(health_data_list, days)
        
        return ConstitutionAnalysis(
            primary_constitution=primary_constitution,
            secondary_constitution=secondary_constitution,
            all_scores=constitution_scores,
            analysis_date=datetime.utcnow(),
            data_period_days=days,
            reliability=reliability
        )
    
    def _group_data_by_type(self, data_list: List[HealthData]) -> Dict[HealthDataType, List[HealthData]]:
        """按数据类型分组"""
        grouped = {}
        for data in data_list:
            if data.data_type not in grouped:
                grouped[data.data_type] = []
            grouped[data.data_type].append(data)
        return grouped
    
    async def _calculate_constitution_score(
        self,
        constitution_type: str,
        data_by_type: Dict[HealthDataType, List[HealthData]]
    ) -> ConstitutionScore:
        """计算特定体质的得分"""
        
        if constitution_type not in self.constitution_rules:
            return ConstitutionScore(
                constitution_type=constitution_type,
                score=0.0,
                confidence=0.0,
                characteristics=[],
                recommendations=[]
            )
        
        rules = self.constitution_rules[constitution_type]
        total_score = 0.0
        total_weight = 0.0
        matched_characteristics = []
        
        # 遍历该体质的所有规则
        for data_type_name, rule in rules.items():
            data_type = self._get_data_type_enum(data_type_name)
            if data_type and data_type in data_by_type:
                data_list = data_by_type[data_type]
                
                # 计算该数据类型的得分
                type_score = await self._calculate_type_score(
                    data_type,
                    data_list,
                    rule,
                    constitution_type
                )
                
                weight = rule.get('weight', 0.1)
                total_score += type_score * weight
                total_weight += weight
                
                # 如果得分较高，添加特征描述
                if type_score > 70:
                    matched_characteristics.append(rule.get('description', ''))
        
        # 计算最终得分
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        # 应用体质权重
        constitution_weight = self.constitution_weights.get(constitution_type, 1.0)
        final_score *= constitution_weight
        
        # 计算置信度
        confidence = min(total_weight, 1.0)
        
        # 生成调理建议
        recommendations = await self._generate_constitution_recommendations(
            constitution_type,
            final_score
        )
        
        return ConstitutionScore(
            constitution_type=constitution_type,
            score=final_score,
            confidence=confidence,
            characteristics=matched_characteristics,
            recommendations=recommendations
        )
    
    def _get_data_type_enum(self, data_type_name: str) -> Optional[HealthDataType]:
        """将字符串转换为数据类型枚举"""
        mapping = {
            'heart_rate': HealthDataType.HEART_RATE,
            'blood_pressure': HealthDataType.BLOOD_PRESSURE,
            'sleep': HealthDataType.SLEEP,
            'steps': HealthDataType.STEPS,
            'body_temperature': HealthDataType.BODY_TEMPERATURE,
            'oxygen_saturation': HealthDataType.OXYGEN_SATURATION,
            'blood_glucose': HealthDataType.BLOOD_GLUCOSE
        }
        return mapping.get(data_type_name)
    
    async def _calculate_type_score(
        self,
        data_type: HealthDataType,
        data_list: List[HealthData],
        rule: Dict[str, Any],
        constitution_type: str
    ) -> float:
        """计算特定数据类型的体质得分"""
        
        if not data_list:
            return 0.0
        
        # 提取数值
        values = []
        for data in data_list:
            if data_type == HealthDataType.BLOOD_PRESSURE:
                # 血压数据特殊处理
                if isinstance(data.value, dict):
                    systolic = data.value.get('systolic')
                    diastolic = data.value.get('diastolic')
                    if systolic and diastolic:
                        values.append({'systolic': systolic, 'diastolic': diastolic})
            elif data_type == HealthDataType.SLEEP:
                # 睡眠数据特殊处理
                if isinstance(data.value, dict):
                    duration = data.value.get('duration')
                    quality = data.value.get('quality')
                    if duration:
                        values.append({'duration': duration, 'quality': quality or 50})
                elif isinstance(data.value, (int, float)):
                    values.append({'duration': float(data.value), 'quality': 50})
            else:
                # 其他数据类型
                if isinstance(data.value, (int, float)):
                    values.append(float(data.value))
        
        if not values:
            return 0.0
        
        # 根据数据类型计算得分
        if data_type == HealthDataType.BLOOD_PRESSURE:
            return self._calculate_blood_pressure_score(values, rule, constitution_type)
        elif data_type == HealthDataType.SLEEP:
            return self._calculate_sleep_score(values, rule, constitution_type)
        else:
            return self._calculate_numeric_score(values, rule, constitution_type)
    
    def _calculate_blood_pressure_score(
        self,
        values: List[Dict[str, float]],
        rule: Dict[str, Any],
        constitution_type: str
    ) -> float:
        """计算血压得分"""
        if not values:
            return 0.0
        
        systolic_values = [v['systolic'] for v in values]
        diastolic_values = [v['diastolic'] for v in values]
        
        avg_systolic = statistics.mean(systolic_values)
        avg_diastolic = statistics.mean(diastolic_values)
        
        score = 0.0
        
        # 检查是否有特征范围（偏离正常的范围）
        if 'characteristic_systolic' in rule:
            sys_range = rule['characteristic_systolic']
            dia_range = rule['characteristic_diastolic']
            
            # 计算匹配度
            sys_match = self._calculate_range_match(avg_systolic, sys_range)
            dia_match = self._calculate_range_match(avg_diastolic, dia_range)
            
            score = (sys_match + dia_match) / 2 * 100
        
        # 检查是否有最优范围（平和质）
        elif 'optimal_systolic' in rule:
            sys_range = rule['optimal_systolic']
            dia_range = rule['optimal_diastolic']
            
            sys_match = self._calculate_range_match(avg_systolic, sys_range)
            dia_match = self._calculate_range_match(avg_diastolic, dia_range)
            
            score = (sys_match + dia_match) / 2 * 100
        
        return score
    
    def _calculate_sleep_score(
        self,
        values: List[Dict[str, float]],
        rule: Dict[str, Any],
        constitution_type: str
    ) -> float:
        """计算睡眠得分"""
        if not values:
            return 0.0
        
        durations = [v['duration'] for v in values]
        qualities = [v['quality'] for v in values if v['quality'] is not None]
        
        avg_duration = statistics.mean(durations)
        avg_quality = statistics.mean(qualities) if qualities else 50
        
        score = 0.0
        
        # 检查睡眠时长
        if 'characteristic_duration' in rule:
            duration_range = rule['characteristic_duration']
            duration_match = self._calculate_range_match(avg_duration, duration_range)
            score += duration_match * 60  # 时长占60%
        elif 'optimal_duration' in rule:
            duration_range = rule['optimal_duration']
            duration_match = self._calculate_range_match(avg_duration, duration_range)
            score += duration_match * 60
        
        # 检查睡眠质量
        if 'characteristic_quality' in rule:
            quality_range = rule['characteristic_quality']
            quality_match = self._calculate_range_match(avg_quality, quality_range)
            score += quality_match * 40  # 质量占40%
        elif 'optimal_quality' in rule:
            quality_range = rule['optimal_quality']
            quality_match = self._calculate_range_match(avg_quality, quality_range)
            score += quality_match * 40
        
        return score
    
    def _calculate_numeric_score(
        self,
        values: List[float],
        rule: Dict[str, Any],
        constitution_type: str
    ) -> float:
        """计算数值型数据得分"""
        if not values:
            return 0.0
        
        avg_value = statistics.mean(values)
        
        # 检查特征范围
        if 'characteristic_range' in rule:
            range_tuple = rule['characteristic_range']
            match = self._calculate_range_match(avg_value, range_tuple)
            return match * 100
        
        # 检查最优范围
        elif 'optimal_range' in rule:
            range_tuple = rule['optimal_range']
            match = self._calculate_range_match(avg_value, range_tuple)
            return match * 100
        
        return 0.0
    
    def _calculate_range_match(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """计算值与范围的匹配度"""
        min_val, max_val = range_tuple
        
        if min_val <= value <= max_val:
            # 在范围内，计算距离中心的程度
            center = (min_val + max_val) / 2
            range_width = max_val - min_val
            distance_from_center = abs(value - center)
            
            # 距离中心越近，匹配度越高
            match = 1.0 - (distance_from_center / (range_width / 2))
            return max(0.8, match)  # 在范围内至少0.8的匹配度
        else:
            # 在范围外，计算距离范围的程度
            if value < min_val:
                distance = min_val - value
                tolerance = (max_val - min_val) * 0.5  # 容忍度为范围宽度的50%
            else:
                distance = value - max_val
                tolerance = (max_val - min_val) * 0.5
            
            # 距离越远，匹配度越低
            if distance <= tolerance:
                match = 1.0 - (distance / tolerance) * 0.8  # 最多降低0.8
                return max(0.0, match)
            else:
                return 0.0
    
    async def _generate_constitution_recommendations(
        self,
        constitution_type: str,
        score: float
    ) -> List[str]:
        """生成体质调理建议"""
        
        recommendations_map = {
            "平和质": [
                "保持现有的良好生活习惯",
                "适度运动，如太极拳、八段锦",
                "饮食均衡，五谷杂粮搭配",
                "保持心情愉悦，避免过度劳累"
            ],
            
            "气虚质": [
                "多食补气食物：人参、黄芪、山药、大枣",
                "避免剧烈运动，适合缓和运动如散步、太极",
                "保证充足睡眠，避免熬夜",
                "可进行艾灸调理，重点穴位：足三里、关元"
            ],
            
            "阳虚质": [
                "多食温阳食物：羊肉、生姜、肉桂、核桃",
                "避免生冷食物，注意保暖",
                "适合温和运动，如慢跑、瑜伽",
                "可进行温灸调理，重点穴位：命门、肾俞、关元"
            ],
            
            "阴虚质": [
                "多食滋阴食物：银耳、百合、枸杞、梨",
                "避免辛辣燥热食物，少熬夜",
                "适合静态运动，如瑜伽、太极",
                "保持环境湿润，避免过度用眼"
            ],
            
            "痰湿质": [
                "多食健脾化湿食物：薏米、冬瓜、白萝卜",
                "避免甜腻油腻食物，控制体重",
                "增加有氧运动，如快走、游泳",
                "保持环境干燥，避免潮湿"
            ],
            
            "湿热质": [
                "多食清热利湿食物：绿豆、苦瓜、茯苓",
                "避免辛辣油腻食物，戒烟限酒",
                "适合强度适中的运动，如跑步、球类",
                "保持心情舒畅，避免情绪激动"
            ],
            
            "血瘀质": [
                "多食活血化瘀食物：山楂、黑木耳、红花茶",
                "避免久坐久立，适度运动促进血液循环",
                "可进行按摩、刮痧等物理疗法",
                "保持心情愉悦，避免情志抑郁"
            ],
            
            "气郁质": [
                "多食疏肝理气食物：玫瑰花茶、柑橘、佛手",
                "避免情绪压抑，多与人交流",
                "适合舒缓运动，如瑜伽、太极、散步",
                "培养兴趣爱好，保持心情愉悦"
            ],
            
            "特禀质": [
                "避免接触过敏原，注意环境卫生",
                "饮食清淡，避免易过敏食物",
                "适度运动增强体质，避免过度疲劳",
                "可进行脱敏治疗，提高免疫力"
            ]
        }
        
        base_recommendations = recommendations_map.get(constitution_type, [])
        
        # 根据得分调整建议
        if score > 80:
            return base_recommendations[:2]  # 高分时给出重点建议
        elif score > 60:
            return base_recommendations[:3]  # 中等分数给出更多建议
        else:
            return base_recommendations  # 低分时给出全部建议
    
    def _calculate_reliability(self, health_data_list: List[HealthData], days: int) -> float:
        """计算分析可靠性"""
        if not health_data_list:
            return 0.0
        
        # 数据量因子
        data_count_factor = min(len(health_data_list) / 100, 1.0)  # 100条数据为满分
        
        # 数据类型多样性因子
        data_types = set(data.data_type for data in health_data_list)
        type_diversity_factor = min(len(data_types) / 5, 1.0)  # 5种类型为满分
        
        # 时间跨度因子
        time_span_factor = min(days / 30, 1.0)  # 30天为满分
        
        # 数据质量因子（如果有质量评分）
        quality_scores = []
        for data in health_data_list:
            if hasattr(data, 'quality_score') and data.quality_score is not None:
                quality_scores.append(data.quality_score)
        
        if quality_scores:
            quality_factor = statistics.mean(quality_scores)
        else:
            quality_factor = 0.8  # 默认质量
        
        # 综合可靠性
        reliability = (
            data_count_factor * 0.3 +
            type_diversity_factor * 0.3 +
            time_span_factor * 0.2 +
            quality_factor * 0.2
        )
        
        return reliability
    
    async def get_constitution_description(self, constitution_type: str) -> Dict[str, Any]:
        """获取体质详细描述"""
        
        descriptions = {
            "平和质": {
                "name": "平和质",
                "description": "阴阳气血调和，体质平和",
                "characteristics": [
                    "体形匀称健壮",
                    "面色润泽，头发稠密有光泽",
                    "目光有神，鼻色明润",
                    "嗅觉、味觉正常",
                    "唇色红润，不易疲劳",
                    "精力充沛，耐受寒热",
                    "睡眠良好，胃纳佳",
                    "二便正常，舌色淡红，苔薄白",
                    "脉和缓有力"
                ],
                "susceptible_diseases": ["较少生病"],
                "adjustment_methods": [
                    "保持良好的生活习惯",
                    "适度运动",
                    "均衡饮食",
                    "心情愉悦"
                ]
            },
            
            "气虚质": {
                "name": "气虚质",
                "description": "元气不足，气息低弱",
                "characteristics": [
                    "肌肉不健壮",
                    "平素语音低怯，气短懒言",
                    "容易疲乏，精神不振",
                    "易出汗，活动时尤甚",
                    "舌淡红，舌边有齿痕",
                    "脉弱"
                ],
                "susceptible_diseases": [
                    "感冒",
                    "内脏下垂",
                    "虚劳证"
                ],
                "adjustment_methods": [
                    "补气养气",
                    "避免剧烈运动",
                    "保证充足睡眠",
                    "艾灸调理"
                ]
            }
            # ... 其他体质描述
        }
        
        return descriptions.get(constitution_type, {
            "name": constitution_type,
            "description": "体质类型描述",
            "characteristics": [],
            "susceptible_diseases": [],
            "adjustment_methods": []
        }) 