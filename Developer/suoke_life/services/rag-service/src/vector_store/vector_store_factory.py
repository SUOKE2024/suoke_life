#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
向量存储工厂
========
创建不同类型的向量存储实例
"""

import os
from typing import Dict, Any, Optional
from loguru import logger

from ..config import (
    VECTOR_DB_TYPE, 
    VECTOR_DB_PATH,
    VECTOR_DB_COLLECTION,
    VECTOR_DIMENSION,
    CHROMA_PERSIST_DIR,
    QDRANT_URL,
    QDRANT_PORT,
    QDRANT_COLLECTION_NAME,
    MILVUS_URI,
    MILVUS_COLLECTION_NAME
)


class VectorStoreFactory:
    """向量存储工厂类，用于创建不同类型的向量存储实例"""
    
    @staticmethod
    def create_vector_store(
        vector_db_type: Optional[str] = None,
        embedding_manager = None, 
        **kwargs
    ):
        """
        创建向量存储实例
        
        Args:
            vector_db_type: 向量数据库类型，支持chroma, qdrant, milvus
            embedding_manager: 嵌入管理器实例
            **kwargs: 其他参数
            
        Returns:
            BaseVectorStore实例
        """
        db_type = vector_db_type or VECTOR_DB_TYPE
        
        if not embedding_manager:
            from ..embeddings import EmbeddingManager
            embedding_manager = EmbeddingManager()
        
        logger.info(f"正在创建{db_type}向量存储...")
        
        if db_type == "chroma":
            return VectorStoreFactory._create_chroma(embedding_manager, **kwargs)
        elif db_type == "qdrant":
            return VectorStoreFactory._create_qdrant(embedding_manager, **kwargs)
        elif db_type == "milvus":
            return VectorStoreFactory._create_milvus(embedding_manager, **kwargs)
        else:
            raise ValueError(f"不支持的向量数据库类型: {db_type}")
    
    @staticmethod
    def _create_chroma(embedding_manager, **kwargs):
        """创建Chroma向量存储"""
        from .chroma_store import ChromaVectorStore
        
        persist_dir = kwargs.get("persist_dir", CHROMA_PERSIST_DIR)
        collection_name = kwargs.get("collection_name", VECTOR_DB_COLLECTION)
        
        # 确保目录存在
        os.makedirs(persist_dir, exist_ok=True)
        
        return ChromaVectorStore(
            embedding_manager=embedding_manager,
            collection_name=collection_name,
            persist_dir=persist_dir,
            **kwargs
        )
    
    @staticmethod
    def _create_qdrant(embedding_manager, **kwargs):
        """创建Qdrant向量存储"""
        from .qdrant_store import QdrantVectorStore
        
        url = kwargs.get("url", QDRANT_URL)
        port = kwargs.get("port", QDRANT_PORT)
        collection_name = kwargs.get("collection_name", QDRANT_COLLECTION_NAME)
        dim = kwargs.get("dim", VECTOR_DIMENSION)
        
        return QdrantVectorStore(
            embedding_manager=embedding_manager,
            url=url,
            port=port,
            collection_name=collection_name,
            dim=dim,
            **kwargs
        )
    
    @staticmethod
    def _create_milvus(embedding_manager, **kwargs):
        """创建Milvus向量存储"""
        from .milvus_store import MilvusVectorStore
        
        uri = kwargs.get("uri", MILVUS_URI)
        collection_name = kwargs.get("collection_name", MILVUS_COLLECTION_NAME)
        dim = kwargs.get("dim", VECTOR_DIMENSION)
        
        return MilvusVectorStore(
            embedding_manager=embedding_manager,
            uri=uri,
            collection_name=collection_name,
            dim=dim,
            **kwargs
        ) 