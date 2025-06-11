"""
MCP增强版智能体协调器
实现基于MCP理念的实时协作决策引擎和共识算法
支持跨应用、跨系统的智能体协作
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import hashlib
from collections import defaultdict
import uuid

from .agent_orchestrator import AgentOrchestrator, CollaborationSession, AgentTask
from ..core.event_bus import SuokeEventBus

logger = logging.getLogger(__name__)

class ConsensusAlgorithm(Enum):
    """共识算法类型"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_CONSENSUS = "weighted_consensus"
    BYZANTINE_FAULT_TOLERANT = "byzantine_fault_tolerant"
    CONFIDENCE_BASED = "confidence_based"

class DecisionType(Enum):
    """决策类型"""
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    RECOMMENDATION = "recommendation"
    EMERGENCY = "emergency"
    LIFESTYLE = "lifestyle"

class AgentCapability(Enum):
    """智能体能力"""
    TCM_DIAGNOSIS = "tcm_diagnosis"
    SYMPTOM_ANALYSIS = "symptom_analysis"
    SERVICE_MATCHING = "service_matching"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    LIFESTYLE_ANALYSIS = "lifestyle_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    DATA_INTEGRATION = "data_integration"

@dataclass
class AgentDecision:
    """智能体决策"""
    agent_id: str
    agent_type: str
    decision_type: DecisionType
    decision_data: Dict[str, Any]
    confidence_score: float
    reasoning: str
    evidence: List[Dict[str, Any]]
    timestamp: datetime
    context_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "decision_type": self.decision_type.value,
            "decision_data": self.decision_data,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat(),
            "context_hash": self.context_hash
        }

@dataclass
class ConsensusResult:
    """共识结果"""
    consensus_id: str
    decision_type: DecisionType
    final_decision: Dict[str, Any]
    consensus_score: float
    participating_agents: List[str]
    algorithm_used: ConsensusAlgorithm
    individual_decisions: List[AgentDecision]
    convergence_time: float
    confidence_distribution: Dict[str, float]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "consensus_id": self.consensus_id,
            "decision_type": self.decision_type.value,
            "final_decision": self.final_decision,
            "consensus_score": self.consensus_score,
            "participating_agents": self.participating_agents,
            "algorithm_used": self.algorithm_used.value,
            "individual_decisions": [d.to_dict() for d in self.individual_decisions],
            "convergence_time": self.convergence_time,
            "confidence_distribution": self.confidence_distribution,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class ContextAwareness:
    """上下文感知"""
    user_context: Dict[str, Any]
    device_context: Dict[str, Any]
    environmental_context: Dict[str, Any]
    temporal_context: Dict[str, Any]
    health_context: Dict[str, Any]
    interaction_history: List[Dict[str, Any]]
    
    def get_context_hash(self) -> str:
        """获取上下文哈希"""
        context_str = json.dumps({
            "user": self.user_context,
            "device": self.device_context,
            "environment": self.environmental_context,
            "temporal": self.temporal_context,
            "health": self.health_context
        }, sort_keys=True)
        return hashlib.sha256(context_str.encode()).hexdigest()

class RealTimeDecisionEngine:
    """实时决策引擎"""
    
    def __init__(self):
        self.active_decisions: Dict[str, List[AgentDecision]] = defaultdict(list)
        self.consensus_history: List[ConsensusResult] = []
        self.agent_capabilities: Dict[str, Set[AgentCapability]] = {
            "xiaoai": {
                AgentCapability.TCM_DIAGNOSIS,
                AgentCapability.SYMPTOM_ANALYSIS,
                AgentCapability.RISK_ASSESSMENT
            },
            "xiaoke": {
                AgentCapability.SERVICE_MATCHING,
                AgentCapability.DATA_INTEGRATION
            },
            "laoke": {
                AgentCapability.KNOWLEDGE_RETRIEVAL,
                AgentCapability.SYMPTOM_ANALYSIS
            },
            "soer": {
                AgentCapability.LIFESTYLE_ANALYSIS,
                AgentCapability.DATA_INTEGRATION,
                AgentCapability.RISK_ASSESSMENT
            }
        }
        
    async def submit_decision(self, decision: AgentDecision, session_id: str) -> None:
        """提交智能体决策"""
        self.active_decisions[session_id].append(decision)
        logger.info(f"智能体 {decision.agent_id} 提交决策: {decision.decision_type.value}")
        
        # 检查是否可以开始共识
        await self._check_consensus_readiness(session_id, decision.decision_type)
        
    async def _check_consensus_readiness(self, session_id: str, decision_type: DecisionType) -> None:
        """检查共识准备状态"""
        decisions = [d for d in self.active_decisions[session_id] if d.decision_type == decision_type]
        
        # 获取具备相关能力的智能体
        required_capabilities = self._get_required_capabilities(decision_type)
        capable_agents = set()
        
        for agent_id, capabilities in self.agent_capabilities.items():
            if any(cap in capabilities for cap in required_capabilities):
                capable_agents.add(agent_id)
                
        # 检查是否有足够的决策
        decision_agents = {d.agent_id for d in decisions}
        
        if len(decision_agents.intersection(capable_agents)) >= len(capable_agents) * 0.6:  # 60%的智能体参与
            await self._trigger_consensus(session_id, decision_type, decisions)
            
    def _get_required_capabilities(self, decision_type: DecisionType) -> Set[AgentCapability]:
        """获取决策类型所需的能力"""
        capability_map = {
            DecisionType.DIAGNOSIS: {
                AgentCapability.TCM_DIAGNOSIS,
                AgentCapability.SYMPTOM_ANALYSIS,
                AgentCapability.RISK_ASSESSMENT
            },
            DecisionType.TREATMENT: {
                AgentCapability.TCM_DIAGNOSIS,
                AgentCapability.KNOWLEDGE_RETRIEVAL
            },
            DecisionType.RECOMMENDATION: {
                AgentCapability.SERVICE_MATCHING,
                AgentCapability.LIFESTYLE_ANALYSIS
            },
            DecisionType.EMERGENCY: {
                AgentCapability.RISK_ASSESSMENT,
                AgentCapability.SERVICE_MATCHING
            },
            DecisionType.LIFESTYLE: {
                AgentCapability.LIFESTYLE_ANALYSIS,
                AgentCapability.DATA_INTEGRATION
            }
        }
        return capability_map.get(decision_type, set())
        
    async def _trigger_consensus(self, session_id: str, decision_type: DecisionType, decisions: List[AgentDecision]) -> ConsensusResult:
        """触发共识算法"""
        start_time = datetime.utcnow()
        
        # 选择合适的共识算法
        algorithm = self._select_consensus_algorithm(decision_type, decisions)
        
        # 执行共识算法
        consensus_result = await self._execute_consensus(session_id, decision_type, decisions, algorithm)
        
        # 计算收敛时间
        consensus_result.convergence_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 保存共识结果
        self.consensus_history.append(consensus_result)
        
        # 清理已处理的决策
        self.active_decisions[session_id] = [
            d for d in self.active_decisions[session_id] 
            if d.decision_type != decision_type
        ]
        
        logger.info(f"共识完成: {consensus_result.consensus_id}, 算法: {algorithm.value}, 分数: {consensus_result.consensus_score}")
        
        return consensus_result
        
    def _select_consensus_algorithm(self, decision_type: DecisionType, decisions: List[AgentDecision]) -> ConsensusAlgorithm:
        """选择共识算法"""
        # 根据决策类型和参与情况选择算法
        if decision_type == DecisionType.EMERGENCY:
            return ConsensusAlgorithm.CONFIDENCE_BASED  # 紧急情况优先高置信度
        elif len(decisions) >= 3:
            return ConsensusAlgorithm.WEIGHTED_CONSENSUS  # 多智能体加权共识
        else:
            return ConsensusAlgorithm.MAJORITY_VOTE  # 简单多数投票
            
    async def _execute_consensus(self, session_id: str, decision_type: DecisionType, 
                               decisions: List[AgentDecision], algorithm: ConsensusAlgorithm) -> ConsensusResult:
        """执行共识算法"""
        consensus_id = f"consensus_{session_id}_{decision_type.value}_{int(datetime.utcnow().timestamp())}"
        
        if algorithm == ConsensusAlgorithm.MAJORITY_VOTE:
            return await self._majority_vote_consensus(consensus_id, decision_type, decisions)
        elif algorithm == ConsensusAlgorithm.WEIGHTED_CONSENSUS:
            return await self._weighted_consensus(consensus_id, decision_type, decisions)
        elif algorithm == ConsensusAlgorithm.CONFIDENCE_BASED:
            return await self._confidence_based_consensus(consensus_id, decision_type, decisions)
        else:
            return await self._byzantine_fault_tolerant_consensus(consensus_id, decision_type, decisions)
            
    async def _majority_vote_consensus(self, consensus_id: str, decision_type: DecisionType, 
                                     decisions: List[AgentDecision]) -> ConsensusResult:
        """多数投票共识"""
        # 统计决策选项
        decision_counts = defaultdict(int)
        decision_details = defaultdict(list)
        
        for decision in decisions:
            key = json.dumps(decision.decision_data, sort_keys=True)
            decision_counts[key] += 1
            decision_details[key].append(decision)
            
        # 找到多数选择
        majority_key = max(decision_counts.keys(), key=lambda k: decision_counts[k])
        majority_decisions = decision_details[majority_key]
        
        # 计算共识分数
        consensus_score = decision_counts[majority_key] / len(decisions)
        
        # 生成最终决策
        final_decision = json.loads(majority_key)
        
        # 计算置信度分布
        confidence_distribution = {
            d.agent_id: d.confidence_score for d in majority_decisions
        }
        
        return ConsensusResult(
            consensus_id=consensus_id,
            decision_type=decision_type,
            final_decision=final_decision,
            consensus_score=consensus_score,
            participating_agents=[d.agent_id for d in decisions],
            algorithm_used=ConsensusAlgorithm.MAJORITY_VOTE,
            individual_decisions=decisions,
            convergence_time=0.0,  # 将在外部设置
            confidence_distribution=confidence_distribution,
            timestamp=datetime.utcnow()
        )
        
    async def _weighted_consensus(self, consensus_id: str, decision_type: DecisionType, 
                                decisions: List[AgentDecision]) -> ConsensusResult:
        """加权共识算法"""
        # 智能体权重（基于专业领域）
        agent_weights = {
            "xiaoai": 0.4,  # 中医诊断专家，权重最高
            "xiaoke": 0.25, # 服务匹配专家
            "laoke": 0.2,   # 知识支持专家
            "soer": 0.15    # 生活方式专家
        }
        
        # 根据决策类型调整权重
        if decision_type == DecisionType.DIAGNOSIS:
            agent_weights["xiaoai"] = 0.5
            agent_weights["xiaoke"] = 0.2
        elif decision_type == DecisionType.RECOMMENDATION:
            agent_weights["xiaoke"] = 0.4
            agent_weights["xiaoai"] = 0.3
        elif decision_type == DecisionType.LIFESTYLE:
            agent_weights["soer"] = 0.4
            agent_weights["xiaoai"] = 0.3
            
        # 计算加权决策
        weighted_decisions = defaultdict(float)
        decision_details = defaultdict(list)
        
        for decision in decisions:
            key = json.dumps(decision.decision_data, sort_keys=True)
            weight = agent_weights.get(decision.agent_id, 0.1)
            confidence_weight = decision.confidence_score * weight
            
            weighted_decisions[key] += confidence_weight
            decision_details[key].append(decision)
            
        # 找到加权最高的决策
        best_key = max(weighted_decisions.keys(), key=lambda k: weighted_decisions[k])
        best_decisions = decision_details[best_key]
        
        # 计算共识分数
        total_weight = sum(agent_weights.get(d.agent_id, 0.1) for d in decisions)
        consensus_score = weighted_decisions[best_key] / total_weight
        
        final_decision = json.loads(best_key)
        
        confidence_distribution = {
            d.agent_id: d.confidence_score for d in best_decisions
        }
        
        return ConsensusResult(
            consensus_id=consensus_id,
            decision_type=decision_type,
            final_decision=final_decision,
            consensus_score=consensus_score,
            participating_agents=[d.agent_id for d in decisions],
            algorithm_used=ConsensusAlgorithm.WEIGHTED_CONSENSUS,
            individual_decisions=decisions,
            convergence_time=0.0,
            confidence_distribution=confidence_distribution,
            timestamp=datetime.utcnow()
        )
        
    async def _confidence_based_consensus(self, consensus_id: str, decision_type: DecisionType, 
                                        decisions: List[AgentDecision]) -> ConsensusResult:
        """基于置信度的共识"""
        # 选择置信度最高的决策
        best_decision = max(decisions, key=lambda d: d.confidence_score)
        
        # 计算支持该决策的智能体比例
        best_key = json.dumps(best_decision.decision_data, sort_keys=True)
        supporting_decisions = [
            d for d in decisions 
            if json.dumps(d.decision_data, sort_keys=True) == best_key
        ]
        
        consensus_score = len(supporting_decisions) / len(decisions)
        
        confidence_distribution = {
            d.agent_id: d.confidence_score for d in supporting_decisions
        }
        
        return ConsensusResult(
            consensus_id=consensus_id,
            decision_type=decision_type,
            final_decision=best_decision.decision_data,
            consensus_score=consensus_score,
            participating_agents=[d.agent_id for d in decisions],
            algorithm_used=ConsensusAlgorithm.CONFIDENCE_BASED,
            individual_decisions=decisions,
            convergence_time=0.0,
            confidence_distribution=confidence_distribution,
            timestamp=datetime.utcnow()
        )
        
    async def _byzantine_fault_tolerant_consensus(self, consensus_id: str, decision_type: DecisionType, 
                                                decisions: List[AgentDecision]) -> ConsensusResult:
        """拜占庭容错共识"""
        # 简化的拜占庭容错算法
        # 需要至少2/3的智能体达成一致
        
        decision_groups = defaultdict(list)
        for decision in decisions:
            key = json.dumps(decision.decision_data, sort_keys=True)
            decision_groups[key].append(decision)
            
        # 找到满足2/3条件的决策组
        required_count = len(decisions) * 2 // 3 + 1
        valid_groups = {k: v for k, v in decision_groups.items() if len(v) >= required_count}
        
        if valid_groups:
            # 选择置信度最高的组
            best_key = max(valid_groups.keys(), 
                          key=lambda k: sum(d.confidence_score for d in valid_groups[k]))
            best_group = valid_groups[best_key]
            
            consensus_score = len(best_group) / len(decisions)
            final_decision = json.loads(best_key)
        else:
            # 没有达成2/3共识，选择置信度最高的决策
            best_decision = max(decisions, key=lambda d: d.confidence_score)
            best_group = [best_decision]
            consensus_score = 1.0 / len(decisions)
            final_decision = best_decision.decision_data
            
        confidence_distribution = {
            d.agent_id: d.confidence_score for d in best_group
        }
        
        return ConsensusResult(
            consensus_id=consensus_id,
            decision_type=decision_type,
            final_decision=final_decision,
            consensus_score=consensus_score,
            participating_agents=[d.agent_id for d in decisions],
            algorithm_used=ConsensusAlgorithm.BYZANTINE_FAULT_TOLERANT,
            individual_decisions=decisions,
            convergence_time=0.0,
            confidence_distribution=confidence_distribution,
            timestamp=datetime.utcnow()
        )

class ContextAwarenessEngine:
    """上下文感知引擎"""
    
    def __init__(self):
        self.context_cache: Dict[str, ContextAwareness] = {}
        self.context_history: List[Tuple[str, ContextAwareness]] = []
        
    async def build_context(self, user_id: str, session_id: str, 
                          additional_context: Dict[str, Any] = None) -> ContextAwareness:
        """构建上下文感知"""
        current_time = datetime.utcnow()
        
        # 用户上下文
        user_context = {
            "user_id": user_id,
            "session_id": session_id,
            "current_time": current_time.isoformat(),
            "timezone": "UTC+8",  # 默认中国时区
            **(additional_context or {})
        }
        
        # 设备上下文（模拟）
        device_context = {
            "primary_device": "smartphone",
            "connected_devices": ["apple_watch", "fitbit", "xiaomi_band"],
            "device_capabilities": ["heart_rate", "steps", "sleep", "blood_oxygen"],
            "network_status": "connected",
            "battery_levels": {"smartphone": 85, "apple_watch": 60, "fitbit": 78}
        }
        
        # 环境上下文
        environmental_context = {
            "location": "home",  # 可以从GPS或用户设置获取
            "weather": "sunny",  # 可以从天气API获取
            "air_quality": "good",
            "noise_level": "quiet",
            "time_of_day": self._get_time_period(current_time)
        }
        
        # 时间上下文
        temporal_context = {
            "current_hour": current_time.hour,
            "day_of_week": current_time.weekday(),
            "is_weekend": current_time.weekday() >= 5,
            "season": self._get_season(current_time),
            "meal_time": self._get_meal_time(current_time)
        }
        
        # 健康上下文（从历史数据获取）
        health_context = await self._get_health_context(user_id)
        
        # 交互历史
        interaction_history = await self._get_interaction_history(user_id, limit=10)
        
        context = ContextAwareness(
            user_context=user_context,
            device_context=device_context,
            environmental_context=environmental_context,
            temporal_context=temporal_context,
            health_context=health_context,
            interaction_history=interaction_history
        )
        
        # 缓存上下文
        self.context_cache[session_id] = context
        self.context_history.append((session_id, context))
        
        return context
        
    def _get_time_period(self, dt: datetime) -> str:
        """获取时间段"""
        hour = dt.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
            
    def _get_season(self, dt: datetime) -> str:
        """获取季节"""
        month = dt.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
            
    def _get_meal_time(self, dt: datetime) -> str:
        """获取用餐时间"""
        hour = dt.hour
        if 6 <= hour < 10:
            return "breakfast"
        elif 11 <= hour < 14:
            return "lunch"
        elif 17 <= hour < 20:
            return "dinner"
        else:
            return "snack"
            
    async def _get_health_context(self, user_id: str) -> Dict[str, Any]:
        """获取健康上下文"""
        # 模拟从健康数据服务获取
        return {
            "recent_vitals": {
                "heart_rate": 72,
                "blood_pressure": "120/80",
                "temperature": 36.5,
                "weight": 65.0
            },
            "health_trends": {
                "sleep_quality": "good",
                "stress_level": "low",
                "activity_level": "moderate"
            },
            "medical_history": {
                "chronic_conditions": [],
                "allergies": [],
                "medications": []
            },
            "tcm_constitution": "平和质",
            "last_diagnosis": "健康"
        }
        
    async def _get_interaction_history(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取交互历史"""
        # 模拟从数据库获取交互历史
        return [
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "interaction_type": "health_query",
                "content": f"查询健康状态 {i}",
                "result": "successful"
            }
            for i in range(limit)
        ]

class MCPEnhancedOrchestrator(AgentOrchestrator):
    """MCP增强版智能体协调器"""
    
    def __init__(self, event_bus: SuokeEventBus):
        super().__init__(event_bus)
        self.decision_engine = RealTimeDecisionEngine()
        self.context_engine = ContextAwarenessEngine()
        self.cross_validation_enabled = True
        self.real_time_sync_enabled = True
        
    async def start_mcp_collaboration(self, scenario: str, user_id: str, 
                                    context: Dict[str, Any] = None) -> str:
        """启动MCP增强协作"""
        # 构建上下文感知
        session_id = await super().start_collaboration(scenario, user_id, context)
        
        # 增强上下文感知
        enhanced_context = await self.context_engine.build_context(user_id, session_id, context)
        
        # 更新会话上下文
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.context.update({
                "mcp_enhanced": True,
                "context_hash": enhanced_context.get_context_hash(),
                "enhanced_context": enhanced_context
            })
            
        logger.info(f"启动MCP增强协作: {session_id}, 上下文哈希: {enhanced_context.get_context_hash()}")
        
        return session_id
        
    async def submit_agent_decision(self, session_id: str, agent_id: str, agent_type: str,
                                  decision_type: DecisionType, decision_data: Dict[str, Any],
                                  confidence_score: float, reasoning: str = "",
                                  evidence: List[Dict[str, Any]] = None) -> None:
        """提交智能体决策"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"会话 {session_id} 不存在")
            
        # 获取上下文哈希
        enhanced_context = session.context.get("enhanced_context")
        context_hash = enhanced_context.get_context_hash() if enhanced_context else ""
        
        # 创建决策对象
        decision = AgentDecision(
            agent_id=agent_id,
            agent_type=agent_type,
            decision_type=decision_type,
            decision_data=decision_data,
            confidence_score=confidence_score,
            reasoning=reasoning,
            evidence=evidence or [],
            timestamp=datetime.utcnow(),
            context_hash=context_hash
        )
        
        # 提交到决策引擎
        await self.decision_engine.submit_decision(decision, session_id)
        
        # 如果启用了交叉验证，触发验证流程
        if self.cross_validation_enabled:
            await self._trigger_cross_validation(session_id, decision)
            
    async def _trigger_cross_validation(self, session_id: str, decision: AgentDecision) -> None:
        """触发交叉验证"""
        # 找到其他具备相关能力的智能体
        required_capabilities = self.decision_engine._get_required_capabilities(decision.decision_type)
        
        for agent_id, capabilities in self.decision_engine.agent_capabilities.items():
            if (agent_id != decision.agent_id and 
                any(cap in capabilities for cap in required_capabilities)):
                
                # 请求交叉验证
                await self.event_bus.publish(
                    "agent.cross_validation.requested",
                    {
                        "session_id": session_id,
                        "original_decision": decision.to_dict(),
                        "validator_agent": agent_id,
                        "validation_type": "peer_review"
                    }
                )
                
    async def get_consensus_result(self, session_id: str, decision_type: DecisionType) -> Optional[ConsensusResult]:
        """获取共识结果"""
        # 从决策引擎的历史记录中查找
        for consensus in self.decision_engine.consensus_history:
            if (consensus.decision_type == decision_type and 
                session_id in consensus.consensus_id):
                return consensus
        return None
        
    async def get_real_time_status(self, session_id: str) -> Dict[str, Any]:
        """获取实时状态"""
        base_status = await super().get_session_status(session_id)
        if not base_status:
            return None
            
        # 添加MCP增强信息
        active_decisions = self.decision_engine.active_decisions.get(session_id, [])
        
        mcp_status = {
            "mcp_enhanced": True,
            "active_decisions": len(active_decisions),
            "decision_types": list(set(d.decision_type.value for d in active_decisions)),
            "consensus_ready": {},
            "context_awareness": {
                "context_cached": session_id in self.context_engine.context_cache,
                "last_context_update": datetime.utcnow().isoformat()
            },
            "real_time_sync": self.real_time_sync_enabled
        }
        
        # 检查各决策类型的共识准备状态
        for decision_type in DecisionType:
            type_decisions = [d for d in active_decisions if d.decision_type == decision_type]
            required_capabilities = self.decision_engine._get_required_capabilities(decision_type)
            capable_agents = set()
            
            for agent_id, capabilities in self.decision_engine.agent_capabilities.items():
                if any(cap in capabilities for cap in required_capabilities):
                    capable_agents.add(agent_id)
                    
            decision_agents = {d.agent_id for d in type_decisions}
            readiness = len(decision_agents.intersection(capable_agents)) / len(capable_agents) if capable_agents else 0
            
            mcp_status["consensus_ready"][decision_type.value] = {
                "readiness_percentage": readiness * 100,
                "participating_agents": list(decision_agents),
                "required_agents": list(capable_agents),
                "decisions_count": len(type_decisions)
            }
            
        base_status.update(mcp_status)
        return base_status
        
    async def export_collaboration_analytics(self, session_id: str) -> Dict[str, Any]:
        """导出协作分析数据"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {}
            
        # 收集共识结果
        consensus_results = [
            c.to_dict() for c in self.decision_engine.consensus_history
            if session_id in c.consensus_id
        ]
        
        # 分析协作效率
        if consensus_results:
            avg_convergence_time = sum(c["convergence_time"] for c in consensus_results) / len(consensus_results)
            avg_consensus_score = sum(c["consensus_score"] for c in consensus_results) / len(consensus_results)
        else:
            avg_convergence_time = 0
            avg_consensus_score = 0
            
        # 智能体参与度分析
        agent_participation = defaultdict(int)
        for consensus in consensus_results:
            for agent in consensus["participating_agents"]:
                agent_participation[agent] += 1
                
        analytics = {
            "session_id": session_id,
            "collaboration_summary": {
                "total_consensus": len(consensus_results),
                "avg_convergence_time": avg_convergence_time,
                "avg_consensus_score": avg_consensus_score,
                "session_duration": (datetime.utcnow() - session.created_at).total_seconds()
            },
            "agent_participation": dict(agent_participation),
            "consensus_results": consensus_results,
            "context_analysis": {
                "context_changes": len(self.context_engine.context_history),
                "context_stability": "high"  # 可以基于上下文变化频率计算
            },
            "algorithm_usage": {
                alg.value: sum(1 for c in consensus_results if c["algorithm_used"] == alg.value)
                for alg in ConsensusAlgorithm
            }
        }
        
        return analytics 