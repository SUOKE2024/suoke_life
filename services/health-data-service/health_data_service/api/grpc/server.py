"""
server - 索克生活项目模块
"""

    from health_data_service.api.grpc import health_data_pb2, health_data_pb2_grpc
from datetime import datetime
from google.protobuf import struct_pb2, timestamp_pb2
from grpc import aio
from health_data_service.core.config import get_settings
from health_data_service.core.exceptions import DatabaseError, NotFoundError, ValidationError
from health_data_service.models import (
from health_data_service.services.health_data_service import (
from typing import Dict, Any, List, Optional
import asyncio
import grpc
import logging

#!/usr/bin/env python3
"""
gRPC服务器实现

提供健康数据服务的gRPC接口实现。
"""



    CreateHealthDataRequest,
    CreateVitalSignsRequest,
    UpdateHealthDataRequest,
    DataType,
    DataSource,
)
    HealthDataService,
    VitalSignsService,
    TCMDiagnosisService,
)

# 导入生成的gRPC代码（需要先编译proto文件）
try:
except ImportError:
    # 如果没有生成的代码，创建占位符
    class health_data_pb2:
        pass
    
    class health_data_pb2_grpc:
        class HealthDataServiceServicer:
            pass

settings = get_settings()
logger = logging.getLogger(__name__)


# 模拟gRPC生成的代码结构
class HealthDataPb2:
    """模拟health_data_pb2模块"""
    
    # 枚举值
    DATA_TYPE_UNSPECIFIED = 0
    VITAL_SIGNS = 1
    BLOOD_TEST = 2
    URINE_TEST = 3
    IMAGING = 4
    SYMPTOMS = 5
    MEDICATION = 6
    EXERCISE = 7
    SLEEP = 8
    DIET = 9
    MOOD = 10
    
    DATA_SOURCE_UNSPECIFIED = 0
    MANUAL = 1
    DEVICE = 2
    HOSPITAL = 3
    THIRD_PARTY = 4
    AI_ANALYSIS = 5
    
    class HealthData:
        def __init__(self):
            self.id = 0
            self.user_id = 0
            self.data_type = 0
            self.data_source = 0
            self.raw_data = struct_pb2.Struct()
            self.processed_data = struct_pb2.Struct()
            self.device_id = ""
            self.location = ""
            self.tags = []
            self.quality_score = 0.0
            self.confidence_score = 0.0
            self.is_validated = False
            self.is_anomaly = False
            self.recorded_at = timestamp_pb2.Timestamp()
            self.created_at = timestamp_pb2.Timestamp()
            self.updated_at = timestamp_pb2.Timestamp()
    
    class HealthDataResponse:
        def __init__(self):
            self.success = False
            self.message = ""
            self.data = self.HealthData()
    
    class CreateHealthDataRequest:
        def __init__(self):
            self.user_id = 0
            self.data_type = 0
            self.data_source = 0
            self.raw_data = struct_pb2.Struct()
            self.device_id = ""
            self.location = ""
            self.tags = []
            self.recorded_at = timestamp_pb2.Timestamp()
    
    class GetHealthDataRequest:
        def __init__(self):
            self.id = 0
    
    class UpdateHealthDataRequest:
        def __init__(self):
            self.id = 0
            self.processed_data = struct_pb2.Struct()
            self.quality_score = 0.0
            self.confidence_score = 0.0
            self.is_validated = False
            self.is_anomaly = False
            self.tags = []
    
    class DeleteHealthDataRequest:
        def __init__(self):
            self.id = 0
    
    class DeleteHealthDataResponse:
        def __init__(self):
            self.success = False
            self.message = ""
    
    class ListHealthDataRequest:
        def __init__(self):
            self.user_id = 0
            self.data_type = ""
            self.skip = 0
            self.limit = 100
    
    class ListHealthDataResponse:
        def __init__(self):
            self.success = False
            self.message = ""
            self.items = []
            self.total = 0
            self.skip = 0
            self.limit = 100
    
    class HealthCheckRequest:
        def __init__(self):
            pass
    
    class HealthCheckResponse:
        def __init__(self):
            self.healthy = False
            self.status = ""
            self.timestamp = timestamp_pb2.Timestamp()


class HealthDataServiceServicer:
    """健康数据gRPC服务基类"""
    pass


# 使用模拟的类
health_data_pb2 = HealthDataPb2()


class HealthDataServicer(HealthDataServiceServicer):
    """健康数据gRPC服务实现"""

    def __init__(self):
        self.health_data_service = HealthDataService()
        self.vital_signs_service = VitalSignsService()
        self.tcm_diagnosis_service = TCMDiagnosisService()

    def _convert_timestamp_to_pb(self, dt: datetime) -> timestamp_pb2.Timestamp:
        """将datetime转换为protobuf Timestamp"""
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp

    def _convert_pb_to_timestamp(self, pb_timestamp: timestamp_pb2.Timestamp) -> datetime:
        """将protobuf Timestamp转换为datetime"""
        return pb_timestamp.ToDatetime()

    def _convert_dict_to_struct(self, data: Dict[str, Any]) -> struct_pb2.Struct:
        """将字典转换为protobuf Struct"""
        struct = struct_pb2.Struct()
        struct.update(data)
        return struct

    def _convert_struct_to_dict(self, struct: struct_pb2.Struct) -> Dict[str, Any]:
        """将protobuf Struct转换为字典"""
        return dict(struct)

    def _convert_health_data_to_pb(self, health_data) -> HealthDataPb2.HealthData:
        """将健康数据模型转换为protobuf消息"""
        pb_health_data = health_data_pb2.HealthData()
        pb_health_data.id = health_data.id
        pb_health_data.user_id = health_data.user_id
        
        # 转换枚举
        data_type_map = {
            DataType.VITAL_SIGNS: health_data_pb2.VITAL_SIGNS,
            DataType.BLOOD_TEST: health_data_pb2.BLOOD_TEST,
            DataType.URINE_TEST: health_data_pb2.URINE_TEST,
            DataType.IMAGING: health_data_pb2.IMAGING,
            DataType.SYMPTOMS: health_data_pb2.SYMPTOMS,
            DataType.MEDICATION: health_data_pb2.MEDICATION,
            DataType.EXERCISE: health_data_pb2.EXERCISE,
            DataType.SLEEP: health_data_pb2.SLEEP,
            DataType.DIET: health_data_pb2.DIET,
            DataType.MOOD: health_data_pb2.MOOD,
        }
        pb_health_data.data_type = data_type_map.get(health_data.data_type, health_data_pb2.DATA_TYPE_UNSPECIFIED)
        
        data_source_map = {
            DataSource.MANUAL: health_data_pb2.MANUAL,
            DataSource.DEVICE: health_data_pb2.DEVICE,
            DataSource.HOSPITAL: health_data_pb2.HOSPITAL,
            DataSource.THIRD_PARTY: health_data_pb2.THIRD_PARTY,
            DataSource.AI_ANALYSIS: health_data_pb2.AI_ANALYSIS,
        }
        pb_health_data.data_source = data_source_map.get(health_data.data_source, health_data_pb2.DATA_SOURCE_UNSPECIFIED)
        
        # 转换数据
        pb_health_data.raw_data = self._convert_dict_to_struct(health_data.raw_data)
        if health_data.processed_data:
            pb_health_data.processed_data = self._convert_dict_to_struct(health_data.processed_data)
        
        # 可选字段
        if health_data.device_id:
            pb_health_data.device_id = health_data.device_id
        if health_data.location:
            pb_health_data.location = health_data.location
        if health_data.tags:
            pb_health_data.tags.extend(health_data.tags)
        if health_data.quality_score is not None:
            pb_health_data.quality_score = health_data.quality_score
        if health_data.confidence_score is not None:
            pb_health_data.confidence_score = health_data.confidence_score
        
        pb_health_data.is_validated = health_data.is_validated
        pb_health_data.is_anomaly = health_data.is_anomaly
        
        # 时间戳
        pb_health_data.recorded_at = self._convert_timestamp_to_pb(health_data.recorded_at)
        pb_health_data.created_at = self._convert_timestamp_to_pb(health_data.created_at)
        pb_health_data.updated_at = self._convert_timestamp_to_pb(health_data.updated_at)
        
        return pb_health_data

    async def CreateHealthData(self, request, context) -> HealthDataPb2.HealthDataResponse:
        """创建健康数据"""
        try:
            # 转换请求
            data_type_map = {
                health_data_pb2.VITAL_SIGNS: DataType.VITAL_SIGNS,
                health_data_pb2.BLOOD_TEST: DataType.BLOOD_TEST,
                health_data_pb2.URINE_TEST: DataType.URINE_TEST,
                health_data_pb2.IMAGING: DataType.IMAGING,
                health_data_pb2.SYMPTOMS: DataType.SYMPTOMS,
                health_data_pb2.MEDICATION: DataType.MEDICATION,
                health_data_pb2.EXERCISE: DataType.EXERCISE,
                health_data_pb2.SLEEP: DataType.SLEEP,
                health_data_pb2.DIET: DataType.DIET,
                health_data_pb2.MOOD: DataType.MOOD,
            }
            
            data_source_map = {
                health_data_pb2.MANUAL: DataSource.MANUAL,
                health_data_pb2.DEVICE: DataSource.DEVICE,
                health_data_pb2.HOSPITAL: DataSource.HOSPITAL,
                health_data_pb2.THIRD_PARTY: DataSource.THIRD_PARTY,
                health_data_pb2.AI_ANALYSIS: DataSource.AI_ANALYSIS,
            }
            
            create_request = CreateHealthDataRequest(
                user_id=request.user_id,
                data_type=data_type_map.get(request.data_type, DataType.VITAL_SIGNS),
                data_source=data_source_map.get(request.data_source, DataSource.MANUAL),
                raw_data=self._convert_struct_to_dict(request.raw_data),
                device_id=request.device_id if request.device_id else None,
                location=request.location if request.location else None,
                tags=list(request.tags) if request.tags else [],
                recorded_at=self._convert_pb_to_timestamp(request.recorded_at) if hasattr(request, 'recorded_at') else None,
            )
            
            # 调用服务
            health_data = await self.health_data_service.create(create_request)
            
            # 构建响应
            response = health_data_pb2.HealthDataResponse()
            response.success = True
            response.message = "健康数据创建成功"
            response.data = self._convert_health_data_to_pb(health_data)
            
            return response
            
        except ValidationError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            response = health_data_pb2.HealthDataResponse()
            response.success = False
            response.message = f"数据验证失败: {str(e)}"
            return response
            
        except DatabaseError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            response = health_data_pb2.HealthDataResponse()
            response.success = False
            response.message = f"数据库操作失败: {str(e)}"
            return response
            
        except Exception as e:
            logger.error(f"创建健康数据失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            response = health_data_pb2.HealthDataResponse()
            response.success = False
            response.message = f"创建健康数据失败: {str(e)}"
            return response

    async def GetHealthData(self, request, context) -> HealthDataPb2.HealthDataResponse:
        """获取健康数据"""
        try:
            health_data = await self.health_data_service.get_by_id(request.id)
            
            if not health_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"健康数据不存在: id={request.id}")
                response = health_data_pb2.HealthDataResponse()
                response.success = False
                response.message = f"健康数据不存在: id={request.id}"
                return response
            
            response = health_data_pb2.HealthDataResponse()
            response.success = True
            response.message = "获取健康数据成功"
            response.data = self._convert_health_data_to_pb(health_data)
            
            return response
            
        except Exception as e:
            logger.error(f"获取健康数据失败: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            response = health_data_pb2.HealthDataResponse()
            response.success = False
            response.message = f"获取健康数据失败: {str(e)}"
            return response

    async def HealthCheck(self, request, context) -> HealthDataPb2.HealthCheckResponse:
        """健康检查"""
        try:
            response = health_data_pb2.HealthCheckResponse()
            response.healthy = True
            response.status = "健康数据服务运行正常"
            response.timestamp = self._convert_timestamp_to_pb(datetime.now())
            
            return response
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            response = health_data_pb2.HealthCheckResponse()
            response.healthy = False
            response.status = f"健康数据服务异常: {str(e)}"
            response.timestamp = self._convert_timestamp_to_pb(datetime.now())
            
            return response


def add_HealthDataServiceServicer_to_server(servicer, server):
    """添加服务到gRPC服务器（模拟函数）"""
    # 这里应该是生成的代码，暂时用占位符
    pass


async def serve():
    """启动gRPC服务器"""
    server = aio.server()
    
    # 添加服务
    add_HealthDataServiceServicer_to_server(HealthDataServicer(), server)
    
    # 配置监听地址
    grpc_port = getattr(settings.api, 'grpc_port', 50051)
    listen_addr = f"[::]:{grpc_port}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"启动gRPC服务器，监听地址: {listen_addr}")
    
    # 启动服务器
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭gRPC服务器...")
        await server.stop(grace=5)


if __name__ == "__main__":
    asyncio.run(serve()) 