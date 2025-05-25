"""
知识图谱分析API路由
提供图谱可视化、路径分析、关系发现等功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import EntityNotFoundException, ValidationException, GraphException, PathNotFoundException
from app.models.requests import GraphVisualizationRequest, PathAnalysisRequest, RelationshipAnalysisRequest
from app.services.knowledge_service import KnowledgeService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.api.rest.deps import get_knowledge_service
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/graph", tags=["知识图谱分析"])


@router.get("/statistics", summary="图谱统计信息")
async def get_graph_statistics(
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取知识图谱的统计信息
    
    返回格式：
    ```json
    {
        "node_count": "节点总数",
        "relationship_count": "关系总数",
        "entity_types": {
            "constitution": "体质数量",
            "symptom": "症状数量",
            "herb": "中药数量",
            ...
        },
        "relationship_types": {
            "TREATS": "治疗关系数量",
            "CAUSES": "致病关系数量",
            ...
        }
    }
    ```
    """
    try:
        node_count = await knowledge_service.get_node_count()
        relationship_count = await knowledge_service.get_relationship_count()
        
        # 这里可以添加更详细的统计信息
        statistics = {
            "node_count": node_count,
            "relationship_count": relationship_count,
            "entity_types": {
                "constitution": 9,  # 九种体质
                "symptom": 500,     # 估算值
                "herb": 1000,       # 估算值
                "acupoint": 400,    # 估算值
                "syndrome": 200,    # 估算值
                "biomarker": 150,   # 估算值
                "western_disease": 300,  # 估算值
            },
            "relationship_types": {
                "TREATS": 2000,
                "CAUSES": 800,
                "PREVENTS": 600,
                "RELATED_TO": 1500,
                "INDICATES": 400,
                "BELONGS_TO": 300,
            }
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"获取图谱统计信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取图谱统计信息失败")


@router.get("/visualization", summary="图谱可视化数据")
async def get_graph_visualization(
    entity_type: Optional[str] = Query(None, description="实体类型过滤"),
    entity_id: Optional[str] = Query(None, description="中心实体ID"),
    depth: int = Query(2, ge=1, le=5, description="遍历深度"),
    max_nodes: int = Query(100, ge=10, le=500, description="最大节点数"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取知识图谱可视化数据
    
    - **entity_type**: 实体类型过滤
    - **entity_id**: 中心实体ID，如果指定则以该实体为中心展开
    - **depth**: 遍历深度，范围1-5
    - **max_nodes**: 最大节点数，范围10-500
    
    返回格式：
    ```json
    {
        "nodes": [
            {
                "id": "节点ID",
                "label": "节点标签",
                "type": "节点类型",
                "properties": {...}
            }
        ],
        "edges": [
            {
                "source": "源节点ID",
                "target": "目标节点ID",
                "type": "关系类型",
                "properties": {...}
            }
        ]
    }
    ```
    """
    try:
        request = GraphVisualizationRequest(
            entity_type=entity_type,
            entity_id=entity_id,
            depth=depth,
            max_nodes=max_nodes
        )
        
        # 这里应该调用图谱服务获取可视化数据
        # 暂时返回示例数据
        visualization_data = {
            "nodes": [
                {
                    "id": "constitution_1",
                    "label": "气虚体质",
                    "type": "constitution",
                    "properties": {
                        "name": "气虚体质",
                        "description": "元气不足，以疲乏、气短、自汗等气虚表现为主要特征"
                    }
                },
                {
                    "id": "symptom_1",
                    "label": "疲乏无力",
                    "type": "symptom",
                    "properties": {
                        "name": "疲乏无力",
                        "severity": "中等"
                    }
                }
            ],
            "edges": [
                {
                    "source": "constitution_1",
                    "target": "symptom_1",
                    "type": "MANIFESTS_AS",
                    "properties": {
                        "strength": 0.8,
                        "frequency": "常见"
                    }
                }
            ]
        }
        
        return visualization_data
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取图谱可视化数据失败: {e}")
        raise HTTPException(status_code=500, detail="获取图谱可视化数据失败")


@router.get("/path-analysis", summary="路径分析")
async def analyze_path(
    from_id: str = Query(..., description="起始节点ID"),
    to_id: str = Query(..., description="目标节点ID"),
    max_depth: int = Query(5, ge=1, le=10, description="最大搜索深度"),
    max_paths: int = Query(10, ge=1, le=50, description="最大路径数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    分析两个实体之间的关联路径
    
    - **from_id**: 起始节点ID
    - **to_id**: 目标节点ID
    - **max_depth**: 最大搜索深度，范围1-10
    - **max_paths**: 最大路径数量，范围1-50
    
    返回格式：
    ```json
    {
        "paths": [
            {
                "nodes": ["节点ID列表"],
                "relationships": ["关系类型列表"],
                "length": "路径长度",
                "strength": "关联强度"
            }
        ],
        "summary": {
            "total_paths": "总路径数",
            "shortest_length": "最短路径长度",
            "strongest_path": "最强关联路径"
        }
    }
    ```
    """
    try:
        request = PathAnalysisRequest(
            from_id=from_id,
            to_id=to_id,
            max_depth=max_depth,
            max_paths=max_paths
        )
        
        # 这里应该调用图谱服务进行路径分析
        # 暂时返回示例数据
        path_analysis = {
            "paths": [
                {
                    "nodes": [from_id, "intermediate_1", to_id],
                    "relationships": ["RELATED_TO", "TREATS"],
                    "length": 2,
                    "strength": 0.85
                }
            ],
            "summary": {
                "total_paths": 1,
                "shortest_length": 2,
                "strongest_path": 0
            }
        }
        
        return path_analysis
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PathNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except GraphException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"路径分析失败: {e}")
        raise HTTPException(status_code=500, detail="路径分析失败")


@router.get("/relationships/{node_id}", summary="关系分析")
async def analyze_relationships(
    node_id: str,
    relationship_types: Optional[str] = Query(None, description="关系类型过滤，多个用逗号分隔"),
    direction: str = Query("both", description="关系方向: in, out, both"),
    limit: int = Query(50, ge=1, le=200, description="返回数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    分析指定节点的关系网络
    
    - **node_id**: 节点ID
    - **relationship_types**: 关系类型过滤，多个用逗号分隔
    - **direction**: 关系方向，可选值：in（入边）, out（出边）, both（双向）
    - **limit**: 返回的关系数量，范围1-200
    
    返回格式：
    ```json
    {
        "node": {
            "id": "节点ID",
            "label": "节点标签",
            "type": "节点类型"
        },
        "relationships": [
            {
                "target_node": {...},
                "relationship_type": "关系类型",
                "direction": "关系方向",
                "properties": {...}
            }
        ],
        "statistics": {
            "total_relationships": "总关系数",
            "relationship_type_counts": {...}
        }
    }
    ```
    """
    try:
        # 解析关系类型
        type_list = None
        if relationship_types:
            type_list = [t.strip() for t in relationship_types.split(",") if t.strip()]
        
        request = RelationshipAnalysisRequest(
            node_id=node_id,
            relationship_types=type_list,
            direction=direction
        )
        
        # 这里应该调用图谱服务进行关系分析
        # 暂时返回示例数据
        relationship_analysis = {
            "node": {
                "id": node_id,
                "label": "示例节点",
                "type": "constitution"
            },
            "relationships": [
                {
                    "target_node": {
                        "id": "target_1",
                        "label": "相关症状",
                        "type": "symptom"
                    },
                    "relationship_type": "MANIFESTS_AS",
                    "direction": "out",
                    "properties": {
                        "strength": 0.9,
                        "frequency": "常见"
                    }
                }
            ],
            "statistics": {
                "total_relationships": 1,
                "relationship_type_counts": {
                    "MANIFESTS_AS": 1
                }
            }
        }
        
        return relationship_analysis
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"关系分析失败: {e}")
        raise HTTPException(status_code=500, detail="关系分析失败")


@router.get("/recommendations/{entity_id}", summary="基于图谱的推荐")
async def get_graph_recommendations(
    entity_id: str,
    recommendation_type: str = Query("similar", description="推荐类型: similar, related, complementary"),
    limit: int = Query(10, ge=1, le=50, description="推荐数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    基于知识图谱的智能推荐
    
    - **entity_id**: 实体ID
    - **recommendation_type**: 推荐类型
      - similar: 相似实体推荐
      - related: 相关实体推荐  
      - complementary: 互补实体推荐
    - **limit**: 推荐数量，范围1-50
    
    返回格式：
    ```json
    {
        "source_entity": {...},
        "recommendations": [
            {
                "entity": {...},
                "score": "推荐分数",
                "reason": "推荐理由",
                "relationship_path": [...]
            }
        ]
    }
    ```
    """
    try:
        if recommendation_type not in ["similar", "related", "complementary"]:
            raise ValidationException("无效的推荐类型")
        
        # 这里应该实现基于图谱的推荐算法
        # 暂时返回示例数据
        recommendations = {
            "source_entity": {
                "id": entity_id,
                "label": "源实体",
                "type": "constitution"
            },
            "recommendations": [
                {
                    "entity": {
                        "id": "rec_1",
                        "label": "推荐实体",
                        "type": "herb"
                    },
                    "score": 0.85,
                    "reason": "基于体质特征的中药推荐",
                    "relationship_path": ["SUITABLE_FOR"]
                }
            ]
        }
        
        return recommendations
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"图谱推荐失败: {e}")
        raise HTTPException(status_code=500, detail="图谱推荐失败") 