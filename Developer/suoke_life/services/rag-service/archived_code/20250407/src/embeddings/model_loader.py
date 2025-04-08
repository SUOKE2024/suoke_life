#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
嵌入模型加载器
===========
负责加载和管理文本嵌入模型
"""

import os
import time
import torch
from typing import Dict, Any, Optional
from loguru import logger
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer

from ..config import (
    EMBEDDING_MODEL, 
    MODEL_CACHE_DIR, 
    EMBEDDING_MODEL_KWARGS
)


class EmbeddingModelLoader:
    """
    嵌入模型加载器类
    负责加载和管理文本嵌入模型
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(EmbeddingModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_name: str = EMBEDDING_MODEL, cache_dir: str = MODEL_CACHE_DIR, 
                 model_kwargs: Optional[Dict[str, Any]] = None):
        """
        初始化嵌入模型加载器
        
        Args:
            model_name: 模型名称或路径
            cache_dir: 模型缓存目录
            model_kwargs: 模型加载参数
        """
        # 单例模式下避免重复初始化
        if self._initialized:
            return
            
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.model_kwargs = model_kwargs or EMBEDDING_MODEL_KWARGS
        self.model = None
        self.tokenizer = None
        self.device = self._get_device()
        self._initialized = True
        
        # 立即加载模型
        self._load_model()
        
    def _get_device(self) -> torch.device:
        """
        获取可用的设备（GPU或CPU）
        
        Returns:
            torch.device: 可用的设备
        """
        if torch.cuda.is_available():
            device_id = 0
            device = f"cuda:{device_id}"
            logger.info(f"使用GPU设备: {torch.cuda.get_device_name(device_id)}")
            return torch.device(device)
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("使用MPS设备 (Apple Silicon)")
            return torch.device("mps")
            
        logger.info("使用CPU设备")
        return torch.device("cpu")
        
    def _load_model(self) -> None:
        """加载嵌入模型和分词器"""
        try:
            start_time = time.time()
            logger.info(f"正在加载嵌入模型: {self.model_name}")
            
            # 确保缓存目录存在
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # 加载分词器
            tokenizer_path = os.path.join(self.cache_dir, "tokenizer")
            os.makedirs(tokenizer_path, exist_ok=True)
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                cache_dir=tokenizer_path
            )
            
            # 加载模型
            model_path = os.path.join(self.cache_dir, "embedding_model")
            os.makedirs(model_path, exist_ok=True)
            
            # 使用 SentenceTransformer 加载模型
            self.model = SentenceTransformer(
                self.model_name, 
                cache_folder=model_path,
                device=self.model_kwargs.get("device", self.device)
            )
            
            # 设置最大长度
            if "max_length" in self.model_kwargs:
                self.model.max_seq_length = self.model_kwargs["max_length"]
                
            elapsed_time = time.time() - start_time
            logger.info(f"嵌入模型加载完成, 耗时: {elapsed_time:.2f} 秒")
            
        except Exception as e:
            logger.error(f"加载嵌入模型失败: {str(e)}")
            raise RuntimeError(f"加载嵌入模型失败: {str(e)}")
            
    def get_model(self) -> SentenceTransformer:
        """
        获取嵌入模型实例
        
        Returns:
            SentenceTransformer: 加载的嵌入模型
        """
        if self.model is None:
            self._load_model()
        return self.model
        
    def get_tokenizer(self) -> AutoTokenizer:
        """
        获取分词器实例
        
        Returns:
            AutoTokenizer: 加载的分词器
        """
        if self.tokenizer is None:
            self._load_model()
        return self.tokenizer
        
    def encode(self, texts, **kwargs):
        """
        编码文本为嵌入向量
        
        Args:
            texts: 文本或文本列表
            **kwargs: 传递给模型的额外参数
            
        Returns:
            numpy.ndarray: 嵌入向量
        """
        if self.model is None:
            self._load_model()
            
        # 使用模型编码文本
        return self.model.encode(texts, **kwargs)
        
    def is_model_loaded(self) -> bool:
        """
        检查模型是否已加载
        
        Returns:
            bool: 模型是否已加载
        """
        return self.model is not None 