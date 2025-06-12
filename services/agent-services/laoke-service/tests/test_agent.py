"""老克智能体核心功能单元测试"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from laoke_service.core.agent import (
    LaokeAgent,
    Message,
    MessageRole,
    ConversationContext,
    SessionStatus,
    OpenAIClient,
    get_agent,
    shutdown_agent
)
from laoke_service.core.config import AgentConfig, AIModelConfig, ConversationConfig
from laoke_service.core.exceptions import (
    SessionException,
    ValidationException,
    AIModelException
)


class TestMessage:
    """消息类测试"""
    
    def test_message_creation(self):
        """测试消息创建"""
        message = Message(
            role=MessageRole.USER,
            content="你好"
        )
        
        assert message.role==MessageRole.USER
        assert message.content=="你好"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata=={}
    
    def test_message_to_dict(self):
        """测试消息序列化"""
        message = Message(
            role=MessageRole.ASSISTANT,
            content="你好！",
            metadata={"model": "gpt-4"}
        )
        
        data = message.to_dict()
        
        assert data["role"]=="assistant"
        assert data["content"]=="你好！"
        assert "timestamp" in data
        assert data["metadata"]=={"model": "gpt-4"}
    
    def test_message_from_dict(self):
        """测试消息反序列化"""
        data = {
            "role": "user",
            "content": "你好",
            "timestamp": "2024-01-01T12:00:00",
            "metadata": {"source": "test"}
        }
        
        message = Message.from_dict(data)
        
        assert message.role==MessageRole.USER
        assert message.content=="你好"
        assert message.metadata=={"source": "test"}


class TestConversationContext:
    """对话上下文测试"""
    
    def test_context_creation(self):
        """测试上下文创建"""
        context = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        assert context.user_id=="user123"
        assert context.session_id=="session456"
        assert context.messages==[]
        assert context.status==SessionStatus.ACTIVE
        assert isinstance(context.created_at, datetime)
        assert isinstance(context.last_activity, datetime)
    
    def test_add_message(self):
        """测试添加消息"""
        context = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        message = Message(MessageRole.USER, "你好")
        old_activity = context.last_activity
        
        context.add_message(message)
        
        assert len(context.messages)==1
        assert context.messages[0]==message
        assert context.last_activity > old_activity
    
    @patch('laoke_service.core.agent.get_config')
    def test_message_history_limit(self, mock_get_config):
        """测试消息历史限制"""
        # 模拟配置
        mock_config = Mock()
        mock_config.agent.conversation.max_history_turns = 3
        mock_get_config.return_value = mock_config
        
        context = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        # 添加系统消息
        system_msg = Message(MessageRole.SYSTEM, "你是老克")
        context.add_message(system_msg)
        
        # 添加超过限制的消息
        for i in range(5):
            context.add_message(Message(MessageRole.USER, f"消息{i}"))
            context.add_message(Message(MessageRole.ASSISTANT, f"回复{i}"))
        
        # 系统消息应该保留，只保留最近的3条对话
        assert len(context.messages)==4  # 1个系统 + 3条最近消息
        assert context.messages[0].role==MessageRole.SYSTEM
        assert "消息4" in context.messages[-2].content
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        context = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        context.add_message(Message(MessageRole.USER, "你好"))
        context.add_message(Message(MessageRole.ASSISTANT, "你好！"))
        
        history = context.get_conversation_history()
        
        assert len(history)==2
        assert history[0]=={"role": "user", "content": "你好"}
        assert history[1]=={"role": "assistant", "content": "你好！"}
    
    def test_is_expired(self):
        """测试会话过期检查"""
        context = ConversationContext(
            user_id="user123",
            session_id="session456"
        )
        
        # 新创建的会话不应该过期
        assert not context.is_expired(3600)
        
        # 模拟过期
        context.last_activity = datetime.now() - timedelta(seconds=3700)
        assert context.is_expired(3600)


class TestOpenAIClient:
    """
OpenAI客户端测试"""
    
    def test_client_creation(self):
        """测试客户端创建"""
        client = OpenAIClient(
            api_key="test-key",
            base_url="https://api.openai.com/v1"
        )
        
        assert client.api_key=="test-key"
        assert client.base_url=="https://api.openai.com/v1"
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_generate_response_success(self, mock_openai):
        """测试成功生成响应"""
        # 模拟 OpenAI 响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "你好！"
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        client = OpenAIClient("test-key")
        
        messages = [{"role": "user", "content": "你好"}]
        content, metadata = await client.generate_response(messages)
        
        assert content=="你好！"
        assert metadata["model"]=="gpt-4o-mini"
        assert metadata["usage"]["total_tokens"]==15
        assert "duration_ms" in metadata
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    async def test_generate_response_error(self, mock_openai):
        """测试生成响应错误"""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        client = OpenAIClient("test-key")
        
        messages = [{"role": "user", "content": "你好"}]
        
        with pytest.raises(AIModelException):
            await client.generate_response(messages)


class TestLaokeAgent:
    """老克智能体测试"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置"""
        config = AgentConfig(
            models=ModelsConfig(
                primary_model="gpt-4o-mini",
                api_key="test-key",
                base_url="https://api.openai.com/v1",
                temperature=0.7,
                max_tokens=4096
            ),
            conversation=ConversationConfig(
                system_prompt="你是老克",
                max_history_turns=10,
                max_tokens_per_message=4096
            ),
            max_concurrent_sessions=100,
            session_timeout=3600,
            cleanup_interval=300
        )
        return config
    
    @pytest.fixture
    def agent(self, mock_config):
        """创建测试智能体实例"""
        return LaokeAgent(mock_config)
    
    @pytest.mark.asyncio
    async def test_create_session(self, agent):
        """测试创建会话"""
        session_id = await agent.create_session("user123")
        
        assert session_id is not None
        assert session_id in agent.sessions
        
        context = agent.sessions[session_id]
        assert context.user_id=="user123"
        assert context.status==SessionStatus.ACTIVE
        assert len(context.messages)==1  # 系统消息
        assert context.messages[0].role==MessageRole.SYSTEM
    
    @pytest.mark.asyncio
    async def test_get_session(self, agent):
        """测试获取会话"""
        session_id = await agent.create_session("user123")
        
        context = await agent.get_session(session_id)
        
        assert context.session_id==session_id
        assert context.user_id=="user123"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, agent):
        """测试获取不存在的会话"""
        with pytest.raises(SessionException) as exc_info:
            await agent.get_session("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_terminate_session(self, agent):
        """测试终止会话"""
        session_id = await agent.create_session("user123")
        
        await agent.terminate_session(session_id)
        
        assert session_id not in agent.sessions
    
    @pytest.mark.asyncio
    async def test_validate_message(self, agent):
        """测试消息验证"""
        # 空消息
        with pytest.raises(ValidationException):
            agent._validate_message("")
        
        with pytest.raises(ValidationException):
            agent._validate_message("   ")
        
        # 过长消息
        long_message = "a" * 5000
        with pytest.raises(ValidationException):
            agent._validate_message(long_message)
        
        # 正常消息
        agent._validate_message("你好")  # 不应该抛出异常
    
    @pytest.mark.asyncio
    @patch.object(OpenAIClient, 'generate_response')
    async def test_chat_success(self, mock_generate, agent):
        """测试成功对话"""
        # 模拟AI响应
        mock_generate.return_value = (
            "你好！我是老克。",
            {"model": "gpt-4o-mini", "usage": {"total_tokens": 20}}
        )
        
        session_id = await agent.create_session("user123")
        
        response = await agent.chat(session_id, "你好")
        
        assert response=="你好！我是老克。"
        
        # 检查会话历史
        context = await agent.get_session(session_id)
        assert len(context.messages)==3  # 系统 + 用户 + 助手
        assert context.messages[1].role==MessageRole.USER
        assert context.messages[1].content=="你好"
        assert context.messages[2].role==MessageRole.ASSISTANT
        assert context.messages[2].content=="你好！我是老克。"
    
    @pytest.mark.asyncio
    async def test_get_session_info(self, agent):
        """测试获取会话信息"""
        session_id = await agent.create_session("user123", {"source": "test"})
        
        info = await agent.get_session_info(session_id)
        
        assert info["session_id"]==session_id
        assert info["user_id"]=="user123"
        assert info["status"]=="active"
        assert info["message_count"]==1
        assert info["metadata"]=={"source": "test"}
        assert "created_at" in info
        assert "last_activity" in info
    
    @pytest.mark.asyncio
    async def test_get_conversation_history(self, agent):
        """测试获取对话历史"""
        session_id = await agent.create_session("user123")
        
        # 模拟添加一些消息
        context = await agent.get_session(session_id)
        context.add_message(Message(MessageRole.USER, "你好"))
        context.add_message(Message(MessageRole.ASSISTANT, "你好！"))
        
        history = await agent.get_conversation_history(session_id)
        
        assert len(history)==3  # 系统 + 用户 + 助手
        assert history[0]["role"]=="system"
        assert history[1]["role"]=="user"
        assert history[2]["role"]=="assistant"
        
        # 测试限制
        limited_history = await agent.get_conversation_history(session_id, limit=2)
        assert len(limited_history)==2
    
    def test_get_stats(self, agent):
        """测试获取统计信息"""
        stats = agent.get_stats()
        
        assert "total_sessions" in stats
        assert "active_sessions" in stats
        assert "max_concurrent_sessions" in stats
        assert "session_timeout" in stats
        assert "cleanup_interval" in stats
        
        assert stats["total_sessions"]==0
        assert stats["active_sessions"]==0
    
    @pytest.mark.asyncio
    async def test_max_concurrent_sessions(self, agent):
        """测试最大并发会话限制"""
        # 修改配置为小值以便测试
        agent.config.max_concurrent_sessions = 2
        
        # 创建两个会话
        session1 = await agent.create_session("user1")
        session2 = await agent.create_session("user2")
        
        # 第三个会话应该失败
        with pytest.raises(SessionException) as exc_info:
            await agent.create_session("user3")
        
        assert "exceeded" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_session_expiry(self, agent):
        """测试会话过期"""
        session_id = await agent.create_session("user123")
        
        # 模拟会话过期
        context = agent.sessions[session_id]
        context.last_activity = datetime.now() - timedelta(seconds=3700)
        
        # 获取过期会话应该失败
        with pytest.raises(SessionException) as exc_info:
            await agent.get_session(session_id)
        
        assert "expired" in str(exc_info.value)
        assert session_id not in agent.sessions
    
    @pytest.mark.asyncio
    async def test_shutdown(self, agent):
        """测试关闭智能体"""
        # 创建一些会话
        session1 = await agent.create_session("user1")
        session2 = await agent.create_session("user2")
        
        assert len(agent.sessions)==2
        
        await agent.shutdown()
        
        # 所有会话应该被清理
        assert len(agent.sessions)==0


class TestGlobalFunctions:
    """全局函数测试"""
    
    @pytest.mark.asyncio
    async def test_get_agent_singleton(self):
        """测试全局智能体单例"""
        # 清理全局实例
        await shutdown_agent()
        
        agent1 = get_agent()
        agent2 = get_agent()
        
        # 应该是同一个实例
        assert agent1 is agent2
        
        await shutdown_agent()
    
    @pytest.mark.asyncio
    async def test_shutdown_agent(self):
        """测试关闭全局智能体"""
        agent = get_agent()
        session_id = await agent.create_session("user123")
        
        assert len(agent.sessions)==1
        
        await shutdown_agent()
        
        # 新的智能体实例应该没有会话
        new_agent = get_agent()
        assert len(new_agent.sessions)==0
        
        await shutdown_agent()


if __name__=="__main__":
    pytest.main([__file__])
