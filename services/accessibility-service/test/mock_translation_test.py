#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
翻译服务模拟测试脚本 - 不依赖于实际安装的库
"""

import unittest
import os
import sys
import json
from unittest.mock import MagicMock, patch, Mock

# 模拟导入相关的库
sys.modules['torch'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['transformers'] = MagicMock()
sys.modules['transformers.MBartTokenizer'] = MagicMock()
sys.modules['transformers.MBartForConditionalGeneration'] = MagicMock()

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockConfig:
    """测试用配置类"""
    def __init__(self):
        self.translation = type('obj', (object,), {
            'model_name': 'mocked_model',
            'special_pairs': {}
        })

class MockTranslationService:
    """模拟的翻译服务类"""
    
    def __init__(self, config=None):
        """初始化模拟的翻译服务"""
        self.config = config or MockConfig()
        self.supported_languages = [
            {"code": "zh_CN", "name": "中文", "supports_speech": True},
            {"code": "en_XX", "name": "英语", "supports_speech": True},
            {"code": "ja_XX", "name": "日语", "supports_speech": True}
        ]
        self.translation_models = {"general": {"tokenizer": None, "model": None}}
        self.active_sessions = {}
        self.dialect_service = None
    
    def translate_text(self, text, source_language, target_language):
        """模拟文本翻译功能"""
        translations = {
            "zh_CN-en_XX": {
                "你好": "Hello",
                "我需要帮助": "I need help"
            },
            "en_XX-zh_CN": {
                "Hello": "你好",
                "I need help": "我需要帮助"
            }
        }
        
        pair_key = f"{source_language}-{target_language}"
        if pair_key in translations and text in translations[pair_key]:
            return translations[pair_key][text]
        return f"[Translated] {text}"
    
    def translate_speech(self, audio_data, source_language, target_language, 
                        source_dialect=None, target_dialect=None, preferences=None):
        """模拟语音翻译功能"""
        # 根据来源语言生成不同的示例文本
        if source_language == "zh_CN":
            source_text = "你好，我需要帮助"
            translated_text = "Hello, I need help"
        else:
            source_text = "Hello, I need help"
            translated_text = "你好，我需要帮助"
        
        return {
            "source_text": source_text,
            "translated_text": translated_text,
            "translated_audio": b"mock_audio_data",
            "source_confidence": 0.9,
            "translation_confidence": 0.85,
            "processing_time_ms": 500
        }
    
    def create_streaming_session(self, user_id, source_language, target_language,
                               source_dialect=None, target_dialect=None, preferences=None):
        """模拟创建流式翻译会话"""
        import uuid
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "source_language": source_language,
            "target_language": target_language,
            "source_dialect": source_dialect,
            "target_dialect": target_dialect,
            "preferences": preferences,
            "created_at": 1635000000,
            "last_activity": 1635000000,
            "is_active": True,
            "segments": []
        }
        
        return session_id
    
    def process_streaming_chunk(self, session_id, audio_chunk, is_final=False):
        """模拟处理流式翻译的音频数据块"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # 生成模拟的翻译结果
        result = {
            "segment_id": str(len(session["segments"]) + 1),
            "source_text": "模拟源文本",
            "translated_text": "Mock source text",
            "translated_audio": b"mock_audio_data",
            "timestamp": 1635000000,
            "is_final": is_final
        }
        
        session["segments"].append(result)
        session["last_activity"] = 1635000000
        
        if is_final:
            session["is_active"] = False
        
        return result
    
    def get_session_status(self, session_id):
        """模拟获取会话状态"""
        if session_id not in self.active_sessions:
            return {"error": "session_not_found"}
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "source_language": session["source_language"],
            "target_language": session["target_language"],
            "is_active": session["is_active"],
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "segment_count": len(session["segments"]),
            "duration_seconds": 0
        }
    
    def get_supported_language_pairs(self):
        """模拟获取支持的语言对"""
        language_pairs = []
        
        for source in self.supported_languages:
            for target in self.supported_languages:
                if source["code"] != target["code"]:
                    language_pairs.append({
                        "source_code": source["code"],
                        "source_name": source["name"],
                        "target_code": target["code"],
                        "target_name": target["name"],
                        "supports_speech": source["supports_speech"] and target["supports_speech"]
                    })
        
        return language_pairs
    
    def cleanup_inactive_sessions(self, max_age_seconds=3600):
        """模拟清理不活跃的会话"""
        to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if not session["is_active"]:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.active_sessions[session_id]
        
        return len(to_remove)


class TestMockTranslationService(unittest.TestCase):
    """翻译服务模拟测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.config = MockConfig()
        self.service = MockTranslationService(self.config)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.service.supported_languages)
        self.assertIsNotNone(self.service.translation_models)
        self.assertEqual(len(self.service.active_sessions), 0)
    
    def test_translate_text(self):
        """测试文本翻译功能"""
        result = self.service.translate_text("你好", "zh_CN", "en_XX")
        self.assertEqual(result, "Hello")
        
        result = self.service.translate_text("未知文本", "zh_CN", "en_XX")
        self.assertEqual(result, "[Translated] 未知文本")
    
    def test_translate_speech(self):
        """测试语音翻译功能"""
        result = self.service.translate_speech(b"test_audio", "zh_CN", "en_XX")
        
        self.assertEqual(result["source_text"], "你好，我需要帮助")
        self.assertEqual(result["translated_text"], "Hello, I need help")
        self.assertEqual(result["translated_audio"], b"mock_audio_data")
        self.assertEqual(result["source_confidence"], 0.9)
    
    def test_streaming_session(self):
        """测试流式翻译会话"""
        # 创建会话
        session_id = self.service.create_streaming_session("test_user", "zh_CN", "en_XX")
        self.assertIn(session_id, self.service.active_sessions)
        
        # 处理数据块
        result = self.service.process_streaming_chunk(session_id, b"audio_chunk")
        self.assertEqual(result["source_text"], "模拟源文本")
        self.assertEqual(result["translated_text"], "Mock source text")
        self.assertEqual(result["segment_id"], "1")
        
        # 处理最终数据块
        result = self.service.process_streaming_chunk(session_id, b"audio_chunk", is_final=True)
        self.assertTrue(result["is_final"])
        self.assertFalse(self.service.active_sessions[session_id]["is_active"])
        
        # 获取会话状态
        status = self.service.get_session_status(session_id)
        self.assertEqual(status["session_id"], session_id)
        self.assertEqual(status["segment_count"], 2)
        self.assertFalse(status["is_active"])
        
        # 清理不活跃会话
        cleaned = self.service.cleanup_inactive_sessions()
        self.assertEqual(cleaned, 1)
        self.assertEqual(len(self.service.active_sessions), 0)
    
    def test_supported_language_pairs(self):
        """测试支持的语言对"""
        pairs = self.service.get_supported_language_pairs()
        self.assertEqual(len(pairs), 6)  # 3种语言，每种语言可以翻译到其他2种语言
        
        zh_to_en_pair = next((p for p in pairs if p["source_code"] == "zh_CN" and p["target_code"] == "en_XX"), None)
        self.assertIsNotNone(zh_to_en_pair)
        self.assertTrue(zh_to_en_pair["supports_speech"])

if __name__ == "__main__":
    unittest.main() 