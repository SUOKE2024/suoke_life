"""老克智能体核心模块"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .config import get_config, AgentConfig
from .exceptions import (
    LaokeServiceException, 
    AIModelException, 
    SessionException,
    ValidationException,
    ContentException
)
from .logging import get_logger, log_ai_interaction, log_business_event, log_error


class MessageRole(Enum):
    """消息角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class SessionStatus(Enum):
    """会话状态"""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class Message:
    """消息数据类"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class ConversationContext:
    """对话上下文"""
    user_id: str
    session_id: str
    messages: List[Message] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    status: SessionStatus = SessionStatus.ACTIVE
    
    def add_message(self, message: Message) -> None:
        """添加消息"""
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # 限制历史消息数量
        config = get_config()
        max_history = config.agent.conversation.max_history_turns
        
        if len(self.messages) > max_history:
            # 保留系统消息和最近的对话
            system_messages = [msg for msg in self.messages if msg.role==MessageRole.SYSTEM]
            recent_messages = [msg for msg in self.messages if msg.role!=MessageRole.SYSTEM][-max_history:]
            self.messages = system_messages + recent_messages
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]
    
    def is_expired(self, timeout_seconds: int) -> bool:
        """检查会话是否过期"""
        return (datetime.now() - self.last_activity).total_seconds() > timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "status": self.status.value
        }


class AIModelClient:
    """
AI模型客户端抽象类"""
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
       **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """生成响应"""
        raise NotImplementedError
    
    async def generate_stream_response(
        self, 
        messages: List[Dict[str, str]], 
       **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        raise NotImplementedError


class OpenAIClient(AIModelClient):
    """
OpenAI客户端实现"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = get_logger("openai_client")
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4096,
       **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """生成响应"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            start_time = time.time()
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
               **kwargs
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            content = response.choices[0].message.content
            usage = response.usage
            
            # 记录AI交互日志
            log_ai_interaction(
                model=model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                duration_ms=duration_ms
            )
            
            metadata = {
                "model": model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "duration_ms": duration_ms
            }
            
            return content, metadata
            
        except Exception as e:
            self.logger.error(f"OpenAI API调用失败: {e}")
            
            # 根据错误类型分类
            error_str = str(e).lower()
            if "timeout" in error_str:
                raise AIModelException(f"OpenAI API timeout: {e}", model, "timeout", e)
            elif "quota" in error_str or "rate_limit" in error_str:
                raise AIModelException(f"OpenAI API quota exceeded: {e}", model, "quota", e)
            else:
                raise AIModelException(f"OpenAI API error: {e}", model, "general", e)
    
    async def generate_stream_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4096,
       **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
               **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI流式API调用失败: {e}")
            raise AIModelException(f"OpenAI streaming error: {e}", model, "general", e)


class LaokeAgent:
    """老克智能体核心类"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            app_config = get_config()
            config = app_config.agent
        
        self.config = config
        self.logger = get_logger("laoke_agent")
        
        # 初始化AI模型客户端
        self.ai_client = self._create_ai_client()
        
        # 会话管理
        self.sessions: Dict[str, ConversationContext] = {}
        self.session_lock = asyncio.Lock()
        
        # 启动清理任务
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_cleanup_task()
    
    def _create_ai_client(self) -> AIModelClient:
        """创建AI模型客户端"""
        models_config = self.config.models
        
        if "gpt" in models_config.primary_model.lower():
            return OpenAIClient(
                api_key=models_config.api_key,
                base_url=models_config.base_url
            )
        else:
            # 默认使用OpenAI兼容接口
            return OpenAIClient(
                api_key=models_config.api_key,
                base_url=models_config.base_url
            )
    
    def _start_cleanup_task(self) -> None:
        """启动清理任务"""
        async def cleanup_sessions():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval)
                    await self._cleanup_expired_sessions()
                except Exception as e:
                    self.logger.error(f"会话清理任务失败: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_sessions())
    
    async def _cleanup_expired_sessions(self) -> None:
        """清理过期会话"""
        async with self.session_lock:
            expired_sessions = []
            
            for session_id, context in self.sessions.items():
                if context.is_expired(self.config.session_timeout):
                    expired_sessions.append(session_id)
                    context.status = SessionStatus.EXPIRED
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                self.logger.info(f"清理过期会话: {session_id}")
            
            if expired_sessions:
                log_business_event(
                    "sessions_cleaned",
                    count=len(expired_sessions)
                )
    
    async def create_session(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """创建新会话"""
        # 检查并发会话数量限制
        async with self.session_lock:
            active_sessions = len([s for s in self.sessions.values() if s.status==SessionStatus.ACTIVE])
            
            if active_sessions>=self.config.max_concurrent_sessions:
                raise SessionException(
                    "Maximum concurrent sessions exceeded",
                    error_type="limit_exceeded"
                )
            
            session_id = str(uuid.uuid4())
            
            # 创建会话上下文
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # 添加系统消息
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=self.config.conversation.system_prompt
            )
            context.add_message(system_message)
            
            self.sessions[session_id] = context
            
            log_business_event(
                "session_created",
                user_id=user_id,
                session_id=session_id
            )
            
            return session_id
    
    async def get_session(self, session_id: str) -> ConversationContext:
        """获取会话上下文"""
        async with self.session_lock:
            if session_id not in self.sessions:
                raise SessionException(
                    f"Session not found: {session_id}",
                    session_id=session_id,
                    error_type="not_found"
                )
            
            context = self.sessions[session_id]
            
            # 检查会话是否过期
            if context.is_expired(self.config.session_timeout):
                context.status = SessionStatus.EXPIRED
                del self.sessions[session_id]
                
                raise SessionException(
                    f"Session expired: {session_id}",
                    session_id=session_id,
                    error_type="expired"
                )
            
            return context
    
    async def terminate_session(self, session_id: str) -> None:
        """终止会话"""
        async with self.session_lock:
            if session_id in self.sessions:
                context = self.sessions[session_id]
                context.status = SessionStatus.TERMINATED
                del self.sessions[session_id]
                
                log_business_event(
                    "session_terminated",
                    user_id=context.user_id,
                    session_id=session_id
                )
    
    def _validate_message(self, content: str) -> None:
        """验证消息内容"""
        if not content or not content.strip():
            raise ValidationException("消息内容不能为空")
        
        max_tokens = self.config.conversation.max_tokens_per_message
        if len(content) > max_tokens:
            raise ContentException(
                f"消息内容过长，最大允许{max_tokens}个字符",
                error_type="too_long"
            )
    
    async def chat(
        self, 
        session_id: str, 
        message: str, 
        stream: bool = False,
       **kwargs
    ) -> str:
        """对话接口"""
        try:
            # 验证消息
            self._validate_message(message)
            
            # 获取会话上下文
            context = await self.get_session(session_id)
            
            # 添加用户消息
            user_message = Message(
                role=MessageRole.USER,
                content=message
            )
            context.add_message(user_message)
            
            # 生成响应
            if stream:
                return await self._generate_stream_response(context,**kwargs)
            else:
                return await self._generate_response(context,**kwargs)
                
        except Exception as e:
            log_error(e, {
                "session_id": session_id,
                "message_length": len(message) if message else 0
            })
            raise
    
    async def _generate_response(self, context: ConversationContext,**kwargs) -> str:
        """生成普通响应"""
        try:
            messages = context.get_conversation_history()
            
            # 调用AI模型
            response_content, metadata = await self.ai_client.generate_response(
                messages=messages,
                model=self.config.models.primary_model,
                temperature=self.config.models.temperature,
                max_tokens=self.config.models.max_tokens,
               **kwargs
            )
            
            # 添加助手消息
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=response_content,
                metadata=metadata
            )
            context.add_message(assistant_message)
            
            log_business_event(
                "chat_response_generated",
                user_id=context.user_id,
                session_id=context.session_id,
                model=metadata.get("model"),
                tokens=metadata.get("usage", {}).get("total_tokens")
            )
            
            return response_content
            
        except AIModelException:
            # AI模型异常直接抛出
            raise
        except Exception as e:
            # 其他异常转换为AI模型异常
            raise AIModelException(f"Failed to generate response: {e}", cause=e)
    
    async def _generate_stream_response(self, context: ConversationContext,**kwargs) -> AsyncGenerator[str, None]:
        """生成流式响应"""
        try:
            messages = context.get_conversation_history()
            
            full_response = ""
            
            async for chunk in self.ai_client.generate_stream_response(
                messages=messages,
                model=self.config.models.primary_model,
                temperature=self.config.models.temperature,
                max_tokens=self.config.models.max_tokens,
               **kwargs
            ):
                full_response+=chunk
                yield chunk
            
            # 添加助手消息
            assistant_message = Message(
                role=MessageRole.ASSISTANT,
                content=full_response
            )
            context.add_message(assistant_message)
            
            log_business_event(
                "chat_stream_response_generated",
                user_id=context.user_id,
                session_id=context.session_id,
                response_length=len(full_response)
            )
            
        except AIModelException:
            raise
        except Exception as e:
            raise AIModelException(f"Failed to generate stream response: {e}", cause=e)
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        context = await self.get_session(session_id)
        
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "status": context.status.value,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.last_activity.isoformat(),
            "message_count": len(context.messages),
            "metadata": context.metadata
        }
    
    async def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取对话历史"""
        context = await self.get_session(session_id)
        
        messages = context.messages
        if limit:
            messages = messages[-limit:]
        
        return [msg.to_dict() for msg in messages]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        active_sessions = len([s for s in self.sessions.values() if s.status==SessionStatus.ACTIVE])
        
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": active_sessions,
            "max_concurrent_sessions": self.config.max_concurrent_sessions,
            "session_timeout": self.config.session_timeout,
            "cleanup_interval": self.config.cleanup_interval
        }
    
    async def shutdown(self) -> None:
        """关闭智能体"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # 终止所有会话
        async with self.session_lock:
            for session_id in list(self.sessions.keys()):
                await self.terminate_session(session_id)
        
        self.logger.info("老克智能体已关闭")


# 全局智能体实例
_agent_instance: Optional[LaokeAgent] = None


def get_agent() -> LaokeAgent:
    """获取全局智能体实例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LaokeAgent()
    return _agent_instance


async def shutdown_agent() -> None:
    """关闭全局智能体实例"""
    global _agent_instance
    if _agent_instance:
        await _agent_instance.shutdown()
        _agent_instance = None
