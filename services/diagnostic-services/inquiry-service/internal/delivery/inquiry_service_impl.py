#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问诊服务实现模块，处理各种RPC请求
"""

import logging
import time
from typing import Dict, List, Optional, Any

import grpc
from google.protobuf.json_format import MessageToDict

from ..dialogue.dialogue_manager import DialogueManager
from ..llm.symptom_extractor import SymptomExtractor
from ..llm.tcm_pattern_mapper import TCMPatternMapper
from ..llm.health_risk_assessor import HealthRiskAssessor
from ..knowledge.tcm_knowledge_base import TCMKnowledgeBase

# 导入生成的gRPC代码
# 需要先生成proto文件的Python代码
# python -m grpc_tools.protoc -I./api/grpc --python_out=. --grpc_python_out=. ./api/grpc/inquiry_service.proto
from api.grpc import inquiry_service_pb2 as pb2
from api.grpc import inquiry_service_pb2_grpc as pb2_grpc

logger = logging.getLogger(__name__)


class InquiryServiceServicer(pb2_grpc.InquiryServiceServicer):
    """问诊服务的gRPC实现类"""

    def __init__(
        self,
        dialogue_manager: DialogueManager,
        symptom_extractor: SymptomExtractor,
        tcm_pattern_mapper: TCMPatternMapper,
        health_risk_assessor: HealthRiskAssessor,
        tcm_knowledge_base: TCMKnowledgeBase,
        config: Dict[str, Any]
    ):
        """
        初始化问诊服务实现
        
        Args:
            dialogue_manager: 对话管理器
            symptom_extractor: 症状提取器
            tcm_pattern_mapper: TCM证型映射器
            health_risk_assessor: 健康风险评估器
            tcm_knowledge_base: 中医知识库
            config: 配置信息
        """
        self.dialogue_manager = dialogue_manager
        self.symptom_extractor = symptom_extractor
        self.tcm_pattern_mapper = tcm_pattern_mapper
        self.health_risk_assessor = health_risk_assessor
        self.tcm_knowledge_base = tcm_knowledge_base
        self.config = config
        
        logger.info("问诊服务实现初始化完成")

    async def StartInquirySession(self, request, context):
        """
        开始问诊会话
        
        Args:
            request: StartSessionRequest
            context: gRPC上下文
            
        Returns:
            SessionResponse
        """
        try:
            # 提取请求参数
            user_id = request.user_id
            session_type = request.session_type
            language_preference = request.language_preference
            context_data = dict(request.context_data)
            
            # 调用对话管理器开始会话
            session_id, welcome_message, suggested_questions = await self.dialogue_manager.start_session(
                user_id=user_id,
                session_type=session_type,
                language=language_preference,
                context_data=context_data
            )
            
            # 构建响应
            response = pb2.SessionResponse(
                session_id=session_id,
                welcome_message=welcome_message,
                suggested_questions=suggested_questions,
                timestamp=int(time.time())
            )
            
            logger.info(f"开始问诊会话: user_id={user_id}, session_id={session_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"开始问诊会话失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"开始问诊会话失败: {str(e)}")
            return pb2.SessionResponse()

    async def InteractWithUser(self, request, context):
        """
        与用户交互
        
        Args:
            request: InteractionRequest
            context: gRPC上下文
            
        Returns:
            stream InteractionResponse
        """
        try:
            # 提取请求参数
            session_id = request.session_id
            user_message = request.user_message
            timestamp = request.timestamp or int(time.time())
            attached_data_urls = list(request.attached_data_urls)
            
            # 调用对话管理器处理交互
            response_dict = await self.dialogue_manager.interact(
                session_id=session_id,
                user_message=user_message,
                timestamp=timestamp,
                attached_data_urls=attached_data_urls
            )
            
            # 构建响应
            response = pb2.InteractionResponse(
                response_text=response_dict.get('response_text', ''),
                response_type=self._get_response_type(response_dict.get('response_type', 'TEXT')),
                detected_symptoms=response_dict.get('detected_symptoms', []),
                follow_up_questions=response_dict.get('follow_up_questions', []),
                timestamp=response_dict.get('timestamp', int(time.time()))
            )
            
            logger.info(f"用户交互: session_id={session_id}, message={user_message[:50]}...")
            
            # 返回流式响应
            yield response
            
        except ValueError as e:
            # 会话不存在或已过期
            logger.error(f"用户交互失败(会话无效): {str(e)}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"会话不存在或已过期: {str(e)}")
            yield pb2.InteractionResponse()
        except Exception as e:
            # 其他错误
            logger.error(f"用户交互失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"用户交互失败: {str(e)}")
            yield pb2.InteractionResponse()
            
    def _get_response_type(self, type_str: str) -> int:
        """将响应类型字符串转换为枚举值"""
        response_types = {
            'TEXT': pb2.InteractionResponse.TEXT,
            'FOLLOW_UP_QUESTION': pb2.InteractionResponse.FOLLOW_UP_QUESTION,
            'SYMPTOM_CONFIRMATION': pb2.InteractionResponse.SYMPTOM_CONFIRMATION,
            'RECOMMENDATION': pb2.InteractionResponse.RECOMMENDATION,
            'INFO_REQUEST': pb2.InteractionResponse.INFO_REQUEST
        }
        
        return response_types.get(type_str, pb2.InteractionResponse.TEXT)

    async def EndInquirySession(self, request, context):
        """
        结束问诊会话
        
        Args:
            request: EndSessionRequest
            context: gRPC上下文
            
        Returns:
            InquirySummary
        """
        try:
            # 提取请求参数
            session_id = request.session_id
            feedback = request.feedback
            
            # 调用对话管理器结束会话
            summary_dict = await self.dialogue_manager.end_session(
                session_id=session_id,
                feedback=feedback
            )
            
            # 构建响应
            response = pb2.InquirySummary(
                session_id=summary_dict.get('session_id', ''),
                user_id=summary_dict.get('user_id', ''),
                session_duration=int(summary_dict.get('session_duration', 0)),
                session_end_time=int(summary_dict.get('session_end_time', 0))
            )
            
            # 添加检测到的症状
            symptoms = summary_dict.get('detected_symptoms', [])
            for symptom in symptoms:
                symptom_info = pb2.SymptomInfo(
                    symptom_name=symptom.get('symptom_name', ''),
                    severity=self._get_symptom_severity(symptom.get('severity', 'MODERATE')),
                    onset_time=int(symptom.get('onset_time', 0)),
                    duration=int(symptom.get('duration', 0)),
                    description=symptom.get('description', ''),
                    confidence=float(symptom.get('confidence', 0.8))
                )
                response.detected_symptoms.append(symptom_info)
                
            # 添加TCM证型
            tcm_patterns = summary_dict.get('tcm_patterns', [])
            for pattern in tcm_patterns:
                tcm_pattern = pb2.TCMPattern(
                    pattern_name=pattern.get('pattern_name', ''),
                    category=pattern.get('category', ''),
                    match_score=float(pattern.get('match_score', 0.0)),
                    description=pattern.get('description', '')
                )
                tcm_pattern.related_symptoms.extend(pattern.get('related_symptoms', []))
                response.tcm_patterns.append(tcm_pattern)
                
            # 添加健康档案
            health_profile = summary_dict.get('health_profile', {})
            profile = pb2.HealthProfile(
                user_id=health_profile.get('user_id', ''),
                constitution_type=self._get_constitution_type(health_profile.get('constitution_type', 'BALANCED'))
            )
            response.health_profile.CopyFrom(profile)
            
            # 添加建议
            recommendations = summary_dict.get('recommendations', [])
            for rec in recommendations:
                recommendation = pb2.FollowUpRecommendation(
                    type=self._get_recommendation_type(rec.get('type', 'MONITORING')),
                    description=rec.get('description', ''),
                    rationale=rec.get('rationale', ''),
                    suggested_timeframe=int(rec.get('suggested_timeframe', 0))
                )
                response.recommendations.append(recommendation)
                
            logger.info(f"结束问诊会话: session_id={session_id}")
            
            return response
            
        except ValueError as e:
            # 会话不存在或已过期
            logger.error(f"结束问诊会话失败(会话无效): {str(e)}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"会话不存在或已过期: {str(e)}")
            return pb2.InquirySummary()
        except Exception as e:
            # 其他错误
            logger.error(f"结束问诊会话失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"结束问诊会话失败: {str(e)}")
            return pb2.InquirySummary()
            
    def _get_symptom_severity(self, severity_str: str) -> int:
        """将症状严重程度字符串转换为枚举值"""
        severity_types = {
            'MILD': pb2.SymptomInfo.MILD,
            'MODERATE': pb2.SymptomInfo.MODERATE,
            'SEVERE': pb2.SymptomInfo.SEVERE,
            'EXTREME': pb2.SymptomInfo.EXTREME
        }
        
        return severity_types.get(severity_str, pb2.SymptomInfo.MODERATE)
        
    def _get_constitution_type(self, type_str: str) -> int:
        """将体质类型字符串转换为枚举值"""
        constitution_types = {
            'BALANCED': pb2.HealthProfile.BALANCED,
            'QI_DEFICIENCY': pb2.HealthProfile.QI_DEFICIENCY,
            'YANG_DEFICIENCY': pb2.HealthProfile.YANG_DEFICIENCY,
            'YIN_DEFICIENCY': pb2.HealthProfile.YIN_DEFICIENCY,
            'PHLEGM_DAMPNESS': pb2.HealthProfile.PHLEGM_DAMPNESS,
            'DAMP_HEAT': pb2.HealthProfile.DAMP_HEAT,
            'BLOOD_STASIS': pb2.HealthProfile.BLOOD_STASIS,
            'QI_STAGNATION': pb2.HealthProfile.QI_STAGNATION,
            'SPECIAL_CONSTITUTION': pb2.HealthProfile.SPECIAL_CONSTITUTION
        }
        
        return constitution_types.get(type_str, pb2.HealthProfile.BALANCED)
        
    def _get_recommendation_type(self, type_str: str) -> int:
        """将建议类型字符串转换为枚举值"""
        recommendation_types = {
            'MEDICAL_EXAM': pb2.FollowUpRecommendation.MEDICAL_EXAM,
            'LIFESTYLE_CHANGE': pb2.FollowUpRecommendation.LIFESTYLE_CHANGE,
            'DIETARY_ADJUSTMENT': pb2.FollowUpRecommendation.DIETARY_ADJUSTMENT,
            'EXERCISE_PROGRAM': pb2.FollowUpRecommendation.EXERCISE_PROGRAM,
            'SPECIALIST_CONSULTATION': pb2.FollowUpRecommendation.SPECIALIST_CONSULTATION,
            'MONITORING': pb2.FollowUpRecommendation.MONITORING,
            'TCM_INTERVENTION': pb2.FollowUpRecommendation.TCM_INTERVENTION
        }
        
        return recommendation_types.get(type_str, pb2.FollowUpRecommendation.MONITORING)

    async def AnalyzeMedicalHistory(self, request, context):
        """
        分析用户病史
        
        Args:
            request: MedicalHistoryRequest
            context: gRPC上下文
            
        Returns:
            MedicalHistoryAnalysis
        """
        try:
            # 提取请求参数
            user_id = request.user_id
            medical_records = [MessageToDict(record) for record in request.medical_records]
            family_history = list(request.family_history)
            additional_info = dict(request.additional_info)
            
            # 这里应该实现病史分析逻辑
            # 为简化示例，返回一个基本的分析结果
            response = pb2.MedicalHistoryAnalysis()
            
            # 添加慢性病状况
            if medical_records:
                conditions = set()
                for record in medical_records:
                    condition = record.get('condition', '')
                    if condition and condition not in conditions:
                        conditions.add(condition)
                        chronic = pb2.ChronicCondition(
                            condition_name=condition,
                            severity=pb2.ChronicCondition.MODERATE,
                            current_status="持续存在" if "慢性" in condition else "已治愈"
                        )
                        response.chronic_conditions.append(chronic)
                        
            # 添加风险因素
            risk_factors = [
                ("肥胖", 0.7, "体重过高增加多种疾病风险", ["控制饮食", "规律运动", "定期体检"]),
                ("高血压家族史", 0.65, "家族中有高血压病史，增加发病风险", ["低盐饮食", "规律运动", "定期监测血压"]),
                ("久坐生活方式", 0.8, "长时间久坐增加心血管疾病风险", ["每小时起身活动", "规律运动", "站立办公"])
            ]
            
            for name, score, desc, suggestions in risk_factors:
                risk = pb2.RiskFactor(
                    factor_name=name,
                    risk_score=score,
                    description=desc
                )
                risk.prevention_suggestions.extend(suggestions)
                response.risk_factors.append(risk)
                
            # 添加历史证型
            historical_patterns = [
                pb2.TCMPattern(
                    pattern_name="气虚证",
                    category="虚证",
                    match_score=0.75,
                    description="气虚证是指人体内气的不足所导致的一系列症状"
                ),
                pb2.TCMPattern(
                    pattern_name="痰湿证",
                    category="实证",
                    match_score=0.65,
                    description="痰湿证是指体内水液代谢异常，聚湿成痰所导致的一系列症状"
                )
            ]
            historical_patterns[0].related_symptoms.extend(["疲劳", "气短", "自汗"])
            historical_patterns[1].related_symptoms.extend(["痰多", "胸闷", "肢体沉重"])
            
            response.historical_patterns.extend(historical_patterns)
            
            # 添加生活方式影响
            lifestyle = pb2.LifestyleImpact(
                overall_impact_score=0.7
            )
            lifestyle.dietary_factors.extend(["高糖饮食", "油腻食物", "不规律进餐"])
            lifestyle.exercise_factors.extend(["缺乏运动", "久坐"])
            lifestyle.sleep_factors.extend(["睡眠不足", "睡眠质量差"])
            lifestyle.mental_factors.extend(["工作压力大", "焦虑"])
            
            response.lifestyle_impact.CopyFrom(lifestyle)
            
            logger.info(f"分析病史: user_id={user_id}, records_count={len(medical_records)}")
            
            return response
            
        except Exception as e:
            logger.error(f"分析病史失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"分析病史失败: {str(e)}")
            return pb2.MedicalHistoryAnalysis()

    async def ExtractSymptoms(self, request, context):
        """
        提取症状信息
        
        Args:
            request: SymptomsExtractionRequest
            context: gRPC上下文
            
        Returns:
            SymptomsResponse
        """
        try:
            # 提取请求参数
            text_content = request.text_content
            user_id = request.user_id
            language = request.language
            
            # 调用症状提取器
            extraction_result = await self.symptom_extractor.extract_symptoms(text_content)
            
            # 构建响应
            response = pb2.SymptomsResponse(
                confidence_score=extraction_result.get('confidence_score', 0.0)
            )
            
            # 添加症状
            symptoms = extraction_result.get('symptoms', [])
            for symptom in symptoms:
                symptom_info = pb2.SymptomInfo(
                    symptom_name=symptom.get('symptom_name', ''),
                    severity=self._get_symptom_severity(symptom.get('severity', 'MODERATE')),
                    onset_time=int(symptom.get('onset_time', 0)),
                    duration=int(symptom.get('duration', 0)),
                    description=symptom.get('description', ''),
                    confidence=float(symptom.get('confidence', 0.8))
                )
                response.symptoms.append(symptom_info)
                
            # 添加身体部位
            body_locations = extraction_result.get('body_locations', [])
            for location in body_locations:
                body_location = pb2.BodyLocation(
                    location_name=location.get('location_name', ''),
                    side=location.get('side', 'central')
                )
                body_location.associated_symptoms.extend(location.get('associated_symptoms', []))
                response.body_locations.append(body_location)
                
            # 添加时间因素
            temporal_factors = extraction_result.get('temporal_factors', [])
            for factor in temporal_factors:
                temporal_factor = pb2.TemporalFactor(
                    factor_type=factor.get('factor_type', ''),
                    description=factor.get('description', '')
                )
                temporal_factor.symptoms_affected.extend(factor.get('symptoms_affected', []))
                response.temporal_factors.append(temporal_factor)
                
            logger.info(f"提取症状: user_id={user_id}, symptoms_count={len(symptoms)}")
            
            return response
            
        except Exception as e:
            logger.error(f"提取症状失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"提取症状失败: {str(e)}")
            return pb2.SymptomsResponse()

    async def MapToTCMPatterns(self, request, context):
        """
        中医症状匹配
        
        Args:
            request: TCMPatternMappingRequest
            context: gRPC上下文
            
        Returns:
            TCMPatternResponse
        """
        try:
            # 提取请求参数
            symptoms = [MessageToDict(symptom) for symptom in request.symptoms]
            user_constitution = request.user_constitution
            body_locations = [MessageToDict(location) for location in request.body_locations]
            temporal_factors = [MessageToDict(factor) for factor in request.temporal_factors]
            
            # 调用TCM映射器
            mapping_result = await self.tcm_pattern_mapper.map_to_tcm_patterns(
                symptoms=symptoms,
                user_constitution=user_constitution,
                body_locations=body_locations,
                temporal_factors=temporal_factors
            )
            
            # 构建响应
            response = pb2.TCMPatternResponse(
                interpretation=mapping_result.get('interpretation', ''),
                confidence_score=mapping_result.get('confidence_score', 0.0)
            )
            
            # 添加主证
            primary_patterns = mapping_result.get('primary_patterns', [])
            for pattern in primary_patterns:
                tcm_pattern = pb2.TCMPattern(
                    pattern_name=pattern.get('pattern_name', ''),
                    category=pattern.get('category', ''),
                    match_score=float(pattern.get('match_score', 0.0)),
                    description=pattern.get('description', '')
                )
                tcm_pattern.related_symptoms.extend(pattern.get('related_symptoms', []))
                response.primary_patterns.append(tcm_pattern)
                
            # 添加次证
            secondary_patterns = mapping_result.get('secondary_patterns', [])
            for pattern in secondary_patterns:
                tcm_pattern = pb2.TCMPattern(
                    pattern_name=pattern.get('pattern_name', ''),
                    category=pattern.get('category', ''),
                    match_score=float(pattern.get('match_score', 0.0)),
                    description=pattern.get('description', '')
                )
                tcm_pattern.related_symptoms.extend(pattern.get('related_symptoms', []))
                response.secondary_patterns.append(tcm_pattern)
                
            logger.info(f"中医证型匹配: primary_patterns_count={len(primary_patterns)}, secondary_patterns_count={len(secondary_patterns)}")
            
            return response
            
        except Exception as e:
            logger.error(f"中医证型匹配失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"中医证型匹配失败: {str(e)}")
            return pb2.TCMPatternResponse()

    async def BatchAnalyzeInquiryData(self, request, context):
        """
        批量分析健康数据
        
        Args:
            request: BatchInquiryRequest
            context: gRPC上下文
            
        Returns:
            BatchInquiryResponse
        """
        try:
            # 提取请求参数
            session_ids = list(request.session_ids)
            analysis_type = request.analysis_type
            analysis_parameters = dict(request.analysis_parameters)
            
            # 实现批量分析逻辑
            # 此处为简化示例，实际应实现完整的批量分析逻辑
            response = pb2.BatchInquiryResponse()
            
            # 添加聚合指标
            response.aggregated_metrics['symptom_frequency'] = 0.65
            response.aggregated_metrics['pattern_consistency'] = 0.78
            response.aggregated_metrics['recommendation_relevance'] = 0.82
            
            # 添加分析洞察
            insights = [
                pb2.AnalysisInsight(
                    insight_type="symptom_pattern",
                    description="症状'疲劳'在多次问诊中持续出现，与'气虚证'高度相关",
                    confidence=0.85
                ),
                pb2.AnalysisInsight(
                    insight_type="lifestyle_impact",
                    description="工作压力与'失眠'、'焦虑'症状呈现显著相关性",
                    confidence=0.78
                ),
                pb2.AnalysisInsight(
                    insight_type="treatment_effectiveness",
                    description="调整饮食结构后，'腹胀'症状明显改善",
                    confidence=0.72
                )
            ]
            
            for insight in insights:
                insight.supporting_evidence.extend([
                    "多次问诊记录分析",
                    "症状频率统计",
                    "时间序列对比"
                ])
                response.insights.append(insight)
                
            logger.info(f"批量分析健康数据: session_count={len(session_ids)}, analysis_type={analysis_type}")
            
            return response
            
        except Exception as e:
            logger.error(f"批量分析健康数据失败: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"批量分析健康数据失败: {str(e)}")
            return pb2.BatchInquiryResponse()

    async def AssessHealthRisks(self, request, context):
        """
        健康风险评估
        
        Args:
            request: HealthRiskRequest
            context: gRPC上下文
            
        Returns:
            HealthRiskResponse
        """
        try:
            # 提取请求参数
            user_id = request.user_id
            current_symptoms = [MessageToDict(symptom) for symptom in request.current_symptoms]
            medical_history = MessageToDict(request.medical_history)
            health_profile = MessageToDict(request.health_profile)
            
            # 调用健康风险评估器
            assessment_result = await self.health_risk_assessor.assess_health_risks(
                user_id=user_id,
                current_symptoms=current_symptoms,
                medical_history=medical_history,
                health_profile=health_profile
            )
            
            # 构建响应
            response = pb2.HealthRiskResponse(
                overall_risk_score=assessment_result.get('overall_risk_score', 0.0)
            )
            
            # 添加即时风险
            immediate_risks = assessment_result.get('immediate_risks', [])
            for risk in immediate_risks:
                health_risk = pb2.HealthRisk(
                    risk_name=risk.get('risk_name', ''),
                    probability=float(risk.get('probability', 0.0)),
                    severity=risk.get('severity', 'low'),
                    timeframe=risk.get('timeframe', 'unknown')
                )
                health_risk.contributing_factors.extend(risk.get('contributing_factors', []))
                response.immediate_risks.append(health_risk)
                
            # 添加长期风险
            long_term_risks = assessment_result.get('long_term_risks', [])
            for risk in long_term_risks:
                health_risk = pb2.HealthRisk(
                    risk_name=risk.get('risk_name', ''),
                    probability=float(risk.get('probability', 0.0)),
                    severity=risk.get('severity', 'low'),
                    timeframe=risk.get('timeframe', 'unknown')
                )
                health_risk.contributing_factors.extend(risk.get('contributing_factors', []))
                response.long_term_risks.append(health_risk)
                
            # 添加预防策略
            prevention_strategies = assessment_result.get('prevention_strategies', [])
            for strategy in prevention_strategies:
                prevention_strategy = pb2.PreventionStrategy(
                    strategy_name=strategy.get('strategy_name', ''),
                    description=strategy.get('description', ''),
                    effectiveness_score=float(strategy.get('effectiveness_score', 0.0))
                )
                prevention_strategy.action_items.extend(strategy.get('action_items', []))
                prevention_strategy.targets.extend(strategy.get('targets', []))
                response.prevention_strategies.append(prevention_strategy)
                
            logger.info(f"健康风险评估完成: user_id={user_id}, "
                       f"即时风险={len(immediate_risks)}, "
                       f"长期风险={len(long_term_risks)}, "
                       f"预防策略={len(prevention_strategies)}")
            
            return response
            
        except Exception as e:
            logger.error(f"健康风险评估失败: {str(e)}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"健康风险评估失败: {str(e)}")
            return pb2.HealthRiskResponse() 