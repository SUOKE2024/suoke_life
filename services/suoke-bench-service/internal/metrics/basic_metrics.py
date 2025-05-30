"""
基础评估指标

实现常用评估指标的计算函数。
"""

import logging
import re
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

from internal.metrics.metric_registry import MetricInfo, metric_registry

logger = logging.getLogger(__name__)


def register_basic_metrics():
    """注册基础指标"""
    # 分类指标
    metric_registry.register(
        MetricInfo(
            name="accuracy",
            display_name="准确率",
            description="预测正确的样本比例",
            func=compute_accuracy,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.7,
            unit="%",
            tags=["classification", "basic"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="precision",
            display_name="精确率",
            description="真正例占所有预测为正例的比例",
            func=compute_precision,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.7,
            unit="%",
            tags=["classification", "basic"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="recall",
            display_name="召回率",
            description="真正例占所有实际为正例的比例",
            func=compute_recall,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.7,
            unit="%",
            tags=["classification", "basic"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="f1",
            display_name="F1分数",
            description="精确率和召回率的调和平均值",
            func=compute_f1,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.7,
            unit="%",
            tags=["classification", "basic"],
        )
    )

    # 回归指标
    metric_registry.register(
        MetricInfo(
            name="mae",
            display_name="平均绝对误差",
            description="预测值与真实值差的绝对值的平均值",
            func=compute_mae,
            higher_is_better=False,
            min_value=0.0,
            max_value=float("inf"),
            threshold=0.1,
            unit="",
            tags=["regression", "basic"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="mse",
            display_name="均方误差",
            description="预测值与真实值差的平方的平均值",
            func=compute_mse,
            higher_is_better=False,
            min_value=0.0,
            max_value=float("inf"),
            threshold=0.01,
            unit="",
            tags=["regression", "basic"],
        )
    )

    # 生成指标
    metric_registry.register(
        MetricInfo(
            name="exact_match",
            display_name="精确匹配率",
            description="预测值与真实值完全匹配的比例",
            func=compute_exact_match,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.5,
            unit="%",
            tags=["generation", "basic"],
        )
    )

    # 中医五诊指标
    metric_registry.register(
        MetricInfo(
            name="tongue_classification_accuracy",
            display_name="舌象分类准确率",
            description="舌象分类任务的准确率",
            func=compute_tongue_classification_accuracy,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.8,
            unit="%",
            tags=["tcm", "tongue", "classification"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="syndrome_classification_accuracy",
            display_name="辩证分类准确率",
            description="中医辩证分类任务的准确率",
            func=compute_syndrome_classification_accuracy,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.75,
            unit="%",
            tags=["tcm", "syndrome", "classification"],
        )
    )

    # 性能指标
    metric_registry.register(
        MetricInfo(
            name="latency",
            display_name="推理延迟",
            description="模型推理的平均延迟时间",
            func=compute_latency,
            higher_is_better=False,
            min_value=0.0,
            max_value=float("inf"),
            threshold=100.0,
            unit="ms",
            tags=["performance", "basic"],
        )
    )

    metric_registry.register(
        MetricInfo(
            name="throughput",
            display_name="吞吐量",
            description="每秒处理的样本数",
            func=compute_throughput,
            higher_is_better=True,
            min_value=0.0,
            max_value=float("inf"),
            threshold=10.0,
            unit="samples/s",
            tags=["performance", "basic"],
        )
    )

    # 多智能体协作指标
    metric_registry.register(
        MetricInfo(
            name="collaboration_efficiency",
            display_name="协作效率",
            description="多智能体协作完成任务的效率",
            func=compute_collaboration_efficiency,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.7,
            unit="%",
            tags=["agent", "collaboration"],
        )
    )

    # 隐私指标
    metric_registry.register(
        MetricInfo(
            name="privacy_leakage",
            display_name="隐私泄露率",
            description="隐私保护技术的泄露率",
            func=compute_privacy_leakage,
            higher_is_better=False,
            min_value=0.0,
            max_value=1.0,
            threshold=0.1,
            unit="%",
            tags=["privacy", "security"],
        )
    )

    # 健康方案生成指标
    metric_registry.register(
        MetricInfo(
            name="health_plan_quality",
            display_name="健康方案质量",
            description="生成的健康方案的综合质量评估",
            func=compute_health_plan_quality,
            higher_is_better=True,
            min_value=0.0,
            max_value=1.0,
            threshold=0.8,
            unit="%",
            tags=["health_plan", "generation"],
        )
    )


# 基础分类指标实现
def compute_accuracy(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算准确率

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        准确率
    """
    try:
        return float(accuracy_score(targets, predictions))
    except Exception as e:
        logger.error(f"计算准确率失败: {str(e)}")
        return 0.0


def compute_precision(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算精确率

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        精确率
    """
    try:
        average = params.get("average", "binary") if params else "binary"
        return float(precision_score(targets, predictions, average=average))
    except Exception as e:
        logger.error(f"计算精确率失败: {str(e)}")
        return 0.0


def compute_recall(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算召回率

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        召回率
    """
    try:
        average = params.get("average", "binary") if params else "binary"
        return float(recall_score(targets, predictions, average=average))
    except Exception as e:
        logger.error(f"计算召回率失败: {str(e)}")
        return 0.0


def compute_f1(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算F1分数

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        F1分数
    """
    try:
        average = params.get("average", "binary") if params else "binary"
        return float(f1_score(targets, predictions, average=average))
    except Exception as e:
        logger.error(f"计算F1分数失败: {str(e)}")
        return 0.0


# 回归指标实现
def compute_mae(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算平均绝对误差

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        平均绝对误差
    """
    try:
        return float(np.mean(np.abs(np.array(predictions) - np.array(targets))))
    except Exception as e:
        logger.error(f"计算平均绝对误差失败: {str(e)}")
        return float("inf")


def compute_mse(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算均方误差

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        均方误差
    """
    try:
        return float(np.mean(np.square(np.array(predictions) - np.array(targets))))
    except Exception as e:
        logger.error(f"计算均方误差失败: {str(e)}")
        return float("inf")


# 生成指标实现
def compute_exact_match(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算精确匹配率

    Args:
        predictions: 预测值
        targets: 目标值
        params: 计算参数

    Returns:
        精确匹配率
    """
    try:
        if isinstance(predictions, list) and isinstance(targets, list):
            # 列表匹配
            matches = [p == t for p, t in zip(predictions, targets, strict=False)]
            return float(sum(matches) / len(matches))
        elif isinstance(predictions, str) and isinstance(targets, str):
            # 字符串匹配
            normalize = params.get("normalize", True) if params else True
            if normalize:
                predictions = predictions.strip().lower()
                targets = targets.strip().lower()
            return float(predictions == targets)
        else:
            logger.error(f"不支持的数据类型: {type(predictions)}, {type(targets)}")
            return 0.0
    except Exception as e:
        logger.error(f"计算精确匹配率失败: {str(e)}")
        return 0.0


# 中医五诊指标实现
def compute_tongue_classification_accuracy(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算舌象分类准确率

    Args:
        predictions: 预测值，预期格式为字典列表，每个字典包含舌象特征
        targets: 目标值，预期格式为字典列表，每个字典包含舌象特征
        params: 计算参数

    Returns:
        舌象分类准确率
    """
    try:
        # 关键特征字段
        key_features = (
            params.get("key_features", ["color", "coating", "shape"])
            if params
            else ["color", "coating", "shape"]
        )

        if not isinstance(predictions, list) or not isinstance(targets, list):
            logger.error("预期输入和目标为字典列表")
            return 0.0

        total_score = 0.0
        for pred, target in zip(predictions, targets, strict=False):
            # 每个特征匹配得分
            feature_scores = []
            for feature in key_features:
                if feature in pred and feature in target:
                    if isinstance(pred[feature], list) and isinstance(
                        target[feature], list
                    ):
                        # 计算列表的Jaccard相似度
                        intersection = len(set(pred[feature]) & set(target[feature]))
                        union = len(set(pred[feature]) | set(target[feature]))
                        feature_scores.append(
                            intersection / union if union > 0 else 0.0
                        )
                    else:
                        # 字符串完全匹配
                        feature_scores.append(
                            1.0 if pred[feature] == target[feature] else 0.0
                        )
                else:
                    feature_scores.append(0.0)

            # 计算样本平均得分
            total_score += sum(feature_scores) / len(key_features)

        # 返回所有样本的平均分数
        return total_score / len(predictions) if predictions else 0.0
    except Exception as e:
        logger.error(f"计算舌象分类准确率失败: {str(e)}")
        return 0.0


def compute_syndrome_classification_accuracy(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算中医辩证分类准确率

    Args:
        predictions: 预测值，预期格式为辩证类型列表
        targets: 目标值，预期格式为辩证类型列表
        params: 计算参数

    Returns:
        中医辩证分类准确率
    """
    try:
        if isinstance(predictions[0], list) and isinstance(targets[0], list):
            # 多标签情况，使用Jaccard相似度
            scores = []
            for pred, target in zip(predictions, targets, strict=False):
                intersection = len(set(pred) & set(target))
                union = len(set(pred) | set(target))
                scores.append(intersection / union if union > 0 else 0.0)
            return float(np.mean(scores))
        else:
            # 单标签情况，使用准确率
            return compute_accuracy(predictions, targets, params)
    except Exception as e:
        logger.error(f"计算中医辩证分类准确率失败: {str(e)}")
        return 0.0


# 性能指标实现
def compute_latency(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算推理延迟

    Args:
        predictions: 不使用
        targets: 不使用
        params: 计算参数，必须包含latency_ms字段

    Returns:
        平均推理延迟（毫秒）
    """
    try:
        if not params or "latency_ms" not in params:
            logger.error("计算延迟需要提供latency_ms参数")
            return float("inf")

        latency_list = params["latency_ms"]
        if not latency_list:
            return float("inf")

        return float(np.mean(latency_list))
    except Exception as e:
        logger.error(f"计算推理延迟失败: {str(e)}")
        return float("inf")


def compute_throughput(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算吞吐量

    Args:
        predictions: 不使用
        targets: 不使用
        params: 计算参数，必须包含latency_ms字段

    Returns:
        吞吐量（每秒样本数）
    """
    try:
        if not params or "latency_ms" not in params:
            logger.error("计算吞吐量需要提供latency_ms参数")
            return 0.0

        latency_list = params["latency_ms"]
        if not latency_list:
            return 0.0

        # 计算每个样本的平均处理时间（秒）
        avg_latency_s = np.mean(latency_list) / 1000.0
        if avg_latency_s <= 0:
            return 0.0

        # 计算每秒可处理样本数
        return float(1.0 / avg_latency_s)
    except Exception as e:
        logger.error(f"计算吞吐量失败: {str(e)}")
        return 0.0


# 多智能体协作指标实现
def compute_collaboration_efficiency(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算多智能体协作效率

    Args:
        predictions: 预测结果，预期包含多智能体对话记录
        targets: 目标值，预期包含专家评分
        params: 计算参数

    Returns:
        协作效率分数
    """
    try:
        # 此处需要根据实际场景实现，简单示例如下
        if not params or not isinstance(params, dict):
            logger.error("计算协作效率需要提供参数")
            return 0.0

        # 从专家评分中提取协作效率分数
        if "expert_scores" in params:
            scores = params["expert_scores"]
            if "collaboration_efficiency" in scores:
                return float(scores["collaboration_efficiency"])

        # 如果没有专家评分，则分析对话结构
        if "dialogue" in predictions:
            dialogue = predictions["dialogue"]

            # 智能体统计
            agent_counts = {}
            for turn in dialogue:
                if (
                    "speaker" in turn
                    and turn["speaker"] != "user"
                    and turn["speaker"] != "system"
                ):
                    agent = turn["speaker"]
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1

            # 计算信息传递效率
            total_turns = len(dialogue)
            user_turns = sum(1 for turn in dialogue if turn.get("speaker") == "user")
            system_turns = sum(
                1 for turn in dialogue if turn.get("speaker") == "system"
            )
            agent_turns = total_turns - user_turns - system_turns

            # 简单评估：智能体参与均衡性 + 对话轮次效率
            if agent_turns == 0 or len(agent_counts) <= 1:
                return 0.0  # 无协作

            # 计算智能体参与均衡度
            balance_score = 1.0 - np.std(list(agent_counts.values())) / np.mean(
                list(agent_counts.values())
            )

            # 计算对话效率（越少轮次完成任务越高效）
            efficiency_factor = min(1.0, 15.0 / total_turns)  # 假设理想轮次为15

            # 综合得分
            return float(0.6 * balance_score + 0.4 * efficiency_factor)

        logger.error("未找到有效的对话数据")
        return 0.0
    except Exception as e:
        logger.error(f"计算协作效率失败: {str(e)}")
        return 0.0


# 隐私指标实现
def compute_privacy_leakage(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算隐私泄露率

    Args:
        predictions: 预测结果
        targets: 目标敏感数据
        params: 计算参数

    Returns:
        隐私泄露率
    """
    try:
        # 此处需要根据实际场景实现，简单示例如下
        if "attack_success_rate" in params:
            # 直接使用攻击成功率作为泄露率
            return float(params["attack_success_rate"])

        # 如果是敏感信息推断测试
        if isinstance(predictions, list) and isinstance(targets, list):
            # 计算准确推断的敏感信息比例
            matches = [p == t for p, t in zip(predictions, targets, strict=False)]
            return float(sum(matches) / len(matches))

        logger.error("无法计算隐私泄露率，缺少必要信息")
        return 0.0
    except Exception as e:
        logger.error(f"计算隐私泄露率失败: {str(e)}")
        return 0.0


# 健康方案生成指标实现
def compute_health_plan_quality(
    predictions: Any, targets: Any, params: dict[str, Any] | None = None
) -> float:
    """
    计算健康方案质量

    Args:
        predictions: 预测生成的健康方案
        targets: 专家生成的健康方案（参考）
        params: 计算参数，可能包含专家评分

    Returns:
        健康方案质量评分
    """
    try:
        # 此处需要根据实际场景实现，简单示例如下

        # 如果有专家评分，直接使用
        if params and "expert_scores" in params:
            if "quality" in params["expert_scores"]:
                return float(params["expert_scores"]["quality"])

        # 如果没有专家评分，执行自动评估
        if not isinstance(predictions, dict) or not isinstance(targets, dict):
            logger.error("健康方案应为字典格式")
            return 0.0

        # 关键部分评分
        scores = []

        # 1. 评估饮食建议
        if "diet" in predictions and "diet" in targets:
            diet_score = _evaluate_plan_section(predictions["diet"], targets["diet"])
            scores.append(diet_score)

        # 2. 评估运动建议
        if "exercise" in predictions and "exercise" in targets:
            exercise_score = _evaluate_plan_section(
                predictions["exercise"], targets["exercise"]
            )
            scores.append(exercise_score)

        # 3. 评估生活习惯建议
        if "living_habits" in predictions and "living_habits" in targets:
            habits_score = _evaluate_plan_section(
                predictions["living_habits"], targets["living_habits"]
            )
            scores.append(habits_score)

        # 如果没有足够的部分进行评估
        if not scores:
            logger.error("无法评估健康方案质量，缺少必要部分")
            return 0.0

        # 返回平均评分
        return float(np.mean(scores))
    except Exception as e:
        logger.error(f"计算健康方案质量失败: {str(e)}")
        return 0.0


def _evaluate_plan_section(pred_section, target_section):
    """
    评估健康方案的某一部分

    这是一个辅助函数，用于计算健康方案各部分的相似度

    Args:
        pred_section: 预测的部分
        target_section: 目标部分

    Returns:
        该部分的评分
    """
    # 首先检查原则一致性
    if "principles" in pred_section and "principles" in target_section:
        pred_principles = set(pred_section["principles"])
        target_principles = set(target_section["principles"])
        principles_score = len(pred_principles & target_principles) / len(
            target_principles
        )
    else:
        principles_score = 0.5  # 无法评估原则

    # 然后检查建议项的匹配度
    recommendations_score = 0.5  # 默认中等

    # 检查各种可能的建议字段
    for field in ["recommended_foods", "recommended_activities", "recommendations"]:
        if field in pred_section and field in target_section:
            if isinstance(pred_section[field], list) and isinstance(
                target_section[field], list
            ):
                # 简单文本相似度评估
                pred_texts = " ".join([str(item) for item in pred_section[field]])
                target_texts = " ".join([str(item) for item in target_section[field]])

                # 计算关键词匹配率
                pred_words = set(re.findall(r"\b\w+\b", pred_texts.lower()))
                target_words = set(re.findall(r"\b\w+\b", target_texts.lower()))

                if target_words:
                    recommendations_score = len(pred_words & target_words) / len(
                        target_words
                    )
                break

    # 整合评分
    return 0.6 * principles_score + 0.4 * recommendations_score
