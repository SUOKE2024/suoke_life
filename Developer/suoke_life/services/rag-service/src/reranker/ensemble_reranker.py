#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
集成重排序器
========
组合多个重排序器实现的集成重排序器
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

from .base_reranker import BaseReranker


class EnsembleReranker(BaseReranker):
    """集成重排序器，组合多个重排序器"""
    
    def __init__(
        self,
        rerankers: List[Tuple[BaseReranker, float]],
        normalize_scores: bool = True,
        **kwargs
    ):
        """
        初始化集成重排序器
        
        Args:
            rerankers: 重排序器及其权重的列表，每项为(reranker, weight)
            normalize_scores: 是否标准化得分
            **kwargs: 其他参数
        """
        self._rerankers = rerankers
        self._normalize_scores = normalize_scores
        
        # 确保权重之和为1
        total_weight = sum(weight for _, weight in rerankers)
        if total_weight != 1.0:
            logger.warning(f"重排序器权重总和 ({total_weight}) 不为1，将自动归一化")
            self._rerankers = [(reranker, weight / total_weight) for reranker, weight in rerankers]
            
        logger.info(f"创建集成重排序器，包含 {len(rerankers)} 个子重排序器")
    
    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return "Ensemble(" + ",".join([r.model_name for r, _ in self._rerankers]) + ")"
    
    def _normalize_score_list(self, scores: List[float]) -> List[float]:
        """
        标准化得分列表
        
        Args:
            scores: 得分列表
            
        Returns:
            List[float]: 标准化后的得分列表
        """
        if not scores:
            return []
            
        min_score = min(scores)
        max_score = max(scores)
        
        # 如果所有得分相同，返回原始得分
        if max_score == min_score:
            return scores
            
        # 归一化到[0,1]范围
        return [(score - min_score) / (max_score - min_score) for score in scores]
    
    def compute_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        计算单个文档的得分
        
        Args:
            query: 查询文本
            document: 文档，包含text和metadata字段
            
        Returns:
            float: 得分
        """
        total_score = 0.0
        
        # 计算每个重排序器的加权得分总和
        for reranker, weight in self._rerankers:
            score = reranker.compute_score(query, document)
            total_score += score * weight
            
        return total_score
    
    def batch_compute_scores(
        self, 
        query: str, 
        documents: List[Dict[str, Any]]
    ) -> List[float]:
        """
        批量计算文档得分
        
        Args:
            query: 查询文本
            documents: 文档列表，包含text和metadata字段
            
        Returns:
            List[float]: 得分列表
        """
        if not documents:
            return []
            
        # 初始化得分列表
        total_scores = [0.0] * len(documents)
        
        # 对每个重排序器计算得分并加权求和
        for reranker, weight in self._rerankers:
            scores = reranker.batch_compute_scores(query, documents)
            
            # 如果需要标准化得分
            if self._normalize_scores:
                scores = self._normalize_score_list(scores)
                
            # 累加加权得分
            for i, score in enumerate(scores):
                total_scores[i] += score * weight
                
        return total_scores
    
    def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        重排序文档列表
        
        Args:
            query: 查询文本
            documents: 文档列表，包含text和metadata字段
            top_n: 返回的结果数量，None表示返回所有结果
            
        Returns:
            List[Dict[str, Any]]: 重排序后的文档列表
        """
        if not documents:
            return []
            
        # 计算所有文档的得分
        scores = self.batch_compute_scores(query, documents)
        
        # 为每个文档添加重排序得分
        scored_docs = []
        for doc, score in zip(documents, scores):
            doc_copy = doc.copy()
            doc_copy["rerank_score"] = score
            # 如果已经有score字段，保留为原始得分
            if "score" in doc_copy:
                doc_copy["original_score"] = doc_copy["score"]
            doc_copy["score"] = score
            scored_docs.append(doc_copy)
            
        # 按得分排序
        sorted_docs = sorted(scored_docs, key=lambda x: x["score"], reverse=True)
        
        # 返回top_n结果
        if top_n is not None:
            sorted_docs = sorted_docs[:top_n]
            
        return sorted_docs 