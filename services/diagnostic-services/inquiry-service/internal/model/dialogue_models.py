from typing import Dict, List, Any, Optional, Union

"""
dialogue_models - 索克生活项目模块
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

#! / usr / bin / env python

"""
对话模型定义
"""



@dataclass
class Message:
    """对话消息"""

    id: str
    role: str  # "user", "system", "assistant"
    content: str
    created_at: datetime
    metadata: dict | None = None


@dataclass
class DialogueSession:
    """对话会话"""

    id: str
    user_id: str
    status: str  # "active", "completed", "expired"
    created_at: datetime
    last_interaction: datetime
    messages: list[Message]
    metadata: dict | None = None


@dataclass
class InteractionRequest:
    """交互请求"""

    session_id: str
    user_id: str
    content: str
    context: dict | None = None


@dataclass
class InteractionResponse:
    """交互响应"""

    response_text: str
    response_type: str
    detected_symptoms: list[str]
    follow_up_questions: list[str]
    confidence: float
    metadata: dict | None = None


@dataclass
class InquirySummary:
    """问诊摘要"""

    session_id: str
    user_id: str
    symptoms: list[dict]
    patterns: list[dict]
    recommendations: list[str]
    potential_risks: list[str]
    confidence: float
    created_at: datetime


class SymptomSeverity(Enum):
    """症状严重程度"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class SymptomDuration(Enum):
    """症状持续时间"""
    ACUTE = "acute"  # 急性（<1周）
    SUBACUTE = "subacute"  # 亚急性（1 - 4周）
    CHRONIC = "chronic"  # 慢性（>4周）


@dataclass
class Symptom:
    """症状"""
    name: str
    confidence: float
    severity: SymptomSeverity = SymptomSeverity.MILD
    duration: SymptomDuration = SymptomDuration.ACUTE
    description: str = ""
    body_part: str = ""
    onset_time: datetime = None
    location: str = ""
    metadata: dict = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TCMPattern:
    """中医证型"""
    name: str
    score: float
    category: str = ""
    description: str = ""
    key_symptoms: list = None
    recommendations: list = None
    confidence: float = 0.0

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.key_symptoms is None:
            self.key_symptoms = []
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class TCMPatternMappingResult:
    """中医证型映射结果"""
    patterns: list[TCMPattern]
    confidence: float
    interpretation: str = ""
    metadata: dict = None

    def __post_init__(self)-> None:
        """TODO: 添加文档字符串"""
        if self.metadata is None:
            self.metadata = {}
