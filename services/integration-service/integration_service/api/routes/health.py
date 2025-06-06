"""
health - 索克生活项目模块
"""

from fastapi import APIRouter
from pydantic import BaseModel

"""
健康检查路由
"""


router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    message: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        message="Service is running"
    )
