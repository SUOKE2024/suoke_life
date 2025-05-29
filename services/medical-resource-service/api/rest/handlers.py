"""
医疗资源服务REST API处理器
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...internal.infrastructure.container import (
    get_database_manager,
    get_food_service,
    get_medical_resource_coordinator,
    get_scheduler_service,
    get_tcm_service,
    get_wellness_service,
    get_xiaoke_agent,
)
from ...internal.infrastructure.models import ConstitutionType, ResourceType

logger = logging.getLogger(__name__)

# 路由器
router = APIRouter()


# 请求/响应模型
class SearchRequest(BaseModel):
    """搜索请求"""

    query: str = Field(..., description="搜索关键词")
    category: Optional[str] = Field(None, description="知识类别")
    constitution: Optional[str] = Field(None, description="体质类型")
    limit: int = Field(20, description="返回结果数量")


class TreatmentRecommendationRequest(BaseModel):
    """治疗推荐请求"""

    constitution_type: str = Field(..., description="体质类型")
    symptoms: List[str] = Field(..., description="症状列表")
    syndrome: Optional[str] = Field(None, description="证候")
    severity: Optional[str] = Field("moderate", description="严重程度")


class FoodRecommendationRequest(BaseModel):
    """食疗推荐请求"""

    constitution_type: str = Field(..., description="体质类型")
    season: Optional[str] = Field(None, description="季节")
    health_goals: List[str] = Field(default_factory=list, description="健康目标")
    dietary_restrictions: List[str] = Field(
        default_factory=list, description="饮食限制"
    )


class WellnessRecommendationRequest(BaseModel):
    """养生推荐请求"""

    constitution_type: str = Field(..., description="体质类型")
    wellness_type: Optional[str] = Field(None, description="养生类型")
    location_preference: Optional[str] = Field(None, description="地点偏好")
    duration: Optional[int] = Field(None, description="时长（天）")


class ResourceSchedulingRequest(BaseModel):
    """资源调度请求"""

    user_id: str = Field(..., description="用户ID")
    resource_type: str = Field(..., description="资源类型")
    constitution_type: str = Field(..., description="体质类型")
    priority: int = Field(1, description="优先级")
    preferred_time: Optional[str] = Field(None, description="偏好时间")
    special_requirements: List[str] = Field(
        default_factory=list, description="特殊要求"
    )


class AgentQueryRequest(BaseModel):
    """智能体查询请求"""

    user_id: str = Field(..., description="用户ID")
    query: str = Field(..., description="查询内容")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")


class AppointmentRequest(BaseModel):
    """预约请求"""

    user_id: str = Field(..., description="用户ID")
    resource_id: str = Field(..., description="资源ID")
    appointment_date: str = Field(..., description="预约日期")
    appointment_time: str = Field(..., description="预约时间")
    constitution_type: str = Field(..., description="体质类型")
    symptoms: List[str] = Field(default_factory=list, description="症状描述")
    special_requirements: Optional[str] = Field(None, description="特殊要求")


class HealthAssessmentRequest(BaseModel):
    """健康评估请求"""

    user_id: str = Field(..., description="用户ID")
    symptoms: List[str] = Field(..., description="症状列表")
    lifestyle_factors: Dict[str, Any] = Field(
        default_factory=dict, description="生活方式因素"
    )
    medical_history: Dict[str, Any] = Field(default_factory=dict, description="病史")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="偏好设置")


# API端点


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        db_manager = await get_database_manager()
        db_health = await db_manager.health_check()

        return {
            "status": "healthy",
            "service": "medical-resource-service",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "database": db_health,
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "medical-resource-service",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get("/agent/status")
async def get_agent_status():
    """获取智能体状态"""
    try:
        agent = await get_xiaoke_agent()
        status = await agent.get_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"获取智能体状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/query")
async def query_agent(request: AgentQueryRequest):
    """查询智能体"""
    try:
        agent = await get_xiaoke_agent()
        response = await agent.process_query(
            user_id=request.user_id, query=request.query, context=request.context
        )
        return {"success": True, "data": response}
    except Exception as e:
        logger.error(f"智能体查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tcm/search")
async def search_tcm_knowledge(request: SearchRequest):
    """搜索中医知识"""
    try:
        tcm_service = await get_tcm_service()

        # 转换参数
        constitution = None
        if request.constitution:
            try:
                constitution = ConstitutionType(request.constitution)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"无效的体质类型: {request.constitution}"
                )

        results = await tcm_service.search_knowledge(
            query=request.query, category=request.category, constitution=constitution
        )

        return {
            "success": True,
            "data": {
                "query": request.query,
                "total": len(results),
                "results": results[: request.limit],
            },
        }
    except Exception as e:
        logger.error(f"搜索中医知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tcm/formula/{formula_id}")
async def get_formula_details(formula_id: str = Path(..., description="方剂ID")):
    """获取方剂详情"""
    try:
        tcm_service = await get_tcm_service()
        details = await tcm_service.get_formula_details(formula_id)
        if not details:
            raise HTTPException(status_code=404, detail="方剂不存在")

        return {"success": True, "data": details}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取方剂详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tcm/herb/{herb_id}")
async def get_herb_details(
    herb_id: str = Path(..., description="中药ID"),
    tcm_service: TCMKnowledgeService = Depends(get_tcm_service),
):
    """获取中药详情"""
    try:
        details = await tcm_service.get_herb_details(herb_id)
        if not details:
            raise HTTPException(status_code=404, detail="中药不存在")

        return {"success": True, "data": details}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取中药详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tcm/acupoint/{acupoint_id}")
async def get_acupoint_details(
    acupoint_id: str = Path(..., description="穴位ID"),
    tcm_service: TCMKnowledgeService = Depends(get_tcm_service),
):
    """获取穴位详情"""
    try:
        details = await tcm_service.get_acupoint_details(acupoint_id)
        if not details:
            raise HTTPException(status_code=404, detail="穴位不存在")

        return {"success": True, "data": details}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取穴位详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tcm/recommend")
async def recommend_treatment(request: TreatmentRecommendationRequest):
    """推荐治疗方案"""
    try:
        tcm_service = await get_tcm_service()

        # 转换体质类型
        try:
            constitution = ConstitutionType(request.constitution_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"无效的体质类型: {request.constitution_type}"
            )

        recommendations = await tcm_service.recommend_treatment(
            constitution_type=constitution,
            symptoms=request.symptoms,
            syndrome=request.syndrome,
            severity=request.severity,
        )

        return {"success": True, "data": recommendations}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推荐治疗方案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tcm/statistics")
async def get_tcm_statistics(
    tcm_service: TCMKnowledgeService = Depends(get_tcm_service),
):
    """获取中医知识库统计信息"""
    try:
        stats = tcm_service.get_service_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/food/recommend")
async def recommend_food_therapy(request: FoodRecommendationRequest):
    """推荐食疗方案"""
    try:
        food_service = await get_food_service()

        # 转换体质类型
        try:
            constitution = ConstitutionType(request.constitution_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"无效的体质类型: {request.constitution_type}"
            )

        recommendations = await food_service.recommend_food_therapy(
            constitution_type=constitution,
            season=request.season,
            health_goals=request.health_goals,
            dietary_restrictions=request.dietary_restrictions,
        )

        return {"success": True, "data": recommendations}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推荐食疗方案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/food/seasonal")
async def get_seasonal_foods(
    season: str = Query(..., description="季节"),
    constitution: Optional[str] = Query(None, description="体质类型"),
    food_service: FoodAgricultureService = Depends(get_food_service),
):
    """获取季节性食材推荐"""
    try:
        constitution_type = None
        if constitution:
            try:
                constitution_type = ConstitutionType(constitution)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"无效的体质类型: {constitution}"
                )

        foods = await food_service.get_seasonal_foods(season, constitution_type)

        return {
            "success": True,
            "data": {"season": season, "constitution": constitution, "foods": foods},
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取季节性食材失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/food/nutrition/{food_id}")
async def get_nutrition_analysis(
    food_id: str = Path(..., description="食物ID"),
    food_service: FoodAgricultureService = Depends(get_food_service),
):
    """获取营养分析"""
    try:
        analysis = await food_service.get_nutrition_analysis(food_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="食物不存在")

        return {"success": True, "data": analysis}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取营养分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wellness/recommend")
async def recommend_wellness_tourism(request: WellnessRecommendationRequest):
    """推荐养生旅游"""
    try:
        wellness_service = await get_wellness_service()

        # 转换体质类型
        try:
            constitution = ConstitutionType(request.constitution_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"无效的体质类型: {request.constitution_type}"
            )

        recommendations = await wellness_service.recommend_wellness_tourism(
            constitution_type=constitution,
            wellness_type=request.wellness_type,
            location_preference=request.location_preference,
            duration=request.duration,
        )

        return {"success": True, "data": recommendations}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推荐养生旅游失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wellness/destinations")
async def get_wellness_destinations(
    wellness_type: Optional[str] = Query(None, description="养生类型"),
    location: Optional[str] = Query(None, description="地点"),
    wellness_service: WellnessTourismService = Depends(get_wellness_service),
):
    """获取养生目的地列表"""
    try:
        destinations = await wellness_service.search_destinations(
            wellness_type=wellness_type, location=location
        )

        return {
            "success": True,
            "data": {"total": len(destinations), "destinations": destinations},
        }
    except Exception as e:
        logger.error(f"获取养生目的地失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wellness/destination/{destination_id}")
async def get_destination_details(
    destination_id: str = Path(..., description="目的地ID"),
    wellness_service: WellnessTourismService = Depends(get_wellness_service),
):
    """获取养生目的地详情"""
    try:
        details = await wellness_service.get_destination_details(destination_id)
        if not details:
            raise HTTPException(status_code=404, detail="目的地不存在")

        return {"success": True, "data": details}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取目的地详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resource/schedule")
async def schedule_resource(request: ResourceSchedulingRequest):
    """调度资源"""
    try:
        scheduler = await get_scheduler_service()

        # 转换参数
        try:
            constitution = ConstitutionType(request.constitution_type)
            resource_type = ResourceType(request.resource_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"参数错误: {e}")

        result = await scheduler.schedule_resource(
            user_id=request.user_id,
            resource_type=resource_type,
            constitution_type=constitution,
            priority=request.priority,
            preferred_time=request.preferred_time,
            special_requirements=request.special_requirements,
        )

        return {"success": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"资源调度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource/status")
async def get_resource_status(
    resource_type: Optional[str] = Query(None, description="资源类型"),
    scheduler: ResourceScheduler = Depends(get_scheduler_service),
):
    """获取资源状态"""
    try:
        resource_type_enum = None
        if resource_type:
            try:
                resource_type_enum = ResourceType(resource_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"无效的资源类型: {resource_type}"
                )

        status = await scheduler.get_resource_status(resource_type_enum)

        return {"success": True, "data": status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取资源状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource/queue")
async def get_scheduling_queue(
    scheduler: ResourceScheduler = Depends(get_scheduler_service),
):
    """获取调度队列状态"""
    try:
        queue_status = await scheduler.get_queue_status()

        return {"success": True, "data": queue_status}
    except Exception as e:
        logger.error(f"获取调度队列失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/appointments")
async def create_appointment(request: AppointmentRequest):
    """创建预约"""
    try:
        coordinator = await get_medical_resource_coordinator()

        # 转换体质类型
        try:
            constitution = ConstitutionType(request.constitution_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"无效的体质类型: {request.constitution_type}"
            )

        appointment = await coordinator.create_appointment(
            user_id=request.user_id,
            resource_id=request.resource_id,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            constitution_type=constitution,
            symptoms=request.symptoms,
            special_requirements=request.special_requirements,
        )

        return {"success": True, "data": appointment}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建预约失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments/{user_id}")
async def get_user_appointments(
    user_id: str = Path(..., description="用户ID"),
    status: Optional[str] = Query(None, description="预约状态"),
    limit: int = Query(20, description="返回数量"),
):
    """获取用户预约"""
    try:
        coordinator = await get_medical_resource_coordinator()

        appointments = await coordinator.get_user_appointments(
            user_id=user_id, status=status, limit=limit
        )

        return {"success": True, "data": appointments}
    except Exception as e:
        logger.error(f"获取用户预约失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health/assessment")
async def create_health_assessment(request: HealthAssessmentRequest):
    """创建健康评估"""
    try:
        coordinator = await get_medical_resource_coordinator()

        assessment = await coordinator.create_comprehensive_health_plan(
            user_id=request.user_id,
            health_assessment={
                "symptoms": request.symptoms,
                "lifestyle_factors": request.lifestyle_factors,
                "medical_history": request.medical_history,
            },
            preferences=request.preferences,
        )

        return {"success": True, "data": assessment}
    except Exception as e:
        logger.error(f"创建健康评估失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def search_resources(
    resource_type: Optional[str] = Query(None, description="资源类型"),
    location: Optional[str] = Query(None, description="位置"),
    constitution: Optional[str] = Query(None, description="体质类型"),
    available_only: bool = Query(True, description="仅显示可用资源"),
    limit: int = Query(20, description="返回数量"),
):
    """搜索医疗资源"""
    try:
        coordinator = await get_medical_resource_coordinator()

        # 转换参数
        constitution_type = None
        if constitution:
            try:
                constitution_type = ConstitutionType(constitution)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"无效的体质类型: {constitution}"
                )

        resource_type_enum = None
        if resource_type:
            try:
                resource_type_enum = ResourceType(resource_type)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"无效的资源类型: {resource_type}"
                )

        resources = await coordinator.search_resources(
            resource_type=resource_type_enum,
            location=location,
            constitution_type=constitution_type,
            available_only=available_only,
            limit=limit,
        )

        return {"success": True, "data": resources}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"搜索医疗资源失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_service_statistics():
    """获取服务统计信息"""
    try:
        coordinator = await get_medical_resource_coordinator()
        statistics = await coordinator.get_service_statistics()

        return {"success": True, "data": statistics}
    except Exception as e:
        logger.error(f"获取服务统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 异常处理器
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.now().isoformat(),
            },
        },
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "内部服务器错误",
                "timestamp": datetime.now().isoformat(),
            },
        },
    )
