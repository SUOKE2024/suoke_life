"""智能体协作评测指标实现。"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from .metrics import Metric


@dataclass
class MetricResult:
    """指标结果数据类。"""

    name: str
    value: float
    threshold: float
    details: dict[str, Any]

    @property
    def passed(self) -> bool:
        """是否通过阈值。"""
        return self.value >= self.threshold


@dataclass
class DialogueTurn:
    """对话轮次数据类。"""

    agent_id: str  # 智能体ID
    role: str  # 角色（如主导、协助等）
    content: str  # 对话内容
    intent: str  # 对话意图
    entities: list[dict[str, Any]]  # 识别的实体
    confidence: float  # 置信度
    response_time: float  # 响应时间(ms)
    context_relevance: float  # 上下文相关度


@dataclass
class TaskCompletion:
    """任务完成情况数据类。"""

    task_id: str  # 任务ID
    status: str  # 完成状态
    duration: float  # 完成时间(s)
    steps: list[str]  # 完成步骤
    agent_contributions: dict[str, float]  # 各智能体贡献度
    user_satisfaction: float | None  # 用户满意度


class AgentCollaborationMetric(Metric):
    """智能体协作评测指标。"""

    def __init__(self, threshold: float = 0.85):
        super().__init__("agent_collaboration", threshold, "", True)
        self.description = "评估多智能体协作效果"

    def calculate(
        self, dialogue_turns: list[DialogueTurn], task_completion: TaskCompletion
    ) -> MetricResult:
        """计算智能体协作的评测指标。"""

        # 计算对话质量指标
        dialogue_quality = self._calculate_dialogue_quality(dialogue_turns)

        # 计算任务完成指标
        task_success = self._calculate_task_success(task_completion)

        # 计算协作效率指标
        collab_efficiency = self._calculate_collaboration_efficiency(
            dialogue_turns, task_completion
        )

        # 计算响应性能指标
        performance = self._calculate_performance_metrics(dialogue_turns)

        # 计算加权总分
        weights = {
            "dialogue_quality": 0.3,
            "task_success": 0.3,
            "collab_efficiency": 0.25,
            "performance": 0.15,
        }

        total_score = (
            weights["dialogue_quality"] * dialogue_quality["overall"]
            + weights["task_success"] * task_success["overall"]
            + weights["collab_efficiency"] * collab_efficiency["overall"]
            + weights["performance"] * performance["overall"]
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "dialogue_quality": dialogue_quality,
                "task_success": task_success,
                "collaboration_efficiency": collab_efficiency,
                "performance": performance,
            },
        )

    def _calculate_dialogue_quality(
        self, turns: list[DialogueTurn]
    ) -> dict[str, float]:
        """计算对话质量指标。"""

        # 计算平均置信度
        avg_confidence = np.mean([turn.confidence for turn in turns])

        # 计算平均上下文相关度
        avg_context_relevance = np.mean([turn.context_relevance for turn in turns])

        # 计算意图一致性
        intent_consistency = self._calculate_intent_consistency(turns)

        # 计算实体识别质量
        entity_quality = self._calculate_entity_recognition_quality(turns)

        # 计算整体对话质量分数
        weights = {
            "confidence": 0.25,
            "context_relevance": 0.3,
            "intent_consistency": 0.25,
            "entity_quality": 0.2,
        }

        overall = (
            weights["confidence"] * avg_confidence
            + weights["context_relevance"] * avg_context_relevance
            + weights["intent_consistency"] * intent_consistency
            + weights["entity_quality"] * entity_quality
        )

        return {
            "overall": overall,
            "confidence": avg_confidence,
            "context_relevance": avg_context_relevance,
            "intent_consistency": intent_consistency,
            "entity_quality": entity_quality,
        }

    def _calculate_task_success(self, completion: TaskCompletion) -> dict[str, float]:
        """计算任务完成指标。"""

        # 计算完成状态得分
        status_score = (
            1.0
            if completion.status == "completed"
            else (0.5 if completion.status == "partial" else 0.0)
        )

        # 计算时间效率得分（假设基准时间为300秒）
        time_score = max(0, 1 - (completion.duration / 300))

        # 计算步骤完整性得分
        steps_score = len(completion.steps) / 10  # 假设标准步骤数为10
        steps_score = min(1.0, steps_score)  # 上限为1.0

        # 计算贡献均衡度
        contribution_balance = self._calculate_contribution_balance(
            completion.agent_contributions
        )

        # 计算用户满意度得分
        satisfaction_score = (
            completion.user_satisfaction
            if completion.user_satisfaction is not None
            else 0.8
        )

        # 计算整体任务完成分数
        weights = {
            "status": 0.3,
            "time": 0.2,
            "steps": 0.2,
            "balance": 0.15,
            "satisfaction": 0.15,
        }

        overall = (
            weights["status"] * status_score
            + weights["time"] * time_score
            + weights["steps"] * steps_score
            + weights["balance"] * contribution_balance
            + weights["satisfaction"] * satisfaction_score
        )

        return {
            "overall": overall,
            "status_score": status_score,
            "time_score": time_score,
            "steps_score": steps_score,
            "contribution_balance": contribution_balance,
            "satisfaction_score": satisfaction_score,
        }

    def _calculate_collaboration_efficiency(
        self, turns: list[DialogueTurn], completion: TaskCompletion
    ) -> dict[str, float]:
        """计算协作效率指标。"""

        # 计算角色转换合理性
        role_transition = self._calculate_role_transition_score(turns)

        # 计算信息流转效率
        info_flow = self._calculate_information_flow_score(turns)

        # 计算决策一致性
        decision_consistency = self._calculate_decision_consistency(turns)

        # 计算协作负载均衡度
        workload_balance = self._calculate_workload_balance(turns)

        # 计算整体协作效率分数
        weights = {
            "role_transition": 0.25,
            "info_flow": 0.3,
            "decision_consistency": 0.25,
            "workload_balance": 0.2,
        }

        overall = (
            weights["role_transition"] * role_transition
            + weights["info_flow"] * info_flow
            + weights["decision_consistency"] * decision_consistency
            + weights["workload_balance"] * workload_balance
        )

        return {
            "overall": overall,
            "role_transition": role_transition,
            "info_flow": info_flow,
            "decision_consistency": decision_consistency,
            "workload_balance": workload_balance,
        }

    def _calculate_performance_metrics(
        self, turns: list[DialogueTurn]
    ) -> dict[str, float]:
        """计算性能指标。"""

        # 计算平均响应时间得分
        response_times = [turn.response_time for turn in turns]
        avg_response_time = np.mean(response_times)
        response_time_score = max(0, 1 - (avg_response_time / 1000))  # 基准1000ms

        # 计算响应时间稳定性
        response_time_std = np.std(response_times)
        stability_score = max(0, 1 - (response_time_std / 500))  # 基准500ms

        # 计算整体性能分数
        weights = {"response_time": 0.6, "stability": 0.4}

        overall = (
            weights["response_time"] * response_time_score
            + weights["stability"] * stability_score
        )

        return {
            "overall": overall,
            "response_time_score": response_time_score,
            "stability_score": stability_score,
            "avg_response_time": avg_response_time,
            "response_time_std": response_time_std,
        }

    def _calculate_intent_consistency(self, turns: list[DialogueTurn]) -> float:
        """计算意图一致性得分。"""
        if len(turns) < 2:
            return 1.0

        consistent_transitions = 0
        total_transitions = len(turns) - 1

        for i in range(total_transitions):
            current_intent = turns[i].intent
            next_intent = turns[i + 1].intent

            # 检查意图转换是否合理
            if self._is_valid_intent_transition(current_intent, next_intent):
                consistent_transitions += 1

        return consistent_transitions / total_transitions

    def _is_valid_intent_transition(
        self, current_intent: str, next_intent: str
    ) -> bool:
        """检查意图转换是否合理。"""
        # 这里可以实现更复杂的意图转换规则
        valid_transitions = {
            "greeting": ["inquiry", "information"],
            "inquiry": ["information", "clarification", "suggestion"],
            "information": ["inquiry", "suggestion", "confirmation"],
            "suggestion": ["confirmation", "inquiry", "information"],
            "confirmation": ["farewell", "inquiry", "suggestion"],
            "clarification": ["information", "suggestion"],
            "farewell": ["greeting"],  # 循环对话可能的情况
        }

        return (
            current_intent in valid_transitions
            and next_intent in valid_transitions[current_intent]
        )

    def _calculate_entity_recognition_quality(self, turns: list[DialogueTurn]) -> float:
        """计算实体识别质量得分。"""
        if not turns:
            return 0.0

        total_quality = 0.0
        total_entities = 0

        for turn in turns:
            for entity in turn.entities:
                # 假设每个实体都有confidence字段
                if "confidence" in entity:
                    total_quality += entity["confidence"]
                    total_entities += 1

        return total_quality / total_entities if total_entities > 0 else 0.0

    def _calculate_contribution_balance(self, contributions: dict[str, float]) -> float:
        """计算贡献均衡度。"""
        if not contributions:
            return 0.0

        values = list(contributions.values())
        mean_contribution = np.mean(values)
        max_deviation = max(abs(v - mean_contribution) for v in values)

        # 计算均衡度得分（偏差越小得分越高）
        balance_score = max(0, 1 - (max_deviation / mean_contribution))

        return balance_score

    def _calculate_role_transition_score(self, turns: list[DialogueTurn]) -> float:
        """计算角色转换合理性得分。"""
        if len(turns) < 2:
            return 1.0

        valid_transitions = 0
        total_transitions = len(turns) - 1

        for i in range(total_transitions):
            current_role = turns[i].role
            next_role = turns[i + 1].role

            # 检查角色转换是否合理
            if self._is_valid_role_transition(current_role, next_role):
                valid_transitions += 1

        return valid_transitions / total_transitions

    def _is_valid_role_transition(self, current_role: str, next_role: str) -> bool:
        """检查角色转换是否合理。"""
        valid_transitions = {
            "leader": ["assistant", "coordinator"],
            "assistant": ["leader", "coordinator"],
            "coordinator": ["leader", "assistant"],
        }

        return (
            current_role in valid_transitions
            and next_role in valid_transitions[current_role]
        )

    def _calculate_information_flow_score(self, turns: list[DialogueTurn]) -> float:
        """计算信息流转效率得分。"""
        if len(turns) < 2:
            return 1.0

        # 计算上下文相关度的连续性
        context_continuity = []
        for i in range(len(turns) - 1):
            current_relevance = turns[i].context_relevance
            next_relevance = turns[i + 1].context_relevance
            continuity = 1 - abs(current_relevance - next_relevance)
            context_continuity.append(continuity)

        return np.mean(context_continuity)

    def _calculate_decision_consistency(self, turns: list[DialogueTurn]) -> float:
        """计算决策一致性得分。"""
        if len(turns) < 2:
            return 1.0

        # 使用置信度来评估决策一致性
        confidence_consistency = []
        for i in range(len(turns) - 1):
            current_conf = turns[i].confidence
            next_conf = turns[i + 1].confidence
            consistency = 1 - abs(current_conf - next_conf)
            confidence_consistency.append(consistency)

        return np.mean(confidence_consistency)

    def _calculate_workload_balance(self, turns: list[DialogueTurn]) -> float:
        """计算协作负载均衡度。"""
        if not turns:
            return 0.0

        # 统计每个智能体的参与次数
        agent_counts = {}
        for turn in turns:
            agent_counts[turn.agent_id] = agent_counts.get(turn.agent_id, 0) + 1

        # 计算参与度的标准差
        counts = list(agent_counts.values())
        mean_count = np.mean(counts)
        std_count = np.std(counts)

        # 计算均衡度得分（标准差越小得分越高）
        balance_score = max(0, 1 - (std_count / mean_count))

        return balance_score
