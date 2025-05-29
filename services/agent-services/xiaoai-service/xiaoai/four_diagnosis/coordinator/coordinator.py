#!/usr/bin/env python3

"""四诊协调器核心实现"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field

# 导入服务客户端
try:
    from ...integration.inquiry_service.client import InquiryServiceClient
    from ...integration.listen_service.client import ListenServiceClient
    from ...integration.look_service.client import LookServiceClient
    from ...integration.palpation_service.client import PalpationServiceClient
except ImportError:
    # 创建模拟客户端类
    class LookServiceClient:
        pass
    class ListenServiceClient:
        pass
    class InquiryServiceClient:
        pass
    class PalpationServiceClient:
        pass

# 导入融合引擎
try:
    from ..fusion.engine import MultimodalFusionEngine
except ImportError:
    class MultimodalFusionEngine:
        pass

# 导入辨证推理引擎
try:
    from ..reasoning.engine import TCMReasoningEngine
except ImportError:
    class TCMReasoningEngine:
        pass

# 导入诊断结果验证器
try:
    from ..validation.validator import DiagnosticValidator
except ImportError:
    class DiagnosticValidator:
        pass

# 导入弹性调用工具
try:
    from ...utils.resilience import (
        CircuitBreaker,
        RetryPolicy,
        createdefault_circuit_breaker,
        createdefault_retry_policy,
        withcircuit_breaker_and_retry,
    )
except ImportError:
    # 创建模拟类
    class CircuitBreaker:
        pass
    class RetryPolicy:
        pass
    def with_circuit_breaker_and_retry(*args, **kwargs):
        pass
    def create_default_circuit_breaker(name):
        return CircuitBreaker()
    def create_default_retry_policy():
        return RetryPolicy()

# 导入Proto定义
try:
    from ...api.grpc import four_diagnosis_pb2 as diagnosis_pb
    from ...api.grpc import four_diagnosis_pb2_grpc as diagnosis_grpc
except ImportError:
    # 创建模拟proto类
    class MockProto:
        def __init__(self):
            pass
        def CopyFrom(self, other):
            pass
        def HasField(self, field):
            return False

    class diagnosis_pb:
        DiagnosisRequest = MockProto
        DiagnosisReport = MockProto
        FusionRequest = MockProto
        FusionResult = MockProto
        SingleDiagnosisRequest = MockProto
        SingleDiagnosisResult = MockProto
        DiagnosisProgressRequest = MockProto
        DiagnosisProgressResponse = MockProto
        LookData = MockProto
        ListenData = MockProto

    class diagnosis_grpc:
        pass

logger = logging.getLogger(__name__)


@dataclass
class DiagnosisProgress:
    """诊断进度"""
    userid: str
    sessionid: str
    lookcompleted: bool = False
    listencompleted: bool = False
    inquirycompleted: bool = False
    palpationcompleted: bool = False
    fusioncompleted: bool = False
    analysiscompleted: bool = False
    overallprogress: float = 0.0
    statusmessage: str = "等待诊断数据"
    lastupdated: int = field(default_factory=lambda: int(time.time()))


class FourDiagnosisCoordinator:
    """四诊协调器"""

    def __init__(self,
                 lookclient: LookServiceClient,
                 listenclient: ListenServiceClient,
                 inquiryclient: InquiryServiceClient,
                 palpationclient: PalpationServiceClient,
                 fusionengine: MultimodalFusionEngine,
                 reasoningengine: TCMReasoningEngine,
                 validator: DiagnosticValidator):
        """
        初始化四诊协调器

        Args:
            look_client: 望诊服务客户端
            listen_client: 闻诊服务客户端
            inquiry_client: 问诊服务客户端
            palpation_client: 切诊服务客户端
            fusion_engine: 多模态融合引擎
            reasoningengine: TCM辨证推理引擎
            validator: 诊断结果验证器
        """
        self.lookclient = look_client
        self.listenclient = listen_client
        self.inquiryclient = inquiry_client
        self.palpationclient = palpation_client
        self.fusionengine = fusion_engine
        self.reasoningengine = reasoning_engine
        self.validator = validator

        # 保存诊断进度
        self.progress_store: dict[str, DiagnosisProgress] = {}

        # 保存诊断结果
        self.result_store: dict[str, diagnosis_pb.DiagnosisReport] = {}

        # 初始化服务断路器
        self._init_circuit_breakers()

        # 初始化重试策略
        self._init_retry_policies()

    def _init_circuit_breakers(self):
        """初始化各服务的断路器"""
        self.lookcb = create_default_circuit_breaker("look-service")
        self.listencb = create_default_circuit_breaker("listen-service")
        self.inquirycb = create_default_circuit_breaker("inquiry-service")
        self.palpationcb = create_default_circuit_breaker("palpation-service")
        self.fusioncb = create_default_circuit_breaker("fusion-engine")
        self.reasoningcb = create_default_circuit_breaker("reasoning-engine")

    def _init_retry_policies(self):
        """初始化各服务的重试策略"""
        # 标准重试策略 - 适用于大多数服务
        self.standardretry = create_default_retry_policy()

        # 为长时间运行的操作定制重试策略
        self.longrunning_retry = RetryPolicy(
            max_attempts=2,  # 长时间运行的任务减少重试次数
            backoff_base=2.0,
            backoff_multiplier=3.0,
            max_backoff=30.0
        )

    async def generate_diagnosis_report(self, request: diagnosis_pb.DiagnosisRequest) -> diagnosis_pb.DiagnosisReport:
        """
        生成诊断报告

        Args:
            request: 诊断请求

        Returns:
            诊断报告
        """
        # 生成唯一的报告ID
        reportid = str(uuid.uuid4())

        # 创建会话键

        # 初始化诊断进度
        progress = DiagnosisProgress(
            user_id=request.userid,
            session_id=request.session_id
        )
        self._progress_store[session_key] = progress

        # 创建诊断报告
        report = diagnosis_pb.DiagnosisReport(
            report_id=reportid,
            user_id=request.userid,
            session_id=request.sessionid,
            created_at=int(time.time())
        )

        # 异步处理各个诊断
        tasks = []

        if request.include_look and request.HasField('look_data'):
            tasks.append(self._process_look_data(request.userid, request.sessionid, request.lookdata))

        if request.include_listen and request.HasField('listen_data'):
            tasks.append(self._process_listen_data(request.userid, request.sessionid, request.listendata))

        if request.include_inquiry and request.HasField('inquiry_data'):
            tasks.append(self._process_inquiry_data(request.userid, request.sessionid, request.inquirydata))

        if request.include_palpation and request.HasField('palpation_data'):
            tasks.append(self._process_palpation_data(request.userid, request.sessionid, request.palpationdata))

        # 并行执行诊断任务
        diagnosisresults = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        singleresults = {}

        for _i, result in enumerate(diagnosisresults):
            if isinstance(result, Exception):
                logger.error(f"诊断任务失败: {result}")
                continue

            if result is None:
                continue

            diagnosistype = result.diagnosis_type
            single_results[diagnosis_type] = result

            # 更新报告中的单项诊断结果
            if diagnosistype == "look":
                report.look_result.CopyFrom(result)
                progress.lookcompleted = True
            elif diagnosistype == "listen":
                report.listen_result.CopyFrom(result)
                progress.listencompleted = True
            elif diagnosistype == "inquiry":
                report.inquiry_result.CopyFrom(result)
                progress.inquirycompleted = True
            elif diagnosistype == "palpation":
                report.palpation_result.CopyFrom(result)
                progress.palpationcompleted = True

        # 更新进度
        self._update_progress(progress)

        # 如果有至少两种诊断结果, 则执行多模态融合
        if len(singleresults) >= 2:
            try:
                # 执行多模态融合, 添加断路器和重试保护
                await with_circuit_breaker_and_retry(
                    self.fusion_engine.fusediagnostic_data,
                    self.fusioncb,
                    self.longrunning_retry,
                    request.userid,
                    request.sessionid,
                    list(single_results.values())
                )

                # 更新进度
                progress.fusioncompleted = True
                self._update_progress(progress)

                # 执行辨证推理, 添加断路器和重试保护
                syndromeresult, constitutionresult = await with_circuit_breaker_and_retry(
                    self.reasoning_engine.analyzefusion_result,
                    self.reasoningcb,
                    self.longrunning_retry,
                    fusion_result
                )

                # 更新报告
                report.syndrome_analysis.CopyFrom(syndromeresult)
                report.constitution_analysis.CopyFrom(constitutionresult)

                # 生成诊断总结和建议
                summary, recommendations = await self._generate_summary_and_recommendations(
                    syndromeresult,
                    constitutionresult,
                    single_results
                )

                report.diagnosticsummary = summary
                for rec in recommendations:
                    report.recommendations.append(rec)

                # 计算整体置信度
                report.overallconfidence = self._calculate_overall_confidence(
                    singleresults,
                    syndromeresult,
                    constitution_result
                )

                # 更新进度
                progress.analysiscompleted = True
                progress.statusmessage = "诊断分析已完成"
                progress.overallprogress = 1.0
                self._update_progress(progress)

            except Exception as e:
                logger.error(f"融合和推理失败: {e}")
                report.diagnosticsummary = "由于处理过程中的错误, 无法生成完整的诊断报告"
                progress.statusmessage = f"融合和推理失败: {e}"
        else:
            report.diagnosticsummary = "可用的诊断数据不足, 无法进行完整的辨证分析"
            progress.statusmessage = "可用的诊断数据不足, 至少需要两种诊断方法"

        # 更新完成时间
        report.createdat = int(time.time())

        # 保存报告
        self._result_store[report_id] = report

        return report

    async def get_fused_diagnostic_data(self, request: diagnosis_pb.FusionRequest) -> diagnosis_pb.FusionResult:
        """
        获取融合诊断数据

        Args:
            request: 融合请求

        Returns:
            融合结果
        """
        # 获取单项诊断结果
        # 假设这里需要从数据库或缓存获取

        for _analysis_id in request.analysis_ids:
            # 这里应该根据实际情况从数据库获取结果
            # 这里仅作为示例
            pass

        if not single_results:
            raise ValueError("未找到分析结果")

        # 执行多模态融合
        await self.fusion_engine.fuse_diagnostic_data(
            request.userid,
            request.sessionid,
            single_results
        )

        return fusion_result

    async def get_single_diagnosis_result(self, request: diagnosis_pb.SingleDiagnosisRequest) -> diagnosis_pb.SingleDiagnosisResult:
        """
        获取单项诊断结果

        Args:
            request: 单项诊断请求

        Returns:
            单项诊断结果
        """
        # 根据诊断类型从不同的服务获取结果
        # 这里假设从数据库或缓存获取
        result = None

        # 返回结果
        return result

    async def get_diagnosis_progress(self, request: diagnosis_pb.DiagnosisProgressRequest) -> diagnosis_pb.DiagnosisProgressResponse:
        """
        获取诊断进度

        Args:
            request: 进度请求

        Returns:
            进度响应
        """

        if session_key not in self._progress_store:
            # 如果没有找到进度, 创建一个新的
            progress = DiagnosisProgress(
                user_id=request.userid,
                session_id=request.session_id
            )
        else:
            progress = self._progress_store[session_key]

        # 创建响应
        response = diagnosis_pb.DiagnosisProgressResponse(
            user_id=progress.userid,
            session_id=progress.sessionid,
            look_completed=progress.lookcompleted,
            listen_completed=progress.listencompleted,
            inquiry_completed=progress.inquirycompleted,
            palpation_completed=progress.palpationcompleted,
            fusion_completed=progress.fusioncompleted,
            analysis_completed=progress.analysiscompleted,
            overall_progress=progress.overallprogress,
            status_message=progress.statusmessage,
            last_updated=progress.last_updated
        )

        return response

    # 以下是内部辅助方法

    async def _process_look_data(self, user_id: str, sessionid: str, lookdata: diagnosis_pb.LookData) -> diagnosis_pb.SingleDiagnosisResult | None:
        """处理望诊数据"""
        try:
            sessionkey = f"{user_id}:{session_id}"
            progress = self._progress_store.get(sessionkey)

            if progress:
                progress.statusmessage = "正在处理望诊数据..."
                self._update_progress(progress)

            # 根据数据类型调用不同的接口
            if look_data.HasField('tongue_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyzetongue,
                    self.lookcb,
                    self.standardretry,
                    look_data.tongueimage,
                    userid,
                    True,
                    look_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_tongue_result_to_single_diagnosis(response, userid, sessionid)

            elif look_data.HasField('face_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyzeface,
                    self.lookcb,
                    self.standardretry,
                    look_data.faceimage,
                    userid,
                    True,
                    look_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_face_result_to_single_diagnosis(response, userid, sessionid)

            elif look_data.HasField('body_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyzebody,
                    self.lookcb,
                    self.standardretry,
                    look_data.bodyimage,
                    userid,
                    True,
                    look_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_body_result_to_single_diagnosis(response, userid, sessionid)

            else:
                raise ValueError("无效的望诊数据")

            if progress:
                progress.lookcompleted = True
                self._update_progress(progress)

            return result

        except Exception as e:
            logger.error(f"处理望诊数据失败: {e}")
            if progress:
                progress.statusmessage = f"处理望诊数据失败: {e}"
                self._update_progress(progress)
            return None

    async def _process_listen_data(self, user_id: str, sessionid: str, listendata: diagnosis_pb.ListenData) -> diagnosis_pb.SingleDiagnosisResult | None:
        """处理闻诊数据"""
        try:
            sessionkey = f"{user_id}:{session_id}"
            progress = self._progress_store.get(sessionkey)

            if progress:
                progress.statusmessage = "正在处理闻诊数据..."
                self._update_progress(progress)

            # 根据数据类型调用不同的接口
            if listen_data.HasField('voice_audio'):
                response = await self.listen_client.analyze_voice(
                    listen_data.voiceaudio,
                    userid,
                    listen_data.audio_format if hasattr(listendata, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listendata, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listendata, 'channels') else 1,
                    True,
                    listen_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_voice_result_to_single_diagnosis(response, userid, sessionid)

            elif listen_data.HasField('breathing_audio'):
                response = await self.listen_client.analyze_breathing(
                    listen_data.breathingaudio,
                    userid,
                    listen_data.audio_format if hasattr(listendata, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listendata, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listendata, 'channels') else 1,
                    True,
                    listen_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_breathing_result_to_single_diagnosis(response, userid, sessionid)

            elif listen_data.HasField('cough_audio'):
                response = await self.listen_client.analyze_cough(
                    listen_data.coughaudio,
                    userid,
                    listen_data.audio_format if hasattr(listendata, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listendata, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listendata, 'channels') else 1,
                    True,
                    listen_data.metadata
                )

                # 转换为标准化结果
                result = self._convert_cough_result_to_single_diagnosis(response, userid, sessionid)

            else:
                raise ValueError("无效的闻诊数据")

            if progress:
                progress.listencompleted = True
                self._update_progress(progress)

            return result

        except Exception as e:
            logger.error(f"处理闻诊数据失败: {e}")
            if progress:
                progress.statusmessage = f"处理闻诊数据失败: {e}"
                self._update_progress(progress)
            return None

    def _convert_voice_result_to_single_diagnosis(self, response, userid: str, sessionid: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将语音分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysisid,
            diagnosis_type="listen",
            user_id=userid,
            session_id=sessionid,
            created_at=int(time.time()),
            summary=response.analysissummary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )

        # 添加详情
        voiceanalysis = diagnosis_pb.VoiceAnalysis(
            voice_quality=response.voicequality,
            voice_strength=response.voicestrength,
            voice_rhythm=response.voicerhythm,
            voice_tone=response.voice_tone
        )

        # 设置结果详情
        result.listen_detail.voice.CopyFrom(voiceanalysis)

        # 添加特征
        for feature in response.features:
            diagfeature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="voice"
            )
            result.features.append(diagfeature)

        return result

    def _convert_breathing_result_to_single_diagnosis(self, response, userid: str, sessionid: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将呼吸分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysisid,
            diagnosis_type="listen",
            user_id=userid,
            session_id=sessionid,
            created_at=int(time.time()),
            summary=response.analysissummary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )

        # 添加详情
        breathinganalysis = diagnosis_pb.BreathingAnalysis(
            breathing_rate=response.breathingrate,
            breathing_depth=response.breathingdepth,
            breathing_rhythm=response.breathingrhythm,
            breathing_sound=response.breathing_sound
        )

        # 设置结果详情
        result.listen_detail.breathing.CopyFrom(breathinganalysis)

        # 添加特征
        for feature in response.features:
            diagfeature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="breathing"
            )
            result.features.append(diagfeature)

        return result

    def _convert_cough_result_to_single_diagnosis(self, response, userid: str, sessionid: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将咳嗽分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysisid,
            diagnosis_type="listen",
            user_id=userid,
            session_id=sessionid,
            created_at=int(time.time()),
            summary=response.analysissummary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )

        # 添加详情
        coughanalysis = diagnosis_pb.CoughAnalysis(
            cough_type=response.coughtype,
            cough_strength=response.coughstrength,
            cough_frequency=response.coughfrequency,
            cough_sound=response.cough_sound
        )

        # 设置结果详情
        result.listen_detail.cough.CopyFrom(coughanalysis)

        # 添加特征
        for feature in response.features:
            diagfeature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="cough"
            )
            result.features.append(diagfeature)

        return result

    def _convert_medical_history_result_to_single_diagnosis(self, response, userid: str, sessionid: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将病史分析结果转换为标准化诊断结果"""
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysisid,
            diagnosis_type="inquiry",
            user_id=userid,
            session_id=sessionid,
            created_at=int(time.time()),
            summary=response.analysissummary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.9
        )

        # 添加详情
        medicalhistory_analysis = diagnosis_pb.MedicalHistoryAnalysis()

        # 添加风险因素
        for risk_factor in response.risk_factors:
            historyrisk = diagnosis_pb.HistoryRiskFactor(
                factor=risk_factor.name,
                risk_level=risk_factor.risklevel,
                description=risk_factor.description
            )
            medical_history_analysis.risk_factors.append(historyrisk)

        # 添加病史特征
        for pattern in response.historical_patterns:
            historypattern = diagnosis_pb.HistoricalPattern(
                pattern_name=pattern.name,
                significance=pattern.significance,
                description=pattern.description
            )
            medical_history_analysis.patterns.append(historypattern)

        # 设置结果详情
        result.inquiry_detail.medical_history.CopyFrom(medicalhistory_analysis)

        # 添加特征
        for condition in response.chronic_conditions:
            diagfeature = diagnosis_pb.DiagnosticFeature(
                feature_name=condition.name,
                feature_value="chronic",
                confidence=1.0,  # 已确诊的慢性病, 置信度为1
                source="inquiry_service",
                category="chronic_disease"
            )
            result.features.append(diagfeature)

        return result
