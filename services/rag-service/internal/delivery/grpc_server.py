#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
gRPC服务器
提供高性能的RAG服务接口
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, AsyncIterator
import grpc
from grpc import aio
from loguru import logger

from ..container import Container


# 模拟的protobuf消息类（实际应该从生成的pb2文件导入）
class QueryRequest:
    def __init__(self, query: str, user_id: str, context: Dict[str, Any] = None):
        self.query = query
        self.user_id = user_id
        self.context = context or {}
        self.session_id = ""
        self.max_tokens = 1000
        self.temperature = 0.7
        self.stream = False


class QueryResponse:
    def __init__(self, request_id: str, answer: str, sources: List[Dict[str, Any]] = None):
        self.request_id = request_id
        self.answer = answer
        self.sources = sources or []
        self.confidence = 0.0
        self.processing_time = 0.0


class StreamChunk:
    def __init__(self, chunk: str, is_final: bool = False):
        self.chunk = chunk
        self.is_final = is_final
        self.timestamp = time.time()


class TCMAnalysisRequest:
    def __init__(self, symptoms: List[str], user_id: str):
        self.symptoms = symptoms
        self.user_id = user_id
        self.constitution_type = ""
        self.medical_history = []
        self.current_medications = []


class TCMAnalysisResponse:
    def __init__(self, request_id: str, syndrome_analysis: Dict[str, Any]):
        self.request_id = request_id
        self.syndrome_analysis = syndrome_analysis
        self.constitution_assessment = {}
        self.treatment_principles = []
        self.confidence = 0.0


class HealthRequest:
    def __init__(self):
        pass


class HealthResponse:
    def __init__(self, status: str, components: Dict[str, str]):
        self.status = status
        self.components = components
        self.version = "1.2.0"
        self.timestamp = time.time()


class RAGServicer:
    """RAG服务gRPC实现"""
    
    def __init__(self, container: Container):
        self.container = container
        logger.info("RAG gRPC服务器初始化完成")
    
    async def Query(self, request: QueryRequest, context: grpc.aio.ServicerContext) -> QueryResponse:
        """
        RAG查询
        
        Args:
            request: 查询请求
            context: gRPC上下文
            
        Returns:
            查询响应
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到gRPC查询请求: {request_id}")
            
            # 获取RAG服务
            rag_service = self.container.rag_service()
            
            # 执行查询
            result = await rag_service.query(
                query=request.query,
                user_id=request.user_id,
                context=request.context,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            processing_time = time.time() - start_time
            
            response = QueryResponse(
                request_id=request_id,
                answer=result.get("answer", ""),
                sources=result.get("sources", [])
            )
            response.confidence = result.get("confidence", 0.0)
            response.processing_time = processing_time
            
            logger.info(f"gRPC查询完成: {request_id}, 耗时: {processing_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"gRPC查询失败: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"查询失败: {str(e)}")
    
    async def QueryStream(
        self, 
        request: QueryRequest, 
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[StreamChunk]:
        """
        流式RAG查询
        
        Args:
            request: 查询请求
            context: gRPC上下文
            
        Yields:
            流式响应块
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到gRPC流式查询请求: {request_id}")
            
            # 获取RAG服务
            rag_service = self.container.rag_service()
            
            # 流式查询
            async for chunk in rag_service.query_stream(
                query=request.query,
                user_id=request.user_id,
                context=request.context,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            ):
                if context.cancelled():
                    logger.info(f"gRPC流式查询被取消: {request_id}")
                    break
                
                yield StreamChunk(chunk=chunk, is_final=False)
            
            # 发送结束标记
            yield StreamChunk(chunk="", is_final=True)
            
            logger.info(f"gRPC流式查询完成: {request_id}")
            
        except Exception as e:
            logger.error(f"gRPC流式查询失败: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"流式查询失败: {str(e)}")
    
    async def AnalyzeTCM(
        self, 
        request: TCMAnalysisRequest, 
        context: grpc.aio.ServicerContext
    ) -> TCMAnalysisResponse:
        """
        中医分析
        
        Args:
            request: 中医分析请求
            context: gRPC上下文
            
        Returns:
            中医分析响应
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到gRPC中医分析请求: {request_id}")
            
            # 获取中医辨证分析器
            syndrome_analyzer = self.container.syndrome_analyzer()
            
            # 执行辨证分析
            analysis_result = await syndrome_analyzer.analyze_symptoms(
                symptoms=request.symptoms,
                constitution_type=request.constitution_type,
                medical_history=request.medical_history
            )
            
            response = TCMAnalysisResponse(
                request_id=request_id,
                syndrome_analysis=analysis_result.get("syndrome_analysis", {})
            )
            response.constitution_assessment = analysis_result.get("constitution_assessment", {})
            response.treatment_principles = analysis_result.get("treatment_principles", [])
            response.confidence = analysis_result.get("confidence", 0.0)
            
            logger.info(f"gRPC中医分析完成: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"gRPC中医分析失败: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"中医分析失败: {str(e)}")
    
    async def HealthCheck(
        self, 
        request: HealthRequest, 
        context: grpc.aio.ServicerContext
    ) -> HealthResponse:
        """
        健康检查
        
        Args:
            request: 健康检查请求
            context: gRPC上下文
            
        Returns:
            健康检查响应
        """
        try:
            logger.debug("收到gRPC健康检查请求")
            
            # 检查核心组件状态
            components = {
                "container": "healthy" if self.container else "unhealthy",
                "vector_database": "healthy",  # 简化检查
                "embedding_service": "healthy",
                "generator": "healthy"
            }
            
            # 检查向量数据库连接
            try:
                vector_db = self.container.vector_database()
                if await vector_db.health_check():
                    components["vector_database"] = "healthy"
                else:
                    components["vector_database"] = "unhealthy"
            except Exception:
                components["vector_database"] = "unhealthy"
            
            overall_status = "healthy" if all(
                status == "healthy" for status in components.values()
            ) else "unhealthy"
            
            response = HealthResponse(
                status=overall_status,
                components=components
            )
            
            return response
            
        except Exception as e:
            logger.error(f"gRPC健康检查失败: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"健康检查失败: {str(e)}")


class RAGGRPCServer:
    """RAG gRPC服务器"""
    
    def __init__(self, container: Container):
        self.container = container
        self.server: Optional[aio.Server] = None
        self.servicer = RAGServicer(container)
        
    async def start(self, listen_addr: str = "[::]:50051"):
        """
        启动gRPC服务器
        
        Args:
            listen_addr: 监听地址
        """
        try:
            # 创建服务器
            self.server = aio.server()
            
            # 添加服务实现
            # 注意：这里需要根据实际的protobuf定义来注册服务
            # add_RAGServiceServicer_to_server(self.servicer, self.server)
            
            # 添加监听端口
            listen_port = self.server.add_insecure_port(listen_addr)
            
            # 启动服务器
            await self.server.start()
            
            logger.info(f"gRPC服务器启动成功，监听地址: {listen_addr}")
            logger.info(f"实际监听端口: {listen_port}")
            
        except Exception as e:
            logger.error(f"gRPC服务器启动失败: {e}")
            raise
    
    async def stop(self, grace: Optional[float] = None):
        """
        停止gRPC服务器
        
        Args:
            grace: 优雅关闭时间（秒）
        """
        if self.server:
            try:
                logger.info("正在停止gRPC服务器...")
                await self.server.stop(grace)
                logger.info("gRPC服务器已停止")
            except Exception as e:
                logger.error(f"停止gRPC服务器失败: {e}")
    
    async def wait_for_termination(self):
        """等待服务器终止"""
        if self.server:
            await self.server.wait_for_termination()


class GRPCInterceptor:
    """gRPC拦截器"""
    
    def __init__(self, metrics_collector=None):
        self.metrics_collector = metrics_collector
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """拦截一元调用"""
        start_time = time.time()
        method_name = client_call_details.method
        
        try:
            # 记录请求开始
            logger.debug(f"gRPC请求开始: {method_name}")
            
            # 执行实际调用
            response = await continuation(client_call_details, request)
            
            # 记录成功指标
            processing_time = time.time() - start_time
            if self.metrics_collector:
                await self.metrics_collector.record_histogram(
                    "grpc_request_duration_seconds",
                    processing_time,
                    {"method": method_name, "status": "success"}
                )
                await self.metrics_collector.increment_counter(
                    "grpc_requests_total",
                    {"method": method_name, "status": "success"}
                )
            
            logger.debug(f"gRPC请求完成: {method_name}, 耗时: {processing_time:.3f}s")
            return response
            
        except Exception as e:
            # 记录错误指标
            processing_time = time.time() - start_time
            if self.metrics_collector:
                await self.metrics_collector.record_histogram(
                    "grpc_request_duration_seconds",
                    processing_time,
                    {"method": method_name, "status": "error"}
                )
                await self.metrics_collector.increment_counter(
                    "grpc_requests_total",
                    {"method": method_name, "status": "error"}
                )
                await self.metrics_collector.increment_counter(
                    "grpc_request_errors_total",
                    {"method": method_name}
                )
            
            logger.error(f"gRPC请求失败: {method_name}, 错误: {e}")
            raise
    
    async def intercept_unary_stream(self, continuation, client_call_details, request):
        """拦截流式调用"""
        start_time = time.time()
        method_name = client_call_details.method
        
        try:
            logger.debug(f"gRPC流式请求开始: {method_name}")
            
            # 执行实际调用
            response_iterator = await continuation(client_call_details, request)
            
            # 包装响应迭代器以记录指标
            async def wrapped_iterator():
                chunk_count = 0
                try:
                    async for response in response_iterator:
                        chunk_count += 1
                        yield response
                    
                    # 记录成功指标
                    processing_time = time.time() - start_time
                    if self.metrics_collector:
                        await self.metrics_collector.record_histogram(
                            "grpc_stream_duration_seconds",
                            processing_time,
                            {"method": method_name, "status": "success"}
                        )
                        await self.metrics_collector.record_histogram(
                            "grpc_stream_chunks_total",
                            chunk_count,
                            {"method": method_name}
                        )
                    
                    logger.debug(f"gRPC流式请求完成: {method_name}, 块数: {chunk_count}, 耗时: {processing_time:.3f}s")
                    
                except Exception as e:
                    # 记录错误指标
                    processing_time = time.time() - start_time
                    if self.metrics_collector:
                        await self.metrics_collector.record_histogram(
                            "grpc_stream_duration_seconds",
                            processing_time,
                            {"method": method_name, "status": "error"}
                        )
                        await self.metrics_collector.increment_counter(
                            "grpc_stream_errors_total",
                            {"method": method_name}
                        )
                    
                    logger.error(f"gRPC流式请求失败: {method_name}, 错误: {e}")
                    raise
            
            return wrapped_iterator()
            
        except Exception as e:
            processing_time = time.time() - start_time
            if self.metrics_collector:
                await self.metrics_collector.record_histogram(
                    "grpc_stream_duration_seconds",
                    processing_time,
                    {"method": method_name, "status": "error"}
                )
                await self.metrics_collector.increment_counter(
                    "grpc_stream_errors_total",
                    {"method": method_name}
                )
            
            logger.error(f"gRPC流式请求失败: {method_name}, 错误: {e}")
            raise


async def create_grpc_server(container: Container) -> RAGGRPCServer:
    """
    创建gRPC服务器
    
    Args:
        container: 依赖注入容器
        
    Returns:
        gRPC服务器实例
    """
    try:
        # 创建服务器
        grpc_server = RAGGRPCServer(container)
        
        logger.info("gRPC服务器创建成功")
        return grpc_server
        
    except Exception as e:
        logger.error(f"创建gRPC服务器失败: {e}")
        raise


# 便捷函数
async def start_grpc_service(
    container: Container,
    listen_addr: str = "[::]:50051"
) -> RAGGRPCServer:
    """
    启动gRPC服务的便捷函数
    
    Args:
        container: 依赖注入容器
        listen_addr: 监听地址
        
    Returns:
        gRPC服务器实例
    """
    server = await create_grpc_server(container)
    await server.start(listen_addr)
    return server


# 示例protobuf定义（实际应该在单独的.proto文件中定义）
PROTO_DEFINITION = """
syntax = "proto3";

package rag;

service RAGService {
    // RAG查询
    rpc Query(QueryRequest) returns (QueryResponse);
    
    // 流式RAG查询
    rpc QueryStream(QueryRequest) returns (stream StreamChunk);
    
    // 中医分析
    rpc AnalyzeTCM(TCMAnalysisRequest) returns (TCMAnalysisResponse);
    
    // 健康检查
    rpc HealthCheck(HealthRequest) returns (HealthResponse);
}

message QueryRequest {
    string query = 1;
    string user_id = 2;
    map<string, string> context = 3;
    string session_id = 4;
    int32 max_tokens = 5;
    float temperature = 6;
    bool stream = 7;
}

message QueryResponse {
    string request_id = 1;
    string answer = 2;
    repeated Source sources = 3;
    float confidence = 4;
    float processing_time = 5;
    repeated string reasoning_chain = 6;
    map<string, string> metadata = 7;
}

message StreamChunk {
    string chunk = 1;
    bool is_final = 2;
    double timestamp = 3;
}

message Source {
    string content = 1;
    string title = 2;
    string source = 3;
    float score = 4;
    map<string, string> metadata = 5;
}

message TCMAnalysisRequest {
    repeated string symptoms = 1;
    string user_id = 2;
    string constitution_type = 3;
    repeated string medical_history = 4;
    repeated string current_medications = 5;
}

message TCMAnalysisResponse {
    string request_id = 1;
    map<string, string> syndrome_analysis = 2;
    map<string, string> constitution_assessment = 3;
    repeated string treatment_principles = 4;
    float confidence = 5;
}

message HealthRequest {
    // 空消息
}

message HealthResponse {
    string status = 1;
    map<string, string> components = 2;
    string version = 3;
    double timestamp = 4;
}
""" 