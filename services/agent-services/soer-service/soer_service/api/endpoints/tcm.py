"""
中医功能API端点

提供中医相关功能的HTTP接口，主要用于集成其他中医微服务
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.auth import get_current_user
from ...services.tcm_service import TCMService
from ...models.tcm import TCMRecommendationResponse


router = APIRouter(prefix="/tcm", tags=["中医功能"])


class TCMConsultationRequest(BaseModel):
    """中医咨询请求"""
    symptoms: List[str] = []
    affected_areas: List[str] = []
    duration: Optional[str] = None
    severity: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class TCMSearchRequest(BaseModel):
    """中医知识搜索请求"""
    query: str
    category: str = "all"  # all, constitution, meridian, herbs


@router.get("/profile", summary="获取用户中医档案")
async def get_user_tcm_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """获取用户的中医档案信息"""
    try:
        user_id = current_user["user_id"]
        profile = await tcm_service.get_user_tcm_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="用户中医档案不存在")
        
        return {
            "success": True,
            "data": profile,
            "message": "成功获取用户中医档案"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取中医档案失败: {str(e)}")


@router.post("/consultation", response_model=TCMRecommendationResponse, summary="中医咨询")
async def tcm_consultation(
    request: TCMConsultationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """提供中医咨询服务，获取个性化建议"""
    try:
        user_id = current_user["user_id"]
        
        # 获取个性化中医建议
        recommendations = await tcm_service.get_personalized_tcm_advice(
            user_id=user_id,
            symptoms=request.symptoms,
            context=request.context
        )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"中医咨询失败: {str(e)}")


@router.get("/insights", summary="获取中医健康洞察")
async def get_tcm_health_insights(
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """获取用户的中医健康洞察分析"""
    try:
        user_id = current_user["user_id"]
        insights = await tcm_service.get_tcm_health_insights(user_id)
        
        return {
            "success": True,
            "data": insights,
            "message": "成功获取中医健康洞察"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取健康洞察失败: {str(e)}")


@router.post("/search", summary="搜索中医知识")
async def search_tcm_knowledge(
    request: TCMSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """搜索中医相关知识，返回个性化结果"""
    try:
        user_id = current_user["user_id"]
        results = await tcm_service.search_tcm_knowledge_for_user(user_id, request.query)
        
        return {
            "success": True,
            "data": {
                "query": request.query,
                "results": results,
                "total": len(results)
            },
            "message": "搜索完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/daily-guidance", summary="获取每日中医养生指导")
async def get_daily_tcm_guidance(
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """获取基于用户体质的每日养生指导"""
    try:
        user_id = current_user["user_id"]
        guidance = await tcm_service.get_daily_tcm_guidance(user_id)
        
        return {
            "success": True,
            "data": guidance,
            "message": "成功获取每日养生指导"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取每日指导失败: {str(e)}")


@router.get("/constitution", summary="获取用户体质信息")
async def get_user_constitution(
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """获取用户的中医体质信息"""
    try:
        user_id = current_user["user_id"]
        
        # 通过中医服务客户端获取体质信息
        constitution_data = await tcm_service.tcm_client.get_user_constitution(user_id)
        
        if not constitution_data:
            return {
                "success": True,
                "data": None,
                "message": "用户暂无体质评估记录，建议进行体质评估"
            }
        
        return {
            "success": True,
            "data": constitution_data,
            "message": "成功获取用户体质信息"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取体质信息失败: {str(e)}")


@router.get("/meridian/analysis", summary="获取经络分析")
async def get_meridian_analysis(
    symptoms: List[str] = Query(..., description="症状列表"),
    affected_areas: List[str] = Query(default=[], description="受影响区域"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """根据症状获取经络分析"""
    try:
        analysis = await tcm_service.tcm_client.get_meridian_analysis(symptoms, affected_areas)
        
        return {
            "success": True,
            "data": analysis,
            "message": "成功获取经络分析"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"经络分析失败: {str(e)}")


@router.get("/acupuncture/points", summary="获取针灸穴位建议")
async def get_acupuncture_points(
    condition: str = Query(..., description="症状或疾病"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """根据症状获取针灸穴位建议"""
    try:
        user_id = current_user["user_id"]
        
        # 获取用户体质信息
        tcm_profile = await tcm_service.get_user_tcm_profile(user_id)
        constitution_type = None
        if tcm_profile.get("constitution"):
            constitution_type = tcm_profile["constitution"].get("primary_constitution")
        
        # 获取穴位建议
        points = await tcm_service.tcm_client.get_acupuncture_points(condition, constitution_type)
        
        return {
            "success": True,
            "data": {
                "condition": condition,
                "constitution_type": constitution_type,
                "points": points
            },
            "message": "成功获取穴位建议"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取穴位建议失败: {str(e)}")


@router.get("/herbs/recommendations", summary="获取中药建议")
async def get_herbal_recommendations(
    symptoms: List[str] = Query(..., description="症状列表"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """根据症状和体质获取中药建议"""
    try:
        user_id = current_user["user_id"]
        
        # 获取用户体质信息
        tcm_profile = await tcm_service.get_user_tcm_profile(user_id)
        constitution_type = None
        if tcm_profile.get("constitution"):
            constitution_type = tcm_profile["constitution"].get("primary_constitution")
        
        # 获取中药建议
        recommendations = await tcm_service.tcm_client.get_herbal_recommendations(
            symptoms, constitution_type
        )
        
        return {
            "success": True,
            "data": {
                "symptoms": symptoms,
                "constitution_type": constitution_type,
                "recommendations": recommendations
            },
            "message": "成功获取中药建议"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取中药建议失败: {str(e)}")


@router.get("/seasonal/guidance", summary="获取时令养生指导")
async def get_seasonal_guidance(
    season: Optional[str] = Query(default=None, description="季节 (spring/summer/autumn/winter)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """获取时令养生指导"""
    try:
        user_id = current_user["user_id"]
        
        # 获取用户体质信息
        tcm_profile = await tcm_service.get_user_tcm_profile(user_id)
        constitution_type = "平和质"  # 默认体质
        if tcm_profile.get("constitution"):
            constitution_type = tcm_profile["constitution"].get("primary_constitution", "平和质")
        
        # 获取时令指导
        guidance = await tcm_service.tcm_client.get_seasonal_guidance(constitution_type, season)
        
        return {
            "success": True,
            "data": {
                "constitution_type": constitution_type,
                "season": season,
                "guidance": guidance
            },
            "message": "成功获取时令养生指导"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时令指导失败: {str(e)}")


@router.get("/health-check", summary="中医服务健康检查")
async def tcm_health_check(
    tcm_service: TCMService = Depends(lambda: TCMService())
):
    """检查中医相关服务的健康状态"""
    try:
        status = await tcm_service.health_check()
        return {
            "success": True,
            "data": status,
            "message": "健康检查完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")