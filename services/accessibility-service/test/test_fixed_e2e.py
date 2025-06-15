#!/usr/bin/env python

"""
修复后的端到端测试
"""

from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

# 导入服务组件
from internal.service.coordinators import AccessibilityServiceCoordinator
from internal.service.dependency_injection import DIContainer
from internal.service.factories import AccessibilityServiceFactory


class TestFixedE2E:
    """修复后的端到端测试类"""

    @pytest_asyncio.fixture
    async def fixed_coordinator(self):
        """创建修复后的协调器"""
        # 创建mock依赖
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()

        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()

        mock_config_manager = Mock()
        mock_config_manager.get = Mock(return_value=True)

        # 创建DIContainer并注册依赖
        container = DIContainer()
        container.register(
            "model_manager", type(mock_model_manager), mock_model_manager
        )
        container.register(
            "cache_manager", type(mock_cache_manager), mock_cache_manager
        )
        container.register(
            "config_manager", type(mock_config_manager), mock_config_manager
        )

        # 注册核心服务的mock实现
        from internal.service.implementations.blind_assistance_impl import (
            BlindAssistanceServiceImpl,
        )
        from internal.service.implementations.voice_assistance_impl import (
            VoiceAssistanceServiceImpl,
        )

        # 创建mock服务实例，确保返回正确的字典格式
        mock_blind_service = Mock(spec=BlindAssistanceServiceImpl)
        mock_blind_service.analyze_scene = AsyncMock(
            return_value={
                "user_id": "test_user",
                "timestamp": "2024-01-01T00:00:00Z",
                "scene_type": "outdoor",
                "obstacles": [],
                "navigation_suggestions": ["前方安全"],
                "confidence": 0.9,
            }
        )

        mock_voice_service = Mock(spec=VoiceAssistanceServiceImpl)
        mock_voice_service.process_voice_command = AsyncMock(
            return_value={
                "user_id": "test_user",
                "timestamp": "2024-01-01T00:00:00Z",
                "intent": "navigation_query",
                "response": "前方有一个路口",
                "confidence": 0.9,
            }
        )
        mock_voice_service.text_to_speech = AsyncMock(
            return_value={
                "audio_data": b"fake_audio_data",
                "duration": 2.5,
                "format": "wav",
            }
        )

        # 注册服务
        container.register(
            "blind_assistance",
            BlindAssistanceServiceImpl,
            factory=lambda: mock_blind_service,
        )
        container.register(
            "voice_assistance",
            VoiceAssistanceServiceImpl,
            factory=lambda: mock_voice_service,
        )

        # 创建factory和coordinator
        factory = AccessibilityServiceFactory(container)
        await factory.initialize()

        coordinator = AccessibilityServiceCoordinator(factory)
        await coordinator.initialize()

        return coordinator

    @pytest.mark.asyncio
    async def test_fixed_scene_analysis(self, fixed_coordinator):
        """测试修复后的场景分析"""
        user_id = "test_user"
        image_data = b"fake_camera_image_data"
        location = {"lat": 39.9042, "lng": 116.4074}
        preferences = {
            "detail_level": "detailed",
            "voice_enabled": True,
            "language": "zh-CN",
        }

        # 场景分析
        scene_result = await fixed_coordinator.analyze_scene(
            image_data, user_id, preferences, location
        )

        # 验证结果
        assert scene_result is not None
        assert isinstance(scene_result, dict)
        assert scene_result["user_id"] == user_id
        assert "scene_type" in scene_result
        assert "obstacles" in scene_result
        assert "navigation_suggestions" in scene_result
        assert "coordinator" in scene_result

        print(f"✅ 场景分析成功: {scene_result['scene_type']}")
        print(f"✅ 检测到 {len(scene_result['obstacles'])} 个障碍物")
        print(f"✅ 协调器信息: {scene_result['coordinator']['service']}")

    @pytest.mark.asyncio
    async def test_fixed_voice_processing(self, fixed_coordinator):
        """测试修复后的语音处理"""
        user_id = "test_user"
        audio_data = b"fake_voice_data"
        context = "navigation"
        language = "zh-CN"
        dialect = "standard"

        # 语音处理
        voice_result = await fixed_coordinator.process_voice_command(
            audio_data, user_id, context, language, dialect
        )

        # 验证结果
        assert voice_result is not None
        assert isinstance(voice_result, dict)
        assert voice_result["user_id"] == user_id
        assert "intent" in voice_result
        assert "response" in voice_result
        assert "coordinator" in voice_result

        print(f"✅ 语音处理成功: {voice_result['intent']}")
        print(f"✅ 语音回复: {voice_result['response']}")

    @pytest.mark.asyncio
    async def test_fixed_text_to_speech(self, fixed_coordinator):
        """测试修复后的文本转语音"""
        text = "前方有一个路口，请小心通过"
        language = "zh-CN"
        voice_preferences = {"speed": "normal", "pitch": "medium"}

        # 文本转语音
        tts_result = await fixed_coordinator.text_to_speech(
            text, language, voice_preferences
        )

        # 验证结果
        assert tts_result is not None
        assert isinstance(tts_result, dict)
        assert "audio_data" in tts_result
        assert "duration" in tts_result

        print(f"✅ 文本转语音成功，时长: {tts_result['duration']}秒")

    @pytest.mark.asyncio
    async def test_coordinator_status(self, fixed_coordinator):
        """测试协调器状态"""
        status = await fixed_coordinator.get_status()

        assert status is not None
        assert isinstance(status, dict)
        assert "coordinator" in status
        assert "services" in status
        assert "loaded_services" in status

        coordinator_status = status["coordinator"]
        assert "initialized" in coordinator_status
        assert "error_count" in coordinator_status

        print(
            f"✅ 协调器状态: 初始化={coordinator_status['initialized']}, 错误数={coordinator_status['error_count']}"
        )
        print(f"✅ 已加载服务: {list(status['loaded_services'].keys())}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
