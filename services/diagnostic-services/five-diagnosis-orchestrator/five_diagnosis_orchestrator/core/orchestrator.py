"""
五诊协同编排器核心实现

负责协调和编排五个诊断服务的执行，实现智能化的诊断流程管理
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from ..config.settings import get_settings
from ..models.diagnosis_models import (
    DiagnosisEvent,
    DiagnosisInput,
    DiagnosisResult,
    DiagnosisSession,
    DiagnosisType,
    FusedDiagnosisResult,
    PatientInfo,
    SessionStatus,
)
from ..utils.event_bus import EventBus
from ..utils.exceptions import (
    OrchestrationError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)
from ..utils.service_registry import ServiceRegistry
from .decision_engine import DiagnosisDecisionEngine
from .fusion_engine import DiagnosisFusionEngine

logger = logging.getLogger(__name__)


class OrchestrationMode(Enum):
    """编排模式"""

    PARALLEL = "parallel"  # 并行执行
    SEQUENTIAL = "sequential"  # 顺序执行
    ADAPTIVE = "adaptive"  # 自适应执行
    PRIORITY_BASED = "priority_based"  # 基于优先级执行


@dataclass
class OrchestrationConfig:
    """编排配置"""

    mode: OrchestrationMode = OrchestrationMode.ADAPTIVE
    timeout_seconds: int = 300
    max_concurrent_diagnoses: int = 5
    retry_attempts: int = 3
    enable_fallback: bool = True
    require_minimum_diagnoses: int = 2
    diagnosis_priorities: Dict[DiagnosisType, int] = field(
        default_factory=lambda: {
            DiagnosisType.INQUIRY: 1,  # 问诊优先级最高
            DiagnosisType.LOOK: 2,  # 望诊次之
            DiagnosisType.CALCULATION: 3,  # 算诊
            DiagnosisType.LISTEN: 4,  # 闻诊
            DiagnosisType.PALPATION: 5,  # 切诊
        }
    )


class FiveDiagnosisOrchestrator:
    """五诊协同编排器"""

    def __init__(self):
        self.settings = get_settings()
        self.config = OrchestrationConfig()
        self.service_registry = ServiceRegistry()
        self.event_bus = EventBus()
        self.fusion_engine = DiagnosisFusionEngine()
        self.decision_engine = DiagnosisDecisionEngine()

        # 会话管理
        self.active_sessions: Dict[str, DiagnosisSession] = {}
        self.session_locks: Dict[str, asyncio.Lock] = {}

        # 性能监控
        self.metrics = {
            "total_sessions": 0,
            "successful_sessions": 0,
            "failed_sessions": 0,
            "average_processing_time": 0.0,
            "service_availability": {},
        }

        self._initialized = False

    async def initialize(self) -> None:
        """初始化编排器"""
        if self._initialized:
            return

        logger.info("初始化五诊协同编排器...")

        try:
            # 初始化服务注册中心
            await self.service_registry.initialize()

            # 初始化事件总线
            await self.event_bus.initialize()

            # 初始化融合引擎
            await self.fusion_engine.initialize()

            # 初始化决策引擎
            await self.decision_engine.initialize()

            # 注册事件处理器
            await self._register_event_handlers()

            # 启动健康检查
            asyncio.create_task(self._health_check_loop())

            self._initialized = True
            logger.info("五诊协同编排器初始化完成")

        except Exception as e:
            logger.error(f"编排器初始化失败: {e}")
            raise OrchestrationError(f"编排器初始化失败: {e}")

    async def create_diagnosis_session(
        self,
        patient_info: PatientInfo,
        enabled_diagnoses: List[DiagnosisType],
        config: Optional[OrchestrationConfig] = None,
    ) -> str:
        """创建诊断会话"""
        if not self._initialized:
            await self.initialize()

        session_id = str(uuid.uuid4())

        # 验证输入
        if not enabled_diagnoses:
            raise ValidationError("至少需要启用一种诊断类型")

        if len(enabled_diagnoses) < self.config.require_minimum_diagnoses:
            raise ValidationError(
                f"至少需要启用{self.config.require_minimum_diagnoses}种诊断类型"
            )

        # 创建会话
        session = DiagnosisSession(
            session_id=session_id,
            patient_info=patient_info,
            enabled_diagnoses=enabled_diagnoses,
            status=SessionStatus.CREATED,
        )

        if config:
            session.diagnosis_timeout = config.timeout_seconds
            session.require_all_diagnoses = not config.enable_fallback

        # 存储会话
        self.active_sessions[session_id] = session
        self.session_locks[session_id] = asyncio.Lock()

        # 发布事件
        await self._publish_event(
            session_id,
            "session_created",
            {
                "patient_id": patient_info.patient_id,
                "enabled_diagnoses": [d.value for d in enabled_diagnoses],
            },
        )

        logger.info(
            f"创建诊断会话: {session_id}, 启用诊断: {[d.value for d in enabled_diagnoses]}"
        )
        return session_id

    async def start_diagnosis(
        self, session_id: str, diagnosis_inputs: List[DiagnosisInput]
    ) -> None:
        """启动诊断流程"""
        async with self.session_locks.get(session_id, asyncio.Lock()):
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValidationError(f"会话不存在: {session_id}")

            if session.status != SessionStatus.CREATED:
                raise ValidationError(f"会话状态无效: {session.status}")

            # 更新会话状态
            session.status = SessionStatus.RUNNING
            session.started_at = datetime.utcnow()

            # 发布事件
            await self._publish_event(session_id, "diagnosis_started", {})

            try:
                # 根据编排模式执行诊断
                if self.config.mode == OrchestrationMode.PARALLEL:
                    await self._execute_parallel_diagnosis(session, diagnosis_inputs)
                elif self.config.mode == OrchestrationMode.SEQUENTIAL:
                    await self._execute_sequential_diagnosis(session, diagnosis_inputs)
                elif self.config.mode == OrchestrationMode.PRIORITY_BASED:
                    await self._execute_priority_based_diagnosis(
                        session, diagnosis_inputs
                    )
                else:  # ADAPTIVE
                    await self._execute_adaptive_diagnosis(session, diagnosis_inputs)

                # 执行诊断融合
                await self._execute_diagnosis_fusion(session)

                # 生成决策建议
                await self._execute_decision_making(session)

                # 更新会话状态
                session.status = SessionStatus.COMPLETED
                session.completed_at = datetime.utcnow()
                session.total_duration = (
                    session.completed_at - session.started_at
                ).total_seconds()

                # 更新指标
                self.metrics["successful_sessions"] += 1
                self._update_average_processing_time(session.total_duration)

                # 发布事件
                await self._publish_event(
                    session_id,
                    "diagnosis_completed",
                    {
                        "duration": session.total_duration,
                        "results_count": len(session.diagnosis_results),
                    },
                )

                logger.info(
                    f"诊断完成: {session_id}, 耗时: {session.total_duration:.2f}秒"
                )

            except Exception as e:
                session.status = SessionStatus.FAILED
                session.errors.append(str(e))
                self.metrics["failed_sessions"] += 1

                await self._publish_event(
                    session_id, "diagnosis_failed", {"error": str(e)}
                )
                logger.error(f"诊断失败: {session_id}, 错误: {e}")
                raise

    async def _execute_parallel_diagnosis(
        self, session: DiagnosisSession, diagnosis_inputs: List[DiagnosisInput]
    ) -> None:
        """并行执行诊断"""
        tasks = []
        semaphore = asyncio.Semaphore(self.config.max_concurrent_diagnoses)

        for diagnosis_input in diagnosis_inputs:
            if diagnosis_input.diagnosis_type in session.enabled_diagnoses:
                task = self._execute_single_diagnosis_with_semaphore(
                    semaphore, session, diagnosis_input
                )
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_sequential_diagnosis(
        self, session: DiagnosisSession, diagnosis_inputs: List[DiagnosisInput]
    ) -> None:
        """顺序执行诊断"""
        # 按优先级排序
        sorted_inputs = sorted(
            diagnosis_inputs,
            key=lambda x: self.config.diagnosis_priorities.get(x.diagnosis_type, 999),
        )

        for diagnosis_input in sorted_inputs:
            if diagnosis_input.diagnosis_type in session.enabled_diagnoses:
                await self._execute_single_diagnosis(session, diagnosis_input)

    async def _execute_priority_based_diagnosis(
        self, session: DiagnosisSession, diagnosis_inputs: List[DiagnosisInput]
    ) -> None:
        """基于优先级执行诊断"""
        # 按优先级分组
        priority_groups = {}
        for diagnosis_input in diagnosis_inputs:
            if diagnosis_input.diagnosis_type in session.enabled_diagnoses:
                priority = self.config.diagnosis_priorities.get(
                    diagnosis_input.diagnosis_type, 999
                )
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(diagnosis_input)

        # 按优先级顺序执行，同优先级并行执行
        for priority in sorted(priority_groups.keys()):
            tasks = [
                self._execute_single_diagnosis(session, diagnosis_input)
                for diagnosis_input in priority_groups[priority]
            ]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _execute_adaptive_diagnosis(
        self, session: DiagnosisSession, diagnosis_inputs: List[DiagnosisInput]
    ) -> None:
        """自适应执行诊断"""
        # 检查服务可用性
        available_services = await self.service_registry.get_available_services()

        # 根据服务可用性和负载情况决定执行策略
        if len(available_services) >= len(diagnosis_inputs):
            # 服务充足，使用并行执行
            await self._execute_parallel_diagnosis(session, diagnosis_inputs)
        else:
            # 服务不足，使用优先级执行
            await self._execute_priority_based_diagnosis(session, diagnosis_inputs)

    async def _execute_single_diagnosis_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        session: DiagnosisSession,
        diagnosis_input: DiagnosisInput,
    ) -> None:
        """使用信号量执行单个诊断"""
        async with semaphore:
            await self._execute_single_diagnosis(session, diagnosis_input)

    async def _execute_single_diagnosis(
        self, session: DiagnosisSession, diagnosis_input: DiagnosisInput
    ) -> None:
        """执行单个诊断"""
        diagnosis_type = diagnosis_input.diagnosis_type
        start_time = datetime.utcnow()

        try:
            # 获取服务实例
            service_client = await self.service_registry.get_service_client(
                diagnosis_type.value
            )
            if not service_client:
                raise ServiceUnavailableError(f"服务不可用: {diagnosis_type.value}")

            # 执行诊断
            result_data = await asyncio.wait_for(
                service_client.analyze(
                    session.patient_info.patient_id,
                    session.session_id,
                    diagnosis_input.data,
                ),
                timeout=session.diagnosis_timeout,
            )

            # 创建诊断结果
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result = DiagnosisResult(
                diagnosis_id=str(uuid.uuid4()),
                diagnosis_type=diagnosis_type,
                session_id=session.session_id,
                patient_id=session.patient_info.patient_id,
                confidence=result_data.get("confidence", 0.0),
                features=result_data.get("features", {}),
                raw_result=result_data,
                processing_time=processing_time,
                status="completed",
            )

            # 存储结果
            session.diagnosis_results[diagnosis_type] = result

            # 发布事件
            await self._publish_event(
                session.session_id,
                "diagnosis_completed",
                {
                    "diagnosis_type": diagnosis_type.value,
                    "processing_time": processing_time,
                },
            )

            logger.info(
                f"诊断完成: {diagnosis_type.value}, 耗时: {processing_time:.2f}秒"
            )

        except asyncio.TimeoutError:
            error_msg = f"诊断超时: {diagnosis_type.value}"
            session.errors.append(error_msg)
            logger.warning(error_msg)

        except Exception as e:
            error_msg = f"诊断失败: {diagnosis_type.value}, 错误: {str(e)}"
            session.errors.append(error_msg)
            logger.error(error_msg)

    async def _execute_diagnosis_fusion(self, session: DiagnosisSession) -> None:
        """执行诊断融合"""
        if not session.diagnosis_results:
            session.warnings.append("没有可用的诊断结果进行融合")
            return

        try:
            # 使用融合引擎处理结果
            fused_result = await self.fusion_engine.fuse_diagnosis_results(
                session.session_id, session.patient_info, session.diagnosis_results
            )

            session.fused_result = fused_result

            # 发布事件
            await self._publish_event(
                session.session_id,
                "fusion_completed",
                {"overall_confidence": fused_result.overall_confidence},
            )

            logger.info(f"诊断融合完成: {session.session_id}")

        except Exception as e:
            error_msg = f"诊断融合失败: {str(e)}"
            session.errors.append(error_msg)
            logger.error(error_msg)

    async def _execute_decision_making(self, session: DiagnosisSession) -> None:
        """执行决策制定"""
        if not session.fused_result:
            session.warnings.append("没有融合结果，跳过决策制定")
            return

        try:
            # 使用决策引擎生成建议
            recommendations = await self.decision_engine.generate_recommendations(
                session.fused_result, session.patient_info
            )

            # 更新融合结果中的建议
            session.fused_result.treatment_recommendations = recommendations.get(
                "treatment", []
            )
            session.fused_result.lifestyle_recommendations = recommendations.get(
                "lifestyle", []
            )
            session.fused_result.follow_up_recommendations = recommendations.get(
                "follow_up", []
            )

            # 发布事件
            await self._publish_event(
                session.session_id,
                "decision_completed",
                {"recommendations_count": len(recommendations)},
            )

            logger.info(f"决策制定完成: {session.session_id}")

        except Exception as e:
            error_msg = f"决策制定失败: {str(e)}"
            session.errors.append(error_msg)
            logger.error(error_msg)

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValidationError(f"会话不存在: {session_id}")

        # 计算进度
        total_diagnoses = len(session.enabled_diagnoses)
        completed_diagnoses = len(session.diagnosis_results)
        progress = completed_diagnoses / total_diagnoses if total_diagnoses > 0 else 0.0

        return {
            "session_id": session_id,
            "status": session.status.value,
            "progress": progress,
            "enabled_diagnoses": [d.value for d in session.enabled_diagnoses],
            "completed_diagnoses": list(session.diagnosis_results.keys()),
            "created_at": session.created_at.isoformat(),
            "started_at": (
                session.started_at.isoformat() if session.started_at else None
            ),
            "completed_at": (
                session.completed_at.isoformat() if session.completed_at else None
            ),
            "total_duration": session.total_duration,
            "errors": session.errors,
            "warnings": session.warnings,
        }

    async def get_session_result(
        self, session_id: str
    ) -> Optional[FusedDiagnosisResult]:
        """获取会话结果"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValidationError(f"会话不存在: {session_id}")

        return session.fused_result

    async def cancel_session(self, session_id: str) -> None:
        """取消会话"""
        async with self.session_locks.get(session_id, asyncio.Lock()):
            session = self.active_sessions.get(session_id)
            if not session:
                raise ValidationError(f"会话不存在: {session_id}")

            if session.status in [
                SessionStatus.COMPLETED,
                SessionStatus.FAILED,
                SessionStatus.CANCELLED,
            ]:
                return  # 已经结束的会话无需取消

            session.status = SessionStatus.CANCELLED
            session.completed_at = datetime.utcnow()

            # 发布事件
            await self._publish_event(session_id, "session_cancelled", {})

            logger.info(f"会话已取消: {session_id}")

    async def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        # 更新服务可用性指标
        available_services = await self.service_registry.get_available_services()
        for service_type in DiagnosisType:
            self.metrics["service_availability"][service_type.value] = (
                service_type.value in available_services
            )

        return {
            "total_sessions": self.metrics["total_sessions"],
            "successful_sessions": self.metrics["successful_sessions"],
            "failed_sessions": self.metrics["failed_sessions"],
            "success_rate": self.metrics["successful_sessions"]
            / max(self.metrics["total_sessions"], 1),
            "average_processing_time": self.metrics["average_processing_time"],
            "active_sessions": len(
                [
                    s
                    for s in self.active_sessions.values()
                    if s.status == SessionStatus.RUNNING
                ]
            ),
            "service_availability": self.metrics["service_availability"],
        }

    async def _register_event_handlers(self) -> None:
        """注册事件处理器"""
        await self.event_bus.subscribe("session_created", self._handle_session_created)
        await self.event_bus.subscribe(
            "diagnosis_started", self._handle_diagnosis_started
        )
        await self.event_bus.subscribe(
            "diagnosis_completed", self._handle_diagnosis_completed
        )
        await self.event_bus.subscribe(
            "fusion_completed", self._handle_fusion_completed
        )
        await self.event_bus.subscribe(
            "session_completed", self._handle_session_completed
        )

    async def _handle_session_created(self, event: DiagnosisEvent) -> None:
        """处理会话创建事件"""
        self.metrics["total_sessions"] += 1

    async def _handle_diagnosis_started(self, event: DiagnosisEvent) -> None:
        """处理诊断开始事件"""
        pass

    async def _handle_diagnosis_completed(self, event: DiagnosisEvent) -> None:
        """处理诊断完成事件"""
        pass

    async def _handle_fusion_completed(self, event: DiagnosisEvent) -> None:
        """处理融合完成事件"""
        pass

    async def _handle_session_completed(self, event: DiagnosisEvent) -> None:
        """处理会话完成事件"""
        pass

    async def _publish_event(
        self, session_id: str, event_type: str, data: Dict[str, Any]
    ) -> None:
        """发布事件"""
        event = DiagnosisEvent(session_id=session_id, event_type=event_type, data=data)
        await self.event_bus.publish(event_type, event)

    def _update_average_processing_time(self, processing_time: float) -> None:
        """更新平均处理时间"""
        total_successful = self.metrics["successful_sessions"]
        if total_successful == 1:
            self.metrics["average_processing_time"] = processing_time
        else:
            current_avg = self.metrics["average_processing_time"]
            self.metrics["average_processing_time"] = (
                current_avg * (total_successful - 1) + processing_time
            ) / total_successful

    async def _health_check_loop(self) -> None:
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(30)  # 每30秒检查一次
                await self.service_registry.health_check_all()
            except Exception as e:
                logger.warning(f"健康检查失败: {e}")

    async def cleanup_completed_sessions(self, max_age_hours: int = 24) -> int:
        """清理已完成的会话"""
        cutoff_time = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(
            hours=max_age_hours
        )
        cleaned_count = 0

        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if (
                session.status
                in [
                    SessionStatus.COMPLETED,
                    SessionStatus.FAILED,
                    SessionStatus.CANCELLED,
                ]
                and session.completed_at
                and session.completed_at < cutoff_time
            ):
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
            if session_id in self.session_locks:
                del self.session_locks[session_id]
            cleaned_count += 1

        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个过期会话")

        return cleaned_count

    async def close(self) -> None:
        """关闭编排器"""
        logger.info("关闭五诊协同编排器...")

        # 取消所有活跃会话
        for session_id in list(self.active_sessions.keys()):
            try:
                await self.cancel_session(session_id)
            except Exception as e:
                logger.warning(f"取消会话失败: {session_id}, 错误: {e}")

        # 关闭组件
        if hasattr(self, "fusion_engine"):
            await self.fusion_engine.close()
        if hasattr(self, "decision_engine"):
            await self.decision_engine.close()
        if hasattr(self, "event_bus"):
            await self.event_bus.close()
        if hasattr(self, "service_registry"):
            await self.service_registry.close()

        logger.info("五诊协同编排器已关闭")
