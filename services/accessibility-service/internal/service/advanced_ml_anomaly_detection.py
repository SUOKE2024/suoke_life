#!/usr/bin/env python3
"""
高级机器学习异常检测模块
特性：
1. 多算法融合检测
2. 自适应阈值调整
3. 时序模式识别
4. 实时流处理
5. 异常根因分析
6. 预测性异常检测
"""

import asyncio
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """异常类型"""

    POINT_ANOMALY = "point"  # 点异常
    CONTEXTUAL_ANOMALY = "contextual"  # 上下文异常
    COLLECTIVE_ANOMALY = "collective"  # 集体异常
    TREND_ANOMALY = "trend"  # 趋势异常
    SEASONAL_ANOMALY = "seasonal"  # 季节性异常


class AnomalySeverity(Enum):
    """异常严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyResult:
    """异常检测结果"""

    timestamp: float
    metric_name: str
    value: float
    is_anomaly: bool
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    expected_range: tuple[float, float]
    deviation_score: float
    context: dict[str, Any] = field(default_factory=dict)
    root_cause: str | None = None


@dataclass
class MetricData:
    """指标数据"""

    name: str
    values: deque
    timestamps: deque
    max_size: int = 1000

    def add_value(self, value: float, timestamp: float = None):
        """添加数值"""
        if timestamp is None:
            timestamp = time.time()

        self.values.append(value)
        self.timestamps.append(timestamp)

        # 保持固定大小
        while len(self.values) > self.max_size:
            self.values.popleft()
            self.timestamps.popleft()

    def get_recent_values(self, count: int = None) -> list[float]:
        """获取最近的数值"""
        if count is None:
            return list(self.values)
        return list(self.values)[-count:]

    def get_values_in_window(self, window_seconds: int) -> list[tuple[float, float]]:
        """获取时间窗口内的数值"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        result = []
        for value, timestamp in zip(self.values, self.timestamps, strict=False):
            if timestamp >= cutoff_time:
                result.append((value, timestamp))

        return result


class StatisticalAnomalyDetector:
    """统计异常检测器"""

    def __init__(self, window_size: int = 50, z_threshold: float = 3.0):
        self.window_size = window_size
        self.z_threshold = z_threshold

    def detect(self, data: MetricData) -> AnomalyResult | None:
        """检测异常"""
        values = data.get_recent_values(self.window_size)

        if len(values) < 10:  # 需要足够的数据
            return None

        current_value = values[-1]
        historical_values = values[:-1]

        # 计算统计指标
        mean = np.mean(historical_values)
        std = np.std(historical_values)

        if std == 0:  # 避免除零
            return None

        # Z-score检测
        z_score = abs(current_value - mean) / std
        is_anomaly = z_score > self.z_threshold

        if is_anomaly:
            # 计算期望范围
            expected_range = (
                mean - self.z_threshold * std,
                mean + self.z_threshold * std,
            )

            # 确定严重程度
            if z_score > 5:
                severity = AnomalySeverity.CRITICAL
            elif z_score > 4:
                severity = AnomalySeverity.HIGH
            elif z_score > 3.5:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW

            return AnomalyResult(
                timestamp=time.time(),
                metric_name=data.name,
                value=current_value,
                is_anomaly=True,
                anomaly_type=AnomalyType.POINT_ANOMALY,
                severity=severity,
                confidence=min(z_score / 5.0, 1.0),
                expected_range=expected_range,
                deviation_score=z_score,
                context={
                    "mean": mean,
                    "std": std,
                    "z_score": z_score,
                    "method": "statistical",
                },
            )

        return None


class IsolationForestDetector:
    """孤立森林异常检测器"""

    def __init__(self, contamination: float = 0.1, n_estimators: int = 100):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.model = None
        self.is_fitted = False
        self.feature_scaler = None

        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler

            self.IsolationForest = IsolationForest
            self.StandardScaler = StandardScaler
            self.sklearn_available = True
        except ImportError:
            logger.warning("scikit-learn不可用，孤立森林检测器将被禁用")
            self.sklearn_available = False

    def _prepare_features(self, data: MetricData) -> np.ndarray | None:
        """准备特征"""
        values = data.get_recent_values(100)

        if len(values) < 20:
            return None

        # 构建特征：当前值、移动平均、趋势等
        features = []
        window_sizes = [5, 10, 20]

        for i in range(len(values)):
            feature_vector = [values[i]]  # 当前值

            # 移动平均特征
            for window in window_sizes:
                if i >= window - 1:
                    ma = np.mean(values[i - window + 1 : i + 1])
                    feature_vector.append(ma)
                else:
                    feature_vector.append(values[i])

            # 趋势特征
            if i >= 5:
                trend = np.polyfit(range(5), values[i - 4 : i + 1], 1)[0]
                feature_vector.append(trend)
            else:
                feature_vector.append(0)

            # 波动性特征
            if i >= 10:
                volatility = np.std(values[i - 9 : i + 1])
                feature_vector.append(volatility)
            else:
                feature_vector.append(0)

            features.append(feature_vector)

        return np.array(features)

    def detect(self, data: MetricData) -> AnomalyResult | None:
        """检测异常"""
        if not self.sklearn_available:
            return None

        features = self._prepare_features(data)
        if features is None:
            return None

        try:
            # 训练模型（如果需要）
            if not self.is_fitted or len(features) > 200:  # 定期重训练
                self.feature_scaler = self.StandardScaler()
                scaled_features = self.feature_scaler.fit_transform(features)

                self.model = self.IsolationForest(
                    contamination=self.contamination,
                    n_estimators=self.n_estimators,
                    random_state=42,
                )
                self.model.fit(scaled_features)
                self.is_fitted = True

            # 预测当前点
            current_features = features[-1:]
            scaled_current = self.feature_scaler.transform(current_features)

            anomaly_score = self.model.decision_function(scaled_current)[0]
            is_anomaly = self.model.predict(scaled_current)[0] == -1

            if is_anomaly:
                # 计算置信度和严重程度
                confidence = abs(anomaly_score)

                if confidence > 0.5:
                    severity = AnomalySeverity.CRITICAL
                elif confidence > 0.3:
                    severity = AnomalySeverity.HIGH
                elif confidence > 0.1:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                current_value = data.get_recent_values(1)[0]

                return AnomalyResult(
                    timestamp=time.time(),
                    metric_name=data.name,
                    value=current_value,
                    is_anomaly=True,
                    anomaly_type=AnomalyType.CONTEXTUAL_ANOMALY,
                    severity=severity,
                    confidence=min(confidence, 1.0),
                    expected_range=(
                        float("-inf"),
                        float("inf"),
                    ),  # 孤立森林不提供具体范围
                    deviation_score=abs(anomaly_score),
                    context={
                        "anomaly_score": anomaly_score,
                        "method": "isolation_forest",
                        "features_count": len(current_features[0]),
                    },
                )

        except Exception as e:
            logger.error(f"孤立森林检测失败: {e}")

        return None


class TrendAnomalyDetector:
    """趋势异常检测器"""

    def __init__(self, window_size: int = 30, trend_threshold: float = 0.1):
        self.window_size = window_size
        self.trend_threshold = trend_threshold

    def detect(self, data: MetricData) -> AnomalyResult | None:
        """检测趋势异常"""
        values = data.get_recent_values(self.window_size)

        if len(values) < self.window_size:
            return None

        try:
            # 计算线性趋势
            x = np.arange(len(values))
            coeffs = np.polyfit(x, values, 1)
            trend_slope = coeffs[0]

            # 计算趋势强度
            y_pred = np.polyval(coeffs, x)
            r_squared = 1 - (
                np.sum((values - y_pred) ** 2) / np.sum((values - np.mean(values)) ** 2)
            )

            # 检测异常趋势
            is_anomaly = abs(trend_slope) > self.trend_threshold and r_squared > 0.7

            if is_anomaly:
                # 确定严重程度
                trend_magnitude = abs(trend_slope)
                if trend_magnitude > self.trend_threshold * 5:
                    severity = AnomalySeverity.CRITICAL
                elif trend_magnitude > self.trend_threshold * 3:
                    severity = AnomalySeverity.HIGH
                elif trend_magnitude > self.trend_threshold * 2:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                current_value = values[-1]

                return AnomalyResult(
                    timestamp=time.time(),
                    metric_name=data.name,
                    value=current_value,
                    is_anomaly=True,
                    anomaly_type=AnomalyType.TREND_ANOMALY,
                    severity=severity,
                    confidence=r_squared,
                    expected_range=(float("-inf"), float("inf")),
                    deviation_score=trend_magnitude,
                    context={
                        "trend_slope": trend_slope,
                        "r_squared": r_squared,
                        "trend_direction": (
                            "increasing" if trend_slope > 0 else "decreasing"
                        ),
                        "method": "trend_analysis",
                    },
                )

        except Exception as e:
            logger.error(f"趋势检测失败: {e}")

        return None


class SeasonalAnomalyDetector:
    """季节性异常检测器"""

    def __init__(self, period: int = 60, seasonal_threshold: float = 2.0):
        self.period = period  # 季节周期（分钟）
        self.seasonal_threshold = seasonal_threshold
        self.seasonal_patterns = {}

    def detect(self, data: MetricData) -> AnomalyResult | None:
        """检测季节性异常"""
        # 获取足够的历史数据
        window_data = data.get_values_in_window(self.period * 60 * 3)  # 3个周期的数据

        if len(window_data) < self.period * 2:
            return None

        try:
            current_time = time.time()
            current_value = data.get_recent_values(1)[0]

            # 计算当前时间在周期中的位置
            time_in_period = int((current_time % (self.period * 60)) / 60)

            # 收集同一时间点的历史数据
            historical_values = []
            for value, timestamp in window_data[:-1]:  # 排除当前值
                hist_time_in_period = int((timestamp % (self.period * 60)) / 60)
                if abs(hist_time_in_period - time_in_period) <= 2:  # 允许2分钟误差
                    historical_values.append(value)

            if len(historical_values) < 3:
                return None

            # 计算季节性期望值和标准差
            seasonal_mean = np.mean(historical_values)
            seasonal_std = np.std(historical_values)

            if seasonal_std == 0:
                return None

            # 计算季节性偏差
            seasonal_deviation = abs(current_value - seasonal_mean) / seasonal_std
            is_anomaly = seasonal_deviation > self.seasonal_threshold

            if is_anomaly:
                # 确定严重程度
                if seasonal_deviation > 4:
                    severity = AnomalySeverity.CRITICAL
                elif seasonal_deviation > 3:
                    severity = AnomalySeverity.HIGH
                elif seasonal_deviation > 2.5:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                expected_range = (
                    seasonal_mean - self.seasonal_threshold * seasonal_std,
                    seasonal_mean + self.seasonal_threshold * seasonal_std,
                )

                return AnomalyResult(
                    timestamp=current_time,
                    metric_name=data.name,
                    value=current_value,
                    is_anomaly=True,
                    anomaly_type=AnomalyType.SEASONAL_ANOMALY,
                    severity=severity,
                    confidence=min(seasonal_deviation / 4.0, 1.0),
                    expected_range=expected_range,
                    deviation_score=seasonal_deviation,
                    context={
                        "seasonal_mean": seasonal_mean,
                        "seasonal_std": seasonal_std,
                        "time_in_period": time_in_period,
                        "historical_count": len(historical_values),
                        "method": "seasonal_analysis",
                    },
                )

        except Exception as e:
            logger.error(f"季节性检测失败: {e}")

        return None


class EnsembleAnomalyDetector:
    """集成异常检测器"""

    def __init__(self) -> None:
        self.detectors = [
            StatisticalAnomalyDetector(),
            IsolationForestDetector(),
            TrendAnomalyDetector(),
            SeasonalAnomalyDetector(),
        ]
        self.weights = [0.3, 0.3, 0.2, 0.2]  # 检测器权重

    def detect(self, data: MetricData) -> list[AnomalyResult]:
        """集成检测"""
        results = []

        for detector in self.detectors:
            try:
                result = detector.detect(data)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"检测器 {type(detector).__name__} 失败: {e}")

        return results

    def get_consensus_result(self, data: MetricData) -> AnomalyResult | None:
        """获取共识结果"""
        results = self.detect(data)

        if not results:
            return None

        # 如果多个检测器都认为是异常，则提高置信度
        if len(results) >= 2:
            # 选择最高严重程度的结果
            critical_results = [
                r for r in results if r.severity == AnomalySeverity.CRITICAL
            ]
            if critical_results:
                best_result = critical_results[0]
            else:
                best_result = max(results, key=lambda r: r.confidence)

            # 提高置信度
            best_result.confidence = min(best_result.confidence * 1.5, 1.0)
            best_result.context["ensemble_count"] = len(results)
            best_result.context["consensus"] = True

            return best_result

        # 单个检测器结果
        return results[0]


class AdvancedMLAnomalyManager:
    """高级机器学习异常管理器"""

    def __init__(self, max_metrics: int = 100):
        self.metrics_data: dict[str, MetricData] = {}
        self.ensemble_detector = EnsembleAnomalyDetector()
        self.max_metrics = max_metrics
        self.anomaly_history: deque = deque(maxlen=1000)
        self.lock = threading.RLock()

        # 自适应参数
        self.adaptive_thresholds = {}
        self.false_positive_rates = defaultdict(float)

        # 性能统计
        self.detection_count = 0
        self.anomaly_count = 0
        self.processing_times = deque(maxlen=100)

    def add_metric_value(self, metric_name: str, value: float, timestamp: float = None):
        """添加指标值"""
        with self.lock:
            if metric_name not in self.metrics_data:
                if len(self.metrics_data) >= self.max_metrics:
                    # 移除最旧的指标
                    oldest_metric = min(self.metrics_data.keys())
                    del self.metrics_data[oldest_metric]

                self.metrics_data[metric_name] = MetricData(
                    name=metric_name, values=deque(), timestamps=deque()
                )

            self.metrics_data[metric_name].add_value(value, timestamp)

    async def detect_anomalies(self, metric_name: str = None) -> list[AnomalyResult]:
        """检测异常"""
        start_time = time.time()
        results = []

        try:
            with self.lock:
                metrics_to_check = (
                    [metric_name] if metric_name else list(self.metrics_data.keys())
                )

                for name in metrics_to_check:
                    if name in self.metrics_data:
                        data = self.metrics_data[name]

                        # 执行检测
                        result = self.ensemble_detector.get_consensus_result(data)

                        if result:
                            # 应用自适应阈值
                            result = self._apply_adaptive_threshold(result)

                            if result.is_anomaly:
                                # 添加根因分析
                                result.root_cause = self._analyze_root_cause(
                                    result, data
                                )

                                results.append(result)
                                self.anomaly_history.append(result)
                                self.anomaly_count += 1

                        self.detection_count += 1

            # 记录处理时间
            processing_time = time.time() - start_time
            self.processing_times.append(processing_time)

        except Exception as e:
            logger.error(f"异常检测失败: {e}")

        return results

    def _apply_adaptive_threshold(self, result: AnomalyResult) -> AnomalyResult:
        """应用自适应阈值"""
        metric_name = result.metric_name

        # 获取历史误报率
        false_positive_rate = self.false_positive_rates.get(metric_name, 0.1)

        # 根据误报率调整置信度阈值
        if false_positive_rate > 0.3:  # 误报率过高
            result.confidence *= 0.8  # 降低置信度
        elif false_positive_rate < 0.05:  # 误报率很低
            result.confidence *= 1.2  # 提高置信度

        result.confidence = min(result.confidence, 1.0)

        # 更新是否为异常的判断
        confidence_threshold = 0.7 if false_positive_rate > 0.2 else 0.5
        result.is_anomaly = result.confidence >= confidence_threshold

        return result

    def _analyze_root_cause(self, result: AnomalyResult, data: MetricData) -> str:
        """分析根因"""
        try:
            # 简单的根因分析
            if result.anomaly_type == AnomalyType.TREND_ANOMALY:
                trend_direction = result.context.get("trend_direction", "unknown")
                return f"检测到{trend_direction}趋势异常，可能原因：负载变化、资源泄漏或系统配置变更"

            elif result.anomaly_type == AnomalyType.SEASONAL_ANOMALY:
                return "检测到季节性模式异常，可能原因：业务模式变化、定时任务异常或外部依赖问题"

            elif result.anomaly_type == AnomalyType.POINT_ANOMALY:
                if result.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]:
                    return "检测到突发异常峰值，可能原因：系统故障、攻击或配置错误"
                else:
                    return "检测到轻微异常，可能原因：正常波动或临时负载变化"

            elif result.anomaly_type == AnomalyType.CONTEXTUAL_ANOMALY:
                return "检测到上下文异常，可能原因：系统行为模式变化或多指标关联异常"

            else:
                return "异常原因需要进一步分析"

        except Exception as e:
            logger.error(f"根因分析失败: {e}")
            return "根因分析失败"

    def update_false_positive_feedback(self, metric_name: str, is_false_positive: bool):
        """更新误报反馈"""
        current_rate = self.false_positive_rates.get(metric_name, 0.1)

        # 使用指数移动平均更新误报率
        alpha = 0.1
        if is_false_positive:
            new_rate = current_rate * (1 - alpha) + alpha
        else:
            new_rate = current_rate * (1 - alpha)

        self.false_positive_rates[metric_name] = max(0.01, min(0.5, new_rate))

    def get_anomaly_summary(self) -> dict[str, Any]:
        """获取异常摘要"""
        recent_anomalies = [
            a for a in self.anomaly_history if time.time() - a.timestamp < 3600
        ]  # 最近1小时

        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for anomaly in recent_anomalies:
            severity_counts[anomaly.severity.value] += 1
            type_counts[anomaly.anomaly_type.value] += 1

        avg_processing_time = (
            np.mean(self.processing_times) if self.processing_times else 0
        )

        return {
            "total_detections": self.detection_count,
            "total_anomalies": self.anomaly_count,
            "anomaly_rate": (self.anomaly_count / max(self.detection_count, 1)) * 100,
            "recent_anomalies": len(recent_anomalies),
            "severity_distribution": dict(severity_counts),
            "type_distribution": dict(type_counts),
            "avg_processing_time": round(avg_processing_time, 4),
            "monitored_metrics": len(self.metrics_data),
            "false_positive_rates": dict(self.false_positive_rates),
        }

    def get_metric_health_score(self, metric_name: str) -> float:
        """获取指标健康分数"""
        if metric_name not in self.metrics_data:
            return 1.0

        # 计算最近异常的影响
        recent_anomalies = [
            a
            for a in self.anomaly_history
            if a.metric_name == metric_name
            and time.time() - a.timestamp < 1800  # 最近30分钟
        ]

        if not recent_anomalies:
            return 1.0

        # 根据异常严重程度和数量计算健康分数
        severity_weights = {
            AnomalySeverity.LOW: 0.1,
            AnomalySeverity.MEDIUM: 0.3,
            AnomalySeverity.HIGH: 0.6,
            AnomalySeverity.CRITICAL: 1.0,
        }

        total_impact = sum(
            severity_weights.get(a.severity, 0.5) for a in recent_anomalies
        )
        health_score = max(
            0.0, 1.0 - (total_impact / 10.0)
        )  # 最多10个严重异常会使分数降到0

        return round(health_score, 2)


# 全局高级异常管理器
advanced_ml_anomaly_manager = AdvancedMLAnomalyManager()


async def demo_advanced_ml_anomaly() -> None:
    """演示高级机器学习异常检测"""
    print("🚀 高级机器学习异常检测演示")

    # 模拟数据生成
    import random

    print("\n📊 生成模拟数据...")

    # 正常数据
    for i in range(100):
        timestamp = time.time() - (100 - i) * 60  # 过去100分钟的数据

        # CPU使用率 - 正常波动
        cpu_value = 30 + 10 * np.sin(i * 0.1) + random.gauss(0, 2)
        advanced_ml_anomaly_manager.add_metric_value(
            "cpu_percent", cpu_value, timestamp
        )

        # 内存使用率 - 缓慢增长趋势
        memory_value = 40 + i * 0.1 + random.gauss(0, 1)
        advanced_ml_anomaly_manager.add_metric_value(
            "memory_percent", memory_value, timestamp
        )

        # 响应时间 - 季节性模式
        response_time = 100 + 20 * np.sin(i * 0.2) + random.gauss(0, 5)
        advanced_ml_anomaly_manager.add_metric_value(
            "response_time", response_time, timestamp
        )

    # 添加异常数据
    print("🔥 注入异常数据...")

    # CPU突发异常
    advanced_ml_anomaly_manager.add_metric_value("cpu_percent", 95.0)

    # 内存异常趋势
    for i in range(5):
        memory_value = 50 + i * 10 + random.gauss(0, 1)
        advanced_ml_anomaly_manager.add_metric_value("memory_percent", memory_value)
        await asyncio.sleep(0.1)

    # 响应时间季节性异常
    advanced_ml_anomaly_manager.add_metric_value("response_time", 300.0)

    print("\n🔍 执行异常检测...")

    # 检测异常
    anomalies = await advanced_ml_anomaly_manager.detect_anomalies()

    print("\n📋 检测结果:")
    print(f"发现异常数量: {len(anomalies)}")

    for anomaly in anomalies:
        print("\n🚨 异常详情:")
        print(f"  指标: {anomaly.metric_name}")
        print(f"  类型: {anomaly.anomaly_type.value}")
        print(f"  严重程度: {anomaly.severity.value}")
        print(f"  置信度: {anomaly.confidence:.2f}")
        print(f"  当前值: {anomaly.value:.2f}")
        print(f"  期望范围: {anomaly.expected_range}")
        print(f"  偏差分数: {anomaly.deviation_score:.2f}")
        print(f"  根因: {anomaly.root_cause}")
        print(f"  检测方法: {anomaly.context.get('method', 'unknown')}")

    # 显示摘要统计
    summary = advanced_ml_anomaly_manager.get_anomaly_summary()
    print("\n📊 异常检测摘要:")
    print(f"总检测次数: {summary['total_detections']}")
    print(f"总异常数量: {summary['total_anomalies']}")
    print(f"异常率: {summary['anomaly_rate']:.1f}%")
    print(f"平均处理时间: {summary['avg_processing_time']:.4f}s")
    print(f"监控指标数: {summary['monitored_metrics']}")

    # 显示指标健康分数
    print("\n💚 指标健康分数:")
    for metric in ["cpu_percent", "memory_percent", "response_time"]:
        score = advanced_ml_anomaly_manager.get_metric_health_score(metric)
        status = "健康" if score > 0.8 else "警告" if score > 0.5 else "异常"
        print(f"  {metric}: {score:.2f} ({status})")

    return {
        "anomalies_detected": len(anomalies),
        "summary": summary,
        "health_scores": {
            metric: advanced_ml_anomaly_manager.get_metric_health_score(metric)
            for metric in ["cpu_percent", "memory_percent", "response_time"]
        },
    }


if __name__ == "__main__":
    asyncio.run(demo_advanced_ml_anomaly())
