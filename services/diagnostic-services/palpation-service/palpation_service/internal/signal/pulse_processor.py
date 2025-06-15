"""
pulse_processor - 索克生活项目模块
"""

from scipy import signal
from typing import Any
import logging
import pywt

#! / usr / bin / env python

"""
脉诊信号处理模块
负责脉搏波形的处理、分析和特征提取
"""



logger = logging.getLogger(__name__)

class PulseProcessor:
    """脉诊信号处理器，负责脉搏波形的处理和分析"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化脉诊信号处理器

        Args:
            config: 包含处理参数的配置字典
        """
        self.config = config
        self.sampling_rate = config.get("sampling_rate", 1000)  # Hz
        self.window_size = config.get("window_size", 512)
        self.overlap = config.get("overlap", 128)
        self.low_pass_cutoff = config.get("low_pass_filter", 20)  # Hz
        self.high_pass_cutoff = config.get("high_pass_filter", 0.5)  # Hz

        # 小波变换配置
        self.wavelet_type = config.get("wavelet_transform", {}).get("wavelet_type", "db4")
        self.decomposition_level = config.get("wavelet_transform", {}).get("decomposition_level", 5)

        # 加载模型
        self.model_loaded = False
        self.model = self._load_model()
        self.model_loaded = True

        # 初始化信号处理参数
        self.feature_extraction_params = config.get("feature_extraction", {})
        self.wavelet_params = config.get("wavelet_transform", {})

        logger.info(
            f"初始化脉诊信号处理器，采样率: {self.sampling_rate}Hz, 窗口大小: {self.window_size}"
        )

    def preprocess(np.ndarray):
        """
        预处理原始脉搏信号数据

        Args:
            raw_data: 原始脉搏信号数据数组

        Returns:
            预处理后的信号数据
        """
        # 去除基线漂移
        detrended_data = self._remove_baseline_wander(raw_data)

        # 带通滤波
        filtered_data = self._apply_bandpass_filter(detrended_data)

        # 归一化
        normalized_data = self._normalize_signal(filtered_data)

        return normalized_data

    def _remove_baseline_wander(np.ndarray):
        """
        去除基线漂移

        Args:
            data: 原始信号数据

        Returns:
            去除基线漂移后的信号
        """
        # 使用中值滤波去除基线漂移
        window_size = int(self.sampling_rate * 0.2)  # 200ms窗口
        if window_size % 2 == 0:
            window_size + = 1  # 确保窗口大小为奇数

        baseline = signal.medfilt(data, window_size)
        return data - baseline

    def _apply_bandpass_filter(np.ndarray):
        """
        应用带通滤波器

        Args:
            data: 输入信号数据

        Returns:
            滤波后的信号
        """
        # 计算归一化截止频率
        nyquist_freq = 0.5 * self.sampling_rate
        low_cut = self.high_pass_cutoff / nyquist_freq
        high_cut = self.low_pass_cutoff / nyquist_freq

        # 设计带通滤波器
        b, a = signal.butter(4, [low_cut, high_cut], btype = "band")

        # 应用滤波器
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data

    def _normalize_signal(np.ndarray):
        """
        归一化信号到[0,1]范围

        Args:
            data: 输入信号数据

        Returns:
            归一化后的信号
        """
        min_val = np.min(data)
        max_val = np.max(data)

        if max_val == min_val:
            return np.zeros_like(data)

        return (data - min_val) / (max_val - min_val)

    def segment_pulse_waves(list[np.ndarray]):
        """
        将连续的脉搏信号分割为单个脉搏波

        Args:
            data: 预处理后的脉搏信号

        Returns:
            分割后的单个脉搏波列表
        """
        # 使用峰值检测查找脉搏波起点
        peaks, _ = signal.find_peaks(data, distance = int(0.5 * self.sampling_rate))

        # 分割单个脉搏波
        pulse_waves = []
        for i in range(len(peaks) - 1):
            if peaks[i + 1] - peaks[i] > 0.3 * self.sampling_rate:  # 至少300ms
                wave = data[peaks[i] : peaks[i + 1]]
                # 重采样到标准长度
                standard_length = int(0.8 * self.sampling_rate)  # 标准化为800ms
                wave_resampled = signal.resample(wave, standard_length)
                pulse_waves.append(wave_resampled)

        return pulse_waves

    def extract_time_domain_features(dict[str, float]):
        """
        提取时域特征

        Args:
            pulse_wave: 单个脉搏波

        Returns:
            时域特征字典
        """
        features = {}

        # 峰值检测
        peaks, peak_props = signal.find_peaks(
            pulse_wave, prominence = 0.1, width = 0.05 * self.sampling_rate
        )

        if len(peaks) > = 1:
            main_peak = peaks[0]

            # 主峰高度
            features["main_peak_amplitude"] = pulse_wave[main_peak]

            # 主峰位置（相对时间）
            features["main_peak_position"] = main_peak / len(pulse_wave)

            # 上升时间
            features["rising_time"] = main_peak / self.sampling_rate

            # 上升斜率
            if main_peak > 0:
                features["rising_slope"] = pulse_wave[main_peak] / main_peak
            else:
                features["rising_slope"] = 0

            # 下降斜率
            if len(pulse_wave) - main_peak > 0:
                features["falling_slope"] = (pulse_wave[main_peak] - pulse_wave[ - 1]) / (
                    len(pulse_wave) - main_peak
                )
            else:
                features["falling_slope"] = 0

            # 如果有重博(重搏波)
            if len(peaks) > = 2:
                dicrotic_peak = peaks[1]
                features["dicrotic_peak_amplitude"] = pulse_wave[dicrotic_peak]
                features["dicrotic_peak_position"] = dicrotic_peak / len(pulse_wave)
                # 重搏波与主波振幅比
                features["dicrotic_ratio"] = pulse_wave[dicrotic_peak] / pulse_wave[main_peak]
            else:
                features["dicrotic_peak_amplitude"] = 0
                features["dicrotic_peak_position"] = 0
                features["dicrotic_ratio"] = 0

            # 波形宽度
            if "widths" in peak_props:
                features["pulse_width"] = peak_props["widths"][0] / self.sampling_rate
            else:
                features["pulse_width"] = 0
        else:
            # 如果没有检测到峰值，设置默认值
            features["main_peak_amplitude"] = 0
            features["main_peak_position"] = 0
            features["rising_time"] = 0
            features["rising_slope"] = 0
            features["falling_slope"] = 0
            features["dicrotic_peak_amplitude"] = 0
            features["dicrotic_peak_position"] = 0
            features["dicrotic_ratio"] = 0
            features["pulse_width"] = 0

        # 脉象曲线曲率
        features["area_under_curve"] = np.trapz(pulse_wave)

        # 脉象能量
        features["energy"] = np.sum(np.square(pulse_wave))

        # 统计特征
        features["mean"] = np.mean(pulse_wave)
        features["std"] = np.std(pulse_wave)
        features["skewness"] = self._calculate_skewness(pulse_wave)
        features["kurtosis"] = self._calculate_kurtosis(pulse_wave)

        return features

    def _calculate_skewness(float):
        """计算偏度"""
        if len(data) < = 1:
            return 0
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        n = len(data)
        return np.sum(((data - mean) / std) * * 3) / n

    def _calculate_kurtosis(float):
        """计算峰度"""
        if len(data) < = 1:
            return 0
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        n = len(data)
        return np.sum(((data - mean) / std) * * 4) / n - 3

    def extract_frequency_domain_features(dict[str, float]):
        """
        提取频域特征

        Args:
            pulse_wave: 单个脉搏波

        Returns:
            频域特征字典
        """
        features = {}

        # 计算FFT
        fft_result = np.abs(np.fft.rfft(pulse_wave))
        freqs = np.fft.rfftfreq(len(pulse_wave), 1 / self.sampling_rate)

        # 频域特征
        if len(fft_result) > 0:
            # 主频率
            max_freq_idx = np.argmax(fft_result)
            features["dominant_frequency"] = freqs[max_freq_idx]

            # 主频率能量
            features["dominant_frequency_power"] = fft_result[max_freq_idx]

            # 频带能量
            total_power = np.sum(fft_result * *2)
            features["total_power"] = total_power

            # 低频能量比 (0 - 2Hz)
            low_freq_mask = (freqs > = 0) & (freqs < = 2)
            low_freq_power = np.sum(fft_result[low_freq_mask] * * 2)
            features["low_frequency_ratio"] = low_freq_power / total_power if total_power > 0 else 0

            # 中频能量比 (2 - 5Hz)
            mid_freq_mask = (freqs > 2) & (freqs < = 5)
            mid_freq_power = np.sum(fft_result[mid_freq_mask] * * 2)
            features["mid_frequency_ratio"] = mid_freq_power / total_power if total_power > 0 else 0

            # 高频能量比 (>5Hz)
            high_freq_mask = freqs > 5
            high_freq_power = np.sum(fft_result[high_freq_mask] * * 2)
            features["high_frequency_ratio"] = (
                high_freq_power / total_power if total_power > 0 else 0
            )

            # 频谱熵
            fft_norm = fft_result / np.sum(fft_result) if np.sum(fft_result) > 0 else fft_result
            entropy = - np.sum(fft_norm * np.log2(fft_norm + 1e - 10))
            features["spectral_entropy"] = entropy
        else:
            features["dominant_frequency"] = 0
            features["dominant_frequency_power"] = 0
            features["total_power"] = 0
            features["low_frequency_ratio"] = 0
            features["mid_frequency_ratio"] = 0
            features["high_frequency_ratio"] = 0
            features["spectral_entropy"] = 0

        return features

    def extract_wavelet_features(dict[str, float]):
        """
        使用小波变换提取特征

        Args:
            pulse_wave: 单个脉搏波

        Returns:
            小波特征字典
        """
        features = {}

        # 小波分解
        try:
            coeffs = pywt.wavedec(pulse_wave, self.wavelet_type, level = self.decomposition_level)

            # 提取各层系数的能量
            for i, coef in enumerate(coeffs):
                if i == 0:
                    features["wavelet_approximation_energy"] = np.sum(coef * *2)
                else:
                    features[f"wavelet_detail_{i}_energy"] = np.sum(coef * *2)

            # 小波熵
            total_energy = sum(np.sum(c * *2) for c in coeffs)
            wavelet_entropy = 0
            for coef in coeffs:
                coef_energy = np.sum(coef * *2)
                if coef_energy > 0 and total_energy > 0:
                    p = coef_energy / total_energy
                    wavelet_entropy - = p * np.log2(p)
            features["wavelet_entropy"] = wavelet_entropy
        except Exception as e:
            logger.error(f"小波变换提取特征失败: {e!s}")
            features["wavelet_approximation_energy"] = 0
            for i in range(1, self.decomposition_level + 1):
                features[f"wavelet_detail_{i}_energy"] = 0
            features["wavelet_entropy"] = 0

        return features

    def extract_features(dict[str, Any]):
        """
        从脉搏数据中提取完整的特征集

        Args:
            pulse_data: 原始脉搏数据
            position: 脉诊位置 (CUN_LEFT, GUAN_LEFT 等)

        Returns:
            完整的特征集合
        """
        # 预处理信号
        processed_data = self.preprocess(pulse_data)

        # 分割为单个脉搏波
        pulse_waves = self.segment_pulse_waves(processed_data)

        if not pulse_waves:
            logger.warning(f"未能分割出有效的脉搏波，位置: {position}")
            return {
                "position": position,
                "quality": {
                    "is_valid": False,
                    "signal_quality": 0,
                    "noise_level": 1.0,
                    "quality_issues": "未能分割出有效的脉搏波",
                },
                "features": {},
            }

        # 计算各波形的特征，然后求平均
        all_features = []
        for wave in pulse_waves:
            time_features = self.extract_time_domain_features(wave)
            freq_features = self.extract_frequency_domain_features(wave)
            wavelet_features = self.extract_wavelet_features(wave)

            # 合并特征
            wave_features = { * *time_features, * *freq_features, * *wavelet_features}
            all_features.append(wave_features)

        # 计算平均特征
        avg_features = {}
        for key in all_features[0].keys():
            values = [f[key] for f in all_features]
            avg_features[key] = np.mean(values)
            avg_features[f"{key}_std"] = np.std(values)

        # 信号质量评估
        signal_quality = self._assess_signal_quality(processed_data, pulse_waves)

        return {
            "position": position,
            "quality": signal_quality,
            "features": avg_features,
            "n_pulse_waves": len(pulse_waves),
        }

    def _assess_signal_quality(
        self, full_signal: np.ndarray, pulse_waves: list[np.ndarray]
    ) - > dict[str, Any]:
        """
        评估信号质量

        Args:
            full_signal: 完整的预处理信号
            pulse_waves: 分割的脉搏波列表

        Returns:
            信号质量评估结果
        """
        issues = []

        # 检查是否有足够的脉搏波
        if len(pulse_waves) < 3:
            issues.append("脉搏波数量不足")

        # 计算信噪比
        if len(full_signal) > 0:
            signal_power = np.var(full_signal)
            # 估计噪声功率（使用高频分量）
            noise = self._estimate_noise(full_signal)
            noise_power = np.var(noise)
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0
        else:
            snr = 0

        # 检查脉搏波一致性
        if len(pulse_waves) > = 2:
            # 计算相邻脉搏波的相关性
            correlations = []
            for i in range(len(pulse_waves) - 1):
                # 重采样到相同长度
                min_len = min(len(pulse_waves[i]), len(pulse_waves[i + 1]))
                wave1 = signal.resample(pulse_waves[i], min_len)
                wave2 = signal.resample(pulse_waves[i + 1], min_len)

                corr = np.corrcoef(wave1, wave2)[0, 1]
                correlations.append(corr)

            avg_correlation = np.mean(correlations)
            if avg_correlation < 0.7:
                issues.append("脉搏波一致性差")

        # 根据SNR和其他因素评估信号质量
        is_valid = len(issues) == 0 and snr > 10

        # 归一化质量分数到0 - 1
        quality_score = 0.0
        if snr > 0:
            # 转换SNR到0 - 1分数，假设20dB为最佳
            quality_score = min(1.0, snr / 20.0)

        # 如果有问题，降低质量分数
        quality_score = quality_score * (1.0 - 0.2 * len(issues))

        return {
            "is_valid": is_valid,
            "signal_quality": max(0.0, quality_score),
            "noise_level": max(0.0, min(1.0, 1.0 - quality_score)),
            "quality_issues": ", ".join(issues) if issues else "无",
        }

    def _estimate_noise(np.ndarray):
        """估计信号中的噪声分量，使用高通滤波"""
        nyquist_freq = 0.5 * self.sampling_rate
        cutoff = 10 / nyquist_freq  # 10Hz以上认为是噪声
        b, a = signal.butter(4, cutoff, btype = "high")
        return signal.filtfilt(b, a, signal_data)

    def analyze_pulse_rhythm(dict[str, Any]):
        """
        分析脉搏节律

        Args:
            pulse_data: 原始脉搏数据

        Returns:
            节律分析结果
        """
        # 预处理信号
        processed_data = self.preprocess(pulse_data)

        # 检测峰值
        peaks, _ = signal.find_peaks(processed_data, distance = int(0.5 * self.sampling_rate))

        if len(peaks) < 2:
            return {
                "rhythm_type": "unknown",
                "is_regular": False,
                "heart_rate": 0,
                "rhythm_description": "未检测到足够的脉搏",
                "confidence": 0,
            }

        # 计算峰值间隔
        intervals = np.diff(peaks) / self.sampling_rate  # 转换为秒

        # 计算心率
        heart_rate = 60 / np.mean(intervals)

        # 计算不规则性
        irregularity = np.std(intervals) / np.mean(intervals)
        is_regular = irregularity < 0.1

        # 判断节律类型
        rhythm_type = "regular"
        rhythm_description = "脉律均匀"
        confidence = 0.9

        if not is_regular:
            if irregularity > 0.2:
                rhythm_type = "very_irregular"
                rhythm_description = "脉律极不规则"
                confidence = 0.8
            else:
                rhythm_type = "slightly_irregular"
                rhythm_description = "脉律稍不规则"
                confidence = 0.7

        # 检查是否有漏跳
        missing_beats = False
        for i in range(len(intervals)):
            if intervals[i] > 1.7 * np.median(intervals):  # 间隔过长表示可能漏跳
                missing_beats = True
                rhythm_type = "intermittent"
                rhythm_description = "脉律间代"
                confidence = 0.75
                break

        # 检查是否有早搏
        premature_beats = False
        for i in range(len(intervals) - 1):
            if intervals[i] < 0.7 * np.median(intervals) and intervals[i + 1] > 1.3 * np.median(
                intervals
            ):
                # 短间隔后跟长间隔，可能是早搏
                premature_beats = True
                rhythm_type = "premature"
                rhythm_description = "脉律早搏"
                confidence = 0.75
                break

        return {
            "rhythm_type": rhythm_type,
            "is_regular": is_regular,
            "heart_rate": heart_rate,
            "irregularity": irregularity,
            "missing_beats": missing_beats,
            "premature_beats": premature_beats,
            "rhythm_description": rhythm_description,
            "confidence": confidence,
        }

    def classify_pulse_type(list[dict[str, Any]]):
        """
        基于提取的特征，对脉象类型进行分类
        使用简化的规则引擎进行初步分类

        Args:
            features: 提取的脉象特征

        Returns:
            脉象类型列表，按照匹配置信度排序
        """
        # 提取关键特征
        feature_dict = features.get("features", {})
        if not feature_dict:
            return []

        # 获取关键脉象特征
        amplitude = feature_dict.get("main_peak_amplitude", 0)
        width = feature_dict.get("pulse_width", 0)
        rising_slope = feature_dict.get("rising_slope", 0)
        falling_slope = feature_dict.get("falling_slope", 0)
        dicrotic_ratio = feature_dict.get("dicrotic_ratio", 0)
        energy = feature_dict.get("energy", 0)
        dominant_freq = feature_dict.get("dominant_frequency", 0)

        # 脉象类型匹配规则
        pulse_types = []

        # 浮脉 (Floating)
        if amplitude > 0.7 and width < 0.2:
            pulse_types.append(
                {
                    "type": "FLOATING",
                    "name": "浮脉",
                    "confidence": min(1.0, 0.5 + amplitude - width),
                    "description": "脉搏轻取即得,按之无力",
                }
            )

        # 沉脉 (Sunken)
        if amplitude < 0.4 and energy < 0.3:
            pulse_types.append(
                {
                    "type": "SUNKEN",
                    "name": "沉脉",
                    "confidence": min(1.0, 0.8 - amplitude),
                    "description": "脉搏重按始得,举指则无",
                }
            )

        # 迟脉 (Slow)
        if dominant_freq < 1.2:
            pulse_types.append(
                {
                    "type": "SLOW",
                    "name": "迟脉",
                    "confidence": min(1.0, 0.9 - dominant_freq / 2),
                    "description": "脉搏一息四至以下,脉来缓慢",
                }
            )

        # 数脉 (Rapid)
        if dominant_freq > 1.8:
            pulse_types.append(
                {
                    "type": "RAPID",
                    "name": "数脉",
                    "confidence": min(1.0, 0.5 + dominant_freq / 4),
                    "description": "脉搏一息六至以上,脉来快速",
                }
            )

        # 滑脉 (Slippery)
        if dicrotic_ratio > 0.4 and amplitude > 0.5:
            pulse_types.append(
                {
                    "type": "SLIPPERY",
                    "name": "滑脉",
                    "confidence": min(1.0, 0.6 + dicrotic_ratio / 2),
                    "description": "脉来流利,往来圆滑如珠走盘",
                }
            )

        # 涩脉 (Rough)
        if dicrotic_ratio < 0.2 and rising_slope < 0.4:
            pulse_types.append(
                {
                    "type": "ROUGH",
                    "name": "涩脉",
                    "confidence": min(1.0, 0.7 - dicrotic_ratio),
                    "description": "脉来迟缓艰涩,指下涩滞不畅",
                }
            )

        # 弦脉 (Wiry)
        if rising_slope > 0.8 and falling_slope > 0.8:
            pulse_types.append(
                {
                    "type": "WIRY",
                    "name": "弦脉",
                    "confidence": min(1.0, 0.5 + (rising_slope + falling_slope) / 4),
                    "description": "脉来挺直强硬如弓弦",
                }
            )

        # 洪脉 (Surging)
        if amplitude > 0.8 and width > 0.3:
            pulse_types.append(
                {
                    "type": "SURGING",
                    "name": "洪脉",
                    "confidence": min(1.0, amplitude * 0.8),
                    "description": "脉来洪大而盛,来势浩大",
                }
            )

        # 细脉 (Thready)
        if amplitude < 0.3 and width < 0.15:
            pulse_types.append(
                {
                    "type": "THREADY",
                    "name": "细脉",
                    "confidence": min(1.0, 0.9 - amplitude),
                    "description": "脉来细而软弱,如线状",
                }
            )

        # 微脉 (Faint)
        if amplitude < 0.2 and energy < 0.15:
            pulse_types.append(
                {
                    "type": "FAINT",
                    "name": "微脉",
                    "confidence": min(1.0, 0.9 - amplitude),
                    "description": "脉细而欲绝,若有若无",
                }
            )

        # 如果没有匹配的脉象类型，添加默认的"和脉"
        if not pulse_types:
            pulse_types.append(
                {
                    "type": "MODERATE",
                    "name": "和脉",
                    "confidence": 0.5,
                    "description": "脉象平和,不浮不沉,不迟不数",
                }
            )

        # 按置信度排序
        pulse_types.sort(key = lambda x: x["confidence"], reverse = True)

        return pulse_types

    def check_model_loaded(None):
        """
        检查模型是否正确加载

        Returns:
            bool: 如果模型正确加载则返回True

        Raises:
            Exception: 如果模型未正确加载则抛出异常
        """
        if not self.model_loaded or self.model is None:
            logger.error("脉搏分析模型未正确加载")
            raise Exception("脉搏分析模型未正确加载")

        # 执行简单推理验证模型可用性
        try:
            # 创建一个简单的假样本数据用于测试
            test_data = np.random.rand(self.feature_extraction_params.get("window_size", 512))
            _ = self._extract_basic_features(test_data)
            return True
        except Exception as e:
            logger.error(f"模型可用性检查失败: {e}")
            raise Exception(f"脉搏分析模型不可用: {e!s}")

    def _load_model(None):
        """加载脉搏分析模型"""
        model_path = self.config.get("model_path")
        model_version = self.config.get("model_version")

        logger.info(f"加载脉搏分析模型: {model_path}, 版本: {model_version}")

        try:
            # TODO: 实际模型加载代码
            # 这里是占位代码，实际应当根据具体ML框架加载模型
            model = {}  # 假模型
            logger.info("脉搏分析模型加载成功")
            return model
        except Exception as e:
            logger.error(f"加载脉搏分析模型失败: {e}")
            raise
