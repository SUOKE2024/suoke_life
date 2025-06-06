"""
test_dialogue_manager - 索克生活项目模块
"""

from internal.dialogue.dialogue_manager import DialogueManager
from internal.llm.llm_client import LLMClient
from internal.repository.session_repository import SessionRepository
from internal.repository.user_repository import UserRepository
from unittest.mock import AsyncMock
import json
import pytest
import time

#!/usr/bin/env python

"""
对话管理器测试
"""





class TestDialogueManager:
    """对话管理器测试类"""

    @pytest.fixture
    def config(self):
        """测试配置"""
        return {
            "dialogue": {
                "session_timeout_seconds": 1800,  # 30分钟
                "default_language": "zh-CN",
                "max_history_messages": 20,
                "max_tokens_per_message": 1000,
            },
            "llm": {"use_mock_mode": True, "model_type": "test", "timeout_seconds": 10},
        }

    @pytest.fixture
    def mock_session_repo(self):
        """模拟会话存储库"""
        repo = AsyncMock()

        # 模拟创建会话
        async def create_session(session_data):
            return {
                "session_id": session_data.get("session_id"),
                "user_id": session_data.get("user_id"),
                "session_type": session_data.get("session_type"),
                "language": session_data.get("language"),
                "created_at": int(time.time()),
                "last_interaction": int(time.time()),
                "messages": [],
            }

        repo.create_session.side_effect = create_session

        # 模拟获取会话
        async def get_session(session_id):
            if session_id == "invalid_session":
                return None
            return {
                "id": session_id,  # 修复：使用id而不是session_id
                "session_id": session_id,
                "user_id": "test_user",
                "type": "general",  # 修复：使用type而不是session_type
                "session_type": "general",
                "language": "zh-CN",
                "created_at": int(time.time()) - 600,  # 10分钟前创建
                "last_interaction": int(time.time()) - 60,  # 1分钟前交互
                "history": [  # 修复：使用history而不是messages
                    {"role": "system", "content": "你是一位专业的中医问诊助手"},
                    {
                        "role": "assistant",
                        "content": "您好，我是您的中医问诊助手，请问有什么可以帮助您的?",
                    },
                ],
                "messages": [
                    {"role": "system", "content": "你是一位专业的中医问诊助手"},
                    {
                        "role": "assistant",
                        "content": "您好，我是您的中医问诊助手，请问有什么可以帮助您的?",
                    },
                ],
            }

        repo.get_session_by_id.side_effect = get_session

        # 模拟添加消息
        async def add_message(session_id, role, content):
            return True

        repo.add_message.side_effect = add_message

        # 模拟结束会话
        async def end_session(session_id, summary=None):
            return {
                "session_id": session_id,
                "user_id": "test_user",
                "session_duration": 600,  # 10分钟
                "session_end_time": int(time.time()),
            }

        repo.end_session.side_effect = end_session

        # 模拟更新会话
        async def update_session(session_id, session_data):
            return True

        repo.update_session.side_effect = update_session

        # 模拟更新会话状态
        async def update_session_status(session_id, status):
            return True

        repo.update_session_status.side_effect = update_session_status

        return repo

    @pytest.fixture
    def mock_user_repo(self):
        """模拟用户存储库"""
        repo = AsyncMock()

        # 模拟获取用户信息
        async def get_user(user_id):
            return {
                "user_id": user_id,
                "name": "测试用户",
                "age": 30,
                "gender": "male",
                "constitution_type": "BALANCED",
                "medical_history": [],
            }

        repo.get_user_by_id.side_effect = get_user

        return repo

    @pytest.fixture
    def mock_llm_client(self):
        """模拟LLM客户端"""
        client = AsyncMock()

        # 模拟生成响应
        async def generate_response(request):
            # 从请求中获取历史记录
            history = request.get("history", [])
            last_message = ""
            if history:
                last_message = history[-1].get("content", "")
            
            if "问诊开始" in str(last_message):
                return {
                    "response_text": "您好，我是您的中医问诊助手。请问您最近有什么不适吗？",
                    "response_type": "GREETING",
                    "detected_symptoms": [],
                    "follow_up_questions": ["您有什么不适症状吗？"],
                }
            elif "头痛" in str(last_message):
                return {
                    "response_text": "您的头痛是位于太阳穴位置吗？能否描述一下疼痛的性质，比如是钝痛还是刺痛？",
                    "response_type": "FOLLOW_UP_QUESTION",
                    "detected_symptoms": ["头痛"],
                    "follow_up_questions": [
                        "疼痛性质是怎样的？",
                        "是否伴有其他症状？",
                    ],
                }
            else:
                return {
                    "response_text": "感谢您的描述。请问您还有其他症状吗？",
                    "response_type": "INFO_REQUEST",
                    "detected_symptoms": [],
                    "follow_up_questions": ["是否有睡眠障碍？", "饮食习惯如何？"],
                }

        client.generate_response.side_effect = generate_response

        return client

    @pytest.fixture
    def dialogue_manager(
        self, config, mock_session_repo, mock_user_repo, mock_llm_client
    ):
        """创建对话管理器实例"""
        return DialogueManager(
            llm_client=mock_llm_client,
            session_repository=mock_session_repo,
            user_repository=mock_user_repo,
            config=config,
        )

    @pytest.mark.asyncio
    async def test_start_session(
        self, dialogue_manager, mock_session_repo, mock_llm_client
    ):
        """测试开始会话"""
        # 执行测试
        (
            session_id,
            welcome_message,
            suggested_questions,
        ) = await dialogue_manager.start_session(
            user_id="test_user",
            session_type="general",
            language="zh-CN",
            context_data={"key": "value"},
        )

        # 验证结果
        assert isinstance(session_id, str)
        assert isinstance(welcome_message, str)
        assert welcome_message.startswith("您好")
        assert isinstance(suggested_questions, list)

        # 验证调用
        mock_session_repo.create_session.assert_called_once()
        # 注意：欢迎信息生成不需要调用LLM，使用模板即可

    @pytest.mark.asyncio
    async def test_interact_with_valid_session(
        self, dialogue_manager, mock_session_repo, mock_llm_client
    ):
        """测试有效会话的交互"""
        # 执行测试
        result = await dialogue_manager.interact(
            session_id="valid_session",
            user_message="我最近总是头痛，特别是在右侧太阳穴",
            timestamp=int(time.time()),
            attached_data_urls=[],
        )

        # 验证结果
        assert isinstance(result, dict)
        assert "response_text" in result
        assert "detected_symptoms" in result
        assert "头痛" in result["detected_symptoms"]

        # 验证调用
        mock_session_repo.get_session_by_id.assert_called_once_with("valid_session")
        mock_session_repo.update_session.assert_called()
        mock_llm_client.generate_response.assert_called_once()

    @pytest.mark.asyncio
    async def test_interact_with_invalid_session(
        self, dialogue_manager, mock_session_repo
    ):
        """测试无效会话的交互"""
        # 执行测试
        with pytest.raises(ValueError) as exc_info:
            await dialogue_manager.interact(
                session_id="invalid_session",
                user_message="我最近总是头痛",
                timestamp=int(time.time()),
                attached_data_urls=[],
            )

        # 验证异常
        assert "不存在或已过期" in str(exc_info.value)

        # 验证调用
        mock_session_repo.get_session_by_id.assert_called_once_with("invalid_session")

    @pytest.mark.asyncio
    async def test_end_session(self, dialogue_manager, mock_session_repo):
        """测试结束会话"""
        # 执行测试
        result = await dialogue_manager.end_session(
            session_id="valid_session", feedback="很满意这次问诊"
        )

        # 验证结果
        assert isinstance(result, dict)
        assert "session_id" in result
        assert "user_id" in result
        assert "session_duration" in result

        # 验证调用
        mock_session_repo.get_session_by_id.assert_called_once_with("valid_session")
        mock_session_repo.update_session.assert_called()


# 引入json用于LLM模拟响应

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
