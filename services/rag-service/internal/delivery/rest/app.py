"""
app - 索克生活项目模块
"""

        from ...model.document import Document
from ...service.rag_service import RagService
from fastapi import FastAPI, HTTPException, Depends, Query, Body, Path, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import time

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API 应用
"""



# 请求和响应模型
class DocumentModel(BaseModel):
    """文档模型"""
    id: Optional[str] = Field(None, description="文档ID")
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    score: float = Field(0.0, description="相关性分数")
    source: Optional[str] = Field(None, description="文档来源")
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'documentmodel'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'searchrequest'
        ordering = ['-created_at']


class DocumentReferenceModel(BaseModel):
    """文档引用模型"""
    id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    source: str = Field(..., description="文档来源")
    url: Optional[str] = Field(None, description="文档URL")
    snippet: str = Field(..., description="引用片段")
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'searchresponse'
        ordering = ['-created_at']


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="查询文本")
    top_k: int = Field(5, description="返回结果数量")
    collection_names: Optional[List[str]] = Field(None, description="集合名称列表")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤条件")
    score_threshold: float = Field(0.7, description="相关性分数阈值")
    rerank: bool = Field(False, description="是否重排序")
    user_id: Optional[str] = Field(None, description="用户ID")
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'generateresponse'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'queryresponse'
        ordering = ['-created_at']


class SearchResponse(BaseModel):
    """搜索响应"""
    documents: List[DocumentModel] = Field(..., description="检索到的文档")
    latency_ms: float = Field(..., description="延迟(毫秒)")
    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'adddocumentrequest'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'adddocumentresponse'
        ordering = ['-created_at']

    class Meta:
        # 性能优化: 添加常用查询字段的索引
        indexes = [
            # 根据实际查询需求添加索引
            # models.Index(fields=['created_at']),
            # models.Index(fields=['user_id']),
            # models.Index(fields=['status']),
        ]
        # 数据库表选项
        db_table = 'deletedocumentresponse'
        ordering = ['-created_at']


class GenerateRequest(BaseModel):
    """生成请求"""
    query: str = Field(..., description="查询文本")
    context_documents: List[DocumentModel] = Field(..., description="上下文文档")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="生成参数")
    user_id: Optional[str] = Field(None, description="用户ID")

class GenerateResponse(BaseModel):
    """生成响应"""
    answer: str = Field(..., description="生成的回答")
    references: List[DocumentReferenceModel] = Field(..., description="引用的文档")
    latency_ms: float = Field(..., description="延迟(毫秒)")

class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询文本")
    top_k: int = Field(5, description="检索文档数量")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    collection_names: Optional[List[str]] = Field(None, description="集合名称列表")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="生成参数")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤条件")
    user_id: Optional[str] = Field(None, description="用户ID")

class QueryResponse(BaseModel):
    """查询响应"""
    answer: str = Field(..., description="生成的回答")
    references: List[DocumentReferenceModel] = Field(..., description="引用的文档")
    retrieval_latency_ms: float = Field(..., description="检索延迟(毫秒)")
    generation_latency_ms: float = Field(..., description="生成延迟(毫秒)")
    total_latency_ms: float = Field(..., description="总延迟(毫秒)")

class AddDocumentRequest(BaseModel):
    """添加文档请求"""
    document: DocumentModel = Field(..., description="要添加的文档")
    collection_name: str = Field("default", description="集合名称")
    reindex: bool = Field(True, description="是否重新索引")

class AddDocumentResponse(BaseModel):
    """添加文档响应"""
    document_id: str = Field(..., description="文档ID")
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")

class DeleteDocumentRequest(BaseModel):
    """删除文档请求"""
    document_id: str = Field(..., description="文档ID")
    collection_name: str = Field("default", description="集合名称")

class DeleteDocumentResponse(BaseModel):
    """删除文档响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    details: Dict[str, str] = Field(..., description="详细信息")

def create_app(config: Dict[str, Any]) -> FastAPI:
    """
    创建FastAPI应用
    
    Args:
        config: 配置信息
        
    Returns:
        FastAPI应用实例
    """
    # 创建RAG服务实例
    rag_service = RagService(config)
    
    # 创建FastAPI应用
    app = FastAPI(
        title="索克生活RAG服务",
        description="检索增强生成服务，提供知识检索和智能问答功能",
        version=config['service'].get('version', "0.1.0"),
    )
    
    # 添加中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config['server']['rest'].get('cors_origins', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # API前缀
    api_prefix = config['server']['rest'].get('api_prefix', "/api/v1")
    
    # 依赖项：获取RAG服务实例
    async def get_rag_service() -> RagService:
        """获取RAG服务实例"""
        if not rag_service.is_initialized:
            # 仅在第一次请求时初始化
            await rag_service.initialize()
        return rag_service
    
    # 健康检查端点
    @app.get(f"{api_prefix}/health", response_model=HealthResponse, tags=["系统"])
    async def health_check(rag_service: RagService = Depends(get_rag_service)):
        """健康检查"""
        try:
            status, details = await rag_service.health_check()
            return {"status": status, "details": details}
        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {"status": "NOT_SERVING", "details": {"error": str(e)}}
    
    # 搜索端点
    @app.post(f"{api_prefix}/search", response_model=SearchResponse, tags=["检索"])
    async def search(request: SearchRequest, rag_service: RagService = Depends(get_rag_service)):
        """搜索知识库"""
        start_time = time.time()
        
        try:
            # 调用服务执行检索
            result = await rag_service.retrieve(
                query=request.query,
                top_k=request.top_k,
                collection_names=request.collection_names,
                metadata_filter=request.metadata_filter,
                score_threshold=request.score_threshold,
                rerank=request.rerank,
                user_id=request.user_id
            )
            
            # 转换文档模型
            documents = [
                DocumentModel(
                    id=doc.id,
                    content=doc.content,
                    metadata=doc.metadata,
                    score=doc.score,
                    source=doc.source
                )
                for doc in result.documents
            ]
            
            return {
                "documents": documents,
                "latency_ms": result.latency_ms
            }
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
    
    # 生成端点
    @app.post(f"{api_prefix}/generate", response_model=GenerateResponse, tags=["生成"])
    async def generate(request: GenerateRequest, rag_service: RagService = Depends(get_rag_service)):
        """根据上下文生成回答"""
        try:
            # 转换上下文文档模型
            context_documents = [
                from_document_model(doc)
                for doc in request.context_documents
            ]
            
            # 调用服务执行生成
            result = await rag_service.generate(
                query=request.query,
                context_documents=context_documents,
                system_prompt=request.system_prompt,
                generation_params=request.generation_params,
                user_id=request.user_id
            )
            
            # 转换引用模型
            references = [
                DocumentReferenceModel(
                    id=ref.id,
                    title=ref.title,
                    source=ref.source,
                    url=ref.url,
                    snippet=ref.snippet
                )
                for ref in result.references
            ]
            
            return {
                "answer": result.answer,
                "references": references,
                "latency_ms": result.latency_ms
            }
            
        except Exception as e:
            logger.error(f"生成失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
    
    # 查询端点
    @app.post(f"{api_prefix}/query", response_model=QueryResponse, tags=["查询"])
    async def query(request: QueryRequest, rag_service: RagService = Depends(get_rag_service)):
        """执行检索增强生成查询"""
        try:
            # 调用服务执行查询
            result = await rag_service.query(
                query=request.query,
                top_k=request.top_k,
                system_prompt=request.system_prompt,
                collection_names=request.collection_names,
                generation_params=request.generation_params,
                metadata_filter=request.metadata_filter,
                user_id=request.user_id
            )
            
            # 转换引用模型
            references = [
                DocumentReferenceModel(
                    id=ref.id,
                    title=ref.title,
                    source=ref.source,
                    url=ref.url,
                    snippet=ref.snippet
                )
                for ref in result.references
            ]
            
            return {
                "answer": result.answer,
                "references": references,
                "retrieval_latency_ms": result.retrieval_latency_ms,
                "generation_latency_ms": result.generation_latency_ms,
                "total_latency_ms": result.total_latency_ms
            }
            
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    
    # 添加文档端点
    @app.post(f"{api_prefix}/knowledge/add", response_model=AddDocumentResponse, tags=["知识库管理"])
    async def add_document(
        request: AddDocumentRequest, 
        background_tasks: BackgroundTasks,
        rag_service: RagService = Depends(get_rag_service)
    ):
        """添加文档到知识库"""
        try:
            # 转换文档模型
            document = from_document_model(request.document)
            
            # 调用服务添加文档
            document_id = await rag_service.add_document(
                document=document,
                collection_name=request.collection_name,
                reindex=request.reindex
            )
            
            return {
                "document_id": document_id,
                "success": True,
                "message": "文档添加成功"
            }
            
        except Exception as e:
            logger.error(f"添加文档失败: {str(e)}")
            return {
                "document_id": "",
                "success": False,
                "message": f"添加文档失败: {str(e)}"
            }
    
    # 删除文档端点
    @app.post(f"{api_prefix}/knowledge/delete", response_model=DeleteDocumentResponse, tags=["知识库管理"])
    async def delete_document(
        request: DeleteDocumentRequest,
        rag_service: RagService = Depends(get_rag_service)
    ):
        """从知识库删除文档"""
        try:
            # 调用服务删除文档
            success = await rag_service.delete_document(
                document_id=request.document_id,
                collection_name=request.collection_name
            )
            
            if success:
                return {
                    "success": True,
                    "message": "文档删除成功"
                }
            else:
                return {
                    "success": False,
                    "message": "文档不存在或删除失败"
                }
            
        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return {
                "success": False,
                "message": f"删除文档失败: {str(e)}"
            }
    
    # 监控指标端点
    @app.get(f"{api_prefix}/metrics", tags=["系统"])
    async def metrics():
        """获取监控指标"""
        # 该功能需要集成Prometheus客户端库
        return {"message": "指标端点占位符，需要集成Prometheus客户端"}
    
    # 辅助函数：从API模型转换到内部模型
    def from_document_model(doc_model: DocumentModel):
        """将API文档模型转换为内部文档模型"""
        
        return Document(
            id=doc_model.id or "",
            content=doc_model.content,
            metadata=doc_model.metadata or {},
            score=doc_model.score,
            source=doc_model.source or ""
        )
    
    # 注册应用关闭事件
    @app.on_event("shutdown")
    async def shutdown_event():
        """应用关闭时清理资源"""
        logger.info("应用关闭，清理资源")
        await rag_service.close()
    
    return app