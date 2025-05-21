"""
音频分析器核心模块 - 负责处理和分析各种音频输入
"""
import os
import time
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

import torch
import librosa
import soundfile as sf
from scipy import signal

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """音频分析器基类，提供音频处理和分析的核心功能"""
    
    def __init__(self, config: Dict):
        """
        初始化音频分析器
        
        Args:
            config: 配置字典，包含音频处理参数
        """
        self.config = config
        self.audio_config = config.get("audio_processing", {})
        
        # 基本参数
        self.default_sample_rate = self.audio_config.get("default_sample_rate", 16000)
        self.default_channels = self.audio_config.get("default_channels", 1)
        self.supported_formats = self.audio_config.get("supported_formats", ["wav", "mp3", "flac"])
        self.max_duration = self.audio_config.get("max_duration", 300)  # 秒
        self.min_duration = self.audio_config.get("min_duration", 1)  # 秒
        self.max_file_size = self.audio_config.get("max_file_size", 50) * 1024 * 1024  # 转为字节
        self.chunk_size = self.audio_config.get("chunk_size", 4096)
        
        # 预处理选项
        self.noise_reduction = self.audio_config.get("noise_reduction", True)
        self.normalize_volume = self.audio_config.get("normalize_volume", True)
        self.vad_enabled = self.audio_config.get("vad_enabled", True)
        self.vad_threshold = self.audio_config.get("vad_threshold", 0.5)
        
        # 临时目录
        self.temp_dir = self.audio_config.get("temp_dir", "/tmp/listen_service")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 设备选择
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"初始化音频分析器，使用设备: {self.device}")
        
        # 统计信息
        self.processed_count = 0
        self.total_duration = 0.0
        self.processing_times = []

    def load_audio(self, audio_data: bytes, audio_format: str, 
                  target_sr: Optional[int] = None, 
                  convert_to_mono: bool = True) -> Tuple[np.ndarray, int]:
        """
        加载音频数据
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            target_sr: 目标采样率，如果为None则使用原始采样率
            convert_to_mono: 是否转换为单声道
            
        Returns:
            Tuple[np.ndarray, int]: 音频数据和采样率
        """
        if audio_format not in self.supported_formats:
            raise ValueError(f"不支持的音频格式: {audio_format}")
        
        # 将二进制数据写入临时文件
        tmp_path = os.path.join(self.temp_dir, f"temp_{int(time.time()*1000)}.{audio_format}")
        try:
            with open(tmp_path, "wb") as f:
                f.write(audio_data)
            
            # 加载音频
            y, sr = librosa.load(tmp_path, sr=target_sr, mono=convert_to_mono)
            
            # 验证音频时长
            duration = librosa.get_duration(y=y, sr=sr)
            if duration > self.max_duration:
                raise ValueError(f"音频时长超过限制: {duration}秒 > {self.max_duration}秒")
            if duration < self.min_duration:
                raise ValueError(f"音频时长过短: {duration}秒 < {self.min_duration}秒")
                
            self.total_duration += duration
            return y, sr
        
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    def preprocess_audio(self, audio: np.ndarray, sr: int, 
                         apply_noise_reduction: bool = None,
                         apply_normalization: bool = None,
                         apply_vad: bool = None) -> np.ndarray:
        """
        预处理音频数据
        
        Args:
            audio: 音频数据
            sr: 采样率
            apply_noise_reduction: 是否应用降噪，None使用默认配置
            apply_normalization: 是否应用音量规范化，None使用默认配置
            apply_vad: 是否应用语音活动检测，None使用默认配置
            
        Returns:
            np.ndarray: 预处理后的音频数据
        """
        start_time = time.time()
        processed_audio = audio.copy()
        
        # 应用降噪
        if apply_noise_reduction or (apply_noise_reduction is None and self.noise_reduction):
            processed_audio = self._reduce_noise(processed_audio, sr)
        
        # 应用音量规范化
        if apply_normalization or (apply_normalization is None and self.normalize_volume):
            processed_audio = self._normalize_volume(processed_audio)
        
        # 应用语音活动检测
        if apply_vad or (apply_vad is None and self.vad_enabled):
            processed_audio = self._apply_vad(processed_audio, sr)
        
        processing_time = time.time() - start_time
        self.processing_times.append(processing_time)
        self.processed_count += 1
        
        logger.debug(f"音频预处理完成，耗时: {processing_time:.3f}秒")
        return processed_audio
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        降噪处理，使用简单的频谱减法
        
        Args:
            audio: 原始音频数据
            sr: 采样率
            
        Returns:
            np.ndarray: 降噪后的音频数据
        """
        # 计算静音部分的噪声特征
        # 这里使用前0.5秒或前10%的音频（取较小值）估计噪声特征
        n_samples = len(audio)
        noise_samples = min(int(sr * 0.5), int(n_samples * 0.1))
        
        if noise_samples < 100:  # 音频太短，无法进行有效的噪声估计
            return audio
            
        noise_part = audio[:noise_samples]
        
        # 计算噪声的频谱
        noise_stft = librosa.stft(noise_part)
        noise_power = np.mean(np.abs(noise_stft)**2, axis=1)
        noise_power = noise_power[:, np.newaxis]
        
        # 计算信号的频谱
        audio_stft = librosa.stft(audio)
        audio_power = np.abs(audio_stft)**2
        
        # 应用频谱减法
        mask = 1 - noise_power / (audio_power + 1e-10)
        mask = np.maximum(mask, 0.1)  # 确保掩码不会完全消除信号
        
        # 应用掩码并重建信号
        audio_stft_denoised = audio_stft * mask
        denoised_audio = librosa.istft(audio_stft_denoised, length=len(audio))
        
        return denoised_audio
    
    def _normalize_volume(self, audio: np.ndarray, target_dBFS: float = -20.0) -> np.ndarray:
        """
        音量规范化，将音频调整到目标音量
        
        Args:
            audio: 原始音频数据
            target_dBFS: 目标音量，以分贝为单位
            
        Returns:
            np.ndarray: 规范化后的音频数据
        """
        # 跳过静音音频
        if np.max(np.abs(audio)) < 1e-10:
            return audio
            
        # 计算当前音量
        current_dBFS = 20 * np.log10(np.max(np.abs(audio)))
        
        # 应用增益
        gain = 10 ** ((target_dBFS - current_dBFS) / 20)
        normalized_audio = audio * gain
        
        # 防止裁剪
        if np.max(np.abs(normalized_audio)) > 1.0:
            normalized_audio = normalized_audio / np.max(np.abs(normalized_audio))
            
        return normalized_audio
    
    def _apply_vad(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        应用语音活动检测，移除静音部分
        
        Args:
            audio: 原始音频数据
            sr: 采样率
            
        Returns:
            np.ndarray: 只包含语音部分的音频数据
        """
        # 计算短时能量
        frame_length = int(sr * 0.025)  # 25ms帧
        hop_length = int(sr * 0.010)    # 10ms跳变
        
        # 计算能量包络
        energy = np.array([
            np.sum(audio[i:i+frame_length]**2) 
            for i in range(0, len(audio)-frame_length, hop_length)
        ])
        
        # 计算阈值
        threshold = self.vad_threshold * np.mean(energy)
        
        # 二值化能量，1表示语音，0表示静音
        speech_frames = energy > threshold
        
        # 平滑处理，填充短的静音部分
        min_speech_frames = int(0.1 / (hop_length / sr))  # 100ms
        for i in range(len(speech_frames) - min_speech_frames):
            if sum(speech_frames[i:i+min_speech_frames]) > 0:
                speech_frames[i:i+min_speech_frames] = 1
        
        # 生成只包含语音的音频
        voiced_audio = np.zeros_like(audio)
        for i, is_speech in enumerate(speech_frames):
            if is_speech:
                start = i * hop_length
                end = min(start + frame_length, len(audio))
                voiced_audio[start:end] = audio[start:end]
        
        # 如果语音部分太少，则返回原始音频
        if np.sum(voiced_audio**2) < 0.1 * np.sum(audio**2):
            return audio
            
        return voiced_audio
    
    def extract_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        从音频中提取基本特征
        
        Args:
            audio: 预处理后的音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        features = {}
        
        # 跳过静音音频
        if np.max(np.abs(audio)) < 1e-10:
            logger.warning("音频为静音，无法提取特征")
            return features
        
        # 基本时域特征
        features["duration"] = len(audio) / sr
        features["rms_energy"] = np.sqrt(np.mean(audio**2))
        features["zero_crossing_rate"] = np.mean(librosa.feature.zero_crossing_rate(audio))
        
        # 频域特征
        # MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        features["mfccs_mean"] = np.mean(mfccs, axis=1).tolist()
        features["mfccs_std"] = np.std(mfccs, axis=1).tolist()
        
        # 频谱中心
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features["spectral_centroid_mean"] = float(np.mean(spectral_centroid))
        features["spectral_centroid_std"] = float(np.std(spectral_centroid))
        
        # 频谱带宽
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        features["spectral_bandwidth_mean"] = float(np.mean(spectral_bandwidth))
        
        # 频谱对比度
        spectral_contrast = librosa.feature.spectral_contrast(y=audio, sr=sr)
        features["spectral_contrast_mean"] = np.mean(spectral_contrast, axis=1).tolist()
        
        # 基频估计（F0）
        if len(audio) / sr > 0.5:  # 只处理长度超过0.5秒的音频
            f0, voiced_flag, _ = librosa.pyin(audio, 
                                             fmin=librosa.note_to_hz('C2'), 
                                             fmax=librosa.note_to_hz('C7'),
                                             sr=sr)
            # 去除NaN值
            f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
            
            if len(f0) > 0:
                features["f0_mean"] = float(np.mean(f0))
                features["f0_std"] = float(np.std(f0))
                features["f0_min"] = float(np.min(f0))
                features["f0_max"] = float(np.max(f0))
        
        return features
    
    def save_audio(self, audio: np.ndarray, sr: int, filename: str) -> str:
        """
        保存音频文件
        
        Args:
            audio: 音频数据
            sr: 采样率
            filename: 文件名
            
        Returns:
            str: 保存文件的完整路径
        """
        filepath = os.path.join(self.temp_dir, filename)
        sf.write(filepath, audio, sr)
        return filepath
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        avg_processing_time = np.mean(self.processing_times) if self.processing_times else 0
        
        return {
            "processed_count": self.processed_count,
            "total_duration": self.total_duration,
            "avg_processing_time": avg_processing_time,
            "device": self.device
        } 