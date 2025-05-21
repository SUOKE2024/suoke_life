from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional, Dict, Any

from app.core.logger import get_logger
from app.models.entities import (
    Constitution, ConstitutionListResponse, Symptom, SymptomListResponse,
    Acupoint, AcupointListResponse, Herb, HerbListResponse,
    Syndrome, SyndromeListResponse, SearchResponse, SyndromePathwaysResponse,
    RecommendationListResponse, ErrorResponse, Biomarker, BiomarkerListResponse,
    WesternDisease, WesternDiseaseListResponse, PreventionEvidence, PreventionEvidenceListResponse,
    IntegratedTreatment, IntegratedTreatmentListResponse, LifestyleIntervention,
    LifestyleInterventionListResponse
)
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.api.rest.deps import get_knowledge_service, get_knowledge_graph_service
from pydantic import BaseModel

logger = get_logger()

router = APIRouter(prefix="/api/v1")

@router.get(
    "/health",
    summary="健康检查",
    description="检查服务是否正常运行",
    tags=["系统"]
)
async def health_check():
    return {"status": "ok", "service": "med-knowledge"}

@router.get(
    "/stats",
    summary="获取知识图谱统计信息",
    description="返回当前知识图谱的节点和关系数量",
    tags=["系统"]
)
async def get_stats(
    service: KnowledgeService = Depends(get_knowledge_service)
):
    node_count = await service.get_node_count()
    relationship_count = await service.get_relationship_count()
    return {
        "node_count": node_count,
        "relationship_count": relationship_count
    }

@router.get(
    "/constitutions",
    response_model=ConstitutionListResponse,
    summary="获取体质列表",
    description="分页获取中医体质类型列表",
    tags=["体质"]
)
async def get_constitutions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_constitutions(limit, offset)

@router.get(
    "/constitutions/{constitution_id}",
    response_model=Constitution,
    summary="获取体质详情",
    description="根据ID获取特定体质的详细信息",
    tags=["体质"]
)
async def get_constitution(
    constitution_id: str = Path(..., description="体质ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    constitution = await service.get_constitution_by_id(constitution_id)
    if not constitution:
        raise HTTPException(status_code=404, detail=f"未找到ID为{constitution_id}的体质")
    return constitution

@router.get(
    "/symptoms",
    response_model=SymptomListResponse,
    summary="获取症状列表",
    description="分页获取中医症状列表",
    tags=["症状"]
)
async def get_symptoms(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_symptoms(limit, offset)

@router.get(
    "/symptoms/{symptom_id}",
    response_model=Symptom,
    summary="获取症状详情",
    description="根据ID获取特定症状的详细信息",
    tags=["症状"]
)
async def get_symptom(
    symptom_id: str = Path(..., description="症状ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    symptom = await service.get_symptom_by_id(symptom_id)
    if not symptom:
        raise HTTPException(status_code=404, detail=f"未找到ID为{symptom_id}的症状")
    return symptom

@router.get(
    "/acupoints",
    response_model=AcupointListResponse,
    summary="获取穴位列表",
    description="分页获取中医穴位列表",
    tags=["穴位"]
)
async def get_acupoints(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    meridian: Optional[str] = Query(None, description="按经络筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_acupoints(limit, offset, meridian)

@router.get(
    "/acupoints/{acupoint_id}",
    response_model=Acupoint,
    summary="获取穴位详情",
    description="根据ID获取特定穴位的详细信息",
    tags=["穴位"]
)
async def get_acupoint(
    acupoint_id: str = Path(..., description="穴位ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    acupoint = await service.get_acupoint_by_id(acupoint_id)
    if not acupoint:
        raise HTTPException(status_code=404, detail=f"未找到ID为{acupoint_id}的穴位")
    return acupoint

@router.get(
    "/herbs",
    response_model=HerbListResponse,
    summary="获取中药列表",
    description="分页获取中药列表",
    tags=["中药"]
)
async def get_herbs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="按分类筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_herbs(limit, offset, category)

@router.get(
    "/herbs/{herb_id}",
    response_model=Herb,
    summary="获取中药详情",
    description="根据ID获取特定中药的详细信息",
    tags=["中药"]
)
async def get_herb(
    herb_id: str = Path(..., description="中药ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    herb = await service.get_herb_by_id(herb_id)
    if not herb:
        raise HTTPException(status_code=404, detail=f"未找到ID为{herb_id}的中药")
    return herb

@router.get(
    "/syndromes",
    response_model=SyndromeListResponse,
    summary="获取证型列表",
    description="分页获取中医证型列表",
    tags=["证型"]
)
async def get_syndromes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_syndromes(limit, offset)

@router.get(
    "/syndromes/{syndrome_id}",
    response_model=Syndrome,
    summary="获取证型详情",
    description="根据ID获取特定证型的详细信息",
    tags=["证型"]
)
async def get_syndrome(
    syndrome_id: str = Path(..., description="证型ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    syndrome = await service.get_syndrome_by_id(syndrome_id)
    if not syndrome:
        raise HTTPException(status_code=404, detail=f"未找到ID为{syndrome_id}的证型")
    return syndrome

@router.get(
    "/syndromes/{syndrome_id}/pathways",
    response_model=SyndromePathwaysResponse,
    summary="获取证型辨证路径",
    description="获取特定证型的辨证路径",
    tags=["证型"]
)
async def get_syndrome_pathways(
    syndrome_id: str = Path(..., description="证型ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_syndrome_pathways(syndrome_id)

@router.get(
    "/search",
    response_model=SearchResponse,
    summary="知识库搜索",
    description="搜索知识库中的实体",
    tags=["搜索"]
)
async def search(
    q: str = Query(..., description="搜索关键词"),
    entity_type: Optional[str] = Query(None, description="实体类型筛选"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.search_knowledge(q, entity_type, limit, offset)

@router.get(
    "/recommendations",
    response_model=RecommendationListResponse,
    summary="获取推荐",
    description="获取体质相关的健康推荐",
    tags=["推荐"]
)
async def get_recommendations(
    constitution_id: str = Query(..., description="体质ID"),
    types: Optional[List[str]] = Query(None, description="推荐类型筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_recommendations_by_constitution(constitution_id, types)

@router.get(
    "/biomarkers",
    response_model=BiomarkerListResponse,
    summary="获取生物标志物列表",
    description="分页获取生物标志物列表",
    tags=["生物标志物"]
)
async def get_biomarkers(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="按分类筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_biomarkers(limit, offset, category)

@router.get(
    "/biomarkers/{biomarker_id}",
    response_model=Biomarker,
    summary="获取生物标志物详情",
    description="根据ID获取特定生物标志物的详细信息",
    tags=["生物标志物"]
)
async def get_biomarker(
    biomarker_id: str = Path(..., description="生物标志物ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    biomarker = await service.get_biomarker_by_id(biomarker_id)
    if not biomarker:
        raise HTTPException(status_code=404, detail=f"未找到ID为{biomarker_id}的生物标志物")
    return biomarker

@router.get(
    "/biomarkers/by-constitution/{constitution_id}",
    response_model=BiomarkerListResponse,
    summary="获取体质相关生物标志物",
    description="获取与特定体质相关的生物标志物",
    tags=["生物标志物"]
)
async def get_biomarkers_by_constitution(
    constitution_id: str = Path(..., description="体质ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_biomarkers_by_constitution(constitution_id, limit, offset)

@router.get(
    "/western-diseases",
    response_model=WesternDiseaseListResponse,
    summary="获取西医疾病列表",
    description="分页获取西医疾病列表",
    tags=["西医疾病"]
)
async def get_western_diseases(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_western_diseases(limit, offset)

@router.get(
    "/western-diseases/{disease_id}",
    response_model=WesternDisease,
    summary="获取西医疾病详情",
    description="根据ID获取特定西医疾病的详细信息",
    tags=["西医疾病"]
)
async def get_western_disease(
    disease_id: str = Path(..., description="疾病ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    disease = await service.get_western_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail=f"未找到ID为{disease_id}的疾病")
    return disease

@router.get(
    "/western-diseases/by-syndrome/{syndrome_id}",
    response_model=WesternDiseaseListResponse,
    summary="获取证型相关西医疾病",
    description="获取与特定证型相关的西医疾病",
    tags=["西医疾病"]
)
async def get_western_diseases_by_syndrome(
    syndrome_id: str = Path(..., description="证型ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_western_diseases_by_syndrome(syndrome_id, limit, offset)

@router.get(
    "/prevention-evidence",
    response_model=PreventionEvidenceListResponse,
    summary="获取预防医学证据列表",
    description="分页获取预防医学证据列表",
    tags=["预防医学"]
)
async def get_prevention_evidence(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="按分类筛选"),
    evidence_level: Optional[str] = Query(None, description="按证据级别筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_prevention_evidence(limit, offset, category, evidence_level)

@router.get(
    "/prevention-evidence/{evidence_id}",
    response_model=PreventionEvidence,
    summary="获取预防医学证据详情",
    description="根据ID获取特定预防医学证据的详细信息",
    tags=["预防医学"]
)
async def get_prevention_evidence_by_id(
    evidence_id: str = Path(..., description="证据ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    evidence = await service.get_prevention_evidence_by_id(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail=f"未找到ID为{evidence_id}的预防医学证据")
    return evidence

@router.get(
    "/integrated-treatments",
    response_model=IntegratedTreatmentListResponse,
    summary="获取中西医结合治疗方案列表",
    description="分页获取中西医结合治疗方案列表",
    tags=["中西医结合"]
)
async def get_integrated_treatments(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    target_condition: Optional[str] = Query(None, description="按目标状况筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_integrated_treatments(limit, offset, target_condition)

@router.get(
    "/integrated-treatments/{treatment_id}",
    response_model=IntegratedTreatment,
    summary="获取中西医结合治疗方案详情",
    description="根据ID获取特定中西医结合治疗方案的详细信息",
    tags=["中西医结合"]
)
async def get_integrated_treatment(
    treatment_id: str = Path(..., description="治疗方案ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    treatment = await service.get_integrated_treatment_by_id(treatment_id)
    if not treatment:
        raise HTTPException(status_code=404, detail=f"未找到ID为{treatment_id}的中西医结合治疗方案")
    return treatment

@router.get(
    "/lifestyle-interventions",
    response_model=LifestyleInterventionListResponse,
    summary="获取生活方式干预列表",
    description="分页获取生活方式干预列表",
    tags=["生活方式干预"]
)
async def get_lifestyle_interventions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="按分类筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_lifestyle_interventions(limit, offset, category)

@router.get(
    "/lifestyle-interventions/{intervention_id}",
    response_model=LifestyleIntervention,
    summary="获取生活方式干预详情",
    description="根据ID获取特定生活方式干预的详细信息",
    tags=["生活方式干预"]
)
async def get_lifestyle_intervention(
    intervention_id: str = Path(..., description="干预ID"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    intervention = await service.get_lifestyle_intervention_by_id(intervention_id)
    if not intervention:
        raise HTTPException(status_code=404, detail=f"未找到ID为{intervention_id}的生活方式干预")
    return intervention

@router.get(
    "/lifestyle-interventions/by-constitution/{constitution_id}",
    response_model=LifestyleInterventionListResponse,
    summary="获取体质相关生活方式干预",
    description="获取适合特定体质的生活方式干预",
    tags=["生活方式干预"]
)
async def get_lifestyle_interventions_by_constitution(
    constitution_id: str = Path(..., description="体质ID"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = Query(None, description="按分类筛选"),
    service: KnowledgeService = Depends(get_knowledge_service)
):
    return await service.get_lifestyle_interventions_by_constitution(constitution_id, limit, offset, category)

# 新增知识图谱API端点

class GraphStatisticsResponse(BaseModel):
    """知识图谱统计响应"""
    node_count: int
    relationship_count: int
    node_types: List[Dict[str, Any]]
    relationship_types: List[Dict[str, Any]]


class CypherQueryRequest(BaseModel):
    """Cypher查询请求"""
    query: str
    params: Optional[Dict[str, Any]] = None


@router.get("/v1/graph/statistics", response_model=GraphStatisticsResponse, tags=["知识图谱"])
async def get_graph_statistics(
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取知识图谱统计信息"""
    return await graph_service.get_graph_statistics()


@router.get("/v1/graph/visualization", tags=["知识图谱"])
async def get_graph_visualization(
    limit: int = Query(100, description="节点限制数量"),
    node_types: Optional[List[str]] = Query(None, description="节点类型过滤"),
    relationship_types: Optional[List[str]] = Query(None, description="关系类型过滤"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取知识图谱可视化数据"""
    return await graph_service.get_graph_visualization_data(
        limit, node_types, relationship_types
    )


@router.get("/v1/graph/paths", tags=["知识图谱"])
async def find_paths(
    start_node_id: str = Query(..., description="起始节点ID"),
    end_node_id: str = Query(..., description="终止节点ID"),
    max_depth: int = Query(4, description="最大深度"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """查找两个节点之间的路径"""
    return await graph_service.find_path_between_nodes(
        start_node_id, end_node_id, max_depth
    )


@router.get("/v1/graph/nodes/{node_id}/relationships", tags=["知识图谱"])
async def get_node_relationships(
    node_id: str = Path(..., description="节点ID"),
    direction: str = Query("both", description="关系方向: outgoing, incoming, both"),
    relationship_types: Optional[List[str]] = Query(None, description="关系类型过滤"),
    limit: int = Query(20, description="限制数量"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取节点的关系"""
    return await graph_service.get_node_relationships(
        node_id, direction, relationship_types, limit
    )


@router.post("/v1/graph/cypher", tags=["知识图谱"])
async def execute_cypher_query(
    request: CypherQueryRequest,
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """执行Cypher查询（高级用户）"""
    try:
        return await graph_service.execute_cypher_query(request.query, request.params)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/v1/graph/subgraph/{entity_type}/{entity_id}", tags=["知识图谱"])
async def get_knowledge_subgraph(
    entity_type: str = Path(..., description="实体类型"),
    entity_id: str = Path(..., description="实体ID"),
    depth: int = Query(2, description="探索深度"),
    max_nodes: int = Query(50, description="最大节点数"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取以特定实体为中心的知识子图"""
    return await graph_service.get_knowledge_subgraph(
        entity_type, entity_id, depth, max_nodes
    )


@router.get("/v1/graph/entities/{entity_type}/{entity_id}/neighbors", tags=["知识图谱"])
async def get_entity_neighbors(
    entity_type: str = Path(..., description="实体类型"),
    entity_id: str = Path(..., description="实体ID"),
    neighbor_types: Optional[List[str]] = Query(None, description="邻居类型过滤"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取实体相邻节点"""
    return await graph_service.get_entity_neighbors(
        entity_type, entity_id, neighbor_types
    )


@router.get("/v1/graph/entities/{entity_type}/{entity_id}/related/{target_type}", tags=["知识图谱"])
async def get_related_entities(
    entity_type: str = Path(..., description="实体类型"),
    entity_id: str = Path(..., description="实体ID"),
    target_type: str = Path(..., description="目标实体类型"),
    relationship_type: Optional[str] = Query(None, description="关系类型"),
    limit: int = Query(20, description="限制数量"),
    graph_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """获取相关实体"""
    return await graph_service.get_related_entities(
        entity_type, entity_id, target_type, relationship_type, limit
    ) 