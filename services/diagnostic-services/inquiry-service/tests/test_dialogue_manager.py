"""
对话管理器测试
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from internal.dialogue.dialogue_manager import DialogueManager
from internal.llm.llm_client import LLMClient
from internal.repository.session_repository import SessionRepository


@pytest.fixture
def mock_config():
    """模拟配置"""
    return {
        "dialogue": {
            "max_session_duration_minutes": 30,
            "max_messages_per_session": 100,
            "session_timeout_minutes": 5,
            "welcome_message": "您好！我是您的健康顾问，请问有什么可以帮助您的？",
            "default_suggestions": [
                "描述您的症状",
                "了解体质调理",
                "咨询健康建议",
                "预防保健知识"
            ]
        },
        "llm": {
            "use_mock_mode": True,
            "temperature": 0.7,
            "max_tokens": 1024
        },
        "database": {
            "url": "sqlite+aiosqlite:///:memory:"
        },
        "cache": {
            "enabled": False
        }
    }


@pytest.fixture
async def mock_llm_client():
    """模拟LLM客户端"""
    client = AsyncMock(spec=LLMClient)
    client.generate_response.return_value = {
        "response_text": "我理解您的症状，请详细描述一下。",
        "response_type": "TEXT",
        "detected_symptoms": ["头痛"],
        "follow_up_questions": ["疼痛持续多长时间了？", "疼痛的性质如何？"],
        "confidence": 0.85
    }
    return client


@pytest.fixture
async def mock_session_repository():
    """模拟会话存储库"""
    repo = AsyncMock(spec=SessionRepository)
    repo.create_session.return_value = "test-session-id"
    repo.get_session.return_value = {
        "session_id": "test-session-id",
        "user_id": "test-user",
        "status": "active",
        "created_at": "2024-01-01T00:00:00",
        "metadata": {}
    }
    repo.add_message.return_value = "test-message-id"
    repo.get_session_messages.return_value = []
    return repo


@pytest.fixture
async def dialogue_manager(mock_config, mock_llm_client, mock_session_repository):
    """创建对话管理器实例"""
    manager = DialogueManager(mock_config)
    manager.llm_client = mock_llm_client
    manager.session_repository = mock_session_repository
    return manager


class TestDialogueManager:
    """对话管理器测试类"""

    @pytest.mark.asyncio
    async def test_start_session_success(self, dialogue_manager):
        """测试成功开始会话"""
        request = {
            "user_id": "test-user",
            "agent_id": "xiaoai",
            "user_profile": {"age": 30, "gender": "female"}
        }

        result = await dialogue_manager.start_session(request)

        assert result["success"] is True
        assert "session_id" in result
        assert "welcome_message" in result
        assert "suggested_questions" in result
        assert len(result["suggested_questions"]) > 0

    @pytest.mark.asyncio
    async def test_start_session_missing_user_id(self, dialogue_manager):
        """测试缺少用户ID时开始会话"""
        request = {"agent_id": "xiaoai"}

        result = await dialogue_manager.start_session(request)

        assert result["success"] is False
        assert "error" in result
        assert "用户ID不能为空" in result["error"]

    @pytest.mark.asyncio
    async def test_interact_with_user_success(self, dialogue_manager):
        """测试成功的用户交互"""
        # 先开始会话
        start_request = {
            "user_id": "test-user",
            "agent_id": "xiaoai"
        }
        start_result = await dialogue_manager.start_session(start_request)
        session_id = start_result["session_id"]

        # 进行交互
        interact_request = {
            "session_id": session_id,
            "user_message": "我最近头痛",
            "message_type": "text"
        }

        result = await dialogue_manager.interact_with_user(interact_request)

        assert result["success"] is True
        assert "response" in result
        assert "detected_symptoms" in result
        assert "follow_up_questions" in result

    @pytest.mark.asyncio
    async def test_interact_invalid_session(self, dialogue_manager):
        """测试无效会话ID的交互"""
        dialogue_manager.session_repository.get_session.return_value = None

        request = {
            "session_id": "invalid-session",
            "user_message": "测试消息"
        }

        result = await dialogue_manager.interact_with_user(request)

        assert result["success"] is False
        assert "error" in result
        assert "会话不存在" in result["error"]

    @pytest.mark.asyncio
    async def test_end_session_success(self, dialogue_manager):
        """测试成功结束会话"""
        # 先开始会话
        start_request = {
            "user_id": "test-user",
            "agent_id": "xiaoai"
        }
        start_result = await dialogue_manager.start_session(start_request)
        session_id = start_result["session_id"]

        # 模拟会话消息
        dialogue_manager.session_repository.get_session_messages.return_value = [
            {
                "role": "user",
                "content": "我头痛",
                "timestamp": "2024-01-01T00:00:00"
            },
            {
                "role": "assistant",
                "content": "请详细描述症状",
                "timestamp": "2024-01-01T00:01:00"
            }
        ]

        # 结束会话
        request = {"session_id": session_id}
        result = await dialogue_manager.end_session(request)

        assert result["success"] is True
        assert "session_summary" in result
        assert "extracted_symptoms" in result
        assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_end_session_invalid_session(self, dialogue_manager):
        """测试结束无效会话"""
        dialogue_manager.session_repository.get_session.return_value = None

        request = {"session_id": "invalid-session"}
        result = await dialogue_manager.end_session(request)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_generate_welcome_message(self, dialogue_manager):
        """测试生成欢迎消息"""
        user_profile = {"name": "张三", "age": 30}

        welcome_msg, suggestions = await dialogue_manager._generate_welcome_message(user_profile)

        assert isinstance(welcome_msg, str)
        assert len(welcome_msg) > 0
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    @pytest.mark.asyncio
    async def test_extract_symptoms_from_history(self, dialogue_manager):
        """测试从历史记录提取症状"""
        history = [
            {"role": "user", "content": "我头痛，还有点发烧"},
            {"role": "assistant", "content": "请详细描述"},
            {"role": "user", "content": "胃也有点不舒服"}
        ]

        symptoms = await dialogue_manager._extract_symptoms_from_history(history)

        assert isinstance(symptoms, list)
        # 由于使用模拟客户端，具体症状取决于模拟返回值

    @pytest.mark.asyncio
    async def test_generate_session_summary(self, dialogue_manager):
        """测试生成会话总结"""
        history = [
            {"role": "user", "content": "我头痛"},
            {"role": "assistant", "content": "请详细描述症状"},
            {"role": "user", "content": "持续了两天，很疼"}
        ]

        summary = await dialogue_manager._generate_session_summary(history)

        assert isinstance(summary, str)
        assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_session_timeout_check(self, dialogue_manager):
        """测试会话超时检查"""
        # 模拟超时会话
        from datetime import datetime, timedelta
        old_time = datetime.utcnow() - timedelta(minutes=10)

        dialogue_manager.session_repository.get_session.return_value = {
            "session_id": "test-session",
            "updated_at": old_time.isoformat(),
            "status": "active"
        }

        is_valid = await dialogue_manager._is_session_valid("test-session")

        # 根据配置的超时时间（5分钟），10分钟前的会话应该超时
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_message_limit_check(self, dialogue_manager):
        """测试消息数量限制检查"""
        # 模拟大量消息
        messages = [{"role": "user", "content": f"消息{i}"} for i in range(150)]
        dialogue_manager.session_repository.get_session_messages.return_value = messages

        request = {
            "session_id": "test-session",
            "user_message": "新消息"
        }

        result = await dialogue_manager.interact_with_user(request)

        # 应该因为消息数量超限而失败
        assert result["success"] is False
        assert "消息数量超限" in result["error"]

    @pytest.mark.asyncio
    async def test_llm_client_error_handling(self, dialogue_manager):
        """测试LLM客户端错误处理"""
        # 模拟LLM客户端错误
        dialogue_manager.llm_client.generate_response.side_effect = Exception("LLM服务不可用")

        start_request = {
            "user_id": "test-user",
            "agent_id": "xiaoai"
        }
        start_result = await dialogue_manager.start_session(start_request)
        session_id = start_result["session_id"]

        interact_request = {
            "session_id": session_id,
            "user_message": "测试消息"
        }

        result = await dialogue_manager.interact_with_user(interact_request)

        # 应该有错误处理机制
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, dialogue_manager):
        """测试并发会话处理"""
        # 创建多个并发会话
        tasks = []
        for i in range(5):
            request = {
                "user_id": f"user-{i}",
                "agent_id": "xiaoai"
            }
            tasks.append(dialogue_manager.start_session(request))

        results = await asyncio.gather(*tasks)

        # 所有会话都应该成功创建
        for result in results:
            assert result["success"] is True
            assert "session_id" in result

        # 会话ID应该都不相同
        session_ids = [result["session_id"] for result in results]
        assert len(set(session_ids)) == len(session_ids)

    @pytest.mark.asyncio
    async def test_session_metadata_handling(self, dialogue_manager):
        """测试会话元数据处理"""
        request = {
            "user_id": "test-user",
            "agent_id": "xiaoai",
            "user_profile": {
                "age": 30,
                "gender": "female",
                "constitution": "气虚质"
            },
            "session_config": {
                "language": "zh-CN",
                "mode": "detailed"
            }
        }

        result = await dialogue_manager.start_session(request)

        assert result["success"] is True

        # 验证元数据是否正确传递
        dialogue_manager.session_repository.create_session.assert_called_once()
        call_args = dialogue_manager.session_repository.create_session.call_args[0][0]
        assert "user_profile" in call_args["metadata"]
        assert "session_config" in call_args["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
