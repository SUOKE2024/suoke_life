"""
API路由模块
"""

import logging
from fastapi import APIRouter
from typing import Any

logger = logging.getLogger(__name__)

def create_api_router(med_knowledge=None, benchmark=None) -> APIRouter:
    """创建API路由器"""
    router = APIRouter()
    
    @router.get("/status")
    async def get_status():
        """获取服务状态"""
        return {
            "status": "running",
            "modules": {
                "med_knowledge": "available" if med_knowledge else "unavailable",
                "benchmark": "available" if benchmark else "unavailable"
            }
        }
    
    @router.get("/med-knowledge/info")
    async def get_med_knowledge_info():
        """获取医学知识信息"""
        if med_knowledge:
            return await med_knowledge.get_status()
        return {"error": "医学知识模块不可用"}
    
    @router.get("/benchmark/info")
    async def get_benchmark_info():
        """获取基准测试信息"""
        if benchmark:
            return await benchmark.get_status()
        return {"error": "基准测试模块不可用"}
    
    logger.info("API路由器创建完成")
    return router

__all__ = ["create_api_router"] 