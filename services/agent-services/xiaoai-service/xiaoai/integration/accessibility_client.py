#!/usr/bin/env python3

"""
小艾(xiaoai)智能体的无障碍服务客户端适配器
支持多模态输入处理和四诊协调中的无障碍功能
"""

import asyncio
import base64
import logging

# 导入配置
import os
import sys
from dataclasses import dataclass
from typing import Any

import aiohttp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
except ImportError:
    # 如果导入失败, 创建一个简单的配置类
    class Config:
        def __init__(self):
            pass

        def get(self, key, default=None):
            return default

# 实际项目中需要导入生成的proto文件
# from accessibility_service.api.grpc import accessibility_pb2 as pb2
# from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)

@dataclass
class AccessibilityConfig:
    """无障碍服务配置"""
    serviceurl: str = "http://localhost:50051"
    grpcurl: str = "localhost:50051"
    timeout: int = 30
    maxretries: int = 3
    enabled: bool = True

class AccessibilityServiceClient:
    """无障碍服务客户端"""

    def __init__(self, config: AccessibilityConfig = None):
        self.config = config or AccessibilityConfig()
        self.session = None
        self.grpcchannel = None
        self.grpcstub = None

    async def initialize(self):
        """初始化客户端连接"""
        try:
            # 初始化HTTP会话
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )

            # 测试连接
            await self.health_check()
            logger.info("无障碍服务客户端初始化成功")

        except Exception as e:
            logger.error(f"无障碍服务客户端初始化失败: {e}")
            raise

    async def close(self):
        """关闭客户端连接"""
        if self.session:
            await self.session.close()
        if self.grpc_channel:
            await self.grpc_channel.close()

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.config.enabled:
                return False

            async with self.session.get(f"{self.config.service_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"无障碍服务健康检查失败: {e}")
            return False

    async def process_voice_input(self,
                                audiodata: bytes,
                                userid: str,
                                context: str = "health_consultation",
                                language: str = "zh-CN") -> dict[str, Any]:
        """
        处理语音输入

        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 上下文类型
            language: 语言代码

        Returns:
            Dict: 包含识别文本和响应的字典
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = aiohttp.FormData()
            data.add_field('audio_data', base64.b64encode(audiodata).decode())
            data.add_field('user_id', userid)
            data.add_field('context', context)
            data.add_field('language', language)

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/voice-assistance",
                data=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "recognized_text": result.get("recognized_text", ""),
                        "response_text": result.get("response_text", ""),
                        "response_audio": result.get("response_audio", ""),
                        "confidence": result.get("confidence", 0.0)
                    }
                else:
                    await response.text()
                    logger.error(f"语音处理失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"语音输入处理异常: {e}")
            return {"success": False, "error": str(e)}

    async def process_image_input(self,
                                imagedata: bytes,
                                userid: str,
                                imagetype: str = "tongue",
                                context: str = "visual_diagnosis") -> dict[str, Any]:
        """
        处理图像输入

        Args:
            image_data: 图像数据
            user_id: 用户ID
            image_type: 图像类型
            context: 上下文类型

        Returns:
            Dict: 包含图像分析结果的字典
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = aiohttp.FormData()
            data.add_field('image_data', base64.b64encode(imagedata).decode())
            data.add_field('user_id', userid)
            data.add_field('image_type', imagetype)
            data.add_field('context', context)

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/image-assistance",
                data=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "scene_description": result.get("scene_description", ""),
                        "medical_features": result.get("medical_features", []),
                        "navigation_guidance": result.get("navigation_guidance", ""),
                        "audio_guidance": result.get("audio_guidance", ""),
                        "confidence": result.get("confidence", 0.0)
                    }
                else:
                    await response.text()
                    logger.error(f"图像处理失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"图像输入处理异常: {e}")
            return {"success": False, "error": str(e)}

    async def generate_accessible_content(self,
                                        content: str,
                                        userid: str,
                                        contenttype: str = "health_advice",
                                        targetformat: str = "audio") -> dict[str, Any]:
        """
        生成无障碍内容

        Args:
            content: 原始内容
            user_id: 用户ID
            content_type: 内容类型
            target_format: 目标格式

        Returns:
            Dict: 包含无障碍内容的字典
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = {
                "content": content,
                "user_id": userid,
                "content_type": contenttype,
                "target_format": target_format
            }

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/accessible-content",
                json=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "accessible_content": result.get("accessible_content", ""),
                        "audio_content": result.get("audio_content", ""),
                        "tactile_content": result.get("tactile_content", ""),
                        "content_url": result.get("content_url", "")
                    }
                else:
                    await response.text()
                    logger.error(f"内容转换失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"内容转换异常: {e}")
            return {"success": False, "error": str(e)}

    async def provide_screen_reading(self,
                                   screendata: str,
                                   userid: str,
                                   context: str = "health_interface") -> dict[str, Any]:
        """
        提供屏幕阅读服务

        Args:
            screen_data: 屏幕数据(base64编码)
            user_id: 用户ID
            context: 上下文类型

        Returns:
            Dict: 包含屏幕阅读结果的字典
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = {
                "screen_data": screendata,
                "user_id": userid,
                "context": context
            }

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/screen-reading",
                json=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "screen_description": result.get("screen_description", ""),
                        "ui_elements": result.get("ui_elements", []),
                        "audio_description": result.get("audio_description", "")
                    }
                else:
                    await response.text()
                    logger.error(f"屏幕阅读失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"屏幕阅读异常: {e}")
            return {"success": False, "error": str(e)}

    async def manage_accessibility_settings(self,
                                          userid: str,
                                          preferences: dict[str, Any],
                                          action: str = "update") -> dict[str, Any]:
        """
        管理无障碍设置

        Args:
            user_id: 用户ID
            preferences: 用户偏好设置
            action: 操作类型

        Returns:
            Dict: 操作结果
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = {
                "user_id": userid,
                "preferences": preferences,
                "action": action
            }

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/settings",
                json=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "current_preferences": result.get("current_preferences", {}),
                        "message": result.get("message", "")
                    }
                else:
                    await response.text()
                    logger.error(f"设置管理失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"设置管理异常: {e}")
            return {"success": False, "error": str(e)}

    async def translate_speech(self,
                             audiodata: bytes,
                             userid: str,
                             sourcelanguage: str = "zh_CN",
                             targetlanguage: str = "en_XX") -> dict[str, Any]:
        """
        语音翻译服务

        Args:
            audio_data: 音频数据
            user_id: 用户ID
            source_language: 源语言
            target_language: 目标语言

        Returns:
            Dict: 翻译结果
        """
        try:
            if not self.config.enabled:
                return {"success": False, "error": "无障碍服务未启用"}

            # 准备请求数据
            data = aiohttp.FormData()
            data.add_field('audio_data', base64.b64encode(audiodata).decode())
            data.add_field('user_id', userid)
            data.add_field('source_language', sourcelanguage)
            data.add_field('target_language', targetlanguage)

            async with self.session.post(
                f"{self.config.service_url}/api/v1/accessibility/speech-translation",
                data=data
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return {
                        "success": True,
                        "original_text": result.get("original_text", ""),
                        "translated_text": result.get("translated_text", ""),
                        "translated_audio": result.get("translated_audio", ""),
                        "confidence": result.get("confidence", 0.0)
                    }
                else:
                    await response.text()
                    logger.error(f"语音翻译失败: {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}

        except Exception as e:
            logger.error(f"语音翻译异常: {e}")
            return {"success": False, "error": str(e)}

# 全局客户端实例
accessibility_client = None

async def get_accessibility_client(config: AccessibilityConfig = None) -> AccessibilityServiceClient:
    """获取无障碍服务客户端实例"""
    global _accessibility_client

    if _accessibility_client is None:
        AccessibilityServiceClient(config)
        await _accessibility_client.initialize()

    return _accessibility_client

async def close_accessibility_client():
    """关闭无障碍服务客户端"""
    global _accessibility_client

    if _accessibility_client:
        await _accessibility_client.close()

class MockAccessibilityStub:
    """模拟的无障碍服务存根(用于开发和测试)"""

    def __init__(self):
        logger.info("使用模拟无障碍服务存根")

    async def VoiceAssistance(self, request):
        """模拟语音辅助"""
        await asyncio.sleep(0.1)
        return type('Response', (), {
            'recognized_text': '模拟识别文本',
            'response_text': '模拟回复文本',
            'response_audio': b'mock_audio',
            'confidence': 0.9
        })()

# 单例实例
accessibilityclient = AccessibilityServiceClient()
