"""
五诊协调引擎

负责协调望、闻、问、切、算五诊数据的收集、分析和融合
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..config.settings import get_settings
from ..utils.exceptions import DiagnosisError, ServiceUnavailableError
from ..utils.validators import validate_diagnosis_data

logger = logging.getLogger(__name__)


class DiagnosisType(Enum):
    """诊断类型枚举"""

    LOOKING = "looking"  # 望诊
    LISTENING = "listening"  # 闻诊
    INQUIRY = "inquiry"  # 问诊
    PALPATION = "palpation"  # 切诊
    CALCULATION = "calculation"  # 算诊


class DiagnosisStatus(Enum):
    """诊断状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class DiagnosisRequest:
    """诊断请求数据结构"""

    user_id: str
    session_id: str
    diagnosis_types: List[DiagnosisType]
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DiagnosisResult:
    """单项诊断结果"""

    diagnosis_id: str
    diagnosis_type: DiagnosisType
    status: DiagnosisStatus
    confidence: float
    features: Dict[str, Any] = field(default_factory=dict)
    raw_result: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    processing_time_ms: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FusedDiagnosisResult:
    """融合诊断结果"""

    coordination_id: str
    user_id: str
    session_id: str
    individual_results: List[DiagnosisResult]
    syndrome_analysis: Dict[str, Any] = field(default_factory=dict)
    constitution_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    overall_confidence: float = 0.0
    summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FiveDiagnosisCoordinator:
    """五诊协调器"""

    def __init__(self):
        self.settings = get_settings()
        self.service_clients: Dict[DiagnosisType, Any] = {}
        self.active_sessions: Dict[str, Any] = {}

    async def initialize(self) -> None:
        """初始化协调器"""
        logger.info("初始化五诊协调器...")

        # 初始化服务客户端
        await self._initialize_service_clients()

        logger.info("五诊协调器初始化完成")

    async def _initialize_service_clients(self) -> None:
        """初始化各诊断服务客户端"""
        from ..integration.service_clients import (
            CalculationServiceClient,
            InquiryServiceClient,
            ListenServiceClient,
            LookServiceClient,
            PalpationServiceClient,
        )

        try:
            self.service_clients = {
                DiagnosisType.LOOKING: LookServiceClient(),
                DiagnosisType.LISTENING: ListenServiceClient(),
                DiagnosisType.INQUIRY: InquiryServiceClient(),
                DiagnosisType.PALPATION: PalpationServiceClient(),
                DiagnosisType.CALCULATION: CalculationServiceClient(),
            }

            # 初始化所有客户端
            for client in self.service_clients.values():
                await client.initialize()

        except Exception as e:
            logger.error(f"初始化服务客户端失败: {e}")
            raise ServiceUnavailableError(f"无法初始化诊断服务: {e}")

    async def coordinate_diagnosis(
        self, request: DiagnosisRequest
    ) -> FusedDiagnosisResult:
        """协调五诊分析"""
        coordination_id = f"{request.session_id}_{int(datetime.now().timestamp())}"

        logger.info(f"开始五诊协调 - ID: {coordination_id}")

        try:
            # 验证请求数据
            await self._validate_request(request)

            # 记录会话状态
            self.active_sessions[coordination_id] = {
                "request": request,
                "status": "in_progress",
                "start_time": datetime.now(timezone.utc),
            }

            # 执行诊断
            individual_results = await self._execute_diagnoses(request)

            # 融合分析结果
            fused_result = await self._fuse_diagnosis_results(
                coordination_id, request, individual_results
            )

            # 更新会话状态
            self.active_sessions[coordination_id]["status"] = "completed"

            logger.info(f"五诊协调完成 - ID: {coordination_id}")
            return fused_result

        except Exception as e:
            logger.error(f"五诊协调失败 - ID: {coordination_id}, 错误: {e}")
            if coordination_id in self.active_sessions:
                self.active_sessions[coordination_id]["status"] = "failed"
            raise DiagnosisError(f"五诊协调失败: {e}")

    async def _validate_request(self, request: DiagnosisRequest) -> None:
        """验证诊断请求"""
        if not request.user_id:
            raise ValueError("用户ID不能为空")

        if not request.session_id:
            raise ValueError("会话ID不能为空")

        if not request.diagnosis_types:
            raise ValueError("诊断类型不能为空")

        # 验证诊断数据
        for diagnosis_type in request.diagnosis_types:
            if diagnosis_type.value in request.data:
                await validate_diagnosis_data(
                    diagnosis_type, request.data[diagnosis_type.value]
                )

    async def _execute_diagnoses(
        self, request: DiagnosisRequest
    ) -> List[DiagnosisResult]:
        """执行各项诊断"""
        coordinator_mode = self.settings.five_diagnosis.coordinator_mode

        if coordinator_mode == "parallel":
            return await self._execute_parallel_diagnoses(request)
        else:
            return await self._execute_sequential_diagnoses(request)

    async def _execute_parallel_diagnoses(
        self, request: DiagnosisRequest
    ) -> List[DiagnosisResult]:
        """并行执行诊断"""
        tasks = []

        for diagnosis_type in request.diagnosis_types:
            if diagnosis_type in self.service_clients:
                task = self._execute_single_diagnosis(request, diagnosis_type)
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                diagnosis_type = request.diagnosis_types[i]
                error_result = DiagnosisResult(
                    diagnosis_id=f"{request.session_id}_{diagnosis_type.value}",
                    diagnosis_type=diagnosis_type,
                    status=DiagnosisStatus.FAILED,
                    confidence=0.0,
                    error_message=str(result),
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_sequential_diagnoses(
        self, request: DiagnosisRequest
    ) -> List[DiagnosisResult]:
        """顺序执行诊断"""
        results = []

        for diagnosis_type in request.diagnosis_types:
            try:
                result = await self._execute_single_diagnosis(request, diagnosis_type)
                results.append(result)
            except Exception as e:
                logger.error(f"诊断失败 - 类型: {diagnosis_type.value}, 错误: {e}")
                error_result = DiagnosisResult(
                    diagnosis_id=f"{request.session_id}_{diagnosis_type.value}",
                    diagnosis_type=diagnosis_type,
                    status=DiagnosisStatus.FAILED,
                    confidence=0.0,
                    error_message=str(e),
                )
                results.append(error_result)

        return results

    async def _execute_single_diagnosis(
        self, request: DiagnosisRequest, diagnosis_type: DiagnosisType
    ) -> DiagnosisResult:
        """执行单项诊断"""
        start_time = datetime.now()
        diagnosis_id = (
            f"{request.session_id}_{diagnosis_type.value}_{int(start_time.timestamp())}"
        )

        try:
            client = self.service_clients[diagnosis_type]
            diagnosis_data = request.data.get(diagnosis_type.value, {})

            # 调用相应的诊断服务
            raw_result = await asyncio.wait_for(
                client.analyze(request.user_id, request.session_id, diagnosis_data),
                timeout=request.timeout_seconds,
            )

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return DiagnosisResult(
                diagnosis_id=diagnosis_id,
                diagnosis_type=diagnosis_type,
                status=DiagnosisStatus.COMPLETED,
                confidence=raw_result.get("confidence", 0.0),
                features=raw_result.get("features", {}),
                raw_result=raw_result,
                processing_time_ms=processing_time,
            )

        except asyncio.TimeoutError:
            logger.warning(f"诊断超时 - 类型: {diagnosis_type.value}")
            return DiagnosisResult(
                diagnosis_id=diagnosis_id,
                diagnosis_type=diagnosis_type,
                status=DiagnosisStatus.TIMEOUT,
                confidence=0.0,
                error_message="诊断超时",
            )
        except Exception as e:
            logger.error(f"诊断执行失败 - 类型: {diagnosis_type.value}, 错误: {e}")
            return DiagnosisResult(
                diagnosis_id=diagnosis_id,
                diagnosis_type=diagnosis_type,
                status=DiagnosisStatus.FAILED,
                confidence=0.0,
                error_message=str(e),
            )

    async def _fuse_diagnosis_results(
        self,
        coordination_id: str,
        request: DiagnosisRequest,
        individual_results: List[DiagnosisResult],
    ) -> FusedDiagnosisResult:
        """融合诊断结果"""
        from ..core.constitution_analyzer import ConstitutionAnalyzer
        from ..core.recommendation_engine import RecommendationEngine
        from ..core.syndrome_analyzer import SyndromeAnalyzer

        # 初始化分析器
        syndrome_analyzer = SyndromeAnalyzer()
        constitution_analyzer = ConstitutionAnalyzer()
        recommendation_engine = RecommendationEngine()

        # 提取有效结果
        valid_results = [
            r for r in individual_results if r.status == DiagnosisStatus.COMPLETED
        ]

        if not valid_results:
            logger.warning(f"没有有效的诊断结果 - 协调ID: {coordination_id}")
            return FusedDiagnosisResult(
                coordination_id=coordination_id,
                user_id=request.user_id,
                session_id=request.session_id,
                individual_results=individual_results,
                summary="诊断失败，无有效结果",
            )

        # 辨证分析
        syndrome_analysis = await syndrome_analyzer.analyze(valid_results)

        # 体质分析
        constitution_analysis = await constitution_analyzer.analyze(valid_results)

        # 生成建议
        recommendations = await recommendation_engine.generate_recommendations(
            syndrome_analysis, constitution_analysis, valid_results
        )

        # 计算整体置信度
        overall_confidence = self._calculate_overall_confidence(valid_results)

        # 生成总结
        summary = await self._generate_summary(
            syndrome_analysis, constitution_analysis, recommendations
        )

        return FusedDiagnosisResult(
            coordination_id=coordination_id,
            user_id=request.user_id,
            session_id=request.session_id,
            individual_results=individual_results,
            syndrome_analysis=syndrome_analysis,
            constitution_analysis=constitution_analysis,
            recommendations=recommendations,
            overall_confidence=overall_confidence,
            summary=summary,
        )

    def _calculate_overall_confidence(self, results: List[DiagnosisResult]) -> float:
        """计算整体置信度"""
        if not results:
            return 0.0

        # 加权平均置信度
        weights = {
            DiagnosisType.INQUIRY: 1.5,  # 问诊权重最高
            DiagnosisType.LOOKING: 1.0,
            DiagnosisType.LISTENING: 1.0,
            DiagnosisType.PALPATION: 1.0,
            DiagnosisType.CALCULATION: 0.8,
        }

        total_weighted_confidence = 0.0
        total_weight = 0.0

        for result in results:
            weight = weights.get(result.diagnosis_type, 1.0)
            total_weighted_confidence += result.confidence * weight
            total_weight += weight

        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0

    async def _generate_summary(
        self,
        syndrome_analysis: Dict[str, Any],
        constitution_analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
    ) -> str:
        """生成诊断总结"""
        summary_parts = []

        # 证型总结
        if syndrome_analysis.get("primary_syndromes"):
            syndromes = [s["name"] for s in syndrome_analysis["primary_syndromes"][:2]]
            summary_parts.append(f"主要证型：{', '.join(syndromes)}")

        # 体质总结
        if constitution_analysis.get("dominant_constitution"):
            constitution = constitution_analysis["dominant_constitution"]["type"]
            summary_parts.append(f"体质类型：{constitution}")

        # 建议总结
        if recommendations:
            high_priority_recs = [
                r for r in recommendations if r.get("priority", 0) >= 4
            ]
            if high_priority_recs:
                summary_parts.append(f"重点建议：{len(high_priority_recs)}项")

        return "；".join(summary_parts) if summary_parts else "诊断分析完成"

    async def get_diagnosis_progress(self, session_id: str) -> Dict[str, Any]:
        """获取诊断进度"""
        progress_info = {
            "session_id": session_id,
            "overall_progress": 0.0,
            "status_message": "未开始",
            "completed_diagnoses": [],
            "pending_diagnoses": [],
            "failed_diagnoses": [],
        }

        # 查找相关的协调会话
        for coordination_id, session_info in self.active_sessions.items():
            if session_info["request"].session_id == session_id:
                request = session_info["request"]
                status = session_info["status"]

                progress_info["status_message"] = status

                if status == "completed":
                    progress_info["overall_progress"] = 1.0
                    progress_info["completed_diagnoses"] = [
                        dt.value for dt in request.diagnosis_types
                    ]
                elif status == "in_progress":
                    # 这里可以实现更详细的进度跟踪
                    progress_info["overall_progress"] = 0.5
                    progress_info["status_message"] = "诊断进行中"

                break

        return progress_info

    async def cleanup_session(self, session_id: str) -> None:
        """清理会话数据"""
        to_remove = []
        for coordination_id, session_info in self.active_sessions.items():
            if session_info["request"].session_id == session_id:
                to_remove.append(coordination_id)

        for coordination_id in to_remove:
            del self.active_sessions[coordination_id]
            logger.info(f"清理会话数据 - 协调ID: {coordination_id}")
