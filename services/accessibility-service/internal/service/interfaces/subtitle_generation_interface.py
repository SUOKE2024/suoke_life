#!/usr/bin/env python

"""
字幕生成服务接口定义
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class SubtitleFormat(Enum):
    """字幕格式"""

    SRT = "srt"
    VTT = "vtt"
    ASS = "ass"
    SSA = "ssa"
    TTML = "ttml"
    JSON = "json"


class SubtitleStyle(Enum):
    """字幕样式"""

    DEFAULT = "default"
    LARGE_TEXT = "large_text"
    HIGH_CONTRAST = "high_contrast"
    COLORED = "colored"
    OUTLINED = "outlined"
    SHADOW = "shadow"


class AudioSource(Enum):
    """音频源类型"""

    MICROPHONE = "microphone"
    SYSTEM_AUDIO = "system_audio"
    FILE = "file"
    STREAM = "stream"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"


class ISubtitleGenerationService(ABC):
    """字幕生成服务接口"""

    @abstractmethod
    async def initialize(self):
        """初始化服务"""
        pass

    @abstractmethod
    async def start_subtitle_generation(
        self, user_id: str, audio_source: AudioSource, settings: dict[str, Any] = None
    ) -> dict[str, Any]:
        """
        开始字幕生成

        Args:
            user_id: 用户ID
            audio_source: 音频源类型
            settings: 生成设置

        Returns:
            生成会话信息
        """
        pass

    @abstractmethod
    async def generate_subtitle_file(
        self,
        session_id: str,
        format_type: SubtitleFormat,
        start_time: float | None = None,
        end_time: float | None = None,
    ) -> dict[str, Any]:
        """
        生成字幕文件

        Args:
            session_id: 会话ID
            format_type: 字幕格式
            start_time: 开始时间（秒）
            end_time: 结束时间（秒）

        Returns:
            字幕文件内容
        """
        pass

    @abstractmethod
    async def stop_subtitle_generation(self, session_id: str) -> dict[str, Any]:
        """
        停止字幕生成

        Args:
            session_id: 会话ID

        Returns:
            停止结果
        """
        pass

    @abstractmethod
    async def get_service_status(self) -> dict[str, Any]:
        """获取服务状态"""
        pass

    @abstractmethod
    async def cleanup(self):
        """清理服务资源"""
        pass
