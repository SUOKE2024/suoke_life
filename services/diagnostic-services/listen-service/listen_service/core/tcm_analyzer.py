"""
tcm_analyzer - 索克生活项目模块
"""

from ..config.settings import get_settings
from ..models.audio_models import VoiceFeatures
from ..models.tcm_models import (
from ..utils.performance import async_timer
from dataclasses import dataclass
from enum import Enum
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from typing import Any
import asyncio
import numpy as np
import structlog
import time

"""
中医特征分析器

基于传统中医理论和现代音频分析技术，从语音特征中提取中医诊断相关信息。
支持体质分析、情绪状态识别、脏腑功能评估等功能。
"""



    TCMDiagnosis,
)

logger = structlog.get_logger(__name__)

class TCMAnalysisMethod(str, Enum):
    """中医分析方法"""

    TRADITIONAL = "traditional"  # 传统理论分析
    ML_ENHANCED = "ml_enhanced"  # 机器学习增强
    HYBRID = "hybrid"  # 混合方法

@dataclass
class TCMFeatureWeights:
    """中医特征权重配置"""

    # 五脏对应的音频特征权重
    heart_weights: dict[str, float]  # 心 - 舌音、语速
    liver_weights: dict[str, float]  # 肝 - 呼音、音调变化
    spleen_weights: dict[str, float]  # 脾 - 唇音、音量
    lung_weights: dict[str, float]  # 肺 - 鼻音、呼吸音
    kidney_weights: dict[str, float]  # 肾 - 齿音、低频能量

    @classmethod
    def default_weights(cls) -> "TCMFeatureWeights":
        """默认权重配置"""
        return cls(
            heart_weights={
                "f0_mean": 0.3,
                "f0_std": 0.2,
                "speech_rate": 0.3,
                "spectral_centroids": 0.2,
            },
            liver_weights={
                "f0_range": 0.4,
                "spectral_bandwidth": 0.3,
                "zero_crossing_rate": 0.3,
            },
            spleen_weights={
                "rms_energy": 0.4,
                "spectral_rolloff": 0.3,
                "voiced_ratio": 0.3,
            },
            lung_weights={
                "harmonic_noise_ratio": 0.4,
                "spectral_flatness": 0.3,
                "breath_features": 0.3,
            },
            kidney_weights={
                "low_frequency_energy": 0.4,
                "formant_stability": 0.3,
                "voice_quality": 0.3,
            },
        )

class TCMFeatureExtractor:
    """
    中医特征分析器

    基于中医理论从音频特征中提取诊断相关信息，
    支持体质分析、情绪识别和脏腑功能评估。
    """

    def __init__(
        self,
        method: TCMAnalysisMethod = TCMAnalysisMethod.HYBRID,
        feature_weights: TCMFeatureWeights | None = None,
        enable_ml: bool = True,
    ) -> None:
        """
        初始化中医特征分析器

        Args:
            method: 分析方法
            feature_weights: 特征权重配置
            enable_ml: 是否启用机器学习
        """
        self.settings = get_settings()
        self.method = method
        self.feature_weights = feature_weights or TCMFeatureWeights.default_weights()
        self.enable_ml = enable_ml

        # 初始化分析器组件
        self.constitution_analyzer = ConstitutionAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.organ_analyzer = OrganAnalyzer(self.feature_weights)

        # 机器学习模型（如果启用）
        self.ml_models = {}
        if self.enable_ml:
            self._initialize_ml_models()

        # 性能统计
        self.analysis_stats = {
            "total_analyses": 0,
            "average_time": 0.0,
            "constitution_accuracy": 0.0,
            "emotion_accuracy": 0.0,
        }

        logger.info(
            "中医特征分析器初始化完成",
            method=self.method.value,
            enable_ml=self.enable_ml,
        )

    def _initialize_ml_models(self) -> None:
        """初始化机器学习模型"""
        try:
            # 体质分类模型
            self.ml_models["constitution"] = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                max_depth=10,
            )

            # 情绪分类模型
            self.ml_models["emotion"] = SVC(
                kernel="rbf",
                probability=True,
                random_state=42,
            )

            # 脏腑功能评估模型
            self.ml_models["organ"] = RandomForestClassifier(
                n_estimators=50,
                random_state=42,
                max_depth=8,
            )

            logger.info("机器学习模型初始化完成")

        except Exception as e:
            logger.warning("机器学习模型初始化失败", error=str(e))
            self.enable_ml = False

    @async_timer
    async def analyze_tcm_features(
        self,
        voice_features: VoiceFeatures,
        audio_metadata: dict[str, Any] | None = None,
    ) -> TCMDiagnosis:
        """
        分析中医特征

        Args:
            voice_features: 语音特征
            audio_metadata: 音频元数据

        Returns:
            中医诊断结果
        """
        start_time = time.time()

        try:
            # 并行执行各项分析
            tasks = [
                self._analyze_constitution(voice_features),
                self._analyze_emotion(voice_features),
                self._analyze_organs(voice_features),
            ]

            constitution_result, emotion_result, organ_result = await asyncio.gather(
                *tasks
            )

            # 综合分析结果
            diagnosis = await self._synthesize_diagnosis(
                constitution_result,
                emotion_result,
                organ_result,
                voice_features,
            )

            # 更新统计
            processing_time = time.time() - start_time
            self._update_stats(processing_time)

            logger.info(
                "中医特征分析完成",
                constitution=diagnosis.constitution_type,
                emotion=diagnosis.emotion_state,
                processing_time=processing_time,
            )

            return diagnosis

        except Exception as e:
            logger.error("中医特征分析失败", error=str(e), exc_info=True)
            # 返回默认诊断结果
            return TCMDiagnosis(
                constitution_type="未知",
                emotion_state="平静",
                organ_analysis={},
                confidence_score=0.0,
                analysis_method=self.method.value,
                error_message=str(e),
            )

    async def _analyze_constitution(self, features: VoiceFeatures) -> dict[str, Any]:
        """分析体质类型"""
        return await self.constitution_analyzer.analyze(
            features, self.ml_models.get("constitution")
        )

    async def _analyze_emotion(self, features: VoiceFeatures) -> dict[str, Any]:
        """分析情绪状态"""
        return await self.emotion_analyzer.analyze(
            features, self.ml_models.get("emotion")
        )

    async def _analyze_organs(self, features: VoiceFeatures) -> dict[str, Any]:
        """分析脏腑功能"""
        return await self.organ_analyzer.analyze(features, self.ml_models.get("organ"))

    async def _synthesize_diagnosis(
        self,
        constitution_result: dict[str, Any],
        emotion_result: dict[str, Any],
        organ_result: dict[str, Any],
        features: VoiceFeatures,
    ) -> TCMDiagnosis:
        """综合诊断结果"""

        # 计算综合置信度
        confidence_scores = [
            constitution_result.get("confidence", 0.0),
            emotion_result.get("confidence", 0.0),
            organ_result.get("confidence", 0.0),
        ]
        overall_confidence = np.mean(confidence_scores)

        # 生成建议
        recommendations = await self._generate_recommendations(
            constitution_result,
            emotion_result,
            organ_result,
        )

        return TCMDiagnosis(
            constitution_type=constitution_result.get("type", "平和质"),
            emotion_state=emotion_result.get("state", "平静"),
            organ_analysis=organ_result.get("analysis", {}),
            confidence_score=float(overall_confidence),
            analysis_method=self.method.value,
            detailed_scores={
                "constitution_confidence": constitution_result.get("confidence", 0.0),
                "emotion_confidence": emotion_result.get("confidence", 0.0),
                "organ_confidence": organ_result.get("confidence", 0.0),
            },
            recommendations=recommendations,
            timestamp=time.time(),
        )

    async def _generate_recommendations(
        self,
        constitution_result: dict[str, Any],
        emotion_result: dict[str, Any],
        organ_result: dict[str, Any],
    ) -> list[str]:
        """生成中医建议"""
        recommendations = []

        # 基于体质的建议
        constitution_type = constitution_result.get("type", "")
        if constitution_type in ["气虚质", "阳虚质"]:
            recommendations.append("建议适当运动，增强体质")
            recommendations.append("注意保暖，避免过度劳累")
        elif constitution_type in ["阴虚质", "湿热质"]:
            recommendations.append("注意清淡饮食，避免辛辣刺激")
            recommendations.append("保持充足睡眠，调节情绪")

        # 基于情绪的建议
        emotion_state = emotion_result.get("state", "")
        if emotion_state in ["怒", "急躁"]:
            recommendations.append("建议练习深呼吸，保持心情平和")
        elif emotion_state in ["忧", "思虑过度"]:
            recommendations.append("适当放松，避免过度思虑")

        # 基于脏腑的建议
        organ_analysis = organ_result.get("analysis", {})
        for organ, score in organ_analysis.items():
            if isinstance(score, (int, float)) and score < 0.6:
                if organ == "心":
                    recommendations.append("注意心脏保养，避免情绪激动")
                elif organ == "肝":
                    recommendations.append("注意肝脏调理，保持情绪稳定")
                elif organ == "脾":
                    recommendations.append("注意脾胃调理，规律饮食")
                elif organ == "肺":
                    recommendations.append("注意肺部保养，避免吸烟")
                elif organ == "肾":
                    recommendations.append("注意肾脏保养，避免过度劳累")

        return recommendations[:5]  # 限制建议数量

    def _update_stats(self, processing_time: float) -> None:
        """更新统计信息"""
        self.analysis_stats["total_analyses"] += 1
        total_time = (
            self.analysis_stats["average_time"]
            * (self.analysis_stats["total_analyses"] - 1)
            + processing_time
        )
        self.analysis_stats["average_time"] = (
            total_time / self.analysis_stats["total_analyses"]
        )

    async def get_analysis_stats(self) -> dict[str, Any]:
        """获取分析统计"""
        return self.analysis_stats.copy()

class ConstitutionAnalyzer:
    """体质分析器"""

    async def analyze(
        self,
        features: VoiceFeatures,
        ml_model: Any | None = None,
    ) -> dict[str, Any]:
        """分析体质类型"""

        # 提取体质相关特征
        constitution_features = self._extract_constitution_features(features)

        # 传统理论分析
        traditional_result = self._traditional_constitution_analysis(
            constitution_features
        )

        # 机器学习分析（如果可用）
        ml_result = None
        if ml_model is not None:
            ml_result = self._ml_constitution_analysis(constitution_features, ml_model)

        # 综合结果
        if ml_result:
            # 结合传统和ML结果
            confidence = (
                traditional_result["confidence"] + ml_result["confidence"]
            ) / 2
            constitution_type = (
                ml_result["type"]
                if ml_result["confidence"] > traditional_result["confidence"]
                else traditional_result["type"]
            )
        else:
            confidence = traditional_result["confidence"]
            constitution_type = traditional_result["type"]

        return {
            "type": constitution_type,
            "confidence": confidence,
            "traditional_analysis": traditional_result,
            "ml_analysis": ml_result,
        }

    def _extract_constitution_features(self, features: VoiceFeatures) -> np.ndarray:
        """提取体质相关特征"""
        feature_vector = []

        # 基频特征
        if features.prosodic_features:
            feature_vector.extend(
                [
                    features.prosodic_features.get("f0_mean", 0.0),
                    features.prosodic_features.get("f0_std", 0.0),
                    features.prosodic_features.get("f0_range", 0.0),
                ]
            )

        # 能量特征
        if features.voice_quality:
            feature_vector.extend(
                [
                    features.voice_quality.get("rms_energy", 0.0),
                    features.voice_quality.get("harmonic_noise_ratio", 0.0),
                ]
            )

        # 频谱特征
        if features.spectral_features:
            spectral_centroids = features.spectral_features.get(
                "spectral_centroids", np.array([])
            )
            if len(spectral_centroids) > 0:
                feature_vector.extend(
                    [
                        np.mean(spectral_centroids),
                        np.std(spectral_centroids),
                    ]
                )

        return np.array(feature_vector)

    def _traditional_constitution_analysis(
        self, features: np.ndarray
    ) -> dict[str, Any]:
        """传统体质分析"""
        # 简化的传统分析逻辑
        if len(features) < 5:
            return {"type": "平和质", "confidence": 0.5}

        f0_mean, f0_std, f0_range, rms_energy, hnr = features[:5]

        # 基于传统理论的简单规则
        if f0_mean < 120 and rms_energy < 0.3:
            constitution_type = "阳虚质"
            confidence = 0.7
        elif f0_std > 30 and f0_range > 100:
            constitution_type = "气郁质"
            confidence = 0.6
        elif rms_energy > 0.7 and hnr < 0.5:
            constitution_type = "湿热质"
            confidence = 0.6
        else:
            constitution_type = "平和质"
            confidence = 0.8

        return {"type": constitution_type, "confidence": confidence}

    def _ml_constitution_analysis(
        self, features: np.ndarray, model: Any
    ) -> dict[str, Any]:
        """机器学习体质分析"""
        try:
            # 这里应该使用训练好的模型
            # 暂时返回模拟结果
            constitution_types = [
                "平和质",
                "气虚质",
                "阳虚质",
                "阴虚质",
                "痰湿质",
                "湿热质",
                "血瘀质",
                "气郁质",
                "特禀质",
            ]

            # 模拟预测
            predicted_idx = np.random.randint(0, len(constitution_types))
            confidence = np.random.uniform(0.6, 0.9)

            return {
                "type": constitution_types[predicted_idx],
                "confidence": confidence,
            }
        except Exception as e:
            logger.warning("机器学习体质分析失败", error=str(e))
            return {"type": "平和质", "confidence": 0.5}

class EmotionAnalyzer:
    """情绪分析器"""

    async def analyze(
        self,
        features: VoiceFeatures,
        ml_model: Any | None = None,
    ) -> dict[str, Any]:
        """分析情绪状态"""

        # 提取情绪相关特征
        emotion_features = self._extract_emotion_features(features)

        # 传统五志分析
        traditional_result = self._traditional_emotion_analysis(emotion_features)

        # 机器学习分析（如果可用）
        ml_result = None
        if ml_model is not None:
            ml_result = self._ml_emotion_analysis(emotion_features, ml_model)

        # 综合结果
        if ml_result:
            confidence = (
                traditional_result["confidence"] + ml_result["confidence"]
            ) / 2
            emotion_state = (
                ml_result["state"]
                if ml_result["confidence"] > traditional_result["confidence"]
                else traditional_result["state"]
            )
        else:
            confidence = traditional_result["confidence"]
            emotion_state = traditional_result["state"]

        return {
            "state": emotion_state,
            "confidence": confidence,
            "traditional_analysis": traditional_result,
            "ml_analysis": ml_result,
        }

    def _extract_emotion_features(self, features: VoiceFeatures) -> np.ndarray:
        """提取情绪相关特征"""
        feature_vector = []

        # 韵律特征
        if features.prosodic_features:
            feature_vector.extend(
                [
                    features.prosodic_features.get("f0_mean", 0.0),
                    features.prosodic_features.get("f0_std", 0.0),
                    features.prosodic_features.get("speech_rate", 0.0),
                ]
            )

        # 音质特征
        if features.voice_quality:
            feature_vector.extend(
                [
                    features.voice_quality.get("harmonic_noise_ratio", 0.0),
                    features.voice_quality.get("spectral_flatness", 0.0),
                ]
            )

        return np.array(feature_vector)

    def _traditional_emotion_analysis(self, features: np.ndarray) -> dict[str, Any]:
        """传统五志情绪分析"""
        if len(features) < 3:
            return {"state": "平静", "confidence": 0.5}

        f0_mean, f0_std, speech_rate = features[:3]

        # 基于传统五志理论的简单规则
        if f0_std > 25 and speech_rate > 3.0:
            emotion_state = "怒"  # 愤怒
            confidence = 0.7
        elif f0_mean < 100 and speech_rate < 1.5:
            emotion_state = "忧"  # 忧虑
            confidence = 0.6
        elif f0_std < 10 and speech_rate > 2.5:
            emotion_state = "思"  # 思虑
            confidence = 0.6
        elif f0_mean > 200:
            emotion_state = "喜"  # 喜悦
            confidence = 0.7
        else:
            emotion_state = "平静"
            confidence = 0.8

        return {"state": emotion_state, "confidence": confidence}

    def _ml_emotion_analysis(self, features: np.ndarray, model: Any) -> dict[str, Any]:
        """机器学习情绪分析"""
        try:
            # 模拟ML分析
            emotion_states = ["喜", "怒", "忧", "思", "恐", "平静"]
            predicted_idx = np.random.randint(0, len(emotion_states))
            confidence = np.random.uniform(0.6, 0.9)

            return {
                "state": emotion_states[predicted_idx],
                "confidence": confidence,
            }
        except Exception as e:
            logger.warning("机器学习情绪分析失败", error=str(e))
            return {"state": "平静", "confidence": 0.5}

class OrganAnalyzer:
    """脏腑分析器"""

    def __init__(self, feature_weights: TCMFeatureWeights):
        self.feature_weights = feature_weights

    async def analyze(
        self,
        features: VoiceFeatures,
        ml_model: Any | None = None,
    ) -> dict[str, Any]:
        """分析脏腑功能"""

        # 分析各个脏腑
        organ_scores = {}

        # 心脏分析
        organ_scores["心"] = self._analyze_heart(features)

        # 肝脏分析
        organ_scores["肝"] = self._analyze_liver(features)

        # 脾脏分析
        organ_scores["脾"] = self._analyze_spleen(features)

        # 肺脏分析
        organ_scores["肺"] = self._analyze_lung(features)

        # 肾脏分析
        organ_scores["肾"] = self._analyze_kidney(features)

        # 计算整体置信度
        confidence = np.mean(list(organ_scores.values()))

        return {
            "analysis": organ_scores,
            "confidence": float(confidence),
        }

    def _analyze_heart(self, features: VoiceFeatures) -> float:
        """分析心脏功能"""
        score = 0.8  # 默认正常

        if features.prosodic_features:
            f0_mean = features.prosodic_features.get("f0_mean", 150)
            speech_rate = features.prosodic_features.get("speech_rate", 2.0)

            # 心主神志，语速和音调反映心的功能
            if f0_mean > 200 or speech_rate > 4.0:
                score -= 0.2  # 心火旺
            elif f0_mean < 100 or speech_rate < 1.0:
                score -= 0.3  # 心气虚

        return max(0.0, min(1.0, score))

    def _analyze_liver(self, features: VoiceFeatures) -> float:
        """分析肝脏功能"""
        score = 0.8

        if features.prosodic_features:
            f0_range = features.prosodic_features.get("f0_range", 50)

            # 肝主疏泄，音调变化反映肝的功能
            if f0_range > 150:
                score -= 0.2  # 肝气郁结
            elif f0_range < 20:
                score -= 0.1  # 肝气不足

        return max(0.0, min(1.0, score))

    def _analyze_spleen(self, features: VoiceFeatures) -> float:
        """分析脾脏功能"""
        score = 0.8

        if features.voice_quality:
            rms_energy = features.voice_quality.get("rms_energy", 0.5)

            # 脾主运化，声音能量反映脾的功能
            if rms_energy < 0.3:
                score -= 0.3  # 脾气虚
            elif rms_energy > 0.8:
                score -= 0.1  # 脾胃湿热

        return max(0.0, min(1.0, score))

    def _analyze_lung(self, features: VoiceFeatures) -> float:
        """分析肺脏功能"""
        score = 0.8

        if features.voice_quality:
            hnr = features.voice_quality.get("harmonic_noise_ratio", 0.7)

            # 肺主气，声音清浊反映肺的功能
            if hnr < 0.5:
                score -= 0.3  # 肺气虚或有痰
            elif hnr > 0.9:
                score += 0.1  # 肺气充足

        return max(0.0, min(1.0, score))

    def _analyze_kidney(self, features: VoiceFeatures) -> float:
        """分析肾脏功能"""
        score = 0.8

        if features.prosodic_features:
            f0_mean = features.prosodic_features.get("f0_mean", 150)

            # 肾主骨生髓，低频能量反映肾的功能
            if f0_mean < 80:
                score -= 0.2  # 肾阳虚
            elif f0_mean > 250:
                score -= 0.1  # 肾阴虚

        return max(0.0, min(1.0, score))
