#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能路由器
支持四个智能体（小艾、小克、老克、索儿）的协同决策和任务分发
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from loguru import logger

from ..observability.metrics import MetricsCollector


class AgentType(str, Enum):
    """智能体类型"""
    XIAOAI = "xiaoai"          # 小艾 - AI助手，负责智能对话和初步分析
    XIAOKE = "xiaoke"          # 小克 - 专业诊断，负责症状分析和辨证论治
    LAOKE = "laoke"            # 老克 - 资深专家，负责复杂病例和治疗方案
    SOER = "soer"              # 索儿 - 健康管理，负责预防保健和生活指导


class TaskType(str, Enum):
    """任务类型"""
    CONSULTATION = "consultation"              # 健康咨询
    DIAGNOSIS = "diagnosis"                    # 诊断分析
    TREATMENT = "treatment"                    # 治疗建议
    PREVENTION = "prevention"                  # 预防保健
    LIFESTYLE = "lifestyle"                    # 生活指导
    EMERGENCY = "emergency"                    # 紧急情况
    EDUCATION = "education"                    # 健康教育
    MONITORING = "monitoring"                  # 健康监测


class UrgencyLevel(str, Enum):
    """紧急程度"""
    LOW = "low"                # 低
    MEDIUM = "medium"          # 中
    HIGH = "high"              # 高
    CRITICAL = "critical"      # 紧急


class ComplexityLevel(str, Enum):
    """复杂程度"""
    SIMPLE = "simple"          # 简单
    MODERATE = "moderate"      # 中等
    COMPLEX = "complex"        # 复杂
    EXPERT = "expert"          # 专家级


@dataclass
class RoutingRequest:
    """路由请求"""
    request_id: str
    user_id: str
    query: str
    task_type: TaskType
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    complexity: ComplexityLevel = ComplexityLevel.MODERATE
    context: Dict[str, Any] = field(default_factory=dict)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    session_history: List[Dict[str, Any]] = field(default_factory=list)
    multimodal_data: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = ""


@dataclass
class AgentCapability:
    """智能体能力"""
    agent_type: AgentType
    supported_tasks: List[TaskType]
    expertise_areas: List[str]
    complexity_handling: List[ComplexityLevel]
    urgency_handling: List[UrgencyLevel]
    load_capacity: int = 100
    current_load: int = 0
    availability: bool = True
    performance_score: float = 1.0
    specializations: List[str] = field(default_factory=list)


@dataclass
class RoutingDecision:
    """路由决策"""
    primary_agent: AgentType
    secondary_agents: List[AgentType] = field(default_factory=list)
    collaboration_mode: str = "sequential"  # sequential, parallel, hierarchical
    confidence: float = 0.0
    reasoning: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationPlan:
    """协作计划"""
    agents: List[AgentType]
    workflow: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    communication_protocol: str = "async"
    quality_gates: List[Dict[str, Any]] = field(default_factory=list)
    fallback_strategy: str = "escalate"


class AgentManager:
    """智能体管理器"""
    
    def __init__(self):
        self.agents = self._initialize_agents()
        self.agent_states = {agent: {"status": "available", "load": 0} for agent in AgentType}
    
    def _initialize_agents(self) -> Dict[AgentType, AgentCapability]:
        """初始化智能体能力"""
        return {
            AgentType.XIAOAI: AgentCapability(
                agent_type=AgentType.XIAOAI,
                supported_tasks=[
                    TaskType.CONSULTATION,
                    TaskType.EDUCATION,
                    TaskType.MONITORING
                ],
                expertise_areas=[
                    "自然语言处理", "用户交互", "基础健康咨询",
                    "症状收集", "初步分析", "健康教育"
                ],
                complexity_handling=[ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE],
                urgency_handling=[UrgencyLevel.LOW, UrgencyLevel.MEDIUM],
                specializations=["对话管理", "情感分析", "用户画像"]
            ),
            
            AgentType.XIAOKE: AgentCapability(
                agent_type=AgentType.XIAOKE,
                supported_tasks=[
                    TaskType.DIAGNOSIS,
                    TaskType.TREATMENT,
                    TaskType.CONSULTATION
                ],
                expertise_areas=[
                    "中医诊断", "辨证论治", "症状分析",
                    "方剂推荐", "病理分析", "治疗方案"
                ],
                complexity_handling=[
                    ComplexityLevel.SIMPLE,
                    ComplexityLevel.MODERATE,
                    ComplexityLevel.COMPLEX
                ],
                urgency_handling=[
                    UrgencyLevel.LOW,
                    UrgencyLevel.MEDIUM,
                    UrgencyLevel.HIGH
                ],
                specializations=["辨证分析", "方剂配伍", "病症诊断"]
            ),
            
            AgentType.LAOKE: AgentCapability(
                agent_type=AgentType.LAOKE,
                supported_tasks=[
                    TaskType.DIAGNOSIS,
                    TaskType.TREATMENT,
                    TaskType.EMERGENCY
                ],
                expertise_areas=[
                    "复杂病例", "疑难杂症", "专家诊断",
                    "高级治疗", "临床经验", "医学研究"
                ],
                complexity_handling=[
                    ComplexityLevel.COMPLEX,
                    ComplexityLevel.EXPERT
                ],
                urgency_handling=[
                    UrgencyLevel.HIGH,
                    UrgencyLevel.CRITICAL
                ],
                specializations=["疑难病症", "复杂治疗", "临床决策"]
            ),
            
            AgentType.SOER: AgentCapability(
                agent_type=AgentType.SOER,
                supported_tasks=[
                    TaskType.PREVENTION,
                    TaskType.LIFESTYLE,
                    TaskType.MONITORING,
                    TaskType.EDUCATION
                ],
                expertise_areas=[
                    "预防保健", "生活方式", "健康管理",
                    "营养指导", "运动建议", "心理健康"
                ],
                complexity_handling=[ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE],
                urgency_handling=[UrgencyLevel.LOW, UrgencyLevel.MEDIUM],
                specializations=["健康管理", "生活指导", "预防医学"]
            )
        }
    
    def get_agent_capability(self, agent_type: AgentType) -> AgentCapability:
        """获取智能体能力"""
        return self.agents.get(agent_type)
    
    def update_agent_load(self, agent_type: AgentType, load_change: int):
        """更新智能体负载"""
        if agent_type in self.agent_states:
            self.agent_states[agent_type]["load"] += load_change
            self.agent_states[agent_type]["load"] = max(0, self.agent_states[agent_type]["load"])
    
    def get_available_agents(self) -> List[AgentType]:
        """获取可用智能体"""
        available = []
        for agent_type, state in self.agent_states.items():
            if state["status"] == "available" and state["load"] < 80:  # 负载阈值
                available.append(agent_type)
        return available
    
    def get_agent_performance(self, agent_type: AgentType) -> float:
        """获取智能体性能分数"""
        capability = self.agents.get(agent_type)
        return capability.performance_score if capability else 0.0


class TaskAnalyzer:
    """任务分析器"""
    
    def __init__(self):
        self.task_patterns = self._load_task_patterns()
        self.complexity_indicators = self._load_complexity_indicators()
        self.urgency_indicators = self._load_urgency_indicators()
    
    def _load_task_patterns(self) -> Dict[str, TaskType]:
        """加载任务模式"""
        return {
            # 咨询类关键词
            "咨询": TaskType.CONSULTATION,
            "询问": TaskType.CONSULTATION,
            "请问": TaskType.CONSULTATION,
            "想了解": TaskType.CONSULTATION,
            
            # 诊断类关键词
            "诊断": TaskType.DIAGNOSIS,
            "什么病": TaskType.DIAGNOSIS,
            "症状": TaskType.DIAGNOSIS,
            "不舒服": TaskType.DIAGNOSIS,
            "疼痛": TaskType.DIAGNOSIS,
            
            # 治疗类关键词
            "治疗": TaskType.TREATMENT,
            "怎么治": TaskType.TREATMENT,
            "用什么药": TaskType.TREATMENT,
            "方剂": TaskType.TREATMENT,
            
            # 预防类关键词
            "预防": TaskType.PREVENTION,
            "如何避免": TaskType.PREVENTION,
            "保健": TaskType.PREVENTION,
            
            # 生活指导类关键词
            "生活": TaskType.LIFESTYLE,
            "饮食": TaskType.LIFESTYLE,
            "运动": TaskType.LIFESTYLE,
            "调理": TaskType.LIFESTYLE,
            
            # 紧急情况关键词
            "急": TaskType.EMERGENCY,
            "紧急": TaskType.EMERGENCY,
            "严重": TaskType.EMERGENCY,
            "出血": TaskType.EMERGENCY,
            
            # 教育类关键词
            "学习": TaskType.EDUCATION,
            "了解": TaskType.EDUCATION,
            "知识": TaskType.EDUCATION,
            
            # 监测类关键词
            "监测": TaskType.MONITORING,
            "检查": TaskType.MONITORING,
            "观察": TaskType.MONITORING
        }
    
    def _load_complexity_indicators(self) -> Dict[str, ComplexityLevel]:
        """加载复杂度指标"""
        return {
            # 简单
            "简单": ComplexityLevel.SIMPLE,
            "基础": ComplexityLevel.SIMPLE,
            "常见": ComplexityLevel.SIMPLE,
            
            # 中等
            "复杂": ComplexityLevel.MODERATE,
            "多种": ComplexityLevel.MODERATE,
            "综合": ComplexityLevel.MODERATE,
            
            # 复杂
            "疑难": ComplexityLevel.COMPLEX,
            "罕见": ComplexityLevel.COMPLEX,
            "多系统": ComplexityLevel.COMPLEX,
            
            # 专家级
            "专家": ComplexityLevel.EXPERT,
            "研究": ComplexityLevel.EXPERT,
            "学术": ComplexityLevel.EXPERT
        }
    
    def _load_urgency_indicators(self) -> Dict[str, UrgencyLevel]:
        """加载紧急度指标"""
        return {
            # 低
            "不急": UrgencyLevel.LOW,
            "慢慢": UrgencyLevel.LOW,
            "有时间": UrgencyLevel.LOW,
            
            # 中等
            "一般": UrgencyLevel.MEDIUM,
            "正常": UrgencyLevel.MEDIUM,
            
            # 高
            "急": UrgencyLevel.HIGH,
            "赶紧": UrgencyLevel.HIGH,
            "尽快": UrgencyLevel.HIGH,
            
            # 紧急
            "紧急": UrgencyLevel.CRITICAL,
            "立即": UrgencyLevel.CRITICAL,
            "马上": UrgencyLevel.CRITICAL
        }
    
    async def analyze_request(self, request: RoutingRequest) -> RoutingRequest:
        """分析请求"""
        # 分析任务类型
        if request.task_type == TaskType.CONSULTATION:  # 如果未指定，则自动识别
            request.task_type = self._identify_task_type(request.query)
        
        # 分析复杂度
        if request.complexity == ComplexityLevel.MODERATE:  # 如果未指定，则自动识别
            request.complexity = self._assess_complexity(request)
        
        # 分析紧急度
        if request.urgency == UrgencyLevel.MEDIUM:  # 如果未指定，则自动识别
            request.urgency = self._assess_urgency(request)
        
        return request
    
    def _identify_task_type(self, query: str) -> TaskType:
        """识别任务类型"""
        # 基于关键词匹配
        for keyword, task_type in self.task_patterns.items():
            if keyword in query:
                return task_type
        
        # 默认为咨询
        return TaskType.CONSULTATION
    
    def _assess_complexity(self, request: RoutingRequest) -> ComplexityLevel:
        """评估复杂度"""
        complexity_score = 0
        
        # 基于查询内容
        for keyword, level in self.complexity_indicators.items():
            if keyword in request.query:
                if level == ComplexityLevel.SIMPLE:
                    complexity_score += 1
                elif level == ComplexityLevel.MODERATE:
                    complexity_score += 2
                elif level == ComplexityLevel.COMPLEX:
                    complexity_score += 3
                elif level == ComplexityLevel.EXPERT:
                    complexity_score += 4
        
        # 基于多模态数据
        if request.multimodal_data:
            complexity_score += len(request.multimodal_data)
        
        # 基于历史会话
        if len(request.session_history) > 5:
            complexity_score += 1
        
        # 基于用户档案
        if request.user_profile.get("medical_history"):
            complexity_score += 1
        
        # 转换为复杂度等级
        if complexity_score <= 2:
            return ComplexityLevel.SIMPLE
        elif complexity_score <= 4:
            return ComplexityLevel.MODERATE
        elif complexity_score <= 6:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.EXPERT
    
    def _assess_urgency(self, request: RoutingRequest) -> UrgencyLevel:
        """评估紧急度"""
        urgency_score = 0
        
        # 基于关键词
        for keyword, level in self.urgency_indicators.items():
            if keyword in request.query:
                if level == UrgencyLevel.LOW:
                    urgency_score += 1
                elif level == UrgencyLevel.MEDIUM:
                    urgency_score += 2
                elif level == UrgencyLevel.HIGH:
                    urgency_score += 3
                elif level == UrgencyLevel.CRITICAL:
                    urgency_score += 4
        
        # 基于症状严重性
        severe_symptoms = ["剧痛", "出血", "呼吸困难", "胸痛", "昏迷"]
        for symptom in severe_symptoms:
            if symptom in request.query:
                urgency_score += 3
        
        # 转换为紧急度等级
        if urgency_score <= 1:
            return UrgencyLevel.LOW
        elif urgency_score <= 3:
            return UrgencyLevel.MEDIUM
        elif urgency_score <= 5:
            return UrgencyLevel.HIGH
        else:
            return UrgencyLevel.CRITICAL


class RoutingEngine:
    """路由引擎"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.routing_rules = self._initialize_routing_rules()
        self.collaboration_patterns = self._initialize_collaboration_patterns()
    
    def _initialize_routing_rules(self) -> Dict[str, Any]:
        """初始化路由规则"""
        return {
            # 基于任务类型的路由规则
            "task_routing": {
                TaskType.CONSULTATION: [AgentType.XIAOAI, AgentType.XIAOKE],
                TaskType.DIAGNOSIS: [AgentType.XIAOKE, AgentType.LAOKE],
                TaskType.TREATMENT: [AgentType.XIAOKE, AgentType.LAOKE],
                TaskType.PREVENTION: [AgentType.SOER, AgentType.XIAOAI],
                TaskType.LIFESTYLE: [AgentType.SOER, AgentType.XIAOAI],
                TaskType.EMERGENCY: [AgentType.LAOKE, AgentType.XIAOKE],
                TaskType.EDUCATION: [AgentType.XIAOAI, AgentType.SOER],
                TaskType.MONITORING: [AgentType.SOER, AgentType.XIAOAI]
            },
            
            # 基于复杂度的路由规则
            "complexity_routing": {
                ComplexityLevel.SIMPLE: [AgentType.XIAOAI, AgentType.SOER],
                ComplexityLevel.MODERATE: [AgentType.XIAOKE, AgentType.XIAOAI],
                ComplexityLevel.COMPLEX: [AgentType.XIAOKE, AgentType.LAOKE],
                ComplexityLevel.EXPERT: [AgentType.LAOKE]
            },
            
            # 基于紧急度的路由规则
            "urgency_routing": {
                UrgencyLevel.LOW: [AgentType.XIAOAI, AgentType.SOER],
                UrgencyLevel.MEDIUM: [AgentType.XIAOKE, AgentType.XIAOAI],
                UrgencyLevel.HIGH: [AgentType.XIAOKE, AgentType.LAOKE],
                UrgencyLevel.CRITICAL: [AgentType.LAOKE]
            }
        }
    
    def _initialize_collaboration_patterns(self) -> Dict[str, Dict[str, Any]]:
        """初始化协作模式"""
        return {
            "sequential": {
                "description": "顺序协作，一个智能体完成后传递给下一个",
                "suitable_for": ["诊断流程", "治疗方案制定"],
                "communication": "async"
            },
            
            "parallel": {
                "description": "并行协作，多个智能体同时工作",
                "suitable_for": ["多角度分析", "快速响应"],
                "communication": "sync"
            },
            
            "hierarchical": {
                "description": "分层协作，专家智能体监督和指导",
                "suitable_for": ["复杂病例", "质量控制"],
                "communication": "hierarchical"
            },
            
            "consultative": {
                "description": "咨询协作，主要智能体咨询其他智能体",
                "suitable_for": ["专业咨询", "第二意见"],
                "communication": "request_response"
            }
        }
    
    async def route_request(self, request: RoutingRequest) -> RoutingDecision:
        """路由请求"""
        try:
            # 获取候选智能体
            candidates = self._get_candidate_agents(request)
            
            # 选择主要智能体
            primary_agent = self._select_primary_agent(candidates, request)
            
            # 选择次要智能体
            secondary_agents = self._select_secondary_agents(candidates, primary_agent, request)
            
            # 确定协作模式
            collaboration_mode = self._determine_collaboration_mode(request, primary_agent, secondary_agents)
            
            # 计算置信度
            confidence = self._calculate_routing_confidence(primary_agent, secondary_agents, request)
            
            # 生成推理链
            reasoning = self._generate_routing_reasoning(primary_agent, secondary_agents, request)
            
            # 估算处理时间
            estimated_duration = self._estimate_processing_duration(request, primary_agent, secondary_agents)
            
            return RoutingDecision(
                primary_agent=primary_agent,
                secondary_agents=secondary_agents,
                collaboration_mode=collaboration_mode,
                confidence=confidence,
                reasoning=reasoning,
                estimated_duration=estimated_duration
            )
            
        except Exception as e:
            logger.error(f"路由请求失败: {e}")
            # 默认路由到小艾
            return RoutingDecision(
                primary_agent=AgentType.XIAOAI,
                secondary_agents=[],
                collaboration_mode="sequential",
                confidence=0.5,
                reasoning=[f"路由失败，默认分配给小艾: {str(e)}"]
            )
    
    def _get_candidate_agents(self, request: RoutingRequest) -> List[AgentType]:
        """获取候选智能体"""
        candidates = set()
        
        # 基于任务类型
        task_candidates = self.routing_rules["task_routing"].get(request.task_type, [])
        candidates.update(task_candidates)
        
        # 基于复杂度
        complexity_candidates = self.routing_rules["complexity_routing"].get(request.complexity, [])
        candidates.update(complexity_candidates)
        
        # 基于紧急度
        urgency_candidates = self.routing_rules["urgency_routing"].get(request.urgency, [])
        candidates.update(urgency_candidates)
        
        # 过滤可用智能体
        available_agents = self.agent_manager.get_available_agents()
        candidates = [agent for agent in candidates if agent in available_agents]
        
        return list(candidates) if candidates else [AgentType.XIAOAI]  # 默认小艾
    
    def _select_primary_agent(self, candidates: List[AgentType], request: RoutingRequest) -> AgentType:
        """选择主要智能体"""
        if not candidates:
            return AgentType.XIAOAI
        
        # 计算每个候选智能体的适合度分数
        scores = {}
        
        for agent in candidates:
            capability = self.agent_manager.get_agent_capability(agent)
            if not capability:
                continue
            
            score = 0
            
            # 任务匹配度
            if request.task_type in capability.supported_tasks:
                score += 3
            
            # 复杂度匹配度
            if request.complexity in capability.complexity_handling:
                score += 2
            
            # 紧急度匹配度
            if request.urgency in capability.urgency_handling:
                score += 2
            
            # 性能分数
            score += capability.performance_score
            
            # 负载情况（负载越低分数越高）
            load_factor = 1 - (capability.current_load / capability.load_capacity)
            score += load_factor
            
            scores[agent] = score
        
        # 选择分数最高的智能体
        return max(scores, key=scores.get) if scores else AgentType.XIAOAI
    
    def _select_secondary_agents(
        self,
        candidates: List[AgentType],
        primary_agent: AgentType,
        request: RoutingRequest
    ) -> List[AgentType]:
        """选择次要智能体"""
        secondary_agents = []
        
        # 移除主要智能体
        remaining_candidates = [agent for agent in candidates if agent != primary_agent]
        
        # 根据任务复杂度和紧急度决定是否需要协作
        need_collaboration = (
            request.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.EXPERT] or
            request.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL] or
            len(request.multimodal_data) > 1
        )
        
        if need_collaboration and remaining_candidates:
            # 选择最多2个次要智能体
            for agent in remaining_candidates[:2]:
                capability = self.agent_manager.get_agent_capability(agent)
                if capability and capability.availability:
                    secondary_agents.append(agent)
        
        return secondary_agents
    
    def _determine_collaboration_mode(
        self,
        request: RoutingRequest,
        primary_agent: AgentType,
        secondary_agents: List[AgentType]
    ) -> str:
        """确定协作模式"""
        if not secondary_agents:
            return "sequential"
        
        # 紧急情况使用并行模式
        if request.urgency == UrgencyLevel.CRITICAL:
            return "parallel"
        
        # 复杂病例使用分层模式
        if request.complexity == ComplexityLevel.EXPERT:
            return "hierarchical"
        
        # 诊断任务使用顺序模式
        if request.task_type in [TaskType.DIAGNOSIS, TaskType.TREATMENT]:
            return "sequential"
        
        # 默认使用咨询模式
        return "consultative"
    
    def _calculate_routing_confidence(
        self,
        primary_agent: AgentType,
        secondary_agents: List[AgentType],
        request: RoutingRequest
    ) -> float:
        """计算路由置信度"""
        confidence = 0.5  # 基础置信度
        
        # 主要智能体匹配度
        primary_capability = self.agent_manager.get_agent_capability(primary_agent)
        if primary_capability:
            if request.task_type in primary_capability.supported_tasks:
                confidence += 0.2
            if request.complexity in primary_capability.complexity_handling:
                confidence += 0.1
            if request.urgency in primary_capability.urgency_handling:
                confidence += 0.1
        
        # 协作智能体加成
        if secondary_agents:
            confidence += len(secondary_agents) * 0.05
        
        # 智能体性能加成
        performance_bonus = self.agent_manager.get_agent_performance(primary_agent) * 0.1
        confidence += performance_bonus
        
        return min(confidence, 1.0)
    
    def _generate_routing_reasoning(
        self,
        primary_agent: AgentType,
        secondary_agents: List[AgentType],
        request: RoutingRequest
    ) -> List[str]:
        """生成路由推理"""
        reasoning = []
        
        # 主要智能体选择原因
        primary_capability = self.agent_manager.get_agent_capability(primary_agent)
        if primary_capability:
            reasoning.append(f"选择{primary_agent.value}作为主要智能体，因为其擅长{', '.join(primary_capability.expertise_areas[:3])}")
        
        # 任务匹配原因
        reasoning.append(f"任务类型为{request.task_type.value}，复杂度为{request.complexity.value}，紧急度为{request.urgency.value}")
        
        # 协作原因
        if secondary_agents:
            agent_names = [agent.value for agent in secondary_agents]
            reasoning.append(f"协作智能体{', '.join(agent_names)}将提供专业支持")
        
        return reasoning
    
    def _estimate_processing_duration(
        self,
        request: RoutingRequest,
        primary_agent: AgentType,
        secondary_agents: List[AgentType]
    ) -> float:
        """估算处理时间"""
        base_duration = 30.0  # 基础处理时间（秒）
        
        # 复杂度影响
        complexity_multiplier = {
            ComplexityLevel.SIMPLE: 0.5,
            ComplexityLevel.MODERATE: 1.0,
            ComplexityLevel.COMPLEX: 1.5,
            ComplexityLevel.EXPERT: 2.0
        }
        base_duration *= complexity_multiplier.get(request.complexity, 1.0)
        
        # 紧急度影响（紧急情况可能需要更多时间进行仔细分析）
        urgency_multiplier = {
            UrgencyLevel.LOW: 0.8,
            UrgencyLevel.MEDIUM: 1.0,
            UrgencyLevel.HIGH: 1.2,
            UrgencyLevel.CRITICAL: 1.5
        }
        base_duration *= urgency_multiplier.get(request.urgency, 1.0)
        
        # 协作影响
        if secondary_agents:
            base_duration += len(secondary_agents) * 15.0  # 每个协作智能体增加15秒
        
        # 多模态数据影响
        if request.multimodal_data:
            base_duration += len(request.multimodal_data) * 10.0  # 每个模态增加10秒
        
        return base_duration


class CollaborationOrchestrator:
    """协作编排器"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
    
    async def create_collaboration_plan(
        self,
        routing_decision: RoutingDecision,
        request: RoutingRequest
    ) -> CollaborationPlan:
        """创建协作计划"""
        try:
            agents = [routing_decision.primary_agent] + routing_decision.secondary_agents
            
            # 生成工作流
            workflow = self._generate_workflow(routing_decision, request)
            
            # 确定依赖关系
            dependencies = self._determine_dependencies(routing_decision)
            
            # 设置质量门控
            quality_gates = self._setup_quality_gates(routing_decision, request)
            
            return CollaborationPlan(
                agents=agents,
                workflow=workflow,
                dependencies=dependencies,
                communication_protocol=self._get_communication_protocol(routing_decision.collaboration_mode),
                quality_gates=quality_gates,
                fallback_strategy=self._determine_fallback_strategy(request)
            )
            
        except Exception as e:
            logger.error(f"创建协作计划失败: {e}")
            # 返回简单的单智能体计划
            return CollaborationPlan(
                agents=[routing_decision.primary_agent],
                workflow=[{
                    "step": 1,
                    "agent": routing_decision.primary_agent.value,
                    "action": "process_request",
                    "timeout": 60
                }]
            )
    
    def _generate_workflow(
        self,
        routing_decision: RoutingDecision,
        request: RoutingRequest
    ) -> List[Dict[str, Any]]:
        """生成工作流"""
        workflow = []
        
        if routing_decision.collaboration_mode == "sequential":
            # 顺序工作流
            step = 1
            
            # 主要智能体处理
            workflow.append({
                "step": step,
                "agent": routing_decision.primary_agent.value,
                "action": "primary_processing",
                "timeout": 60,
                "description": "主要智能体进行初步处理"
            })
            step += 1
            
            # 次要智能体处理
            for agent in routing_decision.secondary_agents:
                workflow.append({
                    "step": step,
                    "agent": agent.value,
                    "action": "secondary_processing",
                    "timeout": 45,
                    "description": f"{agent.value}进行专业分析",
                    "depends_on": [step - 1]
                })
                step += 1
            
            # 结果整合
            if routing_decision.secondary_agents:
                workflow.append({
                    "step": step,
                    "agent": routing_decision.primary_agent.value,
                    "action": "result_integration",
                    "timeout": 30,
                    "description": "整合所有智能体的分析结果",
                    "depends_on": list(range(2, step))
                })
        
        elif routing_decision.collaboration_mode == "parallel":
            # 并行工作流
            step = 1
            
            # 所有智能体并行处理
            for agent in [routing_decision.primary_agent] + routing_decision.secondary_agents:
                workflow.append({
                    "step": step,
                    "agent": agent.value,
                    "action": "parallel_processing",
                    "timeout": 60,
                    "description": f"{agent.value}并行处理请求"
                })
                step += 1
            
            # 结果合并
            workflow.append({
                "step": step,
                "agent": routing_decision.primary_agent.value,
                "action": "result_merging",
                "timeout": 30,
                "description": "合并并行处理结果",
                "depends_on": list(range(1, step))
            })
        
        elif routing_decision.collaboration_mode == "hierarchical":
            # 分层工作流
            step = 1
            
            # 初级智能体处理
            for agent in routing_decision.secondary_agents:
                if agent != AgentType.LAOKE:  # 非专家智能体先处理
                    workflow.append({
                        "step": step,
                        "agent": agent.value,
                        "action": "initial_processing",
                        "timeout": 45,
                        "description": f"{agent.value}进行初步分析"
                    })
                    step += 1
            
            # 专家智能体审核
            workflow.append({
                "step": step,
                "agent": routing_decision.primary_agent.value,
                "action": "expert_review",
                "timeout": 60,
                "description": "专家智能体审核和指导",
                "depends_on": list(range(1, step))
            })
        
        return workflow
    
    def _determine_dependencies(self, routing_decision: RoutingDecision) -> Dict[str, List[str]]:
        """确定依赖关系"""
        dependencies = {}
        
        if routing_decision.collaboration_mode == "sequential":
            # 顺序依赖
            agents = [routing_decision.primary_agent] + routing_decision.secondary_agents
            for i, agent in enumerate(agents[1:], 1):
                dependencies[agent.value] = [agents[i-1].value]
        
        elif routing_decision.collaboration_mode == "hierarchical":
            # 分层依赖
            if routing_decision.primary_agent == AgentType.LAOKE:
                # 专家智能体依赖其他所有智能体
                dependencies[AgentType.LAOKE.value] = [
                    agent.value for agent in routing_decision.secondary_agents
                ]
        
        return dependencies
    
    def _setup_quality_gates(
        self,
        routing_decision: RoutingDecision,
        request: RoutingRequest
    ) -> List[Dict[str, Any]]:
        """设置质量门控"""
        quality_gates = []
        
        # 基础质量检查
        quality_gates.append({
            "name": "response_completeness",
            "description": "检查响应完整性",
            "criteria": {
                "min_length": 50,
                "required_fields": ["diagnosis", "recommendation"]
            }
        })
        
        # 专业性检查
        if request.task_type in [TaskType.DIAGNOSIS, TaskType.TREATMENT]:
            quality_gates.append({
                "name": "medical_accuracy",
                "description": "检查医学准确性",
                "criteria": {
                    "medical_terms_present": True,
                    "contraindications_checked": True
                }
            })
        
        # 安全性检查
        if request.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
            quality_gates.append({
                "name": "safety_check",
                "description": "安全性检查",
                "criteria": {
                    "emergency_protocols": True,
                    "risk_assessment": True
                }
            })
        
        return quality_gates
    
    def _get_communication_protocol(self, collaboration_mode: str) -> str:
        """获取通信协议"""
        protocols = {
            "sequential": "async",
            "parallel": "sync",
            "hierarchical": "hierarchical",
            "consultative": "request_response"
        }
        return protocols.get(collaboration_mode, "async")
    
    def _determine_fallback_strategy(self, request: RoutingRequest) -> str:
        """确定回退策略"""
        if request.urgency == UrgencyLevel.CRITICAL:
            return "escalate_immediately"
        elif request.complexity == ComplexityLevel.EXPERT:
            return "escalate_to_expert"
        else:
            return "retry_with_different_agent"


class IntelligentRouter:
    """智能路由器主类"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.agent_manager = AgentManager()
        self.task_analyzer = TaskAnalyzer()
        self.routing_engine = RoutingEngine(self.agent_manager)
        self.collaboration_orchestrator = CollaborationOrchestrator(self.agent_manager)
    
    async def route_and_orchestrate(
        self,
        request: RoutingRequest
    ) -> Tuple[RoutingDecision, CollaborationPlan]:
        """
        路由和编排请求
        
        Args:
            request: 路由请求
            
        Returns:
            路由决策和协作计划
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 分析请求
            analyzed_request = await self.task_analyzer.analyze_request(request)
            
            # 路由决策
            routing_decision = await self.routing_engine.route_request(analyzed_request)
            
            # 创建协作计划
            collaboration_plan = await self.collaboration_orchestrator.create_collaboration_plan(
                routing_decision, analyzed_request
            )
            
            # 更新智能体负载
            self._update_agent_loads(routing_decision)
            
            # 记录指标
            processing_time = asyncio.get_event_loop().time() - start_time
            await self._record_metrics(analyzed_request, routing_decision, processing_time)
            
            logger.info(
                f"路由完成: {analyzed_request.request_id} -> "
                f"主要智能体: {routing_decision.primary_agent.value}, "
                f"协作模式: {routing_decision.collaboration_mode}, "
                f"置信度: {routing_decision.confidence:.2f}"
            )
            
            return routing_decision, collaboration_plan
            
        except Exception as e:
            logger.error(f"路由和编排失败: {e}")
            # 返回默认路由
            default_decision = RoutingDecision(
                primary_agent=AgentType.XIAOAI,
                collaboration_mode="sequential",
                confidence=0.5,
                reasoning=[f"路由失败，使用默认配置: {str(e)}"]
            )
            default_plan = CollaborationPlan(
                agents=[AgentType.XIAOAI],
                workflow=[{
                    "step": 1,
                    "agent": AgentType.XIAOAI.value,
                    "action": "fallback_processing",
                    "timeout": 60
                }]
            )
            return default_decision, default_plan
    
    def _update_agent_loads(self, routing_decision: RoutingDecision):
        """更新智能体负载"""
        # 主要智能体负载增加
        self.agent_manager.update_agent_load(routing_decision.primary_agent, 10)
        
        # 次要智能体负载增加
        for agent in routing_decision.secondary_agents:
            self.agent_manager.update_agent_load(agent, 5)
    
    async def _record_metrics(
        self,
        request: RoutingRequest,
        routing_decision: RoutingDecision,
        processing_time: float
    ):
        """记录指标"""
        # 路由处理时间
        await self.metrics_collector.record_histogram(
            "routing_duration_seconds",
            processing_time,
            {
                "task_type": request.task_type.value,
                "complexity": request.complexity.value,
                "urgency": request.urgency.value
            }
        )
        
        # 路由置信度
        await self.metrics_collector.record_histogram(
            "routing_confidence_score",
            routing_decision.confidence,
            {"primary_agent": routing_decision.primary_agent.value}
        )
        
        # 智能体选择统计
        await self.metrics_collector.increment_counter(
            "agent_selection_total",
            {"agent": routing_decision.primary_agent.value}
        )
        
        # 协作模式统计
        await self.metrics_collector.increment_counter(
            "collaboration_mode_total",
            {"mode": routing_decision.collaboration_mode}
        )
        
        # 任务类型统计
        await self.metrics_collector.increment_counter(
            "task_type_total",
            {"task_type": request.task_type.value}
        )
    
    async def get_routing_statistics(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        stats = {
            "agent_capabilities": {},
            "agent_loads": {},
            "routing_rules_count": len(self.routing_engine.routing_rules),
            "collaboration_patterns_count": len(self.routing_engine.collaboration_patterns)
        }
        
        # 智能体能力统计
        for agent_type, capability in self.agent_manager.agents.items():
            stats["agent_capabilities"][agent_type.value] = {
                "supported_tasks": [task.value for task in capability.supported_tasks],
                "expertise_areas": capability.expertise_areas,
                "performance_score": capability.performance_score
            }
        
        # 智能体负载统计
        for agent_type, state in self.agent_manager.agent_states.items():
            stats["agent_loads"][agent_type.value] = state
        
        return stats 