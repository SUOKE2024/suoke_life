#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
无障碍服务的gRPC服务端实现
"""

import logging
import time
from typing import Dict, Any

import grpc
from google.protobuf.json_format import MessageToDict

# 导入生成的proto文件
from api.grpc import accessibility_pb2 as pb2
from api.grpc import accessibility_pb2_grpc as pb2_grpc

# 导入服务实现
from internal.service.accessibility_service import AccessibilityService


logger = logging.getLogger(__name__)


class AccessibilityServicer(pb2_grpc.AccessibilityServiceServicer):
    """无障碍服务的gRPC实现类"""
    
    def __init__(self, service: AccessibilityService):
        """
        初始化服务
        
        Args:
            service: 无障碍服务实例
        """
        self.service = service
        logger.info("无障碍服务gRPC接口初始化完成")
    
    def _log_request(self, method_name: str, user_id: str) -> float:
        """记录请求开始，并返回开始时间"""
        start_time = time.time()
        logger.info(f"收到{method_name}请求: 用户={user_id}")
        return start_time
    
    def _log_response(self, method_name: str, user_id: str, start_time: float) -> None:
        """记录请求完成"""
        elapsed_time = time.time() - start_time
        logger.info(f"{method_name}请求处理完成: 用户={user_id}, 耗时={elapsed_time:.2f}秒")
    
    def _handle_error(self, method_name: str, user_id: str, error: Exception) -> None:
        """处理并记录错误"""
        logger.error(f"{method_name}请求处理失败: 用户={user_id}, 错误={str(error)}", exc_info=True)
        return grpc.StatusCode.INTERNAL, f"服务内部错误: {str(error)}"
    
    def BlindAssistance(self, request, context):
        """
        导盲服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("BlindAssistance", user_id)
        
        try:
            # 将Protobuf对象转换为Python字典
            preferences = MessageToDict(request.preferences, preserving_proto_field_name=True)
            location = MessageToDict(request.location, preserving_proto_field_name=True)
            
            # 调用服务方法
            result = self.service.blind_assistance(
                image_data=request.image_data,
                user_id=user_id,
                preferences=preferences,
                location=location
            )
            
            # 创建响应
            response = pb2.BlindAssistanceResponse(
                scene_description=result.get("scene_description", ""),
                navigation_guidance=result.get("navigation_guidance", ""),
                confidence=result.get("confidence", 0.0),
                audio_guidance=result.get("audio_guidance", b"")
            )
            
            # 添加障碍物信息
            for obstacle_dict in result.get("obstacles", []):
                obstacle = pb2.Obstacle(
                    type=obstacle_dict.get("type", ""),
                    distance=obstacle_dict.get("distance", 0.0),
                    direction=obstacle_dict.get("direction", ""),
                    confidence=obstacle_dict.get("confidence", 0.0)
                )
                response.obstacles.append(obstacle)
            
            self._log_response("BlindAssistance", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("BlindAssistance", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.BlindAssistanceResponse()
    
    def SignLanguageRecognition(self, request, context):
        """
        手语识别服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("SignLanguageRecognition", user_id)
        
        try:
            # 调用服务方法
            result = self.service.sign_language_recognition(
                video_data=request.video_data,
                user_id=user_id,
                language=request.language
            )
            
            # 创建响应
            response = pb2.SignLanguageResponse(
                text=result.get("text", ""),
                confidence=result.get("confidence", 0.0),
            )
            
            # 添加分段信息
            for segment_dict in result.get("segments", []):
                segment = pb2.SignSegment(
                    text=segment_dict.get("text", ""),
                    start_time_ms=segment_dict.get("start_time_ms", 0),
                    end_time_ms=segment_dict.get("end_time_ms", 0),
                    confidence=segment_dict.get("confidence", 0.0)
                )
                response.segments.append(segment)
            
            self._log_response("SignLanguageRecognition", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("SignLanguageRecognition", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.SignLanguageResponse()
    
    def ScreenReading(self, request, context):
        """
        屏幕阅读服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("ScreenReading", user_id)
        
        try:
            # 将Protobuf对象转换为Python字典
            preferences = MessageToDict(request.preferences, preserving_proto_field_name=True)
            
            # 调用服务方法
            result = self.service.screen_reading(
                screen_data=request.screen_data,
                user_id=user_id,
                context=request.context,
                preferences=preferences
            )
            
            # 创建响应
            response = pb2.ScreenReadingResponse(
                screen_description=result.get("screen_description", ""),
                audio_description=result.get("audio_description", b"")
            )
            
            # 添加UI元素信息
            for element_dict in result.get("elements", []):
                location_dict = element_dict.get("location", {})
                location = pb2.BoundingBox(
                    x=location_dict.get("x", 0.0),
                    y=location_dict.get("y", 0.0),
                    width=location_dict.get("width", 0.0),
                    height=location_dict.get("height", 0.0)
                )
                
                element = pb2.UIElement(
                    element_type=element_dict.get("element_type", ""),
                    content=element_dict.get("content", ""),
                    action=element_dict.get("action", ""),
                    location=location
                )
                response.elements.append(element)
            
            self._log_response("ScreenReading", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("ScreenReading", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.ScreenReadingResponse()
    
    def VoiceAssistance(self, request, context):
        """
        语音辅助服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("VoiceAssistance", user_id)
        
        try:
            # 调用服务方法
            result = self.service.voice_assistance(
                audio_data=request.audio_data,
                user_id=user_id,
                context=request.context,
                language=request.language,
                dialect=request.dialect
            )
            
            # 创建响应
            response = pb2.VoiceAssistanceResponse(
                recognized_text=result.get("recognized_text", ""),
                response_text=result.get("response_text", ""),
                response_audio=result.get("response_audio", b""),
                confidence=result.get("confidence", 0.0)
            )
            
            self._log_response("VoiceAssistance", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("VoiceAssistance", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.VoiceAssistanceResponse()
    
    def AccessibleContent(self, request, context):
        """
        健康内容无障碍转换服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("AccessibleContent", user_id)
        
        try:
            # 将Protobuf对象转换为Python字典
            preferences = MessageToDict(request.preferences, preserving_proto_field_name=True)
            
            # 调用服务方法
            result = self.service.accessible_content(
                content_id=request.content_id,
                content_type=request.content_type,
                user_id=user_id,
                target_format=request.target_format,
                preferences=preferences
            )
            
            # 创建响应
            response = pb2.AccessibleContentResponse(
                accessible_content=result.get("accessible_content", ""),
                content_url=result.get("content_url", ""),
                audio_content=result.get("audio_content", b""),
                tactile_content=result.get("tactile_content", b"")
            )
            
            self._log_response("AccessibleContent", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("AccessibleContent", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.AccessibleContentResponse()
    
    def ManageSettings(self, request, context):
        """
        无障碍设置管理服务实现
        
        Args:
            request: 请求对象
            context: gRPC上下文
            
        Returns:
            响应对象
        """
        user_id = request.user_id
        start_time = self._log_request("ManageSettings", user_id)
        
        try:
            # 将Protobuf对象转换为Python字典
            preferences = MessageToDict(request.preferences, preserving_proto_field_name=True)
            
            # 调用服务方法
            result = self.service.manage_settings(
                user_id=user_id,
                preferences=preferences,
                action=request.action
            )
            
            # 创建响应
            response = pb2.SettingsResponse(
                success=result.get("success", False),
                message=result.get("message", "")
            )
            
            # 设置当前偏好
            current_preferences = result.get("current_preferences", {})
            if current_preferences:
                response.current_preferences.font_size = current_preferences.get("font_size", "")
                response.current_preferences.high_contrast = current_preferences.get("high_contrast", False)
                response.current_preferences.voice_type = current_preferences.get("voice_type", "")
                response.current_preferences.speech_rate = current_preferences.get("speech_rate", 1.0)
                response.current_preferences.language = current_preferences.get("language", "")
                response.current_preferences.dialect = current_preferences.get("dialect", "")
                response.current_preferences.screen_reader = current_preferences.get("screen_reader", False)
                response.current_preferences.sign_language = current_preferences.get("sign_language", False)
                
                # 添加启用的功能
                for feature in current_preferences.get("enabled_features", []):
                    response.current_preferences.enabled_features.append(feature)
            
            self._log_response("ManageSettings", user_id, start_time)
            return response
            
        except Exception as e:
            status_code, error_message = self._handle_error("ManageSettings", user_id, e)
            context.set_code(status_code)
            context.set_details(error_message)
            return pb2.SettingsResponse() 