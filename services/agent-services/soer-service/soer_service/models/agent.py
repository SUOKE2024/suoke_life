"""
智能体相关模型
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


class AgentMessage(BaseModel):
    """智能体消息模型"""
    message_id: str = Field(..., description="消息ID")
    user_id: str = Field(..., description="用户ID")
    content: str = Field(..., description="消息内容")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class AgentResponse(BaseModel):
    """智能体响应模型"""
    response_id: str = Field(..., description="响应ID")
    message_id: str = Field(..., description="原消息ID")
    content: str = Field(..., description="响应内容")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    suggestions: Optional[List[str]] = Field(default=None, description="建议")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ConversationHistory(BaseModel):
    """对话历史模型"""
    user_id: str = Field(..., description="用户ID")
    messages: List[AgentMessage] = Field(default_factory=list, description="消息列表")
    responses: List[AgentResponse] = Field(default_factory=list, description="响应列表")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
