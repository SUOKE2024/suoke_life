"""
routes - 索克生活项目模块
"""

from fastapi import APIRouter
from xiaoke_service.api.v1 import chat, health, knowledge

"""
API 路由模块

定义所有的 REST API 端点和路由。
"""



# 创建主路由器
api_router = APIRouter()

# 包含各个版本的路由
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])
api_router.include_router(chat.router, prefix="/chat", tags=["智能对话"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
