#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检索器基类定义
"""

import abc
import time
from typing import List, Dict, Any, Optional
from ..model.document import Document, RetrieveResult


class BaseRetriever(abc.ABC):
    """
    检索器基类，定义了检索器的通用接口
    """
    
    @abc.abstractmethod
    async def initialize(self):
        """初始化检索器"""
        pass
    
    @abc.abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        collection_names: Optional[List[str]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0,
        rerank: bool = False
    ) -> RetrieveResult:
        """
        根据查询检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            collection_names: 集合名称列表，为空则搜索所有集合
            metadata_filter: 元数据过滤条件
            score_threshold: 相关性分数阈值
            rerank: 是否启用重排序
            
        Returns:
            检索结果
        """
        start_time = time.time()
        
        # 子类需要实现具体的检索逻辑
        documents = await self._do_retrieve(
            query=query,
            top_k=top_k,
            collection_names=collection_names,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
            rerank=rerank
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return RetrieveResult(
            documents=documents,
            latency_ms=latency_ms
        )
    
    @abc.abstractmethod
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
        实际执行检索的内部方法
        
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    async def close(self):
        """关闭检索器及相关连接"""
        pass