"""
容量规划和预测模块

实现基于历史数据的容量预测，包括：
- 资源使用趋势分析
- 容量预测算法
- 扩容建议生成
- 成本优化分析
"""

import logging
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """资源类型枚举"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class PredictionModel(Enum):
    """预测模型枚举"""

    LINEAR = "linear"
    MOVING_AVERAGE = "moving_average"


class ScalingDirection(Enum):
    """扩容方向枚举"""

    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MAINTAIN = "maintain"


@dataclass
class ResourceMetric:
    """资源指标"""

    timestamp: datetime
    resource_type: ResourceType
    value: float
    unit: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionResult:
    """预测结果"""

    resource_type: ResourceType
    model_type: PredictionModel
    predicted_value: float
    confidence: float
    prediction_time: datetime
    target_time: datetime
    trend: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class CapacityRecommendation:
    """容量建议"""

    resource_type: ResourceType
    current_capacity: float
    predicted_demand: float
    recommended_capacity: float
    scaling_direction: ScalingDirection
    urgency: str
    cost_impact: float
    timeline: str
    reasoning: str
    context: dict[str, Any] = field(default_factory=dict)


class LinearPredictor:
    """线性预测器"""

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_buffer = deque(maxlen=window_size)

    def add_data(self, timestamp: datetime, value: float) -> None:
        """添加数据点"""
        self.data_buffer.append((timestamp, value))

    def predict(self, target_time: datetime) -> PredictionResult | None:
        """线性预测"""
        if len(self.data_buffer) < 10:
            return None

        # 转换时间戳为数值
        base_time = self.data_buffer[0][0]
        x_data = []
        y_data = []

        for timestamp, value in self.data_buffer:
            x = (timestamp - base_time).total_seconds()
            x_data.append(x)
            y_data.append(value)

        x_array = np.array(x_data)
        y_array = np.array(y_data)

        # 线性回归
        n = len(x_array)
        slope = (n * np.sum(x_array * y_array) - np.sum(x_array) * np.sum(y_array)) / (
            n * np.sum(x_array**2) - np.sum(x_array) ** 2
        )
        intercept = (np.sum(y_array) - slope * np.sum(x_array)) / n

        # 预测目标时间的值
        target_x = (target_time - base_time).total_seconds()
        predicted_value = slope * target_x + intercept

        # 计算置信度
        y_pred = slope * x_array + intercept
        ss_res = np.sum((y_array - y_pred) ** 2)
        ss_tot = np.sum((y_array - np.mean(y_array)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0, min(1, r_squared))

        # 判断趋势
        if slope > 0.01:
            trend = "increasing"
        elif slope < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"

        return PredictionResult(
            resource_type=ResourceType.CPU,
            model_type=PredictionModel.LINEAR,
            predicted_value=max(0, predicted_value),
            confidence=confidence,
            prediction_time=datetime.now(),
            target_time=target_time,
            trend=trend,
            context={
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
                "data_points": len(self.data_buffer),
            },
        )


class CapacityPlanner:
    """容量规划器"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.predictors = {}
        self.resource_data = defaultdict(lambda: deque(maxlen=1000))
        self.capacity_limits = {}
        self.lock = threading.Lock()

        # 初始化预测器
        self._initialize_predictors()

        # 设置默认容量限制
        self._initialize_capacity_limits()

    def _initialize_predictors(self) -> None:
        """初始化预测器"""
        for resource_type in ResourceType:
            self.predictors[resource_type] = {
                PredictionModel.LINEAR: LinearPredictor(
                    window_size=self.config.get("linear_window", 100)
                )
            }

    def _initialize_capacity_limits(self) -> None:
        """初始化容量限制"""
        self.capacity_limits = {
            ResourceType.CPU: {"max": 100, "warning": 80, "critical": 95},
            ResourceType.MEMORY: {"max": 100, "warning": 80, "critical": 95},
            ResourceType.DISK: {"max": 100, "warning": 85, "critical": 95},
            ResourceType.NETWORK: {"max": 1000, "warning": 800, "critical": 950},
        }

    def add_metric(self, metric: ResourceMetric) -> None:
        """添加资源指标"""
        with self.lock:
            self.resource_data[metric.resource_type].append(metric)

            # 更新预测器
            for predictor in self.predictors[metric.resource_type].values():
                predictor.add_data(metric.timestamp, metric.value)

    def predict_resource_usage(
        self, resource_type: ResourceType, target_time: datetime
    ) -> list[PredictionResult]:
        """预测资源使用情况"""
        results = []

        with self.lock:
            for pred_model, predictor in self.predictors[resource_type].items():
                result = predictor.predict(target_time)
                if result:
                    result.resource_type = resource_type
                    results.append(result)

        return results

    def generate_capacity_recommendations(
        self, time_horizon: timedelta = timedelta(days=30)
    ) -> list[CapacityRecommendation]:
        """生成容量建议"""
        recommendations = []
        target_time = datetime.now() + time_horizon

        for resource_type in ResourceType:
            # 获取预测结果
            predictions = self.predict_resource_usage(resource_type, target_time)

            if not predictions:
                continue

            # 选择最可信的预测
            best_prediction = max(predictions, key=lambda p: p.confidence)

            # 获取当前容量
            current_capacity = self.capacity_limits[resource_type]["max"]
            predicted_demand = best_prediction.predicted_value

            # 生成建议
            recommendation = self._generate_recommendation(
                resource_type, current_capacity, predicted_demand, best_prediction
            )

            if recommendation:
                recommendations.append(recommendation)

        return recommendations

    def _generate_recommendation(
        self,
        resource_type: ResourceType,
        current_capacity: float,
        predicted_demand: float,
        prediction: PredictionResult,
    ) -> CapacityRecommendation | None:
        """生成单个资源的容量建议"""
        limits = self.capacity_limits[resource_type]
        warning_threshold = limits["warning"]
        critical_threshold = limits["critical"]

        # 计算使用率
        usage_rate = predicted_demand / current_capacity if current_capacity > 0 else 0

        # 确定扩容方向和建议容量
        if usage_rate > critical_threshold / 100:
            scaling_direction = ScalingDirection.SCALE_UP
            recommended_capacity = predicted_demand * 1.3
            urgency = "critical"
            timeline = "立即"
        elif usage_rate > warning_threshold / 100:
            scaling_direction = ScalingDirection.SCALE_UP
            recommended_capacity = predicted_demand * 1.2
            urgency = "high"
            timeline = "1-2周内"
        elif usage_rate < 0.5:
            scaling_direction = ScalingDirection.SCALE_DOWN
            recommended_capacity = predicted_demand * 1.5
            urgency = "low"
            timeline = "1-3个月内"
        else:
            scaling_direction = ScalingDirection.MAINTAIN
            recommended_capacity = current_capacity
            urgency = "low"
            timeline = "无需调整"

        # 计算成本影响
        capacity_change = recommended_capacity - current_capacity
        cost_impact = capacity_change * 0.1

        # 生成推理说明
        reasoning = self._generate_reasoning(
            resource_type, usage_rate, prediction, scaling_direction
        )

        return CapacityRecommendation(
            resource_type=resource_type,
            current_capacity=current_capacity,
            predicted_demand=predicted_demand,
            recommended_capacity=recommended_capacity,
            scaling_direction=scaling_direction,
            urgency=urgency,
            cost_impact=cost_impact,
            timeline=timeline,
            reasoning=reasoning,
            context={
                "usage_rate": usage_rate,
                "prediction_confidence": prediction.confidence,
                "trend": prediction.trend,
                "model_type": prediction.model_type.value,
            },
        )

    def _generate_reasoning(
        self,
        resource_type: ResourceType,
        usage_rate: float,
        prediction: PredictionResult,
        scaling_direction: ScalingDirection,
    ) -> str:
        """生成推理说明"""
        resource_name = resource_type.value.upper()
        trend_desc = {"increasing": "上升", "decreasing": "下降", "stable": "稳定"}.get(
            prediction.trend, "未知"
        )

        confidence_desc = (
            "高"
            if prediction.confidence > 0.8
            else "中" if prediction.confidence > 0.5 else "低"
        )

        if scaling_direction == ScalingDirection.SCALE_UP:
            return (
                f"{resource_name}使用率预计达到{usage_rate:.1%}，呈{trend_desc}趋势。"
                f"基于{prediction.model_type.value}模型预测（置信度：{confidence_desc}），"
                f"建议扩容以避免性能瓶颈。"
            )
        elif scaling_direction == ScalingDirection.SCALE_DOWN:
            return (
                f"{resource_name}使用率预计仅为{usage_rate:.1%}，呈{trend_desc}趋势。"
                f"基于{prediction.model_type.value}模型预测（置信度：{confidence_desc}），"
                f"可考虑缩容以优化成本。"
            )
        else:
            return (
                f"{resource_name}使用率预计为{usage_rate:.1%}，呈{trend_desc}趋势。"
                f"基于{prediction.model_type.value}模型预测（置信度：{confidence_desc}），"
                f"当前容量配置合理。"
            )

    def get_capacity_status(self) -> dict[str, Any]:
        """获取容量状态"""
        with self.lock:
            status = {}

            for resource_type in ResourceType:
                resource_data = list(self.resource_data[resource_type])

                if not resource_data:
                    status[resource_type.value] = {
                        "current_usage": 0,
                        "data_points": 0,
                        "last_update": None,
                    }
                    continue

                # 获取最新数据
                latest_metric = resource_data[-1]
                current_usage = latest_metric.value

                status[resource_type.value] = {
                    "current_usage": current_usage,
                    "data_points": len(resource_data),
                    "last_update": latest_metric.timestamp.isoformat(),
                }

            return status


# 全局容量规划器实例
_global_capacity_planner: CapacityPlanner | None = None


def get_capacity_planner(config: dict[str, Any] | None = None) -> CapacityPlanner:
    """获取全局容量规划器实例"""
    global _global_capacity_planner

    if _global_capacity_planner is None:
        _global_capacity_planner = CapacityPlanner(config)

    return _global_capacity_planner


if __name__ == "__main__":
    # 示例使用
    import random

    # 创建容量规划器
    planner = CapacityPlanner({"linear_window": 50})

    print("📊 容量规划系统演示...")

    # 模拟历史数据
    base_time = datetime.now() - timedelta(days=7)

    for i in range(168):  # 一周的小时数据
        timestamp = base_time + timedelta(hours=i)

        # 模拟CPU使用率
        cpu_usage = 30 + random.gauss(0, 5) + i * 0.1
        cpu_usage = max(0, min(100, cpu_usage))

        # 添加指标
        planner.add_metric(
            ResourceMetric(
                timestamp=timestamp,
                resource_type=ResourceType.CPU,
                value=cpu_usage,
                unit="percent",
            )
        )

    print("✅ 历史数据加载完成")

    # 预测未来一周的资源使用
    future_time = datetime.now() + timedelta(days=7)

    print(f"\n🔮 预测 {future_time.strftime('%Y-%m-%d %H:%M')} 的资源使用:")

    predictions = planner.predict_resource_usage(ResourceType.CPU, future_time)

    for pred in predictions:
        print(
            f"  {pred.model_type.value}: {pred.predicted_value:.1f}% "
            f"(置信度: {pred.confidence:.2f}, 趋势: {pred.trend})"
        )

    # 生成容量建议
    print("\n💡 容量规划建议:")
    recommendations = planner.generate_capacity_recommendations(timedelta(days=30))

    for rec in recommendations:
        print(f"\n{rec.resource_type.value.upper()}:")
        print(f"  当前容量: {rec.current_capacity}")
        print(f"  预测需求: {rec.predicted_demand:.1f}")
        print(f"  建议容量: {rec.recommended_capacity:.1f}")
        print(f"  扩容方向: {rec.scaling_direction.value}")
        print(f"  紧急程度: {rec.urgency}")
        print(f"  时间线: {rec.timeline}")
        print(f"  推理: {rec.reasoning}")

    print("\n✅ 容量规划演示完成")
