#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情绪分析服务测试
"""
import sys
import os
import unittest
import json
import asyncio
from datetime import datetime

# 确保能够导入应用代码
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.lifecycle.emotional_analyzer.emotional_service import EmotionalService

class TestEmotionalService(unittest.TestCase):
    """情绪分析服务测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.emotional_service = EmotionalService()
        
        # 测试用户数据
        self.user_id = "test_user_001"
        
        # 测试文本输入
        self.text_inputs = [
            {
                "input_type": "text",
                "data": "我今天感到非常生气，因为工作中遇到了很多问题，心情很糟糕。",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "text",
                "data": "这几天一直很开心，和家人一起度过了愉快的周末。",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "text",
                "data": "我有点担心最近的健康状况，可能需要去医院检查一下。",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "text",
                "data": "最近工作很忙，但是心情还算平静，没有太大的波动。",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "text",
                "data": "我非常难过，感觉自己的努力都没有得到回报。",
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        # 测试语音输入
        self.voice_inputs = [
            {
                "input_type": "voice",
                "data": b"mock_voice_data_angry",
                "metadata": {
                    "pitch": "0.8",
                    "volume": "0.9",
                    "speech_rate": "0.8",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "voice",
                "data": b"mock_voice_data_happy",
                "metadata": {
                    "pitch": "0.7",
                    "volume": "0.7",
                    "speech_rate": "0.6",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
        
        # 测试生理数据输入
        self.physiological_inputs = [
            {
                "input_type": "physiological",
                "data": b"mock_physiological_data_stressed",
                "metadata": {
                    "heart_rate": "95",
                    "hrv": "25",
                    "eda": "6.5",
                    "timestamp": datetime.now().isoformat()
                }
            },
            {
                "input_type": "physiological",
                "data": b"mock_physiological_data_calm",
                "metadata": {
                    "heart_rate": "65",
                    "hrv": "65",
                    "eda": "2.1",
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
    
    def test_analyze_text_emotion(self):
        """测试文本情绪分析"""
        for text_input in self.text_inputs:
            text = text_input["data"]
            emotion_scores = self.emotional_service._analyze_text_emotion(text)
            
            # 验证基本结构
            self.assertIsInstance(emotion_scores, dict)
            self.assertTrue(len(emotion_scores) > 0)
            
            # 验证情绪得分
            for emotion, score in emotion_scores.items():
                self.assertIsInstance(emotion, str)
                self.assertIsInstance(score, float)
                self.assertTrue(0 <= score <= 1.0)
    
    def test_analyze_voice_emotion(self):
        """测试语音情绪分析"""
        for voice_input in self.voice_inputs:
            data = voice_input["data"]
            metadata = voice_input["metadata"]
            emotion_scores = self.emotional_service._analyze_voice_emotion(data, metadata)
            
            # 验证基本结构
            self.assertIsInstance(emotion_scores, dict)
            self.assertTrue(len(emotion_scores) > 0)
            
            # 验证情绪得分
            for emotion, score in emotion_scores.items():
                self.assertIsInstance(emotion, str)
                self.assertIsInstance(score, float)
                self.assertTrue(0 <= score <= 1.0)
    
    def test_analyze_physiological_data(self):
        """测试生理数据情绪分析"""
        for physio_input in self.physiological_inputs:
            data = physio_input["data"]
            metadata = physio_input["metadata"]
            emotion_scores = self.emotional_service._analyze_physiological_data(data, metadata)
            
            # 验证基本结构
            self.assertIsInstance(emotion_scores, dict)
            self.assertTrue(len(emotion_scores) > 0)
            
            # 验证情绪得分
            for emotion, score in emotion_scores.items():
                self.assertIsInstance(emotion, str)
                self.assertIsInstance(score, float)
                self.assertTrue(0 <= score <= 1.0)
    
    def test_analyze_emotional_state_text_only(self):
        """测试仅有文本输入的情绪状态分析"""
        # 创建异步函数包装器
        async def async_test():
            result = await self.emotional_service.analyze_emotional_state(
                self.user_id, 
                [self.text_inputs[0]]  # 使用愤怒情绪的文本
            )
            return result
        
        # 运行异步测试
        result = asyncio.run(async_test())
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("emotion_scores", result)
        self.assertIn("primary_emotion", result)
        self.assertIn("emotional_tendency", result)
        self.assertIn("health_impact", result)
        self.assertIn("suggestions", result)
        
        # 验证愤怒应该是主要情绪
        self.assertEqual(result["primary_emotion"], "愤怒")
        
        # 验证健康影响
        health_impact = result["health_impact"]
        self.assertIn("affected_systems", health_impact)
        self.assertIn("tcm_interpretation", health_impact)
        self.assertIn("severity", health_impact)
        
        # 验证干预建议
        suggestions = result["suggestions"]
        self.assertTrue(len(suggestions) > 0)
        for suggestion in suggestions:
            self.assertIn("intervention_type", suggestion)
            self.assertIn("description", suggestion)
            self.assertIn("estimated_effectiveness", suggestion)
            self.assertIn("is_urgent", suggestion)
    
    def test_analyze_emotional_state_multi_input(self):
        """测试多种输入源的情绪状态分析"""
        # 创建混合输入
        mixed_inputs = [
            self.text_inputs[1],  # 快乐文本
            self.voice_inputs[0],  # 愤怒语音
            self.physiological_inputs[0]  # 紧张生理数据
        ]
        
        # 创建异步函数包装器
        async def async_test():
            result = await self.emotional_service.analyze_emotional_state(
                self.user_id, 
                mixed_inputs
            )
            return result
        
        # 运行异步测试
        result = asyncio.run(async_test())
        
        # 验证结果有多种情绪得分
        emotion_scores = result["emotion_scores"]
        self.assertTrue(len(emotion_scores) >= 3)
        
        # 验证主要情绪应该受到权重高的输入源(生理数据)影响
        # 由于生理数据的权重最高，且示例数据表现为紧张/愤怒，
        # 预期主要情绪应该是愤怒或恐惧
        self.assertIn(result["primary_emotion"], ["愤怒", "恐惧"])
    
    def test_tcm_emotion_mappings(self):
        """测试中医情志理论映射"""
        mappings = self.emotional_service.tcm_emotion_mappings
        
        # 验证基本结构
        self.assertIsInstance(mappings, dict)
        self.assertTrue(len(mappings) >= 7)  # 至少包含七情
        
        # 验证每种情志的数据结构
        for emotion, data in mappings.items():
            self.assertIn("modern_emotions", data)
            self.assertIn("organ", data)
            self.assertIn("imbalance_symptoms", data)
            self.assertIn("balancing_elements", data)
    
    def test_intervention_strategies(self):
        """测试干预策略"""
        strategies = self.emotional_service.intervention_strategies
        
        # 验证基本结构
        self.assertIsInstance(strategies, dict)
        self.assertTrue(len(strategies) > 0)
        
        # 验证每种情绪的干预策略
        for emotion, emotion_strategies in strategies.items():
            self.assertTrue(len(emotion_strategies) > 0)
            
            # 验证每种策略的数据结构
            for strategy in emotion_strategies:
                self.assertIn("type", strategy)
                self.assertIn("name", strategy)
                self.assertIn("description", strategy)
                self.assertIn("effectiveness", strategy)
                self.assertIn("suitable_for", strategy)


if __name__ == "__main__":
    unittest.main() 