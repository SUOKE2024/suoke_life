"""
语音处理器

专门处理语音信号的预处理、特征提取和质量评估。
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional

import structlog

from ..models.audio_models import AudioFeatures
from ..utils.performance import async_timer

logger = structlog.get_logger(__name__)


class VoiceProcessor:
    """语音处理器"""

    def __init__(self) -> None:
        """初始化语音处理器"""
        self.sample_rate = 16000  # 标准采样率
        self.frame_length = 1024
        self.hop_length = 512

    @async_timer
    async def process_voice(
        self,
        audio_data: np.ndarray,
        sample_rate: int = 16000
    ) -> AudioFeatures:
        """
        处理语音数据并提取特征

        Args:
            audio_data: 音频数据
            sample_rate: 采样率

        Returns:
            音频特征
        """
        try:
            # 预处理音频
            processed_audio = await self._preprocess_audio(audio_data, sample_rate)

            # 提取基本特征
            features = AudioFeatures(
                duration=len(audio_data) / sample_rate,
                sample_rate=sample_rate,
                channels=1,
                bit_depth=16,
                file_size=len(audio_data) * 2,  # 假设16位
                format="wav",
                
                # 基本音频特征
                rms_energy=float(np.sqrt(np.mean(processed_audio ** 2))),
                zero_crossing_rate=self._calculate_zcr(processed_audio),
                spectral_centroid=self._calculate_spectral_centroid(processed_audio),
                spectral_bandwidth=self._calculate_spectral_bandwidth(processed_audio),
                spectral_rolloff=self._calculate_spectral_rolloff(processed_audio),
                
                # MFCC特征
                mfcc=self._extract_mfcc_features(processed_audio),
                
                # 基音特征
                pitch_mean=self._calculate_pitch_mean(processed_audio),
                pitch_std=self._calculate_pitch_std(processed_audio),
                
                # 其他特征
                tempo=120.0,  # 默认值
                energy_mean=float(np.mean(processed_audio ** 2)),
                energy_std=float(np.std(processed_audio ** 2))
            )

            self.logger.info("语音处理完成", duration=features.duration)
            return features

        except Exception as e:
            logger.error("语音处理失败", error=str(e))
            raise

    async def _preprocess_audio(
        self,
        audio_data: np.ndarray,
        sample_rate: int
    ) -> np.ndarray:
        """预处理音频数据"""
        # 归一化
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        # 预加重
        audio_data = np.append(audio_data[0], audio_data[1:] - 0.97 * audio_data[:-1])
        
        return audio_data

    def _calculate_zcr(self, audio_data: np.ndarray) -> float:
        """计算过零率"""
        zero_crossings = np.where(np.diff(np.sign(audio_data)))[0]
        return len(zero_crossings) / len(audio_data)

    def _calculate_spectral_centroid(self, audio_data: np.ndarray) -> float:
        """计算频谱质心"""
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_data), 1 / self.sample_rate)
        
        positive_freqs = freqs[:len(freqs) // 2]
        positive_magnitude = magnitude[:len(magnitude) // 2]
        
        if np.sum(positive_magnitude) > 0:
            return float(np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude))
        return 0.0

    def _calculate_spectral_bandwidth(self, audio_data: np.ndarray) -> float:
        """计算频谱带宽"""
        centroid = self._calculate_spectral_centroid(audio_data)
        
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_data), 1 / self.sample_rate)
        
        positive_freqs = freqs[:len(freqs) // 2]
        positive_magnitude = magnitude[:len(magnitude) // 2]
        
        if np.sum(positive_magnitude) > 0:
            bandwidth = np.sqrt(
                np.sum(((positive_freqs - centroid) ** 2) * positive_magnitude) /
                np.sum(positive_magnitude)
            )
            return float(bandwidth)
        return 0.0

    def _calculate_spectral_rolloff(self, audio_data: np.ndarray) -> float:
        """计算频谱滚降"""
        fft = np.fft.fft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio_data), 1 / self.sample_rate)
        
        positive_freqs = freqs[:len(freqs) // 2]
        positive_magnitude = magnitude[:len(magnitude) // 2]
        
        cumsum = np.cumsum(positive_magnitude)
        if cumsum[-1] > 0:
            rolloff_idx = np.where(cumsum >= 0.85 * cumsum[-1])[0]
            if len(rolloff_idx) > 0:
                return float(positive_freqs[rolloff_idx[0]])
        return 0.0

    def _extract_mfcc_features(self, audio_data: np.ndarray) -> List[float]:
        """提取MFCC特征（简化版本）"""
        # 简化的MFCC实现
        fft = np.fft.fft(audio_data, n=2048)
        power_spectrum = np.abs(fft) ** 2
        
        # 简化的Mel滤波器
        n_mels = 13
        mel_filters = np.random.random((n_mels, len(power_spectrum) // 2))
        
        # 应用滤波器
        mel_spectrum = np.dot(mel_filters, power_spectrum[:len(power_spectrum) // 2])
        
        # 对数变换
        log_mel = np.log(mel_spectrum + 1e-10)
        
        # 简化的DCT
        mfcc = np.fft.dct(log_mel)[:13]
        
        return mfcc.tolist()

    def _calculate_pitch_mean(self, audio_data: np.ndarray) -> float:
        """计算基音平均值（简化版本）"""
        # 简化的基音估计
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]
        
        # 寻找峰值
        min_period = int(self.sample_rate / 500)  # 最高500Hz
        max_period = int(self.sample_rate / 50)   # 最低50Hz
        
        if len(autocorr) > max_period:
            peak_idx = np.argmax(autocorr[min_period:max_period]) + min_period
            if autocorr[peak_idx] > 0.3 * autocorr[0]:
                return float(self.sample_rate / peak_idx)
        
        return 150.0  # 默认基音频率

    def _calculate_pitch_std(self, audio_data: np.ndarray) -> float:
        """计算基音标准差（简化版本）"""
        # 简化实现，返回固定值
        return 20.0

    async def batch_process_voices(self, audio_data_list: List[np.ndarray]) -> List[AudioFeatures]:
        """批量处理语音"""
        tasks = [self.process_voice(audio_data) for audio_data in audio_data_list]
        return await asyncio.gather(*tasks) 