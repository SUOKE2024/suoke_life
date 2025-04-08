#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重排序基类
=======
定义所有重排序器必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseReranker(ABC):
    """重排序基类，定义通用接口"""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def compute_score(self, query: str, document: Dict[str, Any]) -> float:
        """
        计算单个文档的得分
        
        Args:
            query: 查询文本
            document: 文档，包含text和metadata字段
            
        Returns:
            float: 得分
        """
        pass
        
    @abstractmethod
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
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        获取模型名称
        
        Returns:
            str: 模型名称
        """
        pass 