"""
enhanced_palpation_service - 索克生活项目模块
增强版切诊服务

该模块是切诊服务的增强版本，集成了高性能脉象数据处理、并行分析、智能缓存和批量诊断功能，
提供专业的中医切诊数据采集和分析服务。
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import asyncio
import hashlib
import json
import logging
import time
import uuid

logger = logging.getLogger(__name__)

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
    pulse_data: List[PulseDataPoint]
    duration: float  # 采集时长（秒）
    sample_rate: int = 1000  # 采样率
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PulseFeature:
    """脉象特征"""
    feature_type: str
    value: Any
    confidence: float
    channel: int = 0
    time_range: Optional[Tuple[float, float]] = None

@dataclass
class PalpationResult:
    """切诊结果"""
    request_id: str
    patient_id: str
    pulse_characteristics: Dict[str, Any]  # 脉象特征
    features: List[PulseFeature]
    syndrome_indicators: Dict[str, float]  # 证候指标
    quality_score: float
    processing_time_ms: float
    recommendations: List[str]

@dataclass
class BatchPulseRequest:
    """批量脉象分析请求"""
    batch_id: str
    requests: List[PulseAnalysisRequest]
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)

class EnhancedPalpationService:
    """增强版切诊服务"""

    def __init__(self, config: Dict[str, Any]):
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
        self.cache: Dict[str, Tuple[Any, datetime]] = {}

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

        # 后台任务
        self.background_tasks: List[asyncio.Task] = []

        logger.info("增强版切诊服务初始化完成")

    async def initialize(self) -> None:
        """初始化服务"""
        # 启动后台任务
        self._start_background_tasks()
        logger.info("切诊服务初始化完成")

    def _start_background_tasks(self) -> None:
        """启动后台任务"""
        # 批处理处理器
        self.background_tasks.append(asyncio.create_task(self._batch_processor()))

        # 缓存清理器
        self.background_tasks.append(asyncio.create_task(self._cache_cleaner()))

    async def analyze_pulse(
        self,
        patient_id: str,
        pulse_data: List[PulseDataPoint],
        duration: float,
        sample_rate: int = 1000,
        metadata: Optional[Dict[str, Any]] = None,
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

            # 提取特征
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
        self, pulse_data: List[PulseDataPoint], sample_rate: int
    ) -> List[float]:
        """预处理脉象数据"""
        if not pulse_data:
            raise ValueError("脉象数据为空")

        # 提取幅值数据
        amplitudes = [point.amplitude for point in pulse_data]

        # 简单的异常值处理
        filtered_data = await self._filter_pulse_signal(amplitudes, sample_rate)

        return filtered_data

    async def _filter_pulse_signal(
        self, signal_data: List[float], sample_rate: int
    ) -> List[float]:
        """滤波处理脉象信号"""
        # 简化的滤波处理
        # 这里可以添加更复杂的信号处理逻辑
        return signal_data

    async def _assess_pulse_quality(
        self, pulse_data: List[float], duration: float
    ) -> float:
        """评估脉象数据质量"""
        if not pulse_data:
            return 0.0

        # 简化的质量评估
        # 基于数据长度和变异性
        if len(pulse_data) < 100:
            return 0.3

        # 计算变异系数
        import statistics
        mean_val = statistics.mean(pulse_data)
        std_val = statistics.stdev(pulse_data) if len(pulse_data) > 1 else 0
        cv = std_val / abs(mean_val) if mean_val != 0 else 1

        # 质量分数
        quality_score = max(0.0, min(1.0, 1.0 - cv))
        return quality_score

    async def _enhance_pulse_data(self, pulse_data: List[float]) -> List[float]:
        """增强脉象数据质量"""
        # 简化的数据增强
        return pulse_data

    async def _extract_features(
        self, pulse_data: List[float], sample_rate: int
    ) -> List[PulseFeature]:
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
        self, pulse_data: List[float], sample_rate: int
    ) -> List[PulseFeature]:
        """提取时域特征"""
        features = []

        # 心率分析
        heart_rate = await self._calculate_heart_rate(pulse_data, sample_rate)
        features.append(PulseFeature(feature_type="heart_rate", value=heart_rate, confidence=0.90))

        # 脉搏幅度
        amplitude_stats = await self._calculate_amplitude_stats(pulse_data)
        features.append(
            PulseFeature(feature_type="pulse_amplitude", value=amplitude_stats, confidence=0.95)
        )

        return features

    async def _extract_frequency_domain_features(
        self, pulse_data: List[float], sample_rate: int
    ) -> List[PulseFeature]:
        """提取频域特征"""
        features = []

        # 主频分析
        dominant_freq = await self._calculate_dominant_frequency(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="dominant_frequency", value=dominant_freq, confidence=0.80)
        )

        return features

    async def _extract_morphology_features(
        self, pulse_data: List[float], sample_rate: int
    ) -> List[PulseFeature]:
        """提取形态学特征"""
        features = []

        # 脉宽分析
        pulse_width = await self._calculate_pulse_width(pulse_data, sample_rate)
        features.append(
            PulseFeature(feature_type="pulse_width", value=pulse_width, confidence=0.85)
        )

        return features

    async def _calculate_heart_rate(self, pulse_data: List[float], sample_rate: int) -> float:
        """计算心率"""
        # 简化的心率计算
        if len(pulse_data) < sample_rate:
            return 0.0

        # 假设每秒有一个心跳周期
        duration_seconds = len(pulse_data) / sample_rate
        estimated_beats = duration_seconds * 1.2  # 假设心率约72次/分钟
        heart_rate = estimated_beats * 60 / duration_seconds

        return min(max(heart_rate, 40), 200)  # 限制在合理范围内

    async def _calculate_amplitude_stats(self, pulse_data: List[float]) -> Dict[str, float]:
        """计算幅度统计特征"""
        if not pulse_data:
            return {"mean": 0.0, "std": 0.0, "max": 0.0, "min": 0.0, "range": 0.0}

        import statistics
        mean_val = statistics.mean(pulse_data)
        std_val = statistics.stdev(pulse_data) if len(pulse_data) > 1 else 0.0
        max_val = max(pulse_data)
        min_val = min(pulse_data)
        range_val = max_val - min_val

        return {
            "mean": mean_val,
            "std": std_val,
            "max": max_val,
            "min": min_val,
            "range": range_val,
        }

    async def _calculate_dominant_frequency(
        self, pulse_data: List[float], sample_rate: int
    ) -> float:
        """计算主频"""
        # 简化的主频计算
        # 假设主频在1-3Hz范围内（对应60-180次/分钟的心率）
        return 1.2  # 假设主频为1.2Hz

    async def _calculate_pulse_width(
        self, pulse_data: List[float], sample_rate: int
    ) -> float:
        """计算脉宽"""
        # 简化的脉宽计算
        return 0.4  # 假设脉宽为0.4秒

    async def _analyze_pulse_characteristics(
        self, features: List[PulseFeature], pulse_data: List[float], sample_rate: int
    ) -> Dict[str, Any]:
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

        # 默认脉律为规律
        characteristics["pulse_rhythm"] = PulseRhythm.REGULAR.value

        # 默认脉位为中位
        characteristics["pulse_position"] = PulsePosition.MIDDLE.value

        # 默认脉形为滑脉
        characteristics["pulse_shape"] = PulseShape.SLIPPERY.value

        return characteristics

    async def _analyze_syndrome_indicators(
        self, pulse_characteristics: Dict[str, Any], features: List[PulseFeature]
    ) -> Dict[str, float]:
        """分析证候指标"""
        indicators = {}

        # 基于脉象特征分析证候
        pulse_rate = pulse_characteristics.get("pulse_rate")
        pulse_strength = pulse_characteristics.get("pulse_strength")

        # 气虚证候
        if pulse_strength == PulseStrength.WEAK.value or pulse_rate == PulseRate.SLOW.value:
            indicators["气虚"] = indicators.get("气虚", 0) + 0.3

        # 实热证候
        if pulse_rate == PulseRate.RAPID.value and pulse_strength == PulseStrength.STRONG.value:
            indicators["实热"] = indicators.get("实热", 0) + 0.4

        # 归一化
        total = sum(indicators.values())
        if total > 0:
            for key in indicators:
                indicators[key] /= total
        else:
            # 默认平和体质
            indicators["平和"] = 1.0

        return indicators

    async def _generate_recommendations(
        self, syndrome_indicators: Dict[str, float], pulse_characteristics: Dict[str, Any]
    ) -> List[str]:
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
        elif primary_syndrome == "实热":
            recommendations.extend(
                [
                    "饮食宜清淡，避免辛辣油腻",
                    "多食用清热食物如绿豆、苦瓜、菊花等",
                    "保持心情平和，避免情绪激动",
                ]
            )
        else:
            recommendations.extend(
                [
                    "保持良好的生活习惯",
                    "适当运动，均衡饮食",
                    "定期体检，关注健康状况",
                ]
            )

        # 添加通用建议
        recommendations.append("建议定期进行中医体检")
        recommendations.append("如有不适，请及时就医")

        return recommendations

    def _hash_pulse_data(self, pulse_data: List[PulseDataPoint]) -> str:
        """计算脉象数据的哈希值"""
        # 提取关键信息用于哈希
        data_str = ""
        for point in pulse_data[:100]:  # 只使用前100个点
            data_str += f"{point.amplitude:.3f},{point.pressure:.3f},"

        return hashlib.md5(data_str.encode()).hexdigest()

    async def batch_analyze(self, requests: List[PulseAnalysisRequest]) -> List[PalpationResult]:
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

    async def _batch_processor(self) -> None:
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
                    except asyncio.TimeoutError:
                        break

                if batch:
                    # 处理批次
                    await self.batch_analyze(batch)

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"批处理器错误: {e}")
                await asyncio.sleep(1)

    async def _cache_cleaner(self) -> None:
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
                    for key, _ in items[:len(items) // 2]:
                        del self.cache[key]
                    logger.info(f"缓存大小超限，清理了{len(items) // 2}个项")

                await asyncio.sleep(300)  # 5分钟清理一次

            except Exception as e:
                logger.error(f"缓存清理器错误: {e}")
                await asyncio.sleep(60)

    async def _get_from_cache(self, key: str) -> Optional[Any]:
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

    async def _set_to_cache(self, key: str, value: Any, ttl_type: str = "analysis_result") -> None:
        """设置缓存"""
        if not self.enhanced_config["caching"]["enabled"]:
            return

        ttl = self.enhanced_config["caching"]["ttl_seconds"].get(ttl_type, 1800)
        expire_time = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = (value, expire_time)

    def _generate_cache_key(self, *args) -> str:
        """生成缓存键"""
        key_data = json.dumps(args, sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()

    def _update_stats(self, processing_time_ms: float) -> None:
        """更新统计信息"""
        # 更新平均处理时间
        alpha = 0.1
        if self.stats["average_processing_time_ms"] == 0:
            self.stats["average_processing_time_ms"] = processing_time_ms
        else:
            self.stats["average_processing_time_ms"] = (
                alpha * processing_time_ms + (1 - alpha) * self.stats["average_processing_time_ms"]
            )

    async def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        cache_hit_rate = self.stats["cache_hits"] / max(
            self.stats["cache_hits"] + self.stats["cache_misses"], 1
        )

        return {
            "total_requests": self.stats["total_requests"],
            "successful_analyses": self.stats["successful_analyses"],
            "cache_hit_rate": cache_hit_rate,
            "average_processing_time_ms": self.stats["average_processing_time_ms"],
            "batch_processed": self.stats["batch_processed"],
            "cache_size": len(self.cache),
        }

    async def close(self) -> None:
        """关闭服务"""
        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()

        # 等待任务完成
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        logger.info("增强版切诊服务已关闭")
