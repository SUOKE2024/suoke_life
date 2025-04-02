#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG引擎
======
实现检索增强生成
"""

import time
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from loguru import logger

from ..vector_store import BaseVectorStore, VectorStoreFactory
from ..embeddings import EmbeddingManager
from ..reranker import BaseReranker, RerankerFactory
from ..llm import BaseLLMClient, LLMFactory
from .document_processor import DocumentProcessor
from .result_formatter import ResultFormatter

from ..config import (
    RERANK_ENABLED,
    RERANK_TOP_N,
    TOP_K
)


class RAGEngine:
    """RAG引擎，实现检索增强生成"""
    
    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        embedding_manager: Optional[EmbeddingManager] = None,
        document_processor: Optional[DocumentProcessor] = None,
        result_formatter: Optional[ResultFormatter] = None,
        llm_client: Optional[BaseLLMClient] = None,
        reranker: Optional[BaseReranker] = None,
        max_context_docs: int = 5,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        初始化RAG引擎
        
        Args:
            vector_store: 向量存储实例，不提供则自动创建
            embedding_manager: 嵌入管理器实例，不提供则自动创建
            document_processor: 文档处理器实例，不提供则自动创建
            result_formatter: 结果格式化器实例，不提供则自动创建
            llm_client: LLM客户端实例，不提供则创建默认客户端
            reranker: 重排序器实例，不提供则创建默认重排序器
            max_context_docs: 最大上下文文档数量
            chunk_size: 默认文本块大小
            chunk_overlap: 默认文本块重叠大小
        """
        # 确保嵌入管理器存在
        if not embedding_manager:
            from ..embeddings import EmbeddingManager
            embedding_manager = EmbeddingManager()
            logger.info("创建默认嵌入管理器")
            
        self.embedding_manager = embedding_manager
        
        # 确保向量存储存在
        if not vector_store:
            vector_store = VectorStoreFactory.create_vector_store(
                embedding_manager=embedding_manager
            )
            logger.info("创建默认向量存储")
            
        self.vector_store = vector_store
        
        # 确保文档处理器存在
        if not document_processor:
            document_processor = DocumentProcessor(
                vector_store=vector_store,
                embedding_manager=embedding_manager,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            logger.info("创建默认文档处理器")
            
        self.document_processor = document_processor
        
        # 确保结果格式化器存在
        if not result_formatter:
            result_formatter = ResultFormatter()
            logger.info("创建默认结果格式化器")
            
        self.result_formatter = result_formatter
        
        # 创建LLM客户端
        if not llm_client:
            try:
                from ..llm import LLMFactory
                llm_client = LLMFactory.create_llm_client()
                logger.info(f"创建默认LLM客户端: {llm_client.model_name if llm_client else 'None'}")
            except Exception as e:
                logger.warning(f"创建LLM客户端失败: {e}")
                llm_client = None
                
        self.llm_client = llm_client
        
        # 创建重排序器（如果启用）
        if RERANK_ENABLED and not reranker:
            try:
                from ..reranker import RerankerFactory
                reranker = RerankerFactory.create_reranker()
                logger.info(f"创建默认重排序器: {reranker.model_name if reranker else 'None'}")
            except Exception as e:
                logger.warning(f"创建重排序器失败: {e}")
                reranker = None
                
        self.reranker = reranker
        
        # 其他参数
        self.max_context_docs = max_context_docs
        
    def add_document(
        self, 
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        添加文档到知识库
        
        Args:
            document: 文档文本
            metadata: 文档元数据
            doc_id: 文档ID，如不提供则生成
            
        Returns:
            List[str]: 添加的块ID列表
        """
        return self.document_processor.process_document(
            document=document,
            metadata=metadata,
            doc_id=doc_id,
            **kwargs
        )
        
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None,
        **kwargs
    ) -> List[List[str]]:
        """
        批量添加文档到知识库
        
        Args:
            documents: 文档文本列表
            metadatas: 文档元数据列表
            doc_ids: 文档ID列表，如不提供则生成
            
        Returns:
            List[List[str]]: 每个文档添加的块ID列表的列表
        """
        return self.document_processor.process_documents(
            documents=documents,
            metadatas=metadatas,
            doc_ids=doc_ids,
            **kwargs
        )
        
    def delete_document(self, doc_id: str) -> bool:
        """
        从知识库删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            bool: 操作是否成功
        """
        return self.document_processor.delete_document(doc_id)
        
    def search(
        self, 
        query: str,
        k: int = TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        rerank: Optional[bool] = None,
        rerank_top_n: Optional[int] = None,
        format_type: str = "json"
    ) -> Union[str, Dict[str, Any]]:
        """
        使用RAG引擎进行搜索，不生成回答
        
        Args:
            query: 查询文本
            k: 返回的文档数量
            filter: 过滤条件
            rerank: 是否使用重排序，None表示使用默认设置
            rerank_top_n: 重排序返回的结果数量，None表示使用默认设置
            format_type: 返回格式，json或text
            
        Returns:
            Union[str, Dict[str, Any]]: 搜索结果
        """
        try:
            start_time = time.time()
            
            # 获取搜索的初始结果数量
            initial_k = k
            should_rerank = rerank if rerank is not None else (self.reranker is not None and RERANK_ENABLED)
            rerank_top_n = rerank_top_n or RERANK_TOP_N
            
            # 如果要进行重排序，需要获取更多的初始结果
            if should_rerank:
                initial_k = max(k, rerank_top_n)
            
            # 执行向量搜索
            contexts = self.vector_store.similarity_search(
                query=query,
                k=initial_k,
                filter=filter
            )
            
            # 计算搜索时间
            search_time = time.time() - start_time
            
            # 如果启用了重排序并且有重排序器
            reranked = False
            if should_rerank and self.reranker and contexts:
                try:
                    rerank_start_time = time.time()
                    contexts = self.reranker.rerank(
                        query=query,
                        documents=contexts,
                        top_n=k
                    )
                    rerank_time = time.time() - rerank_start_time
                    reranked = True
                    logger.info(f"重排序完成，耗时 {rerank_time:.2f}s")
                except Exception as e:
                    logger.error(f"重排序失败: {e}")
                    # 如果重排序失败，截取Top-K结果
                    contexts = contexts[:k]
            elif contexts and len(contexts) > k:
                # 截取Top-K结果
                contexts = contexts[:k]
            
            # 准备元数据
            metadata = {
                "total_results": len(contexts),
                "search_time_ms": int(search_time * 1000),
                "reranked": reranked
            }
            
            # 格式化结果
            result = self.result_formatter.format_search_result(
                query=query,
                contexts=contexts,
                metadata=metadata,
                format_type=format_type
            )
            
            logger.info(f"RAG搜索完成，找到 {len(contexts)} 个结果，耗时 {search_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"RAG搜索失败: {e}")
            return self.result_formatter.format_error(
                error_message=f"搜索失败: {str(e)}",
                format_type=format_type
            )
            
    def query(
        self, 
        query: str,
        k: int = TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        rerank: Optional[bool] = None,
        rerank_top_n: Optional[int] = None,
        format_type: str = "json",
        llm_args: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[str, Dict[str, Any]]:
        """
        使用RAG引擎进行查询，检索并生成回答
        
        Args:
            query: 查询文本
            k: 检索的文档数量
            filter: 过滤条件
            rerank: 是否使用重排序，None表示使用默认设置
            rerank_top_n: 重排序返回的结果数量，None表示使用默认设置
            format_type: 返回格式，json或text
            llm_args: LLM参数
            stream: 是否使用流式生成
            
        Returns:
            Union[str, Dict[str, Any]]: 查询结果
        """
        try:
            start_time = time.time()
            
            # 获取搜索的初始结果数量
            initial_k = k
            should_rerank = rerank if rerank is not None else (self.reranker is not None and RERANK_ENABLED)
            rerank_top_n = rerank_top_n or RERANK_TOP_N
            
            # 如果要进行重排序，需要获取更多的初始结果
            if should_rerank:
                initial_k = max(k, rerank_top_n)
            
            # 执行向量搜索
            contexts = self.vector_store.similarity_search(
                query=query,
                k=initial_k,
                filter=filter
            )
            
            # 计算搜索时间
            search_time = time.time() - start_time
            
            # 如果启用了重排序并且有重排序器
            reranked = False
            if should_rerank and self.reranker and contexts:
                try:
                    rerank_start_time = time.time()
                    contexts = self.reranker.rerank(
                        query=query,
                        documents=contexts,
                        top_n=k
                    )
                    rerank_time = time.time() - rerank_start_time
                    reranked = True
                    logger.info(f"重排序完成，耗时 {rerank_time:.2f}s")
                except Exception as e:
                    logger.error(f"重排序失败: {e}")
                    # 如果重排序失败，截取Top-K结果
                    contexts = contexts[:k]
            elif contexts and len(contexts) > k:
                # 截取Top-K结果
                contexts = contexts[:k]
            
            # 如果没有配置LLM客户端，只返回搜索结果
            if self.llm_client is None:
                logger.warning("未配置LLM客户端，只返回搜索结果")
                metadata = {
                    "total_results": len(contexts),
                    "search_time_ms": int(search_time * 1000),
                    "reranked": reranked,
                    "generation": False,
                    "message": "未配置LLM客户端，只返回搜索结果"
                }
                
                return self.result_formatter.format_query_result(
                    query=query,
                    answer=None,
                    contexts=contexts,
                    metadata=metadata,
                    format_type=format_type
                )
                
            # 准备生成回答
            generate_start_time = time.time()
            llm_args = llm_args or {}
            
            # 调用LLM生成回答
            if stream:
                # 流式生成的情况下，直接返回生成器
                answer_generator = self.llm_client.rag_complete_stream(query, contexts, **llm_args)
                return answer_generator
            else:
                # 非流式生成
                answer = self.llm_client.rag_complete(query, contexts, **llm_args)
                
                # 计算生成时间
                generation_time = time.time() - generate_start_time
                total_time = time.time() - start_time
                
                # 准备元数据
                metadata = {
                    "total_results": len(contexts),
                    "search_time_ms": int(search_time * 1000),
                    "reranked": reranked,
                    "generation_time_ms": int(generation_time * 1000),
                    "total_time_ms": int(total_time * 1000),
                    "generation": True,
                    "model": self.llm_client.model_name
                }
                
                # 格式化结果
                result = self.result_formatter.format_query_result(
                    query=query,
                    answer=answer,
                    contexts=contexts,
                    metadata=metadata,
                    format_type=format_type
                )
                
                logger.info(f"RAG查询完成，找到 {len(contexts)} 个结果，生成回答耗时 {generation_time:.2f}s，总耗时 {total_time:.2f}s")
                return result
            
        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            return self.result_formatter.format_error(
                error_message=f"查询失败: {str(e)}",
                format_type=format_type
            ) 