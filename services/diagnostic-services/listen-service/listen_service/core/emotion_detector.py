"""
情绪检测器

基于音频特征进行情绪识别和分析。
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
import structlog

from ..models.emotion_models import (
    EmotionType, EmotionScore, EmotionAnalysis, MoodState, MoodLevel
)
from ..models.audio_models import AudioFeature, SoundFeatures
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


class EmotionDetector:
    """情绪检测器"""
    
    def __init__(self):
        self.emotion_models = self._initialize_emotion_models()
        self.feature_weights = self._get_feature_weights()
        
    def _initialize_emotion_models(self) -> Dict[str, Dict]:
        """初始化情绪识别模型"""
        return {
            "prosodic": {
                "pitch_range": {"joy": 0.8, "anger": 0.7, "sadness": 0.2, "fear": 0.6},
                "tempo": {"joy": 0.7, "anger": 0.8, "sadness": 0.3, "fear": 0.5},
                "volume": {"joy": 0.6, "anger": 0.9, "sadness": 0.3, "fear": 0.4}
            },
            "spectral": {
                "formant_dispersion": {"joy": 0.7, "anger": 0.6, "sadness": 0.4, "fear": 0.5},
                "spectral_centroid": {"joy": 0.6, "anger": 0.7, "sadness": 0.3, "fear": 0.5}
            },
            "voice_quality": {
                "jitter": {"neutral": 0.1, "anger": 0.8, "sadness": 0.6, "fear": 0.7},
                "shimmer": {"neutral": 0.1, "anger": 0.7, "sadness": 0.5, "fear": 0.6}
            }
        }
    
    def _get_feature_weights(self) -> Dict[str, float]:
        """获取特征权重"""
        return {
            "pitch_mean": 0.15,
            "pitch_std": 0.12,
            "intensity_mean": 0.10,
            "intensity_std": 0.08,
            "speaking_rate": 0.12,
            "pause_duration": 0.10,
            "jitter": 0.08,
            "shimmer": 0.08,
            "spectral_centroid": 0.09,
            "spectral_bandwidth": 0.08
        }
    
    @async_timer
    async def detect_emotion(
        self, 
        audio_features: List[AudioFeature],
        sound_features: Optional[SoundFeatures] = None
    ) -> EmotionAnalysis:
        """
        检测音频中的情绪
        
        Args:
            audio_features: 音频特征列表
            sound_features: 声音特征
            
        Returns:
            情绪分析结果
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # 提取情绪相关特征
            emotion_features = self._extract_emotion_features(audio_features, sound_features)
            
            # 计算各种情绪的得分
            emotion_scores = await self._calculate_emotion_scores(emotion_features)
            
            # 确定主要情绪
            primary_emotion = max(emotion_scores, key=lambda x: x.score)
            
            # 计算整体情绪指标
            valence, arousal = self._calculate_valence_arousal(emotion_scores)
            stability = self._calculate_emotional_stability(emotion_scores)
            confidence = self._calculate_confidence(emotion_scores)
            
            # 分析使用的特征
            features_used = list(emotion_features.keys())
            
            end_time = asyncio.get_event_loop().time()
            analysis_duration = (end_time - start_time) * 1000
            
            return EmotionAnalysis(
                primary_emotion=primary_emotion.emotion_type,
                emotion_scores=emotion_scores,
                overall_valence=valence,
                overall_arousal=arousal,
                stability=stability,
                confidence=confidence,
                analysis_duration_ms=analysis_duration,
                audio_features_used=features_used
            )
            
        except Exception as e:
            logger.error("情绪检测失败", error=str(e), exc_info=True)
            # 返回默认的中性情绪分析
            return EmotionAnalysis(
                primary_emotion=EmotionType.NEUTRAL,
                emotion_scores=[EmotionScore(
                    emotion_type=EmotionType.NEUTRAL,
                    score=1.0,
                    confidence=0.5,
                    intensity="moderate"
                )],
                overall_valence=0.0,
                overall_arousal=0.0,
                stability=1.0,
                confidence=0.5,
                analysis_duration_ms=0.0,
                audio_features_used=[]
            )
    
    def _extract_emotion_features(
        self, 
        audio_features: List[AudioFeature],
        sound_features: Optional[SoundFeatures]
    ) -> Dict[str, float]:
        """提取情绪相关特征"""
        features = {}
        
        # 从音频特征中提取
        for feature in audio_features:
            if feature.feature_type in self.feature_weights:
                features[feature.feature_type] = float(feature.value)
        
        # 从声音特征中提取
        if sound_features:
            features.update({
                "fundamental_frequency": sound_features.fundamental_frequency,
                "spectral_centroid": sound_features.spectral_centroid,
                "spectral_bandwidth": sound_features.spectral_bandwidth,
                "zero_crossing_rate": sound_features.zero_crossing_rate,
                "energy": sound_features.energy
            })
        
        return features
    
    async def _calculate_emotion_scores(
        self, 
        features: Dict[str, float]
    ) -> List[EmotionScore]:
        """计算各种情绪的得分"""
        emotion_scores = []
        
        for emotion_type in EmotionType:
            score = await self._calculate_single_emotion_score(emotion_type, features)
            confidence = self._calculate_emotion_confidence(emotion_type, features)
            intensity = self._determine_emotion_intensity(score)
            
            emotion_scores.append(EmotionScore(
                emotion_type=emotion_type,
                score=score,
                confidence=confidence,
                intensity=intensity
            ))
        
        return emotion_scores
    
    async def _calculate_single_emotion_score(
        self, 
        emotion_type: EmotionType, 
        features: Dict[str, float]
    ) -> float:
        """计算单个情绪的得分"""
        total_score = 0.0
        total_weight = 0.0
        
        # 基于韵律特征
        prosodic_score = self._calculate_prosodic_score(emotion_type, features)
        total_score += prosodic_score * 0.4
        total_weight += 0.4
        
        # 基于频谱特征
        spectral_score = self._calculate_spectral_score(emotion_type, features)
        total_score += spectral_score * 0.3
        total_weight += 0.3
        
        # 基于语音质量特征
        quality_score = self._calculate_quality_score(emotion_type, features)
        total_score += quality_score * 0.3
        total_weight += 0.3
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_prosodic_score(
        self, 
        emotion_type: EmotionType, 
        features: Dict[str, float]
    ) -> float:
        """计算韵律特征得分"""
        score = 0.0
        count = 0
        
        # 基音频率相关
        if "pitch_mean" in features:
            pitch_score = self._map_feature_to_emotion(
                "pitch_range", emotion_type.value, features["pitch_mean"]
            )
            score += pitch_score
            count += 1
        
        # 语速相关
        if "speaking_rate" in features:
            tempo_score = self._map_feature_to_emotion(
                "tempo", emotion_type.value, features["speaking_rate"]
            )
            score += tempo_score
            count += 1
        
        # 音量相关
        if "intensity_mean" in features:
            volume_score = self._map_feature_to_emotion(
                "volume", emotion_type.value, features["intensity_mean"]
            )
            score += volume_score
            count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_spectral_score(
        self, 
        emotion_type: EmotionType, 
        features: Dict[str, float]
    ) -> float:
        """计算频谱特征得分"""
        score = 0.0
        count = 0
        
        if "spectral_centroid" in features:
            centroid_score = self._map_feature_to_emotion(
                "spectral_centroid", emotion_type.value, features["spectral_centroid"]
            )
            score += centroid_score
            count += 1
        
        return score / count if count > 0 else 0.0
    
    def _calculate_quality_score(
        self, 
        emotion_type: EmotionType, 
        features: Dict[str, float]
    ) -> float:
        """计算语音质量特征得分"""
        score = 0.0
        count = 0
        
        if "jitter" in features:
            jitter_score = self._map_feature_to_emotion(
                "jitter", emotion_type.value, features["jitter"]
            )
            score += jitter_score
            count += 1
        
        if "shimmer" in features:
            shimmer_score = self._map_feature_to_emotion(
                "shimmer", emotion_type.value, features["shimmer"]
            )
            score += shimmer_score
            count += 1
        
        return score / count if count > 0 else 0.0
    
    def _map_feature_to_emotion(
        self, 
        feature_category: str, 
        emotion: str, 
        feature_value: float
    ) -> float:
        """将特征值映射到情绪得分"""
        # 简化的映射逻辑，实际应用中需要更复杂的模型
        if feature_category in self.emotion_models.get("prosodic", {}):
            emotion_mapping = self.emotion_models["prosodic"][feature_category]
        elif feature_category in self.emotion_models.get("spectral", {}):
            emotion_mapping = self.emotion_models["spectral"][feature_category]
        elif feature_category in self.emotion_models.get("voice_quality", {}):
            emotion_mapping = self.emotion_models["voice_quality"][feature_category]
        else:
            return 0.0
        
        return emotion_mapping.get(emotion, 0.0) * min(feature_value, 1.0)
    
    def _calculate_emotion_confidence(
        self, 
        emotion_type: EmotionType, 
        features: Dict[str, float]
    ) -> float:
        """计算情绪识别的置信度"""
        # 基于特征完整性和一致性计算置信度
        feature_completeness = len(features) / len(self.feature_weights)
        return min(feature_completeness * 0.8 + 0.2, 1.0)
    
    def _determine_emotion_intensity(self, score: float) -> str:
        """确定情绪强度"""
        if score >= 0.7:
            return "strong"
        elif score >= 0.4:
            return "moderate"
        else:
            return "weak"
    
    def _calculate_valence_arousal(
        self, 
        emotion_scores: List[EmotionScore]
    ) -> Tuple[float, float]:
        """计算效价和唤醒度"""
        # 情绪的效价和唤醒度映射
        emotion_mapping = {
            EmotionType.JOY: (0.8, 0.7),
            EmotionType.ANGER: (-0.6, 0.9),
            EmotionType.SADNESS: (-0.7, 0.3),
            EmotionType.FEAR: (-0.5, 0.8),
            EmotionType.SURPRISE: (0.2, 0.8),
            EmotionType.DISGUST: (-0.6, 0.5),
            EmotionType.NEUTRAL: (0.0, 0.0)
        }
        
        total_valence = 0.0
        total_arousal = 0.0
        total_weight = 0.0
        
        for emotion_score in emotion_scores:
            if emotion_score.emotion_type in emotion_mapping:
                valence, arousal = emotion_mapping[emotion_score.emotion_type]
                weight = emotion_score.score * emotion_score.confidence
                
                total_valence += valence * weight
                total_arousal += arousal * weight
                total_weight += weight
        
        if total_weight > 0:
            return total_valence / total_weight, total_arousal / total_weight
        else:
            return 0.0, 0.0
    
    def _calculate_emotional_stability(
        self, 
        emotion_scores: List[EmotionScore]
    ) -> float:
        """计算情绪稳定性"""
        # 基于情绪得分的方差计算稳定性
        scores = [score.score for score in emotion_scores]
        if len(scores) > 1:
            variance = np.var(scores)
            stability = 1.0 / (1.0 + variance)
            return min(stability, 1.0)
        return 1.0
    
    def _calculate_confidence(
        self, 
        emotion_scores: List[EmotionScore]
    ) -> float:
        """计算整体置信度"""
        if not emotion_scores:
            return 0.0
        
        # 基于最高得分和置信度的加权平均
        max_score = max(emotion_scores, key=lambda x: x.score)
        avg_confidence = sum(score.confidence for score in emotion_scores) / len(emotion_scores)
        
        return (max_score.score * 0.6 + avg_confidence * 0.4)
    
    async def analyze_mood_state(
        self, 
        emotion_analysis: EmotionAnalysis
    ) -> MoodState:
        """分析心境状态"""
        try:
            # 确定心境水平
            mood_level = self._determine_mood_level(emotion_analysis)
            
            # 确定主导情绪
            dominant_emotions = self._get_dominant_emotions(emotion_analysis.emotion_scores)
            
            # 计算能量水平
            energy_level = emotion_analysis.overall_arousal
            
            # 计算压力水平
            stress_level = self._calculate_stress_level(emotion_analysis)
            
            # 计算情绪平衡
            emotional_balance = emotion_analysis.stability
            
            # 生成心境描述
            mood_description = self._generate_mood_description(
                mood_level, dominant_emotions, energy_level
            )
            
            # 生成建议
            recommendations = self._generate_mood_recommendations(
                mood_level, dominant_emotions, stress_level
            )
            
            return MoodState(
                mood_level=mood_level,
                dominant_emotions=dominant_emotions,
                energy_level=energy_level,
                stress_level=stress_level,
                emotional_balance=emotional_balance,
                mood_description=mood_description,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error("心境状态分析失败", error=str(e), exc_info=True)
            return MoodState(
                mood_level=MoodLevel.NORMAL,
                dominant_emotions=[EmotionType.NEUTRAL],
                energy_level=0.5,
                stress_level=0.5,
                emotional_balance=0.5,
                mood_description="无法确定心境状态",
                recommendations=["建议重新进行音频分析"]
            )
    
    def _determine_mood_level(self, emotion_analysis: EmotionAnalysis) -> MoodLevel:
        """确定心境水平"""
        valence = emotion_analysis.overall_valence
        
        if valence >= 0.6:
            return MoodLevel.VERY_HIGH
        elif valence >= 0.2:
            return MoodLevel.HIGH
        elif valence >= -0.2:
            return MoodLevel.NORMAL
        elif valence >= -0.6:
            return MoodLevel.LOW
        else:
            return MoodLevel.VERY_LOW
    
    def _get_dominant_emotions(
        self, 
        emotion_scores: List[EmotionScore], 
        threshold: float = 0.3
    ) -> List[EmotionType]:
        """获取主导情绪"""
        dominant = [
            score.emotion_type for score in emotion_scores 
            if score.score >= threshold
        ]
        
        if not dominant:
            # 如果没有超过阈值的情绪，返回得分最高的
            max_emotion = max(emotion_scores, key=lambda x: x.score)
            dominant = [max_emotion.emotion_type]
        
        return dominant
    
    def _calculate_stress_level(self, emotion_analysis: EmotionAnalysis) -> float:
        """计算压力水平"""
        # 基于负面情绪和唤醒度计算压力
        negative_emotions = [EmotionType.ANGER, EmotionType.FEAR, EmotionType.SADNESS]
        negative_score = sum(
            score.score for score in emotion_analysis.emotion_scores
            if score.emotion_type in negative_emotions
        )
        
        stress = (negative_score / len(negative_emotions) + emotion_analysis.overall_arousal) / 2
        return min(stress, 1.0)
    
    def _generate_mood_description(
        self, 
        mood_level: MoodLevel, 
        dominant_emotions: List[EmotionType], 
        energy_level: float
    ) -> str:
        """生成心境描述"""
        level_desc = {
            MoodLevel.VERY_HIGH: "非常积极",
            MoodLevel.HIGH: "积极",
            MoodLevel.NORMAL: "平稳",
            MoodLevel.LOW: "低落",
            MoodLevel.VERY_LOW: "非常低落"
        }
        
        emotion_desc = {
            EmotionType.JOY: "愉悦",
            EmotionType.ANGER: "愤怒",
            EmotionType.SADNESS: "悲伤",
            EmotionType.FEAR: "恐惧",
            EmotionType.SURPRISE: "惊讶",
            EmotionType.DISGUST: "厌恶",
            EmotionType.NEUTRAL: "平静"
        }
        
        energy_desc = "高能量" if energy_level > 0.6 else "低能量" if energy_level < 0.4 else "中等能量"
        
        emotions_str = "、".join([emotion_desc.get(e, e.value) for e in dominant_emotions])
        
        return f"心境{level_desc[mood_level]}，主要表现为{emotions_str}，{energy_desc}状态"
    
    def _generate_mood_recommendations(
        self, 
        mood_level: MoodLevel, 
        dominant_emotions: List[EmotionType], 
        stress_level: float
    ) -> List[str]:
        """生成心境建议"""
        recommendations = []
        
        if mood_level in [MoodLevel.LOW, MoodLevel.VERY_LOW]:
            recommendations.extend([
                "建议进行放松训练或冥想",
                "适当进行户外活动",
                "与亲友交流分享感受"
            ])
        
        if EmotionType.ANGER in dominant_emotions:
            recommendations.append("建议进行深呼吸练习，控制情绪")
        
        if EmotionType.SADNESS in dominant_emotions:
            recommendations.append("建议寻求专业心理支持")
        
        if stress_level > 0.7:
            recommendations.extend([
                "建议减少工作压力",
                "保证充足睡眠",
                "进行适度运动"
            ])
        
        if not recommendations:
            recommendations.append("保持当前良好的情绪状态")
        
        return recommendations 