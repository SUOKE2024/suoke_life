"""
constitutions - 索克生活项目模块
"""

from app.api.rest.deps import get_knowledge_service
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.core.logger import get_logger
from app.models.entities import (
from app.models.requests import ConstitutionListRequest
from app.services.knowledge_service import KnowledgeService
from fastapi import APIRouter, Depends, HTTPException, Query

"""
体质相关API路由
提供体质信息查询和推荐功能
"""


    Constitution,
    ConstitutionListResponse,
    RecommendationListResponse,
)

logger = get_logger()
router = APIRouter(prefix="/constitutions", tags=["体质管理"])


@router.get("/", response_model=ConstitutionListResponse, summary="获取体质列表")
async def get_constitutions(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    获取所有体质信息列表

    - **limit**: 每页返回的记录数量,范围1-100
    - **offset**: 分页偏移量,从0开始
    """
    try:
        request = ConstitutionListRequest(limit=limit, offset=offset)
        result = await knowledge_service.get_constitutions(
            limit=request.limit, offset=request.offset
        )
        return result

    except ValidationException as e:
        logger.warning(f"体质列表查询参数验证失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取体质列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取体质列表失败")


@router.get("/{constitution_id}", response_model=Constitution, summary="获取体质详情")
async def get_constitution_by_id(
    constitution_id: str, knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    根据ID获取特定体质的详细信息

    - **constitution_id**: 体质唯一标识符
    """
    try:
        constitution = await knowledge_service.get_constitution_by_id(constitution_id)
        if not constitution:
            raise EntityNotFoundException("体质", constitution_id)
        return constitution

    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail=f"体质 {constitution_id} 未找到")
    except Exception as e:
        logger.error(f"获取体质详情失败 constitution_id={constitution_id}: {e}")
        raise HTTPException(status_code=500, detail="获取体质详情失败")


@router.get(
    "/{constitution_id}/recommendations",
    response_model=RecommendationListResponse,
    summary="获取体质推荐",
)
async def get_constitution_recommendations(
    constitution_id: str,
    types: str | None = Query(None, description="推荐类型,多个用逗号分隔"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    获取特定体质的个性化推荐

    - **constitution_id**: 体质唯一标识符
    - **types**: 推荐类型过滤,可选值:diet,exercise,lifestyle,acupoint,herb
    """
    try:
        # 验证体质是否存在
        constitution = await knowledge_service.get_constitution_by_id(constitution_id)
        if not constitution:
            raise EntityNotFoundException("体质", constitution_id)

        # 解析推荐类型
        type_list = None
        if types:
            type_list = [t.strip() for t in types.split(",") if t.strip()]
            # 验证推荐类型
            allowed_types = ["diet", "exercise", "lifestyle", "acupoint", "herb"]
            for t in type_list:
                if t not in allowed_types:
                    raise ValidationException(f"无效的推荐类型: {t}")

        result = await knowledge_service.get_recommendations_by_constitution(
            constitution_id=constitution_id, types=type_list
        )
        return result

    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail=f"体质 {constitution_id} 未找到")
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取体质推荐失败 constitution_id={constitution_id}: {e}")
        raise HTTPException(status_code=500, detail="获取体质推荐失败")


@router.get(
    "/{constitution_id}/biomarkers",
    response_model=RecommendationListResponse,
    summary="获取体质相关生物标志物",
)
async def get_constitution_biomarkers(
    constitution_id: str,
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    获取与特定体质相关的生物标志物

    - **constitution_id**: 体质唯一标识符
    - **limit**: 每页返回的记录数量
    - **offset**: 分页偏移量
    """
    try:
        # 验证体质是否存在
        constitution = await knowledge_service.get_constitution_by_id(constitution_id)
        if not constitution:
            raise EntityNotFoundException("体质", constitution_id)

        result = await knowledge_service.get_biomarkers_by_constitution(
            constitution_id=constitution_id, limit=limit, offset=offset
        )
        return result

    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail=f"体质 {constitution_id} 未找到")
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取体质相关生物标志物失败 constitution_id={constitution_id}: {e}")
        raise HTTPException(status_code=500, detail="获取体质相关生物标志物失败")


@router.get(
    "/{constitution_id}/lifestyle-interventions",
    response_model=RecommendationListResponse,
    summary="获取体质生活方式干预",
)
async def get_constitution_lifestyle_interventions(
    constitution_id: str,
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    category: str | None = Query(None, description="干预分类过滤"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    获取适合特定体质的生活方式干预建议

    - **constitution_id**: 体质唯一标识符
    - **limit**: 每页返回的记录数量
    - **offset**: 分页偏移量
    - **category**: 干预分类过滤
    """
    try:
        # 验证体质是否存在
        constitution = await knowledge_service.get_constitution_by_id(constitution_id)
        if not constitution:
            raise EntityNotFoundException("体质", constitution_id)

        result = await knowledge_service.get_lifestyle_interventions_by_constitution(
            constitution_id=constitution_id, limit=limit, offset=offset, category=category
        )
        return result

    except EntityNotFoundException:
        raise HTTPException(status_code=404, detail=f"体质 {constitution_id} 未找到")
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取体质生活方式干预失败 constitution_id={constitution_id}: {e}")
        raise HTTPException(status_code=500, detail="获取体质生活方式干预失败")
