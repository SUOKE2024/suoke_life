"""
audio_analysis - 索克生活项目模块
"""

from dataclasses import dataclass
from scipy import signal
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional, Tuple, Union
import asyncio
import joblib
import librosa
import logging
import numpy as np
import pyaudio
import queue
import soundfile as sf
import threading
import torch
import torch.nn as nn
import torch.nn.functional as F
import wave

"""
音频分析核心模块

基于深度学习的中医闻诊音频特征识别和分析
"""


logger = logging.getLogger(__name__)

@dataclass
class AudioFeatures:
    """音频特征数据类"""
    mfcc: np.ndarray
    spectral_centroid: np.ndarray
    spectral_rolloff: np.ndarray
    zero_crossing_rate: np.ndarray
    chroma: np.ndarray
    mel_spectrogram: np.ndarray
    pitch: np.ndarray
    energy: np.ndarray
    formants: List[float]
    voice_quality_metrics: Dict[str, float]

@dataclass
class TCMAudioAnalysis:
    """中医音频分析结果"""
    voice_type: str
    breath_pattern: str
    cough_analysis: Dict[str, Any]
    heart_sound_analysis: Dict[str, Any]
    lung_sound_analysis: Dict[str, Any]
    tcm_interpretation: Dict[str, str]
    confidence_scores: Dict[str, float]

class AdvancedAudioFeatureExtractor:
    """高级音频特征提取器"""

    def __init__(self, sample_rate: int = 22050):
        """TODO: 添加文档字符串"""
        self.sample_rate = sample_rate
        self.n_mfcc = 13
        self.n_fft = 2048
        self.hop_length = 512

    def extract_comprehensive_features(self, audio: np.ndarray) -> AudioFeatures:
        """提取综合音频特征"""
        try:
            # MFCC特征
            mfcc = librosa.feature.mfcc(
                y = audio, sr = self.sample_rate,
                n_mfcc = self.n_mfcc, n_fft = self.n_fft,
                hop_length = self.hop_length
            )

            # 频谱质心
            spectral_centroid = librosa.feature.spectral_centroid(
                y = audio, sr = self.sample_rate, hop_length = self.hop_length
            )

            # 频谱滚降
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y = audio, sr = self.sample_rate, hop_length = self.hop_length
            )

            # 过零率
            zero_crossing_rate = librosa.feature.zero_crossing_rate(
                audio, hop_length = self.hop_length
            )

            # 色度特征
            chroma = librosa.feature.chroma_stft(
                y = audio, sr = self.sample_rate, hop_length = self.hop_length
            )

            # 梅尔频谱图
            mel_spectrogram = librosa.feature.melspectrogram(
                y = audio, sr = self.sample_rate, n_fft = self.n_fft,
                hop_length = self.hop_length
            )

            # 基频提取
            pitch = self._extract_pitch(audio)

            # 能量特征
            energy = self._calculate_energy(audio)

            # 共振峰
            formants = self._extract_formants(audio)

            # 语音质量指标
            voice_quality = self._analyze_voice_quality(audio)

            return AudioFeatures(
                mfcc = mfcc,
                spectral_centroid = spectral_centroid,
                spectral_rolloff = spectral_rolloff,
                zero_crossing_rate = zero_crossing_rate,
                chroma = chroma,
                mel_spectrogram = mel_spectrogram,
                pitch = pitch,
                energy = energy,
                formants = formants,
                voice_quality_metrics = voice_quality
            )

        except Exception as e:
            logger.error(f"音频特征提取失败: {e}")
            return self._get_default_features()

    def _extract_pitch(self, audio: np.ndarray) -> np.ndarray:
        """提取基频"""
        try:
            pitches, magnitudes = librosa.piptrack(
                y = audio, sr = self.sample_rate,
                hop_length = self.hop_length
            )

            # 选择最强的基频
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                pitch_values.append(pitch if pitch > 0 else 0)

            return np.array(pitch_values)

        except Exception as e:
            logger.error(f"基频提取失败: {e}")
            return np.zeros(100)

    def _calculate_energy(self, audio: np.ndarray) -> np.ndarray:
        """计算能量特征"""
        try:
            # 短时能量
            frame_length = 2048
            hop_length = 512

            energy = []
            for i in range(0, len(audio) - frame_length, hop_length):
                frame = audio[i:i + frame_length]
                frame_energy = np.sum(frame**2)
                energy.append(frame_energy)

            return np.array(energy)

        except Exception as e:
            logger.error(f"能量计算失败: {e}")
            return np.zeros(100)

    def _extract_formants(self, audio: np.ndarray) -> List[float]:
        """提取共振峰"""
        try:
            # 使用LPC分析提取共振峰
            # 简化实现，实际应用中可能需要更复杂的算法

            # 预加重
            pre_emphasis = 0.97
            emphasized_audio = np.append(audio[0], audio[1:] - pre_emphasis * audio[: - 1])

            # 窗函数
            windowed = emphasized_audio * np.hamming(len(emphasized_audio))

            # LPC分析
            lpc_order = 12
            lpc_coeffs = librosa.lpc(windowed, order = lpc_order)

            # 从LPC系数计算共振峰
            roots = np.roots(lpc_coeffs)
            roots = roots[np.imag(roots) >=0]

            formants = []
            for root in roots:
                if np.abs(root) < 1:
                    freq = np.angle(root) * self.sample_rate / (2 * np.pi)
                    if 200 < freq < 4000:  # 人声共振峰范围
                        formants.append(freq)

            formants.sort()
            return formants[:4]  # 返回前4个共振峰

        except Exception as e:
            logger.error(f"共振峰提取失败: {e}")
            return [0.0, 0.0, 0.0, 0.0]

    def _analyze_voice_quality(self, audio: np.ndarray) -> Dict[str, float]:
        """分析语音质量"""
        try:
            # 计算各种语音质量指标

            # 基频抖动 (Jitter)
            pitch = self._extract_pitch(audio)
            valid_pitch = pitch[pitch > 0]
            if len(valid_pitch) > 1:
                jitter = np.std(np.diff(valid_pitch)) / np.mean(valid_pitch) if np.mean(valid_pitch) > 0 else 0
            else:
                jitter = 0

            # 振幅微扰 (Shimmer)
            energy = self._calculate_energy(audio)
            if len(energy) > 1:
                shimmer = np.std(np.diff(energy)) / np.mean(energy) if np.mean(energy) > 0 else 0
            else:
                shimmer = 0

            # 谐噪比 (HNR)
            hnr = self._calculate_hnr(audio)

            # 语音清晰度
            clarity = self._calculate_clarity(audio)

            return {
                'jitter': float(jitter),
                'shimmer': float(shimmer),
                'hnr': float(hnr),
                'clarity': float(clarity)
            }

        except Exception as e:
            logger.error(f"语音质量分析失败: {e}")
            return {'jitter': 0.0, 'shimmer': 0.0, 'hnr': 0.0, 'clarity': 0.0}

    def _calculate_hnr(self, audio: np.ndarray) -> float:
        """计算谐噪比"""
        try:
            # 简化的谐噪比计算
            # 实际应用中需要更精确的算法

            # 自相关函数
            autocorr = np.correlate(audio, audio, mode = 'full')
            autocorr = autocorr[autocorr.size //2:]

            # 找到基频周期
            if len(autocorr) > 1:
                peak_idx = np.argmax(autocorr[1:]) + 1
                if peak_idx > 0:
                    hnr = 10 * np.log10(autocorr[peak_idx] / (autocorr[0] - autocorr[peak_idx] + 1e-10))
                    return max( - 10, min(hnr, 30))  # 限制在合理范围内

            return 0.0

        except Exception as e:
            logger.error(f"谐噪比计算失败: {e}")
            return 0.0

    def _calculate_clarity(self, audio: np.ndarray) -> float:
        """计算语音清晰度"""
        try:
            # 基于频谱特征的清晰度评估
            stft = librosa.stft(audio, hop_length = self.hop_length)
            magnitude = np.abs(stft)

            # 计算频谱平坦度
            spectral_flatness = librosa.feature.spectral_flatness(S = magnitude)
            clarity = 1.0 - np.mean(spectral_flatness)

            return float(np.clip(clarity, 0.0, 1.0))

        except Exception as e:
            logger.error(f"清晰度计算失败: {e}")
            return 0.5

    def _get_default_features(self) -> AudioFeatures:
        """获取默认特征"""
        return AudioFeatures(
            mfcc = np.zeros((self.n_mfcc, 100)),
            spectral_centroid = np.zeros((1, 100)),
            spectral_rolloff = np.zeros((1, 100)),
            zero_crossing_rate = np.zeros((1, 100)),
            chroma = np.zeros((12, 100)),
            mel_spectrogram = np.zeros((128, 100)),
            pitch = np.zeros(100),
            energy = np.zeros(100),
            formants = [0.0, 0.0, 0.0, 0.0],
            voice_quality_metrics = {'jitter': 0.0, 'shimmer': 0.0, 'hnr': 0.0, 'clarity': 0.0}
        )

class TCMAudioAnalyzer:
    """中医音频分析器"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.feature_extractor = AdvancedAudioFeatureExtractor()

        # 中医音频特征映射
        self.tcm_voice_mapping = {
            'high_pitch': '声音尖细 - 肺气不足',
            'low_pitch': '声音低沉 - 肾气虚弱',
            'hoarse': '声音嘶哑 - 肺阴不足',
            'weak': '声音微弱 - 气虚',
            'loud': '声音洪亮 - 气血充足',
            'trembling': '声音颤抖 - 气血不稳'
        }

        self.tcm_breath_mapping = {
            'shallow': '呼吸浅短 - 肺气虚',
            'deep': '呼吸深长 - 肺气充足',
            'rapid': '呼吸急促 - 肺热',
            'slow': '呼吸缓慢 - 肺寒',
            'irregular': '呼吸不规律 - 气机不畅'
        }

    def analyze_tcm_audio(self, audio: np.ndarray, audio_type: str = "voice") -> TCMAudioAnalysis:
        """中医音频分析"""
        try:
            # 提取音频特征
            features = self.feature_extractor.extract_comprehensive_features(audio)

            # 分析语音类型
            voice_type = self._classify_voice_type(features)

            # 分析呼吸模式
            breath_pattern = self._analyze_breath_pattern(features, audio_type)

            # 咳嗽分析
            cough_analysis = self._analyze_cough(features, audio_type)

            # 心音分析
            heart_sound_analysis = self._analyze_heart_sounds(features, audio_type)

            # 肺音分析
            lung_sound_analysis = self._analyze_lung_sounds(features, audio_type)

            # 中医解释
            tcm_interpretation = self._generate_tcm_interpretation(
                voice_type, breath_pattern, cough_analysis
            )

            # 置信度评估
            confidence_scores = self._calculate_confidence_scores(features)

            return TCMAudioAnalysis(
                voice_type = voice_type,
                breath_pattern = breath_pattern,
                cough_analysis = cough_analysis,
                heart_sound_analysis = heart_sound_analysis,
                lung_sound_analysis = lung_sound_analysis,
                tcm_interpretation = tcm_interpretation,
                confidence_scores = confidence_scores
            )

        except Exception as e:
            logger.error(f"中医音频分析失败: {e}")
            return self._get_default_analysis()

    def _classify_voice_type(self, features: AudioFeatures) -> str:
        """分类语音类型"""
        try:
            # 基于基频分析语音特征
            pitch_mean = np.mean(features.pitch[features.pitch > 0])
            pitch_std = np.std(features.pitch[features.pitch > 0])

            # 基于语音质量指标
            jitter = features.voice_quality_metrics.get('jitter', 0)
            shimmer = features.voice_quality_metrics.get('shimmer', 0)
            hnr = features.voice_quality_metrics.get('hnr', 0)

            # 分类逻辑
            if pitch_mean > 200:
                return "high_pitch"
            elif pitch_mean < 100:
                return "low_pitch"
            elif jitter > 0.05 or shimmer > 0.1:
                return "hoarse"
            elif hnr < 10:
                return "weak"
            elif pitch_std > 20:
                return "trembling"
            else:
                return "normal"

        except Exception as e:
            logger.error(f"语音类型分类失败: {e}")
            return "unknown"

    def _analyze_breath_pattern(self, features: AudioFeatures, audio_type: str) -> str:
        """分析呼吸模式"""
        try:
            if audio_type !="breath":
                return "not_applicable"

            # 基于能量和频率特征分析呼吸
            energy_mean = np.mean(features.energy)
            energy_std = np.std(features.energy)

            # 呼吸频率分析
            breath_rate = self._estimate_breath_rate(features.energy)

            # 分类呼吸模式
            if breath_rate > 20:
                return "rapid"
            elif breath_rate < 12:
                return "slow"
            elif energy_std > energy_mean * 0.5:
                return "irregular"
            elif energy_mean < 0.1:
                return "shallow"
            else:
                return "normal"

        except Exception as e:
            logger.error(f"呼吸模式分析失败: {e}")
            return "unknown"

    def _estimate_breath_rate(self, energy: np.ndarray) -> float:
        """估算呼吸频率"""
        try:
            # 简化的呼吸频率估算
            # 寻找能量的周期性变化

            # 平滑能量信号
            smoothed_energy = signal.savgol_filter(energy, 11, 3)

            # 寻找峰值
            peaks, _ = signal.find_peaks(smoothed_energy, distance = 10)

            if len(peaks) > 1:
                # 计算平均间隔
                intervals = np.diff(peaks)
                avg_interval = np.mean(intervals)

                # 转换为每分钟呼吸次数
                # 假设hop_length = 512, sr = 22050
                time_per_frame = 512 / 22050
                breath_rate = 60 / (avg_interval * time_per_frame)

                return float(np.clip(breath_rate, 5, 40))

            return 15.0  # 默认正常呼吸频率

        except Exception as e:
            logger.error(f"呼吸频率估算失败: {e}")
            return 15.0

    def _analyze_cough(self, features: AudioFeatures, audio_type: str) -> Dict[str, Any]:
        """分析咳嗽"""
        try:
            if audio_type !="cough":
                return {"type": "not_applicable", "severity": "none"}

            # 基于频谱特征分析咳嗽类型
            spectral_centroid_mean = np.mean(features.spectral_centroid)
            energy_max = np.max(features.energy)

            # 咳嗽类型分类
            if spectral_centroid_mean > 3000:
                cough_type = "dry"  # 干咳
            elif spectral_centroid_mean < 1500:
                cough_type = "wet"  # 湿咳
            else:
                cough_type = "normal"

            # 严重程度评估
            if energy_max > 1.0:
                severity = "severe"
            elif energy_max > 0.5:
                severity = "moderate"
            else:
                severity = "mild"

            # 中医解释
            tcm_interpretation = {
                "dry": "燥热伤肺，肺阴不足",
                "wet": "痰湿内蕴，肺失宣降",
                "normal": "肺气正常"
            }.get(cough_type, "未知")

            return {
                "type": cough_type,
                "severity": severity,
                "tcm_interpretation": tcm_interpretation,
                "spectral_features": {
                    "centroid": float(spectral_centroid_mean),
                    "energy": float(energy_max)
                }
            }

        except Exception as e:
            logger.error(f"咳嗽分析失败: {e}")
            return {"type": "unknown", "severity": "unknown"}

    def _analyze_heart_sounds(self, features: AudioFeatures, audio_type: str) -> Dict[str, Any]:
        """分析心音"""
        try:
            if audio_type !="heart":
                return {"rhythm": "not_applicable", "murmur": "none"}

            # 简化的心音分析
            # 实际应用中需要更专业的心音分析算法

            energy_peaks = self._find_energy_peaks(features.energy)
            heart_rate = self._estimate_heart_rate(energy_peaks)

            # 心律分析
            if 60<=heart_rate<=100:
                rhythm = "normal"
            elif heart_rate < 60:
                rhythm = "bradycardia"  # 心动过缓
            elif heart_rate > 100:
                rhythm = "tachycardia"  # 心动过速
            else:
                rhythm = "irregular"

            # 杂音检测（简化）
            spectral_irregularity = np.std(features.spectral_centroid)
            murmur = "present" if spectral_irregularity > 500 else "absent"

            return {
                "rhythm": rhythm,
                "heart_rate": heart_rate,
                "murmur": murmur,
                "tcm_interpretation": self._interpret_heart_sounds(rhythm, heart_rate)
            }

        except Exception as e:
            logger.error(f"心音分析失败: {e}")
            return {"rhythm": "unknown", "murmur": "unknown"}

    def _analyze_lung_sounds(self, features: AudioFeatures, audio_type: str) -> Dict[str, Any]:
        """分析肺音"""
        try:
            if audio_type !="lung":
                return {"breath_sounds": "not_applicable", "adventitious": "none"}

            # 基础呼吸音分析
            energy_mean = np.mean(features.energy)
            spectral_features = np.mean(features.spectral_centroid)

            # 呼吸音强度
            if energy_mean > 0.5:
                breath_sounds = "loud"
            elif energy_mean < 0.1:
                breath_sounds = "diminished"
            else:
                breath_sounds = "normal"

            # 附加音检测（简化）
            high_freq_energy = np.mean(features.mel_spectrogram[64:, :])
            if high_freq_energy > 0.3:
                adventitious = "crackles"  # 湿啰音
            elif np.std(features.spectral_centroid) > 300:
                adventitious = "wheeze"    # 哮鸣音
            else:
                adventitious = "none"

            return {
                "breath_sounds": breath_sounds,
                "adventitious": adventitious,
                "tcm_interpretation": self._interpret_lung_sounds(breath_sounds, adventitious)
            }

        except Exception as e:
            logger.error(f"肺音分析失败: {e}")
            return {"breath_sounds": "unknown", "adventitious": "unknown"}

    def _find_energy_peaks(self, energy: np.ndarray) -> np.ndarray:
        """寻找能量峰值"""
        try:
            peaks, _ = signal.find_peaks(energy, height = np.mean(energy), distance = 5)
            return peaks
        except Exception:
            return np.array([])

    def _estimate_heart_rate(self, peaks: np.ndarray) -> float:
        """估算心率"""
        try:
            if len(peaks) < 2:
                return 75.0  # 默认心率

            intervals = np.diff(peaks)
            avg_interval = np.mean(intervals)

            # 转换为每分钟心跳次数
            time_per_frame = 512 / 22050  # 假设参数
            heart_rate = 60 / (avg_interval * time_per_frame)

            return float(np.clip(heart_rate, 30, 200))

        except Exception:
            return 75.0

    def _interpret_heart_sounds(self, rhythm: str, heart_rate: float) -> str:
        """解释心音的中医意义"""
        interpretations = {
            "normal": "心气充足，心律正常",
            "bradycardia": "心阳不足，心动过缓",
            "tachycardia": "心火亢盛，心动过速",
            "irregular": "心气不稳，心律不齐"
        }
        return interpretations.get(rhythm, "心音异常")

    def _interpret_lung_sounds(self, breath_sounds: str, adventitious: str) -> str:
        """解释肺音的中医意义"""
        if adventitious=="crackles":
            return "痰湿内蕴，肺失宣降"
        elif adventitious=="wheeze":
            return "痰阻气道，肺气不利"
        elif breath_sounds=="diminished":
            return "肺气虚弱，呼吸无力"
        elif breath_sounds=="loud":
            return "肺热炽盛，呼吸粗糙"
        else:
            return "肺气正常，呼吸平和"

    def _generate_tcm_interpretation(self, voice_type: str, breath_pattern: str,
                                cough_analysis: Dict[str, Any]) -> Dict[str, str]:
        """生成中医解释"""
        interpretation = {}

        # 语音解释
        if voice_type in self.tcm_voice_mapping:
            interpretation["voice"] = self.tcm_voice_mapping[voice_type]

        # 呼吸解释
        if breath_pattern in self.tcm_breath_mapping:
            interpretation["breath"] = self.tcm_breath_mapping[breath_pattern]

        # 咳嗽解释
        if "tcm_interpretation" in cough_analysis:
            interpretation["cough"] = cough_analysis["tcm_interpretation"]

        return interpretation

    def _calculate_confidence_scores(self, features: AudioFeatures) -> Dict[str, float]:
        """计算置信度分数"""
        # 基于特征质量评估置信度
        base_confidence = 0.8

        # 基于语音质量调整
        voice_quality = features.voice_quality_metrics
        quality_score = (
            (1 - min(voice_quality.get('jitter', 0), 0.1) / 0.1) * 0.3 +
            (1 - min(voice_quality.get('shimmer', 0), 0.2) / 0.2) * 0.3 +
            min(voice_quality.get('hnr', 0), 20) / 20 * 0.4
        )

        final_confidence = base_confidence * quality_score

        return {
            "voice_analysis": round(final_confidence, 3),
            "breath_analysis": round(final_confidence * 0.9, 3),
            "overall": round(final_confidence * 0.95, 3)
        }

    def _get_default_analysis(self) -> TCMAudioAnalysis:
        """获取默认分析结果"""
        return TCMAudioAnalysis(
            voice_type = "unknown",
            breath_pattern = "unknown",
            cough_analysis = {"type": "unknown", "severity": "unknown"},
            heart_sound_analysis = {"rhythm": "unknown", "murmur": "unknown"},
            lung_sound_analysis = {"breath_sounds": "unknown", "adventitious": "unknown"},
            tcm_interpretation = {},
            confidence_scores = {"overall": 0.0}
        )

class RealTimeAudioProcessor:
    """实时音频处理器"""

    def __init__(self, sample_rate: int = 22050, chunk_size: int = 1024):
        """TODO: 添加文档字符串"""
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_thread = None
        self.analyzer = TCMAudioAnalyzer()

        # PyAudio设置
        self.audio_format = pyaudio.paFloat32
        self.channels = 1

    def start_recording(self) -> None:
        """开始录音"""
        try:
            self.is_recording = True
            self.audio_thread = threading.Thread(target = self._audio_callback)
            self.audio_thread.start()
            logger.info("开始实时音频录制")
        except Exception as e:
            logger.error(f"启动录音失败: {e}")
            self.is_recording = False

    def stop_recording(self) -> None:
        """停止录音"""
        self.is_recording = False
        if self.audio_thread:
            self.audio_thread.join()
        logger.info("停止实时音频录制")

    def _audio_callback(self) -> None:
        """音频回调函数"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format = self.audio_format,
                channels = self.channels,
                rate = self.sample_rate,
                input = True,
                frames_per_buffer = self.chunk_size
            )

            while self.is_recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow = False)
                    audio_data = np.frombuffer(data, dtype = np.float32)
                    self.audio_queue.put(audio_data)
                except Exception as e:
                    logger.error(f"音频数据读取失败: {e}")
                    break

            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as e:
            logger.error(f"音频回调失败: {e}")

    async def process_real_time_audio(self, duration: float = 5.0) -> Dict[str, Any]:
        """处理实时音频"""
        try:
            # 收集指定时长的音频数据
            audio_chunks = []
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < duration:
                try:
                    chunk = self.audio_queue.get(timeout = 0.1)
                    audio_chunks.append(chunk)
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue

            if not audio_chunks:
                return {"status": "no_audio", "message": "未检测到音频数据"}

            # 合并音频数据
            audio_data = np.concatenate(audio_chunks)

            # 分析音频
            analysis_result = self.analyzer.analyze_tcm_audio(audio_data, "voice")

            return {
                "status": "success",
                "duration": duration,
                "audio_length": len(audio_data),
                "analysis": {
                    "voice_type": analysis_result.voice_type,
                    "breath_pattern": analysis_result.breath_pattern,
                    "tcm_interpretation": analysis_result.tcm_interpretation,
                    "confidence_scores": analysis_result.confidence_scores
                },
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"实时音频处理失败: {e}")
            return {"status": "error", "error": str(e)}

class AudioAnalysisModel:
    """音频分析主模型"""

    def __init__(self) -> None:
        """TODO: 添加文档字符串"""
        self.feature_extractor = AdvancedAudioFeatureExtractor()
        self.tcm_analyzer = TCMAudioAnalyzer()
        self.real_time_processor = RealTimeAudioProcessor()

        logger.info("音频分析模型初始化完成")

    async def analyze_audio_file(self, file_path: str, audio_type: str = "voice") -> Dict[str, Any]:
        """分析音频文件"""
        try:
            # 加载音频文件
            audio, sr = librosa.load(file_path, sr = self.feature_extractor.sample_rate)

            # 进行中医音频分析
            analysis_result = self.tcm_analyzer.analyze_tcm_audio(audio, audio_type)

            return {
                "status": "success",
                "file_path": file_path,
                "audio_type": audio_type,
                "duration": len(audio) / sr,
                "sample_rate": sr,
                "analysis": {
                    "voice_type": analysis_result.voice_type,
                    "breath_pattern": analysis_result.breath_pattern,
                    "cough_analysis": analysis_result.cough_analysis,
                    "heart_sound_analysis": analysis_result.heart_sound_analysis,
                    "lung_sound_analysis": analysis_result.lung_sound_analysis,
                    "tcm_interpretation": analysis_result.tcm_interpretation,
                    "confidence_scores": analysis_result.confidence_scores
                },
                "timestamp": asyncio.get_event_loop().time()
            }

        except Exception as e:
            logger.error(f"音频文件分析失败: {e}")
            return {
                "status": "error",
                "file_path": file_path,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def start_real_time_analysis(self) -> None:
        """启动实时音频分析"""
        self.real_time_processor.start_recording()

    async def stop_real_time_analysis(self) -> None:
        """停止实时音频分析"""
        self.real_time_processor.stop_recording()

    async def get_real_time_analysis(self, duration: float = 5.0) -> Dict[str, Any]:
        """获取实时音频分析结果"""
        return await self.real_time_processor.process_real_time_audio(duration)

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": "TCM Audio Analysis Model",
            "version": "2.0.0",
            "features": [
                "语音特征提取",
                "呼吸模式分析",
                "咳嗽类型识别",
                "心音分析",
                "肺音分析",
                "中医音频诊断",
                "实时音频处理"
            ],
            "supported_formats": ["wav", "mp3", "flac", "m4a"],
            "sample_rate": self.feature_extractor.sample_rate,
            "real_time_support": True
        }