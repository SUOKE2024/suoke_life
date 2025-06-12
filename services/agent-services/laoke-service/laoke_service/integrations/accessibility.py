"""老克智能体无障碍服务集成模块"""

import asyncio
import aiohttp
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from ..core.config import get_config
from ..core.exceptions import AccessibilityServiceException
from ..core.logging import get_logger, log_error


class AccessibilityFeature(Enum):
    """无障碍功能类型"""
    TEXT_TO_SPEECH = "text_to_speech"  # 文本转语音
    SPEECH_TO_TEXT = "speech_to_text"  # 语音转文本
    LARGE_TEXT = "large_text"  # 大字体
    HIGH_CONTRAST = "high_contrast"  # 高对比度
    SCREEN_READER = "screen_reader"  # 屏幕阅读器
    VOICE_NAVIGATION = "voice_navigation"  # 语音导航
    SIMPLIFIED_UI = "simplified_ui"  # 简化界面
    BRAILLE_SUPPORT = "braille_support"  # 盲文支持


class TTSVoice(Enum):
    """语音合成声音类型"""
    MALE_STANDARD = "male_standard"
    FEMALE_STANDARD = "female_standard"
    MALE_WARM = "male_warm"
    FEMALE_WARM = "female_warm"
    CHILD_FRIENDLY = "child_friendly"


class TTSSpeed(Enum):
    """语音合成语速"""
    VERY_SLOW = "very_slow"  # 0.5x
    SLOW = "slow"  # 0.75x
    NORMAL = "normal"  # 1.0x
    FAST = "fast"  # 1.25x
    VERY_FAST = "very_fast"  # 1.5x


@dataclass
class TTSRequest:
    """文本转语音请求"""
    text: str
    voice: TTSVoice = TTSVoice.FEMALE_STANDARD
    speed: TTSSpeed = TTSSpeed.NORMAL
    language: str = "zh-CN"
    format: str = "mp3"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TTSResponse:
    """文本转语音响应"""
    audio_url: str
    audio_data: Optional[bytes] = None
    duration_seconds: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class STTRequest:
    """语音转文本请求"""
    audio_url: Optional[str] = None
    audio_data: Optional[bytes] = None
    language: str = "zh-CN"
    format: str = "wav"
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class STTResponse:
    """语音转文本响应"""
    text: str
    confidence: float
    alternatives: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AccessibilityProfile:
    """用户无障碍配置文件"""
    user_id: str
    enabled_features: List[AccessibilityFeature]
    tts_preferences: Optional[Dict[str, Any]] = None
    ui_preferences: Optional[Dict[str, Any]] = None
    navigation_preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class AccessibilityClient:
    """无障碍服务客户端"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("accessibility_client")
        self.base_url = self.config.external_services.accessibility_service_url
        self.api_key = self.config.external_services.accessibility_service_api_key
        self.timeout = self.config.external_services.accessibility_service_timeout
        self.enabled = self.config.external_services.accessibility_service_enabled
        
        # 缓存用户配置
        self._user_profiles: Dict[str, AccessibilityProfile] = {}
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求到无障碍服务"""
        if not self.enabled:
            raise AccessibilityServiceException(
                "Accessibility service is disabled",
                conversion_type="general"
            )
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Laoke-Agent/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                if files:
                    # 文件上传
                    form_data = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form_data.add_field(key, json.dumps(value) if isinstance(value, (dict, list)) else str(value))
                    
                    for key, file_data in files.items():
                        form_data.add_field(key, file_data)
                    
                    async with session.request(method, url, data=form_data, headers={k: v for k, v in headers.items() if k!="Content-Type"}) as response:
                        response.raise_for_status()
                        return await response.json()
                else:
                    # JSON请求
                    async with session.request(method, url, json=data, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
                        
        except aiohttp.ClientTimeout:
            raise AccessibilityServiceException(
                f"Accessibility service timeout after {self.timeout}s",
                conversion_type="timeout"
            )
        except aiohttp.ClientError as e:
            raise AccessibilityServiceException(
                f"Accessibility service request failed: {e}",
                conversion_type="network"
            )
        except Exception as e:
            log_error(e, {"endpoint": endpoint, "method": method})
            raise AccessibilityServiceException(
                f"Unexpected error in accessibility service: {e}",
                conversion_type="general"
            )
    
    async def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """文本转语音"""
        try:
            data = {
                "text": request.text,
                "voice": request.voice.value,
                "speed": request.speed.value,
                "language": request.language,
                "format": request.format
            }
            
            if request.metadata:
                data["metadata"] = request.metadata
            
            response = await self._make_request("POST", "/tts", data=data)
            
            return TTSResponse(
                audio_url=response["audio_url"],
                audio_data=response.get("audio_data"),
                duration_seconds=response.get("duration_seconds"),
                metadata=response.get("metadata")
            )
            
        except Exception as e:
            if not isinstance(e, AccessibilityServiceException):
                e = AccessibilityServiceException(
                    f"TTS conversion failed: {e}",
                    conversion_type="tts"
                )
            raise e
    
    async def speech_to_text(self, request: STTRequest) -> STTResponse:
        """语音转文本"""
        try:
            data = {
                "language": request.language,
                "format": request.format
            }
            
            if request.metadata:
                data["metadata"] = request.metadata
            
            files = {}
            if request.audio_url:
                data["audio_url"] = request.audio_url
            elif request.audio_data:
                files["audio"] = request.audio_data
            else:
                raise AccessibilityServiceException(
                    "Either audio_url or audio_data must be provided",
                    conversion_type="stt"
                )
            
            response = await self._make_request("POST", "/stt", data=data, files=files)
            
            return STTResponse(
                text=response["text"],
                confidence=response["confidence"],
                alternatives=response.get("alternatives"),
                metadata=response.get("metadata")
            )
            
        except Exception as e:
            if not isinstance(e, AccessibilityServiceException):
                e = AccessibilityServiceException(
                    f"STT conversion failed: {e}",
                    conversion_type="stt"
                )
            raise e
    
    async def get_user_profile(self, user_id: str) -> Optional[AccessibilityProfile]:
        """获取用户无障碍配置"""
        # 先从缓存获取
        if user_id in self._user_profiles:
            return self._user_profiles[user_id]
        
        try:
            response = await self._make_request("GET", f"/users/{user_id}/profile")
            
            profile = AccessibilityProfile(
                user_id=user_id,
                enabled_features=[AccessibilityFeature(f) for f in response["enabled_features"]],
                tts_preferences=response.get("tts_preferences"),
                ui_preferences=response.get("ui_preferences"),
                navigation_preferences=response.get("navigation_preferences"),
                metadata=response.get("metadata")
            )
            
            # 缓存结果
            self._user_profiles[user_id] = profile
            
            return profile
            
        except aiohttp.ClientResponseError as e:
            if e.status==404:
                return None
            raise AccessibilityServiceException(
                f"Failed to get user profile: {e}",
                conversion_type="profile"
            )
        except Exception as e:
            if not isinstance(e, AccessibilityServiceException):
                e = AccessibilityServiceException(
                    f"Failed to get user profile: {e}",
                    conversion_type="profile"
                )
            raise e
    
    async def update_user_profile(self, profile: AccessibilityProfile) -> AccessibilityProfile:
        """更新用户无障碍配置"""
        try:
            data = {
                "enabled_features": [f.value for f in profile.enabled_features],
                "tts_preferences": profile.tts_preferences,
                "ui_preferences": profile.ui_preferences,
                "navigation_preferences": profile.navigation_preferences,
                "metadata": profile.metadata
            }
            
            response = await self._make_request(
                "PUT",
                f"/users/{profile.user_id}/profile",
                data=data
            )
            
            updated_profile = AccessibilityProfile(
                user_id=profile.user_id,
                enabled_features=[AccessibilityFeature(f) for f in response["enabled_features"]],
                tts_preferences=response.get("tts_preferences"),
                ui_preferences=response.get("ui_preferences"),
                navigation_preferences=response.get("navigation_preferences"),
                metadata=response.get("metadata")
            )
            
            # 更新缓存
            self._user_profiles[profile.user_id] = updated_profile
            
            return updated_profile
            
        except Exception as e:
            if not isinstance(e, AccessibilityServiceException):
                e = AccessibilityServiceException(
                    f"Failed to update user profile: {e}",
                    conversion_type="profile"
                )
            raise e
    
    async def convert_response_for_user(
        self,
        user_id: str,
        text_response: str,
        preferred_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """根据用户需求转换响应格式"""
        try:
            # 获取用户配置
            profile = await self.get_user_profile(user_id)
            
            result = {
                "text": text_response,
                "accessibility_features": []
            }
            
            if not profile:
                return result
            
            # 根据用户需求提供不同格式
            if AccessibilityFeature.TEXT_TO_SPEECH in profile.enabled_features:
                # 生成语音版本
                tts_request = TTSRequest(
                    text=text_response,
                    voice=TTSVoice(profile.tts_preferences.get("voice", TTSVoice.FEMALE_STANDARD.value)) if profile.tts_preferences else TTSVoice.FEMALE_STANDARD,
                    speed=TTSSpeed(profile.tts_preferences.get("speed", TTSSpeed.NORMAL.value)) if profile.tts_preferences else TTSSpeed.NORMAL,
                    language=profile.tts_preferences.get("language", "zh-CN") if profile.tts_preferences else "zh-CN"
                )
                
                tts_response = await self.text_to_speech(tts_request)
                result["audio_url"] = tts_response.audio_url
                result["audio_duration"] = tts_response.duration_seconds
                result["accessibility_features"].append("text_to_speech")
            
            if AccessibilityFeature.LARGE_TEXT in profile.enabled_features:
                # 添加大字体标记
                result["large_text"] = True
                result["accessibility_features"].append("large_text")
            
            if AccessibilityFeature.HIGH_CONTRAST in profile.enabled_features:
                # 添加高对比度标记
                result["high_contrast"] = True
                result["accessibility_features"].append("high_contrast")
            
            if AccessibilityFeature.SIMPLIFIED_UI in profile.enabled_features:
                # 简化界面标记
                result["simplified_ui"] = True
                result["accessibility_features"].append("simplified_ui")
            
            if AccessibilityFeature.SCREEN_READER in profile.enabled_features:
                # 屏幕阅读器优化
                result["screen_reader_optimized"] = True
                result["accessibility_features"].append("screen_reader")
                
                # 添加结构化数据
                result["structured_content"] = self._create_structured_content(text_response)
            
            return result
            
        except Exception as e:
            self.logger.error(f"转换响应格式失败: {e}")
            # 如果转换失败，返回原始文本
            return {"text": text_response, "accessibility_features": []}
    
    def _create_structured_content(self, text: str) -> Dict[str, Any]:
        """为屏幕阅读器创建结构化内容"""
        # 简单的结构化处理
        lines = text.split('\n')
        structured = {
            "type": "document",
            "content": [],
            "summary": text[:100] + "..." if len(text) > 100 else text
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测标题（简单的启发式检测）
            if line.endswith('：') or line.endswith(':'):
                structured["content"].append({
                    "type": "heading",
                    "level": 2,
                    "text": line
                })
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                structured["content"].append({
                    "type": "list_item",
                    "text": line[1:].strip()
                })
            else:
                structured["content"].append({
                    "type": "paragraph",
                    "text": line
                })
        
        return structured
    
    async def health_check(self) -> Dict[str, Any]:
        """检查无障碍服务健康状态"""
        if not self.enabled:
            return {"status": "disabled", "message": "Accessibility service is disabled"}
        
        try:
            response = await self._make_request("GET", "/health")
            return {"status": "healthy", "details": response}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# 全局实例
_accessibility_client: Optional[AccessibilityClient] = None


def get_accessibility_client() -> AccessibilityClient:
    """获取无障碍服务客户端实例"""
    global _accessibility_client
    if _accessibility_client is None:
        _accessibility_client = AccessibilityClient()
    return _accessibility_client


# 便捷函数
async def convert_text_to_speech(
    text: str,
    voice: TTSVoice = TTSVoice.FEMALE_STANDARD,
    speed: TTSSpeed = TTSSpeed.NORMAL,
    language: str = "zh-CN"
) -> TTSResponse:
    """便捷的文本转语音函数"""
    client = get_accessibility_client()
    request = TTSRequest(text=text, voice=voice, speed=speed, language=language)
    return await client.text_to_speech(request)


async def convert_speech_to_text(
    audio_data: Optional[bytes] = None,
    audio_url: Optional[str] = None,
    language: str = "zh-CN"
) -> STTResponse:
    """便捷的语音转文本函数"""
    client = get_accessibility_client()
    request = STTRequest(audio_data=audio_data, audio_url=audio_url, language=language)
    return await client.speech_to_text(request)


async def get_accessible_response(user_id: str, text_response: str) -> Dict[str, Any]:
    """获取适合用户的无障碍响应格式"""
    client = get_accessibility_client()
    return await client.convert_response_for_user(user_id, text_response)
