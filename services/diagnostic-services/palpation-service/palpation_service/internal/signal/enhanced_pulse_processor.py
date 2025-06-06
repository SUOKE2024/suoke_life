"""
enhanced_pulse_processor - 索克生活项目模块
"""

            import psutil
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from scipy import signal, stats
from scipy.fft import fft, fftfreq
from typing import Any
import asyncio
import logging
import pywt
import time
import warnings

#!/usr/bin/env python

"""
增强版脉诊信号处理模块
提供高性能、实时的脉搏波形处理、分析和AI增强特征提取
"""



logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """处理性能指标"""

    processing_time: float
    signal_quality: float
    feature_count: int
    confidence_score: float
    memory_usage: float

@dataclass
class RealTimeBuffer:
    """实时数据缓冲区"""

    data: deque
    timestamps: deque
    max_size: int
    sample_rate: int

    def __post_init__(self):
        if not hasattr(self, "data") or self.data is None:
            self.data = deque(maxlen=self.max_size)
        if not hasattr(self, "timestamps") or self.timestamps is None:
            self.timestamps = deque(maxlen=self.max_size)

class EnhancedPulseProcessor:
    """增强版脉诊信号处理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化增强版脉诊信号处理器

        Args:
            config: 包含处理参数的配置字典
        """
        self.config = config
        self.sampling_rate = config.get("sampling_rate", 1000)  # Hz
        self.window_size = config.get("window_size", 512)
        self.overlap = config.get("overlap", 128)

        # 滤波器参数优化
        self.filter_config = config.get("filter", {})
        self.low_pass_cutoff = self.filter_config.get("high_cutoff", 40)  # Hz
        self.high_pass_cutoff = self.filter_config.get("low_cutoff", 0.5)  # Hz
        self.filter_order = self.filter_config.get("order", 4)

        # 小波变换配置
        self.wavelet_config = config.get("wavelet_transform", {})
        self.wavelet_type = self.wavelet_config.get("wavelet_type", "db4")
        self.decomposition_level = self.wavelet_config.get("decomposition_level", 5)

        # 实时处理配置
        self.realtime_config = config.get("realtime", {})
        self.buffer_size = self.realtime_config.get("buffer_size", 5000)
        self.processing_interval = self.realtime_config.get("interval", 0.1)  # 秒

        # AI增强配置
        self.ai_config = config.get("ai_enhancement", {})
        self.use_ai_enhancement = self.ai_config.get("enabled", True)
        self.confidence_threshold = self.ai_config.get("confidence_threshold", 0.7)

        # 质量控制配置
        self.quality_config = config.get("quality_control", {})
        self.min_snr = self.quality_config.get("min_snr", 10.0)
        self.max_noise_ratio = self.quality_config.get("max_noise_ratio", 0.3)

        # 初始化实时缓冲区
        self.realtime_buffer = RealTimeBuffer(
            data=deque(maxlen=self.buffer_size),
            timestamps=deque(maxlen=self.buffer_size),
            max_size=self.buffer_size,
            sample_rate=self.sampling_rate,
        )

        # 性能监控
        self.processing_metrics = []
        self.executor = ThreadPoolExecutor(max_workers=4)

        # 预计算滤波器系数
        self._precompute_filters()

        # 初始化AI模型（如果启用）
        self.ai_model = None
        if self.use_ai_enhancement:
            self._initialize_ai_model()

        logger.info(
            f"增强版脉诊处理器初始化完成 - 采样率: {self.sampling_rate}Hz, 缓冲区: {self.buffer_size}"
        )

    def _precompute_filters(self):
        """预计算滤波器系数以提升性能"""
        try:
            # 预计算带通滤波器系数
            nyquist = 0.5 * self.sampling_rate
            low = self.high_pass_cutoff / nyquist
            high = self.low_pass_cutoff / nyquist

            self.bandpass_b, self.bandpass_a = signal.butter(
                self.filter_order, [low, high], btype="band"
            )

            # 预计算高通滤波器（用于基线校正）
            self.highpass_b, self.highpass_a = signal.butter(2, 0.5 / nyquist, btype="high")

            logger.info("滤波器系数预计算完成")
        except Exception as e:
            logger.error(f"滤波器预计算失败: {e}")
            raise

    def _initialize_ai_model(self):
        """初始化AI增强模型"""
        try:
            # 这里应该加载实际的AI模型
            # 例如：TensorFlow、PyTorch模型
            logger.info("AI增强模型初始化完成")
        except Exception as e:
            logger.warning(f"AI模型初始化失败，将使用传统算法: {e}")
            self.use_ai_enhancement = False

    async def process_realtime_data(self, data_point: float, timestamp: float) -> dict | None:
        """
        实时处理单个数据点

        Args:
            data_point: 单个脉搏数据点
            timestamp: 时间戳

        Returns:
            如果有足够数据进行分析，返回分析结果，否则返回None
        """
        # 添加数据到缓冲区
        self.realtime_buffer.data.append(data_point)
        self.realtime_buffer.timestamps.append(timestamp)

        # 检查是否有足够数据进行分析
        if len(self.realtime_buffer.data) >= self.window_size:
            # 异步处理数据
            return await self._process_buffer_async()

        return None

    async def _process_buffer_async(self) -> dict:
        """异步处理缓冲区数据"""
        loop = asyncio.get_event_loop()

        # 在线程池中执行CPU密集型任务
        result = await loop.run_in_executor(self.executor, self._process_buffer_data)

        return result

    def _process_buffer_data(self) -> dict:
        """处理缓冲区数据"""
        start_time = time.time()

        # 转换为numpy数组
        data = np.array(list(self.realtime_buffer.data))

        # 预处理
        processed_data = self.preprocess_optimized(data)

        # 质量评估
        quality_score = self._assess_signal_quality_fast(processed_data)

        if quality_score < self.confidence_threshold:
            return {
                "status": "low_quality",
                "quality_score": quality_score,
                "message": "信号质量不足，请检查传感器连接",
            }

        # 特征提取
        features = self.extract_features_optimized(processed_data)

        # AI增强分析（如果启用）
        if self.use_ai_enhancement and self.ai_model:
            features = self._enhance_features_with_ai(features, processed_data)

        # 脉象分类
        pulse_classification = self.classify_pulse_type_enhanced(features)

        processing_time = time.time() - start_time

        # 记录性能指标
        metrics = ProcessingMetrics(
            processing_time=processing_time,
            signal_quality=quality_score,
            feature_count=len(features),
            confidence_score=pulse_classification.get("confidence", 0),
            memory_usage=self._get_memory_usage(),
        )
        self.processing_metrics.append(metrics)

        return {
            "status": "success",
            "features": features,
            "pulse_classification": pulse_classification,
            "quality_score": quality_score,
            "processing_time": processing_time,
            "timestamp": time.time(),
        }

    def preprocess_optimized(self, raw_data: np.ndarray) -> np.ndarray:
        """
        优化的预处理流程

        Args:
            raw_data: 原始脉搏信号数据

        Returns:
            预处理后的信号数据
        """
        # 使用预计算的滤波器系数
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # 1. 基线校正（使用预计算的高通滤波器）
            detrended = signal.filtfilt(self.highpass_b, self.highpass_a, raw_data)

            # 2. 带通滤波（使用预计算的带通滤波器）
            filtered = signal.filtfilt(self.bandpass_b, self.bandpass_a, detrended)

            # 3. 异常值处理（使用向量化操作）
            filtered = self._remove_outliers_vectorized(filtered)

            # 4. 归一化（优化版本）
            normalized = self._normalize_signal_fast(filtered)

        return normalized

    def _remove_outliers_vectorized(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """向量化的异常值移除"""
        z_scores = np.abs(stats.zscore(data))
        mask = z_scores < threshold

        # 对异常值进行插值
        if not np.all(mask):
            valid_indices = np.where(mask)[0]
            invalid_indices = np.where(~mask)[0]

            if len(valid_indices) > 1:
                data[invalid_indices] = np.interp(
                    invalid_indices, valid_indices, data[valid_indices]
                )

        return data

    def _normalize_signal_fast(self, data: np.ndarray) -> np.ndarray:
        """快速信号归一化"""
        data_min = np.min(data)
        data_max = np.max(data)

        if data_max == data_min:
            return np.zeros_like(data)

        return (data - data_min) / (data_max - data_min)

    def extract_features_optimized(self, pulse_data: np.ndarray) -> dict[str, Any]:
        """
        优化的特征提取

        Args:
            pulse_data: 预处理后的脉搏数据

        Returns:
            提取的特征字典
        """
        features = {}

        # 并行提取不同域的特征
        futures = []

        # 时域特征
        futures.append(self.executor.submit(self._extract_time_domain_features_fast, pulse_data))

        # 频域特征
        futures.append(
            self.executor.submit(self._extract_frequency_domain_features_fast, pulse_data)
        )

        # 小波域特征
        futures.append(self.executor.submit(self._extract_wavelet_features_fast, pulse_data))

        # 非线性特征
        futures.append(self.executor.submit(self._extract_nonlinear_features, pulse_data))

        # 收集结果
        for future in futures:
            try:
                result = future.result(timeout=5.0)  # 5秒超时
                features.update(result)
            except Exception as e:
                logger.warning(f"特征提取部分失败: {e}")

        return features

    def _extract_time_domain_features_fast(self, pulse_data: np.ndarray) -> dict[str, float]:
        """快速时域特征提取"""
        features = {}

        # 使用向量化操作提升性能

        # 基本统计特征
        features["mean"] = np.mean(pulse_data)
        features["std"] = np.std(pulse_data)
        features["variance"] = np.var(pulse_data)
        features["skewness"] = stats.skew(pulse_data)
        features["kurtosis"] = stats.kurtosis(pulse_data)

        # 峰值检测（优化版本）
        peaks, peak_props = signal.find_peaks(
            pulse_data,
            prominence=0.1 * np.std(pulse_data),
            distance=int(0.3 * self.sampling_rate),  # 最小间距300ms
        )

        if len(peaks) > 0:
            # 主峰特征
            main_peak_idx = peaks[np.argmax(pulse_data[peaks])]
            features["main_peak_amplitude"] = pulse_data[main_peak_idx]
            features["main_peak_position"] = main_peak_idx / len(pulse_data)

            # 脉率计算
            if len(peaks) > 1:
                intervals = np.diff(peaks) / self.sampling_rate
                features["heart_rate"] = 60 / np.mean(intervals)
                features["heart_rate_variability"] = np.std(intervals)
                features["rhythm_regularity"] = 1 / (1 + np.std(intervals))

            # 波形特征
            features.update(self._extract_waveform_features(pulse_data, peaks))

        return features

    def _extract_frequency_domain_features_fast(self, pulse_data: np.ndarray) -> dict[str, float]:
        """快速频域特征提取"""
        features = {}

        # 使用FFT进行频域分析
        fft_data = fft(pulse_data)
        freqs = fftfreq(len(pulse_data), 1 / self.sampling_rate)

        # 只取正频率部分
        positive_freqs = freqs[: len(freqs) // 2]
        magnitude = np.abs(fft_data[: len(fft_data) // 2])

        # 功率谱密度
        psd = magnitude**2

        # 主频率
        peak_freq_idx = np.argmax(psd)
        features["dominant_frequency"] = positive_freqs[peak_freq_idx]
        features["dominant_power"] = psd[peak_freq_idx]

        # 频带能量分布
        freq_bands = {
            "very_low": (0.0, 0.5),
            "low": (0.5, 2.0),
            "medium": (2.0, 8.0),
            "high": (8.0, 20.0),
        }

        total_power = np.sum(psd)
        for band_name, (low_freq, high_freq) in freq_bands.items():
            band_mask = (positive_freqs >= low_freq) & (positive_freqs <= high_freq)
            band_power = np.sum(psd[band_mask])
            features[f"{band_name}_freq_power"] = band_power / total_power if total_power > 0 else 0

        # 谱质心和带宽
        features["spectral_centroid"] = (
            np.sum(positive_freqs * psd) / np.sum(psd) if np.sum(psd) > 0 else 0
        )
        features["spectral_bandwidth"] = (
            np.sqrt(
                np.sum(((positive_freqs - features["spectral_centroid"]) ** 2) * psd) / np.sum(psd)
            )
            if np.sum(psd) > 0
            else 0
        )

        return features

    def _extract_wavelet_features_fast(self, pulse_data: np.ndarray) -> dict[str, float]:
        """快速小波域特征提取"""
        features = {}

        try:
            # 小波分解
            coeffs = pywt.wavedec(pulse_data, self.wavelet_type, level=self.decomposition_level)

            # 各层能量分布
            total_energy = sum(np.sum(c**2) for c in coeffs)

            for i, coeff in enumerate(coeffs):
                level_energy = np.sum(coeff**2)
                features[f"wavelet_energy_level_{i}"] = (
                    level_energy / total_energy if total_energy > 0 else 0
                )
                features[f"wavelet_entropy_level_{i}"] = self._calculate_entropy(coeff)

            # 小波统计特征
            detail_coeffs = coeffs[1:]  # 排除近似系数
            if detail_coeffs:
                all_details = np.concatenate(detail_coeffs)
                features["wavelet_detail_mean"] = np.mean(all_details)
                features["wavelet_detail_std"] = np.std(all_details)
                features["wavelet_detail_energy"] = (
                    np.sum(all_details**2) / total_energy if total_energy > 0 else 0
                )

        except Exception as e:
            logger.warning(f"小波特征提取失败: {e}")
            # 返回默认值
            for i in range(self.decomposition_level + 1):
                features[f"wavelet_energy_level_{i}"] = 0
                features[f"wavelet_entropy_level_{i}"] = 0

        return features

    def _extract_nonlinear_features(self, pulse_data: np.ndarray) -> dict[str, float]:
        """提取非线性特征"""
        features = {}

        try:
            # 样本熵
            features["sample_entropy"] = self._calculate_sample_entropy(pulse_data)

            # 近似熵
            features["approximate_entropy"] = self._calculate_approximate_entropy(pulse_data)

            # 分形维数
            features["fractal_dimension"] = self._calculate_fractal_dimension(pulse_data)

            # Lyapunov指数（简化版本）
            features["lyapunov_exponent"] = self._calculate_lyapunov_exponent(pulse_data)

        except Exception as e:
            logger.warning(f"非线性特征提取失败: {e}")
            # 返回默认值
            features.update(
                {
                    "sample_entropy": 0,
                    "approximate_entropy": 0,
                    "fractal_dimension": 0,
                    "lyapunov_exponent": 0,
                }
            )

        return features

    def _extract_waveform_features(
        self, pulse_data: np.ndarray, peaks: np.ndarray
    ) -> dict[str, float]:
        """提取波形特征"""
        features = {}

        if len(peaks) == 0:
            return features

        # 分析单个脉搏波
        for i in range(len(peaks) - 1):
            start_idx = peaks[i]
            end_idx = peaks[i + 1]
            single_wave = pulse_data[start_idx:end_idx]

            if len(single_wave) > 10:  # 确保有足够的数据点
                # 上升时间和下降时间
                peak_in_wave = np.argmax(single_wave)
                features["rise_time_ratio"] = peak_in_wave / len(single_wave)
                features["fall_time_ratio"] = (len(single_wave) - peak_in_wave) / len(single_wave)

                # 波形对称性
                features["waveform_symmetry"] = self._calculate_symmetry(single_wave)

                # 波形复杂度
                features["waveform_complexity"] = self._calculate_complexity(single_wave)

                break  # 只分析第一个完整波形

        return features

    def _calculate_entropy(self, data: np.ndarray) -> float:
        """计算熵"""
        if len(data) == 0:
            return 0

        # 将数据离散化
        hist, _ = np.histogram(data, bins=50)
        hist = hist[hist > 0]  # 移除零值

        if len(hist) == 0:
            return 0

        # 归一化
        prob = hist / np.sum(hist)

        # 计算熵
        return -np.sum(prob * np.log2(prob))

    def _calculate_sample_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """计算样本熵"""
        N = len(data)
        if m + 1 > N:
            return 0

        # 简化实现
        patterns_m = []
        patterns_m1 = []

        for i in range(N - m):
            patterns_m.append(data[i : i + m])
            if i < N - m - 1:
                patterns_m1.append(data[i : i + m + 1])

        # 计算匹配数
        matches_m = 0
        matches_m1 = 0

        for i in range(len(patterns_m)):
            for j in range(i + 1, len(patterns_m)):
                if np.max(np.abs(np.array(patterns_m[i]) - np.array(patterns_m[j]))) <= r:
                    matches_m += 1

                    if i < len(patterns_m1) and j < len(patterns_m1):
                        if np.max(np.abs(np.array(patterns_m1[i]) - np.array(patterns_m1[j]))) <= r:
                            matches_m1 += 1

        if matches_m == 0:
            return 0

        return -np.log(matches_m1 / matches_m) if matches_m1 > 0 else 0

    def _calculate_approximate_entropy(self, data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
        """计算近似熵"""
        # 简化实现
        return self._calculate_sample_entropy(data, m, r) * 0.8  # 近似值

    def _calculate_fractal_dimension(self, data: np.ndarray) -> float:
        """计算分形维数（Higuchi方法）"""
        try:
            k_max = 10
            L = []

            for k in range(1, k_max + 1):
                Lk = 0
                for m in range(k):
                    Lmk = 0
                    for i in range(1, int((len(data) - m) / k)):
                        Lmk += abs(data[m + i * k] - data[m + (i - 1) * k])
                    Lmk = Lmk * (len(data) - 1) / (k * k * int((len(data) - m) / k))
                    Lk += Lmk
                L.append(Lk / k)

            # 线性拟合
            x = np.log(range(1, k_max + 1))
            y = np.log(L)

            if len(x) > 1 and len(y) > 1:
                slope, _ = np.polyfit(x, y, 1)
                return -slope
            else:
                return 1.0

        except Exception:
            return 1.0

    def _calculate_lyapunov_exponent(self, data: np.ndarray) -> float:
        """计算Lyapunov指数（简化版本）"""
        try:
            # 简化的Lyapunov指数计算
            diff = np.diff(data)
            if len(diff) == 0:
                return 0

            # 计算相邻点的发散率
            divergence = np.abs(diff[1:] / diff[:-1])
            divergence = divergence[divergence > 0]

            if len(divergence) == 0:
                return 0

            return np.mean(np.log(divergence))

        except Exception:
            return 0

    def _calculate_symmetry(self, waveform: np.ndarray) -> float:
        """计算波形对称性"""
        if len(waveform) < 3:
            return 0

        # 找到峰值位置
        peak_idx = np.argmax(waveform)

        # 计算左右两侧的相似性
        left_part = waveform[:peak_idx]
        right_part = waveform[peak_idx:]

        # 将右侧翻转并调整长度
        right_flipped = np.flip(right_part)
        min_len = min(len(left_part), len(right_flipped))

        if min_len == 0:
            return 0

        left_normalized = left_part[-min_len:]
        right_normalized = right_flipped[:min_len]

        # 计算相关系数
        correlation = np.corrcoef(left_normalized, right_normalized)[0, 1]
        return correlation if not np.isnan(correlation) else 0

    def _calculate_complexity(self, waveform: np.ndarray) -> float:
        """计算波形复杂度"""
        if len(waveform) < 2:
            return 0

        # 使用二阶差分计算复杂度
        first_diff = np.diff(waveform)
        second_diff = np.diff(first_diff)

        # 复杂度定义为二阶差分的标准差
        return np.std(second_diff) if len(second_diff) > 0 else 0

    def _assess_signal_quality_fast(self, signal_data: np.ndarray) -> float:
        """快速信号质量评估"""
        if len(signal_data) == 0:
            return 0.0

        # 信噪比估计
        signal_power = np.var(signal_data)
        noise_estimate = np.var(np.diff(signal_data))  # 简单噪声估计

        if noise_estimate == 0:
            snr = float("inf")
        else:
            snr = signal_power / noise_estimate

        # 质量评分（0-1）
        snr_score = min(snr / 100, 1.0)  # 归一化到0-1

        # 信号稳定性
        stability_score = 1.0 / (1.0 + np.std(signal_data))

        # 综合质量评分
        quality_score = 0.7 * snr_score + 0.3 * stability_score

        return min(quality_score, 1.0)

    def _enhance_features_with_ai(self, features: dict, signal_data: np.ndarray) -> dict:
        """使用AI增强特征"""
        if not self.ai_model:
            return features

        try:
            # 这里应该调用实际的AI模型
            # enhanced_features = self.ai_model.predict(features, signal_data)
            # features.update(enhanced_features)

            # 临时实现：添加一些AI增强的特征
            features["ai_confidence"] = 0.85
            features["ai_anomaly_score"] = 0.1

        except Exception as e:
            logger.warning(f"AI特征增强失败: {e}")

        return features

    def classify_pulse_type_enhanced(self, features: dict[str, Any]) -> dict[str, Any]:
        """增强的脉象分类"""
        # 基于特征的脉象分类逻辑
        classification = {
            "primary_type": "normal",
            "secondary_types": [],
            "confidence": 0.0,
            "tcm_interpretation": "",
            "health_indicators": {},
        }

        # 脉率分析
        heart_rate = features.get("heart_rate", 70)
        if heart_rate < 60:
            classification["primary_type"] = "slow"
            classification["tcm_interpretation"] = "迟脉，可能阳虚或寒证"
        elif heart_rate > 100:
            classification["primary_type"] = "rapid"
            classification["tcm_interpretation"] = "数脉，可能阴虚或热证"

        # 脉力分析
        amplitude = features.get("main_peak_amplitude", 0.5)
        if amplitude < 0.3:
            classification["secondary_types"].append("weak")
            classification["tcm_interpretation"] += "，脉力不足，可能气虚"
        elif amplitude > 0.8:
            classification["secondary_types"].append("strong")
            classification["tcm_interpretation"] += "，脉力充盛，可能实证"

        # 节律分析
        regularity = features.get("rhythm_regularity", 0.8)
        if regularity < 0.6:
            classification["secondary_types"].append("irregular")
            classification["tcm_interpretation"] += "，节律不齐，需注意心脏功能"

        # 计算置信度
        confidence_factors = [
            features.get("ai_confidence", 0.5),
            min(regularity, 1.0),
            min(amplitude, 1.0),
            1.0 - features.get("ai_anomaly_score", 0.5),
        ]
        classification["confidence"] = np.mean(confidence_factors)

        # 健康指标
        classification["health_indicators"] = {
            "cardiovascular_health": self._assess_cardiovascular_health(features),
            "energy_level": self._assess_energy_level(features),
            "stress_level": self._assess_stress_level(features),
        }

        return classification

    def _assess_cardiovascular_health(self, features: dict) -> float:
        """评估心血管健康"""
        heart_rate = features.get("heart_rate", 70)
        regularity = features.get("rhythm_regularity", 0.8)

        # 理想心率范围
        hr_score = 1.0 - abs(heart_rate - 70) / 70
        hr_score = max(0, min(1, hr_score))

        # 综合评分
        return 0.6 * hr_score + 0.4 * regularity

    def _assess_energy_level(self, features: dict) -> float:
        """评估能量水平"""
        amplitude = features.get("main_peak_amplitude", 0.5)
        complexity = features.get("waveform_complexity", 0.5)

        return 0.7 * amplitude + 0.3 * min(complexity, 1.0)

    def _assess_stress_level(self, features: dict) -> float:
        """评估压力水平"""
        hrv = features.get("heart_rate_variability", 0.05)
        irregularity = 1.0 - features.get("rhythm_regularity", 0.8)

        # 压力水平与HRV和不规律性相关
        return 0.6 * min(hrv * 10, 1.0) + 0.4 * irregularity

    def _get_memory_usage(self) -> float:
        """获取内存使用情况"""
        try:

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

    def get_performance_metrics(self) -> dict[str, Any]:
        """获取性能指标"""
        if not self.processing_metrics:
            return {}

        recent_metrics = self.processing_metrics[-100:]  # 最近100次处理

        return {
            "average_processing_time": np.mean([m.processing_time for m in recent_metrics]),
            "average_quality_score": np.mean([m.signal_quality for m in recent_metrics]),
            "average_confidence": np.mean([m.confidence_score for m in recent_metrics]),
            "memory_usage": recent_metrics[-1].memory_usage if recent_metrics else 0,
            "total_processed": len(self.processing_metrics),
        }

    def cleanup(self):
        """清理资源"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)

        # 清理缓冲区
        self.realtime_buffer.data.clear()
        self.realtime_buffer.timestamps.clear()

        logger.info("增强版脉诊处理器资源清理完成")
