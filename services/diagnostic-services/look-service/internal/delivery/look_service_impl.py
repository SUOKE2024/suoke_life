#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
望诊服务(Look Service)gRPC接口实现
处理舌象分析、面色分析、形体分析等请求

本模块实现了望诊服务的gRPC接口，基于传统中医"望诊"理论，通过计算机视觉技术
分析用户提供的舌象、面色、形体图像，从而辅助中医诊断和健康状况评估。
"""

import time
import uuid
import traceback
from typing import Dict, List, Optional, Tuple, Any

import grpc
import structlog
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent import futures
from prometheus_client import Counter, Histogram, start_http_server

from api.grpc import look_service_pb2, look_service_pb2_grpc
from internal.analysis.tongue_analyzer import (ConstitutionCorrelation,
                                              TongueAnalyzer)
from internal.model.model_factory import ModelFactory
from internal.repository.analysis_repository import AnalysisRepository
from pkg.utils.exceptions import (InvalidInputError, ProcessingError, 
                                 ResourceNotFoundError, AuthenticationError)
from config.config import get_config
from internal.analysis.face_analyzer import FaceAnalyzer, FaceAnalysisResult
from internal.analysis.body_analyzer import BodyAnalyzer, BodyAnalysisResult
from internal.integration.xiaoai_client import XiaoaiServiceClient

# 设置日志
logger = structlog.get_logger()

# 监控指标
REQUEST_COUNTER = Counter(
    'look_service_requests_total',
    'Total number of requests received',
    ['method', 'status']
)
REQUEST_LATENCY = Histogram(
    'look_service_request_latency_seconds',
    'Request latency in seconds',
    ['method']
)


class LookServiceServicer(look_service_pb2_grpc.LookServiceServicer):
    """
    望诊服务gRPC接口实现
    
    实现look_service.proto中定义的所有望诊相关服务接口，包括：
    - 舌象分析 (AnalyzeTongue)
    - 面色分析 (AnalyzeFace)
    - 形体分析 (AnalyzeBody)
    - 获取历史分析记录 (GetAnalysisHistory)
    - 比较分析结果 (CompareAnalysis)
    - 健康检查 (HealthCheck)
    """
    
    def __init__(
        self, 
        config: Dict, 
        model_factory: ModelFactory,
        tongue_analyzer: TongueAnalyzer,
        analysis_repository: AnalysisRepository
    ):
        """
        初始化服务实现
        
        Args:
            config: 服务配置字典，包含所有服务配置参数
            model_factory: 模型工厂，用于创建和管理各类模型实例
            tongue_analyzer: 舌象分析器，处理舌象分析相关的核心逻辑
            analysis_repository: 分析结果存储库，负责持久化和检索分析结果
        """
        self.config = config
        self.model_factory = model_factory
        self.tongue_analyzer = tongue_analyzer
        self.analysis_repository = analysis_repository
        
        # 配置参数
        self.save_visualizations = config.get("save_visualizations", True)
        self.max_image_size = config.get("max_image_size", 10 * 1024 * 1024)  # 默认最大10MB
        self.default_limit = config.get("default_history_limit", 10)
        
        # 初始化小艾服务客户端
        xiaoai_config = config.get("integration.xiaoai_service", {})
        self.xiaoai_client = XiaoaiServiceClient(
            host=xiaoai_config.get("host", "xiaoai-service"),
            port=xiaoai_config.get("port", 50050)
        )
        
        logger.info(
            "望诊服务初始化完成",
            save_visualizations=self.save_visualizations,
            max_image_size=self.max_image_size
        )
    
    def AnalyzeTongue(
        self, 
        request: look_service_pb2.TongueAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.TongueAnalysisResponse:
        """
        舌象分析接口实现，处理舌象图像并返回详细分析结果
        
        分析内容包括：舌色、舌形、舌苔、舌苔分布等特征，以及对应的中医体质关联分析。
        
        Args:
            request: 舌象分析请求，包含用户ID、图像数据等信息
            context: gRPC服务上下文，用于设置响应状态和元数据
            
        Returns:
            舌象分析响应，包含全面的舌象特征和中医分析结果
            
        Raises:
            grpc.RpcError: 当处理失败时通过context设置适当的错误码和错误信息
        """
        try:
            logger.info(
                "接收到舌象分析请求", 
                user_id=request.user_id,
                analysis_type=look_service_pb2.AnalysisType.Name(request.analysis_type),
                save_result=request.save_result,
                image_size=len(request.image),
                metadata=dict(request.metadata)
            )
            
            # 验证请求参数
            self._validate_analysis_request(request, context)
            if context.code() != grpc.StatusCode.OK:
                return look_service_pb2.TongueAnalysisResponse()
                
            # 检查图像大小
            if len(request.image) > self.max_image_size:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details(f"图像大小超出限制，最大允许{self.max_image_size}字节")
                return look_service_pb2.TongueAnalysisResponse()
            
            # 分析舌象
            start_time = time.time()
            analysis_result = self.tongue_analyzer.analyze(
                image_data=request.image,
                user_id=request.user_id,
                save_result=request.save_result,
                save_visualizations=self.save_visualizations
            )
            processing_time = time.time() - start_time
            
            logger.info(
                "舌象分析完成", 
                user_id=request.user_id,
                processing_time_ms=int(processing_time * 1000),
                analysis_id=analysis_result.analysis_id,
                tongue_color=analysis_result.tongue_color.value,
                coating_color=analysis_result.coating_color.value
            )
            
            # 构建响应
            response = look_service_pb2.TongueAnalysisResponse(
                request_id=analysis_result.request_id,
                tongue_color=analysis_result.tongue_color.value,
                tongue_shape=analysis_result.tongue_shape.value,
                coating_color=analysis_result.coating_color.value,
                coating_distribution=analysis_result.coating_distribution,
                features=analysis_result.features,
                analysis_summary=analysis_result.analysis_summary,
                analysis_id=analysis_result.analysis_id,
                timestamp=analysis_result.timestamp
            )
            
            # 添加特征位置
            for location in analysis_result.locations:
                response.locations.append(look_service_pb2.FeatureLocation(
                    feature_name=location.feature_name,
                    x_min=location.x_min,
                    y_min=location.y_min,
                    x_max=location.x_max,
                    y_max=location.y_max,
                    confidence=location.confidence
                ))
            
            # 添加体质关联
            for constitution in analysis_result.body_constitution:
                response.body_constitution.append(look_service_pb2.ConstitutionCorrelation(
                    constitution_type=constitution.constitution_type,
                    confidence=constitution.confidence,
                    description=constitution.description
                ))
                
            # 添加量化指标
            for key, value in analysis_result.metrics.items():
                response.metrics[key] = value
                
            # 设置响应元数据
            context.set_trailing_metadata([
                ('processing_time_ms', str(int(processing_time * 1000))),
                ('analyzer_version', self.tongue_analyzer.version)
            ])
            
            return response
            
        except InvalidInputError as e:
            logger.warning(
                "舌象分析输入验证失败", 
                error=str(e),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"输入错误: {str(e)}")
            return look_service_pb2.TongueAnalysisResponse()
            
        except ResourceNotFoundError as e:
            logger.warning(
                "舌象分析资源不存在", 
                error=str(e),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"资源不存在: {str(e)}")
            return look_service_pb2.TongueAnalysisResponse()
            
        except ProcessingError as e:
            logger.error(
                "舌象分析处理失败", 
                error=str(e),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"处理错误: {str(e)}")
            return look_service_pb2.TongueAnalysisResponse()
            
        except Exception as e:
            logger.error(
                "舌象分析过程发生未预期的错误", 
                error=str(e),
                traceback=traceback.format_exc(),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"内部服务错误: {str(e)}")
            return look_service_pb2.TongueAnalysisResponse()
    
    def _validate_analysis_request(
        self, 
        request: Any, 
        context: grpc.ServicerContext
    ) -> None:
        """
        验证分析请求的通用参数
        
        Args:
            request: 分析请求
            context: gRPC服务上下文
        """
        if not request.image:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("缺少图像数据")
            return
        
        if not request.user_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("缺少用户ID")
            return
            
        # 成功验证，保持默认OK状态
        # 注意：grpc.StatusCode.OK是默认值，不需要显式设置
    
    def AnalyzeFace(
        self, 
        request: look_service_pb2.FaceAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.FaceAnalysisResponse:
        """
        面色分析接口实现
        
        Args:
            request: 面色分析请求
            context: gRPC服务上下文
            
        Returns:
            面色分析响应
        """
        start_time = time.time()
        method_name = "AnalyzeFace"
        
        try:
            logger.info(
                "Received face analysis request", 
                user_id=request.user_id,
                analysis_type=look_service_pb2.AnalysisType.Name(request.analysis_type),
                save_result=request.save_result,
                image_size=len(request.image),
                metadata=dict(request.metadata)
            )
            
            # 验证请求
            if not request.image:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing image data")
                return look_service_pb2.FaceAnalysisResponse()
            
            if not request.user_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing user ID")
                return look_service_pb2.FaceAnalysisResponse()
            
            # 执行面色分析
            analysis_result = self.face_analyzer.analyze(
                image_data=request.image,
                user_id=request.user_id
            )
            
            # 保存分析结果
            analysis_id = self.analysis_repository.save_face_analysis(analysis_result)
            
            # 转换为响应对象
            response = self._convert_to_face_response(analysis_result, analysis_id)
            
            # 异步发送分析结果到小艾服务
            self._notify_xiaoai_async(
                user_id=request.user_id,
                analysis_type="face",
                analysis_id=analysis_id,
                analysis_result=analysis_result.tcm_analysis
            )
            
            # 记录成功
            REQUEST_COUNTER.labels(method=method_name, status="success").inc()
            REQUEST_LATENCY.labels(method=method_name).observe(time.time() - start_time)
            logger.info("Face analysis completed", analysis_id=analysis_id, user_id=request.user_id)
            
            return response
            
        except InvalidInputError as e:
            self._handle_error(context, e, grpc.StatusCode.INVALID_ARGUMENT, method_name)
        except ModelLoadingError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except ProcessingError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except DatabaseError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except Exception as e:
            self._handle_error(context, e, grpc.StatusCode.UNKNOWN, method_name)
    
    def AnalyzeBody(
        self, 
        request: look_service_pb2.BodyAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.BodyAnalysisResponse:
        """
        形体姿态分析接口实现
        
        Args:
            request: 形体分析请求
            context: gRPC服务上下文
            
        Returns:
            形体分析响应
        """
        start_time = time.time()
        method_name = "AnalyzeBody"
        
        try:
            logger.info(
                "Received body analysis request", 
                user_id=request.user_id,
                analysis_type=look_service_pb2.AnalysisType.Name(request.analysis_type),
                save_result=request.save_result,
                image_size=len(request.image),
                metadata=dict(request.metadata)
            )
            
            # 验证请求
            if not request.image:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing image data")
                return look_service_pb2.BodyAnalysisResponse()
            
            if not request.user_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing user ID")
                return look_service_pb2.BodyAnalysisResponse()
            
            # 执行形体分析
            analysis_result = self.body_analyzer.analyze(
                image_data=request.image,
                user_id=request.user_id
            )
            
            # 保存分析结果
            analysis_id = self.analysis_repository.save_body_analysis(analysis_result)
            
            # 转换为响应对象
            response = self._convert_to_body_response(analysis_result, analysis_id)
            
            # 异步发送分析结果到小艾服务
            self._notify_xiaoai_async(
                user_id=request.user_id,
                analysis_type="body",
                analysis_id=analysis_id,
                analysis_result=analysis_result.tcm_analysis
            )
            
            # 记录成功
            REQUEST_COUNTER.labels(method=method_name, status="success").inc()
            REQUEST_LATENCY.labels(method=method_name).observe(time.time() - start_time)
            logger.info("Body analysis completed", analysis_id=analysis_id, user_id=request.user_id)
            
            return response
            
        except InvalidInputError as e:
            self._handle_error(context, e, grpc.StatusCode.INVALID_ARGUMENT, method_name)
        except ModelLoadingError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except ProcessingError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except DatabaseError as e:
            self._handle_error(context, e, grpc.StatusCode.INTERNAL, method_name)
        except Exception as e:
            self._handle_error(context, e, grpc.StatusCode.UNKNOWN, method_name)
    
    def GetAnalysisHistory(
        self, 
        request: look_service_pb2.AnalysisHistoryRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.AnalysisHistoryResponse:
        """
        获取历史分析记录
        
        Args:
            request: 历史记录请求
            context: gRPC服务上下文
            
        Returns:
            历史记录响应
        """
        try:
            logger.info(
                "Received analysis history request", 
                user_id=request.user_id,
                analysis_type=request.analysis_type,
                limit=request.limit,
                start_time=request.start_time,
                end_time=request.end_time
            )
            
            # 验证请求
            if not request.user_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing user ID")
                return look_service_pb2.AnalysisHistoryResponse()
            
            if not request.analysis_type:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing analysis type")
                return look_service_pb2.AnalysisHistoryResponse()
            
            # TODO: 从存储库获取历史记录
            # 此处为模拟数据
            response = look_service_pb2.AnalysisHistoryResponse(
                total_count=5
            )
            
            # 添加模拟记录
            for i in range(3):
                record_id = str(uuid.uuid4())
                timestamp = int(time.time()) - i * 86400  # 每天一条记录
                
                record = look_service_pb2.AnalysisRecord(
                    analysis_id=record_id,
                    analysis_type=request.analysis_type,
                    timestamp=timestamp,
                    summary=f"{request.analysis_type}分析记录 #{i+1}",
                    thumbnail=b"Mock thumbnail data"  # 实际应该是真实图像的缩略图
                )
                
                response.records.append(record)
            
            logger.info(
                "Analysis history retrieved (mock)", 
                user_id=request.user_id,
                record_count=len(response.records)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Error retrieving analysis history", 
                error=str(e),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return look_service_pb2.AnalysisHistoryResponse()
    
    def CompareAnalysis(
        self, 
        request: look_service_pb2.CompareAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.CompareAnalysisResponse:
        """
        比较两次分析结果
        
        Args:
            request: 比较分析请求
            context: gRPC服务上下文
            
        Returns:
            比较分析响应
        """
        try:
            logger.info(
                "Received compare analysis request", 
                user_id=request.user_id,
                analysis_type=request.analysis_type,
                first_analysis_id=request.first_analysis_id,
                second_analysis_id=request.second_analysis_id
            )
            
            # 验证请求
            if not request.user_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing user ID")
                return look_service_pb2.CompareAnalysisResponse()
            
            if not request.analysis_type:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing analysis type")
                return look_service_pb2.CompareAnalysisResponse()
                
            if not request.first_analysis_id or not request.second_analysis_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Missing analysis IDs for comparison")
                return look_service_pb2.CompareAnalysisResponse()
            
            # TODO: 从存储库获取分析记录并比较
            # 此处为模拟数据
            response = look_service_pb2.CompareAnalysisResponse(
                comparison_summary="两次分析对比显示，舌象整体状态有所改善，舌色由淡红转为正常红润，舌苔由薄白转为均匀白苔，表明脾胃功能转好。"
            )
            
            # 添加特征比较
            response.feature_comparisons.append(look_service_pb2.FeatureComparison(
                feature_name="舌色",
                first_value="淡红",
                second_value="红润",
                change_percentage=15.5,
                change_direction="improved"
            ))
            
            response.feature_comparisons.append(look_service_pb2.FeatureComparison(
                feature_name="舌苔",
                first_value="薄白",
                second_value="均匀白苔",
                change_percentage=10.2,
                change_direction="improved"
            ))
            
            response.feature_comparisons.append(look_service_pb2.FeatureComparison(
                feature_name="舌体",
                first_value="略胖",
                second_value="略胖",
                change_percentage=0.0,
                change_direction="unchanged"
            ))
            
            # 添加改善项
            response.improvements.append("舌色改善")
            response.improvements.append("舌苔分布更均匀")
            
            # 添加未变项
            response.unchanged.append("舌体大小")
            
            logger.info(
                "Compare analysis completed (mock)", 
                user_id=request.user_id,
                first_analysis_id=request.first_analysis_id,
                second_analysis_id=request.second_analysis_id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Error comparing analysis", 
                error=str(e),
                user_id=request.user_id
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return look_service_pb2.CompareAnalysisResponse()
    
    def HealthCheck(
        self, 
        request: look_service_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.HealthCheckResponse:
        """
        健康检查接口
        
        Args:
            request: 健康检查请求
            context: gRPC服务上下文
            
        Returns:
            健康检查响应
        """
        try:
            logger.debug("Health check requested", include_details=request.include_details)
            
            # 检查面色分析器状态
            face_analyzer_status = self.face_analyzer is not None
            
            # 检查形体分析器状态
            body_analyzer_status = self.body_analyzer is not None
            
            # 检查存储库状态
            repository_status = True  # 由于SQLite是文件数据库，假定它始终可用
            
            # 检查小艾服务客户端状态
            xiaoai_client_status = self.xiaoai_client.check_connection()
            
            # 构建响应
            response = look_service_pb2.HealthCheckResponse(
                status=look_service_pb2.HealthCheckResponse.SERVING,
                version=self.config.get("server.version", "1.0.0"),
                face_analyzer_status=face_analyzer_status,
                body_analyzer_status=body_analyzer_status,
                repository_status=repository_status,
                xiaoai_service_status=xiaoai_client_status
            )
            
            # 如果任何关键组件不可用，服务状态为不健康
            if not (face_analyzer_status and body_analyzer_status and repository_status):
                response.status = look_service_pb2.HealthCheckResponse.NOT_SERVING
            
            return response
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Health check failed: {str(e)}")
            return look_service_pb2.HealthCheckResponse(
                status=look_service_pb2.HealthCheckResponse.NOT_SERVING
            )
    
    def _convert_to_face_response(self, result: FaceAnalysisResult, 
                                 analysis_id: str) -> look_service_pb2.FaceAnalysisResponse:
        """
        将面色分析结果转换为gRPC响应

        Args:
            result: 面色分析结果
            analysis_id: 分析ID

        Returns:
            面色分析响应对象
        """
        response = look_service_pb2.FaceAnalysisResponse(
            analysis_id=analysis_id,
            user_id=result.user_id,
            timestamp=result.timestamp,
            face_color=result.features.face_color.value,
            skin_moisture=result.features.skin_moisture.value,
            confidence=result.confidence,
            tcm_analysis=self._dict_to_struct(result.tcm_analysis)
        )
        
        if result.annotated_image:
            response.annotated_image = result.annotated_image
        
        return response
    
    def _convert_to_body_response(self, result: BodyAnalysisResult, 
                                 analysis_id: str) -> look_service_pb2.BodyAnalysisResponse:
        """
        将形体分析结果转换为gRPC响应

        Args:
            result: 形体分析结果
            analysis_id: 分析ID

        Returns:
            形体分析响应对象
        """
        response = look_service_pb2.BodyAnalysisResponse(
            analysis_id=analysis_id,
            user_id=result.user_id,
            timestamp=result.timestamp,
            body_shape=result.features.body_shape.value,
            posture=result.features.posture.value,
            confidence=result.confidence,
            tcm_analysis=self._dict_to_struct(result.tcm_analysis)
        )
        
        if result.annotated_image:
            response.annotated_image = result.annotated_image
        
        return response
    
    def _dict_to_struct(self, data: Dict[str, Any]) -> Any:
        """
        将字典转换为Protobuf结构

        Args:
            data: 字典数据

        Returns:
            Protobuf结构
        """
        # 简化实现，实际中应该使用 google.protobuf.Struct
        # 但为了避免太多依赖，这里直接返回字典
        # 在实际项目中，应该使用正确的转换方法
        return data
    
    def _handle_error(self, context, error, status_code, method_name):
        """
        处理服务错误

        Args:
            context: gRPC上下文
            error: 错误对象
            status_code: gRPC状态码
            method_name: 方法名称
        """
        details = str(error)
        logger.error(
            "服务错误",
            method=method_name,
            error=details,
            code=status_code.name
        )
        
        # 增加错误计数
        REQUEST_COUNTER.labels(method=method_name, status="error").inc()
        
        # 设置gRPC错误响应
        context.set_code(status_code)
        context.set_details(details)
        return look_service_pb2.Empty()
    
    def _notify_xiaoai_async(self, user_id: str, analysis_type: str, 
                           analysis_id: str, analysis_result: Dict[str, Any]) -> None:
        """
        异步通知小艾服务

        Args:
            user_id: 用户ID
            analysis_type: 分析类型
            analysis_id: 分析ID
            analysis_result: 分析结果
        """
        try:
            futures.ThreadPoolExecutor(max_workers=1).submit(
                self.xiaoai_client.notify_analysis_result,
                user_id=user_id,
                analysis_type=analysis_type,
                analysis_id=analysis_id,
                analysis_result=analysis_result
            )
        except Exception as e:
            logger.error(
                "通知小艾服务失败",
                error=str(e),
                user_id=user_id,
                analysis_id=analysis_id
            )
            # 失败不影响主流程 