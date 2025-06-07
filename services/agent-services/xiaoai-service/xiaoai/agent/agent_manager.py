#!/usr/bin/env python3
"""
小艾智能体管理器模块
提供智能体的生命周期管理、会话管理和诊断协调功能
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """智能体状态枚举"""
    IDLE = "idle"
    PROCESSING = "processing"
    LEARNING = "learning"
    ERROR = "error"
    OFFLINE = "offline"


class DiagnosisType(Enum):
    """诊断类型枚举"""
    LOOKING = "looking"  # 望诊
    LISTENING = "listening"  # 闻诊
    INQUIRY = "inquiry"  # 问诊
    PALPATION = "palpation"  # 切诊
    CALCULATION = "calculation"  # 算诊


@dataclass
class AgentConfig:
    """智能体配置类"""
    agent_id: str = "xiaoai"
    name: str = "小艾"
    description: str = "中医诊断智能体"
    version: str = "1.0.0"
    max_concurrent_sessions: int = 100
    session_timeout: int = 3600  # 1小时
    context_window_size: int = 4096
    confidence_threshold: float = 0.7
    enable_learning: bool = True
    enable_metrics: bool = True


@dataclass
class SessionData:
    """会话数据类"""
    session_id: str
    user_id: str
    created_at: float
    last_activity: float
    context: dict[str, Any] = field(default_factory=dict)
    diagnosis_history: list[dict[str, Any]] = field(default_factory=list)
    patient_info: dict[str, Any] = field(default_factory=dict)
    status: str = "active"


@dataclass
class DiagnosisRequest:
    """诊断请求类"""
    user_id: str
    session_id: str
    diagnosis_type: DiagnosisType
    data: dict[str, Any]
    patient_info: dict[str, Any] | None = None
    context: dict[str, Any] | None = None


@dataclass
class DiagnosisResponse:
    """诊断响应类"""
    message_id: str
    diagnosis_type: DiagnosisType
    result: dict[str, Any]
    confidence: float
    suggestions: list[str]
    metadata: dict[str, Any]
    timestamp: float


class XiaoaiAgentManager:
    """小艾智能体管理器"""

    def __init__(self, config: AgentConfig | None = None):
        """初始化智能体管理器"""
        self.config = config or AgentConfig()
        self.status = AgentStatus.OFFLINE
        self.active_sessions: dict[str, SessionData] = {}
        self.metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_diagnoses": 0,
            "successful_diagnoses": 0,
            "failed_diagnoses": 0,
            "average_response_time": 0.0,
            "uptime": 0.0,
        }
        self.start_time = time.time()
        self.logger = logging.getLogger(f"xiaoai.{self.config.agent_id}")

    async def start(self) -> None:
        """启动智能体管理器"""
        try:
            self.status = AgentStatus.IDLE
            self.logger.info("小艾智能体管理器启动成功")
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"启动失败: {e}")
            raise

    async def stop(self) -> None:
        """停止智能体管理器"""
        try:
            self.status = AgentStatus.OFFLINE
            # 清理所有活跃会话
            for session_id in list(self.active_sessions.keys()):
                await self.end_session(session_id)
            self.logger.info("小艾智能体管理器已停止")
        except Exception as e:
            self.logger.error(f"停止失败: {e}")
            raise

    async def create_session(
        self, user_id: str, patient_info: dict[str, Any] | None = None
    ) -> str:
        """创建新会话"""
        session_id = f"session_{user_id}_{int(time.time())}"

        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            created_at=time.time(),
            last_activity=time.time(),
            patient_info=patient_info or {}
        )

        self.active_sessions[session_id] = session_data
        self.metrics["total_sessions"] += 1
        self.metrics["active_sessions"] = len(self.active_sessions)

        self.logger.info(f"创建会话: {session_id}")
        return session_id

    async def end_session(self, session_id: str) -> None:
        """结束会话"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.metrics["active_sessions"] = len(self.active_sessions)
            self.logger.info(f"结束会话: {session_id}")

    async def process_diagnosis(self, request: DiagnosisRequest) -> DiagnosisResponse:
        """处理诊断请求"""
        start_time = time.time()

        try:
            # 更新会话活动时间
            if request.session_id in self.active_sessions:
                self.active_sessions[request.session_id].last_activity = time.time()

            # 根据诊断类型处理
            if request.diagnosis_type == DiagnosisType.LOOKING:
                result = await self._process_looking_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.LISTENING:
                result = await self._process_listening_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.INQUIRY:
                result = await self._process_inquiry_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.PALPATION:
                result = await self._process_palpation_diagnosis(request)
            elif request.diagnosis_type == DiagnosisType.CALCULATION:
                result = await self._process_calculation_diagnosis(request)
            else:
                raise ValueError(f"不支持的诊断类型: {request.diagnosis_type}")

            # 创建响应
            response = DiagnosisResponse(
                message_id=f"msg_{int(time.time())}",
                diagnosis_type=request.diagnosis_type,
                result=result,
                confidence=result.get("confidence", 0.0),
                suggestions=result.get("suggestions", []),
                metadata={"processing_time": time.time() - start_time},
                timestamp=time.time()
            )

            # 更新指标
            self.metrics["total_diagnoses"] += 1
            self.metrics["successful_diagnoses"] += 1

            return response

        except Exception as e:
            self.metrics["failed_diagnoses"] += 1
            self.logger.error(f"诊断处理失败: {e}")
            raise

    async def _process_looking_diagnosis(self, request: DiagnosisRequest) -> dict[str, Any]:
        """处理望诊"""
        # 模拟望诊处理
        return {
            "type": "looking",
            "analysis": "基于面色、舌象等进行分析",
            "confidence": 0.8,
            "suggestions": ["建议进一步观察舌象变化", "注意面色变化"]
        }

    async def _process_listening_diagnosis(self, request: DiagnosisRequest) -> dict[str, Any]:
        """处理闻诊"""
        # 模拟闻诊处理
        return {
            "type": "listening",
            "analysis": "基于声音、气味等进行分析",
            "confidence": 0.7,
            "suggestions": ["建议注意声音变化", "观察呼吸情况"]
        }

    async def _process_inquiry_diagnosis(self, request: DiagnosisRequest) -> dict[str, Any]:
        """处理问诊"""
        # 模拟问诊处理
        return {
            "type": "inquiry",
            "analysis": "基于症状描述进行分析",
            "confidence": 0.9,
            "suggestions": ["建议详细描述症状", "注意症状变化规律"]
        }

    async def _process_palpation_diagnosis(self, request: DiagnosisRequest) -> dict[str, Any]:
        """处理切诊"""
        # 模拟切诊处理
        return {
            "type": "palpation",
            "analysis": "基于脉象等进行分析",
            "confidence": 0.8,
            "suggestions": ["建议定期检查脉象", "注意脉象变化"]
        }

    async def _process_calculation_diagnosis(self, request: DiagnosisRequest) -> dict[str, Any]:
        """处理算诊"""
        # 模拟算诊处理
        return {
            "type": "calculation",
            "analysis": "基于综合信息进行辨证分析",
            "confidence": 0.85,
            "suggestions": ["建议综合调理", "注意生活习惯"]
        }

    def get_status(self) -> dict[str, Any]:
        """获取智能体状态"""
        return {
            "status": self.status.value,
            "config": {
                "agent_id": self.config.agent_id,
                "name": self.config.name,
                "version": self.config.version
            },
            "metrics": self.metrics,
            "active_sessions": len(self.active_sessions)
        }

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """获取会话信息"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "status": session.status,
                "diagnosis_count": len(session.diagnosis_history)
            }
        return None


# 全局实例
_agent_manager: XiaoaiAgentManager | None = None


async def get_agent_manager() -> XiaoaiAgentManager:
    """获取智能体管理器实例"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = XiaoaiAgentManager()
        await _agent_manager.start()
    return _agent_manager


async def cleanup_agent_manager():
    """清理智能体管理器"""
    global _agent_manager
    if _agent_manager:
        await _agent_manager.stop()
        _agent_manager = None
