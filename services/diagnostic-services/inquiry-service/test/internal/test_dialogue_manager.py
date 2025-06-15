#!/usr/bin/env python
"""
对话管理器单元测试
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from internal.dialogue.dialogue_manager import DialogueManager
from internal.models.session_models import InquirySession, SessionMessage


class TestDialogueManager:
    """对话管理器测试类"""

    @pytest.fixture
    def config(self) -> dict[str, Any]:
        """测试配置"""
        return {
            "dialogue": {
                "max_session_duration": 3600,
                "max_messages_per_session": 100,
                "welcome_message": "欢迎使用索克生活健康问诊服务",
                "session_timeout": 1800,
            },
            "llm": {
                "model": "test-model",
                "max_tokens": 1000,
                "temperature": 0.7,
            },
        }

    @pytest.fixture
    def mock_session_repo(self) -> AsyncMock:
        """模拟会话存储库"""
        repo = AsyncMock()

        # 模拟创建会话
        repo.create_session.return_value = InquirySession(
            session_id="test-session-123",
            user_id="test-user-456",
            status="active",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        # 模拟获取会话
        repo.get_session.return_value = InquirySession(
            session_id="test-session-123",
            user_id="test-user-456",
            status="active",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        # 模拟添加消息
        repo.add_message.return_value = SessionMessage(
            message_id="msg-123",
            session_id="test-session-123",
            role="user",
            content="我感觉头痛",
            timestamp="2024-01-01T00:01:00Z",
        )

        # 模拟更新会话状态
        repo.update_session_status.return_value = True

        # 模拟保存会话总结
        repo.save_session_summary.return_value = True

        # 模拟获取会话消息
        repo.get_session_messages.return_value = [
            SessionMessage(
                message_id="msg-123",
                session_id="test-session-123",
                role="user",
                content="我感觉头痛",
                timestamp="2024-01-01T00:01:00Z",
            )
        ]

        return repo

    @pytest.fixture
    def mock_user_repo(self) -> AsyncMock:
        """模拟用户存储库"""
        repo = AsyncMock()

        # 模拟获取用户信息
        repo.get_user.return_value = {
            "user_id": "test-user-456",
            "name": "测试用户",
            "age": 30,
            "gender": "male",
            "medical_history": [],
        }

        # 模拟更新用户信息
        repo.update_user.return_value = True

        # 模拟获取用户历史会话
        repo.get_user_sessions.return_value = []

        return repo

    @pytest.fixture
    def mock_llm_client(self) -> AsyncMock:
        """模拟LLM客户端"""
        client = AsyncMock()

        # 模拟生成响应
        client.generate_response.return_value = {
            "content": "根据您描述的头痛症状，我需要了解更多信息。请问您的头痛是什么时候开始的？",
            "suggestions": [
                "头痛的具体位置在哪里？",
                "头痛的性质是胀痛、刺痛还是其他？",
                "是否伴有其他症状？",
            ],
        }

        # 模拟流式响应
        async def mock_stream_response(*args, **kwargs):
            responses = [
                {"content": "根据您描述的", "is_complete": False},
                {"content": "头痛症状，我需要", "is_complete": False},
                {"content": "了解更多信息", "is_complete": True},
            ]
            for response in responses:
                yield response

        client.stream_response.return_value = mock_stream_response()

        # 模拟生成总结
        client.generate_summary.return_value = {
            "summary": "用户主诉头痛，需要进一步了解症状详情",
            "key_symptoms": ["头痛"],
            "recommendations": ["建议详细询问头痛的性质、位置和伴随症状"],
        }

        return client

    @pytest.fixture
    def dialogue_manager(
        self, config, mock_session_repo, mock_user_repo, mock_llm_client
    ) -> DialogueManager:
        """创建对话管理器实例"""
        return DialogueManager(
            config=config,
            session_repository=mock_session_repo,
            user_repository=mock_user_repo,
            llm_client=mock_llm_client,
        )

    @pytest.mark.asyncio
    async def test_start_session(self, dialogue_manager, mock_session_repo):
        """测试开始会话"""
        # 执行测试
        result = await dialogue_manager.start_session("test-user-456")

        # 验证结果
        assert result["session_id"] == "test-session-123"
        assert result["status"] == "active"
        assert "welcome_message" in result
        assert "suggested_questions" in result

        # 验证调用
        mock_session_repo.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_user_input(self, dialogue_manager, mock_session_repo, mock_llm_client):
        """测试处理用户输入"""
        # 执行测试
        result = await dialogue_manager.process_user_input(
            session_id="test-session-123",
            user_input="我感觉头痛"
        )

        # 验证结果
        assert result["response"]["content"] is not None
        assert "suggestions" in result["response"]
        assert result["session_id"] == "test-session-123"

        # 验证调用
        mock_session_repo.add_message.assert_called()
        mock_llm_client.generate_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_end_session(self, dialogue_manager, mock_session_repo, mock_llm_client):
        """测试结束会话"""
        # 执行测试
        result = await dialogue_manager.end_session("test-session-123")

        # 验证结果
        assert result["session_id"] == "test-session-123"
        assert result["status"] == "completed"
        assert "summary" in result

        # 验证调用
        mock_session_repo.update_session_status.assert_called_with(
            "test-session-123", "completed"
        )
        mock_session_repo.save_session_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_history(self, dialogue_manager, mock_session_repo):
        """测试获取会话历史"""
        # 执行测试
        result = await dialogue_manager.get_session_history("test-session-123")

        # 验证结果
        assert result["session_id"] == "test-session-123"
        assert "messages" in result
        assert len(result["messages"]) > 0

        # 验证调用
        mock_session_repo.get_session_messages.assert_called_once_with("test-session-123")

    @pytest.mark.asyncio
    async def test_session_not_found(self, dialogue_manager, mock_session_repo):
        """测试会话不存在的情况"""
        # 设置模拟返回None
        mock_session_repo.get_session.return_value = None

        # 执行测试并验证异常
        with pytest.raises(ValueError, match="Session not found"):
            await dialogue_manager.process_user_input(
                session_id="non-existent-session",
                user_input="测试输入"
            )


# 引入json用于LLM模拟响应

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
