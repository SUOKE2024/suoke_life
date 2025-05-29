#!/usr/bin/env python3

"""
智能问诊流程管理器

该模块实现智能化的问诊流程管理，包括自适应问诊流程、动态问题生成、
智能决策树和个性化问诊策略。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from loguru import logger
import numpy as np

from ..common.base import BaseService
from ..common.cache import cached
from ..common.exceptions import InquiryServiceError
from ..common.metrics import counter, memory_optimized, timer


class FlowStage(Enum):
    """问诊流程阶段"""

    INITIALIZATION = "initialization"  # 初始化
    CHIEF_COMPLAINT = "chief_complaint"  # 主诉收集
    SYMPTOM_EXPLORATION = "symptom_exploration"  # 症状探索
    SYSTEM_REVIEW = "system_review"  # 系统回顾
    HISTORY_TAKING = "history_taking"  # 病史采集
    RISK_ASSESSMENT = "risk_assessment"  # 风险评估
    CONCLUSION = "conclusion"  # 结论总结


class QuestionPriority(Enum):
    """问题优先级"""

    CRITICAL = "critical"  # 关键问题
    HIGH = "high"  # 高优先级
    MEDIUM = "medium"  # 中等优先级
    LOW = "low"  # 低优先级
    OPTIONAL = "optional"  # 可选问题


class DecisionType(Enum):
    """决策类型"""

    CONTINUE_CURRENT = "continue_current"  # 继续当前阶段
    ADVANCE_STAGE = "advance_stage"  # 进入下一阶段
    BRANCH_EXPLORATION = "branch_exploration"  # 分支探索
    EMERGENCY_PROTOCOL = "emergency_protocol"  # 紧急处理
    CONCLUDE_INQUIRY = "conclude_inquiry"  # 结束问诊


@dataclass
class QuestionTemplate:
    """问题模板"""

    id: str
    template: str
    category: str
    priority: QuestionPriority
    conditions: dict[str, Any]
    follow_up_rules: list[dict[str, Any]]
    expected_answer_type: str
    validation_rules: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowDecision:
    """流程决策"""

    decision_type: DecisionType
    next_stage: FlowStage | None
    next_questions: list[str]
    reasoning: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InquiryContext:
    """问诊上下文"""

    session_id: str
    patient_id: str
    current_stage: FlowStage
    collected_data: dict[str, Any]
    symptom_profile: dict[str, Any]
    risk_factors: list[str]
    answered_questions: set[str]
    skipped_questions: set[str]
    confidence_scores: dict[str, float]
    stage_history: list[tuple[FlowStage, datetime]]
    metadata: dict[str, Any] = field(default_factory=dict)


class IntelligentFlowManager(BaseService):
    """智能问诊流程管理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化智能流程管理器

        Args:
            config: 配置信息
        """
        super().__init__(config)

        # 问题模板库
        self.question_templates: dict[str, QuestionTemplate] = {}

        # 决策规则
        self.decision_rules: dict[FlowStage, list[dict[str, Any]]] = {}

        # 流程配置
        self.flow_config = {
            "max_questions_per_stage": {
                FlowStage.CHIEF_COMPLAINT: 5,
                FlowStage.SYMPTOM_EXPLORATION: 15,
                FlowStage.SYSTEM_REVIEW: 10,
                FlowStage.HISTORY_TAKING: 8,
                FlowStage.RISK_ASSESSMENT: 5,
            },
            "min_confidence_threshold": 0.7,
            "emergency_keywords": [
                "胸痛",
                "呼吸困难",
                "意识丧失",
                "大出血",
                "剧烈头痛",
                "高热",
                "抽搐",
                "昏迷",
                "休克",
                "心悸",
            ],
            "adaptive_questioning": True,
            "personalization_enabled": True,
        }

        # 活跃上下文
        self.active_contexts: dict[str, InquiryContext] = {}

        # 性能统计
        self.stats = {
            "total_sessions": 0,
            "average_questions_per_session": 0.0,
            "stage_completion_rates": {},
            "decision_accuracy": 0.0,
            "emergency_detections": 0,
        }

        self._initialize_templates()
        self._initialize_decision_rules()

        logger.info("智能问诊流程管理器初始化完成")

    def _initialize_templates(self):
        """初始化问题模板"""
        templates = [
            # 主诉相关
            QuestionTemplate(
                id="chief_complaint_main",
                template="请详细描述您最主要的不适症状？",
                category="chief_complaint",
                priority=QuestionPriority.CRITICAL,
                conditions={},
                follow_up_rules=[
                    {"condition": "symptom_mentioned", "action": "explore_symptom"}
                ],
                expected_answer_type="text",
                validation_rules=["min_length:10"],
            ),
            # 症状探索
            QuestionTemplate(
                id="symptom_duration",
                template="这个症状持续多长时间了？",
                category="symptom_exploration",
                priority=QuestionPriority.HIGH,
                conditions={"has_symptom": True},
                follow_up_rules=[
                    {"condition": "chronic_symptom", "action": "explore_triggers"}
                ],
                expected_answer_type="duration",
                validation_rules=["valid_duration"],
            ),
            QuestionTemplate(
                id="symptom_severity",
                template="请用1-10分来评价症状的严重程度（1分最轻，10分最重）？",
                category="symptom_exploration",
                priority=QuestionPriority.HIGH,
                conditions={"has_symptom": True},
                follow_up_rules=[
                    {"condition": "severe_symptom", "action": "emergency_check"}
                ],
                expected_answer_type="scale",
                validation_rules=["range:1-10"],
            ),
            # 系统回顾
            QuestionTemplate(
                id="associated_symptoms",
                template="除了{main_symptom}，您还有其他不适吗？",
                category="system_review",
                priority=QuestionPriority.MEDIUM,
                conditions={"main_symptom_identified": True},
                follow_up_rules=[
                    {"condition": "multiple_symptoms", "action": "system_analysis"}
                ],
                expected_answer_type="text",
                validation_rules=[],
            ),
            # 病史采集
            QuestionTemplate(
                id="past_medical_history",
                template="您之前有过类似的症状或相关疾病吗？",
                category="history_taking",
                priority=QuestionPriority.MEDIUM,
                conditions={},
                follow_up_rules=[
                    {"condition": "has_history", "action": "explore_history"}
                ],
                expected_answer_type="text",
                validation_rules=[],
            ),
            # 风险评估
            QuestionTemplate(
                id="family_history",
                template="您的家族中有相关疾病史吗？",
                category="risk_assessment",
                priority=QuestionPriority.LOW,
                conditions={},
                follow_up_rules=[],
                expected_answer_type="text",
                validation_rules=[],
            ),
        ]

        for template in templates:
            self.question_templates[template.id] = template

    def _initialize_decision_rules(self):
        """初始化决策规则"""
        self.decision_rules = {
            FlowStage.INITIALIZATION: [
                {
                    "condition": "session_started",
                    "action": "advance_to_chief_complaint",
                    "priority": 1,
                }
            ],
            FlowStage.CHIEF_COMPLAINT: [
                {
                    "condition": "emergency_detected",
                    "action": "emergency_protocol",
                    "priority": 1,
                },
                {
                    "condition": "chief_complaint_clear",
                    "action": "advance_to_symptom_exploration",
                    "priority": 2,
                },
                {
                    "condition": "insufficient_information",
                    "action": "continue_chief_complaint",
                    "priority": 3,
                },
            ],
            FlowStage.SYMPTOM_EXPLORATION: [
                {
                    "condition": "emergency_detected",
                    "action": "emergency_protocol",
                    "priority": 1,
                },
                {
                    "condition": "symptoms_well_characterized",
                    "action": "advance_to_system_review",
                    "priority": 2,
                },
                {
                    "condition": "complex_symptom_pattern",
                    "action": "branch_exploration",
                    "priority": 3,
                },
                {
                    "condition": "max_questions_reached",
                    "action": "advance_to_system_review",
                    "priority": 4,
                },
            ],
            FlowStage.SYSTEM_REVIEW: [
                {
                    "condition": "comprehensive_review_complete",
                    "action": "advance_to_history_taking",
                    "priority": 1,
                },
                {
                    "condition": "significant_findings",
                    "action": "branch_exploration",
                    "priority": 2,
                },
            ],
            FlowStage.HISTORY_TAKING: [
                {
                    "condition": "relevant_history_collected",
                    "action": "advance_to_risk_assessment",
                    "priority": 1,
                }
            ],
            FlowStage.RISK_ASSESSMENT: [
                {
                    "condition": "risk_assessment_complete",
                    "action": "conclude_inquiry",
                    "priority": 1,
                }
            ],
        }

    @timer("flow_manager.start_session")
    @counter("flow_manager.sessions_started")
    async def start_inquiry_session(
        self,
        session_id: str,
        patient_id: str,
        initial_data: dict[str, Any] | None = None,
    ) -> InquiryContext:
        """
        开始问诊会话

        Args:
            session_id: 会话ID
            patient_id: 患者ID
            initial_data: 初始数据

        Returns:
            问诊上下文
        """
        try:
            context = InquiryContext(
                session_id=session_id,
                patient_id=patient_id,
                current_stage=FlowStage.INITIALIZATION,
                collected_data=initial_data or {},
                symptom_profile={},
                risk_factors=[],
                answered_questions=set(),
                skipped_questions=set(),
                confidence_scores={},
                stage_history=[(FlowStage.INITIALIZATION, datetime.now())],
                metadata={},
            )

            self.active_contexts[session_id] = context
            self.stats["total_sessions"] += 1

            # 自动进入主诉阶段
            await self._advance_to_stage(context, FlowStage.CHIEF_COMPLAINT)

            logger.info(f"问诊会话已开始: {session_id}")
            return context

        except Exception as e:
            logger.error(f"开始问诊会话失败: {e}")
            raise InquiryServiceError(f"开始问诊会话失败: {e}")

    @timer("flow_manager.process_answer")
    @counter("flow_manager.answers_processed")
    async def process_answer(
        self, session_id: str, question_id: str, answer: Any, confidence: float = 1.0
    ) -> FlowDecision:
        """
        处理用户回答并做出流程决策

        Args:
            session_id: 会话ID
            question_id: 问题ID
            answer: 用户回答
            confidence: 置信度

        Returns:
            流程决策
        """
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                raise InquiryServiceError(f"会话不存在: {session_id}")

            # 记录回答
            context.answered_questions.add(question_id)
            context.confidence_scores[question_id] = confidence

            # 更新收集的数据
            await self._update_collected_data(context, question_id, answer)

            # 检测紧急情况
            if await self._detect_emergency(context, answer):
                return FlowDecision(
                    decision_type=DecisionType.EMERGENCY_PROTOCOL,
                    next_stage=None,
                    next_questions=[],
                    reasoning="检测到紧急情况，需要立即处理",
                    confidence=1.0,
                    metadata={"emergency_type": "detected"},
                )

            # 分析当前阶段完成度
            stage_completion = await self._analyze_stage_completion(context)

            # 做出流程决策
            decision = await self._make_flow_decision(context, stage_completion)

            # 执行决策
            await self._execute_decision(context, decision)

            logger.debug(f"处理回答完成: {session_id}, 决策: {decision.decision_type}")
            return decision

        except Exception as e:
            logger.error(f"处理回答失败: {e}")
            raise InquiryServiceError(f"处理回答失败: {e}")

    @cached(ttl=300)
    async def generate_next_questions(
        self, session_id: str, max_questions: int = 3
    ) -> list[dict[str, Any]]:
        """
        生成下一批问题

        Args:
            session_id: 会话ID
            max_questions: 最大问题数

        Returns:
            问题列表
        """
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                raise InquiryServiceError(f"会话不存在: {session_id}")

            # 获取当前阶段的候选问题
            candidate_questions = await self._get_candidate_questions(context)

            # 根据优先级和相关性排序
            prioritized_questions = await self._prioritize_questions(
                context, candidate_questions
            )

            # 个性化问题生成
            if self.flow_config["personalization_enabled"]:
                prioritized_questions = await self._personalize_questions(
                    context, prioritized_questions
                )

            # 选择最终问题
            selected_questions = prioritized_questions[:max_questions]

            # 格式化问题
            formatted_questions = []
            for question_template in selected_questions:
                formatted_question = await self._format_question(
                    context, question_template
                )
                formatted_questions.append(formatted_question)

            logger.debug(
                f"生成问题完成: {session_id}, 数量: {len(formatted_questions)}"
            )
            return formatted_questions

        except Exception as e:
            logger.error(f"生成问题失败: {e}")
            raise InquiryServiceError(f"生成问题失败: {e}")

    async def _update_collected_data(
        self, context: InquiryContext, question_id: str, answer: Any
    ):
        """更新收集的数据"""
        template = self.question_templates.get(question_id)
        if not template:
            return

        # 根据问题类别更新数据
        if template.category == "chief_complaint":
            context.collected_data["chief_complaint"] = answer
            # 提取症状信息
            symptoms = await self._extract_symptoms_from_text(str(answer))
            context.symptom_profile.update(symptoms)

        elif template.category == "symptom_exploration":
            if question_id == "symptom_duration":
                context.collected_data["symptom_duration"] = answer
            elif question_id == "symptom_severity":
                context.collected_data["symptom_severity"] = answer

        elif template.category == "history_taking":
            if "medical_history" not in context.collected_data:
                context.collected_data["medical_history"] = []
            context.collected_data["medical_history"].append(
                {"question": question_id, "answer": answer}
            )

        # 更新风险因素
        risk_factors = await self._identify_risk_factors(answer)
        context.risk_factors.extend(risk_factors)

    async def _detect_emergency(self, context: InquiryContext, answer: Any) -> bool:
        """检测紧急情况"""
        answer_text = str(answer).lower()

        # 检查紧急关键词
        for keyword in self.flow_config["emergency_keywords"]:
            if keyword in answer_text:
                self.stats["emergency_detections"] += 1
                logger.warning(f"检测到紧急关键词: {keyword}")
                return True

        # 检查严重程度评分
        if "symptom_severity" in context.collected_data:
            severity = context.collected_data["symptom_severity"]
            if isinstance(severity, (int, float)) and severity >= 8:
                logger.warning(f"检测到高严重程度评分: {severity}")
                return True

        return False

    async def _analyze_stage_completion(
        self, context: InquiryContext
    ) -> dict[str, Any]:
        """分析当前阶段完成度"""
        stage = context.current_stage

        # 计算已回答问题数
        stage_questions = [
            q_id
            for q_id, template in self.question_templates.items()
            if template.category == stage.value.replace("_", "")
        ]

        answered_in_stage = len(
            context.answered_questions.intersection(set(stage_questions))
        )

        # 计算完成度
        max_questions = self.flow_config["max_questions_per_stage"].get(stage, 10)
        completion_rate = min(answered_in_stage / max_questions, 1.0)

        # 计算信息充分度
        information_adequacy = await self._calculate_information_adequacy(context)

        # 计算置信度
        avg_confidence = (
            np.mean(list(context.confidence_scores.values()))
            if context.confidence_scores
            else 0.0
        )

        return {
            "completion_rate": completion_rate,
            "information_adequacy": information_adequacy,
            "average_confidence": avg_confidence,
            "answered_questions": answered_in_stage,
            "max_questions": max_questions,
        }

    async def _make_flow_decision(
        self, context: InquiryContext, stage_completion: dict[str, Any]
    ) -> FlowDecision:
        """做出流程决策"""
        stage = context.current_stage
        rules = self.decision_rules.get(stage, [])

        for rule in sorted(rules, key=lambda x: x["priority"]):
            condition = rule["condition"]
            action = rule["action"]

            if await self._evaluate_condition(context, condition, stage_completion):
                return await self._create_decision(context, action, rule)

        # 默认决策：继续当前阶段
        return FlowDecision(
            decision_type=DecisionType.CONTINUE_CURRENT,
            next_stage=context.current_stage,
            next_questions=[],
            reasoning="继续当前阶段收集信息",
            confidence=0.5,
        )

    async def _evaluate_condition(
        self, context: InquiryContext, condition: str, stage_completion: dict[str, Any]
    ) -> bool:
        """评估条件"""
        if condition == "session_started":
            return True

        elif condition == "emergency_detected":
            return any(
                keyword in str(context.collected_data.get("chief_complaint", ""))
                for keyword in self.flow_config["emergency_keywords"]
            )

        elif condition == "chief_complaint_clear":
            return (
                stage_completion["information_adequacy"] > 0.7
                and "chief_complaint" in context.collected_data
            )

        elif condition == "symptoms_well_characterized":
            return (
                stage_completion["completion_rate"] > 0.6
                and stage_completion["average_confidence"] > 0.7
            )

        elif condition == "max_questions_reached":
            return stage_completion["completion_rate"] >= 1.0

        elif condition == "comprehensive_review_complete":
            return stage_completion["information_adequacy"] > 0.8

        elif condition == "relevant_history_collected":
            return "medical_history" in context.collected_data

        elif condition == "risk_assessment_complete":
            return (
                len(context.risk_factors) > 0
                or stage_completion["completion_rate"] > 0.5
            )

        return False

    async def _create_decision(
        self, context: InquiryContext, action: str, rule: dict[str, Any]
    ) -> FlowDecision:
        """创建决策"""
        if action == "advance_to_chief_complaint":
            return FlowDecision(
                decision_type=DecisionType.ADVANCE_STAGE,
                next_stage=FlowStage.CHIEF_COMPLAINT,
                next_questions=["chief_complaint_main"],
                reasoning="开始收集主诉信息",
                confidence=1.0,
            )

        elif action == "advance_to_symptom_exploration":
            return FlowDecision(
                decision_type=DecisionType.ADVANCE_STAGE,
                next_stage=FlowStage.SYMPTOM_EXPLORATION,
                next_questions=["symptom_duration", "symptom_severity"],
                reasoning="主诉明确，开始详细症状探索",
                confidence=0.9,
            )

        elif action == "emergency_protocol":
            return FlowDecision(
                decision_type=DecisionType.EMERGENCY_PROTOCOL,
                next_stage=None,
                next_questions=[],
                reasoning="检测到紧急情况，启动紧急处理流程",
                confidence=1.0,
                metadata={"emergency": True},
            )

        elif action == "conclude_inquiry":
            return FlowDecision(
                decision_type=DecisionType.CONCLUDE_INQUIRY,
                next_stage=FlowStage.CONCLUSION,
                next_questions=[],
                reasoning="问诊信息收集完成，准备生成结论",
                confidence=0.8,
            )

        # 默认继续当前阶段
        return FlowDecision(
            decision_type=DecisionType.CONTINUE_CURRENT,
            next_stage=context.current_stage,
            next_questions=[],
            reasoning="继续当前阶段",
            confidence=0.5,
        )

    async def _execute_decision(self, context: InquiryContext, decision: FlowDecision):
        """执行决策"""
        if decision.decision_type == DecisionType.ADVANCE_STAGE and decision.next_stage:
            await self._advance_to_stage(context, decision.next_stage)

        elif decision.decision_type == DecisionType.EMERGENCY_PROTOCOL:
            await self._handle_emergency(context)

        elif decision.decision_type == DecisionType.CONCLUDE_INQUIRY:
            await self._conclude_inquiry(context)

    async def _advance_to_stage(self, context: InquiryContext, next_stage: FlowStage):
        """进入下一阶段"""
        context.current_stage = next_stage
        context.stage_history.append((next_stage, datetime.now()))

        logger.info(f"会话 {context.session_id} 进入阶段: {next_stage.value}")

    async def _handle_emergency(self, context: InquiryContext):
        """处理紧急情况"""
        context.metadata["emergency_detected"] = True
        context.metadata["emergency_time"] = datetime.now().isoformat()

        logger.warning(f"会话 {context.session_id} 检测到紧急情况")

    async def _conclude_inquiry(self, context: InquiryContext):
        """结束问诊"""
        context.current_stage = FlowStage.CONCLUSION
        context.metadata["concluded"] = True
        context.metadata["conclusion_time"] = datetime.now().isoformat()

        logger.info(f"会话 {context.session_id} 问诊结束")

    async def _get_candidate_questions(
        self, context: InquiryContext
    ) -> list[QuestionTemplate]:
        """获取候选问题"""
        stage_category = context.current_stage.value

        candidates = []
        for template in self.question_templates.values():
            # 检查是否已回答
            if template.id in context.answered_questions:
                continue

            # 检查类别匹配
            if template.category != stage_category:
                continue

            # 检查条件
            if await self._check_question_conditions(context, template):
                candidates.append(template)

        return candidates

    async def _check_question_conditions(
        self, context: InquiryContext, template: QuestionTemplate
    ) -> bool:
        """检查问题条件"""
        for condition, value in template.conditions.items():
            if condition == "has_symptom":
                if not context.symptom_profile and value:
                    return False
            elif condition == "main_symptom_identified":
                if "chief_complaint" not in context.collected_data and value:
                    return False

        return True

    async def _prioritize_questions(
        self, context: InquiryContext, questions: list[QuestionTemplate]
    ) -> list[QuestionTemplate]:
        """问题优先级排序"""

        def priority_score(template: QuestionTemplate) -> float:
            base_score = {
                QuestionPriority.CRITICAL: 100,
                QuestionPriority.HIGH: 80,
                QuestionPriority.MEDIUM: 60,
                QuestionPriority.LOW: 40,
                QuestionPriority.OPTIONAL: 20,
            }[template.priority]

            # 根据上下文调整分数
            relevance_score = self._calculate_relevance(context, template)

            return base_score + relevance_score

        return sorted(questions, key=priority_score, reverse=True)

    def _calculate_relevance(
        self, context: InquiryContext, template: QuestionTemplate
    ) -> float:
        """计算问题相关性"""
        relevance = 0.0

        # 基于已收集信息的相关性
        if template.category in context.collected_data:
            relevance += 10

        # 基于症状档案的相关性
        if context.symptom_profile:
            relevance += 5

        return relevance

    async def _personalize_questions(
        self, context: InquiryContext, questions: list[QuestionTemplate]
    ) -> list[QuestionTemplate]:
        """个性化问题"""
        # 基于患者历史和偏好调整问题
        # 这里可以集成机器学习模型进行个性化
        return questions

    async def _format_question(
        self, context: InquiryContext, template: QuestionTemplate
    ) -> dict[str, Any]:
        """格式化问题"""
        question_text = template.template

        # 替换模板变量
        if "{main_symptom}" in question_text:
            main_symptom = context.collected_data.get("chief_complaint", "症状")
            question_text = question_text.replace("{main_symptom}", main_symptom)

        return {
            "id": template.id,
            "question": question_text,
            "type": template.expected_answer_type,
            "priority": template.priority.value,
            "category": template.category,
            "validation_rules": template.validation_rules,
            "metadata": template.metadata,
        }

    async def _extract_symptoms_from_text(self, text: str) -> dict[str, Any]:
        """从文本中提取症状"""
        # 这里应该调用症状提取器
        # 简化实现
        symptoms = {}
        common_symptoms = ["头痛", "发热", "咳嗽", "乏力", "恶心"]

        for symptom in common_symptoms:
            if symptom in text:
                symptoms[symptom] = {"mentioned": True, "context": text}

        return symptoms

    async def _identify_risk_factors(self, answer: Any) -> list[str]:
        """识别风险因素"""
        risk_factors = []
        answer_text = str(answer).lower()

        risk_keywords = {
            "高血压": ["血压高", "高血压"],
            "糖尿病": ["血糖高", "糖尿病"],
            "心脏病": ["心脏", "胸痛", "心悸"],
            "吸烟": ["吸烟", "抽烟"],
            "饮酒": ["喝酒", "饮酒"],
        }

        for risk_factor, keywords in risk_keywords.items():
            if any(keyword in answer_text for keyword in keywords):
                risk_factors.append(risk_factor)

        return risk_factors

    async def _calculate_information_adequacy(self, context: InquiryContext) -> float:
        """计算信息充分度"""
        stage = context.current_stage

        # 基于阶段的必要信息检查
        required_info = {
            FlowStage.CHIEF_COMPLAINT: ["chief_complaint"],
            FlowStage.SYMPTOM_EXPLORATION: ["symptom_duration", "symptom_severity"],
            FlowStage.SYSTEM_REVIEW: ["associated_symptoms"],
            FlowStage.HISTORY_TAKING: ["medical_history"],
            FlowStage.RISK_ASSESSMENT: ["risk_factors"],
        }

        required = required_info.get(stage, [])
        if not required:
            return 1.0

        available = sum(1 for info in required if info in context.collected_data)
        return available / len(required)

    @memory_optimized
    async def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """获取会话摘要"""
        context = self.active_contexts.get(session_id)
        if not context:
            raise InquiryServiceError(f"会话不存在: {session_id}")

        return {
            "session_id": session_id,
            "patient_id": context.patient_id,
            "current_stage": context.current_stage.value,
            "answered_questions": len(context.answered_questions),
            "collected_data_keys": list(context.collected_data.keys()),
            "symptom_count": len(context.symptom_profile),
            "risk_factors": context.risk_factors,
            "stage_history": [
                {"stage": stage.value, "time": time.isoformat()}
                for stage, time in context.stage_history
            ],
            "average_confidence": np.mean(list(context.confidence_scores.values()))
            if context.confidence_scores
            else 0.0,
        }

    async def cleanup_session(self, session_id: str):
        """清理会话"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
            logger.info(f"会话已清理: {session_id}")

    async def get_service_stats(self) -> dict[str, Any]:
        """获取服务统计"""
        return {
            **self.stats,
            "active_sessions": len(self.active_contexts),
            "question_templates": len(self.question_templates),
            "decision_rules": sum(len(rules) for rules in self.decision_rules.values()),
        }
