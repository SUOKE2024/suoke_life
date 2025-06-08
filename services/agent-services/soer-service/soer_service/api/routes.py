from typing import Dict, List, Any, Optional, Union

"""
routes - 索克生活项目模块
"""

from .endpoints import agent, health, lifestyle, nutrition
from fastapi import APIRouter, Request, Body
from soer_service.services.agent_service import FourDiagnosisAggregator

"""
API 路由模块

定义所有的 API 端点
"""



# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(nutrition.router, prefix = " / nutrition", tags = ["营养分析"])

api_router.include_router(health.router, prefix = " / health", tags = ["健康管理"])

api_router.include_router(lifestyle.router, prefix = " / lifestyle", tags = ["生活方式"])

api_router.include_router(agent.router, prefix = " / agent", tags = ["智能体交互"])

@api_router.post(" / four - diagnosis / aggregation")
async def four_diagnosis_aggregation(
    request: Request,
    body: dict = Body(...)
):
    """四诊聚合接口，聚合四诊诊断结果"""
    user_id = body.get("user_id") or "anonymous"
    diagnosis_request = body.get("diagnosis_request") or body
    result = await FourDiagnosisAggregator.aggregate(diagnosis_request, user_id)
    return {"success": True, "data": result}
