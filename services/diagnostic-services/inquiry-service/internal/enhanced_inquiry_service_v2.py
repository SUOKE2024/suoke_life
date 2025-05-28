#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版问诊服务 V2

该模块是问诊服务的最新优化版本，集成了智能流程管理、中医知识图谱、
实时健康监测等先进功能，提供全面的智能问诊解决方案。
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from loguru import logger

from .common.base import BaseService
from .common.exceptions import InquiryServiceError
from .common.metrics import timer, counter, memory_optimized
from .common.cache import cached

# 导入新增的优化组件
from .dialogue.intelligent_flow_manager import (
    IntelligentFlowManager, InquiryContext, FlowDecision
)
from .knowledge.tcm_knowledge_graph import (
    TCMKnowledgeGraph, SyndromeMapping, FormulaRecommendation
)
from .observability.health_monitor import (
    HealthMonitor, HealthStatus
)

# 导入现有组件
from .extractors.symptom_extractor import SymptomExtractor
from .extractors.context_analyzer import ContextAnalyzer
from .extractors.severity_analyzer import SeverityAnalyzer


@dataclass
class InquiryRequest:
    """问诊请求"""
    session_id: str
    patient_id: str
    message: str
    message_type: str = "text"  # text, voice, image
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InquiryResponse:
    """问诊响应"""
    session_id: str
    response_text: str
    next_questions: List[Dict[str, Any]]
    detected_symptoms: List[Dict[str, Any]]
    syndrome_analysis: Optional[Dict[str, Any]] = None
    formula_recommendations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagnosisResult:
    """诊断结果"""
    session_id: str
    patient_id: str
    chief_complaint: str
    symptom_summary: List[Dict[str, Any]]
    syndrome_mappings: List[SyndromeMapping]
    formula_recommendations: List[FormulaRecommendation]
    health_assessment: Dict[str, Any]
    recommendations: List[str]
    confidence_score: float
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedInquiryServiceV2(BaseService):
    """增强版问诊服务 V2"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化增强版问诊服务 V2
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        
        # 核心组件
        self.flow_manager: Optional[IntelligentFlowManager] = None
        self.knowledge_graph: Optional[TCMKnowledgeGraph] = None
        self.health_monitor: Optional[HealthMonitor] = None
        
        # 提取器组件
        self.symptom_extractor: Optional[SymptomExtractor] = None
        self.context_analyzer: Optional[ContextAnalyzer] = None
        self.severity_analyzer: Optional[SeverityAnalyzer] = None
        
        # 服务配置
        self.service_config = {
            'max_concurrent_sessions': 1000,
            'session_timeout_minutes': 30,
            'auto_diagnosis_threshold': 0.8,
            'emergency_detection_enabled': True,
            'knowledge_graph_enabled': True,
            'health_monitoring_enabled': True,
            'real_time_analysis': True
        }
        
        # 活跃会话
        self.active_sessions: Dict[str, InquiryContext] = {}
        
        # 性能统计
        self.stats = {
            'total_sessions': 0,
            'completed_sessions': 0,
            'emergency_detections': 0,
            'syndrome_mappings': 0,
            'formula_recommendations': 0,
            'average_session_duration': 0.0,
            'average_questions_per_session': 0.0,
            'service_uptime': datetime.now()
        }
        
        logger.info("增强版问诊服务 V2 初始化开始")

    async def initialize(self):
        """初始化服务组件"""
        try:
            # 初始化智能流程管理器
            self.flow_manager = IntelligentFlowManager(self.config)
            
            # 初始化中医知识图谱
            if self.service_config['knowledge_graph_enabled']:
                self.knowledge_graph = TCMKnowledgeGraph(self.config)
            
            # 初始化健康监测器
            if self.service_config['health_monitoring_enabled']:
                self.health_monitor = HealthMonitor(self.config)
                await self.health_monitor.start_monitoring()
            
            # 初始化提取器组件
            self.symptom_extractor = SymptomExtractor(self.config)
            self.context_analyzer = ContextAnalyzer(self.config)
            self.severity_analyzer = SeverityAnalyzer(self.config)
            
            logger.info("增强版问诊服务 V2 初始化完成")
            
        except Exception as e:
            logger.error(f"服务初始化失败: {e}")
            raise InquiryServiceError(f"服务初始化失败: {e}")

    @timer("inquiry_service_v2.start_session")
    @counter("inquiry_service_v2.sessions_started")
    async def start_inquiry_session(
        self,
        patient_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> InquiryContext:
        """
        开始问诊会话
        
        Args:
            patient_id: 患者ID
            initial_data: 初始数据
            
        Returns:
            问诊上下文
        """
        try:
            # 检查并发限制
            if len(self.active_sessions) >= self.service_config['max_concurrent_sessions']:
                raise InquiryServiceError("服务繁忙，请稍后重试")
            
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 使用流程管理器创建会话
            context = await self.flow_manager.start_inquiry_session(
                session_id=session_id,
                patient_id=patient_id,
                initial_data=initial_data
            )
            
            # 注册会话
            self.active_sessions[session_id] = context
            self.stats['total_sessions'] += 1
            
            logger.info(f"问诊会话已开始: {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"开始问诊会话失败: {e}")
            raise InquiryServiceError(f"开始问诊会话失败: {e}")

    @timer("inquiry_service_v2.process_message")
    @counter("inquiry_service_v2.messages_processed")
    async def process_inquiry_message(
        self,
        request: InquiryRequest
    ) -> InquiryResponse:
        """
        处理问诊消息
        
        Args:
            request: 问诊请求
            
        Returns:
            问诊响应
        """
        try:
            # 获取会话上下文
            context = self.active_sessions.get(request.session_id)
            if not context:
                raise InquiryServiceError(f"会话不存在: {request.session_id}")
            
            # 提取症状信息
            symptoms = await self._extract_symptoms(request.message)
            
            # 分析上下文
            context_info = await self._analyze_context(request.message, context)
            
            # 分析严重程度
            severity_info = await self._analyze_severity(symptoms)
            
            # 更新会话数据
            await self._update_session_data(
                context, request.message, symptoms, context_info, severity_info
            )
            
            # 流程决策
            decision = await self.flow_manager.process_answer(
                session_id=request.session_id,
                question_id="user_message",
                answer=request.message,
                confidence=1.0
            )
            
            # 生成响应
            response = await self._generate_response(context, decision, symptoms)
            
            # 实时分析（如果启用）
            if self.service_config['real_time_analysis']:
                await self._perform_real_time_analysis(context, response)
            
            logger.debug(f"消息处理完成: {request.session_id}")
            return response
            
        except Exception as e:
            logger.error(f"处理问诊消息失败: {e}")
            raise InquiryServiceError(f"处理问诊消息失败: {e}")

    async def _extract_symptoms(self, message: str) -> List[Dict[str, Any]]:
        """提取症状"""
        if not self.symptom_extractor:
            return []
        
        try:
            symptoms = await self.symptom_extractor.extract_symptoms(message)
            return symptoms
        except Exception as e:
            logger.warning(f"症状提取失败: {e}")
            return []

    async def _analyze_context(
        self,
        message: str,
        context: InquiryContext
    ) -> Dict[str, Any]:
        """分析上下文"""
        if not self.context_analyzer:
            return {}
        
        try:
            context_info = await self.context_analyzer.analyze_context(
                text=message,
                existing_symptoms=context.symptom_profile
            )
            return context_info
        except Exception as e:
            logger.warning(f"上下文分析失败: {e}")
            return {}

    async def _analyze_severity(
        self,
        symptoms: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析严重程度"""
        if not self.severity_analyzer or not symptoms:
            return {}
        
        try:
            severity_info = await self.severity_analyzer.analyze_severity(symptoms)
            return severity_info
        except Exception as e:
            logger.warning(f"严重程度分析失败: {e}")
            return {}

    async def _update_session_data(
        self,
        context: InquiryContext,
        message: str,
        symptoms: List[Dict[str, Any]],
        context_info: Dict[str, Any],
        severity_info: Dict[str, Any]
    ):
        """更新会话数据"""
        # 更新症状档案
        for symptom in symptoms:
            symptom_name = symptom.get('name', '')
            if symptom_name:
                context.symptom_profile[symptom_name] = {
                    'severity': symptom.get('severity', 0),
                    'confidence': symptom.get('confidence', 0),
                    'context': context_info,
                    'timestamp': datetime.now().isoformat()
                }
        
        # 更新收集的数据
        context.collected_data.update({
            'latest_message': message,
            'symptoms_detected': len(symptoms),
            'context_analysis': context_info,
            'severity_analysis': severity_info
        })

    async def _generate_response(
        self,
        context: InquiryContext,
        decision: FlowDecision,
        symptoms: List[Dict[str, Any]]
    ) -> InquiryResponse:
        """生成响应"""
        # 生成下一批问题
        next_questions = await self.flow_manager.generate_next_questions(
            session_id=context.session_id,
            max_questions=3
        )
        
        # 生成响应文本
        response_text = await self._generate_response_text(context, decision)
        
        # 证型分析（如果有足够信息）
        syndrome_analysis = None
        formula_recommendations = []
        
        if (self.knowledge_graph and 
            len(context.symptom_profile) >= 3):  # 至少3个症状才进行分析
            
            syndrome_mappings = await self.knowledge_graph.map_symptoms_to_syndromes(
                symptoms=symptoms,
                patient_context=context.metadata
            )
            
            if syndrome_mappings:
                syndrome_analysis = {
                    'primary_syndrome': syndrome_mappings[0].syndrome_name,
                    'confidence': syndrome_mappings[0].confidence,
                    'all_mappings': [
                        {
                            'name': mapping.syndrome_name,
                            'score': mapping.match_score,
                            'confidence': mapping.confidence
                        }
                        for mapping in syndrome_mappings[:3]
                    ]
                }
                
                # 方剂推荐
                formula_recs = await self.knowledge_graph.recommend_formulas(
                    syndrome_mappings=syndrome_mappings[:2],  # 取前2个证型
                    patient_context=context.metadata
                )
                
                formula_recommendations = [
                    {
                        'name': rec.formula_name,
                        'score': rec.recommendation_score,
                        'confidence': rec.confidence,
                        'reasoning': rec.reasoning
                    }
                    for rec in formula_recs[:3]
                ]
        
        return InquiryResponse(
            session_id=context.session_id,
            response_text=response_text,
            next_questions=next_questions,
            detected_symptoms=[
                {
                    'name': symptom.get('name', ''),
                    'severity': symptom.get('severity', 0),
                    'confidence': symptom.get('confidence', 0)
                }
                for symptom in symptoms
            ],
            syndrome_analysis=syndrome_analysis,
            formula_recommendations=formula_recommendations,
            confidence=decision.confidence,
            metadata={
                'decision_type': decision.decision_type.value,
                'current_stage': context.current_stage.value,
                'processing_time': datetime.now().isoformat()
            }
        )

    async def _generate_response_text(
        self,
        context: InquiryContext,
        decision: FlowDecision
    ) -> str:
        """生成响应文本"""
        # 基于决策类型生成不同的响应
        if decision.decision_type.value == "emergency_protocol":
            return "根据您描述的症状，建议您立即就医。请尽快前往最近的医院急诊科。"
        
        elif decision.decision_type.value == "advance_stage":
            stage_messages = {
                "chief_complaint": "感谢您的描述。让我们进一步了解您的症状。",
                "symptom_exploration": "我需要更详细地了解您的症状特点。",
                "system_review": "让我们检查一下是否还有其他相关症状。",
                "history_taking": "请告诉我您的相关病史。",
                "risk_assessment": "最后，我需要了解一些风险因素。"
            }
            
            next_stage = decision.next_stage
            if next_stage:
                return stage_messages.get(
                    next_stage.value, 
                    "让我们继续问诊。"
                )
        
        elif decision.decision_type.value == "conclude_inquiry":
            return "感谢您的配合。基于您提供的信息，我将为您生成诊断建议。"
        
        # 默认响应
        return "我理解了您的情况。让我们继续深入了解。"

    async def _perform_real_time_analysis(
        self,
        context: InquiryContext,
        response: InquiryResponse
    ):
        """执行实时分析"""
        try:
            # 检查是否需要自动诊断
            if (response.syndrome_analysis and 
                response.syndrome_analysis.get('confidence', 0) >= 
                self.service_config['auto_diagnosis_threshold']):
                
                # 触发自动诊断流程
                await self._trigger_auto_diagnosis(context)
            
            # 更新统计信息
            self._update_real_time_stats(context, response)
            
        except Exception as e:
            logger.warning(f"实时分析失败: {e}")

    async def _trigger_auto_diagnosis(self, context: InquiryContext):
        """触发自动诊断"""
        try:
            # 标记为自动诊断
            context.metadata['auto_diagnosis_triggered'] = True
            context.metadata['auto_diagnosis_time'] = datetime.now().isoformat()
            
            logger.info(f"自动诊断已触发: {context.session_id}")
            
        except Exception as e:
            logger.error(f"自动诊断触发失败: {e}")

    def _update_real_time_stats(
        self,
        context: InquiryContext,
        response: InquiryResponse
    ):
        """更新实时统计"""
        # 更新证型映射统计
        if response.syndrome_analysis:
            self.stats['syndrome_mappings'] += 1
        
        # 更新方剂推荐统计
        if response.formula_recommendations:
            self.stats['formula_recommendations'] += len(response.formula_recommendations)

    @timer("inquiry_service_v2.generate_diagnosis")
    @counter("inquiry_service_v2.diagnoses_generated")
    async def generate_diagnosis(
        self,
        session_id: str
    ) -> DiagnosisResult:
        """
        生成诊断结果
        
        Args:
            session_id: 会话ID
            
        Returns:
            诊断结果
        """
        try:
            start_time = datetime.now()
            
            # 获取会话上下文
            context = self.active_sessions.get(session_id)
            if not context:
                raise InquiryServiceError(f"会话不存在: {session_id}")
            
            # 提取主诉
            chief_complaint = context.collected_data.get('chief_complaint', '未明确主诉')
            
            # 症状汇总
            symptom_summary = [
                {
                    'name': name,
                    'details': details
                }
                for name, details in context.symptom_profile.items()
            ]
            
            # 证型映射
            syndrome_mappings = []
            formula_recommendations = []
            
            if self.knowledge_graph and symptom_summary:
                # 转换症状格式
                symptoms_for_mapping = [
                    {
                        'name': item['name'],
                        'severity': item['details'].get('severity', 0),
                        'confidence': item['details'].get('confidence', 0)
                    }
                    for item in symptom_summary
                ]
                
                # 证型映射
                syndrome_mappings = await self.knowledge_graph.map_symptoms_to_syndromes(
                    symptoms=symptoms_for_mapping,
                    patient_context=context.metadata
                )
                
                # 方剂推荐
                if syndrome_mappings:
                    formula_recommendations = await self.knowledge_graph.recommend_formulas(
                        syndrome_mappings=syndrome_mappings,
                        patient_context=context.metadata
                    )
            
            # 健康评估
            health_assessment = await self._generate_health_assessment(
                context, syndrome_mappings
            )
            
            # 生成建议
            recommendations = await self._generate_recommendations(
                context, syndrome_mappings, formula_recommendations
            )
            
            # 计算置信度
            confidence_score = self._calculate_diagnosis_confidence(
                context, syndrome_mappings
            )
            
            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # 更新统计
            self.stats['completed_sessions'] += 1
            
            # 创建诊断结果
            diagnosis = DiagnosisResult(
                session_id=session_id,
                patient_id=context.patient_id,
                chief_complaint=chief_complaint,
                symptom_summary=symptom_summary,
                syndrome_mappings=syndrome_mappings,
                formula_recommendations=formula_recommendations,
                health_assessment=health_assessment,
                recommendations=recommendations,
                confidence_score=confidence_score,
                processing_time_ms=processing_time,
                metadata={
                    'session_duration': (datetime.now() - context.stage_history[0][1]).total_seconds(),
                    'questions_answered': len(context.answered_questions),
                    'stages_completed': len(context.stage_history),
                    'generation_time': datetime.now().isoformat()
                }
            )
            
            logger.info(f"诊断结果已生成: {session_id}")
            return diagnosis
            
        except Exception as e:
            logger.error(f"生成诊断结果失败: {e}")
            raise InquiryServiceError(f"生成诊断结果失败: {e}")

    async def _generate_health_assessment(
        self,
        context: InquiryContext,
        syndrome_mappings: List[SyndromeMapping]
    ) -> Dict[str, Any]:
        """生成健康评估"""
        assessment = {
            'overall_status': 'unknown',
            'risk_level': 'low',
            'key_concerns': [],
            'positive_indicators': []
        }
        
        # 基于症状数量评估
        symptom_count = len(context.symptom_profile)
        if symptom_count >= 5:
            assessment['risk_level'] = 'high'
            assessment['key_concerns'].append('症状较多，需要重点关注')
        elif symptom_count >= 3:
            assessment['risk_level'] = 'medium'
        
        # 基于证型评估
        if syndrome_mappings:
            primary_syndrome = syndrome_mappings[0]
            if primary_syndrome.confidence >= 0.8:
                assessment['overall_status'] = 'identifiable_pattern'
                assessment['key_concerns'].append(f'识别出明确证型：{primary_syndrome.syndrome_name}')
            else:
                assessment['overall_status'] = 'unclear_pattern'
        
        # 检查紧急情况
        if context.metadata.get('emergency_detected'):
            assessment['risk_level'] = 'critical'
            assessment['key_concerns'].append('检测到紧急情况')
        
        return assessment

    async def _generate_recommendations(
        self,
        context: InquiryContext,
        syndrome_mappings: List[SyndromeMapping],
        formula_recommendations: List[FormulaRecommendation]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 基于证型的建议
        if syndrome_mappings:
            primary_syndrome = syndrome_mappings[0]
            recommendations.append(f"根据症状分析，您可能存在{primary_syndrome.syndrome_name}的情况")
            
            # 生活方式建议
            if '气虚' in primary_syndrome.syndrome_name:
                recommendations.extend([
                    "建议适当休息，避免过度劳累",
                    "可以适量进行温和的运动，如散步、太极拳",
                    "饮食上可以多食用补气的食物，如山药、大枣等"
                ])
            elif '血瘀' in primary_syndrome.syndrome_name:
                recommendations.extend([
                    "建议适当活动，促进血液循环",
                    "避免久坐久卧",
                    "可以进行适量的有氧运动"
                ])
        
        # 基于方剂的建议
        if formula_recommendations:
            top_formula = formula_recommendations[0]
            recommendations.append(f"可以考虑使用{top_formula.formula_name}进行调理")
            recommendations.append("具体用药请咨询专业中医师")
        
        # 通用建议
        recommendations.extend([
            "建议保持规律的作息时间",
            "注意饮食均衡，避免过度辛辣刺激食物",
            "如症状持续或加重，请及时就医"
        ])
        
        # 紧急情况建议
        if context.metadata.get('emergency_detected'):
            recommendations.insert(0, "⚠️ 建议立即就医，前往最近的医院急诊科")
        
        return recommendations

    def _calculate_diagnosis_confidence(
        self,
        context: InquiryContext,
        syndrome_mappings: List[SyndromeMapping]
    ) -> float:
        """计算诊断置信度"""
        confidence_factors = []
        
        # 症状数量因子
        symptom_count = len(context.symptom_profile)
        if symptom_count >= 5:
            confidence_factors.append(0.9)
        elif symptom_count >= 3:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 证型匹配因子
        if syndrome_mappings:
            primary_confidence = syndrome_mappings[0].confidence
            confidence_factors.append(primary_confidence)
        else:
            confidence_factors.append(0.3)
        
        # 问诊完整度因子
        answered_questions = len(context.answered_questions)
        if answered_questions >= 10:
            confidence_factors.append(0.9)
        elif answered_questions >= 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # 计算综合置信度
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.5

    @memory_optimized
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        context = self.active_sessions.get(session_id)
        if not context:
            raise InquiryServiceError(f"会话不存在: {session_id}")
        
        return await self.flow_manager.get_session_summary(session_id)

    async def end_inquiry_session(self, session_id: str) -> Dict[str, Any]:
        """结束问诊会话"""
        try:
            context = self.active_sessions.get(session_id)
            if not context:
                raise InquiryServiceError(f"会话不存在: {session_id}")
            
            # 获取会话摘要
            summary = await self.flow_manager.get_session_summary(session_id)
            
            # 清理会话
            await self.flow_manager.cleanup_session(session_id)
            del self.active_sessions[session_id]
            
            logger.info(f"问诊会话已结束: {session_id}")
            return summary
            
        except Exception as e:
            logger.error(f"结束问诊会话失败: {e}")
            raise InquiryServiceError(f"结束问诊会话失败: {e}")

    async def get_service_health(self) -> Dict[str, Any]:
        """获取服务健康状态"""
        health_info = {
            'service_status': 'healthy',
            'active_sessions': len(self.active_sessions),
            'stats': self.stats,
            'uptime_seconds': (datetime.now() - self.stats['service_uptime']).total_seconds()
        }
        
        # 添加健康监测信息
        if self.health_monitor:
            monitor_health = await self.health_monitor.get_health_status()
            health_info['health_monitor'] = monitor_health
        
        # 添加知识图谱统计
        if self.knowledge_graph:
            kg_stats = await self.knowledge_graph.get_knowledge_stats()
            health_info['knowledge_graph'] = kg_stats
        
        return health_info

    async def cleanup(self):
        """清理资源"""
        try:
            # 停止健康监测
            if self.health_monitor:
                await self.health_monitor.stop_monitoring()
            
            # 清理所有会话
            for session_id in list(self.active_sessions.keys()):
                await self.flow_manager.cleanup_session(session_id)
            
            self.active_sessions.clear()
            
            logger.info("增强版问诊服务 V2 清理完成")
            
        except Exception as e:
            logger.error(f"服务清理失败: {e}")
            raise InquiryServiceError(f"服务清理失败: {e}") 