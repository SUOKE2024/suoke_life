#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版闻诊服务

该模块是闻诊服务的增强版本，集成了高性能音频分析、并行处理、智能缓存和批量诊断功能，
提供专业的中医闻诊数据采集和分析服务。
"""

import asyncio
import time
import uuid
import hashlib
import json
import base64
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import numpy as np
from loguru import logger
import librosa
import soundfile as sf
from io import BytesIO
from scipy import signal
from scipy.fft import fft, fftfreq

# 导入通用组件
from services.common.governance.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
)
from services.common.governance.rate_limiter import (
    RateLimitConfig, get_rate_limiter, rate_limit
)
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

class AudioType(Enum):
    """音频类型"""
    VOICE = "voice"  # 语音
    BREATHING = "breathing"  # 呼吸音
    COUGH = "cough"  # 咳嗽音
    HEARTBEAT = "heartbeat"  # 心音
    GENERAL = "general"  # 一般音频

class AudioQuality(Enum):
    """音频质量"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class AudioAnalysisRequest:
    """音频分析请求"""
    request_id: str
    patient_id: str
    audio_type: AudioType
    audio_data: str  # Base64编码的音频数据
    sample_rate: int = 44100
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AudioFeature:
    """音频特征"""
    feature_type: str
    value: Any
    confidence: float
    time_range: Optional[Tuple[float, float]] = None  # 时间范围（秒）

@dataclass
class ListenResult:
    """闻诊结果"""
    request_id: str
    patient_id: str
    audio_type: AudioType
    features: List[AudioFeature]
    syndrome_indicators: Dict[str, float]  # 证候指标
    quality_score: float
    processing_time_ms: float
    recommendations: List[str]

@dataclass
class BatchAudioRequest:
    """批量音频分析请求"""
    batch_id: str
    requests: List[AudioAnalysisRequest]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedListenService:
    """增强版闻诊服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版闻诊服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 增强配置
        self.enhanced_config = {
            'audio_processing': {
                'supported_formats': ['wav', 'mp3', 'm4a', 'flac'],
                'max_duration': 300,  # 最大5分钟
                'quality_threshold': 0.6,
                'enhancement': {
                    'noise_reduction': True,
                    'normalization': True,
                    'filtering': True
                }
            },
            'parallel_processing': {
                'enabled': True,
                'max_workers': 4,
                'batch_size': 8
            },
            'caching': {
                'enabled': True,
                'ttl_seconds': {
                    'audio_features': 3600,
                    'analysis_result': 1800,
                    'model_inference': 7200
                },
                'max_cache_size': 3000
            },
            'feature_extraction': {
                'voice': ['pitch', 'intensity', 'rhythm', 'clarity'],
                'breathing': ['rate', 'depth', 'pattern', 'quality'],
                'cough': ['frequency', 'intensity', 'type', 'duration']
            },
            'model_optimization': {
                'use_gpu': False,  # 音频处理通常CPU足够
                'batch_inference': True,
                'feature_caching': True
            }
        }
        
        # 音频处理参数
        self.audio_params = {
            'sample_rate': 22050,  # 标准采样率
            'n_fft': 2048,
            'hop_length': 512,
            'n_mels': 128,
            'fmin': 0,
            'fmax': 8000
        }
        
        # 批处理队列
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        
        # 缓存
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # 性能统计
        self.stats = {
            'total_requests': 0,
            'successful_analyses': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'average_processing_time_ms': 0.0,
            'quality_distribution': defaultdict(int),
            'batch_processed': 0,
            'audio_types_processed': defaultdict(int)
        }
        
        # 断路器配置
        self.circuit_breaker_configs = {
            'audio_processing': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30.0,
                timeout=15.0
            ),
            'feature_extraction': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=20.0,
                timeout=10.0
            )
        }
        
        # 限流配置
        self.rate_limit_configs = {
            'analysis': RateLimitConfig(rate=20.0, burst=40),
            'batch': RateLimitConfig(rate=5.0, burst=10)
        }
        
        # 后台任务
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info("增强版闻诊服务初始化完成")
    
    async def initialize(self):
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("闻诊服务初始化完成")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 批处理处理器
        self.background_tasks.append(
            asyncio.create_task(self._batch_processor())
        )
        
        # 缓存清理器
        self.background_tasks.append(
            asyncio.create_task(self._cache_cleaner())
        )
    
    @trace(service_name="listen-service", kind=SpanKind.SERVER)
    @rate_limit(name="analysis", tokens=1)
    async def analyze_audio(
        self,
        patient_id: str,
        audio_type: AudioType,
        audio_data: str,
        sample_rate: int = 44100,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ListenResult:
        """
        分析音频
        
        Args:
            patient_id: 患者ID
            audio_type: 音频类型
            audio_data: Base64编码的音频数据
            sample_rate: 采样率
            metadata: 元数据
            
        Returns:
            闻诊结果
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        self.stats['total_requests'] += 1
        self.stats['audio_types_processed'][audio_type.value] += 1
        
        # 检查缓存
        cache_key = self._generate_cache_key(
            "analysis", patient_id, audio_type.value,
            hashlib.md5(audio_data.encode()).hexdigest()
        )
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            self.stats['cache_hits'] += 1
            return cached_result
        
        self.stats['cache_misses'] += 1
        
        try:
            # 解码和预处理音频
            audio_signal = await self._decode_and_preprocess_audio(
                audio_data, sample_rate
            )
            
            # 评估音频质量
            quality_score = await self._assess_audio_quality(audio_signal, audio_type)
            quality_level = self._get_quality_level(quality_score)
            self.stats['quality_distribution'][quality_level.value] += 1
            
            if quality_score < self.enhanced_config['audio_processing']['quality_threshold']:
                logger.warning(f"音频质量不足: {quality_score}")
                # 尝试增强音频
                audio_signal = await self._enhance_audio(audio_signal)
            
            # 并行提取特征
            if self.enhanced_config['parallel_processing']['enabled']:
                features = await self._parallel_feature_extraction(
                    audio_signal, audio_type
                )
            else:
                features = await self._extract_features(audio_signal, audio_type)
            
            # 分析证候指标
            syndrome_indicators = await self._analyze_syndrome_indicators(
                features, audio_type
            )
            
            # 生成建议
            recommendations = await self._generate_recommendations(
                syndrome_indicators, audio_type
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            result = ListenResult(
                request_id=request_id,
                patient_id=patient_id,
                audio_type=audio_type,
                features=features,
                syndrome_indicators=syndrome_indicators,
                quality_score=quality_score,
                processing_time_ms=processing_time_ms,
                recommendations=recommendations
            )
            
            # 缓存结果
            await self._set_to_cache(cache_key, result)
            
            # 更新统计
            self.stats['successful_analyses'] += 1
            self._update_stats(processing_time_ms)
            
            return result
            
        except Exception as e:
            logger.error(f"音频分析失败: {e}")
            raise
    
    async def _decode_and_preprocess_audio(
        self, 
        audio_data: str, 
        original_sample_rate: int
    ) -> np.ndarray:
        """解码和预处理音频"""
        # 解码Base64音频
        audio_bytes = base64.b64decode(audio_data)
        
        # 使用soundfile读取音频
        audio_signal, sr = sf.read(BytesIO(audio_bytes))
        
        # 如果是立体声，转换为单声道
        if len(audio_signal.shape) > 1:
            audio_signal = np.mean(audio_signal, axis=1)
        
        # 重采样到标准采样率
        if sr != self.audio_params['sample_rate']:
            audio_signal = librosa.resample(
                audio_signal, 
                orig_sr=sr, 
                target_sr=self.audio_params['sample_rate']
            )
        
        # 限制音频长度
        max_samples = (
            self.enhanced_config['audio_processing']['max_duration'] * 
            self.audio_params['sample_rate']
        )
        if len(audio_signal) > max_samples:
            audio_signal = audio_signal[:max_samples]
        
        return audio_signal
    
    async def _assess_audio_quality(
        self, 
        audio_signal: np.ndarray, 
        audio_type: AudioType
    ) -> float:
        """评估音频质量"""
        quality_factors = []
        
        # 1. 信噪比评估
        snr = await self._calculate_snr(audio_signal)
        snr_score = min(snr / 20, 1.0)  # 20dB为满分
        quality_factors.append(snr_score)
        
        # 2. 动态范围评估
        dynamic_range = np.max(audio_signal) - np.min(audio_signal)
        dr_score = min(dynamic_range / 0.8, 1.0)
        quality_factors.append(dr_score)
        
        # 3. 频谱完整性评估
        spectrum_score = await self._assess_spectrum_completeness(audio_signal)
        quality_factors.append(spectrum_score)
        
        # 4. 特定类型的质量检查
        if audio_type == AudioType.VOICE:
            # 检查语音活动
            voice_activity = await self._detect_voice_activity(audio_signal)
            quality_factors.append(voice_activity)
        elif audio_type == AudioType.BREATHING:
            # 检查呼吸模式
            breathing_pattern = await self._detect_breathing_pattern(audio_signal)
            quality_factors.append(breathing_pattern)
        
        # 综合质量分数
        quality_score = np.mean(quality_factors)
        return quality_score
    
    async def _calculate_snr(self, audio_signal: np.ndarray) -> float:
        """计算信噪比"""
        # 简化实现：基于能量分布
        # 假设前10%和后10%为噪声
        signal_length = len(audio_signal)
        noise_samples = int(signal_length * 0.1)
        
        noise_power = np.mean(audio_signal[:noise_samples]**2) + np.mean(audio_signal[-noise_samples:]**2)
        noise_power /= 2
        
        signal_power = np.mean(audio_signal**2)
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 40  # 很高的SNR
        
        return max(snr, 0)
    
    async def _assess_spectrum_completeness(self, audio_signal: np.ndarray) -> float:
        """评估频谱完整性"""
        # 计算频谱
        freqs = fftfreq(len(audio_signal), 1/self.audio_params['sample_rate'])
        spectrum = np.abs(fft(audio_signal))
        
        # 检查重要频段的能量分布
        important_bands = [
            (80, 250),    # 基频范围
            (250, 1000),  # 语音清晰度
            (1000, 4000), # 语音理解度
            (4000, 8000)  # 高频细节
        ]
        
        band_scores = []
        for low, high in important_bands:
            band_mask = (freqs >= low) & (freqs <= high)
            band_energy = np.sum(spectrum[band_mask])
            total_energy = np.sum(spectrum)
            
            if total_energy > 0:
                band_ratio = band_energy / total_energy
                band_scores.append(min(band_ratio * 10, 1.0))
            else:
                band_scores.append(0.0)
        
        return np.mean(band_scores)
    
    async def _detect_voice_activity(self, audio_signal: np.ndarray) -> float:
        """检测语音活动"""
        # 简化实现：基于能量和零交叉率
        frame_length = 1024
        hop_length = 512
        
        # 计算短时能量
        energy = []
        for i in range(0, len(audio_signal) - frame_length, hop_length):
            frame = audio_signal[i:i + frame_length]
            energy.append(np.sum(frame**2))
        
        energy = np.array(energy)
        
        # 语音活动检测阈值
        threshold = np.mean(energy) * 0.1
        voice_frames = np.sum(energy > threshold)
        total_frames = len(energy)
        
        if total_frames > 0:
            voice_activity_ratio = voice_frames / total_frames
        else:
            voice_activity_ratio = 0.0
        
        return voice_activity_ratio
    
    async def _detect_breathing_pattern(self, audio_signal: np.ndarray) -> float:
        """检测呼吸模式"""
        # 简化实现：检测周期性模式
        # 使用自相关检测周期性
        correlation = np.correlate(audio_signal, audio_signal, mode='full')
        correlation = correlation[correlation.size // 2:]
        
        # 寻找峰值
        peaks, _ = signal.find_peaks(correlation, height=np.max(correlation) * 0.3)
        
        if len(peaks) > 1:
            # 计算周期性强度
            periodicity = np.std(np.diff(peaks))
            periodicity_score = max(1.0 - periodicity / 1000, 0.0)
        else:
            periodicity_score = 0.0
        
        return periodicity_score
    
    def _get_quality_level(self, score: float) -> AudioQuality:
        """获取质量级别"""
        if score >= 0.8:
            return AudioQuality.EXCELLENT
        elif score >= 0.6:
            return AudioQuality.GOOD
        elif score >= 0.4:
            return AudioQuality.FAIR
        else:
            return AudioQuality.POOR
    
    async def _enhance_audio(self, audio_signal: np.ndarray) -> np.ndarray:
        """增强音频质量"""
        enhanced = audio_signal.copy()
        config = self.enhanced_config['audio_processing']['enhancement']
        
        if config['noise_reduction']:
            # 简单的噪声抑制
            # 使用谱减法
            stft = librosa.stft(enhanced, n_fft=self.audio_params['n_fft'])
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # 估计噪声谱（使用前几帧）
            noise_frames = 5
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)
            
            # 谱减法
            alpha = 2.0  # 过减因子
            enhanced_magnitude = magnitude - alpha * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)
            
            # 重构信号
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced = librosa.istft(enhanced_stft)
        
        if config['normalization']:
            # 归一化
            max_val = np.max(np.abs(enhanced))
            if max_val > 0:
                enhanced = enhanced / max_val * 0.8
        
        if config['filtering']:
            # 带通滤波
            nyquist = self.audio_params['sample_rate'] / 2
            low = 80 / nyquist
            high = 8000 / nyquist
            
            b, a = signal.butter(4, [low, high], btype='band')
            enhanced = signal.filtfilt(b, a, enhanced)
        
        return enhanced
    
    async def _parallel_feature_extraction(
        self,
        audio_signal: np.ndarray,
        audio_type: AudioType
    ) -> List[AudioFeature]:
        """并行特征提取"""
        feature_types = self.enhanced_config['feature_extraction'].get(
            audio_type.value, []
        )
        
        # 创建特征提取任务
        tasks = []
        for feature_type in feature_types:
            task = self._extract_single_feature(audio_signal, audio_type, feature_type)
            tasks.append(task)
        
        # 并行执行
        feature_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集有效结果
        features = []
        for result in feature_results:
            if isinstance(result, list):
                features.extend(result)
            elif isinstance(result, AudioFeature):
                features.append(result)
            else:
                logger.error(f"特征提取失败: {result}")
        
        return features
    
    async def _extract_features(
        self,
        audio_signal: np.ndarray,
        audio_type: AudioType
    ) -> List[AudioFeature]:
        """提取音频特征"""
        features = []
        
        if audio_type == AudioType.VOICE:
            features.extend(await self._extract_voice_features(audio_signal))
        elif audio_type == AudioType.BREATHING:
            features.extend(await self._extract_breathing_features(audio_signal))
        elif audio_type == AudioType.COUGH:
            features.extend(await self._extract_cough_features(audio_signal))
        else:
            features.extend(await self._extract_general_features(audio_signal))
        
        return features
    
    async def _extract_single_feature(
        self,
        audio_signal: np.ndarray,
        audio_type: AudioType,
        feature_type: str
    ) -> List[AudioFeature]:
        """提取单个特征类型"""
        if audio_type == AudioType.VOICE:
            if feature_type == 'pitch':
                return await self._extract_pitch_features(audio_signal)
            elif feature_type == 'intensity':
                return await self._extract_intensity_features(audio_signal)
            elif feature_type == 'rhythm':
                return await self._extract_rhythm_features(audio_signal)
            elif feature_type == 'clarity':
                return await self._extract_clarity_features(audio_signal)
        elif audio_type == AudioType.BREATHING:
            if feature_type == 'rate':
                return await self._extract_breathing_rate(audio_signal)
            elif feature_type == 'depth':
                return await self._extract_breathing_depth(audio_signal)
        
        return []
    
    async def _extract_voice_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取语音特征"""
        features = []
        
        # 基频分析
        pitch = await self._analyze_pitch(audio_signal)
        features.append(AudioFeature(
            feature_type="voice_pitch",
            value=pitch,
            confidence=0.85
        ))
        
        # 音强分析
        intensity = await self._analyze_intensity(audio_signal)
        features.append(AudioFeature(
            feature_type="voice_intensity",
            value=intensity,
            confidence=0.90
        ))
        
        # 语音清晰度
        clarity = await self._analyze_clarity(audio_signal)
        features.append(AudioFeature(
            feature_type="voice_clarity",
            value=clarity,
            confidence=0.80
        ))
        
        return features
    
    async def _extract_breathing_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取呼吸特征"""
        features = []
        
        # 呼吸频率
        breathing_rate = await self._analyze_breathing_rate(audio_signal)
        features.append(AudioFeature(
            feature_type="breathing_rate",
            value=breathing_rate,
            confidence=0.85
        ))
        
        # 呼吸深度
        breathing_depth = await self._analyze_breathing_depth(audio_signal)
        features.append(AudioFeature(
            feature_type="breathing_depth",
            value=breathing_depth,
            confidence=0.80
        ))
        
        # 呼吸模式
        breathing_pattern = await self._analyze_breathing_pattern(audio_signal)
        features.append(AudioFeature(
            feature_type="breathing_pattern",
            value=breathing_pattern,
            confidence=0.75
        ))
        
        return features
    
    async def _extract_cough_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取咳嗽特征"""
        features = []
        
        # 咳嗽频率
        cough_frequency = await self._analyze_cough_frequency(audio_signal)
        features.append(AudioFeature(
            feature_type="cough_frequency",
            value=cough_frequency,
            confidence=0.85
        ))
        
        # 咳嗽强度
        cough_intensity = await self._analyze_cough_intensity(audio_signal)
        features.append(AudioFeature(
            feature_type="cough_intensity",
            value=cough_intensity,
            confidence=0.80
        ))
        
        return features
    
    async def _extract_general_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取通用特征"""
        features = []
        
        # MFCC特征
        mfcc = librosa.feature.mfcc(
            y=audio_signal,
            sr=self.audio_params['sample_rate'],
            n_mfcc=13
        )
        mfcc_mean = np.mean(mfcc, axis=1)
        
        features.append(AudioFeature(
            feature_type="mfcc",
            value=mfcc_mean.tolist(),
            confidence=0.95
        ))
        
        # 频谱质心
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio_signal,
            sr=self.audio_params['sample_rate']
        )
        
        features.append(AudioFeature(
            feature_type="spectral_centroid",
            value=float(np.mean(spectral_centroid)),
            confidence=0.90
        ))
        
        return features
    
    # 具体的特征分析方法（简化实现）
    async def _analyze_pitch(self, audio_signal: np.ndarray) -> Dict[str, float]:
        """分析基频"""
        # 使用librosa提取基频
        pitches, magnitudes = librosa.piptrack(
            y=audio_signal,
            sr=self.audio_params['sample_rate']
        )
        
        # 提取主要基频
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if pitch_values:
            return {
                "mean": float(np.mean(pitch_values)),
                "std": float(np.std(pitch_values)),
                "min": float(np.min(pitch_values)),
                "max": float(np.max(pitch_values))
            }
        else:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
    
    async def _analyze_intensity(self, audio_signal: np.ndarray) -> str:
        """分析音强"""
        rms = librosa.feature.rms(y=audio_signal)[0]
        mean_rms = np.mean(rms)
        
        if mean_rms > 0.1:
            return "强"
        elif mean_rms > 0.05:
            return "中等"
        else:
            return "弱"
    
    async def _analyze_clarity(self, audio_signal: np.ndarray) -> str:
        """分析清晰度"""
        # 基于高频能量比例
        stft = librosa.stft(audio_signal)
        magnitude = np.abs(stft)
        
        # 计算高频能量比例
        total_energy = np.sum(magnitude)
        high_freq_energy = np.sum(magnitude[magnitude.shape[0]//2:, :])
        
        if total_energy > 0:
            high_freq_ratio = high_freq_energy / total_energy
            if high_freq_ratio > 0.3:
                return "清晰"
            elif high_freq_ratio > 0.15:
                return "一般"
            else:
                return "模糊"
        else:
            return "无声"
    
    async def _analyze_breathing_rate(self, audio_signal: np.ndarray) -> float:
        """分析呼吸频率"""
        # 简化实现：基于包络检测
        envelope = np.abs(signal.hilbert(audio_signal))
        
        # 低通滤波提取呼吸模式
        b, a = signal.butter(4, 2.0 / (self.audio_params['sample_rate'] / 2), 'low')
        filtered_envelope = signal.filtfilt(b, a, envelope)
        
        # 检测峰值
        peaks, _ = signal.find_peaks(filtered_envelope, distance=self.audio_params['sample_rate'])
        
        # 计算呼吸频率（次/分钟）
        duration = len(audio_signal) / self.audio_params['sample_rate']
        if duration > 0:
            breathing_rate = len(peaks) / duration * 60
        else:
            breathing_rate = 0.0
        
        return breathing_rate
    
    async def _analyze_breathing_depth(self, audio_signal: np.ndarray) -> str:
        """分析呼吸深度"""
        # 基于音量变化幅度
        envelope = np.abs(signal.hilbert(audio_signal))
        depth_variation = np.std(envelope)
        
        if depth_variation > 0.1:
            return "深"
        elif depth_variation > 0.05:
            return "中等"
        else:
            return "浅"
    
    async def _analyze_breathing_pattern(self, audio_signal: np.ndarray) -> str:
        """分析呼吸模式"""
        # 简化实现
        return "规律"
    
    async def _analyze_cough_frequency(self, audio_signal: np.ndarray) -> float:
        """分析咳嗽频率"""
        # 检测咳嗽事件
        # 简化实现：基于能量突变
        energy = librosa.feature.rms(y=audio_signal, frame_length=2048, hop_length=512)[0]
        
        # 检测能量峰值
        threshold = np.mean(energy) + 2 * np.std(energy)
        peaks, _ = signal.find_peaks(energy, height=threshold, distance=10)
        
        # 计算咳嗽频率
        duration = len(audio_signal) / self.audio_params['sample_rate']
        if duration > 0:
            cough_frequency = len(peaks) / duration * 60  # 次/分钟
        else:
            cough_frequency = 0.0
        
        return cough_frequency
    
    async def _analyze_cough_intensity(self, audio_signal: np.ndarray) -> str:
        """分析咳嗽强度"""
        max_amplitude = np.max(np.abs(audio_signal))
        
        if max_amplitude > 0.7:
            return "强烈"
        elif max_amplitude > 0.3:
            return "中等"
        else:
            return "轻微"
    
    async def _extract_pitch_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取基频特征"""
        pitch_data = await self._analyze_pitch(audio_signal)
        return [AudioFeature(
            feature_type="pitch_analysis",
            value=pitch_data,
            confidence=0.85
        )]
    
    async def _extract_intensity_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取音强特征"""
        intensity = await self._analyze_intensity(audio_signal)
        return [AudioFeature(
            feature_type="intensity_analysis",
            value=intensity,
            confidence=0.90
        )]
    
    async def _extract_rhythm_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取节律特征"""
        # 简化实现
        return [AudioFeature(
            feature_type="rhythm_analysis",
            value="规律",
            confidence=0.75
        )]
    
    async def _extract_clarity_features(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取清晰度特征"""
        clarity = await self._analyze_clarity(audio_signal)
        return [AudioFeature(
            feature_type="clarity_analysis",
            value=clarity,
            confidence=0.80
        )]
    
    async def _extract_breathing_rate(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取呼吸频率特征"""
        rate = await self._analyze_breathing_rate(audio_signal)
        return [AudioFeature(
            feature_type="breathing_rate_analysis",
            value=rate,
            confidence=0.85
        )]
    
    async def _extract_breathing_depth(self, audio_signal: np.ndarray) -> List[AudioFeature]:
        """提取呼吸深度特征"""
        depth = await self._analyze_breathing_depth(audio_signal)
        return [AudioFeature(
            feature_type="breathing_depth_analysis",
            value=depth,
            confidence=0.80
        )]
    
    async def _analyze_syndrome_indicators(
        self,
        features: List[AudioFeature],
        audio_type: AudioType
    ) -> Dict[str, float]:
        """分析证候指标"""
        indicators = {}
        
        # 基于特征分析证候
        for feature in features:
            if audio_type == AudioType.VOICE:
                if feature.feature_type == "voice_intensity" and feature.value == "弱":
                    indicators["气虚"] = indicators.get("气虚", 0) + 0.3
                elif feature.feature_type == "voice_clarity" and feature.value == "模糊":
                    indicators["痰湿"] = indicators.get("痰湿", 0) + 0.2
            
            elif audio_type == AudioType.BREATHING:
                if feature.feature_type == "breathing_rate" and feature.value > 20:
                    indicators["肺热"] = indicators.get("肺热", 0) + 0.3
                elif feature.feature_type == "breathing_depth" and feature.value == "浅":
                    indicators["肺气虚"] = indicators.get("肺气虚", 0) + 0.3
            
            elif audio_type == AudioType.COUGH:
                if feature.feature_type == "cough_intensity" and feature.value == "强烈":
                    indicators["肺热"] = indicators.get("肺热", 0) + 0.4
                elif feature.feature_type == "cough_frequency" and feature.value > 10:
                    indicators["肺燥"] = indicators.get("肺燥", 0) + 0.3
        
        # 归一化
        total = sum(indicators.values())
        if total > 0:
            for key in indicators:
                indicators[key] /= total
        
        return indicators
    
    async def _generate_recommendations(
        self,
        syndrome_indicators: Dict[str, float],
        audio_type: AudioType
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于证候指标生成建议
        primary_syndrome = max(syndrome_indicators.items(), key=lambda x: x[1])[0] if syndrome_indicators else None
        
        if primary_syndrome == "气虚":
            recommendations.extend([
                "建议适当休息，避免过度用声",
                "可进行呼吸训练，如腹式呼吸",
                "适当食用补气食物如人参、黄芪等"
            ])
        elif primary_syndrome == "肺热":
            recommendations.extend([
                "建议多饮水，保持咽喉湿润",
                "避免辛辣刺激食物",
                "可食用清热润肺的食物如梨、百合等"
            ])
        elif primary_syndrome == "痰湿":
            recommendations.extend([
                "建议清淡饮食，减少油腻食物",
                "适当运动，促进痰湿排出",
                "可食用化痰食物如陈皮、茯苓等"
            ])
        
        # 添加通用建议
        if audio_type == AudioType.VOICE:
            recommendations.append("注意用声卫生，避免大声喊叫")
        elif audio_type == AudioType.BREATHING:
            recommendations.append("保持室内空气清新")
        elif audio_type == AudioType.COUGH:
            recommendations.append("如咳嗽持续，请及时就医")
        
        recommendations.append("建议定期进行中医体检")
        
        return recommendations
    
    async def batch_analyze(
        self,
        requests: List[AudioAnalysisRequest]
    ) -> List[ListenResult]:
        """
        批量分析音频
        
        Args:
            requests: 音频分析请求列表
            
        Returns:
            分析结果列表
        """
        if self.enhanced_config['parallel_processing']['enabled']:
            # 并行处理
            tasks = []
            for request in requests:
                task = self.analyze_audio(
                    patient_id=request.patient_id,
                    audio_type=request.audio_type,
                    audio_data=request.audio_data,
                    sample_rate=request.sample_rate,
                    metadata=request.metadata
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 过滤有效结果
            valid_results = []
            for result in results:
                if isinstance(result, ListenResult):
                    valid_results.append(result)
                else:
                    logger.error(f"批量分析失败: {result}")
            
            self.stats['batch_processed'] += 1
            return valid_results
        else:
            # 串行处理
            results = []
            for request in requests:
                try:
                    result = await self.analyze_audio(
                        patient_id=request.patient_id,
                        audio_type=request.audio_type,
                        audio_data=request.audio_data,
                        sample_rate=request.sample_rate,
                        metadata=request.metadata
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"分析请求{request.request_id}失败: {e}")
            
            return results
    
    async def _batch_processor(self):
        """批处理处理器"""
        while True:
            try:
                batch = []
                deadline = time.time() + 1.0  # 1秒收集窗口
                
                # 收集批次
                while len(batch) < self.enhanced_config['parallel_processing']['batch_size']:
                    try:
                        remaining_time = deadline - time.time()
                        if remaining_time <= 0:
                            break
                        
                        request = await asyncio.wait_for(
                            self.batch_queue.get(),
                            timeout=remaining_time
                        )
                        batch.append(request)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # 处理批次
                    await self.batch_analyze(batch)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"批处理器错误: {e}")
                await asyncio.sleep(1)
    
    async def _cache_cleaner(self):
        """缓存清理器"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                # 查找过期项
                for key, (value, expire_time) in self.cache.items():
                    if current_time > expire_time:
                        expired_keys.append(key)
                
                # 删除过期项
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.info(f"清理了{len(expired_keys)}个过期缓存项")
                
                # 检查缓存大小
                max_size = self.enhanced_config['caching']['max_cache_size']
                if len(self.cache) > max_size:
                    # 删除最旧的项
                    items = sorted(self.cache.items(), key=lambda x: x[1][1])
                    for key, _ in items[:len(items)//2]:
                        del self.cache[key]
                    logger.info(f"缓存大小超限，清理了{len(items)//2}个项")
                
                await asyncio.sleep(300)  # 5分钟清理一次
                
            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)
    
    async def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if not self.enhanced_config['caching']['enabled']:
            return None
        
        if key in self.cache:
            value, expire_time = self.cache[key]
            if datetime.now() < expire_time:
                return value
            else:
                del self.cache[key]
        
        return None
    
    async def _set_to_cache(self, key: str, value: Any, ttl_type: str = "analysis_result"):
        """设置缓存"""
        if not self.enhanced_config['caching']['enabled']:
            return
        
        ttl = self.enhanced_config['caching']['ttl_seconds'].get(ttl_type, 1800)
        expire_time = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expire_time)
    
    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _update_stats(self, processing_time_ms: float):
        """更新统计信息"""
        # 更新平均处理时间
        alpha = 0.1
        if self.stats['average_processing_time_ms'] == 0:
            self.stats['average_processing_time_ms'] = processing_time_ms
        else:
            self.stats['average_processing_time_ms'] = (
                alpha * processing_time_ms + 
                (1 - alpha) * self.stats['average_processing_time_ms']
            )
    
    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = (
            self.stats['cache_hits'] / 
            max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
        )
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_analyses': self.stats['successful_analyses'],
            'cache_hit_rate': cache_hit_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'quality_distribution': dict(self.stats['quality_distribution']),
            'batch_processed': self.stats['batch_processed'],
            'cache_size': len(self.cache),
            'audio_types_processed': dict(self.stats['audio_types_processed'])
        }
    
    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()
        
        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("增强版闻诊服务已关闭") 