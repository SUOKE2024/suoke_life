#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译服务单元测试脚本
"""

import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch, Mock

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入需要测试的模块
from internal.service.translation_service import TranslationService

class MockConfig:
    """测试用配置类"""
    def __init__(self):
        self.translation = type('obj', (object,), {
            'model_name': 'facebook/mbart-large-50-many-to-many-mmt',
            'special_pairs': {
                'zh_CN-en_XX': {'model_name': 'Helsinki-NLP/opus-mt-zh-en'},
                'en_XX-zh_CN': {'model_name': 'Helsinki-NLP/opus-mt-en-zh'}
            }
        })

class TestTranslationService(unittest.TestCase):
    """翻译服务的测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.config = MockConfig()
        
        # 创建模拟的tokenizer和model
        self.mock_tokenizer = Mock()
        self.mock_model = Mock()
        
        # 模拟模型输出
        self.mock_model.generate.return_value = [0]  # 生成的token IDs
        self.mock_tokenizer.batch_decode.return_value = ["这是测试翻译结果"]
        self.mock_tokenizer.lang_code_to_id = {'en_XX': 0, 'zh_CN': 1}
        
        # 模拟加载模型函数
        with patch('transformers.MBartTokenizer.from_pretrained', return_value=self.mock_tokenizer), \
             patch('transformers.MBartForConditionalGeneration.from_pretrained', return_value=self.mock_model):
            self.service = TranslationService(self.config)
        
        # 模拟方言服务
        self.mock_dialect_service = Mock()
        self.mock_dialect_service.transcribe_with_dialect.return_value = {
            "text": "这是方言识别结果",
            "confidence": 0.9
        }
        self.mock_dialect_service.synthesize_speech_with_dialect.return_value = {
            "audio_data": b"mock_audio_data",
            "duration_ms": 1000
        }
        self.mock_dialect_service.get_supported_dialects.return_value = [
            {"code": "mandarin", "name": "普通话"},
            {"code": "cantonese", "name": "粤语"},
            {"code": "sichuanese", "name": "四川话"}
        ]
        
        # 注入依赖
        self.service.dialect_service = self.mock_dialect_service
        
        # 强制将mock对象放入service的translation_models字典
        self.service.translation_models = {
            "general": {
                "tokenizer": self.mock_tokenizer,
                "model": self.mock_model
            }
        }
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.service.supported_languages)
        self.assertIsNotNone(self.service.translation_models)
        self.assertEqual(len(self.service.active_sessions), 0)
    
    def test_supported_languages(self):
        """测试支持的语言列表"""
        languages = self.service.supported_languages
        self.assertGreater(len(languages), 0)
        self.assertIn('code', languages[0])
        self.assertIn('name', languages[0])
        self.assertIn('supports_speech', languages[0])
    
    def test_get_supported_language_pairs(self):
        """测试获取支持的语言对"""
        pairs = self.service.get_supported_language_pairs()
        self.assertGreater(len(pairs), 0)
        self.assertIn('source_code', pairs[0])
        self.assertIn('target_code', pairs[0])
        self.assertIn('supports_speech', pairs[0])
    
    def test_translate_text(self):
        """测试文本翻译功能"""
        source_text = "这是测试文本"
        source_lang = "zh_CN"
        target_lang = "en_XX"
        
        # 调用翻译方法
        result = self.service.translate_text(source_text, source_lang, target_lang)
        
        # 验证模型和tokenizer是否被正确调用
        self.mock_tokenizer.assert_called()
        self.mock_model.generate.assert_called()
        
        # la11
        # 验证结果
        self.assertEqual(result, "这是测试翻译结果")
    
    def test_translate_speech(self):
        """测试语音翻译功能"""
        audio_data = b"test_audio_data"
        source_lang = "zh_CN"
        target_lang = "en_XX"
        
        # 模拟翻译文本的方法
        with patch.object(self.service, 'translate_text', return_value="This is a test translation"):
            result = self.service.translate_speech(audio_data, source_lang, target_lang)
            
            # 验证结果字段
            self.assertIn("source_text", result)
            self.assertIn("translated_text", result)
            self.assertIn("translated_audio", result)
            self.assertIn("source_confidence", result)
            self.assertIn("translation_confidence", result)
            self.assertIn("processing_time_ms", result)
    
    def test_create_streaming_session(self):
        """测试创建流式翻译会话"""
        user_id = "test_user"
        source_lang = "zh_CN"
        target_lang = "en_XX"
        
        session_id = self.service.create_streaming_session(user_id, source_lang, target_lang)
        
        # 验证会话是否被创建
        self.assertTrue(session_id in self.service.active_sessions)
        self.assertEqual(self.service.active_sessions[session_id]["user_id"], user_id)
        self.assertEqual(self.service.active_sessions[session_id]["source_language"], source_lang)
        self.assertEqual(self.service.active_sessions[session_id]["target_language"], target_lang)
    
    def test_process_streaming_chunk(self):
        """测试处理流式翻译数据块"""
        # 先创建一个会话
        user_id = "test_user"
        source_lang = "zh_CN"
        target_lang = "en_XX"
        
        session_id = self.service.create_streaming_session(user_id, source_lang, target_lang)
        
        # 模拟_process_audio_buffer方法
        mock_result = {
            "source_text": "测试源文本",
            "translated_text": "Test source text",
            "translated_audio": b"audio_data",
            "source_confidence": 0.9,
            "translation_confidence": 0.85
        }
        
        with patch.object(self.service, '_process_audio_buffer', return_value=mock_result):
            # 处理一个最终的数据块
            result = self.service.process_streaming_chunk(session_id, b"audio_data", is_final=True)
            
            # 验证处理结果
            self.assertEqual(result["source_text"], mock_result["source_text"])
            self.assertEqual(result["translated_text"], mock_result["translated_text"])
            self.assertEqual(result["translated_audio"], mock_result["translated_audio"])
            self.assertTrue("segment_id" in result)
            self.assertTrue(result["is_final"])
    
    def test_get_session_status(self):
        """测试获取会话状态"""
        # 先创建一个会话
        user_id = "test_user"
        source_lang = "zh_CN"
        target_lang = "en_XX"
        
        session_id = self.service.create_streaming_session(user_id, source_lang, target_lang)
        
        # 获取会话状态
        status = self.service.get_session_status(session_id)
        
        # 验证状态信息
        self.assertEqual(status["session_id"], session_id)
        self.assertEqual(status["user_id"], user_id)
        self.assertEqual(status["source_language"], source_lang)
        self.assertEqual(status["target_language"], target_lang)
        self.assertTrue(status["is_active"])
    
    def test_cleanup_inactive_sessions(self):
        """测试清理不活跃的会话"""
        # 创建一些测试会话
        for i in range(3):
            user_id = f"test_user_{i}"
            session_id = self.service.create_streaming_session(user_id, "zh_CN", "en_XX")
            
            # 修改一些会话的状态
            if i == 1:
                self.service.active_sessions[session_id]["is_active"] = False
                # 修改最后活动时间为很久以前
                self.service.active_sessions[session_id]["last_activity"] = 0
        
        # 执行清理
        cleaned = self.service.cleanup_inactive_sessions(max_age_seconds=10)
        
        # 验证清理结果
        self.assertEqual(cleaned, 1)  # 应该清理了一个会话
        self.assertEqual(len(self.service.active_sessions), 2)  # 应该还剩两个会话

if __name__ == "__main__":
    unittest.main() 