"""
现代化音频分析器

基于 Python 3.13.3 和异步处理的高性能音频分析模块，
专为中医闻诊设计，支持语音特征提取、声音分析和情绪识别。
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile as sf
import structlog
import torch
import webrtcvad
from sklearn.preprocessing import StandardScaler

from ..config.settings import get_settings
from ..models.audio_models import (
    AudioAnalysisRequest,
    AudioAnalysisResponse,
    VoiceFeatures,
)
from ..models.tcm_models import TCMDiagnosis
from ..utils.cache import AudioCache
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


@dataclass
class AudioProcessingConfig:
    """音频处理配置"""

    sample_rate: int = 16000
    frame_length: int = 2048
    hop_length: int = 512
    n_mels: int = 128
    n_mfcc: int = 13
    max_duration: float = 300.0  # 5分钟
    min_duration: float = 0.5  # 0.5秒
    enable_gpu: bool = True
    batch_size: int = 32


class AudioAnalyzer:
    """
    现代化音频分析器

    提供高性能的音频处理和特征提取功能，专为中医闻诊优化。
    支持异步处理、GPU加速和智能缓存。
    """

    def __init__(
        self,
        config: AudioProcessingConfig | None = None,
        cache_enabled: bool = True,
        max_workers: int = 4,
    ) -> None:
        """
        初始化音频分析器

        Args:
            config: 音频处理配置
            cache_enabled: 是否启用缓存
            max_workers: 最大工作线程数
        """
        self.config = config or AudioProcessingConfig()
        self.settings = get_settings()
        self.cache = AudioCache() if cache_enabled else None
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # 设备配置
        self.device = self._setup_device()

        # VAD 配置
        self.vad = webrtcvad.Vad(2)  # 中等敏感度

        # 特征缩放器
        self.scaler = StandardScaler()

        # 性能监控
        self.performance_stats = {
            "total_processed": 0,
            "total_duration": 0.0,
            "average_processing_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        logger.info(
            "音频分析器初始化完成",
            device=str(self.device),
            config=self.config,
            cache_enabled=cache_enabled,
        )

    def _setup_device(self) -> torch.device:
        """设置计算设备"""
        if self.config.enable_gpu and torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("使用 GPU 加速", gpu_count=torch.cuda.device_count())
        else:
            device = torch.device("cpu")
            logger.info("使用 CPU 处理")
        return device

    @async_timer
    async def analyze_audio(
        self,
        audio_data: np.ndarray | bytes | str | Path,
        request: AudioAnalysisRequest | None = None,
    ) -> AudioAnalysisResponse:
        """
        异步音频分析主入口

        Args:
            audio_data: 音频数据（数组、字节、文件路径）
            request: 分析请求参数

        Returns:
            音频分析结果
        """
        start_time = time.time()

        try:
            # 检查缓存
            cache_key = self._generate_cache_key(audio_data, request)
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    self.performance_stats["cache_hits"] += 1
                    logger.info("缓存命中", cache_key=cache_key)
                    return cached_result
                self.performance_stats["cache_misses"] += 1

            # 预处理音频
            processed_audio, metadata = await self._preprocess_audio(audio_data)

            # 并行特征提取
            features = await self._extract_features_parallel(processed_audio)

            # 中医特征分析
            tcm_features = await self._analyze_tcm_features(features, processed_audio)

            # 构建响应
            response = AudioAnalysisResponse(
                voice_features=features,
                tcm_diagnosis=tcm_features,
                metadata=metadata,
                processing_time=time.time() - start_time,
            )

            # 缓存结果
            if self.cache:
                await self.cache.set(cache_key, response)

            # 更新统计
            self._update_performance_stats(time.time() - start_time)

            logger.info(
                "音频分析完成",
                processing_time=response.processing_time,
                features_count=len(features.mfcc) if features.mfcc is not None else 0,
            )

            return response

        except Exception as e:
            logger.error("音频分析失败", error=str(e), exc_info=True)
            raise

    async def _preprocess_audio(
        self, audio_data: np.ndarray | bytes | str | Path
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """
        异步音频预处理

        Args:
            audio_data: 原始音频数据

        Returns:
            处理后的音频数组和元数据
        """
        loop = asyncio.get_event_loop()

        # 在线程池中执行 I/O 密集型操作
        audio_array, sample_rate = await loop.run_in_executor(
            self.executor, self._load_audio, audio_data
        )

        # 音频验证
        self._validate_audio(audio_array, sample_rate)

        # 重采样到目标采样率
        if sample_rate != self.config.sample_rate:
            audio_array = await loop.run_in_executor(
                self.executor,
                librosa.resample,
                audio_array,
                orig_sr=sample_rate,
                target_sr=self.config.sample_rate,
            )

        # 音频增强
        enhanced_audio = await self._enhance_audio(audio_array)

        # 语音活动检测
        voice_segments = await self._detect_voice_activity(enhanced_audio)

        metadata = {
            "original_sample_rate": sample_rate,
            "target_sample_rate": self.config.sample_rate,
            "duration": len(enhanced_audio) / self.config.sample_rate,
            "voice_segments": voice_segments,
            "enhancement_applied": True,
        }

        return enhanced_audio, metadata

    def _load_audio(
        self, audio_data: np.ndarray | bytes | str | Path
    ) -> tuple[np.ndarray, int]:
        """加载音频数据"""
        if isinstance(audio_data, np.ndarray):
            return audio_data, self.config.sample_rate
        elif isinstance(audio_data, (str, Path)):
            return librosa.load(str(audio_data), sr=None)
        elif isinstance(audio_data, bytes):
            # 处理字节数据
            import io

            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            return audio_array, sample_rate
        else:
            raise ValueError(f"不支持的音频数据类型: {type(audio_data)}")

    def _validate_audio(self, audio_array: np.ndarray, sample_rate: int) -> None:
        """验证音频数据"""
        duration = len(audio_array) / sample_rate

        if duration < self.config.min_duration:
            raise ValueError(
                f"音频时长过短: {duration:.2f}s < {self.config.min_duration}s"
            )

        if duration > self.config.max_duration:
            raise ValueError(
                f"音频时长过长: {duration:.2f}s > {self.config.max_duration}s"
            )

        if len(audio_array) == 0:
            raise ValueError("音频数据为空")

    async def _enhance_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """音频增强处理"""
        loop = asyncio.get_event_loop()

        # 降噪处理
        enhanced = await loop.run_in_executor(
            self.executor, self._spectral_subtraction_denoise, audio_array
        )

        # 音量归一化
        enhanced = enhanced / (np.max(np.abs(enhanced)) + 1e-8)

        return enhanced

    def _spectral_subtraction_denoise(self, audio: np.ndarray) -> np.ndarray:
        """频谱减法降噪"""
        # 简化的频谱减法实现
        stft = librosa.stft(audio, hop_length=self.config.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)

        # 估计噪声谱（使用前几帧）
        noise_frames = min(10, magnitude.shape[1] // 4)
        noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)

        # 频谱减法
        alpha = 2.0  # 过减因子
        enhanced_magnitude = magnitude - alpha * noise_spectrum
        enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)

        # 重构音频
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=self.config.hop_length)

        return enhanced_audio

    async def _detect_voice_activity(
        self, audio: np.ndarray
    ) -> list[tuple[float, float]]:
        """语音活动检测"""
        loop = asyncio.get_event_loop()

        return await loop.run_in_executor(self.executor, self._vad_segments, audio)

    def _vad_segments(self, audio: np.ndarray) -> list[tuple[float, float]]:
        """VAD 分段检测"""
        # 转换为 16kHz, 16-bit PCM
        audio_16k = librosa.resample(
            audio, orig_sr=self.config.sample_rate, target_sr=16000
        )
        audio_int16 = (audio_16k * 32767).astype(np.int16)

        frame_duration = 30  # ms
        frame_size = int(16000 * frame_duration / 1000)

        segments = []
        start_time = None

        for i in range(0, len(audio_int16) - frame_size, frame_size):
            frame = audio_int16[i : i + frame_size].tobytes()

            if self.vad.is_speech(frame, 16000):
                if start_time is None:
                    start_time = i / 16000
            else:
                if start_time is not None:
                    end_time = i / 16000
                    segments.append((start_time, end_time))
                    start_time = None

        # 处理最后一个段
        if start_time is not None:
            segments.append((start_time, len(audio_int16) / 16000))

        return segments

    async def _extract_features_parallel(self, audio: np.ndarray) -> VoiceFeatures:
        """并行特征提取"""
        loop = asyncio.get_event_loop()

        # 创建并行任务
        tasks = [
            loop.run_in_executor(self.executor, self._extract_mfcc, audio),
            loop.run_in_executor(self.executor, self._extract_spectral_features, audio),
            loop.run_in_executor(self.executor, self._extract_prosodic_features, audio),
            loop.run_in_executor(
                self.executor, self._extract_voice_quality_features, audio
            ),
        ]

        # 等待所有任务完成
        mfcc, spectral, prosodic, voice_quality = await asyncio.gather(*tasks)

        return VoiceFeatures(
            mfcc=mfcc,
            spectral_features=spectral,
            prosodic_features=prosodic,
            voice_quality=voice_quality,
        )

    def _extract_mfcc(self, audio: np.ndarray) -> np.ndarray:
        """提取 MFCC 特征"""
        mfcc = librosa.feature.mfcc(
            y=audio,
            sr=self.config.sample_rate,
            n_mfcc=self.config.n_mfcc,
            n_fft=self.config.frame_length,
            hop_length=self.config.hop_length,
        )
        return mfcc

    def _extract_spectral_features(self, audio: np.ndarray) -> dict[str, np.ndarray]:
        """提取频谱特征"""
        # 频谱质心
        spectral_centroids = librosa.feature.spectral_centroid(
            y=audio, sr=self.config.sample_rate
        )[0]

        # 频谱带宽
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio, sr=self.config.sample_rate
        )[0]

        # 频谱滚降
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, sr=self.config.sample_rate
        )[0]

        # 零交叉率
        zcr = librosa.feature.zero_crossing_rate(audio)[0]

        return {
            "spectral_centroids": spectral_centroids,
            "spectral_bandwidth": spectral_bandwidth,
            "spectral_rolloff": spectral_rolloff,
            "zero_crossing_rate": zcr,
        }

    def _extract_prosodic_features(self, audio: np.ndarray) -> dict[str, float]:
        """提取韵律特征"""
        # 基频提取
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=self.config.sample_rate,
        )

        # 去除 NaN 值
        f0_clean = f0[~np.isnan(f0)]

        if len(f0_clean) > 0:
            f0_mean = np.mean(f0_clean)
            f0_std = np.std(f0_clean)
            f0_range = np.max(f0_clean) - np.min(f0_clean)
        else:
            f0_mean = f0_std = f0_range = 0.0

        # 语音速率（简化计算）
        speech_rate = len(audio) / self.config.sample_rate

        return {
            "f0_mean": f0_mean,
            "f0_std": f0_std,
            "f0_range": f0_range,
            "speech_rate": speech_rate,
            "voiced_ratio": np.mean(voiced_flag),
        }

    def _extract_voice_quality_features(self, audio: np.ndarray) -> dict[str, float]:
        """提取音质特征"""
        # 抖动和颤动（简化计算）
        stft = librosa.stft(audio, hop_length=self.config.hop_length)
        magnitude = np.abs(stft)

        # 谐噪比估计
        harmonic, percussive = librosa.decompose.hpss(magnitude)
        hnr = np.mean(harmonic) / (np.mean(percussive) + 1e-8)

        # 频谱平坦度
        spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=audio))

        # RMS 能量
        rms_energy = np.mean(librosa.feature.rms(y=audio))

        return {
            "harmonic_noise_ratio": float(hnr),
            "spectral_flatness": float(spectral_flatness),
            "rms_energy": float(rms_energy),
        }

    async def _analyze_tcm_features(
        self, features: VoiceFeatures, audio: np.ndarray
    ) -> TCMDiagnosis:
        """中医特征分析"""
        # 这里应该调用专门的中医分析器
        # 暂时返回基础分析结果
        return TCMDiagnosis(
            constitution_type="平和质",  # 默认体质
            emotion_state="平静",
            organ_analysis={},
            confidence_score=0.8,
        )

    def _generate_cache_key(
        self,
        audio_data: np.ndarray | bytes | str | Path,
        request: AudioAnalysisRequest | None,
    ) -> str:
        """生成缓存键"""
        import hashlib

        # 简化的缓存键生成
        if isinstance(audio_data, (str, Path)):
            key_data = str(audio_data)
        else:
            key_data = str(
                hash(
                    audio_data.tobytes()
                    if hasattr(audio_data, "tobytes")
                    else str(audio_data)
                )
            )

        if request:
            key_data += str(request.dict())

        return hashlib.md5(key_data.encode()).hexdigest()

    def _update_performance_stats(self, processing_time: float) -> None:
        """更新性能统计"""
        self.performance_stats["total_processed"] += 1
        self.performance_stats["total_duration"] += processing_time
        self.performance_stats["average_processing_time"] = (
            self.performance_stats["total_duration"]
            / self.performance_stats["total_processed"]
        )

    async def get_performance_stats(self) -> dict[str, Any]:
        """获取性能统计"""
        return self.performance_stats.copy()

    async def cleanup(self) -> None:
        """清理资源"""
        self.executor.shutdown(wait=True)
        if self.cache:
            await self.cache.close()
        logger.info("音频分析器资源清理完成")
