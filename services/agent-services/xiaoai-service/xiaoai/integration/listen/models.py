"""
闻诊服务数据模型

定义与闻诊服务交互的数据结构
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AudioType(str, Enum):
    """音频类型"""

    VOICE = "voice"  # 语音
    BREATH = "breath"  # 呼吸音
    HEARTBEAT = "heartbeat"  # 心音
    COUGH = "cough"  # 咳嗽


class ListenAnalysisRequest(BaseModel):
    """闻诊分析请求"""

    user_id: str = Field(description="用户ID")
    session_id: str = Field(description="会话ID")
    audio_data: bytes = Field(description="音频数据")
    audio_type: AudioType = Field(description="音频类型")
    sample_rate: int = Field(default=44100, description="采样率")
    duration: float = Field(description="音频时长(秒)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class VoiceFeatures(BaseModel):
    """语音特征"""

    pitch: float = Field(description="音调")
    volume: float = Field(description="音量")
    tone_quality: str = Field(description="音质")
    speech_rate: float = Field(description="语速")
    clarity: str = Field(description="清晰度")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class BreathFeatures(BaseModel):
    """呼吸音特征"""

    breath_rate: float = Field(description="呼吸频率")
    breath_depth: str = Field(description="呼吸深度")
    breath_rhythm: str = Field(description="呼吸节律")
    abnormal_sounds: List[str] = Field(default_factory=list, description="异常音")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class HeartFeatures(BaseModel):
    """心音特征"""

    heart_rate: float = Field(description="心率")
    heart_rhythm: str = Field(description="心律")
    heart_sounds: List[str] = Field(default_factory=list, description="心音")
    murmurs: List[str] = Field(default_factory=list, description="杂音")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")


class ListenAnalysisResponse(BaseModel):
    """闻诊分析响应"""

    confidence: float = Field(ge=0.0, le=1.0, description="总体置信度")
    audio_type: AudioType = Field(description="音频类型")

    # 不同类型的分析结果
    voice_features: Optional[VoiceFeatures] = Field(default=None, description="语音特征")
    breath_features: Optional[BreathFeatures] = Field(default=None, description="呼吸音特征")
    heart_features: Optional[HeartFeatures] = Field(default=None, description="心音特征")

    # 通用分析结果
    features: Dict[str, Any] = Field(default_factory=dict, description="提取的特征")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")

    # 元数据
    processing_time: float = Field(description="处理时间(秒)")
    model_version: str = Field(description="模型版本")
    timestamp: str = Field(description="分析时间戳")


# 新的简化模型，用于重构后的客户端
class ListenRequest(BaseModel):
    """闻诊请求（简化版）"""

    audio_data: bytes = Field(description="音频数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ListenResponse(BaseModel):
    """闻诊响应（简化版）"""

    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    features: Dict[str, Any] = Field(default_factory=dict, description="提取的特征")
    analysis_results: Dict[str, Any] = Field(default_factory=dict, description="分析结果")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    processing_time: Optional[float] = Field(default=None, description="处理时间(秒)")
    timestamp: Optional[str] = Field(default=None, description="分析时间戳")
