"""
test_agent_manager - 索克生活项目模块
"""

from internal.agent.agent_manager import AgentManager
from unittest.mock import AsyncMock, patch
import asyncio
import pytest
import uuid

#!/usr/bin/env python

"""
老克智能体管理器单元测试
"""





class TestAgentManager:
    """老克智能体管理器测试类"""

    @pytest.fixture
    def session_repository_mock(self):
        """创建会话存储库mock"""
        repository = AsyncMock()
        repository.find_by_id = AsyncMock(return_value=None)
        repository.save = AsyncMock(return_value=None)
        return repository

    @pytest.fixture
    def knowledge_repository_mock(self):
        """创建知识库存储库mock"""
        repository = AsyncMock()
        repository.search = AsyncMock(return_value=[])
        repository.find_by_id = AsyncMock(return_value=None)
        return repository

    @pytest.fixture
    def model_factory_mock(self):
        """创建模型工厂mock"""
        factory = AsyncMock()
        factory.generate_chat_completion = AsyncMock(
            return_value=("模拟的智能体回复内容", {"model": "gpt-4o-mini", "confidence": 0.95})
        )
        return factory

    @pytest.fixture
    def agent_manager(self, session_repository_mock, knowledge_repository_mock, model_factory_mock):
        """创建智能体管理器实例"""
        with patch('internal.agent.agent_manager.ModelFactory', return_value=model_factory_mock):
            manager = AgentManager(
                session_repository=session_repository_mock,
                knowledge_repository=knowledge_repository_mock
            )
            yield manager
            asyncio.run(manager.close())

    @pytest.mark.asyncio
    async     @cache(timeout=300)  # 5分钟缓存
def test_process_knowledge_query(self, agent_manager, model_factory_mock):
        """测试知识查询处理"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "knowledge_query",
            "query": "中医五诊是什么？",
            "knowledge_type": "theory"
        }

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is True
        assert "answer" in result
        assert result["query"] == "中医五诊是什么？"
        assert result["metadata"]["session_id"] == session_id

        # 验证模型调用
        model_factory_mock.generate_chat_completion.assert_called_once()
        call_args = model_factory_mock.generate_chat_completion.call_args[1]
        assert call_args["model"] == agent_manager.primary_model
        assert any("五诊" in msg["content"] for msg in call_args["messages"] if msg["role"] == "user")

    @pytest.mark.asyncio
    async def test_generate_educational_content(self, agent_manager, model_factory_mock):
        """测试教育内容生成"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "content_creation",
            "topic": "太极拳基础入门",
            "content_type": "course",
            "target_audience": "beginner"
        }

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is True
        assert "content" in result
        assert result["topic"] == "太极拳基础入门"
        assert result["metadata"]["session_id"] == session_id

        # 验证模型调用
        model_factory_mock.generate_chat_completion.assert_called_once()
        call_args = model_factory_mock.generate_chat_completion.call_args[1]
        assert call_args["temperature"] == 0.7  # 创造性内容生成应使用较高温度
        assert any("太极拳" in msg["content"] for msg in call_args["messages"] if msg["role"] == "user")

    @pytest.mark.asyncio
    async def test_handle_community_request(self, agent_manager, model_factory_mock):
        """测试社群管理请求处理"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "community_management",
            "action": "advice",
            "issue": "如何提高社区参与度？",
            "context": {"current_users": 100, "active_users": 30}
        }

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is True
        assert "suggestion" in result
        assert result["action"] == "advice"
        assert result["metadata"]["session_id"] == session_id

        # 验证模型调用
        model_factory_mock.generate_chat_completion.assert_called_once()
        call_args = model_factory_mock.generate_chat_completion.call_args[1]
        assert any("社群" in msg["content"] for msg in call_args["messages"] if msg["role"] == "user")

    @pytest.mark.asyncio
    async def test_create_learning_path(self, agent_manager, model_factory_mock):
        """测试学习路径创建"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "learning_path",
            "goal": "学习中医基础理论",
            "current_level": "beginner",
            "interests": ["经络", "中药"],
            "time_commitment": "medium"
        }

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is True
        assert "learning_path" in result
        assert result["goal"] == "学习中医基础理论"
        assert result["metadata"]["session_id"] == session_id

        # 验证模型调用
        model_factory_mock.generate_chat_completion.assert_called_once()
        call_args = model_factory_mock.generate_chat_completion.call_args[1]
        assert any("学习路径" in msg["content"] for msg in call_args["messages"] if msg["role"] == "user")
        assert any("经络" in msg["content"] for msg in call_args["messages"] if msg["role"] == "user")

    @pytest.mark.asyncio
    async def test_process_general_inquiry(self, agent_manager, model_factory_mock):
        """测试一般性咨询处理"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "general",
            "message": "索克生活APP有哪些特色功能？"
        }

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is True
        assert "message" in result
        assert result["metadata"]["session_id"] == session_id

        # 验证模型调用
        model_factory_mock.generate_chat_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, agent_manager, model_factory_mock):
        """测试错误处理"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        request_data = {
            "type": "knowledge_query",
            "query": "中医五诊是什么？"
        }

        # 模拟异常
        model_factory_mock.generate_chat_completion.side_effect = Exception("模型调用失败")

        # 执行测试
        result = await agent_manager.process_request(user_id, request_data, session_id)

        # 验证结果
        assert result["success"] is False
        assert "error" in result
        assert "message" in result
        assert result["metadata"]["session_id"] == session_id
