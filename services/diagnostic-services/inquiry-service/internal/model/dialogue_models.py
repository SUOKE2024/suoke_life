#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
对话模型定义
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """对话消息"""
    id: str
    role: str  # "user", "system", "assistant"
    content: str
    created_at: datetime
    metadata: Optional[Dict] = None

@dataclass
class DialogueSession:
    """对话会话"""
    id: str
    user_id: str
    status: str  # "active", "completed", "expired"
    created_at: datetime
    last_interaction: datetime
    messages: List[Message]
    metadata: Optional[Dict] = None

@dataclass
class InteractionRequest:
    """交互请求"""
    session_id: str
    user_id: str
    content: str
    context: Optional[Dict] = None

@dataclass
class InteractionResponse:
    """交互响应"""
    response_text: str
    response_type: str
    detected_symptoms: List[str]
    follow_up_questions: List[str]
    confidence: float
    metadata: Optional[Dict] = None

@dataclass
class InquirySummary:
    """问诊摘要"""
    session_id: str
    user_id: str
    symptoms: List[Dict]
    patterns: List[Dict]
    recommendations: List[str]
    potential_risks: List[str]
    confidence: float
    created_at: datetime