"""
评测指标实现
"""

import logging
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, f1_score

logger = logging.getLogger(__name__)


class Metric:
    """指标基类"""

    def __init__(
        self,
        name: str,
        threshold: float = 0.0,
        unit: str = "",
        higher_is_better: bool = True,
    ):
        """
        初始化指标

        Args:
            name: 指标名称
            threshold: 阈值
            unit: 单位
            higher_is_better: 是否越高越好
        """
        self.name = name
        self.threshold = threshold
        self.unit = unit
        self.higher_is_better = higher_is_better

    def compute(self, predictions: list[Any], references: list[Any]) -> float:
        """
        计算指标值

        Args:
            predictions: 预测值列表
            references: 参考值列表

        Returns:
            指标值
        """
        raise NotImplementedError("子类必须实现compute方法")

    def is_pass(self, value: float) -> bool:
        """
        判断指标值是否通过阈值

        Args:
            value: 指标值

        Returns:
            是否通过
        """
        if self.higher_is_better:
            return value >= self.threshold
        else:
            return value <= self.threshold


class AccuracyMetric(Metric):
    """准确率指标"""

    def __init__(self, threshold: float = 0.8, unit: str = "%"):
        """
        初始化准确率指标

        Args:
            threshold: 阈值
            unit: 单位
        """
        super().__init__("accuracy", threshold, unit, higher_is_better=True)

    def compute(self, predictions: list[Any], references: list[Any]) -> float:
        """
        计算准确率

        Args:
            predictions: 预测值列表
            references: 参考值列表

        Returns:
            准确率
        """
        if len(predictions) != len(references):
            logger.warning(
                f"预测值与参考值数量不一致: {len(predictions)} vs {len(references)}"
            )
            return 0.0

        if not predictions:
            logger.warning("空预测值列表")
            return 0.0

        try:
            return accuracy_score(references, predictions)
        except Exception as e:
            logger.error(f"计算准确率出错: {str(e)}")
            return 0.0


class F1Metric(Metric):
    """F1分数指标"""

    def __init__(
        self, threshold: float = 0.75, unit: str = "", average: str = "weighted"
    ):
        """
        初始化F1分数指标

        Args:
            threshold: 阈值
            unit: 单位
            average: 平均方式
        """
        super().__init__("f1", threshold, unit, higher_is_better=True)
        self.average = average

    def compute(self, predictions: list[Any], references: list[Any]) -> float:
        """
        计算F1分数

        Args:
            predictions: 预测值列表
            references: 参考值列表

        Returns:
            F1分数
        """
        if len(predictions) != len(references):
            logger.warning(
                f"预测值与参考值数量不一致: {len(predictions)} vs {len(references)}"
            )
            return 0.0

        if not predictions:
            logger.warning("空预测值列表")
            return 0.0

        try:
            return f1_score(references, predictions, average=self.average)
        except Exception as e:
            logger.error(f"计算F1分数出错: {str(e)}")
            return 0.0


class AgreementRateMetric(Metric):
    """辨证一致率指标"""

    def __init__(self, threshold: float = 0.7, unit: str = "%"):
        """
        初始化辨证一致率指标

        Args:
            threshold: 阈值
            unit: 单位
        """
        super().__init__("agreement_rate", threshold, unit, higher_is_better=True)

    def compute(
        self, predictions: list[dict[str, Any]], expert_opinions: list[dict[str, Any]]
    ) -> float:
        """
        计算辨证一致率

        Args:
            predictions: 预测辨证结果列表
            expert_opinions: 专家辨证结果列表

        Returns:
            辨证一致率
        """
        if len(predictions) != len(expert_opinions):
            logger.warning(
                f"预测值与专家意见数量不一致: {len(predictions)} vs {len(expert_opinions)}"
            )
            return 0.0

        if not predictions:
            logger.warning("空预测值列表")
            return 0.0

        # 计算一致率
        agreement_count = 0
        total_count = len(predictions)

        for pred, expert in zip(predictions, expert_opinions, strict=False):
            # 判断主诊断是否一致
            if pred.get("primary_diagnosis") == expert.get("primary_diagnosis"):
                agreement_count += 1

        return agreement_count / total_count if total_count > 0 else 0.0


class ROUGEMetric(Metric):
    """ROUGE评分指标"""

    def __init__(
        self, threshold: float = 0.6, unit: str = "", rouge_type: str = "rouge-l"
    ):
        """
        初始化ROUGE评分指标

        Args:
            threshold: 阈值
            unit: 单位
            rouge_type: ROUGE类型
        """
        super().__init__(
            f"rouge_{rouge_type.split('-')[1]}", threshold, unit, higher_is_better=True
        )
        self.rouge_type = rouge_type

    def compute(self, predictions: list[str], references: list[str]) -> float:
        """
        计算ROUGE评分

        Args:
            predictions: 预测文本列表
            references: 参考文本列表

        Returns:
            ROUGE评分
        """
        if len(predictions) != len(references):
            logger.warning(
                f"预测值与参考值数量不一致: {len(predictions)} vs {len(references)}"
            )
            return 0.0

        if not predictions:
            logger.warning("空预测值列表")
            return 0.0

        try:
            # 简化版ROUGE-L计算
            scores = []
            for pred, ref in zip(predictions, references, strict=False):
                pred_tokens = pred.split()
                ref_tokens = ref.split()

                # 计算最长公共子序列
                lcs_length = self._lcs_length(pred_tokens, ref_tokens)

                # 计算精确率、召回率和F1
                precision = lcs_length / len(pred_tokens) if pred_tokens else 0
                recall = lcs_length / len(ref_tokens) if ref_tokens else 0

                if precision + recall > 0:
                    f1 = (2 * precision * recall) / (precision + recall)
                else:
                    f1 = 0

                scores.append(f1)

            return np.mean(scores) if scores else 0.0

        except Exception as e:
            logger.error(f"计算ROUGE评分出错: {str(e)}")
            return 0.0

    def _lcs_length(self, a: list[str], b: list[str]) -> int:
        """
        计算最长公共子序列长度

        Args:
            a: 序列A
            b: 序列B

        Returns:
            最长公共子序列长度
        """
        if not a or not b:
            return 0

        # 动态规划计算LCS
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if a[i - 1] == b[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]


class LatencyMetric(Metric):
    """延迟指标"""

    def __init__(
        self, threshold: float = 500.0, unit: str = "ms", percentile: int = 95
    ):
        """
        初始化延迟指标

        Args:
            threshold: 阈值
            unit: 单位
            percentile: 百分位数
        """
        super().__init__(
            f"latency_p{percentile}", threshold, unit, higher_is_better=False
        )
        self.percentile = percentile

    def compute(self, latencies: list[float]) -> float:
        """
        计算延迟

        Args:
            latencies: 延迟列表

        Returns:
            延迟值
        """
        if not latencies:
            logger.warning("空延迟列表")
            return 0.0

        try:
            return np.percentile(latencies, self.percentile)
        except Exception as e:
            logger.error(f"计算延迟出错: {str(e)}")
            return 0.0


class MemoryUsageMetric(Metric):
    """内存使用指标"""

    def __init__(self, threshold: float = 200.0, unit: str = "MB"):
        """
        初始化内存使用指标

        Args:
            threshold: 阈值
            unit: 单位
        """
        super().__init__("memory_usage", threshold, unit, higher_is_better=False)

    def compute(self, memory_usages: list[float]) -> float:
        """
        计算内存使用

        Args:
            memory_usages: 内存使用列表

        Returns:
            内存使用值
        """
        if not memory_usages:
            logger.warning("空内存使用列表")
            return 0.0

        try:
            return np.max(memory_usages)
        except Exception as e:
            logger.error(f"计算内存使用出错: {str(e)}")
            return 0.0


class TaskSuccessRateMetric(Metric):
    """任务成功率指标"""

    def __init__(self, threshold: float = 0.9, unit: str = "%"):
        """
        初始化任务成功率指标

        Args:
            threshold: 阈值
            unit: 单位
        """
        super().__init__("task_success_rate", threshold, unit, higher_is_better=True)

    def compute(self, task_results: list[dict[str, Any]]) -> float:
        """
        计算任务成功率

        Args:
            task_results: 任务结果列表

        Returns:
            任务成功率
        """
        if not task_results:
            logger.warning("空任务结果列表")
            return 0.0

        try:
            success_count = sum(1 for r in task_results if r.get("success", False))
            return success_count / len(task_results)
        except Exception as e:
            logger.error(f"计算任务成功率出错: {str(e)}")
            return 0.0


class MetricRegistry:
    """指标注册表"""

    def __init__(self):
        """初始化指标注册表"""
        self.metrics: dict[str, Metric] = {}

    def register(self, metric: Metric) -> None:
        """
        注册指标

        Args:
            metric: 指标实例
        """
        self.metrics[metric.name] = metric

    def get(self, name: str) -> Metric | None:
        """
        获取指标

        Args:
            name: 指标名称

        Returns:
            指标实例
        """
        return self.metrics.get(name)

    def compute(
        self, name: str, predictions: list[Any], references: list[Any]
    ) -> float | None:
        """
        计算指标值

        Args:
            name: 指标名称
            predictions: 预测值
            references: 参考值

        Returns:
            指标值
        """
        metric = self.get(name)
        if metric:
            return metric.compute(predictions, references)
        return None


# 全局指标注册表
METRIC_REGISTRY = MetricRegistry()

# 注册常用指标
METRIC_REGISTRY.register(AccuracyMetric())
METRIC_REGISTRY.register(F1Metric())
METRIC_REGISTRY.register(AgreementRateMetric())
METRIC_REGISTRY.register(ROUGEMetric())
METRIC_REGISTRY.register(LatencyMetric())
METRIC_REGISTRY.register(MemoryUsageMetric())
METRIC_REGISTRY.register(TaskSuccessRateMetric())
