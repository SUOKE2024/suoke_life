"""
诊断决策引擎

基于融合诊断结果生成个性化的治疗建议、生活方式指导和随访计划
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..config.settings import get_settings
from ..models.diagnosis_models import (
    DiagnosisRecommendation,
    FusedDiagnosisResult,
    PatientInfo,
)
from ..utils.recommendation_rules import RecommendationRuleEngine
from ..utils.tcm_knowledge import TCMKnowledgeBase

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """建议类型"""

    TREATMENT = "treatment"  # 治疗建议
    LIFESTYLE = "lifestyle"  # 生活方式
    DIET = "diet"  # 饮食建议
    EXERCISE = "exercise"  # 运动建议
    EMOTIONAL = "emotional"  # 情志调节
    FOLLOW_UP = "follow_up"  # 随访建议
    PREVENTION = "prevention"  # 预防建议
    EMERGENCY = "emergency"  # 紧急建议


class PriorityLevel(Enum):
    """优先级级别"""

    CRITICAL = 1  # 紧急
    HIGH = 2  # 高
    MEDIUM = 3  # 中
    LOW = 4  # 低
    INFO = 5  # 信息性


@dataclass
class DecisionContext:
    """决策上下文"""

    patient_info: PatientInfo
    fused_result: FusedDiagnosisResult
    current_season: str = ""
    local_climate: str = ""
    patient_preferences: Dict[str, Any] = field(default_factory=dict)
    medical_history: List[str] = field(default_factory=list)
    current_medications: List[str] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)


@dataclass
class RecommendationItem:
    """建议项目"""

    id: str
    type: RecommendationType
    priority: PriorityLevel
    title: str
    description: str
    rationale: str  # 建议依据
    implementation_steps: List[str]  # 实施步骤
    duration: Optional[str] = None  # 持续时间
    frequency: Optional[str] = None  # 频率
    precautions: List[str] = field(default_factory=list)  # 注意事项
    contraindications: List[str] = field(default_factory=list)  # 禁忌症
    expected_outcomes: List[str] = field(default_factory=list)  # 预期效果
    monitoring_indicators: List[str] = field(default_factory=list)  # 监测指标
    confidence: float = 0.0  # 建议置信度
    evidence_level: str = "expert_opinion"  # 证据级别
    source_diagnoses: List[str] = field(default_factory=list)  # 来源诊断


class DiagnosisDecisionEngine:
    """诊断决策引擎"""

    def __init__(self):
        self.settings = get_settings()
        self.tcm_knowledge = TCMKnowledgeBase()
        self.rule_engine = RecommendationRuleEngine()

        # 决策统计
        self.decision_stats = {
            "total_decisions": 0,
            "recommendations_generated": 0,
            "high_priority_recommendations": 0,
            "average_confidence": 0.0,
        }

        self._initialized = False

    async def initialize(self) -> None:
        """初始化决策引擎"""
        if self._initialized:
            return

        logger.info("初始化诊断决策引擎...")

        try:
            # 初始化中医知识库
            await self.tcm_knowledge.initialize()

            # 初始化规则引擎
            await self.rule_engine.initialize()

            self._initialized = True
            logger.info("诊断决策引擎初始化完成")

        except Exception as e:
            logger.error(f"决策引擎初始化失败: {e}")
            raise

    async def generate_recommendations(
        self,
        fused_result: FusedDiagnosisResult,
        patient_info: PatientInfo,
        context: Optional[DecisionContext] = None,
    ) -> Dict[str, List[str]]:
        """生成建议"""
        if not self._initialized:
            await self.initialize()

        # 创建决策上下文
        if not context:
            context = DecisionContext(
                patient_info=patient_info,
                fused_result=fused_result,
                current_season=self._get_current_season(),
            )

        try:
            # 生成各类建议
            recommendations = []

            # 1. 治疗建议
            treatment_recs = await self._generate_treatment_recommendations(context)
            recommendations.extend(treatment_recs)

            # 2. 生活方式建议
            lifestyle_recs = await self._generate_lifestyle_recommendations(context)
            recommendations.extend(lifestyle_recs)

            # 3. 饮食建议
            diet_recs = await self._generate_diet_recommendations(context)
            recommendations.extend(diet_recs)

            # 4. 运动建议
            exercise_recs = await self._generate_exercise_recommendations(context)
            recommendations.extend(exercise_recs)

            # 5. 情志调节建议
            emotional_recs = await self._generate_emotional_recommendations(context)
            recommendations.extend(emotional_recs)

            # 6. 随访建议
            follow_up_recs = await self._generate_follow_up_recommendations(context)
            recommendations.extend(follow_up_recs)

            # 7. 预防建议
            prevention_recs = await self._generate_prevention_recommendations(context)
            recommendations.extend(prevention_recs)

            # 8. 紧急建议（如果需要）
            emergency_recs = await self._generate_emergency_recommendations(context)
            recommendations.extend(emergency_recs)

            # 过滤和排序建议
            filtered_recommendations = await self._filter_and_rank_recommendations(
                recommendations, context
            )

            # 按类型分组
            grouped_recommendations = self._group_recommendations_by_type(
                filtered_recommendations
            )

            # 转换为简单格式
            simple_recommendations = {}
            for rec_type, recs in grouped_recommendations.items():
                simple_recommendations[rec_type.value] = [
                    rec.description for rec in recs
                ]

            # 更新统计
            self._update_decision_stats(len(recommendations))

            logger.info(f"生成建议完成: 总计{len(recommendations)}条建议")
            return simple_recommendations

        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            raise

    async def _generate_treatment_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成治疗建议"""
        recommendations = []
        fused_result = context.fused_result

        # 基于主要证型生成治疗建议
        if fused_result.primary_syndrome:
            syndrome_treatments = await self.tcm_knowledge.get_syndrome_treatments(
                fused_result.primary_syndrome
            )

            for i, treatment in enumerate(syndrome_treatments[:3]):  # 取前3个治疗建议
                rec = RecommendationItem(
                    id=f"treatment_{i+1}",
                    type=RecommendationType.TREATMENT,
                    priority=PriorityLevel.HIGH if i == 0 else PriorityLevel.MEDIUM,
                    title=f"针对{fused_result.primary_syndrome}的治疗",
                    description=treatment,
                    rationale=f"基于主要证型{fused_result.primary_syndrome}的中医治疗原则",
                    implementation_steps=await self._get_treatment_steps(treatment),
                    duration="2-4周",
                    frequency="每日1-2次",
                    confidence=fused_result.overall_confidence * 0.9,
                    evidence_level="tcm_classic",
                    source_diagnoses=[fused_result.primary_syndrome],
                )

                # 添加注意事项
                rec.precautions = await self.tcm_knowledge.get_treatment_precautions(
                    treatment
                )
                rec.contraindications = (
                    await self.tcm_knowledge.get_treatment_contraindications(
                        treatment, context.patient_info.age, context.patient_info.gender
                    )
                )

                recommendations.append(rec)

        # 基于次要证型生成辅助治疗建议
        for syndrome in fused_result.secondary_syndromes[:2]:  # 取前2个次要证型
            treatments = await self.tcm_knowledge.get_syndrome_treatments(syndrome)
            if treatments:
                rec = RecommendationItem(
                    id=f"treatment_secondary_{syndrome}",
                    type=RecommendationType.TREATMENT,
                    priority=PriorityLevel.MEDIUM,
                    title=f"辅助治疗{syndrome}",
                    description=treatments[0],
                    rationale=f"针对次要证型{syndrome}的辅助治疗",
                    implementation_steps=await self._get_treatment_steps(treatments[0]),
                    duration="1-2周",
                    confidence=fused_result.overall_confidence * 0.7,
                    source_diagnoses=[syndrome],
                )
                recommendations.append(rec)

        return recommendations

    async def _generate_lifestyle_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成生活方式建议"""
        recommendations = []
        fused_result = context.fused_result

        # 基于体质类型生成生活方式建议
        if fused_result.constitution_type:
            lifestyle_advice = await self.tcm_knowledge.get_constitution_lifestyle(
                fused_result.constitution_type
            )

            for i, advice in enumerate(lifestyle_advice[:3]):
                rec = RecommendationItem(
                    id=f"lifestyle_{i+1}",
                    type=RecommendationType.LIFESTYLE,
                    priority=PriorityLevel.MEDIUM,
                    title=f"{fused_result.constitution_type}体质生活调理",
                    description=advice,
                    rationale=f"基于{fused_result.constitution_type}体质特点的生活方式调整",
                    implementation_steps=await self._get_lifestyle_steps(advice),
                    duration="长期坚持",
                    confidence=fused_result.overall_confidence * 0.8,
                    source_diagnoses=[fused_result.constitution_type],
                )
                recommendations.append(rec)

        # 基于季节生成生活方式建议
        seasonal_advice = await self.tcm_knowledge.get_seasonal_lifestyle(
            context.current_season, fused_result.constitution_type
        )

        if seasonal_advice:
            rec = RecommendationItem(
                id="lifestyle_seasonal",
                type=RecommendationType.LIFESTYLE,
                priority=PriorityLevel.LOW,
                title=f"{context.current_season}季养生",
                description=seasonal_advice,
                rationale=f"顺应{context.current_season}季节特点的养生方法",
                implementation_steps=await self._get_seasonal_steps(seasonal_advice),
                duration=f"{context.current_season}季期间",
                confidence=0.7,
            )
            recommendations.append(rec)

        return recommendations

    async def _generate_diet_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成饮食建议"""
        recommendations = []
        fused_result = context.fused_result

        # 基于证型生成饮食建议
        if fused_result.primary_syndrome:
            diet_advice = await self.tcm_knowledge.get_syndrome_diet(
                fused_result.primary_syndrome
            )

            for i, advice in enumerate(diet_advice[:2]):
                rec = RecommendationItem(
                    id=f"diet_{i+1}",
                    type=RecommendationType.DIET,
                    priority=PriorityLevel.MEDIUM,
                    title=f"针对{fused_result.primary_syndrome}的饮食调理",
                    description=advice,
                    rationale=f"基于{fused_result.primary_syndrome}的饮食治疗原则",
                    implementation_steps=await self._get_diet_steps(advice),
                    duration="2-4周",
                    frequency="每日三餐",
                    confidence=fused_result.overall_confidence * 0.8,
                )
                recommendations.append(rec)

        # 基于体质生成饮食建议
        if fused_result.constitution_type:
            constitution_diet = await self.tcm_knowledge.get_constitution_diet(
                fused_result.constitution_type
            )

            if constitution_diet:
                rec = RecommendationItem(
                    id="diet_constitution",
                    type=RecommendationType.DIET,
                    priority=PriorityLevel.MEDIUM,
                    title=f"{fused_result.constitution_type}体质饮食",
                    description=constitution_diet,
                    rationale=f"适合{fused_result.constitution_type}体质的饮食方案",
                    implementation_steps=await self._get_constitution_diet_steps(
                        constitution_diet
                    ),
                    duration="长期坚持",
                    confidence=0.8,
                )
                recommendations.append(rec)

        # 基于季节生成饮食建议
        seasonal_diet = await self.tcm_knowledge.get_seasonal_diet(
            context.current_season
        )
        if seasonal_diet:
            rec = RecommendationItem(
                id="diet_seasonal",
                type=RecommendationType.DIET,
                priority=PriorityLevel.LOW,
                title=f"{context.current_season}季饮食养生",
                description=seasonal_diet,
                rationale=f"顺应{context.current_season}季节的饮食调养",
                implementation_steps=await self._get_seasonal_diet_steps(seasonal_diet),
                duration=f"{context.current_season}季期间",
                confidence=0.7,
            )
            recommendations.append(rec)

        return recommendations

    async def _generate_exercise_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成运动建议"""
        recommendations = []
        fused_result = context.fused_result
        patient_info = context.patient_info

        # 基于体质和年龄生成运动建议
        exercise_advice = await self.tcm_knowledge.get_constitution_exercise(
            fused_result.constitution_type, patient_info.age
        )

        for i, advice in enumerate(exercise_advice[:2]):
            rec = RecommendationItem(
                id=f"exercise_{i+1}",
                type=RecommendationType.EXERCISE,
                priority=PriorityLevel.MEDIUM,
                title=f"适合{fused_result.constitution_type}体质的运动",
                description=advice,
                rationale=f"基于{fused_result.constitution_type}体质和年龄{patient_info.age}岁的运动方案",
                implementation_steps=await self._get_exercise_steps(advice),
                duration="每次30-60分钟",
                frequency="每周3-5次",
                confidence=0.8,
            )

            # 添加运动注意事项
            rec.precautions = await self.tcm_knowledge.get_exercise_precautions(
                advice, patient_info.age, fused_result.health_status
            )

            recommendations.append(rec)

        return recommendations

    async def _generate_emotional_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成情志调节建议"""
        recommendations = []
        fused_result = context.fused_result

        # 基于证型生成情志调节建议
        if fused_result.primary_syndrome:
            emotional_advice = await self.tcm_knowledge.get_syndrome_emotional_care(
                fused_result.primary_syndrome
            )

            if emotional_advice:
                rec = RecommendationItem(
                    id="emotional_syndrome",
                    type=RecommendationType.EMOTIONAL,
                    priority=PriorityLevel.MEDIUM,
                    title=f"针对{fused_result.primary_syndrome}的情志调节",
                    description=emotional_advice,
                    rationale=f"基于{fused_result.primary_syndrome}的情志治疗原则",
                    implementation_steps=await self._get_emotional_steps(
                        emotional_advice
                    ),
                    duration="每日练习",
                    frequency="每次15-30分钟",
                    confidence=fused_result.overall_confidence * 0.7,
                )
                recommendations.append(rec)

        # 基于体质生成情志调节建议
        if fused_result.constitution_type:
            constitution_emotional = (
                await self.tcm_knowledge.get_constitution_emotional_care(
                    fused_result.constitution_type
                )
            )

            if constitution_emotional:
                rec = RecommendationItem(
                    id="emotional_constitution",
                    type=RecommendationType.EMOTIONAL,
                    priority=PriorityLevel.LOW,
                    title=f"{fused_result.constitution_type}体质情志养生",
                    description=constitution_emotional,
                    rationale=f"适合{fused_result.constitution_type}体质的情志调养方法",
                    implementation_steps=await self._get_constitution_emotional_steps(
                        constitution_emotional
                    ),
                    duration="长期坚持",
                    confidence=0.7,
                )
                recommendations.append(rec)

        return recommendations

    async def _generate_follow_up_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成随访建议"""
        recommendations = []
        fused_result = context.fused_result

        # 基于健康状态确定随访频率
        if fused_result.health_status == "需要关注":
            follow_up_interval = "1-2周"
            priority = PriorityLevel.HIGH
        elif fused_result.health_status == "轻度不适":
            follow_up_interval = "2-4周"
            priority = PriorityLevel.MEDIUM
        else:
            follow_up_interval = "1-3个月"
            priority = PriorityLevel.LOW

        rec = RecommendationItem(
            id="follow_up_general",
            type=RecommendationType.FOLLOW_UP,
            priority=priority,
            title="定期随访",
            description=f"建议{follow_up_interval}后进行复查，监测健康状态变化",
            rationale=f"基于当前健康状态'{fused_result.health_status}'的随访计划",
            implementation_steps=[
                "记录症状变化",
                "监测重要指标",
                "评估治疗效果",
                "调整治疗方案",
            ],
            monitoring_indicators=await self._get_monitoring_indicators(fused_result),
            confidence=0.9,
        )
        recommendations.append(rec)

        # 基于风险因素生成特殊随访建议
        for risk_factor in fused_result.risk_factors:
            risk_follow_up = await self.tcm_knowledge.get_risk_follow_up(risk_factor)
            if risk_follow_up:
                rec = RecommendationItem(
                    id=f"follow_up_{risk_factor}",
                    type=RecommendationType.FOLLOW_UP,
                    priority=PriorityLevel.MEDIUM,
                    title=f"{risk_factor}风险监测",
                    description=risk_follow_up,
                    rationale=f"针对{risk_factor}风险因素的专项监测",
                    implementation_steps=await self._get_risk_monitoring_steps(
                        risk_factor
                    ),
                    confidence=0.8,
                )
                recommendations.append(rec)

        return recommendations

    async def _generate_prevention_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成预防建议"""
        recommendations = []
        fused_result = context.fused_result
        patient_info = context.patient_info

        # 基于年龄和性别生成预防建议
        age_prevention = await self.tcm_knowledge.get_age_prevention(
            patient_info.age, patient_info.gender
        )

        for i, prevention in enumerate(age_prevention[:2]):
            rec = RecommendationItem(
                id=f"prevention_{i+1}",
                type=RecommendationType.PREVENTION,
                priority=PriorityLevel.LOW,
                title=f"{patient_info.age}岁{patient_info.gender}性预防保健",
                description=prevention,
                rationale=f"基于年龄{patient_info.age}岁和性别的预防保健措施",
                implementation_steps=await self._get_prevention_steps(prevention),
                duration="长期坚持",
                confidence=0.8,
            )
            recommendations.append(rec)

        # 基于体质生成预防建议
        if fused_result.constitution_type:
            constitution_prevention = (
                await self.tcm_knowledge.get_constitution_prevention(
                    fused_result.constitution_type
                )
            )

            if constitution_prevention:
                rec = RecommendationItem(
                    id="prevention_constitution",
                    type=RecommendationType.PREVENTION,
                    priority=PriorityLevel.LOW,
                    title=f"{fused_result.constitution_type}体质疾病预防",
                    description=constitution_prevention,
                    rationale=f"基于{fused_result.constitution_type}体质特点的疾病预防",
                    implementation_steps=await self._get_constitution_prevention_steps(
                        constitution_prevention
                    ),
                    duration="长期坚持",
                    confidence=0.7,
                )
                recommendations.append(rec)

        return recommendations

    async def _generate_emergency_recommendations(
        self, context: DecisionContext
    ) -> List[RecommendationItem]:
        """生成紧急建议"""
        recommendations = []
        fused_result = context.fused_result

        # 检查是否有需要紧急关注的症状或证型
        emergency_syndromes = await self.tcm_knowledge.get_emergency_syndromes()

        if fused_result.primary_syndrome in emergency_syndromes:
            rec = RecommendationItem(
                id="emergency_syndrome",
                type=RecommendationType.EMERGENCY,
                priority=PriorityLevel.CRITICAL,
                title="紧急医疗建议",
                description=f"检测到{fused_result.primary_syndrome}，建议立即就医",
                rationale=f"{fused_result.primary_syndrome}可能需要紧急医疗干预",
                implementation_steps=[
                    "立即联系医疗机构",
                    "准备相关病历资料",
                    "记录当前症状",
                    "避免自行用药",
                ],
                confidence=fused_result.overall_confidence,
                evidence_level="clinical_guideline",
            )
            recommendations.append(rec)

        # 检查高风险因素
        critical_risks = await self.tcm_knowledge.get_critical_risks()
        for risk in fused_result.risk_factors:
            if risk in critical_risks:
                rec = RecommendationItem(
                    id=f"emergency_risk_{risk}",
                    type=RecommendationType.EMERGENCY,
                    priority=PriorityLevel.HIGH,
                    title=f"{risk}风险警示",
                    description=f"检测到{risk}高风险，建议及时医疗咨询",
                    rationale=f"{risk}风险因素需要专业医疗评估",
                    implementation_steps=await self._get_emergency_steps(risk),
                    confidence=0.9,
                )
                recommendations.append(rec)

        return recommendations

    async def _filter_and_rank_recommendations(
        self, recommendations: List[RecommendationItem], context: DecisionContext
    ) -> List[RecommendationItem]:
        """过滤和排序建议"""
        # 过滤低置信度建议
        filtered = [rec for rec in recommendations if rec.confidence >= 0.5]

        # 检查禁忌症
        safe_recommendations = []
        for rec in filtered:
            is_safe = await self._check_safety(rec, context)
            if is_safe:
                safe_recommendations.append(rec)

        # 按优先级和置信度排序
        sorted_recommendations = sorted(
            safe_recommendations, key=lambda x: (x.priority.value, -x.confidence)
        )

        # 限制每种类型的建议数量
        type_counts = {}
        final_recommendations = []

        for rec in sorted_recommendations:
            count = type_counts.get(rec.type, 0)
            if count < 3:  # 每种类型最多3条建议
                final_recommendations.append(rec)
                type_counts[rec.type] = count + 1

        return final_recommendations

    async def _check_safety(
        self, recommendation: RecommendationItem, context: DecisionContext
    ) -> bool:
        """检查建议安全性"""
        # 检查过敏史
        for allergy in context.allergies:
            if allergy.lower() in recommendation.description.lower():
                return False

        # 检查药物相互作用
        for medication in context.current_medications:
            if await self.tcm_knowledge.has_drug_interaction(
                recommendation.description, medication
            ):
                return False

        # 检查年龄适宜性
        if not await self.tcm_knowledge.is_age_appropriate(
            recommendation.description, context.patient_info.age
        ):
            return False

        return True

    def _group_recommendations_by_type(
        self, recommendations: List[RecommendationItem]
    ) -> Dict[RecommendationType, List[RecommendationItem]]:
        """按类型分组建议"""
        grouped = {}
        for rec in recommendations:
            if rec.type not in grouped:
                grouped[rec.type] = []
            grouped[rec.type].append(rec)

        return grouped

    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"

    # 辅助方法 - 获取实施步骤
    async def _get_treatment_steps(self, treatment: str) -> List[str]:
        """获取治疗实施步骤"""
        return await self.tcm_knowledge.get_treatment_implementation_steps(treatment)

    async def _get_lifestyle_steps(self, advice: str) -> List[str]:
        """获取生活方式实施步骤"""
        return [
            "制定具体的作息时间表",
            "逐步调整生活习惯",
            "记录执行情况",
            "定期评估效果",
        ]

    async def _get_seasonal_steps(self, advice: str) -> List[str]:
        """获取季节养生实施步骤"""
        return ["了解季节特点", "调整作息时间", "适应季节变化", "注意保健要点"]

    async def _get_diet_steps(self, advice: str) -> List[str]:
        """获取饮食实施步骤"""
        return ["制定饮食计划", "选择合适食材", "注意烹饪方法", "监测身体反应"]

    async def _get_constitution_diet_steps(self, advice: str) -> List[str]:
        """获取体质饮食实施步骤"""
        return ["了解体质特点", "选择适宜食物", "避免不宜食物", "调整饮食结构"]

    async def _get_seasonal_diet_steps(self, advice: str) -> List[str]:
        """获取季节饮食实施步骤"""
        return ["选择时令食材", "调整饮食温度", "注意营养搭配", "适应季节需求"]

    async def _get_exercise_steps(self, advice: str) -> List[str]:
        """获取运动实施步骤"""
        return [
            "选择合适的运动项目",
            "制定运动计划",
            "循序渐进增加强度",
            "注意运动安全",
        ]

    async def _get_emotional_steps(self, advice: str) -> List[str]:
        """获取情志调节实施步骤"""
        return ["学习调节方法", "每日练习", "保持积极心态", "寻求专业指导"]

    async def _get_constitution_emotional_steps(self, advice: str) -> List[str]:
        """获取体质情志实施步骤"""
        return [
            "了解体质情志特点",
            "选择适合的调节方法",
            "培养良好心态",
            "维持情志平衡",
        ]

    async def _get_monitoring_indicators(
        self, fused_result: FusedDiagnosisResult
    ) -> List[str]:
        """获取监测指标"""
        indicators = ["症状变化", "精神状态", "睡眠质量", "食欲情况"]

        if fused_result.primary_syndrome:
            syndrome_indicators = (
                await self.tcm_knowledge.get_syndrome_monitoring_indicators(
                    fused_result.primary_syndrome
                )
            )
            indicators.extend(syndrome_indicators)

        return list(set(indicators))

    async def _get_risk_monitoring_steps(self, risk_factor: str) -> List[str]:
        """获取风险监测步骤"""
        return await self.tcm_knowledge.get_risk_monitoring_steps(risk_factor)

    async def _get_prevention_steps(self, prevention: str) -> List[str]:
        """获取预防实施步骤"""
        return ["了解预防要点", "制定预防计划", "定期健康检查", "维持健康生活方式"]

    async def _get_constitution_prevention_steps(self, prevention: str) -> List[str]:
        """获取体质预防实施步骤"""
        return ["了解体质易患疾病", "针对性预防措施", "定期体质调理", "监测健康指标"]

    async def _get_emergency_steps(self, risk: str) -> List[str]:
        """获取紧急处理步骤"""
        return ["立即停止当前活动", "联系医疗机构", "记录症状表现", "等待专业指导"]

    def _update_decision_stats(self, recommendations_count: int) -> None:
        """更新决策统计"""
        self.decision_stats["total_decisions"] += 1
        self.decision_stats["recommendations_generated"] += recommendations_count

    async def get_decision_stats(self) -> Dict[str, Any]:
        """获取决策统计"""
        return self.decision_stats.copy()

    async def close(self) -> None:
        """关闭决策引擎"""
        logger.info("关闭诊断决策引擎...")

        if hasattr(self, "tcm_knowledge"):
            await self.tcm_knowledge.close()
        if hasattr(self, "rule_engine"):
            await self.rule_engine.close()

        logger.info("诊断决策引擎已关闭")
