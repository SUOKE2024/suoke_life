"""
session - 索克生活项目模块
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import uuid

#! / usr / bin / env python

"""
问诊会话模型
定义问诊会话的数据结构，包括会话状态、问答历史等
"""



class SessionStatus(str, Enum):
    """会话状态枚举"""

    PENDING = "pending"  # 等待开始
    ACTIVE = "active"  # 进行中
    PAUSED = "paused"  # 暂停
    COMPLETED = "completed"  # 已完成
    EXPIRED = "expired"  # 已过期
    FAILED = "failed"  # 失败


class MessageRole(str, Enum):
    """消息角色枚举"""

    SYSTEM = "system"  # 系统消息
    USER = "user"  # 用户消息
    ASSISTANT = "assistant"  # 助手（医生）消息
    FUNCTION = "function"  # 函数调用


@dataclass
class Message:
    """对话消息"""

    role: MessageRole  # 消息角色
    content: str  # 消息内容
    timestamp: float = field(default_factory = time.time)  # 消息时间戳
    message_id: str = field(default_factory = lambda: str(uuid.uuid4()))  # 消息ID
    metadata: dict[str, Any] = field(default_factory = dict)  # 元数据


@dataclass
class InquirySession:
    """问诊会话"""

    session_id: str  # 会话ID
    user_id: str  # 用户ID
    status: SessionStatus  # 会话状态
    messages: list[Message] = field(default_factory = list)  # 消息历史
    created_at: float = field(default_factory = time.time)  # 创建时间
    updated_at: float = field(default_factory = time.time)  # 更新时间
    expires_at: float | None = None  # 过期时间
    metadata: dict[str, Any] = field(
        default_factory = dict
    )  # 元数据，可包含会话上下文信息

    # 症状和证型分析结果
    extracted_symptoms: list[dict[str, Any]] = field(default_factory = list)  # 提取的症状
    tcm_patterns: list[dict[str, Any]] = field(default_factory = list)  # 中医证型
    health_risks: list[dict[str, Any]] = field(default_factory = list)  # 健康风险

    # 摘要和结论
    summary: str | None = None  # 会话摘要
    conclusion: str | None = None  # 会话结论

    def add_message(
        self, role: MessageRole, content: str, metadata: dict[str, Any] | None = None
    )-> Message:
        """添加新消息到会话"""
        message = Message(role = role, content = content, metadata = metadata or {})
        self.messages.append(message)
        self.updated_at = time.time()
        return message

    def get_conversation_history(
        self, max_messages: int | None = None
    )-> list[dict[str, Any]]:
        """获取对话历史（格式化为LLM输入格式）"""
        history = []
        messages = self.messages[ - max_messages:] if max_messages else self.messages

        for msg in messages:
            history.append({"role": msg.role, "content": msg.content})

        return history

    def update_status(self, status: SessionStatus)-> None:
        """更新会话状态"""
        self.status = status
        self.updated_at = time.time()

        # 如果状态为已完成或失败，设置过期时间
        if status in [SessionStatus.COMPLETED, SessionStatus.FAILED]:
            # 默认24小时后过期
            self.expires_at = time.time() + 86400

    def is_expired(self)-> bool:
        """检查会话是否已过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def to_dict(self)-> dict[str, Any]:
        """转换为字典，用于存储"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "status": self.status.value,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "message_id": msg.message_id,
                    "metadata": msg.metadata,
                }
                for msg in self.messages
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata,
            "extracted_symptoms": self.extracted_symptoms,
            "tcm_patterns": self.tcm_patterns,
            "health_risks": self.health_risks,
            "summary": self.summary,
            "conclusion": self.conclusion,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any])-> "InquirySession":
        """从字典创建会话对象"""
        messages = [
            Message(
                role = MessageRole(msg["role"]),
                content = msg["content"],
                timestamp = msg["timestamp"],
                message_id = msg["message_id"],
                metadata = msg.get("metadata", {}),
            )
            for msg in data.get("messages", [])
        ]

        return cls(
            session_id = data["session_id"],
            user_id = data["user_id"],
            status = SessionStatus(data["status"]),
            messages = messages,
            created_at = data["created_at"],
            updated_at = data["updated_at"],
            expires_at = data.get("expires_at"),
            metadata = data.get("metadata", {}),
            extracted_symptoms = data.get("extracted_symptoms", []),
            tcm_patterns = data.get("tcm_patterns", []),
            health_risks = data.get("health_risks", []),
            summary = data.get("summary"),
            conclusion = data.get("conclusion"),
        )
