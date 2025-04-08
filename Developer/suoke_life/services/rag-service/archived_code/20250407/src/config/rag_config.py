#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RAG服务配置
=========
定义服务配置和数据模型
"""

import os
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    """文档类型枚举"""
    CLASSIC = "classic"      # 经典文献
    ARTICLE = "article"      # 学术文章
    CASE = "case"            # 病例
    FORMULA = "formula"      # 方剂
    HERB = "herb"            # 药材
    SYMPTOM = "symptom"      # 症状
    THERAPY = "therapy"      # 疗法

class DocumentProcessConfig(BaseModel):
    """文档处理配置"""
    min_chunk_size: int = 100
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    enable_term_extraction: bool = True
    enable_weight_calculation: bool = True
    enable_deduplication: bool = True
    enable_filtering: bool = True
    
class EmbeddingConfig(BaseModel):
    """嵌入配置"""
    model_name: str = "shibing624/text2vec-base-chinese"
    model_path: Optional[str] = None
    device: str = "cpu"
    use_local: bool = False
    batch_size: int = 32
    embedding_dim: int = 768
    normalize_embeddings: bool = True
    max_length: int = 256
    
class RerankerConfig(BaseModel):
    """重排序配置"""
    model_name: str = "BAAI/bge-reranker-base"
    device: str = "cpu"
    use_local: bool = False
    batch_size: int = 16
    max_length: int = 512

class ChunkingConfig(BaseModel):
    """分块配置"""
    chunk_size: int = 500
    chunk_overlap: int = 50
    split_by: str = "sentence"  # 'character' or 'sentence'
    
class AugmentationConfig(BaseModel):
    """增强配置"""
    enable_term_extraction: bool = True
    enable_weight_calculation: bool = True
    
class DocumentProcessorConfig(BaseModel):
    """文档处理器配置"""
    remove_special_chars: bool = True
    chunking: Optional[ChunkingConfig] = None
    augmentation: Optional[AugmentationConfig] = None 