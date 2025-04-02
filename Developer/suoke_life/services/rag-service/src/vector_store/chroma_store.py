#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chroma向量存储实现
===============
使用ChromaDB实现向量存储
"""

import os
import uuid
import time
from typing import List, Dict, Any, Optional, Union
from loguru import logger

try:
    import chromadb
    from chromadb.utils import embedding_functions
    from chromadb.config import Settings
except ImportError:
    logger.error("请安装 chromadb 包: pip install chromadb")
    raise

from .base_vector_store import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    """使用ChromaDB实现的向量存储"""
    
    def __init__(
        self,
        embedding_manager,
        collection_name: str = "suoke_documents",
        persist_dir: Optional[str] = None,
        **kwargs
    ):
        """
        初始化ChromaDB向量存储
        
        Args:
            embedding_manager: 嵌入管理器实例
            collection_name: 集合名称
            persist_dir: 持久化目录，如未提供则使用内存存储
            **kwargs: 其他参数
        """
        self.embedding_manager = embedding_manager
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        
        if persist_dir:
            # 确保目录存在
            os.makedirs(persist_dir, exist_ok=True)
            
            settings = Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            )
            self.client = chromadb.PersistentClient(settings=settings)
            logger.info(f"初始化ChromaDB持久化客户端，存储目录: {persist_dir}")
        else:
            self.client = chromadb.EphemeralClient()
            logger.info("初始化ChromaDB内存客户端")
            
        # 创建自定义嵌入函数
        self.embedding_function = embedding_functions.UserDefinedEmbeddingFunction(
            lambda texts: self.embedding_manager.get_embeddings(texts)
        )
        
        # 获取或创建集合
        try:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "索克生活知识库"}
            )
            logger.info(f"获取或创建ChromaDB集合: {collection_name}")
        except Exception as e:
            logger.error(f"创建ChromaDB集合失败: {e}")
            raise
            
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加文本到向量存储
        
        Args:
            texts: 文本列表
            metadatas: 文本元数据列表
            ids: 文本ID列表
            
        Returns:
            List[str]: 添加的文本ID列表
        """
        if not texts:
            return []
            
        # 准备ID
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        elif len(ids) != len(texts):
            raise ValueError(f"ids长度({len(ids)})与texts长度({len(texts)})不匹配")
            
        # 准备元数据
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]
        elif len(metadatas) != len(texts):
            raise ValueError(f"metadatas长度({len(metadatas)})与texts长度({len(texts)})不匹配")
            
        # 为每个元数据添加时间戳
        timestamp = int(time.time())
        for metadata in metadatas:
            if "timestamp" not in metadata:
                metadata["timestamp"] = timestamp
        
        # 添加到集合
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"向ChromaDB集合添加了{len(texts)}条文档")
            return ids
        except Exception as e:
            logger.error(f"向ChromaDB添加文档失败: {e}")
            raise
            
    def add_embeddings(
        self, 
        embeddings: List[List[float]], 
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        添加预计算的嵌入向量到存储
        
        Args:
            embeddings: 嵌入向量列表
            texts: 文本列表
            metadatas: 文本元数据列表
            ids: 文本ID列表
            
        Returns:
            List[str]: 添加的文本ID列表
        """
        if not embeddings or not texts:
            return []
            
        if len(embeddings) != len(texts):
            raise ValueError(f"embeddings长度({len(embeddings)})与texts长度({len(texts)})不匹配")
            
        # 准备ID
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        elif len(ids) != len(texts):
            raise ValueError(f"ids长度({len(ids)})与texts长度({len(texts)})不匹配")
            
        # 准备元数据
        if metadatas is None:
            metadatas = [{} for _ in range(len(texts))]
        elif len(metadatas) != len(texts):
            raise ValueError(f"metadatas长度({len(metadatas)})与texts长度({len(texts)})不匹配")
            
        # 为每个元数据添加时间戳
        timestamp = int(time.time())
        for metadata in metadatas:
            if "timestamp" not in metadata:
                metadata["timestamp"] = timestamp
        
        # 添加到集合
        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"向ChromaDB集合添加了{len(texts)}条预计算嵌入文档")
            return ids
        except Exception as e:
            logger.error(f"向ChromaDB添加预计算嵌入文档失败: {e}")
            raise
            
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        基于查询文本进行相似性搜索
        
        Args:
            query: 查询文本
            k: 返回的结果数量
            filter: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 相似结果列表
        """
        try:
            # 获取嵌入向量
            query_embedding = self.embedding_manager.get_embedding(query)
            return self.similarity_search_by_vector(query_embedding, k, filter)
        except Exception as e:
            logger.error(f"相似性搜索失败: {e}")
            return []
            
    def similarity_search_by_vector(
        self, 
        embedding: List[float], 
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        基于嵌入向量进行相似性搜索
        
        Args:
            embedding: 查询嵌入向量
            k: 返回的结果数量
            filter: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 相似结果列表
        """
        try:
            # 执行查询
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=k,
                where=filter
            )
            
            if not results["documents"]:
                return []
                
            # 组织返回结果
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]
            distances = results["distances"][0]
            
            return [
                {
                    "id": id,
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                    "score": 1.0 - distance  # 将距离转换为相似度分数
                }
                for id, document, metadata, distance in zip(ids, documents, metadatas, distances)
            ]
        except Exception as e:
            logger.error(f"基于向量的相似性搜索失败: {e}")
            return []
            
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        从存储中删除文档
        
        Args:
            ids: 要删除的文档ID或ID列表
            
        Returns:
            bool: 操作是否成功
        """
        if not ids:
            return True
            
        if isinstance(ids, str):
            ids = [ids]
            
        try:
            self.collection.delete(ids=ids)
            logger.info(f"从ChromaDB删除了{len(ids)}条文档")
            return True
        except Exception as e:
            logger.error(f"从ChromaDB删除文档失败: {e}")
            return False
            
    def get(self, ids: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        获取指定ID的文档
        
        Args:
            ids: 要获取的文档ID或ID列表
            
        Returns:
            List[Dict[str, Any]]: 文档列表
        """
        if not ids:
            return []
            
        if isinstance(ids, str):
            ids = [ids]
            
        try:
            results = self.collection.get(ids=ids)
            
            if not results["documents"]:
                return []
                
            # 组织返回结果
            documents = results["documents"]
            metadatas = results["metadatas"]
            ids = results["ids"]
            
            return [
                {
                    "id": id,
                    "text": document,
                    "metadata": metadata
                }
                for id, document, metadata in zip(ids, documents, metadatas)
            ]
        except Exception as e:
            logger.error(f"从ChromaDB获取文档失败: {e}")
            return []
            
    def count(self) -> int:
        """
        获取存储中的文档数量
        
        Returns:
            int: 文档数量
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"获取ChromaDB文档数量失败: {e}")
            return 0
            
    def clear(self) -> bool:
        """
        清空向量存储
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # ChromaDB没有直接清空集合的方法，需要删除集合然后重新创建
            self.client.delete_collection(name=self.collection_name)
            
            # 重新创建集合
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "索克生活知识库"}
            )
            
            logger.info(f"清空了ChromaDB集合: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"清空ChromaDB集合失败: {e}")
            return False 