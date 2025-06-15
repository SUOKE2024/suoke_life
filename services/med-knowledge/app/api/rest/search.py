"""
搜索相关API路由
提供智能搜索和知识发现功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.exceptions import ValidationException, SearchException, InvalidQueryException
from app.models.requests import SearchRequest
from app.models.entities import SearchResponse
from app.services.knowledge_service import KnowledgeService
from app.api.rest.deps import get_knowledge_service
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/search", tags=["智能搜索"])


@router.get("/", response_model=SearchResponse, summary="知识库搜索")
async def search_knowledge(
    q: str = Query(..., min_length=1, max_length=200, description="搜索关键词"),
    entity_type: Optional[str] = Query(None, description="实体类型过滤"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    在知识库中搜索相关信息
    
    - **q**: 搜索关键词，支持中文和英文
    - **entity_type**: 实体类型过滤，可选值：constitution, symptom, acupoint, herb, syndrome, biomarker, western_disease, prevention_evidence, integrated_treatment, lifestyle_intervention
    - **limit**: 每页返回的记录数量，范围1-100
    - **offset**: 分页偏移量，从0开始
    
    支持的搜索功能：
    - 模糊匹配：根据名称、描述等字段进行模糊搜索
    - 分类过滤：按实体类型筛选搜索结果
    - 相关性排序：根据匹配度对结果进行排序
    """
    try:
        # 验证搜索参数
        request = SearchRequest(
            query=q,
            entity_type=entity_type,
            limit=limit,
            offset=offset
        )
        
        # 执行搜索
        result = await knowledge_service.search_knowledge(
            query=request.query,
            entity_type=request.entity_type,
            limit=request.limit,
            offset=request.offset
        )
        
        return result
        
    except ValidationException as e:
        logger.warning(f"搜索参数验证失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidQueryException as e:
        logger.warning(f"无效的搜索查询: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except SearchException as e:
        logger.error(f"搜索执行失败: {e}")
        raise HTTPException(status_code=500, detail="搜索服务暂时不可用")
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail="搜索失败")


@router.get("/suggestions", summary="搜索建议")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=100, description="搜索前缀"),
    limit: int = Query(10, ge=1, le=20, description="建议数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取搜索建议和自动补全
    
    - **q**: 搜索前缀
    - **limit**: 返回的建议数量，范围1-20
    
    返回格式：
    ```json
    {
        "suggestions": [
            {
                "text": "建议文本",
                "type": "实体类型",
                "count": "匹配数量"
            }
        ]
    }
    ```
    """
    try:
        if len(q.strip()) < 1:
            raise ValidationException("搜索前缀不能为空")
        
        # 这里可以实现搜索建议逻辑
        # 暂时返回基础搜索结果作为建议
        search_result = await knowledge_service.search_knowledge(
            query=q.strip(),
            entity_type=None,
            limit=limit,
            offset=0
        )
        
        # 转换为建议格式
        suggestions = []
        for item in search_result.data:
            suggestions.append({
                "text": item.get("name", ""),
                "type": item.get("type", ""),
                "count": 1
            })
        
        return {"suggestions": suggestions}
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取搜索建议失败: {e}")
        raise HTTPException(status_code=500, detail="获取搜索建议失败")


@router.get("/popular", summary="热门搜索")
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取热门搜索关键词
    
    - **limit**: 返回的热门搜索数量，范围1-50
    
    返回格式：
    ```json
    {
        "popular_searches": [
            {
                "keyword": "关键词",
                "count": "搜索次数",
                "trend": "趋势变化"
            }
        ]
    }
    ```
    """
    try:
        # 这里可以实现热门搜索统计逻辑
        # 暂时返回预定义的热门搜索
        popular_searches = [
            {"keyword": "气虚体质", "count": 1250, "trend": "up"},
            {"keyword": "湿热体质", "count": 980, "trend": "stable"},
            {"keyword": "血瘀体质", "count": 856, "trend": "up"},
            {"keyword": "阴虚体质", "count": 742, "trend": "down"},
            {"keyword": "痰湿体质", "count": 698, "trend": "stable"},
            {"keyword": "阳虚体质", "count": 634, "trend": "up"},
            {"keyword": "气郁体质", "count": 567, "trend": "stable"},
            {"keyword": "特禀体质", "count": 423, "trend": "down"},
            {"keyword": "平和体质", "count": 389, "trend": "stable"},
        ]
        
        return {"popular_searches": popular_searches[:limit]}
        
    except Exception as e:
        logger.error(f"获取热门搜索失败: {e}")
        raise HTTPException(status_code=500, detail="获取热门搜索失败") 