#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""问诊服务客户端集成"""

import logging
from typing import Dict, Optional, List, Tuple

import grpc
from google.protobuf.any_pb2 import Any

# 假设已经生成了对应的proto Python文件
from xiaoai_service.protos import inquiry_service_pb2 as inquiry_pb
from xiaoai_service.protos import inquiry_service_pb2_grpc as inquiry_grpc

logger = logging.getLogger(__name__)


class InquiryServiceClient:
    """问诊服务客户端"""

    def __init__(self, channel: grpc.Channel):
        """
        初始化问诊服务客户端
        
        Args:
            channel: gRPC通道
        """
        self.stub = inquiry_grpc.InquiryServiceStub(channel)
        
    async def analyze_conversation(self, 
                                  conversation_data: str, 
                                  user_id: str,
                                  save_result: bool = True,
                                  metadata: Optional[Dict[str, str]] = None) -> inquiry_pb.ConversationAnalysisResponse:
        """
        分析问诊对话
        
        Args:
            conversation_data: 对话数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            对话分析结果
        """
        if not metadata:
            metadata = {}
        
        request = inquiry_pb.ConversationAnalysisRequest(
            conversation=conversation_data,
            user_id=user_id,
            analysis_type=inquiry_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeConversation(request)
            logger.info(f"对话分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"对话分析失败: {e}")
            raise RuntimeError(f"对话分析失败: {e}")
            
    async def analyze_symptoms(self, 
                              symptoms: List[str], 
                              user_id: str,
                              save_result: bool = True,
                              metadata: Optional[Dict[str, str]] = None) -> inquiry_pb.SymptomAnalysisResponse:
        """
        分析症状
        
        Args:
            symptoms: 症状列表
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            症状分析结果
        """
        if not metadata:
            metadata = {}
        
        request = inquiry_pb.SymptomAnalysisRequest(
            symptoms=symptoms,
            user_id=user_id,
            analysis_type=inquiry_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeSymptoms(request)
            logger.info(f"症状分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"症状分析失败: {e}")
            raise RuntimeError(f"症状分析失败: {e}")
            
    async def analyze_medical_history(self, 
                                     medical_history: Dict[str, Any], 
                                     user_id: str,
                                     save_result: bool = True,
                                     metadata: Optional[Dict[str, str]] = None) -> inquiry_pb.MedicalHistoryAnalysisResponse:
        """
        分析病史
        
        Args:
            medical_history: 病史数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            病史分析结果
        """
        if not metadata:
            metadata = {}
        
        # 将病史数据转换为protobuf格式
        history_pb = inquiry_pb.MedicalHistoryData()
        
        # 这里需要根据实际的protobuf定义进行转换
        # 示例：
        if 'chronic_diseases' in medical_history:
            for disease in medical_history['chronic_diseases']:
                history_pb.chronic_diseases.append(disease)
        
        if 'allergies' in medical_history:
            for allergy in medical_history['allergies']:
                history_pb.allergies.append(allergy)
        
        if 'family_history' in medical_history:
            for condition in medical_history['family_history']:
                history_pb.family_history.append(condition)
        
        # 创建请求
        request = inquiry_pb.MedicalHistoryAnalysisRequest(
            medical_history=history_pb,
            user_id=user_id,
            analysis_type=inquiry_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeMedicalHistory(request)
            logger.info(f"病史分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"病史分析失败: {e}")
            raise RuntimeError(f"病史分析失败: {e}")
    
    async def generate_inquiry_questions(self, 
                                        user_id: str,
                                        initial_symptoms: Optional[List[str]] = None,
                                        previous_answers: Optional[Dict[str, str]] = None,
                                        max_questions: int = 10,
                                        metadata: Optional[Dict[str, str]] = None) -> inquiry_pb.InquiryQuestionsResponse:
        """
        生成问诊问题
        
        Args:
            user_id: 用户ID
            initial_symptoms: 初始症状列表
            previous_answers: 之前的回答
            max_questions: 最大问题数量
            metadata: 元数据
            
        Returns:
            问诊问题
        """
        if not metadata:
            metadata = {}
        
        request = inquiry_pb.InquiryQuestionsRequest(
            user_id=user_id,
            max_questions=max_questions,
            metadata=metadata
        )
        
        if initial_symptoms:
            request.initial_symptoms.extend(initial_symptoms)
        
        if previous_answers:
            for question, answer in previous_answers.items():
                qa_pair = inquiry_pb.QuestionAnswerPair(
                    question=question,
                    answer=answer
                )
                request.previous_answers.append(qa_pair)
        
        try:
            response = await self.stub.GenerateInquiryQuestions(request)
            logger.info(f"生成问诊问题成功，用户: {user_id}")
            return response
        except Exception as e:
            logger.error(f"生成问诊问题失败: {e}")
            raise RuntimeError(f"生成问诊问题失败: {e}")
    
    async def get_analysis_history(self, 
                                  user_id: str, 
                                  analysis_type: str,
                                  limit: int = 10,
                                  start_time: Optional[int] = None,
                                  end_time: Optional[int] = None) -> inquiry_pb.AnalysisHistoryResponse:
        """
        获取分析历史
        
        Args:
            user_id: 用户ID
            analysis_type: 分析类型 ("conversation", "symptom", "medical_history")
            limit: 返回记录数量限制
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            分析历史
        """
        request = inquiry_pb.AnalysisHistoryRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            limit=limit
        )
        
        if start_time:
            request.start_time = start_time
        
        if end_time:
            request.end_time = end_time
        
        try:
            response = await self.stub.GetAnalysisHistory(request)
            logger.info(f"获取分析历史成功，用户: {user_id}, 类型: {analysis_type}")
            return response
        except Exception as e:
            logger.error(f"获取分析历史失败: {e}")
            raise RuntimeError(f"获取分析历史失败: {e}")
            
    async def health_check(self, include_details: bool = False) -> inquiry_pb.HealthCheckResponse:
        """
        健康检查
        
        Args:
            include_details: 是否包含详细信息
            
        Returns:
            健康检查结果
        """
        request = inquiry_pb.HealthCheckRequest(include_details=include_details)
        
        try:
            response = await self.stub.HealthCheck(request)
            status = "SERVING" if response.status == inquiry_pb.HealthCheckResponse.Status.SERVING else "NOT SERVING"
            logger.info(f"问诊服务健康检查：{status}")
            return response
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            raise RuntimeError(f"健康检查失败: {e}") 