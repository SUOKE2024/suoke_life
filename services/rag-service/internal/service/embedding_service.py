"""
embedding_service - 索克生活项目模块
"""

from ..model.document import Document
from loguru import logger
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any, Optional
import os
import time
import torch

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
嵌入服务模块，负责生成文本的嵌入向量
"""



class EmbeddingService:
    """
    嵌入服务，提供文本向量化功能
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化嵌入服务
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.model_name = config['embeddings'].get('model_name', 'paraphrase-multilingual-MiniLM-L12-v2')
        self.device = config['embeddings'].get('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        self.batch_size = config['embeddings'].get('batch_size', 32)
        self.cache_dir = config['embeddings'].get('cache_dir', '/app/data/models')
        self.model = None
        self.max_length = 512
        self.is_initialized = False
    
    async def initialize(self) -> None:
        """初始化嵌入模型"""
        if self.is_initialized:
            return
            
        logger.info(f"Initializing embedding service with model: {self.model_name}")
        logger.info(f"Using device: {self.device}")
        
        try:
            # 确保缓存目录存在
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # 加载模型
            self.model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir
            )
            
            logger.info(f"Embedding model loaded successfully")
            self.is_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {str(e)}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """
        为单个文本生成嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not text.strip():
            # 空文本返回零向量
            return [0.0] * self.model.get_sentence_embedding_dimension()
        
        start_time = time.time()
        
        try:
            # 截断过长的文本
            if len(text) > self.max_length * 4:  # 估算字符数
                logger.warning(f"Text too long ({len(text)} chars), truncating to {self.max_length*4} chars")
                text = text[:self.max_length*4]
            
            # 生成嵌入向量
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # 转换为原生列表
            embedding_list = embedding.tolist()
            
            logger.debug(f"Embedded text in {time.time()-start_time:.3f}s")
            return embedding_list
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # 返回零向量作为回退
            return [0.0] * self.model.get_sentence_embedding_dimension()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        为多个文本生成嵌入向量
        
        Args:
            texts: 输入文本列表
            
        Returns:
            嵌入向量列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not texts:
            return []
        
        start_time = time.time()
        
        try:
            # 处理空文本
            texts = [text if text.strip() else " " for text in texts]
            
            # 截断过长的文本
            texts = [
                text[:self.max_length*4] if len(text) > self.max_length*4 else text
                for text in texts
            ]
            
            # 批量生成嵌入向量
            embeddings = self.model.encode(
                texts, 
                batch_size=self.batch_size,
                convert_to_numpy=True
            )
            
            # 转换为原生列表
            embedding_lists = embeddings.tolist()
            
            logger.debug(f"Embedded {len(texts)} texts in {time.time()-start_time:.3f}s")
            return embedding_lists
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # 返回零向量列表作为回退
            dimension = self.model.get_sentence_embedding_dimension()
            return [[0.0] * dimension for _ in range(len(texts))]
    
    async def embed_documents(self, documents: List[Document]) -> List[Document]:
        """
        为文档列表生成嵌入向量
        
        Args:
            documents: 文档列表
            
        Returns:
            添加了嵌入向量的文档列表
        """
        if not self.is_initialized:
            await self.initialize()
        
        if not documents:
            return []
        
        # 提取文档内容
        texts = [doc.content for doc in documents]
        
        # 生成嵌入向量
        embeddings = await self.embed_texts(texts)
        
        # 将嵌入向量添加到文档
        for doc, embedding in zip(documents, embeddings):
            doc.vector = embedding
        
        return documents
    
    async def close(self) -> None:
        """释放资源"""
        self.model = None
        self.is_initialized = False
        
        # 清理GPU内存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Embedding service closed") 