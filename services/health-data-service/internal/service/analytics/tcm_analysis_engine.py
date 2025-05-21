#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医数据分析引擎
用于基于多模态健康数据和中医四诊数据进行体质辨识
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from internal.model.health_data import HealthDataType, TCMConstitutionType

logger = logging.getLogger(__name__)

# 中医体质评分权重配置
TCM_CONSTITUTION_WEIGHTS = {
    # 四诊权重
    "inspection": 0.3,  # 望诊
    "auscultation": 0.2,  # 闻诊
    "inquiry": 0.3,  # 问诊
    "palpation": 0.2,  # 切诊
    
    # 各数据类型权重
    "data_types": {
        HealthDataType.PULSE.value: 0.15,
        HealthDataType.TONGUE.value: 0.15,
        HealthDataType.FACE.value: 0.10,
        HealthDataType.VOICE.value: 0.10,
        HealthDataType.SYMPTOM.value: 0.20,
        HealthDataType.HEART_RATE.value: 0.05,
        HealthDataType.SLEEP.value: 0.05,
        HealthDataType.BLOOD_PRESSURE.value: 0.05,
        HealthDataType.BODY_TEMPERATURE.value: 0.05,
        HealthDataType.BLOOD_GLUCOSE.value: 0.05,
        HealthDataType.ACTIVITY.value: 0.05
    }
}

# 中医体质特征映射
TCM_CONSTITUTION_FEATURES = {
    TCMConstitutionType.BALANCED.value: {
        "pulse_features": ["smooth", "moderate", "regular"],
        "tongue_features": ["normal_color", "normal_coating", "moderate_size"],
        "face_features": ["normal_complexion", "lustrous"],
        "voice_features": ["clear", "moderate_volume"],
        "symptom_features": ["good_sleep", "normal_appetite", "regular_bowel"]
    },
    TCMConstitutionType.QI_DEFICIENCY.value: {
        "pulse_features": ["weak", "soft", "empty"],
        "tongue_features": ["pale", "teeth_marks", "thin_coating"],
        "face_features": ["pale", "puffy", "lack_luster"],
        "voice_features": ["weak", "low_volume", "shortness_of_breath"],
        "symptom_features": ["fatigue", "spontaneous_sweating", "poor_appetite"]
    },
    TCMConstitutionType.YANG_DEFICIENCY.value: {
        "pulse_features": ["deep", "slow", "weak"],
        "tongue_features": ["pale", "swollen", "wet_coating"],
        "face_features": ["pale", "puffy", "bright_white"],
        "voice_features": ["weak", "low_volume"],
        "symptom_features": ["cold_limbs", "cold_intolerance", "clear_urine"]
    },
    TCMConstitutionType.YIN_DEFICIENCY.value: {
        "pulse_features": ["thready", "rapid", "floating"],
        "tongue_features": ["red", "little_coating", "dry", "cracked"],
        "face_features": ["red_cheeks", "dry_skin"],
        "voice_features": ["dry", "hoarse"],
        "symptom_features": ["night_sweats", "dry_mouth", "heat_sensation"]
    },
    TCMConstitutionType.PHLEGM_DAMPNESS.value: {
        "pulse_features": ["slippery", "soft", "moderate"],
        "tongue_features": ["swollen", "teeth_marks", "thick_coating"],
        "face_features": ["oily", "puffy", "pale_yellow"],
        "voice_features": ["thick", "mucus_sound"],
        "symptom_features": ["heaviness", "sticky_phlegm", "poor_appetite"]
    },
    TCMConstitutionType.DAMPNESS_HEAT.value: {
        "pulse_features": ["rapid", "slippery", "forceful"],
        "tongue_features": ["red", "yellow_coating", "thick_coating"],
        "face_features": ["reddish", "oily", "yellow_hue"],
        "voice_features": ["loud", "thick"],
        "symptom_features": ["bitter_taste", "yellow_urine", "irritability"]
    },
    TCMConstitutionType.BLOOD_STASIS.value: {
        "pulse_features": ["choppy", "wiry", "hesitant"],
        "tongue_features": ["purple", "dark_spots", "distended_veins"],
        "face_features": ["dull_complexion", "purple_lips", "dark_patches"],
        "voice_features": ["weak", "sighing"],
        "symptom_features": ["fixed_pain", "dark_complexion", "irregular_periods"]
    },
    TCMConstitutionType.QI_DEPRESSION.value: {
        "pulse_features": ["wiry", "tight", "moderate"],
        "tongue_features": ["normal_color", "thin_coating", "teeth_marks"],
        "face_features": ["dull_complexion", "expression_of_depression"],
        "voice_features": ["sighing", "low_volume"],
        "symptom_features": ["irritability", "chest_distension", "irregular_bowel"]
    },
    TCMConstitutionType.SPECIAL.value: {
        "pulse_features": ["unique", "unusual", "variable"],
        "tongue_features": ["unusual_shape", "unusual_coating", "unusual_color"],
        "face_features": ["unusual_complexion", "asymmetric"],
        "voice_features": ["unusual_timbre", "variable"],
        "symptom_features": ["unusual_symptoms", "variable_patterns"]
    }
}


class TCMAnalysisEngine:
    """中医数据分析引擎"""
    
    def __init__(self):
        """初始化中医数据分析引擎"""
        # 特征权重配置
        self.weights = TCM_CONSTITUTION_WEIGHTS
        self.features = TCM_CONSTITUTION_FEATURES
    
    def analyze_constitution(self, 
                            user_id: str, 
                            health_data: List[Dict[str, Any]],
                            time_range: Optional[int] = 30) -> Dict[str, Any]:
        """分析用户中医体质
        
        Args:
            user_id: 用户ID
            health_data: 健康数据列表
            time_range: 分析的时间范围（天），默认30天
            
        Returns:
            Dict: 体质分析结果
        """
        logger.info(f"开始分析用户 {user_id} 的中医体质")
        
        # 过滤时间范围内的数据
        if time_range:
            cutoff_date = datetime.utcnow() - timedelta(days=time_range)
            filtered_data = [
                data for data in health_data 
                if datetime.fromisoformat(data.get("timestamp").replace("Z", "+00:00")) >= cutoff_date
            ]
        else:
            filtered_data = health_data
        
        if not filtered_data:
            logger.warning(f"用户 {user_id} 在指定时间范围内没有健康数据")
            return {
                "error": "insufficient_data",
                "message": "用户在指定时间范围内没有足够的健康数据进行分析"
            }
        
        # 按照中医四诊方法分组数据
        data_by_diagnosis = self._group_data_by_diagnosis(filtered_data)
        
        # 计算每种体质的得分
        constitution_scores = self._calculate_constitution_scores(data_by_diagnosis)
        
        # 确定主要体质和次要体质
        primary_type, secondary_types = self._determine_constitution_types(constitution_scores)
        
        # 生成分析依据
        analysis_basis = self._generate_analysis_basis(data_by_diagnosis, constitution_scores)
        
        # 生成体质调理建议
        recommendations = self._generate_recommendations(primary_type, secondary_types)
        
        # 构建分析结果
        result = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "primary_type": primary_type,
            "secondary_types": secondary_types,
            "scores": constitution_scores,
            "analysis_basis": analysis_basis,
            "recommendations": recommendations,
            "data_summary": {
                "data_count": len(filtered_data),
                "data_types": self._count_data_types(filtered_data),
                "time_range": {
                    "start": cutoff_date.isoformat() + "Z" if time_range else "all",
                    "end": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
        
        logger.info(f"用户 {user_id} 的中医体质分析完成，主要体质: {primary_type}")
        return result
    
    def _group_data_by_diagnosis(self, health_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """按照中医四诊方法分组健康数据
        
        Args:
            health_data: 健康数据列表
            
        Returns:
            Dict: 按四诊分组的健康数据
        """
        # 各诊法对应的数据类型
        diagnosis_mapping = {
            "inspection": [
                HealthDataType.FACE.value, 
                HealthDataType.TONGUE.value, 
                HealthDataType.BODY_MASS.value, 
                HealthDataType.BODY_FAT.value
            ],
            "auscultation": [
                HealthDataType.VOICE.value
            ],
            "inquiry": [
                HealthDataType.SYMPTOM.value, 
                HealthDataType.SLEEP.value, 
                HealthDataType.ACTIVITY.value, 
                HealthDataType.WATER_INTAKE.value, 
                HealthDataType.NUTRITION.value
            ],
            "palpation": [
                HealthDataType.PULSE.value, 
                HealthDataType.HEART_RATE.value, 
                HealthDataType.BLOOD_PRESSURE.value, 
                HealthDataType.BODY_TEMPERATURE.value, 
                HealthDataType.BLOOD_GLUCOSE.value
            ]
        }
        
        # 初始化分组数据
        grouped_data = {
            "inspection": [],
            "auscultation": [],
            "inquiry": [],
            "palpation": []
        }
        
        # 分组数据
        for data in health_data:
            data_type = data.get("data_type")
            for diagnosis, types in diagnosis_mapping.items():
                if data_type in types:
                    grouped_data[diagnosis].append(data)
                    break
        
        return grouped_data
    
    def _calculate_constitution_scores(self, 
                                      data_by_diagnosis: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
        """计算各种体质得分
        
        Args:
            data_by_diagnosis: 按四诊分组的健康数据
            
        Returns:
            Dict: 各种体质的得分
        """
        # 初始化各体质得分
        constitution_scores = {
            constitution_type: 0.0 
            for constitution_type in TCM_CONSTITUTION_FEATURES.keys()
        }
        
        # 计算各诊法的体质得分
        for diagnosis, data_list in data_by_diagnosis.items():
            if not data_list:
                continue
                
            # 该诊法的权重
            diagnosis_weight = self.weights.get(diagnosis, 0.25)
            
            # 计算该诊法下各体质的得分
            diagnosis_scores = self._calculate_diagnosis_scores(diagnosis, data_list)
            
            # 将该诊法的得分按权重加入总体质得分
            for constitution_type, score in diagnosis_scores.items():
                constitution_scores[constitution_type] += score * diagnosis_weight
        
        # 归一化体质得分（总分为100）
        total_score = sum(constitution_scores.values())
        if total_score > 0:
            for constitution_type in constitution_scores:
                constitution_scores[constitution_type] = round(constitution_scores[constitution_type] * 100 / total_score, 2)
        
        return constitution_scores
    
    def _calculate_diagnosis_scores(self, 
                                   diagnosis: str, 
                                   data_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算某诊法下各体质的得分
        
        Args:
            diagnosis: 诊法名称
            data_list: 该诊法的健康数据列表
            
        Returns:
            Dict: 该诊法下各体质的得分
        """
        # 初始化各体质在该诊法下的得分
        diagnosis_scores = {
            constitution_type: 0.0 
            for constitution_type in TCM_CONSTITUTION_FEATURES.keys()
        }
        
        # 按数据类型分组
        data_by_type = {}
        for data in data_list:
            data_type = data.get("data_type")
            if data_type not in data_by_type:
                data_by_type[data_type] = []
            data_by_type[data_type].append(data)
        
        # 计算各数据类型对各体质的贡献分
        for data_type, type_data_list in data_by_type.items():
            # 该数据类型的权重
            type_weight = self.weights["data_types"].get(data_type, 0.1)
            
            # 计算该数据类型下各体质的匹配度
            type_scores = self._calculate_feature_matching(data_type, type_data_list)
            
            # 将该数据类型的匹配度按权重加入诊法体质得分
            for constitution_type, score in type_scores.items():
                diagnosis_scores[constitution_type] += score * type_weight
        
        # 归一化该诊法下的体质得分
        total_score = sum(diagnosis_scores.values())
        if total_score > 0:
            for constitution_type in diagnosis_scores:
                diagnosis_scores[constitution_type] = diagnosis_scores[constitution_type] / total_score
        
        return diagnosis_scores
    
    def _calculate_feature_matching(self, 
                                   data_type: str, 
                                   data_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算数据类型与各体质特征的匹配度
        
        Args:
            data_type: 数据类型
            data_list: 该类型的健康数据列表
            
        Returns:
            Dict: 该数据类型与各体质的匹配度
        """
        # 初始化各体质的匹配度
        feature_scores = {
            constitution_type: 0.0 
            for constitution_type in TCM_CONSTITUTION_FEATURES.keys()
        }
        
        # 如果是中医特征数据类型
        if data_type in [HealthDataType.PULSE.value, HealthDataType.TONGUE.value, 
                        HealthDataType.FACE.value, HealthDataType.VOICE.value, 
                        HealthDataType.SYMPTOM.value]:
            
            # 提取特征字段
            feature_field = {
                HealthDataType.PULSE.value: "pulse_features",
                HealthDataType.TONGUE.value: "tongue_features",
                HealthDataType.FACE.value: "face_features",
                HealthDataType.VOICE.value: "voice_features",
                HealthDataType.SYMPTOM.value: "symptom_features"
            }.get(data_type)
            
            # 收集用户的所有特征
            user_features = set()
            for data in data_list:
                value = data.get("value", {})
                if isinstance(value, dict):
                    # 从JSON值中提取特征
                    features = value.get("features", [])
                    if isinstance(features, list):
                        user_features.update(features)
                elif isinstance(value, str):
                    # 尝试解析JSON字符串
                    try:
                        value_dict = json.loads(value)
                        features = value_dict.get("features", [])
                        if isinstance(features, list):
                            user_features.update(features)
                    except json.JSONDecodeError:
                        # 当作单个特征处理
                        user_features.add(value)
            
            # 计算与各体质的特征匹配度
            for constitution_type, constitution_features in TCM_CONSTITUTION_FEATURES.items():
                type_features = set(constitution_features.get(feature_field, []))
                if type_features:
                    # 计算交集比例作为匹配度
                    intersection = user_features.intersection(type_features)
                    match_ratio = len(intersection) / len(type_features) if type_features else 0
                    feature_scores[constitution_type] = match_ratio
        
        # 如果是常规健康数据类型
        else:
            # 各体质对常规健康指标的预期范围
            # 这里简化处理，实际应该有更复杂的指标范围映射
            normal_ranges = {
                TCMConstitutionType.BALANCED.value: {
                    HealthDataType.HEART_RATE.value: (60, 80),
                    HealthDataType.BODY_TEMPERATURE.value: (36.5, 37.0),
                    HealthDataType.BLOOD_PRESSURE.value: {"systolic": (110, 130), "diastolic": (70, 85)},
                    HealthDataType.SLEEP.value: (7, 9),
                    HealthDataType.ACTIVITY.value: (8000, 12000)
                }
            }
            
            # 填充其他体质的正常范围（简化处理）
            for constitution_type in feature_scores:
                if constitution_type not in normal_ranges:
                    normal_ranges[constitution_type] = normal_ranges[TCMConstitutionType.BALANCED.value].copy()
            
            # 根据数据与预期范围的偏差计算匹配度
            for constitution_type, ranges in normal_ranges.items():
                if data_type in ranges:
                    expected_range = ranges[data_type]
                    
                    # 计算数据与预期范围的匹配度
                    deviation_score = self._calculate_deviation_score(data_list, expected_range, data_type)
                    
                    # 转换为匹配度得分
                    feature_scores[constitution_type] = 1.0 - deviation_score
        
        # 归一化特征匹配度得分
        total_score = sum(feature_scores.values())
        if total_score > 0:
            for constitution_type in feature_scores:
                feature_scores[constitution_type] = feature_scores[constitution_type] / total_score
        
        return feature_scores
    
    def _calculate_deviation_score(self, 
                                  data_list: List[Dict[str, Any]], 
                                  expected_range: Any, 
                                  data_type: str) -> float:
        """计算数据与预期范围的偏差得分
        
        Args:
            data_list: 健康数据列表
            expected_range: 预期范围
            data_type: 数据类型
            
        Returns:
            float: 偏差得分（0-1，越小越匹配）
        """
        if not data_list:
            return 0.5  # 中性得分
        
        values = []
        
        # 提取数值
        for data in data_list:
            value = data.get("value")
            
            # 处理不同类型的值
            if isinstance(value, (int, float)):
                values.append(value)
            elif isinstance(value, dict):
                # 血压等复合指标
                if data_type == HealthDataType.BLOOD_PRESSURE.value:
                    systolic = value.get("systolic")
                    diastolic = value.get("diastolic")
                    if systolic is not None and diastolic is not None:
                        # 简化为平均偏差
                        systolic_range = expected_range["systolic"]
                        diastolic_range = expected_range["diastolic"]
                        
                        systolic_dev = min(max(0, systolic - systolic_range[1]), systolic_range[0] - systolic)
                        diastolic_dev = min(max(0, diastolic - diastolic_range[1]), diastolic_range[0] - diastolic)
                        
                        deviation = (systolic_dev + diastolic_dev) / 2
                        return min(1.0, deviation / 20)  # 假设20 mmHg偏差为显著
            elif isinstance(value, str):
                try:
                    numeric_value = float(value)
                    values.append(numeric_value)
                except ValueError:
                    pass
        
        if not values:
            return 0.5  # 中性得分
        
        # 计算平均值
        avg_value = sum(values) / len(values)
        
        # 计算与预期范围的偏差
        if isinstance(expected_range, tuple) and len(expected_range) == 2:
            min_val, max_val = expected_range
            if avg_value < min_val:
                deviation = min_val - avg_value
                range_width = max_val - min_val
                return min(1.0, deviation / range_width)
            elif avg_value > max_val:
                deviation = avg_value - max_val
                range_width = max_val - min_val
                return min(1.0, deviation / range_width)
            else:
                return 0.0  # 在范围内，无偏差
        
        return 0.5  # 默认中性得分
    
    def _determine_constitution_types(self, 
                                     scores: Dict[str, float]) -> Tuple[str, List[str]]:
        """确定主要体质和次要体质
        
        Args:
            scores: 各体质得分
            
        Returns:
            Tuple: (主要体质, [次要体质列表])
        """
        # 按得分排序
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 主要体质是得分最高的
        primary_type = sorted_scores[0][0]
        
        # 次要体质是得分超过平均值且不是主要体质的
        avg_score = sum(scores.values()) / len(scores)
        secondary_types = [
            constitution_type 
            for constitution_type, score in sorted_scores[1:] 
            if score > avg_score and score > 10.0  # 至少10分
        ]
        
        return primary_type, secondary_types
    
    def _generate_analysis_basis(self, 
                                data_by_diagnosis: Dict[str, List[Dict[str, Any]]], 
                                scores: Dict[str, float]) -> Dict[str, Any]:
        """生成分析依据
        
        Args:
            data_by_diagnosis: 按四诊分组的健康数据
            scores: 各体质得分
            
        Returns:
            Dict: 分析依据
        """
        analysis_basis = {
            "diagnosis_summary": {},
            "key_indicators": {},
            "constitution_evidence": {}
        }
        
        # 四诊数据摘要
        for diagnosis, data_list in data_by_diagnosis.items():
            if data_list:
                data_types = {}
                for data in data_list:
                    data_type = data.get("data_type")
                    if data_type not in data_types:
                        data_types[data_type] = 0
                    data_types[data_type] += 1
                
                analysis_basis["diagnosis_summary"][diagnosis] = {
                    "data_count": len(data_list),
                    "data_types": data_types
                }
        
        # 关键健康指标
        key_indicators = {
            HealthDataType.HEART_RATE.value: "心率",
            HealthDataType.BLOOD_PRESSURE.value: "血压",
            HealthDataType.BODY_TEMPERATURE.value: "体温",
            HealthDataType.SLEEP.value: "睡眠",
            HealthDataType.ACTIVITY.value: "活动"
        }
        
        for data_type, name in key_indicators.items():
            data_list = [
                data for diagnosis in data_by_diagnosis.values()
                for data in diagnosis
                if data.get("data_type") == data_type
            ]
            
            if data_list:
                values = []
                for data in data_list:
                    value = data.get("value")
                    if isinstance(value, (int, float)):
                        values.append(value)
                    elif isinstance(value, dict) and "value" in value:
                        values.append(value["value"])
                
                if values:
                    analysis_basis["key_indicators"][data_type] = {
                        "name": name,
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
        
        # 体质证据
        # 获取得分前三的体质
        top_constitutions = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for constitution_type, score in top_constitutions:
            # 收集该体质的特征匹配证据
            evidence = {}
            
            # 遍历四诊数据
            for diagnosis, data_list in data_by_diagnosis.items():
                diagnosis_evidence = []
                
                # 按数据类型分组
                data_by_type = {}
                for data in data_list:
                    data_type = data.get("data_type")
                    if data_type not in data_by_type:
                        data_by_type[data_type] = []
                    data_by_type[data_type].append(data)
                
                # 检查特征匹配
                for data_type, type_data_list in data_by_type.items():
                    if data_type in [HealthDataType.PULSE.value, HealthDataType.TONGUE.value, 
                                    HealthDataType.FACE.value, HealthDataType.VOICE.value, 
                                    HealthDataType.SYMPTOM.value]:
                        
                        feature_field = {
                            HealthDataType.PULSE.value: "pulse_features",
                            HealthDataType.TONGUE.value: "tongue_features",
                            HealthDataType.FACE.value: "face_features",
                            HealthDataType.VOICE.value: "voice_features",
                            HealthDataType.SYMPTOM.value: "symptom_features"
                        }.get(data_type)
                        
                        constitution_features = set(self.features[constitution_type].get(feature_field, []))
                        
                        # 收集用户特征
                        user_features = set()
                        for data in type_data_list:
                            value = data.get("value", {})
                            if isinstance(value, dict):
                                features = value.get("features", [])
                                if isinstance(features, list):
                                    user_features.update(features)
                        
                        # 查找匹配的特征
                        matched_features = user_features.intersection(constitution_features)
                        if matched_features:
                            diagnosis_evidence.append({
                                "data_type": data_type,
                                "matched_features": list(matched_features),
                                "expected_features": list(constitution_features)
                            })
                
                if diagnosis_evidence:
                    evidence[diagnosis] = diagnosis_evidence
            
            # 只有存在证据才添加
            if evidence:
                analysis_basis["constitution_evidence"][constitution_type] = evidence
        
        return analysis_basis
    
    def _generate_recommendations(self, 
                                 primary_type: str, 
                                 secondary_types: List[str]) -> Dict[str, Any]:
        """生成体质调理建议
        
        Args:
            primary_type: 主要体质
            secondary_types: 次要体质列表
            
        Returns:
            Dict: 调理建议
        """
        # 构建基础建议模板
        base_recommendations = {
            "diet": [],
            "lifestyle": [],
            "exercise": [],
            "meridian_acupoints": [],
            "herbs": []
        }
        
        # 各体质的调理建议
        constitution_recommendations = {
            TCMConstitutionType.BALANCED.value: {
                "diet": [
                    "饮食有节制，不偏食",
                    "清淡饮食，少油腻",
                    "五谷杂粮搭配均衡"
                ],
                "lifestyle": [
                    "作息规律，早睡早起",
                    "保持心情舒畅",
                    "适当参加社交活动"
                ],
                "exercise": [
                    "每天适量运动30-60分钟",
                    "太极、八段锦、五禽戏等传统养生功法",
                    "散步、慢跑等有氧运动"
                ],
                "meridian_acupoints": [
                    "按摩足三里穴位增强脾胃功能",
                    "揉捏涌泉穴补益肾气",
                    "常搓手掌强身健体"
                ],
                "herbs": [
                    "可常饮菊花茶清热明目",
                    "绿茶有助于消脂减肥",
                    "山楂茶帮助消食"
                ]
            },
            TCMConstitutionType.QI_DEFICIENCY.value: {
                "diet": [
                    "多食黄豆、大枣、山药等补气食物",
                    "多食温补食物，如鸡肉、羊肉",
                    "少食生冷食物，避免过度耗气"
                ],
                "lifestyle": [
                    "保持充足睡眠，避免过度劳累",
                    "适当午休，调养正气",
                    "避免情绪波动，保持心情舒畅"
                ],
                "exercise": [
                    "循序渐进地进行运动，不宜过度",
                    "八段锦、太极等传统养生功法",
                    "深呼吸练习，增加肺活量"
                ],
                "meridian_acupoints": [
                    "常按足三里、气海、关元等穴位",
                    "揉捏涌泉穴补益肾气",
                    "按摩中脘穴健脾和胃"
                ],
                "herbs": [
                    "可服用党参茶、黄芪茶等补气",
                    "山药粥、枸杞粥有助于补益气血",
                    "石斛、沙参等滋阴润肺"
                ]
            },
            TCMConstitutionType.YANG_DEFICIENCY.value: {
                "diet": [
                    "多食温补食物，如羊肉、狗肉等",
                    "适量食用桂圆、核桃等温补食材",
                    "少食寒凉食物，如梨、西瓜等"
                ],
                "lifestyle": [
                    "注意保暖，特别是腰腹部和脚部",
                    "避免受寒，少待空调房",
                    "保持充足睡眠，避免熬夜"
                ],
                "exercise": [
                    "适量进行有氧运动，如慢跑、散步",
                    "八段锦中的"双手托天理三焦"",
                    "六字诀中的"嘘"字诀温补肝阳"
                ],
                "meridian_acupoints": [
                    "经常按摩命门穴温补肾阳",
                    "艾灸关元、气海等穴位",
                    "温灸涌泉穴补肾壮阳"
                ],
                "herbs": [
                    "肉桂茶温补阳气",
                    "杜仲、续断等补肾壮腰",
                    "附子理中丸温中散寒"
                ]
            }
        }
        
        # 添加其他体质的建议（此处略）
        # ...
        
        # 合并主要体质和次要体质的建议
        recommendations = base_recommendations.copy()
        
        # 添加主要体质的建议
        if primary_type in constitution_recommendations:
            primary_recs = constitution_recommendations[primary_type]
            for category, items in primary_recs.items():
                recommendations[category].extend(items)
        
        # 添加次要体质的部分建议
        for secondary_type in secondary_types:
            if secondary_type in constitution_recommendations:
                secondary_recs = constitution_recommendations[secondary_type]
                for category, items in secondary_recs.items():
                    # 只添加前两条建议，避免过多
                    recommendations[category].extend(items[:2])
        
        # 限制每个类别的建议数量，避免过多
        for category in recommendations:
            recommendations[category] = list(set(recommendations[category]))[:5]
        
        # 添加综合调理建议
        recommendations["general"] = [
            "建议定期进行中医体质检测，了解体质变化",
            "根据季节变化适时调整饮食与起居",
            "保持心情舒畅，情志安宁",
            "适当参加户外活动，接触阳光和自然"
        ]
        
        return recommendations
    
    def _count_data_types(self, health_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """统计各类型数据的数量
        
        Args:
            health_data: 健康数据列表
            
        Returns:
            Dict: 各类型数据的数量
        """
        counts = {}
        for data in health_data:
            data_type = data.get("data_type")
            if data_type not in counts:
                counts[data_type] = 0
            counts[data_type] += 1
        return counts 