#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重排序器工厂类
==========
用于创建不同类型的重排序器实例
"""

import os
from typing import Dict, Any, Optional
from loguru import logger

from ..config import (
    RERANK_ENABLED,
    RERANK_MODEL,
    RERANK_TYPE,
    MODEL_CACHE_DIR
)


class RerankerFactory:
    """重排序器工厂类，用于创建不同类型的重排序器实例"""
    
    @staticmethod
    def create_reranker(
        rerank_type: Optional[str] = None,
        model_name: Optional[str] = None,
        cache_dir: Optional[str] = None,
        **kwargs
    ):
        """
        创建重排序器实例
        
        Args:
            rerank_type: 重排序类型，支持bge, cross_encoder, ensemble
            model_name: 模型名称
            cache_dir: 模型缓存目录
            **kwargs: 其他参数
            
        Returns:
            BaseReranker实例
        """
        if not RERANK_ENABLED:
            logger.info("重排序功能已禁用")
            return None
            
        rerank_type = rerank_type or RERANK_TYPE
        model_name = model_name or RERANK_MODEL
        cache_dir = cache_dir or MODEL_CACHE_DIR
        
        logger.info(f"正在创建{rerank_type}重排序器...")
        
        if rerank_type == "bge":
            return RerankerFactory._create_bge_reranker(model_name, cache_dir, **kwargs)
        elif rerank_type == "cross_encoder":
            return RerankerFactory._create_cross_encoder_reranker(model_name, cache_dir, **kwargs)
        elif rerank_type == "ensemble":
            return RerankerFactory._create_ensemble_reranker(model_name, cache_dir, **kwargs)
        else:
            raise ValueError(f"不支持的重排序类型: {rerank_type}")
    
    @staticmethod
    def _create_bge_reranker(model_name, cache_dir, **kwargs):
        """创建BGE重排序器"""
        from .bge_reranker import BGEReranker
        
        return BGEReranker(
            model_name=model_name,
            cache_dir=cache_dir,
            **kwargs
        )
    
    @staticmethod
    def _create_cross_encoder_reranker(model_name, cache_dir, **kwargs):
        """创建Cross Encoder重排序器"""
        from .cross_encoder_reranker import CrossEncoderReranker
        
        return CrossEncoderReranker(
            model_name=model_name,
            cache_dir=cache_dir,
            **kwargs
        )
    
    @staticmethod
    def _create_ensemble_reranker(model_name, cache_dir, **kwargs):
        """创建集成重排序器"""
        from .ensemble_reranker import EnsembleReranker
        
        # 创建集成使用的重排序器
        rerankers = []
        
        # 添加BGE重排序器
        bge_model = kwargs.get("bge_model", "BAAI/bge-reranker-base")
        bge_weight = kwargs.get("bge_weight", 0.5)
        bge_reranker = RerankerFactory._create_bge_reranker(
            model_name=bge_model,
            cache_dir=cache_dir
        )
        rerankers.append((bge_reranker, bge_weight))
        
        # 添加Cross Encoder重排序器
        ce_model = kwargs.get("ce_model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        ce_weight = kwargs.get("ce_weight", 0.5)
        ce_reranker = RerankerFactory._create_cross_encoder_reranker(
            model_name=ce_model,
            cache_dir=cache_dir
        )
        rerankers.append((ce_reranker, ce_weight))
        
        return EnsembleReranker(
            rerankers=rerankers,
            **kwargs
        ) 