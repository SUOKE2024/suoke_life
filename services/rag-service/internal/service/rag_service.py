#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务实现，提供检索增强生成的核心功能
"""

import time
import uuid
from typing import Dict, List, Any, Optional, AsyncGenerator, Tuple
from loguru import logger

from ..model.document import Document, DocumentReference, RetrieveResult, GenerateResult, QueryResult
from ..retriever.hybrid_retriever import HybridRetriever
from ..generator.openai_generator import OpenAIGenerator
from ..generator.local_generator import LocalGenerator
from ..repository.milvus_repository import MilvusRepository
from .embedding_service import EmbeddingService
from .cache_service import CacheService
from .kg_integration_service import KnowledgeGraphIntegrationService
from ..retriever.kg_enhanced_retriever import KGEnhancedRetriever
from ..platform.model_manager import get_model_manager, ModelType


class RagService:
    """
    RAG服务，协调检索和生成组件
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化RAG服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 组件初始化
        self.milvus_repository = None
        self.embedding_service = None
        self.retriever = None
        self.generator = None
        self.cache_service = None
        self.kg_integration_service = None
        
        # 服务状态
        self.is_initialized = False
        
        # 检查是否启用知识图谱增强
        self.kg_enhanced = config.get('knowledge_graph', {}).get('enabled', False)
        
        self.model_manager = get_model_manager()
    
    async def initialize(self) -> None:
        """初始化所有组件"""
        if self.is_initialized:
            return
            
        logger.info("Initializing RAG service")
        
        # 初始化向量数据库
        self.milvus_repository = MilvusRepository(self.config['vector_database'])
        await self.milvus_repository.initialize()
        
        # 初始化嵌入服务
        self.embedding_service = EmbeddingService(self.config)
        await self.embedding_service.initialize()
        
        # 初始化检索器（根据配置选择是否使用知识图谱增强）
        if self.kg_enhanced:
            logger.info("Using Knowledge Graph Enhanced Retriever")
            self.retriever = KGEnhancedRetriever(self.config, self.milvus_repository)
        else:
            self.retriever = HybridRetriever(self.config, self.milvus_repository)
        await self.retriever.initialize()
        
        # 通过模型管理器加载生成模型和嵌入模型
        if self.model_manager:
            gen_model = await self.model_manager.get_model(
                self.config['generator']['model_name'],
                self.config['generator'].get('model_version')
            )
            if gen_model:
                self.generator = gen_model
            embed_model = await self.model_manager.get_model(
                self.config['embedding']['model_name'],
                self.config['embedding'].get('model_version')
            )
            if embed_model:
                self.embedding_service.set_model(embed_model)
        
        # 初始化缓存服务
        self.cache_service = CacheService(self.config['cache'])
        await self.cache_service.initialize()
        
        # 如果启用知识图谱，初始化知识图谱集成服务
        if self.kg_enhanced:
            self.kg_integration_service = KnowledgeGraphIntegrationService(self.config)
            await self.kg_integration_service.initialize()
        
        self.is_initialized = True
        logger.info("RAG service initialized successfully")
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        collection_names: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
        rerank: bool = False,
        user_id: Optional[str] = None
    ) -> RetrieveResult:
        """
        检索相关文档
        
        Args:
            query: 查询
            top_k: 返回结果数量
            collection_names: 集合名称列表
            metadata_filter: 元数据过滤条件
            score_threshold: 相关性分数阈值
            rerank: 是否启用重排序
            user_id: 用户ID
            
        Returns:
            检索结果
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 尝试从缓存获取结果
        cache_key = {
            "query": query,
            "top_k": top_k,
            "collection_names": collection_names,
            "metadata_filter": metadata_filter,
            "score_threshold": score_threshold,
            "rerank": rerank
        }
        cached_result = await self.cache_service.get("retrieval", cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for query: {query}")
            return cached_result
        
        # 执行检索
        logger.info(f"Retrieving documents for query: {query}")
        result = await self.retriever.retrieve(
            query=query,
            top_k=top_k,
            collection_names=collection_names,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
            rerank=rerank
        )
        
        # 缓存结果
        await self.cache_service.set("retrieval", cache_key, result)
        
        return result
    
    async def generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> GenerateResult:
        """
        生成回答
        
        Args:
            query: 查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Returns:
            生成结果
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 尝试从缓存获取结果
        cache_key = {
            "query": query,
            "context_doc_ids": [doc.id for doc in context_documents],
            "system_prompt": system_prompt,
            "generation_params": generation_params
        }
        cached_result = await self.cache_service.get("generation", cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for generation: {query}")
            return cached_result
        
        # 执行生成
        logger.info(f"Generating answer for query: {query}")
        result = await self.generator.generate(
            query=query,
            context_documents=context_documents,
            system_prompt=system_prompt,
            generation_params=generation_params,
            user_id=user_id
        )
        
        # 缓存结果
        await self.cache_service.set("generation", cache_key, result)
        
        return result
    
    async def query(
        self,
        query: str,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
        collection_names: Optional[List[str]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> QueryResult:
        """
        执行完整的检索增强生成查询
        
        Args:
            query: 查询
            top_k: 检索文档数量
            system_prompt: 系统提示词
            collection_names: 集合名称列表
            generation_params: 生成参数
            metadata_filter: 元数据过滤条件
            user_id: 用户ID
            
        Returns:
            查询结果
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 尝试从缓存获取结果
        cache_key = {
            "query": query,
            "top_k": top_k,
            "system_prompt": system_prompt,
            "collection_names": collection_names,
            "generation_params": generation_params,
            "metadata_filter": metadata_filter
        }
        cached_result = await self.cache_service.get("query", cache_key)
        
        if cached_result:
            logger.info(f"Cache hit for combined query: {query}")
            return cached_result
        
        # 记录时间
        total_start_time = time.time()
        
        # 1. 执行检索
        retrieval_start_time = time.time()
        retrieve_result = await self.retrieve(
            query=query,
            top_k=top_k,
            collection_names=collection_names,
            metadata_filter=metadata_filter,
            rerank=True
        )
        retrieval_latency_ms = (time.time() - retrieval_start_time) * 1000
        
        # 2. 执行生成
        generation_start_time = time.time()
        generate_result = await self.generate(
            query=query,
            context_documents=retrieve_result.documents,
            system_prompt=system_prompt,
            generation_params=generation_params,
            user_id=user_id
        )
        generation_latency_ms = (time.time() - generation_start_time) * 1000
        
        # 计算总延迟
        total_latency_ms = (time.time() - total_start_time) * 1000
        
        # 构建结果
        result = QueryResult(
            answer=generate_result.answer,
            references=generate_result.references,
            retrieval_latency_ms=retrieval_latency_ms,
            generation_latency_ms=generation_latency_ms,
            total_latency_ms=total_latency_ms
        )
        
        # 缓存结果
        await self.cache_service.set("query", cache_key, result)
        
        return result
    
    async def stream_query(
        self,
        query: str,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
        collection_names: Optional[List[str]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[Tuple[str, bool, Optional[List[DocumentReference]]], None]:
        """
        执行流式检索增强生成查询
        
        Args:
            query: 查询
            top_k: 检索文档数量
            system_prompt: 系统提示词
            collection_names: 集合名称列表
            generation_params: 生成参数
            metadata_filter: 元数据过滤条件
            user_id: 用户ID
            
        Yields:
            元组: (回答片段, 是否最后一个片段, 引用的文档[仅最后一个片段中提供])
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 执行检索
        retrieve_result = await self.retrieve(
            query=query,
            top_k=top_k,
            collection_names=collection_names,
            metadata_filter=metadata_filter,
            rerank=True
        )
        
        # 流式生成
        async for answer_fragment, is_final, references in self.generator.stream_generate(
            query=query,
            context_documents=retrieve_result.documents,
            system_prompt=system_prompt,
            generation_params=generation_params,
            user_id=user_id
        ):
            yield answer_fragment, is_final, references
    
    async def add_document(
        self,
        document: Document,
        collection_name: str = "default",
        reindex: bool = True
    ) -> str:
        """
        添加文档到知识库
        
        Args:
            document: 文档
            collection_name: 集合名称
            reindex: 是否重新索引
            
        Returns:
            文档ID
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 如果没有ID，生成一个
        if not document.id:
            document.id = str(uuid.uuid4())
        
        # 添加集合信息到元数据
        if "collection" not in document.metadata:
            document.metadata["collection"] = collection_name
        
        # 生成嵌入向量
        if not document.vector:
            documents_with_vectors = await self.embedding_service.embed_documents([document])
            document = documents_with_vectors[0]
        
        # 添加到向量数据库
        success = await self.milvus_repository.add_documents([document])
        
        if success:
            logger.info(f"Document {document.id} added to collection {collection_name}")
            
            # 如果需要重新索引，触发相关操作
            if reindex and hasattr(self.retriever, "_initialize_bm25"):
                await self.retriever._initialize_bm25()
        else:
            logger.error(f"Failed to add document {document.id} to collection {collection_name}")
        
        return document.id
    
    async def delete_document(
        self,
        document_id: str,
        collection_name: str = "default"
    ) -> bool:
        """
        从知识库删除文档
        
        Args:
            document_id: 文档ID
            collection_name: 集合名称
            
        Returns:
            是否成功
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 从向量数据库删除
        success = await self.milvus_repository.delete_documents([document_id])
        
        if success:
            logger.info(f"Document {document_id} deleted from collection {collection_name}")
            
            # 重新初始化关键词索引
            if hasattr(self.retriever, "_initialize_bm25"):
                await self.retriever._initialize_bm25()
        else:
            logger.error(f"Failed to delete document {document_id} from collection {collection_name}")
        
        return success
    
    async def health_check(self) -> Tuple[str, Dict[str, str]]:
        """
        检查服务健康状态
        
        Returns:
            状态和详细信息
        """
        status = "SERVING"
        details = {
            "version": self.config['service'].get('version', "0.1.0"),
            "name": self.config['service'].get('name', "rag-service")
        }
        
        try:
            if not self.is_initialized:
                status = "NOT_SERVING"
                details["reason"] = "Service not initialized"
                return status, details
            
            # 检查向量数据库连接
            if not self.milvus_repository or not self.milvus_repository.is_connected:
                status = "NOT_SERVING"
                details["reason"] = "Vector database not connected"
                return status, details
            
            # 检查嵌入服务
            if not self.embedding_service or not self.embedding_service.is_initialized:
                status = "NOT_SERVING"
                details["reason"] = "Embedding service not initialized"
                return status, details
            
            # 检查检索器
            if not self.retriever or not self.retriever.is_initialized:
                status = "NOT_SERVING"
                details["reason"] = "Retriever not initialized"
                return status, details
            
            # 检查生成器
            if not self.generator or not hasattr(self.generator, 'is_initialized') or not self.generator.is_initialized:
                status = "NOT_SERVING"
                details["reason"] = "Generator not initialized"
                return status, details
            
            # 添加组件状态
            details["milvus_connected"] = "true"
            details["embedding_model"] = self.embedding_service.model_name
            details["generator_type"] = self.config['generator']['model_type']
            
            return status, details
            
        except Exception as e:
            status = "NOT_SERVING"
            details["error"] = str(e)
            logger.error(f"Health check failed: {str(e)}")
            return status, details
    
    async def close(self) -> None:
        """关闭服务和所有组件"""
        logger.info("Closing RAG service")
        
        # 关闭生成器
        if self.generator:
            await self.generator.close()
        
        # 关闭检索器
        if self.retriever:
            await self.retriever.close()
        
        # 关闭嵌入服务
        if self.embedding_service:
            await self.embedding_service.close()
        
        # 关闭向量数据库
        if self.milvus_repository:
            await self.milvus_repository.close()
        
        # 关闭缓存服务
        if self.cache_service:
            await self.cache_service.close()
        
        self.is_initialized = False
        logger.info("RAG service closed")
    
    async def sync_knowledge_graph(self) -> Dict[str, int]:
        """
        同步知识图谱数据到向量数据库
        
        Returns:
            同步结果统计
        """
        if not self.kg_integration_service:
            raise ValueError("Knowledge graph integration is not enabled")
        
        logger.info("Starting knowledge graph synchronization")
        
        # 同步所有知识图谱数据
        sync_results = await self.kg_integration_service.sync_all_knowledge()
        
        # 获取所有文档类型的同步结果
        all_documents = []
        
        # 同步体质数据
        if sync_results["constitutions"] > 0:
            constitution_docs = await self.kg_integration_service.sync_constitutions()
            all_documents.extend(constitution_docs)
        
        # 同步证型数据
        if sync_results["syndromes"] > 0:
            syndrome_docs = await self.kg_integration_service.sync_syndromes()
            all_documents.extend(syndrome_docs)
        
        # 同步中药数据
        if sync_results["herbs"] > 0:
            herb_docs = await self.kg_integration_service.sync_herbs()
            all_documents.extend(herb_docs)
        
        # 同步穴位数据
        if sync_results["acupoints"] > 0:
            acupoint_docs = await self.kg_integration_service.sync_acupoints()
            all_documents.extend(acupoint_docs)
        
        # 生成嵌入向量
        if all_documents:
            logger.info(f"Generating embeddings for {len(all_documents)} documents")
            documents_with_vectors = await self.embedding_service.embed_documents(all_documents)
            
            # 添加到向量数据库
            success = await self.milvus_repository.add_documents(documents_with_vectors)
            
            if success:
                logger.info(f"Successfully synced {len(documents_with_vectors)} documents to vector database")
            else:
                logger.error("Failed to sync documents to vector database")
        
        return sync_results
    
    async def reload_model(self, model_name: str, version: str = None):
        """支持热更新指定模型"""
        if self.model_manager:
            await self.model_manager.load_model(model_name, version)
        logger.info(f"模型{model_name}已热更新")