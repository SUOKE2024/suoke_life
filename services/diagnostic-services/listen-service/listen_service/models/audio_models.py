"""
音频相关数据模型

定义音频处理和分析相关的数据结构。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AudioFormat(str, Enum):
    """音频格式枚举"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"


class AnalysisType(str, Enum):
    """分析类型枚举"""
    BASIC = "basic"              # 基础音频分析
    ADVANCED = "advanced"        # 高级音频分析
    TCM = "tcm"                 # 中医分析
    EMOTION = "emotion"         # 情感分析
    COMPREHENSIVE = "comprehensive"  # 综合分析


class AudioMetadata(BaseModel):
    """音频元数据"""
    duration: float = Field(..., description="音频时长（秒）", ge=0)
    sample_rate: int = Field(..., description="采样率", ge=1000)
    channels: int = Field(..., description="声道数", ge=1, le=8)
    format: AudioFormat = Field(..., description="音频格式")
    bit_depth: int = Field(..., description="位深度", ge=8, le=32)
    file_size: int = Field(..., description="文件大小（字节）", ge=0)
    
    @validator('duration')
    def validate_duration(cls, v):
        if v > 3600:  # 1小时限制
            raise ValueError('音频时长不能超过1小时')
        return v


class AudioFeatures(BaseModel):
    """音频特征"""
    # 频谱特征
    mfcc: List[List[float]] = Field(..., description="MFCC特征")
    spectral_centroid: List[float] = Field(..., description="频谱质心")
    spectral_bandwidth: List[float] = Field(..., description="频谱带宽")
    spectral_rolloff: List[float] = Field(..., description="频谱滚降")
    zero_crossing_rate: List[float] = Field(..., description="过零率")
    chroma: List[List[float]] = Field(..., description="色度特征")
    mel_spectrogram: List[List[float]] = Field(..., description="梅尔频谱图")
    
    # 时域特征
    rms_energy: List[float] = Field(..., description="RMS能量")
    tempo: float = Field(..., description="节拍速度", ge=0)
    onset_frames: List[int] = Field(..., description="起始帧")
    duration: float = Field(..., description="持续时间", ge=0)
    silence_ratio: float = Field(..., description="静音比例", ge=0, le=1)
    
    # 高级特征
    mean_amplitude: float = Field(..., description="平均振幅")
    std_amplitude: float = Field(..., description="振幅标准差")
    skewness: float = Field(..., description="偏度")
    kurtosis: float = Field(..., description="峰度")
    spectral_centroid_manual: float = Field(..., description="手动计算的频谱质心")
    spectral_spread: float = Field(..., description="频谱扩散")
    fundamental_frequency: float = Field(..., description="基频", ge=0)
    harmonic_ratio: float = Field(..., description="谐波比", ge=0, le=1)


class AnalysisRequest(BaseModel):
    """分析请求"""
    request_id: str = Field(..., description="请求ID")
    analysis_type: AnalysisType = Field(default=AnalysisType.BASIC, description="分析类型")
    enable_tcm_analysis: bool = Field(default=False, description="启用中医分析")
    enable_emotion_analysis: bool = Field(default=False, description="启用情感分析")
    enable_constitution_analysis: bool = Field(default=False, description="启用体质分析")
    
    # 音频处理参数
    normalize_audio: bool = Field(default=True, description="音频归一化")
    remove_silence: bool = Field(default=True, description="移除静音")
    apply_filter: bool = Field(default=False, description="应用滤波器")
    
    # 特征提取参数
    extract_mfcc: bool = Field(default=True, description="提取MFCC特征")
    extract_spectral: bool = Field(default=True, description="提取频谱特征")
    extract_temporal: bool = Field(default=True, description="提取时域特征")
    
    # 缓存设置
    use_cache: bool = Field(default=True, description="使用缓存")
    cache_ttl: int = Field(default=3600, description="缓存TTL（秒）", ge=0)
    
    @validator('request_id')
    def validate_request_id(cls, v):
        if not v or len(v) < 8:
            raise ValueError('请求ID长度至少为8个字符')
        return v


class AnalysisResult(BaseModel):
    """分析结果"""
    request_id: str = Field(..., description="请求ID")
    metadata: AudioMetadata = Field(..., description="音频元数据")
    features: AudioFeatures = Field(..., description="音频特征")
    quality: str = Field(..., description="音频质量评级")
    processing_time: float = Field(..., description="处理时间（秒）", ge=0)
    timestamp: float = Field(..., description="分析时间戳")
    
    # 可选的高级分析结果
    tcm_diagnosis: Optional[Dict[str, Any]] = Field(None, description="中医诊断结果")
    emotion_analysis: Optional[Dict[str, Any]] = Field(None, description="情感分析结果")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AudioUploadRequest(BaseModel):
    """音频上传请求"""
    filename: str = Field(..., description="文件名")
    content_type: str = Field(..., description="内容类型")
    file_size: int = Field(..., description="文件大小", ge=0, le=50*1024*1024)  # 50MB限制
    analysis_request: AnalysisRequest = Field(..., description="分析请求")
    
    @validator('filename')
    def validate_filename(cls, v):
        allowed_extensions = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'不支持的文件格式，支持的格式: {", ".join(allowed_extensions)}')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'audio/wav', 'audio/wave', 'audio/x-wav',
            'audio/mpeg', 'audio/mp3',
            'audio/flac',
            'audio/aac', 'audio/x-aac',
            'audio/ogg', 'audio/vorbis',
            'audio/mp4', 'audio/m4a'
        ]
        if v not in allowed_types:
            raise ValueError(f'不支持的内容类型: {v}')
        return v


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""
    batch_id: str = Field(..., description="批次ID")
    requests: List[AnalysisRequest] = Field(..., description="分析请求列表", min_items=1, max_items=10)
    priority: int = Field(default=0, description="优先级", ge=0, le=10)
    callback_url: Optional[str] = Field(None, description="回调URL")
    
    @validator('batch_id')
    def validate_batch_id(cls, v):
        if not v or len(v) < 8:
            raise ValueError('批次ID长度至少为8个字符')
        return v


class BatchAnalysisResult(BaseModel):
    """批量分析结果"""
    batch_id: str = Field(..., description="批次ID")
    results: List[AnalysisResult] = Field(..., description="分析结果列表")
    failed_requests: List[Dict[str, str]] = Field(default_factory=list, description="失败的请求")
    total_processing_time: float = Field(..., description="总处理时间（秒）", ge=0)
    success_count: int = Field(..., description="成功数量", ge=0)
    failure_count: int = Field(..., description="失败数量", ge=0)
    timestamp: float = Field(..., description="完成时间戳")


class AudioProcessingConfig(BaseModel):
    """音频处理配置"""
    sample_rate: int = Field(default=22050, description="目标采样率", ge=8000, le=48000)
    n_mfcc: int = Field(default=13, description="MFCC系数数量", ge=1, le=50)
    n_fft: int = Field(default=2048, description="FFT窗口大小", ge=512, le=8192)
    hop_length: int = Field(default=512, description="跳跃长度", ge=128, le=2048)
    n_mels: int = Field(default=128, description="梅尔滤波器数量", ge=64, le=256)
    
    # 预处理参数
    normalize: bool = Field(default=True, description="归一化")
    trim_silence: bool = Field(default=True, description="裁剪静音")
    preemphasis: float = Field(default=0.97, description="预加重系数", ge=0, le=1)
    
    # 质量控制
    min_duration: float = Field(default=0.5, description="最小时长（秒）", ge=0.1)
    max_duration: float = Field(default=300, description="最大时长（秒）", le=3600)
    min_sample_rate: int = Field(default=8000, description="最小采样率")
    
    @validator('hop_length')
    def validate_hop_length(cls, v, values):
        if 'n_fft' in values and v >= values['n_fft']:
            raise ValueError('hop_length必须小于n_fft')
        return v


class AudioAnalysisError(BaseModel):
    """音频分析错误"""
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    request_id: Optional[str] = Field(None, description="请求ID")
    timestamp: float = Field(..., description="错误时间戳")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")


class AudioAnalysisStats(BaseModel):
    """音频分析统计"""
    total_requests: int = Field(default=0, description="总请求数", ge=0)
    successful_requests: int = Field(default=0, description="成功请求数", ge=0)
    failed_requests: int = Field(default=0, description="失败请求数", ge=0)
    average_processing_time: float = Field(default=0.0, description="平均处理时间", ge=0)
    total_audio_duration: float = Field(default=0.0, description="总音频时长", ge=0)
    cache_hit_rate: float = Field(default=0.0, description="缓存命中率", ge=0, le=1)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    @property
    def failure_rate(self) -> float:
        """失败率"""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests