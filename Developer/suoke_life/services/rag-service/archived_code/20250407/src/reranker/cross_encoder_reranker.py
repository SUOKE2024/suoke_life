#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CrossEncoder重排序器
================
使用CrossEncoder模型实现的重排序器
"""

import os
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

from sentence_transformers import CrossEncoder

from .base_reranker import BaseReranker


class CrossEncoderReranker(BaseReranker):
    """CrossEncoder重排序器，使用CrossEncoder模型"""
    
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        cache_dir: Optional[str] = None,
        device: Optional[str] = None,
        batch_size: int = 32,
        **kwargs
    ):
        """
        初始化CrossEncoder重排序器
        
        Args:
            model_name: 模型名称
            cache_dir: 模型缓存目录
            device: 设备，如cuda:0, cpu等，None表示自动选择
            batch_size: 批处理大小
            **kwargs: 其他参数
        """
        self._model_name = model_name
        self._cache_dir = cache_dir
        self._device = device
        self._batch_size = batch_size
        self._model = None
        self._load_model()
        
    def _load_model(self) -> None:
        """加载CrossEncoder模型"""
        try:
            start_time = time.time()
            logger.info(f"正在加载CrossEncoder模型: {self._model_name}")
            
            # 设置模型选项
            model_kwargs = {}
            if self._cache_dir:
                model_kwargs["cache_folder"] = self._cache_dir
            if self._device:
                model_kwargs["device"] = self._device
            
            # 加载模型
            self._model = CrossEncoder(self._model_name, **model_kwargs)
            
            elapsed_time = time.time() - start_time
            logger.info(f"CrossEncoder模型加载完成, 耗时: {elapsed_time:.2f} 秒")
            
        except Exception as e:
            logger.error(f"加载CrossEncoder模型失败: {str(e)}")
            raise RuntimeError(f"加载CrossEncoder模型失败: {str(e)}")
    
    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return self._model_name
    
    def compute_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        计算单个文档的得分
        
        Args:
            query: 查询文本
            document: 文档，包含text和metadata字段
            
        Returns:
            float: 得分
        """
        text = document.get("text", "")
        if not text or not query:
            return 0.0
            
        return self._model.predict([(query, text)])[0]
    
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
        if not documents or not query:
            return [0.0] * len(documents)
            
        # 准备输入
        pairs = [(query, doc.get("text", "")) for doc in documents]
        
        # 使用CrossEncoder批量预测
        scores = self._model.predict(
            pairs,
            batch_size=self._batch_size,
            show_progress_bar=len(pairs) > 100
        )
        
        return scores.tolist() if hasattr(scores, "tolist") else scores
    
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