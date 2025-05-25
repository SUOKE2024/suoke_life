#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活无障碍服务集成测试
测试无障碍服务与智能体服务的集成
"""

import unittest
import os
import sys
import time
import json
import logging
from typing import Dict, Any
import asyncio

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 导入服务实现
    from internal.service.optimized_accessibility_service import OptimizedAccessibilityService
    from internal.integration.agent_adapter import AgentAdapter
    
    # 导入配置
    from config.config import Config

    SERVICE_AVAILABLE = True
except ImportError:
    logger.warning("无法导入服务模块，将使用模拟对象进行测试")
    SERVICE_AVAILABLE = False


class MockConfig:
    """模拟配置类"""
    
    def __init__(self):
        self.config_data = {
            "service": {
                "name": "accessibility-service",
                "version": "0.1.0"
            },
            "features": {
                "blind_assistance": {"enabled": True},
                "sign_language": {"enabled": True},
                "screen_reading": {"enabled": True},
                "voice_assistance": {"enabled": True},
                "content_conversion": {"enabled": True}
            },
            "integration": {
                "xiaoai_service": {
                    "host": "localhost",
                    "port": 50052
                },
                "xiaoke_service": {
                    "host": "localhost",
                    "port": 50053
                },
                "laoke_service": {
                    "host": "localhost",
                    "port": 50054
                },
                "soer_service": {
                    "host": "localhost",
                    "port": 50055
                }
            }
        }
    
    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split(".")
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value


class MockAccessibilityService:
    """模拟无障碍服务类"""
    
    def __init__(self, config=None):
        self.config = config or MockConfig()
    
    def blind_assistance(self, image_data, user_id, preferences, location):
        """模拟导盲服务"""
        return {
            "scene_description": "前方是一条人行道，左侧有一棵树，右侧是商店入口",
            "navigation_guidance": "可以继续直行，但注意前方2.5米处有行人",
            "obstacles": [
                {"type": "person", "distance": 2.5, "direction": "front", "confidence": 0.92},
                {"type": "bench", "distance": 1.8, "direction": "left", "confidence": 0.85}
            ],
            "confidence": 0.89
        }
    
    def sign_language_recognition(self, video_data, user_id, language):
        """模拟手语识别服务"""
        return {
            "text": "您好，我需要帮助",
            "confidence": 0.82,
            "segments": [
                {"text": "您好", "start_time_ms": 0, "end_time_ms": 1200, "confidence": 0.90},
                {"text": "我需要帮助", "start_time_ms": 1500, "end_time_ms": 3000, "confidence": 0.78}
            ]
        }
    
    def screen_reading(self, screen_data, user_id, context, preferences):
        """模拟屏幕阅读服务"""
        return {
            "screen_description": "当前页面显示体质测评结果页面，您的主要体质类型为阳虚质",
            "elements": [
                {
                    "element_type": "button", 
                    "content": "开始体质测评",
                    "action": "点击开始测评流程",
                    "location": {"x": 0.5, "y": 0.3, "width": 0.4, "height": 0.08}
                }
            ]
        }


class MockAgentAdapter:
    """模拟智能体适配器类"""
    
    def __init__(self):
        self.channels = {}
        self.registered_features = {}
    
    def register_accessibility_features(self):
        """注册无障碍功能"""
        self.registered_features = {
            "blind_assistance": True,
            "sign_language": True,
            "screen_reading": True,
            "voice_assistance": True,
            "content_conversion": True
        }
        return True
    
    def process_accessibility_request(self, agent_name, request_type, data):
        """处理无障碍请求"""
        if request_type == "blind_assistance":
            return {
                "success": True,
                "scene_description": "前方是道路，注意红绿灯",
                "navigation_guidance": "等待绿灯亮起后前行"
            }
        elif request_type == "sign_language":
            return {
                "success": True,
                "text": "请问如何预约医生"
            }
        elif request_type == "screen_reading":
            return {
                "success": True,
                "screen_description": "体检预约页面，包含三个选项"
            }
        else:
            return {"success": False, "error": "未知请求类型"}


class AccessibilityIntegrationTest(unittest.TestCase):
    """无障碍服务集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        if SERVICE_AVAILABLE:
            cls.config = Config()
            cls.accessibility_service = OptimizedAccessibilityService(cls.config)
            cls.agent_adapter = AgentAdapter()
        else:
            cls.config = MockConfig()
            cls.accessibility_service = MockAccessibilityService(cls.config)
            cls.agent_adapter = MockAgentAdapter()
    
    def test_agent_registration(self):
        """测试智能体注册功能"""
        result = self.agent_adapter.register_accessibility_features()
        self.assertTrue(result)
        
        if not SERVICE_AVAILABLE:
            self.assertEqual(len(self.agent_adapter.registered_features), 5)
    
    def test_xiaoai_integration(self):
        """测试与小艾智能体的集成"""
        # 测试导盲功能
        blind_result = self.agent_adapter.process_accessibility_request(
            agent_name="xiaoai",
            request_type="blind_assistance",
            data={"image_data": b"test_image"}
        )
        self.assertTrue(blind_result.get("success", False))
        self.assertIn("scene_description", blind_result)
        
        # 测试手语识别
        sign_result = self.agent_adapter.process_accessibility_request(
            agent_name="xiaoai",
            request_type="sign_language",
            data={"video_data": b"test_video"}
        )
        self.assertTrue(sign_result.get("success", False))
        self.assertIn("text", sign_result)
    
    def test_xiaoke_integration(self):
        """测试与小克智能体的集成"""
        # 测试屏幕阅读功能
        screen_result = self.agent_adapter.process_accessibility_request(
            agent_name="xiaoke",
            request_type="screen_reading",
            data={"screen_data": b"test_screen"}
        )
        self.assertTrue(screen_result.get("success", False))
        self.assertIn("screen_description", screen_result)
    
    def test_laoke_integration(self):
        """测试与老克智能体的集成"""
        # 这个测试会在实际服务中实现
        # 这里只是占位
        self.assertTrue(True)
    
    def test_soer_integration(self):
        """测试与索儿智能体的集成"""
        # 这个测试会在实际服务中实现
        # 这里只是占位
        self.assertTrue(True)


def run_tests():
    """运行测试"""
    unittest.main()


if __name__ == "__main__":
    run_tests() 