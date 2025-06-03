#!/usr/bin/env python3

"""切诊服务客户端集成"""

import grpc
from google.protobuf.any_pb2 import Any

# 使用loguru logger

class PalpationServiceClient:
    """切诊服务客户端"""

    def __init__(self, channel: grpc.Channel):
        """
        初始化切诊服务客户端

        Args:
            channel: gRPC通道
        """
        self.stub = palpation_grpc.PalpationServiceStub(channel)

    async def analyze_pulse(self,
                           pulse_data: bytes,
                           user_id: str,
                           data_format: str = "raw",
                           sampling_rate: int = 1000,
                           save_result: bool = True,
                           metadata: dict[str, str] | None = None) -> palpation_pb.PulseAnalysisResponse:
        """
        分析脉象

        Args:
            pulse_data: 脉象数据
            user_id: 用户ID
            data_format: 数据格式
            sampling_rate: 采样率
            save_result: 是否保存分析结果
            metadata: 元数据

        Returns:
            脉象分析结果
        """
        if not metadata:
            metadata = {}

        request = palpation_pb.PulseAnalysisRequest(
            pulse_data=pulse_data,
            user_id=user_id,
            data_format=data_format,
            sampling_rate=sampling_rate,
            analysis_type=palpation_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )

        try:
            response = await self.stub.AnalyzePulse(request)
            logger.info(f"脉象分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def analyze_abdominal_palpation(self,
                                        pressure_map: bytes,
                                        user_id: str,
                                        data_format: str = "raw",
                                        resolution: tuple[int, int] = (128, 128),
                                        save_result: bool = True,
                                        metadata: dict[str, str] | None = None) -> palpation_pb.AbdominalAnalysisResponse:
        """
        分析腹诊

        Args:
            pressure_map: 腹部压力图数据
            user_id: 用户ID
            data_format: 数据格式
            resolution: 压力图分辨率
            save_result: 是否保存分析结果
            metadata: 元数据

        Returns:
            腹诊分析结果
        """
        if not metadata:
            metadata = {}

        request = palpation_pb.AbdominalAnalysisRequest(
            pressure_map=pressure_map,
            user_id=user_id,
            data_format=data_format,
            width=resolution[0],
            height=resolution[1],
            analysis_type=palpation_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )

        try:
            response = await self.stub.AnalyzeAbdominalPalpation(request)
            logger.info(f"腹诊分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def analyze_skin_touch(self,
                               touch_data: dict[str, Any],
                               user_id: str,
                               save_result: bool = True,
                               metadata: dict[str, str] | None = None) -> palpation_pb.SkinTouchAnalysisResponse:
        """
        分析皮肤触感

        Args:
            touch_data: 触感数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据

        Returns:
            皮肤触感分析结果
        """
        if not metadata:
            metadata = {}

        # 将触感数据转换为protobuf格式
        touch_pb = palpation_pb.SkinTouchData()

        # 这里需要根据实际的protobuf定义进行转换
        # 示例:
        if 'temperature' in touch_data:
            touch_pb.temperature = touch_data['temperature']

        if 'moisture' in touch_data:
            touch_pb.moisture = touch_data['moisture']

        if 'elasticity' in touch_data:
            touch_pb.elasticity = touch_data['elasticity']

        if 'regions' in touch_data:
            for region_name, region_data in touch_data['regions'].items():
                region = palpation_pb.SkinRegion(
                    region_name=region_name
                )

                if 'temperature' in region_data:
                    region.temperature = region_data['temperature']

                if 'moisture' in region_data:
                    region.moisture = region_data['moisture']

                if 'elasticity' in region_data:
                    region.elasticity = region_data['elasticity']

                touch_pb.regions.append(region)

        request = palpation_pb.SkinTouchAnalysisRequest(
            touch_data=touch_pb,
            user_id=user_id,
            analysis_type=palpation_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )

        try:
            response = await self.stub.AnalyzeSkinTouch(request)
            logger.info(f"皮肤触感分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def analyze_acupoint(self,
                              acupoint_data: dict[str, Any],
                              user_id: str,
                              save_result: bool = True,
                              metadata: dict[str, str] | None = None) -> palpation_pb.AcupointAnalysisResponse:
        """
        分析穴位反应

        Args:
            acupoint_data: 穴位反应数据
            user_id: 用户ID
            save_result: 是否保存分析结果
            metadata: 元数据

        Returns:
            穴位反应分析结果
        """
        if not metadata:
            metadata = {}

        # 将穴位数据转换为protobuf格式
        acupoint_pb = palpation_pb.AcupointData()

        # 这里需要根据实际的protobuf定义进行转换
        # 示例:
        if 'points' in acupoint_data:
            for point_name, point_data in acupoint_data['points'].items():
                point = palpation_pb.Acupoint(
                    point_name=point_name
                )

                if 'sensitivity' in point_data:
                    point.sensitivity = point_data['sensitivity']

                if 'temperature' in point_data:
                    point.temperature = point_data['temperature']

                if 'meridian' in point_data:
                    point.meridian = point_data['meridian']

                acupoint_pb.points.append(point)

        request = palpation_pb.AcupointAnalysisRequest(
            acupoint_data=acupoint_pb,
            user_id=user_id,
            analysis_type=palpation_pb.AnalysisType.COMPREHENSIVE,
            save_result=save_result,
            metadata=metadata
        )

        try:
            response = await self.stub.AnalyzeAcupoint(request)
            logger.info(f"穴位反应分析成功,ID: {response.analysis_id}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def get_analysis_history(self,
                                  user_id: str,
                                  analysis_type: str,
                                  limit: int = 10,
                                  start_time: int | None = None,
                                  end_time: int | None = None) -> palpation_pb.AnalysisHistoryResponse:
        """
        获取分析历史

        Args:
            user_id: 用户ID
            analysis_type: 分析类型 ("pulse", "abdominal", "skin_touch", "acupoint")
            limit: 返回记录数量限制
            start_time: 开始时间戳
            end_time: 结束时间戳

        Returns:
            分析历史
        """
        request = palpation_pb.AnalysisHistoryRequest(
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
            logger.info(f"获取分析历史成功,用户: {user_id}, 类型: {analysis_type}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def compare_analysis(self,
                              user_id: str,
                              analysis_type: str,
                              first_analysis_id: str,
                              second_analysis_id: str) -> palpation_pb.CompareAnalysisResponse:
        """
        比较两次分析结果

        Args:
            user_id: 用户ID
            analysis_type: 分析类型 ("pulse", "abdominal", "skin_touch", "acupoint")
            first_analysis_id: 第一个分析ID
            second_analysis_id: 第二个分析ID

        Returns:
            比较结果
        """
        request = palpation_pb.CompareAnalysisRequest(
            user_id=user_id,
            analysis_type=analysis_type,
            first_analysis_id=first_analysis_id,
            second_analysis_id=second_analysis_id
        )

        try:
            response = await self.stub.CompareAnalysis(request)
            logger.info(f"比较分析成功,用户: {user_id}, 类型: {analysis_type}")
            return response
        except Exception as e:
            raise RuntimeError() from e

    async def health_check(self, include_details: bool = False) -> palpation_pb.HealthCheckResponse:
        """
        健康检查

        Args:
            include_details: 是否包含详细信息

        Returns:
            健康检查结果
        """
        request = palpation_pb.HealthCheckRequest(include_details=include_details)

        try:
            response = await self.stub.HealthCheck(request)
            status = "SERVING" if response.status == palpation_pb.HealthCheckResponse.Status.SERVING else "NOT SERVING"
            logger.info(f"切诊服务健康检查:{status}")
            return response
        except Exception as e:
            raise RuntimeError() from e
