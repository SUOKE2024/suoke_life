"""
医疗资源服务REST API处理器
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...internal.infrastructure.container import (
    get_database_manager,
    get_medical_resource_coordinator,
    get_scheduler_service,
    get_xiaoke_agent,
)
from ...internal.infrastructure.models import ResourceType

logger = logging.getLogger(__name__)

# 路由器
router = APIRouter()

# 请求/响应模型
class ResourceSearchRequest(BaseModel):
    """资源搜索请求"""
    query: str = Field(..., description="搜索关键词")
    resource_type: Optional[str] = Field(None, description="资源类型")
    location: Optional[str] = Field(None, description="位置")
    limit: int = Field(20, description="返回结果数量")

class ResourceRecommendationRequest(BaseModel):
    """资源推荐请求"""
    user_id: str = Field(..., description="用户ID")
    symptoms: List[str] = Field(..., description="症状列表")
    location: str = Field(..., description="用户位置")
    urgency: str = Field("normal", description="紧急程度")
    max_results: int = Field(10, description="最大返回结果数")

class ResourceSchedulingRequest(BaseModel):
    """资源调度请求"""
    user_id: str = Field(..., description="用户ID")
    resource_type: str = Field(..., description="资源类型")
    priority: int = Field(1, description="优先级")
    preferred_time: Optional[str] = Field(None, description="偏好时间")
    special_requirements: List[str] = Field(default_factory=list, description="特殊要求")

class ScheduleOptimizationRequest(BaseModel):
    """调度优化请求"""
    resource_ids: List[str] = Field(..., description="资源ID列表")
    optimization_date: str = Field(..., description="优化日期")
    optimization_weights: Dict[str, float] = Field(default_factory=dict, description="优化权重")

class AppointmentRequest(BaseModel):
    """预约请求"""
    user_id: str = Field(..., description="用户ID")
    resource_id: str = Field(..., description="资源ID")
    appointment_date: str = Field(..., description="预约日期")
    appointment_time: str = Field(..., description="预约时间")
    symptoms: List[str] = Field(default_factory=list, description="症状描述")
    special_requirements: Optional[str] = Field(None, description="特殊要求")

class HealthAssessmentRequest(BaseModel):
    """健康评估请求"""
    user_id: str = Field(..., description="用户ID")
    symptoms: List[str] = Field(..., description="症状列表")
    lifestyle_factors: Dict[str, Any] = Field(default_factory=dict, description="生活方式因素")
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
            "version": "2.0.0",
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
        status = agent.get_agent_status()
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"获取智能体状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/recommend")
async def recommend_resources(request: ResourceRecommendationRequest):
    """推荐医疗资源"""
    try:
        agent = await get_xiaoke_agent()
        
        # 转换紧急程度
        from ...internal.domain.models import UrgencyLevel
        urgency_map = {
            "low": UrgencyLevel.LOW,
            "normal": UrgencyLevel.NORMAL,
            "high": UrgencyLevel.HIGH,
            "emergency": UrgencyLevel.EMERGENCY
        }
        urgency = urgency_map.get(request.urgency, UrgencyLevel.NORMAL)
        
        recommendations = await agent.recommend_resources(
            user_id=request.user_id,
            symptoms=request.symptoms,
            location=request.location,
            urgency=urgency,
            max_results=request.max_results
        )
        
        return {
            "success": True,
            "data": {
                "user_id": request.user_id,
                "total": len(recommendations),
                "recommendations": [
                    {
                        "resource_type": rec.resource_type.value,
                        "resource_id": rec.resource_id,
                        "title": rec.title,
                        "description": rec.description,
                        "confidence_score": rec.confidence_score,
                        "reasoning": rec.reasoning,
                        "metadata": rec.metadata
                    }
                    for rec in recommendations
                ]
            }
        }
    except Exception as e:
        logger.error(f"资源推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule/optimize")
async def optimize_schedule(request: ScheduleOptimizationRequest):
    """优化资源调度"""
    try:
        agent = await get_xiaoke_agent()
        
        # 解析优化日期
        optimization_date = datetime.fromisoformat(request.optimization_date)
        
        result = await agent.optimize_schedule(
            resource_ids=request.resource_ids,
            optimization_date=optimization_date,
            optimization_weights=request.optimization_weights
        )
        
        return {
            "success": result.success,
            "data": {
                "message": result.message,
                "suggestions": result.suggestions,
                "expected_improvement": result.expected_improvement
            }
        }
    except Exception as e:
        logger.error(f"调度优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/schedule")
async def schedule_resource(request: ResourceSchedulingRequest):
    """调度资源"""
    try:
        scheduler = await get_scheduler_service()
        
        # 转换资源类型
        resource_type = ResourceType(request.resource_type)
        
        result = await scheduler.schedule_resource(
            user_id=request.user_id,
            resource_type=resource_type,
            priority=request.priority,
            preferred_time=request.preferred_time,
            special_requirements=request.special_requirements
        )
        
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"资源调度失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources/status")
async def get_resource_status(
    resource_type: Optional[str] = Query(None, description="资源类型"),
    location: Optional[str] = Query(None, description="位置")
):
    """获取资源状态"""
    try:
        scheduler = await get_scheduler_service()
        
        status = await scheduler.get_resource_status(
            resource_type=resource_type,
            location=location
        )
        
        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"获取资源状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedule/queue")
async def get_scheduling_queue():
    """获取调度队列"""
    try:
        scheduler = await get_scheduler_service()
        queue = await scheduler.get_scheduling_queue()
        
        return {"success": True, "data": queue}
    except Exception as e:
        logger.error(f"获取调度队列失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/appointments")
async def create_appointment(request: AppointmentRequest):
    """创建预约"""
    try:
        coordinator = await get_medical_resource_coordinator()
        
        appointment = await coordinator.create_appointment(
            user_id=request.user_id,
            resource_id=request.resource_id,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            symptoms=request.symptoms,
            special_requirements=request.special_requirements
        )
        
        return {"success": True, "data": appointment}
    except Exception as e:
        logger.error(f"创建预约失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/appointments/{user_id}")
async def get_user_appointments(
    user_id: str = Path(..., description="用户ID"),
    status: Optional[str] = Query(None, description="预约状态"),
    limit: int = Query(20, description="返回数量")
):
    """获取用户预约"""
    try:
        coordinator = await get_medical_resource_coordinator()
        
        appointments = await coordinator.get_user_appointments(
            user_id=user_id,
            status=status,
            limit=limit
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
        
        assessment = await coordinator.create_health_assessment(
            user_id=request.user_id,
            symptoms=request.symptoms,
            lifestyle_factors=request.lifestyle_factors,
            medical_history=request.medical_history,
            preferences=request.preferences
        )
        
        return {"success": True, "data": assessment}
    except Exception as e:
        logger.error(f"创建健康评估失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources")
async def search_resources(
    resource_type: Optional[str] = Query(None, description="资源类型"),
    location: Optional[str] = Query(None, description="位置"),
    available_only: bool = Query(True, description="仅显示可用资源"),
    limit: int = Query(20, description="返回数量")
):
    """搜索医疗资源"""
    try:
        coordinator = await get_medical_resource_coordinator()
        
        resources = await coordinator.search_resources(
            resource_type=resource_type,
            location=location,
            available_only=available_only,
            limit=limit
        )
        
        return {"success": True, "data": resources}
    except Exception as e:
        logger.error(f"搜索医疗资源失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_service_statistics():
    """获取服务统计"""
    try:
        coordinator = await get_medical_resource_coordinator()
        stats = await coordinator.get_service_statistics()
        
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"获取服务统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 异常处理
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.now().isoformat(),
            }
        },
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "内部服务器错误",
                "timestamp": datetime.now().isoformat(),
            }
        },
    )
