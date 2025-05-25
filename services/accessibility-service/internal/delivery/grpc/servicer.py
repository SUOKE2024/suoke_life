"""
gRPC服务注册模块
"""
import logging
import asyncio
from typing import Dict, Any

import grpc

from api.grpc import accessibility_pb2 as pb2
from api.grpc import accessibility_pb2_grpc as pb2_grpc
from internal.service.optimized_accessibility_service import OptimizedAccessibilityService
from internal.delivery.grpc.translation_handler import TranslationHandler

logger = logging.getLogger(__name__)


class AccessibilityServicer(pb2_grpc.AccessibilityServiceServicer):
    """无障碍服务gRPC接口实现"""

    def __init__(self, service: OptimizedAccessibilityService):
        """初始化服务实现

        Args:
            service: 核心服务实例
        """
        super().__init__()
        self.service = service
        
        # 初始化各功能处理器
        self.translation_handler = TranslationHandler(service)
        
        logger.info("无障碍服务gRPC接口初始化完成")
    
    # 现有服务方法保持不变，这里只添加翻译服务相关方法
    
    async def SpeechTranslation(self, request, context):
        """语音翻译API"""
        return await self.translation_handler.speech_translation(request, context)
    
    async def StreamingSpeechTranslation(self, request_iterator, context):
        """流式语音翻译API"""
        async for result in self.translation_handler.streaming_speech_translation(request_iterator, context):
            yield result
    
    async def CreateTranslationSession(self, request, context):
        """创建翻译会话API"""
        return await self.translation_handler.create_translation_session(request, context)
    
    async def GetSessionStatus(self, request, context):
        """获取会话状态API"""
        return await self.translation_handler.get_session_status(request, context)
    
    async def GetSupportedLanguages(self, request, context):
        """获取支持的语言和方言API"""
        return await self.translation_handler.get_supported_languages(request, context)


def register_servicer(server: grpc.aio.Server, service: OptimizedAccessibilityService, config: Dict[str, Any]) -> AccessibilityServicer:
    """注册服务到gRPC服务器

    Args:
        server: gRPC服务器
        service: 核心服务实例
        config: 配置信息

    Returns:
        AccessibilityServicer: 服务实现实例
    """
    # 创建服务实现实例
    servicer = AccessibilityServicer(service)
    
    # 注册到服务器
    pb2_grpc.add_AccessibilityServiceServicer_to_server(servicer, server)
    
    logger.info("无障碍服务已注册到gRPC服务器")
    return servicer 