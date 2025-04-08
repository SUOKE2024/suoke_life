"""
专业领域检索路由
提供针对特定知识领域的检索服务
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from ...knowledge_graph.schema import NodeType
from ...knowledge_graph.client import get_knowledge_graph_client
from ...vector_db.client import get_vector_db_client
from ...retrievers.knowledge_retrievers import SpecializedKnowledgeRetriever
from ..models.retrieval import (
    RetrievalResponse,
    PrecisionMedicineQuery,
    MultimodalHealthQuery,
    EnvironmentalHealthQuery,
    MentalHealthQuery,
    TCMQuery
)

router = APIRouter(prefix="/specialized", tags=["Specialized Retrievers"])


@router.post("/precision-medicine", response_model=RetrievalResponse)
async def retrieve_precision_medicine(
    query: PrecisionMedicineQuery,
    kg_client = Depends(get_knowledge_graph_client),
    vector_client = Depends(get_vector_db_client)
):
    """
    精准医学知识检索服务
    
    根据用户查询和过滤条件检索精准医学相关知识
    """
    try:
        retriever = SpecializedKnowledgeRetriever(kg_client, vector_client)
        
        # 准备检索参数
        retrieval_params = {
            "domain": "precision_medicine",
            "node_types": [NodeType.PRECISION_MEDICINE],
            "limit": query.limit,
            "semantic_weight": 0.8
        }
        
        # 添加额外过滤条件
        if query.study_type:
            retrieval_params["study_type"] = query.study_type
        
        if query.confidence_level:
            retrieval_params["confidence_level"] = query.confidence_level
        
        if query.genes:
            retrieval_params["genes"] = query.genes
        
        if query.diseases:
            retrieval_params["diseases"] = query.diseases
        
        # 执行检索
        results = await retriever.retrieve(query.query, **retrieval_params)
        
        return {
            "results": results,
            "count": len(results),
            "query": query.query,
            "domain": "precision_medicine"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multimodal-health", response_model=RetrievalResponse)
async def retrieve_multimodal_health(
    query: MultimodalHealthQuery,
    kg_client = Depends(get_knowledge_graph_client),
    vector_client = Depends(get_vector_db_client)
):
    """
    多模态健康数据知识检索服务
    
    根据用户查询和过滤条件检索多模态健康数据相关知识
    """
    try:
        retriever = SpecializedKnowledgeRetriever(kg_client, vector_client)
        
        # 准备检索参数
        retrieval_params = {
            "domain": "multimodal_health",
            "node_types": [NodeType.MULTIMODAL_HEALTH],
            "limit": query.limit,
            "semantic_weight": 0.7
        }
        
        # 添加额外过滤条件
        if query.modality_type:
            retrieval_params["modality_type"] = query.modality_type
        
        if query.features:
            retrieval_params["features"] = query.features
        
        # 执行检索
        results = await retriever.retrieve(query.query, **retrieval_params)
        
        return {
            "results": results,
            "count": len(results),
            "query": query.query,
            "domain": "multimodal_health"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/environmental-health", response_model=RetrievalResponse)
async def retrieve_environmental_health(
    query: EnvironmentalHealthQuery,
    kg_client = Depends(get_knowledge_graph_client),
    vector_client = Depends(get_vector_db_client)
):
    """
    环境健康知识检索服务
    
    根据用户查询和过滤条件检索环境健康相关知识
    """
    try:
        retriever = SpecializedKnowledgeRetriever(kg_client, vector_client)
        
        # 准备检索参数
        retrieval_params = {
            "domain": "environmental_health",
            "node_types": [NodeType.ENVIRONMENTAL_HEALTH],
            "limit": query.limit,
            "semantic_weight": 0.7
        }
        
        # 添加额外过滤条件
        if query.factor_type:
            retrieval_params["factor_type"] = query.factor_type
        
        if query.exposure_routes:
            retrieval_params["exposure_routes"] = query.exposure_routes
        
        if query.temporal_pattern:
            retrieval_params["temporal_pattern"] = query.temporal_pattern
        
        if query.location:
            retrieval_params["location"] = query.location
        
        # 执行检索
        results = await retriever.retrieve(query.query, **retrieval_params)
        
        return {
            "results": results,
            "count": len(results),
            "query": query.query,
            "domain": "environmental_health"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mental-health", response_model=RetrievalResponse)
async def retrieve_mental_health(
    query: MentalHealthQuery,
    kg_client = Depends(get_knowledge_graph_client),
    vector_client = Depends(get_vector_db_client)
):
    """
    心理健康知识检索服务
    
    根据用户查询和过滤条件检索心理健康相关知识
    """
    try:
        retriever = SpecializedKnowledgeRetriever(kg_client, vector_client)
        
        # 准备检索参数
        retrieval_params = {
            "domain": "mental_health",
            "node_types": [NodeType.MENTAL_HEALTH],
            "limit": query.limit,
            "semantic_weight": 0.75
        }
        
        # 添加额外过滤条件
        if query.psychology_domain:
            retrieval_params["psychology_domain"] = query.psychology_domain
        
        if query.age_groups:
            retrieval_params["age_groups"] = query.age_groups
        
        if query.techniques:
            retrieval_params["techniques"] = query.techniques
        
        # 执行检索
        results = await retriever.retrieve(query.query, **retrieval_params)
        
        return {
            "results": results,
            "count": len(results),
            "query": query.query,
            "domain": "mental_health"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tcm", response_model=RetrievalResponse)
async def retrieve_tcm(
    query: TCMQuery,
    kg_client = Depends(get_knowledge_graph_client),
    vector_client = Depends(get_vector_db_client)
):
    """
    中医养生特色检索服务
    
    根据用户查询和过滤条件检索中医养生相关知识，支持按体质类型、节气、经典文献的检索
    """
    try:
        retriever = SpecializedKnowledgeRetriever(kg_client, vector_client)
        
        # 准备检索参数
        retrieval_params = {
            "domain": "tcm",
            "node_types": [NodeType.TCM_KNOWLEDGE],
            "limit": query.limit,
            "semantic_weight": 0.85  # 中医知识更重视语义匹配
        }
        
        # 添加额外过滤条件
        if query.constitution_type:
            retrieval_params["constitution_type"] = query.constitution_type
        
        if query.season:
            retrieval_params["season"] = query.season
        
        if query.source_type:
            retrieval_params["source_type"] = query.source_type
        
        if query.keywords:
            retrieval_params["keywords"] = query.keywords
        
        # 执行检索
        results = await retriever.retrieve(query.query, **retrieval_params)
        
        return {
            "results": results,
            "count": len(results),
            "query": query.query,
            "domain": "tcm"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))