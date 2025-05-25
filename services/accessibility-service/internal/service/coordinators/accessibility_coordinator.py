#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
无障碍服务协调器
统一管理和协调所有无障碍相关的服务
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timezone

from ..interfaces import (
    IBlindAssistanceService, ISignLanguageService, IScreenReadingService,
    IVoiceAssistanceService, IContentConversionService
)
from ..factories import AccessibilityServiceFactory
from ..decorators import performance_monitor, error_handler, trace

logger = logging.getLogger(__name__)


class AccessibilityServiceCoordinator:
    """
    无障碍服务协调器
    提供统一的API接口，协调各个子服务的工作
    """
    
    def __init__(self, service_factory: AccessibilityServiceFactory):
        """
        初始化服务协调器
        
        Args:
            service_factory: 无障碍服务工厂
        """
        self.service_factory = service_factory
        
        # 服务实例缓存
        self._blind_assistance_service: Optional[IBlindAssistanceService] = None
        self._sign_language_service: Optional[ISignLanguageService] = None
        self._screen_reading_service: Optional[IScreenReadingService] = None
        self._voice_assistance_service: Optional[IVoiceAssistanceService] = None
        self._content_conversion_service: Optional[IContentConversionService] = None
        
        # 协调器状态
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        
        logger.info("无障碍服务协调器初始化完成")
    
    async def initialize(self):
        """初始化协调器"""
        if self._initialized:
            return
        
        try:
            # 初始化服务工厂
            await self.service_factory.initialize()
            
            # 预加载核心服务
            await self._preload_services()
            
            self._initialized = True
            logger.info("无障碍服务协调器初始化成功")
            
        except Exception as e:
            logger.error(f"无障碍服务协调器初始化失败: {str(e)}")
            raise
    
    async def _preload_services(self):
        """预加载核心服务"""
        try:
            # 预加载导盲服务
            self._blind_assistance_service = await self.service_factory.create_blind_assistance_service()
            
            # 预加载语音辅助服务
            self._voice_assistance_service = await self.service_factory.create_voice_assistance_service()
            
            logger.info("核心服务预加载完成")
            
        except Exception as e:
            logger.warning(f"核心服务预加载失败: {str(e)}")
    
    # ==================== 导盲服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.analyze_scene")
    @error_handler(operation_name="coordinator.analyze_scene")
    @trace(operation_name="analyze_scene", kind="server")
    async def analyze_scene(self, image_data: bytes, user_id: str, 
                          preferences: Dict, location: Dict) -> Dict:
        """
        分析场景并提供导航建议
        
        Args:
            image_data: 图像数据
            user_id: 用户ID
            preferences: 用户偏好
            location: 位置信息
        
        Returns:
            场景分析结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取导盲服务
            if not self._blind_assistance_service:
                self._blind_assistance_service = await self.service_factory.create_blind_assistance_service()
            
            # 调用导盲服务
            result = await self._blind_assistance_service.analyze_scene(
                image_data, user_id, preferences, location
            )
            
            # 添加协调器信息
            result['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"场景分析协调失败: {str(e)}")
            raise
    
    @performance_monitor(operation_name="coordinator.detect_obstacles")
    @error_handler(operation_name="coordinator.detect_obstacles")
    @trace(operation_name="detect_obstacles", kind="server")
    async def detect_obstacles(self, image_data: bytes, 
                             confidence_threshold: float = 0.7) -> List[Dict]:
        """
        检测障碍物
        
        Args:
            image_data: 图像数据
            confidence_threshold: 置信度阈值
        
        Returns:
            障碍物检测结果列表
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取导盲服务
            if not self._blind_assistance_service:
                self._blind_assistance_service = await self.service_factory.create_blind_assistance_service()
            
            # 调用导盲服务
            result = await self._blind_assistance_service.detect_obstacles(
                image_data, confidence_threshold
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"障碍物检测协调失败: {str(e)}")
            raise
    
    # ==================== 语音辅助服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.process_voice_command")
    @error_handler(operation_name="coordinator.process_voice_command")
    @trace(operation_name="process_voice_command", kind="server")
    async def process_voice_command(self, audio_data: bytes, user_id: str,
                                  context: str, language: str, dialect: str) -> Dict:
        """
        处理语音命令
        
        Args:
            audio_data: 音频数据
            user_id: 用户ID
            context: 上下文信息
            language: 语言
            dialect: 方言
        
        Returns:
            语音命令处理结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取语音辅助服务
            if not self._voice_assistance_service:
                self._voice_assistance_service = await self.service_factory.create_voice_assistance_service()
            
            # 调用语音辅助服务
            result = await self._voice_assistance_service.process_voice_command(
                audio_data, user_id, context, language, dialect
            )
            
            # 根据意图协调其他服务
            await self._coordinate_voice_response(result, user_id)
            
            # 添加协调器信息
            result['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"语音命令处理协调失败: {str(e)}")
            raise
    
    @performance_monitor(operation_name="coordinator.text_to_speech")
    @error_handler(operation_name="coordinator.text_to_speech")
    @trace(operation_name="text_to_speech", kind="server")
    async def text_to_speech(self, text: str, language: str, 
                           voice_preferences: Dict) -> bytes:
        """
        文本转语音
        
        Args:
            text: 要转换的文本
            language: 语言
            voice_preferences: 语音偏好设置
        
        Returns:
            音频数据
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取语音辅助服务
            if not self._voice_assistance_service:
                self._voice_assistance_service = await self.service_factory.create_voice_assistance_service()
            
            # 调用语音辅助服务
            result = await self._voice_assistance_service.text_to_speech(
                text, language, voice_preferences
            )
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"文本转语音协调失败: {str(e)}")
            raise
    
    # ==================== 手语识别服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.recognize_sign_language")
    @error_handler(operation_name="coordinator.recognize_sign_language")
    @trace(operation_name="recognize_sign_language", kind="server")
    async def recognize_sign_language(self, video_data: bytes, 
                                    language: str, user_id: str) -> Dict:
        """
        识别手语
        
        Args:
            video_data: 视频数据
            language: 手语语言
            user_id: 用户ID
        
        Returns:
            手语识别结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取手语识别服务
            if not self._sign_language_service:
                self._sign_language_service = await self.service_factory.create_sign_language_service()
            
            # 调用手语识别服务
            result = await self._sign_language_service.recognize_sign_language(
                video_data, language, user_id
            )
            
            # 添加协调器信息
            result['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"手语识别协调失败: {str(e)}")
            raise
    
    # ==================== 屏幕阅读服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.read_screen")
    @error_handler(operation_name="coordinator.read_screen")
    @trace(operation_name="read_screen", kind="server")
    async def read_screen(self, screen_data: bytes, user_id: str, 
                         context: str, preferences: Dict) -> Dict:
        """
        读取屏幕内容
        
        Args:
            screen_data: 屏幕数据
            user_id: 用户ID
            context: 上下文
            preferences: 用户偏好
        
        Returns:
            屏幕阅读结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取屏幕阅读服务
            if not self._screen_reading_service:
                self._screen_reading_service = await self.service_factory.create_screen_reading_service()
            
            # 调用屏幕阅读服务
            result = await self._screen_reading_service.read_screen(
                screen_data, user_id, context, preferences
            )
            
            # 如果需要语音输出，协调语音服务
            if preferences.get('voice_output', True):
                await self._coordinate_screen_reading_voice(result, preferences)
            
            # 添加协调器信息
            result['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"屏幕阅读协调失败: {str(e)}")
            raise
    
    # ==================== 内容转换服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.convert_content")
    @error_handler(operation_name="coordinator.convert_content")
    @trace(operation_name="convert_content", kind="server")
    async def convert_content(self, content_id: str, content_type: str,
                            target_format: str, user_id: str, 
                            preferences: Dict) -> Dict:
        """
        转换内容格式
        
        Args:
            content_id: 内容ID
            content_type: 内容类型
            target_format: 目标格式
            user_id: 用户ID
            preferences: 用户偏好
        
        Returns:
            内容转换结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            # 获取内容转换服务
            if not self._content_conversion_service:
                self._content_conversion_service = await self.service_factory.create_content_conversion_service()
            
            # 调用内容转换服务
            result = await self._content_conversion_service.convert_content(
                content_id, content_type, target_format, user_id, preferences
            )
            
            # 添加协调器信息
            result['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"内容转换协调失败: {str(e)}")
            raise
    
    # ==================== 协调逻辑 ====================
    
    async def _coordinate_voice_response(self, voice_result: Dict, user_id: str):
        """
        协调语音响应，根据意图调用其他服务
        
        Args:
            voice_result: 语音处理结果
            user_id: 用户ID
        """
        try:
            intent = voice_result.get('intent', {}).get('intent', '')
            response = voice_result.get('response', {})
            
            # 根据意图协调其他服务
            if intent == 'find_facility':
                # 如果是查找设施，可以协调地图服务等
                logger.debug(f"协调查找设施服务: 用户 {user_id}")
                
            elif intent == 'navigation':
                # 如果是导航，可以协调导盲服务
                logger.debug(f"协调导航服务: 用户 {user_id}")
                
            elif intent == 'read_screen':
                # 如果是屏幕阅读，协调屏幕阅读服务
                logger.debug(f"协调屏幕阅读服务: 用户 {user_id}")
            
        except Exception as e:
            logger.warning(f"语音响应协调失败: {str(e)}")
    
    async def _coordinate_screen_reading_voice(self, screen_result: Dict, 
                                             preferences: Dict):
        """
        协调屏幕阅读的语音输出
        
        Args:
            screen_result: 屏幕阅读结果
            preferences: 用户偏好
        """
        try:
            text_content = screen_result.get('text_content', '')
            if text_content and preferences.get('voice_output', True):
                # 获取语音偏好
                voice_preferences = preferences.get('voice', {})
                language = preferences.get('language', 'zh-CN')
                
                # 生成语音
                if not self._voice_assistance_service:
                    self._voice_assistance_service = await self.service_factory.create_voice_assistance_service()
                
                audio_data = await self._voice_assistance_service.text_to_speech(
                    text_content, language, voice_preferences
                )
                
                # 将语音数据添加到结果中
                screen_result['audio_output'] = {
                    'data': audio_data,
                    'language': language,
                    'preferences': voice_preferences
                }
                
        except Exception as e:
            logger.warning(f"屏幕阅读语音协调失败: {str(e)}")
    
    # ==================== 综合服务接口 ====================
    
    @performance_monitor(operation_name="coordinator.comprehensive_assistance")
    @error_handler(operation_name="coordinator.comprehensive_assistance")
    @trace(operation_name="comprehensive_assistance", kind="server")
    async def comprehensive_assistance(self, request_data: Dict, user_id: str) -> Dict:
        """
        综合无障碍辅助
        根据请求类型协调多个服务
        
        Args:
            request_data: 请求数据
            user_id: 用户ID
        
        Returns:
            综合辅助结果
        """
        if not self._initialized:
            await self.initialize()
        
        self._request_count += 1
        
        try:
            request_type = request_data.get('type', '')
            results = {}
            
            # 根据请求类型协调多个服务
            if request_type == 'scene_analysis_with_voice':
                # 场景分析 + 语音播报
                image_data = request_data.get('image_data')
                preferences = request_data.get('preferences', {})
                location = request_data.get('location', {})
                
                # 场景分析
                scene_result = await self.analyze_scene(
                    image_data, user_id, preferences, location
                )
                results['scene_analysis'] = scene_result
                
                # 语音播报
                advice_text = scene_result.get('navigation_advice', {}).get('primary_advice', '')
                if advice_text:
                    voice_preferences = preferences.get('voice', {})
                    language = preferences.get('language', 'zh-CN')
                    
                    audio_data = await self.text_to_speech(
                        advice_text, language, voice_preferences
                    )
                    results['voice_output'] = audio_data
            
            elif request_type == 'voice_controlled_navigation':
                # 语音控制导航
                audio_data = request_data.get('audio_data')
                context = request_data.get('context', '')
                language = request_data.get('language', 'zh-CN')
                dialect = request_data.get('dialect', 'standard')
                
                # 语音命令处理
                voice_result = await self.process_voice_command(
                    audio_data, user_id, context, language, dialect
                )
                results['voice_command'] = voice_result
                
                # 根据意图执行相应操作
                intent = voice_result.get('intent', {}).get('intent', '')
                if intent == 'find_facility':
                    # 这里可以调用地图服务等
                    results['facility_search'] = {'status': 'initiated'}
            
            # 添加协调器信息
            results['coordinator'] = {
                'service': 'AccessibilityServiceCoordinator',
                'request_type': request_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            return results
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"综合辅助协调失败: {str(e)}")
            raise
    
    # ==================== 状态和管理接口 ====================
    
    async def get_status(self) -> Dict[str, Any]:
        """
        获取协调器状态
        
        Returns:
            协调器状态信息
        """
        try:
            # 获取服务工厂状态
            factory_status = await self.service_factory.get_service_status()
            
            return {
                'coordinator': {
                    'name': 'AccessibilityServiceCoordinator',
                    'initialized': self._initialized,
                    'request_count': self._request_count,
                    'error_count': self._error_count,
                    'error_rate': self._error_count / max(self._request_count, 1),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                'services': factory_status,
                'loaded_services': {
                    'blind_assistance': self._blind_assistance_service is not None,
                    'sign_language': self._sign_language_service is not None,
                    'screen_reading': self._screen_reading_service is not None,
                    'voice_assistance': self._voice_assistance_service is not None,
                    'content_conversion': self._content_conversion_service is not None
                }
            }
            
        except Exception as e:
            logger.error(f"获取协调器状态失败: {str(e)}")
            return {
                'coordinator': {
                    'name': 'AccessibilityServiceCoordinator',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            }
    
    async def reload_service(self, service_name: str):
        """
        重新加载指定服务
        
        Args:
            service_name: 服务名称
        """
        try:
            # 清除本地缓存
            if service_name == 'blind_assistance':
                self._blind_assistance_service = None
            elif service_name == 'sign_language':
                self._sign_language_service = None
            elif service_name == 'screen_reading':
                self._screen_reading_service = None
            elif service_name == 'voice_assistance':
                self._voice_assistance_service = None
            elif service_name == 'content_conversion':
                self._content_conversion_service = None
            
            # 重新加载服务配置
            await self.service_factory.reload_service_config(f"{service_name.title().replace('_', '')}ServiceImpl")
            
            logger.info(f"服务重新加载完成: {service_name}")
            
        except Exception as e:
            logger.error(f"服务重新加载失败: {service_name}, 错误: {str(e)}")
            raise
    
    async def cleanup(self):
        """清理协调器资源"""
        try:
            # 清理服务工厂
            await self.service_factory.cleanup()
            
            # 清除服务缓存
            self._blind_assistance_service = None
            self._sign_language_service = None
            self._screen_reading_service = None
            self._voice_assistance_service = None
            self._content_conversion_service = None
            
            self._initialized = False
            logger.info("无障碍服务协调器清理完成")
            
        except Exception as e:
            logger.error(f"无障碍服务协调器清理失败: {str(e)}")
            raise 