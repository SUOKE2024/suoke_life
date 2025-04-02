#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
嵌入生成模块
=========
负责生成文本的向量嵌入表示
"""

import logging
import numpy as np
from typing import List, Dict, Any, Union, Optional

from config.rag_config import EmbeddingConfig
from embeddings.model_loader import ModelLoader

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """文本嵌入生成器类"""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        初始化嵌入生成器
        
        Args:
            config: 嵌入配置
        """
        self.config = config or EmbeddingConfig()
        self.model_loader = ModelLoader(
            model_name=self.config.model_name,
            model_path=self.config.model_path,
            device=self.config.device,
            use_local=self.config.use_local
        )
        
        # 初始化模型
        self._init_model()
        
    def _init_model(self):
        """初始化模型"""
        try:
            self.model_loader.load_model()
            logger.info(
                f"已加载嵌入模型: {self.model_loader.model_name}"
            )
        except Exception as e:
            logger.error(f"加载嵌入模型失败: {e}")
            raise
            
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32
    ) -> Union[List[float], List[List[float]]]:
        """
        获取文本嵌入向量
        
        Args:
            texts: 单个文本字符串或文本列表
            batch_size: 批处理大小
            
        Returns:
            嵌入向量或嵌入向量列表
        """
        # 处理单个文本输入
        single_text = isinstance(texts, str)
        if single_text:
            texts = [texts]
            
        embeddings = []
        
        try:
            # 分批处理
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                
                # 获取嵌入
                batch_embeddings = self.model_loader.get_embeddings(batch)
                embeddings.extend(batch_embeddings)
                
            # 如果输入是单个文本，返回单个嵌入
            if single_text:
                return embeddings[0]
                
            return embeddings
            
        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            # 返回零向量作为后备
            if single_text:
                return [0.0] * self.model_loader.embedding_dim
            else:
                return [[0.0] * self.model_loader.embedding_dim for _ in texts]
                
    def compute_similarity(
        self,
        query_text: str,
        documents: List[str]
    ) -> List[float]:
        """
        计算查询与文档的相似度
        
        Args:
            query_text: 查询文本
            documents: 文档列表
            
        Returns:
            相似度分数列表
        """
        try:
            # 获取查询嵌入
            query_embedding = self.get_embeddings(query_text)
            
            # 获取文档嵌入
            doc_embeddings = self.get_embeddings(documents)
            
            # 计算余弦相似度
            similarities = []
            for doc_embedding in doc_embeddings:
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append(similarity)
                
            return similarities
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return [0.0] * len(documents)
            
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度
        """
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
        
    def batch_compute_similarity(
        self,
        queries: List[str],
        documents: List[str]
    ) -> List[List[float]]:
        """
        批量计算多个查询与多个文档的相似度
        
        Args:
            queries: 查询文本列表
            documents: 文档列表
            
        Returns:
            相似度矩阵，形状为 [查询数, 文档数]
        """
        try:
            # 获取查询嵌入
            query_embeddings = self.get_embeddings(queries)
            
            # 获取文档嵌入
            doc_embeddings = self.get_embeddings(documents)
            
            # 计算相似度矩阵
            similarity_matrix = []
            for q_emb in query_embeddings:
                similarities = []
                for d_emb in doc_embeddings:
                    similarity = self._cosine_similarity(q_emb, d_emb)
                    similarities.append(similarity)
                similarity_matrix.append(similarities)
                
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"批量计算相似度失败: {e}")
            return [[0.0] * len(documents) for _ in queries] 