"""
数据模型模块

提供音频分析和中医诊断相关的数据模型。
"""

from .audio_models import (
    AudioFormat,
    AnalysisType,
    AudioMetadata,
    AudioFeatures,
    AnalysisRequest,
    AnalysisResult,
    AudioUploadRequest,
    BatchAnalysisRequest,
    BatchAnalysisResult,
    AudioProcessingConfig,
    AudioAnalysisError,
    AudioAnalysisStats
)

from .tcm_models import (
    ConstitutionType,
    EmotionState,
    VoiceQuality,
    SpeechPattern,
    VoiceCharacteristics,
    OrganFunction,
    ConstitutionAnalysis,
    EmotionAnalysis,
    TCMPattern,
    TCMRecommendation,
    TCMDiagnosis,
    TCMKnowledgeBase,
    TCMAnalysisConfig,
    TCMAnalysisResult
)

__all__ = [
    # Audio models
    "AudioFormat",
    "AnalysisType",
    "AudioMetadata",
    "AudioFeatures",
    "AnalysisRequest",
    "AnalysisResult",
    "AudioUploadRequest",
    "BatchAnalysisRequest",
    "BatchAnalysisResult",
    "AudioProcessingConfig",
    "AudioAnalysisError",
    "AudioAnalysisStats",
    
    # TCM models
    "ConstitutionType",
    "EmotionState",
    "VoiceQuality",
    "SpeechPattern",
    "VoiceCharacteristics",
    "OrganFunction",
    "ConstitutionAnalysis",
    "EmotionAnalysis",
    "TCMPattern",
    "TCMRecommendation",
    "TCMDiagnosis",
    "TCMKnowledgeBase",
    "TCMAnalysisConfig",
    "TCMAnalysisResult"
]
