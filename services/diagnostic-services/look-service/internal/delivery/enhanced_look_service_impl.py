#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强的望诊服务实现

使用依赖注入容器和中间件系统的重构版本。
"""

import time
import uuid
import asyncio
from typing import Dict, List, Optional, Any

import grpc
from structlog import get_logger

from api.grpc import look_service_pb2, look_service_pb2_grpc
from internal.container.container import get_container
from internal.middleware.middleware import create_middleware_chain
from internal.service.notification_service import NotificationLevel
from internal.analysis.face_analyzer import FaceAnalysisResult
from internal.analysis.body_analyzer import BodyAnalysisResult
from internal.analysis.tongue_analyzer import TongueAnalysisResult
from pkg.utils.exceptions import (
    InvalidInputError, ProcessingError, 
    ResourceNotFoundError, AuthenticationError
)

logger = get_logger()


class EnhancedLookServiceServicer(look_service_pb2_grpc.LookServiceServicer):
    """
    增强的望诊服务实现
    
    使用依赖注入容器管理依赖，支持中间件链处理请求。
    """
    
    def __init__(self):
        self.container = get_container()
        self.middleware_chain = None
        self.initialized = False
        
    async def initialize(self):
        """异步初始化服务"""
        if self.initialized:
            return
            
        try:
            # 初始化容器
            await self.container.initialize()
            
            # 获取配置
            config = self.container.get("config", dict)
            
            # 创建中间件链
            metrics_service = self.container.get("metrics_service")
            middleware_config = config.get("middleware", {})
            self.middleware_chain = create_middleware_chain(middleware_config, metrics_service)
            
            self.initialized = True
            logger.info("增强的望诊服务初始化完成")
            
        except Exception as e:
            logger.error("增强的望诊服务初始化失败", error=str(e))
            raise
    
    async def _process_with_middleware(self, request, context, handler):
        """使用中间件处理请求"""
        if not self.initialized:
            await self.initialize()
            
        if self.middleware_chain:
            return await self.middleware_chain.process_request(request, context, handler)
        else:
            return await handler(request, context)
    
    async def AnalyzeTongue(
        self, 
        request: look_service_pb2.TongueAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.TongueAnalysisResponse:
        """舌象分析接口"""
        
        async def handler(req, ctx):
            return await self._handle_tongue_analysis(req, ctx)
        
        return await self._process_with_middleware(request, context, handler)
    
    async def _handle_tongue_analysis(
        self, 
        request: look_service_pb2.TongueAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.TongueAnalysisResponse:
        """处理舌象分析"""
        try:
            # 获取服务依赖
            tongue_analyzer = self.container.get("tongue_analyzer")
            analysis_repository = self.container.get("analysis_repository")
            cache_service = self.container.get("cache_service")
            notification_service = self.container.get("notification_service")
            metrics_service = self.container.get("metrics_service")
            
            # 验证请求
            self._validate_tongue_analysis_request(request)
            
            # 检查缓存
            cache_key = f"tongue_analysis:{request.user_id}:{hash(request.image)}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                logger.info("从缓存获取舌象分析结果", user_id=request.user_id, cache_key=cache_key)
                metrics_service.inc_counter("cache_hits_total", labels={"cache_type": "tongue_analysis"})
                return self._build_tongue_response_from_cache(cached_result)
            
            metrics_service.inc_counter("cache_misses_total", labels={"cache_type": "tongue_analysis"})
            
            # 执行分析
            with metrics_service.time_histogram("analysis_duration", labels={"analysis_type": "tongue"}):
                analysis_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    tongue_analyzer.analyze,
                    request.image,
                    request.user_id,
                    request.save_result
                )
            
            # 保存到缓存
            await cache_service.set(cache_key, analysis_result.to_dict(), ttl=3600)
            
            # 保存分析结果
            if request.save_result:
                await analysis_repository.save_tongue_analysis(analysis_result)
            
            # 发送通知
            await notification_service.notify(
                event_type="tongue_analysis_completed",
                level=NotificationLevel.INFO,
                title="舌象分析完成",
                message=f"用户 {request.user_id} 的舌象分析已完成",
                data={
                    "analysis_id": analysis_result.analysis_id,
                    "user_id": request.user_id,
                    "tongue_color": analysis_result.tongue_color.value,
                    "coating_color": analysis_result.coating_color.value
                },
                user_id=request.user_id
            )
            
            # 记录成功指标
            metrics_service.inc_counter(
                "analysis_total",
                labels={"analysis_type": "tongue", "status": "success"}
            )
            
            # 构建响应
            return self._build_tongue_response(analysis_result)
            
        except InvalidInputError as e:
            logger.warning("舌象分析请求参数无效", user_id=request.user_id, error=str(e))
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return look_service_pb2.TongueAnalysisResponse()
            
        except ProcessingError as e:
            logger.error("舌象分析处理失败", user_id=request.user_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("分析处理失败，请稍后重试")
            return look_service_pb2.TongueAnalysisResponse()
            
        except Exception as e:
            logger.error("舌象分析未知错误", user_id=request.user_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("内部服务错误")
            return look_service_pb2.TongueAnalysisResponse()
    
    async def AnalyzeFace(
        self, 
        request: look_service_pb2.FaceAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.FaceAnalysisResponse:
        """面色分析接口"""
        
        async def handler(req, ctx):
            return await self._handle_face_analysis(req, ctx)
        
        return await self._process_with_middleware(request, context, handler)
    
    async def _handle_face_analysis(
        self, 
        request: look_service_pb2.FaceAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.FaceAnalysisResponse:
        """处理面色分析"""
        try:
            # 获取服务依赖
            face_analyzer = self.container.get("face_analyzer")
            analysis_repository = self.container.get("analysis_repository")
            cache_service = self.container.get("cache_service")
            notification_service = self.container.get("notification_service")
            metrics_service = self.container.get("metrics_service")
            
            # 验证请求
            self._validate_face_analysis_request(request)
            
            # 检查缓存
            cache_key = f"face_analysis:{request.user_id}:{hash(request.image)}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                logger.info("从缓存获取面色分析结果", user_id=request.user_id)
                metrics_service.inc_counter("cache_hits_total", labels={"cache_type": "face_analysis"})
                return self._build_face_response_from_cache(cached_result)
            
            metrics_service.inc_counter("cache_misses_total", labels={"cache_type": "face_analysis"})
            
            # 执行分析
            with metrics_service.time_histogram("analysis_duration", labels={"analysis_type": "face"}):
                analysis_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    face_analyzer.analyze,
                    request.image,
                    request.user_id,
                    request.save_result
                )
            
            # 保存到缓存
            await cache_service.set(cache_key, analysis_result.to_dict(), ttl=3600)
            
            # 保存分析结果
            if request.save_result:
                await analysis_repository.save_face_analysis(analysis_result)
            
            # 发送通知
            await notification_service.notify(
                event_type="face_analysis_completed",
                level=NotificationLevel.INFO,
                title="面色分析完成",
                message=f"用户 {request.user_id} 的面色分析已完成",
                data={
                    "analysis_id": analysis_result.analysis_id,
                    "user_id": request.user_id,
                    "face_color": analysis_result.face_color.value
                },
                user_id=request.user_id
            )
            
            # 记录成功指标
            metrics_service.inc_counter(
                "analysis_total",
                labels={"analysis_type": "face", "status": "success"}
            )
            
            # 构建响应
            return self._build_face_response(analysis_result)
            
        except Exception as e:
            logger.error("面色分析失败", user_id=request.user_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("面色分析失败")
            return look_service_pb2.FaceAnalysisResponse()
    
    async def AnalyzeBody(
        self, 
        request: look_service_pb2.BodyAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.BodyAnalysisResponse:
        """形体分析接口"""
        
        async def handler(req, ctx):
            return await self._handle_body_analysis(req, ctx)
        
        return await self._process_with_middleware(request, context, handler)
    
    async def _handle_body_analysis(
        self, 
        request: look_service_pb2.BodyAnalysisRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.BodyAnalysisResponse:
        """处理形体分析"""
        try:
            # 获取服务依赖
            body_analyzer = self.container.get("body_analyzer")
            analysis_repository = self.container.get("analysis_repository")
            cache_service = self.container.get("cache_service")
            notification_service = self.container.get("notification_service")
            metrics_service = self.container.get("metrics_service")
            
            # 验证请求
            self._validate_body_analysis_request(request)
            
            # 检查缓存
            cache_key = f"body_analysis:{request.user_id}:{hash(request.image)}"
            cached_result = await cache_service.get(cache_key)
            
            if cached_result:
                logger.info("从缓存获取形体分析结果", user_id=request.user_id)
                metrics_service.inc_counter("cache_hits_total", labels={"cache_type": "body_analysis"})
                return self._build_body_response_from_cache(cached_result)
            
            metrics_service.inc_counter("cache_misses_total", labels={"cache_type": "body_analysis"})
            
            # 执行分析
            with metrics_service.time_histogram("analysis_duration", labels={"analysis_type": "body"}):
                analysis_result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    body_analyzer.analyze,
                    request.image,
                    request.user_id,
                    request.save_result
                )
            
            # 保存到缓存
            await cache_service.set(cache_key, analysis_result.to_dict(), ttl=3600)
            
            # 保存分析结果
            if request.save_result:
                await analysis_repository.save_body_analysis(analysis_result)
            
            # 发送通知
            await notification_service.notify(
                event_type="body_analysis_completed",
                level=NotificationLevel.INFO,
                title="形体分析完成",
                message=f"用户 {request.user_id} 的形体分析已完成",
                data={
                    "analysis_id": analysis_result.analysis_id,
                    "user_id": request.user_id,
                    "body_type": analysis_result.body_type.value
                },
                user_id=request.user_id
            )
            
            # 记录成功指标
            metrics_service.inc_counter(
                "analysis_total",
                labels={"analysis_type": "body", "status": "success"}
            )
            
            # 构建响应
            return self._build_body_response(analysis_result)
            
        except Exception as e:
            logger.error("形体分析失败", user_id=request.user_id, error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("形体分析失败")
            return look_service_pb2.BodyAnalysisResponse()
    
    async def HealthCheck(
        self, 
        request: look_service_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.HealthCheckResponse:
        """健康检查接口"""
        
        async def handler(req, ctx):
            return await self._handle_health_check(req, ctx)
        
        return await self._process_with_middleware(request, context, handler)
    
    async def _handle_health_check(
        self, 
        request: look_service_pb2.HealthCheckRequest, 
        context: grpc.ServicerContext
    ) -> look_service_pb2.HealthCheckResponse:
        """处理健康检查"""
        try:
            # 执行容器健康检查
            health_results = await self.container.health_check()
            
            # 检查所有组件状态
            overall_status = "healthy"
            component_statuses = {}
            
            for component, health in health_results.items():
                status = health.status
                component_statuses[component] = status
                
                if status != "healthy":
                    overall_status = "unhealthy"
            
            # 构建响应
            response = look_service_pb2.HealthCheckResponse(
                status=overall_status,
                timestamp=int(time.time()),
                version="1.0.0"
            )
            
            # 添加组件状态
            for component, status in component_statuses.items():
                component_health = look_service_pb2.ComponentHealth(
                    name=component,
                    status=status,
                    last_check=int(time.time())
                )
                response.components.append(component_health)
            
            logger.debug("健康检查完成", status=overall_status, components=len(component_statuses))
            return response
            
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("健康检查失败")
            return look_service_pb2.HealthCheckResponse(
                status="unhealthy",
                timestamp=int(time.time()),
                version="1.0.0"
            )
    
    def _validate_tongue_analysis_request(self, request):
        """验证舌象分析请求"""
        if not request.user_id:
            raise InvalidInputError("用户ID不能为空")
        
        if not request.image:
            raise InvalidInputError("图像数据不能为空")
        
        if len(request.image) > 10 * 1024 * 1024:  # 10MB
            raise InvalidInputError("图像大小不能超过10MB")
    
    def _validate_face_analysis_request(self, request):
        """验证面色分析请求"""
        if not request.user_id:
            raise InvalidInputError("用户ID不能为空")
        
        if not request.image:
            raise InvalidInputError("图像数据不能为空")
        
        if len(request.image) > 10 * 1024 * 1024:  # 10MB
            raise InvalidInputError("图像大小不能超过10MB")
    
    def _validate_body_analysis_request(self, request):
        """验证形体分析请求"""
        if not request.user_id:
            raise InvalidInputError("用户ID不能为空")
        
        if not request.image:
            raise InvalidInputError("图像数据不能为空")
        
        if len(request.image) > 10 * 1024 * 1024:  # 10MB
            raise InvalidInputError("图像大小不能超过10MB")
    
    def _build_tongue_response(self, result: TongueAnalysisResult) -> look_service_pb2.TongueAnalysisResponse:
        """构建舌象分析响应"""
        response = look_service_pb2.TongueAnalysisResponse(
            request_id=result.request_id,
            tongue_color=result.tongue_color.value,
            tongue_shape=result.tongue_shape.value,
            coating_color=result.coating_color.value,
            coating_distribution=result.coating_distribution,
            features=result.features,
            analysis_summary=result.analysis_summary,
            analysis_id=result.analysis_id,
            timestamp=result.timestamp
        )
        
        # 添加体质关联
        for constitution in result.body_constitution:
            response.body_constitution.append(look_service_pb2.ConstitutionCorrelation(
                constitution_type=constitution.constitution_type,
                confidence=constitution.confidence,
                description=constitution.description
            ))
        
        return response
    
    def _build_face_response(self, result: FaceAnalysisResult) -> look_service_pb2.FaceAnalysisResponse:
        """构建面色分析响应"""
        response = look_service_pb2.FaceAnalysisResponse(
            request_id=result.request_id,
            face_color=result.face_color.value,
            analysis_summary=result.analysis_summary,
            analysis_id=result.analysis_id,
            timestamp=result.timestamp
        )
        
        # 添加体质关联
        for constitution in result.body_constitution:
            response.body_constitution.append(look_service_pb2.ConstitutionCorrelation(
                constitution_type=constitution.constitution_type,
                confidence=constitution.confidence,
                description=constitution.description
            ))
        
        return response
    
    def _build_body_response(self, result: BodyAnalysisResult) -> look_service_pb2.BodyAnalysisResponse:
        """构建形体分析响应"""
        response = look_service_pb2.BodyAnalysisResponse(
            request_id=result.request_id,
            body_type=result.body_type.value,
            analysis_summary=result.analysis_summary,
            analysis_id=result.analysis_id,
            timestamp=result.timestamp
        )
        
        # 添加体质关联
        for constitution in result.body_constitution:
            response.body_constitution.append(look_service_pb2.ConstitutionCorrelation(
                constitution_type=constitution.constitution_type,
                confidence=constitution.confidence,
                description=constitution.description
            ))
        
        return response
    
    def _build_tongue_response_from_cache(self, cached_data: Dict) -> look_service_pb2.TongueAnalysisResponse:
        """从缓存数据构建舌象分析响应"""
        # 这里需要根据实际的缓存数据结构来实现
        # 简化实现
        return look_service_pb2.TongueAnalysisResponse()
    
    def _build_face_response_from_cache(self, cached_data: Dict) -> look_service_pb2.FaceAnalysisResponse:
        """从缓存数据构建面色分析响应"""
        # 这里需要根据实际的缓存数据结构来实现
        # 简化实现
        return look_service_pb2.FaceAnalysisResponse()
    
    def _build_body_response_from_cache(self, cached_data: Dict) -> look_service_pb2.BodyAnalysisResponse:
        """从缓存数据构建形体分析响应"""
        # 这里需要根据实际的缓存数据结构来实现
        # 简化实现
        return look_service_pb2.BodyAnalysisResponse() 