"""
智能体协同事件处理器
处理四个智能体之间的协同诊断流程
"""

from datetime import datetime
from typing import Any, Dict, Optional

import structlog

from ..core.event_bus import Event, SuokeEventBus
from ..core.event_store import EventStore
from ..core.event_types import AgentCollaborationEvents

logger = structlog.get_logger(__name__)


class AgentEventHandlers:
    """智能体事件处理器"""

    def __init__(self, event_bus: SuokeEventBus, event_store: EventStore):
        """初始化智能体事件处理器"""
        self.event_bus = event_bus
        self.event_store = event_store

        # 诊断会话状态管理
        self.diagnosis_sessions: Dict[str, Dict[str, Any]] = {}

        # 智能体状态
        self.agent_status = {
            "xiaoai": {"available": True, "current_task": None},
            "xiaoke": {"available": True, "current_task": None},
            "laoke": {"available": True, "current_task": None},
            "soer": {"available": True, "current_task": None},
        }

    async def register_handlers(self) -> None:
        """注册所有事件处理器"""
        # 诊断流程事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.DIAGNOSIS_STARTED, self.handle_diagnosis_started
        )

        # 小艾（望诊）事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.XIAOAI_LOOK_COMPLETED,
            self.handle_xiaoai_look_completed,
        )

        # 小克（闻诊）事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.XIAOKE_LISTEN_COMPLETED,
            self.handle_xiaoke_listen_completed,
        )

        # 老克（问诊）事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.LAOKE_INQUIRY_COMPLETED,
            self.handle_laoke_inquiry_completed,
        )

        # 索儿（切诊）事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.SOER_PALPATION_COMPLETED,
            self.handle_soer_palpation_completed,
        )

        # 综合诊断事件
        await self.event_bus.subscribe(
            AgentCollaborationEvents.SYNDROME_DIFFERENTIATION_COMPLETED,
            self.handle_syndrome_differentiation_completed,
        )

        logger.info("智能体事件处理器注册完成")

    async def handle_diagnosis_started(self, event: Event) -> None:
        """处理诊断开始事件"""
        try:
            user_id = event.data.get("user_id")
            session_id = event.data.get("session_id")

            if not user_id or not session_id:
                logger.error("诊断开始事件缺少必要参数", event_id=event.id)
                return

            # 创建诊断会话
            self.diagnosis_sessions[session_id] = {
                "user_id": user_id,
                "session_id": session_id,
                "started_at": datetime.utcnow().isoformat(),
                "status": "in_progress",
                "current_step": "look",
                "results": {
                    "look": None,
                    "listen": None,
                    "inquiry": None,
                    "palpation": None,
                },
                "correlation_id": event.correlation_id,
            }

            # 启动小艾的望诊
            await self.event_bus.publish(
                AgentCollaborationEvents.XIAOAI_LOOK_STARTED,
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "user_data": event.data.get("user_data", {}),
                    "priority": "normal",
                },
                correlation_id=event.correlation_id,
            )

            # 更新智能体状态
            self.agent_status["xiaoai"]["current_task"] = session_id

            logger.info("诊断流程启动成功", session_id=session_id, user_id=user_id)

        except Exception as e:
            logger.error("处理诊断开始事件失败", event_id=event.id, error=str(e))

    async def handle_xiaoai_look_completed(self, event: Event) -> None:
        """处理小艾望诊完成事件"""
        try:
            session_id = event.data.get("session_id")
            look_result = event.data.get("result")

            if session_id not in self.diagnosis_sessions:
                logger.warning("未找到诊断会话", session_id=session_id)
                return

            # 更新会话状态
            session = self.diagnosis_sessions[session_id]
            session["results"]["look"] = look_result
            session["current_step"] = "listen"

            # 释放小艾
            self.agent_status["xiaoai"]["current_task"] = None

            # 启动小克的闻诊
            await self.event_bus.publish(
                AgentCollaborationEvents.XIAOKE_LISTEN_STARTED,
                {
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "look_result": look_result,
                    "priority": "normal",
                },
                correlation_id=session["correlation_id"],
            )

            # 更新智能体状态
            self.agent_status["xiaoke"]["current_task"] = session_id

            logger.info("小艾望诊完成，启动小克闻诊", session_id=session_id)

        except Exception as e:
            logger.error("处理小艾望诊完成事件失败", event_id=event.id, error=str(e))

    async def handle_xiaoke_listen_completed(self, event: Event) -> None:
        """处理小克闻诊完成事件"""
        try:
            session_id = event.data.get("session_id")
            listen_result = event.data.get("result")

            if session_id not in self.diagnosis_sessions:
                logger.warning("未找到诊断会话", session_id=session_id)
                return

            # 更新会话状态
            session = self.diagnosis_sessions[session_id]
            session["results"]["listen"] = listen_result
            session["current_step"] = "inquiry"

            # 释放小克
            self.agent_status["xiaoke"]["current_task"] = None

            # 启动老克的问诊
            await self.event_bus.publish(
                AgentCollaborationEvents.LAOKE_INQUIRY_STARTED,
                {
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "look_result": session["results"]["look"],
                    "listen_result": listen_result,
                    "priority": "normal",
                },
                correlation_id=session["correlation_id"],
            )

            # 更新智能体状态
            self.agent_status["laoke"]["current_task"] = session_id

            logger.info("小克闻诊完成，启动老克问诊", session_id=session_id)

        except Exception as e:
            logger.error("处理小克闻诊完成事件失败", event_id=event.id, error=str(e))

    async def handle_laoke_inquiry_completed(self, event: Event) -> None:
        """处理老克问诊完成事件"""
        try:
            session_id = event.data.get("session_id")
            inquiry_result = event.data.get("result")

            if session_id not in self.diagnosis_sessions:
                logger.warning("未找到诊断会话", session_id=session_id)
                return

            # 更新会话状态
            session = self.diagnosis_sessions[session_id]
            session["results"]["inquiry"] = inquiry_result
            session["current_step"] = "palpation"

            # 释放老克
            self.agent_status["laoke"]["current_task"] = None

            # 启动索儿的切诊
            await self.event_bus.publish(
                AgentCollaborationEvents.SOER_PALPATION_STARTED,
                {
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "look_result": session["results"]["look"],
                    "listen_result": session["results"]["listen"],
                    "inquiry_result": inquiry_result,
                    "priority": "normal",
                },
                correlation_id=session["correlation_id"],
            )

            # 更新智能体状态
            self.agent_status["soer"]["current_task"] = session_id

            logger.info("老克问诊完成，启动索儿切诊", session_id=session_id)

        except Exception as e:
            logger.error("处理老克问诊完成事件失败", event_id=event.id, error=str(e))

    async def handle_soer_palpation_completed(self, event: Event) -> None:
        """处理索儿切诊完成事件"""
        try:
            session_id = event.data.get("session_id")
            palpation_result = event.data.get("result")

            if session_id not in self.diagnosis_sessions:
                logger.warning("未找到诊断会话", session_id=session_id)
                return

            # 更新会话状态
            session = self.diagnosis_sessions[session_id]
            session["results"]["palpation"] = palpation_result
            session["current_step"] = "syndrome_differentiation"

            # 释放索儿
            self.agent_status["soer"]["current_task"] = None

            # 检查是否所有四诊都完成
            if all(session["results"].values()):
                # 启动辨证论治
                await self.event_bus.publish(
                    AgentCollaborationEvents.SYNDROME_DIFFERENTIATION_STARTED,
                    {
                        "user_id": session["user_id"],
                        "session_id": session_id,
                        "four_diagnosis_results": session["results"],
                        "priority": "high",
                    },
                    correlation_id=session["correlation_id"],
                )

                logger.info("四诊完成，启动辨证论治", session_id=session_id)
            else:
                logger.warning(
                    "四诊结果不完整", session_id=session_id, results=session["results"]
                )

        except Exception as e:
            logger.error("处理索儿切诊完成事件失败", event_id=event.id, error=str(e))

    async def handle_syndrome_differentiation_completed(self, event: Event) -> None:
        """处理辨证论治完成事件"""
        try:
            session_id = event.data.get("session_id")
            syndrome_result = event.data.get("result")

            if session_id not in self.diagnosis_sessions:
                logger.warning("未找到诊断会话", session_id=session_id)
                return

            # 更新会话状态
            session = self.diagnosis_sessions[session_id]
            session["syndrome_differentiation"] = syndrome_result
            session["current_step"] = "completed"
            session["completed_at"] = datetime.utcnow().isoformat()
            session["status"] = "completed"

            # 发布诊断完成事件
            await self.event_bus.publish(
                AgentCollaborationEvents.DIAGNOSIS_COMPLETED,
                {
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "diagnosis_result": {
                        "four_diagnosis": session["results"],
                        "syndrome_differentiation": syndrome_result,
                        "session_duration": self._calculate_session_duration(session),
                    },
                    "priority": "high",
                },
                correlation_id=session["correlation_id"],
            )

            # 生成治疗方案
            await self.event_bus.publish(
                AgentCollaborationEvents.TREATMENT_PLAN_GENERATED,
                {
                    "user_id": session["user_id"],
                    "session_id": session_id,
                    "syndrome_result": syndrome_result,
                    "priority": "normal",
                },
                correlation_id=session["correlation_id"],
            )

            logger.info(
                "诊断流程完成",
                session_id=session_id,
                duration=self._calculate_session_duration(session),
            )

            # 清理会话（可选，也可以保留用于审计）
            # del self.diagnosis_sessions[session_id]

        except Exception as e:
            logger.error("处理辨证论治完成事件失败", event_id=event.id, error=str(e))

    def _calculate_session_duration(self, session: Dict[str, Any]) -> float:
        """计算会话持续时间（秒）"""
        try:
            started_at = datetime.fromisoformat(session["started_at"])
            completed_at = datetime.fromisoformat(session["completed_at"])
            return (completed_at - started_at).total_seconds()
        except Exception:
            return 0.0

    async def get_agent_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "agents": self.agent_status,
            "active_sessions": len(
                [
                    s
                    for s in self.diagnosis_sessions.values()
                    if s["status"] == "in_progress"
                ]
            ),
            "total_sessions": len(self.diagnosis_sessions),
        }

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        return self.diagnosis_sessions.get(session_id)

    async def handle_agent_failure(
        self, agent_name: str, session_id: str, error: str
    ) -> None:
        """处理智能体失败"""
        try:
            # 更新智能体状态
            self.agent_status[agent_name]["current_task"] = None

            # 更新会话状态
            if session_id in self.diagnosis_sessions:
                session = self.diagnosis_sessions[session_id]
                session["status"] = "failed"
                session["error"] = error
                session["failed_at"] = datetime.utcnow().isoformat()

            # 发布失败事件
            await self.event_bus.publish(
                AgentCollaborationEvents.DIAGNOSIS_FAILED,
                {
                    "session_id": session_id,
                    "failed_agent": agent_name,
                    "error": error,
                    "priority": "high",
                },
            )

            logger.error(
                "智能体执行失败", agent=agent_name, session_id=session_id, error=error
            )

        except Exception as e:
            logger.error("处理智能体失败事件失败", agent=agent_name, error=str(e))


class AgentCollaborationOrchestrator:
    """智能体协同编排器"""

    def __init__(self, event_bus: SuokeEventBus):
        """初始化协同编排器"""
        self.event_bus = event_bus
        self.collaboration_rules = self._load_collaboration_rules()

    def _load_collaboration_rules(self) -> Dict[str, Any]:
        """加载协同规则"""
        return {
            "parallel_diagnosis": {
                "enabled": False,  # 是否允许并行诊断
                "max_parallel_sessions": 3,
            },
            "agent_priority": {
                "xiaoai": 1,  # 望诊优先级最高
                "xiaoke": 2,
                "laoke": 3,
                "soer": 4,
            },
            "timeout_settings": {
                "look": 300,  # 5分钟
                "listen": 300,  # 5分钟
                "inquiry": 600,  # 10分钟
                "palpation": 300,  # 5分钟
                "syndrome_differentiation": 180,  # 3分钟
            },
        }

    async def start_collaborative_diagnosis(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> str:
        """启动协同诊断"""
        session_id = f"diagnosis_{user_id}_{int(datetime.utcnow().timestamp())}"
        correlation_id = str(uuid4())

        await self.event_bus.publish(
            AgentCollaborationEvents.DIAGNOSIS_STARTED,
            {
                "user_id": user_id,
                "session_id": session_id,
                "user_data": user_data,
                "collaboration_rules": self.collaboration_rules,
            },
            correlation_id=correlation_id,
        )

        return session_id
