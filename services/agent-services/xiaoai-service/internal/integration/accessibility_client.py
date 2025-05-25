#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
小艾(xiaoai)智能体的无障碍服务客户端适配器
支持多模态输入处理和四诊协调中的无障碍功能
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List, Union

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
    """无障碍服务客户端适配器，为小艾智能体提供无障碍能力"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化客户端
        
        Args:
            config: 配置字典，包含无障碍服务的连接信息
        """
        self.config = config or {}
        self.channel = None
        self.stub = None
        self._connect()
        logger.info("小艾智能体无障碍服务客户端初始化完成")
    
    def _connect(self):
        """连接到无障碍服务"""
        try:
            # 从配置获取服务地址
            host = self.config.get('accessibility_service', {}).get('host', 'accessibility-service')
            port = self.config.get('accessibility_service', {}).get('port', 50051)
            
            # 创建gRPC通道
            self.channel = grpc.insecure_channel(f'{host}:{port}')
            
            # 导入生成的proto文件（实际项目中需要正确的导入路径）
            # from accessibility_service.api.grpc import accessibility_pb2_grpc as pb2_grpc
            # self.stub = pb2_grpc.AccessibilityServiceStub(self.channel)
            
            # 模拟stub（实际项目中替换为真实的stub）
            self.stub = MockAccessibilityStub()
            
            logger.info(f"已连接到无障碍服务: {host}:{port}")
            
        except Exception as e:
            logger.error(f"连接无障碍服务失败: {e}")
            self.stub = MockAccessibilityStub()  # 使用模拟客户端作为降级
    
    async def process_voice_input(self, audio_data: bytes, user_id: str, 
                                context: str = "diagnosis", language: str = "zh-CN",
                                dialect: str = "standard") -> Dict[str, Any]:
        """
        处理语音输入，支持语音识别和语音辅助
        
        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 上下文信息
            language: 语言代码
            dialect: 方言代码
            
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"处理语音输入: 用户={user_id}, 上下文={context}")
            
            # 构建请求（实际项目中使用真实的proto消息）
            request = {
                'audio_data': audio_data,
                'user_id': user_id,
                'context': context,
                'language': language,
                'dialect': dialect
            }
            
            # 调用无障碍服务的语音辅助接口
            response = await self._call_voice_assistance(request)
            
            return {
                'recognized_text': response.get('recognized_text', ''),
                'response_text': response.get('response_text', ''),
                'response_audio': response.get('response_audio', b''),
                'confidence': response.get('confidence', 0.0),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"语音输入处理失败: {e}")
            return {
                'recognized_text': '',
                'response_text': f'语音处理失败: {str(e)}',
                'response_audio': b'',
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    async def process_image_input(self, image_data: bytes, user_id: str,
                                image_type: str = "tongue", context: str = "looking_diagnosis") -> Dict[str, Any]:
        """
        处理图像输入，支持图像识别和描述
        
        Args:
            image_data: 图像数据
            user_id: 用户ID
            image_type: 图像类型（舌象、面色等）
            context: 上下文信息
            
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"处理图像输入: 用户={user_id}, 类型={image_type}")
            
            # 构建请求
            request = {
                'image_data': image_data,
                'user_id': user_id,
                'preferences': {
                    'language': 'zh-CN',
                    'detail_level': 'high',
                    'medical_context': True
                },
                'location': {
                    'location_context': context
                }
            }
            
            # 调用无障碍服务的导盲辅助接口（用于图像识别）
            response = await self._call_blind_assistance(request)
            
            return {
                'scene_description': response.get('scene_description', ''),
                'medical_features': self._extract_medical_features(response),
                'navigation_guidance': response.get('navigation_guidance', ''),
                'confidence': response.get('confidence', 0.0),
                'audio_guidance': response.get('audio_guidance', b''),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"图像输入处理失败: {e}")
            return {
                'scene_description': f'图像处理失败: {str(e)}',
                'medical_features': [],
                'navigation_guidance': '',
                'confidence': 0.0,
                'audio_guidance': b'',
                'success': False,
                'error': str(e)
            }
    
    async def process_sign_language_input(self, video_data: bytes, user_id: str,
                                        language: str = "csl") -> Dict[str, Any]:
        """
        处理手语输入，支持手语识别
        
        Args:
            video_data: 视频数据
            user_id: 用户ID
            language: 手语语言代码
            
        Returns:
            处理结果字典
        """
        try:
            logger.info(f"处理手语输入: 用户={user_id}, 语言={language}")
            
            # 构建请求
            request = {
                'video_data': video_data,
                'user_id': user_id,
                'language': language
            }
            
            # 调用无障碍服务的手语识别接口
            response = await self._call_sign_language_recognition(request)
            
            return {
                'recognized_text': response.get('text', ''),
                'confidence': response.get('confidence', 0.0),
                'segments': response.get('segments', []),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"手语输入处理失败: {e}")
            return {
                'recognized_text': f'手语处理失败: {str(e)}',
                'confidence': 0.0,
                'segments': [],
                'success': False,
                'error': str(e)
            }
    
    async def generate_accessible_health_content(self, content: str, user_id: str,
                                               content_type: str = "diagnosis_result",
                                               target_format: str = "audio") -> Dict[str, Any]:
        """
        生成无障碍健康内容
        
        Args:
            content: 原始内容
            user_id: 用户ID
            content_type: 内容类型
            target_format: 目标格式
            
        Returns:
            无障碍内容字典
        """
        try:
            logger.info(f"生成无障碍健康内容: 用户={user_id}, 类型={content_type}")
            
            # 构建请求
            request = {
                'content_id': f"xiaoai_{int(time.time())}",
                'content_type': content_type,
                'user_id': user_id,
                'target_format': target_format,
                'preferences': {
                    'language': 'zh-CN',
                    'voice_type': 'female',
                    'speech_rate': 1.0,
                    'high_contrast': False
                }
            }
            
            # 调用无障碍服务的内容转换接口
            response = await self._call_accessible_content(request)
            
            return {
                'accessible_content': response.get('accessible_content', ''),
                'content_url': response.get('content_url', ''),
                'audio_content': response.get('audio_content', b''),
                'tactile_content': response.get('tactile_content', b''),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"无障碍内容生成失败: {e}")
            return {
                'accessible_content': f'内容转换失败: {str(e)}',
                'content_url': '',
                'audio_content': b'',
                'tactile_content': b'',
                'success': False,
                'error': str(e)
            }
    
    async def provide_screen_reading(self, screen_data: bytes, user_id: str,
                                   context: str = "diagnosis_interface") -> Dict[str, Any]:
        """
        提供屏幕阅读服务
        
        Args:
            screen_data: 屏幕截图数据
            user_id: 用户ID
            context: 上下文信息
            
        Returns:
            屏幕阅读结果字典
        """
        try:
            logger.info(f"提供屏幕阅读: 用户={user_id}, 上下文={context}")
            
            # 构建请求
            request = {
                'screen_data': screen_data,
                'user_id': user_id,
                'context': context,
                'preferences': {
                    'language': 'zh-CN',
                    'detail_level': 'medium',
                    'medical_context': True
                }
            }
            
            # 调用无障碍服务的屏幕阅读接口
            response = await self._call_screen_reading(request)
            
            return {
                'screen_description': response.get('screen_description', ''),
                'ui_elements': response.get('elements', []),
                'audio_description': response.get('audio_description', b''),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"屏幕阅读失败: {e}")
            return {
                'screen_description': f'屏幕阅读失败: {str(e)}',
                'ui_elements': [],
                'audio_description': b'',
                'success': False,
                'error': str(e)
            }
    
    async def manage_accessibility_settings(self, user_id: str, 
                                          preferences: Dict[str, Any],
                                          action: str = "update") -> Dict[str, Any]:
        """
        管理用户的无障碍设置
        
        Args:
            user_id: 用户ID
            preferences: 用户偏好设置
            action: 操作类型（获取/更新）
            
        Returns:
            设置管理结果字典
        """
        try:
            logger.info(f"管理无障碍设置: 用户={user_id}, 操作={action}")
            
            # 构建请求
            request = {
                'user_id': user_id,
                'preferences': preferences,
                'action': action
            }
            
            # 调用无障碍服务的设置管理接口
            response = await self._call_manage_settings(request)
            
            return {
                'current_preferences': response.get('current_preferences', {}),
                'success': response.get('success', False),
                'message': response.get('message', ''),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"无障碍设置管理失败: {e}")
            return {
                'current_preferences': {},
                'success': False,
                'message': f'设置管理失败: {str(e)}',
                'error': str(e)
            }
    
    def _extract_medical_features(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从图像识别结果中提取医学特征"""
        features = []
        
        # 从场景描述中提取医学相关信息
        description = response.get('scene_description', '')
        if '舌' in description:
            features.append({
                'type': 'tongue',
                'description': description,
                'confidence': response.get('confidence', 0.0)
            })
        
        # 从障碍物信息中提取相关特征
        for obstacle in response.get('obstacles', []):
            if obstacle.get('type') in ['medical_feature', 'symptom_indicator']:
                features.append({
                    'type': obstacle.get('type'),
                    'description': f"{obstacle.get('direction')} {obstacle.get('distance')}米处",
                    'confidence': obstacle.get('confidence', 0.0)
                })
        
        return features
    
    # 模拟的服务调用方法（实际项目中替换为真实的gRPC调用）
    async def _call_voice_assistance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用语音辅助服务"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        return {
            'recognized_text': '用户说：我感觉头痛',
            'response_text': '我理解您的症状，让我为您进行详细分析',
            'response_audio': b'mock_audio_data',
            'confidence': 0.95
        }
    
    async def _call_blind_assistance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用导盲辅助服务"""
        await asyncio.sleep(0.1)
        return {
            'scene_description': '检测到舌象图片，舌质偏红，苔薄白',
            'obstacles': [
                {
                    'type': 'medical_feature',
                    'distance': 0.0,
                    'direction': '中央',
                    'confidence': 0.9
                }
            ],
            'navigation_guidance': '请保持图片清晰度以便更好分析',
            'confidence': 0.88,
            'audio_guidance': b'mock_audio_guidance'
        }
    
    async def _call_sign_language_recognition(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用手语识别服务"""
        await asyncio.sleep(0.1)
        return {
            'text': '我需要看医生',
            'confidence': 0.92,
            'segments': [
                {
                    'text': '我',
                    'start_time_ms': 0,
                    'end_time_ms': 500,
                    'confidence': 0.95
                },
                {
                    'text': '需要',
                    'start_time_ms': 500,
                    'end_time_ms': 1000,
                    'confidence': 0.90
                },
                {
                    'text': '看医生',
                    'start_time_ms': 1000,
                    'end_time_ms': 2000,
                    'confidence': 0.91
                }
            ]
        }
    
    async def _call_accessible_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用无障碍内容转换服务"""
        await asyncio.sleep(0.1)
        return {
            'accessible_content': '根据您的症状分析，建议您注意休息，多喝水',
            'content_url': 'https://accessibility.suoke.life/content/123',
            'audio_content': b'mock_audio_content',
            'tactile_content': b'mock_braille_content'
        }
    
    async def _call_screen_reading(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用屏幕阅读服务"""
        await asyncio.sleep(0.1)
        return {
            'screen_description': '当前显示四诊协调界面，包含望闻问切四个选项',
            'elements': [
                {
                    'element_type': 'button',
                    'content': '望诊',
                    'action': 'click',
                    'location': {'x': 100, 'y': 100, 'width': 80, 'height': 40}
                },
                {
                    'element_type': 'button',
                    'content': '闻诊',
                    'action': 'click',
                    'location': {'x': 200, 'y': 100, 'width': 80, 'height': 40}
                }
            ],
            'audio_description': b'mock_screen_audio'
        }
    
    async def _call_manage_settings(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """调用设置管理服务"""
        await asyncio.sleep(0.1)
        return {
            'current_preferences': {
                'language': 'zh-CN',
                'voice_type': 'female',
                'speech_rate': 1.0,
                'high_contrast': False,
                'screen_reader': True
            },
            'success': True,
            'message': '设置更新成功'
        }
    
    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
        logger.info("无障碍服务客户端连接已关闭")


class MockAccessibilityStub:
    """模拟的无障碍服务存根（用于开发和测试）"""
    
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
accessibility_client = AccessibilityClient() 