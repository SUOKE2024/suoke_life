"""
音频处理器模块

负责音频的解码、预处理、质量评估和增强等功能。
"""

import base64
from io import BytesIO

import librosa
from loguru import logger
from scipy import signal

from ..models.audio_models import AudioQuality, AudioType

class AudioProcessor:
    """音频处理器"""

    def __init__(self, config: dict | None = None):
        """
        初始化音频处理器

        Args:
            config: 配置信息
        """
        self.config = config or {}

        # 音频处理参数
        self.audio_params = {
            "sample_rate": 22050,  # 标准采样率
            "n_fft": 2048,
            "hop_length": 512,
            "n_mels": 128,
            "fmin": 0,
            "fmax": 8000,
        }

        # 质量评估阈值
        self.quality_thresholds = {
            "snr_min": 10.0,  # 最小信噪比
            "spectrum_completeness_min": 0.7,  # 最小频谱完整性
            "voice_activity_min": 0.3,  # 最小语音活动度
        }

        logger.info("音频处理器初始化完成")

    async def decode_and_preprocess_audio(
        self, audio_data: str, original_sample_rate: int
    ) -> np.ndarray:
        """
        解码和预处理音频

        Args:
            audio_data: Base64编码的音频数据
            original_sample_rate: 原始采样率

        Returns:
            预处理后的音频信号
        """
        try:
            # 解码Base64音频数据
            audio_bytes = base64.b64decode(audio_data)

            # 使用soundfile读取音频
            audio_signal, sr = sf.read(BytesIO(audio_bytes))

            # 如果是立体声，转换为单声道
            if len(audio_signal.shape) > 1:
                audio_signal = np.mean(audio_signal, axis=1)

            # 重采样到目标采样率
            if sr != self.audio_params["sample_rate"]:
                audio_signal = librosa.resample(
                    audio_signal, orig_sr=sr, target_sr=self.audio_params["sample_rate"]
                )

            # 归一化
            audio_signal = librosa.util.normalize(audio_signal)

            return audio_signal.astype(np.float32)

        except Exception as e:
            logger.error(f"音频解码和预处理失败: {e}")
            raise

    async def assess_audio_quality(
        self, audio_signal: np.ndarray, audio_type: AudioType
    ) -> float:
        """
        评估音频质量

        Args:
            audio_signal: 音频信号
            audio_type: 音频类型

        Returns:
            质量分数 (0-1)
        """
        try:
            quality_scores = []

            # 计算信噪比
            snr = await self._calculate_snr(audio_signal)
            snr_score = min(snr / 20.0, 1.0)  # 归一化到0-1
            quality_scores.append(snr_score)

            # 评估频谱完整性
            spectrum_score = await self._assess_spectrum_completeness(audio_signal)
            quality_scores.append(spectrum_score)

            # 根据音频类型进行特定评估
            if audio_type == AudioType.VOICE:
                voice_activity = await self._detect_voice_activity(audio_signal)
                quality_scores.append(voice_activity)
            elif audio_type == AudioType.BREATHING:
                breathing_pattern = await self._detect_breathing_pattern(audio_signal)
                quality_scores.append(breathing_pattern)

            # 计算综合质量分数
            overall_quality = np.mean(quality_scores)

            logger.debug(
                f"音频质量评估: SNR={snr:.2f}, 频谱完整性={spectrum_score:.2f}, 综合质量={overall_quality:.2f}"
            )

            return float(overall_quality)

        except Exception as e:
            logger.error(f"音频质量评估失败: {e}")
            return 0.0

    async def _calculate_snr(self, audio_signal: np.ndarray) -> float:
        """
        计算信噪比

        Args:
            audio_signal: 音频信号

        Returns:
            信噪比 (dB)
        """
        try:
            # 计算信号功率
            signal_power = np.mean(audio_signal**2)

            # 估算噪声功率（使用信号的低能量部分）
            energy = audio_signal**2
            noise_threshold = np.percentile(energy, 20)  # 使用20%分位数作为噪声阈值
            noise_power = np.mean(energy[energy <= noise_threshold])

            # 避免除零
            if noise_power == 0:
                return 60.0  # 返回一个高SNR值

            snr = 10 * np.log10(signal_power / noise_power)
            return max(snr, 0.0)

        except Exception as e:
            logger.error(f"SNR计算失败: {e}")
            return 0.0

    async def _assess_spectrum_completeness(self, audio_signal: np.ndarray) -> float:
        """
        评估频谱完整性

        Args:
            audio_signal: 音频信号

        Returns:
            频谱完整性分数 (0-1)
        """
        try:
            # 计算功率谱密度
            frequencies, psd = signal.welch(
                audio_signal, fs=self.audio_params["sample_rate"], nperseg=1024
            )

            # 定义重要频率范围
            important_ranges = [
                (80, 250),  # 基频范围
                (250, 2000),  # 语音清晰度范围
                (2000, 4000),  # 高频清晰度
            ]

            completeness_scores = []
            for low, high in important_ranges:
                # 找到频率范围内的索引
                freq_mask = (frequencies >= low) & (frequencies <= high)
                if np.any(freq_mask):
                    range_power = np.mean(psd[freq_mask])
                    # 归一化分数
                    score = min(range_power / np.mean(psd), 1.0)
                    completeness_scores.append(score)

            return float(np.mean(completeness_scores)) if completeness_scores else 0.0

        except Exception as e:
            logger.error(f"频谱完整性评估失败: {e}")
            return 0.0

    async def _detect_voice_activity(self, audio_signal: np.ndarray) -> float:
        """
        检测语音活动

        Args:
            audio_signal: 音频信号

        Returns:
            语音活动度分数 (0-1)
        """
        try:
            # 计算短时能量
            frame_length = 1024
            hop_length = 512

            # 分帧
            frames = librosa.util.frame(
                audio_signal, frame_length=frame_length, hop_length=hop_length
            )

            # 计算每帧的能量
            frame_energy = np.sum(frames**2, axis=0)

            # 使用阈值检测语音活动
            energy_threshold = np.percentile(frame_energy, 60)
            voice_frames = frame_energy > energy_threshold

            voice_activity_ratio = np.sum(voice_frames) / len(voice_frames)

            return float(voice_activity_ratio)

        except Exception as e:
            logger.error(f"语音活动检测失败: {e}")
            return 0.0

    async def _detect_breathing_pattern(self, audio_signal: np.ndarray) -> float:
        """
        检测呼吸模式

        Args:
            audio_signal: 音频信号

        Returns:
            呼吸模式质量分数 (0-1)
        """
        try:
            # 低通滤波，保留呼吸频率范围 (0.1-2 Hz)
            nyquist = self.audio_params["sample_rate"] / 2
            low_cutoff = 0.1 / nyquist
            high_cutoff = 2.0 / nyquist

            b, a = signal.butter(4, [low_cutoff, high_cutoff], btype="band")
            filtered_signal = signal.filtfilt(b, a, audio_signal)

            # 计算包络
            envelope = np.abs(signal.hilbert(filtered_signal))

            # 检测周期性
            autocorr = np.correlate(envelope, envelope, mode="full")
            autocorr = autocorr[autocorr.size // 2 :]

            # 寻找峰值来确定周期性
            peaks, _ = signal.find_peaks(autocorr, height=np.max(autocorr) * 0.3)

            if len(peaks) > 0:
                # 计算周期性强度
                periodicity = np.max(autocorr[peaks]) / np.max(autocorr)
                return float(min(periodicity, 1.0))
            else:
                return 0.0

        except Exception as e:
            logger.error(f"呼吸模式检测失败: {e}")
            return 0.0

    def get_quality_level(self, score: float) -> AudioQuality:
        """
        根据质量分数获取质量等级

        Args:
            score: 质量分数 (0-1)

        Returns:
            质量等级
        """
        if score >= 0.8:
            return AudioQuality.EXCELLENT
        elif score >= 0.6:
            return AudioQuality.GOOD
        elif score >= 0.4:
            return AudioQuality.FAIR
        else:
            return AudioQuality.POOR

    async def enhance_audio(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        增强音频质量

        Args:
            audio_signal: 原始音频信号

        Returns:
            增强后的音频信号
        """
        try:
            enhanced_signal = audio_signal.copy()

            # 降噪处理
            enhanced_signal = await self._reduce_noise(enhanced_signal)

            # 归一化
            enhanced_signal = librosa.util.normalize(enhanced_signal)

            # 预加重（增强高频）
            enhanced_signal = await self._apply_preemphasis(enhanced_signal)

            logger.debug("音频增强完成")
            return enhanced_signal

        except Exception as e:
            logger.error(f"音频增强失败: {e}")
            return audio_signal

    async def _reduce_noise(self, audio_signal: np.ndarray) -> np.ndarray:
        """
        降噪处理

        Args:
            audio_signal: 音频信号

        Returns:
            降噪后的音频信号
        """
        try:
            # 使用谱减法进行降噪
            # 计算短时傅里叶变换
            stft = librosa.stft(
                audio_signal,
                n_fft=self.audio_params["n_fft"],
                hop_length=self.audio_params["hop_length"],
            )

            # 计算幅度谱和相位谱
            magnitude = np.abs(stft)
            phase = np.angle(stft)

            # 估算噪声谱（使用前几帧）
            noise_frames = min(10, magnitude.shape[1] // 4)
            noise_spectrum = np.mean(magnitude[:, :noise_frames], axis=1, keepdims=True)

            # 谱减法
            alpha = 2.0  # 过减因子
            enhanced_magnitude = magnitude - alpha * noise_spectrum
            enhanced_magnitude = np.maximum(enhanced_magnitude, 0.1 * magnitude)

            # 重构信号
            enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
            enhanced_signal = librosa.istft(
                enhanced_stft, hop_length=self.audio_params["hop_length"]
            )

            return enhanced_signal

        except Exception as e:
            logger.error(f"降噪处理失败: {e}")
            return audio_signal

    async def _apply_preemphasis(
        self, audio_signal: np.ndarray, alpha: float = 0.97
    ) -> np.ndarray:
        """
        应用预加重滤波器

        Args:
            audio_signal: 音频信号
            alpha: 预加重系数

        Returns:
            预加重后的音频信号
        """
        try:
            # 预加重滤波器: y[n] = x[n] - alpha * x[n-1]
            preemphasized = np.append(
                audio_signal[0], audio_signal[1:] - alpha * audio_signal[:-1]
            )
            return preemphasized

        except Exception as e:
            logger.error(f"预加重处理失败: {e}")
            return audio_signal
