#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
向量存储基类
=========
定义向量数据库的抽象接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseVectorStore(ABC):
    """向量存储基类，定义通用接口"""
    
    @abstractmethod
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, 
                 ids: Optional[List[str]] = None) -> List[str]:
        """
        添加文本到向量存储
        
        Args:
            texts: 文本列表
            metadatas: 文本元数据列表
            ids: 文本ID列表
            
        Returns:
            List[str]: 添加的文本ID列表
        """
        pass
        
    @abstractmethod
    def add_embeddings(self, embeddings: List[List[float]], texts: List[str], 
                      metadatas: Optional[List[Dict[str, Any]]] = None, 
                      ids: Optional[List[str]] = None) -> List[str]:
        """
        添加预计算的嵌入向量到存储
        
        Args:
            embeddings: 嵌入向量列表
            texts: 文本列表
            metadatas: 文本元数据列表
            ids: 文本ID列表
            
        Returns:
            List[str]: 添加的文本ID列表
        """
        pass
        
    @abstractmethod
    def similarity_search(self, query: str, k: int = 5, 
                         filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        基于查询文本进行相似性搜索
        
        Args:
            query: 查询文本
            k: 返回的结果数量
            filter: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 相似结果列表
        """
        pass
        
    @abstractmethod
    def similarity_search_by_vector(self, embedding: List[float], k: int = 5, 
                                   filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        基于嵌入向量进行相似性搜索
        
        Args:
            embedding: 查询嵌入向量
            k: 返回的结果数量
            filter: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 相似结果列表
        """
        pass
        
    @abstractmethod
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        从存储中删除文档
        
        Args:
            ids: 要删除的文档ID或ID列表
            
        Returns:
            bool: 操作是否成功
        """
        pass
        
    @abstractmethod
    def get(self, ids: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        获取指定ID的文档
        
        Args:
            ids: 要获取的文档ID或ID列表
            
        Returns:
            List[Dict[str, Any]]: 文档列表
        """
        pass
        
    @abstractmethod
    def count(self) -> int:
        """
        获取存储中的文档数量
        
        Returns:
            int: 文档数量
        """
        pass
        
    @abstractmethod
    def clear(self) -> bool:
        """
        清空向量存储
        
        Returns:
            bool: 操作是否成功
        """
        pass 