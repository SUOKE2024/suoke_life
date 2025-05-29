"""
API 路由模块

定义所有的 API 端点
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from laoke_service.core.agent import AgentMessage, LaoKeAgent
from laoke_service.core.exceptions import LaoKeServiceError

# 创建主路由器
api_router = APIRouter()


# 请求/响应模型
class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(description="用户消息")
    message_type: str = Field(default="general_chat", description="消息类型")
    user_id: str | None = Field(default=None, description="用户ID")
    context: dict[str, Any] | None = Field(default=None, description="上下文信息")
    metadata: dict[str, Any] | None = Field(default=None, description="元数据")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    success: bool = Field(description="是否成功")
    message: str = Field(description="响应消息")
    data: dict[str, Any] | None = Field(default=None, description="响应数据")
    suggestions: list[str] = Field(default_factory=list, description="建议")
    error_code: str | None = Field(default=None, description="错误代码")


class KnowledgeQueryRequest(BaseModel):
    """知识查询请求模型"""
    query: str = Field(description="查询关键词")
    category: str | None = Field(default=None, description="知识分类")
    difficulty: str | None = Field(default=None, description="难度级别")
    limit: int = Field(default=10, description="返回数量限制")


class LearningPlanRequest(BaseModel):
    """学习计划请求模型"""
    goal: str = Field(description="学习目标")
    current_level: str = Field(default="初级", description="当前水平")
    available_time: str = Field(default="30分钟/天", description="可用时间")
    interests: list[str] | None = Field(default=None, description="兴趣领域")


class CommunityPostRequest(BaseModel):
    """社区帖子请求模型"""
    title: str = Field(description="帖子标题")
    content: str = Field(description="帖子内容")
    category: str = Field(description="帖子分类")
    tags: list[str] | None = Field(default=None, description="标签")


# 依赖注入
async def get_agent(request: Request) -> LaoKeAgent:
    """获取智能体实例"""
    agent = getattr(request.app.state, 'agent', None)
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not available")
    return agent  # type: ignore[no-any-return]


# 聊天相关路由
@api_router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent: LaoKeAgent = Depends(get_agent)
) -> ChatResponse:
    """与老克智能体聊天"""
    try:
        # 创建智能体消息
        agent_message = AgentMessage(
            content=request.message,
            message_type=request.message_type,
            metadata=request.metadata or {}
        )

        # 处理消息
        response = await agent.process_message(
            message=agent_message,
            user_id=request.user_id,
            context=request.context
        )

        return ChatResponse(
            success=response.success,
            message=response.message,
            data=response.data,
            suggestions=response.suggestions,
            error_code=response.error_code
        )

    except LaoKeServiceError as e:
        return ChatResponse(
            success=False,
            message=e.message,
            error_code=e.error_code
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# 知识管理相关路由
@api_router.post("/knowledge/search", response_model=ChatResponse)
async def search_knowledge(
    request: KnowledgeQueryRequest,
    agent: LaoKeAgent = Depends(get_agent)
) -> ChatResponse:
    """搜索知识内容"""
    try:
        # 创建知识查询消息
        agent_message = AgentMessage(
            content=request.query,
            message_type="knowledge_query",
            metadata={
                "category": request.category,
                "difficulty": request.difficulty,
                "limit": request.limit
            }
        )

        response = await agent.process_message(agent_message)

        return ChatResponse(
            success=response.success,
            message=response.message,
            data=response.data,
            suggestions=response.suggestions,
            error_code=response.error_code
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@api_router.get("/knowledge/categories")
async def get_knowledge_categories(
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """获取知识分类"""
    try:
        # 这里应该从智能体获取实际的分类数据
        categories = {
            "中医基础理论": ["阴阳学说", "五行学说", "脏腑学说", "经络学说"],
            "中医诊断": ["望诊", "闻诊", "问诊", "切诊", "辨证论治"],
            "中药学": ["中药性味", "中药归经", "中药配伍", "方剂学"],
            "养生保健": ["四季养生", "体质养生", "饮食养生", "运动养生"],
            "疾病防治": ["常见病防治", "慢性病管理", "亚健康调理"]
        }

        return {
            "success": True,
            "data": {"categories": categories}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# 学习路径相关路由
@api_router.post("/learning/plan", response_model=ChatResponse)
async def create_learning_plan(
    request: LearningPlanRequest,
    agent: LaoKeAgent = Depends(get_agent)
) -> ChatResponse:
    """创建学习计划"""
    try:
        # 创建学习计划消息
        agent_message = AgentMessage(
            content=f"为我制定{request.goal}的学习计划",
            message_type="learning_plan",
            metadata={
                "requirements": {
                    "goal": request.goal,
                    "level": request.current_level,
                    "time": request.available_time,
                    "interests": request.interests or []
                }
            }
        )

        response = await agent.process_message(agent_message)

        return ChatResponse(
            success=response.success,
            message=response.message,
            data=response.data,
            suggestions=response.suggestions,
            error_code=response.error_code
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@api_router.get("/learning/paths")
async def get_learning_paths(
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """获取可用的学习路径"""
    try:
        # 这里应该从智能体获取实际的学习路径数据
        paths = [
            {
                "id": "tcm_basics",
                "name": "中医基础入门",
                "description": "适合零基础学习者的中医入门课程",
                "duration": "30天",
                "difficulty": "入门",
                "modules_count": 4
            },
            {
                "id": "constitution_health",
                "name": "体质养生",
                "description": "了解九种体质，学会个性化养生",
                "duration": "21天",
                "difficulty": "初级",
                "modules_count": 3
            },
            {
                "id": "food_therapy",
                "name": "食疗养生",
                "description": "掌握中医营养学和食疗方法",
                "duration": "28天",
                "difficulty": "中级",
                "modules_count": 4
            }
        ]

        return {
            "success": True,
            "data": {"learning_paths": paths}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# 社区相关路由
@api_router.get("/community/posts")
async def get_community_posts(
    category: str | None = None,
    limit: int = 10,
    offset: int = 0,
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """获取社区帖子"""
    try:
        # 创建社区浏览消息
        agent_message = AgentMessage(
            content="浏览社区内容",
            message_type="community_interaction",
            metadata={
                "action": "browse",
                "category": category,
                "limit": limit,
                "offset": offset
            }
        )

        response = await agent.process_message(agent_message)

        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@api_router.post("/community/posts")
async def create_community_post(
    request: CommunityPostRequest,
    user_id: str | None = None,
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """创建社区帖子"""
    try:
        # 创建社区发帖消息
        agent_message = AgentMessage(
            content=request.content,
            message_type="community_interaction",
            metadata={
                "action": "create_post",
                "title": request.title,
                "category": request.category,
                "tags": request.tags or []
            }
        )

        response = await agent.process_message(agent_message, user_id=user_id)

        return {
            "success": response.success,
            "data": response.data,
            "message": response.message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# 智能体状态相关路由
@api_router.get("/agent/status")
async def get_agent_status(
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """获取智能体状态"""
    try:
        status = await agent.get_agent_status()
        return {
            "success": True,
            "data": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@api_router.get("/agent/capabilities")
async def get_agent_capabilities(
    agent: LaoKeAgent = Depends(get_agent)
) -> dict[str, Any]:
    """获取智能体能力"""
    try:
        capabilities = [
            {
                "name": "知识内容管理",
                "description": "管理中医知识内容，包括内容创建、编辑、分类和质量控制",
                "endpoints": ["/api/v1/knowledge/search", "/api/v1/knowledge/categories"]
            },
            {
                "name": "学习路径规划",
                "description": "为用户规划个性化的中医学习路径，包括课程安排和进度跟踪",
                "endpoints": ["/api/v1/learning/plan", "/api/v1/learning/paths"]
            },
            {
                "name": "社区内容管理",
                "description": "管理社区内容，包括内容审核、用户互动和社区活动组织",
                "endpoints": ["/api/v1/community/posts"]
            },
            {
                "name": "中医知识问答",
                "description": "回答用户的中医相关问题，提供专业的知识解答和建议",
                "endpoints": ["/api/v1/chat"]
            },
            {
                "name": "内容推荐",
                "description": "基于用户兴趣和学习历史推荐个性化的学习内容",
                "endpoints": ["/api/v1/chat"]
            }
        ]

        return {
            "success": True,
            "data": {"capabilities": capabilities}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
