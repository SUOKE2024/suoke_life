"""
gRPC服务器实现

提供音频分析和中医诊断的gRPC接口服务。
"""

import asyncio
import time
from typing import Optional, Dict, Any
import uuid

import grpc
from grpc import aio
import structlog

from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..models.audio_models import AudioMetadata, AudioFormat, AnalysisRequest, AnalysisResponse
from ..models.tcm_models import TCMAnalysisRequest, TCMAnalysisResponse
from ..config.settings import get_settings
from ..utils.cache import AudioCache
from ..utils.performance import async_timer
from ..utils.logging import audit_logger, security_logger

logger = structlog.get_logger(__name__)


class ListenServiceGRPCServer:
    """索克生活闻诊服务gRPC服务器"""
    
    def __init__(
        self,
        audio_analyzer: Optional[AudioAnalyzer] = None,
        tcm_analyzer: Optional[TCMFeatureExtractor] = None,
        cache: Optional[AudioCache] = None,
    ):
        self.settings = get_settings()
        self.audio_analyzer = audio_analyzer or AudioAnalyzer()
        self.tcm_analyzer = tcm_analyzer or TCMFeatureExtractor()
        self.cache = cache or AudioCache()
        
        # 服务器状态
        self.server: Optional[aio.Server] = None
        self.is_running = False
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_processing_time": 0.0,
            "start_time": time.time(),
        }
        
        logger.info("gRPC服务器初始化完成")
    
    @async_timer
    async def AnalyzeAudio(self, request, context) -> AnalysisResponse:
        """
        分析音频接口
        
        Args:
            request: 音频分析请求
            context: gRPC上下文
            
        Returns:
            音频分析响应
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # 更新统计
        self.stats["total_requests"] += 1
        
        try:
            # 验证请求
            if not request.audio_data:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "音频数据不能为空")
            
            # 记录审计日志
            audit_logger.log_audio_analysis(
                user_id=getattr(request, 'user_id', None),
                audio_hash=self._hash_audio_data(request.audio_data),
                analysis_type=getattr(request, 'analysis_type', 'default'),
                success=False,  # 先设为False，成功后更新
                duration=0.0,
            )
            
            # 创建音频元数据
            metadata = AudioMetadata(
                sample_rate=getattr(request, 'sample_rate', 16000),
                channels=getattr(request, 'channels', 1),
                duration=len(request.audio_data) / (getattr(request, 'sample_rate', 16000) * getattr(request, 'channels', 1) * 2),  # 假设16位
                format=AudioFormat.WAV,
                file_size=len(request.audio_data),
            )
            
            # 创建分析请求
            analysis_request = AnalysisRequest(
                request_id=request_id,
                audio_data=request.audio_data,
                metadata=metadata,
                analysis_type=getattr(request, 'analysis_type', 'default'),
                enable_caching=getattr(request, 'enable_caching', True),
            )
            
            # 执行音频分析
            logger.info("开始音频分析", request_id=request_id, audio_size=len(request.audio_data))
            
            analysis_result = await self.audio_analyzer.analyze_audio(analysis_request)
            
            # 记录成功
            processing_time = time.time() - start_time
            self.stats["successful_requests"] += 1
            self.stats["total_processing_time"] += processing_time
            
            # 更新审计日志
            audit_logger.log_audio_analysis(
                user_id=getattr(request, 'user_id', None),
                audio_hash=self._hash_audio_data(request.audio_data),
                analysis_type=getattr(request, 'analysis_type', 'default'),
                success=True,
                duration=processing_time,
            )
            
            logger.info(
                "音频分析完成",
                request_id=request_id,
                processing_time=processing_time,
                success=analysis_result.success,
            )
            
            return self._convert_to_grpc_response(analysis_result)
            
        except Exception as e:
            # 记录错误
            processing_time = time.time() - start_time
            self.stats["failed_requests"] += 1
            
            logger.error(
                "音频分析失败",
                request_id=request_id,
                error=str(e),
                processing_time=processing_time,
                exc_info=True,
            )
            
            # 记录安全日志（如果是可疑错误）
            if "permission" in str(e).lower() or "unauthorized" in str(e).lower():
                security_logger.log_suspicious_activity(
                    activity_type="unauthorized_audio_analysis",
                    description=str(e),
                    user_id=getattr(request, 'user_id', None),
                )
            
            await context.abort(grpc.StatusCode.INTERNAL, f"音频分析失败: {str(e)}")
    
    @async_timer
    async def AnalyzeTCM(self, request, context) -> TCMAnalysisResponse:
        """
        中医分析接口
        
        Args:
            request: 中医分析请求
            context: gRPC上下文
            
        Returns:
            中医分析响应
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # 验证请求
            if not request.audio_data:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "音频数据不能为空")
            
            # 首先进行音频特征提取
            metadata = AudioMetadata(
                sample_rate=getattr(request, 'sample_rate', 16000),
                channels=getattr(request, 'channels', 1),
                duration=len(request.audio_data) / (getattr(request, 'sample_rate', 16000) * getattr(request, 'channels', 1) * 2),
                format=AudioFormat.WAV,
                file_size=len(request.audio_data),
            )
            
            analysis_request = AnalysisRequest(
                request_id=request_id,
                audio_data=request.audio_data,
                metadata=metadata,
                analysis_type="tcm",
            )
            
            # 提取音频特征
            logger.info("开始中医分析", request_id=request_id)
            
            audio_result = await self.audio_analyzer.analyze_audio(analysis_request)
            
            if not audio_result.success or not audio_result.voice_features:
                await context.abort(grpc.StatusCode.INTERNAL, "音频特征提取失败")
            
            # 执行中医分析
            tcm_diagnosis = await self.tcm_analyzer.analyze_tcm_features(
                audio_result.voice_features,
                audio_metadata=metadata.model_dump(),
            )
            
            # 创建响应
            processing_time = time.time() - start_time
            
            response = TCMAnalysisResponse(
                request_id=request_id,
                success=True,
                diagnosis=tcm_diagnosis,
                processing_time=processing_time,
            )
            
            # 记录审计日志
            audit_logger.log_tcm_diagnosis(
                user_id=getattr(request, 'user_id', None),
                diagnosis_id=tcm_diagnosis.diagnosis_id,
                constitution_type=tcm_diagnosis.constitution_type,
                emotion_state=tcm_diagnosis.emotion_state,
                confidence_score=tcm_diagnosis.confidence_score,
            )
            
            logger.info(
                "中医分析完成",
                request_id=request_id,
                processing_time=processing_time,
                constitution=tcm_diagnosis.constitution_type,
                emotion=tcm_diagnosis.emotion_state,
            )
            
            return self._convert_to_grpc_tcm_response(response)
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            logger.error(
                "中医分析失败",
                request_id=request_id,
                error=str(e),
                processing_time=processing_time,
                exc_info=True,
            )
            
            await context.abort(grpc.StatusCode.INTERNAL, f"中医分析失败: {str(e)}")
    
    async def GetServiceHealth(self, request, context):
        """
        健康检查接口
        
        Args:
            request: 健康检查请求
            context: gRPC上下文
            
        Returns:
            健康状态响应
        """
        try:
            # 检查各组件状态
            health_status = await self._check_service_health()
            
            return {
                "status": "SERVING" if health_status["healthy"] else "NOT_SERVING",
                "details": health_status,
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error("健康检查失败", error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, f"健康检查失败: {str(e)}")
    
    async def GetServiceStats(self, request, context):
        """
        获取服务统计信息
        
        Args:
            request: 统计请求
            context: gRPC上下文
            
        Returns:
            统计信息响应
        """
        try:
            uptime = time.time() - self.stats["start_time"]
            avg_processing_time = (
                self.stats["total_processing_time"] / self.stats["successful_requests"]
                if self.stats["successful_requests"] > 0 else 0.0
            )
            
            stats = {
                **self.stats,
                "uptime": uptime,
                "average_processing_time": avg_processing_time,
                "success_rate": (
                    self.stats["successful_requests"] / self.stats["total_requests"]
                    if self.stats["total_requests"] > 0 else 0.0
                ),
                "requests_per_second": self.stats["total_requests"] / uptime if uptime > 0 else 0.0,
            }
            
            # 添加缓存统计
            cache_stats = await self.cache.get_cache_stats()
            stats["cache"] = cache_stats
            
            # 添加分析器统计
            analyzer_stats = await self.audio_analyzer.get_analysis_stats()
            stats["audio_analyzer"] = analyzer_stats
            
            tcm_stats = await self.tcm_analyzer.get_analysis_stats()
            stats["tcm_analyzer"] = tcm_stats
            
            return {
                "stats": stats,
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error("获取统计信息失败", error=str(e))
            await context.abort(grpc.StatusCode.INTERNAL, f"获取统计信息失败: {str(e)}")
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 50051) -> None:
        """启动gRPC服务器"""
        if self.is_running:
            logger.warning("gRPC服务器已在运行")
            return
        
        try:
            # 创建服务器
            self.server = aio.server()
            
            # 添加服务
            # 这里需要根据实际的protobuf定义来添加服务
            # add_ListenServiceServicer_to_server(self, self.server)
            
            # 添加端口
            listen_addr = f"{host}:{port}"
            self.server.add_insecure_port(listen_addr)
            
            # 启动服务器
            await self.server.start()
            self.is_running = True
            
            logger.info("gRPC服务器已启动", address=listen_addr)
            
            # 等待服务器停止
            await self.server.wait_for_termination()
            
        except Exception as e:
            logger.error("gRPC服务器启动失败", error=str(e))
            raise
        finally:
            self.is_running = False
    
    async def stop_server(self, grace_period: float = 5.0) -> None:
        """停止gRPC服务器"""
        if not self.is_running or not self.server:
            return
        
        logger.info("正在停止gRPC服务器", grace_period=grace_period)
        
        try:
            await self.server.stop(grace_period)
            self.is_running = False
            logger.info("gRPC服务器已停止")
        except Exception as e:
            logger.error("停止gRPC服务器失败", error=str(e))
    
    def _hash_audio_data(self, audio_data: bytes) -> str:
        """计算音频数据哈希"""
        import hashlib
        return hashlib.sha256(audio_data).hexdigest()[:16]
    
    def _convert_to_grpc_response(self, analysis_result: AnalysisResponse) -> Any:
        """转换为gRPC响应格式"""
        # 这里需要根据实际的protobuf定义来转换
        # 暂时返回字典格式
        return {
            "request_id": analysis_result.request_id,
            "success": analysis_result.success,
            "voice_features": analysis_result.voice_features.model_dump() if analysis_result.voice_features else None,
            "processing_time": analysis_result.processing_time,
            "error_message": analysis_result.error_message,
            "timestamp": analysis_result.timestamp.isoformat() if analysis_result.timestamp else None,
        }
    
    def _convert_to_grpc_tcm_response(self, tcm_response: TCMAnalysisResponse) -> Any:
        """转换为gRPC中医分析响应格式"""
        # 这里需要根据实际的protobuf定义来转换
        return {
            "request_id": tcm_response.request_id,
            "success": tcm_response.success,
            "diagnosis": tcm_response.diagnosis.model_dump() if tcm_response.diagnosis else None,
            "processing_time": tcm_response.processing_time,
            "error_message": tcm_response.error_message,
            "timestamp": tcm_response.timestamp.isoformat(),
        }
    
    async def _check_service_health(self) -> Dict[str, Any]:
        """检查服务健康状态"""
        health_checks = {}
        overall_healthy = True
        
        try:
            # 检查音频分析器
            analyzer_stats = await self.audio_analyzer.get_analysis_stats()
            health_checks["audio_analyzer"] = {
                "healthy": True,
                "stats": analyzer_stats,
            }
        except Exception as e:
            health_checks["audio_analyzer"] = {
                "healthy": False,
                "error": str(e),
            }
            overall_healthy = False
        
        try:
            # 检查中医分析器
            tcm_stats = await self.tcm_analyzer.get_analysis_stats()
            health_checks["tcm_analyzer"] = {
                "healthy": True,
                "stats": tcm_stats,
            }
        except Exception as e:
            health_checks["tcm_analyzer"] = {
                "healthy": False,
                "error": str(e),
            }
            overall_healthy = False
        
        try:
            # 检查缓存
            cache_stats = await self.cache.get_cache_stats()
            health_checks["cache"] = {
                "healthy": True,
                "stats": cache_stats,
            }
        except Exception as e:
            health_checks["cache"] = {
                "healthy": False,
                "error": str(e),
            }
            overall_healthy = False
        
        return {
            "healthy": overall_healthy,
            "components": health_checks,
            "uptime": time.time() - self.stats["start_time"],
            "total_requests": self.stats["total_requests"],
        }


# gRPC服务器工厂函数
async def create_grpc_server(
    host: str = "0.0.0.0",
    port: int = 50051,
    **kwargs
) -> ListenServiceGRPCServer:
    """
    创建并配置gRPC服务器
    
    Args:
        host: 监听主机
        port: 监听端口
        **kwargs: 其他配置参数
        
    Returns:
        配置好的gRPC服务器实例
    """
    server = ListenServiceGRPCServer(**kwargs)
    
    # 可以在这里添加更多的配置
    
    return server 