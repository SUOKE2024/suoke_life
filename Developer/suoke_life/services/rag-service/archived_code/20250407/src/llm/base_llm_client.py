#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM客户端基类
==========
定义所有LLM客户端必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class BaseLLMClient(ABC):
    """LLM客户端基类，定义通用接口"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            str: 生成的文本
        """
        pass
        
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Any:
        """
        流式生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数
            
        Returns:
            迭代器，产生生成的文本片段
        """
        pass
        
    @abstractmethod
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        获取文本的嵌入向量
        
        Args:
            text: 输入文本
            **kwargs: 其他参数
            
        Returns:
            List[float]: 嵌入向量
        """
        pass
        
    @abstractmethod
    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        批量获取文本的嵌入向量
        
        Args:
            texts: 输入文本列表
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        pass
        
    @abstractmethod
    def rag_complete(self, query: str, contexts: List[Dict[str, Any]], **kwargs) -> str:
        """
        基于检索上下文生成回答
        
        Args:
            query: 查询文本
            contexts: 上下文信息列表
            **kwargs: 其他参数
            
        Returns:
            str: 生成的回答
        """
        pass
        
    @abstractmethod
    def rag_complete_stream(self, query: str, contexts: List[Dict[str, Any]], **kwargs) -> Any:
        """
        基于检索上下文流式生成回答
        
        Args:
            query: 查询文本
            contexts: 上下文信息列表
            **kwargs: 其他参数
            
        Returns:
            迭代器，产生生成的文本片段
        """
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查LLM服务是否可用
        
        Returns:
            bool: 服务是否可用
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