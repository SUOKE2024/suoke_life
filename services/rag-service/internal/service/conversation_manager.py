"""
智能对话管理器

支持多轮对话、上下文管理、对话状态跟踪和智能体协同
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

from loguru import logger

class ConversationState(Enum):
    """对话状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    WAITING_INPUT = "waiting_input"

class MessageType(Enum):
    """消息类型"""
    USER_QUERY = "user_query"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_MESSAGE = "system_message"
    CLARIFICATION = "clarification"
    RECOMMENDATION = "recommendation"
    WARNING = "warning"

class AgentType(Enum):
    """智能体类型"""
    XIAOAI = "xiaoai"  # 小艾 - AI助手
    XIAOKE = "xiaoke"  # 小克 - 专业诊断
    LAOKE = "laoke"    # 老克 - 资深专家
    SOER = "soer"      # 索儿 - 健康管理

@dataclass
class Message:
    """对话消息"""
    id: str
    conversation_id: str
    message_type: MessageType
    content: str
    agent_type: Optional[AgentType] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ConversationContext:
    """对话上下文"""
    user_id: str
    session_id: str
    current_topic: Optional[str] = None
    user_profile: Dict[str, Any] = None
    health_context: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    conversation_history: List[str] = None
    
    def __post_init__(self):
        if self.user_profile is None:
            self.user_profile = {}
        if self.health_context is None:
            self.health_context = {}
        if self.preferences is None:
            self.preferences = {}
        if self.conversation_history is None:
            self.conversation_history = []

@dataclass
class Conversation:
    """对话会话"""
    id: str
    user_id: str
    state: ConversationState
    context: ConversationContext
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    current_agent: Optional[AgentType] = None
    escalation_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)

class ConversationManager:
    """智能对话管理器"""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        max_conversation_length: int = 100,
        context_window_size: int = 10,
        session_timeout: int = 3600
    ):
        self.redis = redis_client
        self.max_conversation_length = max_conversation_length
        self.context_window_size = context_window_size
        self.session_timeout = session_timeout
        
        # 对话存储
        self.conversations: Dict[str, Conversation] = {}
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)
        
        # 上下文管理
        self.context_cache: Dict[str, ConversationContext] = {}
        
        # 智能体状态
        self.agent_availability: Dict[AgentType, bool] = {
            agent: True for agent in AgentType
        }
        
        logger.info("对话管理器初始化完成")
    
    async def create_conversation(
        self,
        user_id: str,
        initial_message: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """创建新对话"""
        try:
            conversation_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            
            # 创建对话上下文
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                user_profile=user_profile or {}
            )
            
            # 创建初始消息
            initial_msg = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                message_type=MessageType.USER_QUERY,
                content=initial_message
            )
            
            # 创建对话
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                state=ConversationState.ACTIVE,
                context=context,
                messages=[initial_msg],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 存储对话
            await self._store_conversation(conversation)
            
            # 更新用户会话
            self.user_sessions[user_id].append(conversation_id)
            
            logger.info(f"创建新对话: {conversation_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"创建对话失败: {e}")
            raise
    
    async def add_message(
        self,
        conversation_id: str,
        content: str,
        message_type: MessageType,
        agent_type: Optional[AgentType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """添加消息到对话"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                raise ValueError(f"对话不存在: {conversation_id}")
            
            # 创建消息
            message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                message_type=message_type,
                content=content,
                agent_type=agent_type,
                metadata=metadata or {}
            )
            
            # 添加到对话
            conversation.messages.append(message)
            conversation.updated_at = datetime.now()
            
            # 限制对话长度
            if len(conversation.messages) > self.max_conversation_length:
                conversation.messages = conversation.messages[-self.max_conversation_length:]
            
            # 更新对话状态
            await self._update_conversation_state(conversation, message)
            
            # 存储对话
            await self._store_conversation(conversation)
            
            logger.debug(f"添加消息到对话 {conversation_id}: {message_type.value}")
            return message
            
        except Exception as e:
            logger.error(f"添加消息失败: {e}")
            raise
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取对话"""
        try:
            # 先从内存缓存获取
            if conversation_id in self.conversations:
                return self.conversations[conversation_id]
            
            # 从Redis获取
            conversation_data = await self.redis.get(f"conversation:{conversation_id}")
            if conversation_data:
                data = json.loads(conversation_data)
                conversation = self._deserialize_conversation(data)
                self.conversations[conversation_id] = conversation
                return conversation
            
            return None
            
        except Exception as e:
            logger.error(f"获取对话失败: {e}")
            return None
    
    async def get_conversation_context(
        self,
        conversation_id: str,
        include_history: bool = True
    ) -> Optional[Dict[str, Any]]:
        """获取对话上下文"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return None
            
            context = {
                "user_id": conversation.user_id,
                "session_id": conversation.context.session_id,
                "current_topic": conversation.context.current_topic,
                "user_profile": conversation.context.user_profile,
                "health_context": conversation.context.health_context,
                "preferences": conversation.context.preferences,
                "current_agent": conversation.current_agent.value if conversation.current_agent else None,
                "conversation_state": conversation.state.value
            }
            
            if include_history:
                # 获取最近的消息作为上下文
                recent_messages = conversation.messages[-self.context_window_size:]
                context["recent_messages"] = [
                    {
                        "type": msg.message_type.value,
                        "content": msg.content,
                        "agent": msg.agent_type.value if msg.agent_type else None,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in recent_messages
                ]
            
            return context
            
        except Exception as e:
            logger.error(f"获取对话上下文失败: {e}")
            return None
    
    async def update_context(
        self,
        conversation_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """更新对话上下文"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            # 更新上下文
            if "current_topic" in updates:
                conversation.context.current_topic = updates["current_topic"]
            
            if "health_context" in updates:
                conversation.context.health_context.update(updates["health_context"])
            
            if "preferences" in updates:
                conversation.context.preferences.update(updates["preferences"])
            
            if "user_profile" in updates:
                conversation.context.user_profile.update(updates["user_profile"])
            
            conversation.updated_at = datetime.now()
            
            # 存储更新
            await self._store_conversation(conversation)
            
            logger.debug(f"更新对话上下文: {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"更新对话上下文失败: {e}")
            return False
    
    async def assign_agent(
        self,
        conversation_id: str,
        agent_type: AgentType,
        reason: Optional[str] = None
    ) -> bool:
        """分配智能体"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            # 检查智能体可用性
            if not self.agent_availability.get(agent_type, False):
                logger.warning(f"智能体 {agent_type.value} 不可用")
                return False
            
            # 分配智能体
            conversation.current_agent = agent_type
            conversation.updated_at = datetime.now()
            
            # 添加系统消息
            await self.add_message(
                conversation_id,
                f"已分配智能体: {agent_type.value}" + (f" - {reason}" if reason else ""),
                MessageType.SYSTEM_MESSAGE,
                agent_type
            )
            
            logger.info(f"分配智能体 {agent_type.value} 到对话 {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"分配智能体失败: {e}")
            return False
    
    async def escalate_conversation(
        self,
        conversation_id: str,
        target_agent: AgentType,
        reason: str
    ) -> bool:
        """升级对话到高级智能体"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            # 更新状态
            conversation.state = ConversationState.ESCALATED
            conversation.escalation_reason = reason
            conversation.updated_at = datetime.now()
            
            # 分配新智能体
            await self.assign_agent(conversation_id, target_agent, f"升级原因: {reason}")
            
            logger.info(f"对话 {conversation_id} 升级到 {target_agent.value}")
            return True
            
        except Exception as e:
            logger.error(f"升级对话失败: {e}")
            return False
    
    async def end_conversation(
        self,
        conversation_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """结束对话"""
        try:
            conversation = await self.get_conversation(conversation_id)
            if not conversation:
                return False
            
            # 更新状态
            conversation.state = ConversationState.COMPLETED
            conversation.updated_at = datetime.now()
            
            # 添加结束消息
            await self.add_message(
                conversation_id,
                f"对话已结束" + (f" - {reason}" if reason else ""),
                MessageType.SYSTEM_MESSAGE
            )
            
            # 存储最终状态
            await self._store_conversation(conversation)
            
            logger.info(f"对话 {conversation_id} 已结束")
            return True
            
        except Exception as e:
            logger.error(f"结束对话失败: {e}")
            return False
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 10,
        state_filter: Optional[ConversationState] = None
    ) -> List[Conversation]:
        """获取用户的对话列表"""
        try:
            conversations = []
            conversation_ids = self.user_sessions.get(user_id, [])
            
            for conv_id in conversation_ids[-limit:]:
                conversation = await self.get_conversation(conv_id)
                if conversation:
                    if state_filter is None or conversation.state == state_filter:
                        conversations.append(conversation)
            
            return sorted(conversations, key=lambda x: x.updated_at, reverse=True)
            
        except Exception as e:
            logger.error(f"获取用户对话失败: {e}")
            return []
    
    async def cleanup_expired_conversations(self) -> int:
        """清理过期对话"""
        try:
            cleaned_count = 0
            current_time = datetime.now()
            
            # 获取所有对话ID
            conversation_keys = await self.redis.keys("conversation:*")
            
            for key in conversation_keys:
                conversation_data = await self.redis.get(key)
                if conversation_data:
                    data = json.loads(conversation_data)
                    expires_at = datetime.fromisoformat(data["expires_at"])
                    
                    if current_time > expires_at:
                        await self.redis.delete(key)
                        conversation_id = key.decode().split(":")[-1]
                        self.conversations.pop(conversation_id, None)
                        cleaned_count += 1
            
            logger.info(f"清理了 {cleaned_count} 个过期对话")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期对话失败: {e}")
            return 0
    
    async def _store_conversation(self, conversation: Conversation):
        """存储对话到Redis"""
        try:
            conversation_data = self._serialize_conversation(conversation)
            await self.redis.setex(
                f"conversation:{conversation.id}",
                self.session_timeout,
                json.dumps(conversation_data)
            )
            
            # 更新内存缓存
            self.conversations[conversation.id] = conversation
            
        except Exception as e:
            logger.error(f"存储对话失败: {e}")
            raise
    
    async def _update_conversation_state(
        self,
        conversation: Conversation,
        message: Message
    ):
        """根据消息更新对话状态"""
        try:
            # 根据消息类型和内容更新状态
            if message.message_type == MessageType.USER_QUERY:
                if conversation.state == ConversationState.WAITING_INPUT:
                    conversation.state = ConversationState.ACTIVE
            
            elif message.message_type == MessageType.CLARIFICATION:
                conversation.state = ConversationState.WAITING_INPUT
            
            elif message.message_type == MessageType.WARNING:
                # 可能需要升级到专业智能体
                if conversation.current_agent == AgentType.XIAOAI:
                    await self.escalate_conversation(
                        conversation.id,
                        AgentType.XIAOKE,
                        "检测到健康警告"
                    )
            
        except Exception as e:
            logger.error(f"更新对话状态失败: {e}")
    
    def _serialize_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """序列化对话对象"""
        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "state": conversation.state.value,
            "context": asdict(conversation.context),
            "messages": [asdict(msg) for msg in conversation.messages],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "expires_at": conversation.expires_at.isoformat() if conversation.expires_at else None,
            "current_agent": conversation.current_agent.value if conversation.current_agent else None,
            "escalation_reason": conversation.escalation_reason
        }
    
    def _deserialize_conversation(self, data: Dict[str, Any]) -> Conversation:
        """反序列化对话对象"""
        # 反序列化消息
        messages = []
        for msg_data in data["messages"]:
            msg_data["message_type"] = MessageType(msg_data["message_type"])
            if msg_data["agent_type"]:
                msg_data["agent_type"] = AgentType(msg_data["agent_type"])
            msg_data["timestamp"] = datetime.fromisoformat(msg_data["timestamp"])
            messages.append(Message(**msg_data))
        
        # 反序列化上下文
        context_data = data["context"]
        context = ConversationContext(**context_data)
        
        # 反序列化对话
        return Conversation(
            id=data["id"],
            user_id=data["user_id"],
            state=ConversationState(data["state"]),
            context=context,
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            current_agent=AgentType(data["current_agent"]) if data["current_agent"] else None,
            escalation_reason=data["escalation_reason"]
        ) 