#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Milvus向量存储
==========
提供与Milvus向量数据库的集成
"""

import time
import json
import uuid
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    MilvusException
)

from ..config import (
    VECTOR_DIMENSION,
    MILVUS_URI,
    MILVUS_COLLECTION_NAME
)
from .base_vector_store import BaseVectorStore


class MilvusVectorStore(BaseVectorStore):
    """Milvus向量存储，提供与Milvus数据库的集成"""
    
    def __init__(
        self,
        embedding_manager,
        uri: str = MILVUS_URI,
        collection_name: str = MILVUS_COLLECTION_NAME,
        dim: int = VECTOR_DIMENSION,
        alias: str = "default",
        metadata_schema: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        初始化Milvus向量存储
        
        Args:
            embedding_manager: 嵌入管理器实例
            uri: Milvus服务URI
            collection_name: 集合名称
            dim: 向量维度
            alias: 连接别名
            metadata_schema: 元数据字段定义，格式为{字段名: 字段类型}
            max_retries: 操作重试次数
            **kwargs: 其他参数
        """
        self.embedding_manager = embedding_manager
        self.uri = uri
        self.collection_name = collection_name
        self.dim = dim
        self.alias = alias
        self.metadata_schema = metadata_schema or {
            "source": "VARCHAR",
            "doc_id": "VARCHAR",
            "chunk_id": "VARCHAR"
        }
        self.max_retries = max_retries
        self.connection_args = kwargs.get("connection_args", {})
        self.collection = None
        
        # 连接到Milvus
        self._connect()
        
        # 确保集合存在
        self._ensure_collection()
    
    def _connect(self) -> None:
        """连接到Milvus服务"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                logger.info(f"正在连接Milvus服务: {self.uri}")
                connections.connect(
                    alias=self.alias,
                    uri=self.uri,
                    **self.connection_args
                )
                logger.info(f"Milvus连接成功")
                break
            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                logger.error(f"Milvus连接失败 (重试 {retry_count}/{self.max_retries}): {str(e)}")
                if retry_count < self.max_retries:
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.critical(f"Milvus连接失败，已达最大重试次数")
                    raise
    
    def _create_collection(self) -> None:
        """创建Milvus集合"""
        try:
            # 定义集合字段
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=36),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            
            # 添加元数据字段
            for field_name, field_type in self.metadata_schema.items():
                dtype = getattr(DataType, field_type)
                max_length = 65535 if field_type == "VARCHAR" else None
                
                field_kwargs = {"name": field_name, "dtype": dtype}
                if max_length:
                    field_kwargs["max_length"] = max_length
                    
                fields.append(FieldSchema(**field_kwargs))
                
            # 创建集合
            schema = CollectionSchema(
                fields=fields,
                description=f"索克生活RAG服务向量存储集合: {self.collection_name}"
            )
            
            # 创建集合
            self.collection = Collection(
                name=self.collection_name,
                schema=schema,
                using=self.alias
            )
            
            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "HNSW",
                "params": {"M": 8, "efConstruction": 64}
            }
            
            self.collection.create_index(
                field_name="embedding",
                index_params=index_params
            )
            
            # 加载集合
            self.collection.load()
            
            logger.info(f"创建Milvus集合成功: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"创建Milvus集合失败: {e}")
            raise
    
    def _ensure_collection(self) -> None:
        """确保集合存在，不存在则创建"""
        try:
            if utility.has_collection(self.collection_name, using=self.alias):
                logger.info(f"Milvus集合已存在: {self.collection_name}")
                self.collection = Collection(self.collection_name, using=self.alias)
                self.collection.load()
            else:
                logger.info(f"Milvus集合不存在，正在创建: {self.collection_name}")
                self._create_collection()
        except Exception as e:
            logger.error(f"检查或创建Milvus集合失败: {e}")
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
            insert_data = {
                "id": ids,
                "text": texts,
                "embedding": embeddings
            }
            
            # 添加元数据字段
            for field_name in self.metadata_schema.keys():
                insert_data[field_name] = []
                for meta in metadatas:
                    # 将缺失的字段设为空字符串
                    insert_data[field_name].append(
                        str(meta.get(field_name, "")) 
                        if self.metadata_schema[field_name] == "VARCHAR" 
                        else meta.get(field_name, 0)
                    )
            
            # 插入数据
            mr = self.collection.insert(insert_data)
            self.collection.flush()
            
            logger.info(f"向Milvus添加了 {n_vectors} 个向量")
            return ids
            
        except Exception as e:
            logger.error(f"向Milvus添加向量失败: {e}")
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
            # 准备搜索参数
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64}
            }
            
            # 构建过滤表达式
            expr = None
            if filter:
                conditions = []
                for field, value in filter.items():
                    if field in self.metadata_schema:
                        if isinstance(value, str):
                            conditions.append(f'{field} == "{value}"')
                        else:
                            conditions.append(f'{field} == {value}')
                
                if conditions:
                    expr = " && ".join(conditions)
            
            # 执行搜索
            output_fields = ["id", "text"] + list(self.metadata_schema.keys())
            search_result = self.collection.search(
                data=[embedding],
                anns_field="embedding",
                param=search_params,
                limit=k,
                expr=expr,
                output_fields=output_fields
            )
            
            # 解析结果
            results = []
            for hits in search_result:
                for hit in hits:
                    metadata = {}
                    for field in self.metadata_schema.keys():
                        if hasattr(hit, field):
                            metadata[field] = getattr(hit, field)
                    
                    results.append({
                        "id": hit.id,
                        "text": hit.text,
                        "metadata": metadata,
                        "score": hit.score
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Milvus向量搜索失败: {e}")
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
                
            # 构建过滤表达式
            expr = " || ".join([f'id == "{id}"' for id in ids])
            
            # 执行删除
            self.collection.delete(expr)
            
            logger.info(f"从Milvus删除了 {len(ids)} 个向量")
            return True
            
        except Exception as e:
            logger.error(f"从Milvus删除向量失败: {e}")
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
                
            # 构建过滤表达式
            expr = " || ".join([f'id == "{id}"' for id in ids])
            
            # 执行查询
            output_fields = ["id", "text"] + list(self.metadata_schema.keys())
            result = self.collection.query(
                expr=expr,
                output_fields=output_fields
            )
            
            # 解析结果
            documents = []
            for item in result:
                metadata = {}
                for field in self.metadata_schema.keys():
                    if hasattr(item, field):
                        metadata[field] = getattr(item, field)
                
                documents.append({
                    "id": item.id,
                    "text": item.text,
                    "metadata": metadata
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"获取Milvus文档失败: {e}")
            raise
    
    def count(self) -> int:
        """
        获取存储中的文档数量
        
        Returns:
            int: 文档数量
        """
        try:
            return self.collection.num_entities
        except Exception as e:
            logger.error(f"获取Milvus文档数量失败: {e}")
            return 0
    
    def clear(self) -> bool:
        """
        清空向量存储
        
        Returns:
            bool: 操作是否成功
        """
        try:
            self.collection.drop()
            logger.info(f"已清空Milvus集合: {self.collection_name}")
            
            # 重新创建集合
            self._create_collection()
            
            return True
        except Exception as e:
            logger.error(f"清空Milvus集合失败: {e}")
            return False