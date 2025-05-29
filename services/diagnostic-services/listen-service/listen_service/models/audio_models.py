"""
音频分析相关的数据模型

包含音频类型、质量、请求、响应等数据结构定义。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AudioType(Enum):
    """音频类型"""

    VOICE = "voice"  # 语音
    BREATHING = "breathing"  # 呼吸音
    COUGH = "cough"  # 咳嗽音
    HEARTBEAT = "heartbeat"  # 心音
    GENERAL = "general"  # 一般音频


class AudioQuality(Enum):
    """音频质量"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class AudioFormat(Enum):
    """音频格式"""

    WAV = "wav"
    MP3 = "mp3"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"


@dataclass
class AudioMetadata:
    """音频元数据"""

    sample_rate: int
    channels: int
    duration: float
    format: AudioFormat
    file_size: int
    bit_depth: int | None = None
    codec: str | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AudioAnalysisRequest:
    """音频分析请求"""

    request_id: str
    patient_id: str
    audio_type: AudioType
    audio_data: str  # Base64编码的音频数据
    sample_rate: int = 44100
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    enable_caching: bool = True
    analysis_type: str = "default"


@dataclass
class AudioFeature:
    """音频特征"""

    feature_type: str
    value: Any
    confidence: float
    time_range: tuple[float, float] | None = None  # 时间范围（秒）
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VoiceFeatures:
    """语音特征集合"""

    mfcc_features: list[float]
    spectral_features: dict[str, float]
    prosodic_features: dict[str, float]
    pitch_features: dict[str, float]
    intensity_features: dict[str, float]
    rhythm_features: dict[str, float]
    clarity_features: dict[str, float]


@dataclass
class BreathingFeatures:
    """呼吸音特征集合"""

    rate: float
    depth: str
    pattern: str
    quality: str
    irregularities: list[str]


@dataclass
class CoughFeatures:
    """咳嗽音特征集合"""

    frequency: float
    intensity: str
    type: str
    duration: float
    wet_dry_classification: str


@dataclass
class ListenResult:
    """闻诊结果"""

    request_id: str
    patient_id: str
    audio_type: AudioType
    features: list[AudioFeature]
    syndrome_indicators: dict[str, float]  # 证候指标
    quality_score: float
    processing_time_ms: float
    recommendations: list[str]
    success: bool = True
    error_message: str | None = None
    voice_features: VoiceFeatures | None = None
    breathing_features: BreathingFeatures | None = None
    cough_features: CoughFeatures | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BatchAudioRequest:
    """批量音频分析请求"""

    batch_id: str
    requests: list[AudioAnalysisRequest]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BatchAnalysisResult:
    """批量分析结果"""

    batch_id: str
    results: list[ListenResult]
    total_requests: int
    successful_analyses: int
    failed_analyses: int
    total_processing_time_ms: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisRequest:
    """通用分析请求"""

    request_id: str
    audio_data: bytes
    metadata: AudioMetadata
    analysis_type: str = "default"
    enable_caching: bool = True
    patient_id: str | None = None
    session_id: str | None = None


@dataclass
class ServiceStats:
    """服务统计信息"""

    total_requests: int
    successful_analyses: int
    failed_analyses: int
    cache_hits: int
    cache_misses: int
    average_processing_time_ms: float
    quality_distribution: dict[str, int]
    batch_processed: int
    audio_types_processed: dict[str, int]
    uptime_seconds: float
    memory_usage_mb: float
    cpu_usage_percent: float
