#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强向量检索服务
支持混合检索、重排序、知识图谱增强等高级功能
"""

import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
from loguru import logger

from config.settings import get_settings
from internal.model.entities import Document, SearchResult, SearchQuery
from internal.repository.vector_repository import VectorRepository
from internal.repository.knowledge_graph_repository import KnowledgeGraphRepository
from pkg.cache.cache_manager import CacheManager
from pkg.metrics.metrics_collector import MetricsCollector


@dataclass
class RetrievalContext:
    """检索上下文"""
    query: str
    query_embedding: Optional[np.ndarray] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    domain: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class SearchCandidate:
    """搜索候选项"""
    document: Document
    score: float
    source: str  # vector, keyword, hybrid, kg
    metadata: Optional[Dict[str, Any]] = None


class BaseRetriever(ABC):
    """基础检索器抽象类"""
    
    @abstractmethod
    async def retrieve(
        self, 
        context: RetrievalContext, 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """执行检索"""
        pass


class VectorRetriever(BaseRetriever):
    """向量检索器"""
    
    def __init__(self, vector_repo: VectorRepository):
        self.vector_repo = vector_repo
        self.settings = get_settings()
    
    async def retrieve(
        self, 
        context: RetrievalContext, 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """向量检索"""
        try:
            if context.query_embedding is None:
                raise ValueError("向量检索需要查询嵌入")
            
            # 执行向量搜索
            results = await self.vector_repo.search_vectors(
                query_vector=context.query_embedding,
                top_k=top_k,
                filters=context.filters
            )
            
            candidates = []
            for result in results:
                candidate = SearchCandidate(
                    document=result.document,
                    score=result.score,
                    source="vector",
                    metadata={"vector_score": result.score}
                )
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []


class KeywordRetriever(BaseRetriever):
    """关键词检索器"""
    
    def __init__(self, vector_repo: VectorRepository):
        self.vector_repo = vector_repo
        self.settings = get_settings()
    
    async def retrieve(
        self, 
        context: RetrievalContext, 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """关键词检索"""
        try:
            # 执行关键词搜索
            results = await self.vector_repo.search_keywords(
                query=context.query,
                top_k=top_k,
                filters=context.filters
            )
            
            candidates = []
            for result in results:
                candidate = SearchCandidate(
                    document=result.document,
                    score=result.score,
                    source="keyword",
                    metadata={"keyword_score": result.score}
                )
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []


class KnowledgeGraphRetriever(BaseRetriever):
    """知识图谱检索器"""
    
    def __init__(self, kg_repo: KnowledgeGraphRepository):
        self.kg_repo = kg_repo
        self.settings = get_settings()
    
    async def retrieve(
        self, 
        context: RetrievalContext, 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """知识图谱检索"""
        try:
            # 实体识别和链接
            entities = await self._extract_entities(context.query)
            
            if not entities:
                return []
            
            # 图谱扩展
            expanded_entities = await self._expand_entities(
                entities, 
                depth=self.settings.retrieval.kg_expansion_depth
            )
            
            # 获取相关文档
            documents = await self._get_entity_documents(expanded_entities)
            
            candidates = []
            for doc, relevance_score in documents[:top_k]:
                candidate = SearchCandidate(
                    document=doc,
                    score=relevance_score,
                    source="kg",
                    metadata={
                        "kg_entities": entities,
                        "expanded_entities": expanded_entities,
                        "kg_score": relevance_score
                    }
                )
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"知识图谱检索失败: {e}")
            return []
    
    async def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """提取实体"""
        # 这里应该实现实体识别逻辑
        # 可以使用NER模型或者基于规则的方法
        return await self.kg_repo.extract_entities(query)
    
    async def _expand_entities(
        self, 
        entities: List[Dict[str, Any]], 
        depth: int = 2
    ) -> List[Dict[str, Any]]:
        """扩展实体"""
        expanded = []
        
        for entity in entities:
            # 获取相关实体
            related = await self.kg_repo.get_related_entities(
                entity_id=entity["id"],
                max_depth=depth,
                max_entities=self.settings.retrieval.kg_max_entities
            )
            expanded.extend(related)
        
        return expanded
    
    async def _get_entity_documents(
        self, 
        entities: List[Dict[str, Any]]
    ) -> List[Tuple[Document, float]]:
        """获取实体相关文档"""
        documents = []
        
        for entity in entities:
            entity_docs = await self.kg_repo.get_entity_documents(entity["id"])
            for doc in entity_docs:
                # 计算相关性分数
                relevance_score = self._calculate_entity_relevance(entity, doc)
                documents.append((doc, relevance_score))
        
        # 按相关性排序
        documents.sort(key=lambda x: x[1], reverse=True)
        return documents
    
    def _calculate_entity_relevance(
        self, 
        entity: Dict[str, Any], 
        document: Document
    ) -> float:
        """计算实体与文档的相关性"""
        # 简单的相关性计算，可以根据需要优化
        base_score = entity.get("confidence", 0.5)
        
        # 考虑实体类型权重
        entity_type_weights = {
            "symptom": 1.0,
            "syndrome": 0.9,
            "herb": 0.8,
            "acupoint": 0.7,
            "constitution": 0.6
        }
        
        type_weight = entity_type_weights.get(entity.get("type", ""), 0.5)
        return base_score * type_weight


class HybridRetriever(BaseRetriever):
    """混合检索器"""
    
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        kg_retriever: Optional[KnowledgeGraphRetriever] = None
    ):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.kg_retriever = kg_retriever
        self.settings = get_settings()
    
    async def retrieve(
        self, 
        context: RetrievalContext, 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """混合检索"""
        try:
            # 并行执行多种检索
            tasks = []
            
            # 向量检索
            if context.query_embedding is not None:
                tasks.append(self.vector_retriever.retrieve(context, top_k * 2))
            
            # 关键词检索
            tasks.append(self.keyword_retriever.retrieve(context, top_k * 2))
            
            # 知识图谱检索
            if (self.kg_retriever and 
                self.settings.retrieval.enable_kg_enhancement):
                tasks.append(self.kg_retriever.retrieve(context, top_k))
            
            # 等待所有检索完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 合并结果
            all_candidates = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"检索任务 {i} 失败: {result}")
                    continue
                all_candidates.extend(result)
            
            # 混合排序
            hybrid_candidates = self._hybrid_ranking(all_candidates)
            
            return hybrid_candidates[:top_k]
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return []
    
    def _hybrid_ranking(self, candidates: List[SearchCandidate]) -> List[SearchCandidate]:
        """混合排序"""
        # 按文档ID分组
        doc_groups = {}
        for candidate in candidates:
            doc_id = candidate.document.id
            if doc_id not in doc_groups:
                doc_groups[doc_id] = []
            doc_groups[doc_id].append(candidate)
        
        # 计算混合分数
        hybrid_candidates = []
        for doc_id, group in doc_groups.items():
            hybrid_score = self._calculate_hybrid_score(group)
            
            # 选择最佳候选项作为代表
            best_candidate = max(group, key=lambda x: x.score)
            best_candidate.score = hybrid_score
            best_candidate.source = "hybrid"
            
            # 合并元数据
            metadata = {}
            for candidate in group:
                if candidate.metadata:
                    metadata.update(candidate.metadata)
            best_candidate.metadata = metadata
            
            hybrid_candidates.append(best_candidate)
        
        # 按混合分数排序
        hybrid_candidates.sort(key=lambda x: x.score, reverse=True)
        return hybrid_candidates
    
    def _calculate_hybrid_score(self, candidates: List[SearchCandidate]) -> float:
        """计算混合分数"""
        vector_score = 0.0
        keyword_score = 0.0
        kg_score = 0.0
        
        for candidate in candidates:
            if candidate.source == "vector":
                vector_score = max(vector_score, candidate.score)
            elif candidate.source == "keyword":
                keyword_score = max(keyword_score, candidate.score)
            elif candidate.source == "kg":
                kg_score = max(kg_score, candidate.score)
        
        # 加权平均
        weights = self.settings.retrieval
        hybrid_score = (
            vector_score * weights.vector_weight +
            keyword_score * weights.keyword_weight
        )
        
        # 知识图谱增强
        if kg_score > 0:
            hybrid_score = hybrid_score * 0.8 + kg_score * 0.2
        
        return hybrid_score


class Reranker:
    """重排序器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """加载重排序模型"""
        try:
            if self.settings.retrieval.enable_reranking:
                # 这里应该加载实际的重排序模型
                # 例如 cross-encoder 模型
                logger.info(f"加载重排序模型: {self.settings.retrieval.rerank_model_name}")
                # self.model = CrossEncoder(self.settings.retrieval.rerank_model_name)
        except Exception as e:
            logger.error(f"加载重排序模型失败: {e}")
    
    async def rerank(
        self, 
        query: str, 
        candidates: List[SearchCandidate], 
        top_k: int = 10
    ) -> List[SearchCandidate]:
        """重排序"""
        try:
            if not self.settings.retrieval.enable_reranking or not self.model:
                return candidates[:top_k]
            
            # 准备输入对
            pairs = []
            for candidate in candidates:
                pairs.append([query, candidate.document.content])
            
            # 计算重排序分数
            rerank_scores = await self._compute_rerank_scores(pairs)
            
            # 更新分数
            for i, candidate in enumerate(candidates):
                if i < len(rerank_scores):
                    candidate.score = rerank_scores[i]
                    if candidate.metadata is None:
                        candidate.metadata = {}
                    candidate.metadata["rerank_score"] = rerank_scores[i]
            
            # 重新排序
            candidates.sort(key=lambda x: x.score, reverse=True)
            return candidates[:top_k]
            
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return candidates[:top_k]
    
    async def _compute_rerank_scores(self, pairs: List[List[str]]) -> List[float]:
        """计算重排序分数"""
        # 这里应该实现实际的重排序逻辑
        # 目前返回模拟分数
        return [0.8 - i * 0.1 for i in range(len(pairs))]


class VectorService:
    """增强向量检索服务"""
    
    def __init__(
        self,
        vector_repo: VectorRepository,
        kg_repo: Optional[KnowledgeGraphRepository] = None,
        cache_manager: Optional[CacheManager] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        self.vector_repo = vector_repo
        self.kg_repo = kg_repo
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.settings = get_settings()
        
        # 初始化检索器
        self.vector_retriever = VectorRetriever(vector_repo)
        self.keyword_retriever = KeywordRetriever(vector_repo)
        self.kg_retriever = KnowledgeGraphRetriever(kg_repo) if kg_repo else None
        self.hybrid_retriever = HybridRetriever(
            self.vector_retriever,
            self.keyword_retriever,
            self.kg_retriever
        )
        
        # 初始化重排序器
        self.reranker = Reranker()
    
    async def search(
        self,
        query: str,
        query_embedding: Optional[np.ndarray] = None,
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        enable_reranking: Optional[bool] = None,
        enable_kg_enhancement: Optional[bool] = None
    ) -> SearchResult:
        """执行搜索"""
        start_time = time.time()
        
        try:
            # 参数处理
            if top_k is None:
                top_k = self.settings.retrieval.default_top_k
            top_k = min(top_k, self.settings.retrieval.max_top_k)
            
            if enable_reranking is None:
                enable_reranking = self.settings.retrieval.enable_reranking
            
            if enable_kg_enhancement is None:
                enable_kg_enhancement = self.settings.retrieval.enable_kg_enhancement
            
            # 构建检索上下文
            context = RetrievalContext(
                query=query,
                query_embedding=query_embedding,
                user_id=user_id,
                session_id=session_id,
                filters=filters
            )
            
            # 缓存检查
            cache_key = self._generate_cache_key(context, top_k)
            if self.cache_manager:
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    logger.info("从缓存返回搜索结果")
                    return cached_result
            
            # 执行检索
            if self.settings.retrieval.enable_hybrid_search:
                candidates = await self.hybrid_retriever.retrieve(context, top_k * 2)
            else:
                # 单一检索模式
                if query_embedding is not None:
                    candidates = await self.vector_retriever.retrieve(context, top_k * 2)
                else:
                    candidates = await self.keyword_retriever.retrieve(context, top_k * 2)
            
            # 重排序
            if enable_reranking and candidates:
                candidates = await self.reranker.rerank(query, candidates, top_k)
            else:
                candidates = candidates[:top_k]
            
            # 过滤低质量结果
            candidates = self._filter_candidates(candidates)
            
            # 构建搜索结果
            search_result = SearchResult(
                query=query,
                documents=[c.document for c in candidates],
                scores=[c.score for c in candidates],
                total_found=len(candidates),
                search_time=time.time() - start_time,
                metadata={
                    "retrieval_method": "hybrid" if self.settings.retrieval.enable_hybrid_search else "single",
                    "reranking_enabled": enable_reranking,
                    "kg_enhancement_enabled": enable_kg_enhancement,
                    "candidates_metadata": [c.metadata for c in candidates]
                }
            )
            
            # 缓存结果
            if self.cache_manager:
                await self.cache_manager.set(
                    cache_key, 
                    search_result, 
                    ttl=self.settings.cache.default_ttl
                )
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.record_search_request(
                    query_length=len(query),
                    results_count=len(candidates),
                    search_time=search_result.search_time,
                    cache_hit=False
                )
            
            logger.info(f"搜索完成: 查询='{query}', 结果数={len(candidates)}, 耗时={search_result.search_time:.3f}s")
            return search_result
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_search_error(str(e))
            raise
    
    async def batch_search(
        self,
        queries: List[str],
        query_embeddings: Optional[List[np.ndarray]] = None,
        top_k: int = None,
        **kwargs
    ) -> List[SearchResult]:
        """批量搜索"""
        try:
            tasks = []
            for i, query in enumerate(queries):
                query_embedding = query_embeddings[i] if query_embeddings else None
                task = self.search(
                    query=query,
                    query_embedding=query_embedding,
                    top_k=top_k,
                    **kwargs
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"批量搜索第 {i} 个查询失败: {result}")
                    # 返回空结果
                    valid_results.append(SearchResult(
                        query=queries[i],
                        documents=[],
                        scores=[],
                        total_found=0,
                        search_time=0.0,
                        metadata={"error": str(result)}
                    ))
                else:
                    valid_results.append(result)
            
            return valid_results
            
        except Exception as e:
            logger.error(f"批量搜索失败: {e}")
            raise
    
    async def get_similar_documents(
        self,
        document_id: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """获取相似文档"""
        try:
            # 获取文档嵌入
            document = await self.vector_repo.get_document(document_id)
            if not document or not document.embedding:
                return []
            
            # 搜索相似文档
            context = RetrievalContext(
                query="",
                query_embedding=document.embedding,
                filters=filters
            )
            
            candidates = await self.vector_retriever.retrieve(context, top_k + 1)
            
            # 排除自身
            similar_docs = []
            for candidate in candidates:
                if candidate.document.id != document_id:
                    similar_docs.append(candidate.document)
            
            return similar_docs[:top_k]
            
        except Exception as e:
            logger.error(f"获取相似文档失败: {e}")
            return []
    
    def _generate_cache_key(self, context: RetrievalContext, top_k: int) -> str:
        """生成缓存键"""
        key_parts = [
            "search",
            hash(context.query),
            str(top_k),
            hash(str(context.filters)) if context.filters else "no_filters",
            context.user_id or "anonymous"
        ]
        return ":".join(key_parts)
    
    def _filter_candidates(self, candidates: List[SearchCandidate]) -> List[SearchCandidate]:
        """过滤候选项"""
        threshold = self.settings.retrieval.similarity_threshold
        return [c for c in candidates if c.score >= threshold]
    
    async def get_search_suggestions(
        self,
        partial_query: str,
        limit: int = 10
    ) -> List[str]:
        """获取搜索建议"""
        try:
            # 这里可以实现基于历史查询、热门查询等的建议逻辑
            suggestions = await self.vector_repo.get_query_suggestions(partial_query, limit)
            return suggestions
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    async def get_search_statistics(self) -> Dict[str, Any]:
        """获取搜索统计信息"""
        try:
            stats = {
                "total_documents": await self.vector_repo.get_document_count(),
                "total_vectors": await self.vector_repo.get_vector_count(),
                "index_status": await self.vector_repo.get_index_status(),
                "cache_stats": await self.cache_manager.get_stats() if self.cache_manager else {},
            }
            
            if self.metrics_collector:
                search_metrics = self.metrics_collector.get_search_metrics()
                stats.update(search_metrics)
            
            return stats
        except Exception as e:
            logger.error(f"获取搜索统计失败: {e}")
            return {}


# 工厂函数
async def create_vector_service(
    vector_repo: VectorRepository,
    kg_repo: Optional[KnowledgeGraphRepository] = None,
    cache_manager: Optional[CacheManager] = None,
    metrics_collector: Optional[MetricsCollector] = None
) -> VectorService:
    """创建向量服务实例"""
    service = VectorService(
        vector_repo=vector_repo,
        kg_repo=kg_repo,
        cache_manager=cache_manager,
        metrics_collector=metrics_collector
    )
    
    logger.info("向量检索服务已初始化")
    return service 