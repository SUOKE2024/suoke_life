#!/usr/bin/env python

"""
端到端测试
测试完整用户场景、API接口和真实数据流
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入服务组件
from internal.service.coordinators import AccessibilityServiceCoordinator
from internal.service.factories import AccessibilityServiceFactory
from internal.service.optimized_accessibility_service import (
    OptimizedAccessibilityService,
)


class TestCompleteUserScenarios:
    """完整用户场景测试类"""

    @pytest_asyncio.fixture
    async def e2e_coordinator(self):
        """创建端到端测试协调器"""
        from internal.service.dependency_injection import DIContainer

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
        from internal.service.implementations.content_conversion_impl import (
            ContentConversionServiceImpl,
        )
        from internal.service.implementations.screen_reading_impl import (
            ScreenReadingServiceImpl,
        )
        from internal.service.implementations.sign_language_impl import (
            SignLanguageServiceImpl,
        )
        from internal.service.implementations.voice_assistance_impl import (
            VoiceAssistanceServiceImpl,
        )

        # 创建mock服务实例
        mock_blind_service = Mock(spec=BlindAssistanceServiceImpl)
        mock_blind_service.analyze_environment = AsyncMock(
            return_value={"obstacles": [], "safe_path": True}
        )
        mock_blind_service.provide_navigation = AsyncMock(
            return_value={"direction": "forward", "distance": 10}
        )

        mock_voice_service = Mock(spec=VoiceAssistanceServiceImpl)
        mock_voice_service.process_voice_command = AsyncMock(
            return_value={"command": "navigate", "confidence": 0.9}
        )

        mock_sign_service = Mock(spec=SignLanguageServiceImpl)
        mock_sign_service.recognize_sign_language = AsyncMock(
            return_value={
                "language": "CSL",
                "semantic": {"sentence": "你好"},
                "recognition": {"confidence": 0.9},
            }
        )

        mock_screen_service = Mock(spec=ScreenReadingServiceImpl)
        mock_screen_service.read_screen = AsyncMock(
            return_value={"ui_elements": [], "reading_content": {"summary": "测试页面"}}
        )

        mock_content_service = Mock(spec=ContentConversionServiceImpl)
        mock_content_service.convert_content = AsyncMock(
            return_value={"converted_content": {"adapted_content": "简化内容"}}
        )
        mock_content_service.simplify_text = AsyncMock(return_value="简化文本")

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
        container.register(
            "sign_language", SignLanguageServiceImpl, factory=lambda: mock_sign_service
        )
        container.register(
            "screen_reading",
            ScreenReadingServiceImpl,
            factory=lambda: mock_screen_service,
        )
        container.register(
            "content_conversion",
            ContentConversionServiceImpl,
            factory=lambda: mock_content_service,
        )

        # 创建factory和coordinator
        factory = AccessibilityServiceFactory(container)
        await factory.initialize()

        coordinator = AccessibilityServiceCoordinator(factory)
        await coordinator.initialize()

        return coordinator

    @pytest.mark.asyncio
    async def test_blind_user_navigation_scenario(self, e2e_coordinator):
        """测试盲人用户导航场景"""
        user_id = "blind_user_001"

        # 场景1: 用户到达新环境，需要场景分析
        print("\n=== 场景1: 环境感知 ===")

        # 模拟用户拍照
        image_data = b"fake_camera_image_data"
        location = {"lat": 39.9042, "lng": 116.4074}  # 天安门广场
        preferences = {
            "detail_level": "detailed",
            "voice_enabled": True,
            "language": "zh-CN",
        }

        # 场景分析
        scene_result = await e2e_coordinator.analyze_scene(
            image_data, user_id, preferences, location
        )

        assert scene_result is not None
        assert scene_result["user_id"] == user_id
        assert "scene_type" in scene_result
        assert "obstacles" in scene_result
        assert "navigation_suggestions" in scene_result

        print(f"场景类型: {scene_result['scene_type']}")
        print(f"检测到 {len(scene_result['obstacles'])} 个障碍物")

        # 场景2: 基于场景分析的语音交互
        print("\n=== 场景2: 语音询问 ===")

        # 用户语音询问："前面有什么？"
        voice_data = b"fake_voice_question_data"
        voice_context = {
            "previous_scene": scene_result["scene_type"],
            "current_location": location,
            "detected_obstacles": scene_result["obstacles"],
        }

        voice_result = (
            await e2e_coordinator._voice_assistance_service.process_voice_command(
                voice_data, "zh-CN", user_id, voice_context
            )
        )

        assert voice_result is not None
        assert voice_result["intent"] is not None
        assert voice_result["response"] is not None

        print(f"识别意图: {voice_result['intent']}")
        print(f"语音回复: {voice_result['response']}")

        # 场景3: 综合辅助 - 场景分析 + 语音输出
        print("\n=== 场景3: 综合辅助 ===")

        comprehensive_request = {
            "type": "scene_analysis_with_voice",
            "image_data": image_data,
            "preferences": preferences,
        }

        comprehensive_result = await e2e_coordinator.comprehensive_assistance(
            comprehensive_request, user_id
        )

        assert comprehensive_result is not None
        assert "scene_analysis" in comprehensive_result
        assert "voice_output" in comprehensive_result
        assert comprehensive_result["coordination_success"] is True

        print("综合辅助完成，包含场景分析和语音输出")

    @pytest.mark.asyncio
    async def test_deaf_user_communication_scenario(self, e2e_coordinator):
        """测试聋人用户交流场景"""
        user_id = "deaf_user_001"

        # 场景1: 手语识别
        print("\n=== 场景1: 手语识别 ===")

        # 模拟用户手语视频
        sign_video_data = b"fake_sign_language_video"
        sign_language = "CSL"  # 中国手语

        sign_result = (
            await e2e_coordinator._sign_language_service.recognize_sign_language(
                sign_video_data, sign_language, user_id
            )
        )

        assert sign_result is not None
        assert sign_result["language"] == sign_language
        assert "semantic" in sign_result
        assert "recognition" in sign_result

        recognized_text = sign_result["semantic"]["sentence"]
        print(f"识别的手语内容: {recognized_text}")

        # 场景2: 内容转换 - 手语转文字转语音
        print("\n=== 场景2: 多模态转换 ===")

        # 将识别的手语转换为简化文本
        simplified_text = (
            await e2e_coordinator._content_conversion_service.simplify_text(
                recognized_text, "easy"
            )
        )

        assert simplified_text is not None
        print(f"简化文本: {simplified_text}")

        # 转换为语音（为听力正常的交流对象）
        voice_output = await e2e_coordinator._voice_assistance_service.text_to_speech(
            simplified_text, "zh-CN", {"speed": "normal"}
        )

        assert voice_output is not None
        assert "audio_data" in voice_output
        print("已生成语音输出")

        # 场景3: 屏幕阅读辅助
        print("\n=== 场景3: 屏幕阅读 ===")

        # 模拟屏幕截图
        screen_data = b"fake_screen_capture"
        reading_preferences = {"reading_mode": "detailed", "include_descriptions": True}

        screen_result = await e2e_coordinator._screen_reading_service.read_screen(
            screen_data, user_id, "mobile_app", reading_preferences
        )

        assert screen_result is not None
        assert "ui_elements" in screen_result
        assert "reading_content" in screen_result

        ui_count = len(screen_result["ui_elements"])
        print(f"识别到 {ui_count} 个UI元素")
        print(f"页面摘要: {screen_result['reading_content']['summary']}")

    @pytest.mark.asyncio
    async def test_elderly_user_assistance_scenario(self, e2e_coordinator):
        """测试老年用户辅助场景"""
        user_id = "elderly_user_001"

        # 场景1: 复杂内容简化
        print("\n=== 场景1: 内容简化 ===")

        complex_text = """
        根据最新的医疗研究报告显示，通过实施个性化的健康管理方案，
        结合先进的生物标志物分析技术和人工智能算法，
        可以有效提升老年人群的生活质量和健康水平。
        该系统采用多模态传感技术进行数据采集，
        并通过机器学习模型进行智能分析和预测。
        """

        # 为老年人适配内容
        adapted_content = (
            await e2e_coordinator._content_conversion_service.convert_content(
                complex_text,
                "content_adaptation",
                {"target_audience": "elderly", "reading_level": "beginner"},
                user_id,
            )
        )

        assert adapted_content is not None
        adapted_text = adapted_content["converted_content"]["adapted_content"]
        print(f"适配后内容: {adapted_text}")

        # 场景2: 语音交互（慢速、清晰）
        print("\n=== 场景2: 语音交互 ===")

        # 将简化内容转为语音
        elderly_voice_options = {
            "speed": "slow",
            "pitch": "low",
            "volume": "high",
            "clarity": "enhanced",
        }

        voice_result = await e2e_coordinator._voice_assistance_service.text_to_speech(
            adapted_text, "zh-CN", elderly_voice_options
        )

        assert voice_result is not None
        assert voice_result["speed"] == "slow"
        print("已生成适合老年人的语音输出")

        # 场景3: 综合健康管理场景
        print("\n=== 场景3: 健康管理 ===")

        health_request = {
            "type": "health_content_processing",
            "content": "您的血压监测结果显示收缩压140mmHg，舒张压90mmHg",
            "conversion_options": {
                "target_audience": "elderly",
                "add_explanations": True,
            },
            "voice_options": elderly_voice_options,
        }

        health_result = await e2e_coordinator.comprehensive_assistance(
            health_request, user_id
        )

        assert health_result is not None
        print("健康信息已处理并转换为适合老年人的格式")

    @pytest.mark.asyncio
    async def test_multilingual_user_scenario(self, e2e_coordinator):
        """测试多语言用户场景"""
        user_id = "multilingual_user_001"

        # 场景1: 中英文混合内容处理
        print("\n=== 场景1: 多语言内容处理 ===")

        mixed_content = (
            "欢迎使用Suoke Life健康管理平台，我们提供AI-powered的个性化服务。"
        )

        # 翻译为英文
        translation_result = (
            await e2e_coordinator._content_conversion_service.convert_content(
                mixed_content,
                "language_translation",
                {"source_language": "zh-CN", "target_language": "en-US"},
                user_id,
            )
        )

        assert translation_result is not None
        translated_text = translation_result["converted_content"]["translated_text"]
        print(f"英文翻译: {translated_text}")

        # 场景2: 多语言语音支持
        print("\n=== 场景2: 多语言语音 ===")

        # 中文语音
        chinese_voice = await e2e_coordinator._voice_assistance_service.text_to_speech(
            mixed_content, "zh-CN", {"speed": "normal"}
        )

        # 英文语音
        english_voice = await e2e_coordinator._voice_assistance_service.text_to_speech(
            translated_text, "en-US", {"speed": "normal"}
        )

        assert chinese_voice is not None
        assert english_voice is not None
        print("已生成中英文双语音频")

        # 场景3: 多语言手语识别
        print("\n=== 场景3: 多语言手语 ===")

        # 测试不同手语语言
        sign_languages = ["ASL", "CSL", "BSL"]

        for lang in sign_languages:
            supported_languages = (
                await e2e_coordinator._sign_language_service.get_supported_languages()
            )

            if lang in supported_languages:
                print(f"支持 {lang} 手语识别")
            else:
                print(f"暂不支持 {lang} 手语识别")


class TestAPICompatibility:
    """API兼容性测试类"""

    @pytest_asyncio.fixture
    async def legacy_service(self):
        """创建原有服务实例（模拟）"""
        # 这里应该是原有的AccessibilityService实例
        # 由于我们没有完整的原有实现，这里用Mock模拟
        mock_service = Mock()

        # 模拟原有API方法
        mock_service.analyze_scene = AsyncMock(
            return_value={"scene_type": "outdoor", "obstacles": [], "confidence": 0.85}
        )

        mock_service.process_voice_command = AsyncMock(
            return_value={"intent": "navigation_query", "response": "前方有一个路口"}
        )

        return mock_service

    @pytest_asyncio.fixture
    async def new_coordinator(self):
        """创建新的协调器"""
        from internal.service.dependency_injection import DIContainer

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
        from internal.service.implementations.content_conversion_impl import (
            ContentConversionServiceImpl,
        )
        from internal.service.implementations.screen_reading_impl import (
            ScreenReadingServiceImpl,
        )
        from internal.service.implementations.sign_language_impl import (
            SignLanguageServiceImpl,
        )
        from internal.service.implementations.voice_assistance_impl import (
            VoiceAssistanceServiceImpl,
        )

        # 创建mock服务实例
        mock_blind_service = Mock(spec=BlindAssistanceServiceImpl)
        mock_blind_service.analyze_environment = AsyncMock(
            return_value={"obstacles": [], "safe_path": True}
        )
        mock_blind_service.provide_navigation = AsyncMock(
            return_value={"direction": "forward", "distance": 10}
        )

        mock_voice_service = Mock(spec=VoiceAssistanceServiceImpl)
        mock_voice_service.process_voice_command = AsyncMock(
            return_value={"command": "navigate", "confidence": 0.9}
        )

        mock_sign_service = Mock(spec=SignLanguageServiceImpl)
        mock_sign_service.recognize_sign_language = AsyncMock(
            return_value={
                "language": "CSL",
                "semantic": {"sentence": "你好"},
                "recognition": {"confidence": 0.9},
            }
        )

        mock_screen_service = Mock(spec=ScreenReadingServiceImpl)
        mock_screen_service.read_screen = AsyncMock(
            return_value={"ui_elements": [], "reading_content": {"summary": "测试页面"}}
        )

        mock_content_service = Mock(spec=ContentConversionServiceImpl)
        mock_content_service.convert_content = AsyncMock(
            return_value={"converted_content": {"adapted_content": "简化内容"}}
        )
        mock_content_service.simplify_text = AsyncMock(return_value="简化文本")

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
        container.register(
            "sign_language", SignLanguageServiceImpl, factory=lambda: mock_sign_service
        )
        container.register(
            "screen_reading",
            ScreenReadingServiceImpl,
            factory=lambda: mock_screen_service,
        )
        container.register(
            "content_conversion",
            ContentConversionServiceImpl,
            factory=lambda: mock_content_service,
        )

        factory = AccessibilityServiceFactory(container)
        await factory.initialize()

        coordinator = AccessibilityServiceCoordinator(factory)
        await coordinator.initialize()

        return coordinator

    @pytest.mark.asyncio
    async def test_api_backward_compatibility(self, legacy_service, new_coordinator):
        """测试API向后兼容性"""
        # 测试参数
        image_data = b"test_image_data"
        user_id = "test_user"
        preferences = {"detail_level": "basic"}
        location = {"lat": 39.9, "lng": 116.4}

        # 调用原有API
        legacy_result = await legacy_service.analyze_scene(
            image_data, user_id, preferences, location
        )

        # 调用新API
        new_result = await new_coordinator.analyze_scene(
            image_data, user_id, preferences, location
        )

        # 验证返回结果结构兼容
        assert "scene_type" in legacy_result
        assert "scene_type" in new_result

        assert "obstacles" in legacy_result
        assert "obstacles" in new_result

        assert "confidence" in legacy_result
        assert "confidence" in new_result

        print("✅ API向后兼容性测试通过")

    @pytest.mark.asyncio
    async def test_response_format_consistency(self, new_coordinator):
        """测试响应格式一致性"""
        # 测试所有主要API的响应格式

        # 场景分析API
        scene_result = await new_coordinator.analyze_scene(b"test_data", "user", {}, {})

        required_scene_fields = ["user_id", "timestamp", "scene_type", "confidence"]
        for field in required_scene_fields:
            assert field in scene_result, f"场景分析结果缺少字段: {field}"

        # 语音处理API
        voice_result = (
            await new_coordinator._voice_assistance_service.process_voice_command(
                b"test_audio", "zh-CN", "user", {}
            )
        )

        required_voice_fields = ["user_id", "timestamp", "intent", "confidence"]
        for field in required_voice_fields:
            assert field in voice_result, f"语音处理结果缺少字段: {field}"

        # 手语识别API
        sign_result = (
            await new_coordinator._sign_language_service.recognize_sign_language(
                b"test_video", "CSL", "user"
            )
        )

        required_sign_fields = ["user_id", "timestamp", "language", "confidence"]
        for field in required_sign_fields:
            assert field in sign_result, f"手语识别结果缺少字段: {field}"

        print("✅ 响应格式一致性测试通过")

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self, new_coordinator):
        """测试错误处理一致性"""
        # 测试各种错误情况

        # 1. 无效输入数据
        with pytest.raises(Exception) as exc_info:
            await new_coordinator.analyze_scene(None, "user", {}, {})  # 无效的图像数据

        assert exc_info.value is not None

        # 2. 不支持的语言
        with pytest.raises(Exception) as exc_info:
            await new_coordinator._sign_language_service.recognize_sign_language(
                b"test_data", "INVALID_LANG", "user"
            )

        assert "不支持的手语语言" in str(exc_info.value)

        # 3. 服务未初始化
        uninitialized_service = (
            await new_coordinator._factory.create_blind_assistance_service()
        )
        # 不调用initialize()

        with pytest.raises(Exception) as exc_info:
            await uninitialized_service.analyze_scene(b"test_data", "user", {}, {})

        assert "未初始化" in str(exc_info.value)

        print("✅ 错误处理一致性测试通过")


class TestRealWorldDataFlow:
    """真实世界数据流测试类"""

    @pytest.mark.asyncio
    async def test_image_processing_pipeline(self):
        """测试图像处理管道"""
        # 模拟真实图像数据处理流程

        # 1. 图像预处理
        raw_image = b"fake_raw_image_data" * 1000  # 模拟较大的图像

        # 2. 场景分析
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()

        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()

        from internal.service.implementations import BlindAssistanceServiceImpl

        service = BlindAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        await service.initialize()

        # 3. 处理图像
        result = await service.analyze_scene(
            raw_image, "user", {}, {"lat": 39.9, "lng": 116.4}
        )

        # 4. 验证处理结果
        assert result is not None
        assert "scene_type" in result
        assert "processing_time_ms" in result

        # 5. 验证性能
        processing_time = result.get("processing_time_ms", 0)
        assert processing_time < 5000, f"图像处理时间过长: {processing_time}ms"

        await service.cleanup()
        print("✅ 图像处理管道测试通过")

    @pytest.mark.asyncio
    async def test_audio_processing_pipeline(self):
        """测试音频处理管道"""
        # 模拟真实音频数据处理流程

        # 1. 音频预处理
        raw_audio = b"fake_raw_audio_data" * 500  # 模拟音频数据

        # 2. 语音识别和处理
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()

        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()

        from internal.service.implementations import VoiceAssistanceServiceImpl

        service = VoiceAssistanceServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        await service.initialize()

        # 3. 处理音频
        result = await service.process_voice_command(raw_audio, "zh-CN", "user", {})

        # 4. 验证处理结果
        assert result is not None
        assert "intent" in result
        assert "confidence" in result

        # 5. 文本转语音
        tts_result = await service.text_to_speech(
            result["response"], "zh-CN", {"speed": "normal"}
        )

        assert tts_result is not None
        assert "audio_data" in tts_result

        await service.cleanup()
        print("✅ 音频处理管道测试通过")

    @pytest.mark.asyncio
    async def test_video_processing_pipeline(self):
        """测试视频处理管道"""
        # 模拟真实视频数据处理流程

        # 1. 视频预处理
        raw_video = b"fake_raw_video_data" * 2000  # 模拟视频数据

        # 2. 手语识别
        mock_model_manager = Mock()
        mock_model_manager.load_model = AsyncMock(return_value=Mock())
        mock_model_manager.unload_model = AsyncMock()

        mock_cache_manager = Mock()
        mock_cache_manager.get = AsyncMock(return_value=None)
        mock_cache_manager.set = AsyncMock()
        mock_cache_manager.delete = AsyncMock()

        from internal.service.implementations import SignLanguageServiceImpl

        service = SignLanguageServiceImpl(
            mock_model_manager, mock_cache_manager, enabled=True
        )
        await service.initialize()

        # 3. 处理视频
        result = await service.recognize_sign_language(raw_video, "CSL", "user")

        # 4. 验证处理结果
        assert result is not None
        assert "recognition" in result
        assert "semantic" in result
        assert "gestures" in result

        # 5. 验证手势检测
        gestures = result["gestures"]
        assert isinstance(gestures, list)

        await service.cleanup()
        print("✅ 视频处理管道测试通过")


if __name__ == "__main__":
    # 运行端到端测试
    pytest.main([__file__, "-v", "-s"])
