#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小艾(xiaoai)智能体的无障碍服务客户端适配器
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict

# 导入配置
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.config import Config

# 实际项目中需要导入生成的proto文件
# from accessibility_service.api.grpc import accessibility_pb2 as pb2
# from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)

class AccessibilityClient:
    """无障碍服务客户端适配器，处理与无障碍服务的通信"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        初始化客户端
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.channel = None
        self.stub = None
        self._connect()
        logger.info("无障碍服务客户端初始化完成")
    
    def _connect(self) -> None:
        """连接到无障碍服务"""
        try:
            # 获取服务地址
            host = self.config.get("integration.accessibility_service.host", "accessibility-service")
            port = self.config.get("integration.accessibility_service.port", 50051)
            timeout_ms = self.config.get("integration.accessibility_service.timeout_ms", 5000)
            
            # 创建通道
            self.channel = grpc.insecure_channel(
                f"{host}:{port}",
                options=[
                    ('grpc.max_send_message_length', 50 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 50 * 1024 * 1024),
                    ('grpc.enable_retries', 1),
                    ('grpc.service_config', json.dumps({
                        'methodConfig': [{
                            'name': [{}],
                            'retryPolicy': {
                                'maxAttempts': 3,
                                'initialBackoff': '0.1s',
                                'maxBackoff': '1s',
                                'backoffMultiplier': 2,
                                'retryableStatusCodes': ['UNAVAILABLE']
                            },
                            'timeout': f'{timeout_ms}ms'
                        }]
                    }))
                ]
            )
            
            # 创建stub
            # 实际项目中应该创建实际的stub
            # self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)
            # 这里为简化，不创建实际的stub
            
            logger.info(f"成功连接到无障碍服务: {host}:{port}")
            
        except Exception as e:
            logger.error(f"连接无障碍服务失败: {str(e)}", exc_info=True)
            self.channel = None
    
    def blind_assistance(self, image_data: bytes, user_id: str, 
                         preferences: Dict[str, Any], location: Dict[str, Any]) -> Dict[str, Any]:
        """
        导盲服务 - 分析图像并提供场景描述和障碍物检测
        
        Args:
            image_data: 场景图像数据
            user_id: 用户ID
            preferences: 用户偏好设置
            location: 地理位置信息
            
        Returns:
            包含场景描述、障碍物信息和导航建议的字典
        """
        logger.info(f"发送导盲服务请求: 用户={user_id}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # user_preferences = pb2.UserPreferences(**preferences)
            # geo_location = pb2.GeoLocation(**location)
            # request = pb2.BlindAssistanceRequest(
            #     image_data=image_data,
            #     user_id=user_id,
            #     preferences=user_preferences,
            #     location=geo_location
            # )
            # response = self.stub.BlindAssistance(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.1)  # 模拟网络延迟
            result = {
                "scene_description": "前方是一条人行道，左侧有一棵树，右侧是商店入口",
                "obstacles": [
                    {"type": "person", "distance": 2.5, "direction": "front", "confidence": 0.92},
                    {"type": "bench", "distance": 1.8, "direction": "left", "confidence": 0.85},
                ],
                "navigation_guidance": "可以继续直行，但注意前方2.5米处有行人",
                "confidence": 0.89,
                "audio_guidance": b""  # 实际应该返回音频数据
            }
            
            logger.info(f"导盲服务请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"导盲服务请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "scene_description": "无法获取场景描述",
                "obstacles": [],
                "navigation_guidance": "服务暂时不可用，请稍后重试",
                "confidence": 0.0,
                "audio_guidance": b""
            }
    
    def sign_language_recognition(self, video_data: bytes, user_id: str, 
                                 language: str) -> Dict[str, Any]:
        """
        手语识别服务 - 将手语视频转换为文本
        
        Args:
            video_data: 手语视频数据
            user_id: 用户ID
            language: 语言代码
            
        Returns:
            包含识别文本和置信度的字典
        """
        logger.info(f"发送手语识别请求: 用户={user_id}, 语言={language}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # request = pb2.SignLanguageRequest(
            #     video_data=video_data,
            #     user_id=user_id,
            #     language=language
            # )
            # response = self.stub.SignLanguageRecognition(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.2)  # 模拟网络延迟
            result = {
                "text": "您好，我需要帮助",
                "confidence": 0.82,
                "segments": [
                    {"text": "您好", "start_time_ms": 0, "end_time_ms": 1200, "confidence": 0.90},
                    {"text": "我需要帮助", "start_time_ms": 1500, "end_time_ms": 3000, "confidence": 0.78}
                ]
            }
            
            logger.info(f"手语识别请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"手语识别请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "segments": []
            }
    
    def screen_reading(self, screen_data: bytes, user_id: str, 
                      context: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        屏幕阅读服务 - 分析屏幕内容并提供语音描述
        
        Args:
            screen_data: 屏幕截图数据
            user_id: 用户ID
            context: 上下文信息
            preferences: 用户偏好设置
            
        Returns:
            包含屏幕描述和UI元素的字典
        """
        logger.info(f"发送屏幕阅读请求: 用户={user_id}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # user_preferences = pb2.UserPreferences(**preferences)
            # request = pb2.ScreenReadingRequest(
            #     screen_data=screen_data,
            #     user_id=user_id,
            #     context=context,
            #     preferences=user_preferences
            # )
            # response = self.stub.ScreenReading(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.15)  # 模拟网络延迟
            result = {
                "screen_description": "当前页面显示了3个元素，包含1个可操作按钮：开始体质测评。",
                "elements": [
                    {
                        "element_type": "button", 
                        "content": "开始体质测评",
                        "action": "点击开始测评流程",
                        "location": {"x": 0.5, "y": 0.3, "width": 0.4, "height": 0.08}
                    },
                    {
                        "element_type": "text", 
                        "content": "了解您的中医体质",
                        "action": "静态文本",
                        "location": {"x": 0.5, "y": 0.2, "width": 0.6, "height": 0.05}
                    },
                    {
                        "element_type": "image", 
                        "content": "体质类型图谱",
                        "action": "显示体质介绍",
                        "location": {"x": 0.5, "y": 0.5, "width": 0.7, "height": 0.3}
                    }
                ],
                "audio_description": b""  # 实际应该返回音频数据
            }
            
            logger.info(f"屏幕阅读请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"屏幕阅读请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "screen_description": "无法解析屏幕内容",
                "elements": [],
                "audio_description": b""
            }
    
    def voice_assistance(self, audio_data: bytes, user_id: str, context: str, 
                        language: str, dialect: str) -> Dict[str, Any]:
        """
        语音辅助服务 - 进行语音识别和响应
        
        Args:
            audio_data: 语音数据
            user_id: 用户ID
            context: 上下文信息
            language: 语言代码
            dialect: 方言代码
            
        Returns:
            包含识别文本和响应的字典
        """
        logger.info(f"发送语音辅助请求: 用户={user_id}, 语言={language}, 方言={dialect}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # request = pb2.VoiceAssistanceRequest(
            #     audio_data=audio_data,
            #     user_id=user_id,
            #     context=context,
            #     language=language,
            #     dialect=dialect
            # )
            # response = self.stub.VoiceAssistance(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.12)  # 模拟网络延迟
            result = {
                "recognized_text": "我想了解痰湿体质的特点",
                "response_text": "痰湿体质的主要特点是体形肥胖，腹部松软，容易疲劳，痰多，舌苔厚腻。建议饮食清淡，少食多餐，多运动以促进代谢。",
                "response_audio": b"",  # 实际应该返回音频数据
                "confidence": 0.88
            }
            
            logger.info(f"语音辅助请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"语音辅助请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "recognized_text": "",
                "response_text": "抱歉，我无法处理您的语音请求",
                "response_audio": b"",
                "confidence": 0.0
            }
    
    def accessible_content(self, content_id: str, content_type: str, user_id: str, 
                          target_format: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        健康内容无障碍转换 - 将健康内容转换为无障碍格式
        
        Args:
            content_id: 内容ID
            content_type: 内容类型
            user_id: 用户ID
            target_format: 目标格式
            preferences: 用户偏好设置
            
        Returns:
            包含可访问内容的字典
        """
        logger.info(f"发送内容转换请求: 用户={user_id}, 内容ID={content_id}, 目标格式={target_format}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # user_preferences = pb2.UserPreferences(**preferences)
            # request = pb2.AccessibleContentRequest(
            #     content_id=content_id,
            #     content_type=content_type,
            #     user_id=user_id,
            #     target_format=target_format,
            #     preferences=user_preferences
            # )
            # response = self.stub.AccessibleContent(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.18)  # 模拟网络延迟
            
            if target_format == "audio":
                result = {
                    "accessible_content": "",
                    "content_url": "https://storage.suoke.life/audio/content_123.mp3",
                    "audio_content": b"",  # 实际应该返回音频数据
                    "tactile_content": b""
                }
            elif target_format == "simplified":
                result = {
                    "accessible_content": "痰湿体质特点：胖、疲劳、痰多。建议：少吃、多动、清淡饮食。",
                    "content_url": "",
                    "audio_content": b"",
                    "tactile_content": b""
                }
            else:
                result = {
                    "accessible_content": "痰湿体质的主要特点是体形肥胖，腹部松软，容易疲劳，痰多，舌苔厚腻。建议饮食清淡，少食多餐，多运动以促进代谢。",
                    "content_url": "",
                    "audio_content": b"",
                    "tactile_content": b""
                }
            
            logger.info(f"内容转换请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"内容转换请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "accessible_content": "内容转换失败",
                "content_url": "",
                "audio_content": b"",
                "tactile_content": b""
            }
    
    def manage_settings(self, user_id: str, preferences: Dict[str, Any], 
                       action: str) -> Dict[str, Any]:
        """
        无障碍设置管理 - 获取或更新用户的无障碍设置
        
        Args:
            user_id: 用户ID
            preferences: 用户偏好设置
            action: 操作（获取/更新）
            
        Returns:
            包含当前设置的字典
        """
        logger.info(f"发送设置管理请求: 用户={user_id}, 操作={action}")
        start_time = time.time()
        
        try:
            if not self.channel:
                self._connect()
                if not self.channel:
                    raise Exception("无法连接到无障碍服务")
            
            # 实际项目中应该构建请求并调用stub
            # user_preferences = pb2.UserPreferences(**preferences)
            # request = pb2.SettingsRequest(
            #     user_id=user_id,
            #     preferences=user_preferences,
            #     action=action
            # )
            # response = self.stub.ManageSettings(request)
            # return MessageToDict(response, preserving_proto_field_name=True)
            
            # 模拟服务调用结果
            time.sleep(0.08)  # 模拟网络延迟
            
            if action == "get":
                result = {
                    "current_preferences": {
                        "font_size": "large",
                        "high_contrast": True,
                        "voice_type": "female",
                        "speech_rate": 1.2,
                        "language": "zh-CN",
                        "dialect": "mandarin",
                        "screen_reader": True,
                        "sign_language": False,
                        "enabled_features": ["voice_assistance", "screen_reading"]
                    },
                    "success": True,
                    "message": "成功获取用户设置"
                }
            elif action == "update":
                result = {
                    "current_preferences": preferences,
                    "success": True,
                    "message": "成功更新用户设置"
                }
            else:
                result = {
                    "current_preferences": {},
                    "success": False,
                    "message": f"不支持的操作: {action}"
                }
            
            logger.info(f"设置管理请求完成: 用户={user_id}, 耗时={time.time() - start_time:.2f}秒")
            return result
            
        except Exception as e:
            logger.error(f"设置管理请求失败: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "current_preferences": {},
                "success": False,
                "message": f"处理失败: {str(e)}"
            }
    
    def close(self) -> None:
        """关闭与无障碍服务的连接"""
        if self.channel:
            try:
                self.channel.close()
                logger.info("关闭与无障碍服务的连接")
            except Exception as e:
                logger.error(f"关闭与无障碍服务的连接失败: {str(e)}", exc_info=True)


# 单例实例
accessibility_client = AccessibilityClient() 