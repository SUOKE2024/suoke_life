#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档处理器
=======
用于文档分块、预处理和索引
"""

import re
import uuid
import hashlib
import time
from typing import List, Dict, Any, Optional, Union, Tuple
from loguru import logger

from ..vector_store import BaseVectorStore
from ..embeddings import EmbeddingManager


class DocumentProcessor:
    """文档处理器，用于文档分块、预处理和索引"""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embedding_manager: Optional[EmbeddingManager] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = ["\n\n", "\n", ". ", ", ", " ", ""]
    ):
        """
        初始化文档处理器
        
        Args:
            vector_store: 向量存储实例
            embedding_manager: 嵌入管理器实例，如不提供则从vector_store获取
            chunk_size: 文本块大小（字符数）
            chunk_overlap: 文本块重叠大小（字符数）
            separators: 分隔符列表，按优先级排序
        """
        self.vector_store = vector_store
        self.embedding_manager = embedding_manager or vector_store.embedding_manager
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        
    def process_document(
        self, 
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        sync: bool = True
    ) -> List[str]:
        """
        处理文档并添加到向量存储
        
        Args:
            document: 文档文本
            metadata: 文档元数据
            doc_id: 文档ID，如不提供则生成
            sync: 是否同步处理，False为异步处理（创建任务后立即返回）
            
        Returns:
            List[str]: 添加的块ID列表
        """
        if not document or not document.strip():
            logger.warning("文档为空，跳过处理")
            return []
            
        # 生成文档ID
        if not doc_id:
            doc_id = str(uuid.uuid4())
            
        # 准备元数据
        if metadata is None:
            metadata = {}
            
        # 添加文档级别的元数据
        doc_metadata = metadata.copy()
        doc_metadata.update({
            "doc_id": doc_id,
            "timestamp": int(time.time()),
            "document_hash": self._get_text_hash(document)
        })
        
        # 文档分块
        chunks = self.split_text(document)
        if not chunks:
            logger.warning("文档分块结果为空，跳过处理")
            return []
            
        # 准备块级别的元数据和ID
        chunk_ids = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            # 为每个块添加元数据
            chunk_metadata = doc_metadata.copy()
            chunk_metadata.update({
                "chunk_id": chunk_id,
                "chunk_index": i,
                "chunk_count": len(chunks)
            })
            chunk_metadatas.append(chunk_metadata)
        
        # 添加到向量存储
        try:
            result_ids = self.vector_store.add_texts(
                texts=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            logger.info(f"成功处理文档 {doc_id}，共添加了 {len(result_ids)} 个文本块")
            return result_ids
        except Exception as e:
            logger.error(f"处理文档失败: {e}")
            return []
            
    def process_documents(
        self, 
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None,
        sync: bool = True
    ) -> List[List[str]]:
        """
        批量处理文档并添加到向量存储
        
        Args:
            documents: 文档文本列表
            metadatas: 文档元数据列表
            doc_ids: 文档ID列表，如不提供则生成
            sync: 是否同步处理，False为异步处理（创建任务后立即返回）
            
        Returns:
            List[List[str]]: 每个文档添加的块ID列表的列表
        """
        if not documents:
            return []
            
        # 准备元数据
        if metadatas is None:
            metadatas = [{} for _ in range(len(documents))]
        elif len(metadatas) != len(documents):
            raise ValueError(f"metadatas长度({len(metadatas)})与documents长度({len(documents)})不匹配")
            
        # 准备文档ID
        if doc_ids is None:
            doc_ids = [str(uuid.uuid4()) for _ in range(len(documents))]
        elif len(doc_ids) != len(documents):
            raise ValueError(f"doc_ids长度({len(doc_ids)})与documents长度({len(documents)})不匹配")
            
        # 处理每个文档
        results = []
        for i, document in enumerate(documents):
            chunk_ids = self.process_document(
                document=document,
                metadata=metadatas[i],
                doc_id=doc_ids[i],
                sync=sync
            )
            results.append(chunk_ids)
            
        return results
            
    def split_text(
        self, 
        text: str, 
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = None
    ) -> List[str]:
        """
        将文本分割成块
        
        Args:
            text: 要分割的文本
            chunk_size: 块大小（字符数），如不提供则使用默认值
            chunk_overlap: 块重叠大小（字符数），如不提供则使用默认值
            separators: 分隔符列表，如不提供则使用默认值
            
        Returns:
            List[str]: 文本块列表
        """
        if not text or not text.strip():
            return []
            
        # 使用提供的参数或默认参数
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap
        separators = separators or self.separators
        
        # 清理文本
        text = self._clean_text(text)
        
        # 如果文本小于块大小，直接返回
        if len(text) <= chunk_size:
            return [text]
            
        # 分割文本
        return self._split_text_on_separators(
            text=text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators
        )
    
    def _clean_text(self, text: str) -> str:
        """清理文本，删除多余的空白字符"""
        # 替换制表符为空格
        text = text.replace("\t", " ")
        
        # 替换多个空格为单个空格
        text = re.sub(r" +", " ", text)
        
        # 删除行首和行尾的空白字符
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        
        # 删除空行
        lines = [line for line in lines if line]
        
        return "\n".join(lines)
        
    def _split_text_on_separators(
        self, 
        text: str, 
        chunk_size: int,
        chunk_overlap: int,
        separators: List[str]
    ) -> List[str]:
        """
        根据分隔符递归分割文本
        
        Args:
            text: 要分割的文本
            chunk_size: 块大小（字符数）
            chunk_overlap: 块重叠大小（字符数）
            separators: 分隔符列表
            
        Returns:
            List[str]: 文本块列表
        """
        # 如果没有分隔符了，按字符分割
        if not separators:
            return self._split_text_by_chunks(text, chunk_size, chunk_overlap)
            
        # 获取当前分隔符
        separator = separators[0]
        
        # 使用当前分隔符分割文本
        splits = text.split(separator)
        
        # 如果分割后只有一个元素，或者每个元素都很小，尝试下一个分隔符
        if len(splits) == 1 or max(len(s) for s in splits) < chunk_size / 2:
            return self._split_text_on_separators(
                text=text,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=separators[1:]
            )
            
        # 合并块，使其接近但不超过chunk_size
        good_splits = []
        current_split = []
        current_length = 0
        
        for split in splits:
            split_with_separator = split + separator if split != splits[-1] else split
            split_length = len(split_with_separator)
            
            # 如果当前块加上这个分割会超过chunk_size，保存当前块并开始新块
            if current_length + split_length > chunk_size and current_split:
                good_splits.append(separator.join(current_split))
                
                # 处理重叠
                if chunk_overlap > 0:
                    # 计算要保留的最后几个元素的索引
                    overlap_start_index = max(0, len(current_split) - chunk_overlap // len(separator))
                    current_split = current_split[overlap_start_index:]
                else:
                    current_split = []
                
                current_length = sum(len(s) + len(separator) for s in current_split)
            
            # 如果单个分割超过chunk_size，递归处理
            if split_length > chunk_size:
                # 为保持顺序，先处理之前累积的分割
                if current_split:
                    good_splits.append(separator.join(current_split))
                    current_split = []
                    current_length = 0
                
                # 递归处理这个大的分割
                sub_splits = self._split_text_on_separators(
                    text=split_with_separator,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=separators[1:]
                )
                good_splits.extend(sub_splits)
            else:
                # 添加到当前块
                current_split.append(split)
                current_length += split_length
        
        # 处理最后一个块
        if current_split:
            good_splits.append(separator.join(current_split))
        
        return good_splits
    
    def _split_text_by_chunks(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        按固定大小分割文本
        
        Args:
            text: 要分割的文本
            chunk_size: 块大小（字符数）
            chunk_overlap: 块重叠大小（字符数）
            
        Returns:
            List[str]: 文本块列表
        """
        # 如果文本小于块大小，直接返回
        if len(text) <= chunk_size:
            return [text]
            
        # 计算步长
        stride = chunk_size - chunk_overlap
        
        # 分割文本
        chunks = []
        for i in range(0, len(text), stride):
            chunk = text[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)
            
            # 如果剩余文本小于chunk_size，且不是最后一块，直接添加剩余文本并结束
            if i + chunk_size >= len(text) and i + stride < len(text):
                chunks.append(text[i + stride:])
                break
                
        return chunks
    
    def _get_text_hash(self, text: str) -> str:
        """计算文本的哈希值"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
        
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档及其所有块
        
        Args:
            doc_id: 文档ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 使用向量存储的过滤器查询功能找到所有相关块
            # 如果向量存储不支持此功能，则可能需要单独实现
            
            # 示例实现（假设向量存储支持元数据查询）
            document_chunks = []
            # 这里应该根据具体的向量存储实现方式来查询
            
            # 删除每个块
            if document_chunks:
                chunk_ids = [chunk["id"] for chunk in document_chunks]
                return self.vector_store.delete(chunk_ids)
            else:
                logger.warning(f"未找到文档 {doc_id} 的任何块")
                return True
                
        except Exception as e:
            logger.error(f"删除文档 {doc_id} 失败: {e}")
            return False 