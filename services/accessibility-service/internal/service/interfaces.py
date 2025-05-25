#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
无障碍服务接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
import asyncio


class IBlindAssistanceService(ABC):
    """导盲服务接口"""
    
    @abstractmethod
    async def analyze_scene(self, image_data: bytes, user_id: str, 
                          preferences: Dict, location: Dict) -> Dict:
        """分析场景并提供导航建议"""
        pass
    
    @abstractmethod
    async def detect_obstacles(self, image_data: bytes, 
                             confidence_threshold: float = 0.7) -> List[Dict]:
        """检测障碍物"""
        pass


class ISignLanguageService(ABC):
    """手语识别服务接口"""
    
    @abstractmethod
    async def recognize_sign_language(self, video_data: bytes, 
                                    language: str, user_id: str) -> Dict:
        """识别手语"""
        pass
    
    @abstractmethod
    async def get_supported_languages(self) -> List[str]:
        """获取支持的手语语言"""
        pass


class IScreenReadingService(ABC):
    """屏幕阅读服务接口"""
    
    @abstractmethod
    async def read_screen(self, screen_data: bytes, user_id: str, 
                         context: str, preferences: Dict) -> Dict:
        """读取屏幕内容"""
        pass
    
    @abstractmethod
    async def extract_ui_elements(self, screen_data: bytes) -> List[Dict]:
        """提取UI元素"""
        pass


class IVoiceAssistanceService(ABC):
    """语音辅助服务接口"""
    
    @abstractmethod
    async def process_voice_command(self, audio_data: bytes, user_id: str,
                                  context: str, language: str, dialect: str) -> Dict:
        """处理语音命令"""
        pass
    
    @abstractmethod
    async def text_to_speech(self, text: str, language: str, 
                           voice_preferences: Dict) -> bytes:
        """文本转语音"""
        pass


class IContentConversionService(ABC):
    """内容转换服务接口"""
    
    @abstractmethod
    async def convert_content(self, content_id: str, content_type: str,
                            target_format: str, user_id: str, 
                            preferences: Dict) -> Dict:
        """转换内容格式"""
        pass
    
    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        pass


class ITranslationService(ABC):
    """翻译服务接口"""
    
    @abstractmethod
    async def translate_speech(self, audio_data: bytes, source_lang: str,
                             target_lang: str, user_id: str) -> Dict:
        """语音翻译"""
        pass
    
    @abstractmethod
    async def stream_translation(self, audio_stream: AsyncGenerator[bytes, None],
                               source_lang: str, target_lang: str, 
                               user_id: str) -> AsyncGenerator[Dict, None]:
        """流式翻译"""
        pass


class ISettingsService(ABC):
    """设置管理服务接口"""
    
    @abstractmethod
    async def get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好"""
        pass
    
    @abstractmethod
    async def update_user_preferences(self, user_id: str, 
                                    preferences: Dict) -> Dict:
        """更新用户偏好"""
        pass


class IModelManager(ABC):
    """AI模型管理接口"""
    
    @abstractmethod
    async def load_model(self, model_name: str, model_config: Dict) -> Any:
        """加载模型"""
        pass
    
    @abstractmethod
    async def unload_model(self, model_name: str) -> bool:
        """卸载模型"""
        pass
    
    @abstractmethod
    async def get_model_status(self, model_name: str) -> Dict:
        """获取模型状态"""
        pass


class IHealthMonitor(ABC):
    """健康监控接口"""
    
    @abstractmethod
    async def check_health(self) -> Dict:
        """健康检查"""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict:
        """获取指标"""
        pass


class ICacheManager(ABC):
    """缓存管理接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        pass 