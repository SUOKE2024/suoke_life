"""
gRPC API 接口模块

提供音频分析和中医诊断的gRPC接口。
"""

import asyncio
import time
from typing import AsyncIterator

import grpc
import structlog
from grpc import aio

from ..config.settings import get_settings
from ..core.audio_analyzer import AudioAnalyzer
from ..core.tcm_analyzer import TCMFeatureExtractor
from ..utils.cache import get_cache
from ..utils.performance import async_timer, get_performance_monitor
from ..utils.validation import validate_comprehensive_request

logger = structlog.get_logger(__name__)

# 全局组件
settings = get_settings()
audio_analyzer = AudioAnalyzer()
tcm_analyzer = TCMFeatureExtractor()
cache = get_cache()
performance_monitor = get_performance_monitor()


# gRPC服务实现
class ListenServicer:
    """Listen Service gRPC服务实现"""

    @async_timer
    async def AnalyzeAudio(self, request, context):
        """分析音频"""
        try:
            # 验证请求
            request_data = {
                "file_path": request.file_path,
                "analysis_type": request.analysis_type,
                "user_id": request.user_id
            }
            validate_comprehensive_request(request_data)
            
            # 检查缓存
            cache_key = cache.generate_key(request.file_path, request.analysis_type)
            cached_result = await cache.get(cache_key)
            
            if cached_result:
                logger.info("使用缓存结果", cache_key=cache_key)
                return self._create_audio_response(cached_result)
            
            # 执行分析
            start_time = time.time()
            
            # 基础音频分析
            audio_features = await audio_analyzer.extract_features(request.file_path)
            
            result_data = {
                "request_id": request.request_id,
                "file_path": request.file_path,
                "analysis_type": request.analysis_type,
                "audio_features": audio_features,
                "timestamp": time.time(),
                "processing_time": time.time() - start_time,
                "status": "success"
            }
            
            # 根据分析类型执行不同的分析
            if request.analysis_type in ["tcm", "comprehensive"]:
                tcm_features = await tcm_analyzer.extract_features(request.file_path)
                result_data["tcm_features"] = tcm_features
            
            # 缓存结果
            await cache.set(cache_key, result_data, ttl=3600)
            
            # 记录性能指标
            performance_monitor.record_audio_analysis(
                analysis_type=request.analysis_type,
                duration=result_data["processing_time"]
            )
            
            logger.info(
                "gRPC音频分析完成",
                request_id=request.request_id,
                analysis_type=request.analysis_type,
                processing_time=result_data["processing_time"]
            )
            
            return self._create_audio_response(result_data)
            
        except Exception as e:
            logger.error("gRPC音频分析失败", error=str(e), request_id=request.request_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self._create_error_response(str(e))

    @async_timer
    async def TCMDiagnose(self, request, context):
        """中医诊断"""
        try:
            # 验证请求
            request_data = {
                "file_path": request.file_path,
                "user_id": request.user_id,
                "constitution_type": request.constitution_type
            }
            validate_comprehensive_request(request_data)
            
            # 检查缓存
            cache_key = cache.generate_key("tcm_diagnose", request.file_path, request.constitution_type)
            cached_result = await cache.get(cache_key)
            
            if cached_result:
                logger.info("使用缓存的中医诊断结果", cache_key=cache_key)
                return self._create_tcm_response(cached_result)
            
            # 执行中医诊断
            start_time = time.time()
            
            diagnosis = await tcm_analyzer.diagnose(
                file_path=request.file_path,
                constitution_type=request.constitution_type,
                symptoms=list(request.symptoms) if request.symptoms else [],
                context=request.context if request.context else {}
            )
            
            diagnosis_data = diagnosis.dict()
            diagnosis_data["request_id"] = request.request_id
            diagnosis_data["processing_time"] = time.time() - start_time
            
            # 缓存结果
            await cache.set(cache_key, diagnosis_data, ttl=1800)
            
            logger.info(
                "gRPC中医诊断完成",
                request_id=request.request_id,
                constitution_type=request.constitution_type,
                processing_time=diagnosis_data["processing_time"]
            )
            
            return self._create_tcm_response(diagnosis_data)
            
        except Exception as e:
            logger.error("gRPC中医诊断失败", error=str(e), request_id=request.request_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self._create_error_response(str(e))

    async def BatchAnalyze(self, request, context):
        """批量分析音频"""
        try:
            # 验证批量请求
            if len(request.file_paths) > 10:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("批量分析最多支持10个文件")
                return
            
            total_files = len(request.file_paths)
            
            for i, file_path in enumerate(request.file_paths):
                try:
                    # 分析单个文件
                    audio_features = await audio_analyzer.extract_features(file_path)
                    
                    result_data = {
                        "file_path": file_path,
                        "status": "success",
                        "audio_features": audio_features,
                        "progress": (i + 1) / total_files
                    }
                    
                    if request.analysis_type in ["tcm", "comprehensive"]:
                        tcm_features = await tcm_analyzer.extract_features(file_path)
                        result_data["tcm_features"] = tcm_features
                    
                    # 流式返回结果
                    yield self._create_batch_response(result_data)
                    
                    logger.info(f"批量分析进度 {i+1}/{total_files}", file_path=file_path)
                    
                except Exception as e:
                    logger.error(f"文件分析失败 {i+1}/{total_files}", file_path=file_path, error=str(e))
                    
                    error_result = {
                        "file_path": file_path,
                        "status": "failed",
                        "error": str(e),
                        "progress": (i + 1) / total_files
                    }
                    
                    yield self._create_batch_response(error_result)
            
            logger.info("gRPC批量分析完成", request_id=request.request_id, total_files=total_files)
            
        except Exception as e:
            logger.error("gRPC批量分析失败", error=str(e), request_id=request.request_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    async def GetHealth(self, request, context):
        """健康检查"""
        try:
            health_data = {
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0",
                "service": "listen-service"
            }
            
            return self._create_health_response(health_data)
            
        except Exception as e:
            logger.error("gRPC健康检查失败", error=str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return self._create_error_response(str(e))

    def _create_audio_response(self, data):
        """创建音频分析响应"""
        # 这里需要根据实际的protobuf定义来创建响应
        # 暂时返回字典格式
        return {
            "request_id": data.get("request_id", ""),
            "status": data.get("status", "success"),
            "audio_features": data.get("audio_features", {}),
            "tcm_features": data.get("tcm_features", {}),
            "processing_time": data.get("processing_time", 0.0),
            "timestamp": data.get("timestamp", time.time())
        }

    def _create_tcm_response(self, data):
        """创建中医诊断响应"""
        return {
            "request_id": data.get("request_id", ""),
            "constitution_type": data.get("constitution_type", ""),
            "emotion_state": data.get("emotion_state", ""),
            "voice_features": data.get("voice_features", {}),
            "diagnosis_result": data.get("diagnosis_result", {}),
            "recommendations": data.get("recommendations", []),
            "confidence_score": data.get("confidence_score", 0.0),
            "processing_time": data.get("processing_time", 0.0)
        }

    def _create_batch_response(self, data):
        """创建批量分析响应"""
        return {
            "file_path": data.get("file_path", ""),
            "status": data.get("status", ""),
            "progress": data.get("progress", 0.0),
            "audio_features": data.get("audio_features", {}),
            "tcm_features": data.get("tcm_features", {}),
            "error": data.get("error", "")
        }

    def _create_health_response(self, data):
        """创建健康检查响应"""
        return {
            "status": data.get("status", "healthy"),
            "timestamp": data.get("timestamp", time.time()),
            "version": data.get("version", "1.0.0"),
            "service": data.get("service", "listen-service")
        }

    def _create_error_response(self, error_message):
        """创建错误响应"""
        return {
            "error": error_message,
            "timestamp": time.time()
        }


class ListenServiceServer:
    """Listen Service gRPC服务器"""

    def __init__(self, port: int = 50051):
        self.port = port
        self.server = None
        self.servicer = ListenServicer()

    async def start(self):
        """启动gRPC服务器"""
        try:
            self.server = aio.server()
            
            # 添加服务
            # listen_pb2_grpc.add_ListenServiceServicer_to_server(self.servicer, self.server)
            
            # 添加端口
            listen_port = f'[::]:{self.port}'
            self.server.add_insecure_port(listen_port)
            
            # 启动服务器
            await self.server.start()
            
            logger.info("gRPC服务器启动", port=self.port)
            
            # 等待终止
            await self.server.wait_for_termination()
            
        except Exception as e:
            logger.error("gRPC服务器启动失败", error=str(e))
            raise

    async def stop(self):
        """停止gRPC服务器"""
        if self.server:
            await self.server.stop(grace=5)
            logger.info("gRPC服务器已停止")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


# gRPC客户端
class ListenServiceClient:
    """Listen Service gRPC客户端"""

    def __init__(self, server_address: str = "localhost:50051"):
        self.server_address = server_address
        self.channel = None
        self.stub = None

    async def connect(self):
        """连接到gRPC服务器"""
        try:
            self.channel = aio.insecure_channel(self.server_address)
            # self.stub = listen_pb2_grpc.ListenServiceStub(self.channel)
            
            logger.info("gRPC客户端连接成功", server=self.server_address)
            
        except Exception as e:
            logger.error("gRPC客户端连接失败", error=str(e))
            raise

    async def disconnect(self):
        """断开连接"""
        if self.channel:
            await self.channel.close()
            logger.info("gRPC客户端连接已关闭")

    async def analyze_audio(self, file_path: str, analysis_type: str, user_id: str, request_id: str = None):
        """分析音频"""
        try:
            if not self.stub:
                await self.connect()
            
            # 创建请求
            request = {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "user_id": user_id,
                "request_id": request_id or f"req_{int(time.time())}"
            }
            
            # 发送请求
            response = await self.stub.AnalyzeAudio(request)
            
            logger.info("gRPC音频分析请求完成", request_id=request["request_id"])
            
            return response
            
        except Exception as e:
            logger.error("gRPC音频分析请求失败", error=str(e))
            raise

    async def tcm_diagnose(self, file_path: str, constitution_type: str, user_id: str, 
                          symptoms: list = None, context: dict = None, request_id: str = None):
        """中医诊断"""
        try:
            if not self.stub:
                await self.connect()
            
            # 创建请求
            request = {
                "file_path": file_path,
                "constitution_type": constitution_type,
                "user_id": user_id,
                "symptoms": symptoms or [],
                "context": context or {},
                "request_id": request_id or f"req_{int(time.time())}"
            }
            
            # 发送请求
            response = await self.stub.TCMDiagnose(request)
            
            logger.info("gRPC中医诊断请求完成", request_id=request["request_id"])
            
            return response
            
        except Exception as e:
            logger.error("gRPC中医诊断请求失败", error=str(e))
            raise

    async def batch_analyze(self, file_paths: list, analysis_type: str, user_id: str, request_id: str = None):
        """批量分析"""
        try:
            if not self.stub:
                await self.connect()
            
            # 创建请求
            request = {
                "file_paths": file_paths,
                "analysis_type": analysis_type,
                "user_id": user_id,
                "request_id": request_id or f"req_{int(time.time())}"
            }
            
            # 发送流式请求
            response_stream = self.stub.BatchAnalyze(request)
            
            results = []
            async for response in response_stream:
                results.append(response)
                logger.info(f"批量分析进度: {response.progress:.2%}")
            
            logger.info("gRPC批量分析完成", request_id=request["request_id"], total_results=len(results))
            
            return results
            
        except Exception as e:
            logger.error("gRPC批量分析失败", error=str(e))
            raise

    async def get_health(self):
        """健康检查"""
        try:
            if not self.stub:
                await self.connect()
            
            response = await self.stub.GetHealth({})
            
            logger.info("gRPC健康检查完成", status=response.status)
            
            return response
            
        except Exception as e:
            logger.error("gRPC健康检查失败", error=str(e))
            raise

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


# 工具函数
async def create_grpc_server(port: int = 50051) -> ListenServiceServer:
    """创建gRPC服务器"""
    return ListenServiceServer(port)


async def create_grpc_client(server_address: str = "localhost:50051") -> ListenServiceClient:
    """创建gRPC客户端"""
    return ListenServiceClient(server_address)


# 启动脚本
async def main():
    """主函数"""
    server = await create_grpc_server()
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())