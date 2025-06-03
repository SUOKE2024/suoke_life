#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Milvus向量数据库连接实现
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from pymilvus import (
    connections,
    utility,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
)
from loguru import logger

from ..model.document import Document

class MilvusRepository:
    """
    Milvus向量数据库存储库
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Milvus连接
        
        Args:
            config: 向量数据库配置
        """
        self.config = config
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 19530)
        self.collection_name = config.get('collection_name', 'suoke_knowledge')
        self.dimension = config.get('dimension', 768)
        self.distance_metric = config.get('distance_metric', 'COSINE')
        self.alias = "default"
        self.is_connected = False
        self.collection = None
    
    async def initialize(self):
        """初始化连接和集合"""
        try:
            logger.info(f"Connecting to Milvus at {self.host}:{self.port}")
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port
            )
            self.is_connected = True
            logger.info("Connected to Milvus successfully")
            
            # 检查集合是否存在，不存在则创建
            await self._ensure_collection()
            
            # 获取集合
            self.collection = Collection(name=self.collection_name)
            
            # 加载集合到内存
            self.collection.load()
            
            logger.info(f"Collection '{self.collection_name}' is ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {str(e)}")
            raise
    
    async def _ensure_collection(self):
        """确保集合存在，不存在则创建"""
        if utility.has_collection(self.collection_name):
            logger.info(f"Collection '{self.collection_name}' already exists")
            return
        
        logger.info(f"Creating collection '{self.collection_name}'")
        
        # 定义集合字段
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.JSON),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=255),
        ]
        
        # 创建集合架构
        schema = CollectionSchema(
            fields=fields, 
            description=f"索克生活知识库 - {self.collection_name}"
        )
        
        # 创建集合
        collection = Collection(
            name=self.collection_name, 
            schema=schema,
            using=self.alias
        )
        
        # 创建索引
        index_params = {
            "index_type": "HNSW",
            "metric_type": self.distance_metric,
            "params": {"M": 16, "efConstruction": 200}
        }
        
        collection.create_index(
            field_name="vector",
            index_params=index_params
        )
        
        logger.info(f"Collection '{self.collection_name}' created successfully with index")
    
    async def add_documents(self, documents: List[Document], batch_size: int = 100) -> bool:
        """
        批量添加文档到向量数据库
        
        Args:
            documents: 文档列表
            batch_size: 批处理大小
            
        Returns:
            是否成功
        """
        if not self.is_connected or self.collection is None:
            logger.error("Not connected to Milvus or collection not initialized")
            return False
        
        try:
            total_docs = len(documents)
            logger.info(f"Adding {total_docs} documents to collection '{self.collection_name}'")
            
            # 准备数据
            ids = []
            vectors = []
            contents = []
            metadata_list = []
            sources = []
            
            for doc in documents:
                if not hasattr(doc, 'vector') or doc.vector is None:
                    logger.warning(f"Document {doc.id} has no vector, skipping")
                    continue
                
                ids.append(doc.id)
                vectors.append(doc.vector)
                contents.append(doc.content)
                metadata_list.append(doc.metadata or {})
                sources.append(doc.source or "")
            
            # 批量插入
            for i in range(0, len(ids), batch_size):
                end = min(i + batch_size, len(ids))
                
                batch_data = [
                    ids[i:end],
                    vectors[i:end],
                    contents[i:end],
                    metadata_list[i:end],
                    sources[i:end]
                ]
                
                self.collection.insert(batch_data)
                logger.info(f"Inserted batch {i//batch_size + 1}/{(len(ids) + batch_size - 1)//batch_size}")
            
            # 刷新集合
            self.collection.flush()
            
            logger.info(f"Successfully added {len(ids)} documents to collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Milvus: {str(e)}")
            return False
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            document_ids: 要删除的文档ID列表
            
        Returns:
            是否成功
        """
        if not self.is_connected or self.collection is None:
            logger.error("Not connected to Milvus or collection not initialized")
            return False
        
        try:
            ids_str = ",".join([f'\"{doc_id}\"' for doc_id in document_ids])
            expr = f"id in [{ids_str}]"
            self.collection.delete(expr)
            self.collection.flush()
            
            logger.info(f"Successfully deleted {len(document_ids)} documents from collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents from Milvus: {str(e)}")
            return False
    
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[Document]:
        """
        向量搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            metadata_filter: 元数据过滤条件
            score_threshold: 相关性分数阈值
            
        Returns:
            文档列表
        """
        if not self.is_connected or self.collection is None:
            logger.error("Not connected to Milvus or collection not initialized")
            return []
        
        start_time = time.time()
        
        try:
            # 构建表达式过滤条件
            expr = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    if isinstance(value, str):
                        conditions.append(f"metadata['{key}'] == '{value}'")
                    elif isinstance(value, (int, float, bool)):
                        conditions.append(f"metadata['{key}'] == {value}")
                
                if conditions:
                    expr = " && ".join(conditions)
            
            # 搜索参数
            search_params = {
                "metric_type": self.distance_metric,
                "params": {"ef": 200}
            }
            
            # 执行搜索
            results = self.collection.search(
                data=[query_vector],  # 查询向量
                anns_field="vector",  # 搜索的向量字段
                param=search_params,
                limit=top_k,  # 返回的最大结果数
                expr=expr,  # 过滤表达式
                output_fields=["content", "metadata", "source"]  # 返回的字段
            )
            
            # 处理结果
            documents = []
            for hits in results:
                for hit in hits:
                    # 根据分数阈值过滤
                    if hasattr(hit, "distance"):
                        # 对于 COSINE，distance ∈ [0, 2] (Milvus 计算方式为 1 - cosSim)
                        # 对于 L2，distance ≥ 0，常见 embedding 通常距离不会很大
                        # 统一做 1 - distance 的近似归一化，必要时可在外部再做截断或缩放。
                        score = 1.0 - float(hit.distance)
                    else:
                        score = float(hit.score)
                    if score < score_threshold:
                        continue
                    
                    # 创建文档对象
                    doc = Document(
                        id=hit.id,
                        content=hit.entity.get('content'),
                        metadata=hit.entity.get('metadata', {}),
                        score=score,
                        source=hit.entity.get('source', "")
                    )
                    documents.append(doc)
            
            logger.debug(f"Search completed in {time.time() - start_time:.3f}s, found {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to search in Milvus: {str(e)}")
            return []
    
    async def get_all_documents(self, limit: Optional[int] = None) -> List[Document]:
        """
        获取集合中的所有文档（主要用于离线任务，如构建 BM25 索引）。

        NOTE:
            1. 该方法会一次性将结果加载到内存，若数据量较大请酌情设置 `limit` 或在调用端做分批处理。
            2. 目前 Milvus Python SDK 的 `query` 接口并不支持异步，这里仍采用同步调用，
               但整体方法保持 `async` 以与仓库其它接口保持一致。

        Args:
            limit: 最大返回文档数量，None 表示返回全部（谨慎使用）。

        Returns:
            包含 Document 对象的列表。
        """
        if not self.is_connected or self.collection is None:
            logger.error("Not connected to Milvus or collection not initialized")
            return []

        try:
            logger.info(f"Fetching all documents from collection '{self.collection_name}'" + (f" (limit={limit})" if limit else ""))

            query_results = self.collection.query(
                expr=None,  # 不设置过滤条件，查询全部
                output_fields=["id", "content", "metadata", "source"],
                limit=limit  # Milvus 3.x 支持 None 表示全部，旧版本需设置一个较大的数字
            )

            documents = [
                Document(
                    id=record.get("id"),
                    content=record.get("content", ""),
                    metadata=record.get("metadata", {}),
                    source=record.get("source", "")
                )
                for record in query_results
            ]

            logger.info(f"Fetched {len(documents)} documents from collection '{self.collection_name}'")
            return documents
        except Exception as e:
            logger.error(f"Failed to fetch documents from Milvus: {str(e)}")
            return []
    
    async def close(self):
        """关闭连接"""
        try:
            if self.collection:
                self.collection.release()
            
            connections.disconnect(self.alias)
            self.is_connected = False
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error closing Milvus connection: {str(e)}") 