"""
索克生活闻诊服务 (Listen Service)

中医四诊中的听觉感知与音频分析微服务，提供语音特征提取、声音分析、
情绪识别、方言检测和语音转写等功能。
"""

__version__ = "1.0.0"
__author__ = "SUOKE Team"
__email__ = "dev@suoke.life"

from .core import AudioAnalyzer, TCMFeatureExtractor
from .models import (
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    VoiceFeatures,
    EmotionAnalysis,
    TCMDiagnosis,
)

__all__ = [
    "AudioAnalyzer",
    "TCMFeatureExtractor", 
    "AudioAnalysisRequest",
    "AudioAnalysisResponse",
    "VoiceFeatures",
    "EmotionAnalysis",
    "TCMDiagnosis",
] 