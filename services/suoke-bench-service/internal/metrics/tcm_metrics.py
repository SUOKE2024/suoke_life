"""中医特色评测指标实现。"""

from dataclasses import dataclass
from typing import Any

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from .agent_metrics import MetricResult
from .metrics import Metric

@dataclass
class TongueFeature:
    """舌象特征数据类。"""

    color: str  # 舌色
    coating: str  # 舌苔
    shape: str  # 舌形
    moisture: str  # 舌润
    cracks: list[str]  # 裂纹
    spots: list[dict[str, Any]]  # 斑点

@dataclass
class FaceFeature:
    """面色特征数据类。"""

    color: str  # 面色
    luster: str  # 光泽
    expression: str  # 神态
    areas: dict[str, str]  # 面部分区特征

@dataclass
class PulseFeature:
    """脉象特征数据类。"""

    frequency: float  # 脉率
    strength: str  # 脉力
    rhythm: str  # 脉律
    width: str  # 脉宽
    depth: str  # 脉位深浅
    length: str  # 脉长短

class TongueRecognitionMetric(Metric):
    """舌象识别评测指标。"""

    def __init__(self, threshold: float = 0.85):
        super().__init__("tongue_recognition", threshold, "", True)
        self.description = "评估舌象识别的准确性"

    def calculate(
        self, predictions: list[TongueFeature], ground_truth: list[TongueFeature]
    ) -> MetricResult:
        """计算舌象识别的准确性指标。"""

        # 计算各个特征的准确率
        color_acc = self._calculate_feature_accuracy(
            [p.color for p in predictions], [g.color for g in ground_truth]
        )

        coating_acc = self._calculate_feature_accuracy(
            [p.coating for p in predictions], [g.coating for g in ground_truth]
        )

        shape_acc = self._calculate_feature_accuracy(
            [p.shape for p in predictions], [g.shape for g in ground_truth]
        )

        moisture_acc = self._calculate_feature_accuracy(
            [p.moisture for p in predictions], [g.moisture for g in ground_truth]
        )

        # 计算裂纹识别的F1分数
        cracks_f1 = self._calculate_cracks_f1(
            [p.cracks for p in predictions], [g.cracks for g in ground_truth]
        )

        # 计算斑点识别的IoU
        spots_iou = self._calculate_spots_iou(
            [p.spots for p in predictions], [g.spots for g in ground_truth]
        )

        # 计算加权总分
        weights = {
            "color": 0.25,
            "coating": 0.25,
            "shape": 0.15,
            "moisture": 0.15,
            "cracks": 0.1,
            "spots": 0.1,
        }

        total_score = (
            weights["color"] * color_acc
            + weights["coating"] * coating_acc
            + weights["shape"] * shape_acc
            + weights["moisture"] * moisture_acc
            + weights["cracks"] * cracks_f1
            + weights["spots"] * spots_iou
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "color_accuracy": color_acc,
                "coating_accuracy": coating_acc,
                "shape_accuracy": shape_acc,
                "moisture_accuracy": moisture_acc,
                "cracks_f1": cracks_f1,
                "spots_iou": spots_iou,
            },
        )

    def _calculate_feature_accuracy(self, pred: list[str], true: list[str]) -> float:
        """计算分类特征的准确率。"""
        return accuracy_score(true, pred)

    def _calculate_cracks_f1(
        self, pred: list[list[str]], true: list[list[str]]
    ) -> float:
        """计算裂纹识别的F1分数。"""
        f1_scores = []
        for p, t in zip(pred, true, strict=False):
            # 将裂纹列表转换为集合
            p_set = set(p)
            t_set = set(t)

            # 计算精确率和召回率
            if len(p_set) == 0 and len(t_set) == 0:
                f1_scores.append(1.0)
            elif len(p_set) == 0 or len(t_set) == 0:
                f1_scores.append(0.0)
            else:
                precision = len(p_set & t_set) / len(p_set)
                recall = len(p_set & t_set) / len(t_set)
                if precision + recall == 0:
                    f1_scores.append(0.0)
                else:
                    f1 = 2 * (precision * recall) / (precision + recall)
                    f1_scores.append(f1)

        return np.mean(f1_scores)

    def _calculate_spots_iou(
        self, pred: list[list[dict[str, Any]]], true: list[list[dict[str, Any]]]
    ) -> float:
        """计算斑点识别的IoU (Intersection over Union)。"""
        ious = []
        for p_spots, t_spots in zip(pred, true, strict=False):
            if len(p_spots) == 0 and len(t_spots) == 0:
                ious.append(1.0)
                continue

            if len(p_spots) == 0 or len(t_spots) == 0:
                ious.append(0.0)
                continue

            # 计算每对斑点之间的IoU
            max_ious = []
            for t_spot in t_spots:
                spot_ious = []
                for p_spot in p_spots:
                    # 计算两个斑点区域的IoU
                    intersection = self._calculate_spot_intersection(p_spot, t_spot)
                    union = self._calculate_spot_union(p_spot, t_spot)
                    iou = intersection / union if union > 0 else 0
                    spot_ious.append(iou)
                max_ious.append(max(spot_ious))

            ious.append(np.mean(max_ious))

        return np.mean(ious)

    def _calculate_spot_intersection(
        self, spot1: dict[str, Any], spot2: dict[str, Any]
    ) -> float:
        """计算两个斑点区域的交集面积。"""
        x1 = max(spot1["x"], spot2["x"])
        y1 = max(spot1["y"], spot2["y"])
        x2 = min(spot1["x"] + spot1["width"], spot2["x"] + spot2["width"])
        y2 = min(spot1["y"] + spot1["height"], spot2["y"] + spot2["height"])

        if x2 <= x1 or y2 <= y1:
            return 0

        return (x2 - x1) * (y2 - y1)

    def _calculate_spot_union(
        self, spot1: dict[str, Any], spot2: dict[str, Any]
    ) -> float:
        """计算两个斑点区域的并集面积。"""
        area1 = spot1["width"] * spot1["height"]
        area2 = spot2["width"] * spot2["height"]
        intersection = self._calculate_spot_intersection(spot1, spot2)
        return area1 + area2 - intersection

class FaceRecognitionMetric(Metric):
    """面色识别评测指标。"""

    def __init__(self, threshold: float = 0.85):
        super().__init__(threshold)
        self.name = "face_recognition"
        self.description = "评估面色识别的准确性"

    def calculate(
        self, predictions: list[FaceFeature], ground_truth: list[FaceFeature]
    ) -> MetricResult:
        """计算面色识别的准确性指标。"""

        # 计算基本特征的准确率
        color_acc = self._calculate_feature_accuracy(
            [p.color for p in predictions], [g.color for g in ground_truth]
        )

        luster_acc = self._calculate_feature_accuracy(
            [p.luster for p in predictions], [g.luster for g in ground_truth]
        )

        expression_acc = self._calculate_feature_accuracy(
            [p.expression for p in predictions], [g.expression for g in ground_truth]
        )

        # 计算面部分区特征的准确率
        areas_acc = self._calculate_areas_accuracy(
            [p.areas for p in predictions], [g.areas for g in ground_truth]
        )

        # 计算加权总分
        weights = {"color": 0.3, "luster": 0.2, "expression": 0.2, "areas": 0.3}

        total_score = (
            weights["color"] * color_acc
            + weights["luster"] * luster_acc
            + weights["expression"] * expression_acc
            + weights["areas"] * areas_acc
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "color_accuracy": color_acc,
                "luster_accuracy": luster_acc,
                "expression_accuracy": expression_acc,
                "areas_accuracy": areas_acc,
            },
        )

    def _calculate_feature_accuracy(self, pred: list[str], true: list[str]) -> float:
        """计算分类特征的准确率。"""
        return accuracy_score(true, pred)

    def _calculate_areas_accuracy(
        self, pred: list[dict[str, str]], true: list[dict[str, str]]
    ) -> float:
        """计算面部分区特征的准确率。"""
        accuracies = []
        for p_areas, t_areas in zip(pred, true, strict=False):
            # 确保两个字典有相同的键
            common_areas = set(p_areas.keys()) & set(t_areas.keys())
            if not common_areas:
                accuracies.append(0.0)
                continue

            # 计算每个分区的准确率
            area_matches = sum(
                1 for area in common_areas if p_areas[area] == t_areas[area]
            )
            accuracies.append(area_matches / len(common_areas))

        return np.mean(accuracies)

class PulseRecognitionMetric(Metric):
    """脉象识别评测指标。"""

    def __init__(self, threshold: float = 0.85):
        super().__init__(threshold)
        self.name = "pulse_recognition"
        self.description = "评估脉象识别的准确性"

    def calculate(
        self, predictions: list[PulseFeature], ground_truth: list[PulseFeature]
    ) -> MetricResult:
        """计算脉象识别的准确性指标。"""

        # 计算脉率的均方根误差
        frequency_rmse = self._calculate_frequency_rmse(
            [p.frequency for p in predictions], [g.frequency for g in ground_truth]
        )

        # 计算其他特征的准确率
        strength_acc = self._calculate_feature_accuracy(
            [p.strength for p in predictions], [g.strength for g in ground_truth]
        )

        rhythm_acc = self._calculate_feature_accuracy(
            [p.rhythm for p in predictions], [g.rhythm for g in ground_truth]
        )

        width_acc = self._calculate_feature_accuracy(
            [p.width for p in predictions], [g.width for g in ground_truth]
        )

        depth_acc = self._calculate_feature_accuracy(
            [p.depth for p in predictions], [g.depth for g in ground_truth]
        )

        length_acc = self._calculate_feature_accuracy(
            [p.length for p in predictions], [g.length for g in ground_truth]
        )

        # 将RMSE转换为准确率分数
        frequency_acc = 1.0 - min(frequency_rmse / 10.0, 1.0)

        # 计算加权总分
        weights = {
            "frequency": 0.2,
            "strength": 0.2,
            "rhythm": 0.15,
            "width": 0.15,
            "depth": 0.15,
            "length": 0.15,
        }

        total_score = (
            weights["frequency"] * frequency_acc
            + weights["strength"] * strength_acc
            + weights["rhythm"] * rhythm_acc
            + weights["width"] * width_acc
            + weights["depth"] * depth_acc
            + weights["length"] * length_acc
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "frequency_accuracy": frequency_acc,
                "frequency_rmse": frequency_rmse,
                "strength_accuracy": strength_acc,
                "rhythm_accuracy": rhythm_acc,
                "width_accuracy": width_acc,
                "depth_accuracy": depth_acc,
                "length_accuracy": length_acc,
            },
        )

    def _calculate_feature_accuracy(self, pred: list[str], true: list[str]) -> float:
        """计算分类特征的准确率。"""
        return accuracy_score(true, pred)

    def _calculate_frequency_rmse(self, pred: list[float], true: list[float]) -> float:
        """计算脉率的均方根误差。"""
        return np.sqrt(np.mean((np.array(pred) - np.array(true)) ** 2))

class ConstitutionClassificationMetric(Metric):
    """体质辨识评测指标。"""

    def __init__(self, threshold: float = 0.85):
        super().__init__(threshold)
        self.name = "constitution_classification"
        self.description = "评估体质辨识的准确性"
        self.constitution_types = [
            "balanced",
            "qi_deficiency",
            "yang_deficiency",
            "yin_deficiency",
            "phlegm_dampness",
            "damp_heat",
            "blood_stasis",
            "qi_depression",
            "special",
        ]

    def calculate(
        self,
        predictions: list[str],
        ground_truth: list[str],
        confidences: list[float] | None = None,
    ) -> MetricResult:
        """计算体质辨识的准确性指标。"""

        # 计算基本分类指标
        accuracy = accuracy_score(ground_truth, predictions)
        precision = precision_score(
            ground_truth,
            predictions,
            average="weighted",
            labels=self.constitution_types,
        )
        recall = recall_score(
            ground_truth,
            predictions,
            average="weighted",
            labels=self.constitution_types,
        )
        f1 = f1_score(
            ground_truth,
            predictions,
            average="weighted",
            labels=self.constitution_types,
        )

        # 如果提供了置信度，计算置信度加权的准确率
        if confidences is not None:
            confidence_weighted_acc = self._calculate_confidence_weighted_accuracy(
                predictions, ground_truth, confidences
            )
        else:
            confidence_weighted_acc = accuracy

        # 计算加权总分
        weights = {
            "accuracy": 0.3,
            "precision": 0.2,
            "recall": 0.2,
            "f1": 0.2,
            "confidence_weighted": 0.1,
        }

        total_score = (
            weights["accuracy"] * accuracy
            + weights["precision"] * precision
            + weights["recall"] * recall
            + weights["f1"] * f1
            + weights["confidence_weighted"] * confidence_weighted_acc
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "confidence_weighted_accuracy": confidence_weighted_acc,
            },
        )

    def _calculate_confidence_weighted_accuracy(
        self, pred: list[str], true: list[str], conf: list[float]
    ) -> float:
        """计算置信度加权的准确率。"""
        correct = [1 if p == t else 0 for p, t in zip(pred, true, strict=False)]
        weighted_correct = sum(c * w for c, w in zip(correct, conf, strict=False))
        return weighted_correct / sum(conf)
