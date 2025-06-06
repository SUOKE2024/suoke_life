"""
enhanced_palpation_service - 索克生活项目模块
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from scipy import signal
from services.common.governance.circuit_breaker import CircuitBreakerConfig
from services.common.governance.rate_limiter import RateLimitConfig, rate_limit
from services.common.observability.tracing import SpanKind, trace
from typing import Any
import asyncio
import hashlib
import json
import time
import uuid

#!/usr/bin/env python3

"""
增强版切诊服务

该模块是切诊服务的增强版本，集成了高性能脉象数据处理、并行分析、智能缓存和批量诊断功能，
提供专业的中医切诊数据采集和分析服务。
"""



# 导入通用组件

class PulsePosition(Enum):
    """脉位"""

    FLOATING = "floating"  # 浮脉
    DEEP = "deep"  # 沉脉
    MIDDLE = "middle"  # 中脉

class PulseRate(Enum):
    """脉率"""

    SLOW = "slow"  # 迟脉 (<60次/分)
    NORMAL = "normal"  # 正常 (60-100次/分)
    RAPID = "rapid"  # 数脉 (>100次/分)

class PulseStrength(Enum):
    """脉力"""

    WEAK = "weak"  # 虚脉
    STRONG = "strong"  # 实脉
    MODERATE = "moderate"  # 中等

class PulseRhythm(Enum):
    """脉律"""

    REGULAR = "regular"  # 齐脉
    IRREGULAR = "irregular"  # 不齐脉
    INTERMITTENT = "intermittent"  # 结脉
    MISSED = "missed"  # 代脉

class PulseShape(Enum):
    """脉形"""

    THIN = "thin"  # 细脉
    THICK = "thick"  # 大脉
    LONG = "long"  # 长脉
    SHORT = "short"  # 短脉
    SLIPPERY = "slippery"  # 滑脉
    ROUGH = "rough"  # 涩脉

@dataclass
class PulseDataPoint:
    """脉象数据点"""

    timestamp: float
    amplitude: float
    pressure: float
    channel: int = 0  # 传感器通道

@dataclass
class PulseAnalysisRequest:
    """脉象分析请求"""

    request_id: str
    patient_id: str
    pulse_data: list[PulseDataPoint]
    duration: float  # 采集时长（秒）
    sample_rate: int = 1000  # 采样率
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PulseFeature:
    """脉象特征"""

    feature_type: str
    value: Any
    confidence: float
    channel: int = 0
    time_range: tuple[float, float] | None = None

@dataclass
class PalpationResult:
    """切诊结果"""

    request_id: str
    patient_id: str
    pulse_characteristics: dict[str, Any]  # 脉象特征
    features: list[PulseFeature]
    syndrome_indicators: dict[str, float]  # 证候指标
    quality_score: float
    processing_time_ms: float
    recommendations: list[str]

@dataclass
class BatchPulseRequest:
    """批量脉象分析请求"""

    batch_id: str
    requests: list[PulseAnalysisRequest]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedPalpationService:
    """增强版切诊服务"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化增强版切诊服务

        Args:
            config: 配置信息
        """
        self.config = config

        # 增强配置
        self.enhanced_config = {
            "pulse_processing": {
                "min_duration": 30,  # 最小采集时长（秒）
                "max_duration": 300,  # 最大采集时长（秒）
                "quality_threshold": 0.7,
                "filtering": {
                    "lowpass_freq": 20,  # 低通滤波频率
                    "highpass_freq": 0.5,  # 高通滤波频率
                    "notch_freq": 50,  # 陷波滤波频率（工频干扰）
                },
            },
            "parallel_processing": {"enabled": True, "max_workers": 4, "batch_size": 6},
            "caching": {
                "enabled": True,
                "ttl_seconds": {
                    "pulse_features": 3600,
                    "analysis_result": 1800,
                    "pattern_recognition": 7200,
                },
                "max_cache_size": 2000,
            },
            "feature_extraction": {
                "time_domain": ["heart_rate", "hrv", "amplitude", "rhythm"],
                "frequency_domain": ["power_spectrum", "dominant_frequency"],
                "morphology": ["pulse_width", "rise_time", "fall_time", "shape_index"],
            },
            "pulse_detection": {
                "peak_detection": {
                    "height_threshold": 0.3,
                    "distance_threshold": 0.4,  # 最小间隔（秒）
                    "prominence": 0.1,
                }
            },
        }

        # 批处理队列
        self.batch_queue: asyncio.Queue = asyncio.Queue()

        # 缓存
        self.cache: dict[str, tuple[Any, datetime]] = {}

        # 性能统计
        self.stats = {
            "total_requests": 0,
            "successful_analyses": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_processing_time_ms": 0.0,
            "quality_distribution": defaultdict(int),
            "batch_processed": 0,
            "pulse_patterns_detected": defaultdict(int),
        }

        # 断路器配置
        self.circuit_breaker_configs = {
            "pulse_processing": CircuitBreakerConfig(
                failure_threshold=3, recovery_timeout=30.0, timeout=20.0
            ),
            "feature_extraction": CircuitBreakerConfig(
                failure_threshold=5, recovery_timeout=20.0, timeout=15.0
            ),
        }

        # 限流配置
        self.rate_limit_configs = {
            "analysis": RateLimitConfig(rate=15.0, burst=30),
            "batch": RateLimitConfig(rate=3.0, burst=6),
        }

        # 后台任务
        self.background_tasks: list[asyncio.Task] = []

        logger.info("增强版切诊服务初始化完成")

    async def initialize(self):
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("切诊服务初始化完成")

    def _start_background_tasks(self):
        """启动后台任务"""
        # 批处理处理器
        self.background_tasks.append(asyncio.create_task(self._batch_processor()))

        # 缓存清理器
        self.background_tasks.append(asyncio.create_task(self._cache_cleaner()))

    @trace(service_name="palpation-service", kind=SpanKind.SERVER)
    @rate_limit(name="analysis", tokens=1)
    async def analyze_pulse(
        self,
        patient_id: str,
        pulse_data: list[PulseDataPoint],
        duration: float,
        sample_rate: int = 1000,
        metadata: dict[str, Any] | None = None,
    ) -> PalpationResult:
        """
        分析脉象数据

        Args:
            patient_id: 患者ID
            pulse_data: 脉象数据点列表
            duration: 采集时长
            sample_rate: 采样率
            metadata: 元数据

        Returns:
            切诊结果
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        self.stats["total_requests"] += 1

        # 检查缓存
        data_hash = self._hash_pulse_data(pulse_data)
        cache_key = self._generate_cache_key("analysis", patient_id, data_hash, duration)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            self.stats["cache_hits"] += 1
            return cached_result

        self.stats["cache_misses"] += 1

        try:
            # 预处理脉象数据
            processed_data = await self._preprocess_pulse_data(pulse_data, sample_rate)

            # 评估数据质量
            quality_score = await self._assess_pulse_quality(processed_data, duration)

            if quality_score < self.enhanced_config["pulse_processing"]["quality_threshold"]:
                logger.warning(f"脉象数据质量不足: {quality_score}")
                # 尝试数据增强
                processed_data = await self._enhance_pulse_data(processed_data)

            # 并行提取特征
            if self.enhanced_config["parallel_processing"]["enabled"]:
                features = await self._parallel_feature_extraction(processed_data, sample_rate)
            else:
                features = await self._extract_features(processed_data, sample_rate)

            # 分析脉象特征
            pulse_characteristics = await self._analyze_pulse_characteristics(
                features, processed_data, sample_rate
            )

            # 分析证候指标
            syndrome_indicators = await self._analyze_syndrome_indicators(
                pulse_characteristics, features
            )

            # 生成建议
            recommendations = await self._generate_recommendations(
                syndrome_indicators, pulse_characteristics
            )

            processing_time_ms = (time.time() - start_time) * 1000

            result = PalpationResult(
                request_id=request_id,
                patient_id=patient_id,
                pulse_characteristics=pulse_characteristics,
                features=features,
                syndrome_indicators=syndrome_indicators,
                quality_score=quality_score,
                processing_time_ms=processing_time_ms,
                recommendations=recommendations,
            )

            # 缓存结果
            await self._set_to_cache(cache_key, result)

            # 更新统计
            self.stats["successful_analyses"] += 1
            self._update_stats(processing_time_ms)

            return result

        except Exception as e:
            logger.error(f"脉象分析失败: {e}")
            raise

    async def _preprocess_pulse_data(
        self, pulse_data: list[PulseDataPoint], sample_rate: int
    ) -> np.ndarray:
        """预处理脉象数据"""
        # 转换为numpy数组
        if not pulse_data:
            raise ValueError("脉象数据为空")

        # 提取幅值数据
        amplitudes = np.array([point.amplitude for point in pulse_data])

        # 去除异常值
        amplitudes = self._remove_outliers(amplitudes)

        # 滤波处理
        filtered_data = await self._filter_pulse_signal(amplitudes, sample_rate)

        return filtered_data

    def _remove_outliers(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """去除异常值"""
        mean = np.mean(data)
        std = np.std(data)

        # 使用3σ准则
        mask = np.abs(data - mean) < threshold * std

        # 对于被标记为异常值的点，使用邻近点的平均值替代
        cleaned_data = data.copy()
        outlier_indices = np.where(~mask)[0]

        for idx in outlier_indices:
            # 使用前后各3个点的平均值
            start = max(0, idx - 3)
            end = min(len(data), idx + 4)
            neighbors = data[start:end]
            neighbors = neighbors[neighbors != data[idx]]  # 排除当前异常值

            if len(neighbors) > 0:
                cleaned_data[idx] = np.mean(neighbors)

        return cleaned_data

    async def _filter_pulse_signal(self, signal_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """滤波处理脉象信号"""
        config = self.enhanced_config["pulse_processing"]["filtering"]

        # 高通滤波（去除基线漂移）
        nyquist = sample_rate / 2
        high_cutoff = config["highpass_freq"] / nyquist
        b_high, a_high = signal.butter(4, high_cutoff, btype="high")
        filtered_signal = signal.filtfilt(b_high, a_high, signal_data)

        # 低通滤波（去除高频噪声）
        low_cutoff = config["lowpass_freq"] / nyquist
        b_low, a_low = signal.butter(4, low_cutoff, btype="low")
        filtered_signal = signal.filtfilt(b_low, a_low, filtered_signal)

        # 陷波滤波（去除工频干扰）
        notch_freq = config["notch_freq"]
        quality_factor = 30
        b_notch, a_notch = signal.iirnotch(notch_freq, quality_factor, sample_rate)
        filtered_signal = signal.filtfilt(b_notch, a_notch, filtered_signal)

        return filtered_signal

    async def _assess_pulse_quality(self, pulse_data: np.ndarray, duration: float) -> float:
        """评估脉象数据质量"""
        quality_factors = []

        # 1. 信号稳定性
        stability = 1.0 - (np.std(pulse_data) / (np.mean(np.abs(pulse_data)) + 1e-8))
        quality_factors.append(max(stability, 0.0))

        # 2. 信噪比
        snr = await self._calculate_pulse_snr(pulse_data)
        snr_score = min(snr / 15, 1.0)  # 15dB为满分
        quality_factors.append(snr_score)

        # 3. 采集时长充足性
        min_duration = self.enhanced_config["pulse_processing"]["min_duration"]
        duration_score = min(duration / min_duration, 1.0)
        quality_factors.append(duration_score)

        # 4. 脉搏检测成功率
        detection_rate = await self._calculate_pulse_detection_rate(pulse_data)
        quality_factors.append(detection_rate)

        # 综合质量分数
        quality_score = np.mean(quality_factors)
        return quality_score

    async def _calculate_pulse_snr(self, pulse_data: np.ndarray) -> float:
        """计算脉象信号的信噪比"""
        # 检测脉搏峰值
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) < 2:
            return 0.0

        # 计算信号功率（峰值区域）
        signal_power = 0
        for peak in peaks:
            start = max(0, peak - 50)
            end = min(len(pulse_data), peak + 50)
            signal_power += np.sum(pulse_data[start:end] ** 2)

        signal_power /= len(peaks)

        # 计算噪声功率（谷值区域）
        noise_power = 0
        for i in range(len(peaks) - 1):
            valley_start = peaks[i] + 25
            valley_end = peaks[i + 1] - 25
            if valley_end > valley_start:
                noise_power += np.sum(pulse_data[valley_start:valley_end] ** 2)

        if len(peaks) > 1:
            noise_power /= len(peaks) - 1

        # 计算SNR
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = 30  # 很高的SNR

        return max(snr, 0)

    async def _calculate_pulse_detection_rate(self, pulse_data: np.ndarray) -> float:
        """计算脉搏检测成功率"""
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) < 2:
            return 0.0

        # 计算平均心率
        intervals = np.diff(peaks)
        if len(intervals) == 0:
            return 0.0

        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)

        # 检测异常间隔
        normal_intervals = intervals[np.abs(intervals - mean_interval) < 2 * std_interval]
        detection_rate = len(normal_intervals) / len(intervals)

        return detection_rate

    async def _enhance_pulse_data(self, pulse_data: np.ndarray) -> np.ndarray:
        """增强脉象数据质量"""
        enhanced = pulse_data.copy()

        # 自适应滤波
        # 使用Savitzky-Golay滤波平滑信号
        window_length = min(51, len(enhanced) // 10)
        if window_length % 2 == 0:
            window_length += 1

        if window_length >= 3:
            enhanced = signal.savgol_filter(enhanced, window_length, 3)

        # 基线校正
        # 使用多项式拟合去除基线漂移
        x = np.arange(len(enhanced))
        baseline = np.polyval(np.polyfit(x, enhanced, 3), x)
        enhanced = enhanced - baseline

        return enhanced

    async def _parallel_feature_extraction(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> list[PulseFeature]:
        """并行特征提取"""
        feature_categories = self.enhanced_config["feature_extraction"]

        # 创建特征提取任务
        tasks = []

        # 时域特征
        for feature_type in feature_categories["time_domain"]:
            task = self._extract_time_domain_feature(pulse_data, sample_rate, feature_type)
            tasks.append(task)

        # 频域特征
        for feature_type in feature_categories["frequency_domain"]:
            task = self._extract_frequency_domain_feature(pulse_data, sample_rate, feature_type)
            tasks.append(task)

        # 形态学特征
        for feature_type in feature_categories["morphology"]:
            task = self._extract_morphology_feature(pulse_data, sample_rate, feature_type)
            tasks.append(task)

        # 并行执行
        feature_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 收集有效结果
        features = []
        for result in feature_results:
            if isinstance(result, list):
                features.extend(result)
            elif isinstance(result, PulseFeature):
                features.append(result)
            else:
                logger.error(f"特征提取失败: {result}")

        return features

    async def _extract_features(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> list[PulseFeature]:
        """提取脉象特征"""
        features = []

        # 时域特征
        features.extend(await self._extract_time_domain_features(pulse_data, sample_rate))

        # 频域特征
        features.extend(await self._extract_frequency_domain_features(pulse_data, sample_rate))

        # 形态学特征
        features.extend(await self._extract_morphology_features(pulse_data, sample_rate))

        return features

    async def _extract_time_domain_features(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> list[PulseFeature]:
        """提取时域特征"""
        features = []

        # 心率分析
        heart_rate = await self._calculate_heart_rate(pulse_data, sample_rate)
        features.append(PulseFeature(feature_type="heart_rate", value=heart_rate, confidence=0.90))

        # 心率变异性
        hrv = await self._calculate_hrv(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="heart_rate_variability", value=hrv, confidence=0.85)
        )

        # 脉搏幅度
        amplitude_stats = await self._calculate_amplitude_stats(pulse_data)
        features.append(
            PulseFeature(feature_type="pulse_amplitude", value=amplitude_stats, confidence=0.95)
        )

        return features

    async def _extract_frequency_domain_features(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> list[PulseFeature]:
        """提取频域特征"""
        features = []

        # 功率谱分析
        power_spectrum = await self._calculate_power_spectrum(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="power_spectrum", value=power_spectrum, confidence=0.85)
        )

        # 主频分析
        dominant_freq = await self._calculate_dominant_frequency(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="dominant_frequency", value=dominant_freq, confidence=0.80)
        )

        return features

    async def _extract_morphology_features(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> list[PulseFeature]:
        """提取形态学特征"""
        features = []

        # 脉宽分析
        pulse_width = await self._calculate_pulse_width(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="pulse_width", value=pulse_width, confidence=0.85)
        )

        # 上升时间
        rise_time = await self._calculate_rise_time(pulse_data, sample_rate)
        features.append(PulseFeature(feature_type="rise_time", value=rise_time, confidence=0.80))

        # 形状指数
        shape_index = await self._calculate_shape_index(pulse_data)
        features.append(
            PulseFeature(feature_type="shape_index", value=shape_index, confidence=0.75)
        )

        return features

    async def _extract_time_domain_feature(
        self, pulse_data: np.ndarray, sample_rate: int, feature_type: str
    ) -> list[PulseFeature]:
        """提取单个时域特征"""
        if feature_type == "heart_rate":
            value = await self._calculate_heart_rate(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.90)]
        elif feature_type == "hrv":
            value = await self._calculate_hrv(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.85)]
        elif feature_type == "amplitude":
            value = await self._calculate_amplitude_stats(pulse_data)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.95)]

        return []

    async def _extract_frequency_domain_feature(
        self, pulse_data: np.ndarray, sample_rate: int, feature_type: str
    ) -> list[PulseFeature]:
        """提取单个频域特征"""
        if feature_type == "power_spectrum":
            value = await self._calculate_power_spectrum(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.85)]
        elif feature_type == "dominant_frequency":
            value = await self._calculate_dominant_frequency(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.80)]

        return []

    async def _extract_morphology_feature(
        self, pulse_data: np.ndarray, sample_rate: int, feature_type: str
    ) -> list[PulseFeature]:
        """提取单个形态学特征"""
        if feature_type == "pulse_width":
            value = await self._calculate_pulse_width(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.85)]
        elif feature_type == "rise_time":
            value = await self._calculate_rise_time(pulse_data, sample_rate)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.80)]
        elif feature_type == "shape_index":
            value = await self._calculate_shape_index(pulse_data)
            return [PulseFeature(feature_type=feature_type, value=value, confidence=0.75)]

        return []

    # 具体的特征计算方法
    async def _detect_pulse_peaks(self, pulse_data: np.ndarray) -> np.ndarray:
        """检测脉搏峰值"""
        config = self.enhanced_config["pulse_detection"]["peak_detection"]

        # 使用scipy的find_peaks函数
        peaks, _ = signal.find_peaks(
            pulse_data,
            height=config["height_threshold"] * np.max(pulse_data),
            distance=int(config["distance_threshold"] * 1000),  # 转换为样本数
            prominence=config["prominence"] * np.max(pulse_data),
        )

        return peaks

    async def _calculate_heart_rate(self, pulse_data: np.ndarray, sample_rate: int) -> float:
        """计算心率"""
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) < 2:
            return 0.0

        # 计算平均RR间期
        rr_intervals = np.diff(peaks) / sample_rate  # 转换为秒
        mean_rr = np.mean(rr_intervals)

        # 转换为心率（次/分钟）
        heart_rate = 60.0 / mean_rr if mean_rr > 0 else 0.0

        return heart_rate

    async def _calculate_hrv(self, pulse_data: np.ndarray, sample_rate: int) -> dict[str, float]:
        """计算心率变异性"""
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) < 3:
            return {"rmssd": 0.0, "sdnn": 0.0, "pnn50": 0.0}

        # RR间期（毫秒）
        rr_intervals = np.diff(peaks) / sample_rate * 1000

        # RMSSD: 相邻RR间期差值的均方根
        rr_diff = np.diff(rr_intervals)
        rmssd = np.sqrt(np.mean(rr_diff**2))

        # SDNN: RR间期的标准差
        sdnn = np.std(rr_intervals)

        # pNN50: 相邻RR间期差值>50ms的百分比
        pnn50 = np.sum(np.abs(rr_diff) > 50) / len(rr_diff) * 100

        return {"rmssd": float(rmssd), "sdnn": float(sdnn), "pnn50": float(pnn50)}

    async def _calculate_amplitude_stats(self, pulse_data: np.ndarray) -> dict[str, float]:
        """计算幅度统计特征"""
        return {
            "mean": float(np.mean(pulse_data)),
            "std": float(np.std(pulse_data)),
            "max": float(np.max(pulse_data)),
            "min": float(np.min(pulse_data)),
            "range": float(np.max(pulse_data) - np.min(pulse_data)),
        }

    async def _calculate_power_spectrum(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> dict[str, float]:
        """计算功率谱"""
        # 计算功率谱密度
        freqs, psd = signal.welch(pulse_data, sample_rate, nperseg=min(256, len(pulse_data) // 4))

        # 定义频段
        vlf_band = (0.003, 0.04)  # 极低频
        lf_band = (0.04, 0.15)  # 低频
        hf_band = (0.15, 0.4)  # 高频

        # 计算各频段功率
        vlf_power = np.trapz(psd[(freqs >= vlf_band[0]) & (freqs < vlf_band[1])])
        lf_power = np.trapz(psd[(freqs >= lf_band[0]) & (freqs < lf_band[1])])
        hf_power = np.trapz(psd[(freqs >= hf_band[0]) & (freqs < hf_band[1])])

        total_power = vlf_power + lf_power + hf_power

        return {
            "vlf_power": float(vlf_power),
            "lf_power": float(lf_power),
            "hf_power": float(hf_power),
            "total_power": float(total_power),
            "lf_hf_ratio": float(lf_power / hf_power) if hf_power > 0 else 0.0,
        }

    async def _calculate_dominant_frequency(
        self, pulse_data: np.ndarray, sample_rate: int
    ) -> float:
        """计算主频"""
        # FFT分析
        fft_result = np.fft.fft(pulse_data)
        freqs = np.fft.fftfreq(len(pulse_data), 1 / sample_rate)

        # 只考虑正频率
        positive_freqs = freqs[: len(freqs) // 2]
        magnitude = np.abs(fft_result[: len(fft_result) // 2])

        # 找到最大幅值对应的频率
        dominant_freq_idx = np.argmax(magnitude)
        dominant_freq = positive_freqs[dominant_freq_idx]

        return float(dominant_freq)

    async def _calculate_pulse_width(self, pulse_data: np.ndarray, sample_rate: int) -> float:
        """计算脉宽"""
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) == 0:
            return 0.0

        widths = []
        for peak in peaks:
            # 找到半高宽
            peak_height = pulse_data[peak]
            half_height = peak_height / 2

            # 向左搜索
            left_idx = peak
            while left_idx > 0 and pulse_data[left_idx] > half_height:
                left_idx -= 1

            # 向右搜索
            right_idx = peak
            while right_idx < len(pulse_data) - 1 and pulse_data[right_idx] > half_height:
                right_idx += 1

            width = (right_idx - left_idx) / sample_rate
            widths.append(width)

        return float(np.mean(widths)) if widths else 0.0

    async def _calculate_rise_time(self, pulse_data: np.ndarray, sample_rate: int) -> float:
        """计算上升时间"""
        peaks = await self._detect_pulse_peaks(pulse_data)

        if len(peaks) == 0:
            return 0.0

        rise_times = []
        for peak in peaks:
            # 找到10%和90%的位置
            peak_height = pulse_data[peak]
            ten_percent = peak_height * 0.1
            ninety_percent = peak_height * 0.9

            # 向左搜索10%位置
            left_idx = peak
            while left_idx > 0 and pulse_data[left_idx] > ten_percent:
                left_idx -= 1

            # 从10%位置向右搜索90%位置
            ninety_idx = left_idx
            while ninety_idx < peak and pulse_data[ninety_idx] < ninety_percent:
                ninety_idx += 1

            rise_time = (ninety_idx - left_idx) / sample_rate
            rise_times.append(rise_time)

        return float(np.mean(rise_times)) if rise_times else 0.0

    async def _calculate_shape_index(self, pulse_data: np.ndarray) -> float:
        """计算形状指数"""
        # 使用偏度和峰度来描述波形形状
        skewness = float(pd.Series(pulse_data).skew())
        kurtosis = float(pd.Series(pulse_data).kurtosis())

        # 组合形状指数
        shape_index = np.sqrt(skewness**2 + kurtosis**2)

        return float(shape_index)

    async def _analyze_pulse_characteristics(
        self, features: list[PulseFeature], pulse_data: np.ndarray, sample_rate: int
    ) -> dict[str, Any]:
        """分析脉象特征"""
        characteristics = {}

        # 提取心率特征
        heart_rate_feature = next((f for f in features if f.feature_type == "heart_rate"), None)
        if heart_rate_feature:
            heart_rate = heart_rate_feature.value
            if heart_rate < 60:
                characteristics["pulse_rate"] = PulseRate.SLOW.value
            elif heart_rate > 100:
                characteristics["pulse_rate"] = PulseRate.RAPID.value
            else:
                characteristics["pulse_rate"] = PulseRate.NORMAL.value

        # 分析脉力
        amplitude_feature = next((f for f in features if f.feature_type == "pulse_amplitude"), None)
        if amplitude_feature:
            amplitude_range = amplitude_feature.value.get("range", 0)
            if amplitude_range < 0.3:
                characteristics["pulse_strength"] = PulseStrength.WEAK.value
            elif amplitude_range > 0.7:
                characteristics["pulse_strength"] = PulseStrength.STRONG.value
            else:
                characteristics["pulse_strength"] = PulseStrength.MODERATE.value

        # 分析脉律
        hrv_feature = next(
            (f for f in features if f.feature_type == "heart_rate_variability"), None
        )
        if hrv_feature:
            rmssd = hrv_feature.value.get("rmssd", 0)
            if rmssd < 20:
                characteristics["pulse_rhythm"] = PulseRhythm.REGULAR.value
            elif rmssd > 50:
                characteristics["pulse_rhythm"] = PulseRhythm.IRREGULAR.value
            else:
                characteristics["pulse_rhythm"] = PulseRhythm.REGULAR.value

        # 分析脉位（基于幅度特征）
        if amplitude_feature:
            mean_amplitude = amplitude_feature.value.get("mean", 0)
            if mean_amplitude > 0.6:
                characteristics["pulse_position"] = PulsePosition.FLOATING.value
            elif mean_amplitude < 0.3:
                characteristics["pulse_position"] = PulsePosition.DEEP.value
            else:
                characteristics["pulse_position"] = PulsePosition.MIDDLE.value

        # 分析脉形
        shape_feature = next((f for f in features if f.feature_type == "shape_index"), None)
        width_feature = next((f for f in features if f.feature_type == "pulse_width"), None)

        if shape_feature and width_feature:
            shape_index = shape_feature.value
            pulse_width = width_feature.value

            if pulse_width < 0.3:
                characteristics["pulse_shape"] = PulseShape.THIN.value
            elif pulse_width > 0.6:
                characteristics["pulse_shape"] = PulseShape.THICK.value
            elif shape_index > 2.0:
                characteristics["pulse_shape"] = PulseShape.ROUGH.value
            else:
                characteristics["pulse_shape"] = PulseShape.SLIPPERY.value

        return characteristics

    async def _analyze_syndrome_indicators(
        self, pulse_characteristics: dict[str, Any], features: list[PulseFeature]
    ) -> dict[str, float]:
        """分析证候指标"""
        indicators = {}

        # 基于脉象特征分析证候
        pulse_rate = pulse_characteristics.get("pulse_rate")
        pulse_strength = pulse_characteristics.get("pulse_strength")
        pulse_position = pulse_characteristics.get("pulse_position")
        pulse_shape = pulse_characteristics.get("pulse_shape")

        # 气虚证候
        if pulse_strength == PulseStrength.WEAK.value or pulse_rate == PulseRate.SLOW.value:
            indicators["气虚"] = indicators.get("气虚", 0) + 0.3

        # 血虚证候
        if pulse_shape == PulseShape.THIN.value or pulse_strength == PulseStrength.WEAK.value:
            indicators["血虚"] = indicators.get("血虚", 0) + 0.3

        # 阳虚证候
        if pulse_rate == PulseRate.SLOW.value and pulse_position == PulsePosition.DEEP.value:
            indicators["阳虚"] = indicators.get("阳虚", 0) + 0.4

        # 阴虚证候
        if pulse_rate == PulseRate.RAPID.value and pulse_shape == PulseShape.THIN.value:
            indicators["阴虚"] = indicators.get("阴虚", 0) + 0.4

        # 实热证候
        if pulse_rate == PulseRate.RAPID.value and pulse_strength == PulseStrength.STRONG.value:
            indicators["实热"] = indicators.get("实热", 0) + 0.4

        # 痰湿证候
        if pulse_shape == PulseShape.SLIPPERY.value:
            indicators["痰湿"] = indicators.get("痰湿", 0) + 0.3

        # 血瘀证候
        if pulse_shape == PulseShape.ROUGH.value:
            indicators["血瘀"] = indicators.get("血瘀", 0) + 0.3

        # 归一化
        total = sum(indicators.values())
        if total > 0:
            for key in indicators:
                indicators[key] /= total

        return indicators

    async def _generate_recommendations(
        self, syndrome_indicators: dict[str, float], pulse_characteristics: dict[str, Any]
    ) -> list[str]:
        """生成建议"""
        recommendations = []

        # 基于证候指标生成建议
        primary_syndrome = (
            max(syndrome_indicators.items(), key=lambda x: x[1])[0] if syndrome_indicators else None
        )

        if primary_syndrome == "气虚":
            recommendations.extend(
                [
                    "建议适当休息，避免过度劳累",
                    "可进行温和的运动如太极拳、八段锦",
                    "适当食用补气食物如人参、黄芪、山药等",
                ]
            )
        elif primary_syndrome == "血虚":
            recommendations.extend(
                [
                    "保证充足的睡眠，避免熬夜",
                    "适当食用补血食物如红枣、枸杞、当归等",
                    "避免过度用眼和思虑",
                ]
            )
        elif primary_syndrome == "阳虚":
            recommendations.extend(
                ["注意保暖，避免受寒", "适当食用温阳食物如羊肉、生姜、肉桂等", "进行适度的有氧运动"]
            )
        elif primary_syndrome == "阴虚":
            recommendations.extend(
                [
                    "多饮水，保持充足的水分",
                    "适当食用滋阴食物如银耳、百合、麦冬等",
                    "避免熬夜和辛辣刺激食物",
                ]
            )
        elif primary_syndrome == "实热":
            recommendations.extend(
                [
                    "饮食宜清淡，避免辛辣油腻",
                    "多食用清热食物如绿豆、苦瓜、菊花等",
                    "保持心情平和，避免情绪激动",
                ]
            )
        elif primary_syndrome == "痰湿":
            recommendations.extend(
                [
                    "饮食清淡，减少油腻甜腻食物",
                    "适当运动，促进痰湿排出",
                    "可食用化痰食物如陈皮、茯苓、薏米等",
                ]
            )
        elif primary_syndrome == "血瘀":
            recommendations.extend(
                [
                    "适当运动，促进血液循环",
                    "可食用活血食物如山楂、红花、丹参等",
                    "保持心情舒畅，避免情志不畅",
                ]
            )

        # 基于脉象特征的通用建议
        pulse_rate = pulse_characteristics.get("pulse_rate")
        if pulse_rate == PulseRate.RAPID.value:
            recommendations.append("注意休息，避免过度兴奋")
        elif pulse_rate == PulseRate.SLOW.value:
            recommendations.append("适当增加运动量，促进血液循环")

        # 添加通用建议
        recommendations.append("建议定期进行中医体检")
        recommendations.append("如有不适，请及时就医")

        return recommendations

    def _hash_pulse_data(self, pulse_data: list[PulseDataPoint]) -> str:
        """计算脉象数据的哈希值"""
        # 提取关键信息用于哈希
        data_str = ""
        for point in pulse_data[:100]:  # 只使用前100个点
            data_str += f"{point.amplitude:.3f},{point.pressure:.3f},"

        return hashlib.md5(data_str.encode()).hexdigest()

    async def batch_analyze(self, requests: list[PulseAnalysisRequest]) -> list[PalpationResult]:
        """
        批量分析脉象数据

        Args:
            requests: 脉象分析请求列表

        Returns:
            分析结果列表
        """
        if self.enhanced_config["parallel_processing"]["enabled"]:
            # 并行处理
            tasks = []
            for request in requests:
                task = self.analyze_pulse(
                    patient_id=request.patient_id,
                    pulse_data=request.pulse_data,
                    duration=request.duration,
                    sample_rate=request.sample_rate,
                    metadata=request.metadata,
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 过滤有效结果
            valid_results = []
            for result in results:
                if isinstance(result, PalpationResult):
                    valid_results.append(result)
                else:
                    logger.error(f"批量分析失败: {result}")

            self.stats["batch_processed"] += 1
            return valid_results
        else:
            # 串行处理
            results = []
            for request in requests:
                try:
                    result = await self.analyze_pulse(
                        patient_id=request.patient_id,
                        pulse_data=request.pulse_data,
                        duration=request.duration,
                        sample_rate=request.sample_rate,
                        metadata=request.metadata,
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
                deadline = time.time() + 2.0  # 2秒收集窗口

                # 收集批次
                while len(batch) < self.enhanced_config["parallel_processing"]["batch_size"]:
                    try:
                        remaining_time = deadline - time.time()
                        if remaining_time <= 0:
                            break

                        request = await asyncio.wait_for(
                            self.batch_queue.get(), timeout=remaining_time
                        )
                        batch.append(request)
                    except TimeoutError:
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
                max_size = self.enhanced_config["caching"]["max_cache_size"]
                if len(self.cache) > max_size:
                    # 删除最旧的项
                    items = sorted(self.cache.items(), key=lambda x: x[1][1])
                    for key, _ in items[: len(items) // 2]:
                        del self.cache[key]
                    logger.info(f"缓存大小超限，清理了{len(items)//2}个项")

                await asyncio.sleep(300)  # 5分钟清理一次

            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)

    async def _get_from_cache(self, key: str) -> Any | None:
        """从缓存获取数据"""
        if not self.enhanced_config["caching"]["enabled"]:
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
        if not self.enhanced_config["caching"]["enabled"]:
            return

        ttl = self.enhanced_config["caching"]["ttl_seconds"].get(ttl_type, 1800)
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
        if self.stats["average_processing_time_ms"] == 0:
            self.stats["average_processing_time_ms"] = processing_time_ms
        else:
            self.stats["average_processing_time_ms"] = (
                alpha * processing_time_ms + (1 - alpha) * self.stats["average_processing_time_ms"]
            )

    async def get_service_stats(self) -> dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = self.stats["cache_hits"] / max(
            1, self.stats["cache_hits"] + self.stats["cache_misses"]
        )

        return {
            "total_requests": self.stats["total_requests"],
            "successful_analyses": self.stats["successful_analyses"],
            "cache_hit_rate": cache_hit_rate,
            "average_processing_time_ms": self.stats["average_processing_time_ms"],
            "quality_distribution": dict(self.stats["quality_distribution"]),
            "batch_processed": self.stats["batch_processed"],
            "cache_size": len(self.cache),
            "pulse_patterns_detected": dict(self.stats["pulse_patterns_detected"]),
        }

    async def close(self):
        """关闭服务"""
        # 停止后台任务
        for task in self.background_tasks:
            task.cancel()

        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        logger.info("增强版切诊服务已关闭")
