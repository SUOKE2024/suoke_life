#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""望诊服务客户端集成"""

import logging
from typing import Dict, Optional, List, Tuple

import grpc
from google.protobuf.any_pb2 import Any

# 假设已经生成了对应的proto Python文件
from xiaoai_service.protos import look_service_pb2 as look_pb
from xiaoai_service.protos import look_service_pb2_grpc as look_grpc

logger = logging.getLogger(__name__)


class LookServiceClient:
    """望诊服务客户端"""

    def __init__(self, channel: grpc.Channel):
        """
        初始化望诊服务客户端
        
        Args:
            channel: gRPC通道
        """
        self.stub = look_grpc.LookServiceStub(channel)
        
    async def analyze_tongue(self, 
                             image_data: bytes, 
                             user_id: str, 
                             save_result: bool = True,
                             metadata: Optional[Dict[str, str]] = None) -> look_pb.TongueAnalysisResponse:
        """
        分析舌象
        
        Args:
            image_data: 舌象图像数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            舌象分析结果
        """
        if not metadata:
            metadata = {}
        
        request = look_pb.TongueAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeTongue(request)
            logger.info(f"舌象分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"舌象分析失败: {e}")
            raise RuntimeError(f"舌象分析失败: {e}")
            
    async def analyze_face(self, 
                           image_data: bytes, 
                           user_id: str, 
                           save_result: bool = True,
                           metadata: Optional[Dict[str, str]] = None) -> look_pb.FaceAnalysisResponse:
        """
        分析面色
        
        Args:
            image_data: 面色图像数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            面色分析结果
        """
        if not metadata:
            metadata = {}
        
        request = look_pb.FaceAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeFace(request)
            logger.info(f"面色分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"面色分析失败: {e}")
            raise RuntimeError(f"面色分析失败: {e}")
            
    async def analyze_body(self, 
                           image_data: bytes, 
                           user_id: str, 
                           save_result: bool = True,
                           metadata: Optional[Dict[str, str]] = None) -> look_pb.BodyAnalysisResponse:
        """
        分析形体
        
        Args:
            image_data: 形体图像数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据
            
        Returns:
            形体分析结果
        """
        if not metadata:
            metadata = {}
        
        request = look_pb.BodyAnalysisRequest(
            image=image_data,
            user_id=user_id,
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )
        
        try:
            response = await self.stub.AnalyzeBody(request)
            logger.info(f"形体分析成功，ID: {response.analysis_id}")
            return response
        except Exception as e:
            logger.error(f"形体分析失败: {e}")
            raise RuntimeError(f"形体分析失败: {e}")
            
    async def get_analysis_history(self, 
                                  user_id: str, 
                                  analysis_type: str,
                                  limit: int = 10,
                                  start_time: Optional[int] = None,
                                  end_time: Optional[int] = None) -> look_pb.AnalysisHistoryResponse:
        """
        获取分析历史
        
        Args:
            user_id: 用户ID
            analysis_type: 分析类型 ("tongue", "face", "body")
            limit: 返回记录数量限制
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        Returns:
            分析历史
        """
        request = look_pb.AnalysisHistoryRequest(
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
            
    async def compare_analysis(self,
                              user_id: str,
                              analysis_type: str,
                              first_analysis_id: str,
                              second_analysis_id: str) -> look_pb.CompareAnalysisResponse:
        """
        比较两次分析结果
        
        Args:
            user_id: 用户ID
            analysis_type: 分析类型 ("tongue", "face", "body")
            first_analysis_id: 第一个分析ID
            second_analysis_id: 第二个分析ID
            
        Returns:
            比较结果
        """
        request = look_pb.CompareAnalysisRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            first_analysis_id=first_analysis_id,
            second_analysis_id=second_analysis_id
        )
        
        try:
            response = await self.stub.CompareAnalysis(request)
            logger.info(f"比较分析成功，用户: {user_id}, 类型: {analysis_type}")
            return response
        except Exception as e:
            logger.error(f"比较分析失败: {e}")
            raise RuntimeError(f"比较分析失败: {e}")
            
    async def health_check(self, include_details: bool = False) -> look_pb.HealthCheckResponse:
        """
        健康检查
        
        Args:
            include_details: 是否包含详细信息
            
        Returns:
            健康检查结果
        """
        request = look_pb.HealthCheckRequest(include_details=include_details)
        
        try:
            response = await self.stub.HealthCheck(request)
            status = "SERVING" if response.status == look_pb.HealthCheckResponse.Status.SERVING else "NOT SERVING"
            logger.info(f"望诊服务健康检查：{status}")
            return response
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            raise RuntimeError(f"健康检查失败: {e}") 