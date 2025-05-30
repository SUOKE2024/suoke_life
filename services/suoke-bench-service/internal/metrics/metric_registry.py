"""
指标注册表

用于管理评测指标的中央注册表。
"""

import logging
from collections.abc import Callable
from typing import Any

from .agent_metrics import AgentCollaborationMetric
from .edge_metrics import EdgePerformanceMetric
from .metrics import BaseMetric
from .privacy_metrics import PrivacyVerificationMetric
from .tcm_metrics import (
    ConstitutionClassificationMetric,
    FaceRecognitionMetric,
    PulseRecognitionMetric,
    TongueRecognitionMetric,
)

logger = logging.getLogger(__name__)

# 指标计算函数类型
MetricFunction = Callable[[Any, Any, dict[str, Any] | None], float]


class MetricInfo:
    """指标信息"""

    def __init__(
        self,
        name: str,
        display_name: str,
        description: str,
        func: MetricFunction,
        higher_is_better: bool = True,
        min_value: float = 0.0,
        max_value: float = 1.0,
        threshold: float = 0.5,
        unit: str = "",
        tags: list[str] | None = None,
    ):
        """
        初始化指标信息

        Args:
            name: 指标名称
            display_name: 显示名称
            description: 描述
            func: 计算函数
            higher_is_better: 更高值是否更好
            min_value: 最小值
            max_value: 最大值
            threshold: 合格阈值
            unit: 单位
            tags: 标签列表
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        self.func = func
        self.higher_is_better = higher_is_better
        self.min_value = min_value
        self.max_value = max_value
        self.threshold = threshold
        self.unit = unit
        self.tags = tags or []

    def compute(
        self, predictions: Any, targets: Any, params: dict[str, Any] | None = None
    ) -> float:
        """
        计算指标值

        Args:
            predictions: 预测值
            targets: 目标值
            params: 计算参数

        Returns:
            指标值
        """
        params = params or {}
        try:
            return self.func(predictions, targets, params)
        except Exception as e:
            logger.error(f"计算指标 {self.name} 失败: {str(e)}")
            return float("nan")

    def is_pass(self, value: float) -> bool:
        """
        判断指标值是否合格

        Args:
            value: 指标值

        Returns:
            是否合格
        """
        if self.higher_is_better:
            return value >= self.threshold
        else:
            return value <= self.threshold

    def to_dict(self) -> dict[str, Any]:
        """
        转换为字典

        Returns:
            指标信息字典
        """
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "higher_is_better": self.higher_is_better,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "threshold": self.threshold,
            "unit": self.unit,
            "tags": self.tags,
        }


class MetricRegistry:
    """指标注册表"""

    def __init__(self):
        """初始化指标注册表"""
        self._metrics: dict[str, type[BaseMetric]] = {}
        self._register_default_metrics()

    def _register_default_metrics(self):
        """注册默认指标。"""

        # 中医五诊指标
        self.register("tongue_recognition", TongueRecognitionMetric)
        self.register("face_recognition", FaceRecognitionMetric)
        self.register("pulse_recognition", PulseRecognitionMetric)
        self.register("constitution_classification", ConstitutionClassificationMetric)

        # 智能体协作指标
        self.register("agent_collaboration", AgentCollaborationMetric)

        # 隐私安全指标
        self.register("privacy_verification", PrivacyVerificationMetric)

        # 端侧性能指标
        self.register("edge_performance", EdgePerformanceMetric)

    def register(self, name: str, metric_class: type[BaseMetric]):
        """注册新的指标。"""
        if name in self._metrics:
            raise ValueError(f"指标 '{name}' 已经注册")

        self._metrics[name] = metric_class

    def unregister(self, name: str):
        """取消注册指标。"""
        if name not in self._metrics:
            raise ValueError(f"指标 '{name}' 未注册")

        del self._metrics[name]

    def get_metric(self, name: str, **kwargs) -> BaseMetric:
        """获取指标实例。"""
        if name not in self._metrics:
            raise ValueError(f"指标 '{name}' 未注册")

        return self._metrics[name](**kwargs)

    def list_metrics(self) -> dict[str, type[BaseMetric]]:
        """列出所有注册的指标。"""
        return self._metrics.copy()

    def has_metric(self, name: str) -> bool:
        """检查指标是否已注册。"""
        return name in self._metrics

    def compute_metric(
        self,
        name: str,
        predictions: Any,
        targets: Any,
        params: dict[str, Any] | None = None,
    ) -> float:
        """
        计算指标值

        Args:
            name: 指标名称
            predictions: 预测值
            targets: 目标值
            params: 计算参数

        Returns:
            指标值
        """
        metric = self.get_metric(name)
        return metric.compute(predictions, targets, params)

    def compute_metrics(
        self,
        metric_names: list[str],
        predictions: Any,
        targets: Any,
        params: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """
        计算多个指标值

        Args:
            metric_names: 指标名称列表
            predictions: 预测值
            targets: 目标值
            params: 计算参数

        Returns:
            指标值字典
        """
        results = {}
        for name in metric_names:
            results[name] = self.compute_metric(name, predictions, targets, params)
        return results

    def get_metrics_by_tags(self, tags: list[str]) -> list[BaseMetric]:
        """
        通过标签获取指标

        Args:
            tags: 标签列表

        Returns:
            符合条件的指标列表
        """
        result = []
        for metric in self._metrics.values():
            if any(tag in metric.tags for tag in tags):
                result.append(metric)
        return result


# 全局指标注册表实例
metric_registry = MetricRegistry()
