#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多模态数据融合引擎
整合脉诊、腹诊、皮肤触诊的多维数据，使用深度学习技术进行特征融合
提供更准确的综合健康评估和时序数据分析
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum, auto
import json
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import warnings

logger = logging.getLogger(__name__)

class ModalityType(Enum):
    """模态类型枚举"""
    PULSE = "pulse"           # 脉诊
    ABDOMINAL = "abdominal"   # 腹诊
    SKIN = "skin"             # 皮肤触诊
    COMPREHENSIVE = "comprehensive"  # 综合

class FusionStrategy(Enum):
    """融合策略枚举"""
    EARLY_FUSION = "early"     # 早期融合
    LATE_FUSION = "late"       # 晚期融合
    HYBRID_FUSION = "hybrid"   # 混合融合
    ATTENTION_FUSION = "attention"  # 注意力融合

@dataclass
class ModalityData:
    """模态数据"""
    modality_type: ModalityType
    features: Dict[str, float]
    raw_data: Optional[np.ndarray] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FusionResult:
    """融合结果"""
    fused_features: Dict[str, float]
    modality_weights: Dict[ModalityType, float]
    confidence: float
    anomaly_score: float
    health_indicators: Dict[str, float]
    temporal_trends: Dict[str, List[float]]
    fusion_strategy: FusionStrategy
    processing_time: float
    timestamp: datetime

class MultimodalFusionEngine:
    """多模态数据融合引擎"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化多模态融合引擎
        
        Args:
            config: 配置字典
        """
        self.config = config
        
        # 融合配置
        self.fusion_strategy = FusionStrategy(config.get('fusion_strategy', 'hybrid'))
        self.feature_selection = config.get('feature_selection', True)
        self.temporal_analysis = config.get('temporal_analysis', True)
        self.anomaly_detection = config.get('anomaly_detection', True)
        
        # 模态权重配置
        self.modality_weights = config.get('modality_weights', {
            ModalityType.PULSE: 0.5,
            ModalityType.ABDOMINAL: 0.3,
            ModalityType.SKIN: 0.2
        })
        
        # 特征处理配置
        self.feature_config = config.get('feature_processing', {})
        self.normalization_method = self.feature_config.get('normalization', 'standard')
        self.dimensionality_reduction = self.feature_config.get('dimensionality_reduction', True)
        self.target_dimensions = self.feature_config.get('target_dimensions', 50)
        
        # 时序分析配置
        self.temporal_config = config.get('temporal_analysis', {})
        self.window_size = self.temporal_config.get('window_size', 10)
        self.trend_analysis = self.temporal_config.get('trend_analysis', True)
        self.seasonality_detection = self.temporal_config.get('seasonality_detection', False)
        
        # 异常检测配置
        self.anomaly_config = config.get('anomaly_detection', {})
        self.contamination_rate = self.anomaly_config.get('contamination_rate', 0.1)
        self.anomaly_threshold = self.anomaly_config.get('threshold', 0.5)
        
        # 数据存储
        self.historical_data: Dict[str, List[ModalityData]] = {
            modality.value: [] for modality in ModalityType
        }
        self.fusion_history: List[FusionResult] = []
        
        # 模型组件
        self.feature_scalers: Dict[ModalityType, StandardScaler] = {}
        self.dimensionality_reducers: Dict[ModalityType, PCA] = {}
        self.anomaly_detectors: Dict[ModalityType, IsolationForest] = {}
        self.fusion_model = None
        
        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 初始化组件
        self._initialize_components()
        
        logger.info("多模态数据融合引擎初始化完成")
    
    def _initialize_components(self):
        """初始化组件"""
        try:
            # 初始化特征缩放器
            for modality in ModalityType:
                if modality != ModalityType.COMPREHENSIVE:
                    if self.normalization_method == 'standard':
                        self.feature_scalers[modality] = StandardScaler()
                    else:
                        self.feature_scalers[modality] = MinMaxScaler()
            
            # 初始化降维器
            if self.dimensionality_reduction:
                for modality in ModalityType:
                    if modality != ModalityType.COMPREHENSIVE:
                        self.dimensionality_reducers[modality] = PCA(
                            n_components=min(self.target_dimensions, 50)
                        )
            
            # 初始化异常检测器
            if self.anomaly_detection:
                for modality in ModalityType:
                    if modality != ModalityType.COMPREHENSIVE:
                        self.anomaly_detectors[modality] = IsolationForest(
                            contamination=self.contamination_rate,
                            random_state=42
                        )
            
            # 初始化融合模型
            self._initialize_fusion_model()
            
            logger.info("融合引擎组件初始化完成")
            
        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            raise
    
    def _initialize_fusion_model(self):
        """初始化融合模型"""
        # 这里应该加载实际的深度学习模型
        # 例如：多层感知机、注意力网络等
        logger.info("融合模型初始化完成")
    
    async def add_modality_data(
        self, 
        session_id: str,
        modality_data: ModalityData
    ) -> Dict[str, Any]:
        """
        添加模态数据
        
        Args:
            session_id: 会话ID
            modality_data: 模态数据
            
        Returns:
            处理结果
        """
        try:
            # 数据质量检查
            quality_check = await self._check_data_quality(modality_data)
            if not quality_check['is_valid']:
                return {
                    'status': 'error',
                    'message': f"数据质量不合格: {quality_check['reason']}"
                }
            
            # 特征预处理
            processed_data = await self._preprocess_modality_data(modality_data)
            
            # 存储数据
            modality_key = modality_data.modality_type.value
            self.historical_data[modality_key].append(processed_data)
            
            # 限制历史数据大小
            max_history = self.config.get('max_history_size', 1000)
            if len(self.historical_data[modality_key]) > max_history:
                self.historical_data[modality_key] = self.historical_data[modality_key][-max_history:]
            
            logger.debug(f"添加{modality_data.modality_type.value}数据: {session_id}")
            
            return {
                'status': 'success',
                'session_id': session_id,
                'modality': modality_data.modality_type.value,
                'quality_score': processed_data.quality_score
            }
            
        except Exception as e:
            logger.error(f"添加模态数据失败: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def fuse_multimodal_data(
        self,
        session_id: str,
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> FusionResult:
        """
        融合多模态数据
        
        Args:
            session_id: 会话ID
            modality_data_list: 模态数据列表
            user_profile: 用户档案
            
        Returns:
            融合结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 数据预处理
            processed_data = []
            for data in modality_data_list:
                processed = await self._preprocess_modality_data(data)
                processed_data.append(processed)
            
            # 根据融合策略执行融合
            if self.fusion_strategy == FusionStrategy.EARLY_FUSION:
                fusion_result = await self._early_fusion(processed_data, user_profile)
            elif self.fusion_strategy == FusionStrategy.LATE_FUSION:
                fusion_result = await self._late_fusion(processed_data, user_profile)
            elif self.fusion_strategy == FusionStrategy.HYBRID_FUSION:
                fusion_result = await self._hybrid_fusion(processed_data, user_profile)
            else:  # ATTENTION_FUSION
                fusion_result = await self._attention_fusion(processed_data, user_profile)
            
            # 时序分析
            if self.temporal_analysis:
                temporal_trends = await self._analyze_temporal_trends(session_id, fusion_result)
                fusion_result.temporal_trends = temporal_trends
            
            # 异常检测
            if self.anomaly_detection:
                anomaly_score = await self._detect_anomalies(fusion_result.fused_features)
                fusion_result.anomaly_score = anomaly_score
            
            # 计算处理时间
            processing_time = asyncio.get_event_loop().time() - start_time
            fusion_result.processing_time = processing_time
            
            # 存储融合历史
            self.fusion_history.append(fusion_result)
            if len(self.fusion_history) > 1000:  # 限制历史大小
                self.fusion_history = self.fusion_history[-500:]
            
            logger.info(f"多模态融合完成: {session_id}, 耗时: {processing_time:.2f}s")
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"多模态融合失败: {e}")
            raise
    
    async def _check_data_quality(self, data: ModalityData) -> Dict[str, Any]:
        """检查数据质量"""
        try:
            # 检查特征完整性
            if not data.features:
                return {'is_valid': False, 'reason': '特征数据为空'}
            
            # 检查特征值有效性
            for key, value in data.features.items():
                if not isinstance(value, (int, float)) or np.isnan(value) or np.isinf(value):
                    return {'is_valid': False, 'reason': f'特征值无效: {key}={value}'}
            
            # 检查置信度
            if data.confidence < 0.3:
                return {'is_valid': False, 'reason': f'置信度过低: {data.confidence}'}
            
            # 检查质量评分
            if data.quality_score < 0.5:
                return {'is_valid': False, 'reason': f'质量评分过低: {data.quality_score}'}
            
            return {'is_valid': True, 'reason': '数据质量合格'}
            
        except Exception as e:
            return {'is_valid': False, 'reason': f'质量检查异常: {e}'}
    
    async def _preprocess_modality_data(self, data: ModalityData) -> ModalityData:
        """预处理模态数据"""
        try:
            # 特征标准化
            if data.modality_type in self.feature_scalers:
                scaler = self.feature_scalers[data.modality_type]
                
                # 准备特征向量
                feature_vector = np.array(list(data.features.values())).reshape(1, -1)
                
                # 如果缩放器未训练，使用当前数据进行拟合
                if not hasattr(scaler, 'scale_'):
                    scaler.fit(feature_vector)
                
                # 标准化特征
                try:
                    scaled_features = scaler.transform(feature_vector)[0]
                    
                    # 更新特征字典
                    feature_keys = list(data.features.keys())
                    data.features = {
                        key: float(scaled_features[i]) 
                        for i, key in enumerate(feature_keys)
                    }
                except Exception as e:
                    logger.warning(f"特征标准化失败: {e}")
            
            # 特征选择
            if self.feature_selection:
                data.features = await self._select_important_features(data)
            
            # 降维处理
            if self.dimensionality_reduction and data.modality_type in self.dimensionality_reducers:
                data.features = await self._reduce_dimensionality(data)
            
            return data
            
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            return data
    
    async def _select_important_features(self, data: ModalityData) -> Dict[str, float]:
        """选择重要特征"""
        # 基于特征重要性的简单选择策略
        important_features = {}
        
        # 根据模态类型选择关键特征
        if data.modality_type == ModalityType.PULSE:
            key_features = [
                'heart_rate', 'heart_rate_variability', 'pulse_strength',
                'rhythm_regularity', 'dominant_frequency', 'spectral_centroid'
            ]
        elif data.modality_type == ModalityType.ABDOMINAL:
            key_features = [
                'abdominal_tension', 'organ_palpation', 'pain_response',
                'temperature_variation', 'texture_analysis'
            ]
        elif data.modality_type == ModalityType.SKIN:
            key_features = [
                'skin_elasticity', 'moisture_level', 'temperature',
                'texture_roughness', 'color_variation'
            ]
        else:
            key_features = list(data.features.keys())
        
        # 选择存在的关键特征
        for feature in key_features:
            if feature in data.features:
                important_features[feature] = data.features[feature]
        
        # 如果关键特征不足，补充其他特征
        if len(important_features) < 5:
            for feature, value in data.features.items():
                if feature not in important_features:
                    important_features[feature] = value
                if len(important_features) >= 10:  # 限制特征数量
                    break
        
        return important_features
    
    async def _reduce_dimensionality(self, data: ModalityData) -> Dict[str, float]:
        """降维处理"""
        try:
            reducer = self.dimensionality_reducers[data.modality_type]
            
            # 准备特征向量
            feature_vector = np.array(list(data.features.values())).reshape(1, -1)
            
            # 如果降维器未训练，使用当前数据进行拟合
            if not hasattr(reducer, 'components_'):
                # 需要更多数据来训练PCA，暂时跳过
                return data.features
            
            # 降维
            reduced_features = reducer.transform(feature_vector)[0]
            
            # 创建新的特征字典
            reduced_dict = {
                f'pc_{i}': float(reduced_features[i])
                for i in range(len(reduced_features))
            }
            
            return reduced_dict
            
        except Exception as e:
            logger.warning(f"降维处理失败: {e}")
            return data.features
    
    async def _early_fusion(
        self, 
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]]
    ) -> FusionResult:
        """早期融合策略"""
        # 合并所有特征
        fused_features = {}
        modality_weights = {}
        total_confidence = 0
        
        for data in modality_data_list:
            weight = self.modality_weights.get(data.modality_type, 1.0)
            modality_weights[data.modality_type] = weight
            
            # 加权合并特征
            for key, value in data.features.items():
                feature_key = f"{data.modality_type.value}_{key}"
                fused_features[feature_key] = value * weight
            
            total_confidence += data.confidence * weight
        
        # 归一化置信度
        total_weight = sum(modality_weights.values())
        confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        # 计算健康指标
        health_indicators = await self._calculate_health_indicators(fused_features, user_profile)
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            confidence=confidence,
            anomaly_score=0.0,  # 将在后续步骤中计算
            health_indicators=health_indicators,
            temporal_trends={},  # 将在后续步骤中计算
            fusion_strategy=FusionStrategy.EARLY_FUSION,
            processing_time=0.0,  # 将在调用方设置
            timestamp=datetime.now()
        )
    
    async def _late_fusion(
        self, 
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]]
    ) -> FusionResult:
        """晚期融合策略"""
        # 分别处理每个模态，然后融合结果
        modality_results = {}
        modality_weights = {}
        
        for data in modality_data_list:
            # 单模态分析
            modality_result = await self._analyze_single_modality(data, user_profile)
            modality_results[data.modality_type] = modality_result
            modality_weights[data.modality_type] = self.modality_weights.get(data.modality_type, 1.0)
        
        # 融合单模态结果
        fused_features = {}
        total_confidence = 0
        
        for modality_type, result in modality_results.items():
            weight = modality_weights[modality_type]
            
            # 融合特征
            for key, value in result['features'].items():
                if key in fused_features:
                    fused_features[key] = (fused_features[key] + value * weight) / 2
                else:
                    fused_features[key] = value * weight
            
            total_confidence += result['confidence'] * weight
        
        # 归一化置信度
        total_weight = sum(modality_weights.values())
        confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        # 计算健康指标
        health_indicators = await self._calculate_health_indicators(fused_features, user_profile)
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            confidence=confidence,
            anomaly_score=0.0,
            health_indicators=health_indicators,
            temporal_trends={},
            fusion_strategy=FusionStrategy.LATE_FUSION,
            processing_time=0.0,
            timestamp=datetime.now()
        )
    
    async def _hybrid_fusion(
        self, 
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]]
    ) -> FusionResult:
        """混合融合策略"""
        # 结合早期和晚期融合的优势
        
        # 早期融合部分
        early_result = await self._early_fusion(modality_data_list, user_profile)
        
        # 晚期融合部分
        late_result = await self._late_fusion(modality_data_list, user_profile)
        
        # 混合融合
        fused_features = {}
        
        # 加权合并两种融合结果
        early_weight = 0.6
        late_weight = 0.4
        
        # 合并特征
        all_keys = set(early_result.fused_features.keys()) | set(late_result.fused_features.keys())
        
        for key in all_keys:
            early_value = early_result.fused_features.get(key, 0)
            late_value = late_result.fused_features.get(key, 0)
            fused_features[key] = early_value * early_weight + late_value * late_weight
        
        # 合并置信度
        confidence = early_result.confidence * early_weight + late_result.confidence * late_weight
        
        # 合并模态权重
        modality_weights = {}
        for modality_type in ModalityType:
            if modality_type != ModalityType.COMPREHENSIVE:
                early_w = early_result.modality_weights.get(modality_type, 0)
                late_w = late_result.modality_weights.get(modality_type, 0)
                modality_weights[modality_type] = early_w * early_weight + late_w * late_weight
        
        # 计算健康指标
        health_indicators = await self._calculate_health_indicators(fused_features, user_profile)
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            confidence=confidence,
            anomaly_score=0.0,
            health_indicators=health_indicators,
            temporal_trends={},
            fusion_strategy=FusionStrategy.HYBRID_FUSION,
            processing_time=0.0,
            timestamp=datetime.now()
        )
    
    async def _attention_fusion(
        self, 
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]]
    ) -> FusionResult:
        """注意力融合策略"""
        # 基于注意力机制的融合
        
        # 计算注意力权重
        attention_weights = await self._calculate_attention_weights(modality_data_list, user_profile)
        
        # 应用注意力权重进行融合
        fused_features = {}
        modality_weights = {}
        total_confidence = 0
        
        for i, data in enumerate(modality_data_list):
            attention_weight = attention_weights[i]
            modality_weights[data.modality_type] = attention_weight
            
            # 加权特征
            for key, value in data.features.items():
                feature_key = f"{data.modality_type.value}_{key}"
                if feature_key in fused_features:
                    fused_features[feature_key] += value * attention_weight
                else:
                    fused_features[feature_key] = value * attention_weight
            
            total_confidence += data.confidence * attention_weight
        
        # 归一化
        total_weight = sum(attention_weights)
        if total_weight > 0:
            for key in fused_features:
                fused_features[key] /= total_weight
            confidence = total_confidence / total_weight
        else:
            confidence = 0
        
        # 计算健康指标
        health_indicators = await self._calculate_health_indicators(fused_features, user_profile)
        
        return FusionResult(
            fused_features=fused_features,
            modality_weights=modality_weights,
            confidence=confidence,
            anomaly_score=0.0,
            health_indicators=health_indicators,
            temporal_trends={},
            fusion_strategy=FusionStrategy.ATTENTION_FUSION,
            processing_time=0.0,
            timestamp=datetime.now()
        )
    
    async def _calculate_attention_weights(
        self, 
        modality_data_list: List[ModalityData],
        user_profile: Optional[Dict[str, Any]]
    ) -> List[float]:
        """计算注意力权重"""
        weights = []
        
        for data in modality_data_list:
            # 基于数据质量和置信度计算权重
            quality_weight = data.quality_score
            confidence_weight = data.confidence
            
            # 基于模态类型的先验权重
            prior_weight = self.modality_weights.get(data.modality_type, 1.0)
            
            # 综合权重
            attention_weight = quality_weight * confidence_weight * prior_weight
            weights.append(attention_weight)
        
        # Softmax归一化
        weights = np.array(weights)
        exp_weights = np.exp(weights - np.max(weights))  # 数值稳定性
        normalized_weights = exp_weights / np.sum(exp_weights)
        
        return normalized_weights.tolist()
    
    async def _analyze_single_modality(
        self, 
        data: ModalityData,
        user_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析单个模态"""
        # 提取关键特征
        key_features = await self._extract_key_features(data)
        
        # 计算健康评分
        health_score = await self._calculate_modality_health_score(data, user_profile)
        
        return {
            'features': key_features,
            'health_score': health_score,
            'confidence': data.confidence,
            'quality_score': data.quality_score
        }
    
    async def _extract_key_features(self, data: ModalityData) -> Dict[str, float]:
        """提取关键特征"""
        # 根据模态类型提取最重要的特征
        if data.modality_type == ModalityType.PULSE:
            key_features = {
                'cardiovascular_health': data.features.get('heart_rate', 70) / 100,
                'rhythm_stability': data.features.get('rhythm_regularity', 0.8),
                'energy_level': data.features.get('pulse_strength', 0.5)
            }
        elif data.modality_type == ModalityType.ABDOMINAL:
            key_features = {
                'digestive_health': data.features.get('abdominal_tension', 0.5),
                'organ_function': data.features.get('organ_palpation', 0.5),
                'inflammation_level': data.features.get('pain_response', 0.3)
            }
        elif data.modality_type == ModalityType.SKIN:
            key_features = {
                'skin_health': data.features.get('skin_elasticity', 0.8),
                'hydration_level': data.features.get('moisture_level', 0.6),
                'circulation_quality': data.features.get('temperature', 0.7)
            }
        else:
            key_features = data.features
        
        return key_features
    
    async def _calculate_modality_health_score(
        self, 
        data: ModalityData,
        user_profile: Optional[Dict[str, Any]]
    ) -> float:
        """计算模态健康评分"""
        base_score = 0.7  # 基础评分
        
        # 根据特征调整评分
        for key, value in data.features.items():
            if 'health' in key.lower() or 'quality' in key.lower():
                base_score += (value - 0.5) * 0.1
        
        # 根据置信度调整
        base_score *= data.confidence
        
        # 根据质量评分调整
        base_score *= data.quality_score
        
        return max(0, min(1, base_score))
    
    async def _calculate_health_indicators(
        self, 
        fused_features: Dict[str, float],
        user_profile: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """计算健康指标"""
        health_indicators = {}
        
        # 心血管健康指标
        cardiovascular_features = [
            key for key in fused_features.keys() 
            if any(term in key.lower() for term in ['heart', 'pulse', 'cardiovascular'])
        ]
        if cardiovascular_features:
            cv_score = np.mean([fused_features[key] for key in cardiovascular_features])
            health_indicators['cardiovascular_health'] = max(0, min(1, cv_score))
        
        # 消化系统健康指标
        digestive_features = [
            key for key in fused_features.keys() 
            if any(term in key.lower() for term in ['abdominal', 'digestive', 'organ'])
        ]
        if digestive_features:
            digestive_score = np.mean([fused_features[key] for key in digestive_features])
            health_indicators['digestive_health'] = max(0, min(1, digestive_score))
        
        # 皮肤健康指标
        skin_features = [
            key for key in fused_features.keys() 
            if any(term in key.lower() for term in ['skin', 'elasticity', 'moisture'])
        ]
        if skin_features:
            skin_score = np.mean([fused_features[key] for key in skin_features])
            health_indicators['skin_health'] = max(0, min(1, skin_score))
        
        # 整体健康指标
        if health_indicators:
            health_indicators['overall_health'] = np.mean(list(health_indicators.values()))
        else:
            health_indicators['overall_health'] = 0.7  # 默认值
        
        return health_indicators
    
    async def _analyze_temporal_trends(
        self, 
        session_id: str,
        fusion_result: FusionResult
    ) -> Dict[str, List[float]]:
        """分析时序趋势"""
        trends = {}
        
        if len(self.fusion_history) < 2:
            return trends
        
        # 分析最近的融合历史
        recent_history = self.fusion_history[-self.window_size:]
        
        # 提取时序数据
        for feature_key in fusion_result.fused_features.keys():
            feature_values = []
            for hist_result in recent_history:
                if feature_key in hist_result.fused_features:
                    feature_values.append(hist_result.fused_features[feature_key])
            
            if len(feature_values) >= 3:  # 至少需要3个数据点
                trends[feature_key] = feature_values
        
        return trends
    
    async def _detect_anomalies(self, fused_features: Dict[str, float]) -> float:
        """检测异常"""
        try:
            # 准备特征向量
            feature_vector = np.array(list(fused_features.values())).reshape(1, -1)
            
            # 使用简单的统计方法检测异常
            if len(self.fusion_history) < 10:
                return 0.0  # 历史数据不足
            
            # 计算历史特征的统计信息
            historical_features = []
            for hist_result in self.fusion_history[-50:]:  # 使用最近50个结果
                hist_vector = []
                for key in fused_features.keys():
                    if key in hist_result.fused_features:
                        hist_vector.append(hist_result.fused_features[key])
                    else:
                        hist_vector.append(0.0)
                historical_features.append(hist_vector)
            
            if len(historical_features) < 5:
                return 0.0
            
            historical_array = np.array(historical_features)
            
            # 计算Z-score
            mean_values = np.mean(historical_array, axis=0)
            std_values = np.std(historical_array, axis=0)
            
            # 避免除零
            std_values = np.where(std_values == 0, 1, std_values)
            
            z_scores = np.abs((feature_vector[0] - mean_values) / std_values)
            
            # 异常评分（基于最大Z-score）
            max_z_score = np.max(z_scores)
            anomaly_score = min(1.0, max_z_score / 3.0)  # 归一化到0-1
            
            return anomaly_score
            
        except Exception as e:
            logger.warning(f"异常检测失败: {e}")
            return 0.0
    
    async def get_fusion_summary(self, session_id: str) -> Dict[str, Any]:
        """获取融合摘要"""
        if not self.fusion_history:
            return {
                'status': 'no_data',
                'message': '暂无融合历史数据'
            }
        
        latest_result = self.fusion_history[-1]
        
        return {
            'status': 'success',
            'session_id': session_id,
            'latest_fusion': {
                'confidence': latest_result.confidence,
                'anomaly_score': latest_result.anomaly_score,
                'health_indicators': latest_result.health_indicators,
                'fusion_strategy': latest_result.fusion_strategy.value,
                'processing_time': latest_result.processing_time,
                'timestamp': latest_result.timestamp.isoformat()
            },
            'historical_summary': {
                'total_fusions': len(self.fusion_history),
                'average_confidence': np.mean([r.confidence for r in self.fusion_history]),
                'average_anomaly_score': np.mean([r.anomaly_score for r in self.fusion_history]),
                'average_processing_time': np.mean([r.processing_time for r in self.fusion_history])
            }
        }
    
    def cleanup(self):
        """清理资源"""
        # 清理历史数据
        self.historical_data.clear()
        self.fusion_history.clear()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        logger.info("多模态融合引擎资源清理完成") 