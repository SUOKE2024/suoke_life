#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG服务增强版API网关
提供RESTful API接口，支持检索增强生成、文档管理、批量处理和性能监控
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn
import json

# 导入服务
from services.rag_service.internal.service.enhanced_rag_service import (
    EnhancedRagService, IndexType, ShardingStrategy
)
from services.rag_service.internal.model.document import Document
from services.rag_service.internal.multimodal.feature_extractors import (
    extract_image_text, extract_audio_text, extract_video_keyframes
)

# 导入通用组件
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RAG服务API",
    description="索克生活RAG服务，提供高性能的检索增强生成功能，支持向量索引优化、知识库分片和批量推理",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
rag_service: Optional[EnhancedRagService] = None

# 请求模型
class QueryRequest(BaseModel):
    """查询请求"""
    query: str = Field(..., description="查询文本")
    top_k: int = Field(5, description="返回文档数量")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    collection_names: Optional[List[str]] = Field(None, description="集合名称列表")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="生成参数")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤条件")
    user_id: Optional[str] = Field(None, description="用户ID")

class RetrieveRequest(BaseModel):
    """检索请求"""
    query: str = Field(..., description="查询文本")
    top_k: int = Field(5, description="返回文档数量")
    collection_names: Optional[List[str]] = Field(None, description="集合名称列表")
    metadata_filter: Optional[Dict[str, Any]] = Field(None, description="元数据过滤条件")
    score_threshold: float = Field(0.0, description="相关性分数阈值")
    rerank: bool = Field(False, description="是否重排序")
    user_id: Optional[str] = Field(None, description="用户ID")

class GenerateRequest(BaseModel):
    """生成请求"""
    query: str = Field(..., description="查询文本")
    context_documents: List[Dict[str, Any]] = Field(..., description="上下文文档")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    generation_params: Optional[Dict[str, Any]] = Field(None, description="生成参数")
    user_id: Optional[str] = Field(None, description="用户ID")

class DocumentRequest(BaseModel):
    """文档请求"""
    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    collection_name: str = Field("default", description="集合名称")

class BatchDocumentRequest(BaseModel):
    """批量文档请求"""
    documents: List[DocumentRequest] = Field(..., description="文档列表")
    collection_name: str = Field("default", description="集合名称")
    use_sharding: bool = Field(True, description="是否使用分片")

# 响应模型
class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    references: List[Dict[str, Any]]
    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float

class RetrieveResponse(BaseModel):
    """检索响应"""
    documents: List[Dict[str, Any]]
    latency_ms: float

class GenerateResponse(BaseModel):
    """生成响应"""
    answer: str
    references: List[Dict[str, Any]]
    latency_ms: float

class ServiceStats(BaseModel):
    """服务统计"""
    total_queries: int
    cache_hit_rate: float
    average_latency_ms: float
    batch_processed: int
    sharding: Dict[str, Any]
    cache_sizes: Dict[str, int]
    queue_sizes: Dict[str, int]

# 中间件
@app.middleware("http")
async def add_tracing(request, call_next):
    """添加分布式追踪"""
    tracer = get_tracer("rag-api")
    
    with tracer.start_span(
        f"{request.method} {request.url.path}",
        kind=SpanKind.SERVER
    ) as span:
        # 添加请求信息到span
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.scheme", request.url.scheme)
        span.set_attribute("http.host", request.url.hostname)
        span.set_attribute("http.target", request.url.path)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加响应信息到span
        span.set_attribute("http.status_code", response.status_code)
        
        return response

# 依赖项
async def get_rag_service() -> EnhancedRagService:
    """获取RAG服务实例"""
    global rag_service
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG服务未初始化")
    return rag_service

# API端点
@app.post("/api/v1/rag/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    执行检索增强生成查询
    
    完整的RAG流程：检索相关文档 -> 生成回答
    """
    try:
        result = await service.query(
            query=request.query,
            top_k=request.top_k,
            system_prompt=request.system_prompt,
            collection_names=request.collection_names,
            generation_params=request.generation_params,
            metadata_filter=request.metadata_filter,
            user_id=request.user_id
        )
        
        return QueryResponse(
            answer=result.answer,
            references=[ref.__dict__ for ref in result.references],
            retrieval_latency_ms=result.retrieval_latency_ms,
            generation_latency_ms=result.generation_latency_ms,
            total_latency_ms=result.total_latency_ms
        )
        
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/query/stream")
async def query_stream(
    request: QueryRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    执行流式检索增强生成查询
    
    返回Server-Sent Events流，实时返回生成的内容
    """
    async def generate():
        try:
            async for fragment, is_final, references in service.stream_query(
                query=request.query,
                top_k=request.top_k,
                system_prompt=request.system_prompt,
                collection_names=request.collection_names,
                generation_params=request.generation_params,
                metadata_filter=request.metadata_filter,
                user_id=request.user_id
            ):
                data = {
                    "fragment": fragment,
                    "is_final": is_final
                }
                if is_final and references:
                    data["references"] = [ref.__dict__ for ref in references]
                
                yield f"data: {json.dumps(data)}\n\n"
                
        except Exception as e:
            logger.error(f"流式查询失败: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/v1/rag/retrieve", response_model=RetrieveResponse)
async def retrieve(
    request: RetrieveRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    执行文档检索
    
    仅返回相关文档，不进行生成
    """
    try:
        result = await service.retrieve(
            query=request.query,
            top_k=request.top_k,
            collection_names=request.collection_names,
            metadata_filter=request.metadata_filter,
            score_threshold=request.score_threshold,
            rerank=request.rerank,
            user_id=request.user_id
        )
        
        return RetrieveResponse(
            documents=[doc.__dict__ for doc in result.documents],
            latency_ms=result.latency_ms
        )
        
    except Exception as e:
        logger.error(f"检索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    基于上下文生成回答
    
    使用提供的文档作为上下文生成回答
    """
    try:
        # 转换文档格式
        context_documents = []
        for doc_data in request.context_documents:
            doc = Document(
                id=doc_data.get("id"),
                content=doc_data["content"],
                metadata=doc_data.get("metadata", {}),
                vector=doc_data.get("vector")
            )
            context_documents.append(doc)
        
        result = await service.generate(
            query=request.query,
            context_documents=context_documents,
            system_prompt=request.system_prompt,
            generation_params=request.generation_params,
            user_id=request.user_id
        )
        
        return GenerateResponse(
            answer=result.answer,
            references=[ref.__dict__ for ref in result.references],
            latency_ms=result.latency_ms
        )
        
    except Exception as e:
        logger.error(f"生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/documents")
async def add_document(
    request: DocumentRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    添加单个文档到知识库
    """
    try:
        document = Document(
            content=request.content,
            metadata=request.metadata
        )
        
        doc_id = await service.add_document(
            document=document,
            collection_name=request.collection_name
        )
        
        return {
            "status": "success",
            "document_id": doc_id,
            "message": "文档添加成功"
        }
        
    except Exception as e:
        logger.error(f"添加文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/documents/batch")
async def add_documents_batch(
    request: BatchDocumentRequest,
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    批量添加文档到知识库
    
    支持分片存储和并行处理
    """
    try:
        documents = []
        for doc_req in request.documents:
            document = Document(
                content=doc_req.content,
                metadata=doc_req.metadata
            )
            documents.append(document)
        
        doc_ids = await service.add_documents_batch(
            documents=documents,
            collection_name=request.collection_name,
            use_sharding=request.use_sharding
        )
        
        return {
            "status": "success",
            "document_ids": doc_ids,
            "count": len(doc_ids),
            "message": f"成功添加{len(doc_ids)}个文档"
        }
        
    except Exception as e:
        logger.error(f"批量添加文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/documents/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    collection_name: str = Query("default", description="集合名称"),
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    上传文档文件
    
    支持txt、pdf、docx等格式
    """
    try:
        documents = []
        
        for file in files:
            # 读取文件内容
            content = await file.read()
            
            # 根据文件类型处理（这里简化处理，实际需要更复杂的文档解析）
            if file.filename.endswith('.txt'):
                text_content = content.decode('utf-8')
            else:
                # 其他格式需要专门的解析器
                text_content = f"文件内容: {file.filename}"
            
            document = Document(
                content=text_content,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "upload_time": datetime.now().isoformat()
                }
            )
            documents.append(document)
        
        # 批量添加文档
        doc_ids = await service.add_documents_batch(
            documents=documents,
            collection_name=collection_name
        )
        
        return {
            "status": "success",
            "document_ids": doc_ids,
            "count": len(doc_ids),
            "message": f"成功上传{len(doc_ids)}个文档"
        }
        
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/rag/documents/{document_id}")
async def delete_document(
    document_id: str,
    collection_name: str = Query("default", description="集合名称"),
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    删除文档
    """
    try:
        success = await service.delete_document(
            document_id=document_id,
            collection_name=collection_name
        )
        
        if success:
            return {
                "status": "success",
                "message": f"文档{document_id}删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="文档不存在")
            
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/optimize/indices")
async def optimize_indices(
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    优化向量索引
    
    根据查询模式自动优化索引参数
    """
    try:
        await service.optimize_indices()
        
        return {
            "status": "success",
            "message": "索引优化完成"
        }
        
    except Exception as e:
        logger.error(f"索引优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/rag/stats", response_model=ServiceStats)
async def get_stats(
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    获取服务统计信息
    
    包括查询统计、缓存命中率、分片信息等
    """
    try:
        stats = await service.get_service_stats()
        
        return ServiceStats(
            total_queries=stats['total_queries'],
            cache_hit_rate=stats['cache_hit_rate'],
            average_latency_ms=stats['average_latency_ms'],
            batch_processed=stats['batch_processed'],
            sharding=stats['sharding'],
            cache_sizes=stats['cache_sizes'],
            queue_sizes=stats['queue_sizes']
        )
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/rag/metrics")
async def get_metrics(
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    获取Prometheus格式的指标
    """
    try:
        stats = await service.get_service_stats()
        
        # 构建Prometheus格式的指标
        metrics = []
        
        # 查询指标
        metrics.append(f'# HELP rag_total_queries Total number of queries')
        metrics.append(f'# TYPE rag_total_queries counter')
        metrics.append(f'rag_total_queries {stats["total_queries"]}')
        
        # 缓存命中率
        metrics.append(f'# HELP rag_cache_hit_rate Cache hit rate')
        metrics.append(f'# TYPE rag_cache_hit_rate gauge')
        metrics.append(f'rag_cache_hit_rate {stats["cache_hit_rate"]}')
        
        # 平均延迟
        metrics.append(f'# HELP rag_average_latency_ms Average query latency in milliseconds')
        metrics.append(f'# TYPE rag_average_latency_ms gauge')
        metrics.append(f'rag_average_latency_ms {stats["average_latency_ms"]}')
        
        # 批处理数量
        metrics.append(f'# HELP rag_batch_processed Total number of batches processed')
        metrics.append(f'# TYPE rag_batch_processed counter')
        metrics.append(f'rag_batch_processed {stats["batch_processed"]}')
        
        # 分片指标
        if stats['sharding']['enabled']:
            for shard_id, shard_info in stats['sharding']['shards'].items():
                metrics.append(f'# HELP rag_shard_document_count Number of documents in shard')
                metrics.append(f'# TYPE rag_shard_document_count gauge')
                metrics.append(f'rag_shard_document_count{{shard="{shard_id}"}} {shard_info["document_count"]}')
                
                metrics.append(f'# HELP rag_shard_queries Number of queries to shard')
                metrics.append(f'# TYPE rag_shard_queries counter')
                metrics.append(f'rag_shard_queries{{shard="{shard_id}"}} {shard_info["queries"]}')
        
        # 缓存大小
        for cache_level, size in stats['cache_sizes'].items():
            metrics.append(f'# HELP rag_cache_size Cache size by level')
            metrics.append(f'# TYPE rag_cache_size gauge')
            metrics.append(f'rag_cache_size{{level="{cache_level}"}} {size}')
        
        # 队列大小
        for queue_name, size in stats['queue_sizes'].items():
            metrics.append(f'# HELP rag_queue_size Queue size')
            metrics.append(f'# TYPE rag_queue_size gauge')
            metrics.append(f'rag_queue_size{{queue="{queue_name}"}} {size}')
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/rag/query_multimodal")
async def query_multimodal(
    query: str = Form(..., description="查询文本"),
    files: Optional[List[UploadFile]] = File(None, description="多模态文件（图片/音频/视频等）"),
    system_prompt: Optional[str] = Form(None),
    collection_names: Optional[str] = Form(None),
    generation_params: Optional[str] = Form(None),
    metadata_filter: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    多模态RAG推理接口，支持文本+图片/音频/视频联合推理
    """
    multimodal_context = []
    multimodal_texts = []
    if files:
        for file in files:
            content = await file.read()
            if file.content_type.startswith('image/'):
                ocr_text = extract_image_text(content)
                multimodal_context.append({"type": "image", "filename": file.filename, "ocr_text": ocr_text})
                multimodal_texts.append(ocr_text)
            elif file.content_type.startswith('audio/'):
                asr_text = extract_audio_text(content)
                multimodal_context.append({"type": "audio", "filename": file.filename, "asr_text": asr_text})
                multimodal_texts.append(asr_text)
            elif file.content_type.startswith('video/'):
                keyframes = extract_video_keyframes(content)
                frame_texts = []
                for idx, frame_bytes in enumerate(keyframes):
                    ocr_text = extract_image_text(frame_bytes)
                    frame_texts.append(ocr_text)
                multimodal_context.append({"type": "video", "filename": file.filename, "frame_ocr_texts": frame_texts})
                multimodal_texts.extend(frame_texts)
            else:
                multimodal_context.append({"type": "file", "filename": file.filename})
    # 拼接多模态文本作为RAG上下文
    full_query = query + "\n" + "\n".join([t for t in multimodal_texts if t])
    result = await service.query(
        query=full_query,
        top_k=5,
        system_prompt=system_prompt,
        collection_names=None,
        generation_params=None,
        metadata_filter=None,
        user_id=user_id
    )
    return {
        "answer": result.answer,
        "references": [ref.__dict__ for ref in result.references],
        "multimodal_context": multimodal_context,
        "retrieval_latency_ms": result.retrieval_latency_ms,
        "generation_latency_ms": result.generation_latency_ms,
        "total_latency_ms": result.total_latency_ms
    }

@app.post("/api/v1/rag/documents/upload_multimodal")
async def upload_documents_multimodal(
    files: List[UploadFile] = File(...),
    collection_name: str = Query("default", description="集合名称"),
    service: EnhancedRagService = Depends(get_rag_service)
):
    """
    多模态文件上传接口，支持图片、音频、视频、PDF等
    """
    try:
        documents = []
        for file in files:
            content = await file.read()
            doc_type = file.content_type.split('/')[0]
            if doc_type == 'image':
                ocr_text = extract_image_text(content)
                text_content = f"图片OCR: {ocr_text}"
            elif doc_type == 'audio':
                asr_text = extract_audio_text(content)
                text_content = f"音频ASR: {asr_text}"
            elif doc_type == 'video':
                keyframes = extract_video_keyframes(content)
                frame_texts = []
                for idx, frame_bytes in enumerate(keyframes):
                    ocr_text = extract_image_text(frame_bytes)
                    frame_texts.append(ocr_text)
                text_content = f"视频帧OCR: {'; '.join(frame_texts)}"
            else:
                text_content = f"文件内容: {file.filename}"
            document = Document(
                content=text_content,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "upload_time": datetime.now().isoformat()
                }
            )
            documents.append(document)
        doc_ids = await service.add_documents_batch(
            documents=documents,
            collection_name=collection_name
        )
        return {
            "status": "success",
            "document_ids": doc_ids,
            "count": len(doc_ids),
            "message": f"成功上传{len(doc_ids)}个多模态文件"
        }
    except Exception as e:
        logger.error(f"多模态文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@app.get("/health")
async def health_check():
    """基本健康检查"""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check(
    service: EnhancedRagService = Depends(get_rag_service)
):
    """就绪检查"""
    try:
        status, details = await service.health_check()
        
        if status != "SERVING":
            raise HTTPException(
                status_code=503,
                detail=f"服务未就绪: {details.get('reason', 'Unknown')}"
            )
        
        return {
            "status": "ready",
            "details": details
        }
        
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global rag_service
    
    logger.info("RAG服务API启动中...")
    
    # 初始化服务
    try:
        # 加载配置
        config = {
            "service": {
                "name": "rag-service",
                "version": "2.0.0"
            },
            "vector_database": {
                "host": "localhost",
                "port": 19530,
                "collection_name": "rag_documents"
            },
            "generator": {
                "model_type": "openai",  # 或 "local"
                "model_name": "gpt-3.5-turbo"
            },
            "cache": {
                "redis_url": "redis://localhost:6379/4"
            }
        }
        
        rag_service = EnhancedRagService(config)
        await rag_service.initialize()
        
        logger.info("RAG服务初始化成功")
        
    except Exception as e:
        logger.error(f"RAG服务初始化失败: {e}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global rag_service
    
    logger.info("RAG服务API关闭中...")
    
    # 清理资源
    try:
        if rag_service:
            await rag_service.close()
            logger.info("RAG服务清理完成")
    except Exception as e:
        logger.error(f"RAG服务清理失败: {e}")

# 主函数
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8085,
        reload=True,
        log_level="info"
    ) 