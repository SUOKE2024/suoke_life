"""
document - 索克生活项目模块
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
import uuid

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档和结果模型定义
"""


@dataclass
class Document:
    """知识库文档模型"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    source: str = ""
    vector: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "score": self.score,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """从字典创建文档"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            score=data.get("score", 0.0),
            source=data.get("source", ""),
            vector=data.get("vector", None)
        )

@dataclass
class DocumentReference:
    """文档引用模型，用于生成答案时引用的文档来源"""
    
    id: str
    title: str = ""
    source: str = ""
    url: str = ""
    snippet: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "snippet": self.snippet
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentReference':
        """从字典创建文档引用"""
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            source=data.get("source", ""),
            url=data.get("url", ""),
            snippet=data.get("snippet", "")
        )

@dataclass
class RetrieveResult:
    """检索结果"""
    
    documents: List[Document] = field(default_factory=list)
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "documents": [doc.to_dict() for doc in self.documents],
            "latency_ms": self.latency_ms
        }

@dataclass
class GenerateResult:
    """生成结果"""
    
    answer: str = ""
    references: List[DocumentReference] = field(default_factory=list)
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "answer": self.answer,
            "references": [ref.to_dict() for ref in self.references],
            "latency_ms": self.latency_ms
        }

@dataclass
class QueryResult:
    """查询结果（检索+生成）"""
    
    answer: str = ""
    references: List[DocumentReference] = field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "answer": self.answer,
            "references": [ref.to_dict() for ref in self.references],
            "retrieval_latency_ms": self.retrieval_latency_ms,
            "generation_latency_ms": self.generation_latency_ms,
            "total_latency_ms": self.total_latency_ms
        }

@dataclass
class QueryRequest:
    """查询请求"""
    
    query: str
    top_k: int = 3
    system_prompt: str = ""
    collection_names: List[str] = field(default_factory=list)
    generation_params: Dict[str, Any] = field(default_factory=dict)
    metadata_filter: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "query": self.query,
            "top_k": self.top_k,
            "system_prompt": self.system_prompt,
            "collection_names": self.collection_names,
            "generation_params": self.generation_params,
            "metadata_filter": self.metadata_filter,
            "user_id": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryRequest':
        """从字典创建查询请求"""
        return cls(
            query=data.get("query", ""),
            top_k=data.get("top_k", 3),
            system_prompt=data.get("system_prompt", ""),
            collection_names=data.get("collection_names", []),
            generation_params=data.get("generation_params", {}),
            metadata_filter=data.get("metadata_filter", {}),
            user_id=data.get("user_id")
        )