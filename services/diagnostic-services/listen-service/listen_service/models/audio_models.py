"""
音频分析数据模型

使用 Pydantic v2 定义的现代化数据模型，支持类型验证、序列化和文档生成。
专为中医闻诊音频分析设计。
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

import numpy as np
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveFloat, PositiveInt


class AudioFormat(str, Enum):
    """音频格式枚举"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"


class AnalysisType(str, Enum):
    """分析类型枚举"""
    VOICE_FEATURES = "voice_features"
    EMOTION_ANALYSIS = "emotion_analysis"
    TCM_DIAGNOSIS = "tcm_diagnosis"
    DIALECT_DETECTION = "dialect_detection"
    TRANSCRIPTION = "transcription"
    BATCH_ANALYSIS = "batch_analysis"


class AudioMetadata(BaseModel):
    """音频元数据"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )
    
    duration: PositiveFloat = Field(
        ..., 
        description="音频时长（秒）",
        examples=[30.5, 120.0]
    )
    sample_rate: PositiveInt = Field(
        ..., 
        description="采样率（Hz）",
        examples=[16000, 44100]
    )
    channels: PositiveInt = Field(
        default=1, 
        description="声道数",
        examples=[1, 2]
    )
    bit_depth: PositiveInt = Field(
        default=16, 
        description="位深度",
        examples=[16, 24, 32]
    )
    format: AudioFormat = Field(
        default=AudioFormat.WAV,
        description="音频格式"
    )
    file_size: Optional[PositiveInt] = Field(
        default=None,
        description="文件大小（字节）"
    )
    original_sample_rate: Optional[PositiveInt] = Field(
        default=None,
        description="原始采样率（重采样前）"
    )
    voice_segments: List[tuple[float, float]] = Field(
        default_factory=list,
        description="语音活动段落 [(开始时间, 结束时间)]"
    )
    enhancement_applied: bool = Field(
        default=False,
        description="是否应用了音频增强"
    )


class VoiceFeatures(BaseModel):
    """语音特征数据"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )
    
    # MFCC 特征
    mfcc: Optional[np.ndarray] = Field(
        default=None,
        description="MFCC 特征矩阵"
    )
    
    # 频谱特征
    spectral_features: Optional[Dict[str, np.ndarray]] = Field(
        default=None,
        description="频谱特征（质心、带宽、滚降等）"
    )
    
    # 韵律特征
    prosodic_features: Optional[Dict[str, float]] = Field(
        default=None,
        description="韵律特征（基频、语速等）"
    )
    
    # 音质特征
    voice_quality: Optional[Dict[str, float]] = Field(
        default=None,
        description="音质特征（谐噪比、抖动等）"
    )
    
    # 统计特征
    statistical_features: Optional[Dict[str, float]] = Field(
        default=None,
        description="统计特征（均值、方差等）"
    )
    
    @field_validator('mfcc')
    @classmethod
    def validate_mfcc(cls, v):
        if v is not None and not isinstance(v, np.ndarray):
            raise ValueError("MFCC 必须是 numpy 数组")
        return v


class SoundFeatures(BaseModel):
    """声音特征数据（非语言声音）"""
    model_config = ConfigDict(validate_assignment=True)
    
    # 咳嗽声特征
    cough_features: Optional[Dict[str, float]] = Field(
        default=None,
        description="咳嗽声特征"
    )
    
    # 呼吸声特征
    breath_features: Optional[Dict[str, float]] = Field(
        default=None,
        description="呼吸声特征"
    )
    
    # 心音特征
    heartbeat_features: Optional[Dict[str, float]] = Field(
        default=None,
        description="心音特征"
    )
    
    # 其他生理声音
    physiological_sounds: Optional[Dict[str, Any]] = Field(
        default=None,
        description="其他生理声音特征"
    )


class AudioAnalysisRequest(BaseModel):
    """音频分析请求"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    
    request_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="请求唯一标识符"
    )
    
    analysis_types: List[AnalysisType] = Field(
        default=[AnalysisType.VOICE_FEATURES],
        description="要执行的分析类型列表"
    )
    
    # 音频数据（可以是文件路径、URL 或 base64 编码）
    audio_source: Optional[str] = Field(
        default=None,
        description="音频源（文件路径、URL 或 base64）"
    )
    
    # 处理参数
    sample_rate: Optional[PositiveInt] = Field(
        default=16000,
        description="目标采样率"
    )
    
    enable_enhancement: bool = Field(
        default=True,
        description="是否启用音频增强"
    )
    
    enable_vad: bool = Field(
        default=True,
        description="是否启用语音活动检测"
    )
    
    # 中医分析参数
    tcm_analysis_enabled: bool = Field(
        default=True,
        description="是否启用中医特征分析"
    )
    
    constitution_analysis: bool = Field(
        default=True,
        description="是否进行体质分析"
    )
    
    emotion_analysis: bool = Field(
        default=True,
        description="是否进行情绪分析"
    )
    
    # 缓存控制
    use_cache: bool = Field(
        default=True,
        description="是否使用缓存"
    )
    
    cache_ttl: Optional[PositiveInt] = Field(
        default=3600,
        description="缓存生存时间（秒）"
    )
    
    # 用户信息
    user_id: Optional[str] = Field(
        default=None,
        description="用户ID"
    )
    
    session_id: Optional[str] = Field(
        default=None,
        description="会话ID"
    )
    
    # 元数据
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="请求时间戳"
    )
    
    client_info: Optional[Dict[str, str]] = Field(
        default=None,
        description="客户端信息"
    )


class AudioAnalysisResponse(BaseModel):
    """音频分析响应"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )
    
    request_id: str = Field(
        ...,
        description="对应的请求ID"
    )
    
    success: bool = Field(
        default=True,
        description="分析是否成功"
    )
    
    # 分析结果
    voice_features: Optional[VoiceFeatures] = Field(
        default=None,
        description="语音特征分析结果"
    )
    
    sound_features: Optional[SoundFeatures] = Field(
        default=None,
        description="声音特征分析结果"
    )
    
    # 中医诊断结果（从其他模块导入）
    tcm_diagnosis: Optional[Any] = Field(
        default=None,
        description="中医诊断结果"
    )
    
    # 情绪分析结果
    emotion_analysis: Optional[Any] = Field(
        default=None,
        description="情绪分析结果"
    )
    
    # 方言检测结果
    dialect_detection: Optional[Dict[str, Any]] = Field(
        default=None,
        description="方言检测结果"
    )
    
    # 语音转写结果
    transcription: Optional[str] = Field(
        default=None,
        description="语音转写文本"
    )
    
    # 元数据和统计
    metadata: Optional[AudioMetadata] = Field(
        default=None,
        description="音频元数据"
    )
    
    processing_time: PositiveFloat = Field(
        ...,
        description="处理时间（秒）"
    )
    
    confidence_scores: Optional[Dict[str, float]] = Field(
        default=None,
        description="各项分析的置信度分数"
    )
    
    # 错误信息
    error_message: Optional[str] = Field(
        default=None,
        description="错误信息（如果有）"
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="错误代码"
    )
    
    # 时间戳
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="响应时间戳"
    )
    
    # 缓存信息
    from_cache: bool = Field(
        default=False,
        description="结果是否来自缓存"
    )


class BatchAnalysisRequest(BaseModel):
    """批量音频分析请求"""
    model_config = ConfigDict(validate_assignment=True)
    
    batch_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="批次唯一标识符"
    )
    
    requests: List[AudioAnalysisRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="批量分析请求列表"
    )
    
    parallel_processing: bool = Field(
        default=True,
        description="是否并行处理"
    )
    
    max_concurrent: PositiveInt = Field(
        default=5,
        le=20,
        description="最大并发数"
    )
    
    fail_fast: bool = Field(
        default=False,
        description="是否快速失败（遇到错误立即停止）"
    )


class BatchAnalysisResponse(BaseModel):
    """批量音频分析响应"""
    model_config = ConfigDict(validate_assignment=True)
    
    batch_id: str = Field(
        ...,
        description="对应的批次ID"
    )
    
    total_requests: PositiveInt = Field(
        ...,
        description="总请求数"
    )
    
    successful_requests: int = Field(
        default=0,
        description="成功处理的请求数"
    )
    
    failed_requests: int = Field(
        default=0,
        description="失败的请求数"
    )
    
    results: List[AudioAnalysisResponse] = Field(
        default_factory=list,
        description="分析结果列表"
    )
    
    errors: List[Dict[str, str]] = Field(
        default_factory=list,
        description="错误信息列表"
    )
    
    total_processing_time: PositiveFloat = Field(
        ...,
        description="总处理时间（秒）"
    )
    
    average_processing_time: Optional[float] = Field(
        default=None,
        description="平均处理时间（秒）"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="响应时间戳"
    )


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    model_config = ConfigDict(validate_assignment=True)
    
    status: str = Field(
        ...,
        description="服务状态",
        examples=["healthy", "unhealthy", "degraded"]
    )
    
    version: str = Field(
        ...,
        description="服务版本"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="检查时间戳"
    )
    
    checks: Dict[str, bool] = Field(
        default_factory=dict,
        description="各组件健康状态"
    )
    
    performance_stats: Optional[Dict[str, Any]] = Field(
        default=None,
        description="性能统计信息"
    )
    
    uptime: Optional[float] = Field(
        default=None,
        description="运行时间（秒）"
    ) 