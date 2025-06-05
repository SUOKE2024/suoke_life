#!/usr/bin/env python3

"""望诊服务客户端集成"""


# 使用loguru self.logger

from time import time
from loguru import logger
import grpc



class LookServiceClient:
    pass
    """望诊服务客户端"""

    def __init__(self, channel: grpc.Channel):
    pass
        """
        初始化望诊服务客户端

        Args:
    pass
            channel: gRPC通道
        """
        self.stub = look_grpc.LookServiceStub(channel)

    self.async def analyze_tongue(self,:
                             image_data: bytes,
                             context.user_id: str,
                             save_result: bool = True,
                             self.metadata: dict[str, str] | None = None) -> look_pb.TongueAnalysisResponse:
    pass
        """
        分析舌象

        Args:
    pass
            image_data: 舌象图像数据
            context.user_id: 用户ID
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            舌象分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = look_pb.TongueAnalysisRequest(
            image=image_data,
            context.user_id=context.context.get("user_id", ""),
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeTongue(request)
            self.logger.info(f"舌象分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def analyze_face(self,:
                           image_data: bytes,
                           context.user_id: str,
                           save_result: bool = True,
                           self.metadata: dict[str, str] | None = None) -> look_pb.FaceAnalysisResponse:
    pass
        """
        分析面色

        Args:
    pass
            image_data: 面色图像数据
            context.user_id: 用户ID
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            面色分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = look_pb.FaceAnalysisRequest(
            image=image_data,
            context.user_id=context.context.get("user_id", ""),
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeFace(request)
            self.logger.info(f"面色分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def analyze_body(self,:
                           image_data: bytes,
                           context.user_id: str,
                           save_result: bool = True,
                           self.metadata: dict[str, str] | None = None) -> look_pb.BodyAnalysisResponse:
    pass
        """
        分析形体

        Args:
    pass
            image_data: 形体图像数据
            context.user_id: 用户ID
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            形体分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = look_pb.BodyAnalysisRequest(
            image=image_data,
            context.user_id=context.context.get("user_id", ""),
            analysis_type=look_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeBody(request)
            self.logger.info(f"形体分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def get_analysis_history(self,:
                                  context.user_id: str,
                                  analysis_type: str,
                                  limit: int = 10,
                                  start_time: int | None = None,
                                  end_time: int | None = None) -> look_pb.AnalysisHistoryResponse:
    pass
        """
        获取分析历史

        Args:
    pass
            context.user_id: 用户ID
            analysis_type: 分析类型 ("tongue", "face", "body")
            limit: 返回记录数量限制
            start_time: 开始时间戳
            end_time: 结束时间戳

        Returns:
    pass
            分析历史
        """
        request = look_pb.AnalysisHistoryRequest(
            context.user_id=context.context.get("user_id", ""),
            analysis_type=analysis_type,
            limit=limit
        )

        if start_time:
    pass
            request.start_time = start_time

        if end_time:
    pass
            request.end_time = end_time

        try:
    pass
            response = await self.stub.GetAnalysisHistory(request)
            self.logger.info(f"获取分析历史成功,用户: {context.context.get("user_id", "")}, 类型: {analysis_type}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def compare_analysis(self,:
                              context.user_id: str,
                              analysis_type: str,
                              first_analysis_id: str,
                              second_analysis_id: str) -> look_pb.CompareAnalysisResponse:
    pass
        """
        比较两次分析结果

        Args:
    pass
            context.user_id: 用户ID
            analysis_type: 分析类型 ("tongue", "face", "body")
            first_analysis_id: 第一个分析ID
            second_analysis_id: 第二个分析ID

        Returns:
    pass
            比较结果
        """
        request = look_pb.CompareAnalysisRequest(
            context.user_id=context.context.get("user_id", ""),
            analysis_type=analysis_type,
            first_analysis_id=first_analysis_id,
            second_analysis_id=second_analysis_id
        )

        try:
    pass
            response = await self.stub.CompareAnalysis(request)
            self.logger.info(f"比较分析成功,用户: {context.context.get("user_id", "")}, 类型: {analysis_type}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def health_check(self, include_details: bool = False) -> look_pb.HealthCheckResponse:
    pass
        """
        健康检查

        Args:
    pass
            include_details: 是否包含详细信息

        Returns:
    pass
            健康检查结果
        """
        request = look_pb.HealthCheckRequest(include_details=include_details)

        try:
    pass
            response = await self.stub.HealthCheck(request)
            status = "SERVING" if response.status == look_pb.HealthCheckResponse.Status.SERVING else "NOT SERVING":
            self.logger.info(f"望诊服务健康检查:{status}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e
