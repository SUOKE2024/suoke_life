#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医体质分析引擎，负责分析用户健康数据、四诊数据，判断中医体质类型
"""

import uuid
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import json
import math
import numpy as np
from loguru import logger

from ...model.health_data import (
    HealthDataType, TCMConstitutionType, HealthData,
    TCMConstitutionData, DeviceType
)


class TCMConstitutionAnalyzer:
    """中医体质分析引擎类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化中医体质分析引擎
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.constitution_types = [t.value for t in TCMConstitutionType]
        self.models = {}
        self.feature_weights = self._load_feature_weights()
        self.diagnostic_weights = {
            "inquiry": 0.35,    # 问诊权重
            "inspection": 0.30, # 望诊权重
            "auscultation": 0.15, # 闻诊权重
            "palpation": 0.20,  # 切诊权重
        }
        logger.info("中医体质分析引擎初始化完成")
    
    def _load_feature_weights(self) -> Dict[str, Dict[str, float]]:
        """
        加载特征权重
        
        Returns:
            特征权重字典
        """
        try:
            # 实际应用中应该从配置文件或数据库加载
            return {
                TCMConstitutionType.BALANCED.value: {
                    # 脉象特征
                    "pulse_rhythm_regular": 0.8,
                    "pulse_force_moderate": 0.7,
                    "pulse_width_moderate": 0.7,
                    # 舌象特征
                    "tongue_color_pale_red": 0.8,
                    "tongue_coating_thin_white": 0.7,
                    "tongue_moisture_moderate": 0.7,
                    # 面色特征
                    "face_color_ruddy": 0.7,
                    "face_spirit_vibrant": 0.8,
                    # 症状特征
                    "sleep_quality_good": 0.6,
                    "energy_level_high": 0.7,
                    "digestion_normal": 0.7,
                    # 体格特征
                    "body_shape_balanced": 0.6,
                    "skin_smooth": 0.5,
                },
                TCMConstitutionType.QI_DEFICIENCY.value: {
                    # 脉象特征
                    "pulse_force_weak": 0.8,
                    "pulse_rhythm_regular": 0.5,
                    "pulse_speed_slow": 0.6,
                    # 舌象特征
                    "tongue_color_pale": 0.7,
                    "tongue_body_tender": 0.6,
                    "tongue_coating_thin": 0.5,
                    # 面色特征
                    "face_color_pale": 0.7,
                    "face_spirit_weak": 0.8,
                    # 症状特征
                    "fatigue_easy": 0.9,
                    "breath_shortness": 0.8,
                    "sweating_spontaneous": 0.7,
                    "voice_weak": 0.7,
                    "appetite_poor": 0.6,
                    # 体格特征
                    "body_weakness": 0.7,
                },
                TCMConstitutionType.YANG_DEFICIENCY.value: {
                    # 脉象特征
                    "pulse_force_weak": 0.7,
                    "pulse_speed_slow": 0.8,
                    "pulse_depth_deep": 0.7,
                    # 舌象特征
                    "tongue_color_pale": 0.8,
                    "tongue_coating_white": 0.7,
                    "tongue_body_swollen": 0.6,
                    # 面色特征
                    "face_color_pale": 0.7,
                    "face_spirit_weak": 0.6,
                    # 症状特征
                    "cold_intolerance": 0.9,
                    "limbs_cold": 0.9,
                    "urine_clear_profuse": 0.7,
                    "stool_loose": 0.6,
                    "abdomen_cold_pain": 0.7,
                    # 体格特征
                    "body_cold": 0.8,
                },
                TCMConstitutionType.YIN_DEFICIENCY.value: {
                    # 脉象特征
                    "pulse_force_weak": 0.5,
                    "pulse_speed_rapid": 0.8,
                    "pulse_quality_thready": 0.7,
                    # 舌象特征
                    "tongue_color_red": 0.8,
                    "tongue_coating_little": 0.7,
                    "tongue_body_dry": 0.9,
                    # 面色特征
                    "face_red_cheeks": 0.7,
                    "face_dry": 0.6,
                    # 症状特征
                    "heat_sensation": 0.8,
                    "night_sweating": 0.8,
                    "dry_mouth_throat": 0.9,
                    "insomnia": 0.7,
                    "constipation_dry": 0.7,
                    # 体格特征
                    "body_thin": 0.6,
                    "skin_dry": 0.7,
                },
                TCMConstitutionType.PHLEGM_DAMPNESS.value: {
                    # 脉象特征
                    "pulse_force_moderate": 0.5,
                    "pulse_quality_slippery": 0.8,
                    "pulse_width_wide": 0.6,
                    # 舌象特征
                    "tongue_coating_thick": 0.9,
                    "tongue_coating_greasy": 0.9,
                    "tongue_body_swollen": 0.7,
                    # 面色特征
                    "face_puffy": 0.7,
                    "face_oily": 0.7,
                    # 症状特征
                    "chest_fullness": 0.7,
                    "phlegm_production": 0.8,
                    "heaviness_sensation": 0.9,
                    "digestion_poor": 0.7,
                    "sticky_taste": 0.7,
                    # 体格特征
                    "body_overweight": 0.8,
                    "body_soft_weak": 0.6,
                },
                TCMConstitutionType.DAMPNESS_HEAT.value: {
                    # 脉象特征
                    "pulse_force_strong": 0.6,
                    "pulse_speed_rapid": 0.7,
                    "pulse_quality_slippery": 0.7,
                    # 舌象特征
                    "tongue_color_red": 0.7,
                    "tongue_coating_yellow": 0.9,
                    "tongue_coating_greasy": 0.8,
                    # 面色特征
                    "face_color_reddish": 0.7,
                    "face_oily": 0.8,
                    # 症状特征
                    "bitter_taste": 0.8,
                    "heavy_head": 0.7,
                    "thirst_no_desire": 0.6,
                    "urine_dark_scanty": 0.7,
                    "acne_oily_skin": 0.8,
                    # 体格特征
                    "body_heat": 0.7,
                    "sweat_sticky": 0.7,
                },
                TCMConstitutionType.BLOOD_STASIS.value: {
                    # 脉象特征
                    "pulse_rhythm_choppy": 0.9,
                    "pulse_quality_wiry": 0.7,
                    "pulse_quality_hidden": 0.6,
                    # 舌象特征
                    "tongue_color_purple": 0.9,
                    "tongue_spots_purple": 0.9,
                    "tongue_vessels_distended": 0.7,
                    # 面色特征
                    "face_color_dark": 0.8,
                    "face_spots_dark": 0.7,
                    # 症状特征
                    "fixed_pain": 0.9,
                    "blood_spots_under_skin": 0.8,
                    "menstrual_dark_clots": 0.8,
                    "lips_dark": 0.7,
                    "memory_poor": 0.5,
                    # 体格特征
                    "skin_dry_rough": 0.6,
                    "complexion_dark": 0.7,
                },
                TCMConstitutionType.QI_DEPRESSION.value: {
                    # 脉象特征
                    "pulse_quality_wiry": 0.9,
                    "pulse_force_moderate": 0.5,
                    "pulse_rhythm_irregular": 0.6,
                    # 舌象特征
                    "tongue_coating_thin": 0.6,
                    "tongue_sides_red": 0.7,
                    "tongue_teeth_marks": 0.7,
                    # 面色特征
                    "face_expression_depressed": 0.9,
                    "face_color_greenish": 0.7,
                    # 症状特征
                    "mood_depression": 0.9,
                    "chest_distension": 0.8,
                    "sighing_frequent": 0.8,
                    "throat_plum_sensation": 0.7,
                    "digestive_disturbance": 0.7,
                    # 体格特征
                    "breast_hypochondrium_distension": 0.8,
                    "sleep_restless": 0.7,
                },
                TCMConstitutionType.SPECIAL.value: {
                    # 脉象特征
                    "pulse_rhythm_irregular": 0.6,
                    "pulse_quality_variable": 0.7,
                    # 舌象特征
                    "tongue_shape_unusual": 0.7,
                    "tongue_coating_unusual": 0.7,
                    # 面色特征
                    "face_color_unusual": 0.7,
                    "face_allergic": 0.8,
                    # 症状特征
                    "allergies": 0.9,
                    "asthma_tendency": 0.8,
                    "skin_sensitivity": 0.8,
                    "food_sensitivity": 0.8,
                    "medication_sensitivity": 0.7,
                    # 体格特征
                    "immune_susceptibility": 0.9,
                    "skin_allergic": 0.8,
                }
            }
        except Exception as e:
            logger.error(f"加载特征权重出错: {e}")
            # 返回空字典作为默认值
            return {}
    
    async def analyze_tcm_constitution(
        self,
        user_id: Union[uuid.UUID, str],
        health_data: List[HealthData],
        inquiry_data: Optional[Dict[str, Any]] = None,
        inspection_data: Optional[Dict[str, Any]] = None,
        auscultation_data: Optional[Dict[str, Any]] = None,
        palpation_data: Optional[Dict[str, Any]] = None,
    ) -> TCMConstitutionData:
        """
        分析中医体质
        
        Args:
            user_id: 用户ID
            health_data: 健康数据列表
            inquiry_data: 问诊数据
            inspection_data: 望诊数据
            auscultation_data: 闻诊数据
            palpation_data: 切诊数据
            
        Returns:
            中医体质数据
        """
        user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        
        # 计算各体质得分
        scores = {}
        
        # 分析问诊数据
        inquiry_scores = self._analyze_inquiry_data(inquiry_data) if inquiry_data else {}
        
        # 分析望诊数据
        inspection_scores = self._analyze_inspection_data(inspection_data) if inspection_data else {}
        
        # 分析闻诊数据
        auscultation_scores = self._analyze_auscultation_data(auscultation_data) if auscultation_data else {}
        
        # 分析切诊数据
        palpation_scores = self._analyze_palpation_data(palpation_data) if palpation_data else {}
        
        # 分析健康数据
        health_data_scores = self._analyze_health_data(health_data) if health_data else {}
        
        # 合并所有得分，加权计算
        for constitution_type in self.constitution_types:
            # 四诊数据加权
            score = 0.0
            if inquiry_scores:
                score += inquiry_scores.get(constitution_type, 0) * self.diagnostic_weights["inquiry"]
            if inspection_scores:
                score += inspection_scores.get(constitution_type, 0) * self.diagnostic_weights["inspection"]
            if auscultation_scores:
                score += auscultation_scores.get(constitution_type, 0) * self.diagnostic_weights["auscultation"]
            if palpation_scores:
                score += palpation_scores.get(constitution_type, 0) * self.diagnostic_weights["palpation"]
            
            # 健康数据可以作为额外补充
            if health_data_scores:
                # 健康数据作为辅助信息，权重较低
                score = score * 0.8 + health_data_scores.get(constitution_type, 0) * 0.2
            
            scores[constitution_type] = round(score, 2)
        
        # 找出主要体质和次要体质
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_type_value = sorted_scores[0][0] if sorted_scores else TCMConstitutionType.BALANCED.value
        
        # 找出得分超过阈值的次要体质
        threshold = max(0.7 * sorted_scores[0][1] if sorted_scores else 0, 50)  # 得分至少50分
        secondary_types_values = [t[0] for t in sorted_scores[1:] if t[1] >= threshold]
        
        # 创建分析结果说明
        analysis_basis = {
            "scores": scores,
            "diagnostic_data": {
                "inquiry": inquiry_data,
                "inspection": inspection_data,
                "auscultation": auscultation_data,
                "palpation": palpation_data
            },
            "health_data_summary": self._summarize_health_data(health_data) if health_data else {}
        }
        
        # 生成体质调理建议
        recommendations = self._generate_recommendations(primary_type_value, secondary_types_values, scores)
        
        # 创建TCM体质数据对象
        constitution_data = TCMConstitutionData(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            primary_type=TCMConstitutionType(primary_type_value),
            secondary_types=[TCMConstitutionType(t) for t in secondary_types_values],
            scores=scores,
            analysis_basis=analysis_basis,
            recommendations=recommendations,
            created_by="ai_analysis"
        )
        
        logger.info(f"用户体质分析完成，主体质: {primary_type_value}")
        return constitution_data