from typing import Dict, List, Any, Optional, Union

"""
symptoms - 索克生活项目模块
"""

from app.api.rest.deps import get_knowledge_service
from app.core.exceptions import EntityNotFoundException, ValidationException
from app.core.logger import get_logger
from app.models.entities import Symptom, SymptomListResponse
from app.models.requests import SymptomListRequest
from app.services.knowledge_service import KnowledgeService
from fastapi import APIRouter, Depends, HTTPException, Query

"""
症状相关API路由
提供症状信息查询和分析功能
"""



logger = get_logger()
router = APIRouter(prefix = " / symptoms", tags = ["症状管理"])


@router.get(" / ", response_model = SymptomListResponse, summary = "获取症状列表")
async def get_symptoms(
    limit: int = Query(20, ge = 1, le = 100, description = "每页数量"),
    offset: int = Query(0, ge = 0, description = "偏移量"),
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
):
    """
    获取所有症状信息列表

    - * *limit * *: 每页返回的记录数量,范围1 - 100
    - * *offset * *: 分页偏移量,从0开始
    """
    try:
        request = SymptomListRequest(limit = limit, offset = offset)
        result = await knowledge_service.get_symptoms(limit = request.limit, offset = request.offset)
        return result

    except ValidationException as e:
        logger.warning(f"症状列表查询参数验证失败: {e}")
        raise HTTPException(status_code = 400, detail = str(e))
    except Exception as e:
        logger.error(f"获取症状列表失败: {e}")
        raise HTTPException(status_code = 500, detail = "获取症状列表失败")


@router.get(" / {symptom_id}", response_model = Symptom, summary = "获取症状详情")
async def get_symptom_by_id(
    symptom_id: str, knowledge_service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    根据ID获取特定症状的详细信息

    - * *symptom_id * *: 症状唯一标识符
    """
    try:
        symptom = await knowledge_service.get_symptom_by_id(symptom_id)
        if not symptom:
            raise EntityNotFoundException("症状", symptom_id)
        return symptom

    except EntityNotFoundException:
        raise HTTPException(status_code = 404, detail = f"症状 {symptom_id} 未找到")
    except Exception as e:
        logger.error(f"获取症状详情失败 symptom_id = {symptom_id}: {e}")
        raise HTTPException(status_code = 500, detail = "获取症状详情失败")
