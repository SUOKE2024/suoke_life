"""
小克智能体决策引擎
基于规则和机器学习的智能决策系统
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..domain.models import (
    Appointment,
    ConstitutionType,
    Doctor,
    Recommendation,
    Resource,
    ResourceType,
    UrgencyLevel,
)

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """决策类型"""

    RESOURCE_ALLOCATION = "resource_allocation"  # 资源分配
    APPOINTMENT_SCHEDULING = "appointment_scheduling"  # 预约调度
    TREATMENT_RECOMMENDATION = "treatment_recommendation"  # 治疗推荐
    EMERGENCY_RESPONSE = "emergency_response"  # 应急响应
    CONSTITUTION_ANALYSIS = "constitution_analysis"  # 体质分析
    FOOD_THERAPY = "food_therapy"  # 食疗推荐
    WELLNESS_TOURISM = "wellness_tourism"  # 养生旅游
    PREVENTIVE_CARE = "preventive_care"  # 预防保健

class DecisionStrategy(Enum):
    """决策策略"""

    RULE_BASED = "rule_based"  # 基于规则
    ML_BASED = "ml_based"  # 基于机器学习
    HYBRID = "hybrid"  # 混合策略
    REINFORCEMENT = "reinforcement"  # 强化学习
    MULTI_CRITERIA = "multi_criteria"  # 多准则决策
    FUZZY_LOGIC = "fuzzy_logic"  # 模糊逻辑

class ConfidenceLevel(Enum):
    """置信度等级"""

    VERY_LOW = "very_low"  # 0.0-0.2
    LOW = "low"  # 0.2-0.4
    MEDIUM = "medium"  # 0.4-0.6
    HIGH = "high"  # 0.6-0.8
    VERY_HIGH = "very_high"  # 0.8-1.0

@dataclass
class DecisionContext:
    """决策上下文"""

    user_id: str
    constitution_type: ConstitutionType
    symptoms: List[str]
    urgency_level: UrgencyLevel
    historical_data: Dict[str, Any]
    environmental_factors: Dict[str, Any]
    time_constraints: Dict[str, Any]
    resource_availability: Dict[str, Any]
    user_preferences: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionRule:
    """决策规则"""

    rule_id: str
    name: str
    condition: str
    action: str
    priority: int
    confidence_weight: float
    applicable_contexts: List[DecisionType]
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    usage_count: int = 0
    success_rate: float = 0.0

@dataclass
class DecisionResult:
    """决策结果"""

    decision_id: str
    decision_type: DecisionType
    strategy_used: DecisionStrategy
    recommendation: Dict[str, Any]
    confidence_score: float
    confidence_level: ConfidenceLevel
    reasoning: List[str]
    alternative_options: List[Dict[str, Any]]
    execution_plan: Dict[str, Any]
    expected_outcome: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0

@dataclass
class DecisionFeedback:
    """决策反馈"""

    decision_id: str
    actual_outcome: Dict[str, Any]
    satisfaction_score: float
    effectiveness_score: float
    side_effects: List[str]
    user_comments: str
    timestamp: datetime = field(default_factory=datetime.now)

class DecisionEngine:
    """
    小克智能体决策引擎

    结合规则引擎和机器学习模型，为医疗资源管理提供智能决策支持
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_alternatives = config.get("max_alternatives", 5)
        self.min_confidence_threshold = config.get("min_confidence_threshold", 0.6)
        self.learning_rate = config.get("learning_rate", 0.01)

        # 决策规则库
        self.decision_rules: Dict[DecisionType, List[DecisionRule]] = defaultdict(list)

        # 决策历史
        self.decision_history: deque = deque(maxlen=10000)
        self.feedback_history: Dict[str, DecisionFeedback] = {}

        # 性能统计
        self.decision_stats: Dict[DecisionType, Dict[str, Any]] = defaultdict(dict)

        # 体质-资源权重矩阵
        self.constitution_resource_weights = self._initialize_constitution_weights()

        # 症状-治疗映射
        self.symptom_treatment_mapping = self._initialize_symptom_mapping()

        # 季节性因子
        self.seasonal_factors = self._initialize_seasonal_factors()

        # 初始化决策规则
        self._initialize_decision_rules()

        logger.info("决策引擎初始化完成")

    def _initialize_constitution_weights(
        self,
    ) -> Dict[ConstitutionType, Dict[str, float]]:
        """初始化体质-资源权重矩阵"""
        weights = {
            ConstitutionType.BALANCED: {
                "general_medicine": 1.0,
                "tcm_internal": 0.8,
                "nutrition": 0.9,
                "exercise": 1.0,
                "wellness": 0.8,
            },
            ConstitutionType.QI_DEFICIENCY: {
                "tcm_internal": 1.0,
                "nutrition": 0.9,
                "exercise": 0.7,
                "respiratory": 0.8,
                "wellness": 0.9,
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "tcm_internal": 1.0,
                "endocrinology": 0.8,
                "nutrition": 0.9,
                "thermal_therapy": 1.0,
                "wellness": 0.9,
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "tcm_internal": 1.0,
                "nephrology": 0.8,
                "nutrition": 0.9,
                "hydration_therapy": 1.0,
                "wellness": 0.8,
            },
            ConstitutionType.PHLEGM_DAMPNESS: {
                "tcm_internal": 1.0,
                "gastroenterology": 0.9,
                "nutrition": 1.0,
                "exercise": 0.9,
                "detox": 0.9,
            },
            ConstitutionType.DAMP_HEAT: {
                "tcm_internal": 1.0,
                "dermatology": 0.8,
                "nutrition": 1.0,
                "cooling_therapy": 1.0,
                "detox": 1.0,
            },
            ConstitutionType.BLOOD_STASIS: {
                "tcm_internal": 1.0,
                "cardiology": 0.9,
                "circulation_therapy": 1.0,
                "exercise": 0.8,
                "massage": 0.9,
            },
            ConstitutionType.QI_STAGNATION: {
                "tcm_internal": 1.0,
                "psychology": 0.8,
                "stress_management": 1.0,
                "exercise": 0.9,
                "meditation": 1.0,
            },
            ConstitutionType.ALLERGIC: {
                "allergy_immunology": 1.0,
                "tcm_internal": 0.8,
                "nutrition": 0.9,
                "environmental_medicine": 0.9,
                "wellness": 0.7,
            },
        }
        return weights

    def _initialize_symptom_mapping(self) -> Dict[str, Dict[str, float]]:
        """初始化症状-治疗映射"""
        mapping = {
            "乏力": {
                "qi_tonification": 1.0,
                "nutrition_therapy": 0.8,
                "exercise_therapy": 0.7,
                "sleep_optimization": 0.9,
            },
            "怕冷": {
                "yang_tonification": 1.0,
                "thermal_therapy": 0.9,
                "circulation_improvement": 0.8,
                "dietary_warming": 0.8,
            },
            "口干": {
                "yin_nourishment": 1.0,
                "hydration_therapy": 0.9,
                "saliva_stimulation": 0.7,
                "dietary_moistening": 0.8,
            },
            "失眠": {
                "heart_calming": 1.0,
                "sleep_hygiene": 0.9,
                "stress_reduction": 0.8,
                "meditation": 0.8,
            },
            "便秘": {
                "intestinal_moistening": 1.0,
                "dietary_fiber": 0.9,
                "exercise_therapy": 0.8,
                "hydration": 0.7,
            },
            "腹胀": {
                "qi_regulation": 1.0,
                "digestive_aid": 0.9,
                "dietary_adjustment": 0.8,
                "massage_therapy": 0.7,
            },
            "头痛": {
                "wind_dispelling": 1.0,
                "stress_relief": 0.8,
                "circulation_improvement": 0.7,
                "acupuncture": 0.9,
            },
            "易感冒": {
                "immune_boost": 1.0,
                "qi_tonification": 0.9,
                "lifestyle_adjustment": 0.8,
                "preventive_care": 0.9,
            },
        }
        return mapping

    def _initialize_seasonal_factors(self) -> Dict[int, Dict[str, float]]:
        """初始化季节性因子"""
        factors = {
            # 春季 (3-5月)
            3: {
                "liver_care": 1.2,
                "detox": 1.1,
                "allergy_prevention": 1.3,
                "exercise": 1.1,
            },
            4: {
                "liver_care": 1.3,
                "detox": 1.2,
                "allergy_prevention": 1.4,
                "exercise": 1.2,
            },
            5: {
                "liver_care": 1.1,
                "detox": 1.0,
                "allergy_prevention": 1.2,
                "exercise": 1.1,
            },
            # 夏季 (6-8月)
            6: {
                "heart_care": 1.2,
                "cooling": 1.3,
                "hydration": 1.2,
                "heat_prevention": 1.3,
            },
            7: {
                "heart_care": 1.3,
                "cooling": 1.4,
                "hydration": 1.3,
                "heat_prevention": 1.4,
            },
            8: {
                "heart_care": 1.2,
                "cooling": 1.3,
                "hydration": 1.2,
                "heat_prevention": 1.3,
            },
            # 秋季 (9-11月)
            9: {
                "lung_care": 1.2,
                "moistening": 1.2,
                "immune_boost": 1.1,
                "dryness_prevention": 1.2,
            },
            10: {
                "lung_care": 1.3,
                "moistening": 1.3,
                "immune_boost": 1.2,
                "dryness_prevention": 1.3,
            },
            11: {
                "lung_care": 1.1,
                "moistening": 1.1,
                "immune_boost": 1.3,
                "dryness_prevention": 1.1,
            },
            # 冬季 (12-2月)
            12: {
                "kidney_care": 1.2,
                "warming": 1.3,
                "energy_conservation": 1.2,
                "cold_prevention": 1.3,
            },
            1: {
                "kidney_care": 1.3,
                "warming": 1.4,
                "energy_conservation": 1.3,
                "cold_prevention": 1.4,
            },
            2: {
                "kidney_care": 1.2,
                "warming": 1.3,
                "energy_conservation": 1.2,
                "cold_prevention": 1.3,
            },
        }
        return factors

    def _initialize_decision_rules(self):
        """初始化决策规则"""
        # 资源分配规则
        self._add_resource_allocation_rules()

        # 治疗推荐规则
        self._add_treatment_recommendation_rules()

        # 应急响应规则
        self._add_emergency_response_rules()

        # 体质分析规则
        self._add_constitution_analysis_rules()

        # 食疗推荐规则
        self._add_food_therapy_rules()

        # 养生旅游规则
        self._add_wellness_tourism_rules()

    def _add_resource_allocation_rules(self):
        """添加资源分配规则"""
        rules = [
            DecisionRule(
                rule_id="RA001",
                name="紧急情况优先",
                condition="urgency_level == 'EMERGENCY'",
                action="allocate_emergency_resources",
                priority=1,
                confidence_weight=1.0,
                applicable_contexts=[DecisionType.RESOURCE_ALLOCATION],
            ),
            DecisionRule(
                rule_id="RA002",
                name="体质匹配分配",
                condition="constitution_type in ['QI_DEFICIENCY', 'YANG_DEFICIENCY']",
                action="allocate_tcm_resources",
                priority=2,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.RESOURCE_ALLOCATION],
            ),
            DecisionRule(
                rule_id="RA003",
                name="症状严重度分配",
                condition="len(symptoms) >= 3",
                action="allocate_comprehensive_resources",
                priority=3,
                confidence_weight=0.8,
                applicable_contexts=[DecisionType.RESOURCE_ALLOCATION],
            ),
        ]

        self.decision_rules[DecisionType.RESOURCE_ALLOCATION].extend(rules)

    def _add_treatment_recommendation_rules(self):
        """添加治疗推荐规则"""
        rules = [
            DecisionRule(
                rule_id="TR001",
                name="中医体质调理",
                condition="constitution_type != 'BALANCED'",
                action="recommend_constitution_treatment",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.TREATMENT_RECOMMENDATION],
            ),
            DecisionRule(
                rule_id="TR002",
                name="症状对症治疗",
                condition="symptoms is not empty",
                action="recommend_symptom_treatment",
                priority=2,
                confidence_weight=0.8,
                applicable_contexts=[DecisionType.TREATMENT_RECOMMENDATION],
            ),
            DecisionRule(
                rule_id="TR003",
                name="季节性调理",
                condition="seasonal_factors available",
                action="recommend_seasonal_treatment",
                priority=3,
                confidence_weight=0.7,
                applicable_contexts=[DecisionType.TREATMENT_RECOMMENDATION],
            ),
        ]

        self.decision_rules[DecisionType.TREATMENT_RECOMMENDATION].extend(rules)

    def _add_emergency_response_rules(self):
        """添加应急响应规则"""
        rules = [
            DecisionRule(
                rule_id="ER001",
                name="生命威胁响应",
                condition="urgency_level == 'EMERGENCY' and life_threatening",
                action="immediate_emergency_response",
                priority=1,
                confidence_weight=1.0,
                applicable_contexts=[DecisionType.EMERGENCY_RESPONSE],
            ),
            DecisionRule(
                rule_id="ER002",
                name="急性症状处理",
                condition="urgency_level == 'HIGH' and acute_symptoms",
                action="urgent_care_response",
                priority=2,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.EMERGENCY_RESPONSE],
            ),
        ]

        self.decision_rules[DecisionType.EMERGENCY_RESPONSE].extend(rules)

    def _add_constitution_analysis_rules(self):
        """添加体质分析规则"""
        rules = [
            DecisionRule(
                rule_id="CA001",
                name="气虚体质识别",
                condition="symptoms include ['乏力', '气短', '易感冒']",
                action="identify_qi_deficiency",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.CONSTITUTION_ANALYSIS],
            ),
            DecisionRule(
                rule_id="CA002",
                name="阳虚体质识别",
                condition="symptoms include ['怕冷', '手脚冰凉', '精神不振']",
                action="identify_yang_deficiency",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.CONSTITUTION_ANALYSIS],
            ),
            DecisionRule(
                rule_id="CA003",
                name="阴虚体质识别",
                condition="symptoms include ['口干', '盗汗', '五心烦热']",
                action="identify_yin_deficiency",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.CONSTITUTION_ANALYSIS],
            ),
        ]

        self.decision_rules[DecisionType.CONSTITUTION_ANALYSIS].extend(rules)

    def _add_food_therapy_rules(self):
        """添加食疗推荐规则"""
        rules = [
            DecisionRule(
                rule_id="FT001",
                name="气虚食疗",
                condition="constitution_type == 'QI_DEFICIENCY'",
                action="recommend_qi_tonifying_foods",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.FOOD_THERAPY],
            ),
            DecisionRule(
                rule_id="FT002",
                name="阳虚食疗",
                condition="constitution_type == 'YANG_DEFICIENCY'",
                action="recommend_yang_warming_foods",
                priority=1,
                confidence_weight=0.9,
                applicable_contexts=[DecisionType.FOOD_THERAPY],
            ),
            DecisionRule(
                rule_id="FT003",
                name="季节性食疗",
                condition="seasonal_factors available",
                action="recommend_seasonal_foods",
                priority=2,
                confidence_weight=0.8,
                applicable_contexts=[DecisionType.FOOD_THERAPY],
            ),
        ]

        self.decision_rules[DecisionType.FOOD_THERAPY].extend(rules)

    def _add_wellness_tourism_rules(self):
        """添加养生旅游规则"""
        rules = [
            DecisionRule(
                rule_id="WT001",
                name="体质养生旅游",
                condition="constitution_type != 'BALANCED'",
                action="recommend_constitution_wellness",
                priority=1,
                confidence_weight=0.8,
                applicable_contexts=[DecisionType.WELLNESS_TOURISM],
            ),
            DecisionRule(
                rule_id="WT002",
                name="季节性养生",
                condition="seasonal_factors available",
                action="recommend_seasonal_wellness",
                priority=2,
                confidence_weight=0.7,
                applicable_contexts=[DecisionType.WELLNESS_TOURISM],
            ),
        ]

        self.decision_rules[DecisionType.WELLNESS_TOURISM].extend(rules)

    async def make_decision(
        self,
        decision_type: DecisionType,
        context: DecisionContext,
        strategy: DecisionStrategy = DecisionStrategy.HYBRID,
    ) -> DecisionResult:
        """执行决策"""
        start_time = datetime.now()

        try:
            decision_id = (
                f"{decision_type.value}_{context.user_id}_{int(start_time.timestamp())}"
            )

            # 根据策略执行决策
            if strategy == DecisionStrategy.RULE_BASED:
                result = await self._rule_based_decision(decision_type, context)
            elif strategy == DecisionStrategy.ML_BASED:
                result = await self._ml_based_decision(decision_type, context)
            elif strategy == DecisionStrategy.HYBRID:
                result = await self._hybrid_decision(decision_type, context)
            elif strategy == DecisionStrategy.MULTI_CRITERIA:
                result = await self._multi_criteria_decision(decision_type, context)
            elif strategy == DecisionStrategy.FUZZY_LOGIC:
                result = await self._fuzzy_logic_decision(decision_type, context)
            else:
                result = await self._rule_based_decision(decision_type, context)

            # 设置决策结果属性
            result.decision_id = decision_id
            result.decision_type = decision_type
            result.strategy_used = strategy
            result.execution_time_ms = (
                datetime.now() - start_time
            ).total_seconds() * 1000

            # 确定置信度等级
            result.confidence_level = self._determine_confidence_level(
                result.confidence_score
            )

            # 记录决策历史
            self.decision_history.append(result)

            # 更新统计信息
            self._update_decision_stats(decision_type, result)

            logger.info(
                f"决策完成: {decision_id}, 置信度: {result.confidence_score:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"决策执行失败: {e}")
            # 返回默认决策结果
            return self._create_default_decision_result(
                decision_type, context, strategy
            )

    async def _rule_based_decision(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> DecisionResult:
        """基于规则的决策"""
        applicable_rules = self.decision_rules.get(decision_type, [])

        if not applicable_rules:
            return self._create_default_decision_result(
                decision_type, context, DecisionStrategy.RULE_BASED
            )

        # 评估规则
        rule_scores = []
        reasoning = []

        for rule in applicable_rules:
            score = self._evaluate_rule(rule, context)
            if score > 0:
                rule_scores.append((rule, score))
                reasoning.append(f"规则 {rule.name}: {score:.2f}")

        if not rule_scores:
            return self._create_default_decision_result(
                decision_type, context, DecisionStrategy.RULE_BASED
            )

        # 按分数排序
        rule_scores.sort(key=lambda x: x[1], reverse=True)

        # 生成推荐
        best_rule, best_score = rule_scores[0]
        recommendation = await self._execute_rule_action(best_rule, context)

        # 生成备选方案
        alternatives = []
        for rule, score in rule_scores[1 : self.max_alternatives]:
            alt_recommendation = await self._execute_rule_action(rule, context)
            alternatives.append(
                {
                    "recommendation": alt_recommendation,
                    "confidence": score,
                    "rule": rule.name,
                }
            )

        return DecisionResult(
            decision_id="",  # 将在make_decision中设置
            decision_type=decision_type,
            strategy_used=DecisionStrategy.RULE_BASED,
            recommendation=recommendation,
            confidence_score=best_score,
            confidence_level=ConfidenceLevel.MEDIUM,  # 将在make_decision中更新
            reasoning=reasoning,
            alternative_options=alternatives,
            execution_plan=self._create_execution_plan(recommendation),
            expected_outcome=self._predict_outcome(recommendation, context),
            risk_assessment=self._assess_risks(recommendation, context),
        )

    async def _ml_based_decision(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> DecisionResult:
        """基于机器学习的决策"""
        # 这里可以集成机器学习模型
        # 暂时使用简化的实现

        features = self._extract_features(context)

        # 模拟ML预测
        if decision_type == DecisionType.RESOURCE_ALLOCATION:
            recommendation = await self._ml_resource_allocation(features, context)
        elif decision_type == DecisionType.TREATMENT_RECOMMENDATION:
            recommendation = await self._ml_treatment_recommendation(features, context)
        else:
            recommendation = {"type": "general", "confidence": 0.5}

        confidence_score = recommendation.get("confidence", 0.5)

        return DecisionResult(
            decision_id="",
            decision_type=decision_type,
            strategy_used=DecisionStrategy.ML_BASED,
            recommendation=recommendation,
            confidence_score=confidence_score,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=[f"机器学习模型预测，置信度: {confidence_score:.2f}"],
            alternative_options=[],
            execution_plan=self._create_execution_plan(recommendation),
            expected_outcome=self._predict_outcome(recommendation, context),
            risk_assessment=self._assess_risks(recommendation, context),
        )

    async def _hybrid_decision(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> DecisionResult:
        """混合决策策略"""
        # 获取规则决策结果
        rule_result = await self._rule_based_decision(decision_type, context)

        # 获取ML决策结果
        ml_result = await self._ml_based_decision(decision_type, context)

        # 融合两种结果
        rule_weight = 0.6
        ml_weight = 0.4

        combined_confidence = (
            rule_result.confidence_score * rule_weight
            + ml_result.confidence_score * ml_weight
        )

        # 选择置信度更高的推荐
        if rule_result.confidence_score > ml_result.confidence_score:
            primary_recommendation = rule_result.recommendation
            primary_reasoning = rule_result.reasoning
        else:
            primary_recommendation = ml_result.recommendation
            primary_reasoning = ml_result.reasoning

        # 合并推理过程
        combined_reasoning = primary_reasoning + [
            f"混合决策: 规则权重{rule_weight}, ML权重{ml_weight}",
            f"最终置信度: {combined_confidence:.3f}",
        ]

        return DecisionResult(
            decision_id="",
            decision_type=decision_type,
            strategy_used=DecisionStrategy.HYBRID,
            recommendation=primary_recommendation,
            confidence_score=combined_confidence,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=combined_reasoning,
            alternative_options=rule_result.alternative_options
            + ml_result.alternative_options,
            execution_plan=self._create_execution_plan(primary_recommendation),
            expected_outcome=self._predict_outcome(primary_recommendation, context),
            risk_assessment=self._assess_risks(primary_recommendation, context),
        )

    async def _multi_criteria_decision(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> DecisionResult:
        """多准则决策"""
        criteria = {
            "effectiveness": 0.3,
            "safety": 0.25,
            "cost": 0.2,
            "accessibility": 0.15,
            "user_preference": 0.1,
        }

        # 生成候选方案
        candidates = await self._generate_candidates(decision_type, context)

        if not candidates:
            return self._create_default_decision_result(
                decision_type, context, DecisionStrategy.MULTI_CRITERIA
            )

        # 评估每个候选方案
        scored_candidates = []
        for candidate in candidates:
            scores = {}
            total_score = 0

            for criterion, weight in criteria.items():
                score = self._evaluate_criterion(candidate, criterion, context)
                scores[criterion] = score
                total_score += score * weight

            scored_candidates.append(
                {
                    "candidate": candidate,
                    "total_score": total_score,
                    "criterion_scores": scores,
                }
            )

        # 排序并选择最佳方案
        scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)
        best_candidate = scored_candidates[0]

        # 生成推理过程
        reasoning = [
            f"多准则决策分析，总分: {best_candidate['total_score']:.3f}",
            "各准则得分:",
        ]
        for criterion, score in best_candidate["criterion_scores"].items():
            reasoning.append(f"  {criterion}: {score:.3f}")

        # 生成备选方案
        alternatives = []
        for candidate_data in scored_candidates[1 : self.max_alternatives]:
            alternatives.append(
                {
                    "recommendation": candidate_data["candidate"],
                    "confidence": candidate_data["total_score"],
                    "criterion_scores": candidate_data["criterion_scores"],
                }
            )

        return DecisionResult(
            decision_id="",
            decision_type=decision_type,
            strategy_used=DecisionStrategy.MULTI_CRITERIA,
            recommendation=best_candidate["candidate"],
            confidence_score=best_candidate["total_score"],
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=reasoning,
            alternative_options=alternatives,
            execution_plan=self._create_execution_plan(best_candidate["candidate"]),
            expected_outcome=self._predict_outcome(
                best_candidate["candidate"], context
            ),
            risk_assessment=self._assess_risks(best_candidate["candidate"], context),
        )

    async def _fuzzy_logic_decision(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> DecisionResult:
        """模糊逻辑决策"""
        # 定义模糊集合
        fuzzy_sets = {
            "urgency": {
                "low": self._triangular_membership(
                    context.urgency_level.value, 0, 0, 0.3
                ),
                "medium": self._triangular_membership(
                    context.urgency_level.value, 0.2, 0.5, 0.8
                ),
                "high": self._triangular_membership(
                    context.urgency_level.value, 0.7, 1.0, 1.0
                ),
            },
            "symptom_severity": {
                "mild": self._triangular_membership(len(context.symptoms), 0, 0, 2),
                "moderate": self._triangular_membership(len(context.symptoms), 1, 3, 5),
                "severe": self._triangular_membership(len(context.symptoms), 4, 6, 10),
            },
        }

        # 模糊推理规则
        fuzzy_rules = [
            {
                "condition": {"urgency": "high", "symptom_severity": "severe"},
                "action": "immediate_intervention",
                "confidence": 0.9,
            },
            {
                "condition": {"urgency": "medium", "symptom_severity": "moderate"},
                "action": "standard_treatment",
                "confidence": 0.7,
            },
            {
                "condition": {"urgency": "low", "symptom_severity": "mild"},
                "action": "preventive_care",
                "confidence": 0.6,
            },
        ]

        # 评估模糊规则
        rule_activations = []
        for rule in fuzzy_rules:
            activation = 1.0
            for variable, value in rule["condition"].items():
                activation = min(activation, fuzzy_sets[variable][value])

            if activation > 0:
                rule_activations.append(
                    {
                        "rule": rule,
                        "activation": activation,
                        "weighted_confidence": activation * rule["confidence"],
                    }
                )

        if not rule_activations:
            return self._create_default_decision_result(
                decision_type, context, DecisionStrategy.FUZZY_LOGIC
            )

        # 选择最高激活度的规则
        best_rule = max(rule_activations, key=lambda x: x["weighted_confidence"])

        # 生成推荐
        recommendation = await self._execute_fuzzy_action(
            best_rule["rule"]["action"], context
        )

        reasoning = [
            f"模糊逻辑推理，激活度: {best_rule['activation']:.3f}",
            f"执行动作: {best_rule['rule']['action']}",
            f"加权置信度: {best_rule['weighted_confidence']:.3f}",
        ]

        return DecisionResult(
            decision_id="",
            decision_type=decision_type,
            strategy_used=DecisionStrategy.FUZZY_LOGIC,
            recommendation=recommendation,
            confidence_score=best_rule["weighted_confidence"],
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=reasoning,
            alternative_options=[],
            execution_plan=self._create_execution_plan(recommendation),
            expected_outcome=self._predict_outcome(recommendation, context),
            risk_assessment=self._assess_risks(recommendation, context),
        )

    def _triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        """三角形隶属函数"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x < c:
            return (c - x) / (c - b)
        else:
            return 0.0

    def _evaluate_rule(self, rule: DecisionRule, context: DecisionContext) -> float:
        """评估规则适用性"""
        try:
            # 简化的规则评估逻辑
            base_score = rule.confidence_weight

            # 根据规则条件调整分数
            if "urgency_level" in rule.condition:
                if context.urgency_level.value in rule.condition:
                    base_score *= 1.2

            if "constitution_type" in rule.condition:
                if context.constitution_type.value in rule.condition:
                    base_score *= 1.1

            if "symptoms" in rule.condition:
                symptom_match = any(
                    symptom in context.symptoms for symptom in ["乏力", "怕冷", "口干"]
                )
                if symptom_match:
                    base_score *= 1.1

            # 考虑规则的历史成功率
            if rule.success_rate > 0:
                base_score *= 0.5 + rule.success_rate * 0.5

            return min(base_score, 1.0)

        except Exception as e:
            logger.error(f"规则评估失败: {e}")
            return 0.0

    async def _execute_rule_action(
        self, rule: DecisionRule, context: DecisionContext
    ) -> Dict[str, Any]:
        """执行规则动作"""
        action = rule.action

        if action == "allocate_emergency_resources":
            return {
                "type": "emergency_allocation",
                "resources": ["emergency_doctor", "ambulance", "emergency_room"],
                "priority": "immediate",
                "estimated_time": "5-10 minutes",
            }
        elif action == "allocate_tcm_resources":
            return {
                "type": "tcm_allocation",
                "resources": ["tcm_doctor", "acupuncture", "herbal_medicine"],
                "priority": "high",
                "estimated_time": "30-60 minutes",
            }
        elif action == "recommend_constitution_treatment":
            return await self._get_constitution_treatment(context.constitution_type)
        elif action == "recommend_symptom_treatment":
            return await self._get_symptom_treatment(context.symptoms)
        else:
            return {"type": "general", "action": action, "priority": "medium"}

    async def _get_constitution_treatment(
        self, constitution_type: ConstitutionType
    ) -> Dict[str, Any]:
        """获取体质治疗方案"""
        treatments = {
            ConstitutionType.QI_DEFICIENCY: {
                "type": "qi_tonification",
                "methods": ["四君子汤", "补中益气汤", "太子参", "黄芪"],
                "lifestyle": ["适量运动", "规律作息", "避免过劳"],
                "diet": ["山药", "大枣", "莲子", "小米粥"],
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "type": "yang_warming",
                "methods": ["金匮肾气丸", "右归丸", "附子", "肉桂"],
                "lifestyle": ["保暖", "温水泡脚", "避免寒凉"],
                "diet": ["羊肉", "韭菜", "生姜", "核桃"],
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "type": "yin_nourishment",
                "methods": ["六味地黄丸", "知柏地黄丸", "沙参", "麦冬"],
                "lifestyle": ["避免熬夜", "保持心情平静", "适度运动"],
                "diet": ["银耳", "百合", "枸杞", "梨"],
            },
        }

        return treatments.get(
            constitution_type,
            {
                "type": "general_care",
                "methods": ["综合调理"],
                "lifestyle": ["健康生活方式"],
                "diet": ["均衡饮食"],
            },
        )

    async def _get_symptom_treatment(self, symptoms: List[str]) -> Dict[str, Any]:
        """获取症状治疗方案"""
        treatment_plan = {
            "type": "symptom_based_treatment",
            "treatments": [],
            "priority_symptoms": [],
            "estimated_duration": "1-2 weeks",
        }

        for symptom in symptoms:
            if symptom in self.symptom_treatment_mapping:
                treatments = self.symptom_treatment_mapping[symptom]
                for treatment, confidence in treatments.items():
                    treatment_plan["treatments"].append(
                        {
                            "treatment": treatment,
                            "confidence": confidence,
                            "target_symptom": symptom,
                        }
                    )

        # 按置信度排序
        treatment_plan["treatments"].sort(key=lambda x: x["confidence"], reverse=True)

        return treatment_plan

    def _extract_features(self, context: DecisionContext) -> Dict[str, Any]:
        """提取决策特征"""
        features = {
            "constitution_encoded": self._encode_constitution(
                context.constitution_type
            ),
            "symptom_count": len(context.symptoms),
            "urgency_encoded": self._encode_urgency(context.urgency_level),
            "time_of_day": context.timestamp.hour,
            "day_of_week": context.timestamp.weekday(),
            "month": context.timestamp.month,
            "has_historical_data": len(context.historical_data) > 0,
            "resource_availability_score": self._calculate_resource_availability_score(
                context.resource_availability
            ),
        }

        return features

    def _encode_constitution(self, constitution_type: ConstitutionType) -> int:
        """编码体质类型"""
        constitution_mapping = {
            ConstitutionType.BALANCED: 0,
            ConstitutionType.QI_DEFICIENCY: 1,
            ConstitutionType.YANG_DEFICIENCY: 2,
            ConstitutionType.YIN_DEFICIENCY: 3,
            ConstitutionType.PHLEGM_DAMPNESS: 4,
            ConstitutionType.DAMP_HEAT: 5,
            ConstitutionType.BLOOD_STASIS: 6,
            ConstitutionType.QI_STAGNATION: 7,
            ConstitutionType.ALLERGIC: 8,
        }
        return constitution_mapping.get(constitution_type, 0)

    def _encode_urgency(self, urgency_level: UrgencyLevel) -> float:
        """编码紧急程度"""
        urgency_mapping = {
            UrgencyLevel.LOW: 0.2,
            UrgencyLevel.MEDIUM: 0.5,
            UrgencyLevel.HIGH: 0.8,
            UrgencyLevel.EMERGENCY: 1.0,
        }
        return urgency_mapping.get(urgency_level, 0.5)

    def _calculate_resource_availability_score(
        self, resource_availability: Dict[str, Any]
    ) -> float:
        """计算资源可用性分数"""
        if not resource_availability:
            return 0.5

        total_score = 0
        count = 0

        for resource, availability in resource_availability.items():
            if isinstance(availability, (int, float)):
                total_score += availability
                count += 1
            elif isinstance(availability, bool):
                total_score += 1.0 if availability else 0.0
                count += 1

        return total_score / count if count > 0 else 0.5

    async def _ml_resource_allocation(
        self, features: Dict[str, Any], context: DecisionContext
    ) -> Dict[str, Any]:
        """机器学习资源分配"""
        # 简化的ML逻辑
        constitution_weights = self.constitution_resource_weights.get(
            context.constitution_type, {}
        )

        recommended_resources = []
        for resource, weight in constitution_weights.items():
            score = weight * (1 + features.get("urgency_encoded", 0.5))
            recommended_resources.append(
                {
                    "resource": resource,
                    "score": score,
                    "allocation_percentage": min(score * 100, 100),
                }
            )

        recommended_resources.sort(key=lambda x: x["score"], reverse=True)

        return {
            "type": "ml_resource_allocation",
            "resources": recommended_resources[:5],
            "confidence": 0.7,
            "model_version": "v1.0",
        }

    async def _ml_treatment_recommendation(
        self, features: Dict[str, Any], context: DecisionContext
    ) -> Dict[str, Any]:
        """机器学习治疗推荐"""
        # 基于症状和体质的治疗推荐
        treatments = []

        # 体质相关治疗
        constitution_treatment = await self._get_constitution_treatment(
            context.constitution_type
        )
        treatments.append(
            {
                "treatment": constitution_treatment,
                "confidence": 0.8,
                "type": "constitution_based",
            }
        )

        # 症状相关治疗
        if context.symptoms:
            symptom_treatment = await self._get_symptom_treatment(context.symptoms)
            treatments.append(
                {
                    "treatment": symptom_treatment,
                    "confidence": 0.7,
                    "type": "symptom_based",
                }
            )

        # 季节性调理
        month = context.timestamp.month
        seasonal_factors = self.seasonal_factors.get(month, {})
        if seasonal_factors:
            seasonal_treatment = {
                "type": "seasonal_care",
                "recommendations": list(seasonal_factors.keys()),
                "factors": seasonal_factors,
            }
            treatments.append(
                {"treatment": seasonal_treatment, "confidence": 0.6, "type": "seasonal"}
            )

        return {
            "type": "ml_treatment_recommendation",
            "treatments": treatments,
            "confidence": 0.75,
            "model_version": "v1.0",
        }

    async def _generate_candidates(
        self, decision_type: DecisionType, context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """生成候选方案"""
        candidates = []

        if decision_type == DecisionType.TREATMENT_RECOMMENDATION:
            # 生成治疗候选方案
            candidates.extend(
                [
                    await self._get_constitution_treatment(context.constitution_type),
                    await self._get_symptom_treatment(context.symptoms),
                ]
            )
        elif decision_type == DecisionType.RESOURCE_ALLOCATION:
            # 生成资源分配候选方案
            constitution_weights = self.constitution_resource_weights.get(
                context.constitution_type, {}
            )
            for resource, weight in constitution_weights.items():
                candidates.append(
                    {
                        "type": "resource_allocation",
                        "resource": resource,
                        "weight": weight,
                        "priority": "high" if weight > 0.8 else "medium",
                    }
                )

        return candidates

    def _evaluate_criterion(
        self, candidate: Dict[str, Any], criterion: str, context: DecisionContext
    ) -> float:
        """评估候选方案的准则得分"""
        if criterion == "effectiveness":
            return self._evaluate_effectiveness(candidate, context)
        elif criterion == "safety":
            return self._evaluate_safety(candidate, context)
        elif criterion == "cost":
            return self._evaluate_cost(candidate, context)
        elif criterion == "accessibility":
            return self._evaluate_accessibility(candidate, context)
        elif criterion == "user_preference":
            return self._evaluate_user_preference(candidate, context)
        else:
            return 0.5

    def _evaluate_effectiveness(
        self, candidate: Dict[str, Any], context: DecisionContext
    ) -> float:
        """评估有效性"""
        # 简化的有效性评估
        base_score = 0.7

        if candidate.get("type") == "constitution_based":
            base_score += 0.2

        if context.urgency_level == UrgencyLevel.HIGH and "emergency" in str(candidate):
            base_score += 0.1

        return min(base_score, 1.0)

    def _evaluate_safety(
        self, candidate: Dict[str, Any], context: DecisionContext
    ) -> float:
        """评估安全性"""
        # 中医治疗通常安全性较高
        if "tcm" in str(candidate).lower():
            return 0.9
        return 0.8

    def _evaluate_cost(
        self, candidate: Dict[str, Any], context: DecisionContext
    ) -> float:
        """评估成本"""
        # 简化的成本评估
        if "emergency" in str(candidate):
            return 0.3  # 急诊成本高
        elif "tcm" in str(candidate).lower():
            return 0.7  # 中医成本适中
        return 0.6

    def _evaluate_accessibility(
        self, candidate: Dict[str, Any], context: DecisionContext
    ) -> float:
        """评估可及性"""
        # 基于资源可用性评估
        return self._calculate_resource_availability_score(
            context.resource_availability
        )

    def _evaluate_user_preference(
        self, candidate: Dict[str, Any], context: DecisionContext
    ) -> float:
        """评估用户偏好"""
        # 基于用户偏好设置
        preferences = context.user_preferences

        if preferences.get("prefer_tcm", False) and "tcm" in str(candidate).lower():
            return 0.9
        elif (
            preferences.get("prefer_western", False)
            and "western" in str(candidate).lower()
        ):
            return 0.9

        return 0.6

    async def _execute_fuzzy_action(
        self, action: str, context: DecisionContext
    ) -> Dict[str, Any]:
        """执行模糊动作"""
        if action == "immediate_intervention":
            return {
                "type": "immediate_intervention",
                "priority": "emergency",
                "resources": ["emergency_doctor", "monitoring_equipment"],
                "timeline": "immediate",
            }
        elif action == "standard_treatment":
            return await self._get_constitution_treatment(context.constitution_type)
        elif action == "preventive_care":
            return {
                "type": "preventive_care",
                "recommendations": ["健康检查", "生活方式调整", "定期随访"],
                "timeline": "1-3 months",
            }
        else:
            return {"type": "general_care"}

    def _create_execution_plan(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """创建执行计划"""
        return {
            "steps": [
                {"step": 1, "action": "评估当前状态", "duration": "5-10分钟"},
                {"step": 2, "action": "实施推荐方案", "duration": "30-60分钟"},
                {"step": 3, "action": "监测效果", "duration": "持续"},
                {"step": 4, "action": "调整方案", "duration": "根据需要"},
            ],
            "total_estimated_time": "1-2小时",
            "follow_up_required": True,
            "success_indicators": ["症状改善", "用户满意度提升", "无不良反应"],
        }

    def _predict_outcome(
        self, recommendation: Dict[str, Any], context: DecisionContext
    ) -> Dict[str, Any]:
        """预测结果"""
        return {
            "expected_improvement": "70-80%",
            "time_to_improvement": "1-2周",
            "success_probability": 0.75,
            "potential_benefits": ["症状缓解", "体质改善", "生活质量提升"],
            "monitoring_indicators": ["症状变化", "体征改善", "用户反馈"],
        }

    def _assess_risks(
        self, recommendation: Dict[str, Any], context: DecisionContext
    ) -> Dict[str, Any]:
        """评估风险"""
        return {
            "risk_level": "low",
            "potential_risks": ["轻微不适", "个体差异反应"],
            "mitigation_strategies": ["密切监测", "及时调整", "专业指导"],
            "contraindications": [],
            "warning_signs": ["症状加重", "新症状出现", "不良反应"],
        }

    def _determine_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """确定置信度等级"""
        if confidence_score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _create_default_decision_result(
        self,
        decision_type: DecisionType,
        context: DecisionContext,
        strategy: DecisionStrategy,
    ) -> DecisionResult:
        """创建默认决策结果"""
        return DecisionResult(
            decision_id="",
            decision_type=decision_type,
            strategy_used=strategy,
            recommendation={
                "type": "default",
                "message": "使用默认推荐方案",
                "actions": ["咨询专业医生", "保持健康生活方式"],
            },
            confidence_score=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            reasoning=["无法找到合适的决策规则，使用默认方案"],
            alternative_options=[],
            execution_plan=self._create_execution_plan({}),
            expected_outcome=self._predict_outcome({}, context),
            risk_assessment=self._assess_risks({}, context),
        )

    def _update_decision_stats(
        self, decision_type: DecisionType, result: DecisionResult
    ):
        """更新决策统计信息"""
        if decision_type not in self.decision_stats:
            self.decision_stats[decision_type] = {
                "total_decisions": 0,
                "avg_confidence": 0.0,
                "avg_execution_time": 0.0,
                "strategy_usage": defaultdict(int),
            }

        stats = self.decision_stats[decision_type]
        stats["total_decisions"] += 1
        stats["avg_confidence"] = (
            stats["avg_confidence"] * (stats["total_decisions"] - 1)
            + result.confidence_score
        ) / stats["total_decisions"]
        stats["avg_execution_time"] = (
            stats["avg_execution_time"] * (stats["total_decisions"] - 1)
            + result.execution_time_ms
        ) / stats["total_decisions"]
        stats["strategy_usage"][result.strategy_used.value] += 1

    async def record_feedback(self, feedback: DecisionFeedback):
        """记录决策反馈"""
        try:
            self.feedback_history[feedback.decision_id] = feedback

            # 更新相关规则的成功率
            await self._update_rule_success_rates(feedback)

            logger.info(f"决策反馈已记录: {feedback.decision_id}")

        except Exception as e:
            logger.error(f"记录决策反馈失败: {e}")

    async def _update_rule_success_rates(self, feedback: DecisionFeedback):
        """更新规则成功率"""
        # 查找对应的决策记录
        decision_result = None
        for decision in self.decision_history:
            if decision.decision_id == feedback.decision_id:
                decision_result = decision
                break

        if not decision_result:
            return

        # 更新相关规则的成功率
        success = feedback.effectiveness_score >= 0.7

        for decision_type, rules in self.decision_rules.items():
            for rule in rules:
                if (
                    rule.last_used
                    and (datetime.now() - rule.last_used).total_seconds() < 3600
                ):
                    # 更新成功率
                    rule.usage_count += 1
                    if success:
                        rule.success_rate = (
                            rule.success_rate * (rule.usage_count - 1) + 1.0
                        ) / rule.usage_count
                    else:
                        rule.success_rate = (
                            rule.success_rate
                            * (rule.usage_count - 1)
                            / rule.usage_count
                        )

    def get_decision_statistics(self) -> Dict[str, Any]:
        """获取决策统计信息"""
        return {
            "total_decisions": len(self.decision_history),
            "decision_types": {
                dt.value: stats for dt, stats in self.decision_stats.items()
            },
            "feedback_count": len(self.feedback_history),
            "rule_count": {
                dt.value: len(rules) for dt, rules in self.decision_rules.items()
            },
            "avg_confidence": (
                np.mean([d.confidence_score for d in self.decision_history])
                if self.decision_history
                else 0.0
            ),
            "avg_execution_time": (
                np.mean([d.execution_time_ms for d in self.decision_history])
                if self.decision_history
                else 0.0
            ),
        }

    def get_rule_performance(self) -> Dict[str, Any]:
        """获取规则性能统计"""
        rule_stats = {}

        for decision_type, rules in self.decision_rules.items():
            rule_stats[decision_type.value] = []

            for rule in rules:
                rule_stats[decision_type.value].append(
                    {
                        "rule_id": rule.rule_id,
                        "name": rule.name,
                        "usage_count": rule.usage_count,
                        "success_rate": rule.success_rate,
                        "priority": rule.priority,
                        "confidence_weight": rule.confidence_weight,
                        "last_used": (
                            rule.last_used.isoformat() if rule.last_used else None
                        ),
                    }
                )

        return rule_stats

    async def optimize_rules(self):
        """优化决策规则"""
        try:
            for decision_type, rules in self.decision_rules.items():
                # 根据成功率调整规则权重
                for rule in rules:
                    if rule.usage_count >= 10:  # 有足够的使用数据
                        # 根据成功率调整置信度权重
                        if rule.success_rate > 0.8:
                            rule.confidence_weight = min(
                                rule.confidence_weight * 1.1, 1.0
                            )
                        elif rule.success_rate < 0.5:
                            rule.confidence_weight = max(
                                rule.confidence_weight * 0.9, 0.1
                            )

                # 按成功率和使用频率重新排序规则
                rules.sort(key=lambda r: (r.success_rate, r.usage_count), reverse=True)

            logger.info("决策规则优化完成")

        except Exception as e:
            logger.error(f"决策规则优化失败: {e}")

    async def shutdown(self):
        """关闭决策引擎"""
        try:
            # 保存决策统计信息
            logger.info("决策引擎已关闭")

        except Exception as e:
            logger.error(f"关闭决策引擎失败: {e}")
