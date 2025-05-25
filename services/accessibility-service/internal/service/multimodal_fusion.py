#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
多模态融合分析器 - 整合多种数据源的深度分析系统
包含数据融合、特征提取、模式识别、异常检测、预测分析等功能
"""

import logging
import time
import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from scipy import signal
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)


class ModalityType(Enum):
    """模态类型枚举"""
    SENSOR_DATA = "sensor_data"
    AUDIO_DATA = "audio_data"
    VISUAL_DATA = "visual_data"
    BEHAVIORAL_DATA = "behavioral_data"
    ENVIRONMENTAL_DATA = "environmental_data"
    PHYSIOLOGICAL_DATA = "physiological_data"
    CONTEXTUAL_DATA = "contextual_data"
    TEMPORAL_DATA = "temporal_data"


class FusionStrategy(Enum):
    """融合策略枚举"""
    EARLY_FUSION = "early_fusion"  # 特征级融合
    LATE_FUSION = "late_fusion"    # 决策级融合
    HYBRID_FUSION = "hybrid_fusion"  # 混合融合
    ATTENTION_FUSION = "attention_fusion"  # 注意力融合
    WEIGHTED_FUSION = "weighted_fusion"  # 加权融合


class AnalysisType(Enum):
    """分析类型枚举"""
    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    CLUSTERING_ANALYSIS = "clustering_analysis"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


@dataclass
class ModalityData:
    """模态数据结构"""
    modality_id: str
    modality_type: ModalityType
    data: Any
    timestamp: float
    quality_score: float
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    features: Optional[np.ndarray] = None
    processed: bool = False


@dataclass
class FusionResult:
    """融合结果"""
    fusion_id: str
    strategy: FusionStrategy
    input_modalities: List[str]
    fused_features: np.ndarray
    confidence: float
    quality_score: float
    timestamp: float
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    """分析结果"""
    analysis_id: str
    analysis_type: AnalysisType
    input_data: str  # fusion_id or modality_id
    results: Dict[str, Any]
    confidence: float
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class FeatureExtractor:
    """特征提取器"""
    
    def __init__(self):
        self.extractors = {
            ModalityType.SENSOR_DATA: self._extract_sensor_features,
            ModalityType.AUDIO_DATA: self._extract_audio_features,
            ModalityType.VISUAL_DATA: self._extract_visual_features,
            ModalityType.BEHAVIORAL_DATA: self._extract_behavioral_features,
            ModalityType.ENVIRONMENTAL_DATA: self._extract_environmental_features,
            ModalityType.PHYSIOLOGICAL_DATA: self._extract_physiological_features,
            ModalityType.CONTEXTUAL_DATA: self._extract_contextual_features,
            ModalityType.TEMPORAL_DATA: self._extract_temporal_features
        }
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # 保留95%的方差
    
    def extract_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取特征"""
        try:
            extractor = self.extractors.get(modality_data.modality_type)
            if not extractor:
                logger.warning(f"未找到模态 {modality_data.modality_type} 的特征提取器")
                return np.array([])
            
            features = extractor(modality_data)
            
            # 标准化特征
            if len(features) > 0:
                features = features.reshape(1, -1)
                features = self.scaler.fit_transform(features).flatten()
            
            modality_data.features = features
            modality_data.processed = True
            
            return features
            
        except Exception as e:
            logger.error(f"特征提取失败: {str(e)}")
            return np.array([])
    
    def _extract_sensor_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取传感器特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            for sensor_type, sensor_data in data.items():
                if isinstance(sensor_data, dict) and 'values' in sensor_data:
                    values = np.array(sensor_data['values'])
                    if len(values) > 0:
                        # 统计特征
                        features.extend([
                            np.mean(values),
                            np.std(values),
                            np.min(values),
                            np.max(values),
                            np.median(values)
                        ])
                        
                        # 频域特征
                        if len(values) > 1:
                            fft = np.fft.fft(values)
                            features.extend([
                                np.mean(np.abs(fft)),
                                np.std(np.abs(fft)),
                                np.argmax(np.abs(fft))  # 主频率
                            ])
        
        return np.array(features)
    
    def _extract_audio_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取音频特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 音量特征
            if 'volume' in data:
                volume = data['volume']
                features.extend([volume, volume**2])  # 音量和音量平方
            
            # 频谱特征
            if 'spectrum' in data:
                spectrum = np.array(data['spectrum'])
                if len(spectrum) > 0:
                    features.extend([
                        np.mean(spectrum),
                        np.std(spectrum),
                        np.max(spectrum),
                        np.argmax(spectrum)  # 峰值频率
                    ])
            
            # 语音活动检测
            if 'voice_activity' in data:
                features.append(float(data['voice_activity']))
            
            # 情感特征
            if 'emotion_scores' in data:
                emotion_scores = data['emotion_scores']
                if isinstance(emotion_scores, dict):
                    features.extend(list(emotion_scores.values()))
        
        return np.array(features)
    
    def _extract_visual_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取视觉特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 面部特征
            if 'facial_landmarks' in data:
                landmarks = data['facial_landmarks']
                if isinstance(landmarks, list) and len(landmarks) > 0:
                    landmarks_array = np.array(landmarks).flatten()
                    features.extend(landmarks_array[:20])  # 取前20个关键点
            
            # 眼部特征
            if 'eye_tracking' in data:
                eye_data = data['eye_tracking']
                if isinstance(eye_data, dict):
                    features.extend([
                        eye_data.get('gaze_x', 0),
                        eye_data.get('gaze_y', 0),
                        eye_data.get('pupil_diameter', 0),
                        eye_data.get('blink_rate', 0)
                    ])
            
            # 手势特征
            if 'gestures' in data:
                gestures = data['gestures']
                if isinstance(gestures, list):
                    # 手势类型编码
                    gesture_encoding = {
                        'swipe_left': 1, 'swipe_right': 2, 'swipe_up': 3, 'swipe_down': 4,
                        'tap': 5, 'double_tap': 6, 'pinch': 7, 'zoom': 8
                    }
                    for gesture in gestures[:5]:  # 最多5个手势
                        features.append(gesture_encoding.get(gesture, 0))
            
            # 姿态特征
            if 'posture' in data:
                posture = data['posture']
                if isinstance(posture, dict):
                    features.extend([
                        posture.get('head_tilt', 0),
                        posture.get('shoulder_angle', 0),
                        posture.get('spine_curvature', 0)
                    ])
        
        return np.array(features)
    
    def _extract_behavioral_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取行为特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 交互频率
            if 'interaction_frequency' in data:
                features.append(data['interaction_frequency'])
            
            # 操作类型分布
            if 'action_distribution' in data:
                action_dist = data['action_distribution']
                if isinstance(action_dist, dict):
                    features.extend(list(action_dist.values())[:10])  # 最多10种操作类型
            
            # 会话持续时间
            if 'session_duration' in data:
                features.append(data['session_duration'])
            
            # 错误率
            if 'error_rate' in data:
                features.append(data['error_rate'])
            
            # 完成率
            if 'completion_rate' in data:
                features.append(data['completion_rate'])
            
            # 响应时间统计
            if 'response_times' in data:
                response_times = np.array(data['response_times'])
                if len(response_times) > 0:
                    features.extend([
                        np.mean(response_times),
                        np.std(response_times),
                        np.median(response_times)
                    ])
        
        return np.array(features)
    
    def _extract_environmental_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取环境特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 环境传感器数据
            env_sensors = ['temperature', 'humidity', 'light_level', 'noise_level', 'air_quality']
            for sensor in env_sensors:
                if sensor in data:
                    features.append(data[sensor])
            
            # 位置信息
            if 'location' in data:
                location = data['location']
                if isinstance(location, dict):
                    features.extend([
                        location.get('latitude', 0),
                        location.get('longitude', 0),
                        location.get('altitude', 0),
                        location.get('accuracy', 0)
                    ])
            
            # 网络状态
            if 'network_status' in data:
                network = data['network_status']
                if isinstance(network, dict):
                    features.extend([
                        network.get('signal_strength', 0),
                        network.get('bandwidth', 0),
                        network.get('latency', 0)
                    ])
            
            # 设备状态
            if 'device_status' in data:
                device = data['device_status']
                if isinstance(device, dict):
                    features.extend([
                        device.get('battery_level', 0),
                        device.get('cpu_usage', 0),
                        device.get('memory_usage', 0),
                        device.get('storage_usage', 0)
                    ])
        
        return np.array(features)
    
    def _extract_physiological_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取生理特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 心率相关
            if 'heart_rate' in data:
                hr_data = data['heart_rate']
                if isinstance(hr_data, dict):
                    features.extend([
                        hr_data.get('bpm', 0),
                        hr_data.get('hrv', 0),  # 心率变异性
                        hr_data.get('resting_hr', 0)
                    ])
            
            # 血压
            if 'blood_pressure' in data:
                bp_data = data['blood_pressure']
                if isinstance(bp_data, dict):
                    features.extend([
                        bp_data.get('systolic', 0),
                        bp_data.get('diastolic', 0)
                    ])
            
            # 体温
            if 'body_temperature' in data:
                features.append(data['body_temperature'])
            
            # 血氧饱和度
            if 'spo2' in data:
                features.append(data['spo2'])
            
            # 压力水平
            if 'stress_level' in data:
                features.append(data['stress_level'])
            
            # 睡眠质量
            if 'sleep_quality' in data:
                sleep_data = data['sleep_quality']
                if isinstance(sleep_data, dict):
                    features.extend([
                        sleep_data.get('duration', 0),
                        sleep_data.get('efficiency', 0),
                        sleep_data.get('deep_sleep_ratio', 0)
                    ])
        
        return np.array(features)
    
    def _extract_contextual_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取上下文特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 时间上下文
            if 'time_context' in data:
                time_ctx = data['time_context']
                if isinstance(time_ctx, dict):
                    features.extend([
                        time_ctx.get('hour_of_day', 0),
                        time_ctx.get('day_of_week', 0),
                        time_ctx.get('day_of_month', 0),
                        time_ctx.get('month', 0)
                    ])
            
            # 活动上下文
            if 'activity_context' in data:
                activity = data['activity_context']
                # 活动类型编码
                activity_encoding = {
                    'working': 1, 'resting': 2, 'exercising': 3, 'eating': 4,
                    'sleeping': 5, 'commuting': 6, 'socializing': 7, 'learning': 8
                }
                features.append(activity_encoding.get(activity, 0))
            
            # 社交上下文
            if 'social_context' in data:
                social = data['social_context']
                if isinstance(social, dict):
                    features.extend([
                        social.get('people_nearby', 0),
                        social.get('interaction_level', 0)
                    ])
            
            # 应用使用上下文
            if 'app_context' in data:
                app_ctx = data['app_context']
                if isinstance(app_ctx, dict):
                    features.extend([
                        app_ctx.get('app_category_id', 0),
                        app_ctx.get('usage_duration', 0),
                        app_ctx.get('interaction_count', 0)
                    ])
        
        return np.array(features)
    
    def _extract_temporal_features(self, modality_data: ModalityData) -> np.ndarray:
        """提取时间特征"""
        data = modality_data.data
        features = []
        
        if isinstance(data, dict):
            # 时间序列统计特征
            if 'time_series' in data:
                ts_data = np.array(data['time_series'])
                if len(ts_data) > 0:
                    features.extend([
                        np.mean(ts_data),
                        np.std(ts_data),
                        np.min(ts_data),
                        np.max(ts_data),
                        np.median(ts_data)
                    ])
                    
                    # 趋势特征
                    if len(ts_data) > 1:
                        diff = np.diff(ts_data)
                        features.extend([
                            np.mean(diff),
                            np.std(diff),
                            len(diff[diff > 0]) / len(diff)  # 上升趋势比例
                        ])
            
            # 周期性特征
            if 'periodicity' in data:
                period_data = data['periodicity']
                if isinstance(period_data, dict):
                    features.extend([
                        period_data.get('daily_pattern_strength', 0),
                        period_data.get('weekly_pattern_strength', 0),
                        period_data.get('dominant_period', 0)
                    ])
            
            # 事件频率
            if 'event_frequency' in data:
                features.append(data['event_frequency'])
            
            # 时间间隔统计
            if 'intervals' in data:
                intervals = np.array(data['intervals'])
                if len(intervals) > 0:
                    features.extend([
                        np.mean(intervals),
                        np.std(intervals),
                        np.median(intervals)
                    ])
        
        return np.array(features)


class DataFusionEngine:
    """数据融合引擎"""
    
    def __init__(self):
        self.fusion_strategies = {
            FusionStrategy.EARLY_FUSION: self._early_fusion,
            FusionStrategy.LATE_FUSION: self._late_fusion,
            FusionStrategy.HYBRID_FUSION: self._hybrid_fusion,
            FusionStrategy.ATTENTION_FUSION: self._attention_fusion,
            FusionStrategy.WEIGHTED_FUSION: self._weighted_fusion
        }
        self.feature_extractor = FeatureExtractor()
        self.fusion_history = deque(maxlen=1000)
    
    def fuse_modalities(self, modalities: List[ModalityData], 
                       strategy: FusionStrategy = FusionStrategy.HYBRID_FUSION) -> FusionResult:
        """融合多模态数据"""
        try:
            # 提取特征
            for modality in modalities:
                if not modality.processed:
                    self.feature_extractor.extract_features(modality)
            
            # 过滤有效模态
            valid_modalities = [m for m in modalities if m.features is not None and len(m.features) > 0]
            
            if not valid_modalities:
                logger.warning("没有有效的模态数据进行融合")
                return self._create_empty_fusion_result(modalities, strategy)
            
            # 执行融合
            fusion_func = self.fusion_strategies.get(strategy, self._hybrid_fusion)
            fused_features, confidence, quality_score = fusion_func(valid_modalities)
            
            # 创建融合结果
            fusion_result = FusionResult(
                fusion_id=f"fusion_{int(time.time())}_{len(self.fusion_history)}",
                strategy=strategy,
                input_modalities=[m.modality_id for m in valid_modalities],
                fused_features=fused_features,
                confidence=confidence,
                quality_score=quality_score,
                timestamp=time.time(),
                metadata={
                    "modality_types": [m.modality_type.value for m in valid_modalities],
                    "feature_dimensions": [len(m.features) for m in valid_modalities],
                    "total_features": len(fused_features)
                }
            )
            
            # 记录融合历史
            self.fusion_history.append(fusion_result)
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"数据融合失败: {str(e)}")
            return self._create_empty_fusion_result(modalities, strategy)
    
    def _early_fusion(self, modalities: List[ModalityData]) -> Tuple[np.ndarray, float, float]:
        """早期融合（特征级融合）"""
        # 直接连接所有特征
        all_features = []
        total_confidence = 0
        total_quality = 0
        
        for modality in modalities:
            all_features.extend(modality.features)
            total_confidence += modality.confidence
            total_quality += modality.quality_score
        
        fused_features = np.array(all_features)
        avg_confidence = total_confidence / len(modalities)
        avg_quality = total_quality / len(modalities)
        
        return fused_features, avg_confidence, avg_quality
    
    def _late_fusion(self, modalities: List[ModalityData]) -> Tuple[np.ndarray, float, float]:
        """晚期融合（决策级融合）"""
        # 对每个模态单独处理，然后融合决策
        decisions = []
        confidences = []
        qualities = []
        
        for modality in modalities:
            # 简化的决策：使用特征的统计量作为决策
            decision = np.array([
                np.mean(modality.features),
                np.std(modality.features),
                np.max(modality.features),
                np.min(modality.features)
            ])
            decisions.extend(decision)
            confidences.append(modality.confidence)
            qualities.append(modality.quality_score)
        
        fused_features = np.array(decisions)
        avg_confidence = np.mean(confidences)
        avg_quality = np.mean(qualities)
        
        return fused_features, avg_confidence, avg_quality
    
    def _hybrid_fusion(self, modalities: List[ModalityData]) -> Tuple[np.ndarray, float, float]:
        """混合融合"""
        # 结合早期和晚期融合
        early_features, early_conf, early_qual = self._early_fusion(modalities)
        late_features, late_conf, late_qual = self._late_fusion(modalities)
        
        # 加权组合
        weight_early = 0.7
        weight_late = 0.3
        
        # 特征维度对齐
        min_dim = min(len(early_features), len(late_features))
        early_features = early_features[:min_dim]
        late_features = late_features[:min_dim]
        
        fused_features = weight_early * early_features + weight_late * late_features
        confidence = weight_early * early_conf + weight_late * late_conf
        quality = weight_early * early_qual + weight_late * late_qual
        
        return fused_features, confidence, quality
    
    def _attention_fusion(self, modalities: List[ModalityData]) -> Tuple[np.ndarray, float, float]:
        """注意力融合"""
        # 基于质量分数计算注意力权重
        qualities = np.array([m.quality_score for m in modalities])
        confidences = np.array([m.confidence for m in modalities])
        
        # 计算注意力权重
        attention_weights = qualities * confidences
        attention_weights = attention_weights / np.sum(attention_weights)
        
        # 加权融合特征
        max_feature_dim = max(len(m.features) for m in modalities)
        fused_features = np.zeros(max_feature_dim)
        
        for i, modality in enumerate(modalities):
            features = modality.features
            # 填充或截断特征到统一维度
            if len(features) < max_feature_dim:
                features = np.pad(features, (0, max_feature_dim - len(features)))
            else:
                features = features[:max_feature_dim]
            
            fused_features += attention_weights[i] * features
        
        avg_confidence = np.sum(attention_weights * confidences)
        avg_quality = np.sum(attention_weights * qualities)
        
        return fused_features, avg_confidence, avg_quality
    
    def _weighted_fusion(self, modalities: List[ModalityData]) -> Tuple[np.ndarray, float, float]:
        """加权融合"""
        # 基于模态类型的预定义权重
        modality_weights = {
            ModalityType.SENSOR_DATA: 0.2,
            ModalityType.BEHAVIORAL_DATA: 0.25,
            ModalityType.PHYSIOLOGICAL_DATA: 0.2,
            ModalityType.ENVIRONMENTAL_DATA: 0.15,
            ModalityType.VISUAL_DATA: 0.1,
            ModalityType.AUDIO_DATA: 0.05,
            ModalityType.CONTEXTUAL_DATA: 0.03,
            ModalityType.TEMPORAL_DATA: 0.02
        }
        
        # 计算加权特征
        weighted_features = []
        total_weight = 0
        weighted_confidence = 0
        weighted_quality = 0
        
        for modality in modalities:
            weight = modality_weights.get(modality.modality_type, 0.1)
            weighted_features.extend(weight * modality.features)
            total_weight += weight
            weighted_confidence += weight * modality.confidence
            weighted_quality += weight * modality.quality_score
        
        fused_features = np.array(weighted_features)
        avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0
        avg_quality = weighted_quality / total_weight if total_weight > 0 else 0
        
        return fused_features, avg_confidence, avg_quality
    
    def _create_empty_fusion_result(self, modalities: List[ModalityData], 
                                  strategy: FusionStrategy) -> FusionResult:
        """创建空的融合结果"""
        return FusionResult(
            fusion_id=f"empty_fusion_{int(time.time())}",
            strategy=strategy,
            input_modalities=[m.modality_id for m in modalities],
            fused_features=np.array([]),
            confidence=0.0,
            quality_score=0.0,
            timestamp=time.time(),
            metadata={"error": "No valid modalities for fusion"}
        )


class AnalysisEngine:
    """分析引擎"""
    
    def __init__(self):
        self.analyzers = {
            AnalysisType.PATTERN_RECOGNITION: self._pattern_recognition,
            AnalysisType.ANOMALY_DETECTION: self._anomaly_detection,
            AnalysisType.TREND_ANALYSIS: self._trend_analysis,
            AnalysisType.CORRELATION_ANALYSIS: self._correlation_analysis,
            AnalysisType.PREDICTIVE_ANALYSIS: self._predictive_analysis,
            AnalysisType.CLUSTERING_ANALYSIS: self._clustering_analysis,
            AnalysisType.CLASSIFICATION: self._classification,
            AnalysisType.REGRESSION: self._regression
        }
        self.analysis_history = deque(maxlen=1000)
        self.pattern_templates = self._initialize_pattern_templates()
    
    def analyze(self, data: Union[FusionResult, ModalityData], 
               analysis_types: List[AnalysisType]) -> List[AnalysisResult]:
        """执行分析"""
        try:
            results = []
            
            # 获取特征数据
            if isinstance(data, FusionResult):
                features = data.fused_features
                data_id = data.fusion_id
                confidence_base = data.confidence
            else:
                features = data.features if data.features is not None else np.array([])
                data_id = data.modality_id
                confidence_base = data.confidence
            
            if len(features) == 0:
                logger.warning("没有有效特征进行分析")
                return results
            
            # 执行各种分析
            for analysis_type in analysis_types:
                analyzer = self.analyzers.get(analysis_type)
                if analyzer:
                    try:
                        analysis_result = analyzer(features, confidence_base)
                        analysis_result.analysis_id = f"analysis_{analysis_type.value}_{int(time.time())}"
                        analysis_result.input_data = data_id
                        analysis_result.timestamp = time.time()
                        
                        results.append(analysis_result)
                        self.analysis_history.append(analysis_result)
                        
                    except Exception as e:
                        logger.error(f"分析 {analysis_type.value} 失败: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"执行分析失败: {str(e)}")
            return []
    
    def _initialize_pattern_templates(self) -> Dict[str, Dict[str, Any]]:
        """初始化模式模板"""
        return {
            "stress_pattern": {
                "features": ["high_heart_rate", "low_hrv", "high_cortisol"],
                "thresholds": [100, 20, 15],
                "confidence_threshold": 0.7
            },
            "fatigue_pattern": {
                "features": ["slow_response", "low_activity", "eye_strain"],
                "thresholds": [2.0, 0.3, 0.8],
                "confidence_threshold": 0.6
            },
            "focus_pattern": {
                "features": ["stable_gaze", "low_movement", "consistent_interaction"],
                "thresholds": [0.1, 0.2, 0.8],
                "confidence_threshold": 0.8
            },
            "distraction_pattern": {
                "features": ["erratic_gaze", "high_movement", "inconsistent_interaction"],
                "thresholds": [0.5, 0.7, 0.3],
                "confidence_threshold": 0.7
            }
        }
    
    def _pattern_recognition(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """模式识别分析"""
        recognized_patterns = []
        pattern_confidences = []
        
        for pattern_name, pattern_template in self.pattern_templates.items():
            # 简化的模式匹配：基于特征统计量
            pattern_score = self._calculate_pattern_score(features, pattern_template)
            
            if pattern_score > pattern_template["confidence_threshold"]:
                recognized_patterns.append(pattern_name)
                pattern_confidences.append(pattern_score)
        
        results = {
            "recognized_patterns": recognized_patterns,
            "pattern_confidences": pattern_confidences,
            "dominant_pattern": recognized_patterns[0] if recognized_patterns else None,
            "pattern_strength": max(pattern_confidences) if pattern_confidences else 0.0
        }
        
        confidence = confidence_base * (max(pattern_confidences) if pattern_confidences else 0.5)
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.PATTERN_RECOGNITION,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _calculate_pattern_score(self, features: np.ndarray, pattern_template: Dict[str, Any]) -> float:
        """计算模式匹配分数"""
        if len(features) == 0:
            return 0.0
        
        # 简化的模式匹配：基于特征的统计特性
        feature_stats = [
            np.mean(features),
            np.std(features),
            np.max(features),
            np.min(features)
        ]
        
        # 计算与模式模板的相似度
        thresholds = pattern_template.get("thresholds", [0.5] * len(feature_stats))
        
        scores = []
        for i, (stat, threshold) in enumerate(zip(feature_stats, thresholds)):
            if threshold > 0:
                score = min(1.0, stat / threshold)
            else:
                score = 0.5
            scores.append(score)
        
        return np.mean(scores)
    
    def _anomaly_detection(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """异常检测分析"""
        if len(features) < 2:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.ANOMALY_DETECTION,
                input_data="",
                results={"anomaly_detected": False, "anomaly_score": 0.0},
                confidence=0.0,
                timestamp=0
            )
        
        # 使用Z-score检测异常
        z_scores = np.abs((features - np.mean(features)) / np.std(features))
        anomaly_threshold = 2.5
        
        anomalies = z_scores > anomaly_threshold
        anomaly_score = np.max(z_scores) if len(z_scores) > 0 else 0.0
        anomaly_detected = np.any(anomalies)
        
        results = {
            "anomaly_detected": anomaly_detected,
            "anomaly_score": float(anomaly_score),
            "anomaly_indices": np.where(anomalies)[0].tolist(),
            "anomaly_count": int(np.sum(anomalies)),
            "anomaly_percentage": float(np.mean(anomalies) * 100)
        }
        
        confidence = confidence_base * (0.9 if anomaly_detected else 0.7)
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _trend_analysis(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """趋势分析"""
        if len(features) < 3:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.TREND_ANALYSIS,
                input_data="",
                results={"trend": "insufficient_data"},
                confidence=0.0,
                timestamp=0
            )
        
        # 计算趋势
        x = np.arange(len(features))
        slope = np.polyfit(x, features, 1)[0]
        
        # 趋势分类
        if slope > 0.1:
            trend = "increasing"
        elif slope < -0.1:
            trend = "decreasing"
        else:
            trend = "stable"
        
        # 计算趋势强度
        correlation = np.corrcoef(x, features)[0, 1]
        trend_strength = abs(correlation)
        
        results = {
            "trend": trend,
            "slope": float(slope),
            "trend_strength": float(trend_strength),
            "correlation": float(correlation),
            "trend_confidence": float(trend_strength)
        }
        
        confidence = confidence_base * trend_strength
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.TREND_ANALYSIS,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _correlation_analysis(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """相关性分析"""
        if len(features) < 4:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.CORRELATION_ANALYSIS,
                input_data="",
                results={"correlations": []},
                confidence=0.0,
                timestamp=0
            )
        
        # 将特征分成两半进行相关性分析
        mid = len(features) // 2
        part1 = features[:mid]
        part2 = features[mid:2*mid]
        
        if len(part1) == len(part2) and len(part1) > 1:
            correlation = np.corrcoef(part1, part2)[0, 1]
            correlation_strength = abs(correlation)
        else:
            correlation = 0.0
            correlation_strength = 0.0
        
        results = {
            "correlation": float(correlation),
            "correlation_strength": float(correlation_strength),
            "correlation_type": "positive" if correlation > 0 else "negative" if correlation < 0 else "none"
        }
        
        confidence = confidence_base * correlation_strength
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.CORRELATION_ANALYSIS,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _predictive_analysis(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """预测分析"""
        if len(features) < 5:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.PREDICTIVE_ANALYSIS,
                input_data="",
                results={"prediction": None},
                confidence=0.0,
                timestamp=0
            )
        
        # 简单的线性预测
        x = np.arange(len(features))
        coeffs = np.polyfit(x, features, 1)
        
        # 预测下一个值
        next_x = len(features)
        predicted_value = np.polyval(coeffs, next_x)
        
        # 计算预测置信度（基于拟合优度）
        fitted_values = np.polyval(coeffs, x)
        r_squared = 1 - np.sum((features - fitted_values) ** 2) / np.sum((features - np.mean(features)) ** 2)
        
        results = {
            "predicted_value": float(predicted_value),
            "prediction_confidence": float(r_squared),
            "trend_slope": float(coeffs[0]),
            "r_squared": float(r_squared)
        }
        
        confidence = confidence_base * r_squared
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.PREDICTIVE_ANALYSIS,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _clustering_analysis(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """聚类分析"""
        if len(features) < 6:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.CLUSTERING_ANALYSIS,
                input_data="",
                results={"clusters": 0},
                confidence=0.0,
                timestamp=0
            )
        
        # 将特征重塑为2D数组进行聚类
        features_2d = features.reshape(-1, 1)
        
        try:
            # 使用DBSCAN聚类
            clustering = DBSCAN(eps=0.5, min_samples=2)
            cluster_labels = clustering.fit_predict(features_2d)
            
            n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
            n_noise = list(cluster_labels).count(-1)
            
            results = {
                "n_clusters": n_clusters,
                "n_noise_points": n_noise,
                "cluster_labels": cluster_labels.tolist(),
                "silhouette_score": 0.5  # 简化的轮廓系数
            }
            
            confidence = confidence_base * (0.8 if n_clusters > 0 else 0.3)
            
        except Exception as e:
            logger.error(f"聚类分析失败: {str(e)}")
            results = {"clusters": 0, "error": str(e)}
            confidence = 0.0
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.CLUSTERING_ANALYSIS,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _classification(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """分类分析"""
        # 简化的分类：基于特征统计量
        mean_val = np.mean(features)
        std_val = np.std(features)
        
        # 基于统计量进行分类
        if mean_val > 0.7 and std_val < 0.2:
            class_label = "high_stable"
            class_confidence = 0.9
        elif mean_val > 0.7 and std_val >= 0.2:
            class_label = "high_variable"
            class_confidence = 0.8
        elif mean_val <= 0.3 and std_val < 0.2:
            class_label = "low_stable"
            class_confidence = 0.9
        elif mean_val <= 0.3 and std_val >= 0.2:
            class_label = "low_variable"
            class_confidence = 0.8
        else:
            class_label = "medium"
            class_confidence = 0.7
        
        results = {
            "class_label": class_label,
            "class_confidence": class_confidence,
            "feature_mean": float(mean_val),
            "feature_std": float(std_val)
        }
        
        confidence = confidence_base * class_confidence
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.CLASSIFICATION,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )
    
    def _regression(self, features: np.ndarray, confidence_base: float) -> AnalysisResult:
        """回归分析"""
        if len(features) < 3:
            return AnalysisResult(
                analysis_id="",
                analysis_type=AnalysisType.REGRESSION,
                input_data="",
                results={"regression_coefficients": []},
                confidence=0.0,
                timestamp=0
            )
        
        # 简单线性回归
        x = np.arange(len(features))
        coeffs = np.polyfit(x, features, 1)
        
        # 计算拟合优度
        fitted_values = np.polyval(coeffs, x)
        ss_res = np.sum((features - fitted_values) ** 2)
        ss_tot = np.sum((features - np.mean(features)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        results = {
            "regression_coefficients": coeffs.tolist(),
            "r_squared": float(r_squared),
            "slope": float(coeffs[0]),
            "intercept": float(coeffs[1]),
            "fitted_values": fitted_values.tolist()
        }
        
        confidence = confidence_base * r_squared
        
        return AnalysisResult(
            analysis_id="",
            analysis_type=AnalysisType.REGRESSION,
            input_data="",
            results=results,
            confidence=confidence,
            timestamp=0
        )


class MultimodalFusionAnalyzer:
    """多模态融合分析器核心类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化多模态融合分析器
        
        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("multimodal_fusion", {}).get("enabled", True)
        
        # 子模块
        self.feature_extractor = FeatureExtractor()
        self.fusion_engine = DataFusionEngine()
        self.analysis_engine = AnalysisEngine()
        
        # 数据存储
        self.modality_buffer = defaultdict(deque)  # modality_type -> deque of ModalityData
        self.fusion_results = deque(maxlen=500)
        self.analysis_results = deque(maxlen=1000)
        
        # 配置参数
        self.buffer_size = config.get("multimodal_fusion", {}).get("buffer_size", 100)
        self.fusion_interval = config.get("multimodal_fusion", {}).get("fusion_interval", 5.0)
        self.analysis_interval = config.get("multimodal_fusion", {}).get("analysis_interval", 10.0)
        
        # 统计信息
        self.stats = {
            "total_modalities_processed": 0,
            "total_fusions_performed": 0,
            "total_analyses_performed": 0,
            "average_fusion_confidence": 0.0,
            "average_analysis_confidence": 0.0
        }
        
        # 定时任务
        self._fusion_task = None
        self._analysis_task = None
        
        logger.info(f"多模态融合分析器初始化完成 - 启用: {self.enabled}")
    
    async def process_modality_data(self, modality_data: ModalityData) -> Dict[str, Any]:
        """
        处理模态数据
        
        Args:
            modality_data: 模态数据
            
        Returns:
            处理结果
        """
        if not self.enabled:
            return {"status": "disabled"}
        
        try:
            # 提取特征
            features = self.feature_extractor.extract_features(modality_data)
            
            # 添加到缓冲区
            self.modality_buffer[modality_data.modality_type].append(modality_data)
            
            # 保持缓冲区大小
            if len(self.modality_buffer[modality_data.modality_type]) > self.buffer_size:
                self.modality_buffer[modality_data.modality_type].popleft()
            
            # 更新统计信息
            self.stats["total_modalities_processed"] += 1
            
            return {
                "status": "success",
                "modality_id": modality_data.modality_id,
                "features_extracted": len(features),
                "buffer_size": len(self.modality_buffer[modality_data.modality_type])
            }
            
        except Exception as e:
            logger.error(f"处理模态数据失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def perform_fusion(self, modality_types: Optional[List[ModalityType]] = None,
                           strategy: FusionStrategy = FusionStrategy.HYBRID_FUSION) -> Optional[FusionResult]:
        """
        执行数据融合
        
        Args:
            modality_types: 要融合的模态类型列表，None表示融合所有可用模态
            strategy: 融合策略
            
        Returns:
            融合结果
        """
        if not self.enabled:
            return None
        
        try:
            # 获取要融合的模态数据
            modalities_to_fuse = []
            
            if modality_types is None:
                # 融合所有可用模态的最新数据
                for modality_type, buffer in self.modality_buffer.items():
                    if buffer:
                        modalities_to_fuse.append(buffer[-1])  # 取最新数据
            else:
                # 融合指定模态类型的数据
                for modality_type in modality_types:
                    buffer = self.modality_buffer.get(modality_type)
                    if buffer:
                        modalities_to_fuse.append(buffer[-1])
            
            if not modalities_to_fuse:
                logger.warning("没有可用的模态数据进行融合")
                return None
            
            # 执行融合
            fusion_result = self.fusion_engine.fuse_modalities(modalities_to_fuse, strategy)
            
            # 存储融合结果
            self.fusion_results.append(fusion_result)
            
            # 更新统计信息
            self.stats["total_fusions_performed"] += 1
            self.stats["average_fusion_confidence"] = (
                (self.stats["average_fusion_confidence"] * (self.stats["total_fusions_performed"] - 1) + 
                 fusion_result.confidence) / self.stats["total_fusions_performed"]
            )
            
            logger.info(f"数据融合完成 - ID: {fusion_result.fusion_id}, 置信度: {fusion_result.confidence:.3f}")
            
            return fusion_result
            
        except Exception as e:
            logger.error(f"执行数据融合失败: {str(e)}")
            return None
    
    async def perform_analysis(self, data: Union[FusionResult, ModalityData],
                             analysis_types: List[AnalysisType]) -> List[AnalysisResult]:
        """
        执行分析
        
        Args:
            data: 要分析的数据（融合结果或模态数据）
            analysis_types: 分析类型列表
            
        Returns:
            分析结果列表
        """
        if not self.enabled:
            return []
        
        try:
            # 执行分析
            analysis_results = self.analysis_engine.analyze(data, analysis_types)
            
            # 存储分析结果
            self.analysis_results.extend(analysis_results)
            
            # 更新统计信息
            self.stats["total_analyses_performed"] += len(analysis_results)
            if analysis_results:
                avg_confidence = np.mean([r.confidence for r in analysis_results])
                self.stats["average_analysis_confidence"] = (
                    (self.stats["average_analysis_confidence"] * 
                     (self.stats["total_analyses_performed"] - len(analysis_results)) + 
                     avg_confidence * len(analysis_results)) / self.stats["total_analyses_performed"]
                )
            
            logger.info(f"分析完成 - 执行了 {len(analysis_results)} 个分析")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"执行分析失败: {str(e)}")
            return []
    
    async def get_comprehensive_analysis(self, modality_types: Optional[List[ModalityType]] = None) -> Dict[str, Any]:
        """
        获取综合分析结果
        
        Args:
            modality_types: 要分析的模态类型列表
            
        Returns:
            综合分析结果
        """
        try:
            # 执行数据融合
            fusion_result = await self.perform_fusion(modality_types)
            
            if not fusion_result:
                return {"status": "no_fusion_result"}
            
            # 执行多种分析
            analysis_types = [
                AnalysisType.PATTERN_RECOGNITION,
                AnalysisType.ANOMALY_DETECTION,
                AnalysisType.TREND_ANALYSIS,
                AnalysisType.PREDICTIVE_ANALYSIS
            ]
            
            analysis_results = await self.perform_analysis(fusion_result, analysis_types)
            
            # 整合分析结果
            comprehensive_result = {
                "fusion_info": {
                    "fusion_id": fusion_result.fusion_id,
                    "strategy": fusion_result.strategy.value,
                    "confidence": fusion_result.confidence,
                    "quality_score": fusion_result.quality_score,
                    "input_modalities": fusion_result.input_modalities
                },
                "analyses": {}
            }
            
            for result in analysis_results:
                comprehensive_result["analyses"][result.analysis_type.value] = {
                    "results": result.results,
                    "confidence": result.confidence
                }
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"获取综合分析失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_modality_status(self) -> Dict[str, Any]:
        """获取模态状态"""
        status = {}
        
        for modality_type, buffer in self.modality_buffer.items():
            if buffer:
                latest_data = buffer[-1]
                status[modality_type.value] = {
                    "buffer_size": len(buffer),
                    "latest_timestamp": latest_data.timestamp,
                    "latest_quality": latest_data.quality_score,
                    "latest_confidence": latest_data.confidence,
                    "features_available": latest_data.processed
                }
            else:
                status[modality_type.value] = {
                    "buffer_size": 0,
                    "latest_timestamp": None,
                    "latest_quality": 0.0,
                    "latest_confidence": 0.0,
                    "features_available": False
                }
        
        return status
    
    def get_fusion_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取融合历史"""
        recent_fusions = list(self.fusion_results)[-limit:]
        
        return [
            {
                "fusion_id": fr.fusion_id,
                "strategy": fr.strategy.value,
                "confidence": fr.confidence,
                "quality_score": fr.quality_score,
                "timestamp": fr.timestamp,
                "input_modalities": fr.input_modalities,
                "feature_count": len(fr.fused_features)
            }
            for fr in recent_fusions
        ]
    
    def get_analysis_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取分析历史"""
        recent_analyses = list(self.analysis_results)[-limit:]
        
        return [
            {
                "analysis_id": ar.analysis_id,
                "analysis_type": ar.analysis_type.value,
                "confidence": ar.confidence,
                "timestamp": ar.timestamp,
                "input_data": ar.input_data,
                "results_summary": self._summarize_analysis_results(ar.results)
            }
            for ar in recent_analyses
        ]
    
    def _summarize_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """总结分析结果"""
        summary = {}
        
        for key, value in results.items():
            if isinstance(value, (int, float, bool, str)):
                summary[key] = value
            elif isinstance(value, list) and len(value) <= 5:
                summary[key] = value
            elif isinstance(value, dict) and len(value) <= 3:
                summary[key] = value
            else:
                summary[f"{key}_type"] = type(value).__name__
                summary[f"{key}_length"] = len(value) if hasattr(value, '__len__') else 1
        
        return summary
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "enabled": self.enabled,
            "modality_buffer_sizes": {
                mt.value: len(buffer) for mt, buffer in self.modality_buffer.items()
            },
            "fusion_results_count": len(self.fusion_results),
            "analysis_results_count": len(self.analysis_results),
            **self.stats
        }
    
    async def start_background_processing(self):
        """启动后台处理任务"""
        if not self.enabled:
            return
        
        logger.info("启动多模态融合分析器后台处理任务")
        
        # 启动定时融合任务
        self._fusion_task = asyncio.create_task(self._background_fusion_loop())
        
        # 启动定时分析任务
        self._analysis_task = asyncio.create_task(self._background_analysis_loop())
    
    async def _background_fusion_loop(self):
        """后台融合循环"""
        while True:
            try:
                await asyncio.sleep(self.fusion_interval)
                
                # 检查是否有足够的数据进行融合
                available_modalities = [
                    mt for mt, buffer in self.modality_buffer.items() if buffer
                ]
                
                if len(available_modalities) >= 2:
                    await self.perform_fusion()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"后台融合任务错误: {str(e)}")
    
    async def _background_analysis_loop(self):
        """后台分析循环"""
        while True:
            try:
                await asyncio.sleep(self.analysis_interval)
                
                # 分析最新的融合结果
                if self.fusion_results:
                    latest_fusion = self.fusion_results[-1]
                    analysis_types = [
                        AnalysisType.PATTERN_RECOGNITION,
                        AnalysisType.ANOMALY_DETECTION
                    ]
                    await self.perform_analysis(latest_fusion, analysis_types)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"后台分析任务错误: {str(e)}")
    
    async def shutdown(self):
        """关闭多模态融合分析器"""
        logger.info("正在关闭多模态融合分析器...")
        
        # 取消后台任务
        if self._fusion_task:
            self._fusion_task.cancel()
            try:
                await self._fusion_task
            except asyncio.CancelledError:
                pass
        
        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass
        
        logger.info("多模态融合分析器已关闭") 