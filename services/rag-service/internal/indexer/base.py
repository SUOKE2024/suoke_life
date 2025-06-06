"""
base - 索克生活项目模块
"""

from ..model.document import Document, Chunk
from typing import List, Dict, Any, Optional
import abc

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
索引器基类定义
"""



class BaseIndexer(abc.ABC):
    """
    索引器基类，定义了索引器的通用接口
    """
    
    @abc.abstractmethod
    async def initialize(self):
        """初始化索引器，建立连接和索引"""
        pass
    
    @abc.abstractmethod
    async def add_document(self, document: Document) -> str:
        """
        添加文档到索引
        
        Args:
            document: 文档对象
            
        Returns:
            文档ID
        """
        pass
    
    @abc.abstractmethod
    async def add_documents(self, documents: List[Document]) -> List[str]:
        """
        批量添加文档到索引
        
        Args:
            documents: 文档对象列表
            
        Returns:
            文档ID列表
        """
        pass
    
    @abc.abstractmethod
    async def get_document(self, document_id: str, collection_name: Optional[str] = None) -> Optional[Document]:
        """
        获取文档
        
        Args:
            document_id: 文档ID
            collection_name: 集合名称
            
        Returns:
            文档对象，如果不存在则返回None
        """
        pass
    
    @abc.abstractmethod
    async def delete_document(self, document_id: str, collection_name: Optional[str] = None) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            collection_name: 集合名称
            
        Returns:
            是否成功删除
        """
        pass
    
    @abc.abstractmethod
    async def search(
        self, 
        query_vector: List[float], 
        top_k: int = 5, 
        collection_name: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None,
        score_threshold: float = 0.0
    ) -> List[Chunk]:
        """
        向量搜索
        
        Args:
            query_vector: 查询向量
            top_k: 返回结果数量
            collection_name: 集合名称
            filter_dict: 过滤条件
            score_threshold: 分数阈值
            
        Returns:
            匹配的文档分块列表
        """
        pass
    
    @abc.abstractmethod
    async def create_collection(self, collection_name: str, dimension: int, description: Optional[str] = None) -> bool:
        """
        创建集合
        
        Args:
            collection_name: 集合名称
            dimension: 向量维度
            description: 集合描述
            
        Returns:
            是否成功创建
        """
        pass
    
    @abc.abstractmethod
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        列出所有集合
        
        Returns:
            集合信息列表
        """
        pass
    
    @abc.abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """
        检查集合是否存在
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否存在
        """
        pass
    
    @abc.abstractmethod
    async def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否成功删除
        """
        pass
    
    @abc.abstractmethod
    async def count_documents(self, collection_name: Optional[str] = None) -> int:
        """
        统计文档数量
        
        Args:
            collection_name: 集合名称
            
        Returns:
            文档数量
        """
        pass
    
    @abc.abstractmethod
    async def close(self):
        """关闭索引器连接"""
        pass