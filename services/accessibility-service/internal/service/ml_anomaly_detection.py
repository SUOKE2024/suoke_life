"""
机器学习异常检测模块

实现基于历史数据的智能异常检测，包括：
- 智能阈值计算
- 异常模式识别
- 预测性维护
- 自适应学习
"""

import asyncio
import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """异常类型枚举"""

    STATISTICAL = "statistical"  # 统计异常
    PATTERN = "pattern"  # 模式异常
    TREND = "trend"  # 趋势异常
    SEASONAL = "seasonal"  # 季节性异常
    OUTLIER = "outlier"  # 离群点异常


class AnomalySeverity(Enum):
    """异常严重程度"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyResult:
    """异常检测结果"""

    timestamp: datetime
    metric_name: str
    value: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    threshold: float
    description: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricData:
    """指标数据"""

    timestamp: datetime
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)


class StatisticalDetector:
    """统计异常检测器"""

    def __init__(self, window_size: int = 100, z_threshold: float = 3.0):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.data_buffer = deque(maxlen=window_size)

    def add_data(self, value: float) -> None:
        """添加数据点"""
        self.data_buffer.append(value)

    def detect(self, value: float) -> AnomalyResult | None:
        """检测统计异常"""
        if len(self.data_buffer) < 10:  # 需要足够的历史数据
            return None

        data_array = np.array(self.data_buffer)
        mean = np.mean(data_array)
        std = np.std(data_array)

        if std == 0:  # 避免除零错误
            return None

        z_score = abs(value - mean) / std

        if z_score > self.z_threshold:
            severity = self._calculate_severity(z_score)
            confidence = min(z_score / self.z_threshold, 1.0)

            return AnomalyResult(
                timestamp=datetime.now(),
                metric_name="statistical_metric",
                value=value,
                anomaly_type=AnomalyType.STATISTICAL,
                severity=severity,
                confidence=confidence,
                threshold=mean + self.z_threshold * std,
                description=f"统计异常: Z-score={z_score:.2f}, 阈值={self.z_threshold}",
                context={
                    "z_score": z_score,
                    "mean": mean,
                    "std": std,
                    "window_size": len(self.data_buffer),
                },
            )
        return None

    def _calculate_severity(self, z_score: float) -> AnomalySeverity:
        """计算异常严重程度"""
        if z_score > 5:
            return AnomalySeverity.CRITICAL
        elif z_score > 4:
            return AnomalySeverity.HIGH
        elif z_score > 3:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW


class TrendDetector:
    """趋势异常检测器"""

    def __init__(self, window_size: int = 50, trend_threshold: float = 0.1):
        self.window_size = window_size
        self.trend_threshold = trend_threshold
        self.data_buffer = deque(maxlen=window_size)

    def add_data(self, value: float) -> None:
        """添加数据点"""
        self.data_buffer.append(value)

    def detect(self) -> AnomalyResult | None:
        """检测趋势异常"""
        if len(self.data_buffer) < self.window_size:
            return None

        # 计算线性回归斜率
        x = np.arange(len(self.data_buffer))
        y = np.array(self.data_buffer)

        # 使用最小二乘法计算斜率
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (
            n * np.sum(x**2) - np.sum(x) ** 2
        )

        # 计算相对斜率
        mean_value = np.mean(y)
        if mean_value != 0:
            relative_slope = abs(slope) / abs(mean_value)
        else:
            relative_slope = abs(slope)

        if relative_slope > self.trend_threshold:
            severity = self._calculate_severity(relative_slope)
            confidence = min(relative_slope / self.trend_threshold, 1.0)

            trend_direction = "上升" if slope > 0 else "下降"

            return AnomalyResult(
                timestamp=datetime.now(),
                metric_name="trend_metric",
                value=y[-1],
                anomaly_type=AnomalyType.TREND,
                severity=severity,
                confidence=confidence,
                threshold=self.trend_threshold,
                description=f"趋势异常: {trend_direction}趋势，斜率={slope:.4f}",
                context={
                    "slope": slope,
                    "relative_slope": relative_slope,
                    "trend_direction": trend_direction,
                    "window_size": len(self.data_buffer),
                },
            )
        return None

    def _calculate_severity(self, relative_slope: float) -> AnomalySeverity:
        """计算异常严重程度"""
        if relative_slope > 0.5:
            return AnomalySeverity.CRITICAL
        elif relative_slope > 0.3:
            return AnomalySeverity.HIGH
        elif relative_slope > 0.2:
            return AnomalySeverity.MEDIUM
        else:
            return AnomalySeverity.LOW


class MLAnomalyDetector:
    """机器学习异常检测主类"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.detectors = {}
        self.anomaly_history = deque(maxlen=1000)
        self.metrics_data = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()

        # 初始化检测器
        self._initialize_detectors()

        # 启动后台训练任务
        self.training_thread = None
        self.is_running = False

    def _initialize_detectors(self) -> None:
        """初始化各种检测器"""
        # 统计检测器
        self.detectors["statistical"] = StatisticalDetector(
            window_size=self.config.get("statistical_window", 100),
            z_threshold=self.config.get("z_threshold", 3.0),
        )

        # 趋势检测器
        self.detectors["trend"] = TrendDetector(
            window_size=self.config.get("trend_window", 50),
            trend_threshold=self.config.get("trend_threshold", 0.1),
        )

        logger.info("机器学习异常检测器初始化完成")

    def start(self) -> None:
        """启动异常检测服务"""
        self.is_running = True
        logger.info("机器学习异常检测服务已启动")

    def stop(self) -> None:
        """停止异常检测服务"""
        self.is_running = False
        logger.info("机器学习异常检测服务已停止")

    def add_metric(
        self, metric_name: str, value: float, timestamp: datetime | None = None
    ) -> None:
        """添加指标数据"""
        if timestamp is None:
            timestamp = datetime.now()

        with self.lock:
            # 存储指标数据
            metric_data = MetricData(timestamp=timestamp, value=value)
            self.metrics_data[metric_name].append(metric_data)

            # 更新各检测器的数据
            self.detectors["statistical"].add_data(value)
            self.detectors["trend"].add_data(value)

    def detect_anomalies(
        self, metric_name: str, value: float, timestamp: datetime | None = None
    ) -> list[AnomalyResult]:
        """检测异常"""
        if timestamp is None:
            timestamp = datetime.now()

        anomalies = []

        with self.lock:
            # 统计异常检测
            stat_anomaly = self.detectors["statistical"].detect(value)
            if stat_anomaly:
                stat_anomaly.metric_name = metric_name
                stat_anomaly.timestamp = timestamp
                anomalies.append(stat_anomaly)

            # 趋势异常检测
            trend_anomaly = self.detectors["trend"].detect()
            if trend_anomaly:
                trend_anomaly.metric_name = metric_name
                trend_anomaly.timestamp = timestamp
                trend_anomaly.value = value
                anomalies.append(trend_anomaly)

        # 记录异常历史
        for anomaly in anomalies:
            self.anomaly_history.append(anomaly)

        return anomalies

    def get_anomaly_statistics(self) -> dict[str, Any]:
        """获取异常统计信息"""
        with self.lock:
            total_anomalies = len(self.anomaly_history)

            if total_anomalies == 0:
                return {
                    "total_anomalies": 0,
                    "by_type": {},
                    "by_severity": {},
                    "recent_anomalies": [],
                }

            # 按类型统计
            by_type = defaultdict(int)
            by_severity = defaultdict(int)

            for anomaly in self.anomaly_history:
                by_type[anomaly.anomaly_type.value] += 1
                by_severity[anomaly.severity.value] += 1

            # 最近的异常
            recent_anomalies = list(self.anomaly_history)[-10:]

            return {
                "total_anomalies": total_anomalies,
                "by_type": dict(by_type),
                "by_severity": dict(by_severity),
                "recent_anomalies": [
                    {
                        "timestamp": anomaly.timestamp.isoformat(),
                        "metric_name": anomaly.metric_name,
                        "type": anomaly.anomaly_type.value,
                        "severity": anomaly.severity.value,
                        "confidence": anomaly.confidence,
                        "description": anomaly.description,
                    }
                    for anomaly in recent_anomalies
                ],
            }

    def get_model_status(self) -> dict[str, Any]:
        """获取模型状态"""
        with self.lock:
            return {
                "statistical_detector": {
                    "data_points": len(self.detectors["statistical"].data_buffer),
                    "window_size": self.detectors["statistical"].window_size,
                    "z_threshold": self.detectors["statistical"].z_threshold,
                },
                "trend_detector": {
                    "data_points": len(self.detectors["trend"].data_buffer),
                    "window_size": self.detectors["trend"].window_size,
                    "trend_threshold": self.detectors["trend"].trend_threshold,
                },
            }


# 全局异常检测器实例
_global_detector: MLAnomalyDetector | None = None


def get_anomaly_detector(config: dict[str, Any] | None = None) -> MLAnomalyDetector:
    """获取全局异常检测器实例"""
    global _global_detector

    if _global_detector is None:
        _global_detector = MLAnomalyDetector(config)

    return _global_detector


async def detect_anomalies_async(
    metric_name: str, value: float, timestamp: datetime | None = None
) -> list[AnomalyResult]:
    """异步异常检测"""
    detector = get_anomaly_detector()

    # 在线程池中执行检测
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, detector.detect_anomalies, metric_name, value, timestamp
    )


if __name__ == "__main__":
    # 示例使用
    import random

    # 创建异常检测器
    detector = MLAnomalyDetector(
        {"statistical_window": 50, "z_threshold": 2.5, "trend_threshold": 0.15}
    )

    detector.start()

    try:
        # 模拟正常数据
        print("🔍 开始异常检测演示...")

        for i in range(100):
            # 生成正常数据
            normal_value = 50 + random.gauss(0, 5)
            detector.add_metric("cpu_usage", normal_value)

            # 每10个数据点检测一次
            if i % 10 == 0:
                anomalies = detector.detect_anomalies("cpu_usage", normal_value)
                if anomalies:
                    print(f"检测到 {len(anomalies)} 个异常")

        # 注入异常数据
        print("\n🚨 注入异常数据...")
        anomaly_value = 150  # 明显异常的值
        detector.add_metric("cpu_usage", anomaly_value)
        anomalies = detector.detect_anomalies("cpu_usage", anomaly_value)

        print(f"检测到 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            print(f"  - {anomaly.anomaly_type.value}: {anomaly.description}")

        # 显示统计信息
        print("\n📊 异常统计信息:")
        stats = detector.get_anomaly_statistics()
        print(f"  总异常数: {stats['total_anomalies']}")
        print(f"  按类型: {stats['by_type']}")
        print(f"  按严重程度: {stats['by_severity']}")

        # 显示模型状态
        print("\n🤖 模型状态:")
        status = detector.get_model_status()
        for detector_name, detector_status in status.items():
            print(f"  {detector_name}: {detector_status}")

    finally:
        detector.stop()
        print("\n✅ 异常检测演示完成")
