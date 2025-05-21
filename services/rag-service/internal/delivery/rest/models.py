#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API 数据模型
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentReference(BaseModel):
    """文档引用"""
    id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    source: str = Field(..., description="文档来源")
    url: Optional[str] = Field(None, description="文档URL")
    snippet: str = Field(..., description="相关片段")


class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="用户查询")
    topK: Optional[int] = Field(5, description="返回的最相关文档数量")
    systemPrompt: Optional[str] = Field(None, description="系统提示词")
    collectionNames: Optional[List[str]] = Field(None, description="在特定集合中搜索")
    generationParams: Optional[Dict[str, str]] = Field(None, description="生成参数")
    metadataFilter: Optional[Dict[str, str]] = Field(None, description="元数据过滤")
    userId: Optional[str] = Field(None, description="用户ID")


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str = Field(..., description="生成的回答")
    references: List[DocumentReference] = Field(default_factory=list, description="引用的文档")
    retrievalLatencyMs: float = Field(..., description="检索耗时(毫秒)")
    generationLatencyMs: float = Field(..., description="生成耗时(毫秒)")
    totalLatencyMs: float = Field(..., description="总耗时(毫秒)")


class AddDocumentRequest(BaseModel):
    """添加文档请求"""
    content: str = Field(..., description="文档内容")
    metadata: Optional[Dict[str, str]] = Field(None, description="文档元数据")
    reindex: Optional[bool] = Field(False, description="是否重新索引")
    collectionName: Optional[str] = Field("default", description="集合名称")


class AddDocumentResponse(BaseModel):
    """添加文档响应"""
    documentId: str = Field(..., description="文档ID")
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")


class DeleteDocumentResponse(BaseModel):
    """删除文档响应"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="消息")


class DocumentMetadata(BaseModel):
    """文档元数据"""
    id: str = Field(..., description="文档ID")
    title: Optional[str] = Field(None, description="文档标题")
    metadata: Dict[str, str] = Field(default_factory=dict, description="文档元数据")
    createdAt: Optional[str] = Field(None, description="创建时间")
    updatedAt: Optional[str] = Field(None, description="更新时间")


class ListDocumentsResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentMetadata] = Field(..., description="文档列表")
    total: int = Field(..., description="文档总数")
    page: int = Field(1, description="当前页码")
    pageSize: int = Field(20, description="每页数量")


class Collection(BaseModel):
    """知识集合"""
    name: str = Field(..., description="集合名称")
    documentCount: int = Field(0, description="文档数量")
    description: Optional[str] = Field(None, description="集合描述")
    lastUpdated: Optional[str] = Field(None, description="最后更新时间")


class ListCollectionsResponse(BaseModel):
    """集合列表响应"""
    collections: List[Collection] = Field(..., description="集合列表")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态", enum=["UNKNOWN", "SERVING", "NOT_SERVING"])
    details: Dict[str, str] = Field(default_factory=dict, description="详细信息")