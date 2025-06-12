"""老克智能体服务集成测试"""

import asyncio
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock, patch

from fastapi.testclient import TestClient
from httpx import AsyncClient
from laoke_service.api.routes import app
from laoke_service.core.agent import get_agent, shutdown_agent
from laoke_service.integrations.accessibility import (
    AccessibilityFeature,
    AccessibilityProfile,
    TTSRequest,
    TTSResponse,
    get_accessibility_client,
)
import pytest


class TestAPIIntegration:
    """
    API集成测试"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """创建异步测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac

    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "checks" in data

    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "老克智能体服务"
        assert "version" in data
        assert "endpoints" in data

    def test_stats_endpoint(self, client):
        """测试统计信息接口"""
        response = client.get("/stats")

        assert response.status_code == 200
        data = response.json()

        assert "total_sessions" in data
        assert "active_sessions" in data
        assert "max_concurrent_sessions" in data

    @patch("laoke_service.core.agent.get_agent")
    def test_create_session(self, mock_create_session, client):
        """测试创建会话接口"""
        mock_create_session.return_value = "session123"

        # 模拟 get_session_info 返回
        with patch.object(get_agent(), "get_session_info") as mock_get_info:
            mock_get_info.return_value = {
                "session_id": "session123",
                "user_id": "user123",
                "status": "active",
                "created_at": "2024-01-01T12:00:00",
                "last_activity": "2024-01-01T12:00:00",
                "message_count": 1,
                "metadata": {},
            }

            response = client.post(
                "/sessions", json={"user_id": "user123", "metadata": {"source": "test"}}
            )

            assert response.status_code == 200
            data = response.json()

            assert data["session_id"] == "session123"
            assert data["user_id"] == "user123"
            assert data["status"] == "active"

    @patch.object(get_agent(), "get_session_info")
    def test_get_session_info(self, mock_get_info, client):
        """测试获取会话信息接口"""
        mock_get_info.return_value = {
            "session_id": "session123",
            "user_id": "user123",
            "status": "active",
            "created_at": "2024-01-01T12:00:00",
            "last_activity": "2024-01-01T12:00:00",
            "message_count": 1,
            "metadata": {},
        }

        response = client.get("/sessions/session123")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == "session123"
        assert data["user_id"] == "user123"

    @patch.object(get_agent(), "terminate_session")
    def test_terminate_session(self, mock_terminate, client):
        """测试终止会话接口"""
        mock_terminate.return_value = None

        response = client.delete("/sessions/session123")

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "会话已终止"
        assert data["session_id"] == "session123"

    @patch.object(get_agent(), "chat")
    def test_chat_endpoint(self, mock_chat, client):
        """测试对话接口"""
        mock_chat.return_value = "你好！我是老克。"

        response = client.post(
            "/sessions/session123/chat", json={"message": "你好", "stream": False}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["response"] == "你好！我是老克。"
        assert data["session_id"] == "session123"

    @patch.object(get_agent(), "get_conversation_history")
    def test_get_history_endpoint(self, mock_get_history, client):
        """测试获取对话历史接口"""
        mock_get_history.return_value = [
            {
                "role": "user",
                "content": "你好",
                "timestamp": "2024-01-01T12:00:00",
                "metadata": {},
            },
            {
                "role": "assistant",
                "content": "你好！",
                "timestamp": "2024-01-01T12:00:01",
                "metadata": {},
            },
        ]

        response = client.get("/sessions/session123/history")

        assert response.status_code == 200
        data = response.json()

        assert data["session_id"] == "session123"
        assert len(data["messages"]) == 2
        assert data["messages"][0]["role"] == "user"
        assert data["messages"][1]["role"] == "assistant"

    def test_invalid_session_id(self, client):
        """测试无效会话 ID"""
        with patch.object(get_agent(), "get_session_info") as mock_get_info:
            from laoke_service.core.exceptions import SessionException

            mock_get_info.side_effect = SessionException(
                "Session not found", session_id="invalid", error_type="not_found"
            )

            response = client.get("/sessions/invalid")

            assert response.status_code == 404
            data = response.json()

            assert "error_code" in data
            assert "message" in data

    def test_validation_error(self, client):
        """测试验证错误"""
        response = client.post(
            "/sessions",
            json={
                "user_id": "",  # 空用户ID
            },
        )

        assert response.status_code == 422  # FastAPI验证错误


class TestAccessibilityIntegration:
    """无障碍服务集成测试"""

    @pytest.fixture
    def mock_accessibility_client(self):
        """模拟无障碍服务客户端"""
        with patch(
            "laoke_service.integrations.accessibility.get_accessibility_client"
        ) as mock:
            client = Mock()
            mock.return_value = client
            yield client

    @pytest.mark.asyncio
    async def test_text_to_speech_integration(self, mock_accessibility_client):
        """测试文本转语音集成"""
        # 模拟TTS响应
        mock_response = TTSResponse(
            audio_url="https://example.com/audio.mp3",
            duration_seconds=5.2,
            metadata={"voice": "female_standard"},
        )
        mock_accessibility_client.text_to_speech.return_value = mock_response

        from laoke_service.integrations.accessibility import (
            TTSSpeed,
            TTSVoice,
            convert_text_to_speech,
        )

        result = await convert_text_to_speech(
            text="你好，欢迎使用老克智能体。",
            voice=TTSVoice.FEMALE_STANDARD,
            speed=TTSSpeed.NORMAL,
        )

        assert result.audio_url == "https://example.com/audio.mp3"
        assert result.duration_seconds == 5.2

        # 验证调用参数
        mock_accessibility_client.text_to_speech.assert_called_once()
        call_args = mock_accessibility_client.text_to_speech.call_args[0][0]
        assert call_args.text == "你好，欢迎使用老克智能体。"
        assert call_args.voice == TTSVoice.FEMALE_STANDARD

    @pytest.mark.asyncio
    async def test_user_accessibility_profile(self, mock_accessibility_client):
        """测试用户无障碍配置"""
        # 模拟用户配置
        mock_profile = AccessibilityProfile(
            user_id="user123",
            enabled_features=[
                AccessibilityFeature.TEXT_TO_SPEECH,
                AccessibilityFeature.LARGE_TEXT,
            ],
            tts_preferences={
                "voice": "female_warm",
                "speed": "slow",
                "language": "zh-CN",
            },
        )
        mock_accessibility_client.get_user_profile.return_value = mock_profile

        # 模拟TTS响应
        mock_tts_response = TTSResponse(
            audio_url="https://example.com/user_audio.mp3", duration_seconds=8.5
        )
        mock_accessibility_client.text_to_speech.return_value = mock_tts_response

        # 模拟响应转换
        mock_accessibility_client.convert_response_for_user.return_value = {
            "text": "你好！我是老克。",
            "audio_url": "https://example.com/user_audio.mp3",
            "audio_duration": 8.5,
            "large_text": True,
            "accessibility_features": ["text_to_speech", "large_text"],
        }

        from laoke_service.integrations.accessibility import get_accessible_response

        result = await get_accessible_response(
            user_id="user123", text_response="你好！我是老克。"
        )

        assert result["text"] == "你好！我是老克。"
        assert result["audio_url"] == "https://example.com/user_audio.mp3"
        assert result["large_text"] is True
        assert "text_to_speech" in result["accessibility_features"]
        assert "large_text" in result["accessibility_features"]

    @pytest.mark.asyncio
    async def test_accessibility_service_disabled(self):
        """测试无障碍服务禁用"""
        with patch(
            "laoke_service.integrations.accessibility.get_config"
        ) as mock_config:
            # 模拟服务禁用
            config = Mock()
            config.external_services.accessibility_service_enabled = False
            mock_config.return_value = config

            from laoke_service.core.exceptions import AccessibilityServiceException
            from laoke_service.integrations.accessibility import AccessibilityClient

            client = AccessibilityClient()

            with pytest.raises(AccessibilityServiceException) as exc_info:
                await client._make_request("GET", "/health")

            assert "disabled" in str(exc_info.value)


class TestEndToEndWorkflow:
    """端到端工作流测试"""

    @pytest.fixture
    async def setup_agent(self):
        """设置测试智能体"""
        # 清理现有实例
        await shutdown_agent()

        # 模拟AI响应
        with patch(
            "laoke_service.core.agent.OpenAIClient.generate_response"
        ) as mock_generate:
            mock_generate.return_value = (
                "你好！我是老克，一个专注于中医知识传播的智能体。有什么可以帮助您的吗？",
                {
                    "model": "gpt-4o-mini",
                    "usage": {
                        "prompt_tokens": 15,
                        "completion_tokens": 25,
                        "total_tokens": 40,
                    },
                    "duration_ms": 1200,
                },
            )

            yield get_agent()

        # 清理
        await shutdown_agent()

    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self, setup_agent):
        """测试完整的对话流程"""
        agent = setup_agent

        # 1. 创建会话
        session_id = await agent.create_session(
            user_id="test_user", metadata={"source": "integration_test"}
        )

        assert session_id is not None

        # 2. 检查会话信息
        session_info = await agent.get_session_info(session_id)
        assert session_info["user_id"] == "test_user"
        assert session_info["status"] == "active"
        assert session_info["message_count"] == 1  # 系统消息

        # 3. 进行对话
        response = await agent.chat(session_id, "你好，请介绍一下你自己")

        assert "老克" in response
        assert "中医" in response

        # 4. 检查对话历史
        history = await agent.get_conversation_history(session_id)
        assert len(history) == 3  # 系统 + 用户 + 助手

        user_message = next(msg for msg in history if msg["role"] == "user")
        assistant_message = next(msg for msg in history if msg["role"] == "assistant")

        assert user_message["content"] == "你好，请介绍一下你自己"
        assert assistant_message["content"] == response

        # 5. 获取统计信息
        stats = agent.get_stats()
        assert stats["total_sessions"] == 1
        assert stats["active_sessions"] == 1

        # 6. 终止会话
        await agent.terminate_session(session_id)

        # 7. 验证会话已终止
        from laoke_service.core.exceptions import SessionException

        with pytest.raises(SessionException):
            await agent.get_session(session_id)

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(self, setup_agent):
        """测试多个并发会话"""
        agent = setup_agent

        # 创建多个会话
        sessions = []
        for i in range(3):
            session_id = await agent.create_session(f"user_{i}")
            sessions.append(session_id)

        # 并发对话
        tasks = []
        for i, session_id in enumerate(sessions):
            task = agent.chat(session_id, f"你好，我是用户{i}")
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # 验证所有响应
        for response in responses:
            assert "老克" in response

        # 验证统计信息
        stats = agent.get_stats()
        assert stats["total_sessions"] == 3
        assert stats["active_sessions"] == 3

        # 清理所有会话
        for session_id in sessions:
            await agent.terminate_session(session_id)

    @pytest.mark.asyncio
    async def test_session_timeout_handling(self, setup_agent):
        """测试会话超时处理"""
        agent = setup_agent

        # 修改超时配置为小值
        agent.config.session_timeout = 1  # 1秒

        session_id = await agent.create_session("test_user")

        # 等待超时
        await asyncio.sleep(1.5)

        # 手动触发清理
        await agent._cleanup_expired_sessions()

        # 验证会话已过期
        from laoke_service.core.exceptions import SessionException

        with pytest.raises(SessionException) as exc_info:
            await agent.get_session(session_id)

        assert "expired" in str(exc_info.value)


class TestErrorHandling:
    """错误处理测试"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_api_error_handling(self, client):
        """测试API错误处理"""
        # 模拟内部错误
        with patch.object(get_agent(), "get_session_info") as mock_get_info:
            mock_get_info.side_effect = Exception("Internal error")

            response = client.get("/sessions/test")

            assert response.status_code == 500
            data = response.json()

            assert "error_code" in data
            assert "message" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_ai_model_error_handling(self):
        """测试AI模型错误处理"""
        with patch(
            "laoke_service.core.agent.OpenAIClient.generate_response"
        ) as mock_generate:
            from laoke_service.core.exceptions import AIModelException

            mock_generate.side_effect = AIModelException(
                "API quota exceeded", model="gpt-4o-mini", error_type="quota"
            )

            agent = get_agent()
            session_id = await agent.create_session("test_user")

            with pytest.raises(AIModelException) as exc_info:
                await agent.chat(session_id, "你好")

            assert "quota" in str(exc_info.value)

            await shutdown_agent()

    def test_validation_error_handling(self, client):
        """测试验证错误处理"""
        # 空消息
        response = client.post(
            "/sessions/test/chat", json={"message": "", "stream": False}
        )

        assert response.status_code == 422  # FastAPI验证错误

        # 过长消息
        long_message = "a" * 5000
        response = client.post(
            "/sessions/test/chat", json={"message": long_message, "stream": False}
        )

        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
