"""API路由模块"""
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
