#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM工厂类
=======
用于创建不同类型的LLM客户端
"""

import os
from typing import Dict, Any, Optional
from loguru import logger

from ..config import (
    LLM_PROVIDER,
    LLM_API_KEY,
    LLM_API_BASE,
    LLM_MODEL_NAME
)


class LLMFactory:
    """LLM工厂类，用于创建不同类型的LLM客户端"""
    
    @staticmethod
    def create_llm_client(
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ):
        """
        创建LLM客户端实例
        
        Args:
            provider: LLM提供商，支持openai, zhipu, baidu, alibaba, local
            api_key: API密钥
            api_base: API基础URL
            model_name: 模型名称
            **kwargs: 其他参数
            
        Returns:
            BaseLLMClient实例
        """
        llm_provider = provider or LLM_PROVIDER
        
        logger.info(f"正在创建{llm_provider} LLM客户端...")
        
        if llm_provider == "openai":
            return LLMFactory._create_openai_client(api_key, api_base, model_name, **kwargs)
        elif llm_provider == "zhipu":
            return LLMFactory._create_zhipu_client(api_key, api_base, model_name, **kwargs)
        elif llm_provider == "baidu":
            return LLMFactory._create_baidu_client(api_key, api_base, model_name, **kwargs)
        elif llm_provider == "alibaba":
            return LLMFactory._create_alibaba_client(api_key, api_base, model_name, **kwargs)
        elif llm_provider == "local":
            return LLMFactory._create_local_client(model_name, **kwargs)
        else:
            raise ValueError(f"不支持的LLM提供商: {llm_provider}")
    
    @staticmethod
    def _create_openai_client(api_key, api_base, model_name, **kwargs):
        """创建OpenAI客户端"""
        from .openai_client import OpenAIClient
        
        return OpenAIClient(
            api_key=api_key or LLM_API_KEY,
            api_base=api_base or LLM_API_BASE,
            model_name=model_name or LLM_MODEL_NAME,
            **kwargs
        )
    
    @staticmethod
    def _create_zhipu_client(api_key, api_base, model_name, **kwargs):
        """创建智谱AI客户端"""
        from .zhipu_client import ZhipuClient
        
        return ZhipuClient(
            api_key=api_key or LLM_API_KEY,
            api_base=api_base or LLM_API_BASE,
            model_name=model_name or LLM_MODEL_NAME,
            **kwargs
        )
    
    @staticmethod
    def _create_baidu_client(api_key, api_base, model_name, **kwargs):
        """创建百度文心客户端"""
        from .baidu_client import BaiduClient
        
        return BaiduClient(
            api_key=api_key or LLM_API_KEY,
            api_base=api_base or LLM_API_BASE,
            model_name=model_name or LLM_MODEL_NAME,
            **kwargs
        )
    
    @staticmethod
    def _create_alibaba_client(api_key, api_base, model_name, **kwargs):
        """创建阿里通义千问客户端"""
        from .alibaba_client import AlibabaClient
        
        return AlibabaClient(
            api_key=api_key or LLM_API_KEY,
            api_base=api_base or LLM_API_BASE,
            model_name=model_name or LLM_MODEL_NAME,
            **kwargs
        )
    
    @staticmethod
    def _create_local_client(model_name, **kwargs):
        """创建本地LLM客户端"""
        from .local_client import LocalLLMClient
        
        return LocalLLMClient(
            model_name=model_name or LLM_MODEL_NAME,
            **kwargs
        )