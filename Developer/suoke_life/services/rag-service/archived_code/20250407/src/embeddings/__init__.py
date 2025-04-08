#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索克生活APP - RAG服务嵌入向量模块
=============================
提供文本嵌入向量模型和操作
"""

from .model_loader import EmbeddingModelLoader
from .embedding_manager import EmbeddingManager

__all__ = ["EmbeddingModelLoader", "EmbeddingManager"] 