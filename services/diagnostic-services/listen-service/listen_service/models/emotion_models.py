"""
emotion_models - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

"""
情绪分析相关的数据模型

包含情绪状态、情绪评分、心境状态等数据结构定义。
"""



class EmotionType(Enum):
    """情绪类型"""

    JOY = "joy"          # 喜
    ANGER = "anger"      # 怒
    SADNESS = "sadness"  # 悲
    FEAR = "fear"        # 恐
    SURPRISE = "surprise" # 惊
    DISGUST = "disgust"  # 厌
    NEUTRAL = "neutral"  # 平静


class MoodLevel(Enum):
    """心境水平"""

    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class EmotionScore:
    """情绪评分"""

    emotion_type: EmotionType
    score: float  # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    intensity: str  # "weak", "moderate", "strong"
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory = datetime.now)


@dataclass
class EmotionAnalysis:
    """情绪分析结果"""

    primary_emotion: EmotionType
    emotion_scores: List[EmotionScore]
    overall_valence: float  # - 1.0 (negative) to 1.0 (positive)
    overall_arousal: float  # 0.0 (calm) to 1.0 (excited)
    stability: float  # 0.0 (unstable) to 1.0 (stable)
    confidence: float
    analysis_duration_ms: float
    audio_features_used: List[str]
    timestamp: datetime = field(default_factory = datetime.now)


@dataclass
class MoodState:
    """心境状态"""

    mood_level: MoodLevel
    dominant_emotions: List[EmotionType]
    energy_level: float  # 0.0 - 1.0
    stress_level: float  # 0.0 - 1.0
    emotional_balance: float  # 0.0 - 1.0
    mood_description: str
    recommendations: List[str] = field(default_factory = list)
    timestamp: datetime = field(default_factory = datetime.now)


@dataclass
class EmotionTrend:
    """情绪趋势"""

    time_period: str  # "hourly", "daily", "weekly"
    emotion_changes: Dict[str, List[float]]
    trend_direction: str  # "improving", "declining", "stable"
    volatility: float  # 0.0 - 1.0
    pattern_detected: bool
    pattern_description: str = ""
    created_at: datetime = field(default_factory = datetime.now)


@dataclass
class EmotionalProfile:
    """情绪档案"""

    patient_id: str
    baseline_emotions: Dict[EmotionType, float]
    typical_mood_range: tuple[MoodLevel, MoodLevel]
    emotional_triggers: List[str]
    coping_strategies: List[str]
    last_updated: datetime = field(default_factory = datetime.now)