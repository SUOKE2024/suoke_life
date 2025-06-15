#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
REST API处理器
提供完整的RAG服务API接口
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger

from ..container import Container
from ..routing.intelligent_router import (
    IntelligentRouter, RoutingRequest, TaskType, 
    UrgencyLevel, ComplexityLevel, AgentType
)
from ..integration.api_gateway import APIGateway, ServiceType
from ..tcm.tcm_models import ConstitutionType, SyndromeType


# 请求模型
class RAGQueryRequest(BaseModel):
    """RAG查询请求"""
    query: str = Field(..., description="用户查询")
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    task_type: Optional[TaskType] = Field(None, description="任务类型")
    urgency: Optional[UrgencyLevel] = Field(None, description="紧急程度")
    complexity: Optional[ComplexityLevel] = Field(None, description="复杂程度")
    preferred_agent: Optional[AgentType] = Field(None, description="首选智能体")
    multimodal_data: List[Dict[str, Any]] = Field(default_factory=list, description="多模态数据")
    max_tokens: int = Field(default=1000, description="最大生成token数")
    temperature: float = Field(default=0.7, description="生成温度")
    stream: bool = Field(default=False, description="是否流式响应")


class TCMAnalysisRequest(BaseModel):
    """中医分析请求"""
    symptoms: List[str] = Field(..., description="症状列表")
    user_id: str = Field(..., description="用户ID")
    constitution_type: Optional[ConstitutionType] = Field(None, description="体质类型")
    medical_history: List[str] = Field(default_factory=list, description="病史")
    current_medications: List[str] = Field(default_factory=list, description="当前用药")
    lifestyle_factors: Dict[str, Any] = Field(default_factory=dict, description="生活方式因素")


class HerbRecommendationRequest(BaseModel):
    """中药推荐请求"""
    syndrome_type: SyndromeType = Field(..., description="证型")
    constitution_type: ConstitutionType = Field(..., description="体质类型")
    user_id: str = Field(..., description="用户ID")
    contraindications: List[str] = Field(default_factory=list, description="禁忌症")
    allergies: List[str] = Field(default_factory=list, description="过敏史")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    pregnancy_status: Optional[bool] = Field(None, description="是否怀孕")


class DocumentIndexRequest(BaseModel):
    """文档索引请求"""
    content: str = Field(..., description="文档内容")
    title: str = Field(..., description="文档标题")
    source: str = Field(..., description="文档来源")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    document_type: str = Field(default="general", description="文档类型")


class KnowledgeGraphQueryRequest(BaseModel):
    """知识图谱查询请求"""
    entity: str = Field(..., description="实体名称")
    relation_types: List[str] = Field(default_factory=list, description="关系类型")
    max_depth: int = Field(default=2, description="最大查询深度")
    limit: int = Field(default=50, description="结果限制")


# 响应模型
class RAGQueryResponse(BaseModel):
    """RAG查询响应"""
    request_id: str = Field(..., description="请求ID")
    answer: str = Field(..., description="回答")
    sources: List[Dict[str, Any]] = Field(..., description="来源文档")
    confidence: float = Field(..., description="置信度")
    reasoning_chain: List[str] = Field(default_factory=list, description="推理链")
    agent_info: Dict[str, Any] = Field(default_factory=dict, description="智能体信息")
    processing_time: float = Field(..., description="处理时间")
    follow_up_questions: List[str] = Field(default_factory=list, description="后续问题")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class TCMAnalysisResponse(BaseModel):
    """中医分析响应"""
    request_id: str = Field(..., description="请求ID")
    syndrome_analysis: Dict[str, Any] = Field(..., description="证型分析")
    constitution_assessment: Dict[str, Any] = Field(..., description="体质评估")
    treatment_principles: List[str] = Field(..., description="治疗原则")
    lifestyle_recommendations: List[str] = Field(..., description="生活建议")
    reasoning_chain: List[str] = Field(..., description="推理链")
    confidence: float = Field(..., description="置信度")


class HerbRecommendationResponse(BaseModel):
    """中药推荐响应"""
    request_id: str = Field(..., description="请求ID")
    recommended_formulas: List[Dict[str, Any]] = Field(..., description="推荐方剂")
    single_herbs: List[Dict[str, Any]] = Field(..., description="单味药")
    safety_warnings: List[str] = Field(default_factory=list, description="安全警告")
    usage_instructions: Dict[str, Any] = Field(..., description="用法指导")
    contraindications: List[str] = Field(default_factory=list, description="禁忌症")
    monitoring_advice: List[str] = Field(default_factory=list, description="监测建议")


class ServiceStatusResponse(BaseModel):
    """服务状态响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本")
    uptime: float = Field(..., description="运行时间")
    components: Dict[str, str] = Field(..., description="组件状态")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="统计信息")


def create_rest_handler(
    container: Container,
    intelligent_router: IntelligentRouter,
    api_gateway: APIGateway
) -> APIRouter:
    """
    创建REST API处理器
    
    Args:
        container: 依赖注入容器
        intelligent_router: 智能路由器
        api_gateway: API网关
        
    Returns:
        FastAPI路由器
    """
    router = APIRouter()
    
    # 依赖注入
    def get_container() -> Container:
        return container
    
    def get_router() -> IntelligentRouter:
        return intelligent_router
    
    def get_gateway() -> APIGateway:
        return api_gateway
    
    @router.post("/query", response_model=RAGQueryResponse)
    async def query_rag(
        request: RAGQueryRequest,
        container: Container = Depends(get_container),
        router: IntelligentRouter = Depends(get_router)
    ):
        """
        RAG查询接口
        
        Args:
            request: 查询请求
            container: 依赖注入容器
            router: 智能路由器
            
        Returns:
            查询响应
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到RAG查询请求: {request_id}")
            
            # 创建路由请求
            routing_request = RoutingRequest(
                request_id=request_id,
                user_id=request.user_id,
                query=request.query,
                task_type=request.task_type or TaskType.CONSULTATION,
                urgency=request.urgency or UrgencyLevel.MEDIUM,
                complexity=request.complexity or ComplexityLevel.MODERATE,
                context=request.context,
                multimodal_data=request.multimodal_data,
                timestamp=str(time.time())
            )
            
            # 路由和编排
            routing_decision, collaboration_plan = await router.route_and_orchestrate(routing_request)
            
            # 获取RAG服务
            rag_service = container.rag_service()
            
            # 执行查询
            result = await rag_service.query(
                query=request.query,
                user_id=request.user_id,
                context=request.context,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                routing_decision=routing_decision
            )
            
            processing_time = time.time() - start_time
            
            return RAGQueryResponse(
                request_id=request_id,
                answer=result.get("answer", ""),
                sources=result.get("sources", []),
                confidence=result.get("confidence", 0.0),
                reasoning_chain=result.get("reasoning_chain", []),
                agent_info={
                    "primary_agent": routing_decision.primary_agent.value,
                    "secondary_agents": [agent.value for agent in routing_decision.secondary_agents],
                    "collaboration_mode": routing_decision.collaboration_mode,
                    "confidence": routing_decision.confidence
                },
                processing_time=processing_time,
                follow_up_questions=result.get("follow_up_questions", []),
                metadata=result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
    
    @router.post("/query/stream")
    async def query_rag_stream(
        request: RAGQueryRequest,
        container: Container = Depends(get_container),
        router: IntelligentRouter = Depends(get_router)
    ):
        """
        流式RAG查询接口
        
        Args:
            request: 查询请求
            container: 依赖注入容器
            router: 智能路由器
            
        Returns:
            流式响应
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到流式RAG查询请求: {request_id}")
            
            # 创建路由请求
            routing_request = RoutingRequest(
                request_id=request_id,
                user_id=request.user_id,
                query=request.query,
                task_type=request.task_type or TaskType.CONSULTATION,
                urgency=request.urgency or UrgencyLevel.MEDIUM,
                complexity=request.complexity or ComplexityLevel.MODERATE,
                context=request.context,
                multimodal_data=request.multimodal_data,
                timestamp=str(time.time())
            )
            
            # 路由和编排
            routing_decision, collaboration_plan = await router.route_and_orchestrate(routing_request)
            
            # 获取RAG服务
            rag_service = container.rag_service()
            
            # 流式生成器
            async def generate_stream():
                async for chunk in rag_service.query_stream(
                    query=request.query,
                    user_id=request.user_id,
                    context=request.context,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    routing_decision=routing_decision
                ):
                    yield f"data: {chunk}\n\n"
                
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={"X-Request-ID": request_id}
            )
            
        except Exception as e:
            logger.error(f"流式RAG查询失败: {e}")
            raise HTTPException(status_code=500, detail=f"流式查询失败: {str(e)}")
    
    @router.post("/tcm/analysis", response_model=TCMAnalysisResponse)
    async def analyze_tcm(
        request: TCMAnalysisRequest,
        container: Container = Depends(get_container)
    ):
        """
        中医分析接口
        
        Args:
            request: 中医分析请求
            container: 依赖注入容器
            
        Returns:
            中医分析响应
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到中医分析请求: {request_id}")
            
            # 获取中医辨证分析器
            syndrome_analyzer = container.syndrome_analyzer()
            
            # 执行辨证分析
            analysis_result = await syndrome_analyzer.analyze_symptoms(
                symptoms=request.symptoms,
                constitution_type=request.constitution_type,
                medical_history=request.medical_history,
                lifestyle_factors=request.lifestyle_factors
            )
            
            return TCMAnalysisResponse(
                request_id=request_id,
                syndrome_analysis=analysis_result.get("syndrome_analysis", {}),
                constitution_assessment=analysis_result.get("constitution_assessment", {}),
                treatment_principles=analysis_result.get("treatment_principles", []),
                lifestyle_recommendations=analysis_result.get("lifestyle_recommendations", []),
                reasoning_chain=analysis_result.get("reasoning_chain", []),
                confidence=analysis_result.get("confidence", 0.0)
            )
            
        except Exception as e:
            logger.error(f"中医分析失败: {e}")
            raise HTTPException(status_code=500, detail=f"中医分析失败: {str(e)}")
    
    @router.post("/tcm/herbs", response_model=HerbRecommendationResponse)
    async def recommend_herbs(
        request: HerbRecommendationRequest,
        container: Container = Depends(get_container)
    ):
        """
        中药推荐接口
        
        Args:
            request: 中药推荐请求
            container: 依赖注入容器
            
        Returns:
            中药推荐响应
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到中药推荐请求: {request_id}")
            
            # 获取中药推荐器
            herb_recommender = container.herb_recommender()
            
            # 创建患者档案
            patient_profile = {
                "user_id": request.user_id,
                "constitution_type": request.constitution_type,
                "contraindications": request.contraindications,
                "allergies": request.allergies,
                "age": request.age,
                "gender": request.gender,
                "pregnancy_status": request.pregnancy_status
            }
            
            # 执行中药推荐
            recommendation_result = await herb_recommender.recommend_herbs(
                syndrome_type=request.syndrome_type,
                patient_profile=patient_profile
            )
            
            return HerbRecommendationResponse(
                request_id=request_id,
                recommended_formulas=recommendation_result.get("formulas", []),
                single_herbs=recommendation_result.get("single_herbs", []),
                safety_warnings=recommendation_result.get("safety_warnings", []),
                usage_instructions=recommendation_result.get("usage_instructions", {}),
                contraindications=recommendation_result.get("contraindications", []),
                monitoring_advice=recommendation_result.get("monitoring_advice", [])
            )
            
        except Exception as e:
            logger.error(f"中药推荐失败: {e}")
            raise HTTPException(status_code=500, detail=f"中药推荐失败: {str(e)}")
    
    @router.post("/documents/index")
    async def index_document(
        request: DocumentIndexRequest,
        container: Container = Depends(get_container)
    ):
        """
        文档索引接口
        
        Args:
            request: 文档索引请求
            container: 依赖注入容器
            
        Returns:
            索引结果
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到文档索引请求: {request_id}")
            
            # 获取索引服务
            indexer = container.indexer()
            
            # 执行文档索引
            result = await indexer.index_document(
                content=request.content,
                title=request.title,
                source=request.source,
                metadata=request.metadata,
                document_type=request.document_type
            )
            
            return {
                "request_id": request_id,
                "status": "success",
                "document_id": result.get("document_id"),
                "chunks_count": result.get("chunks_count", 0),
                "processing_time": result.get("processing_time", 0.0)
            }
            
        except Exception as e:
            logger.error(f"文档索引失败: {e}")
            raise HTTPException(status_code=500, detail=f"文档索引失败: {str(e)}")
    
    @router.get("/documents/search")
    async def search_documents(
        query: str = Query(..., description="搜索查询"),
        limit: int = Query(default=10, description="结果限制"),
        threshold: float = Query(default=0.7, description="相似度阈值"),
        document_type: Optional[str] = Query(None, description="文档类型"),
        container: Container = Depends(get_container)
    ):
        """
        文档搜索接口
        
        Args:
            query: 搜索查询
            limit: 结果限制
            threshold: 相似度阈值
            document_type: 文档类型
            container: 依赖注入容器
            
        Returns:
            搜索结果
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到文档搜索请求: {request_id}")
            
            # 获取检索器
            retriever = container.retriever()
            
            # 执行文档搜索
            results = await retriever.search(
                query=query,
                limit=limit,
                threshold=threshold,
                filters={"document_type": document_type} if document_type else None
            )
            
            return {
                "request_id": request_id,
                "query": query,
                "results": results,
                "total_count": len(results)
            }
            
        except Exception as e:
            logger.error(f"文档搜索失败: {e}")
            raise HTTPException(status_code=500, detail=f"文档搜索失败: {str(e)}")
    
    @router.post("/knowledge-graph/query")
    async def query_knowledge_graph(
        request: KnowledgeGraphQueryRequest,
        container: Container = Depends(get_container)
    ):
        """
        知识图谱查询接口
        
        Args:
            request: 知识图谱查询请求
            container: 依赖注入容器
            
        Returns:
            查询结果
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"收到知识图谱查询请求: {request_id}")
            
            # 获取知识图谱增强器
            kg_enhancer = container.knowledge_graph_enhancer()
            
            # 执行知识图谱查询
            results = await kg_enhancer.query_entity_relations(
                entity=request.entity,
                relation_types=request.relation_types,
                max_depth=request.max_depth,
                limit=request.limit
            )
            
            return {
                "request_id": request_id,
                "entity": request.entity,
                "relations": results.get("relations", []),
                "subgraph": results.get("subgraph", {}),
                "statistics": results.get("statistics", {})
            }
            
        except Exception as e:
            logger.error(f"知识图谱查询失败: {e}")
            raise HTTPException(status_code=500, detail=f"知识图谱查询失败: {str(e)}")
    
    @router.get("/agents/{agent_name}/status")
    async def get_agent_status(
        agent_name: str = Path(..., description="智能体名称"),
        gateway: APIGateway = Depends(get_gateway)
    ):
        """
        获取智能体状态
        
        Args:
            agent_name: 智能体名称
            gateway: API网关
            
        Returns:
            智能体状态
        """
        try:
            logger.info(f"获取智能体状态: {agent_name}")
            
            # 通过网关查询智能体状态
            response = await gateway.send_agent_request(
                agent_name=agent_name,
                endpoint="/status",
                data={},
                method="GET"
            )
            
            if response.status_code == 200:
                return response.data
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.error or "获取智能体状态失败"
                )
                
        except Exception as e:
            logger.error(f"获取智能体状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取智能体状态失败: {str(e)}")
    
    @router.post("/agents/broadcast")
    async def broadcast_to_agents(
        endpoint: str = Body(..., description="端点路径"),
        data: Dict[str, Any] = Body(..., description="请求数据"),
        agents: Optional[List[str]] = Body(None, description="智能体列表"),
        gateway: APIGateway = Depends(get_gateway)
    ):
        """
        广播到智能体
        
        Args:
            endpoint: 端点路径
            data: 请求数据
            agents: 智能体列表
            gateway: API网关
            
        Returns:
            广播结果
        """
        request_id = str(uuid.uuid4())
        
        try:
            logger.info(f"广播到智能体: {request_id}")
            
            # 通过网关广播
            responses = await gateway.broadcast_to_agents(
                endpoint=endpoint,
                data=data,
                agents=agents
            )
            
            return {
                "request_id": request_id,
                "endpoint": endpoint,
                "responses": {
                    agent: {
                        "status_code": response.status_code,
                        "data": response.data,
                        "error": response.error,
                        "response_time": response.response_time
                    }
                    for agent, response in responses.items()
                }
            }
            
        except Exception as e:
            logger.error(f"广播到智能体失败: {e}")
            raise HTTPException(status_code=500, detail=f"广播失败: {str(e)}")
    
    @router.get("/status", response_model=ServiceStatusResponse)
    async def get_service_status(
        container: Container = Depends(get_container),
        router: IntelligentRouter = Depends(get_router),
        gateway: APIGateway = Depends(get_gateway)
    ):
        """
        获取服务状态
        
        Args:
            container: 依赖注入容器
            router: 智能路由器
            gateway: API网关
            
        Returns:
            服务状态
        """
        try:
            # 获取各组件状态
            components = {
                "container": "healthy" if container else "unhealthy",
                "router": "healthy" if router else "unhealthy",
                "gateway": "healthy" if gateway else "unhealthy"
            }
            
            # 获取统计信息
            statistics = {}
            
            if router:
                statistics["routing"] = await router.get_routing_statistics()
            
            if gateway:
                statistics["gateway"] = await gateway.get_gateway_statistics()
            
            return ServiceStatusResponse(
                status="healthy" if all(status == "healthy" for status in components.values()) else "degraded",
                version="1.2.0",
                uptime=time.time(),
                components=components,
                statistics=statistics
            )
            
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取服务状态失败: {str(e)}")
    
    @router.get("/metrics")
    async def get_metrics(
        container: Container = Depends(get_container)
    ):
        """
        获取服务指标
        
        Args:
            container: 依赖注入容器
            
        Returns:
            服务指标
        """
        try:
            metrics_collector = container.metrics_collector()
            
            if metrics_collector:
                return await metrics_collector.export_prometheus_metrics()
            else:
                return {"error": "指标收集器未初始化"}
                
        except Exception as e:
            logger.error(f"获取服务指标失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取服务指标失败: {str(e)}")
    
    return router 