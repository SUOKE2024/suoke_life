#!/usr/bin/env python

"""
对话模型定义
"""

from dataclasses import dataclass
from datetime import datetime


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
