#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Milvus向量数据库连接器
===========
提供与Milvus向量数据库交互的API
"""

import os
import time
import json
import uuid
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
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

from config import DEFAULT_EMBEDDING_DIMENSION, VECTOR_SIMILARITY_METRIC


class MilvusConnector:
    """Milvus向量数据库连接器"""
    
    def __init__(
        self,
        host: str = None,
        port: str = None,
        user: str = None,
        password: str = None,
        collection_name: str = "suoke_vectors",
        dimension: int = DEFAULT_EMBEDDING_DIMENSION,
        metric_type: str = VECTOR_SIMILARITY_METRIC,
        index_type: str = "HNSW",
        auto_id: bool = False,
        timeout: int = 60
    ):
        """初始化Milvus连接器
        
        Args:
            host: Milvus服务器地址
            port: Milvus服务器端口
            user: 用户名
            password: 密码
            collection_name: 集合名称
            dimension: 向量维度
            metric_type: 相似度度量方式
            index_type: 索引类型
            auto_id: 是否自动生成ID
            timeout: 连接超时时间
        """
        # 配置信息
        self.host = host or os.environ.get("MILVUS_HOST", "localhost")
        self.port = port or os.environ.get("MILVUS_PORT", "19530")
        self.user = user or os.environ.get("MILVUS_USER", "")
        self.password = password or os.environ.get("MILVUS_PASSWORD", "")
        self.collection_name = collection_name
        self.dimension = dimension
        self.metric_type = self._format_metric_type(metric_type)
        self.index_type = index_type
        self.auto_id = auto_id
        self.timeout = timeout
        
        # 连接状态
        self._connected = False
        self._collection = None
        
        # 连接Milvus
        self._connect()
        
        # 初始化集合
        self._init_collection()
    
    def _format_metric_type(self, metric_type: str) -> str:
        """格式化相似度度量方式"""
        metric_map = {
            "cosine": "COSINE",
            "l2": "L2",
            "ip": "IP",
            "jaccard": "JACCARD",
            "hamming": "HAMMING"
        }
        return metric_map.get(metric_type.lower(), "COSINE")
    
    def _connect(self) -> None:
        """连接到Milvus服务器"""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                timeout=self.timeout
            )
            self._connected = True
            logger.info(f"连接到Milvus服务器: {self.host}:{self.port}")
        except MilvusException as e:
            self._connected = False
            logger.error(f"连接Milvus失败: {e}")
            raise
    
    def _init_collection(self) -> None:
        """初始化集合"""
        try:
            # 检查集合是否存在
            if utility.has_collection(self.collection_name):
                logger.info(f"集合已存在: {self.collection_name}")
                self._collection = Collection(self.collection_name)
                # 加载集合到内存
                self._collection.load()
            else:
                logger.info(f"创建新集合: {self.collection_name}")
                # 定义字段
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="metadata", dtype=DataType.JSON),
                    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
                ]
                
                # 创建集合模式
                schema = CollectionSchema(fields=fields, description="索克生活RAG向量存储")
                
                # 创建集合
                self._collection = Collection(
                    name=self.collection_name,
                    schema=schema,
                    using='default',
                    shards_num=2
                )
                
                # 创建索引
                index_params = self._get_index_params()
                self._collection.create_index(
                    field_name="vector",
                    index_params=index_params
                )
                
                # 加载集合到内存
                self._collection.load()
                
                logger.info(f"集合创建成功: {self.collection_name}")
        except MilvusException as e:
            logger.error(f"初始化集合失败: {e}")
            raise
    
    def _get_index_params(self) -> Dict[str, Any]:
        """获取索引参数"""
        if self.index_type == "HNSW":
            return {
                "index_type": "HNSW",
                "metric_type": self.metric_type,
                "params": {"M": 16, "efConstruction": 200}
            }
        elif self.index_type == "IVF_FLAT":
            return {
                "index_type": "IVF_FLAT",
                "metric_type": self.metric_type,
                "params": {"nlist": 1024}
            }
        elif self.index_type == "FLAT":
            return {
                "index_type": "FLAT",
                "metric_type": self.metric_type,
                "params": {}
            }
        else:
            # 默认使用HNSW
            return {
                "index_type": "HNSW",
                "metric_type": self.metric_type,
                "params": {"M": 16, "efConstruction": 200}
            }
    
    def ping(self) -> bool:
        """检查连接状态"""
        try:
            connections.get_connection_addr('default')
            return True
        except:
            return False
    
    def add(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict] = None) -> List[str]:
        """添加文本和向量到Milvus
        
        Args:
            texts: 文本列表
            embeddings: 向量列表
            metadatas: 元数据列表
            
        Returns:
            List[str]: 文档ID列表
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        # 检查输入
        count = len(texts)
        if len(embeddings) != count:
            raise ValueError(f"文本数量 ({count}) 与向量数量 ({len(embeddings)}) 不匹配")
            
        if metadatas is None:
            metadatas = [{} for _ in range(count)]
        elif len(metadatas) != count:
            raise ValueError(f"文本数量 ({count}) 与元数据数量 ({len(metadatas)}) 不匹配")
        
        # 生成ID
        ids = [str(uuid.uuid4()) for _ in range(count)]
        
        # 准备插入数据
        entities = [
            ids,
            texts,
            [json.dumps(meta) for meta in metadatas],
            embeddings
        ]
        
        try:
            # 插入数据
            insert_result = self._collection.insert(entities)
            self._collection.flush()
            logger.info(f"成功添加 {count} 条记录到 Milvus")
            return ids
        except MilvusException as e:
            logger.error(f"添加记录失败: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_expr: str = None,
        output_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索最相似的向量
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            filter_expr: 过滤表达式
            output_fields: 要返回的字段列表
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        # 默认输出字段
        if output_fields is None:
            output_fields = ["id", "text", "metadata"]
            
        # 搜索参数
        search_params = {"metric_type": self.metric_type}
        if self.index_type == "HNSW":
            search_params["params"] = {"ef": 100}
        elif self.index_type == "IVF_FLAT":
            search_params["params"] = {"nprobe": 16}
            
        try:
            # 执行搜索
            results = self._collection.search(
                data=[query_embedding],
                anns_field="vector",
                param=search_params,
                limit=top_k,
                expr=filter_expr,
                output_fields=output_fields
            )
            
            # 格式化结果
            formatted_results = []
            for hits in results:
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "score": hit.score,
                    }
                    
                    # 添加其他字段
                    for field in output_fields:
                        if field != "id":  # id已经添加
                            value = hit.entity.get(field)
                            # 处理JSON元数据
                            if field == "metadata" and isinstance(value, str):
                                try:
                                    value = json.loads(value)
                                except:
                                    value = {}
                            result[field] = value
                            
                    formatted_results.append(result)
                    
            return formatted_results
        except MilvusException as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    def delete(self, ids: List[str]) -> bool:
        """删除指定ID的记录
        
        Args:
            ids: 要删除的记录ID列表
            
        Returns:
            bool: 操作是否成功
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        try:
            expr = f'id in ["{"\",\"".join(ids)}"]'
            self._collection.delete(expr)
            logger.info(f"成功删除 {len(ids)} 条记录")
            return True
        except MilvusException as e:
            logger.error(f"删除记录失败: {e}")
            return False
    
    def update(self, id: str, text: str = None, embedding: List[float] = None, metadata: Dict = None) -> bool:
        """更新记录
        
        Args:
            id: 记录ID
            text: 新文本
            embedding: 新向量
            metadata: 新元数据
            
        Returns:
            bool: 操作是否成功
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        try:
            # 构建更新数据
            data = {}
            if text is not None:
                data["text"] = text
            if embedding is not None:
                data["vector"] = embedding
            if metadata is not None:
                data["metadata"] = json.dumps(metadata)
                
            if not data:
                return True  # 没有要更新的数据
                
            # 执行更新
            self._collection.update(
                expr=f'id == "{id}"',
                data=data
            )
            logger.info(f"成功更新记录 {id}")
            return True
        except MilvusException as e:
            logger.error(f"更新记录失败: {e}")
            return False
    
    def count(self, filter_expr: str = None) -> int:
        """获取记录数量
        
        Args:
            filter_expr: 过滤表达式
            
        Returns:
            int: 记录数量
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        try:
            return self._collection.num_entities
        except MilvusException as e:
            logger.error(f"获取记录数量失败: {e}")
            return 0
    
    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """通过ID获取记录
        
        Args:
            ids: 记录ID列表
            
        Returns:
            List[Dict[str, Any]]: 记录列表
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        try:
            expr = f'id in ["{"\",\"".join(ids)}"]'
            results = self._collection.query(
                expr=expr,
                output_fields=["id", "text", "metadata", "vector"]
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                metadata = result.get("metadata", "{}")
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                        
                formatted_results.append({
                    "id": result.get("id"),
                    "text": result.get("text"),
                    "metadata": metadata,
                    "vector": result.get("vector")
                })
                
            return formatted_results
        except MilvusException as e:
            logger.error(f"获取记录失败: {e}")
            return []
    
    def close(self) -> None:
        """关闭连接"""
        try:
            if self._collection:
                self._collection.release()
            connections.disconnect("default")
            logger.info("已关闭Milvus连接")
        except MilvusException as e:
            logger.error(f"关闭连接失败: {e}")
    
    def create_partition(self, partition_name: str, description: str = "") -> bool:
        """创建分区
        
        Args:
            partition_name: 分区名称
            description: 分区描述
            
        Returns:
            bool: 操作是否成功
        """
        if not self._collection:
            raise ValueError("集合未初始化")
            
        try:
            if not self._collection.has_partition(partition_name):
                self._collection.create_partition(partition_name, description=description)
                logger.info(f"成功创建分区: {partition_name}")
            else:
                logger.info(f"分区已存在: {partition_name}")
            return True
        except MilvusException as e:
            logger.error(f"创建分区失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            "connected": self._connected,
            "collection_name": self.collection_name,
            "total_records": 0,
            "index_type": self.index_type,
            "metric_type": self.metric_type,
            "dimension": self.dimension
        }
        
        if self._collection:
            try:
                stats["total_records"] = self._collection.num_entities
                index_info = self._collection.index().params
                stats["index_info"] = index_info
            except:
                pass
                
        return stats 