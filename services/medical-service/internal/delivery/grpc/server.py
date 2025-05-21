#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import threading
import grpc
from concurrent import futures
from typing import Dict, Any
from google.protobuf.timestamp_pb2 import Timestamp

# 假设API生成的gRPC服务实现
# 实际使用时需要通过protoc生成Python代码
# import medical_service_pb2
# import medical_service_pb2_grpc

from api.grpc import medical_pb2_grpc
from internal.delivery.grpc.medical_service import MedicalServicer

logger = logging.getLogger(__name__)


class MedicalServiceServicer:
    """
    gRPC医疗服务实现
    注意：这是一个占位符实现，实际使用时需要根据生成的proto代码实现接口
    """
    
    def __init__(self, services):
        self.medical_record_service = services['medical_record_service']
        self.diagnosis_service = services['diagnosis_service']
        self.treatment_service = services['treatment_service']
        self.health_risk_service = services['health_risk_service']
        self.medical_query_service = services['medical_query_service']
    
    def CreateMedicalRecord(self, request, context):
        """创建医疗记录"""
        try:
            logger.info(f"Creating medical record for user {request.user_id}")
            record_date = request.record_date.ToDatetime() if hasattr(request, 'record_date') else None
            
            record = self.medical_record_service.create_medical_record(
                user_id=request.user_id,
                record_type=request.record_type,
                record_date=record_date,
                doctor_id=request.doctor_id if hasattr(request, 'doctor_id') else None,
                doctor_name=request.doctor_name if hasattr(request, 'doctor_name') else None,
                institution=request.institution if hasattr(request, 'institution') else None,
                chief_complaint=request.chief_complaint if hasattr(request, 'chief_complaint') else None,
                diagnosis=request.diagnosis if hasattr(request, 'diagnosis') else None,
                treatment=request.treatment if hasattr(request, 'treatment') else None,
                notes=request.notes if hasattr(request, 'notes') else None
            )
            
            # 将domainModel转换为protobuf message
            # 注意：实际代码需要根据生成的proto定义填充
            # response = medical_service_pb2.MedicalRecord(
            #     id=record.id,
            #     user_id=record.user_id,
            #     ...
            # )
            # return response
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error creating medical record: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    def GetMedicalRecord(self, request, context):
        """获取医疗记录"""
        try:
            logger.info(f"Getting medical record with id {request.id}")
            record = self.medical_record_service.get_medical_record(request.id)
            
            if not record:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Medical record with id {request.id} not found")
                return None
            
            # 将domainModel转换为protobuf message
            # 实际代码需要根据生成的proto定义填充
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error getting medical record: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    def ListMedicalRecords(self, request, context):
        """列出医疗记录"""
        try:
            logger.info(f"Listing medical records for user {request.user_id}")
            
            # 构造查询参数
            filters = {
                'user_id': request.user_id
            }
            
            if hasattr(request, 'record_type') and request.record_type:
                filters['record_type'] = request.record_type
                
            if hasattr(request, 'start_date') and request.start_date:
                filters['start_date'] = request.start_date.ToDatetime()
                
            if hasattr(request, 'end_date') and request.end_date:
                filters['end_date'] = request.end_date.ToDatetime()
            
            page = request.page if hasattr(request, 'page') else 1
            page_size = request.page_size if hasattr(request, 'page_size') else 10
            
            records, total = self.medical_record_service.list_medical_records(
                filters=filters,
                page=page,
                page_size=page_size
            )
            
            # 将domainModel列表转换为protobuf message
            # 实际代码需要根据生成的proto定义填充
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error listing medical records: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    def UpdateMedicalRecord(self, request, context):
        """更新医疗记录"""
        try:
            logger.info(f"Updating medical record with id {request.id}")
            
            # 构造更新参数
            record_date = request.record_date.ToDatetime() if hasattr(request, 'record_date') else None
            
            updated_record = self.medical_record_service.update_medical_record(
                record_id=request.id,
                record_type=request.record_type if hasattr(request, 'record_type') else None,
                record_date=record_date,
                doctor_id=request.doctor_id if hasattr(request, 'doctor_id') else None,
                doctor_name=request.doctor_name if hasattr(request, 'doctor_name') else None,
                institution=request.institution if hasattr(request, 'institution') else None,
                chief_complaint=request.chief_complaint if hasattr(request, 'chief_complaint') else None,
                diagnosis=request.diagnosis if hasattr(request, 'diagnosis') else None,
                treatment=request.treatment if hasattr(request, 'treatment') else None,
                notes=request.notes if hasattr(request, 'notes') else None
            )
            
            if not updated_record:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Medical record with id {request.id} not found")
                return None
            
            # 将domainModel转换为protobuf message
            # 实际代码需要根据生成的proto定义填充
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error updating medical record: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    def DeleteMedicalRecord(self, request, context):
        """删除医疗记录"""
        try:
            logger.info(f"Deleting medical record with id {request.id}")
            
            success = self.medical_record_service.delete_medical_record(request.id)
            
            if not success:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Medical record with id {request.id} not found")
                return None
            
            # 返回空响应
            # return medical_service_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error deleting medical record: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    def RequestDiagnosis(self, request, context):
        """请求诊断"""
        try:
            logger.info(f"Requesting diagnosis for user {request.user_id}")
            
            diagnosis_id = self.diagnosis_service.request_diagnosis(
                user_id=request.user_id,
                chief_complaint=request.chief_complaint,
                symptoms=list(request.symptoms) if hasattr(request, 'symptoms') else [],
                health_data={k: v for k, v in request.health_data.items()} if hasattr(request, 'health_data') else {},
                diagnostic_methods=list(request.diagnostic_methods) if hasattr(request, 'diagnostic_methods') else [],
                include_western_medicine=request.include_western_medicine if hasattr(request, 'include_western_medicine') else True,
                include_tcm=request.include_tcm if hasattr(request, 'include_tcm') else True
            )
            
            # 将结果转换为protobuf message
            # 实际代码需要根据生成的proto定义填充
            
            # 占位符返回
            return None
            
        except Exception as e:
            logger.error(f"Error requesting diagnosis: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return None
    
    # 更多方法实现...
    # 示例方法仅作为参考，实际应用中需要实现所有proto文件中定义的方法


class GrpcServer:
    """gRPC服务器类"""
    
    def __init__(self, config, services):
        """
        初始化gRPC服务器
        
        Args:
            config: 服务配置
            services: 服务对象字典
        """
        self.config = config
        self.services = services
        self.server = None
        self.server_thread = None
        self.is_running = False
    
    def start(self):
        """启动gRPC服务器"""
        if self.is_running:
            logger.warning("gRPC服务器已经在运行")
            return
        
        try:
            # 创建gRPC服务器
            self.server = grpc.server(
                futures.ThreadPoolExecutor(max_workers=self.config.server.grpc.workers),
                options=[
                    ('grpc.max_send_message_length', self.config.server.grpc.max_message_length),
                    ('grpc.max_receive_message_length', self.config.server.grpc.max_message_length)
                ]
            )
            
            # 注册服务
            medical_servicer = MedicalServicer(self.services)
            medical_pb2_grpc.add_MedicalServiceServicer_to_server(medical_servicer, self.server)
            
            # 添加健康检查服务
            from grpc_health.v1 import health, health_pb2_grpc
            health_servicer = health.HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)
            
            # 设置健康状态
            health_servicer.set('', health_pb2_grpc.HealthCheckResponse.SERVING)
            health_servicer.set('medical.MedicalService', health_pb2_grpc.HealthCheckResponse.SERVING)
            
            # 绑定端口
            port = self.config.server.grpc.port
            address = f'[::]:{port}'
            self.server.add_insecure_port(address)
            
            # 在单独的线程中启动服务器
            self.server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self.server_thread.start()
            self.is_running = True
            
            logger.info(f"gRPC服务器已启动，监听端口：{port}")
            
        except Exception as e:
            logger.error(f"启动gRPC服务器失败: {str(e)}")
            raise
    
    def _run_server(self):
        """在线程中运行服务器"""
        try:
            self.server.start()
            # 阻塞线程，等待服务器停止
            self.server.wait_for_termination()
        except Exception as e:
            logger.error(f"gRPC服务器运行失败: {str(e)}")
            self.is_running = False
    
    def stop(self):
        """停止gRPC服务器"""
        if not self.is_running:
            logger.warning("gRPC服务器未运行")
            return
        
        try:
            logger.info("正在停止gRPC服务器...")
            
            # 停止接受新请求
            self.server.stop(grace=5)  # 优雅关闭，等待5秒完成现有请求
            
            # 确保服务器完全停止
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=10)
            
            self.is_running = False
            logger.info("gRPC服务器已停止")
            
        except Exception as e:
            logger.error(f"停止gRPC服务器失败: {str(e)}")
            raise

def create_grpc_server(config, services):
    """
    创建gRPC服务器
    
    Args:
        config: 服务配置
        services: 服务对象字典
        
    Returns:
        GrpcServer实例
    """
    return GrpcServer(config, services) 