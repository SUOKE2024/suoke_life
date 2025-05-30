"""
integration-service 业务路由
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ServiceResponse(BaseModel):
    message: str
    data: dict = {}

@router.get("/", response_model=ServiceResponse)
async def get_service_info():
    """获取服务信息"""
    return ServiceResponse(
        message="integration-service is running",
        data={"version": "1.0.0"}
    )
