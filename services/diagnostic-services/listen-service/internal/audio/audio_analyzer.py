"""
音频分析器核心模块 - 负责处理和分析各种音频输入
优化版本：支持异步处理、改进内存管理、增强错误处理
"""
import os
import time
import logging
import asyncio
import tempfile
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import torch
import librosa
import soundfile as sf
from scipy import signal
import aiofiles
from numba import jit

logger = logging.getLogger(__name__)

@dataclass
class AudioProcessingStats:
    """音频处理统计信息"""
    processed_count: int = 0
    total_duration: float = 0.0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    peak_memory_usage: int = 0
    error_count: int = 0

class AudioAnalyzerError(Exception):
    """音频分析器自定义异常"""
    pass

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
        self.supported_formats = self.audio_config.get("supported_formats", ["wav", "mp3", "flac", "m4a"])
        self.max_duration = self.audio_config.get("max_duration", 300)  # 秒
        self.min_duration = self.audio_config.get("min_duration", 0.5)  # 秒
        self.max_file_size = self.audio_config.get("max_file_size", 50) * 1024 * 1024  # 转为字节
        self.chunk_size = self.audio_config.get("chunk_size", 4096)
        
        # 预处理选项
        self.noise_reduction = self.audio_config.get("noise_reduction", True)
        self.normalize_volume = self.audio_config.get("normalize_volume", True)
        self.vad_enabled = self.audio_config.get("vad_enabled", True)
        self.vad_threshold = self.audio_config.get("vad_threshold", 0.5)
        
        # 性能优化选项
        self.enable_gpu = self.audio_config.get("enable_gpu", True)
        self.batch_processing = self.audio_config.get("batch_processing", True)
        self.cache_enabled = self.audio_config.get("cache_enabled", True)
        self.max_concurrent_tasks = self.audio_config.get("max_concurrent_tasks", 4)
        
        # 临时目录
        self.temp_dir = Path(self.audio_config.get("temp_dir", "/tmp/listen_service"))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 设备选择
        if self.enable_gpu and torch.cuda.is_available():
            self.device = "cuda"
            torch.backends.cudnn.benchmark = True  # 优化CUDA性能
        else:
            self.device = "cpu"
        
        logger.info(f"初始化音频分析器，使用设备: {self.device}")
        
        # 统计信息
        self.stats = AudioProcessingStats()
        self._processing_times = []
        self._memory_usage = []
        
        # 异步信号量，限制并发处理数量
        self._semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # 缓存
        self._feature_cache = {} if self.cache_enabled else None

    async def load_audio_async(self, audio_data: bytes, audio_format: str, 
                              target_sr: Optional[int] = None, 
                              convert_to_mono: bool = True) -> Tuple[np.ndarray, int]:
        """
        异步加载音频数据
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            target_sr: 目标采样率，如果为None则使用原始采样率
            convert_to_mono: 是否转换为单声道
            
        Returns:
            Tuple[np.ndarray, int]: 音频数据和采样率
            
        Raises:
            AudioAnalyzerError: 音频处理相关错误
        """
        async with self._semaphore:
            try:
                return await self._load_audio_impl(audio_data, audio_format, target_sr, convert_to_mono)
            except Exception as e:
                self.stats.error_count += 1
                logger.error(f"异步加载音频失败: {str(e)}")
                raise AudioAnalyzerError(f"音频加载失败: {str(e)}") from e

    async def _load_audio_impl(self, audio_data: bytes, audio_format: str, 
                              target_sr: Optional[int], convert_to_mono: bool) -> Tuple[np.ndarray, int]:
        """音频加载的具体实现"""
        if audio_format not in self.supported_formats:
            raise AudioAnalyzerError(f"不支持的音频格式: {audio_format}")
        
        if len(audio_data) > self.max_file_size:
            raise AudioAnalyzerError(f"音频文件过大: {len(audio_data)} bytes > {self.max_file_size} bytes")
        
        # 使用临时文件异步处理
        async with self._create_temp_file(audio_format) as tmp_path:
            # 异步写入音频数据
            async with aiofiles.open(tmp_path, "wb") as f:
                await f.write(audio_data)
            
            # 在线程池中执行CPU密集型的音频加载
            loop = asyncio.get_event_loop()
            y, sr = await loop.run_in_executor(
                None, 
                self._load_audio_sync, 
                str(tmp_path), 
                target_sr, 
                convert_to_mono
            )
            
            # 验证音频时长
            duration = librosa.get_duration(y=y, sr=sr)
            if duration > self.max_duration:
                raise AudioAnalyzerError(f"音频时长超过限制: {duration}秒 > {self.max_duration}秒")
            if duration < self.min_duration:
                raise AudioAnalyzerError(f"音频时长过短: {duration}秒 < {self.min_duration}秒")
                
            self.stats.total_duration += duration
            return y, sr

    @asynccontextmanager
    async def _create_temp_file(self, audio_format: str):
        """创建临时文件的异步上下文管理器"""
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=f".{audio_format}",
            dir=self.temp_dir,
            delete=False
        )
        tmp_path = tmp_file.name
        tmp_file.close()
        
        try:
            yield tmp_path
        finally:
            # 确保清理临时文件
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _load_audio_sync(self, file_path: str, target_sr: Optional[int], convert_to_mono: bool) -> Tuple[np.ndarray, int]:
        """同步加载音频文件"""
        return librosa.load(file_path, sr=target_sr, mono=convert_to_mono)

    def load_audio(self, audio_data: bytes, audio_format: str, 
                  target_sr: Optional[int] = None, 
                  convert_to_mono: bool = True) -> Tuple[np.ndarray, int]:
        """
        同步加载音频数据（向后兼容）
        
        Args:
            audio_data: 原始音频二进制数据
            audio_format: 音频格式
            target_sr: 目标采样率，如果为None则使用原始采样率
            convert_to_mono: 是否转换为单声道
            
        Returns:
            Tuple[np.ndarray, int]: 音频数据和采样率
        """
        if audio_format not in self.supported_formats:
            raise AudioAnalyzerError(f"不支持的音频格式: {audio_format}")
        
        if len(audio_data) > self.max_file_size:
            raise AudioAnalyzerError(f"音频文件过大: {len(audio_data)} bytes > {self.max_file_size} bytes")
        
        # 将二进制数据写入临时文件
        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", dir=self.temp_dir, delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(audio_data)
        
        try:
            # 加载音频
            y, sr = librosa.load(tmp_path, sr=target_sr, mono=convert_to_mono)
            
            # 验证音频时长
            duration = librosa.get_duration(y=y, sr=sr)
            if duration > self.max_duration:
                raise AudioAnalyzerError(f"音频时长超过限制: {duration}秒 > {self.max_duration}秒")
            if duration < self.min_duration:
                raise AudioAnalyzerError(f"音频时长过短: {duration}秒 < {self.min_duration}秒")
                
            self.stats.total_duration += duration
            return y, sr
        
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    async def preprocess_audio_async(self, audio: np.ndarray, sr: int, 
                                   apply_noise_reduction: bool = None,
                                   apply_normalization: bool = None,
                                   apply_vad: bool = None) -> np.ndarray:
        """
        异步预处理音频数据
        
        Args:
            audio: 音频数据
            sr: 采样率
            apply_noise_reduction: 是否应用降噪，None使用默认配置
            apply_normalization: 是否应用音量规范化，None使用默认配置
            apply_vad: 是否应用语音活动检测，None使用默认配置
            
        Returns:
            np.ndarray: 预处理后的音频数据
        """
        async with self._semaphore:
            start_time = time.time()
            
            try:
                # 在线程池中执行CPU密集型的预处理
                loop = asyncio.get_event_loop()
                processed_audio = await loop.run_in_executor(
                    None,
                    self._preprocess_audio_sync,
                    audio, sr, apply_noise_reduction, apply_normalization, apply_vad
                )
                
                processing_time = time.time() - start_time
                self._processing_times.append(processing_time)
                self.stats.processed_count += 1
                self.stats.total_processing_time += processing_time
                self.stats.average_processing_time = self.stats.total_processing_time / self.stats.processed_count
                
                logger.debug(f"异步音频预处理完成，耗时: {processing_time:.3f}秒")
                return processed_audio
                
            except Exception as e:
                self.stats.error_count += 1
                logger.error(f"异步音频预处理失败: {str(e)}")
                raise AudioAnalyzerError(f"音频预处理失败: {str(e)}") from e

    def _preprocess_audio_sync(self, audio: np.ndarray, sr: int,
                              apply_noise_reduction: bool, apply_normalization: bool, apply_vad: bool) -> np.ndarray:
        """同步预处理音频数据"""
        processed_audio = audio.copy()
        
        # 应用降噪
        if apply_noise_reduction or (apply_noise_reduction is None and self.noise_reduction):
            processed_audio = self._reduce_noise_optimized(processed_audio, sr)
        
        # 应用音量规范化
        if apply_normalization or (apply_normalization is None and self.normalize_volume):
            processed_audio = self._normalize_volume_optimized(processed_audio)
        
        # 应用语音活动检测
        if apply_vad or (apply_vad is None and self.vad_enabled):
            processed_audio = self._apply_vad_optimized(processed_audio, sr)
        
        return processed_audio

    def preprocess_audio(self, audio: np.ndarray, sr: int, 
                         apply_noise_reduction: bool = None,
                         apply_normalization: bool = None,
                         apply_vad: bool = None) -> np.ndarray:
        """
        预处理音频数据（向后兼容的同步版本）
        
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
        
        try:
            processed_audio = self._preprocess_audio_sync(
                audio, sr, apply_noise_reduction, apply_normalization, apply_vad
            )
            
            processing_time = time.time() - start_time
            self._processing_times.append(processing_time)
            self.stats.processed_count += 1
            self.stats.total_processing_time += processing_time
            self.stats.average_processing_time = self.stats.total_processing_time / self.stats.processed_count
            
            logger.debug(f"音频预处理完成，耗时: {processing_time:.3f}秒")
            return processed_audio
            
        except Exception as e:
            self.stats.error_count += 1
            logger.error(f"音频预处理失败: {str(e)}")
            raise AudioAnalyzerError(f"音频预处理失败: {str(e)}") from e

    def _reduce_noise_optimized(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        优化的降噪处理，使用改进的频谱减法
        
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
        
        try:
            # 计算噪声的频谱
            noise_stft = librosa.stft(noise_part, n_fft=1024, hop_length=256)
            noise_power = np.mean(np.abs(noise_stft)**2, axis=1, keepdims=True)
            
            # 计算信号的频谱
            audio_stft = librosa.stft(audio, n_fft=1024, hop_length=256)
            audio_power = np.abs(audio_stft)**2
            
            # 应用改进的频谱减法，使用自适应阈值
            alpha = 2.0  # 过减因子
            beta = 0.01  # 最小保留比例
            
            mask = 1 - alpha * noise_power / (audio_power + 1e-10)
            mask = np.maximum(mask, beta)  # 确保掩码不会完全消除信号
            
            # 平滑掩码以减少音乐噪声
            mask = signal.medfilt(mask, kernel_size=(1, 3))
            
            # 应用掩码并重建信号
            audio_stft_denoised = audio_stft * mask
            denoised_audio = librosa.istft(audio_stft_denoised, length=len(audio), hop_length=256)
            
            return denoised_audio
            
        except Exception as e:
            logger.warning(f"降噪处理失败，返回原始音频: {str(e)}")
            return audio
    
    def _normalize_volume_optimized(self, audio: np.ndarray, target_dBFS: float = -20.0) -> np.ndarray:
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
    
    def _apply_vad_optimized(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        优化的语音活动检测，移除静音部分
        
        Args:
            audio: 原始音频数据
            sr: 采样率
            
        Returns:
            np.ndarray: 移除静音后的音频数据
        """
        try:
            # 使用librosa的能量检测进行VAD
            frame_length = int(sr * 0.025)  # 25ms帧
            hop_length = int(sr * 0.010)    # 10ms跳跃
            
            # 计算短时能量
            energy = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
            
            # 动态阈值计算
            energy_mean = np.mean(energy)
            energy_std = np.std(energy)
            threshold = energy_mean + self.vad_threshold * energy_std
            
            # 找到语音活动区域
            voice_frames = energy > threshold
            
            # 扩展语音区域以避免切断
            voice_frames = np.convolve(voice_frames, np.ones(5), mode='same') > 0
            
            # 将帧索引转换为样本索引
            voice_samples = np.repeat(voice_frames, hop_length)
            
            # 确保长度匹配
            if len(voice_samples) > len(audio):
                voice_samples = voice_samples[:len(audio)]
            elif len(voice_samples) < len(audio):
                voice_samples = np.pad(voice_samples, (0, len(audio) - len(voice_samples)), mode='edge')
            
            # 提取语音部分
            if np.any(voice_samples):
                return audio[voice_samples]
            else:
                # 如果没有检测到语音，返回原始音频
                logger.warning("VAD未检测到语音活动，返回原始音频")
                return audio
                
        except Exception as e:
            logger.warning(f"VAD处理失败，返回原始音频: {str(e)}")
            return audio

    async def extract_features_async(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        异步提取音频特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 提取的特征字典
        """
        async with self._semaphore:
            # 检查缓存
            if self._feature_cache is not None:
                cache_key = hash((audio.tobytes(), sr))
                if cache_key in self._feature_cache:
                    logger.debug("从缓存中获取特征")
                    return self._feature_cache[cache_key]
            
            # 在线程池中执行特征提取
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(None, self._extract_features_sync, audio, sr)
            
            # 缓存结果
            if self._feature_cache is not None and len(self._feature_cache) < 100:  # 限制缓存大小
                self._feature_cache[cache_key] = features
            
            return features

    def _extract_features_sync(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        同步提取音频特征
        
        Args:
            audio: 预处理后的音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        features = {}
        
        try:
            # 跳过静音音频
            if np.max(np.abs(audio)) < 1e-10:
                logger.warning("音频为静音，无法提取特征")
                return features
            
            # 基本时域特征
            features["duration"] = len(audio) / sr
            features["rms_energy"] = float(np.sqrt(np.mean(audio**2)))
            features["zero_crossing_rate"] = float(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
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
            
            # 色度特征
            chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
            features["chroma_mean"] = np.mean(chroma, axis=1).tolist()
            
            # 音调特征
            tonnetz = librosa.feature.tonnetz(y=audio, sr=sr)
            features["tonnetz_mean"] = np.mean(tonnetz, axis=1).tolist()
            
            # 基频估计（F0）
            if len(audio) / sr > 0.5:  # 只处理长度超过0.5秒的音频
                try:
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
                        features["f0_range"] = float(np.max(f0) - np.min(f0))
                        
                        # 计算基频变化率
                        f0_diff = np.diff(f0)
                        features["f0_variation"] = float(np.std(f0_diff)) if len(f0_diff) > 0 else 0.0
                        
                except Exception as e:
                    logger.warning(f"基频提取失败: {str(e)}")
            
            # 中医相关特征
            features.update(self._extract_tcm_features(audio, sr))
            
        except Exception as e:
            logger.error(f"特征提取失败: {str(e)}")
            features["error"] = str(e)
        
        return features

    def _extract_tcm_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        提取中医相关的音频特征
        
        Args:
            audio: 音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 中医相关特征
        """
        tcm_features = {}
        
        try:
            # 声音的气息特征（基于能量变化）
            energy = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
            energy_variation = np.std(energy) / (np.mean(energy) + 1e-10)
            tcm_features["qi_stability"] = float(1.0 / (1.0 + energy_variation))  # 气息稳定性
            
            # 声音的清浊度（基于谐波噪声比）
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            harmonic, percussive = librosa.decompose.hpss(magnitude)
            hnr = np.mean(harmonic) / (np.mean(percussive) + 1e-10)  # 谐波噪声比
            tcm_features["voice_clarity"] = float(np.log(1 + hnr))  # 声音清浊度
            
            # 声音的厚薄度（基于频谱重心）
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
            tcm_features["voice_thickness"] = float(1.0 / (1.0 + np.mean(spectral_centroid) / 1000))
            
            # 声音的强弱度（基于动态范围）
            dynamic_range = np.max(energy) - np.min(energy)
            tcm_features["voice_strength"] = float(dynamic_range)
            
            # 声音的节律性（基于节拍跟踪）
            try:
                tempo, beats = librosa.beat.beat_track(y=audio, sr=sr)
                beat_intervals = np.diff(beats) * (512 / sr)  # 转换为时间间隔
                rhythm_regularity = 1.0 / (1.0 + np.std(beat_intervals)) if len(beat_intervals) > 1 else 0.5
                tcm_features["rhythm_regularity"] = float(rhythm_regularity)
                tcm_features["tempo"] = float(tempo)
            except Exception:
                tcm_features["rhythm_regularity"] = 0.5
                tcm_features["tempo"] = 0.0
                
        except Exception as e:
            logger.warning(f"中医特征提取失败: {str(e)}")
        
        return tcm_features
    
    def extract_features(self, audio: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        从音频中提取基本特征（向后兼容的同步版本）
        
        Args:
            audio: 预处理后的音频数据
            sr: 采样率
            
        Returns:
            Dict[str, Any]: 特征字典
        """
        return self._extract_features_sync(audio, sr)
    
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
        try:
            filepath = self.temp_dir / filename
            sf.write(str(filepath), audio, sr)
            logger.debug(f"音频已保存到: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"保存音频文件失败: {str(e)}")
            raise AudioAnalyzerError(f"保存音频文件失败: {str(e)}") from e

    async def batch_process_async(self, audio_batch: List[Tuple[bytes, str]], 
                                 target_sr: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        批量异步处理音频
        
        Args:
            audio_batch: 音频数据和格式的列表
            target_sr: 目标采样率
            
        Returns:
            List[Dict[str, Any]]: 处理结果列表
        """
        tasks = []
        for audio_data, audio_format in audio_batch:
            task = self._process_single_audio_async(audio_data, audio_format, target_sr)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"批量处理第{i}个音频失败: {str(result)}")
                processed_results.append({"error": str(result)})
            else:
                processed_results.append(result)
        
        return processed_results

    async def _process_single_audio_async(self, audio_data: bytes, audio_format: str, 
                                        target_sr: Optional[int]) -> Dict[str, Any]:
        """处理单个音频的异步方法"""
        try:
            # 加载音频
            audio, sr = await self.load_audio_async(audio_data, audio_format, target_sr)
            
            # 预处理
            processed_audio = await self.preprocess_audio_async(audio, sr)
            
            # 提取特征
            features = await self.extract_features_async(processed_audio, sr)
            
            return {
                "success": True,
                "features": features,
                "audio_info": {
                    "duration": len(audio) / sr,
                    "sample_rate": sr,
                    "channels": 1 if audio.ndim == 1 else audio.shape[0]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def clear_cache(self):
        """清理特征缓存"""
        if self._feature_cache is not None:
            self._feature_cache.clear()
            logger.info("特征缓存已清理")

    def update_memory_usage(self):
        """更新内存使用统计"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            current_memory = memory_info.rss
            
            if current_memory > self.stats.peak_memory_usage:
                self.stats.peak_memory_usage = current_memory
                
            self._memory_usage.append(current_memory)
            
            # 保持最近100个记录
            if len(self._memory_usage) > 100:
                self._memory_usage = self._memory_usage[-100:]
                
        except ImportError:
            pass  # psutil不可用时忽略
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        avg_processing_time = np.mean(self._processing_times) if self._processing_times else 0
        
        return {
            "processed_count": self.stats.processed_count,
            "total_duration": self.stats.total_duration,
            "avg_processing_time": avg_processing_time,
            "device": self.device,
            "total_processing_time": self.stats.total_processing_time,
            "average_processing_time": self.stats.average_processing_time,
            "peak_memory_usage": self.stats.peak_memory_usage,
            "error_count": self.stats.error_count
        } 