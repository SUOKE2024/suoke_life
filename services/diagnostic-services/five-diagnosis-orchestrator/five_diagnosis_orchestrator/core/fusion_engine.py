"""
诊断融合引擎

负责将多个诊断服务的结果进行智能融合，生成综合诊断结果
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..config.settings import get_settings
from ..models.diagnosis_models import (
    DiagnosisRecommendation,
    DiagnosisResult,
    DiagnosisType,
    FusedDiagnosisResult,
    PatientInfo,
)
from ..utils.ml_models import MLModelManager
from ..utils.tcm_knowledge import TCMKnowledgeBase

logger = logging.getLogger(__name__)


class FusionStrategy(Enum):
    """融合策略"""

    WEIGHTED_AVERAGE = "weighted_average"  # 加权平均
    BAYESIAN_FUSION = "bayesian_fusion"  # 贝叶斯融合
    ENSEMBLE_LEARNING = "ensemble_learning"  # 集成学习
    EXPERT_SYSTEM = "expert_system"  # 专家系统
    HYBRID = "hybrid"  # 混合策略


@dataclass
class FusionConfig:
    """融合配置"""

    strategy: FusionStrategy = FusionStrategy.HYBRID
    confidence_threshold: float = 0.6
    consistency_threshold: float = 0.7
    enable_conflict_resolution: bool = True
    enable_uncertainty_quantification: bool = True

    # 诊断类型权重
    diagnosis_weights: Dict[DiagnosisType, float] = field(
        default_factory=lambda: {
            DiagnosisType.INQUIRY: 0.30,  # 问诊权重最高
            DiagnosisType.LOOK: 0.25,  # 望诊次之
            DiagnosisType.CALCULATION: 0.20,  # 算诊
            DiagnosisType.LISTEN: 0.15,  # 闻诊
            DiagnosisType.PALPATION: 0.10,  # 切诊
        }
    )

    # 特征权重
    feature_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "syndrome": 0.4,  # 证型
            "constitution": 0.3,  # 体质
            "symptoms": 0.2,  # 症状
            "pulse": 0.1,  # 脉象
        }
    )


@dataclass
class ConflictInfo:
    """冲突信息"""

    feature_name: str
    conflicting_values: List[Tuple[str, float, DiagnosisType]]  # (值, 置信度, 来源)
    resolution_method: str
    resolved_value: str
    resolved_confidence: float


class DiagnosisFusionEngine:
    """诊断融合引擎"""

    def __init__(self, config: Optional[FusionConfig] = None):
        self.config = config or FusionConfig()
        self.settings = get_settings()
        self.tcm_knowledge = TCMKnowledgeBase()
        self.ml_models = MLModelManager()

        # 融合统计
        self.fusion_stats = {
            "total_fusions": 0,
            "successful_fusions": 0,
            "conflicts_resolved": 0,
            "average_confidence": 0.0,
            "average_consistency": 0.0,
        }

        self._initialized = False

    async def initialize(self) -> None:
        """初始化融合引擎"""
        if self._initialized:
            return

        logger.info("初始化诊断融合引擎...")

        try:
            # 初始化中医知识库
            await self.tcm_knowledge.initialize()

            # 初始化机器学习模型
            await self.ml_models.initialize()

            self._initialized = True
            logger.info("诊断融合引擎初始化完成")

        except Exception as e:
            logger.error(f"融合引擎初始化失败: {e}")
            raise

    async def fuse_diagnosis_results(
        self,
        session_id: str,
        patient_info: PatientInfo,
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> FusedDiagnosisResult:
        """融合诊断结果"""
        if not self._initialized:
            await self.initialize()

        start_time = datetime.utcnow()

        try:
            # 验证输入
            if not diagnosis_results:
                raise ValueError("没有可用的诊断结果")

            # 提取特征
            features = await self._extract_features(diagnosis_results)

            # 检测冲突
            conflicts = await self._detect_conflicts(features)

            # 解决冲突
            if conflicts and self.config.enable_conflict_resolution:
                features = await self._resolve_conflicts(features, conflicts)

            # 执行融合
            if self.config.strategy == FusionStrategy.WEIGHTED_AVERAGE:
                fused_features = await self._weighted_average_fusion(
                    features, diagnosis_results
                )
            elif self.config.strategy == FusionStrategy.BAYESIAN_FUSION:
                fused_features = await self._bayesian_fusion(
                    features, diagnosis_results
                )
            elif self.config.strategy == FusionStrategy.ENSEMBLE_LEARNING:
                fused_features = await self._ensemble_learning_fusion(
                    features, diagnosis_results
                )
            elif self.config.strategy == FusionStrategy.EXPERT_SYSTEM:
                fused_features = await self._expert_system_fusion(
                    features, diagnosis_results
                )
            else:  # HYBRID
                fused_features = await self._hybrid_fusion(features, diagnosis_results)

            # 计算置信度和一致性
            overall_confidence = await self._calculate_overall_confidence(
                fused_features, diagnosis_results
            )
            consistency_score = await self._calculate_consistency_score(
                diagnosis_results
            )
            completeness_score = await self._calculate_completeness_score(
                diagnosis_results
            )

            # 分析证型和体质
            syndrome_analysis = await self._analyze_syndromes(fused_features)
            constitution_analysis = await self._analyze_constitution(
                fused_features, patient_info
            )

            # 评估健康状态和风险
            health_status = await self._assess_health_status(
                fused_features, syndrome_analysis
            )
            risk_factors = await self._identify_risk_factors(
                fused_features, patient_info
            )

            # 生成建议
            recommendations = await self._generate_recommendations(
                fused_features, syndrome_analysis, constitution_analysis, patient_info
            )

            # 创建融合结果
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            fused_result = FusedDiagnosisResult(
                session_id=session_id,
                patient_info=patient_info,
                individual_results=diagnosis_results,
                primary_syndrome=syndrome_analysis.get("primary", ""),
                secondary_syndromes=syndrome_analysis.get("secondary", []),
                constitution_type=constitution_analysis.get("type", ""),
                health_status=health_status,
                risk_factors=risk_factors,
                overall_confidence=overall_confidence,
                consistency_score=consistency_score,
                completeness_score=completeness_score,
                treatment_recommendations=recommendations.get("treatment", []),
                lifestyle_recommendations=recommendations.get("lifestyle", []),
                follow_up_recommendations=recommendations.get("follow_up", []),
                total_processing_time=processing_time,
            )

            # 更新统计
            self._update_fusion_stats(
                overall_confidence, consistency_score, len(conflicts)
            )

            logger.info(
                f"诊断融合完成: {session_id}, 置信度: {overall_confidence:.3f}, 一致性: {consistency_score:.3f}"
            )
            return fused_result

        except Exception as e:
            logger.error(f"诊断融合失败: {session_id}, 错误: {e}")
            raise

    async def _extract_features(
        self, diagnosis_results: Dict[DiagnosisType, DiagnosisResult]
    ) -> Dict[str, Any]:
        """提取特征"""
        features = {
            "syndromes": {},
            "constitution": {},
            "symptoms": {},
            "pulse": {},
            "tongue": {},
            "face": {},
            "voice": {},
            "other": {},
        }

        for diagnosis_type, result in diagnosis_results.items():
            if result.features:
                # 根据诊断类型分类特征
                if diagnosis_type == DiagnosisType.INQUIRY:
                    features["symptoms"].update(result.features.get("symptoms", {}))
                    features["syndromes"].update(result.features.get("syndromes", {}))
                elif diagnosis_type == DiagnosisType.LOOK:
                    features["tongue"].update(result.features.get("tongue", {}))
                    features["face"].update(result.features.get("face", {}))
                elif diagnosis_type == DiagnosisType.LISTEN:
                    features["voice"].update(result.features.get("voice", {}))
                elif diagnosis_type == DiagnosisType.PALPATION:
                    features["pulse"].update(result.features.get("pulse", {}))
                elif diagnosis_type == DiagnosisType.CALCULATION:
                    features["constitution"].update(
                        result.features.get("constitution", {})
                    )

                # 通用特征
                features["other"].update(result.features.get("other", {}))

        return features

    async def _detect_conflicts(self, features: Dict[str, Any]) -> List[ConflictInfo]:
        """检测特征冲突"""
        conflicts = []

        # 检测证型冲突
        syndrome_conflicts = await self._detect_syndrome_conflicts(
            features.get("syndromes", {})
        )
        conflicts.extend(syndrome_conflicts)

        # 检测体质冲突
        constitution_conflicts = await self._detect_constitution_conflicts(
            features.get("constitution", {})
        )
        conflicts.extend(constitution_conflicts)

        return conflicts

    async def _detect_syndrome_conflicts(
        self, syndromes: Dict[str, Any]
    ) -> List[ConflictInfo]:
        """检测证型冲突"""
        conflicts = []

        # 使用中医知识库检测互斥证型
        for syndrome1, confidence1 in syndromes.items():
            for syndrome2, confidence2 in syndromes.items():
                if syndrome1 != syndrome2:
                    if await self.tcm_knowledge.are_syndromes_conflicting(
                        syndrome1, syndrome2
                    ):
                        conflicts.append(
                            ConflictInfo(
                                feature_name="syndrome_conflict",
                                conflicting_values=[
                                    (syndrome1, confidence1, DiagnosisType.INQUIRY),
                                    (syndrome2, confidence2, DiagnosisType.INQUIRY),
                                ],
                                resolution_method="tcm_knowledge",
                                resolved_value="",
                                resolved_confidence=0.0,
                            )
                        )

        return conflicts

    async def _detect_constitution_conflicts(
        self, constitutions: Dict[str, Any]
    ) -> List[ConflictInfo]:
        """检测体质冲突"""
        conflicts = []

        # 体质类型通常是互斥的，检测多个高置信度体质
        high_confidence_constitutions = [
            (const, conf) for const, conf in constitutions.items() if conf > 0.7
        ]

        if len(high_confidence_constitutions) > 1:
            conflicts.append(
                ConflictInfo(
                    feature_name="constitution_conflict",
                    conflicting_values=[
                        (const, conf, DiagnosisType.CALCULATION)
                        for const, conf in high_confidence_constitutions
                    ],
                    resolution_method="highest_confidence",
                    resolved_value="",
                    resolved_confidence=0.0,
                )
            )

        return conflicts

    async def _resolve_conflicts(
        self, features: Dict[str, Any], conflicts: List[ConflictInfo]
    ) -> Dict[str, Any]:
        """解决冲突"""
        resolved_features = features.copy()

        for conflict in conflicts:
            if conflict.resolution_method == "tcm_knowledge":
                # 使用中医知识库解决冲突
                resolved_value, confidence = await self._resolve_with_tcm_knowledge(
                    conflict
                )
            elif conflict.resolution_method == "highest_confidence":
                # 选择置信度最高的值
                resolved_value, confidence = max(
                    [(val, conf) for val, conf, _ in conflict.conflicting_values],
                    key=lambda x: x[1],
                )
            else:
                # 默认使用加权平均
                resolved_value, confidence = await self._resolve_with_weighted_average(
                    conflict
                )

            conflict.resolved_value = resolved_value
            conflict.resolved_confidence = confidence

            # 更新特征
            if "syndrome" in conflict.feature_name:
                resolved_features["syndromes"] = {resolved_value: confidence}
            elif "constitution" in conflict.feature_name:
                resolved_features["constitution"] = {resolved_value: confidence}

        return resolved_features

    async def _resolve_with_tcm_knowledge(
        self, conflict: ConflictInfo
    ) -> Tuple[str, float]:
        """使用中医知识库解决冲突"""
        # 查询中医知识库，找到最合适的证型
        values = [val for val, _, _ in conflict.conflicting_values]
        confidences = [conf for _, conf, _ in conflict.conflicting_values]

        best_syndrome = await self.tcm_knowledge.resolve_syndrome_conflict(
            values, confidences
        )
        best_confidence = max(confidences)

        return best_syndrome, best_confidence

    async def _resolve_with_weighted_average(
        self, conflict: ConflictInfo
    ) -> Tuple[str, float]:
        """使用加权平均解决冲突"""
        # 简单选择置信度最高的值
        return max(
            [(val, conf) for val, conf, _ in conflict.conflicting_values],
            key=lambda x: x[1],
        )

    async def _weighted_average_fusion(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> Dict[str, Any]:
        """加权平均融合"""
        fused_features = {}

        for feature_category, feature_data in features.items():
            if not feature_data:
                continue

            category_weight = self.config.feature_weights.get(feature_category, 1.0)
            weighted_features = {}

            for feature_name, feature_value in feature_data.items():
                if isinstance(feature_value, (int, float)):
                    # 数值特征：计算加权平均
                    total_weight = 0
                    weighted_sum = 0

                    for diagnosis_type, result in diagnosis_results.items():
                        if feature_name in result.features.get(feature_category, {}):
                            diagnosis_weight = self.config.diagnosis_weights.get(
                                diagnosis_type, 1.0
                            )
                            weight = (
                                diagnosis_weight * result.confidence * category_weight
                            )
                            weighted_sum += feature_value * weight
                            total_weight += weight

                    if total_weight > 0:
                        weighted_features[feature_name] = weighted_sum / total_weight
                else:
                    # 分类特征：选择置信度最高的
                    weighted_features[feature_name] = feature_value

            fused_features[feature_category] = weighted_features

        return fused_features

    async def _bayesian_fusion(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> Dict[str, Any]:
        """贝叶斯融合"""
        # 简化的贝叶斯融合实现
        fused_features = {}

        for feature_category, feature_data in features.items():
            if not feature_data:
                continue

            bayesian_features = {}

            for feature_name, feature_value in feature_data.items():
                # 计算后验概率
                prior = 0.5  # 先验概率
                likelihood_product = 1.0

                for diagnosis_type, result in diagnosis_results.items():
                    if feature_name in result.features.get(feature_category, {}):
                        likelihood = result.confidence
                        likelihood_product *= likelihood

                # 贝叶斯更新
                posterior = (likelihood_product * prior) / (
                    likelihood_product * prior + (1 - likelihood_product) * (1 - prior)
                )
                bayesian_features[feature_name] = (
                    feature_value if isinstance(feature_value, str) else posterior
                )

            fused_features[feature_category] = bayesian_features

        return fused_features

    async def _ensemble_learning_fusion(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> Dict[str, Any]:
        """集成学习融合"""
        # 使用预训练的集成模型进行融合
        if not self.ml_models.has_fusion_model():
            # 如果没有训练好的模型，回退到加权平均
            return await self._weighted_average_fusion(features, diagnosis_results)

        # 准备输入数据
        input_data = await self._prepare_ml_input(features, diagnosis_results)

        # 使用集成模型预测
        fused_output = await self.ml_models.predict_fusion(input_data)

        return fused_output

    async def _expert_system_fusion(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> Dict[str, Any]:
        """专家系统融合"""
        # 使用中医专家规则进行融合
        fused_features = {}

        # 应用专家规则
        rules_output = await self.tcm_knowledge.apply_expert_rules(
            features, diagnosis_results
        )

        # 合并规则输出
        for category, rule_features in rules_output.items():
            fused_features[category] = rule_features

        return fused_features

    async def _hybrid_fusion(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> Dict[str, Any]:
        """混合策略融合"""
        # 结合多种融合策略

        # 1. 首先使用加权平均作为基础
        base_fusion = await self._weighted_average_fusion(features, diagnosis_results)

        # 2. 使用专家系统进行规则校正
        expert_fusion = await self._expert_system_fusion(features, diagnosis_results)

        # 3. 如果有ML模型，使用集成学习进行优化
        if self.ml_models.has_fusion_model():
            ml_fusion = await self._ensemble_learning_fusion(
                features, diagnosis_results
            )
            # 融合三种结果
            final_fusion = await self._combine_fusion_results(
                [base_fusion, expert_fusion, ml_fusion]
            )
        else:
            # 融合两种结果
            final_fusion = await self._combine_fusion_results(
                [base_fusion, expert_fusion]
            )

        return final_fusion

    async def _combine_fusion_results(
        self, fusion_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """合并多个融合结果"""
        if not fusion_results:
            return {}

        if len(fusion_results) == 1:
            return fusion_results[0]

        combined = {}

        # 获取所有类别
        all_categories = set()
        for result in fusion_results:
            all_categories.update(result.keys())

        for category in all_categories:
            category_features = {}

            # 获取所有特征名
            all_features = set()
            for result in fusion_results:
                if category in result:
                    all_features.update(result[category].keys())

            for feature_name in all_features:
                feature_values = []
                for result in fusion_results:
                    if category in result and feature_name in result[category]:
                        feature_values.append(result[category][feature_name])

                if feature_values:
                    if all(isinstance(v, (int, float)) for v in feature_values):
                        # 数值特征：取平均值
                        category_features[feature_name] = sum(feature_values) / len(
                            feature_values
                        )
                    else:
                        # 分类特征：取第一个非空值
                        category_features[feature_name] = next(
                            v for v in feature_values if v
                        )

            combined[category] = category_features

        return combined

    async def _calculate_overall_confidence(
        self,
        fused_features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> float:
        """计算整体置信度"""
        if not diagnosis_results:
            return 0.0

        # 加权平均置信度
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for diagnosis_type, result in diagnosis_results.items():
            weight = self.config.diagnosis_weights.get(diagnosis_type, 1.0)
            total_weighted_confidence += result.confidence * weight
            total_weight += weight

        base_confidence = (
            total_weighted_confidence / total_weight if total_weight > 0 else 0.0
        )

        # 根据特征完整性调整置信度
        completeness_factor = len(fused_features) / 8  # 假设有8个主要特征类别
        completeness_factor = min(completeness_factor, 1.0)

        return base_confidence * (0.7 + 0.3 * completeness_factor)

    async def _calculate_consistency_score(
        self, diagnosis_results: Dict[DiagnosisType, DiagnosisResult]
    ) -> float:
        """计算一致性分数"""
        if len(diagnosis_results) < 2:
            return 1.0

        # 计算诊断结果间的相似度
        confidences = [result.confidence for result in diagnosis_results.values()]

        # 使用置信度的标准差来衡量一致性
        if len(confidences) > 1:
            mean_confidence = sum(confidences) / len(confidences)
            variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(
                confidences
            )
            std_dev = variance**0.5

            # 标准差越小，一致性越高
            consistency = max(0.0, 1.0 - std_dev)
        else:
            consistency = 1.0

        return consistency

    async def _calculate_completeness_score(
        self, diagnosis_results: Dict[DiagnosisType, DiagnosisResult]
    ) -> float:
        """计算完整性分数"""
        total_diagnosis_types = len(DiagnosisType)
        completed_types = len(diagnosis_results)

        return completed_types / total_diagnosis_types

    async def _analyze_syndromes(
        self, fused_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析证型"""
        syndromes = fused_features.get("syndromes", {})

        if not syndromes:
            return {"primary": "", "secondary": [], "confidence": 0.0}

        # 按置信度排序
        sorted_syndromes = sorted(syndromes.items(), key=lambda x: x[1], reverse=True)

        primary_syndrome = sorted_syndromes[0][0] if sorted_syndromes else ""
        secondary_syndromes = [s[0] for s in sorted_syndromes[1:3]]  # 取前2个次要证型

        return {
            "primary": primary_syndrome,
            "secondary": secondary_syndromes,
            "confidence": sorted_syndromes[0][1] if sorted_syndromes else 0.0,
            "all_syndromes": dict(sorted_syndromes),
        }

    async def _analyze_constitution(
        self, fused_features: Dict[str, Any], patient_info: PatientInfo
    ) -> Dict[str, Any]:
        """分析体质"""
        constitution_features = fused_features.get("constitution", {})

        if not constitution_features:
            return {"type": "", "confidence": 0.0}

        # 结合患者基本信息进行体质分析
        constitution_analysis = await self.tcm_knowledge.analyze_constitution(
            constitution_features, patient_info.age, patient_info.gender
        )

        return constitution_analysis

    async def _assess_health_status(
        self, fused_features: Dict[str, Any], syndrome_analysis: Dict[str, Any]
    ) -> str:
        """评估健康状态"""
        # 基于证型和症状评估健康状态
        primary_syndrome = syndrome_analysis.get("primary", "")
        syndrome_confidence = syndrome_analysis.get("confidence", 0.0)

        if not primary_syndrome or syndrome_confidence < 0.3:
            return "健康"
        elif syndrome_confidence < 0.6:
            return "亚健康"
        else:
            # 根据证型严重程度判断
            if await self.tcm_knowledge.is_severe_syndrome(primary_syndrome):
                return "需要关注"
            else:
                return "轻度不适"

    async def _identify_risk_factors(
        self, fused_features: Dict[str, Any], patient_info: PatientInfo
    ) -> List[str]:
        """识别风险因素"""
        risk_factors = []

        # 基于症状识别风险
        symptoms = fused_features.get("symptoms", {})
        for symptom, confidence in symptoms.items():
            if confidence > 0.7:
                risks = await self.tcm_knowledge.get_symptom_risks(symptom)
                risk_factors.extend(risks)

        # 基于年龄和性别识别风险
        age_risks = await self.tcm_knowledge.get_age_related_risks(
            patient_info.age, patient_info.gender
        )
        risk_factors.extend(age_risks)

        # 去重并返回
        return list(set(risk_factors))

    async def _generate_recommendations(
        self,
        fused_features: Dict[str, Any],
        syndrome_analysis: Dict[str, Any],
        constitution_analysis: Dict[str, Any],
        patient_info: PatientInfo,
    ) -> Dict[str, List[str]]:
        """生成建议"""
        recommendations = {"treatment": [], "lifestyle": [], "follow_up": []}

        # 基于证型生成治疗建议
        primary_syndrome = syndrome_analysis.get("primary", "")
        if primary_syndrome:
            treatment_recs = await self.tcm_knowledge.get_syndrome_treatments(
                primary_syndrome
            )
            recommendations["treatment"].extend(treatment_recs)

        # 基于体质生成生活方式建议
        constitution_type = constitution_analysis.get("type", "")
        if constitution_type:
            lifestyle_recs = await self.tcm_knowledge.get_constitution_lifestyle(
                constitution_type
            )
            recommendations["lifestyle"].extend(lifestyle_recs)

        # 基于症状生成随访建议
        symptoms = fused_features.get("symptoms", {})
        high_risk_symptoms = [s for s, c in symptoms.items() if c > 0.8]
        if high_risk_symptoms:
            follow_up_recs = await self.tcm_knowledge.get_follow_up_recommendations(
                high_risk_symptoms
            )
            recommendations["follow_up"].extend(follow_up_recs)

        return recommendations

    async def _prepare_ml_input(
        self,
        features: Dict[str, Any],
        diagnosis_results: Dict[DiagnosisType, DiagnosisResult],
    ) -> np.ndarray:
        """准备机器学习输入数据"""
        # 将特征转换为数值向量
        feature_vector = []

        # 添加诊断置信度
        for diagnosis_type in DiagnosisType:
            if diagnosis_type in diagnosis_results:
                feature_vector.append(diagnosis_results[diagnosis_type].confidence)
            else:
                feature_vector.append(0.0)

        # 添加特征值
        for category in ["syndromes", "constitution", "symptoms", "pulse"]:
            category_features = features.get(category, {})
            if category_features:
                # 取前5个最高置信度的特征
                sorted_features = sorted(
                    category_features.items(), key=lambda x: x[1], reverse=True
                )[:5]
                for _, confidence in sorted_features:
                    feature_vector.append(
                        confidence if isinstance(confidence, (int, float)) else 0.0
                    )
                # 填充到固定长度
                while len(sorted_features) < 5:
                    feature_vector.append(0.0)
                    sorted_features.append(("", 0.0))
            else:
                # 填充空值
                feature_vector.extend([0.0] * 5)

        return np.array(feature_vector)

    def _update_fusion_stats(
        self, confidence: float, consistency: float, conflicts_count: int
    ) -> None:
        """更新融合统计"""
        self.fusion_stats["total_fusions"] += 1

        if confidence >= self.config.confidence_threshold:
            self.fusion_stats["successful_fusions"] += 1

        self.fusion_stats["conflicts_resolved"] += conflicts_count

        # 更新平均值
        total = self.fusion_stats["total_fusions"]
        self.fusion_stats["average_confidence"] = (
            self.fusion_stats["average_confidence"] * (total - 1) + confidence
        ) / total
        self.fusion_stats["average_consistency"] = (
            self.fusion_stats["average_consistency"] * (total - 1) + consistency
        ) / total

    async def get_fusion_stats(self) -> Dict[str, Any]:
        """获取融合统计"""
        total = self.fusion_stats["total_fusions"]
        return {
            "total_fusions": total,
            "successful_fusions": self.fusion_stats["successful_fusions"],
            "success_rate": self.fusion_stats["successful_fusions"] / max(total, 1),
            "conflicts_resolved": self.fusion_stats["conflicts_resolved"],
            "average_confidence": self.fusion_stats["average_confidence"],
            "average_consistency": self.fusion_stats["average_consistency"],
        }

    async def close(self) -> None:
        """关闭融合引擎"""
        logger.info("关闭诊断融合引擎...")

        if hasattr(self, "tcm_knowledge"):
            await self.tcm_knowledge.close()
        if hasattr(self, "ml_models"):
            await self.ml_models.close()

        logger.info("诊断融合引擎已关闭")
