#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
生成器基类定义
"""

import abc
import time
from typing import List, Dict, Any, AsyncGenerator, Optional
from ..model.document import Document, DocumentReference, GenerateResult


class BaseGenerator(abc.ABC):
    """
    生成器基类，定义了生成器的通用接口
    """
    
    @abc.abstractmethod
    async def initialize(self):
        """初始化生成器"""
        pass
    
    @abc.abstractmethod
    async def generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> GenerateResult:
        """
        根据查询和上下文文档生成回答
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Returns:
            生成结果
        """
        start_time = time.time()
        
        # 子类需要实现具体的生成逻辑
        answer, references = await self._do_generate(
            query=query,
            context_documents=context_documents,
            system_prompt=system_prompt,
            generation_params=generation_params,
            user_id=user_id
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return GenerateResult(
            answer=answer,
            references=references,
            latency_ms=latency_ms
        )
    
    @abc.abstractmethod
    async def _do_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> tuple[str, List[DocumentReference]]:
        """
        实际执行生成的内部方法
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Returns:
            生成的回答和引用的文档
        """
        pass
    
    @abc.abstractmethod
    async def stream_generate(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> AsyncGenerator[tuple[str, bool, Optional[List[DocumentReference]]], None]:
        """
        流式生成回答
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            generation_params: 生成参数
            user_id: 用户ID
            
        Yields:
            元组: (答案片段, 是否最后一个片段, 引用的文档[仅在最后一个片段中])
        """
        pass
    
    @abc.abstractmethod
    def create_prompt(
        self,
        query: str,
        context_documents: List[Document],
        system_prompt: Optional[str] = None
    ) -> str:
        """
        创建包含上下文的提示
        
        Args:
            query: 用户查询
            context_documents: 上下文文档
            system_prompt: 系统提示词
            
        Returns:
            完整的提示
        """
        pass
    
    @abc.abstractmethod
    def extract_references(
        self,
        answer: str,
        context_documents: List[Document]
    ) -> List[DocumentReference]:
        """
        从回答和上下文文档中提取引用
        
        Args:
            answer: 生成的回答
            context_documents: 上下文文档
            
        Returns:
            引用的文档列表
        """
        pass
    
    @abc.abstractmethod
    async def close(self):
        """关闭生成器及相关连接"""
        pass