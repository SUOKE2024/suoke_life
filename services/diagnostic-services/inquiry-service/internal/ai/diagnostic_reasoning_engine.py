#!/usr/bin/env python3

"""
智能诊断推理引擎

该模块实现基于症状的智能诊断推理，包括疾病概率计算、
诊断建议生成、风险评估和治疗建议，为问诊服务提供专业的诊断支持。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid

from loguru import logger

from ..common.base import BaseService
from ..common.cache import cached
from ..common.exceptions import InquiryServiceError
from ..common.metrics import counter, memory_optimized, timer


class DiagnosisConfidence(Enum):
    """诊断置信度"""

    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskLevel(Enum):
    """风险等级"""

    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(Enum):
    """建议类型"""

    IMMEDIATE_MEDICAL_ATTENTION = "immediate_medical_attention"
    SCHEDULE_APPOINTMENT = "schedule_appointment"
    MONITOR_SYMPTOMS = "monitor_symptoms"
    LIFESTYLE_CHANGES = "lifestyle_changes"
    MEDICATION = "medication"
    FURTHER_TESTING = "further_testing"


@dataclass
class Symptom:
    """症状"""

    name: str
    severity: float  # 0-10
    duration: str
    frequency: str
    location: str = ""
    quality: str = ""
    associated_factors: list[str] = field(default_factory=list)
    relieving_factors: list[str] = field(default_factory=list)
    aggravating_factors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Disease:
    """疾病"""

    name: str
    icd_code: str
    category: str
    typical_symptoms: list[str]
    required_symptoms: list[str] = field(default_factory=list)
    exclusion_symptoms: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    prevalence: float = 0.0
    severity_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosisResult:
    """诊断结果"""

    disease: Disease
    probability: float
    confidence: DiagnosisConfidence
    supporting_symptoms: list[str]
    missing_symptoms: list[str]
    risk_level: RiskLevel
    reasoning: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Recommendation:
    """建议"""

    type: RecommendationType
    description: str
    urgency: int  # 1-10
    rationale: str
    specific_actions: list[str] = field(default_factory=list)
    timeframe: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosticAssessment:
    """诊断评估"""

    patient_id: str
    assessment_id: str
    symptoms: list[Symptom]
    differential_diagnoses: list[DiagnosisResult]
    primary_diagnosis: DiagnosisResult | None
    recommendations: list[Recommendation]
    overall_risk_level: RiskLevel
    confidence_score: float
    reasoning_summary: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class DiagnosticReasoningEngine(BaseService):
    """智能诊断推理引擎"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化诊断推理引擎

        Args:
            config: 配置信息
        """
        super().__init__(config)

        # 推理配置
        self.reasoning_config = {
            "max_differential_diagnoses": 10,
            "min_probability_threshold": 0.1,
            "confidence_threshold": 0.7,
            "risk_assessment_enabled": True,
            "bayesian_inference_enabled": True,
            "symptom_weighting_enabled": True,
            "temporal_reasoning_enabled": True,
        }

        # 疾病知识库
        self.disease_database = self._initialize_disease_database()

        # 症状权重映射
        self.symptom_weights = self._initialize_symptom_weights()

        # 诊断规则
        self.diagnostic_rules = self._initialize_diagnostic_rules()

        # 风险评估规则
        self.risk_assessment_rules = self._initialize_risk_assessment_rules()

        # 缓存的评估结果
        self.assessment_cache: dict[str, DiagnosticAssessment] = {}

        # 性能统计
        self.stats = {
            "total_assessments": 0,
            "successful_diagnoses": 0,
            "high_confidence_diagnoses": 0,
            "emergency_cases_detected": 0,
            "average_processing_time": 0.0,
            "accuracy_score": 0.0,
            "cache_hits": 0,
        }

        logger.info("智能诊断推理引擎初始化完成")

    def _initialize_disease_database(self) -> dict[str, Disease]:
        """初始化疾病数据库"""
        diseases = {
            "common_cold": Disease(
                name="普通感冒",
                icd_code="J00",
                category="呼吸系统疾病",
                typical_symptoms=["鼻塞", "流鼻涕", "咳嗽", "喉咙痛", "轻微发热"],
                required_symptoms=["鼻塞", "流鼻涕"],
                prevalence=0.15,
                severity_score=2.0,
            ),
            "influenza": Disease(
                name="流行性感冒",
                icd_code="J11",
                category="呼吸系统疾病",
                typical_symptoms=["发热", "头痛", "肌肉酸痛", "乏力", "咳嗽", "喉咙痛"],
                required_symptoms=["发热", "肌肉酸痛"],
                prevalence=0.08,
                severity_score=4.0,
            ),
            "tension_headache": Disease(
                name="紧张性头痛",
                icd_code="G44.2",
                category="神经系统疾病",
                typical_symptoms=["头痛", "颈部僵硬", "压迫感", "双侧疼痛"],
                required_symptoms=["头痛"],
                exclusion_symptoms=["发热", "呕吐", "视觉障碍"],
                prevalence=0.12,
                severity_score=3.0,
            ),
            "migraine": Disease(
                name="偏头痛",
                icd_code="G43",
                category="神经系统疾病",
                typical_symptoms=["单侧头痛", "搏动性疼痛", "恶心", "光敏感", "声敏感"],
                required_symptoms=["头痛"],
                prevalence=0.06,
                severity_score=6.0,
            ),
            "gastroenteritis": Disease(
                name="急性胃肠炎",
                icd_code="K59.1",
                category="消化系统疾病",
                typical_symptoms=["腹痛", "腹泻", "恶心", "呕吐", "发热"],
                required_symptoms=["腹痛", "腹泻"],
                prevalence=0.10,
                severity_score=4.0,
            ),
            "hypertension": Disease(
                name="高血压",
                icd_code="I10",
                category="循环系统疾病",
                typical_symptoms=["头痛", "头晕", "心悸", "疲劳"],
                risk_factors=["年龄", "肥胖", "吸烟", "家族史"],
                prevalence=0.25,
                severity_score=5.0,
            ),
        }

        return diseases

    def _initialize_symptom_weights(self) -> dict[str, float]:
        """初始化症状权重"""
        return {
            # 高权重症状（特异性强）
            "胸痛": 0.9,
            "呼吸困难": 0.9,
            "意识障碍": 0.95,
            "剧烈头痛": 0.85,
            "大出血": 0.95,
            # 中等权重症状
            "发热": 0.7,
            "头痛": 0.6,
            "腹痛": 0.6,
            "咳嗽": 0.5,
            "恶心": 0.5,
            # 低权重症状（常见但特异性低）
            "乏力": 0.3,
            "头晕": 0.4,
            "失眠": 0.3,
            "食欲不振": 0.3,
            "鼻塞": 0.4,
        }

    def _initialize_diagnostic_rules(self) -> list[dict[str, Any]]:
        """初始化诊断规则"""
        return [
            {
                "name": "emergency_chest_pain",
                "condition": lambda symptoms: any(
                    s.name == "胸痛" and s.severity >= 7 for s in symptoms
                ),
                "action": "immediate_medical_attention",
                "priority": 10,
            },
            {
                "name": "severe_headache_with_fever",
                "condition": lambda symptoms: (
                    any(s.name == "头痛" and s.severity >= 8 for s in symptoms)
                    and any(s.name == "发热" for s in symptoms)
                ),
                "action": "urgent_evaluation",
                "priority": 9,
            },
            {
                "name": "respiratory_distress",
                "condition": lambda symptoms: any(
                    s.name == "呼吸困难" and s.severity >= 6 for s in symptoms
                ),
                "action": "immediate_medical_attention",
                "priority": 10,
            },
        ]

    def _initialize_risk_assessment_rules(self) -> dict[str, dict[str, Any]]:
        """初始化风险评估规则"""
        return {
            "age_risk": {
                "high_risk_age": [0, 5, 65, 100],  # 儿童和老年人
                "risk_multiplier": 1.5,
            },
            "symptom_severity": {
                "critical_threshold": 8,
                "high_threshold": 6,
                "moderate_threshold": 4,
            },
            "symptom_combinations": {
                "chest_pain_shortness": ["胸痛", "呼吸困难"],
                "headache_fever_stiff_neck": ["头痛", "发热", "颈部僵硬"],
                "abdominal_pain_vomiting": ["腹痛", "呕吐"],
            },
        }

    @timer("diagnostic.perform_assessment")
    @counter("diagnostic.assessments_performed")
    async def perform_diagnostic_assessment(
        self,
        patient_id: str,
        symptoms: list[Symptom],
        patient_context: dict[str, Any] | None = None,
    ) -> DiagnosticAssessment:
        """
        执行诊断评估

        Args:
            patient_id: 患者ID
            symptoms: 症状列表
            patient_context: 患者上下文信息

        Returns:
            诊断评估结果
        """
        try:
            start_time = datetime.now()

            # 生成评估ID
            assessment_id = str(uuid.uuid4())

            # 症状预处理和验证
            processed_symptoms = await self._preprocess_symptoms(symptoms)

            # 计算差异诊断
            differential_diagnoses = await self._calculate_differential_diagnoses(
                processed_symptoms, patient_context
            )

            # 确定主要诊断
            primary_diagnosis = await self._determine_primary_diagnosis(
                differential_diagnoses
            )

            # 风险评估
            overall_risk_level = await self._assess_overall_risk(
                processed_symptoms, differential_diagnoses, patient_context
            )

            # 生成建议
            recommendations = await self._generate_recommendations(
                processed_symptoms,
                differential_diagnoses,
                overall_risk_level,
                patient_context,
            )

            # 计算置信度
            confidence_score = await self._calculate_overall_confidence(
                differential_diagnoses, processed_symptoms
            )

            # 生成推理摘要
            reasoning_summary = await self._generate_reasoning_summary(
                processed_symptoms, differential_diagnoses, primary_diagnosis
            )

            # 创建评估结果
            assessment = DiagnosticAssessment(
                patient_id=patient_id,
                assessment_id=assessment_id,
                symptoms=processed_symptoms,
                differential_diagnoses=differential_diagnoses,
                primary_diagnosis=primary_diagnosis,
                recommendations=recommendations,
                overall_risk_level=overall_risk_level,
                confidence_score=confidence_score,
                reasoning_summary=reasoning_summary,
                metadata={
                    "processing_time_ms": (datetime.now() - start_time).total_seconds()
                    * 1000,
                    "patient_context": patient_context or {},
                    "engine_version": "1.0.0",
                },
            )

            # 缓存结果
            self.assessment_cache[assessment_id] = assessment

            # 更新统计
            self._update_assessment_stats(assessment)

            logger.info(f"诊断评估完成: {assessment_id}")
            return assessment

        except Exception as e:
            logger.error(f"诊断评估失败: {e}")
            raise InquiryServiceError(f"诊断评估失败: {e}")

    async def _preprocess_symptoms(self, symptoms: list[Symptom]) -> list[Symptom]:
        """预处理症状"""
        processed_symptoms = []

        for symptom in symptoms:
            # 标准化症状名称
            normalized_name = await self._normalize_symptom_name(symptom.name)

            # 验证严重程度
            severity = max(0, min(10, symptom.severity))

            # 创建处理后的症状
            processed_symptom = Symptom(
                name=normalized_name,
                severity=severity,
                duration=symptom.duration,
                frequency=symptom.frequency,
                location=symptom.location,
                quality=symptom.quality,
                associated_factors=symptom.associated_factors,
                relieving_factors=symptom.relieving_factors,
                aggravating_factors=symptom.aggravating_factors,
                metadata=symptom.metadata,
            )

            processed_symptoms.append(processed_symptom)

        return processed_symptoms

    async def _normalize_symptom_name(self, symptom_name: str) -> str:
        """标准化症状名称"""
        # 症状名称映射
        symptom_mapping = {
            "头疼": "头痛",
            "肚子疼": "腹痛",
            "拉肚子": "腹泻",
            "发烧": "发热",
            "咳嗽有痰": "咳嗽",
            "喉咙疼": "喉咙痛",
            "流鼻水": "流鼻涕",
        }

        return symptom_mapping.get(symptom_name, symptom_name)

    async def _calculate_differential_diagnoses(
        self, symptoms: list[Symptom], patient_context: dict[str, Any] | None
    ) -> list[DiagnosisResult]:
        """计算差异诊断"""
        diagnoses = []
        symptom_names = [s.name for s in symptoms]

        for disease_id, disease in self.disease_database.items():
            # 计算疾病概率
            probability = await self._calculate_disease_probability(
                disease, symptoms, patient_context
            )

            if probability >= self.reasoning_config["min_probability_threshold"]:
                # 确定置信度
                confidence = await self._determine_confidence_level(
                    probability, disease, symptoms
                )

                # 识别支持和缺失的症状
                supporting_symptoms = [
                    s for s in symptom_names if s in disease.typical_symptoms
                ]
                missing_symptoms = [
                    s for s in disease.typical_symptoms if s not in symptom_names
                ]

                # 评估风险等级
                risk_level = await self._assess_disease_risk(
                    disease, symptoms, patient_context
                )

                # 生成推理说明
                reasoning = await self._generate_disease_reasoning(
                    disease, symptoms, probability, supporting_symptoms
                )

                diagnosis_result = DiagnosisResult(
                    disease=disease,
                    probability=probability,
                    confidence=confidence,
                    supporting_symptoms=supporting_symptoms,
                    missing_symptoms=missing_symptoms,
                    risk_level=risk_level,
                    reasoning=reasoning,
                )

                diagnoses.append(diagnosis_result)

        # 按概率排序
        diagnoses.sort(key=lambda x: x.probability, reverse=True)

        # 限制数量
        max_diagnoses = self.reasoning_config["max_differential_diagnoses"]
        return diagnoses[:max_diagnoses]

    async def _calculate_disease_probability(
        self,
        disease: Disease,
        symptoms: list[Symptom],
        patient_context: dict[str, Any] | None,
    ) -> float:
        """计算疾病概率"""
        if not self.reasoning_config["bayesian_inference_enabled"]:
            return await self._calculate_simple_probability(disease, symptoms)

        # 贝叶斯推理
        prior_probability = disease.prevalence

        # 计算似然度
        likelihood = await self._calculate_likelihood(disease, symptoms)

        # 考虑患者上下文
        context_factor = await self._calculate_context_factor(disease, patient_context)

        # 贝叶斯公式：P(Disease|Symptoms) ∝ P(Symptoms|Disease) * P(Disease) * Context
        posterior_probability = likelihood * prior_probability * context_factor

        # 归一化到0-1范围
        return min(1.0, posterior_probability)

    async def _calculate_simple_probability(
        self, disease: Disease, symptoms: list[Symptom]
    ) -> float:
        """计算简单概率（基于症状匹配）"""
        symptom_names = [s.name for s in symptoms]

        # 检查必需症状
        if disease.required_symptoms:
            required_present = all(
                req in symptom_names for req in disease.required_symptoms
            )
            if not required_present:
                return 0.0

        # 检查排除症状
        if disease.exclusion_symptoms:
            exclusion_present = any(
                excl in symptom_names for excl in disease.exclusion_symptoms
            )
            if exclusion_present:
                return 0.0

        # 计算匹配度
        matching_symptoms = len(
            [s for s in symptom_names if s in disease.typical_symptoms]
        )
        total_typical_symptoms = len(disease.typical_symptoms)

        if total_typical_symptoms == 0:
            return 0.0

        match_ratio = matching_symptoms / total_typical_symptoms

        # 考虑症状权重
        if self.reasoning_config["symptom_weighting_enabled"]:
            weighted_score = 0.0
            total_weight = 0.0

            for symptom in symptoms:
                if symptom.name in disease.typical_symptoms:
                    weight = self.symptom_weights.get(symptom.name, 0.5)
                    severity_factor = symptom.severity / 10.0
                    weighted_score += weight * severity_factor
                    total_weight += weight

            if total_weight > 0:
                match_ratio = weighted_score / total_weight

        return match_ratio

    async def _calculate_likelihood(
        self, disease: Disease, symptoms: list[Symptom]
    ) -> float:
        """计算似然度 P(Symptoms|Disease)"""
        likelihood = 1.0

        for symptom in symptoms:
            if symptom.name in disease.typical_symptoms:
                # 症状存在的概率（基于疾病）
                symptom_probability = 0.8  # 简化实现
                severity_factor = symptom.severity / 10.0
                likelihood *= symptom_probability * severity_factor
            else:
                # 症状不典型的惩罚
                likelihood *= 0.5

        return likelihood

    async def _calculate_context_factor(
        self, disease: Disease, patient_context: dict[str, Any] | None
    ) -> float:
        """计算上下文因子"""
        if not patient_context:
            return 1.0

        context_factor = 1.0

        # 年龄因子
        age = patient_context.get("age", 0)
        if disease.name == "高血压" and age > 50:
            context_factor *= 1.5
        elif disease.name == "普通感冒" and age < 18:
            context_factor *= 1.2

        # 性别因子
        gender = patient_context.get("gender", "")
        if disease.name == "偏头痛" and gender == "female":
            context_factor *= 1.3

        # 既往病史
        medical_history = patient_context.get("medical_history", [])
        if disease.name in medical_history:
            context_factor *= 1.4

        # 家族史
        family_history = patient_context.get("family_history", [])
        if disease.name in family_history:
            context_factor *= 1.2

        return context_factor

    async def _determine_confidence_level(
        self, probability: float, disease: Disease, symptoms: list[Symptom]
    ) -> DiagnosisConfidence:
        """确定置信度等级"""
        # 基于概率的基础置信度
        if probability >= 0.8:
            base_confidence = DiagnosisConfidence.VERY_HIGH
        elif probability >= 0.6:
            base_confidence = DiagnosisConfidence.HIGH
        elif probability >= 0.4:
            base_confidence = DiagnosisConfidence.MODERATE
        elif probability >= 0.2:
            base_confidence = DiagnosisConfidence.LOW
        else:
            base_confidence = DiagnosisConfidence.VERY_LOW

        # 考虑症状的特异性
        symptom_names = [s.name for s in symptoms]
        specific_symptoms = [s for s in symptom_names if s in disease.required_symptoms]

        if specific_symptoms and base_confidence.value in ["moderate", "high"]:
            # 提升置信度
            confidence_levels = list(DiagnosisConfidence)
            current_index = confidence_levels.index(base_confidence)
            if current_index < len(confidence_levels) - 1:
                return confidence_levels[current_index + 1]

        return base_confidence

    async def _assess_disease_risk(
        self,
        disease: Disease,
        symptoms: list[Symptom],
        patient_context: dict[str, Any] | None,
    ) -> RiskLevel:
        """评估疾病风险等级"""
        # 基于疾病严重程度的基础风险
        base_risk = RiskLevel.LOW

        if disease.severity_score >= 8:
            base_risk = RiskLevel.CRITICAL
        elif disease.severity_score >= 6:
            base_risk = RiskLevel.HIGH
        elif disease.severity_score >= 4:
            base_risk = RiskLevel.MODERATE
        elif disease.severity_score >= 2:
            base_risk = RiskLevel.LOW
        else:
            base_risk = RiskLevel.MINIMAL

        # 考虑症状严重程度
        max_severity = max([s.severity for s in symptoms], default=0)
        if max_severity >= 8:
            base_risk = RiskLevel.CRITICAL
        elif max_severity >= 6 and base_risk.value in ["minimal", "low"]:
            base_risk = RiskLevel.MODERATE

        # 考虑患者年龄
        if patient_context:
            age = patient_context.get("age", 0)
            if (age < 5 or age > 65) and base_risk.value in ["minimal", "low"]:
                # 提升风险等级
                risk_levels = list(RiskLevel)
                current_index = risk_levels.index(base_risk)
                if current_index < len(risk_levels) - 1:
                    base_risk = risk_levels[current_index + 1]

        return base_risk

    async def _generate_disease_reasoning(
        self,
        disease: Disease,
        symptoms: list[Symptom],
        probability: float,
        supporting_symptoms: list[str],
    ) -> str:
        """生成疾病推理说明"""
        reasoning_parts = []

        # 概率说明
        reasoning_parts.append(
            f"基于症状分析，{disease.name}的可能性为{probability:.1%}"
        )

        # 支持症状
        if supporting_symptoms:
            reasoning_parts.append(
                f"支持该诊断的症状包括：{', '.join(supporting_symptoms)}"
            )

        # 严重程度
        max_severity = max([s.severity for s in symptoms], default=0)
        if max_severity >= 7:
            reasoning_parts.append("症状严重程度较高，需要密切关注")

        # 疾病特点
        if disease.category:
            reasoning_parts.append(f"该疾病属于{disease.category}")

        return "。".join(reasoning_parts) + "。"

    async def _determine_primary_diagnosis(
        self, differential_diagnoses: list[DiagnosisResult]
    ) -> DiagnosisResult | None:
        """确定主要诊断"""
        if not differential_diagnoses:
            return None

        # 选择概率最高且置信度足够的诊断
        for diagnosis in differential_diagnoses:
            if diagnosis.probability >= self.reasoning_config[
                "confidence_threshold"
            ] and diagnosis.confidence.value in ["high", "very_high"]:
                return diagnosis

        # 如果没有高置信度的诊断，返回概率最高的
        return differential_diagnoses[0]

    async def _assess_overall_risk(
        self,
        symptoms: list[Symptom],
        differential_diagnoses: list[DiagnosisResult],
        patient_context: dict[str, Any] | None,
    ) -> RiskLevel:
        """评估总体风险等级"""
        # 检查紧急症状
        emergency_symptoms = ["胸痛", "呼吸困难", "意识障碍", "大出血"]
        has_emergency = any(
            s.name in emergency_symptoms and s.severity >= 7 for s in symptoms
        )

        if has_emergency:
            return RiskLevel.CRITICAL

        # 基于最高风险诊断
        if differential_diagnoses:
            max_risk = max(
                [d.risk_level for d in differential_diagnoses],
                key=lambda x: list(RiskLevel).index(x),
            )
            return max_risk

        # 基于症状严重程度
        max_severity = max([s.severity for s in symptoms], default=0)
        if max_severity >= 8:
            return RiskLevel.HIGH
        elif max_severity >= 6:
            return RiskLevel.MODERATE
        elif max_severity >= 4:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    async def _generate_recommendations(
        self,
        symptoms: list[Symptom],
        differential_diagnoses: list[DiagnosisResult],
        overall_risk_level: RiskLevel,
        patient_context: dict[str, Any] | None,
    ) -> list[Recommendation]:
        """生成建议"""
        recommendations = []

        # 基于风险等级的建议
        if overall_risk_level == RiskLevel.CRITICAL:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.IMMEDIATE_MEDICAL_ATTENTION,
                    description="立即就医",
                    urgency=10,
                    rationale="症状提示可能存在紧急情况",
                    specific_actions=["立即前往急诊科", "拨打120急救电话"],
                    timeframe="立即",
                )
            )

        elif overall_risk_level == RiskLevel.HIGH:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.SCHEDULE_APPOINTMENT,
                    description="尽快就医",
                    urgency=8,
                    rationale="症状需要专业医生评估",
                    specific_actions=["24小时内预约医生", "密切监测症状变化"],
                    timeframe="24小时内",
                )
            )

        elif overall_risk_level == RiskLevel.MODERATE:
            recommendations.append(
                Recommendation(
                    type=RecommendationType.MONITOR_SYMPTOMS,
                    description="监测症状并考虑就医",
                    urgency=5,
                    rationale="症状需要观察，如有恶化应及时就医",
                    specific_actions=["记录症状变化", "如症状加重立即就医"],
                    timeframe="48-72小时",
                )
            )

        # 基于具体诊断的建议
        if differential_diagnoses:
            primary_diagnosis = differential_diagnoses[0]

            if primary_diagnosis.disease.name == "普通感冒":
                recommendations.append(
                    Recommendation(
                        type=RecommendationType.LIFESTYLE_CHANGES,
                        description="休息和对症治疗",
                        urgency=3,
                        rationale="普通感冒通常可以自愈",
                        specific_actions=["充分休息", "多喝水", "保持室内湿度"],
                        timeframe="7-10天",
                    )
                )

            elif primary_diagnosis.disease.name == "高血压":
                recommendations.append(
                    Recommendation(
                        type=RecommendationType.FURTHER_TESTING,
                        description="血压监测和进一步检查",
                        urgency=6,
                        rationale="需要确认高血压诊断并评估并发症",
                        specific_actions=["定期测量血压", "心电图检查", "血液检查"],
                        timeframe="1-2周内",
                    )
                )

        # 基于症状的特定建议
        for symptom in symptoms:
            if symptom.name == "头痛" and symptom.severity >= 6:
                recommendations.append(
                    Recommendation(
                        type=RecommendationType.MONITOR_SYMPTOMS,
                        description="头痛症状监测",
                        urgency=4,
                        rationale="严重头痛需要密切观察",
                        specific_actions=["记录头痛发作时间和诱因", "避免已知诱发因素"],
                        timeframe="持续监测",
                    )
                )

        # 按紧急程度排序
        recommendations.sort(key=lambda x: x.urgency, reverse=True)

        return recommendations

    async def _calculate_overall_confidence(
        self, differential_diagnoses: list[DiagnosisResult], symptoms: list[Symptom]
    ) -> float:
        """计算总体置信度"""
        if not differential_diagnoses:
            return 0.0

        # 基于最高概率诊断的置信度
        primary_confidence = differential_diagnoses[0].probability

        # 考虑诊断数量的影响
        diagnosis_count_factor = 1.0 - (len(differential_diagnoses) - 1) * 0.05
        diagnosis_count_factor = max(0.5, diagnosis_count_factor)

        # 考虑症状完整性
        symptom_completeness = min(1.0, len(symptoms) / 5.0)  # 假设5个症状为完整

        overall_confidence = (
            primary_confidence * diagnosis_count_factor * symptom_completeness
        )

        return min(1.0, overall_confidence)

    async def _generate_reasoning_summary(
        self,
        symptoms: list[Symptom],
        differential_diagnoses: list[DiagnosisResult],
        primary_diagnosis: DiagnosisResult | None,
    ) -> str:
        """生成推理摘要"""
        summary_parts = []

        # 症状总结
        symptom_names = [s.name for s in symptoms]
        summary_parts.append(f"患者主要症状包括：{', '.join(symptom_names)}")

        # 主要诊断
        if primary_diagnosis:
            summary_parts.append(
                f"最可能的诊断是{primary_diagnosis.disease.name}，"
                f"可能性为{primary_diagnosis.probability:.1%}"
            )

        # 差异诊断
        if len(differential_diagnoses) > 1:
            other_diagnoses = [d.disease.name for d in differential_diagnoses[1:3]]
            summary_parts.append(
                f"需要考虑的其他可能诊断包括：{', '.join(other_diagnoses)}"
            )

        # 风险评估
        max_severity = max([s.severity for s in symptoms], default=0)
        if max_severity >= 7:
            summary_parts.append("症状较为严重，建议及时就医")

        return "。".join(summary_parts) + "。"

    def _update_assessment_stats(self, assessment: DiagnosticAssessment):
        """更新评估统计"""
        self.stats["total_assessments"] += 1

        if assessment.primary_diagnosis:
            self.stats["successful_diagnoses"] += 1

            if assessment.primary_diagnosis.confidence.value in ["high", "very_high"]:
                self.stats["high_confidence_diagnoses"] += 1

        if assessment.overall_risk_level == RiskLevel.CRITICAL:
            self.stats["emergency_cases_detected"] += 1

        # 更新平均处理时间
        processing_time = assessment.metadata.get("processing_time_ms", 0)
        current_avg = self.stats["average_processing_time"]
        total_assessments = self.stats["total_assessments"]

        if total_assessments == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            self.stats["average_processing_time"] = (
                current_avg * (total_assessments - 1) + processing_time
            ) / total_assessments

    @cached(ttl=600)
    async def get_assessment_by_id(
        self, assessment_id: str
    ) -> DiagnosticAssessment | None:
        """根据ID获取评估结果"""
        return self.assessment_cache.get(assessment_id)

    @memory_optimized
    async def get_patient_assessment_history(
        self, patient_id: str, limit: int = 10
    ) -> list[DiagnosticAssessment]:
        """获取患者评估历史"""
        patient_assessments = [
            assessment
            for assessment in self.assessment_cache.values()
            if assessment.patient_id == patient_id
        ]

        # 按时间排序
        patient_assessments.sort(key=lambda x: x.timestamp, reverse=True)

        return patient_assessments[:limit]

    async def update_disease_database(self, disease_data: dict[str, Disease]):
        """更新疾病数据库"""
        self.disease_database.update(disease_data)
        logger.info(f"疾病数据库已更新，新增 {len(disease_data)} 个疾病")

    async def get_service_stats(self) -> dict[str, Any]:
        """获取服务统计"""
        return {
            **self.stats,
            "disease_count": len(self.disease_database),
            "cached_assessments": len(self.assessment_cache),
            "success_rate": (
                self.stats["successful_diagnoses"]
                / max(self.stats["total_assessments"], 1)
            ),
            "high_confidence_rate": (
                self.stats["high_confidence_diagnoses"]
                / max(self.stats["successful_diagnoses"], 1)
            ),
            "emergency_detection_rate": (
                self.stats["emergency_cases_detected"]
                / max(self.stats["total_assessments"], 1)
            ),
        }
