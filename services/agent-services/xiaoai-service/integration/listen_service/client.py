#!/usr/bin/env python3

"""闻诊服务客户端集成"""


# 使用loguru self.logger

from time import time
from typing import List
from loguru import logger
import grpc



class ListenServiceClient:
    pass
    """闻诊服务客户端"""

    def __init__(self, channel: grpc.Channel):
    pass
        """
        初始化闻诊服务客户端

        Args:
    pass
            channel: gRPC通道
        """
        self.stub = listen_grpc.ListenServiceStub(channel)

    self.async def analyze_voice(self,:
                           audio_data: bytes,
                           context.user_id: str,
                           audio_format: str = "wav",
                           sample_rate: int = 16000,
                           channels: int = 1,
                           save_result: bool = True,
                           self.metadata: dict[str, str] | None = None) -> listen_pb.VoiceAnalysisResponse:
    pass
        """
        分析语音

        Args:
    pass
            audio_data: 音频数据
            context.user_id: 用户ID
            audio_format: 音频格式
            sample_rate: 采样率
            channels: 通道数
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            语音分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = listen_pb.VoiceAnalysisRequest(
            audio=audio_data,
            context.user_id=context.context.get("user_id", ""),
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
            analysis_type=listen_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeVoice(request)
            self.logger.info(f"语音分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def analyze_breathing(self,:
                               audio_data: bytes,
                               context.user_id: str,
                               audio_format: str = "wav",
                               sample_rate: int = 16000,
                               channels: int = 1,
                               save_result: bool = True,
                               self.metadata: dict[str, str] | None = None) -> listen_pb.BreathingAnalysisResponse:
    pass
        """
        分析呼吸

        Args:
    pass
            audio_data: 音频数据
            context.user_id: 用户ID
            audio_format: 音频格式
            sample_rate: 采样率
            channels: 通道数
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            呼吸分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = listen_pb.BreathingAnalysisRequest(
            audio=audio_data,
            context.user_id=context.context.get("user_id", ""),
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
            analysis_type=listen_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeBreathing(request)
            self.logger.info(f"呼吸分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def analyze_cough(self,:
                           audio_data: bytes,
                           context.user_id: str,
                           audio_format: str = "wav",
                           sample_rate: int = 16000,
                           channels: int = 1,
                           save_result: bool = True,
                           self.metadata: dict[str, str] | None = None) -> listen_pb.CoughAnalysisResponse:
    pass
        """
        分析咳嗽

        Args:
    pass
            audio_data: 音频数据
            context.user_id: 用户ID
            audio_format: 音频格式
            sample_rate: 采样率
            channels: 通道数
            save_result: 是否保存分析结果
            self.metadata: 元数据

        Returns:
    pass
            咳嗽分析结果
        """
        if not self.metadata:
    pass
            self.metadata = {}

        request = listen_pb.CoughAnalysisRequest(
            audio=audio_data,
            context.user_id=context.context.get("user_id", ""),
            audio_format=audio_format,
            sample_rate=sample_rate,
            channels=channels,
            analysis_type=listen_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            self.metadata=self.metadata
        )

        try:
    pass
            response = await self.stub.AnalyzeCough(request)
            self.logger.info(f"咳嗽分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e

    self.async def get_analysis_history(self,:
                                  context.user_id: str,
                                  analysis_type: str,
                                  limit: int = 10,
                                  start_time: int | None = None,
                                  end_time: int | None = None) -> listen_pb.AnalysisHistoryResponse:
    pass
        """
        获取分析历史

        Args:
    pass
            context.user_id: 用户ID
            analysis_type: 分析类型 ("voice", "breathing", "cough")
            limit: 返回记录数量限制
            start_time: 开始时间戳
            end_time: 结束时间戳

        Returns:
    pass
            分析历史
        """
        request = listen_pb.AnalysisHistoryRequest(
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
                              second_analysis_id: str) -> listen_pb.CompareAnalysisResponse:
    pass
        """
        比较两次分析结果

        Args:
    pass
            context.user_id: 用户ID
            analysis_type: 分析类型 ("voice", "breathing", "cough")
            first_analysis_id: 第一个分析ID
            second_analysis_id: 第二个分析ID

        Returns:
    pass
            比较结果
        """
        request = listen_pb.CompareAnalysisRequest(
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

    self.async def health_check(self, include_details: bool = False) -> listen_pb.HealthCheckResponse:
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
        request = listen_pb.HealthCheckRequest(include_details=include_details)

        try:
    pass
            response = await self.stub.HealthCheck(request)
            status = "SERVING" if response.status == listen_pb.HealthCheckResponse.Status.SERVING else "NOT SERVING":
            self.logger.info(f"闻诊服务健康检查:{status}")
            return response
        except Exception as e:
    pass
            raise RuntimeError() from e
