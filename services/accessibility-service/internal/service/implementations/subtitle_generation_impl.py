#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
字幕自动生成服务实现
为听力障碍用户提供实时字幕生成支持
"""

import logging
import asyncio
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum

from ..interfaces import ISubtitleGenerationService, ICacheManager, IModelManager
from ..decorators import performance_monitor, error_handler, cache_result, trace

logger = logging.getLogger(__name__)


class SubtitleFormat(Enum):
    """字幕格式"""
    SRT = "srt"                       # SubRip格式
    VTT = "vtt"                       # WebVTT格式
    ASS = "ass"                       # Advanced SubStation Alpha格式
    SSA = "ssa"                       # SubStation Alpha格式
    TTML = "ttml"                     # Timed Text Markup Language格式
    JSON = "json"                     # JSON格式


class SubtitleStyle(Enum):
    """字幕样式"""
    DEFAULT = "default"               # 默认样式
    LARGE_TEXT = "large_text"         # 大字体
    HIGH_CONTRAST = "high_contrast"   # 高对比度
    COLORED = "colored"               # 彩色字幕
    OUTLINED = "outlined"             # 描边字幕
    SHADOW = "shadow"                 # 阴影字幕


class AudioSource(Enum):
    """音频源类型"""
    MICROPHONE = "microphone"         # 麦克风
    SYSTEM_AUDIO = "system_audio"     # 系统音频
    FILE = "file"                     # 音频文件
    STREAM = "stream"                 # 音频流
    PHONE_CALL = "phone_call"         # 电话通话
    VIDEO_CALL = "video_call"         # 视频通话


class SubtitleGenerationServiceImpl(ISubtitleGenerationService):
    """
    字幕自动生成服务实现类
    """
    
    def __init__(self, 
                 model_manager: IModelManager,
                 cache_manager: ICacheManager,
                 enabled: bool = True,
                 max_concurrent_requests: int = 15):
        """
        初始化字幕生成服务
        
        Args:
            model_manager: AI模型管理器
            cache_manager: 缓存管理器
            enabled: 是否启用服务
            max_concurrent_requests: 最大并发请求数
        """
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.enabled = enabled
        self.max_concurrent_requests = max_concurrent_requests
        
        # 并发控制
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # 服务状态
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        
        # 语音识别模型
        self._speech_recognition_models = {}
        self._language_detection_model = None
        self._speaker_identification_model = None
        
        # 字幕生成会话
        self._active_sessions = {}
        
        # 支持的语言
        self._supported_languages = [
            "zh-CN", "zh-TW", "en-US", "en-GB", "ja-JP", "ko-KR",
            "fr-FR", "de-DE", "es-ES", "it-IT", "pt-PT", "ru-RU",
            "ar-SA", "hi-IN", "th-TH", "vi-VN"
        ]
        
        # 字幕样式配置
        self._subtitle_styles = {
            SubtitleStyle.DEFAULT: {
                "font_size": 16,
                "font_family": "Arial",
                "color": "#FFFFFF",
                "background_color": "#000000",
                "background_opacity": 0.7,
                "outline_color": "#000000",
                "outline_width": 1
            },
            SubtitleStyle.LARGE_TEXT: {
                "font_size": 24,
                "font_family": "Arial Bold",
                "color": "#FFFFFF",
                "background_color": "#000000",
                "background_opacity": 0.8,
                "outline_color": "#000000",
                "outline_width": 2
            },
            SubtitleStyle.HIGH_CONTRAST: {
                "font_size": 18,
                "font_family": "Arial Bold",
                "color": "#FFFF00",
                "background_color": "#000000",
                "background_opacity": 0.9,
                "outline_color": "#000000",
                "outline_width": 2
            },
            SubtitleStyle.COLORED: {
                "font_size": 16,
                "font_family": "Arial",
                "speaker_colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
                "background_color": "#000000",
                "background_opacity": 0.6
            },
            SubtitleStyle.OUTLINED: {
                "font_size": 16,
                "font_family": "Arial Bold",
                "color": "#FFFFFF",
                "outline_color": "#000000",
                "outline_width": 3,
                "background_opacity": 0.0
            },
            SubtitleStyle.SHADOW: {
                "font_size": 16,
                "font_family": "Arial",
                "color": "#FFFFFF",
                "shadow_color": "#000000",
                "shadow_offset": {"x": 2, "y": 2},
                "background_opacity": 0.0
            }
        }
        
        logger.info("字幕生成服务初始化完成")
    
    async def initialize(self):
        """初始化服务"""
        if self._initialized:
            return
        
        try:
            if not self.enabled:
                logger.info("字幕生成服务已禁用")
                return
            
            # 加载语音识别模型
            await self._load_speech_recognition_models()
            
            # 初始化音频处理组件
            await self._initialize_audio_processing()
            
            self._initialized = True
            logger.info("字幕生成服务初始化成功")
            
        except Exception as e:
            logger.error(f"字幕生成服务初始化失败: {str(e)}")
            raise
    
    async def _load_speech_recognition_models(self):
        """加载语音识别模型"""
        try:
            # 加载主要语言的语音识别模型
            for lang in ["zh-CN", "en-US", "ja-JP", "ko-KR"]:
                try:
                    model = await self.model_manager.load_model(
                        f"speech_recognition_{lang}",
                        "whisper_large_v3"
                    )
                    self._speech_recognition_models[lang] = model
                except Exception as e:
                    logger.warning(f"加载{lang}语音识别模型失败: {str(e)}")
            
            # 加载语言检测模型
            try:
                self._language_detection_model = await self.model_manager.load_model(
                    "language_detection",
                    "whisper_language_detector"
                )
            except Exception as e:
                logger.warning(f"加载语言检测模型失败: {str(e)}")
            
            # 加载说话人识别模型
            try:
                self._speaker_identification_model = await self.model_manager.load_model(
                    "speaker_identification",
                    "pyannote_speaker_diarization"
                )
            except Exception as e:
                logger.warning(f"加载说话人识别模型失败: {str(e)}")
            
            logger.info(f"语音识别模型加载完成，支持{len(self._speech_recognition_models)}种语言")
            
        except Exception as e:
            logger.warning(f"语音识别模型加载失败: {str(e)}")
    
    async def _initialize_audio_processing(self):
        """初始化音频处理组件"""
        try:
            # 在实际实现中，这里应该初始化音频捕获和处理组件
            # 例如：PyAudio、sounddevice等
            logger.info("音频处理组件初始化完成")
            
        except Exception as e:
            logger.warning(f"音频处理组件初始化失败: {str(e)}")
    
    @performance_monitor
    @error_handler
    async def start_subtitle_generation(self, 
                                      user_id: str,
                                      audio_source: AudioSource,
                                      settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        开始字幕生成
        
        Args:
            user_id: 用户ID
            audio_source: 音频源类型
            settings: 生成设置
            
        Returns:
            生成会话信息
        """
        async with self._semaphore:
            self._request_count += 1
            
            try:
                # 检查服务状态
                if not self._initialized:
                    await self.initialize()
                
                # 生成会话ID
                session_id = f"subtitle_{user_id}_{int(time.time() * 1000)}"
                
                # 获取用户偏好设置
                user_preferences = await self._get_user_subtitle_preferences(user_id)
                
                # 合并设置
                final_settings = {**user_preferences, **(settings or {})}
                
                # 创建字幕生成会话
                session_data = {
                    "session_id": session_id,
                    "user_id": user_id,
                    "audio_source": audio_source.value,
                    "settings": final_settings,
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "status": "active",
                    "subtitle_count": 0,
                    "total_duration": 0
                }
                
                # 保存会话数据
                self._active_sessions[session_id] = session_data
                await self._save_subtitle_session(session_data)
                
                # 启动音频捕获和处理
                await self._start_audio_capture(session_id, audio_source, final_settings)
                
                logger.info(f"字幕生成会话启动: {session_id}, 音频源={audio_source.value}")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "audio_source": audio_source.value,
                    "language": final_settings.get("language", "auto"),
                    "format": final_settings.get("format", SubtitleFormat.JSON.value),
                    "style": final_settings.get("style", SubtitleStyle.DEFAULT.value),
                    "message": "字幕生成启动成功"
                }
                
            except Exception as e:
                self._error_count += 1
                logger.error(f"启动字幕生成失败: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"启动字幕生成失败: {str(e)}"
                }
    
    async def _get_user_subtitle_preferences(self, user_id: str) -> Dict[str, Any]:
        """获取用户字幕偏好设置"""
        try:
            cache_key = f"subtitle_preferences:{user_id}"
            cached_prefs = await self.cache_manager.get(cache_key)
            
            if cached_prefs:
                return json.loads(cached_prefs)
            
            # 默认偏好设置
            default_preferences = {
                "language": "auto",
                "format": SubtitleFormat.JSON.value,
                "style": SubtitleStyle.DEFAULT.value,
                "max_line_length": 40,
                "max_lines_per_subtitle": 2,
                "min_duration": 1.0,
                "max_duration": 6.0,
                "speaker_identification": True,
                "punctuation_enhancement": True,
                "profanity_filter": False,
                "real_time_display": True,
                "confidence_threshold": 0.7
            }
            
            # 缓存默认设置
            await self.cache_manager.set(
                cache_key,
                json.dumps(default_preferences),
                ttl=3600
            )
            
            return default_preferences
            
        except Exception as e:
            logger.warning(f"获取用户字幕偏好失败: {str(e)}")
            return {
                "language": "auto",
                "format": SubtitleFormat.JSON.value,
                "style": SubtitleStyle.DEFAULT.value
            }
    
    async def _save_subtitle_session(self, session_data: Dict[str, Any]):
        """保存字幕生成会话数据"""
        try:
            session_key = f"subtitle_session:{session_data['session_id']}"
            await self.cache_manager.set(
                session_key,
                json.dumps(session_data),
                ttl=3600  # 1小时
            )
            
        except Exception as e:
            logger.warning(f"保存字幕会话失败: {str(e)}")
    
    async def _start_audio_capture(self, 
                                 session_id: str,
                                 audio_source: AudioSource,
                                 settings: Dict[str, Any]):
        """启动音频捕获和处理"""
        try:
            # 在实际实现中，这里应该启动音频捕获线程
            # 根据不同的音频源类型，使用不同的捕获方法
            
            capture_config = {
                "session_id": session_id,
                "audio_source": audio_source.value,
                "sample_rate": settings.get("sample_rate", 16000),
                "channels": settings.get("channels", 1),
                "chunk_size": settings.get("chunk_size", 1024),
                "buffer_duration": settings.get("buffer_duration", 3.0)
            }
            
            logger.info(f"音频捕获启动: {capture_config}")
            
            # 启动实时处理任务
            asyncio.create_task(self._process_audio_stream(session_id, settings))
            
        except Exception as e:
            logger.error(f"启动音频捕获失败: {str(e)}")
            raise
    
    async def _process_audio_stream(self, session_id: str, settings: Dict[str, Any]):
        """处理音频流并生成字幕"""
        try:
            while session_id in self._active_sessions:
                # 模拟音频数据处理
                # 在实际实现中，这里应该从音频缓冲区读取数据
                
                # 模拟音频片段
                audio_chunk = {
                    "data": b"mock_audio_data",
                    "timestamp": time.time(),
                    "duration": 3.0
                }
                
                # 处理音频片段
                subtitle_result = await self._process_audio_chunk(
                    session_id, audio_chunk, settings
                )
                
                if subtitle_result:
                    # 发送字幕到客户端
                    await self._send_subtitle_to_client(session_id, subtitle_result)
                
                # 等待下一个处理周期
                await asyncio.sleep(1.0)
                
        except Exception as e:
            logger.error(f"音频流处理失败: {str(e)}")
        finally:
            logger.info(f"音频流处理结束: {session_id}")
    
    async def _process_audio_chunk(self, 
                                 session_id: str,
                                 audio_chunk: Dict[str, Any],
                                 settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理音频片段并生成字幕"""
        try:
            # 检测语言（如果设置为自动）
            language = settings.get("language", "auto")
            if language == "auto":
                language = await self._detect_language(audio_chunk)
            
            # 语音识别
            transcription_result = await self._transcribe_audio(audio_chunk, language)
            
            if not transcription_result or not transcription_result.get("text"):
                return None
            
            # 说话人识别
            speaker_info = None
            if settings.get("speaker_identification", True):
                speaker_info = await self._identify_speaker(audio_chunk)
            
            # 文本后处理
            processed_text = await self._post_process_text(
                transcription_result["text"], settings
            )
            
            # 生成字幕条目
            subtitle_entry = {
                "id": f"{session_id}_{int(time.time() * 1000)}",
                "start_time": audio_chunk["timestamp"],
                "end_time": audio_chunk["timestamp"] + audio_chunk["duration"],
                "text": processed_text,
                "language": language,
                "confidence": transcription_result.get("confidence", 0.0),
                "speaker": speaker_info.get("speaker_id") if speaker_info else None,
                "speaker_confidence": speaker_info.get("confidence") if speaker_info else None
            }
            
            # 应用字幕样式
            styled_subtitle = await self._apply_subtitle_style(
                subtitle_entry, settings
            )
            
            return styled_subtitle
            
        except Exception as e:
            logger.warning(f"音频片段处理失败: {str(e)}")
            return None
    
    async def _detect_language(self, audio_chunk: Dict[str, Any]) -> str:
        """检测音频语言"""
        try:
            if self._language_detection_model:
                # 使用AI模型检测语言
                # 这里应该是实际的语言检测代码
                detected_language = "zh-CN"  # 模拟检测结果
                return detected_language
            else:
                # 默认返回中文
                return "zh-CN"
                
        except Exception as e:
            logger.warning(f"语言检测失败: {str(e)}")
            return "zh-CN"
    
    async def _transcribe_audio(self, 
                              audio_chunk: Dict[str, Any],
                              language: str) -> Optional[Dict[str, Any]]:
        """语音转文字"""
        try:
            # 获取对应语言的模型
            model = self._speech_recognition_models.get(language)
            
            if model:
                # 使用AI模型进行语音识别
                # 这里应该是实际的语音识别代码
                transcription = {
                    "text": "这是一个模拟的语音识别结果",
                    "confidence": 0.85,
                    "words": [
                        {"word": "这是", "start": 0.0, "end": 0.5, "confidence": 0.9},
                        {"word": "一个", "start": 0.5, "end": 1.0, "confidence": 0.8},
                        {"word": "模拟的", "start": 1.0, "end": 1.8, "confidence": 0.85},
                        {"word": "语音识别", "start": 1.8, "end": 2.5, "confidence": 0.9},
                        {"word": "结果", "start": 2.5, "end": 3.0, "confidence": 0.8}
                    ]
                }
                return transcription
            else:
                # 使用基础实现
                return {
                    "text": "基础语音识别结果",
                    "confidence": 0.6
                }
                
        except Exception as e:
            logger.warning(f"语音识别失败: {str(e)}")
            return None
    
    async def _identify_speaker(self, audio_chunk: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """说话人识别"""
        try:
            if self._speaker_identification_model:
                # 使用AI模型进行说话人识别
                # 这里应该是实际的说话人识别代码
                speaker_result = {
                    "speaker_id": "speaker_001",
                    "confidence": 0.8,
                    "gender": "male",
                    "age_group": "adult"
                }
                return speaker_result
            else:
                return None
                
        except Exception as e:
            logger.warning(f"说话人识别失败: {str(e)}")
            return None
    
    async def _post_process_text(self, text: str, settings: Dict[str, Any]) -> str:
        """文本后处理"""
        try:
            processed_text = text
            
            # 标点符号增强
            if settings.get("punctuation_enhancement", True):
                processed_text = await self._enhance_punctuation(processed_text)
            
            # 脏话过滤
            if settings.get("profanity_filter", False):
                processed_text = await self._filter_profanity(processed_text)
            
            # 文本格式化
            processed_text = await self._format_text(processed_text, settings)
            
            return processed_text
            
        except Exception as e:
            logger.warning(f"文本后处理失败: {str(e)}")
            return text
    
    async def _enhance_punctuation(self, text: str) -> str:
        """增强标点符号"""
        try:
            # 简单的标点符号增强
            # 在实际实现中，这里应该使用更复杂的NLP模型
            
            # 添加句号
            if not text.endswith(('.', '!', '?', '。', '！', '？')):
                if any(char in text for char in '。！？'):
                    text += '。'
                else:
                    text += '.'
            
            # 添加逗号
            text = re.sub(r'(\w+)\s+(\w+)\s+(\w+)', r'\1，\2 \3', text)
            
            return text
            
        except Exception as e:
            logger.warning(f"标点符号增强失败: {str(e)}")
            return text
    
    async def _filter_profanity(self, text: str) -> str:
        """过滤脏话"""
        try:
            # 简单的脏话过滤
            # 在实际实现中，这里应该使用专门的脏话检测库
            
            profanity_words = ["脏话1", "脏话2", "脏话3"]  # 示例
            
            for word in profanity_words:
                if word in text:
                    text = text.replace(word, "*" * len(word))
            
            return text
            
        except Exception as e:
            logger.warning(f"脏话过滤失败: {str(e)}")
            return text
    
    async def _format_text(self, text: str, settings: Dict[str, Any]) -> str:
        """格式化文本"""
        try:
            max_line_length = settings.get("max_line_length", 40)
            max_lines = settings.get("max_lines_per_subtitle", 2)
            
            # 按长度分行
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_line_length:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        lines.append(current_line)
                        current_line = word
                    else:
                        lines.append(word)
                
                # 限制行数
                if len(lines) >= max_lines:
                    break
            
            if current_line and len(lines) < max_lines:
                lines.append(current_line)
            
            return "\n".join(lines[:max_lines])
            
        except Exception as e:
            logger.warning(f"文本格式化失败: {str(e)}")
            return text
    
    async def _apply_subtitle_style(self, 
                                  subtitle_entry: Dict[str, Any],
                                  settings: Dict[str, Any]) -> Dict[str, Any]:
        """应用字幕样式"""
        try:
            style_name = settings.get("style", SubtitleStyle.DEFAULT.value)
            style_config = self._subtitle_styles.get(
                SubtitleStyle(style_name), 
                self._subtitle_styles[SubtitleStyle.DEFAULT]
            )
            
            # 应用样式
            styled_subtitle = {
                **subtitle_entry,
                "style": {
                    **style_config,
                    "position": settings.get("position", {"x": "center", "y": "bottom"}),
                    "animation": settings.get("animation", "fade_in")
                }
            }
            
            # 如果是彩色字幕且有说话人信息
            if (style_name == SubtitleStyle.COLORED.value and 
                subtitle_entry.get("speaker")):
                speaker_colors = style_config.get("speaker_colors", [])
                if speaker_colors:
                    # 根据说话人ID分配颜色
                    speaker_id = subtitle_entry["speaker"]
                    color_index = hash(speaker_id) % len(speaker_colors)
                    styled_subtitle["style"]["color"] = speaker_colors[color_index]
            
            return styled_subtitle
            
        except Exception as e:
            logger.warning(f"应用字幕样式失败: {str(e)}")
            return subtitle_entry
    
    async def _send_subtitle_to_client(self, 
                                     session_id: str,
                                     subtitle_data: Dict[str, Any]):
        """发送字幕到客户端"""
        try:
            # 在实际实现中，这里应该通过WebSocket或其他实时通信方式
            # 将字幕数据发送给客户端
            
            # 更新会话统计
            if session_id in self._active_sessions:
                session = self._active_sessions[session_id]
                session["subtitle_count"] += 1
                session["total_duration"] += (
                    subtitle_data["end_time"] - subtitle_data["start_time"]
                )
            
            # 保存字幕历史
            await self._save_subtitle_history(session_id, subtitle_data)
            
            logger.debug(f"字幕发送: {session_id}, 文本={subtitle_data['text'][:20]}...")
            
        except Exception as e:
            logger.warning(f"发送字幕失败: {str(e)}")
    
    async def _save_subtitle_history(self, 
                                   session_id: str,
                                   subtitle_data: Dict[str, Any]):
        """保存字幕历史"""
        try:
            history_key = f"subtitle_history:{session_id}"
            
            # 获取现有历史
            existing_history = await self.cache_manager.get(history_key)
            if existing_history:
                history_list = json.loads(existing_history)
            else:
                history_list = []
            
            # 添加新字幕
            history_list.append(subtitle_data)
            
            # 保持最近1000条记录
            if len(history_list) > 1000:
                history_list = history_list[-1000:]
            
            # 保存历史
            await self.cache_manager.set(
                history_key,
                json.dumps(history_list),
                ttl=86400 * 7  # 保存7天
            )
            
        except Exception as e:
            logger.warning(f"保存字幕历史失败: {str(e)}")
    
    @performance_monitor
    @error_handler
    async def generate_subtitle_file(self, 
                                   session_id: str,
                                   format_type: SubtitleFormat,
                                   start_time: Optional[float] = None,
                                   end_time: Optional[float] = None) -> Dict[str, Any]:
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
        try:
            # 获取字幕历史
            history_key = f"subtitle_history:{session_id}"
            history_data = await self.cache_manager.get(history_key)
            
            if not history_data:
                return {
                    "success": False,
                    "message": "未找到字幕数据"
                }
            
            subtitle_list = json.loads(history_data)
            
            # 时间范围过滤
            if start_time is not None or end_time is not None:
                filtered_subtitles = []
                for subtitle in subtitle_list:
                    sub_start = subtitle["start_time"]
                    sub_end = subtitle["end_time"]
                    
                    if start_time is not None and sub_end < start_time:
                        continue
                    if end_time is not None and sub_start > end_time:
                        continue
                    
                    filtered_subtitles.append(subtitle)
                
                subtitle_list = filtered_subtitles
            
            # 生成指定格式的字幕文件
            subtitle_content = await self._format_subtitle_file(
                subtitle_list, format_type
            )
            
            return {
                "success": True,
                "session_id": session_id,
                "format": format_type.value,
                "subtitle_count": len(subtitle_list),
                "content": subtitle_content,
                "file_size": len(subtitle_content.encode('utf-8'))
            }
            
        except Exception as e:
            logger.error(f"生成字幕文件失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"生成字幕文件失败: {str(e)}"
            }
    
    async def _format_subtitle_file(self, 
                                  subtitle_list: List[Dict[str, Any]],
                                  format_type: SubtitleFormat) -> str:
        """格式化字幕文件"""
        try:
            if format_type == SubtitleFormat.SRT:
                return await self._format_srt(subtitle_list)
            elif format_type == SubtitleFormat.VTT:
                return await self._format_vtt(subtitle_list)
            elif format_type == SubtitleFormat.ASS:
                return await self._format_ass(subtitle_list)
            elif format_type == SubtitleFormat.JSON:
                return json.dumps(subtitle_list, ensure_ascii=False, indent=2)
            else:
                # 默认使用SRT格式
                return await self._format_srt(subtitle_list)
                
        except Exception as e:
            logger.error(f"格式化字幕文件失败: {str(e)}")
            raise
    
    async def _format_srt(self, subtitle_list: List[Dict[str, Any]]) -> str:
        """格式化SRT字幕"""
        srt_content = []
        
        for i, subtitle in enumerate(subtitle_list, 1):
            start_time = self._seconds_to_srt_time(subtitle["start_time"])
            end_time = self._seconds_to_srt_time(subtitle["end_time"])
            text = subtitle["text"]
            
            # 添加说话人信息
            if subtitle.get("speaker"):
                text = f"[{subtitle['speaker']}] {text}"
            
            srt_entry = f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
            srt_content.append(srt_entry)
        
        return "".join(srt_content)
    
    async def _format_vtt(self, subtitle_list: List[Dict[str, Any]]) -> str:
        """格式化VTT字幕"""
        vtt_content = ["WEBVTT\n\n"]
        
        for subtitle in subtitle_list:
            start_time = self._seconds_to_vtt_time(subtitle["start_time"])
            end_time = self._seconds_to_vtt_time(subtitle["end_time"])
            text = subtitle["text"]
            
            # 添加说话人信息
            if subtitle.get("speaker"):
                text = f"<v {subtitle['speaker']}>{text}"
            
            vtt_entry = f"{start_time} --> {end_time}\n{text}\n\n"
            vtt_content.append(vtt_entry)
        
        return "".join(vtt_content)
    
    async def _format_ass(self, subtitle_list: List[Dict[str, Any]]) -> str:
        """格式化ASS字幕"""
        # ASS格式头部
        ass_header = """[Script Info]
Title: Generated Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,16,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        ass_content = [ass_header]
        
        for subtitle in subtitle_list:
            start_time = self._seconds_to_ass_time(subtitle["start_time"])
            end_time = self._seconds_to_ass_time(subtitle["end_time"])
            text = subtitle["text"].replace("\n", "\\N")
            
            speaker = subtitle.get("speaker", "")
            
            ass_entry = f"Dialogue: 0,{start_time},{end_time},Default,{speaker},0,0,0,,{text}\n"
            ass_content.append(ass_entry)
        
        return "".join(ass_content)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """将秒数转换为SRT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """将秒数转换为VTT时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """将秒数转换为ASS时间格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        
        return f"{hours:01d}:{minutes:02d}:{secs:05.2f}"
    
    @performance_monitor
    async def stop_subtitle_generation(self, session_id: str) -> Dict[str, Any]:
        """
        停止字幕生成
        
        Args:
            session_id: 会话ID
            
        Returns:
            停止结果
        """
        try:
            if session_id not in self._active_sessions:
                return {
                    "success": False,
                    "message": "会话不存在或已停止"
                }
            
            # 获取会话数据
            session_data = self._active_sessions[session_id]
            
            # 更新会话状态
            session_data["status"] = "stopped"
            session_data["end_time"] = datetime.now(timezone.utc).isoformat()
            
            # 停止音频捕获
            await self._stop_audio_capture(session_id)
            
            # 移除活跃会话
            del self._active_sessions[session_id]
            
            # 保存最终会话数据
            await self._save_subtitle_session(session_data)
            
            logger.info(f"字幕生成会话停止: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "subtitle_count": session_data.get("subtitle_count", 0),
                "total_duration": session_data.get("total_duration", 0),
                "message": "字幕生成已停止"
            }
            
        except Exception as e:
            logger.error(f"停止字幕生成失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"停止字幕生成失败: {str(e)}"
            }
    
    async def _stop_audio_capture(self, session_id: str):
        """停止音频捕获"""
        try:
            # 在实际实现中，这里应该停止音频捕获线程
            logger.info(f"音频捕获已停止: {session_id}")
            
        except Exception as e:
            logger.warning(f"停止音频捕获失败: {str(e)}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "SubtitleGenerationService",
            "enabled": self.enabled,
            "initialized": self._initialized,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "active_sessions": len(self._active_sessions),
            "supported_languages": self._supported_languages,
            "supported_formats": [fmt.value for fmt in SubtitleFormat],
            "supported_styles": [style.value for style in SubtitleStyle],
            "models_loaded": {
                "speech_recognition": len(self._speech_recognition_models),
                "language_detection": self._language_detection_model is not None,
                "speaker_identification": self._speaker_identification_model is not None
            }
        }
    
    async def cleanup(self):
        """清理服务资源"""
        try:
            # 停止所有活跃会话
            for session_id in list(self._active_sessions.keys()):
                await self.stop_subtitle_generation(session_id)
            
            # 释放模型资源
            self._speech_recognition_models.clear()
            self._language_detection_model = None
            self._speaker_identification_model = None
            
            self._initialized = False
            logger.info("字幕生成服务清理完成")
            
        except Exception as e:
            logger.error(f"字幕生成服务清理失败: {str(e)}") 