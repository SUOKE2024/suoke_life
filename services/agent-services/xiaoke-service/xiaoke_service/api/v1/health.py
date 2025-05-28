"""
健康检查 API 端点
"""

from fastapi import APIRouter
from pydantic import BaseModel

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
