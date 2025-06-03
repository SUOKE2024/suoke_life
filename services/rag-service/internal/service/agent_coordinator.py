#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能体协调器 - 管理四个智能体的协同工作和任务分配
"""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
from collections import defaultdict, deque

class AgentType(Enum):
    """智能体类型"""
    XIAOAI = "xiaoai"      # 小艾 - AI助手，负责基础健康咨询和用户交互
    XIAOKE = "xiaoke"      # 小克 - 专业诊断，负责症状分析和初步诊断
    LAOKE = "laoke"        # 老克 - 资深专家，负责复杂病例和深度分析
    SOER = "soer"          # 索儿 - 健康管理，负责预防保健和生活指导

class TaskType(Enum):
    """任务类型"""
    HEALTH_CONSULTATION = "health_consultation"      # 健康咨询
    SYMPTOM_ANALYSIS = "symptom_analysis"            # 症状分析
    DIAGNOSIS_SUPPORT = "diagnosis_support"          # 诊断支持
    TREATMENT_PLANNING = "treatment_planning"        # 治疗规划
    PREVENTION_GUIDANCE = "prevention_guidance"      # 预防指导
    LIFESTYLE_ADVICE = "lifestyle_advice"            # 生活建议
    EMERGENCY_RESPONSE = "emergency_response"        # 紧急响应
    KNOWLEDGE_QUERY = "knowledge_query"              # 知识查询
    DATA_ANALYSIS = "data_analysis"                  # 数据分析
    EDUCATION = "education"                          # 健康教育

class TaskPriority(Enum):
    """任务优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    EMERGENCY = 5

class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"          # 待处理
    ASSIGNED = "assigned"        # 已分配
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"           # 失败
    CANCELLED = "cancelled"      # 已取消
    ESCALATED = "escalated"      # 已升级

class CollaborationMode(Enum):
    """协作模式"""
    SEQUENTIAL = "sequential"    # 顺序协作
    PARALLEL = "parallel"        # 并行协作
    HIERARCHICAL = "hierarchical" # 层次协作
    CONSENSUS = "consensus"       # 共识协作

@dataclass
class Task:
    """任务"""
    id: str
    type: TaskType
    priority: TaskPriority
    status: TaskStatus
    title: str
    description: str
    user_id: str
    input_data: Dict[str, Any]
    created_at: datetime
    assigned_agents: List[AgentType] = field(default_factory=list)
    collaboration_mode: CollaborationMode = CollaborationMode.SEQUENTIAL
    deadline: Optional[datetime] = None
    estimated_duration: Optional[timedelta] = None
    actual_duration: Optional[timedelta] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentCapability:
    """智能体能力"""
    agent_type: AgentType
    task_types: List[TaskType]
    expertise_level: float  # 专业水平 (0-1)
    current_load: int       # 当前负载
    max_load: int          # 最大负载
    availability: bool     # 可用性
    response_time: float   # 平均响应时间（秒）
    success_rate: float    # 成功率 (0-1)
    specialties: List[str] = field(default_factory=list)

@dataclass
class CollaborationResult:
    """协作结果"""
    task_id: str
    participating_agents: List[AgentType]
    collaboration_mode: CollaborationMode
    individual_results: Dict[AgentType, Dict[str, Any]]
    consensus_result: Optional[Dict[str, Any]]
    confidence_score: float
    execution_time: timedelta
    success: bool
    error_message: Optional[str] = None

class AgentCoordinator:
    """智能体协调器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能体协调器
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # Redis连接
        self.redis_client = None
        
        # 智能体能力配置
        self.agent_capabilities = self._init_agent_capabilities()
        
        # 任务队列
        self.task_queue: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }
        
        # 活跃任务
        self.active_tasks: Dict[str, Task] = {}
        
        # 任务历史
        self.task_history: List[Task] = []
        
        # 协作历史
        self.collaboration_history: List[CollaborationResult] = []
        
        # 任务分配策略
        self.assignment_strategies = self._init_assignment_strategies()
        
        # 事件回调
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # 统计信息
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_completion_time": 0.0,
            "agent_utilization": defaultdict(float),
            "task_distribution": defaultdict(int),
            "collaboration_success_rate": 0.0
        }
    
    def _init_agent_capabilities(self) -> Dict[AgentType, AgentCapability]:
        """初始化智能体能力"""
        capabilities = {
            AgentType.XIAOAI: AgentCapability(
                agent_type=AgentType.XIAOAI,
                task_types=[
                    TaskType.HEALTH_CONSULTATION,
                    TaskType.KNOWLEDGE_QUERY,
                    TaskType.EDUCATION
                ],
                expertise_level=0.7,
                current_load=0,
                max_load=10,
                availability=True,
                response_time=2.0,
                success_rate=0.85,
                specialties=["用户交互", "基础咨询", "健康教育"]
            ),
            AgentType.XIAOKE: AgentCapability(
                agent_type=AgentType.XIAOKE,
                task_types=[
                    TaskType.SYMPTOM_ANALYSIS,
                    TaskType.DIAGNOSIS_SUPPORT,
                    TaskType.DATA_ANALYSIS
                ],
                expertise_level=0.8,
                current_load=0,
                max_load=8,
                availability=True,
                response_time=5.0,
                success_rate=0.88,
                specialties=["症状分析", "初步诊断", "数据分析"]
            ),
            AgentType.LAOKE: AgentCapability(
                agent_type=AgentType.LAOKE,
                task_types=[
                    TaskType.DIAGNOSIS_SUPPORT,
                    TaskType.TREATMENT_PLANNING,
                    TaskType.EMERGENCY_RESPONSE
                ],
                expertise_level=0.95,
                current_load=0,
                max_load=5,
                availability=True,
                response_time=10.0,
                success_rate=0.95,
                specialties=["复杂诊断", "治疗方案", "疑难病例"]
            ),
            AgentType.SOER: AgentCapability(
                agent_type=AgentType.SOER,
                task_types=[
                    TaskType.PREVENTION_GUIDANCE,
                    TaskType.LIFESTYLE_ADVICE,
                    TaskType.DATA_ANALYSIS
                ],
                expertise_level=0.75,
                current_load=0,
                max_load=12,
                availability=True,
                response_time=3.0,
                success_rate=0.82,
                specialties=["预防保健", "生活指导", "健康管理"]
            )
        }
        
        return capabilities
    
    def _init_assignment_strategies(self) -> Dict[str, Callable]:
        """初始化任务分配策略"""
        return {
            "capability_based": self._assign_by_capability,
            "load_balanced": self._assign_by_load_balance,
            "expertise_weighted": self._assign_by_expertise,
            "response_time_optimized": self._assign_by_response_time,
            "collaborative": self._assign_collaborative
        }
    
    async def initialize(self):
        """初始化协调器"""
        logger.info("Initializing agent coordinator")
        
        # 初始化Redis连接
        redis_config = self.config.get('redis', {})
        self.redis_client = redis.Redis(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            decode_responses=True
        )
        
        # 启动任务处理循环
        asyncio.create_task(self._task_processing_loop())
        asyncio.create_task(self._monitoring_loop())
        asyncio.create_task(self._cleanup_loop())
        
        logger.info("Agent coordinator initialized successfully")
    
    async def submit_task(
        self,
        task_type: TaskType,
        title: str,
        description: str,
        user_id: str,
        input_data: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: Optional[datetime] = None,
        collaboration_mode: CollaborationMode = CollaborationMode.SEQUENTIAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交任务
        
        Args:
            task_type: 任务类型
            title: 任务标题
            description: 任务描述
            user_id: 用户ID
            input_data: 输入数据
            priority: 优先级
            deadline: 截止时间
            collaboration_mode: 协作模式
            metadata: 元数据
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_type,
            priority=priority,
            status=TaskStatus.PENDING,
            title=title,
            description=description,
            user_id=user_id,
            input_data=input_data,
            created_at=datetime.now(),
            deadline=deadline,
            collaboration_mode=collaboration_mode,
            metadata=metadata or {}
        )
        
        # 添加到任务队列
        self.task_queue[priority].append(task)
        
        # 存储到Redis
        await self._store_task(task)
        
        # 触发事件
        await self._trigger_event("task_submitted", {"task": task})
        
        # 更新统计信息
        self.stats["total_tasks"] += 1
        self.stats["task_distribution"][task_type.value] += 1
        
        logger.info(f"Task submitted: {task_id} - {title}")
        return task_id
    
    async def _task_processing_loop(self):
        """任务处理循环"""
        while True:
            try:
                # 按优先级处理任务
                for priority in reversed(list(TaskPriority)):
                    if self.task_queue[priority]:
                        task = self.task_queue[priority].popleft()
                        await self._process_task(task)
                
                await asyncio.sleep(1)  # 避免过度占用CPU
                
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_task(self, task: Task):
        """处理单个任务"""
        try:
            logger.info(f"Processing task: {task.id} - {task.title}")
            
            # 分配智能体
            assigned_agents = await self._assign_agents(task)
            if not assigned_agents:
                logger.warning(f"No agents available for task: {task.id}")
                task.status = TaskStatus.FAILED
                task.results = {"error": "No agents available"}
                return
            
            task.assigned_agents = assigned_agents
            task.status = TaskStatus.ASSIGNED
            task.started_at = datetime.now()
            
            # 添加到活跃任务
            self.active_tasks[task.id] = task
            
            # 更新智能体负载
            for agent_type in assigned_agents:
                self.agent_capabilities[agent_type].current_load += 1
            
            # 触发事件
            await self._trigger_event("task_assigned", {"task": task})
            
            # 执行任务
            if len(assigned_agents) == 1:
                # 单智能体执行
                result = await self._execute_single_agent_task(task, assigned_agents[0])
            else:
                # 多智能体协作执行
                result = await self._execute_collaborative_task(task, assigned_agents)
            
            # 更新任务状态
            task.status = TaskStatus.COMPLETED if result.get("success", False) else TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.actual_duration = task.completed_at - task.started_at
            task.results = result
            
            # 从活跃任务中移除
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            # 添加到历史
            self.task_history.append(task)
            
            # 更新智能体负载
            for agent_type in assigned_agents:
                self.agent_capabilities[agent_type].current_load -= 1
            
            # 更新统计信息
            if task.status == TaskStatus.COMPLETED:
                self.stats["completed_tasks"] += 1
            else:
                self.stats["failed_tasks"] += 1
            
            # 触发事件
            await self._trigger_event("task_completed", {"task": task})
            
            logger.info(f"Task completed: {task.id} - Status: {task.status.value}")
            
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            task.status = TaskStatus.FAILED
            task.results = {"error": str(e)}
            
            # 清理
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            
            for agent_type in task.assigned_agents:
                if agent_type in self.agent_capabilities:
                    self.agent_capabilities[agent_type].current_load -= 1
    
    async def _assign_agents(self, task: Task) -> List[AgentType]:
        """分配智能体"""
        strategy = self.config.get('assignment_strategy', 'capability_based')
        assignment_func = self.assignment_strategies.get(strategy, self._assign_by_capability)
        
        return await assignment_func(task)
    
    async def _assign_by_capability(self, task: Task) -> List[AgentType]:
        """基于能力分配智能体"""
        suitable_agents = []
        
        for agent_type, capability in self.agent_capabilities.items():
            if (capability.availability and
                task.type in capability.task_types and
                capability.current_load < capability.max_load):
                suitable_agents.append((agent_type, capability.expertise_level))
        
        # 按专业水平排序
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        
        if suitable_agents:
            return [suitable_agents[0][0]]
        
        return []
    
    async def _assign_by_load_balance(self, task: Task) -> List[AgentType]:
        """基于负载均衡分配智能体"""
        suitable_agents = []
        
        for agent_type, capability in self.agent_capabilities.items():
            if (capability.availability and
                task.type in capability.task_types and
                capability.current_load < capability.max_load):
                load_ratio = capability.current_load / capability.max_load
                suitable_agents.append((agent_type, load_ratio))
        
        # 按负载比例排序（负载低的优先）
        suitable_agents.sort(key=lambda x: x[1])
        
        if suitable_agents:
            return [suitable_agents[0][0]]
        
        return []
    
    async def _assign_by_expertise(self, task: Task) -> List[AgentType]:
        """基于专业水平分配智能体"""
        suitable_agents = []
        
        for agent_type, capability in self.agent_capabilities.items():
            if (capability.availability and
                task.type in capability.task_types and
                capability.current_load < capability.max_load):
                # 综合考虑专业水平和成功率
                score = capability.expertise_level * 0.7 + capability.success_rate * 0.3
                suitable_agents.append((agent_type, score))
        
        # 按综合得分排序
        suitable_agents.sort(key=lambda x: x[1], reverse=True)
        
        if suitable_agents:
            return [suitable_agents[0][0]]
        
        return []
    
    async def _assign_by_response_time(self, task: Task) -> List[AgentType]:
        """基于响应时间分配智能体"""
        suitable_agents = []
        
        for agent_type, capability in self.agent_capabilities.items():
            if (capability.availability and
                task.type in capability.task_types and
                capability.current_load < capability.max_load):
                suitable_agents.append((agent_type, capability.response_time))
        
        # 按响应时间排序（响应时间短的优先）
        suitable_agents.sort(key=lambda x: x[1])
        
        if suitable_agents:
            return [suitable_agents[0][0]]
        
        return []
    
    async def _assign_collaborative(self, task: Task) -> List[AgentType]:
        """分配协作智能体"""
        # 根据任务类型确定需要协作的智能体
        collaboration_patterns = {
            TaskType.DIAGNOSIS_SUPPORT: [AgentType.XIAOKE, AgentType.LAOKE],
            TaskType.TREATMENT_PLANNING: [AgentType.XIAOKE, AgentType.LAOKE, AgentType.SOER],
            TaskType.EMERGENCY_RESPONSE: [AgentType.XIAOAI, AgentType.LAOKE],
            TaskType.HEALTH_CONSULTATION: [AgentType.XIAOAI, AgentType.SOER],
            TaskType.PREVENTION_GUIDANCE: [AgentType.SOER, AgentType.XIAOKE]
        }
        
        suggested_agents = collaboration_patterns.get(task.type, [])
        available_agents = []
        
        for agent_type in suggested_agents:
            capability = self.agent_capabilities[agent_type]
            if (capability.availability and
                capability.current_load < capability.max_load):
                available_agents.append(agent_type)
        
        return available_agents
    
    async def _execute_single_agent_task(
        self,
        task: Task,
        agent_type: AgentType
    ) -> Dict[str, Any]:
        """执行单智能体任务"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            
            # 模拟智能体处理
            result = await self._simulate_agent_processing(agent_type, task)
            
            return {
                "success": True,
                "agent": agent_type.value,
                "result": result,
                "processing_time": (datetime.now() - task.started_at).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error in single agent execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": agent_type.value
            }
    
    async def _execute_collaborative_task(
        self,
        task: Task,
        agent_types: List[AgentType]
    ) -> Dict[str, Any]:
        """执行协作任务"""
        try:
            task.status = TaskStatus.IN_PROGRESS
            
            if task.collaboration_mode == CollaborationMode.SEQUENTIAL:
                return await self._execute_sequential_collaboration(task, agent_types)
            elif task.collaboration_mode == CollaborationMode.PARALLEL:
                return await self._execute_parallel_collaboration(task, agent_types)
            elif task.collaboration_mode == CollaborationMode.HIERARCHICAL:
                return await self._execute_hierarchical_collaboration(task, agent_types)
            elif task.collaboration_mode == CollaborationMode.CONSENSUS:
                return await self._execute_consensus_collaboration(task, agent_types)
            else:
                return await self._execute_sequential_collaboration(task, agent_types)
                
        except Exception as e:
            logger.error(f"Error in collaborative execution: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents": [agent.value for agent in agent_types]
            }
    
    async def _execute_sequential_collaboration(
        self,
        task: Task,
        agent_types: List[AgentType]
    ) -> Dict[str, Any]:
        """执行顺序协作"""
        results = {}
        current_input = task.input_data
        
        for agent_type in agent_types:
            agent_result = await self._simulate_agent_processing(agent_type, task, current_input)
            results[agent_type.value] = agent_result
            
            # 下一个智能体的输入是前一个的输出
            current_input = agent_result.get("output", current_input)
        
        # 记录协作结果
        collaboration_result = CollaborationResult(
            task_id=task.id,
            participating_agents=agent_types,
            collaboration_mode=CollaborationMode.SEQUENTIAL,
            individual_results={agent: results[agent.value] for agent in agent_types},
            consensus_result=results.get(agent_types[-1].value),  # 最后一个智能体的结果
            confidence_score=self._calculate_collaboration_confidence(results),
            execution_time=datetime.now() - task.started_at,
            success=True
        )
        
        self.collaboration_history.append(collaboration_result)
        
        return {
            "success": True,
            "collaboration_mode": "sequential",
            "agents": [agent.value for agent in agent_types],
            "individual_results": results,
            "final_result": current_input,
            "confidence_score": collaboration_result.confidence_score
        }
    
    async def _execute_parallel_collaboration(
        self,
        task: Task,
        agent_types: List[AgentType]
    ) -> Dict[str, Any]:
        """执行并行协作"""
        # 并行执行所有智能体
        tasks_coroutines = [
            self._simulate_agent_processing(agent_type, task)
            for agent_type in agent_types
        ]
        
        agent_results = await asyncio.gather(*tasks_coroutines, return_exceptions=True)
        
        results = {}
        for i, agent_type in enumerate(agent_types):
            if isinstance(agent_results[i], Exception):
                results[agent_type.value] = {"error": str(agent_results[i])}
            else:
                results[agent_type.value] = agent_results[i]
        
        # 合并结果
        merged_result = await self._merge_parallel_results(results)
        
        # 记录协作结果
        collaboration_result = CollaborationResult(
            task_id=task.id,
            participating_agents=agent_types,
            collaboration_mode=CollaborationMode.PARALLEL,
            individual_results={agent: results[agent.value] for agent in agent_types},
            consensus_result=merged_result,
            confidence_score=self._calculate_collaboration_confidence(results),
            execution_time=datetime.now() - task.started_at,
            success=True
        )
        
        self.collaboration_history.append(collaboration_result)
        
        return {
            "success": True,
            "collaboration_mode": "parallel",
            "agents": [agent.value for agent in agent_types],
            "individual_results": results,
            "merged_result": merged_result,
            "confidence_score": collaboration_result.confidence_score
        }
    
    async def _execute_hierarchical_collaboration(
        self,
        task: Task,
        agent_types: List[AgentType]
    ) -> Dict[str, Any]:
        """执行层次协作"""
        # 按专业水平排序
        sorted_agents = sorted(
            agent_types,
            key=lambda x: self.agent_capabilities[x].expertise_level
        )
        
        results = {}
        
        # 初级智能体先处理
        for agent_type in sorted_agents[:-1]:
            agent_result = await self._simulate_agent_processing(agent_type, task)
            results[agent_type.value] = agent_result
        
        # 高级智能体进行审核和最终决策
        senior_agent = sorted_agents[-1]
        review_input = {
            "original_task": task.input_data,
            "preliminary_results": results
        }
        
        final_result = await self._simulate_agent_processing(senior_agent, task, review_input)
        results[senior_agent.value] = final_result
        
        # 记录协作结果
        collaboration_result = CollaborationResult(
            task_id=task.id,
            participating_agents=agent_types,
            collaboration_mode=CollaborationMode.HIERARCHICAL,
            individual_results={agent: results[agent.value] for agent in agent_types},
            consensus_result=final_result,
            confidence_score=self._calculate_collaboration_confidence(results),
            execution_time=datetime.now() - task.started_at,
            success=True
        )
        
        self.collaboration_history.append(collaboration_result)
        
        return {
            "success": True,
            "collaboration_mode": "hierarchical",
            "agents": [agent.value for agent in agent_types],
            "individual_results": results,
            "final_result": final_result,
            "confidence_score": collaboration_result.confidence_score
        }
    
    async def _execute_consensus_collaboration(
        self,
        task: Task,
        agent_types: List[AgentType]
    ) -> Dict[str, Any]:
        """执行共识协作"""
        # 第一轮：所有智能体独立处理
        first_round_tasks = [
            self._simulate_agent_processing(agent_type, task)
            for agent_type in agent_types
        ]
        
        first_round_results = await asyncio.gather(*first_round_tasks)
        results = {
            agent_types[i].value: first_round_results[i]
            for i in range(len(agent_types))
        }
        
        # 第二轮：基于其他智能体的结果进行协商
        consensus_input = {
            "original_task": task.input_data,
            "peer_results": results
        }
        
        second_round_tasks = [
            self._simulate_agent_processing(agent_type, task, consensus_input)
            for agent_type in agent_types
        ]
        
        second_round_results = await asyncio.gather(*second_round_tasks)
        
        # 更新结果
        for i, agent_type in enumerate(agent_types):
            results[f"{agent_type.value}_consensus"] = second_round_results[i]
        
        # 计算共识结果
        consensus_result = await self._calculate_consensus(second_round_results)
        
        # 记录协作结果
        collaboration_result = CollaborationResult(
            task_id=task.id,
            participating_agents=agent_types,
            collaboration_mode=CollaborationMode.CONSENSUS,
            individual_results={agent: results[agent.value] for agent in agent_types},
            consensus_result=consensus_result,
            confidence_score=self._calculate_collaboration_confidence(results),
            execution_time=datetime.now() - task.started_at,
            success=True
        )
        
        self.collaboration_history.append(collaboration_result)
        
        return {
            "success": True,
            "collaboration_mode": "consensus",
            "agents": [agent.value for agent in agent_types],
            "individual_results": results,
            "consensus_result": consensus_result,
            "confidence_score": collaboration_result.confidence_score
        }
    
    async def _simulate_agent_processing(
        self,
        agent_type: AgentType,
        task: Task,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """模拟智能体处理"""
        capability = self.agent_capabilities[agent_type]
        processing_data = input_data or task.input_data
        
        # 模拟处理时间
        await asyncio.sleep(capability.response_time)
        
        # 根据智能体类型生成不同的结果
        if agent_type == AgentType.XIAOAI:
            return await self._simulate_xiaoai_processing(task, processing_data)
        elif agent_type == AgentType.XIAOKE:
            return await self._simulate_xiaoke_processing(task, processing_data)
        elif agent_type == AgentType.LAOKE:
            return await self._simulate_laoke_processing(task, processing_data)
        elif agent_type == AgentType.SOER:
            return await self._simulate_soer_processing(task, processing_data)
        else:
            return {"error": f"Unknown agent type: {agent_type}"}
    
    async def _simulate_xiaoai_processing(
        self,
        task: Task,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """模拟小艾处理"""
        if task.type == TaskType.HEALTH_CONSULTATION:
            return {
                "response": "基于您的描述，我为您提供以下健康建议...",
                "confidence": 0.8,
                "recommendations": [
                    "建议保持规律作息",
                    "注意饮食均衡",
                    "适当运动"
                ],
                "follow_up_questions": [
                    "您的症状持续多长时间了？",
                    "是否有其他不适症状？"
                ],
                "output": input_data
            }
        elif task.type == TaskType.EDUCATION:
            return {
                "educational_content": "健康教育内容...",
                "confidence": 0.85,
                "learning_materials": ["文章链接", "视频链接"],
                "output": input_data
            }
        else:
            return {
                "message": "小艾正在学习处理这类任务",
                "confidence": 0.6,
                "output": input_data
            }
    
    async def _simulate_xiaoke_processing(
        self,
        task: Task,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """模拟小克处理"""
        if task.type == TaskType.SYMPTOM_ANALYSIS:
            return {
                "symptom_analysis": {
                    "primary_symptoms": ["症状1", "症状2"],
                    "secondary_symptoms": ["症状3"],
                    "severity": "中等",
                    "possible_causes": ["原因1", "原因2"]
                },
                "confidence": 0.85,
                "recommendations": [
                    "建议进一步检查",
                    "注意观察症状变化"
                ],
                "output": {
                    **input_data,
                    "analysis_result": "症状分析完成"
                }
            }
        elif task.type == TaskType.DIAGNOSIS_SUPPORT:
            return {
                "preliminary_diagnosis": "初步诊断结果",
                "confidence": 0.75,
                "differential_diagnosis": ["鉴别诊断1", "鉴别诊断2"],
                "recommended_tests": ["检查项目1", "检查项目2"],
                "output": {
                    **input_data,
                    "diagnosis_support": "诊断支持完成"
                }
            }
        else:
            return {
                "analysis": "小克的专业分析",
                "confidence": 0.8,
                "output": input_data
            }
    
    async def _simulate_laoke_processing(
        self,
        task: Task,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """模拟老克处理"""
        if task.type == TaskType.DIAGNOSIS_SUPPORT:
            return {
                "expert_diagnosis": "专家级诊断意见",
                "confidence": 0.95,
                "clinical_reasoning": "基于多年临床经验的推理过程",
                "treatment_priority": "高",
                "specialist_referral": "是否需要专科转诊",
                "output": {
                    **input_data,
                    "expert_review": "专家审核完成"
                }
            }
        elif task.type == TaskType.TREATMENT_PLANNING:
            return {
                "treatment_plan": {
                    "immediate_actions": ["立即处理措施"],
                    "short_term_plan": ["短期治疗计划"],
                    "long_term_plan": ["长期治疗计划"]
                },
                "confidence": 0.92,
                "risk_assessment": "风险评估结果",
                "monitoring_plan": "监测计划",
                "output": {
                    **input_data,
                    "treatment_plan": "治疗计划制定完成"
                }
            }
        elif task.type == TaskType.EMERGENCY_RESPONSE:
            return {
                "emergency_assessment": "紧急情况评估",
                "immediate_actions": ["紧急处理措施"],
                "urgency_level": "高",
                "confidence": 0.98,
                "output": {
                    **input_data,
                    "emergency_handled": True
                }
            }
        else:
            return {
                "expert_opinion": "老克的专家意见",
                "confidence": 0.9,
                "output": input_data
            }
    
    async def _simulate_soer_processing(
        self,
        task: Task,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """模拟索儿处理"""
        if task.type == TaskType.PREVENTION_GUIDANCE:
            return {
                "prevention_plan": {
                    "lifestyle_modifications": ["生活方式调整"],
                    "dietary_recommendations": ["饮食建议"],
                    "exercise_plan": ["运动计划"],
                    "monitoring_schedule": ["监测计划"]
                },
                "confidence": 0.82,
                "risk_factors": ["风险因素识别"],
                "health_goals": ["健康目标设定"],
                "output": {
                    **input_data,
                    "prevention_plan": "预防计划制定完成"
                }
            }
        elif task.type == TaskType.LIFESTYLE_ADVICE:
            return {
                "lifestyle_recommendations": {
                    "diet": ["饮食建议"],
                    "exercise": ["运动建议"],
                    "sleep": ["睡眠建议"],
                    "stress_management": ["压力管理"]
                },
                "confidence": 0.8,
                "personalized_tips": ["个性化建议"],
                "tracking_metrics": ["追踪指标"],
                "output": {
                    **input_data,
                    "lifestyle_advice": "生活指导完成"
                }
            }
        else:
            return {
                "health_management": "索儿的健康管理建议",
                "confidence": 0.75,
                "output": input_data
            }
    
    async def _merge_parallel_results(
        self,
        results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """合并并行结果"""
        merged = {
            "combined_analysis": {},
            "consensus_recommendations": [],
            "confidence_scores": {},
            "individual_contributions": results
        }
        
        # 提取所有建议
        all_recommendations = []
        for agent, result in results.items():
            if "recommendations" in result:
                all_recommendations.extend(result["recommendations"])
            merged["confidence_scores"][agent] = result.get("confidence", 0.5)
        
        # 去重并排序建议
        unique_recommendations = list(set(all_recommendations))
        merged["consensus_recommendations"] = unique_recommendations
        
        # 计算平均置信度
        if merged["confidence_scores"]:
            merged["average_confidence"] = sum(merged["confidence_scores"].values()) / len(merged["confidence_scores"])
        else:
            merged["average_confidence"] = 0.5
        
        return merged
    
    async def _calculate_consensus(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算共识结果"""
        consensus = {
            "agreed_points": [],
            "disputed_points": [],
            "final_recommendation": "",
            "consensus_confidence": 0.0
        }
        
        # 简化的共识计算
        all_recommendations = []
        confidence_scores = []
        
        for result in results:
            if "recommendations" in result:
                all_recommendations.extend(result["recommendations"])
            confidence_scores.append(result.get("confidence", 0.5))
        
        # 统计建议出现频率
        from collections import Counter
        recommendation_counts = Counter(all_recommendations)
        
        # 出现频率高的作为共识点
        total_agents = len(results)
        for recommendation, count in recommendation_counts.items():
            if count >= total_agents * 0.6:  # 60%以上同意
                consensus["agreed_points"].append(recommendation)
            else:
                consensus["disputed_points"].append(recommendation)
        
        # 计算共识置信度
        if confidence_scores:
            consensus["consensus_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        # 生成最终建议
        if consensus["agreed_points"]:
            consensus["final_recommendation"] = f"基于多智能体共识，建议：{'; '.join(consensus['agreed_points'])}"
        else:
            consensus["final_recommendation"] = "智能体间存在分歧，建议进一步咨询专家"
        
        return consensus
    
    def _calculate_collaboration_confidence(
        self,
        results: Dict[str, Dict[str, Any]]
    ) -> float:
        """计算协作置信度"""
        confidence_scores = []
        
        for result in results.values():
            if isinstance(result, dict) and "confidence" in result:
                confidence_scores.append(result["confidence"])
        
        if confidence_scores:
            return sum(confidence_scores) / len(confidence_scores)
        else:
            return 0.5
    
    async def _store_task(self, task: Task):
        """存储任务到Redis"""
        try:
            task_data = {
                "id": task.id,
                "type": task.type.value,
                "priority": task.priority.value,
                "status": task.status.value,
                "title": task.title,
                "description": task.description,
                "user_id": task.user_id,
                "input_data": json.dumps(task.input_data),
                "created_at": task.created_at.isoformat(),
                "assigned_agents": [agent.value for agent in task.assigned_agents],
                "collaboration_mode": task.collaboration_mode.value,
                "metadata": json.dumps(task.metadata)
            }
            
            await self.redis_client.hset(f"task:{task.id}", mapping=task_data)
            await self.redis_client.lpush("task_queue", task.id)
            
        except Exception as e:
            logger.error(f"Error storing task: {e}")
    
    async def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """触发事件"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                await callback(data)
            except Exception as e:
                logger.error(f"Error in event callback for {event_type}: {e}")
    
    async def _monitoring_loop(self):
        """监控循环"""
        while True:
            try:
                # 检查任务超时
                await self._check_task_timeouts()
                
                # 更新智能体状态
                await self._update_agent_status()
                
                # 更新统计信息
                await self._update_statistics()
                
                await asyncio.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_task_timeouts(self):
        """检查任务超时"""
        current_time = datetime.now()
        
        for task_id, task in list(self.active_tasks.items()):
            if task.deadline and current_time > task.deadline:
                logger.warning(f"Task {task_id} has exceeded deadline")
                
                # 标记为失败
                task.status = TaskStatus.FAILED
                task.results = {"error": "Task exceeded deadline"}
                task.completed_at = current_time
                
                # 清理
                del self.active_tasks[task_id]
                self.task_history.append(task)
                
                # 释放智能体负载
                for agent_type in task.assigned_agents:
                    if agent_type in self.agent_capabilities:
                        self.agent_capabilities[agent_type].current_load -= 1
                
                # 触发事件
                await self._trigger_event("task_timeout", {"task": task})
    
    async def _update_agent_status(self):
        """更新智能体状态"""
        for agent_type, capability in self.agent_capabilities.items():
            # 根据当前负载调整可用性
            load_ratio = capability.current_load / capability.max_load
            
            if load_ratio >= 1.0:
                capability.availability = False
            elif load_ratio < 0.8:
                capability.availability = True
            
            # 更新利用率统计
            self.stats["agent_utilization"][agent_type.value] = load_ratio
    
    async def _update_statistics(self):
        """更新统计信息"""
        # 计算平均完成时间
        completed_tasks = [t for t in self.task_history if t.status == TaskStatus.COMPLETED and t.actual_duration]
        if completed_tasks:
            total_duration = sum(t.actual_duration.total_seconds() for t in completed_tasks)
            self.stats["average_completion_time"] = total_duration / len(completed_tasks)
        
        # 计算协作成功率
        if self.collaboration_history:
            successful_collaborations = sum(1 for c in self.collaboration_history if c.success)
            self.stats["collaboration_success_rate"] = successful_collaborations / len(self.collaboration_history)
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                # 清理过期的任务历史
                cutoff_time = datetime.now() - timedelta(days=30)
                self.task_history = [
                    t for t in self.task_history
                    if t.completed_at and t.completed_at > cutoff_time
                ]
                
                # 清理过期的协作历史
                self.collaboration_history = [
                    c for c in self.collaboration_history
                    if c.execution_time and datetime.now() - c.execution_time < timedelta(days=30)
                ]
                
                await asyncio.sleep(3600)  # 每小时清理一次
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 检查活跃任务
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "status": task.status.value,
                "progress": "in_progress",
                "assigned_agents": [agent.value for agent in task.assigned_agents],
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "estimated_completion": self._estimate_completion_time(task)
            }
        
        # 检查历史任务
        for task in self.task_history:
            if task.id == task_id:
                return {
                    "id": task.id,
                    "status": task.status.value,
                    "progress": "completed",
                    "assigned_agents": [agent.value for agent in task.assigned_agents],
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "actual_duration": task.actual_duration.total_seconds() if task.actual_duration else None,
                    "results": task.results
                }
        
        return None
    
    def _estimate_completion_time(self, task: Task) -> Optional[str]:
        """估算完成时间"""
        if not task.assigned_agents or not task.started_at:
            return None
        
        # 基于智能体响应时间估算
        max_response_time = max(
            self.agent_capabilities[agent].response_time
            for agent in task.assigned_agents
        )
        
        estimated_completion = task.started_at + timedelta(seconds=max_response_time * 2)
        return estimated_completion.isoformat()
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        # 检查活跃任务
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            
            # 释放智能体负载
            for agent_type in task.assigned_agents:
                if agent_type in self.agent_capabilities:
                    self.agent_capabilities[agent_type].current_load -= 1
            
            # 移动到历史
            del self.active_tasks[task_id]
            self.task_history.append(task)
            
            # 触发事件
            await self._trigger_event("task_cancelled", {"task": task})
            
            logger.info(f"Task cancelled: {task_id}")
            return True
        
        # 检查队列中的任务
        for priority_queue in self.task_queue.values():
            for i, task in enumerate(priority_queue):
                if task.id == task_id:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    
                    # 从队列中移除
                    del priority_queue[i]
                    self.task_history.append(task)
                    
                    logger.info(f"Queued task cancelled: {task_id}")
                    return True
        
        return False
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        status = {}
        
        for agent_type, capability in self.agent_capabilities.items():
            status[agent_type.value] = {
                "availability": capability.availability,
                "current_load": capability.current_load,
                "max_load": capability.max_load,
                "load_ratio": capability.current_load / capability.max_load,
                "expertise_level": capability.expertise_level,
                "response_time": capability.response_time,
                "success_rate": capability.success_rate,
                "specialties": capability.specialties,
                "task_types": [task_type.value for task_type in capability.task_types]
            }
        
        return status
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_tasks": self.stats["total_tasks"],
            "completed_tasks": self.stats["completed_tasks"],
            "failed_tasks": self.stats["failed_tasks"],
            "active_tasks": len(self.active_tasks),
            "queued_tasks": sum(len(queue) for queue in self.task_queue.values()),
            "average_completion_time": self.stats["average_completion_time"],
            "agent_utilization": dict(self.stats["agent_utilization"]),
            "task_distribution": dict(self.stats["task_distribution"]),
            "collaboration_success_rate": self.stats["collaboration_success_rate"],
            "collaboration_history_size": len(self.collaboration_history)
        }
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """添加事件回调"""
        self.event_callbacks[event_type].append(callback)
    
    def remove_event_callback(self, event_type: str, callback: Callable):
        """移除事件回调"""
        if callback in self.event_callbacks[event_type]:
            self.event_callbacks[event_type].remove(callback)
    
    async def update_agent_capability(
        self,
        agent_type: AgentType,
        updates: Dict[str, Any]
    ) -> bool:
        """更新智能体能力"""
        try:
            if agent_type not in self.agent_capabilities:
                return False
            
            capability = self.agent_capabilities[agent_type]
            
            # 更新允许的字段
            allowed_updates = [
                'expertise_level', 'max_load', 'availability',
                'response_time', 'success_rate', 'specialties'
            ]
            
            for key, value in updates.items():
                if key in allowed_updates:
                    setattr(capability, key, value)
            
            logger.info(f"Updated capability for {agent_type.value}: {updates}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating agent capability: {e}")
            return False 