#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级检索器 - 支持多种检索策略和智能策略选择
"""

import asyncio
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from ..model.document import Document, DocumentMetadata
from ..service.embedding_service import EmbeddingService
from ..repository.milvus_repository import MilvusRepository
from ..observability.metrics import MetricsCollector
from ..resilience.circuit_breaker import CircuitBreakerService

class RetrievalStrategy(str, Enum):
    """检索策略枚举"""
    VECTOR = "vector"                    # 纯向量检索
    KEYWORD = "keyword"                  # 关键词检索
    HYBRID = "hybrid"                    # 混合检索
    SEMANTIC_ENHANCED = "semantic_enhanced"  # 语义增强检索
    TCM_SPECIALIZED = "tcm_specialized"  # 中医专业检索
    MULTIMODAL = "multimodal"           # 多模态检索

@dataclass
class RetrievalContext:
    """检索上下文"""
    query: str
    query_type: str = "general"         # general, medical, tcm, symptom, formula
    user_profile: Optional[Dict[str, Any]] = None
    session_context: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 10
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    enable_explanation: bool = False

@dataclass
class RetrievalResult:
    """检索结果"""
    documents: List[Document]
    scores: List[float]
    strategy_used: RetrievalStrategy
    total_time: float
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class QueryAnalyzer:
    """查询分析器"""
    
    def __init__(self):
        # 中医术语词典
        self.tcm_terms = {
            "症状": ["头痛", "发热", "咳嗽", "胸闷", "心悸", "失眠", "便秘", "腹泻"],
            "脏腑": ["心", "肝", "脾", "肺", "肾", "胃", "胆", "小肠", "大肠", "膀胱"],
            "病理": ["气虚", "血瘀", "痰湿", "阴虚", "阳虚", "湿热", "寒湿"],
            "治法": ["补气", "活血", "化痰", "清热", "温阳", "滋阴", "祛湿"],
            "方剂": ["四君子汤", "逍遥散", "六味地黄丸", "补中益气汤"]
        }
        
        # 查询意图模式
        self.intent_patterns = {
            "symptom_query": [r"什么症状", r"有.*症状", r"出现.*症状"],
            "treatment_query": [r"怎么治疗", r"如何调理", r"治疗方法"],
            "formula_query": [r"什么方剂", r"用什么药", r"推荐.*方"],
            "constitution_query": [r"什么体质", r"体质.*特点", r"体质分析"],
            "prevention_query": [r"如何预防", r"预防.*方法", r"养生.*建议"]
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        分析查询
        
        Args:
            query: 查询文本
            
        Returns:
            分析结果
        """
        analysis = {
            "query_type": "general",
            "intent": "unknown",
            "tcm_terms_found": [],
            "complexity": "simple",
            "language": "zh",
            "entities": [],
            "keywords": []
        }
        
        # 检测中医术语
        for category, terms in self.tcm_terms.items():
            found_terms = [term for term in terms if term in query]
            if found_terms:
                analysis["tcm_terms_found"].extend(found_terms)
                analysis["query_type"] = "tcm"
        
        # 检测查询意图
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    analysis["intent"] = intent
                    break
        
        # 评估查询复杂度
        if len(query) > 50 or "和" in query or "或" in query:
            analysis["complexity"] = "complex"
        elif len(analysis["tcm_terms_found"]) > 2:
            analysis["complexity"] = "medium"
        
        # 提取关键词
        analysis["keywords"] = self._extract_keywords(query)
        
        return analysis
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取，实际应用中可以使用更复杂的NLP技术
        import jieba
        words = jieba.lcut(query)
        # 过滤停用词
        stopwords = {"的", "是", "在", "有", "和", "或", "但", "如果", "因为", "所以"}
        keywords = [word for word in words if len(word) > 1 and word not in stopwords]
        return keywords

class StrategySelector:
    """策略选择器"""
    
    def __init__(self):
        self.strategy_rules = {
            RetrievalStrategy.TCM_SPECIALIZED: self._should_use_tcm_specialized,
            RetrievalStrategy.SEMANTIC_ENHANCED: self._should_use_semantic_enhanced,
            RetrievalStrategy.HYBRID: self._should_use_hybrid,
            RetrievalStrategy.VECTOR: self._should_use_vector,
            RetrievalStrategy.KEYWORD: self._should_use_keyword,
        }
    
    def select_strategy(self, context: RetrievalContext, query_analysis: Dict[str, Any]) -> RetrievalStrategy:
        """
        选择最佳检索策略
        
        Args:
            context: 检索上下文
            query_analysis: 查询分析结果
            
        Returns:
            选择的策略
        """
        # 按优先级检查策略
        for strategy, rule_func in self.strategy_rules.items():
            if rule_func(context, query_analysis):
                return strategy
        
        # 默认使用混合检索
        return RetrievalStrategy.HYBRID
    
    def _should_use_tcm_specialized(self, context: RetrievalContext, analysis: Dict[str, Any]) -> bool:
        """是否使用中医专业检索"""
        return (
            analysis["query_type"] == "tcm" or
            len(analysis["tcm_terms_found"]) >= 2 or
            context.query_type == "tcm"
        )
    
    def _should_use_semantic_enhanced(self, context: RetrievalContext, analysis: Dict[str, Any]) -> bool:
        """是否使用语义增强检索"""
        return (
            analysis["complexity"] == "complex" or
            analysis["intent"] in ["treatment_query", "prevention_query"]
        )
    
    def _should_use_hybrid(self, context: RetrievalContext, analysis: Dict[str, Any]) -> bool:
        """是否使用混合检索"""
        return (
            analysis["complexity"] in ["medium", "complex"] or
            len(analysis["keywords"]) > 3
        )
    
    def _should_use_vector(self, context: RetrievalContext, analysis: Dict[str, Any]) -> bool:
        """是否使用纯向量检索"""
        return analysis["complexity"] == "simple" and len(analysis["keywords"]) <= 2
    
    def _should_use_keyword(self, context: RetrievalContext, analysis: Dict[str, Any]) -> bool:
        """是否使用关键词检索"""
        return len(analysis["keywords"]) == 1

class QueryProcessor:
    """查询处理器"""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.tcm_synonyms = {
            "头痛": ["头疼", "脑袋疼", "偏头痛"],
            "发热": ["发烧", "体温升高", "热症"],
            "咳嗽": ["咳", "干咳", "咳痰"],
        }
    
    async def preprocess_query(self, context: RetrievalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理查询
        
        Args:
            context: 检索上下文
            analysis: 查询分析结果
            
        Returns:
            处理后的查询信息
        """
        processed = {
            "original_query": context.query,
            "processed_query": context.query,
            "expanded_queries": [],
            "embedding": None,
            "keywords": analysis["keywords"]
        }
        
        # 查询扩展
        if analysis["query_type"] == "tcm":
            processed["expanded_queries"] = self._expand_tcm_query(context.query)
        
        # 生成查询嵌入
        processed["embedding"] = await self.embedding_service.embed_text(context.query)
        
        # 上下文增强
        if context.session_context:
            processed["processed_query"] = self._enhance_with_context(
                context.query, context.session_context
            )
        
        return processed
    
    def _expand_tcm_query(self, query: str) -> List[str]:
        """扩展中医查询"""
        expanded = []
        
        # 同义词扩展
        for term, synonyms in self.tcm_synonyms.items():
            if term in query:
                for synonym in synonyms:
                    expanded.append(query.replace(term, synonym))
        
        return expanded
    
    def _enhance_with_context(self, query: str, context: Dict[str, Any]) -> str:
        """使用上下文增强查询"""
        # 添加用户历史症状信息
        if "symptoms" in context:
            symptoms = ", ".join(context["symptoms"][-3:])  # 最近3个症状
            return f"{query} (相关症状: {symptoms})"
        
        return query

class ResultProcessor:
    """结果处理器"""
    
    def __init__(self):
        self.rerank_model = None  # 可以加载重排序模型
    
    async def postprocess_results(
        self,
        documents: List[Document],
        scores: List[float],
        context: RetrievalContext,
        strategy: RetrievalStrategy
    ) -> Tuple[List[Document], List[float]]:
        """
        后处理检索结果
        
        Args:
            documents: 文档列表
            scores: 分数列表
            context: 检索上下文
            strategy: 使用的策略
            
        Returns:
            处理后的文档和分数
        """
        # 重排序
        if context.enable_reranking and len(documents) > 1:
            documents, scores = await self._rerank_results(documents, scores, context.query)
        
        # 多样性过滤
        documents, scores = self._diversify_results(documents, scores)
        
        # 质量过滤
        documents, scores = self._filter_by_quality(documents, scores, context.similarity_threshold)
        
        # 添加解释信息
        if context.enable_explanation:
            self._add_explanations(documents, context.query, strategy)
        
        return documents, scores
    
    async def _rerank_results(
        self,
        documents: List[Document],
        scores: List[float],
        query: str
    ) -> Tuple[List[Document], List[float]]:
        """重排序结果"""
        # 简化的重排序逻辑，实际应用中可以使用专门的重排序模型
        # 这里基于文档长度和关键词匹配度进行简单重排序
        
        reranked_pairs = []
        for doc, score in zip(documents, scores):
            # 计算关键词匹配度
            keyword_score = self._calculate_keyword_match(doc.content, query)
            # 计算文档质量分数
            quality_score = self._calculate_quality_score(doc)
            # 综合分数
            final_score = 0.5 * score + 0.3 * keyword_score + 0.2 * quality_score
            reranked_pairs.append((doc, final_score))
        
        # 按分数排序
        reranked_pairs.sort(key=lambda x: x[1], reverse=True)
        
        documents = [pair[0] for pair in reranked_pairs]
        scores = [pair[1] for pair in reranked_pairs]
        
        return documents, scores
    
    def _calculate_keyword_match(self, content: str, query: str) -> float:
        """计算关键词匹配度"""
        import jieba
        query_words = set(jieba.lcut(query))
        content_words = set(jieba.lcut(content))
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)
    
    def _calculate_quality_score(self, document: Document) -> float:
        """计算文档质量分数"""
        score = 0.0
        
        # 基于文档长度
        if 100 <= len(document.content) <= 1000:
            score += 0.3
        
        # 基于元数据
        if document.metadata:
            if document.metadata.source == "authoritative":
                score += 0.4
            if document.metadata.confidence and document.metadata.confidence > 0.8:
                score += 0.3
        
        return min(score, 1.0)
    
    def _diversify_results(
        self,
        documents: List[Document],
        scores: List[float]
    ) -> Tuple[List[Document], List[float]]:
        """多样性过滤"""
        if len(documents) <= 3:
            return documents, scores
        
        # 简单的多样性过滤：避免内容过于相似的文档
        diversified_docs = []
        diversified_scores = []
        
        for i, (doc, score) in enumerate(zip(documents, scores)):
            is_diverse = True
            for existing_doc in diversified_docs:
                similarity = self._calculate_content_similarity(doc.content, existing_doc.content)
                if similarity > 0.8:  # 相似度阈值
                    is_diverse = False
                    break
            
            if is_diverse:
                diversified_docs.append(doc)
                diversified_scores.append(score)
        
        return diversified_docs, diversified_scores
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度"""
        # 简化的相似度计算
        import jieba
        words1 = set(jieba.lcut(content1))
        words2 = set(jieba.lcut(content2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _filter_by_quality(
        self,
        documents: List[Document],
        scores: List[float],
        threshold: float
    ) -> Tuple[List[Document], List[float]]:
        """按质量过滤"""
        filtered_docs = []
        filtered_scores = []
        
        for doc, score in zip(documents, scores):
            if score >= threshold:
                filtered_docs.append(doc)
                filtered_scores.append(score)
        
        return filtered_docs, filtered_scores
    
    def _add_explanations(self, documents: List[Document], query: str, strategy: RetrievalStrategy):
        """添加解释信息"""
        for doc in documents:
            if not doc.metadata:
                doc.metadata = DocumentMetadata()
            
            explanation = f"使用{strategy.value}策略检索到此文档"
            if hasattr(doc.metadata, 'explanation'):
                doc.metadata.explanation = explanation

class AdvancedRetriever:
    """高级检索器"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        milvus_repository: MilvusRepository,
        embedding_service: EmbeddingService,
        metrics_collector: MetricsCollector,
        circuit_breaker: CircuitBreakerService
    ):
        self.config = config
        self.milvus_repository = milvus_repository
        self.embedding_service = embedding_service
        self.metrics_collector = metrics_collector
        self.circuit_breaker = circuit_breaker
        
        # 初始化组件
        self.query_analyzer = QueryAnalyzer()
        self.strategy_selector = StrategySelector()
        self.query_processor = QueryProcessor(embedding_service)
        self.result_processor = ResultProcessor()
        
        # 策略实现映射
        self.strategy_implementations = {
            RetrievalStrategy.VECTOR: self._vector_retrieval,
            RetrievalStrategy.KEYWORD: self._keyword_retrieval,
            RetrievalStrategy.HYBRID: self._hybrid_retrieval,
            RetrievalStrategy.SEMANTIC_ENHANCED: self._semantic_enhanced_retrieval,
            RetrievalStrategy.TCM_SPECIALIZED: self._tcm_specialized_retrieval,
            RetrievalStrategy.MULTIMODAL: self._multimodal_retrieval,
        }
    
    async def retrieve(self, context: RetrievalContext) -> RetrievalResult:
        """
        执行检索
        
        Args:
            context: 检索上下文
            
        Returns:
            检索结果
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 分析查询
            query_analysis = self.query_analyzer.analyze_query(context.query)
            logger.info(f"查询分析结果: {query_analysis}")
            
            # 选择策略
            strategy = self.strategy_selector.select_strategy(context, query_analysis)
            logger.info(f"选择的检索策略: {strategy}")
            
            # 预处理查询
            processed_query = await self.query_processor.preprocess_query(context, query_analysis)
            
            # 执行检索
            documents, scores = await self.strategy_implementations[strategy](
                context, processed_query, query_analysis
            )
            
            # 后处理结果
            documents, scores = await self.result_processor.postprocess_results(
                documents, scores, context, strategy
            )
            
            # 记录指标
            end_time = asyncio.get_event_loop().time()
            total_time = end_time - start_time
            
            await self._record_metrics(strategy, total_time, len(documents))
            
            # 生成解释
            explanation = None
            if context.enable_explanation:
                explanation = self._generate_explanation(strategy, query_analysis, len(documents))
            
            return RetrievalResult(
                documents=documents,
                scores=scores,
                strategy_used=strategy,
                total_time=total_time,
                explanation=explanation,
                metadata={
                    "query_analysis": query_analysis,
                    "processed_query": processed_query
                }
            )
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            await self.metrics_collector.increment_counter("retrieval_errors")
            raise
    
    async def _vector_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """向量检索"""
        embedding = processed_query["embedding"]
        
        results = await self.milvus_repository.search(
            embedding=embedding,
            top_k=context.top_k,
            filters=context.filters
        )
        
        documents = [result["document"] for result in results]
        scores = [result["score"] for result in results]
        
        return documents, scores
    
    async def _keyword_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """关键词检索"""
        keywords = processed_query["keywords"]
        
        # 使用BM25或其他关键词检索算法
        # 这里简化实现
        results = await self.milvus_repository.keyword_search(
            keywords=keywords,
            top_k=context.top_k,
            filters=context.filters
        )
        
        documents = [result["document"] for result in results]
        scores = [result["score"] for result in results]
        
        return documents, scores
    
    async def _hybrid_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """混合检索"""
        # 并行执行向量检索和关键词检索
        vector_task = self._vector_retrieval(context, processed_query, analysis)
        keyword_task = self._keyword_retrieval(context, processed_query, analysis)
        
        vector_results, keyword_results = await asyncio.gather(vector_task, keyword_task)
        
        # 合并和重新排序结果
        combined_results = self._combine_results(
            vector_results, keyword_results,
            vector_weight=self.config.get("vector_weight", 0.7),
            keyword_weight=self.config.get("keyword_weight", 0.3)
        )
        
        # 取前top_k个结果
        combined_results = combined_results[:context.top_k]
        
        documents = [result[0] for result in combined_results]
        scores = [result[1] for result in combined_results]
        
        return documents, scores
    
    async def _semantic_enhanced_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """语义增强检索"""
        # 使用扩展查询进行多次检索
        all_documents = []
        all_scores = []
        
        # 原始查询检索
        docs, scores = await self._vector_retrieval(context, processed_query, analysis)
        all_documents.extend(docs)
        all_scores.extend(scores)
        
        # 扩展查询检索
        for expanded_query in processed_query["expanded_queries"]:
            expanded_embedding = await self.embedding_service.embed_text(expanded_query)
            expanded_processed = {**processed_query, "embedding": expanded_embedding}
            
            docs, scores = await self._vector_retrieval(context, expanded_processed, analysis)
            all_documents.extend(docs)
            all_scores.extend([s * 0.8 for s in scores])  # 降权扩展查询结果
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_documents, all_scores)
        unique_results = sorted(unique_results, key=lambda x: x[1], reverse=True)
        
        documents = [result[0] for result in unique_results[:context.top_k]]
        scores = [result[1] for result in unique_results[:context.top_k]]
        
        return documents, scores
    
    async def _tcm_specialized_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """中医专业检索"""
        # 添加中医特定的过滤条件
        tcm_filters = {**(context.filters or {}), "domain": "tcm"}
        tcm_context = RetrievalContext(
            query=context.query,
            query_type="tcm",
            filters=tcm_filters,
            top_k=context.top_k,
            similarity_threshold=context.similarity_threshold * 0.9  # 降低阈值
        )
        
        # 使用混合检索但专注于中医内容
        return await self._hybrid_retrieval(tcm_context, processed_query, analysis)
    
    async def _multimodal_retrieval(
        self,
        context: RetrievalContext,
        processed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Tuple[List[Document], List[float]]:
        """多模态检索"""
        # 目前主要处理文本，未来可以扩展到图像、音频等
        return await self._semantic_enhanced_retrieval(context, processed_query, analysis)
    
    def _combine_results(
        self,
        vector_results: Tuple[List[Document], List[float]],
        keyword_results: Tuple[List[Document], List[float]],
        vector_weight: float,
        keyword_weight: float
    ) -> List[Tuple[Document, float]]:
        """合并检索结果"""
        vector_docs, vector_scores = vector_results
        keyword_docs, keyword_scores = keyword_results
        
        # 创建文档ID到分数的映射
        doc_scores = {}
        
        # 添加向量检索结果
        for doc, score in zip(vector_docs, vector_scores):
            doc_id = doc.id
            doc_scores[doc_id] = {
                "document": doc,
                "vector_score": score,
                "keyword_score": 0.0
            }
        
        # 添加关键词检索结果
        for doc, score in zip(keyword_docs, keyword_scores):
            doc_id = doc.id
            if doc_id in doc_scores:
                doc_scores[doc_id]["keyword_score"] = score
            else:
                doc_scores[doc_id] = {
                    "document": doc,
                    "vector_score": 0.0,
                    "keyword_score": score
                }
        
        # 计算综合分数
        combined_results = []
        for doc_info in doc_scores.values():
            combined_score = (
                vector_weight * doc_info["vector_score"] +
                keyword_weight * doc_info["keyword_score"]
            )
            combined_results.append((doc_info["document"], combined_score))
        
        # 按分数排序
        combined_results.sort(key=lambda x: x[1], reverse=True)
        
        return combined_results
    
    def _deduplicate_results(
        self,
        documents: List[Document],
        scores: List[float]
    ) -> List[Tuple[Document, float]]:
        """去重结果"""
        seen_ids = set()
        unique_results = []
        
        for doc, score in zip(documents, scores):
            if doc.id not in seen_ids:
                seen_ids.add(doc.id)
                unique_results.append((doc, score))
        
        return unique_results
    
    def _generate_explanation(
        self,
        strategy: RetrievalStrategy,
        analysis: Dict[str, Any],
        result_count: int
    ) -> str:
        """生成检索解释"""
        explanations = {
            RetrievalStrategy.VECTOR: "基于语义相似度的向量检索",
            RetrievalStrategy.KEYWORD: "基于关键词匹配的检索",
            RetrievalStrategy.HYBRID: "结合向量和关键词的混合检索",
            RetrievalStrategy.SEMANTIC_ENHANCED: "语义增强检索，包含查询扩展",
            RetrievalStrategy.TCM_SPECIALIZED: "专门针对中医内容的检索",
            RetrievalStrategy.MULTIMODAL: "多模态检索"
        }
        
        base_explanation = explanations.get(strategy, "未知检索策略")
        
        if analysis["query_type"] == "tcm":
            base_explanation += f"，检测到{len(analysis['tcm_terms_found'])}个中医术语"
        
        base_explanation += f"，返回{result_count}个相关结果"
        
        return base_explanation
    
    async def _record_metrics(self, strategy: RetrievalStrategy, time_taken: float, result_count: int):
        """记录指标"""
        await self.metrics_collector.record_histogram(
            "retrieval_duration_seconds",
            time_taken,
            {"strategy": strategy.value}
        )
        
        await self.metrics_collector.record_histogram(
            "retrieval_result_count",
            result_count,
            {"strategy": strategy.value}
        )
        
        await self.metrics_collector.increment_counter(
            "retrieval_requests_total",
            {"strategy": strategy.value}
        ) 