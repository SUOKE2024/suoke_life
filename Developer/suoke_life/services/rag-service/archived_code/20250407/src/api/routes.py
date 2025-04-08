#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API路由和处理函数
=============
定义API路由和处理函数
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
from flask import Flask, Blueprint, request, jsonify, current_app, Response, stream_with_context
from loguru import logger
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..config import VERSION, SERVICE_NAME
from ..rag import RAGEngine, ResultFormatter


# 创建单例RAG引擎
_rag_engine = None

def get_rag_engine() -> RAGEngine:
    """
    获取RAG引擎单例实例
    
    Returns:
        RAGEngine: RAG引擎实例
    """
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
        logger.info("创建RAG引擎单例实例")
    return _rag_engine


def register_routes(app: Flask) -> None:
    """
    注册API路由
    
    Args:
        app: Flask应用实例
    """
    # 健康检查路由
    @app.route('/health', methods=['GET'])
    def health_check():
        """健康检查接口"""
        rag_engine = get_rag_engine()
        vector_store_count = 0
        
        try:
            vector_store_count = rag_engine.vector_store.count()
        except Exception as e:
            logger.warning(f"获取向量存储计数失败: {e}")
            
        status = {
            "status": "healthy",
            "service": SERVICE_NAME,
            "version": VERSION,
            "timestamp": int(time.time()),
            "vector_count": vector_store_count,
            "llm_client": rag_engine.llm_client.model_name if rag_engine.llm_client else None,
            "reranker": rag_engine.reranker.model_name if rag_engine.reranker else None
        }
        return jsonify(status)
    
    # API版本前缀
    api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
    
    # 文档管理路由
    @api_v1.route('/documents', methods=['POST'])
    def add_document():
        """添加文档接口"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": True, "message": "请求体为空或非JSON格式"}), 400
                
            # 验证必须字段
            if 'text' not in data:
                return jsonify({"error": True, "message": "缺少必要字段 'text'"}), 400
                
            # 提取参数
            text = data['text']
            metadata = data.get('metadata', {})
            doc_id = data.get('doc_id')
            
            # 添加文档
            rag_engine = get_rag_engine()
            chunk_ids = rag_engine.add_document(
                document=text,
                metadata=metadata,
                doc_id=doc_id
            )
            
            return jsonify({
                "success": True,
                "doc_id": doc_id,
                "chunk_count": len(chunk_ids),
                "chunk_ids": chunk_ids
            })
            
        except Exception as e:
            logger.error(f"添加文档失败: {e}")
            return jsonify({"error": True, "message": f"添加文档失败: {str(e)}"}), 500
    
    @api_v1.route('/documents/batch', methods=['POST'])
    def add_documents_batch():
        """批量添加文档接口"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": True, "message": "请求体为空或非JSON格式"}), 400
                
            # 验证必须字段
            if 'documents' not in data or not isinstance(data['documents'], list):
                return jsonify({"error": True, "message": "缺少必要字段 'documents' 或格式不是数组"}), 400
                
            documents = []
            metadatas = []
            doc_ids = []
            
            # 处理每个文档
            for doc in data['documents']:
                if not isinstance(doc, dict) or 'text' not in doc:
                    return jsonify({"error": True, "message": "文档数组中的项必须是包含 'text' 字段的对象"}), 400
                    
                documents.append(doc['text'])
                metadatas.append(doc.get('metadata', {}))
                doc_ids.append(doc.get('doc_id'))
                
            # 批量添加文档
            rag_engine = get_rag_engine()
            results = rag_engine.add_documents(
                documents=documents,
                metadatas=metadatas,
                doc_ids=doc_ids
            )
            
            # 准备响应
            response_docs = []
            for i, (doc_id, chunk_ids) in enumerate(zip(doc_ids, results)):
                response_docs.append({
                    "doc_id": doc_id,
                    "chunk_count": len(chunk_ids),
                    "chunk_ids": chunk_ids
                })
                
            return jsonify({
                "success": True,
                "total_documents": len(documents),
                "documents": response_docs
            })
            
        except Exception as e:
            logger.error(f"批量添加文档失败: {e}")
            return jsonify({"error": True, "message": f"批量添加文档失败: {str(e)}"}), 500
    
    @api_v1.route('/documents/<doc_id>', methods=['DELETE'])
    def delete_document(doc_id):
        """删除文档接口"""
        try:
            rag_engine = get_rag_engine()
            success = rag_engine.delete_document(doc_id)
            
            if success:
                return jsonify({
                    "success": True,
                    "doc_id": doc_id,
                    "message": "文档删除成功"
                })
            else:
                return jsonify({
                    "error": True,
                    "message": f"文档 {doc_id} 删除失败"
                }), 500
                
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return jsonify({"error": True, "message": f"删除文档失败: {str(e)}"}), 500
    
    # 搜索和查询路由
    @api_v1.route('/search', methods=['POST'])
    def search():
        """搜索接口"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": True, "message": "请求体为空或非JSON格式"}), 400
                
            # 验证必须字段
            if 'query' not in data:
                return jsonify({"error": True, "message": "缺少必要字段 'query'"}), 400
                
            # 提取参数
            query = data['query']
            k = data.get('k', 5)
            filter = data.get('filter')
            rerank = data.get('rerank')
            rerank_top_n = data.get('rerank_top_n')
            format_type = data.get('format', 'json')
            
            # 执行搜索
            rag_engine = get_rag_engine()
            result = rag_engine.search(
                query=query,
                k=k,
                filter=filter,
                rerank=rerank,
                rerank_top_n=rerank_top_n,
                format_type='json'  # 强制使用JSON格式
            )
            
            # 格式化为文本（如果需要）
            if format_type.lower() == 'text':
                return ResultFormatter.search_json_to_text(result), 200, {'Content-Type': 'text/plain; charset=utf-8'}
                
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return jsonify({"error": True, "message": f"搜索失败: {str(e)}"}), 500
    
    @api_v1.route('/query', methods=['POST'])
    def query():
        """查询接口"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": True, "message": "请求体为空或非JSON格式"}), 400
                
            # 验证必须字段
            if 'query' not in data:
                return jsonify({"error": True, "message": "缺少必要字段 'query'"}), 400
                
            # 提取参数
            query = data['query']
            k = data.get('k', 5)
            filter = data.get('filter')
            format_type = data.get('format', 'json')
            llm_args = data.get('llm_args', {})
            rerank = data.get('rerank')
            rerank_top_n = data.get('rerank_top_n')
            stream = data.get('stream', False)
            
            # 检查是否需要流式生成
            if stream:
                rag_engine = get_rag_engine()
                
                # 流式查询
                def generate():
                    try:
                        for text_chunk in rag_engine.query(
                            query=query,
                            k=k,
                            filter=filter,
                            rerank=rerank,
                            rerank_top_n=rerank_top_n,
                            llm_args=llm_args,
                            stream=True
                        ):
                            yield f"data: {json.dumps({'text': text_chunk})}\n\n"
                    except Exception as e:
                        logger.error(f"流式查询失败: {e}")
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                    finally:
                        yield "data: [DONE]\n\n"
                        
                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'X-Accel-Buffering': 'no'
                    }
                )
            else:
                # 执行查询（非流式）
                rag_engine = get_rag_engine()
                result = rag_engine.query(
                    query=query,
                    k=k,
                    filter=filter,
                    rerank=rerank,
                    rerank_top_n=rerank_top_n,
                    format_type='json',  # 强制使用JSON格式
                    llm_args=llm_args,
                    stream=False
                )
                
                # 格式化为文本（如果需要）
                if format_type.lower() == 'text':
                    return ResultFormatter.json_to_text(result), 200, {'Content-Type': 'text/plain; charset=utf-8'}
                    
                return jsonify(result)
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return jsonify({"error": True, "message": f"查询失败: {str(e)}"}), 500
    
    # 模型和服务信息路由
    @api_v1.route('/info', methods=['GET'])
    def get_info():
        """获取服务信息接口"""
        try:
            rag_engine = get_rag_engine()
            
            # 获取向量存储信息
            vector_store_info = {
                "type": rag_engine.vector_store.__class__.__name__,
                "count": rag_engine.vector_store.count()
            }
            
            # 获取LLM信息
            llm_info = None
            if rag_engine.llm_client:
                llm_info = {
                    "provider": rag_engine.llm_client.__class__.__name__,
                    "model": rag_engine.llm_client.model_name,
                    "available": rag_engine.llm_client.is_available()
                }
                
            # 获取重排序器信息
            reranker_info = None
            if rag_engine.reranker:
                reranker_info = {
                    "type": rag_engine.reranker.__class__.__name__,
                    "model": rag_engine.reranker.model_name
                }
                
            # 构建响应
            info = {
                "service": SERVICE_NAME,
                "version": VERSION,
                "vector_store": vector_store_info,
                "llm": llm_info,
                "reranker": reranker_info,
                "embedding_model": rag_engine.embedding_manager.model_loader.model_name
            }
            
            return jsonify(info)
            
        except Exception as e:
            logger.error(f"获取服务信息失败: {e}")
            return jsonify({"error": True, "message": f"获取服务信息失败: {str(e)}"}), 500
    
    # 注册蓝图
    app.register_blueprint(api_v1)

# 数据模型定义
class SearchRequest(BaseModel):
    query: str
    search_types: Optional[List[str]] = ["semantic", "keyword", "knowledge_graph"]
    filters: Optional[Dict[str, List[str]]] = None
    top_k: Optional[int] = 10

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]

# 创建路由
router = APIRouter(prefix="/rag", tags=["RAG Service"])

@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    执行TCM知识搜索
    
    参数:
    - query: 搜索查询
    - search_types: 搜索类型列表，可包含 "semantic"、"keyword"、"knowledge_graph"
    - filters: 过滤条件
    - top_k: 返回结果数量
    """
    try:
        # 从依赖注入获取retriever实例
        from api.dependencies import get_retriever
        retriever = get_retriever()
        
        # 执行搜索
        results = await retriever.search(
            query=request.query,
            search_types=request.search_types,
            filters=request.filters,
            top_k=request.top_k
        )
        
        # 构建响应
        return SearchResponse(
            results=results,
            metadata={
                "total": len(results),
                "search_types": request.search_types,
                "filters_applied": request.filters is not None
            }
        )
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/term/{term}", response_model=Dict[str, Any])
async def get_term_info(term: str):
    """
    获取中医术语信息
    
    参数:
    - term: 中医术语
    """
    try:
        from api.dependencies import get_dictionary
        dictionary = get_dictionary()
        
        info = dictionary.get_term_info(term)
        if info is None:
            raise HTTPException(
                status_code=404,
                detail=f"Term '{term}' not found"
            )
            
        return info
        
    except Exception as e:
        logger.error(f"Get term info error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get term info: {str(e)}"
        )

@router.get("/extract_terms")
async def extract_terms(text: str = Query(..., description="要分析的文本")):
    """
    从文本中提取中医术语
    
    参数:
    - text: 要分析的文本
    """
    try:
        from api.dependencies import get_dictionary
        dictionary = get_dictionary()
        
        terms = dictionary.extract_terms(text)
        return {
            "terms": terms,
            "total": len(terms)
        }
        
    except Exception as e:
        logger.error(f"Extract terms error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract terms: {str(e)}"
        ) 