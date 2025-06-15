#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医体质API路由
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from .....model.health_data import TCMConstitutionType, TCMConstitutionData
from ....service.health_data_service import HealthDataService
from ..dependencies import get_health_data_service, get_current_user


router = APIRouter(tags=["中医体质"])


class TCMConstitutionResponse(BaseModel):
    """中医体质响应模型"""
    id: UUID
    user_id: UUID
    timestamp: datetime
    primary_type: str
    secondary_types: List[str]
    scores: Dict[str, float]
    analysis_basis: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_by: str
    created_at: datetime
    updated_at: datetime


class TCMConstitutionCreateRequest(BaseModel):
    """中医体质创建请求模型"""
    primary_type: TCMConstitutionType
    secondary_types: List[TCMConstitutionType] = Field(default_factory=list)
    scores: Dict[str, float]
    analysis_basis: Dict[str, Any]
    recommendations: Dict[str, Any]
    created_by: str = "ai"  # "ai", "tcm_doctor", "self_assessment"


@router.get("/constitution", response_model=TCMConstitutionResponse)
async def get_tcm_constitution(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    获取用户最新的中医体质数据
    """
    user_id = current_user["id"]
    
    constitution = await service.get_latest_tcm_constitution(user_id)
    
    if not constitution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到中医体质数据"
        )
    
    return TCMConstitutionResponse(
        id=constitution.id,
        user_id=constitution.user_id,
        timestamp=constitution.timestamp,
        primary_type=constitution.primary_type.value,
        secondary_types=[t.value for t in constitution.secondary_types],
        scores=constitution.scores,
        analysis_basis=constitution.analysis_basis,
        recommendations=constitution.recommendations,
        created_by=constitution.created_by,
        created_at=constitution.created_at,
        updated_at=constitution.updated_at
    )


@router.get("/constitution/history", response_model=List[TCMConstitutionResponse])
async def get_tcm_constitution_history(
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    获取用户的中医体质历史记录
    
    - **limit**: 返回记录限制
    """
    user_id = current_user["id"]
    
    async with service.session_factory() as session:
        repository = service.get_repository(session)
        constitutions = await repository.get_tcm_constitution_history(
            user_id=user_id,
            limit=limit
        )
    
    if not constitutions:
        return []
    
    from .....model.health_data import TCMConstitutionType
    
    results = []
    for constitution in constitutions:
        results.append(
            TCMConstitutionResponse(
                id=constitution.id,
                user_id=constitution.user_id,
                timestamp=constitution.timestamp,
                primary_type=constitution.primary_type,
                secondary_types=constitution.secondary_types,
                scores=constitution.scores,
                analysis_basis=constitution.analysis_basis,
                recommendations=constitution.recommendations,
                created_by=constitution.created_by,
                created_at=constitution.created_at,
                updated_at=constitution.updated_at
            )
        )
    
    return results


@router.post("/constitution", status_code=status.HTTP_201_CREATED)
async def create_tcm_constitution(
    request: TCMConstitutionCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    创建中医体质记录
    
    - **primary_type**: 主要体质类型
    - **secondary_types**: 次要体质类型列表
    - **scores**: 各体质类型得分
    - **analysis_basis**: 分析依据
    - **recommendations**: 调理建议
    - **created_by**: 创建来源
    """
    user_id = current_user["id"]
    
    # 创建中医体质数据对象
    constitution = TCMConstitutionData(
        user_id=user_id,
        timestamp=datetime.utcnow(),
        primary_type=request.primary_type,
        secondary_types=request.secondary_types,
        scores=request.scores,
        analysis_basis=request.analysis_basis,
        recommendations=request.recommendations,
        created_by=request.created_by
    )
    
    # 保存中医体质数据
    async with service.session_factory() as session:
        async with session.begin():
            repository = service.get_repository(session)
            record = await repository.save_tcm_constitution(constitution)
    
    return {"id": str(record.id), "message": "中医体质数据已成功保存"}


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_tcm_constitution(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HealthDataService = Depends(get_health_data_service)
):
    """
    分析用户的中医体质
    
    基于用户的健康数据和四诊数据，自动分析用户的中医体质
    """
    user_id = current_user["id"]
    
    try:
        # 获取分析服务
        tcm_analyzer = service.analytics_services.get("tcm_constitution")
        if not tcm_analyzer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="中医体质分析服务不可用"
            )
        
        # 获取用户健康数据
        async with service.session_factory() as session:
            repository = service.get_repository(session)
            
            # 获取相关的健康数据
            pulse_data = await repository.get_health_data(
                user_id=user_id,
                data_type="pulse",
                limit=5,
                sort_desc=True
            )
            
            tongue_data = await repository.get_health_data(
                user_id=user_id,
                data_type="tongue",
                limit=5,
                sort_desc=True
            )
            
            face_data = await repository.get_health_data(
                user_id=user_id,
                data_type="face",
                limit=5,
                sort_desc=True
            )
            
            voice_data = await repository.get_health_data(
                user_id=user_id,
                data_type="voice",
                limit=5,
                sort_desc=True
            )
            
            symptom_data = await repository.get_health_data(
                user_id=user_id,
                data_type="symptom",
                limit=20,
                sort_desc=True
            )
        
        # 分析体质
        analysis_result = await tcm_analyzer.analyze(
            user_id=user_id,
            pulse_data=pulse_data,
            tongue_data=tongue_data,
            face_data=face_data,
            voice_data=voice_data,
            symptom_data=symptom_data
        )
        
        # 保存体质结果
        constitution = TCMConstitutionData(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            primary_type=analysis_result["primary_type"],
            secondary_types=analysis_result["secondary_types"],
            scores=analysis_result["scores"],
            analysis_basis=analysis_result["analysis_basis"],
            recommendations=analysis_result["recommendations"],
            created_by="ai"
        )
        
        async with service.session_factory() as session:
            async with session.begin():
                repository = service.get_repository(session)
                record = await repository.save_tcm_constitution(constitution)
        
        return {
            "id": str(record.id),
            "primary_type": analysis_result["primary_type"].value,
            "secondary_types": [t.value for t in analysis_result["secondary_types"]],
            "message": "中医体质分析完成"
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"体质分析时发生错误: {str(e)}"
        ) 