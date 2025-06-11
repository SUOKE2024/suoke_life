"""
索克生活智能体协同编排器
实现四个智能体的协同工作流程和决策机制
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..core.agent_event_types import (
    COLLABORATION_SCENARIOS,
    AgentCollaborationEvents,
    LaokeEvents,
    SoerEvents,
    XiaoaiEvents,
    XiaokeEvents,
)
from ..core.event_bus import SuokeEventBus


class CollaborationState(Enum):
    """协同状态枚举"""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    COORDINATING = "coordinating"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """智能体任务定义"""
    agent_id: str
    task_type: str
    task_data: Dict[str, Any]
    priority: str = "normal"
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 5分钟超时
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class CollaborationSession:
    """协同会话"""
    session_id: str
    scenario: str
    user_id: str
    participating_agents: List[str]
    tasks: List[AgentTask] = field(default_factory=list)
    state: CollaborationState = CollaborationState.IDLE
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None


class AgentOrchestrator:
    """智能体协同编排器"""
    
    def __init__(self, event_bus: SuokeEventBus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.workflow_templates: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_workflows()
        
    def _initialize_workflows(self):
        """初始化工作流模板"""
        self.workflow_templates = {
            "comprehensive_health_diagnosis": [
                {
                    "agent": "xiaoai",
                    "task": "四诊合参统筹",
                    "events": [
                        XiaoaiEvents.FOUR_DIAGNOSIS_COORDINATION_STARTED,
                        XiaoaiEvents.CONSTITUTION_SCREENING_STARTED,
                        XiaoaiEvents.FACE_COLOR_ANALYSIS_STARTED,
                        XiaoaiEvents.TONGUE_DIAGNOSIS_STARTED
                    ],
                    "dependencies": [],
                    "timeout": 600
                },
                {
                    "agent": "soer",
                    "task": "生活数据分析",
                    "events": [
                        SoerEvents.SENSOR_DATA_COLLECTED,
                        SoerEvents.LIFESTYLE_HABIT_ANALYZED,
                        SoerEvents.HEALTH_TREND_ANALYZED
                    ],
                    "dependencies": ["xiaoai.四诊合参统筹"],
                    "timeout": 300
                },
                {
                    "agent": "xiaoke",
                    "task": "名医资源匹配",
                    "events": [
                        XiaokeEvents.DOCTOR_MATCHING_STARTED,
                        XiaokeEvents.SERVICE_SUBSCRIPTION_REQUESTED
                    ],
                    "dependencies": ["xiaoai.四诊合参统筹", "soer.生活数据分析"],
                    "timeout": 180
                },
                {
                    "agent": "laoke",
                    "task": "知识支持提供",
                    "events": [
                        LaokeEvents.KNOWLEDGE_SEARCH_REQUESTED,
                        LaokeEvents.PERSONALIZED_LEARNING_PATH_GENERATED
                    ],
                    "dependencies": ["xiaoai.四诊合参统筹"],
                    "timeout": 120
                }
            ],
            "personalized_wellness_plan": [
                {
                    "agent": "soer",
                    "task": "个性化方案生成",
                    "events": [
                        SoerEvents.PERSONALIZED_WELLNESS_PLAN_CREATED,
                        SoerEvents.LIFESTYLE_HABIT_ANALYZED
                    ],
                    "dependencies": [],
                    "timeout": 300
                },
                {
                    "agent": "xiaoai",
                    "task": "中医体质分析",
                    "events": [
                        XiaoaiEvents.CONSTITUTION_SCREENING_STARTED,
                        XiaoaiEvents.FACE_COLOR_ANALYSIS_STARTED
                    ],
                    "dependencies": [],
                    "timeout": 240
                },
                {
                    "agent": "xiaoke",
                    "task": "相关产品推荐",
                    "events": [
                        XiaokeEvents.PERSONALIZED_RECOMMENDATION_GENERATED,
                        XiaokeEvents.AGRICULTURAL_PRODUCT_CUSTOMIZED
                    ],
                    "dependencies": ["soer.个性化方案生成", "xiaoai.中医体质分析"],
                    "timeout": 180
                }
            ],
            "emergency_health_support": [
                {
                    "agent": "soer",
                    "task": "异常状态检测",
                    "events": [
                        SoerEvents.STRESS_LEVEL_MONITORED,
                        SoerEvents.MENTAL_HEALTH_ASSESSED
                    ],
                    "dependencies": [],
                    "timeout": 60,
                    "priority": "high"
                },
                {
                    "agent": "xiaoai",
                    "task": "紧急评估处理",
                    "events": [
                        XiaoaiEvents.HEALTH_CONSULTATION_STARTED,
                        XiaoaiEvents.FOUR_DIAGNOSIS_COORDINATION_STARTED
                    ],
                    "dependencies": ["soer.异常状态检测"],
                    "timeout": 120,
                    "priority": "high"
                },
                {
                    "agent": "xiaoke",
                    "task": "医疗资源调度",
                    "events": [
                        XiaokeEvents.DOCTOR_MATCHING_STARTED,
                        XiaokeEvents.APPOINTMENT_SCHEDULED
                    ],
                    "dependencies": ["xiaoai.紧急评估处理"],
                    "timeout": 180,
                    "priority": "high"
                }
            ]
        }
    
    async def start_collaboration(
        self,
        scenario: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """启动智能体协同"""
        session_id = f"collab_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if scenario not in COLLABORATION_SCENARIOS:
            raise ValueError(f"未知的协同场景: {scenario}")
        
        scenario_config = COLLABORATION_SCENARIOS[scenario]
        participating_agents = scenario_config["participating_agents"]
        
        session = CollaborationSession(
            session_id=session_id,
            scenario=scenario,
            user_id=user_id,
            participating_agents=participating_agents,
            context=context or {}
        )
        
        # 生成任务列表
        tasks = await self._generate_tasks(scenario, session_id, context or {})
        session.tasks = tasks
        session.state = CollaborationState.PLANNING
        
        self.active_sessions[session_id] = session
        
        # 发布协同开始事件
        await self.event_bus.publish(
            AgentCollaborationEvents.MULTI_AGENT_CONSULTATION_STARTED,
            {
                "session_id": session_id,
                "scenario": scenario,
                "user_id": user_id,
                "participating_agents": participating_agents,
                "context": context
            }
        )
        
        # 开始执行工作流
        asyncio.create_task(self._execute_workflow(session_id))
        
        self.logger.info(f"启动智能体协同会话: {session_id}, 场景: {scenario}")
        return session_id
    
    async def _generate_tasks(
        self,
        scenario: str,
        session_id: str,
        context: Dict[str, Any]
    ) -> List[AgentTask]:
        """生成任务列表"""
        tasks = []
        workflow = self.workflow_templates.get(scenario, [])
        
        for step in workflow:
            task = AgentTask(
                agent_id=step["agent"],
                task_type=step["task"],
                task_data={
                    "session_id": session_id,
                    "events": step["events"],
                    "context": context
                },
                priority=step.get("priority", "normal"),
                dependencies=step.get("dependencies", []),
                timeout=step.get("timeout", 300)
            )
            tasks.append(task)
        
        return tasks
    
    async def _execute_workflow(self, session_id: str):
        """执行工作流"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        try:
            session.state = CollaborationState.EXECUTING
            session.updated_at = datetime.now()
            
            # 按依赖关系执行任务
            completed_tasks = set()
            
            while len(completed_tasks) < len(session.tasks):
                # 找到可以执行的任务
                ready_tasks = []
                for task in session.tasks:
                    if (task.status == "pending" and 
                        all(dep in completed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # 检查是否有任务失败导致死锁
                    failed_tasks = [t for t in session.tasks if t.status == "failed"]
                    if failed_tasks:
                        session.state = CollaborationState.FAILED
                        break
                    
                    # 等待一段时间再检查
                    await asyncio.sleep(1)
                    continue
                
                # 并行执行准备好的任务
                await asyncio.gather(*[
                    self._execute_task(task, session_id) 
                    for task in ready_tasks
                ])
                
                # 更新完成的任务
                for task in ready_tasks:
                    if task.status == "completed":
                        completed_tasks.add(f"{task.agent_id}.{task.task_type}")
            
            # 检查最终状态
            if all(task.status == "completed" for task in session.tasks):
                session.state = CollaborationState.COMPLETED
                session.completed_at = datetime.now()
                
                # 生成协同结果
                session.result = await self._generate_collaboration_result(session)
                
                # 发布协同完成事件
                await self.event_bus.publish(
                    AgentCollaborationEvents.MULTI_AGENT_CONSULTATION_COMPLETED,
                    {
                        "session_id": session_id,
                        "scenario": session.scenario,
                        "user_id": session.user_id,
                        "result": session.result,
                        "duration": (session.completed_at - session.created_at).total_seconds()
                    }
                )
                
                self.logger.info(f"智能体协同完成: {session_id}")
            else:
                session.state = CollaborationState.FAILED
                self.logger.error(f"智能体协同失败: {session_id}")
        
        except Exception as e:
            session.state = CollaborationState.FAILED
            self.logger.error(f"执行工作流异常: {session_id}, {str(e)}")
    
    async def _execute_task(self, task: AgentTask, session_id: str):
        """执行单个任务"""
        try:
            task.status = "running"
            task.started_at = datetime.now()
            
            # 发布任务开始事件
            for event_type in task.task_data["events"]:
                await self.event_bus.publish(
                    event_type,
                    {
                        "session_id": session_id,
                        "task_id": f"{task.agent_id}.{task.task_type}",
                        "agent_id": task.agent_id,
                        "task_data": task.task_data,
                        "context": task.task_data.get("context", {})
                    }
                )
            
            # 等待任务完成或超时
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < task.timeout:
                # 检查任务是否完成（这里简化处理，实际应该监听智能体的响应事件）
                await asyncio.sleep(1)
                
                # 模拟任务完成（实际应该根据智能体响应判断）
                if (datetime.now() - start_time).total_seconds() > 5:  # 模拟5秒完成
                    task.status = "completed"
                    task.completed_at = datetime.now()
                    task.result = {
                        "agent_id": task.agent_id,
                        "task_type": task.task_type,
                        "execution_time": (task.completed_at - task.started_at).total_seconds(),
                        "success": True
                    }
                    break
            
            if task.status != "completed":
                # 任务超时
                task.status = "timeout"
                task.error = f"任务超时: {task.timeout}秒"
                
                # 重试机制
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = "pending"
                    self.logger.warning(f"任务超时，准备重试: {task.agent_id}.{task.task_type}")
                else:
                    task.status = "failed"
                    self.logger.error(f"任务最终失败: {task.agent_id}.{task.task_type}")
        
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.logger.error(f"执行任务异常: {task.agent_id}.{task.task_type}, {str(e)}")
    
    async def _generate_collaboration_result(self, session: CollaborationSession) -> Dict[str, Any]:
        """生成协同结果"""
        result = {
            "session_id": session.session_id,
            "scenario": session.scenario,
            "user_id": session.user_id,
            "participating_agents": session.participating_agents,
            "execution_summary": {
                "total_tasks": len(session.tasks),
                "completed_tasks": len([t for t in session.tasks if t.status == "completed"]),
                "failed_tasks": len([t for t in session.tasks if t.status == "failed"]),
                "total_duration": (session.completed_at - session.created_at).total_seconds()
            },
            "agent_contributions": {},
            "recommendations": [],
            "next_actions": []
        }
        
        # 收集各智能体的贡献
        for task in session.tasks:
            if task.status == "completed" and task.result:
                agent_id = task.agent_id
                if agent_id not in result["agent_contributions"]:
                    result["agent_contributions"][agent_id] = []
                result["agent_contributions"][agent_id].append(task.result)
        
        # 根据场景生成推荐和后续行动
        if session.scenario == "comprehensive_health_diagnosis":
            result["recommendations"] = [
                "基于四诊合参结果，建议定期监测相关健康指标",
                "结合生活数据分析，调整日常作息和饮食习惯",
                "考虑预约推荐的专科医生进行进一步检查"
            ]
            result["next_actions"] = [
                "制定个性化健康管理计划",
                "设置健康监测提醒",
                "安排后续复查时间"
            ]
        elif session.scenario == "personalized_wellness_plan":
            result["recommendations"] = [
                "根据体质分析结果，采用个性化养生方案",
                "选择推荐的健康产品和服务",
                "建立长期的健康习惯培养计划"
            ]
            result["next_actions"] = [
                "开始执行个性化养生计划",
                "定期评估和调整方案",
                "参与相关的健康教育活动"
            ]
        
        return result
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取协同会话状态"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "scenario": session.scenario,
            "state": session.state.value,
            "participating_agents": session.participating_agents,
            "progress": {
                "total_tasks": len(session.tasks),
                "completed_tasks": len([t for t in session.tasks if t.status == "completed"]),
                "running_tasks": len([t for t in session.tasks if t.status == "running"]),
                "failed_tasks": len([t for t in session.tasks if t.status == "failed"])
            },
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
    
    async def cancel_collaboration(self, session_id: str) -> bool:
        """取消协同会话"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.state = CollaborationState.FAILED
        session.updated_at = datetime.now()
        
        # 取消所有运行中的任务
        for task in session.tasks:
            if task.status == "running":
                task.status = "cancelled"
        
        self.logger.info(f"取消智能体协同会话: {session_id}")
        return True
    
    async def update_agent_status(self, agent_id: str, status: Dict[str, Any]):
        """更新智能体状态"""
        self.agent_status[agent_id] = {
            **status,
            "updated_at": datetime.now().isoformat()
        }
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取智能体状态"""
        return self.agent_status.get(agent_id)
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """列出活跃的协同会话"""
        return [
            await self.get_session_status(session_id)
            for session_id in self.active_sessions.keys()
        ]
    
    async def cleanup_completed_sessions(self, max_age_hours: int = 24):
        """清理已完成的会话"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.active_sessions.items():
            if (session.state in [CollaborationState.COMPLETED, CollaborationState.FAILED] and
                session.updated_at < cutoff_time):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
            self.logger.info(f"清理已完成的协同会话: {session_id}")
        
        return len(sessions_to_remove)


class AgentCollaborationManager:
    """智能体协同管理器"""
    
    def __init__(self, event_bus: SuokeEventBus):
        self.event_bus = event_bus
        self.orchestrator = AgentOrchestrator(event_bus)
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """初始化协同管理器"""
        # 订阅相关事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.AGENT_HANDOFF_INITIATED,
            self._handle_agent_handoff
        )
        
        # 启动定期清理任务
        asyncio.create_task(self._periodic_cleanup())
        
        self.logger.info("智能体协同管理器初始化完成")
    
    async def _handle_agent_handoff(self, event_data: Dict[str, Any]):
        """处理智能体交接"""
        from_agent = event_data.get("from_agent")
        to_agent = event_data.get("to_agent")
        context = event_data.get("context", {})
        
        self.logger.info(f"处理智能体交接: {from_agent} -> {to_agent}")
        
        # 发布交接完成事件
        await self.event_bus.publish(
            AgentCollaborationEvents.AGENT_HANDOFF_COMPLETED,
            {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "context": context,
                "handoff_time": datetime.now().isoformat()
            }
        )
    
    async def _periodic_cleanup(self):
        """定期清理任务"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时执行一次
                cleaned_count = await self.orchestrator.cleanup_completed_sessions()
                if cleaned_count > 0:
                    self.logger.info(f"定期清理完成，清理了 {cleaned_count} 个会话")
            except Exception as e:
                self.logger.error(f"定期清理异常: {str(e)}")
    
    async def start_collaboration(
        self,
        scenario: str,
        user_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """启动智能体协同"""
        return await self.orchestrator.start_collaboration(scenario, user_id, context)
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取协同会话状态"""
        return await self.orchestrator.get_session_status(session_id)
    
    async def cancel_collaboration(self, session_id: str) -> bool:
        """取消协同会话"""
        return await self.orchestrator.cancel_collaboration(session_id)
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """列出活跃的协同会话"""
        return await self.orchestrator.list_active_sessions() 