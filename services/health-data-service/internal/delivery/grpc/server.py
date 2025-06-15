#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据服务gRPC服务器实现
"""

import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from loguru import logger
import grpc
from google.protobuf import wrappers_pb2, timestamp_pb2, struct_pb2

from api.grpc.generated import health_data_pb2, health_data_pb2_grpc
from internal.service.health_data_service import HealthDataService
from internal.model.health_data import (
    HealthData, HealthDataType, TCMConstitutionData, HealthInsight,
    HealthProfile, DeviceType, MeasurementUnit, TCMConstitutionType
)


class HealthDataServicer(health_data_pb2_grpc.HealthDataServiceServicer):
    """健康数据服务实现"""
    
    def __init__(self, config: Dict[str, Any], service: HealthDataService):
        """
        初始化gRPC服务
        
        Args:
            config: 配置信息
            service: 健康数据服务实例
        """
        self.config = config
        self.service = service
        logger.info("gRPC服务初始化成功")
    
    async def GetHealthData(
        self, 
        request: health_data_pb2.GetHealthDataRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.GetHealthDataResponse:
        """
        获取健康数据
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            健康数据响应
        """
        try:
            # 解析请求参数
            user_id = request.user_id
            data_type = request.data_type.value if request.HasField("data_type") else None
            start_time = datetime.fromtimestamp(request.start_time.seconds) if request.HasField("start_time") else None
            end_time = datetime.fromtimestamp(request.end_time.seconds) if request.HasField("end_time") else None
            limit = request.limit if request.limit > 0 else 100
            offset = request.offset if request.offset >= 0 else 0
            
            # 获取健康数据
            data_list = await self.service.get_health_data(
                user_id=user_id,
                data_type=data_type,
                start_time=start_time,
                end_time=end_time,
                limit=limit,
                offset=offset
            )
            
            # 构建响应
            response = health_data_pb2.GetHealthDataResponse()
            for data in data_list:
                health_data = self._convert_to_pb_health_data(data)
                response.data.append(health_data)
            
            response.total_count = len(data_list)
            return response
            
        except Exception as e:
            logger.error(f"获取健康数据出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.GetHealthDataResponse()
    
    async def CreateHealthData(
        self, 
        request: health_data_pb2.CreateHealthDataRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.CreateHealthDataResponse:
        """
        创建健康数据
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            创建健康数据响应
        """
        try:
            # 解析请求参数
            user_id = request.user_id
            data_type = self._convert_from_pb_health_data_type(request.data_type)
            timestamp = datetime.fromtimestamp(request.timestamp.seconds)
            device_type = self._convert_from_pb_device_type(request.device_type)
            device_id = request.device_id.value if request.HasField("device_id") else None
            
            # 解析值
            value = None
            value_case = request.WhichOneof("value")
            if value_case == "numeric_value":
                value = request.numeric_value
            elif value_case == "integer_value":
                value = request.integer_value
            elif value_case == "string_value":
                value = request.string_value
            elif value_case == "json_value":
                value = dict(request.json_value)
            
            unit = self._convert_from_pb_measurement_unit(request.unit)
            source = request.source
            metadata = dict(request.metadata) if request.HasField("metadata") else {}
            
            # 创建健康数据对象
            health_data = HealthData(
                user_id=uuid.UUID(user_id),
                data_type=data_type,
                timestamp=timestamp,
                device_type=device_type,
                device_id=device_id,
                value=value,
                unit=unit,
                source=source,
                metadata=metadata
            )
            
            # 保存健康数据
            data_id = await self.service.save_health_data(health_data)
            
            # 构建响应
            response = health_data_pb2.CreateHealthDataResponse()
            response.id = data_id
            return response
            
        except Exception as e:
            logger.error(f"创建健康数据出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.CreateHealthDataResponse()
    
    async def CreateHealthDataBatch(
        self, 
        request: health_data_pb2.CreateHealthDataBatchRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.CreateHealthDataBatchResponse:
        """
        批量创建健康数据
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            批量创建健康数据响应
        """
        try:
            # 解析请求参数
            user_id = request.user_id
            data_list = []
            
            # 解析数据列表
            for item in request.data:
                data_type = self._convert_from_pb_health_data_type(item.data_type)
                timestamp = datetime.fromtimestamp(item.timestamp.seconds)
                device_type = self._convert_from_pb_device_type(item.device_type)
                device_id = item.device_id.value if item.HasField("device_id") else None
                
                # 解析值
                value = None
                value_case = item.WhichOneof("value")
                if value_case == "numeric_value":
                    value = item.numeric_value
                elif value_case == "integer_value":
                    value = item.integer_value
                elif value_case == "string_value":
                    value = item.string_value
                elif value_case == "json_value":
                    value = dict(item.json_value)
                
                unit = self._convert_from_pb_measurement_unit(item.unit)
                source = item.source
                metadata = dict(item.metadata) if item.HasField("metadata") else {}
                
                # 创建健康数据对象
                health_data = HealthData(
                    user_id=uuid.UUID(user_id),
                    data_type=data_type,
                    timestamp=timestamp,
                    device_type=device_type,
                    device_id=device_id,
                    value=value,
                    unit=unit,
                    source=source,
                    metadata=metadata
                )
                data_list.append(health_data)
            
            # 批量保存健康数据
            data_ids = await self.service.save_health_data_batch(data_list)
            
            # 构建响应
            response = health_data_pb2.CreateHealthDataBatchResponse()
            response.ids.extend(data_ids)
            response.processed_count = len(data_ids)
            return response
            
        except Exception as e:
            logger.error(f"批量创建健康数据出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.CreateHealthDataBatchResponse()
    
    async def GetHealthStatistics(
        self, 
        request: health_data_pb2.GetHealthStatisticsRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.GetHealthStatisticsResponse:
        """
        获取健康数据统计
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            健康数据统计响应
        """
        try:
            # 解析请求参数
            user_id = request.user_id
            data_type = self._convert_from_pb_health_data_type(request.data_type)
            days = request.days if request.days > 0 else 30
            
            # 获取健康数据统计
            stats = await self.service.get_health_statistics(
                user_id=user_id,
                data_type=data_type,
                days=days
            )
            
            # 构建响应
            response = health_data_pb2.GetHealthStatisticsResponse()
            response.average = stats["average"]
            response.maximum = stats["maximum"]
            response.minimum = stats["minimum"]
            response.count = stats["count"]
            
            start_ts = timestamp_pb2.Timestamp()
            start_ts.FromDatetime(stats["start_time"])
            response.start_time.CopyFrom(start_ts)
            
            end_ts = timestamp_pb2.Timestamp()
            end_ts.FromDatetime(stats["end_time"])
            response.end_time.CopyFrom(end_ts)
            
            response.data_type = stats["data_type"]
            return response
            
        except Exception as e:
            logger.error(f"获取健康数据统计出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.GetHealthStatisticsResponse()
    
    async def GetTCMConstitution(
        self, 
        request: health_data_pb2.GetTCMConstitutionRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.GetTCMConstitutionResponse:
        """
        获取中医体质
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            中医体质响应
        """
        try:
            # 解析请求参数
            user_id = request.user_id
            
            # 获取中医体质
            constitution = await self.service.get_latest_tcm_constitution(user_id)
            
            # 构建响应
            response = health_data_pb2.GetTCMConstitutionResponse()
            if constitution:
                response.data.CopyFrom(self._convert_to_pb_tcm_constitution(constitution))
            return response
            
        except Exception as e:
            logger.error(f"获取中医体质出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.GetTCMConstitutionResponse()
    
    async def HealthCheck(
        self, 
        request: health_data_pb2.HealthCheckRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_data_pb2.HealthCheckResponse:
        """
        健康检查
        
        Args:
            request: 请求
            context: 上下文
            
        Returns:
            健康检查响应
        """
        try:
            # 执行健康检查
            status, details = await self.service.health_check()
            
            # 构建响应
            response = health_data_pb2.HealthCheckResponse()
            response.status = status
            
            if details:
                struct = struct_pb2.Struct()
                struct.update(details)
                response.details.CopyFrom(struct)
                
            return response
            
        except Exception as e:
            logger.error(f"健康检查出错: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"服务器内部错误: {str(e)}")
            return health_data_pb2.HealthCheckResponse()
    
    def _convert_to_pb_health_data(self, data: HealthData) -> health_data_pb2.HealthData:
        """
        将健康数据转换为protobuf格式
        
        Args:
            data: 健康数据
            
        Returns:
            protobuf格式的健康数据
        """
        pb_data = health_data_pb2.HealthData()
        pb_data.id = str(data.id)
        pb_data.user_id = str(data.user_id)
        pb_data.data_type = self._convert_to_pb_health_data_type(data.data_type)
        
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(data.timestamp)
        pb_data.timestamp.CopyFrom(timestamp)
        
        pb_data.device_type = self._convert_to_pb_device_type(data.device_type)
        
        if data.device_id:
            pb_data.device_id.value = data.device_id
        
        # 设置值
        if isinstance(data.value, float):
            pb_data.numeric_value = data.value
        elif isinstance(data.value, int):
            pb_data.integer_value = data.value
        elif isinstance(data.value, str):
            pb_data.string_value = data.value
        elif isinstance(data.value, dict):
            struct = struct_pb2.Struct()
            struct.update(data.value)
            pb_data.json_value.CopyFrom(struct)
        
        pb_data.unit = self._convert_to_pb_measurement_unit(data.unit)
        pb_data.source = data.source
        
        if data.metadata:
            metadata = struct_pb2.Struct()
            metadata.update(data.metadata)
            pb_data.metadata.CopyFrom(metadata)
        
        created_at = timestamp_pb2.Timestamp()
        created_at.FromDatetime(data.created_at)
        pb_data.created_at.CopyFrom(created_at)
        
        updated_at = timestamp_pb2.Timestamp()
        updated_at.FromDatetime(data.updated_at)
        pb_data.updated_at.CopyFrom(updated_at)
        
        return pb_data
    
    def _convert_to_pb_tcm_constitution(self, data: TCMConstitutionData) -> health_data_pb2.TCMConstitutionData:
        """
        将中医体质数据转换为protobuf格式
        
        Args:
            data: 中医体质数据
            
        Returns:
            protobuf格式的中医体质数据
        """
        pb_data = health_data_pb2.TCMConstitutionData()
        pb_data.id = str(data.id)
        pb_data.user_id = str(data.user_id)
        
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(data.timestamp)
        pb_data.timestamp.CopyFrom(timestamp)
        
        pb_data.primary_type = self._convert_to_pb_tcm_constitution_type(data.primary_type)
        
        for t in data.secondary_types:
            pb_data.secondary_types.append(self._convert_to_pb_tcm_constitution_type(t))
        
        for key, value in data.scores.items():
            pb_data.scores[key] = value
        
        if data.analysis_basis:
            analysis = struct_pb2.Struct()
            analysis.update(data.analysis_basis)
            pb_data.analysis_basis.CopyFrom(analysis)
        
        if data.recommendations:
            recommendations = struct_pb2.Struct()
            recommendations.update(data.recommendations)
            pb_data.recommendations.CopyFrom(recommendations)
        
        pb_data.created_by = data.created_by
        
        created_at = timestamp_pb2.Timestamp()
        created_at.FromDatetime(data.created_at)
        pb_data.created_at.CopyFrom(created_at)
        
        updated_at = timestamp_pb2.Timestamp()
        updated_at.FromDatetime(data.updated_at)
        pb_data.updated_at.CopyFrom(updated_at)
        
        return pb_data
    
    def _convert_to_pb_health_data_type(self, data_type: HealthDataType) -> health_data_pb2.HealthDataType:
        """
        将健康数据类型转换为protobuf枚举
        
        Args:
            data_type: 健康数据类型
            
        Returns:
            protobuf格式的健康数据类型
        """
        mapping = {
            HealthDataType.STEPS: health_data_pb2.HEALTH_DATA_TYPE_STEPS,
            HealthDataType.HEART_RATE: health_data_pb2.HEALTH_DATA_TYPE_HEART_RATE,
            HealthDataType.SLEEP: health_data_pb2.HEALTH_DATA_TYPE_SLEEP,
            HealthDataType.BLOOD_PRESSURE: health_data_pb2.HEALTH_DATA_TYPE_BLOOD_PRESSURE,
            HealthDataType.BLOOD_GLUCOSE: health_data_pb2.HEALTH_DATA_TYPE_BLOOD_GLUCOSE,
            HealthDataType.BODY_TEMPERATURE: health_data_pb2.HEALTH_DATA_TYPE_BODY_TEMPERATURE,
            HealthDataType.OXYGEN_SATURATION: health_data_pb2.HEALTH_DATA_TYPE_OXYGEN_SATURATION,
            HealthDataType.RESPIRATORY_RATE: health_data_pb2.HEALTH_DATA_TYPE_RESPIRATORY_RATE,
            HealthDataType.BODY_MASS: health_data_pb2.HEALTH_DATA_TYPE_BODY_MASS,
            HealthDataType.BODY_FAT: health_data_pb2.HEALTH_DATA_TYPE_BODY_FAT,
            HealthDataType.ACTIVITY: health_data_pb2.HEALTH_DATA_TYPE_ACTIVITY,
            HealthDataType.WATER_INTAKE: health_data_pb2.HEALTH_DATA_TYPE_WATER_INTAKE,
            HealthDataType.NUTRITION: health_data_pb2.HEALTH_DATA_TYPE_NUTRITION,
            HealthDataType.MEDICATION: health_data_pb2.HEALTH_DATA_TYPE_MEDICATION,
            HealthDataType.SYMPTOM: health_data_pb2.HEALTH_DATA_TYPE_SYMPTOM,
            HealthDataType.PULSE: health_data_pb2.HEALTH_DATA_TYPE_PULSE,
            HealthDataType.TONGUE: health_data_pb2.HEALTH_DATA_TYPE_TONGUE,
            HealthDataType.FACE: health_data_pb2.HEALTH_DATA_TYPE_FACE,
            HealthDataType.VOICE: health_data_pb2.HEALTH_DATA_TYPE_VOICE,
            HealthDataType.CUSTOM: health_data_pb2.HEALTH_DATA_TYPE_CUSTOM,
        }
        return mapping.get(data_type, health_data_pb2.HEALTH_DATA_TYPE_UNSPECIFIED)
    
    def _convert_from_pb_health_data_type(self, data_type: health_data_pb2.HealthDataType) -> HealthDataType:
        """
        将protobuf枚举转换为健康数据类型
        
        Args:
            data_type: protobuf格式的健康数据类型
            
        Returns:
            健康数据类型
        """
        mapping = {
            health_data_pb2.HEALTH_DATA_TYPE_STEPS: HealthDataType.STEPS,
            health_data_pb2.HEALTH_DATA_TYPE_HEART_RATE: HealthDataType.HEART_RATE,
            health_data_pb2.HEALTH_DATA_TYPE_SLEEP: HealthDataType.SLEEP,
            health_data_pb2.HEALTH_DATA_TYPE_BLOOD_PRESSURE: HealthDataType.BLOOD_PRESSURE,
            health_data_pb2.HEALTH_DATA_TYPE_BLOOD_GLUCOSE: HealthDataType.BLOOD_GLUCOSE,
            health_data_pb2.HEALTH_DATA_TYPE_BODY_TEMPERATURE: HealthDataType.BODY_TEMPERATURE,
            health_data_pb2.HEALTH_DATA_TYPE_OXYGEN_SATURATION: HealthDataType.OXYGEN_SATURATION,
            health_data_pb2.HEALTH_DATA_TYPE_RESPIRATORY_RATE: HealthDataType.RESPIRATORY_RATE,
            health_data_pb2.HEALTH_DATA_TYPE_BODY_MASS: HealthDataType.BODY_MASS,
            health_data_pb2.HEALTH_DATA_TYPE_BODY_FAT: HealthDataType.BODY_FAT,
            health_data_pb2.HEALTH_DATA_TYPE_ACTIVITY: HealthDataType.ACTIVITY,
            health_data_pb2.HEALTH_DATA_TYPE_WATER_INTAKE: HealthDataType.WATER_INTAKE,
            health_data_pb2.HEALTH_DATA_TYPE_NUTRITION: HealthDataType.NUTRITION,
            health_data_pb2.HEALTH_DATA_TYPE_MEDICATION: HealthDataType.MEDICATION,
            health_data_pb2.HEALTH_DATA_TYPE_SYMPTOM: HealthDataType.SYMPTOM,
            health_data_pb2.HEALTH_DATA_TYPE_PULSE: HealthDataType.PULSE,
            health_data_pb2.HEALTH_DATA_TYPE_TONGUE: HealthDataType.TONGUE,
            health_data_pb2.HEALTH_DATA_TYPE_FACE: HealthDataType.FACE,
            health_data_pb2.HEALTH_DATA_TYPE_VOICE: HealthDataType.VOICE,
            health_data_pb2.HEALTH_DATA_TYPE_CUSTOM: HealthDataType.CUSTOM,
        }
        return mapping.get(data_type, HealthDataType.CUSTOM)
    
    def _convert_to_pb_device_type(self, device_type: DeviceType) -> health_data_pb2.DeviceType:
        """
        将设备类型转换为protobuf枚举
        
        Args:
            device_type: 设备类型
            
        Returns:
            protobuf格式的设备类型
        """
        mapping = {
            DeviceType.APPLE_HEALTH: health_data_pb2.DEVICE_TYPE_APPLE_HEALTH,
            DeviceType.FITBIT: health_data_pb2.DEVICE_TYPE_FITBIT,
            DeviceType.GARMIN: health_data_pb2.DEVICE_TYPE_GARMIN,
            DeviceType.XIAOMI: health_data_pb2.DEVICE_TYPE_XIAOMI,
            DeviceType.TCM_DEVICE: health_data_pb2.DEVICE_TYPE_TCM_DEVICE,
            DeviceType.MANUAL_ENTRY: health_data_pb2.DEVICE_TYPE_MANUAL_ENTRY,
            DeviceType.OTHER: health_data_pb2.DEVICE_TYPE_OTHER,
        }
        return mapping.get(device_type, health_data_pb2.DEVICE_TYPE_UNSPECIFIED)
    
    def _convert_from_pb_device_type(self, device_type: health_data_pb2.DeviceType) -> DeviceType:
        """
        将protobuf枚举转换为设备类型
        
        Args:
            device_type: protobuf格式的设备类型
            
        Returns:
            设备类型
        """
        mapping = {
            health_data_pb2.DEVICE_TYPE_APPLE_HEALTH: DeviceType.APPLE_HEALTH,
            health_data_pb2.DEVICE_TYPE_FITBIT: DeviceType.FITBIT,
            health_data_pb2.DEVICE_TYPE_GARMIN: DeviceType.GARMIN,
            health_data_pb2.DEVICE_TYPE_XIAOMI: DeviceType.XIAOMI,
            health_data_pb2.DEVICE_TYPE_TCM_DEVICE: DeviceType.TCM_DEVICE,
            health_data_pb2.DEVICE_TYPE_MANUAL_ENTRY: DeviceType.MANUAL_ENTRY,
            health_data_pb2.DEVICE_TYPE_OTHER: DeviceType.OTHER,
        }
        return mapping.get(device_type, DeviceType.OTHER)
    
    def _convert_to_pb_measurement_unit(self, unit: MeasurementUnit) -> health_data_pb2.MeasurementUnit:
        """
        将测量单位转换为protobuf枚举
        
        Args:
            unit: 测量单位
            
        Returns:
            protobuf格式的测量单位
        """
        mapping = {
            MeasurementUnit.COUNT: health_data_pb2.MEASUREMENT_UNIT_COUNT,
            MeasurementUnit.STEPS: health_data_pb2.MEASUREMENT_UNIT_STEPS,
            MeasurementUnit.BPM: health_data_pb2.MEASUREMENT_UNIT_BPM,
            MeasurementUnit.MMHG: health_data_pb2.MEASUREMENT_UNIT_MMHG,
            MeasurementUnit.MGDL: health_data_pb2.MEASUREMENT_UNIT_MGDL,
            MeasurementUnit.MMOLL: health_data_pb2.MEASUREMENT_UNIT_MMOLL,
            MeasurementUnit.CELSIUS: health_data_pb2.MEASUREMENT_UNIT_CELSIUS,
            MeasurementUnit.FAHRENHEIT: health_data_pb2.MEASUREMENT_UNIT_FAHRENHEIT,
            MeasurementUnit.PERCENT: health_data_pb2.MEASUREMENT_UNIT_PERCENT,
            MeasurementUnit.KG: health_data_pb2.MEASUREMENT_UNIT_KG,
            MeasurementUnit.LB: health_data_pb2.MEASUREMENT_UNIT_LB,
            MeasurementUnit.MINUTES: health_data_pb2.MEASUREMENT_UNIT_MINUTES,
            MeasurementUnit.HOURS: health_data_pb2.MEASUREMENT_UNIT_HOURS,
            MeasurementUnit.KCAL: health_data_pb2.MEASUREMENT_UNIT_KCAL,
            MeasurementUnit.ML: health_data_pb2.MEASUREMENT_UNIT_ML,
            MeasurementUnit.G: health_data_pb2.MEASUREMENT_UNIT_G,
            MeasurementUnit.MG: health_data_pb2.MEASUREMENT_UNIT_MG,
            MeasurementUnit.RPM: health_data_pb2.MEASUREMENT_UNIT_RPM,
            MeasurementUnit.CUSTOM: health_data_pb2.MEASUREMENT_UNIT_CUSTOM,
        }
        return mapping.get(unit, health_data_pb2.MEASUREMENT_UNIT_UNSPECIFIED)
    
    def _convert_from_pb_measurement_unit(self, unit: health_data_pb2.MeasurementUnit) -> MeasurementUnit:
        """
        将protobuf枚举转换为测量单位
        
        Args:
            unit: protobuf格式的测量单位
            
        Returns:
            测量单位
        """
        mapping = {
            health_data_pb2.MEASUREMENT_UNIT_COUNT: MeasurementUnit.COUNT,
            health_data_pb2.MEASUREMENT_UNIT_STEPS: MeasurementUnit.STEPS,
            health_data_pb2.MEASUREMENT_UNIT_BPM: MeasurementUnit.BPM,
            health_data_pb2.MEASUREMENT_UNIT_MMHG: MeasurementUnit.MMHG,
            health_data_pb2.MEASUREMENT_UNIT_MGDL: MeasurementUnit.MGDL,
            health_data_pb2.MEASUREMENT_UNIT_MMOLL: MeasurementUnit.MMOLL,
            health_data_pb2.MEASUREMENT_UNIT_CELSIUS: MeasurementUnit.CELSIUS,
            health_data_pb2.MEASUREMENT_UNIT_FAHRENHEIT: MeasurementUnit.FAHRENHEIT,
            health_data_pb2.MEASUREMENT_UNIT_PERCENT: MeasurementUnit.PERCENT,
            health_data_pb2.MEASUREMENT_UNIT_KG: MeasurementUnit.KG,
            health_data_pb2.MEASUREMENT_UNIT_LB: MeasurementUnit.LB,
            health_data_pb2.MEASUREMENT_UNIT_MINUTES: MeasurementUnit.MINUTES,
            health_data_pb2.MEASUREMENT_UNIT_HOURS: MeasurementUnit.HOURS,
            health_data_pb2.MEASUREMENT_UNIT_KCAL: MeasurementUnit.KCAL,
            health_data_pb2.MEASUREMENT_UNIT_ML: MeasurementUnit.ML,
            health_data_pb2.MEASUREMENT_UNIT_G: MeasurementUnit.G,
            health_data_pb2.MEASUREMENT_UNIT_MG: MeasurementUnit.MG,
            health_data_pb2.MEASUREMENT_UNIT_RPM: MeasurementUnit.RPM,
            health_data_pb2.MEASUREMENT_UNIT_CUSTOM: MeasurementUnit.CUSTOM,
        }
        return mapping.get(unit, MeasurementUnit.CUSTOM)
    
    def _convert_to_pb_tcm_constitution_type(self, constitution_type: TCMConstitutionType) -> health_data_pb2.TCMConstitutionType:
        """
        将中医体质类型转换为protobuf枚举
        
        Args:
            constitution_type: 中医体质类型
            
        Returns:
            protobuf格式的中医体质类型
        """
        mapping = {
            TCMConstitutionType.BALANCED: health_data_pb2.TCM_CONSTITUTION_TYPE_BALANCED,
            TCMConstitutionType.QI_DEFICIENCY: health_data_pb2.TCM_CONSTITUTION_TYPE_QI_DEFICIENCY,
            TCMConstitutionType.YANG_DEFICIENCY: health_data_pb2.TCM_CONSTITUTION_TYPE_YANG_DEFICIENCY,
            TCMConstitutionType.YIN_DEFICIENCY: health_data_pb2.TCM_CONSTITUTION_TYPE_YIN_DEFICIENCY,
            TCMConstitutionType.PHLEGM_DAMPNESS: health_data_pb2.TCM_CONSTITUTION_TYPE_PHLEGM_DAMPNESS,
            TCMConstitutionType.DAMPNESS_HEAT: health_data_pb2.TCM_CONSTITUTION_TYPE_DAMPNESS_HEAT,
            TCMConstitutionType.BLOOD_STASIS: health_data_pb2.TCM_CONSTITUTION_TYPE_BLOOD_STASIS,
            TCMConstitutionType.QI_DEPRESSION: health_data_pb2.TCM_CONSTITUTION_TYPE_QI_DEPRESSION,
            TCMConstitutionType.SPECIAL: health_data_pb2.TCM_CONSTITUTION_TYPE_SPECIAL,
        }
        return mapping.get(constitution_type, health_data_pb2.TCM_CONSTITUTION_TYPE_UNSPECIFIED)
    
    def _convert_from_pb_tcm_constitution_type(self, constitution_type: health_data_pb2.TCMConstitutionType) -> TCMConstitutionType:
        """
        将protobuf枚举转换为中医体质类型
        
        Args:
            constitution_type: protobuf格式的中医体质类型
            
        Returns:
            中医体质类型
        """
        mapping = {
            health_data_pb2.TCM_CONSTITUTION_TYPE_BALANCED: TCMConstitutionType.BALANCED,
            health_data_pb2.TCM_CONSTITUTION_TYPE_QI_DEFICIENCY: TCMConstitutionType.QI_DEFICIENCY,
            health_data_pb2.TCM_CONSTITUTION_TYPE_YANG_DEFICIENCY: TCMConstitutionType.YANG_DEFICIENCY,
            health_data_pb2.TCM_CONSTITUTION_TYPE_YIN_DEFICIENCY: TCMConstitutionType.YIN_DEFICIENCY,
            health_data_pb2.TCM_CONSTITUTION_TYPE_PHLEGM_DAMPNESS: TCMConstitutionType.PHLEGM_DAMPNESS,
            health_data_pb2.TCM_CONSTITUTION_TYPE_DAMPNESS_HEAT: TCMConstitutionType.DAMPNESS_HEAT,
            health_data_pb2.TCM_CONSTITUTION_TYPE_BLOOD_STASIS: TCMConstitutionType.BLOOD_STASIS,
            health_data_pb2.TCM_CONSTITUTION_TYPE_QI_DEPRESSION: TCMConstitutionType.QI_DEPRESSION,
            health_data_pb2.TCM_CONSTITUTION_TYPE_SPECIAL: TCMConstitutionType.SPECIAL,
        }
        return mapping.get(constitution_type, TCMConstitutionType.BALANCED)