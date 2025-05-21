#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""四诊协调器核心实现"""

import logging
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field

import grpc
import asyncio

# 导入服务客户端
from xiaoai_service.integration.look_service.client import LookServiceClient
from xiaoai_service.integration.listen_service.client import ListenServiceClient
from xiaoai_service.integration.inquiry_service.client import InquiryServiceClient
from xiaoai_service.integration.palpation_service.client import PalpationServiceClient

# 导入融合引擎
from xiaoai_service.internal.four_diagnosis.fusion.engine import MultimodalFusionEngine

# 导入辨证推理引擎
from xiaoai_service.internal.four_diagnosis.reasoning.engine import TCMReasoningEngine

# 导入诊断结果验证器
from xiaoai_service.internal.four_diagnosis.validation.validator import DiagnosticValidator

# 导入弹性调用工具
from pkg.utils.resilience import (
    CircuitBreaker, 
    RetryPolicy, 
    with_circuit_breaker_and_retry,
    create_default_circuit_breaker,
    create_default_retry_policy
)

# 导入Proto定义
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb
from xiaoai_service.protos import four_diagnosis_pb2_grpc as diagnosis_grpc

logger = logging.getLogger(__name__)


@dataclass
class DiagnosisProgress:
    """诊断进度"""
    user_id: str
    session_id: str
    look_completed: bool = False
    listen_completed: bool = False
    inquiry_completed: bool = False
    palpation_completed: bool = False
    fusion_completed: bool = False
    analysis_completed: bool = False
    overall_progress: float = 0.0
    status_message: str = "等待诊断数据"
    last_updated: int = field(default_factory=lambda: int(time.time()))


class FourDiagnosisCoordinator:
    """四诊协调器"""
    
    def __init__(self,
                 look_client: LookServiceClient,
                 listen_client: ListenServiceClient,
                 inquiry_client: InquiryServiceClient,
                 palpation_client: PalpationServiceClient,
                 fusion_engine: MultimodalFusionEngine,
                 reasoning_engine: TCMReasoningEngine,
                 validator: DiagnosticValidator):
        """
        初始化四诊协调器
        
        Args:
            look_client: 望诊服务客户端
            listen_client: 闻诊服务客户端
            inquiry_client: 问诊服务客户端
            palpation_client: 切诊服务客户端
            fusion_engine: 多模态融合引擎
            reasoning_engine: TCM辨证推理引擎
            validator: 诊断结果验证器
        """
        self.look_client = look_client
        self.listen_client = listen_client
        self.inquiry_client = inquiry_client
        self.palpation_client = palpation_client
        self.fusion_engine = fusion_engine
        self.reasoning_engine = reasoning_engine
        self.validator = validator
        
        # 保存诊断进度
        self._progress_store: Dict[str, DiagnosisProgress] = {}
        
        # 保存诊断结果
        self._result_store: Dict[str, diagnosis_pb.DiagnosisReport] = {}
        
        # 初始化服务断路器
        self._init_circuit_breakers()
        
        # 初始化重试策略
        self._init_retry_policies()
    
    def _init_circuit_breakers(self):
        """初始化各服务的断路器"""
        self.look_cb = create_default_circuit_breaker("look-service")
        self.listen_cb = create_default_circuit_breaker("listen-service")
        self.inquiry_cb = create_default_circuit_breaker("inquiry-service")
        self.palpation_cb = create_default_circuit_breaker("palpation-service")
        self.fusion_cb = create_default_circuit_breaker("fusion-engine")
        self.reasoning_cb = create_default_circuit_breaker("reasoning-engine")
    
    def _init_retry_policies(self):
        """初始化各服务的重试策略"""
        # 标准重试策略 - 适用于大多数服务
        self.standard_retry = create_default_retry_policy()
        
        # 为长时间运行的操作定制重试策略
        self.long_running_retry = RetryPolicy(
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
        report_id = str(uuid.uuid4())
        
        # 创建会话键
        session_key = f"{request.user_id}:{request.session_id}"
        
        # 初始化诊断进度
        progress = DiagnosisProgress(
            user_id=request.user_id,
            session_id=request.session_id
        )
        self._progress_store[session_key] = progress
        
        # 创建诊断报告
        report = diagnosis_pb.DiagnosisReport(
            report_id=report_id,
            user_id=request.user_id,
            session_id=request.session_id,
            created_at=int(time.time())
        )
        
        # 异步处理各个诊断
        tasks = []
        
        if request.include_look and request.HasField('look_data'):
            tasks.append(self._process_look_data(request.user_id, request.session_id, request.look_data))
        
        if request.include_listen and request.HasField('listen_data'):
            tasks.append(self._process_listen_data(request.user_id, request.session_id, request.listen_data))
        
        if request.include_inquiry and request.HasField('inquiry_data'):
            tasks.append(self._process_inquiry_data(request.user_id, request.session_id, request.inquiry_data))
        
        if request.include_palpation and request.HasField('palpation_data'):
            tasks.append(self._process_palpation_data(request.user_id, request.session_id, request.palpation_data))
        
        # 并行执行诊断任务
        diagnosis_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        single_results = {}
        
        for i, result in enumerate(diagnosis_results):
            if isinstance(result, Exception):
                logger.error(f"诊断任务失败: {result}")
                continue
            
            if result is None:
                continue
                
            diagnosis_type = result.diagnosis_type
            single_results[diagnosis_type] = result
            
            # 更新报告中的单项诊断结果
            if diagnosis_type == "look":
                report.look_result.CopyFrom(result)
                progress.look_completed = True
            elif diagnosis_type == "listen":
                report.listen_result.CopyFrom(result)
                progress.listen_completed = True
            elif diagnosis_type == "inquiry":
                report.inquiry_result.CopyFrom(result)
                progress.inquiry_completed = True
            elif diagnosis_type == "palpation":
                report.palpation_result.CopyFrom(result)
                progress.palpation_completed = True
        
        # 更新进度
        self._update_progress(progress)
        
        # 如果有至少两种诊断结果，则执行多模态融合
        if len(single_results) >= 2:
            try:
                # 执行多模态融合，添加断路器和重试保护
                fusion_result = await with_circuit_breaker_and_retry(
                    self.fusion_engine.fuse_diagnostic_data,
                    self.fusion_cb,
                    self.long_running_retry,
                    request.user_id, 
                    request.session_id, 
                    list(single_results.values())
                )
                
                # 更新进度
                progress.fusion_completed = True
                self._update_progress(progress)
                
                # 执行辨证推理，添加断路器和重试保护
                syndrome_result, constitution_result = await with_circuit_breaker_and_retry(
                    self.reasoning_engine.analyze_fusion_result,
                    self.reasoning_cb,
                    self.long_running_retry,
                    fusion_result
                )
                
                # 更新报告
                report.syndrome_analysis.CopyFrom(syndrome_result)
                report.constitution_analysis.CopyFrom(constitution_result)
                
                # 生成诊断总结和建议
                summary, recommendations = await self._generate_summary_and_recommendations(
                    syndrome_result, 
                    constitution_result,
                    single_results
                )
                
                report.diagnostic_summary = summary
                for rec in recommendations:
                    report.recommendations.append(rec)
                
                # 计算整体置信度
                report.overall_confidence = self._calculate_overall_confidence(
                    single_results, 
                    syndrome_result, 
                    constitution_result
                )
                
                # 更新进度
                progress.analysis_completed = True
                progress.status_message = "诊断分析已完成"
                progress.overall_progress = 1.0
                self._update_progress(progress)
                
            except Exception as e:
                logger.error(f"融合和推理失败: {e}")
                report.diagnostic_summary = "由于处理过程中的错误，无法生成完整的诊断报告"
                progress.status_message = f"融合和推理失败: {e}"
        else:
            report.diagnostic_summary = "可用的诊断数据不足，无法进行完整的辨证分析"
            progress.status_message = "可用的诊断数据不足，至少需要两种诊断方法"
        
        # 更新完成时间
        report.created_at = int(time.time())
        
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
        single_results = []
        
        for analysis_id in request.analysis_ids:
            # 这里应该根据实际情况从数据库获取结果
            # 这里仅作为示例
            pass
        
        if not single_results:
            raise ValueError("未找到分析结果")
        
        # 执行多模态融合
        fusion_result = await self.fusion_engine.fuse_diagnostic_data(
            request.user_id,
            request.session_id,
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
        # 实际实现应该根据analysis_id从数据库获取
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
        session_key = f"{request.user_id}:{request.session_id}"
        
        if session_key not in self._progress_store:
            # 如果没有找到进度，创建一个新的
            progress = DiagnosisProgress(
                user_id=request.user_id,
                session_id=request.session_id
            )
        else:
            progress = self._progress_store[session_key]
        
        # 创建响应
        response = diagnosis_pb.DiagnosisProgressResponse(
            user_id=progress.user_id,
            session_id=progress.session_id,
            look_completed=progress.look_completed,
            listen_completed=progress.listen_completed,
            inquiry_completed=progress.inquiry_completed,
            palpation_completed=progress.palpation_completed,
            fusion_completed=progress.fusion_completed,
            analysis_completed=progress.analysis_completed,
            overall_progress=progress.overall_progress,
            status_message=progress.status_message,
            last_updated=progress.last_updated
        )
        
        return response
    
    # 以下是内部辅助方法
    
    async def _process_look_data(self, user_id: str, session_id: str, look_data: diagnosis_pb.LookData) -> Optional[diagnosis_pb.SingleDiagnosisResult]:
        """处理望诊数据"""
        try:
            session_key = f"{user_id}:{session_id}"
            progress = self._progress_store.get(session_key)
            
            if progress:
                progress.status_message = "正在处理望诊数据..."
                self._update_progress(progress)
            
            # 根据数据类型调用不同的接口
            if look_data.HasField('tongue_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyze_tongue,
                    self.look_cb,
                    self.standard_retry,
                    look_data.tongue_image,
                    user_id,
                    True,
                    look_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_tongue_result_to_single_diagnosis(response, user_id, session_id)
                
            elif look_data.HasField('face_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyze_face,
                    self.look_cb,
                    self.standard_retry,
                    look_data.face_image,
                    user_id,
                    True,
                    look_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_face_result_to_single_diagnosis(response, user_id, session_id)
                
            elif look_data.HasField('body_image'):
                # 使用断路器和重试机制包装调用
                response = await with_circuit_breaker_and_retry(
                    self.look_client.analyze_body,
                    self.look_cb,
                    self.standard_retry,
                    look_data.body_image,
                    user_id,
                    True,
                    look_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_body_result_to_single_diagnosis(response, user_id, session_id)
                
            else:
                raise ValueError("无效的望诊数据")
            
            if progress:
                progress.look_completed = True
                self._update_progress(progress)
                
            return result
            
        except Exception as e:
            logger.error(f"处理望诊数据失败: {e}")
            if progress:
                progress.status_message = f"处理望诊数据失败: {e}"
                self._update_progress(progress)
            return None
    
    async def _process_listen_data(self, user_id: str, session_id: str, listen_data: diagnosis_pb.ListenData) -> Optional[diagnosis_pb.SingleDiagnosisResult]:
        """处理闻诊数据"""
        try:
            session_key = f"{user_id}:{session_id}"
            progress = self._progress_store.get(session_key)
            
            if progress:
                progress.status_message = "正在处理闻诊数据..."
                self._update_progress(progress)
            
            # 根据数据类型调用不同的接口
            if listen_data.HasField('voice_audio'):
                response = await self.listen_client.analyze_voice(
                    listen_data.voice_audio,
                    user_id,
                    listen_data.audio_format if hasattr(listen_data, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listen_data, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listen_data, 'channels') else 1,
                    True,
                    listen_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_voice_result_to_single_diagnosis(response, user_id, session_id)
                
            elif listen_data.HasField('breathing_audio'):
                response = await self.listen_client.analyze_breathing(
                    listen_data.breathing_audio,
                    user_id,
                    listen_data.audio_format if hasattr(listen_data, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listen_data, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listen_data, 'channels') else 1,
                    True,
                    listen_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_breathing_result_to_single_diagnosis(response, user_id, session_id)
                
            elif listen_data.HasField('cough_audio'):
                response = await self.listen_client.analyze_cough(
                    listen_data.cough_audio,
                    user_id,
                    listen_data.audio_format if hasattr(listen_data, 'audio_format') else "wav",
                    listen_data.sample_rate if hasattr(listen_data, 'sample_rate') else 16000,
                    listen_data.channels if hasattr(listen_data, 'channels') else 1,
                    True,
                    listen_data.metadata
                )
                
                # 转换为标准化结果
                result = self._convert_cough_result_to_single_diagnosis(response, user_id, session_id)
                
            else:
                raise ValueError("无效的闻诊数据")
            
            if progress:
                progress.listen_completed = True
                self._update_progress(progress)
                
            return result
            
        except Exception as e:
            logger.error(f"处理闻诊数据失败: {e}")
            if progress:
                progress.status_message = f"处理闻诊数据失败: {e}"
                self._update_progress(progress)
            return None
    
    def _convert_voice_result_to_single_diagnosis(self, response, user_id: str, session_id: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将语音分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysis_id,
            diagnosis_type="listen",
            user_id=user_id,
            session_id=session_id,
            created_at=int(time.time()),
            summary=response.analysis_summary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )
        
        # 添加详情
        voice_analysis = diagnosis_pb.VoiceAnalysis(
            voice_quality=response.voice_quality,
            voice_strength=response.voice_strength,
            voice_rhythm=response.voice_rhythm,
            voice_tone=response.voice_tone
        )
        
        # 设置结果详情
        result.listen_detail.voice.CopyFrom(voice_analysis)
        
        # 添加特征
        for feature in response.features:
            diag_feature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="voice"
            )
            result.features.append(diag_feature)
        
        return result
    
    def _convert_breathing_result_to_single_diagnosis(self, response, user_id: str, session_id: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将呼吸分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysis_id,
            diagnosis_type="listen",
            user_id=user_id,
            session_id=session_id,
            created_at=int(time.time()),
            summary=response.analysis_summary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )
        
        # 添加详情
        breathing_analysis = diagnosis_pb.BreathingAnalysis(
            breathing_rate=response.breathing_rate,
            breathing_depth=response.breathing_depth,
            breathing_rhythm=response.breathing_rhythm,
            breathing_sound=response.breathing_sound
        )
        
        # 设置结果详情
        result.listen_detail.breathing.CopyFrom(breathing_analysis)
        
        # 添加特征
        for feature in response.features:
            diag_feature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="breathing"
            )
            result.features.append(diag_feature)
        
        return result
    
    def _convert_cough_result_to_single_diagnosis(self, response, user_id: str, session_id: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将咳嗽分析结果转换为标准化诊断结果"""
        # 这里根据实际响应结构进行转换
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysis_id,
            diagnosis_type="listen",
            user_id=user_id,
            session_id=session_id,
            created_at=int(time.time()),
            summary=response.analysis_summary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.8
        )
        
        # 添加详情
        cough_analysis = diagnosis_pb.CoughAnalysis(
            cough_type=response.cough_type,
            cough_strength=response.cough_strength,
            cough_frequency=response.cough_frequency,
            cough_sound=response.cough_sound
        )
        
        # 设置结果详情
        result.listen_detail.cough.CopyFrom(cough_analysis)
        
        # 添加特征
        for feature in response.features:
            diag_feature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature,
                feature_value="present",
                confidence=0.85,  # 这里应该使用实际置信度
                source="listen_service",
                category="cough"
            )
            result.features.append(diag_feature)
        
        return result
    
    def _convert_medical_history_result_to_single_diagnosis(self, response, user_id: str, session_id: str) -> diagnosis_pb.SingleDiagnosisResult:
        """将病史分析结果转换为标准化诊断结果"""
        result = diagnosis_pb.SingleDiagnosisResult(
            diagnosis_id=response.analysis_id,
            diagnosis_type="inquiry",
            user_id=user_id,
            session_id=session_id,
            created_at=int(time.time()),
            summary=response.analysis_summary,
            confidence=response.confidence if hasattr(response, 'confidence') else 0.9
        )
        
        # 添加详情
        medical_history_analysis = diagnosis_pb.MedicalHistoryAnalysis()
        
        # 添加风险因素
        for risk_factor in response.risk_factors:
            history_risk = diagnosis_pb.HistoryRiskFactor(
                factor=risk_factor.name,
                risk_level=risk_factor.risk_level,
                description=risk_factor.description
            )
            medical_history_analysis.risk_factors.append(history_risk)
        
        # 添加病史特征
        for pattern in response.historical_patterns:
            history_pattern = diagnosis_pb.HistoricalPattern(
                pattern_name=pattern.name,
                significance=pattern.significance,
                description=pattern.description
            )
            medical_history_analysis.patterns.append(history_pattern)
        
        # 设置结果详情
        result.inquiry_detail.medical_history.CopyFrom(medical_history_analysis)
        
        # 添加特征
        for condition in response.chronic_conditions:
            diag_feature = diagnosis_pb.DiagnosticFeature(
                feature_name=condition.name,
                feature_value="chronic",
                confidence=1.0,  # 已确诊的慢性病，置信度为1
                source="inquiry_service",
                category="chronic_disease"
            )
            result.features.append(diag_feature)
        
        return result