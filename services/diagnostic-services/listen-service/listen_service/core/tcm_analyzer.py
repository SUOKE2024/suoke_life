"""
中医特征提取器模块

基于传统中医理论的音频分析和诊断功能。
"""

import asyncio
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog
from scipy import stats
from sklearn.preprocessing import MinMaxScaler

from ..models.audio_models import AudioFeatures
from ..models.tcm_models import (
    ConstitutionType,
    EmotionState,
    OrganFunction,
    TCMDiagnosis,
    VoiceCharacteristics,
)
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


class VoiceQuality(Enum):
    """声音质量类型"""
    CLEAR = "clear"          # 清亮
    HOARSE = "hoarse"        # 嘶哑
    WEAK = "weak"            # 微弱
    ROUGH = "rough"          # 粗糙
    TREMBLING = "trembling"  # 颤抖
    NASAL = "nasal"          # 鼻音


class SpeechPattern(Enum):
    """语音模式"""
    FLUENT = "fluent"        # 流利
    HESITANT = "hesitant"    # 犹豫
    RAPID = "rapid"          # 急促
    SLOW = "slow"            # 缓慢
    INTERRUPTED = "interrupted"  # 断续


@dataclass
class TCMFeatures:
    """中医特征"""
    voice_quality: VoiceQuality
    speech_pattern: SpeechPattern
    energy_level: float
    breath_pattern: str
    emotional_tone: str
    constitution_indicators: Dict[str, float]
    organ_function_scores: Dict[str, float]


class TCMFeatureExtractor:
    """中医特征提取器"""
    
    def __init__(self):
        """初始化中医特征提取器"""
        self.scaler = MinMaxScaler()
        
        # 中医理论参数
        self.constitution_weights = {
            ConstitutionType.BALANCED: {
                "energy_stability": 0.3,
                "voice_clarity": 0.25,
                "breath_regularity": 0.25,
                "emotional_balance": 0.2
            },
            ConstitutionType.QI_DEFICIENCY: {
                "low_energy": 0.4,
                "weak_voice": 0.3,
                "shallow_breath": 0.3
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "low_energy": 0.35,
                "slow_speech": 0.25,
                "weak_voice": 0.25,
                "cold_indicators": 0.15
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "restless_energy": 0.3,
                "dry_voice": 0.25,
                "rapid_speech": 0.25,
                "heat_indicators": 0.2
            },
            ConstitutionType.PHLEGM_DAMPNESS: {
                "heavy_voice": 0.3,
                "slow_speech": 0.25,
                "thick_breath": 0.25,
                "dampness_indicators": 0.2
            },
            ConstitutionType.DAMP_HEAT: {
                "irritable_tone": 0.3,
                "rapid_speech": 0.25,
                "heavy_breath": 0.25,
                "heat_indicators": 0.2
            },
            ConstitutionType.BLOOD_STASIS: {
                "dark_tone": 0.3,
                "irregular_speech": 0.25,
                "blocked_breath": 0.25,
                "stasis_indicators": 0.2
            },
            ConstitutionType.QI_STAGNATION: {
                "tense_voice": 0.3,
                "irregular_speech": 0.25,
                "sighing_breath": 0.25,
                "stress_indicators": 0.2
            },
            ConstitutionType.SPECIAL: {
                "allergic_indicators": 0.4,
                "sensitive_voice": 0.3,
                "irregular_patterns": 0.3
            }
        }
        
        # 五脏功能评估权重
        self.organ_weights = {
            "heart": {
                "speech_fluency": 0.3,
                "emotional_expression": 0.3,
                "voice_rhythm": 0.25,
                "joy_indicators": 0.15
            },
            "liver": {
                "voice_tension": 0.3,
                "emotional_control": 0.3,
                "speech_smoothness": 0.25,
                "anger_indicators": 0.15
            },
            "spleen": {
                "voice_strength": 0.3,
                "speech_clarity": 0.25,
                "thinking_patterns": 0.25,
                "worry_indicators": 0.2
            },
            "lung": {
                "breath_quality": 0.35,
                "voice_clarity": 0.25,
                "speech_volume": 0.25,
                "sadness_indicators": 0.15
            },
            "kidney": {
                "voice_depth": 0.3,
                "energy_foundation": 0.3,
                "speech_stability": 0.25,
                "fear_indicators": 0.15
            }
        }
        
        logger.info("中医特征提取器初始化完成")
    
    async def initialize(self) -> None:
        """初始化中医特征提取器"""
        # 这里可以添加任何需要异步初始化的资源
        logger.info("中医特征提取器异步初始化完成")
    
    @async_timer
    async def extract_tcm_features(
        self,
        audio_features: AudioFeatures,
        enable_constitution_analysis: bool = True,
        enable_emotion_analysis: bool = True
    ) -> TCMDiagnosis:
        """提取中医特征并进行诊断"""
        try:
            # 分析声音特征
            voice_characteristics = await self._analyze_voice_characteristics(audio_features)
            
            # 体质分析
            constitution_analysis = None
            if enable_constitution_analysis:
                constitution_analysis = await self._analyze_constitution(
                    audio_features, voice_characteristics
                )
            
            # 情志分析
            emotion_analysis = None
            if enable_emotion_analysis:
                emotion_analysis = await self._analyze_emotions(
                    audio_features, voice_characteristics
                )
            
            # 脏腑功能评估
            organ_functions = await self._assess_organ_functions(
                audio_features, voice_characteristics
            )
            
            # 生成诊断建议
            recommendations = await self._generate_recommendations(
                voice_characteristics,
                constitution_analysis,
                emotion_analysis,
                organ_functions
            )
            
            diagnosis = TCMDiagnosis(
                voice_characteristics=voice_characteristics,
                constitution_type=constitution_analysis,
                emotion_state=emotion_analysis,
                organ_functions=organ_functions,
                recommendations=recommendations,
                confidence_score=self._calculate_confidence_score(
                    voice_characteristics, constitution_analysis, emotion_analysis
                ),
                analysis_timestamp=time.time()
            )
            
            logger.info(
                "中医特征提取完成",
                constitution=constitution_analysis.value if constitution_analysis else None,
                emotion=emotion_analysis.value if emotion_analysis else None,
                confidence=diagnosis.confidence_score
            )
            
            return diagnosis
            
        except Exception as e:
            logger.error("中医特征提取失败", error=str(e), exc_info=True)
            raise
    
    async def _analyze_voice_characteristics(
        self,
        audio_features: AudioFeatures
    ) -> VoiceCharacteristics:
        """分析声音特征"""
        # 计算声音强度
        rms_mean = np.mean(audio_features.rms_energy)
        rms_std = np.std(audio_features.rms_energy)
        
        # 计算音调稳定性
        if audio_features.fundamental_frequency > 0:
            pitch_stability = 1.0 / (1.0 + rms_std)
        else:
            pitch_stability = 0.5
        
        # 计算语速
        speech_rate = len(audio_features.onset_frames) / audio_features.duration
        
        # 计算清晰度
        spectral_centroid_mean = np.mean(audio_features.spectral_centroid)
        clarity = min(spectral_centroid_mean / 2000.0, 1.0)  # 归一化到0-1
        
        # 计算颤抖程度
        tremor_level = np.std(audio_features.rms_energy) / (np.mean(audio_features.rms_energy) + 1e-10)
        
        # 计算呼吸模式
        breath_pattern = self._analyze_breath_pattern(audio_features)
        
        return VoiceCharacteristics(
            pitch_range=(
                float(np.min(audio_features.spectral_centroid)),
                float(np.max(audio_features.spectral_centroid))
            ),
            volume_level=float(rms_mean),
            clarity_score=float(clarity),
            stability_score=float(pitch_stability),
            speech_rate=float(speech_rate),
            tremor_level=float(tremor_level),
            breath_pattern=breath_pattern,
            voice_quality=self._determine_voice_quality(
                clarity, tremor_level, rms_mean
            ),
            emotional_tone=self._analyze_emotional_tone(audio_features)
        )
    
    def _analyze_breath_pattern(self, audio_features: AudioFeatures) -> str:
        """分析呼吸模式"""
        silence_ratio = audio_features.silence_ratio
        
        if silence_ratio > 0.3:
            return "深长"  # 深长呼吸
        elif silence_ratio > 0.2:
            return "平稳"  # 平稳呼吸
        elif silence_ratio > 0.1:
            return "急促"  # 急促呼吸
        else:
            return "微弱"  # 微弱呼吸
    
    def _determine_voice_quality(
        self,
        clarity: float,
        tremor_level: float,
        volume: float
    ) -> VoiceQuality:
        """确定声音质量"""
        if clarity > 0.8 and tremor_level < 0.2:
            return VoiceQuality.CLEAR
        elif tremor_level > 0.5:
            return VoiceQuality.TREMBLING
        elif volume < 0.3:
            return VoiceQuality.WEAK
        elif clarity < 0.4:
            return VoiceQuality.HOARSE
        else:
            return VoiceQuality.ROUGH
    
    def _analyze_emotional_tone(self, audio_features: AudioFeatures) -> str:
        """分析情感色调"""
        # 基于音频特征分析情感
        mfcc_mean = np.mean(audio_features.mfcc)
        spectral_centroid_mean = np.mean(audio_features.spectral_centroid)
        tempo = audio_features.tempo
        
        # 简化的情感分析
        if spectral_centroid_mean > 1500 and tempo > 120:
            return "激动"
        elif spectral_centroid_mean < 800 and tempo < 80:
            return "沉闷"
        elif mfcc_mean > 0:
            return "平和"
        else:
            return "低沉"
    
    async def _analyze_constitution(
        self,
        audio_features: AudioFeatures,
        voice_characteristics: VoiceCharacteristics
    ) -> ConstitutionType:
        """分析体质类型"""
        constitution_scores = {}
        
        for constitution, weights in self.constitution_weights.items():
            score = 0.0
            
            # 根据不同体质的特征计算得分
            if constitution == ConstitutionType.BALANCED:
                score += weights["energy_stability"] * (1.0 - voice_characteristics.tremor_level)
                score += weights["voice_clarity"] * voice_characteristics.clarity_score
                score += weights["breath_regularity"] * self._assess_breath_regularity(voice_characteristics)
                score += weights["emotional_balance"] * self._assess_emotional_balance(voice_characteristics)
            
            elif constitution == ConstitutionType.QI_DEFICIENCY:
                score += weights["low_energy"] * (1.0 - voice_characteristics.volume_level)
                score += weights["weak_voice"] * (1.0 - voice_characteristics.clarity_score)
                score += weights["shallow_breath"] * self._assess_shallow_breath(voice_characteristics)
            
            elif constitution == ConstitutionType.YANG_DEFICIENCY:
                score += weights["low_energy"] * (1.0 - voice_characteristics.volume_level)
                score += weights["slow_speech"] * (1.0 / (voice_characteristics.speech_rate + 1))
                score += weights["weak_voice"] * (1.0 - voice_characteristics.clarity_score)
            
            elif constitution == ConstitutionType.YIN_DEFICIENCY:
                score += weights["restless_energy"] * voice_characteristics.tremor_level
                score += weights["rapid_speech"] * min(voice_characteristics.speech_rate / 5.0, 1.0)
                score += weights["dry_voice"] * self._assess_voice_dryness(voice_characteristics)
            
            # 其他体质类型的评估...
            
            constitution_scores[constitution] = score
        
        # 返回得分最高的体质类型
        best_constitution = max(constitution_scores, key=constitution_scores.get)
        return best_constitution
    
    async def _analyze_emotions(
        self,
        audio_features: AudioFeatures,
        voice_characteristics: VoiceCharacteristics
    ) -> EmotionState:
        """分析情志状态"""
        # 基于五志理论分析情感状态
        emotion_scores = {
            EmotionState.JOY: 0.0,
            EmotionState.ANGER: 0.0,
            EmotionState.WORRY: 0.0,
            EmotionState.SADNESS: 0.0,
            EmotionState.FEAR: 0.0,
            EmotionState.BALANCED: 0.0
        }
        
        # 喜（心志）- 语音流畅、音调明亮
        if voice_characteristics.clarity_score > 0.7 and voice_characteristics.speech_rate > 3:
            emotion_scores[EmotionState.JOY] += 0.8
        
        # 怒（肝志）- 语音紧张、音调高亢
        if voice_characteristics.tremor_level > 0.5 and np.mean(audio_features.spectral_centroid) > 1500:
            emotion_scores[EmotionState.ANGER] += 0.8
        
        # 忧（肺志）- 语音低沉、气息不足
        if voice_characteristics.volume_level < 0.4 and voice_characteristics.breath_pattern == "微弱":
            emotion_scores[EmotionState.SADNESS] += 0.8
        
        # 思（脾志）- 语音犹豫、节奏不稳
        if voice_characteristics.stability_score < 0.5:
            emotion_scores[EmotionState.WORRY] += 0.7
        
        # 恐（肾志）- 语音颤抖、音量微弱
        if voice_characteristics.tremor_level > 0.6 and voice_characteristics.volume_level < 0.3:
            emotion_scores[EmotionState.FEAR] += 0.8
        
        # 平和状态
        if all(score < 0.5 for score in emotion_scores.values()):
            emotion_scores[EmotionState.BALANCED] = 0.8
        
        return max(emotion_scores, key=emotion_scores.get)
    
    async def _assess_organ_functions(
        self,
        audio_features: AudioFeatures,
        voice_characteristics: VoiceCharacteristics
    ) -> List[OrganFunction]:
        """评估脏腑功能"""
        organ_functions = []
        
        for organ, weights in self.organ_weights.items():
            score = 0.0
            
            if organ == "heart":
                score += weights["speech_fluency"] * voice_characteristics.stability_score
                score += weights["voice_rhythm"] * (1.0 - voice_characteristics.tremor_level)
                score += weights["emotional_expression"] * voice_characteristics.clarity_score
            
            elif organ == "liver":
                score += weights["voice_tension"] * (1.0 - voice_characteristics.tremor_level)
                score += weights["speech_smoothness"] * voice_characteristics.stability_score
                score += weights["emotional_control"] * (1.0 - voice_characteristics.tremor_level)
            
            elif organ == "spleen":
                score += weights["voice_strength"] * voice_characteristics.volume_level
                score += weights["speech_clarity"] * voice_characteristics.clarity_score
                score += weights["thinking_patterns"] * voice_characteristics.stability_score
            
            elif organ == "lung":
                score += weights["breath_quality"] * self._assess_breath_quality(voice_characteristics)
                score += weights["voice_clarity"] * voice_characteristics.clarity_score
                score += weights["speech_volume"] * voice_characteristics.volume_level
            
            elif organ == "kidney":
                score += weights["voice_depth"] * self._assess_voice_depth(audio_features)
                score += weights["energy_foundation"] * voice_characteristics.volume_level
                score += weights["speech_stability"] * voice_characteristics.stability_score
            
            # 评估功能状态
            if score > 0.8:
                status = "旺盛"
            elif score > 0.6:
                status = "正常"
            elif score > 0.4:
                status = "偏弱"
            else:
                status = "虚弱"
            
            organ_functions.append(OrganFunction(
                organ=organ,
                function_score=float(score),
                status=status,
                indicators=self._get_organ_indicators(organ, voice_characteristics)
            ))
        
        return organ_functions
    
    def _assess_breath_regularity(self, voice_characteristics: VoiceCharacteristics) -> float:
        """评估呼吸规律性"""
        if voice_characteristics.breath_pattern == "平稳":
            return 1.0
        elif voice_characteristics.breath_pattern == "深长":
            return 0.8
        elif voice_characteristics.breath_pattern == "急促":
            return 0.4
        else:
            return 0.2
    
    def _assess_emotional_balance(self, voice_characteristics: VoiceCharacteristics) -> float:
        """评估情感平衡"""
        return (voice_characteristics.stability_score + voice_characteristics.clarity_score) / 2
    
    def _assess_shallow_breath(self, voice_characteristics: VoiceCharacteristics) -> float:
        """评估浅呼吸程度"""
        return 1.0 if voice_characteristics.breath_pattern == "微弱" else 0.0
    
    def _assess_voice_dryness(self, voice_characteristics: VoiceCharacteristics) -> float:
        """评估声音干燥程度"""
        return 1.0 - voice_characteristics.clarity_score
    
    def _assess_breath_quality(self, voice_characteristics: VoiceCharacteristics) -> float:
        """评估呼吸质量"""
        quality_map = {
            "深长": 1.0,
            "平稳": 0.8,
            "急促": 0.4,
            "微弱": 0.2
        }
        return quality_map.get(voice_characteristics.breath_pattern, 0.5)
    
    def _assess_voice_depth(self, audio_features: AudioFeatures) -> float:
        """评估声音深度"""
        low_freq_energy = np.mean(audio_features.mfcc[:3])  # 低频MFCC系数
        return min(abs(low_freq_energy) / 10.0, 1.0)
    
    def _get_organ_indicators(self, organ: str, voice_characteristics: VoiceCharacteristics) -> List[str]:
        """获取脏腑指标"""
        indicators = []
        
        if organ == "heart":
            if voice_characteristics.stability_score > 0.7:
                indicators.append("语音流畅")
            if voice_characteristics.clarity_score > 0.7:
                indicators.append("表达清晰")
        
        elif organ == "liver":
            if voice_characteristics.tremor_level < 0.3:
                indicators.append("情绪稳定")
            if voice_characteristics.stability_score > 0.6:
                indicators.append("语音平和")
        
        elif organ == "spleen":
            if voice_characteristics.volume_level > 0.6:
                indicators.append("声音有力")
            if voice_characteristics.clarity_score > 0.6:
                indicators.append("思维清晰")
        
        elif organ == "lung":
            if voice_characteristics.breath_pattern in ["深长", "平稳"]:
                indicators.append("呼吸调匀")
            if voice_characteristics.clarity_score > 0.6:
                indicators.append("声音清亮")
        
        elif organ == "kidney":
            if voice_characteristics.volume_level > 0.5:
                indicators.append("声音深厚")
            if voice_characteristics.stability_score > 0.6:
                indicators.append("精神充沛")
        
        return indicators
    
    async def _generate_recommendations(
        self,
        voice_characteristics: VoiceCharacteristics,
        constitution: Optional[ConstitutionType],
        emotion: Optional[EmotionState],
        organ_functions: List[OrganFunction]
    ) -> List[str]:
        """生成调理建议"""
        recommendations = []
        
        # 基于体质的建议
        if constitution:
            constitution_recommendations = {
                ConstitutionType.QI_DEFICIENCY: [
                    "建议多食用补气食物，如人参、黄芪、大枣",
                    "适当进行缓和运动，如太极拳、八段锦",
                    "保证充足睡眠，避免过度劳累"
                ],
                ConstitutionType.YANG_DEFICIENCY: [
                    "建议温阳补肾，多食用温热性食物",
                    "避免生冷食物，注意保暖",
                    "可进行温和的有氧运动"
                ],
                ConstitutionType.YIN_DEFICIENCY: [
                    "建议滋阴润燥，多食用滋阴食物",
                    "避免辛辣燥热食物，保持心情平和",
                    "适当进行静态运动，如瑜伽、冥想"
                ]
            }
            recommendations.extend(constitution_recommendations.get(constitution, []))
        
        # 基于情志的建议
        if emotion:
            emotion_recommendations = {
                EmotionState.ANGER: [
                    "建议疏肝理气，保持心情舒畅",
                    "可进行适当的运动发泄情绪",
                    "避免过度愤怒，学会情绪管理"
                ],
                EmotionState.WORRY: [
                    "建议健脾益气，多思考积极事物",
                    "适当进行社交活动，转移注意力",
                    "保持规律作息，避免过度思虑"
                ],
                EmotionState.SADNESS: [
                    "建议宣肺理气，多进行户外活动",
                    "保持乐观心态，寻求社会支持",
                    "适当进行呼吸练习，调节情绪"
                ]
            }
            recommendations.extend(emotion_recommendations.get(emotion, []))
        
        # 基于脏腑功能的建议
        for organ_function in organ_functions:
            if organ_function.function_score < 0.5:
                organ_recommendations = {
                    "heart": ["建议养心安神，保持心情愉悦"],
                    "liver": ["建议疏肝解郁，避免情绪波动"],
                    "spleen": ["建议健脾益气，规律饮食"],
                    "lung": ["建议宣肺理气，注意呼吸调节"],
                    "kidney": ["建议补肾固本，避免过度劳累"]
                }
                recommendations.extend(organ_recommendations.get(organ_function.organ, []))
        
        return recommendations
    
    def _calculate_confidence_score(
        self,
        voice_characteristics: VoiceCharacteristics,
        constitution: Optional[ConstitutionType],
        emotion: Optional[EmotionState]
    ) -> float:
        """计算诊断置信度"""
        base_score = 0.5
        
        # 基于声音质量调整置信度
        if voice_characteristics.clarity_score > 0.7:
            base_score += 0.2
        if voice_characteristics.stability_score > 0.7:
            base_score += 0.2
        if voice_characteristics.volume_level > 0.5:
            base_score += 0.1
        
        return min(base_score, 1.0)