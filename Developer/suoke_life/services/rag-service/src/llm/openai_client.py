#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI客户端
=========
提供与OpenAI API的集成
"""

import time
import json
from typing import List, Dict, Any, Optional, Union, Generator
from loguru import logger

import openai
from openai import OpenAI

from .base_llm_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """OpenAI客户端，实现与OpenAI API的集成"""
    
    def __init__(
        self,
        api_key: str,
        api_base: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        embedding_model: str = "text-embedding-3-small",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 30,
        **kwargs
    ):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: OpenAI API密钥
            api_base: API基础URL，如果不提供则使用OpenAI默认值
            model_name: 模型名称
            embedding_model: 嵌入模型名称
            max_tokens: 最大生成令牌数
            temperature: 温度
            timeout: 请求超时时间(秒)
            **kwargs: 其他参数
        """
        self._api_key = api_key
        self._api_base = api_base
        self._model_name = model_name
        self._embedding_model = embedding_model
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._timeout = timeout
        self._client = None
        self._init_client()
        
    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            client_kwargs = {"api_key": self._api_key, "timeout": self._timeout}
            
            if self._api_base:
                client_kwargs["base_url"] = self._api_base
                
            self._client = OpenAI(**client_kwargs)
            
            logger.info(f"OpenAI客户端初始化成功，使用模型: {self._model_name}")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")
            self._client = None
    
    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return self._model_name
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        if not self._client:
            return False
            
        try:
            # 简单的可用性检查
            self._client.models.list(limit=1)
            return True
        except Exception as e:
            logger.error(f"OpenAI服务不可用: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数，可覆盖构造函数中的默认值
            
        Returns:
            str: 生成的文本
        """
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("model", self._model_name)
            max_tokens = kwargs.get("max_tokens", self._max_tokens)
            temperature = kwargs.get("temperature", self._temperature)
            
            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI生成文本失败: {e}")
            raise
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        流式生成文本
        
        Args:
            prompt: 提示文本
            **kwargs: 其他参数，可覆盖构造函数中的默认值
            
        Returns:
            Generator[str, None, None]: 生成的文本片段
        """
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("model", self._model_name)
            max_tokens = kwargs.get("max_tokens", self._max_tokens)
            temperature = kwargs.get("temperature", self._temperature)
            
            response = self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI流式生成文本失败: {e}")
            raise
    
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """
        获取文本的嵌入向量
        
        Args:
            text: 输入文本
            **kwargs: 其他参数
            
        Returns:
            List[float]: 嵌入向量
        """
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("embedding_model", self._embedding_model)
            
            response = self._client.embeddings.create(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI获取嵌入向量失败: {e}")
            raise
    
    def get_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """
        批量获取文本的嵌入向量
        
        Args:
            texts: 输入文本列表
            **kwargs: 其他参数
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("embedding_model", self._embedding_model)
            
            response = self._client.embeddings.create(
                model=model,
                input=texts
            )
            
            # 按照输入顺序排列结果
            sorted_embeddings = sorted(response.data, key=lambda x: x.index)
            
            return [item.embedding for item in sorted_embeddings]
            
        except Exception as e:
            logger.error(f"OpenAI批量获取嵌入向量失败: {e}")
            raise
    
    def _format_contexts(self, contexts: List[Dict[str, Any]]) -> str:
        """
        格式化上下文信息
        
        Args:
            contexts: 上下文信息列表
            
        Returns:
            str: 格式化后的上下文信息
        """
        formatted_contexts = []
        
        for i, context in enumerate(contexts):
            text = context.get("text", "")
            source = context.get("metadata", {}).get("source", "未知来源")
            formatted_contexts.append(f"[{i+1}] {text}\n来源: {source}")
            
        return "\n\n".join(formatted_contexts)
    
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
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("model", self._model_name)
            max_tokens = kwargs.get("max_tokens", self._max_tokens)
            temperature = kwargs.get("temperature", self._temperature)
            system_prompt = kwargs.get("system_prompt", "你是索克生活APP的AI助手，请基于提供的上下文信息回答用户的问题。如果无法从上下文中找到答案，请明确指出。")
            
            # 格式化上下文
            formatted_contexts = self._format_contexts(contexts)
            
            # 构建提示
            prompt = f"""请基于以下上下文信息回答问题。如果无法从上下文中找到答案，请直接说"根据提供的信息，我无法回答这个问题"。

上下文信息:
{formatted_contexts}

问题: {query}

回答:"""
            
            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI RAG完成失败: {e}")
            raise
    
    def rag_complete_stream(self, query: str, contexts: List[Dict[str, Any]], **kwargs) -> Generator[str, None, None]:
        """
        基于检索上下文流式生成回答
        
        Args:
            query: 查询文本
            contexts: 上下文信息列表
            **kwargs: 其他参数
            
        Returns:
            Generator[str, None, None]: 生成的文本片段
        """
        if not self._client:
            self._init_client()
            if not self._client:
                raise RuntimeError("OpenAI客户端未初始化")
                
        try:
            # 提取参数，优先使用kwargs中的值
            model = kwargs.get("model", self._model_name)
            max_tokens = kwargs.get("max_tokens", self._max_tokens)
            temperature = kwargs.get("temperature", self._temperature)
            system_prompt = kwargs.get("system_prompt", "你是索克生活APP的AI助手，请基于提供的上下文信息回答用户的问题。如果无法从上下文中找到答案，请明确指出。")
            
            # 格式化上下文
            formatted_contexts = self._format_contexts(contexts)
            
            # 构建提示
            prompt = f"""请基于以下上下文信息回答问题。如果无法从上下文中找到答案，请直接说"根据提供的信息，我无法回答这个问题"。

上下文信息:
{formatted_contexts}

问题: {query}

回答:"""
            
            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI流式RAG完成失败: {e}")
            raise 