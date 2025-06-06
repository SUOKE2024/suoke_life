"""
evaluator - 索克生活项目模块
"""

from internal.metrics.metrics import METRIC_REGISTRY
from typing import Any
import logging

"""
评估器实现
"""



logger = logging.getLogger(__name__)


class BaseEvaluator:
    """评估器基类"""

    def __init__(self, metrics: list[str], config: dict[str, Any] | None = None):
        """
        初始化评估器

        Args:
            metrics: 指标列表
            config: 配置
        """
        self.metrics = metrics
        self.config = config or {}

    def evaluate(
        self, predictions: list[Any], references: list[Any]
    ) -> dict[str, float]:
        """
        评估预测结果

        Args:
            predictions: 预测结果
            references: 参考结果

        Returns:
            评估结果
        """
        results = {}

        for metric_name in self.metrics:
            try:
                # 使用指标注册表计算指标
                metric_value = METRIC_REGISTRY.compute(
                    metric_name, predictions, references
                )

                if metric_value is not None:
                    results[metric_name] = metric_value
                else:
                    logger.warning(f"指标 {metric_name} 计算结果为空")
            except Exception as e:
                logger.error(f"计算指标 {metric_name} 出错: {str(e)}", exc_info=True)

        return results


class ClassificationEvaluator(BaseEvaluator):
    """分类评估器"""

    def __init__(self, metrics: list[str], config: dict[str, Any] | None = None):
        """
        初始化分类评估器

        Args:
            metrics: 指标列表
            config: 配置
        """
        super().__init__(metrics, config)

    def evaluate(
        self, predictions: list[Any], references: list[Any]
    ) -> dict[str, float]:
        """
        评估分类预测结果

        Args:
            predictions: 预测结果
            references: 参考结果

        Returns:
            评估结果
        """
        return super().evaluate(predictions, references)


class GenerationEvaluator(BaseEvaluator):
    """文本生成评估器"""

    def __init__(self, metrics: list[str], config: dict[str, Any] | None = None):
        """
        初始化文本生成评估器

        Args:
            metrics: 指标列表
            config: 配置
        """
        super().__init__(metrics, config)

    def evaluate(
        self, predictions: list[str], references: list[str]
    ) -> dict[str, float]:
        """
        评估文本生成预测结果

        Args:
            predictions: 预测文本
            references: 参考文本

        Returns:
            评估结果
        """
        return super().evaluate(predictions, references)


class TCMDiagnosisEvaluator(BaseEvaluator):
    """中医辨证评估器"""

    def __init__(self, metrics: list[str], config: dict[str, Any] | None = None):
        """
        初始化中医辨证评估器

        Args:
            metrics: 指标列表
            config: 配置
        """
        super().__init__(metrics, config)

    def evaluate(
        self, predictions: list[dict[str, Any]], expert_opinions: list[dict[str, Any]]
    ) -> dict[str, float]:
        """
        评估中医辨证预测结果

        Args:
            predictions: 预测辨证结果
            expert_opinions: 专家辨证结果

        Returns:
            评估结果
        """
        # 转换为适合评估的格式
        prepared_predictions = []
        prepared_references = []

        for pred, ref in zip(predictions, expert_opinions, strict=False):
            # 提取主要特征
            pred_primary = pred.get("primary_diagnosis", "")
            ref_primary = ref.get("primary_diagnosis", "")

            prepared_predictions.append(pred_primary)
            prepared_references.append(ref_primary)

        # 使用基础评估方法
        basic_results = super().evaluate(prepared_predictions, prepared_references)

        # 添加特定于中医辨证的评估
        tcm_specific_results = self._evaluate_tcm_specific(predictions, expert_opinions)

        # 合并结果
        results = {**basic_results, **tcm_specific_results}

        return results

    def _evaluate_tcm_specific(
        self, predictions: list[dict[str, Any]], expert_opinions: list[dict[str, Any]]
    ) -> dict[str, float]:
        """
        中医特定评估

        Args:
            predictions: 预测辨证结果
            expert_opinions: 专家辨证结果

        Returns:
            评估结果
        """
        results = {}

        # 计算症状匹配率
        symptom_match_rate = self._calculate_symptom_match_rate(
            predictions, expert_opinions
        )
        results["symptom_match_rate"] = symptom_match_rate

        # 计算治法一致性
        treatment_consistency = self._calculate_treatment_consistency(
            predictions, expert_opinions
        )
        results["treatment_consistency"] = treatment_consistency

        return results

    def _calculate_symptom_match_rate(
        self, predictions: list[dict[str, Any]], expert_opinions: list[dict[str, Any]]
    ) -> float:
        """
        计算症状匹配率

        Args:
            predictions: 预测辨证结果
            expert_opinions: 专家辨证结果

        Returns:
            症状匹配率
        """
        total_match_rate = 0.0
        valid_count = 0

        for pred, ref in zip(predictions, expert_opinions, strict=False):
            pred_symptoms = set(pred.get("symptoms", []))
            ref_symptoms = set(ref.get("symptoms", []))

            if not ref_symptoms:
                continue

            # 计算匹配率
            intersection = pred_symptoms.intersection(ref_symptoms)
            match_rate = len(intersection) / len(ref_symptoms)

            total_match_rate += match_rate
            valid_count += 1

        return total_match_rate / valid_count if valid_count > 0 else 0.0

    def _calculate_treatment_consistency(
        self, predictions: list[dict[str, Any]], expert_opinions: list[dict[str, Any]]
    ) -> float:
        """
        计算治法一致性

        Args:
            predictions: 预测辨证结果
            expert_opinions: 专家辨证结果

        Returns:
            治法一致性
        """
        total_consistency = 0.0
        valid_count = 0

        for pred, ref in zip(predictions, expert_opinions, strict=False):
            pred_treatments = set(pred.get("treatments", []))
            ref_treatments = set(ref.get("treatments", []))

            if not ref_treatments:
                continue

            # 计算一致性
            intersection = pred_treatments.intersection(ref_treatments)
            consistency = len(intersection) / len(ref_treatments)

            total_consistency += consistency
            valid_count += 1

        return total_consistency / valid_count if valid_count > 0 else 0.0


class PerformanceEvaluator(BaseEvaluator):
    """性能评估器"""

    def __init__(self, metrics: list[str], config: dict[str, Any] | None = None):
        """
        初始化性能评估器

        Args:
            metrics: 指标列表
            config: 配置
        """
        super().__init__(metrics, config)

    def evaluate(self, performance_data: dict[str, list[float]]) -> dict[str, float]:
        """
        评估性能数据

        Args:
            performance_data: 性能数据
                {
                    "latencies": [...],  # 单位：毫秒
                    "memory_usage": [...],  # 单位：MB
                    "cpu_usage": [...],  # 单位：%
                    "energy_consumption": [...]  # 单位：mW·h
                }

        Returns:
            评估结果
        """
        results = {}

        for metric_name in self.metrics:
            try:
                # 针对不同类型的指标使用不同的数据
                if "latency" in metric_name:
                    data = performance_data.get("latencies", [])
                elif "memory" in metric_name:
                    data = performance_data.get("memory_usage", [])
                elif "cpu" in metric_name:
                    data = performance_data.get("cpu_usage", [])
                elif "energy" in metric_name:
                    data = performance_data.get("energy_consumption", [])
                else:
                    data = []

                # 使用指标注册表计算指标
                metric_value = METRIC_REGISTRY.compute(metric_name, data, [])

                if metric_value is not None:
                    results[metric_name] = metric_value
                else:
                    logger.warning(f"指标 {metric_name} 计算结果为空")
            except Exception as e:
                logger.error(f"计算指标 {metric_name} 出错: {str(e)}", exc_info=True)

        return results


class EvaluatorFactory:
    """评估器工厂"""

    @staticmethod
    def create(
        task_type: str, metrics: list[str], config: dict[str, Any] | None = None
    ) -> BaseEvaluator:
        """
        创建评估器

        Args:
            task_type: 任务类型
            metrics: 指标列表
            config: 配置

        Returns:
            评估器实例
        """
        if task_type in [
            "TCM_DIAGNOSIS",
            "TONGUE_RECOGNITION",
            "FACE_RECOGNITION",
            "PULSE_RECOGNITION",
        ]:
            return TCMDiagnosisEvaluator(metrics, config)
        elif task_type == "HEALTH_PLAN_GENERATION":
            return GenerationEvaluator(metrics, config)
        elif task_type == "EDGE_PERFORMANCE":
            return PerformanceEvaluator(metrics, config)
        else:
            # 默认使用基础评估器
            return BaseEvaluator(metrics, config)
