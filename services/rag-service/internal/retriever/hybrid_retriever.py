#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
混合检索器模块，实现向量检索与关键词检索的融合
"""

import time
import re
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from loguru import logger

from .base import BaseRetriever
from ..model.document import Document, RetrieveResult
from ..repository.milvus_repository import MilvusRepository


class HybridRetriever(BaseRetriever):
    """
    混合检索器，结合向量检索和关键词检索优势
    
    特点:
    1. 向量检索 - 捕获语义相似性
    2. 关键词检索 - 捕获精确关键词匹配
    3. 混合重排 - 融合两种检索的结果
    """
    
    def __init__(self, config: Dict[str, Any], vector_db_repository: MilvusRepository):
        """
        初始化混合检索器
        
        Args:
            config: 配置字典
            vector_db_repository: 向量数据库仓库
        """
        self.config = config
        self.vector_db = vector_db_repository
        
        # 混合检索配置
        hybrid_config = config['retriever'].get('hybrid_search', {})
        self.hybrid_enabled = hybrid_config.get('enabled', True)
        self.keyword_weight = hybrid_config.get('keyword_weight', 0.3)
        self.vector_weight = hybrid_config.get('vector_weight', 0.7)
        self.bm25_b = hybrid_config.get('bm25_b', 0.75)
        self.bm25_k1 = hybrid_config.get('bm25_k1', 1.2)
        
        # BM25索引
        self.corpus_docs = []
        self.tokenized_corpus = []
        self.bm25_index = None
        
        # 初始化状态
        self.is_initialized = False
    
    async def initialize(self):
        """初始化检索器"""
        if self.is_initialized:
            return
            
        logger.info("Initializing hybrid retriever")
        
        # 确保向量数据库已初始化
        if not hasattr(self.vector_db, 'is_connected') or not self.vector_db.is_connected:
            await self.vector_db.initialize()
        
        # 如果启用混合检索，需要初始化BM25
        if self.hybrid_enabled:
            await self._initialize_bm25()
        
        self.is_initialized = True
        logger.info(f"Hybrid retriever initialized, hybrid search enabled: {self.hybrid_enabled}")
    
    async def _initialize_bm25(self):
        """初始化BM25索引"""
        logger.info("Building BM25 index from vector database documents...")

        # 通过向量数据库仓库获取全部文档
        self.corpus_docs = await self.vector_db.get_all_documents()

        if not self.corpus_docs:
            logger.warning("No documents retrieved from vector database; BM25 index will not be created")
            return

        # 分词并生成语料
        self.tokenized_corpus = [self._tokenize(doc.content) for doc in self.corpus_docs]

        # 初始化 BM25 索引
        self.bm25_index = BM25Okapi(
            self.tokenized_corpus,
            k1=self.bm25_k1,
            b=self.bm25_b
        )

        logger.info(f"BM25 index built with {len(self.corpus_docs)} documents")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        简单的中文分词实现
        
        Args:
            text: 输入文本
            
        Returns:
            分词结果
        """
        # 在实际项目中，应使用专业的中文分词工具如jieba
        # 这里使用简单的正则表达式分词
        return [w for w in re.findall(r'[\w\u4e00-\u9fff]+', text.lower())]
    
    async def _do_retrieve(
        self,
        query: str,
        top_k: int = 5,
        collection_names: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
        rerank: bool = False
    ) -> List[Document]:
        """
        执行检索操作
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            collection_names: 集合名称列表
            metadata_filter: 元数据过滤条件
            score_threshold: 相关性分数阈值
            rerank: 是否启用重排序
            
        Returns:
            检索到的文档列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        # 嵌入查询
        query_embedding = await self._get_query_embedding(query)
        
        if self.hybrid_enabled and self.bm25_index:
            # 如果启用混合检索且BM25索引已初始化
            # 执行向量检索
            vector_docs = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k * 2,  # 检索更多结果用于混合
                metadata_filter=metadata_filter,
                score_threshold=0.0  # 不过滤，混合后再过滤
            )
            
            # 执行关键词检索
            keyword_docs = await self._keyword_search(
                query=query, 
                top_k=top_k * 2  # 检索更多结果用于混合
            )
            
            # 混合结果
            merged_docs = self._merge_results(
                vector_docs=vector_docs,
                keyword_docs=keyword_docs,
                top_k=top_k
            )
            
            # 按分数过滤
            result_docs = [doc for doc in merged_docs if doc.score >= score_threshold]
            
        else:
            # 仅使用向量检索
            result_docs = await self.vector_db.search(
                query_vector=query_embedding,
                top_k=top_k,
                metadata_filter=metadata_filter,
                score_threshold=score_threshold
            )
        
        # 如果需要重排序
        if rerank and result_docs:
            result_docs = await self.rerank(query, result_docs, top_k)
        
        return result_docs
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """
        获取查询的嵌入向量
        
        Args:
            query: 查询文本
            
        Returns:
            嵌入向量
        """
        # 在实际应用中，应该调用嵌入模型生成向量
        # 这里简单返回一个随机向量作为示例
        # 实际实现中需要使用真实的嵌入模型
        dim = self.config.get('vector_database', {}).get('dimension', 768)
        return list(np.random.uniform(-1, 1, dim))
    
    async def _keyword_search(self, query: str, top_k: int) -> List[Document]:
        """
        执行关键词搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索到的文档列表
        """
        if not self.bm25_index:
            return []
        
        # 分词
        tokenized_query = self._tokenize(query)
        
        # 计算BM25分数
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        
        # 构建分数-索引对
        scored_indices = [(score, idx) for idx, score in enumerate(bm25_scores)]
        
        # 按分数降序排序并获取top_k结果
        top_results = sorted(scored_indices, reverse=True)[:top_k]
        
        # 获取结果文档
        result_docs = []
        max_score = max([score for score, _ in top_results]) if top_results else 1.0
        
        for score, idx in top_results:
            # 归一化分数到0-1范围
            normalized_score = score / max_score if max_score > 0 else 0
            
            doc = self.corpus_docs[idx]
            doc.score = normalized_score
            result_docs.append(doc)
        
        return result_docs
    
    def _merge_results(
        self,
        vector_docs: List[Document],
        keyword_docs: List[Document],
        top_k: int
    ) -> List[Document]:
        """
        合并向量检索和关键词检索结果
        
        Args:
            vector_docs: 向量检索结果
            keyword_docs: 关键词检索结果
            top_k: 返回数量
            
        Returns:
            合并后的文档列表
        """
        # 创建文档ID到文档的映射
        doc_map = {}
        
        # 处理向量检索结果
        for doc in vector_docs:
            doc_map[doc.id] = {
                "document": doc,
                "vector_score": doc.score,
                "keyword_score": 0.0
            }
        
        # 处理关键词检索结果
        for doc in keyword_docs:
            if doc.id in doc_map:
                doc_map[doc.id]["keyword_score"] = doc.score
            else:
                doc_map[doc.id] = {
                    "document": doc,
                    "vector_score": 0.0,
                    "keyword_score": doc.score
                }
        
        # 计算组合分数
        merged_docs = []
        for doc_id, scores in doc_map.items():
            combined_score = (
                self.vector_weight * scores["vector_score"] +
                self.keyword_weight * scores["keyword_score"]
            )
            
            doc = scores["document"]
            doc.score = combined_score
            merged_docs.append(doc)
        
        # 按组合分数排序
        merged_docs.sort(key=lambda x: x.score, reverse=True)
        
        # 返回top_k个结果
        return merged_docs[:top_k]
    
    async def rerank(self, query: str, documents: List[Document], top_k: int = 5) -> List[Document]:
        """
        重排序检索结果
        
        Args:
            query: 查询文本
            documents: 待重排序的文档列表
            top_k: 返回结果数量
            
        Returns:
            重排序后的文档列表
        """
        # 获取配置的重排序模型
        reranker_model = self.config['retriever'].get('reranker_model')
        
        if reranker_model:
            # 在实际应用中，需要集成一个重排序模型
            # 这里简单返回原始文档，可以替换为实际的重排序实现
            logger.info(f"Reranking {len(documents)} documents with model: {reranker_model}")
            
            # 简单模拟重排序结果，实际中应使用真实模型
            for doc in documents:
                # 在实际重排序中，这里应该是根据查询与文档内容计算的分数
                # 此处仅调整原分数以示区别
                doc.score = min(doc.score * 1.1, 1.0)
        
        # 按分数重新排序
        documents.sort(key=lambda x: x.score, reverse=True)
        
        # 返回top_k个结果
        return documents[:top_k]
    
    async def close(self):
        """关闭检索器及相关连接"""
        # 释放BM25索引资源
        self.bm25_index = None
        self.tokenized_corpus = []
        self.corpus_docs = []
        
        # 关闭向量数据库连接
        if self.vector_db:
            await self.vector_db.close() 