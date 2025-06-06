"""
collaborative_decision_bus - 索克生活项目模块
"""

            import aiohttp
from ..common.service_registry.agent_discovery import (
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from uuid import uuid4
import aioredis
import asyncio
import json
import logging

#!/usr/bin/env python3
"""
四智能体协同决策总线
实现小艾、小克、老克、索儿之间的协同决策机制
"""



    AgentType, CapabilityType, AgentServiceRegistry, get_agent_registry
)

logger = logging.getLogger(__name__)

class DecisionType(Enum):
    """决策类型"""
    HEALTH_ASSESSMENT = "health_assessment"        # 健康评估
    DIAGNOSIS_ANALYSIS = "diagnosis_analysis"      # 诊断分析
    TREATMENT_PLANNING = "treatment_planning"      # 治疗规划
    LIFESTYLE_GUIDANCE = "lifestyle_guidance"      # 生活方式指导
    EMERGENCY_RESPONSE = "emergency_response"      # 应急响应
    PREVENTIVE_CARE = "preventive_care"           # 预防保健
    SYNDROME_DIFFERENTIATION = "syndrome_diff"     # 中医辨证

class DecisionPriority(Enum):
    """决策优先级"""
    EMERGENCY = "emergency"      # 紧急
    HIGH = "high"               # 高
    MEDIUM = "medium"           # 中
    LOW = "low"                 # 低

class DecisionStatus(Enum):
    """决策状态"""
    PENDING = "pending"         # 待处理
    IN_PROGRESS = "in_progress" # 处理中
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"     # 已取消

class VotingStrategy(Enum):
    """投票策略"""
    UNANIMOUS = "unanimous"     # 一致同意
    MAJORITY = "majority"       # 多数决
    WEIGHTED = "weighted"       # 加权投票
    EXPERT_LEAD = "expert_lead" # 专家主导

@dataclass
class DecisionContext:
    """决策上下文"""
    user_id: str
    session_id: str
    health_data: Dict[str, Any] = field(default_factory=dict)
    symptoms: List[str] = field(default_factory=list)
    medical_history: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentVote:
    """智能体投票"""
    agent_type: AgentType
    service_id: str
    confidence: float           # 置信度 0.0-1.0
    recommendation: Dict[str, Any]
    reasoning: str
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DecisionRequest:
    """决策请求"""
    request_id: str
    decision_type: DecisionType
    priority: DecisionPriority
    context: DecisionContext
    required_agents: Set[AgentType]
    voting_strategy: VotingStrategy
    timeout_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionResult:
    """决策结果"""
    request_id: str
    status: DecisionStatus
    final_recommendation: Dict[str, Any]
    agent_votes: List[AgentVote]
    consensus_score: float      # 共识度 0.0-1.0
    execution_plan: Dict[str, Any] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class CollaborativeDecisionBus:
    """协同决策总线"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self.registry: Optional[AgentServiceRegistry] = None
        
        # 决策处理器
        self.active_decisions: Dict[str, DecisionRequest] = {}
        self.decision_results: Dict[str, DecisionResult] = {}
        
        # 智能体权重配置（基于专业领域）
        self.agent_weights = {
            DecisionType.HEALTH_ASSESSMENT: {
                AgentType.XIAOAI: 0.4,  # 小艾主导健康监测
                AgentType.XIAOKE: 0.3,  # 小克辅助分析
                AgentType.LAOKE: 0.2,   # 老克提供经验
                AgentType.SOER: 0.1     # 索儿生活建议
            },
            DecisionType.DIAGNOSIS_ANALYSIS: {
                AgentType.XIAOKE: 0.4,  # 小克主导诊断
                AgentType.LAOKE: 0.3,   # 老克中医辨证
                AgentType.XIAOAI: 0.2,  # 小艾数据支持
                AgentType.SOER: 0.1     # 索儿生活因素
            },
            DecisionType.TREATMENT_PLANNING: {
                AgentType.LAOKE: 0.4,   # 老克主导治疗
                AgentType.XIAOKE: 0.3,  # 小克现代医学
                AgentType.SOER: 0.2,    # 索儿生活调理
                AgentType.XIAOAI: 0.1   # 小艾监测建议
            },
            DecisionType.LIFESTYLE_GUIDANCE: {
                AgentType.SOER: 0.4,    # 索儿主导生活方式
                AgentType.LAOKE: 0.3,   # 老克养生指导
                AgentType.XIAOAI: 0.2,  # 小艾健康监测
                AgentType.XIAOKE: 0.1   # 小克医学建议
            }
        }
        
        self._running = False
        
    async def initialize(self):
        """初始化协同决策总线"""
        try:
            self.redis = aioredis.from_url(self.redis_url)
            await self.redis.ping()
            
            self.registry = await get_agent_registry()
            
            logger.info("协同决策总线初始化成功")
            
            # 启动后台任务
            self._running = True
            asyncio.create_task(self._decision_processor())
            asyncio.create_task(self._timeout_monitor())
            
        except Exception as e:
            logger.error(f"协同决策总线初始化失败: {e}")
            raise
    
    async def submit_decision_request(self, request: DecisionRequest) -> str:
        """提交决策请求"""
        try:
            # 验证请求
            if not await self._validate_decision_request(request):
                raise ValueError("决策请求验证失败")
            
            # 存储请求
            self.active_decisions[request.request_id] = request
            
            # 发布决策请求事件
            await self._publish_decision_event("decision_requested", request)
            
            logger.info(f"决策请求已提交: {request.request_id} ({request.decision_type.value})")
            return request.request_id
            
        except Exception as e:
            logger.error(f"提交决策请求失败: {e}")
            raise
    
    async def get_decision_result(self, request_id: str) -> Optional[DecisionResult]:
        """获取决策结果"""
        return self.decision_results.get(request_id)
    
    async def cancel_decision(self, request_id: str) -> bool:
        """取消决策"""
        try:
            if request_id in self.active_decisions:
                request = self.active_decisions.pop(request_id)
                
                result = DecisionResult(
                    request_id=request_id,
                    status=DecisionStatus.CANCELLED,
                    final_recommendation={},
                    agent_votes=[],
                    consensus_score=0.0,
                    completed_at=datetime.now()
                )
                
                self.decision_results[request_id] = result
                
                await self._publish_decision_event("decision_cancelled", request)
                
                logger.info(f"决策已取消: {request_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"取消决策失败: {e}")
            return False
    
    async def _validate_decision_request(self, request: DecisionRequest) -> bool:
        """验证决策请求"""
        try:
            # 检查必需的智能体是否可用
            for agent_type in request.required_agents:
                services = await self.registry.discover_services(agent_type=agent_type)
                if not services:
                    logger.warning(f"智能体不可用: {agent_type.value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"验证决策请求失败: {e}")
            return False
    
    async def _decision_processor(self):
        """决策处理器后台任务"""
        while self._running:
            try:
                # 处理待处理的决策
                for request_id, request in list(self.active_decisions.items()):
                    if request_id not in self.decision_results:
                        await self._process_decision(request)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"决策处理器异常: {e}")
                await asyncio.sleep(5)
    
    async def _process_decision(self, request: DecisionRequest):
        """处理单个决策"""
        try:
            logger.info(f"开始处理决策: {request.request_id}")
            
            # 收集智能体投票
            votes = await self._collect_agent_votes(request)
            
            if not votes:
                # 没有收到任何投票
                result = DecisionResult(
                    request_id=request.request_id,
                    status=DecisionStatus.FAILED,
                    final_recommendation={},
                    agent_votes=[],
                    consensus_score=0.0,
                    completed_at=datetime.now(),
                    error_message="未收到智能体投票"
                )
            else:
                # 根据投票策略生成最终决策
                final_recommendation, consensus_score = await self._generate_final_decision(
                    request, votes
                )
                
                result = DecisionResult(
                    request_id=request.request_id,
                    status=DecisionStatus.COMPLETED,
                    final_recommendation=final_recommendation,
                    agent_votes=votes,
                    consensus_score=consensus_score,
                    completed_at=datetime.now()
                )
            
            # 存储结果
            self.decision_results[request.request_id] = result
            
            # 移除活跃决策
            self.active_decisions.pop(request.request_id, None)
            
            # 发布决策完成事件
            await self._publish_decision_event("decision_completed", request, result)
            
            logger.info(f"决策处理完成: {request.request_id}")
            
        except Exception as e:
            logger.error(f"处理决策失败: {e}")
            
            # 记录失败结果
            result = DecisionResult(
                request_id=request.request_id,
                status=DecisionStatus.FAILED,
                final_recommendation={},
                agent_votes=[],
                consensus_score=0.0,
                completed_at=datetime.now(),
                error_message=str(e)
            )
            
            self.decision_results[request.request_id] = result
            self.active_decisions.pop(request.request_id, None)
    
    async def _collect_agent_votes(self, request: DecisionRequest) -> List[AgentVote]:
        """收集智能体投票"""
        votes = []
        
        try:
            # 为每个必需的智能体发送决策请求
            vote_tasks = []
            
            for agent_type in request.required_agents:
                task = self._request_agent_vote(agent_type, request)
                vote_tasks.append(task)
            
            # 等待所有投票（带超时）
            try:
                vote_results = await asyncio.wait_for(
                    asyncio.gather(*vote_tasks, return_exceptions=True),
                    timeout=request.timeout_seconds
                )
                
                for result in vote_results:
                    if isinstance(result, AgentVote):
                        votes.append(result)
                    elif isinstance(result, Exception):
                        logger.warning(f"智能体投票失败: {result}")
                
            except asyncio.TimeoutError:
                logger.warning(f"决策请求超时: {request.request_id}")
            
        except Exception as e:
            logger.error(f"收集智能体投票失败: {e}")
        
        return votes
    
    async def _request_agent_vote(self, agent_type: AgentType, request: DecisionRequest) -> Optional[AgentVote]:
        """向特定智能体请求投票"""
        try:
            # 获取最佳服务实例
            service = await self.registry.get_best_service_for_capability(
                self._get_required_capability(request.decision_type)
            )
            
            if not service or service.agent_type != agent_type:
                # 如果没有找到合适的服务，尝试获取该类型的任意服务
                services = await self.registry.discover_services(agent_type=agent_type)
                if services:
                    service = services[0]
                else:
                    logger.warning(f"未找到可用的{agent_type.value}服务")
                    return None
            
            # 构建投票请求
            vote_request = {
                "request_id": request.request_id,
                "decision_type": request.decision_type.value,
                "context": {
                    "user_id": request.context.user_id,
                    "session_id": request.context.session_id,
                    "health_data": request.context.health_data,
                    "symptoms": request.context.symptoms,
                    "medical_history": request.context.medical_history,
                    "preferences": request.context.preferences,
                    "constraints": request.context.constraints,
                    "metadata": request.context.metadata
                },
                "timeout": 30  # 单个智能体投票超时
            }
            
            # 发送投票请求（这里应该调用实际的智能体服务API）
            vote = await self._call_agent_service(service, vote_request)
            
            return vote
            
        except Exception as e:
            logger.error(f"请求{agent_type.value}投票失败: {e}")
            return None
    
    async def _call_agent_service(self, service, vote_request: Dict[str, Any]) -> Optional[AgentVote]:
        """调用智能体服务API"""
        try:
            
            url = f"http://{service.host}:{service.port}/api/v1/vote"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=vote_request,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return AgentVote(
                            agent_type=service.agent_type,
                            service_id=service.service_id,
                            confidence=data.get("confidence", 0.5),
                            recommendation=data.get("recommendation", {}),
                            reasoning=data.get("reasoning", ""),
                            supporting_evidence=data.get("supporting_evidence", []),
                            timestamp=datetime.now()
                        )
                    else:
                        logger.warning(f"智能体服务返回错误状态: {response.status}")
                        return None
            
        except Exception as e:
            logger.error(f"调用智能体服务失败: {e}")
            return None
    
    async def _generate_final_decision(
        self, 
        request: DecisionRequest, 
        votes: List[AgentVote]
    ) -> tuple[Dict[str, Any], float]:
        """生成最终决策"""
        try:
            if request.voting_strategy == VotingStrategy.WEIGHTED:
                return await self._weighted_voting(request, votes)
            elif request.voting_strategy == VotingStrategy.MAJORITY:
                return await self._majority_voting(request, votes)
            elif request.voting_strategy == VotingStrategy.UNANIMOUS:
                return await self._unanimous_voting(request, votes)
            elif request.voting_strategy == VotingStrategy.EXPERT_LEAD:
                return await self._expert_lead_voting(request, votes)
            else:
                # 默认使用加权投票
                return await self._weighted_voting(request, votes)
                
        except Exception as e:
            logger.error(f"生成最终决策失败: {e}")
            return {}, 0.0
    
    async def _weighted_voting(self, request: DecisionRequest, votes: List[AgentVote]) -> tuple[Dict[str, Any], float]:
        """加权投票"""
        weights = self.agent_weights.get(request.decision_type, {})
        
        # 计算加权推荐
        weighted_recommendations = {}
        total_weight = 0.0
        consensus_scores = []
        
        for vote in votes:
            weight = weights.get(vote.agent_type, 0.25)  # 默认权重
            confidence_weight = weight * vote.confidence
            total_weight += confidence_weight
            
            # 合并推荐内容
            for key, value in vote.recommendation.items():
                if key not in weighted_recommendations:
                    weighted_recommendations[key] = []
                weighted_recommendations[key].append({
                    "value": value,
                    "weight": confidence_weight,
                    "agent": vote.agent_type.value,
                    "reasoning": vote.reasoning
                })
            
            consensus_scores.append(vote.confidence)
        
        # 生成最终推荐
        final_recommendation = {}
        for key, values in weighted_recommendations.items():
            if len(values) == 1:
                final_recommendation[key] = values[0]["value"]
            else:
                # 选择权重最高的推荐
                best_value = max(values, key=lambda x: x["weight"])
                final_recommendation[key] = best_value["value"]
        
        # 计算共识度
        consensus_score = sum(consensus_scores) / len(consensus_scores) if consensus_scores else 0.0
        
        return final_recommendation, consensus_score
    
    async def _majority_voting(self, request: DecisionRequest, votes: List[AgentVote]) -> tuple[Dict[str, Any], float]:
        """多数决投票"""
        # 简化实现：选择置信度最高的推荐
        if not votes:
            return {}, 0.0
        
        best_vote = max(votes, key=lambda v: v.confidence)
        consensus_score = sum(v.confidence for v in votes) / len(votes)
        
        return best_vote.recommendation, consensus_score
    
    async def _unanimous_voting(self, request: DecisionRequest, votes: List[AgentVote]) -> tuple[Dict[str, Any], float]:
        """一致同意投票"""
        if not votes:
            return {}, 0.0
        
        # 检查是否所有投票都有足够的置信度
        min_confidence = 0.7
        if all(vote.confidence >= min_confidence for vote in votes):
            # 合并所有推荐
            final_recommendation = {}
            for vote in votes:
                final_recommendation.update(vote.recommendation)
            
            consensus_score = min(vote.confidence for vote in votes)
            return final_recommendation, consensus_score
        else:
            # 没有达成一致
            return {}, 0.0
    
    async def _expert_lead_voting(self, request: DecisionRequest, votes: List[AgentVote]) -> tuple[Dict[str, Any], float]:
        """专家主导投票"""
        weights = self.agent_weights.get(request.decision_type, {})
        
        # 找到权重最高的智能体
        expert_agent = max(weights.keys(), key=lambda agent: weights[agent])
        
        # 找到专家智能体的投票
        expert_vote = None
        for vote in votes:
            if vote.agent_type == expert_agent:
                expert_vote = vote
                break
        
        if expert_vote:
            # 使用专家推荐，但考虑其他智能体的意见调整置信度
            other_confidences = [v.confidence for v in votes if v.agent_type != expert_agent]
            if other_confidences:
                avg_other_confidence = sum(other_confidences) / len(other_confidences)
                consensus_score = (expert_vote.confidence + avg_other_confidence) / 2
            else:
                consensus_score = expert_vote.confidence
            
            return expert_vote.recommendation, consensus_score
        else:
            # 专家不可用，回退到加权投票
            return await self._weighted_voting(request, votes)
    
    def _get_required_capability(self, decision_type: DecisionType) -> CapabilityType:
        """获取决策类型对应的能力类型"""
        mapping = {
            DecisionType.HEALTH_ASSESSMENT: CapabilityType.HEALTH_MONITORING,
            DecisionType.DIAGNOSIS_ANALYSIS: CapabilityType.DIAGNOSIS,
            DecisionType.TREATMENT_PLANNING: CapabilityType.TREATMENT_PLAN,
            DecisionType.LIFESTYLE_GUIDANCE: CapabilityType.LIFESTYLE_ADVICE,
            DecisionType.EMERGENCY_RESPONSE: CapabilityType.EMERGENCY_RESPONSE,
            DecisionType.PREVENTIVE_CARE: CapabilityType.HEALTH_MONITORING,
            DecisionType.SYNDROME_DIFFERENTIATION: CapabilityType.SYMPTOM_ANALYSIS
        }
        return mapping.get(decision_type, CapabilityType.DATA_ANALYSIS)
    
    async def _timeout_monitor(self):
        """超时监控后台任务"""
        while self._running:
            try:
                current_time = datetime.now()
                
                # 检查超时的决策
                expired_requests = []
                for request_id, request in self.active_decisions.items():
                    if current_time - request.created_at > timedelta(seconds=request.timeout_seconds):
                        expired_requests.append(request_id)
                
                # 处理超时决策
                for request_id in expired_requests:
                    request = self.active_decisions.pop(request_id, None)
                    if request:
                        result = DecisionResult(
                            request_id=request_id,
                            status=DecisionStatus.FAILED,
                            final_recommendation={},
                            agent_votes=[],
                            consensus_score=0.0,
                            completed_at=datetime.now(),
                            error_message="决策请求超时"
                        )
                        
                        self.decision_results[request_id] = result
                        
                        await self._publish_decision_event("decision_timeout", request)
                        
                        logger.warning(f"决策请求超时: {request_id}")
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"超时监控异常: {e}")
                await asyncio.sleep(5)
    
    async def _publish_decision_event(
        self, 
        event_type: str, 
        request: DecisionRequest, 
        result: Optional[DecisionResult] = None
    ):
        """发布决策事件"""
        try:
            event_data = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "request": {
                    "request_id": request.request_id,
                    "decision_type": request.decision_type.value,
                    "priority": request.priority.value,
                    "required_agents": [agent.value for agent in request.required_agents],
                    "voting_strategy": request.voting_strategy.value
                }
            }
            
            if result:
                event_data["result"] = {
                    "status": result.status.value,
                    "consensus_score": result.consensus_score,
                    "agent_count": len(result.agent_votes)
                }
            
            await self.redis.publish(
                "collaborative_decision_events",
                json.dumps(event_data)
            )
            
        except Exception as e:
            logger.error(f"发布决策事件失败: {e}")
    
    async def close(self):
        """关闭协同决策总线"""
        self._running = False
        if self.redis:
            await self.redis.close()

# 全局决策总线实例
_decision_bus: Optional[CollaborativeDecisionBus] = None

async def get_decision_bus() -> CollaborativeDecisionBus:
    """获取全局协同决策总线"""
    global _decision_bus
    if _decision_bus is None:
        _decision_bus = CollaborativeDecisionBus()
        await _decision_bus.initialize()
    return _decision_bus

async def submit_collaborative_decision(
    decision_type: DecisionType,
    user_id: str,
    session_id: str,
    health_data: Dict[str, Any] = None,
    symptoms: List[str] = None,
    priority: DecisionPriority = DecisionPriority.MEDIUM,
    voting_strategy: VotingStrategy = VotingStrategy.WEIGHTED,
    timeout_seconds: int = 300
) -> str:
    """提交协同决策请求的便捷函数"""
    bus = await get_decision_bus()
    
    # 根据决策类型确定需要的智能体
    required_agents = {AgentType.XIAOAI, AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER}
    
    # 特殊情况下可以减少必需的智能体
    if decision_type == DecisionType.EMERGENCY_RESPONSE:
        required_agents = {AgentType.XIAOAI, AgentType.XIAOKE}  # 紧急情况优先快速响应
    
    request = DecisionRequest(
        request_id=str(uuid4()),
        decision_type=decision_type,
        priority=priority,
        context=DecisionContext(
            user_id=user_id,
            session_id=session_id,
            health_data=health_data or {},
            symptoms=symptoms or []
        ),
        required_agents=required_agents,
        voting_strategy=voting_strategy,
        timeout_seconds=timeout_seconds
    )
    
    return await bus.submit_decision_request(request) 