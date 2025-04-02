#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
嵌入向量管理器
===========
提供文本嵌入向量生成和管理功能
"""

import os
import time
import re
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

from ..config import CHINESE_SEGMENTATION, TOP_K
from .model_loader import EmbeddingModelLoader


class EmbeddingManager:
    """嵌入向量管理器类，负责文本向量化和管理"""
    
    def __init__(self, model_loader: Optional[EmbeddingModelLoader] = None):
        """
        初始化嵌入向量管理器
        
        Args:
            model_loader: 嵌入模型加载器实例，如果为None则创建新实例
        """
        self.model_loader = model_loader or EmbeddingModelLoader()
        self.segmentation_type = CHINESE_SEGMENTATION
        self._initialize_segmentation()
        
    def _initialize_segmentation(self):
        """初始化中文分词器"""
        if self.segmentation_type == "jieba":
            try:
                import jieba
                self.segmenter = jieba
                logger.info("已初始化 jieba 分词器")
            except ImportError:
                logger.warning("无法导入 jieba 分词器，将使用空格分词")
                self.segmenter = None
                self.segmentation_type = "space"
        elif self.segmentation_type == "pkuseg":
            try:
                import pkuseg
                self.segmenter = pkuseg.pkuseg()
                logger.info("已初始化 pkuseg 分词器")
            except ImportError:
                logger.warning("无法导入 pkuseg 分词器，将使用空格分词")
                self.segmenter = None
                self.segmentation_type = "space"
        else:
            logger.info("使用空格分词")
            self.segmenter = None
            self.segmentation_type = "space"
            
    def preprocess_text(self, text: str) -> str:
        """
        预处理文本
        
        Args:
            text: 输入文本
            
        Returns:
            str: 预处理后的文本
        """
        if not text:
            return ""
            
        # 删除多余的空白字符
        text = re.sub(r"\s+", " ", text.strip())
        
        # 针对中文文本进行额外处理
        if self._is_chinese_text(text) and self.segmentation_type != "space":
            if self.segmentation_type == "jieba":
                # 使用jieba分词
                segments = self.segmenter.cut(text)
                text = " ".join(segments)
            elif self.segmentation_type == "pkuseg":
                # 使用pkuseg分词
                segments = self.segmenter.cut(text)
                text = " ".join(segments)
                
        return text
        
    def _is_chinese_text(self, text: str) -> bool:
        """
        检测文本是否包含中文字符
        
        Args:
            text: 输入文本
            
        Returns:
            bool: 是否包含中文字符
        """
        # 检测文本中是否包含中文字符
        return bool(re.search(r'[\u4e00-\u9fff]', text))
        
    def get_embedding(self, text: str) -> np.ndarray:
        """
        获取单个文本的嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            np.ndarray: 嵌入向量
        """
        if not text:
            raise ValueError("输入文本不能为空")
            
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 使用模型生成嵌入向量
        embedding = self.model_loader.encode(processed_text, show_progress_bar=False)
        
        return embedding
        
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        批量获取文本的嵌入向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            np.ndarray: 嵌入向量矩阵，每行是一个文本的向量
        """
        if not texts:
            return np.array([])
            
        # 预处理所有文本
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # 使用模型批量生成嵌入向量
        embeddings = self.model_loader.encode(
            processed_texts, 
            show_progress_bar=len(texts) > 10,
            batch_size=32
        )
        
        return embeddings
        
    def compute_similarity(self, query_embedding: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
        """
        计算查询向量与一组向量的相似度
        
        Args:
            query_embedding: 查询向量
            embeddings: 向量矩阵，每行是一个向量
            
        Returns:
            np.ndarray: 相似度分数数组
        """
        # 确保向量被正确归一化
        query_embedding_normalized = query_embedding / np.linalg.norm(query_embedding)
        embeddings_normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # 计算余弦相似度
        similarities = np.dot(embeddings_normalized, query_embedding_normalized)
        
        return similarities
        
    def find_similar(self, query: str, texts: List[str], top_k: int = TOP_K) -> List[Dict[str, Any]]:
        """
        在文本列表中查找与查询最相似的文本
        
        Args:
            query: 查询文本
            texts: 文本列表
            top_k: 返回的最相似结果数量
            
        Returns:
            List[Dict[str, Any]]: 包含文本、相似度和索引的结果列表
        """
        if not texts:
            return []
            
        # 获取查询文本的嵌入向量
        query_embedding = self.get_embedding(query)
        
        # 获取所有文本的嵌入向量
        embeddings = self.get_embeddings(texts)
        
        # 计算相似度
        similarities = self.compute_similarity(query_embedding, embeddings)
        
        # 获取最相似的top_k个结果
        top_k = min(top_k, len(texts))
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        # 构建结果
        results = []
        for idx in top_indices:
            results.append({
                "text": texts[idx],
                "similarity": float(similarities[idx]),
                "index": int(idx)
            })
            
        return results
        
    def compute_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本之间的相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            float: 相似度分数 (0-1)
        """
        # 获取两个文本的嵌入向量
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        # 归一化向量
        embedding1_normalized = embedding1 / np.linalg.norm(embedding1)
        embedding2_normalized = embedding2 / np.linalg.norm(embedding2)
        
        # 计算余弦相似度
        similarity = np.dot(embedding1_normalized, embedding2_normalized)
        
        return float(similarity)
        
    def get_text_hash(self, text: str) -> str:
        """
        计算文本的哈希值
        
        Args:
            text: 输入文本
            
        Returns:
            str: 文本的哈希值
        """
        # 预处理文本
        processed_text = self.preprocess_text(text)
        
        # 计算SHA-256哈希值
        hash_obj = hashlib.sha256(processed_text.encode('utf-8'))
        
        return hash_obj.hexdigest() 