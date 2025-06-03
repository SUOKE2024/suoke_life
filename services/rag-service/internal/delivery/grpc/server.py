#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
gRPC 服务实现
"""

import time
from typing import Dict, Any, List
import grpc
from loguru import logger

# 以下导入语句在proto文件编译后需要替换为实际的导入
# import suoke.rag.rag_service_pb2 as rag_pb2
# import suoke.rag.rag_service_pb2_grpc as rag_pb2_grpc

from ...service.rag_service import RagService
from ...model.document import Document, DocumentReference

class RagServicer:
    """
    RAG 服务的 gRPC 实现
    """
    
    def __init__(self, config: Dict[str, Any], rag_service: RagService):
        """
        初始化 gRPC 服务
        
        Args:
            config: 配置信息
            rag_service: RAG 服务实例
        """
        self.config = config
        self.rag_service = rag_service
    
    async def Retrieve(self, request, context):
        """
        实现检索 RPC
        
        Args:
            request: 检索请求
            context: gRPC 上下文
            
        Returns:
            检索响应
        """
        try:
            # 从请求中提取参数
            query = request.query
            top_k = request.top_k
            score_threshold = request.score_threshold
            collection_names = list(request.collection_names) if request.collection_names else None
            rerank = request.rerank
            user_id = request.user_id if request.user_id else None
            
            # 构建元数据过滤条件
            metadata_filter = {}
            if request.metadata_filter:
                for key, value in request.metadata_filter.items():
                    metadata_filter[key] = value
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"Retrieve request: query='{query}', top_k={top_k}, user_id={user_id}")
            
            # 调用服务执行检索
            result = await self.rag_service.retrieve(
                query=query,
                top_k=top_k,
                collection_names=collection_names,
                metadata_filter=metadata_filter,
                score_threshold=score_threshold,
                rerank=rerank,
                user_id=user_id
            )
            
            # 构建响应
            response = self._build_retrieve_response(result.documents, result.latency_ms)
            
            logger.info(f"Retrieve completed in {time.time() - start_time:.3f}s, found {len(result.documents)} documents")
            return response
            
        except Exception as e:
            logger.error(f"Error in Retrieve RPC: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def Generate(self, request, context):
        """
        实现生成 RPC
        
        Args:
            request: 生成请求
            context: gRPC 上下文
            
        Returns:
            生成响应
        """
        try:
            # 从请求中提取参数
            query = request.query
            system_prompt = request.system_prompt if request.system_prompt else None
            user_id = request.user_id if request.user_id else None
            
            # 解析上下文文档
            context_documents = [
                self._parse_document(doc) for doc in request.context_documents
            ]
            
            # 解析生成参数
            generation_params = {}
            if request.generation_params:
                for key, value in request.generation_params.items():
                    generation_params[key] = value
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"Generate request: query='{query}', docs={len(context_documents)}, user_id={user_id}")
            
            # 调用服务执行生成
            result = await self.rag_service.generate(
                query=query,
                context_documents=context_documents,
                system_prompt=system_prompt,
                generation_params=generation_params,
                user_id=user_id
            )
            
            # 构建响应
            response = self._build_generate_response(
                result.answer, 
                result.references, 
                result.latency_ms
            )
            
            logger.info(f"Generate completed in {time.time() - start_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in Generate RPC: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def Query(self, request, context):
        """
        实现查询 RPC (检索+生成)
        
        Args:
            request: 查询请求
            context: gRPC 上下文
            
        Returns:
            查询响应
        """
        try:
            # 从请求中提取参数
            query = request.query
            top_k = request.top_k
            system_prompt = request.system_prompt if request.system_prompt else None
            collection_names = list(request.collection_names) if request.collection_names else None
            user_id = request.user_id if request.user_id else None
            
            # 解析生成参数
            generation_params = {}
            if request.generation_params:
                for key, value in request.generation_params.items():
                    generation_params[key] = value
            
            # 解析元数据过滤
            metadata_filter = {}
            if request.metadata_filter:
                for key, value in request.metadata_filter.items():
                    metadata_filter[key] = value
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"Query request: query='{query}', top_k={top_k}, user_id={user_id}")
            
            # 调用服务执行查询
            result = await self.rag_service.query(
                query=query,
                top_k=top_k,
                system_prompt=system_prompt,
                collection_names=collection_names,
                generation_params=generation_params,
                metadata_filter=metadata_filter,
                user_id=user_id
            )
            
            # 构建响应
            response = self._build_query_response(
                result.answer,
                result.references,
                result.retrieval_latency_ms,
                result.generation_latency_ms,
                result.total_latency_ms
            )
            
            logger.info(f"Query completed in {time.time() - start_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in Query RPC: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def StreamQuery(self, request, context):
        """
        实现流式查询 RPC
        
        Args:
            request: 查询请求
            context: gRPC 上下文
            
        Yields:
            流式响应
        """
        try:
            # 从请求中提取参数
            query = request.query
            top_k = request.top_k
            system_prompt = request.system_prompt if request.system_prompt else None
            collection_names = list(request.collection_names) if request.collection_names else None
            user_id = request.user_id if request.user_id else None
            
            # 解析生成参数
            generation_params = {}
            if request.generation_params:
                for key, value in request.generation_params.items():
                    generation_params[key] = value
            
            # 解析元数据过滤
            metadata_filter = {}
            if request.metadata_filter:
                for key, value in request.metadata_filter.items():
                    metadata_filter[key] = value
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"StreamQuery request: query='{query}', top_k={top_k}, user_id={user_id}")
            
            # 调用服务执行流式查询
            async for answer_fragment, is_final, references in self.rag_service.stream_query(
                query=query,
                top_k=top_k,
                system_prompt=system_prompt,
                collection_names=collection_names,
                generation_params=generation_params,
                metadata_filter=metadata_filter,
                user_id=user_id
            ):
                # 构建流式响应
                response = self._build_stream_response(answer_fragment, is_final, references)
                yield response
            
            logger.info(f"StreamQuery completed in {time.time() - start_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error in StreamQuery RPC: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def AddDocument(self, request, context):
        """
        实现添加文档 RPC
        
        Args:
            request: 添加文档请求
            context: gRPC 上下文
            
        Returns:
            添加文档响应
        """
        try:
            # 解析文档
            document = self._parse_document(request.document)
            collection_name = request.collection_name
            reindex = request.reindex
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"AddDocument request: collection={collection_name}, reindex={reindex}")
            
            # 调用服务添加文档
            document_id = await self.rag_service.add_document(
                document=document,
                collection_name=collection_name,
                reindex=reindex
            )
            
            # 构建响应
            response = self._build_add_document_response(document_id, True, "Document added successfully")
            
            logger.info(f"AddDocument completed in {time.time() - start_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in AddDocument RPC: {str(e)}")
            response = self._build_add_document_response(
                "", False, f"Failed to add document: {str(e)}"
            )
            return response
    
    async def DeleteDocument(self, request, context):
        """
        实现删除文档 RPC
        
        Args:
            request: 删除文档请求
            context: gRPC 上下文
            
        Returns:
            删除文档响应
        """
        try:
            # 从请求中提取参数
            document_id = request.document_id
            collection_name = request.collection_name
            
            # 记录开始时间
            start_time = time.time()
            logger.info(f"DeleteDocument request: id={document_id}, collection={collection_name}")
            
            # 调用服务删除文档
            success = await self.rag_service.delete_document(
                document_id=document_id,
                collection_name=collection_name
            )
            
            # 构建响应
            if success:
                response = self._build_delete_document_response(True, "Document deleted successfully")
            else:
                response = self._build_delete_document_response(False, "Document not found or couldn't be deleted")
            
            logger.info(f"DeleteDocument completed in {time.time() - start_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in DeleteDocument RPC: {str(e)}")
            response = self._build_delete_document_response(False, f"Failed to delete document: {str(e)}")
            return response
    
    async def Health(self, request, context):
        """
        实现健康检查 RPC
        
        Args:
            request: 健康检查请求
            context: gRPC 上下文
            
        Returns:
            健康检查响应
        """
        try:
            # 调用服务检查健康状态
            status, details = await self.rag_service.health_check()
            
            # 构建响应
            response = self._build_health_response(status, details)
            return response
            
        except Exception as e:
            logger.error(f"Error in Health RPC: {str(e)}")
            return self._build_health_response("NOT_SERVING", {"error": str(e)})
    
    def _parse_document(self, doc_proto) -> Document:
        """
        将 protobuf 文档对象转换为内部文档对象
        
        Args:
            doc_proto: protobuf 文档对象
            
        Returns:
            内部文档对象
        """
        metadata = {}
        if doc_proto.metadata:
            for key, value in doc_proto.metadata.items():
                metadata[key] = value
        
        return Document(
            id=doc_proto.id,
            content=doc_proto.content,
            metadata=metadata,
            score=doc_proto.score,
            source=doc_proto.source
        )
    
    def _build_document_proto(self, document: Document):
        """
        将内部文档对象转换为 protobuf 文档对象
        
        Args:
            document: 内部文档对象
            
        Returns:
            protobuf 文档对象
        """
        # 导入时防止循环引用
        from api.grpc.generated.rag_service_pb2 import Document as DocumentProto
        
        doc_proto = DocumentProto(
            id=document.id,
            content=document.content,
            score=document.score,
            source=document.source or ""
        )
        
        # 添加元数据
        if document.metadata:
            for key, value in document.metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    doc_proto.metadata[key] = str(value)
        
        return doc_proto
    
    def _build_document_reference_proto(self, reference: DocumentReference):
        """
        将内部文档引用对象转换为 protobuf 文档引用对象
        
        Args:
            reference: 内部文档引用对象
            
        Returns:
            protobuf 文档引用对象
        """
        # 导入时防止循环引用
        from api.grpc.generated.rag_service_pb2 import DocumentReference as DocumentReferenceProto
        
        ref_proto = DocumentReferenceProto(
            id=reference.id,
            title=reference.title,
            source=reference.source,
            url=reference.url or "",
            snippet=reference.snippet or ""
        )
        
        return ref_proto
    
    def _build_retrieve_response(self, documents: List[Document], latency_ms: float):
        """
        构建检索响应
        
        Args:
            documents: 文档列表
            latency_ms: 延迟(毫秒)
            
        Returns:
            检索响应
        """
        from api.grpc.generated.rag_service_pb2 import RetrieveResponse
        
        response = RetrieveResponse(
            latency_ms=latency_ms
        )
        
        # 添加文档
        for doc in documents:
            doc_proto = self._build_document_proto(doc)
            response.documents.append(doc_proto)
        
        return response
    
    def _build_generate_response(self, answer: str, references: List[DocumentReference], latency_ms: float):
        """
        构建生成响应
        
        Args:
            answer: 生成的回答
            references: 引用的文档
            latency_ms: 延迟(毫秒)
            
        Returns:
            生成响应
        """
        from api.grpc.generated.rag_service_pb2 import GenerateResponse
        
        response = GenerateResponse(
            answer=answer,
            latency_ms=latency_ms
        )
        
        # 添加引用
        for ref in references:
            ref_proto = self._build_document_reference_proto(ref)
            response.references.append(ref_proto)
        
        return response
    
    def _build_query_response(
        self, 
        answer: str, 
        references: List[DocumentReference],
        retrieval_latency_ms: float,
        generation_latency_ms: float,
        total_latency_ms: float
    ):
        """
        构建查询响应
        
        Args:
            answer: 生成的回答
            references: 引用的文档
            retrieval_latency_ms: 检索延迟(毫秒)
            generation_latency_ms: 生成延迟(毫秒)
            total_latency_ms: 总延迟(毫秒)
            
        Returns:
            查询响应
        """
        from api.grpc.generated.rag_service_pb2 import QueryResponse
        
        response = QueryResponse(
            answer=answer,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            total_latency_ms=total_latency_ms
        )
        
        # 添加引用
        for ref in references:
            ref_proto = self._build_document_reference_proto(ref)
            response.references.append(ref_proto)
        
        return response
    
    def _build_stream_response(self, answer_fragment: str, is_final: bool, references: List[DocumentReference] = None):
        """
        构建流式响应
        
        Args:
            answer_fragment: 回答片段
            is_final: 是否是最后一个片段
            references: 引用的文档(仅最后一个片段提供)
            
        Returns:
            流式响应
        """
        from api.grpc.generated.rag_service_pb2 import StreamResponse
        
        response = StreamResponse(
            answer_fragment=answer_fragment,
            is_final=is_final
        )
        
        # 如果是最后一个片段且有引用，添加引用
        if is_final and references:
            for ref in references:
                ref_proto = self._build_document_reference_proto(ref)
                response.references.append(ref_proto)
        
        return response
    
    def _build_add_document_response(self, document_id: str, success: bool, message: str):
        """
        构建添加文档响应
        
        Args:
            document_id: 文档ID
            success: 是否成功
            message: 消息
            
        Returns:
            添加文档响应
        """
        from api.grpc.generated.rag_service_pb2 import AddDocumentResponse
        
        response = AddDocumentResponse(
            document_id=document_id,
            success=success,
            message=message
        )
        
        return response
    
    def _build_delete_document_response(self, success: bool, message: str):
        """
        构建删除文档响应
        
        Args:
            success: 是否成功
            message: 消息
            
        Returns:
            删除文档响应
        """
        from api.grpc.generated.rag_service_pb2 import DeleteDocumentResponse
        
        response = DeleteDocumentResponse(
            success=success,
            message=message
        )
        
        return response
    
    def _build_health_response(self, status: str, details: Dict[str, str]):
        """
        构建健康检查响应
        
        Args:
            status: 状态
            details: 详细信息
            
        Returns:
            健康检查响应
        """
        from api.grpc.generated.rag_service_pb2 import HealthResponse
        
        # 转换状态
        status_map = {
            "SERVING": 1,
            "NOT_SERVING": 2,
            "UNKNOWN": 0
        }
        
        status_enum = status_map.get(status, 0)
        
        response = HealthResponse(
            status=status_enum
        )
        
        # 添加详细信息
        if details:
            for key, value in details.items():
                response.details[key] = value
        
        return response