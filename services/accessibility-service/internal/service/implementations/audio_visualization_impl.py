#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音频可视化服务实现
为听力障碍用户提供音频内容的视觉化展示
"""

import logging
import asyncio
import json
import time
import numpy as np
import cv2
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from enum import Enum

from ..interfaces import IAudioVisualizationService, ICacheManager, IModelManager
from ..decorators import performance_monitor, error_handler, cache_result, trace

logger = logging.getLogger(__name__)


class VisualizationType(Enum):
    """可视化类型"""
    WAVEFORM = "waveform"               # 波形图
    SPECTRUM = "spectrum"               # 频谱图
    SPECTROGRAM = "spectrogram"         # 语谱图
    VOLUME_METER = "volume_meter"       # 音量计
    FREQUENCY_BARS = "frequency_bars"   # 频率条
    CIRCULAR_SPECTRUM = "circular"      # 圆形频谱
    PARTICLE_SYSTEM = "particles"       # 粒子系统
    RHYTHM_PATTERN = "rhythm"           # 节奏模式


class AudioFeature(Enum):
    """音频特征"""
    AMPLITUDE = "amplitude"             # 振幅
    FREQUENCY = "frequency"             # 频率
    PITCH = "pitch"                    # 音调
    TEMPO = "tempo"                    # 节拍
    TIMBRE = "timbre"                  # 音色
    LOUDNESS = "loudness"              # 响度
    ONSET = "onset"                    # 起始点
    BEAT = "beat"                      # 节拍


class ColorScheme(Enum):
    """颜色方案"""
    RAINBOW = "rainbow"                 # 彩虹色
    BLUE_GRADIENT = "blue_gradient"     # 蓝色渐变
    FIRE = "fire"                      # 火焰色
    OCEAN = "ocean"                    # 海洋色
    FOREST = "forest"                  # 森林色
    SUNSET = "sunset"                  # 日落色
    MONOCHROME = "monochrome"          # 单色
    HIGH_CONTRAST = "high_contrast"    # 高对比度


class VisualizationMode(Enum):
    """可视化模式"""
    REAL_TIME = "real_time"            # 实时模式
    BUFFERED = "buffered"              # 缓冲模式
    ANALYSIS = "analysis"              # 分析模式
    INTERACTIVE = "interactive"        # 交互模式


class AudioVisualizationServiceImpl(IAudioVisualizationService):
    """
    音频可视化服务实现类
    """
    
    def __init__(self, 
                 model_manager: IModelManager,
                 cache_manager: ICacheManager,
                 enabled: bool = True,
                 max_concurrent_streams: int = 50):
        """
        初始化音频可视化服务
        
        Args:
            model_manager: AI模型管理器
            cache_manager: 缓存管理器
            enabled: 是否启用服务
            max_concurrent_streams: 最大并发流数
        """
        self.model_manager = model_manager
        self.cache_manager = cache_manager
        self.enabled = enabled
        self.max_concurrent_streams = max_concurrent_streams
        
        # 并发控制
        self._semaphore = asyncio.Semaphore(max_concurrent_streams)
        
        # 服务状态
        self._initialized = False
        self._request_count = 0
        self._error_count = 0
        
        # 活跃流管理
        self._active_streams = {}
        
        # AI模型
        self._audio_analysis_model = None
        self._feature_extraction_model = None
        self._pattern_recognition_model = None
        self._emotion_detection_model = None
        
        # 可视化引擎
        self._visualization_engines = {}
        
        # 音频处理参数
        self._sample_rate = 44100
        self._buffer_size = 1024
        self._hop_length = 512
        self._n_fft = 2048
        
        # 颜色映射
        self._color_maps = {
            ColorScheme.RAINBOW: self._create_rainbow_colormap(),
            ColorScheme.BLUE_GRADIENT: self._create_blue_gradient_colormap(),
            ColorScheme.FIRE: self._create_fire_colormap(),
            ColorScheme.OCEAN: self._create_ocean_colormap(),
            ColorScheme.FOREST: self._create_forest_colormap(),
            ColorScheme.SUNSET: self._create_sunset_colormap(),
            ColorScheme.MONOCHROME: self._create_monochrome_colormap(),
            ColorScheme.HIGH_CONTRAST: self._create_high_contrast_colormap()
        }
        
        # 预设可视化配置
        self._visualization_presets = {
            "music": {
                "type": VisualizationType.SPECTRUM,
                "color_scheme": ColorScheme.RAINBOW,
                "features": [AudioFeature.FREQUENCY, AudioFeature.AMPLITUDE],
                "sensitivity": 0.8
            },
            "speech": {
                "type": VisualizationType.WAVEFORM,
                "color_scheme": ColorScheme.BLUE_GRADIENT,
                "features": [AudioFeature.AMPLITUDE, AudioFeature.PITCH],
                "sensitivity": 0.6
            },
            "ambient": {
                "type": VisualizationType.PARTICLE_SYSTEM,
                "color_scheme": ColorScheme.OCEAN,
                "features": [AudioFeature.TIMBRE, AudioFeature.LOUDNESS],
                "sensitivity": 0.4
            },
            "alert": {
                "type": VisualizationType.VOLUME_METER,
                "color_scheme": ColorScheme.HIGH_CONTRAST,
                "features": [AudioFeature.LOUDNESS, AudioFeature.ONSET],
                "sensitivity": 1.0
            }
        }
        
        logger.info("音频可视化服务初始化完成")
    
    async def initialize(self):
        """初始化服务"""
        if self._initialized:
            return
        
        try:
            if not self.enabled:
                logger.info("音频可视化服务已禁用")
                return
            
            # 加载AI模型
            await self._load_audio_models()
            
            # 初始化可视化引擎
            await self._initialize_visualization_engines()
            
            # 启动后台任务
            await self._start_background_tasks()
            
            self._initialized = True
            logger.info("音频可视化服务初始化成功")
            
        except Exception as e:
            logger.error(f"音频可视化服务初始化失败: {str(e)}")
            raise
    
    async def _load_audio_models(self):
        """加载音频分析AI模型"""
        try:
            # 音频分析模型
            self._audio_analysis_model = await self.model_manager.load_model(
                "audio_analysis",
                "audio_feature_analyzer"
            )
            
            # 特征提取模型
            self._feature_extraction_model = await self.model_manager.load_model(
                "feature_extraction",
                "audio_feature_extractor"
            )
            
            # 模式识别模型
            self._pattern_recognition_model = await self.model_manager.load_model(
                "pattern_recognition",
                "audio_pattern_detector"
            )
            
            # 情感检测模型
            self._emotion_detection_model = await self.model_manager.load_model(
                "emotion_detection",
                "audio_emotion_classifier"
            )
            
            logger.info("音频可视化AI模型加载完成")
            
        except Exception as e:
            logger.warning(f"音频可视化模型加载失败: {str(e)}")
    
    async def _initialize_visualization_engines(self):
        """初始化可视化引擎"""
        try:
            # 波形可视化引擎
            self._visualization_engines[VisualizationType.WAVEFORM] = WaveformVisualizer()
            
            # 频谱可视化引擎
            self._visualization_engines[VisualizationType.SPECTRUM] = SpectrumVisualizer()
            
            # 语谱图可视化引擎
            self._visualization_engines[VisualizationType.SPECTROGRAM] = SpectrogramVisualizer()
            
            # 音量计可视化引擎
            self._visualization_engines[VisualizationType.VOLUME_METER] = VolumeMeterVisualizer()
            
            # 频率条可视化引擎
            self._visualization_engines[VisualizationType.FREQUENCY_BARS] = FrequencyBarsVisualizer()
            
            # 圆形频谱可视化引擎
            self._visualization_engines[VisualizationType.CIRCULAR_SPECTRUM] = CircularSpectrumVisualizer()
            
            # 粒子系统可视化引擎
            self._visualization_engines[VisualizationType.PARTICLE_SYSTEM] = ParticleSystemVisualizer()
            
            # 节奏模式可视化引擎
            self._visualization_engines[VisualizationType.RHYTHM_PATTERN] = RhythmPatternVisualizer()
            
            logger.info("可视化引擎初始化完成")
            
        except Exception as e:
            logger.warning(f"可视化引擎初始化失败: {str(e)}")
    
    async def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 启动流管理任务
            asyncio.create_task(self._stream_management_loop())
            
            # 启动性能监控任务
            asyncio.create_task(self._performance_monitoring_loop())
            
            logger.info("音频可视化后台任务启动完成")
            
        except Exception as e:
            logger.warning(f"启动后台任务失败: {str(e)}")
    
    def _create_rainbow_colormap(self) -> np.ndarray:
        """创建彩虹色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            hue = i / 255.0 * 360
            colors[i] = self._hsv_to_rgb(hue, 1.0, 1.0)
        return colors
    
    def _create_blue_gradient_colormap(self) -> np.ndarray:
        """创建蓝色渐变色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            intensity = i / 255.0
            colors[i] = [int(intensity * 100), int(intensity * 150), int(intensity * 255)]
        return colors
    
    def _create_fire_colormap(self) -> np.ndarray:
        """创建火焰色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            if i < 85:
                colors[i] = [i * 3, 0, 0]
            elif i < 170:
                colors[i] = [255, (i - 85) * 3, 0]
            else:
                colors[i] = [255, 255, (i - 170) * 3]
        return colors
    
    def _create_ocean_colormap(self) -> np.ndarray:
        """创建海洋色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            intensity = i / 255.0
            colors[i] = [
                int(intensity * 50),
                int(intensity * 150 + 50),
                int(intensity * 200 + 55)
            ]
        return colors
    
    def _create_forest_colormap(self) -> np.ndarray:
        """创建森林色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            intensity = i / 255.0
            colors[i] = [
                int(intensity * 100),
                int(intensity * 200 + 55),
                int(intensity * 100)
            ]
        return colors
    
    def _create_sunset_colormap(self) -> np.ndarray:
        """创建日落色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            if i < 128:
                colors[i] = [255, i * 2, 0]
            else:
                colors[i] = [255, 255, (i - 128) * 2]
        return colors
    
    def _create_monochrome_colormap(self) -> np.ndarray:
        """创建单色彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            colors[i] = [i, i, i]
        return colors
    
    def _create_high_contrast_colormap(self) -> np.ndarray:
        """创建高对比度彩映射"""
        colors = np.zeros((256, 3), dtype=np.uint8)
        for i in range(256):
            if i < 128:
                colors[i] = [0, 0, 0]
            else:
                colors[i] = [255, 255, 255]
        return colors
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> Tuple[int, int, int]:
        """HSV转RGB"""
        h = h / 60.0
        i = int(h)
        f = h - i
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return int(r * 255), int(g * 255), int(b * 255)
    
    @performance_monitor
    @error_handler
    async def create_visualization_stream(self, 
                                        user_id: str,
                                        audio_source: Dict[str, Any],
                                        visualization_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建音频可视化流
        
        Args:
            user_id: 用户ID
            audio_source: 音频源配置
            visualization_config: 可视化配置
            
        Returns:
            流创建结果
        """
        async with self._semaphore:
            self._request_count += 1
            
            try:
                # 检查服务状态
                if not self._initialized:
                    await self.initialize()
                
                # 生成流ID
                stream_id = f"vis_stream_{user_id}_{int(time.time())}"
                
                # 解析可视化配置
                config = await self._parse_visualization_config(visualization_config)
                
                # 创建可视化流
                stream = {
                    "stream_id": stream_id,
                    "user_id": user_id,
                    "audio_source": audio_source,
                    "config": config,
                    "status": "initializing",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_frame_time": None,
                    "frame_count": 0,
                    "buffer": [],
                    "visualizer": None
                }
                
                # 初始化可视化器
                visualizer = await self._create_visualizer(config)
                stream["visualizer"] = visualizer
                
                # 启动音频处理
                await self._start_audio_processing(stream)
                
                # 添加到活跃流
                self._active_streams[stream_id] = stream
                
                stream["status"] = "active"
                
                logger.info(f"音频可视化流创建成功: {stream_id}")
                
                return {
                    "success": True,
                    "stream_id": stream_id,
                    "user_id": user_id,
                    "visualization_type": config["type"],
                    "message": "音频可视化流创建成功"
                }
                
            except Exception as e:
                self._error_count += 1
                logger.error(f"创建音频可视化流失败: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"创建音频可视化流失败: {str(e)}"
                }
    
    async def _parse_visualization_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """解析可视化配置"""
        try:
            # 使用预设配置
            preset = config.get("preset")
            if preset and preset in self._visualization_presets:
                parsed_config = self._visualization_presets[preset].copy()
            else:
                parsed_config = {}
            
            # 覆盖自定义配置
            parsed_config.update({
                "type": VisualizationType(config.get("type", "spectrum")),
                "color_scheme": ColorScheme(config.get("color_scheme", "rainbow")),
                "features": [AudioFeature(f) for f in config.get("features", ["frequency", "amplitude"])],
                "sensitivity": config.get("sensitivity", 0.7),
                "width": config.get("width", 800),
                "height": config.get("height", 600),
                "fps": config.get("fps", 30),
                "smoothing": config.get("smoothing", 0.8),
                "mode": VisualizationMode(config.get("mode", "real_time"))
            })
            
            return parsed_config
            
        except Exception as e:
            logger.warning(f"解析可视化配置失败: {str(e)}")
            # 返回默认配置
            return {
                "type": VisualizationType.SPECTRUM,
                "color_scheme": ColorScheme.RAINBOW,
                "features": [AudioFeature.FREQUENCY, AudioFeature.AMPLITUDE],
                "sensitivity": 0.7,
                "width": 800,
                "height": 600,
                "fps": 30,
                "smoothing": 0.8,
                "mode": VisualizationMode.REAL_TIME
            }
    
    async def _create_visualizer(self, config: Dict[str, Any]):
        """创建可视化器"""
        try:
            visualization_type = config["type"]
            
            if visualization_type in self._visualization_engines:
                visualizer = self._visualization_engines[visualization_type]
                await visualizer.initialize(config)
                return visualizer
            else:
                # 创建默认可视化器
                visualizer = SpectrumVisualizer()
                await visualizer.initialize(config)
                return visualizer
                
        except Exception as e:
            logger.warning(f"创建可视化器失败: {str(e)}")
            # 返回默认可视化器
            visualizer = SpectrumVisualizer()
            await visualizer.initialize(config)
            return visualizer
    
    async def _start_audio_processing(self, stream: Dict[str, Any]):
        """启动音频处理"""
        try:
            # 在实际实现中，这里应该启动音频捕获和处理
            # 例如：从麦克风、音频文件或网络流获取音频数据
            
            # 创建音频处理任务
            asyncio.create_task(self._audio_processing_loop(stream))
            
            logger.info(f"音频处理启动: {stream['stream_id']}")
            
        except Exception as e:
            logger.warning(f"启动音频处理失败: {str(e)}")
    
    async def _audio_processing_loop(self, stream: Dict[str, Any]):
        """音频处理循环"""
        try:
            stream_id = stream["stream_id"]
            config = stream["config"]
            visualizer = stream["visualizer"]
            
            frame_interval = 1.0 / config["fps"]
            
            while stream_id in self._active_streams and stream["status"] == "active":
                try:
                    # 获取音频数据
                    audio_data = await self._get_audio_data(stream)
                    
                    if audio_data is not None:
                        # 提取音频特征
                        features = await self._extract_audio_features(audio_data, config["features"])
                        
                        # 生成可视化帧
                        frame = await visualizer.generate_frame(features, config)
                        
                        # 更新流状态
                        stream["last_frame_time"] = datetime.now(timezone.utc).isoformat()
                        stream["frame_count"] += 1
                        
                        # 缓存帧数据
                        await self._cache_frame(stream_id, frame)
                    
                    # 控制帧率
                    await asyncio.sleep(frame_interval)
                    
                except Exception as e:
                    logger.warning(f"音频处理循环错误: {str(e)}")
                    await asyncio.sleep(frame_interval)
            
        except Exception as e:
            logger.error(f"音频处理循环失败: {str(e)}")
            stream["status"] = "error"
    
    async def _get_audio_data(self, stream: Dict[str, Any]) -> Optional[np.ndarray]:
        """获取音频数据"""
        try:
            # 在实际实现中，这里应该从音频源获取数据
            # 例如：麦克风、音频文件、网络流等
            
            # 模拟音频数据
            audio_data = np.random.randn(self._buffer_size).astype(np.float32)
            
            return audio_data
            
        except Exception as e:
            logger.warning(f"获取音频数据失败: {str(e)}")
            return None
    
    async def _extract_audio_features(self, 
                                    audio_data: np.ndarray,
                                    features: List[AudioFeature]) -> Dict[str, Any]:
        """提取音频特征"""
        try:
            extracted_features = {}
            
            for feature in features:
                if feature == AudioFeature.AMPLITUDE:
                    extracted_features["amplitude"] = np.abs(audio_data)
                
                elif feature == AudioFeature.FREQUENCY:
                    # 计算FFT
                    fft = np.fft.fft(audio_data, n=self._n_fft)
                    magnitude = np.abs(fft[:self._n_fft//2])
                    extracted_features["frequency"] = magnitude
                
                elif feature == AudioFeature.PITCH:
                    # 简化的基频检测
                    autocorr = np.correlate(audio_data, audio_data, mode='full')
                    autocorr = autocorr[autocorr.size // 2:]
                    
                    # 查找第一个峰值
                    peak_idx = np.argmax(autocorr[1:]) + 1
                    if peak_idx > 0:
                        pitch = self._sample_rate / peak_idx
                        extracted_features["pitch"] = pitch
                    else:
                        extracted_features["pitch"] = 0
                
                elif feature == AudioFeature.LOUDNESS:
                    # 计算RMS响度
                    rms = np.sqrt(np.mean(audio_data ** 2))
                    extracted_features["loudness"] = rms
                
                elif feature == AudioFeature.ONSET:
                    # 简化的起始点检测
                    energy = np.sum(audio_data ** 2)
                    extracted_features["onset"] = energy
                
                # 其他特征的提取...
            
            return extracted_features
            
        except Exception as e:
            logger.warning(f"提取音频特征失败: {str(e)}")
            return {}
    
    async def _cache_frame(self, stream_id: str, frame: np.ndarray):
        """缓存帧数据"""
        try:
            # 将帧数据编码为JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()
            
            # 缓存帧
            frame_key = f"vis_frame:{stream_id}:latest"
            await self.cache_manager.set(
                frame_key,
                frame_data,
                ttl=60  # 缓存1分钟
            )
            
        except Exception as e:
            logger.warning(f"缓存帧数据失败: {str(e)}")
    
    @performance_monitor
    @error_handler
    async def get_visualization_frame(self, 
                                    user_id: str,
                                    stream_id: str) -> Dict[str, Any]:
        """
        获取可视化帧
        
        Args:
            user_id: 用户ID
            stream_id: 流ID
            
        Returns:
            帧数据
        """
        try:
            # 检查流是否存在
            if stream_id not in self._active_streams:
                return {
                    "success": False,
                    "message": "可视化流不存在"
                }
            
            stream = self._active_streams[stream_id]
            
            # 检查用户权限
            if stream["user_id"] != user_id:
                return {
                    "success": False,
                    "message": "无权限访问此流"
                }
            
            # 获取最新帧
            frame_key = f"vis_frame:{stream_id}:latest"
            frame_data = await self.cache_manager.get(frame_key)
            
            if frame_data:
                return {
                    "success": True,
                    "stream_id": stream_id,
                    "frame_data": frame_data,
                    "frame_count": stream["frame_count"],
                    "last_frame_time": stream["last_frame_time"],
                    "message": "获取可视化帧成功"
                }
            else:
                return {
                    "success": False,
                    "message": "暂无可用帧数据"
                }
                
        except Exception as e:
            logger.error(f"获取可视化帧失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"获取可视化帧失败: {str(e)}"
            }
    
    async def _stream_management_loop(self):
        """流管理循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次
                
                current_time = datetime.now(timezone.utc)
                
                # 清理非活跃流
                inactive_streams = []
                for stream_id, stream in self._active_streams.items():
                    if stream["last_frame_time"]:
                        last_frame_time = datetime.fromisoformat(stream["last_frame_time"])
                        if (current_time - last_frame_time).total_seconds() > 300:  # 5分钟无活动
                            inactive_streams.append(stream_id)
                
                # 移除非活跃流
                for stream_id in inactive_streams:
                    await self._cleanup_stream(stream_id)
                
            except Exception as e:
                logger.error(f"流管理循环错误: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_stream(self, stream_id: str):
        """清理流"""
        try:
            if stream_id in self._active_streams:
                stream = self._active_streams[stream_id]
                stream["status"] = "stopped"
                
                # 清理可视化器
                if stream.get("visualizer"):
                    await stream["visualizer"].cleanup()
                
                # 清理缓存
                frame_key = f"vis_frame:{stream_id}:latest"
                await self.cache_manager.delete(frame_key)
                
                # 移除流
                del self._active_streams[stream_id]
                
                logger.info(f"流清理完成: {stream_id}")
                
        except Exception as e:
            logger.warning(f"清理流失败: {str(e)}")
    
    async def _performance_monitoring_loop(self):
        """性能监控循环"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟监控一次
                
                # 监控活跃流数量
                active_count = len(self._active_streams)
                
                # 监控错误率
                error_rate = self._error_count / max(self._request_count, 1)
                
                # 记录性能指标
                metrics = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "active_streams": active_count,
                    "total_requests": self._request_count,
                    "error_count": self._error_count,
                    "error_rate": error_rate
                }
                
                # 缓存性能指标
                metrics_key = "audio_visualization_metrics"
                await self.cache_manager.set(
                    metrics_key,
                    json.dumps(metrics),
                    ttl=3600  # 缓存1小时
                )
                
                logger.info(f"音频可视化性能指标: {metrics}")
                
            except Exception as e:
                logger.error(f"性能监控循环错误: {str(e)}")
                await asyncio.sleep(300)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service_name": "AudioVisualizationService",
            "enabled": self.enabled,
            "initialized": self._initialized,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "active_streams": len(self._active_streams),
            "max_concurrent_streams": self.max_concurrent_streams,
            "supported_visualization_types": [vtype.value for vtype in VisualizationType],
            "supported_color_schemes": [scheme.value for scheme in ColorScheme],
            "supported_audio_features": [feature.value for feature in AudioFeature],
            "visualization_presets": list(self._visualization_presets.keys()),
            "models_loaded": {
                "audio_analysis": self._audio_analysis_model is not None,
                "feature_extraction": self._feature_extraction_model is not None,
                "pattern_recognition": self._pattern_recognition_model is not None,
                "emotion_detection": self._emotion_detection_model is not None
            }
        }
    
    async def cleanup(self):
        """清理服务资源"""
        try:
            # 停止所有活跃流
            for stream_id in list(self._active_streams.keys()):
                await self._cleanup_stream(stream_id)
            
            # 清理可视化引擎
            for visualizer in self._visualization_engines.values():
                if hasattr(visualizer, 'cleanup'):
                    await visualizer.cleanup()
            
            # 释放模型资源
            self._audio_analysis_model = None
            self._feature_extraction_model = None
            self._pattern_recognition_model = None
            self._emotion_detection_model = None
            
            self._initialized = False
            logger.info("音频可视化服务清理完成")
            
        except Exception as e:
            logger.error(f"音频可视化服务清理失败: {str(e)}")


# 可视化器基类和具体实现
class BaseVisualizer:
    """可视化器基类"""
    
    def __init__(self):
        self.config = None
        self.color_map = None
    
    async def initialize(self, config: Dict[str, Any]):
        """初始化可视化器"""
        self.config = config
        self.color_map = self._get_color_map(config["color_scheme"])
    
    def _get_color_map(self, color_scheme: ColorScheme) -> np.ndarray:
        """获取颜色映射"""
        # 这里应该从服务实例获取颜色映射
        # 简化实现
        return np.random.randint(0, 255, (256, 3), dtype=np.uint8)
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        """生成可视化帧"""
        raise NotImplementedError
    
    async def cleanup(self):
        """清理资源"""
        pass


class SpectrumVisualizer(BaseVisualizer):
    """频谱可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        """生成频谱可视化帧"""
        try:
            width = config["width"]
            height = config["height"]
            
            # 创建空白帧
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 获取频率数据
            frequency_data = features.get("frequency", np.zeros(width//2))
            
            # 归一化
            if len(frequency_data) > 0:
                frequency_data = frequency_data / np.max(frequency_data + 1e-8)
            
            # 绘制频谱条
            bar_width = width // len(frequency_data)
            for i, magnitude in enumerate(frequency_data):
                bar_height = int(magnitude * height * config["sensitivity"])
                x = i * bar_width
                
                # 获取颜色
                color_idx = int(magnitude * 255)
                color = self.color_map[color_idx]
                
                # 绘制条形
                cv2.rectangle(
                    frame,
                    (x, height - bar_height),
                    (x + bar_width - 1, height),
                    color.tolist(),
                    -1
                )
            
            return frame
            
        except Exception as e:
            logger.warning(f"生成频谱可视化帧失败: {str(e)}")
            return np.zeros((config["height"], config["width"], 3), dtype=np.uint8)


class WaveformVisualizer(BaseVisualizer):
    """波形可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        """生成波形可视化帧"""
        try:
            width = config["width"]
            height = config["height"]
            
            # 创建空白帧
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 获取振幅数据
            amplitude_data = features.get("amplitude", np.zeros(width))
            
            # 调整数据长度
            if len(amplitude_data) != width:
                amplitude_data = np.interp(
                    np.linspace(0, len(amplitude_data)-1, width),
                    np.arange(len(amplitude_data)),
                    amplitude_data
                )
            
            # 归一化
            if len(amplitude_data) > 0:
                amplitude_data = amplitude_data / np.max(np.abs(amplitude_data) + 1e-8)
            
            # 绘制波形
            center_y = height // 2
            points = []
            
            for i, amplitude in enumerate(amplitude_data):
                y = center_y + int(amplitude * center_y * config["sensitivity"])
                points.append((i, y))
            
            # 绘制连线
            for i in range(len(points) - 1):
                cv2.line(frame, points[i], points[i+1], (0, 255, 0), 2)
            
            return frame
            
        except Exception as e:
            logger.warning(f"生成波形可视化帧失败: {str(e)}")
            return np.zeros((config["height"], config["width"], 3), dtype=np.uint8)


# 其他可视化器的简化实现
class SpectrogramVisualizer(BaseVisualizer):
    """语谱图可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8)


class VolumeMeterVisualizer(BaseVisualizer):
    """音量计可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8)


class FrequencyBarsVisualizer(BaseVisualizer):
    """频率条可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8)


class CircularSpectrumVisualizer(BaseVisualizer):
    """圆形频谱可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8)


class ParticleSystemVisualizer(BaseVisualizer):
    """粒子系统可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8)


class RhythmPatternVisualizer(BaseVisualizer):
    """节奏模式可视化器"""
    
    async def generate_frame(self, features: Dict[str, Any], config: Dict[str, Any]) -> np.ndarray:
        # 简化实现
        return np.random.randint(0, 255, (config["height"], config["width"], 3), dtype=np.uint8) 