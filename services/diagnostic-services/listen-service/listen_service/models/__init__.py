"""
数据模型定义

包含音频分析请求/响应、特征数据结构、中医诊断模型等。
"""

from .audio_models import (
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    VoiceFeatures,
    SoundFeatures,
    AudioMetadata,
)
from .tcm_models import (
    TCMDiagnosis,
    ConstitutionType,
    EmotionState,
    OrganSoundMapping,
)
from .emotion_models import (
    EmotionAnalysis,
    EmotionScore,
    MoodState,
)

__all__ = [
    # 音频模型
    "AudioAnalysisRequest",
    "AudioAnalysisResponse", 
    "VoiceFeatures",
    "SoundFeatures",
    "AudioMetadata",
    # 中医模型
    "TCMDiagnosis",
    "ConstitutionType",
    "EmotionState",
    "OrganSoundMapping",
    # 情绪模型
    "EmotionAnalysis",
    "EmotionScore",
    "MoodState",
] 