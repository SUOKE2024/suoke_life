#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Qdrant向量存储
==========
提供与Qdrant向量数据库的集成
"""

import time
import json
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

import qdrant_client
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from ..config import (
    VECTOR_DIMENSION,
    QDRANT_URL,
    QDRANT_PORT,
    QDRANT_COLLECTION_NAME
)
from .base_vector_store import BaseVectorStore


class QdrantVectorStore(BaseVectorStore):
    """Qdrant向量存储，提供与Qdrant数据库的集成"""
    
    def __init__(
        self,
        embedding_manager,
        url: str = QDRANT_URL,
        port: int = QDRANT_PORT,
        collection_name: str = QDRANT_COLLECTION_NAME,
        dim: int = VECTOR_DIMENSION,
        distance_func: str = "Cosine",
        max_retries: int = 3,
        **kwargs
    ):
        """
        初始化Qdrant向量存储
        
        Args:
            embedding_manager: 嵌入管理器实例
            url: Qdrant服务URL
            port: Qdrant服务端口
            collection_name: 集合名称
            dim: 向量维度
            distance_func: 距离函数，支持Cosine, Euclid, Dot
            max_retries: 操作重试次数
            **kwargs: 其他参数
        """
        self.embedding_manager = embedding_manager
        self.url = url
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self.distance_func = getattr(models.Distance, distance_func)
        self.max_retries = max_retries
        self.client_params = kwargs.get("client_params", {})
        self.client = None
        
        # 连接到Qdrant
        self._connect()
        
        # 确保集合存在
        self._ensure_collection()
    
    def _connect(self) -> None:
        """连接到Qdrant服务"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"正在连接Qdrant服务: {self.url}:{self.port}")
                if self.port:
                    self.client = QdrantClient(url=self.url, port=self.port, **self.client_params)
                else:
                    self.client = QdrantClient(url=self.url, **self.client_params)
                    
                # 尝试获取集合列表，验证连接
                self.client.get_collections()
                
                logger.info(f"Qdrant连接成功")
                break
            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                logger.error(f"Qdrant连接失败 (重试 {retry_count}/{self.max_retries}): {str(e)}")
                if retry_count < self.max_retries:
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.critical(f"Qdrant连接失败，已达最大重试次数")
                    raise
    
    def _ensure_collection(self) -> None:
        """确保集合存在，不存在则创建"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                logger.info(f"Qdrant集合已存在: {self.collection_name}")
                
                # 获取集合信息，确认向量维度
                collection_info = self.client.get_collection(self.collection_name)
                existing_dim = collection_info.config.params.vectors.size
                
                if existing_dim != self.dim:
                    logger.warning(f"集合维度不匹配: 期望 {self.dim}，实际 {existing_dim}")
            else:
                logger.info(f"Qdrant集合不存在，正在创建: {self.collection_name}")
                self._create_collection()
        except Exception as e:
            logger.error(f"检查或创建Qdrant集合失败: {e}")
            raise
    
    def _create_collection(self) -> None:
        """创建Qdrant集合"""
        try:
            # 创建集合
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dim,
                    distance=self.distance_func
                )
            )
            
            # 创建索引
            logger.info(f"创建Qdrant集合成功: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"创建Qdrant集合失败: {e}")
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
            
        # 确保数据一致性
        n_texts = len(texts)
        metadatas = metadatas or [{}] * n_texts
        ids = ids or [str(uuid.uuid4()) for _ in range(n_texts)]
        
        # 确保metadatas和ids的长度与texts相同
        if len(metadatas) != n_texts:
            metadatas = metadatas + [{}] * (n_texts - len(metadatas))
        if len(ids) != n_texts:
            ids = ids + [str(uuid.uuid4()) for _ in range(n_texts - len(ids))]
            
        # 获取嵌入向量
        embeddings = self.embedding_manager.get_embeddings(texts)
        
        # 添加嵌入向量
        return self.add_embeddings(embeddings, texts, metadatas, ids)
    
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
            
        # 确保数据一致性
        n_vectors = len(embeddings)
        if len(texts) != n_vectors:
            raise ValueError(f"文本数量 ({len(texts)}) 必须与嵌入向量数量 ({n_vectors}) 相同")
            
        metadatas = metadatas or [{}] * n_vectors
        ids = ids or [str(uuid.uuid4()) for _ in range(n_vectors)]
        
        # 确保metadatas和ids的长度与embeddings相同
        if len(metadatas) != n_vectors:
            metadatas = metadatas + [{}] * (n_vectors - len(metadatas))
        if len(ids) != n_vectors:
            ids = ids + [str(uuid.uuid4()) for _ in range(n_vectors - len(ids))]
            
        try:
            # 准备数据
            points = []
            for i in range(n_vectors):
                # 准备点位数据
                point = models.PointStruct(
                    id=ids[i],
                    vector=embeddings[i],
                    payload={
                        "text": texts[i],
                        **metadatas[i]
                    }
                )
                points.append(point)
            
            # 批量插入数据
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"向Qdrant添加了 {n_vectors} 个向量")
            return ids
            
        except Exception as e:
            logger.error(f"向Qdrant添加向量失败: {e}")
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
        # 获取查询的嵌入向量
        embedding = self.embedding_manager.get_embedding(query)
        
        # 使用嵌入向量搜索
        return self.similarity_search_by_vector(embedding, k, filter)
    
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
            # 转换过滤条件
            search_filter = None
            if filter:
                conditions = []
                for field, value in filter.items():
                    if isinstance(value, str):
                        conditions.append(models.FieldCondition(
                            key=field,
                            match=models.MatchValue(value=value)
                        ))
                    elif isinstance(value, (int, float)):
                        conditions.append(models.FieldCondition(
                            key=field,
                            range=models.Range(
                                gte=value,
                                lte=value
                            )
                        ))
                    elif isinstance(value, list) and len(value) == 2:
                        conditions.append(models.FieldCondition(
                            key=field,
                            range=models.Range(
                                gte=value[0],
                                lte=value[1]
                            )
                        ))
                
                if conditions:
                    search_filter = models.Filter(
                        must=conditions
                    )
            
            # 执行搜索
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=k,
                query_filter=search_filter
            )
            
            # 解析结果
            results = []
            for scored_point in search_result:
                results.append({
                    "id": scored_point.id,
                    "text": scored_point.payload.get("text", ""),
                    "metadata": {k: v for k, v in scored_point.payload.items() if k != "text"},
                    "score": scored_point.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Qdrant向量搜索失败: {e}")
            raise
    
    def delete(self, ids: Union[str, List[str]]) -> bool:
        """
        从存储中删除文档
        
        Args:
            ids: 要删除的文档ID或ID列表
            
        Returns:
            bool: 操作是否成功
        """
        try:
            if isinstance(ids, str):
                ids = [ids]
                
            if not ids:
                return True
                
            # 执行删除
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=ids
                )
            )
            
            logger.info(f"从Qdrant删除了 {len(ids)} 个向量")
            return True
            
        except Exception as e:
            logger.error(f"从Qdrant删除向量失败: {e}")
            return False
    
    def get(self, ids: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        获取指定ID的文档
        
        Args:
            ids: 要获取的文档ID或ID列表
            
        Returns:
            List[Dict[str, Any]]: 文档列表
        """
        try:
            if isinstance(ids, str):
                ids = [ids]
                
            if not ids:
                return []
                
            # 执行查询
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=ids
            )
            
            # 解析结果
            documents = []
            for point in points:
                documents.append({
                    "id": point.id,
                    "text": point.payload.get("text", ""),
                    "metadata": {k: v for k, v in point.payload.items() if k != "text"}
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"获取Qdrant文档失败: {e}")
            raise
    
    def count(self) -> int:
        """
        获取存储中的文档数量
        
        Returns:
            int: 文档数量
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.vectors_count
        except Exception as e:
            logger.error(f"获取Qdrant文档数量失败: {e}")
            return 0
    
    def clear(self) -> bool:
        """
        清空向量存储
        
        Returns:
            bool: 操作是否成功
        """
        try:
            # 删除集合
            self.client.delete_collection(self.collection_name)
            logger.info(f"已删除Qdrant集合: {self.collection_name}")
            
            # 重新创建集合
            self._create_collection()
            
            return True
        except Exception as e:
            logger.error(f"清空Qdrant集合失败: {e}")
            return False 