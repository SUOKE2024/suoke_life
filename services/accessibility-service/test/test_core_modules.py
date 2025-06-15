#!/usr/bin/env python3
"""
核心模块单元测试
轻量级测试，不依赖重型AI库
"""

import sys
import unittest
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config import Config
from internal.service.modules.content_conversion import ContentConversionModule
from internal.service.modules.sign_language import SignLanguageModule
from internal.service.modules.translation import TranslationModule
from internal.service.modules.voice_assistance import VoiceAssistanceModule


class TestConfig(unittest.TestCase):
    """配置模块测试"""

    def setUp(self) -> None:
        """测试前准备"""
        self.config = Config()

    def test_config_loading(self) -> None:
        """测试配置加载"""
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.config.service)
        self.assertEqual(self.config.service.name, "accessibility-service")

    def test_version_property(self) -> None:
        """测试版本属性"""
        self.assertIsNotNone(self.config.version)
        self.assertIsInstance(self.config.version, str)

    def test_service_config(self) -> None:
        """测试服务配置"""
        self.assertEqual(self.config.service.port, 50051)
        self.assertEqual(self.config.service.host, "0.0.0.0")

    def test_features_config(self) -> None:
        """测试功能配置"""
        self.assertIsNotNone(self.config.features)
        # 测试配置存在性而不是具体值
        self.assertIsNotNone(self.config.features.blind_assistance)
        self.assertIsInstance(self.config.features.blind_assistance.enabled, bool)


class TestTranslationModule(unittest.TestCase):
    """翻译模块测试"""

    def setUp(self) -> None:
        """测试前准备"""
        self.module = TranslationModule()

    def test_module_initialization(self) -> None:
        """测试模块初始化"""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.module_name, "translation")

    def test_process_request(self) -> None:
        """测试请求处理"""
        request_data = {"text": "你好", "source_lang": "zh", "target_lang": "en"}
        result = self.module.process(request_data)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)


class TestVoiceAssistanceModule(unittest.TestCase):
    """语音辅助模块测试"""

    def setUp(self) -> None:
        """测试前准备"""
        self.module = VoiceAssistanceModule()

    def test_module_initialization(self) -> None:
        """测试模块初始化"""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.module_name, "voice_assistance")

    def test_process_voice_command(self) -> None:
        """测试语音指令处理"""
        result = self.module.process_voice_command("打开无障碍设置")
        self.assertIsNotNone(result)
        self.assertTrue(result["success"])
        self.assertIn("response", result)


class TestSignLanguageModule(unittest.TestCase):
    """手语识别模块测试"""

    def setUp(self) -> None:
        """测试前准备"""
        self.module = SignLanguageModule()

    def test_module_initialization(self) -> None:
        """测试模块初始化"""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.module_name, "sign_language")


class TestContentConversionModule(unittest.TestCase):
    """内容转换模块测试"""

    def setUp(self) -> None:
        """测试前准备"""
        self.module = ContentConversionModule()

    def test_module_initialization(self) -> None:
        """测试模块初始化"""
        self.assertIsNotNone(self.module)
        self.assertEqual(self.module.module_name, "content_conversion")

    def test_simplify_content(self) -> None:
        """测试内容简化"""
        content = "这是一个复杂的医学术语和技术说明文档"
        # 使用process方法进行测试
        request_data = {
            "content": content,
            "conversion_type": "simplified",
            "level": "basic",
        }
        result = self.module.process(request_data)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
