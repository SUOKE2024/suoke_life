"""
音频分析器模块

提供音频特征提取、语音分析和音频质量评估功能。
"""

import asyncio
import hashlib
import io
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import librosa
import numpy as np
import scipy.signal
import soundfile as sf
import structlog
import torch
from scipy.stats import kurtosis, skew
from sklearn.preprocessing import StandardScaler

from ..config.settings import get_settings
from ..models.audio_models import (
    AudioFeatures,
    AudioFormat,
    AudioMetadata,
    AnalysisRequest,
    AnalysisResult,
)
from ..models.tcm_models import TCMDiagnosis
from ..utils.cache import AudioCache
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


class AudioQuality(Enum):
    """音频质量等级"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class SpectralFeatures:
    """频谱特征"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_bandwidth: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    mel_spectrogram: np.ndarray


@dataclass
class TemporalFeatures:
    """时域特征"""
    rms_energy: np.ndarray
    tempo: float
    beat_frames: np.ndarray
    onset_frames: np.ndarray
    duration: float
    silence_ratio: float


class AudioAnalyzer:
    """音频分析器"""
    
    def __init__(self, cache: Optional[AudioCache] = None):
        """初始化音频分析器"""
        self.settings = get_settings()
        self.cache = cache
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.scaler = StandardScaler()
        
        # 音频处理参数
        self.sample_rate = 22050
        self.n_mfcc = 13
        self.n_fft = 2048
        self.hop_length = 512
        self.n_mels = 128
        
        logger.info("音频分析器初始化完成")
    
    async def initialize(self) -> None:
        """初始化音频分析器"""
        # 这里可以添加任何需要异步初始化的资源
        logger.info("音频分析器异步初始化完成")
    
    async def analyze_audio(
        self,
        audio_data: Union[bytes, np.ndarray, str, Path],
        request: AnalysisRequest
    ) -> AnalysisResult:
        """分析音频文件"""
        start_time = time.time()
        
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(audio_data, request)
            
            # 检查缓存
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info("从缓存获取分析结果", cache_key=cache_key)
                    return cached_result
            
            # 加载音频数据
            audio_array, sr = await self._load_audio(audio_data)
            
            # 音频预处理
            audio_array = await self._preprocess_audio(audio_array, sr)
            
            # 提取音频元数据
            metadata = self._extract_metadata(audio_array, sr)
            
            # 评估音频质量
            quality = await self._assess_audio_quality(audio_array, sr)
            
            # 提取特征
            features = await self._extract_features(audio_array, sr, request)
            
            # 创建分析结果
            result = AnalysisResult(
                request_id=request.request_id,
                metadata=metadata,
                features=features,
                quality=quality,
                processing_time=time.time() - start_time,
                timestamp=time.time()
            )
            
            # 缓存结果
            if self.cache:
                await self.cache.set(cache_key, result, ttl=3600)
            
            logger.info(
                "音频分析完成",
                request_id=request.request_id,
                duration=metadata.duration,
                quality=quality.value,
                processing_time=result.processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "音频分析失败",
                request_id=request.request_id,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def _load_audio(
        self,
        audio_data: Union[bytes, np.ndarray, str, Path]
    ) -> Tuple[np.ndarray, int]:
        """加载音频数据"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.sample_rate
        
        if isinstance(audio_data, bytes):
            # 从字节数据加载
            audio_array, sr = sf.read(io.BytesIO(audio_data))
        elif isinstance(audio_data, (str, Path)):
            # 从文件路径加载
            audio_array, sr = sf.read(str(audio_data))
        else:
            raise ValueError(f"不支持的音频数据类型: {type(audio_data)}")
        
        # 重采样到标准采样率
        if sr != self.sample_rate:
            audio_array = librosa.resample(
                audio_array, 
                orig_sr=sr, 
                target_sr=self.sample_rate
            )
        
        # 转换为单声道
        if audio_array.ndim > 1:
            audio_array = librosa.to_mono(audio_array)
        
        return audio_array, self.sample_rate
    
    async def _preprocess_audio(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> np.ndarray:
        """音频预处理"""
        # 归一化
        audio_array = librosa.util.normalize(audio_array)
        
        # 去除静音
        audio_array, _ = librosa.effects.trim(
            audio_array,
            top_db=20,
            frame_length=2048,
            hop_length=512
        )
        
        # 预加重滤波
        audio_array = np.append(audio_array[0], audio_array[1:] - 0.97 * audio_array[:-1])
        
        return audio_array
    
    def _extract_metadata(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> AudioMetadata:
        """提取音频元数据"""
        duration = len(audio_array) / sr
        
        return AudioMetadata(
            duration=duration,
            sample_rate=sr,
            channels=1,
            format=AudioFormat.WAV,
            bit_depth=16,
            file_size=len(audio_array) * 2  # 16-bit = 2 bytes per sample
        )
    
    async def _assess_audio_quality(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> AudioQuality:
        """评估音频质量"""
        # 计算信噪比
        signal_power = np.mean(audio_array ** 2)
        noise_power = np.var(audio_array - np.mean(audio_array))
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        
        # 计算动态范围
        dynamic_range = np.max(audio_array) - np.min(audio_array)
        
        # 计算频谱平坦度
        stft = librosa.stft(audio_array)
        magnitude = np.abs(stft)
        spectral_flatness = np.mean(
            scipy.stats.gmean(magnitude, axis=0) / 
            (np.mean(magnitude, axis=0) + 1e-10)
        )
        
        # 质量评分
        quality_score = 0
        
        if snr > 20:
            quality_score += 3
        elif snr > 10:
            quality_score += 2
        elif snr > 5:
            quality_score += 1
        
        if dynamic_range > 0.5:
            quality_score += 2
        elif dynamic_range > 0.3:
            quality_score += 1
        
        if spectral_flatness > 0.1:
            quality_score += 1
        
        # 映射到质量等级
        if quality_score >= 5:
            return AudioQuality.EXCELLENT
        elif quality_score >= 3:
            return AudioQuality.GOOD
        elif quality_score >= 2:
            return AudioQuality.FAIR
        else:
            return AudioQuality.POOR
    
    @async_timer
    async def _extract_features(
        self,
        audio_array: np.ndarray,
        sr: int,
        request: AnalysisRequest
    ) -> AudioFeatures:
        """提取音频特征"""
        # 在线程池中执行CPU密集型操作
        loop = asyncio.get_event_loop()
        
        # 提取频谱特征
        spectral_features = await loop.run_in_executor(
            self.executor,
            self._extract_spectral_features,
            audio_array,
            sr
        )
        
        # 提取时域特征
        temporal_features = await loop.run_in_executor(
            self.executor,
            self._extract_temporal_features,
            audio_array,
            sr
        )
        
        # 提取高级特征
        advanced_features = await loop.run_in_executor(
            self.executor,
            self._extract_advanced_features,
            audio_array,
            sr
        )
        
        return AudioFeatures(
            mfcc=spectral_features.mfcc.tolist(),
            spectral_centroid=spectral_features.spectral_centroid.tolist(),
            spectral_bandwidth=spectral_features.spectral_bandwidth.tolist(),
            spectral_rolloff=spectral_features.spectral_rolloff.tolist(),
            zero_crossing_rate=spectral_features.zero_crossing_rate.tolist(),
            chroma=spectral_features.chroma.tolist(),
            mel_spectrogram=spectral_features.mel_spectrogram.tolist(),
            rms_energy=temporal_features.rms_energy.tolist(),
            tempo=temporal_features.tempo,
            onset_frames=temporal_features.onset_frames.tolist(),
            duration=temporal_features.duration,
            silence_ratio=temporal_features.silence_ratio,
            **advanced_features
        )
    
    def _extract_spectral_features(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> SpectralFeatures:
        """提取频谱特征"""
        # MFCC特征
        mfcc = librosa.feature.mfcc(
            y=audio_array,
            sr=sr,
            n_mfcc=self.n_mfcc,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        
        # 频谱质心
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 频谱带宽
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 频谱滚降
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 过零率
        zero_crossing_rate = librosa.feature.zero_crossing_rate(
            audio_array,
            hop_length=self.hop_length
        )
        
        # 色度特征
        chroma = librosa.feature.chroma_stft(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 梅尔频谱图
        mel_spectrogram = librosa.feature.melspectrogram(
            y=audio_array,
            sr=sr,
            n_mels=self.n_mels,
            hop_length=self.hop_length
        )
        
        return SpectralFeatures(
            mfcc=mfcc,
            spectral_centroid=spectral_centroid,
            spectral_bandwidth=spectral_bandwidth,
            spectral_rolloff=spectral_rolloff,
            zero_crossing_rate=zero_crossing_rate,
            chroma=chroma,
            mel_spectrogram=mel_spectrogram
        )
    
    def _extract_temporal_features(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> TemporalFeatures:
        """提取时域特征"""
        # RMS能量
        rms_energy = librosa.feature.rms(
            y=audio_array,
            hop_length=self.hop_length
        )
        
        # 节拍和速度
        tempo, beat_frames = librosa.beat.beat_track(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 起始点检测
        onset_frames = librosa.onset.onset_detect(
            y=audio_array,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # 持续时间
        duration = len(audio_array) / sr
        
        # 静音比例
        silence_threshold = np.max(np.abs(audio_array)) * 0.01
        silence_frames = np.sum(np.abs(audio_array) < silence_threshold)
        silence_ratio = silence_frames / len(audio_array)
        
        return TemporalFeatures(
            rms_energy=rms_energy[0],
            tempo=float(tempo),
            beat_frames=beat_frames,
            onset_frames=onset_frames,
            duration=duration,
            silence_ratio=silence_ratio
        )
    
    def _extract_advanced_features(
        self,
        audio_array: np.ndarray,
        sr: int
    ) -> Dict[str, Any]:
        """提取高级特征"""
        # 统计特征
        mean_amplitude = np.mean(np.abs(audio_array))
        std_amplitude = np.std(audio_array)
        skewness = skew(audio_array)
        kurt = kurtosis(audio_array)
        
        # 频域统计
        fft = np.fft.fft(audio_array)
        magnitude_spectrum = np.abs(fft)
        power_spectrum = magnitude_spectrum ** 2
        
        # 频谱质心
        freqs = np.fft.fftfreq(len(fft), 1/sr)
        spectral_centroid_manual = np.sum(
            freqs[:len(freqs)//2] * magnitude_spectrum[:len(freqs)//2]
        ) / np.sum(magnitude_spectrum[:len(freqs)//2])
        
        # 频谱扩散
        spectral_spread = np.sqrt(
            np.sum(
                ((freqs[:len(freqs)//2] - spectral_centroid_manual) ** 2) * 
                magnitude_spectrum[:len(freqs)//2]
            ) / np.sum(magnitude_spectrum[:len(freqs)//2])
        )
        
        return {
            "mean_amplitude": float(mean_amplitude),
            "std_amplitude": float(std_amplitude),
            "skewness": float(skewness),
            "kurtosis": float(kurt),
            "spectral_centroid_manual": float(spectral_centroid_manual),
            "spectral_spread": float(spectral_spread),
            "fundamental_frequency": self._estimate_f0(audio_array, sr),
            "harmonic_ratio": self._calculate_harmonic_ratio(audio_array, sr)
        }
    
    def _estimate_f0(self, audio_array: np.ndarray, sr: int) -> float:
        """估计基频"""
        try:
            f0 = librosa.yin(
                audio_array,
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=sr
            )
            return float(np.median(f0[f0 > 0]))
        except Exception:
            return 0.0
    
    def _calculate_harmonic_ratio(self, audio_array: np.ndarray, sr: int) -> float:
        """计算谐波比"""
        try:
            harmonic, percussive = librosa.effects.hpss(audio_array)
            harmonic_energy = np.sum(harmonic ** 2)
            total_energy = np.sum(audio_array ** 2)
            return float(harmonic_energy / (total_energy + 1e-10))
        except Exception:
            return 0.0
    
    def _generate_cache_key(
        self,
        audio_data: Union[bytes, np.ndarray, str, Path],
        request: AnalysisRequest
    ) -> str:
        """生成缓存键"""
        # 创建数据哈希
        if isinstance(audio_data, bytes):
            data_hash = hashlib.md5(audio_data).hexdigest()
        elif isinstance(audio_data, np.ndarray):
            data_hash = hashlib.md5(audio_data.tobytes()).hexdigest()
        else:
            # 文件路径，使用文件内容哈希
            with open(audio_data, 'rb') as f:
                data_hash = hashlib.md5(f.read()).hexdigest()
        
        # 创建请求参数哈希
        request_str = f"{request.analysis_type}_{request.enable_tcm_analysis}_{request.enable_emotion_analysis}"
        request_hash = hashlib.md5(request_str.encode()).hexdigest()
        
        return f"audio_analysis_{data_hash}_{request_hash}"
    
    async def cleanup(self) -> None:
        """清理资源"""
        if self.executor:
            self.executor.shutdown(wait=True)
        logger.info("音频分析器资源清理完成")