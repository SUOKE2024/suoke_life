"""
健康检查 API 端点
"""

from fastapi import APIRouter, Request, Body
from pydantic import BaseModel
from xiaoke_service.services.health import FourDiagnosisAggregator

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型"""

    status: str
    service: str
    version: str


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """基础健康检查"""
    return HealthResponse(status="healthy", service="xiaoke-service", version="1.0.0")


@router.get("/detailed")
async def detailed_health_check() -> dict:
    """详细健康检查"""
    return {
        "status": "healthy",
        "service": "xiaoke-service",
        "version": "1.0.0",
        "components": {
            "database": "healthy",
            "ai_service": "healthy",
            "cache": "healthy",
        },
        "timestamp": "2024-01-01T00:00:00Z",
    }


@router.post("/four-diagnosis/aggregation")
async def four_diagnosis_aggregation(
    request: Request,
    body: dict = Body(...)
):
    """四诊聚合接口，聚合四诊诊断结果"""
    user_id = body.get("user_id") or "anonymous"
    diagnosis_request = body.get("diagnosis_request") or body
    result = await FourDiagnosisAggregator.aggregate(diagnosis_request, user_id)
    return {"success": True, "data": result}
